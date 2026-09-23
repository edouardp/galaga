"""CGA object classification and semantic highlight recipes."""

from __future__ import annotations

import numpy as np
import pytest

import galaga_annotation as ga
from galaga import Algebra, outer_product, presets
from galaga.cga import ConformalModel


@pytest.fixture(scope="module")
def cga() -> ConformalModel:
    return ConformalModel(Algebra(config=presets.lengyel_cga(), expr=True), expr=True)


@pytest.fixture(scope="module")
def objects(cga: ConformalModel) -> dict[str, object]:
    a = cga.up((0.75, 1.0, 2.0))
    b = cga.up((-0.25, 0.1, 0.2))
    c = cga.up((0.0, 1.0, 0.0))
    d = cga.up((0.0, 0.0, 1.0))
    return {
        "round point": a,
        "flat point": outer_product(a, cga.infinity),
        "dipole": outer_product(a, b),
        "line": outer_product(a, b, cga.infinity),
        "circle": outer_product(a, b, c),
        "plane": outer_product(a, b, c, cga.infinity),
        "sphere": outer_product(a, b, c, d),
    }


@pytest.mark.parametrize(
    "kind",
    ("round point", "flat point", "dipole", "line", "circle", "plane", "sphere"),
)
def test_direct_object_kinds_are_classified(cga: ConformalModel, objects, kind: str) -> None:
    value = objects[kind]
    classified = ga.classify_cga(value, cga)
    assert classified.kind == kind
    assert classified.grade == value.homogeneous_grade()
    assert classified.simple is True
    assert classified.flat == (kind in {"flat point", "line", "plane"})


def test_classification_is_projective_above_the_zero_floor(cga: ConformalModel, objects) -> None:
    for kind, value in objects.items():
        expected_parts = set(ga.cga_parts(value, cga))
        for scale in (1e-4, -2.5, 1e6):
            scaled = scale * value
            classified = ga.classify_cga(scaled, cga)
            assert classified.kind == kind
            assert classified.simple is True
            assert set(ga.cga_parts(scaled, cga)) == expected_parts


def test_grade_one_distinguishes_direct_points_and_dual_planes(cga: ConformalModel) -> None:
    e1, _, _ = cga.euclidean_basis_vectors()
    assert ga.classify_cga(cga.origin, cga).kind == "round point"
    assert ga.classify_cga(cga.infinity, cga).kind == "point at infinity"
    assert ga.classify_cga(e1, cga).kind == "dual plane"
    assert ga.classify_cga(e1 + 2 * cga.infinity, cga).kind == "dual plane"
    assert ga.classify_cga(cga.origin + cga.infinity, cga).kind == "dual sphere"


def test_scalar_general_and_zero_values_are_distinguished(cga: ConformalModel, objects) -> None:
    value = objects["round point"]
    scalar = ga.classify_cga(value.algebra.scalar(1.0), cga)
    pseudoscalar = ga.classify_cga(value.algebra.I, cga)
    assert scalar.kind == "scalar" and scalar.flat is None and scalar.simple is True
    assert pseudoscalar.kind == "pseudoscalar" and pseudoscalar.flat is None and pseudoscalar.simple is True
    assert ga.classify_cga(value + value.algebra.scalar(1.0), cga).kind == "general"
    assert ga.classify_cga(value.algebra.scalar(0.0), cga).kind == "zero"


def test_classification_uses_and_validates_its_tolerance(cga: ConformalModel) -> None:
    e1, e2, _ = cga.euclidean_basis_vectors()
    nearly_vector = e1 + 5e-10 * outer_product(e1, e2)
    assert ga.classify_cga(nearly_vector, cga, atol=1e-9).kind == "dual plane"
    assert ga.classify_cga(nearly_vector, cga, atol=1e-12).kind == "general"
    with pytest.raises(TypeError, match="atol"):
        ga.classify_cga(e1, cga, atol=True)
    for invalid in (-1.0, float("inf"), float("nan")):
        with pytest.raises(ValueError, match="atol"):
            ga.classify_cga(e1, cga, atol=invalid)


