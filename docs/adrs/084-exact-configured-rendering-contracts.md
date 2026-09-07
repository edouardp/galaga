---
status: accepted
date: 2026-07-19
deciders: edouard
---

# ADR-084: Exact Configured Rendering Contracts

## Context and problem statement

The legacy/facade differential audit proves whether two implementations agree,
but agreement is not proof that either output is the rendering Galaga intends.
The maintained Marimo notebooks prove that expressions execute and can be
rendered, but they do not pin the exact emitted LaTeX. A renderer regression can
therefore remain invisible when both implementations share it, when only one
implementation supports a presentation setting, or when a notebook continues
to execute with less readable output.

Rendering depends on more than an expression. The numeric algebra, blade
convention, display order, notation, content policy, zero cutoff, coefficient
precision, and implementation version can all affect the correct string. The
test identity must include those inputs rather than treating one expression as
having a context-free expected rendering.

## Decision drivers

- Store human-reviewed exact LaTeX rather than relying only on renderer parity.
- Exercise realistic compound expressions taken from maintained notebooks.
- Preserve cross-version evidence without copying expression-building code or
  requiring the retired engine to execute.
- Make algebra and display configuration visible in every failing Pytest ID.
- Keep tests independent of Marimo cells, dynamic Python locals, and ambient
  presentation context.
- Make a newly discovered rendering defect easy to add as a permanent guard.

## Decision outcome

Galaga keeps an exact configured-rendering contract alongside the differential
parity audit. A scenario has four independent identifiers:

1. implementation (`core-facade-v2` live, `legacy-v1` in historical evidence);
2. algebra profile, including its metric and presentation convention;
3. display profile, including content, zero cutoff, and coefficient precision;
4. value-returning compound-expression test function.

`tools.rendering_contract` owns immutable algebra profiles, display profiles,
named complete configurations, and the small public-facade context adapter.
`tools.latex_contract` owns a lightweight `@latex_test(...)` decorator and
`testcase(...)` values. Each decorated function contains the ordinary
expression-building code and returns its multivector result. The decorator
looks up each named algebra, passes a fresh `ExpressionContext`, and compares
full LaTeX only after the function has returned. This makes the lifetime
contract executable: a result must retain everything needed to render without
its builder's local scope.

Test functions use explicit semantic basis lookup and ordinary local variables.
They never mutate a function frame through `locals()`.

Exact expected strings are grouped by mathematical domain in
`tests/rendering/test_compound_latex_contract.py`,
`test_sta_latex_contract.py`, and `test_rga_latex_contract.py`. Standard Pytest
parameterization gives every assertion a stable named-algebra ID underneath
the human expression test name. The expression body and all exact expected
strings are adjacent in the test source. A construction check covers every
named algebra configuration. Default notebook scenarios were captured for both
implementations before the live v1 path was retired in Phase 9.

For readability, `testcase()` accepts raw triple-quoted LaTeX. It dedents the
literal, strips the edge whitespace, and joins its physical source lines with
one space before comparison. Whitespace within each authored line remains
exact; the facility formats test source rather than making emitted LaTeX
arbitrarily whitespace-agnostic.

The default matrix covers Euclidean Cl(2) and Cl(3), mostly-minus STA,
three-dimensional PGA, and Lengyel RGA. Notebook-derived test functions cover
mixed grades, exterior area and volume, rotor sandwiches, projection,
electromagnetic field construction and invariants, null vectors, STA
pseudoscalar structure, non-collinear boost composition, a PGA join, and the
RGA product decomposition, meet, bulk/weight projections and duals, nested
complements, and transwedge families. The STA samples come from maintained
notebooks in both the main repository and `galaga-marimo-demos`; the RGA
samples come from the maintained RGA demo and source-derived numeric tables. A
separate exact RGA matrix owns every Lengyel operation spelling and all sixteen
blade labels. A display-sensitive compound vector exercises exact-zero and
unit-scalar normalization, near-zero cutoff behavior, and three, six, and
twelve significant-digit policies.

