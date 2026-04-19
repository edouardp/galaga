# galaga-marimo

Marimo notebook helpers for geometric algebra — t-string powered LaTeX rendering.

Requires Python 3.14+ for t-string support.

## Usage

```python
import galaga_marimo as gm

gm.md(t"""
# Example

Rotor: {R}
Vector: {v}
""")
```

## Recognizing Known Values

When computed results are numerically equal to named multivectors (e.g.
eigenstates, basis elements), use `recognize=` to annotate them:

```python
from galaga import Algebra

alg = Algebra(2)
e1, e2 = alg.basis_vectors()
u = alg.scalar(1.0).name(r"\uparrow")
d = (e1 * e2).name(r"\downarrow")

knowns = {r"\uparrow": u, r"\downarrow": d}

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

Labels are LaTeX strings — use whatever notation fits your domain.
