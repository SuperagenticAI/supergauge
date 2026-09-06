---
id: assurance.judge_agreement
version: "0.1"
type: deterministic
group: assurance
parameters: []
author: Superagentic AI
---

# `assurance.judge_agreement`

Agreement between a model judge and a sampled human review, on the same items,
under the same rubric.

## Why it exists

Every judged measure in a record inherits the judge's reliability, and an
unmeasured judge produces numbers of unknown meaning. Judge output also drifts:
the same judge, the same items, a different day, and the ranking moves. Pinning
a version bounds that. Measuring agreement quantifies what the version is worth.

This measure is deterministic even though it grades a judge, because computing
agreement between two label sets is arithmetic.

## Computation

Sample items the judge has already scored. Have a human score the same items
blind to the judge's verdict. Report Cohen's kappa:

```
kappa = (p_observed - p_chance) / (1 - p_chance)
```

Report the sample size alongside. Below thirty items the interval is too wide to
act on.

The human MUST be blind to the judge's output. A reviewer shown the verdict
first is measuring their own agreeableness.

### Interpretation

Kappa is a correlation, not a grade. A judge at 0.7 is useful for ranking
candidates and unsuited to deciding a release, which is why judged measures
cannot back a gate at any kappa.

### Failure cases

| Case | Required behaviour |
|---|---|
| Human labels came from the judge's own output | Do not report |
| Fewer than 30 sampled items | Report with `n`, and treat as indicative |
| The rubric changed between passes | Do not report; the passes are incomparable |

## Evidence required

The sampled item ids, both label sets, the rubric version, and the pinned judge
id and model.

## Record entry

```yaml
- id: assurance.judge_agreement
  value: 0.71
  n: 40
```

## Backing a gate

Permitted. A profile MAY require a minimum kappa before judged measures are
reported at all.

## Related

`answer.grounded` and `robustness.multi_turn` are the judged measures this
qualifies.
