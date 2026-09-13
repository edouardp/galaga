---
status: accepted
date: 2026-09-13
deciders: edouard
---

# ADR-136: Witt Bases and Four-Dimensional Rotor Lessons

## Context

The user requested teaching notebooks connecting non-orthogonal/null bases,
CGA/PGA orientation and duality, and the decomposition of a 4D rotor into
plane rotations. The supplied conversation conflated bivector simplicity
with a vanishing self-dual sector. We must demonstrate corrected statements
with the algebra, not reproduce an informal sign or branch convention.

## Decision

Add two maintained Python 3.14 Marimo lessons:

- `algebra/witt_bases_and_null_geometry.py`: one to three real Witt pairs,
  reciprocal and orthogonal bases, a moving receiver's Doppler shifts, a
  finite fermionic occupation-state model and matrices, and CGA versus PGA
  degeneracy and complements.
- `algebra/four_dimensional_rotor_planes.py`: Euclidean 4D double rotations,
  principal logarithms, invariant plane extraction, self-dual sectors,
  isoclinic nonuniqueness, and the metric-independent bivector simplicity test.

Keep construction and decomposition helpers local to the lessons.
No new preset, pseudoscalar sign field, general decomposition API or
production numerical algorithm is introduced. Witt Gram matrices use
$p_i\cdot q_j=\delta_{ij}$ in interleaved native order; basis names denote
native wedges, not geometric products. Ordinary CGA's negative null-pair
normalization is related explicitly by $p=e_o$, $q=-e_\infty$.
PGA's radical direction is not a hyperbolic/Witt pair.

The 4D extraction is restricted to an orthonormal real Euclidean algebra.
With $D=\operatorname{dual}(B)$, $S=-\langle B^2\rangle_0$,
$T=(B\wedge B)/I$ and $\Delta=\sqrt{S^2-T^2}$, extract
$B_1=((S+\Delta)B+TD)/(2\Delta)$ and $B_2=B-B_1$.
Derive the sign from the computed `dual(e12) == -e34` convention.
Do not apply the formula to other signatures or dimensions.

The zero generator and equal/near-equal plane magnitudes are explicit
non-extraction cases. The lesson uses a relative gap cutoff
$\Delta\leq10^{-6}S$, and $S\leq10^{-24}$ for numerical zero. It reports an
unresolved or nonunique pair, rather than assigning artificial planes.
Angles are bounded to $[-100^\circ,100^\circ]$ in each plane to stay inside
the principal-logarithm branch; every result is checked by exponentiation.
The notebook is an explanatory calculation, not a robustness guarantee for
arbitrary rotor logarithms.

For the stated Euclidean Hodge star, `star(B) = -dual(B)` on bivectors.
Simplicity means $B\wedge B=0$, equivalently equal metric norms of the two
self-dual sectors, not one sector vanishing. A nonzero single-sector
generator is isoclinic and nonsimple. Distinguish this sector splitting
from the pair of simple plane generators. The Plücker test is for
bivectors, includes zero as decomposable, and remains valid with a
degenerate metric; test the exterior coefficients, not a metric norm.

Keep controls beside the results they affect, at most two plots side by
side, and plotting helpers in an appendix. The 4D plots are labelled
coordinate projections. Limit the full Witt metric display to one pair.
Use existing Galaga rendering and matrix conversion; do not add plotting
dependencies or modify unrelated notebooks.

## Verification

Register both lessons in the executable gallery. Runtime tests cover all
Witt pair counts and positive/zero/negative boost parameters, native label
and determinant signs, reciprocal pairings, compact matrix identities, and
PGA's expected inverse-dual rejection.

### Application-led revision

The initial examples demonstrated algebraic identities without sufficiently
motivating their use. Frame the lesson around two explicit tasks. In the
first, compute frequencies of opposing laboratory light signals measured by
a moving observer. With the notebook's `R=exp(-eta*K/2)` convention, the
observer is `U=~R*u*R` and a frequency is `metric_inner_product(k,U)`;
`R*k*~R` instead gives signal components in the observer frame. Test both
routes against the signed longitudinal Doppler factors.

In the second, use `a_i=p_i/sqrt(2)` and `c_i=q_i/sqrt(2)` as annihilation
and creation operators. Construct the ideal vacuum and every ordered
occupation state, then derive matrices of left multiplication by solving
for coordinates in that basis. Check basis rank and closure. This is not a
hardcoded occupation matrix or a claim that the compact matrix conversion
uses this particular state basis.

Choose the positive inner product on occupation columns explicitly; creation
is matrix-adjoint to annihilation there, not Clifford reversion. Do not use
the indefinite Clifford pairing for quantum probabilities. Display creation,
annihilation and counting actions, forbidden transitions, fermionic signs and
independent-mode energies. The zero result is not the vacuum. Test every
basis action and the CAR for one to three modes, plus UI choices. This is a
real finite-mode operator example, not quantum time evolution or a
derivation of spin-statistics.

Rotation tests cover distinct, swapped, single-plane, zero, equal and
opposite angles; rotate the input planes before checking extraction to
exclude coordinate-specific logic. Test the near-isoclinic cutoff and
several alternate plane choices for the same isoclinic rotor.
Check plots against the computed sandwiches and rendered equations for
nested math delimiters or indented-code regressions.

The lessons link primary mathematical references and distinguish those
general results from the specific formulas verified locally. No release
metadata or CI changes are involved.
