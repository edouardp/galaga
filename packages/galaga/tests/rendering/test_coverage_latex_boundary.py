"""Archive ownership, corruption controls and the rendering teaching boundary."""

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
PUBLIC_FILE = "rendering/test_coverage_latex_contracts.py"
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILE))
ARCHIVE = CONTRACT["ARCHIVE"]


def test_all_forty_three_historical_identities_have_source_evidence_and_public_owners():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "506cb838f846445d476c04fa91ed5ef2cfc08bc1"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_path"] == "packages/galaga/tests/test_coverage.py"
    assert ARCHIVE["public_owner"] == PUBLIC_FILE
    assert ARCHIVE["sha256"] == "a413894f95f5813086206c3c8e05864c1bce30873ebc9ab9784769d13f57699c"
    assert hashlib.sha256(ARCHIVE["source"].encode()).hexdigest() == ARCHIVE["sha256"]
    source = ast.parse(ARCHIVE["source"])
    identifiers = [
        f"{cls.name}.{method.name}"
        for cls in source.body
        if isinstance(cls, ast.ClassDef)
        for method in cls.body
        if isinstance(method, ast.FunctionDef) and method.name.startswith("test_")
    ]
    assert identifiers == ARCHIVE["all_source_test_ids"] and len(set(identifiers)) == 72
    owners = {
        f"{name}.{method}"
        for name, cls in CONTRACT.items()
        if name.startswith("Test") and inspect.isclass(cls)
        for method, function in inspect.getmembers(cls, inspect.isfunction)
        if method.startswith("test_")
    }
    rows = ARCHIVE["tests"]
    assert len(owners) == len(rows) == 43
    assert owners == set(ARCHIVE["test_ids"]) == {row["id"] for row in rows}
    assert owners <= set(identifiers)
    assert sum(len(row["observations"]) for row in rows) == 55
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


def test_archive_retains_old_glyphs_zero_examples_and_the_explicit_custom_latex():
    first = {row["id"]: row["observations"][0] for row in ARCHIVE["tests"]}
    for operation, glyph in (("left", r"\lrcorner"), ("right", r"\llcorner")):
        row = first[f"TestLatex.test_{operation}_contraction"]
        assert glyph in row["latex"]
        assert row["data"] == [0] * 8  # Old orthogonal vectors did not prove signs.
    assert first["TestLatex.test_reverse"]["latex"] == r"\tilde{R}"
    assert first["TestLatex.test_involute"]["latex"] == r"\hat{v}"
    assert first["TestLatex.test_conjugate"]["latex"] == r"\bar{v}"
    assert first["TestLatex.test_multivector_latex_bare"]["latex"] == "3 e_{1} + 4 e_{2}"
    assert first["TestCoverageGaps.test_blade_latex_custom_names_no_latex"]["latex"] == "𝐚 𝐛"
    assert "3 e_{12}" in ARCHIVE["source"]  # The permissive assertion's wrong alternative is archived.


@pytest.mark.parametrize("corruption", ("coefficients", "shape", "nonfinite", "bindings", "latex", "wrap"))
def test_archive_replay_rejects_corrupted_evidence(corruption, monkeypatch):
    row = copy.deepcopy(next(r for r in ARCHIVE["tests"] if r["id"] == "TestLatex.test_gp"))
    observation = row["observations"][0]
    if corruption == "coefficients":
        observation["data"] = [0] * 8
    elif corruption == "shape":
        observation["data"] = [0]
    elif corruption == "nonfinite":
        observation["data"] = [float("nan")] * 8
    elif corruption == "bindings":
        observation["bindings"]["v"] = [0] * 8
    elif corruption == "wrap":
        observation["wrap"] = "$$"
    else:
        observation["latex"] = "unreviewed"
    with pytest.raises(AssertionError):
        CONTRACT["check_archived_method"](row, monkeypatch)


