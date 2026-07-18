"""Gram-native geometric algebra and immutable dense multivectors.

The public ``Algebra`` constructor accepts the same three metric descriptions
planned for Galaga. Every form is normalized to one immutable, real symmetric
Gram matrix, from which exterior metadata and a Clifford-product backend are
derived.
"""

from __future__ import annotations

from collections.abc import Iterable
from numbers import Integral, Real
from types import NotImplementedType
from typing import Any

import numpy as np
from numpy.typing import ArrayLike, NDArray

from ._backends import (
    GradeSelector,
    make_product_backend,
    packed_backend_byte_estimate,
)
from ._metadata import dimension_metadata, set_bit_indices
from ._metric import exterior_antimetric_matrix, exterior_metric_matrix

__all__ = [
    "Algebra",
    "Multivector",
    "anticommutator",
    "antidot_product",
    "antimetric_apply",
    "antireverse",
    "antiwedge",
    "bulk_part",
    "commutator",
    "complement",
    "conjugate",
    "doran_lasenby_inner",
    "dorst_inner",
    "dual",
    "even_grades",
    "exp",
    "geometric_antiproduct",
    "geometric_product",
    "gp",
    "grade",
    "grades",
    "half_anticommutator",
    "half_commutator",
    "hestenes_inner",
    "inverse",
    "involute",
    "is_basis_blade",
    "is_bivector",
    "is_even",
    "is_rotor",
    "is_scalar",
    "is_vector",
    "jordan_product",
    "join",
    "left_complement",
    "left_contraction",
    "left_hodge_dual",
    "left_interior_product",
    "left_weight_dual",
    "lie_bracket",
    "log",
    "meet",
    "metric_apply",
    "metric_inner_product",
    "metric_regressive_product",
    "norm",
    "norm2",
    "op",
    "odd_grades",
    "outercos",
    "outerexp",
    "outer_product",
    "outersin",
    "outertan",
    "regressive_product",
    "reverse",
    "right_complement",
    "right_contraction",
    "right_hodge_dual",
    "right_interior_product",
    "right_weight_dual",
    "sandwich",
    "scalar_sqrt",
    "scalar_product",
    "sqrt",
    "squared",
    "sw",
    "transwedge",
    "transwedge_antiproduct",
    "uncomplement",
    "undual",
    "unit",
    "weight_part",
]

_SYMMETRY_RTOL = 1e-12
_SYMMETRY_ATOL = 1e-12


