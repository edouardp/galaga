"""Algebra logarithms and geometric generators have distinct domains."""

import numpy as np
import pytest

import galaga.core as core


def assert_close(actual, expected, *, atol=1e-12):
    np.testing.assert_allclose(actual.data, expected.data, rtol=0, atol=atol)


@pytest.mark.parametrize("scalar", (1e-100, 0.25, 1, 2, 1e100))
def test_positive_scalar_logarithm_does_not_require_a_rotor(scalar):
    algebra = core.Algebra(0)
    assert core.log(algebra.scalar(scalar)).scalar_part == pytest.approx(np.log(scalar))


@pytest.mark.parametrize("signature", ((1,), (-1,), (0,)))
@pytest.mark.parametrize("scale", (0.25, 1, 3))
def test_nonrotor_study_logarithms_include_vector_and_null_generators(signature, scale):
    algebra = core.Algebra(signature=signature)
    vector = algebra.blade(1)
    assert vector * vector == algebra.gram[0, 0]
    generator = np.log(scale) + 0.3 * vector
    value = core.exp(generator)
    assert not core.is_rotor(value)
    result = core.log(value)
    assert_close(result, generator)
    assert_close(core.exp(result), value)


@pytest.mark.parametrize("phase", (0.25, np.pi / 4, np.pi / 2, 2.8, -2.8))
def test_pseudoscalar_logarithm_is_valid_even_when_not_a_rotor_generator(phase):
    algebra = core.Algebra(6)
    volume = algebra.I
    assert volume * volume == -1 and ~volume == -volume
    value = np.cos(phase) + np.sin(phase) * volume
    result = core.log(value)
    assert_close(result, phase * volume)
    assert_close(core.exp(result), value)
    assert not core.is_rotor_generator(result)


@pytest.mark.parametrize("backend", ("auto", "reference", "packed", "lazy"))
@pytest.mark.parametrize(
    "gram",
    (
        np.eye(4),
        np.diag([1, -1, 1, 1]),
        np.diag([0, 1, 1, 1]),
        np.array([[2, 0.5, 0, 0], [0.5, 1, 0, 0], [0, 0, 1, 0.2], [0, 0, 0.2, -1]]),
    ),
    ids=("euclidean", "indefinite", "degenerate", "oblique"),
)
def test_compound_logarithm_uses_full_native_products(gram, backend):
    algebra = core.Algebra(gram=gram, product_backend=backend)
    first, second = algebra.blade(3), algebra.blade(12)
    assert_close(first * second, second * first)
    generator = 0.2 * first + 0.3 * second
    assert np.linalg.norm(core.grade(generator * generator, 4).data) > 0.1
    rotor = core.exp(0.2 * first) * core.exp(0.3 * second)
    result = core.log(rotor)
    assert_close(result, generator)
    assert_close(core.exp(result), rotor)
    assert_close(core.rotor_generator(rotor), generator)


@pytest.mark.parametrize("backend", ("reference", "packed", "lazy"))
def test_general_mixed_grade_logarithm_does_not_discard_nonscalar_square(backend):
    algebra = core.Algebra(gram=[[2, 0.5], [0.5, -1]], product_backend=backend)
    generator = algebra.multivector([0.2, 0.1, 0.2, 0.3])
    value = core.exp(generator)
    result = core.log(value)
    assert_close(result, generator)
    assert_close(core.exp(result), value)


def test_defective_nilpotent_logarithm_keeps_the_quadratic_term():
    algebra = core.Algebra(signature=(0, 0, 0))
    nilpotent = algebra.blade(1) + algebra.blade(6)
    square = nilpotent * nilpotent
    assert square != 0 and square * nilpotent == 0
    value = 1 + nilpotent
    expected = nilpotent - square / 2
    assert_close(core.exp(expected), value)
    assert_close(core.log(value), expected)


@pytest.mark.parametrize("amount", (1e-7, 1e-10, 1e-14))
def test_tiny_non_study_terms_are_not_thresholded_into_the_null_formula(amount):
    algebra = core.Algebra(4)
    generator = amount * (algebra.blade(3) + algebra.blade(12))
    value = core.exp(generator)
    result = core.log(value)
    assert_close(result - core.grade(result, 0), generator, atol=1e-20)
    # Rounded input coefficients need not have exactly unit norm. Keep their
    # actual scalar logarithm rather than forcibly projecting it away.
    assert abs(result.scalar_part) < np.finfo(float).eps


