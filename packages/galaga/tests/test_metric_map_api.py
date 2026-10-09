"""Metric maps remain algebra operations; component splits belong to models."""

import importlib
import inspect
import itertools

import numpy as np
import pytest

import galaga as ga
from galaga.models import ConformalModel


@pytest.mark.parametrize("name", ("bulk_part", "weight_part"))
@pytest.mark.parametrize("module_name", ("galaga", "galaga.facade", "galaga.facade._numeric", "galaga.core"))
def test_generic_component_names_are_not_public(module_name, name):
    module = importlib.import_module(module_name)
    assert not hasattr(module, name)
    assert name not in module.__all__
    assert name not in dir(module)
    with pytest.raises(ImportError, match=name):
        exec(f"from {module_name} import {name}", {})
    namespace = {}
    exec(f"from {module_name} import *", namespace)
    assert name not in namespace
    assert not hasattr(module.Algebra(3), name)


@pytest.mark.parametrize("name", ("bulk_part", "weight_part"))
def test_generic_component_ids_cannot_construct_or_replay_expressions(name):
    assert name not in ga.OPERATIONS
    with pytest.raises(KeyError, match=name):
        ga.get_operation(name)
    with pytest.raises(ValueError, match=name):
        ga.Call(name, (ga.Symbol("A"),))


@pytest.mark.parametrize("factory", (ga.presets.notation.default, ga.presets.notation.lengyel))
def test_builtin_notation_does_not_advertise_generic_components(factory):
    notation = factory()
    parameters = inspect.signature(ga.presets.notation.override).parameters
    for name in ("bulk_part", "weight_part"):
        assert name not in parameters
        for target in ("ascii", "unicode", "latex"):
            assert notation.rule(name, target) is None


@pytest.mark.parametrize("module_name", ("galaga", "galaga.core"))
@pytest.mark.parametrize(
    "gram",
    (np.zeros((3, 3)), np.diag([1, 1, 0]), np.array([[2, 0.5], [0.5, -1]])),
)
def test_metric_maps_follow_gram_minors(module_name, gram):
    api = importlib.import_module(module_name)
    algebra = api.Algebra(gram=gram)
    axes = [tuple(i for i in range(algebra.n) if mask & (1 << i)) for mask in range(algebra.dim)]
    matrix = np.zeros((algebra.dim, algebra.dim))
    for i, j in itertools.product(range(algebra.dim), repeat=2):
        if len(axes[i]) == len(axes[j]):
            matrix[i, j] = np.linalg.det(gram[np.ix_(axes[i], axes[j])])
    right = np.column_stack([api.right_complement(algebra.blade(mask)).data for mask in range(algebra.dim)])
    antimetric = right @ matrix @ right.T
    value = algebra.multivector(np.arange(1, algebra.dim + 1))
    np.testing.assert_allclose(api.metric_apply(value).data, matrix @ value.data, atol=1e-12, rtol=0)
    np.testing.assert_allclose(api.antimetric_apply(value).data, antimetric @ value.data, atol=1e-12, rtol=0)


def test_exterior_metric_maps_do_not_claim_a_component_decomposition():
    algebra = ga.Algebra(0, 0, 3, expr=True)
    e1 = algebra.blade(1)
    value = (2 + e1 + algebra.I).named("A")
    metric = ga.metric_apply(value)
    antimetric = ga.antimetric_apply(value)
    assert metric == 2
    assert antimetric == algebra.I
    assert metric + antimetric != value
    assert value - metric - antimetric == e1
    for result, operation in ((metric, "metric_apply"), (antimetric, "antimetric_apply")):
        assert result.expr is not None
        assert result.expr.operation_id == operation
        assert ga.evaluate(result.expr, algebra=algebra, environment={"A": value}) == result


@pytest.mark.parametrize("dimension", (2, 3))
def test_cga_component_methods_keep_their_semantic_ids_and_reconstruction(dimension):
    algebra = ga.Algebra(config=ga.presets.cga(dimension), expr=True)
    model = ConformalModel(algebra, expr=True)
    value = (model.origin + model.infinity + model.euclidean_basis_vectors()[0]).named("A")
    bulk, weight = model.bulk_part(value), model.weight_part(value)
    assert bulk + weight == value
    assert model.bulk_part(bulk) == bulk and model.weight_part(weight) == weight
    assert model.bulk_part(weight) == 0 and model.weight_part(bulk) == 0
    for result, operation in ((bulk, "conformal_bulk_part"), (weight, "conformal_weight_part")):
        assert result.expr is not None
        assert result.expr.operation_id == operation
        assert ga.evaluate(result.expr, algebra=algebra, environment={"A": value}) == result
