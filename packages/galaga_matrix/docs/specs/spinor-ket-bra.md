# SPEC: Spinor Columns as MatrixRepr with Ket/Bra Semantics

## Status

Accepted — implemented.

## Problem

`to_spinor_column` returns a raw numpy array. This loses metadata (algebra,
basis, name) and prevents chaining operations or automatic basis handling.
Meanwhile `to_matrix` returns a rich `MatrixRepr`. The two should be
consistent.

## Rules

### Rule 1: MatrixRepr.kind attribute

`MatrixRepr` gains a `kind` attribute:

| Value        | Shape  | Meaning                   |
| ------------ | ------ | ------------------------- |
| `"operator"` | (k, k) | Matrix operator (default) |
| `"ket"`      | (k, 1) | Spinor column (ket)       |
| `"bra"`      | (1, k) | Spinor row (bra)          |

Default: `"operator"` for k×k, `"ket"` for k×1 from spinor functions.

### Rule 2: `to_spinor_column` returns MatrixRepr

```python
to_spinor_column(R)  # returns MatrixRepr with kind="ket"
```

Metadata set: algebra, mode="compact", basis (from algebra), kind="ket".
If MV is named, MatrixRepr `.name()` uses ket notation:
`\left|\rho(\psi)\right\rangle`.

### Rule 3: `from_spinor_column` accepts MatrixRepr

```python
from_spinor_column(M)       # MatrixRepr with kind="ket" — just works
from_spinor_column(alg, M)  # also works (explicit algebra)
from_spinor_column(alg, np.array(...))  # raw array — existing API
```

### Rule 4: Basis-aware spinor transforms

`to_basis()` checks `kind`:
- `"operator"`: similarity transform M' = S M S†
- `"ket"`: single-sided ψ' = S ψ
- `"bra"`: single-sided φ' = φ S†

### Rule 5: `.H` on ket gives bra

```python
ket = to_spinor_column(R)    # kind="ket", shape (k,1)
bra = ket.H                  # kind="bra", shape (1,k), conjugate transpose
```

The symbolic adjoint expression renders ket notation as a bra:
`|ψ⟩` → `⟨ψ|`.

### Rule 6: Type propagation under @

| Left     | Right    | Result kind                    |
| -------- | -------- | ------------------------------ |
| operator | operator | operator                       |
| operator | ket      | ket                            |
| bra      | operator | bra                            |
| bra      | ket      | scalar (numpy, not MatrixRepr) |
| ket      | bra      | operator (outer product)       |

### Rule 7: Naming

| kind          | Named MV "ψ" | Name/expression format           |
| ------------- | ------------ | -------------------------------- |
| ket           | yes          | `\left\|\rho(\psi)\right\rangle` |
| ket           | no           | unnamed                          |
| bra (from .H) | yes          | `\left\langle\rho(\psi)\right\|` |
| operator      | yes          | `\rho(\psi)` (existing)          |

### Rule 8: LaTeX rendering

Kets render as a column pmatrix (existing), optionally with ket decoration in
the symbolic name. Bras render as a row pmatrix.

### Rule 9: Backward compatibility

`to_spinor_matrix` / `from_spinor_matrix` remain as aliases.
Code doing `np.allclose(to_spinor_column(R), ...)` still works via
`__array__`.

## Examples

```python
sta = Algebra(1, 3)
g = sta.basis_vectors()
R = exp(-0.3 * (g[0] * g[1])).name(latex=r"\psi")

# Returns MatrixRepr ket
ket = to_spinor_column(R)
ket.kind          # "ket"
ket.shape         # (4, 1)
ket.basis         # "dirac"
ket.latex()       # r"\left|\rho(\psi)\right\rangle = \begin{pmatrix}..."

# Basis change (single-sided)
ket_weyl = ket.to_basis("weyl")
ket_weyl.basis    # "weyl"

# Bra from conjugation
bra = ket.H
bra.kind          # "bra"
bra.shape         # (1, 4)

# Inner product
overlap = bra @ ket    # complex scalar

# Operator acts on spinor
M = to_matrix(g[0])
result = M @ ket       # MatrixRepr with kind="ket"

# Roundtrip
from_spinor_column(ket)                  # recovers R
from_spinor_column(ket.to_basis("weyl")) # also recovers R (basis-aware)
```

## Edge Cases

- `to_spinor_column` on algebra that doesn't support roundtrip: still raises
  `TypeError` (unchanged).
- `.H` on an operator: still returns conjugate transpose operator (unchanged).
- `kind` propagation through arithmetic: `ket + ket = ket`,
  `scalar * ket = ket`, `ket / scalar = ket`.

## Impact

- New attribute: `MatrixRepr.kind` (str, default "operator").
- Modified: `to_spinor_column` return type changes from ndarray to MatrixRepr.
- Modified: `from_spinor_column` accepts MatrixRepr.
- Modified: `to_basis()` dispatches on kind.
- Modified: `.H` returns kind="bra" when source is kind="ket".
- Modified: `__matmul__` checks kinds for type propagation.
