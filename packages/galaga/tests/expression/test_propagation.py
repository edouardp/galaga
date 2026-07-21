from __future__ import annotations

from typing import Any, cast

import pytest

from galaga.expression import Call, ScalarLiteral, Symbol, evaluate
from galaga.facade import (
    OPERATIONS,
    Algebra,
    Multivector,
    OperationSpec,
    _numeric,
    exp,
    geometric_product,
    inverse,
    log,
    norm,
    sqrt,
    unit,
)


def _arguments(operation_id: str, left: Multivector, right: Multivector) -> tuple[tuple[Any, ...], dict[str, Any]]:
    if operation_id in {"scalar_multiply", "scalar_divide"}:
        return (left, 2), {}
    if operation_id == "power":
        return (left, 2), {}
    if operation_id == "grade":
        return (left, 0), {}
    if operation_id == "grades":
        return (left, [0, 1]), {}
    if operation_id in {"transwedge", "transwedge_antiproduct"}:
        return (left, right, 0), {}
    if operation_id == "inverse":
        return (left,), {"rtol": 1e-9, "atol": 1e-11}
    if operation_id in {
        "is_basis_blade",
        "is_bivector",
        "is_even",
        "is_rotor",
        "is_scalar",
        "is_vector",
        "log",
        "sqrt",
        "unit",
    }:
        return (left,), {"atol": 1e-11}
    operation = OPERATIONS[operation_id]
    return ((left,) if operation.expression_arity == 1 else (left, right)), {}


@pytest.mark.parametrize("operation_id", tuple(OPERATIONS))
def test_every_catalog_operation_has_declared_expression_behavior(operation_id: str) -> None:
    algebra = Algebra(3)
    left = algebra.scalar(1, name="x", expr=True)
    right = algebra.scalar(1, name="y")
    args, kwargs = _arguments(operation_id, left, right)

    eager = _numeric._invoke(operation_id, *args, **kwargs)
    operation = OPERATIONS[operation_id]

    if isinstance(eager, Multivector):
        assert isinstance(eager.expr, Call)
        assert eager.expr.operation_id == operation_id
        evaluated = evaluate(eager.expr, algebra=algebra, environment={"x": left, "y": right})
        assert evaluated.almost_equal(eager)
    else:
        expression_values, parameters = operation.bind_expression_call(args, kwargs)
        expression = Call(operation_id, tuple(Symbol(value.name) for value in expression_values), parameters)
        evaluated = evaluate(expression, algebra=algebra, environment={"x": left, "y": right})
        assert evaluated == eager


def test_untracked_path_constructs_no_expression_node(monkeypatch: pytest.MonkeyPatch) -> None:
    algebra = Algebra(2)
    x, y = algebra.basis_vectors()

    def unexpected_node(*args: Any, **kwargs: Any) -> None:
        raise AssertionError("untracked evaluation constructed an expression node")

    for node_name in ("BladeLiteral", "Call", "MultivectorLiteral", "ScalarLiteral", "Symbol"):
        monkeypatch.setattr(_numeric, node_name, unexpected_node)

    result = geometric_product(x + y, x, y)

    assert result.expr is None


def test_one_numeric_evaluator_call_occurs_per_variadic_binary_edge(monkeypatch: pytest.MonkeyPatch) -> None:
    algebra = Algebra(2)
    x, y = algebra.basis_vectors(expr=True)
    calls = 0

    def evaluate_edge(left: Any, right: Any) -> Any:
        nonlocal calls
        calls += 1
        return left * right

    operation = OperationSpec(
        "geometric_product",
        2,
        evaluate_edge,
        OPERATIONS["geometric_product"].call_policy,
    )
    monkeypatch.setattr(_numeric, "get_operation", lambda operation_id: operation)

    result = _numeric._invoke("geometric_product", x, y, x)

    assert calls == 2
    assert isinstance(result.expr, Call)


def test_later_tracked_variadic_operand_retains_untracked_prefix() -> None:
    algebra = Algebra(3)
    x, y, z = (value.named(name) for value, name in zip(algebra.basis_vectors(), "xyz", strict=True))
    z = z.with_expr()

    result = geometric_product(x, y, z)

    assert result.expr == Call(
        "geometric_product",
        (
            Call("geometric_product", (Symbol("x"), Symbol("y"))),
            Symbol("z"),
        ),
    )


