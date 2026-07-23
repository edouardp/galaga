from __future__ import annotations

from collections.abc import Callable

import pytest

from galaga import Algebra, DisplayPolicy, Multivector, outer_product, p_lengyel_cga
from galaga.cga import CGAExpressionForm, ConformalModel
from galaga.expression import Call, evaluate


def _model(*, expression_form: CGAExpressionForm = "operator") -> ConformalModel:
    algebra = Algebra(
        config=p_lengyel_cga(),
        display=DisplayPolicy(content="full"),
    )
    return ConformalModel(
        algebra,
        expr=True,
        expression_form=expression_form,
    )


def _circle(cga: ConformalModel) -> Multivector:
    a = cga.up((0.0, 0.0, 0.0))
    b = cga.up((1.0, 0.0, 0.0))
    c = cga.up((0.0, 1.0, 0.0))
    return outer_product(a, b, c).named("C")


def test_model_selects_operator_provenance_by_default_and_can_derive_an_expanded_view() -> None:
    compact = _model()
    expanded = compact.with_expression_form("expanded")

    assert compact.expression_form == "operator"
    assert expanded.expression_form == "expanded"
    assert expanded is not compact
    assert expanded.algebra is compact.algebra
    assert expanded.expr is compact.expr is True

    with pytest.raises(ValueError, match="'operator' or 'expanded'"):
        compact.with_expression_form("formula")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="must be a string"):
        ConformalModel(compact.algebra, expression_form=1)  # type: ignore[arg-type]


def test_up_can_show_the_cga_operator_or_the_null_basis_embedding() -> None:
    compact = _model()
    expanded = compact.with_expression_form("expanded")

    operator_point = compact.up((1.0, 2.0, 3.0)).named("P")
    expanded_point = expanded.up((1.0, 2.0, 3.0)).named("P")
    overridden_point = compact.up(
        (1.0, 2.0, 3.0),
        expression_form="expanded",
    ).named("P")

    assert operator_point == expanded_point == overridden_point
    assert isinstance(operator_point.expr, Call)
    assert operator_point.expr.operation_id == "up"
    assert operator_point.latex(content="expr") == (
        r"\operatorname{up}(\mathbf{e}_{1} + 2 \mathbf{e}_{2} + 3 \mathbf{e}_{3})"
    )
    expected_expansion = (
        r"\mathbf{e}_{4} + \mathbf{e}_{1} + 2 \mathbf{e}_{2} + 3 \mathbf{e}_{3}"
        r" + \frac{\left(\mathbf{e}_{1} + 2 \mathbf{e}_{2} + 3 \mathbf{e}_{3}\right)^2"
        r" \mathbin{\text{⟑}} \mathbf{e}_{5}}{2}"
    )
    assert expanded_point.latex(content="expr") == expected_expansion
    assert overridden_point.latex(content="expr") == expected_expansion
    assert compact.expression_form == "operator"

    for point in (operator_point, expanded_point, overridden_point):
        assert point.expr is not None
        assert evaluate(point.expr, algebra=compact.algebra) == point


def test_explicit_expr_false_suppresses_both_expression_forms() -> None:
    cga = _model()

    assert cga.up((1.0, 2.0, 3.0), expr=False).expr is None
    assert (
        cga.up(
            (1.0, 2.0, 3.0),
            expr=False,
            expression_form="expanded",
        ).expr
        is None
    )


def test_round_point_retains_radius_in_both_executable_explanations() -> None:
    compact = _model()
    expanded = compact.with_expression_form("expanded")

    operator_point = compact.round_point(
        (1.0, 2.0, 3.0),
        radius_squared=4.0,
    )
    expanded_point = expanded.round_point(
        (1.0, 2.0, 3.0),
        radius_squared=4.0,
    )

    assert operator_point == expanded_point
    assert isinstance(operator_point.expr, Call)
    assert operator_point.expr.operation_id == "round_point"
    assert r"\operatorname{round\_point}" in operator_point.latex(content="expr")
    assert r"\operatorname{round\_point}" not in expanded_point.latex(content="expr")
    assert operator_point.expr is not None
    assert expanded_point.expr is not None
    assert evaluate(operator_point.expr, algebra=compact.algebra) == operator_point
    assert evaluate(expanded_point.expr, algebra=compact.algebra) == expanded_point


