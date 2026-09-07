"""Exact numeric equality must imply equal hashes, including IEEE signed zero."""

from __future__ import annotations

from fractions import Fraction

import numpy as np
import pytest

from galaga.core import Algebra


@pytest.mark.parametrize(
    "gram",
    (
        np.eye(2),
        np.diag([1.0, 0.0]),
        np.array([[2.0, 0.5], [0.5, -1.0]]),
        np.array([[0.0, -1.0], [-1.0, 0.0]]),
    ),
    ids=("euclidean", "degenerate", "oblique", "native-null"),
)
@pytest.mark.parametrize("kind", ("zero", "scalar", "vector", "bivector", "mixed"))
def test_signed_zero_peers_are_interchangeable_dictionary_and_set_keys(gram, kind: str) -> None:
    algebra = Algebra(gram=gram)
    data = np.zeros(algebra.dim)
    if kind in ("scalar", "mixed"):
        data[0] = 1.25
    if kind in ("vector", "mixed"):
        data[1] = -2.0
    if kind in ("bivector", "mixed"):
        data[-1] = 0.5
    negative_data = data.copy()
    negative_data[negative_data == 0] = -0.0
    first = algebra.multivector(data)
    second = algebra.multivector(negative_data)
    original_bytes = second.data.tobytes()

    assert first == second and second == first
    assert hash(first) == hash(second)
    assert {first: "found"}[second] == "found"
    assert {second: "found"}[first] == "found"
    assert len({first, second}) == 1
    assert second.data.tobytes() == original_bytes
    assert np.signbit(second.data[second.data == 0]).all()
    assert not second.data.flags.writeable


@pytest.mark.parametrize("dimension", (0, 2))
@pytest.mark.parametrize(
    "number",
    (
        0,
        -0.0,
        1,
        -1,
        1.25,
        2**53,
        2**100,
        True,
        False,
        Fraction(5, 4),
        np.int64(-3),
        np.uint64(2**63),
        np.float16(1.25),
        np.float32(1.25),
        np.float64(1.25),
        np.longdouble(1.25),
        np.bool_(True),
        np.bool_(False),
    ),
)
def test_exact_real_scalar_peers_have_numeric_hashes_in_both_lookup_directions(dimension: int, number) -> None:
    algebra = Algebra(dimension)
    data = np.zeros(algebra.dim)
    data[0] = float(number)
    value = algebra.multivector(data)

    assert value == number and number == value
    assert hash(value) == hash(number)
    assert {value: "found"}[number] == "found"
    assert {number: "found"}[value] == "found"
    assert len({value, number}) == len({number, value}) == 1


@pytest.mark.parametrize(
    "coefficient, other",
    (
        (float(2**53), 2**53 + 1),
        (float(-(2**53)), -(2**53 + 1)),
        (float(2**53), np.int64(2**53 + 1)),
        (float(2**63), np.uint64(2**63 + 1)),
        (1.0, 10**1000),
        (1.0, -(10**1000)),
        (0.1, Fraction(1, 10)),
        (1.0, Fraction(10**1000 + 1, 10**1000)),
        (np.nextafter(1.0, 2.0), np.float16(1.0)),
        (np.nextafter(1.0, 2.0), np.float32(1.0)),
        (np.nextafter(1.0, 2.0), np.longdouble(1.0)),
    ),
    ids=(
        "large-int",
        "negative-large-int",
        "numpy-int64",
        "numpy-uint64",
        "huge-int",
        "negative-huge-int",
        "one-tenth-fraction",
        "tiny-rational-difference",
        "numpy-float16",
        "numpy-float32",
        "numpy-longdouble",
    ),
)
def test_scalar_comparison_does_not_round_the_other_number_to_float64(coefficient: float, other) -> None:
    value = Algebra(2).scalar(coefficient)

    assert not (value == other)
    assert not (other == value)
    assert len({value, other}) == len({other, value}) == 2


@pytest.mark.parametrize("other", (float("nan"), float("inf"), -float("inf"), np.float32("nan"), np.longdouble("inf")))
def test_comparison_with_nonfinite_numbers_returns_false_without_constructing_a_value(other) -> None:
    value = Algebra(2).identity

    assert not (value == other)
    assert not (other == value)


def test_comparison_with_a_wider_numpy_float_does_not_narrow_its_precision() -> None:
    if np.finfo(np.longdouble).nmant <= np.finfo(np.float64).nmant:
        pytest.skip("longdouble has no extra precision on this platform")
    wider = np.longdouble(1) + np.finfo(np.longdouble).eps
    value = Algebra(2).identity

    assert float(wider) == 1.0  # This conversion would lose the distinguishing bit.
    assert not (value == wider)
    assert not (wider == value)


@pytest.mark.parametrize("mask", (0, 1, 2, 3))
def test_equality_remains_exact_for_neighboring_floats_and_subnormal_coefficients(mask: int) -> None:
    algebra = Algebra(2)
    data = np.zeros(algebra.dim)
    data[0] = 1.0
    neighbor = data.copy()
    neighbor[mask] = np.nextafter(data[mask], np.inf)
    first = algebra.multivector(data)
    second = algebra.multivector(neighbor)

    assert first != second and second != first
    assert first.almost_equal(second)
    assert first == algebra.multivector(data.copy())
    assert len({first, second}) == 2  # Unequal values may collide; never assert different hashes.
    if mask:
        assert second != 1 and not (1 == second)


@pytest.mark.parametrize("coefficient", (0.0, 1.0, -2.5))
def test_scalar_hashing_does_not_erase_algebra_identity_from_multivector_equality(coefficient: float) -> None:
    first = Algebra(2).scalar(coefficient)
    second = Algebra(2).scalar(coefficient)

    assert first != second
    assert first == coefficient and second == coefficient
    assert hash(first) == hash(second) == hash(coefficient)
    assert len({first, second}) == 2


def test_non_scalar_keys_remain_distinct_across_algebra_instances() -> None:
    first = Algebra(2).vector([1, 2])
    second = Algebra(2).vector([1, 2])

    assert first != second
    assert len({first, second}) == 2


def test_hashing_and_scalar_comparison_do_not_use_tolerant_float_or_grade_inspection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    algebra = Algebra(2)
    scalar = algebra.identity
    mixed = algebra.multivector([1.0, 1e-14, -0.0, 0.0])

    def reject_tolerant_conversion(*args, **kwargs):
        raise AssertionError("equality/hash used a tolerance-sensitive conversion")

    monkeypatch.setattr(type(scalar), "__float__", reject_tolerant_conversion)
    monkeypatch.setattr(type(scalar), "homogeneous_grade", reject_tolerant_conversion)
    assert scalar == 1 and hash(scalar) == hash(1)
    assert mixed != 1
    assert hash(mixed) == hash(algebra.multivector([1.0, 1e-14, 0.0, 0.0]))
