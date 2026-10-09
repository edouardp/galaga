"""Public aliases, rejected spellings, and numeric call contracts."""

from __future__ import annotations

import importlib
import inspect
import warnings

import pytest

import galaga.facade as facade

CURATED_OPERATION_ALIASES = {
    "conjugate": "clifford_conjugate",
    "dorst_inner": "doran_lasenby_inner",
    "gp": "geometric_product",
    "join": "outer_product",
    "meet": "regressive_product",
    "op": "outer_product",
    "rev": "reverse",
    "sw": "sandwich",
    "wedge": "outer_product",
}
REMOVED_OPERATION_ALIASES = {
    "bulk_part": "metric_apply",
    "weight_part": "antimetric_apply",
    "involute": "grade_involution",
    "mag2": "norm2",
    "magnitude_squared": "norm2",
    "normalise": "unit",
    "normalize": "unit",
    "norm_squared": "norm2",
}


@pytest.mark.parametrize(
    "name",
    (
        "__abs__",
        "__add__",
        "__eq__",
        "__float__",
        "__format__",
        "__getitem__",
        "__hash__",
        "__init__",
        "__invert__",
        "__mul__",
        "__neg__",
        "__or__",
        "__pos__",
        "__pow__",
        "__radd__",
        "__repr__",
        "__rmul__",
        "__ror__",
        "__rsub__",
        "__rtruediv__",
        "__rxor__",
        "__str__",
        "__sub__",
        "__truediv__",
        "__xor__",
        "_repr_latex_",
        "display",
        "latex",
    ),
)
def test_multivector_protocol_and_display_hooks_are_callable(name):
    assert callable(getattr(facade.Multivector, name))


@pytest.mark.parametrize(("alias", "canonical"), tuple(CURATED_OPERATION_ALIASES.items()))
def test_permanent_concise_aliases_remain_exact_objects(alias: str, canonical: str) -> None:
    assert getattr(facade, alias) is getattr(facade, canonical)
    assert alias not in facade.OPERATIONS


@pytest.mark.parametrize("module_name", ("galaga", "galaga.facade", "galaga.core", "galaga.facade._numeric"))
@pytest.mark.parametrize(("alias", "canonical"), tuple(REMOVED_OPERATION_ALIASES.items()))
def test_removed_spellings_are_absent_from_attributes_imports_and_wildcard_exports(module_name, alias, canonical):
    module = importlib.import_module(module_name)
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        assert not hasattr(module, alias)
        assert alias not in module.__all__
        assert alias not in dir(module)
        assert callable(getattr(module, canonical))
        with pytest.raises(ImportError, match=alias):
            exec(f"from {module_name} import {alias}", {})
        exported = {}
        exec(f"from {module_name} import *", exported)
        assert alias not in exported
    assert not caught, "Removed APIs must fail, not fall back to warning adapters"


@pytest.mark.parametrize("module_name", ("galaga", "galaga.facade"))
@pytest.mark.parametrize("name", ("GalagaDeprecationWarning", "DEPRECATED_OPERATION_ALIASES"))
def test_obsolete_adapter_infrastructure_is_not_public(module_name, name):
    module = importlib.import_module(module_name)
    assert not hasattr(module, name)
    assert name not in module.__all__


def test_retired_spellings_cannot_return_as_catalog_or_core_aliases():
    import galaga.core as core

    removed = set(REMOVED_OPERATION_ALIASES)
    assert removed.isdisjoint(facade.OPERATIONS)
    assert removed.isdisjoint(facade.OPERATION_ALIASES)
    assert removed.isdisjoint(core.OPERATION_ALIASES)


@pytest.mark.parametrize("alias,canonical", tuple(REMOVED_OPERATION_ALIASES.items()))
def test_replacements_keep_canonical_numeric_values_and_provenance(alias, canonical):
    algebra = facade.Algebra(3)
    a = algebra.vector([3, 4, 0]).named("a")
    result = getattr(facade, canonical)(a)
    squared_norm = float(a * a)
    expected = {
        "grade_involution": -a,
        "norm2": algebra.scalar(squared_norm),
        "unit": a / abs(squared_norm) ** 0.5,
        "metric_apply": a,
        "antimetric_apply": a,
    }[canonical]
    assert result.almost_equal(expected)
    assert result.expr == facade.Call(canonical, (facade.Symbol("a"),))


@pytest.mark.parametrize("name", ("inner_product", "ip"))
def test_ambiguous_inner_product_names_are_absent_with_actionable_guidance(name: str) -> None:
    with pytest.raises(AttributeError) as caught:
        getattr(facade, name)

    message = str(caught.value)
    assert "does not select an ambiguous inner product" in message
    for replacement in (
        "doran_lasenby_inner",
        "hestenes_inner",
        "metric_inner_product",
        "scalar_product",
        "left_contraction",
        "right_contraction",
    ):
        assert replacement in message
    assert not hasattr(facade, name)


@pytest.mark.parametrize("member", ("bar", "dag", "inv", "sq"))
def test_curated_unary_conveniences_are_implemented_as_read_only_canonical_operations(member: str) -> None:
    descriptor = getattr(facade.Multivector, member)
    assert isinstance(descriptor, property) and descriptor.fset is None
    operation = {"bar": "grade_involution", "dag": "reverse", "inv": "inverse", "sq": "squared"}[member]
    value = facade.Algebra(2).multivector([2, 0.1, -0.2, 0.05]).named("X")
    expected = getattr(facade, operation)(value)
    result = getattr(value, member)
    assert result.almost_equal(expected)
    assert result.same_expression(expected)


def test_operation_call_shapes_are_explicit() -> None:
    for operation in (facade.geometric_product, facade.outer_product):
        parameters = tuple(inspect.signature(operation).parameters.values())
        assert len(parameters) == 1
        assert parameters[0].kind is inspect.Parameter.VAR_POSITIONAL

    for operation in (
        facade.doran_lasenby_inner,
        facade.hestenes_inner,
        facade.metric_inner_product,
        facade.scalar_product,
    ):
        parameters = tuple(inspect.signature(operation).parameters.values())
        assert len(parameters) == 2
        assert all(parameter.kind is inspect.Parameter.POSITIONAL_OR_KEYWORD for parameter in parameters)


def test_scalar_extraction_requires_explicit_grade_selection() -> None:
    algebra = facade.Algebra(2)
    e1, _ = algebra.basis_vectors()
    mixed = 2 + e1

    assert not hasattr(facade.Multivector, "scalar_part")
    assert facade.scalar_part(mixed) == float(facade.grade(mixed, 0)) == 2.0
    with pytest.raises(TypeError):
        float(mixed)
    assert not hasattr(facade, "inner_product")
    assert not hasattr(facade, "ip")
