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
        assert f._is_lazy

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
        assert result._is_lazy
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
        assert alg.pi._is_lazy

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
        assert E._is_lazy
        assert np.isclose(E.eval().scalar_part, 1.054571817e-34 * 299792458.0)

    def test_pi_in_fraction(self, alg):
        """pi/2 renders symbolically."""
        half_pi = alg.pi / alg.scalar(2).name("2")
        assert r"\pi" in half_pi.latex()
