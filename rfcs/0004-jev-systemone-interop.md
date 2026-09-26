---
rfc: 0004
title: Jev / SystemOne interop for AQR (assurance pinning and soft hold)
status: draft          # draft | accepted | rejected | superseded
surface: spec
author: Superagentic AI
created: 2026-09-23
---

# RFC 0004: Jev / SystemOne interop for AQR (assurance pinning and soft hold)

## Summary

Define how emitters serialise TypeSafe AI **Jev** (the first System One model)
and SuperQode SystemOne harness outputs into an Agent Quality Record. The
mapping covers judged measures from Score and Noul answers, assurance pinning
(versioned model id, question-pack digest, optional human agreement and
calibration notes), soft `decision.hold` heuristics when confidence is low, and
an optional deterministic gate only on agreement statistics computed from stored
labels. SuperGauge does not host or call Jev; emit means serialise values the
emitter already holds. Light SPEC and schema patches keep status at
`0.1.0-draft`.

## Problem

Teams already run Jev (and SuperQode SystemOne packs such as `tool_gate`) as a
typed decision service beside a coding or evaluation loop. Those runs produce
model ids (`jev-1.x.y`), pack content hashes, Choice/Score confidence,
Noul probabilities, and sometimes human-reviewed labels for agreement. Today an
AQR can pin a generic `assurance.judge.model`, but has no documented home for a
System One question-pack digest, no interop guide for confidence-aware soft
holds, and a risk that integrators hard-gate `ship` on raw confidence or Noul
values. SPEC §4.1 forbids judged measures from backing gates; raw System One
confidence is a probabilistic signal and must not alone hard-gate `ship`.

## Proposal

### What Jev is (for this RFC)

Jev is TypeSafe AI's flagship System One model. Callers send a state and typed
questions; Jev returns structured answers without generating chat prose:

| Primitive | Returns | Role in AQR |
|---|---|---|
| **Choice** | `choice`, `probabilities`, `confidence` | Routing / classification signals; confidence informs emitter hold policy, not gates |
| **Score** | `score`, `probabilities`, `confidence` | Rubric-style levels; map to judged measures when the score grades agent output |
| **Noul** | `noul` in `[0, 1]` | Yes/no probability; judged signal unless recomputed from stored labels only |

Pin the versioned model id returned by the API (for example `jev-1.13.0`), not
only an alias such as `jev-latest`. Aliases move; thresholds and agreement
studies do not.

