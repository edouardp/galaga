"""Immutable results for geometric and operator classification."""

from dataclasses import dataclass
from typing import Literal

CausalKind = Literal["timelike", "null", "spacelike"]


@dataclass(frozen=True, slots=True)
class CSTAClassification:
    """Structure and causal interpretation of a homogeneous CSTA object.

    Carrier and tangent inertias are ``(positive, negative, zero)`` counts.
    ``causal`` describes a carrier for flats, tangents for curves, and radial
    intervals for full signed rounds. Surface tangent metrics are in properties.
    """

    kind: str
    grade: int | None
    representation: str | None
    simple: bool | None
    finite: bool | None
    causal: CausalKind | None = None
    properties: tuple[tuple[str, object], ...] = ()


@dataclass(frozen=True, slots=True)
class CSTAOperatorClassification:
    """Overlapping algebraic traits and a verified conformal action.

    ``nilpotency_index=None`` means no vanishing power was found within the
    requested bound. Transformation names describe the normalized twisted
    adjoint action; an arbitrary scalar multiple has the same action, though
    its idempotency and involution traits can differ.
    """

    traits: tuple[str, ...]
    transformation: str | None = None
    nilpotency_index: int | None = None
    properties: tuple[tuple[str, object], ...] = ()


__all__ = ["CSTAClassification", "CSTAOperatorClassification", "CausalKind"]
