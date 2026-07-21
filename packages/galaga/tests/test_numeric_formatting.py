"""Formatting contracts for concrete legacy numeric values."""

from __future__ import annotations

import numpy as np
import pytest

from galaga.legacy import Algebra, b_gamma, exp


@pytest.fixture
def cl3():
    return Algebra((1, 1, 1))


def test_algebra_repr_summarizes_signature():
    assert repr(Algebra(3)) == "Cl(3,0)"
    assert repr(Algebra(1, 3)) == "Cl(1,3)"
    assert repr(Algebra((1, 1, 1, 0))) == "Cl(3,0,1)"


def test_multivector_repr_handles_zero_components_and_named_blades(cl3):
    e1, e2, _ = cl3.basis_vectors()
    value = 3 + 2 * e1 - e2

    assert repr(value) == str(value)
    assert all(fragment in repr(value) for fragment in ("3", "e₁", "e₂"))
    assert repr(cl3.scalar(0)) == "0"

    spacetime = Algebra((1, -1, -1, -1), blades=b_gamma(), repr_unicode=True)
    g0, g1, _, _ = spacetime.basis_vectors()
    assert "γ" in repr(g0 * g1)


@pytest.mark.parametrize(
    ("format_spec", "expected"),
    ((".3f", ("3.142", "2.718")), (".1f", ("3.1",))),
)
def test_numeric_format_spec_controls_coefficient_precision(cl3, format_spec, expected):
    e1, e2, _ = cl3.basis_vectors()
    value = 3.14159 * e1 + 2.71828 * e2
    rendered = format(value, format_spec)

    assert all(fragment in rendered for fragment in expected)


def test_scalar_and_zero_respect_numeric_format_specs(cl3):
    assert f"{cl3.scalar(3.14159):.2f}" == "3.14"
    assert f"{cl3.scalar(0):.3f}" == "0.000"


def test_semantic_format_targets_delegate_to_their_renderers(cl3):
    e1, _, _ = cl3.basis_vectors()

    assert f"{e1}" == str(e1)
    assert f"{e1:unicode}" == str(e1)
    assert f"{e1:latex}" == e1.latex()
    assert "e1" in f"{e1:ascii}"
    assert "₁" not in f"{e1:ascii}"


def test_mixed_value_formatting_keeps_signs_and_all_components(cl3):
    e1, e2, _ = cl3.basis_vectors()
    value = cl3.scalar(1) + 2 * e1 - 3 * (e1 ^ e2)
    rendered = f"{value:.0f}"

    assert all(fragment in rendered for fragment in ("1", "2", "3", "-"))


def test_near_minus_one_coefficients_are_suppressed_in_text_and_latex():
    algebra = Algebra((1, 1, 1))
    e1, e2, _ = algebra.basis_vectors(lazy=True)
    generator = e1 ^ e2
    rotor = exp(-generator * algebra.scalar(np.radians(180)) / 2)
    transformed = (rotor * (e1 + e2) * ~rotor).eval()

    assert str(transformed) == "-e₁ - e₂"
    assert transformed.latex() == "-e_{1} - e_{2}"
    assert "-1e" not in str(transformed)
    assert "-1 e" not in transformed.latex()
