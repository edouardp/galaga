from __future__ import annotations

import pytest

from galaga.expression import BladeLiteral, Call, Expr, MultivectorLiteral, ScalarLiteral, Symbol, evaluate
from galaga.facade import Algebra, geometric_product


@pytest.mark.parametrize(
    "algebra",
    [
        Algebra(2),
        Algebra(1, 0, 1),
        Algebra(gram=((1, 0.25), (0.25, -1))),
        Algebra(gram=((0, -1), (-1, 0))),
    ],
    ids=("orthogonal", "degenerate", "oblique", "native-null"),
)
def test_generated_expression_round_trips_across_metric_families(algebra: Algebra) -> None:
    x, y = algebra.basis_vectors()
    x = x.named("x").with_expr()
    y = y.named("y")

    eager = geometric_product(x + y, y, x)
    assert eager.expr is not None
    evaluated = evaluate(eager.expr, algebra=algebra, environment={"x": x, "y": y})

    assert evaluated.almost_equal(eager)


def test_leaf_literals_evaluate_in_native_mask_order() -> None:
    algebra = Algebra(2)

    assert evaluate(ScalarLiteral(3), algebra=algebra) == algebra.scalar(3)
    assert evaluate(BladeLiteral(2, -1), algebra=algebra) == -algebra.blade(2)
    assert evaluate(MultivectorLiteral((1, 2, 3, 4)), algebra=algebra) == algebra.multivector([1, 2, 3, 4])


def test_missing_symbol_fails_clearly() -> None:
    with pytest.raises(KeyError, match="x"):
        evaluate(Symbol("x"), algebra=Algebra(1), environment={})


def test_symbol_from_another_algebra_fails_clearly() -> None:
    expression = Symbol("x")

    with pytest.raises(ValueError, match="different algebra"):
        evaluate(expression, algebra=Algebra(1), environment={"x": Algebra(1).blade(1)})


def test_literal_dimension_mismatches_fail_clearly() -> None:
    with pytest.raises(ValueError, match="coefficient count"):
        evaluate(MultivectorLiteral((1, 2, 3, 4)), algebra=Algebra(1))
    with pytest.raises(ValueError, match="outside algebra"):
        evaluate(BladeLiteral(4), algebra=Algebra(1))


def test_variadic_expression_uses_numeric_left_association() -> None:
    algebra = Algebra(2)
    x, y = algebra.basis_vectors()
    expression = Call(
        "geometric_product",
        (Call("geometric_product", (Symbol("x"), Symbol("y"))), Symbol("x")),
    )

    evaluated = evaluate(expression, algebra=algebra.numeric, environment={"x": x.numeric, "y": y.numeric})

    assert evaluated == (x.numeric * y.numeric) * x.numeric


def test_evaluation_accepts_name_keys_and_scalar_symbol_values() -> None:
    symbol = Symbol("s")
    algebra = Algebra(1)

    assert evaluate(symbol, algebra=algebra, environment={symbol.name: 2}) == algebra.scalar(2)


def test_invalid_evaluation_inputs_fail_clearly() -> None:
    algebra = Algebra(1)

    with pytest.raises(TypeError, match="expression"):
        evaluate(object(), algebra=algebra)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="algebra"):
        evaluate(ScalarLiteral(1), algebra=object())
    with pytest.raises(TypeError, match="scalar or multivector"):
        evaluate(Symbol("x"), algebra=algebra, environment={"x": object()})
    with pytest.raises(TypeError, match="unsupported expression"):
        evaluate(Expr(), algebra=algebra)
