# SuperQode to Agent Quality Record

Map a SuperQode promotion or SystemOne ledger onto an AQR. SuperQode remains the
harness, policy engine, and (when enabled) System One client. SuperGauge
serialises the release decision.

Peer docs: [SuperQode](https://superqode.dev),
[Jev Integration / SystemOne](https://docs.superqode.dev/advanced/systemone/),
draft AQR binding
[`rfcs/0004-jev-systemone-interop.md`](../../rfcs/0004-jev-systemone-interop.md).
For Jev primitives alone, see [`jev-systemone.md`](jev-systemone.md).

## Scope

This guide covers **serialize-only** projection:

- Promotion registry state (staged → canary → activated), digests, actor,
  rollback snapshot, ACS-shaped policy decisions.
- SystemOne ledger fields: `tool_gate` (or other pack) hash, versioned model id,
  typed answers, confidence / abstentions, rubric grades, disagreement traces.

It does **not** replace SuperQode's SystemOne client, Tune/GEPA flows, or live
calls to TypeSafe. SuperGauge must not depend on `typesafe.ai`.

## Peer concepts to AQR fields

| SuperQode concept | AQR field | Notes |
|---|---|---|
| Agent / harness id + harness digest | `subject.agent`, `subject.harness_digest` | Digest the loop that ran |
| ACS / YAML exec-policy in force | `subject.authority`, `gates[]` with `source: acs` | Policy actually applied |
| Task / eval manifest | `task_set.manifest_digest`, `sealed`, `canary_ids` | Same sealing rules as SPEC §2.4 |
| Deterministic harness metrics | Matching deterministic measure ids | May gate when definitions match |
| SystemOne model id (`jev-1.x.y`) | `assurance.judge.model` | From live response metadata |
| Pack content hash | `assurance.judge.pack_digest` | Includes questions, schemas, decision_policy |
| `tool_gate` ALLOW/DENY/ASK composition | Ledger + optional human comparison | Raw gate recommendation is not an AQR gate unless recomputed deterministically from ACS |
| Rubric grade (`satisfied` / `needs_revision` / `ungraded`) | Judged measure and/or rationale | **Must not** hard-gate `ship` alone |
| Choice/Score confidence, Noul abstain band | Soft `decision.hold` + rationale | Emitter policy; gates stay independent |
| Labelled decision-report (Jev vs `humanAction`) | `assurance.judge_agreement` | Deterministic kappa; may gate |
| Harness-protocol / decision-traces directory | `assurance.evidence.ledger` | `format: superqode.harness-protocol/1` |
| Promotion actor + rollback snapshot | `decision.actor`, `decision.rolls_back_to` | Verdict from human or policy after gates |

## tool_gate and permissions

Shadow mode records `intendedAction` (Jev), `policyAction`, and
`permissionAction` without letting Jev override hard denials. When emitting:

- Put final ACS / native permission outcomes in deterministic `gates[]` when
  they match registry measures such as `policy.hard_rules` or
  `safety.tool_abuse`.
- Keep Jev's recommendation in the ledger. Do not copy raw confidence into
  `gates[].floor`.
- If you have blind human labels on the same checks, compute
  `assurance.judge_agreement` and optionally gate on that statistic only.

## Rubric grades

`SUPERQODE_RUBRIC_GRADER=systemone` and `jev_rubric` evaluators produce model
judgments with evidence. Treat them as judged:

- Map a grounding-style rubric toward `answer.grounded` when the computation
  matches that measure.
- Otherwise leave the grade in the ledger and summarise in
  `decision.rationale` until a dedicated judged measure exists under
  `measures/`.
- `ungraded` / low confidence: prefer `decision.verdict: hold` rather than a
  fake pass.

## Soft hold with gates still green

```yaml
gates:
  - {id: policy.hard_rules, result: pass, source: acs}
  - {id: safety.tool_abuse, result: pass, source: acs}
  - {id: task.completion, floor: 0.8, split: held-out, result: pass}

assurance:
  judge:
    id: superqode/systemone-tool-gate@1
    model: jev-1.13.0
    pack_digest: sha256:1111111111111111111111111111111111111111111111111111111111111111

decision:
  verdict: hold
  actor: "priya@acme.example"
  rationale: >
    ACS gates and held-out completion passed. SystemOne tool_gate abstained
    (confidence below pack min_confidence); holding promotion for review.
```

## Minimal YAML skeleton

```yaml
supergauge: "0.1"
record_id: aqr_superqode_systemone_example
emitted_at: 2026-09-23T12:00:00Z

profile: {id: sg/coding-agent, version: "0.1", tier: T1}

subject:
  agent: acme-coding-harness
  harness_digest: sha256:0000000000000000000000000000000000000000000000000000000000000000
  authority:
    acs_policy_version: "2.1"
    sandbox: docker
    egress: deny-by-default

task_set:
  manifest_digest: sha256:0000000000000000000000000000000000000000000000000000000000000000
  held_out: 0
  sealed: false

measures:
  - {id: task.completion, value: 0.0, n: 1}
  - {id: assurance.judge_agreement, value: 0.0, n: 30}

gates:
  - {id: policy.hard_rules, result: pass, source: acs}

assurance:
  judge:
    id: superqode/systemone@1
    model: jev-1.13.0
    pack_digest: sha256:0000000000000000000000000000000000000000000000000000000000000000
  evidence:
    ledger: .superqode/harness-protocol/
    format: superqode.harness-protocol/1
    events: 0
    replayable: false
  evaluator_independent: true

decision:
  verdict: hold
  actor: "team@example.com"
  rationale: "Example skeleton for SuperQode SystemOne projection."
```

## Related registry ids

`policy.hard_rules`, `safety.tool_abuse`, `safety.isolation`, `task.completion`,
`reliability.pass_hat_k`, `answer.grounded`, `assurance.judge_agreement`,
`assurance.evidence_complete`, `assurance.evaluator_independence`.
