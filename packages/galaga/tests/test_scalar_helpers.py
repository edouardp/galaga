"""Tests for Algebra scalar helpers: fraction(), pi, e_constant, hbar, etc."""

import numpy as np
import pytest

from galaga import Algebra


@pytest.fixture
def alg():
    return Algebra((1, 1, 1))


class TestFraction:
    """Algebra.fraction() and .frac() alias."""

    def test_half_value(self, alg):
        """fraction(1, 2) has value 0.5."""
        assert np.isclose(alg.fraction(1, 2).eval().scalar_part, 0.5)

    def test_half_latex(self, alg):
        """fraction(1, 2) renders as \\frac{1}{2}."""
        assert alg.fraction(1, 2).latex() == r"\frac{1}{2}"

    def test_half_display(self, alg):
        """fraction(1, 2) is lazy with expression tree."""
        f = alg.fraction(1, 2)
        assert f._is_symbolic

    def test_third(self, alg):
        """fraction(1, 3) has value 1/3."""
        assert np.isclose(alg.fraction(1, 3).eval().scalar_part, 1 / 3)

    def test_negative_numerator(self, alg):
        """fraction(-1, 2) has value -0.5."""
        f = alg.fraction(-1, 2)
        assert np.isclose(f.eval().scalar_part, -0.5)

    def test_negative_denominator(self, alg):
        """fraction(1, -2) has value -0.5."""
        f = alg.fraction(1, -2)
        assert np.isclose(f.eval().scalar_part, -0.5)

    def test_zero_numerator(self, alg):
        """fraction(0, 3) has value 0."""
        f = alg.fraction(0, 3)
        assert np.isclose(f.eval().scalar_part, 0.0)

    def test_zero_denominator_raises(self, alg):
        """fraction(1, 0) raises ValueError."""
        with pytest.raises(ValueError, match="zero"):
            alg.fraction(1, 0)

    def test_large_numbers(self, alg):
        """fraction(355, 113) ≈ π."""
        f = alg.fraction(355, 113)
        assert np.isclose(f.eval().scalar_part, 355 / 113)

    def test_frac_alias(self, alg):
        """frac() is an alias for fraction()."""
        assert np.isclose(alg.frac(1, 2).eval().scalar_part, 0.5)

    def test_in_expression(self, alg):
        """fraction works in lazy expressions."""
        e1, _, _ = alg.basis_vectors(lazy=True)
        result = alg.frac(1, 2) * e1
        assert result._is_symbolic
        assert np.isclose(result.eval().data[1], 0.5)

    def test_in_exp(self, alg):
        """fraction in exp renders with slash in superscript."""
        from galaga import exp

        e1, e2, _ = alg.basis_vectors(lazy=True)
        B = (e1 ^ e2).name("B")
        R = exp(-B * alg.frac(1, 2))
        latex = R.latex()
        assert "/" in latex or r"\frac" in latex


class TestScalarConstants:
    """Algebra.pi, .e_constant, .tau, .h, .hbar, .c."""

    def test_pi_value(self, alg):
        """pi has value π."""
        assert np.isclose(alg.pi.eval().scalar_part, np.pi)

    def test_pi_latex(self, alg):
        """pi renders as \\pi."""
        assert alg.pi.latex() == r"\pi"

    def test_pi_lazy(self, alg):
        """pi is lazy."""
        assert alg.pi._is_symbolic

    def test_e_value(self, alg):
        """e_constant has value e."""
        assert np.isclose(alg.e.eval().scalar_part, np.e)

    def test_e_latex(self, alg):
        """e_constant renders as e."""
        assert alg.e.latex() == "e"

    def test_tau_value(self, alg):
        """tau has value 2π."""
        assert np.isclose(alg.tau.eval().scalar_part, 2 * np.pi)

    def test_tau_latex(self, alg):
        """tau renders as \\tau."""
        assert alg.tau.latex() == r"\tau"

    def test_sqrt2_value(self, alg):
        """sqrt2 has value √2."""
        assert np.isclose(alg.sqrt2.eval().scalar_part, np.sqrt(2))

    def test_sqrt2_latex(self, alg):
        """sqrt2 renders as \\sqrt{2}."""
        assert alg.sqrt2.latex() == r"\sqrt{2}"

    def test_sqrt2_lazy(self, alg):
        """sqrt2 is lazy."""
        assert alg.sqrt2._is_symbolic

    def test_h_value(self, alg):
        """h has Planck constant value."""
        assert np.isclose(alg.h.eval().scalar_part, 6.62607015e-34)

    def test_h_latex(self, alg):
        """h renders as h."""
        assert alg.h.latex() == "h"

    def test_hbar_value(self, alg):
        """hbar has reduced Planck constant value."""
        assert np.isclose(alg.hbar.eval().scalar_part, 1.054571817e-34)

    def test_hbar_latex(self, alg):
        """hbar renders as \\hbar."""
        assert alg.hbar.latex() == r"\hbar"

    def test_c_value(self, alg):
        """c has speed of light value."""
        assert np.isclose(alg.c.eval().scalar_part, 299792458.0)

    def test_c_latex(self, alg):
        """c renders as c."""
        assert alg.c.latex() == "c"

    def test_constants_in_expressions(self, alg):
        """Constants work in lazy expressions."""
        E = alg.hbar * alg.c
        assert E._is_symbolic
        assert np.isclose(E.eval().scalar_part, 1.054571817e-34 * 299792458.0)

    def test_pi_in_fraction(self, alg):
        """pi/2 renders symbolically."""
        half_pi = alg.pi / alg.scalar(2).name("2")
        assert r"\pi" in half_pi.latex()


