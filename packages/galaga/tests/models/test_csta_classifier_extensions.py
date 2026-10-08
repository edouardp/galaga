"""Geometric names must follow actual incidence and induced metric signs."""

import numpy as np
import pytest

from galaga import Algebra, exp, outer_product, presets, right_hodge_dual, sandwich, squared
from galaga.models import ConformalSpacetimeModel


@pytest.fixture
def model():
    return ConformalSpacetimeModel(Algebra(config=presets.csta(), user_config_files=False))


def classifications(model, value):
    for scale in (1, -3, 7):
        yield model.classify(scale * value)
        yield model.classify(right_hodge_dual(scale * value), representation="dual")


def test_null_pair_represents_an_entire_lightlike_line(model):
    first = model.event(2, 1, -1, 0)
    second = model.event(3, 2, -1, 0)
    pair = first ^ second
    assert float(squared(model.down(second) - model.down(first))) == pytest.approx(0)
    for parameter in (-2, 0.25, 2):
        event = model.event(2 + parameter, 1 + parameter, -1, 0)
        assert (event ^ pair).almost_equal(model.algebra.scalar(0))
    for result in classifications(model, pair):
        assert result.kind == "lightlike line" and result.causal == "null"


@pytest.mark.parametrize(
    ("directions", "expected", "inertia"),
    (
        ((0, 1), "timelike", (1, 1, 0)),
        ((1, 2), "spacelike", (0, 2, 0)),
        (("null", 2), "null", (0, 1, 1)),
        ((0, 1, 2), "timelike", (1, 2, 0)),
        ((1, 2, 3), "spacelike", (0, 3, 0)),
        (("null", 2, 3), "null", (0, 2, 1)),
    ),
)
def test_flat_carrier_signatures_match_spacetime_products(model, directions, expected, inertia):
    basis = model.spacetime_basis_vectors()
    vectors = tuple(basis[0] + basis[1] if index == "null" else basis[index] for index in directions)
    gram = np.array([[float((a * b).grade(0)) for b in vectors] for a in vectors])
    eigenvalues = np.linalg.eigvalsh(gram)
    computed = (sum(eigenvalues > 1e-9), sum(eigenvalues < -1e-9), sum(abs(eigenvalues) <= 1e-9))
    assert computed == inertia
    origin = model.event(1, 2, -1, 0)
    events = (origin, *(model.event(model.down(origin) + v) for v in vectors))
    flat = outer_product(*events, model.infinity)
    for event in events:
        assert (event ^ flat).almost_equal(model.algebra.scalar(0))
    for result in classifications(model, flat):
        assert result.causal == expected
        assert dict(result.properties)["carrier_inertia"] == computed


@pytest.mark.parametrize("radius", (-1, 0, 1))
@pytest.mark.parametrize("lorentzian", (False, True))
def test_round_surface_names_follow_carrier_and_signed_radius(model, radius, lorentzian):
    g0, g1, g2, g3 = model.spacetime_basis_vectors()
    anchor = model.origin + radius * model.infinity / 2
    assert float(squared(anchor)) == pytest.approx(-radius)
    directions = (g0, g1, g2) if lorentzian else (g1, g2, g3)
    surface = outer_product(anchor, *directions)
    names = (
        {1: "two-sheet hyperboloid", -1: "one-sheet hyperboloid", 0: "cone"}
        if lorentzian
        else {-1: "sphere", 0: "point sphere", 1: "imaginary sphere"}
    )
    for result in classifications(model, surface):
        assert result.kind == names[radius]
        assert dict(result.properties)["signed_radius_squared"] == pytest.approx(radius)
        assert dict(result.properties)["carrier_inertia"] == ((1, 2, 0) if lorentzian else (0, 3, 0))
    if lorentzian:
        point = (1, 0, 0, 0) if radius == 1 else (0, 1, 0, 0) if radius == -1 else (1, 1, 0, 0)
        # The example and its tangent vectors satisfy the metric equation.
        q = model.spacetime_vector(point)
        assert float(squared(q)) == pytest.approx(radius)
        assert (model.event(q) ^ surface).almost_equal(model.algebra.scalar(0))
        tangents = (g1, g2) if radius == 1 else (g0, g2) if radius == -1 else (g0 + g1, g2)
        for tangent in tangents:
            assert float((q * tangent).grade(0)) == pytest.approx(0)
        tangent_gram = np.array([[float((a * b).grade(0)) for b in tangents] for a in tangents])
        eigenvalues = np.linalg.eigvalsh(tangent_gram)
        computed_tangents = (sum(eigenvalues > 1e-9), sum(eigenvalues < -1e-9), sum(abs(eigenvalues) <= 1e-9))
        assert dict(model.classify(surface).properties)["tangent_inertia"] == computed_tangents
    elif radius == -1:
        for q in ((0, 1, 0, 0), (0, 0, -1, 0), (0, 0, 0, 1)):
            assert (model.event(q) ^ surface).almost_equal(model.algebra.scalar(0))


