# SuperGauge

**An open format for the agent release record.**

Version `0.1.0-draft` · Status: **Draft, unstable** · Licence: CC BY 4.0 (this
text), Apache-2.0 (schemas and conformance suite)

---

## 1. What this is

SuperGauge defines one artifact: the **Agent Quality Record** (AQR).

An AQR is a file emitted at the moment somebody decides whether an agent may
ship. It states what was measured, what it was measured against, how the agent
performed, which rules had to hold, whether they held, who decided, and how to
get back to the previous version.

It exists because that decision currently leaves no durable trace. Evaluation
platforms score runs. Control specifications bound behaviour at runtime.
Neither produces the document an auditor asks for, a platform team argues over,
or a rollback points back to.

### 1.1 Scope

The format covers one moment: the release decision. Everything that produces the
inputs to that decision belongs to a neighbouring layer, and the record points at
those layers instead of absorbing them.

| Concern | Where it belongs | What the record holds |
|---|---|---|
| Running and grading an agent | An evaluation platform | The values a grader returned |
| Task content | The implementer's own corpus | A manifest digest |
| Trace and event storage | An observability backend | A reference to the ledger |
| Runtime enforcement | A policy engine, such as ACS | The decisions that engine returned |
| Assurance that a claim is true | A third party replaying the ledger | A signature and a replay pointer |

Two consequences worth stating plainly. Conformance is self-asserted, so §5
describes what an implementer claims and how anyone else reproduces it. And the
record has nowhere to put an aggregate score, which is deliberate; see §4.2.

### 1.2 Relationship to adjacent work

SuperGauge is designed to sit above these, not to replace any of them.

| Layer | Specification | SuperGauge's relationship |
|---|---|---|
| Runtime control | Agent Control Specification (ACS) | A `gates[]` entry may cite `source: acs` and carry an ACS checkpoint decision verbatim |
| Behaviour exposure | Evaluation Context Protocol (ECP) | An ECP-conformant agent supplies the trajectory and tool calls a measure computes over |
| Trace substrate | OpenTelemetry | `assurance.evidence.ledger` may reference OTel-shaped traces; see §8 |
| Inner-loop grading | Google's agent quality flywheel | The flywheel produces the measurements. The record captures the release decision the flywheel does not make |
| Where to fix | HarnessX D1–D9 | Orthogonal. SuperGauge measures say *how good*; D1–D9 says *where to change it*. A record may carry a D-tag as advisory |
| Agent discovery | A2A Agent Card | `subject.agent_card` may bind the well-known card digest and skill allowlist; see [`rfcs/0002-a2a-agent-card-binding.md`](rfcs/0002-a2a-agent-card-binding.md) (draft) |
| Supply-chain attestation | CycloneDX AIBOM, SLSA / in-toto | Optional `supply_chain` carries BOM and provenance digests; see [`rfcs/0003-supply-chain-aibom-slsa.md`](rfcs/0003-supply-chain-aibom-slsa.md) (draft) |

Three positions this specification shares with the wider field, and claims no
credit for: the party proposing a change must not grade it; a model
judge is a directional signal and not an oracle; anything checkable
deterministically should be checked deterministically, leaving the judge for
what resists it.

---

## 2. The record

An AQR is a YAML or JSON document. Field names are identical in both.

### 2.1 Skeleton

```yaml
supergauge: "0.1"                 # spec version this record conforms to
record_id: aqr_01J9F3QK7B2N       # unique, opaque
emitted_at: 2026-09-06T11:04:22Z  # RFC 3339, UTC

profile:   { ... }   # §2.2 — the bar this release was held to
subject:   { ... }   # §2.3 — what was measured
task_set:  { ... }   # §2.4 — what it was measured against
measures:  [ ... ]   # §2.5 — how it performed
gates:     [ ... ]   # §2.6 — what had to hold
assurance: { ... }   # §2.7 — why the above can be believed
decision:  { ... }   # §2.8 — who decided, and the way back
```

All eight blocks are REQUIRED. An emitter that cannot populate a block MUST
omit the record; a partial one asserts more than it can support.

### 2.2 `profile`

```yaml
profile:
  id: sg/coding-agent
  version: "0.1"
  tier: T2
```

The profile is the only thing entitled to state which gates are mandatory and
what floors they must clear (§4.3). Pinning its version is what lets a reader
reconstruct the bar months later, when the profile itself has moved on.

`tier` MUST be one of `T0`, `T1`, `T2` (§4.4).

### 2.3 `subject`

