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
from galaga.legacy import sandwich as ssandwich
from galaga.legacy import sw as ssw_alias


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


# TestLatex now lives in rendering/test_coverage_latex_contracts.py.


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


# TestMultivectorLatex now lives in rendering/test_coverage_latex_contracts.py.


class TestCoverageGaps:
    """Tests targeting specific uncovered lines."""

    # Display identities now live in rendering/test_coverage_latex_contracts.py.
    # Historical source and observations: tools/baselines/coverage-latex-v1.json.

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
