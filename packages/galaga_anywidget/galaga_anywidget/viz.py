"""Marimo-native visualization entry points."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from numbers import Real

import marimo as mo
import numpy as np
from marimo._runtime.state import State

from galaga import Multivector
from galaga.cga import ConformalModel

from .cga2d import CGA2DChange, CGA2DPlot


class ReactiveMultivector(Multivector, State[Multivector]):
    """A stable Marimo state handle with the current value of a multivector.

    Galaga multivectors remain immutable snapshots.  This integration-owned
    subtype replaces the snapshot held by one stable Python object and asks
    Marimo to rerun cells that reference that object.  Algebra operations see
    it as an ordinary :class:`galaga.Multivector`.  Equality and hashing are
    identity-based because the value held by this object can change; compare
    :meth:`snapshot` results when value equality is required.
    """

    __hash__ = object.__hash__

    def __init__(self, value: Multivector) -> None:
        if not isinstance(value, Multivector):
            raise TypeError("mutable() requires a galaga Multivector")
        Multivector.__init__(
            self,
            value.algebra,
            value.numeric,
            name=value.name,
            expr=value.expr,
        )
        State.__init__(self, self)

    def set(self, value: Multivector) -> None:
        """Replace the current immutable snapshot and notify Marimo once."""
        if not isinstance(value, Multivector):
            raise TypeError("reactive multivector values must be galaga Multivectors")
        if value.algebra is not self.algebra:
            raise ValueError("a reactive replacement must belong to the same algebra")
        if self._same_value(value):
            return
        Multivector.__init__(
            self,
            value.algebra,
            value.numeric,
            name=value.name,
            expr=value.expr,
        )
        self._set_value(self)

    def snapshot(self) -> Multivector:
        """Return the current value as an ordinary immutable multivector."""
        return Multivector(
            self.algebra,
            self.numeric,
            name=self.name,
            expr=self.expr,
        )

    def __eq__(self, other: object) -> bool:
        return self is other

    def _same_value(self, value: Multivector) -> bool:
        return (
            value.algebra is self.algebra
            and np.array_equal(value.data, self.data)
            and value.name == self.name
            and value.expr == self.expr
        )


def mutable(value: Multivector) -> ReactiveMultivector:
    """Make one multivector a stable, directly reactive Marimo value."""
    if isinstance(value, ReactiveMultivector):
        return value
    return ReactiveMultivector(value)


class CGA2D(mo.ui.anywidget):
    """One persistent reactive view whose coordinates drive ordinary algebra.

    Construct this object in a cell that depends only on stable plot
    configuration, and render it from that cell. Downstream cells can read
    named coordinate pairs with :meth:`coordinates`, construct ordinary
    immutable multivectors from them, and pass the results to :meth:`display`.
    Browser drags change this UI element's synchronized coordinate state, so
    Marimo reruns those ordinary dependent cells. The display method updates
    the widget created by this object's constructor and never creates or
    returns another view.
    """

    def __init__(
        self,
        model: ConformalModel,
        *,
        colors: Sequence[str] | None = None,
        on_change: Callable[[CGA2DChange], None] | None = None,
        on_values: Callable[[tuple[Multivector, ...]], None] | None = None,
        xlim: Sequence[Real] = (-4.0, 4.0),
        ylim: Sequence[Real] = (-3.0, 3.0),
        width: int = 640,
        height: int = 420,
        grid: bool = True,
        atol: float = 1e-9,
    ) -> None:
        if not isinstance(model, ConformalModel):
            raise TypeError("model must be a galaga ConformalModel")
        plot = CGA2DPlot(
            model,
            xlim=xlim,
            ylim=ylim,
            width=width,
            height=height,
            grid=grid,
            atol=atol,
        )
        plot._viz_palette = _palette(colors)
        plot._viz_atol = float(atol)
        _bind_reactive_points(plot, (), keys=())
        if on_change is not None:
            plot.on_change(on_change)
        if on_values is not None:
            plot.on_values(on_values)
        super().__init__(plot)

    @property
    def view(self) -> CGA2D:
        """This visualization's single Marimo UI element."""
        return self

    @property
    def values(self) -> tuple[Multivector, ...]:
        """Current displayed multivectors in insertion order."""
        return self.widget.values

    def __getitem__(self, index: int | str | slice) -> Multivector | tuple[Multivector, ...]:
        """Return a current displayed value by index, slice, or object key."""
        return self.widget[index]

    def coordinates(
        self,
        name: str,
        *,
        default: Sequence[Real] = (0.0, 0.0),
    ) -> tuple[float, float]:
        """Return one reactive named point, creating its coordinates on demand.

        A cell that calls this method references this UI element in Marimo's
        normal dependency graph. Dragging the corresponding named point causes
        that cell to rerun. ``default`` is used only until the name first
        exists in synchronized widget state.
        """
        key = _coordinate_key(name)
        current = self.value.get("point_coordinates", {})
        if key not in current:
            coordinates = _coordinate_pair(default, name=f"default for {key!r}")
            updated = dict(self.widget.point_coordinates)
            updated[key] = list(coordinates)
            self.widget.point_coordinates = updated
            return coordinates
        return _coordinate_pair(current[key], name=f"coordinates for {key!r}")

    def display(
        self,
        objects: Sequence[Multivector],
        *,
        immutable: Sequence[Multivector] = (),
        labels: Sequence[str | None] | None = None,
        draggable: bool = True,
        read_only: Sequence[int] = (),
        through: Mapping[int, Sequence[int]] | None = None,
    ) -> None:
        """Synchronize current geometry without replacing the rendered view."""
        editable_values = _objects(objects)
        immutable_values = _objects(immutable, name="immutable")
        _update(
            self,
            editable_values,
            immutable_values,
            keys=_named_object_keys(editable_values + immutable_values),
            labels=labels,
            draggable=draggable,
            read_only=read_only,
            through=through,
        )

    def set_point(self, index: int | str, coordinates: Sequence[Real]) -> None:
        """Move one displayed point and synchronize all live browser views."""
        set_point(self, index, coordinates)

    def on_change(self, handler: Callable[[CGA2DChange], None]) -> Callable[[CGA2DChange], None]:
        """Register a callback for individual point changes."""
        return self.widget.on_change(handler)

    def on_values(
        self,
        handler: Callable[[tuple[Multivector, ...]], None],
    ) -> Callable[[tuple[Multivector, ...]], None]:
        """Register a callback for the complete current value tuple."""
        return self.widget.on_values(handler)


