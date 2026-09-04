from pathlib import Path

import marimo as mo
import numpy as np
import pytest
from marimo._runtime import state as marimo_state
from marimo._runtime.state import State

from galaga import Algebra, Multivector, meet, outer_product, p_cga
from galaga.cga import ConformalModel
from galaga_anywidget import DEFAULT_COLOR_CYCLE, viz
from galaga_anywidget.cga2d import CGA2DPlot, cga2d


@pytest.fixture
def cga() -> ConformalModel:
    return ConformalModel(Algebra(config=p_cga(spatial_dim=2)), expr=True)


def _objects(cga: ConformalModel):
    p = cga.up(1.0, 0.0).named("P")
    q = cga.up(0.0, 1.0).named("Q")
    r = cga.up(-1.0, 0.0).named("R")
    line = outer_product(p, q, cga.infinity).named("L")
    circle = outer_product(p, q, r).named("C")
    return p, q, r, line, circle


def test_plot_classifies_direct_objects_and_derives_drawing_geometry(cga: ConformalModel) -> None:
    p, q, _, line, circle = _objects(cga)
    plot = CGA2DPlot(cga).add("P", p).add("L", line).add("C", circle)

    assert [item["kind"] for item in plot.scene] == ["point", "line", "circle"]
    point_scene, line_scene, circle_scene = plot.scene
    assert (point_scene["x"], point_scene["y"]) == pytest.approx((1.0, 0.0))
    for point in (p, q):
        x, y = cga.coordinates(point)
        assert line_scene["a"] * x + line_scene["b"] * y + line_scene["c"] == pytest.approx(0.0)
    assert (circle_scene["cx"], circle_scene["cy"], circle_scene["r"]) == pytest.approx((0.0, 0.0, 1.0))


def test_plot_splits_real_circle_meet_dipole_from_cga_semantics(cga: ConformalModel) -> None:
    circle_a = cga.dual(cga.round_point(-1.0, 0.0, radius_squared=-4.0)).named("C1")
    circle_b = cga.dual(cga.round_point(1.0, 0.0, radius_squared=-4.0)).named("C2")
    dipole = meet(circle_a, circle_b).named("D")

    plot = CGA2DPlot(cga).add("D", dipole)

    assert dipole.homogeneous_grade() == 2
    assert plot.scene[0]["kind"] == "dipole"
    assert plot.scene[0]["real"] is True
    assert plot.scene[0]["tangent"] is False
    assert plot.scene[0]["radius_squared"] == pytest.approx(3.0)
    endpoints = [
        (plot.scene[0]["x1"], plot.scene[0]["y1"]),
        (plot.scene[0]["x2"], plot.scene[0]["y2"]),
    ]
    endpoints.sort(key=lambda coordinates: coordinates[1])
    assert endpoints == pytest.approx([(0.0, -(3.0**0.5)), (0.0, 3.0**0.5)])
    for coordinates in endpoints:
        intersection = cga.up(coordinates)
        assert np.allclose(outer_product(intersection, dipole).data, 0.0, rtol=0.0, atol=1e-12)
        assert np.allclose(outer_product(intersection, circle_a).data, 0.0, rtol=0.0, atol=1e-12)
        assert np.allclose(outer_product(intersection, circle_b).data, 0.0, rtol=0.0, atol=1e-12)


@pytest.mark.parametrize(
    ("radius", "real", "tangent"),
    [(1.0, True, True), (0.5, False, False)],
)
def test_plot_distinguishes_tangent_and_imaginary_circle_meet_dipoles(
    cga: ConformalModel,
    radius: float,
    real: bool,
    tangent: bool,
) -> None:
    radius_squared = -(radius * radius)
    circle_a = cga.dual(cga.round_point(-1.0, 0.0, radius_squared=radius_squared))
    circle_b = cga.dual(cga.round_point(1.0, 0.0, radius_squared=radius_squared))
    dipole = meet(circle_a, circle_b)

    plot = CGA2DPlot(cga).add("D", dipole)

    assert plot.scene[0]["real"] is real
    assert plot.scene[0]["tangent"] is tangent
    if tangent:
        assert (plot.scene[0]["x1"], plot.scene[0]["y1"]) == pytest.approx((0.0, 0.0))
        assert (plot.scene[0]["x2"], plot.scene[0]["y2"]) == pytest.approx((0.0, 0.0))
    else:
        assert plot.scene[0]["radius_squared"] < 0.0
        assert "x1" not in plot.scene[0]


