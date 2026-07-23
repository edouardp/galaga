"""Point-based rigid/projective geometry over Lengyel's RGA convention.

The generic Galaga facade owns products, complements, duals, and numeric
functions.  :class:`RigidModel` adds only semantics that depend on identifying
the Euclidean basis and the null projective basis vector: homogeneous points,
attitude, paired norms, projective measurements, projections, and geometric
constraint checks.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Iterable
from numbers import Real
from types import MappingProxyType

import numpy as np

from .blades import BladeRef
from .expression import Call, Expr, Symbol
from .facade import (
    Algebra,
    Multivector,
    antidot_product,
    antiwedge,
    complement,
    is_scalar,
    metric_inner_product,
    outer_product,
    right_hodge_dual,
    right_weight_dual,
    scalar_product,
    squared,
)


class RigidModel:
    """Validated point-based 3D RGA semantics over ``Algebra(config=p_rga())``."""

    __slots__ = (
        "_algebra",
        "_antiscalar_ref",
        "_euclidean_refs",
        "_expr",
        "_projective_ref",
    )

    def __init__(self, algebra: Algebra, *, expr: bool = False) -> None:
        if not isinstance(algebra, Algebra):
            raise TypeError("algebra must be a galaga Algebra")
        _require_expr_flag(expr)
        model = algebra.model
        if model is None or model.id != "lengyel-rga":
            raise ValueError("RigidModel requires Algebra(config=p_rga())")

        roles = MappingProxyType(dict(model.roles))
        euclidean_refs = _ordered_euclidean_roles(roles)
        try:
            projective_ref = roles["projective"]
            antiscalar_ref = roles["antiscalar"]
        except KeyError as error:  # pragma: no cover - malformed custom ModelConfig
            raise ValueError("RGA model roles must include projective and antiscalar") from error

        if len(euclidean_refs) != 3:
            raise ValueError("RigidModel currently requires exactly three Euclidean roles")
        vector_refs = (*euclidean_refs, projective_ref)
        if len(vector_refs) != algebra.n or any(not _is_vector_ref(ref) for ref in vector_refs):
            raise ValueError("RGA vector roles must account for all four basis vectors")
        if len({ref.mask for ref in vector_refs}) != len(vector_refs):
            raise ValueError("RGA vector roles must refer to distinct basis vectors")
        if antiscalar_ref.mask != algebra.dim - 1 or antiscalar_ref.orientation != 1:
            raise ValueError("RGA antiscalar role must refer to the positive top-grade basis blade")

        self._algebra = algebra
        self._antiscalar_ref = antiscalar_ref
        self._euclidean_refs = euclidean_refs
        self._expr = expr
        self._projective_ref = projective_ref
        self._validate_metric()

    @property
    def algebra(self) -> Algebra:
        """The facade algebra carrying the RGA numeric and presentation policy."""
        return self._algebra

    @property
    def expr(self) -> bool:
        """Whether model-owned factories track expression provenance by default."""
        return self._expr

    @property
    def spatial_dim(self) -> int:
        """The Euclidean dimension represented by the projective algebra."""
        return len(self._euclidean_refs)

    @property
    def projective(self) -> Multivector:
        """The null projective vector ``e4``."""
        return self._algebra.blade(self._projective_ref, expr=self._expr)

    @property
    def antiscalar(self) -> Multivector:
        """Lengyel's antiscalar ``𝟙``."""
        return self._algebra.blade(self._antiscalar_ref, expr=self._expr)

    @property
    def horizon(self) -> Multivector:
        """The projective horizon, the complement of ``e4``."""
        return complement(self.projective)

    def euclidean_basis_vectors(self, *, expr: bool | None = None) -> tuple[Multivector, ...]:
        """Return ``e1, e2, e3`` with the selected expression policy."""
        tracking = self._resolve_expr(expr)
        return tuple(self._algebra.blade(ref, expr=tracking) for ref in self._euclidean_refs)

    def euclidean_vector(
        self,
        value: Iterable[Real] | Multivector,
        *,
        expr: bool | None = None,
    ) -> Multivector:
        """Construct or validate a vector in the Euclidean three-space subspace."""
        tracking = self._resolve_expr(expr)
        if isinstance(value, Multivector):
            self._check_value(value)
            self._require_euclidean_vector(value)
            return value.with_expr() if tracking and value.expr is None else value

        coordinates = _coordinates(value, expected=self.spatial_dim)
        data = np.zeros(self._algebra.dim)
        for coordinate, ref in zip(coordinates, self._euclidean_refs, strict=True):
            data[ref.mask] = ref.orientation * coordinate
        result = self._algebra.multivector(data)
        return result.with_expr() if tracking else result

    def point(
        self,
        position: Iterable[Real] | Multivector,
        *,
        weight: Real = 1.0,
        expr: bool | None = None,
    ) -> Multivector:
        r"""Construct the homogeneous point ``x + weight*e4``."""
        tracking = self._resolve_expr(expr)
        homogeneous_weight = _finite_real(weight, name="point weight")
        x = self.euclidean_vector(position, expr=tracking)
        projective = self._algebra.blade(self._projective_ref, expr=tracking)
        return x + homogeneous_weight * projective

    def point_weight(self, value: Multivector) -> Multivector:
        """Return a point's scalar homogeneous weight."""
        self._require_point(value)
        return self.attitude(value)

    def homogenize(self, value: Multivector, *, atol: float = 1e-12) -> Multivector:
        """Scale a finite point so its projective coefficient is one."""
        _require_nonnegative_tolerance(atol)
        weight = self.point_weight(value)
        coefficient = float(weight)
        if abs(coefficient) <= atol:
            raise ValueError("cannot homogenize a point with zero weight")
        return value / coefficient

    def coordinates(self, value: Multivector, *, atol: float = 1e-12) -> np.ndarray:
        """Return immutable Euclidean coordinates for a finite point."""
        normalized = self.homogenize(value, atol=atol)
        result = np.array(
            [ref.orientation * normalized.coefficient(ref.mask) for ref in self._euclidean_refs],
            dtype=float,
        )
        result.setflags(write=False)
        return result

    def attitude(self, value: Multivector) -> Multivector:
        """Extract a geometry's purely directional object."""
        self._require_geometry(value)
        result = antiwedge(value, self.horizon)
        return self._semantic(
            result,
            "attitude",
            value,
            origin=self._role(self._projective_ref),
        )

    def bulk_norm(self, value: Multivector, *, atol: float = 1e-12) -> Multivector:
        """Return ``sqrt(value • value)`` as a scalar."""
        _require_nonnegative_tolerance(atol)
        self._check_value(value)
        result = self._scalar_norm_root(
            metric_inner_product(value, value),
            name="bulk norm",
            atol=atol,
        )
        return self._semantic(result, "bulk_norm", value, atol=atol)

    def weight_norm(self, value: Multivector, *, atol: float = 1e-12) -> Multivector:
        """Return ``sqrt(value ∘ value)`` as an antiscalar."""
        _require_nonnegative_tolerance(atol)
        self._check_value(value)
        result = self._antiscalar_norm_root(
            antidot_product(value, value),
            name="weight norm",
            atol=atol,
        )
        return self._semantic(result, "weight_norm", value, atol=atol)

    def geometric_norm(self, value: Multivector, *, atol: float = 1e-12) -> Multivector:
        """Return the scalar bulk norm plus antiscalar weight norm."""
        _require_nonnegative_tolerance(atol)
        result = self.bulk_norm(value, atol=atol) + self.weight_norm(value, atol=atol)
        return self._semantic(result, "geometric_norm", value, atol=atol)

    def unitize(self, value: Multivector, *, atol: float = 1e-12) -> Multivector:
        """Scale a projective element until its weight norm is the unit antiscalar."""
        _require_nonnegative_tolerance(atol)
        weight = self.weight_norm(value, atol=atol)
        magnitude = self._blade_magnitude(
            weight,
            self._algebra.blade(self._antiscalar_ref),
            name="weight norm",
            atol=atol,
        )
        if magnitude <= atol:
            raise ValueError("cannot unitize an element with zero weight norm")
        result = value / magnitude
        return self._semantic(result, "unitize", value, atol=atol)

    def bulk_contraction(self, left: Multivector, right: Multivector) -> Multivector:
        """Return the right bulk contraction ``left ∨ right^★``."""
        self._check_pair(left, right)
        result = antiwedge(left, right_hodge_dual(right))
        return self._semantic(result, "bulk_contraction", left, right)

    def weight_contraction(self, left: Multivector, right: Multivector) -> Multivector:
        """Return the right weight contraction ``left ∨ right^☆``."""
        self._check_pair(left, right)
        result = antiwedge(left, right_weight_dual(right))
        return self._semantic(result, "weight_contraction", left, right)

    def bulk_expansion(self, left: Multivector, right: Multivector) -> Multivector:
        """Return the right bulk expansion ``left ∧ right^★``."""
        self._check_pair(left, right)
        result = outer_product(left, right_hodge_dual(right))
        return self._semantic(result, "bulk_expansion", left, right)

    def weight_expansion(self, left: Multivector, right: Multivector) -> Multivector:
        """Return the right weight expansion ``left ∧ right^☆``."""
        self._check_pair(left, right)
        result = outer_product(left, right_weight_dual(right))
        return self._semantic(result, "weight_expansion", left, right)

    def homogeneous_distance(
        self,
        left: Multivector,
        right: Multivector,
        *,
        atol: float = 1e-12,
    ) -> Multivector:
        """Return Eric Lengyel's projectively weighted Euclidean distance."""
        _require_nonnegative_tolerance(atol)
        self._require_geometry(left)
        self._require_geometry(right)
        join = outer_product(left, right)
        result = self.bulk_norm(self.attitude(join), atol=atol) + self.weight_norm(
            outer_product(left, self.attitude(right)),
            atol=atol,
        )
        return self._semantic(
            result,
            "homogeneous_distance",
            left,
            right,
            projective=self._role(self._projective_ref),
            atol=atol,
        )

    def homogeneous_angle(
        self,
        left: Multivector,
        right: Multivector,
        *,
        atol: float = 1e-12,
    ) -> Multivector:
        """Return the homogeneous cosine of the absolute Euclidean angle."""
        _require_nonnegative_tolerance(atol)
        self._require_geometry(left)
        self._require_geometry(right)
        result = self.bulk_norm(self.weight_contraction(left, right), atol=atol) + antiwedge(
            self.weight_norm(left, atol=atol),
            self.weight_norm(right, atol=atol),
        )
        return self._semantic(result, "homogeneous_angle", left, right, atol=atol)

    def orthogonal_projection(self, value: Multivector, onto: Multivector) -> Multivector:
        """Orthogonally project ``value`` onto ``onto``."""
        self._require_geometry(value)
        self._require_geometry(onto)
        result = antiwedge(onto, self.weight_expansion(value, onto))
        return self._semantic(result, "orthogonal_projection", value, onto)

    def orthogonal_antiprojection(self, value: Multivector, onto: Multivector) -> Multivector:
        """Return the projection dual to :meth:`orthogonal_projection`."""
        self._require_geometry(value)
        self._require_geometry(onto)
        result = outer_product(onto, self.weight_contraction(value, onto))
        return self._semantic(result, "orthogonal_antiprojection", value, onto)

    def central_projection(self, value: Multivector, onto: Multivector) -> Multivector:
        """Centrally project ``value`` onto ``onto`` through the origin."""
        self._require_geometry(value)
        self._require_geometry(onto)
        result = antiwedge(onto, self.bulk_expansion(value, onto))
        return self._semantic(result, "central_projection", value, onto)

    def central_antiprojection(self, value: Multivector, onto: Multivector) -> Multivector:
        """Return the projection dual to :meth:`central_projection`."""
        self._require_geometry(value)
        self._require_geometry(onto)
        result = outer_product(onto, self.bulk_contraction(value, onto))
        return self._semantic(result, "central_antiprojection", value, onto)

    def support(self, value: Multivector) -> Multivector:
        """Return the point on ``value`` nearest the Euclidean origin."""
        self._require_geometry(value)
        result = self.orthogonal_projection(self.projective, value)
        return self._semantic(
            result,
            "support",
            value,
            projective=self._role(self._projective_ref),
        )

    def antisupport(self, value: Multivector) -> Multivector:
        """Return the plane dual to :meth:`support`."""
        self._require_geometry(value)
        result = self.central_antiprojection(self.horizon, value)
        return self._semantic(
            result,
            "antisupport",
            value,
            projective=self._role(self._projective_ref),
        )

    def line_constraint(self, value: Multivector) -> float:
        """Return the Plücker constraint ``direction·moment`` for a line bivector."""
        self._require_grade(value, 2, name="line")
        direction, moment = self._line_components(value)
        return float(np.dot(direction, moment))

    def is_valid_line(self, value: Multivector, *, atol: float = 1e-12) -> bool:
        """Whether a bivector satisfies the RGA line constraint."""
        _require_nonnegative_tolerance(atol)
        try:
            constraint = self.line_constraint(value)
        except (TypeError, ValueError):
            return False
        scale = max(1.0, float(np.linalg.norm(value.data)) ** 2)
        return abs(constraint) <= atol * scale

    def orthogonalize_line(self, value: Multivector, *, atol: float = 1e-12) -> Multivector:
        """Project a finite line's moment perpendicular to its direction."""
        _require_nonnegative_tolerance(atol)
        self._require_grade(value, 2, name="line")
        direction, moment = self._line_components(value)
        denominator = float(np.dot(direction, direction))
        if denominator <= atol:
            if self.is_valid_line(value, atol=atol):
                return value
            raise ValueError("cannot orthogonalize an ideal line with zero direction")
        corrected_moment = moment - (float(np.dot(direction, moment)) / denominator) * direction
        result = self._line_from_components(direction, corrected_moment)
        return result.with_expr() if self._expr or value.expr is not None else result

    def motor_constraint(self, value: Multivector, *, atol: float = 1e-12) -> float:
        """Return Lengyel's scalar motor constraint."""
        _require_nonnegative_tolerance(atol)
        self._check_value(value)
        scale = max(1.0, float(np.linalg.norm(value.data)))
        if any(
            abs(value.coefficient(mask)) > atol * scale for mask in range(self._algebra.dim) if mask.bit_count() % 2
        ):
            raise ValueError("motor must contain only even grades")
        velocity = np.array([self._component(value, name) for name in ("e41", "e42", "e43", "I")])
        moment = np.array([self._component(value, name) for name in ("e23", "e31", "e12")] + [value.coefficient(0)])
        return float(np.dot(velocity, moment))

    def is_valid_motor(self, value: Multivector, *, atol: float = 1e-12) -> bool:
        """Whether an even element satisfies the RGA motor constraint."""
        return self._constraint_predicate(
            lambda item: self.motor_constraint(item, atol=atol),
            value,
            atol=atol,
        )

    def flector_constraint(self, value: Multivector, *, atol: float = 1e-12) -> float:
        """Return Lengyel's scalar flector constraint."""
        _require_nonnegative_tolerance(atol)
        self._check_value(value)
        scale = max(1.0, float(np.linalg.norm(value.data)))
        if any(
            abs(value.coefficient(mask)) > atol * scale
            for mask in range(self._algebra.dim)
            if mask.bit_count() % 2 == 0
        ):
            raise ValueError("flector must contain only odd grades")
        point = np.array([self._component(value, name) for name in ("e1", "e2", "e3", "e4")])
        plane = np.array([self._component(value, name) for name in ("e423", "e431", "e412", "e321")])
        return float(np.dot(point, plane))

    def is_valid_flector(self, value: Multivector, *, atol: float = 1e-12) -> bool:
        """Whether an odd element satisfies the RGA flector constraint."""
        return self._constraint_predicate(
            lambda item: self.flector_constraint(item, atol=atol),
            value,
            atol=atol,
        )

    # Eric's established abbreviations remain convenient aliases.
    att = attitude
    angle = homogeneous_angle
    distance = homogeneous_distance
    ortho_project = orthogonal_projection
    ortho_antiproject = orthogonal_antiprojection

    def _semantic(
        self,
        result: Multivector,
        operation_id: str,
        *values: Multivector,
        **parameters: object,
    ) -> Multivector:
        if not self._expr and all(value.name is None and value.expr is None for value in values):
            return result
        operands = tuple(self._expression_operand(value) for value in values)
        return result.with_expr(Call(operation_id, operands, parameters))

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

    def _resolve_expr(self, value: bool | None) -> bool:
        if value is None:
            return self._expr
        _require_expr_flag(value)
        return value

    def _check_value(self, value: Multivector) -> None:
        if not isinstance(value, Multivector):
            raise TypeError("expected a Galaga multivector")
        if value.numeric.algebra is not self._algebra.numeric:
            raise ValueError("multivector belongs to a different numeric algebra")

    def _check_pair(self, left: Multivector, right: Multivector) -> None:
        self._check_value(left)
        self._check_value(right)

    def _require_geometry(self, value: Multivector) -> int:
        self._check_value(value)
        grade = value.homogeneous_grade()
        if grade is None or not 1 <= grade < self._algebra.n:
            raise ValueError("expected a homogeneous rigid geometry of grade 1 through n - 1")
        return grade

    def _require_grade(self, value: Multivector, grade: int, *, name: str) -> None:
        self._check_value(value)
        if value.homogeneous_grade() != grade:
            raise ValueError(f"{name} must be a homogeneous grade-{grade} multivector")

    def _require_point(self, value: Multivector) -> None:
        self._require_grade(value, 1, name="point")

    def _require_euclidean_vector(self, value: Multivector, *, atol: float = 1e-12) -> None:
        if value.homogeneous_grade(atol=atol) not in {None, 1}:
            raise ValueError("expected a vector in the Euclidean subspace")
        allowed = {ref.mask for ref in self._euclidean_refs}
        for mask, coefficient in enumerate(value.data):
            if mask not in allowed and abs(float(coefficient)) > atol:
                raise ValueError("expected a vector in the Euclidean subspace")

    def _validate_metric(self) -> None:
        basis = tuple(self._algebra.blade(ref) for ref in self._euclidean_refs)
        projective = self._algebra.blade(self._projective_ref)
        gram = np.array([[float(scalar_product(left, right)) for right in basis] for left in basis])
        if not np.allclose(gram, np.eye(3), rtol=0.0, atol=1e-12):
            raise ValueError("RGA Euclidean roles must have an identity Gram block")
        if any(abs(float(scalar_product(vector, projective))) > 1e-12 for vector in basis):
            raise ValueError("RGA projective role must be orthogonal to Euclidean space")
        if abs(float(squared(projective))) > 1e-12:
            raise ValueError("RGA projective role must be null")

    def _scalar_norm_root(self, value: Multivector, *, name: str, atol: float) -> Multivector:
        if not is_scalar(value, atol=atol):
            raise ValueError(f"{name} squared must be scalar")
        coefficient = float(value.coefficient(0))
        scale = max(1.0, abs(coefficient))
        if coefficient < -atol * scale:
            raise ValueError(f"{name} is not real")
        return self._algebra.scalar(math.sqrt(max(0.0, coefficient)))

    def _antiscalar_norm_root(self, value: Multivector, *, name: str, atol: float) -> Multivector:
        basis = self._algebra.blade(self._antiscalar_ref)
        coefficient = self._blade_magnitude(value, basis, name=f"{name} squared", atol=atol)
        scale = max(1.0, abs(coefficient))
        if coefficient < -atol * scale:
            raise ValueError(f"{name} is not real")
        return math.sqrt(max(0.0, coefficient)) * basis

    @staticmethod
    def _blade_magnitude(
        value: Multivector,
        basis: Multivector,
        *,
        name: str,
        atol: float,
    ) -> float:
        masks = [mask for mask, coefficient in enumerate(basis.data) if coefficient]
        if len(masks) != 1:  # pragma: no cover - internal role invariant
            raise RuntimeError("expected a single basis blade")
        mask = masks[0]
        coefficient = float(value.data[mask] / basis.data[mask])
        scale = max(1.0, abs(coefficient))
        if any(
            abs(float(actual - coefficient * expected)) > atol * scale
            for actual, expected in zip(value.data, basis.data, strict=True)
        ):
            raise ValueError(f"{name} must be proportional to its expected basis blade")
        return coefficient

    def _line_components(self, value: Multivector) -> tuple[np.ndarray, np.ndarray]:
        direction = np.array([self._component(value, name) for name in ("e41", "e42", "e43")])
        moment = np.array([self._component(value, name) for name in ("e23", "e31", "e12")])
        return direction, moment

    def _line_from_components(self, direction: np.ndarray, moment: np.ndarray) -> Multivector:
        result = self._algebra.scalar(0)
        for coefficient, name in zip(direction, ("e41", "e42", "e43"), strict=True):
            result = result + float(coefficient) * self._algebra.blade(name)
        for coefficient, name in zip(moment, ("e23", "e31", "e12"), strict=True):
            result = result + float(coefficient) * self._algebra.blade(name)
        return result

    def _component(self, value: Multivector, name: str) -> float:
        blade = self._algebra.blade(name)
        mask = int(np.flatnonzero(blade.data)[0])
        return float(value.data[mask] / blade.data[mask])

    def _constraint_predicate(
        self,
        operation: Callable[[Multivector], float],
        value: Multivector,
        *,
        atol: float,
    ) -> bool:
        _require_nonnegative_tolerance(atol)
        try:
            constraint = operation(value)
        except (TypeError, ValueError):
            return False
        scale = max(1.0, float(np.linalg.norm(value.data)) ** 2)
        return abs(float(constraint)) <= atol * scale


