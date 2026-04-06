---
status: accepted
date: 2026-03-30
deciders: edouard
---

# ADR-043: Notation-First Rendering Architecture

## Context and Problem Statement

The renderers (`render.py` for unicode, `latex_build.py` for LaTeX) have
accumulated hardcoded special cases that bypass the Notation system:

- `Gp` has smart spacing logic before the notation lookup
- `Unit` has hat-vs-fraction logic duplicated in two places
- `Exp`, `Log`, `Sqrt` have hardcoded rendering inside the `wrap` handler
- `Grade` has subscript logic inside the `wrap` handler
- `Div` has hardcoded slash rendering before the notation lookup

This means adding a new notation preset (like `functional()`) requires
checking every special case and adding `if rule.kind == "function"` guards.
The `Notation.functional()` fix exposed this — 8 operations needed individual
fixes because they bypassed the notation system.

## Current Architecture

```
render(node):
    if t is Gp: ...          # hardcoded
    if t is Unit: ...         # hardcoded
    if t is Div: ...          # hardcoded
    rule = notation.get(...)  # NOW check notation
    if rule.kind == "wrap":
        if t is Exp: ...      # hardcoded inside generic handler
        if t is Grade: ...    # hardcoded inside generic handler
```

## Proposed Architecture

```
render(node):
    rule = notation.get(...)  # ALWAYS check notation first
    dispatch(rule.kind):
        "function" → generic function renderer
        "infix"    → generic infix renderer
        "prefix"   → generic prefix renderer
        "postfix"  → generic postfix renderer
        "accent"   → generic accent renderer
        "wrap"     → generic wrap renderer
        "juxtaposition" → generic juxtaposition renderer
```

Special rendering behaviour (Gp spacing, Exp superscript, Unit hat-vs-fraction)
moves into the NotationRule itself via additional fields, not into the renderer.

## Consequences

- Good, because new notation presets work automatically
- Good, because rendering logic is in one place per kind
- Good, because NotationRule becomes the single source of truth
- Bad, because it's a significant refactor of two core files
- Risk, because 1335 tests must continue to pass

## Implementation Record

The motivation came from adding `Notation.functional()` (`935d728`, `b894135`)
which required 8 individual fixes because operations bypassed the notation
system. The refactor was implemented immediately after this ADR was written:

1. Refactored both `render.py` and `latex_build.py` — notation lookup first,
   then dispatch on `rule.kind`. Removed Gp and Unit pre-notation special
   cases. Structural cases (Sym, Scalar, Neg, ScalarMul, Add, Sub, Div)
   remain pre-notation as they have no notation rules. All 1335 tests passed
   unchanged. (`7e97491`)
2. Subsequent commits built on the new architecture without regressions:
   `unit_fraction` notation kind (`fd08736`), LNode-based scientific notation
   (`091483b`), postfix brace-wrapping fixes (`a63e917`, `c320db2`, `cd9ff92`),
   compound Sym name parenthesization (`a63e917`), inner_expr in Sym nodes
   (`0d1834e`), LaTeX functional notation escaping (`d22df22`).
