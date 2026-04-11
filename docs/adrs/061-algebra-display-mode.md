---
status: accepted
date: 2026-04-11
deciders: edouard
---

# ADR-061: Algebra-Level Display Mode for Multivector Repr

## Context and Problem Statement

In notebook environments (Jupyter, Marimo), multivectors render via
`_repr_latex_`, `__repr__`, and `__str__`. By default these show only the
raw value (or just the name for named multivectors). To see the full
`name = expression = value` form, users must call `.display()` explicitly
on every multivector — tedious when exploring interactively.

## Decision Drivers

* Notebook users want rich display by default without calling `.display()`
  on every cell output
* The default behaviour must not change for existing users
* The setting belongs on the algebra, not on individual multivectors,
  because it is a session-wide preference

## Decision

Add a `display_repr: bool = False` keyword argument to `Algebra.__init__`.
When `True`, `Multivector.__repr__`, `__str__`, and `_repr_latex_` delegate
to `self.display()` instead of their default rendering.

Originally named `display=`, renamed to `display_repr=` for clarity — the
name says exactly what it changes (the repr behaviour) rather than the
vague `display`.

## Consequences

* `Algebra(3, display_repr=True)` makes every multivector auto-render in the
  `name = expression = value` form in notebooks and REPLs
* Unnamed multivectors are unaffected in practice — `display()` deduplicates
  parts, so a single-part result has no `=` sign
* Default behaviour (`display_repr=False`) is unchanged; no existing code breaks
* The flag is stored as `Algebra._display_mode` and checked in three methods
