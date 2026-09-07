"""Fresh-process gates for the migrated expression and grouping contracts."""

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
CONTRACT_FILES = ("test_precedence.py", "test_numeric_function_expressions.py")
CONTRACTS = {name: runpy.run_path(str(TEST_ROOT / name)) for name in CONTRACT_FILES}


def test_expression_contracts_execute_without_legacy_imports() -> None:
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
            raise AssertionError('expression contract imported legacy module: ' + fullname)

sys.meta_path.insert(0, RejectLegacy())
import pytest
# Replace the parent conftest's old-constructor guard with an import ban.
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


def test_expression_contracts_are_not_exempt_from_the_construction_guard() -> None:
    assert not (set(CONTRACT_FILES) & set(LEGACY_ORACLE_TESTS))


def test_archive_retains_all_original_inputs_values_and_display_observations() -> None:
    archive = CONTRACTS["test_precedence.py"]["ARCHIVE"]
    assert archive == CONTRACTS["test_numeric_function_expressions.py"]["ARCHIVE"]
    assert archive["schema_version"] == 1
    assert archive["source_commit"] == "f20a082ea077073285b73b23ac46543d57128300"
    assert archive["captured_on"] == "2026-09-07"
    assert archive["python"] == "3.14.4" and archive["numpy"] == "2.5.2"
    assert archive["source_tests"] == [f"packages/galaga/tests/{name}" for name in CONTRACT_FILES]
    assert archive["inputs"] == {
        "signature": [1, 1, 1],
        "vectors": {"a": 1, "b": 2, "c": 4, "v": 1},
        "scalars": {"s": 9, "m": 3, "p": 4},
        "rotor_angle": 0.7,
    }
    rows = archive["observations"]
    ids = [row["id"] for row in rows]
    recipes = CONTRACTS["test_precedence.py"]["RECIPES"]
    assert set(recipes) == set(CONTRACTS["test_precedence.py"]["RENDERINGS"])
    assert len(ids) == len(set(ids)) == 29
    assert set(ids) == set(recipes) | {"rotor-root", "scalar-root", "energy", "norm2"}
    for row in rows:
        assert np.asarray(row["coefficients"]).shape == (8,)
        assert np.isfinite(row["coefficients"]).all()
        assert set(row["renderings"]) == {"ascii", "unicode", "latex"}
        assert all(isinstance(text, str) and text for text in row["renderings"].values())
        assert row["source"] and row["full_latex"]

    history = CONTRACTS["test_numeric_function_expressions.py"]["HISTORY"]
    assert history["scalar-root"]["renderings"]["latex"] == r"\sqrt{s}"
    assert history["norm2"]["renderings"]["unicode"] == "‖v‖²"
    assert history["norm2"]["renderings"]["latex"] == r"\lVert v \rVert^{2}"
    assert history["rotor-root"]["renderings"]["latex"] == r"\sqrt{e^{0.7 e_{1} \wedge e_{2}}}"
    # A name used to replace expression-only output; full display retained it.
    assert history["energy"]["renderings"] == dict.fromkeys(("ascii", "unicode", "latex"), "E")
    assert history["energy"]["full_latex"] == r"E \quad = \quad \sqrt{m^2 + p^2} \quad = \quad 5"


def test_grouping_archive_changes_are_limited_to_reviewed_spelling_choices() -> None:
    contract = CONTRACTS["test_precedence.py"]
    changed = {
        (case_id, target)
        for case_id, expected in contract["RENDERINGS"].items()
        for target, rendering in zip(("ascii", "unicode", "latex"), expected, strict=True)
        if rendering != contract["HISTORY"][case_id]["renderings"][target]
    }
    # V2 has real ASCII fallbacks, combining Unicode accents, target-specific
    # stars, conservative negated-product grouping, and spaces around infixes.
    ascii_only = {"inverse-sum", "inverse-product", "inverse-name", "squared-product", "squared-name"}
    unicode_only = {"reverse-sum", "reverse-product", "reverse-left", "reverse-right", "sum-sandwich"}
    ascii_unicode = {
        "involute-sum",
        "conjugate-sum",
        "dual-sum",
        "dual-product",
        "dual-name",
        "divide-sum",
        "scale-inside-wedge",
        "scale-outside-wedge",
        "unit-sum",
    }
    assert changed == (
        {(case_id, "ascii") for case_id in ascii_only}
        | {(case_id, "unicode") for case_id in unicode_only}
        | {(case_id, target) for case_id in ascii_unicode for target in ("ascii", "unicode")}
        | {("reverse-name", target) for target in ("ascii", "latex")}
        | {
            (case_id, target)
            for case_id in ("negate-product", "double-reverse")
            for target in ("ascii", "unicode", "latex")
        }
    )


@pytest.mark.parametrize("filename", CONTRACT_FILES)
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
def test_numeric_comparisons_reject_broadcasting_nonfinite_data_and_drift(filename, actual, expected, message) -> None:
    with pytest.raises(AssertionError, match=message):
        CONTRACTS[filename]["_assert_coefficients"](actual, expected)


@pytest.mark.parametrize("filename", CONTRACT_FILES)
def test_numeric_comparisons_allow_finite_roundoff(filename) -> None:
    CONTRACTS[filename]["_assert_coefficients"]([1e-13, 1 + 1e-13], [0, 1])


def test_correct_expression_cannot_hide_an_incorrect_root(monkeypatch: pytest.MonkeyPatch) -> None:
    original = ga.sqrt

    def wrong_root(value, **kwargs):
        correct = original(value, **kwargs)
        return value.algebra.identity.with_expr(correct.expr)

    monkeypatch.setattr(ga, "sqrt", wrong_root)
    with pytest.raises(AssertionError, match="Not equal"):
        CONTRACTS["test_numeric_function_expressions.py"][
            "test_sqrt_of_expression_rotor_preserves_provenance_and_value"
        ]()


@pytest.mark.parametrize("layer", ("eager", "replay", "render"))
def test_grouping_contract_checks_values_replay_and_rendering_independently(
    layer, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = CONTRACTS["test_precedence.py"]
    if layer == "eager":
        original = ga.reverse
        monkeypatch.setattr(ga, "reverse", lambda value: -original(value))
    elif layer == "replay":
        check = contract["test_grouping_preserves_historical_value_replay_and_reviewed_rendering"]
        monkeypatch.setitem(check.__globals__, "evaluate", lambda expression, *, algebra, environment: algebra.identity)
    else:
        monkeypatch.setattr(ga.Multivector, "display", lambda *args, **kwargs: "incorrect grouping")
    with pytest.raises(AssertionError):
        contract["test_grouping_preserves_historical_value_replay_and_reviewed_rendering"]("reverse-product", "latex")
