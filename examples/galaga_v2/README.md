# Galaga 2 examples

These notebooks introduce the Galaga 2 architecture one layer at a time. They
use the promoted top-level `galaga` API; `galaga.facade` remains the explicit
implementation namespace and `galaga.core` the presentation-free engine.

The recommended reading order is:

1. [Algebra construction](algebra_construction.py) — metric constructors,
   complete presets, diagnostic options, and presentation overrides.
2. [Eager values and expressions](eager_values_and_expressions.py) — numeric
   values, optional expression provenance, naming, long-form operations,
   variadic products, and checked scalar conversion.
3. [Presentation contexts](presentation_contexts.py) — content selection,
   immutable presentation views, scoped changes, explicit render overrides,
   and numeric display policy.
4. [Custom functional notation](custom_functional_notation.py) — constructing
   an algebra with custom short forms such as `metric_ip` and `hestenes_ip`,
   extending built-in short notation, and keeping Python aliases separate from
   rendering.
5. [Numeric core](numeric_core.py) — the presentation-free engine beneath the
   facade and the boundary between the two packages.

The notebooks require Python 3.14 because Marimo's dynamic Markdown examples
use t-strings. From the repository root, open one with:

```shell
uv run --python 3.14 marimo edit examples/galaga_v2/algebra_construction.py
```

All five notebooks are part of the executable example ledger. The test suite
compiles them, validates their Marimo dependency graphs, and executes them
headlessly.

The optional [`galaga_matrix` example series](../matrix/README.md) continues
from the facade into compact, left-regular, Pauli, Dirac, quaternion, and
spinor-column representations.