def display(
    objects: Sequence[Multivector] = (),
    *,
    immutable: Sequence[Multivector] = (),
    model: ConformalModel | None = None,
    colors: Sequence[str] | None = None,
    labels: Sequence[str | None] | None = None,
    draggable: bool = True,
    read_only: Sequence[int] = (),
    through: Mapping[int, Sequence[int]] | None = None,
    on_change: Callable[[CGA2DChange], None] | None = None,
    on_values: Callable[[tuple[Multivector, ...]], None] | None = None,
    xlim: Sequence[Real] = (-4.0, 4.0),
    ylim: Sequence[Real] = (-3.0, 3.0),
    width: int = 640,
    height: int = 420,
    grid: bool = True,
    atol: float = 1e-9,
) -> mo.ui.anywidget:
    """Display direct 2D CGA points, dipoles, lines, and circles.

    This is the compact one-cell convenience API. For a persistent two-way
    construction whose algebra remains ordinary Python, construct
    :class:`CGA2D`, read its named coordinates in a downstream cell, and use
    the instance's ``display()`` method to synchronize current results.

    Values are kept in insertion order. In a downstream Marimo cell,
    ``plot[0]`` returns the latest conformal multivector for the first object,
    while ``plot[:]`` returns every current value for direct tuple unpacking.
    Dragging a point causes that cell to rerun. Colors use the default palette
    in display order unless ``colors`` supplies a palette to cycle instead.

    ``immutable`` appends read-only result values after ``objects``. A value
    created with :func:`mutable` is updated directly when its displayed point
    moves, causing Marimo cells that reference that value to rerun.
    ``read_only`` contains additional indices that cannot be manipulated.
    ``through`` maps a derived line or circle index to the indices of two or
    three preceding points. Derived objects are recomputed when those points
    move and use a dotted stroke by default. ``on_values`` receives the full
    current multivector tuple after a point update and can be passed directly
    to a Marimo state setter.
    """
    editable_values = _objects(objects)
    immutable_values = _objects(immutable, name="immutable")
    values = editable_values + immutable_values
    selected_model = _model(model, values)
    if not isinstance(draggable, bool):
        raise TypeError("draggable must be a boolean")
    palette = _palette(colors)

    plot = CGA2DPlot(
        selected_model,
        xlim=xlim,
        ylim=ylim,
        width=width,
        height=height,
        grid=grid,
        atol=atol,
    )
    plot._viz_palette = palette
    plot._viz_atol = float(atol)
    if values:
        _populate(
            plot,
            editable_values,
            immutable_values,
            labels=labels,
            palette=palette,
            draggable=draggable,
            read_only=read_only,
            through=through,
            atol=float(atol),
        )
    elif labels is not None or read_only or through:
        raise ValueError("labels, read_only, and through require initial display objects")
    _bind_reactive_points(plot, editable_values)
    if on_change is not None:
        plot.on_change(on_change)
    if on_values is not None:
        plot.on_values(on_values)
    return mo.ui.anywidget(plot)


