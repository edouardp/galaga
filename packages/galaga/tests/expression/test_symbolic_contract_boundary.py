"""Fresh-process and corruption gates for public symbolic contracts."""

from __future__ import annotations

import runpy
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
CONTRACT_FILES = ("test_symbolic.py", "facade/test_unary_conveniences.py")


def test_symbolic_contracts_execute_without_legacy_imports() -> None:
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
            raise AssertionError('symbolic contract imported legacy module: ' + fullname)

sys.meta_path.insert(0, RejectLegacy())
import pytest
result = pytest.main(['--noconftest', '-q', *sys.argv[1:]])
assert result == 0
assert not any(forbidden(name) for name in sys.modules)
"""
    completed = subprocess.run(
        [sys.executable, "-c", program, *(str(TEST_ROOT / name) for name in CONTRACT_FILES)],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


def test_symbolic_contracts_are_not_exempt_from_the_legacy_construction_guard() -> None:
    assert not (set(CONTRACT_FILES) & set(LEGACY_ORACLE_TESTS))


CONTRACT = runpy.run_path(str(TEST_ROOT / "test_symbolic.py"))


def test_historical_symbolic_archive_retains_inputs_and_contract_ownership() -> None:
    archive = CONTRACT["ARCHIVE"]
    assert archive["schema_version"] == 1
    assert archive["source_commit"] == "ee9f69b6beeb3be121acbbf30ff27142b1f7b43f"
    assert archive["captured_on"] == "2026-09-07"
    assert archive["python"] == "3.14.4" and archive["numpy"] == "2.5.2"
    assert archive["source_test"] == "packages/galaga/tests/test_symbolic.py"
    assert len(archive["original_tests"]) == len(set(archive["original_tests"])) == 57
    assert {name.split(".")[0] for name in archive["original_tests"]} == {
        "TestSymRendering",
        "TestSymEval",
        "TestSymFallback",
        "TestCommutatorSymbolic",
    }
    assert archive["signature"] == [1, 1, 1]
    algebra, values = CONTRACT["_context"]()
    assert set(values) == set(archive["inputs"])
    for name, value in values.items():
        np.testing.assert_array_equal(value.data, archive["inputs"][name])
    assert algebra.n == 3
    rows = archive["values"]
    assert len(rows) == len({row["id"] for row in rows}) == 36
    assert set(CONTRACT["HISTORY"]) == set(CONTRACT["RECIPES"]) == set(CONTRACT["REVIEWED"])
    for row in rows:
        assert np.asarray(row["coefficients"]).shape == (8,)
        assert np.isfinite(row["coefficients"]).all()
        assert set(row["renderings"]) == {"ascii", "unicode", "latex"}
        assert all(isinstance(value, str) and value for value in row["renderings"].values())
        assert isinstance(row["node"], str) and row["node"]
    assert {(row["tracked"], row["operation"]) for row in archive["brackets"]} == {
        (tracked, name)
        for tracked in (False, True)
        for name in ("commutator", "anticommutator", "lie_bracket", "jordan_product")
    }
    assert len(archive["brackets"]) == 8
    assert [(row["kind"], row["before"], row["after"]) for row in archive["simplification"]] == [
        ("vectors", "JordanProduct", "Hi"),
        ("bivectors", "JordanProduct", "JordanProduct"),
    ]
    for row in archive["simplification"]:
        np.testing.assert_array_equal(row["before_coefficients"], row["after_coefficients"])


def test_historical_half_scaling_and_simplification_are_not_claimed_as_v2_parity() -> None:
    history = CONTRACT["HISTORY"]
    assert history["lie-bracket"]["renderings"]["unicode"] == "½[a, b]"
    assert history["lie-bracket"]["renderings"]["latex"] == r"\tfrac{1}{2}[a,\, b]"
    assert history["jordan-product"]["renderings"]["unicode"] == "½{a, b}"
    assert history["jordan-product"]["renderings"]["latex"] == r"\tfrac{1}{2}\{a,\, b\}"
    assert history["lie-bracket"]["coefficients"][3] == 1
    assert history["commutator"]["coefficients"][3] == 2


@pytest.mark.parametrize(
    "actual, expected, message",
    (
        ([1], [1, 1], "shape"),
        ([[1]], [1], "shape"),
        ([np.nan], [np.nan], "nonfinite"),
        ([np.inf], [1], "nonfinite"),
        ([1], [np.inf], "nonfinite"),
        ([1.01], [1], "Not equal"),
    ),
)
def test_archive_comparison_rejects_broadcasting_nonfinite_values_and_drift(actual, expected, message) -> None:
    with pytest.raises(AssertionError, match=message):
        CONTRACT["_assert_coefficients"](actual, expected)


def test_archive_comparison_allows_finite_roundoff() -> None:
    CONTRACT["_assert_coefficients"]([1e-13, 1 + 1e-13], [0, 1])


@pytest.mark.parametrize("layer", ("numeric", "replay", "render"))
def test_symbolic_contract_checks_each_layer_independently(layer, monkeypatch) -> None:
    check = CONTRACT["test_named_recipes_preserve_values_replay_and_reviewed_renderings"]
    if layer == "numeric":
        original = ga.reverse
        monkeypatch.setattr(ga, "reverse", lambda value: -original(value))
    elif layer == "replay":
        monkeypatch.setitem(check.__globals__, "evaluate", lambda expression, *, algebra, environment: algebra.identity)
    else:
        monkeypatch.setattr(ga.Multivector, "display", lambda *args, **kwargs: "wrong output")
    with pytest.raises(AssertionError):
        check("reverse", "latex")


@pytest.mark.parametrize("operation", ("lie_bracket", "jordan_product"))
def test_joint_half_scaling_cannot_pass_on_current_alias_agreement(operation, monkeypatch) -> None:
    peer = {"lie_bracket": "commutator", "jordan_product": "anticommutator"}[operation]

    def half_scaled(original):
        return lambda left, right: 0.5 * original(left, right)

    for name in (operation, peer):
        monkeypatch.setattr(ga, name, half_scaled(getattr(ga, name)))
    row = next(row for row in CONTRACT["ARCHIVE"]["brackets"] if row["operation"] == operation and row["tracked"])
    with pytest.raises(AssertionError, match="Not equal"):
        CONTRACT["test_nonzero_bracket_archive_distinguishes_unscaled_and_half_scaled_conventions"](row)


def test_unsafe_jordan_to_inner_rewrite_is_detected(monkeypatch) -> None:
    check = CONTRACT["test_simplification_does_not_assume_symbol_grades_or_replace_jordan_with_inner"]
    monkeypatch.setitem(
        check.__globals__,
        "simplify",
        lambda expression: ga.Call("hestenes_inner", expression.operands),
    )
    with pytest.raises(AssertionError):
        check("jordan_product", "vectors")
