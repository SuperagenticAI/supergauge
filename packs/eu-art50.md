---
id: sg/eu-art50
version: "0.1"
status: draft
kind: export-profile
maps_to: EU AI Act Article 50
---

# `sg/eu-art50@0.1`

Export mapping from Agent Quality Record evidence onto **EU AI Act Article 50**
transparency expectations for AI systems (including agents) that interact with
natural persons or generate content, as clarified by the Commission FAQ.

Official FAQ:
[How are AI agents addressed within the AI Act?](https://ai-act-service-desk.ec.europa.eu/en/ai-act/faq/how-are-ai-agents-addressed-within-ai-act-0)

## Framing

Article 50 transparency is about disclosure and marking where the Act requires
it. This pack maps AQR fields that help an organisation show what was disclosed,
to whom, and which exceptions were claimed. It is **not** a conformity
assessment, not a risk classification under Chapter III, and not an aggregate
compliance score.

From 2 August 2026, if an AI agent is intended to interact with natural persons
or generate content, Article 50 transparency rules may apply (see FAQ). Agents
are not a separate legal category; AI system and GPAI definitions cover them.

## Disclosure when interacting with persons

| Expectation | Typical AQR evidence |
|---|---|
| Users informed they are interacting with an AI agent / system | `subject.agent`, optional `subject.agent_card` (well-known card / skills); `decision.rationale` or linked policy digest describing the disclosure UX; profile id naming the human-facing surface |
| Content marking where generated content must be detectable / labelled | Measure or pack results that record marking checks (deterministic when implemented as presence/format checks); ledger events showing mark applied; `assurance.evidence` pointer |
| Human oversight / release sign-off for higher-tier human-facing agents | `decision.actor`, T2 `question` / `options` / `rationale`; `rolls_back_to` |

Judged "looks disclosed" opinions MUST NOT alone gate `ship`. Prefer
deterministic checks (string markers present, card published, policy version
pinned).

## Machine↔machine and chain-of-thought exclusions

Not every agent surface is a natural-person interaction. Document exceptions
explicitly when claiming them:

| Situation | How to record on / beside the AQR |
|---|---|
| Pure **machine↔machine** invocation (no natural person in the loop for that interface) | Note in `decision.rationale` or linked policy that Art. 50 person-interaction disclosure does not apply to this interface; still pin `subject.authority` and any Agent Card used by machines |
| **Chain-of-thought / internal reasoning** not exposed as user-facing content | Treat as out of Art. 50 content-marking scope for that artifact; do not claim user-facing marking for hidden CoT. If CoT is shown to persons, apply the content-marking row above |
| Mixed product (human chat + M2M tools) | Split surfaces in rationale: which interfaces disclose, which are M2M exceptions |

Emitters MUST NOT use an exception claim to skip deterministic gates the profile
still requires (sandbox, tool abuse, isolation, and so on).

## Example export claim

```yaml
export:
  profiles:
    - id: sg/eu-art50
      version: "0.1"
      controls: ["art50.disclosure", "art50.content-marking", "art50.m2m-exception"]
```

Control strings here are exporter-local labels for checklist rows, not official
AI Act article subdivisions.

## Out of scope

- Legal advice on whether a deployment is high-risk or GPAI-systemic-risk.
- Implementing the Article 50 Code of Practice inside SuperGauge.
- Aggregate "Art. 50 score."
