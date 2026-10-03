---
status: accepted
date: 2026-10-04
deciders: edouard
---

# ADR-172: Leaf Composition Dispatch

## Context

ADR-161 defines immutable, right-biased `|` composition for presentation
components. The first implementation put both the `PresentationComposable`
operator mixin and the full composition policy in `composition.py`. Blades,
notation, display policies, and presets imported the mixin, while the policy
needed those component types for validation and dispatch. This forced many
imports inside methods and obscured the module dependency direction.

## Decision

Move the small `PresentationComposable` operator hook into
`_composition_base.py`. Component modules import only that leaf module. The
hook imports `compose` when `|` is invoked, after package initialization.
`composition.py` owns recipes and composition policy and imports the blade
and presentation component types normally. Preset factory imports remain at
the point of use because the preset package exposes notation factories that
also import composition. Type-only imports remain under `TYPE_CHECKING`.

Keep the operator semantics and public component types from ADR-161. The
facade, presenter, and YAML configuration continue to use the same recipes
and `compose` function.

## Consequences

The module initialization dependency runs from components to the leaf hook,
then from the composition policy to components. Runtime dispatch has one
explicit import back to the policy. The remaining deferred preset imports
mark the preset package boundary; they do not stand in for the general
component dependency graph. This changes implementation ownership, not the
meaning of `|`.

## Follow-up: normalization and merge responsibilities

Keep `compose()` as dispatch between component kinds. Dedicated helpers merge
notations, notation patches, and presentation recipes. Presentation models
normalize token and rule inputs and validate render-rule options in small
private functions before storing immutable values. These helpers preserve the
same public constructors, validation errors, and right-biased precedence;
they make each rule easier to inspect and change independently.