class Multivector:
    """An immutable dense multivector in one ``Algebra``.

    Coefficients use the exterior basis indexed by bitmasks. ``data[0]`` is
    the scalar coefficient, ``data[1 << i]`` is the coefficient of basis
    vector ``e_i``, and a multi-bit index denotes the corresponding wedge
    blade. The Gram matrix affects products, never this storage layout.
    """

    def __init__(self, algebra: Algebra, data: ArrayLike) -> None:
        coefficients = _as_real_array(data, name="multivector data")
        if coefficients.shape != (algebra.dim,):
            raise ValueError(f"multivector data must have shape ({algebra.dim},), got {coefficients.shape}")
        coefficients = np.array(coefficients, dtype=np.float64, copy=True)
        coefficients.setflags(write=False)
        self._algebra = algebra
        self._data = coefficients

    @property
    def algebra(self) -> Algebra:
        """The algebra whose Gram matrix and product table this value uses."""
        return self._algebra

    @property
    def data(self) -> NDArray[np.float64]:
        """Immutable dense exterior-basis coefficients."""
        return self._data

    @property
    def scalar_part(self) -> float:
        """Coefficient of the scalar basis blade."""
        return float(self._data[0])

    @property
    def vector_part(self) -> NDArray[np.float64]:
        """Copy of the grade-one coefficients in basis-vector order."""
        return np.array(
            [self._data[1 << index] for index in range(self._algebra.n)],
            dtype=np.float64,
        )

    @property
    def inv(self) -> Multivector:
        """Multiplicative inverse."""
        return inverse(self)

    @property
    def dag(self) -> Multivector:
        """Reverse, also called the dagger involution."""
        return reverse(self)

    @property
    def bar(self) -> Multivector:
        """Clifford conjugate."""
        return conjugate(self)

    @property
    def sq(self) -> Multivector:
        """Geometric square."""
        return squared(self)

    def coefficient(self, bitmask: int) -> float:
        """Return the coefficient of one exterior basis blade."""
        if not isinstance(bitmask, Integral) or isinstance(bitmask, (bool, np.bool_)):
            raise TypeError("bitmask must be an integer")
        if bitmask < 0 or bitmask >= self._algebra.dim:
            raise ValueError(f"bitmask must be in [0, {self._algebra.dim})")
        return float(self._data[int(bitmask)])

    def grade(self, value: int) -> Multivector:
        """Return the grade-``value`` projection."""
        return grade(self, value)

    def homogeneous_grade(self, *, atol: float = 1e-12) -> int | None:
        """Return the sole nonzero grade, or ``None`` for zero or mixed grade."""
        found: int | None = None
        for value, mask in enumerate(self._algebra._grade_masks):
            if np.any(np.abs(self._data[mask]) > atol):
                if found is not None:
                    return None
                found = value
        return found

    def geometric_product(self, other: Multivector) -> Multivector:
        """Return the Clifford geometric product with ``other``."""
        return geometric_product(self, other)

    def outer_product(self, other: Multivector) -> Multivector:
        """Return the metric-independent exterior product with ``other``."""
        return outer_product(self, other)

    def doran_lasenby_inner(self, other: Multivector) -> Multivector:
        """Return the grade-difference inner product with ``other``."""
        return doran_lasenby_inner(self, other)

    def almost_equal(self, other: Multivector, *, atol: float = 1e-12) -> bool:
        """Numerically compare values from the same algebra."""
        return (
            isinstance(other, Multivector)
            and self._algebra is other._algebra
            and bool(np.allclose(self._data, other._data, rtol=0.0, atol=atol))
        )

    def _coerce_additive(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Multivector):
            self._check_same(other)
            return other
        if isinstance(other, Real):
            return self._algebra.scalar(float(other))
        return NotImplemented

    def _check_same(self, other: Multivector) -> None:
        if self._algebra is not other._algebra:
            raise ValueError("multivectors belong to different algebras")

    def __add__(self, other: object) -> Multivector | NotImplementedType:
        coerced = self._coerce_additive(other)
        if coerced is NotImplemented:
            return NotImplemented
        return Multivector(self._algebra, self._data + coerced._data)

    def __radd__(self, other: object) -> Multivector | NotImplementedType:
        return self.__add__(other)

    def __sub__(self, other: object) -> Multivector | NotImplementedType:
        coerced = self._coerce_additive(other)
        if coerced is NotImplemented:
            return NotImplemented
        return Multivector(self._algebra, self._data - coerced._data)

    def __rsub__(self, other: object) -> Multivector | NotImplementedType:
        coerced = self._coerce_additive(other)
        if coerced is NotImplemented:
            return NotImplemented
        return Multivector(self._algebra, coerced._data - self._data)

    def __neg__(self) -> Multivector:
        return Multivector(self._algebra, -self._data)

    def __pos__(self) -> Multivector:
        return self

    def __mul__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Multivector):
            return geometric_product(self, other)
        if isinstance(other, Real):
            return Multivector(self._algebra, self._data * float(other))
        return NotImplemented

    def __rmul__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Real):
            return Multivector(self._algebra, float(other) * self._data)
        if isinstance(other, Multivector):
            return geometric_product(other, self)
        return NotImplemented

    def __truediv__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Real):
            divisor = float(other)
            if divisor == 0:
                raise ZeroDivisionError("cannot divide a multivector by zero")
            return Multivector(self._algebra, self._data / divisor)
        if isinstance(other, Multivector):
            self._check_same(other)
            if is_scalar(other):
                divisor = other.scalar_part
                if divisor == 0:
                    raise ZeroDivisionError("cannot divide by a zero scalar multivector")
                return Multivector(self._algebra, self._data / divisor)
            return self * inverse(other)
        return NotImplemented

    def __rtruediv__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Real):
            return float(other) * inverse(self)
        return NotImplemented

    def __pow__(self, exponent: object) -> Multivector | NotImplementedType:
        if not isinstance(exponent, Integral) or isinstance(
            exponent,
            (bool, np.bool_),
        ):
            return NotImplemented
        power = int(exponent)
        factor = self
        if power < 0:
            factor = inverse(factor)
            power = -power
        result = self._algebra.scalar(1)
        while power:
            if power & 1:
                result = result * factor
            power >>= 1
            if power:
                factor = factor * factor
        return result

    def __xor__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Multivector):
            return outer_product(self, other)
        if isinstance(other, Real):
            return outer_product(self, self._algebra.scalar(float(other)))
        return NotImplemented

    def __rxor__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Real):
            return outer_product(self._algebra.scalar(float(other)), self)
        if isinstance(other, Multivector):
            return outer_product(other, self)
        return NotImplemented

    def __or__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Multivector):
            return doran_lasenby_inner(self, other)
        if isinstance(other, Real):
            return doran_lasenby_inner(
                self,
                self._algebra.scalar(float(other)),
            )
        return NotImplemented

    def __ror__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Real):
            return doran_lasenby_inner(
                self._algebra.scalar(float(other)),
                self,
            )
        if isinstance(other, Multivector):
            return doran_lasenby_inner(other, self)
        return NotImplemented

    def __invert__(self) -> Multivector:
        return reverse(self)

    def __getitem__(self, value: int | str) -> Multivector:
        """Return one grade, or the combined ``"even"``/``"odd"`` grades."""
        return grade(self, value)

    def __float__(self) -> float:
        homogeneous = self.homogeneous_grade()
        if homogeneous == 0 or (homogeneous is None and not np.any(np.abs(self._data[1:]) > 1e-12)):
            return self.scalar_part
        if homogeneous is None:
            raise TypeError(
                "cannot convert a mixed-grade multivector to float; only scalar multivectors support float()"
            )
        raise TypeError(
            f"cannot convert a grade-{homogeneous} multivector to float; only scalar multivectors support float()"
        )

    def __abs__(self) -> float:
        return abs(float(self))

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Multivector):
            return self._algebra is other._algebra and bool(np.array_equal(self._data, other._data))
        if isinstance(other, Real):
            return bool(np.array_equal(self._data, self._algebra.scalar(float(other))._data))
        return False

    def __hash__(self) -> int:
        return hash((id(self._algebra), self._data.tobytes()))

    def __repr__(self) -> str:
        terms = []
        for bitmask in np.flatnonzero(self._data):
            coefficient = self._data[bitmask]
            blade = _blade_name(int(bitmask))
            terms.append(f"{coefficient:g}{blade}")
        return " + ".join(terms) if terms else "0"


