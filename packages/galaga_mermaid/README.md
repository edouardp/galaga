# galaga-mermaid

Experimental Mermaid flowcharts for Galaga 2 expression provenance.

```python
from galaga.facade import Algebra, geometric_product
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
