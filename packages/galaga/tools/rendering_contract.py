"""Named algebra contexts for exact rendering unit tests."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType, ModuleType
from typing import Any, Literal

import galaga.algebra as legacy
import galaga.facade as facade
from galaga.blade_convention import b_pga, b_rga, b_sta
from galaga.notation import Notation as LegacyNotation

ImplementationId = Literal["legacy-v1", "core-facade-v2"]
LegacyFactory = Callable[[], Any]
FacadeFactory = Callable[[facade.DisplayPolicy], facade.Algebra]


@dataclass(frozen=True, slots=True)
class AlgebraProfile:
    """Paired construction and basis mapping for one mathematical algebra."""

    id: str
    description: str
    legacy_factory: LegacyFactory
    facade_factory: FacadeFactory
    legacy_vectors: tuple[str, ...]
    facade_vectors: tuple[str, ...]
    vector_order: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DisplayProfile:
    """One exact facade display policy and its legacy support boundary."""

    id: str
    description: str
    facade_policy: facade.DisplayPolicy
    supports_legacy: bool = False


@dataclass(frozen=True, slots=True)
class NamedAlgebra:
    """One named implementation + algebra + display configuration."""

    id: str
    implementation: ImplementationId
    algebra_profile: str
    display_profile: str


class ExpressionContext:
    """Cross-version vocabulary passed directly to a rendering test body."""

    __slots__ = ("_vector_order", "algebra", "api", "configuration", "vectors")

    def __init__(
        self,
        configuration: NamedAlgebra,
        algebra_profile: AlgebraProfile,
        display_profile: DisplayProfile,
    ) -> None:
        self.configuration = configuration
        self._vector_order = algebra_profile.vector_order
        if configuration.implementation == "legacy-v1":
            if not display_profile.supports_legacy:
                raise ValueError(f"display profile {display_profile.id!r} has no faithful legacy-v1 equivalent")
            self.api: ModuleType = legacy
            self.algebra = algebra_profile.legacy_factory()
            basis = self.algebra.basis_vectors(lazy=True)
            names = algebra_profile.legacy_vectors
        else:
            self.api = facade
            self.algebra = algebra_profile.facade_factory(display_profile.facade_policy)
            basis = self.algebra.basis_vectors(expr=True)
            names = algebra_profile.facade_vectors
        if len(names) != len(basis):
            raise ValueError(f"algebra profile {algebra_profile.id!r} has an invalid vector-name map")
        self.vectors = MappingProxyType(dict(zip(names, basis, strict=True)))

    @property
    def implementation(self) -> ImplementationId:
        return self.configuration.implementation

    def basis_vectors(self) -> tuple[Any, ...]:
        """Return tracked basis vectors in the profile's semantic order."""
        return tuple(self.vectors[name] for name in self._vector_order)

    def vector(self, name: str) -> Any:
        try:
            return self.vectors[name]
        except KeyError as error:
            raise KeyError(f"the configured algebra has no semantic basis vector {name!r}") from error

    def call(self, operation: str, *args: Any) -> Any:
        """Invoke one canonical operation through the selected public API."""
        legacy_names = {
            "geometric_product": "gp",
            "grade_involution": "involute",
            "outer_product": "op",
        }
        name = legacy_names.get(operation, operation) if self.implementation == "legacy-v1" else operation
        return getattr(self.api, name)(*args)

    def named(
        self,
        value: Any,
        name: str,
        *,
        latex: str | None = None,
        unicode: str | None = None,
    ) -> Any:
        """Name a result without mutating a shared input value."""
        if self.implementation == "legacy-v1":
            return value.copy_as(name, latex=latex or name, unicode=unicode or name, ascii=name)
        return value.named(name, latex=latex, unicode=unicode)

    def latex(self, value: Any) -> str:
        """Return the configured full LaTeX rendering for one returned value."""
        return self.render(value, target="latex", content="full")

    def render(self, value: Any, *, target: str, content: str) -> str:
        """Render one result through the selected implementation's public path."""
        if self.implementation == "legacy-v1":
            if content == "full" and target == "latex":
                return value.display().latex()
            if content == "expr" and target == "latex":
                return value.latex()
            if content == "expr" and target == "unicode":
                return str(value)
            raise ValueError(f"legacy-v1 has no faithful {content!r} {target!r} rendering path")
        return value.display(content=content, target=target)


def _legacy_cl2() -> legacy.Algebra:
    return legacy.Algebra((1, 1))


def _facade_cl2(display: facade.DisplayPolicy) -> facade.Algebra:
    return facade.Algebra((1, 1), display=display)


def _legacy_cl3() -> legacy.Algebra:
    return legacy.Algebra((1, 1, 1))


def _facade_cl3(display: facade.DisplayPolicy) -> facade.Algebra:
    return facade.Algebra((1, 1, 1), display=display)


