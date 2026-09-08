"""Historical ownership, mutation controls and executable provenance teaching."""

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
PUBLIC_FILE = "facade/test_eager_operation_contracts.py"
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILE))
ARCHIVE = CONTRACT["ARCHIVE"]


def test_all_forty_two_identities_retain_source_evidence_and_public_owners():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "2735fe8cd9928eed93a6b726959ead3644a616d8"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_path"] == "packages/galaga/tests/test_coverage.py"
    assert ARCHIVE["public_owner"] == PUBLIC_FILE
    assert ARCHIVE["sha256"] == "c61a5eac5d6dc930e6c4f5b5fab4b0bfbfdee36ef3474f737145e949d0705f2d"
    assert hashlib.sha256(ARCHIVE["source"].encode()).hexdigest() == ARCHIVE["sha256"]
    classes = {cls.name: cls for cls in ast.parse(ARCHIVE["source"]).body if isinstance(cls, ast.ClassDef)}
    all_ids = [
        f"{cls.name}.{method.name}"
        for cls in classes.values()
        for method in cls.body
        if isinstance(method, ast.FunctionDef) and method.name.startswith("test_")
    ]
    assert ARCHIVE["all_source_test_ids"] == all_ids
    assert len(all_ids) == len(set(all_ids)) == 179
    owners = set(ARCHIVE["owners"])
    assert len(owners) == 10
    ids = {name for name in all_ids if name.split(".")[0] in owners}
    assert len(ids) == len(ARCHIVE["test_ids"]) == 42
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


def test_archive_retains_all_values_nodes_and_actual_old_display_boundaries():
    assert len(ARCHIVE["tables"]) == 2
    assert {tuple(table["signature"]) for table in ARCHIVE["tables"]} == {(1, 1, 1), (1, -1, 1)}
    old_nodes = (
        "Add",
        "Sub",
        "ScalarMul",
        "ScalarDiv",
        "Neg",
        "Add",
        "Sub",
        "Gp",
        "Op",
        "Rc",
        "Hi",
        "Sp",
        "Involute",
        "Conjugate",
        "Reverse",
        "Dual",
        "Undual",
        "Unit",
        "Inverse",
        "Even",
        "Odd",
        "Squared",
        "Norm",
    )
    for table in ARCHIVE["tables"]:
        np.testing.assert_array_equal(table["left"], CONTRACT["LEFT"])
        np.testing.assert_array_equal(table["right"], CONTRACT["RIGHT"])
        assert tuple(row["id"] for row in table["operations"]) == CONTRACT["RECIPES"]
        assert tuple(row["node"] for row in table["operations"]) == old_nodes
        for row in table["operations"]:
            assert row["wrapper"] == "Multivector"
            assert row["unicode"] == row["repr"]
            assert row["latex"] and row["unicode"]
            np.testing.assert_array_equal(row["data"], row["replay"])
        assert [row["id"] for row in table["mixed_inputs"]] == [
            f"{recipe}:{state}"
            for recipe in ("geometric_product", "outer_product")
            for state in ("left_plain", "right_plain")
        ]
        assert [row["node"] for row in table["mixed_inputs"]] == ["Gp", "Gp", "Op", "Op"]
        assert all(row["latex"] and row["unicode"] for row in table["mixed_inputs"])
        rows = {row["id"]: row for row in table["operations"]}
        assert rows["divide"]["unicode"] == "a/2"
        assert rows["right_contraction"]["latex"] == r"a \;\llcorner\; b"
        assert rows["conjugate"]["latex"] == r"\bar{a}"
        assert rows["undual"]["unicode"] == "a⋆⁻¹"
    assert ARCHIVE["metadata"] == {
        "scalar": {
            "str": "3",
            "repr": "3",
            "error": {"type": "TypeError", "message": "Scalar has no algebra context; use with Sym nodes"},
        },
        "unit_long_name": {"unicode": "velocity/‖velocity‖", "latex": r"\widehat{velocity}"},
        "aliases": {"normalize": "unit", "normalise": "unit"},
        "properties": {"inv": "inverse", "dag": "reverse", "sq": "squared"},
    }


@pytest.mark.parametrize("field", ("data", "replay"))
@pytest.mark.parametrize("data", ([1], [np.nan] * 8, [0] * 8))
def test_archive_checks_reject_malformed_nonfinite_and_erased_coefficients(field, data):
    table = copy.deepcopy(ARCHIVE["tables"][0])
    table["operations"][7][field] = data
    with pytest.raises(AssertionError):
        CONTRACT["test_archived_eager_and_replayed_values_have_live_public_owners"](table, 7)


def test_mixed_archive_probe_rejects_corrupted_values_and_unrecognized_states():
    table = copy.deepcopy(ARCHIVE["tables"][1])
    table["mixed_inputs"][0]["data"] = [0] * 8
    with pytest.raises(AssertionError):
        CONTRACT["test_archived_mixed_inputs_preserve_numeric_results_and_literal_leaves"](table, 0)
    table["mixed_inputs"][0]["id"] = "geometric_product:unknown"
    with pytest.raises(AssertionError):
        CONTRACT["test_archived_mixed_inputs_preserve_numeric_results_and_literal_leaves"](table, 0)


