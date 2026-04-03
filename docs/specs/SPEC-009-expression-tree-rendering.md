# SPEC-009: Expression Tree Rendering (SlashFrac, Frac, Sup Interactions)

## Intent

The LaTeX rendering pipeline has three phases: build (Expr → LNode),
rewrite (LNode → LNode), emit (LNode → string). Fractions, superscripts,
and their interactions require careful handling across phases.

## Rules

### Rule 1: Frac Rendering

`Div` and `ScalarDiv` Expr nodes produce `Frac` LNodes in the build phase.

| Expr | LNode | Emitted |
|---|---|---|
| `Div(a, b)` | `Frac(a, b)` | `\frac{a}{b}` |
| `ScalarDiv(a, 2)` | `Frac(a, Text("2"))` | `\frac{a}{2}` |

### Rule 2: Frac → SlashFrac in Superscripts

The rewrite phase converts `Frac` to `SlashFrac` when inside a `Sup` node.

| Before rewrite | After rewrite | Emitted |
|---|---|---|
| `Sup(e, Frac(θ, 2))` | `Sup(e, SlashFrac(θ, 2))` | `e^{θ/2}` |

### Rule 3: SlashFrac Disambiguation

After the main rewrite, a second pass wraps `SlashFrac` in `Parens` when
it has siblings in a `Seq` (indicating it's part of a larger expression).

| Context | Wrapped? | Example |
|---|---|---|
| Standalone in Sup | No | `e^{a/2}` |
| With siblings in Sup | Yes | `e^{(a/2) b}` |
| Leading minus only | No | `e^{-a/2}` |

A leading `Text("-")` does NOT count as a sibling for disambiguation.

### Rule 4: Negation Hoisting

When a `Frac` with a negated numerator is converted to `SlashFrac`, the
negation is hoisted: `-a/2` not `(-a)/2`.

| Before | After |
|---|---|
| `Frac(Seq(["-", "a"]), "2")` in Sup | `Seq(["-", SlashFrac("a", "2")])` |

### Rule 5: Frac Over 1

`Frac(x, Text("1"))` simplifies to `x` (the denominator is removed).

### Rule 6: Nested Parens Collapse

`Parens(Parens(x))` collapses to `Parens(x)`.

### Rule 7: Exp Rendering

`Exp(x)` produces `Sup(Text("e"), build(x))`. The exponent goes through
the rewrite phase, so any `Frac` inside becomes `SlashFrac`.

| Expr | Final output |
|---|---|
| `Exp(ScalarDiv(θ, 2))` | `e^{θ/2}` |
| `Exp(Gp(ScalarDiv(a, 2), b))` | `e^{(a/2) b}` |
| `Exp(Neg(Gp(B, ScalarDiv(θ, 2))))` | `e^{-B θ/2}` |

### Rule 8: Rewrite Idempotence

Applying `rewrite()` twice produces the same result as applying it once.

### Rule 9: SlashFrac in Rewrite

The rewrite pass handles `SlashFrac` nodes (from a previous rewrite)
by passing them through unchanged. This ensures idempotence.
