# Galaga 1 to 2 Public API Migration Matrix

## Purpose and authority

This document is the human-readable view of the exhaustive replacement
contract completed in Phase 1. The executable source of truth is
[`v1_surface_manifest.py`](../../packages/galaga/tests/compatibility/v1_surface_manifest.py),
and
[`test_v1_surface_manifest.py`](../../packages/galaga/tests/compatibility/test_v1_surface_manifest.py)
compares it with the live Galaga 1 API.

The manifest currently classifies:

- all 99 names in `galaga.__all__`;
- all 28 public legacy `Algebra` members;
- all 20 public legacy `Multivector` members;
- all 22 special methods declared by the legacy `Multivector`;
- all six legacy multivector formatting and display hooks, including
  `_repr_latex_`;
- all 59 public legacy expression classes;
- all 19 non-private top-level package modules and seven relied-upon nested
  entry points;
- four companion-package or example touch points; and
- four known dependencies on private legacy structures.

Adding or removing a live v1 export without updating the matrix fails the
compatibility suite. Each row has one owner, action, target, milestone, and,
where applicable, migration-warning text.

## Top-level exports

### Numeric facade: completed in Phase 2

`Algebra`, `Multivector`, and the following long-form numeric operations are
owned by `galaga.facade`:

`antidot_product`, `anticommutator`, `antimetric_apply`, `antireverse`,
`antiwedge`, `bulk_part`, `commutator`, `complement`, `conjugate`,
`doran_lasenby_inner`, `dual`, `even_grades`, `exp`,
`geometric_antiproduct`, `geometric_product`, `grade`, `grade_involution`,
`grades`, `hestenes_inner`, `inverse`, all `is_*` predicates,
`jordan_product`, both complements, both contractions, both Hodge duals, both
interior products, both weight duals, `lie_bracket`, `log`, `metric_apply`,
`metric_inner_product`, `metric_regressive_product`, `norm`, `norm2`,
`odd_grades`, `outer_product`, the four outer transcendentals,
`regressive_product`, `reverse`, `sandwich`, `scalar_product`, `scalar_sqrt`,
`sqrt`, `squared`, `transwedge`, `transwedge_antiproduct`, `uncomplement`,
`undual`, `unit`, and `weight_part`.

The exact list is intentionally machine checked rather than duplicated as an
independent hand-maintained constant in this document.

### Same-object functional aliases

These concise functional spellings remain available without separate catalog
entries or implementations:

| Alias | Canonical operation | Policy |
|---|---|---|
| `dorst_inner` | `doran_lasenby_inner` | retained |
| `gp` | `geometric_product` | retained |
| `join` | `outer_product` | retained |
| `meet` | `regressive_product` | retained |
| `op` | `outer_product` | retained |
| `rev` | `reverse` | retained |
| `sw` | `sandwich` | retained |
| `wedge` | `outer_product` | retained |
| `involute` | `grade_involution` | compatibility through Phase 9 |

`galaga.facade.OPERATION_ALIASES` is the executable facade alias manifest.

The v1 spellings `mag2`, `magnitude_squared`, `norm_squared`, `normalise`, and
`normalize` are temporary Phase 9 aliases. The ambiguous `inner_product` and
`ip` names become deprecation adapters that direct users to an explicitly
named convention; they are not facade catalog operations. Their warning text
is fixed in the executable matrix and will be emitted when the Galaga 2
top-level compatibility shims are installed.

### Later-layer ownership

- `BasisBlade`, `BladeConvention`, `Notation`, and the ten `b_*` constructors
  belong to presentation and blade configuration in Phase 4.
- `sym` and `simplify` belong to expression provenance in Phase 5.
- `project`, `reject`, and `reflect` remain compositional helpers for Phase 7;
  they do not become core primitives.

## `Algebra` contract

The Phase 2 eager facade owns numeric construction, metric metadata, algebra
identity, and numeric factories. This includes `signature`, `n`, `dim`,
`identity`, `I`, `pseudoscalar`, basis vectors and blades, arbitrary blades,
scalars, vectors, the extended metric matrix, and the metric
antiexomorphism matrix.

The accepted numeric construction forms are:

```python
Algebra((1, -1, 0))
Algebra(())
Algebra(2, 1, 0)
Algebra(signature=(1, -1, 0))
Algebra(sig=(1, -1, 0))
Algebra(gram=((2.0, 0.0), (0.0, -3.0)))
Algebra(gram=((1.0, 0.25), (0.25, 1.0)))
```