class Algebra:
    """An algebra metric normalized to a native Gram matrix.

    Construct an algebra from one of:

    - ``Algebra(p, q=0, r=0)`` for ``Cl(p, q, r)``;
    - ``Algebra(signature=...)`` or its short alias ``Algebra(sig=...)`` for
      an explicitly ordered sequence of ``+1``, ``-1``, and ``0``
      basis-vector squares; or
    - ``Algebra(gram=matrix)`` for an arbitrary real symmetric Gram matrix.

    The ``Cl(p, q, r)`` ordering matches Galaga: null vectors first, followed
    by positive vectors and then negative vectors. ``Algebra(0)`` is the
    zero-generator scalar algebra. The diagnostic ``product_backend=`` keyword
    can force ``"diagonal"``, ``"packed"``, ``"lazy"``, or ``"reference"``;
    normal code should retain its ``"auto"`` default.
    """

    def __init__(
        self,
        p: int | None = None,
        q: int = 0,
        r: int = 0,
        *,
        signature: ArrayLike | None = None,
        sig: ArrayLike | None = None,
        gram: ArrayLike | None = None,
        id: str | None = None,
        product_backend: str = "auto",
    ) -> None:
        if id is not None:
            if not isinstance(id, str):
                raise TypeError("id must be a string or None")
            if not id.strip():
                raise ValueError("id must not be empty")
        if not isinstance(product_backend, str):
            raise TypeError("product_backend must be a string")

        if signature is not None and sig is not None:
            raise TypeError("signature= and sig= are aliases; provide only one")
        explicit_signature = signature if signature is not None else sig

        if gram is not None:
            if p is not None or q != 0 or r != 0 or explicit_signature is not None:
                raise TypeError("gram= cannot be combined with a signature or p, q, r")
            normalized = _normalize_gram(gram)
        elif explicit_signature is not None:
            if p is not None or q != 0 or r != 0:
                raise TypeError("signature= cannot be combined with p, q, or r")
            normalized_signature = _normalize_signature(explicit_signature)
            normalized = np.diag(normalized_signature)
        elif p is None:
            raise TypeError("provide p, signature= (or sig=), or gram=")
        elif _is_int(p):
            p_count = _nonnegative_count("p", p)
            q_count = _nonnegative_count("q", q)
            r_count = _nonnegative_count("r", r)
            normalized_signature = (0.0,) * r_count + (1.0,) * p_count + (-1.0,) * q_count
            normalized = np.diag(normalized_signature)
        else:
            raise TypeError("p must be an integer; use signature= or sig= for a signature")

        normalized = np.array(normalized, dtype=np.float64, copy=True)
        normalized.setflags(write=False)

        basis_squares = np.diag(normalized).copy()
        basis_squares.setflags(write=False)

        self._gram = normalized
        self._id = id
        self._basis_squares = basis_squares
        self._n = normalized.shape[0]
        self._dim = 1 << self._n
        self._is_orthogonal_basis = bool(np.array_equal(normalized, np.diag(basis_squares)))
        self._has_legacy_signature = self._is_orthogonal_basis and bool(
            np.all(np.isin(basis_squares, (-1.0, 0.0, 1.0)))
        )
        metadata = dimension_metadata(self._n)
        self._blade_grades = metadata.blade_grades
        self._grade_masks = metadata.grade_masks
        self._reverse_sign = metadata.reverse_sign
        self._involute_sign = metadata.involute_sign
        self._conjugate_sign = metadata.conjugate_sign
        self._antireverse_sign = metadata.antireverse_sign
        self._wedge_factor = metadata.wedge_factor
        self._complement_index = metadata.complement_index
        self._left_complement_sign = metadata.left_complement_sign
        self._right_complement_sign = metadata.right_complement_sign
        self._extended_metric: NDArray[np.float64] | None = None
        self._antimetric: NDArray[np.float64] | None = None
        (
            self._inertia,
            self._metric_rank,
            self._metric_determinant,
        ) = _metric_invariants(self._gram)
        self._product_backend = make_product_backend(
            product_backend,
            self._gram,
            metadata,
            is_diagonal=self._is_orthogonal_basis,
        )
        self._basis_vectors = tuple(self.blade(1 << index) for index in range(self._n))

    @property
    def gram(self) -> NDArray[np.float64]:
        """The immutable matrix ``G[i, j] = e_i · e_j``."""
        return self._gram

    @property
    def id(self) -> str | None:
        """Optional stable name for examples, diagnostics, and test cases."""
        return self._id

    @property
    def basis_squares(self) -> NDArray[np.float64]:
        """The immutable diagonal ``G[i, i] = e_i²`` in the stored basis."""
        return self._basis_squares

    @property
    def n(self) -> int:
        """Number of basis vectors."""
        return self._n

    @property
    def dim(self) -> int:
        """Dimension ``2**n`` of the exterior/Clifford coefficient space."""
        return self._dim

    @property
    def is_orthogonal_basis(self) -> bool:
        """Whether all off-diagonal scalar products are exactly zero."""
        return self._is_orthogonal_basis

    @property
    def inertia(self) -> tuple[int, int, int]:
        """Metric inertia ``(positive, negative, null)`` in any basis."""
        return self._inertia

    @property
    def metric_rank(self) -> int:
        """Numerical rank determined with the inertia classification tolerance."""
        return self._metric_rank

    @property
    def metric_determinant(self) -> float:
        """Unthresholded numerical determinant of the vector Gram matrix."""
        return self._metric_determinant

    @property
    def is_degenerate(self) -> bool:
        """Whether the vector metric has at least one null eigenvalue."""
        return self._inertia[2] != 0

    @property
    def product_backend(self) -> str:
        """Name of the selected geometric-product backend."""
        return self._product_backend.name

    @property
    def packed_product_byte_estimate(self) -> int:
        """Conservative packed-product storage estimate used by ``auto``."""
        return packed_backend_byte_estimate(dimension_metadata(self._n))

    @property
    def product_cache_info(self) -> tuple[int, int, int] | None:
        """Return lazy-cache ``(entries, bytes, budget)`` or ``None``."""
        cache_info = getattr(self._product_backend, "cache_info", None)
        if cache_info is None:
            return None
        return cache_info

    def multivector(self, data: ArrayLike) -> Multivector:
        """Construct a multivector from dense exterior-basis coefficients."""
        return Multivector(self, data)

    def scalar(self, value: Real) -> Multivector:
        """Construct a scalar multivector."""
        if not isinstance(value, Real):
            raise TypeError("scalar value must be real")
        data = np.zeros(self._dim, dtype=np.float64)
        data[0] = float(value)
        return Multivector(self, data)

    def vector(self, values: ArrayLike) -> Multivector:
        """Construct a vector from coefficients in Gram-matrix order."""
        coefficients = _as_real_array(values, name="vector coefficients")
        if coefficients.shape != (self._n,):
            raise ValueError(f"vector coefficients must have shape ({self._n},), got {coefficients.shape}")
        data = np.zeros(self._dim, dtype=np.float64)
        for index, coefficient in enumerate(coefficients):
            data[1 << index] = coefficient
        return Multivector(self, data)

    @property
    def identity(self) -> Multivector:
        """Multiplicative identity."""
        return self.scalar(1)

    @property
    def I(self) -> Multivector:  # noqa: E743 - conventional pseudoscalar name
        """Pseudoscalar compatibility property."""
        return self.pseudoscalar()

    def blade(self, bitmask: int) -> Multivector:
        """Return one native exterior basis blade by bitmask."""
        if not isinstance(bitmask, Integral) or isinstance(bitmask, (bool, np.bool_)):
            raise TypeError("bitmask must be an integer")
        bitmask = int(bitmask)
        if bitmask < 0 or bitmask >= self._dim:
            raise ValueError(f"bitmask must be in [0, {self._dim})")
        data = np.zeros(self._dim, dtype=np.float64)
        data[bitmask] = 1.0
        return Multivector(self, data)

    def basis_vectors(self) -> tuple[Multivector, ...]:
        """Return native one-hot grade-1 multivectors in Gram-matrix order."""
        return self._basis_vectors

    def basis_blades(self, value: int) -> tuple[Multivector, ...]:
        """Return all native exterior basis blades of one grade."""
        if not isinstance(value, Integral) or isinstance(value, (bool, np.bool_)):
            raise TypeError("grade must be an integer")
        value = int(value)
        if value < 0 or value > self._n:
            raise ValueError(f"grade must be in [0, {self._n}]")
        return tuple(self.blade(bitmask) for bitmask in range(self._dim) if self._blade_grades[bitmask] == value)

    def pseudoscalar(self) -> Multivector:
        """Return the top-grade exterior basis blade."""
        return self.blade(self._dim - 1)

    def left_action(self, value: Multivector) -> NDArray[np.float64]:
        """Materialize the matrix for left multiplication by ``value``.

        This backend-neutral interface is intended for regular matrix
        representations and diagnostics. The returned matrix and every
        product backend owned by the algebra remain immutable.
        """
        if not isinstance(value, Multivector):
            raise TypeError("left_action expects a Multivector")
        if value.algebra is not self:
            raise ValueError("multivector belongs to a different algebra")
        action = np.zeros((self._dim, self._dim), dtype=np.float64)
        for bitmask in np.flatnonzero(value.data):
            action += value.data[bitmask] * self._product_backend.left_action(int(bitmask))
        action.setflags(write=False)
        return action

    def extended_metric_matrix(self) -> NDArray[np.float64]:
        """Return the lazy compound-matrix exterior extension ``ΛG``."""
        if self._extended_metric is None:
            self._extended_metric = exterior_metric_matrix(
                self._gram,
                dimension_metadata(self._n),
            )
        return self._extended_metric

    def metric_antiexomorphism_matrix(self) -> NDArray[np.float64]:
        """Return the lazy complementary-compound antimetric matrix."""
        if self._antimetric is None:
            self._antimetric = exterior_antimetric_matrix(
                self._gram,
                dimension_metadata(self._n),
            )
        return self._antimetric

    @property
    def signature(self) -> tuple[int, ...]:
        """Return the legacy ordered signature for normalized diagonal metrics.

        A non-orthogonal Gram matrix has no per-basis-vector signature tuple
        that captures its metric. Returning its diagonal or inertia here would
        discard information, so callers must use ``gram`` instead.
        """
        if not self._has_legacy_signature:
            raise ValueError("signature is only defined for normalized diagonal metrics; use gram or basis_squares")
        return tuple(int(square) for square in self._basis_squares)


