"""Immutable descriptors and cached-data containers for matrix representations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

import numpy as np
from numpy.typing import NDArray

RepresentationDomain = Literal["full", "even"]

_VALID_DOMAINS = frozenset({"full", "even"})


def normalize_domain(domain: str) -> RepresentationDomain:
    """Validate and normalize a matrix representation source domain."""
    if domain not in _VALID_DOMAINS:
        raise ValueError("domain must be 'full' or 'even'")
    return domain  # type: ignore[return-value]


def _readonly_array(value: Any) -> NDArray[Any]:
    result = np.array(value, copy=True)
    result.setflags(write=False)
    return result


@dataclass(frozen=True, slots=True)
class RepresentationDescriptor:
    """Stable identity for one matrix representation convention."""

    mode: str
    domain: RepresentationDomain
    basis: str | None
    convention: str
    dtype: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "domain", normalize_domain(self.domain))
        if not self.mode:
            raise ValueError("representation mode must not be empty")
        if not self.convention:
            raise ValueError("representation convention must not be empty")
        if not self.dtype:
            raise ValueError("representation dtype must not be empty")


@dataclass(frozen=True, slots=True, eq=False)
class MetricCongruence:
    """Validated factorization ``G = S eta S.T`` for a native Gram basis."""

    gram: NDArray[np.float64]
    inertia: tuple[int, int, int]
    transform: NDArray[np.float64]
    orthogonal_metric: NDArray[np.float64]
    inverse_transform: NDArray[np.float64]
    residual: float
    condition_estimate: float
    tolerance: float
    convention: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "gram", _readonly_array(self.gram).astype(np.float64, copy=False))
        object.__setattr__(self, "transform", _readonly_array(self.transform).astype(np.float64, copy=False))
        object.__setattr__(
            self,
            "orthogonal_metric",
            _readonly_array(self.orthogonal_metric).astype(np.float64, copy=False),
        )
        object.__setattr__(
            self,
            "inverse_transform",
            _readonly_array(self.inverse_transform).astype(np.float64, copy=False),
        )
        for field_name in ("gram", "transform", "orthogonal_metric", "inverse_transform"):
            getattr(self, field_name).setflags(write=False)
        if self.gram.ndim != 2 or self.gram.shape[0] != self.gram.shape[1]:
            raise ValueError("metric-congruence Gram matrix must be square")
        dimension = self.gram.shape[0]
        expected_shape = (dimension, dimension)
        if self.transform.shape != expected_shape:
            raise ValueError("metric-congruence transform must match the Gram matrix")
        if self.orthogonal_metric.shape != expected_shape:
            raise ValueError("metric-congruence orthogonal metric must match the Gram matrix")
        if self.inverse_transform.shape != expected_shape:
            raise ValueError("metric-congruence inverse transform must match the Gram matrix")
        if sum(self.inertia) != dimension or any(value < 0 for value in self.inertia):
            raise ValueError("metric-congruence inertia must match the Gram-matrix dimension")
        if (
            not np.isfinite(self.residual)
            or not np.isfinite(self.condition_estimate)
            or not np.isfinite(self.tolerance)
            or self.residual < 0
            or self.condition_estimate < 1
            or self.tolerance <= 0
        ):
            raise ValueError("invalid metric-congruence diagnostics")
        if not self.convention:
            raise ValueError("metric-congruence convention must not be empty")


@dataclass(frozen=True, slots=True, eq=False)
class MatrixRepresentationPlan:
    """Immutable algebra-derived data shared by repeated conversions.

    ``blade_matrices`` and ``system_matrix`` are absent for left-regular mode,
    whose public algebra action is already the direct conversion algorithm.
    Compact-family plans own read-only snapshots so callers cannot corrupt a
    cached conversion basis.
    """

    source_algebra: Any
    descriptor: RepresentationDescriptor
    metric_congruence: MetricCongruence | None
    matrix_shape: tuple[int, int]
    generators: tuple[NDArray[Any], ...]
    blade_matrices: NDArray[Any] | None
    coefficient_indices: NDArray[np.int64]
    system_matrix: NDArray[Any] | None
    real_rank: int
    rank_tolerance: float
    inverse_tolerance: float

    def __post_init__(self) -> None:
        if len(self.matrix_shape) != 2 or any(size < 1 for size in self.matrix_shape):
            raise ValueError("matrix_shape must contain two positive dimensions")
        generators = tuple(_readonly_array(generator) for generator in self.generators)
        coefficient_indices = _readonly_array(self.coefficient_indices).astype(np.int64, copy=False)
        coefficient_indices.setflags(write=False)
        object.__setattr__(self, "generators", generators)
        object.__setattr__(self, "coefficient_indices", coefficient_indices)
        if self.blade_matrices is not None:
            object.__setattr__(self, "blade_matrices", _readonly_array(self.blade_matrices))
        if self.system_matrix is not None:
            object.__setattr__(self, "system_matrix", _readonly_array(self.system_matrix))
        if self.real_rank < 0 or self.real_rank > len(coefficient_indices):
            raise ValueError("real_rank must lie within the represented coefficient domain")
        if self.rank_tolerance <= 0 or self.inverse_tolerance <= 0:
            raise ValueError("representation tolerances must be positive")

    @property
    def is_injective(self) -> bool:
        """Whether the represented real coefficient domain has full rank."""
        return self.real_rank == len(self.coefficient_indices)

    @property
    def conversion_basis(self) -> NDArray[Any]:
        """Return exterior-blade matrices for a compact-family plan."""
        if self.blade_matrices is None:
            raise RuntimeError("left-regular plans use the algebra's public left action")
        return self.blade_matrices

    @property
    def reconstruction_system(self) -> NDArray[Any]:
        """Return the real coefficient system for a compact-family plan."""
        if self.system_matrix is None:
            raise RuntimeError("left-regular plans do not use a reconstruction system")
        return self.system_matrix
