"""Tests derived from Chisolm, "Geometric Algebra" (arXiv:1205.5935v1).
https://arxiv.org/abs/1205.5935

Section 4: The inner, outer, and geometric products.

Each test is named after the theorem or equation it verifies.
The docstring cites the exact reference in the paper.
"""

import numpy as np
import pytest

from galaga.core import (
    Algebra,
    geometric_product,
    grade,
    grade_involution,
    left_contraction,
    outer_product,
    right_contraction,
    scalar_product,
)

# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

ALGEBRA_CONFIGS = [
    {"signature": (1, 1)},
    {"signature": (1, 1, 1)},
    {"signature": (1, -1, -1, -1)},
    {"signature": (0, 1, 1, 1)},
    {
        "gram": np.array(
            [
                [2.0, 0.5, 0.0],
                [0.5, 1.0, 0.25],
                [0.0, 0.25, 1.5],
            ]
        )
    },
]


@pytest.fixture(
    params=ALGEBRA_CONFIGS,
    ids=["Cl2", "Cl3", "STA", "PGA", "oblique-positive-definite"],
)
def alg(request):
    return Algebra(**request.param)


def _rvec(alg, rng):
    return alg.vector(rng.standard_normal(alg.n))


def _rmv(alg, rng):
    return alg.multivector(rng.standard_normal(alg.dim))


def _rblade(alg, rng, r):
    """Build a random r-blade as the wedge of r random vectors."""
    if r == 0:
        return alg.scalar(rng.standard_normal())
    v = _rvec(alg, rng)
    B = v
    for _ in range(r - 1):
        B = outer_product(B, _rvec(alg, rng))
    return B


# ---------------------------------------------------------------------------
# Theorem 5 (§4.1, label:innerlowersgrade) — a⌋A_r is grade r-1.
# ---------------------------------------------------------------------------


class TestThm5InnerLowersGrade:
    """Theorem 5 (§4.1, label:innerlowersgrade): a⌋A_r is an (r-1)-vector."""

    def test_vector_contracts_bivector_to_vector(self, alg):
        """a ⌋ B₂ is a 1-vector."""
        vecs = alg.basis_vectors()
        if len(vecs) < 3:
            pytest.skip("Need n ≥ 3")
        B = outer_product(vecs[0], vecs[1])
        result = left_contraction(vecs[0], B)
        # Should be pure grade-1
        for k in range(alg.n + 1):
            g = grade(result, k)
            if k == 1:
                continue
            assert np.allclose(g.data, 0, atol=1e-12), f"Unexpected grade-{k} component"

    def test_random_contraction_grade(self, alg):
        """a ⌋ A_r has grade r-1 for random blades."""
        rng = np.random.default_rng(42)
        for r in range(1, min(alg.n, 4) + 1):
            a = _rvec(alg, rng)
            Ar = _rblade(alg, rng, r)
            result = left_contraction(a, Ar)
            # All components outside grade r-1 should vanish
            for k in range(alg.n + 1):
                if k == r - 1:
                    continue
                assert np.allclose(grade(result, k).data, 0, atol=1e-10)


# ---------------------------------------------------------------------------
# Theorem 7 (§4.1, label:outerraisesgrade) — a∧A_r is grade r+1.
# ---------------------------------------------------------------------------


class TestThm7OuterRaisesGrade:
    """Theorem 7 (§4.1, label:outerraisesgrade): a∧A_r is an (r+1)-vector."""

    def test_random_wedge_grade(self, alg):
        """a ∧ A_r has grade r+1 for random blades."""
        rng = np.random.default_rng(43)
        for r in range(0, min(alg.n - 1, 3) + 1):
            a = _rvec(alg, rng)
            Ar = _rblade(alg, rng, r)
            result = outer_product(a, Ar)
            for k in range(alg.n + 1):
                if k == r + 1:
                    continue
                assert np.allclose(grade(result, k).data, 0, atol=1e-10)


# ---------------------------------------------------------------------------
# Eq. 1.48 (label:vecrprod) — aA_r = a⌋A_r + a∧A_r
# ---------------------------------------------------------------------------


class TestEq148VectorTimesRVector:
    """Eq. 1.48 (§4.1, label:vecrprod): aA_r = a⌋A_r + a∧A_r."""

    def test_random(self, alg):
        """GP of vector and r-vector decomposes into contraction + wedge."""
        rng = np.random.default_rng(44)
        for r in range(0, min(alg.n, 4) + 1):
            a = _rvec(alg, rng)
            Ar = _rblade(alg, rng, r)
            lhs = geometric_product(a, Ar)
            rhs = left_contraction(a, Ar) + outer_product(a, Ar)
            assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Theorem 6 (§4.2, label:generalprod) — Grade structure of A_r B_s.
