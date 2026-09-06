# SuperGauge

**An open format for the agent release record.**

Your evaluation passed. Your agent shipped. Something went wrong in production.
What document do you hand the person asking what was checked before release?

SuperGauge defines that document: the **Agent Quality Record**. One file,
emitted when somebody decides an agent may ship, stating what was measured,
against what, which rules had to hold, whether they held, who decided, and how
to get back.

```yaml
supergauge: "0.1"
profile: {id: sg/coding-agent, version: "0.1", tier: T2}

subject:
  agent: acme-support-triage
  harness_digest: sha256:9c1e...
  authority: {sandbox: docker, egress: deny-by-default, acs_policy_version: "2.1"}

task_set: {manifest_digest: sha256:7d02..., held_out: 12, sealed: true}

measures:
  - {id: task.completion,          value: 0.83, split: held-out, n: 12}
  - {id: reliability.pass_hat_k,   value: 0.66, k: 5}
  - {id: safety.injection_resistance, value: 1.00, pack: sg/injection@0.1}

gates:
  - {id: policy.no_pii_egress,   result: pass, source: acs}
  - {id: reliability.pass_hat_k, floor: 0.60, result: pass}

decision:
  verdict: ship
  actor: "priya@acme.example"
  rolls_back_to: sha256:2f7a...
```

Read [`SPEC.md`](SPEC.md).

## Why this and not another scorecard

The evaluation layer is crowded and good. Platforms grade runs. The Agent
Control Specification bounds behaviour at runtime. Google's agent quality
flywheel closes the development inner loop and says outer-loop release decisions
are future work. The Evaluation Context Protocol lists signed reports and sealed
held-out manifests as work it has not done.

Everyone measures. Nobody writes down the decision.

That gap is where this sits. SuperGauge composes with all of the above rather
than replacing any of them — an implementation already exporting OpenTelemetry
can emit a valid record without changing runtimes.

## What it refuses to do

- **No single quality score.** Gates pass or fail; everything else is a profile
  with a tolerance. Averaging destroys the information the record exists to carry.
- **No floors in the core.** The specification defines measures and never
  asserts a threshold. Floors live in profiles and must be evidence-backed.
- **No judged gate.** A model judge is a directional signal. Only deterministic
  measures may block a release.
- **No certification.** Conformance is self-asserted across four levels and
  independently verifiable. Nobody issues a badge.

## Layout

```
SPEC.md          the record, the ship rule, tiers, conformance
schema/          JSON Schema for validators
measures/        the open registry — the main place to contribute
profiles/        domain bundles that set tiers and floors
packs/           adversarial and fault-injection case sets
conformance/     the L1–L4 suite
rfcs/            proposals
```

## Contributing

The core is held tightly; the registry is open. Proposing a measure is the
main way in, and two accepted proposals earns a review seat.

Start from [`measures/reliability.pass_hat_k.md`](measures/reliability.pass_hat_k.md),
which is the reference for the detail expected, and
[`rfcs/0000-template.md`](rfcs/0000-template.md).

DCO sign-off (`git commit -s`), no CLA — you keep your copyright and you do not
need your employer's legal team to approve a measure definition.

[`GOVERNANCE.md`](GOVERNANCE.md) states who approves what, and says plainly
which parts of the surrounding work are commercial.

## Status

`0.1.0-draft`. Unstable — it may change incompatibly before `1.0.0`. Measure
ids, once published, are permanent regardless of version.

## Licence

Specification text CC BY 4.0. Schemas, packs and conformance suite Apache-2.0.

Maintained by [Superagentic AI](https://super-agentic.ai).
