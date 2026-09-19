---
status: accepted
date: 2026-09-18
deciders: edouard
---

# ADR-151: Content-Part Annotation Targets

## Context

SPEC-015 section 6 asks for annotations that explain both sides of a teaching
display:

```python
annotate(result, target="expression", label="computed as")
annotate(result, target="value", label="evaluated bivector")
```

`content_document` already builds the display as `name = expr = value` and
exposes a `ContentAnchor` for each displayed part, plus `relation` anchors for
the equals signs. But `galaga_annotation` had no target that selected those
parts, so a rule could only reach the whole display.

## Decision

Add `ContentTarget(kind)` for `kind` in `{"name", "expr", "value"}`, plus the
`ga.content(kind)` selector factory. Resolution reads
`document.select_content(kind)` and uses each anchor's `render_path`; a part
that the active content setting does not display matches nothing and follows
the ordinary `missing` policy. Lowering wraps the whole part body through the
existing direct-placement and style machinery, so labels, colours, fills, and
markers behave exactly like every other target.

The factory is `ga.content(kind)` rather than `ga.name()` / `ga.expression()`
/ `ga.value()` convenience functions. The maintained-notebook gallery runs a
v1→v2 migration codemod that rewrites any `.name(...)` attribute call to
`.named(...)` (the old `Multivector.name` API). A `ga.name()` selector would be
silently rewritten and break the formatter's idempotency gate. One factory
using the same `name`/`expr`/`value` vocabulary as the `content=` presentation
setting keeps a single spelling that the codemod cannot confuse.

`relation` is deliberately not selectable yet. Its `ContentAnchor` points at
the whole `Equality` node rather than the `=` glyph, so decorating it would
wrap the entire display. Isolating the relation glyph needs a core equality
slot analogous to `SumTerm.sign`, and remains future work.

## Consequences

- A lesson can explain the variable name, the recorded expression, and the
  evaluated result independently, and can attach labels that read as a
  relation between the parts.
- Content targets respect `content="name" | "expr" | "value" | "full"`; no
  second content policy is introduced.
- The selector vocabulary gains a `content(kind)` entry rather than three
  narrowly named factories, keeping the codemod-safe spelling.
- Relation annotations and content targets nested inside an expression scope
  remain future work.

## Validation

- `galaga_annotation` tests cover factory validation, part resolution for a
  full display, the value-only empty selection, part wrapping, and content
  labels.
- `examples/annotation/content_parts.py` is executed by the annotation
  notebook test and the maintained example gallery.

## Related

- [SPEC-015](../specs/SPEC-015-expression-and-matrix-annotations.md): the
  annotation capability specification, sections 6 and 13.
- [ADR-143](143-concrete-render-documents-and-semantic-anchors.md),
  [ADR-145](145-teaching-render-documents-and-presenter-capture.md): content
  anchors and teaching documents.
- [ADR-147](147-katex-annotation-lowering-and-decoration-wrappers.md): KaTeX
  lowering.
