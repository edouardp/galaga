"""Galaga 2 facade contracts for numeric matrix representations."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pytest
from galaga_matrix import from_matrix, to_matrix
from galaga_matrix.matrix import _left_regular_matrix, compact_basis

from galaga.facade import Algebra, Multivector, geometric_product

GENERAL_GRAM_METRICS = (
    np.array([[2.0, 0.5], [0.5, -1.0]]),
    np.array([[0.0, -1.0], [-1.0, 0.0]]),
)


@pytest.mark.parametrize("gram", GENERAL_GRAM_METRICS)
def test_left_regular_facade_matrix_reproduces_geometric_product(gram: np.ndarray) -> None:
    algebra = Algebra(gram=gram)
    left = algebra.multivector(np.array([1.5, -2.0, 0.75, 3.0]))
    right = algebra.multivector(np.array([-1.0, 0.5, 2.0, -0.25]))

    matrix = to_matrix(left, mode="left-regular")

    np.testing.assert_allclose(
        np.asarray(matrix) @ right.data,
        geometric_product(left, right).data,
        rtol=0.0,
        atol=1e-12,
    )
    assert matrix.algebra is algebra
    assert matrix.mode == "left-regular"


@pytest.mark.parametrize("gram", GENERAL_GRAM_METRICS)
def test_general_gram_left_regular_roundtrip_preserves_facade_coefficients(gram: np.ndarray) -> None:
    algebra = Algebra(gram=gram)
    value = algebra.multivector(np.array([2.0, -1.0, 3.5, 0.25]))

    matrix = to_matrix(value)
    recovered = from_matrix(matrix)

    assert matrix.mode == "left-regular"
    assert isinstance(recovered, Multivector)
    assert recovered.algebra is algebra
    np.testing.assert_array_equal(recovered.data, value.data)


@pytest.mark.parametrize("gram", GENERAL_GRAM_METRICS)
def test_generator_anticommutators_reproduce_the_supplied_gram_matrix(gram: np.ndarray) -> None:
    algebra = Algebra(gram=gram)
    generators = [np.asarray(to_matrix(vector, mode="left-regular")) for vector in algebra.basis_vectors()]
    identity = np.eye(algebra.dim)

    for row, left in enumerate(generators):
        for column, right in enumerate(generators):
            np.testing.assert_allclose(
                left @ right + right @ left,
                2.0 * gram[row, column] * identity,
                rtol=0.0,
                atol=1e-12,
            )


def test_basis_left_actions_use_the_same_public_representation() -> None:
    algebra = Algebra(gram=np.array([[2.0, 0.5], [0.5, -1.0]]))

    actions = _left_regular_matrix(algebra)

    assert actions.shape == (algebra.dim, algebra.dim, algebra.dim)
    for bitmask in range(algebra.dim):
        np.testing.assert_array_equal(
            actions[bitmask],
            algebra.left_action(algebra.blade(bitmask)),
        )


@pytest.mark.parametrize(
    "gram",
    (*GENERAL_GRAM_METRICS, np.diag([2.0, -3.0])),
)
def test_compact_mode_rejects_metrics_without_a_normalized_orthogonal_basis(
    gram: np.ndarray,
) -> None:
    algebra = Algebra(gram=gram)

    with pytest.raises(NotImplementedError, match="normalized orthogonal.*left-regular"):
        compact_basis(algebra)
    with pytest.raises(NotImplementedError, match="normalized orthogonal.*left-regular"):
        to_matrix(algebra.identity, mode="compact")


def test_quaternion_mode_rejects_a_general_gram_basis_of_cl13() -> None:
    gram = np.diag([1.0, -1.0, -1.0, -1.0])
    gram[1, 2] = gram[2, 1] = 0.25
    algebra = Algebra(gram=gram)

    assert algebra.inertia == (1, 3, 0)
    with pytest.raises(NotImplementedError, match="normalized orthogonal.*left-regular"):
        to_matrix(algebra.identity, mode="quaternion")


def test_normalized_diagonal_compact_behavior_remains_compatible() -> None:
    algebra = Algebra(signature=(1, 1, -1))
    e1, e2, e3 = algebra.basis_vectors()
    left = 1 + 2 * e1 - e2
    right = e1 + 0.5 * e3

    left_matrix = to_matrix(left, mode="compact")
    right_matrix = to_matrix(right, mode="compact")
    product_matrix = to_matrix(geometric_product(left, right), mode="compact")

    np.testing.assert_allclose(
        np.asarray(product_matrix),
        np.asarray(left_matrix) @ np.asarray(right_matrix),
        rtol=0.0,
        atol=1e-12,
    )


def test_named_facade_value_roundtrips_without_legacy_expression_internals() -> None:
    algebra = Algebra(2)
    value = algebra.vector([1.0, -2.0], name="v")

    matrix = to_matrix(value, mode="left-regular")
    recovered = from_matrix(matrix)

    assert matrix._name_latex == r"\rho(v)"
    assert recovered.name is not None
    assert recovered.name.latex == r"\rho^{-1}(\rho(v))"
    np.testing.assert_array_equal(recovered.data, value.data)


def test_matrix_implementation_does_not_read_legacy_multiplication_tables() -> None:
    source = (Path(__file__).parents[1] / "galaga_matrix/matrix.py").read_text()

    assert "_mul_index" not in source
    assert "_mul_sign" not in source
    assert "from galaga import Algebra" not in source
    assert "from galaga.algebra import Multivector" not in source
