<p align="center">
  <img src="logo.png" alt="SuperGauge" width="150">
</p>

<h1 align="center">SuperGauge</h1>

<p align="center">
  <strong>The Agent Quality Record Protocol</strong><br>
  An open format for recording whether an agent is ready to ship:<br>
  what was measured, which conditions had to hold, and who signed off.
</p>

<p align="center">
  <a href="LICENSE"><img src="https://img.shields.io/badge/code-Apache--2.0-blue.svg" alt="Apache 2.0"></a>
  <a href="LICENSE-SPEC"><img src="https://img.shields.io/badge/spec-CC%20BY%204.0-lightgrey.svg" alt="CC BY 4.0"></a>
  <img src="https://img.shields.io/badge/version-0.1.0--draft-orange.svg" alt="0.1.0-draft">
</p>

---

## The problem

An agent mishandles a customer. Someone asks what was checked before it went
live, and the answer has to be assembled from chat logs and recollection.

Agents fail differently from software. One succeeds four times in five, takes a
different route on every run, and reports its own work as finished. The failures
teams describe are consistent:

| | |
|---|---|
| **The agent reports success** | The work never happened |
| **It picks the wrong tool** | Or calls the right one five times |
| **It answers confidently** | With nothing behind it |
| **It worked in the demo** | It has not worked since |
| **The bill went up** | Nobody can say what it bought |
| **Nothing stands before release** | Readiness is a judgement made under deadline |

Every one of these is measurable. Readiness is a decision a team makes, and
SuperGauge is the format that decision is written in, so anyone can check the
measurements later.

## The record

SuperGauge specifies one artifact: the **Agent Quality Record**. A single
document, written when somebody decides an agent may ship, stating what was
measured, what it was measured against, which conditions had to hold, whether
they held, who accepted the result, and which version to revert to.

```yaml
supergauge: "0.1"
profile: {id: sg/coding-agent, version: "0.1", tier: T2}

subject:
  agent: acme-support-triage
  harness_digest: sha256:9c1e...
  authority: {sandbox: docker, egress: deny-by-default, acs_policy_version: "2.1"}

task_set: {manifest_digest: sha256:7d02..., held_out: 12, sealed: true}

measures:
  - {id: task.completion,             value: 0.83, split: held-out, n: 12}
  - {id: reliability.pass_hat_k,      value: 0.66, k: 5}
  - {id: safety.injection_resistance, value: 1.00, pack: sg/injection@0.1}

gates:
  - {id: policy.no_pii_egress,   result: pass, source: acs}
  - {id: reliability.pass_hat_k, floor: 0.60, result: pass}

decision:
  verdict: ship
  actor: "priya@acme.example"
  rolls_back_to: sha256:2f7a...
```

Read [`SPEC.md`](SPEC.md) for the full format.

## Where it sits

The evaluation layer is well served. Platforms grade runs. The Agent Control
Specification bounds behaviour at runtime. Published quality frameworks close
the development loop and state that automated release decisions remain outside
their scope. The Evaluation Context Protocol lists signed reports and sealed
held-out manifests among the work it has not done.

Everyone measures. Nobody writes down the decision.

SuperGauge composes with those layers, and a system already exporting
OpenTelemetry traces can produce a valid record without changing runtimes.

## Four design decisions

**Results are reported as a profile.** Gates resolve to pass or fail. Every
other measure carries its own tolerance, and the format offers nowhere to put an
aggregate. Collapsing twenty measures into a single figure discards the detail
the record exists to preserve, and invites teams to optimise a headline while
the behaviour drifts.

**Thresholds belong to profiles.** The specification defines how each measure is
computed and leaves the acceptable value to a profile, which has to show the
evidence behind it. A figure with reasoning attached survives scrutiny; a round
number chosen for how it looks becomes a target everyone conforms to and nobody
can defend.

**Only deterministic measures block a release.** A model judge varies between
runs and can be influenced by the system it grades, so its output is recorded
against the release and reserved from the decision. Two conformant
implementations given the same evidence produce the same gate result.

**Conformance is self-asserted and third-party verifiable.** An implementer
states the level they meet, and the published suite lets anyone reproduce the
claim. The burden of proof stays on the implementation, which is what an
endorsement would quietly remove.

## Conformance

| Level | Reached when |
|---|---|
| **L1** | Schema-valid, carrying genuine digests and a recorded authority grant |
| **L2** | Deterministic gates enforced, held-out split sealed and fingerprinted, contamination probes present |
| **L3** | Reliability reported across repeated runs, judge version pinned, evaluator independence asserted |
| **L4** | Signed, and reproducible from the referenced ledger by an independent third party |

