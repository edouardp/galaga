"""Immutable blade conventions and local-name policies for Galaga 2."""

from __future__ import annotations

import keyword
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass
from types import MappingProxyType

from .names import Name

_SUBSCRIPT_TRANSLATION = str.maketrans("0123456789+-", "₀₁₂₃₄₅₆₇₈₉₊₋")


@dataclass(frozen=True, slots=True)
class BladeRef:
    """A signed reference to one canonical exterior-basis bitmask."""

    mask: int
    orientation: int = 1

    def __post_init__(self) -> None:
        if not isinstance(self.mask, int) or isinstance(self.mask, bool) or self.mask < 0:
            raise ValueError("a blade mask must be a non-negative integer")
        if self.orientation not in (-1, 1):
            raise ValueError("a blade orientation must be -1 or 1")


@dataclass(frozen=True, slots=True)
class BladeLabel:
    """The displayed name and signed reference for one stored blade."""

    name: Name
    ref: BladeRef

    def __post_init__(self) -> None:
        if not isinstance(self.name, Name):
            raise TypeError("a blade label name must be a Name")
        if not isinstance(self.ref, BladeRef):
            raise TypeError("a blade label reference must be a BladeRef")


@dataclass(frozen=True, slots=True, init=False)
class DisplayOrder:
    """A complete immutable permutation of exterior-basis masks."""

    dimension: int
    masks: tuple[int, ...]

    def __init__(self, dimension: int, masks: Iterable[int] | None = None) -> None:
        _validate_dimension(dimension)
        expected = tuple(range(1 << dimension))
        normalized = expected if masks is None else tuple(masks)
        if (
            any(not isinstance(mask, int) or isinstance(mask, bool) for mask in normalized)
            or len(normalized) != len(expected)
            or set(normalized) != set(expected)
        ):
            raise ValueError(
                f"display order for dimension {dimension} must contain every mask "
                f"from 0 to {(1 << dimension) - 1} exactly once"
            )
        object.__setattr__(self, "dimension", dimension)
        object.__setattr__(self, "masks", normalized)


@dataclass(frozen=True, slots=True, init=False)
class BladeConvention:
    """Complete names, signed aliases, and semantic roles for one dimension."""

    dimension: int
    labels: tuple[BladeLabel, ...]
    aliases: tuple[tuple[str, BladeRef], ...]
    roles: tuple[tuple[str, BladeRef], ...]

    def __init__(
        self,
        dimension: int,
        labels: Mapping[int, BladeLabel | Name | str] | Sequence[BladeLabel | Name | str],
        *,
        aliases: Mapping[str, BladeRef | int] | Iterable[tuple[str, BladeRef | int]] = (),
        roles: Mapping[str, BladeRef | int] | Iterable[tuple[str, BladeRef | int]] = (),
    ) -> None:
        _validate_dimension(dimension)
        count = 1 << dimension
        if isinstance(labels, Mapping):
            if set(labels) != set(range(count)):
                raise ValueError(f"blade convention must label every mask from 0 to {count - 1}")
            source_labels = tuple(labels[mask] for mask in range(count))
        else:
            source_labels = tuple(labels)
            if len(source_labels) != count:
                raise ValueError(f"blade convention for dimension {dimension} requires {count} labels")

        normalized_labels = tuple(_coerce_label(mask, label) for mask, label in enumerate(source_labels))
        canonical: dict[str, BladeRef] = {}
        for label in normalized_labels:
            for spelling in label.name.variants:
                previous = canonical.get(spelling)
                if previous is not None and previous != label.ref:
                    raise ValueError(f"ambiguous canonical blade spelling {spelling!r}")
                canonical[spelling] = label.ref

        normalized_aliases = _normalize_named_refs(
            aliases,
            dimension=dimension,
            kind="alias",
            reserved=canonical,
        )
        alias_lookup = dict(normalized_aliases)
        normalized_roles = _normalize_named_refs(
            roles,
            dimension=dimension,
            kind="role",
            reserved={**canonical, **alias_lookup},
        )

        object.__setattr__(self, "dimension", dimension)
        object.__setattr__(self, "labels", normalized_labels)
        object.__setattr__(self, "aliases", normalized_aliases)
        object.__setattr__(self, "roles", normalized_roles)

    def label(self, mask: int) -> BladeLabel:
        """Return the canonical displayed label for one stored mask."""
        self._validate_mask(mask)
        return self.labels[mask]

    def resolve(self, name: str) -> BladeRef:
        """Resolve a canonical spelling, alias, or semantic role."""
        lookup: dict[str, BladeRef] = {}
        for label in self.labels:
            lookup.update(dict.fromkeys(label.name.variants, label.ref))
        lookup.update(self.aliases)
        lookup.update(self.roles)
        try:
            return lookup[name]
        except KeyError as error:
            available = ", ".join(sorted(lookup))
            raise KeyError(f"unknown blade {name!r}; expected one of: {available}") from error

    @property
    def available_names(self) -> tuple[str, ...]:
        """All accepted canonical spellings, aliases, and roles."""
        names = {spelling for label in self.labels for spelling in label.name.variants}
        names.update(name for name, _ in self.aliases)
        names.update(name for name, _ in self.roles)
        return tuple(sorted(names))

    def _validate_mask(self, mask: int) -> None:
        if not isinstance(mask, int) or isinstance(mask, bool) or not 0 <= mask < (1 << self.dimension):
            raise ValueError(f"blade mask must be an integer from 0 to {(1 << self.dimension) - 1}")


