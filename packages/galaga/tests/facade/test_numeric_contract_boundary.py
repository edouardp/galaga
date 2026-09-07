"""Regression gates for historical numeric evidence and the facade-only boundary."""

from __future__ import annotations

import runpy
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import galaga.core as core
import galaga.facade as facade

CONTRACT_PATH = Path(__file__).with_name("test_numeric_contract.py")
CONTRACT = runpy.run_path(str(CONTRACT_PATH))


@pytest.mark.parametrize("operation", ("geometric_product", "reverse", "norm2", "transwedge", "dual"))
@pytest.mark.parametrize("corrupted_layer", ("facade", "reference", "both"))
def test_numeric_oracles_reject_regressions_even_when_both_current_paths_agree(
    operation: str, corrupted_layer: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def wrong_result(*arguments):
        return arguments[0].algebra.scalar(0)

    if corrupted_layer in ("facade", "both"):
        monkeypatch.setattr(facade, operation, wrong_result)
    if corrupted_layer in ("reference", "both"):
        monkeypatch.setattr(core, operation, wrong_result)

    with pytest.raises(AssertionError, match="Not equal to tolerance"):
        CONTRACT["test_seeded_diagonal_contract_matches_history_and_core_reference"]("cl20-seed1729", operation)


@pytest.mark.parametrize("operation, alias", (("lie_bracket", "commutator"), ("jordan_product", "anticommutator")))
def test_correction_ledger_rejects_joint_half_scaling_of_aliases(
    operation: str, alias: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    def half_scaled(original):
        return lambda *arguments: 0.5 * original(*arguments)

    monkeypatch.setattr(facade, operation, half_scaled(getattr(facade, operation)))
    monkeypatch.setattr(facade, alias, half_scaled(getattr(facade, alias)))

    with pytest.raises(AssertionError, match="Arrays are not equal"):
        CONTRACT["TestV2CorrectionLedger"]().test_bracket_scaling_is_an_explicit_legacy_difference()


@pytest.mark.parametrize(
    "actual, expected, error",
    (
        (np.ones(1), np.ones(4), "shape changed"),
        (np.ones((1, 4)), np.ones(4), "shape changed"),
        (np.array([np.nan]), np.array([np.nan]), "nonfinite"),
        (np.array([np.inf]), np.ones(1), "nonfinite"),
        (np.ones(1), np.array([-np.inf]), "nonfinite"),
        (np.ones(1), np.array([np.nan]), "nonfinite"),
        (np.array([1.0001]), np.ones(1), "Not equal to tolerance"),
    ),
)
def test_sample_comparison_rejects_broadcasting_nonfinite_values_and_real_drift(actual, expected, error) -> None:
    with pytest.raises(AssertionError, match=error):
        CONTRACT["_assert_sample_coefficients"](actual, expected, label="intentional corruption")


@pytest.mark.parametrize("expected, delta", ((0.0, 1e-13), (1000.0, 5e-10)))
def test_sample_comparison_preserves_both_absolute_and_relative_tolerances(expected: float, delta: float) -> None:
    CONTRACT["_assert_sample_coefficients"](np.array([expected + delta]), np.array([expected]), label="roundoff")


def test_unknown_sample_operation_is_not_treated_as_an_arbitrary_unary_call() -> None:
    sample = CONTRACT["SAMPLES"]["cl20-seed1729"]
    algebra = facade.Algebra(signature=sample["signature"])

    with pytest.raises(ValueError, match="not in the historical numeric contract"):
        CONTRACT["_sample_arguments"](algebra, sample, "not_an_operation")


def test_numeric_contract_executes_without_legacy_imports() -> None:
    program = """
import importlib.abc
import sys

class RejectLegacy(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in {'galaga.algebra', 'galaga.expr', 'galaga.ops', 'galaga.symbolic_core', 'galaga.blade_convention', 'galaga.notation'} or fullname.startswith('galaga.legacy'):
            raise AssertionError('numeric contract imported legacy module: ' + fullname)

sys.meta_path.insert(0, RejectLegacy())
import pytest
# The ordinary parent conftest still imports v1 to poison constructors. Here
# the stronger import guard replaces it while the entire contract runs unchanged.
result = pytest.main(['--noconftest', '-q', sys.argv[1]])
assert result == 0
assert 'galaga.legacy' not in sys.modules and 'galaga.algebra' not in sys.modules
"""
    completed = subprocess.run(
        [sys.executable, "-c", program, str(CONTRACT_PATH)],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )

    assert completed.returncode == 0, completed.stdout + completed.stderr
