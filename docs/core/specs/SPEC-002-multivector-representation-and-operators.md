# SPEC-002: Multivector Representation and Operators

**Status:** Implemented

## Intent

A multivector is an immutable numeric value in one algebra's exterior basis.
Its representation must not assume the basis is orthogonal.

## Coefficient representation

For an algebra of dimension `dim = 2**n`, `Multivector(algebra, data)` must
require a real finite array of shape `(dim,)`. The constructor must copy it to
`float64`, make the copy read-only, and retain the exact parent algebra object.

Coefficient masks mean:

| Mask | Meaning |
|---|---|
| `0` | Scalar basis blade |
| `1 << i` | Native basis vector `e_i` |
| Several bits | Ascending exterior product of the selected basis vectors |

A multi-bit mask must never mean an unexpanded geometric word.

## Immutability

`data` must be read-only. Arithmetic and named operations must return new
multivectors and must not mutate operands. Cached basis vectors may therefore
be returned repeatedly by identity.

`vector_part` must return a new array rather than a writable view into the
multivector.

## Algebra compatibility

Binary multivector operations require both operands to belong to the same
`Algebra` instance. Equal Gram matrices in different algebra objects are not
sufficient. Arithmetic and product operations must raise on an algebra
mismatch.

Equality between different algebra instances returns `False` rather than
raising.

## Arithmetic

The following operations are supported:

- addition and subtraction with a same-algebra multivector or real scalar;
- unary plus and minus;
- multiplication by a real scalar or geometric multiplication by a
  same-algebra multivector;
- division by a nonzero real scalar or scalar multivector;
- right division of a real scalar by an invertible multivector;
- division by a nonscalar multivector as multiplication by its inverse;
- integer exponentiation.

Integer powers must use the multiplicative identity for exponent zero and
`inverse` for negative powers. Boolean and nonintegral exponents are not
accepted as multivector powers.

Division by an exact zero scalar must raise `ZeroDivisionError`. Failure to
invert a nonscalar divisor must propagate as a noninvertibility error.

## Operators

| Syntax | Named meaning |
|---|---|
| `A * B` | `geometric_product(A, B)` |
| `A ^ B` | `outer_product(A, B)` |
| `A | B` | `doran_lasenby_inner(A, B)` |
| `~A` | `reverse(A)` |
| `A[k]` | `grade(A, k)` |
| `A["even"]` | `even_grades(A)` |
| `A["odd"]` | `odd_grades(A)` |

Real scalars may participate with `^` and `|` by coercion to scalar
multivectors. Named functions remain the authoritative convention.

## Grade inspection

`homogeneous_grade(atol=...)` returns the sole grade containing a coefficient
whose magnitude exceeds the tolerance. It returns `None` for a zero or
mixed-grade value.

`grade(A, k)` returns zero for an integer grade outside `[0,n]`.
`basis_blades(k)` is stricter and rejects an out-of-range requested grade.
`grades(A, values)` ignores out-of-range integer entries but rejects noninteger
entries.

## Scalar conversion

`grade(A, 0)` is the canonical scalar projection and returns a scalar
multivector regardless of the other grades in `A`. Consequently,
`float(grade(A, 0))` is the canonical composition for extracting coefficient
zero from any multivector.

An implementation may expose a standalone `scalar_part(A)` convenience helper.
If present, it returns a Python `float` and must be equivalent to
`float(grade(A, 0))`. It is an optional helper rather than required
`Multivector` member API.

`float(A)` succeeds only when all nonscalar coefficients are within the
homogeneous-grade inspection tolerance. `abs(A)` is defined as
`abs(float(A))`, not as the multivector norm.

`np.float64(A)` may use the same Python `__float__` conversion. This does not
constitute NumPy array protocol support. `Multivector` does not implement
`__array__`, `__array_ufunc__`, or `__array_function__`; `np.asarray(A)` must
not be documented as a coefficient conversion, and NumPy transcendental
ufuncs are not aliases for `galaga.core`'s named numeric functions. Callers use
`A.data`, `float(A)`, or a named core operation according to intent.

The current implementation's `.scalar_part` property predates this API
decision and remains temporarily as compatibility surface until the code and
tests are migrated.

## Equality and hashing

`==` uses exact coefficient-array equality and exact parent-algebra identity.
Comparison with a real scalar uses exact equality against the corresponding
scalar multivector.

`almost_equal(other, atol=...)` is the explicit approximate comparison. It
uses zero relative tolerance and also requires algebra identity.

The hash combines parent-algebra identity with exact coefficient bytes. This
preserves the Python invariant that equal values have equal hashes.

## Representation scope

The numeric representation is real and dense. Complex coefficients, symbolic
coefficients, expression nodes, display names, and mutable coefficient views
are outside this specification.
