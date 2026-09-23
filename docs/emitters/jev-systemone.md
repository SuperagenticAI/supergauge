# Jev / System One to Agent Quality Record

Map TypeSafe AI **Jev** (System One) answers onto an AQR. Jev remains the
decision model. SuperGauge serialises the release decision afterward.

Peer docs: [typesafe.ai](https://typesafe.ai/),
[System One docs](https://docs.typesafe.ai/),
[Confidence](https://docs.typesafe.ai/confidence),
[Models](https://docs.typesafe.ai/models)
(pin versioned ids such as `jev-1.13.0`).

Draft contract: [`rfcs/0004-jev-systemone-interop.md`](../../rfcs/0004-jev-systemone-interop.md).

## What "emit" means here

1. Your code (or SuperQode SystemOne) already called Jev with a frozen question
   pack and holds typed answers.
2. Map those values onto AQR blocks. Do not call `api.typesafe.ai` from
   SuperGauge.
3. Pin `assurance.judge.model` to the **versioned** model id from the response.
4. Record judged Score/Noul results under judged measure ids. Enforce gates only
   with deterministic measures (SPEC §4.1).

## Peer concepts to AQR fields

| System One concept | AQR field | Notes |
|---|---|---|
| Versioned model id (`jev-1.13.0`) | `assurance.judge.model` | Prefer over `jev-latest` / `jev-preview` |
| Question pack bytes / content hash | `assurance.judge.pack_digest` | `sha256:` of questions, schemas, decision_policy |
| Judge / rubric programme id | `assurance.judge.id` | Emitter-stable lineage, e.g. `typesafe/jev@1` |
| Score over agent output | Judged measure (e.g. `answer.grounded` when applicable) | **Must not** appear in `gates[]` |
| Noul over a free-form claim | Judged measure or `decision.rationale` | **Must not** gate |
| Choice / Score `confidence` | Soft hold policy → `decision.verdict: hold` + rationale | Never a gate floor on raw confidence |
| Abstain / soft-middle band | Rationale and pack guidance | Do not invent a measure id per band |
| Blind human labels vs Jev labels | `assurance.judge_agreement` (+ kappa on `assurance.judge`) | Deterministic; **may** gate |
| Optional ECE study | `assurance.judge.calibration_ece` | Advisory calibration note |
| Decision traces / harness ledger | `assurance.evidence` | Point at the store you already keep |

## Judged ≠ gate

| Kind | May gate? | System One examples |
|---|---|---|
| Deterministic | Yes | `assurance.judge_agreement` over stored Jev vs human labels; ACS / policy gates unrelated to Jev |
| Judged / probabilistic | No | Score, Noul, Choice confidence, rubric `satisfied` without a deterministic recomputation |

If a model sits anywhere in the scoring path, treat the result as judged.

## Soft hold pattern

Emitters MAY hold the release when confidence is below a local threshold even
when every deterministic gate passed:

```yaml
gates:
  - {id: policy.hard_rules, result: pass, source: acs}
  - {id: task.completion, floor: 0.8, split: held-out, result: pass}

decision:
  verdict: hold
  actor: "release@example.com"
  rationale: >
    Deterministic gates passed. Jev Choice confidence 0.41 below emitter
    min_confidence 0.75 on pack sha256:aaaa...; holding for human review.
```

This preserves SPEC §4.1: judged and probabilistic measures do not alone
hard-gate `ship`.

## Minimal YAML skeleton

```yaml
supergauge: "0.1"
record_id: aqr_jev_example
emitted_at: 2026-09-23T12:00:00Z

profile: {id: sg/coding-agent, version: "0.1", tier: T1}

subject:
  agent: my-systemone-agent
  harness_digest: sha256:0000000000000000000000000000000000000000000000000000000000000000
  authority: {sandbox: unknown, egress: unknown}

task_set:
  manifest_digest: sha256:0000000000000000000000000000000000000000000000000000000000000000
  held_out: 0
  sealed: false

measures:
  - {id: task.completion, value: 0.0, n: 1}
  # judged example from Score/Noul: answer.grounded; never put this in gates
  - {id: answer.grounded, value: 0.0, n: 1}
  - {id: assurance.judge_agreement, value: 0.0, n: 30}

gates: []   # add only deterministic floors; never confidence / Noul / Score

assurance:
  judge:
    id: typesafe/jev@1
    model: jev-1.13.0
    pack_digest: sha256:0000000000000000000000000000000000000000000000000000000000000000
    human_agreement_kappa: 0.0
    sampled: 30
  evidence:
    ledger: file://./decision-traces/
    format: superqode.harness-protocol/1
    events: 0
    replayable: false
  evaluator_independent: false

decision:
  verdict: hold
  actor: "team@example.com"
  rationale: "Example skeleton; replace digests and fill real measures before ship."
```

Replace placeholder digests with real `sha256:` values over the artifacts you
ran. Set `replayable: true` only when a third party can recompute deterministic
gates from the referenced ledger.

## Related registry ids

`answer.grounded`, `assurance.judge_agreement`, `assurance.evaluator_independence`,
`assurance.evidence_complete`, `task.completion`, `policy.hard_rules`.
