---
status: accepted
date: 2026-04-03
deciders: edouard
---

# ADR-050: LaTeX Scientific Notation via Regex Rewrite

## Context and Problem Statement

Python's `f"{c:g}"` and `format(c, ".3e")` produce strings like `1.2e-06`.
In LaTeX, the `e-06` renders with a full-size minus sign and spacing,
making it look like subtraction rather than an exponent.

## Decision Outcome

Apply a regex substitution (`_latex_coeff`) to coefficient strings in the
LaTeX rendering path, converting `1.2e-06` to `1.2 \times 10^{-6}`.

### Why Regex (Tactical)

The proper solution would be to produce structured LNodes (`Seq`, `Sup`,
`Text`) for scientific notation, so the three-phase render pipeline handles
it like any other expression. However, coefficient rendering currently
bypasses the LNode pipeline entirely — it's string concatenation in
`Multivector.latex()`. Moving it into the pipeline is a larger refactor.

The regex is a bridge: it runs after `format()` produces the string but
before it's assembled into the final LaTeX. It handles all standard Python
scientific notation formats (`e`, `E`, `+`, `-`).

### Future Improvement

Move coefficient rendering into the LNode pipeline:
1. A concrete MV's coefficients would produce `Seq([Text("1.2"), Text(r" \times "), Sup(Text("10"), Text("-6"))])` instead of `Text("1.2e-06")`
2. The existing emit/rewrite passes handle it from there
3. The regex becomes unnecessary

### Consequences

- Good, because `1.2 \times 10^{-6}` renders correctly in all LaTeX contexts
- Good, because it handles both default `:g` and explicit `coeff_format` paths
- Neutral, because the regex is simple and well-tested
- Bad, because it's a string-level hack outside the render tree architecture
- Acceptable, because the scope is narrow and the future path is documented
