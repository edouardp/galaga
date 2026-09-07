---
status: accepted
date: 2026-09-07
deciders: edouard
---

# ADR-098: Expression Contracts Outlive Legacy Provenance

## Context and problem statement

The remaining numeric-function expression and parenthesization suites still
used the legacy engine, private symbolic flags, mutable names, and implicit
expression rendering. Their 29 cases cover useful numeric and grouping
contracts, but those implementation details are superseded by
[ADR-077](077-optional-expression-provenance.md) and
[ADR-078](078-shared-semantic-rendering-pipeline.md).

Both original suites passed before migration. Direct execution of the same
recipes through both engines established equal coefficients in all 29 cases.
Display differences must be reviewed separately from that numeric agreement.

## Decision outcome

Keep all 29 legacy observations in the development-only
[expression archive](../../packages/galaga/tools/baselines/expression-contracts-v1.json),
captured at commit `f20a082ea077073285b73b23ac46543d57128300`, with Python
3.14.4 and NumPy 2.5.2. Record the signature, native vector masks, scalar inputs,
rotor parameter, equivalent recipes, coefficients, three formatted outputs,
and full LaTeX. The archive is evidence, not an executable legacy adapter or
a baseline automatically regenerated from v2.

Run both suites against the public facade. Each of the 25 grouping recipes
must match its archived coefficients both eagerly and through explicit
expression replay, and match independently stored, reviewed literal v2
strings in ASCII, Unicode, and LaTeX. Rendering must leave coefficients and
the retained expression unchanged.

The numeric-function suite retains its four original scenarios and adds
checks for all four name/tracking states, eager domain errors, explicit
symbol environments, and replay without mutation. Rotor roots also have
independent scalar closed-form checks. For two basis vectors, derive the
bivector square from the actual Gram entries and verify it against their
product and public left action before choosing trigonometric, hyperbolic,
or nilpotent formulas. Cover default and non-default square-root tolerances.

Existing v2 differences remain explicit:

- `named()` alone leaves the value untracked; applying an operation to a
  named or tracked operand starts or propagates provenance.
- Request provenance with `display("expr/latex")` or another explicit target.
  Anonymous tracked values display concrete coefficients by default; named
  values use a deduplicated teaching equality.
- ASCII uses ASCII-safe operators; Unicode uses combining accents and its
  own star spelling. Infix spacing, reverse accents, and conservative
  negated-product parentheses differ from some legacy outputs.
- The conventional hat still denotes both unit normalization and grade
  involution. Their operation IDs and numeric results remain distinct;
  functional notation disambiguates them. This migration does not claim
  unique glyphs for every operation.
- A product under a square must retain its grouping: `(ab)^2` is not `ab^2`.
  The old no-parentheses product example in
  [ADR-023](023-squared-parenthesization.md) does not describe current behavior.

Fresh-process tests run both complete suites with legacy imports prohibited,
and both files leave the constructor-exemption ledger. Mutation checks reject
wrong eager values, replay results, and rendered grouping independently,
including a wrong root carrying the correct expression. Shape, finiteness,
and tolerance checks prevent broadcasting or nonfinite data from passing.

## Consequences and boundaries

- Good, because the original mathematical and pedagogical responsibilities
  survive without importing the old arithmetic or rendering engine.
- Good, because exact grouping checks replace earlier substring/smoke checks
  for sandwiches, double reverse, and unit normalization.
- Boundary, because this changes tests and documentation, not production
  arithmetic, provenance, notation, or display defaults.
- Pending, because fifteen other files still require legacy construction;
  remaining symbol, notation, mixed expression, namespace, and engine-deletion
  work is separate from this checkpoint and the final release gates.