def _populate(
    plot: CGA2DPlot,
    editable_values: tuple[Multivector, ...],
    immutable_values: tuple[Multivector, ...],
    *,
    labels: Sequence[str | None] | None,
    palette: tuple[str, ...] | None,
    draggable: bool,
    read_only: Sequence[int],
    through: Mapping[int, Sequence[int]] | None,
    atol: float,
    keys: Sequence[str] | None = None,
) -> None:
    values = editable_values + immutable_values
    object_keys = tuple(str(index) for index in range(len(values))) if keys is None else tuple(keys)
    if len(object_keys) != len(values):
        raise ValueError("keys must contain one entry per plotted object")
    if len(set(object_keys)) != len(object_keys):
        raise ValueError("plotted object keys must be distinct")
    selected_labels = _labels(labels, len(values))
    read_only_indices = frozenset(
        (*_index_sequence(read_only, len(values), name="read_only"), *range(len(editable_values), len(values)))
    )
    through_indices = _through(through, len(values))
    selected_model = plot.model
    for index, value in enumerate(values):
        key = object_keys[index]
        if value.algebra is not selected_model.algebra:
            raise ValueError("every plotted multivector must belong to the conformal model's algebra")
        kind = plot.kind(value)
        requested_label = selected_labels[index] if selected_labels is not None else None
        label = _default_label(value, index) if requested_label is None else requested_label
        color = palette[index % len(palette)] if palette is not None else None
        dependencies = through_indices.get(index)
        if dependencies is None:
            if kind == "dipole" and index in read_only_indices:
                plot.add_dipole(
                    key,
                    value,
                    label=label,
                    color=color,
                    line_style="dotted",
                )
                continue
            if kind == "line" and index in read_only_indices:
                plot.add_line(
                    key,
                    value,
                    label=label,
                    color=color,
                    line_style="dotted",
                )
                continue
            if kind == "circle" and index in read_only_indices:
                plot.add_circle(
                    key,
                    value,
                    label=label,
                    color=color,
                    line_style="dotted",
                )
                continue
            plot.add(
                key,
                value,
                kind=kind,
                draggable=draggable and kind == "point" and index not in read_only_indices,
                label=label,
                color=color,
            )
            continue
        dependency_keys = tuple(object_keys[dependency] for dependency in dependencies)
        if kind == "line":
            plot.add_line(
                key,
                through=dependency_keys,
                label=label,
                color=color,
                name=value.name,
            )
        elif kind == "circle":
            plot.add_circle(
                key,
                through=dependency_keys,
                label=label,
                color=color,
                name=value.name,
            )
        else:
            raise ValueError("through targets must be direct lines or circles")
        if not _projectively_equal(value, plot[key], atol=float(atol)):
            raise ValueError(
                f"object at index {index} is not projectively equivalent to the geometry declared by through"
            )
    plot._viz_counts = (len(editable_values), len(immutable_values))


