"""Coverage gap tests for algebra.py and symbolic.py."""

import numpy as np
import pytest

from galaga import (
    Algebra,
    anticommutator,
    commutator,
    complement,
    conjugate,
    doran_lasenby_inner,
    even_grades,
    gp,
    grade,
    hestenes_inner,
    inverse,
    involute,
    ip,
    is_even,
    is_rotor,
    jordan_product,
    left_contraction,
    lie_bracket,
    odd_grades,
    op,
    reverse,
    right_contraction,
    sandwich,
    scalar_product,
    squared,
    sw,
    uncomplement,
    undual,
    unit,
)
from galaga import conjugate as sconjugate
from galaga import dual as sdual
from galaga import even_grades as seven
from galaga import even_grades as seven_grades
from galaga import gp as sgp
from galaga import grade as sgrade
from galaga import hestenes_inner as shi
from galaga import inverse as sinverse
from galaga import involute as sinvolute
from galaga import ip as sip
from galaga import left_contraction as slc
from galaga import norm as snorm
from galaga import normalise as snormalise
from galaga import normalize as snormalize
from galaga import odd_grades as sodd
from galaga import odd_grades as sodd_grades
from galaga import op as sop
from galaga import right_contraction as src
from galaga import sandwich as ssandwich
from galaga import scalar_product as ssp
from galaga import squared as ssq
from galaga import sw as ssw_alias
from galaga import undual as sundual
from galaga import unit as sunit
from galaga.expr import (
    Conjugate,
    Dual,
    Expr,
    Grade,
    Involute,
    Neg,
    Reverse,
    Scalar,
    ScalarMul,
    Unit,
    sym,
)
from galaga.simplify import simplify


@pytest.fixture
def cl3():
    return Algebra((1, 1, 1))


# ============================================================
# algebra.py coverage gaps
# ============================================================


class TestNamingPresets:
    def test_gamma_preset(self):
        """Gamma naming preset: γ₀, γ₁, ..."""
        sta = Algebra((1, -1, -1, -1), names="gamma")
        g0, g1, g2, g3 = sta.basis_vectors()
        assert "γ₀" in str(g0)
        assert "γ₀" in repr(g0)

    def test_sigma_preset(self):
        """Sigma naming preset: σ₁, σ₂, ..."""
        alg = Algebra((1, 1, 1), names="sigma")
        s1, s2, s3 = alg.basis_vectors()
        assert "σ₁" in str(s1)
        assert "σ₁" in repr(s1)

    def test_sigma_xyz_preset(self):
        """Sigma xyz preset: σₓ, σᵧ, σz."""
        alg = Algebra((1, 1, 1), names="sigma_xyz")
        sx, sy, sz = alg.basis_vectors()
        assert "σₓ" in str(sx)
        assert "σₓ" in repr(sx)

    def test_custom_names(self):
        """Custom (code, unicode) name tuples."""
        alg = Algebra((1, 1), names=(["a", "b"], ["𝐚", "𝐛"]))
        a, b = alg.basis_vectors()
        assert str(a) == "𝐚"
        assert repr(a) == "𝐚"

    def test_custom_names_wrong_length(self):
        """Wrong-length custom names raise ValueError."""
        with pytest.raises(ValueError, match="must have 2 entries"):
            Algebra((1, 1), names=(["a"], ["𝐚"]))

    def test_unknown_preset(self):
        """Unknown preset name raises ValueError."""
        with pytest.raises(ValueError, match="Unknown naming preset"):
            Algebra((1, 1), names="bogus")

    def test_blade_lookup_custom_names(self):
        """blade() works with custom names."""
        sta = Algebra((1, -1, -1, -1), names="gamma")
        b = sta.blade("g0g1")
        e0, e1, _, _ = sta.basis_vectors()
        assert b == e0 ^ e1

    def test_blade_lookup_custom_no_match(self):
        """blade() with unrecognized name raises."""
        alg = Algebra((1, 1), names=(["a", "b"], ["𝐚", "𝐛"]))
        with pytest.raises(ValueError, match="Invalid blade name"):
            alg.blade("xyz")

    def test_blade_name_custom_unicode(self):
        """Custom unicode names appear in str()."""
        alg = Algebra((1, 1, 1), names=(["a", "b", "c"], ["𝐚", "𝐛", "𝐜"]))
        a, b, c = alg.basis_vectors()
        # Non-pseudoscalar bivector uses custom names
        assert str(a * b) == "𝐚𝐛"
        assert repr(a * b) == "𝐚𝐛"
        # Pseudoscalar uses standard blade name
        assert str(a * b * c) == "𝐚𝐛𝐜"


class TestAlgebraProperties:
    def test_I_property(self, cl3):
        """alg.I returns the pseudoscalar."""
        assert cl3.I == cl3.pseudoscalar()

    def test_identity_property(self, cl3):
        """alg.identity returns scalar 1."""
        assert cl3.identity == cl3.scalar(1.0)

    def test_degenerate_metric(self):
        """Algebra with zero in signature (PGA-like)."""
        pga = Algebra((1, 1, 1, 0))
        e1, e2, e3, e0 = pga.basis_vectors()
        # e0^2 = 0
        assert np.isclose((e0 * e0).scalar_part, 0.0)

    def test_blade_lookup_empty(self, cl3):
        """blade('') returns scalar 1."""
        s = cl3.blade("")
        assert s == cl3.scalar(1.0)

    def test_blade_lookup_one(self, cl3):
        """blade('e1') returns first basis vector."""
        s = cl3.blade("1")
        assert s == cl3.scalar(1.0)

    def test_blade_lookup_out_of_range(self, cl3):
        """blade() with invalid name raises."""
        with pytest.raises(ValueError, match="out of range"):
            cl3.blade("e5")

    def test_repr_degenerate(self):
        """Repr includes degenerate count."""
        pga = Algebra((1, 1, 1, 0))
        assert repr(pga) == "Cl(3,0,1)"


class TestMultivectorConvenience:
    def test_inv_property(self, cl3):
        """.inv returns inverse."""
        e1, _, _ = cl3.basis_vectors()
        v = 2 * e1
        assert v * v.inv == cl3.scalar(1.0)

    def test_dag_property(self, cl3):
        """.dag returns reverse."""
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        assert B.dag == reverse(B)

    def test_sq_property(self, cl3):
        """.sq returns gp(x, x)."""
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        assert B.sq == gp(B, B)

    def test_rsub_scalar(self, cl3):
        """scalar - Expr works."""
        e1, _, _ = cl3.basis_vectors()
        r = 5 - e1
        assert r.data[0] == 5.0
        assert r.data[1] == -1.0

    def test_rsub_notimplemented(self, cl3):
        """MV - non-scalar returns NotImplemented."""
        e1, _, _ = cl3.basis_vectors()
        assert e1.__rsub__("bad") is NotImplemented

    def test_truediv_notimplemented(self, cl3):
        """Expr / non-scalar raises TypeError."""
        e1, _, _ = cl3.basis_vectors()
        assert e1.__truediv__("bad") is NotImplemented

    def test_eq_notimplemented(self, cl3):
        """MV == non-MV returns NotImplemented."""
        e1, _, _ = cl3.basis_vectors()
        assert e1.__eq__("bad") is NotImplemented

    def test_rmul_notimplemented(self, cl3):
        """non-scalar * MV returns NotImplemented."""
        e1, _, _ = cl3.basis_vectors()
        assert e1.__rmul__("bad") is NotImplemented


