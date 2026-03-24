"""Coverage gap tests for algebra.py and symbolic.py."""

import pytest
import numpy as np
from ga import (
    Algebra, Multivector, gp, op, grade, reverse, involute, conjugate,
    left_contraction, right_contraction, hestenes_inner, scalar_product,
    scalar, dual, undual, norm, norm2, unit, inverse, ip,
    normalize, normalise, grades,
    commutator, anticommutator,
    even, odd, squared,
    even_grades, odd_grades,
    is_rotor,
)
from ga.symbolic import (
    sym, Expr, Scalar, Gp, Op, Lc, Rc, Hi, Sp, Grade, Reverse,
    Involute, Conjugate, Dual, Undual, Norm, Unit, Inverse, Neg, ScalarMul,
    Add, Sub,
    gp as sgp, op as sop, grade as sgrade, reverse as sreverse,
    involute as sinvolute, conjugate as sconjugate,
    left_contraction as slc, right_contraction as src,
    hestenes_inner as shi, scalar_product as ssp,
    dual as sdual, undual as sundual,
    norm as snorm, unit as sunit, inverse as sinverse,
    ip as sip, normalize as snormalize, normalise as snormalise,
    squared as ssq, even as seven, odd as sodd,
    even_grades as seven_grades, odd_grades as sodd_grades,
)


@pytest.fixture
def cl3():
    return Algebra((1, 1, 1))


# ============================================================
# algebra.py coverage gaps
# ============================================================

class TestNamingPresets:
    def test_gamma_preset(self):
        sta = Algebra((1, -1, -1, -1), names="gamma")
        g0, g1, g2, g3 = sta.basis_vectors()
        assert "γ₀" in str(g0)
        assert "g0" in repr(g0)

    def test_sigma_preset(self):
        alg = Algebra((1, 1, 1), names="sigma")
        s1, s2, s3 = alg.basis_vectors()
        assert "σ₁" in str(s1)
        assert "s1" in repr(s1)

    def test_sigma_xyz_preset(self):
        alg = Algebra((1, 1, 1), names="sigma_xyz")
        sx, sy, sz = alg.basis_vectors()
        assert "σₓ" in str(sx)
        assert "x" in repr(sx)

    def test_custom_names(self):
        alg = Algebra((1, 1), names=(["a", "b"], ["𝐚", "𝐛"]))
        a, b = alg.basis_vectors()
        assert str(a) == "𝐚"
        assert repr(a) == "a"

    def test_custom_names_wrong_length(self):
        with pytest.raises(ValueError, match="must have 2 entries"):
            Algebra((1, 1), names=(["a"], ["𝐚"]))

    def test_unknown_preset(self):
        with pytest.raises(ValueError, match="Unknown naming preset"):
            Algebra((1, 1), names="bogus")

    def test_blade_lookup_custom_names(self):
        sta = Algebra((1, -1, -1, -1), names="gamma")
        b = sta.blade("g0g1")
        e0, e1, _, _ = sta.basis_vectors()
        assert b == e0 ^ e1

    def test_blade_lookup_custom_no_match(self):
        alg = Algebra((1, 1), names=(["a", "b"], ["𝐚", "𝐛"]))
        with pytest.raises(ValueError, match="Invalid blade name"):
            alg.blade("xyz")

    def test_blade_name_custom_unicode(self):
        alg = Algebra((1, 1, 1), names=(["a", "b", "c"], ["𝐚", "𝐛", "𝐜"]))
        a, b, c = alg.basis_vectors()
        # Non-pseudoscalar bivector uses custom names
        assert str(a * b) == "𝐚𝐛"
        assert repr(a * b) == "ab"
        # Pseudoscalar still shows as I/𝑰
        assert str(a * b * c) == "𝑰"


class TestAlgebraProperties:
    def test_I_property(self, cl3):
        assert cl3.I == cl3.pseudoscalar()

    def test_identity_property(self, cl3):
        assert cl3.identity == cl3.scalar(1.0)

    def test_degenerate_metric(self):
        """Algebra with zero in signature (PGA-like)."""
        pga = Algebra((1, 1, 1, 0))
        e1, e2, e3, e0 = pga.basis_vectors()
        # e0^2 = 0
        assert np.isclose(scalar(e0 * e0), 0.0)

    def test_blade_lookup_empty(self, cl3):
        s = cl3.blade("")
        assert s == cl3.scalar(1.0)

    def test_blade_lookup_one(self, cl3):
        s = cl3.blade("1")
        assert s == cl3.scalar(1.0)

    def test_blade_lookup_out_of_range(self, cl3):
        with pytest.raises(ValueError, match="out of range"):
            cl3.blade("e5")

    def test_repr_degenerate(self):
        pga = Algebra((1, 1, 1, 0))
        assert repr(pga) == "Cl(3,0,1)"


