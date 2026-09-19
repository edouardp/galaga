---
status: accepted
date: 2026-09-18
deciders: edouard
---

# ADR-153: Configurable CGA Cocarrier Markers and Over Markers

## Context

The CGA incidence highlight (ADR-148) draws cocarrier callouts with a fixed
`overgroup` marker. Lessons that prefer a different visual vocabulary — an
overbrace, an overline, or an overbracket — had to rebuild the whole recipe by
hand. The marker vocabulary also lacked `overline` and `overbracket`, so those
choices were not expressible at all.

All four commands are supported by the bundled KaTeX (0.16.x); they differ in
how a label attaches. `\overbrace` and `\overbracket` take limits, while
`\overgroup` and `\overline` do not.

## Decision

Add `overline` and `overbracket` to the renderer-neutral marker vocabulary in
`AnnotationStyle`. Both are above-only, like `overbrace` and `overgroup`.

Lowering follows the command's own grammar:

- `overbracket` behaves like `overbrace`: `\overbracket{body}^{label}`.
- `overline` is an accent without limits, so a label attaches with
  `\overset{label}{\overline{body}}` and a bare marker emits `\overline{body}`.
- `underbrace` and the generic `brace` are unchanged.

`highlight_cga` gains `over_marker` (default `"overgroup"`) restricted to
`overgroup`, `overbrace`, `overline`, or `overbracket`. It replaces the marker
on the round-weight and flat-weight cocarrier rules, the only over-marked
callouts in the incidence recipe. An unsupported value raises `ValueError`.
The parameter has no effect on `decomposition="components"`, which labels
families below with fills and has no over markers.

`highlight_object` is added as an alias of `highlight_cga`, because the
object-level recipe and the CGA factory are the same operation and lessons
already name the bound recipe `highlight_object`. It has the same signature
and validation.

## Consequences

- A lesson can choose the cocarrier callout style without rebuilding the CGA
  recipe: `ga.highlight_cga(model, over_marker="overbracket")`.
- The new markers are general, not CGA-specific, and are available on any
  annotation rule.
- `over_marker` is a marker selector, not a full style override; colors and
  clearance stay recipe-owned. A full style override can be added later if a
  lesson needs it.
- `highlight_object` is an alias rather than a second implementation, so the
  two names can never drift.

## Validation

- `galaga_annotation` tests cover marker validation for the above-only
  directional rules, overline and overbracket lowering with and without labels,
  every `over_marker` choice on a dipole, the invalid-value error, and the
  `highlight_object` alias matching `highlight_cga`.

## Related

- [ADR-142](142-reusable-callable-annotators.md): reusable callable annotators.
- [ADR-147](147-katex-annotation-lowering-and-decoration-wrappers.md): KaTeX
  lowering and marker vocabulary.
- [ADR-148](148-cga-object-classification-and-highlight-recipes.md): CGA object
  classification and highlight recipes.
