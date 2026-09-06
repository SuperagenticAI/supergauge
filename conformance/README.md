# Conformance

Levels are cumulative and self-asserted. An implementation states the highest
level it meets; this suite is how anyone else reproduces that claim.

```bash
pip install pyyaml jsonschema

python conformance/check.py path/to/record.yaml
python conformance/check.py path/to/record.yaml --level L2   # exit 1 below L2
```

`jsonschema` is optional. Without it the L1 check falls back to verifying that
the eight required blocks are present, which is weaker; install it for a real
L1 result.

## What each level checks

| Level | Checked here |
|---|---|
| **L1** | Validates against `schema/agent-quality-record.schema.json`, and the digests are full sha256 values rather than placeholders |
| **L2** | Gates present and none of them model-graded; held-out split sealed, sized and fingerprinted; contamination probes recorded; no ship verdict over a failing gate; every gate with a floor points at a measure the record reports |
| **L3** | `reliability.pass_hat_k` reported with k of at least 2; `evaluator_independent` asserted; where any measure is model-graded, a judge record pinning an id, a model and a human agreement statistic |
| **L4** | Signed, a rollback target recorded, and a referenced ledger marked replayable with an event count |

## What it deliberately does not check

The suite reads a record. It cannot see the run behind it, so several claims are
taken at face value and are only meaningful because a third party can go and
verify them against the ledger:

- Whether `sealed: true` is true. The digest proves the manifest did not change;
  it does not prove no optimizer read it.
- Whether `evaluator_independent: true` is true.
- Whether the ledger reproduces the verdict. L4 checks that a replayable ledger
  is referenced, and replaying it is the reader's job.

This is the point of L4 rather than a gap in it. A record is an assertion, and
an immutable assertion is still an assertion. Independent replay is what turns
it into evidence.

## Examples

`examples/l4-passing.yaml` reaches L4.

`examples/l1-only.yaml` is structurally reasonable and fails everything above
L1, on purpose. It carries an unsealed split with no probes, uses the
model-graded `answer.grounded` as a gate, and claims a ship verdict over a
failing `task.completion`. Useful as a regression fixture when changing the
checker.

## In CI

```yaml
- run: python conformance/check.py "$RECORD" --level L2 --quiet
```

Pick the level your profile requires. `--quiet` suppresses the report and
leaves only the exit code.