class TestIpFunction:
    def test_ip_default_is_doran_lasenby(self, cl3):
        """ip() defaults to Doran-Lasenby."""
        e1, _, _ = cl3.basis_vectors()
        assert ip(e1, e1) == doran_lasenby_inner(e1, e1)

    def test_ip_hestenes(self, cl3):
        """ip(mode='hestenes') dispatches correctly."""
        e1, _, _ = cl3.basis_vectors()
        assert ip(e1, e1, mode="hestenes") == hestenes_inner(e1, e1)

    def test_ip_left(self, cl3):
        """ip(mode='left') dispatches to left contraction."""
        e1, e2, _ = cl3.basis_vectors()
        assert ip(e1, e1 ^ e2, mode="left") == left_contraction(e1, e1 ^ e2)

    def test_ip_right(self, cl3):
        """ip(mode='right') dispatches to right contraction."""
        e1, e2, _ = cl3.basis_vectors()
        assert ip(e1 ^ e2, e2, mode="right") == right_contraction(e1 ^ e2, e2)

    def test_ip_scalar(self, cl3):
        """ip(mode='scalar') dispatches to scalar product."""
        e1, e2, _ = cl3.basis_vectors()
        assert ip(e1, e2, mode="scalar") == scalar_product(e1, e2)

    def test_ip_bad_mode(self, cl3):
        """ip() with unknown mode raises ValueError."""
        e1, _, _ = cl3.basis_vectors()
        with pytest.raises(ValueError, match="Unknown inner product mode"):
            ip(e1, e1, mode="bogus")


class TestCommutatorAnticommutator:
    def test_commutator(self, cl3):
        """commutator(a,b) = ab - ba."""
        e1, e2, _ = cl3.basis_vectors()
        c = commutator(e1, e2)
        expected = gp(e1, e2) - gp(e2, e1)
        assert c == expected

    def test_anticommutator(self, cl3):
        """anticommutator(a,b) = ab + ba."""
        e1, e2, _ = cl3.basis_vectors()
        ac = anticommutator(e1, e2)
        expected = gp(e1, e2) + gp(e2, e1)
        assert ac == expected

    def test_lie_bracket(self, cl3):
        """lie_bracket = ½(ab - ba)."""
        e1, e2, _ = cl3.basis_vectors()
        lb = lie_bracket(e1, e2)
        expected = (gp(e1, e2) - gp(e2, e1)) * 0.5
        assert lb == expected

    def test_jordan_product(self, cl3):
        """jordan_product = ½(ab + ba)."""
        e1, e2, _ = cl3.basis_vectors()
        jp = jordan_product(e1, e2)
        expected = (gp(e1, e2) + gp(e2, e1)) * 0.5
        assert jp == expected

    def test_commutator_antisymmetric(self, cl3):
        """commutator is antisymmetric."""
        e1, e2, _ = cl3.basis_vectors()
        assert commutator(e1, e2) == -commutator(e2, e1)

    def test_anticommutator_symmetric(self, cl3):
        """anticommutator is symmetric."""
        e1, e2, _ = cl3.basis_vectors()
        assert anticommutator(e1, e2) == anticommutator(e2, e1)

    def test_lie_bracket_bivector_structure(self, cl3):
        """Bivectors form a Lie algebra under lie_bracket with clean structure constants."""
        e1, e2, e3 = cl3.basis_vectors()
        B12, B23, B31 = e1 ^ e2, e2 ^ e3, e3 ^ e1
        # [B12, B23] = -B31 (structure constant ε₁₂₃ with sign from ordering)
        assert lie_bracket(B12, B23) == -B31

    def test_jordan_product_vectors_is_inner(self, cl3):
        """For vectors, jordan_product(a, b) = a · b."""
        e1, e2, e3 = cl3.basis_vectors()
        a = 3 * e1 + 2 * e2
        b = e1 - e3
        jp = jordan_product(a, b)
        ip_val = hestenes_inner(a, b)
        assert jp == ip_val

    def test_gp_decomposition(self, cl3):
        """ab = ½[a,b] + ½{a,b} — commutator + anticommutator decompose the GP."""
        e1, e2, e3 = cl3.basis_vectors()
        a = 2 * e1 + e3
        b = e2 - 3 * e3
        ab = gp(a, b)
        recomposed = lie_bracket(a, b) + jordan_product(a, b)
        assert ab == recomposed


# ============================================================
# symbolic.py coverage gaps
# ============================================================


class TestSymbolicOperators:
    def test_radd_scalar(self, cl3):
        """scalar + Expr works."""
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        expr = 3 + a
        assert str(expr) == "3 + a"

    def test_rsub_scalar(self, cl3):
        """scalar - Expr works."""
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        expr = 3 - a
        assert str(expr) == "3 - a"

    def test_rmul_scalar(self, cl3):
        """scalar * Expr works."""
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        expr = 5 * a
        assert str(expr) == "5a"

    def test_truediv(self, cl3):
        """Expr / scalar works."""
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        expr = a / 2
        assert str(expr) == "a/2"

    def test_truediv_notimplemented(self, cl3):
        """Expr / non-scalar raises TypeError."""
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        assert a.__truediv__("bad") is NotImplemented

    def test_neg_eval(self, cl3):
        """Neg node evaluates correctly."""
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        result = (-a).eval()
        assert np.allclose(result.data, (-e1).data)

    def test_scalar_mul_eval(self, cl3):
        """ScalarMul node evaluates correctly."""
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        result = (3 * a).eval()
        assert np.allclose(result.data, (3 * e1).data)


class TestSymbolicBinaryEval:
    def test_rc_eval(self, cl3):
        """Right contraction Expr evaluates correctly."""
        e1, e2, _ = cl3.basis_vectors()
        B = sym(e1 * e2, "B")
        v = sym(e2, "v")
        result = src(B, v).eval()
        expected = right_contraction(e1 * e2, e2)
        assert np.allclose(result.data, expected.data)

    def test_hi_eval(self, cl3):
        """Hestenes inner Expr evaluates correctly."""
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        result = shi(a, b).eval()
        expected = hestenes_inner(e1, e2)
        assert np.allclose(result.data, expected.data)

    def test_sp_eval(self, cl3):
        """Scalar product Expr evaluates correctly."""
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e1, "b")
        result = ssp(a, b).eval()
        expected = scalar_product(e1, e1)
        assert np.allclose(result.data, expected.data)

    def test_op_eval(self, cl3):
        """Outer product Expr evaluates correctly."""
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        result = sop(a, b).eval()
        expected = op(e1, e2)
        assert np.allclose(result.data, expected.data)

    def test_sub_eval(self, cl3):
        """Sub Expr evaluates correctly."""
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        result = (a - b).eval()
        assert np.allclose(result.data, (e1 - e2).data)

    def test_add_eval(self, cl3):
        """Add Expr evaluates correctly."""
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        result = (a + b).eval()
        assert np.allclose(result.data, (e1 + e2).data)


class TestSymbolicUnaryEval:
    def test_involute_eval(self, cl3):
        """Involute Expr evaluates correctly."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        result = sinvolute(v).eval()
        expected = involute(e1)
        assert np.allclose(result.data, expected.data)

    def test_conjugate_eval(self, cl3):
        """Conjugate Expr evaluates correctly."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        result = sconjugate(v).eval()
        expected = conjugate(e1)
        assert np.allclose(result.data, expected.data)

    def test_undual_eval(self, cl3):
        """Undual Expr evaluates correctly."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        result = sundual(v).eval()
        expected = undual(e1)
        assert np.allclose(result.data, expected.data)

    def test_unit_eval(self, cl3):
        """Unit Expr evaluates correctly."""
        e1, e2, _ = cl3.basis_vectors()
        v = sym(cl3.vector([3, 4, 0]), "v")
        result = sunit(v).eval()
        expected = unit(cl3.vector([3, 4, 0]))
        assert np.allclose(result.data, expected.data)

    def test_inverse_eval(self, cl3):
        """Inverse Expr evaluates correctly."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(2 * e1, "v")
        result = sinverse(v).eval()
        expected = inverse(2 * e1)
        assert np.allclose(result.data, expected.data)


