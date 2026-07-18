"""Immutable presentation and complete algebra configuration models."""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from typing import cast

from .blades import BladeConvention, BladeRef, DisplayOrder, LocalNamePolicy


@dataclass(frozen=True, slots=True, init=False)
class Notation:
    """Immutable notation identity and operation-token overrides.

    Phase 6 will attach semantic render rules to these stable operation IDs;
    Phase 4 needs only an immutable, independently replaceable component.
    """

    id: str
    tokens: tuple[tuple[str, str], ...]

    def __init__(
        self,
        id: str = "default",
        tokens: Mapping[str, str] | Iterable[tuple[str, str]] = (),
    ) -> None:
        if not isinstance(id, str) or not id.strip():
            raise ValueError("notation id must be a non-empty string")
        items: tuple[tuple[str, str], ...]
        if isinstance(tokens, Mapping):
            items = tuple(cast(Mapping[str, str], tokens).items())
        else:
            items = tuple(tokens)
        seen: set[str] = set()
        normalized: list[tuple[str, str]] = []
        for operation_id, token in items:
            if not isinstance(operation_id, str) or not isinstance(token, str) or not operation_id or not token:
                raise ValueError("notation operation ids and tokens must be non-empty strings")
            if operation_id in seen:
                raise ValueError(f"duplicate notation token for {operation_id!r}")
            seen.add(operation_id)
            normalized.append((operation_id, token))
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "tokens", tuple(normalized))

    def token(self, operation_id: str, default: str | None = None) -> str | None:
        """Return an operation token without selecting mathematical semantics."""
        return dict(self.tokens).get(operation_id, default)


@dataclass(frozen=True, slots=True)
class DisplayPolicy:
    """Default rendering content and target, independent of notation."""

    content: str = "value"
    target: str = "unicode"

    def __post_init__(self) -> None:
        if self.content not in {"name", "expr", "value", "full"}:
            raise ValueError("display content must be 'name', 'expr', 'value', or 'full'")
        if self.target not in {"ascii", "unicode", "latex"}:
            raise ValueError("display target must be 'ascii', 'unicode', or 'latex'")


@dataclass(frozen=True, slots=True)
class PresentationConfig:
    """Independent immutable components used to present one algebra dimension."""

    blades: BladeConvention
    notation: Notation
    local_names: LocalNamePolicy
    display_order: DisplayOrder
    display: DisplayPolicy

    def __post_init__(self) -> None:
        expected = (
            ("blades", self.blades, BladeConvention),
            ("notation", self.notation, Notation),
            ("local_names", self.local_names, LocalNamePolicy),
            ("display_order", self.display_order, DisplayOrder),
            ("display", self.display, DisplayPolicy),
        )
        for name, value, expected_type in expected:
            if not isinstance(value, expected_type):
                raise TypeError(f"{name} must be a {expected_type.__name__}")
        dimensions = {
            self.blades.dimension,
            self.local_names.dimension,
            self.display_order.dimension,
        }
        if len(dimensions) != 1:
            raise ValueError("blade, local-name, and display-order dimensions must match")

    @property
    def dimension(self) -> int:
        return self.blades.dimension

    def with_blades(self, blades: BladeConvention) -> PresentationConfig:
        return replace(self, blades=blades)

    def with_notation(self, notation: Notation) -> PresentationConfig:
        return replace(self, notation=notation)

    def with_local_names(self, local_names: LocalNamePolicy) -> PresentationConfig:
        return replace(self, local_names=local_names)

    def with_display_order(self, display_order: DisplayOrder) -> PresentationConfig:
        return replace(self, display_order=display_order)

    def with_display(self, display: DisplayPolicy) -> PresentationConfig:
        return replace(self, display=display)


