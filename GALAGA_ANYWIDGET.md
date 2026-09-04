# Galaga AnyWidget Learnings

This note records the design lessons from the first bidirectional Galaga
visualization: the persistent 2D CGA AnyWidget in `galaga_anywidget.viz`.

The important result is not the SVG renderer. It is the division of ownership
between Marimo, AnyWidget, and immutable Galaga multivectors.

## The target notebook shape

A visualization should add interaction without taking the algebra away from
normal notebook cells. The intended pattern is:

```python
# Stable construction cell
construction = viz.CGA2D(cga)
```

```python
# Reactive input cell
px, py = construction.coordinates("P", default=(-1, 0))
P = cga.up(px, py).named("P")
```

```python
# Ordinary algebra cell
C = (P ^ Q ^ R).named("C")
```

```python
# Scene synchronization cell
construction.display([P, Q, R], immutable=[C])
```

The visualization is constructed once. `P`, `Q`, `R`, and `C` are ordinary
immutable Galaga multivectors. Dragging changes the coordinate state read by
the second cell, so Marimo reruns the same visible Python dependency graph a
user would have written without a plot.

## A widget cannot rebind a Python cell variable

An AnyWidget callback cannot reach into a completed cell and rebind its local
name `P`. Mutating the coefficient array inside `P` would be the wrong answer
too: Galaga multivectors are immutable values, and doing so would bypass
Marimo's dependency tracking.

Marimo can react to a UI element's synchronized value. The bridge is therefore
semantic state owned by the UI element:

```text
browser drag
    -> AnyWidget point_coordinates["P"]
    -> Marimo reruns the cell that reads construction.coordinates("P")
    -> P = cga.up(px, py)
    -> derived algebra reruns
    -> construction.display(...) updates the existing scene
```

This is normal Marimo reactivity. It does not require access to Marimo's
private cell graph, variable metadata, or a hidden global state object.

## Store semantic inputs, not multivector coefficients

The browser owns two Cartesian numbers for each draggable point. It does not
own a conformal coefficient array.

Keeping `up()` in Python has several benefits:

- the configured null metric remains authoritative;
- normalization and conformal invariants stay in `ConformalModel`;
- expression provenance still records `up(x, y)`;
- the notebook displays the same multivectors used by later algebra; and
- a future renderer can reuse the coordinate state without duplicating CGA.

The same rule should guide other interactive objects. Prefer semantic controls
such as a circle center and radius, a line point and direction, or a motor
parameter. Convert them to multivectors in Python.

## The visualization object must be the UI element

`CGA2D` subclasses `mo.ui.anywidget`. It is not a plain Python controller that
creates a fresh UI object whenever `display()` is called.

This matters because Marimo tracks UI-element values, and because browser
state such as pointer capture, focus, and the loaded JavaScript model belongs
to one widget instance. `display()` updates scene traits in place and returns
`None`; it never replaces the visualization.

Construct the visualization in a cell that depends only on stable model and
view configuration. Render that same object directly or place it in a layout
alongside live algebra.

## Coordinate state has one owner

The named `point_coordinates` mapping is the source of truth after scene
initialization. Editable point multivectors passed back to `CGA2D.display()`
are projections of that state.

This distinction prevents a subtle feedback race:

1. the browser advances `P` to a new coordinate;
2. Marimo starts recomputing dependent cells;
3. another drag update advances the coordinate again;
4. an older `display([P, ...])` execution completes; and
5. if `display()` writes its stale `P` into `point_coordinates`, the point and
   every derived object jump backwards.

The persistent coordinate-first API therefore validates echoed editable
points but does not let them replace current coordinates. `set_point()` is the
explicit Python operation for moving a coordinate. The lower-level
`viz.update()` API retains point replacement for workflows that deliberately
make Python values authoritative.

This is a general bidirectional-binding rule: choose one owner for every
piece of state, and do not feed a delayed projection back into its source.

## Dragging has two time scales

The dragged point should follow the pointer locally on every browser event.
Sending every pointer event through Python is unnecessary and can build a
queue of obsolete reactive executions.

The current renderer uses:

- immediate local movement for the dragged SVG point;
- a latest-value throttle of roughly 30 updates per second to Python;
- a forced final synchronization on pointer release; and
- equality guards before sending or applying unchanged values.

The local point and the Python-derived scene therefore have different update
paths. This is intentional: pointer feedback stays responsive while Galaga
remains authoritative for algebraic results.

