"""Product-backend, metric-metadata, and grade-selection tests."""

from __future__ import annotations

from collections.abc import Callable

import numpy as np
import pytest

from galaga.core import (
    Algebra,
    Multivector,
    doran_lasenby_inner,
    grade,
    hestenes_inner,
    left_contraction,
    metric_inner_product,
    right_contraction,
    scalar_product,
)
from galaga.core._backends import DiagonalProductBackend, LazyProductBackend
from galaga.core._metadata import bitmask_dtype, dimension_metadata


def native_cga_gram() -> np.ndarray:
    return np.array(
        [
            [1, 0, 0, 0, 0],
            [0, 1, 0, 0, 0],
            [0, 0, 1, 0, 0],
            [0, 0, 0, 0, -1],
            [0, 0, 0, -1, 0],
        ],
        dtype=np.float64,
    )


def assert_data_close(actual: Multivector, expected: Multivector) -> None:
    np.testing.assert_allclose(actual.data, expected.data, rtol=0.0, atol=1e-12)


class TestBackendSelection:
    def test_auto_selects_from_the_exact_metric(self) -> None:
        assert Algebra(3).product_backend == "diagonal"
        assert Algebra(gram=np.array([[1.0, 0.25], [0.25, 1.0]])).product_backend == "packed"

        # A small cross term must not be classified away as numerical noise.
        tiny_cross_term = np.array([[1.0, 1e-30], [1e-30, 1.0]])
        algebra = Algebra(gram=tiny_cross_term)
        e1, e2 = algebra.basis_vectors()
        assert algebra.product_backend == "packed"
        assert scalar_product(e1, e2).scalar_part == 1e-30

        dense_eight_dimensional_metric = np.eye(8) + np.full((8, 8), 0.01)
        large_algebra = Algebra(gram=dense_eight_dimensional_metric)
        assert large_algebra.product_backend == "lazy"
        assert large_algebra.packed_product_byte_estimate > 64 * 1024 * 1024
        assert large_algebra.product_cache_info == (0, 0, 64 * 1024 * 1024)

    def test_backends_can_be_selected_explicitly_for_testing(self) -> None:
        metric = np.array([[2.0, 0.5], [0.5, -1.0]])

        packed = Algebra(gram=metric, product_backend="packed")
        assert packed.product_backend == "packed"
        assert Algebra(gram=metric, product_backend="reference").product_backend == "reference"
        assert Algebra(gram=metric, product_backend="lazy").product_backend == "lazy"
        assert Algebra(2, product_backend="diagonal").product_backend == "diagonal"

        with pytest.raises(ValueError, match="requires a diagonal"):
            Algebra(gram=metric, product_backend="diagonal")
        with pytest.raises(ValueError, match="product_backend must be"):
            Algebra(2, product_backend="unknown")
        with pytest.raises(TypeError, match="must be a string"):
            Algebra(2, product_backend=42)  # type: ignore[arg-type]

    def test_dimension_metadata_is_shared_but_product_backends_are_not(self) -> None:
        first = Algebra(3)
        second = Algebra(gram=np.full((3, 3), 0.25) + np.eye(3))

        assert first._blade_grades is second._blade_grades
        assert first._grade_masks is second._grade_masks
        assert first._wedge_factor is second._wedge_factor
        assert first._product_backend is not second._product_backend

    def test_diagonal_hot_path_uses_native_numpy_indices(self) -> None:
        backend = Algebra(4)._product_backend

        assert isinstance(backend, DiagonalProductBackend)
        # NumPy otherwise converts compact unsigned indices on every fancy
        # indexing operation, roughly doubling dense-product time in Cl(1,3).
        assert backend._outputs.dtype == np.dtype(np.intp)

    def test_lazy_cache_is_bounded_and_reported(self) -> None:
        metric = np.full((4, 4), 0.25) + np.eye(4)
        uncached = LazyProductBackend(
            metric,
            dimension_metadata(4),
            cache_byte_budget=1,
        )

        action = uncached.left_action(0b0011)

        assert action.shape == (16, 16)
        assert uncached.cache_info == (0, 0, 1)

        probe = LazyProductBackend(metric, dimension_metadata(4))
        probe.left_action(0b0011)
        one_action_bytes = probe.cache_info[1]
        bounded = LazyProductBackend(
            metric,
            dimension_metadata(4),
            cache_byte_budget=one_action_bytes,
        )
        bounded.left_action(0b0011)
        assert bounded.cache_info == (1, one_action_bytes, one_action_bytes)
        bounded.left_action(0b0101)
        assert bounded.cache_info == (1, one_action_bytes, one_action_bytes)

        algebra = Algebra(gram=metric, product_backend="lazy")
        assert algebra.product_cache_info == (0, 0, 64 * 1024 * 1024)
        algebra.left_action(algebra.blade(0b0011))
        entries, used_bytes, byte_budget = algebra.product_cache_info or (0, 0, 0)
        assert entries == 1
        assert 0 < used_bytes <= byte_budget

    def test_lazy_cache_budget_rejects_ambiguous_or_negative_limits(self) -> None:
        metric = np.array([[2.0, 0.5], [0.5, 1.0]])
        metadata = dimension_metadata(2)

        for invalid in (-1, 1.5):
            with pytest.raises(ValueError, match="non-negative integer"):
                LazyProductBackend(
                    metric,
                    metadata,
                    cache_byte_budget=invalid,  # type: ignore[arg-type]
                )

    def test_output_mask_dtype_covers_each_supported_size_class(self) -> None:
        """Packed outputs must not truncate masks as dimensions grow."""
        assert bitmask_dtype(1 << 8) == np.dtype(np.uint8)
        assert bitmask_dtype((1 << 8) + 1) == np.dtype(np.uint16)
        assert bitmask_dtype((1 << 16) + 1) == np.dtype(np.uint32)
        assert bitmask_dtype((1 << 32) + 1) == np.dtype(np.uint64)

        with pytest.raises(ValueError, match="non-negative"):
            dimension_metadata(-1)