def test_plot_keeps_concentric_circle_meet_as_hidden_degenerate_dipole(
    cga: ConformalModel,
) -> None:
    circle_a = cga.dual(cga.round_point(0.0, 0.0, radius_squared=-4.0))
    circle_b = cga.dual(cga.round_point(0.0, 0.0, radius_squared=-1.0))
    dipole = meet(circle_a, circle_b)

    plot = CGA2DPlot(cga).add("D", dipole)

    assert dipole.homogeneous_grade() == 2
    assert plot.scene[0]["kind"] == "dipole"
    assert plot.scene[0]["finite"] is False
    assert plot.scene[0]["real"] is False


def test_plot_rejects_flat_point_as_dipole(cga: ConformalModel) -> None:
    flat_point = outer_product(cga.up(1.0, 2.0), cga.infinity)

    with pytest.raises(ValueError, match="does not yet support flat points"):
        CGA2DPlot(cga).add("F", flat_point)


def test_default_colors_cycle_in_object_order(cga: ConformalModel) -> None:
    p, q, r, line, circle = _objects(cga)
    plot = CGA2DPlot(cga)
    for key, value in zip(("P", "Q", "R", "L", "C"), (p, q, r, line, circle), strict=True):
        plot.add(key, value)

    assert [item["color"] for item in plot.scene] == list(DEFAULT_COLOR_CYCLE[:5])


def test_drag_state_reconstructs_named_up_multivector_and_fires_callback(cga: ConformalModel) -> None:
    p, *_ = _objects(cga)
    plot = CGA2DPlot(cga).add_point("P", p, draggable=True)
    changes = []
    plot.on_change(changes.append)

    plot.point_coordinates = {"P": [2.5, -1.25]}

    moved = plot["P"]
    assert moved == cga.up(2.5, -1.25).named(p.name)
    assert cga.down(moved) == cga.euclidean_vector((2.5, -1.25))
    assert moved.name == p.name
    assert len(changes) == 1
    assert changes[0].key == "P"
    assert changes[0].index is None
    assert changes[0].previous == p
    assert changes[0].value == moved
    assert changes[0].coordinates == pytest.approx((2.5, -1.25))


def test_dependent_line_and_circle_are_recomputed_from_moved_points(cga: ConformalModel) -> None:
    p, q, r, *_ = _objects(cga)
    plot = CGA2DPlot(cga)
    plot.add_point("P", p, draggable=True)
    plot.add_point("Q", q, draggable=True)
    plot.add_point("R", r, draggable=True)
    plot.add_line("L", through=("P", "Q"))
    plot.add_circle("C", through=("P", "Q", "R"))

    plot.set_point("P", (2.0, 2.0))

    line = plot["L"]
    circle = plot["C"]
    for key in ("P", "Q"):
        assert np.allclose(outer_product(plot[key], line).data, 0.0)
    for key in ("P", "Q", "R"):
        assert np.allclose(outer_product(plot[key], circle).data, 0.0)


def test_display_is_reactive_anywidget_with_indexed_current_values(cga: ConformalModel) -> None:
    p, _, _, line, circle = _objects(cga)
    changes = []
    view = viz.display(
        [p, line, circle],
        model=cga,
        colors=["tomato", "royalblue"],
        on_change=changes.append,
    )

    assert view[0] == p
    assert view[:] == (p, line, circle)
    assert viz.value(view, slice(1, None)) == (line, circle)
    assert viz.values(view) == (p, line, circle)
    assert [item["label"] for item in view.scene] == ["P", "L", "C"]
    assert [item["color"] for item in view.scene] == ["tomato", "royalblue", "tomato"]
    assert [item["draggable"] for item in view.scene] == [True, False, False]

    viz.set_point(view, 0, (-3.0, 0.5))
    assert viz.value(view, 0) == cga.up(-3.0, 0.5).named(p.name)
    current_point, current_line, current_circle = view[:]
    assert current_point == viz.value(view, 0)
    assert (current_line, current_circle) == (line, circle)
    assert changes[-1].index == 0
    assert changes[-1].value == view[0]


def test_mutable_multivector_is_a_marimo_state_and_ordinary_algebra_value(
    cga: ConformalModel,
) -> None:
    p, q, r, *_ = _objects(cga)

    P = viz.mutable(p)
    Q = viz.mutable(q)
    R = viz.mutable(r)
    same_snapshot = viz.mutable(p)
    C = P ^ Q ^ R

    assert isinstance(P, Multivector)
    assert isinstance(P, State)
    assert viz.mutable(P) is P
    assert P == P
    assert P != same_snapshot
    assert P != p
    assert p != P
    assert len({P: "first", same_snapshot: "second"}) == 2
    assert {P: "registered"}[P] == "registered"
    assert P() is P
    assert P.snapshot() == p
    assert C == outer_product(p, q, r)
    assert cga.down(P) == cga.down(p)


