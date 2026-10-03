"""Source ownership, negative controls and executable rotor teaching."""

import copy
import runpy
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
PUBLIC_FILE = "facade/test_rotor_sandwich_contracts.py"
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILE))
ARCHIVE = CONTRACT["ARCHIVE"]


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
