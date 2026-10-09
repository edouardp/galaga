"""Plane-based projective geometry in two and three spatial dimensions."""

from collections.abc import Iterable
from numbers import Real

import numpy as np

from ..facade import Algebra, Multivector, antiwedge, complement, is_rotor, left_complement, outer_product, reverse
from ._base import _ProjectiveBase, coordinates, finite_real, ordered_euclidean_roles, tolerance
from ._classification import classify_projective
from .classification import ObjectClassification


class PGAModel(_ProjectiveBase):
    """Validated PGA: vectors are hyperplanes and grade-d blades are points.

    ``plane((a, b, c, d))`` represents ``a*x + b*y + c*z + d = 0``.
    In 2D use ``plane((a, b, d))`` for a line. Point weights are homogeneous
    and may be zero to construct ideal points.
    """

    _model_id = "pga"
    _preset_description = "Algebra(config=presets.pga())"

    __slots__ = ()

    def __init__(self, algebra: Algebra, *, expr: bool | None = None) -> None:
        super().__init__(algebra, expr=expr)
        self._euclidean_refs = ordered_euclidean_roles(self._roles)
        if len(self._euclidean_refs) not in {2, 3}:
            raise ValueError("PGAModel supports two or three spatial dimensions")
        try:
            self._projective_ref = self._roles["projective"]
        except KeyError as error:
            raise ValueError("PGA requires a projective role") from error
        self._validate_metric()

    @property
    def spatial_dim(self) -> int:
        return len(self._euclidean_refs)

    def euclidean_basis_vectors(self, *, expr: bool | None = None) -> tuple[Multivector, ...]:
        tracking = self._resolve_expr(expr)
        return tuple(self.algebra.blade(ref, expr=tracking) for ref in self._euclidean_refs)

    def point(self, position: Iterable[Real], *, weight: Real | float = 1, expr: bool | None = None) -> Multivector:
        """Construct a finite or ideal point using signed homogeneous coordinates."""
        coords = coordinates(position, expected=self.spatial_dim)
        weight = finite_real(weight, name="weight")
        tracking = self._resolve_expr(expr)
        vector = self._coordinate_vector(coords, self._euclidean_refs, tracking=tracking)
        weight_value = self.algebra.scalar(weight, expr=tracking)
        result = complement(vector + weight_value * self.algebra.blade(self._projective_ref, expr=tracking))
        return self._semantic(
            result,
            "projective_point",
            vector,
            weight_value,
            tracking=tracking,
            projective=self._role(self._projective_ref),
            dual=True,
        )

    def plane(self, coefficients: Iterable[Real], *, expr: bool | None = None) -> Multivector:
        """Construct a hyperplane from normal components followed by its offset."""
        coeffs = coordinates(coefficients, expected=self.spatial_dim + 1)
        return self._coordinate_vector(
            coeffs, (*self._euclidean_refs, self._projective_ref), tracking=self._resolve_expr(expr)
        )

    def coordinates(self, point: Multivector, *, atol: float = 1e-12) -> np.ndarray:
        """Recover finite point coordinates as an immutable array."""
        self._check_value(point)
        atol = tolerance(atol)
        if point.homogeneous_grade(atol=atol) != self.spatial_dim:
            raise ValueError("coordinates requires a PGA point blade")
        homogeneous = left_complement(point)
        weight = homogeneous.coefficient(self._projective_ref.mask) * self._projective_ref.orientation
        if abs(weight) <= atol:
            raise ValueError("an ideal point has no finite coordinates")
        result = np.array(
            [homogeneous.coefficient(ref.mask) * ref.orientation / weight for ref in self._euclidean_refs]
        )
        result.setflags(write=False)
        return result

    def join(self, left: Multivector, right: Multivector) -> Multivector:
        """Join dual projective objects with the regressive product."""
        self._check_pair(left, right)
        return self._semantic(antiwedge(left, right), "pga_join", left, right)

    def meet(self, left: Multivector, right: Multivector) -> Multivector:
        """Intersect plane-based objects with the exterior product."""
        self._check_pair(left, right)
        return self._semantic(outer_product(left, right), "pga_meet", left, right)

    def transform(self, value: Multivector, motor: Multivector) -> Multivector:
        """Apply a normalized even PGA motor using the geometric product."""
        self._check_pair(value, motor)
        if not is_rotor(motor):
            raise ValueError("transform requires a normalized even motor preserving the vector space")
        return motor * value * reverse(motor)

    def classify(self, value: Multivector, *, atol: float = 1e-9) -> ObjectClassification:
        """Classify finite and ideal PGA blades by their projective incidence."""
        return classify_projective(self, value, point_based=False, atol=atol)


__all__ = ["PGAModel"]
