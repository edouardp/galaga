"""Operator and expanded CSTA provenance must describe the same algebra values."""

import pytest

from galaga import Algebra, presets
from galaga.expression import Call, evaluate
from galaga.models import ConformalSpacetimeModel


@pytest.fixture
def model() -> ConformalSpacetimeModel:
    return ConformalSpacetimeModel(Algebra(config=presets.csta(), user_config_files=False), expr=True)


def test_model_default_can_be_selected_without_mutating_an_existing_view(model):
    expanded = model.with_expression_form("expanded")
    compact = expanded.with_expression_form("operator")

    assert model.expression_form == compact.expression_form == "operator"
    assert expanded.expression_form == "expanded"
    assert expanded is not model
    assert expanded.algebra is model.algebra
    assert expanded.expr is model.expr
    assert compact.event(0, 0, 0, 0).latex(content="expr") == r"\operatorname{event}(0,\, 0,\, 0,\, 0)"
    assert r"\operatorname{event}" not in expanded.event(0, 0, 0, 0).latex(content="expr")


def test_named_event_preserves_coordinates_in_operator_form(model):
    event = model.event(0, 0, 0, 0).named("A_0", latex=r"A_0")

    assert event.latex(content="expr") == r"\operatorname{event}(0,\, 0,\, 0,\, 0)"
    assert event.latex(content="full") == r"A_0 \quad = \quad \operatorname{event}(0,\, 0,\, 0,\, 0) \quad = \quad n_o"
    assert event.expr is not None
    assert evaluate(event.expr, algebra=model.algebra) == event
    assert float(event * event) == 0


@pytest.mark.parametrize("method", ("event", "point", "up"))
def test_coordinate_inputs_and_call_overrides_replay_the_same_null_event(model, method):
    constructor = getattr(model, method)
    compact = constructor(2, 1, -3, 0.5)
    expanded = constructor(2, 1, -3, 0.5, expression_form="expanded")
    sequence = constructor((2, 1, -3, 0.5))
    generator = constructor(iter((2, 1, -3, 0.5)))
    overridden = getattr(model.with_expression_form("expanded"), method)(2, 1, -3, 0.5, expression_form="operator")

    assert compact == expanded == sequence == generator == overridden
    assert compact.expr == sequence.expr == generator.expr == overridden.expr
    assert compact.latex(content="expr") != expanded.latex(content="expr")
    assert model.expression_form == "operator"
    for value in (compact, expanded, overridden):
        assert value.expr is not None
        assert evaluate(value.expr, algebra=model.algebra) == value
        assert float(value * value) == pytest.approx(0)


def test_vector_event_provenance_retains_named_input_for_rebinding(model):
    position = model.spacetime_vector((2, 1, 0, 0)).named("q")
    replacement = model.spacetime_vector((3, 0, 2, 0))

    for expression_form in ("operator", "expanded"):
        event = model.event(position, expression_form=expression_form)
        assert event.expr is not None
        assert evaluate(event.expr, algebra=model.algebra, environment={"q": replacement}) == model.event(replacement)
    assert model.event(position).latex(content="expr") == r"\operatorname{event}(q)"


@pytest.mark.parametrize("expression_form", ("operator", "expanded"))
@pytest.mark.parametrize("tracking", (False, True))
def test_explicit_tracking_flags_control_both_expression_forms(model, expression_form, tracking):
    position = model.spacetime_vector((1, 2, 0, 0))
    for method in (model.event, model.up):
        value = method(position, expr=tracking, expression_form=expression_form)
        assert (value.expr is not None) is tracking
    value = model.signed_round(position, 4, expr=tracking, expression_form=expression_form)
    assert (value.expr is not None) is tracking


def test_untracked_model_constructions_remain_untracked():
    model = ConformalSpacetimeModel(Algebra(config=presets.csta(), user_config_files=False))
    for expression_form in ("operator", "expanded"):
        first = model.event(0, 0, 0, 0, expression_form=expression_form)
        second = model.event(1, 1, 0, 0, expression_form=expression_form)
        assert first.expr is None
        assert model.event_pair(first, second, expression_form=expression_form).expr is None
        assert model.flat_line(first, second, expression_form=expression_form).expr is None
        assert model.signed_round((0, 0, 0, 0), 1, expression_form=expression_form).expr is None


@pytest.mark.parametrize("method", ("event_pair", "flat_line"))
def test_geometric_constructions_replay_named_events_and_keep_expanded_products(model, method):
    first = model.event(0, 0, 0, 0).named("A")
    second = model.event(1, 1, 0, 0).named("B")
    replacement = model.event(2, 0, 1, 0)
    constructor = getattr(model, method)
    compact = constructor(first, second)
    expanded = constructor(first, second, expression_form="expanded")

    assert compact == expanded
    assert isinstance(compact.expr, Call)
    assert compact.expr.operation_id == method
    assert r"\wedge" in expanded.latex(content="expr")
    for value in (compact, expanded):
        assert value.expr is not None
        assert evaluate(value.expr, algebra=model.algebra, environment={"A": first, "B": replacement}) == constructor(
            first, replacement
        )
    raw_pair = constructor(first.without_expr(), second.without_expr(), expression_form="expanded")
    assert raw_pair.expr is not None


def test_signed_round_forms_replay_and_accept_a_coordinate_iterator(model):
    compact = model.signed_round(iter((2, 1, 0, 0)), 4)
    expanded = model.signed_round((2, 1, 0, 0), 4, expression_form="expanded")
    assert compact == expanded
    assert isinstance(compact.expr, Call)
    assert compact.expr.operation_id == "signed_round"
    for value in (compact, expanded):
        assert value.expr is not None
        assert evaluate(value.expr, algebra=model.algebra) == value
        assert float(value * value) == pytest.approx(4)


def test_invalid_expression_forms_are_rejected_even_without_tracking(model):
    with pytest.raises(ValueError, match="'operator' or 'expanded'"):
        model.with_expression_form("formula")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="must be a string"):
        ConformalSpacetimeModel(model.algebra, expression_form=1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="'operator' or 'expanded'"):
        model.event(0, 0, 0, 0, expr=False, expression_form="formula")  # type: ignore[arg-type]
