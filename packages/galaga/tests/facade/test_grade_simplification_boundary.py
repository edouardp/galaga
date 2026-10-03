"""Archive ownership, mutation controls and executable grade/simplification teaching."""

import copy
import runpy
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
PUBLIC_FILE = "facade/test_grade_simplification_contracts.py"
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILE))
ARCHIVE = CONTRACT["ARCHIVE"]


def test_archive_keeps_grade_cache_differences_scalar_errors_and_the_invalid_wedge_rewrite():
    assert len(ARCHIVE["tables"]) == 2
    assert {tuple(t["signature"]) for t in ARCHIVE["tables"]} == {(1, 1, 1), (1, -1, 1)}
    for table in ARCHIVE["tables"]:
        assert len(table["grades"]) == len({r["id"] for r in table["grades"]}) == 15
        assert [r["id"] for r in table["simplifications"]] == list(CONTRACT["RECIPES"])
        assert len(table["simplifications"]) == 30
        assert table["auto_grades"] == {"v": 1, "B": 2, "s": 0}
        grades = {r["id"]: r for r in table["grades"]}
        assert grades["gp"]["cached_grade"] is None
        assert grades["gp"]["homogeneous_grade"] == 2
        assert grades["hestenes_inner"]["cached_grade"] == 0
        assert grades["hestenes_inner"]["homogeneous_grade"] is None
        assert len(table["projections"]) == 4
        assert [r["node"] for r in table["projections"]] == ["Even", "Odd", "Even", "Odd"]
        assert [r["unicode"] for r in table["projections"]] == ["⟨v⟩₊", "⟨v⟩₋", "⟨v⟩₊", "⟨v⟩₋"]
        errors = {r["id"] for r in table["simplifications"] if "evaluation_error" in r}
        assert errors == {
            "mul_identity_left",
            "mul_identity_right",
            "mul_zero_left",
            "mul_zero_right",
            "add_zero_left",
            "add_zero_right",
            "nested",
        }
        for row in table["simplifications"]:
            assert row["unicode"] and row["latex"] and row["wrapper"] and row["node"]
            assert row["simplified"]["unicode"] and row["simplified"]["latex"]
            if row["id"] in errors:
                assert row["evaluation_error"] == {
                    "type": "TypeError",
                    "message": "Scalar has no algebra context; use with Sym nodes",
                }
    counterexample = ARCHIVE["wedge_counterexample"]
    assert counterexample["cached_grade"] == counterexample["homogeneous_grade"] == 4
    assert counterexample["data"] == [0] * 15 + [2]
    assert counterexample["simplified"] == {"unicode": "0", "node": "Scalar", "scalar": 0}


@pytest.mark.parametrize("data", ([1], [np.nan] * 8, [0] * 8))
def test_grade_archive_probe_rejects_malformed_nonfinite_and_erased_coefficients(data):
    table = copy.deepcopy(ARCHIVE["tables"][0])
    table["grades"][0]["data"] = data
    with pytest.raises(AssertionError):
        CONTRACT["test_archived_grade_results_have_live_numeric_owners"](table, 0)


@pytest.mark.parametrize("field", ("original", "simplified"))
def test_simplification_archive_probe_rejects_changed_original_and_replayed_values(field):
    table = copy.deepcopy(ARCHIVE["tables"][0])
    target = table["simplifications"][0]
    if field == "simplified":
        target = target["simplified"]
    target["data"] = [0] * 8
    with pytest.raises(AssertionError):
        CONTRACT["test_archived_simplified_values_replay_with_explicit_bindings"](table, 0)


def test_grade_probe_rejects_stale_cached_grade_metadata(monkeypatch):
    monkeypatch.setattr(ga.Multivector, "homogeneous_grade", lambda value, **kwargs: None)
    with pytest.raises(AssertionError):
        CONTRACT["TestGradePropagation"]().test_gp_no_grade()


def test_wedge_probe_rejects_unconditional_self_annihilation(monkeypatch):
    monkeypatch.setattr(ga, "simplify", lambda expression: ga.ScalarLiteral(0))
    with pytest.raises(AssertionError):
        CONTRACT["test_wedge_self_requires_actual_grade_information_not_a_symbol_name"]()


def test_grade_projection_probe_rejects_assuming_a_symbol_is_always_a_vector(monkeypatch):
    monkeypatch.setattr(ga, "simplify", lambda expression: ga.Symbol("v"))
    with pytest.raises(AssertionError):
        CONTRACT["check_simplification"]("grade_known_match")


def test_fixed_point_probe_rejects_a_single_pass(monkeypatch):
    from galaga.expression._simplify import _simplify_once

    monkeypatch.setattr(ga, "simplify", _simplify_once)
    with pytest.raises(AssertionError):
        CONTRACT["test_fixed_point_reduction_does_not_need_symbol_values"]()


def test_numeric_probe_rejects_replay_that_returns_only_a_scalar(monkeypatch):
    monkeypatch.setattr(ga, "evaluate", lambda expression, **kwargs: kwargs["algebra"].scalar(1))
    with pytest.raises(AssertionError):
        CONTRACT["check_simplification"]("double_reverse")


def test_three_target_projection_probe_rejects_wrong_target_output(monkeypatch):
    original = ga.Multivector.display
    monkeypatch.setattr(
        ga.Multivector, "display", lambda value, **kwargs: original(value, content="expr", target="ascii")
    )
    with pytest.raises(AssertionError):
        CONTRACT["check_projection"]("even_grades", "even")


def test_oracles_reject_unknown_nodes_operations_and_non_multivector_results():
    gram = CONTRACT["GRAMS"][0]
    with pytest.raises(AssertionError):
        CONTRACT["oracle"]("unknown", gram, (CONTRACT["LEFT"], CONTRACT["RIGHT"]))
    with pytest.raises(AssertionError):
        CONTRACT["oracle_expression"](object(), gram, {})
    with pytest.raises(AssertionError):
        CONTRACT["assert_value"](1.0, [1])


def test_grade_and_simplification_contracts_run_without_legacy_imports():
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
            raise AssertionError('grade/simplification contract imported legacy: ' + fullname)
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


NOTEBOOK_GRAMS = (
    ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
    ((2, 0.5, 0, 0), (0.5, -1, 0, 0), (0, 0, 1, 0.25), (0, 0, 0.25, 3)),
    ((1, 1, 0, 0), (1, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 0)),
)
