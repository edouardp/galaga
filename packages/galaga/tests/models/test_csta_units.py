"""Physical units are boundary conversions; the actual CSTA metric stays normalized."""

import math

import numpy as np
import pytest

from galaga import Algebra, exp, presets, sandwich, scalar_product, squared
from galaga.expression import evaluate
from galaga.models import ConformalSpacetimeModel, SpacetimeUnits

C = 299_792_458.0
AU = 149_597_870_700.0
YEAR = 365.25 * 86_400
G = 9.80665


@pytest.fixture
def model():
    return ConformalSpacetimeModel(Algebra(config=presets.csta(), expr=True, user_config_files=False))


@pytest.mark.parametrize("scale", (1, 0.001, C / G))
@pytest.mark.parametrize(
    ("quantity", "unit", "factor"),
    (
        ("time", "ns", 1e-9),
        ("time", "microseconds", 1e-6),
        ("time", "ms", 1e-3),
        ("time", "s", 1),
        ("time", "min", 60),
        ("time", "hour", 3600),
        ("time", "day", 86_400),
        ("time", "week", 604_800),
        ("time", "month", YEAR / 12),
        ("time", "year", YEAR),
        ("distance", "nm", 1e-9),
        ("distance", "um", 1e-6),
        ("distance", "mm", 1e-3),
        ("distance", "cm", 1e-2),
        ("distance", "meters", 1),
        ("distance", "km", 1000),
        ("distance", "light-second", C),
        ("distance", "AU", AU),
        ("distance", "ly", C * YEAR),
        ("speed", "m/s", 1),
        ("speed", "km/h", 1000 / 3600),
        ("speed", "km/s", 1000),
        ("speed", "c", C),
        ("speed", "%c", C / 100),
        ("acceleration", "m/s^2", 1),
        ("acceleration", "g", G),
    ),
)
def test_numeric_conversions_follow_physical_scale_and_round_trip(scale, quantity, unit, factor):
    backend = SpacetimeUnits(scale)
    physical_scales = {"time": scale, "distance": C * scale, "speed": C, "acceleration": C / scale}
    natural = getattr(backend, quantity + "_from")(-2.5, unit)
    assert natural == pytest.approx(-2.5 * factor / physical_scales[quantity])
    assert getattr(backend, quantity + "_in")(natural, unit) == pytest.approx(-2.5)


@pytest.mark.parametrize("method", ("event", "point", "up"))
@pytest.mark.parametrize("form", ("operator", "expanded"))
def test_si_event_matches_algebraic_natural_event_and_replays(model, method, form):
    si = ConformalSpacetimeModel(model.algebra, units="si", expr=True)
    actual = getattr(si, method)(2, C, -3 * C, 0.5 * C, expression_form=form)
    expected = model.event(2, 1, -3, 0.5)
    assert actual.almost_equal(expected)
    assert float(squared(actual)) == pytest.approx(0)
    np.testing.assert_allclose(si.coordinates(actual), (2, C, -3 * C, 0.5 * C))
    np.testing.assert_allclose(si.coordinates(actual, units="natural"), (2, 1, -3, 0.5))
    assert not si.coordinates(actual).flags.writeable
    assert evaluate(actual.expr, algebra=model.algebra).almost_equal(actual)


def test_per_event_units_overrides_mixed_policy_and_retains_labels(model):
    mixed = ConformalSpacetimeModel(model.algebra, units=("minute", "AU"), time_scale_seconds=60, expr=True)
    event = mixed.event(iter((1, 1, 0, 0)))
    assert mixed.units == ("min", "AU")
    np.testing.assert_allclose(mixed.coordinates(event), (1, 1, 0, 0))
    np.testing.assert_allclose(mixed.coordinates(event, units="si"), (60, AU, 0, 0))
    assert event.almost_equal(mixed.event(60, AU, 0, 0, units="si"))
    assert event.almost_equal(mixed.event(1, AU / (60 * C), 0, 0, units="natural"))
    assert "min" in event.latex(content="expr") and "AU" in event.latex(content="expr")
    assert evaluate(event.expr, algebra=model.algebra).almost_equal(event)
    view = mixed.with_expression_form("expanded")
    assert view.units == mixed.units and view.unit_scale is mixed.unit_scale and view.algebra is mixed.algebra
    assert view.event(1, 1, 0, 0).almost_equal(event)


