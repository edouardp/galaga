"""Contracts for immutable cached matrix-representation plans."""

from __future__ import annotations

from dataclasses import FrozenInstanceError

import numpy as np
import pytest
from galaga_matrix import MatrixRepr, to_matrix, to_spinor_column
from galaga_matrix.matrix import (
    _representation_plan,
    _representation_plan_cache_clear,
    _representation_plan_cache_info,
)

from galaga.facade import Algebra


@pytest.fixture(autouse=True)
def _isolated_plan_cache():
    _representation_plan_cache_clear()
    yield
    _representation_plan_cache_clear()


@pytest.mark.parametrize(
    ("p", "q", "mode", "blade_shape", "real_rank"),
    (
        (3, 0, "compact", (8, 2, 2), 8),
        (1, 3, "compact", (16, 4, 4), 16),
        (0, 3, "compact", (8, 2, 2), 4),
        (1, 3, "quaternion", (16, 4, 4), 16),
    ),
)
def test_plan_preserves_generator_algebra_and_reconstruction_rank(
    p: int,
    q: int,
    mode: str,
    blade_shape: tuple[int, int, int],
    real_rank: int,
) -> None:
    algebra = Algebra(p, q)

    plan = _representation_plan(algebra, mode)

    assert plan.blade_matrices is not None
    assert plan.system_matrix is not None
    assert plan.blade_matrices.shape == blade_shape
    assert plan.real_rank == real_rank
    assert plan.is_injective is (real_rank == algebra.dim)
    np.testing.assert_array_equal(plan.coefficient_indices, np.arange(algebra.dim))

    identity = np.eye(plan.matrix_shape[0], dtype=complex)
    for row, left in enumerate(plan.generators):
        for column, right in enumerate(plan.generators):
            np.testing.assert_allclose(
                left @ right + right @ left,
                2.0 * algebra.gram[row, column] * identity,
                rtol=0.0,
                atol=1e-12,
            )


def test_left_regular_plan_keeps_the_public_action_lazy() -> None:
    algebra = Algebra(gram=np.array([[2.0, 0.5], [0.5, -1.0]]))

    plan = _representation_plan(algebra, "left-regular")

    assert plan.matrix_shape == (algebra.dim, algebra.dim)
    assert plan.generators == ()
    assert plan.blade_matrices is None
    assert plan.system_matrix is None
    assert plan.is_injective
    assert to_matrix(algebra.identity).mode == "left-regular"


def test_repeated_conversions_reuse_one_bounded_plan() -> None:
    algebra = Algebra(3)
    e1, e2, _ = algebra.basis_vectors()

    first = _representation_plan(algebra, "compact")
    to_matrix(e1, mode="compact")
    to_matrix(e2, mode="compact")
    second = _representation_plan(algebra, "compact")
    cache_info = _representation_plan_cache_info()

    assert first is second
    assert cache_info.maxsize == 64
    assert cache_info.currsize == 1
    assert cache_info.hits >= 3


def test_presentation_views_share_the_numeric_representation_plan() -> None:
    algebra = Algebra(3)
    presentation_view = algebra.with_presentation(algebra.presentation)

    original = _representation_plan(algebra, "compact")
    shared = _representation_plan(presentation_view, "compact")

    assert original is shared
    assert original.source_algebra is algebra.numeric


def test_modes_have_distinct_stable_descriptors() -> None:
    algebra = Algebra(1, 3)

    compact = _representation_plan(algebra, "compact")
    quaternion = _representation_plan(algebra, "quaternion")

    assert compact is not quaternion
    assert compact.descriptor.basis == "dirac"
    assert compact.descriptor.convention == "orthogonal-compact-v1"
    assert quaternion.descriptor.basis is None
    assert quaternion.descriptor.convention == "quaternion-block-v1"


def test_cached_plan_and_all_numeric_arrays_are_immutable() -> None:
    plan = _representation_plan(Algebra(3), "compact")
    assert plan.blade_matrices is not None
    assert plan.system_matrix is not None

    with pytest.raises(FrozenInstanceError):
        plan.real_rank = 0  # type: ignore[misc]
    with pytest.raises(FrozenInstanceError):
        plan.descriptor.mode = "left-regular"  # type: ignore[misc]
    with pytest.raises(ValueError, match="read-only"):
        plan.generators[0][0, 0] = 10
    with pytest.raises(ValueError, match="read-only"):
        plan.blade_matrices[0, 0, 0] = 10
    with pytest.raises(ValueError, match="read-only"):
        plan.coefficient_indices[0] = 10
    with pytest.raises(ValueError, match="read-only"):
        plan.system_matrix[0, 0] = 10


def test_general_gram_compact_plan_records_the_metric_congruence() -> None:
    algebra = Algebra(gram=np.array([[2.0, 0.5], [0.5, -1.0]]))

    plan = _representation_plan(algebra, "compact")

    assert plan.metric_congruence is not None
    assert plan.descriptor.basis is None
    assert plan.descriptor.convention == "general-gram-congruence-v1"
    assert plan.metric_congruence.inertia == algebra.inertia
    np.testing.assert_allclose(
        plan.metric_congruence.transform
        @ plan.metric_congruence.orthogonal_metric
        @ plan.metric_congruence.transform.T,
        algebra.gram,
        rtol=0.0,
        atol=plan.metric_congruence.tolerance,
    )


def test_matrix_repr_records_and_propagates_the_full_source_domain() -> None:
    algebra = Algebra(3)
    e1, _, _ = algebra.basis_vectors(expr=True)

    matrix = to_matrix(e1, mode="compact")

    assert matrix.domain == "full"
    assert matrix.expr is not None
    assert matrix.expr.domain == "full"
    assert MatrixRepr(matrix).domain == "full"
    assert (matrix + matrix).domain == "full"


def test_spinor_column_records_and_propagates_the_even_source_domain() -> None:
    algebra = Algebra(1, 3)
    scalar = algebra.scalar(1.0, expr=True)

    spinor = to_spinor_column(scalar)

    assert spinor.domain == "even"
    assert spinor.expr is not None
    assert spinor.expr.domain == "even"
    assert spinor.H.domain == "even"
    assert spinor.to_basis("weyl").domain == "even"


def test_matrix_repr_rejects_an_unknown_source_domain() -> None:
    with pytest.raises(ValueError, match="domain must be 'full' or 'even'"):
        MatrixRepr(np.eye(2), domain="odd")