def test_mutable_multivector_replacement_notifies_once_and_guards_noops(
    cga: ConformalModel,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    p, *_ = _objects(cga)
    P = viz.mutable(p)
    updates = []
    registered = {P: "registered"}
    original_hash = hash(P)
    context = type("Context", (), {"register_state_update": updates.append})()
    monkeypatch.setattr(marimo_state, "get_context", lambda: context)

    P.set(p)
    assert updates == []

    moved = cga.up(2.5, -1.25).named("P")
    P.set(moved)

    assert updates == [P]
    assert hash(P) == original_hash
    assert registered[P] == "registered"
    assert P.snapshot() == moved
    assert cga.down(P) == cga.euclidean_vector((2.5, -1.25))


def test_mutable_multivector_rejects_invalid_replacements(cga: ConformalModel) -> None:
    p, *_ = _objects(cga)
    P = viz.mutable(p)

    with pytest.raises(TypeError, match="mutable.*requires a galaga Multivector"):
        viz.mutable(object())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="must be galaga Multivectors"):
        P.set(object())  # type: ignore[arg-type]

    other_cga = ConformalModel(Algebra(config=p_cga(spatial_dim=2)))
    with pytest.raises(ValueError, match="same algebra"):
        P.set(other_cga.up(1.0, 2.0))


def test_display_updates_mutable_inputs_and_appends_immutable_results(cga: ConformalModel) -> None:
    p, q, r, _, circle = _objects(cga)
    P = viz.mutable(p)
    Q = viz.mutable(q)
    R = viz.mutable(r)
    view = viz.display([P, Q, R], immutable=[circle], model=cga)

    assert [item["draggable"] for item in view.scene] == [True, True, True, False]
    assert view.scene[3]["line_style"] == "dotted"

    viz.set_point(view, 0, (2.0, 2.0))

    assert P.snapshot() == cga.up(2.0, 2.0).named("P")
    assert Q.snapshot() == q
    assert R.snapshot() == r
    assert view[3] == circle


def test_cga2d_instance_owns_reactive_coordinates_and_one_widget(
    cga: ConformalModel,
) -> None:
    scene = viz.CGA2D(cga, colors=["tomato", "royalblue"])
    original_view = scene.view
    original_widget = scene.widget

    assert isinstance(scene, mo.ui.anywidget)
    assert original_view is scene
    assert scene.values == ()

    px, py = scene.coordinates("P", default=(1.0, 0.0))
    qx, qy = scene.coordinates("Q", default=(0.0, 1.0))
    rx, ry = scene.coordinates("R", default=(-1.0, 0.0))
    P = cga.up(px, py).named("P")
    Q = cga.up(qx, qy).named("Q")
    R = cga.up(rx, ry).named("R")
    C = (P ^ Q ^ R).named("C")

    assert not isinstance(P, State)
    assert scene.coordinates("P", default=(99.0, 99.0)) == (1.0, 0.0)

    display_result = scene.display([P, Q, R], immutable=[C])

    assert display_result is None
    assert scene.view is original_view
    assert scene.widget is original_widget
    assert tuple(scene.widget.objects) == ("P", "Q", "R", "C")
    assert scene.values == (P, Q, R, C)
    assert [item["color"] for item in scene.widget.scene] == [
        "tomato",
        "royalblue",
        "tomato",
        "royalblue",
    ]
    assert scene.widget.scene[3]["line_style"] == "dotted"

    scene.set_point("P", (2.0, 2.0))
    moved_x, moved_y = scene.coordinates("P")
    moved_P = cga.up(moved_x, moved_y).named("P")
    moved_C = (moved_P ^ Q ^ R).named("C")
    scene.display([moved_P, Q, R], immutable=[moved_C])

    assert scene.view is original_view
    assert scene.widget is original_widget
    assert scene[0] == cga.up(2.0, 2.0).named("P")
    assert scene[3] == moved_C


def test_cga2d_displays_one_point_after_its_coordinates_exist(cga: ConformalModel) -> None:
    scene = viz.CGA2D(cga)
    px, py = scene.coordinates("P", default=(1.0, 2.0))
    point = cga.up(px, py).named("P")

    scene.display([point])

    assert scene.widget.scene == [
        {
            "id": "P",
            "kind": "point",
            "label": "P",
            "color": DEFAULT_COLOR_CYCLE[0],
            "draggable": True,
            "line_style": "solid",
            "x": 1.0,
            "y": 2.0,
        }
    ]


