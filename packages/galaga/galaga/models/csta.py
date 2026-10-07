"""Validated conformal spacetime geometry over a ``(+---)`` base metric."""

from __future__ import annotations

import math
from collections.abc import Iterable
from dataclasses import dataclass, replace
from numbers import Real
from types import MappingProxyType
from typing import Literal, cast

import numpy as np

from ..blades import BladeRef
from ..expression import Call, Expr, Symbol
from ..facade import Algebra, Multivector, outer_product, right_hodge_dual, scalar_product, squared
from .units import CoordinateUnits, SpacetimeUnits, normalize_coordinate_units

CausalKind = Literal["timelike", "null", "spacelike"]
Representation = Literal["auto", "direct", "dual"]
CSTAExpressionForm = Literal["operator", "expanded"]


@dataclass(frozen=True, slots=True)
class CSTAClassification:
    """Structural and causal classification of one CSTA multivector."""

    kind: str
    grade: int | None
    representation: str | None
    simple: bool | None
    finite: bool | None
    causal: CausalKind | None = None
    properties: tuple[tuple[str, object], ...] = ()


class ConformalSpacetimeModel:
    """Conformal spacetime with a normalized ``(+---)`` base metric.

    Numeric coordinates default to natural units. ``units="si"`` selects
    seconds/metres, or use ``(time_unit, distance_unit)``. One natural time
    unit is ``time_scale_seconds`` seconds (default 1); its length unit is
    c times that duration. ``unit_scale`` accepts a reusable SpacetimeUnits
    backend, including a scale selected by proper acceleration.
    """

    __slots__ = (
        "_algebra",
        "_base_refs",
        "_expr",
        "_expression_form",
        "_infinity_ref",
        "_null_pair",
        "_origin_ref",
        "_unit_scale",
        "_units",
    )

    def __init__(
        self,
        algebra: Algebra,
        *,
        expr: bool | None = None,
        expression_form: CSTAExpressionForm = "operator",
        units: CoordinateUnits = "natural",
        time_scale_seconds: float | None = None,
        unit_scale: SpacetimeUnits | None = None,
    ) -> None:
        if not isinstance(algebra, Algebra):
            raise TypeError("algebra must be a galaga Algebra")
        if expr is None:
            expr = algebra.expr
        if not isinstance(expr, bool):
            raise TypeError("expr must be a boolean")
        selected_form = _expression_form(expression_form)
        if unit_scale is not None and time_scale_seconds is not None:
            raise ValueError("choose unit_scale or time_scale_seconds, not both")
        if unit_scale is not None and not isinstance(unit_scale, SpacetimeUnits):
            raise TypeError("unit_scale must be SpacetimeUnits")
        self._unit_scale = (
            unit_scale
            if unit_scale is not None
            else SpacetimeUnits(1.0 if time_scale_seconds is None else time_scale_seconds)
        )
        self._units = normalize_coordinate_units(units)
        model = algebra.model
        if model is None or model.id != "csta-mostly-minus":
            raise ValueError("ConformalSpacetimeModel requires Algebra(config=presets.csta())")

        roles = MappingProxyType(dict(model.roles))
        try:
            base_refs = (roles["time"], *(roles[f"space_{index}"] for index in range(1, 4)))
            origin_ref = roles["origin"]
            infinity_ref = roles["infinity"]
        except KeyError as error:  # pragma: no cover - malformed custom ModelConfig
            raise ValueError("CSTA roles must include time, space_1..3, origin, and infinity") from error
        refs = (*base_refs, origin_ref, infinity_ref)
        if len({ref.mask for ref in refs}) != 6 or any(not _is_vector_ref(ref) for ref in refs):
            raise ValueError("CSTA roles must identify six distinct basis vectors")

        self._algebra = algebra
        self._base_refs = base_refs
        self._expr = expr
        self._expression_form = selected_form
        self._origin_ref = origin_ref
        self._infinity_ref = infinity_ref
        self._null_pair = self._validate_metric()

    @property
    def algebra(self) -> Algebra:
        return self._algebra

    @property
    def expr(self) -> bool:
        return self._expr

    @property
    def expression_form(self) -> CSTAExpressionForm:
        """Default provenance form for model constructions."""

        return self._expression_form

    def with_expression_form(self, expression_form: CSTAExpressionForm) -> ConformalSpacetimeModel:
        """Return a model view with a new default, sharing the same algebra."""

        return type(self)(
            self._algebra,
            expr=self._expr,
            expression_form=expression_form,
            units=self._units,
            unit_scale=self._unit_scale,
        )

    @property
    def units(self) -> Literal["natural"] | tuple[str, str]:
        """Default units for numeric coordinate input and output."""
        return self._units

    @property
    def unit_scale(self) -> SpacetimeUnits:
        """Conversion backend and physical interpretation of natural coordinates."""
        return self._unit_scale

    def time_in(self, value: float, unit: str = "s") -> float:
        """Convert a natural duration to seconds or another time unit."""
        return self._unit_scale.time_in(value, unit)

    def distance_in(self, value: float, unit: str = "m") -> float:
        return self._unit_scale.distance_in(value, unit)

    def speed_in(self, value: float, unit: str = "m/s") -> float:
        """Convert a fraction of c to physical coordinate speed."""
        return self._unit_scale.speed_in(value, unit)

    def acceleration_in(self, value: float, unit: str = "m/s^2") -> float:
        return self._unit_scale.acceleration_in(value, unit)

    def format_time(self, value: float, unit: str = "auto", *, precision: int = 3) -> str:
        return self._unit_scale.format_time(value, unit, precision=precision)

    def format_distance(self, value: float, unit: str = "auto", *, precision: int = 3) -> str:
        return self._unit_scale.format_distance(value, unit, precision=precision)

    def format_speed(self, value: float, unit: str = "auto", *, precision: int = 3) -> str:
        return self._unit_scale.format_speed(value, unit, precision=precision)

    def format_acceleration(self, value: float, unit: str = "g", *, precision: int = 3) -> str:
        return self._unit_scale.format_acceleration(value, unit, precision=precision)

    @property
    def spatial_dim(self) -> int:
        return 3

    @property
    def spacetime_dim(self) -> int:
        return 4

    @property
    def null_pair(self) -> float:
        return self._null_pair

    @property
    def origin(self) -> Multivector:
        return self._algebra.blade(self._origin_ref, expr=self._expr)

    @property
    def infinity(self) -> Multivector:
        return self._algebra.blade(self._infinity_ref, expr=self._expr)

    def spacetime_basis_vectors(self, *, expr: bool | None = None) -> tuple[Multivector, ...]:
        tracking = self._resolve_expr(expr)
        return tuple(self._algebra.blade(ref, expr=tracking) for ref in self._base_refs)

    def spacetime_vector(
        self,
        value: Iterable[Real | float] | Multivector,
        *,
        expr: bool | None = None,
        units: CoordinateUnits | None = None,
    ) -> Multivector:
        tracking = self._resolve_expr(expr)
        if isinstance(value, Multivector):
            if units is not None and normalize_coordinate_units(units) != "natural":
                raise ValueError("multivectors already use natural coordinates; units applies to numeric input")
            self._check_value(value)
            allowed = {ref.mask for ref in self._base_refs}
            if any(coefficient != 0.0 and mask not in allowed for mask, coefficient in enumerate(value.data)):
                raise ValueError("value must be a spacetime vector")
            if not tracking:
                return value.without_expr()
            return value.with_expr() if value.expr is None else value

        coordinates = _coordinates(value, expected=4)
        time_factor, distance_factor = self._unit_scale.coordinate_factors(self._units if units is None else units)
        coordinates = _coordinates(
            (coordinates[0] * time_factor, *(coordinate * distance_factor for coordinate in coordinates[1:])),
            expected=4,
        )
        data = np.zeros(self._algebra.dim)
        for coordinate, ref in zip(coordinates, self._base_refs, strict=True):
            data[ref.mask] = ref.orientation * coordinate
        return self._algebra.multivector(data, expr=tracking)

    def up(
        self,
        position: Real | float | Iterable[Real | float] | Multivector,
        *coordinates: Real | float,
        expr: bool | None = None,
        expression_form: CSTAExpressionForm | None = None,
        units: CoordinateUnits | None = None,
    ) -> Multivector:
        """Embed a spacetime event as a null conformal vector."""

        tracking = self._resolve_expr(expr)
        x = self.spacetime_vector(_position_input(position, coordinates), expr=tracking, units=units)
        origin = self._algebra.blade(self._origin_ref, expr=tracking)
        infinity = self._algebra.blade(self._infinity_ref, expr=tracking)
        result = origin + x + squared(x) * infinity / (-2.0 * self._null_pair)
        return self._semantic(
            result,
            "up",
            x,
            expression_form=expression_form,
            tracking=tracking,
            **self._embedding_roles(),
        )

    def event(
        self,
        position: Real | float | Iterable[Real | float] | Multivector,
        *coordinates: Real | float,
        expr: bool | None = None,
        expression_form: CSTAExpressionForm | None = None,
        units: CoordinateUnits | None = None,
    ) -> Multivector:
        """Construct an event in ``(t, x, y, z)`` order.

        ``units`` overrides the model's numeric coordinate units for this
        call. Multivector inputs are already in natural coordinates.
        Operator provenance records physical coordinates and their units.
        """

        tracking = self._resolve_expr(expr)
        input_position = _position_input(position, coordinates)
        raw_coordinates = None if isinstance(input_position, Multivector) else _coordinates(input_position, expected=4)
        x = self.spacetime_vector(
            input_position if raw_coordinates is None else raw_coordinates, expr=tracking, units=units
        )
        result = self.up(x, expr=tracking, expression_form="expanded")
        if isinstance(position, Multivector):
            return self._semantic(
                result,
                "event_vector",
                x,
                expression_form=expression_form,
                tracking=tracking,
                **self._embedding_roles(),
            )
        if raw_coordinates is None:  # pragma: no cover - vector input returned above
            raise RuntimeError("event coordinates were not resolved")
        values = tuple(self._algebra.scalar(coordinate, expr=tracking) for coordinate in raw_coordinates)
        selected_units = self._units if units is None else normalize_coordinate_units(units)
        unit_parameters: dict[str, object] = {}
        if selected_units != "natural":
            unit_parameters = {
                "coordinate_scale": self._unit_scale.coordinate_factors(selected_units),
                "units": selected_units,
            }
        return self._semantic(
            result,
            "event",
            *values,
            expression_form=expression_form,
            tracking=tracking,
            basis=tuple((ref.mask, ref.orientation) for ref in self._base_refs),
            **self._embedding_roles(),
            **unit_parameters,
        )

    point = event

    def weight(self, value: Multivector) -> float:
        """Return a conformal vector's homogeneous origin coefficient."""

        self._require_vector(value)
        return float(scalar_product(value, self.infinity)) / self._null_pair

    def homogenize(self, value: Multivector, *, atol: float = 1e-12) -> Multivector:
        tolerance = _tolerance(atol)
        weight = self.weight(value)
        if abs(weight) <= tolerance:
            raise ValueError("cannot homogenize a conformal vector with zero weight")
        return value / weight

    def down(self, value: Multivector, *, atol: float = 1e-12) -> Multivector:
        """Extract the spacetime vector from a finite conformal vector."""

        normalized = self.homogenize(value, atol=atol)
        data = np.zeros(self._algebra.dim)
        for ref in self._base_refs:
            data[ref.mask] = normalized.coefficient(ref.mask)
        return self._algebra.multivector(data, expr=False)

    def coordinates(
        self,
        value: Multivector,
        *,
        atol: float = 1e-12,
        units: CoordinateUnits | None = None,
    ) -> np.ndarray:
        """Recover coordinates in model units, or the units selected for this call.

        ``down()`` and algebraic invariants always retain natural coordinates.
        """
        center = self.down(value, atol=atol)
        result = np.array(
            [ref.orientation * center.coefficient(ref.mask) for ref in self._base_refs],
            dtype=float,
        )
        time_factor, distance_factor = self._unit_scale.coordinate_factors(self._units if units is None else units)
        with np.errstate(over="ignore", invalid="ignore"):
            result /= np.array((time_factor, distance_factor, distance_factor, distance_factor))
        if not np.all(np.isfinite(result)):
            raise ValueError("converted coordinates must be finite")
        result.setflags(write=False)
        return result

    def velocity_between(self, left: Multivector, right: Multivector, *, unit: str = "m/s") -> np.ndarray:
        """Average coordinate velocity between events in the model's inertial frame."""
        displacement = self.coordinates(right, units="natural") - self.coordinates(left, units="natural")
        if displacement[0] == 0:
            raise ValueError("coordinate velocity requires nonzero time separation")
        beta = displacement[1:] / displacement[0]
        velocity = np.array([self.speed_in(float(component), unit) for component in beta])
        velocity.setflags(write=False)
        return velocity

    def speed_between(self, left: Multivector, right: Multivector, *, unit: str = "m/s") -> float:
        """Magnitude of average coordinate velocity; this is not proper velocity."""
        beta = self.velocity_between(left, right, unit="c")
        return self.speed_in(float(np.linalg.norm(beta)), unit)

    def separation_squared(self, left: Multivector, right: Multivector, *, atol: float = 1e-12) -> float:
        """Return the signed Minkowski interval in squared natural units."""

        left_normalized = self.homogenize(left, atol=atol)
        right_normalized = self.homogenize(right, atol=atol)
        return -2.0 * float(scalar_product(left_normalized, right_normalized))

    def causal_kind(self, squared_interval: object, *, atol: float = 1e-12) -> CausalKind:
        """Classify a signed interval under the ``(+---)`` convention."""

        tolerance = _tolerance(atol)
        if not isinstance(squared_interval, Real) or isinstance(squared_interval, bool):
            raise TypeError("squared_interval must be a real number")
        value = float(squared_interval)
        if not math.isfinite(value):
            raise ValueError("squared_interval must be finite")
        if value > tolerance:
            return "timelike"
        if value < -tolerance:
            return "spacelike"
        return "null"

    def event_pair(
        self,
        left: Multivector,
        right: Multivector,
        *,
        expression_form: CSTAExpressionForm | None = None,
    ) -> Multivector:
        self._check_pair(left, right)
        tracked_left = left.with_expr() if self._expr and left.expr is None else left
        tracked_right = right.with_expr() if self._expr and right.expr is None else right
        return self._semantic(
            outer_product(tracked_left, tracked_right), "event_pair", left, right, expression_form=expression_form
        )

    def flat_line(
        self,
        left: Multivector,
        right: Multivector,
        *,
        expression_form: CSTAExpressionForm | None = None,
    ) -> Multivector:
        self._check_pair(left, right)
        return self._semantic(
            outer_product(left, right, self.infinity),
            "flat_line",
            left,
            right,
            expression_form=expression_form,
            infinity=(self._infinity_ref.mask, self._infinity_ref.orientation),
        )

    def signed_round(
        self,
        center: Real | float | Iterable[Real | float] | Multivector,
        radius_squared: Real,
        *coordinates: Real | float,
        expr: bool | None = None,
        expression_form: CSTAExpressionForm | None = None,
        units: CoordinateUnits | None = None,
    ) -> Multivector:
        """Return an IPNS signed round centered on an event.

        Numeric centres use model units or the per-call override. The signed
        ``radius_squared`` is in the square of that policy's distance unit;
        a multivector centre is already natural, while the radius still uses
        the selected policy. Classification reports natural invariants.
        """

        if not isinstance(radius_squared, Real) or isinstance(radius_squared, bool):
            raise TypeError("radius_squared must be a real number")
        radius = float(radius_squared)
        if not math.isfinite(radius):
            raise ValueError("radius_squared must be finite")
        tracking = self._resolve_expr(expr)
        x = self.spacetime_vector(_position_input(center, coordinates), expr=tracking, units=units)
        _, length_factor = self._unit_scale.coordinate_factors(self._units if units is None else units)
        radius *= length_factor * length_factor
        if not math.isfinite(radius):
            raise ValueError("converted radius_squared must be finite")
        event = self.up(x, expr=tracking, expression_form="expanded")
        infinity = self._algebra.blade(self._infinity_ref, expr=tracking)
        result = event + radius * infinity / (2.0 * self._null_pair)
        return self._semantic(
            result,
            "signed_round",
            x,
            self._algebra.scalar(radius, expr=tracking),
            expression_form=expression_form,
            tracking=tracking,
            **self._embedding_roles(),
        )

    def classify(
        self,
        value: Multivector,
        *,
        representation: Representation = "auto",
        atol: float = 1e-9,
    ) -> CSTAClassification:
        """Classify a CSTA value using grade, incidence, simplicity, and metric invariants."""

        self._check_value(value)
        tolerance = _tolerance(atol)
        if representation not in {"auto", "direct", "dual"}:
            raise ValueError("representation must be 'auto', 'direct', or 'dual'")
        if _is_zero(value, tolerance):
            return CSTAClassification("zero", None, None, None, None)

        normalized = _normalized(value)
        grade = normalized.homogeneous_grade(atol=tolerance)
        if grade is None:
            return CSTAClassification("general", None, None, None, None)
        if grade == 0:
            return CSTAClassification("scalar", 0, None, True, None)
        if grade == 6:
            return CSTAClassification("pseudoscalar", 6, None, True, None)

        if representation == "dual" and grade > 1:
            direct = self.classify(right_hodge_dual(normalized), representation="direct", atol=tolerance)
            return replace(direct, grade=grade, representation="dual")

        simple = self._is_simple(normalized, grade, tolerance)
        flat = _is_zero(outer_product(normalized, self.infinity.without_expr()), tolerance)
        if not simple:
            return CSTAClassification("general", grade, representation, False, None, properties=(("flat", flat),))
        if grade == 1:
            return self._classify_vector(normalized, representation, flat, tolerance)
        if flat:
            kinds = {2: "flat point", 3: "flat line", 4: "flat 2-plane", 5: "flat hyperplane"}
            causal = self._flat_line_causal(normalized, tolerance) if grade == 3 else None
            return CSTAClassification(kinds[grade], grade, "direct", True, grade != 1, causal)

        if grade == 5:
            dual_vector = right_hodge_dual(normalized)
            classified = self._classify_vector(dual_vector, "dual", False, tolerance)
            return replace(classified, grade=5, representation="direct")

        if grade == 3:
            return self._classify_round_curve(normalized, tolerance)

        direct_kinds = {2: "event pair", 3: "round 2-object", 4: "round 3-object"}
        carrier = outer_product(normalized, self.infinity.without_expr())
        causal = self._flat_line_causal(carrier, tolerance) if grade == 2 else None
        return CSTAClassification(direct_kinds[grade], grade, "direct", True, True, causal)

    def _classify_vector(
        self,
        value: Multivector,
        representation: Representation,
        flat: bool,
        atol: float,
    ) -> CSTAClassification:
        if flat:
            return CSTAClassification("point at infinity", 1, "direct", True, False)
        weight = self.weight(value)
        if abs(weight) <= atol:
            return CSTAClassification("dual hyperplane", 1, "dual", True, None)
        signed_radius = float(squared(value)) / (weight * weight)
        causal = self.causal_kind(signed_radius, atol=atol)
        properties = (("signed_radius_squared", signed_radius),)
        if representation == "direct":
            kind = "event" if causal == "null" else "invalid direct point"
            return CSTAClassification(kind, 1, "direct", True, True, None, properties)
        round_kinds = {
            "timelike": "proper-time hyperboloid",
            "null": "light cone",
            "spacelike": "proper-distance hyperboloid",
        }
        if representation == "dual":
            return CSTAClassification(round_kinds[causal], 1, "dual", True, True, causal, properties)
        kind = "event or light cone" if causal == "null" else round_kinds[causal]
        selected = "ambiguous" if causal == "null" else "dual"
        selected_causal = None if causal == "null" else causal
        return CSTAClassification(kind, 1, selected, True, True, selected_causal, properties)

    def _is_simple(self, value: Multivector, grade: int, atol: float) -> bool:
        rank = int(np.linalg.matrix_rank(self._wedge_matrix(value), tol=atol))
        return rank == self._algebra.n - grade

    def _role_vectors(self) -> tuple[Multivector, ...]:
        return (*self.spacetime_basis_vectors(expr=False), self.origin.without_expr(), self.infinity.without_expr())

    def _wedge_matrix(self, value: Multivector) -> np.ndarray:
        return np.column_stack([outer_product(vector, value).data for vector in self._role_vectors()])

    def _classify_round_curve(self, value: Multivector, atol: float) -> CSTAClassification:
        # The kernel of v -> v∧B is the three-dimensional vector span of B.
        _, _, blade_vh = np.linalg.svd(self._wedge_matrix(value), full_matrices=False)
        span = blade_vh[-3:].T
        weights = span[len(self._base_refs)]
        weight_squared = float(weights @ weights)
        if weight_squared <= atol * atol:
            return CSTAClassification("round 2-object", 3, "direct", True, False)

        # Weight-zero vectors span the affine carrier directions. Their metric
        # determines whether the section is elliptic, hyperbolic, or degenerate.
        _, _, weight_vh = np.linalg.svd(weights.reshape(1, -1), full_matrices=True)
        directions = span @ weight_vh[1:].T
        vectors = self._role_vectors()
        gram = np.array([[float(scalar_product(left, right)) for right in vectors] for left in vectors])
        induced = directions.T @ gram @ directions
        eigenvalues = np.linalg.eigvalsh(induced)
        inertia = (
            int(np.count_nonzero(eigenvalues > atol)),
            int(np.count_nonzero(eigenvalues < -atol)),
            int(np.count_nonzero(np.abs(eigenvalues) <= atol)),
        )
        properties: tuple[tuple[str, object], ...] = (("carrier_inertia", inertia),)
        if inertia[2]:
            return CSTAClassification("round 2-object", 3, "direct", True, True, properties=properties)

        # Complete the restricted quadratic form by locating its stationary
        # weight-one vector. Its negative square is the signed radius squared.
        anchor = span @ weights / weight_squared
        center = anchor - directions @ np.linalg.solve(induced, directions.T @ gram @ anchor)
        radius_squared = float(-center @ gram @ center)
        radius_kind = self.causal_kind(radius_squared, atol=atol)
        properties += (
            ("center", tuple(float(coordinate) for coordinate in center[: len(self._base_refs)])),
            ("signed_radius_squared", radius_squared),
        )
        if inertia == (1, 1, 0):
            kind = "null line pair" if radius_kind == "null" else "hyperbola"
            tangent_kinds: dict[CausalKind, CausalKind] = {
                "timelike": "spacelike",
                "spacelike": "timelike",
                "null": "null",
            }
            return CSTAClassification(kind, 3, "direct", True, True, tangent_kinds[radius_kind], properties)
        if inertia == (0, 2, 0):
            kinds = {"spacelike": "circle", "timelike": "imaginary circle", "null": "point circle"}
            causal: CausalKind | None = "spacelike" if radius_kind == "spacelike" else None
            return CSTAClassification(kinds[radius_kind], 3, "direct", True, True, causal, properties)
        return CSTAClassification("round 2-object", 3, "direct", True, True, properties=properties)

    def _flat_line_causal(self, value: Multivector, atol: float) -> CausalKind | None:
        direction = []
        origin = self.origin.without_expr()
        infinity = self.infinity.without_expr()
        for vector in self.spacetime_basis_vectors(expr=False):
            template = outer_product(origin, vector, infinity)
            masks = np.flatnonzero(np.abs(template.data) > atol)
            if len(masks) != 1:
                return None
            mask = int(masks[0])
            direction.append(value.data[mask] / template.data[mask])
        vector = self.spacetime_vector(direction, expr=False, units="natural")
        return self.causal_kind(float(squared(vector)), atol=atol)

    def _validate_metric(self) -> float:
        indices = tuple(_vector_index(ref) for ref in (*self._base_refs, self._origin_ref, self._infinity_ref))
        gram = self._algebra.gram[np.ix_(indices, indices)]
        expected = np.zeros((6, 6))
        expected[:4, :4] = np.diag((1.0, -1.0, -1.0, -1.0))
        expected[4, 5] = expected[5, 4] = -1.0
        if not np.array_equal(gram, expected):
            raise ValueError("CSTA roles require a (+---) base and origin·infinity == -1")
        return -1.0

    def _resolve_expr(self, value: bool | None) -> bool:
        if value is None:
            return self._expr
        if not isinstance(value, bool):
            raise TypeError("expr must be a boolean")
        return value

    def _embedding_roles(self) -> dict[str, tuple[int, int]]:
        return {
            "origin": (self._origin_ref.mask, self._origin_ref.orientation),
            "infinity": (self._infinity_ref.mask, self._infinity_ref.orientation),
        }

    def _semantic(
        self,
        result: Multivector,
        operation_id: str,
        *values: Multivector,
        expression_form: CSTAExpressionForm | None = None,
        tracking: bool | None = None,
        **parameters: object,
    ) -> Multivector:
        selected = self._expression_form if expression_form is None else _expression_form(expression_form)
        if tracking is False:
            return result.without_expr()
        if selected == "expanded":
            return result
        if (
            tracking is not True
            and not self._expr
            and all(value.expr is None and value.name is None for value in values)
        ):
            return result
        return result.with_expr(Call(operation_id, tuple(_expression_operand(value) for value in values), parameters))

    def _check_value(self, value: Multivector) -> None:
        if not isinstance(value, Multivector):
            raise TypeError("value must be a Galaga Multivector")
        if value.algebra is not self._algebra:
            raise ValueError("value must belong to the model algebra")

    def _check_pair(self, left: Multivector, right: Multivector) -> None:
        self._check_value(left)
        self._check_value(right)

    def _require_vector(self, value: Multivector) -> None:
        self._check_value(value)
        if value.homogeneous_grade() != 1:
            raise ValueError("value must be a conformal vector")


