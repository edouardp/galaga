---
status: accepted
date: 2026-09-06
deciders: edouard
---

# ADR-012: General-Gram Compact Representations Use an Exterior Lift

## Context and Problem Statement

The compact representation previously assigned gamma matrices only to a
normalized orthogonal basis. For a dense or nonnormalized Gram matrix $G$, a
nondegenerate real Clifford algebra is still congruent to a normalized
signature algebra, but native multivector coefficients refer to exterior
blades in the stored basis.

Transforming vector gamma matrices is necessary but not sufficient. In a
nonorthogonal basis,

$$
e_i e_j=G_{ij}+e_i\wedge e_j,
$$

so an ordered product of transformed generators does not represent the native
bivector coefficient. The same issue propagates to every higher grade. The
implementation needs a basis-correct map, deterministic cached metadata, and
the existing strict inverse guarantees.

## Decision Outcome

For explicit `mode="compact"` and a nondegenerate real symmetric Gram matrix,
factor the metric as

$$
G=S\eta S^{\mathsf T},
$$

where positive directions precede negative directions in the normalized
diagonal metric $\eta$. Galaga core's scale-aware inertia is authoritative:
any direction classified as radical keeps the existing degenerate-algebra
`NotImplementedError`.

Use two deterministic factorization paths:

- a signed diagonal scaling for nonnormalized diagonal metrics; and
- `numpy.linalg.eigh` for dense symmetric metrics, ordering positive
  eigendirections before negative ones and fixing each eigenvector sign by its
  largest-magnitude component.

Validate the reconstruction residual using a dimension- and scale-aware
floating-point tolerance. Repeated eigenspaces do not define a unique public
matrix convention; the process-local cached plan supplies consistency for a
given algebra object, while algebraic behavior rather than individual entries
is the compatibility contract.

If $\gamma_a$ are the existing compact generators for $\eta$, map each native
vector to

$$
\Gamma_i=\sum_a S_{ia}\gamma_a
$$

and validate

$$
\Gamma_i\Gamma_j+\Gamma_j\Gamma_i=2G_{ij}I.
$$

Map native exterior blades through the induced exterior power. For equal-grade
ordered index sets $I$ and $A$,

$$
\rho(e_I)=\sum_{|A|=|I|}\det(S_{I,A})\rho(f_A).
$$

This minors-based construction is the only source for higher-grade native
blade matrices. It deliberately does not multiply the transformed generators
in canonical order.

Store the immutable Gram matrix, inertia, $S$, $\eta$, $S^{-1}$, residual,
condition estimate, tolerance, and factorization convention in the cached
`MetricCongruence`. General-Gram compact plans use the stable descriptor
convention `general-gram-congruence-v1` and no named textbook basis. Forward
and inverse matrix conversion share the exterior-lifted plan from ADR-011.

Spinor-column conversion remains restricted to normalized orthogonal native
bases. Its fixed reference-spinor and Pauli/Dirac basis labels require a
separate basis-independent design before they can consume a general-Gram plan.
Likewise, named Dirac/Weyl/Majorana basis changes reject compact matrices whose
algebra is not $\operatorname{Cl}(1,3)$ or $\operatorname{Cl}(3,1)$, even when
an unrelated representation also happens to be $4\times4$.
Matching inertia alone is insufficient: general-Gram matrices of either
signature also reject these named basis changes, because an unspecified
generic convention must not be inferred to mean the named Dirac convention.

This work does not change automatic dispatch. `mode=None` remains compact only
for normalized orthogonal metrics and remains left-regular for dense or scaled
metrics. It also does not reinterpret the named `pauli`, `dirac`, or
`quaternion` modes: those conventions continue to require their normalized
orthogonal native bases.

The real rank of the complete exterior-blade system remains the authority for
inverse conversion. A rank-deficient one-summand representation is valid for
`to_matrix`, while `from_matrix` raises `TypeError` rather than inventing lost
coefficients. Rank and least-squares calculations normalize each represented
blade column first: changing the overall metric scale changes different grades
by different powers and must not create a false rank deficiency. Recovered
scaled coefficients are converted back to the native exterior basis before the
image residual is checked.

This rank normalization is not an accuracy guarantee for individual native
coefficients. Grade-dependent scales can cause cancellation in forward matrix
assembly even when the vector transform is well-conditioned. Documentation
must distinguish algebraic injectivity, matrix-image residuals, and native
coefficient recovery error.

## Consequences

- Good, because explicit compact matrices now preserve products and native
  exterior coefficients for nonnormalized diagonal and dense nonorthogonal
  metrics.
- Good, because the implementation derives all blade maps from $G$ and the
  congruence rather than hardcoding metric-dependent signs or coefficients.
- Good, because the vector relations and every exterior grade have independent
  algebraic test oracles.
- Good, because automatic mode and named textbook conventions do not silently
  change.
- Good, because broader compact support does not accidentally relabel generic
  spinor columns or unrelated $4\times4$ matrices as Dirac conventions.
- Good, because strict rank and image checks retain the prior inverse contract.
- Cost, because first construction performs an eigendecomposition and a
  minors-based exterior lift; the bounded immutable plan cache amortizes that
  work.
- Cost, because generic dense metrics do not promise stable individual matrix
  entries across numerical libraries or future convention revisions.
- Neutral, because genuinely degenerate metrics still require left-regular
  matrices.

## Verification

Tests derive and verify vector anticommutators against every entry of $G$,
compare all blades in dimensions three and four with a fully antisymmetrized
gamma-product oracle, and compare native blades with an independently
outermorphed orthogonal algebra. Deterministic randomized tests verify product
homomorphism. Injective scaled and dense examples round-trip all coefficients;
a uniformly small metric verifies scale-normalized rank detection; and a dense
basis of $\operatorname{Cl}(0,3)$ verifies that genuine rank deficiency still
causes strict inverse failure. Tests also pin conservative automatic dispatch,
named-mode rejection, cache metadata, and array immutability.

The maintained Marimo notebooks
`general_gram_compact_foundations.py` and
`general_gram_compact_workflow.py` teach the product/exterior distinction and a
four-dimensional full-coefficient workflow. `cga_via_gram_matrix.py` then
constructs the native-null conformal model from its $5\times5$ Gram matrix and
connects compact point and translator matrices to geometric sandwiches. All
three pass dependency validation and headless execution.

`cga_complex_and_quaternion.py` adds an interactive object gallery, a
left-regular comparison, and explicit quaternion teaching constructions. It
derives the even CGA coordinate map into the existing auxiliary `Cl(1,3)`
quaternion representation, preserving that auxiliary provenance rather than
claiming native CGA conversion support. For a mixed value it derives a central
unit `J` from the pseudoscalar and encodes `A = E + B J` with two quaternion
matrices. This is a notebook-local encoding, not a new package representation
descriptor or completion of the planned native even-quaternion work unit.
Runtime tests check the map at two null-pair scales, every even blade, all 32
blades through the pair encoding, randomized products, geometric incidence,
translation, and scalar math rendering.
