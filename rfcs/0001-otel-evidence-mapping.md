---
rfc: 0001
title: OpenTelemetry evidence mapping for L4 replay
status: draft          # draft | accepted | rejected | superseded
surface: spec
author: Superagentic AI
created: 2026-09-08
---

# RFC 0001: OpenTelemetry evidence mapping for L4 replay

## Summary

Define a practical attribute and event contract for
`assurance.evidence.format: opentelemetry/1.x` so that a third party can replay
deterministic gates from an OpenTelemetry-shaped ledger. The mapping sits under
SPEC §8. It does not introduce a new evidence format id, and it does not make
SuperGauge an OpenTelemetry product.

## Problem

SPEC §8 already recognises `opentelemetry/1.x` as a ledger shape, and L4
requires independent replay from that ledger. Without a concrete mapping,
two emitters can both claim `opentelemetry/1.x` while storing incompatible
attributes, and a third party cannot recompute measures such as
`tool.correctness`, `trajectory.valid`, `policy.hard_rules`, or
`reliability.pass_hat_k`. The format then looks adoptable on paper and fails
at the moment of verification.

## Proposal

Treat an OTel export (OTLP JSON/Protobuf, or an equivalent span store the
record can resolve) as the ledger referenced by `assurance.evidence.ledger`.
Spans and events carry the facts a deterministic measure needs. Attribute
names below use a `sg.*` prefix for SuperGauge-specific fields and reuse
widely deployed `gen_ai.*` / tool attributes where they already exist. Names
are stable for this RFC; a later accepted revision may align further with
published semantic conventions without changing measure ids.

### Required root context

Every evaluation run that contributes to a measure MUST be recoverable as a
trace (or a contiguous set of spans under one trace) that carries:

| Attribute | Required | Meaning |
|---|---|---|
| `sg.record_id` | recommended | AQR `record_id` when known at export time |
| `sg.task_set.manifest_digest` | required | Same digest as `task_set.manifest_digest` |
| `sg.task.id` | required on task-scoped spans | Stable task identifier within the manifest |
| `sg.run.id` | required | Opaque run id; unique per attempt |
| `sg.attempt.index` | required when k>1 | 0-based attempt index for `reliability.pass_hat_k` |
| `sg.subject.harness_digest` | recommended | Same digest as `subject.harness_digest` |
| `sg.split` | recommended | `held-in` / `held-out` / other split label |

`assurance.evidence.events` SHOULD equal the number of spans plus events the
emitter considers part of the ledger for this record.

### Tool calls

For measures that inspect invocations (`tool.correctness`, `trajectory.valid`,
`safety.tool_abuse`):

| Attribute / event | Required | Meaning |
|---|---|---|
| Span name or `gen_ai.tool.name` / `sg.tool.name` | required | Tool identity as presented to the agent |
| `sg.tool.call_id` | required | Stable id for this invocation |
| `sg.tool.arguments` | required | Arguments as applied (structured or canonical JSON) |
| `sg.tool.result` | recommended | Result payload or a digest of it |
| `sg.tool.outcome` | required | `ok` / `error` / `denied` |
| `sg.tool.schema_ok` | recommended | Whether arguments validated against the declared schema |
| Event `sg.tool.redundant_retry` | optional | Fired when an identical call repeats with an unchanged result |

Ordering MUST be preserved by span start timestamps (and parent/child links
where present). Formats that drop order cannot back `trajectory.valid`.

### Policy and ACS decisions

For `policy.hard_rules` and gates with `source: acs`:

| Attribute / event | Required | Meaning |
|---|---|---|
| Event `sg.policy.decision` | required per checkpoint | One event per evaluated checkpoint |
| `sg.policy.version` | required | Policy / ACS version in force |
| `sg.policy.checkpoint` | required | e.g. `input`, `llm`, `state`, `tool`, `output`, or a recorded extension |
| `sg.policy.result` | required | `allow` / `deny` / `ask` |
| `sg.policy.rule_id` | recommended | Which rule fired |
| `sg.policy.approval_actor` | required when result is `ask` and a human allowed it | Identity recorded in the ledger |

Detective-only enforcement (decision after the action completed) SHOULD set
`sg.policy.enforcement` to `detective`; preventive checkpoints use
`preventive`.

### Attempt resets

For `reliability.pass_hat_k`, the ledger MUST show a reset between attempts of
the same task:

| Attribute / event | Required | Meaning |
|---|---|---|
| Event `sg.attempt.reset` | required between attempts | Marks that starting conditions were restored |
| `sg.task.id` | required | Task being re-attempted |
| `sg.attempt.index` | required | Index of the attempt that is about to begin |
| `sg.attempt.prior_run_id` | recommended | Run id of the attempt just closed |

Absence of reset evidence means `reliability.pass_hat_k` MUST NOT be reported
as computed from that ledger (see Failure cases).

