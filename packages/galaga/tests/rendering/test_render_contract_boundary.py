"""Historical identity, isolation, and corruption gates for rendering migration."""

import ast
import copy
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
PUBLIC_FILES = ("test_render.py", "rendering/test_render_numeric_contract.py")
NUMERIC = runpy.run_path(str(TEST_ROOT / PUBLIC_FILES[1]))
CONTRACT, ARCHIVE = NUMERIC["CONTRACT"], NUMERIC["ARCHIVE"]


def test_every_historical_method_has_the_same_live_public_test_identity():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "370a4e10f4b00887637caa29a51adaa71f2719bc"
    assert ARCHIVE["captured_on"] == "2026-09-07"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_test"] == "packages/galaga/tests/test_render.py"
    assert ARCHIVE["signature"] == [1, 1, 1]
    tests = ARCHIVE["tests"]
    identifiers = [row["id"] for row in tests]
    assert len(identifiers) == len(set(identifiers)) == ARCHIVE["original_case_count"] == 141
    live = {
        f"{name}.{method}"
        for name, cls in CONTRACT.items()
        if name.startswith("Test") and inspect.isclass(cls)
        for method, function in inspect.getmembers(cls, inspect.isfunction)
        if method.startswith("test_")
    }
    assert live == set(identifiers)
    assert sum(len(row["observations"]) for row in tests) == 143
    for row in tests:
        node = ast.parse(row["source"]).body[0]
        assert isinstance(node, ast.FunctionDef) and node.name == row["id"].split(".")[1]
        assert any(isinstance(child, ast.Assert) for child in ast.walk(node))
        first = row["observations"][0]
        for observation in row["observations"]:
            assert observation["target"] in {"unicode", "latex"} and observation["rendered"]
            NUMERIC["assert_coefficients"](observation["coefficients"], first["coefficients"])
            assert observation["bindings"] == first["bindings"]
            for data in (observation["coefficients"], *observation["bindings"].values()):
                assert np.asarray(data).shape == (8,) and np.isfinite(data).all()


def test_archive_keeps_numeric_and_presentation_differences_explicit():
    rows = {row["id"]: row["observations"][0] for row in ARCHIVE["tests"]}
    assert rows["TestNeg.test_double_neg"]["rendered"] == "--a"
    assert rows["TestBracketOps.test_unit_sum"]["rendered"] == "(a + b)/‖a + b‖"
    assert rows["TestDiv.test_div_atoms"]["rendered"] == "a/b"
    assert rows["TestCommutators.test_lie_bracket"]["rendered"] == "½[a, b]"
    assert rows["TestCommutators.test_jordan_product"]["rendered"] == "½{a, b}"
    # Orthogonal vectors made the old Jordan case vacuous, unlike Lie.
    assert any(rows["TestCommutators.test_lie_bracket"]["coefficients"])
    assert not any(rows["TestCommutators.test_jordan_product"]["coefficients"])
    assert rows["TestLatex.test_sandwich_latex"]["bindings"]["R"] == [0, 0, 0, 1, 0, 0, 0, 0]


def test_rendering_suites_are_not_exempt_from_legacy_construction_guard():
    assert not set(PUBLIC_FILES) & set(LEGACY_ORACLE_TESTS)


def test_rendering_suites_run_with_legacy_imports_blocked():
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
            raise AssertionError('render contract imported legacy module: ' + fullname)
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
    "actual, expected, message",
    (
        ([1], [1, 1], "shape"),
        ([[1]], [1], "shape"),
        ([np.nan], [np.nan], "nonfinite"),
        ([1], [np.inf], "nonfinite"),
        ([np.inf], [1], "nonfinite"),
        ([1.1], [1], "Not equal"),
    ),
)
def test_numeric_comparison_rejects_shape_nonfinite_and_coefficient_corruption(actual, expected, message):
    with pytest.raises(AssertionError, match=message):
        NUMERIC["assert_coefficients"](actual, expected)


@pytest.mark.parametrize("case, operation", (("lie", "lie_bracket"), ("jordan", "jordan_product")))
def test_mixed_grade_contract_rejects_old_half_scaling(case, operation, monkeypatch):
    original = getattr(ga, operation)
    monkeypatch.setattr(ga, operation, lambda a, b: 0.5 * original(a, b))
    with pytest.raises(AssertionError):
        NUMERIC["test_mixed_grade_compositions_preserve_numeric_scope_and_all_targets"](
            NUMERIC["GRAMS"][1], case, 0, "ascii"
        )


@pytest.mark.parametrize("layer", ("replay", "render"))
def test_composition_contract_detects_replay_or_rendering_corruption(layer, monkeypatch):
    check = NUMERIC["test_mixed_grade_compositions_preserve_numeric_scope_and_all_targets"]
    if layer == "replay":
        monkeypatch.setitem(check.__globals__, "evaluate", lambda expression, *, algebra, environment: algebra.identity)
    else:
        monkeypatch.setattr(ga.Multivector, "display", lambda *args, **kwargs: "wrong")
    with pytest.raises(AssertionError):
        check(NUMERIC["GRAMS"][1], "division", 0, "ascii")


@pytest.mark.parametrize("field", ("bindings", "coefficients"))
def test_historical_numeric_contract_rejects_corrupted_archive_input_or_output(field, monkeypatch):
    row = copy.deepcopy(next(row for row in ARCHIVE["tests"] if row["id"] == "TestGp.test_two_atoms"))
    observation = row["observations"][0]
    data = observation[field]["a"] if field == "bindings" else observation[field]
    data[0] += 1
    with pytest.raises(AssertionError):
        NUMERIC["test_every_original_rendering_case_keeps_its_archived_numeric_contract"](row, monkeypatch)
