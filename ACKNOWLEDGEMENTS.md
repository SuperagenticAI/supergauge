# Acknowledgements

Contributors are listed here by the work they authored. Two accepted proposals
earn a seat on the measure-group review rotation; see `GOVERNANCE.md`.

## Measures

| Measure | Group | Type | Author |
|---|---|---|---|
| `answer.grounded` | effectiveness | judged | Superagentic AI |
| `task.completion` | effectiveness | deterministic | Superagentic AI |
| `tool.correctness` | effectiveness | deterministic | Superagentic AI |
| `trajectory.valid` | effectiveness | deterministic | Superagentic AI |
| `efficiency.cost_per_success` | efficiency | deterministic | Superagentic AI |
| `efficiency.latency_per_success` | efficiency | deterministic | Superagentic AI |
| `efficiency.tokens_per_success` | efficiency | deterministic | Superagentic AI |
| `reliability.pass_at_k` | robustness | deterministic | Superagentic AI |
| `reliability.pass_hat_k` | robustness | deterministic | Superagentic AI |
| `robustness.multi_turn` | robustness | judged | Superagentic AI |
| `robustness.recovery` | robustness | deterministic | Superagentic AI |
| `policy.hard_rules` | safety | deterministic | Superagentic AI |
| `safety.injection_resistance` | safety | deterministic | Superagentic AI |
| `safety.isolation` | safety | deterministic | Superagentic AI |
| `safety.tool_abuse` | safety | deterministic | Superagentic AI |
| `assurance.evaluator_independence` | assurance | deterministic | Superagentic AI |
| `assurance.evidence_complete` | assurance | deterministic | Superagentic AI |
| `assurance.holdout_sealed` | assurance | deterministic | Superagentic AI |
| `assurance.judge_agreement` | assurance | deterministic | Superagentic AI |

## Profiles

| Profile | Author |
|---|---|
| `sg/coding-agent` | Superagentic AI |

## Packs

| Pack | Author |
|---|---|
| `sg/injection` | Superagentic AI |

## Prior art

This specification borrows its structure from work that came before it.

- **OpenTelemetry**, for the split between a small stable core and an open
  semantic-convention registry that outsiders extend.
- **SLSA**, for graded, self-asserted, independently verifiable levels rather
  than a certification programme.
- **MADR**, the Markdown Architectural Decision Record format, for the shape of
  the `decision` block at tier T2: problem statement, considered options,
  outcome and rationale.
- The **Agent Control Specification**, the **Evaluation Context Protocol** and
  **OpenTelemetry** as the layers this format composes with. Their non-goals
  are what left room for this one.