def _is_vector_ref(ref: BladeRef) -> bool:
    return ref.mask.bit_count() == 1


def _expression_form(value: object) -> CSTAExpressionForm:
    if not isinstance(value, str):
        raise TypeError("expression_form must be a string")
    if value not in {"operator", "expanded"}:
        raise ValueError("expression_form must be 'operator' or 'expanded'")
    return cast(CSTAExpressionForm, value)


def _expression_operand(value: Multivector) -> Expr:
    if value.name is not None:
        return Symbol(value.name)
    expression = value.expr if value.expr is not None else value.with_expr().expr
    if expression is None:  # pragma: no cover - with_expr always supplies provenance
        raise RuntimeError("failed to construct expression provenance")
    return expression


def _vector_index(ref: BladeRef) -> int:
    if not _is_vector_ref(ref):
        raise ValueError("model role must refer to a basis vector")
    return ref.mask.bit_length() - 1


def _coordinates(value: Iterable[Real | float], *, expected: int) -> tuple[float, ...]:
    try:
        coordinates = tuple(value)
    except TypeError as error:
        raise TypeError("coordinates must be an iterable of real numbers") from error
    if len(coordinates) != expected:
        raise ValueError(f"expected {expected} coordinates")
    if any(not isinstance(item, Real) or isinstance(item, bool) for item in coordinates):
        raise TypeError("coordinates must be real numbers")
    normalized = tuple(float(item) for item in coordinates)
    if any(not math.isfinite(item) for item in normalized):
        raise ValueError("coordinates must be finite")
    return normalized


