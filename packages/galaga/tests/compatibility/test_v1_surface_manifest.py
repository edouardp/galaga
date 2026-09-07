"""Executable completeness checks for the Galaga 1 to 2 API contract."""

from __future__ import annotations

import importlib
import inspect
import json
import re
from collections.abc import Collection
from pathlib import Path

import pytest

import galaga
import galaga.facade as facade

from .v1_surface_manifest import (
    ACCIDENTAL_PRIVATE_DEPENDENCIES,
    ALGEBRA_CONSTRUCTION_FORMS,
    ALGEBRA_CONSTRUCTOR_PARAMETERS,
    ALGEBRA_MEMBERS,
    ALGEBRA_SPECIAL_METHODS,
    COMPANION_TOUCHPOINTS,
    CURATED_OPERATION_ALIASES,
    EXPRESSION_NODE_CLASSES,
    LEGACY_ONLY_SUBMODULES,
    MULTIVECTOR_FORMATTING_HOOKS,
    MULTIVECTOR_MEMBERS,
    OPERATION_CALL_FORMS,
    SUBMODULE_DISPOSITIONS,
    SUPPORTED_SUBMODULES,
    TEMPORARY_OPERATION_ALIASES,
    TOP_LEVEL_EXPORTS,
    TOP_LEVEL_PACKAGE_MODULES,
    V1_MULTIVECTOR_SPECIAL_METHODS,
    V2_ADDITIONS,
    V2_MULTIVECTOR_PROTOCOL_ADDITIONS,
    V2_MULTIVECTOR_SPECIAL_METHODS,
)

BASELINE_PATH = Path(__file__).parents[2] / "tools/baselines/public-surface-v1.json"
BASELINE = json.loads(BASELINE_PATH.read_text())
HISTORICAL_SURFACES = {
    "top_level_exports": TOP_LEVEL_EXPORTS,
    "algebra_members": ALGEBRA_MEMBERS,
    "multivector_members": MULTIVECTOR_MEMBERS,
    "algebra_special_methods": ALGEBRA_SPECIAL_METHODS,
    "multivector_special_methods": V1_MULTIVECTOR_SPECIAL_METHODS,
    "multivector_formatting_hooks": MULTIVECTOR_FORMATTING_HOOKS,
    "algebra_constructor_parameters": ALGEBRA_CONSTRUCTOR_PARAMETERS,
    "expression_node_classes": EXPRESSION_NODE_CLASSES,
}

_GENERATED_CLASS_ATTRIBUTES = {
    "__dict__",
    "__doc__",
    "__module__",
    "__slots__",
    "__firstlineno__",
    "__static_attributes__",
    "__weakref__",
}


def _assert_classified_names(observed: object, classified: Collection[str], *, label: str) -> None:
    assert isinstance(observed, list) and observed, f"{label}: expected a nonempty list"
    assert all(isinstance(name, str) and name for name in observed), f"{label}: invalid name"
    assert len(observed) == len(set(observed)), f"{label}: duplicate observation"
    assert set(observed) == set(classified), f"{label}: historical disposition mismatch"


def _declared_special_methods(value: type[object]) -> set[str]:
    return {
        name
        for name in value.__dict__
        if name.startswith("__") and name.endswith("__") and name not in _GENERATED_CLASS_ATTRIBUTES
    }


@pytest.mark.parametrize("surface", tuple(HISTORICAL_SURFACES))
def test_every_observed_v1_name_has_exactly_one_disposition(surface: str) -> None:
    _assert_classified_names(BASELINE["observed"][surface], HISTORICAL_SURFACES[surface], label=surface)


def test_historical_surface_archive_preserves_capture_provenance_and_completeness() -> None:
    assert BASELINE["schema_version"] == 1
    assert BASELINE["source_commit"] == "3dad1cf74be2fa60a9cd6bc3c7e87a005a4fba35"
    assert BASELINE["captured_on"] == "2026-09-07"
    assert BASELINE["python"] == "3.14.4" and BASELINE["numpy"] == "2.5.2"
    assert BASELINE["source_test"] == "packages/galaga/tests/compatibility/test_v1_surface_manifest.py"
    assert {name: len(values) for name, values in BASELINE["observed"].items()} == {
        "top_level_exports": 99,
        "algebra_members": 28,
        "multivector_members": 20,
        "algebra_special_methods": 2,
        "multivector_special_methods": 22,
        "multivector_formatting_hooks": 6,
        "algebra_constructor_parameters": 7,
        "expression_node_classes": 59,
        "top_level_package_modules": 27,
        "importable_submodules": 36,
    }
    for surface in ("top_level_package_modules", "importable_submodules"):
        observed = BASELINE["observed"][surface]
        _assert_classified_names(observed, set(observed), label=surface)
        assert set(observed) <= set(SUBMODULE_DISPOSITIONS)


