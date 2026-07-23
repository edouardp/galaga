"""Inspectable algebra presets built from immutable configuration components."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal, Protocol

from .blades import (
    BladeConvention,
    DisplayOrder,
    LocalNamePolicy,
    complex_blade_convention,
    euclidean_blade_convention,
    exterior_blade_convention,
    lengyel_cga_blade_convention,
    lengyel_cga_display_order,
    null_cga_blade_convention,
    orthogonal_cga_blade_convention,
    pga_blade_convention,
    quaternion_blade_convention,
    quaternion_display_order,
    rga_blade_convention,
    rga_display_order,
    spacetime_blade_convention,
)
from .presentation import (
    AlgebraConfig,
    AlgebraDefinition,
    DisplayPolicy,
    ModelConfig,
    Notation,
    PresentationConfig,
)


class Preset(Protocol):
    """Protocol implemented by deterministic complete algebra presets."""

    def build(self) -> AlgebraConfig:
        """Expand the preset into a complete immutable configuration."""
        ...


@dataclass(frozen=True, slots=True)
class EuclideanPreset:
    """Euclidean geometric algebra in ``spatial_dim`` dimensions."""

    spatial_dim: int = 3

    def __post_init__(self) -> None:
        _validate_spatial_dim(self.spatial_dim)

    def build(self) -> AlgebraConfig:
        blades = euclidean_blade_convention(self.spatial_dim)
        return AlgebraConfig(
            definition=AlgebraDefinition.from_signature(
                (1,) * self.spatial_dim,
                id=f"euclidean-{self.spatial_dim}d",
            ),
            presentation=_presentation(blades, notation=Notation("euclidean")),
            model=_model("euclidean", blades),
        )


@dataclass(frozen=True, slots=True)
class SpacetimePreset:
    """Four-dimensional spacetime algebra with a gamma basis."""

    signature: Literal["mostly-minus", "mostly-plus"] = "mostly-minus"

    def __post_init__(self) -> None:
        if self.signature not in {"mostly-minus", "mostly-plus"}:
            raise ValueError("spacetime signature must be 'mostly-minus' or 'mostly-plus'")

    def build(self) -> AlgebraConfig:
        blades = spacetime_blade_convention()
        squares = (1, -1, -1, -1) if self.signature == "mostly-minus" else (-1, 1, 1, 1)
        return AlgebraConfig(
            definition=AlgebraDefinition.from_signature(squares, id=f"spacetime-{self.signature}"),
            presentation=_presentation(blades, notation=Notation("spacetime")),
            model=_model("spacetime", blades),
        )


@dataclass(frozen=True, slots=True)
class PGAPreset:
    """Projective geometric algebra with a final native-null basis vector."""

    spatial_dim: int = 3

    def __post_init__(self) -> None:
        _validate_spatial_dim(self.spatial_dim)

    def build(self) -> AlgebraConfig:
        blades = pga_blade_convention(self.spatial_dim)
        return AlgebraConfig(
            definition=AlgebraDefinition.from_signature(
                (1,) * self.spatial_dim + (0,),
                id=f"pga-{self.spatial_dim}d",
            ),
            presentation=_presentation(blades, notation=Notation("pga")),
            model=_model("pga", blades),
        )


@dataclass(frozen=True, slots=True)
class CGAPreset:
    """Conformal geometric algebra in a native-null or orthogonal frame."""

    spatial_dim: int = 3
    frame: Literal["null", "orthogonal"] = "null"
    null_pair: float = -1.0

    def __post_init__(self) -> None:
        _validate_spatial_dim(self.spatial_dim)
        if self.frame not in {"null", "orthogonal"}:
            raise ValueError("CGA frame must be 'null' or 'orthogonal'")
        if not isinstance(self.null_pair, (int, float)) or isinstance(self.null_pair, bool):
            raise TypeError("null_pair must be a real number")
        if not math.isfinite(self.null_pair):
            raise ValueError("null_pair must be finite")
        if self.frame == "null" and self.null_pair == 0:
            raise ValueError("a native-null CGA pair must have a nonzero mutual product")
        if self.frame == "orthogonal" and self.null_pair != -1.0:
            raise ValueError("null_pair only applies to the native-null CGA frame")

    def build(self) -> AlgebraConfig:
        if self.frame == "null":
            blades = null_cga_blade_convention(self.spatial_dim)
            gram = _native_null_cga_gram(self.spatial_dim, self.null_pair)
        else:
            blades = orthogonal_cga_blade_convention(self.spatial_dim)
            gram = _diagonal_gram((1,) * self.spatial_dim + (1, -1))
        return AlgebraConfig(
            definition=AlgebraDefinition(
                gram,
                id=f"cga-{self.spatial_dim}d-{self.frame}",
            ),
            presentation=_presentation(blades, notation=Notation(f"cga-{self.frame}")),
            model=_model(f"cga-{self.frame}", blades),
        )


@dataclass(frozen=True, slots=True)
class LengyelRGAPreset:
    """Eric Lengyel's four-basis-vector RGA presentation of 3D PGA."""

    spatial_dim: int = 3

    def __post_init__(self) -> None:
        if self.spatial_dim != 3:
            raise ValueError("Lengyel RGA currently requires spatial_dim=3")

    def build(self) -> AlgebraConfig:
        blades = rga_blade_convention()
        return AlgebraConfig(
            definition=AlgebraDefinition.from_signature((1, 1, 1, 0), id="lengyel-rga-3d"),
            presentation=_presentation(
                blades,
                notation=Notation.lengyel(),
                display_order=rga_display_order(),
            ),
            model=_model("lengyel-rga", blades),
        )


