---
status: superseded
date: 2026-03-25
deciders: edouard
superseded-by: ADR-018
---

# ADR-013: Symbolic Drop-In Replacement Pattern

> **Note:** This ADR is partially superseded by [ADR-018](018-unified-naming-evaluation-semantics.md).
> The drop-in pattern still exists, but the detection logic now checks for lazy
> `Multivector` objects (via `_is_symbolic()`) in addition to `Expr` instances.
> `sym()` returns a `Multivector` with `_is_symbolic=True`, not an `Expr`.

## Context and Problem Statement

How should the symbolic layer relate to the numeric layer? Users shouldn't
need to learn a different API for symbolic vs numeric computation.

## Decision Drivers

* The same code should work with both numeric and symbolic inputs
* Wrapping a value with `sym()` should be the only change needed
* The symbolic layer should have zero overhead for numeric inputs
* Expression trees should build automatically from operator overloading

## Decision Outcome

Every function in `galaga.symbolic` is a drop-in replacement for its `galaga.algebra`
counterpart. Each function checks if any argument is an `Expr`:

- If yes → build the corresponding expression tree node
- If no → delegate directly to `galaga.algebra` with zero overhead

```python
# ga.symbolic.gp
def gp(a, b):
    if isinstance(a, Expr) or isinstance(b, Expr):
        return Gp(_ensure_expr(a), _ensure_expr(b))
    return _alg.gp(a, b)
```

Operators (`*`, `^`, `~`) on `Expr` objects build trees automatically, so
`R * v * ~R` produces `Gp(Gp(R, v), Reverse(R))` without any special syntax.

### Consequences

* Good, because `from galaga import symbolic as sym` is a drop-in replacement
* Good, because numeric code has zero symbolic overhead
* Good, because expression trees build naturally from operators
* Bad, because every new operation needs both a numeric and symbolic implementation