def test_top_level_v2_exports_are_owned_by_the_facade() -> None:
    assert galaga.__all__ == facade.__all__
    for name in facade.__all__:
        assert getattr(galaga, name) is getattr(facade, name)


def test_v2_protocol_and_formatting_hooks_remain_live_contracts() -> None:
    assert V2_MULTIVECTOR_SPECIAL_METHODS == (V1_MULTIVECTOR_SPECIAL_METHODS | V2_MULTIVECTOR_PROTOCOL_ADDITIONS)
    assert V2_MULTIVECTOR_SPECIAL_METHODS <= _declared_special_methods(facade.Multivector)
    assert set(MULTIVECTOR_FORMATTING_HOOKS) == {
        "__format__",
        "__repr__",
        "__str__",
        "_repr_latex_",
        "display",
        "latex",
    }
    assert all(callable(getattr(facade.Multivector, name, None)) for name in MULTIVECTOR_FORMATTING_HOOKS)


def test_dispositions_are_actionable_and_all_retiring_names_have_guidance() -> None:
    groups = (
        TOP_LEVEL_EXPORTS,
        ALGEBRA_CONSTRUCTOR_PARAMETERS,
        ALGEBRA_MEMBERS,
        MULTIVECTOR_MEMBERS,
        MULTIVECTOR_FORMATTING_HOOKS,
        EXPRESSION_NODE_CLASSES,
        SUBMODULE_DISPOSITIONS,
        COMPANION_TOUCHPOINTS,
        ACCIDENTAL_PRIVATE_DEPENDENCIES,
    )
    for group in groups:
        for disposition in group.values():
            assert disposition.owner
            assert disposition.action
            assert disposition.target
            assert disposition.milestone
            if disposition.action.startswith(("deprecated", "remove")):
                assert disposition.warning

    for alias in TEMPORARY_OPERATION_ALIASES:
        assert TOP_LEVEL_EXPORTS[alias].warning


@pytest.mark.parametrize("module_name", tuple(SUPPORTED_SUBMODULES))
def test_supported_package_entry_points_import(module_name: str) -> None:
    disposition = SUPPORTED_SUBMODULES[module_name]
    if module_name.startswith("galaga.gram_bridge"):
        assert disposition.warning is not None
        with pytest.warns(facade.GalagaDeprecationWarning, match=re.escape(disposition.warning)):
            module = importlib.reload(importlib.import_module(module_name))
    else:
        module = importlib.import_module(module_name)
    assert module.__name__ == module_name


def test_current_entry_points_and_legacy_only_modules_form_an_explicit_partition() -> None:
    assert not (set(SUPPORTED_SUBMODULES) & LEGACY_ONLY_SUBMODULES)
    assert set(SUPPORTED_SUBMODULES) | LEGACY_ONLY_SUBMODULES == set(SUBMODULE_DISPOSITIONS)
    assert all(disposition == SUBMODULE_DISPOSITIONS[name] for name, disposition in SUPPORTED_SUBMODULES.items())


def _assert_current_module_inventory(package_path: Path) -> None:
    modules = {
        f"galaga.{path.stem}"
        for path in package_path.glob("*.py")
        if path.stem != "__init__" and not path.stem.startswith("_")
    }
    modules.update(
        f"galaga.{path.name}"
        for path in package_path.iterdir()
        if path.is_dir() and not path.name.startswith("_") and (path / "__init__.py").is_file()
    )

    assert modules == set(TOP_LEVEL_PACKAGE_MODULES)
    assert TOP_LEVEL_PACKAGE_MODULES <= set(SUBMODULE_DISPOSITIONS)


def test_every_nonprivate_top_level_package_module_is_classified() -> None:
    _assert_current_module_inventory(Path(galaga.__file__).parent)


@pytest.mark.parametrize("module_name", tuple(SUBMODULE_DISPOSITIONS))
def test_classified_nested_and_top_level_modules_exist_without_importing_legacy(module_name: str) -> None:
    # Presence is a temporary deletion ledger, not a promise of v2 support.
    # Retired entries stay in SUBMODULE_DISPOSITIONS; update the current
    # top-level inventory and this existence gate when their files are removed.
    package_path = Path(galaga.__file__).parent
    relative = Path(*module_name.split(".")[1:])
    assert (package_path / relative.with_suffix(".py")).is_file() or (package_path / relative / "__init__.py").is_file()