@dataclass(frozen=True, slots=True)
class LengyelCGAPreset:
    """Eric Lengyel's native-null five-dimensional CGA presentation."""

    spatial_dim: int = 3

    def __post_init__(self) -> None:
        if self.spatial_dim != 3:
            raise ValueError("Lengyel CGA currently requires spatial_dim=3")

    def build(self) -> AlgebraConfig:
        blades = lengyel_cga_blade_convention()
        return AlgebraConfig(
            definition=AlgebraDefinition(
                _native_null_cga_gram(self.spatial_dim, -1.0),
                id="lengyel-cga-3d-null",
            ),
            presentation=_presentation(
                blades,
                notation=Notation.lengyel(),
                display_order=lengyel_cga_display_order(),
            ),
            model=_model("cga-null", blades),
        )


@dataclass(frozen=True, slots=True)
class ComplexPreset:
    """Complex numbers in the even subalgebra of Euclidean ``Cl(2, 0)``."""

    def build(self) -> AlgebraConfig:
        blades = complex_blade_convention()
        return AlgebraConfig(
            definition=AlgebraDefinition.from_signature((1, 1), id="complex-cl2"),
            presentation=_presentation(blades, notation=Notation("complex")),
            model=_model("complex", blades),
        )


@dataclass(frozen=True, slots=True)
class QuaternionPreset:
    """Quaternions in the bivector subalgebra of Euclidean ``Cl(3, 0)``."""

    def build(self) -> AlgebraConfig:
        blades = quaternion_blade_convention()
        return AlgebraConfig(
            definition=AlgebraDefinition.from_signature((1, 1, 1), id="quaternion-cl3"),
            presentation=_presentation(
                blades,
                notation=Notation("quaternion"),
                display_order=quaternion_display_order(),
            ),
            model=_model("quaternion", blades),
        )


@dataclass(frozen=True, slots=True)
class ExteriorPreset:
    """A metric-free exterior algebra on ``dimension`` generators."""

    dimension: int = 3

    def __post_init__(self) -> None:
        _validate_spatial_dim(self.dimension, name="dimension")

    def build(self) -> AlgebraConfig:
        blades = exterior_blade_convention(self.dimension)
        return AlgebraConfig(
            definition=AlgebraDefinition.from_signature((0,) * self.dimension, id=f"exterior-{self.dimension}d"),
            presentation=_presentation(blades, notation=Notation("exterior")),
            model=_model("exterior", blades),
        )


