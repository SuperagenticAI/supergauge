# Inspect AI to Agent Quality Record

Map an Inspect eval log (`EvalLog` in `.eval` or JSON form) onto an AQR.
Inspect remains the evaluation runner. SuperGauge serialises the release
decision.

Peer docs:
[Log files](https://inspect.aisi.org.uk/eval-logs.html),
[Log viewer](https://inspect.aisi.org.uk/log-viewer.html),
[`inspect log schema`](https://inspect.aisi.org.uk/reference/inspect_log.html).

## Peer concepts to AQR fields

| Inspect concept | AQR field | Notes |
|---|---|---|
| `eval.task` / `eval.model` | `subject.agent`, `subject.model` | Pin model id as recorded in the log |
| Dataset / sample ids in the log | `task_set.manifest_digest` | Digest the dataset revision actually scored |
| `samples[].scores` with exact match / programmatic scorer | Deterministic `measures[]` entry | Map only onto published ids (e.g. `task.completion` when the score is end-state success) |
| Model-graded scorer | Judged measure + `assurance.judge` | **Must not** gate |
| `samples[].messages` / tool events | `tool.correctness`, `trajectory.valid` | Preserve order for trajectory checks |
| `stats` model usage | `efficiency.tokens_per_success` (and related) | Only with a success denominator consistent with the measure |
| Epochs / repeated samples | `reliability.pass_hat_k` | Map epochs to attempts only when starting conditions reset and k is explicit |
| Log path (`.eval` / JSON) | `assurance.evidence.ledger` | Prefer also exporting OTel as `opentelemetry/1.x` for L4 |
| `results` aggregate metrics | Never a single AQR score | Copy into discrete `measures[]`; SPEC forbids a headline aggregate (section 4.2) |

## Deterministic vs judged

Inspect scorers vary. Before mapping:

- Programmatic scorers over targets, tool traces, or filesystem state:
  deterministic candidates.
- Scorers that call a model for a rubric or preference: judged. Pin
  `assurance.judge` and keep them out of `gates[]`.

`answer.grounded` is the registry example of a judged effectiveness measure.
Do not place it under `gates`.

## Minimal YAML skeleton

```yaml
supergauge: "0.1"
record_id: aqr_inspect_example
emitted_at: 2026-09-08T12:00:00Z

profile: {id: sg/coding-agent, version: "0.1", tier: T1}

subject:
  agent: my-inspect-task
  harness_digest: sha256:0000000000000000000000000000000000000000000000000000000000000000
  model: {provider: unknown, id: as-recorded-in-eval-log}
  authority: {sandbox: unknown, egress: unknown}

task_set:
  manifest_digest: sha256:0000000000000000000000000000000000000000000000000000000000000000
  held_out: 0
  sealed: false

measures:
  - {id: task.completion, value: 0.0, n: 0, split: held-out}

gates: []

assurance:
  evidence:
    ledger: file://./logs/eval.json
    format: opentelemetry/1.x
    events: 0
    replayable: false
  evaluator_independent: false

decision:
  verdict: hold
  actor: "team@example.com"
```

Set `replayable: true` only when deterministic gates recompute from the
ledger under the
[OTel evidence mapping](../../rfcs/0001-otel-evidence-mapping.md) (or another
documented format).

## Related registry ids

`task.completion`, `tool.correctness`, `trajectory.valid`,
`reliability.pass_hat_k`, `answer.grounded`,
`efficiency.tokens_per_success`, `efficiency.latency_per_success`,
`assurance.evidence_complete`.

## Test integrity (RFC 0005)

Map Inspect (or companion harness) integrity facts into optional
`assurance.integrity`. Inspect remains the runner.

| Inspect / harness fact | AQR field |
|---|---|
| Programmatic scorers and targets outside agent write scope | `integrity.metric_custody: external` |
| Third-party recompute of gated scores | `integrity.recompute_digest` |
| Unpassable / contamination samples | `task_set.canary_ids` + `integrity.canaries[]` |
| Isolated sandbox / no answer-key path | `integrity.hermetic_workspace` |
| Optimizer role cannot apply grades | `integrity.capability_disjoint_roles` |
| Model-graded scorer feedback looped to the agent | `integrity.review_feedback` |
| Mechanical rejection of a model-graded PASS | `integrity.mechanical_override` + soft `hold`/`reject` |

Model-graded Inspect scorers remain judged and must not gate. See
[`rfcs/0005-test-integrity-reward-hack.md`](../../rfcs/0005-test-integrity-reward-hack.md).

