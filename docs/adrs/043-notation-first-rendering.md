---
status: proposed
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

## Implementation Plan

1. Branch from main
2. Refactor `render.py` — notation lookup first, then dispatch on kind
3. Refactor `latex_build.py` — same pattern
4. Extend `NotationRule` with fields for special behaviour (e.g. `sup_style`
   for Exp, `smart_spacing` for Gp)
5. Run full test suite after each step
6. Merge when green
