---
status: accepted
date: 2026-07-04
deciders: edouard
---

# ADR-006: MatrixRepr as Transparent Numpy Proxy

## Context and Problem Statement

Users working with matrix representations want to perform standard linear
algebra operations (products, inverses, transposes) without manually extracting
the underlying numpy array and rewrapping the result. They also want metadata
(algebra reference, representation mode, labels) to follow the matrix through
computations, and to display results in LaTeX without extra setup.

## Decision Outcome

Make `MatrixRepr` a transparent numpy proxy that:

1. **Forwards all arithmetic** — `@`, `+`, `-`, `*`, `/`, `**`, unary `-`
2. **Provides linear algebra methods** — `.T`, `.H`, `.conj()`, `.trace()`,
   `.det()`, `.inv()`
3. **Intercepts numpy operations** via `__array_ufunc__` so that `np.add(M1, M2)`,
   `np.conj(M)`, etc. return `MatrixRepr` instances
4. **Propagates metadata** — `algebra` and `mode` pass through to results;
   `label` does NOT propagate (it names a specific matrix, not derived ones)
5. **Preserves escape hatch** — `.mat` gives the raw numpy array at any time
6. **Supports indexing** — `M[i,j]` returns scalar, `M[0:2, 0:2]` returns
   `MatrixRepr` submatrix

### Factory methods

- `MatrixRepr.identity(k)` — k×k identity
- `MatrixRepr.zeros((m,n))` — zero matrix
- `.kron(other)` — Kronecker product

### Quaternion matrices

Quaternion `MatrixRepr` (from `to_quaternion_matrix`) stores a list-of-lists
of `Quat` objects. Arithmetic operations raise `TypeError` for these — only
rendering is supported. This can be extended later if quaternion arithmetic
is needed.

### Consequences

- Good, because users can chain operations: `(M @ N).inv().trace()`
- Good, because `to_matrix(R) @ to_matrix(S)` returns a usable `MatrixRepr`
- Good, because existing code using `np.allclose(to_matrix(v), ...)` still
  works via `__array__`
- Neutral, because we carry a thin wrapper overhead (one object + one pointer)
- Later, the same structure supports a symbolic expression tree for matrix ops
