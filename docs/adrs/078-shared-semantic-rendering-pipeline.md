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
- Keep competing inner-product operation identities distinct, and use explicit
  teaching presets when a shared historical glyph would be ambiguous.
- Preserve signed blade conventions and display order for concrete and literal
  values.
- Keep output escaping and target glyph rewrites out of expression nodes.
- Route Python string, format, and rich-display hooks through one public path.
- Preserve explicit, scoped, and persistent presentation precedence.
- Avoid importing the legacy numeric or rendering implementation.

## Decision outcome

Galaga 2 introduces `galaga.rendering.tree`, an immutable format-neutral layout
model containing identifiers, literals, text, sums, products, fractions,
powers, calls, prefix/postfix/infix operations, scripts, accents, undersets,
math-class annotations, wrappers, groups, delimited sequences, and teaching
equalities. Calls and delimiters record whether their target should use
scalable or compact delimiters; this is semantic layout policy rather than an
emitter-specific string patch.

One precedence and associativity model inserts explicit `Group` nodes during
tree construction. Equal-precedence elision and associative visual flattening
require the same stable operation ID; unrelated products are not assumed to be
interchangeable merely because their binding strength matches.

The expression/value builder inspects eager coefficients, presentation data,
and generic expression nodes. It validates `Call.operation_id` through the
facade catalog but never invokes an evaluator. Native coefficients are adjusted
by `BladeLabel.ref.orientation` and traversed in `DisplayOrder`. Immutable
display policy supplies an absolute near-zero cutoff and significant-digit
precision to the semantic literal nodes. The defaults, `1e-12` and six, retain
legacy display behavior without changing the numeric values held by the core.

Before translating expression provenance, the builder applies the public
conservative structural simplifier to a temporary rendering view. This removes
identities such as `1 x`, `0 x`, `-1 x = -x`, and addition of literal zero
without mutating the retained expression, reordering operands, applying a
metric identity, or performing numeric evaluation. The renderer remains
outside the ownership of general geometric-algebra simplification.

Conventional addition is translated to semantic `Sum` and `SumTerm` nodes.
The builder absorbs a leading negative sign from an added term into the term's
sign, so `a + (-k)b` renders as `a - k b`; nested additions remain one flat
sum. This matches the Galaga 1 rendering oracle while leaving both the stored
binary `add` provenance and eager coefficients unchanged. A customized
addition rule remains an ordinary `Infix` node and retains its configured
symbol and precedence.

Immutable `RenderRule` and `Notation` values remain presentation components.
Rules are keyed by operation ID with optional target-specific overrides. They
record layout kind, semantic symbol, precedence, associativity, parameter
decoration and placement, argument order, delimiters, operand grouping,
delimiter scaling, and visual flattening. Definition-shaped rules cover the
reverse sandwich and metric regressive product without changing the stored
operation ID. A missing rule renders as the long operation name. Optional
short functional notation changes only rendered spelling. Doran-Lasenby,
Hestenes, and Lengyel/RGA presets keep competing inner products visually
distinct. The default LaTeX presentation deliberately retains Galaga 1's
shared dot glyph for the Doran-Lasenby and Hestenes products; their expression
IDs and functional names remain distinct.

Expression provenance stores optional numeric parameters only when they differ
from the operation's public default. This keeps tolerances out of ordinary
mathematical display while preserving non-default parameters for exact
reevaluation. Reflected commutative operators preserve the user's written
operand order even when the eager numeric result would be unchanged.

ASCII, Unicode, and LaTeX emitters consume the same node model. Emitters own
escaping, scripts, combining accents, fractions, delimiter syntax, and
scientific-number rewrites. They import neither the legacy algebra nor legacy
renderers.

`galaga.display` independently resolves content (`name`, `expr`, `value`,
`full`, or automatic policy) and target (`ascii`, `unicode`, or `latex`).
Explicit render arguments override the algebra's context-local presentation,
which overrides its persistent presentation. Facade `display`, `ascii`,
`unicode`, `latex`, `str`, `repr`, `format`, and `_repr_latex_` all delegate to
this pipeline. Full and automatic teaching equalities deduplicate parts after
target-specific emission, because structurally different name, expression, and
value trees can produce the same visible form. Explicit component rendering is
not deduplicated.

During migration, immutable v2 notation remains exported from
`galaga.presentation` and `galaga.facade`; the legacy `galaga.notation` module
is not replaced until its Phase 7 compatibility cutover.

While both engines remain live, an implementation-neutral expression registry
constructs equivalent values against legacy and facade adapters. It compares
expression, concrete value, full display, rich display, and numeric
coefficients. Exact matches are permanent regression cases. Differences must
match an executable review ledger, and each audit writes a structured Markdown
artifact containing both LaTeX outputs. Reviewed entries are emitted with their
accepted checkbox and rationale already populated. The first remediation
reduced 57 differences to eight explicit Galaga 2 decisions: two corrected
unscaled products, one accepted accent choice, four legacy renderer recursion
failures, and one provenance-preserving multi-grade projection. This makes the
legacy renderer a bounded differential oracle rather than an undocumented
compatibility requirement.

An independent exact configured-rendering suite records literal LaTeX for
representative combinations of implementation, algebra/presentation, display
policy, and notebook-derived compound expression. This prevents shared v1/v2
mistakes and facade-only configuration regressions from passing merely because
the differential oracle has no disagreement. Domain-specific STA and RGA files
keep the human-reviewed examples discoverable; the RGA contract additionally
pins all Lengyel operation spellings, every blade label, signed orientation,
and the visible position of Unicode bulk/weight dual markers.

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
- Good, because ordinary displays omit implementation tolerances while custom
  tolerance choices remain visible and reproducible.
- Good, because exact-zero and unit-scalar structural identities render cleanly
  without changing retained provenance.
- Good, because conventional sums render negative addends as subtraction
  without string inspection in an output-specific emitter.
- Good, because left-associated subtraction extends a visible sum without
  redundant parentheses while a meaning-changing right subtraction remains
  grouped.
- Good, because reflected addition preserves source order in provenance rather
  than relying on numeric commutativity.
- Good, because context-local teaching presentations remain safe across threads
  and async tasks.
- Good, because differential reports distinguish numeric changes, provenance
  changes, and presentation-only changes before top-level cutover.
- Cost, because accepted legacy/facade differences require a reviewed ledger
  entry until they converge or receive a final Galaga 2 decision.
- Cost, because the layout model has more node types than a direct string
  renderer.
- Cost, because malformed third-party rules need validation and functional
  fallback behavior.
- Limitation, because this tree applies only the separate conservative
  structural simplifier; it is not a general geometric-algebra simplifier,
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
