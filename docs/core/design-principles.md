# Design Principles

## Project posture

`galaga.core` is the compute-first foundation for Galaga 2.0. It is not an
expression-tree system, renderer, notation engine, or notebook integration.
Those layers may consume core values, but they must not determine the meaning
or storage of the algebra underneath them.

The project prioritizes mathematical correctness, explicit conventions,
inspectable implementation, and predictable failure over clever shortcuts.
Performance matters, but an optimization may change only how an operation is
computed, never what it means.

## 1. The Gram matrix is the metric

Every constructor form is normalized to one real symmetric matrix

$$
G_{ij}=\frac12(e_i e_j+e_j e_i).
$$

Signature tuples and `Cl(p,q,r)` counts are convenience descriptions of
diagonal Gram matrices. They are not a second metric model. A native
nonorthogonal basis, including a conformal origin/infinity null pair, is stored
directly instead of being hidden behind an orthogonal change of basis.

## 2. Exterior coordinates are independent of the metric

A multivector uses dense coefficients in the exterior basis. Bitmask `S`
always denotes the ordered wedge of the basis vectors selected by `S`.

The metric changes geometric products and metric-derived maps. It does not
change coefficient slots, grades, complements, or the exterior product. This
separation is what lets a one-hot native null vector remain a one-hot value
while still having a nonzero scalar product with another native basis vector.

## 3. Compute first, render later

The numeric result exists independently of its name, notation, or expression
history. Symbolic coefficients and expression trees are deliberately outside
the current scope. The Galaga facade should attach those concerns without
making the numeric kernel import or understand them.

This boundary gives tests a simple question to answer: are the coefficient
arrays correct for the supplied metric?

## 4. Named functions carry mathematical meaning

Python operators are convenient but scarce and overloaded across GA
libraries. Named functions are the unambiguous contract:

- `geometric_product`, `outer_product`, and `scalar_product` state which
  product is requested;
- `left_contraction`, `hestenes_inner`, and `metric_inner_product` do not hide
  convention choices behind a generic `inner` name;
- `complement`, `dual`, and `right_hodge_dual` remain distinct because they
  have different metric requirements and meanings.
- `scalar_sqrt`, Study-number `sqrt`, `exp`, and Study-rotor `log` state their
  domains instead of masquerading as unrestricted scalar functions.

Operators remain documented sugar: `*` is geometric product, `^` is exterior
product, `|` is Doran–Lasenby inner, and `~` is reverse.

## 5. Scaling must be visible

The full commutator and anticommutator contain no implicit factor:

$$
[A,B]=AB-BA,
\qquad
\{A,B\}=AB+BA.
$$

`half_commutator` and `half_anticommutator` are the only names that introduce
one half. `galaga.core` also defines `lie_bracket` as the full commutator and
`jordan_product` as the full symmetric product. This differs from texts that
normalize the Jordan product by one half, so the explicit half-named function
is essential for portable code.

## 6. Degenerate metrics are ordinary inputs

PGA is not an exceptional failure mode. Operations that require an inverse
metric or inverse pseudoscalar say so and fail clearly. Metric-independent
complements, regressive products, antimetric operations, weight duals, and RGA
products remain available for singular metrics.

No implementation should manufacture a reciprocal null vector, silently
replace a singular metric, or use a pseudoinverse where the mathematical
operation requires a true inverse.

## 7. Immutability is the default

An `Algebra` copies and freezes its metric. A `Multivector` copies and freezes
its coefficient array. Shared exterior metadata and cached metric matrices are
also read-only.

This makes backend caches and shared dimension metadata safe implementation
details. Operations construct new values instead of mutating their operands.

## 8. Backend selection is semantically invisible

Diagonal, packed, lazy, and dense-reference backends implement the same
contract. Automatic selection may depend on metric shape and a conservative
memory estimate, but every backend must agree on products, grade-selected
products, and left actions.

Explicit backend selection exists for verification and diagnostics. User code
should normally use `auto`.

## 9. Independent oracles are worth their cost

The production product recurrence is checked against a dense Chevalley-action
reference, diagonal closed forms, and an exhaustive conformal change of basis.
The slow implementation is retained because an independent oracle is more
valuable than tests that merely repeat the production algorithm.

Numeric functions follow the same rule. Closed forms check general series,
round trips check square-root and logarithm branches, and general-Gram results
must agree across product backends.

## 10. Add numerical capability, not application vocabulary

The core owns operations that require numerical algorithms, convergence
control, or explicit real branch selection. Geometry conveniences that merely
compose those operations belong in a helper or facade layer.

For example, `exp` belongs in the core because a general multivector
exponential needs a convergence strategy. An explicit rotor constructor does
not: it normalizes a plane-angle generator and calls `exp`. Projection,
rejection, and reflection similarly compose contractions, products, and
`inverse`.

This boundary is about architectural responsibility, not whether a formula
can be written at all. Named algebraic conventions such as contractions and
commutators remain core contracts because their definitions resolve otherwise
ambiguous mathematical vocabulary.

## 11. Python scalar conversion is not implicit array conversion

`float(value)` is an explicit assertion that a multivector is scalar.
`float(grade(value, 0))` explicitly requests coefficient zero without making
that assertion about the original value. A standalone `scalar_part(value)` may
offer convenient shorthand, but it is not a distinct algebraic operation or a
required member method. `galaga.core` does not advertise multivectors as NumPy arrays
or route NumPy ufuncs into GA operations; callers choose the coefficient
array, checked scalar conversion, or named GA function deliberately.

This avoids silently treating a multivector as either one number or an
unstructured coefficient vector in generic numerical code.

## 12. Scope boundaries should stay honest

`galaga.core` currently supports real finite-dimensional Clifford algebras with a
symmetric numeric bilinear form and dense `float64` multivectors. Complex
coefficients, symbolic metrics, nonsymmetric forms, sparse coefficient values,
rendering, and expression trees require separate decisions rather than silent
partial support.

The real-only boundary also applies to analytic functions. A negative scalar
square root or a logarithm branch requiring complex coefficients raises rather
than changing the coefficient dtype or selecting an undocumented plane.
