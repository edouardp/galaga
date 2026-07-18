"""General-Gram metric extensions and RGA convention-layer identities."""

from __future__ import annotations

from itertools import product
from math import prod

import numpy as np
import pytest

from galaga.core import (
    Algebra,
    Multivector,
    antidot_product,
    antimetric_apply,
    antireverse,
    antiwedge,
    bulk_part,
    complement,
    dual,
    geometric_antiproduct,
    left_complement,
    left_hodge_dual,
    left_interior_product,
    left_weight_dual,
    meet,
    metric_apply,
    metric_inner_product,
    metric_regressive_product,
    outer_product,
    regressive_product,
    right_complement,
    right_hodge_dual,
    right_interior_product,
    right_weight_dual,
    transwedge,
    transwedge_antiproduct,
    uncomplement,
    undual,
    weight_part,
)


def assert_mv_close(
    actual: Multivector,
    expected: Multivector | float | int,
    *,
    atol: float = 1e-11,
) -> None:
    if not isinstance(expected, Multivector):
        expected = actual.algebra.scalar(expected)
    assert actual.algebra is expected.algebra
    np.testing.assert_allclose(actual.data, expected.data, rtol=0.0, atol=atol)


def basis_blades(algebra: Algebra) -> tuple[Multivector, ...]:
    return tuple(algebra.blade(bitmask) for bitmask in range(algebra.dim))


class TestExteriorMetricMatrices:
    def test_oblique_metric_and_antimetric_are_compound_and_complementary(self) -> None:
        algebra = Algebra(gram=np.array([[2.0, 1.0], [1.0, 3.0]]))

        assert algebra._extended_metric is None
        assert algebra._antimetric is None
        metric = algebra.extended_metric_matrix()
        antimetric = algebra.metric_antiexomorphism_matrix()

        np.testing.assert_array_equal(
            metric,
            np.array(
                [
                    [1, 0, 0, 0],
                    [0, 2, 1, 0],
                    [0, 1, 3, 0],
                    [0, 0, 0, 5],
                ],
                dtype=float,
            ),
        )
        np.testing.assert_array_equal(
            antimetric,
            np.array(
                [
                    [5, 0, 0, 0],
                    [0, 3, -1, 0],
                    [0, -1, 2, 0],
                    [0, 0, 0, 1],
                ],
                dtype=float,
            ),
        )
        np.testing.assert_array_equal(metric @ antimetric, 5 * np.eye(4))
        assert algebra.extended_metric_matrix() is metric
        assert algebra.metric_antiexomorphism_matrix() is antimetric
        assert not metric.flags.writeable
        assert not antimetric.flags.writeable

    @pytest.mark.parametrize(
        "gram",
        [
            np.diag([1.0, -2.0, 0.5]),
            np.array(
                [
                    [2.0, 0.5, -0.25],
                    [0.5, -1.0, 0.75],
                    [-0.25, 0.75, 1.5],
                ]
            ),
            np.array([[1.0, 1.0], [1.0, 1.0]]),
        ],
        ids=("diagonal", "dense", "singular-oblique"),
    )
    def test_metric_times_antimetric_is_determinant_identity(
        self,
        gram: np.ndarray,
    ) -> None:
        algebra = Algebra(gram=gram)
        metric = algebra.extended_metric_matrix()
        antimetric = algebra.metric_antiexomorphism_matrix()

        np.testing.assert_allclose(
            metric @ antimetric,
            algebra.metric_determinant * np.eye(algebra.dim),
            rtol=0.0,
            atol=2e-12,
        )

    def test_metric_pairing_matches_the_compound_matrix_for_dense_values(self) -> None:
        algebra = Algebra(
            gram=np.array(
                [
                    [2.0, 0.5, -0.25],
                    [0.5, -1.0, 0.75],
                    [-0.25, 0.75, 1.5],
                ]
            )
        )
        rng = np.random.default_rng(20260718)
        left = algebra.multivector(rng.standard_normal(algebra.dim))
        right = algebra.multivector(rng.standard_normal(algebra.dim))
        expected = float(left.data @ algebra.extended_metric_matrix() @ right.data)

        assert metric_inner_product(left, right).scalar_part == pytest.approx(
            expected,
            abs=2e-12,
        )


