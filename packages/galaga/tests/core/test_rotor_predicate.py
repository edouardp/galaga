"""Rotors must preserve native vectors, not merely have unit reverse norm."""

import numpy as np
import pytest

import galaga.core as core


@pytest.fixture(
    params=(
        pytest.param(np.eye(6), id="euclidean"),
        pytest.param(np.diag([1, -1, 1, 1, 1, 1]), id="indefinite"),
        pytest.param(np.diag([0, 1, 1, 1, 1, 1]), id="degenerate"),
        pytest.param(
            np.array(
                [
                    [2, 0.5, 0, 0, 0, 0],
                    [0.5, 1, 0, 0, 0, 0],
                    [0, 0, 1, 0, 0, 0],
                    [0, 0, 0, 1, 0, 0],
                    [0, 0, 0, 0, 1, 0],
                    [0, 0, 0, 0, 0, 1],
                ]
            ),
            id="oblique",
        ),
    )
)
def gram(request):
    return request.param


@pytest.fixture(params=("auto", "reference", "packed", "lazy"))
def algebra(request, gram):
    return core.Algebra(gram=gram, product_backend=request.param)


def assert_close(actual, expected, *, atol=1e-12):
    np.testing.assert_allclose(actual.data, expected.data, rtol=0, atol=atol)


