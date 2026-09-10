---
rfc: 0002
title: A2A Agent Card binding for subject identity
status: draft          # draft | accepted | rejected | superseded
surface: spec
author: Superagentic AI
created: 2026-09-10
---

# RFC 0002: A2A Agent Card binding for subject identity

## Summary

Bind an Agent Quality Record to the published A2A Agent Card that callers
discover at ship time. Add an optional `subject.agent_card` object (well-known
URL, card digest, version or ETag, skill-id allowlist) and a deterministic
measure `interop.agent_card_fresh` that profiles MAY use as a gate. The mapping
sits under SPEC §2.3. It does not implement the A2A wire protocol.

## Problem

An agent published for other agents to call is selected from its Agent Card:
identity, endpoint, capabilities, and skills. Teams already measure completion
and reliability on the harness they evaluated, then ship a different card, a
stale skill list, or a card whose digest no longer matches what discovery
serves. The record pins `subject.harness_digest` and `subject.authority`, but
not the discovery surface peers actually read. Interop regressions such as a
skill disappearing from the card are invisible until traffic stops. OWASP and
procurement checklists increasingly ask whether the published identity matches
the artifact under review; without a card binding the AQR cannot answer.

## Proposal

### `subject.agent_card`

When the subject is (or will be) discoverable via A2A, emitters MAY populate:

```yaml
subject:
  agent: acme-support-triage
  harness_digest: sha256:...
  authority: { ... }                 # unchanged; see below
  agent_card:
    well_known_url: "https://agents.acme.example/.well-known/agent-card.json"
    card_digest: sha256:...          # digest of the card JSON at ship
    version: "1.4.2"                 # card version field when present
    etag: "W/\"1.4.2-9c1e\""         # OPTIONAL HTTP ETag from the serving endpoint
    skill_ids: [triage, escalate]    # allowlist; MUST be a subset of card skills
```

| Field | Required when `agent_card` present | Meaning |
|---|---|---|
| `well_known_url` | required | Absolute URL of the Agent Card (typically `/.well-known/agent-card.json` per A2A discovery) |
| `card_digest` | required | `sha256:` digest of the canonical card JSON bytes used for this release |
| `version` | recommended | Agent Card `version` (or equivalent) when the card carries one |
| `etag` | optional | HTTP `ETag` observed when fetching or publishing the card |
| `skill_ids` | recommended | Skill ids the release claims to expose; each MUST appear on the digested card |

**Canonical digest.** Compute `card_digest` over the exact JSON bytes that were
published or fetched for this release decision (UTF-8). Do not digest a
pretty-printed re-serialisation unless that re-serialisation is what the
endpoint serves. Digests MUST be computed over artifacts used, never over
declared intent (SPEC §7).

**Skill allowlist.** `skill_ids` is an allowlist of skills this subject is
willing to be routed for under this record. It MUST be a subset of the `id`
values in the Agent Card's skills array. Emitting a skill id absent from the
digested card is a schema-valid but materially false record; conformance
checkers and the freshness measure treat that as a failure.

### Relation to `subject.authority`

| Concern | Field | Role |
|---|---|---|
| What peers discover and how they route | `subject.agent_card` | Published identity, endpoint, skills |
| What the agent was permitted to do during measurement | `subject.authority` | Sandbox, egress, capabilities, ACS / grant |

The card describes exposure. Authority describes the execution policy in force
while measures were taken. Both can be true and still disagree with production
(for example a card advertising write skills while measurement used
read-only capabilities). Emitters MUST populate authority from the policy in
force (SPEC §2.3) and MUST NOT treat a skill listed on the card as a substitute
for an authority grant. A profile MAY require both blocks when the agent is
published for interop.

### Optional gate: `interop.agent_card_fresh`

Profiles MAY require the deterministic measure `interop.agent_card_fresh` (see
`measures/interop.agent_card_fresh.md`) and MAY place it in `gates[]`:

```yaml
measures:
  - {id: interop.agent_card_fresh, value: true}
gates:
  - {id: interop.agent_card_fresh, result: pass, source: assert}
```