@pytest.mark.parametrize(
    "metric",
    [
        np.diag([2.5, 0.0, -3.0]),
        np.array(
            [
                [2.0, 0.25, -0.5],
                [0.25, -1.0, 0.75],
                [-0.5, 0.75, 0.5],
            ]
        ),
        native_cga_gram(),
    ],
    ids=("scaled-diagonal", "dense-oblique", "native-cga"),
)
def test_optimized_backends_match_the_dense_reference(metric: np.ndarray) -> None:
    reference = Algebra(gram=metric, product_backend="reference")
    packed = Algebra(gram=metric, product_backend="packed")
    lazy = Algebra(gram=metric, product_backend="lazy")
    optimized = Algebra(gram=metric)
    rng = np.random.default_rng(20260718 + reference.n)

    for _ in range(4):
        left_data = rng.integers(-2, 3, size=reference.dim)
        right_data = rng.integers(-2, 3, size=reference.dim)
        expected = reference.multivector(left_data) * reference.multivector(right_data)

        for algebra in (packed, lazy, optimized):
            actual = algebra.multivector(left_data) * algebra.multivector(right_data)
            np.testing.assert_allclose(
                actual.data,
                expected.data,
                rtol=0.0,
                atol=2e-11,
            )


@pytest.mark.parametrize(
    ("metric", "backend"),
    [
        (np.diag([1.0, -2.0, 0.0]), "diagonal"),
        (np.array([[2.0, 0.5], [0.5, 1.0]]), "packed"),
        (np.array([[2.0, 0.5], [0.5, 1.0]]), "lazy"),
        (np.array([[2.0, 0.5], [0.5, 1.0]]), "reference"),
    ],
)
def test_public_left_action_matches_geometric_product(
    metric: np.ndarray,
    backend: str,
) -> None:
    algebra = Algebra(gram=metric, product_backend=backend)
    left = algebra.multivector(np.arange(algebra.dim) - 2)
    right = algebra.multivector(np.arange(algebra.dim)[::-1] - 1)

    action = algebra.left_action(left)

    np.testing.assert_allclose(
        action @ right.data,
        (left * right).data,
        rtol=0.0,
        atol=1e-12,
    )
    assert not action.flags.writeable

    with pytest.raises(ValueError, match="different algebra"):
        algebra.left_action(Algebra(algebra.n).scalar(1))


