# galaga-anywidget

Interactive AnyWidget visualizations for Galaga geometric algebra.

The first renderer draws direct points, dipoles, lines, and circles in a
two-dimensional conformal model. It owns semantic Euclidean point coordinates,
so browser drags participate in Marimo's normal reactive execution while the
notebook keeps all geometric constructions in Python.

For the Galaga 2 beta, opt into prereleases:

```bash
python -m pip install --pre "galaga-anywidget>=2.0.0b1,<3"
```

## Persistent reactive construction

Requires Python 3.11+. In Marimo, first create the native-null conformal model
in a setup cell:

```python
from galaga import Algebra, presets
from galaga.cga import ConformalModel

cga = ConformalModel(Algebra(config=presets.cga(2)), expr=True)
```

Construct and render the visualization in a cell that has no dependency on
changing geometry:

```python
import galaga_anywidget.viz as viz

circle_viz = viz.CGA2D(
    cga,
    colors=["#0072B2", "#D55E00", "#009E73", "#7C3AED"],
)
circle_viz
```

Read named coordinates in another cell and construct ordinary multivectors:

```python
px, py = circle_viz.coordinates("P", default=(-1.75, -0.75))
qx, qy = circle_viz.coordinates("Q", default=(0.25, 1.5))
rx, ry = circle_viz.coordinates("R", default=(1.75, -0.5))

P = cga.up(px, py).named("P")
Q = cga.up(qx, qy).named("Q")
R = cga.up(rx, ry).named("R")
```

Keep the derived algebra in its own ordinary cell:

```python
C = (P ^ Q ^ R).named("C")
```

Then synchronize the current values into the persistent widget:

```python
circle_viz.display([P, Q, R], immutable=[C])
```

The three points are draggable and the dotted circle is read-only. Dragging a
point updates the named coordinate pair, which causes Marimo to reconstruct
the conformal point and every dependent value. The widget never duplicates the
circle construction in JavaScript.

For compact static or one-cell views, use
`viz.display([point, dipole, line, circle], model=cga)`. The lower-level
`CGA2DPlot` API supports explicit keys, replacements, dependent geometry, and
solid, dashed, or dotted line styles.

## Oblique metric plane

`oblique2d` visualizes a positive-definite two-dimensional Gram metric. It
embeds the stored basis in a Euclidean drawing plane, so the lengths and angle
of the displayed basis arrows are implied by the Gram matrix. Grade-1
values are arrows; grade-2 values are oriented parallelograms whose signed
area follows the bivector coefficient:

```python
from galaga import Algebra
from galaga_anywidget import oblique2d

algebra = Algebra(gram=[[1.0, 0.5], [0.5, 1.0]])
e1, e2 = algebra.basis_vectors()
plane = oblique2d(algebra, [2 * e1 + e2, (e1 ^ e2).named("area")])
plane
```

Indefinite or degenerate metrics are rejected because they do not have this
faithful Euclidean 2D interpretation.

The design and interaction lessons are recorded in
[GALAGA_ANYWIDGET.md](https://github.com/edouardp/galaga/blob/galaga_v2/GALAGA_ANYWIDGET.md).
