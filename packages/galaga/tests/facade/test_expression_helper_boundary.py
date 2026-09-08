"""Historical ownership, mutation checks and teaching for expression helpers."""

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
PUBLIC_FILE = "facade/test_expression_helper_contracts.py"
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILE))
ARCHIVE = CONTRACT["ARCHIVE"]


def test_seventeen_helper_identities_have_complete_source_evidence_and_public_owners():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "4f8b1660323192b07679cc70d67b389930f13b05"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_path"] == "packages/galaga/tests/test_coverage.py"
    assert ARCHIVE["public_owner"] == PUBLIC_FILE
    assert ARCHIVE["sha256"] == "ef65c3104f49824ff1963058ceaa5f81560ae46c5fba8e9397b23f36c6a5e545"
    assert hashlib.sha256(ARCHIVE["source"].encode()).hexdigest() == ARCHIVE["sha256"]
    source = ast.parse(ARCHIVE["source"])
    ids = [
        f"{cls.name}.{method.name}"
        for cls in source.body
        if isinstance(cls, ast.ClassDef)
        for method in cls.body
        if isinstance(method, ast.FunctionDef) and method.name.startswith("test_")
    ]
    assert ids == ARCHIVE["all_source_test_ids"] and len(set(ids)) == 89
    owners = {
        f"TestCoverageGaps.{name}"
        for name, function in inspect.getmembers(CONTRACT["TestCoverageGaps"], inspect.isfunction)
        if name.startswith("test_")
    }
    assert owners == set(ARCHIVE["test_ids"]) and len(owners) == 17
    assert owners <= set(ids)
    current = ast.parse((TEST_ROOT / "test_coverage.py").read_text())
    remaining = {
        f"{cls.name}.{method.name}"
        for cls in current.body
        if isinstance(cls, ast.ClassDef)
        for method in cls.body
        if isinstance(method, ast.FunctionDef) and method.name.startswith("test_")
    }
    assert not owners & remaining
    assert PUBLIC_FILE not in LEGACY_ORACLE_TESTS


