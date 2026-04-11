---
status: accepted
date: 2026-04-11
deciders: edouard
---

# ADR-062: Rename "Lazy" to "Symbolic" Throughout the API

## Context and Problem Statement

The term "lazy" was inherited from functional programming (Haskell-style
lazy evaluation) but is a misnomer in galaga. In true lazy evaluation,
computation is deferred until the value is needed. Galaga's so-called
"lazy" multivectors do the opposite: they compute the numeric result
eagerly at every step, and *additionally* build a symbolic expression
tree alongside it.

The expression tree is not a deferred computation — it is a provenance
record. It tracks the dependency tree of how the current multivector was
derived: which operations were applied, to which operands, in what order.
This tree is used for display (showing `R = e^{-Bθ/2} = 0.877 - 0.479e₁₂`)
and for algebraic simplification, not for deferring work.

Calling this "lazy" confuses users who expect lazy semantics (deferred
evaluation, memoization, potential for infinite structures). The correct
term is "symbolic" — the multivector carries a symbolic representation
of its derivation alongside its concrete numeric value.

## Decision

Rename all internal and public uses of "lazy" to "symbolic", and "eager"
to "numeric":

- `_is_lazy` → `_is_symbolic`
- `_lazy_result` → `_symbolic_result`
- `lazy.py` → `symbolic.py` (old file kept as backward-compat shim)
- `lazy_unary`/`lazy_binary` → `symbolic_unary`/`symbolic_binary`
- `Multivector.symbolic()` replaces `.lazy()` as the primary method
- `Multivector.numeric()` replaces `.eager()` as the primary method
- `symbolic=` parameter added alongside `lazy=` on `basis_vectors`,
  `basis_blades`, `locals`, `pseudoscalar`, `blade`

The old names (`.lazy()`, `.eager()`, `lazy=` parameter) are kept as
deprecated aliases for backward compatibility.

## Consequences

- The API now accurately describes what the system does: numeric
  computation with an optional symbolic provenance tree
- New users see `symbolic=True` and understand they're getting expression
  trees, not deferred computation
- Existing code using `.lazy()` / `.eager()` / `lazy=True` continues to
  work unchanged
- Internal code reads more clearly: `_is_symbolic` immediately conveys
  "this MV carries an expression tree"
