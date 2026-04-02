---
status: accepted
date: 2026-04-03
deciders: edouard
---

# ADR-050: LaTeX Scientific Notation via Notation Setting

## Context and Problem Statement

Python's `f"{c:g}"` and `format(c, ".3e")` produce strings like `1.2e-06`.
In LaTeX, the `e-06` renders with a full-size minus sign and spacing,
making it look like subtraction rather than an exponent.

## Decision Outcome

Add a `scientific` property to `Notation` that controls how scientific
notation is rendered in LaTeX. Three styles:

| Style | Output | Usage |
|---|---|---|
| `"times"` (default) | `1.2 \times 10^{-6}` | Standard LaTeX |
| `"cdot"` | `1.2 \cdot 10^{-6}` | Alternative convention |
| `"raw"` | `1.2e-06` | No conversion (for debugging) |

```python
alg.notation.scientific = "cdot"  # switch style
```

### Implementation

A regex substitution (`_latex_coeff`) runs on formatted coefficient strings,
driven by the algebra's notation setting. This is a string-level transform,
not an LNode pipeline operation.

### Consequences

- Good, because scientific notation renders correctly in LaTeX by default
- Good, because the style is configurable per-algebra via Notation
- Good, because `"raw"` mode available for debugging
- Neutral, because the regex is simple, well-tested, and produces correct output
- Neutral, because coefficient rendering is a separate path from the symbolic
  render tree — moving it into the LNode pipeline would require rewriting
  `Multivector.latex()` to produce LNodes instead of strings. Not planned
  unless the coefficient path needs context-dependent transforms.
