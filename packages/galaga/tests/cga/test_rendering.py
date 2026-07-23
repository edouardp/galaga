from __future__ import annotations

import numpy as np
import pytest

from galaga import Algebra, DisplayPolicy, Multivector, Notation, outer_product, p_cga
from galaga.cga import ConformalModel
from galaga.expression import Call, evaluate


@pytest.fixture
def circle() -> tuple[ConformalModel, Multivector]:
    algebra = Algebra(
        config=p_cga(),
        notation=Notation.lengyel(),
        display=DisplayPolicy(content="full"),
    )
    cga = ConformalModel(algebra, expr=True)
    a = cga.up((0.0, 0.0, 0.0))
    b = cga.up((1.0, 0.0, 0.0))
    c = cga.up((0.0, 1.0, 0.0))
    return cga, outer_product(a, b, c).named("C")


def test_lengyel_cga_semantic_functions_use_the_wiki_names(
    circle: tuple[ConformalModel, Multivector],
) -> None:
    cga, value = circle

    rendered = {
        "att": cga.att(value).latex(content="expr"),
        "car": cga.car(value).latex(content="expr"),
        "ccr": cga.ccr(value).latex(content="expr"),
        "cen": cga.cen(value).latex(content="expr"),
        "con": cga.con(value).latex(content="expr"),
        "par": cga.par(value).latex(content="expr"),
    }

    assert rendered == {name: rf"\operatorname{{{name}}}(C)" for name in rendered}


def test_default_notation_keeps_descriptive_semantic_names(
    circle: tuple[ConformalModel, Multivector],
) -> None:
    cga, value = circle

    assert cga.att(value).latex(content="expr", notation=Notation.default()) == (r"\operatorname{attitude}(C)")
    assert cga.flat_center(value).latex(content="expr") == r"\operatorname{flat\_center}(C)"


def test_semantic_expressions_retain_hidden_model_roles_and_remain_evaluable(
    circle: tuple[ConformalModel, Multivector],
) -> None:
    cga, value = circle
    results = (
        cga.attitude(value),
        cga.carrier(value),
        cga.cocarrier(value),
        cga.center(value),
        cga.flat_center(value),
        cga.container(value),
        cga.partner(value),
    )

    for result in results:
        assert isinstance(result.expr, Call)
        assert result.expr.parameters
        evaluated = evaluate(
            result.expr,
            algebra=cga.algebra,
            environment={"C": value},
        )
        assert evaluated.almost_equal(result)
        assert "infinity" not in result.latex(content="expr")


def test_lengyel_cga_component_parts_use_circle_and_square_subscripts(
    circle: tuple[ConformalModel, Multivector],
) -> None:
    cga, value = circle
    parts = (
        cga.round_bulk_part(value),
        cga.round_weight_part(value),
        cga.flat_bulk_part(value),
        cga.flat_weight_part(value),
    )

    assert [part.latex(content="expr") for part in parts] == [
        r"C_{\text{●}}",
        r"C_{\text{○}}",
        r"C_{\text{■}}",
        r"C_{\text{□}}",
    ]
    assert [part.unicode(content="expr") for part in parts] == ["C_●", "C_○", "C_■", "C_□"]
    assert [part.ascii(content="expr") for part in parts] == [
        "round_bulk_part(C)",
        "round_weight_part(C)",
        "flat_bulk_part(C)",
        "flat_weight_part(C)",
    ]


def test_cga_component_parts_are_an_exact_four_way_decomposition(
    circle: tuple[ConformalModel, Multivector],
) -> None:
    cga, value = circle
    parts = (
        cga.round_bulk_part(value),
        cga.round_weight_part(value),
        cga.flat_bulk_part(value),
        cga.flat_weight_part(value),
    )

    assert sum(parts, cga.algebra.scalar(0)) == value
    for part in parts:
        assert isinstance(part.expr, Call)
        assert evaluate(part.expr, algebra=cga.algebra, environment={"C": value}) == part

    origin_mask = int(np.flatnonzero(cga.origin.data)[0])
    infinity_mask = int(np.flatnonzero(cga.infinity.data)[0])
    for part, contains_origin, contains_infinity in zip(
        parts,
        (False, True, False, True),
        (False, False, True, True),
        strict=True,
    ):
        for mask in np.flatnonzero(part.data):
            assert bool(mask & origin_mask) is contains_origin
            assert bool(mask & infinity_mask) is contains_infinity


def test_lengyel_weighted_norms_use_the_posters_semantic_subscripts(
    circle: tuple[ConformalModel, Multivector],
) -> None:
    cga, value = circle
    norms = (
        cga.weighted_center_norm(value),
        cga.weighted_radius_norm(value),
        cga.round_bulk_norm(value),
        cga.round_weight_norm(value),
        cga.flat_bulk_norm(value),
        cga.flat_weight_norm(value),
    )

    assert [norm.latex(content="expr") for norm in norms] == [
        r"\lVert C \rVert_{\text{ⓒ}}",
        r"\lVert C \rVert_{\text{ⓡ}}",
        r"\lVert C \rVert_{\text{●}}",
        r"\lVert C \rVert_{\text{○}}",
        r"\lVert C \rVert_{\text{■}}",
        r"\lVert C \rVert_{\text{□}}",
    ]
    assert [norm.unicode(content="expr") for norm in norms] == [
        "‖C‖_ⓒ",
        "‖C‖_ⓡ",
        "‖C‖_●",
        "‖C‖_○",
        "‖C‖_■",
        "‖C‖_□",
    ]
    assert [norm.ascii(content="expr") for norm in norms] == [
        "weighted_center_norm(C)",
        "weighted_radius_norm(C)",
        "round_bulk_norm(C)",
        "round_weight_norm(C)",
        "flat_bulk_norm(C)",
        "flat_weight_norm(C)",
    ]

    assert cga.center_norm(value).latex(content="expr") == (
        r"\frac{\lVert C \rVert_{\text{ⓒ}}}{\lVert C \rVert_{\text{○}}}"
    )
    assert cga.radius_norm(value).latex(content="expr") == (
        r"\frac{\lVert C \rVert_{\text{ⓡ}}}{\lVert C \rVert_{\text{○}}}"
    )
    assert cga.center_norm(value).unicode(content="expr") == "‖C‖_ⓒ / ‖C‖_○"
    assert cga.radius_norm(value).unicode(content="expr") == "‖C‖_ⓡ / ‖C‖_○"
    assert cga.center_norm(value).ascii(content="expr") == "center_norm(C)"
    assert cga.radius_norm(value).ascii(content="expr") == "radius_norm(C)"

    assert cga.center_distance(value).latex(content="expr") == r"\operatorname{center\_distance}(C)"
    assert cga.radius(value).latex(content="expr") == r"\operatorname{rad}(C)"
