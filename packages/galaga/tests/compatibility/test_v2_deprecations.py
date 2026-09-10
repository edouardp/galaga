from __future__ import annotations

import importlib
import subprocess
import sys
import warnings
from pathlib import Path

import libcst as cst
import pytest
from libcst.helpers import get_full_name_for_node

import galaga.facade as facade

from .v1_surface_manifest import (
    CURATED_OPERATION_ALIASES,
    REMOVED_OPERATION_ALIASES,
    SUBMODULE_DISPOSITIONS,
    TOP_LEVEL_EXPORTS,
)


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
    }[canonical]
    assert result.almost_equal(expected)
    assert result.expr == facade.Call(canonical, (facade.Symbol("a"),))
    assert TOP_LEVEL_EXPORTS[alias].action == "removed-alias"


def test_examples_do_not_import_retired_operation_spellings():
    """Check real imports, not migration prose or historical code in strings.

    LibCST parses notebook t-strings even on the supported Python 3.11 floor.
    This guard includes scratch examples without claiming they are all runnable.
    """
    repository = Path(__file__).parents[4]

    class Imports(cst.CSTVisitor):
        def visit_ImportFrom(self, node: cst.ImportFrom) -> None:
            if get_full_name_for_node(node.module) not in {"galaga", "galaga.facade", "galaga.core"}:
                return
            if isinstance(node.names, cst.ImportStar):
                return
            for alias in node.names:
                name = get_full_name_for_node(alias.name)
                assert name not in REMOVED_OPERATION_ALIASES, (path, name)

    for path in sorted((repository / "examples").rglob("*.py")):
        cst.parse_module(path.read_text()).visit(Imports())


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


@pytest.mark.parametrize(
    "module",
    (
        "galaga.gram_bridge",
        "galaga.gram_bridge.catalog",
        "galaga.gram_bridge.facade",
        "galaga.facade._compat",
    ),
)
def test_removed_adapters_fail_to_import_without_the_test_guard(module: str) -> None:
    program = f"""
import importlib
import sys
import warnings
import galaga
with warnings.catch_warnings(record=True) as caught:
    warnings.simplefilter('always')
    try:
        importlib.import_module({module!r})
    except ModuleNotFoundError as error:
        assert error.name == {module!r} or {module!r}.startswith(error.name + '.')
    else:
        raise AssertionError('retired adapter is still importable: ' + {module!r})
assert not caught
assert not hasattr(galaga, 'gram_bridge')
assert not any(name.startswith('galaga.gram_bridge') for name in sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-c", program],
        check=False,
        capture_output=True,
        text=True,
        timeout=30,
    )

    assert result.returncode == 0, result.stderr
    assert not result.stderr


def test_compatibility_guide_names_every_removed_alias_and_bridge() -> None:
    repository = Path(__file__).parents[4]
    guide = (repository / "docs/v2/compatibility-shims.md").read_text()

    for alias, canonical in REMOVED_OPERATION_ALIASES.items():
        assert f"`{alias}`" in guide
        assert f"`{canonical}`" in guide
    for module, disposition in SUBMODULE_DISPOSITIONS.items():
        if module.startswith("galaga.gram_bridge"):
            assert f"`{module}`" in guide
            assert f"`{disposition.target}`" in guide


def test_redundant_geometry_helpers_are_explicit_removals_not_facade_operations() -> None:
    for name in ("project", "reject", "reflect"):
        disposition = TOP_LEVEL_EXPORTS[name]
        assert disposition.action == "remove-redundant-helper"
        assert disposition.milestone == "phase-9"
        assert disposition.warning is not None
        assert name not in facade.__all__
        assert name not in facade.OPERATIONS
