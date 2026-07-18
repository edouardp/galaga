# Numeric Test Migration Inventory

## Purpose

This inventory identifies the existing Galaga tests that should become
`galaga.core` tests, the tests that should exercise the core-backed facade, and
the tests that must remain in presentation, expression, rendering, helper, or
compatibility layers.

It is the detailed test input to Phase 3 of the
[Galaga 2 core cutover plan](core-cutover-plan.md). The inventory was audited
against `packages/galaga/tests` on 2026-07-18.

## What “move to core” means

A test belongs in `tests/core` when its subject is true of the numeric algebra
without blade names, notation, expression provenance, rendering, presets, or a
compatibility alias. Typical examples are a product identity, an involution
law, a low-dimensional Clifford-algebra fact, an inverse domain, or a
general-Gram metric property.

Moving a test does not mean copying it blindly:

1. port it to `galaga.core` constructors and long-form operations;
2. retain its independent mathematical oracle, source citation, random seed,
   and useful metric coverage;
3. merge it with an existing core test when both prove the same case;
4. replace assertions about a legacy private table with public mathematical
   behavior;
5. add an oblique or native-null metric case when the identity is valid there;
   and
6. delete the redundant legacy-only version only after the corresponding
   facade contract is covered.

The core and facade need different evidence:

- a core test asks whether the mathematics and numeric protocol are correct;
- a facade test asks whether construction, coercion, delegation, wrapping, and
  optional outer state preserve that result.

Arithmetic therefore does not need two large sets of copied coefficient
tests. The core keeps the exhaustive mathematics; the facade uses a smaller
table-driven parity suite and public contract tests.

## Tests already owned by the core

The migrated Gram suite currently lives in these files:

| Current file | Primary responsibility |
|---|---|
| `core/test_algebra.py` | construction, Gram validation, metadata, and native CGA |
| `core/test_backends.py` | backend selection, reference parity, actions, and selected products |
| `core/test_metric_rga.py` | metric matrices, complements, RGA products, dualities, and transwedge |
| `core/test_multivector.py` | representation, operators, algebra laws, and CGA basis change |
| `core/test_numeric_api.py` | grades, involutions, conveniences, and derived products |
| `core/test_numeric_functions.py` | square roots, exponential, logarithm, and outer functions |
| `core/test_public_contracts.py` | construction, Python protocols, and named-operation boundaries |
| `core/test_migration_boundary.py` | package and temporary cutover boundary, not numeric mathematics |

This suite proves the new engine directly. It does not yet include every
independent, source-derived identity that remains in the legacy Galaga test
directory.

## Priority 1: port complete numeric source suites

These files are almost entirely mathematical conformance tests. Port their
tests into `tests/core`, preserving their source-oriented filenames and
theorem references.

### `test_chisolm_foundations.py`

Destination: `core/test_chisolm_foundations.py`.

Port all test classes:

- `TestAxiom4VectorSquareIsScalar`;
- `TestSymmetrizedProduct`;
- `TestGPDecomposition`;
- `TestThm2OuterProductDependence`;
- `TestThm3BladeSubspace`;
- `TestThm4SameSubspaceScalarMultiple`;
- `TestThm1OrthogonalWedgeEqualsGP`;
- `TestThm5OrthogonalityViaContraction`; and
- `TestVectorInverse`.

Adaptation requirements:

- use explicit core operations;
- replace member `scalar_part` access with checked scalar conversion or
  `float(grade(value, 0))`, according to what the theorem asserts; and
- retain degenerate PGA cases only where the theorem's invertibility
  assumptions hold.

### `test_chisolm_products.py`

Destination: `core/test_chisolm_products.py`.

Port every class. The file provides independent coverage for grade behavior,
outer associativity, contraction/wedge identities, product decompositions, and
the symmetry or antisymmetry rules of explicit inner products.

Adaptation requirements:

- spell each inner product or contraction explicitly;
- do not introduce a generic `ip` adapter in core tests; and
- add an oblique Gram case to identities not restricted to orthogonal bases.

