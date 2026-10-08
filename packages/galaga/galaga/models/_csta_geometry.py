"""Carrier metrics and restricted quadrics for the CSTA object classifier."""

from dataclasses import dataclass

import numpy as np

from ..facade import Multivector, outer_product, scalar_product
from .classification import CausalKind, CSTAClassification


@dataclass(frozen=True, slots=True)
class _Section:
    anchor: np.ndarray
    directions: np.ndarray
    gram: np.ndarray
    finite: bool

    @property
    def induced(self) -> np.ndarray:
        return self.directions.T @ self.gram @ self.directions


def _section(value: Multivector, vectors: tuple[Multivector, ...], grade: int, atol: float) -> _Section:
    matrix = np.column_stack([outer_product(vector, value).data for vector in vectors])
    _, _, vh = np.linalg.svd(matrix, full_matrices=False)
    span = vh[-grade:].T
    weights = span[4]  # Ordered roles: four base vectors, origin, infinity.
    weight_squared = float(weights @ weights)
    gram = np.array([[float(scalar_product(a, b)) for b in vectors] for a in vectors])
    if weight_squared <= atol * atol:
        return _Section(np.zeros(6), span, gram, False)
    _, _, weight_vh = np.linalg.svd(weights.reshape(1, -1), full_matrices=True)
    return _Section(span @ weights / weight_squared, span @ weight_vh[1:].T, gram, True)


def _inertia(eigenvalues: np.ndarray, atol: float) -> tuple[int, int, int]:
    return (
        int(np.count_nonzero(eigenvalues > atol)),
        int(np.count_nonzero(eigenvalues < -atol)),
        int(np.count_nonzero(np.abs(eigenvalues) <= atol)),
    )


def _sign(value: float, atol: float) -> int:
    return 1 if value > atol else -1 if value < -atol else 0


def classify_flat(value: Multivector, vectors: tuple[Multivector, ...], grade: int, atol: float) -> CSTAClassification:
    section = _section(value, vectors, grade, atol)
    names = {2: "flat point", 3: "flat line", 4: "flat 2-plane", 5: "flat hyperplane"}
    if not section.finite:
        return CSTAClassification("ideal " + names[grade], grade, "direct", True, False)
    # Project weight-zero directions into spacetime. This removes infinity;
    # the remaining span is the physical affine carrier, not a coordinate mask.
    u, singular, _ = np.linalg.svd(section.directions[:4], full_matrices=False)
    basis = u[:, singular > atol]
    induced = basis.T @ section.gram[:4, :4] @ basis
    inertia = _inertia(np.linalg.eigvalsh(induced), atol)
    causal: CausalKind | None = None
    if basis.shape[1]:
        causal = "timelike" if inertia[0] else "null" if inertia[2] else "spacelike"
    return CSTAClassification(names[grade], grade, "direct", True, True, causal, (("carrier_inertia", inertia),))


def classify_round_section(
    value: Multivector, vectors: tuple[Multivector, ...], grade: int, atol: float
) -> CSTAClassification:
    section = _section(value, vectors, grade, atol)
    if not section.finite:
        return CSTAClassification(f"round {grade - 1}-object", grade, "direct", True, False)
    induced = section.induced
    eigenvalues, axes = np.linalg.eigh(induced)
    inertia = _inertia(eigenvalues, atol)
    properties: tuple[tuple[str, object], ...] = (("carrier_inertia", inertia),)
    linear = section.directions.T @ section.gram @ section.anchor
    radical = axes[:, np.abs(eigenvalues) <= atol]
    if inertia[2] and np.linalg.norm(radical.T @ linear) > atol:
        kind = "parabola" if grade == 3 else "paraboloid"
        tangent = (0, grade - 2, 0)
        return CSTAClassification(
            kind, grade, "direct", True, True, "spacelike", properties + (("tangent_inertia", tangent),)
        )

    # Complete the quadratic in its nondegenerate directions. With a radical,
    # a stationary set may exist but has no unique centre.
    regular = np.abs(eigenvalues) > atol
    inverse = (axes[:, regular] / eigenvalues[regular]) @ axes[:, regular].T
    center = section.anchor - section.directions @ inverse @ linear
    radius = float(-center @ section.gram @ center)
    sign = _sign(radius, atol)
    properties += (("signed_radius_squared", radius),)
    if not inertia[2]:
        properties += (("center", tuple(float(x) for x in center[:4])),)
    kind, causal, tangent = _round_name(grade, inertia, sign)
    if tangent is not None:
        properties += (("tangent_inertia", tangent),)
    return CSTAClassification(kind, grade, "direct", True, True, causal, properties)


def _round_name(
    grade: int, inertia: tuple[int, int, int], sign: int
) -> tuple[str, CausalKind | None, tuple[int, int, int] | None]:
    dimension = grade - 1
    positive, negative, _ = inertia
    if inertia == (0, dimension, 0):
        names = {
            -1: "circle" if grade == 3 else "sphere",
            0: "point circle" if grade == 3 else "point sphere",
            1: "imaginary circle" if grade == 3 else "imaginary sphere",
        }
        return names[sign], "spacelike" if sign < 0 else None, (0, dimension - 1, 0) if sign < 0 else None
    if inertia == (1, dimension - 1, 0):
        if grade == 3:
            if sign == 0:
                return "null line pair", "null", (0, 0, 1)
            if sign > 0:
                return "hyperbola", "spacelike", (positive - 1, negative, 0)
            return "hyperbola", "timelike", (positive, negative - 1, 0)
        names = {1: "two-sheet hyperboloid", -1: "one-sheet hyperboloid", 0: "cone"}
        tangent = {1: (positive - 1, negative, 0), -1: (positive, negative - 1, 0), 0: (positive - 1, negative - 1, 1)}[
            sign
        ]
        return names[sign], "spacelike" if sign > 0 else None, tangent
    if inertia == (0, dimension - 1, 1):
        if grade == 3:
            names = {-1: "parallel null line pair", 0: "double null line", 1: "imaginary null line pair"}
            return names[sign], "null" if sign <= 0 else None, (0, 0, 1) if sign <= 0 else None
        names = {-1: "null cylinder", 0: "null line", 1: "imaginary null cylinder"}
        tangents = {-1: (0, negative - 1, 1), 0: (0, 0, 1), 1: None}
        return names[sign], "null" if sign == 0 else None, tangents[sign]
    return f"round {grade - 1}-object", None, None