@pytest.mark.parametrize("operation,replacement", (("unit", "inverse"), ("conjugate", "reverse")))
def test_mixed_grade_oracle_rejects_substituted_unary_operations(monkeypatch, operation, replacement):
    monkeypatch.setattr(ga, operation, getattr(ga, replacement))
    with pytest.raises(AssertionError):
        CONTRACT["check_recipe"](operation)


def test_scalar_result_contract_rejects_a_scalar_multivector_on_the_plain_norm_path(monkeypatch):
    original = ga.norm
    monkeypatch.setattr(ga, "norm", lambda value: value.algebra.scalar(original(value)))
    with pytest.raises(AssertionError):
        CONTRACT["test_eager_results_and_replay_respect_provenance_and_metric_domains"](
            CONTRACT["GRAMS"][0], "norm", "plain"
        )


def test_provenance_check_rejects_commutatively_swapped_source_order(monkeypatch):
    original = ga.Multivector.__radd__

    def reordered(value, other):
        result = original(value, other)
        return result.with_expr(ga.Call("add", tuple(reversed(result.expr.operands))))

    monkeypatch.setattr(ga.Multivector, "__radd__", reordered)
    with pytest.raises(AssertionError):
        CONTRACT["check_recipe"]("radd")


def test_changed_binding_probe_rejects_cached_eager_replay(monkeypatch):
    original = ga.evaluate
    saved = {}

    def cached(expression, **kwargs):
        if expression not in saved:
            saved[expression] = original(expression, **kwargs)
        return saved[expression]

    monkeypatch.setattr(ga, "evaluate", cached)
    with pytest.raises(AssertionError):
        CONTRACT["test_eager_results_and_replay_respect_provenance_and_metric_domains"](
            CONTRACT["GRAMS"][1], "geometric_product", "left_plain"
        )


def test_expression_spelling_probe_rejects_rendering_in_the_wrong_target(monkeypatch):
    original = ga.Multivector.display

    def wrong_target(value, *args, **kwargs):
        return original(value, content=kwargs["content"], target="ascii")

    monkeypatch.setattr(ga.Multivector, "display", wrong_target)
    with pytest.raises(AssertionError):
        CONTRACT["test_reviewed_expression_spellings_do_not_replace_numeric_or_structural_checks"]("outer_product")


def test_alias_probe_rejects_a_silent_normalize_adapter(monkeypatch):
    monkeypatch.setattr(ga, "normalize", ga.unit)
    with pytest.raises(pytest.fail.Exception, match="DID NOT WARN"):
        CONTRACT["TestSymbolicNormalize"]().test_normalize_alias()


def test_unknown_oracle_recipe_and_non_numeric_result_are_rejected():
    with pytest.raises(AssertionError):
        CONTRACT["expected_coefficients"]("unknown", CONTRACT["GRAMS"][0], CONTRACT["LEFT"], CONTRACT["RIGHT"])
    with pytest.raises(AssertionError):
        CONTRACT["assert_coefficients"]("wrong", [1])


def test_eager_operation_contracts_run_with_legacy_imports_blocked():
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
            raise AssertionError('eager-operation contract imported legacy: ' + fullname)
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
def test_notebook_teaches_literal_snapshots_changed_bindings_and_node_rendering():
    notebook = TEST_ROOT.parents[2] / "examples/galaga_v2/eager_values_and_expressions.py"
    outputs, definitions = runpy.run_path(str(notebook))["app"].run()
    algebra = definitions["algebra"]
    literal, named = definitions["literal_history"], definitions["named_history"]
    assert literal == named
    assert literal.expr == ga.Call(
        "geometric_product",
        (
            ga.BladeLiteral(3),
            ga.MultivectorLiteral(definitions["history_source"].data),
        ),
    )
    assert named.expr == ga.Call(
        "geometric_product",
        (
            ga.BladeLiteral(3),
            ga.Symbol("a"),
        ),
    )
    gram = tuple(map(tuple, algebra.gram))
    for key, source in (
        ("literal_history", "history_source"),
        ("literal_replay", "history_source"),
        ("named_history", "history_source"),
        ("named_replay", "history_replacement"),
    ):
        expected = CONTRACT["expected_coefficients"](
            "geometric_product",
            gram,
            algebra.blade(3).data,
            definitions[source].data,
        )
        CONTRACT["assert_coefficients"](definitions[key], expected)
    assert definitions["named_replay"] != named
    assert ga.evaluate(literal.expr, algebra=algebra, environment={"a": definitions["history_replacement"]}) == literal
    assert definitions["scalar_node"] == ga.ScalarLiteral(3)
    assert definitions["scalar_node_value"] == 3
    assert definitions["reflected_node"] == ga.Call("subtract", (ga.ScalarLiteral(3), ga.Symbol("a")))
    assert definitions["reflected_replay"] == 3 - definitions["history_replacement"]
    html = "\n".join(getattr(output, "text", "") for output in outputs)
    for phrase in ("Literal snapshots", "literal_replay", "Call(operation_id=", "3 - a", "nonzero null"):
        assert phrase in html
    for value in (literal, definitions["named_replay"]):
        assert value.display("value/latex") in html
    assert "{_original_value" not in html and "{_math" not in html
