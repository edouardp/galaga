"""Complete historical ownership, negative controls and executable teaching."""

import ast
import copy
import hashlib
import json
import runpy
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS, isolate_path, main

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
STATE = runpy.run_path(str(TEST_ROOT / "presentation/test_redesign_state_contracts.py"))
ARCHIVE = STATE["ARCHIVE"]
OWNERS = json.loads((TEST_ROOT.parent / "tools/baselines/redesign-v2-owners.json").read_text())


def validate_owners(manifest):
    assert manifest["schema_version"] == 1
    assert manifest["archive"] == "redesign-v1.json"
    assert manifest["source_sha256"] == ARCHIVE["sha256"]
    identifiers = []
    for group in manifest["groups"].values():
        assert group["decision"] and group["tests"] and group["owners"]
        identifiers.extend(group["tests"])
        for owner in group["owners"]:
            file, *names = owner.split("::")
            assert file not in LEGACY_ORACLE_TESTS and names
            path = TEST_ROOT / file
            assert path.resolve().is_relative_to(TEST_ROOT.resolve())
            body = ast.parse(path.read_text()).body
            for name in names:
                matches = [
                    node for node in body if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name == name
                ]
                assert len(matches) == 1, owner
                body = matches[0].body
            assert isinstance(matches[0], ast.FunctionDef) and names[-1].startswith("test_")
    assert len(identifiers) == len(set(identifiers)) == 279
    assert set(identifiers) == set(ARCHIVE["test_ids"])


def test_all_279_historical_identities_have_source_evidence_and_explicit_public_owners():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "0499fa49800950503467cac60eb9d199231458c0"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_path"] == "packages/galaga/tests/test_redesign.py"
    assert ARCHIVE["sha256"] == "c61490dbb7ed8e3ed6dc6b2574198cc28a4d54fc918cec9ad8c44664117e1b6a"
    assert hashlib.sha256(ARCHIVE["source"].encode()).hexdigest() == ARCHIVE["sha256"]
    identifiers = [
        f"{cls.name}.{method.name}"
        for cls in ast.parse(ARCHIVE["source"]).body
        if isinstance(cls, ast.ClassDef)
        for method in cls.body
        if isinstance(method, ast.FunctionDef) and method.name.startswith("test_")
    ]
    assert identifiers == ARCHIVE["test_ids"]
    assert [row["id"] for row in ARCHIVE["observations"]] == identifiers
    validate_owners(OWNERS)
    assert len(ARCHIVE["snapshots"]) == 189
    for snapshot in ARCHIVE["snapshots"]:
        if snapshot["kind"] == "multivector":
            STATE["sparse_data"](snapshot)
    for row in ARCHIVE["observations"]:
        for value in row["locals"].values():
            if isinstance(value, dict) and "snapshot" in value:
                assert 0 <= value["snapshot"] < len(ARCHIVE["snapshots"])
        for left, right in row["aliases"]:
            assert row["locals"][left] == row["locals"][right]
    renamed = next(row for row in ARCHIVE["observations"] if row["id"] == "TestSpecUseCases.test_use_case_5_rename")
    assert ["B", "B2"] in renamed["aliases"]  # Historical in-place naming, not a v2 promise.
    tree = ast.parse((TEST_ROOT / "test_redesign.py").read_text())
    assert len(tree.body) == 1 and ast.get_docstring(tree)
    assert LEGACY_ORACLE_TESTS == ()


@pytest.mark.parametrize("corruption", ("missing", "duplicate", "unknown", "owner", "decision", "hash"))
def test_crosswalk_validation_rejects_lost_or_fictitious_ownership(corruption):
    manifest = copy.deepcopy(OWNERS)
    group = next(iter(manifest["groups"].values()))
    if corruption == "missing":
        group["tests"].pop()
    elif corruption == "duplicate":
        group["tests"].append(group["tests"][0])
    elif corruption == "unknown":
        group["tests"][0] = "TestFiction.test_missing"
    elif corruption == "owner":
        group["owners"][0] = "facade/test_redesign_workflows.py::test_missing"
    elif corruption == "decision":
        group["decision"] = ""
    else:
        manifest["source_sha256"] = "changed"
    with pytest.raises(AssertionError):
        validate_owners(manifest)


