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
   structural and rendered equality with exact floating-point key semantics,
   rebindable denominator products and finite subnormal division.
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

These notebooks are part of the executable example ledger. The test suite
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

## Further migrated teaching notebooks

These lessons also use the v2 facade and participate in headless validation:

- [Reusable presenters](reusable_presenters.py): one-line recipes for comparing
  notation, content, blade order and spelling; composed blade, notation and
  display presets used with presenters and algebra scopes; metric-derived STA
  signs, CGA frame validation, and stable views for later cells.
- [Display gallery](display_gallery.py): rich algebra displays, basis vectors
  and bivectors, wedge tables, and vector/full bilinear form tables.
- [Notation overrides](notation_overrides.py): change the reverse symbol of a
  complete STA preset while keeping its metric, blade names, and other rules.
- [Oblique plane](oblique_plane.py): vary the angle between basis vectors,
  inspect the Gram and bilinear displays, and draw vectors and bivectors in a
  metric-derived plane with the optional anywidget package.
- [Witt bases and null geometry](../algebra/witt_bases_and_null_geometry.py):
  predict a moving receiver's Doppler shifts and build a finite fermionic
  occupation-state model from null pairs; then compare CGA/PGA duality.
- [The Witt plane in null coordinates](../algebra/witt_plane_from_null_coordinates.py):
  compare signed null-pair metrics with Euclidean 2D, recover an orthogonal
  frame, and derive split-complex projectors and real matrix units.
- [Conformal spacetime events](../spacetime/conformal_spacetime_events.py):
  connect three-point circles to Alice's hyperbolic worldline, construct
  motion with a boost rotor, and meet light cones with a curve and a line
  to trace a radio message and its echo. Natural units have g-dependent
  conversions to human times, distances, and astronomical comparisons.
- [Conformal spacetime versors](../spacetime/conformal_spacetime_versors.py):
  translate and dilate events using the null pair, then compare their
  conformal pairings and direct spacetime coordinates.
- [CSTA object classifier worksheet](../spacetime/conformal_spacetime_classifier.py):
  use grade, infinity incidence, and induced metric signs to describe
  witnessed point pairs, flat lines, and signed rounds.
- [CSTA model and classifiers](../spacetime/csta_model_and_classifiers.py):
  tour `presets.csta()`, event coordinates, signed intervals, direct and dual
  classifier hints, event pairs, causal flat lines, and signed rounds.
- [CSTA zoo and operators](../spacetime/csta_zoo_and_operators.py):
  classify rounds and causal flats, explore projectors and nilpotents,
  and verify boost, rotation, translation, dilation and conformal actions.
- [Four-dimensional rotor planes](../algebra/four_dimensional_rotor_planes.py):
  two-plane rotations and plots, principal logarithms, simple-plane extraction,
  self-dual versus simple bivectors, isoclinic ambiguity, and higher dimensions.
- [Dynamic notation](../basics/dynamic_notation.py): render the same reversal
  with a tilde, dagger, superscript, or function without changing its value.
- [LaTeX layout and simplification](../basics/latex_rewrites_demo.py): script
  fractions, explicit grouping and signs, and the boundary between layout
  and expression simplification.
- [Marimo helper guide](../basics/galaga_marimo_demo.py): interpolation,
  content specs, coefficient precision, document building, and widgets.
- [Spin-½ geometry](../quantum/quantum_physics.py): Bloch sphere, measurement,
  Stern–Gerlach, precession, phase freedom, double cover, and interpolation.
- [Mermaid rotations and boosts](../../test_mermaid.py): Euclidean rotation,
  electromagnetic-field invariants, and Thomas–Wigner rotation. This remains
  at its original root path; open it explicitly with Marimo on Python 3.14.

The separate [NumPy batching benchmark](../../bench_batched.py) derives its
coefficient tensor from public left-action matrices. It runs on Python 3.11
and later and is tested against the algebra, including non-diagonal metrics.