def _position_input(
    position: Real | float | Iterable[Real | float] | Multivector,
    coordinates: tuple[Real | float, ...],
) -> Iterable[Real | float] | Multivector:
    if isinstance(position, Multivector):
        if coordinates:
            raise ValueError("a spacetime vector cannot be combined with positional coordinates")
        return position
    if isinstance(position, (Real, float)):
        if isinstance(position, bool):
            raise TypeError("coordinates must be real numbers")
        return (position, *coordinates)
    if coordinates:
        raise ValueError("an iterable position cannot be combined with positional coordinates")
    return position


def _tolerance(value: object) -> float:
    if not isinstance(value, Real) or isinstance(value, bool):
        raise TypeError("atol must be a real number")
    tolerance = float(value)
    if not math.isfinite(tolerance) or tolerance < 0:
        raise ValueError("atol must be finite and non-negative")
    return tolerance


def _is_zero(value: Multivector, atol: float) -> bool:
    return not np.any(np.abs(value.data) > atol)


def _normalized(value: Multivector) -> Multivector:
    scale = float(np.max(np.abs(value.data)))
    return value if scale == 0.0 else value.algebra.multivector(value.data / scale, expr=False)


__all__ = ["CSTAClassification", "CSTAExpressionForm", "CausalKind", "ConformalSpacetimeModel"]