class TestMultivectorConvenience:
    def test_inv_property(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = 2 * e1
        assert v * v.inv == cl3.scalar(1.0)

    def test_dag_property(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        assert B.dag == reverse(B)

    def test_sq_property(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        assert B.sq == gp(B, B)

    def test_rsub_scalar(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        r = 5 - e1
        assert r.data[0] == 5.0
        assert r.data[1] == -1.0

    def test_rsub_notimplemented(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        assert e1.__rsub__("bad") is NotImplemented

    def test_truediv_notimplemented(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        assert e1.__truediv__("bad") is NotImplemented

    def test_eq_notimplemented(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        assert e1.__eq__("bad") is NotImplemented

    def test_rmul_notimplemented(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        assert e1.__rmul__("bad") is NotImplemented


class TestIpFunction:
    def test_ip_hestenes(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        assert ip(e1, e1) == hestenes_inner(e1, e1)

    def test_ip_left(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        assert ip(e1, e1 ^ e2, mode="left") == left_contraction(e1, e1 ^ e2)

    def test_ip_right(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        assert ip(e1 ^ e2, e2, mode="right") == right_contraction(e1 ^ e2, e2)

    def test_ip_scalar(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        assert ip(e1, e2, mode="scalar") == scalar_product(e1, e2)

    def test_ip_bad_mode(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        with pytest.raises(ValueError, match="Unknown inner product mode"):
            ip(e1, e1, mode="bogus")


class TestCommutatorAnticommutator:
    def test_commutator(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        c = commutator(e1, e2)
        expected = (gp(e1, e2) - gp(e2, e1)) * 0.5
        assert c == expected

    def test_anticommutator(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        ac = anticommutator(e1, e2)
        expected = (gp(e1, e2) + gp(e2, e1)) * 0.5
        assert ac == expected


# ============================================================
# symbolic.py coverage gaps
# ============================================================

class TestSymbolicOperators:
    def test_radd_scalar(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        expr = 3 + a
        assert str(expr) == "3 + a"

    def test_rsub_scalar(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        expr = 3 - a
        assert str(expr) == "3 - a"

    def test_rmul_scalar(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        expr = 5 * a
        assert str(expr) == "5a"

    def test_truediv(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        expr = a / 2
        assert "0.5" in str(expr)

    def test_truediv_notimplemented(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        assert a.__truediv__("bad") is NotImplemented

    def test_neg_eval(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        result = (-a).eval()
        assert np.allclose(result.data, (-e1).data)

    def test_scalar_mul_eval(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        result = (3 * a).eval()
        assert np.allclose(result.data, (3 * e1).data)


class TestSymbolicBinaryEval:
    def test_rc_eval(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = sym(e1 * e2, "B")
        v = sym(e2, "v")
        result = src(B, v).eval()
        expected = right_contraction(e1 * e2, e2)
        assert np.allclose(result.data, expected.data)

    def test_hi_eval(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        result = shi(a, b).eval()
        expected = hestenes_inner(e1, e2)
        assert np.allclose(result.data, expected.data)

    def test_sp_eval(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e1, "b")
        result = ssp(a, b).eval()
        expected = scalar_product(e1, e1)
        assert np.allclose(result.data, expected.data)

    def test_op_eval(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        result = sop(a, b).eval()
        expected = op(e1, e2)
        assert np.allclose(result.data, expected.data)

    def test_sub_eval(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        result = (a - b).eval()
        assert np.allclose(result.data, (e1 - e2).data)

    def test_add_eval(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        result = (a + b).eval()
        assert np.allclose(result.data, (e1 + e2).data)


class TestSymbolicUnaryEval:
    def test_involute_eval(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        result = sinvolute(v).eval()
        expected = involute(e1)
        assert np.allclose(result.data, expected.data)

    def test_conjugate_eval(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        result = sconjugate(v).eval()
        expected = conjugate(e1)
        assert np.allclose(result.data, expected.data)

    def test_undual_eval(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        result = sundual(v).eval()
        expected = undual(e1)
        assert np.allclose(result.data, expected.data)

    def test_unit_eval(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        v = sym(cl3.vector([3, 4, 0]), "v")
        result = sunit(v).eval()
        expected = unit(cl3.vector([3, 4, 0]))
        assert np.allclose(result.data, expected.data)

    def test_inverse_eval(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(2 * e1, "v")
        result = sinverse(v).eval()
        expected = inverse(2 * e1)
        assert np.allclose(result.data, expected.data)


class TestSymbolicIp:
    def test_ip_hestenes(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        assert str(sip(a, b)) == "a·b"

    def test_ip_left(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        assert str(sip(a, b, mode="left")) == "a⌋b"

    def test_ip_right(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        assert str(sip(a, b, mode="right")) == "a⌊b"

    def test_ip_scalar(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        assert str(sip(a, b, mode="scalar")) == "a∗b"

    def test_ip_bad_mode(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        with pytest.raises(ValueError, match="Unknown inner product mode"):
            sip(a, b, mode="bogus")

    def test_ip_numeric_fallback(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        result = sip(e1, e1)
        assert not isinstance(result, Expr)

    def test_ip_numeric_modes(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        assert sip(e1, e1 ^ e2, mode="left") == left_contraction(e1, e1 ^ e2)
        assert sip(e1 ^ e2, e1, mode="right") == right_contraction(e1 ^ e2, e1)
        assert sip(e1, e2, mode="scalar") == scalar_product(e1, e2)


class TestSymbolicNormalize:
    def test_normalize_alias(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(snormalize(v)) == "v̂"
        assert str(snormalise(v)) == "v̂"

    def test_normalize_numeric_fallback(self, cl3):
        v = cl3.vector([3, 4, 0])
        result = snormalize(v)
        assert not isinstance(result, Expr)


class TestSymbolicConvenienceProps:
    def test_inv_property(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(v.inv) == "v⁻¹"

    def test_dag_property(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        assert str(R.dag) == "R̃"

    def test_sq_property(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        assert str(R.sq) == "R²"


class TestSymbolicMixedInputs:
    """Test that mixing Multivector and Expr works via _ensure_expr."""

    def test_gp_mv_and_expr(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        # Multivector * Expr should work
        result = sgp(e1, R)
        assert isinstance(result, Expr)

    def test_op_mv_and_expr(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        result = sop(e2, a)
        assert isinstance(result, Expr)


class TestScalarExpr:
    def test_scalar_str(self):
        s = Scalar(3.0)
        assert str(s) == "3"

    def test_scalar_eval_raises(self):
        s = Scalar(3.0)
        with pytest.raises(TypeError):
            s.eval()


class TestUnitLongName:
    def test_unit_long_name(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "velocity")
        assert str(sunit(v)) == "velocity/‖velocity‖"


class TestRemainingAlgebraGaps:
    def test_mv_sub_scalar(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        r = (3 + e1) - 1
        assert r.data[0] == 2.0
        assert r.data[1] == 1.0

    def test_mv_eq_scalar(self, cl3):
        s = cl3.scalar(5.0)
        assert s == 5.0
        assert not (s == 3.0)

    def test_grade_out_of_range(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        r = grade(e1, -1)
        assert np.allclose(r.data, 0)
        r = grade(e1, 99)
        assert np.allclose(r.data, 0)

    def test_unit_zero_raises(self, cl3):
        with pytest.raises(ValueError, match="Cannot normalize"):
            unit(cl3.scalar(0))


class TestRemainingSymbolicGaps:
    def test_sym_repr(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        s = sym(e1, "v")
        assert repr(s) == "Sym(v)"

    def test_expr_or_operator(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e1 ^ e2, "B")
        result = a | b
        assert str(result) == "a⌋B"

    def test_expr_mul_with_expr(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        result = a * b
        assert str(result) == "ab"

    def test_symbolic_numeric_fallbacks(self, cl3):
        """Test all symbolic functions with plain Multivectors."""
        e1, e2, _ = cl3.basis_vectors()
        # These should all return Multivector, not Expr
        assert not isinstance(sop(e1, e2), Expr)
        assert not isinstance(slc(e1, e1 ^ e2), Expr)
        assert not isinstance(src(e1 ^ e2, e1), Expr)
        assert not isinstance(shi(e1, e2), Expr)
        assert not isinstance(ssp(e1, e2), Expr)
        assert not isinstance(sinvolute(e1), Expr)
        assert not isinstance(sconjugate(e1), Expr)
        assert not isinstance(sdual(e1), Expr)
        assert not isinstance(sundual(e1), Expr)
        assert not isinstance(sinverse(e1), Expr)


class TestEvenOddSquared:
    """Tests for even(), odd(), squared() numeric functions."""

    def test_even(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        mv = 1 + 2*e1 + 3*(e1^e2)
        r = even(mv)
        assert np.isclose(r.data[0], 1.0)   # scalar
        assert np.isclose(r.data[1], 0.0)   # e1 (odd)
        assert np.isclose(r.data[3], 3.0)   # e12

    def test_odd(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        mv = 1 + 2*e1 + 3*(e1^e2)
        r = odd(mv)
        assert np.isclose(r.data[0], 0.0)
        assert np.isclose(r.data[1], 2.0)
        assert np.isclose(r.data[3], 0.0)

    def test_even_odd_sum(self, cl3):
        e1, e2, e3 = cl3.basis_vectors()
        mv = 1 + 2*e1 + 3*(e1^e2) + 4*(e1^e2^e3)
        assert even(mv) + odd(mv) == mv

    def test_squared(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        v = e1 + e2
        assert squared(v) == gp(v, v)

    def test_squared_bivector(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        assert squared(B) == cl3.scalar(-1.0)


class TestSymbolicEvenOddSquared:
    """Tests for symbolic even(), odd(), squared()."""

    def test_squared_str(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1*e2, "R")
        assert str(ssq(R)) == "R²"

    def test_squared_eval(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1*e2, "R")
        result = ssq(R).eval()
        expected = gp(e1*e2, e1*e2)
        assert np.allclose(result.data, expected.data)

    def test_squared_numeric_fallback(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        result = ssq(e1)
        assert not isinstance(result, Expr)

    def test_even_str(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(seven(v)) == "⟨v⟩₊"

    def test_even_eval(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        mv = sym(1 + 2*e1 + 3*(e1^e2), "A")
        result = seven(mv).eval()
        expected = even(1 + 2*e1 + 3*(e1^e2))
        assert np.allclose(result.data, expected.data)

    def test_even_numeric_fallback(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        result = seven(e1)
        assert not isinstance(result, Expr)

    def test_odd_str(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(sodd(v)) == "⟨v⟩₋"

    def test_odd_eval(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        mv = sym(1 + 2*e1 + 3*(e1^e2), "A")
        result = sodd(mv).eval()
        expected = odd(1 + 2*e1 + 3*(e1^e2))
        assert np.allclose(result.data, expected.data)

    def test_odd_numeric_fallback(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        result = sodd(e1)
        assert not isinstance(result, Expr)


class TestGetitem:
    def test_grade_projection_getitem(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        mv = 3 + 2*e1 + (e1^e2)
        assert mv[0] == grade(mv, 0)
        assert mv[1] == grade(mv, 1)
        assert mv[2] == grade(mv, 2)

    def test_getitem_out_of_range(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        r = e1[5]
        assert np.allclose(r.data, 0)


class TestRotorFromPlaneAngle:
    def test_90_degree_rotation(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        R = cl3.rotor_from_plane_angle(B, np.pi / 2)
        v_rot = R * e1 * ~R
        assert np.allclose(v_rot.data, e2.data, atol=1e-12)

    def test_180_degree_rotation(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        R = cl3.rotor_from_plane_angle(B, np.pi)
        v_rot = R * e1 * ~R
        assert np.allclose(v_rot.data, (-e1).data, atol=1e-12)

    def test_zero_rotation(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        R = cl3.rotor_from_plane_angle(B, 0)
        v_rot = R * e1 * ~R
        assert np.allclose(v_rot.data, e1.data, atol=1e-12)

    def test_rotor_is_rotor(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        R = cl3.rotor_from_plane_angle(B, 1.23)
        assert is_rotor(R)


class TestIsRotor:
    def test_unit_rotor(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        R = cl3.rotor_from_plane_angle(e1^e2, 0.5)
        assert is_rotor(R)

    def test_identity_is_rotor(self, cl3):
        assert is_rotor(cl3.identity)

    def test_vector_not_rotor(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        assert not is_rotor(e1)

    def test_scaled_rotor_not_rotor(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        R = cl3.rotor_from_plane_angle(e1^e2, 0.5)
        assert not is_rotor(2 * R)


class TestEvenOddGradesRenamed:
    def test_even_grades(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        mv = 1 + 2*e1 + 3*(e1^e2)
        assert even_grades(mv) == even(mv)

    def test_odd_grades(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        mv = 1 + 2*e1 + 3*(e1^e2)
        assert odd_grades(mv) == odd(mv)

    def test_grade_even_string(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        mv = 1 + 2*e1 + 3*(e1^e2)
        assert grade(mv, "even") == even_grades(mv)

    def test_grade_odd_string(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        mv = 1 + 2*e1 + 3*(e1^e2)
        assert grade(mv, "odd") == odd_grades(mv)


class TestSymbolicGradeEvenOdd:
    def test_sym_grade_even(self, cl3):
        from ga.symbolic import grade as sgrade
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(sgrade(v, "even")) == "⟨v⟩₊"

    def test_sym_grade_odd(self, cl3):
        from ga.symbolic import grade as sgrade
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(sgrade(v, "odd")) == "⟨v⟩₋"

    def test_sym_even_grades(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(seven_grades(v)) == "⟨v⟩₊"

    def test_sym_odd_grades(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(sodd_grades(v)) == "⟨v⟩₋"


class TestLatex:
    """Tests for .latex() output on all expression types."""

    def test_sym(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        assert sym(e1, "v").latex() == "v"

    def test_gp(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1*e2, "R")
        v = sym(e1, "v")
        assert (R * v).latex() == "R v"

    def test_sandwich_grade(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        from ga.symbolic import grade as sgrade
        R = sym(e1*e2, "R")
        v = sym(e1, "v")
        assert sgrade(R * v * ~R, 1).latex() == r"\langle R v \tilde{R} \rangle_{1}"

    def test_wedge(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "a"), sym(e2, "b")
        assert (a ^ b).latex() == r"a \wedge b"

    def test_left_contraction(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "a"), sym(e2, "b")
        assert slc(a, b).latex() == r"a \;\lrcorner\; b"

    def test_right_contraction(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "a"), sym(e2, "b")
        assert src(a, b).latex() == r"a \;\llcorner\; b"

    def test_hestenes_inner(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "A"), sym(e2, "B")
        assert shi(a, b).latex() == r"A \cdot B"

    def test_scalar_product(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "A"), sym(e2, "B")
        assert ssp(a, b).latex() == "A * B"

    def test_reverse(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1*e2, "R")
        assert (~R).latex() == r"\tilde{R}"

    def test_involute(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert sinvolute(v).latex() == r"v^\dagger"

    def test_conjugate(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert sconjugate(v).latex() == r"\bar{v}"

    def test_dual(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert sdual(v).latex() == "v^*"

    def test_undual(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert sundual(v).latex() == "v^{*^{-1}}"

    def test_norm(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert snorm(v).latex() == r"\lVert v \rVert"

    def test_unit(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert sunit(v).latex() == r"\hat{v}"

    def test_inverse(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert sinverse(v).latex() == "v^{-1}"

    def test_squared(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1*e2, "R")
        assert ssq(R).latex() == "R^2"

    def test_even(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert seven(v).latex() == r"\langle v \rangle_{\text{even}}"

    def test_odd(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert sodd(v).latex() == r"\langle v \rangle_{\text{odd}}"

    def test_add(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "a"), sym(e2, "b")
        assert (a + b).latex() == "a + b"

    def test_sub(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "a"), sym(e2, "b")
        assert (a - b).latex() == "a - b"

    def test_neg(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        assert (-a).latex() == "-a"

    def test_scalar_mul(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        assert (3 * a).latex() == "3 a"
        assert (-1 * a).latex() == "-a"

    def test_parens(self, cl3):
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "a"), sym(e2, "b")
        R = sym(e1*e2, "R")
        assert ((a + b) * R).latex() == r"\left(a + b\right) R"

    def test_repr_latex(self, cl3):
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert v._repr_latex_() == "$v$"
        assert (~v)._repr_latex_() == r"$\tilde{v}$"
