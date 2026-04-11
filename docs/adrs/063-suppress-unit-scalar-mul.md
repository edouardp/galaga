---
status: accepted
date: 2026-04-11
deciders: edouard
---

# ADR-063: Suppress Unit Coefficient in Symbolic ScalarMul Rendering

## Context and Problem Statement

ADR-045 handles ±1 coefficient suppression for *evaluated* multivectors
(the `__format__` path). However, the *symbolic expression tree* renderers
(`render.py` for unicode, `latex_build.py` for LaTeX) had an asymmetry:
`ScalarMul(k=-1, x)` correctly rendered as `-x`, but `ScalarMul(k=1, x)`
rendered as `1x` (unicode) or `1 x` (LaTeX).

This appeared in practice when a computed sign (`+1` or `-1`) was multiplied
into a lazy expression. The `-1` case looked correct (`-‖log(R)‖`) but the
`+1` case showed a spurious leading `1` (`1 ‖log(R)‖`).

## Decision Outcome

Add a `k == 1` early return in both renderers, matching the existing `k == -1`
pattern:

- `render.py`: return the inner rendering directly
- `latex_build.py`: return the inner LNode directly

### Consequences

- Good, because `+1` and `-1` are now symmetric — both suppress the unit
  coefficient
- Good, because no change to evaluation semantics — only rendering
- Consistent with ADR-045's principle that ±1 coefficients should not be
  shown unless explicitly requested via format specs
