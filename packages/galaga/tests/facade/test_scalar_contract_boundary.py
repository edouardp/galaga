"""Archive ownership, corruption probes, and legacy-free scalar contracts."""

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
PUBLIC_FILES = ("test_scalar_helpers.py", "facade/test_scalar_contracts.py")
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILES[1]))
ARCHIVE = CONTRACT["ARCHIVE"]


def test_all_51_historical_method_identities_keep_source_evidence_and_live_owners():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "83a89f40db5503d32ba40fe40de4a47dbc302ce7"
    assert ARCHIVE["source_path"] == "packages/galaga/tests/test_scalar_helpers.py"
    assert ARCHIVE["captured_on"] == "2026-09-08"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["sha256"] == "4555c0b2b1f22b7000577a372af6ea495eda4b1e7e54d8166d3e8b19c9b3c5bc"
    assert hashlib.sha256(ARCHIVE["source"].encode()).hexdigest() == ARCHIVE["sha256"]
    assert ARCHIVE["case_count"] == len(ARCHIVE["test_ids"]) == len(set(ARCHIVE["test_ids"])) == 51
    assert ARCHIVE["test_ids"] == [
        f"{cls.name}.{node.name}"
        for cls in ast.parse(ARCHIVE["source"]).body
        if isinstance(cls, ast.ClassDef)
        for node in cls.body
        if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")
    ]
    assert set(ARCHIVE["test_ids"]) == {
        f"{name}.{method}"
        for name, cls in CONTRACT["SOURCE"].items()
        if name.startswith("Test") and inspect.isclass(cls)
        for method, function in inspect.getmembers(cls, inspect.isfunction)
        if method.startswith("test_")
    }


def test_archive_retains_values_and_intentionally_retired_rendering_modes():
    assert len(ARCHIVE["fractions"]) == 6
    assert [row["key"] for row in ARCHIVE["constants"]] == ["pi", "e", "tau", "sqrt2", "h", "hbar", "c"]
    assert set(ARCHIVE["compositions"]) == {"half_vector", "rotor", "hbar_c", "half_pi"}
    assert len(ARCHIVE["scientific_nodes"]) == 8 and len(ARCHIVE["coefficient_nodes"]) == 6
    assert len(set(ARCHIVE["scientific_styles"].values())) == 3
    assert ARCHIVE["zero_denominator_error"] == {"type": "ValueError", "message": "Denominator cannot be zero"}
    assert ARCHIVE["fractions"][0]["latex"] == r"\frac{1}{2}"
    assert ARCHIVE["constants"][3]["names"] == dict.fromkeys(("ascii", "unicode", "latex"))
    assert all(row["symbolic"] for row in ARCHIVE["fractions"] + ARCHIVE["constants"])


def test_scalar_contracts_are_not_exempt_from_legacy_construction_guards():
    assert not set(PUBLIC_FILES) & set(LEGACY_ORACLE_TESTS)


def test_scalar_contracts_execute_without_importing_legacy_modules():
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
            raise AssertionError('scalar contract imported legacy: ' + fullname)
sys.meta_path.insert(0, RejectLegacy())
import pytest
result = pytest.main(['--noconftest', '-q', *sys.argv[1:]])
assert result == 0
assert not any(forbidden(name) for name in sys.modules)
"""
    result = subprocess.run(
        [sys.executable, "-c", program, *(str(TEST_ROOT / name) for name in PUBLIC_FILES)],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.parametrize("data", ([1], [np.nan] * 8, [0] * 8))
def test_archived_constant_replay_rejects_malformed_nonfinite_and_erased_values(data):
    row = copy.deepcopy(ARCHIVE["constants"][4])
    row["data"] = data
    with pytest.raises(AssertionError):
        CONTRACT["test_archived_constants_keep_nonzero_values_and_explicit_names"](row, True, "latex")


@pytest.mark.parametrize("expected", (6.62607015e-34, 1.054571817e-34, 1.054571817e-34 * 299792458.0))
def test_small_value_assertion_rejects_zero_where_the_old_absolute_tolerance_did_not(expected):
    assert np.isclose(0, expected)  # Demonstrate the original vacuous check.
    with pytest.raises(AssertionError):
        CONTRACT["SOURCE"]["assert_scalar"](ga.Algebra(3).scalar(0), expected)


def test_rounding_oracle_rejects_an_emitter_that_erases_small_numbers(monkeypatch):
    monkeypatch.setitem(CONTRACT["EMITTERS"], "latex", lambda node: "0")
    with pytest.raises(AssertionError):
        CONTRACT["test_public_literals_preserve_scientific_magnitudes_without_legacy_string_padding"](
            ARCHIVE["scientific_nodes"][3], "latex"
        )


def test_archive_replay_rejects_a_named_constant_with_changed_magnitude(monkeypatch):
    original = CONTRACT["SOURCE"]["constant"]
    monkeypatch.setitem(CONTRACT["SOURCE"], "constant", lambda algebra, key: 10 * original(algebra, key))
    with pytest.raises(AssertionError):
        CONTRACT["test_archived_constants_keep_nonzero_values_and_explicit_names"](
            ARCHIVE["constants"][4], True, "ascii"
        )


@pytest.mark.skipif(sys.version_info < (3, 14), reason="teaching notebook uses Python 3.14 t-strings")
def test_teaching_notebook_executes_scalar_provenance_and_precision_examples():
    notebook = TEST_ROOT.parents[2] / "examples/galaga_v2/eager_values_and_expressions.py"
    app = runpy.run_path(str(notebook))["app"]
    outputs, definitions = app.run()
    small = definitions["small_scalar"]
    assert float(small) == 1.2e-34
    assert definitions["small_default_latex"] == "0"
    assert definitions["small_visible_latex"] == r"1.2 \times 10^{-34}"
    assert definitions["third_literal"].latex(content="expr") == "0.333333"
    assert definitions["third_named"].latex(content="expr") == r"\frac{a}{3}"
    np.testing.assert_array_equal(definitions["third_replayed"].data, definitions["third_named"].data)
    html = "\n".join(getattr(output, "text", "") for output in outputs)
    assert r"\frac{a}{3}" in html and r"1.2 \times 10^{-34}" in html