@dataclass(frozen=True, slots=True, init=False)
class LocalNamePolicy:
    """An immutable mapping from Python identifiers to signed blades."""

    dimension: int
    entries: tuple[tuple[str, BladeRef], ...]

    def __init__(
        self,
        dimension: int,
        entries: Mapping[str, BladeRef | int] | Iterable[tuple[str, BladeRef | int]] = (),
    ) -> None:
        _validate_dimension(dimension)
        normalized = _normalize_named_refs(entries, dimension=dimension, kind="local name")
        for name, _ in normalized:
            if not name.isidentifier() or keyword.iskeyword(name):
                raise ValueError(f"local name {name!r} is not a valid Python identifier")
        object.__setattr__(self, "dimension", dimension)
        object.__setattr__(self, "entries", normalized)

    @classmethod
    def from_convention(cls, convention: BladeConvention) -> LocalNamePolicy:
        """Use Python-safe canonical ASCII names, excluding the scalar."""
        entries = []
        for mask, label in enumerate(convention.labels):
            name = label.name.ascii
            if mask and name.isidentifier() and not keyword.iskeyword(name):
                entries.append((name, label.ref))
        return cls(convention.dimension, entries)

    @property
    def mapping(self) -> Mapping[str, BladeRef]:
        """A read-only identifier-to-reference view."""
        return MappingProxyType(dict(self.entries))