# Grades are |r-s|, |r-s|+2, ..., r+s.
# ---------------------------------------------------------------------------


class TestThm6GradeStructure:
    """Theorem 6 (§4.2, label:generalprod): A_r B_s has grades |r-s|, |r-s|+2, ..., r+s."""

    def test_grade_structure(self, alg):
        """Product of homogeneous MVs has only the predicted grades."""
        rng = np.random.default_rng(45)
        for r in range(min(alg.n, 3) + 1):
            for s in range(min(alg.n, 3) + 1):
                Ar = _rblade(alg, rng, r)
                Bs = _rblade(alg, rng, s)
                product = geometric_product(Ar, Bs)
                allowed = set(range(abs(r - s), r + s + 1, 2))
                for k in range(alg.n + 1):
                    g = grade(product, k)
                    if k not in allowed:
                        assert np.allclose(g.data, 0, atol=1e-10), (
                            f"Grade {k} nonzero in product of grade-{r} × grade-{s}"
                        )


# ---------------------------------------------------------------------------
# Theorem 10, 1st identity (§4.2, label:associdents) — Outer product associativity.
# A ∧ (B ∧ C) = (A ∧ B) ∧ C
# ---------------------------------------------------------------------------


class TestThm10OuterAssociativity:
    """Theorem 10, 1st identity (§4.2, label:associdents): A∧(B∧C) = (A∧B)∧C."""

    def test_vectors(self, alg):
        """Outer product of three vectors is associative."""
        if alg.n < 3:
            pytest.skip("Need n ≥ 3")
        rng = np.random.default_rng(46)
        a, b, c = [_rvec(alg, rng) for _ in range(3)]
        lhs = outer_product(a, outer_product(b, c))
        rhs = outer_product(outer_product(a, b), c)
        assert np.allclose(lhs.data, rhs.data, atol=1e-12)

    def test_mixed_grades(self, alg):
        """Outer product associativity with mixed-grade operands."""
        if alg.n < 4:
            pytest.skip("Need n ≥ 4")
        rng = np.random.default_rng(47)
        A = _rblade(alg, rng, 1)
        B = _rblade(alg, rng, 1)
        C = _rblade(alg, rng, 2)
        lhs = outer_product(A, outer_product(B, C))
        rhs = outer_product(outer_product(A, B), C)
        assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Theorem 10, 3rd identity (§4.2, label:associdents) — A⌋(B⌋C) = (A∧B)⌋C
# ---------------------------------------------------------------------------


class TestThm10ContractionWedge:
    """Theorem 10, 3rd identity (§4.2, label:associdents): A⌋(B⌋C) = (A∧B)⌋C."""

    def test_vectors_into_trivector(self, alg):
        """a⌋(b⌋C₃) = (a∧b)⌋C₃ for vectors a, b and trivector C₃."""
        if alg.n < 3:
            pytest.skip("Need n ≥ 3")
        rng = np.random.default_rng(48)
        a = _rvec(alg, rng)
        b = _rvec(alg, rng)
        C = _rblade(alg, rng, 3)
        lhs = left_contraction(a, left_contraction(b, C))
        rhs = left_contraction(outer_product(a, b), C)
        assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Theorem 10, 2nd identity (§4.2) — A⌋(B⌊C) = (A⌋B)⌊C
# ---------------------------------------------------------------------------


class TestThm10LeftRightAssoc:
    """Theorem 10, 2nd identity (§4.2, label:associdents): A⌋(B⌊C) = (A⌋B)⌊C."""

    def test_random(self, alg):
        """Mixed left/right contraction associativity."""
        if alg.n < 3:
            pytest.skip("Need n ≥ 3")
        rng = np.random.default_rng(49)
        A = _rblade(alg, rng, 1)
        B = _rblade(alg, rng, 3)
        C = _rblade(alg, rng, 1)
        lhs = left_contraction(A, right_contraction(B, C))
        rhs = right_contraction(left_contraction(A, B), C)
        assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Theorem 10, 4th identity (§4.2) — A⌊(B∧C) = (A⌊B)⌊C
# ---------------------------------------------------------------------------