def test_delayed_display_snapshot_cannot_rewind_widget_owned_coordinates(
    cga: ConformalModel,
) -> None:
    p, q, r, _, _ = _objects(cga)
    scene = viz.CGA2D(cga)
    initial_circle = (p ^ q ^ r).named("C")
    scene.display([p, q, r], immutable=[initial_circle])

    scene.set_point("P", (3.0, 2.0))
    stale_p = cga.up(2.0, 1.0).named("P")
    stale_circle = (stale_p ^ q ^ r).named("C")
    scene.display([stale_p, q, r], immutable=[stale_circle])

    assert scene.coordinates("P") == (3.0, 2.0)
    assert scene["P"] == cga.up(3.0, 2.0).named("P")
    assert scene["C"] == stale_circle


def test_lower_level_update_can_still_replace_point_coordinates(cga: ConformalModel) -> None:
    p, q, *_ = _objects(cga)
    view = viz.display([p, q], model=cga)
    replacement = cga.up(3.0, 2.0).named("P")

    viz.update(view, [replacement, q])

    assert view.point_coordinates["0"] == [3.0, 2.0]
    assert view[0] == replacement


@pytest.mark.parametrize(
    ("name", "default", "error"),
    [
        ("", (0.0, 0.0), ValueError),
        ("P", (0.0,), ValueError),
        ("P", (0.0, object()), TypeError),
        ("P", (0.0, np.inf), ValueError),
    ],
)
def test_cga2d_coordinates_validate_on_demand_state(
    cga: ConformalModel,
    name: str,
    default: object,
    error: type[Exception],
) -> None:
    scene = viz.CGA2D(cga)

    with pytest.raises(error):
        scene.coordinates(name, default=default)  # type: ignore[arg-type]


@pytest.mark.parametrize("default", ["0, 0", object()])
def test_cga2d_coordinates_reject_non_coordinate_iterables(
    cga: ConformalModel,
    default: object,
) -> None:
    scene = viz.CGA2D(cga)

    with pytest.raises(TypeError, match="real x and y coordinates"):
        scene.coordinates("P", default=default)  # type: ignore[arg-type]

    with pytest.raises(TypeError, match="coordinate names must be strings"):
        scene.coordinates(1)  # type: ignore[arg-type]


def test_cga2d_named_scene_rejects_ambiguous_object_names(cga: ConformalModel) -> None:
    p, q, *_ = _objects(cga)
    scene = viz.CGA2D(cga)

    with pytest.raises(ValueError, match="names must be distinct"):
        scene.display([p.named("P"), q.named("P")])


def test_display_read_only_disables_selected_point_dragging(cga: ConformalModel) -> None:
    p, q, _, _, circle = _objects(cga)

    view = viz.display([p, q, circle], model=cga, read_only=[1, 2])

    assert [item["draggable"] for item in view.scene] == [True, False, False]
    assert view.scene[2]["line_style"] == "dotted"


def test_display_styles_immutable_dipole_as_one_dotted_object(cga: ConformalModel) -> None:
    circle_a = cga.dual(cga.round_point(-1.0, 0.0, radius_squared=-4.0))
    circle_b = cga.dual(cga.round_point(1.0, 0.0, radius_squared=-4.0))
    dipole = meet(circle_a, circle_b).named("D")

    view = viz.display([], immutable=[dipole], model=cga, colors=["#7C3AED"])

    assert view[0] == dipole
    assert view.scene[0]["kind"] == "dipole"
    assert view.scene[0]["draggable"] is False
    assert view.scene[0]["line_style"] == "dotted"
    assert view.scene[0]["color"] == "#7C3AED"


def test_reactive_values_can_update_an_existing_persistent_display(cga: ConformalModel) -> None:
    p, q, r, _, circle = _objects(cga)
    changes = []
    value_snapshots = []
    view = viz.display(
        [p, q, r, circle],
        model=cga,
        read_only=[3],
        on_change=changes.append,
        on_values=value_snapshots.append,
    )

    viz.set_point(view, 0, (2.0, 2.0))
    P, Q, R = view[:3]
    C = outer_product(P, Q, R).named("C")
    scene_before_update = tuple(view.scene)

    assert view[3] == circle
    assert value_snapshots == [(P, Q, R, circle)]
    viz.update(view, [P, Q, R, C])

    assert view[:3] == (P, Q, R)
    assert view[3] == C
    assert view.scene[3]["line_style"] == "dotted"
    assert len(changes) == 1
    assert tuple(view.scene) != scene_before_update
    assert value_snapshots == [(P, Q, R, circle)]

    scene_after_update = tuple(view.scene)
    viz.update(view, [P, Q, R, C])
    assert tuple(view.scene) == scene_after_update
    assert len(changes) == 1


