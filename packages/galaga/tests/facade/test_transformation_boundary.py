"""Historical identities, corruption probes and legacy-free transformations."""

import ast
import copy
import hashlib
import inspect
import runpy
import subprocess
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
PUBLIC_FILES = ("test_low_dim.py", "test_chisolm_transformations.py", "facade/test_transformation_contracts.py")
REPLAY = runpy.run_path(str(TEST_ROOT / PUBLIC_FILES[2]))
ARCHIVE = REPLAY["ARCHIVE"]


def test_all_historical_transformation_identities_sources_and_runtime_are_preserved():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "7604c238191ebdd04a13b60e0f6fe90c73f34373"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    hashes = (
        "27d6dae56c17926a136428f4377edf8385b2d6f547926a5008b6cf28f01bc152",
        "be0a230264596facc6011da451537748678d22ee2230dd32a2f1787e12992690",
    )
    for row, filename, digest, count, methods in zip(
        ARCHIVE["sources"], PUBLIC_FILES[:2], hashes, (11, 15), (11, 8), strict=True
    ):
        assert row["path"] == f"packages/galaga/tests/{filename}"
        assert row["sha256"] == digest == hashlib.sha256(row["source"].encode()).hexdigest()
        assert row["case_count"] == count
        assert len(row["test_ids"]) == len(set(row["test_ids"])) == methods
        live = runpy.run_path(str(TEST_ROOT / filename))
        assert set(row["test_ids"]) == {
            f"{name}.{method}"
            for name, cls in live.items()
            if name.startswith("Test") and inspect.isclass(cls)
            for method, function in inspect.getmembers(cls, inspect.isfunction)
            if method.startswith("test_")
        }
        assert row["test_ids"] == [
            f"{cls.name}.{node.name}"
            for cls in ast.parse(row["source"]).body
            if isinstance(cls, ast.ClassDef)
            for node in cls.body
            if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
        ]


def test_every_seeded_case_remains_nonvacuous_and_old_rotor_errors_are_archived():
    assert len(ARCHIVE["sources"]) == 2
    assert len(ARCHIVE["seeded_cases"]) == 40
    assert len({row["id"] for row in ARCHIVE["seeded_cases"]}) == 40
    assert Counter(row["seed"] for row in ARCHIVE["seeded_cases"]) == {
        100: 5,
        101: 5,
        102: 5,
        103: 10,
        104: 10,
        105: 2,
        106: 1,
        109: 2,
    }
    assert ARCHIVE["skipped_seeded_cases"] == 0
    assert len(ARCHIVE["low_dim"]) == 7
    assert [(row["n"], row["kind"], row["type"]) for row in ARCHIVE["rotor_errors"]] == [
        (0, "scalar", "ValueError"),
        (1, "scalar", "ValueError"),
        (1, "vector", "ValueError"),
    ]
    assert all("bivector" in row["message"] for row in ARCHIVE["rotor_errors"][:2])
    assert "odd-grade components: [1]" in ARCHIVE["rotor_errors"][2]["message"]
    for row in ARCHIVE["seeded_cases"]:
        assert np.linalg.norm(row["vector"]) > 0
        if "columns" in row:
            columns = np.asarray(row["columns"]).T
            assert np.linalg.det(columns.T @ columns) > 1e-10
        if "normal" in row:
            assert np.dot(row["normal"], row["normal"]) > 1e-10


def test_transformation_suites_are_not_exempt_from_legacy_construction_guard():
    assert not set(PUBLIC_FILES) & set(LEGACY_ORACLE_TESTS)


def test_transformation_suites_run_with_legacy_imports_blocked():
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
            raise AssertionError('transformation contract imported legacy: ' + fullname)
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


@pytest.mark.parametrize("coefficients", ([1], [np.nan] * 4, [1] * 4))
def test_seeded_replay_rejects_malformed_nonfinite_or_wrong_archived_projection(coefficients):
    row = copy.deepcopy(ARCHIVE["seeded_cases"][0])
    row["projection"] = coefficients
    with pytest.raises(AssertionError):
        REPLAY["test_seeded_legacy_cases_replay_against_archive_and_coordinate_oracles"](row, True, "latex")


def test_projection_matrix_oracle_rejects_the_wrong_contraction_side(monkeypatch):
    monkeypatch.setattr(ga, "left_contraction", ga.right_contraction)
    with pytest.raises(AssertionError):
        REPLAY["test_non_euclidean_projection_uses_the_restricted_metric_and_is_scale_invariant"](
            REPLAY["GRAMS"][1], 2, -3, "latex"
        )


def test_reflection_oracle_rejects_reversion_substituted_for_inverse(monkeypatch):
    monkeypatch.setattr(ga, "inverse", ga.reverse)
    with pytest.raises(AssertionError):
        REPLAY["test_scaled_and_negative_square_normals_require_the_inverse_not_reverse"](
            REPLAY["GRAMS"][1], 2, "unicode"
        )


def test_rotor_oracle_rejects_the_opposite_exponential_orientation(monkeypatch):
    original = ga.exp
    monkeypatch.setattr(ga, "exp", lambda value: original(-value))
    with pytest.raises(AssertionError):
        REPLAY["test_bivector_exponentials_use_elliptic_hyperbolic_or_null_branches"](
            REPLAY["ROTOR_GRAMS"][1], True, "ascii"
        )
