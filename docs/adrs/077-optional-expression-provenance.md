---
status: accepted
date: 2026-07-19
deciders: edouard
---

# ADR-077: Optional Expression Provenance over Eager Facade Values

## Context and problem statement

Galaga's legacy expression design combined eager coefficients, mutable naming,
operation-specific expression classes, rendering behavior, and symbolic/lazy
vocabulary. Galaga 2 needs inspectable operation history for teaching,
rendering, and companion packages, while preserving the now-proven
Gram-matrix numeric core and its small immutable value model.

Expression support must not become a second arithmetic implementation. It
must reproduce eager results, cover parameterized and variadic facade calls,
remain independent of presentation targets, and impose no expression-object
allocation on users who do not opt in.

## Decision drivers

- Keep `galaga.core` numeric and independent of facade and rendering code.
- Preserve eager numeric results as the authoritative value.
- Make naming and expression tracking immutable and independent.
- Give every expression operation the same stable identity and parameter
  schema as facade dispatch.
- Evaluate saved provenance without legacy expression methods or renderer
  dependencies.
- Preserve exact left-association for variadic source calls.
- Avoid promising general geometric-algebra simplification without a separate
  specification and proof strategy.

## Decision outcome

Galaga 2 uses a composition facade whose multivectors hold optional `Name` and
`Expr` references alongside a concrete `core.Multivector`. `named`, `unnamed`,
`with_expr`, and `without_expr` return new wrappers sharing that concrete
value. Naming does not attach provenance to the named value itself, and
equality and hashing ignore both metadata fields.

Expression nodes live in `galaga.expression`. The format-neutral immutable
model consists of `Symbol`, `ScalarLiteral`, `BladeLiteral`,
`MultivectorLiteral`, and generic `Call`. A call stores a stable catalog
operation ID, expression operands, and normalized immutable parameters. The
legacy `galaga.expr` namespace is not replaced before its compatibility
cutover.

Optional numeric tolerances are stored only when they differ from the public
operation default. Default calls therefore remain mathematical expressions
such as `inverse(x)` rather than exposing implementation thresholds, while a
non-default tolerance remains normalized provenance and reproduces evaluation.
Reflected commutative operators also preserve the user's source operand order;
numeric commutativity is not permission to reorder provenance.

`OperationSpec` is extended with expression arity, `ParameterSpec` schemas,
and a result kind. Numeric evaluator arity remains separate: a grade call, for
example, has evaluator arity two but one expression operand plus a normalized
target parameter. The same spec validates constructed calls and evaluates
them.

Facade dispatch computes eagerly exactly once per binary edge. A named or
tracked operand starts or propagates provenance; named operands become symbol
leaves and unnamed values contribute existing provenance or literal leaves.
This prevents an intermediate unary operation from replacing a semantic name
with its current numeric value. If every operand is anonymous and untracked,
dispatch constructs no expression node. Geometric and outer product retain
binary catalog identity while their variadic facade forms lower to explicit
left-associated call trees, including an earlier untracked prefix.

Standalone evaluation requires an algebra and an explicit environment for
symbols. It resolves calls through the operation catalog. Algebra mismatches,
missing symbols, and literal dimension mismatches are errors.

Simplification is a fixed-point pass restricted to structural identities and
scalar-literal folding. It never reorders operands, flattens nonassociative
operations, or attempts general geometric-algebra simplification.

## Consequences

- Good, because every tracked value still owns a complete eager numeric
  result and can drop provenance in constant time.
- Good, because the numeric-only core and untracked facade path remain free of
  expression objects.
- Good, because operation identity, arity, parameter normalization, dispatch,
  and replay have one catalog owner.
- Good, because a semantic name survives intermediate operations without
  requiring a redundant `with_expr()` call.
- Good, because expression identity is stable across ASCII, Unicode, LaTeX,
  and temporary teaching presentations.
- Good, because variadic provenance records the same evaluation association
  as the numeric path.
- Cost, because facade wrappers now contain two optional metadata references.
- Cost, because operation declarations distinguish evaluator arity,
  expression arity, parameters, and result kind.
- Good, because `norm()` retains its direct float result for anonymous numeric
  inputs while named or tracked inputs produce a renderable scalar multivector
  with checked `float()` conversion.
- Limitation, because predicate results cannot retain `.expr`; they terminate
  attached provenance, although explicit catalog calls remain constructible
  and evaluable.
- Deferred, because semantic render trees, emitters, legacy expression-class
  adapters, and companion-package migrations remain later phases.

## Superseded legacy behavior

This decision supersedes the Galaga 2 direction of ADR-018, ADR-020, ADR-021,
ADR-026, ADR-046, ADR-047, ADR-062, and ADR-065 where those records couple
expressions to mutable value state, operation-specific node classes,
symbolic/lazy terminology, or the legacy operation registry. It retains
ADR-014's fixed-point idea but narrows the initial Galaga 2 simplifier to
proven structural rules.
