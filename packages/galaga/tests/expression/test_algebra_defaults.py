"""Algebra factory defaults must not alter arithmetic or explicit opt-outs."""

from __future__ import annotations

import numpy as np
import pytest

from galaga import Algebra, DisplayPolicy, Notation, core, norm, norm2, presets
from galaga.cga import ConformalModel
from galaga.expression import BladeLiteral, Call, ScalarLiteral, Symbol, evaluate
from galaga.rga import RigidModel

FACTORIES = (
    ("scalar", (2,)),
    ("vector", ([1, 2],)),
    ("multivector", ([1, 2, 3, 4],)),
    ("blade", (1,)),
    ("blades", (1, 2, -1)),
    ("basis_vectors", ()),
    ("basis_blades", (2,)),
    ("pseudoscalar", ()),
    ("locals", ()),
)


def values_from(algebra, factory, args, **kwargs):
    # A signed blade is supplied as a value, not a negative bitmask.
    if factory == "blades":
        args = (1, 2, -algebra.blade(1, expr=False))
    result = getattr(algebra, factory)(*args, **kwargs)
    if factory == "locals":
        return tuple(result.values())
    return result if isinstance(result, tuple) else (result,)


@pytest.mark.parametrize("default", [False, True])
@pytest.mark.parametrize("factory,args", FACTORIES)
def test_every_factory_inherits_and_can_override_the_default(default, factory, args):
    algebra = Algebra(2, expr=default)
    assert algebra.expr is default
    reference = values_from(algebra, factory, args, expr=False)
    for kwargs, expected in (
        ({}, default),
        ({"expr": None}, default),
        ({"expr": True}, True),
        ({"expr": False}, False),
    ):
        values = values_from(algebra, factory, args, **kwargs)
        assert len(values) == len(reference) > 0
        for value, plain in zip(values, reference, strict=True):
            assert (value.expr is not None) is expected
            assert value.numeric.algebra is algebra.numeric
            assert value == plain and hash(value) == hash(plain)
            np.testing.assert_array_equal(value.data, plain.data)
            if value.expr is not None:
                environment = {value.name: plain} if value.name is not None else None
                np.testing.assert_array_equal(
                    evaluate(value.expr, algebra=algebra, environment=environment).data, plain.data
                )


@pytest.mark.parametrize("kwargs", [{}, {"expr": False}, {"expr": True}])
def test_identity_pseudoscalar_and_zero_dimension_follow_default(kwargs):
    for dimension in (0, 2):
        algebra = Algebra(dimension, **kwargs)
        assert algebra.expr is kwargs.get("expr", False)
        assert (algebra.identity.expr is not None) is algebra.expr
        assert (algebra.I.expr is not None) is algebra.expr
        np.testing.assert_array_equal(algebra.identity.data, algebra.numeric.identity.data)
        np.testing.assert_array_equal(algebra.I.data, algebra.numeric.I.data)
        if dimension == 0:
            assert algebra.basis_vectors() == ()
            if algebra.expr:
                assert algebra.I.expr == ScalarLiteral(1)


@pytest.mark.parametrize("use_recipe", [False, True])
def test_config_and_presentation_views_preserve_the_factory_default(use_recipe):
    recipe = presets.euclidean(2)
    algebra = Algebra(config=recipe if use_recipe else recipe.build(), expr=True)
    views = (
        algebra.with_presentation(algebra.presentation),
        algebra.with_notation(Notation.functional()),
        algebra.with_blades(presets.blades.indexed(2, prefix="v")),
        algebra.with_local_names(algebra.presentation.local_names),
        algebra.with_display_order(algebra.presentation.display_order),
        algebra.with_display(DisplayPolicy(content="full")),
    )
    for view in views:
        assert view.expr is True
        assert view.numeric is algebra.numeric and view.model is algebra.model
        assert view.blade(1).expr == BladeLiteral(1)
        assert view.blade(1, expr=False).expr is None
    with algebra.use_presentation(algebra.presentation.with_display(DisplayPolicy(content="value"))):
        assert algebra.expr is True and algebra.scalar(2).expr == ScalarLiteral(2)
    assert algebra.expr is True
    with pytest.raises(AttributeError):
        algebra.expr = False


def test_from_numeric_has_an_explicit_independent_default():
    numeric = core.Algebra(2)
    plain = Algebra.from_numeric(numeric)
    tracked = Algebra.from_numeric(numeric, expr=True)
    assert plain.numeric is tracked.numeric is numeric
    assert plain.expr is False and tracked.expr is True
    assert plain.scalar(1).expr is None
    assert tracked.scalar(1).expr == ScalarLiteral(1)
    assert (plain.blade(1) * tracked.blade(2)).expr is not None


@pytest.mark.parametrize("invalid", [None, 0, 1, "yes", np.bool_(True), ScalarLiteral(1)])
def test_constructor_requires_an_actual_boolean(invalid):
    for build in (
        lambda: Algebra(2, expr=invalid),
        lambda: Algebra(config=presets.euclidean(2), expr=invalid),
        lambda: Algebra.from_numeric(core.Algebra(2), expr=invalid),
    ):
        with pytest.raises(TypeError, match="expr must be a boolean"):
            build()