def test_update_validates_the_persistent_display_contract(cga: ConformalModel) -> None:
    p, q, *_ = _objects(cga)
    view = viz.display([p, q], model=cga)

    with pytest.raises(ValueError, match="one current value per plotted object"):
        viz.update(view, [p])
    with pytest.raises(ValueError, match="cannot replace a point with a line"):
        line = outer_product(p, q, cga.infinity)
        viz.update(view, [line, q])

    other_cga = ConformalModel(Algebra(config=p_cga(spatial_dim=2)))
    with pytest.raises(ValueError, match="plot's conformal algebra"):
        viz.update(view, [other_cga.up(0.0, 0.0), q])


def test_display_recomputes_dotted_circle_declared_through_points(cga: ConformalModel) -> None:
    p, q, r, _, circle = _objects(cga)
    view = viz.display(
        [p, q, r, circle],
        model=cga,
        read_only=[3],
        through={3: (0, 1, 2)},
    )

    assert [item["draggable"] for item in view.scene] == [True, True, True, False]
    assert view.scene[3]["line_style"] == "dotted"
    assert view[3] == circle

    viz.set_point(view, 0, (2.0, 2.0))

    expected = outer_product(view[0], view[1], view[2]).named(circle.name)
    assert view[3] == expected
    for index in range(3):
        assert np.allclose(outer_product(view[index], view[3]).data, 0.0)


def test_display_validates_initial_geometry_declared_through_points(cga: ConformalModel) -> None:
    p, q, r, _, circle = _objects(cga)
    other = outer_product(p, q, cga.up(0.0, -2.0))

    scaled = viz.display([p, q, r, -3.0 * circle], model=cga, through={3: (0, 1, 2)})
    assert np.allclose(outer_product(scaled[0], scaled[3]).data, 0.0)

    with pytest.raises(ValueError, match="not projectively equivalent"):
        viz.display([p, q, r, other], model=cga, through={3: (0, 1, 2)})


def test_display_rejects_invalid_through_dependencies(cga: ConformalModel) -> None:
    p, q, r, line, _ = _objects(cga)

    with pytest.raises(ValueError, match="must precede"):
        viz.display([line, p, q], model=cga, through={0: (1, 2)})
    with pytest.raises(ValueError, match="requires 2 defining points"):
        viz.display([p, q, r, line], model=cga, through={3: (0, 1, 2)})
    with pytest.raises(ValueError, match="must be direct lines or circles"):
        viz.display([p, q], model=cga, through={1: (0,)})


def test_display_can_infer_the_model_from_a_nonempty_value_sequence(cga: ConformalModel) -> None:
    p, *_ = _objects(cga)
    view = viz.display([p])

    assert view.model.algebra is cga.algebra
    assert view[0] == p


def test_display_labels_can_use_defaults_or_hide_individual_labels(cga: ConformalModel) -> None:
    p, _, _, line, _ = _objects(cga)
    view = viz.display([p, line], model=cga, labels=[None, ""])

    assert [item["label"] for item in view.scene] == ["P", ""]


def test_plot_rejects_non_planar_model() -> None:
    model = ConformalModel(Algebra(config=p_cga(spatial_dim=3)))

    with pytest.raises(ValueError, match="spatial_dim == 2"):
        CGA2DPlot(model)


@pytest.mark.parametrize(
    ("kwargs", "error", "message"),
    [
        ({"atol": True}, TypeError, "atol must be a finite real number"),
        ({"atol": np.inf}, TypeError, "atol must be a finite real number"),
        ({"atol": -1.0}, ValueError, "atol must be nonnegative"),
        ({"xlim": (0.0,)}, ValueError, "xlim must contain exactly two bounds"),
        ({"xlim": (False, 1.0)}, TypeError, "xlim bounds must be real numbers"),
        ({"xlim": (0.0, np.inf)}, ValueError, "xlim bounds must be finite"),
        ({"xlim": (1.0, 1.0)}, ValueError, "xlim lower bound must be less"),
        ({"width": 0}, ValueError, "width must be a positive integer"),
        ({"height": True}, ValueError, "height must be a positive integer"),
        ({"grid": 1}, TypeError, "grid must be a boolean"),
    ],
)
def test_plot_constructor_validates_numeric_and_view_configuration(
    cga: ConformalModel,
    kwargs: dict[str, object],
    error: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error, match=message):
        CGA2DPlot(cga, **kwargs)


def test_plot_constructor_requires_a_conformal_model() -> None:
    with pytest.raises(TypeError, match="model must be a galaga ConformalModel"):
        CGA2DPlot(object())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="model must be a galaga ConformalModel"):
        viz.CGA2D(object())  # type: ignore[arg-type]