def indexed_blade_convention(
    dimension: int,
    *,
    prefix: Name | str = "e",
    subscripts: Sequence[Name | str] | None = None,
    start: int = 1,
    style: str = "compact",
    overrides: Mapping[int, BladeLabel | Name | str] | None = None,
    aliases: Mapping[str, BladeRef | int] | Iterable[tuple[str, BladeRef | int]] = (),
    roles: Mapping[str, BladeRef | int] | Iterable[tuple[str, BladeRef | int]] = (),
) -> BladeConvention:
    """Generate a complete indexed convention with optional signed overrides."""
    _validate_dimension(dimension)
    if style not in {"compact", "juxtapose", "wedge"}:
        raise ValueError("blade style must be 'compact', 'juxtapose', or 'wedge'")
    normalized_prefix = _coerce_name(prefix)
    if subscripts is None:
        normalized_subscripts = tuple(_numeric_subscript(index) for index in range(start, start + dimension))
    else:
        if len(subscripts) != dimension:
            raise ValueError(f"expected {dimension} vector subscripts, got {len(subscripts)}")
        normalized_subscripts = tuple(_coerce_subscript(value) for value in subscripts)

    vector_names = tuple(
        Name(
            f"{normalized_prefix.ascii}{subscript.ascii}",
            f"{normalized_prefix.unicode}{subscript.unicode}",
            f"{normalized_prefix.latex}_{{{subscript.latex}}}",
        )
        for subscript in normalized_subscripts
    )
    labels: list[BladeLabel] = []
    for mask in range(1 << dimension):
        bits = tuple(index for index in range(dimension) if mask & (1 << index))
        if not bits:
            name = Name("1")
        elif len(bits) == 1:
            name = vector_names[bits[0]]
        elif style == "compact":
            ascii_subscripts = "".join(normalized_subscripts[index].ascii for index in bits)
            unicode_subscripts = "".join(normalized_subscripts[index].unicode or "" for index in bits)
            latex_subscripts = "".join(normalized_subscripts[index].latex or "" for index in bits)
            name = Name(
                f"{normalized_prefix.ascii}{ascii_subscripts}",
                f"{normalized_prefix.unicode}{unicode_subscripts}",
                f"{normalized_prefix.latex}_{{{latex_subscripts}}}",
            )
        else:
            separator = "^" if style == "wedge" else ""
            unicode_separator = "∧" if style == "wedge" else ""
            latex_separator = r" \wedge " if style == "wedge" else " "
            name = Name(
                separator.join(vector_names[index].ascii for index in bits),
                unicode_separator.join(vector_names[index].unicode or "" for index in bits),
                latex_separator.join(vector_names[index].latex or "" for index in bits),
            )
        labels.append(BladeLabel(name, BladeRef(mask)))

    for mask, override in (overrides or {}).items():
        if not isinstance(mask, int) or not 0 <= mask < len(labels):
            raise ValueError(f"blade override mask {mask!r} is outside the convention dimension")
        labels[mask] = _coerce_label(mask, override)
    return BladeConvention(dimension, labels, aliases=aliases, roles=roles)


def default_blade_convention(dimension: int) -> BladeConvention:
    """The default compact ``e1``, ``e2``, … convention."""
    return indexed_blade_convention(dimension)


def euclidean_blade_convention(dimension: int) -> BladeConvention:
    """A role-aware default Euclidean convention."""
    roles = {f"euclidean_{index + 1}": BladeRef(1 << index) for index in range(dimension)}
    return indexed_blade_convention(dimension, roles=roles)


def spacetime_blade_convention() -> BladeConvention:
    """The four-dimensional ``gamma0`` … ``gamma3`` spacetime convention."""
    roles = {
        "time": BladeRef(0b0001),
        "space_1": BladeRef(0b0010),
        "space_2": BladeRef(0b0100),
        "space_3": BladeRef(0b1000),
    }
    return indexed_blade_convention(
        4,
        prefix=Name("g", "γ", r"\gamma"),
        start=0,
        style="juxtapose",
        roles=roles,
    )


def pga_blade_convention(spatial_dim: int) -> BladeConvention:
    """Euclidean vectors followed by one actual null projective vector."""
    _validate_spatial_dimension(spatial_dim)
    subscripts: list[Name | str] = [str(index) for index in range(1, spatial_dim + 1)]
    subscripts.append(Name("0", "₀", "0"))
    roles = {f"euclidean_{index + 1}": BladeRef(1 << index) for index in range(spatial_dim)}
    roles["projective"] = BladeRef(1 << spatial_dim)
    return indexed_blade_convention(spatial_dim + 1, subscripts=subscripts, roles=roles)


def orthogonal_cga_blade_convention(spatial_dim: int) -> BladeConvention:
    """Euclidean vectors followed by actual orthogonal plus/minus vectors."""
    _validate_spatial_dimension(spatial_dim)
    subscripts: list[Name | str] = [str(index) for index in range(1, spatial_dim + 1)]
    subscripts.extend((Name("p", "₊", "+"), Name("m", "₋", "-")))
    roles = {f"euclidean_{index + 1}": BladeRef(1 << index) for index in range(spatial_dim)}
    roles.update(
        {
            "plus": BladeRef(1 << spatial_dim),
            "minus": BladeRef(1 << (spatial_dim + 1)),
        }
    )
    return indexed_blade_convention(spatial_dim + 2, subscripts=subscripts, roles=roles)