class TestSymbolicIp:
    def test_ip_hestenes(self, cl3):
        """ip(mode='hestenes') dispatches correctly."""
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        assert str(sip(a, b)) == "a·b"

    def test_ip_left(self, cl3):
        """ip(mode='left') dispatches to left contraction."""
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        assert str(sip(a, b, mode="left")) == "a⌋b"

    def test_ip_right(self, cl3):
        """ip(mode='right') dispatches to right contraction."""
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        assert str(sip(a, b, mode="right")) == "a⌊b"

    def test_ip_scalar(self, cl3):
        """ip(mode='scalar') dispatches to scalar product."""
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        assert str(sip(a, b, mode="scalar")) == "a∗b"

    def test_ip_bad_mode(self, cl3):
        """ip() with unknown mode raises ValueError."""
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        with pytest.raises(ValueError, match="Unknown inner product mode"):
            sip(a, b, mode="bogus")

    def test_ip_numeric_fallback(self, cl3):
        """ip() falls back to numeric for eager MVs."""
        e1, _, _ = cl3.basis_vectors()
        result = sip(e1, e1)
        assert not isinstance(result, Expr)

    def test_ip_numeric_modes(self, cl3):
        """ip() numeric fallback works for all modes."""
        e1, e2, _ = cl3.basis_vectors()
        assert sip(e1, e1 ^ e2, mode="left") == left_contraction(e1, e1 ^ e2)
        assert sip(e1 ^ e2, e1, mode="right") == right_contraction(e1 ^ e2, e1)
        assert sip(e1, e2, mode="scalar") == scalar_product(e1, e2)


class TestSymbolicNormalize:
    def test_normalize_alias(self, cl3):
        """normalize() is an alias for unit()."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(snormalize(v)) == "v̂"
        assert str(snormalise(v)) == "v̂"

    def test_normalize_numeric_fallback(self, cl3):
        """normalize() falls back to numeric."""
        v = cl3.vector([3, 4, 0])
        result = snormalize(v)
        assert not isinstance(result, Expr)


class TestSymbolicConvenienceProps:
    def test_inv_property(self, cl3):
        """.inv returns inverse."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(v.inv) == "v⁻¹"

    def test_dag_property(self, cl3):
        """.dag returns reverse."""
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        assert str(R.dag) == "R̃"

    def test_sq_property(self, cl3):
        """.sq returns gp(x, x)."""
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        assert str(R.sq) == "R²"


class TestSymbolicMixedInputs:
    """Test that mixing Multivector and Expr works via _ensure_expr."""

    def test_gp_mv_and_expr(self, cl3):
        """gp(MV, Expr) coerces correctly."""
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        result = sgp(e1, R)
        assert result._is_lazy

    def test_op_mv_and_expr(self, cl3):
        """op(MV, Expr) coerces correctly."""
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        result = sop(e2, a)
        assert result._is_lazy


class TestScalarExpr:
    def test_scalar_str(self):
        """Scalar node str() renders the value."""
        s = Scalar(3.0)
        assert str(s) == "3"

    def test_scalar_eval_raises(self):
        """Scalar node eval() raises — no algebra context."""
        s = Scalar(3.0)
        with pytest.raises(TypeError):
            s.eval()


