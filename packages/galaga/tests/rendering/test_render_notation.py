from __future__ import annotations

import pytest

from galaga.display import render
from galaga.expression import Call, Symbol
from galaga.facade import OPERATIONS, Algebra, geometric_product
from galaga.presentation import Notation, RenderRule, default_presentation
from galaga.presets import LengyelRGAPreset
from galaga.rendering import Call as RenderCall
from galaga.rendering import expression_tree


def _required_parameter(name: str) -> object:
    return {
        "exponent": 2,
        "order": 1,
        "scalar": 2,
        "target": 1,
        "targets": (0, 2),
    }[name]


@pytest.mark.parametrize("operation_id", tuple(OPERATIONS))
def test_every_catalog_operation_has_a_long_functional_fallback(operation_id: str) -> None:
    operation = OPERATIONS[operation_id]
    operands = tuple(Symbol(f"x{index}") for index in range(operation.expression_arity or 0))
    parameters = {
        parameter.name: _required_parameter(parameter.name) for parameter in operation.parameters if parameter.required
    }
    expression = Call(operation_id, operands, parameters)
    presentation = default_presentation(3).with_notation(Notation.functional())

    tree = expression_tree(expression, presentation)

    assert isinstance(tree, RenderCall)
    assert tree.function.ascii == operation_id


def test_short_functional_notation_is_optional_and_keeps_inner_products_distinct() -> None:
    presentation = default_presentation(1).with_notation(Notation.functional(short=True))

    rendered = {
        operation_id: render(
            Call(operation_id, (Symbol("a"), Symbol("b"))),
            target="ascii",
            presentation=presentation,
        )
        for operation_id in (
            "doran_lasenby_inner",
            "hestenes_inner",
            "metric_inner_product",
            "scalar_product",
        )
    }

    assert rendered == {
        "doran_lasenby_inner": "dl_inner(a, b)",
        "hestenes_inner": "h_inner(a, b)",
        "metric_inner_product": "metric_inner(a, b)",
        "scalar_product": "sp(a, b)",
    }


@pytest.mark.parametrize(
    "notation",
    (
        Notation.default(),
        Notation.doran_lasenby(),
        Notation.hestenes(),
        Notation.lengyel(),
        Notation.functional(),
        Notation.functional(short=True),
    ),
    ids=lambda notation: notation.id,
)
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_competing_inner_products_are_distinguishable_in_every_preset_and_target(
    notation: Notation,
    target: str,
) -> None:
    presentation = default_presentation(1).with_notation(notation)
    rendered = {
        render(
            Call(operation_id, (Symbol("a"), Symbol("b"))),
            target=target,
            presentation=presentation,
        )
        for operation_id in (
            "doran_lasenby_inner",
            "hestenes_inner",
            "metric_inner_product",
            "scalar_product",
        )
    }

    assert len(rendered) == 4


def test_notation_can_change_layout_without_changing_expression_or_numeric_identity() -> None:
    algebra = Algebra(2)
    x, y = (value.named(name) for value, name in zip(algebra.basis_vectors(expr=True), ("x", "y"), strict=True))
    value = geometric_product(x, y)
    expression_before = value.expr
    coefficients_before = value.data.copy()

    long = value.display(content="expr", target="ascii", notation=Notation.functional())
    short = value.display(content="expr", target="ascii", notation=Notation.functional(short=True))

    assert long == "geometric_product(x, y)"
    assert short == "gp(x, y)"
    assert value.expr is expression_before
    assert (value.data == coefficients_before).all()


def test_lengyel_preset_uses_target_specific_semantic_rules() -> None:
    presentation = LengyelRGAPreset().build().presentation
    expression = Call("geometric_product", (Symbol("a"), Symbol("b")))

    assert render(expression, target="ascii", presentation=presentation) == "gp(a, b)"
    assert render(expression, target="unicode", presentation=presentation) == "a ⟑ b"
    assert render(expression, target="latex", presentation=presentation) == r"a \mathbin{\text{⟑}} b"

    metric_apply = Call("metric_apply", (Symbol("a"),))
    assert render(metric_apply, target="unicode", presentation=presentation) == "Ga"
    assert render(metric_apply, target="latex", presentation=presentation) == r"\mathbf{G}a"


def test_every_declared_rule_has_complete_precedence_and_associativity_metadata() -> None:
    for notation in (
        Notation.default(),
        Notation.doran_lasenby(),
        Notation.hestenes(),
        Notation.lengyel(),
        Notation.functional(short=True),
    ):
        for operation_id, target, rule in notation.rules:
            assert operation_id in OPERATIONS
            assert target in {None, "ascii", "unicode", "latex"}
            assert isinstance(rule.precedence, int)
            assert rule.precedence >= 0
            assert rule.associativity in {"none", "left", "right", "associative"}


def test_notation_rules_are_immutable_and_target_overrides_are_persistent_views() -> None:
    base = Notation.functional()
    infix = RenderRule("infix", symbol="@", precedence=25, associativity="left")
    changed = base.with_rule("geometric_product", infix, target="ascii")

    assert base.rule("geometric_product", "ascii") is None
    assert changed.rule("geometric_product", "ascii") is infix
    assert changed.rule("geometric_product", "unicode") is None
    with pytest.raises(ValueError, match="target"):
        changed.rule("geometric_product", "html")


@pytest.mark.parametrize(
    "factory",
    (
        lambda: RenderRule("magic", symbol="?"),
        lambda: RenderRule("infix"),
        lambda: RenderRule("wrapper", opening="("),
        lambda: RenderRule("function", symbol="f", precedence=-1),
        lambda: RenderRule("function", symbol="f", argument_order=(0, 0)),
        lambda: Notation("bad", rules={("add", "html"): RenderRule("infix", symbol="+")}),
    ),
)
def test_invalid_notation_rules_fail_when_configuration_is_built(factory: object) -> None:
    with pytest.raises((TypeError, ValueError)):
        factory()  # type: ignore[operator]