## Do not replace the pointer-capturing node

Rebuilding the complete SVG during an active drag destroys or disturbs the
node holding pointer capture. Suppressing all redraws avoids that problem but
freezes derived geometry until release.

The working compromise is:

- retain the dragged point node for the duration of pointer capture; and
- update incoming Python-derived line, circle, and other result nodes in
  place.

The browser is not recomputing `P ^ Q ^ R`. It is only painting successive
scene descriptions produced by Python. If the Python round trip eventually
becomes too slow for a larger construction, visual interpolation between
authoritative snapshots is possible, but it should be identified as
interpolation rather than algebra.

## Read-only is a geometric role, not just disabled input

`immutable=[...]` distinguishes Python-derived results from editable inputs.
Read-only objects:

- have no manipulation handles;
- use a dotted style by default; and
- may still change when their Python construction reruns.

This supports explanatory constructions such as movable points and their
derived circle without moving the derivation into widget metadata.
`through=...` remains useful when an internal dependency is concise and the
Python construction does not need to be the teaching focus.

## Object identity and naming matter

Named multivectors provide semantic scene keys. The point named `P` must map
to the coordinate pair named `"P"`; insertion indices are too fragile for a
reactive construction. Names within one scene must therefore be distinct.

Unnamed values can use insertion-index keys in compact or lower-level views,
but named coordinate-first notebooks should prefer semantic names.

Colors are per-object scene data. A color-blind-aware palette cycles in display
order, and callers may replace the palette. This will also allow the same
object to keep its identity across future 2D and 3D views.

## Browser interaction needs no-op guards

Bidirectional traits can easily create update loops. Guard both directions:

- JavaScript should not call `save_changes()` for coordinates already held by
  the model;
- coordinate defaults should not replace an existing named pair;
- Python should not rebuild an unchanged scene; and
- a release event should force the final value once, then wait until the scene
  reaches that value before performing a full redraw.

Use tolerances only where floating-point geometry needs them. State ownership
and revision ordering should not be approximated with a large tolerance.

## Notebook authoring lessons

- Put widget construction in its own stable cell.
- Read widget values in a separate cell and construct ordinary Galaga values
  there.
- Keep each meaningful algebraic operation in normal downstream cells.
- Synchronize the scene in another cell that depends on all displayed values.
- Display the same persistent UI element alongside dynamic markdown if useful.
- Use underscore-prefixed local names for intermediate values that need not be
  shared across cells.
- Do not hide `up()`, wedge, meet, or another operation merely to make the
  visualization work.

## Testing lessons

The test stack needs multiple layers:

1. **Algebra tests.** Compute classifications and extraction formulas from the
   metric, and test incidence or projective equality against constructed
   objects.
2. **Python widget tests.** Exercise trait validation, callbacks, no-op guards,
   stable identity, colors, immutable styling, and stale-update ordering.
3. **JavaScript checks.** At minimum parse the module and pin critical drag
   behavior. A browser interaction harness would be stronger than source
   assertions and remains desirable. Until the repository adopts a browser
   test runtime, end-to-end pointer gestures are explicitly deferred; the
   release gate is JavaScript syntax validation plus source invariants for
   coordinate synchronization, throttling, and pointer release.
4. **Marimo graph validation.** Run `marimo check` so cross-cell dependencies
   and unique variable definitions are verified.
5. **Headless execution.** Export the notebook through Marimo to catch runtime
   integration failures. This validates construction, but not pointer gestures.

For a bug involving ordering, write the test in the problematic order. The
stale-display regression sets a newer coordinate first and then applies an
older displayed point, proving the coordinate cannot be rewound.

## Development and reload behavior

An already mounted widget has already loaded its JavaScript module, and a
running Python process has imported the package modules. Changes to browser
code generally require recreating the widget; changes to Python integration
code generally require restarting the Marimo process. Treat reload behavior as
a development concern, not part of the notebook API.

## Extensions

The architecture is deliberately reusable:

- 2D dipoles can be rendered as the real factors of one point-pair object;
- circle radius handles can own semantic center/radius parameters;
- transformations can own translator, rotor, or motor parameters; and
- a 3D view can show the conformal embedding surface and planar projection
  while sharing the same named coordinate state.

The invariant should remain: the browser owns interaction parameters, Python
owns geometric algebra, and the notebook makes the dependency between them
visible.
