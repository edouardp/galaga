"""Archived scalar evidence and nonvacuous small-value public contracts."""

import json
import math
import re
import runpy
from fractions import Fraction
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
from galaga.expression import evaluate
from galaga.rendering import ascii as ascii_renderer
from galaga.rendering import latex as latex_renderer
from galaga.rendering import unicode as unicode_renderer
from galaga.rendering.tree import Literal

ROOT = Path(__file__).parents[1]
ARCHIVE = json.loads((ROOT.parent / "tools/baselines/scalar-helpers-v1.json").read_text())
SOURCE = runpy.run_path(str(ROOT / "test_scalar_helpers.py"))
EMITTERS = {"ascii": ascii_renderer.emit, "unicode": unicode_renderer.emit, "latex": latex_renderer.emit}
SMALL = (
    np.nextafter(1e-12, 0),
    1e-12,
    np.nextafter(1e-12, np.inf),
    6.62607015e-34,
    -1.054571817e-34,
    -1e-34,
    np.nextafter(0.0, 1.0),
    np.nextafter(0.0, -1.0),
)


def assert_data(actual, expected):
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.shape == expected.shape
    assert np.isfinite(actual).all() and np.isfinite(expected).all()
    np.testing.assert_allclose(actual, expected, rtol=1e-15, atol=0)


def rendered_number(text):
    """Read just the supported scientific-number grammar, independently of GA."""
    match = re.fullmatch(r"(?:(-?[\d.]+) \\times )?10\^{(-?\d+)}", text)
    if match:
        mantissa, exponent = match.groups()
        return float(f"{mantissa or '1'}e{exponent}")
    if text.startswith("-10^{"):
        return -rendered_number(text[1:])
    return float(text)


def check_value(value, expected, target, environment=None):
    assert_data(value.data, expected)
    expression, value_hash = value.expr, hash(value)
    assert value.display("full/" + target)
    assert_data(value.data, expected)
    assert hash(value) == value_hash and value.expr is expression
    if expression is not None:
        assert_data(evaluate(expression, algebra=value.algebra, environment=environment).data, expected)


@pytest.mark.parametrize("row", ARCHIVE["fractions"])
@pytest.mark.parametrize("expr", (False, True))
@pytest.mark.parametrize("target", EMITTERS)
def test_archived_fractions_match_python_rational_rounding_and_replay(row, expr, target):
    algebra = ga.Algebra(3)
    value = algebra.scalar(row["numerator"], expr=expr) / row["denominator"]
    expected = float(Fraction(row["numerator"], row["denominator"]))
    assert float(value) == pytest.approx(expected, rel=1e-15, abs=0)
    check_value(value, row["data"], target)
    assert (value.expr is not None) == expr


@pytest.mark.parametrize("row", ARCHIVE["constants"], ids=lambda row: row["key"])
@pytest.mark.parametrize("expr", (False, True))
@pytest.mark.parametrize("target", EMITTERS)
def test_archived_constants_keep_nonzero_values_and_explicit_names(row, expr, target):
    algebra = ga.Algebra(3, display=ga.DisplayPolicy(zero_tolerance=0))
    value = SOURCE["constant"](algebra, row["key"])
    if not expr:
        value = value.without_expr()
    check_value(value, row["data"], target)
    assert float(value) != 0
    assert not hasattr(algebra, row["key"])
    if row["key"] != "sqrt2":
        assert value.display("name/" + target) == row["names"][target]
    elif expr:
        assert value.latex(content="expr") == row["latex"]
    # At default precision the output rounds, but does not erase the value.
    displayed = value.display("value/" + target)
    assert rendered_number(displayed) == float(format(row["data"][0], ".6g"))


@pytest.mark.parametrize("key", ARCHIVE["compositions"])
@pytest.mark.parametrize("target", EMITTERS)
def test_archived_scalar_compositions_have_numeric_oracles_and_explicit_replay(key, target):
    algebra = ga.Algebra(3, display=ga.DisplayPolicy(zero_tolerance=0))
    e1, e2, _ = algebra.basis_vectors(expr=True)
    plane = (e1 ^ e2).named("B")
    assert plane * plane == -1
    pi, hbar, c = (SOURCE["constant"](algebra, name) for name in ("pi", "hbar", "c"))
    values = {
        "half_vector": (algebra.scalar(1, expr=True) / 2) * e1,
        "rotor": ga.exp(-plane / 2),
        "hbar_c": hbar * c,
        "half_pi": pi / 2,
    }
    expected = {
        "half_vector": 0.5 * e1,
        "rotor": math.cos(0.5) - math.sin(0.5) * plane,
        "hbar_c": algebra.scalar(1.054571817e-34 * 299792458.0),
        "half_pi": algebra.scalar(math.pi / 2),
    }
    assert_data(values[key].data, expected[key].data)
    check_value(values[key], ARCHIVE["compositions"][key]["data"], target, {"B": plane, "pi": pi, "hbar": hbar, "c": c})


