"""Inspectable algebra presets built from immutable configuration components."""

from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal, Protocol

from .blades import (
    BladeConvention,
    DisplayOrder,
    LocalNamePolicy,
    complex_blade_convention,
    euclidean_blade_convention,
    exterior_blade_convention,
    indexed_blade_convention,
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
class BladePreset:
    """A blade-vocabulary recipe resolved against one algebra's Gram matrix."""

    kind: str
    dimension: int | None = None
    options: tuple[tuple[str, Any], ...] = ()

    def resolve(self, gram: Sequence[Sequence[float]]) -> BladeConvention:
        """Build a concrete convention after checking the target metric."""
        matrix = tuple(tuple(float(value) for value in row) for row in gram)
        dimension = len(matrix)
        if any(len(row) != dimension for row in matrix):
            raise ValueError("the algebra Gram matrix must be square")
        if self.dimension is not None and self.dimension != dimension:
            raise ValueError(f"blade preset {self.kind!r} requires dimension {self.dimension}, got {dimension}")
        options = dict(self.options)
        if self.kind == "indexed":
            return indexed_blade_convention(dimension, **options)
        if self.kind == "euclidean":
            return euclidean_blade_convention(dimension)
        if self.kind == "exterior":
            return exterior_blade_convention(dimension)
        if self.kind == "pga":
            return pga_blade_convention(dimension - 1)
        if self.kind == "cga":
            frame = options.get("frame", "null")
            _validate_cga_frame_metric(matrix, frame)
            return (
                null_cga_blade_convention(dimension - 2)
                if frame == "null"
                else orthogonal_cga_blade_convention(dimension - 2)
            )
        if self.kind == "rga":
            return rga_blade_convention()
        if self.kind == "complex":
            return complex_blade_convention()
        if self.kind == "quaternion":
            return quaternion_blade_convention()
        if self.kind == "sta":
            if dimension != 4:
                raise ValueError(f"blade preset 'sta' requires dimension 4, got {dimension}")
            if options.get("sigmas", False) or options.get("pseudovectors", False):
                signature = _unit_diagonal_signature(matrix)
                return spacetime_blade_convention(signature=signature, **options)
            return spacetime_blade_convention()
        raise ValueError(f"unknown blade preset kind {self.kind!r}")


class _BladePresets:
    """Namespace of independently selectable blade-vocabulary recipes."""

    def indexed(self, dimension: int, **options: Any) -> BladePreset:
        _validate_spatial_dim(dimension, name="dimension")
        return BladePreset("indexed", dimension, tuple(sorted(options.items())))

    def euclidean(self, dimension: int = 3) -> BladePreset:
        return BladePreset("euclidean", dimension)

    def sta(self, *, sigmas: bool = False, pseudovectors: bool = False) -> BladePreset:
        _require_bool("sigmas", sigmas)
        _require_bool("pseudovectors", pseudovectors)
        return BladePreset("sta", 4, (("sigmas", sigmas), ("pseudovectors", pseudovectors)))

    def pga(self, spatial_dim: int = 3) -> BladePreset:
        _validate_spatial_dim(spatial_dim)
        return BladePreset("pga", spatial_dim + 1)

    def cga(self, spatial_dim: int = 3, *, frame: Literal["null", "orthogonal"] = "null") -> BladePreset:
        _validate_spatial_dim(spatial_dim)
        if frame not in {"null", "orthogonal"}:
            raise ValueError("CGA frame must be 'null' or 'orthogonal'")
        return BladePreset("cga", spatial_dim + 2, (("frame", frame),))

    def rga(self) -> BladePreset:
        return BladePreset("rga", 4)

    def complex(self) -> BladePreset:
        return BladePreset("complex", 2)

    def quaternion(self) -> BladePreset:
        return BladePreset("quaternion", 3)

    def exterior(self, dimension: int = 3) -> BladePreset:
        _validate_spatial_dim(dimension, name="dimension")
        return BladePreset("exterior", dimension)


blades = _BladePresets()


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
    """Time-first spacetime algebra with optional metric-derived STA names."""

    signature: Literal["mostly-minus", "mostly-plus"] = "mostly-minus"
    sigmas: bool = False
    pseudovectors: bool = False

    def __post_init__(self) -> None:
        if self.signature not in {"mostly-minus", "mostly-plus"}:
            raise ValueError("spacetime signature must be 'mostly-minus' or 'mostly-plus'")
        if not isinstance(self.sigmas, bool) or not isinstance(self.pseudovectors, bool):
            raise TypeError("sigmas and pseudovectors must be booleans")

    def build(self) -> AlgebraConfig:
        squares = (1, -1, -1, -1) if self.signature == "mostly-minus" else (-1, 1, 1, 1)
        blades = spacetime_blade_convention(signature=squares, sigmas=self.sigmas, pseudovectors=self.pseudovectors)
        return AlgebraConfig(
            definition=AlgebraDefinition.from_signature(squares, id=f"spacetime-{self.signature}"),
            presentation=_presentation(blades, notation=Notation("spacetime")),
            model=_model("spacetime", blades),
        )


@dataclass(frozen=True, slots=True)
class PGAPreset:
    """PGA with ``spatial_dim`` Euclidean vectors and one final null vector."""

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
    """CGA with ``spatial_dim`` Euclidean vectors plus two conformal vectors."""

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
    """Quaternions in the even subalgebra of Euclidean ``Cl(3, 0)``."""

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
    *,
    sigmas: bool = False,
    pseudovectors: bool = False,
) -> SpacetimePreset:
    """Return a time-first spacetime preset, optionally naming sigma/dual products."""
    return SpacetimePreset(signature, sigmas=sigmas, pseudovectors=pseudovectors)


