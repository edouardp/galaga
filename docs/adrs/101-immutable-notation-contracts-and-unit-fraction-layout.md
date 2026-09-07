---
status: accepted
date: 2026-09-07
deciders: edouard
---

# ADR-101: Immutable Notation Contracts and Unit-Fraction Layout

## Context and problem statement

The legacy notation suite exercised mutable rules keyed by expression class
names. Its 101 test methods expanded to 239 cases: default layouts, overrides,
copy isolation, presets, functional notation, and normalization fractions.
V2 has immutable rules keyed by operation IDs, but retiring the suite exposed
two genuine presentation gaps.

First, `unit_fraction` from ADR-048 had no v2 counterpart. Second, the
Hestenes preset's generic dagger rule was shadowed by the default
target-specific LaTeX tilde. Thus Unicode and LaTeX made different choices.
Both were reproduced before their regression fixes.

## Decision outcome

### Retain the contracts, not mutable rule internals

The [historical archive](../../packages/galaga/tools/baselines/notation-contracts-v1.json)
captures all original method identifiers and case count, 47 default rule
families in three targets, 28 functional value/rendering observations,
unit-fraction examples, and actual scientific-style output. Its source is
commit `2174c76`, Python 3.14.4, NumPy 2.5.2. The archive retains the full
source commit and explicit input coefficients.

The live suite uses public facade values and standalone `Call` expressions.
Every original test class has a checked live owner. Forty-seven literal
three-target contracts pin reviewed default output; functional cases retain
coefficient, replay, spelling, and immutability checks. Known differences
remain explicit:

- Stable IDs replace old expression class names and mutable setters.
  `with_rule` returns a new value. A target-specific rule takes priority
  over a generic replacement; this resolution policy does not change.
- Missing rules have canonical functional fallback. Unknown rule metadata
  does not register a new numeric or expression operation.
- V2 retains its spacing, wide accents, contraction floors, unscaled
  Lie/Jordan products, and unambiguous short functional names.
  Multivector division is a product with inverse, not a `Div` node.
- V1's `log(a)` sample on a positive-square vector produced a value that
  fails an exponential round trip. Keep the observation as evidence, not
  accepted numeric parity. V2's eager normalized-rotor domain check remains;
  standalone symbolic display and a valid Gram-derived rotor are tested.
- Scientific-number emission retains the `times` style, but v2 currently
  has no `cdot`/`raw` selector or mutable `Notation.scientific`.
  Document that limitation; do not add unrelated display-policy API here.

### Restore the definition-shaped normalization display

Add `RenderRule("unit_fraction")` as an opt-in layout for `unit` only.
Configuration rejects attaching it to another operation. The builder emits
an existing `Fraction` with the same operand in its numerator and a
fixed norm `Wrapper` in its denominator. No node type, evaluator,
catalog operation, core arithmetic, or emitter is added.

The denominator denotes Galaga's actual metric norm,
$\sqrt{|\langle x\widetilde{x}\rangle_0|}$, not an assumption of positive
definiteness. It uses fixed conventional norm delimiters independently of a
custom `norm` rule; the layout is not a general denominator-transform API.
The existing fraction emitters handle compound grouping and target syntax.
The default unit hat is unchanged. Non-default controls remain visible
through canonical functional fallback, and singular normalization still
raises eagerly. Stored provenance remains `Call("unit", ...)`.

Independent grade signs and public left actions verify the norm and
normalization before any naming/layout work, across Euclidean, degenerate,
oblique, and native-null metrics. Tests cover mixed grades, negative squared
norms, null values, near-zero rejection, parameter retention, replay,
target isolation, immutable values, and the full hat-name/fraction/value
teaching equality.

### Make the Hestenes preset consistent across targets

Remove its inherited LaTeX-only reverse override so the preset's dagger rule
actually resolves in LaTeX. Do not change generic/target-specific precedence
or the default and Doran-Lasenby tilde presets. Tests exercise actual facade
rendering, not just the generic rule object, and deliberately reintroduce the
shadowing rule to prove the regression is detected.

## Consequences and boundaries

Fresh-process gates run the public notation and unit-fraction suites with all
legacy imports prohibited. Corruption tests distinguish incorrect eager
values, replay, formatting, and invalid archived numeric comparisons.
The maintained custom-notation notebook demonstrates both restored teaching
capabilities with executable algebraic assertions and dynamic math output.

`test_notation.py` leaves the construction-exemption ledger, reducing it
from thirteen to twelve files. Other legacy rendering/mixed suites, the
legacy notation module's eventual deletion, and final release gates remain
separate work. No changelog or release version is changed.
