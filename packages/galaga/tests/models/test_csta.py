"""Conformal spacetime model and classifier contracts."""

import numpy as np
import pytest

from galaga import Algebra, exp, outer_product, presets, right_hodge_dual, sandwich, scalar_product, squared
from galaga.models import ConformalSpacetimeModel


@pytest.fixture
def csta() -> ConformalSpacetimeModel:
    return ConformalSpacetimeModel(Algebra(config=presets.csta(), user_config_files=False), expr=True)


def test_csta_preset_derives_basis_roles_and_mostly_minus_metric() -> None:
    algebra = Algebra(config=presets.csta(), user_config_files=False)
    expected = np.zeros((6, 6))
    expected[:4, :4] = np.diag((1, -1, -1, -1))
    expected[4, 5] = expected[5, 4] = -1

    np.testing.assert_array_equal(algebra.gram, expected)
    assert algebra.model is not None
    assert algebra.model.id == "csta-mostly-minus"
    assert [value.latex(content="value") for value in algebra.basis_vectors()] == [
        r"\gamma_0",
        r"\gamma_1",
        r"\gamma_2",
        r"\gamma_3",
        "n_o",
        r"n_\infty",
    ]


def test_model_requires_declared_csta_semantics() -> None:
    with pytest.raises(ValueError, match=r"presets\.csta"):
        ConformalSpacetimeModel(Algebra(2, 4, user_config_files=False))


def test_event_embedding_is_null_and_coordinates_round_trip(csta: ConformalSpacetimeModel) -> None:
    event = csta.event(2.0, 1.0, -3.0, 0.5)
    spacetime = csta.spacetime_vector((2.0, 1.0, -3.0, 0.5))

    assert (event * event).almost_equal(csta.algebra.scalar(0))
    assert np.allclose(csta.coordinates(event), (2.0, 1.0, -3.0, 0.5))
    assert csta.down(event).almost_equal(spacetime)
    assert csta.weight(event) == pytest.approx(1.0)


def test_separation_and_causal_kind_follow_the_actual_metric(csta: ConformalSpacetimeModel) -> None:
    origin = csta.event(0, 0, 0, 0)
    cases = (
        (csta.event(1, 0, 0, 0), 1.0, "timelike"),
        (csta.event(1, 1, 0, 0), 0.0, "null"),
        (csta.event(0, 1, 0, 0), -1.0, "spacelike"),
    )

    for event, expected_interval, expected_kind in cases:
        interval = csta.separation_squared(origin, event)
        assert interval == pytest.approx(expected_interval)
        assert csta.causal_kind(interval) == expected_kind


def test_classifier_uses_representation_to_resolve_event_light_cone_ambiguity(
    csta: ConformalSpacetimeModel,
) -> None:
    value = csta.event(0, 0, 0, 0)

    assert csta.classify(value).kind == "event or light cone"
    assert csta.classify(value, representation="direct").kind == "event"
    assert csta.classify(value, representation="dual").kind == "light cone"


def test_signed_round_classifier_uses_computed_square(csta: ConformalSpacetimeModel) -> None:
    cases = (
        (1.0, "proper-time hyperboloid", "timelike"),
        (0.0, "light cone", "null"),
        (-1.0, "proper-distance hyperboloid", "spacelike"),
    )

    for radius_squared, expected_kind, expected_causal in cases:
        value = csta.signed_round((0, 0, 0, 0), radius_squared)
        classified = csta.classify(value, representation="dual")
        assert float(value * value) == pytest.approx(radius_squared)
        assert classified.kind == expected_kind
        assert classified.causal == expected_causal


def test_flat_line_classifier_recovers_carrier_causal_kind(csta: ConformalSpacetimeModel) -> None:
    origin = csta.event(0, 0, 0, 0)
    cases = (
        (csta.event(1, 0, 0, 0), "timelike"),
        (csta.event(1, 1, 0, 0), "null"),
        (csta.event(0, 1, 0, 0), "spacelike"),
    )

    for event, expected_causal in cases:
        line = csta.flat_line(origin, event)
        classified = csta.classify(line)
        assert classified.kind == "flat line"
        assert classified.simple is True
        assert classified.causal == expected_causal
        assert outer_product(line, csta.infinity).almost_equal(csta.algebra.scalar(0))


def test_classifier_is_projective_and_rejects_non_simple_values(csta: ConformalSpacetimeModel) -> None:
    event = csta.event(1, 2, 0, 0)
    assert csta.classify(7 * event, representation="direct").kind == "event"

    g0, g1, g2, g3 = csta.spacetime_basis_vectors(expr=False)
    non_simple = (g0 ^ g1) + (g2 ^ g3)
    classified = csta.classify(non_simple)
    assert classified.kind == "general"
    assert classified.simple is False


