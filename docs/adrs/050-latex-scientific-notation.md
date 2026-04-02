---
status: accepted
date: 2026-04-03
deciders: edouard
---

# ADR-050: LaTeX Scientific Notation via LNodes and Notation Setting

## Context and Problem Statement

Python's `f"{c:g}"` and `format(c, ".3e")` produce strings like `1.2e-06`.
In LaTeX, the `e-06` renders with a full-size minus sign and spacing,
making it look like subtraction rather than an exponent.

## Decision Outcome

Coefficient rendering in `Multivector.latex()` now produces LNodes
(`Text`, `Seq`, `Sup`) instead of raw strings. Scientific notation like
`1.2e-06` becomes `Seq([Text("1.2 \\times "), Sup(Text("10"), Text("-6"))])`,
which emits as `1.2 \times 10^{-6}`.

The style is controlled by `Notation.scientific`:

| Style | Output | Usage |
|---|---|---|
| `"times"` (default) | `1.2 \times 10^{-6}` | Standard LaTeX |
| `"cdot"` | `1.2 \cdot 10^{-6}` | Alternative convention |
| `"raw"` | `1.2e-06` | No conversion |

```python
alg.notation.scientific = "cdot"  # switch style
```

### Implementation

- `_sci_lnode()` parses a formatted number string and returns an LNode tree
- `_coeff_lnode()` builds a complete coefficient × blade term as an LNode
- `Multivector.latex()` builds LNodes per term, then emits them
- The `Sup(Text("10"), Text("-6"))` is a proper render tree node, handled
  by the existing emit pipeline

### Consequences

- Good, because scientific notation is rendered via the LNode tree, not regex
- Good, because the style is configurable per-algebra via Notation
- Good, because no special-case string transforms to maintain
- Good, because new coefficient formatting paths automatically get correct rendering
