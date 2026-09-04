"""Persistent, bidirectional 2D conformal-geometry plotting for notebooks."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass, replace
from math import isfinite, sqrt
from numbers import Real
from pathlib import Path
from types import MappingProxyType
from typing import Literal, cast

import anywidget
import numpy as np
import traitlets

from galaga import Multivector, Name, outer_product, scalar_product
from galaga.cga import ConformalModel

CGA2DKind = Literal["point", "dipole", "line", "circle"]
CGA2DLineStyle = Literal["solid", "dashed", "dotted"]
CGA2DChangeHandler = Callable[["CGA2DChange"], None]
CGA2DValuesHandler = Callable[[tuple[Multivector, ...]], None]

_ASSET_DIR = Path(__file__).parent / "static"
DEFAULT_COLOR_CYCLE = (
    "#0072B2",
    "#D55E00",
    "#009E73",
    "#CC79A7",
    "#E69F00",
    "#56B4E9",
    "#F0E442",
    "#111827",
)


@dataclass(frozen=True, slots=True)
class _GeometryDefinition:
    kind: CGA2DKind
    label: str
    color: str
    draggable: bool = False
    line_style: CGA2DLineStyle = "solid"
    through: tuple[str, ...] = ()
    value: Multivector | None = None
    name: Name | None = None


@dataclass(frozen=True, slots=True)
class CGA2DChange:
    """One browser- or Python-originated update to a plotted point."""

    key: str
    previous: Multivector
    value: Multivector
    coordinates: tuple[float, float]

    @property
    def index(self) -> int | None:
        """The list index used by the high-level CGA2D display API, if any."""
        try:
            return int(self.key)
        except ValueError:
            return None


class CGA2DPlot(anywidget.AnyWidget):
    """An SVG plot of direct 2D CGA objects with synchronized point state.

    The widget treats ``point_coordinates`` as the synchronized source of
    truth. Calling :meth:`point` maps the latest coordinates through the
    model's ``up`` operation, so dragging a point in the browser changes the
    conformal multivector returned by Python. Lines and circles declared with
    ``through=`` are recomputed from their defining points after each update.
    """

    _esm = _ASSET_DIR / "cga2d.js"
    _css = _ASSET_DIR / "cga2d.css"

    scene = traitlets.List(trait=traitlets.Dict(), default_value=[]).tag(sync=True)
    point_coordinates = traitlets.Dict(default_value={}).tag(sync=True)
    view = traitlets.Dict(default_value={}).tag(sync=True)
    error = traitlets.Unicode("").tag(sync=True)

    def __init__(
        self,
        model: ConformalModel,
        *,
        xlim: Sequence[Real] = (-4.0, 4.0),
        ylim: Sequence[Real] = (-3.0, 3.0),
        width: int = 640,
        height: int = 420,
        grid: bool = True,
        atol: float = 1e-9,
        **kwargs: object,
    ) -> None:
        if not isinstance(model, ConformalModel):
            raise TypeError("model must be a galaga ConformalModel")
        if model.spatial_dim != 2:
            raise ValueError("CGA2DPlot requires a ConformalModel with spatial_dim == 2")
        if not isinstance(atol, Real) or isinstance(atol, (bool, np.bool_)) or not isfinite(float(atol)):
            raise TypeError("atol must be a finite real number")
        if float(atol) < 0:
            raise ValueError("atol must be nonnegative")

        self._conformal_model = model
        self._definitions: dict[str, _GeometryDefinition] = {}
        self._change_handlers: list[CGA2DChangeHandler] = []
        self._values_handlers: list[CGA2DValuesHandler] = []
        self._atol = float(atol)
        normalized_view = _view_config(xlim=xlim, ylim=ylim, width=width, height=height, grid=grid)
        super().__init__(
            scene=[],
            point_coordinates={},
            view=normalized_view,
            **kwargs,
        )
        self.observe(self._coordinates_changed, names="point_coordinates")

    @property
    def model(self) -> ConformalModel:
        """The validated two-dimensional conformal model used by the plot."""
        return self._conformal_model

    @property
    def objects(self) -> Mapping[str, Multivector]:
        """A read-only snapshot of every plotted object's current value."""
        return MappingProxyType({key: self.geometry(key) for key in self._definitions})

    @property
    def values(self) -> tuple[Multivector, ...]:
        """Current values in insertion order, convenient for list displays."""
        return tuple(self.geometry(key) for key in self._definitions)

    def __getitem__(self, key: int | str | slice) -> Multivector | tuple[Multivector, ...]:
        """Return current values by insertion index, slice, or object name."""
        if isinstance(key, slice):
            return self.values[key]
        if isinstance(key, int) and not isinstance(key, bool):
            try:
                selected = tuple(self._definitions)[key]
            except IndexError as error:
                raise IndexError("plot object index out of range") from error
            return self.geometry(selected)
        if isinstance(key, str):
            return self.geometry(key)
        raise TypeError("plot object indices must be integers, slices, or strings")

    def kind(self, value: Multivector) -> CGA2DKind:
        """Classify a supported direct 2D conformal value."""
        return self._classify(value)

    def on_change(self, handler: CGA2DChangeHandler) -> CGA2DChangeHandler:
        """Call ``handler`` whenever synchronized point coordinates change."""
        if not callable(handler):
            raise TypeError("change handler must be callable")
        self._change_handlers.append(handler)
        return handler

    def off_change(self, handler: CGA2DChangeHandler) -> None:
        """Stop calling a handler previously registered with :meth:`on_change`."""
        try:
            self._change_handlers.remove(handler)
        except ValueError as error:
            raise ValueError("change handler is not registered") from error

    def on_values(self, handler: CGA2DValuesHandler) -> CGA2DValuesHandler:
        """Call ``handler`` with all current values after a point update."""
        if not callable(handler):
            raise TypeError("values handler must be callable")
        self._values_handlers.append(handler)
        return handler

    def off_values(self, handler: CGA2DValuesHandler) -> None:
        """Stop calling a handler previously registered with :meth:`on_values`."""
        try:
            self._values_handlers.remove(handler)
        except ValueError as error:
            raise ValueError("values handler is not registered") from error

    @traitlets.validate("point_coordinates")
    def _validate_point_coordinates(self, proposal: dict[str, object]) -> dict[str, list[float]]:
        value = proposal["value"]
        if not isinstance(value, dict):
            raise traitlets.TraitError("point_coordinates must be a mapping")
        normalized: dict[str, list[float]] = {}
        for key, coordinates in value.items():
            normalized_key = _object_key(key)
            normalized[normalized_key] = list(_coordinates2(coordinates, name=f"point {normalized_key!r}"))
        return normalized

    def add(
        self,
        key: str,
        value: Multivector,
        *,
        kind: CGA2DKind | Literal["auto"] = "auto",
        draggable: bool = False,
        label: str | None = None,
        color: str | None = None,
    ) -> CGA2DPlot:
        """Add a direct point, dipole, line, or circle, classifying it when requested."""
        selected = self._classify(value) if kind == "auto" else kind
        if selected == "point":
            return self.add_point(
                key,
                value,
                draggable=draggable,
                label=label,
                color=color,
            )
        if draggable:
            raise ValueError("only points can be draggable")
        if selected == "dipole":
            return self.add_dipole(key, value, label=label, color=color)
        if selected == "line":
            return self.add_line(key, value, label=label, color=color)
        if selected == "circle":
            return self.add_circle(key, value, label=label, color=color)
        raise ValueError("kind must be 'auto', 'point', 'dipole', 'line', or 'circle'")

    def add_point(
        self,
        key: str,
        value: Multivector | Sequence[Real],
        *,
        draggable: bool = False,
        label: str | None = None,
        color: str | None = None,
    ) -> CGA2DPlot:
        """Add a conformal point or two Cartesian coordinates."""
        normalized_key = self._new_key(key)
        if isinstance(value, Multivector):
            coordinates = self._point_scene(value)
            xy = (coordinates["x"], coordinates["y"])
        else:
            xy = _coordinates2(value, name=f"point {normalized_key!r}")
            self._point_scene(self._conformal_model.up(xy))

        self._definitions[normalized_key] = _GeometryDefinition(
            kind="point",
            label=_label(label, normalized_key),
            color=self._color(color),
            draggable=bool(draggable),
            name=value.name if isinstance(value, Multivector) else None,
        )
        coordinates_by_key = dict(self.point_coordinates)
        coordinates_by_key[normalized_key] = [float(xy[0]), float(xy[1])]
        coordinates_changed = coordinates_by_key != self.point_coordinates
        self.point_coordinates = coordinates_by_key
        if not coordinates_changed:
            self._rebuild_scene()
        return self

    def add_dipole(
        self,
        key: str,
        value: Multivector,
        *,
        label: str | None = None,
        color: str | None = None,
        line_style: CGA2DLineStyle | None = None,
    ) -> CGA2DPlot:
        """Add one direct point pair, rendering real factors when they exist."""
        normalized_key = self._new_key(key)
        self._dipole_scene(value)
        self._definitions[normalized_key] = _GeometryDefinition(
            kind="dipole",
            label=_label(label, normalized_key),
            color=self._color(color),
            line_style=_line_style(line_style, derived=False),
            value=value,
        )
        self._rebuild_scene()
        return self

    def add_line(
        self,
        key: str,
        value: Multivector | None = None,
        *,
        through: Sequence[str] | None = None,
        label: str | None = None,
        color: str | None = None,
        line_style: CGA2DLineStyle | None = None,
        name: Name | None = None,
    ) -> CGA2DPlot:
        """Add a direct line value or a line through two plotted points."""
        normalized_key = self._new_key(key)
        static_value, dependencies = self._geometry_source(
            value,
            through,
            kind="line",
            expected_points=2,
        )
        candidate = (
            static_value if static_value is not None else self._line_through(cast(tuple[str, str], dependencies))
        )
        self._line_scene(candidate)
        self._definitions[normalized_key] = _GeometryDefinition(
            kind="line",
            label=_label(label, normalized_key),
            color=self._color(color),
            line_style=_line_style(line_style, derived=bool(dependencies)),
            through=dependencies,
            value=static_value,
            name=_name(name),
        )
        self._rebuild_scene()
        return self

    def add_circle(
        self,
        key: str,
        value: Multivector | None = None,
        *,
        through: Sequence[str] | None = None,
        label: str | None = None,
        color: str | None = None,
        line_style: CGA2DLineStyle | None = None,
        name: Name | None = None,
    ) -> CGA2DPlot:
        """Add a direct circle value or a circle through three plotted points."""
        normalized_key = self._new_key(key)
        static_value, dependencies = self._geometry_source(
            value,
            through,
            kind="circle",
            expected_points=3,
        )
        candidate = (
            static_value if static_value is not None else self._circle_through(cast(tuple[str, str, str], dependencies))
        )
        self._circle_scene(candidate)
        self._definitions[normalized_key] = _GeometryDefinition(
            kind="circle",
            label=_label(label, normalized_key),
            color=self._color(color),
            line_style=_line_style(line_style, derived=bool(dependencies)),
            through=dependencies,
            value=static_value,
            name=_name(name),
        )
        self._rebuild_scene()
        return self

    def point(self, key: str) -> Multivector:
        """Return ``up(x, y)`` for a plotted point's latest synchronized state."""
        normalized_key = _object_key(key)
        definition = self._definitions.get(normalized_key)
        if definition is None or definition.kind != "point":
            raise KeyError(f"{normalized_key!r} is not a plotted point")
        x, y = _coordinates2(
            self.point_coordinates[normalized_key],
            name=f"point {normalized_key!r}",
        )
        point = self._conformal_model.up(x, y)
        return point.named(definition.name) if definition.name is not None else point

    def geometry(self, key: str) -> Multivector:
        """Return a plotted object's current conformal multivector."""
        normalized_key = _object_key(key)
        try:
            definition = self._definitions[normalized_key]
        except KeyError as error:
            raise KeyError(f"unknown plotted object {normalized_key!r}") from error
        if definition.kind == "point":
            return self.point(normalized_key)
        if definition.value is not None:
            result = definition.value
        elif definition.kind == "line":
            result = self._line_through(cast(tuple[str, str], definition.through))
        else:
            result = self._circle_through(cast(tuple[str, str, str], definition.through))
        return result.named(definition.name) if definition.name is not None else result

    def set_point(self, key: str, coordinates: Sequence[Real]) -> None:
        """Move a plotted point from Python and synchronize every widget view."""
        normalized_key = _object_key(key)
        definition = self._definitions.get(normalized_key)
        if definition is None or definition.kind != "point":
            raise KeyError(f"{normalized_key!r} is not a plotted point")
        x, y = _coordinates2(coordinates, name=f"point {normalized_key!r}")
        if tuple(self.point_coordinates[normalized_key]) == (x, y):
            return
        updated = dict(self.point_coordinates)
        updated[normalized_key] = [x, y]
        self.point_coordinates = updated

    def set_value(
        self,
        key: str,
        value: Multivector,
        *,
        replace_point_coordinates: bool = True,
    ) -> None:
        """Replace one current value without replacing the persistent widget.

        ``replace_point_coordinates=False`` validates an incoming point but
        retains the widget-owned coordinates. The high-level coordinate-first
        API uses this for editable points so a delayed reactive display pass
        cannot rewind a newer browser drag.
        """
        normalized_key = _object_key(key)
        try:
            definition = self._definitions[normalized_key]
        except KeyError as error:
            raise KeyError(f"unknown plotted object {normalized_key!r}") from error
        if not isinstance(value, Multivector):
            raise TypeError("plot values must be galaga Multivectors")
        if value.algebra is not self._conformal_model.algebra:
            raise ValueError("a replacement value must belong to the plot's conformal algebra")
        selected = self._classify(value)
        if selected != definition.kind:
            raise ValueError(f"cannot replace a {definition.kind} with a {selected} at {normalized_key!r}")

        if selected == "point":
            point_scene = self._point_scene(value)
            coordinates = (point_scene["x"], point_scene["y"])
            name_changed = definition.name != value.name
            if name_changed:
                self._definitions[normalized_key] = replace(definition, name=value.name)
            if replace_point_coordinates and tuple(self.point_coordinates[normalized_key]) != coordinates:
                updated = dict(self.point_coordinates)
                updated[normalized_key] = list(coordinates)
                self.point_coordinates = updated
            elif name_changed:
                self._rebuild_scene()
            return

        current = self.geometry(normalized_key)
        self._definitions[normalized_key] = replace(
            definition,
            through=(),
            value=value,
            name=None,
        )
        if not np.array_equal(current.data, value.data):
            self._rebuild_scene()

    def remove(self, key: str) -> None:
        """Remove an object, rejecting points still used by dependent geometry."""
        normalized_key = _object_key(key)
        if normalized_key not in self._definitions:
            raise KeyError(f"unknown plotted object {normalized_key!r}")
        users = [
            candidate for candidate, definition in self._definitions.items() if normalized_key in definition.through
        ]
        if users:
            raise ValueError(f"cannot remove {normalized_key!r}; it defines {', '.join(users)}")
        definition = self._definitions.pop(normalized_key)
        if definition.kind == "point":
            updated = dict(self.point_coordinates)
            updated.pop(normalized_key, None)
            self.point_coordinates = updated
        else:
            self._rebuild_scene()

    def _color(self, value: str | None) -> str:
        if value is None:
            return DEFAULT_COLOR_CYCLE[len(self._definitions) % len(DEFAULT_COLOR_CYCLE)]
        if not isinstance(value, str) or not value.strip():
            raise TypeError("plot colors must be nonempty CSS color strings")
        return value.strip()

    def _new_key(self, key: str) -> str:
        normalized = _object_key(key)
        if normalized in self._definitions:
            raise ValueError(f"a plotted object named {normalized!r} already exists")
        return normalized

    def _geometry_source(
        self,
        value: Multivector | None,
        through: Sequence[str] | None,
        *,
        kind: CGA2DKind,
        expected_points: int,
    ) -> tuple[Multivector | None, tuple[str, ...]]:
        if (value is None) == (through is None):
            raise TypeError(f"add_{kind} requires exactly one of value or through")
        if value is not None:
            if not isinstance(value, Multivector):
                raise TypeError(f"{kind} value must be a galaga Multivector")
            return value, ()
        dependencies = tuple(_object_key(key) for key in cast(Sequence[str], through))
        if len(dependencies) != expected_points:
            raise ValueError(f"a {kind} requires {expected_points} defining points")
        if len(set(dependencies)) != len(dependencies):
            raise ValueError(f"a {kind}'s defining point names must be distinct")
        for dependency in dependencies:
            definition = self._definitions.get(dependency)
            if definition is None or definition.kind != "point":
                raise KeyError(f"{dependency!r} is not a plotted point")
        return None, dependencies

    def _line_through(self, points: tuple[str, str]) -> Multivector:
        return outer_product(
            self.point(points[0]),
            self.point(points[1]),
            self._conformal_model.infinity,
        )

    def _circle_through(self, points: tuple[str, str, str]) -> Multivector:
        return outer_product(*(self.point(key) for key in points))

    def _classify(self, value: Multivector) -> CGA2DKind:
        if not isinstance(value, Multivector):
            raise TypeError("plotted values must be galaga Multivectors")
        grade = value.homogeneous_grade()
        if grade == 1:
            self._point_scene(value)
            return "point"
        if grade == 2:
            flat_test = outer_product(value, self._conformal_model.infinity)
            if np.allclose(flat_test.data, 0.0, rtol=0.0, atol=self._atol):
                raise ValueError("a direct 2D CGA plot does not yet support flat points")
            self._dipole_scene(value)
            return "dipole"
        if grade == 3:
            flat_test = outer_product(value, self._conformal_model.infinity)
            if np.allclose(flat_test.data, 0.0, rtol=0.0, atol=self._atol):
                self._line_scene(value)
                return "line"
            self._circle_scene(value)
            return "circle"
        raise ValueError("a direct 2D CGA plot supports grade-1 points, grade-2 dipoles, and grade-3 lines or circles")

    def _point_scene(self, value: Multivector) -> dict[str, float]:
        if not isinstance(value, Multivector):
            raise TypeError("point value must be a galaga Multivector")
        if value.homogeneous_grade() != 1:
            raise ValueError("a plotted conformal point must have grade 1")
        radius_squared = float(self._conformal_model.radius_squared(value, atol=self._atol))
        if abs(radius_squared) > self._atol:
            raise ValueError("a plotted point must have zero signed squared radius")
        x, y = self._conformal_model.coordinates(value, atol=self._atol)
        return {"x": float(x), "y": float(y)}

    def _line_scene(self, value: Multivector) -> dict[str, float]:
        if not isinstance(value, Multivector):
            raise TypeError("line value must be a galaga Multivector")
        if value.homogeneous_grade() != 3:
            raise ValueError("a direct 2D conformal line must have grade 3")
        flat_test = outer_product(value, self._conformal_model.infinity)
        if not np.allclose(flat_test.data, 0.0, rtol=0.0, atol=self._atol):
            raise ValueError("a direct 2D conformal line must contain infinity")

        dual_line = self._conformal_model.dual(value)
        basis = self._conformal_model.euclidean_basis_vectors()
        a, b = (float(scalar_product(dual_line, vector)) for vector in basis)
        c = float(scalar_product(dual_line, self._conformal_model.origin))
        magnitude = sqrt(a * a + b * b)
        if magnitude <= self._atol:
            raise ValueError("cannot draw a degenerate conformal line")
        a, b, c = a / magnitude, b / magnitude, c / magnitude
        pivot = a if abs(a) > self._atol else b
        if pivot < 0:
            a, b, c = -a, -b, -c
        return {"a": a, "b": b, "c": c}

    def _dipole_scene(self, value: Multivector) -> dict[str, float | bool]:
        if not isinstance(value, Multivector):
            raise TypeError("dipole value must be a galaga Multivector")
        if value.homogeneous_grade() != 2:
            raise ValueError("a direct 2D conformal dipole must have grade 2")
        flat_test = outer_product(value, self._conformal_model.infinity)
        if np.allclose(flat_test.data, 0.0, rtol=0.0, atol=self._atol):
            raise ValueError("a direct 2D conformal dipole must not contain infinity")

        try:
            center = self._conformal_model.center(value)
        except ValueError:
            return {"finite": False, "real": False, "tangent": False}
        cx, cy = self._conformal_model.coordinates(center, atol=self._atol)
        radius_squared = float(self._conformal_model.radius_squared(center, atol=self._atol))
        attitude = self._conformal_model.attitude(value)
        dx, dy = (float(scalar_product(attitude, vector)) for vector in self._conformal_model.euclidean_basis_vectors())
        magnitude = sqrt(dx * dx + dy * dy)
        if magnitude <= self._atol:
            return {"finite": False, "real": False, "tangent": False}

        if radius_squared < -self._atol:
            return {
                "finite": True,
                "cx": float(cx),
                "cy": float(cy),
                "radius_squared": radius_squared,
                "real": False,
                "tangent": False,
            }

        radius = sqrt(max(0.0, radius_squared))
        ux, uy = dx / magnitude, dy / magnitude
        return {
            "finite": True,
            "cx": float(cx),
            "cy": float(cy),
            "x1": float(cx + radius * ux),
            "y1": float(cy + radius * uy),
            "x2": float(cx - radius * ux),
            "y2": float(cy - radius * uy),
            "radius_squared": radius_squared,
            "real": True,
            "tangent": radius <= self._atol,
        }

    def _circle_scene(self, value: Multivector) -> dict[str, float]:
        if not isinstance(value, Multivector):
            raise TypeError("circle value must be a galaga Multivector")
        if value.homogeneous_grade() != 3:
            raise ValueError("a direct 2D conformal circle must have grade 3")
        flat_test = outer_product(value, self._conformal_model.infinity)
        if np.allclose(flat_test.data, 0.0, rtol=0.0, atol=self._atol):
            raise ValueError("a direct 2D conformal circle must not contain infinity")

        center = self._conformal_model.center(value)
        x, y = self._conformal_model.coordinates(center, atol=self._atol)
        radius_squared = float(self._conformal_model.radius_squared(center, atol=self._atol))
        if radius_squared < -self._atol:
            raise ValueError("cannot draw an imaginary conformal circle")
        return {
            "cx": float(x),
            "cy": float(y),
            "r": sqrt(max(0.0, radius_squared)),
        }

    def _coordinates_changed(self, change: dict[str, object]) -> None:
        self._rebuild_scene()
        old = change.get("old")
        new = change.get("new")
        if not isinstance(old, dict) or not isinstance(new, dict):
            return
        values_changed = False
        for key, definition in self._definitions.items():
            if definition.kind != "point" or key not in old or key not in new:
                continue
            old_coordinates = _coordinates2(old[key], name=f"point {key!r}")
            new_coordinates = _coordinates2(new[key], name=f"point {key!r}")
            if old_coordinates == new_coordinates:
                continue
            values_changed = True
            previous = self._conformal_model.up(old_coordinates)
            value = self._conformal_model.up(new_coordinates)
            if definition.name is not None:
                previous = previous.named(definition.name)
                value = value.named(definition.name)
            event = CGA2DChange(
                key=key,
                previous=previous,
                value=value,
                coordinates=new_coordinates,
            )
            for handler in tuple(self._change_handlers):
                handler(event)
        if values_changed:
            current_values = self.values
            for handler in tuple(self._values_handlers):
                handler(current_values)

    def _rebuild_scene(self) -> None:
        scene: list[dict[str, object]] = []
        errors: list[str] = []
        for key, definition in self._definitions.items():
            try:
                value = self.geometry(key)
                if definition.kind == "point":
                    geometry = self._point_scene(value)
                elif definition.kind == "dipole":
                    geometry = self._dipole_scene(value)
                elif definition.kind == "line":
                    geometry = self._line_scene(value)
                else:
                    geometry = self._circle_scene(value)
            except (TypeError, ValueError) as error:
                errors.append(f"{key}: {error}")
                continue
            scene.append(
                {
                    "id": key,
                    "kind": definition.kind,
                    "label": definition.label,
                    "color": definition.color,
                    "draggable": definition.draggable,
                    "line_style": definition.line_style,
                    **geometry,
                }
            )
        self.error = "; ".join(errors)
        self.scene = scene


