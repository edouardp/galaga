"""Concrete display and quaternion coefficient snapshots."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

import galaga as ga

TEST_ROOT = Path(__file__).parents[1]
ARCHIVE = json.loads((TEST_ROOT.parent / "tools/baselines/concrete-display-v1.json").read_text())


def _sample(sample_id: str):
    if sample_id in {"quaternion-positive", "quaternion-negative"}:
        algebra = ga.Algebra(config=ga.presets.quaternion())
        e1, e2, e3 = algebra.basis_vectors()
        i, j, k = e2 ^ e3, e1 ^ e3, e1 ^ e2
        return 1 + 2 * i + 3 * j + 4 * k if sample_id == "quaternion-positive" else 1 - 2 * i + 3 * j - 4 * k
    if sample_id == "sta-bivector":
        g0, g1, _, _ = ga.Algebra(config=ga.presets.sta()).basis_vectors()
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


@pytest.mark.parametrize("row", ARCHIVE["values"], ids=lambda row: row["id"])
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_concrete_display_matches_snapshots_with_explicit_grade_mask_order(row, target: str) -> None:
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
def test_quaternion_basis_values_use_presentation_enumeration(grade: int) -> None:
    algebra = ga.Algebra(config=ga.presets.quaternion())
    observed = ARCHIVE["quaternion_basis"][str(grade)]
    assert list(algebra.display_order) == ARCHIVE["orders"]["quaternion"]
    for row in observed:
        assert str(algebra.multivector(row["coefficients"])) == row["unicode"]
    positions = {mask: index for index, mask in enumerate(algebra.display_order)}
    ordered = sorted(observed, key=lambda row: positions[int(np.flatnonzero(row["coefficients"])[0])])
    _assert_coefficients(
        [blade.data for blade in algebra.basis_blades(grade)], [row["coefficients"] for row in ordered]
    )


@pytest.mark.parametrize("word", ("ij", "jk", "ki", "ii", "jj", "kk", "ijk"))
def test_quaternion_products_match_snapshots_and_independent_left_actions(word: str) -> None:
    algebra = ga.Algebra(config=ga.presets.quaternion())
    e1, e2, e3 = algebra.basis_vectors()
    units = dict(zip("ijk", (e2 ^ e3, e1 ^ e3, e1 ^ e2), strict=True))
    product, reference = algebra.identity, algebra.identity.data
    for letter in reversed(word):
        unit = units[letter]
        product = unit * product
        reference = algebra.numeric.left_action(unit.numeric) @ reference
    _assert_coefficients(product.data, ARCHIVE["quaternion_products"][word])
    _assert_coefficients(reference, ARCHIVE["quaternion_products"][word])
