# Galaga 2 examples

These notebooks introduce the Galaga 2 architecture one layer at a time. They
use the promoted top-level `galaga` API; `galaga.facade` remains the explicit
implementation namespace and `galaga.core` the presentation-free engine.

The recommended reading order is:

1. [Algebra construction](algebra_construction.py) — metric constructors,
   complete presets, diagnostic options, and presentation overrides, including
   metric-derived STA product names, signed-versus-native blade lookup, and
   exterior-word labels versus geometric products in oblique frames.
2. [Eager values and expressions](eager_values_and_expressions.py) — numeric
   values, optional expression provenance, naming, long-form operations,
   variadic products, checked scalar conversion, tiny-value display tolerance,
   literal versus named fractions, mixed-input snapshots versus symbol
   rebinding, diagnostic nodes versus mathematical rendering, and numeric,
   structural and rendered equality with exact floating-point key semantics.
3. [Presentation contexts](presentation_contexts.py) — content selection,
   immutable presentation views, scoped changes, explicit render overrides,
   numeric display policy, and rendered-string snapshots versus new scoped
   rendering calls, ambiguous accents, and metric-derived contraction signs.
4. [Custom functional notation](custom_functional_notation.py) — constructing
   an algebra with custom short forms such as `metric_ip` and `hestenes_ip`,
   extending built-in short notation, and keeping Python aliases separate from
   rendering.
5. [Numeric core](numeric_core.py) — the presentation-free engine beneath the
   facade and the boundary between the two packages.

The construction and presentation lessons also use `galaga_matrix` to display
their Gram matrices.
The notebooks require Python 3.14 because Marimo's dynamic Markdown examples
use t-strings. From the repository root, open the local example gallery with:

```shell
make run-marimo
```

The launcher uses editable installs of every local Galaga package, so the
notebooks exercise uncommitted source without containing repository-specific
path setup. The same files run unchanged against installed releases outside
the checkout.

All five notebooks are part of the executable example ledger. The test suite
compiles them, validates their Marimo dependency graphs, and executes them
headlessly.

The optional [`galaga_matrix` example series](../matrix/README.md) continues
from the facade into compact, left-regular, Pauli, Dirac, quaternion, and
spinor-column representations.

Continue the expression lesson with
[involutions and grades](../algebra/involutions_and_grade_ops.py): selectable
Gram matrices, grade decomposition, involution signs, symbol rebinding and
why a nonsimple bivector can have a nonzero wedge square.

Then explore [exponentials, logarithms and rotors](../algebra/exp_log_rotors.py):
explicit angle units and plane normalization, displayed Gram matrices for
elliptic/hyperbolic/null generators, compound grade-four terms, and why an
even STA phase need not be a rotor. The lesson distinguishes reversion from
inverse conjugation and explains the current logarithm's narrower domain.
