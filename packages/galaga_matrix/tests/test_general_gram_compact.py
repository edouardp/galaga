"""Algebra-first contracts for compact representations of general Gram bases."""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from itertools import permutations
from math import factorial

import numpy as np
import pytest
from galaga_matrix import from_matrix, to_matrix, to_spinor_column
from galaga_matrix.matrix import _representation_plan

from galaga import p_cga
from galaga.cga import ConformalModel
from galaga.facade import Algebra, geometric_product, outer_product


def _permutation_sign(values: tuple[int, ...]) -> int:
    inversions = sum(
        values[left] > values[right] for left in range(len(values)) for right in range(left + 1, len(values))
    )
    return -1 if inversions % 2 else 1


def _antisymmetrized_product(generators: tuple[np.ndarray, ...], mask: int) -> np.ndarray:
    indices = tuple(index for index in range(len(generators)) if mask & (1 << index))
    if not indices:
        return np.eye(generators[0].shape[0], dtype=complex)

    result = np.zeros_like(generators[0])
    for order in permutations(range(len(indices))):
        term = np.eye(generators[0].shape[0], dtype=complex)
        for position in order:
            term = term @ generators[indices[position]]
        result += _permutation_sign(order) * term
    return result / factorial(len(indices))


def _dense_gram(signature: tuple[int, ...], transform: np.ndarray) -> np.ndarray:
    metric = np.diag(np.asarray(signature, dtype=float))
    return transform @ metric @ transform.T


@pytest.mark.parametrize(
    "gram",
    (
        np.diag([2.0, -3.0]),
        np.array([[2.0, 0.5], [0.5, -1.0]]),
        np.array([[0.0, -1.0], [-1.0, 0.0]]),
    ),
)
def test_native_generators_reproduce_the_supplied_gram_matrix(gram: np.ndarray) -> None:
    algebra = Algebra(gram=gram)
    plan = _representation_plan(algebra, "compact")
    identity = np.eye(plan.matrix_shape[0], dtype=complex)

    for row, left in enumerate(plan.generators):
        for column, right in enumerate(plan.generators):
            np.testing.assert_allclose(
                left @ right + right @ left,
                2.0 * gram[row, column] * identity,
                rtol=0.0,
                atol=1e-12,
            )


def test_nonorthogonal_bivector_is_the_antisymmetrized_not_ordered_product() -> None:
    gram = np.array([[2.0, 0.5], [0.5, -1.0]])
    algebra = Algebra(gram=gram)
    e0, e1 = algebra.basis_vectors()
    plan = _representation_plan(algebra, "compact")
    left, right = plan.generators
    identity = np.eye(plan.matrix_shape[0], dtype=complex)

    bivector = np.asarray(to_matrix(outer_product(e0, e1), mode="compact"))

    np.testing.assert_allclose(bivector, 0.5 * (left @ right - right @ left), rtol=0.0, atol=1e-12)
    np.testing.assert_allclose(left @ right, bivector + gram[0, 1] * identity, rtol=0.0, atol=1e-12)
    assert not np.allclose(bivector, left @ right, rtol=0.0, atol=1e-12)


@pytest.mark.parametrize(
    ("signature", "transform"),
    (
        (
            (1, 1, -1),
            np.array(
                [
                    [1.0, 0.25, 0.4],
                    [0.3, 1.2, -0.2],
                    [0.1, -0.35, 0.9],
                ]
            ),
        ),
        (
            (1, 1, -1, -1),
            np.array(
                [
                    [1.0, 0.2, 0.1, -0.1],
                    [0.3, 1.1, -0.2, 0.2],
                    [-0.1, 0.25, 0.9, 0.15],
                    [0.2, -0.1, 0.3, 1.2],
                ]
            ),
        ),
    ),
)
def test_every_native_exterior_blade_matches_antisymmetrization_oracle(
    signature: tuple[int, ...],
    transform: np.ndarray,
) -> None:
    algebra = Algebra(gram=_dense_gram(signature, transform))
    plan = _representation_plan(algebra, "compact")

    for mask in range(algebra.dim):
        np.testing.assert_allclose(
            plan.conversion_basis[mask],
            _antisymmetrized_product(plan.generators, mask),
            rtol=0.0,
            atol=2e-11,
        )