References: [typesafe.ai](https://typesafe.ai/),
[docs.typesafe.ai](https://docs.typesafe.ai/),
[Confidence](https://docs.typesafe.ai/confidence),
[SuperQode SystemOne integration](https://docs.superqode.dev/advanced/systemone/).

### Mapping into AQR

#### Judged measures from Score / Noul

When Score or Noul grades agent output (rubric satisfaction, claim support,
soft safety middle bands), record the numeric result under a **judged** registry
id. Prefer existing ids when the computation matches:

| System One signal | Typical AQR home | May gate? |
|---|---|---|
| Score / rubric grade over agent work | Judged measure such as `answer.grounded` when the rubric is grounding; otherwise record under a registered judged id or omit until an RFC adds one | No |
| Noul over a free-form claim | Judged measure or advisory note in `decision.rationale` | No |
| Soft-middle safety bands (pack thresholds) | Pack guidance and rationale; do not invent many new measure ids for each band | No |

Do not invent measure ids without adding `measures/<id>.md`. Soft-middle safety
belongs in the reviewed question pack and emitter policy, not in a growing set
of near-duplicate registry entries.

#### Assurance: pin model, pack, optional agreement / calibration

When any judged measure came from Jev / System One, populate `assurance.judge`:

```yaml
assurance:
  judge:
    id: typesafe/jev@1          # rubric or judge programme id the emitter uses
    model: jev-1.13.0           # REQUIRED pin: versioned System One model id
    pack_digest: sha256:...     # OPTIONAL but recommended: digest of the question pack
    human_agreement_kappa: 0.71 # OPTIONAL; same meaning as today
    sampled: 40                 # OPTIONAL sample size for the kappa study
    calibration_ece: 0.08       # OPTIONAL Expected Calibration Error when measured
  evidence:
    ledger: .superqode/decision-traces/
    format: superqode.harness-protocol/1
    events: 120
    replayable: true
  evaluator_independent: true
```

| Field | Required when judging with System One | Meaning |
|---|---|---|
| `judge.model` | required | Versioned id such as `jev-1.13.0` (prefer over `jev-latest`) |
| `judge.id` | required | Stable id for the judge programme / rubric lineage |
| `judge.pack_digest` | recommended | `sha256:` digest of the frozen question pack (questions, schemas, decision_policy) |
| `judge.human_agreement_kappa` | recommended at L3 | Cohen's kappa vs blind human labels (see `assurance.judge_agreement`) |
| `judge.sampled` | with kappa | Sample size for that study |
| `judge.calibration_ece` | optional | ECE or a documented calibration summary in `[0, 1]` when the emitter measured it |

`pack_digest` MUST hash the pack bytes used for the measured runs, not a
description of intent (SPEC §7). SuperQode already records pack hashes on
decision traces; emit that value.

#### Soft `decision.hold` heuristics (emitter policy)

Emitters MAY set `decision.verdict: hold` when System One confidence is below an
emitter-local threshold, when Choice/Score abstains, or when Noul falls in the
pack's abstain band. That is **emitter policy**, recorded in
`decision.rationale`. Deterministic `gates[]` remain independent: every gate may
`pass` while the verdict is still `hold`.

```yaml
decision:
  verdict: hold
  actor: "release@acme.example"
  rationale: >
    Deterministic gates passed. System One Choice confidence 0.41 on the
    release-route pack (min_confidence 0.75); holding for human review.
```

Soft hold MUST NOT be implemented by inventing a gate on raw confidence, Score,
or Noul. Judged and probabilistic measures MUST NOT alone hard-gate `ship`
(SPEC §4.1).

#### Optional deterministic gate on agreement statistics only

`assurance.judge_agreement` remains **deterministic**: it is kappa over two
stored label sets (for example Jev dispositions vs blind human labels on the
same items). A profile MAY gate on that measure. It MUST NOT gate on raw
confidence, Noul, or Score values.

### Light SPEC and schema patches

- SPEC §1.2 adds a relationship row for System One / Jev (interop only).
- SPEC §2.7 documents optional `pack_digest` and `calibration_ece` on
  `assurance.judge`.
- SPEC §8 lists this RFC among related draft bindings.
- JSON Schema adds the two optional judge properties.
- Status remains `0.1.0-draft`.

### Emitter documentation

- [`docs/emitters/jev-systemone.md`](../docs/emitters/jev-systemone.md): field
  maps, YAML skeleton, judged ≠ gate, soft hold pattern.
- [`docs/emitters/superqode.md`](../docs/emitters/superqode.md): how a SuperQode
  SystemOne ledger (tool_gate, pack hash, model id, rubric grades) serialises
  into AQR without replacing the SuperQode client.

## Deterministic or judged

- Raw Choice/Score/Noul answers that grade behaviour: **judged** (a model sits
  in the scoring path). They may not back a gate.
- `assurance.judge_agreement` over stored Jev labels and stored human labels:
  **deterministic** arithmetic. May back a gate.
- Soft hold: decision policy, not a measure type.

## Evidence required

- Versioned model id used for the answers on the record.
- Question-pack bytes (or content-addressed store) matching `pack_digest`.
- Per-item typed answers (and confidence where present) in the referenced
  ledger when claiming replay of judged reporting.
- For kappa / ECE: item ids, both label sets, rubric or pack version, and the
  pinned model id.

## Cost

No additional SuperGauge runtime cost. Emitters that already call Jev or
SuperQode SystemOne only serialise fields they hold. Human agreement and ECE
studies cost whatever sampling the organisation already budgets for L3.

## Failure cases

| Case | Required behaviour |
|---|---|
| Alias (`jev-latest`) recorded without resolved version | Prefer the versioned id from the API response; do not claim L3 judge pinning on an unbound alias |
| `pack_digest` missing while judged System One measures are present | Valid at L1; L3 judge pinning is incomplete until the pack is pinned |
| Gate entry cites confidence, Noul, or Score | Invalid under SPEC §4.1; remove the gate or replace with `assurance.judge_agreement` over stored labels |
| Soft hold omitted while confidence is low | Allowed; soft hold is emitter policy, not a core REQUIRE |
| SuperGauge asked to call typesafe.ai | Out of scope; refuse in the emitter design |

## Alternatives considered

- **Host Jev inside SuperGauge or add a typesafe.ai client dependency.**
  Rejected: emit is serialise-only; neighbouring runtimes own the call.
- **Hard-gate `ship` on confidence or Noul floors in the core.** Rejected:
  SPEC §4.1; confidence is probabilistic and not an oracle.
- **Replace SuperQode's SystemOne client with an AQR-side client.** Rejected:
  SuperQode remains the reference harness; this RFC documents projection only.
- **Many new judged measure ids for every pack question.** Rejected: prefer
  existing judged ids and pack guidance; new ids need `measures/*.md` RFCs.
- **Fold pack digest into `task_set.manifest_digest`.** Rejected: task sets and
  question packs are different artifacts; conflating them breaks replay.

## Prior art

- TypeSafe System One primitives and confidence routing
  ([docs.typesafe.ai](https://docs.typesafe.ai/),
  [Confidence](https://docs.typesafe.ai/confidence)).
- SuperQode SystemOne harness, `tool_gate`, pack hashes, shadow disagreement
  reports, and rubric grading
  ([docs.superqode.dev/advanced/systemone](https://docs.superqode.dev/advanced/systemone/)).
- Existing AQR judge pinning and `assurance.judge_agreement` (SPEC §2.7, §5 L3).
- RFCs 0001–0003: serialize-only interop bindings without absorbing peer runtimes.

## Out of scope

- Hosting, proxying, or calling the TypeSafe API from SuperGauge.
- Shipping a Jev runtime, SDK, or API client as a SuperGauge dependency.
- Replacing SuperQode's SystemOne client, packs, or Tune/GEPA flows.
- Hard-gating `ship` on confidence, Score, or Noul.
- An aggregate quality score (forbidden by SPEC §4.2).
- Declaring numeric confidence floors in the core (floors are profile- or
  emitter-scoped; SPEC §4.3).

## Errata (2026-09-24): Jev swap is a model/component change

Prefactor's note on replacing an LLM step with Jev
([jev-swap-llm-step-did-agent-get-worse](https://prefactor.tech/blog/jev-swap-llm-step-did-agent-get-worse),
2026-09-24) clarifies a governance point this RFC already implies: a Jev swap is
a **model or component change**, with the same regression risk as swapping any
other decision model. Pre-ship evals on a fixed set cannot alone prove production
behaviour did not worsen. Emitters SHOULD version-tag the component that handled
the step (`assurance.judge.model` and related subject digests), record confidence
(or abstention) alongside downstream outcome criteria used for calibration, and
prefer soft `decision.hold` when confidence is low or before/after outcome
coverage is incomplete. Soft hold remains emitter policy; raw confidence still
MUST NOT alone hard-gate `ship` (SPEC §4.1).

## Open questions

- Whether `calibration_ece` should later move to a dedicated deterministic
  assurance measure once a single ECE definition is settled across packs.
- Whether profiles should recommend a default soft-hold confidence band, or
  leave bands entirely to emitter policy.
- How multi-pack releases (tool_gate plus rubric) should present multiple
  `pack_digest` values without widening `assurance.judge` into an array yet.

---

### Review checklist

- [ ] `id` is dotted, lowercase, and not a rename of an existing measure
- [ ] Computation is unambiguous enough for two implementations to agree
- [ ] `deterministic` / `judged` is correctly classified and defended
- [ ] Failure cases are specified
- [ ] Evidence requirements are stated
- [ ] No floor or threshold is asserted (floors are profile-scoped, SPEC §4.3)
- [ ] Commits are DCO signed off
