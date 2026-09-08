"""Frozen v1 evidence and negative controls for the live architecture guards."""

import ast
import hashlib
import inspect
import json
import runpy
import subprocess
import sys
from dataclasses import replace
from pathlib import Path

import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
PUBLIC_FILE = "facade/test_architecture_contracts.py"
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILE))
ARCHIVE = json.loads((TEST_ROOT.parent / "tools/baselines/architecture-contracts-v1.json").read_text())


def test_historical_source_and_all_seven_method_identities_have_a_public_owner():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "62a9f982b4b8662f0a1510d881acb452a967a984"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_path"] == "packages/galaga/tests/test_coverage.py"
    assert ARCHIVE["public_owner"] == PUBLIC_FILE
    assert ARCHIVE["sha256"] == "421d8e88ed07a2265df3ccc45a171834742ff3f3c8563b6ddac882d5dc6ce34f"
    assert hashlib.sha256(ARCHIVE["source"].encode()).hexdigest() == ARCHIVE["sha256"]
    archived_ids = [
        f"{cls.name}.{node.name}"
        for cls in ast.parse(ARCHIVE["source"]).body
        if isinstance(cls, ast.ClassDef)
        for node in cls.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]
    assert ARCHIVE["all_source_test_ids"] == archived_ids
    assert len(archived_ids) == len(set(archived_ids)) == 199
    expected = {name for name in archived_ids if name.startswith("TestArchitecturalInvariants.")}
    assert len(expected) == 7
    assert set(ARCHIVE["test_ids"]) == expected
    assert expected == {
        f"TestArchitecturalInvariants.{name}"
        for name, _function in inspect.getmembers(CONTRACT["TestArchitecturalInvariants"], inspect.isfunction)
        if name.startswith("test_")
    }
    assert PUBLIC_FILE not in LEGACY_ORACLE_TESTS
    # Other mixed classes stay ledgered until their own reviewed migration.
    source = (TEST_ROOT / "test_coverage.py").read_text()
    assert not any(
        isinstance(node, ast.ClassDef) and node.name == "TestArchitecturalInvariants" for node in ast.parse(source).body
    )


def test_archive_keeps_the_complete_old_registry_without_using_it_as_the_current_count():
    operations = ARCHIVE["operations"]
    ids = [row["id"] for row in operations]
    assert len(ids) == len(set(ids)) == 45
    assert ids == ARCHIVE["node_ids"]
    assert len(ARCHIVE["symbolic_handlers"]) == len(set(ARCHIVE["symbolic_handlers"])) == 57
    assert set(ids) <= set(ARCHIVE["symbolic_handlers"])
    aliases = {"gp": "geometric_product", "op": "outer_product", "involute": "grade_involution"}
    for row in operations:
        assert row["arity"] == row["node_arity"]
        assert row["handler"] == row["node_name"]
        canonical = aliases.get(row["id"], row["id"])
        assert ga.get_operation(canonical).arity == row["arity"]
    assert set(ids) != set(ga.OPERATIONS)
    assert ga.get_operation("grade").expression_arity == 1
    assert ga.get_operation("grade").arity == 2


@pytest.mark.parametrize(
    "source",
    (
        "import galaga",
        "import galaga.expression as provenance",
        "import os, galaga.rendering",
        "from galaga import expression",
        "from galaga.expression import Call as Node",
        "from galaga.expression import *",
        "from .. import expression",
        "from ..expression import Call",
        "from . import _numeric",
        "from ._numeric import Algebra",
        "from ..presentation import (\n    DisplayPolicy,\n    Notation,\n)",
        "def later():\n    from ..expression import Call",
        "class Later:\n    import galaga.rendering",
        "if TYPE_CHECKING:\n    from galaga.expression import Expr",
        "try:\n    from galaga.legacy import Algebra\nexcept ImportError:\n    pass",
        "from galaga.names import Name",
    ),
)
def test_catalog_guard_rejects_outer_imports_including_relative_and_nested_forms(source):
    with pytest.raises(AssertionError, match="outside the numeric core"):
        CONTRACT["assert_core_only_imports"](source, "galaga.facade")


@pytest.mark.parametrize(
    "source,package",
    (
        ("import numpy as np\nimport math", "galaga.core"),
        ("from . import _backends", "galaga.core"),
        ("from ._metadata import Metadata", "galaga.core"),
        ("from .. import core", "galaga.facade"),
        ("from galaga import core", "galaga.facade"),
        ("import galaga.core as numeric", "galaga.facade"),
        ("from galaga.core import Algebra", "galaga.facade"),
        ("from .._metadata import Metadata", "galaga.core.nested"),
        ("from .. import _backends", "galaga.core.nested"),
        ("# import galaga.expression\ntext = 'from galaga import legacy'", "galaga.core"),
    ),
)
def test_catalog_guard_accepts_inward_imports_and_ignores_comments_and_strings(source, package):
    CONTRACT["assert_core_only_imports"](source, package)


