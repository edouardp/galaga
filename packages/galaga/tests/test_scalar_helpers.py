"""Public scalar compositions and explicit v1 formatting boundaries.

All 51 historical method identities remain; ADR-109 archives their v1 source.
Tiny numeric values must be checked with zero absolute tolerance.
"""

import math

import numpy as np
import pytest

import galaga as ga
from galaga.expression import ScalarLiteral, evaluate
from galaga.rendering.latex import emit
from galaga.rendering.tree import Fraction, Literal

# Historical supplied values, not a new physical-constants catalogue.
CONSTANTS = {
    "pi": (math.pi, ga.Name("pi", "π", r"\pi")),
    "e": (math.e, ga.Name("e")),
    "tau": (math.tau, ga.Name("tau", "τ", r"\tau")),
    "h": (6.62607015e-34, ga.Name("h")),
    "hbar": (1.054571817e-34, ga.Name("hbar", "ℏ", r"\hbar")),
    "c": (299792458.0, ga.Name("c")),
}


def constant(algebra, key):
    if key == "sqrt2":
        return ga.scalar_sqrt(algebra.scalar(2, expr=True))
    value, name = CONSTANTS[key]
    return algebra.scalar(value, expr=True).named(name)


def assert_scalar(value, expected):
    assert np.isfinite(expected) and np.isfinite(value.data).all()
    assert float(value) == pytest.approx(expected, rel=1e-15, abs=0)
    np.testing.assert_array_equal(value.data[1:], 0)


@pytest.fixture
def alg():
    return ga.Algebra(3, display=ga.DisplayPolicy(zero_tolerance=0))


class TestFraction:
    def test_half_value(self, alg):
        assert_scalar(alg.scalar(1, expr=True) / 2, 0.5)

    def test_half_latex(self, alg):
        # Literal arithmetic folds; a layout tree is not exact arithmetic.
        assert (alg.scalar(1, expr=True) / 2).latex(content="expr") == "0.5"
        assert emit(Fraction(Literal(1), Literal(2))) == r"\frac{1}{2}"

    def test_half_display(self, alg):
        value = alg.scalar(1, expr=True) / 2
        assert value.expr.operation_id == "scalar_divide"
        assert value.expr.operands == (ScalarLiteral(1),)
        assert evaluate(value.expr, algebra=alg) == value

    def test_third(self, alg):
        assert_scalar(alg.scalar(1, expr=True) / 3, 1 / 3)

    def test_negative_numerator(self, alg):
        assert_scalar(alg.scalar(-1, expr=True) / 2, -0.5)

    def test_negative_denominator(self, alg):
        assert_scalar(alg.scalar(1, expr=True) / -2, -0.5)

    def test_zero_numerator(self, alg):
        assert_scalar(alg.scalar(0, expr=True) / 3, 0)

    def test_zero_denominator_raises(self, alg):
        with pytest.raises(ZeroDivisionError, match="zero"):
            alg.scalar(1, expr=True) / 0

    def test_large_numbers(self, alg):
        assert_scalar(alg.scalar(355, expr=True) / 113, 355 / 113)

    def test_frac_alias(self, alg):
        assert not hasattr(alg, "frac") and not hasattr(alg, "fraction")
        assert_scalar(alg.scalar(1) / 2, 0.5)

    def test_in_expression(self, alg):
        e1, _, _ = alg.basis_vectors(expr=True)
        result = (alg.scalar(1, expr=True) / 2) * e1
        assert result.expr is not None
        np.testing.assert_array_equal(result.data, (0.5 * e1).data)
        assert evaluate(result.expr, algebra=alg) == result

    def test_in_exp(self, alg):
        e1, e2, _ = alg.basis_vectors(expr=True)
        plane = (e1 ^ e2).named("B")
        assert plane * plane == -1
        rotor = ga.exp(-plane / 2)
        np.testing.assert_allclose(rotor.data, (math.cos(0.5) - math.sin(0.5) * plane).data, rtol=1e-15, atol=0)
        assert rotor.latex(content="expr") == r"e^{-B/2}"
        np.testing.assert_array_equal(evaluate(rotor.expr, algebra=alg, environment={"B": plane}).data, rotor.data)