def test_unit_even_pseudoscalar_exponential_is_not_a_rotor(algebra):
    volume = algebra.pseudoscalar()
    reverse_sign = (-1) ** (algebra.n * (algebra.n - 1) // 2)
    square = reverse_sign * np.linalg.det(algebra.gram)
    # Establish the actual algebra before testing the classification.
    assert_close(volume * volume, algebra.scalar(square))
    assert core.reverse(volume) == reverse_sign * volume
    for vector in algebra.basis_vectors():
        assert_close(volume * vector, -vector * volume)

    value = core.exp(-0.25 * volume)
    assert core.is_even(value)
    assert_close(value * ~value, algebra.identity)
    images = [core.sandwich(value, vector) for vector in algebra.basis_vectors()]
    assert max(np.max(np.abs(core.grade(image, 5).data)) for image in images) > 0.4
    assert not core.is_rotor(value)


def test_rotor_generator_rejects_nonrotors_but_algebra_log_accepts_them(algebra):
    value = core.exp(-0.25 * algebra.pseudoscalar())
    assert_close(value * ~value, algebra.identity)
    assert_close(core.log(value), -0.25 * algebra.pseudoscalar())
    with pytest.raises(ValueError, match="normalized rotor"):
        core.rotor_generator(value)


def test_compound_bivector_rotors_keep_grades_four_and_six(algebra):
    first, second, third = (algebra.blade(mask) for mask in (3, 12, 48))
    for left, right in ((first, second), (first, third), (second, third)):
        assert_close(left * right, right * left)
    generator = 0.2 * first - 0.3 * second + 0.4 * third
    rotor = core.exp(generator)
    factored = core.exp(0.2 * first) * core.exp(-0.3 * second) * core.exp(0.4 * third)
    assert_close(rotor, factored)
    assert np.linalg.norm(core.grade(rotor, 4).data) > 0.01
    assert np.linalg.norm(core.grade(rotor, 6).data) > 0.01
    assert_close(rotor * ~rotor, algebra.identity)

    for candidate in (rotor, -rotor, ~rotor):
        images = [core.sandwich(candidate, vector) for vector in algebra.basis_vectors()]
        for image in images:
            assert_close(image, core.grade(image, 1))
        action = np.column_stack([image.vector_part for image in images])
        np.testing.assert_allclose(action.T @ algebra.gram @ action, algebra.gram, rtol=0, atol=1e-12)
        assert core.is_rotor(candidate)


def test_composition_of_noncommuting_rotors_preserves_vectors(algebra):
    first, second = algebra.blade(3), algebra.blade(6)
    assert np.linalg.norm((first * second - second * first).data) > 0
    left, right = core.exp(0.2 * first), core.exp(-0.3 * second)
    rotor = left * right
    for vector in algebra.basis_vectors():
        image = core.sandwich(rotor, vector)
        assert_close(image, core.sandwich(left, core.sandwich(right, vector)))
        assert_close(image, core.grade(image, 1))
    assert core.is_rotor(rotor)


@pytest.mark.parametrize("backend", ("auto", "reference", "packed", "lazy"))
def test_every_native_basis_vector_is_checked_including_the_last(backend):
    algebra = core.Algebra(signature=(0, 0, 0, 0, 0, 1), product_backend=backend)
    volume = algebra.pseudoscalar()
    assert volume * volume == 0 and ~volume == -volume
    value = 1 + volume
    assert value * ~value == 1
    for vector in algebra.basis_vectors()[:-1]:
        assert volume * vector == 0
        assert core.sandwich(value, vector) == vector
    last = algebra.basis_vectors()[-1]
    image = core.sandwich(value, last)
    assert image == last + 2 * volume * last
    assert np.linalg.norm(core.grade(image, 5).data) == 2
    assert not core.is_rotor(value)


@pytest.mark.parametrize("dimension", (0, 1, 6))
@pytest.mark.parametrize("sign", (-1, 1))
def test_signed_identity_is_a_rotor_even_at_zero_tolerance(dimension, sign):
    algebra = core.Algebra(dimension)
    assert core.is_rotor(algebra.scalar(sign), atol=0)


@pytest.mark.parametrize("parameter", (2e-13, 8e-13))
@pytest.mark.parametrize("atol", (1e-14, 1e-12, 1e-10))
def test_vector_leakage_uses_the_requested_absolute_coefficient_tolerance(parameter, atol):
    algebra = core.Algebra(6)
    volume = algebra.pseudoscalar()
    assert volume * volume == -1 and ~volume == -volume
    value = core.exp(parameter * volume)
    image = core.sandwich(value, algebra.blade(1))
    leakage = np.max(np.abs(core.grade(image, 5).data))
    assert leakage == pytest.approx(abs(np.sin(2 * parameter)), rel=1e-12, abs=0)
    assert_close(value * ~value, algebra.identity, atol=atol)
    assert core.is_rotor(value, atol=atol) == (leakage <= atol)


def test_tolerance_applies_to_native_action_not_just_input_coefficients():
    algebra = core.Algebra(gram=np.diag([1e6, 1e-6, 1, 1, 1, 1]))
    volume = algebra.pseudoscalar()
    assert volume * volume == -1
    value = core.exp(2e-13 * volume)
    assert abs(value.coefficient(algebra.dim - 1)) < 1e-12
    image = core.sandwich(value, algebra.blade(1))
    leakage = np.max(np.abs(core.grade(image, 5).data))
    assert leakage == pytest.approx(abs(np.sin(4e-13)) * algebra.gram[0, 0], rel=1e-12, abs=0)
    assert leakage > 1e-7
    assert not core.is_rotor(value)
    assert core.is_rotor(value, atol=1e-6)


@pytest.mark.parametrize("rapidity", (2, 10, 12))
def test_large_boosts_allow_explicit_roundoff_tolerance(rapidity):
    algebra = core.Algebra(signature=(1, -1, 1, 1, 1, 1))
    plane = algebra.blade(3)
    assert plane * plane == 1 and ~plane == -plane
    rotor = np.cosh(rapidity / 2) + np.sinh(rapidity / 2) * plane
    # Hyperbolic cancellation can exceed the default absolute tolerance.
    assert_close(rotor * ~rotor, algebra.identity, atol=1e-9)
    for vector in algebra.basis_vectors():
        image = core.sandwich(rotor, vector)
        assert_close(image, core.grade(image, 1), atol=1e-9)
    assert core.is_rotor(rotor, atol=1e-9)