def test_classifier_validates_representation_tolerance_and_algebra(csta: ConformalSpacetimeModel) -> None:
    event = csta.event(0, 0, 0, 0)
    with pytest.raises(ValueError, match="representation"):
        csta.classify(event, representation="opns")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="atol"):
        csta.classify(event, atol=True)
    with pytest.raises(ValueError, match="model algebra"):
        csta.classify(Algebra(config=presets.csta(), user_config_files=False).basis_vectors()[0])


@pytest.mark.parametrize(
    ("radius_squared", "offsets", "kind", "causal"),
    (
        (
            0,
            ((1, 1, 0, 0), (1, -1, 0, 0), (1, 0, 1, 0), (1, 0, 0, 1), (2, 2, 0, 0)),
            "light cone",
            "null",
        ),
        (
            1,
            ((1, 0, 0, 0), (np.sqrt(2), 1, 0, 0), (np.sqrt(2), 0, 1, 0), (np.sqrt(2), 0, 0, 1), (np.sqrt(2), -1, 0, 0)),
            "proper-time hyperboloid",
            "timelike",
        ),
        (
            -1,
            ((0, 1, 0, 0), (0, -1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1), (1, np.sqrt(2), 0, 0)),
            "proper-distance hyperboloid",
            "spacelike",
        ),
    ),
)
def test_round_from_five_events_has_the_same_classification_as_its_dual_vector(
    csta, radius_squared, offsets, kind, causal
):
    center = np.array((10, 3, -2, 1))
    samples = tuple(csta.event(center + np.array(offset), expr=False) for offset in offsets)
    apex = csta.event(center, expr=False)
    round_blade = outer_product(*samples)
    dual_vector = right_hodge_dual(round_blade)

    assert round_blade.homogeneous_grade() == 5
    assert dual_vector.homogeneous_grade() == 1
    for sample in samples:
        assert csta.separation_squared(apex, sample) == pytest.approx(radius_squared, abs=1e-10)
        assert outer_product(sample, round_blade).almost_equal(csta.algebra.scalar(0), atol=1e-10)
        assert float(scalar_product(sample, dual_vector)) == pytest.approx(0, abs=1e-10)
    computed_radius = float(squared(dual_vector)) / csta.weight(dual_vector) ** 2
    assert computed_radius == pytest.approx(radius_squared, abs=1e-10)
    np.testing.assert_allclose(csta.coordinates(dual_vector), center)

    for scale in (1, -3, 7):
        direct = csta.classify(scale * round_blade)
        explicit_direct = csta.classify(scale * round_blade, representation="direct")
        dual = csta.classify(scale * dual_vector, representation="dual")
        assert direct == explicit_direct
        assert direct.kind == dual.kind == kind
        assert direct.causal == dual.causal == causal
        assert direct.grade == 5
        assert dual.grade == 1
        assert direct.representation == "direct"
        assert dual.representation == "dual"
        assert dict(direct.properties)["signed_radius_squared"] == pytest.approx(computed_radius, abs=1e-10)


@pytest.mark.parametrize("offset", ((1, 0, 0, 0), (1, 1, 0, 0), (0, 1, 0, 0)))
def test_event_pair_and_direct_or_dual_line_causal_classes_match_the_computed_interval(csta, offset):
    center = np.array((10, 3, -2, 1))
    first = csta.event(center, expr=False)
    second = csta.event(center + np.array(offset), expr=False)
    computed = float(squared(csta.down(second) - csta.down(first)))
    expected_causal = csta.causal_kind(computed)
    pair = first ^ second
    line = pair ^ csta.infinity

    assert csta.classify(pair).kind == ("lightlike line" if expected_causal == "null" else "event pair")
    assert csta.classify(pair).causal == expected_causal
    for value, representation in ((line, "direct"), (right_hodge_dual(line), "dual")):
        classified = csta.classify(value, representation=representation)
        assert classified.kind == "flat line"
        assert classified.causal == expected_causal
        assert outer_product(first, line).almost_equal(csta.algebra.scalar(0))
        assert outer_product(second, line).almost_equal(csta.algebra.scalar(0))


@pytest.mark.parametrize(("count", "kind"), ((3, "flat 2-plane"), (4, "flat hyperplane")))
def test_higher_flats_constructed_from_events_and_infinity(csta, count, kind):
    samples = tuple(
        csta.event(coordinates, expr=False)
        for coordinates in ((0, 0, 0, 0), (1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0))[:count]
    )
    flat = outer_product(*samples, csta.infinity)

    classified = csta.classify(flat)
    assert classified.kind == kind
    assert classified.grade == count + 1
    assert classified.simple is True
    assert outer_product(flat, csta.infinity).almost_equal(csta.algebra.scalar(0))
    for sample in samples:
        assert outer_product(sample, flat).almost_equal(csta.algebra.scalar(0))


