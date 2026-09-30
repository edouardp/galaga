"""Geometric 2D rendering for positive-definite oblique Gram metrics."""

from __future__ import annotations

from collections.abc import Sequence
from math import isfinite
from pathlib import Path

import anywidget
import numpy as np
import traitlets

from galaga import Algebra, Multivector

_ASSET_DIR = Path(__file__).parent / "static"


class Oblique2DPlot(anywidget.AnyWidget):
    """Draw vectors and bivectors in an orthonormal embedding of a 2D metric.

    The embedding is derived from the algebra's Gram matrix. Basis vectors,
    grade-1 multivectors and grade-2 parallelograms therefore preserve metric
    lengths, angles, and oriented area in the displayed Euclidean plane.
    """

    _esm = _ASSET_DIR / "oblique2d.js"
    _css = _ASSET_DIR / "oblique2d.css"

    scene = traitlets.List(trait=traitlets.Dict(), default_value=[]).tag(sync=True)
    view = traitlets.Dict(default_value={}).tag(sync=True)

    def __init__(
        self,
        algebra: Algebra,
        values: Sequence[Multivector] = (),
        *,
        labels: Sequence[str] | None = None,
        width: int = 640,
        height: int = 440,
        extent: float = 2.5,
        **kwargs: object,
    ) -> None:
        if not isinstance(algebra, Algebra):
            raise TypeError("algebra must be a galaga Algebra")
        if algebra.n != 2:
            raise ValueError("Oblique2DPlot requires a two-dimensional algebra")
        gram = np.asarray(algebra.gram, dtype=float)
        if np.linalg.eigvalsh(gram).min() <= 0:
            raise ValueError("Oblique2DPlot requires a positive-definite Gram matrix")
        if isinstance(width, bool) or not isinstance(width, int) or width < 240:
            raise ValueError("width must be an integer of at least 240")
        if isinstance(height, bool) or not isinstance(height, int) or height < 200:
            raise ValueError("height must be an integer of at least 200")
        if not isfinite(float(extent)) or extent <= 0:
            raise ValueError("extent must be a positive finite number")
        self._algebra = algebra
        # B.T @ B = G, so coefficient pairs map to true Euclidean coordinates.
        self._basis = np.linalg.cholesky(gram).T
        view = {"width": width, "height": height, "extent": float(extent)}
        super().__init__(scene=[], view=view, **kwargs)
        self.add_basis()
        self.add_values(values, labels=labels)

    @property
    def algebra(self) -> Algebra:
        """The algebra whose stored Gram matrix determines the drawing."""
        return self._algebra

    def add_basis(self) -> Oblique2DPlot:
        """Add the basis vectors at their metric-derived lengths and angle."""
        scene = [item for item in self.scene if item["kind"] != "basis"]
        for i in range(2):
            vector = self._basis[:, i]
            scene.append(
                {
                    "kind": "basis",
                    "label": f"e{i + 1}",
                    "x": float(vector[0]),
                    "y": float(vector[1]),
                    "color": ("#0072B2", "#D55E00")[i],
                }
            )
        self.scene = scene
        return self

    def add_values(
        self,
        values: Sequence[Multivector],
        *,
        labels: Sequence[str] | None = None,
    ) -> Oblique2DPlot:
        """Append grade-1 arrows or grade-2 oriented area parallelograms."""
        values = tuple(values)
        if labels is not None and len(labels) != len(values):
            raise ValueError("labels must contain one entry per value")
        scene = list(self.scene)
        for index, value in enumerate(values):
            if not isinstance(value, Multivector):
                raise TypeError("every value must be a galaga Multivector")
            if value.algebra is not self._algebra:
                raise ValueError("every value must belong to the plot's algebra")
            nonzero = np.flatnonzero(np.abs(value.data) > 1e-12)
            grades = {int(mask).bit_count() for mask in nonzero}
            label = labels[index] if labels is not None else (str(value.name) if value.name else f"v{index + 1}")
            if grades == {1}:
                coefficients = np.array([value.coefficient(1), value.coefficient(2)])
                point = self._basis @ coefficients
                scene.append(
                    {"kind": "vector", "label": label, "x": float(point[0]), "y": float(point[1]), "color": "#009E73"}
                )
            elif grades == {2} and abs(value.coefficient(3)) > 1e-12:
                # e1 ^ (c e2) gives the signed coefficient and orientation.
                first, second = self._basis[:, 0], self._basis[:, 1] * value.coefficient(3)
                scene.append(
                    {
                        "kind": "bivector",
                        "label": label,
                        "x1": float(first[0]),
                        "y1": float(first[1]),
                        "x2": float(second[0]),
                        "y2": float(second[1]),
                        "area": float(value.coefficient(3) * np.sqrt(np.linalg.det(self._algebra.gram))),
                        "color": "#7C3AED",
                    }
                )
            else:
                raise ValueError("values must be homogeneous grade-1 vectors or grade-2 bivectors")
        self.scene = scene
        return self


def oblique2d(algebra: Algebra, values: Sequence[Multivector] = (), **kwargs: object) -> Oblique2DPlot:
    """Create a two-dimensional oblique metric visualization."""
    return Oblique2DPlot(algebra, values, **kwargs)
