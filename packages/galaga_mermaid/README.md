# galaga-mermaid

Experimental Mermaid flowcharts for Galaga 2 expression provenance.

This package is independently versioned and is not published by the joint
Galaga release. Install the development integration from a v2 checkout
(Python 3.11+):

```bash
python -m pip install -e ./packages/galaga -e ./packages/galaga_mermaid
```

```python
from galaga import Algebra, geometric_product
from galaga_mermaid import expr_to_mermaid, mv_to_mermaid

algebra = Algebra(3)
e1 = algebra.vector([1, 0, 0], name="a", expr=True)
e2 = algebra.vector([0, 1, 0], name="b", expr=True)
product = geometric_product(e1, e2)

mv_to_mermaid(product)
expr_to_mermaid(product.expr, presentation=algebra.presentation)
```

Expression provenance deliberately contains no algebra or captured symbol
values. `expr_to_mermaid(..., show_values=True)` can annotate evaluable nodes
when `algebra=` and an `environment={"name": value}` mapping are supplied.
`mv_to_mermaid` derives the presentation and algebra from a facade value and
automatically supplies its own value for a named-symbol leaf.

The implementation traverses only the public immutable `Call`, `Symbol`, and
literal node fields. It does not import the Galaga 1 expression hierarchy or
read private multivector expression state.

## Executable example

The repository includes a Marimo notebook demonstrating interactive layout,
compact trees, value annotations, generated source, and notation-sensitive
labels:
[Mermaid diagrams from Galaga expressions](https://github.com/edouardp/galaga/blob/galaga_v2/examples/mermaid/mermaid_diagram.py).
