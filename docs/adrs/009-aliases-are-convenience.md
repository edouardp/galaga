---
status: partially superseded by 074
date: 2026-03-25
deciders: edouard
---

# ADR-009: Aliases Are Convenience, Not Separate Implementations

> ADR-074 retains same-object aliases but reverses the primary direction for
> Galaga 2: long, explicit operation names are canonical and short names are
> compatibility or user-convenience aliases.

## Context and Problem Statement

Users coming from different GA backgrounds expect different names for the same
operation. Should we provide aliases, and if so, how?

## Decision Drivers

* `wedge` and `op` mean the same thing
* `rev` and `reverse` mean the same thing
* `normalize` and `unit` mean the same thing
* Aliases should not diverge — they must be the same function object

## Decision Outcome

Aliases are literally the same function object, not wrappers:

```python
wedge = op
outer_product = op
rev = reverse
normalize = unit
normalise = unit
geometric_product = gp
inner_product = hestenes_inner
```

### Consequences

* Good, because no maintenance burden — one implementation, many names
* Good, because `wedge is op` is `True` — no hidden differences
* Good, because users can import whichever name they prefer
