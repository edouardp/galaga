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
from typing import Literal, cast

import numpy as np

from ..blades import BladeRef
from ..expression import Call
from ..facade import (
    Algebra,
    Multivector,
    antidot_product,
    complement,
    is_scalar,
    metric_inner_product,
    outer_product,
    regressive_product,
    squared,
)
from ._base import _ConformalBase, ordered_euclidean_roles
from ._classification import classify_conformal
from .classification import CGAClassification

CGAExpressionForm = Literal["operator", "expanded"]


class ConformalModel(_ConformalBase):
    """A validated Euclidean conformal model with native ``eo`` and ``einf``.

    Construct the algebra independently so its numeric and presentation
    configuration remain replaceable, then attach these model semantics::

        algebra = Algebra(config=presets.cga(spatial_dim=3))
        cga = ConformalModel(algebra, expr=True)

    The model accepts the standard normalization ``eo·einf == -1`` and any
    other finite nonzero null-pair scaling declared by :func:`presets.cga`.
    """

    _model_id = "cga-null"
    _preset_description = "Algebra(config=presets.cga(..., frame='null')) or Algebra(config=presets.lengyel_cga())"

    __slots__ = ()

    def __init__(
        self,
        algebra: Algebra,
        *,
        expr: bool | None = None,
        expression_form: CGAExpressionForm = "operator",
    ) -> None:
        super().__init__(algebra, expr=expr)
        selected_expression_form = _require_expression_form(expression_form)

        roles = self._roles
        euclidean_refs = ordered_euclidean_roles(roles)
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

        self._base_refs = euclidean_refs
        self._expression_form = selected_expression_form
        self._origin_ref = origin_ref
        self._infinity_ref = infinity_ref
        self._null_pair = self._validate_metric()

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
        return len(self._base_refs)

    def euclidean_basis_vectors(self, *, expr: bool | None = None) -> tuple[Multivector, ...]:
        """Return the ordered native basis, inheriting the model expression default."""
        tracking = self._resolve_expr(expr)
        return tuple(self._algebra.blade(ref, expr=tracking) for ref in self._base_refs)

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

        return self._coordinate_vector(tuple(float(c) for c in coordinates), self._base_refs, tracking=tracking)

    def round_point(
        self,
        position: Real | Iterable[Real] | Multivector,
        *coordinates: Real,
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

        Supply the position as one coordinate iterable, one Euclidean
        multivector, or one real positional argument per spatial dimension.
        """
        tracking = self._resolve_expr(expr)
        x = self.euclidean_vector(
            self._position_input(position, coordinates),
            expr=tracking,
        )
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

    def point(
        self,
        position: Real | Iterable[Real] | Multivector,
        *coordinates: Real,
        expr: bool | None = None,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Construct a conformal point from Euclidean coordinates or a vector."""
        tracking = self._resolve_expr(expr)
        x = self.euclidean_vector(self._position_input(position, coordinates), expr=tracking)
        return self._semantic(
            self._embed(x, tracking=tracking),
            "conformal_point",
            x,
            expression_form=expression_form,
            tracking=tracking,
            origin=self._role(self._origin_ref),
            infinity=self._role(self._infinity_ref),
        )

    def classify(
        self, value: Multivector, *, representation: Literal["auto", "direct", "dual"] = "auto", atol: float = 1e-9
    ) -> CGAClassification:
        """Classify direct or explicitly dual objects in 2D and 3D CGA."""
        return classify_conformal(self, value, representation=representation, atol=atol)

    def up(
        self,
        position: Real | Iterable[Real] | Multivector,
        *coordinates: Real,
        expr: bool | None = None,
        expression_form: CGAExpressionForm | None = None,
    ) -> Multivector:
        """Embed a point from positional coordinates, an iterable, or a Euclidean vector."""
        tracking = self._resolve_expr(expr)
        x = self.euclidean_vector(
            self._position_input(position, coordinates),
            expr=tracking,
        )
        result = self._embed(x, tracking=tracking)
        return self._semantic(
            result,
            "up",
            x,
            expression_form=expression_form,
            tracking=tracking if expr is not None or self._expr else None,
            origin=self._role(self._origin_ref),
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
            self._algebra.pseudoscalar(expr=False),
            name="weighted radius norm",
            atol=atol,
        )
        denominator = self._round_weight_magnitude(value, atol=atol)
        result = self._algebra.scalar(numerator / denominator, expr=False)
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
    cen = center
    con = container
    par = partner
    project = projection

    def _scalar_norm_root(self, value: Multivector, *, name: str, atol: float) -> Multivector:
        if not is_scalar(value, atol=atol):
            raise ValueError(f"{name} squared must be scalar")
        coefficient = float(value.coefficient(0))
        scale = max(1.0, abs(coefficient))
        if coefficient < -atol * scale:
            raise ValueError(f"{name} is not real")
        return self._algebra.scalar(float(np.sqrt(max(0.0, coefficient))), expr=False)

    def _antiscalar_norm_root(self, value: Multivector, *, name: str, atol: float) -> Multivector:
        basis = self._algebra.pseudoscalar(expr=False)
        coefficient = self._blade_magnitude(value, basis, name=f"{name} squared", atol=atol)
        scale = max(1.0, abs(coefficient))
        if coefficient < -atol * scale:
            raise ValueError(f"{name} is not real")
        return float(np.sqrt(max(0.0, coefficient))) * basis

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
        basis = complement(self._algebra.blade(self._infinity_ref, expr=False))
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

    @staticmethod
    def _position_input(
        position: Real | Iterable[Real] | Multivector,
        coordinates: tuple[Real, ...],
    ) -> Iterable[Real] | Multivector:
        """Normalize the point-factory input grammar without changing its values."""
        if not coordinates and not isinstance(position, Real):
            return cast(Iterable[Real] | Multivector, position)

        values = (position, *coordinates)
        if any(isinstance(value, (bool, np.bool_)) for value in values):
            raise TypeError("point coordinates must be real numbers, not booleans")
        if any(not isinstance(value, Real) for value in values):
            raise TypeError(
                "point input must be real positional coordinates, one coordinate iterable, or one Euclidean multivector"
            )
        return cast(tuple[Real, ...], values)

    def _require_euclidean_vector(self, value: Multivector, *, atol: float = 1e-12) -> None:
        if value.homogeneous_grade(atol=atol) not in {None, 1}:
            raise ValueError("expected a vector in the embedded Euclidean subspace")
        allowed = {ref.mask for ref in self._base_refs}
        for mask, coefficient in enumerate(value.data):
            if mask not in allowed and abs(float(coefficient)) > atol:
                raise ValueError("expected a vector in the embedded Euclidean subspace")

    def _validate_metric(self) -> float:
        return self._conformal_metric(np.eye(self.spatial_dim))


def _is_vector_ref(ref: BladeRef) -> bool:
    return ref.mask > 0 and ref.mask.bit_count() == 1


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