def null_cga_blade_convention(spatial_dim: int) -> BladeConvention:
    """Euclidean vectors followed by an actual native-null origin/infinity pair."""
    _validate_spatial_dimension(spatial_dim)
    subscripts: list[Name | str] = [str(index) for index in range(1, spatial_dim + 1)]
    subscripts.extend((Name("o", "ₒ", "o"), Name("inf", "∞", r"\infty")))
    roles = {f"euclidean_{index + 1}": BladeRef(1 << index) for index in range(spatial_dim)}
    roles.update(
        {
            "origin": BladeRef(1 << spatial_dim),
            "infinity": BladeRef(1 << (spatial_dim + 1)),
        }
    )
    return indexed_blade_convention(spatial_dim + 2, subscripts=subscripts, roles=roles)


def rga_blade_convention() -> BladeConvention:
    """Lengyel's signed four-dimensional RGA blade table."""
    overrides: dict[int, BladeLabel] = {}
    displayed = {
        0b0110: ("e23", (1, 2)),
        0b0101: ("e31", (2, 0)),
        0b0011: ("e12", (0, 1)),
        0b1001: ("e41", (3, 0)),
        0b1010: ("e42", (3, 1)),
        0b1100: ("e43", (3, 2)),
        0b1110: ("e423", (3, 1, 2)),
        0b1101: ("e431", (3, 2, 0)),
        0b1011: ("e412", (3, 0, 1)),
        0b0111: ("e321", (2, 1, 0)),
        0b1111: ("I", (0, 1, 2, 3)),
    }
    for mask, (ascii_name, indices) in displayed.items():
        subscript = ascii_name[1:] if ascii_name.startswith("e") else ascii_name
        if ascii_name == "I":
            name = Name("I", "𝟙", r"\text{𝟙}")
        else:
            name = Name(ascii_name, f"e{subscript.translate(_SUBSCRIPT_TRANSLATION)}", rf"\mathbf{{e}}_{{{subscript}}}")
        overrides[mask] = BladeLabel(name, BladeRef(mask, _orientation(indices)))

    aliases = {
        "e13": BladeRef(0b0101),
        "e14": BladeRef(0b1001),
        "e24": BladeRef(0b1010),
        "e34": BladeRef(0b1100),
        "e234": BladeRef(0b1110),
        "e134": BladeRef(0b1101),
        "e124": BladeRef(0b1011),
        "e123": BladeRef(0b0111),
    }
    roles = {
        "projective": BladeRef(0b1000),
        "pseudoscalar": BladeRef(0b1111),
    }
    return indexed_blade_convention(4, overrides=overrides, aliases=aliases, roles=roles)


def rga_display_order() -> DisplayOrder:
    """Lengyel's scalar, vector, bivector, trivector, pseudoscalar table order."""
    return DisplayOrder(
        4,
        (
            0b0000,
            0b0001,
            0b0010,
            0b0100,
            0b1000,
            0b0110,
            0b0101,
            0b0011,
            0b1001,
            0b1010,
            0b1100,
            0b1110,
            0b1101,
            0b1011,
            0b0111,
            0b1111,
        ),
    )


def complex_blade_convention() -> BladeConvention:
    """Complex numbers as the even subalgebra of Euclidean ``Cl(2, 0)``."""
    return indexed_blade_convention(
        2,
        overrides={0b11: BladeLabel(Name("i", "i", "i"), BladeRef(0b11))},
        aliases={"e12": BladeRef(0b11)},
        roles={"imaginary": BladeRef(0b11)},
    )


def quaternion_blade_convention() -> BladeConvention:
    """Quaternions as the bivector subalgebra of Euclidean ``Cl(3, 0)``."""
    return indexed_blade_convention(
        3,
        overrides={
            0b110: BladeLabel(Name("i", "i", "i"), BladeRef(0b110)),
            0b101: BladeLabel(Name("j", "j", "j"), BladeRef(0b101)),
            0b011: BladeLabel(Name("k", "k", "k"), BladeRef(0b011)),
        },
        aliases={
            "e23": BladeRef(0b110),
            "e13": BladeRef(0b101),
            "e12": BladeRef(0b011),
        },
        roles={
            "quaternion_i": BladeRef(0b110),
            "quaternion_j": BladeRef(0b101),
            "quaternion_k": BladeRef(0b011),
        },
    )