def geometric_product(left: Multivector, right: Multivector) -> Multivector:
    """Return the Clifford product computed from the native Gram matrix."""
    if not isinstance(left, Multivector) or not isinstance(right, Multivector):
        raise TypeError("geometric_product expects two Multivectors")
    left._check_same(right)
    output = left.algebra._product_backend.multiply(left.data, right.data)
    return Multivector(left.algebra, output)


gp = geometric_product


def outer_product(left: Multivector, right: Multivector) -> Multivector:
    """Return the metric-independent exterior product."""
    if not isinstance(left, Multivector) or not isinstance(right, Multivector):
        raise TypeError("outer_product expects two Multivectors")
    left._check_same(right)
    output = np.zeros(left.algebra.dim, dtype=np.float64)
    for left_mask in np.flatnonzero(left.data):
        for right_mask in np.flatnonzero(right.data):
            factor = left.algebra._wedge_factor[left_mask, right_mask]
            if factor:
                output[left_mask ^ right_mask] += left.data[left_mask] * right.data[right_mask] * factor
    return Multivector(left.algebra, output)


op = outer_product


def grade(value: Multivector, target: int | str) -> Multivector:
    """Project onto one grade or the combined ``"even"``/``"odd"`` grades."""
    if not isinstance(value, Multivector):
        raise TypeError("grade expects a Multivector")
    if target == "even":
        return even_grades(value)
    if target == "odd":
        return odd_grades(value)
    if not isinstance(target, Integral) or isinstance(target, (bool, np.bool_)):
        raise TypeError("grade must be an integer, 'even', or 'odd'")
    target = int(target)
    if target < 0 or target > value.algebra.n:
        return value.algebra.scalar(0)
    output = np.zeros(value.algebra.dim, dtype=np.float64)
    mask = value.algebra._grade_masks[target]
    output[mask] = value.data[mask]
    return Multivector(value.algebra, output)


def grades(value: Multivector, targets: Iterable[int]) -> Multivector:
    """Project a multivector onto several exterior grades."""
    if not isinstance(value, Multivector):
        raise TypeError("grades expects a Multivector")
    if isinstance(targets, (str, bytes)) or not isinstance(targets, Iterable):
        raise TypeError("grades must be an iterable of integers")
    output = np.zeros(value.algebra.dim, dtype=np.float64)
    for target in targets:
        if not isinstance(target, Integral) or isinstance(target, (bool, np.bool_)):
            raise TypeError("every grade must be an integer")
        target = int(target)
        if 0 <= target <= value.algebra.n:
            mask = value.algebra._grade_masks[target]
            output[mask] = value.data[mask]
    return Multivector(value.algebra, output)


def even_grades(value: Multivector) -> Multivector:
    """Return all even-grade components."""
    if not isinstance(value, Multivector):
        raise TypeError("even_grades expects a Multivector")
    return grades(value, range(0, value.algebra.n + 1, 2))


def odd_grades(value: Multivector) -> Multivector:
    """Return all odd-grade components."""
    if not isinstance(value, Multivector):
        raise TypeError("odd_grades expects a Multivector")
    return grades(value, range(1, value.algebra.n + 1, 2))


def scalar_product(left: Multivector, right: Multivector) -> Multivector:
    """Return the scalar part of the geometric product as a multivector."""
    return _grade_selected_product(left, right, lambda _r, _s: 0)


def metric_inner_product(left: Multivector, right: Multivector) -> Multivector:
    """Return Lengyel's metric-induced pairing ``<left * ~right>_0``."""
    if not isinstance(left, Multivector) or not isinstance(right, Multivector):
        raise TypeError("metric_inner_product expects two Multivectors")
    left._check_same(right)
    return scalar_product(left, reverse(right))


def metric_apply(value: Multivector) -> Multivector:
    """Apply the compound-matrix exterior extension of the vector metric."""
    if not isinstance(value, Multivector):
        raise TypeError("metric_apply expects a Multivector")
    return Multivector(
        value.algebra,
        value.algebra.extended_metric_matrix() @ value.data,
    )


def antimetric_apply(value: Multivector) -> Multivector:
    """Apply the complementary-compound antimetric extension."""
    if not isinstance(value, Multivector):
        raise TypeError("antimetric_apply expects a Multivector")
    return Multivector(
        value.algebra,
        value.algebra.metric_antiexomorphism_matrix() @ value.data,
    )


