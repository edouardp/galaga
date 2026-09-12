---
status: accepted
date: 2026-09-12
deciders: edouard
---

# ADR-132: Algebra-Level Expression Tracking Default

## Context

Teaching notebooks repeatedly request `expr=True` from individual algebra
factories. The user requested `Algebra(..., expr=True)` as an explicit default,
including when a complete preset supplies `config=`. Values must remain eager,
and opting out must not be undone by internal scalar coercion or model helpers.

## Decision

Add a strictly boolean, keyword-only `expr=False` to the public facade's
`Algebra` constructor and `Algebra.from_numeric`. Expose it through the
read-only `algebra.expr` property. This is a facade value-construction policy,
not a numeric-core setting, display policy, or `AlgebraConfig` component.
Complete presets keep describing metric, model metadata and presentation;
`Algebra(config=presets.sta(), expr=True)` selects tracking separately.

The following factories inherit the algebra default when `expr` is omitted
or explicitly `None`: `scalar`, `vector`, `multivector`, `blade`, `blades`,
`basis_vectors`, `basis_blades`, `pseudoscalar`, and `locals`. An explicit
boolean overrides the default. The four singular factories continue to accept
an explicit `Expr`, which takes precedence without changing the eager value.
Constructor `None`, integers, strings, and NumPy boolean scalars are rejected;
`None` means inheritance on factories and model constructors, not on `Algebra`.

`identity` and `I` follow the default too. Use `scalar(1, expr=False)` or
`pseudoscalar(expr=False)` when untracked equivalents are needed. Cached basis
vectors remain untracked internally; tracked requests wrap the same numeric
values rather than contaminating the cache.

All presentation-derived algebra views preserve the tracking default and
numeric identity. Presentation scopes do not change tracking. A new
`Algebra.from_numeric` call selects its own default explicitly. Direct
`Multivector` construction and internal result wrapping retain their existing
explicit metadata semantics; they do not consult the factory default.

### Arithmetic and integration boundaries

Expression propagation remains driven by named or tracked operands, never by
the owning algebra's default alone. An unnamed `expr=False` value stays
untracked under arithmetic with other unnamed/untracked values or Python
scalars. Scalar coercion must therefore construct its internal literals with
`expr=False`. Naming still enables subsequent operation provenance, as before;
factory opt-out is not a prohibition on future tracking.

Expression replay returns untracked numeric results, including scalar-valued
operations replayed into an expression-default algebra. Internal `_wrap` does
not generate expression nodes. Numeric-only execution still allocates no
provenance nodes.

`ConformalModel` and `RigidModel` inherit `algebra.expr` when their constructor
`expr` is omitted or `None`. An explicit model boolean overrides it, and an
explicit factory boolean overrides the model. Thus the effective default is
still false, but a notebook can enable tracking once at the algebra level.
Model-owned value factories forward the resolved policy. Scratch numeric
results and validation constants explicitly opt out where their accidental
literal provenance would bypass the model's semantic provenance policy.
The model then attaches the appropriate expression from its inputs and policy;
these internal opt-outs must not suppress requested public output tracking.

## Consequences

- Notebook authors can opt in once without changing metrics or arithmetic.
- Existing code that omits the new constructor option retains its behavior.
- Factory `expr=None` now means inheritance rather than an invalid flag.
- Equality, hashing, model metadata, numerical results and expression operation
  IDs are unchanged; no lazy evaluation or symbolic coefficient domain is added.
- The default is deliberately absent from preset/config objects and has no
  mutable setter or additional global context manager.

## Validation

Tests cover every factory with both defaults and overrides, explicit expression
objects, strict flag validation, zero-dimensional algebras, cache isolation,
presentation views, immutable public state, numeric identity and hashes.
Arithmetic and replay are compared with actual core products across Euclidean,
indefinite, oblique, null-pair and degenerate metrics. Negative allocation
checks protect the untracked arithmetic path. Model tests cover CGA/RGA
inheritance and explicit overrides. The eager-values teaching notebook
demonstrates the new default alongside an explicit numeric-only override.