@pytest.mark.parametrize(
    ("coordinates", "kind", "causal", "center"),
    (
        (((0, 0, 0, 0), (0.75, 0.25, 0, 0), (4 / 3, 2 / 3, 0, 0)), "hyperbola", "timelike", (0, -1, 0, 0)),
        (((1, 0, 0, 0), (1.25, 0.75, 0, 0), (5 / 3, 4 / 3, 0, 0)), "hyperbola", "spacelike", (0, 0, 0, 0)),
        (((0, 1, 0, 0), (0, 0, 1, 0), (0, -1, 0, 0)), "circle", "spacelike", (0, 0, 0, 0)),
        (((0, 0, 0, 0), (1, 1, 0, 0), (1, -1, 0, 0)), "null line pair", "null", (0, 0, 0, 0)),
    ),
)
def test_round_curve_shape_and_causal_tangents_are_derived_from_its_metric(csta, coordinates, kind, causal, center):
    samples = tuple(csta.event(position, expr=False) for position in coordinates)
    curve = outer_product(*samples)
    center_vector = csta.spacetime_vector(center, expr=False)
    radius_squared = float(squared(csta.down(samples[0]) - center_vector))
    for sample in samples:
        displacement = csta.down(sample) - center_vector
        assert float(squared(displacement)) == pytest.approx(radius_squared, abs=1e-10)
        assert outer_product(sample, curve).almost_equal(csta.algebra.scalar(0))

    for scale in (1, -3, 7):
        direct = csta.classify(scale * curve)
        dual = csta.classify(right_hodge_dual(scale * curve), representation="dual")
        assert direct.kind == dual.kind == kind
        assert direct.causal == dual.causal == causal
        assert direct.grade == dual.grade == 3
        properties = dict(direct.properties)
        np.testing.assert_allclose(properties["center"], center, atol=1e-10)
        assert properties["signed_radius_squared"] == pytest.approx(radius_squared, abs=1e-10)


def test_null_carrier_round_curve_recognizes_a_parabola_without_inventing_a_center(csta):
    samples = tuple(csta.event(position, expr=False) for position in ((0, 0, 0, 0), (1, 1, 1, 0), (2, 2, -1, 0)))
    curve = outer_product(*samples)
    result = csta.classify(curve)
    assert result.kind == "parabola"
    assert result.causal == "spacelike"
    assert "center" not in dict(result.properties)
    assert dict(result.properties)["carrier_inertia"] == (0, 1, 1)


@pytest.mark.parametrize("acceleration", (0.5, 1, 2))
def test_rotor_generated_uniform_acceleration_samples_define_a_timelike_hyperbola(csta, acceleration):
    time_axis, space_axis, _, _ = csta.spacetime_basis_vectors(expr=False)
    generator = space_axis * time_axis
    center = -space_axis / acceleration
    assert squared(generator).almost_equal(csta.algebra.scalar(1))
    samples = []
    for proper_time in (0, 0.5, 1):
        rotor = exp(acceleration * proper_time * generator / 2)
        position = center + sandwich(rotor, space_axis) / acceleration
        velocity = sandwich(rotor, time_axis)
        assert (rotor * ~rotor).almost_equal(csta.algebra.scalar(1))
        assert squared(velocity).almost_equal(squared(time_axis))
        assert float(squared(position - center)) == pytest.approx(-1 / acceleration**2)
        samples.append(csta.event(position, expr=False))

    curve = outer_product(*samples)
    classified = csta.classify(curve)
    properties = dict(classified.properties)
    assert classified.kind == "hyperbola"
    assert classified.causal == "timelike"
    assert properties["carrier_inertia"] == (1, 1, 0)
    assert properties["signed_radius_squared"] == pytest.approx(-1 / acceleration**2)
    np.testing.assert_allclose(properties["center"], (0, -1 / acceleration, 0, 0), atol=1e-10)


@pytest.mark.parametrize(("coefficient", "kind"), ((0.5, "imaginary circle"), (0, "point circle")))
def test_spacelike_round_sections_without_three_real_samples_are_not_called_real_circles(csta, coefficient, kind):
    _, space_1, space_2, _ = csta.spacetime_basis_vectors(expr=False)
    stationary = csta.origin.without_expr() + coefficient * csta.infinity.without_expr()
    blade = stationary ^ space_1 ^ space_2
    result = csta.classify(blade)
    assert result.kind == kind
    assert result.causal is None
    assert dict(result.properties)["signed_radius_squared"] == pytest.approx(-float(squared(stationary)))