### `test_chisolm_involutions.py`

Destination: `core/test_chisolm_involutions.py`.

Port every class. This suite covers grade involution, reversion, Clifford
conjugation, scalar products, versor inverses, blade squares, and norm
identities.

Adaptation requirements:

- treat scalar-coefficient extraction separately from checked `float(value)`;
- make invertibility preconditions explicit; and
- keep the cyclic scalar-part and exchange identities as independent oracles
  even if lower-level involution tests already exist.

### `test_chisolm_dual_commutator.py`

Destination: `core/test_chisolm_dual_commutator.py`.

Port every class. This is important independent coverage for dual/product
relations, pseudoscalar commutation, the commutator Leibniz rule, the Jacobi
identity, grade preservation, and bivector closure.

Adaptation requirements:

- use the unscaled `commutator` or `lie_bracket` consistently;
- use `half_commutator` only when the cited equation truly includes one half;
- state nondegeneracy assumptions for metric duals; and
- retain hand-computed sign cases rather than relying only on self-consistency.

### `test_cohoe.py`

Destination: `core/test_cohoe.py`.

Port every class. These tests cover generalized product identities,
contraction nilpotency and involution behavior, grade projections, scalar
products, versor norms, and sandwich distribution.

Adaptation requirements:

- keep the paper theorem references and deterministic seeds;
- use core multivector construction for random coefficient arrays; and
- extend applicable identities to an oblique positive-definite Gram matrix.

### `test_terathon_layer.py`

Destination: merge into `core/test_metric_rga.py` or split into
`core/test_terathon_identities.py` if the source provenance is clearer that
way.

Port the mathematical cases from:

- `TestExtendedMetricMatrix`;
- `TestMetricInnerProduct`;
- `TestLeftComplement`;
- `TestMetricAntiexomorphismMatrix`;
- `TestMetricApplyAntimetricApply`;
- `TestAntidotProduct`;
- `TestHodgeDuals`;
- `TestAntiwedge`;
- `TestAntireverse`;
- `TestGeometricAntiproduct`;
- `TestTranswedge`; and
- `TestBulkWeightDuals`.

Exceptions:

- the assertion that `antiwedge` is the same Python function object as
  `regressive_product` is an alias contract and belongs in compatibility
  tests; and
- any assertion about a legacy private matrix or table must be rewritten
  against public core metric matrices or the defining identity.

Much of this file overlaps the current exhaustive RGA core suite. Preserve
tests that add hand-computed examples, source-derived formulas, domain errors,
or a genuinely independent oracle; merge or remove exact duplicates.

## Priority 2: split mixed mathematical suites

### `test_chisolm_transformations.py`

This file must split between core identities and facade helpers.

Port to core, using `exp`, `sandwich`, `inverse`, and explicit products:

- the purely algebraic portions of `TestEq324ReflectionInSubspace`;
- `TestEq328ReflectionOfPseudoscalar`;
- `TestEq330RotationFormula`;
- `TestRotationLeavesIAlone`;
- the exponential and rotor-law portions of `TestRotorProperties`;
- `TestCl2ComplexStructure`;
- `TestCl3QuaternionStructure`;
- `TestCl3CrossProductDuality`; and
- `TestHyperbolicRotorSTA`.

Keep in a facade/helper suite:

- `TestThm15ProjPlusRejEqualsOriginal`;
- `TestProjectionLiesInSubspace`;
- `TestRejectionIsOrthogonal`;
- `TestEq322ReflectionPreservesInnerProduct` when it calls the `reflect`
  helper;
- `TestEq128ReflectionFormula`, which validates `reflect` against its defining
  composition;
- helper-dependent portions of `TestEq324ReflectionInSubspace`; and
- the double-`reflect` convenience test in `TestRotorProperties`.

The helper suite should prove equality with compositions of core primitives;
the core should not gain dedicated `project`, `reject`, `reflect`, or rotor
constructor algorithms merely to host these tests.