@pytest.mark.parametrize("n", range(0, 6))
def test_complement_identities_exhaustively(n: int) -> None:
    algebra = Algebra(n)
    for mask, blade in enumerate(basis_blades(algebra)):
        blade_grade = mask.bit_count()
        antigrade = n - blade_grade

        assert outer_product(blade, right_complement(blade)) == algebra.I
        assert outer_product(left_complement(blade), blade) == algebra.I
        assert left_complement(blade) == ((-1) ** (blade_grade * antigrade)) * right_complement(blade)
        assert left_complement(right_complement(blade)) == blade
        assert right_complement(left_complement(blade)) == blade
        assert uncomplement(complement(blade)) == blade


RGA_ALGEBRAS = (
    Algebra(3, id="euclidean"),
    Algebra(1, 2, id="indefinite"),
    Algebra(signature=[1, 1, 1, 0], id="pga"),
    Algebra(gram=np.array([[2.0, 0.5], [0.5, -1.0]]), id="oblique"),
)


@pytest.mark.parametrize("algebra", RGA_ALGEBRAS, ids=lambda algebra: algebra.id)
def test_hodge_and_antidot_identities_exhaustively(algebra: Algebra) -> None:
    blades = basis_blades(algebra)
    determinant = algebra.metric_determinant

    for mask, left in enumerate(blades):
        blade_grade = mask.bit_count()
        square_factor = (-1) ** (blade_grade * (algebra.n - blade_grade)) * determinant
        assert_mv_close(
            right_hodge_dual(right_hodge_dual(left)),
            square_factor * left,
        )
        assert_mv_close(
            left_hodge_dual(left_hodge_dual(left)),
            square_factor * left,
        )

        for right_mask, right in enumerate(blades):
            expected_antidot = complement(
                metric_inner_product(
                    left_complement(left),
                    left_complement(right),
                )
            )
            assert_mv_close(antidot_product(left, right), expected_antidot)
            if mask.bit_count() == right_mask.bit_count():
                pairing = metric_inner_product(left, right) * algebra.I
                assert_mv_close(
                    outer_product(left, right_hodge_dual(right)),
                    pairing,
                )
                assert_mv_close(
                    outer_product(left_hodge_dual(left), right),
                    pairing,
                )


@pytest.mark.parametrize("algebra", RGA_ALGEBRAS, ids=lambda algebra: algebra.id)
def test_weight_dual_and_antiproduct_identities_exhaustively(
    algebra: Algebra,
) -> None:
    determinant = algebra.metric_determinant
    for mask, blade in enumerate(basis_blades(algebra)):
        blade_grade = mask.bit_count()
        square_factor = (-1) ** (blade_grade * (algebra.n - blade_grade)) * determinant

        assert_mv_close(
            right_weight_dual(blade),
            geometric_antiproduct(antireverse(blade), algebra.identity),
        )
        assert_mv_close(
            right_weight_dual(right_weight_dual(blade)),
            square_factor * blade,
        )
        assert_mv_close(
            left_weight_dual(left_weight_dual(blade)),
            square_factor * blade,
        )
        assert_mv_close(
            geometric_antiproduct(blade, antireverse(blade)),
            antidot_product(blade, blade),
        )
        assert_mv_close(geometric_antiproduct(blade, algebra.I), blade)
        assert_mv_close(geometric_antiproduct(algebra.I, blade), blade)


def test_pga_bulk_and_weight_parts_are_complementary() -> None:
    algebra = Algebra(signature=[1, 1, 1, 0])
    rng = np.random.default_rng(71)
    value = algebra.multivector(rng.integers(-5, 6, size=algebra.dim))
    bulk = bulk_part(value)
    weight = weight_part(value)

    assert bulk == metric_apply(value)
    assert weight == antimetric_apply(value)
    assert bulk + weight == value
    for bitmask in range(algebra.dim):
        if bitmask & 0b1000:
            assert bulk.data[bitmask] == 0
        else:
            assert weight.data[bitmask] == 0