class TestThm10RightContractionWedge:
    """Theorem 10, 4th identity (§4.2, label:associdents): A⌊(B∧C) = (A⌊B)⌊C."""

    def test_random(self, alg):
        """Right contraction distributes over wedge."""
        if alg.n < 3:
            pytest.skip("Need n ≥ 3")
        rng = np.random.default_rng(50)
        A = _rblade(alg, rng, 3)
        B = _rblade(alg, rng, 1)
        C = _rblade(alg, rng, 1)
        lhs = right_contraction(A, outer_product(B, C))
        rhs = right_contraction(right_contraction(A, B), C)
        assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Eq. 1.80 (label:wedgehighest) — a₁∧a₂∧…∧aᵣ = ⟨a₁a₂…aᵣ⟩_r
# ---------------------------------------------------------------------------


class TestEq180WedgeIsHighestGrade:
    """Eq. 1.80 (§4.2, label:wedgehighest): a₁∧…∧aᵣ = ⟨a₁…aᵣ⟩_r."""

    def test_two_vectors(self, alg):
        """a∧b = ⟨ab⟩₂."""
        rng = np.random.default_rng(51)
        a, b = _rvec(alg, rng), _rvec(alg, rng)
        assert np.allclose(outer_product(a, b).data, grade(geometric_product(a, b), 2).data, atol=1e-12)

    def test_three_vectors(self, alg):
        """a∧b∧c = ⟨abc⟩₃."""
        if alg.n < 3:
            pytest.skip("Need n ≥ 3")
        rng = np.random.default_rng(52)
        a, b, c = [_rvec(alg, rng) for _ in range(3)]
        lhs = outer_product(outer_product(a, b), c)
        rhs = grade(geometric_product(geometric_product(a, b), c), 3)
        assert np.allclose(lhs.data, rhs.data, atol=1e-12)


# ---------------------------------------------------------------------------
# Eq. 2.38 (label:commuteouter) — A_r ∧ B_s = (-1)^{rs} B_s ∧ A_r
# ---------------------------------------------------------------------------


class TestEq238OuterCommutativity:
    """Eq. 2.38 (§5.2, label:commuteouter): A_r∧B_s = (-1)^{rs} B_s∧A_r."""

    def test_vectors(self, alg):
        """a∧b = -b∧a for vectors (r=s=1, (-1)^1 = -1)."""
        rng = np.random.default_rng(53)
        a, b = _rvec(alg, rng), _rvec(alg, rng)
        assert np.allclose(outer_product(a, b).data, -outer_product(b, a).data, atol=1e-12)

    def test_vector_bivector(self, alg):
        """a∧B₂ = -B₂∧a (r=1, s=2, (-1)^2 = +1)... wait, (-1)^{1·2} = 1."""
        if alg.n < 3:
            pytest.skip("Need n ≥ 3")
        rng = np.random.default_rng(54)
        a = _rvec(alg, rng)
        B = _rblade(alg, rng, 2)
        # (-1)^{1*2} = 1, so a∧B = B∧a
        assert np.allclose(outer_product(a, B).data, outer_product(B, a).data, atol=1e-10)

    def test_bivector_bivector(self, alg):
        """B₂∧C₂ = C₂∧B₂ ((-1)^{2·2} = 1)."""
        if alg.n < 4:
            pytest.skip("Need n ≥ 4")
        rng = np.random.default_rng(55)
        B = _rblade(alg, rng, 2)
        C = _rblade(alg, rng, 2)
        assert np.allclose(outer_product(B, C).data, outer_product(C, B).data, atol=1e-10)


# ---------------------------------------------------------------------------
# Eq. 2.36 (label:commuteinner) — A_r⌋B_s = (-1)^{r(s-1)} B_s⌊A_r
# ---------------------------------------------------------------------------


class TestEq236InnerCommutativity:
    """Eq. 2.36 (§5.2, label:commuteinner): A_r⌋B_s = (-1)^{r(s-1)} B_s⌊A_r."""

    def test_vector_bivector(self, alg):
        """a⌋B₂ = (-1)^{1·1} B₂⌊a = -B₂⌊a."""
        if alg.n < 2:
            pytest.skip("Need n ≥ 2")
        rng = np.random.default_rng(56)
        a = _rvec(alg, rng)
        B = _rblade(alg, rng, 2)
        lhs = left_contraction(a, B)
        rhs = (-1) ** (1 * (2 - 1)) * right_contraction(B, a)
        assert np.allclose(lhs.data, rhs.data, atol=1e-10)

    def test_random_grades(self, alg):
        """General test of Eq. 2.36 for various grade pairs."""
        rng = np.random.default_rng(57)
        for r in range(min(alg.n, 3) + 1):
            for s in range(r, min(alg.n, 3) + 1):
                Ar = _rblade(alg, rng, r)
                Bs = _rblade(alg, rng, s)
                lhs = left_contraction(Ar, Bs)
                sign = (-1) ** (r * (s - 1))
                rhs = sign * right_contraction(Bs, Ar)
                assert np.allclose(lhs.data, rhs.data, atol=1e-10), f"Failed for r={r}, s={s}"


