"""Composition-based numeric facade over :mod:`gram`.

This is the first migration slice.  Values contain only a concrete Gram value
and an owning facade algebra; names, expression provenance, conventions, and
rendering are intentionally absent.
"""

from __future__ import annotations

from collections.abc import Iterable
from numbers import Integral, Real
from types import NotImplementedType
from typing import Any, cast

import gram
import numpy as np

from .catalog import LeftFoldCall, get_operation


class Algebra:
    """A lightweight owner of one immutable :class:`gram.Algebra`."""

    __slots__ = ("_basis_vectors", "_numeric")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self._numeric = gram.Algebra(*args, **kwargs)
        self._basis_vectors: tuple[Multivector, ...] | None = None

    @classmethod
    def from_numeric(cls, numeric: gram.Algebra) -> Algebra:
        """Create a facade over an existing numeric algebra."""
        if not isinstance(numeric, gram.Algebra):
            raise TypeError("numeric must be a gram.Algebra")
        instance = cls.__new__(cls)
        instance._numeric = numeric
        instance._basis_vectors = None
        return instance

    @property
    def numeric(self) -> gram.Algebra:
        """The wrapped numeric algebra."""
        return self._numeric

    @property
    def gram(self) -> np.ndarray:
        return cast(np.ndarray, self._numeric.gram)

    @property
    def basis_squares(self) -> np.ndarray:
        return cast(np.ndarray, self._numeric.basis_squares)

    @property
    def n(self) -> int:
        return self._numeric.n

    @property
    def dim(self) -> int:
        return self._numeric.dim

    @property
    def inertia(self) -> tuple[int, int, int]:
        return self._numeric.inertia

    @property
    def metric_rank(self) -> int:
        return self._numeric.metric_rank

    @property
    def metric_determinant(self) -> float:
        return self._numeric.metric_determinant

    @property
    def is_degenerate(self) -> bool:
        return self._numeric.is_degenerate

    @property
    def is_orthogonal_basis(self) -> bool:
        return self._numeric.is_orthogonal_basis

    @property
    def product_backend(self) -> str:
        return self._numeric.product_backend

    @property
    def identity(self) -> Multivector:
        return self._wrap(self._numeric.identity)

    @property
    def I(self) -> Multivector:  # noqa: E743 - conventional pseudoscalar name
        return self.pseudoscalar()

    def _wrap(self, value: gram.Multivector) -> Multivector:
        if not isinstance(value, gram.Multivector):
            raise TypeError("facade can only wrap a gram.Multivector")
        if value.algebra is not self._numeric:
            raise ValueError("numeric multivector belongs to a different algebra")
        return Multivector(self, value)

    def multivector(self, data: Any) -> Multivector:
        return self._wrap(self._numeric.multivector(data))

    def scalar(self, value: Real) -> Multivector:
        return self._wrap(self._numeric.scalar(value))

    def vector(self, values: Any) -> Multivector:
        return self._wrap(self._numeric.vector(values))

    def blade(self, bitmask: int) -> Multivector:
        return self._wrap(self._numeric.blade(bitmask))

    def basis_vectors(self) -> tuple[Multivector, ...]:
        if self._basis_vectors is None:
            self._basis_vectors = tuple(self._wrap(value) for value in self._numeric.basis_vectors())
        return self._basis_vectors

    def basis_blades(self, value: int) -> tuple[Multivector, ...]:
        return tuple(self._wrap(blade) for blade in self._numeric.basis_blades(value))

    def pseudoscalar(self) -> Multivector:
        return self._wrap(self._numeric.pseudoscalar())

    def left_action(self, value: Multivector) -> np.ndarray:
        self._check_value(value)
        return cast(np.ndarray, self._numeric.left_action(value.numeric))

    def extended_metric_matrix(self) -> np.ndarray:
        return cast(np.ndarray, self._numeric.extended_metric_matrix())

    def metric_antiexomorphism_matrix(self) -> np.ndarray:
        return cast(np.ndarray, self._numeric.metric_antiexomorphism_matrix())

    def _check_value(self, value: Multivector) -> None:
        if not isinstance(value, Multivector):
            raise TypeError("expected a Gram facade Multivector")
        if value.numeric.algebra is not self._numeric:
            raise ValueError("multivector belongs to a different numeric algebra")

    def __repr__(self) -> str:
        return f"Algebra(numeric={self._numeric!r})"


