---
status: superseded
date: 2026-07-04
deciders: edouard
superseded_by: 010-replace-labels-with-names
---

# ADR-007: Auto-labeling Between MV and Matrix Representations

> Superseded by [ADR-010](010-replace-labels-with-names.md): MatrixRepr
> provenance now uses `.name()` and symbolic representation-map expressions,
> not render-only `.label` metadata.

## Context and Problem Statement

When converting between multivectors and matrices, users want to see where a
matrix came from and what a recovered multivector represents. A matrix displayed
as a bare pmatrix with no context is less useful than one labeled with the
name of the source multivector. Similarly, recovering an MV from a named matrix
should carry provenance information.

## Decision Outcome

Use the representation map notation ρ and ρ⁻¹ as automatic labels:

### `to_matrix(mv)` → MatrixRepr label

If `mv` has a name (checked via `_name_latex` or `_name`), the resulting
`MatrixRepr.label` is set to `\rho(<name>)`.

Example: `to_matrix(R.name(latex=r"\psi"))` produces a matrix that renders as
`ρ(ψ) = (matrix contents)`.

If the MV is unnamed, `label` is `None` (no decoration).

### `from_matrix(alg, M)` → MV name

If the `MatrixRepr` has a non-None `label`, the recovered multivector is named
`\rho^{-1}(<label>)` via `.name(latex=...)`.

Example: `from_matrix(alg, M)` where `M.label = r"\sigma_1"` produces an MV
named `ρ⁻¹(σ₁)`.

If the input is a raw numpy array or an unlabeled `MatrixRepr`, the MV is unnamed.

### Design choices

- **Labels don't propagate through arithmetic** — `M @ N` has `label=None`.
  The ρ label names the *representation of a specific MV*, not a derived quantity.
- **ρ⁻¹(ρ(name)) is intentionally verbose** — Roundtripping a named MV through
  matrix form and back gives `ρ⁻¹(ρ(ψ))`. This is mathematically correct and
  makes the provenance chain visible. Users who want a clean name can call
  `.name()` again.
- **ASCII fallback** — If only `_name` (not `_name_latex`) is set, it's used
  directly in the ρ(...) label.

### Consequences

- Good, because matrix output in notebooks shows where it came from
- Good, because recovered MVs carry provenance without manual naming
- Good, because unnamed objects pass through silently (no noise)
- Neutral, because roundtrip names are verbose but correct