def antidot_product(left: Multivector, right: Multivector) -> Multivector:
    """Return the antimetric pairing as a pseudoscalar-valued product."""
    if not isinstance(left, Multivector) or not isinstance(right, Multivector):
        raise TypeError("antidot_product expects two Multivectors")
    left._check_same(right)
    pairing = float(left.data @ left.algebra.metric_antiexomorphism_matrix() @ right.data)
    return pairing * left.algebra.I


def bulk_part(value: Multivector) -> Multivector:
    """Return the metric-applied bulk part of a multivector."""
    return metric_apply(value)


def weight_part(value: Multivector) -> Multivector:
    """Return the antimetric-applied weight part of a multivector."""
    return antimetric_apply(value)


def right_hodge_dual(value: Multivector) -> Multivector:
    """Return ``right_complement(metric_apply(value))``."""
    return right_complement(metric_apply(value))


def left_hodge_dual(value: Multivector) -> Multivector:
    """Return ``left_complement(metric_apply(value))``."""
    return left_complement(metric_apply(value))


def right_weight_dual(value: Multivector) -> Multivector:
    """Return ``right_complement(antimetric_apply(value))``."""
    return right_complement(antimetric_apply(value))


def left_weight_dual(value: Multivector) -> Multivector:
    """Return ``left_complement(antimetric_apply(value))``."""
    return left_complement(antimetric_apply(value))


def left_contraction(left: Multivector, right: Multivector) -> Multivector:
    """Return ``<A_r B_s>_(s-r)`` for each homogeneous pair with ``r <= s``."""
    return _grade_selected_product(
        left,
        right,
        lambda left_grade, right_grade: right_grade - left_grade if left_grade <= right_grade else None,
    )


def right_contraction(left: Multivector, right: Multivector) -> Multivector:
    """Return ``<A_r B_s>_(r-s)`` for each homogeneous pair with ``r >= s``."""
    return _grade_selected_product(
        left,
        right,
        lambda left_grade, right_grade: left_grade - right_grade if left_grade >= right_grade else None,
    )


def hestenes_inner(left: Multivector, right: Multivector) -> Multivector:
    """Return the Hestenes grade-difference product, discarding scalar grades."""
    return _grade_selected_product(
        left,
        right,
        lambda left_grade, right_grade: abs(left_grade - right_grade) if left_grade > 0 and right_grade > 0 else None,
    )


def doran_lasenby_inner(left: Multivector, right: Multivector) -> Multivector:
    """Return the grade-absolute-difference product, including scalars."""
    return _grade_selected_product(
        left,
        right,
        lambda left_grade, right_grade: abs(left_grade - right_grade),
    )


dorst_inner = doran_lasenby_inner


def commutator(left: Multivector, right: Multivector) -> Multivector:
    """Return ``left * right - right * left``."""
    return geometric_product(left, right) - geometric_product(right, left)


def anticommutator(left: Multivector, right: Multivector) -> Multivector:
    """Return ``left * right + right * left``."""
    return geometric_product(left, right) + geometric_product(right, left)


def half_commutator(left: Multivector, right: Multivector) -> Multivector:
    """Return ``(left * right - right * left) / 2``."""
    return 0.5 * commutator(left, right)


def half_anticommutator(left: Multivector, right: Multivector) -> Multivector:
    """Return ``(left * right + right * left) / 2``."""
    return 0.5 * anticommutator(left, right)


def lie_bracket(left: Multivector, right: Multivector) -> Multivector:
    """Return the unscaled Lie bracket ``left * right - right * left``."""
    return commutator(left, right)


def jordan_product(left: Multivector, right: Multivector) -> Multivector:
    """Return the unscaled symmetric product ``left * right + right * left``.

    Many Jordan-algebra texts include a factor of one half. Gram reserves all
    such scaling for :func:`half_anticommutator`, making the function name
    reveal whether normalization occurs.
    """
    return anticommutator(left, right)


def reverse(value: Multivector) -> Multivector:
    """Reverse every exterior blade in a multivector."""
    if not isinstance(value, Multivector):
        raise TypeError("reverse expects a Multivector")
    return Multivector(value.algebra, value.data * value.algebra._reverse_sign)


def involute(value: Multivector) -> Multivector:
    """Apply grade involution, negating every odd grade."""
    if not isinstance(value, Multivector):
        raise TypeError("involute expects a Multivector")
    return Multivector(value.algebra, value.data * value.algebra._involute_sign)


def conjugate(value: Multivector) -> Multivector:
    """Apply Clifford conjugation, the composition of reverse and involute."""
    if not isinstance(value, Multivector):
        raise TypeError("conjugate expects a Multivector")
    return Multivector(value.algebra, value.data * value.algebra._conjugate_sign)


def complement(value: Multivector) -> Multivector:
    """Return the metric-independent right complement.

    Every basis blade ``A`` satisfies ``A ^ complement(A) == I``.
    """
    if not isinstance(value, Multivector):
        raise TypeError("complement expects a Multivector")
    output = np.zeros(value.algebra.dim, dtype=np.float64)
    output[value.algebra._complement_index] = value.data * value.algebra._right_complement_sign
    return Multivector(value.algebra, output)


def uncomplement(value: Multivector) -> Multivector:
    """Return the inverse/left complement.

    Every basis blade ``A`` satisfies ``uncomplement(A) ^ A == I``.
    """
    if not isinstance(value, Multivector):
        raise TypeError("uncomplement expects a Multivector")
    output = np.zeros(value.algebra.dim, dtype=np.float64)
    output[value.algebra._complement_index] = value.data * value.algebra._left_complement_sign
    return Multivector(value.algebra, output)


def right_complement(value: Multivector) -> Multivector:
    """Explicit name for :func:`complement`."""
    return complement(value)


def left_complement(value: Multivector) -> Multivector:
    """Explicit name for :func:`uncomplement`."""
    return uncomplement(value)


def antireverse(value: Multivector) -> Multivector:
    """Apply reversion by antigrade instead of grade."""
    if not isinstance(value, Multivector):
        raise TypeError("antireverse expects a Multivector")
    return Multivector(
        value.algebra,
        value.data * value.algebra._antireverse_sign,
    )


def dual(value: Multivector) -> Multivector:
    """Return the conventional metric dual using the inverse pseudoscalar."""
    if not isinstance(value, Multivector):
        raise TypeError("dual expects a Multivector")
    try:
        pseudoscalar_inverse = inverse(value.algebra.I)
    except ValueError:
        raise ValueError("dual requires an invertible pseudoscalar; use complement in a degenerate algebra") from None
    return left_contraction(value, pseudoscalar_inverse)