### `test_low_dim.py`

Destination for numeric cases: `core/test_low_dim.py`.

Port:

- numeric construction and operations from `TestCl0`;
- numeric construction, inverse, duality, exponential, logarithm, norm, and
  predicates from `TestCl1`;
- product, duality, exponential, logarithm, sandwich, and pseudoscalar cases
  from `TestCl2`;
- all of `TestCl01`; and
- all of `TestCl001`.

Keep above core:

- `Algebra.rotor` validation cases;
- `project`, `reject`, and `reflect` helper cases; and
- all `TestPseudoscalarLazy` cases, rewritten later as expression-provenance
  factory tests without the `lazy` vocabulary.

### `test_ga.py`

This large file should be dismantled rather than moved intact.

Port or merge into core:

- the numeric constructor, validation, dimension, metadata, and coefficient
  factory cases from `TestAlgebra`;
- unique numeric arithmetic and integer-power cases from `TestMultivector`;
- `TestGeometricProduct`;
- `TestOuterProduct`;
- `TestContractions`;
- `TestUnaryOps`;
- `TestGradeOps`;
- `TestDualNormInverse`;
- `TestGeneralInverse`;
- `TestPredicates`;
- `TestGoldenCl2`;
- `TestGoldenCl3`;
- `TestGoldenSTA`;
- `TestOuterTranscendentals`;
- `TestExpLog`;
- `TestExpNonSimpleBivector`;
- `TestExpGeneralInputs`;
- the numeric cases in `TestSqrt`; and
- the numeric cases in `TestScalarSqrt`.

Before porting, compare each case with the existing core suite. Keep unique
golden values, independent Taylor-series oracles, random non-simple inputs,
edge dimensions, and distinct error domains. Merge trivial duplicates into
table-driven existing tests.

Do not port directly to core:

- blade convention, `locals`, signed lookup, display-name, `repr`, `format`,
  and LaTeX portions of `TestAlgebra` or `TestMultivector`;
- the `_mul_sign` equality assertion, which must become a public product parity
  test;
- `lazy` or `symbolic` cases;
- `TestAliases`, which belongs to compatibility;
- `TestProjectReject` and `TestReflect`, which belong to facade helpers;
- the lazy case in `TestSqrt`;
- `TestScalarSqrtSymbolic`; and
- `TestNearUnitCoefficientSuppression`, which belongs to rendering.

The facade still needs smaller contract cases for construction forms,
operators, coercion, algebra mismatch, and wrapped result identity. Those are
not a reason to retain all numeric calculations in a monolithic facade file.

### `test_quaternion.py`

Port to core using explicit Euclidean basis bivectors:

- `TestQuaternionIdentities`;
- the mathematical `i² = -1` case from `TestComplexFactory`;
- complex multiplication; and
- reverse acting as conjugation in the even subalgebra.

Keep in blade/preset/presentation tests:

- `TestQuaternionSigns`;
- `TestQuaternionDisplay`;
- `TestQuaternionBladeLookup`;
- `TestQuaternionVectorNames`;
- factory name mappings; and
- all string and LaTeX assertions.

The core tests prove the `Cl(3, 0)` and `Cl(2, 0)` subalgebra facts. The outer
tests prove that the quaternion and complex presets attach the intended names
and signed aliases to those facts.

### `test_rga_convention_layer.py`

Port to `core/test_metric_rga.py` or a source-oriented companion file:

- `test_metric_and_antimetric_diagonals_are_derived_from_signature`;
- `test_metric_pairing_matches_direct_compound_metric`;
- `test_left_and_right_complement_source_identities_exhaustively`;
- `test_antidot_basis_table_is_computed_from_absent_metric_dimensions`;
- `test_hodge_dual_wedge_pairings_and_double_duals`;
- `test_weight_duals_match_antiproduct_identity_and_double_dual`;
- `test_antiwedge_and_geometric_antiproduct_basis_identities`;
- `test_antireverse_sign_on_every_basis_blade`;
- both exhaustive transwedge reconstruction tests;
- transwedge order validation;
- `test_interior_products_match_dot_and_vector_gp_decompositions`;
- the numeric kernel of the antivector-square, coordinate-meet, bulk/weight,
  source-dual, antiproduct-sandwich, and reversed-join examples.