def test_classification_and_parts_validate_their_inputs(cga: ConformalModel, objects) -> None:
    with pytest.raises(TypeError, match="Multivector"):
        ga.classify_cga(3.0, cga)
    with pytest.raises(TypeError, match="ConformalModel"):
        ga.classify_cga(objects["dipole"], object())
    other_model = ConformalModel(Algebra(config=presets.lengyel_cga()))
    with pytest.raises(ValueError, match="model algebra"):
        ga.classify_cga(objects["dipole"], other_model)
    with pytest.raises(ValueError, match="model algebra"):
        ga.cga_parts(objects["dipole"], other_model)
    planar_model = ConformalModel(Algebra(config=presets.cga(2)))
    with pytest.raises(ValueError, match="three-dimensional"):
        ga.classify_cga(planar_model.origin, planar_model)
    with pytest.raises(ValueError, match="three-dimensional"):
        ga.highlight_cga(planar_model)
    with pytest.raises(ValueError, match="decomposition"):
        ga.highlight_cga(cga, decomposition="invented")
    with pytest.raises(TypeError, match="ConformalModel"):
        ga.highlight_cga(object())


def test_non_simple_bivector_is_not_named_or_highlighted_as_a_dipole(cga: ConformalModel) -> None:
    e1, e2, e3, e4, _ = cga.algebra.basis_vectors()
    value = outer_product(e1, e2) + outer_product(e3, e4)
    assert np.any(np.abs(outer_product(value, value).data) > 1e-9)
    classified = ga.classify_cga(value, cga)
    assert classified.kind == "general"
    assert classified.grade == 2
    assert classified.simple is False
    rendered = ga.highlight_cga(cga)(value).latex()
    for dipole_label in ("carrier line", "flat point", "cocarrier normal", "cocarrier position"):
        assert dipole_label not in rendered


def test_dipole_parts_are_the_four_lengyel_families(cga: ConformalModel, objects) -> None:
    parts = ga.cga_parts(objects["dipole"], cga)
    assert set(parts) == {"round_weight", "round_bulk", "flat_bulk", "flat_weight"}


def test_dipole_without_a_weight_family_still_highlights(cga: ConformalModel) -> None:
    # Equal-radius points produce a decomposable dipole with no e45
    # flat-weight component; derive that case instead of deleting a coefficient.
    dipole = outer_product(cga.up((1.0, 0.0, 0.0)), cga.up((0.0, 1.0, 0.0)))
    assert not np.any(np.abs(outer_product(dipole, dipole).data) > 1e-9)
    parts = ga.cga_parts(dipole, cga)
    assert "flat_weight" not in parts
    assert ga.classify_cga(dipole, cga).kind == "dipole"
    view = ga.highlight_cga(cga)(dipole)
    assert view.plain is dipole
    assert r"\colorbox{#d8c4ee}{" in view.latex()


def test_dipole_highlight_keeps_contiguous_fills_with_overbraces_on_top() -> None:
    cga = ConformalModel(Algebra(config=presets.lengyel_cga(), expr=True), expr=True)
    dipole = outer_product(cga.up((0.75, 1.0, 2.0)), cga.up((-0.25, 0.1, 0.2)))
    view = ga.highlight_cga(cga)(dipole)
    assert view.plain is dipole
    rendered = view.latex()
    assert rendered.count(r"\colorbox{#b8e6bf}") == 1
    assert rendered.count(r"\colorbox{#d8c4ee}") == 1
    # Labels and overbraces are independent overlays over one continuous fill.
    assert (
        r"\colorbox{#b8e6bf}{$\mathord{\mathrlap{\smash[b]{\underset{\mathclap{\textcolor{#2f7d4f}{"
        r"\text{carrier line}}}}{\phantom{" in rendered
    )
    assert rendered.count(r"\overbrace") == 4
    assert r"\overgroup" not in rendered
    assert "cocarrier normal" in rendered
    assert "cocarrier position" in rendered
    assert (
        r"\colorbox{#d8c4ee}{$\mathrlap{\smash[b]{\underset{\mathclap{\textcolor{#6b4a9e}{"
        r"\text{flat point}}}}{\phantom{" in rendered
    )
    green_start = rendered.index(r"\colorbox{#b8e6bf}")
    normal_start = rendered.rindex("cocarrier normal")
    purple_start = rendered.index(r"\colorbox{#d8c4ee}")
    position_start = rendered.rindex("cocarrier position")
    assert green_start < normal_start < purple_start < position_start
    # Marker chrome is coloured; the highlighted terms keep their own colour.
    assert r"\overbrace{\textcolor{#0099cc}{" not in rendered
    assert r"\textcolor{#0099cc}{-\mathbf{e}_{41}" not in rendered
    assert "- -" not in rendered
    assert "+ -" not in rendered


