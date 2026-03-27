---
status: accepted
date: 2026-03-26
deciders: edouard
---

# ADR-024: LaTeX-Driven Name Derivation

## Context and Problem Statement

When naming a multivector with `.name()`, users often know the LaTeX form
(e.g. `\theta`) but shouldn't have to manually specify the unicode (`θ`)
and ASCII (`theta`) equivalents.

## Decision Outcome

If `latex=` is provided to `.name()`, the unicode and ASCII names are
auto-derived using `LatexSymbols`. The `label` parameter is now optional
when `latex` is given. User-supplied `unicode=` and `ascii=` always
take precedence.

```python
# All three formats derived from latex alone
e1.name(latex=r"\theta")
# unicode: θ, ascii: theta, latex: \theta

# User override takes precedence
e1.name(latex=r"\theta", unicode="MY_THETA")
# unicode: MY_THETA, ascii: theta, latex: \theta
```

`LatexSymbols` covers Greek letters, math fonts (`\mathbf`, `\mathit`,
`\mathcal`, `\mathfrak`, `\mathbb`), common symbols, operators, relations,
and arrows.

### Consequences

* Good, because `.name(latex=r"\theta")` is all you need
* Good, because the mapping is explicit and testable (101 tests)
* Good, because user overrides are always respected
* Neutral, because unknown LaTeX commands fall back to the label or raw LaTeX