The first three retain v1 call shapes, including the zero-dimensional scalar
algebra. The keyword signature aliases and native Gram matrix are Galaga 2
forms. Conflicting metric descriptions are rejected.

The exact v1 constructor parameters are also classified. `p_or_signature`,
`q`, and `r` belong to the numeric facade. `blades`, `repr_unicode`,
`notation`, and `display_repr` are presentation or rendering configuration for
Phase 4; their absence from the Phase 2 numeric constructor is deliberate.

`blade`, `get_basis_blade`, `locals`, and `notation` acquire presentation-aware
behavior in Phase 4. Fraction and rotor constructors and the physical-constant
conveniences are classified as Phase 7 helpers rather than responsibilities of
the numeric kernel. The old `Algebra.c`, `.e`, `.h`, `.hbar`, `.pi`, `.sqrt2`,
and `.tau` members are removed in Phase 9 with guidance to explicit domain
helpers or `algebra.scalar(value)`.

## `Multivector` contract

The eager facade owns immutable `.numeric`, `.algebra`, and `.data` access,
coefficient and vector access, grade inspection, exact equality and hashing,
approximate equality, checked scalar conversion, and Python arithmetic
operators.

The 22 legacy declared special methods are recorded exactly. Galaga 2 adds
unary `+`, reflected outer product, and reflected Doran–Lasenby inner product,
because scalar-left and multivector-left forms should follow the same coercion
rules. Those additions are separately classified rather than presented as v1
behavior.

Names, expression state, and old `lazy`/`symbolic` mutation-style methods move
to the immutable expression-provenance design in Phase 5. `display` and
`latex` move to rendering in Phase 6. `bar`, `dag`, `inv`, and `sq` remain
possible Phase 7 conveniences over named operations.

`scalar_part` is deliberately not a `Multivector` member. The optional
standalone helper is equivalent to `float(grade(value, 0))`; plain
`float(value)` rejects every non-scalar value.

## Expression constructors and supported modules

All 59 public v1 expression classes are listed in the executable manifest.
`Expr` remains the base concept; scalar and symbol leaves are redesigned; and
operation-specific constructor classes become compatibility adapters over one
operation-identified expression node in Phases 5 and 9.

The supported import inventory covers every non-private top-level module:
`algebra`, `basis_blade`, `blade_convention`, `core`, `expr`, `facade`,
`gram_bridge`, the five `latex_*` modules, `lazy`, `notation`, `ops`, `render`,
`simplify`, `symbolic`, and `symbolic_core`. It also records
`facade.catalog`, both bridge submodules, and the four `symbolic_core`
submodules used by current tests or companion packages.

`galaga.facade` and `galaga.core` are permanent. Rendering modules,
`galaga.ops`, simplification, and symbolic modules have explicit owners in
Phases 5 through 7 rather than being treated as incidental implementation
files. Old modules remain compatibility entry points according to their
recorded milestones.

## Known private dependencies

The following accidental dependencies are migration requirements, not endorsed
public APIs:

- `galaga_matrix` reads `Algebra._mul_index` and `_mul_sign`; Phase 7 must use
  public linear-action APIs instead.
- `galaga_matrix` reads and mutates private multivector expression state;
  Phase 7 must use the public expression-provenance protocol.
- `galaga_mermaid` traverses private expression and multivector fields; Phase 7
  must use the public expression traversal protocol.
- examples display `_is_lazy` and `_name`; they must move to immutable naming
  and expression provenance.

These rows make the Phase 1 guarantee precise: later work may depend on a
recorded migration target, but not on an unrecorded private legacy structure.

## Deliberate Galaga 2 corrections

- Commutators and Lie brackets are unscaled; explicitly half-scaled functions
  retain the factor of one half.
- Anticommutators and Jordan products are unscaled; the half anticommutator is
  explicit.
- Competing inner products remain explicitly named.
- Equality and hashing are exact; approximate comparison is explicit.
- Scalar conversion is strict and public coefficient arrays are immutable.
- Naming and expression provenance do not mutate values.
- Long operation names are canonical, with selected same-object aliases.
- Only geometric and outer products currently accept variadic calls, lowered
  immediately to deterministic binary left folds.

These corrections are tested in the core, facade, compatibility, and migrated
numeric contract suites.
