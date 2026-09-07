"""Historical ownership, mutation probes, and legacy-free quaternion tests."""

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
PUBLIC_FILES = ("test_quaternion.py", "presentation/test_quaternion_contracts.py")
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILES[0]))
REPLAY = runpy.run_path(str(TEST_ROOT / PUBLIC_FILES[1]))
ARCHIVE = REPLAY["ARCHIVE"]


def test_all_historical_quaternion_identities_and_source_are_preserved():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "8f14835fb09856f0439d28bdd08ec5efcd02c20b"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_test"] == "packages/galaga/tests/test_quaternion.py"
    assert ARCHIVE["source_sha256"] == "ecd602810cf31ef2427b51f9d56a551e767b9ebe6577ffb85a46d11dcaf34a58"
    assert hashlib.sha256(ARCHIVE["source"].encode()).hexdigest() == ARCHIVE["source_sha256"]
    assert ARCHIVE["original_case_count"] == 15
    names = ARCHIVE["test_ids"]
    assert len(names) == len(set(names)) == 15
    assert set(names) == {
        f"{name}.{method}"
        for name, cls in CONTRACT.items()
        if name.startswith("Test") and inspect.isclass(cls)
        for method, function in inspect.getmembers(cls, inspect.isfunction)
        if method.startswith("test_")
    }
    assert names == [
        f"{cls.name}.{node.name}"
        for cls in ast.parse(ARCHIVE["source"]).body
        if isinstance(cls, ast.ClassDef)
        for node in cls.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]
    assert len(ARCHIVE["observations"]) == 19
    assert {row["id"] for row in ARCHIVE["observations"]} == set(REPLAY["observed_values"]())
    assert [table["id"] for table in ARCHIVE["tables"]] == ["quaternion", "complex", "xyz"]


def test_archive_retains_presentation_ordered_bivectors_without_restoring_it():
    quaternion = ga.Algebra(config=ga.p_quaternion())
    semantic = quaternion.blades("quaternion_i", "quaternion_j", "quaternion_k")
    for table in (ARCHIVE["tables"][0], ARCHIVE["tables"][2]):
        np.testing.assert_array_equal(table["basis_bivectors"], [value.data for value in semantic])
        assert not np.array_equal(table["basis_bivectors"], [value.data for value in quaternion.basis_blades(2)])
    complex_algebra = ga.Algebra(config=ga.p_complex())
    np.testing.assert_array_equal(
        ARCHIVE["tables"][1]["basis_bivectors"], [value.data for value in complex_algebra.basis_blades(2)]
    )


def test_quaternion_suites_are_not_exempt_from_legacy_construction_guard():
    assert not set(PUBLIC_FILES) & set(LEGACY_ORACLE_TESTS)


def test_quaternion_suites_run_with_legacy_imports_blocked():
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
            raise AssertionError('quaternion contract imported legacy module: ' + fullname)
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
    (
        ("coefficients", [1]),
        ("coefficients", [np.nan] * 8),
        ("coefficients", [1] * 8),
        ("latex", "wrong"),
        ("id", "e1_e2"),
    ),
)
def test_archive_replay_rejects_corrupted_shape_finiteness_values_spelling_or_identity(field, value):
    row = copy.deepcopy(ARCHIVE["observations"][0])
    row[field] = value
    with pytest.raises(AssertionError):
        REPLAY["test_archived_observations_preserve_coefficients_and_rendering"](row, "latex")


def test_hamilton_oracle_rejects_division_with_inverse_on_the_wrong_side(monkeypatch):
    monkeypatch.setattr(ga.Multivector, "__truediv__", lambda left, right: ga.inverse(right) * left)
    with pytest.raises(AssertionError):
        REPLAY["test_quaternion_arithmetic_matches_independent_hamilton_coordinates"](
            REPLAY["Q_PAIRS"][0], True, "latex"
        )


def test_mixed_grade_probe_rejects_substituting_conjugation_for_reverse(monkeypatch):
    monkeypatch.setattr(ga, "reverse", ga.conjugate)
    with pytest.raises(AssertionError):
        REPLAY["test_reverse_and_conjugate_agree_only_on_the_even_subalgebra"]("unicode")


def test_native_enumeration_guard_rejects_presentation_order_in_the_factory(monkeypatch):
    original = ga.Algebra.basis_blades
    monkeypatch.setattr(ga.Algebra, "basis_blades", lambda algebra, grade: tuple(reversed(original(algebra, grade))))
    with pytest.raises(AssertionError):
        REPLAY["test_hamilton_coordinates_are_derived_from_actual_exterior_products"]()
