"""Tests derived from Cohoe, "Rigorous Development of Geometric Algebra" (2024).
Source: geo.pdf (David Cohoe, September 18, 2024)

Identities that are new or differently stated compared to the existing
Chisolm test suite. Each test class cites the theorem number from the paper.
"""

import numpy as np
import pytest

from galaga import (
    Algebra,
    Multivector,
    gp,
    grade,
    involute,
    left_contraction,
    norm2,
    op,
    reverse,
    right_contraction,
    sandwich,
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
    B = _rvec(alg, rng)
    for _ in range(r - 1):
        B = op(B, _rvec(alg, rng))
    return B


def _rversor(alg, rng, k):
    """Product of k random vectors."""
    result = _rvec(alg, rng)
    for _ in range(k - 1):
        result = gp(result, _rvec(alg, rng))
    return result


# ---------------------------------------------------------------------------
# Thm 3.19 — Generalised anticommutator: aX - X*a = 2(a⌋X)
# ---------------------------------------------------------------------------


class TestThm319GeneralisedAnticommutator:
    """Thm 3.19: aX - involute(X)a = 2(a⌋X) for vector a, multivector X."""

    def test_random(self, alg):
        rng = np.random.default_rng(100)
        for _ in range(5):
            a = _rvec(alg, rng)
            X = _rmv(alg, rng)
            lhs = gp(a, X) - gp(involute(X), a)
            rhs = 2.0 * left_contraction(a, X)
            assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Thm 3.17 — Antisymmetry of iterated vector contractions:
#             a⌋(b⌋X) + b⌋(a⌋X) = 0
# ---------------------------------------------------------------------------


class TestThm317AntisymmetricIteratedContraction:
    """Thm 3.17: a⌋(b⌋X) + b⌋(a⌋X) = 0 for vectors a, b."""

    def test_random(self, alg):
        rng = np.random.default_rng(101)
        for _ in range(5):
            a = _rvec(alg, rng)
            b = _rvec(alg, rng)
            X = _rmv(alg, rng)
            lhs = left_contraction(a, left_contraction(b, X))
            rhs = left_contraction(b, left_contraction(a, X))
            assert np.allclose(lhs.data, -rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Thm 3.20 — Nilpotency: a⌋(a⌋X) = 0
# ---------------------------------------------------------------------------


class TestThm320VectorContractionNilpotent:
    """Thm 3.20: a⌋(a⌋X) = 0 for vector a, multivector X."""

    def test_random(self, alg):
        rng = np.random.default_rng(102)
        for _ in range(5):
            a = _rvec(alg, rng)
            X = _rmv(alg, rng)
            result = left_contraction(a, left_contraction(a, X))
            assert np.allclose(result.data, 0, atol=1e-10)


# ---------------------------------------------------------------------------
# Thm 3.18 — Grade involution and contraction: (a⌋X)* = -a⌋(X*)
# ---------------------------------------------------------------------------


class TestThm318InvoluteContraction:
    """Thm 3.18: involute(a⌋X) = -a⌋involute(X) for vector a."""

    def test_random(self, alg):
        rng = np.random.default_rng(103)
        for _ in range(5):
            a = _rvec(alg, rng)
            X = _rmv(alg, rng)
            lhs = involute(left_contraction(a, X))
            rhs = -1.0 * left_contraction(a, involute(X))
            assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Thm 3.15 — Vector contraction with scalar is zero: a⌋α = 0
# ---------------------------------------------------------------------------


class TestThm315ContractionWithScalar:
    """Thm 3.15: a⌋α = 0 for vector a, scalar α."""

    def test_random(self, alg):
        rng = np.random.default_rng(104)
        for _ in range(5):
            a = _rvec(alg, rng)
            s = alg.scalar(rng.standard_normal())
            result = left_contraction(a, s)
            assert np.allclose(result.data, 0, atol=1e-12)


# ---------------------------------------------------------------------------
# §5.2 — Contraction-involution identities
# ---------------------------------------------------------------------------


class TestSec52ContractionInvolutionIdentities:
    """§5.2: involution/reversion identities for contractions."""

    def test_involute_left_contraction(self, alg):
        """(A⌋B)* = A*⌋B*."""
        rng = np.random.default_rng(105)
        for _ in range(5):
            A = _rmv(alg, rng)
            B = _rmv(alg, rng)
            lhs = involute(left_contraction(A, B))
            rhs = left_contraction(involute(A), involute(B))
            assert np.allclose(lhs.data, rhs.data, atol=1e-10)

    def test_involute_right_contraction(self, alg):
        """(A⌊B)* = A*⌊B*."""
        rng = np.random.default_rng(106)
        for _ in range(5):
            A = _rmv(alg, rng)
            B = _rmv(alg, rng)
            lhs = involute(right_contraction(A, B))
            rhs = right_contraction(involute(A), involute(B))
            assert np.allclose(lhs.data, rhs.data, atol=1e-10)

    def test_reverse_left_contraction_swaps(self, alg):
        """(A⌋B)† = B†⌊A†."""
        rng = np.random.default_rng(107)
        for _ in range(5):
            A = _rmv(alg, rng)
            B = _rmv(alg, rng)
            lhs = reverse(left_contraction(A, B))
            rhs = right_contraction(reverse(B), reverse(A))
            assert np.allclose(lhs.data, rhs.data, atol=1e-10)

    def test_reverse_right_contraction_swaps(self, alg):
        """(A⌊B)† = B†⌋A†."""
        rng = np.random.default_rng(108)
        for _ in range(5):
            A = _rmv(alg, rng)
            B = _rmv(alg, rng)
            lhs = reverse(right_contraction(A, B))
            rhs = left_contraction(reverse(B), reverse(A))
            assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Thm 4.11 — Scalar part invariant under reverse: ⟨A†⟩ = ⟨A⟩
# ---------------------------------------------------------------------------


class TestThm411ScalarPartInvariantUnderReverse:
    """Thm 4.11: ⟨A†⟩ = ⟨A⟩."""

    def test_random(self, alg):
        rng = np.random.default_rng(109)
        for _ in range(5):
            A = _rmv(alg, rng)
            assert grade(reverse(A), 0).scalar_part == pytest.approx(grade(A, 0).scalar_part, abs=1e-12)


# ---------------------------------------------------------------------------
# Thm 4.9/4.10 — Grade projection commutes with involutions
# ---------------------------------------------------------------------------


class TestThm49GradeProjectionCommutesWithInvolutions:
    """Thm 4.9: ⟨X⟩_n* = ⟨X*⟩_n.  Thm 4.10: ⟨X⟩_n† = ⟨X†⟩_n."""

    def test_involute(self, alg):
        rng = np.random.default_rng(110)
        A = _rmv(alg, rng)
        for k in range(alg.n + 1):
            lhs = involute(grade(A, k))
            rhs = grade(involute(A), k)
            assert np.allclose(lhs.data, rhs.data, atol=1e-12)

    def test_reverse(self, alg):
        rng = np.random.default_rng(111)
        A = _rmv(alg, rng)
        for k in range(alg.n + 1):
            lhs = reverse(grade(A, k))
            rhs = grade(reverse(A), k)
            assert np.allclose(lhs.data, rhs.data, atol=1e-12)


# ---------------------------------------------------------------------------
# Thm 4.12 — Grade projection commutes with vector contraction:
#             ⟨a⌋X⟩_n = a⌋⟨X⟩_{n+1}
# ---------------------------------------------------------------------------


class TestThm412GradeProjectionCommuteWithContraction:
    """Thm 4.12: ⟨a⌋X⟩_n = a⌋⟨X⟩_{n+1} for vector a."""

    def test_random(self, alg):
        rng = np.random.default_rng(112)
        for _ in range(5):
            a = _rvec(alg, rng)
            X = _rmv(alg, rng)
            for n in range(alg.n):
                lhs = grade(left_contraction(a, X), n)
                rhs = left_contraction(a, grade(X, n + 1))
                assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Thm 5.2 — ⟨aX⟩_{n-1} = a⌋X for vector a and n-vector X
# ---------------------------------------------------------------------------


class TestThm52VectorContractionViaGradeProjection:
    """Thm 5.2: ⟨aX⟩_{n-1} = a⌋X for vector a and n-vector X."""

    def test_random(self, alg):
        rng = np.random.default_rng(113)
        for _ in range(3):
            a = _rvec(alg, rng)
            for n in range(1, alg.n + 1):
                X = _rblade(alg, rng, n)
                lhs = grade(gp(a, X), n - 1)
                rhs = left_contraction(a, X)
                assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Thm 5.6 (second form) — Xv = X⌊v + X∧v
# ---------------------------------------------------------------------------


class TestThm56RightProductDecomposition:
    """Thm 5.6: Xv = X⌊v + X∧v."""

    def test_random(self, alg):
        rng = np.random.default_rng(114)
        for _ in range(5):
            X = _rmv(alg, rng)
            v = _rvec(alg, rng)
            lhs = gp(X, v)
            rhs = right_contraction(X, v) + op(X, v)
            assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# §5.2 — All vector inner products agree: a⌋b = a⌊b = B(a,b)
# ---------------------------------------------------------------------------


class TestSec52VectorInnerProductsAgree:
    """§5.2: a⌋b = a⌊b = B(a,b) for vectors a, b."""

    def test_random(self, alg):
        rng = np.random.default_rng(115)
        for _ in range(5):
            a = _rvec(alg, rng)
            b = _rvec(alg, rng)
            lc = left_contraction(a, b)
            rc = right_contraction(a, b)
            assert np.allclose(lc.data, rc.data, atol=1e-12)
            # Both should be scalar = sum(a_i * b_i * sig_i)
            expected = sum(a.data[1 << i] * b.data[1 << i] * alg.signature[i] for i in range(alg.n))
            assert lc.scalar_part == pytest.approx(expected, abs=1e-12)


# ---------------------------------------------------------------------------
# Thm 5.3 — Scalar product vanishes for different grades
# ---------------------------------------------------------------------------


class TestThm53ScalarProductDifferentGrades:
    """Thm 5.3: ⟨A_r B_s⟩ = 0 when r ≠ s."""

    def test_random(self, alg):
        rng = np.random.default_rng(116)
        for r in range(min(alg.n, 3) + 1):
            for s in range(min(alg.n, 3) + 1):
                if r == s:
                    continue
                A = _rblade(alg, rng, r)
                B = _rblade(alg, rng, s)
                assert scalar_product(A, B) == pytest.approx(0, abs=1e-10)


# ---------------------------------------------------------------------------
# Thm 5.4 — Scalar product symmetry: A*B = B*A
# ---------------------------------------------------------------------------


class TestThm54ScalarProductSymmetry:
    """Thm 5.4: scalar_product(A, B) = scalar_product(B, A)."""

    def test_random(self, alg):
        rng = np.random.default_rng(117)
        for _ in range(5):
            A = _rmv(alg, rng)
            B = _rmv(alg, rng)
            assert scalar_product(A, B) == pytest.approx(scalar_product(B, A), abs=1e-10)


# ---------------------------------------------------------------------------
# Thm 5.5 — Norm squared invariant under reverse: |A†|² = |A|²
# ---------------------------------------------------------------------------


class TestThm55NormInvariantUnderReverse:
    """Thm 5.5: |A†|² = |A|²."""

    def test_random(self, alg):
        rng = np.random.default_rng(118)
        for _ in range(5):
            A = _rmv(alg, rng)
            assert norm2(reverse(A)) == pytest.approx(norm2(A), abs=1e-10)


# ---------------------------------------------------------------------------
# Thm 6.2 — Versor norm identity: A†A = AA† = |A|²
# ---------------------------------------------------------------------------


class TestThm62VersorNormIdentity:
    """Thm 6.2: A†A = AA† = |A|² for versors (products of vectors)."""

    def test_random_versors(self, alg):
        rng = np.random.default_rng(119)
        for k in range(1, min(alg.n, 4) + 1):
            for _ in range(3):
                V = _rversor(alg, rng, k)
                Vr = reverse(V)
                lhs1 = gp(Vr, V)
                lhs2 = gp(V, Vr)
                n2 = norm2(V)
                expected = alg.scalar(n2)
                assert np.allclose(lhs1.data, expected.data, atol=1e-9)
                assert np.allclose(lhs2.data, expected.data, atol=1e-9)


# ---------------------------------------------------------------------------
# Thm 6.4 — Sandwich distributes over outer product:
#            sandwich(A,X) ∧ sandwich(A,Y) = |A|² sandwich(A, X∧Y)
# ---------------------------------------------------------------------------


class TestThm64SandwichDistributesOverWedge:
    """Thm 6.4: (A†XA)∧(A†YA) = |A|² A†(X∧Y)A for versors."""

    def test_random_versors(self, alg):
        rng = np.random.default_rng(120)
        for k in range(1, min(alg.n, 3) + 1):
            for _ in range(3):
                A = _rversor(alg, rng, k)
                n2 = norm2(A)
                if abs(n2) < 1e-10:
                    continue
                X = _rvec(alg, rng)
                Y = _rvec(alg, rng)
                sX = sandwich(A, X)
                sY = sandwich(A, Y)
                lhs = op(sX, sY)
                rhs = n2 * sandwich(A, op(X, Y))
                assert np.allclose(lhs.data, rhs.data, atol=1e-8)
