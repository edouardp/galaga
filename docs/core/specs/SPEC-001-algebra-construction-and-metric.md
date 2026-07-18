# SPEC-001: Algebra Construction and Metric Metadata

**Status:** Implemented

## Intent

Every accepted constructor form must produce the same canonical metric model:
one immutable real symmetric Gram matrix in the user's native basis.

## Constructor forms

Exactly one metric description must be supplied.

| Form | Meaning |
|---|---|
| `Algebra(p, q=0, r=0)` | `Cl(p,q,r)`, ordered as null, positive, negative |
| `Algebra(signature=values)` | Explicitly ordered diagonal values `+1`, `-1`, or `0` |
| `Algebra(sig=values)` | Exact alias for `signature=` at construction |
| `Algebra(gram=matrix)` | Arbitrary nonempty real symmetric Gram matrix |

`signature=` and `sig=` must not both be supplied. `gram=` and an explicit
signature must not be combined with positional `p`, `q`, or `r` values.

The positional counts must be integers other than booleans and must be
non-negative. Their diagonal order is

```text
(0,) * r + (1,) * p + (-1,) * q
```

`Algebra(0)` is the zero-generator scalar algebra with `n == 0`, `dim == 1`,
empty signature, determinant `1`, and inertia `(0, 0, 0)`. An explicit empty
`signature=` and an empty `gram=` matrix are rejected.

## Gram validation

`gram=` must be:

- two-dimensional and square;
- nonempty;
- real numeric and finite;
- symmetric under construction tolerances `rtol=1e-12` and `atol=1e-12`.

Accepted numerical asymmetry must be canonicalized as `(G + G.T) / 2`. The
result must be copied to `float64` and made read-only. Later mutation of the
caller's input must not affect the algebra.

No entry may be rounded to zero after canonicalization. In particular, a tiny
nonzero off-diagonal entry changes both orthogonality classification and
Clifford products.

## Explicit signature validation

An explicit signature must be a nonempty one-dimensional real finite array
whose entries are exactly members of `{+1, -1, 0}`. Caller order must be
preserved.

## Identity and backend arguments

`id=` may be `None` or a nonempty string. It is diagnostic metadata and must
not change metric or product behavior.

`product_backend=` must be a string accepted by
[SPEC-004](SPEC-004-product-backends.md).

## Public metric properties

| Property | Required behavior |
|---|---|
| `gram` | Return the canonical read-only `float64[n,n]` matrix |
| `basis_squares` | Return the read-only diagonal of `gram` in native basis order |
| `n` | Number of basis vectors |
| `dim` | Exterior/Clifford coefficient dimension `2**n` |
| `is_orthogonal_basis` | Exact equality of `gram` and `diag(basis_squares)` |
| `inertia` | `(positive, negative, null)` eigenvalue counts |
| `metric_rank` | `positive + negative` from the same classification |
| `metric_determinant` | Unthresholded numeric determinant |
| `is_degenerate` | Whether the null inertia count is nonzero |

For a nonempty matrix, inertia classification must use the symmetric
eigenvalues with tolerance

```text
n * float64_epsilon * max(abs(eigenvalues))
```

This tolerance is classification-only and must not alter the metric or product
coefficients.

## Legacy `signature`

`signature` is available only when the native basis is exactly diagonal and
every basis square is one of `+1`, `-1`, or `0`. It returns those values in
native basis order.

For a scaled diagonal or nonorthogonal metric, `signature` must raise rather
than return a lossy diagonal or a basis-independent inertia signature. Callers
must use the property matching their question:

- `gram` for all pairings;
- `basis_squares` for native basis-vector squares;
- `inertia` for the abstract real Clifford-algebra class.

## Value factories

| Factory | Required behavior |
|---|---|
| `multivector(data)` | Require exactly `dim` real finite coefficients |
| `scalar(value)` | Place one real value at mask zero |
| `vector(values)` | Require exactly `n` coefficients and place them at one-bit masks |
| `blade(mask)` | Return a unit exterior basis blade for `0 <= mask < dim` |
| `basis_vectors()` | Return the canonical one-hot vectors in Gram-matrix order |
| `basis_blades(k)` | Return all unit masks of grade `k` in increasing mask order |
| `pseudoscalar()` and `I` | Return the full-mask exterior blade |
| `identity` | Return scalar one |

Returned multivectors must satisfy [SPEC-002](SPEC-002-multivector-representation-and-operators.md).
