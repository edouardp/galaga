"""Source-oriented identities for zero-, one-, and two-dimensional algebras."""

import numpy as np
import pytest

from galaga.core import (
    Algebra,
    conjugate,
    dual,
    even_grades,
    exp,
    geometric_product,
    grade_involution,
    inverse,
    is_bivector,
    is_rotor,
    is_scalar,
    is_vector,
    log,
    norm,
    odd_grades,
    outer_product,
    reverse,
    sandwich,
    undual,
    unit,
)


def test_cl0_operations_collapse_to_real_scalar_arithmetic() -> None:
    algebra = Algebra(0)
    value = algebra.scalar(5)

    assert algebra.dim == 1
    assert algebra.basis_vectors() == ()
    assert algebra.I == algebra.identity
    assert geometric_product(value, algebra.scalar(3)) == 15
    assert reverse(value) == value
    assert grade_involution(value) == value
    assert conjugate(value) == value
    assert norm(value) == 5
    assert geometric_product(value, inverse(value)) == 1
    assert dual(value) == value
    assert exp(algebra.scalar(1)).almost_equal(algebra.scalar(np.e))
    assert even_grades(value) == value
    assert odd_grades(value) == 0
    assert is_scalar(value)
    assert is_rotor(algebra.identity)


def test_cl1_vector_inverse_duality_and_scalar_function_boundaries() -> None:
    algebra = Algebra(1)
    (e1,) = algebra.basis_vectors()

    assert geometric_product(e1, e1) == 1
    assert norm(3 * e1) == 3
    assert norm(unit(3 * e1)) == 1
    assert geometric_product(e1, inverse(e1)) == 1
    assert is_scalar(dual(e1))
    assert undual(dual(e1)) == e1
    assert log(algebra.identity) == 0
    assert exp(algebra.scalar(0)) == algebra.identity
    assert is_vector(e1)
    assert not is_scalar(e1)


def test_cl2_bivector_exponential_rotates_and_round_trips() -> None:
    algebra = Algebra(2)
    e1, e2 = algebra.basis_vectors()
    plane = outer_product(e1, e2)
    rotor = exp((-np.pi / 4) * plane)

    assert is_bivector(plane)
    assert geometric_product(plane, plane) == -1
    assert is_rotor(rotor)
    assert sandwich(rotor, e1).almost_equal(e2)
    assert log(exp(0.3 * plane)).almost_equal(0.3 * plane)
    assert algebra.I == plane


def test_one_dimensional_negative_and_null_generators_use_exact_series() -> None:
    negative = Algebra(signature=[-1])
    (en,) = negative.basis_vectors()
    angle = 0.5
    assert geometric_product(en, en) == -1
    assert exp(angle * en).almost_equal(negative.scalar(np.cos(angle)) + np.sin(angle) * en)

    degenerate = Algebra(signature=[0])
    (e0,) = degenerate.basis_vectors()
    assert geometric_product(e0, e0) == 0
    assert exp(e0) == degenerate.identity + e0
    assert norm(e0) == 0
    with pytest.raises(ValueError, match="not invertible"):
        inverse(e0)