def cga2d(
    model: ConformalModel,
    objects: Mapping[str, Multivector] | None = None,
    **kwargs: object,
) -> CGA2DPlot:
    """Create a :class:`CGA2DPlot`, optionally populated with static values."""
    plot = CGA2DPlot(model, **kwargs)
    for key, value in (objects or {}).items():
        plot.add(key, value)
    return plot


def _view_config(
    *,
    xlim: Sequence[Real],
    ylim: Sequence[Real],
    width: int,
    height: int,
    grid: bool,
) -> dict[str, object]:
    xmin, xmax = _limits(xlim, name="xlim")
    ymin, ymax = _limits(ylim, name="ylim")
    if not isinstance(width, int) or isinstance(width, bool) or width <= 0:
        raise ValueError("width must be a positive integer")
    if not isinstance(height, int) or isinstance(height, bool) or height <= 0:
        raise ValueError("height must be a positive integer")
    if not isinstance(grid, bool):
        raise TypeError("grid must be a boolean")
    return {
        "xlim": [xmin, xmax],
        "ylim": [ymin, ymax],
        "width": width,
        "height": height,
        "grid": grid,
    }


def _limits(value: Sequence[Real], *, name: str) -> tuple[float, float]:
    if isinstance(value, (str, bytes)) or len(value) != 2:
        raise ValueError(f"{name} must contain exactly two bounds")
    lower, upper = value
    if any(not isinstance(bound, Real) or isinstance(bound, (bool, np.bool_)) for bound in (lower, upper)):
        raise TypeError(f"{name} bounds must be real numbers")
    result = (float(lower), float(upper))
    if not all(isfinite(bound) for bound in result):
        raise ValueError(f"{name} bounds must be finite")
    if result[0] >= result[1]:
        raise ValueError(f"{name} lower bound must be less than its upper bound")
    return result


