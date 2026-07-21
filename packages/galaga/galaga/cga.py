"""Conformal-model semantics over Galaga's native Gram-matrix facade.

The generic algebra already owns products, duals, joins, meets, and versor
actions.  This module adds only the information that those operations cannot
infer: which native null vectors are the conformal origin and infinity, which
vectors span Euclidean space, and how Euclidean and conformal points map to
one another.
"""

from __future__ import annotations

from collections.abc import Iterable
from numbers import Real
from types import MappingProxyType

import numpy as np

from .blades import BladeRef
from .facade import (
    Algebra,
    Multivector,
    complement,
    is_scalar,
    outer_product,
    regressive_product,
    right_hodge_dual,
    right_weight_dual,
    scalar_product,
    squared,
)


class ConformalModel:
    """A validated Euclidean conformal model with native ``eo`` and ``einf``.

    Construct the algebra independently so its numeric and presentation
    configuration remain replaceable, then attach these model semantics::

        algebra = Algebra(config=p_cga(spatial_dim=3))
        cga = ConformalModel(algebra)

    The model accepts the standard normalization ``eo·einf == -1`` and any
    other finite nonzero null-pair scaling declared by :func:`p_cga`.
    """

    __slots__ = ("_algebra", "_euclidean_refs", "_infinity_ref", "_null_pair", "_origin_ref")

    def __init__(self, algebra: Algebra) -> None:
        if not isinstance(algebra, Algebra):
            raise TypeError("algebra must be a galaga Algebra")
        model = algebra.model
        if model is None or model.id != "cga-null":
            raise ValueError("ConformalModel requires Algebra(config=p_cga(..., frame='null'))")

        roles = MappingProxyType(dict(model.roles))
        euclidean_refs = _ordered_euclidean_roles(roles)
        try:
            origin_ref = roles["origin"]
            infinity_ref = roles["infinity"]
        except KeyError as error:  # pragma: no cover - malformed custom ModelConfig
            raise ValueError("native-null CGA model roles must include origin and infinity") from error

        all_refs = (*euclidean_refs, origin_ref, infinity_ref)
        if len(all_refs) != algebra.n:
            raise ValueError("native-null CGA roles must account for every basis vector")
        if any(not _is_vector_ref(ref) for ref in all_refs):
            raise ValueError("native-null CGA model roles must refer to basis vectors")
        if len({ref.mask for ref in all_refs}) != len(all_refs):
            raise ValueError("native-null CGA model roles must refer to distinct basis vectors")

        self._algebra = algebra
        self._euclidean_refs = euclidean_refs
        self._origin_ref = origin_ref
        self._infinity_ref = infinity_ref
        self._null_pair = self._validate_metric()

    @property
    def algebra(self) -> Algebra:
        """The facade algebra carrying the numeric and presentation policy."""
        return self._algebra

    @property
    def spatial_dim(self) -> int:
        """The dimension of the embedded Euclidean vector space."""
        return len(self._euclidean_refs)

    @property
    def null_pair(self) -> float:
        """The configured mutual product ``eo·einf``."""
        return self._null_pair

    @property
    def origin(self) -> Multivector:
        """The native conformal-origin basis vector ``eo``."""
        return self._algebra.blade(self._origin_ref)

    @property
    def infinity(self) -> Multivector:
        """The native conformal-infinity basis vector ``einf``."""
        return self._algebra.blade(self._infinity_ref)

    def euclidean_basis_vectors(self, *, expr: bool = False) -> tuple[Multivector, ...]:
        """Return the ordered native basis of the embedded Euclidean space."""
        return tuple(self._algebra.blade(ref, expr=expr) for ref in self._euclidean_refs)

    def euclidean_vector(
        self,
        value: Iterable[Real] | Multivector,
        *,
        expr: bool = False,
    ) -> Multivector:
        """Construct or validate a vector in the embedded Euclidean subspace."""
        _require_expr_flag(expr)
        if isinstance(value, Multivector):
            self._check_value(value)
            self._require_euclidean_vector(value)
            return value.with_expr() if expr and value.expr is None else value

        if isinstance(value, (str, bytes)):
            raise TypeError("Euclidean coordinates must be an iterable of real numbers")
        try:
            coordinates = tuple(value)
        except TypeError as error:
            raise TypeError("Euclidean coordinates must be an iterable of real numbers") from error
        if len(coordinates) != self.spatial_dim:
            raise ValueError(f"expected {self.spatial_dim} Euclidean coordinates, got {len(coordinates)}")
        if any(
            not isinstance(coordinate, Real) or isinstance(coordinate, (bool, np.bool_)) for coordinate in coordinates
        ):
            raise TypeError("Euclidean coordinates must be real numbers")
        if any(not np.isfinite(float(coordinate)) for coordinate in coordinates):
            raise ValueError("Euclidean coordinates must be finite")

        data = np.zeros(self._algebra.dim)
        for coordinate, ref in zip(coordinates, self._euclidean_refs, strict=True):
            data[ref.mask] = ref.orientation * float(coordinate)
        result = self._algebra.multivector(data)
        return result.with_expr() if expr else result

    def round_point(
        self,
        position: Iterable[Real] | Multivector,
        *,
        radius_squared: Real | float | Multivector = 0.0,
        expr: bool = False,
    ) -> Multivector:
        r"""Embed a Euclidean center and signed squared radius as a CGA vector.

        For ``kappa = eo·einf``, the representation is

        ``eo + x - (x² + r²) einf / (2 kappa)``.

        The result therefore has square ``-r²`` for every supported null-pair
        scaling.  ``radius_squared=0`` is an ordinary conformal point; signed
        squared radius also represents the wiki's real and imaginary round
        points without introducing complex coefficients.
        """
        _require_expr_flag(expr)
        x = self.euclidean_vector(position, expr=expr)
        radius = self._scalar(radius_squared, expr=expr)
        eo = self._algebra.blade(self._origin_ref, expr=expr)
        einf = self._algebra.blade(self._infinity_ref, expr=expr)
        return eo + x - (squared(x) + radius) * einf / (2.0 * self._null_pair)

    def weight(self, value: Multivector) -> Multivector:
        """Return a conformal vector's homogeneous origin coefficient."""
        self._require_conformal_vector(value)
        return scalar_product(value, self.infinity) / self._null_pair

    def homogenize(self, value: Multivector, *, atol: float = 1e-12) -> Multivector:
        """Scale a finite conformal vector so its origin coefficient is one."""
        _require_nonnegative_tolerance(atol)
        homogeneous_weight = self.weight(value)
        coefficient = float(homogeneous_weight)
        if abs(coefficient) <= atol:
            raise ValueError("cannot homogenize a conformal vector with zero weight")
        return value / homogeneous_weight

    def down(self, value: Multivector, *, atol: float = 1e-12) -> Multivector:
        """Extract the Euclidean center of a finite conformal vector."""
        normalized = self.homogenize(value, atol=atol)
        data = np.zeros(self._algebra.dim)
        for ref in self._euclidean_refs:
            data[ref.mask] = normalized.coefficient(ref.mask)
        return self._algebra.multivector(data)

    def coordinates(self, value: Multivector, *, atol: float = 1e-12) -> np.ndarray:
        """Return the Euclidean center as an immutable coordinate array."""
        center = self.down(value, atol=atol)
        result = np.array(
            [ref.orientation * center.coefficient(ref.mask) for ref in self._euclidean_refs],
            dtype=float,
        )
        result.setflags(write=False)
        return result

    def radius_squared(self, value: Multivector, *, atol: float = 1e-12) -> Multivector:
        """Return the signed squared radius encoded by a round-point vector."""
        _require_nonnegative_tolerance(atol)
        homogeneous_weight = self.weight(value)
        coefficient = float(homogeneous_weight)
        if abs(coefficient) <= atol:
            raise ValueError("an infinite conformal vector has no finite round radius")
        return -squared(value) / (homogeneous_weight * homogeneous_weight)

    def dual(self, value: Multivector) -> Multivector:
        r"""Return the CGA wiki dual ``complement(metric_apply(value))``."""
        self._check_value(value)
        return right_hodge_dual(value)

    def antidual(self, value: Multivector) -> Multivector:
        r"""Return the CGA wiki antidual ``complement(antimetric_apply(value))``."""
        self._check_value(value)
        return right_weight_dual(value)

    def attitude(self, value: Multivector) -> Multivector:
        """Extract a geometry's purely directional object."""
        self._require_geometry(value)
        return regressive_product(value, complement(self.origin))

    def carrier(self, value: Multivector) -> Multivector:
        """Return the lowest-dimensional flat geometry containing ``value``."""
        self._require_geometry(value)
        result = outer_product(value, self.infinity)
        if not np.any(np.abs(result.data) > 1e-12):
            raise ValueError("carrier requires a round geometry with a nonzero round part")
        return result

    def cocarrier(self, value: Multivector) -> Multivector:
        """Return the carrier of ``value``'s antidual."""
        self._require_geometry(value)
        return self.carrier(self.antidual(value))

    def center(self, value: Multivector) -> Multivector:
        """Return the round point having a round geometry's center and radius."""
        self._require_geometry(value)
        return regressive_product(self.cocarrier(value), value)

    def flat_center(self, value: Multivector) -> Multivector:
        """Return the flat point where a round geometry's carrier and cocarrier meet."""
        self._require_geometry(value)
        return regressive_product(self.cocarrier(value), self.carrier(value))

    def expansion(self, value: Multivector, onto: Multivector) -> Multivector:
        """Return the object containing ``value`` and orthogonal to higher-grade ``onto``."""
        value_grade = self._require_geometry(value)
        onto_grade = self._require_geometry(onto)
        if value_grade >= onto_grade:
            raise ValueError("expansion requires the second geometry to have higher grade")
        return outer_product(value, self.antidual(onto))

    def projection(self, value: Multivector, onto: Multivector) -> Multivector:
        """Project ``value`` onto a higher-grade conformal geometry."""
        expanded = self.expansion(value, onto)
        return regressive_product(onto, expanded)

    def container(self, value: Multivector) -> Multivector:
        """Return the smallest sphere containing a round geometry."""
        self._require_geometry(value)
        return outer_product(value, self.antidual(self.carrier(value)))

    def partner(self, value: Multivector) -> Multivector:
        """Reverse a round geometry's signed squared radius about the same center.

        The wiki's polynomial partner identity is tied to its standard
        ``eo·einf == -1`` normalization.
        """
        if not np.isclose(self._null_pair, -1.0, rtol=0.0, atol=1e-12):
            raise ValueError("partner requires the standard eo·einf == -1 normalization")
        value_grade = self._require_geometry(value)
        result = regressive_product(self.container(self.antidual(value)), self.carrier(value))
        return ((-1) ** (value_grade + 1)) * result

    # The CGA literature uses these abbreviations as functional notation.
    # They are exact aliases; the descriptive names remain the primary API.
    att = attitude
    car = carrier
    ccr = cocarrier
    cen = center
    con = container
    homo = homogenize
    par = partner
    project = projection
    up = round_point

    def _scalar(self, value: Real | float | Multivector, *, expr: bool) -> Multivector:
        if isinstance(value, Multivector):
            self._check_value(value)
            if not is_scalar(value):
                raise ValueError("radius_squared must be a scalar multivector")
            return value.with_expr() if expr and value.expr is None else value
        if not isinstance(value, Real) or isinstance(value, (bool, np.bool_)):
            raise TypeError("radius_squared must be a real number or scalar multivector")
        if not np.isfinite(float(value)):
            raise ValueError("radius_squared must be finite")
        return self._algebra.scalar(value, expr=expr)

    def _check_value(self, value: Multivector) -> None:
        if not isinstance(value, Multivector):
            raise TypeError("expected a Galaga multivector")
        if value.numeric.algebra is not self._algebra.numeric:
            raise ValueError("multivector belongs to a different numeric algebra")

    def _require_conformal_vector(self, value: Multivector) -> None:
        self._check_value(value)
        if value.homogeneous_grade() != 1:
            raise ValueError("expected a homogeneous conformal vector")

    def _require_geometry(self, value: Multivector) -> int:
        self._check_value(value)
        value_grade = value.homogeneous_grade()
        if value_grade is None or not 1 <= value_grade < self._algebra.n:
            raise ValueError("expected a homogeneous conformal geometry of grade 1 through n - 1")
        return value_grade

    def _require_euclidean_vector(self, value: Multivector, *, atol: float = 1e-12) -> None:
        if value.homogeneous_grade(atol=atol) not in {None, 1}:
            raise ValueError("expected a vector in the embedded Euclidean subspace")
        allowed = {ref.mask for ref in self._euclidean_refs}
        for mask, coefficient in enumerate(value.data):
            if mask not in allowed and abs(float(coefficient)) > atol:
                raise ValueError("expected a vector in the embedded Euclidean subspace")

    def _validate_metric(self) -> float:
        basis = tuple(self._algebra.blade(ref) for ref in self._euclidean_refs)
        eo = self._algebra.blade(self._origin_ref)
        einf = self._algebra.blade(self._infinity_ref)
        expected = np.eye(self.spatial_dim)
        euclidean_gram = np.array([[float(scalar_product(a, b)) for b in basis] for a in basis])
        if not np.allclose(euclidean_gram, expected, rtol=0.0, atol=1e-12):
            raise ValueError("native-null CGA Euclidean roles must have an identity Gram block")
        if any(
            abs(float(scalar_product(vector, null_vector))) > 1e-12 for vector in basis for null_vector in (eo, einf)
        ):
            raise ValueError("native-null CGA null roles must be orthogonal to Euclidean space")
        if abs(float(squared(eo))) > 1e-12 or abs(float(squared(einf))) > 1e-12:
            raise ValueError("native-null CGA origin and infinity roles must be null")
        null_pair = float(scalar_product(eo, einf))
        if not np.isfinite(null_pair) or abs(null_pair) <= 1e-12:
            raise ValueError("native-null CGA origin and infinity must have a finite nonzero mutual product")
        return null_pair


