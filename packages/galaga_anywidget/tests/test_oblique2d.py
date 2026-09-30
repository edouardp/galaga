from __future__ import annotations

import numpy as np
import pytest

from galaga import Algebra
from galaga_anywidget import Oblique2DPlot, oblique2d


def test_oblique_widget_embeds_gram_basis_and_oriented_area() -> None:
    algebra = Algebra(gram=[[1.0, 0.5], [0.5, 1.0]])
    e1, e2 = algebra.basis_vectors()
    vector = (2 * e1 + e2).named("v")
    bivector = (2 * (e1 ^ e2)).named("B")
    plot = oblique2d(algebra, [vector, bivector])

    first, second = plot.scene[:2]
    assert first["kind"] == second["kind"] == "basis"
    assert np.isclose(first["x"] * second["x"] + first["y"] * second["y"], 0.5)
    assert plot.scene[2] == {
        "kind": "vector",
        "label": "v",
        "x": pytest.approx(2.5),
        "y": pytest.approx(np.sqrt(0.75)),
        "color": "#009E73",
    }
    assert plot.scene[3]["kind"] == "bivector"
    assert plot.scene[3]["area"] == pytest.approx(np.sqrt(3.0))
    cross = plot.scene[3]["x1"] * plot.scene[3]["y2"] - plot.scene[3]["y1"] * plot.scene[3]["x2"]
    assert cross == pytest.approx(plot.scene[3]["area"])


def test_oblique_widget_preserves_nonunit_basis_metric() -> None:
    gram = np.array([[4.0, 1.0], [1.0, 9.0]])
    plot = oblique2d(Algebra(gram=gram))
    basis = np.array([[item["x"], item["y"]] for item in plot.scene])
    assert [item["label"] for item in plot.scene] == ["e1", "e2"]
    assert np.allclose(basis @ basis.T, gram)


@pytest.mark.parametrize(
    ("algebra", "message"),
    [
        (Algebra(1), "two-dimensional"),
        (Algebra(gram=[[1.0, 2.0], [2.0, 1.0]]), "positive-definite"),
    ],
)
def test_oblique_widget_requires_a_two_dimensional_euclidean_metric(algebra, message) -> None:
    with pytest.raises(ValueError, match=message):
        Oblique2DPlot(algebra)


def test_oblique_widget_rejects_wrong_values() -> None:
    algebra = Algebra(gram=[[1.0, 0.2], [0.2, 1.0]])
    other = Algebra(2)
    with pytest.raises(ValueError, match="belong to the plot's algebra"):
        oblique2d(algebra, [other.basis_vectors()[0]])
    with pytest.raises(ValueError, match="homogeneous grade-1 vectors or grade-2 bivectors"):
        oblique2d(algebra, [algebra.scalar(1)])