The named RGA examples should be represented in core by explicit bitmasks or
coefficient arrays. Keep a second, smaller facade/preset assertion that each
semantic RGA role resolves to the same numeric value.

Keep above core:

- `test_rga_basis_metric_orientation_names_and_display_order` as a split
  preset and rendering contract;
- named role lookup and local-name parts of the projective examples;
- `test_rga_operations_preserve_symbolic_trees_values_and_grades` as facade
  expression propagation;
- `test_lengyel_notation_rendering_snapshot` as notation/rendering; and
- `test_binary_rga_operations_reject_mixed_algebras` as a facade wrapping
  contract, with smaller direct core mismatch coverage kept in core.

## Priority 3: extract unique numeric cases from coverage files

Coverage-oriented files should not be copied wholesale. Their organization is
an artifact of a coverage campaign, not a useful ownership boundary.

### `test_coverage.py`

Audit and merge unique numeric cases from:

- `TestAlgebraProperties`;
- `TestMultivectorConvenience`;
- `TestCommutatorAnticommutator`;
- `TestEvenOddSquared`;
- `TestIsRotor`;
- `TestFloatConversion`;
- `TestSandwich`;
- `TestScalarVectorPart`; and
- `TestComplement`.

Also inspect the numeric portions of `TestRemainingAlgebraGaps` and
`TestCoverageGaps`, but retain a case only when it states a meaningful public
contract or regression. Do not move a test whose only purpose is to execute a
branch already covered by a stronger core contract.

Keep outside core:

- naming and preset cases;
- `TestIpFunction` and aliases as compatibility policy;
- all symbolic and grade-propagation metadata cases;
- rotor-constructor helpers;
- LaTeX, simplification, and display cases; and
- architectural assertions about outer Galaga modules.

### `test_coverage_gaps.py`

Do not move the file. Extract only meaningful protocol cases:

- direct-core unsupported reverse division, if not already covered in
  `core/test_public_contracts.py`;
- direct-core dual domain behavior, if its exception contract is intentionally
  public; and
- numeric factory behavior that does not depend on a blade preset.

Lazy blades, display results, gamma preset behavior, display mode, and symbolic
aliases remain outer-layer concerns.

### `test_redesign.py`

Do not move the file. Most of it documents the legacy mutable symbolic and
display design that v2 is replacing.

Compare these groups with existing core coverage and extract only unique
numeric regressions:

- `TestMVDivision`;
- `TestIsBlade`;
- the mathematical kernel of `TestRegressiveProduct`; and
- numeric operator cases embedded in `TestAdditionalCoverage` or
  `TestCoverageGaps`.

Keep their wrapper behavior in facade tests. Keep all naming, basis protection,
lazy/symbolic propagation, expression nodes, rendering, reveal, display, and
copy behavior above core, rewritten to the immutable v2 contract rather than
preserved mechanically.

## Files that should not move to numeric core

These files are wholly, or overwhelmingly, owned above the core:

| File | Correct owner |
|---|---|
| `test_blade_convention.py` | blade conventions and presets |
| `test_display_order.py` | presentation and rendering |
| `test_example_notebooks.py` | examples and integration |
| `test_examples.py` | example source policy |
| `test_gram_bridge.py` | facade catalog, wrapping, and direct-core parity |
| `test_latex_build.py` | semantic LaTeX pipeline |
| `test_latex_symbols.py` | symbol rendering |
| `test_latex_tree.py` | LaTeX tree and rewrites |
| `test_notation.py` | notation and presentation |
| `test_precedence.py` | expression rendering precedence |
| `test_render.py` | rendering |
| `test_scalar_helpers.py` | facade constants and coefficient rendering |
| `test_symbolic.py` | legacy expression behavior and v2 migration input |
| `test_symbolic_core.py` | expression model, despite its historical name |

