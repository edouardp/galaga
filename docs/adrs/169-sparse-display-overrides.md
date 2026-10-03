---
status: accepted
date: 2026-10-03
deciders: edouard
---

# ADR-169: Sparse Display Overrides

## Context

ADR-076 made `DisplayPolicy` an immutable display component. ADR-161 composed
presentation components by replacing a repeated slot. This made
`DisplayPolicy(coefficient_precision=4)` reset unrelated choices such as
content and target when applied after another policy or to an algebra view.
Notation already has a sparse override form, and presenter factories can be
composed with presentation components.

## Decision

Keep `DisplayPolicy` as the public display component, with concrete readable
defaults and internal tracking of which constructor fields were supplied.
When applied to an existing presentation, only supplied fields override it.
Composition of two display policies merges their supplied fields with the
right-hand value winning on overlap. Explicit default values, including
`content="auto"`, reset that field intentionally. A bare `DisplayPolicy()` is
an empty override.

`PresentationConfig` always stores a complete, resolved policy. Its
`with_display()` method, algebra display overrides, recipes, and presenters
apply sparse policies to the current complete policy. Direct construction or
dataclass replacement of a `PresentationConfig` from a partial policy resolves
unspecified fields against the library defaults; use `with_display()` when
inheritance from an existing config is intended.

Expose `presets.display.override(...)` as the regular factory for composable
display changes, parallel to `presets.notation.override(...)`. Keep direct
`DisplayPolicy(...)` construction for explicit component arguments and
advanced configuration. Policy equality includes which fields were supplied,
because two policies with the same readable defaults can behave differently
when composed. Complete policies in `PresentationConfig` have all fields
supplied, so snapshots compare by their effective values.

## Consequences

Users can write
`presets.presenters.values() | presets.display.override(coefficient_precision=4)`
without losing value-only content. Renderers continue to receive concrete
content, target, zero tolerance, and precision values. ADR-076's independent
component replacement and ADR-161's repeated-slot replacement now have a
field-wise exception for display overrides.