def test_archive_replay_rejects_a_historical_method_that_stops_rendering(monkeypatch):
    row = next(r for r in ARCHIVE["tests"] if r["id"] == "TestLatex.test_gp")
    monkeypatch.setattr(CONTRACT["TestLatex"], "test_gp", lambda self, cl3: None)
    with pytest.raises(AssertionError, match="lost its live numeric owner"):
        CONTRACT["check_archived_method"](row, monkeypatch)


@pytest.mark.parametrize("layer", ("format", "replay", "numeric"))
def test_mixed_probes_reject_wrong_rendering_replay_or_product_order(layer, monkeypatch):
    check = CONTRACT["test_nonvacuous_compositions_preserve_values_replay_and_exact_scope"]
    if layer == "format":
        monkeypatch.setattr(ga.Multivector, "display", lambda *args, **kwargs: "wrong")
    elif layer == "replay":
        monkeypatch.setattr(ga, "evaluate", lambda node, *, algebra, environment: algebra.identity)
    else:
        monkeypatch.setattr(ga, "left_contraction", lambda a, b: ga.right_contraction(b, a))
    with pytest.raises(AssertionError):
        check(CONTRACT["GRAMS"][1], "left", "latex")


def test_wrapper_probe_rejects_rich_display_that_ignores_requested_content(monkeypatch):
    monkeypatch.setattr(ga.Multivector, "_repr_latex_", lambda value: value.latex(content="value", wrap="$"))
    with pytest.raises(AssertionError):
        CONTRACT["test_wrapping_and_rich_hooks_preserve_selected_content_and_scoped_notation"](
            CONTRACT["GRAMS"][0], "expr", "latex"
        )


def test_reference_helpers_reject_unknown_nodes_and_operations():
    oracle = CONTRACT["reference_value"]
    gram = CONTRACT["GRAMS"][0]
    with pytest.raises(AssertionError):
        oracle(object(), gram, {})
    with pytest.raises(AssertionError):
        oracle(ga.Call("subtract", (ga.Symbol("a"), ga.Symbol("a"))), gram, {"a": np.ones(4)})
    with pytest.raises(AssertionError):
        CONTRACT["assert_data"]([float("inf")], [0])


def test_public_latex_contracts_run_with_legacy_imports_blocked():
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
            raise AssertionError('public LaTeX contract imported legacy: ' + fullname)
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
def test_notebook_teaches_ambiguous_accents_and_metric_derived_contraction_signs():
    path = TEST_ROOT.parents[2] / "examples/galaga_v2/presentation_contexts.py"
    outputs, definitions = runpy.run_path(str(path))["app"].run()
    algebra = definitions["comparison_algebra"]
    np.testing.assert_array_equal(definitions["comparison_gram"].mat, algebra.gram)
    a, b, B = (definitions["comparison_" + key] for key in ("a", "b", "plane"))
    gram = tuple(map(tuple, algebra.gram))
    environment = {"a": a, "b": b, "B": B}
    arrays = {name: value.data for name, value in environment.items()}
    for key in ("plane", "left", "right", "unit", "involution"):
        value = definitions["comparison_" + key]
        expected = CONTRACT["reference_value"](value.expr, gram, arrays)
        CONTRACT["assert_data"](value.data, expected)
        CONTRACT["assert_data"](ga.evaluate(value.expr, algebra=algebra, environment=environment).data, expected)
    left, right = definitions["comparison_left"], definitions["comparison_right"]
    assert left == -right and left != 0
    assert left.expr.operation_id == "left_contraction" and right.expr.operation_id == "right_contraction"
    unit, involution = definitions["comparison_unit"], definitions["comparison_involution"]
    assert definitions["comparison_shared_hat"] == unit.latex(content="expr") == involution.latex(content="expr")
    assert unit != involution and unit.expr != involution.expr
    assert definitions["comparison_functional_unit"] != definitions["comparison_functional_involution"]
    html = "\n".join(getattr(output, "text", "") for output in outputs)
    for text in (
        "Read the operation, not just the accent",
        "Unit normalization",
        "Grade involution",
        r"\rfloor",
        r"\lfloor",
    ):
        assert text in html
    for value in (left, right, unit, involution):
        assert value.latex(content="value") in html
