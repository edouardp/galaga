"""Historical ownership, import isolation, and independent notation gates."""

import runpy
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
CONTRACT_FILES = ("test_notation.py", "rendering/test_unit_fraction.py")
CONTRACT = runpy.run_path(str(TEST_ROOT / "test_notation.py"))
UNIT_CONTRACT = runpy.run_path(str(TEST_ROOT / "rendering/test_unit_fraction.py"))

# Every original class has an explicit live owner. Rule-field layout and
# mutable setters are historical evidence, not the v2 representation contract.
HISTORICAL_OWNERS = {
    "TestDefaultsExist": "test_default_notation_retains_reviewed_output_for_every_historical_node",
    "TestAccentDefaults": "test_default_notation_retains_reviewed_output_for_every_historical_node",
    "TestPostfixDefaults": "test_default_notation_retains_reviewed_output_for_every_historical_node",
    "TestPrefixDefaults": "test_default_notation_retains_reviewed_output_for_every_historical_node",
    "TestInfixDefaults": "test_default_notation_retains_reviewed_output_for_every_historical_node",
    "TestJuxtaposition": "test_default_notation_retains_reviewed_output_for_every_historical_node",
    "TestWrapDefaults": "test_default_notation_retains_reviewed_output_for_every_historical_node",
    "TestScalarOps": "test_default_notation_retains_reviewed_output_for_every_historical_node",
    "TestOverride": "test_target_local_reverse_overrides_take_priority_without_mutation",
    "TestCopy": "test_chained_overrides_and_input_containers_are_independently_immutable",
    "TestPresets": "test_reverse_presets_apply_to_actual_algebra_rendering_in_every_target",
    "TestFunctionStyle": "test_binary_function_override_uses_the_public_operation_id",
    "TestFunctionalPreset": "test_functional_notation_preserves_history_replay_and_canonical_operation_names",
    "TestFunctionalShortPreset": "test_short_functional_preset_has_explicit_unambiguous_spelling",
    "TestUnitFractionNotation": "test_unit_fraction_makes_named_teaching_equalities_distinct",
}


def test_historical_notation_archive_has_complete_provenance_and_live_ownership():
    archive = CONTRACT["ARCHIVE"]
    assert archive["schema_version"] == 1
    assert archive["source_commit"] == "2174c761ed0bac3cb2744775f5adcadece7dcc3f"
    assert len(archive["source_commit"]) == 40
    assert archive["captured_on"] == "2026-09-07"
    assert archive["python"] == "3.14.4" and archive["numpy"] == "2.5.2"
    assert archive["source_test"] == "packages/galaga/tests/test_notation.py"
    identifiers = archive["original_tests"]
    assert len(identifiers) == len(set(identifiers)) == 101
    assert {name.split(".")[0] for name in identifiers} == set(HISTORICAL_OWNERS)
    assert all(callable((CONTRACT | UNIT_CONTRACT)[name]) for name in HISTORICAL_OWNERS.values())
    assert len(archive["default_rules"]) == 47
    assert archive["original_case_count"] == len(identifiers) - 3 + 3 * len(archive["default_rules"]) == 239
    assert set(archive["default_rules"]) == set(CONTRACT["OLD_NODE_OPERATIONS"]) == set(CONTRACT["DEFAULT_RENDERINGS"])
    for targets in archive["default_rules"].values():
        assert set(targets) == {"ascii", "unicode", "latex"}
        assert all(isinstance(rule["kind"], str) and rule["kind"] for rule in targets.values())
    assert set(archive["functional_values"]) == set(CONTRACT["RECIPES"]) | {"log"}
    assert len(archive["functional_values"]) == 28
    assert set(CONTRACT["FUNCTIONAL_LATEX"]) == set(CONTRACT["RECIPES"])
    algebra, a, b, s = CONTRACT["_context"](ga.Notation.functional())
    assert archive["signature"] == [1, 1, 1]
    for name, value in zip(("a", "b", "s"), (a, b, s), strict=True):
        np.testing.assert_array_equal(value.data, archive["inputs"][name])
    for row in archive["functional_values"].values():
        coefficients = np.asarray(row["coefficients"])
        assert coefficients.shape == (algebra.dim,) and np.isfinite(coefficients).all()
        assert row["unicode"] and row["latex"]


def test_archived_unit_fraction_examples_still_have_public_numeric_and_teaching_counterparts():
    archive = CONTRACT["ARCHIVE"]["unit_fraction"]
    algebra, a, b, _ = CONTRACT["_context"](UNIT_CONTRACT["_notation"]())
    bivector = (a ^ b).named("B")
    for case_id, value in (("bivector", ga.unit(bivector)), ("sum", ga.unit(a + b))):
        CONTRACT["_assert_coefficients"](value.data, archive[case_id]["coefficients"])
    named = ga.unit(bivector).named(ga.Name.from_latex(r"\hat{B}"))
    assert named.display("full/latex") == archive["full_latex"]
    assert archive["sum"]["unicode"] == "(a + b)/‖a + b‖"
    assert archive["sum"]["latex"] == r"\frac{\left(a + b\right)}{\lVert a + b \rVert}"


def test_notation_contracts_execute_with_legacy_imports_blocked():
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
            raise AssertionError('notation contract imported legacy module: ' + fullname)
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


def test_notation_contracts_are_not_exempt_from_legacy_construction_guard():
    assert not (set(CONTRACT_FILES) & set(LEGACY_ORACLE_TESTS))


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
def test_numeric_archive_comparison_rejects_broadcasting_nonfinite_values_and_drift(actual, expected, message):
    with pytest.raises(AssertionError, match=message):
        CONTRACT["_assert_coefficients"](actual, expected)


@pytest.mark.parametrize("layer", ("numeric", "replay", "render"))
def test_notation_contract_detects_wrong_values_replay_or_rendering_independently(layer, monkeypatch):
    check = CONTRACT["test_functional_notation_preserves_history_replay_and_canonical_operation_names"]
    if layer == "numeric":
        original = ga.reverse
        monkeypatch.setattr(ga, "reverse", lambda value: -original(value))
    elif layer == "replay":
        monkeypatch.setitem(check.__globals__, "evaluate", lambda expression, *, algebra, environment: algebra.identity)
    else:
        monkeypatch.setattr(ga.Multivector, "display", lambda *args, **kwargs: "wrong")
    with pytest.raises(AssertionError):
        check("reverse", "latex")


def test_hestenes_contract_rejects_reintroduction_of_the_shadowing_latex_accent():
    def broken():
        return ga.Notation.hestenes().with_rule(
            "reverse", ga.Notation.default().rule("reverse", "latex"), target="latex"
        )

    with pytest.raises(AssertionError):
        CONTRACT["test_reverse_presets_apply_to_actual_algebra_rendering_in_every_target"](
            broken, ("adag", "a†", r"a^{\dagger}"), 2, "latex"
        )
