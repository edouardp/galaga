# galaga-marimo

Marimo notebook helpers for geometric algebra — t-string powered LaTeX rendering.

Requires Python 3.14+ for t-string support.

`galaga` itself remains Python 3.11+. The t-string requirement belongs only to
this optional adapter package.

During the Galaga 2 prerelease train:

```bash
python -m pip install --pre "galaga-marimo>=2.0.0a4,<3"
```

## Usage

```python
from galaga import Algebra, exp
import galaga_marimo as gm

algebra = Algebra(2)
e1, e2 = algebra.basis_vectors(expr=True)
R = exp(-0.25 * (e1 ^ e2)).named("R")
v = (2 * e1 + e2).named("v")

gm.md(t"""
# Example

Rotor: {R}
Vector: {v}
Derivation: {v:expr}
Concrete coefficients: {v:value}
""")
```

The ordinary interpolation path uses the object's public `.latex()` protocol.
The `:name`, `:expr`, `:value`, and `:full` format specifications select
Galaga facade content while keeping Marimo's inline/block layout independent.

## Recognizing Known Values

When computed results are numerically equal to named multivectors (e.g.
eigenstates, basis elements), use `recognize=` to annotate them:

```python
from galaga import Algebra

alg = Algebra(2)
e1, e2 = alg.basis_vectors()
u = alg.scalar(1.0).named("up", latex=r"\uparrow")
d = (e1 * e2).named("down", latex=r"\downarrow")

knowns = [u, d]

result = alg.scalar(1.0)
gm.md(t"Result: {result}", recognize=knowns)
# renders: Result: $1 \quad (\equiv \uparrow)$
```

The `Doc` builder also supports it:

```python
with gm.doc(recognize=knowns) as document:
    document.md(t"Known scalar: {u}")
    document.md(t"Known bivector: {d}")
document
```

Labels are taken from each MV's immutable `.name` value, created with
`.named(..., latex=...)`. Pass any collection (list, tuple, or dict) of named
multivectors.

Interactive visualizations are intentionally separate from this t-string
renderer. Install `galaga-anywidget` and import `galaga_anywidget.viz` for the
persistent 2D CGA widget.

See the [integration guide](https://github.com/edouardp/galaga/blob/galaga_v2/docs/v2/integration-migration.md)
for the public rendering and expression protocols used by companion packages.