@pytest.mark.parametrize("kind", ("zero", "negative", "singular", "nilpotent", "negative-eigenvalue", "negative-null"))
def test_principal_logarithm_rejects_singular_inputs_and_the_branch_cut(kind):
    algebra = core.Algebra(signature=(1, 0, 1))
    e1, null, _ = algebra.basis_vectors()
    value = {
        "zero": algebra.scalar(0),
        "negative": algebra.scalar(-1),
        "singular": 1 + e1,
        "nilpotent": null,
        "negative-eigenvalue": e1,
        "negative-null": -1 + null,
    }[kind]
    with pytest.raises(ValueError, match="singular|principal real"):
        core.log(value)


def test_generator_predicate_checks_the_whole_one_parameter_action():
    algebra = core.Algebra(6)
    invalid = np.pi / 2 * algebra.I
    assert core.is_rotor(core.exp(invalid))
    assert not core.is_rotor(core.exp(invalid / 2))
    assert not core.is_rotor_generator(invalid)
    valid = np.pi / 2 * (algebra.blade(3) + algebra.blade(12) + algebra.blade(48))
    assert_close(core.exp(valid), algebra.I)
    assert core.is_rotor_generator(valid)
    assert core.is_rotor_generator(algebra.scalar(0))
    assert not core.is_rotor_generator(algebra.scalar(1))
    assert not core.is_rotor_generator(algebra.blade(1))


def test_generator_predicate_matches_degenerate_rotor_contract_not_just_grade():
    algebra = core.Algebra(signature=(0, 0, 0, 0, 0, 0, 1))
    generator = algebra.blade(63)
    assert generator * generator == 0 and ~generator == -generator
    assert not core.is_bivector(generator)
    for vector in algebra.basis_vectors():
        assert generator * vector == vector * generator
    assert core.is_rotor_generator(generator)
    for parameter in (-2, 0, 0.5, 1):
        assert core.is_rotor(core.exp(parameter * generator))


def test_rotor_generator_never_silently_projects_or_changes_the_branch():
    algebra = core.Algebra(6)
    volume = algebra.I
    assert core.is_rotor(volume)
    assert_close(core.log(volume), np.pi / 2 * volume)
    with pytest.raises(ValueError, match="principal logarithm.*rotor generator"):
        core.rotor_generator(volume)
    with pytest.raises(ValueError, match="normalized rotor"):
        core.rotor_generator((1 + volume) / np.sqrt(2))


@pytest.mark.parametrize("atol", (1e-14, 1e-12, 1e-10))
def test_generator_predicate_tolerance_is_applied_to_commutator_coefficients(atol):
    algebra = core.Algebra(6)
    generator = 8e-13 * algebra.I
    commutator = generator * algebra.blade(1) - algebra.blade(1) * generator
    residual = np.max(np.abs(commutator.data))
    assert residual == pytest.approx(1.6e-12, rel=1e-14, abs=0)
    assert core.is_rotor_generator(generator, atol=atol) == (residual <= atol)


@pytest.mark.parametrize("function", ("log", "rotor_generator", "is_rotor_generator"))
def test_operations_require_an_explicit_multivector_algebra(function):
    with pytest.raises(TypeError, match="Multivector"):
        getattr(core, function)(1.0)


@pytest.mark.parametrize("scale", (0.01, 1, 100, 1e50))
def test_general_logarithm_retains_scalar_scale(scale):
    algebra = core.Algebra(4)
    generator = 0.2 * algebra.blade(3) + 0.3 * algebra.blade(12)
    value = scale * core.exp(generator)
    assert_close(core.log(value), np.log(scale) + generator)


@pytest.mark.parametrize("kind", ("singular", "negative-spectrum"))
def test_general_non_study_spectral_rejections(kind):
    algebra = core.Algebra(signature=(1, 1, -1))
    vector, plane = algebra.blade(1), algebra.blade(6)
    assert vector * vector == 1 and plane * plane == 1 and vector * plane == plane * vector
    value = (1 + vector) * (1 + 0.2 * plane) if kind == "singular" else -core.exp(0.2 * vector + 0.3 * plane)
    nonscalar = value - value.scalar_part
    assert not core.is_scalar(nonscalar * nonscalar)
    with pytest.raises(ValueError, match="singular|principal real"):
        core.log(value)