@pytest.mark.parametrize("row", [*ARCHIVE["scientific_nodes"], {"text": "-1e-34", "style": "times"}])
@pytest.mark.parametrize("target", EMITTERS)
def test_public_literals_preserve_scientific_magnitudes_without_legacy_string_padding(row, target):
    value = float(row["text"])
    rendered = EMITTERS[target](Literal(value))
    assert rendered_number(rendered) == float(format(value, ".6g"))
    assert "1.200" not in rendered
    if row["style"] != "times":
        with pytest.raises(TypeError):
            ga.Notation(scientific=row["style"])


@pytest.mark.parametrize("row", ARCHIVE["coefficient_nodes"])
@pytest.mark.parametrize("target", EMITTERS)
def test_public_coefficient_values_and_historical_padding_boundary(row, target):
    algebra = ga.Algebra(1)
    value = row["value"] * algebra.blade(1) if row["blade"] else algebra.scalar(row["value"])
    expected = [0, row["value"]] if row["blade"] else [row["value"], 0]
    check_value(value, expected, target)
    if row["format"] is None:
        assert value.latex() == row["latex"]
    else:
        assert "1.200" in row["latex"]
        assert "1.200" not in value.latex()
        with pytest.raises(TypeError, match="coeff_format"):
            value.latex(coeff_format=row["format"])


@pytest.mark.parametrize("number", SMALL)
@pytest.mark.parametrize("expr", (False, True))
@pytest.mark.parametrize("target", EMITTERS)
def test_display_threshold_and_subnormal_values_do_not_change_storage_or_equality(number, expr, target):
    algebra = ga.Algebra(1)
    value = algebra.scalar(number, expr=expr)
    original, original_hash = value.data.copy(), hash(value)
    assert value != 0 and value != algebra.scalar(0)
    assert hash(value) == hash(float(number))
    default = value.display("value/" + target)
    assert (default == "0") == (abs(number) < algebra.presentation.display.zero_tolerance)
    precise = algebra.presentation.with_display(ga.DisplayPolicy(zero_tolerance=0, coefficient_precision=17))
    rendered = value.display("value/" + target, presentation=precise)
    assert rendered_number(rendered) == number
    np.testing.assert_array_equal(value.data, original)
    assert hash(value) == original_hash
    if expr:
        np.testing.assert_array_equal(evaluate(value.expr, algebra=algebra).data, original)


@pytest.mark.parametrize("gram", (((2, 0.5), (0.5, -1)), ((1, 0), (0, 0))))
@pytest.mark.parametrize("number", (6.62607015e-34, -1.054571817e-34, np.nextafter(0.0, 1.0)))
@pytest.mark.parametrize("target", EMITTERS)
def test_tiny_mixed_grade_values_retain_every_stored_component(gram, number, target):
    algebra = ga.Algebra(gram=gram, display=ga.DisplayPolicy(zero_tolerance=0, coefficient_precision=17))
    e1, e2 = algebra.basis_vectors(expr=True)
    plane = e1 ^ e2
    assert plane * plane == gram[0][1] ** 2 - gram[0][0] * gram[1][1]
    value = number * (2 + e1 - e2 + plane)
    expected = np.array([2, 1, -1, 1]) * number
    check_value(value, expected, target)
    assert np.count_nonzero(value.data) == 4
    assert value != algebra.scalar(0)
    # A precision-preserving display must include all four nonzero terms.
    from galaga.rendering import value_tree

    tree = value_tree(value)
    assert len(tree.terms) == 4


def test_fraction_display_and_named_scalar_values_are_not_exact_rational_arithmetic():
    algebra = ga.Algebra(1)
    third = algebra.scalar(1, expr=True) / 3
    assert Fraction(float(third)) != Fraction(1, 3)
    assert third != Fraction(1, 3)
    numerator = algebra.scalar(1, expr=True).named("a")
    displayed = numerator / 3
    assert displayed.latex(content="expr") == r"\frac{a}{3}"
    assert_data(evaluate(displayed.expr, algebra=algebra, environment={"a": numerator}).data, third.data)
    with pytest.raises(KeyError, match="no value supplied"):
        evaluate(displayed.expr, algebra=algebra)
    assert_data(evaluate(displayed.expr, algebra=algebra, environment={"a": algebra.scalar(2)}).data, (2 * third).data)
    assert float(displayed) == float(third)  # Replay never mutates the stored value.


def test_named_scalar_does_not_turn_tracking_on_or_derive_a_physical_value():
    algebra = ga.Algebra(0)
    supplied = algebra.scalar(1.054571817e-34).named("hbar")
    assert supplied.expr is None
    assert supplied.with_expr().expr is not None
    derived = 6.62607015e-34 / math.tau
    assert float(supplied) != derived  # The archived rounded input is not h/(2*pi).
    assert float(supplied) == 1.054571817e-34
    assert not hasattr(algebra, "fraction")


@pytest.mark.parametrize("numerator", (0, 1, -1))
@pytest.mark.parametrize("denominator", (0.0, -0.0))
def test_zero_division_has_the_public_error_contract(numerator, denominator):
    algebra = ga.Algebra(0)
    assert ARCHIVE["zero_denominator_error"]["type"] == "ValueError"
    with pytest.raises(ZeroDivisionError, match="zero"):
        algebra.scalar(numerator, expr=True) / denominator