def p_euclidean(spatial_dim: int = 3) -> EuclideanPreset:
    """Return an inspectable Euclidean preset."""
    return EuclideanPreset(spatial_dim)


def p_sta(
    signature: Literal["mostly-minus", "mostly-plus"] = "mostly-minus",
) -> SpacetimePreset:
    """Return an inspectable spacetime preset."""
    return SpacetimePreset(signature)


def p_pga(spatial_dim: int = 3) -> PGAPreset:
    """Return an inspectable projective preset."""
    return PGAPreset(spatial_dim)


def p_cga(
    spatial_dim: int = 3,
    *,
    frame: Literal["null", "orthogonal"] = "null",
    null_pair: float = -1.0,
) -> CGAPreset:
    """Return an inspectable conformal preset."""
    return CGAPreset(spatial_dim, frame, null_pair)


def p_rga(spatial_dim: int = 3) -> LengyelRGAPreset:
    """Return an inspectable Lengyel RGA preset."""
    return LengyelRGAPreset(spatial_dim)


def p_lengyel_cga(spatial_dim: int = 3) -> LengyelCGAPreset:
    """Return Eric Lengyel's complete native-null CGA preset."""
    return LengyelCGAPreset(spatial_dim)


def p_complex() -> ComplexPreset:
    """Return an inspectable complex-number preset."""
    return ComplexPreset()


def p_quaternion() -> QuaternionPreset:
    """Return an inspectable quaternion preset."""
    return QuaternionPreset()


def p_exterior(dimension: int = 3) -> ExteriorPreset:
    """Return an inspectable metric-free exterior-algebra preset."""
    return ExteriorPreset(dimension)


def _presentation(
    blades: BladeConvention,
    *,
    notation: Notation,
    display_order: DisplayOrder | None = None,
) -> PresentationConfig:
    return PresentationConfig(
        blades=blades,
        notation=notation,
        local_names=LocalNamePolicy.from_convention(blades),
        display_order=display_order or DisplayOrder(blades.dimension),
        display=DisplayPolicy(),
    )


def _model(model_id: str, blades: BladeConvention) -> ModelConfig:
    return ModelConfig(model_id, dict(blades.roles))


def _diagonal_gram(signature: tuple[int, ...]) -> tuple[tuple[float, ...], ...]:
    return tuple(
        tuple(float(value) if row == column else 0.0 for column in range(len(signature)))
        for row, value in enumerate(signature)
    )


def _native_null_cga_gram(spatial_dim: int, null_pair: float) -> tuple[tuple[float, ...], ...]:
    dimension = spatial_dim + 2
    origin = spatial_dim
    infinity = spatial_dim + 1
    rows = [[0.0] * dimension for _ in range(dimension)]
    for index in range(spatial_dim):
        rows[index][index] = 1.0
    rows[origin][infinity] = null_pair
    rows[infinity][origin] = null_pair
    return tuple(tuple(row) for row in rows)


def _validate_spatial_dim(spatial_dim: int, *, name: str = "spatial_dim") -> None:
    if not isinstance(spatial_dim, int) or isinstance(spatial_dim, bool) or spatial_dim < 1:
        raise ValueError(f"{name} must be a positive integer")


__all__ = [
    "CGAPreset",
    "ComplexPreset",
    "EuclideanPreset",
    "ExteriorPreset",
    "LengyelCGAPreset",
    "LengyelRGAPreset",
    "PGAPreset",
    "Preset",
    "QuaternionPreset",
    "SpacetimePreset",
    "p_cga",
    "p_complex",
    "p_euclidean",
    "p_exterior",
    "p_lengyel_cga",
    "p_pga",
    "p_quaternion",
    "p_rga",
    "p_sta",
]
