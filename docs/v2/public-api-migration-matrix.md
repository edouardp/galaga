# Galaga 1 to 2 Public API Migration Matrix

## Purpose and authority

This document is the human-readable view of the exhaustive replacement
contract completed in Phase 1. The executable source of truth is
[`v1_surface_manifest.py`](../../packages/galaga/tests/compatibility/v1_surface_manifest.py),
and
[`test_v1_surface_manifest.py`](../../packages/galaga/tests/compatibility/test_v1_surface_manifest.py)
compares historical names with the independently captured
[v1 surface archive](../../packages/galaga/tools/baselines/public-surface-v1.json).
Current v2 behavior is still checked live. See
[ADR-096](../adrs/096-compatibility-manifests-use-historical-api-evidence.md).

The manifest currently classifies:

- all 99 former top-level names captured from `galaga.legacy.__all__`;
- all 151 promoted names in `galaga.__all__` and `galaga.facade.__all__`;
- all 28 public legacy `Algebra` members;
- all 20 public legacy `Multivector` members;
- all 22 special methods declared by the legacy `Multivector`;
- all six legacy multivector formatting and display hooks, including
  `_repr_latex_`;
- all 59 public legacy expression classes;
- all 27 non-private top-level package modules and nine relied-upon nested
  entry points;
- four companion-package or example touch points; and
- four known dependencies on private legacy structures.

Missing or invented historical dispositions fail the compatibility suite,
without requiring the old engine to remain importable. A separate identity
contract keeps the promoted top-level manifest exactly synchronized with the
facade. Package-file classification remains live: adding or removing a module
requires an explicit inventory update.

## Top-level exports

### Numeric facade: promoted in Phase 8

`Algebra`, `Multivector`, and the following long-form numeric operations are
owned by `galaga.facade` and re-exported as the exact same objects by `galaga`:

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
`normalize`, together with `involute`, are temporary Phase 9 adapters in
`galaga.facade`. They emit the ledgered `GalagaDeprecationWarning` at the
callsite and dispatch through the canonical operation, so expression
provenance retains the canonical ID. The ambiguous `inner_product` and `ip`
names are absent and attribute access explains the explicit inner-product
choices; they are not facade catalog operations.

The exact policy and replacements are documented in
[Compatibility shims](compatibility-shims.md).

### Later-layer ownership

- `BasisBlade`, `BladeConvention`, `Notation`, and the ten `b_*` constructors
  migrate through the immutable presentation and blade configuration built in
  Phase 4. Legacy constructors remain compatibility work for Phase 7.
- `sym` and `simplify` belong to expression provenance in Phase 5.
- `project`, `reject`, and `reflect` are scheduled for removal rather than
  becoming generic facade helpers. Their meaning depends on the chosen
  subspace or geometry model, while their arithmetic is already an explicit
  composition of primitives. A future model-specific API may provide them
  together with the metadata and validation that make the operation precise.

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
`q`, and `r` belong to the numeric facade. Phase 4 added `config=`,
`presentation=`, `blades=`, `notation=`, `local_names=`, `display_order=`, and
`display=` to the facade. `repr_unicode` and `display_repr` remain rendering
compatibility-only legacy inputs: Galaga 2 uses `DisplayPolicy` and explicit
content/target format specs, while `repr` selects the active content policy in
ASCII. They are removed from the Galaga 2 constructor at the Phase 8 top-level
cutover.

`blade` and `locals` now have presentation-aware Phase 4 behavior; immutable
configuration replaces a mutable `notation` member. `get_basis_blade` remains
a compatibility spelling decision. Fraction and rotor constructors and the physical-constant
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
`latex`, together with `ascii`, `unicode`, `format`, `str`, `repr`, and the rich
LaTeX hook, are implemented through the Phase 6 semantic renderer. `bar`,
`dag`, `inv`, and `sq` remain possible Phase 7 conveniences over named
operations.

`scalar_part` is deliberately not a `Multivector` member. The optional
standalone helper is equivalent to `float(grade(value, 0))`; plain
`float(value)` rejects nonscalar coefficients above the inspection tolerance;
exact equality and hashing do not use that tolerance. See the
[migration guide](migration-guide.md#use-exact-equality-and-compatible-keys).

## Expression constructors and supported modules

All 59 public v1 expression classes are listed in the executable manifest.
`Expr` remains the base concept; scalar and symbol leaves are redesigned; and
operation-specific constructor classes become compatibility adapters over one
operation-identified expression node. The durable Galaga 2 model is now
implemented in `galaga.expression`; the 59 legacy adapters remain Phase 9
compatibility work.

The complete `SUBMODULE_DISPOSITIONS` inventory records 36 transitional import
paths. It is distinct from `SUPPORTED_SUBMODULES`, whose 15 live v2 entry
points are `blades`, `cga`, `core`, `display`, `expression`, `facade`,
`facade.catalog`, `names`, `presentation`, `presets`, `rga`, `rendering`, and
the three temporary `gram_bridge` paths, all under `galaga`.

The other 21 paths belong to the explicit `LEGACY_ONLY_SUBMODULES` inventory:
the old engine, blade and notation implementation, expression implementation,
five `latex_*` helpers, symbolic decorators, and legacy oracle paths. Their
dispositions and current file presence remain checked without importing them.
Some helpers import successfully in isolation but defer use of v1 until a
function call; that is not evidence of v2 support.

The supported prerelease oracle is still `galaga.legacy`, with
`galaga.legacy.render` and `galaga.legacy.simplify` avoiding collisions with
promoted facade functions. It is intentionally excluded from the v2-only
import contract, not removed by this test change. Legacy files and their
remaining tests retire in a separate Phase 9 step.

## Known private dependencies

The following accidental dependencies are migration requirements, not endorsed
public APIs:

- `galaga_matrix` no longer reads `Algebra._mul_index` or `_mul_sign`. Phase 7
  moved left-regular conversion to `Algebra.left_action`; Phase 9 has now
  removed the temporary v1 public-product fallback as well.
- `galaga_matrix` no longer reads or mutates private multivector expression or
  name state. Phase 7 introduced a package-owned immutable matrix expression
  protocol and a one-way adapter over public facade `name`, `expr`, and
  presentation values.
- `galaga_mermaid` now traverses the public immutable expression protocol and
  reads no private multivector fields.
- the maintained notebook ledger now uses immutable naming, eager values, and
  optional expression provenance, with full headless execution as its gate.

All recorded companion and example dependency rows are complete. This makes
the Phase 1 guarantee precise: the Phase 8 cutover may depend on a recorded
compatibility target, but not on unrecorded private legacy structure.

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