def _legacy_sta() -> legacy.Algebra:
    return legacy.Algebra((1, -1, -1, -1), blades=b_sta())


def _facade_sta(display: facade.DisplayPolicy) -> facade.Algebra:
    return facade.Algebra(config=facade.p_sta(), display=display)


def _legacy_pga() -> legacy.Algebra:
    return legacy.Algebra(3, 0, 1, blades=b_pga())


def _facade_pga(display: facade.DisplayPolicy) -> facade.Algebra:
    return facade.Algebra(config=facade.p_pga(), display=display)


def _legacy_rga() -> legacy.Algebra:
    return legacy.Algebra(
        (1, 1, 1, 0),
        blades=b_rga(),
        notation=LegacyNotation.lengyel(),
    )


def _facade_rga(display: facade.DisplayPolicy) -> facade.Algebra:
    return facade.Algebra(config=facade.p_rga(), display=display)


ALGEBRA_PROFILES: Mapping[str, AlgebraProfile] = MappingProxyType(
    {
        "cl2": AlgebraProfile(
            "cl2",
            "Euclidean Cl(2,0) with the conventional basis",
            _legacy_cl2,
            _facade_cl2,
            ("e1", "e2"),
            ("e1", "e2"),
            ("e1", "e2"),
        ),
        "cl3": AlgebraProfile(
            "cl3",
            "Euclidean Cl(3,0) with the conventional basis",
            _legacy_cl3,
            _facade_cl3,
            ("e1", "e2", "e3"),
            ("e1", "e2", "e3"),
            ("e1", "e2", "e3"),
        ),
        "sta-mostly-minus": AlgebraProfile(
            "sta-mostly-minus",
            "Spacetime Cl(1,3) with the gamma presentation",
            _legacy_sta,
            _facade_sta,
            ("g0", "g1", "g2", "g3"),
            ("g0", "g1", "g2", "g3"),
            ("g0", "g1", "g2", "g3"),
        ),
        "pga3": AlgebraProfile(
            "pga3",
            "Three-dimensional PGA with semantic e0/e1/e2/e3 vector mapping",
            _legacy_pga,
            _facade_pga,
            ("e0", "e1", "e2", "e3"),
            ("e1", "e2", "e3", "e0"),
            ("e1", "e2", "e3", "e0"),
        ),
        "lengyel-rga": AlgebraProfile(
            "lengyel-rga",
            "Eric Lengyel's RGA signature, blade table, display order, and notation",
            _legacy_rga,
            _facade_rga,
            ("e1", "e2", "e3", "e4"),
            ("e1", "e2", "e3", "e4"),
            ("e1", "e2", "e3", "e4"),
        ),
    }
)


DISPLAY_PROFILES: Mapping[str, DisplayProfile] = MappingProxyType(
    {
        "full-default": DisplayProfile(
            "full-default",
            "Full teaching equality, 1e-12 zero cutoff, six significant digits",
            facade.DisplayPolicy(content="full"),
            supports_legacy=True,
        ),
        "full-precision-3": DisplayProfile(
            "full-precision-3",
            "Full teaching equality with three significant digits",
            facade.DisplayPolicy(content="full", coefficient_precision=3),
        ),
        "full-unfiltered-12": DisplayProfile(
            "full-unfiltered-12",
            "Full teaching equality with no approximate-zero cutoff and twelve significant digits",
            facade.DisplayPolicy(content="full", zero_tolerance=0, coefficient_precision=12),
        ),
    }
)


_CONFIGURATIONS = (
    *(
        NamedAlgebra(f"{implementation}/{algebra}/full-default", implementation, algebra, "full-default")
        for algebra in ALGEBRA_PROFILES
        for implementation in ("legacy-v1", "core-facade-v2")
    ),
    NamedAlgebra("core-facade-v2/cl3/full-precision-3", "core-facade-v2", "cl3", "full-precision-3"),
    NamedAlgebra("core-facade-v2/cl3/full-unfiltered-12", "core-facade-v2", "cl3", "full-unfiltered-12"),
)

NAMED_ALGEBRAS: Mapping[str, NamedAlgebra] = MappingProxyType(
    {configuration.id: configuration for configuration in _CONFIGURATIONS}
)


def context_for(name: str) -> ExpressionContext:
    """Look up one named configuration and return a fresh expression context."""
    try:
        configuration = NAMED_ALGEBRAS[name]
    except KeyError as error:
        raise KeyError(f"unknown configured algebra {name!r}") from error
    return ExpressionContext(
        configuration,
        ALGEBRA_PROFILES[configuration.algebra_profile],
        DISPLAY_PROFILES[configuration.display_profile],
    )


__all__ = [
    "ALGEBRA_PROFILES",
    "DISPLAY_PROFILES",
    "NAMED_ALGEBRAS",
    "AlgebraProfile",
    "DisplayProfile",
    "ExpressionContext",
    "ImplementationId",
    "NamedAlgebra",
    "context_for",
]