```yaml
subject:
  agent: acme-support-triage
  harness_digest: sha256:9c1e...        # the loop, not only the model
  code_digest: sha256:41ba...
  model:
    provider: anthropic
    id: claude-opus-5
    digest: sha256:77ab...              # OPTIONAL content pin
  authority:                            # REQUIRED — see below
    grant_digest: sha256:b830...
    acs_policy_version: "2.1"
    sandbox: docker
    egress: deny-by-default
    capabilities: [repo.read, "repo.write:branch", test.run]
  agent_card:                           # OPTIONAL - A2A discovery binding
    well_known_url: "https://agents.acme.example/.well-known/agent-card.json"
    card_digest: sha256:c0ff...
    version: "1.4.2"
    skill_ids: [triage, escalate]
```

`authority` is required because a record that pins only what the agent *is*,
and not what it was *permitted to do*, is unsound. An agent measured inside a
sandbox with default-deny egress and then deployed holding a standing
production credential produces a record that is schema-valid and materially
false. Implementations MUST populate `authority` from the policy in
force during measurement, and never from a declared intent.

`agent_card` is optional. When the subject is published for A2A discovery,
emitters MAY bind the well-known Agent Card URL, a digest of the card JSON at
ship time, an optional version or ETag, and a skill-id allowlist that MUST be
a subset of the skills on that card. The card is the discovery surface peers
read; it does not replace `authority`. Profiles MAY gate on the deterministic
measure `interop.agent_card_fresh`. See
[`rfcs/0002-a2a-agent-card-binding.md`](rfcs/0002-a2a-agent-card-binding.md)
(draft).

### 2.4 `task_set`

```yaml
task_set:
  manifest_digest: sha256:7d02...
  held_in: 34
  held_out: 12
  sealed: true                    # held-out unread by any optimizer
  canary_ids: [tsk_c1, tsk_c2]    # contamination probes
```

`sealed: true` asserts that no optimizer, tuning loop or prompt-authoring
process has read the held-out split. An emitter that cannot establish this MUST
report `sealed: false`.

### 2.5 `measures`

An array of results drawn from the measure registry (§3). Each entry:

```yaml
- id: reliability.pass_hat_k     # REQUIRED, registry id
  value: 0.66                    # REQUIRED, number or boolean
  split: held-out                # OPTIONAL
  n: 12                          # OPTIONAL, sample size
  k: 5                           # OPTIONAL, measure-specific parameters
  unit: usd                      # OPTIONAL
  pack: sg/injection@0.1         # OPTIONAL, versioned pack that produced it
```

A measure id not present in the registry MUST carry an `x-` prefix. Records
using `x-` measures may reach conformance L1 only (§5).

### 2.6 `gates`

```yaml
gates:
  - {id: policy.no_write_outside_repo, result: pass, source: acs}
  - {id: policy.no_pii_egress,         result: pass, source: acs}
  - {id: reliability.pass_hat_k,       floor: 0.60, result: pass}
  - {id: task.completion, split: held-out, floor: 0.80, result: pass}
```

`result` MUST be `pass` or `fail`. A gate backed by a measure MUST reference a
measure present in `measures[]`, and that measure MUST be `deterministic` in the
registry. **A judged measure may never back a gate.**

### 2.7 `assurance`

```yaml
assurance:
  judge:
    id: sg/rubric@0.3
    model: claude-sonnet-5
    human_agreement_kappa: 0.71
    sampled: 40
  evidence:
    ledger: .superqode/harness-protocol/
    format: superqode.harness-protocol/1     # or opentelemetry/1.x
    events: 4182
    replayable: true
  evaluator_independent: true
```

`evaluator_independent` asserts that whatever graded this run had access to the
artifact and resulting world state only, and not to the worker's own transcript,
plan or self-report. This is a distinct claim from `task_set.sealed`: sealing
prevents task leakage, independence prevents evidence fabrication. Both are
required at higher conformance levels because both failures have been measured
in production coding-agent sessions.

`judge` MAY be omitted when a record contains no judged measures.

### 2.8 `decision`

```yaml
decision:
  verdict: ship                       # ship | hold | reject
  actor: "priya@acme.example"
  rolls_back_to: sha256:2f7a...
  signature: ed25519:...              # OPTIONAL below L4, REQUIRED at L4
```

At tier `T2` the block additionally REQUIRES the three fields below, following
the Markdown Architectural Decision Record format, so that a later reader has
the question, the alternatives and the reasoning alongside the outcome:

```yaml
  question: "Promote candidate harness c_9f21 to the default review path?"
  options: ["promote", "extend canary to 25%", "reject"]
  rationale: "Held-out completion 0.83 against a 0.80 floor; pass^5 0.66 against 0.60."
```

