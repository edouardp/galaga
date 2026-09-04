---
status: accepted
date: 2026-08-17
deciders: edouard
---

# ADR-091: CGA AnyWidget Synchronizes Semantic Coordinates

## Context and problem statement

The conformal model now provides the embedding, extraction, and semantic
queries needed to interpret ordinary direct CGA objects, but notebooks still
lack a persistent geometric view. A useful first view must draw planar points,
lines, and circles, remain alive after its creating cell finishes, and let a
dragged point participate in Marimo's reactive execution.

Galaga multivectors are immutable facade values. A browser therefore cannot
mutate the numeric core value inside an ordinary `up` result. Synchronizing a
complete coefficient array would also make the JavaScript view responsible
for metric normalization and conformal invariants that belong to
`ConformalModel`. Marimo can, however, rerun cells that read synchronized
values from a stable UI element when that element reports a browser update.

## Decision drivers

- Keep the conformal metric and object interpretation in Python.
- Make moved values ordinary Galaga multivectors that work with `down()` and
  every existing algebra operation.
- Use Marimo's UI-element reactivity rather than a separate event loop or
  notebook-global mutable variable.
- Keep the first renderer small while preserving a path to a 3D conformal
  embedding view.
- Give every object an identifiable, overridable colour.
- Keep all notebook-visible algebra values as ordinary immutable Galaga
  multivectors.

## Decision outcome

The first renderer lives in the separately installable `galaga-anywidget`
distribution. It is implemented as an AnyWidget with an SVG browser view. The
high-level `galaga_anywidget.viz.CGA2D` class constructs and owns one Marimo UI
element in its constructor. Its `display()` method accepts an ordered sequence of direct
2D conformal points, dipoles, lines, and circles and synchronizes them into
that existing element; it does not construct or return another view.

This makes the intended Marimo lifecycle explicit. A cell that depends only
on stable model and view configuration constructs and renders `CGA2D` once. A
separate reactive cell depends on the current algebra values and calls the
instance's `display()` method. Recomputing geometry therefore mutates the
scene trait of the original AnyWidget instead of rerunning the cell that owns
the UI element. The module-level `viz.display(...)` convenience function
remains available for static or one-cell views and can infer a conformal model
from a nonempty value sequence.

`CGA2D` is itself the Marimo AnyWidget UI element, rather than a non-reactive
container around one. The synchronized browser state is a mapping from point
identifiers to two Cartesian coordinates. `coordinates(name, default=...)`
reads one named pair and creates it on demand if absent. The default is used
only once. Because the calling cell references the UI element through this
method, a browser drag follows Marimo's normal AnyWidget dependency path and
reruns that cell.

Notebook cells reconstruct ordinary conformal points explicitly:

```python
px, py = construction.coordinates("P", default=(-1, 0))
P = cga.up(px, py).named("P")
```

The widget stores semantic Euclidean coordinates, not conformal coefficient
arrays. The `up()` call, its expression provenance, and every derived algebra
operation remain visible Python. Named displayed objects use their semantic
names as widget keys, so dragging the rendered `P` updates the same `"P"`
coordinate pair read by the algebra cell. Names in one `CGA2D` scene must be
distinct. Unnamed values retain stable insertion-index keys.

After scene initialization, those named coordinates have single ownership.
Editable point values passed back through `CGA2D.display()` are validated but
cannot replace the widget's current coordinates: they are reactive projections
of that state and may belong to an older Marimo execution. Programmatic moves
use `set_point()`. The lower-level module `viz.update()` API retains explicit
point replacement for compatibility. This separation prevents a delayed
`display([P, ...])` pass from rewinding an in-progress browser drag.

`construction.display([P, Q, R], immutable=[C])` appends read-only results to
the editable inputs in the persistent `construction` instance. Values in
`immutable` are dotted by default and cannot be dragged. The older
`plot[index]`, `plot[:]`, `on_values`, module-level `viz.display(...)`,
`viz.mutable(...)`, and explicit Marimo-state patterns remain available for
compact, compatibility, or lower-level uses; they are not required by the
ordinary coordinate-first notebook pattern.

The mutable compatibility wrapper uses identity equality and identity hashing.
Its multivector snapshot can change while the state handle remains stable, so
value-based equality would violate Python's hash contract and make dictionary
or set membership depend on the current snapshot. Callers compare
`handle.snapshot()` with an ordinary multivector when value equality is
required.

Marimo exposes `mo.state(...)` as a public factory but does not expose the
state-handle base class publicly. Direct algebraic use of the compatibility
wrapper therefore currently subclasses `marimo._runtime.state.State`. The
package constrains Marimo to `>=0.23.14,<0.25` and tests both ends of that
supported minor-version range; widening the range requires rerunning the
compatibility suite. The preferred coordinate-first `CGA2D` workflow does not
use this wrapper, but importing `viz` still validates this package boundary.

Callbacks are notifications over immutable values. A `CGA2DChange` contains
the object key, previous and current conformal multivectors, and current
Cartesian coordinates. Python can also move a point through `set_point`, and
all live views of the AnyWidget receive the synchronized state.

