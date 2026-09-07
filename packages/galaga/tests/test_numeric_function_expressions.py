"""Eager numeric functions preserve optional, replayable expression provenance."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import galaga as ga
from galaga.expression import BladeLiteral, Call, Symbol, evaluate

ARCHIVE = json.loads((Path(__file__).parents[1] / "tools/baselines/expression-contracts-v1.json").read_text())
HISTORY = {row["id"]: row for row in ARCHIVE["observations"]}


def _assert_coefficients(actual, expected) -> None:
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.shape == expected.shape, "coefficient shape changed"
    assert np.isfinite(actual).all() and np.isfinite(expected).all(), "nonfinite coefficient"
    np.testing.assert_allclose(actual, expected, rtol=0, atol=1e-12)


def test_sqrt_of_expression_rotor_preserves_provenance_and_value() -> None:
    algebra = ga.Algebra(3)
    e1, e2, _ = algebra.basis_vectors(expr=True)
    rotor = ga.exp(0.7 * (e1 ^ e2))
    root = ga.sqrt(rotor)

    assert root.expr == Call("sqrt", (rotor.expr,))
    assert rotor.expr == Call(
        "exp",
        (Call("scalar_multiply", (Call("outer_product", (BladeLiteral(1), BladeLiteral(2))),), {"scalar": 0.7}),),
    )
    _assert_coefficients(root.data, HISTORY["rotor-root"]["coefficients"])
    # An independent scalar trigonometric oracle, not sqrt(exp(...)) again.
    expected = np.zeros(algebra.dim)
    expected[[0, 3]] = [np.cos(0.35), np.sin(0.35)]
    _assert_coefficients(root.data, expected)
    _assert_coefficients((root * root).data, rotor.data)
    _assert_coefficients(evaluate(root.expr, algebra=algebra).data, expected)
    assert root.display("expr/ascii") == "sqrt(exp(0.7e1 ^ e2))"
    assert root.display("expr/unicode") == "√(exp(0.7e₁ ∧ e₂))"
    assert root.display("expr/latex") == HISTORY["rotor-root"]["renderings"]["latex"]


@pytest.mark.parametrize(
    "gram",
    (
        ((1, 0), (0, 1)),
        ((1, 0), (0, 0)),
        ((2, 0.5), (0.5, 1)),
        ((0, -1), (-1, 0)),
    ),
    ids=("elliptic", "nilpotent", "oblique-elliptic", "native-null-hyperbolic"),
)
@pytest.mark.parametrize("atol", (1e-12, 1e-10))
def test_tracked_rotor_roots_derive_their_branch_from_the_gram_matrix(gram, atol: float) -> None:
    algebra = ga.Algebra(gram=gram)
    e1, e2 = algebra.basis_vectors(expr=True)
    bivector = e1 ^ e2
    square = algebra.gram[0, 1] ** 2 - algebra.gram[0, 0] * algebra.gram[1, 1]
    assert float(bivector * bivector) == pytest.approx(square)
    expected_square = np.zeros(algebra.dim)
    expected_square[0] = square
    _assert_coefficients(algebra.numeric.left_action(bivector.numeric) @ bivector.data, expected_square)

    # exp(t B) lies in span(1, B). Derive its half-parameter root using B²,
    # including the nilpotent branch, without calling either numeric function.
    expected = np.zeros(algebra.dim)
    half_parameter = 0.35
    if square < 0:
        frequency = np.sqrt(-square)
        expected[[0, 3]] = [np.cos(half_parameter * frequency), np.sin(half_parameter * frequency) / frequency]
    elif square > 0:
        frequency = np.sqrt(square)
        expected[[0, 3]] = [np.cosh(half_parameter * frequency), np.sinh(half_parameter * frequency) / frequency]
    else:
        expected[[0, 3]] = [1, half_parameter]

    rotor = ga.exp(0.7 * bivector)
    root = ga.sqrt(rotor, atol=atol)
    assert root.expr == Call("sqrt", (rotor.expr,), {} if atol == 1e-12 else {"atol": atol})
    _assert_coefficients(root.data, expected)
    _assert_coefficients((root * root).data, rotor.data)
    _assert_coefficients(evaluate(root.expr, algebra=algebra).data, expected)


def test_scalar_sqrt_builds_and_renders_an_expression() -> None:
    algebra = ga.Algebra(3)
    scalar = algebra.scalar(9).named("s")
    assert scalar.expr is None
    result = ga.scalar_sqrt(scalar)

    assert result.expr == Call("scalar_sqrt", (Symbol("s"),))
    _assert_coefficients(result.data, HISTORY["scalar-root"]["coefficients"])
    assert result.display("expr/ascii") == "sqrt(s)"
    assert result.display("expr/unicode") == HISTORY["scalar-root"]["renderings"]["unicode"]
    assert result.display("expr/latex") == HISTORY["scalar-root"]["renderings"]["latex"]
    assert str(result) == "3"  # tracking alone does not replace concrete display
    assert result.latex() == "3"
    assert float(evaluate(result.expr, algebra=algebra, environment={"s": 16})) == 4
    assert float(result) == 3  # replay with another environment never mutates it
    with pytest.raises(KeyError, match="s"):
        evaluate(result.expr, algebra=algebra)


def test_scalar_sqrt_compound_expression_evaluates_and_displays() -> None:
    algebra = ga.Algebra(3)
    mass = algebra.scalar(3).named("m")
    momentum = algebra.scalar(4).named("p")
    energy = ga.scalar_sqrt(mass**2 + momentum**2).named("E")

    assert energy.expr == Call(
        "scalar_sqrt",
        (
            Call(
                "add", (Call("power", (Symbol("m"),), {"exponent": 2}), Call("power", (Symbol("p"),), {"exponent": 2}))
            ),
        ),
    )
    _assert_coefficients(energy.data, HISTORY["energy"]["coefficients"])
    assert float(evaluate(energy.expr, algebra=algebra, environment={"m": 3, "p": 4})) == 5
    assert float(evaluate(energy.expr, algebra=algebra, environment={"m": 5, "p": 12})) == 13
    assert float(energy) == 5
    assert energy.display("name/latex") == "E"
    assert energy.display("expr/ascii") == "sqrt(m^2 + p^2)"
    assert energy.display("expr/unicode") == "√(m² + p²)"
    assert energy.display("expr/latex") == r"\sqrt{m^2 + p^2}"
    assert energy.display("full/latex") == r"E \quad = \quad \sqrt{m^2 + p^2} \quad = \quad 5"
    assert energy.latex() == energy.display("full/latex")


def test_norm2_expression_has_semantic_text_and_latex_rendering() -> None:
    algebra = ga.Algebra(3)
    vector = algebra.blade(1).named("v")
    result = ga.norm2(vector)

    assert result.expr == Call("norm2", (Symbol("v"),))
    _assert_coefficients(result.data, HISTORY["norm2"]["coefficients"])
    assert result.display("expr/ascii") == "||v||^2"
    assert result.display("expr/unicode") == HISTORY["norm2"]["renderings"]["unicode"]
    assert result.display("expr/latex") == HISTORY["norm2"]["renderings"]["latex"]
    assert float(evaluate(result.expr, algebra=algebra, environment={"v": 3 * vector})) == 9


@pytest.mark.parametrize("operation", ("scalar_sqrt", "sqrt", "norm2", "exp"))
@pytest.mark.parametrize("named", (False, True))
@pytest.mark.parametrize("tracked", (False, True))
def test_numeric_functions_respect_all_four_name_and_tracking_states(
    operation: str, named: bool, tracked: bool
) -> None:
    algebra = ga.Algebra(1)
    value = algebra.scalar(4)
    if named:
        value = value.named("s")
    if tracked:
        value = value.with_expr()
    expression_before = value.expr
    result = getattr(ga, operation)(value)
    assert (result.expr is not None) == (named or tracked)
    assert result.name is None
    expected = {"scalar_sqrt": 2, "sqrt": 2, "norm2": 16, "exp": np.exp(4)}[operation]
    assert float(result) == pytest.approx(expected, rel=1e-14)
    if named or tracked:
        assert result.expr.operation_id == operation
        assert float(evaluate(result.expr, algebra=algebra, environment={"s": 4})) == pytest.approx(expected, rel=1e-14)
    assert value.expr is expression_before
    assert float(value) == 4


@pytest.mark.parametrize("operation", ("sqrt", "scalar_sqrt"))
@pytest.mark.parametrize("tracked", (False, True))
def test_invalid_square_roots_fail_eagerly_even_when_provenance_is_requested(operation: str, tracked: bool) -> None:
    value = ga.Algebra(1).scalar(-1, name="s", expr=tracked)
    with pytest.raises(ValueError, match="negative"):
        getattr(ga, operation)(value)
    assert float(value) == -1