@pytest.mark.parametrize(
    ("signature", "transform"),
    (
        ((1, 1), np.array([[1.2, 0.4], [-0.3, 0.9]])),
        ((1, -1), np.array([[1.0, 0.35], [-0.2, 1.3]])),
        (
            (1, 1, -1, -1),
            np.array([[1.0, 0.1, 0.2, 0.0], [0.2, 1.1, 0.0, -0.1], [0.0, 0.3, 1.2, 0.1], [-0.1, 0.0, 0.2, 0.9]]),
        ),
    ),
)
def test_general_gram_compact_map_preserves_random_products(
    signature: tuple[int, ...],
    transform: np.ndarray,
) -> None:
    algebra = Algebra(gram=_dense_gram(signature, transform))
    rng = np.random.default_rng(20260906 + algebra.n)

    for _ in range(8):
        left = algebra.multivector(rng.normal(size=algebra.dim))
        right = algebra.multivector(rng.normal(size=algebra.dim))
        expected = np.asarray(to_matrix(geometric_product(left, right), mode="compact"))
        actual = np.asarray(to_matrix(left, mode="compact")) @ np.asarray(to_matrix(right, mode="compact"))
        np.testing.assert_allclose(actual, expected, rtol=2e-12, atol=2e-11)


@pytest.mark.parametrize(
    "gram",
    (
        np.diag([2.0, -3.0]),
        np.array([[2.0, 0.5], [0.5, -1.0]]),
        np.array([[1.8, 0.4], [0.4, 1.2]]),
    ),
)
def test_injective_general_gram_compact_representation_roundtrips(gram: np.ndarray) -> None:
    algebra = Algebra(gram=gram)
    value = algebra.multivector(np.array([1.25, -2.0, 0.75, 3.5]))

    matrix = to_matrix(value, mode="compact")
    recovered = from_matrix(matrix)

    assert matrix.mode == "compact"
    np.testing.assert_allclose(recovered.data, value.data, rtol=0.0, atol=1e-12)


def test_rank_deficient_general_gram_plan_preserves_strict_inverse_failure() -> None:
    transform = np.array([[1.0, 0.2, -0.1], [0.3, 1.2, 0.25], [-0.2, 0.1, 0.9]])
    algebra = Algebra(gram=_dense_gram((-1, -1, -1), transform))
    value = algebra.multivector(np.arange(algebra.dim, dtype=float))
    plan = _representation_plan(algebra, "compact")

    assert plan.real_rank == 4
    assert not plan.is_injective
    with pytest.raises(TypeError, match="not injective"):
        from_matrix(to_matrix(value, mode="compact"))


def test_native_and_independently_transformed_orthogonal_blades_intertwine() -> None:
    gram = np.array([[2.0, 0.5], [0.5, -1.0]])
    native = Algebra(gram=gram)
    native_plan = _representation_plan(native, "compact")
    congruence = native_plan.metric_congruence
    assert congruence is not None
    orthogonal = Algebra(signature=(1, -1))

    for mask in range(native.dim):
        indices = [index for index in range(native.n) if mask & (1 << index)]
        if indices:
            vectors = [orthogonal.vector(congruence.transform[index]) for index in indices]
            transformed_blade = outer_product(*vectors)
        else:
            transformed_blade = orthogonal.identity
        np.testing.assert_allclose(
            np.asarray(to_matrix(native.blade(mask), mode="compact")),
            np.asarray(to_matrix(transformed_blade, mode="compact")),
            rtol=0.0,
            atol=1e-12,
        )


def test_general_gram_congruence_and_cached_arrays_are_immutable() -> None:
    algebra = Algebra(gram=np.array([[2.0, 0.5], [0.5, -1.0]]))
    plan = _representation_plan(algebra, "compact")
    congruence = plan.metric_congruence
    assert congruence is not None

    with pytest.raises(FrozenInstanceError):
        congruence.residual = 0.0  # type: ignore[misc]
    for array in (
        congruence.gram,
        congruence.transform,
        congruence.orthogonal_metric,
        congruence.inverse_transform,
    ):
        with pytest.raises(ValueError, match="read-only"):
            array[0, 0] = 99.0


def test_scaled_diagonal_congruence_uses_the_exact_analytic_factorization() -> None:
    algebra = Algebra(gram=np.diag([2.0, -3.0]))
    plan = _representation_plan(algebra, "compact")
    congruence = plan.metric_congruence
    assert congruence is not None

    assert congruence.convention == "signed-diagonal-scale-v1"
    np.testing.assert_array_equal(congruence.orthogonal_metric, np.diag([1.0, -1.0]))
    np.testing.assert_array_equal(congruence.transform, np.diag(np.sqrt([2.0, 3.0])))
    np.testing.assert_allclose(
        congruence.inverse_transform @ congruence.transform,
        np.eye(algebra.n),
        rtol=0.0,
        atol=1e-15,
    )


def test_uniform_metric_scale_does_not_create_a_false_rank_deficiency() -> None:
    algebra = Algebra(gram=1e-8 * np.eye(3))
    value = algebra.multivector(np.array([1.0, -2.0, 3.0, -4.0, 0.5, -0.75, 1.25, -1.5]))
    plan = _representation_plan(algebra, "compact")

    assert plan.is_injective
    np.testing.assert_allclose(
        from_matrix(to_matrix(value, mode="compact")).data,
        value.data,
        rtol=0.0,
        atol=2e-4,
    )