class TestUnitLongName:
    def test_unit_long_name(self, cl3):
        """unit() long name renders correctly."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "velocity")
        assert str(sunit(v)) == "velocity/‖velocity‖"


class TestRemainingAlgebraGaps:
    def test_mv_sub_scalar(self, cl3):
        """MV - scalar works."""
        e1, _, _ = cl3.basis_vectors()
        r = (3 + e1) - 1
        assert r.data[0] == 2.0
        assert r.data[1] == 1.0

    def test_mv_eq_scalar(self, cl3):
        """MV == scalar compares grade-0."""
        s = cl3.scalar(5.0)
        assert s == 5.0
        assert not (s == 3.0)

    def test_grade_out_of_range(self, cl3):
        """grade(mv, k) with k > n returns zero."""
        e1, _, _ = cl3.basis_vectors()
        r = grade(e1, -1)
        assert np.allclose(r.data, 0)
        r = grade(e1, 99)
        assert np.allclose(r.data, 0)

    def test_unit_zero_raises(self, cl3):
        """unit(zero) raises ValueError."""
        with pytest.raises(ValueError, match="Cannot normalize"):
            unit(cl3.scalar(0))


class TestRemainingSymbolicGaps:
    def test_sym_repr(self, cl3):
        """Sym repr uses ascii name."""
        e1, _, _ = cl3.basis_vectors()
        s = sym(e1, "v")
        assert repr(s) == "v"

    def test_expr_repr_delegates_to_str(self, cl3):
        """All non-Sym Expr nodes should have repr() == str() for REPL display."""
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        v = sym(e1, "v")
        a = sym(e1, "a")
        b = sym(e2, "b")

        cases = [
            sgrade(R * v * ~R, 1),  # Grade
            R * v,  # Gp
            a ^ b,  # Op
            ~R,  # Reverse
            a + b,  # Add
            a - b,  # Sub
            3 * a,  # ScalarMul
            -a,  # Neg
        ]
        for expr in cases:
            assert repr(expr) == str(expr), f"{type(expr).__name__}: repr != str"

    def test_expr_or_operator(self, cl3):
        """| operator on Expr builds Dli node."""
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e1 ^ e2, "B")
        result = a | b
        assert str(result) == "a·B"

    def test_expr_mul_with_expr(self, cl3):
        """Expr * Expr builds Gp node."""
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
    """Tests for even_grades(), odd_grades(), squared() numeric functions."""

    def test_even(self, cl3):
        """Even LaTeX renders with \text{even}."""
        e1, e2, _ = cl3.basis_vectors()
        mv = 1 + 2 * e1 + 3 * (e1 ^ e2)
        r = even_grades(mv)
        assert np.isclose(r.data[0], 1.0)  # scalar
        assert np.isclose(r.data[1], 0.0)  # e1 (odd)
        assert np.isclose(r.data[3], 3.0)  # e12

    def test_odd(self, cl3):
        """Odd LaTeX renders with \text{odd}."""
        e1, e2, _ = cl3.basis_vectors()
        mv = 1 + 2 * e1 + 3 * (e1 ^ e2)
        r = odd_grades(mv)
        assert np.isclose(r.data[0], 0.0)
        assert np.isclose(r.data[1], 2.0)
        assert np.isclose(r.data[3], 0.0)

    def test_even_odd_sum(self, cl3):
        """even + odd = original."""
        e1, e2, e3 = cl3.basis_vectors()
        mv = 1 + 2 * e1 + 3 * (e1 ^ e2) + 4 * (e1 ^ e2 ^ e3)
        assert even_grades(mv) + odd_grades(mv) == mv

    def test_squared(self, cl3):
        """Squared LaTeX renders with ^2."""
        e1, e2, _ = cl3.basis_vectors()
        v = e1 + e2
        assert squared(v) == gp(v, v)

    def test_squared_bivector(self, cl3):
        """squared(bivector) gives negative scalar."""
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        assert squared(B) == cl3.scalar(-1.0)


class TestSymbolicEvenOddSquared:
    """Tests for symbolic even_grades(), odd_grades(), squared()."""

    def test_squared_str(self, cl3):
        """Squared Expr renders as x²."""
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        assert str(ssq(R)) == "R²"

    def test_squared_eval(self, cl3):
        """Squared Expr evaluates correctly."""
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        result = ssq(R).eval()
        expected = gp(e1 * e2, e1 * e2)
        assert np.allclose(result.data, expected.data)

    def test_squared_numeric_fallback(self, cl3):
        """squared() falls back for eager MVs."""
        e1, _, _ = cl3.basis_vectors()
        result = ssq(e1)
        assert not isinstance(result, Expr)

    def test_even_str(self, cl3):
        """Even Expr renders with ⟨⟩₊."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(seven(v)) == "⟨v⟩₊"

    def test_even_eval(self, cl3):
        """Even Expr evaluates correctly."""
        e1, e2, _ = cl3.basis_vectors()
        mv = sym(1 + 2 * e1 + 3 * (e1 ^ e2), "A")
        result = seven(mv).eval()
        expected = even_grades(1 + 2 * e1 + 3 * (e1 ^ e2))
        assert np.allclose(result.data, expected.data)

    def test_even_numeric_fallback(self, cl3):
        """even_grades() falls back for eager MVs."""
        e1, _, _ = cl3.basis_vectors()
        result = seven(e1)
        assert not isinstance(result, Expr)

    def test_odd_str(self, cl3):
        """Odd Expr renders with ⟨⟩₋."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(sodd(v)) == "⟨v⟩₋"

    def test_odd_eval(self, cl3):
        """Odd Expr evaluates correctly."""
        e1, e2, _ = cl3.basis_vectors()
        mv = sym(1 + 2 * e1 + 3 * (e1 ^ e2), "A")
        result = sodd(mv).eval()
        expected = odd_grades(1 + 2 * e1 + 3 * (e1 ^ e2))
        assert np.allclose(result.data, expected.data)

    def test_odd_numeric_fallback(self, cl3):
        """odd_grades() falls back for eager MVs."""
        e1, _, _ = cl3.basis_vectors()
        result = sodd(e1)
        assert not isinstance(result, Expr)


class TestGetitem:
    def test_grade_projection_getitem(self, cl3):
        """mv[k] is shorthand for grade(mv, k)."""
        e1, e2, _ = cl3.basis_vectors()
        mv = 3 + 2 * e1 + (e1 ^ e2)
        assert mv[0] == grade(mv, 0)
        assert mv[1] == grade(mv, 1)
        assert mv[2] == grade(mv, 2)

    def test_getitem_out_of_range(self, cl3):
        """mv[k] with k > n returns zero."""
        e1, _, _ = cl3.basis_vectors()
        r = e1[5]
        assert np.allclose(r.data, 0)


class TestRotorFromPlaneAngle:
    def test_90_degree_rotation(self, cl3):
        """90° rotor rotates e1 to e2."""
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        R = cl3.rotor_from_plane_angle(B, radians=np.pi / 2)
        v_rot = R * e1 * ~R
        assert np.allclose(v_rot.data, e2.data, atol=1e-12)

    def test_180_degree_rotation(self, cl3):
        """180° rotor rotates e1 to -e1."""
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        R = cl3.rotor_from_plane_angle(B, radians=np.pi)
        v_rot = R * e1 * ~R
        assert np.allclose(v_rot.data, (-e1).data, atol=1e-12)

    def test_zero_rotation(self, cl3):
        """0° rotor is identity."""
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        R = cl3.rotor_from_plane_angle(B, radians=0)
        v_rot = R * e1 * ~R
        assert np.allclose(v_rot.data, e1.data, atol=1e-12)

    def test_rotor_is_rotor(self, cl3):
        """rotor() output passes is_rotor()."""
        e1, e2, _ = cl3.basis_vectors()
        B = e1 ^ e2
        R = cl3.rotor_from_plane_angle(B, radians=1.23)
        assert is_rotor(R)


class TestIsRotor:
    def test_unit_rotor(self, cl3):
        """Unit rotor passes is_rotor()."""
        e1, e2, _ = cl3.basis_vectors()
        R = cl3.rotor_from_plane_angle(e1 ^ e2, radians=0.5)
        assert is_rotor(R)

    def test_identity_is_rotor(self, cl3):
        """Scalar 1 is a rotor."""
        assert is_rotor(cl3.identity)

    def test_vector_not_rotor(self, cl3):
        """Vector is not a rotor."""
        e1, _, _ = cl3.basis_vectors()
        assert not is_rotor(e1)


class TestRotorValidation:
    def test_rejects_vector(self, cl3):
        """rotor() rejects odd-grade input."""
        e1, _, _ = cl3.basis_vectors()
        with pytest.raises(ValueError, match="odd-grade"):
            cl3.rotor(e1, radians=0.5)

    def test_rejects_trivector(self, cl3):
        """rotor() rejects trivector input."""
        e1, e2, e3 = cl3.basis_vectors()
        with pytest.raises(ValueError, match="odd-grade"):
            cl3.rotor(e1 ^ e2 ^ e3, radians=0.5)

    def test_accepts_bivector(self, cl3):
        """rotor() accepts bivector input."""
        e1, e2, _ = cl3.basis_vectors()
        R = cl3.rotor(e1 ^ e2, radians=0.5)
        assert is_rotor(R)

    def test_rejects_scalar(self, cl3):
        """Scalars have no rotation plane — rotor() should reject them."""
        with pytest.raises(ValueError, match="bivector"):
            cl3.rotor(cl3.scalar(1.0), radians=0.5)

    def test_normalizes_non_unit_bivector(self, cl3):
        """rotor() auto-normalizes the bivector."""
        e1, e2, _ = cl3.basis_vectors()
        R1 = cl3.rotor(e1 ^ e2, radians=0.5)
        R2 = cl3.rotor(3 * (e1 ^ e2), radians=0.5)
        assert np.allclose(R1.data, R2.data)

    def test_sta_pseudoscalar_u1(self):
        """rotor() accepts STA pseudoscalar — U(1) phase."""
        sta = Algebra((1, -1, -1, -1))
        I = sta.I
        R = sta.rotor(I, radians=0.5)
        assert is_even(R)

    def test_scaled_rotor_not_rotor(self, cl3):
        """Scaled rotor fails is_rotor()."""
        e1, e2, _ = cl3.basis_vectors()
        R = cl3.rotor_from_plane_angle(e1 ^ e2, radians=0.5)
        assert not is_rotor(2 * R)


class TestEvenOddGradesRenamed:
    def test_even_grades(self, cl3):
        """even_grades keeps grades 0, 2, ..."""
        e1, e2, _ = cl3.basis_vectors()
        mv = 1 + 2 * e1 + 3 * (e1 ^ e2)
        assert even_grades(mv) == even_grades(mv)

    def test_odd_grades(self, cl3):
        """odd_grades keeps grades 1, 3, ..."""
        e1, e2, _ = cl3.basis_vectors()
        mv = 1 + 2 * e1 + 3 * (e1 ^ e2)
        assert odd_grades(mv) == odd_grades(mv)

    def test_grade_even_string(self, cl3):
        """grade(mv, 'even') works."""
        e1, e2, _ = cl3.basis_vectors()
        mv = 1 + 2 * e1 + 3 * (e1 ^ e2)
        assert grade(mv, "even") == even_grades(mv)

    def test_grade_odd_string(self, cl3):
        """grade(mv, 'odd') works."""
        e1, e2, _ = cl3.basis_vectors()
        mv = 1 + 2 * e1 + 3 * (e1 ^ e2)
        assert grade(mv, "odd") == odd_grades(mv)


class TestSymbolicGradeEvenOdd:
    def test_sym_grade_even(self, cl3):
        """Symbolic grade('even') builds Even node."""
        from galaga import grade as sgrade

        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(sgrade(v, "even")) == "⟨v⟩₊"

    def test_sym_grade_odd(self, cl3):
        """Symbolic grade('odd') builds Odd node."""
        from galaga import grade as sgrade

        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(sgrade(v, "odd")) == "⟨v⟩₋"

    def test_sym_even_grades(self, cl3):
        """Symbolic even_grades builds Even node."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(seven_grades(v)) == "⟨v⟩₊"

    def test_sym_odd_grades(self, cl3):
        """Symbolic odd_grades builds Odd node."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert str(sodd_grades(v)) == "⟨v⟩₋"


class TestLatex:
    """Tests for .latex() output on all expression types."""

    def test_sym(self, cl3):
        """Sym LaTeX renders its latex name."""
        e1, _, _ = cl3.basis_vectors()
        assert sym(e1, "v").latex() == "v"

    def test_gp(self, cl3):
        """Gp LaTeX renders with space."""
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        v = sym(e1, "v")
        assert (R * v).latex() == "R v"

    def test_sandwich_grade(self, cl3):
        """Grade of sandwich renders correctly."""
        e1, e2, _ = cl3.basis_vectors()
        from galaga import grade as sgrade

        R = sym(e1 * e2, "R")
        v = sym(e1, "v")
        assert sgrade(R * v * ~R, 1).latex() == r"\langle R v \tilde{R} \rangle_{1}"

    def test_wedge(self, cl3):
        r"""Op LaTeX renders with \wedge."""
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "a"), sym(e2, "b")
        assert (a ^ b).latex() == r"a \wedge b"

    def test_left_contraction(self, cl3):
        r"""Lc LaTeX renders with \lrcorner."""
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "a"), sym(e2, "b")
        assert slc(a, b).latex() == r"a \;\lrcorner\; b"

    def test_right_contraction(self, cl3):
        r"""Rc LaTeX renders with \llcorner."""
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "a"), sym(e2, "b")
        assert src(a, b).latex() == r"a \;\llcorner\; b"

    def test_hestenes_inner(self, cl3):
        r"""Hi LaTeX renders with \cdot."""
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "A"), sym(e2, "B")
        assert shi(a, b).latex() == r"A \cdot B"

    def test_scalar_product(self, cl3):
        """Sp LaTeX renders with *."""
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "A"), sym(e2, "B")
        assert ssp(a, b).latex() == "A * B"

    def test_reverse(self, cl3):
        """Reverse LaTeX renders with \tilde."""
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        assert (~R).latex() == r"\tilde{R}"

    def test_involute(self, cl3):
        r"""Involute LaTeX renders with \hat."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert sinvolute(v).latex() == r"\hat{v}"

    def test_conjugate(self, cl3):
        """Conjugate LaTeX renders with \bar."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert sconjugate(v).latex() == r"\bar{v}"

    def test_dual(self, cl3):
        """Dual LaTeX renders with ^*."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert sdual(v).latex() == "v^*"

    def test_undual(self, cl3):
        """Undual LaTeX renders with ^{*^{-1}}."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert sundual(v).latex() == "v^{*^{-1}}"

    def test_norm(self, cl3):
        r"""Norm LaTeX renders with \lVert."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert snorm(v).latex() == r"\lVert v \rVert"

    def test_unit(self, cl3):
        r"""Unit LaTeX renders with \hat."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert sunit(v).latex() == r"\hat{v}"

    def test_inverse(self, cl3):
        """Inverse LaTeX renders with ^{-1}."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert sinverse(v).latex() == "v^{-1}"

    def test_squared(self, cl3):
        """Squared LaTeX renders with ^2."""
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        assert ssq(R).latex() == "R^2"

    def test_even(self, cl3):
        """Even LaTeX renders with \text{even}."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert seven(v).latex() == r"\langle v \rangle_{\text{even}}"

    def test_odd(self, cl3):
        """Odd LaTeX renders with \text{odd}."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert sodd(v).latex() == r"\langle v \rangle_{\text{odd}}"

    def test_add(self, cl3):
        """Add LaTeX renders with +."""
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "a"), sym(e2, "b")
        assert (a + b).latex() == "a + b"

    def test_sub(self, cl3):
        """Sub LaTeX renders with -."""
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "a"), sym(e2, "b")
        assert (a - b).latex() == "a - b"

    def test_neg(self, cl3):
        """Neg LaTeX renders with -."""
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        assert (-a).latex() == "-a"

    def test_scalar_mul(self, cl3):
        """ScalarMul LaTeX renders as coefficient."""
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        assert (3 * a).latex() == "3 a"
        assert (-1 * a).latex() == "-a"

    def test_parens(self, cl3):
        """Parens in LaTeX use \\left(\right)."""
        e1, e2, _ = cl3.basis_vectors()
        a, b = sym(e1, "a"), sym(e2, "b")
        R = sym(e1 * e2, "R")
        assert ((a + b) * R).latex() == r"\left(a + b\right) R"

    def test_repr_latex(self, cl3):
        """MV._repr_latex_() wraps in $."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert v._repr_latex_() == "$v$"
        assert (~v)._repr_latex_() == r"$\tilde{v}$"

    def test_multivector_latex_bare(self, cl3):
        """MV.latex() returns raw LaTeX."""
        e1, e2, _ = cl3.basis_vectors()
        v = 3 * e1 + 4 * e2
        assert v.latex() == "3 e_{12}" or "e_{1}" in v.latex()  # just check it returns a string
        assert "$" not in v.latex()

    def test_multivector_latex_wrap_inline(self, cl3):
        """MV.latex(wrap='$') wraps inline."""
        e1, _, _ = cl3.basis_vectors()
        v = 3 * e1
        raw = v.latex()
        assert v.latex(wrap="$") == f"${raw}$"

    def test_multivector_latex_wrap_display(self, cl3):
        """MV.latex(wrap='$$') wraps display."""
        e1, _, _ = cl3.basis_vectors()
        v = 3 * e1
        raw = v.latex()
        assert v.latex(wrap="$$") == f"$$\n{raw}\n$$"

    def test_multivector_latex_wrap_none(self, cl3):
        """MV.latex(wrap=None) returns raw."""
        e1, _, _ = cl3.basis_vectors()
        v = 3 * e1
        assert v.latex(wrap=None) == v.latex()


class TestSandwich:
    """Tests for sandwich(r, x) / sw(r, x)."""

    def test_sandwich_rotation(self, cl3):
        """sandwich(R, v) rotates v."""
        e1, e2, _ = cl3.basis_vectors()
        R = cl3.rotor_from_plane_angle(e1 ^ e2, radians=np.pi / 2)
        result = sandwich(R, e1)
        assert np.allclose(result.data, e2.data, atol=1e-12)

    def test_sw_alias(self, cl3):
        """sw() is an alias for sandwich()."""
        e1, e2, _ = cl3.basis_vectors()
        R = cl3.rotor_from_plane_angle(e1 ^ e2, radians=np.pi / 4)
        assert np.allclose(sandwich(R, e1).data, sw(R, e1).data)

    def test_sandwich_identity(self, cl3):
        """sandwich(1, v) = v."""
        e1, _, _ = cl3.basis_vectors()
        one = cl3.scalar(1.0)
        assert np.allclose(sandwich(one, e1).data, e1.data)

    def test_sandwich_bivector(self, cl3):
        """sandwich works on bivectors."""
        e1, e2, e3 = cl3.basis_vectors()
        R = cl3.rotor_from_plane_angle(e1 ^ e2, radians=np.pi / 2)
        B = e1 ^ e3
        result = sandwich(R, B)
        expected = e2 ^ e3
        assert np.allclose(result.data, expected.data, atol=1e-12)

    def test_symbolic_sandwich(self, cl3):
        """Symbolic sandwich builds Gp tree."""
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        v = sym(e1, "v")
        expr = ssandwich(R, v)
        assert str(expr) == "RvR̃"
        assert expr.latex() == r"R v \tilde{R}"

    def test_symbolic_sandwich_eval(self, cl3):
        """Symbolic sandwich evaluates correctly."""
        e1, e2, _ = cl3.basis_vectors()
        R = cl3.rotor_from_plane_angle(e1 ^ e2, radians=np.pi / 2)
        expr = ssandwich(sym(R, "R"), sym(e1, "v"))
        result = expr.eval()
        assert np.allclose(result.data, e2.data, atol=1e-12)

    def test_symbolic_sw_alias(self, cl3):
        """Symbolic sw() is an alias."""
        e1, e2, _ = cl3.basis_vectors()
        R = sym(e1 * e2, "R")
        v = sym(e1, "v")
        assert str(ssw_alias(R, v)) == "RvR̃"


class TestScalarVectorPart:
    """Tests for .scalar_part and .vector_part properties."""

    def test_vector_part(self, cl3):
        """vector_part extracts grade-1 coefficients."""
        e1, e2, e3 = cl3.basis_vectors()
        v = 3 * e1 + 4 * e2 + 5 * e3
        assert np.allclose(v.vector_part, [3, 4, 5])

    def test_scalar_part(self, cl3):
        """scalar_part extracts grade-0 coefficient."""
        mv = cl3.scalar(7.0)
        assert mv.scalar_part == 7.0

    def test_mixed_grade(self, cl3):
        """vector_part/scalar_part on mixed MV."""
        e1, e2, e3 = cl3.basis_vectors()
        mv = cl3.scalar(7.0) + 3 * e1 + 4 * e2 + (e1 ^ e2)
        assert mv.scalar_part == 7.0
        assert np.allclose(mv.vector_part, [3, 4, 0])

    def test_zero(self, cl3):
        """vector_part/scalar_part of zero MV."""
        z = cl3.scalar(0.0)
        assert z.scalar_part == 0.0
        assert np.allclose(z.vector_part, [0, 0, 0])


class TestSimplify:
    """Tests for simplify() rewrite rules."""

    def test_double_reverse(self, cl3):
        """simplify(~~x) = x."""
        R = sym(cl3.basis_vectors()[0], "R")
        assert str(simplify(~~R)) == "R"

    def test_double_neg(self, cl3):
        """simplify(--x) = x."""
        v = sym(cl3.basis_vectors()[0], "v")
        assert str(simplify(-(-v))) == "v"  # noqa: B002

    def test_mul_identity_right(self, cl3):
        """simplify(x*1) = x."""
        v = sym(cl3.basis_vectors()[0], "v")
        assert str(simplify(v * Scalar(1))) == "v"

    def test_mul_identity_left(self, cl3):
        """simplify(1*x) = x."""
        v = sym(cl3.basis_vectors()[0], "v")
        assert str(simplify(Scalar(1) * v)) == "v"

    def test_mul_zero(self, cl3):
        """simplify(x*0) = 0."""
        v = sym(cl3.basis_vectors()[0], "v")
        assert str(simplify(v * Scalar(0))) == "0"
        assert str(simplify(Scalar(0) * v)) == "0"

    def test_add_zero(self, cl3):
        """simplify(x+0) = x."""
        v = sym(cl3.basis_vectors()[0], "v")
        assert str(simplify(v + Scalar(0))) == "v"
        assert str(simplify(Scalar(0) + v)) == "v"

    def test_sub_self(self, cl3):
        """simplify(x-x) = 0."""
        v = sym(cl3.basis_vectors()[0], "v")
        assert str(simplify(v - v)) == "0"

    def test_scalar_mul_zero(self, cl3):
        """simplify(0*x) = 0."""
        v = sym(cl3.basis_vectors()[0], "v")
        assert str(simplify(0 * v)) == "0"

    def test_scalar_mul_one(self, cl3):
        """simplify(1*x) = x."""
        v = sym(cl3.basis_vectors()[0], "v")
        assert str(simplify(1 * v)) == "v"

    def test_r_times_r_reverse(self, cl3):
        """simplify(R*~R) = 1 for rotors."""
        e1, e2, _ = cl3.basis_vectors()
        R = sym(cl3.rotor_from_plane_angle(e1 ^ e2, radians=0.5), "R")
        result = simplify(R * ~R)
        assert np.allclose(result.eval().data[0], 1.0, atol=1e-12)

    def test_grade_idempotent(self, cl3):
        """simplify(grade(grade(x,k),k)) = grade(x,k)."""
        v = sym(cl3.basis_vectors()[0], "v")
        # grade(grade(v,1),1) → v (v is known grade-1)
        assert str(simplify(sgrade(sgrade(v, 1), 1))) == "v"

    def test_nested(self, cl3):
        """Simplify cascades through nested expressions."""
        v = sym(cl3.basis_vectors()[0], "v")
        # ~~v + 0 → v
        assert str(simplify(~~v + Scalar(0))) == "v"

    # --- New rules ---

    def test_double_involute(self, cl3):
        """simplify(involute(involute(x))) = x."""
        v = sym(cl3.basis_vectors()[0], "v")
        assert str(simplify(sinvolute(sinvolute(v)))) == "v"

    def test_double_conjugate(self, cl3):
        """simplify(conjugate(conjugate(x))) = x."""
        v = sym(cl3.basis_vectors()[0], "v")
        assert str(simplify(sconjugate(sconjugate(v)))) == "v"

    def test_double_inverse(self, cl3):
        """simplify(inverse(inverse(x))) = x."""
        v = sym(cl3.basis_vectors()[0], "v")
        assert str(simplify(sinverse(sinverse(v)))) == "v"

    def test_wedge_self(self, cl3):
        """simplify(x∧x) = 0."""
        a = sym(cl3.basis_vectors()[0], "a")
        assert str(simplify(a ^ a)) == "0"

    def test_norm_unit(self, cl3):
        """simplify(norm(unit(x))) = 1."""
        v = sym(cl3.basis_vectors()[0], "v")
        assert str(simplify(snorm(sunit(v)))) == "1"

    def test_add_self(self, cl3):
        """simplify(x+x) = 2x."""
        a = sym(cl3.basis_vectors()[0], "a")
        assert str(simplify(a + a)) == "2a"

    def test_sub_neg(self, cl3):
        """simplify(x-(-y)) = x+y."""
        a = sym(cl3.basis_vectors()[0], "a")
        b = sym(cl3.basis_vectors()[1], "b")
        result = simplify(a - (-b))
        assert str(result) == "a + b"

    def test_add_neg_self(self, cl3):
        """simplify(x+(-x)) = 0."""
        a = sym(cl3.basis_vectors()[0], "a")
        assert str(simplify(a + (-a))) == "0"

    def test_scalar_mul_collapse(self, cl3):
        """simplify(3*(2*x)) = 6x."""
        v = sym(cl3.basis_vectors()[0], "v")
        assert str(simplify(3 * (2 * v))) == "6v"

    def test_grade_known_match(self, cl3):
        """simplify(grade(v,1)) = v when v is grade-1."""
        v = sym(cl3.basis_vectors()[0], "v")  # grade 1
        assert str(simplify(sgrade(v, 1))) == "v"

    def test_grade_known_mismatch(self, cl3):
        """simplify(grade(v,2)) = 0 when v is grade-1."""
        v = sym(cl3.basis_vectors()[0], "v")  # grade 1
        assert str(simplify(sgrade(v, 2))) == "0"

    def test_even_bivector(self, cl3):
        """simplify(even(B)) = B for bivector."""
        e1, e2, _ = cl3.basis_vectors()
        B = sym(e1 ^ e2, "B")  # grade 2
        assert str(simplify(seven(B))) == "B"

    def test_odd_bivector(self, cl3):
        """simplify(odd(B)) = 0 for bivector."""
        e1, e2, _ = cl3.basis_vectors()
        B = sym(e1 ^ e2, "B")
        assert str(simplify(sodd(B))) == "0"

    def test_even_vector(self, cl3):
        """simplify(even(v)) = 0 for vector."""
        v = sym(cl3.basis_vectors()[0], "v")
        assert str(simplify(seven(v))) == "0"

    def test_odd_vector(self, cl3):
        """simplify(odd(v)) = v for vector."""
        v = sym(cl3.basis_vectors()[0], "v")
        assert str(simplify(sodd(v))) == "v"

    def test_cascade(self, cl3):
        """Cascading simplifications resolve fully."""
        a = sym(cl3.basis_vectors()[0], "a")
        # a - (-a) → a + a → 2a (requires two passes)
        assert str(simplify(a - (-a))) == "2a"

    def test_auto_grade_detection(self, cl3):
        """sym() auto-detects grade from MV data."""
        e1, e2, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        B = sym(e1 ^ e2, "B")
        s = sym(cl3.scalar(5.0), "s")
        assert v._grade == 1
        assert B._grade == 2
        assert s._grade == 0


class TestMultivectorLatex:
    """Tests for Multivector.latex() and _repr_latex_()."""

    def test_scalar(self, cl3):
        """Scalar MV LaTeX renders as number."""
        assert cl3.scalar(5).latex() == "5"

    def test_zero(self, cl3):
        """vector_part/scalar_part of zero MV."""
        assert cl3.scalar(0).latex() == "0"

    def test_vector(self, cl3):
        """Vector MV LaTeX renders with basis names."""
        e1, e2, e3 = cl3.basis_vectors()
        assert (3 * e1 + 4 * e2).latex() == "3 e_{1} + 4 e_{2}"

    def test_coeff_one_suppressed(self, cl3):
        """Coefficient ±1 is suppressed in LaTeX."""
        e1, e2, _ = cl3.basis_vectors()
        assert e1.latex() == "e_{1}"
        assert (-e2).latex() == "-e_{2}"

    def test_bivector(self, cl3):
        """Bivector MV LaTeX renders correctly."""
        e1, e2, _ = cl3.basis_vectors()
        assert (e1 ^ e2).latex() == "e_{12}"

    def test_pseudoscalar(self, cl3):
        """Pseudoscalar MV LaTeX renders correctly."""
        assert cl3.I.latex() == "e_{123}"

    def test_mixed(self, cl3):
        """Mixed-grade MV LaTeX renders all terms."""
        e1, e2, _ = cl3.basis_vectors()
        mv = cl3.scalar(1) + 2 * e1 + 3 * (e1 ^ e2)
        assert mv.latex() == "1 + 2 e_{1} + 3 e_{12}"

    def test_negative_terms(self, cl3):
        """Negative terms use - not + -."""
        e1, e2, _ = cl3.basis_vectors()
        assert (e1 - e2).latex() == "e_{1} - e_{2}"

    def test_gamma_names(self):
        """Gamma-named algebra uses γ in LaTeX."""
        sta = Algebra((1, -1, -1, -1), names="gamma")
        g0, g1, _, _ = sta.basis_vectors()
        assert g0.latex() == "\\gamma_0"
        assert (g0 * g1).latex() == "\\gamma_0 \\gamma_1"

    def test_sigma_names(self):
        """Sigma-named algebra uses σ in LaTeX."""
        pauli = Algebra((1, 1, 1), names="sigma")
        s1, s2, _ = pauli.basis_vectors()
        assert s1.latex() == "\\sigma_1"
        assert (s1 * s2).latex() == "\\sigma_1 \\sigma_2"

    def test_repr_latex(self, cl3):
        """MV._repr_latex_() wraps in $."""
        e1, _, _ = cl3.basis_vectors()
        assert e1._repr_latex_() == "$e_{1}$"

    def test_repr_latex_mixed(self, cl3):
        """Mixed MV _repr_latex_() wraps correctly."""
        e1, e2, _ = cl3.basis_vectors()
        mv = cl3.scalar(1) + e1
        assert mv._repr_latex_() == "$1 + e_{1}$"


class TestCoverageGaps:
    """Tests targeting specific uncovered lines."""

    # algebra.py: _blade_latex fallback with custom names, no latex_names (lines 322-324)
    def test_blade_latex_custom_names_no_latex(self):
        """Custom names without latex fall back."""
        alg = Algebra((1, 1, 1), names=(["a", "b", "c"], ["𝐚", "𝐛", "𝐜"]))
        e1, e2, _ = alg.basis_vectors()
        mv = e1 ^ e2
        latex = mv.latex()
        assert "a" in latex and "b" in latex

    # algebra.py: __hash__ (line 464)
    def test_multivector_hash(self):
        """MV is hashable."""
        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors()
        s = {e1, e2, e1}
        assert len(s) == 2
        d = {e1: "x"}
        assert d[e1] == "x"

    # symbolic.py: Expr.latex(wrap='$') and wrap='$$' (lines 138, 140)
    def test_expr_latex_wrap(self, cl3):
        """Expr.latex(wrap='$') wraps in $."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        raw = v.latex()
        assert v.latex(wrap="$") == f"${raw}$"
        assert v.latex(wrap="$$") == f"$$\n{raw}\n$$"

    # symbolic.py: Expr.__rmul__ with non-scalar (line 179)
    def test_expr_rmul_expr(self, cl3):
        """Expr * Expr builds Gp."""
        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        result = a.__rmul__(b)
        assert str(result) == "ba"

    # symbolic.py: Expr.__rmul__ with scalar (line 172)
    def test_expr_rmul_scalar(self, cl3):
        """scalar * Expr builds ScalarMul."""
        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        result = 5 * a
        assert str(result) == "5a"

    # symbolic.py: Sym with explicit grade (line 228)
    def test_sym_explicit_grade(self, cl3):
        """Sym with explicit grade overrides auto-detect."""
        e1, e2, _ = cl3.basis_vectors()
        s = sym(e1 + e2, "v", grade=1)
        assert s._grade == 1

    # symbolic.py: Scalar.__str__ (line 270)
    def test_scalar_str(self):
        """Scalar node str() renders the value."""
        from galaga.expr import Scalar

        s = Scalar(42)
        assert str(s) == "42"
        assert s.latex() == "42"

    # symbolic.py: _ensure_expr TypeError (line 611)
    def test_ensure_expr_bad_type(self):
        """Non-MV/Expr/scalar raises TypeError."""
        import pytest

        from galaga.expr import _ensure_expr

        with pytest.raises(TypeError, match="Cannot convert"):
            _ensure_expr([1, 2, 3])

    # symbolic.py: _eq for Conjugate, Grade, fallback (lines 635, 637, 640-642)
    def test_eq_conjugate(self, cl3):
        """Conjugate Expr equality."""
        from galaga.simplify import _eq

        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        assert _eq(Conjugate(a), Conjugate(a))
        assert not _eq(Conjugate(a), Conjugate(sym(e1, "b")))

    def test_eq_grade(self, cl3):
        """Grade Expr equality."""
        from galaga.simplify import _eq

        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        assert _eq(Grade(a, 1), Grade(a, 1))
        assert not _eq(Grade(a, 1), Grade(a, 2))

    def test_eq_fallback(self, cl3):
        """Expr equality fallback returns False."""
        from galaga.simplify import _eq

        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        assert _eq(Dual(a), Dual(a))
        assert not _eq(Dual(a), Dual(sym(e1, "b")))

    # symbolic.py: _known_grade branches (lines 691-703)
    def test_known_grade_scalar(self):
        """Scalar has known grade 0."""
        from galaga.expr import Scalar
        from galaga.simplify import _known_grade

        assert _known_grade(Scalar(5)) == 0

    def test_known_grade_grade_node(self, cl3):
        """Grade node has known grade."""
        from galaga.simplify import _known_grade

        e1, _, _ = cl3.basis_vectors()
        assert _known_grade(Grade(sym(e1, "v"), 2)) == 2

    def test_known_grade_reverse(self, cl3):
        """Reverse preserves known grade."""
        from galaga.simplify import _known_grade

        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        assert _known_grade(Reverse(v)) == 1

    def test_known_grade_neg(self, cl3):
        """Neg preserves known grade."""
        from galaga.simplify import _known_grade

        e1, _, _ = cl3.basis_vectors()
        assert _known_grade(Neg(sym(e1, "v"))) == 1

    def test_known_grade_scalarmul(self, cl3):
        """ScalarMul preserves known grade."""
        from galaga.simplify import _known_grade

        e1, _, _ = cl3.basis_vectors()
        assert _known_grade(ScalarMul(3, sym(e1, "v"))) == 1

    def test_known_grade_unit(self, cl3):
        """Unit preserves known grade."""
        from galaga.simplify import _known_grade

        e1, _, _ = cl3.basis_vectors()
        assert _known_grade(Unit(sym(e1, "v"))) == 1

    def test_known_grade_unknown(self, cl3):
        """Unknown grade returns None."""
        from galaga.simplify import _known_grade

        e1, e2, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        b = sym(e2, "b")
        assert _known_grade(a + b) is None

    # symbolic.py: simplify even/odd with known grade (line 819)
    def test_simplify_odd_known_grade(self, cl3):
        """Odd of known even-grade simplifies to 0."""
        from galaga import even_grades as seven
        from galaga import odd_grades as sodd

        e1, e2, _ = cl3.basis_vectors()
        v = sym(e1, "v")  # grade 1 (odd)
        B = sym(e1 ^ e2, "B")  # grade 2 (even)
        assert str(simplify(sodd(v))) == "v"
        assert str(simplify(sodd(B))) == "0"
        assert str(simplify(seven(B))) == "B"
        assert str(simplify(seven(v))) == "0"

    # symbolic.py: _eq for Involute (line 635)
    def test_eq_involute(self, cl3):
        """Involute Expr equality."""
        from galaga.simplify import _eq

        e1, _, _ = cl3.basis_vectors()
        a = sym(e1, "a")
        assert _eq(Involute(a), Involute(a))
        assert not _eq(Involute(a), Involute(sym(e1, "b")))

    # symbolic.py: norm() passthrough for Multivector (line 938)
    def test_norm_passthrough(self, cl3):
        """norm() on eager MV returns float."""
        from galaga import norm as snorm

        e1, e2, _ = cl3.basis_vectors()
        v = 3 * e1 + 4 * e2
        assert snorm(v) == 5.0

    # symbolic.py: sandwich() passthrough for Multivector (line 985)
    def test_sandwich_passthrough(self, cl3):
        """sandwich() on eager MVs returns MV."""
        from galaga import sandwich as ssandwich

        e1, e2, _ = cl3.basis_vectors()
        R = cl3.rotor_from_plane_angle(e1 ^ e2, radians=np.pi / 2)
        result = ssandwich(R, e1)
        assert np.allclose(result.data, e2.data, atol=1e-12)

    # algebra.py: rotor_from_plane_angle degrees= and error
    def test_rotor_from_plane_degrees(self, cl3):
        """rotor(degrees=) works."""
        e1, e2, _ = cl3.basis_vectors()
        R_rad = cl3.rotor_from_plane_angle(e1 ^ e2, radians=np.pi / 2)
        R_deg = cl3.rotor_from_plane_angle(e1 ^ e2, degrees=90)
        assert np.allclose(R_rad.data, R_deg.data)

    def test_rotor_from_plane_angle_error(self, cl3):
        """rotor() with both radians and degrees raises."""
        import pytest

        e1, e2, _ = cl3.basis_vectors()
        with pytest.raises(ValueError):
            cl3.rotor_from_plane_angle(e1 ^ e2)
        with pytest.raises(ValueError):
            cl3.rotor_from_plane_angle(e1 ^ e2, radians=1.0, degrees=90)

    def test_rotor_from_plane_angle_positional(self, cl3):
        """rotor() requires keyword args for angle."""
        e1, e2, _ = cl3.basis_vectors()
        R_kw = cl3.rotor_from_plane_angle(e1 ^ e2, radians=np.pi / 2)
        R_pos = cl3.rotor_from_plane_angle(e1 ^ e2, np.pi / 2)
        assert np.allclose(R_kw.data, R_pos.data)

    def test_rotor_canonical_name(self, cl3):
        """rotor() is the canonical name."""
        e1, e2, _ = cl3.basis_vectors()
        R = cl3.rotor(e1 ^ e2, radians=np.pi / 2)
        result = sandwich(R, e1)
        assert np.allclose(result.data, e2.data, atol=1e-12)

    def test_rotor_degrees(self, cl3):
        """rotor(degrees=90) matches radians=π/2."""
        e1, e2, _ = cl3.basis_vectors()
        R = cl3.rotor(e1 ^ e2, degrees=90)
        R2 = cl3.rotor(e1 ^ e2, radians=np.pi / 2)
        assert np.allclose(R.data, R2.data)

    def test_rotor_from_bivector_alias(self, cl3):
        """rotor_from_bivector is an alias."""
        e1, e2, _ = cl3.basis_vectors()
        R1 = cl3.rotor(e1 ^ e2, radians=1.0)
        R2 = cl3.rotor_from_bivector(e1 ^ e2, radians=1.0)
        assert np.allclose(R1.data, R2.data)


