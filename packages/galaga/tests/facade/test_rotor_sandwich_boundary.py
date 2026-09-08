"""Source ownership, negative controls and executable rotor teaching."""

import ast
import copy
import hashlib
import inspect
import runpy
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS, isolate_path

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
PUBLIC_FILE = "facade/test_rotor_sandwich_contracts.py"
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILE))
ARCHIVE = CONTRACT["ARCHIVE"]


def test_twenty_historical_identities_have_full_evidence_and_public_owners():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "fe6d88ae126ef1a5ab8f21757bd53da9da1e7410"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_path"] == "packages/galaga/tests/test_coverage.py"
    assert ARCHIVE["public_owner"] == PUBLIC_FILE
    assert ARCHIVE["sha256"] == "798026ecd51400c85cb8f08710bcb9af819ce16c5c9132b198eaa26c1b0963a1"
    assert hashlib.sha256(ARCHIVE["source"].encode()).hexdigest() == ARCHIVE["sha256"]
    identifiers = [
        f"{cls.name}.{method.name}"
        for cls in ast.parse(ARCHIVE["source"]).body
        if isinstance(cls, ast.ClassDef)
        for method in cls.body
        if isinstance(method, ast.FunctionDef) and method.name.startswith("test_")
    ]
    owners = {
        f"{name}.{method}"
        for name, cls in CONTRACT.items()
        if name.startswith("Test") and inspect.isclass(cls)
        for method, function in inspect.getmembers(cls, inspect.isfunction)
        if method.startswith("test_")
    }
    assert identifiers == ARCHIVE["test_ids"] and len(identifiers) == len(owners) == 20
    assert set(identifiers) == owners
    # The final mixed-file path remains an import-free ownership ledger.
    tree = ast.parse((TEST_ROOT / "test_coverage.py").read_text())
    assert len(tree.body) == 1 and isinstance(tree.body[0], ast.Expr)
    assert ast.get_docstring(tree)
    assert not {PUBLIC_FILE, "test_coverage.py"} & set(LEGACY_ORACLE_TESTS)
    assert not LEGACY_ORACLE_TESTS


def test_complete_archive_keeps_old_errors_aliases_and_false_positive():
    rows = ARCHIVE["rotations"]
    assert len(rows) == len({row["id"] for row in rows}) == 27
    assert {row["method"] for row in rows} == set(CONTRACT["RETIRED"])
    assert {row["form"] for row in rows} == {"radians", "degrees", "positional"}
    assert {row["scale"] for row in rows} == {1, 3, -3}
    assert len(ARCHIVE["sandwiches"]) == 4
    assert {row["method"] for row in ARCHIVE["sandwiches"]} == {"sw", "sandwich"}
    errors = ARCHIVE["errors"]
    assert [row["id"] for row in errors] == ["vector", "trivector", "scalar", "missing_angle", "two_angles"]
    assert all(row["type"] == "ValueError" for row in errors)
    assert errors[0]["message"].endswith("odd-grade components: [1]")
    assert errors[1]["message"].endswith("odd-grade components: [3]")
    assert "bivector" in errors[2]["message"]
    assert errors[3]["arguments"] == {} and errors[4]["arguments"] == {"radians": 1, "degrees": 90}
    assert [row["id"] for row in ARCHIVE["domains"]] == ["elliptic", "hyperbolic", "null", "sta_phase", "nonsimple"]
    nonsimple = CONTRACT["domain_row"]("nonsimple")["result"]
    assert nonsimple["is_rotor"]
    assert nonsimple["reverse_product"][0] == pytest.approx(1)
    assert abs(nonsimple["reverse_product"][15]) > 0.05


@pytest.mark.parametrize("check", (False, True))
def test_isolation_cannot_rewrite_the_completed_mixed_suite(tmp_path, check):
    path = tmp_path / "test_coverage.py"
    source = "from galaga import Algebra\n"
    path.write_text(source)
    with pytest.raises(ValueError, match="not in the Phase 8"):
        isolate_path(path, tests_root=tmp_path, check=check)
    assert path.read_text() == source


@pytest.mark.parametrize(
    "field", ("data", "shape", "nonfinite", "sandwich", "reverse_product", "scale", "theta", "is_rotor")
)
def test_rotation_archive_replay_rejects_corruption(field):
    row = copy.deepcopy(CONTRACT["rotation_row"]("rotor_quarter"))
    if field == "data":
        row["data"][3] *= -1
    elif field == "shape":
        row["data"] = [0]
    elif field == "nonfinite":
        row["data"][0] = np.nan
    elif field == "sandwich":
        row["sandwich"][2] *= -1
    elif field == "reverse_product":
        row["reverse_product"][0] = 4
    elif field == "scale":
        row["scale"] = -1
    elif field == "theta":
        row["theta"] = 0
    else:
        row["is_rotor"] = False
    with pytest.raises(AssertionError):
        CONTRACT["test_every_archived_rotation_uses_explicit_angle_units_and_normalization"](row, True)


