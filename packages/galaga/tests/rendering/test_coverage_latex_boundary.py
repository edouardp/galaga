"""Archive ownership, corruption controls and the rendering teaching boundary."""

import copy
import runpy
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
PUBLIC_FILE = "rendering/test_coverage_latex_contracts.py"
CONTRACT = runpy.run_path(str(TEST_ROOT / PUBLIC_FILE))
ARCHIVE = CONTRACT["ARCHIVE"]


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