def test_sphere_from_four_events_and_boosted_sphere_keep_their_geometry(model):
    sphere = outer_product(*(model.event(q) for q in ((0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1), (0, -1, 0, 0))))
    g0, g1, _, _ = model.spacetime_basis_vectors()
    rotor = exp(0.3 * g1 * g0)
    for result in classifications(model, sandwich(rotor, sphere)):
        assert result.kind == "sphere" and result.causal == "spacelike"


@pytest.mark.parametrize("surface", (False, True))
def test_null_carrier_parabolic_sections_have_spacelike_tangents_and_no_center(model, surface):
    points = ((0, 0, 0, 0), (0.5, 0.5, 1, 0), (0.5, 0.5, -1, 0), (0.5, 0.5, 0, 1))
    blade = outer_product(*(model.event(q) for q in points[: 4 if surface else 3]))
    for y, z in ((2, 0), (-0.25, 0), (0, 1) if surface else (0, 0)):
        t = (y * y + z * z) / 2
        q = model.event(t, t, y, z)
        assert (q ^ blade).almost_equal(model.algebra.scalar(0))
    tangent = model.spacetime_vector((2, 2, 1, 0))
    assert float(squared(tangent)) < 0
    for result in classifications(model, blade):
        assert result.kind == ("paraboloid" if surface else "parabola")
        assert result.causal == "spacelike"
        assert "center" not in dict(result.properties)


@pytest.mark.parametrize(
    ("radius", "grade", "kind"),
    (
        (-1, 3, "parallel null line pair"),
        (0, 3, "double null line"),
        (1, 3, "imaginary null line pair"),
        (-1, 4, "null cylinder"),
        (0, 4, "null line"),
        (1, 4, "imaginary null cylinder"),
    ),
)
def test_centerless_null_round_degeneracies(model, radius, grade, kind):
    g0, g1, g2, g3 = model.spacetime_basis_vectors()
    anchor = model.origin + radius * model.infinity / 2
    directions = (g0 + g1, g2) if grade == 3 else (g0 + g1, g2, g3)
    blade = outer_product(anchor, *directions)
    assert float(squared(anchor)) == pytest.approx(-radius)
    if radius <= 0:
        assert (model.event(2, 2, np.sqrt(-radius), 0) ^ blade).almost_equal(model.algebra.scalar(0))
    for result in classifications(model, blade):
        assert result.kind == kind
        assert "center" not in dict(result.properties)


def test_round_classification_survives_translations_dilations_and_boosts(model):
    g0, g1, g2, g3 = model.spacetime_basis_vectors()
    rotor = exp(model.infinity * g1 / 2) * exp(0.2 * (model.origin ^ model.infinity)) * exp(0.3 * g1 * g0)
    sphere = (model.origin - model.infinity / 2) ^ g1 ^ g2 ^ g3
    parabola = outer_product(*(model.event(q) for q in ((0, 0, 0, 0), (0.5, 0.5, 1, 0), (0.5, 0.5, -1, 0))))
    for object_value, kind in ((sphere, "sphere"), (parabola, "parabola")):
        transformed = sandwich(rotor, object_value)
        assert model.classify(transformed).kind == kind
    sphere_properties = dict(model.classify(sandwich(rotor, sphere)).properties)
    assert sphere_properties["signed_radius_squared"] == pytest.approx(-np.exp(0.8))
    np.testing.assert_allclose(sphere_properties["center"], (0, 1, 0, 0), atol=1e-9)


def test_ideal_flats_are_not_reported_as_finite_affine_objects(model):
    g0, g1, _, _ = model.spacetime_basis_vectors()
    ideal = g0 ^ g1 ^ model.infinity
    result = model.classify(ideal)
    assert result.kind == "ideal flat line" and result.finite is False
