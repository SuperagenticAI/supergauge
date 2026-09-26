---
id: sg/aiuc-1
version: "0.1"
status: draft
kind: export-profile
maps_to: AIUC-1 Q3 2026-07-15
standard_cut: "2026-07-15"
next_cut: "2026-10-15"
---

# `sg/aiuc-1@0.1`

Export mapping from Agent Quality Record evidence onto selected **AIUC-1**
controls, especially coding-agent requirements from the Q3 2026-07-15 standard
cut. AIUC-1 updates quarterly (next cut **2026-10-15**); pin the cut you mapped
against on the record.

Peer references:
[AIUC-1 changelog](https://www.aiuc-1.com/changelog),
[A008 secrets](https://www.aiuc-1.com/data-and-privacy/prevent-secrets-leakage),
[B010 secure code patterns](https://www.aiuc-1.com/security/promote-secure-code-patterns),
[B006 unauthorized actions / sandbox](https://www.aiuc-1.com/security/enforce-contextual-access-controls).

## Framing

This pack is an **export profile over existing AQR evidence**. It does not
define new SuperGauge measures, floors, or an aggregate AIUC score. Passing
deterministic AQR gates does not equal AIUC-1 certification.

## Control mapping (coding-agent focus)

| AIUC-1 control | Intent (short) | Typical AQR evidence classes |
|---|---|---|
| **A008** (A008.1-A008.5) | Prevent leakage of credentials and secrets in inputs, generated code, storage, and logs | `subject.authority` (egress, capabilities); `gates[]` / measures `policy.hard_rules`, `safety.tool_abuse`, `safety.isolation`; pack `sg/injection` exfiltration cases (`ex-*`) under `safety.injection_resistance`; ledger redaction notes in `assurance.evidence`; optional `supply_chain` when secret-store tooling is attested |
| **B010** (B010.1-B010.6) | Promote secure patterns in generated code (vuln classes, auth, deps, sessions, validation, safe logging) | Held-out `task.completion` / `tool.correctness` / `trajectory.valid` where tasks encode secure-default checks; profile `sg/coding-agent` safety gates; judged rubrics (if used) recorded only as judged measures, never as sole ship gates; `decision.rationale` may cite secure-default task packs |
| **B006.1** | Restrict agent access to approved services, APIs, MCP servers, tools | `subject.authority.capabilities`; optional `supply_chain.mcp_servers[]` pins; ACS-sourced `gates[]` |
| **B006.3** | Execution-level safeguards: sandbox FS/network/credential limits for agent-executed code and first-party MCP; tool-integrity; pre-exec authorization; scan hooks/skills/rules | `subject.authority.sandbox`, `egress`; measures `safety.isolation`, `safety.tool_abuse`, `policy.hard_rules`; hermetic / independence claims in `assurance.evaluator_independent`; ledger policy decisions |

Additional AIUC-1 requirements may map later. Emitters SHOULD list the control
ids they claim under `export.profiles[].controls` when using the optional export
block.

## Example export claim (metadata only)

```yaml
export:
  profiles:
    - id: sg/aiuc-1
      version: "0.1"
      standard_cut: "2026-07-15"
      controls: [A008, B010, B006.1, B006.3]
```

Coverage means "these AQR fields were populated to support an auditor mapping,"
not "certified."

## Cadence

| Cut | Notes |
|---|---|
| 2026-07-15 (Q3) | Coding-agent A008 / B010 added; B006.3 broadened to agent-executed code and MCP |
| 2026-10-15 (next) | Remap this pack when the public changelog publishes; bump pack minor or add a new cut field |

## Out of scope

- Performing AIUC-1 audits or issuing certificates.
- Hosting AIUC evidence templates beyond AQR pointers.
- Aggregate control scores.
