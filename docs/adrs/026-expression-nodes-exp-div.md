---
status: accepted
date: 2026-03-26
deciders: edouard
---

# ADR-026: Expression Nodes for Exp, Div, ScalarDiv

## Context and Problem Statement

`exp()`, multivector division, and scalar division were evaluating eagerly
even when operands were lazy. This broke the symbolic workflow — `exp(-Bθ/2)`
would compute a numeric rotor instead of showing the symbolic expression.

## Decision Outcome

Three new expression nodes:

- `Exp(x)` — renders as `exp(x)` / `e^{x}` in LaTeX
- `Div(a, b)` — renders as `a/b` / `\frac{a}{b}` in LaTeX
- `ScalarDiv(x, k)` — renders as `x/k` / `\frac{x}{k}` in LaTeX

All module-level functions (`exp`, `gp`, `op`, `reverse`, `involute`,
`conjugate`, `grade`, `dual`, `undual`, `unit`, `inverse`, `even_grades`,
`odd_grades`, `squared`, `sandwich`, `commutator`, `anticommutator`,
`lie_bracket`, `jordan_product`, `left_contraction`, `right_contraction`,
`hestenes_inner`, `doran_lasenby_inner`, `scalar_product`) check for lazy
inputs and build expression trees when appropriate.

### Consequences

* Good, because `exp(-Bθ/2)` renders symbolically
* Good, because `ℏ/(mₑc)` preserves all names in the expression
* Good, because `v/2` renders as a fraction, not `0.5v`
* Good, because eager inputs take the fast numeric path (zero overhead)

### Additional: `**2` delegates to `squared()`

`mv ** 2` is special-cased to use the `Squared` node, so `v**2` renders
as `v²` rather than `vv`. Other integer powers use repeated multiplication.

### Additional: `norm()` returns lazy scalar MV

When the input is lazy, `norm(v)` returns a lazy scalar MV wrapping a
`Norm` expr (`‖v‖`), rather than a plain float. Eager inputs still
return a float for backward compatibility.

### Additional: `sym()` name is optional

`sym(mv)` with no name returns a lazy copy. `sym(mv).name(latex=r"\hat{n}")`
chains naturally. `sym(mv, "a")` still works as before.
