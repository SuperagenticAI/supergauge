---
rfc: 0000
title: <short noun phrase>
status: draft          # draft | accepted | rejected | superseded
surface: measure       # measure | profile | pack | conformance | spec
author: <name>
created: <YYYY-MM-DD>
---

# RFC 0000 — <title>

## Summary

One paragraph. What is being added, and to which surface.

## Problem

What goes unrecorded or unverifiable today. Prefer a failure you have actually
seen to one you can imagine. If you have a measured rate or a public incident,
cite it here.

## Proposal

The change itself. For a measure, this section is the measure file — follow
`measures/reliability.pass_hat_k.md`, which is the reference for the level of
detail expected. Vague computation is the most common reason an RFC is sent
back.

## Deterministic or judged

State which, and defend it. A measure is `deterministic` only if two conformant
implementations, given the same evidence, must produce the same value. If a
model is consulted anywhere in the computation, it is `judged`, and it may not
back a gate.

## Evidence required

What must exist in the ledger for this to be computable. If it needs evidence
no current implementation captures, say so — that is a legitimate proposal, but
it changes the review.

## Cost

Runs, tokens or wall time this adds relative to a single evaluation pass. A
measure that triples evaluation cost needs to earn it.

## Failure cases

How the measure behaves when the evidence is incomplete, when a run errors for
infrastructure reasons, and at parameter boundaries. Under-specified failure
behaviour is how two implementations silently disagree.

## Alternatives considered

Including doing nothing, and including any existing measure this overlaps with.
If it overlaps, say why a new id is better than extending the existing one —
remember that measure ids are permanent and never change meaning.

## Prior art

Papers, specifications or products that measure this already. Adopting an
established definition is preferred over inventing one; where you diverge from
prior art, say where and why.

## Open questions

Anything you want reviewers to decide rather than rubber-stamp.

---

### Review checklist

- [ ] `id` is dotted, lowercase, and not a rename of an existing measure
- [ ] Computation is unambiguous enough for two implementations to agree
- [ ] `deterministic` / `judged` is correctly classified and defended
- [ ] Failure cases are specified
- [ ] Evidence requirements are stated
- [ ] No floor or threshold is asserted (floors are profile-scoped, SPEC §4.3)
- [ ] Commits are DCO signed off