### 2.9 Optional `supply_chain`

The eight blocks in §2.1 remain REQUIRED. An emitter MAY additionally include
a `supply_chain` object when it holds attestation artifacts for the release:

```yaml
supply_chain:
  aibom_digest: sha256:a1b0...
  aibom_format: "cyclonedx-1.6+aibom"
  slsa_provenance_digest: sha256:b2c1...
  provenance_format: "slsa/v1"
  mcp_servers:
    - {name: github, version: "2.1.0", digest: sha256:d4e3...}
```

Fields record digests and references only. SuperGauge does not generate bills
of materials or provenance. When a profile requires supply-chain evidence, L2
expects a present AIBOM digest covering models and tools in scope; L4 expects
signed BOM and provenance that an independent party can verify. See
[`rfcs/0003-supply-chain-aibom-slsa.md`](rfcs/0003-supply-chain-aibom-slsa.md)
(draft).

---

## 3. The measure registry

The core of this specification is small and changes rarely. The set of things
worth measuring is neither. They are separated deliberately.

Each registered measure lives in `measures/<id>.md` and declares:

| Field | Meaning |
|---|---|
| `id` | Dotted, stable, lowercase. Never reused for a different meaning |
| `type` | `deterministic` or `judged`. Only `deterministic` may back a gate |
| `computes` | Precisely what is calculated, including the failure cases |
| `evidence` | What must exist in the ledger for the value to be computable |
| `parameters` | Any measure-specific fields permitted in a record entry |
| `version` | Semantic. A change in meaning requires a new id, not a new version |

Registered measures at v0.1 are grouped under the four quality pillars in
general use — effectiveness, efficiency, robustness, safety — plus an assurance
group that describes the trustworthiness of the measurement itself.

| Group | Measures |
|---|---|
| Effectiveness | `task.completion` · `trajectory.valid` · `tool.correctness` · `interop.routing_invocation` · `interop.agent_card_fresh` · `answer.grounded` (judged) |
| Efficiency | `efficiency.cost_per_success` · `efficiency.tokens_per_success` · `efficiency.latency_per_success` |
| Robustness | `reliability.pass_hat_k` · `reliability.pass_at_k` · `robustness.recovery` · `robustness.multi_turn` (judged) |
| Safety | `policy.hard_rules` · `safety.injection_resistance` · `safety.tool_abuse` · `safety.isolation` |
| Assurance | `assurance.judge_agreement` · `assurance.holdout_sealed` · `assurance.evidence_complete` · `assurance.evaluator_independence` |

Twenty-one measures, nineteen of them deterministic. That ratio is not a
position this
specification argues for; it reflects an existing consensus that most agent
correctness is checkable without a model in the loop.

Proposing a measure is the primary way to contribute. See `rfcs/0000-template.md`
and `GOVERNANCE.md`.

---

## 4. Rules

### 4.1 The ship rule

> A record MAY carry `verdict: ship` only when every gate in `gates[]` has
> `result: pass`.
>
> Gates are deterministic. A judged measure may never satisfy one.
>
> A record whose `task_set.sealed` is false, or whose canary probes fired, MUST
> NOT carry `verdict: ship` at any measured value.

### 4.2 No single score

An AQR MUST NOT contain an aggregate quality score, and a conformant renderer
MUST NOT compute one. Gates pass or fail; every other measure is reported as a
profile with a tolerance. Averaging across measures destroys the information the
record exists to carry, and invites the failure this format is designed to
prevent, where a system optimises the summary while the behaviour drifts.

### 4.3 Where floors come from

**The core defines measures and never asserts a threshold. Floors are
profile-scoped and evidence-backed.**

A profile MAY publish a floor only once engagements or published research stand
behind it. Until then the measure is reported and the floor is left to the
implementer. A floor asserted without evidence is worse than no floor, because
it invites conformance to a number nobody has justified.

### 4.4 Tiers

Governance that does not scale with consequence becomes ceremony and is then
ignored. A profile declares a tier; the tier sets the mandatory gate set.

| Tier | Scope | Mandatory to ship |
|---|---|---|
| `T0` | Local, reversible, well covered by existing tests | Deterministic gates only |
| `T1` | Cross-service change, shared environment, external callers | Plus a sealed held-out split and a reliability floor |
| `T2` | Irreversible data, production impact, identity, payments, or a regulated decision | Plus a recorded human decision naming the artifact (§2.8), plus signature |

A profile MAY require more than its tier demands. It MUST NOT require less.

---

## 5. Conformance