def undual(value: Multivector) -> Multivector:
    """Return the inverse of :func:`dual` for a nondegenerate metric."""
    if not isinstance(value, Multivector):
        raise TypeError("undual expects a Multivector")
    if value.algebra.is_degenerate:
        raise ValueError("undual requires an invertible pseudoscalar; use uncomplement in a degenerate algebra")
    return left_contraction(value, value.algebra.I)


def regressive_product(left: Multivector, right: Multivector) -> Multivector:
    """Return the metric-independent complement-based regressive product."""
    return uncomplement(
        outer_product(complement(left), complement(right)),
    )


def antiwedge(left: Multivector, right: Multivector) -> Multivector:
    """RGA name for :func:`regressive_product`."""
    return regressive_product(left, right)


def metric_regressive_product(
    left: Multivector,
    right: Multivector,
) -> Multivector:
    """Return the metric-dual regressive product for nondegenerate metrics."""
    return undual(outer_product(dual(left), dual(right)))


def geometric_antiproduct(
    left: Multivector,
    right: Multivector,
) -> Multivector:
    """Return the De Morgan dual of the geometric product."""
    if not isinstance(left, Multivector) or not isinstance(right, Multivector):
        raise TypeError("geometric_antiproduct expects two Multivectors")
    left._check_same(right)
    return complement(
        geometric_product(left_complement(left), left_complement(right)),
    )


def left_interior_product(
    left: Multivector,
    right: Multivector,
) -> Multivector:
    """Return the RGA left interior product from the left Hodge dual."""
    if not isinstance(left, Multivector) or not isinstance(right, Multivector):
        raise TypeError("left_interior_product expects two Multivectors")
    left._check_same(right)
    return antiwedge(left_hodge_dual(left), right)


def right_interior_product(
    left: Multivector,
    right: Multivector,
) -> Multivector:
    """Return the RGA right interior product from the right Hodge dual."""
    if not isinstance(left, Multivector) or not isinstance(right, Multivector):
        raise TypeError("right_interior_product expects two Multivectors")
    left._check_same(right)
    return antiwedge(left, right_hodge_dual(right))