def test_dipole_leading_negative_sign_stays_outside_the_default_span(cga: ConformalModel, objects) -> None:
    # Recipe term targets use the public unsigned default, so the sample
    # dipole's leading minus is outside both its carrier fill and callout.
    rendered = ga.highlight_cga(cga)(objects["dipole"]).latex()
    assert r"\colorbox{#b8e6bf}{$" in rendered
    assert (
        r"\overbrace{\textcolor{black}{\vphantom{\raisebox{4px}{\rule{0pt}{1em}}}"
        r"\phantom{\mathbf{e}_{41}" in rendered
    )
    assert r"\phantom{\mathord{-}\>\mathbf{e}_{41}" not in rendered


def test_cga_highlight_default_is_the_explicit_overbrace(cga: ConformalModel, objects) -> None:
    default = ga.highlight_cga(cga)(objects["dipole"]).latex()
    explicit = ga.highlight_cga(cga, over_marker="overbrace")(objects["dipole"]).latex()
    assert default == explicit
    assert r"\overbrace" in default
    assert r"\overgroup" not in default


def test_circle_families_match_lengyel_blade_groups(cga: ConformalModel, objects) -> None:
    parts = ga.cga_parts(objects["circle"], cga)

    def masks(*names: str) -> set[int]:
        return {ga.blade_mask(cga.algebra.blade(name))[0] for name in names}

    assert set(parts["round_weight"].masks) == masks("e423", "e431", "e412")
    assert set(parts["round_bulk"].masks) == masks("e321")
    assert set(parts["flat_weight"].masks) == masks("e415", "e425", "e435")
    assert set(parts["flat_bulk"].masks) == masks("e235", "e315", "e125")


def test_circle_component_role_view_remains_available(cga: ConformalModel, objects) -> None:
    rendered = ga.highlight_cga(cga, decomposition="components")(objects["circle"]).latex()
    assert all(label in rendered for label in ("plane part", "center part", "flat part", "flat weight"))
    assert "carrier plane" not in rendered
    assert "cocarrier direction" not in rendered


@pytest.mark.parametrize(
    ("kind", "labels"),
    (
        ("round point", ("origin", "position", "infinity")),
        (
            "circle",
            ("carrier plane", "flat line", "cocarrier direction", "cocarrier moment"),
        ),
        ("sphere", ("origin part", "flat part", "flat weight")),
    ),
)
def test_round_object_highlights_explain_component_families(cga: ConformalModel, objects, kind, labels) -> None:
    rendered = ga.highlight_cga(cga)(objects[kind]).latex()
    assert all(label in rendered for label in labels)
    assert r"\colorbox" in rendered
    assert "- -" not in rendered


@pytest.mark.parametrize("marker", ("overgroup", "overbrace", "overline", "overbracket"))
def test_cocarrier_marker_style_is_configurable(cga: ConformalModel, objects, marker: str) -> None:
    rendered = ga.highlight_cga(cga, over_marker=marker)(objects["dipole"]).latex()
    # Two visible cocarrier callouts plus two invisible bounds reservations.
    assert rendered.count("\\" + marker) == 4
    for other in ("overgroup", "overbrace", "overline", "overbracket"):
        if other != marker:
            assert rendered.count("\\" + other) == 0


def test_invalid_over_marker_is_rejected(cga: ConformalModel) -> None:
    with pytest.raises(ValueError, match="over_marker"):
        ga.highlight_cga(cga, over_marker="underbrace")


def test_highlight_object_alias_matches_highlight_cga(cga: ConformalModel, objects) -> None:
    alias = ga.highlight_object(cga, over_marker="overbrace")(objects["dipole"]).latex()
    direct = ga.highlight_cga(cga, over_marker="overbrace")(objects["dipole"]).latex()
    assert alias == direct
    assert ga.OverMarker is not None
