# Emitter guide: A2A Agent Card freshness

How to compute `interop.agent_card_fresh` deterministically from an A2A Agent
Card review and write it into an Agent Quality Record. This guide applies to
any emitter; SuperOptiX (`super a2a adapt` plus its Agent Card Review skill) is
the motivating case.

Field contracts:
[`rfcs/0002-a2a-agent-card-binding.md`](../../rfcs/0002-a2a-agent-card-binding.md)
and [`measures/interop.agent_card_fresh.md`](../../measures/interop.agent_card_fresh.md).
This guide adds no fields; it shows the computation.

## What the measure answers

Does the Agent Card that discovery serves right now match the card this release
was reviewed against, and does it still expose every skill the release claims?
It is a boolean, computed without a model in the loop, so it MAY back a gate.

An LLM-based card review (wording, description quality, skill naming advice) is
judged evidence. Record it in the ledger or as advisory rationale; it never
feeds this measure.

## Inputs

| Input | Source |
|---|---|
| Reviewed card bytes | The card JSON produced by `super a2a adapt` (or your publish step) for this release |
| Served card bytes | HTTP GET of the well-known URL at emission time |
| `skill_ids` | Skills the release claims to expose (the routing allowlist) |
| Freshness window | Emitter or profile policy: maximum age of the fetch relative to `emitted_at` |

## Computation

1. **Digest the reviewed card.** `card_digest = "sha256:" + sha256(bytes)` over
   the exact UTF-8 bytes published. Do not re-serialise or pretty-print first.
2. **Fetch the served card.** GET `well_known_url` (typically
   `https://<host>/.well-known/agent-card.json`). Record status, `ETag`, and
   the fetch timestamp in the ledger.
3. **Digest match.** sha256 of the served bytes MUST equal `card_digest`.
4. **Freshness window.** The fetch MUST have happened within the window before
   `emitted_at` (for example 15 minutes). A fetch older than the window is
   treated as not fetched. The window is policy, not a record field; state it
   in the profile or the emitter config and keep the fetch timestamp in the
   ledger so a reader can recheck it.
5. **Skill allowlist.** Parse the served card; every entry in `skill_ids` MUST
   appear as a `skills[].id`. Extra skills on the card do not fail the
   measure, but a profile MAY tighten that.
6. **Value.** True only when steps 3 to 5 all hold. Any network error,
   non-200 status, empty body, or invalid JSON yields false (or omit the
   measure). Never invent a digest.

```python
import hashlib, json, urllib.request
from datetime import datetime, timezone, timedelta

def agent_card_fresh(url, card_digest, skill_ids, window=timedelta(minutes=15)):
    fetched_at = datetime.now(timezone.utc)
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            if resp.status != 200:
                return False, fetched_at, None
            body, etag = resp.read(), resp.headers.get("ETag")
    except OSError:
        return False, fetched_at, None
    if "sha256:" + hashlib.sha256(body).hexdigest() != card_digest:
        return False, fetched_at, etag
    try:
        served = {s.get("id") for s in json.loads(body).get("skills", [])}
    except (ValueError, AttributeError):
        return False, fetched_at, etag
    ok = set(skill_ids or []) <= served
    # Emit immediately; the caller checks emitted_at - fetched_at <= window.
    return ok, fetched_at, etag
```

## Emitting into the record

```yaml
subject:
  agent: superoptix-support-agent
  harness_digest: sha256:...
  agent_card:
    well_known_url: "https://agents.example.com/.well-known/agent-card.json"
    card_digest: sha256:...          # step 1
    version: "2.0.0"                 # card version when present
    etag: "W/\"2.0.0-ab12\""         # from step 2
    skill_ids: [triage, escalate]    # allowlist checked in step 5

measures:
  - id: interop.agent_card_fresh
    value: true

gates:
  - {id: interop.agent_card_fresh, result: pass}   # optional; profile decides
```

The gate carries no floor (the value is boolean). If the measure is false and
the profile gates on it, the verdict MUST NOT be `ship`.

## Mapping from SuperOptiX

| SuperOptiX | AQR |
|---|---|
| Card emitted by `super a2a adapt` | Bytes digested into `subject.agent_card.card_digest` |
| Deployed well-known endpoint | `subject.agent_card.well_known_url`, `etag` |
| Skills declared for the release | `subject.agent_card.skill_ids` |
| Deterministic digest and skill check | `measures[]` entry `interop.agent_card_fresh` |
| Agent Card Review skill findings (LLM) | Ledger or `decision.rationale` only; advisory, never a gate |

## Related

- [`l2-agent-card-supply-chain.yaml`](../../conformance/examples/l2-agent-card-supply-chain.yaml)
  shows a complete record with a card binding.