class Multivector:
    """An immutable facade value containing one concrete Gram multivector."""

    __slots__ = ("_algebra", "_numeric")

    def __init__(self, algebra: Algebra, numeric: gram.Multivector) -> None:
        if not isinstance(algebra, Algebra):
            raise TypeError("algebra must be a Gram facade Algebra")
        if not isinstance(numeric, gram.Multivector):
            raise TypeError("numeric must be a gram.Multivector")
        if numeric.algebra is not algebra.numeric:
            raise ValueError("numeric multivector belongs to a different algebra")
        self._algebra = algebra
        self._numeric = numeric

    @property
    def algebra(self) -> Algebra:
        return self._algebra

    @property
    def numeric(self) -> gram.Multivector:
        return self._numeric

    @property
    def data(self) -> np.ndarray:
        return cast(np.ndarray, self._numeric.data)

    @property
    def vector_part(self) -> np.ndarray:
        return cast(np.ndarray, self._numeric.vector_part)

    def coefficient(self, bitmask: int) -> float:
        return self._numeric.coefficient(bitmask)

    def homogeneous_grade(self, *, atol: float = 1e-12) -> int | None:
        return self._numeric.homogeneous_grade(atol=atol)

    def almost_equal(self, other: Multivector, *, atol: float = 1e-12) -> bool:
        return (
            isinstance(other, Multivector)
            and self._numeric.algebra is other._numeric.algebra
            and self._numeric.almost_equal(other._numeric, atol=atol)
        )

    def grade(self, value: int) -> Multivector:
        return grade(self, value)

    def _coerce_additive(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Multivector):
            return other
        if isinstance(other, Real):
            return self._algebra.scalar(other)
        return NotImplemented

    def __add__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return _invoke("add", self, converted)

    def __radd__(self, other: object) -> Multivector | NotImplementedType:
        return self.__add__(other)

    def __sub__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return _invoke("subtract", self, converted)

    def __rsub__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return _invoke("subtract", converted, self)

    def __neg__(self) -> Multivector:
        return _invoke("negate", self)

    def __pos__(self) -> Multivector:
        return self

    def __mul__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Multivector):
            return geometric_product(self, other)
        if isinstance(other, Real):
            return _invoke("scalar_multiply", self, other)
        return NotImplemented

    def __rmul__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Real):
            return _invoke("scalar_multiply", self, other)
        if isinstance(other, Multivector):
            return geometric_product(other, self)
        return NotImplemented

    def __truediv__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Real):
            return _invoke("scalar_divide", self, other)
        if isinstance(other, Multivector):
            return geometric_product(self, inverse(other))
        return NotImplemented

    def __rtruediv__(self, other: object) -> Multivector | NotImplementedType:
        if isinstance(other, Real):
            return geometric_product(self._algebra.scalar(other), inverse(self))
        return NotImplemented

    def __pow__(self, exponent: object) -> Multivector | NotImplementedType:
        if not isinstance(exponent, Integral) or isinstance(exponent, (bool, np.bool_)):
            return NotImplemented
        return _invoke("power", self, exponent)

    def __xor__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return outer_product(self, converted)

    def __rxor__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return outer_product(converted, self)

    def __or__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return doran_lasenby_inner(self, converted)

    def __ror__(self, other: object) -> Multivector | NotImplementedType:
        converted = self._coerce_additive(other)
        if converted is NotImplemented:
            return NotImplemented
        return doran_lasenby_inner(converted, self)

    def __invert__(self) -> Multivector:
        return reverse(self)

    def __getitem__(self, value: int | str) -> Multivector:
        return grade(self, value)

    def __float__(self) -> float:
        return float(self._numeric)

    def __abs__(self) -> float:
        return abs(self._numeric)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Multivector):
            return self._numeric == other._numeric
        if isinstance(other, Real):
            return self._numeric == other
        return False

    def __hash__(self) -> int:
        return hash(self._numeric)

    def __repr__(self) -> str:
        return f"Multivector(numeric={self._numeric!r})"