# ---------------------------------------------------------------------------
# Eq. 1.72 / Theorem 9 (label:veclinoutid) —
# a⌋(a₁∧…∧aᵣ) = Σ (-1)^{j-1} (a·aⱼ) a₁∧…∧ǎⱼ∧…∧aᵣ
# ---------------------------------------------------------------------------


class TestThm9ContractionExpansion:
    """Theorem 9 (§4.2, label:veclinoutid): expansion of a⌋(a₁∧…∧aᵣ)."""

    def test_vector_into_bivector(self, alg):
        """a⌋(b∧c) = (a·b)c - (a·c)b."""
        rng = np.random.default_rng(58)
        a, b, c = [_rvec(alg, rng) for _ in range(3)]
        lhs = left_contraction(a, outer_product(b, c))
        ab = float(scalar_product(a, b))
        ac = float(scalar_product(a, c))
        rhs = ab * c - ac * b
        assert np.allclose(lhs.data, rhs.data, atol=1e-10)

    def test_vector_into_trivector(self, alg):
        """a⌋(b∧c∧d) = (a·b)(c∧d) - (a·c)(b∧d) + (a·d)(b∧c)."""
        if alg.n < 3:
            pytest.skip("Need n ≥ 3")
        rng = np.random.default_rng(59)
        a, b, c, d = [_rvec(alg, rng) for _ in range(4)]
        lhs = left_contraction(a, outer_product(outer_product(b, c), d))
        ab = float(scalar_product(a, b))
        ac = float(scalar_product(a, c))
        ad = float(scalar_product(a, d))
        rhs = ab * outer_product(c, d) - ac * outer_product(b, d) + ad * outer_product(b, c)
        assert np.allclose(lhs.data, rhs.data, atol=1e-10)


# ---------------------------------------------------------------------------
# Eqs. 1.62 (label:usefulids, 1st) — a⌋(A_r B_s) = (a⌋A_r)B_s + Â_r(a⌋B_s)
# ---------------------------------------------------------------------------


class TestEq162UsefulIdentity1:
    """Eq. 1.62, 1st identity (§4.2, label:usefulids): a⌋(A_r B_s) = (a⌋A_r)B_s + Â_r(a⌋B_s)."""

    def test_random(self, alg):
        """Test the first useful identity with random blades."""
        rng = np.random.default_rng(60)
        for r in range(1, min(alg.n, 3) + 1):
            for s in range(1, min(alg.n, 3) + 1):
                a = _rvec(alg, rng)
                Ar = _rblade(alg, rng, r)
                Bs = _rblade(alg, rng, s)
                lhs = left_contraction(a, geometric_product(Ar, Bs))
                rhs = geometric_product(left_contraction(a, Ar), Bs) + geometric_product(
                    grade_involution(Ar), left_contraction(a, Bs)
                )
                assert np.allclose(lhs.data, rhs.data, atol=1e-9), f"Failed for r={r}, s={s}"


# ---------------------------------------------------------------------------
# Eq. 1.85, 1st (label:contwedgeids) — a⌋(A_r∧B_s) = (a⌋A_r)∧B_s + Â_r∧(a⌋B_s)
# ---------------------------------------------------------------------------


class TestEq185ContractionWedgeIdentity:
    """Eq. 1.85, 1st (§4.2, label:contwedgeids): a⌋(A_r∧B_s) = (a⌋A_r)∧B_s + Â_r∧(a⌋B_s)."""

    def test_random(self, alg):
        """Test contraction-wedge identity with random blades."""
        if alg.n < 3:
            pytest.skip("Need n ≥ 3")
        rng = np.random.default_rng(61)
        a = _rvec(alg, rng)
        Ar = _rblade(alg, rng, 1)
        Bs = _rblade(alg, rng, 2)
        lhs = left_contraction(a, outer_product(Ar, Bs))
        rhs = outer_product(left_contraction(a, Ar), Bs) + outer_product(grade_involution(Ar), left_contraction(a, Bs))
        assert np.allclose(lhs.data, rhs.data, atol=1e-10)