Freshness is true when the `card_digest` on the record matches the digest of
the card fetched from `well_known_url` (or the bytes the publisher asserts were
served) at emission time, and when every `skill_ids` entry appears on that
card. Two conformant implementations given the same card bytes and record
fields MUST agree.

### Light SPEC and schema patches

- SPEC §2.3 documents `agent_card` as optional under `subject`.
- SPEC §1.2 notes A2A discovery as an adjacent layer the record may bind.
- The JSON Schema adds `subject.agent_card` with the fields above.
- Status remains `0.1.0-draft`; the fields are normative enough for emitters,
  not frozen.

## Deterministic or judged

The binding itself is not a measure. `interop.agent_card_fresh` is
`deterministic`: equality of digests and set inclusion of skill ids. No model
is consulted. It MAY back a gate (SPEC §4.1).

## Evidence required

- The Agent Card JSON bytes (or a content-addressed store of them) corresponding
  to `card_digest`.
- Optionally, HTTP cache validators (`ETag`, `Cache-Control`) from the
  well-known endpoint, for operators who re-check after emission.
- No A2A task messages or streaming sessions are required for this binding.

## Cost

No additional agent runs. One HTTP GET (or a read of the published artifact)
plus a SHA-256 over the card JSON. Negligible relative to an evaluation pass.

## Failure cases

| Case | Required behaviour |
|---|---|
| `agent_card` omitted | Valid; agent is not claiming A2A discovery on this record |
| `well_known_url` unreachable at emission | Do not claim `interop.agent_card_fresh: true`; omit the measure or report false |
| Digested bytes differ from bytes served at the URL | `interop.agent_card_fresh` is false |
| `skill_ids` contains an id absent from the card | `interop.agent_card_fresh` is false; do not ship if gated |
| Card requires authentication the emitter cannot perform | Do not invent a digest; omit `agent_card` or use the authenticated card bytes actually obtained |
| Card changes after ship | Record remains a point-in-time assertion; re-emit a new AQR for the new card |

## Alternatives considered

- **Fold card fields into `subject.authority`.** Rejected: authority is the
  policy in force during measurement; the card is the discovery surface.
  Mixing them obscures both failure modes.
- **Require Agent Cards on every record.** Rejected: many subjects are not
  published over A2A; the block stays optional.
- **Gate on judged card-quality rubrics.** Rejected: freshness is checkable
  without a model; judged routing quality already has
  `interop.routing_invocation` as a separate concern.
- **Embed the full Agent Card in the AQR.** Rejected: digests and URLs keep
  the record small and compose with content-addressed stores; the card lives
  at the well-known URL.

## Prior art

- [A2A Agent Discovery](https://a2a-protocol.org/latest/topics/agent-discovery/)
  (well-known URI `/.well-known/agent-card.json`, registries, ETag / caching).
- Existing SuperGauge measure `interop.routing_invocation`, which grades
  selection given a catalogue; this RFC pins the card the catalogue entry
  came from.
- SPEC §2.3 `authority` and §7 digest rules.

## Out of scope

- Implementing or specifying the A2A wire protocol, task lifecycle, or
  streaming.
- Hosting a curated Agent Card registry.
- Authenticating to protected card endpoints on behalf of emitters.
- Declaring floors or thresholds (profile-scoped, SPEC §4.3).
- Replacing `subject.authority` or ACS checkpoint gates.

## Open questions

- Whether to allow a `registry_url` alongside `well_known_url` for catalog-based
  discovery without a domain well-known path.
- Whether `skill_ids` should be required whenever `agent_card` is present, or
  remain recommended until more emitters adopt cards.
- How to represent authenticated extended Agent Cards without storing secrets
  in the AQR (digest-only is the current proposal).

---

### Review checklist

- [ ] `id` is dotted, lowercase, and not a rename of an existing measure
- [ ] Computation is unambiguous enough for two implementations to agree
- [ ] `deterministic` / `judged` is correctly classified and defended
- [ ] Failure cases are specified
- [ ] Evidence requirements are stated
- [ ] No floor or threshold is asserted (floors are profile-scoped, SPEC §4.3)
- [ ] Commits are DCO signed off