def quaternion_display_order() -> DisplayOrder:
    """Scalar, quaternion units, vectors, and pseudoscalar display order."""
    return DisplayOrder(3, (0b000, 0b110, 0b101, 0b011, 0b001, 0b010, 0b100, 0b111))


def exterior_blade_convention(dimension: int) -> BladeConvention:
    """Explicit wedge notation for a metric-free exterior algebra."""
    return indexed_blade_convention(dimension, style="wedge")


def _validate_dimension(dimension: int) -> None:
    if not isinstance(dimension, int) or isinstance(dimension, bool) or dimension < 0:
        raise ValueError("dimension must be a non-negative integer")


def _validate_spatial_dimension(spatial_dim: int) -> None:
    if not isinstance(spatial_dim, int) or isinstance(spatial_dim, bool) or spatial_dim < 1:
        raise ValueError("spatial_dim must be a positive integer")


def _coerce_name(value: Name | str) -> Name:
    return value if isinstance(value, Name) else Name(value)


def _coerce_subscript(value: Name | str) -> Name:
    if isinstance(value, Name):
        return value
    return Name(value, value.translate(_SUBSCRIPT_TRANSLATION), value)


def _numeric_subscript(value: int) -> Name:
    text = str(value)
    return Name(text, text.translate(_SUBSCRIPT_TRANSLATION), text)


def _coerce_ref(value: BladeRef | int) -> BladeRef:
    return value if isinstance(value, BladeRef) else BladeRef(value)


def _coerce_label(mask: int, value: BladeLabel | Name | str) -> BladeLabel:
    if isinstance(value, BladeLabel):
        if value.ref.mask != mask:
            raise ValueError(f"label for mask {mask} refers to mask {value.ref.mask}")
        return value
    return BladeLabel(_coerce_name(value), BladeRef(mask))


def _normalize_named_refs(
    values: Mapping[str, BladeRef | int] | Iterable[tuple[str, BladeRef | int]],
    *,
    dimension: int,
    kind: str,
    reserved: Mapping[str, BladeRef] | None = None,
) -> tuple[tuple[str, BladeRef], ...]:
    items = tuple(values.items()) if isinstance(values, Mapping) else tuple(values)
    normalized: list[tuple[str, BladeRef]] = []
    seen: set[str] = set()
    for name, raw_ref in items:
        if not isinstance(name, str) or not name:
            raise ValueError(f"{kind} names must be non-empty strings")
        if name in seen:
            raise ValueError(f"duplicate {kind} {name!r}")
        if reserved is not None and name in reserved:
            raise ValueError(f"{kind} {name!r} collides with an existing blade name")
        ref = _coerce_ref(raw_ref)
        if ref.mask >= (1 << dimension):
            raise ValueError(f"{kind} {name!r} refers to mask {ref.mask} outside dimension {dimension}")
        seen.add(name)
        normalized.append((name, ref))
    return tuple(normalized)


def _orientation(indices: Sequence[int]) -> int:
    inversions = sum(left > right for offset, left in enumerate(indices) for right in indices[offset + 1 :])
    return -1 if inversions % 2 else 1


__all__ = [
    "BladeConvention",
    "BladeLabel",
    "BladeRef",
    "DisplayOrder",
    "LocalNamePolicy",
    "complex_blade_convention",
    "default_blade_convention",
    "euclidean_blade_convention",
    "exterior_blade_convention",
    "indexed_blade_convention",
    "null_cga_blade_convention",
    "orthogonal_cga_blade_convention",
    "pga_blade_convention",
    "quaternion_blade_convention",
    "quaternion_display_order",
    "rga_blade_convention",
    "rga_display_order",
    "spacetime_blade_convention",
]