def _bind_reactive_points(
    plot: CGA2DPlot,
    values: tuple[Multivector, ...],
    *,
    keys: Sequence[str] | None = None,
) -> None:
    reactive_points = getattr(plot, "_viz_reactive_points", None)
    if reactive_points is None:
        reactive_points = {}
        plot._viz_reactive_points = reactive_points

        def _set_reactive_value(change: CGA2DChange) -> None:
            target = reactive_points.get(change.key)
            if target is not None:
                target.set(change.value)

        plot.on_change(_set_reactive_value)
    reactive_points.clear()
    object_keys = tuple(str(index) for index in range(len(values))) if keys is None else tuple(keys)
    reactive_points.update(
        {key: value for key, value in zip(object_keys, values, strict=True) if isinstance(value, ReactiveMultivector)}
    )


def value(
    view: object,
    index: int | str | slice,
) -> Multivector | tuple[Multivector, ...]:
    """Return current multivectors by index, slice, or name."""
    return widget(view)[index]


def values(view: object) -> tuple[Multivector, ...]:
    """Return all current multivectors from a display in insertion order."""
    return widget(view).values


def on_change(view: object, handler: Callable[[CGA2DChange], None]) -> Callable[[CGA2DChange], None]:
    """Register a point-change callback on a display or raw 2D widget."""
    return widget(view).on_change(handler)


def on_values(
    view: object,
    handler: Callable[[tuple[Multivector, ...]], None],
) -> Callable[[tuple[Multivector, ...]], None]:
    """Register a complete-values callback on a display or raw 2D widget."""
    return widget(view).on_values(handler)


def set_point(view: object, index: int | str, coordinates: Sequence[Real]) -> None:
    """Move a displayed point from Python and synchronize the browser view."""
    plot = widget(view)
    key = _key_at(plot, index)
    plot.set_point(key, coordinates)


def update(
    view: object,
    objects: Sequence[Multivector],
    *,
    immutable: Sequence[Multivector] | None = None,
    colors: Sequence[str] | None = None,
    labels: Sequence[str | None] | None = None,
    draggable: bool = True,
    read_only: Sequence[int] = (),
    through: Mapping[int, Sequence[int]] | None = None,
) -> None:
    """Initialize or update values in an existing persistent display."""
    editable_values = _objects(objects)
    immutable_values = () if immutable is None else _objects(immutable, name="immutable")
    _update(
        view,
        editable_values,
        immutable_values,
        keys=None,
        colors=colors,
        labels=labels,
        draggable=draggable,
        read_only=read_only,
        through=through,
        preserve_immutable=immutable is not None,
    )


