"""Tests derived from Chisolm, "Geometric Algebra" (arXiv:1205.5935v1).

Sections 2–3: Definitions/Axioms and Contents of a Geometric Algebra.

Each test is named after the axiom, theorem, or equation it verifies.
The docstring cites the exact reference in the paper.
"""

import numpy as np
import pytest

from galaga import (
    Algebra,
    gp,
    grade,
    inverse,
    is_scalar,
    is_vector,
    left_contraction,
    op,
    right_contraction,
    scalar_product,
)

# ---------------------------------------------------------------------------
# Fixtures — test across Euclidean, Minkowski, and degenerate signatures
# ---------------------------------------------------------------------------

SIGNATURES = [
    (1, 1),          # Cl(2,0)
    (1, 1, 1),       # Cl(3,0)
    (1, -1, -1, -1), # Cl(1,3) — STA
    (0, 1, 1, 1),    # Cl(3,0,1) — PGA
]


@pytest.fixture(params=SIGNATURES, ids=["Cl2", "Cl3", "STA", "PGA"])
def alg(request):
    return Algebra(request.param)


def _random_vector(alg, rng):
    """Return a random vector in the algebra."""
    coeffs = rng.standard_normal(alg.n)
    return alg.vector(coeffs)


def _random_multivector(alg, rng):
    """Return a random multivector in the algebra."""
    return alg.multivector(rng.standard_normal(alg.dim))


# ---------------------------------------------------------------------------
# Axiom 4 (§2, label:sqvec) — The square of every vector is a scalar.
# ---------------------------------------------------------------------------

class TestAxiom4VectorSquareIsScalar:
    """Axiom 4 (§2, label:sqvec): v² ∈ G₀ for every vector v."""

    def test_basis_vectors(self, alg):
        """Axiom 4: each basis vector squares to its signature entry."""
        for i, e in enumerate(alg.basis_vectors()):
            v2 = gp(e, e)
            assert is_scalar(v2), f"e{i+1}² is not scalar"
            assert v2.scalar_part == pytest.approx(alg.signature[i])

    def test_random_vectors(self, alg):
        """Axiom 4: random vector squares to a scalar."""
        rng = np.random.default_rng(42)
        for _ in range(5):
            v = _random_vector(alg, rng)
            assert is_scalar(gp(v, v))


# ---------------------------------------------------------------------------
# Eq. after Axiom 4 — Symmetrized product equals inner product.
# ½(uv + vu) = u · v  (a scalar)
# ---------------------------------------------------------------------------

class TestSymmetrizedProduct:
    """Eq. after Axiom 4 (§2): ½(uv + vu) = u · v."""

    def test_basis_pairs(self, alg):
        """Symmetrized product of basis vectors equals their inner product."""
        vecs = alg.basis_vectors()
        for i, ei in enumerate(vecs):
            for j, ej in enumerate(vecs):
                sym = 0.5 * (gp(ei, ej) + gp(ej, ei))
                expected = alg.signature[i] if i == j else 0.0
                assert is_scalar(sym)
                assert sym.scalar_part == pytest.approx(expected)

    def test_random_pairs(self, alg):
        """Symmetrized product of random vectors is a scalar."""
        rng = np.random.default_rng(123)
        for _ in range(5):
            u = _random_vector(alg, rng)
            v = _random_vector(alg, rng)
            sym = 0.5 * (gp(u, v) + gp(v, u))
            assert is_scalar(sym)


# ---------------------------------------------------------------------------
# Eq. 1.6 (label:prodsum / label:def) — GP decomposition: uv = u·v + u∧v
# ---------------------------------------------------------------------------

class TestGPDecomposition:
    """Eq. 1.6 (§1.1, label:def): uv = u·v + u∧v for vectors u, v."""

    def test_random_vectors(self, alg):
        """GP of two vectors equals inner + outer product."""
        rng = np.random.default_rng(77)
        for _ in range(5):
            u = _random_vector(alg, rng)
            v = _random_vector(alg, rng)
            lhs = gp(u, v)
            rhs = left_contraction(u, v) + op(u, v)
            assert np.allclose(lhs.data, rhs.data, atol=1e-12)