```bash
pip install pyyaml jsonschema
python conformance/check.py record.yaml --level L2
```

## Repository layout

| Path | Contents |
|---|---|
| [`SPEC.md`](SPEC.md) | The record, the release rule, tiers, conformance levels |
| [`schema/`](schema) | JSON Schema for validators |
| [`measures/`](measures) | The open registry, and the main place to contribute |
| [`profiles/`](profiles) | Domain bundles that set tiers and thresholds |
| [`packs/`](packs) | Adversarial case sets and assurance export profiles (AIUC-1, EU Art. 50) |
| [`conformance/`](conformance) | The L1 to L4 suite |
| [`rfcs/`](rfcs) | Proposals |
| [`docs/emitters/`](docs/emitters) | Peer-tool emit guides |
| [`ADOPTERS.md`](ADOPTERS.md) | Who is using the format |

## Interop / Emitters

Emit means serialise values you already hold into an Agent Quality Record.
SuperGauge does not replace your evaluation runner.

- Emitter guides for LangSmith, Google ADK, Inspect AI, Jev / System One, and
  SuperQode live under [`docs/emitters/`](docs/emitters/).
- When the ledger is OpenTelemetry-shaped, follow the draft mapping in
  [`rfcs/0001-otel-evidence-mapping.md`](rfcs/0001-otel-evidence-mapping.md)
  so L4 replay stays actionable.
- **A2A Agent Card:** draft binding for `subject.agent_card` (well-known URL,
  card digest, skill allowlist) in
  [`rfcs/0002-a2a-agent-card-binding.md`](rfcs/0002-a2a-agent-card-binding.md).
- **Supply chain:** optional `supply_chain` digests for AIBOM / CycloneDX and
  SLSA or in-toto provenance in
  [`rfcs/0003-supply-chain-aibom-slsa.md`](rfcs/0003-supply-chain-aibom-slsa.md).
- **Jev / System One:** assurance pinning (versioned model id, pack digest),
  judged Score/Noul mapping, and soft `decision.hold` when confidence is low, in
  [`rfcs/0004-jev-systemone-interop.md`](rfcs/0004-jev-systemone-interop.md).
  SuperGauge does not host or call Jev.
- **Assurance export:** map existing AQR evidence to AIUC-1 (A008 / B010 / B006)
  and EU Art. 50 transparency checklists via
  [`packs/assurance-export.md`](packs/assurance-export.md). Export profiles are
  not scores and do not replace deterministic gates.
- Judged peer scores may be recorded; only deterministic measures may gate.

## Contributing

The specification is governed narrowly and the registry is open. The range of
behaviour worth measuring exceeds any single team's experience, and the
practitioners who know what a sound test looks like are frequently not the
people who write specifications.

Proposing a measure is the main way in, and two accepted proposals earn a place
on the review rotation.

Two files are worth reading first. The measure definition for
[`reliability.pass_hat_k`](measures/reliability.pass_hat_k.md) sets the level of
detail a proposal needs, and the [RFC template](rfcs/0000-template.md) carries
the review checklist a submission is assessed against.

Contributions are made under a Developer Certificate of Origin sign-off
(`git commit -s`) in place of a contributor licence agreement. Authors retain
copyright, so a measure definition needs no approval from an employer's legal
team.

[`GOVERNANCE.md`](GOVERNANCE.md) records who approves what, and states which
parts of the surrounding work are commercial.

## Adoption

The format is open to any implementer, and the intention is to steward it with
practitioners from across the agent quality field, not from a single company.
[SuperQode](https://superqode.dev) and [SuperOptiX](https://superoptix.ai)
already emit records, and a tool may equally consume them without producing
any.

[`ADOPTERS.md`](ADOPTERS.md) lists who is using the format, and takes a pull
request from anyone who wants to be on it.

### An open invitation

A record format earns its value from how many tools speak it. Evaluation
platforms, agent frameworks, observability vendors, platform teams and audit
tooling are all welcome to take it up.

Three ways in. **Emit** records after an evaluation, which for most tools is a
serialiser over values they already hold. **Consume** records other tools
produce. **Shape** the registry by proposing a measure, a profile or an
adversarial pack.

Adoption carries no obligation, and a level you claim is one anyone can
reproduce from a record you publish.

## Status

Version 0.1.0-draft. The specification may change incompatibly before 1.0.0.
Measure identifiers, once published, are permanent regardless of version.

## Licence

Specification text under [CC BY 4.0](LICENSE-SPEC). Schemas, packs and the
conformance suite under [Apache 2.0](LICENSE).

Maintained by [Superagentic AI](https://super-agentic.ai/super-gauge).
