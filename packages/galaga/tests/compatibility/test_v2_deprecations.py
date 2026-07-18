from __future__ import annotations

import subprocess
import sys
import warnings
from pathlib import Path

import pytest

import galaga.facade as facade

from .v1_surface_manifest import (
    CURATED_OPERATION_ALIASES,
    SUPPORTED_SUBMODULES,
    TEMPORARY_OPERATION_ALIASES,
    TOP_LEVEL_EXPORTS,
)


@pytest.mark.parametrize(("alias", "canonical"), tuple(CURATED_OPERATION_ALIASES.items()))
def test_permanent_concise_aliases_remain_exact_objects(alias: str, canonical: str) -> None:
    assert getattr(facade, alias) is getattr(facade, canonical)
    assert alias not in facade.OPERATIONS


@pytest.mark.parametrize(("alias", "canonical"), tuple(TEMPORARY_OPERATION_ALIASES.items()))
def test_temporary_alias_warns_at_the_user_callsite_and_invokes_the_canonical_operation(
    alias: str,
    canonical: str,
) -> None:
    algebra = facade.Algebra(2)
    value = algebra.blade(1, expr=True)

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        result = getattr(facade, alias)(value)

    assert len(caught) == 1
    warning = caught[0]
    assert warning.category is facade.GalagaDeprecationWarning
    assert str(warning.message) == TOP_LEVEL_EXPORTS[alias].warning
    assert Path(warning.filename).resolve() == Path(__file__).resolve()
    assert result == getattr(facade, canonical)(value)
    assert result.expr is not None
    assert result.expr.operation_id == canonical


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
    ("module", "message"),
    (
        ("galaga.gram_bridge", "galaga.gram_bridge is deprecated; import galaga.facade"),
        (
            "galaga.gram_bridge.catalog",
            "galaga.gram_bridge.catalog is deprecated; import galaga.facade.catalog",
        ),
        (
            "galaga.gram_bridge.facade",
            "galaga.gram_bridge.facade is deprecated; import galaga.facade",
        ),
    ),
)
def test_migration_only_bridge_imports_emit_the_ledgered_warning(module: str, message: str) -> None:
    program = f"""
import warnings
warnings.simplefilter("always")
import {module}
"""
    result = subprocess.run(
        [sys.executable, "-c", program],
        check=False,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert message in result.stderr
    assert "GalagaDeprecationWarning" in result.stderr


def test_compatibility_guide_names_every_temporary_alias_and_deprecated_bridge() -> None:
    repository = Path(__file__).parents[4]
    guide = (repository / "docs/v2/compatibility-shims.md").read_text()

    for alias, canonical in TEMPORARY_OPERATION_ALIASES.items():
        assert f"`{alias}`" in guide
        assert f"`{canonical}`" in guide
    for module, disposition in SUPPORTED_SUBMODULES.items():
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
