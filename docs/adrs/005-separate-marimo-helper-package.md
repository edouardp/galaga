---
status: accepted
date: 2026-03-25
deciders: edouard
---

# ADR-005: Separate Marimo Notebook Helper Package

## Context and Problem Statement

The library needs rich LaTeX rendering in marimo notebooks. Should this be
part of the core library or a separate package?

## Decision Drivers

* The core library should have minimal dependencies (only NumPy)
* Marimo integration requires marimo as a dependency
* Python 3.14 t-strings enable a clean rendering API
* The helper should work with any object that has `.latex()`, not just GA objects

## Considered Options

1. Build rendering into the core `ga` package
2. Separate `galaga-marimo` (`gamo`) package
3. No special notebook support

## Decision Outcome

Chosen option: "Separate `galaga-marimo` package" because it keeps the core
dependency-free and the rendering protocol generic.

The helper uses t-strings (`gm.md(t"...")`) and auto-detects objects with
`.latex()` or `_repr_latex_()` for inline LaTeX rendering.

### Consequences

* Good, because the core library stays dependency-free (only NumPy)
* Good, because the renderer works with any LaTeX-capable object (SymPy, etc.)
* Good, because t-strings make the API natural: `gm.md(t"Vector: {v}")`
* Bad, because users need to install a second package for notebooks

## Subsequent evolution

This decision remains specific to t-string Markdown rendering. ADR-091 records
the later decision to place interactive browser visualizations in the separate
`galaga-anywidget` distribution, avoiding a dependency from the generic
renderer onto widget assets and interaction state.
