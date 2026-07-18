from __future__ import annotations

import pytest

from galaga.expression import Call, ScalarLiteral, Symbol, evaluate, simplify
from galaga.facade import Algebra


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        (Call("add", (Symbol("x"), ScalarLiteral(0))), Symbol("x")),
        (Call("add", (ScalarLiteral(0), Symbol("x"))), Symbol("x")),
        (Call("subtract", (Symbol("x"), ScalarLiteral(0))), Symbol("x")),
        (Call("negate", (Call("negate", (Symbol("x"),)),)), Symbol("x")),
        (Call("negate", (ScalarLiteral(2),)), ScalarLiteral(-2)),
        (Call("scalar_multiply", (Symbol("x"),), {"scalar": 1}), Symbol("x")),
        (Call("scalar_multiply", (Symbol("x"),), {"scalar": 0}), ScalarLiteral(0)),
        (Call("scalar_multiply", (ScalarLiteral(2),), {"scalar": 3}), ScalarLiteral(6)),
        (Call("scalar_divide", (Symbol("x"),), {"scalar": 1}), Symbol("x")),
        (Call("scalar_divide", (ScalarLiteral(6),), {"scalar": 3}), ScalarLiteral(2)),
        (Call("power", (Symbol("x"),), {"exponent": 1}), Symbol("x")),
        (Call("power", (Symbol("x"),), {"exponent": 0}), ScalarLiteral(1)),
        (Call("power", (ScalarLiteral(2),), {"exponent": 3}), ScalarLiteral(8)),
        (Call("add", (ScalarLiteral(2), ScalarLiteral(3))), ScalarLiteral(5)),
        (Call("subtract", (ScalarLiteral(5), ScalarLiteral(3))), ScalarLiteral(2)),
    ],
)
def test_structural_identities_and_literal_folding(expression: Call, expected: object) -> None:
    assert simplify(expression) == expected


def test_simplification_preserves_evaluation_and_is_idempotent() -> None:
    algebra = Algebra(2)
    x = algebra.blade(1)
    expression = Call(
        "scalar_multiply",
        (Call("add", (Symbol("x"), ScalarLiteral(0))),),
        {"scalar": 1},
    )

    simplified = simplify(expression)

    assert evaluate(simplified, algebra=algebra, environment={"x": x}) == evaluate(
        expression,
        algebra=algebra,
        environment={"x": x},
    )
    assert simplify(simplified) == simplified


def test_noncommutative_order_is_never_changed() -> None:
    expression = Call("geometric_product", (Symbol("y"), Symbol("x")))

    assert simplify(expression) == expression


def test_nonassociative_operations_are_never_flattened() -> None:
    expression = Call("subtract", (Call("subtract", (Symbol("x"), Symbol("y"))), Symbol("z")))

    assert simplify(expression) == expression


def test_simplify_rejects_non_expression_input() -> None:
    with pytest.raises(TypeError, match="expression"):
        simplify(object())  # type: ignore[arg-type]


def test_unsafe_literal_folds_remain_explicit() -> None:
    division_by_zero = Call("scalar_divide", (ScalarLiteral(2),), {"scalar": 0})
    negative_power = Call("power", (ScalarLiteral(2),), {"exponent": -1})
    symbolic_scaling = Call("scalar_multiply", (Symbol("x"),), {"scalar": 2})

    assert simplify(division_by_zero) == division_by_zero
    assert simplify(negative_power) == negative_power
    assert simplify(symbolic_scaling) == symbolic_scaling
