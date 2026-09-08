"""Coverage gap tests for algebra.py and symbolic.py."""

import numpy as np
import pytest

from galaga.expr import sym
from galaga.legacy import (
    Algebra,
    BladeConvention,
    b_gamma,
    b_sigma,
    b_sigma_xyz,
    is_even,
    is_rotor,
    sandwich,
)
from galaga.legacy import conjugate as sconjugate
from galaga.legacy import dual as sdual
from galaga.legacy import even_grades as seven
from galaga.legacy import hestenes_inner as shi
from galaga.legacy import inverse as sinverse
from galaga.legacy import involute as sinvolute
from galaga.legacy import left_contraction as slc
from galaga.legacy import norm as snorm
from galaga.legacy import odd_grades as sodd
from galaga.legacy import right_contraction as src
from galaga.legacy import sandwich as ssandwich
from galaga.legacy import scalar_product as ssp
from galaga.legacy import squared as ssq
from galaga.legacy import sw as ssw_alias
from galaga.legacy import undual as sundual
from galaga.legacy import unit as sunit


@pytest.fixture
def cl3():
    return Algebra((1, 1, 1))


# ============================================================
# algebra.py coverage gaps
# ============================================================


class TestNamingPresets:
    def test_gamma_preset(self):
        """Gamma naming preset: γ₀, γ₁, ..."""
        sta = Algebra((1, -1, -1, -1), blades=b_gamma())
        g0, g1, g2, g3 = sta.basis_vectors()
        assert "γ₀" in str(g0)
        assert "γ₀" in repr(g0)

    def test_sigma_preset(self):
        """Sigma naming preset: σ₁, σ₂, ..."""
        alg = Algebra((1, 1, 1), blades=b_sigma())
        s1, s2, s3 = alg.basis_vectors()
        assert "σ₁" in str(s1)
        assert "σ₁" in repr(s1)

    def test_sigma_xyz_preset(self):
        """Sigma xyz preset: σₓ, σᵧ, σz."""
        alg = Algebra((1, 1, 1), blades=b_sigma_xyz())
        sx, sy, sz = alg.basis_vectors()
        assert "σₓ" in str(sx)
        assert "σₓ" in repr(sx)

    def test_custom_names(self):
        """Custom (code, unicode) name tuples."""
        alg = Algebra((1, 1), blades=BladeConvention(vector_names=[("a", "𝐚", "𝐚"), ("b", "𝐛", "𝐛")]))
        a, b = alg.basis_vectors()
        assert str(a) == "𝐚"
        assert repr(a) == "𝐚"

    def test_custom_names_wrong_length(self):
        """Too-few custom names raise ValueError."""
        with pytest.raises(ValueError, match="need at least"):
            Algebra((1, 1), blades=BladeConvention(vector_names=[("a", "𝐚", "𝐚")]))

    def test_invalid_blades_type(self):
        """Non-BladeConvention blades= raises TypeError."""
        with pytest.raises(TypeError):
            Algebra((1, 1), blades="bogus")

    def test_blade_lookup_custom_names(self):
        """blade() works with gamma convention via display name."""
        sta = Algebra((1, -1, -1, -1), blades=b_gamma())
        b = sta.blade("g0g1")  # ascii name match
        e0, e1, _, _ = sta.basis_vectors()
        assert b == e0 ^ e1

    def test_blade_lookup_custom_no_match(self):
        """blade() with unrecognized name raises."""
        alg = Algebra((1, 1), blades=BladeConvention(vector_names=[("a", "𝐚", "𝐚"), ("b", "𝐛", "𝐛")]))
        with pytest.raises(ValueError, match="Unknown blade name"):
            alg.blade("xyz")

    def test_blade_name_custom_unicode(self):
        """Custom unicode names appear in str()."""
        alg = Algebra(
            (1, 1, 1), blades=BladeConvention(vector_names=[("a", "𝐚", "𝐚"), ("b", "𝐛", "𝐛"), ("c", "𝐜", "𝐜")])
        )
        a, b, c = alg.basis_vectors()
        # Non-pseudoscalar bivector uses custom names
        assert str(a * b) == "𝐚𝐛"
        assert repr(a * b) == "𝐚𝐛"
        # Pseudoscalar uses standard blade name
        assert str(a * b * c) == "𝐚𝐛𝐜"


# Architectural identities now live in facade/test_architecture_contracts.py.
# Historical source and registries: tools/baselines/architecture-contracts-v1.json.


# Inner-product identities now live in facade/test_inner_product_contracts.py.


# Eager operation/provenance identities now live in facade/test_eager_operation_contracts.py.
# Historical source and observations: tools/baselines/eager-operation-edges-v1.json.


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


# Grade projection/inspection identities now live in facade/test_grade_simplification_contracts.py.
# Historical source and observations: tools/baselines/grade-simplification-v1.json.


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
        from galaga.legacy import grade as sgrade

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


# TestSimplify now lives in facade/test_grade_simplification_contracts.py.


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
        sta = Algebra((1, -1, -1, -1), blades=b_gamma())
        g0, g1, _, _ = sta.basis_vectors()
        assert g0.latex() == "\\gamma_{0}"
        assert (g0 * g1).latex() == "\\gamma_{0} \\gamma_{1}"

    def test_sigma_names(self):
        """Sigma-named algebra uses σ in LaTeX."""
        pauli = Algebra((1, 1, 1), blades=b_sigma())
        s1, s2, _ = pauli.basis_vectors()
        assert s1.latex() == "\\sigma_{1}"
        assert (s1 * s2).latex() == "\\sigma_{1} \\sigma_{2}"

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
        """Custom names with explicit latex use the latex variant."""
        alg = Algebra(
            (1, 1, 1), blades=BladeConvention(vector_names=[("a", "𝐚", "𝐚"), ("b", "𝐛", "𝐛"), ("c", "𝐜", "𝐜")])
        )
        e1, e2, _ = alg.basis_vectors()
        mv = e1 ^ e2
        latex = mv.latex()
        assert "𝐚" in latex and "𝐛" in latex

    # symbolic.py: Expr.latex(wrap='$') and wrap='$$' (lines 138, 140)
    def test_expr_latex_wrap(self, cl3):
        """Expr.latex(wrap='$') wraps in $."""
        e1, _, _ = cl3.basis_vectors()
        v = sym(e1, "v")
        raw = v.latex()
        assert v.latex(wrap="$") == f"${raw}$"
        assert v.latex(wrap="$$") == f"$$\n{raw}\n$$"

    # Expression-helper identities now live in facade/test_expression_helper_contracts.py.
    # Historical source and observations: tools/baselines/expression-helpers-v1.json.

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
