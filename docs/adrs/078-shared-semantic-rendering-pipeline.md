---
status: accepted
date: 2026-07-19
deciders: edouard
---

# ADR-078: Shared Semantic Rendering Pipeline

## Context and problem statement

Galaga's legacy renderer has separate structural paths for text and LaTeX,
mutable notation keyed by operation-specific expression class names, and
rendering decisions mixed into the legacy multivector. Galaga 2 now has an
eager core-backed facade, immutable presentation configuration, and generic
expression provenance keyed by stable catalog IDs. It needs human-readable
values and derivations without recreating the earlier coupling.

ASCII, Unicode, and LaTeX must preserve the same mathematical grouping. A
notation preset must be able to change spelling for teaching without changing
which inner product or product is computed. Scoped presentation must remain
thread- and async-safe, and rendering must never become a hidden numeric
evaluation path.

## Decision drivers

- Decide precedence and associativity once for every output target.
- Keep notation keyed by stable mathematical operation identity.
- Make long functional operation names a complete canonical fallback.
- Keep competing inner products visually distinguishable in every preset.
- Preserve signed blade conventions and display order for concrete and literal
  values.
- Keep output escaping and target glyph rewrites out of expression nodes.
- Route Python string, format, and rich-display hooks through one public path.
- Preserve explicit, scoped, and persistent presentation precedence.
- Avoid importing the legacy numeric or rendering implementation.

## Decision outcome

Galaga 2 introduces `galaga.rendering.tree`, an immutable format-neutral layout
model containing identifiers, literals, text, sums, products, fractions,
powers, calls, prefix/postfix/infix operations, scripts, accents, wrappers,
groups, delimited sequences, and teaching equalities.

One precedence and associativity model inserts explicit `Group` nodes during
tree construction. Equal-precedence elision and associative visual flattening
require the same stable operation ID; unrelated products are not assumed to be
interchangeable merely because their binding strength matches.

The expression/value builder inspects eager coefficients, presentation data,
and generic expression nodes. It validates `Call.operation_id` through the
facade catalog but never invokes an evaluator. Native coefficients are adjusted
by `BladeLabel.ref.orientation` and traversed in `DisplayOrder`.

Immutable `RenderRule` and `Notation` values remain presentation components.
Rules are keyed by operation ID with optional target-specific overrides. They
record layout kind, semantic symbol, precedence, associativity, parameter
decoration, argument order, delimiters, and visual flattening. A missing rule
renders as the long operation name. Optional short functional notation changes
only rendered spelling. Doran-Lasenby, Hestenes, and Lengyel/RGA presets keep
the distinct inner-product operation IDs distinguishable.

ASCII, Unicode, and LaTeX emitters consume the same node model. Emitters own
escaping, scripts, combining accents, fractions, delimiter syntax, and
scientific-number rewrites. They import neither the legacy algebra nor legacy
renderers.

`galaga.display` independently resolves content (`name`, `expr`, `value`,
`full`, or automatic policy) and target (`ascii`, `unicode`, or `latex`).
Explicit render arguments override the algebra's context-local presentation,
which overrides its persistent presentation. Facade `display`, `ascii`,
`unicode`, `latex`, `str`, `repr`, `format`, and `_repr_latex_` all delegate to
this pipeline.

During migration, immutable v2 notation remains exported from
`galaga.presentation` and `galaga.facade`; the legacy `galaga.notation` module
is not replaced until its Phase 7 compatibility cutover.

## Consequences

- Good, because every target shares one structural vocabulary and grouping
  decision.
- Good, because render trees can be tested structurally before brittle final
  strings.
- Good, because all catalog operations render through a long-name fallback
  without a parallel renderer registry.
- Good, because target-specific fallbacks can be honest when a notation has no
  appropriate ASCII glyph.
- Good, because notation and target changes cannot alter eager values or
  expression identity.
- Good, because signed RGA blades render consistently from concrete values and
  expression literals.
- Good, because context-local teaching presentations remain safe across threads
  and async tasks.
- Cost, because the layout model has more node types than a direct string
  renderer.
- Cost, because malformed third-party rules need validation and functional
  fallback behavior.
- Limitation, because this tree is display structure, not a simplifier,
  evaluator, or serialization format.
- Deferred, because legacy renderer adapters and companion-package consumers
  remain Phase 7 work.

## Superseded legacy behavior

For Galaga 2, this decision supersedes ADR-023, ADR-025, ADR-027, ADR-029,
ADR-033, ADR-034, ADR-043, ADR-048, ADR-050, ADR-061, and ADR-068 where those
records depend on mutable global/algebra display state, operation-specific
expression classes, or separate legacy text and LaTeX structures. Their useful
notation and output examples remain compatibility inputs rather than the new
architecture.