def _coordinates2(value: object, *, name: str) -> tuple[float, float]:
    if isinstance(value, (str, bytes)):
        raise TypeError(f"{name} coordinates must be real numbers")
    try:
        coordinates = tuple(cast(Sequence[object], value))
    except TypeError as error:
        raise TypeError(f"{name} coordinates must be an iterable") from error
    if len(coordinates) != 2:
        raise ValueError(f"{name} requires exactly two coordinates")
    if any(not isinstance(coordinate, Real) or isinstance(coordinate, (bool, np.bool_)) for coordinate in coordinates):
        raise TypeError(f"{name} coordinates must be real numbers")
    result = (float(coordinates[0]), float(coordinates[1]))
    if not all(isfinite(coordinate) for coordinate in result):
        raise ValueError(f"{name} coordinates must be finite")
    return result


def _object_key(value: object) -> str:
    if not isinstance(value, str):
        raise TypeError("plot object names must be strings")
    normalized = value.strip()
    if not normalized:
        raise ValueError("plot object names must not be empty")
    return normalized


def _label(value: str | None, key: str) -> str:
    if value is None:
        return key
    if not isinstance(value, str):
        raise TypeError("plot labels must be strings")
    return value


def _line_style(value: CGA2DLineStyle | None, *, derived: bool) -> CGA2DLineStyle:
    if value is None:
        return "dotted" if derived else "solid"
    if value not in ("solid", "dashed", "dotted"):
        raise ValueError("line_style must be 'solid', 'dashed', or 'dotted'")
    return value


def _name(value: Name | None) -> Name | None:
    if value is not None and not isinstance(value, Name):
        raise TypeError("generated geometry names must be galaga Name values or None")
    return value
