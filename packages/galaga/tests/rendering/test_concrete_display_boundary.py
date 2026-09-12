"""Concrete display contracts retain history without a running v1 engine."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest
from tools.isolate_phase8_legacy_tests import LEGACY_ORACLE_TESTS

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
CONTRACT_FILES = ("test_display_order.py", "test_numeric_formatting.py")
ARCHIVE = json.loads((TEST_ROOT.parent / "tools/baselines/concrete-display-v1.json").read_text())


def _sample(sample_id: str):
    if sample_id in {"quaternion-positive", "quaternion-negative"}:
        algebra = ga.Algebra(config=ga.p_quaternion())
        e1, e2, e3 = algebra.basis_vectors()
        i, j, k = e2 ^ e3, e1 ^ e3, e1 ^ e2
        return 1 + 2 * i + 3 * j + 4 * k if sample_id == "quaternion-positive" else 1 - 2 * i + 3 * j - 4 * k
    if sample_id == "sta-bivector":
        g0, g1, _, _ = ga.Algebra(config=ga.p_sta()).basis_vectors()
        return g0 * g1
    algebra = ga.Algebra(3)
    e1, e2, e3 = algebra.basis_vectors()
    if sample_id == "vectors":
        return e1 + 2 * e2 + 3 * e3
    if sample_id == "mixed-default":
        return 1 + e1 + e2 + (e1 ^ e2) + e3
    if sample_id == "precision":
        return 3.14159 * e1 + 2.71828 * e2
    if sample_id == "scalar":
        return algebra.scalar(3.14159)
    if sample_id == "zero":
        return algebra.scalar(0)
    if sample_id == "mixed-signs":
        return 1 + 2 * e1 - 3 * (e1 ^ e2)
    if sample_id == "repr-mixed":
        return 3 + 2 * e1 - e2
    if sample_id == "half-turn":
        rotor = ga.exp(-(e1 ^ e2) * np.pi / 2)
        return rotor * (e1 + e2) * ~rotor
    raise ValueError(f"unknown historical display sample: {sample_id}")


def _assert_coefficients(actual, expected) -> None:
    actual, expected = np.asarray(actual), np.asarray(expected)
    assert actual.shape == expected.shape, "coefficient shape changed"
    assert np.isfinite(actual).all() and np.isfinite(expected).all(), "nonfinite coefficient"
    np.testing.assert_allclose(actual, expected, atol=1e-12, rtol=0)


def test_archive_retains_capture_provenance_and_all_display_observations() -> None:
    assert ARCHIVE["schema_version"] == 1
    assert ARCHIVE["source_commit"] == "c05d800d4df4b92b7141d6c990a190721cce84c1"
    assert ARCHIVE["captured_on"] == "2026-09-07"
    assert ARCHIVE["python"] == "3.14.4" and ARCHIVE["numpy"] == "2.5.2"
    assert ARCHIVE["source_tests"] == [f"packages/galaga/tests/{name}" for name in CONTRACT_FILES]
    ids = [row["id"] for row in ARCHIVE["values"]]
    assert len(ids) == len(set(ids)) == 11
    assert set(ids) == {
        "vectors",
        "mixed-default",
        "quaternion-positive",
        "quaternion-negative",
        "precision",
        "scalar",
        "zero",
        "mixed-signs",
        "repr-mixed",
        "sta-bivector",
        "half-turn",
    }
    assert sum(len(row["numeric_formats"]) for row in ARCHIVE["values"]) == 6
    for row in ARCHIVE["values"]:
        assert set(row["renderings"]) == {"ascii", "unicode", "latex", "repr"}
        assert all(isinstance(text, str) and text for text in row["renderings"].values())
        assert row["profile"] in ARCHIVE["profiles"]


@pytest.mark.parametrize("row", ARCHIVE["values"], ids=lambda row: row["id"])
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_concrete_display_matches_history_with_explicit_legacy_order(row, target: str) -> None:
    value = _sample(row["id"])
    assert list(value.algebra.signature) == ARCHIVE["profiles"][row["profile"]]["signature"]
    _assert_coefficients(value.data, row["coefficients"])
    presentation = value.algebra.presentation
    if row["id"] == "mixed-default":
        # Pin the historical grade-then-mask convention independently of defaults.
        masks = sorted(range(value.algebra.dim), key=lambda mask: (mask.bit_count(), mask))
        presentation = presentation.with_display_order(ga.DisplayOrder(value.algebra.n, masks))
        assert masks == ARCHIVE["orders"]["cl3-default"]
    assert value.display(f"value/{target}", presentation=presentation) == row["renderings"][target]


@pytest.mark.parametrize("grade", (0, 1, 2, 3))
def test_historical_quaternion_basis_values_survive_native_enumeration(grade: int) -> None:
    algebra = ga.Algebra(config=ga.p_quaternion())
    observed = ARCHIVE["quaternion_basis"][str(grade)]
    assert list(algebra.display_order) == ARCHIVE["orders"]["quaternion"]
    for row in observed:
        assert str(algebra.multivector(row["coefficients"])) == row["unicode"]
    ordered = sorted(observed, key=lambda row: int(np.flatnonzero(row["coefficients"])[0]))
    _assert_coefficients(
        [blade.data for blade in algebra.basis_blades(grade)], [row["coefficients"] for row in ordered]
    )


@pytest.mark.parametrize("word", ("ij", "jk", "ki", "ii", "jj", "kk", "ijk"))
def test_quaternion_products_match_history_and_independent_left_actions(word: str) -> None:
    algebra = ga.Algebra(config=ga.p_quaternion())
    e1, e2, e3 = algebra.basis_vectors()
    units = dict(zip("ijk", (e2 ^ e3, e1 ^ e3, e1 ^ e2), strict=True))
    product, reference = algebra.identity, algebra.identity.data
    for letter in reversed(word):
        unit = units[letter]
        product = unit * product
        reference = algebra.numeric.left_action(unit.numeric) @ reference
    _assert_coefficients(product.data, ARCHIVE["quaternion_products"][word])
    _assert_coefficients(reference, ARCHIVE["quaternion_products"][word])


def test_legacy_repr_and_fixed_decimal_examples_remain_explicit_history() -> None:
    rows = {row["id"]: row for row in ARCHIVE["values"]}
    assert rows["repr-mixed"]["renderings"]["repr"] == "3 + 2e₁ - e₂"
    assert repr(_sample("repr-mixed")) == "3 + 2e1 - e2"
    assert rows["precision"]["numeric_formats"] == {".3f": "3.142e₁ + 2.718e₂", ".1f": "3.1e₁ + 2.7e₂"}
    assert rows["zero"]["numeric_formats"] == {".3f": "0.000"}
    assert rows["scalar"]["numeric_formats"] == {".2f": "3.14"}
    assert rows["quaternion-positive"]["numeric_formats"] == {".1f": "1.0 + 2.0i + 3.0j + 4.0k"}
    assert rows["mixed-signs"]["numeric_formats"] == {".0f": "1 + 2e₁ - 3e₁₂"}
    assert [row["repr"] for row in ARCHIVE["algebra_reprs"]] == ["Cl(3,0)", "Cl(1,3)", "Cl(3,0,1)"]
    for row in ARCHIVE["algebra_reprs"]:
        algebra = ga.Algebra(signature=row["signature"])
        assert repr(algebra) != row["repr"]
        np.testing.assert_array_equal(algebra.gram, np.diag(row["signature"]))


@pytest.mark.parametrize(
    "actual, expected, message",
    (
        ([1], [1, 1], "shape"),
        ([np.nan], [np.nan], "nonfinite"),
        ([1], [np.inf], "nonfinite"),
        ([1.01], [1], "Not equal"),
    ),
)
def test_historical_numeric_checks_reject_broadcasting_nonfinite_data_and_drift(actual, expected, message) -> None:
    with pytest.raises(AssertionError, match=message):
        _assert_coefficients(actual, expected)


def test_wrong_rotor_cannot_pass_by_rendering_like_an_archived_sample(monkeypatch: pytest.MonkeyPatch) -> None:
    row = next(row for row in ARCHIVE["values"] if row["id"] == "half-turn")
    monkeypatch.setattr(ga, "exp", lambda value: value.algebra.identity)
    with pytest.raises(AssertionError, match="Not equal"):
        test_concrete_display_matches_history_with_explicit_legacy_order(row, "unicode")


def test_wrong_rendering_cannot_pass_on_numeric_agreement_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    row = next(row for row in ARCHIVE["values"] if row["id"] == "vectors")
    monkeypatch.setattr(ga.Multivector, "display", lambda *args, **kwargs: "wrong display")
    with pytest.raises(AssertionError):
        test_concrete_display_matches_history_with_explicit_legacy_order(row, "unicode")


@pytest.mark.parametrize("sample_id", ("unknown", "quaternion-unknown"))
def test_unknown_historical_sample_is_rejected(sample_id: str) -> None:
    with pytest.raises(ValueError, match="unknown historical display sample"):
        _sample(sample_id)


def test_concrete_display_contracts_execute_without_legacy_imports() -> None:
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
            raise AssertionError('concrete display contract imported legacy module: ' + fullname)

sys.meta_path.insert(0, RejectLegacy())
import pytest
# The ordinary parent conftest imports v1 to poison constructors. This fresh
# process replaces it with an import prohibition and runs both real suites.
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


def test_concrete_display_contracts_are_not_exempt_from_the_legacy_construction_guard() -> None:
    assert not (set(CONTRACT_FILES) & set(LEGACY_ORACLE_TESTS))