def test_resource_walk_checks_nested_packages_and_ignores_non_python_files(tmp_path):
    (tmp_path / "__init__.py").write_text("import math\n")
    (tmp_path / "notes.txt").write_text("import galaga.legacy\n")
    nested = tmp_path / "nested"
    nested.mkdir()
    (nested / "module.py").write_text("from ...expression import Call\n")
    sources = list(CONTRACT["python_sources"](tmp_path, "galaga.core"))
    assert sources == [
        ("galaga.core", "galaga.core", "import math\n"),
        ("galaga.core.nested.module", "galaga.core.nested", "from ...expression import Call\n"),
    ]
    with pytest.raises(AssertionError, match="galaga.expression.Call"):
        CONTRACT["assert_core_only_imports"](sources[1][2], sources[1][1])


@pytest.mark.parametrize("mutation", ("missing", "extra", "wrong-id", "empty-exclusion", "overlap"))
def test_catalog_completeness_rejects_missing_unowned_or_misidentified_entries(mutation):
    operations, excluded = dict(ga.OPERATIONS), dict(ga.EXCLUDED_PUBLIC_NAMES)
    if mutation == "missing":
        del operations["reverse"]
    elif mutation == "extra":
        operations["unowned"] = replace(operations["reverse"], id="unowned")
    elif mutation == "wrong-id":
        operations["reverse"] = operations["conjugate"]
    elif mutation == "empty-exclusion":
        excluded["Algebra"] = ""
    else:
        excluded["reverse"] = "must not be both cataloged and excluded"
    with pytest.raises(AssertionError):
        CONTRACT["assert_catalog_complete"](operations, excluded)


def test_schema_routing_probe_rejects_an_incompatible_evaluator_signature():
    broken = replace(ga.OPERATIONS["grade"], evaluate=lambda value: value)
    with pytest.raises(TypeError, match="too many positional arguments"):
        CONTRACT["test_catalog_binding_and_replay_forward_the_same_operands_and_parameters"](broken, True)


def test_schema_routing_probe_rejects_swapped_operands(monkeypatch):
    original = ga.OperationSpec.invoke_expression

    def swapped(self, operands, parameters=()):
        return original(self, tuple(reversed(operands)), parameters)

    monkeypatch.setattr(ga.OperationSpec, "invoke_expression", swapped)
    with pytest.raises(AssertionError):
        CONTRACT["test_catalog_binding_and_replay_forward_the_same_operands_and_parameters"](
            ga.OPERATIONS["geometric_product"], True
        )


def test_gram_probe_rejects_replay_that_ignores_changed_symbol_bindings(monkeypatch):
    original = ga.evaluate
    seen = {}

    def cached(expression, **kwargs):
        key = (expression, id(kwargs["algebra"]))
        if key not in seen:
            seen[key] = original(expression, **kwargs)
        return seen[key]

    monkeypatch.setattr(ga, "evaluate", cached)
    with pytest.raises(AssertionError):
        CONTRACT["test_catalog_provenance_replays_gram_derived_values_without_rendering_state"](
            ((2, 0.5), (0.5, -1)), "latex"
        )


def test_architecture_contracts_run_in_a_fresh_process_with_legacy_imports_blocked():
    program = """
import importlib.abc
import sys
roots = {
    'galaga.algebra', 'galaga.basis_blade', 'galaga.blade_convention',
    'galaga.expr', 'galaga.latex_build', 'galaga.latex_emit',
    'galaga.latex_nodes', 'galaga.latex_rewrite', 'galaga.latex_symbols',
    'galaga.lazy', 'galaga.legacy', 'galaga.notation', 'galaga.ops',
    'galaga.symbolic', 'galaga.symbolic_core',
}
def forbidden(name):
    return any(name == root or name.startswith(root + '.') for root in roots)
class RejectLegacy(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if forbidden(fullname):
            raise AssertionError('architecture contract imported legacy: ' + fullname)
sys.meta_path.insert(0, RejectLegacy())
import pytest
result = pytest.main(['--noconftest', '-q', sys.argv[1]])
assert result == 0
assert not any(forbidden(name) for name in sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-c", program, str(TEST_ROOT / PUBLIC_FILE)],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr
