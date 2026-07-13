"""Tests for the Terathon/RGA convention layer operations."""

import numpy as np
import pytest

from galaga import Algebra, metric_inner_product, reverse, scalar_product
from galaga.algebra import Multivector


class TestExtendedMetricMatrix:
    """Tests for Algebra.extended_metric_matrix()."""

    def test_euclidean_cl3_diagonal(self):
        """In Cl(3,0), all diagonal entries are 1 (all signatures +1)."""
        alg = Algebra(3)
        G = alg.extended_metric_matrix()
        assert G.shape == (8, 8)
        # Every blade's metric entry = product of +1s = 1
        assert np.allclose(G, np.eye(8))

    def test_scalar_entry_is_one(self):
        """G[0,0] = 1 (empty product) for any algebra."""
        for alg in [Algebra(3), Algebra(1, 3), Algebra(3, 0, 1)]:
            G = alg.extended_metric_matrix()
            assert G[0, 0] == 1.0

    def test_vector_entries_match_signature(self):
        """G[1<<k, 1<<k] = signature[k]."""
        alg = Algebra(1, 3)  # signature is (1, -1, -1, -1) after reordering
        G = alg.extended_metric_matrix()
        for k in range(alg.n):
            assert G[1 << k, 1 << k] == alg.signature[k]

    def test_bivector_entries_are_products(self):
        """G[bitmask] = product of signature values for set bits."""
        alg = Algebra(1, 3)
        G = alg.extended_metric_matrix()
        sig = alg.signature
        # bitmask 0b0011 = bits 0,1 → sig[0]*sig[1]
        assert G[0b0011, 0b0011] == sig[0] * sig[1]
        # bitmask 0b1100 = bits 2,3 → sig[2]*sig[3]
        assert G[0b1100, 0b1100] == sig[2] * sig[3]

    def test_off_diagonal_zero(self):
        """G is diagonal."""
        alg = Algebra(3)
        G = alg.extended_metric_matrix()
        assert np.allclose(G - np.diag(np.diag(G)), 0)

    def test_pga_has_zero_entries(self):
        """In PGA, blades containing the null vector have G entry = 0."""
        pga = Algebra(3, 0, 1)
        G = pga.extended_metric_matrix()
        # e0 is null (bit 0 in galaga's ordering for PGA)
        # Find which bit is the null vector
        null_bit = None
        for k in range(pga.n):
            if pga.signature[k] == 0:
                null_bit = k
                break
        assert null_bit is not None
        # Any bitmask containing the null bit should have G=0
        for idx in range(pga.dim):
            if idx & (1 << null_bit):
                assert G[idx, idx] == 0.0

    def test_caching(self):
        """Extended metric matrix is computed once and cached."""
        alg = Algebra(3)
        G1 = alg.extended_metric_matrix()
        G2 = alg.extended_metric_matrix()
        assert G1 is G2


class TestMetricInnerProduct:
    """Tests for metric_inner_product()."""

    def test_vector_self_product_euclidean(self):
        """metric_inner_product(e_i, e_i) = 1 in Euclidean space."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        assert metric_inner_product(e1, e1).data[0] == pytest.approx(1.0)
        assert metric_inner_product(e2, e2).data[0] == pytest.approx(1.0)
        assert metric_inner_product(e3, e3).data[0] == pytest.approx(1.0)

    def test_bivector_self_product_euclidean(self):
        """metric_inner_product(e12, e12) = +1 in Cl(3,0).

        This is the key difference from scalar_product which gives -1.
        """
        alg = Algebra(3)
        e1, e2, _ = alg.basis_vectors()
        e12 = e1 * e2
        assert metric_inner_product(e12, e12).data[0] == pytest.approx(1.0)
        assert scalar_product(e12, e12).data[0] == pytest.approx(-1.0)

    def test_identity_with_scalar_product_reverse(self):
        """metric_inner_product(A,B) == scalar_product(A, reverse(B))."""
        alg = Algebra(3)
        rng = np.random.default_rng(42)
        for _ in range(100):
            A = Multivector(alg, rng.standard_normal(alg.dim))
            B = Multivector(alg, rng.standard_normal(alg.dim))
            mip = metric_inner_product(A, B).data[0]
            sp_rev = scalar_product(A, reverse(B)).data[0]
            assert mip == pytest.approx(sp_rev, abs=1e-12)

    def test_mixed_grades_zero(self):
        """metric_inner_product of different-grade blades is 0."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        e12 = e1 * e2
        e123 = e1 * e2 * e3
        assert metric_inner_product(e1, e12).data[0] == pytest.approx(0.0)
        assert metric_inner_product(e1, e123).data[0] == pytest.approx(0.0)
        assert metric_inner_product(e12, e123).data[0] == pytest.approx(0.0)

    def test_indefinite_signature(self):
        """Correct signs in Cl(1,3)."""
        sta = Algebra(1, 3)
        g0, g1, g2, g3 = sta.basis_vectors()
        # g0²=+1, g1²=-1
        assert metric_inner_product(g0, g0).data[0] == pytest.approx(1.0)
        assert metric_inner_product(g1, g1).data[0] == pytest.approx(-1.0)
        # g01: sig[0]*sig[1] = 1*(-1) = -1
        g01 = g0 * g1
        assert metric_inner_product(g01, g01).data[0] == pytest.approx(-1.0)

    def test_pga_null_blade(self):
        """Null blades have metric_inner_product = 0 with themselves."""
        pga = Algebra(3, 0, 1)
        e0, e1, e2, e3 = pga.basis_vectors()
        assert metric_inner_product(e0, e0).data[0] == pytest.approx(0.0)
        # e0 ∧ e1 also contains the null vector
        e01 = e0 * e1
        assert metric_inner_product(e01, e01).data[0] == pytest.approx(0.0)

    def test_orthogonal_vectors(self):
        """Orthogonal vectors have metric_inner_product = 0."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        assert metric_inner_product(e1, e2).data[0] == pytest.approx(0.0)
        assert metric_inner_product(e1, e3).data[0] == pytest.approx(0.0)

    def test_returns_scalar_multivector(self):
        """Result is a scalar multivector, not a float."""
        alg = Algebra(3)
        e1, _, _ = alg.basis_vectors()
        result = metric_inner_product(e1, e1)
        assert isinstance(result, Multivector)
        assert result.algebra is alg

    def test_different_algebras_raises(self):
        """Operands from different algebras should raise."""
        alg1 = Algebra(3)
        alg2 = Algebra(2)
        a = Multivector(alg1, np.ones(alg1.dim))
        b = Multivector(alg2, np.ones(alg2.dim))
        with pytest.raises((ValueError, TypeError)):
            metric_inner_product(a, b)