@pytest.mark.parametrize("coefficients", ([[1, 1], [1, 2]], [[-1, 1]], [[8, 1]], [[1.0, 1]], [[1, np.nan]], [[1, 0]]))
def test_archive_data_validation_rejects_duplicate_invalid_or_nonfinite_coefficients(coefficients):
    with pytest.raises(AssertionError):
        STATE["sparse_data"]({"signature": [1, 1, 1], "coefficients": coefficients})


@pytest.mark.parametrize("data", ([0] * 8, [1], [np.nan] * 8))
def test_workflow_oracle_rejects_erased_misshapen_or_nonfinite_results(data, monkeypatch):
    contract = runpy.run_path(str(TEST_ROOT / "facade/test_redesign_workflows.py"))
    monkeypatch.setitem(contract["STATE"], "sparse_data", lambda _: np.asarray(data))
    with pytest.raises(AssertionError):
        contract["test_ten_archived_workflows_keep_numeric_results_with_explicit_state_choices"](
            *contract["CASES"][0], True
        )


@pytest.mark.parametrize("check", (False, True))
def test_completed_redesign_cannot_be_rewritten_and_the_empty_ledger_is_a_noop(tmp_path, check):
    path = tmp_path / "test_redesign.py"
    source = "from galaga import Algebra\n"
    path.write_text(source)
    with pytest.raises(ValueError, match="not in the Phase 8"):
        isolate_path(path, tests_root=tmp_path, check=check)
    assert path.read_text() == source
    args = ["--repository", str(tmp_path / "nonexistent")]
    assert main(args + (["--check"] if check else [])) == 0


def test_every_mapped_owner_collects_and_runs_with_legacy_imports_blocked():
    owners = sorted({owner for group in OWNERS["groups"].values() for owner in group["owners"]})
    files = sorted({owner.split("::")[0] for owner in owners} | {"core/test_division_contracts.py"})
    program = """
import importlib.abc
import json
import sys
from pathlib import Path
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
            raise AssertionError('redesign owner imported legacy: ' + fullname)
sys.meta_path.insert(0, RejectLegacy())
root = Path(sys.argv[1])
expected = set(json.loads(sys.argv[2]))
class CheckOwners:
    def pytest_collection_modifyitems(self, items):
        collected = {
            str(Path(str(item.path)).relative_to(root)) + '::' + item.nodeid.split('::', 1)[1].split('[', 1)[0]
            for item in items
        }
        assert expected <= collected, expected - collected
        assert not any(item.get_closest_marker('skip') or item.get_closest_marker('xfail') for item in items)
import pytest
result = pytest.main(['--noconftest', '-c', '/dev/null', '-p', 'no:cacheprovider', '-q', *sys.argv[3:]],
                     plugins=[CheckOwners()])
assert result == 0
assert not any(forbidden(name) for name in sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-c", program, str(TEST_ROOT), json.dumps(owners), *(str(TEST_ROOT / file) for file in files)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.skipif(sys.version_info < (3, 14), reason="Native template strings require Python 3.14")
def test_eager_values_lesson_teaches_rebindable_denominators_and_finite_subnormal_division():
    path = TEST_ROOT.parents[2] / "examples/galaga_v2/eager_values_and_expressions.py"
    outputs, definitions = runpy.run_path(str(path))["app"].run()
    assert outputs
    quotient = definitions["physical_quotient"]
    expected = 1.055e-34 / (9.109e-31 * 3e8)
    assert float(quotient) == pytest.approx(expected, rel=2e-15, abs=0)
    assert float(definitions["quotient_rebound"]) == pytest.approx(expected / 2, rel=2e-15, abs=0)
    assert quotient.display("expr/latex") == r"\frac{\hbar}{m_e c}"
    assert quotient.expr.operands[1].operation_id == "geometric_product"
    tiny = definitions["subnormal_quotient"]
    assert tiny == 1 and ga.evaluate(tiny.expr, algebra=tiny.algebra) == 1
    assert definitions["small_default_latex"] == "0" and definitions["small_visible_latex"] != "0"
    assert definitions["third_replayed"] == definitions["third_named"]
