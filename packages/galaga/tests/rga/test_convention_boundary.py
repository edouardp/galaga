"""Historical ownership, corruption probes, and legacy-free RGA execution."""

import ast
import copy
import inspect
import runpy
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

import galaga as ga
from galaga.expression import Call

TEST_ROOT = Path(__file__).parents[1]
PUBLIC_FILES = (
    "test_rga_convention_layer.py",
    "rga/test_convention_numeric_contract.py",
    "rendering/test_underaccent_fallback.py",
)
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILES[0]))
NUMERIC = runpy.run_path(str(TEST_ROOT / PUBLIC_FILES[1]))
ARCHIVE = NUMERIC["ARCHIVE"]


def test_original_rga_identities_and_archive_provenance_are_preserved():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "48f5d0fd82f15225d22e4069cc8341d4760eec97"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_test"] == "packages/galaga/tests/test_rga_convention_layer.py"
    assert ARCHIVE["original_case_count"] == 11
    assert ARCHIVE["signature"] == [1, 1, 1, 0]
    identifiers = [row["id"] for row in ARCHIVE["tests"]]
    assert len(identifiers) == len(set(identifiers)) == 5
    assert set(identifiers) == {
        name for name, value in CONTRACT.items() if name.startswith("test_") and inspect.isfunction(value)
    }
    for row in ARCHIVE["tests"]:
        node = ast.parse(row["source"]).body[0]
        assert isinstance(node, ast.FunctionDef) and node.name == row["id"]
        assert any(isinstance(child, (ast.Assert, ast.With)) for child in ast.walk(node))
    for index, name in enumerate(("e1", "e2")):
        np.testing.assert_array_equal(ARCHIVE["bindings"][name], np.eye(16)[1 << index])
    assert len(ARCHIVE["observations"]) == 26
    for row in ARCHIVE["observations"]:
        assert np.asarray(row["coefficients"]).shape == (16,)
        assert np.isfinite(row["coefficients"]).all()
        assert all(isinstance(row[target], str) and row[target] for target in ("ascii", "unicode", "latex"))


def test_archive_retains_all_oriented_blades_and_exposes_vacuous_old_operation_samples():
    algebra = ga.Algebra(config=ga.p_rga())
    assert len(ARCHIVE["basis"]) == 16
    for row, mask in zip(ARCHIVE["basis"], algebra.presentation.display_order.masks, strict=True):
        value = algebra.blade(algebra.blade_label(mask).ref)
        NUMERIC["assert_coefficients"](value.data, row["coefficients"])
        for target in ("ascii", "unicode", "latex"):
            assert value.display(f"value/{target}") == row[target]
    operations = set(CONTRACT["UNARY"]) | set(CONTRACT["BINARY"])
    rows = [row for row in ARCHIVE["observations"] if row.get("operation") in operations]
    assert len(rows) == 16
    assert sum(not any(row["coefficients"]) for row in rows) == 11
    assert any(row["ascii"] != row["latex"] and "e₁" in row["ascii"] for row in rows)


def test_rga_suites_are_not_exempt_from_legacy_construction_guard():
    assert not set(PUBLIC_FILES) & set(LEGACY_ORACLE_TESTS)


def test_rga_suites_run_with_legacy_imports_blocked():
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
            raise AssertionError('RGA contract imported legacy module: ' + fullname)
sys.meta_path.insert(0, RejectLegacy())
import pytest
result = pytest.main(['--noconftest', '-q', *sys.argv[1:]])
assert result == 0
assert not any(forbidden(name) for name in sys.modules)
"""
    completed = subprocess.run(
        [sys.executable, "-c", program, *(str(TEST_ROOT / path) for path in PUBLIC_FILES)],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


@pytest.mark.parametrize(
    "field, value",
    (("coefficients", [1]), ("coefficients", [np.nan] * 16), ("coefficients", [1] * 16), ("latex", "wrong")),
)
def test_archive_replay_rejects_corrupted_shape_finiteness_coefficients_or_spelling(field, value):
    row = copy.deepcopy(ARCHIVE["observations"][0])
    row[field] = value
    with pytest.raises(AssertionError):
        NUMERIC["test_original_rga_observations_keep_numeric_values_and_reviewed_spelling"](row, "latex")


@pytest.mark.parametrize(
    "operation, replacement",
    (("right_hodge_dual", "left_hodge_dual"), ("right_weight_dual", "left_weight_dual")),
)
def test_mixed_grade_oracle_rejects_swapped_dual_sides(operation, replacement, monkeypatch):
    monkeypatch.setattr(ga, operation, getattr(ga, replacement))
    oracle = NUMERIC["CoefficientOracle"](NUMERIC["GRAMS"][0])
    with pytest.raises(AssertionError):
        NUMERIC["test_nonzero_rga_operations_keep_coefficients_grades_and_provenance"](oracle, operation, "latex")


def test_nonzero_antiproduct_catches_a_sign_error_hidden_by_the_old_vector_example(monkeypatch):
    original = ga.geometric_antiproduct
    monkeypatch.setattr(ga, "geometric_antiproduct", lambda a, b: -original(a, b))
    oracle = NUMERIC["CoefficientOracle"](NUMERIC["GRAMS"][0])
    with pytest.raises(AssertionError):
        NUMERIC["test_nonzero_rga_operations_keep_coefficients_grades_and_provenance"](
            oracle, "geometric_antiproduct", "unicode"
        )


def test_transwedge_guard_rejects_simplification_that_loses_the_order_parameter(monkeypatch):
    function = NUMERIC["test_transwedge_order_survives_simplification_and_controls_actual_grade_selection"]
    monkeypatch.setitem(
        function.__globals__,
        "simplify",
        lambda expression: Call(expression.operation_id, expression.operands, (("order", 0),)),
    )
    oracle = NUMERIC["CoefficientOracle"](NUMERIC["GRAMS"][0])
    with pytest.raises(AssertionError):
        function(oracle, "transwedge", 2)