def test_plot_index_lookup_and_callback_registration_validate_inputs(cga: ConformalModel) -> None:
    p, q, *_ = _objects(cga)
    line = outer_product(p, q, cga.infinity)
    plot = CGA2DPlot(cga).add_point("P", p).add_line("L", line)

    assert plot.objects["P"] == p
    assert plot[-1] == line
    with pytest.raises(IndexError, match="plot object index out of range"):
        _ = plot[2]
    with pytest.raises(TypeError, match="integers, slices, or strings"):
        _ = plot[True]
    with pytest.raises(KeyError, match="not a plotted point"):
        plot.point("L")
    with pytest.raises(KeyError, match="unknown plotted object"):
        plot.geometry("missing")

    with pytest.raises(TypeError, match="change handler must be callable"):
        plot.on_change(None)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="values handler must be callable"):
        plot.on_values(None)  # type: ignore[arg-type]

    def change_handler(_change):
        return None

    def values_handler(_values):
        return None

    assert plot.on_change(change_handler) is change_handler
    assert plot.on_values(values_handler) is values_handler
    plot.off_change(change_handler)
    plot.off_values(values_handler)
    with pytest.raises(ValueError, match="change handler is not registered"):
        plot.off_change(change_handler)
    with pytest.raises(ValueError, match="values handler is not registered"):
        plot.off_values(values_handler)


@pytest.mark.parametrize(
    ("coordinates", "error", "message"),
    [
        ("1, 2", TypeError, "coordinates must be real numbers"),
        (object(), TypeError, "coordinates must be an iterable"),
        ((1.0,), ValueError, "requires exactly two coordinates"),
        ((True, 1.0), TypeError, "coordinates must be real numbers"),
        ((1.0, np.nan), ValueError, "coordinates must be finite"),
    ],
)
def test_add_point_validates_coordinate_sequences(
    cga: ConformalModel,
    coordinates: object,
    error: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error, match=message):
        CGA2DPlot(cga).add_point("P", coordinates)  # type: ignore[arg-type]


def test_plot_add_methods_validate_keys_styles_and_geometry_sources(cga: ConformalModel) -> None:
    p, q, r, line, circle = _objects(cga)
    plot = CGA2DPlot(cga).add_point("P", (1.0, 0.0), draggable=True)

    assert plot["P"] == p
    with pytest.raises(TypeError, match="plot object names must be strings"):
        plot.add_point(1, p)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="must not be empty"):
        plot.add_point(" ", p)
    with pytest.raises(ValueError, match="already exists"):
        plot.add_point("P", p)
    with pytest.raises(TypeError, match="plot colors must be nonempty"):
        plot.add_point("bad-color", p, color="")
    with pytest.raises(TypeError, match="plot labels must be strings"):
        plot.add_point("bad-label", p, label=1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="kind must be"):
        plot.add("bad-kind", p, kind="plane")  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="only points can be draggable"):
        plot.add("moving-line", line, draggable=True)

    plot.add_point("Q", q).add_point("R", r).add_line("L", line)
    with pytest.raises(TypeError, match="requires exactly one"):
        plot.add_line("no-source")
    with pytest.raises(TypeError, match="requires exactly one"):
        plot.add_line("two-sources", line, through=("P", "Q"))
    with pytest.raises(ValueError, match="requires 2 defining points"):
        plot.add_line("short-line", through=("P",))
    with pytest.raises(ValueError, match="defining point names must be distinct"):
        plot.add_line("duplicate-line", through=("P", "P"))
    with pytest.raises(KeyError, match="not a plotted point"):
        plot.add_line("missing-line", through=("P", "missing"))
    with pytest.raises(KeyError, match="not a plotted point"):
        plot.add_line("nonpoint-line", through=("P", "L"))
    with pytest.raises(ValueError, match="line_style must be"):
        plot.add_circle("bad-style", circle, line_style="double")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="generated geometry names"):
        plot.add_circle("bad-name", circle, name="C")  # type: ignore[arg-type]


