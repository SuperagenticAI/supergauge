# Emitters

An **emitter** turns values a tool already holds into an Agent Quality Record.
SuperGauge does not run evaluations, grade trajectories, or host a harness.
Those stay in the peer tool. The record is the release decision written down
afterward.

## What "emit" means

1. Run your usual evaluation (LangSmith experiment, ADK evalset, Inspect log,
   or any other runner).
2. Map peer fields onto the AQR blocks in [`SPEC.md`](../../SPEC.md).
3. Point `assurance.evidence` at the ledger you already keep. Prefer
   `opentelemetry/1.x` when you export OTel; see
   [`rfcs/0001-otel-evidence-mapping.md`](../../rfcs/0001-otel-evidence-mapping.md).
4. Enforce gates only with **deterministic** measures. Judged scores may be
   recorded; they must not back a gate (SPEC §4.1).

Conformance stays self-asserted. After you emit, run:

```bash
pip install pyyaml jsonschema
python conformance/check.py record.yaml --level L1
```

## Guides

| Peer | Guide | Typical inputs |
|---|---|---|
| LangSmith | [`langsmith.md`](langsmith.md) | Experiment / dataset eval results, feedback scores, traces |
| Google ADK | [`adk.md`](adk.md) | Evalset cases, trajectory and response metrics, result JSON |
| Inspect AI | [`inspect.md`](inspect.md) | `.eval` / JSON eval logs (`EvalLog`) |

## Measure ids

Cite only ids published under [`measures/`](../../measures/). Do not invent
identifiers. If a peer score has no registry home yet, leave it out of
`measures[]` or propose an RFC; do not gate on it under a made-up name.

## Deterministic vs judged (reminder)

| Kind | May gate? | Examples in the registry |
|---|---|---|
| Deterministic | Yes | `task.completion`, `tool.correctness`, `trajectory.valid`, `reliability.pass_hat_k`, `policy.hard_rules`, `safety.injection_resistance` |
| Judged | No | `answer.grounded` |

A peer "LLM-as-judge" or rubric score maps to a judged measure (or to
`assurance.judge`), never to `gates[]`.