class TestScalarConstants:
    def test_pi_value(self, alg):
        assert_scalar(constant(alg, "pi"), math.pi)

    def test_pi_latex(self, alg):
        assert constant(alg, "pi").latex(content="name") == r"\pi"

    def test_pi_lazy(self, alg):
        assert constant(alg, "pi").expr == ScalarLiteral(math.pi)
        assert not hasattr(alg, "pi")

    def test_e_value(self, alg):
        assert_scalar(constant(alg, "e"), math.e)

    def test_e_latex(self, alg):
        assert constant(alg, "e").latex(content="name") == "e"

    def test_tau_value(self, alg):
        assert_scalar(constant(alg, "tau"), 2 * math.pi)

    def test_tau_latex(self, alg):
        assert constant(alg, "tau").latex(content="name") == r"\tau"

    def test_sqrt2_value(self, alg):
        assert_scalar(constant(alg, "sqrt2"), math.sqrt(2))

    def test_sqrt2_latex(self, alg):
        assert constant(alg, "sqrt2").latex(content="expr") == r"\sqrt{2}"

    def test_sqrt2_lazy(self, alg):
        value = constant(alg, "sqrt2")
        assert value.expr.operation_id == "scalar_sqrt"
        np.testing.assert_array_equal(evaluate(value.expr, algebra=alg).data, value.data)

    def test_h_value(self, alg):
        assert_scalar(constant(alg, "h"), 6.62607015e-34)

    def test_h_latex(self, alg):
        assert constant(alg, "h").latex(content="name") == "h"

    def test_hbar_value(self, alg):
        assert_scalar(constant(alg, "hbar"), 1.054571817e-34)

    def test_hbar_latex(self, alg):
        assert constant(alg, "hbar").latex(content="name") == r"\hbar"

    def test_c_value(self, alg):
        assert_scalar(constant(alg, "c"), 299792458.0)

    def test_c_latex(self, alg):
        assert constant(alg, "c").latex(content="name") == "c"

    def test_constants_in_expressions(self, alg):
        hbar, c = constant(alg, "hbar"), constant(alg, "c")
        value = hbar * c
        assert_scalar(value, 1.054571817e-34 * 299792458.0)
        assert value.latex(content="expr") == r"\hbar c"
        np.testing.assert_array_equal(
            evaluate(value.expr, algebra=alg, environment={"hbar": hbar, "c": c}).data, value.data
        )
        with pytest.raises(KeyError, match="no value supplied"):
            evaluate(value.expr, algebra=alg)

    def test_pi_in_fraction(self, alg):
        pi = constant(alg, "pi")
        half_pi = pi / 2
        assert half_pi.latex(content="expr") == r"\frac{\pi}{2}"
        assert_scalar(evaluate(half_pi.expr, algebra=alg, environment={"pi": pi}), math.pi / 2)


class TestScientificNotationStyle:
    def test_default_is_times(self, alg):
        assert alg.scalar(1.2e-7).latex() == r"1.2 \times 10^{-7}"
        assert not hasattr(alg.presentation.notation, "scientific")

    def test_times_style(self, alg):
        assert (1.2e-7 * alg.blade(1)).latex() == r"1.2 \times 10^{-7} e_{1}"

    def test_cdot_style(self, alg):
        with pytest.raises(TypeError):
            ga.Notation(scientific="cdot")

    def test_raw_style(self, alg):
        with pytest.raises(TypeError):
            ga.Notation(scientific="raw")
        assert alg.scalar(1.2e-7).ascii() == "1.2e-07"

    def test_invalid_style_raises(self, alg):
        with pytest.raises(TypeError):
            ga.Notation(scientific="invalid")

    def test_non_scientific_unaffected(self, alg):
        assert (0.5 * alg.blade(1)).latex() == "0.5 e_{1}"

    def test_coeff_format_respects_style(self, alg):
        value = alg.scalar(1.2e-7)
        with pytest.raises(TypeError, match="coeff_format"):
            value.latex(coeff_format=".3e")
        assert format(float(value), ".3e") == "1.200e-07"


class TestSciLnode:
    def test_times_style(self):
        assert emit(Literal(1.2e-6)) == r"1.2 \times 10^{-6}"

    def test_cdot_style(self):
        with pytest.raises(TypeError):
            ga.Notation(scientific="cdot")
        assert emit(Literal(1.2e-6)) == r"1.2 \times 10^{-6}"

    def test_raw_style(self):
        from galaga.rendering.ascii import emit as ascii_emit

        assert ascii_emit(Literal(1.2e-6)) == "1.2e-06"

    def test_mantissa_one(self):
        assert emit(Literal(1e-34)) == "10^{-34}"

    def test_positive_exponent(self):
        assert emit(Literal(3e8)) == r"3 \times 10^{8}"

    def test_negative_mantissa(self):
        assert emit(Literal(-1.2e-6)) == r"-1.2 \times 10^{-6}"

    def test_non_scientific_passthrough(self):
        assert emit(Literal(42)) == "42"

    def test_decimal_passthrough(self):
        assert emit(Literal(0.5)) == "0.5"


class TestCoeffLnode:
    def test_simple_coeff(self):
        assert (0.5 * ga.Algebra(1).blade(1)).latex() == "0.5 e_{1}"

    def test_unit_coeff_suppressed(self):
        assert ga.Algebra(1).blade(1).latex() == "e_{1}"

    def test_neg_unit_coeff(self):
        assert (-ga.Algebra(1).blade(1)).latex() == "-e_{1}"

    def test_scientific_coeff(self):
        assert (1.2e-7 * ga.Algebra(1).blade(1)).latex() == r"1.2 \times 10^{-7} e_{1}"

    def test_scalar_no_blade(self):
        assert ga.Algebra(1).scalar(3.14).latex() == "3.14"

    def test_coeff_format(self):
        value = 1.2e-6 * ga.Algebra(1).blade(1)
        presentation = value.algebra.presentation.with_display(ga.DisplayPolicy(coefficient_precision=4))
        assert value.display("value/latex", presentation=presentation) == r"1.2 \times 10^{-6} e_{1}"
        with pytest.raises(ValueError, match="format specification"):
            format(value, ".3e")