The conventional Galaga 2 contract pins left and right contractions to the
mirrored LaTeX floor symbols `\mathbin{\rfloor}` and
`\mathbin{\lfloor}`. The archived legacy expectation intentionally retains its
historical corner symbol, making this reviewed presentation change explicit
rather than weakening the exact comparison.

The golden contract and differential audit have distinct authority:

- the golden contract decides the exact output for one complete configuration;
- the differential audit discovers and classifies cross-version differences;
- notebook execution proves the surrounding integration still runs.

One does not replace either of the others. Configuration combinations with no
faithful v1 equivalent are facade-only cases rather than artificial parity
comparisons.

### Phase 9 retirement of the live v1 adapter

On 2026-09-06, the three exact suites stop constructing v1 contexts and leave
the legacy-construction allowlist. Their expression bodies, source citations,
34 v2 full-LaTeX cases, 26 three-channel RGA operation contracts, and complete
16-blade RGA table remain live. The seven named facade configurations retain
their existing IDs, including the two additional precision policies.

The development-only
[configured-rendering archive](../../packages/galaga/tools/baselines/configured-rendering-v1.json)
preserves the 32 historical full-LaTeX observations and all 26 RGA operations'
Unicode and LaTeX spellings. Every observation was computed and checked
against its original literal at commit
`af3c167c188f2174fad65948e17d9b2706ee755b`, using Python 3.14.4 and NumPy 2.5.2.
The archive records source-test identity, source descriptions where available,
configuration, coefficient data, and the old compound cases' native vector order.

Numeric regression tests transport the old compound coefficients into the
current exterior basis using actual wedge products of semantically matched
vectors. This matters for PGA's e0-first versus e0-last coefficient storage;
indices cannot be compared directly or corrected by guessed signs. All 32
pre-retirement compound comparisons had zero mapped residual on the capture
run. Ongoing comparisons use `rtol=0, atol=1e-12`; public equality and hashing
are unaffected. The RGA operation samples also retain coefficient checks.
These samples supplement, not replace, the direct-core algebraic identities.

Current exact strings stay adjacent to their expression bodies and remain the
rendering authority, including reviewed differences from v1. The archive must
not be regenerated from current output. New v2-only tests can be added without
inventing historical observations; inventory checks require preservation of
the historical subset, not a permanently frozen live test count.

A fresh process runs all three suites with legacy imports forbidden. It omits
the parent conftest because that temporary guard itself imports v1 to poison
constructors; ordinary full-suite runs still use that guard. Context-boundary
tests also reject retired implementation IDs and malformed semantic vector
maps and cover public operations, immutable naming, display channels, and
post-builder rendering. No production engine or rendering implementation is
changed by this checkpoint.

## Consequences

The remaining RGA convention-layer source suite is also migrated in
[ADR-105](105-public-rga-contracts-and-underaccent-fallback.md). Its separate
archive retains all original identities, oriented basis values, and observed
outputs. Nonzero coefficient oracles complement this exact spelling matrix;
the custom under-accent fallback is fixed without changing default Lengyel
output or the existing exact configured-rendering contracts.

- Good, because two renderers can no longer agree on a wrong string silently.
- Good, because a failure names the complete configuration that produced it.
- Good, because notebook examples become reusable unit-level rendering inputs.
- Good, because exact whitespace, grouping, commands, coefficient formatting,
  blade typography, and teaching equalities are reviewable code changes.
- Good, because regression cases do not require Marimo or lexical-local tricks.
- Good, because v1/v2 differences such as reverse accents and PGA blade order
  can be captured honestly instead of weakening the assertion.
- Cost, because intentional rendering changes require updating reviewed literal
  strings.
- Cost, because representative coverage is curated rather than an exhaustive
  Cartesian product of every algebra, policy, and expression.
- Limitation, because emitted LaTeX equality does not prove two renderings have
  identical visual pixels in every TeX engine.