class TestMetricMetadata:
    @pytest.mark.parametrize(
        ("algebra", "inertia", "rank", "determinant", "degenerate"),
        [
            (Algebra(3, 0, 1), (3, 0, 1), 3, 0.0, True),
            (
                Algebra(gram=native_cga_gram()),
                (4, 1, 0),
                5,
                -1.0,
                False,
            ),
            (
                Algebra(gram=np.array([[2.0, 1.0], [1.0, 3.0]])),
                (2, 0, 0),
                2,
                5.0,
                False,
            ),
            (Algebra(gram=np.zeros((2, 2))), (0, 0, 2), 0, 0.0, True),
        ],
    )
    def test_inertia_rank_determinant_and_degeneracy(
        self,
        algebra: Algebra,
        inertia: tuple[int, int, int],
        rank: int,
        determinant: float,
        degenerate: bool,
    ) -> None:
        assert algebra.inertia == inertia
        assert algebra.metric_rank == rank
        assert algebra.metric_determinant == pytest.approx(determinant)
        assert algebra.is_degenerate is degenerate

    def test_inertia_tolerance_is_relative_to_metric_scale(self) -> None:
        algebra = Algebra(gram=np.diag([1e-300, -2e-300]))

        assert algebra.inertia == (1, 1, 0)
        assert algebra.metric_rank == 2
        assert not algebra.is_degenerate


class TestGradeSelectedProducts:
    def test_documented_cl3_inner_product_conventions(self) -> None:
        algebra = Algebra(3)
        e1, e2, _ = algebra.basis_vectors()
        bivector = e1 ^ e2

        assert scalar_product(bivector, bivector) == -1
        assert metric_inner_product(bivector, bivector) == 1
        assert left_contraction(e1, bivector) == e2
        assert right_contraction(bivector, e1) == -e2
        assert hestenes_inner(e1, bivector) == e2
        assert hestenes_inner(bivector, e1) == -e2
        assert hestenes_inner(3 * algebra.scalar(1), e1) == 0
        assert doran_lasenby_inner(3 * algebra.scalar(1), e1) == 3 * e1
        assert (3 | e1) == 3 * e1
        assert (bivector | e1) == -e2

    def test_metric_inner_product_uses_the_full_gram_determinant(self) -> None:
        algebra = Algebra(gram=np.array([[2.0, 1.0], [1.0, 3.0]]))
        e1, e2 = algebra.basis_vectors()
        bivector = e1 ^ e2

        assert metric_inner_product(bivector, bivector) == 5
        assert scalar_product(bivector, bivector) == -5

    @pytest.mark.parametrize(
        "operation",
        (
            scalar_product,
            left_contraction,
            right_contraction,
            hestenes_inner,
            doran_lasenby_inner,
        ),
        ids=lambda operation: operation.__name__,
    )
    def test_grade_selected_products_agree_across_general_backends(
        self,
        operation: Callable[[Multivector, Multivector], Multivector],
    ) -> None:
        """The reference backend must oracle selectors as well as full products."""
        metric = np.array(
            [
                [2.0, 0.5, -0.25],
                [0.5, 1.0, 0.75],
                [-0.25, 0.75, -1.0],
            ]
        )
        results = []
        for backend in ("reference", "packed", "lazy"):
            algebra = Algebra(gram=metric, product_backend=backend)
            left = algebra.multivector(np.arange(algebra.dim) - 3)
            right = algebra.multivector(np.arange(algebra.dim)[::-1] - 2)
            results.append(operation(left, right).data)

        for result in results[1:]:
            np.testing.assert_allclose(result, results[0], rtol=0.0, atol=1e-12)

    @pytest.mark.parametrize(
        ("operation", "selector"),
        [
            (left_contraction, lambda r, s: s - r if r <= s else None),
            (right_contraction, lambda r, s: r - s if r >= s else None),
            (
                hestenes_inner,
                lambda r, s: abs(r - s) if r > 0 and s > 0 else None,
            ),
            (doran_lasenby_inner, lambda r, s: abs(r - s)),
        ],
        ids=("left", "right", "hestenes", "doran-lasenby"),
    )
    def test_mixed_grade_selection_matches_explicit_homogeneous_expansion(
        self,
        operation: Callable[[Multivector, Multivector], Multivector],
        selector: Callable[[int, int], int | None],
    ) -> None:
        algebra = Algebra(
            gram=np.array(
                [
                    [2.0, 0.5, -0.25],
                    [0.5, 1.0, 0.75],
                    [-0.25, 0.75, -1.0],
                ]
            ),
            product_backend="lazy",
        )
        left = algebra.multivector(np.arange(algebra.dim) - 3)
        right = algebra.multivector(np.arange(algebra.dim)[::-1] - 2)
        expected = algebra.scalar(0)
        for left_grade in range(algebra.n + 1):
            for right_grade in range(algebra.n + 1):
                target = selector(left_grade, right_grade)
                if target is not None:
                    expected += grade(
                        grade(left, left_grade) * grade(right, right_grade),
                        target,
                    )

        assert_data_close(operation(left, right), expected)
