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
- Parameterize legacy v1 and facade v2 without copying expression-building code.
- Make algebra and display configuration visible in every failing Pytest ID.
- Keep tests independent of Marimo cells, dynamic Python locals, and ambient
  presentation context.
- Make a newly discovered rendering defect easy to add as a permanent guard.

## Decision outcome

Galaga keeps an exact configured-rendering contract alongside the differential
parity audit. A scenario has four independent identifiers:

1. implementation (`legacy-v1` or `core-facade-v2`);
2. algebra profile, including its metric and presentation convention;
3. display profile, including content, zero cutoff, and coefficient precision;
4. value-returning compound-expression test function.

`tools.rendering_contract` owns immutable algebra profiles, display profiles,
named complete configurations, and the small v1/v2 context adapter.
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
named algebra configuration; default notebook scenarios are captured for both
live implementations.

For readability, `testcase()` accepts raw triple-quoted LaTeX. It dedents the
literal, strips the edge whitespace, and joins its physical source lines with
one space before comparison. Whitespace within each authored line remains
exact; the facility formats test source rather than making emitted LaTeX
arbitrarily whitespace-agnostic.

The default paired matrix covers Euclidean Cl(2) and Cl(3), mostly-minus STA,
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

The golden contract and differential audit have distinct authority:

- the golden contract decides the exact output for one complete configuration;
- the differential audit discovers and classifies cross-version differences;
- notebook execution proves the surrounding integration still runs.

One does not replace either of the others. Configuration combinations with no
faithful v1 equivalent are explicit facade-only cases rather than artificial
parity comparisons.

## Consequences

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
