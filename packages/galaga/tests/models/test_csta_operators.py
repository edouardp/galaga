"""Operator recognition checks identities and full actions, not construction names."""

import numpy as np
import pytest

from galaga import Algebra, exp, grade, presets, scalar_product, squared
from galaga.models import ConformalSpacetimeModel


@pytest.fixture
def model():
    return ConformalSpacetimeModel(Algebra(config=presets.csta(), user_config_files=False))


def test_projectors_and_joint_sectors_follow_actual_products_and_preserve_scale(model):
    g0, g1, _, _ = model.spacetime_basis_vectors()
    K = g1 * g0
    E = model.origin ^ model.infinity
    one = model.algebra.scalar(1)
    zero = model.algebra.scalar(0)
    assert squared(K) == one and squared(E) == one
    assert K * E == E * K
    projectors = ((1 + E) / 2, (1 - E) / 2, (1 + K) / 2, (1 - K) / 2)
    sectors = tuple((1 + s * K) * (1 + t * E) / 4 for s in (-1, 1) for t in (-1, 1))
    assert sum(sectors) == one
    for index, a in enumerate(sectors):
        for other, b in enumerate(sectors):
            assert (a * b).almost_equal(a if index == other else zero)
    for P in (*projectors, *sectors):
        assert (P * P).almost_equal(P)
        assert model.classify_operator(P).traits == ("idempotent",)
        assert "idempotent" not in model.classify_operator(2 * P).traits
        assert "involution" in model.classify_operator(2 * P - one).traits
    assert "idempotent" not in model.classify_operator(1e-6 * projectors[0]).traits


def test_zero_and_identity_have_multiple_traits(model):
    zero = model.classify_operator(model.algebra.scalar(0))
    assert set(zero.traits) == {"zero", "idempotent", "nilpotent"} and zero.nilpotency_index == 1
    one = model.classify_operator(model.algebra.scalar(1))
    assert {"identity", "idempotent", "involution", "versor", "rotor"} <= set(one.traits)
    assert one.transformation == "identity"
    assert model.classify_operator(model.algebra.scalar(-1)).transformation == "identity"


def test_nilpotency_uses_bounded_products_and_does_not_confuse_decay_with_zero(model):
    g0, g1, g2, g3 = model.spacetime_basis_vectors()
    A = (g0 + g1) * g2
    B = model.origin * g3
    N = A + B
    assert squared(A).almost_equal(model.algebra.scalar(0))
    assert squared(B).almost_equal(model.algebra.scalar(0))
    assert A * B == B * A
    assert np.any((N * N).data) and not np.any((N * N * N).data)
    for scale in (1, 1e-8, 1e8):
        assert model.classify_operator(scale * N, max_power=2).nilpotency_index is None
        assert model.classify_operator(scale * N, max_power=3).nilpotency_index == 3
    for scalar in (0.1, 1e-8, 1e8):
        assert model.classify_operator(model.algebra.scalar(scalar), max_power=64).nilpotency_index is None


@pytest.mark.parametrize(
    "name",
    (
        "boost",
        "rotation",
        "translation",
        "dilation",
        "special conformal transformation",
        "conformal inversion",
        "spatial reflection",
    ),
)
def test_versor_names_follow_verified_basis_action_and_metric(model, name):
    g0, g1, g2, g3 = model.spacetime_basis_vectors()
    o = model.origin
    i = model.infinity
    values = {
        "boost": exp(0.4 * g1 * g0),
        "rotation": exp(0.4 * g1 * g2),
        "translation": exp(-i * g1 / 2),
        "dilation": exp(0.3 * (o ^ i) / 2),
        "special conformal transformation": exp(-o * g1 / 2),
        "conformal inversion": o + 0.5 * i,
        "spatial reflection": g1,
    }
    value = values[name]
    vectors = (*model.spacetime_basis_vectors(), o, i)
    G = np.array([[float(scalar_product(a, b)) for b in vectors] for a in vectors])
    norm = float(value * ~value)
    inverse = ~value / norm
    odd = value.homogeneous_grade() == 1
    images = tuple((-1 if odd else 1) * value * v * inverse for v in vectors)
    for scale in (1, -3, 7):
        result = model.classify_operator(scale * value)
        assert "versor" in result.traits and result.transformation == name
        action = np.array(dict(result.properties)["action"])
        np.testing.assert_allclose(action.T @ G @ action, G, atol=1e-9)
        for column, image in zip(action.T, images, strict=True):
            reconstructed = sum((float(c) * v for c, v in zip(column, vectors, strict=True)), model.algebra.scalar(0))
            assert reconstructed.almost_equal(image)
        assert ("rotor" in result.traits) is (scale == 1 and not odd)


def test_combined_action_reports_components_and_natural_translation(model):
    g0, g1, _, _ = model.spacetime_basis_vectors()
    E = model.origin ^ model.infinity
    operator = exp(-model.infinity * g1 / 2) * exp(0.3 * E / 2) * exp(0.4 * g1 * g0)
    result = model.classify_operator(operator)
    assert result.transformation == "affine conformal transformation"
    props = dict(result.properties)
    assert props["components"] == ("translation", "dilation", "boost")
    np.testing.assert_allclose(props["translation"], (0, -1, 0, 0), atol=1e-9)
    assert props["dilation_factor"] == pytest.approx(np.exp(0.3))


def test_unit_reverse_norm_is_insufficient_to_prove_a_versor(model):
    pseudoscalar = model.algebra.blade((1 << model.algebra.n) - 1)
    candidate = exp(0.3 * pseudoscalar)
    assert (candidate * ~candidate).almost_equal(model.algebra.scalar(1))
    image = candidate * model.spacetime_basis_vectors()[0] * ~candidate
    assert np.any(grade(image, 5).data)
    assert "versor" not in model.classify_operator(candidate).traits


def test_operator_classifier_validates_tolerance_bound_and_algebra(model):
    value = model.algebra.scalar(1)
    for bound in (True, 0, -1, 65, 1.5):
        with pytest.raises(ValueError, match="max_power"):
            model.classify_operator(value, max_power=bound)
    for argument in ("atol", "rtol"):
        with pytest.raises(ValueError, match=argument):
            model.classify_operator(value, **{argument: -1})
    with pytest.raises(ValueError, match="model algebra"):
        model.classify_operator(Algebra(config=presets.csta(), user_config_files=False).scalar(1))
    with pytest.raises(TypeError, match="Multivector"):
        model.classify_operator(1)
    with pytest.raises(TypeError, match="rtol"):
        model.classify_operator(value, rtol=True)
    for coefficient in (float("nan"), float("inf")):
        data = np.zeros(model.algebra.dim)
        data[0] = coefficient
        with pytest.raises(ValueError, match="finite"):
            model.classify_operator(model.algebra.multivector(data))


def test_composed_inversion_and_improper_rotation_are_not_named_pure_actions(model):
    _, g1, g2, _ = model.spacetime_basis_vectors()
    rotation = exp(0.2 * g1 * g2)
    inversion = model.origin + model.infinity / 2
    assert model.classify_operator(rotation * inversion).transformation == "conformal transformation"
    # Rotate in a plane orthogonal to the reflection normal: a rotoreflection.
    _, _, _, g3 = model.spacetime_basis_vectors()
    assert model.classify_operator(rotation * g3).transformation == "improper spatial transformation"
