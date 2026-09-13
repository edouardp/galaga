---
status: accepted
date: 2026-09-13
deciders: edouard
---

# ADR-138: Scoped Notation Shortcut

## Context

Comparing operation symbols in teaching notebooks currently requires composing
a full presentation even when only notation changes. The existing
`presets.notation` namespace already supplies dimension-independent recipes,
including Lengyel's bullet for metric inner product.

## Decision

Add `Algebra.use_notation(notation: Notation)` as a context manager equivalent
to `use_presentation(self.presentation.with_notation(notation))`. Resolve the
current presentation on entry, not when the context manager is constructed.
Yield the same algebra, matching `use_presentation`.

Delegate validation, restoration and context isolation to the existing
presentation machinery. Preserve all other effective components, including
those supplied by enclosing scopes. Accept custom immutable `Notation` objects
and existing notation presets; introduce no strings, new preset namespace or
global state.

Rendering still selects the presentation at render time. Results do not
capture a temporary presentation. In Marimo, teach explicit output inside the
scope with `mo.output.replace(mo.as_html(value))`, or retain the rendered HTML
for later display. A bare expression inside a `with` block is not automatic
notebook output.

## Consequences

- Notation comparisons require less boilerplate without changing the
  presentation architecture described in ADR-076.
- Numeric results, expression tracking, equality and hashing remain unchanged.
- Explicit per-render presentations still override a notation scope.
- Thread and async-task isolation, nesting and exceptional cleanup use the
  existing context-local implementation.
- `with_notation` remains the persistent-view API; `use_notation` is temporary.

## Validation

Tests verify metric-derived numeric results alongside the bullet rendering,
custom LaTeX rules, render-time selection, explicit rendering precedence,
component preservation, delayed context entry, mixed nested scopes, exception
cleanup, invalid inputs, thread and async-task isolation, and captured Marimo
HTML after scope exit.
