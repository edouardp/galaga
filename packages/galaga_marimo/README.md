# galaga-marimo

Marimo notebook helpers for geometric algebra — t-string powered LaTeX rendering.

Requires Python 3.14+ for t-string support.

`galaga` itself remains Python 3.11+. The t-string requirement belongs only to
this optional adapter package.

## Usage

```python
import galaga_marimo as gm

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
from galaga.facade import Algebra

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
with gm.doc(recognize=knowns) as d:
    d.md(t"g₊(↓) = {g_plus(d)}")
    d.md(t"g₋(↓) = {g_minus(d)}")
```

Labels are taken from each MV's immutable `.name` value, created with
`.named(..., latex=...)`. Pass any collection (list, tuple, or dict) of named
multivectors.