def test_plot_rejects_values_with_the_wrong_geometric_kind(cga: ConformalModel) -> None:
    p, q, _, line, circle = _objects(cga)
    plot = CGA2DPlot(cga)

    with pytest.raises(TypeError, match="plotted values must be galaga Multivectors"):
        plot.kind(object())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="supports grade-1 points"):
        plot.add("scalar", cga.algebra.scalar(1.0))
    with pytest.raises(ValueError, match="must have grade 1"):
        plot.add_point("not-point", line)
    with pytest.raises(ValueError, match="zero signed squared radius"):
        plot.add_point("round-point", cga.round_point(0.0, 0.0, radius_squared=1.0))
    with pytest.raises(TypeError, match="dipole value must be"):
        plot.add_dipole("not-value", object())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="dipole must have grade 2"):
        plot.add_dipole("not-dipole", line)
    with pytest.raises(ValueError, match="dipole must not contain infinity"):
        plot.add_dipole("flat-point", outer_product(p, cga.infinity))
    with pytest.raises(ValueError, match="line must have grade 3"):
        plot.add_line("not-line", p)
    with pytest.raises(TypeError, match="line value must be a galaga Multivector"):
        plot.add_line("not-a-value", object())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="line must contain infinity"):
        plot.add_line("circle-as-line", circle)
    with pytest.raises(ValueError, match="circle must have grade 3"):
        plot.add_circle("not-circle", p)
    with pytest.raises(ValueError, match="circle must not contain infinity"):
        plot.add_circle("line-as-circle", line)

    imaginary_circle = cga.dual(cga.round_point(0.0, 0.0, radius_squared=1.0))
    with pytest.raises(ValueError, match="imaginary conformal circle"):
        plot.add_circle("imaginary", imaginary_circle)

    other_cga = ConformalModel(Algebra(config=p_cga(spatial_dim=2)))
    with pytest.raises(ValueError, match="conformal model's algebra"):
        viz.display([other_cga.up(0.0, 0.0)], model=cga)


def test_plot_set_and_remove_preserve_scene_structure(cga: ConformalModel) -> None:
    p, q, r, line, circle = _objects(cga)
    plot = CGA2DPlot(cga)
    plot.add_point("P", p).add_point("Q", q).add_point("R", r)
    plot.add_line("L", through=("P", "Q")).add_circle("C", circle)

    original_scene = tuple(plot.scene)
    plot.set_point("P", (1.0, 0.0))
    assert tuple(plot.scene) == original_scene
    with pytest.raises(KeyError, match="not a plotted point"):
        plot.set_point("L", (0.0, 0.0))
    with pytest.raises(KeyError, match="unknown plotted object"):
        plot.set_value("missing", p)
    with pytest.raises(TypeError, match="plot values must be"):
        plot.set_value("P", object())  # type: ignore[arg-type]

    other_cga = ConformalModel(Algebra(config=p_cga(spatial_dim=2)))
    with pytest.raises(ValueError, match="plot's conformal algebra"):
        plot.set_value("P", other_cga.up(0.0, 0.0))
    with pytest.raises(ValueError, match="cannot replace a point with a line"):
        plot.set_value("P", line)

    plot.set_value("P", p.named("renamed"), replace_point_coordinates=False)
    assert str(plot["P"].name) == "renamed"
    plot.set_value("C", circle)

    with pytest.raises(ValueError, match="it defines L"):
        plot.remove("P")
    plot.remove("L")
    plot.remove("P")
    assert "L" not in plot.objects
    assert "P" not in plot.objects
    assert "P" not in plot.point_coordinates
    with pytest.raises(KeyError, match="unknown plotted object"):
        plot.remove("missing")


@pytest.mark.parametrize("colors", [[], "red", [""]])
def test_display_rejects_invalid_color_palettes(cga: ConformalModel, colors: object) -> None:
    p, *_ = _objects(cga)

    with pytest.raises((TypeError, ValueError)):
        viz.display([p], model=cga, colors=colors)


@pytest.mark.parametrize(
    ("objects", "error", "message"),
    [
        ("P", TypeError, "must be a sequence"),
        (object(), TypeError, "must be a sequence"),
        ([object()], TypeError, "every objects value"),
    ],
)
def test_display_validates_object_sequences(
    cga: ConformalModel,
    objects: object,
    error: type[Exception],
    message: str,
) -> None:
    with pytest.raises(error, match=message):
        viz.display(objects, model=cga)  # type: ignore[arg-type]


def test_display_and_widget_helpers_validate_public_contract(cga: ConformalModel) -> None:
    p, q, *_ = _objects(cga)

    with pytest.raises(ValueError, match="model is required"):
        viz.display()
    with pytest.raises(TypeError, match="model must be a galaga ConformalModel"):
        viz.display([p], model=object())  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="draggable must be a boolean"):
        viz.display([p], model=cga, draggable=1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="require initial display objects"):
        viz.display(model=cga, labels=[])
    with pytest.raises(ValueError, match="require initial display objects"):
        viz.display(model=cga, read_only=[0])
    with pytest.raises(TypeError, match="labels must be a sequence"):
        viz.display([p], model=cga, labels="P")
    with pytest.raises(ValueError, match="one entry per plotted object"):
        viz.display([p], model=cga, labels=[])
    with pytest.raises(TypeError, match="only strings or None"):
        viz.display([p], model=cga, labels=[1])  # type: ignore[list-item]
    with pytest.raises(TypeError, match="sequence of object indices"):
        viz.display([p], model=cga, read_only="0")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="only integer object indices"):
        viz.display([p], model=cga, read_only=[True])
    with pytest.raises(IndexError, match="outside the display"):
        viz.display([p], model=cga, read_only=[1])
    with pytest.raises(ValueError, match="indices must be distinct"):
        viz.display([p, q], model=cga, read_only=[0, 0])
    with pytest.raises(TypeError, match="through must map"):
        viz.display([p], model=cga, through=[])  # type: ignore[arg-type]

    raw_plot = CGA2DPlot(cga).add_point("P", p)
    assert viz.widget(raw_plot) is raw_plot
    with pytest.raises(TypeError, match="view must be a CGA2D visualization"):
        viz.widget(object())
    with pytest.raises(TypeError, match="indices must be integers or strings"):
        viz.set_point(raw_plot, True, (0.0, 0.0))
    with pytest.raises(IndexError, match="index out of range"):
        viz.set_point(raw_plot, 1, (0.0, 0.0))