def test_semantic_geometry_helpers_can_expose_their_algebraic_definitions() -> None:
    compact = _model()
    expanded = compact.with_expression_form("expanded")
    circle = _circle(compact)

    operator_carrier = compact.carrier(circle)
    expanded_carrier = expanded.carrier(circle)
    operator_center = compact.center(circle)
    expanded_center = expanded.center(circle)

    assert operator_carrier == expanded_carrier
    assert operator_center == expanded_center
    assert operator_carrier.latex(content="expr") == r"\operatorname{car}(C)"
    assert expanded_carrier.latex(content="expr") == r"C \wedge \mathbf{e}_{5}"
    assert operator_center.latex(content="expr") == r"\operatorname{cen}(C)"
    assert expanded_center.latex(content="expr") == (
        r"\left(\overline{\mathbb{G}C} \wedge \mathbf{e}_{5}\right) \vee C"
    )

    for result in (operator_carrier, expanded_carrier, operator_center, expanded_center):
        assert result.expr is not None
        assert evaluate(
            result.expr,
            algebra=compact.algebra,
            environment={"C": circle},
        ).almost_equal(result)


@pytest.mark.parametrize(
    ("operation", "operator_id"),
    (
        (lambda cga, value: cga.weighted_center_norm(value), "weighted_center_norm"),
        (lambda cga, value: cga.weighted_radius_norm(value), "weighted_radius_norm"),
        (lambda cga, value: cga.carrier(value), "carrier"),
        (lambda cga, value: cga.cocarrier(value), "cocarrier"),
        (lambda cga, value: cga.center(value), "center"),
        (lambda cga, value: cga.flat_center(value), "flat_center"),
        (lambda cga, value: cga.container(value), "container"),
        (lambda cga, value: cga.partner(value), "partner"),
    ),
)
def test_operator_and_expanded_geometry_provenance_are_both_evaluable(
    operation: Callable[[ConformalModel, Multivector], Multivector],
    operator_id: str,
) -> None:
    compact = _model()
    expanded = compact.with_expression_form("expanded")
    circle = _circle(compact)

    operator_result = operation(compact, circle)
    expanded_result = operation(expanded, circle)

    assert operator_result.almost_equal(expanded_result)
    assert isinstance(operator_result.expr, Call)
    assert operator_result.expr.operation_id == operator_id
    assert expanded_result.expr is not None
    assert evaluate(
        operator_result.expr,
        algebra=compact.algebra,
        environment={"C": circle},
    ).almost_equal(operator_result)
    assert evaluate(
        expanded_result.expr,
        algebra=compact.algebra,
        environment={"C": circle},
    ).almost_equal(expanded_result)


def test_expanded_point_measurements_preserve_their_defining_formulas() -> None:
    compact = _model()
    expanded = compact.with_expression_form("expanded")
    point = (3.0 * compact.round_point((1.0, 2.0, 3.0), radius_squared=4.0)).named("Q")

    cases = (
        (expanded.weight(point), r"\frac{Q * \mathbf{e}_{5}}{-1}"),
        (expanded.homogenize(point), r"\frac{Q}{3}"),
        (expanded.radius_squared(point), r"\frac{-Q^2}{9}"),
    )

    for result, expected_latex in cases:
        assert result.latex(content="expr") == expected_latex
        assert result.expr is not None
        assert evaluate(
            result.expr,
            algebra=compact.algebra,
            environment={"Q": point},
        ).almost_equal(result)

    # ``down`` performs a coefficient projection, so there is no lower-level
    # generic GA expression to expose. It deliberately remains an atomic call.
    down = expanded.down(point)
    assert isinstance(down.expr, Call)
    assert down.expr.operation_id == "down"
