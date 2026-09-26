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
5. When claiming resistance to reward hacking, map integrity facts into
   optional `assurance.integrity` per
   [`rfcs/0005-test-integrity-reward-hack.md`](../../rfcs/0005-test-integrity-reward-hack.md).

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
| Jev / System One | [`jev-systemone.md`](jev-systemone.md) | Versioned model id, pack digest, Score/Noul/Choice answers, confidence |
| SuperQode | [`superqode.md`](superqode.md) | Harness-protocol ledger, SystemOne tool_gate / rubric grades, promotion state |

## Measure ids

Cite only ids published under [`measures/`](../../measures/). Do not invent
identifiers. If a peer score has no registry home yet, leave it out of
`measures[]` or propose an RFC; do not gate on it under a made-up name.

## Agent Card and AIBOM digests (serialize-only)

When the peer already holds an A2A Agent Card or an AIBOM / provenance
artifact, emit digests into the record. Do not fetch or invent them inside
SuperGauge.

| Already held | Write into |
|---|---|
| Published Agent Card JSON (or its content hash) | `subject.agent_card.well_known_url`, `card_digest`, optional `version` / `etag` / `skill_ids` |
| Card freshness check at emission | `measures[]` / optional `gates[]` entry for `interop.agent_card_fresh` |
| CycloneDX ML-BOM / AIBOM document | `supply_chain.aibom_digest` (optional `aibom_format`) |
| SLSA or in-toto attestation | `supply_chain.slsa_provenance_digest` (optional `provenance_format`) |
| MCP servers configured for the run | `supply_chain.mcp_servers[]` with name and digests |

Draft field contracts:
[`rfcs/0002-a2a-agent-card-binding.md`](../../rfcs/0002-a2a-agent-card-binding.md),
[`rfcs/0003-supply-chain-aibom-slsa.md`](../../rfcs/0003-supply-chain-aibom-slsa.md),
[`rfcs/0004-jev-systemone-interop.md`](../../rfcs/0004-jev-systemone-interop.md).

When the peer already holds System One answers, pin `assurance.judge.model` and
optional `pack_digest`; map Score/Noul to judged measures; use soft
`decision.hold` for low confidence. Do not call TypeSafe from SuperGauge.

## Deterministic vs judged (reminder)

| Kind | May gate? | Examples in the registry |
|---|---|---|
| Deterministic | Yes | `task.completion`, `tool.correctness`, `trajectory.valid`, `reliability.pass_hat_k`, `policy.hard_rules`, `safety.injection_resistance`, `interop.agent_card_fresh` |
| Judged | No | `answer.grounded`, System One Score/Noul grades |

A peer "LLM-as-judge" or rubric score maps to a judged measure (or to
`assurance.judge`), never to `gates[]`.
