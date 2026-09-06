# Governance

This document says who decides what, and states plainly which parts of this
project are commercial. It is written up front so that nobody contributes under
a mistaken impression of what they are contributing to.

## Scope of this repository

This repository contains a specification, its schemas, a measure registry,
profiles, evaluation packs and a conformance suite. **It contains no product
code.** The implementations live in their own repositories under their own
licences.

## Surfaces, and who may change them

| Surface | Who may propose | Who must approve |
|---|---|---|
| `measures/` | Anyone | One measure-group reviewer |
| `profiles/` | Anyone | One measure-group reviewer |
| `packs/` | Anyone | One measure-group reviewer |
| `conformance/` | Anyone | One core reviewer |
| `SPEC.md`, `schema/` | Anyone | Two core reviewers, one of whom did not author the change |

The core is held tightly on purpose. A specification that changes as easily as
its registry cannot be pinned, and a record that pins an unstable spec version
means nothing.

The registry is open on purpose. The set of things worth measuring about an
agent is larger than any one team's experience of it, and the people who know
what a good test looks like are mostly not the people who write specifications.

## Becoming a reviewer

Two accepted measure or pack RFCs earns a seat on the measure-group review
rotation. That seat carries real authority over `measures/`, `profiles/` and
`packs/`: your approval merges a change.

Core reviewers are appointed, and the current list is in `CODEOWNERS`.

## Contributing terms

- **DCO sign-off, not a CLA.** Sign your commits with `git commit -s`. You keep
  your copyright. No assignment is requested, so you do not need your employer's
  legal team to approve a measure definition.
- Specification text is **CC BY 4.0**. Schemas, packs and the conformance suite
  are **Apache-2.0**.
- Contributors are credited by name in `ACKNOWLEDGEMENTS.md` and against the
  measures they authored.

## What is commercial, and therefore not contributable

Superagentic AI maintains this specification and also sells services around it.
Those are separate, and the boundary is:

**In this repository, free and open to contribution:**
the record format, the ship rule, the measure registry, published profiles,
starter evaluation packs, the conformance suite.

**Commercial, and not part of this repository:**

- Consulting engagements that build a task set, calibrate floors and wire gates
  into a customer's pipeline.
- Calibration data accumulated across engagements. Where that data supports a
  floor well enough to publish, the floor is contributed back to `profiles/`;
  the underlying dataset is not.
- Assessment benchmarking against other organisations.
- Extended adversarial packs beyond the published starter sets.
- Hosted or managed running of any of the above.

Nothing here restricts anyone else from offering the same services. The
specification is not a lead magnet with a gated tier, and there is no
"enterprise edition" of the record format. If that changes, it will change in
this file first.

## Decision process

Changes to `SPEC.md` or `schema/` require an RFC in `rfcs/`. Everything else may
be a pull request that follows the templates in `measures/` and `packs/`.

An RFC is accepted when the required approvals are recorded and no core reviewer
has an unresolved objection. Objections must state what would resolve them.

## Stability

Until `1.0.0` this specification may change incompatibly. Measure ids, once
published, are permanent regardless of version: if what a measure means changes,
it gets a new id. Records in the wild must remain interpretable.
