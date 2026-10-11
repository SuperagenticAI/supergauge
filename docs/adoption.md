# Adopt Agent Quality Records

Start with one agent and your current evaluation stack. Agree the release
criteria and name the owner before running the suite.

1. Version the dataset and protect the held-out split from tuning.
2. Classify each evaluator as deterministic or model-graded.
3. Emit the subject, permissions, dataset digest, measures, gate results and
   decision from the values your system holds. Link the evidence ledger.
4. Validate the record and check the recorded approval in your deployment job.

## SuperOptiX evaluation path

```bash
super agent evaluate developer --gauge-out record.yaml
```

The current evaluation path starts on hold with empty gates and emits at L1.
Optional Jev advice can hold or reject a candidate. Acceptance retains an
existing approval only where deterministic checks permit it. Heuristic
fallbacks identify their source and confidence proxy separately.

## Release check

Use the protocol checker from a pinned repository revision:

```bash
python conformance/check.py record.yaml --level L2 --require-ship --quiet
```

Install `pyyaml` and `jsonschema` before running the checker. This path runs
independently of the agent runtime and harness.

L2 requires deterministic gates, a sealed held-out split and contamination
probes. A hold or reject record can meet a level while blocking deployment.
The release check also requires a ship verdict and a named actor. Your release
system must authenticate that actor, enforce the profile and bind the record
to the candidate artifact.

Recorded minimum floors are compared with their matching measures. Profile
completeness, evidence recomputation, signature verification and ledger replay
require the corresponding release controls and reviewers.

## Handover

Keep the dataset manifest, labelled cases, rubric, baseline and candidate
records, CI configuration and rollback procedure in client-owned storage.
Demonstrate that a failed check and a hold decision each block deployment.
Train an owner to rerun the suite and add cases from incidents.
