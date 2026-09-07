"""Source-derived ownership and import isolation for LaTeX contracts."""

import ast
import json
import runpy
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
ARCHIVE = json.loads((TEST_ROOT.parent / "tools/baselines/latex-build-contracts-v1.json").read_text())
CONTRACT_FILES = ("test_latex_build.py", "rendering/test_latex_script_safety.py")
CONTRACT = runpy.run_path(str(TEST_ROOT / CONTRACT_FILES[0]))
HISTORICAL_OWNERS = {
    "TestAtoms": "test_expression_layout",
    "TestArithmetic": "test_expression_layout",
    "TestProducts": "test_expression_layout",
    "TestUnary": "test_unary_layout",
    "TestPostfixOnPostfix": "test_nested_operation_scripts_keep_semantic_parentheses",
    "TestPostfixOnSup": "test_script_on_exponential_braces_the_existing_power",
    "TestWrap": "test_expression_layout",
    "TestExp": "test_fractions_keep_builder_grouping_and_script_slash_disambiguation",
    "TestLog": "test_rotor_fraction_display_retains_metric_derived_values_and_replay",
    "TestCommutator": "test_expression_layout",
    "TestPrecedence": "test_expression_layout",
    "TestPrefixSpacing": "test_target_specific_custom_rules",
    "TestSuperscriptKind": "test_target_specific_custom_rules",
    "TestEndToEndLatex": "test_rotor_fraction_display_retains_metric_derived_values_and_replay",
    "TestAccentWidth": "test_accent_policy_is_consistently_wide",
    "TestPostfixOnSuperscriptName": "test_scripted_and_compound_name_layout",
    "TestPostfixOnCompoundName": "test_scripted_and_compound_name_layout",
    "TestSymProperties": "test_names_do_not_hide_bindings_or_change_the_value_expression",
    "TestFracNoParens": "test_explicit_fraction_layout_is_independent_of_expression_constant_folding",
    "TestSlashFracAmbiguity": "test_fractions_keep_builder_grouping_and_script_slash_disambiguation",
    "TestScientificNotation": "test_scientific_literals_and_coefficients",
}


def test_historical_archive_preserves_every_method_and_its_live_owner():
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "813eb6047a97753f207ea356164e104664df3c61"
    assert ARCHIVE["captured_on"] == "2026-09-07"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_test"] == "packages/galaga/tests/test_latex_build.py"
    tests = ARCHIVE["tests"]
    identifiers = [row["id"] for row in tests]
    assert len(identifiers) == len(set(identifiers)) == ARCHIVE["original_case_count"] == 112
    assert {name.split(".")[0] for name in identifiers} == set(HISTORICAL_OWNERS)
    assert all(callable(CONTRACT[owner]) for owner in HISTORICAL_OWNERS.values())
    for row in tests:
        node = ast.parse(row["source"]).body[0]
        assert isinstance(node, ast.FunctionDef) and node.name == row["id"].split(".")[1]
        assert any(isinstance(child, ast.Assert) for child in ast.walk(node))
        assert all(isinstance(value, str) and value for value in row["latex_observations"])


def test_archive_retains_intentional_layout_differences_and_retired_api_evidence():
    rows = {row["id"]: row for row in ARCHIVE["tests"]}
    assert rows["TestUnary.test_reverse"]["latex_observations"] == [r"\tilde{a}"]
    assert rows["TestProducts.test_lc"]["latex_observations"] == [r"a \;\lrcorner\; b"]
    assert rows["TestArithmetic.test_div"]["latex_observations"] == [r"\frac{a}{b}"]
    assert rows["TestFracNoParens.test_scalar_div_in_gp"]["latex_observations"] == [r"\frac{a}{2} b"]
    assert rows["TestPostfixOnSup.test_postfix_star_on_exp"]["latex_observations"] == [r"{e^{a}}^*"]
    assert rows["TestPostfixOnCompoundName.test_dual_of_wedge_name"]["latex_observations"] == [
        r"\left(a \wedge b\right)^*"
    ]
    # These custom-rule cases bypassed the old _latex helper; preserve their
    # complete source assertions instead of inventing captured observations.
    assert r"1.2 \cdot 10^{-7}" in rows["TestScientificNotation.test_scalar_cdot_style"]["source"]
    assert "1.2e-07" in rows["TestScientificNotation.test_scalar_raw_style"]["source"]
    assert "_inner_expr" in rows["TestSymProperties.test_inner_expr_preserved"]["source"]
    assert not rows["TestScientificNotation.test_scalar_cdot_style"]["latex_observations"]


def test_latex_contracts_are_not_exempt_from_legacy_construction_guard():
    assert not set(CONTRACT_FILES) & set(LEGACY_ORACLE_TESTS)


def test_latex_contracts_execute_with_all_legacy_imports_blocked():
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
            raise AssertionError('LaTeX contract imported legacy module: ' + fullname)
sys.meta_path.insert(0, RejectLegacy())
import pytest
result = pytest.main(['--noconftest', '-q', *sys.argv[1:]])
assert result == 0
assert not any(forbidden(name) for name in sys.modules)
"""
    completed = subprocess.run(
        [sys.executable, "-c", program, *(str(TEST_ROOT / path) for path in CONTRACT_FILES)],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


@pytest.mark.parametrize("layer", ("numeric", "replay", "render"))
def test_rotor_contract_detects_numeric_replay_and_display_regressions(layer, monkeypatch):
    check = CONTRACT["test_rotor_fraction_display_retains_metric_derived_values_and_replay"]
    if layer == "numeric":
        original = ga.exp
        monkeypatch.setattr(ga, "exp", lambda value: -original(value))
    elif layer == "replay":
        monkeypatch.setitem(check.__globals__, "evaluate", lambda expression, *, algebra, environment: algebra.identity)
    else:
        monkeypatch.setattr(ga.Multivector, "display", lambda *args, **kwargs: "wrong")
    with pytest.raises(AssertionError):
        check(((2, 0.5), (0.5, 1)), np.pi / 4)
