"""Tests derived from Chisolm, "Geometric Algebra" (arXiv:1205.5935v1).
https://arxiv.org/abs/1205.5935

Section 5: Other operations — grade involution, reversion, Clifford
conjugation, scalar product, and their interrelations.

Each test is named after the equation or theorem it verifies.
The docstring cites the exact reference in the paper.
"""

import numpy as np
import pytest

from galaga import (
    Algebra,
    Multivector,
    conjugate,
    gp,
    grade,
    inverse,
    involute,
    left_contraction,
    norm2,
    op,
    reverse,
    right_contraction,
    scalar_product,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

SIGNATURES = [
    (1, 1),
    (1, 1, 1),
    (1, -1, -1, -1),
    (0, 1, 1, 1),
]


@pytest.fixture(params=SIGNATURES, ids=["Cl2", "Cl3", "STA", "PGA"])
def alg(request):
    return Algebra(request.param)


def _rvec(alg, rng):
    return alg.vector(rng.standard_normal(alg.n))


def _rmv(alg, rng):
    return Multivector(alg, rng.standard_normal(alg.dim))


def _rblade(alg, rng, r):
    if r == 0:
        return alg.scalar(rng.standard_normal())
    v = _rvec(alg, rng)
    B = v
    for _ in range(r - 1):
        B = op(B, _rvec(alg, rng))
    return B


# ---------------------------------------------------------------------------
# Eq. 2.2 (label:grinvr) — Grade involution: (A_r)* = (-1)^r A_r
# ---------------------------------------------------------------------------

class TestEq202GradeInvolution:
    """Eq. 2.2 (§5.1, label:grinvr): involute(A_r) = (-1)^r A_r."""

    def test_per_grade(self, alg):
        """Grade involution negates odd grades, preserves even grades."""
        rng = np.random.default_rng(70)
        A = _rmv(alg, rng)
        Astar = involute(A)
        for k in range(alg.n + 1):
            expected = (-1) ** k * grade(A, k)
            actual = grade(Astar, k)
            assert np.allclose(actual.data, expected.data, atol=1e-12)


# ---------------------------------------------------------------------------
# Double grade involution: A** = A
# ---------------------------------------------------------------------------

class TestDoubleGradeInvolution:
    """After Eq. 2.3 (§5.1): involute(involute(A)) = A."""

    def test_random(self, alg):
        """Double grade involution is identity."""
        rng = np.random.default_rng(71)
        A = _rmv(alg, rng)
        assert np.allclose(involute(involute(A)).data, A.data, atol=1e-12)


# ---------------------------------------------------------------------------
# Eq. 2.4 (label:evenoddfromgrinv) — Even/odd extraction via involution.
# ⟨A⟩₊ = ½(A + A*), ⟨A⟩₋ = ½(A - A*)
# ---------------------------------------------------------------------------

class TestEq204EvenOddExtraction:
    """Eq. 2.4 (§5.1, label:evenoddfromgrinv): ⟨A⟩± = ½(A ± Â)."""

    def test_even_odd(self, alg):
        """Even and odd parts via grade involution."""
        rng = np.random.default_rng(72)
        A = _rmv(alg, rng)
        Astar = involute(A)
        even_part = 0.5 * (A + Astar)
        odd_part = 0.5 * (A - Astar)
        assert np.allclose(even_part.data, grade(A, "even").data, atol=1e-12)
        assert np.allclose(odd_part.data, grade(A, "odd").data, atol=1e-12)


# ---------------------------------------------------------------------------
# Grade involution of product: (AB)* = A* B*
# ---------------------------------------------------------------------------

class TestGradeInvolutionProduct:
    """Eq. 2.1, 3rd rule (§5.1, label:grinvrules): involute(AB) = involute(A) involute(B)."""

    def test_random(self, alg):
        """Grade involution is an algebra homomorphism."""
        rng = np.random.default_rng(73)
        A = _rmv(alg, rng)
        B = _rmv(alg, rng)
        lhs = involute(gp(A, B))
        rhs = gp(involute(A), involute(B))
        assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Eq. 2.14 (label:revA) — Reversion: (A_r)† = (-1)^{r(r-1)/2} A_r
# ---------------------------------------------------------------------------

class TestEq214Reversion:
    """Eq. 2.14 (§5.2, label:revA): reverse(A_r) = (-1)^{r(r-1)/2} A_r."""

    def test_per_grade(self, alg):
        """Reversion sign pattern: +, +, -, -, +, +, -, -, ..."""
        rng = np.random.default_rng(74)
        A = _rmv(alg, rng)
        Arev = reverse(A)
        for k in range(alg.n + 1):
            sign = (-1) ** (k * (k - 1) // 2)
            expected = sign * grade(A, k)
            actual = grade(Arev, k)
            assert np.allclose(actual.data, expected.data, atol=1e-12)


# ---------------------------------------------------------------------------
# Double reversion: A†† = A
# ---------------------------------------------------------------------------

class TestDoubleReversion:
    """After Eq. 2.13 (§5.2, label:revrules): reverse(reverse(A)) = A."""

    def test_random(self, alg):
        """Double reversion is identity."""
        rng = np.random.default_rng(75)
        A = _rmv(alg, rng)
        assert np.allclose(reverse(reverse(A)).data, A.data, atol=1e-12)


# ---------------------------------------------------------------------------
# Eq. 2.12, 3rd rule (label:revrules) — (AB)† = B†A†
# ---------------------------------------------------------------------------

class TestEq212ReversionOfProduct:
    """Eq. 2.12, 3rd rule (§5.2, label:revrules): reverse(AB) = reverse(B) reverse(A)."""

    def test_random(self, alg):
        """Reversion is an anti-homomorphism."""
        rng = np.random.default_rng(76)
        A = _rmv(alg, rng)
        B = _rmv(alg, rng)
        lhs = reverse(gp(A, B))
        rhs = gp(reverse(B), reverse(A))
        assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Eq. 2.42 (label:clifconjA) — Clifford conjugation: A‡ = (-1)^{r(r+1)/2} A_r
# ---------------------------------------------------------------------------

class TestEq242CliffordConjugation:
    """Eq. 2.42 (§5.3, label:clifconjA): conjugate(A_r) = (-1)^{r(r+1)/2} A_r."""

    def test_per_grade(self, alg):
        """Clifford conjugation sign pattern: +, -, -, +, +, -, -, +, ..."""
        rng = np.random.default_rng(77)
        A = _rmv(alg, rng)
        Aconj = conjugate(A)
        for k in range(alg.n + 1):
            sign = (-1) ** (k * (k + 1) // 2)
            expected = sign * grade(A, k)
            actual = grade(Aconj, k)
            assert np.allclose(actual.data, expected.data, atol=1e-12)


# ---------------------------------------------------------------------------
# Clifford conjugation = involute(reverse(A))
# ---------------------------------------------------------------------------

class TestCliffordConjIsInvoluteReverse:
    """§5.3: conjugate(A) = involute(reverse(A))."""

    def test_random(self, alg):
        """Clifford conjugation equals grade involution composed with reversion."""
        rng = np.random.default_rng(78)
        A = _rmv(alg, rng)
        assert np.allclose(conjugate(A).data, involute(reverse(A)).data, atol=1e-12)


# ---------------------------------------------------------------------------
# Eq. 2.25 (label:inv) — ⟨AB⟩₀ = ⟨BA⟩₀
# ---------------------------------------------------------------------------

class TestEq225ScalarPartCommutes:
    """Eq. 2.25 (§5.2, label:inv): ⟨AB⟩₀ = ⟨BA⟩₀."""

    def test_random(self, alg):
        """Scalar part of product is symmetric."""
        rng = np.random.default_rng(79)
        A = _rmv(alg, rng)
        B = _rmv(alg, rng)
        lhs = grade(gp(A, B), 0).scalar_part
        rhs = grade(gp(B, A), 0).scalar_part
        assert lhs == pytest.approx(rhs, abs=1e-10)


# ---------------------------------------------------------------------------
# Eq. 2.26 (label:cyclic) — ⟨AB…CD⟩₀ = ⟨DAB…C⟩₀
# ---------------------------------------------------------------------------

class TestEq226CyclicScalarPart:
    """Eq. 2.26 (§5.2, label:cyclic): scalar part of product is cyclic."""

    def test_three_factors(self, alg):
        """⟨ABC⟩₀ = ⟨CAB⟩₀ = ⟨BCA⟩₀."""
        rng = np.random.default_rng(80)
        A = _rmv(alg, rng)
        B = _rmv(alg, rng)
        C = _rmv(alg, rng)
        abc = grade(gp(gp(A, B), C), 0).scalar_part
        cab = grade(gp(gp(C, A), B), 0).scalar_part
        bca = grade(gp(gp(B, C), A), 0).scalar_part
        assert abc == pytest.approx(cab, abs=1e-10)
        assert abc == pytest.approx(bca, abs=1e-10)


# ---------------------------------------------------------------------------
# Eq. 2.30 (label:revscprod) — Scalar product symmetry: A*B = B*A
# Note: library scalar_product is ⟨AB⟩₀, paper's is ⟨A†B⟩₀.
# We test the paper's definition: ⟨A†B⟩₀ = ⟨B†A⟩₀.
# ---------------------------------------------------------------------------

class TestEq230ScalarProductSymmetry:
    """Eq. 2.30 (§5.4, label:revscprod): ⟨A†B⟩₀ = ⟨B†A⟩₀."""

    def test_random(self, alg):
        """Paper's scalar product is symmetric."""
        rng = np.random.default_rng(81)
        A = _rmv(alg, rng)
        B = _rmv(alg, rng)
        lhs = grade(gp(reverse(A), B), 0).scalar_part
        rhs = grade(gp(reverse(B), A), 0).scalar_part
        assert lhs == pytest.approx(rhs, abs=1e-10)


# ---------------------------------------------------------------------------
# Eq. 2.29 (label:grinvscprod) — ⟨Â†B̂⟩₀ = ⟨A†B⟩₀
# ---------------------------------------------------------------------------

class TestEq229ScalarProductGradeInvolution:
    """Eq. 2.29 (§5.4, label:grinvscprod): ⟨Â†B̂⟩₀ = ⟨A†B⟩₀."""

    def test_random(self, alg):
        """Scalar product invariant under grade involution of both args."""
        rng = np.random.default_rng(82)
        A = _rmv(alg, rng)
        B = _rmv(alg, rng)
        lhs = grade(gp(reverse(A), B), 0).scalar_part
        rhs = grade(gp(reverse(involute(A)), involute(B)), 0).scalar_part
        assert lhs == pytest.approx(rhs, abs=1e-10)


# ---------------------------------------------------------------------------
# ⟨A_r B_s⟩₀ = 0 if r ≠ s (before Eq. 2.28, label:scalarproddecomp)
# ---------------------------------------------------------------------------

class TestScalarPartVanishesDifferentGrades:
    """Before Eq. 2.28 (§5.4, label:scalarproddecomp): ⟨A_r B_s⟩₀ = 0 if r ≠ s."""

    def test_different_grades(self, alg):
        """Scalar part of product of different-grade blades vanishes."""
        rng = np.random.default_rng(83)
        for r in range(min(alg.n, 3) + 1):
            for s in range(min(alg.n, 3) + 1):
                if r == s:
                    continue
                Ar = _rblade(alg, rng, r)
                Bs = _rblade(alg, rng, s)
                sp = grade(gp(Ar, Bs), 0).scalar_part
                assert sp == pytest.approx(0.0, abs=1e-10), (
                    f"⟨A_{r} B_{s}⟩₀ ≠ 0"
                )


# ---------------------------------------------------------------------------
# Eq. 2.22 (label:revex) — ⟨A_r B_s⟩_{r+s-2j} = (-1)^{rs-j} ⟨B_s A_r⟩_{r+s-2j}
# ---------------------------------------------------------------------------

class TestEq222ReversionExchange:
    """Eq. 2.22 (§5.2, label:revex): ⟨A_r B_s⟩_{r+s-2j} = (-1)^{rs-j} ⟨B_s A_r⟩_{r+s-2j}."""

    def test_random(self, alg):
        """Term-by-term sign relation between A_r B_s and B_s A_r."""
        rng = np.random.default_rng(84)
        for r in range(1, min(alg.n, 3) + 1):
            for s in range(1, min(alg.n, 3) + 1):
                Ar = _rblade(alg, rng, r)
                Bs = _rblade(alg, rng, s)
                AB = gp(Ar, Bs)
                BA = gp(Bs, Ar)
                for j in range(min(r, s) + 1):
                    k = r + s - 2 * j
                    if k > alg.n:
                        continue
                    sign = (-1) ** (r * s - j)
                    lhs = grade(AB, k)
                    rhs = sign * grade(BA, k)
                    assert np.allclose(lhs.data, rhs.data, atol=1e-10), (
                        f"Failed for r={r}, s={s}, j={j}"
                    )


# ---------------------------------------------------------------------------
# Eq. 2.20 (label:revprods) — Reversion of inner/outer products.
# (A⌋B)† = B†⌊A†,  (A∧B)† = B†∧A†
# ---------------------------------------------------------------------------

class TestEq220ReversionOfProducts:
    """Eq. 2.20 (§5.2, label:revprods): reversion distributes over inner/outer products."""

    def test_reversion_of_left_contraction(self, alg):
        """(A⌋B)† = B†⌊A†."""
        rng = np.random.default_rng(85)
        A = _rblade(alg, rng, 1)
        B = _rblade(alg, rng, 2)
        lhs = reverse(left_contraction(A, B))
        rhs = right_contraction(reverse(B), reverse(A))
        assert np.allclose(lhs.data, rhs.data, atol=1e-10)

    def test_reversion_of_outer_product(self, alg):
        """(A∧B)† = B†∧A†."""
        rng = np.random.default_rng(86)
        A = _rmv(alg, rng)
        B = _rmv(alg, rng)
        lhs = reverse(op(A, B))
        rhs = op(reverse(B), reverse(A))
        assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Theorem 14 / Eq. 2.35 (label:versorinv) — Versor inverse: A⁻¹ = A†/|A|²
# ---------------------------------------------------------------------------

class TestThm14VersorInverse:
    """Theorem 14 (§5.4, label:versorinv): A⁻¹ = A†/|A|² for versors."""

    def test_vector_inverse(self, alg):
        """Vector (1-versor) inverse via reverse/norm."""
        rng = np.random.default_rng(87)
        for _ in range(5):
            v = _rvec(alg, rng)
            n2 = norm2(v)
            if abs(n2) < 1e-10:
                continue
            v_inv_formula = reverse(v) / n2
            v_inv_library = inverse(v)
            assert np.allclose(v_inv_formula.data, v_inv_library.data, atol=1e-12)

    def test_rotor_inverse(self, alg):
        """Rotor (2-versor) inverse via reverse/norm."""
        if alg.n < 2:
            pytest.skip("Need n ≥ 2")
        vecs = alg.basis_vectors()
        # Find two non-null basis vectors
        nonnull = [v for v, s in zip(vecs, alg.signature) if s != 0]
        if len(nonnull) < 2:
            pytest.skip("Need 2 non-null basis vectors")
        R = gp(nonnull[0], nonnull[1])  # biversor
        n2 = norm2(R)
        if abs(n2) < 1e-10:
            pytest.skip("Null rotor")
        R_inv_formula = reverse(R) / n2
        product = gp(R, R_inv_formula)
        assert product.scalar_part == pytest.approx(1.0, abs=1e-12)


# ---------------------------------------------------------------------------
# After Theorem 14 (label:bladeinv) — Blade squared is scalar.
# ---------------------------------------------------------------------------

class TestBladeSquaredIsScalar:
    """After Theorem 14 (§5.4, label:bladeinv): A_r² is a scalar for any r-blade."""

    def test_basis_blades(self, alg):
        """Every basis blade squares to a scalar."""
        for k in range(alg.n + 1):
            for B in alg.basis_blades(k):
                B2 = gp(B, B)
                # All non-scalar components should vanish
                non_scalar = B2.data.copy()
                non_scalar[0] = 0
                assert np.allclose(non_scalar, 0, atol=1e-12), (
                    f"Grade-{k} basis blade squared is not scalar"
                )


# ---------------------------------------------------------------------------
# Theorem 13 (label:facversorfromscprod) — |AB|² = |A|²|B|² for versors.
# ---------------------------------------------------------------------------

class TestThm13VersorNormProduct:
    """Theorem 13 (§5.4, label:facversorfromscprod): |AB|² = |A|²|B|² for versors."""

    def test_vector_product(self, alg):
        """|ab|² = |a|²|b|² for vectors."""
        rng = np.random.default_rng(88)
        for _ in range(5):
            a = _rvec(alg, rng)
            b = _rvec(alg, rng)
            lhs = norm2(gp(a, b))
            rhs = norm2(a) * norm2(b)
            assert lhs == pytest.approx(rhs, abs=1e-10)