def _ordered_euclidean_roles(roles: MappingProxyType[str, BladeRef]) -> tuple[BladeRef, ...]:
    indexed: dict[int, BladeRef] = {}
    for name, ref in roles.items():
        if not name.startswith("euclidean_"):
            continue
        suffix = name.removeprefix("euclidean_")
        if not suffix.isdecimal() or int(suffix) < 1:
            raise ValueError("Euclidean RGA model roles must be numbered from euclidean_1")
        indexed[int(suffix)] = ref
    if not indexed or tuple(sorted(indexed)) != tuple(range(1, len(indexed) + 1)):
        raise ValueError("Euclidean RGA model roles must be contiguous from euclidean_1")
    return tuple(indexed[index] for index in range(1, len(indexed) + 1))


def _coordinates(value: Iterable[Real], *, expected: int) -> tuple[float, ...]:
    if isinstance(value, (str, bytes)):
        raise TypeError("Euclidean coordinates must be an iterable of real numbers")
    try:
        coordinates = tuple(value)
    except TypeError as error:
        raise TypeError("Euclidean coordinates must be an iterable of real numbers") from error
    if len(coordinates) != expected:
        raise ValueError(f"expected {expected} Euclidean coordinates, got {len(coordinates)}")
    return tuple(_finite_real(coordinate, name="Euclidean coordinate") for coordinate in coordinates)


def _finite_real(value: Real, *, name: str) -> float:
    if not isinstance(value, Real) or isinstance(value, (bool, np.bool_)):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def _is_vector_ref(ref: BladeRef) -> bool:
    return isinstance(ref, BladeRef) and ref.mask > 0 and ref.mask.bit_count() == 1


def _require_expr_flag(value: object) -> None:
    if not isinstance(value, bool):
        raise TypeError("expr must be a boolean")


def _require_nonnegative_tolerance(value: object) -> None:
    if not isinstance(value, Real) or isinstance(value, (bool, np.bool_)):
        raise TypeError("atol must be a real number")
    if not math.isfinite(float(value)) or float(value) < 0:
        raise ValueError("atol must be finite and non-negative")


__all__ = ["RigidModel"]
