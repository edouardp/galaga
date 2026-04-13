---
status: accepted
date: 2026-04-13
deciders: edouard
---

# ADR-065: Operation Registry Breaks algebra↔expr Circular Dependency

## Context and Problem Statement

`algebra.py` and `expr.py` had a circular import: algebra imported expr to
build expression trees, and expr imported algebra to evaluate them. This was
fragile, scattered symbolic dispatch across ~40 `_sym.*` references in
algebra.py, and made adding new operations require changes in both modules.

## Decision

Introduce `ops.py` as a leaf module (depends on nothing except stdlib) that
provides:

1. **`@ga_op` decorator** — registers operations with metadata (name, arity,
   grade rule) in a `GA_OPS` dict. The wrapper handles symbolic dispatch
   automatically.

2. **`register_symbolic_handler`** — called by `expr.py` at import time to
   map operation names to expression node classes.

3. **`register_sym_factory` / `make_sym` / `is_sym`** — callbacks for Sym
   node construction, so algebra.py can build expression tree leaves without
   importing expr.py.

4. **`build_expr`** — looks up a handler by name and calls it, replacing
   all direct `_sym.NodeClass(...)` calls in algebra.py.

The dependency graph becomes: `algebra.py → ops.py ← expr.py`. No cycles.

## Consequences

- `algebra.py` has zero imports from `expr.py`.
- Adding a new GA operation requires: `@ga_op` in algebra.py, one entry in
  `_NODE_NAMES`, one entry in `_HANDLER_MAP` (both in expr.py). Invariant
  tests catch omissions.
- The `@ga_op` wrapper handles symbolic dispatch uniformly — no more inline
  `if x._is_symbolic` branches for registered operations.
- Operator overloads (`__add__`, `__mul__`, etc.) use `build_expr()` for
  arithmetic node construction.
- Bare `Expr` objects are no longer accepted as operands to Multivector
  operators. `NotImplemented` is returned for non-MV, non-scalar types.