@pytest.mark.parametrize("seed", range(8))
def test_seeded_mixed_grade_logs_roundtrip_in_the_principal_neighborhood(seed):
    algebra = core.Algebra(gram=[[2, 0.5, 0], [0.5, -1, 0.2], [0, 0.2, 0]])
    generator = algebra.multivector(np.random.default_rng(seed).normal(size=algebra.dim) * 0.08)
    # Independent unscaled Taylor oracle, not the production exp algorithm.
    expected, term = algebra.identity, algebra.identity
    for order in range(1, 60):
        term = term * generator / order
        expected = expected + term
    assert_close(core.log(expected), generator)


@pytest.mark.parametrize("atol", (-1, np.inf, np.nan))
def test_log_rejects_invalid_tolerances(atol):
    with pytest.raises(ValueError, match="finite and nonnegative"):
        core.log(core.Algebra(0).identity, atol=atol)


def test_wrong_closed_form_cannot_bypass_the_exponential_residual(monkeypatch):
    algebra = core.Algebra(2)
    value = core.exp(0.3 * algebra.blade(3))
    monkeypatch.setattr(core, "_log_scalar_square", lambda *args: algebra.scalar(0))
    with pytest.raises(ValueError, match="round-trip"):
        core.log(value)


def test_agreeing_quadrature_estimates_still_need_the_exponential_residual(monkeypatch):
    algebra = core.Algebra(4)
    value = core.exp(0.2 * algebra.blade(3) + 0.3 * algebra.blade(12))
    monkeypatch.setattr(core, "principal_log_candidates", lambda action: iter((np.zeros(16), np.zeros(16))))
    with pytest.raises(ValueError, match="did not converge"):
        core.log(value)


def test_exhausted_quadrature_never_returns_an_unconverged_candidate(monkeypatch):
    from galaga.core import _logarithm

    algebra = core.Algebra(4)
    value = core.exp(0.2 * algebra.blade(3) + 0.3 * algebra.blade(12))
    monkeypatch.setattr(_logarithm, "_QUADRATURE_ORDERS", (1,))
    with pytest.raises(ValueError, match="did not converge"):
        core.log(value)


@pytest.mark.parametrize("operation", ("eigvals", "solve"))
def test_unresolved_spectral_or_resolvent_calculations_raise(operation, monkeypatch):
    algebra = core.Algebra(4)
    value = core.exp(0.2 * algebra.blade(3) + 0.3 * algebra.blade(12))

    def fail(*args, **kwargs):
        raise np.linalg.LinAlgError("unresolved")

    monkeypatch.setattr(np.linalg, operation, fail)
    with pytest.raises(ValueError, match="principal real|singular resolvent"):
        core.log(value)


def test_nonfinite_left_action_is_rejected(monkeypatch):
    algebra = core.Algebra(4)
    value = core.exp(0.2 * algebra.blade(3) + 0.3 * algebra.blade(12))
    monkeypatch.setattr(core.Algebra, "left_action", lambda self, value: np.full((16, 16), np.inf))
    with pytest.raises(ValueError, match="non-finite"):
        core.log(value)


def test_generator_checks_the_last_basis_vector_and_full_reverse_skewness():
    algebra = core.Algebra(signature=(0, 0, 0, 0, 0, 1))
    generator = algebra.I
    assert ~generator == -generator
    for vector in algebra.basis_vectors()[:-1]:
        assert generator * vector == vector * generator
    assert not core.is_rotor_generator(generator)
    assert not core.is_rotor_generator(algebra.blade(15))


def test_principal_log_of_a_large_compound_rotation_can_have_grade_six():
    algebra = core.Algebra(6)
    first, second, third = (algebra.blade(mask) for mask in (3, 12, 48))
    generator = 1.2 * first + 1.3 * second + 1.4 * third
    # The aligned-plane spectral sector crosses pi; reduce only that sector
    # by 2*pi. The projector is computed from commuting planes, not log().
    projector = (1 - first * second) * (1 - first * third) / 4
    assert projector * projector == projector
    expected = generator - 2 * np.pi * first * projector
    rotor = core.exp(1.2 * first) * core.exp(1.3 * second) * core.exp(1.4 * third)
    assert_close(core.exp(expected), rotor)
    assert_close(core.log(rotor), expected)
    assert np.linalg.norm(core.grade(expected, 6).data) > 1
    assert not core.is_rotor_generator(expected)
    with pytest.raises(ValueError, match="alternative branch"):
        core.rotor_generator(rotor)
