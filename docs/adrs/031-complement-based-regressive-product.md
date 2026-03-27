---
status: accepted
date: 2026-03-27
deciders: edouard
---

# ADR-031: Complement-Based Regressive Product

## Context and Problem Statement

The regressive product (meet) computes subspace intersections — dual to
the wedge (join). The classic definition uses the metric dual:
`(A* ∧ B*)*`. But this breaks in degenerate algebras like PGA where
the pseudoscalar is not invertible.

## Decision Outcome

The default `regressive_product` uses the **complement operator** (metric-
independent), not the metric dual:

```
A ∨ B = uncomplement(complement(A) ∧ complement(B))
```

This works in VGA, STA, PGA, and CGA. A separate `metric_regressive_product`
is available for users who specifically want the metric-dual version.

### API

```python
regressive_product(a, b)          # default, complement-based
metric_regressive_product(a, b)   # uses dual/undual (nondegenerate only)
meet = regressive_product         # alias
join = op                         # alias (wedge)
```

Renders as `A∨B` (unicode) / `A \vee B` (LaTeX), same precedence as wedge.

### Consequences

* Good, because it works in all signatures including PGA
* Good, because the complement operator was already implemented
* Good, because `meet`/`join` aliases are intuitive
* Neutral, because complement-based and metric-based may differ by sign