def test_si_scale_does_not_change_null_sign_or_classifier(model):
    si = ConformalSpacetimeModel(model.algebra, units="si")
    origin = si.event(0, 0, 0, 0)
    for time, distance, kind in ((1, C, "null"), (2, C, "timelike"), (0, C, "spacelike")):
        event = si.event(time, distance, 0, 0)
        displacement = si.down(event) - si.down(origin)
        interval = si.separation_squared(origin, event)
        assert interval == pytest.approx(float(displacement * displacement))
        assert si.causal_kind(interval) == kind
        assert si.classify(si.flat_line(origin, event)).causal == kind


def test_multivectors_are_never_double_converted(model):
    si = ConformalSpacetimeModel(model.algebra, units="si")
    position = model.spacetime_vector((2, 1, 0, 0)).named("q")
    assert si.event(position) == model.event(position)
    assert si.up(position, units="natural") == model.up(position)
    for constructor in (si.spacetime_vector, si.event, si.up):
        with pytest.raises(ValueError, match="already use natural"):
            constructor(position, units="si")


def test_physical_round_radius_squared_follows_computed_algebra_square(model):
    si = ConformalSpacetimeModel(model.algebra, units="si", expr=True)
    for radius_squared in (C * C, -4 * C * C, 0):
        round_value = si.signed_round((2, C, 0, 0), radius_squared)
        expected = model.signed_round((2, 1, 0, 0), radius_squared / (C * C))
        assert round_value.almost_equal(expected)
        assert float(squared(round_value)) == pytest.approx(radius_squared / (C * C))
        assert evaluate(round_value.expr, algebra=model.algebra).almost_equal(round_value)
        assert si.classify(round_value, representation="dual") == model.classify(expected, representation="dual")


def test_average_velocity_is_frame_coordinate_displacement_over_time(model):
    first = model.event(1, 0, 0, 0)
    second = model.event(3, 0.6, 0.8, 0)
    np.testing.assert_allclose(model.velocity_between(first, second, unit="c"), (0.3, 0.4, 0))
    np.testing.assert_allclose(model.velocity_between(second, first), C * np.array((0.3, 0.4, 0)))
    assert model.speed_between(first, second, unit="%c") == pytest.approx(50)
    assert not model.velocity_between(first, second).flags.writeable
    assert model.speed_between(first, model.event(2, 2, 0, 0), unit="c") == pytest.approx(2)
    with pytest.raises(ValueError, match="nonzero time"):
        model.velocity_between(first, model.event(1, 1, 0, 0))


def test_one_g_scale_interprets_rotor_trajectory_without_changing_metric(model):
    scale = SpacetimeUnits.for_acceleration(1, unit="g")
    physical = ConformalSpacetimeModel(model.algebra, unit_scale=scale)
    g0, g1, _, _ = physical.spacetime_basis_vectors()
    rotor = exp(0.5 * (g1 * g0) / 2)
    event = physical.event(-g1 + sandwich(rotor, g1))
    natural = physical.coordinates(event)
    assert natural[0] == pytest.approx(math.sinh(0.5))
    assert natural[1] == pytest.approx(math.cosh(0.5) - 1)
    assert physical.time_in(natural[0]) == pytest.approx(C / G * math.sinh(0.5))
    assert physical.distance_in(natural[1]) == pytest.approx(C * C / G * (math.cosh(0.5) - 1))
    assert physical.acceleration_in(1, "g") == pytest.approx(1)
    assert physical.format_acceleration(1) == "1 g"
    velocity = sandwich(rotor, g0)
    time_component = float(scalar_product(velocity, g0)) / float(squared(g0))
    space_component = float(scalar_product(velocity, g1)) / float(squared(g1))
    assert space_component / time_component == pytest.approx(math.tanh(0.5))


