---
status: accepted
date: 2026-09-18
deciders: edouard
---

# ADR-150: Sign-Only Annotation Targets

## Context

SPEC-015 provides `document.select("sign", mask=...)` anchors and lists
`sign(blade)` as a selector, but the first `galaga_annotation` milestone
deferred sign-only targets. Implementing them exposed a gap: the render tree
represents a sum sign only as `SumTerm.negative`, and the shared emitter turns
that flag into the `-`/`+` separator. There was no layout slot a decoration
could wrap, so a sign rule would otherwise have to recolour the whole term.

The anchor documents the intended behaviour clearly: a sign is a distinct
visible component, separate from the coefficient magnitude and the blade.

## Decision

Give `SumTerm` an optional `sign: Node | None` field. When present it replaces
the emitted sign glyph while `negative` remains the semantic sign. `_emit`
renders the override in the slot's normal position (prefix for the first term,
surrounded by spaces between terms). Plain-text targets emit the decorated
node unchanged because `Decorated` is transparent there, so a decorated sign
still reads back as `-`/`+`.

Add `SignTarget` plus the `sign(blade)` and `signs(*blades)` selectors to
`galaga_annotation.targets`. Resolution selects the displayed sign anchors and
addresses each one as `(*render_path, "terms", term_index, "sign")`. A sign is
only selectable when it is visible: omitted unit coefficients, implicit
leading plus signs, and terms hidden by display tolerance have no anchor, so
those rules match nothing under the ordinary `missing` policy.

Concrete value documents preserve a semantic one-term `Sum`, including its
sign slot, even though ordinary value rendering still collapses to the familiar
singleton text. A singleton negative term can therefore expose and decorate
only its sign. This avoids a representation-dependent fallback in which the
same selector unexpectedly decorated the entire term.

The KaTeX lowerer partitions sign placements out of the term/span pipeline
before layout. It applies them to the owning `SumTerm` (resolving a label or
marker side with the ordinary `_default_side` policy), then runs the existing
span machinery. `_SumLayout` carries the `sign` field through its segment
splits with the same ownership rule it already uses for `negative`, so a sign
stays attached to whichever construct emits it. Sign highlighting therefore
composes with grade fills and joined term spans: the sign is recoloured inside
the fill and the fill keeps its own separators.

One composition is deliberately fused rather than nested: when a sign-only
rule requests the same background as a joined term span beginning at that
sign, the lowerer consumes the redundant sign box and emits the sign inside
the span's single continuous box. This lets a recipe select the sign and term
independently without producing a visible seam. Sign rules with a different
fill, foreground, border, marker, or label remain independent decorations.

Sign decorations reuse the ordinary rule styles and markers (`_wrap`), so
colour, fill, border, emphasis, labels, arrows, and braces all work. The sign
glyph is not a second rendering dialect; it is one more semantic slot that
lowers through the shared wrappers and emitter.

## Consequences

- Core gains a small, optional presentation field on `SumTerm`; the semantic
  sign stays `negative`, and builders never set the override.
- The three value-component selectors now read as a set:
  `sign(blade)`, `coefficient(blade)`, and `term(blade)` address the sign, the
  magnitude, and the whole term.
- Sign rules isolate the glyph consistently for singleton and multi-term
  values; preserving the semantic singleton `Sum` does not change ordinary
  emitted output.
- Sign placements do not participate in the approximate label-collision
  solver. Labels still render on the sign; residual collisions are not
  staggered for signs alone.

## Validation

- Core emitter tests cover the `SumTerm.sign` override on the LaTeX target and
  its transparency on plain text.
- `galaga_annotation` tests cover selector validation and algebra
  compatibility, sum-slot resolution, implicit leading plus and singleton
  policy, glyph-only lowering for fill and colour, sign labels, survival
  through a joined term span, and numerical transparency.
- `examples/annotation/sign_highlights.py` is executed by the annotation
  notebook test and the maintained example gallery.

## Related

- [SPEC-015](../specs/SPEC-015-expression-and-matrix-annotations.md): the
  annotation capability specification.
- [ADR-142](142-reusable-callable-annotators.md): reusable callable annotators.
- [ADR-143](143-concrete-render-documents-and-semantic-anchors.md): sign
  anchors in the concrete value document.
- [ADR-147](147-katex-annotation-lowering-and-decoration-wrappers.md): KaTeX
  lowering and the `Decorated` extension point.
