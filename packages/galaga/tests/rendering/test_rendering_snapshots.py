"""Exact public output and coefficient regressions across expression recipes."""

import json
from pathlib import Path

import numpy as np
import pytest
from tools.rendering_snapshots import CASES, PROFILES, RenderingContext

SNAPSHOTS = json.loads((Path(__file__).parents[2] / "tools/baselines/rendering-snapshots.json").read_text())


def test_every_snapshot_has_one_expression_recipe():
    keys = [case.key for case in CASES]
    assert len(keys) == len(set(keys))
    assert set(keys) == set(SNAPSHOTS)


@pytest.mark.parametrize("case", CASES, ids=lambda case: case.key)
def test_rendering_and_coefficients_match_snapshot(case):
    context = RenderingContext(PROFILES[case.profile])
    value = context.name_result(case.build(context), case.result_name)
    expected = SNAPSHOTS[case.key]
    actual = {
        "expression": value.latex(content="expr"),
        "value": value.latex(content="value"),
        "full": value.latex(),
        "rich": value._repr_latex_(),
    }
    for channel in case.channels:
        assert actual[channel] == expected[channel], channel
    coefficients = np.asarray(expected["coefficients"])
    assert value.data.shape == coefficients.shape
    assert np.isfinite(value.data).all() and np.isfinite(coefficients).all()
    np.testing.assert_allclose(value.data, coefficients, rtol=1e-12, atol=1e-12)