def test_display_public_callbacks_and_cga2d_factory_delegate_to_the_plot(
    cga: ConformalModel,
) -> None:
    p, q, *_ = _objects(cga)
    plot = cga2d(cga, {"P": p})
    assert plot["P"] == p

    def change_handler(_change):
        return None

    def values_handler(_values):
        return None

    scene = viz.CGA2D(cga)
    assert scene.on_change(change_handler) is change_handler
    assert scene.on_values(values_handler) is values_handler
    assert viz.on_change(scene, change_handler) is change_handler
    assert viz.on_values(scene, values_handler) is values_handler

    immutable_line = outer_product(p, q, cga.infinity)
    view = viz.display([], immutable=[immutable_line], model=cga)
    assert view.scene[0]["kind"] == "line"
    assert view.scene[0]["line_style"] == "dotted"


def test_unnamed_point_changes_emit_unnamed_values(cga: ConformalModel) -> None:
    plot = CGA2DPlot(cga).add_point("P", (1.0, 0.0), draggable=True)
    changes = []
    plot.on_change(changes.append)

    plot.set_point("P", (2.0, 1.0))

    assert changes[-1].previous.name is None
    assert changes[-1].value.name is None


def test_update_can_initialize_an_empty_view_and_reject_structural_changes(cga: ConformalModel) -> None:
    p, q, *_ = _objects(cga)
    scene = viz.CGA2D(cga)

    viz.update(scene, [p, q])
    assert scene.values == (p, q)

    with pytest.raises(ValueError, match="names and order must preserve"):
        scene.display([q.named("Q"), p.named("P")])
    with pytest.raises(ValueError, match="preserve the initialized display structure"):
        scene.display(
            [cga.up(1.0, 0.0)],
            immutable=[cga.up(0.0, 1.0)],
        )


def test_browser_drag_synchronizes_semantic_point_coordinates() -> None:
    javascript = Path(__file__).parents[1] / "galaga_anywidget" / "static" / "cga2d.js"
    source = javascript.read_text()

    assert 'model.set("point_coordinates", next)' in source
    assert "model.save_changes()" in source
    assert "POINT_SYNC_INTERVAL_MS = 33" in source
    assert "samePointCoordinates(current[id], x, y)" in source
    assert "POINT_EQUALITY_TOLERANCE = 1e-12" in source
    assert "syncPointToPython(released.id, released.x, released.y, true)" in source
    assert "sceneReachedReleasedPoint" in source


def test_python_derived_geometry_repaints_during_active_drag() -> None:
    javascript = Path(__file__).parents[1] / "galaga_anywidget" / "static" / "cga2d.js"
    source = javascript.read_text()

    assert "function updateDerivedGeometryDuringDrag()" in source
    assert "const rendered = renderedGeometry.get(item.id)" in source
    assert "if (activeDrag) {\n      updateDerivedGeometryDuringDrag();\n      return;\n    }" in source
    assert 'model.on("change:scene", redraw)' in source


def test_widget_disables_browser_text_selection() -> None:
    stylesheet = Path(__file__).parents[1] / "galaga_anywidget" / "static" / "cga2d.css"
    source = stylesheet.read_text()

    root_rule = source.split("}", 1)[0]
    assert "user-select: none" in root_rule
    assert "-webkit-user-select: none" in root_rule
    assert ".galaga-cga2d-widget *" in source


def test_widget_supports_dotted_derived_geometry() -> None:
    static = Path(__file__).parents[1] / "galaga_anywidget" / "static"

    assert 'item.line_style ?? "solid"' in (static / "cga2d.js").read_text()
    assert "updateDipoleGeometry(rendered, item, transform)" in (static / "cga2d.js").read_text()
    assert ".galaga-cga2d-dipole-point" in (static / "cga2d.css").read_text()
    assert ".galaga-cga2d-dotted" in (static / "cga2d.css").read_text()
