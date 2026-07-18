"""Executable completeness checks for the Galaga 1 to 2 API contract."""

from __future__ import annotations

import importlib
import inspect
import re
from pathlib import Path

import pytest

import galaga
import galaga.expr as legacy_expr
import galaga.facade as facade
from galaga import algebra as legacy_algebra

from .v1_surface_manifest import (
    ACCIDENTAL_PRIVATE_DEPENDENCIES,
    ALGEBRA_CONSTRUCTION_FORMS,
    ALGEBRA_CONSTRUCTOR_PARAMETERS,
    ALGEBRA_MEMBERS,
    ALGEBRA_SPECIAL_METHODS,
    COMPANION_TOUCHPOINTS,
    CURATED_OPERATION_ALIASES,
    EXPRESSION_NODE_CLASSES,
    MULTIVECTOR_FORMATTING_HOOKS,
    MULTIVECTOR_MEMBERS,
    OPERATION_CALL_FORMS,
    SUPPORTED_SUBMODULES,
    TEMPORARY_OPERATION_ALIASES,
    TOP_LEVEL_EXPORTS,
    TOP_LEVEL_PACKAGE_MODULES,
    V1_MULTIVECTOR_SPECIAL_METHODS,
    V2_ADDITIONS,
    V2_MULTIVECTOR_PROTOCOL_ADDITIONS,
    V2_MULTIVECTOR_SPECIAL_METHODS,
)

_GENERATED_CLASS_ATTRIBUTES = {
    "__dict__",
    "__doc__",
    "__module__",
    "__slots__",
    "__weakref__",
}


def _public_members(value: type[object]) -> set[str]:
    return {name for name, _ in inspect.getmembers(value) if not name.startswith("_")}


def _declared_special_methods(value: type[object]) -> set[str]:
    return {
        name
        for name in value.__dict__
        if name.startswith("__") and name.endswith("__") and name not in _GENERATED_CLASS_ATTRIBUTES
    }


def test_every_top_level_v1_export_has_exactly_one_disposition() -> None:
    assert len(galaga.__all__) == len(set(galaga.__all__))
    assert set(galaga.__all__) == set(TOP_LEVEL_EXPORTS)


def test_legacy_type_members_and_protocols_are_exhaustively_recorded() -> None:
    assert _public_members(legacy_algebra.Algebra) == set(ALGEBRA_MEMBERS)
    assert _public_members(legacy_algebra.Multivector) == set(MULTIVECTOR_MEMBERS)
    assert _declared_special_methods(legacy_algebra.Algebra) == set(ALGEBRA_SPECIAL_METHODS)
    assert _declared_special_methods(legacy_algebra.Multivector) == set(V1_MULTIVECTOR_SPECIAL_METHODS)

    assert V2_MULTIVECTOR_SPECIAL_METHODS == (V1_MULTIVECTOR_SPECIAL_METHODS | V2_MULTIVECTOR_PROTOCOL_ADDITIONS)
    assert V2_MULTIVECTOR_PROTOCOL_ADDITIONS <= _declared_special_methods(facade.Multivector)
    assert set(MULTIVECTOR_FORMATTING_HOOKS) == {
        "__format__",
        "__repr__",
        "__str__",
        "_repr_latex_",
        "display",
        "latex",
    }
    assert all(hasattr(legacy_algebra.Multivector, name) for name in MULTIVECTOR_FORMATTING_HOOKS)


def test_every_public_legacy_expression_node_is_recorded() -> None:
    public_classes = {
        name
        for name, value in inspect.getmembers(legacy_expr, inspect.isclass)
        if not name.startswith("_") and value.__module__ == legacy_expr.__name__
    }

    assert public_classes == set(EXPRESSION_NODE_CLASSES)


def test_dispositions_are_actionable_and_all_retiring_names_have_guidance() -> None:
    groups = (
        TOP_LEVEL_EXPORTS,
        ALGEBRA_CONSTRUCTOR_PARAMETERS,
        ALGEBRA_MEMBERS,
        MULTIVECTOR_MEMBERS,
        MULTIVECTOR_FORMATTING_HOOKS,
        EXPRESSION_NODE_CLASSES,
        SUPPORTED_SUBMODULES,
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


def test_supported_package_entry_points_import() -> None:
    for module_name, disposition in SUPPORTED_SUBMODULES.items():
        if module_name.startswith("galaga.gram_bridge"):
            assert disposition.warning is not None
            with pytest.warns(facade.GalagaDeprecationWarning, match=re.escape(disposition.warning)):
                module = importlib.reload(importlib.import_module(module_name))
        else:
            module = importlib.import_module(module_name)
        assert module.__name__ == module_name


def test_every_nonprivate_top_level_package_module_is_classified() -> None:
    package_path = Path(galaga.__file__).parent
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
    assert TOP_LEVEL_PACKAGE_MODULES <= set(SUPPORTED_SUBMODULES)


def test_constructor_forms_and_invalid_combinations_are_characterized() -> None:
    assert set(inspect.signature(legacy_algebra.Algebra).parameters) == set(ALGEBRA_CONSTRUCTOR_PARAMETERS)
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


def test_accidental_private_dependencies_remain_visible_until_phase_7() -> None:
    repository = Path(__file__).parents[4]
    matrix_source = (repository / "packages/galaga_matrix/galaga_matrix/matrix.py").read_text()
    mermaid_source = (repository / "packages/galaga_mermaid/galaga_mermaid/mermaid.py").read_text()

    assert "alg._mul_index" in matrix_source
    assert "alg._mul_sign" in matrix_source
    assert "mv._to_expr()" in mermaid_source
