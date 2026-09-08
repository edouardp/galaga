---
status: accepted
date: 2026-03-25
deciders: edouard
---

# ADR-014: Fixed-Point Simplification

For Galaga 2, ADR-077 retains fixed-point structural rewriting but narrows
the rules and removes dependence on legacy node types and hidden bindings.
The migrated contracts explicitly distinguish numeric identities from
promised tree reductions; see
[ADR-114](114-grade-inspection-and-bounded-simplification-contracts.md).

## Context and Problem Statement

How should symbolic expression simplification work? A single pass may not
catch all simplifications (e.g., after one rewrite, a new pattern may emerge).

## Decision Drivers

* Simplification rules are local rewrites (e.g., `~~x → x`, `x * 1 → x`)
* One pass may expose new opportunities (e.g., after `~~x → x`, a `grade` rule may apply)
* Must terminate — infinite loops are unacceptable
* Must be predictable — same input always gives same output

## Decision Outcome

`simplify()` applies `_simplify()` in a loop until the expression stabilises
(fixed-point iteration). Equality is checked structurally via `_eq()`, which
compares tree shapes and names without numeric evaluation.

```python
def simplify(expr):
    prev = None
    e = expr
    while not (prev is not None and _eq(prev, e)):
        prev = e
        e = _simplify(e)
    return e
```

### Consequences

* Good, because multi-step simplifications work automatically
* Good, because structural equality avoids expensive numeric evaluation
* Good, because termination is guaranteed (each pass either changes the tree or stops)
* Bad, because `_eq()` must handle every expression type — missing a type causes infinite loops
