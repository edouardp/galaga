"""Algebraic identities for conformal spinors, independent of notebook layout."""

import numpy as np
import pytest

from galaga import Algebra, exp, grade, presets, scalar_product
from galaga.models import ConformalSpacetimeModel


@pytest.fixture
def model():
    return ConformalSpacetimeModel(Algebra(config=presets.csta(), user_config_files=False))


@pytest.fixture
def spin_frame(model):
    g0, g1, g2, _ = model.spacetime_basis_vectors()
    o, n = model.origin, model.infinity
    P = (1 + g1 * g0) * (1 + (o ^ n)) / 4
    I = model.algebra.I
    return P, I, (P, g0 * g2 * P, I * g0 * o * P, I * g2 * o * P)


def _encode(model, spin_frame, z):
    _, I, frame = spin_frame
    return sum(
        (float(c.real) * f + float(c.imag) * I * f for c, f in zip(np.asarray(z, dtype=complex), frame, strict=True)),
        model.algebra.scalar(0),
    )


def _coordinates(spin_frame, psi):
    _, I, frame = spin_frame
    columns = np.column_stack([v.data for f in frame for v in (f, I * f)])
    coefficients, _, rank, _ = np.linalg.lstsq(columns, psi.data, rcond=None)
    assert rank == 8
    np.testing.assert_allclose(columns @ coefficients, psi.data, atol=1e-12)
    return coefficients[::2] + 1j * coefficients[1::2]


def _pairing(model, spin_frame, psi, phi):
    _, I, _ = spin_frame
    g0 = model.spacetime_basis_vectors()[0]
    connector = I * g0 * (model.origin - model.infinity / 2)
    real = 4 * float(grade(~psi * phi * connector, 0))
    imag = -4 * float(grade(~psi * I * phi * connector, 0))
    return complex(real, imag)


def _matrix(spin_frame, operator):
    return np.column_stack([_coordinates(spin_frame, operator * f) for f in spin_frame[2]])


def _coordinate_matrix(q):
    """The convention to check against products, not a source of metric data."""
    t, x, y, z = q
    return np.array([[t + x, -y + 1j * z], [-y - 1j * z, t - x]], dtype=complex)


def test_even_ideal_and_complex_structure_follow_actual_products(model, spin_frame):
    P, I, frame = spin_frame
    one = model.algebra.scalar(1)
    g0, g1, _, _ = model.spacetime_basis_vectors()
    K = g1 * g0
    E = model.origin ^ model.infinity
    assert K * K == one and E * E == one and K * E == E * K
    assert P * P == P and I * I == -one
    assert I == model.algebra.basis_blades(6)[0]
    assert ~I == -I
    all_blades = [b for k in range(7) for b in model.algebra.basis_blades(k)]
    even_blades = [b for k in (0, 2, 4, 6) for b in model.algebra.basis_blades(k)]
    assert np.linalg.matrix_rank(np.column_stack([(b * P).data for b in all_blades])) == 16
    assert np.linalg.matrix_rank(np.column_stack([(b * P).data for b in even_blades])) == 8
    for b in even_blades:
        assert I * b == b * I
    for f in frame:
        assert f * P == f
    for column in np.eye(8).reshape(8, 4, 2):
        z = column[:, 0] + 1j * column[:, 1]
        psi = _encode(model, spin_frame, z)
        np.testing.assert_allclose(_coordinates(spin_frame, psi), z, atol=1e-12)
        np.testing.assert_allclose(_coordinates(spin_frame, I * psi), 1j * z, atol=1e-12)


def test_pairing_is_hermitian_with_computed_signature(model, spin_frame):
    frame = spin_frame[2]
    H = np.array([[_pairing(model, spin_frame, u, v) for v in frame] for u in frame])
    np.testing.assert_allclose(H, H.conj().T, atol=1e-12)
    np.testing.assert_allclose(np.linalg.eigvalsh(H), [-1, -1, 1, 1], atol=1e-12)
    np.testing.assert_allclose(H, np.block([[np.zeros((2, 2)), np.eye(2)], [np.eye(2), np.zeros((2, 2))]]))
    z = np.array([0.4 + 0.7j, -0.5j, 0.3, -0.2 + 0.6j])
    w = np.array([-0.1j, 0.8, 0.2 + 0.3j, -0.4j])
    psi, phi = _encode(model, spin_frame, z), _encode(model, spin_frame, w)
    assert _pairing(model, spin_frame, psi, phi) == pytest.approx(z.conj() @ H @ w)
    assert _pairing(model, spin_frame, phi, psi) == pytest.approx(_pairing(model, spin_frame, psi, phi).conjugate())
    I = spin_frame[1]
    scaled = (2 + 3 * I) * psi
    assert _pairing(model, spin_frame, scaled, scaled) == pytest.approx(13 * _pairing(model, spin_frame, psi, psi))


