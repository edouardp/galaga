"""Tests derived from Chisolm, "Geometric Algebra" (arXiv:1205.5935v1).

Section 5.5: Dual properties.
Section 5.6: Commutator properties.
Section 9.4: Skew-symmetric operators via bivectors.

Each test is named after the equation or theorem it verifies.
The docstring cites the exact reference in the paper.

Convention note — commutator product:
    Chisolm defines the commutator as  [A, B] := ½(AB − BA)  (Eq. 2.61).
    In galaga this is ``lie_bracket(A, B)``, NOT ``commutator(A, B)``.
    galaga's ``commutator(A, B)`` omits the ½ factor: it computes AB − BA.
    All tests in this file use ``lie_bracket`` to match the paper exactly.
"""

import numpy as np
import pytest

from galaga import (
    Algebra,
    Multivector,
    dual,
    gp,
    grade,
    inverse,
    involute,
    left_contraction,
    lie_bracket,
    op,
    right_contraction,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SIGNATURES = [
    (1, 1),
    (1, 1, 1),
    (1, -1, -1, -1),
]


@pytest.fixture(params=SIGNATURES, ids=["Cl2", "Cl3", "STA"])
def alg(request):
    return Algebra(request.param)


def _rvec(alg, rng):
    return alg.vector(rng.standard_normal(alg.n))


def _rmv(alg, rng):
    return Multivector(alg, rng.standard_normal(alg.dim))


def _rblade(alg, rng, r):
    if r == 0:
        return alg.scalar(rng.standard_normal())
    B = _rvec(alg, rng)
    for _ in range(r - 1):
        B = op(B, _rvec(alg, rng))
    return B


# ===========================================================================
# Section 5.5: Dual properties
# ===========================================================================

# ---------------------------------------------------------------------------
# After Eq. 2.56 — dual(AB) = A · dual(B)
# ---------------------------------------------------------------------------

class TestDualOfProduct:
    """After Eq. 2.56 (§5.5): dual(AB) = A · dual(B)."""

    def test_random(self, alg):
        """dual(AB) = A * dual(B) for random multivectors."""
        rng = np.random.default_rng(200)
        for _ in range(5):
            A = _rmv(alg, rng)
            B = _rmv(alg, rng)
            lhs = dual(gp(A, B))
            rhs = gp(A, dual(B))
            assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Eq. 2.58, 1st (label:dualprods) — dual(A ∧ B) = A ⌋ dual(B)
# ---------------------------------------------------------------------------

class TestEq258DualOfWedge:
    """Eq. 2.58, 1st (§5.5, label:dualprods): dual(A∧B) = A⌋dual(B)."""

    def test_vectors(self, alg):
        """dual(a∧b) = a⌋dual(b) for vectors."""
        rng = np.random.default_rng(201)
        for _ in range(5):
            a = _rvec(alg, rng)
            b = _rvec(alg, rng)
            lhs = dual(op(a, b))
            rhs = left_contraction(a, dual(b))
            assert np.allclose(lhs.data, rhs.data, atol=1e-10)

    def test_mixed_grades(self, alg):
        """dual(A∧B) = A⌋dual(B) for random multivectors."""
        rng = np.random.default_rng(202)
        for _ in range(5):
            A = _rmv(alg, rng)
            B = _rmv(alg, rng)
            lhs = dual(op(A, B))
            rhs = left_contraction(A, dual(B))
            assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Eq. 2.58, 2nd (label:dualprods) — dual(A ⌋ B) = A ∧ dual(B)
# ---------------------------------------------------------------------------

class TestEq258DualOfContraction:
    """Eq. 2.58, 2nd (§5.5, label:dualprods): dual(A⌋B) = A∧dual(B)."""

    def test_vector_into_bivector(self, alg):
        """dual(a⌋B₂) = a∧dual(B₂)."""
        if alg.n < 2:
            pytest.skip("Need n ≥ 2")
        rng = np.random.default_rng(203)
        for _ in range(5):
            a = _rvec(alg, rng)
            B = _rblade(alg, rng, 2)
            lhs = dual(left_contraction(a, B))
            rhs = op(a, dual(B))
            assert np.allclose(lhs.data, rhs.data, atol=1e-10)

    def test_mixed_grades(self, alg):
        """dual(A⌋B) = A∧dual(B) for random multivectors."""
        rng = np.random.default_rng(204)
        for _ in range(5):
            A = _rmv(alg, rng)
            B = _rmv(alg, rng)
            lhs = dual(left_contraction(A, B))
            rhs = op(A, dual(B))
            assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Eq. 2.54 (label:commuteI) — A·I = I·involute^{n-1}(A)
# ---------------------------------------------------------------------------

class TestEq254PseudoscalarCommutation:
    """Eq. 2.54 (§5.5, label:commuteI): A·I = I·involute^{n-1}(A)."""

    def test_random(self, alg):
        """Pseudoscalar commutation rule."""
        rng = np.random.default_rng(205)
        I = alg.pseudoscalar()
        for _ in range(5):
            A = _rmv(alg, rng)
            lhs = gp(A, I)
            # involute^{n-1} = involute if n-1 is odd, identity if n-1 is even
            A_inv = involute(A) if (alg.n - 1) % 2 == 1 else A
            rhs = gp(I, A_inv)
            assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Eq. 2.57 (label:AoutdualA) — A ∧ dual(A) ∝ I for invertible blades
# ---------------------------------------------------------------------------

class TestBladeWedgeDualProportionalToI:
    """Eq. 2.57 (§5.5, label:AoutdualA): A∧dual(A) = A²/I² · I for invertible blades."""

    def test_basis_blades(self, alg):
        """A∧dual(A) is proportional to I for each non-null basis blade."""
        I = alg.pseudoscalar()
        I2 = gp(I, I).scalar_part
        for k in range(1, alg.n):
            for B in alg.basis_blades(k):
                B2 = gp(B, B).scalar_part
                if abs(B2) < 1e-10:
                    continue
                result = op(B, dual(B))
                expected = (B2 / I2) * I
                assert np.allclose(result.data, expected.data, atol=1e-10)


# ===========================================================================
# Section 5.6: Commutator properties
#
# CONVENTION: Chisolm's "commutator" [A, B] := ½(AB − BA) includes a ½
# factor (Eq. 2.61). In galaga:
#   - lie_bracket(A, B)  = ½(AB − BA)   ← matches Chisolm, used here
#   - commutator(A, B)   =   AB − BA    ← twice Chisolm's convention
#   - jordan_product(A,B) = ½(AB + BA)  ← the symmetric counterpart
#   - anticommutator(A,B) =   AB + BA   ← twice jordan_product
# ===========================================================================

# ---------------------------------------------------------------------------
# Eq. 2.62 (label:commident) — [A, BC] = [A,B]C + B[A,C]  (Leibniz rule)
# Uses lie_bracket = ½(AB−BA), matching Chisolm's [A,B].
# ---------------------------------------------------------------------------

class TestEq262CommutatorLeibniz:
    """Eq. 2.62 (§5.6, label:commident): [A,BC] = [A,B]C + B[A,C].

    Uses galaga's lie_bracket (½(AB−BA)) which matches Chisolm's commutator.
    """

    def test_random(self, alg):
        """Commutator Leibniz rule for random multivectors."""
        rng = np.random.default_rng(210)
        for _ in range(5):
            A = _rmv(alg, rng)
            B = _rmv(alg, rng)
            C = _rmv(alg, rng)
            lhs = lie_bracket(A, gp(B, C))
            rhs = gp(lie_bracket(A, B), C) + gp(B, lie_bracket(A, C))
            assert np.allclose(lhs.data, rhs.data, atol=1e-9)


# ---------------------------------------------------------------------------
# After Eq. 2.62 — Jacobi identity:
# [A,[B,C]] + [B,[C,A]] + [C,[A,B]] = 0
# ---------------------------------------------------------------------------

class TestJacobiIdentity:
    """After Eq. 2.62 (§5.6): [A,[B,C]] + [B,[C,A]] + [C,[A,B]] = 0.

    Uses galaga's lie_bracket (½(AB−BA)) which matches Chisolm's commutator.
    """

    def test_random(self, alg):
        """Jacobi identity for random multivectors."""
        rng = np.random.default_rng(211)
        for _ in range(5):
            A = _rmv(alg, rng)
            B = _rmv(alg, rng)
            C = _rmv(alg, rng)
            t1 = lie_bracket(A, lie_bracket(B, C))
            t2 = lie_bracket(B, lie_bracket(C, A))
            t3 = lie_bracket(C, lie_bracket(A, B))
            result = t1 + t2 + t3
            assert np.allclose(result.data, 0, atol=1e-9)


# ---------------------------------------------------------------------------
# Theorem after Eq. 2.66 — [A₂, B_r] is grade r
# (bivector commutator preserves grade)
# ---------------------------------------------------------------------------

class TestBivectorCommutatorPreservesGrade:
    """Theorem after Eq. 2.66 (§5.6): [A₂, B_r] = ⟨A₂ B_r⟩_r.

    Uses galaga's lie_bracket (½(AB−BA)) which matches Chisolm's commutator.
    """

    def test_per_grade(self, alg):
        """Commutator of bivector with r-vector is an r-vector."""
        rng = np.random.default_rng(212)
        A2 = _rblade(alg, rng, 2)
        for r in range(alg.n + 1):
            Br = _rblade(alg, rng, r)
            comm = lie_bracket(A2, Br)
            for k in range(alg.n + 1):
                if k == r:
                    continue
                assert np.allclose(grade(comm, k).data, 0, atol=1e-10), (
                    f"[A₂, B_{r}] has nonzero grade-{k} component"
                )

    def test_equals_grade_r_of_product(self, alg):
        """[A₂, B_r] = ½⟨A₂ B_r - B_r A₂⟩_r = ⟨A₂ B_r⟩_r (since other grades cancel)."""
        rng = np.random.default_rng(213)
        A2 = _rblade(alg, rng, 2)
        for r in range(alg.n + 1):
            Br = _rblade(alg, rng, r)
            comm = lie_bracket(A2, Br)
            # lie_bracket = (A2*Br - Br*A2)/2, and the grade-r part of that
            # equals the grade-r part of A2*Br (since inner/outer parts cancel)
            expected = grade(gp(A2, Br), r)
            assert np.allclose(comm.data, expected.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Eq. 2.65 (label:commutewithvec) —
# [a, A] = a⌋A₊ + a∧A₋  (vector commutator decomposition)
# Uses lie_bracket = ½(aA−Aa), matching Chisolm's [a,A].
# ---------------------------------------------------------------------------

class TestEq265VectorCommutatorDecomposition:
    """Eq. 2.65 (§5.6, label:commutewithvec): [a,A] = a⌋A₊ + a∧A₋.

    Uses galaga's lie_bracket (½(AB−BA)) which matches Chisolm's commutator.
    """

    def test_random(self, alg):
        """Vector commutator decomposes into contraction of even + wedge of odd."""
        rng = np.random.default_rng(214)
        for _ in range(5):
            a = _rvec(alg, rng)
            A = _rmv(alg, rng)
            A_even = grade(A, "even")
            A_odd = grade(A, "odd")
            lhs = lie_bracket(a, A)
            rhs = left_contraction(a, A_even) + op(a, A_odd)
            assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Bivectors closed under commutation (Lie algebra)
# ---------------------------------------------------------------------------

class TestBivectorsClosedUnderCommutation:
    """§5.6: The set of bivectors is closed under commutation.

    Uses galaga's lie_bracket (½(AB−BA)) which matches Chisolm's commutator.
    """

    def test_bivector_commutator_is_bivector(self, alg):
        """[B₂, C₂] is a bivector."""
        if alg.n < 2:
            pytest.skip("Need n ≥ 2")
        rng = np.random.default_rng(215)
        for _ in range(5):
            B = _rblade(alg, rng, 2)
            C = _rblade(alg, rng, 2)
            comm = lie_bracket(B, C)
            for k in range(alg.n + 1):
                if k == 2:
                    continue
                assert np.allclose(grade(comm, k).data, 0, atol=1e-10)


# ===========================================================================
# Section 9.4: Skew-symmetric operators via bivectors
# ===========================================================================

# ---------------------------------------------------------------------------
# Theorem in §9.4 — F(a) = a⌋A₂ is skew: a·F(b) = -b·F(a)
# ---------------------------------------------------------------------------

class TestSkewSymmetricBivectorOperator:
    """Theorem in §9.4: F(a) = a⌋A₂ defines a skew-symmetric operator."""

    def test_antisymmetric_bilinear_form(self, alg):
        """a·(b⌋A₂) = -b·(a⌋A₂) for any bivector A₂."""
        if alg.n < 2:
            pytest.skip("Need n ≥ 2")
        rng = np.random.default_rng(220)
        A2 = _rblade(alg, rng, 2)
        for _ in range(5):
            a = _rvec(alg, rng)
            b = _rvec(alg, rng)
            lhs = gp(a, left_contraction(b, A2)).scalar_part
            rhs = -gp(b, left_contraction(a, A2)).scalar_part
            assert lhs == pytest.approx(rhs, abs=1e-10)

    def test_equals_wedge_contracted(self, alg):
        """a·(b⌋A₂) = (a∧b)⌋A₂ (the antisymmetric form)."""
        if alg.n < 2:
            pytest.skip("Need n ≥ 2")
        rng = np.random.default_rng(221)
        A2 = _rblade(alg, rng, 2)
        for _ in range(5):
            a = _rvec(alg, rng)
            b = _rvec(alg, rng)
            lhs = gp(a, left_contraction(b, A2)).scalar_part
            rhs = left_contraction(op(a, b), A2).scalar_part
            assert lhs == pytest.approx(rhs, abs=1e-10)

    def test_reconstruct_bivector(self, alg):
        """A₂ = ½ Σᵢ eⁱ∧F(eᵢ) reconstructs the bivector from the operator."""
        if alg.n < 2:
            pytest.skip("Need n ≥ 2")
        rng = np.random.default_rng(222)
        A2 = _rblade(alg, rng, 2)
        # Use orthonormal basis: eⁱ = eᵢ/eᵢ² for non-null, skip null
        vecs = alg.basis_vectors()
        reconstructed = alg.scalar(0.0)
        for i, ei in enumerate(vecs):
            ei2 = alg.signature[i]
            if ei2 == 0:
                continue
            ei_recip = ei / ei2
            F_ei = left_contraction(ei, A2)
            reconstructed = reconstructed + op(ei_recip, F_ei)
        reconstructed = 0.5 * reconstructed
        assert np.allclose(reconstructed.data, A2.data, atol=1e-10)