def _update(
    view: object,
    editable_values: tuple[Multivector, ...],
    immutable_values: tuple[Multivector, ...],
    *,
    keys: Sequence[str] | None,
    colors: Sequence[str] | None = None,
    labels: Sequence[str | None] | None = None,
    draggable: bool = True,
    read_only: Sequence[int] = (),
    through: Mapping[int, Sequence[int]] | None = None,
    preserve_immutable: bool = True,
) -> None:
    plot = widget(view)
    selected_keys = None if keys is None else tuple(keys)
    existing_keys = tuple(plot.objects)
    if not existing_keys:
        palette = _palette(colors) if colors is not None else getattr(plot, "_viz_palette", None)
        _populate(
            plot,
            editable_values,
            immutable_values,
            labels=labels,
            palette=palette,
            draggable=draggable,
            read_only=read_only,
            through=through,
            atol=getattr(plot, "_viz_atol", 1e-9),
            keys=selected_keys,
        )
        editable_keys = None if selected_keys is None else selected_keys[: len(editable_values)]
        _bind_reactive_points(plot, editable_values, keys=editable_keys)
        return

    if selected_keys is not None and selected_keys != existing_keys:
        raise ValueError("display object names and order must preserve the initialized scene structure")
    if not preserve_immutable:
        replacements = editable_values
    else:
        expected_counts = getattr(plot, "_viz_counts", None)
        selected_counts = (len(editable_values), len(immutable_values))
        if expected_counts != selected_counts:
            raise ValueError("objects and immutable must preserve the initialized display structure")
        replacements = editable_values + immutable_values
        editable_keys = existing_keys[: len(editable_values)]
        _bind_reactive_points(plot, editable_values, keys=editable_keys)
    if len(replacements) != len(existing_keys):
        raise ValueError("objects must contain one current value per plotted object")
    coordinate_owned_count = len(editable_values) if selected_keys is not None else 0
    for index, (key, replacement) in enumerate(zip(existing_keys, replacements, strict=True)):
        plot.set_value(
            key,
            replacement,
            replace_point_coordinates=index >= coordinate_owned_count,
        )


def widget(view: object) -> CGA2DPlot:
    """Return the raw :class:`CGA2DPlot` behind a Marimo display."""
    if isinstance(view, CGA2DPlot):
        return view
    candidate = getattr(view, "widget", None)
    if isinstance(candidate, CGA2DPlot):
        return candidate
    raise TypeError("view must be a CGA2D visualization, plot, or Marimo AnyWidget element")


def _objects(
    objects: Sequence[Multivector],
    *,
    name: str = "objects",
) -> tuple[Multivector, ...]:
    if isinstance(objects, (str, bytes)):
        raise TypeError(f"{name} must be a sequence of galaga Multivectors")
    try:
        values = tuple(objects)
    except TypeError as error:
        raise TypeError(f"{name} must be a sequence of galaga Multivectors") from error
    if any(not isinstance(value, Multivector) for value in values):
        raise TypeError(f"every {name} value must be a galaga Multivector")
    return values


def _model(model: ConformalModel | None, values: tuple[Multivector, ...]) -> ConformalModel:
    if model is not None:
        if not isinstance(model, ConformalModel):
            raise TypeError("model must be a galaga ConformalModel")
        return model
    if not values:
        raise ValueError("model is required when displaying no objects")
    return ConformalModel(values[0].algebra, expr=values[0].expr is not None)


def _labels(labels: Sequence[str | None] | None, count: int) -> tuple[str | None, ...] | None:
    if labels is None:
        return None
    if isinstance(labels, (str, bytes)):
        raise TypeError("labels must be a sequence of strings or None")
    result = tuple(labels)
    if len(result) != count:
        raise ValueError("labels must contain one entry per plotted object")
    if any(label is not None and not isinstance(label, str) for label in result):
        raise TypeError("labels must contain only strings or None")
    return result


def _palette(colors: Sequence[str] | None) -> tuple[str, ...] | None:
    if colors is None:
        return None
    if isinstance(colors, (str, bytes)):
        raise TypeError("colors must be a sequence of CSS color strings")
    result = tuple(colors)
    if not result:
        raise ValueError("colors must contain at least one CSS color string")
    if any(not isinstance(color, str) or not color.strip() for color in result):
        raise TypeError("colors must contain nonempty CSS color strings")
    return tuple(color.strip() for color in result)