The current `test_symbolic_core.py` is not a numeric-core test. Its module name
means “core of the symbolic layer”; v2 should move it under `tests/expression`
to remove that ambiguity.

## Facade contract tests retained after migration

After numeric identities move to core, the facade should still test:

- every accepted public algebra construction form;
- wrapping and unwrapping identity;
- scalar coercion and every Python operator binding;
- algebra mismatch and unsupported-operand behavior;
- exact equality, hashing, approximate comparison, checked `float`, and
  read-only coefficient access;
- one representative value per product family and metric class;
- every operation catalog entry through table-driven direct-core parity;
- variadic lowering and numeric invocation counts;
- optional name and expression state propagation; and
- absence of expression allocation on the numeric-only path.

These tests should use the required matrix from the cutover plan, but they do
not need to repeat every Chisholm, Cohoe, Terathon, exponential, or low-
dimensional identity already proved directly against the core.

## Migration work units

### T1 Port source-derived identity suites

Scope:

- four Chisholm numeric files;
- Cohoe; and
- nonduplicated Terathon identities.

Validation:

```bash
uv run --python 3.11 pytest packages/galaga/tests/core/test_chisolm_foundations.py -q
uv run --python 3.11 pytest packages/galaga/tests/core/test_chisolm_products.py -q
uv run --python 3.11 pytest packages/galaga/tests/core/test_chisolm_involutions.py -q
uv run --python 3.11 pytest packages/galaga/tests/core/test_chisolm_dual_commutator.py -q
uv run --python 3.11 pytest packages/galaga/tests/core/test_cohoe.py -q
uv run --python 3.11 pytest packages/galaga/tests/core -q
```

Exit condition:

- every source theorem runs directly on `galaga.core`;
- no ported file imports top-level `galaga.Algebra` or legacy `Multivector`;
  and
- overlaps have been merged without losing independent oracles.

### T2 Split the large mixed suites

Scope:

- `test_ga.py`;
- `test_low_dim.py`;
- `test_chisolm_transformations.py`;
- `test_quaternion.py`; and
- `test_rga_convention_layer.py`.

Validation:

- run the new core files;
- run the retained facade/helper/presentation files;
- run the entire original source files until all of their cases have a new
  owner; and
- compare collected test IDs with the checked migration inventory.

Exit condition:

- every original class or function has a recorded destination;
- no mathematical identity depends on names or rendering merely to create its
  operands; and
- no helper has been added to core solely to make a legacy test fit.

### T3 Consolidate coverage-driven regressions

Scope:

- `test_coverage.py`;
- `test_coverage_gaps.py`; and
- numeric fragments of `test_redesign.py`.

Validation:

- branch coverage does not decrease unintentionally;
- every retained test has a behavioral name and clear owner; and
- deletion of a duplicate is supported by the stronger destination test.

Exit condition:

- no generic “coverage gap” file is treated as a permanent numeric-core
  specification; and
- unique historical regressions have not been lost.

### T4 Parameterize the public numeric contract over the facade

After the core ports pass, run the implementation-neutral public numeric
contract against the facade. This is the evidence required by Phase 3 of the
cutover plan.

Validation:

- collected test IDs visibly include the facade implementation;
- all applicable public numeric behavior passes;
- v2 corrections have explicit alternative expectations; and
- no test claims facade coverage while still constructing a legacy value.

### T5 Remove legacy-only numeric tests

Delete legacy-only duplicates only after T1 through T4 pass and the facade-only
shadow suite can fail on any legacy constructor call.

Validation:

- the full suite passes with the legacy execution guard;
- source references and theorem citations remain in their core tests;
- coverage is measured against `galaga.core` and the facade separately; and
- repository searches find no numeric test importing the private legacy
  implementation.
