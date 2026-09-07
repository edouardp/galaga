"""Historical identities, sign-corruption probes, and legacy-free execution."""

import ast
import copy
import hashlib
import inspect
import runpy
import subprocess
import sys
from pathlib import Path
from types import MappingProxyType

import numpy as np
import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
PUBLIC_FILES = ("test_locals.py", "presentation/test_local_name_contracts.py")
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILES[0]))
REPLAY = runpy.run_path(str(TEST_ROOT / PUBLIC_FILES[1]))
ARCHIVE = REPLAY["ARCHIVE"]


def test_every_historical_locals_identity_and_source_is_preserved():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "28562452e4111bf8494a2e04f61e7f6c01028b22"
    assert ARCHIVE["source_test"] == "packages/galaga/tests/test_locals.py"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_sha256"] == "602c3ae748d246f802f4781f87626a0f3c3109a84ed57c78d0ef010140f9a939"
    assert hashlib.sha256(ARCHIVE["source"].encode()).hexdigest() == ARCHIVE["source_sha256"]
    assert ARCHIVE["original_case_count"] == 12
    names = ARCHIVE["test_ids"]
    assert len(names) == len(set(names)) == 11
    assert set(names) == {
        name for name, function in CONTRACT.items() if name.startswith("test_") and inspect.isfunction(function)
    }
    assert names == [
        node.name
        for node in ast.parse(ARCHIVE["source"]).body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]
    assert len(ARCHIVE["tables"]) == 11
    assert {table["id"] for table in ARCHIVE["tables"]} == set(REPLAY["historical_binding_views"]())


def test_archive_preserves_retired_scalar_errors_and_signed_basis_enumeration():
    algebra = ga.Algebra(config=ga.p_sta(sigmas=True))
    expected = [algebra.blade(algebra.blade_label(mask).ref).data for mask in (3, 5, 6, 9, 10, 12)]
    np.testing.assert_array_equal(ARCHIVE["sta_basis_bivectors"], expected)
    assert not np.array_equal(ARCHIVE["sta_basis_bivectors"][0], algebra.basis_blades(2)[0].data)
    scalar = ga.Algebra(3).scalar(1)
    assert set(ARCHIVE["scalar_lookups"]) == {"", "1"}
    for data in ARCHIVE["scalar_lookups"].values():
        np.testing.assert_array_equal(data, scalar.data)
    assert ARCHIVE["errors"] == [
        {"operation": "invalid_prefix", "type": "TypeError", "message": "prefix must be a string or None, got int"},
        {
            "operation": "out_of_range",
            "type": "ValueError",
            "message": "Basis index 5 out of range for 3D algebra (index_base=1)",
        },
    ]


def test_locals_suites_are_not_exempt_from_legacy_construction_guard():
    assert not set(PUBLIC_FILES) & set(LEGACY_ORACLE_TESTS)


def test_locals_suites_run_with_legacy_imports_blocked():
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
            raise AssertionError('locals contract imported legacy module: ' + fullname)
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
        ("key", "wrong"),
        ("coefficients", [1]),
        ("coefficients", [np.nan] * 8),
        ("coefficients", [1] * 8),
        ("unicode", "wrong"),
    ),
)
def test_archive_replay_rejects_corrupted_keys_coefficients_or_spelling(field, value):
    table = copy.deepcopy(ARCHIVE["tables"][0])
    table["bindings"][0][field] = value
    with pytest.raises(AssertionError):
        REPLAY["test_archived_keys_coefficients_order_and_value_rendering"](table, True)


def test_coefficient_oracle_rejects_local_factory_that_drops_orientation(monkeypatch):
    original = ga.Algebra.locals

    def unsigned_locals(algebra, *, expr=False):
        values = original(algebra, expr=expr)
        return MappingProxyType(
            {name: algebra.multivector(np.abs(value.data), name=name, expr=expr) for name, value in values.items()}
        )

    monkeypatch.setattr(ga.Algebra, "locals", unsigned_locals)
    with pytest.raises(AssertionError):
        REPLAY["test_signed_local_values_and_nonzero_replay_are_independent_of_display"](
            REPLAY["GRAMS"][1], -1, "wedge"
        )
