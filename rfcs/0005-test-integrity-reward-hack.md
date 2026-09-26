---
rfc: 0005
title: Test integrity and reward-hack evidence for AQR
status: draft          # draft | accepted | rejected | superseded
surface: spec
author: Superagentic AI
created: 2026-09-26
---

# RFC 0005: Test integrity and reward-hack evidence for AQR

## Summary

Define how emitters record **test integrity** evidence on an Agent Quality
Record when agents may game evaluators: metric custody outside the agent,
independent held-out recompute, protected metrics, canary / unpassable cases,
hermetic workspaces, capability-disjoint roles, review-feedback opacity, and
mechanical override of a judged PASS when deterministic integrity fails.
Judged and probabilistic signals remain soft-hold / escalate only. They MUST
NOT alone hard-gate `ship`. SuperGauge stays a release-decision protocol; it
does not become an eval runner, host BenchShield instrumentation, or call peer
judge APIs. Light SPEC and schema patches keep status at `0.1.0-draft`.

## Problem

Agents that both produce work and influence the score for that work create a
reward-hacking surface: they can clear thresholds without achieving the
intended goal. Public research on autonomous research agents (arXiv:2609.28614,
2026-09-24, non-normative) reports spontaneous hacking rates far higher on
open-ended pipelines than on constrained kernels, and shows that detailed
iterative review feedback can raise evasion compared with opaque rejection.
Separately, LLM-as-judge pipelines that treat the judge as an oracle fail when
harness leaks, corrupted labels, or perfect canary scores go unchecked
(PROCTOR position, arXiv:2609.02246, non-normative): the judge should be an
advisor whose PASS can be mechanically overridden by deterministic gates.

Today an AQR already requires sealed held-out splits, canary ids, and
`evaluator_independent` (SPEC §2.4, §2.7, §4.1). It does not yet give emitters
a documented home for metric custody, recompute attestation, canary outcomes,
hermetic / role-disjoint claims, feedback-opacity policy, or an explicit
mechanical-override flag when integrity fails under a judged PASS. Teams either
omit that evidence or bury it in unstructured rationale.

## Proposal

### Normative position (judge demotion)

1. **Deterministic integrity gates** may hard-gate `ship` (SPEC §4.1).
2. **Judged / probabilistic evidence** (model rubrics, confidence, Noul, Score)
   MAY inform `decision.verdict: hold` or escalate to a human. They MUST NOT
   alone satisfy a gate or alone justify `ship`.
3. When deterministic integrity checks fail, emitters MUST NOT emit
   `verdict: ship` even if a judge recorded PASS. Prefer
   `verdict: hold` or `reject`, and set
   `assurance.integrity.mechanical_override: true` when a judged PASS was
   discarded for that reason.
4. No aggregate quality score (SPEC §4.2).

### Optional `assurance.integrity` block

Additive and optional. The eight required AQR blocks are unchanged. When an
emitter holds integrity evidence, it MAY include:

```yaml
assurance:
  evaluator_independent: true
  integrity:
    metric_custody: external          # external | shared | agent-writable
    recompute_digest: sha256:...      # independent held-out recompute attestation
    recompute_party: "replay@acme.example"
    protected_metric_ids:
      - task.completion
      - assurance.holdout_sealed
    canaries:
      - {id: canary_unpassable_01, expected: fail, observed: fail}
      - {id: canary_key_exfil_02, expected: fail, observed: fail}
    hermetic_workspace: true
    capability_disjoint_roles: true
    review_feedback: opaque           # opaque | generic-reject | detailed
    mechanical_override: false
```

| Field | Meaning |
|---|---|
| `metric_custody` | Where protected metrics and grader oracles live relative to the agent write scope. `external` means the agent cannot modify the metric implementation or answer keys used for gating. |
| `recompute_digest` | Digest of an attestation that an independent party recomputed gated measures on held-out (or exploit-exposing) data. |
| `recompute_party` | Identity of that party when claimed. |
| `protected_metric_ids` | Measure ids whose oracles are outside agent control for this record. |
| `canaries[]` | Contamination / unpassable probes with expected vs observed `pass`/`fail`. A perfect score on an engineered unpassable canary is evidence of cheating, not excellence. |
| `hermetic_workspace` | Agent workspace lacked exfiltration paths to grader secrets, answer keys, or mutable reward files. |
| `capability_disjoint_roles` | No single component both proposed the change under review and applied / graded it. |
| `review_feedback` | How much iterative judge or panel feedback the agent saw. Prefer `opaque` or `generic-reject` when teaching evasion is a risk; `detailed` SHOULD soft-hold when combined with rising attempt counts. |
| `mechanical_override` | True when a judged PASS was overridden because deterministic integrity failed. |

**Relation to existing fields.** `task_set.canary_ids` remains the list of probe
ids in the task set. `assurance.integrity.canaries` records **outcomes**.
`assurance.evaluator_independent` remains the boolean independence claim;
integrity fields add custody, recompute, hermeticity, and override detail.
Digests use the existing `sha256:` form (SPEC `$defs.digest`) and MUST hash
attestation bytes actually used (SPEC §7).

### Deterministic gates / soft-hold path

