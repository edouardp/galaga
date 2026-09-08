"""Archive integrity, corruption probes, and legacy-free factory/display edges."""

import ast
import copy
import hashlib
import inspect
import runpy
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
PUBLIC_FILES = ("test_coverage_gaps.py", "facade/test_factory_display_contracts.py")
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILES[1]))
ARCHIVE = CONTRACT["ARCHIVE"]


def test_all_30_historical_identities_retain_their_source_and_live_public_owner():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "0105096b97b5839d2f397fa52369471886cac3e9"
    assert ARCHIVE["source_path"] == "packages/galaga/tests/test_coverage_gaps.py"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["sha256"] == "f9c69f323ea07af2f4ff6c364b03198e9dc3bc91728a68e74ec63a4ba4336aca"
    assert hashlib.sha256(ARCHIVE["source"].encode()).hexdigest() == ARCHIVE["sha256"]
    assert ARCHIVE["case_count"] == len(ARCHIVE["test_ids"]) == len(set(ARCHIVE["test_ids"])) == 30
    assert ARCHIVE["test_ids"] == [
        f"{cls.name}.{node.name}"
        for cls in ast.parse(ARCHIVE["source"]).body
        if isinstance(cls, ast.ClassDef)
        for node in cls.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]
    assert set(ARCHIVE["test_ids"]) == {
        f"{name}.{method}"
        for name, cls in CONTRACT["SOURCE"].items()
        if name.startswith("Test") and inspect.isclass(cls)
        for method, function in inspect.getmembers(cls, inspect.isfunction)
        if method.startswith("test_")
    }


def test_archive_retains_complete_values_tables_and_intentional_v2_differences():
    assert len(ARCHIVE["lookups"]) == 6
    assert len(ARCHIVE["displays"]) == 6
    assert len(ARCHIVE["factories"]) == 10
    assert [(row["id"], len(row["basis"])) for row in ARCHIVE["pseudoscalar_tables"]] == [
        ("gamma", 16),
        ("sigma", 8),
        ("sigma_xyz", 8),
    ]
    assert [row["id"] for row in ARCHIVE["errors"]] == ["unknown", "not_basis", "conflict_true", "conflict_false"]
    assert all(row["type"] == "ValueError" for row in ARCHIVE["errors"])
    assert ARCHIVE["lookups"][1]["data"][3] == 1
    assert ARCHIVE["lookups"][1]["unicode"] == "-σ₁"
    assert ARCHIVE["displays"][1]["wrapped"] == "$v$"
    assert "2.12" in ARCHIVE["displays"][4]["display_fixed"]
    assert "3.79" in ARCHIVE["displays"][4]["display_fixed"]


def test_migrated_edge_suites_leave_the_legacy_construction_ledger():
    assert not set(PUBLIC_FILES) & set(LEGACY_ORACLE_TESTS)


def test_factory_display_edges_run_with_legacy_imports_blocked():
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
            raise AssertionError('factory/display contract imported legacy: ' + fullname)
sys.meta_path.insert(0, RejectLegacy())
import pytest
result = pytest.main(['--noconftest', '-q', *sys.argv[1:]])
assert result == 0
assert not any(forbidden(name) for name in sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-c", program, *(str(TEST_ROOT / name) for name in PUBLIC_FILES)],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("data", ([1], [np.nan] * 8, [0] * 8))
def test_archived_display_replay_rejects_malformed_nonfinite_or_erased_coefficients(data):
    row = copy.deepcopy(ARCHIVE["displays"][1])
    row["data"] = data
    with pytest.raises(AssertionError):
        CONTRACT["test_archived_display_values_keep_explicit_content_targets_and_wrapping"](row, True, "latex")


def test_lookup_oracle_rejects_the_old_unsigned_semantic_name_behavior(monkeypatch):
    original = ga.Algebra.blade

    def unsigned(self, blade, **kwargs):
        return original(self, 3 if blade == "σ₁" else blade, **kwargs)

    monkeypatch.setattr(ga.Algebra, "blade", unsigned)
    with pytest.raises(AssertionError):
        CONTRACT["test_archived_lookup_values_have_explicit_public_replacements"](
            ARCHIVE["lookups"][1], True, "unicode"
        )


def test_display_oracle_rejects_unicode_repr_instead_of_ascii(monkeypatch):
    monkeypatch.setattr(ga.Multivector, "__repr__", lambda value: value.unicode())
    with pytest.raises(AssertionError):
        CONTRACT["test_archived_display_values_keep_explicit_content_targets_and_wrapping"](
            ARCHIVE["displays"][1], True, "unicode"
        )


def test_snapshot_oracle_rejects_a_non_string_display_wrapper(monkeypatch):
    original = ga.Multivector.display

    class OldStyleWrapper:
        def __init__(self, text):
            self.text = text

        def __str__(self):
            return self.text

    monkeypatch.setattr(
        ga.Multivector, "display", lambda value, *args, **kwargs: OldStyleWrapper(original(value, *args, **kwargs))
    )
    assert str(OldStyleWrapper("example")) == "example"
    with pytest.raises(AssertionError):
        CONTRACT["test_rendered_strings_are_snapshots_while_new_calls_observe_scoped_policy"](((1, 0), (0, 1)), "ascii")


def test_pseudoscalar_table_replay_rejects_changed_labels():
    table = copy.deepcopy(ARCHIVE["pseudoscalar_tables"][0])
    table["basis"][-1]["latex"] = "wrong"
    with pytest.raises(AssertionError):
        CONTRACT["test_complete_named_pseudoscalar_basis_tables_preserve_exterior_coefficients"](table, True, "latex")


@pytest.mark.skipif(sys.version_info < (3, 14), reason="presentation notebook uses Python 3.14 t-strings")
def test_notebook_executes_snapshot_scope_and_numeric_identity_checks():
    notebook = TEST_ROOT.parents[2] / "examples/galaga_v2/presentation_contexts.py"
    outputs, definitions = runpy.run_path(str(notebook))["app"].run()
    before = definitions["default_expression_latex"]
    during = definitions["functional_expression_latex"]
    assert definitions["saved_expression_latex"] == before == definitions["restored_expression_latex"]
    assert type(before) is type(during) is str
    assert before != during and r"geometric\_product" in during
    product = definitions["product"]
    gram = product.algebra.gram
    x, y = np.array([1, 2]), np.array([3, -1])
    expected = [float(x @ gram @ y), 0, 0, float(np.linalg.det(np.column_stack((x, y))))]
    np.testing.assert_allclose(product.data, expected, rtol=0, atol=1e-12)
    html = "\n".join(getattr(output, "text", "") for output in outputs)
    assert before in html and during in html
    assert "saved string" in html