@pytest.mark.parametrize("factory,args", FACTORIES)
@pytest.mark.parametrize("invalid", [0, 1, "yes", np.bool_(False)])
def test_factory_overrides_do_not_accept_truthy_non_booleans(factory, args, invalid):
    with pytest.raises(TypeError, match="expr"):
        values_from(Algebra(2, expr=True), factory, args, expr=invalid)


@pytest.mark.parametrize("default", [False, True])
@pytest.mark.parametrize("factory,args", FACTORIES[:4])
def test_explicit_expression_overrides_either_default(default, factory, args):
    algebra = Algebra(2, expr=default)
    expression = Symbol("source")
    value = getattr(algebra, factory)(*args, expr=expression)
    assert value.expr is expression
    assert evaluate(value.expr, algebra=algebra, environment={"source": value}) == value


def test_basis_cache_never_leaks_tracking_between_requests():
    algebra = Algebra(2, expr=True)
    for _ in range(3):
        tracked = algebra.basis_vectors()
        plain = algebra.basis_vectors(expr=False)
        assert all(value.expr is not None for value in tracked)
        assert all(value.expr is None for value in plain)
        assert algebra.basis_vectors(expr=False) is plain
        assert all(a.numeric is b.numeric for a, b in zip(tracked, plain, strict=True))
    assert algebra.blades() == ()
    with pytest.raises(TypeError, match="expr"):
        algebra.blades(expr="yes")


@pytest.mark.parametrize(
    "gram", [np.eye(2), np.diag([1, -1]), [[2, 0.5], [0.5, 1]], [[0, -1], [-1, 0]], np.diag([1, 0])]
)
def test_tracked_arithmetic_replays_against_actual_core_products(gram):
    algebra = Algebra(gram=gram, expr=True)
    a, b = algebra.basis_vectors()
    result = (2 * a + b) * (a - 3 * b)
    core_a, core_b = algebra.numeric.basis_vectors()
    expected = (2 * core_a + core_b) * (core_a - 3 * core_b)
    assert isinstance(result.expr, Call)
    np.testing.assert_allclose(result.data, expected.data, atol=1e-12)
    for value in (result, norm2(a + b), norm(a + b)):
        replayed = evaluate(value.expr, algebra=algebra)
        np.testing.assert_allclose(replayed.data, value.data, atol=1e-12)
        assert replayed.expr is None, "Replay returns numeric results, not newly tracked literals"


def test_explicit_opt_out_survives_scalar_coercion_and_untracked_operations(monkeypatch):
    from galaga.facade import _numeric

    algebra = Algebra(2, expr=True)
    a, b = algebra.basis_vectors(expr=False)

    def forbidden(*args, **kwargs):
        raise AssertionError("Untracked arithmetic must not allocate expression nodes")

    monkeypatch.setattr(_numeric, "_literal_expression", forbidden)
    monkeypatch.setattr(_numeric, "Call", forbidden)
    for value in (a + 1, 1 + a, a - 1, 1 - a, 2 * a, a * 2, a / 2, 2 / a, a * b, a ^ b, -a, a.without_expr()):
        assert value.expr is None
    assert norm2(a).expr is None
    assert isinstance(norm(a), float)


def test_names_still_trigger_propagation_independently_of_factory_tracking():
    algebra = Algebra(2, expr=True)
    a = algebra.blade(1, name="a", expr=False)
    b = algebra.blade(2, expr=False)
    assert a.expr is None and b.expr is None
    assert (a * b).expr == Call("geometric_product", (Symbol("a"), BladeLiteral(2)))


@pytest.mark.parametrize(
    "model_type,recipe,point_factory", [(ConformalModel, presets.cga, "up"), (RigidModel, presets.rga, "point")]
)
@pytest.mark.parametrize("algebra_expr", [False, True])
@pytest.mark.parametrize("model_expr", [None, False, True])
def test_models_inherit_the_default_and_allow_overrides(model_type, recipe, point_factory, model_expr, algebra_expr):
    algebra = Algebra(config=recipe(), expr=algebra_expr)
    model = model_type(algebra, expr=model_expr)
    numeric_model = model_type(Algebra(config=recipe()))
    assert model.algebra is algebra
    effective = algebra_expr if model_expr is None else model_expr
    assert model.expr is effective
    assert model_type(algebra).expr is algebra_expr
    for override, expected in ((None, effective), (False, False), (True, True)):
        value = getattr(model, point_factory)((1, 2, 3), expr=override)
        reference = getattr(numeric_model, point_factory)((1, 2, 3))
        assert (value.expr is not None) is expected
        np.testing.assert_array_equal(value.data, reference.data)
        if expected:
            assert isinstance(value.expr, Call), (
                "Model provenance should describe the operation, not a literal snapshot"
            )
            replayed = evaluate(value.expr, algebra=algebra)
            np.testing.assert_allclose(replayed.data, reference.data, atol=1e-12)
            assert replayed.expr is None
        vector = model.euclidean_vector((1, 2, 3), expr=override)
        assert (vector.expr is not None) is expected
    plain_model = model_type(algebra, expr=False)
    point = getattr(plain_model, point_factory)((1, 2, 3))
    assert point.expr is None
    measurement = (
        plain_model.flat_bulk_norm(point) if isinstance(plain_model, ConformalModel) else plain_model.bulk_norm(point)
    )
    assert measurement.expr is None