def _ordered_euclidean_roles(roles: MappingProxyType[str, BladeRef]) -> tuple[BladeRef, ...]:
    indexed: dict[int, BladeRef] = {}
    for name, ref in roles.items():
        if not name.startswith("euclidean_"):
            continue
        suffix = name.removeprefix("euclidean_")
        if not suffix.isdecimal() or int(suffix) < 1:
            raise ValueError("Euclidean CGA model roles must be numbered from euclidean_1")
        indexed[int(suffix)] = ref
    if not indexed or set(indexed) != set(range(1, len(indexed) + 1)):
        raise ValueError("Euclidean CGA model roles must be contiguous from euclidean_1")
    return tuple(indexed[index] for index in range(1, len(indexed) + 1))


def _is_vector_ref(ref: BladeRef) -> bool:
    return ref.mask > 0 and ref.mask.bit_count() == 1


def _require_expr_flag(value: bool) -> None:
    if not isinstance(value, bool):
        raise TypeError("expr must be a boolean")


def _require_nonnegative_tolerance(value: float) -> None:
    if not isinstance(value, Real) or isinstance(value, (bool, np.bool_)):
        raise TypeError("atol must be a real number")
    if not np.isfinite(float(value)) or value < 0:
        raise ValueError("atol must be finite and non-negative")


__all__ = ["ConformalModel"]
