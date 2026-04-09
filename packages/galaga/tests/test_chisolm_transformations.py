"""Tests derived from Chisolm, "Geometric Algebra" (arXiv:1205.5935v1).
https://arxiv.org/abs/1205.5935

Section 7: Projections, reflections, and rotations.
Section 6: Euclidean space specializations (Cl(2,0), Cl(3,0)).

Each test is named after the theorem or equation it verifies.
The docstring cites the exact reference in the paper.
"""

import numpy as np
import pytest

from galaga import (
    Algebra,
    dual,
    exp,
    gp,
    grade,
    inverse,
    involute,
    is_vector,
    left_contraction,
    norm2,
    op,
    project,
    reflect,
    reject,
    reverse,
    sandwich,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def cl2():
    return Algebra(2)


@pytest.fixture
def cl3():
    return Algebra(3)


@pytest.fixture
def sta():
    return Algebra(1, 3)


EUCLIDEAN_SIGS = [(1, 1), (1, 1, 1)]


@pytest.fixture(params=EUCLIDEAN_SIGS, ids=["Cl2", "Cl3"])
def eucl(request):
    return Algebra(request.param)


def _rvec(alg, rng):
    return alg.vector(rng.standard_normal(alg.n))


def _rblade(alg, rng, r):
    if r == 0:
        return alg.scalar(rng.standard_normal())
    v = _rvec(alg, rng)
    B = v
    for _ in range(r - 1):
        B = op(B, _rvec(alg, rng))
    return B


# ===========================================================================
# Section 7.1: Projections and rejections
# ===========================================================================

# ---------------------------------------------------------------------------
# Theorem 15 (§7.1, label:vectorprojrej) — P_A(a) + R_A(a) = a
# ---------------------------------------------------------------------------

class TestThm15ProjPlusRejEqualsOriginal:
    """Theorem 15 (§7.1, label:vectorprojrej): P_A(a) + R_A(a) = a."""

    def test_vector_onto_blade(self, eucl):
        """Projection + rejection recovers the original vector."""
        rng = np.random.default_rng(100)
        for r in range(1, eucl.n + 1):
            a = _rvec(eucl, rng)
            B = _rblade(eucl, rng, r)
            if abs(norm2(B)) < 1e-10:
                continue
            p = project(a, B)
            rej = reject(a, B)
            assert np.allclose((p + rej).data, a.data, atol=1e-10)


# ---------------------------------------------------------------------------
# After Theorem 15 — P_A(a) ∧ A = 0 (projection lies in subspace).
# ---------------------------------------------------------------------------

class TestProjectionLiesInSubspace:
    """After Theorem 15 (§7.1): P_A(a) ∧ A = 0."""

    def test_vector_projection(self, eucl):
        """Projection of a vector into a blade wedges to zero with that blade."""
        rng = np.random.default_rng(101)
        for r in range(1, eucl.n + 1):
            a = _rvec(eucl, rng)
            B = _rblade(eucl, rng, r)
            if abs(norm2(B)) < 1e-10:
                continue
            p = project(a, B)
            assert np.allclose(op(p, B).data, 0, atol=1e-10)


# ---------------------------------------------------------------------------
# After Theorem 15 — R_A(a) ⌋ A = 0 (rejection is orthogonal).
# ---------------------------------------------------------------------------

class TestRejectionIsOrthogonal:
    """After Theorem 15 (§7.1): R_A(a) ⌋ A = 0."""

    def test_vector_rejection(self, eucl):
        """Rejection of a vector from a blade contracts to zero with that blade."""
        rng = np.random.default_rng(102)
        for r in range(1, eucl.n + 1):
            a = _rvec(eucl, rng)
            B = _rblade(eucl, rng, r)
            if abs(norm2(B)) < 1e-10:
                continue
            rej = reject(a, B)
            assert np.allclose(left_contraction(rej, B).data, 0, atol=1e-10)


# ===========================================================================
# Section 7.2: Reflections
# ===========================================================================

# ---------------------------------------------------------------------------
# Eq. 3.22 (label:refinnerprod) — Reflection preserves inner product.
# ---------------------------------------------------------------------------

class TestEq322ReflectionPreservesInnerProduct:
    """Eq. 3.22 (§7.2, label:refinnerprod): a'·b' = a·b under reflection."""

    def test_vector_reflection(self, eucl):
        """Reflecting two vectors preserves their inner product."""
        rng = np.random.default_rng(103)
        for _ in range(5):
            a = _rvec(eucl, rng)
            b = _rvec(eucl, rng)
            n = _rvec(eucl, rng)
            if abs(norm2(n)) < 1e-10:
                continue
            a_ref = reflect(a, n)
            b_ref = reflect(b, n)
            ip_orig = gp(a, b).scalar_part
            ip_ref = gp(a_ref, b_ref).scalar_part
            assert ip_orig == pytest.approx(ip_ref, abs=1e-10)


# ---------------------------------------------------------------------------
# Eq. 1.28 (label:refdef) — Reflection formula: v' = -nvn⁻¹
# ---------------------------------------------------------------------------

class TestEq128ReflectionFormula:
    """Eq. 1.28 (§1.1, label:refdef): v' = -nvn⁻¹."""

    def test_matches_library(self, eucl):
        """Library reflect() matches the sandwich formula."""
        rng = np.random.default_rng(104)
        for _ in range(5):
            v = _rvec(eucl, rng)
            n = _rvec(eucl, rng)
            if abs(norm2(n)) < 1e-10:
                continue
            lib_result = reflect(v, n)
            manual = gp(gp(-n, v), inverse(n))
            assert np.allclose(lib_result.data, manual.data, atol=1e-12)

    def test_result_is_vector(self, eucl):
        """Reflection of a vector is a vector."""
        rng = np.random.default_rng(105)
        v = _rvec(eucl, rng)
        n = _rvec(eucl, rng)
        if abs(norm2(n)) < 1e-10:
            return
        assert is_vector(reflect(v, n))


# ---------------------------------------------------------------------------
# Eq. 3.24 (label:refainAr) — Reflection in subspace: v' = (-1)^r A_r v A_r⁻¹
# ---------------------------------------------------------------------------

class TestEq324ReflectionInSubspace:
    """Eq. 3.24 (§7.2.1, label:refainAr): v' = (-1)^r A_r v A_r⁻¹."""

    def test_reflection_in_plane(self, cl3):
        """Reflection of a vector in a bivector (plane) in Cl(3,0)."""
        rng = np.random.default_rng(106)
        v = _rvec(cl3, rng)
        B = _rblade(cl3, rng, 2)
        if abs(norm2(B)) < 1e-10:
            return
        # (-1)^2 = 1, so v' = B v B⁻¹
        v_ref = gp(gp(B, v), inverse(B))
        # Should be a vector
        assert is_vector(v_ref)
        # Projection into B should flip sign, rejection should stay
        p = project(v, B)
        rej = reject(v, B)
        expected = -p + rej
        assert np.allclose(v_ref.data, expected.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Eq. 3.28 (label:reflectI) — Reflection of I: I' = (-1)^r I
# ---------------------------------------------------------------------------

class TestEq328ReflectionOfPseudoscalar:
    """Eq. 3.28 (§7.2.2, label:reflectI): reflection of I in A_r gives (-1)^r I."""

    def test_reflect_I_in_vector(self, cl3):
        """Reflecting I in a vector: I' = -I (r=1)."""
        e1, _, _ = cl3.basis_vectors()
        I = cl3.pseudoscalar()
        I_ref = gp(gp(-e1, I), inverse(e1))
        assert np.allclose(I_ref.data, (-I).data, atol=1e-12)

    def test_reflect_I_in_bivector(self, cl3):
        """Reflecting I in a bivector: I' = I (r=2)."""
        e1, e2, _ = cl3.basis_vectors()
        B = op(e1, e2)
        I = cl3.pseudoscalar()
        # (-1)^2 = 1, so I' = B I B⁻¹
        I_ref = gp(gp(B, I), inverse(B))
        assert np.allclose(I_ref.data, I.data, atol=1e-12)


# ===========================================================================
# Section 7.3: Rotations
# ===========================================================================

# ---------------------------------------------------------------------------
# Eq. 3.30 (label:generalrot) — Rotation: A' = R A R⁻¹
# ---------------------------------------------------------------------------

class TestEq330RotationFormula:
    """Eq. 3.30 (§7.3, label:generalrot): A' = R A R⁻¹."""

    def test_rotation_preserves_inner_product(self, eucl):
        """Rotation preserves inner product of vectors."""
        if eucl.n < 2:
            pytest.skip("Need n ≥ 2")
        rng = np.random.default_rng(107)
        vecs = eucl.basis_vectors()
        B = op(vecs[0], vecs[1])
        R = exp(-0.3 * B)
        a = _rvec(eucl, rng)
        b = _rvec(eucl, rng)
        a_rot = sandwich(R, a)
        b_rot = sandwich(R, b)
        assert gp(a, b).scalar_part == pytest.approx(
            gp(a_rot, b_rot).scalar_part, abs=1e-10
        )

    def test_rotation_preserves_grade(self, eucl):
        """Rotation of a vector is a vector."""
        if eucl.n < 2:
            pytest.skip("Need n ≥ 2")
        vecs = eucl.basis_vectors()
        B = op(vecs[0], vecs[1])
        R = exp(-0.5 * B)
        v = _rvec(eucl, np.random.default_rng(108))
        assert is_vector(sandwich(R, v))

    def test_rotation_of_bivector(self, cl3):
        """Rotation of a bivector is a bivector (grade-preserving)."""
        e1, e2, e3 = cl3.basis_vectors()
        B_plane = op(e1, e2)
        R = exp(-0.4 * B_plane)
        B_target = op(e1, e3)
        rotated = sandwich(R, B_target)
        # Should be pure grade-2
        for k in range(cl3.n + 1):
            if k == 2:
                continue
            assert np.allclose(grade(rotated, k).data, 0, atol=1e-10)


# ---------------------------------------------------------------------------
# After Eq. 3.30 — R I R⁻¹ = I (rotation leaves pseudoscalar alone).
# ---------------------------------------------------------------------------

class TestRotationLeavesIAlone:
    """After Eq. 3.30 (§7.3): R I R⁻¹ = I."""

    def test_pseudoscalar_invariant(self, eucl):
        """Pseudoscalar is invariant under rotation."""
        if eucl.n < 2:
            pytest.skip("Need n ≥ 2")
        vecs = eucl.basis_vectors()
        B = op(vecs[0], vecs[1])
        R = exp(-0.7 * B)
        I = eucl.pseudoscalar()
        assert np.allclose(sandwich(R, I).data, I.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Eq. 1.30 (§1.1) — Rotor: R = exp(-Bθ/2), R R† = 1 for unit rotor.
# ---------------------------------------------------------------------------

class TestRotorProperties:
    """Eq. 1.30 (§1.1): R = exp(-Bθ/2), and R~R = 1 for unit bivector B."""

    def test_unit_rotor_norm(self, eucl):
        """exp(-Bθ/2) satisfies R~R = 1 when B is a unit bivector."""
        if eucl.n < 2:
            pytest.skip("Need n ≥ 2")
        vecs = eucl.basis_vectors()
        B = op(vecs[0], vecs[1])  # unit bivector in Euclidean space
        for theta in [0.0, 0.5, 1.0, np.pi, 2 * np.pi]:
            R = exp(-theta / 2 * B)
            RRt = gp(R, reverse(R))
            assert RRt.scalar_part == pytest.approx(1.0, abs=1e-10)
            # Non-scalar parts should vanish
            non_scalar = RRt.data.copy()
            non_scalar[0] = 0
            assert np.allclose(non_scalar, 0, atol=1e-10)

    def test_double_reflection_is_rotation(self, eucl):
        """Two reflections = one rotation (Hamilton's theorem)."""
        if eucl.n < 2:
            pytest.skip("Need n ≥ 2")
        rng = np.random.default_rng(109)
        vecs = eucl.basis_vectors()
        n = vecs[0]  # first reflection axis
        m = vecs[1]  # second reflection axis
        v = _rvec(eucl, rng)
        # Two reflections
        v1 = reflect(v, n)
        v2 = reflect(v1, m)
        # Equivalent rotation: R = mn
        R = gp(m, n)
        v_rot = gp(gp(R, v), inverse(R))
        assert np.allclose(v2.data, v_rot.data, atol=1e-10)


# ===========================================================================
# Section 6: Euclidean space specializations
# ===========================================================================

# ---------------------------------------------------------------------------
# §6.1 — Complex number structure in Cl(2,0): (e₁e₂)² = -1
# ---------------------------------------------------------------------------

class TestCl2ComplexStructure:
    """§6.1: The bivector e₁₂ in Cl(2,0) satisfies e₁₂² = -1."""

    def test_pseudoscalar_squares_to_minus_one(self, cl2):
        """(e₁e₂)² = -1 in Cl(2,0)."""
        e1, e2 = cl2.basis_vectors()
        I = gp(e1, e2)
        I2 = gp(I, I)
        assert I2.scalar_part == pytest.approx(-1.0)
        assert np.allclose(I2.data[1:], 0, atol=1e-12)


# ---------------------------------------------------------------------------
# §6.2 — Quaternion structure in Cl(3,0).
# ---------------------------------------------------------------------------

class TestCl3QuaternionStructure:
    """§6.2: Bivectors in Cl(3,0) satisfy quaternion relations."""

    def test_bivector_squares(self, cl3):
        """(eᵢeⱼ)² = -1 for all basis bivectors in Cl(3,0)."""
        e1, e2, e3 = cl3.basis_vectors()
        for B in [gp(e1, e2), gp(e2, e3), gp(e1, e3)]:
            B2 = gp(B, B)
            assert B2.scalar_part == pytest.approx(-1.0)
            assert np.allclose(B2.data[1:], 0, atol=1e-12)

    def test_quaternion_product(self, cl3):
        """e₁₂ · e₂₃ = e₁₃ (up to sign) — quaternion-like multiplication."""
        e1, e2, e3 = cl3.basis_vectors()
        e12 = gp(e1, e2)
        e23 = gp(e2, e3)
        e13 = gp(e1, e3)
        product = gp(e12, e23)
        # e12 * e23 = e1 e2 e2 e3 = e1 e3 = e13
        assert np.allclose(product.data, e13.data, atol=1e-12)


# ---------------------------------------------------------------------------
# §6.2 — Cross product via duality: a×b = -(a∧b)I⁻¹ in 3D.
# ---------------------------------------------------------------------------

class TestCl3CrossProductDuality:
    """§6.2 (label:crossprod): a×b = dual(a∧b) = (a∧b)I⁻¹ in Cl(3,0).

    Chisolm defines dual(A) = A·I⁻¹ (Eq. 2.56, label:dualdef), so
    a×b = (a∧b)I⁻¹. This is equivalent to Wikipedia's a×b = -I(a∧b)
    since I⁻¹ = -I when I² = -1 and I commutes with all elements in 3D.
    """

    def test_basis_cross_products(self, cl3):
        """e₁×e₂ = e₃, etc., via the duality formula."""
        e1, e2, e3 = cl3.basis_vectors()
        I_inv = inverse(cl3.pseudoscalar())
        # e1 × e2 = e3
        cross = gp(op(e1, e2), I_inv)
        assert np.allclose(cross.data, e3.data, atol=1e-12)
        # e2 × e3 = e1
        cross = gp(op(e2, e3), I_inv)
        assert np.allclose(cross.data, e1.data, atol=1e-12)
        # e3 × e1 = e2
        cross = gp(op(e3, e1), I_inv)
        assert np.allclose(cross.data, e2.data, atol=1e-12)

    def test_random_cross_product(self, cl3):
        """Random cross product via duality matches component formula."""
        rng = np.random.default_rng(110)
        a = _rvec(cl3, rng)
        b = _rvec(cl3, rng)
        I_inv = inverse(cl3.pseudoscalar())
        ga_cross = gp(op(a, b), I_inv)
        # Extract components for numpy cross product
        ac = [a.data[1], a.data[2], a.data[4]]
        bc = [b.data[1], b.data[2], b.data[4]]
        np_cross = np.cross(ac, bc)
        assert ga_cross.data[1] == pytest.approx(np_cross[0], abs=1e-10)
        assert ga_cross.data[2] == pytest.approx(np_cross[1], abs=1e-10)
        assert ga_cross.data[4] == pytest.approx(np_cross[2], abs=1e-10)


# ===========================================================================
# Section 9.5.2: Hyperbolic rotors (boosts) in STA
#
# Chisolm §9.5.2 (label:rotors): In a plane where B² = +1 (indefinite
# inner product), the biversor ab = ±exp(-Bφ/2) where the exponential
# uses cosh/sinh instead of cos/sin. In STA Cl(1,3), a timelike-spacelike
# bivector plane has B² = +1, and the resulting rotor is a Lorentz boost.
# ===========================================================================


class TestHyperbolicRotorSTA:
    """§9.5.2 (label:rotors): Hyperbolic rotors (boosts) in Cl(1,3).

    When B² = +1 (timelike bivector plane), exp(B) uses cosh/sinh:
        exp(-Bφ/2) = cosh(φ/2) - B sinh(φ/2)
    and the sandwich product RvR⁻¹ preserves the Minkowski inner product.
    """

    @pytest.fixture
    def sta(self):
        return Algebra(1, 3)

    def test_timelike_bivector_squares_positive(self, sta):
        """A time-space bivector B = γ₀γ₁ satisfies B² = +1 in Cl(1,3)."""
        g0, g1, _, _ = sta.basis_vectors()
        B = gp(g0, g1)
        B2 = gp(B, B).scalar_part
        assert B2 == pytest.approx(1.0)

    def test_boost_rotor_form(self, sta):
        """exp(-Bφ/2) = cosh(φ/2) - B sinh(φ/2) for timelike B."""
        g0, g1, _, _ = sta.basis_vectors()
        B = op(g0, g1)  # B² = +1
        for phi in [0.0, 0.5, 1.0, 2.0]:
            R = exp(-phi / 2 * B)
            expected = sta.scalar(np.cosh(phi / 2)) - np.sinh(phi / 2) * B
            assert np.allclose(R.data, expected.data, atol=1e-12)

    def test_boost_rotor_norm(self, sta):
        """Boost rotor satisfies R~R = 1."""
        g0, g1, _, _ = sta.basis_vectors()
        B = op(g0, g1)
        for phi in [0.0, 0.5, 1.0, 2.0]:
            R = exp(-phi / 2 * B)
            RRt = gp(R, reverse(R))
            assert RRt.scalar_part == pytest.approx(1.0, abs=1e-12)
            non_scalar = RRt.data.copy()
            non_scalar[0] = 0
            assert np.allclose(non_scalar, 0, atol=1e-12)

    def test_boost_preserves_minkowski_inner_product(self, sta):
        """Boosted vectors preserve the Minkowski inner product: a'·b' = a·b."""
        g0, g1, _, _ = sta.basis_vectors()
        B = op(g0, g1)
        R = exp(-0.7 * B)
        rng = np.random.default_rng(300)
        for _ in range(5):
            a = _rvec(sta, rng)
            b = _rvec(sta, rng)
            a_boost = sandwich(R, a)
            b_boost = sandwich(R, b)
            ip_orig = gp(a, b).scalar_part
            ip_boost = gp(a_boost, b_boost).scalar_part
            assert ip_orig == pytest.approx(ip_boost, abs=1e-10)

    def test_boost_preserves_grade(self, sta):
        """Boosted vector is still a vector."""
        g0, g1, _, _ = sta.basis_vectors()
        B = op(g0, g1)
        R = exp(-0.5 * B)
        rng = np.random.default_rng(301)
        v = _rvec(sta, rng)
        v_boost = sandwich(R, v)
        assert is_vector(v_boost)

    def test_boost_of_timelike_basis(self, sta):
        """Boosting γ₀ along γ₁: γ₀' = cosh(φ)γ₀ + sinh(φ)γ₁."""
        g0, g1, _, _ = sta.basis_vectors()
        B = op(g0, g1)
        phi = 0.8
        R = exp(-phi / 2 * B)
        g0_boost = sandwich(R, g0)
        expected = np.cosh(phi) * g0 + np.sinh(phi) * g1
        assert np.allclose(g0_boost.data, expected.data, atol=1e-10)

    def test_euclidean_vs_hyperbolic_bivector(self, sta):
        """Spacelike bivector B = γ₁γ₂ has B² = -1 (Euclidean rotation)."""
        _, g1, g2, _ = sta.basis_vectors()
        B = gp(g1, g2)
        B2 = gp(B, B).scalar_part
        # γ₁² = -1, γ₂² = -1, so (γ₁γ₂)² = -γ₁γ₂γ₁γ₂ = -(-1)(-1) = -1
        assert B2 == pytest.approx(-1.0)
