---
status: accepted
date: 2026-09-20
deciders: edouard
---

# ADR-155: Internal Decoration Boundary and Lockstep Dependency Floors

## Context

The matrix renderer originally imported `_default_side`, `_style_body`, and
`_wrap` from the expression-oriented `katex` renderer. Although both modules
are internal implementation, cross-module imports of underscore helpers make
ownership unclear and allow one renderer's private refactoring to break the
other. The shared behavior is target-independent decoration lowering, not an
expression-renderer implementation detail.

Matrix annotations also consume `MatrixRepr.logical_shape` and `cell_latex`,
which first ship with the same joint release as the adapter. A static future
dependency floor makes the current editable package set unresolvable, while a
floor left at the previous release would produce incorrect published metadata
after the next release bump.

## Decision

Extract target-independent KaTeX decoration lowering into the deliberately
package-private `galaga_annotation._decoration` module. It exposes a small
named internal interface—`decorate`, `style_body`, `default_side`, and
`external_parts`—to the expression and matrix renderers. Its lower-level
marker construction remains private to that module. None of these names are
re-exported from `galaga_annotation`.

Add an architecture test that rejects imports of underscore-prefixed names
from sibling modules. Private implementation modules may therefore be shared,
but their cross-module interface must be explicit.

Keep dependency floors equal to the current jointly released package version
during development. The release script already advances every companion's
`galaga` floor when it changes their versions; extend that atomic step to also
advance `galaga_annotation`'s optional `galaga-matrix` floor. Release topology
tests require both floors to be at least their corresponding package version.

## Consequences

- Expression and matrix rendering still share exactly one decoration
  implementation without one renderer reaching into another's private scope.
- Internal helpers can be reorganized behind `_decoration` without expanding
  the public API or compatibility surface.
- Editable installs remain resolvable between releases.
- A release cannot publish the annotation matrix extra against an older matrix
  package that lacks its required hooks.

## Validation

- The complete annotation suite exercises expression, matrix, direct overlay,
  span overlay, notebook, and standalone KaTeX lowering through the extracted
  module.
- Architecture tests reject sibling private-name imports and public leakage of
  the internal interface.
- Release topology tests validate the core and matrix dependency floors, and
  inspect the release script for the atomic matrix-floor update.

## Related

- [ADR-147](147-katex-annotation-lowering-and-decoration-wrappers.md): original
  decoration lowering.
- [ADR-149](149-matrix-cell-and-region-annotations.md): matrix adapter and its
  optional dependency.
- [ADR-154](154-independent-external-span-overlays.md): external span overlay
  lowering now hosted by the shared internal module.