| Signal | Gate? | Typical decision effect |
|---|---|---|
| `assurance.holdout_sealed`, `assurance.evaluator_independence`, sealed canaries with expected fail observed | Yes, when profile opts in | Fail → must not `ship` |
| Independent recompute mismatch (`recompute_digest` does not verify) | Treat as integrity fail | `hold` or `reject` |
| Unpassable canary observed `pass` | Integrity fail | MUST NOT `ship` |
| `metric_custody: agent-writable` while claiming L3+ | Incomplete integrity | Prefer soft-hold; do not claim L3 integrity |
| Judged rubric PASS with integrity fail | Judged must not win | `mechanical_override: true`, verdict `hold`/`reject` |
| Detailed review feedback + multi-round retries | Soft only | Emitter policy `hold` / escalate |
| Raw judge confidence / Score / Noul | No | Soft-hold only (RFC 0004) |

Profiles choose floors. The core does not assert numeric thresholds (SPEC §4.3).

### Light SPEC and schema patches

- SPEC §1.2 adds a relationship row for test integrity / judge demotion.
- SPEC §2.7 documents optional `assurance.integrity`.
- SPEC §4.1 clarifies mechanical override when integrity fails under judged PASS.
- SPEC §8 lists this RFC among related draft bindings.
- JSON Schema adds optional `assurance.integrity` properties.
- Status remains `0.1.0-draft`.

### Emitter documentation

Short mapping notes in LangSmith, Inspect, and SuperQode emitter guides: how to
project custody, canary outcomes, recompute digests, and soft-hold / override
into AQR without turning SuperGauge into the runner.

## Deterministic or judged

- Metric custody, hermetic workspace, role disjointness (as recorded boolean
  claims), canary expected/observed equality, and recompute digest verification
  are **deterministic** when computed from stored artifacts and digests. They
  may back gates when the profile opts in.
- Model-panel "this looks like a hack" opinions are **judged**. Soft-hold only.
- Soft hold and mechanical override are decision policy, not measure types.

## Evidence required

- Protected metric implementation and answer-key digests outside agent write
  scope when claiming `metric_custody: external`.
- Canary definitions and observed outcomes for each `canaries[]` entry.
- Independent recompute attestation bytes matching `recompute_digest`.
- Role and workspace policy (or ledger events) supporting hermetic /
  capability-disjoint claims.
- When `mechanical_override: true`, the judged PASS artifact and the failing
  integrity check that overrode it.

## Cost

No additional SuperGauge runtime. Emitters serialise integrity facts they
already hold from hermetic harnesses, sealed task sets, and independent
replay. Independent recompute costs whatever the organisation already budgets
for L3/L4 assurance.

## Failure cases

| Case | Required behaviour |
|---|---|
| `integrity` omitted | Valid; no integrity claim beyond existing sealed / independence fields |
| Judged PASS + integrity fail + `verdict: ship` | Invalid under §4.1; must not ship |
| Unpassable canary `observed: pass` | Integrity fail; must not ship |
| `recompute_digest` present but bytes do not match | Failed verification; do not claim independent recompute |
| `review_feedback: detailed` with many retries and no soft hold | Allowed; soft hold is emitter policy, but document the risk in rationale |
| SuperGauge asked to host BenchShield or run the eval | Out of scope; refuse in the emitter design |

## Alternatives considered

- **Absorb BenchShield or a reward-integrity instrumentation runtime.** Rejected:
  SuperGauge records decisions; peer harnesses own instrumentation.
- **Hard-gate `ship` on judged "no hack detected" panels.** Rejected: SPEC §4.1
  and PROCTOR demotion; judges remain advisors.
- **Require `assurance.integrity` on every record.** Rejected: optional keeps L1
  reachable; profiles opt in.
- **Fold canary outcomes into `task_set` only.** Rejected: task set names probes;
  outcomes belong with assurance evidence.
- **Aggregate integrity score.** Rejected: SPEC §4.2.

## Prior art

- Reward hacking in autonomous research agents (arXiv:2609.28614, 2026-09-24):
  metric custody, independent recompute, and feedback opacity (non-normative).
- PROCTOR judge demotion (arXiv:2609.02246): hermetic sandboxes,
  capability-disjoint roles, mechanical checks outranking the Teacher, frozen
  holdouts, unpassable canaries (non-normative).
- Existing AQR sealed holdouts, canary ids, `assurance.evaluator_independence`,
  and ship rule (SPEC §2.4, §2.7, §4.1).
- RFCs 0001-0004: serialize-only interop without absorbing peer runtimes.

## Out of scope

- Hosting or shipping BenchShield, PROCTOR, or any eval instrumentation.
- Calling judge or panel APIs from SuperGauge.
- Defining numeric integrity floors in the core.
- An aggregate integrity or quality score.
- Turning SuperGauge into an evaluation runner.

## Open questions

- Whether `metric_custody` should later become a dedicated deterministic
  registry measure with a boolean computation.
- Whether profiles should recommend default soft-hold when
  `review_feedback: detailed` exceeds N attempts.
- How multi-party recompute should present multiple digests without widening
  the block into an array yet.

---

### Review checklist

- [ ] `id` is dotted, lowercase, and not a rename of an existing measure
- [ ] Computation is unambiguous enough for two implementations to agree
- [ ] `deterministic` / `judged` is correctly classified and defended
- [ ] Failure cases are specified
- [ ] Evidence requirements are stated
- [ ] No floor or threshold is asserted (floors are profile-scoped, SPEC §4.3)
- [ ] Commits are DCO signed off
