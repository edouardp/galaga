---
status: accepted
date: 2026-03-31
deciders: edouard
---

# ADR-048: unit_fraction Notation Kind

## Context and Problem Statement

The default `unit()` rendering uses a hat accent (`\hat{B}` / `B̂`) for
single-glyph names. This is visually clean but means `display()` can't
show the intermediate step — the accent form is identical to the name,
so it gets deduplicated.

Users want to see `\hat{B} = \frac{B}{\lVert B \rVert} = e_{12}` in
notebooks, which requires the expression form to differ from the name.

## Decision Outcome

Add a `unit_fraction` notation kind that renders `unit(x)` as `x/‖x‖`
(unicode) or `\frac{x}{\lVert x \rVert}` (LaTeX). Users opt in per-algebra:

```python
from galaga.notation import NotationRule
alg.notation.set("Unit", "latex", NotationRule(kind="unit_fraction"))
alg.notation.set("Unit", "unicode", NotationRule(kind="unit_fraction"))
```

### Tactical, Not Generic

This is a purpose-built notation kind for `unit()`, not a generic
"fraction with transformed denominator" system. A generic approach would
support arbitrary denominator transforms (`x/f(x)`) but adds complexity
for a single use case. If more fraction-with-transform patterns emerge,
generalise then.

### Consequences

- Good, because `display()` can show the fraction form as a distinct step
- Good, because it's opt-in — default accent behaviour unchanged
- Good, because compound expressions auto-wrap: `(a + b)/‖a + b‖`
- Neutral, because it's a new notation kind (increases the kind vocabulary)
- Acceptable, because the tactical scope is documented for future reference