@pytest.mark.parametrize(
    ("quantity", "physical", "unit", "expected"),
    (
        ("time", 0, "s", "0 s"),
        ("time", 1e-9, "s", "1 ns"),
        ("time", 2e-6, "s", "2 μs"),
        ("time", -0.003, "s", "-3 ms"),
        ("time", 90, "s", "1.5 min"),
        ("time", 7200, "s", "2 h"),
        ("time", 2, "day", "2 day"),
        ("time", 3, "week", "3 week"),
        ("time", 2, "month", "2 month"),
        ("time", 3, "year", "3 year"),
        ("distance", 0, "m", "0 m"),
        ("distance", 3, "nm", "3 nm"),
        ("distance", 4, "um", "4 μm"),
        ("distance", 5, "mm", "5 mm"),
        ("distance", 6, "m", "6 m"),
        ("distance", 7, "km", "7 km"),
        ("distance", 1, "AU", "1 AU"),
        ("distance", 0.5, "ly", "0.5 ly"),
        ("speed", 3, "m/s", "3 m/s"),
        ("speed", 4, "km/s", "4 km/s"),
        ("speed", 97, "%c", "97% c"),
        ("speed", -0.5, "c", "-50% c"),
    ),
)
def test_human_friendly_formatting_preserves_sign_and_selects_magnitude(quantity, physical, unit, expected):
    backend = SpacetimeUnits()
    natural = getattr(backend, quantity + "_from")(physical, unit)
    assert getattr(backend, "format_" + quantity)(natural) == expected


def test_model_numeric_and_format_methods_share_backend(model):
    assert model.time_in(1) == 1
    assert model.distance_in(1) == C
    assert model.speed_in(0.97) == pytest.approx(0.97 * C)
    assert model.format_time(3600) == "1 h"
    assert model.format_distance(model.unit_scale.distance_from(1, "AU")) == "1 AU"
    assert model.format_speed(0.97) == "97% c"
    assert model.format_speed(0.97, "m/s", precision=6) == "2.90799e+08 m/s"
    assert model.unit_scale.format_time(60, "s") == "60 s"
    assert model.unit_scale.format_distance(1, "light-second") == "1 light-second"


@pytest.mark.parametrize("quantity", ("time", "distance", "speed", "acceleration"))
def test_converters_reject_wrong_dimensions_nonfinite_and_overflow(quantity):
    backend = SpacetimeUnits()
    for method in (getattr(backend, quantity + "_in"), getattr(backend, quantity + "_from")):
        with pytest.raises(ValueError, match="unsupported"):
            method(1, "nonsense")
        for value in (float("nan"), float("inf")):
            with pytest.raises(ValueError, match="finite"):
                method(value)
        with pytest.raises(TypeError, match="real number"):
            method(True)
    with pytest.raises(ValueError, match="finite"):
        backend.distance_in(1e308)


@pytest.mark.parametrize("value", (0, -1, float("nan"), float("inf"), 1e308, 1e-308))
def test_invalid_scales_are_rejected(value):
    with pytest.raises(ValueError):
        SpacetimeUnits(value)


def test_model_rejects_ambiguous_scale_and_unknown_coordinate_policy(model):
    with pytest.raises(ValueError, match="not both"):
        ConformalSpacetimeModel(model.algebra, time_scale_seconds=1, unit_scale=SpacetimeUnits())
    with pytest.raises(TypeError, match="SpacetimeUnits"):
        ConformalSpacetimeModel(model.algebra, unit_scale=1)
    for policy in ("m/s", ("m", "s"), ["s", "m"], ("s",), np.array(("s", "m"))):
        with pytest.raises(ValueError):
            ConformalSpacetimeModel(model.algebra, units=policy)
    with pytest.raises(ValueError, match="precision"):
        model.format_time(1, precision=0)
    with pytest.raises(ValueError, match="positive"):
        SpacetimeUnits.for_acceleration(0)


def test_coordinate_conversion_rejects_overflow_and_small_scale_resolves_metres(model):
    small = ConformalSpacetimeModel(model.algebra, units="si", time_scale_seconds=1 / C)
    origin = small.event(0, 0, 0, 0)
    next_event = small.event(0, 1, 0, 0)
    assert small.separation_squared(origin, next_event) == pytest.approx(-1)
    assert small.classify(small.flat_line(origin, next_event)).causal == "spacelike"
    with pytest.raises(ValueError, match="finite"):
        small.event(1e308, 0, 0, 0)
    with pytest.raises(TypeError, match="real numbers"):
        small.event(True, 0, 0, 0)
    enormous = ConformalSpacetimeModel(model.algebra, time_scale_seconds=1e299)
    with pytest.raises(ValueError, match="finite"):
        enormous.coordinates(model.event(0, 100, 0, 0), units="si")