# ---------------------------------------------------------------------------
# Theorem 2 (§3, label:zeroifffindep) — Outer product vanishes iff dependent.
# ---------------------------------------------------------------------------

class TestThm2OuterProductDependence:
    """Theorem 2 (§3, label:zeroifffindep): a₁∧…∧aᵣ = 0 iff dependent."""

    def test_self_wedge_vanishes(self, alg):
        """a ∧ a = 0 for any vector."""
        rng = np.random.default_rng(10)
        v = _random_vector(alg, rng)
        assert np.allclose(op(v, v).data, 0, atol=1e-12)

    def test_dependent_triple_vanishes(self, alg):
        """(αa + βb) ∧ a ∧ b = 0."""
        if alg.n < 3:
            pytest.skip("Need n ≥ 3 for trivector test")
        rng = np.random.default_rng(11)
        a = _random_vector(alg, rng)
        b = _random_vector(alg, rng)
        c = 2.0 * a + 3.0 * b  # linearly dependent on a, b
        assert np.allclose(op(op(c, a), b).data, 0, atol=1e-12)

    def test_independent_nonzero(self, alg):
        """Outer product of independent basis vectors is nonzero."""
        vecs = alg.basis_vectors()
        if len(vecs) >= 2:
            result = op(vecs[0], vecs[1])
            assert not np.allclose(result.data, 0)


# ---------------------------------------------------------------------------
# Theorem 3 (§3, label:Aissubspace) — a ∧ A_r = 0 iff a in span(A_r).
# ---------------------------------------------------------------------------

class TestThm3BladeSubspace:
    """Theorem 3 (§3, label:Aissubspace): a∧A_r = 0 iff a ∈ subspace(A_r)."""

    def test_vector_in_blade_wedges_to_zero(self, alg):
        """A factor of a blade wedges to zero with that blade."""
        vecs = alg.basis_vectors()
        if len(vecs) < 2:
            pytest.skip("Need n ≥ 2")
        B = op(vecs[0], vecs[1])
        assert np.allclose(op(vecs[0], B).data, 0, atol=1e-12)
        assert np.allclose(op(vecs[1], B).data, 0, atol=1e-12)

    def test_vector_outside_blade_nonzero(self, alg):
        """A vector not in the blade's subspace gives nonzero wedge."""
        vecs = alg.basis_vectors()
        if len(vecs) < 3:
            pytest.skip("Need n ≥ 3")
        B = op(vecs[0], vecs[1])
        assert not np.allclose(op(vecs[2], B).data, 0)

    def test_linear_combination_in_blade(self, alg):
        """A linear combination of blade factors wedges to zero."""
        vecs = alg.basis_vectors()
        if len(vecs) < 2:
            pytest.skip("Need n ≥ 2")
        B = op(vecs[0], vecs[1])
        combo = 3.0 * vecs[0] - 2.0 * vecs[1]
        assert np.allclose(op(combo, B).data, 0, atol=1e-12)


# ---------------------------------------------------------------------------
# Theorem 4 (§3, label:AmultofBifsamespace) — Same subspace iff scalar multiple.
# ---------------------------------------------------------------------------

class TestThm4SameSubspaceScalarMultiple:
    """Theorem 4 (§3, label:AmultofBifsamespace): same subspace ↔ scalar multiple."""

    def test_rescaled_blade(self, alg):
        """λ(a∧b) represents the same subspace as a∧b."""
        vecs = alg.basis_vectors()
        if len(vecs) < 2:
            pytest.skip("Need n ≥ 2")
        B1 = op(vecs[0], vecs[1])
        B2 = 5.0 * B1
        # Same subspace: any vector in B1 also wedges to zero with B2
        assert np.allclose(op(vecs[0], B2).data, 0, atol=1e-12)
        assert np.allclose(op(vecs[1], B2).data, 0, atol=1e-12)

    def test_reordered_factors(self, alg):
        """a∧b and b∧a differ only by sign (same subspace)."""
        vecs = alg.basis_vectors()
        if len(vecs) < 2:
            pytest.skip("Need n ≥ 2")
        B1 = op(vecs[0], vecs[1])
        B2 = op(vecs[1], vecs[0])
        assert np.allclose(B1.data, -B2.data, atol=1e-12)