def _index_sequence(values: Sequence[int], count: int, *, name: str) -> tuple[int, ...]:
    if isinstance(values, (str, bytes)):
        raise TypeError(f"{name} must be a sequence of object indices")
    result = tuple(values)
    if any(not isinstance(index, int) or isinstance(index, bool) for index in result):
        raise TypeError(f"{name} must contain only integer object indices")
    if any(index < 0 or index >= count for index in result):
        raise IndexError(f"{name} contains an object index outside the display")
    if len(set(result)) != len(result):
        raise ValueError(f"{name} object indices must be distinct")
    return result


def _through(
    value: Mapping[int, Sequence[int]] | None,
    count: int,
) -> dict[int, tuple[int, ...]]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise TypeError("through must map object indices to defining point indices")
    result: dict[int, tuple[int, ...]] = {}
    for target, dependencies in value.items():
        target_index = _index_sequence((target,), count, name="through target")[0]
        dependency_indices = _index_sequence(dependencies, count, name=f"through[{target_index}]")
        if any(dependency >= target_index for dependency in dependency_indices):
            raise ValueError("through dependencies must precede their derived object in display order")
        result[target_index] = dependency_indices
    return result


def _projectively_equal(left: Multivector, right: Multivector, *, atol: float) -> bool:
    if left.algebra is not right.algebra:
        return False
    left_data = np.asarray(left.data, dtype=float)
    right_data = np.asarray(right.data, dtype=float)
    left_norm = float(np.linalg.norm(left_data))
    right_norm = float(np.linalg.norm(right_data))
    if left_norm <= atol or right_norm <= atol:
        return False
    normalized_left = left_data / left_norm
    normalized_right = right_data / right_norm
    tolerance = max(atol, 1e-9)
    return bool(
        np.allclose(normalized_left, normalized_right, rtol=1e-7, atol=tolerance)
        or np.allclose(normalized_left, -normalized_right, rtol=1e-7, atol=tolerance)
    )


def _default_label(value: Multivector, index: int) -> str:
    return str(value.name) if value.name is not None else str(index)


def _named_object_keys(values: tuple[Multivector, ...]) -> tuple[str, ...]:
    keys = tuple(
        str(index) if value.name is None else _coordinate_key(str(value.name)) for index, value in enumerate(values)
    )
    if len(set(keys)) != len(keys):
        raise ValueError("CGA2D display object names must be distinct")
    return keys


def _coordinate_key(value: str) -> str:
    if not isinstance(value, str):
        raise TypeError("coordinate names must be strings")
    key = value.strip()
    if not key:
        raise ValueError("coordinate names must not be empty")
    return key


def _coordinate_pair(value: object, *, name: str) -> tuple[float, float]:
    if isinstance(value, (str, bytes)):
        raise TypeError(f"{name} must contain real x and y coordinates")
    try:
        coordinates = tuple(value)  # type: ignore[arg-type]
    except TypeError as error:
        raise TypeError(f"{name} must contain real x and y coordinates") from error
    if len(coordinates) != 2:
        raise ValueError(f"{name} must contain exactly two coordinates")
    if any(not isinstance(coordinate, Real) or isinstance(coordinate, (bool, np.bool_)) for coordinate in coordinates):
        raise TypeError(f"{name} must contain real x and y coordinates")
    result = (float(coordinates[0]), float(coordinates[1]))
    if not all(np.isfinite(coordinate) for coordinate in result):
        raise ValueError(f"{name} coordinates must be finite")
    return result


def _key_at(plot: CGA2DPlot, index: int | str) -> str:
    if isinstance(index, str):
        return index
    if not isinstance(index, int) or isinstance(index, bool):
        raise TypeError("plot object indices must be integers or strings")
    try:
        return tuple(plot.objects)[index]
    except IndexError as error:
        raise IndexError("plot object index out of range") from error


__all__ = [
    "CGA2D",
    "ReactiveMultivector",
    "display",
    "mutable",
    "on_change",
    "on_values",
    "set_point",
    "update",
    "value",
    "values",
    "widget",
]
