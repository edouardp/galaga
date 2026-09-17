---
status: accepted
date: 2026-09-18
deciders: edouard
---

# ADR-147: KaTeX Annotation Lowering and Decoration Wrappers

## Context

ADR-142 specifies an optional `galaga_annotation` package with immutable rules
and callable annotators, and ADR-143–146 provide the semantic anchors it
selects. Implementing the first renderer raised four design questions the
package could not answer alone:

1. How does an optional renderer wrap a subtree inside the shared emitter
   without duplicating its precedence, spacing and escaping logic?
2. How can an annotated view compose with the existing `Presenter` without
   making core Galaga import the optional package?
3. Which annotation targets are in the first milestone, and which stay later?
4. How are labels placed when nearby annotations would collide?

The package must not become a second rendering engine, and core imports must
remain annotation-free.

## Decision

Add one renderer-owned node, `galaga.rendering.Decorated`, with fields
`body`, `opening` and `closing`. The LaTeX emitter wraps the emitted body with
the two opaque strings; ASCII and Unicode emit the body unchanged because
decoration spelling is renderer-specific. Its precedence remains that of its
body, so removing the wrapper for plain-text targets cannot erase required
parentheses. Core builders never create it. Export `Decorated` and the existing
`emit` function from `galaga.rendering` so optional presentation packages can
lower transformed trees through the shared emitter instead of re-implementing
it.

Extend `Presenter.__call__` with a duck-typed adapter hook: when the input is
not a `Multivector` or `PresentedMultivector` but exposes a callable
`__galaga_present__`, the presenter delegates to it. `galaga_annotation`
implements the hook on its rendering-only view so `lengyel(annotated)` keeps
both the captured presentation and the rules. Core gains no import of the
extension and unsupported inputs still raise `TypeError`.

The first `galaga_annotation` milestone implements whole-value/expression
targets, expression paths, operator occurrences including the implicit
geometric-product extent, variable occurrences, grades, terms and
coefficients, plus text colour, fills, borders, labels, arrows, rules,
braces, underlines and boxes. Expression spans, sign-only targets,
semantic-role targets, matrix regions and arithmetic propagation remain
later milestones; the specialization follows SPEC-015.

Adjacent terms carrying the same rule join into one continuous span only when
the rule sets `join=True`; otherwise every placement renders separately. A
joined span keeps its internal separators and leading sign inside the
highlight and shows one label for the run. Independent rules form independent
layers, so a wide fill may contain narrower brackets. Crossing (partially
overlapping) spans in one sum are rejected as ambiguous.

Fill and overlay lowering re-enter math mode with `$...$` inside
`\colorbox` and `\fcolorbox`, the spelling KaTeX expects there. A border with
no requested fill uses a transparent background rather than assuming a light
theme. Annotated views keep inline `$...$` in `_repr_latex_` and add a Marimo
rich-display `_repr_html_` that hands the math to the frontend as one inline
block: routing `_repr_latex_` through Marimo's Markdown parser would split the
equation at those inner dollar delimiters. The final TeX payload is HTML-escaped
at this custom-element boundary so even trusted raw TeX cannot terminate or
inject sibling markup.

Marker rules colour their chrome rather than their content: the bracket glyph
and label take the rule's colour, while the highlighted terms keep their own
colour. Plain labels render upright with `\text{...}` so word spacing is
preserved, and newlines stack lines; `label_latex` is an explicit trusted
mode for equation labels. This raw mode is a deliberate KaTeX trust boundary;
ordinary `label` values remain escaped text. `label_color` colours only a label,
so a span label can match its fill in a darker shade. `overlay=True` smashes the marker
(`\smash[t]` above, `\smash[b]` below) so it protrudes over an enclosing
fill instead of inflating or splitting it. Overlay `clearance` becomes an
outward lift implemented by a raised zero-width strut inside `\vphantom`, so
the marker rises while the visible terms stay on the baseline without
serializing the subtree during transformation.

Label placement is approximate and greedy: labels stay centred on their
anchors; adjacent same-side labels whose estimated widths overlap alternate to
the free side; residual collisions are recorded in the exposed layout rather
than resolved with renderer-specific offsets. `side="auto"` lets the solver
choose; explicit and directional sides are respected.

Ordinary lowering is trusted-free: plain labels use the shared text escaper,
colours and non-negative dimensions are validated, and boxes re-enter math
mode explicitly. `label_latex` is the one named advanced escape hatch and is
therefore trusted as KaTeX source; it is still HTML-escaped before entering the
Marimo custom element. `undergroup` and `overgroup` lower to KaTeX's
`\undergroup` and `\overgroup` group accents, which are visually distinct
from the `underbrace` and `overbrace` markers. Generic `brace` follows the
solved side, while a labelled underline remains an underline with an attached
underset. KaTeX group accents do not take limits, so their labels attach with
`\underset` and `\overset`; a bare group marker with no label emits the accent
alone. The bundled KaTeX used by Marimo (0.16.47) supports both group accents.

`galaga-annotation` is jointly versioned and released with core Galaga because
it consumes the public render-tree extension point introduced in the same
release. Its declared core floor must name the first release that contains all
imported rendering APIs; the repository build, artifact check and publish
stages include the distribution.

## Consequences

- The shared emitter stays the single source of LaTeX spelling and spacing.
- Core carries a small, documented rendering extension point rather than an
  annotation dependency; tests cover the wrapper and the adapter hook
  independently of the extension.
- Annotated views remain rendering-only. Arithmetic propagation is deferred.
- Approximate placement may leave residual collisions; the solved layout is
  exposed for tests and debugging instead of silently shifting content.
- The extension can grow new lowerings without changing core as long as it
  emits `Decorated` wrappers.

## Validation

- Core tests cover `Decorated` emission for all three targets and the
  presenter adapter hook.
- Extension tests cover target resolution, empty selections, algebra
  compatibility, escaping, marker lowering, label layout and numerical
  transparency.
- Repository linting enforces Ruff C901 on the annotation implementation so
  selection, lowering, and span-layout responsibilities cannot silently grow
  back into high-complexity functions.
- The companion README example is executed by the release-workflow tests.

## Related

- [ADR-142](142-reusable-callable-annotators.md): reusable callable annotators.
- [ADR-143](143-concrete-render-documents-and-semantic-anchors.md),
  [ADR-144](144-expression-render-occurrence-anchors.md),
  [ADR-145](145-teaching-render-documents-and-presenter-capture.md),
  [ADR-146](146-expression-component-anchor-scopes.md): semantic anchors.
- [SPEC-015](../specs/SPEC-015-expression-and-matrix-annotations.md): the
  annotation capability specification.
