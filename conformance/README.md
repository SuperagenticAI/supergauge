# Conformance

Levels are cumulative and self-asserted. An implementation states the highest
level it meets; this suite is how anyone else reproduces that claim.

```bash
pip install pyyaml jsonschema

python conformance/check.py path/to/record.yaml
python conformance/check.py path/to/record.yaml --level L2   # exit 1 below L2
```

`jsonschema` is optional. Without it the L1 check falls back to verifying that
the eight required blocks are present, which is weaker; install it for a full
L1 result.

## What each level checks

| Level | Checked here |
|---|---|
| **L1** | Validates against `schema/agent-quality-record.schema.json`, and the digests are full sha256 values, so a placeholder is caught |
| **L2** | Gates present and none of them model-graded; held-out split sealed, sized and fingerprinted; contamination probes recorded; no ship verdict over a failing gate; every gate with a floor points at a measure the record reports |
| **L3** | `reliability.pass_hat_k` reported with k of at least 2; `evaluator_independent` asserted; where any measure is model-graded, a judge record pinning an id, a model and a human agreement statistic |
| **L4** | Signed, a rollback target recorded, and a referenced ledger marked replayable with an event count |

## Evidence verification

The suite reads a record. It cannot see the run behind it, so several claims are
taken at face value and are only meaningful because a third party can go and
verify them against the ledger:

- Whether `sealed: true` is true. The digest proves the manifest did not change;
  it does not prove no optimizer read it.
- Whether `evaluator_independent: true` is true.
- Whether the ledger reproduces the verdict. L4 checks that a replayable ledger
  is referenced, and replaying it is the reader's job.

The L4 checks inspect the signature and ledger fields. Signature verification
and independent replay require access to keys and the referenced evidence.
The checker compares recorded minimum floors with their matching measures.
Profile completeness and recomputation from the evidence remain the work of
the release policy and evidence reviewer.

## Examples

`examples/l4-passing.yaml` reaches L4.

`examples/l3-integrity-soft-hold.yaml` is an L3-shaped soft-hold with
optional `assurance.integrity` (RFC 0005): deterministic gates pass,
judged evidence stays non-gating, and detailed review feedback triggers hold.

`examples/l2-assurance-export.yaml` shows optional `export.profiles[]`
metadata for AIUC-1 and EU Art. 50 mappings (not scores).

`examples/l1-only.yaml` is structurally reasonable and fails everything above
L1, on purpose. It carries an unsealed split with no probes, uses the
model-graded `answer.grounded` as a gate, and claims a ship verdict over a
failing `task.completion`. Useful as a regression fixture when changing the
checker.

## In CI

```yaml
- run: python conformance/check.py "$RECORD" --level L2 --require-ship --quiet
```

Pick the level your profile requires. `--quiet` suppresses the report and
leaves only the exit code. `--require-ship` requires at least L2, a recorded
ship verdict, a named actor and passing gates. A hold or reject record can meet
a conformance level while still blocking deployment.

The release system must authenticate the approver, bind the record to the
candidate artifact, enforce its profile, and verify the required evidence.
The actor field records an identity; the checker cannot authenticate it.

## Regression cases

```bash
python -m unittest discover -s conformance -p 'test_*.py'
```

`fixtures/release-policy.json` contains nine synthetic records covering ship,
hold, rejection, gate failures, sealing, probes, actor identity and recorded
floors. The test checks conformance and the deployment exit code separately.