@pytest.mark.parametrize(
    "q", [(0, 0, 0, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1), (0.7, 0.2, -0.3, 0.4)]
)
@pytest.mark.parametrize("pi", [(1, 0), (0, 1), (1, 0.4 + 0.3j)])
def test_event_incidence_and_coordinate_matrix_match_clifford_action(model, spin_frame, q, pi):
    vector = model.spacetime_vector(q)
    translator = 1 - vector * model.infinity / 2
    event = model.event(*q)
    assert (translator * model.origin * ~translator).almost_equal(event)
    matrix = _matrix(spin_frame, translator)
    Q = _coordinate_matrix(q)
    np.testing.assert_allclose(1j * matrix[:2, 2:], Q, atol=1e-12)
    np.testing.assert_allclose(matrix, np.block([[np.eye(2), -1j * Q], [np.zeros((2, 2)), np.eye(2)]]), atol=1e-12)
    assert np.linalg.det(Q) == pytest.approx(float(vector * vector))
    psi = _encode(model, spin_frame, np.concatenate((-1j * Q @ pi, pi)))
    np.testing.assert_allclose((event * psi).data, 0, atol=1e-12)
    assert _pairing(model, spin_frame, psi, psi) == pytest.approx(0, abs=1e-12)
    real_action = np.column_stack([(event * v).data for f in spin_frame[2] for v in (f, spin_frame[1] * f)])
    assert np.linalg.matrix_rank(real_action) == 4


def test_ray_incidence_and_two_spinor_event_recovery(model, spin_frame):
    q = np.array([0.7, 0.2, -0.3, 0.4])
    systems, targets = [], []
    for pi in (np.array([1, 0.4 + 0.3j]), np.array([0, 1])):
        omega = -1j * _coordinate_matrix(q) @ pi
        psi = _encode(model, spin_frame, np.concatenate((omega, pi)))
        coefficients = np.column_stack([_coordinate_matrix(unit) @ pi for unit in np.eye(4)])
        A = np.vstack((coefficients.real, coefficients.imag))
        target = 1j * omega
        b = np.concatenate((target.real, target.imag))
        systems.append(A)
        targets.append(b)
        assert np.linalg.matrix_rank(A) == 3
        anchor = np.linalg.lstsq(A, b, rcond=None)[0]
        direction = np.linalg.svd(A)[2][-1]
        direction /= direction[0]
        assert float(model.spacetime_vector(direction) ** 2) == pytest.approx(0, abs=1e-12)
        events = [model.event(*(anchor + s * direction)) for s in (-1, 0, 1)]
        for event in events:
            np.testing.assert_allclose((event * psi).data, 0, atol=1e-12)
        line = events[0] ^ events[1]
        np.testing.assert_allclose((events[2] ^ line).data, 0, atol=1e-12)
        assert model.classify(line).kind == "lightlike line"
    joint = np.vstack(systems)
    assert np.linalg.matrix_rank(joint) == 4
    recovered = np.linalg.lstsq(joint, np.concatenate(targets), rcond=None)[0]
    np.testing.assert_allclose(recovered, q, atol=1e-12)
    first = _encode(model, spin_frame, np.concatenate((-1j * _coordinate_matrix(q)[:, 0], [1, 0])))
    second = _encode(model, spin_frame, np.concatenate((-1j * _coordinate_matrix(q)[:, 1], [0, 1])))
    assert _pairing(model, spin_frame, first, second) == pytest.approx(0, abs=1e-12)


@pytest.mark.parametrize("sign", [-1, 1])
def test_nonnull_twistors_have_no_real_finite_event_incidence(model, spin_frame, sign):
    z = np.array([1, 0, sign, 0], dtype=complex)
    psi = _encode(model, spin_frame, z)
    assert _pairing(model, spin_frame, psi, psi).real * sign > 0
    coefficients = np.column_stack([_coordinate_matrix(unit) @ z[2:] for unit in np.eye(4)])
    A = np.vstack((coefficients.real, coefficients.imag))
    target = 1j * z[:2]
    b = np.concatenate((target.real, target.imag))
    solution = np.linalg.lstsq(A, b, rcond=None)[0]
    assert np.linalg.norm(A @ solution - b) > 0.1


def test_null_boundary_twistor_is_not_incident_to_a_finite_event(model, spin_frame):
    psi = spin_frame[2][0]
    assert _pairing(model, spin_frame, psi, psi) == 0
    assert (model.infinity * psi).almost_equal(model.algebra.scalar(0))
    for q in ((0, 0, 0, 0), (1, 2, 3, 4)):
        assert np.max(np.abs((model.event(*q) * psi).data)) > 0.1


def test_bivector_rotors_preserve_twistor_pairing_and_incidence(model, spin_frame):
    frame = spin_frame[2]
    H = np.array([[_pairing(model, spin_frame, u, v) for v in frame] for u in frame])
    q = (0.7, 0.2, -0.3, 0.4)
    pi = np.array([1, 0.4 + 0.3j])
    psi = _encode(model, spin_frame, np.concatenate((-1j * _coordinate_matrix(q) @ pi, pi)))
    X = model.event(*q)
    for plane in model.algebra.basis_blades(2):
        R = exp(0.13 * plane)
        assert (R * ~R).almost_equal(model.algebra.scalar(1))
        M = _matrix(spin_frame, R)
        np.testing.assert_allclose(M.conj().T @ H @ M, H, atol=1e-12)
        assert np.linalg.det(M) == pytest.approx(1, abs=1e-12)
        np.testing.assert_allclose(((R * X * ~R) * (R * psi)).data, 0, atol=1e-12)