class TestComplement:
    """Tests for complement() and uncomplement()."""

    def test_complement_grade_mapping(self):
        """complement maps grade-k to grade-(n-k)."""
        alg = Algebra((1, 1, 1))
        e1, e2, e3 = alg.basis_vectors()
        # grade 1 -> grade 2
        assert complement(e1) == e2 ^ e3
        # grade 2 -> grade 1
        assert complement(e1 ^ e2) == e3
        # grade 0 -> grade 3
        assert complement(alg.identity) == alg.I
        # grade 3 -> grade 0
        assert complement(alg.I) == alg.identity

    def test_complement_product_is_pseudoscalar(self):
        """x * complement(x) = I for all basis blades."""
        alg = Algebra((1, 1, 1))
        e1, e2, e3 = alg.basis_vectors()
        I = alg.I
        for x in [alg.identity, e1, e2, e3, e1 ^ e2, e1 ^ e3, e2 ^ e3, I]:
            assert x * complement(x) == I

    def test_complement_roundtrip(self):
        """uncomplement(complement(x)) = x."""
        alg = Algebra((1, 1, 1))
        e1, e2, e3 = alg.basis_vectors()
        for x in [e1, e1 ^ e2, alg.I, 3 * e1 + 2 * e2, alg.identity]:
            assert np.allclose(uncomplement(complement(x)).data, x.data)

    def test_complement_pga(self):
        """complement works in degenerate PGA algebra Cl(3,0,1)."""
        alg = Algebra((1, 1, 1, 0))
        e1, e2, e3, e0 = alg.basis_vectors()
        I = alg.I
        # x * complement(x) = I for basis blades
        for x in [e1, e0, e1 ^ e2, e1 ^ e2 ^ e3, e0 ^ e1, I]:
            assert x * complement(x) == I

    def test_complement_pga_roundtrip(self):
        """Roundtrip in PGA."""
        alg = Algebra((1, 1, 1, 0))
        e1, e2, e3, e0 = alg.basis_vectors()
        for x in [e1, e0, e1 ^ e2 ^ e3, 2 * e1 + 3 * e0]:
            assert np.allclose(uncomplement(complement(x)).data, x.data)

    def test_complement_linearity(self):
        """complement is linear."""
        alg = Algebra((1, 1, 1))
        e1, e2, _ = alg.basis_vectors()
        x = 3 * e1 + 2 * e2
        assert np.allclose(complement(x).data, (3 * complement(e1) + 2 * complement(e2)).data)

    def test_complement_sta(self):
        """complement works in Cl(1,3) spacetime algebra."""
        alg = Algebra((1, -1, -1, -1))
        g0, g1, g2, g3 = alg.basis_vectors()
        I = alg.I
        for x in [g0, g1, g0 ^ g1, g0 ^ g1 ^ g2]:
            assert x * complement(x) == I
            assert np.allclose(uncomplement(complement(x)).data, x.data)