def p_pga(spatial_dim: int = 3) -> PGAPreset:
    """Return a ``spatial_dim + 1`` projective-algebra preset."""
    return PGAPreset(spatial_dim)


def p_cga(
    spatial_dim: int = 3,
    *,
    frame: Literal["null", "orthogonal"] = "null",
    null_pair: float = -1.0,
) -> CGAPreset:
    """Return a ``spatial_dim + 2`` conformal-algebra preset."""
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


# Short names are the canonical spelling for new code. The p_* functions stay
# available for compatibility with the a3 API.
euclidean = p_euclidean
sta = p_sta
pga = p_pga
cga = p_cga
rga = p_rga
lengyel_cga = p_lengyel_cga
complex = p_complex
quaternion = p_quaternion
exterior = p_exterior


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


def _require_bool(name: str, value: Any) -> None:
    if not isinstance(value, bool):
        raise TypeError(f"{name} must be a boolean")


def _unit_diagonal_signature(gram: tuple[tuple[float, ...], ...]) -> tuple[int, ...]:
    """Return an ordered STA signature, rejecting non-diagonal metrics."""
    for row, values in enumerate(gram):
        for column, value in enumerate(values):
            if row != column and value != 0.0:
                raise ValueError("metric-aware STA blade names require a diagonal Gram matrix")
    diagonal = tuple(gram[index][index] for index in range(len(gram)))
    if any(value not in (-1.0, 1.0) for value in diagonal):
        raise ValueError("metric-aware STA blade names require unit diagonal entries (+1 or -1)")
    return tuple(int(value) for value in diagonal)


def _validate_cga_frame_metric(gram: tuple[tuple[float, ...], ...], frame: str) -> None:
    """Reject a CGA naming frame that would misdescribe the target metric."""
    if frame not in {"null", "orthogonal"}:
        raise ValueError("CGA frame must be 'null' or 'orthogonal'")
    spatial_dim = len(gram) - 2
    if spatial_dim < 1:
        raise ValueError("CGA blade presets require at least one spatial dimension")
    for row in range(len(gram)):
        for column, value in enumerate(gram[row]):
            if row != column and value != 0.0 and {row, column} != {spatial_dim, spatial_dim + 1}:
                raise ValueError("blade preset CGA frame is incompatible with the target Gram matrix")
    diagonal = tuple(gram[index][index] for index in range(len(gram)))
    if any(value != 1.0 for value in diagonal[:spatial_dim]):
        raise ValueError("blade preset CGA frame requires unit Euclidean spatial entries")
    if frame == "null":
        if diagonal[-2:] != (0.0, 0.0) or gram[-2][-1] == 0.0:
            raise ValueError("blade preset CGA null frame requires a nonzero null-pair metric")
    elif diagonal[-2:] != (1.0, -1.0) or gram[-2][-1] != 0.0:
        raise ValueError("blade preset CGA orthogonal frame requires a (+1, -1) pair")


__all__ = [
    "BladePreset",
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
    "blades",
    "cga",
    "complex",
    "euclidean",
    "exterior",
    "lengyel_cga",
    "pga",
    "p_cga",
    "p_complex",
    "p_euclidean",
    "p_exterior",
    "p_lengyel_cga",
    "p_pga",
    "p_quaternion",
    "p_rga",
    "p_sta",
    "quaternion",
    "rga",
    "sta",
]
