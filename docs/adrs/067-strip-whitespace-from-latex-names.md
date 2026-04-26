---
status: accepted
date: 2026-04-25
deciders: edouard
---

# ADR-067: Strip Whitespace from LaTeX Names in .name()

## Context and Problem Statement

The `.name()` method accepts a `latex` keyword for custom LaTeX rendering.
Trailing (or leading) whitespace in the latex string causes the renderer to
misclassify the name as "wide" or "compound", changing parenthesization
decisions. For example:

```python
v1 = mv.name(latex=r"x_{(+---)}")   # renders: x_{(+---)}^2
v2 = mv.name(latex=r"x_{(-+++) }")  # renders: \left(x_{(-+++) }\right)^2
```

The trailing space in `v2` makes the accent-width heuristic treat it as a
compound name, wrapping it in `\left(...\right)` before appending the
superscript. LaTeX itself ignores this whitespace, so the two names are
visually identical in math mode — but the expression tree renders them
differently.

## Decision Outcome

Two complementary fixes:

1. **Strip outer whitespace in `.name()`**: call `.strip()` on all name
   arguments (label, latex, unicode, ascii) before assignment. This handles
   cases like `.name("  v  ")` or `.name(latex="  \\theta  ")`.

2. **Fix `is_compound` to ignore spaces inside brace groups**: the heuristic
   `" " in latex` was triggering on spaces inside `{}` (e.g. `x_{(-+++) }`),
   which are meaningless in LaTeX math mode. The check now walks the string
   and only counts spaces at brace depth 0.

### Consequences

- Good, because whitespace-only differences can no longer cause rendering
  divergence — both outer whitespace and spaces inside brace groups are
  handled
- Good, because LaTeX ignores whitespace in math mode, so neither fix
  changes visual output
- Good, because the fixes are minimal and localised: `.name()` entry point
  and `Sym.is_compound` property
- Neutral: if someone intentionally used whitespace to force
  parenthesization, that escape hatch is removed. This is not a documented
  or intended use case; an explicit API (e.g. `compound=True`) would be the
  correct approach if needed in the future