def transwedge(
    left: Multivector,
    right: Multivector,
    order: int,
) -> Multivector:
    """Return Lengyel's order-``order`` transwedge product.

    For homogeneous grades ``r`` and ``s``, this selects grade
    ``r + s - 2*order`` from the geometric product and removes the reversion
    sign used by its geometric-product decomposition.
    """
    if not isinstance(order, Integral) or isinstance(order, (bool, np.bool_)):
        raise TypeError("transwedge order must be an integer")
    order = int(order)
    if order < 0:
        raise ValueError("transwedge order must be non-negative")
    sign = (-1.0) ** (order * (order - 1) // 2)
    selected = _grade_selected_product(
        left,
        right,
        lambda left_grade, right_grade: (
            left_grade + right_grade - 2 * order if order <= min(left_grade, right_grade) else None
        ),
    )
    return sign * selected


def transwedge_antiproduct(
    left: Multivector,
    right: Multivector,
    order: int,
) -> Multivector:
    """Return the De Morgan dual of the order-``order`` transwedge."""
    if not isinstance(left, Multivector) or not isinstance(right, Multivector):
        raise TypeError("transwedge_antiproduct expects two Multivectors")
    left._check_same(right)
    return complement(
        transwedge(left_complement(left), left_complement(right), order),
    )


meet = regressive_product
join = outer_product


def squared(value: Multivector) -> Multivector:
    """Return the geometric square of a multivector."""
    if not isinstance(value, Multivector):
        raise TypeError("squared expects a Multivector")
    return geometric_product(value, value)


def scalar_sqrt(value: Real | Multivector) -> float | Multivector:
    """Return the nonnegative real square root of a scalar value.

    Plain real numbers produce a ``float``. A scalar multivector produces a
    scalar in the same algebra. Negative values and nonscalar multivectors do
    not have a result in this real numeric core and therefore raise.
    """
    if isinstance(value, Multivector):
        if np.any(value.data[1:]):
            raise ValueError("scalar_sqrt requires a scalar multivector")
        scalar = value.scalar_part
        if scalar < 0:
            raise ValueError(f"scalar_sqrt of negative value {scalar}")
        return value.algebra.scalar(float(np.sqrt(scalar)))
    if not isinstance(value, Real):
        raise TypeError("scalar_sqrt expects a Multivector or real number")
    scalar = float(value)
    if not np.isfinite(scalar):
        raise ValueError("scalar_sqrt expects a finite real number")
    if scalar < 0:
        raise ValueError(f"scalar_sqrt of negative value {scalar}")
    return float(np.sqrt(scalar))


def sqrt(value: Real | Multivector, *, atol: float = 1e-12) -> float | Multivector:
    """Return the principal real square root of a Study number.

    A non-scalar multivector must have the form ``a + N`` with scalar ``a``
    and scalar ``N*N``. This includes simple elliptic and hyperbolic rotors as
    well as null PGA translators. The returned value lies in the same
    two-dimensional subalgebra and squares to ``value``.
    """
    if not isinstance(value, Multivector):
        if isinstance(value, Real):
            return scalar_sqrt(value)
        raise TypeError("sqrt expects a Multivector or real number")
    if not np.any(value.data[1:]):
        return scalar_sqrt(value)

    scalar = value.scalar_part
    nonscalar = value - value.algebra.scalar(scalar)
    nonscalar_square = squared(nonscalar)
    if not is_scalar(nonscalar_square, atol=atol):
        raise ValueError("sqrt requires a Study number whose nonscalar part squares to a scalar")

    square = nonscalar_square.scalar_part
    discriminant = scalar * scalar - square
    scale = max(1.0, abs(scalar * scalar), abs(square))
    if discriminant < -atol * scale:
        raise ValueError("Study number has no square root in the real algebra")
    discriminant = max(0.0, discriminant)
    scalar_root_square = 0.5 * (scalar + float(np.sqrt(discriminant)))
    if scalar_root_square < -atol * scale:
        raise ValueError("Study number has no principal real square root")
    scalar_root = float(np.sqrt(max(0.0, scalar_root_square)))
    if scalar_root <= atol:
        raise ValueError("Study-number square root is singular on the selected real branch")

    result = value.algebra.scalar(scalar_root) + nonscalar / (2 * scalar_root)
    if not np.allclose(
        squared(result).data,
        value.data,
        rtol=10 * atol,
        atol=10 * atol,
    ):
        raise ValueError("Study-number square root could not be resolved numerically")
    return result


def exp(value: Multivector) -> Multivector:
    """Return the geometric exponential of a multivector.

    Scalar inputs and elements with scalar square use their closed forms.
    General multivectors use a scaling-and-squaring Taylor evaluation, with
    scaling determined from the backend-neutral left-regular action.
    """
    if not isinstance(value, Multivector):
        raise TypeError("exp expects a Multivector")
    if not np.any(value.data[1:]):
        return value.algebra.scalar(float(np.exp(value.scalar_part)))

    value_square = squared(value)
    if not np.any(value_square.data[1:]):
        return _exp_scalar_square(value, value_square.scalar_part)

    action_norm = float(np.linalg.norm(value.algebra.left_action(value), ord=np.inf))
    if not np.isfinite(action_norm):
        raise ValueError("exponential cannot be resolved from a non-finite action")
    if action_norm == 0:
        return value.algebra.identity
    scaling_steps = max(0, int(np.ceil(np.log2(action_norm / 0.5))))
    scaled = (2.0 ** (-scaling_steps)) * value

    result = value.algebra.identity
    term = value.algebra.identity
    for order in range(1, 129):
        term = geometric_product(term, scaled) / order
        result = result + term
        term_size = float(np.max(np.abs(term.data)))
        result_size = max(1.0, float(np.max(np.abs(result.data))))
        if term_size <= np.finfo(np.float64).eps * result_size:
            break
    else:
        raise ValueError("exponential series did not converge")

    for _ in range(scaling_steps):
        result = squared(result)
    return result


def _exp_scalar_square(value: Multivector, square: float) -> Multivector:
    """Return ``exp(value)`` when ``value*value`` is exactly scalar."""
    if square == 0:
        return value.algebra.identity + value
    if square < 0:
        magnitude = float(np.sqrt(-square))
        factor = float(np.sinc(magnitude / np.pi))
        return value.algebra.scalar(float(np.cos(magnitude))) + factor * value
    magnitude = float(np.sqrt(square))
    factor = float(np.sinh(magnitude) / magnitude)
    return value.algebra.scalar(float(np.cosh(magnitude))) + factor * value


def log(value: Multivector, *, atol: float = 1e-12) -> Multivector:
    """Return the principal logarithm of a real Study-number rotor.

    The supported rotor has scalar part ``a`` and nonscalar part ``N`` with
    scalar ``N*N``. Elliptic, hyperbolic, and null generators are handled.
    General non-Study rotors require a separate matrix or bivector-factor
    logarithm algorithm and are rejected instead of returning a partial
    answer.
    """
    if not isinstance(value, Multivector):
        raise TypeError("log expects a Multivector")
    if not is_rotor(value, atol=atol):
        raise ValueError("log expects a normalized rotor")

    scalar = value.scalar_part
    nonscalar = value - value.algebra.scalar(scalar)
    if not np.any(nonscalar.data):
        if scalar > 0:
            return value.algebra.scalar(0)
        raise ValueError("the logarithm of -1 is undefined without a plane")

    nonscalar_square = squared(nonscalar)
    if not is_scalar(nonscalar_square, atol=atol):
        raise ValueError("log currently requires a Study-number rotor")
    square = nonscalar_square.scalar_part
    square_scale = max(1.0, float(np.max(np.abs(nonscalar.data))) ** 2)

    if abs(square) <= atol * square_scale:
        if not np.isclose(scalar, 1.0, rtol=0.0, atol=atol):
            raise ValueError("null-rotor logarithm requires scalar part +1")
        return nonscalar
    if square < 0:
        magnitude = float(np.sqrt(-square))
        angle = float(np.arctan2(magnitude, scalar))
        return (angle / magnitude) * nonscalar

    magnitude = float(np.sqrt(square))
    if scalar <= 0 or magnitude >= scalar:
        raise ValueError("hyperbolic rotor is outside the principal real branch")
    rapidity = float(np.arctanh(magnitude / scalar))
    return (rapidity / magnitude) * nonscalar


def outerexp(value: Multivector) -> Multivector:
    """Return the exponential series formed with the exterior product."""
    even, odd = _outer_even_odd(value)
    scalar_exp = float(np.exp(value.scalar_part))
    return scalar_exp * (even + odd)


def outersin(value: Multivector) -> Multivector:
    """Return the odd-power part of the outer exponential series."""
    even, odd = _outer_even_odd(value)
    scalar = value.scalar_part
    return float(np.sinh(scalar)) * even + float(np.cosh(scalar)) * odd


def outercos(value: Multivector) -> Multivector:
    """Return the even-power part of the outer exponential series."""
    even, odd = _outer_even_odd(value)
    scalar = value.scalar_part
    return float(np.cosh(scalar)) * even + float(np.sinh(scalar)) * odd


def outertan(value: Multivector) -> Multivector:
    """Return ``outersin(value) * inverse(outercos(value))``."""
    if not isinstance(value, Multivector):
        raise TypeError("outertan expects a Multivector")
    return geometric_product(outersin(value), inverse(outercos(value)))


def _outer_even_odd(value: Multivector) -> tuple[Multivector, Multivector]:
    """Return even and odd wedge-power sums of the positive-grade part."""
    if not isinstance(value, Multivector):
        raise TypeError("outer transcendental functions expect a Multivector")
    positive_grades = value - value.algebra.scalar(value.scalar_part)
    even = value.algebra.identity
    odd = value.algebra.scalar(0)
    term = value.algebra.identity
    for order in range(1, value.algebra.n + 1):
        term = outer_product(term, positive_grades) / order
        if not np.any(term.data):
            break
        if order % 2:
            odd = odd + term
        else:
            even = even + term
    return even, odd


def norm2(value: Multivector) -> Multivector:
    """Return the scalar squared norm ``<value * ~value>_0``."""
    if not isinstance(value, Multivector):
        raise TypeError("norm2 expects a Multivector")
    return metric_inner_product(value, value)


def norm(value: Multivector) -> float:
    """Return ``sqrt(abs(norm2(value)))`` for any real metric."""
    return float(np.sqrt(abs(float(norm2(value)))))


def unit(value: Multivector, *, atol: float = 1e-15) -> Multivector:
    """Normalize a multivector by :func:`norm`."""
    magnitude = norm(value)
    if magnitude < atol:
        raise ValueError("cannot normalize a near-zero multivector")
    return value / magnitude


def inverse(
    value: Multivector,
    *,
    rtol: float = 1e-10,
    atol: float = 1e-12,
) -> Multivector:
    """Return the general inverse using the left-regular representation.

    The solve is followed by both left- and right-inverse residual checks. This
    makes the implementation basis-neutral and rejects singular or numerically
    unresolved candidates instead of returning an unchecked pseudoinverse.
    """
    if not isinstance(value, Multivector):
        raise TypeError("inverse expects a Multivector")
    identity = value.algebra.identity
    try:
        coefficients = np.linalg.solve(
            value.algebra.left_action(value),
            identity.data,
        )
        candidate = Multivector(value.algebra, coefficients)
    except (np.linalg.LinAlgError, TypeError, ValueError):
        raise ValueError("multivector is not invertible") from None
    left_residual = geometric_product(value, candidate)
    right_residual = geometric_product(candidate, value)
    if not (
        np.allclose(left_residual.data, identity.data, rtol=rtol, atol=atol)
        and np.allclose(right_residual.data, identity.data, rtol=rtol, atol=atol)
    ):
        raise ValueError("multivector is not invertible")
    return candidate


def is_scalar(value: Multivector, *, atol: float = 1e-12) -> bool:
    """Whether all nonscalar coefficients are numerically zero."""
    if not isinstance(value, Multivector):
        raise TypeError("is_scalar expects a Multivector")
    return bool(np.all(np.abs(value.data[1:]) <= atol))


def is_vector(value: Multivector, *, atol: float = 1e-12) -> bool:
    """Whether only grade-one coefficients are numerically nonzero."""
    if not isinstance(value, Multivector):
        raise TypeError("is_vector expects a Multivector")
    return bool(np.all(np.abs((value - grade(value, 1)).data) <= atol))


def is_bivector(value: Multivector, *, atol: float = 1e-12) -> bool:
    """Whether only grade-two coefficients are numerically nonzero."""
    if not isinstance(value, Multivector):
        raise TypeError("is_bivector expects a Multivector")
    return bool(np.all(np.abs((value - grade(value, 2)).data) <= atol))


def is_even(value: Multivector, *, atol: float = 1e-12) -> bool:
    """Whether every odd-grade coefficient is numerically zero."""
    if not isinstance(value, Multivector):
        raise TypeError("is_even expects a Multivector")
    return bool(np.all(np.abs(odd_grades(value).data) <= atol))


def is_rotor(value: Multivector, *, atol: float = 1e-12) -> bool:
    """Whether ``value`` is even and ``value * ~value`` is approximately one."""
    if not is_even(value, atol=atol):
        return False
    product = geometric_product(value, reverse(value))
    return bool(
        np.allclose(
            product.data,
            value.algebra.identity.data,
            rtol=0.0,
            atol=atol,
        )
    )


def is_basis_blade(value: Multivector, *, atol: float = 1e-12) -> bool:
    """Whether exactly one exterior-basis coefficient is numerically nonzero."""
    if not isinstance(value, Multivector):
        raise TypeError("is_basis_blade expects a Multivector")
    return int(np.count_nonzero(np.abs(value.data) > atol)) == 1


def sandwich(rotor: Multivector, value: Multivector) -> Multivector:
    """Return the sandwich product ``rotor * value * ~rotor``."""
    return geometric_product(geometric_product(rotor, value), reverse(rotor))


sw = sandwich


def _grade_selected_product(
    left: Multivector,
    right: Multivector,
    selector: GradeSelector,
) -> Multivector:
    """Apply a homogeneous grade-pair selector to geometric-product terms."""
    if not isinstance(left, Multivector) or not isinstance(right, Multivector):
        raise TypeError("grade-selected products expect two Multivectors")
    left._check_same(right)
    output = left.algebra._product_backend.grade_selected_product(
        left.data,
        right.data,
        selector,
    )
    return Multivector(left.algebra, output)


def _blade_name(bitmask: int) -> str:
    if bitmask == 0:
        return ""
    indices = "".join(str(index + 1) for index in set_bit_indices(bitmask))
    return f"e{indices}"


def _metric_invariants(
    gram: NDArray[np.float64],
) -> tuple[tuple[int, int, int], int, float]:
    """Return scale-aware inertia, consistent rank, and raw determinant."""
    if gram.shape == (0, 0):
        return (0, 0, 0), 0, 1.0
    eigenvalues = np.linalg.eigvalsh(gram)
    scale = float(np.max(np.abs(eigenvalues)))
    tolerance = gram.shape[0] * np.finfo(np.float64).eps * scale
    positive = int(np.count_nonzero(eigenvalues > tolerance))
    negative = int(np.count_nonzero(eigenvalues < -tolerance))
    null = gram.shape[0] - positive - negative
    determinant = float(np.linalg.det(gram))
    return (positive, negative, null), positive + negative, determinant


def _is_int(value: Any) -> bool:
    return isinstance(value, Integral) and not isinstance(value, (bool, np.bool_))


def _nonnegative_count(name: str, value: Any) -> int:
    if not _is_int(value):
        raise TypeError(f"{name} must be an integer")
    result = int(value)
    if result < 0:
        raise ValueError(f"{name} must be non-negative")
    return result


def _as_real_array(value: ArrayLike, *, name: str) -> NDArray[np.float64]:
    raw = np.asarray(value)
    if np.iscomplexobj(raw):
        raise TypeError(f"{name} must contain real values")
    try:
        result = np.asarray(value, dtype=np.float64)
    except (TypeError, ValueError) as error:
        raise TypeError(f"{name} must contain real numeric values") from error
    if not np.all(np.isfinite(result)):
        raise ValueError(f"{name} must contain only finite values")
    return result


def _normalize_signature(value: ArrayLike) -> NDArray[np.float64]:
    signature = _as_real_array(value, name="signature")
    if signature.ndim != 1:
        raise TypeError("signature must be a one-dimensional sequence")
    if signature.size == 0:
        raise ValueError("signature must contain at least one basis-vector square")
    if not np.all(np.isin(signature, (-1.0, 0.0, 1.0))):
        raise ValueError("signature values must be +1, -1, or 0")
    return signature


def _normalize_gram(value: ArrayLike) -> NDArray[np.float64]:
    gram = _as_real_array(value, name="gram")
    if gram.ndim != 2:
        raise TypeError("gram must be a two-dimensional square matrix")
    rows, columns = gram.shape
    if rows == 0 or rows != columns:
        raise ValueError("gram must be a non-empty square matrix")
    if not np.allclose(
        gram,
        gram.T,
        rtol=_SYMMETRY_RTOL,
        atol=_SYMMETRY_ATOL,
    ):
        raise ValueError("gram must be symmetric")
    return (gram + gram.T) / 2.0
