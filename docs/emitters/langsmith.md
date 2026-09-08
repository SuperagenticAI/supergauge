# LangSmith to Agent Quality Record

Map a LangSmith experiment (dataset eval) onto an AQR. LangSmith remains the
runner and trace store. SuperGauge serialises the release decision.

Peer docs:
[Evaluate](https://docs.langchain.com/langsmith/evaluate-llm-application),
[Analyze an experiment](https://docs.langchain.com/langsmith/analyze-an-experiment),
[Export data](https://docs.langchain.com/langsmith/data-export).

## Peer concepts to AQR fields

| LangSmith concept | AQR field | Notes |
|---|---|---|
| Experiment / project name + run ids | `record_id`, `subject.agent` | Choose a stable agent name; keep LangSmith ids in the ledger, not as digests |
| Dataset version / example ids | `task_set.manifest_digest` | Hash the exact example set evaluated; set `sealed` only if the split was held back from optimizers |
| Root run `status` / task success key | `measures` id `task.completion` | Only when success is a declared world-state or reference check, not a fluent summary |
| Tool runs (`run_type=tool`) args/outputs | `tool.correctness`, `trajectory.valid` | Needs schemas and ordered invocations in the trace |
| Feedback score from a model grader | Judged measure e.g. `answer.grounded`, plus `assurance.judge` | **Must not** appear in `gates[]` |
| Feedback score from a deterministic evaluator | Matching deterministic measure id | May gate when the computation matches the registry definition |
| Latency / token / cost aggregates | `efficiency.latency_per_success`, `efficiency.tokens_per_success`, `efficiency.cost_per_success` | Use only when the denominator is successes as the measure defines |
| Trace export / OTel bridge | `assurance.evidence` | `format: opentelemetry/1.x` when exporting OTel; otherwise reference the LangSmith trace export and use a named format string the schema allows |
| Repetition across examples | `reliability.pass_hat_k` | Requires k independent runs per task and a recorded reset (see OTel RFC) |

## Deterministic vs judged

LangSmith evaluators often return free-form `score` keys. Classify each key
before mapping:

- Exact match, JSON-schema check, tool-arg validation, policy denial count:
  deterministic candidates.
- LLM rubric, "helpfulness", semantic similarity judged by a model: judged.
  Record under a judged measure and pin `assurance.judge.{id,model}`; do not
  gate.

If you cannot defend determinism the way SPEC section 4.1 requires, treat the
score as judged.

## Minimal YAML skeleton

```yaml
supergauge: "0.1"
record_id: aqr_langsmith_example
emitted_at: 2026-09-08T12:00:00Z

profile: {id: sg/coding-agent, version: "0.1", tier: T1}

subject:
  agent: my-langsmith-agent
  harness_digest: sha256:0000000000000000000000000000000000000000000000000000000000000000
  authority: {sandbox: unknown, egress: unknown}

task_set:
  manifest_digest: sha256:0000000000000000000000000000000000000000000000000000000000000000
  held_out: 0
  sealed: false

measures:
  - {id: task.completion, value: 0.0, n: 0}
  # judged example (optional): answer.grounded; never put this in gates

gates: []   # add only deterministic floors you can recompute from evidence

assurance:
  evidence:
    ledger: langsmith://project/<experiment-id>
    format: opentelemetry/1.x
    events: 0
    replayable: false
  evaluator_independent: false

decision:
  verdict: hold
  actor: "team@example.com"
```

Replace placeholder digests with real sha256 values over the artifacts you
ran. Set `replayable: true` only when a third party can recompute deterministic
gates from the referenced ledger
([OTel mapping RFC](../../rfcs/0001-otel-evidence-mapping.md)).

## Related registry ids

`task.completion`, `tool.correctness`, `trajectory.valid`,
`reliability.pass_hat_k`, `answer.grounded`,
`efficiency.cost_per_success`, `efficiency.latency_per_success`,
`efficiency.tokens_per_success`, `assurance.evidence_complete`.