@pytest.mark.parametrize("algebra", RGA_ALGEBRAS, ids=lambda algebra: algebra.id)
def test_regressive_and_interior_identities_exhaustively(algebra: Algebra) -> None:
    blades = basis_blades(algebra)
    for left, right in product(blades, repeat=2):
        expected_regressive = uncomplement(outer_product(complement(left), complement(right)))
        assert regressive_product(left, right) == expected_regressive
        assert antiwedge(left, right) == expected_regressive
        assert meet(left, right) == expected_regressive

        if left.homogeneous_grade() == right.homogeneous_grade():
            pairing = metric_inner_product(left, right)
            assert_mv_close(left_interior_product(left, right), pairing)
            assert_mv_close(right_interior_product(left, right), pairing)

    for vector, blade in product(algebra.basis_vectors(), blades):
        assert_mv_close(
            vector * blade,
            outer_product(vector, blade) + right_interior_product(blade, vector),
        )
        assert_mv_close(
            blade * vector,
            outer_product(blade, vector) + left_interior_product(vector, blade),
        )


def test_metric_dual_and_regressive_require_a_nondegenerate_metric() -> None:
    algebra = Algebra(gram=np.array([[2.0, 0.5], [0.5, -1.0]]))
    blades = basis_blades(algebra)
    for blade in blades:
        assert_mv_close(undual(dual(blade)), blade)

    expected = undual(outer_product(dual(blades[1]), dual(blades[2])))
    assert_mv_close(metric_regressive_product(blades[1], blades[2]), expected)

    pga = Algebra(signature=[1, 1, 1, 0])
    with pytest.raises(ValueError, match="invertible pseudoscalar"):
        dual(pga.basis_vectors()[0])
    with pytest.raises(ValueError, match="invertible pseudoscalar"):
        metric_regressive_product(pga.blade(0b0011), pga.blade(0b0110))


@pytest.mark.parametrize("algebra", RGA_ALGEBRAS, ids=lambda algebra: algebra.id)
def test_transwedge_families_reconstruct_products_exhaustively(
    algebra: Algebra,
) -> None:
    for left, right in product(basis_blades(algebra), repeat=2):
        geometric_total = algebra.scalar(0)
        antiproduct_total = algebra.scalar(0)
        for order in range(algebra.n + 1):
            factor = (-1) ** (order * (order - 1) // 2)
            geometric_total += factor * transwedge(left, right, order)
            antiproduct_total += factor * transwedge_antiproduct(
                left,
                right,
                order,
            )

        assert_mv_close(transwedge(left, right, 0), outer_product(left, right))
        assert_mv_close(geometric_total, left * right)
        assert_mv_close(
            antiproduct_total,
            geometric_antiproduct(left, right),
        )
        assert_mv_close(
            transwedge(left, right, left.homogeneous_grade()),
            right_interior_product(right, left),
        )


@pytest.mark.parametrize(
    ("order", "error"),
    [(-1, ValueError), (0.5, TypeError), (True, TypeError)],
)
def test_transwedge_rejects_invalid_orders(
    order: object,
    error: type[Exception],
) -> None:
    algebra = Algebra(2)
    e1, e2 = algebra.basis_vectors()

    with pytest.raises(error):
        transwedge(e1, e2, order)  # type: ignore[arg-type]
    with pytest.raises(error):
        transwedge_antiproduct(e1, e2, order)  # type: ignore[arg-type]


def test_diagonal_metric_and_antimetric_use_present_and_absent_squares() -> None:
    signature = (1, -1, 0, 2)
    algebra = Algebra(gram=np.diag(signature))
    metric = algebra.extended_metric_matrix()
    antimetric = algebra.metric_antiexomorphism_matrix()

    for bitmask in range(algebra.dim):
        present = [signature[index] for index in range(algebra.n) if bitmask & (1 << index)]
        absent = [signature[index] for index in range(algebra.n) if not bitmask & (1 << index)]
        assert metric[bitmask, bitmask] == prod(present)
        assert antimetric[bitmask, bitmask] == prod(absent)
