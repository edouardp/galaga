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

    def test_cached_matrix_is_read_only(self):
        """Callers cannot mutate the cached algebra-level metric."""
        G = Algebra(3).extended_metric_matrix()
        with pytest.raises(ValueError, match="read-only"):
            G[0, 0] = 2


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

    def test_cached_matrix_is_read_only(self):
        """Callers cannot mutate the cached algebra-level antimetric."""
        Gbar = Algebra(3).metric_antiexomorphism_matrix()
        with pytest.raises(ValueError, match="read-only"):
            Gbar[0, 0] = 2


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


class TestHodgeDuals:
    """Tests for right_hodge_dual() and left_hodge_dual()."""

    def test_hodge_identity_same_grade(self):
        """op(A, right_hodge_dual(B)) == metric_inner_product(A, B) * I for same-grade."""
        from galaga import right_hodge_dual

        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        I = alg.I

        # Grade 1: vectors
        for a, b in [(e1, e1), (e1, e2), (e2, e3)]:
            lhs = op(a, right_hodge_dual(b))
            rhs = metric_inner_product(a, b).data[0] * I
            assert np.allclose(lhs.data, rhs.data, atol=1e-12)

        # Grade 2: bivectors
        e12 = e1 * e2
        e13 = e1 * e3
        e23 = e2 * e3
        for a, b in [(e12, e12), (e12, e23), (e13, e23)]:
            lhs = op(a, right_hodge_dual(b))
            rhs = metric_inner_product(a, b).data[0] * I
            assert np.allclose(lhs.data, rhs.data, atol=1e-12)

    def test_nondegenerate_equals_gp_reverse_I(self):
        """In non-degenerate algebras, right_hodge_dual(A) == gp(reverse(A), I)."""
        from galaga import gp, right_hodge_dual

        for sig in [(3,), (1, 3), (2, 1)]:
            alg = Algebra(*sig)
            I = alg.I
            rng = np.random.default_rng(42)
            for _ in range(50):
                A = Multivector(alg, rng.standard_normal(alg.dim))
                lhs = right_hodge_dual(A)
                rhs = gp(reverse(A), I)
                assert np.allclose(lhs.data, rhs.data, atol=1e-12), f"Failed for {sig}"

    def test_pga_works_where_dual_raises(self):
        """right_hodge_dual works in PGA where dual() raises."""
        from galaga import dual, right_hodge_dual

        pga = Algebra(3, 0, 1)
        e0, e1, e2, e3 = pga.basis_vectors()

        # dual() should raise for PGA
        with pytest.raises(ValueError):
            dual(e1)

        # right_hodge_dual should work fine
        result = right_hodge_dual(e1)
        assert not np.allclose(result.data, 0)

    def test_double_dual_formula(self):
        """right_hodge_dual(right_hodge_dual(A)) == (-1)^(gr*ag) * det(g) * A."""
        import operator
        from functools import reduce

        from galaga import right_hodge_dual

        alg = Algebra(3)  # det = 1
        det = reduce(operator.mul, alg.signature, 1)
        e1, e2, e3 = alg.basis_vectors()

        # For a grade-1 blade in n=3: gr=1, ag=2, (-1)^(1*2)=+1
        dd = right_hodge_dual(right_hodge_dual(e1))
        expected = ((-1) ** (1 * 2)) * det * e1
        assert np.allclose(dd.data, expected.data, atol=1e-12)

        # For a grade-2 blade in n=3: gr=2, ag=1, (-1)^(2*1)=+1
        e12 = e1 * e2
        dd2 = right_hodge_dual(right_hodge_dual(e12))
        expected2 = ((-1) ** (2 * 1)) * det * e12
        assert np.allclose(dd2.data, expected2.data, atol=1e-12)

    def test_left_hodge_dual_identity(self):
        """op(left_hodge_dual(A), B) == metric_inner_product(A, B) * I for same-grade."""
        from galaga import left_hodge_dual

        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        I = alg.I

        for a, b in [(e1, e1), (e1, e2), (e2, e3)]:
            lhs = op(left_hodge_dual(a), b)
            rhs = metric_inner_product(a, b).data[0] * I
            assert np.allclose(lhs.data, rhs.data, atol=1e-12)

    def test_euclidean_vector_duals(self):
        """In Cl(3,0): hodge dual of e1 is e23, of e2 is -e13, of e3 is e12."""
        from galaga import right_hodge_dual

        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        _e12 = e1 * e2
        e13 = e1 * e3
        e23 = e2 * e3

        assert np.allclose(right_hodge_dual(e1).data, e23.data, atol=1e-12)
        assert np.allclose(right_hodge_dual(e2).data, -e13.data, atol=1e-12)