def test_single_variadic_operand_preserves_wrapper_and_provenance() -> None:
    value = Algebra(1).blade(1, name="x", expr=True)

    assert geometric_product(value) is value


def test_tracked_parameter_iterables_are_normalized_before_numeric_evaluation() -> None:
    algebra = Algebra(3)
    value = algebra.multivector(range(8), expr=True)
    targets = (target for target in (0, 2))

    result = _numeric.grades(value, targets)

    assert isinstance(result.expr, Call)
    assert result.expr.parameters == (("targets", (0, 2)),)
    assert evaluate(result.expr, algebra=algebra) == result


def test_reflected_addition_preserves_the_users_source_order_in_provenance() -> None:
    algebra = Algebra(2)
    a, b = (value.named(name) for value, name in zip(algebra.basis_vectors(expr=True), "ab", strict=True))

    result = 1 + a + (a ^ b)

    assert result.expr == Call(
        "add",
        (
            Call("add", (ScalarLiteral(1), Symbol("a"))),
            Call("outer_product", (Symbol("a"), Symbol("b"))),
        ),
    )


def test_named_scalar_survives_unary_negation_before_a_tracked_rotor_expression() -> None:
    algebra = Algebra((1, 1, 1))
    e1, e2, _ = algebra.basis_vectors(expr=True)
    theta = algebra.scalar(0.25).named("theta", latex=r"\theta")
    plane = (e1 ^ e2).named("B")

    rotor = exp(-theta * plane / 2)

    assert theta.expr is None
    assert rotor.expr == Call(
        "exp",
        (
            Call(
                "scalar_divide",
                (
                    Call(
                        "geometric_product",
                        (
                            Call("negate", (Symbol(theta.name),)),
                            Symbol(plane.name),
                        ),
                    ),
                ),
                {"scalar": 2},
            ),
        ),
    )
    assert rotor.latex(content="expr") == r"e^{-\theta B/2}"


def test_norm_lifts_only_semantic_inputs_to_a_scalar_multivector() -> None:
    algebra = Algebra((1, 1, 1))
    numeric = algebra.vector((3, 4, 0))
    named = numeric.named("v")

    numeric_norm = norm(numeric)
    semantic_norm = norm(named)

    assert type(numeric_norm) is float
    assert numeric_norm == 5.0
    assert isinstance(semantic_norm, Multivector)
    assert float(semantic_norm) == 5.0
    assert semantic_norm.expr == Call("norm", (Symbol(named.name),))
    assert semantic_norm.latex(content="full") == r"\lVert v \rVert \quad = \quad 5"
    assert evaluate(semantic_norm.expr, algebra=algebra, environment={"v": named}) == semantic_norm
    assert type(evaluate(semantic_norm.expr, algebra=algebra.numeric, environment={"v": named})) is float


def test_default_numeric_tolerances_do_not_leak_into_expression_provenance() -> None:
    algebra = Algebra(2)
    a, b = (value.named(name) for value, name in zip(algebra.basis_vectors(expr=True), "ab", strict=True))
    invertible = cast(Multivector, 2 + 0.25 * a)
    rotor = exp(cast(Multivector, 0.25 * (a ^ b)))

    results = (unit(a + b), inverse(invertible), log(rotor), sqrt(rotor))

    for result in results:
        assert isinstance(result, Multivector)
        assert isinstance(result.expr, Call)
        assert result.expr.parameters == ()


def test_nondefault_numeric_tolerances_remain_reproducible_expression_parameters() -> None:
    algebra = Algebra(1)
    (a,) = (value.named("a") for value in algebra.basis_vectors(expr=True))

    result = inverse(cast(Multivector, 2 + a), rtol=1e-8)

    assert isinstance(result.expr, Call)
    assert result.expr.parameters == (("rtol", 1e-8),)
    assert evaluate(result.expr, algebra=algebra, environment={"a": a}).almost_equal(result)
