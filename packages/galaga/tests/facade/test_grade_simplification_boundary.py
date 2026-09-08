"""Archive ownership, mutation controls and executable grade/simplification teaching."""

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
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
PUBLIC_FILE = "facade/test_grade_simplification_contracts.py"
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILE))
ARCHIVE = CONTRACT["ARCHIVE"]


def test_all_forty_eight_identities_retain_source_evidence_and_live_owners():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "334133b7987b359929df7f76c7c397e6cbf6765e"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_path"] == "packages/galaga/tests/test_coverage.py"
    assert ARCHIVE["public_owner"] == PUBLIC_FILE
    assert ARCHIVE["sha256"] == "2983d2f42b6032fe238ea3b4f6251411f2779b2fd541f93b78045a1af0ec0333"
    assert hashlib.sha256(ARCHIVE["source"].encode()).hexdigest() == ARCHIVE["sha256"]
    classes = {cls.name: cls for cls in ast.parse(ARCHIVE["source"]).body if isinstance(cls, ast.ClassDef)}
    all_ids = [
        f"{cls.name}.{method.name}"
        for cls in classes.values()
        for method in cls.body
        if isinstance(method, ast.FunctionDef) and method.name.startswith("test_")
    ]
    assert all_ids == ARCHIVE["all_source_test_ids"]
    assert len(all_ids) == len(set(all_ids)) == 137
    owners = {"TestSymbolicGradeEvenOdd", "TestGradePropagation", "TestSimplify"}
    assert set(ARCHIVE["owners"]) == owners
    ids = {name for name in all_ids if name.split(".")[0] in owners}
    assert len(ids) == len(ARCHIVE["test_ids"]) == 48
    assert (
        ids
        == set(ARCHIVE["test_ids"])
        == {
            f"{name}.{method}"
            for name in owners
            for method, _function in inspect.getmembers(CONTRACT[name], inspect.isfunction)
            if method.startswith("test_")
        }
    )
    assert PUBLIC_FILE not in LEGACY_ORACLE_TESTS
    current = ast.parse((TEST_ROOT / "test_coverage.py").read_text())
    assert not owners & {node.name for node in current.body if isinstance(node, ast.ClassDef)}


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


@pytest.mark.skipif(sys.version_info < (3, 14), reason="notebook uses Python 3.14 t-strings")
@pytest.mark.parametrize("gram", NOTEBOOK_GRAMS)
def test_notebook_teaches_computed_grades_rebinding_and_nonzero_wedge_squares(gram):
    notebook = TEST_ROOT.parents[2] / "examples/algebra/involutions_and_grade_ops.py"
    app = runpy.run_path(str(notebook))["app"]
    overrides = {} if gram == NOTEBOOK_GRAMS[0] else {"metric_selector": SimpleNamespace(value=gram)}
    outputs, definitions = app.run(defs=overrides)
    np.testing.assert_array_equal(definitions["gram_matrix"].mat, gram)
    algebra, x = definitions["algebra"], definitions["x"]
    for degree, part in enumerate(definitions["grade_parts"]):
        expected = CONTRACT["oracle"]("grade", gram, (x.data,), {"target": degree})
        CONTRACT["assert_value"](part, expected)
    assert sum(definitions["grade_parts"], algebra.scalar(0)) == x
    assert definitions["even_part"] + definitions["odd_part"] == x
    for title, operation in (
        ("Grade involution", "grade_involution"),
        ("Reverse", "reverse"),
        ("Clifford conjugation", "conjugate"),
    ):
        value = definitions["involution_results"][title]
        CONTRACT["assert_value"](value, CONTRACT["oracle"](operation, gram, (x.data,)))
        assert getattr(ga, operation)(value) == x
    assert definitions["selected_parts"] == definitions["even_part"]
    assert (
        definitions["projection_node"]
        == definitions["simplified_projection"]
        == ga.Call("grade", (ga.Symbol("v"),), {"target": 1})
    )
    assert definitions["vector_projection"] == definitions["e1"]
    assert definitions["bivector_projection"] == 0
    assert definitions["bivector_projection"].homogeneous_grade() is None
    assert definitions["structural_reduction"] == ga.Symbol("v")
    B = definitions["nonsimple_bivector"]
    expected = CONTRACT["oracle"]("outer_product", gram, (B.data, B.data))
    assert np.count_nonzero(expected) == 1 and expected[-1] != 0
    for key in ("wedge_square", "wedge_replay"):
        CONTRACT["assert_value"](definitions[key], expected)
    assert definitions["vector_wedge_replay"] == 0
    assert definitions["wedge_node"] == ga.Call("outer_product", (ga.Symbol("B"), ga.Symbol("B")))
    html = "\n".join(getattr(output, "text", "") for output in outputs)
    for text in (r"\begin{pmatrix}", "Project first", "A name does not promise a grade", "2 e_{1234}", "None"):
        assert text in html
    for value in (x, B, definitions["wedge_square"], *definitions["grade_parts"]):
        assert value.display("value/latex") in html