def test_constructor_forms_and_invalid_combinations_are_characterized() -> None:
    assert set(ALGEBRA_CONSTRUCTION_FORMS) == {
        "legacy-signature-positional",
        "legacy-empty-signature-positional",
        "legacy-pqr-positional",
        "signature-keyword",
        "signature-short-keyword",
        "diagonal-gram-keyword",
        "full-gram-keyword",
    }

    algebras = {
        "legacy-signature-positional": facade.Algebra((1, -1, 0)),
        "legacy-empty-signature-positional": facade.Algebra(()),
        "legacy-pqr-positional": facade.Algebra(2, 1, 0),
        "signature-keyword": facade.Algebra(signature=(1, -1, 0)),
        "signature-short-keyword": facade.Algebra(sig=(1, -1, 0)),
        "diagonal-gram-keyword": facade.Algebra(gram=((2.0, 0.0), (0.0, -3.0))),
        "full-gram-keyword": facade.Algebra(gram=((1.0, 0.25), (0.25, 1.0))),
    }
    assert set(algebras) == set(ALGEBRA_CONSTRUCTION_FORMS)
    assert algebras["legacy-signature-positional"].signature == (1, -1, 0)
    assert algebras["legacy-empty-signature-positional"].signature == ()
    assert algebras["legacy-pqr-positional"].signature == (1, 1, -1)
    assert algebras["diagonal-gram-keyword"].basis_squares.tolist() == [2.0, -3.0]

    with pytest.raises(TypeError, match="provide p"):
        facade.Algebra()
    with pytest.raises(TypeError, match="cannot be combined"):
        facade.Algebra((1, -1), 1)
    with pytest.raises(TypeError, match="cannot be combined"):
        facade.Algebra(2, signature=(1, -1))


def test_operation_call_shapes_are_explicit() -> None:
    assert set(OPERATION_CALL_FORMS) == {
        "variadic-geometric-product",
        "variadic-outer-product",
        "binary-inner-products",
        "unary-involutions",
        "parameterized-grade",
    }
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


def test_facade_alias_manifest_has_one_object_per_operation() -> None:
    assert dict(facade.OPERATION_ALIASES) == CURATED_OPERATION_ALIASES
    assert dict(facade.DEPRECATED_OPERATION_ALIASES) == TEMPORARY_OPERATION_ALIASES
    with pytest.raises(TypeError):
        facade.OPERATION_ALIASES["product"] = "geometric_product"  # type: ignore[index]
    with pytest.raises(TypeError):
        facade.DEPRECATED_OPERATION_ALIASES["product"] = "geometric_product"  # type: ignore[index]
    for alias, canonical in CURATED_OPERATION_ALIASES.items():
        assert getattr(facade, alias) is getattr(facade, canonical)
        assert alias not in facade.OPERATIONS
    for alias, canonical in TEMPORARY_OPERATION_ALIASES.items():
        assert getattr(facade, alias) is not getattr(facade, canonical)
        assert alias not in facade.OPERATIONS


def test_deliberate_v2_scalar_and_inner_product_corrections_are_visible() -> None:
    algebra = facade.Algebra(2)
    e1, _ = algebra.basis_vectors()
    mixed = 2 + e1

    assert not hasattr(facade.Multivector, "scalar_part")
    assert facade.scalar_part(mixed) == float(facade.grade(mixed, 0)) == 2.0
    with pytest.raises(TypeError):
        float(mixed)
    assert not hasattr(facade, "inner_product")
    assert not hasattr(facade, "ip")
    assert V2_ADDITIONS <= set(facade.__all__)


def test_accidental_private_dependencies_are_removed_as_phase_7_advances() -> None:
    repository = Path(__file__).parents[4]
    matrix_source = (repository / "packages/galaga_matrix/galaga_matrix/matrix.py").read_text()
    mermaid_source = (repository / "packages/galaga_mermaid/galaga_mermaid/mermaid.py").read_text()

    assert "_mul_index" not in matrix_source
    assert "_mul_sign" not in matrix_source
    assert "from galaga.facade import Algebra, Multivector" in matrix_source
    assert "left_action" in matrix_source
    assert "_to_expr" not in mermaid_source
    assert "from galaga.expression import" in mermaid_source