class TestAntiwedge:
    """Tests for antiwedge() sign convention audit."""

    def test_antiwedge_is_regressive_product(self):
        """antiwedge is an alias for regressive_product."""
        from galaga import antiwedge, regressive_product

        assert antiwedge is regressive_product

    def test_antiwedge_matches_rga_definition(self):
        """antiwedge(A,B) == complement(op(left_complement(A), left_complement(B)))."""
        from galaga import antiwedge, complement, left_complement

        for sig in [(3,), (1, 3), (3, 0, 1)]:
            alg = Algebra(*sig)
            rng = np.random.default_rng(42)
            for _ in range(50):
                a = Multivector(alg, rng.standard_normal(alg.dim))
                b = Multivector(alg, rng.standard_normal(alg.dim))
                lhs = antiwedge(a, b)
                rhs = complement(op(left_complement(a), left_complement(b)))
                assert np.allclose(lhs.data, rhs.data, atol=1e-12), f"Failed for {sig}"

    def test_antiwedge_exhaustive_basis_cl3(self):
        """Exhaustive check on all basis blade pairs in Cl(3,0)."""
        from galaga import antiwedge, complement, left_complement

        alg = Algebra(3)
        for i in range(1, alg.dim):
            for j in range(1, alg.dim):
                a = Multivector(alg, np.eye(alg.dim)[i])
                b = Multivector(alg, np.eye(alg.dim)[j])
                lhs = antiwedge(a, b)
                rhs = complement(op(left_complement(a), left_complement(b)))
                assert np.allclose(lhs.data, rhs.data, atol=1e-12)

    def test_antiwedge_pga_meet(self):
        """In PGA, antiwedge of two points (trivectors) gives a line (bivector)."""
        from galaga import antiwedge

        pga = Algebra(3, 0, 1)
        e0, e1, e2, e3 = pga.basis_vectors()
        # Points in PGA are grade-3 (trivectors): p = e_i ^ e_j ^ e_k
        # Point at origin: e1^e2^e3
        p1 = e1 * e2 * e3  # point at origin
        p2 = e0 * e1 * e2  # a different point
        # Regressive of two grade-3 in n=4: result grade = 3+3-4 = 2 (a line)
        line = antiwedge(p1, p2)
        # Should be a grade-2 (bivector = line in PGA), non-zero
        assert not np.allclose(line.data, 0)


