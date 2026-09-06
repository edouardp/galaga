"""Named Galaga 2 algebra contexts for exact rendering unit tests."""

from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from types import MappingProxyType
from typing import Any, Literal

import galaga.facade as facade

ImplementationId = Literal["core-facade-v2"]
FacadeFactory = Callable[[facade.DisplayPolicy], facade.Algebra]


@dataclass(frozen=True, slots=True)
class AlgebraProfile:
    """Public facade construction and semantic basis mapping for one algebra."""

    id: str
    description: str
    facade_factory: FacadeFactory
    facade_vectors: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DisplayProfile:
    """One exact facade display policy."""

    id: str
    description: str
    facade_policy: facade.DisplayPolicy


@dataclass(frozen=True, slots=True)
class NamedAlgebra:
    """One named implementation + algebra + display configuration."""

    id: str
    implementation: ImplementationId
    algebra_profile: str
    display_profile: str


class ExpressionContext:
    """Public facade vocabulary passed directly to a rendering test body."""

    __slots__ = ("algebra", "api", "configuration", "vectors")

    def __init__(
        self,
        configuration: NamedAlgebra,
        algebra_profile: AlgebraProfile,
        display_profile: DisplayProfile,
    ) -> None:
        if configuration.implementation != "core-facade-v2":
            raise ValueError("configured rendering executes only core-facade-v2; v1 observations are archived")
        self.configuration = configuration
        self.api = facade
        # Keep the recipe adapter's existing dynamic vocabulary: public numeric
        # operator annotations also include NotImplemented dispatch results.
        # Runtime boundary tests pin the concrete facade types independently.
        self.algebra: Any = algebra_profile.facade_factory(display_profile.facade_policy)
        basis = self.algebra.basis_vectors(expr=True)
        names = algebra_profile.facade_vectors
        if len(names) != len(basis):
            raise ValueError(f"algebra profile {algebra_profile.id!r} has an invalid vector-name map")
        if len(set(names)) != len(names):
            raise ValueError(f"algebra profile {algebra_profile.id!r} has duplicate vector names")
        self.vectors = MappingProxyType(dict(zip(names, basis, strict=True)))

    @property
    def implementation(self) -> ImplementationId:
        return self.configuration.implementation

    def basis_vectors(self) -> tuple[Any, ...]:
        """Return tracked basis vectors in the profile's semantic order."""
        return tuple(self.vectors.values())

    def vector(self, name: str) -> Any:
        try:
            return self.vectors[name]
        except KeyError as error:
            raise KeyError(f"the configured algebra has no semantic basis vector {name!r}") from error

    def call(self, operation: str, *args: Any) -> Any:
        """Invoke one operation through the public facade API without v1 remapping."""
        return getattr(self.api, operation)(*args)

    def named(
        self,
        value: Any,
        name: str,
        *,
        latex: str | None = None,
        unicode: str | None = None,
    ) -> Any:
        """Name a result without mutating a shared input value."""
        return value.named(name, latex=latex, unicode=unicode)

    def latex(self, value: Any) -> str:
        """Return the configured full LaTeX rendering for one returned value."""
        return self.render(value, target="latex", content="full")

    def render(self, value: Any, *, target: str, content: str) -> str:
        """Render one result through the public facade display path."""
        return value.display(content=content, target=target)


def _facade_cl2(display: facade.DisplayPolicy) -> facade.Algebra:
    return facade.Algebra((1, 1), display=display)


def _facade_cl3(display: facade.DisplayPolicy) -> facade.Algebra:
    return facade.Algebra((1, 1, 1), display=display)


def _facade_sta(display: facade.DisplayPolicy) -> facade.Algebra:
    return facade.Algebra(config=facade.p_sta(), display=display)


def _facade_pga(display: facade.DisplayPolicy) -> facade.Algebra:
    return facade.Algebra(config=facade.p_pga(), display=display)


def _facade_rga(display: facade.DisplayPolicy) -> facade.Algebra:
    return facade.Algebra(config=facade.p_rga(), display=display)


ALGEBRA_PROFILES: Mapping[str, AlgebraProfile] = MappingProxyType(
    {
        "cl2": AlgebraProfile(
            "cl2",
            "Euclidean Cl(2,0) with the conventional basis",
            _facade_cl2,
            ("e1", "e2"),
        ),
        "cl3": AlgebraProfile(
            "cl3",
            "Euclidean Cl(3,0) with the conventional basis",
            _facade_cl3,
            ("e1", "e2", "e3"),
        ),
        "sta-mostly-minus": AlgebraProfile(
            "sta-mostly-minus",
            "Spacetime Cl(1,3) with the gamma presentation",
            _facade_sta,
            ("g0", "g1", "g2", "g3"),
        ),
        "pga3": AlgebraProfile(
            "pga3",
            "Three-dimensional PGA with semantic e0/e1/e2/e3 vector mapping",
            _facade_pga,
            ("e1", "e2", "e3", "e0"),
        ),
        "lengyel-rga": AlgebraProfile(
            "lengyel-rga",
            "Eric Lengyel's RGA signature, blade table, display order, and notation",
            _facade_rga,
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
        NamedAlgebra(f"core-facade-v2/{algebra}/full-default", "core-facade-v2", algebra, "full-default")
        for algebra in ALGEBRA_PROFILES
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