@pytest.mark.parametrize("basis_order", ("origin-first", "euclidean-first"))
def test_native_null_cga_reaches_the_generic_explicit_compact_path(basis_order) -> None:
    algebra = Algebra(config=p_cga(spatial_dim=3, frame="null", basis_order=basis_order))
    cga = ConformalModel(algebra)
    point = cga.up((1.0, 2.0, -0.5))
    plan = _representation_plan(algebra, "compact")

    assert plan.metric_congruence is not None
    assert plan.matrix_shape == (4, 4)
    assert plan.real_rank == algebra.dim == 32
    assert to_matrix(point).mode == "left-regular"
    np.testing.assert_allclose(
        from_matrix(to_matrix(point, mode="compact")).data,
        point.data,
        rtol=0.0,
        atol=2e-12,
    )


@pytest.mark.parametrize("basis_order", ("origin-first", "euclidean-first"))
@pytest.mark.parametrize("null_pair", (-2.0, -1.0, 0.5))
def test_cga_native_orders_preserve_all_blade_roundtrips_and_matrix_products(basis_order, null_pair):
    algebra = Algebra(config=p_cga(3, basis_order=basis_order, null_pair=null_pair))
    rng = np.random.default_rng(134)
    for mask in range(algebra.dim):
        blade = algebra.blade(mask)
        np.testing.assert_allclose(from_matrix(to_matrix(blade, mode="compact")).data, blade.data, rtol=0, atol=1e-12)
    left, right = (algebra.multivector(rng.normal(size=algebra.dim)) for _ in range(2))
    np.testing.assert_allclose(
        (to_matrix(left, mode="compact") @ to_matrix(right, mode="compact")).mat,
        to_matrix(left * right, mode="compact").mat,
        rtol=0,
        atol=1e-10,
    )


def test_general_gram_support_does_not_claim_a_named_spinor_convention() -> None:
    algebra = Algebra(gram=np.array([[2.0, 0.5], [0.5, -1.0]]))

    with pytest.raises(TypeError, match="normalized orthogonal native basis.*to_matrix"):
        to_spinor_column(algebra.identity)


@pytest.mark.parametrize("basis_order", ("origin-first", "euclidean-first"))
def test_native_null_cga_matrix_does_not_claim_a_dirac_basis_transform(basis_order) -> None:
    algebra = Algebra(config=p_cga(spatial_dim=3, frame="null", basis_order=basis_order))
    cga = ConformalModel(algebra)
    matrix = to_matrix(cga.origin, mode="compact")

    with pytest.raises(TypeError, match=r"requires Cl\(1,3\) or Cl\(3,1\)"):
        matrix.to_basis("weyl")


@pytest.mark.parametrize("target", ("dirac", "weyl", "majorana"))
@pytest.mark.parametrize(
    "gram",
    (
        np.diag([2.0, -3.0, -4.0, -5.0]),
        _dense_gram(
            (1, 1, 1, -1),
            np.array([[1.0, 0.2, 0.0, 0.0], [0.0, 1.1, 0.1, 0.0], [0.1, 0.0, 0.9, 0.2], [0.0, 0.1, 0.0, 1.2]]),
        ),
    ),
)
def test_matching_inertia_does_not_imply_a_named_dirac_basis(gram, target) -> None:
    algebra = Algebra(gram=gram)
    value = algebra.vector([1.0, -0.5, 0.25, 0.75])
    matrix = to_matrix(value, mode="compact")

    np.testing.assert_allclose(from_matrix(matrix).data, value.data, atol=2e-12, rtol=0)
    with pytest.raises(TypeError, match="normalized orthogonal native basis"):
        matrix.to_basis(target)


@pytest.mark.parametrize(
    ("mode", "gram"),
    (
        ("pauli", _dense_gram((1, 1, 1), np.array([[1.0, 0.2, 0.0], [0.1, 1.1, 0.1], [0.0, -0.1, 0.9]]))),
        (
            "dirac",
            _dense_gram(
                (1, -1, -1, -1),
                np.array([[1.0, 0.1, 0.0, 0.0], [0.0, 1.1, 0.2, 0.0], [0.1, 0.0, 0.9, 0.1], [0.0, -0.1, 0.2, 1.0]]),
            ),
        ),
        (
            "quaternion",
            _dense_gram(
                (1, -1, -1, -1),
                np.array([[1.0, 0.1, 0.0, 0.0], [0.0, 1.1, 0.2, 0.0], [0.1, 0.0, 0.9, 0.1], [0.0, -0.1, 0.2, 1.0]]),
            ),
        ),
    ),
)
def test_named_matrix_conventions_remain_limited_to_normalized_orthogonal_bases(
    mode: str,
    gram: np.ndarray,
) -> None:
    algebra = Algebra(gram=gram)

    with pytest.raises(NotImplementedError, match="normalized orthogonal.*mode='compact'.*left-regular"):
        to_matrix(algebra.identity, mode=mode)
