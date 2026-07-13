"""Tests for the Terathon/RGA convention layer operations."""

import numpy as np
import pytest

from galaga import Algebra, metric_inner_product, op, reverse, scalar_product
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


class TestLeftComplement:
    """Tests for left_complement() and right_complement() aliases."""

    def test_left_complement_is_uncomplement(self):
        """left_complement is numerically identical to uncomplement."""
        from galaga import left_complement, uncomplement

        alg = Algebra(3)
        rng = np.random.default_rng(42)
        A = Multivector(alg, rng.standard_normal(alg.dim))
        assert np.allclose(left_complement(A).data, uncomplement(A).data)

    def test_right_complement_is_complement(self):
        """right_complement is the same as complement."""
        from galaga import complement, right_complement

        alg = Algebra(1, 3)
        rng = np.random.default_rng(42)
        A = Multivector(alg, rng.standard_normal(alg.dim))
        assert np.allclose(right_complement(A).data, complement(A).data)

    def test_round_trip_left_right(self):
        """left_complement(right_complement(A)) == A."""
        from galaga import left_complement, right_complement

        for sig in [(3,), (1, 3), (3, 0, 1)]:
            alg = Algebra(*sig)
            rng = np.random.default_rng(77)
            A = Multivector(alg, rng.standard_normal(alg.dim))
            rt = left_complement(right_complement(A))
            assert np.allclose(rt.data, A.data), f"Failed for {sig}"

    def test_round_trip_right_left(self):
        """right_complement(left_complement(A)) == A."""
        from galaga import left_complement, right_complement

        for sig in [(3,), (1, 3), (3, 0, 1)]:
            alg = Algebra(*sig)
            rng = np.random.default_rng(88)
            A = Multivector(alg, rng.standard_normal(alg.dim))
            rt = right_complement(left_complement(A))
            assert np.allclose(rt.data, A.data), f"Failed for {sig}"

    def test_left_complement_wedge_identity(self):
        """left_complement(e_S) ∧ e_S = +I for all basis blades."""
        from galaga import left_complement

        for sig in [(3,), (1, 3), (3, 0, 1)]:
            alg = Algebra(*sig)
            for blade_idx in range(1, alg.dim):
                data = np.zeros(alg.dim)
                data[blade_idx] = 1.0
                blade = Multivector(alg, data)
                lc = left_complement(blade)
                product = op(lc, blade)
                # Should equal +1 * I
                assert product.data[alg.dim - 1] == pytest.approx(1.0), (
                    f"Failed for sig={sig}, bitmask={blade_idx:0{alg.n}b}"
                )

    def test_left_complement_random_mvs(self):
        """Round-trip works for random multivectors in multiple algebras."""
        from galaga import complement, left_complement

        rng = np.random.default_rng(123)
        for sig in [(2,), (3,), (1, 3), (3, 0, 1), (4, 1)]:
            alg = Algebra(*sig)
            for _ in range(50):
                A = Multivector(alg, rng.standard_normal(alg.dim))
                rt = left_complement(complement(A))
                assert np.allclose(rt.data, A.data, atol=1e-12), f"Failed for {sig}"


class TestMetricAntiexomorphismMatrix:
    """Tests for Algebra.metric_antiexomorphism_matrix()."""

    def test_g_times_gbar_equals_det_identity_nondegenerate(self):
        """G · 𝔾 = det(metric) · I for non-degenerate algebras."""
        import operator
        from functools import reduce

        for sig in [(3,), (1, 3), (2, 1)]:
            alg = Algebra(*sig)
            G = alg.extended_metric_matrix()
            Gbar = alg.metric_antiexomorphism_matrix()
            det = reduce(operator.mul, alg.signature, 1)
            expected = det * np.eye(alg.dim)
            assert np.allclose(G @ Gbar, expected), f"Failed for {sig}"

    def test_g_times_gbar_zero_pga(self):
        """G · 𝔾 = 0 for degenerate algebras (det=0)."""
        pga = Algebra(3, 0, 1)
        G = pga.extended_metric_matrix()
        Gbar = pga.metric_antiexomorphism_matrix()
        assert np.allclose(G @ Gbar, 0)

    def test_pga_antimetric_nonzero(self):
        """In PGA, 𝔾 is still individually meaningful even though G·𝔾=0."""
        pga = Algebra(3, 0, 1)
        Gbar = pga.metric_antiexomorphism_matrix()
        # The pseudoscalar entry should be 1 (empty product over absent vectors)
        assert Gbar[pga.dim - 1, pga.dim - 1] == 1.0
        # Non-zero entries exist
        assert np.any(np.diag(Gbar) != 0)

    def test_scalar_entry_is_determinant(self):
        """𝔾[0,0] = det(metric) = product of all signature values."""
        import operator
        from functools import reduce

        alg = Algebra(1, 3)
        det = reduce(operator.mul, alg.signature, 1)
        Gbar = alg.metric_antiexomorphism_matrix()
        assert Gbar[0, 0] == det

    def test_pseudoscalar_entry_is_one(self):
        """𝔾[full, full] = 1 (empty product over no absent vectors)."""
        for sig in [(3,), (1, 3), (3, 0, 1)]:
            alg = Algebra(*sig)
            Gbar = alg.metric_antiexomorphism_matrix()
            assert Gbar[alg.dim - 1, alg.dim - 1] == 1.0

    def test_caching(self):
        """Antimetric matrix is computed once and cached."""
        alg = Algebra(3)
        G1 = alg.metric_antiexomorphism_matrix()
        G2 = alg.metric_antiexomorphism_matrix()
        assert G1 is G2


