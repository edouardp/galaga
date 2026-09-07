"""Replay archived STA vocabulary without loading its retired implementation."""

import json
from pathlib import Path

import numpy as np
import pytest

import galaga as ga

ARCHIVE = json.loads((Path(__file__).parents[2] / "tools/baselines/blade-convention-contracts-v1.json").read_text())
ASCII_CHANGES = {"iy0": "ig0", "iy1": "ig1", "iy2": "ig2", "iy3": "ig3"}


@pytest.mark.parametrize("table", ARCHIVE["sta_tables"])
@pytest.mark.parametrize("target", ("ascii", "unicode", "latex"))
def test_archived_sta_table_preserves_labels_signs_and_numeric_lookup(table, target):
    algebra = ga.Algebra(signature=table["signature"], product_backend="reference")
    convention = ga.spacetime_blade_convention(
        signature=algebra.basis_squares, sigmas=table["sigmas"], pseudovectors=table["pseudovectors"]
    )
    view = algebra.with_blades(convention)
    for old in table["labels"]:
        mask, sign = old["mask"], old["orientation"]
        expected = old[target]
        if target == "ascii":
            expected = ASCII_CHANGES.get(expected, expected)
        label = convention.label(mask)
        assert label.name.for_target(target) == expected
        assert label.ref == ga.BladeRef(mask, sign)
        data = np.zeros(16)
        data[mask] = sign
        actual = view.blade(expected)
        np.testing.assert_array_equal(actual.data, data)
        assert actual == sign * algebra.blade(mask)
        assert actual.display(f"value/{target}") == expected
        assert view.blade(mask).display(f"value/{target}") == ("" if sign == 1 else "-") + expected