def _invoke(operation_id: str, *args: Any, **kwargs: Any) -> Any:
    operation = get_operation(operation_id)
    if isinstance(operation.call_policy, LeftFoldCall) and len(args) == 1 and isinstance(args[0], Multivector):
        return args[0]

    owner: Algebra | None = None
    numeric_args: list[Any] = []
    for argument in args:
        if isinstance(argument, Multivector):
            if owner is None:
                owner = argument.algebra
            elif argument.numeric.algebra is not owner.numeric:
                raise ValueError("cannot mix multivectors from different algebras")
            numeric_args.append(argument.numeric)
        else:
            numeric_args.append(argument)

    result = operation.invoke(*numeric_args, **kwargs)
    if isinstance(result, gram.Multivector):
        if owner is None:
            raise RuntimeError(f"{operation_id} produced a value without an owner")
        return owner._wrap(result)
    return result


def geometric_product(*values: Multivector) -> Multivector:
    return _invoke("geometric_product", *values)


def outer_product(*values: Multivector) -> Multivector:
    return _invoke("outer_product", *values)


def grade(value: Multivector, target: int | str) -> Multivector:
    return _invoke("grade", value, target)


def grades(value: Multivector, targets: Iterable[int]) -> Multivector:
    return _invoke("grades", value, targets)


def scalar_part(value: Multivector) -> float:
    """Optional shorthand for ``float(grade(value, 0))``."""
    return float(grade(value, 0))


def scalar_product(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("scalar_product", left, right)


def metric_inner_product(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("metric_inner_product", left, right)


def left_contraction(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("left_contraction", left, right)


def right_contraction(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("right_contraction", left, right)


def hestenes_inner(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("hestenes_inner", left, right)


def doran_lasenby_inner(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("doran_lasenby_inner", left, right)


def commutator(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("commutator", left, right)


def anticommutator(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("anticommutator", left, right)


def half_commutator(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("half_commutator", left, right)


def half_anticommutator(left: Multivector, right: Multivector) -> Multivector:
    return _invoke("half_anticommutator", left, right)


def reverse(value: Multivector) -> Multivector:
    return _invoke("reverse", value)


def involute(value: Multivector) -> Multivector:
    return _invoke("involute", value)


def conjugate(value: Multivector) -> Multivector:
    return _invoke("conjugate", value)


def complement(value: Multivector) -> Multivector:
    return _invoke("complement", value)


def dual(value: Multivector) -> Multivector:
    return _invoke("dual", value)


def inverse(
    value: Multivector,
    *,
    rtol: float = 1e-10,
    atol: float = 1e-12,
) -> Multivector:
    return _invoke("inverse", value, rtol=rtol, atol=atol)


def squared(value: Multivector) -> Multivector:
    return _invoke("squared", value)


def norm2(value: Multivector) -> Multivector:
    return _invoke("norm2", value)


def norm(value: Multivector) -> float:
    return _invoke("norm", value)


def unit(value: Multivector, *, atol: float = 1e-15) -> Multivector:
    return _invoke("unit", value, atol=atol)


def exp(value: Multivector) -> Multivector:
    return _invoke("exp", value)


def log(value: Multivector, *, atol: float = 1e-12) -> Multivector:
    return _invoke("log", value, atol=atol)


__all__ = [
    "Algebra",
    "Multivector",
    "anticommutator",
    "commutator",
    "complement",
    "conjugate",
    "doran_lasenby_inner",
    "dual",
    "exp",
    "geometric_product",
    "grade",
    "grades",
    "half_anticommutator",
    "half_commutator",
    "hestenes_inner",
    "inverse",
    "involute",
    "left_contraction",
    "log",
    "metric_inner_product",
    "norm",
    "norm2",
    "outer_product",
    "reverse",
    "right_contraction",
    "scalar_part",
    "scalar_product",
    "squared",
    "unit",
]