# ---------------------------------------------------------------------------
# Proof of Theorem 1 (§3, label:outerisblade) — Orthogonal wedge = GP.
# ---------------------------------------------------------------------------

class TestThm1OrthogonalWedgeEqualsGP:
    """Theorem 1 proof (§3, label:outerisblade): e_i ∧ e_j = e_i e_j when orthogonal."""

    def test_orthogonal_basis(self, alg):
        """Wedge of orthogonal basis vectors equals their geometric product."""
        vecs = alg.basis_vectors()
        for i in range(len(vecs)):
            for j in range(i + 1, len(vecs)):
                w = op(vecs[i], vecs[j])
                g = gp(vecs[i], vecs[j])
                assert np.allclose(w.data, g.data, atol=1e-12)


# ---------------------------------------------------------------------------
# Theorem 5 (§3, label:vecorthtoA) — a ⌋ A_r = 0 iff a ⊥ subspace(A_r).
# ---------------------------------------------------------------------------

class TestThm5OrthogonalityViaContraction:
    """Theorem 5 (§3, label:vecorthtoA): a⌋A_r = 0 iff a ⊥ A_r."""

    def test_orthogonal_vector_contracts_to_zero(self, alg):
        """A vector orthogonal to a blade contracts to zero."""
        vecs = alg.basis_vectors()
        if len(vecs) < 3:
            pytest.skip("Need n ≥ 3")
        B = op(vecs[0], vecs[1])  # blade in e1-e2 plane
        # e3 is orthogonal to both e1 and e2
        result = left_contraction(vecs[2], B)
        assert np.allclose(result.data, 0, atol=1e-12)

    def test_nonorthogonal_vector_contracts_nonzero(self, alg):
        """A factor of a blade contracts to nonzero."""
        vecs = alg.basis_vectors()
        if len(vecs) < 2:
            pytest.skip("Need n ≥ 2")
        # Skip if e1 is null (PGA)
        if alg.signature[0] == 0:
            pytest.skip("e1 is null in this algebra")
        B = op(vecs[0], vecs[1])
        result = left_contraction(vecs[0], B)
        assert not np.allclose(result.data, 0)


# ---------------------------------------------------------------------------
# Eq. 1.4 — Vector inverse: v⁻¹ = v / v² for non-null v.
# ---------------------------------------------------------------------------

class TestVectorInverse:
    """Eq. 1.4 (§1.1): v⁻¹ = v / v² for non-null vectors."""

    def test_basis_inverse(self, alg):
        """Each non-null basis vector has v * v⁻¹ = 1."""
        for i, e in enumerate(alg.basis_vectors()):
            if alg.signature[i] == 0:
                continue  # skip null vectors
            v_inv = inverse(e)
            product = gp(e, v_inv)
            assert product.scalar_part == pytest.approx(1.0, abs=1e-12)
            assert np.allclose(product.data[1:], 0, atol=1e-12)

    def test_random_nonnull_inverse(self, alg):
        """Random non-null vector satisfies v * v⁻¹ = 1."""
        rng = np.random.default_rng(99)
        for _ in range(5):
            v = _random_vector(alg, rng)
            v2 = gp(v, v).scalar_part
            if abs(v2) < 1e-10:
                continue
            v_inv = inverse(v)
            product = gp(v, v_inv)
            assert product.scalar_part == pytest.approx(1.0, abs=1e-12)