class TestMetricApplyAntimetricApply:
    """Tests for metric_apply() and antimetric_apply()."""

    def test_metric_apply_euclidean_identity(self):
        """In Euclidean Cl(3,0), metric_apply is the identity (all G entries are 1)."""
        from galaga import metric_apply

        alg = Algebra(3)
        rng = np.random.default_rng(42)
        A = Multivector(alg, rng.standard_normal(alg.dim))
        result = metric_apply(A)
        assert np.allclose(result.data, A.data)

    def test_metric_apply_pga_zeroes_null_blades(self):
        """In PGA, metric_apply zeroes blades containing the null vector."""
        from galaga import metric_apply

        pga = Algebra(3, 0, 1)
        e0, e1, e2, e3 = pga.basis_vectors()
        # e0 is null — metric_apply should zero it
        assert np.allclose(metric_apply(e0).data, 0)
        # e1 is not null — should be preserved
        assert np.allclose(metric_apply(e1).data, e1.data)

    def test_antimetric_apply_pga_zeroes_non_null_blades(self):
        """In PGA, antimetric_apply zeroes blades NOT containing the null vector."""
        from galaga import antimetric_apply

        pga = Algebra(3, 0, 1)
        e0, e1, e2, e3 = pga.basis_vectors()
        # e0 contains null vector — antimetric preserves
        result = antimetric_apply(e0)
        assert not np.allclose(result.data, 0)
        # e1 does NOT contain null vector — zeroed
        assert np.allclose(antimetric_apply(e1).data, 0)

    def test_metric_apply_indefinite(self):
        """In Cl(1,3), metric_apply scales by signature products."""
        from galaga import metric_apply

        sta = Algebra(1, 3)
        g0, g1, g2, g3 = sta.basis_vectors()
        # g0 has sig +1, g1 has sig -1
        assert metric_apply(g0).data[1] == pytest.approx(1.0)  # bit 0
        assert metric_apply(g1).data[2] == pytest.approx(-1.0)  # bit 1


class TestAntidotProduct:
    """Tests for antidot_product()."""

    def test_returns_antiscalar(self):
        """antidot_product returns a grade-n multivector."""
        from galaga import antidot_product

        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        result = antidot_product(e1, e1)
        # Only the pseudoscalar component should be nonzero
        assert result.data[alg.dim - 1] != 0 or np.allclose(result.data, 0)
        # All non-PSS components must be zero
        assert np.allclose(result.data[: alg.dim - 1], 0)

    def test_de_morgan_identity(self):
        """antidot(a, b) == complement(metric_inner_product(left_complement(a), left_complement(b)))."""
        from galaga import antidot_product, complement, left_complement, metric_inner_product

        for sig in [(3,), (1, 3)]:
            alg = Algebra(*sig)
            rng = np.random.default_rng(42)
            for _ in range(50):
                a = Multivector(alg, rng.standard_normal(alg.dim))
                b = Multivector(alg, rng.standard_normal(alg.dim))
                lhs = antidot_product(a, b)
                rhs = complement(metric_inner_product(left_complement(a), left_complement(b)))
                assert np.allclose(lhs.data, rhs.data, atol=1e-12), f"Failed for {sig}"

    def test_euclidean_vectors(self):
        """In Euclidean Cl(3,0), antidot of orthogonal vectors is 0."""
        from galaga import antidot_product

        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        # Orthogonal: antidot should be 0
        assert np.allclose(antidot_product(e1, e2).data, 0)
        # Self: should be nonzero antiscalar
        result = antidot_product(e1, e1)
        assert result.data[alg.dim - 1] != 0

    def test_pga_weight_pairing(self):
        """In PGA, antidot product pairs weight components."""
        from galaga import antidot_product

        pga = Algebra(3, 0, 1)
        e0, e1, e2, e3 = pga.basis_vectors()
        # e0 is null — its antimetric entry should be nonzero
        # (𝔾 for e0 = product of sig values NOT in bitmask = sig[1]*sig[2]*sig[3] = 1)
        result = antidot_product(e0, e0)
        assert result.data[pga.dim - 1] == pytest.approx(1.0)