def test_spinor_double_cover_and_geometric_sandwich(model, spin_frame):
    _, g1, g2, _ = model.spacetime_basis_vectors()
    psi = _encode(model, spin_frame, [1, 0.4j, -0.2, 0.6])
    event = model.event(0.7, 0.2, -0.3, 0.4)
    R = exp(np.pi * g1 * g2)
    assert (R * psi).almost_equal(-psi)
    assert (R * event * ~R).almost_equal(event)
    assert (exp(2 * np.pi * g1 * g2) * psi).almost_equal(psi)


@pytest.mark.parametrize("q", [(0, 0, 0, 0), (0.7, 0.2, -0.3, 0.4), (2, 3, 4, 5)])
@pytest.mark.parametrize("phase", [1, 1j, 2 + 3j])
def test_alternating_spinor_product_recovers_event_with_arbitrary_phase(model, spin_frame, q, phase):
    _, I, frame = spin_frame
    g0, _, g2, _ = model.spacetime_basis_vectors()
    o, n = model.origin, model.infinity
    B = g0 * g2 * (o - n / 2)
    assert ~B == -B
    origin_pair = frame[2] * B * ~frame[3] - frame[3] * B * ~frame[2]
    assert origin_pair == -o
    T = 1 - model.spacetime_vector(q) * n / 2
    psi = (phase.real + phase.imag * I) * T * frame[2]
    phi = (2 - 0.5 * I) * T * frame[3]
    alternating = psi * B * ~phi - phi * B * ~psi
    V, W = grade(alternating, 1), grade(alternating, 5) * I
    np.testing.assert_allclose((alternating - grade(alternating, 1) - grade(alternating, 5)).data, 0, atol=1e-12)
    a, b = -float(scalar_product(V, n)), -float(scalar_product(W, n))
    recovered = (a * V + b * W) / (a * a + b * b)
    expected = model.event(*q)
    assert recovered.almost_equal(expected)
    assert (recovered * recovered).almost_equal(model.algebra.scalar(0))
    np.testing.assert_allclose((recovered * psi).data, 0, atol=1e-12)
    np.testing.assert_allclose((recovered * phi).data, 0, atol=1e-12)
    determinant = phase * (2 - 0.5j)
    assert alternating.almost_equal(-(determinant.real + determinant.imag * I) * expected)


def test_event_bilinear_is_covariant_and_alternates_over_complex_spinors(model, spin_frame):
    _, I, frame = spin_frame
    g0, _, g2, _ = model.spacetime_basis_vectors()
    B = g0 * g2 * (model.origin - model.infinity / 2)
    T = 1 - model.spacetime_vector((0.7, 0.2, -0.3, 0.4)) * model.infinity / 2
    u, v = T * frame[2], T * frame[3]
    psi, phi = (1 + 0.4 * I) * u + (0.3 - I) * v, (0.2 + I) * u + 2 * v
    alternating = psi * B * ~phi - phi * B * ~psi
    assert (psi * B * ~(I * psi) - (I * psi) * B * ~psi).almost_equal(model.algebra.scalar(0))
    V, W = grade(alternating, 1), grade(alternating, 5) * I
    a, b = -float(scalar_product(V, model.infinity)), -float(scalar_product(W, model.infinity))
    assert ((a * V + b * W) / (a * a + b * b)).almost_equal(model.event(0.7, 0.2, -0.3, 0.4))
    imaginary_pair = (I * u) * B * ~v - v * B * ~(I * u)
    assert grade(imaginary_pair, 1).almost_equal(model.algebra.scalar(0))
    W = grade(imaginary_pair, 5) * I
    assert (W / -float(scalar_product(W, model.infinity))).almost_equal(model.event(0.7, 0.2, -0.3, 0.4))
    for plane in model.algebra.basis_blades(2):
        R = exp(0.13 * plane)
        transformed = (R * psi) * B * ~(R * phi) - (R * phi) * B * ~(R * psi)
        assert transformed.almost_equal(R * alternating * ~R)


def test_boundary_spinor_pair_yields_infinity_with_zero_finite_weight(model, spin_frame):
    _, I, frame = spin_frame
    g0, _, g2, _ = model.spacetime_basis_vectors()
    B = g0 * g2 * (model.origin - model.infinity / 2)
    alternating = frame[0] * B * ~frame[1] - frame[1] * B * ~frame[0]
    assert np.max(np.abs(alternating.data)) > 0
    for vector in (grade(alternating, 1), grade(alternating, 5) * I):
        assert float(scalar_product(vector, model.infinity)) == pytest.approx(0)
        assert (vector ^ model.infinity).almost_equal(model.algebra.scalar(0))