The Python layer classifies supported direct objects algebraically. A
grade-one zero-radius round point is drawn as a point. A non-flat direct
grade-two value is drawn as a dipole. A direct grade-three value containing
infinity is drawn as a line, while a direct grade-three value not containing
infinity is drawn as a circle. Line equations, dipole factors, circle centres,
and radii are derived through `ConformalModel` and public products; the
JavaScript view receives only rendering geometry. Lines declared through two
plotted points and circles through three plotted points are recomputed after a
defining point moves.

For a dipole, `center()` supplies its midpoint and signed squared
half-separation, while the Euclidean projection of `attitude()` supplies its
axis. Positive separation produces two real markers, zero produces one
repeated tangent marker, and negative separation produces an imaginary-pair
marker at the real center. This supports a visible
`D = meet(C1, C2)` notebook cell without implementing circle intersection in
JavaScript. A nonzero degenerate point pair with no finite round center remains
in the scene but has no planar marker. Direct flat points remain unsupported.

The list API makes those relationships explicit. `display(read_only=...)`
accepts object indices that cannot be directly manipulated, while
`display(through=...)` maps a derived line or circle index to two or three
preceding point indices. Galaga does not infer incidence from the original
coefficient arrays or expression provenance. Instead, it validates that the
supplied result is projectively equivalent to the declared construction and
then rebuilds the current result from the synchronized point values. The
semantic name is retained. Dependent geometry is read-only with respect to
direct manipulation and uses a dotted stroke by default; it still changes
indirectly when a defining point moves.

Replacement is no-op-guarded in both directions. JavaScript does not send
coordinates already held by its model, on-demand coordinate defaults do not
replace existing state, and `CGA2D.display()` does not rebuild scene data for
unchanged values. A read-only dipole, line, or circle uses a dotted stroke
whether it came from `immutable`, `read_only`, `through`, or a later Python
update.

Point coordinates are synchronized to Python at a roughly 30-frame-per-second
bounded interval during a drag, with a final forced synchronization at
release. This is a latest-value throttle rather than an end-of-drag debounce:
it avoids sending every browser pointer event while keeping Python-derived
geometry responsive. While pointer capture is active, the browser retains the
locally moved point instead of replacing the SVG and losing the drag. Incoming
Python `scene` updates still repaint derived dipole, line, and circle nodes in place.
Consequently a circle such as `P ^ Q ^ R` changes continuously during a drag,
but its geometry continues to come from the reactive Python algebra cell
rather than a duplicate JavaScript construction or interpolated rendering.

Colours are scene data rather than kind-wide CSS. Objects cycle through one
colour-blind-aware default palette in display order. `CGA2D(colors=...)`
replaces that palette for the persistent view, while the module-level
convenience function and lower-level add methods also accept colour overrides.

The initial view deliberately supports direct 2D points, dipoles, lines, and
circles only. A later 3D view may show the conformal paraboloid and its planar
projection, but it should consume the same semantic point-coordinate state
rather than reinterpret multivector coefficients in JavaScript.

The renderer was initially implemented under `galaga_marimo` while its API was
being explored. On 2026-08-21, before the first release, that temporary
placement was replaced by `galaga-anywidget`. The widget has its own
dependencies, browser assets, interaction tests, and likely 2D/3D evolution;
the t-string Markdown renderer has none of those responsibilities. Keeping the
packages separate therefore establishes the intended dependency and release
boundary before users depend on the provisional import path.

## Consequences

- Dragging changes a named Euclidean coordinate pair owned by the persistent
  UI element; ordinary notebook code then recomputes `up(x, y)`.
- Notebook cells can display both the current conformal point and its
  `down()` image with ordinary Marimo dependency tracking.
- Notebook-visible `P`, `Q`, and `R` are ordinary immutable multivectors with
  no Marimo-specific subtype or mutation API.
- Echoed editable point snapshots cannot overwrite newer widget-owned drag
  coordinates.
- The cell that owns a `CGA2D` instance has no dependency on the changing
  multivectors, so reactive scene synchronization preserves widget identity
  and browser interaction state.
- Python-derived read-only results can flow back into the same widget without
  making the widget responsible for their algebraic construction.
- Python-derived dipoles, lines, and circles repaint during an active point
  drag without replacing the pointer-capturing point node.
- A circle-circle meet remains one notebook-visible dipole even though the 2D
  renderer displays its two real factors when they exist.
- Direct object classification and drawing formulas are testable without a
  browser.
- A notebook can keep the Python wedge construction visible while displaying
  its read-only geometric result and movable inputs in one ordered scene.
- `galaga-anywidget` depends on AnyWidget, Marimo, and Traitlets and packages a
  small JavaScript/CSS asset pair.
- `galaga-marimo` remains responsible only for t-string Markdown rendering and
  does not depend on or re-export the visualization package.
- Editable input/result dependencies are explicit list metadata rather than
  inferred from multivector expressions.
