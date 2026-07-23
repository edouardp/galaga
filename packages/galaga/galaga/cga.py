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
from typing import Literal, cast

import numpy as np

from .blades import BladeRef
from .expression import Call, Expr, Symbol
from .facade import (
    Algebra,
    Multivector,
    antidot_product,
    antimetric_apply,
    complement,
    is_scalar,
    metric_apply,
    metric_inner_product,
    outer_product,
    regressive_product,
    right_hodge_dual,
    right_weight_dual,
    scalar_product,
    squared,
)

CGAExpressionForm = Literal["operator", "expanded"]


class ConformalModel:
    """A validated Euclidean conformal model with native ``eo`` and ``einf``.

    Construct the algebra independently so its numeric and presentation
    configuration remain replaceable, then attach these model semantics::

        algebra = Algebra(config=p_cga(spatial_dim=3))
        cga = ConformalModel(algebra, expr=True)

    The model accepts the standard normalization ``eo·einf == -1`` and any
    other finite nonzero null-pair scaling declared by :func:`p_cga`.
    """

    __slots__ = (
        "_algebra",
        "_euclidean_refs",
        "_expr",
        "_expression_form",
        "_infinity_ref",
        "_null_pair",
        "_origin_ref",
    )

    def __init__(
        self,
        algebra: Algebra,
        *,
        expr: bool = False,
        expression_form: CGAExpressionForm = "operator",
    ) -> None:
        if not isinstance(algebra, Algebra):
            raise TypeError("algebra must be a galaga Algebra")
        _require_expr_flag(expr)
        selected_expression_form = _require_expression_form(expression_form)
        model = algebra.model
        if model is None or model.id != "cga-null":
            raise ValueError(
                "ConformalModel requires Algebra(config=p_cga(..., frame='null')) or Algebra(config=p_lengyel_cga())"
            )

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
        self._expr = expr
        self._expression_form = selected_expression_form
        self._origin_ref = origin_ref
        self._infinity_ref = infinity_ref
        self._null_pair = self._validate_metric()

    @property
    def algebra(self) -> Algebra:
        """The facade algebra carrying the numeric and presentation policy."""
        return self._algebra

    @property
    def expr(self) -> bool:
        """Whether model-owned factories track expression provenance by default."""
        return self._expr

    @property
    def expression_form(self) -> CGAExpressionForm:
        """The default provenance form attached by CGA helper operations."""
        return self._expression_form

    def with_expression_form(self, expression_form: CGAExpressionForm) -> ConformalModel:
        """Return a model view selecting operator or expanded helper provenance."""
        return type(self)(
            self._algebra,
            expr=self._expr,
            expression_form=_require_expression_form(expression_form),
        )

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
        return self._algebra.blade(self._origin_ref, expr=self._expr)

    @property
    def infinity(self) -> Multivector:
        """The native conformal-infinity basis vector ``einf``."""
        return self._algebra.blade(self._infinity_ref, expr=self._expr)

    def euclidean_basis_vectors(self, *, expr: bool | None = None) -> tuple[Multivector, ...]:
        """Return the ordered native basis, inheriting the model expression default."""
        tracking = self._resolve_expr(expr)
        return tuple(self._algebra.blade(ref, expr=tracking) for ref in self._euclidean_refs)

    def euclidean_vector(
        self,
        value: Iterable[Real] | Multivector,
        *,
        expr: bool | None = None,
    ) -> Multivector:
        """Construct or validate a Euclidean vector, inheriting the expression default."""
        tracking = self._resolve_expr(expr)
        if isinstance(value, Multivector):
            self._check_value(value)
            self._require_euclidean_vector(value)
            return value.with_expr() if tracking and value.expr is None else value

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
        return result.with_expr() if tracking else result

    def round_point(
        self,
        position: Iterable[Real] | Multivector,
        *,
        radius_squared: Real | float | Multivector = 0.0,
        expr: bool | None = None,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        r"""Embed a Euclidean center and signed squared radius as a CGA vector.

        For ``kappa = eo·einf``, the representation is

        ``eo + x - (x² + r²) einf / (2 kappa)``.

        The result therefore has square ``-r²`` for every supported null-pair
        scaling.  ``radius_squared=0`` is an ordinary conformal point; signed
        squared radius also represents the wiki's real and imaginary round
        points without introducing complex coefficients.
        """
        tracking = self._resolve_expr(expr)
        x = self.euclidean_vector(position, expr=tracking)
        radius = self._scalar(radius_squared, expr=tracking)
        eo = self._algebra.blade(self._origin_ref, expr=tracking)
        einf = self._algebra.blade(self._infinity_ref, expr=tracking)
        result = eo + x + (squared(x) + radius) * einf / (-2.0 * self._null_pair)
        return self._semantic(
            result,
            "round_point",
            x,
            radius,
            expression_form=expression_form,
            tracking=tracking if expr is not None or self._expr else None,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
        )

    def up(
        self,
        position: Iterable[Real] | Multivector,
        *,
        expr: bool | None = None,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Embed an ordinary conformal point, preserving the ``up`` operation identity."""
        tracking = self._resolve_expr(expr)
        x = self.euclidean_vector(position, expr=tracking)
        eo = self._algebra.blade(self._origin_ref, expr=tracking)
        einf = self._algebra.blade(self._infinity_ref, expr=tracking)
        result = eo + x + squared(x) * einf / (-2.0 * self._null_pair)
        return self._semantic(
            result,
            "up",
            x,
            expression_form=expression_form,
            tracking=tracking if expr is not None or self._expr else None,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
        )

    def weight(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return a conformal vector's homogeneous origin coefficient."""
        self._require_conformal_vector(value)
        result = scalar_product(value, self.infinity) / self._null_pair
        return self._semantic(
            result,
            "weight",
            value,
            expression_form=expression_form,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
        )

    def homogenize(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Scale a finite conformal vector so its origin coefficient is one."""
        _require_nonnegative_tolerance(atol)
        selected = self._resolve_expression_form(expression_form)
        homogeneous_weight = self.weight(value, expression_form=selected)
        coefficient = float(homogeneous_weight)
        if abs(coefficient) <= atol:
            raise ValueError("cannot homogenize a conformal vector with zero weight")
        result = value / homogeneous_weight
        return self._semantic(
            result,
            "homogenize",
            value,
            expression_form=selected,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def down(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Extract the Euclidean center of a finite conformal vector."""
        selected = self._resolve_expression_form(expression_form)
        normalized = self.homogenize(value, atol=atol, expression_form=selected)
        data = np.zeros(self._algebra.dim)
        for ref in self._euclidean_refs:
            data[ref.mask] = normalized.coefficient(ref.mask)
        result = self._algebra.multivector(data)
        return self._semantic(
            result,
            "down",
            value,
            expression_form=selected,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def coordinates(self, value: Multivector, *, atol: float = 1e-12) -> np.ndarray:
        """Return the Euclidean center as an immutable coordinate array."""
        center = self.down(value, atol=atol)
        result = np.array(
            [ref.orientation * center.coefficient(ref.mask) for ref in self._euclidean_refs],
            dtype=float,
        )
        result.setflags(write=False)
        return result

    def radius_squared(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return the signed squared radius encoded by a round-point vector."""
        _require_nonnegative_tolerance(atol)
        selected = self._resolve_expression_form(expression_form)
        homogeneous_weight = self.weight(value, expression_form=selected)
        coefficient = float(homogeneous_weight)
        if abs(coefficient) <= atol:
            raise ValueError("an infinite conformal vector has no finite round radius")
        result = -squared(value) / (homogeneous_weight * homogeneous_weight)
        return self._semantic(
            result,
            "radius_squared",
            value,
            expression_form=selected,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def dual(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        r"""Return the CGA wiki dual ``complement(metric_apply(value))``."""
        self._check_value(value)
        tracked = self._tracked(value)
        if self._resolve_expression_form(expression_form) == "operator":
            return right_hodge_dual(tracked)
        return complement(metric_apply(tracked))

    def antidual(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        r"""Return the CGA wiki antidual ``complement(antimetric_apply(value))``."""
        self._check_value(value)
        tracked = self._tracked(value)
        if self._resolve_expression_form(expression_form) == "operator":
            return right_weight_dual(tracked)
        return complement(antimetric_apply(tracked))

    def round_bulk_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return terms containing neither the origin nor infinity basis vector."""
        return self._component_part(
            value,
            "round_bulk_part",
            contains_origin=False,
            contains_infinity=False,
            expression_form=expression_form,
        )

    def round_weight_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return terms containing the origin but not the infinity basis vector."""
        return self._component_part(
            value,
            "round_weight_part",
            contains_origin=True,
            contains_infinity=False,
            expression_form=expression_form,
        )

    def flat_bulk_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return terms containing infinity but not the origin basis vector."""
        return self._component_part(
            value,
            "flat_bulk_part",
            contains_origin=False,
            contains_infinity=True,
            expression_form=expression_form,
        )

    def flat_weight_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return terms containing both the origin and infinity basis vectors."""
        return self._component_part(
            value,
            "flat_weight_part",
            contains_origin=True,
            contains_infinity=True,
            expression_form=expression_form,
        )

    def round_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return all terms that do not contain the infinity basis vector."""
        return self._role_part(
            value,
            "round_part",
            role=self._infinity_ref,
            contains_role=False,
            expression_form=expression_form,
            infinity=self._role(self._infinity_ref),
        )

    def flat_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return all terms that contain the infinity basis vector."""
        return self._role_part(
            value,
            "flat_part",
            role=self._infinity_ref,
            contains_role=True,
            expression_form=expression_form,
            infinity=self._role(self._infinity_ref),
        )

    def bulk_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return CGA terms that do not contain the origin basis vector."""
        return self._role_part(
            value,
            "conformal_bulk_part",
            role=self._origin_ref,
            contains_role=False,
            expression_form=expression_form,
            origin=self._role(self._origin_ref),
        )

    def weight_part(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return CGA terms that contain the origin basis vector."""
        return self._role_part(
            value,
            "conformal_weight_part",
            role=self._origin_ref,
            contains_role=True,
            expression_form=expression_form,
            origin=self._role(self._origin_ref),
        )

    def conformal_conjugate(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Preserve round terms and negate flat terms."""
        self._require_geometry(value)
        selected = self._resolve_expression_form(expression_form)
        result = self.round_part(value, expression_form=selected) - self.flat_part(
            value,
            expression_form=selected,
        )
        return self._semantic(
            result,
            "conformal_conjugate",
            value,
            expression_form=selected,
            infinity=self._role(self._infinity_ref),
        )

    def weighted_center_norm(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        r"""Return the homogeneous numerator of Lengyel's center norm."""
        _require_nonnegative_tolerance(atol)
        self._require_geometry(value)
        selected = self._resolve_expression_form(expression_form)
        pairing = metric_inner_product(
            value,
            self.conformal_conjugate(value, expression_form=selected),
        )
        result = self._scalar_norm_root(pairing, name="weighted center norm", atol=atol)
        result = self._with_norm_expression(result, pairing, "cga_scalar_norm_root", atol=atol)
        return self._semantic(
            result,
            "weighted_center_norm",
            value,
            expression_form=selected,
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def weighted_radius_norm(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        r"""Return the homogeneous antiscalar numerator of Lengyel's radius norm."""
        _require_nonnegative_tolerance(atol)
        self._require_standard_normalization("weighted_radius_norm")
        self._require_geometry(value)
        pairing = antidot_product(value, value)
        result = self._antiscalar_norm_root(
            pairing,
            name="weighted radius norm",
            atol=atol,
        )
        result = self._with_norm_expression(result, pairing, "cga_antiscalar_norm_root", atol=atol)
        return self._semantic(
            result,
            "weighted_radius_norm",
            value,
            expression_form=expression_form,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def round_bulk_norm(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return the scalar-valued norm of a geometry's round bulk part."""
        _require_nonnegative_tolerance(atol)
        self._require_geometry(value)
        carrier = outer_product(value, self.infinity)
        reduced = regressive_product(carrier, complement(self.infinity))
        pairing = metric_inner_product(reduced, reduced)
        result = self._scalar_norm_root(
            pairing,
            name="round bulk norm",
            atol=atol,
        )
        result = self._with_norm_expression(result, pairing, "cga_scalar_norm_root", atol=atol)
        return self._semantic(
            result,
            "round_bulk_norm",
            value,
            expression_form=expression_form,
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def round_weight_norm(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return the origin-complement-valued norm of the round weight part."""
        _require_nonnegative_tolerance(atol)
        self._require_geometry(value)
        carrier = outer_product(value, self.infinity)
        pairing = antidot_product(carrier, carrier)
        antiscalar = self._antiscalar_norm_root(
            pairing,
            name="round weight norm",
            atol=atol,
        )
        antiscalar = self._with_norm_expression(
            antiscalar,
            pairing,
            "cga_antiscalar_norm_root",
            atol=atol,
        )
        result = regressive_product(antiscalar, complement(self.infinity))
        return self._semantic(
            result,
            "round_weight_norm",
            value,
            expression_form=expression_form,
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def flat_bulk_norm(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return the infinity-vector-valued norm of the flat bulk part."""
        _require_nonnegative_tolerance(atol)
        self._require_geometry(value)
        reduced = regressive_product(value, complement(self.infinity))
        pairing = metric_inner_product(reduced, reduced)
        magnitude = self._scalar_norm_root(
            pairing,
            name="flat bulk norm",
            atol=atol,
        )
        magnitude = self._with_norm_expression(
            magnitude,
            pairing,
            "cga_scalar_norm_root",
            atol=atol,
        )
        result = outer_product(magnitude, self.infinity)
        return self._semantic(
            result,
            "flat_bulk_norm",
            value,
            expression_form=expression_form,
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def flat_weight_norm(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return the antiscalar-valued norm of the flat weight part."""
        _require_nonnegative_tolerance(atol)
        self._require_geometry(value)
        reduced = regressive_product(value, complement(self.infinity))
        isolated = outer_product(reduced, self.infinity)
        pairing = antidot_product(isolated, isolated)
        result = self._antiscalar_norm_root(
            pairing,
            name="flat weight norm",
            atol=atol,
        )
        result = self._with_norm_expression(result, pairing, "cga_antiscalar_norm_root", atol=atol)
        return self._semantic(
            result,
            "flat_weight_norm",
            value,
            expression_form=expression_form,
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def center_norm(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return Lengyel's projectively normalized center norm."""
        _require_nonnegative_tolerance(atol)
        selected = self._resolve_expression_form(expression_form)
        weighted_center = self.weighted_center_norm(value, atol=atol, expression_form=selected)
        weight = self._round_weight_magnitude(value, atol=atol)
        result = (weighted_center / weight).without_expr()
        return self._semantic(
            result,
            "center_norm",
            value,
            expression_form=selected,
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def radius_norm(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return Lengyel's projectively normalized real radius norm."""
        _require_nonnegative_tolerance(atol)
        self._require_standard_normalization("radius_norm")
        selected = self._resolve_expression_form(expression_form)
        weighted_radius = self.weighted_radius_norm(value, atol=atol, expression_form=selected)
        numerator = self._blade_magnitude(
            weighted_radius,
            self._algebra.I,
            name="weighted radius norm",
            atol=atol,
        )
        denominator = self._round_weight_magnitude(value, atol=atol)
        result = self._algebra.scalar(numerator / denominator)
        return self._semantic(
            result,
            "radius_norm",
            value,
            expression_form=selected,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def center_distance(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return ``center_norm(value)`` under an explicit geometric alias."""
        selected = self._resolve_expression_form(expression_form)
        result = self.center_norm(value, atol=atol, expression_form=selected)
        return self._semantic(
            result,
            "center_distance",
            value,
            expression_form=selected,
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def radius(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return ``radius_norm(value)`` under the conventional geometry name."""
        selected = self._resolve_expression_form(expression_form)
        result = self.radius_norm(value, atol=atol, expression_form=selected)
        return self._semantic(
            result,
            "radius",
            value,
            expression_form=selected,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
            atol=atol,
        )

    def attitude(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Extract a geometry's purely directional object."""
        self._require_geometry(value)
        result = regressive_product(value, complement(self.origin))
        return self._semantic(
            result,
            "attitude",
            value,
            expression_form=expression_form,
            origin=self._role(self._origin_ref),
        )

    def carrier(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return the lowest-dimensional flat geometry containing ``value``."""
        self._require_geometry(value)
        result = outer_product(value, self.infinity)
        if not np.any(np.abs(result.data) > 1e-12):
            raise ValueError("carrier requires a round geometry with a nonzero round part")
        return self._semantic(
            result,
            "carrier",
            value,
            expression_form=expression_form,
            infinity=self._role(self._infinity_ref),
        )

    def cocarrier(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return the carrier of ``value``'s antidual."""
        self._require_geometry(value)
        selected = self._resolve_expression_form(expression_form)
        result = self.carrier(self.antidual(value), expression_form=selected)
        return self._semantic(
            result,
            "cocarrier",
            value,
            expression_form=selected,
            infinity=self._role(self._infinity_ref),
        )

    def center(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return the round point having a round geometry's center and radius."""
        self._require_geometry(value)
        selected = self._resolve_expression_form(expression_form)
        result = regressive_product(self.cocarrier(value, expression_form=selected), value)
        return self._semantic(
            result,
            "center",
            value,
            expression_form=selected,
            infinity=self._role(self._infinity_ref),
        )

    def flat_center(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return the flat point where a round geometry's carrier and cocarrier meet."""
        self._require_geometry(value)
        selected = self._resolve_expression_form(expression_form)
        result = regressive_product(
            self.cocarrier(value, expression_form=selected),
            self.carrier(value, expression_form=selected),
        )
        return self._semantic(
            result,
            "flat_center",
            value,
            expression_form=selected,
            infinity=self._role(self._infinity_ref),
        )

    def expansion(
        self,
        value: Multivector,
        onto: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return the object containing ``value`` and orthogonal to higher-grade ``onto``."""
        value_grade = self._require_geometry(value)
        onto_grade = self._require_geometry(onto)
        if value_grade >= onto_grade:
            raise ValueError("expansion requires the second geometry to have higher grade")
        selected = self._resolve_expression_form(expression_form)
        result = outer_product(value, self.antidual(onto, expression_form=selected))
        return self._semantic(
            result,
            "expansion",
            value,
            onto,
            expression_form=selected,
        )

    def projection(
        self,
        value: Multivector,
        onto: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Project ``value`` onto a higher-grade conformal geometry."""
        selected = self._resolve_expression_form(expression_form)
        expanded = self.expansion(value, onto, expression_form=selected)
        result = regressive_product(onto, expanded)
        return self._semantic(
            result,
            "projection",
            value,
            onto,
            expression_form=selected,
        )

    def container(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Return the smallest sphere containing a round geometry."""
        self._require_geometry(value)
        selected = self._resolve_expression_form(expression_form)
        result = outer_product(
            value,
            self.antidual(self.carrier(value, expression_form=selected)),
        )
        return self._semantic(
            result,
            "container",
            value,
            expression_form=selected,
            infinity=self._role(self._infinity_ref),
        )

    def partner(
        self,
        value: Multivector,
        *,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Reverse a round geometry's signed squared radius about the same center.

        The wiki's polynomial partner identity is tied to its standard
        ``eo·einf == -1`` normalization.
        """
        if not np.isclose(self._null_pair, -1.0, rtol=0.0, atol=1e-12):
            raise ValueError("partner requires the standard eo·einf == -1 normalization")
        selected = self._resolve_expression_form(expression_form)
        value_grade = self._require_geometry(value)
        result = regressive_product(
            self.container(self.antidual(value), expression_form=selected),
            self.carrier(value, expression_form=selected),
        )
        result = ((-1) ** (value_grade + 1)) * result
        return self._semantic(
            result,
            "partner",
            value,
            expression_form=selected,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
        )

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

    def _component_part(
        self,
        value: Multivector,
        operation_id: str,
        *,
        contains_origin: bool,
        contains_infinity: bool,
        expression_form: CGAExpressionForm | None,
    ) -> Multivector:
        self._require_geometry(value)
        data = np.zeros_like(value.data)
        for mask, coefficient in enumerate(value.data):
            if (
                bool(mask & self._origin_ref.mask) is contains_origin
                and bool(mask & self._infinity_ref.mask) is contains_infinity
            ):
                data[mask] = coefficient
        result = self._algebra.multivector(data)
        return self._semantic(
            result,
            operation_id,
            value,
            expression_form=expression_form,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
        )

    def _role_part(
        self,
        value: Multivector,
        operation_id: str,
        *,
        role: BladeRef,
        contains_role: bool,
        expression_form: CGAExpressionForm | None,
        **parameters: object,
    ) -> Multivector:
        self._require_geometry(value)
        data = np.zeros_like(value.data)
        for mask, coefficient in enumerate(value.data):
            if bool(mask & role.mask) is contains_role:
                data[mask] = coefficient
        result = self._algebra.multivector(data)
        return self._semantic(
            result,
            operation_id,
            value,
            expression_form=expression_form,
            **parameters,
        )

    def _scalar_norm_root(self, value: Multivector, *, name: str, atol: float) -> Multivector:
        if not is_scalar(value, atol=atol):
            raise ValueError(f"{name} squared must be scalar")
        coefficient = float(value.coefficient(0))
        scale = max(1.0, abs(coefficient))
        if coefficient < -atol * scale:
            raise ValueError(f"{name} is not real")
        return self._algebra.scalar(float(np.sqrt(max(0.0, coefficient))))

    def _antiscalar_norm_root(self, value: Multivector, *, name: str, atol: float) -> Multivector:
        coefficient = self._blade_magnitude(value, self._algebra.I, name=f"{name} squared", atol=atol)
        scale = max(1.0, abs(coefficient))
        if coefficient < -atol * scale:
            raise ValueError(f"{name} is not real")
        return float(np.sqrt(max(0.0, coefficient))) * self._algebra.I

    def _with_norm_expression(
        self,
        result: Multivector,
        squared_value: Multivector,
        operation_id: str,
        *,
        atol: float,
    ) -> Multivector:
        if not self._expr and squared_value.name is None and squared_value.expr is None:
            return result
        return result.with_expr(
            Call(
                operation_id,
                (self._expression_operand(squared_value),),
                {"atol": atol},
            )
        )

    def _round_weight_magnitude(self, value: Multivector, *, atol: float) -> float:
        basis = complement(self._algebra.blade(self._infinity_ref))
        magnitude = self._blade_magnitude(
            self.round_weight_norm(value, atol=atol),
            basis,
            name="round weight norm",
            atol=atol,
        )
        if abs(magnitude) <= atol:
            raise ValueError("normalized conformal measurement requires nonzero round weight")
        return magnitude

    @staticmethod
    def _blade_magnitude(value: Multivector, basis: Multivector, *, name: str, atol: float) -> float:
        mask = int(np.flatnonzero(basis.data)[0])
        coefficient = value.coefficient(mask) / basis.coefficient(mask)
        residual = value.data - coefficient * basis.data
        if np.any(np.abs(residual) > atol * max(1.0, abs(coefficient))):
            raise ValueError(f"{name} must be proportional to its expected basis blade")
        return float(coefficient)

    def _require_standard_normalization(self, operation: str) -> None:
        if not np.isclose(self._null_pair, -1.0, rtol=0.0, atol=1e-12):
            raise ValueError(f"{operation} requires the standard eo·einf == -1 normalization")

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

    def _resolve_expr(self, value: bool | None) -> bool:
        if value is None:
            return self._expr
        _require_expr_flag(value)
        return value

    def _tracked(self, value: Multivector) -> Multivector:
        if self._expr and value.name is None and value.expr is None:
            return value.with_expr()
        return value

    def _semantic(
        self,
        result: Multivector,
        operation_id: str,
        *values: Multivector,
        expression_form: CGAExpressionForm | None = None,
        tracking: bool | None = None,
        expanded: Expr | None = None,
        **parameters: object,
    ) -> Multivector:
        selected = self._resolve_expression_form(expression_form)
        if tracking is False:
            return result.without_expr() if result.expr is not None else result
        if (
            tracking is not True
            and not self._expr
            and all(value.name is None and value.expr is None for value in values)
        ):
            return result
        operator = Call(
            operation_id,
            tuple(self._expression_operand(value) for value in values),
            parameters,
        )
        if selected == "operator":
            return result.with_expr(operator)
        formula = expanded if expanded is not None else result.expr
        return result.with_expr(operator if formula is None else formula)

    def _resolve_expression_form(
        self,
        value: CGAExpressionForm | None,
    ) -> CGAExpressionForm:
        if value is None:
            return self._expression_form
        return _require_expression_form(value)

    @staticmethod
    def _expression_operand(value: Multivector) -> Expr:
        if value.name is not None:
            return Symbol(value.name)
        if value.expr is not None:
            return value.expr
        expression = value.with_expr().expr
        if expression is None:  # pragma: no cover - with_expr always supplies one
            raise RuntimeError("failed to construct expression provenance")
        return expression

    @staticmethod
    def _role(ref: BladeRef) -> tuple[int, int]:
        return ref.mask, ref.orientation

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


def _require_expression_form(value: object) -> CGAExpressionForm:
    if not isinstance(value, str):
        raise TypeError("expression_form must be a string")
    if value not in {"operator", "expanded"}:
        raise ValueError("expression_form must be 'operator' or 'expanded'")
    return cast(CGAExpressionForm, value)


def _require_nonnegative_tolerance(value: float) -> None:
    if not isinstance(value, Real) or isinstance(value, (bool, np.bool_)):
        raise TypeError("atol must be a real number")
    if not np.isfinite(float(value)) or value < 0:
        raise ValueError("atol must be finite and non-negative")


__all__ = ["CGAExpressionForm", "ConformalModel"]
