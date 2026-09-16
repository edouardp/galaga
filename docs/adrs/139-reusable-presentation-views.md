---
status: accepted
date: 2026-09-16
deciders: edouard
---

# ADR-139: Reusable Presentation Views

## Context

`Algebra.use_presentation(...)` and `use_notation(...)` make it convenient to
render a block under a temporary presentation. They correctly restore their
context-local state at scope exit, but a Marimo assignment within that scope
followed by a later cell display renders with the restored presentation.

Attaching a temporary presentation automatically to every multivector created
inside a scope would make arithmetic presentation-dependent. It would leave
ambiguous inheritance for operations combining values created under different
scopes, and assignment of an existing value would not create anything to
capture.

## Decision

Add public immutable `Presenter` recipes and `PresentedMultivector` views.

`Presenter(...)` accepts independent presentation components: `presentation`,
`blades`, `notation`, `local_names`, `display_order`, `display`, and convenience
`content`. Calling a presenter on a multivector resolves omitted settings from
that value's effective presentation, resolves blade/order recipes against its
actual algebra, then returns a view capturing the result. Calling a presenter
on a view starts from the view's captured presentation.

Views implement the ordinary rendering protocol (`display`, `ascii`, `unicode`,
`latex`, rich LaTeX and format hooks) but intentionally no arithmetic. Their
`value` property exposes the original multivector for computation. Explicit
per-render presentation or notation selections retain their normal precedence.

Expose concise choices under `presets.presenters`: default capture, value/full
content, functional and Lengyel notation, and grade/bitmap display order. The
namespace contains only one-line factories; it does not duplicate
algebra-specific blade vocabularies already supplied by `presets.blades`.

## Consequences

- A teaching notebook can prepare a presenter once, apply it in any cell, and
  display the captured view later without a context manager or pre-rendered
  HTML.
- One numerical value can appear in deliberately different notations side by
  side, without implicit formatting inheritance through arithmetic.
- Metric-sensitive blade recipes validate against the target value. They
  preserve computed orientation signs and reject incompatible frames rather
  than reinterpret a metric or basis.
- `use_*` remains useful for rendering groups of already existing values in one
  temporary context; presenters provide the stable assigned-output workflow.
- Tables and matrix representation objects keep their own snapshot/display
  APIs for now. The view protocol is deliberately scoped to facade
  multivectors.

## Validation

Unit tests cover immutability, public identity, render protocol, rich display
and Galaga-Marimo interpolation, all presentation components and their
precedence, scope capture, compatible/incompatible metric recipes, order
resolution across dimensions, signed STA labels, oblique products, and
thread-independent values. The teaching notebook is gallery-listed and executes
under all notation/content/signature controls while recomputing each displayed
identity from the algebra.