def test_quarter_turn_probe_rejects_reversed_exponential_orientation(monkeypatch):
    original = ga.exp
    monkeypatch.setattr(ga, "exp", lambda value: original(-value))
    with pytest.raises(AssertionError):
        CONTRACT["TestRotorFromPlaneAngle"]().test_90_degree_rotation(ga.Algebra(3))


def test_domain_probe_rejects_the_old_scalar_only_rotor_predicate(monkeypatch):
    def scalar_only(value, *, atol=1e-12):
        return ga.is_even(value) and abs(float(ga.grade(value * ~value, 0)) - 1) <= atol

    monkeypatch.setattr(ga, "is_rotor", scalar_only)
    with pytest.raises(AssertionError):
        CONTRACT["test_legacy_domain_observations_are_evidence_not_rotor_guarantees"](
            CONTRACT["domain_row"]("nonsimple")
        )


def test_sandwich_probe_rejects_substituting_inverse_for_reverse(monkeypatch):
    monkeypatch.setattr(ga, "sandwich", lambda rotor, value: rotor * value * ga.inverse(rotor))
    with pytest.raises(AssertionError):
        CONTRACT["test_sandwich_preserves_all_input_grades_and_uses_reverse_even_when_scaled"](
            CONTRACT["GRAMS"][1], True
        )


def test_assertion_helpers_reject_nonfinite_expected_data_and_unknown_rows():
    with pytest.raises(AssertionError):
        CONTRACT["assert_data"]([0], [np.inf])
    for helper in ("domain_row", "rotation_row"):
        with pytest.raises(StopIteration):
            CONTRACT[helper]("unknown")


def test_public_rotor_contracts_run_with_legacy_imports_blocked():
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
            raise AssertionError('rotor contract imported legacy: ' + fullname)
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


@pytest.mark.skipif(sys.version_info < (3, 14), reason="notebook uses Python 3.14 t-strings")
@pytest.mark.parametrize("degrees", (0, 55, 90, 180))
def test_notebook_teaches_metric_branches_compound_rotors_and_even_phase_boundaries(degrees):
    path = TEST_ROOT.parents[2] / "examples/algebra/exp_log_rotors.py"
    outputs, definitions = runpy.run_path(str(path))["app"].run(defs={"angle": SimpleNamespace(value=degrees)})
    theta, plane = definitions["rotation_angle"], definitions["rotation_plane"]
    assert theta == np.deg2rad(degrees)
    a, b, _ = plane.algebra.basis_vectors()
    CONTRACT["assert_data"](definitions["rotated_vector"].data, (np.cos(theta) * a + np.sin(theta) * b).data)
    CONTRACT["assert_data"](definitions["recovered_generator"].data, (-theta / 2 * plane).data)
    assert len(definitions["metric_examples"]) == 4
    for row in definitions["metric_examples"]:
        gram = row["plane"].algebra.gram
        np.testing.assert_array_equal(row["gram"].mat, gram)
        square = gram[0, 1] ** 2 - gram[0, 0] * gram[1, 1]
        assert square == row["square"] == float(row["plane"] * row["plane"])
        scale = 1 / np.sqrt(abs(square)) if square else 1
        generator = 2 * scale * np.array([[gram[0, 1], gram[1, 1]], [-gram[0, 0], -gram[0, 1]]])
        coordinates = CONTRACT["matrix_exp"](-0.3 * generator)[:, 0]
        CONTRACT["assert_data"](row["result"].data, row["plane"].algebra.vector(coordinates).data)
        CONTRACT["assert_data"](row["logarithm"].data, (-0.3 * row["generator"]).data)
    compound, factored = definitions["compound_rotor"], definitions["compound_factored"]
    CONTRACT["assert_data"](compound.data, factored.data)
    assert ga.is_rotor(compound) and not ga.is_rotor(definitions["incomplete_rotor"])
    assert np.linalg.norm(definitions["compound_grade_four"].data) > 0.05
    assert np.linalg.norm(ga.grade(definitions["incomplete_reverse_product"], 4).data) > 0.05
    phase = definitions["sta_phase"]
    assert ga.is_even(phase) and not ga.is_rotor(phase)
    CONTRACT["assert_data"](definitions["phase_sandwich"].data, phase.algebra.blade(1).data)
    assert np.linalg.norm(ga.grade(definitions["phase_conjugated"], 3).data) > 0.4
    html = "\n".join(getattr(output, "text", "") for output in outputs)
    for text in ("An oriented Euclidean plane", "Gram matrix choose", "grade-four term", "even phase", "rapidity"):
        assert text in html
    for key in ("compound_grade_four", "incomplete_reverse_product", "phase_reverse_product", "phase_conjugated"):
        assert definitions[key].latex(content="value") in html