class TestScientificNotationStyle:
    """Notation.scientific controls LaTeX scientific notation rendering."""

    def test_default_is_times(self, alg):
        """Default style is 'times'."""
        assert alg.notation.scientific == "times"

    def test_times_style(self, alg):
        """'times' renders as \\times."""
        e1, _, _ = alg.basis_vectors()
        result = (1.2e-7 * e1).latex()
        assert r"\times 10^{-7}" in result

    def test_cdot_style(self, alg):
        """'cdot' renders as \\cdot."""
        alg.notation.scientific = "cdot"
        e1, _, _ = alg.basis_vectors()
        result = (1.2e-7 * e1).latex()
        assert r"\cdot 10^{-7}" in result

    def test_raw_style(self, alg):
        """'raw' passes through Python notation."""
        alg.notation.scientific = "raw"
        e1, _, _ = alg.basis_vectors()
        result = (1.2e-7 * e1).latex()
        assert "e-07" in result

    def test_invalid_style_raises(self, alg):
        """Unknown style raises ValueError."""
        with pytest.raises(ValueError):
            alg.notation.scientific = "invalid"

    def test_non_scientific_unaffected(self, alg):
        """Normal coefficients are not affected."""
        e1, _, _ = alg.basis_vectors()
        assert (0.5 * e1).latex() == "0.5 e_{1}"

    def test_coeff_format_respects_style(self, alg):
        """coeff_format also uses the notation style."""
        mv = alg.scalar(1.2e-7)
        result = mv.latex(coeff_format=".3e")
        assert r"\times 10^{-7}" in result


class TestSciLnode:
    """_sci_lnode produces correct LNode trees for scientific notation."""

    def test_times_style(self):
        """1.2e-06 → Seq with Sup(10, -6)."""
        from galaga.algebra import _sci_lnode
        from galaga.latex_emit import emit

        node = _sci_lnode("1.200e-06", "times")
        assert emit(node) == r"1.200 \times 10^{-6}"

    def test_cdot_style(self):
        """1.2e-06 with cdot → \\cdot."""
        from galaga.algebra import _sci_lnode
        from galaga.latex_emit import emit

        node = _sci_lnode("1.200e-06", "cdot")
        assert emit(node) == r"1.200 \cdot 10^{-6}"

    def test_raw_style(self):
        """raw style passes through unchanged."""
        from galaga.algebra import _sci_lnode
        from galaga.latex_emit import emit

        node = _sci_lnode("1.200e-06", "raw")
        assert emit(node) == "1.200e-06"

    def test_mantissa_one(self):
        """1e-34 → 10^{-34} (no mantissa)."""
        from galaga.algebra import _sci_lnode
        from galaga.latex_emit import emit

        node = _sci_lnode("1e-34", "times")
        assert emit(node) == "10^{-34}"

    def test_positive_exponent(self):
        """3e+08 → 3 \\times 10^{8}."""
        from galaga.algebra import _sci_lnode
        from galaga.latex_emit import emit

        node = _sci_lnode("3e+08", "times")
        assert emit(node) == r"3 \times 10^{8}"

    def test_negative_mantissa(self):
        """-1.2e-06 → -1.2 \\times 10^{-6}."""
        from galaga.algebra import _sci_lnode
        from galaga.latex_emit import emit

        node = _sci_lnode("-1.200e-06", "times")
        assert emit(node) == r"-1.200 \times 10^{-6}"

    def test_non_scientific_passthrough(self):
        """Plain number passes through as Text."""
        from galaga.algebra import _sci_lnode
        from galaga.latex_emit import emit

        node = _sci_lnode("42", "times")
        assert emit(node) == "42"

    def test_decimal_passthrough(self):
        """Decimal number passes through as Text."""
        from galaga.algebra import _sci_lnode
        from galaga.latex_emit import emit

        node = _sci_lnode("0.5", "times")
        assert emit(node) == "0.5"


class TestCoeffLnode:
    """_coeff_lnode produces correct LNode trees for coefficient × blade terms."""

    def test_simple_coeff(self):
        """0.5 e_{1}."""
        from galaga.algebra import _coeff_lnode
        from galaga.latex_emit import emit

        node = _coeff_lnode(0.5, "e_{1}", None, "times")
        assert emit(node) == "0.5 e_{1}"

    def test_unit_coeff_suppressed(self):
        """Coefficient 1.0 suppressed: e_{1} not 1 e_{1}."""
        from galaga.algebra import _coeff_lnode
        from galaga.latex_emit import emit

        node = _coeff_lnode(1.0, "e_{1}", None, "times")
        assert emit(node) == "e_{1}"

    def test_neg_unit_coeff(self):
        """Coefficient -1.0: -e_{1}."""
        from galaga.algebra import _coeff_lnode
        from galaga.latex_emit import emit

        node = _coeff_lnode(-1.0, "e_{1}", None, "times")
        assert emit(node) == "-e_{1}"

    def test_scientific_coeff(self):
        """1.2e-7 e_{1} with \\times."""
        from galaga.algebra import _coeff_lnode
        from galaga.latex_emit import emit

        node = _coeff_lnode(1.2e-7, "e_{1}", None, "times")
        result = emit(node)
        assert r"\times 10^{-7}" in result
        assert "e_{1}" in result

    def test_scalar_no_blade(self):
        """Pure scalar: just the number."""
        from galaga.algebra import _coeff_lnode
        from galaga.latex_emit import emit

        node = _coeff_lnode(3.14, "", None, "times")
        assert emit(node) == "3.14"

    def test_coeff_format(self):
        """Explicit coeff_format."""
        from galaga.algebra import _coeff_lnode
        from galaga.latex_emit import emit

        node = _coeff_lnode(1.2e-6, "e_{1}", ".3e", "times")
        result = emit(node)
        assert "1.200" in result
        assert r"\times 10^{-6}" in result