class TestAntireverse:
    """Tests for antireverse()."""

    def test_sign_pattern(self):
        """Antireverse sign follows (-1)^(ag*(ag-1)/2) where ag = n - grade."""
        from galaga import antireverse

        alg = Algebra(4, 1)  # n=5 for interesting antigrade pattern
        n = alg.n
        for k in range(n + 1):
            ag = n - k
            expected_sign = (-1) ** (ag * (ag - 1) // 2)
            # Create a pure grade-k blade
            # Find first bitmask with popcount k
            for idx in range(alg.dim):
                if bin(idx).count("1") == k:
                    data = np.zeros(alg.dim)
                    data[idx] = 1.0
                    blade = Multivector(alg, data)
                    result = antireverse(blade)
                    assert result.data[idx] == pytest.approx(expected_sign), (
                        f"grade={k}, ag={ag}, expected sign={expected_sign}"
                    )
                    break

    def test_antireverse_vs_reverse_complementary(self):
        """Antireverse and reverse have complementary sign patterns."""
        from galaga import antireverse

        alg = Algebra(3)
        # In n=3: reverse sign for grade k is (-1)^(k(k-1)/2)
        # antireverse sign for grade k is (-1)^((3-k)(3-k-1)/2)
        # These are NOT the same in general
        e1, e2, e3 = alg.basis_vectors()
        e12 = e1 * e2
        e123 = e1 * e2 * e3

        # grade 1: ag=2, sign = (-1)^(2*1/2) = -1
        assert antireverse(e1).data[1] == pytest.approx(-1.0)
        # grade 2: ag=1, sign = (-1)^(1*0/2) = +1
        assert antireverse(e12).data[3] == pytest.approx(1.0)
        # grade 3: ag=0, sign = (-1)^(0) = +1
        assert antireverse(e123).data[7] == pytest.approx(1.0)

    def test_antireverse_scalar(self):
        """Antireverse of scalar: ag = n, sign = (-1)^(n(n-1)/2)."""
        from galaga import antireverse

        alg = Algebra(3)  # n=3, ag=3, sign = (-1)^(3*2/2) = (-1)^3 = -1
        s = alg.scalar(5.0)
        result = antireverse(s)
        assert result.data[0] == pytest.approx(-5.0)


class TestGeometricAntiproduct:
    """Tests for geometric_antiproduct()."""

    def test_de_morgan_with_gp(self):
        """geometric_antiproduct(A,B) == complement(gp(left_complement(A), left_complement(B)))."""
        from galaga import complement, geometric_antiproduct, gp, left_complement

        for sig in [(3,), (1, 3), (3, 0, 1)]:
            alg = Algebra(*sig)
            rng = np.random.default_rng(42)
            for _ in range(50):
                a = Multivector(alg, rng.standard_normal(alg.dim))
                b = Multivector(alg, rng.standard_normal(alg.dim))
                lhs = geometric_antiproduct(a, b)
                rhs = complement(gp(left_complement(a), left_complement(b)))
                assert np.allclose(lhs.data, rhs.data, atol=1e-12), f"Failed for {sig}"

    def test_antiproduct_of_pseudoscalars(self):
        """The antiproduct of two pseudoscalars should relate to the scalar."""
        from galaga import geometric_antiproduct

        alg = Algebra(3)
        I = alg.I
        # gap(I, I) should be a scalar (complement of gp(lc(I), lc(I)))
        result = geometric_antiproduct(I, I)
        # I is grade-n, left_complement(I) is grade-0 (scalar)
        # gp(scalar, scalar) = scalar, complement(scalar) = grade-n
        # Actually: lc(I) = uncomplement(I), which for the PSS gives +/-1 scalar
        assert not np.allclose(result.data, 0)

    def test_antiproduct_vectors_cl3(self):
        """Geometric antiproduct of vectors in Cl(3,0)."""
        from galaga import geometric_antiproduct

        alg = Algebra(3)
        e1, e2, _ = alg.basis_vectors()
        result = geometric_antiproduct(e1, e2)
        # Should be nonzero
        assert not np.allclose(result.data, 0)


class TestTranswedge:
    """Tests for transwedge(A, B, k) — experimental."""

    def test_order_zero_is_wedge(self):
        """transwedge(A, B, 0) == op(A, B)."""
        from galaga import transwedge

        alg = Algebra(3)
        rng = np.random.default_rng(42)
        for _ in range(50):
            a = Multivector(alg, rng.standard_normal(alg.dim))
            b = Multivector(alg, rng.standard_normal(alg.dim))
            lhs = transwedge(a, b, 0)
            rhs = op(a, b)
            assert np.allclose(lhs.data, rhs.data, atol=1e-11), "Order 0 != wedge"

    def test_signed_sum_is_gp(self):
        """sum_k (-1)^(k(k-1)/2) * transwedge(a, b, k) == gp(a, b)."""
        from galaga import gp, transwedge

        for sig in [(3,), (1, 3)]:
            alg = Algebra(*sig)
            n = alg.n
            rng = np.random.default_rng(77)
            for _ in range(20):
                a = Multivector(alg, rng.standard_normal(alg.dim))
                b = Multivector(alg, rng.standard_normal(alg.dim))
                total = np.zeros(alg.dim)
                for k in range(n + 1):
                    sign = (-1) ** (k * (k - 1) // 2)
                    tw = transwedge(a, b, k)
                    total += sign * tw.data
                expected = gp(a, b)
                assert np.allclose(total, expected.data, atol=1e-10), f"Signed sum != gp for {sig}"

    def test_vectors_order_one_is_inner_product(self):
        """For vectors a, b: transwedge(a, b, 1) == metric_inner_product(a, b)."""
        from galaga import transwedge

        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        # e1 dot e1 = 1
        tw = transwedge(e1, e1, 1)
        assert tw.data[0] == pytest.approx(1.0)
        # e1 dot e2 = 0
        tw2 = transwedge(e1, e2, 1)
        assert np.allclose(tw2.data, 0, atol=1e-12)

    def test_zero_when_k_exceeds_grade(self):
        """transwedge(A, B, k) == 0 when k > gr(A) or k > gr(B)."""
        from galaga import transwedge

        alg = Algebra(3)
        e1, e2, _ = alg.basis_vectors()
        # e1 is grade 1, so k=2 should give zero
        tw = transwedge(e1, e2, 2)
        assert np.allclose(tw.data, 0, atol=1e-12)

    def test_negative_k_raises(self):
        """A transwedge order is a non-negative integer."""
        from galaga import transwedge

        alg = Algebra(3)
        e1, _, _ = alg.basis_vectors()
        with pytest.raises(ValueError, match="non-negative"):
            transwedge(e1, e1, -1)

    def test_pga_signed_sum(self):
        """Signed sum reconstructs GP even in degenerate PGA."""
        from galaga import gp, transwedge

        pga = Algebra(3, 0, 1)
        n = pga.n
        rng = np.random.default_rng(99)
        for _ in range(10):
            a = Multivector(pga, rng.standard_normal(pga.dim))
            b = Multivector(pga, rng.standard_normal(pga.dim))
            total = np.zeros(pga.dim)
            for k in range(n + 1):
                sign = (-1) ** (k * (k - 1) // 2)
                tw = transwedge(a, b, k)
                total += sign * tw.data
            expected = gp(a, b)
            assert np.allclose(total, expected.data, atol=1e-10), "PGA signed sum != gp"


class TestBulkWeightDuals:
    """Tests for bulk_part, weight_part, right_weight_dual, left_weight_dual."""

    def test_bulk_part_is_metric_apply(self):
        """bulk_part is an alias for metric_apply."""
        from galaga import bulk_part, metric_apply

        alg = Algebra(3, 0, 1)
        rng = np.random.default_rng(42)
        A = Multivector(alg, rng.standard_normal(alg.dim))
        assert np.allclose(bulk_part(A).data, metric_apply(A).data)

    def test_weight_part_is_antimetric_apply(self):
        """weight_part is an alias for antimetric_apply."""
        from galaga import antimetric_apply, weight_part

        alg = Algebra(3, 0, 1)
        rng = np.random.default_rng(42)
        A = Multivector(alg, rng.standard_normal(alg.dim))
        assert np.allclose(weight_part(A).data, antimetric_apply(A).data)

    def test_pga_bulk_zeroes_null_blades(self):
        """In PGA, bulk_part zeroes blades containing the null vector."""
        from galaga import bulk_part

        pga = Algebra(3, 0, 1)
        e0, e1, e2, e3 = pga.basis_vectors()
        assert np.allclose(bulk_part(e0).data, 0)
        assert np.allclose(bulk_part(e1).data, e1.data)

    def test_pga_weight_zeroes_non_null_blades(self):
        """In PGA, weight_part zeroes blades NOT containing the null vector."""
        from galaga import weight_part

        pga = Algebra(3, 0, 1)
        e0, e1, e2, e3 = pga.basis_vectors()
        assert not np.allclose(weight_part(e0).data, 0)
        assert np.allclose(weight_part(e1).data, 0)

    def test_right_weight_dual_definition(self):
        """right_weight_dual(A) == complement(antimetric_apply(A))."""
        from galaga import antimetric_apply, complement, right_weight_dual

        alg = Algebra(3, 0, 1)
        rng = np.random.default_rng(42)
        for _ in range(20):
            A = Multivector(alg, rng.standard_normal(alg.dim))
            lhs = right_weight_dual(A)
            rhs = complement(antimetric_apply(A))
            assert np.allclose(lhs.data, rhs.data, atol=1e-12)

    def test_left_weight_dual_definition(self):
        """left_weight_dual(A) == left_complement(antimetric_apply(A))."""
        from galaga import antimetric_apply, left_complement, left_weight_dual

        alg = Algebra(3, 0, 1)
        rng = np.random.default_rng(42)
        for _ in range(20):
            A = Multivector(alg, rng.standard_normal(alg.dim))
            lhs = left_weight_dual(A)
            rhs = left_complement(antimetric_apply(A))
            assert np.allclose(lhs.data, rhs.data, atol=1e-12)

    def test_euclidean_bulk_is_identity(self):
        """In Euclidean Cl(3,0), bulk_part is the identity (all G entries are 1)."""
        from galaga import bulk_part

        alg = Algebra(3)
        rng = np.random.default_rng(42)
        A = Multivector(alg, rng.standard_normal(alg.dim))
        assert np.allclose(bulk_part(A).data, A.data)

    def test_euclidean_weight_is_identity(self):
        """In Euclidean Cl(3,0), weight_part is also identity (all G-bar entries are 1)."""
        from galaga import weight_part

        alg = Algebra(3)
        rng = np.random.default_rng(42)
        A = Multivector(alg, rng.standard_normal(alg.dim))
        assert np.allclose(weight_part(A).data, A.data)