def test_archive_keeps_actual_private_behavior_instead_of_misleading_test_comments():
    assert len(ARCHIVE["tables"]) == 2
    assert {tuple(t["signature"]) for t in ARCHIVE["tables"]} == {(1, 1, 1), (1, -1, 1)}
    for table in ARCHIVE["tables"]:
        assert [r["id"] for r in table["known_grades"]] == list(CONTRACT["KNOWN"])
        assert len(table["equalities"]) == len({r["id"] for r in table["equalities"]}) == 8
        assert [r["equal"] for r in table["equalities"]] == [True, False, True, False, True, False, True, False]
        assert [r["id"] for r in table["reflected"]] == ["geometric_product", "scalar_multiply"]
        assert [r["unicode"] for r in table["reflected"]] == ["ba", "5a"]
        assert [r["id"] for r in table["parity"]] == ["even_grades:v", "even_grades:B", "odd_grades:v", "odd_grades:B"]
        known = {r["id"]: r for r in table["known_grades"]}
        assert known["grade"]["known_grade"] == 2 and known["grade"]["homogeneous_grade"] is None
        assert known["add"]["known_grade"] is None and known["add"]["homogeneous_grade"] == 1
        assert table["equality_bindings"]["a"] == table["equality_bindings"]["b"]
        for row in table["equalities"]:
            for side in ("left", "right"):
                assert row[side]["unicode"] and row[side]["latex"] and row[side]["node"]
    explicit = ARCHIVE["explicit_grade"]
    assert explicit["requested"] == explicit["raw_Sym_grade"] == 2
    assert explicit["sym_grade"] == explicit["inspected"] == 1
    assert ARCHIVE["scalar"]["scalar"] == 42
    assert ARCHIVE["scalar"]["unicode"] == ARCHIVE["scalar"]["latex"] == "42"
    assert ARCHIVE["invalid_coercion"] == {"type": "TypeError", "message": "Cannot convert <class 'list'> to Expr"}
    assert ARCHIVE["unknown_equality"] is False
    source_class = next(
        n for n in ast.parse(ARCHIVE["source"]).body if isinstance(n, ast.ClassDef) and n.name == "TestCoverageGaps"
    )
    fallback = next(n for n in source_class.body if isinstance(n, ast.FunctionDef) and n.name == "test_eq_fallback")
    calls = {n.func.id for n in ast.walk(fallback) if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert "Dual" in calls and "Expr" not in calls


@pytest.mark.parametrize("data", ([1], [np.nan] * 8, [0] * 8))
def test_archive_grade_replay_rejects_bad_shapes_nonfinite_and_erased_values(data):
    table = copy.deepcopy(ARCHIVE["tables"][0])
    table["known_grades"][2]["data"] = data
    with pytest.raises(AssertionError):
        CONTRACT["test_archived_known_grade_observations_retain_numeric_owners"](table, 2)


@pytest.mark.parametrize("corruption", ("equality", "coefficients"))
def test_archive_equality_probe_checks_both_structure_and_numeric_observations(corruption):
    table = copy.deepcopy(ARCHIVE["tables"][0])
    row = table["equalities"][0]
    if corruption == "equality":
        row["equal"] = False
    else:
        row["left"]["data"] = [0] * 8
    with pytest.raises(AssertionError):
        CONTRACT["test_archived_private_equalities_use_public_structure_and_explicit_replay"](table, 0)


def test_operand_order_probe_rejects_forward_multiplication_as_reflected_multiplication(monkeypatch):
    monkeypatch.setattr(ga.Multivector, "__rmul__", ga.Multivector.__mul__)
    with pytest.raises(AssertionError):
        CONTRACT["TestCoverageGaps"]().test_expr_rmul_expr()


def test_structural_probe_rejects_calls_that_compare_equal_regardless_of_operands(monkeypatch):
    monkeypatch.setattr(ga.Call, "__eq__", lambda left, right: True)
    with pytest.raises(AssertionError):
        CONTRACT["check_pair"]("conjugate")


def test_hash_probe_rejects_identity_hashes_on_structurally_equal_nodes(monkeypatch):
    monkeypatch.setattr(ga.Call, "__hash__", object.__hash__)
    with pytest.raises(AssertionError):
        CONTRACT["check_pair"]("conjugate")


def test_float_probe_rejects_approximate_literal_equality(monkeypatch):
    monkeypatch.setattr(ga.ScalarLiteral, "__eq__", lambda left, right: bool(np.isclose(left.value, right.value)))
    with pytest.raises(AssertionError):
        CONTRACT["test_float_literal_equality_is_exact_and_equal_hashes_support_lookup"]((1.0, np.nextafter(1.0, 2.0)))


def test_name_probe_rejects_identity_based_only_on_the_ascii_spelling(monkeypatch):
    monkeypatch.setattr(ga.Name, "__eq__", lambda left, right: left.ascii == right.ascii)
    with pytest.raises(AssertionError):
        CONTRACT["test_all_name_spellings_participate_in_symbol_identity_not_only_ascii"]()


def test_replay_probe_rejects_a_cache_that_ignores_new_bindings(monkeypatch):
    original = ga.evaluate
    saved = {}

    def cached(node, **kwargs):
        if node not in saved:
            saved[node] = original(node, **kwargs)
        return saved[node]

    monkeypatch.setattr(ga, "evaluate", cached)
    with pytest.raises(AssertionError):
        CONTRACT["test_equal_nodes_replay_with_new_bindings_without_becoming_cached_values"](
            "conjugate", CONTRACT["GRAMS"][1]
        )


def test_comparison_helpers_reject_non_values_and_unknown_oracle_nodes():
    with pytest.raises(AssertionError):
        CONTRACT["assert_value"](1, [1])
    with pytest.raises(AssertionError):
        CONTRACT["expected"](object(), CONTRACT["GRAMS"][0], {})
    with pytest.raises(AssertionError):
        CONTRACT["expected"](ga.Call("squared", (ga.Symbol("a"),)), CONTRACT["GRAMS"][0], {"a": CONTRACT["MIXED"]})


def test_public_helper_contracts_run_with_legacy_imports_blocked():
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
            raise AssertionError('expression helper contract imported legacy: ' + fullname)
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
def test_notebook_distinguishes_numeric_structural_rendered_and_float_equality():
    notebook = TEST_ROOT.parents[2] / "examples/galaga_v2/eager_values_and_expressions.py"
    outputs, definitions = runpy.run_path(str(notebook))["app"].run()
    left, right = definitions["identity_left"], definitions["identity_right"]
    assert definitions["identity_values_equal"] is True
    assert definitions["identity_histories_equal"] is False
    assert definitions["identity_renderings_equal"] is True
    assert left == right and hash(left) == hash(right) and left.expr != right.expr
    assert left.expr == ga.Call("scalar_multiply", (ga.Symbol(ga.Name("left", "left", "x")),), {"scalar": 5})
    assert right.expr == ga.Call("scalar_multiply", (ga.Symbol(ga.Name("right", "right", "x")),), {"scalar": 5})
    assert left.display("expr/latex") == right.display("expr/latex") == "5 x"
    algebra = definitions["algebra"]
    CONTRACT["assert_value"](left, 5 * algebra.vector((1, 2, -1)).data)
    CONTRACT["assert_value"](definitions["identity_rebound"], 5 * algebra.vector((2, 0, 1)).data)
    assert definitions["identity_rebound"] != right
    first, second = definitions["adjacent_literals"]
    assert first.value == 1 and second.value == np.nextafter(1.0, 2.0) and first != second
    assert definitions["adjacent_literals_equal"] is False
    CONTRACT["assert_equal_nodes"](*definitions["signed_zero_literals"])
    assert definitions["signed_zero_lookup"] == "same key"
    html = "\n".join(getattr(output, "text", "") for output in outputs)
    for text in (
        "Three different meanings of equality",
        "Expression histories",
        "False",
        "1.0000000000000002",
        "same key",
    ):
        assert text in html
    assert definitions["identity_rebound"].display("value/latex") in html