Levels are cumulative and self-asserted. No percentage is published, and no
authority issues a badge. An implementation states the highest level it meets
and the conformance suite in `conformance/` reproduces the claim.

| Level | Requirement |
|---|---|
| **L1 — Emits** | Produces a schema-valid record carrying genuine digests for `profile`, `subject` and `task_set` |
| **L2 — Gated** | Deterministic gates enforced per §4.1; held-out split sealed with a manifest digest; canary probes present |
| **L3 — Calibrated** | Reliability reported as `pass^k`; judge version pinned with a human-agreement record; `assurance.evaluator_independence` asserted |
| **L4 — Verifiable** | Record signed, and independently replayable from the referenced ledger by a party that did not run it |

When a profile requires supply-chain evidence, L2 additionally expects
`supply_chain.aibom_digest` covering models and tools in scope, and L4
expects signed BOM and provenance digests that verify independently (see
[`rfcs/0003-supply-chain-aibom-slsa.md`](rfcs/0003-supply-chain-aibom-slsa.md)).
Those expectations do not invent new level numbers; they refine what the
profile asks of an existing level.

L4 is not a finishing touch. Severe monitor evasion — agents disabling tests and
reporting that a review passed — has been measured in roughly 2% of production
coding-agent sessions. Immutability alone only guarantees an unchanging record
of whatever was submitted. Independent replay is what distinguishes a trustworthy
record from a durable one.

---

## 6. Versioning

- The `supergauge` field names the spec version a record conforms to.
- Measure ids are permanent. A change in what a measure means requires a new id.
- Profiles are versioned independently and pinned per record.
- Packs are versioned and referenced as `<pack>@<version>` in a measure entry.
- Additive fields are minor. Removing or narrowing a field is major.

Until `1.0.0` this specification is unstable and may change in incompatible ways.

---

## 7. Security considerations

An AQR asserts that an agent met a bar. Anything that can write records can
assert that falsely, so:

- Digests MUST be computed over the artifacts the run used, never over declared
  intent.
- `authority` MUST reflect the policy in force, not the policy intended.
- An emitter SHOULD NOT run inside the same trust boundary as the agent being
  measured. Where it must, the record SHOULD NOT claim L3 or above.
- A signing key used for `decision.signature` MUST NOT be reachable by the agent
  under measurement.

---

## 8. Evidence formats

`assurance.evidence.format` names the shape of the referenced ledger. Two are
recognised at v0.1:

- `opentelemetry/1.x` - spans carrying agent run, tool call and model call
  events. Chosen because it is what the surrounding ecosystem already exports.
  For L4 replay to be actionable, emitters SHOULD follow the attribute and
  event contract in [`rfcs/0001-otel-evidence-mapping.md`](rfcs/0001-otel-evidence-mapping.md)
  (draft): tool invocations, policy/ACS decisions, attempt resets, task-set
  manifest digests, and measure-derivation markers. The RFC is a mapping over
  values a system already holds; it is not an OpenTelemetry product.
- `superqode.harness-protocol/1` - the native event ledger of the reference
  implementation, carrying protocol version, event id, sequence, session, run,
  harness id, timestamp and parent event on every event.

An implementation that already exports OTel can reach L1 without adopting any
particular runtime. That is intentional: a format that requires switching
runtimes before it can be tried does not get tried. Independent replay at L4
still requires the ledger to carry enough structure that deterministic gates
recompute identically; the OTel mapping RFC states what "enough" means in
practice.

Related draft bindings outside the ledger itself:
[`rfcs/0002-a2a-agent-card-binding.md`](rfcs/0002-a2a-agent-card-binding.md)
(Agent Card under `subject`) and
[`rfcs/0003-supply-chain-aibom-slsa.md`](rfcs/0003-supply-chain-aibom-slsa.md)
(optional `supply_chain` digests).

---

## 9. Reference implementation

SuperQode implements the emitter. Its promotion registry already carries the
staged → canary → activated lifecycle, digest matching, actor, rollback snapshot
and a policy decision at the promotion phase; the emitter projects that state
into an AQR. See the `conformance/` suite for what is verified.

An implementation of this specification is not required to be SuperQode, and
nothing in this document depends on it.

---

## 10. Acknowledgements

This specification borrows its structural approach from OpenTelemetry's split
between a small stable core and an open semantic-convention registry, and its
graded self-assertion model from SLSA. It is designed to compose with the Agent
Control Specification, the Evaluation Context Protocol and OpenTelemetry rather
than to compete with any of them.

Contributors are listed in `ACKNOWLEDGEMENTS.md`.