@dataclass(frozen=True, slots=True, init=False)
class AlgebraDefinition:
    """A validated immutable real symmetric Gram matrix and backend options."""

    gram: tuple[tuple[float, ...], ...]
    id: str | None
    product_backend: str

    def __init__(
        self,
        gram: Sequence[Sequence[int | float]],
        *,
        id: str | None = None,
        product_backend: str = "auto",
    ) -> None:
        normalized = tuple(tuple(float(value) for value in row) for row in gram)
        dimension = len(normalized)
        if any(len(row) != dimension for row in normalized):
            raise ValueError("an algebra definition Gram matrix must be square")
        if any(not math.isfinite(value) for row in normalized for value in row):
            raise ValueError("an algebra definition Gram matrix must contain finite values")
        for row in range(dimension):
            for column in range(row + 1, dimension):
                if not math.isclose(
                    normalized[row][column],
                    normalized[column][row],
                    rel_tol=1e-12,
                    abs_tol=1e-12,
                ):
                    raise ValueError("an algebra definition Gram matrix must be symmetric")
        if id is not None and (not isinstance(id, str) or not id.strip()):
            raise ValueError("an algebra definition id must be a non-empty string or None")
        if product_backend not in {"auto", "diagonal", "packed", "lazy", "reference"}:
            raise ValueError("product_backend must be 'auto', 'diagonal', 'packed', 'lazy', or 'reference'")
        object.__setattr__(self, "gram", normalized)
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "product_backend", product_backend)

    @classmethod
    def from_signature(
        cls,
        signature: Sequence[int | float],
        *,
        id: str | None = None,
        product_backend: str = "auto",
    ) -> AlgebraDefinition:
        normalized = tuple(float(value) for value in signature)
        if any(value not in (-1.0, 0.0, 1.0) for value in normalized):
            raise ValueError("signature values must be +1, -1, or 0")
        gram = tuple(
            tuple(value if row == column else 0.0 for column in range(len(normalized)))
            for row, value in enumerate(normalized)
        )
        return cls(gram, id=id, product_backend=product_backend)

    @classmethod
    def from_pqr(
        cls,
        p: int,
        q: int = 0,
        r: int = 0,
        *,
        id: str | None = None,
        product_backend: str = "auto",
    ) -> AlgebraDefinition:
        if any(not isinstance(value, int) or isinstance(value, bool) or value < 0 for value in (p, q, r)):
            raise ValueError("p, q, and r must be non-negative integers")
        return cls.from_signature(
            (0,) * r + (1,) * p + (-1,) * q,
            id=id,
            product_backend=product_backend,
        )

    @property
    def dimension(self) -> int:
        return len(self.gram)


@dataclass(frozen=True, slots=True, init=False)
class ModelConfig:
    """Optional semantic model identity and signed basis roles."""

    id: str
    roles: tuple[tuple[str, BladeRef], ...]

    def __init__(
        self,
        id: str,
        roles: Mapping[str, BladeRef] | Iterable[tuple[str, BladeRef]] = (),
    ) -> None:
        if not isinstance(id, str) or not id.strip():
            raise ValueError("model id must be a non-empty string")
        items: tuple[tuple[str, BladeRef], ...]
        if isinstance(roles, Mapping):
            items = tuple(cast(Mapping[str, BladeRef], roles).items())
        else:
            items = tuple(roles)
        if len({name for name, _ in items}) != len(items):
            raise ValueError("model role names must be unique")
        if any(not isinstance(name, str) or not name for name, _ in items):
            raise ValueError("model role names must be non-empty strings")
        if any(not isinstance(ref, BladeRef) for _, ref in items):
            raise TypeError("model role references must be BladeRef values")
        object.__setattr__(self, "id", id)
        object.__setattr__(self, "roles", items)


@dataclass(frozen=True, slots=True)
class AlgebraConfig:
    """A complete numeric definition, optional model, and presentation."""

    definition: AlgebraDefinition
    presentation: PresentationConfig
    model: ModelConfig | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.definition, AlgebraDefinition):
            raise TypeError("definition must be an AlgebraDefinition")
        if not isinstance(self.presentation, PresentationConfig):
            raise TypeError("presentation must be a PresentationConfig")
        if self.model is not None and not isinstance(self.model, ModelConfig):
            raise TypeError("model must be a ModelConfig or None")
        if self.definition.dimension != self.presentation.dimension:
            raise ValueError("algebra definition and presentation dimensions must match")
        if self.model is not None:
            limit = 1 << self.definition.dimension
            for name, ref in self.model.roles:
                if ref.mask >= limit:
                    raise ValueError(f"model role {name!r} refers to mask {ref.mask} outside the algebra dimension")

    def with_presentation(self, presentation: PresentationConfig) -> AlgebraConfig:
        return replace(self, presentation=presentation)


def default_presentation(dimension: int) -> PresentationConfig:
    """Construct independent default presentation components for a dimension."""
    from .blades import default_blade_convention

    blades = default_blade_convention(dimension)
    return PresentationConfig(
        blades=blades,
        notation=Notation(),
        local_names=LocalNamePolicy.from_convention(blades),
        display_order=DisplayOrder(dimension),
        display=DisplayPolicy(),
    )


__all__ = [
    "AlgebraConfig",
    "AlgebraDefinition",
    "DisplayPolicy",
    "ModelConfig",
    "Notation",
    "PresentationConfig",
    "default_presentation",
]
