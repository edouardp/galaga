"""Concrete v2 display policies, with v1-only formatting recorded in the archive."""

from __future__ import annotations

import numpy as np
import pytest

from galaga import Algebra, DisplayPolicy, exp, p_sta


@pytest.mark.parametrize("signature", ((1, 1, 1), (1, -1, -1, -1), (1, 1, 1, 0)))
def test_algebra_repr_identifies_its_numeric_owner_and_metric_metadata(signature) -> None:
    algebra = Algebra(signature)
    assert repr(algebra) == f"Algebra(numeric={algebra.numeric!r})"
    assert algebra.signature == signature
    np.testing.assert_array_equal(algebra.gram, np.diag(signature))


def test_multivector_repr_is_ascii_while_str_uses_unicode() -> None:
    algebra = Algebra(3)
    e1, e2, _ = algebra.basis_vectors()
    value = 3 + 2 * e1 - e2
    assert repr(value) == value.ascii() == "3 + 2e1 - e2"
    assert str(value) == value.unicode() == "3 + 2e₁ - e₂"
    assert repr(algebra.scalar(0)) == str(algebra.scalar(0)) == "0"
    g0, g1, _, _ = Algebra(config=p_sta()).basis_vectors()
    assert repr(g0 * g1) == "g0g1"
    assert str(g0 * g1) == "γ₀γ₁"


@pytest.mark.parametrize("precision, expected", ((4, "3.142e₁ + 2.718e₂"), (2, "3.1e₁ + 2.7e₂")))
def test_display_policy_controls_significant_digits_without_changing_coefficients(
    precision: int, expected: str
) -> None:
    algebra = Algebra(3)
    e1, e2, _ = algebra.basis_vectors()
    value = 3.14159 * e1 + 2.71828 * e2
    data = value.data.copy()
    presentation = algebra.presentation.with_display(DisplayPolicy(coefficient_precision=precision))
    assert value.display("value/unicode", presentation=presentation) == expected
    assert str(value) == "3.14159e₁ + 2.71828e₂"
    np.testing.assert_array_equal(value.data, data)


def test_scalar_and_zero_use_significant_digits_without_fixed_decimal_padding() -> None:
    algebra = Algebra(3, display=DisplayPolicy(coefficient_precision=3))
    assert str(algebra.scalar(3.14159)) == "3.14"
    assert str(algebra.scalar(0)) == "0"
    # Significant digits are not a replacement spelling for decimal places.
    assert str(algebra.scalar(0.00123456)) == "0.00123"
    assert str(algebra.scalar(12345.6)) == "1.23e+04"


@pytest.mark.parametrize("spec", (".0f", ".1f", ".2f", ".3f"))
def test_legacy_numeric_multivector_format_specs_are_not_v2_semantic_specs(spec: str) -> None:
    for value in (Algebra(1).scalar(3.14159), Algebra(1).scalar(0), Algebra(1).blade(1)):
        with pytest.raises(ValueError, match="format specification must be"):
            format(value, spec)


def test_semantic_format_targets_delegate_to_their_renderers() -> None:
    e1, _, _ = Algebra(3).basis_vectors()
    assert f"{e1}" == f"{e1:unicode}" == str(e1)
    assert f"{e1:latex}" == e1.latex() == r"e_{1}"
    assert f"{e1:ascii}" == "e1"


def test_mixed_value_formatting_keeps_signs_and_all_components() -> None:
    algebra = Algebra(3, display=DisplayPolicy(coefficient_precision=1))
    e1, e2, _ = algebra.basis_vectors()
    value = 1 + 2 * e1 - 3 * (e1 ^ e2)
    assert str(value) == "1 + 2e₁ - 3e₁₂"
    assert value.latex() == r"1 + 2 e_{1} - 3 e_{12}"


def test_near_minus_one_coefficients_are_suppressed_without_rounding_the_value() -> None:
    algebra = Algebra(3)
    e1, e2, _ = algebra.basis_vectors(expr=True)
    generator = e1 ^ e2
    rotor = exp(-generator * np.pi / 2)
    transformed = rotor * (e1 + e2) * ~rotor
    assert transformed.expr is not None
    np.testing.assert_allclose(transformed.data, (-e1 - e2).data, atol=1e-12, rtol=0)
    original = transformed.data.copy()
    assert str(transformed) == "-e₁ - e₂"
    assert transformed.latex() == r"-e_{1} - e_{2}"
    # Also pin the floating-point boundary independently of platform libm.
    neighbor = algebra.multivector([0, -1.0, np.nextafter(-1.0, 0.0), 0, 0, 0, 0, 0])
    assert neighbor != -e1 - e2
    assert str(neighbor) == "-e₁ - e₂"
    precise = algebra.presentation.with_display(DisplayPolicy(coefficient_precision=17, zero_tolerance=0))
    assert neighbor.display("value/ascii", presentation=precise) == "-e1 - 0.99999999999999989e2"
    np.testing.assert_array_equal(transformed.data, original)
