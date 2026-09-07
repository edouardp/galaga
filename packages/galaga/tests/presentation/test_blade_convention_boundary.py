"""Historical identities, archive integrity, and legacy-free execution gates."""

import ast
import copy
import inspect
import runpy
import subprocess
import sys
from itertools import product
from pathlib import Path

import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
PUBLIC_FILES = (
    "test_blade_convention.py",
    "presentation/test_sta_named_blades.py",
    "presentation/test_blade_convention_contracts.py",
)
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILES[0]))
TABLES = runpy.run_path(str(TEST_ROOT / PUBLIC_FILES[2]))
ARCHIVE = TABLES["ARCHIVE"]


def test_every_historical_method_retains_its_public_identity():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "a502b30c8c8730c117e7caa64d24d95c888b5b83"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_test"] == "packages/galaga/tests/test_blade_convention.py"
    assert ARCHIVE["original_case_count"] == 107
    tests = ARCHIVE["tests"]
    identifiers = [row["id"] for row in tests]
    assert len(identifiers) == len(set(identifiers)) == 102
    live = {
        f"{name}.{method}"
        for name, cls in CONTRACT.items()
        if name.startswith("Test") and inspect.isclass(cls)
        for method, function in inspect.getmembers(cls, inspect.isfunction)
        if method.startswith("test_")
    }
    assert live == set(identifiers)
    for row in tests:
        node = ast.parse(row["source"]).body[0]
        assert isinstance(node, ast.FunctionDef) and node.name == row["id"].split(".")[1]
        assert any(isinstance(child, (ast.Assert, ast.With)) for child in ast.walk(node))


def test_archive_covers_both_time_first_metrics_and_the_distinct_counts_order():
    tables = ARCHIVE["sta_tables"]
    assert len(tables) == 12
    assert {(tuple(row["signature"]), row["sigmas"], row["pseudovectors"]) for row in tables} == {
        (signature, sigmas, pseudovectors)
        for signature in ((1, -1, -1, -1), (-1, 1, 1, 1), (1, 1, 1, -1))
        for sigmas, pseudovectors in product((False, True), repeat=2)
    }
    for table in tables:
        assert [label["mask"] for label in table["labels"]] == list(range(16))
        for label in table["labels"]:
            assert type(label["orientation"]) is int and label["orientation"] in (-1, 1)
            assert all(isinstance(label[target], str) and label[target] for target in ("ascii", "unicode", "latex"))
    assert TABLES["ASCII_CHANGES"] == {"iy0": "ig0", "iy1": "ig1", "iy2": "ig2", "iy3": "ig3"}


def test_blade_suites_are_not_exempt_from_legacy_construction_guard():
    assert not set(PUBLIC_FILES) & set(LEGACY_ORACLE_TESTS)


def test_blade_suites_run_with_legacy_imports_blocked():
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
            raise AssertionError('blade contract imported legacy module: ' + fullname)
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


@pytest.mark.parametrize("field, value", (("orientation", 1), ("unicode", "wrong"), ("mask", 2)))
def test_archive_replay_rejects_corrupted_sign_name_or_mask(field, value):
    table = copy.deepcopy(ARCHIVE["sta_tables"][-1])
    assert table["labels"][3]["orientation"] == -1
    table["labels"][3][field] = value
    with pytest.raises(AssertionError):
        TABLES["test_archived_sta_table_preserves_labels_signs_and_numeric_lookup"](table, "unicode")


def test_numeric_lookup_guard_rejects_the_old_unsigned_name_lookup(monkeypatch):
    original = ga.Algebra.blade

    def unsigned(self, value, **kwargs):
        if value == "σ₁":
            return original(self, 3, **kwargs)
        return original(self, value, **kwargs)

    monkeypatch.setattr(ga.Algebra, "blade", unsigned)
    with pytest.raises(AssertionError):
        TABLES["test_archived_sta_table_preserves_labels_signs_and_numeric_lookup"](
            ARCHIVE["sta_tables"][-1], "unicode"
        )
