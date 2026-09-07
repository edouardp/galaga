"""Public facade keys share the core's exact numeric equality/hash policy."""

from __future__ import annotations

from fractions import Fraction

import numpy as np
import pytest

import galaga
from galaga import Algebra, DisplayPolicy


@pytest.mark.parametrize("kind", ("scalar", "mixed"))
def test_signed_zero_hash_fix_crosses_the_top_level_facade(kind: str) -> None:
    algebra = Algebra(gram=[[0.0, -1.0], [-1.0, 0.0]])
    data = np.zeros(algebra.dim)
    data[0] = 1.0
    if kind == "mixed":
        data[-1] = 0.5
    negative = data.copy()
    negative[negative == 0] = -0.0
    first = algebra.multivector(data)
    second = algebra.multivector(negative)

    assert isinstance(first, galaga.Multivector)
    assert first == second
    assert hash(first) == hash(second) == hash(first.numeric)
    assert {first: "found"}[second] == {second: "found"}[first] == "found"
    assert len({first, second}) == 1
    np.testing.assert_array_equal(np.signbit(second.data), np.signbit(negative))


@pytest.mark.parametrize(
    "number", (0, -0.0, True, 1.25, 2**100, Fraction(5, 4), np.int64(1), np.float32(1.25), np.bool_(True))
)
def test_public_scalar_numeric_key_interoperability(number) -> None:
    value = Algebra(2).scalar(float(number))

    assert value == number and number == value
    assert hash(value) == hash(number)
    assert {number: "found"}[value] == {value: "found"}[number] == "found"
    assert len({number, value}) == len({value, number}) == 1


@pytest.mark.parametrize(
    "coefficient, other",
    (
        (float(2**53), 2**53 + 1),
        (float(2**53), np.int64(2**53 + 1)),
        (0.1, Fraction(1, 10)),
        (1.0, 10**1000),
        (1.0, float("nan")),
        (1.0, float("inf")),
        (np.nextafter(1.0, 2.0), np.float32(1.0)),
    ),
    ids=("large-int", "numpy-int", "fraction", "huge-int", "nan", "infinity", "numpy-float32"),
)
def test_public_scalar_comparison_preserves_exact_values_without_lossy_coercion(coefficient: float, other) -> None:
    value = Algebra(2).scalar(coefficient)

    assert not (value == other) and not (other == value)


def test_hash_is_independent_of_names_tracking_and_presentation_views() -> None:
    algebra = Algebra(2)
    first = algebra.multivector([1.0, 2.0, -0.0, 0.0])
    alternate = Algebra.from_numeric(algebra.numeric)
    variants = (
        first.named("v"),
        first.with_expr(),
        first.named("v").with_expr().unnamed(),
        first.named("v").with_expr().without_expr(),
        alternate.multivector([1.0, 2.0, 0.0, -0.0]),
    )
    for value in variants:
        assert value == first and hash(value) == hash(first)
        assert {first: "found"}[value] == "found"
    with algebra.use_presentation(algebra.presentation.with_display(DisplayPolicy(coefficient_precision=3))):
        assert hash(first) == hash(variants[0])


def test_public_equality_remains_algebra_scoped_and_distinguishes_tiny_nonzero_grades() -> None:
    algebra = Algebra(2)
    first = algebra.identity
    separate = Algebra(2).identity
    nearby = algebra.multivector([1.0, np.nextafter(0.0, 1.0), 0.0, 0.0])

    assert first != separate and first != nearby
    assert first == 1 and separate == 1
    assert hash(first) == hash(separate) == hash(1)
    assert len({first, separate, nearby}) == 3