### Task-set and manifest digests

| Attribute | Required | Meaning |
|---|---|---|
| `sg.task_set.manifest_digest` | required | Fingerprint of the evaluated task set |
| `sg.task_set.sealed` | recommended | Mirrors `task_set.sealed` |
| `sg.task_set.canary_id` | required on canary probe runs | Matches an entry in `task_set.canary_ids` |

Digests MUST be computed over the artifacts used, never over declared intent
(SPEC §7).

### Measure derivation markers

Emitters SHOULD record how each reported deterministic measure was derived:

| Attribute / event | Required | Meaning |
|---|---|---|
| Event `sg.measure.derived` | recommended per deterministic measure | Ties a measure id to the runs used |
| `sg.measure.id` | required on that event | Registry id (e.g. `task.completion`) |
| `sg.measure.value` | required on that event | Value written into the AQR |
| `sg.measure.run_ids` | recommended | Run ids included in the denominator |

Judged measures MAY appear as evidence of presence for
`assurance.evidence_complete`, but their values are not reproduced by replay
(see that measure's definition).

### How evidence supports replaying deterministic gates

A third party reaching L4:

1. Resolves `assurance.evidence.ledger` and confirms `format` is
   `opentelemetry/1.x` (or a more precise `opentelemetry/1.<n>`).
2. Reconstructs the ordered tool and policy event streams per `sg.run.id`.
3. Recomputes each deterministic measure cited by a gate from those streams
   and the pinned `task_set.manifest_digest`.
4. Confirms gate floors and pass/fail outcomes match the record.
5. Treats judged measures as non-gating: presence may be checked; values are
   taken as recorded.

Two conformant implementations given the same OTel ledger MUST produce the
same deterministic gate results (SPEC §4.1).

## Deterministic or judged

This RFC defines an evidence mapping, not a measure. The mapping exists so
that deterministic measures remain deterministic when the ledger is OTel.
Anything that requires a model to interpret a span is out of scope for gate
replay.

## Evidence required

An export or store of OpenTelemetry spans/events that includes the required
attributes above for every run referenced by a deterministic measure on the
record. The AQR continues to carry `assurance.evidence.{ledger,format,events,replayable}` as today.

## Cost

No additional agent runs. Export cost is whatever the emitter already pays to
emit OTel, plus optional `sg.measure.derived` events (negligible).

## Failure cases

| Case | Required behaviour |
|---|---|
| Required attribute missing on a run used by a gate | `assurance.evidence_complete` is false; do not claim L4 replay for that measure |
| Spans present but unordered / timestamps unavailable | Do not report `trajectory.valid` from that ledger |
| `reliability.pass_hat_k` without `sg.attempt.reset` between attempts | Do not report the measure from that ledger |
| Judged-only feedback in the peer tool, no world-state assertion | Map to a judged measure such as `answer.grounded`; never to a gate |
| Ledger pruned by retention | `assurance.evidence_complete` is false; note the retention window |

## Alternatives considered

- **Leave §8 as a one-line name only.** Rejected: L4 is not actionable.
- **Require `superqode.harness-protocol/1` for L4.** Rejected: SPEC deliberately lets OTel-only stacks reach the format without switching runtimes.
- **Mint a new format id (`opentelemetry-sg/1`).** Deferred: the existing
  `opentelemetry/1.x` id is enough if the attribute contract is documented;
  a new id can be added later if divergence from plain OTel becomes large.
- **Full semantic-convention ownership inside SuperGauge.** Rejected: out of
  scope (see below).

## Prior art

OpenTelemetry GenAI and tool semantic conventions; Agent Control Specification
checkpoint decisions; Evaluation Context Protocol trajectory exposure; the
native `superqode.harness-protocol/1` ledger in the reference implementation.

## Out of scope

- Shipping an OpenTelemetry collector, SDK, or distribution.
- Redefining upstream GenAI semantic conventions.
- Runners, CLIs, or evaluation harnesses inside this repository.
- Declaring floors or thresholds (those remain profile-scoped, SPEC §4.3).
- Replaying judged measures as if they were deterministic.

## Open questions

- How tightly to bind attribute names to the final OTel GenAI conventions once
  those stabilize.
- Whether `events` counts spans only, or spans plus log/events records.
- Whether a minimal JSON Schema for the `sg.*` attributes should live under
  `schema/` in a follow-up RFC.

---

### Review checklist

- [ ] `id` is dotted, lowercase, and not a rename of an existing measure
- [ ] Computation is unambiguous enough for two implementations to agree
- [ ] `deterministic` / `judged` is correctly classified and defended
- [ ] Failure cases are specified
- [ ] Evidence requirements are stated
- [ ] No floor or threshold is asserted (floors are profile-scoped, SPEC §4.3)
- [ ] Commits are DCO signed off
