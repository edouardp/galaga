---
status: accepted
date: 2026-07-19
deciders: edouard
---

# ADR-082: Matrix Provenance Is Package-Owned

## Context and problem statement

`MatrixRepr` historically reused `galaga.symbolic_core` for names, scalar
arithmetic, and expression rendering, then added matrix-specific nodes beside
it. Conversion also inspected Galaga 1 multivector fields such as `_expr`,
`_is_symbolic`, `_to_expr`, and private name spellings.

That coupling is wrong for Galaga 2. The immutable `galaga.expression` model
contains catalogued geometric-algebra operations. Matrix multiplication,
transpose, adjoint, inverse, basis change, Kronecker product, spinor-column
conversion, and the representation map `rho` are operations in the companion
package's domain. Adding them to the GA catalog would blur ownership and make
the base package depend on optional representation semantics.

## Decision drivers

- Keep `galaga_matrix` optional and independently evolvable.
- Preserve eager numeric matrices and evaluable operation provenance.
- Consume only public Galaga 2 names, expressions, and presentation objects.
- Keep expression nodes immutable and detached from mutable matrix storage.
- Make removal of legacy symbolic imports and private-field access executable.

## Decision outcome

`galaga_matrix.expr` owns a small immutable matrix-expression hierarchy. Its
frozen nodes cover matrix arithmetic, transpose, adjoint, conjugation, inverse,
basis change, Kronecker product, representation maps, and spinor columns.
Matrix leaf nodes snapshot NumPy data into read-only arrays, so later mutation
of a `MatrixRepr` cannot rewrite recorded provenance.

A `GalagaExpression` adapter is the only cross-domain node. It stores a public
`galaga.expression.Expr`, the explicit `PresentationConfig` used to render it,
and the eager facade value used to evaluate the surrounding representation.
Named facade values become matrix symbols using their public immutable `Name`.
Unnamed tracked values retain their public Galaga expression through the same
adapter. At render time the adapter resolves the value's public context-local
presentation, using the stored presentation only as a fallback, so scoped
teaching notation remains thread- and async-safe through a matrix conversion.

`MatrixRepr` exposes `symbolic_name`, `is_symbolic`, `expr`, and
`as_expression()` as its inspection boundary. Its established `.name()` method
remains an in-place matrix convenience, while the stored name itself is an
immutable `galaga.names.Name`. Conversion functions attach provenance through
matrix-owned methods and read no private multivector state.

The table-free Galaga 1 numeric fallback remains until the Phase 8 top-level
cutover, but Galaga 1 symbolic mutation is no longer a supported companion
boundary.

## Verification

Tests prove that:

- matrix expression nodes reject field assignment;
- captured matrix leaf arrays are read-only;
- expression evaluation reproduces eager matrix results;
- named and unnamed tracked facade values retain representation provenance;
- context-local facade notation remains effective after matrix conversion;
- basis-specific and quaternion representation notation remains correct;
- facade-to-matrix-to-facade names use only public `Name` values; and
- source checks reject `galaga.symbolic_core` imports and private multivector
  expression/name reads.

## Consequences

- Good, because the base GA expression catalog contains only GA operations.
- Good, because the optional matrix package owns its domain vocabulary and
  evaluation rules.
- Good, because facade notation can change without changing a stored Galaga or
  matrix expression.
- Good, because immutable snapshots prevent provenance from being rewritten by
  later NumPy mutation.
- Cost, because matrix expressions have their own small renderer rather than
  being native nodes in Galaga's semantic render tree.
- Cost, because callers that used private MatrixRepr fields must use the public
  inspection properties.
