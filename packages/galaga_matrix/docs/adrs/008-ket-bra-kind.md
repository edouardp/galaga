---
status: accepted
date: 2026-07-04
deciders: edouard
---

# ADR-008: MatrixRepr.kind — Ket, Bra, and Operator Semantics

## Context and Problem Statement

`MatrixRepr` wraps both matrix operators (k×k) and spinor column vectors (k×1).
These transform differently under basis changes (similarity vs single-sided),
have different product semantics (operator×operator vs operator×spinor), and
render differently in LaTeX (plain matrix vs ket/bra notation).

Without tracking what a `MatrixRepr` represents, we cannot dispatch correctly.

## Decision Outcome

Add a `kind` attribute with three values:

| kind | Shape | Transform under basis change | Label notation |
|---|---|---|---|
| `"operator"` | (k, k) | M' = S M S† (similarity) | `\rho(name)` |
| `"ket"` | (k, 1) | ψ' = S ψ (left-multiply) | `\|ρ(name)⟩` |
| `"bra"` | (1, k) | φ' = φ S† (right-multiply) | `⟨ρ(name)\|` |

### Product type propagation

| Left kind | Right kind | Result |
|---|---|---|
| operator | operator | operator |
| operator | ket | ket |
| bra | operator | bra |
| bra | ket | scalar (complex, not MatrixRepr) |
| ket | bra | operator (outer product) |

### `.H` converts ket ↔ bra

`ket.H` returns a `MatrixRepr` with `kind="bra"` and vice versa.
For operators, `.H` returns the Hermitian adjoint operator (unchanged behavior).

### Consequences

- Good, because `to_basis("weyl")` automatically does the right transform
  for both operators and spinors without the user specifying
- Good, because `bra @ ket` gives a scalar (inner product) naturally
- Good, because `to_matrix(g0) @ to_spinor_column(R)` returns a ket
- Good, because labeling in notebooks shows ket/bra notation
- Neutral, because `kind` defaults to `"operator"` so all existing code
  is unaffected
