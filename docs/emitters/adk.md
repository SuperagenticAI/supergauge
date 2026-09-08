# Google ADK to Agent Quality Record

Map ADK evalset cases and evaluation results onto an AQR. ADK remains the
agent runtime and evaluator. SuperGauge serialises the release decision.

Peer docs:
[Why evaluate agents (ADK)](https://adk.dev/evaluate/),
[ADK evaluate guide (source)](https://github.com/google/adk-docs/blob/main/docs/evaluate/index.md).

## Peer concepts to AQR fields

| ADK concept | AQR field | Notes |
|---|---|---|
| `app_name` / agent module | `subject.agent` | Stable product name, not a transient session id |
| Evalset file + `eval_id` list | `task_set.manifest_digest` | Digest the exact evalset artifact used |
| `conversation[].intermediate_data.tool_uses` | `tool.correctness`, `trajectory.valid` | Ordered tool names and args |
| Metric `tool_trajectory_avg_score` | Often near `trajectory.valid` / `tool.correctness` | Exact trajectory match is stricter than SuperGauge selection rules; document any divergence |
| Metric `response_match_score` (ROUGE) | Usually **not** a registry measure | Do not invent an id; omit or propose an RFC. Not a gate by default |
| Metric `final_response_match_v2` (LLM-judged) | Judged (e.g. toward `answer.grounded`) + `assurance.judge` | **Must not** gate |
| Session / invocation results JSON | `assurance.evidence.ledger` | Point at the saved EvalSetResult / output directory, or an OTel export if configured |
| Multi-run retries with reset | `reliability.pass_hat_k` | Only with explicit k attempts and reset evidence |
| Safety / policy hooks outside the model | `policy.hard_rules`, ACS-sourced `gates[]` | Requires a decision log, not a prompt instruction |

## Deterministic vs judged

| ADK metric | SuperGauge stance |
|---|---|
| `tool_trajectory_avg_score` | Deterministic candidate when recomputed from tool_uses alone |
| `response_match_score` | Lexical overlap; not a published measure id here; do not gate under a fake id |
| `final_response_match_v2` | Judged; record, do not gate |

Custom ADK metrics follow the same rule: if a model sits in the scoring path,
the result is judged.

## Minimal YAML skeleton

```yaml
supergauge: "0.1"
record_id: aqr_adk_example
emitted_at: 2026-09-08T12:00:00Z

profile: {id: sg/coding-agent, version: "0.1", tier: T1}

subject:
  agent: my-adk-app
  harness_digest: sha256:0000000000000000000000000000000000000000000000000000000000000000
  authority: {sandbox: unknown, egress: unknown}

task_set:
  manifest_digest: sha256:0000000000000000000000000000000000000000000000000000000000000000
  held_out: 0
  sealed: false

measures:
  - {id: trajectory.valid, value: 0.0, n: 0}
  - {id: tool.correctness, value: 0.0, n: 0}

gates: []

assurance:
  evidence:
    ledger: file://./eval_results/
    format: opentelemetry/1.x
    events: 0
    replayable: false
  evaluator_independent: false

decision:
  verdict: hold
  actor: "team@example.com"
```

If you do not export OTel, keep a resolvable `ledger` path to the ADK result
files and use a schema-allowed `format` string you document; prefer moving to
`opentelemetry/1.x` for L4
([RFC 0001](../../rfcs/0001-otel-evidence-mapping.md)).

## Related registry ids

`trajectory.valid`, `tool.correctness`, `task.completion`,
`reliability.pass_hat_k`, `answer.grounded`, `policy.hard_rules`,
`assurance.evidence_complete`, `assurance.evaluator_independence`.
