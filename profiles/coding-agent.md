---
id: sg/coding-agent
version: "0.1"
status: draft
tier: T1
applies_to: Agents that read and modify a source repository
---

# `sg/coding-agent`

A starting profile for agents that open branches, edit files, run tests and
propose or land changes in a repository.

## Tier

Declared `T1` by default: a coding agent typically changes shared state that
other people depend on, but its work is reviewable and revertible through
version control.

Raise the profile to `T2` where any of the following hold, and record the
decision:

- The agent can merge without human review.
- The agent can reach a deployment pipeline, a production database or a secret
  store.
- The repository governs a regulated decision.

A profile may demand more than its tier requires. It may not demand less.

## Mandatory gates

Every record claiming this profile MUST carry these gates.

| Gate | Source | What it asserts |
|---|---|---|
| `policy.hard_rules` | `acs` | The run stayed inside its declared capability grant |
| `safety.tool_abuse` | `acs` | No privilege escalation, no destructive call outside the declared surface |
| `safety.isolation` | `native` | No writes outside the working tree and no unsanctioned network egress |
| `task.completion` | `native` | Measured on the held-out split |

At `T2`, add:

| Gate | Source | What it asserts |
|---|---|---|
| `reliability.pass_hat_k` | `native` | Consistency across repeated independent attempts |
| `safety.injection_resistance` | `pack` | The adversarial pack ran and reported no successful attack |

## Recommended measures

Reported, not gated:

`trajectory.valid` · `tool.correctness` · `efficiency.cost_per_success` ·
`efficiency.tokens_per_success` · `robustness.recovery` ·
`assurance.evidence_complete`

Coding agents have two failure modes worth measuring beyond the core registry,
both of which have established behavioural checks in the wild and neither of
which is a registered measure yet:

- Tests weakened or deleted to make a task pass.
- Implementation drifting from the plan it was given.

Both are good RFC candidates. See `rfcs/0000-template.md`.

## Thresholds

**This profile publishes no floors at version 0.1.**

Under SPEC §4.3 a profile may publish a floor only once engagements or published
research stand behind it. Nothing yet does for coding agents across the range of
repositories this profile is meant to cover, and a number invented to look
authoritative would be worse than none: implementers would conform to it, and it
would be defending nothing.

Set floors locally, record them in the `gates[]` entries of your own records, and
propose a published floor by RFC once you have evidence. Useful evidence is a
distribution across repositories, not a single team's average.

## Task set guidance

- Draw cases from merged pull requests and from incidents, in that order of
  preference. A benchmark repository measures the benchmark.
- Hold back at least a quarter of cases and fingerprint the manifest. Anything
  that tunes the agent MUST NOT read the held-out portion.
- Include at least two contamination probes: cases whose expected outcome is
  known to be unreachable, so a passing result exposes leakage.
- Reset the working tree between attempts. Without a reset,
  `reliability.pass_hat_k` measures nothing.

## Evidence

`assurance.evidence.format` SHOULD be `opentelemetry/1.x` where the repository
already exports traces. Coding agents produce long tool-call sequences, so the
ledger is usually the largest artifact a record references; retaining it for the
life of the record is what makes L4 reachable.

## Advisory: System One / Jev reporting

When the coding loop uses SuperQode SystemOne or TypeSafe Jev for tool gates or
rubric grades, emitters MAY pin `assurance.judge.model` and `pack_digest`,
record judged scores, and apply a soft `decision.hold` on low confidence.
Those signals are advisory for this profile: they do not add mandatory gates at
`0.1`. See
[`rfcs/0004-jev-systemone-interop.md`](../rfcs/0004-jev-systemone-interop.md).

## Changelog

- `0.1` — first draft. Gates settled, thresholds deliberately unset.
