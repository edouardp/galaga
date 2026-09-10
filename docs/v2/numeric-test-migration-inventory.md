# Numeric Test Migration Inventory

This is a historical migration inventory and delivery log. Migration and
physical engine deletion are complete; references below to files still
shipping describe intermediate checkpoints. The
[cutover plan](core-cutover-plan.md) and [release report](legacy-engine-deletion-gate.md)
record the current position.

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

Canonical naming follows ADR-074. A first port may bind a canonical import to
the source file's old local name to isolate numeric migration. Canonicalizing
the destination is a separate syntax-aware change. Brackets, inner products,
scalar extraction, and facade helpers always require manual semantic review.

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
| `test_numeric_formatting.py` | concrete display policies and semantic format hooks |
| `test_example_notebooks.py` | examples and integration |
| `test_examples.py` | example source policy |
| `facade/test_numeric_facade.py` | facade catalog, wrapping, and direct-core parity |
| `test_latex_build.py` | semantic LaTeX pipeline |
| `test_latex_symbols.py` | bounded symbol conversion and immutable presentation names |
| `test_latex_tree.py` | LaTeX tree and rewrites |
| `test_notation.py` | immutable operation-ID notation, configured rendering, and teaching layouts |
| `test_numeric_function_expressions.py` | eager facade functions and replayable expression provenance |
| `test_precedence.py` | expression rendering precedence |
| `test_render.py` | rendering |
| `test_scalar_helpers.py` | facade constants and coefficient rendering |
| `test_symbolic.py` | facade named-value, replay, bracket, and structural simplification contracts |
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

Status: **complete (2026-07-18)**.

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

Completion evidence:

- all four Chisolm suites and the Cohoe suite now run from their
  source-oriented filenames under `packages/galaga/tests/core`;
- executable uses of `gp`, `op`, and `involute` were converted with the
  LibCST-based `tools.canonicalize_core_test_operations` codemod, whose tests
  prove that comments, strings, local names, and convention-sensitive bracket
  aliases are not rewritten;
- Chisolm's half-scaled commutator equations explicitly call
  `half_commutator`; Galaga's unscaled `commutator` and `lie_bracket` semantics
  are not substituted into those source formulas;
- source scalar parts are expressed as `scalar_product` when the theorem says
  $a\mathbin{\cdot}b$, as checked `float(value)` when the result must itself be
  scalar, and as `float(grade(value, 0))` only when extracting grade zero from
  a potentially mixed-grade value;
- the Chisolm product and Cohoe suites include an oblique positive-definite
  Gram matrix, and Cohoe's vector pairing oracle is the independent
  $a^T G b$ formula rather than a diagonal-signature sum; and
- the nonduplicated Terathon oracles were merged into
  `core/test_metric_rga.py`: Hodge dual via $\widetilde{A}I$, the antireverse
  grade-sign formula, geometric-antiproduct De Morgan identity, and the direct
  antimetric definitions of both weight duals. Existing exhaustive tests
  already subsume the remaining mathematical cases across Euclidean,
  indefinite, degenerate, and oblique metrics.

The original facade suites remain in place until T1 through T4 and their
facade-contract replacements pass, as required by the deletion gate below.

### T2 Split the large mixed suites

Status: **complete (2026-07-18)**.

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

Completion crosswalk:

| Legacy source | Direct-core owner | Retained outer-layer owner |
|---|---|---|
| `test_chisolm_transformations.py` | Primitive reflection, rotation, rotor-law, cross-product, and boost identities in `core/test_chisolm_transformations.py`; complex and quaternion subalgebras in `core/test_quaternion.py` | Projection, rejection, `reflect`, double-reflection, and rotor-constructor helper contracts remain in the source facade suite |
| `test_low_dim.py` | Compact source-oriented boundary cases in `core/test_low_dim.py`, with stronger inverse and function coverage in `core/test_numeric_api.py` and `core/test_numeric_functions.py` | Rotor-constructor validation, projection/rejection/reflection helpers, and pseudoscalar expression provenance remain above core |
| `test_quaternion.py` | Hamilton identities, complex multiplication, and reverse-as-conjugation in `core/test_quaternion.py` | Blade signs, semantic names, lookup, rendering, and custom vector-name contracts remain in preset/presentation tests |
| `test_rga_convention_layer.py` | Exhaustive operations and unnamed source-table kernels in `core/test_metric_rga.py` | RGA semantic roles, notation snapshots, expression propagation, and facade mismatch wrapping remain above core |
| `test_ga.py` | Construction in `core/test_algebra.py`; representation and laws in `core/test_multivector.py`; explicit products and protocols in `core/test_backends.py`, `core/test_numeric_api.py`, and `core/test_public_contracts.py`; functions in `core/test_numeric_functions.py`; golden low-dimensional cases in the new source-oriented files | `TestAliases`, helpers, symbolic square root, and near-unit rendering remain compatibility, helper, expression, and rendering concerns respectively |

The `test_ga.py` comparison retained two independent regressions that were
stronger than the existing destinations: a direct unscaled Taylor-series
oracle for nonsimple, mixed-grade, oblique, and random geometric
exponentials, and two-sided inverse checks from dimension zero through six.
Trivial coefficient duplicates were not copied.

The direct-core exponential suite also owns the full acceptance matrix for
[GitHub issue 11](https://github.com/edouardp/galaga/issues/11): the explicit
grade-four cross term, commuting-plane factorization, Cl(4,1), STA and Cl(2,2)
compound rotors, a three-plane bivector, five deterministic random Cl(4,1)
bivectors, Taylor parity, and $R\widetilde{R}=1$. None of those regressions now
depends solely on the retained legacy `TestExpNonSimpleBivector` class.

No numeric test creates operands through a blade-name preset. RGA source
tables are derived from ordered wedges of unnamed basis vectors, quaternion
units are explicit Euclidean bivectors, and rotors are constructed with
`exp`; core gained no `project`, `reject`, `reflect`, or rotor-constructor
helper.

### T3 Consolidate coverage-driven regressions

Status: **complete (2026-07-18)**.

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

Completion evidence:

- `test_coverage.py` numeric contracts are already owned by
  `core/test_algebra.py`, `core/test_public_contracts.py`,
  `core/test_numeric_api.py`, and `core/test_metric_rga.py`; this includes
  unsupported Python operands, checked float conversion, full and half
  brackets, grade families, sandwiches, scalar/vector inspection, and
  complement laws;
- `test_coverage_gaps.py` adds no unique core mathematics: its dual-domain and
  reflected-division boundaries are already direct public-contract tests,
  while its remaining cases concern blade lookup, display, or symbolic
  aliases;
- `test_redesign.py` division and predicate kernels are covered in
  `core/test_numeric_api.py`, regressive identities in
  `core/test_metric_rga.py`, and the hyperbolic logarithm domain in
  `core/test_numeric_functions.py`; its other cases describe the outer
  expression, naming, rendering, and mutable legacy design; and
- no generic coverage-named test was copied. Each retained numeric regression
  has a behavioral owner, while duplicate branch-execution tests remain in
  the legacy suite only until the deletion gate.

The Python 3.11 direct-core coverage baseline after T1 through T3 is 98% with
branch measurement: 697 tests passed and 19 were skipped; `_backends.py`,
`_metadata.py`, and `_metric.py` each report 100%, while the public core module
reports 97%. The remaining uncovered paths are defensive numerical-failure
guards, protocol fallbacks that are unreachable through normal reflected
dispatch, or diagnostic representation branches. T3 deliberately does not
add assertions whose only purpose is to raise that headline number.

### T4 Parameterize the public numeric contract over the facade

Status: **complete (2026-07-18)**.

After the core ports pass, run the implementation-neutral public numeric
contract against the facade. This is the evidence required by Phase 3 of the
cutover plan.

The following records the original overlap checkpoint. Its live v1 adapter
has since been retired by the
[Phase 9 follow-through](#phase-9-follow-through-shared-numeric-contract).

Validation:

- collected test IDs visibly include the facade implementation;
- all applicable public numeric behavior passes;
- v2 corrections have explicit alternative expectations; and
- no test claims facade coverage while still constructing a legacy value.

Completion evidence:

- `facade/test_numeric_contract.py` defines one construction adapter and runs
  the same public contracts with collected IDs ending in `[legacy-v1]` and
  `[core-facade-v2]`; facade cases always construct
  `galaga.facade.Algebra`, never a legacy value hidden behind a fixture;
- the shared contract covers algebra construction, factories, Python
  operators, checked scalar conversion, grade families, named products,
  involutions, dualities, inverse, predicates, norms, exponential,
  logarithm, square root, and outer functions without reaching through
  `.numeric`;
- separate correction-ledger assertions record full Galaga 2 Lie and Jordan
  products versus the legacy half-scaled meanings, immutable versus mutable
  coefficient storage, exact versus approximate equality, and the optional
  standalone `scalar_part` helper instead of a facade member;
- four deterministic mixed-grade differential cases cover Cl(2,0), Cl(1,2),
  Cl(2,0,1), and Cl(4,0), comparing the facade with retained v1 diagonal
  behavior for products, metric and antimetric operations, grade selection,
  involutions, complements, and valid dualities;
- the facade now exports a catalog-backed wrapper for every canonical numeric
  operation. A completeness assertion compares those callables with the
  immutable operation catalog, so adding a catalog entry without exposing it
  fails the suite; and
- `facade/test_numeric_facade.py` reserves `.numeric` for its stated direct-core parity
  purpose. It checks every operation family on an oblique Gram matrix and
  verifies that inverse, unit, logarithm, and square-root domain errors retain
  the direct core exception and message; and
- the public-boundary pass exposed and fixed one facade defect: division by a
  zero scalar multivector now preserves the core `ZeroDivisionError` contract
  instead of falling through general inverse and raising `ValueError`.

The Python 3.11 T4 run collected 22 implementation-neutral contract tests and
95 direct facade and boundary tests; all 117 passed. Separate branch coverage
was 98% for both the transitional facade package and its implementation. The remaining
lines are defensive guards for a misconfigured fold policy, duplicate catalog
construction, invalid private wrapping, unreachable reflected multivector
dispatch, or a core value returned without any facade owner; no test was added
merely to force those internal guards. This completes T4, but it does not by
itself satisfy the Phase 3 deletion gate: the facade-only legacy-execution
guard and removal of redundant legacy numeric tests remain T5 work.

### T5 Remove legacy-only numeric tests

Status: **complete (2026-07-18)**.

Delete legacy-only duplicates only after T1 through T4 pass and the facade-only
shadow suite can fail on any legacy constructor call.

Validation:

- the full suite passes with the legacy execution guard;
- source references and theorem citations remain in their core tests;
- coverage is measured against `galaga.core` and the facade separately; and
- repository searches find no numeric test importing the private legacy
  implementation.

Completion evidence:

- the wholly numeric legacy Chisholm foundations, products, involutions, and
  dual/commutator files, plus the Cohoe and Terathon files, were deleted after
  their direct-core destinations passed;
- mixed Chisholm transformations, low-dimensional, quaternion, and RGA files
  now retain only helper, naming, presentation, expression, or facade-wrapping
  contracts. Their mathematical kernels remain in behaviorally named core
  files with their source references and theorem citations;
- the monolithic `test_ga.py` was replaced by focused local-name, numeric
  formatting, and numeric-function expression-provenance tests. Compatibility
  aliases, including the exact v1 `meet`, `join`, and `antiwedge` identities,
  now have an explicit `tests/compatibility` owner;
- the numeric-only classes and methods in `test_coverage.py`,
  `test_coverage_gaps.py`, and `test_redesign.py` were removed. Blade lookup,
  degenerate-signature rendering, and symbolic `norm2` rendering were first
  retained in focused outer-layer files; rotor constructors and all symbolic,
  notation, rendering, and mutable-v1 presentation contracts remain above
  core;
- all direct facade tests in `facade/test_numeric_facade.py` monkeypatch the private legacy
  constructor to fail immediately. The same guard is installed for every
  `core-facade-v2` invocation of the implementation-neutral shared contract,
  and an explicit self-test proves that the guard trips, so a facade fallback
  to v1 cannot pass the shadow suite unnoticed;
- the only remaining test imports from `galaga.algebra` are deliberately
  classified: the differential contract imports the v1 oracle explicitly,
  the facade guard imports it only to disable construction, and the other
  imports inspect legacy expression or rendering implementation details. No
  direct-core numeric specification imports the private legacy engine; and
- Python 3.11 validation passed with 697 direct-core tests and 19 skips at 98%
  branch coverage, and 118 facade/boundary tests at 98% branch coverage. The
  complete Galaga suite passed with 2,327 tests and 19 skips; all non-marimo
  packages passed with 2,701 tests and 19 skips (one existing complex-cast
  warning); and the Python 3.14 marimo suite passed all 91 tests.

The lower aggregate test count is intentional: it reflects removal of
duplicate executions of the retired v1 numeric engine, not removal of the
mathematical contracts. Those contracts are now owned once by direct-core
tests, exercised through the guarded facade contract, and supplemented by
explicit v1/v2 differential and correction-ledger cases.

### Phase 9 follow-through: configured rendering

The exact compound, STA, and RGA rendering suites now execute only through the
facade and have left the legacy-construction ledger. All expression bodies,
source citations, 34 facade full-LaTeX cases, 26 three-channel RGA notation
entries, and 16 RGA blade entries remain live. Their pre-retirement v1 outputs
are archived as development data under
[ADR-084](../adrs/084-exact-configured-rendering-contracts.md).

The new boundary suite also checks all 32 compound numeric samples against
captured coefficients after algebraically deriving the semantic exterior
basis transport; the 26 RGA operation samples retain numeric checks too.
These are retained representative regressions, not replacements for the
source-derived core identities above. Fresh-process execution blocks legacy
imports throughout the three exact suites. At that checkpoint, twenty other
files remained in the legacy ledger; it retired the exact suites'
rendering-adapter dependency, not the engine.

### Phase 9 follow-through: shared numeric contract

The seven public numeric protocol tests now construct the facade directly;
their v1 execution and construction adapter are removed. The catalogue export
gate and explicit v2 correction tests remain. All 146 original seeded operation
results are preserved in `tools/baselines/numeric-contract-v1.json`, with the
four signatures, seeds, explicit inputs, and capture provenance. Each result is
now a separate regression case, so the increased collected count is improved
failure granularity rather than 146 newly invented mathematical requirements.

Both default facade and forced core-reference results must match the captured
observations independently. Additional checks derive products, reverse signs,
and corrected bracket scaling from left actions or exterior grades. The
singular duality boundary, immutable data, and exact equality remain explicit
contracts. Corruption tests cover matching wrong results in both current
paths, jointly mis-scaled aliases, wrong shapes, nonfinite data, and the
retained numerical tolerances.

The contract leaves the legacy ledger, which now has nineteen files. A fresh
process runs the whole contract with legacy imports blocked. No production
arithmetic or value semantics change in this checkpoint; the hash inconsistency
found during boundary review was recorded separately as the next release
blocker. See [ADR-094](../adrs/094-numeric-contracts-outlive-the-legacy-engine.md).
The subsequent [ADR-095](../adrs/095-exact-numeric-equality-and-compatible-hashes.md)
correction resolves that blocker with dedicated core and facade regressions;
it does not change the nineteen-file legacy ledger.

### Phase 9 follow-through: compatibility-manifest introspection

The v1 surface manifest no longer imports legacy classes or expression nodes
to prove completeness. `tools/baselines/public-surface-v1.json` preserves the
observed exports, public members, declared protocols, formatting hooks,
constructor parameters, expression classes, and transitional module inventory
with source and environment provenance. Historical names still require exact
disposition coverage; malformed or duplicate observations are rejected.

The complete `SUBMODULE_DISPOSITIONS` ledger is separate from the 15 live
`SUPPORTED_SUBMODULES` and 21 `LEGACY_ONLY_SUBMODULES`. Current constructor,
protocol, formatting, namespace, alias, warning, and removal contracts remain
live. Package files retain non-importing presence and classification checks
until the explicit engine deletion, so retiring an import test cannot conceal
an unclassified file. Current namespace and constructor guards outside this
contract remain later work.

A fresh process runs the entire surface and deprecation contracts with all
legacy implementation imports forbidden. Mutation tests prove that historical
disposition drift, broken v2 methods, namespace changes, malformed archives,
module partition errors, and file-inventory drift fail. The compatibility
suite passes 144 tests; the manifest and new contract guards have 100% line
and branch coverage in the full Python 3.11 run. The numeric-construction
ledger remains at nineteen files because this manifest only introspected v1
and was never ledgered for construction. No production behavior changes.
See [ADR-096](../adrs/096-compatibility-manifests-use-historical-api-evidence.md).

### Phase 9 follow-through: concrete display ordering and numeric formatting

`test_display_order.py` and `test_numeric_formatting.py` now use the public
facade and leave the constructor-exemption ledger, reducing it from nineteen
files to seventeen. Their former 25 tests are replaced by current contracts
for permutation validation, target-specific term order, significant-digit
precision, native basis enumeration, repr, semantic format hooks, and
near-unit display. Scoped order is also checked against Euclidean, degenerate,
oblique, and native-null metrics without changing numeric values or provenance.

`tools/baselines/concrete-display-v1.json` records eleven sample values with
coefficients and four rendering observations each, six fixed-decimal outputs,
three algebra repr outputs, resolved orders, all quaternion basis grades, and
seven quaternion products. Live samples are recomputed from public operations
before comparing coefficients and each visible target. Old default grade
grouping is reproduced explicitly rather than imposed on v2's native default;
quaternion products also have public left-action checks.

Existing v2 differences are retained and documented, not hidden as parity:
`basis_blades(2)` enumerates quaternion masks as `k, j, i`; semantic roles
select `i, j, k`. V2 multivector format specs select content/target, and
`DisplayPolicy` counts significant digits without fixed-decimal padding.
Numeric specs such as `.3f` are currently unsupported. Multivector repr is
ASCII and algebra repr is diagnostic. No production implementation changed.

Fresh-process tests forbid legacy imports while running both entire suites.
Mutation tests reject incorrect rotor results and rendered strings independently;
shape, nonfinite-data, and coefficient-drift checks protect the numeric archive
comparison. All 101 cases across the two suites and their archive/boundary
tests pass with 100% line and branch coverage in the focused Python 3.11 run.
See [ADR-097](../adrs/097-concrete-display-contracts-outlive-legacy-rendering.md).

### Phase 9 follow-through: numeric-function provenance and grouping

`test_numeric_function_expressions.py` and `test_precedence.py` now use the
public facade and leave the construction ledger, reducing it from seventeen
files to fifteen. All 29 original scenarios survive in
`tools/baselines/expression-contracts-v1.json`, with explicit inputs,
coefficients, formatted outputs, and capture provenance.

The 25 grouping recipes each have exact ASCII, Unicode, and LaTeX contracts,
independent historical coefficient checks, explicit replay checks, and
rendering immutability checks. The four numeric-function cases retain rotor
roots, scalar roots, named compound energy, and squared-norm notation.
Additional cases cover all four name/tracking states, eager negative-root
errors, environment substitution, and Gram-derived elliptic, nilpotent,
oblique, and native-null rotor roots with default and custom tolerances.

Existing spelling and display-policy differences are documented separately
from numerical agreement. Unit normalization and grade involution retain
their conventional shared hat; functional notation disambiguates them.
No production behavior changes, and the larger symbol-parser, notation, and
mixed expression suites remain separate work.

All 131 cases across the two suites and their archive/boundary gates pass
with 100% line and branch coverage in a focused Python 3.11 run.
Fresh-process checks prohibit legacy imports, while corruption tests reject
wrong eager values, replay values, or rendered grouping independently.
See [ADR-098](../adrs/098-expression-contracts-outlive-legacy-provenance.md).

### Phase 9 follow-through: symbolic contracts and unary conveniences

The remaining `test_symbolic.py` suite now uses only the public facade,
reducing the construction ledger from fifteen files to fourteen. Its 57
legacy tests covered named rendering, replay, numeric-only fallback, unary
properties, bracket scaling, and simplification. Those responsibilities now
have exact public contracts backed by 36 representative v1 value observations,
eight nonzero tracked/untracked bracket probes, and two historical
simplification observations in `tools/baselines/symbolic-contracts-v1.json`.

Migration exposed the missing curated `bar`, `dag`, `inv`, and `sq`
properties. They are now read-only delegates to the ledgered canonical
functions, with no new core arithmetic or expression IDs. Independent
grade-sign, left-action, and linear-solve checks cover all four
name/tracking states across four metric families. The live surface contract
also verifies their implementation, rather than only their classification.

V1's half-scaled Lie/Jordan products remain historical evidence; v2's
unscaled definitions and explicit half operations are checked independently.
Nonzero probes and mixed-grade examples prevent vacuous scaling tests or an
unsafe Jordan-to-inner rewrite. Production simplification and rendering do
not change.

The symbolic, unary-property, and boundary suites pass 322 tests at 100%
line and branch coverage in the focused Python 3.11 run. Both public suites
also pass all 305 tests when importing Galaga directly from the built wheel,
with legacy imports prohibited and package origins verified. The archive
and test utilities remain outside the wheel.
See [ADR-099](../adrs/099-symbolic-contracts-and-curated-unary-properties.md).

### Phase 9 follow-through: explicit symbol conversion

`test_latex_symbols.py` now imports `galaga.names.LatexSymbols`.
All 108 original test identifiers and valid literal mappings remain; only
the canonical import and final naming integration change. The integration
uses the facade with `Name.from_latex`, removing this file from the legacy
construction ledger and reducing the count from fourteen to thirteen.

This migration preserves conversion, not just already-supplied spellings.
The converter has one private, standard-library-only implementation, with a
temporary same-object re-export at the old path. The opt-in name factory
derives supported spellings and requires explicit ASCII fallback for unknown
TeX; ordinary `Name` and `named` semantics remain unchanged.

Regression probes demonstrated wrong lowercase script/double-struck offsets,
unassigned codepoints, and even emoji from Unicode input treated as Latin.
Independent Unicode-name checks now cover all 260 font letters and all 50
font/digit pairs; six accent tests each exercise every ASCII letter and
digit. Malformed input, exact matching, override validation, and fallback
rules are covered. Gram-derived products across four metric families check
that naming preserves numeric identity, equality, hashes, and replay.

The conversion and boundary suites pass 543 tests; including the existing
`Name` configuration suite gives 556 focused cases and 100% line/branch
coverage in `Name`, the converter, and all three conversion-related test
files. All 540 public conversion cases also pass directly from the built
wheel with legacy imports prohibited and package origins verified.
The full Python 3.11 and 3.14 package/release suites pass 5,092 and 5,209 tests
respectively, with only the existing complex-to-real matrix warning.
See [ADR-100](../adrs/100-explicit-bounded-latex-name-conversion.md).

### Phase 9 follow-through: immutable notation contracts

The 239 cases from `test_notation.py` now have public v2 owners. The
historical archive `tools/baselines/notation-contracts-v1.json` preserves
all 101 original method identifiers, 47 default rule families in three
targets, 28 functional value/rendering observations, normalization-fraction
examples, and scientific-style outputs with explicit inputs and provenance.

The live suite pins exact reviewed output for every default family and checks
functional values, replay, stable IDs, target overrides, immutable sharing,
and actual preset rendering. V1's mutable fields and class-name dispatch stay
historical. Existing unscaled brackets and functional-name changes remain
explicit. The old positive-square-vector logarithm is not accepted numeric
parity: its exponential fails to recover the input. A valid rotor probe
checks the v2 logarithm domain separately. V2 still has no configurable
`cdot`/`raw` scientific-number selector; that limitation is documented.

Two missing presentation responsibilities are implemented: opt-in
`RenderRule("unit_fraction")` builds existing fraction/wrapper nodes for
`unit` without numeric evaluation, and the Hestenes preset no longer
inherits a LaTeX tilde that shadows its dagger. Independent metric/grade-law
checks cover normalization, mixed grades, null/near-zero errors, tolerances,
and presentation/provenance invariance. The custom-notation notebook teaches
both capabilities with executable assertions.

The legacy construction ledger falls from thirteen files to twelve after
removing `test_notation.py`. Fresh-process tests prohibit all legacy imports.
The three focused suites pass 338 cases at 100% line/branch coverage;
their two public suites pass 324 cases directly from the built wheel.
The full package/release suites pass 5,192 cases on Python 3.11 and 5,309
on Python 3.14, including maintained notebook exports, with only the existing
complex-to-real conversion warning. Type checking remains at 296 errors.
See [ADR-101](../adrs/101-immutable-notation-contracts-and-unit-fraction-layout.md).

### Phase 9 follow-through: LaTeX pipeline contracts

`test_latex_build.py` now constructs public expressions and semantic
nodes rather than the old expression/build/rewrite/emission pipeline.
The historical archive `tools/baselines/latex-build-contracts-v1.json`
preserves all 112 original identifiers, complete method sources, and actual
helper-observed output with source commit and runtime provenance. Every
historical class has a checked live owner.

Regressions reproduced merged command prefixes, invalid double superscripts,
and ambiguous scripts on compound names. A bounded LaTeX emitter guard now
separates control words, protects existing scripts, and groups recognized
outer operators in names and scientific literals. It respects braces, escapes,
and script arguments without parsing arbitrary TeX or changing expression
precedence. Existing wide accents, floor contractions, fraction grouping,
constant folding, and unavailable scientific-style selectors remain explicit.

Independent Gram-determinant rotor/logarithm checks include an oblique metric;
complement is checked against the exterior-product law. Naming, expression
identity, numeric data, hashes, explicit replay, and missing-binding errors
remain live contracts. Corruption probes independently reject wrong numeric
values, replay, and display.

The construction ledger falls from twelve files to eleven. All 161 focused
cases pass with 100% line/branch coverage in the three test files; all new
emitter paths are covered, with overall emitter coverage increasing to 94%.
Fresh-process legacy-import bans pass, and the 154 public cases also pass
against the built wheel with verified package origins. Full package/release
suites pass 5,241 cases on Python 3.11 and 5,358 on Python 3.14, including
maintained notebook exports. Only the existing matrix complex-to-real warning
remains; type checking reports 295 errors, down from 296.
See [ADR-102](../adrs/102-latex-contracts-and-script-safe-spelling.md).

### Phase 9 follow-through: mixed rendering with numeric ownership

All 141 class/method identifiers from `test_render.py` remain live,
using public `Call`/`Symbol` expressions and immutable notation views.
`tools/baselines/render-contracts-v1.json` captures their complete method
sources and 143 observed renderings, each with the actual symbol bindings
and evaluated native-mask coefficients. Source commit and runtime provenance
are retained. The 54 changed expectations are existing v2 policies, not new
renderer changes; three permissive assertions are strengthened to exact output.

A companion numeric suite executes every original method using those archived
bindings. Its explicit Lie/Jordan factor-of-two correction is separately
checked with nonzero mixed grades, because the original orthogonal-vector
Jordan example was zero. Ten compositions cover brackets, division, products,
reversal, sandwiches, grade projection, squared sums, and negative addends
across Euclidean, oblique-indefinite, and native-null metrics in three targets.
Expected coefficients come from a forced core-reference backend, grade signs,
and linear solves before any naming or display. A wrong-side inverse is
explicitly distinguished from correct right division.

Eager values, replay, data, expression identity, hashes, and scoped notation
remain checked. Corruption probes reject old half scaling, wrong rendering
or replay, altered archive bindings/results, invalid shapes, and nonfinite
coefficients. Fresh-process tests prohibit all legacy imports.

The construction ledger falls from eleven files to ten. All 394 focused
cases pass at 100% line/branch coverage in the three test files. Their 378
public cases pass directly from the built wheel with package origins verified.
Full package/release suites pass 5,494 cases on Python 3.11 and 5,611 on
Python 3.14, including maintained notebook exports. Coverage remains 97%
for core/facade numeric modules and 94% for the emitter; the existing matrix
warning and 295 type errors remain. No production code or notebook content
changes. See
[ADR-103](../adrs/103-mixed-rendering-contracts-with-numeric-ownership.md).

### Phase 9 follow-through: blade conventions and metric-derived STA names

All 102 historical method identities and 107 collected cases in
`test_blade_convention.py` remain live against public immutable conventions
and facade values. The archive `tools/baselines/blade-convention-contracts-v1.json`
preserves every method source plus twelve complete v1 STA name/sign tables:
three ordered metrics and four option combinations, with source/runtime
provenance. The original literal STA tables remain in the public suite.

Restore opt-in `sigmas` and `pseudovectors` on `p_sta`/`SpacetimePreset`.
The standalone `spacetime_blade_convention` requires explicit ordered unit
basis squares for either option. A bounded word reduction derives signs;
it does not infer them from inertia or import the core into presentation.
Names describe actual products, with native gamma spellings retained as
positive-orientation aliases. New tests compute first across all sixteen
unit-diagonal sign patterns, then verify labels, lookup, rendering, local
bindings, replay, hashes, and numeric sharing.

Archive replay permits only the explicit ASCII pseudovector change from
`iy0` … `iy3` to `ig0` … `ig3`. Mutable renaming becomes immutable views or
scoped presentation; explicit names/masks replace tuple and metric-role
parsing. Repr, PGA basis order, and actual-null versus display-only CGA naming
retain established v2 policy. Corruption probes reject wrong signs, names,
masks, and the old unsigned sigma lookup.

All 739 presentation/blade tests pass. The four blade test files measure
100% line and branch coverage; both changed production modules measure 98%
with every new path covered. Fresh-process legacy-import gates pass, and
all 224 public blade cases pass directly from the wheel with package origins
verified. Full package/release suites pass 5,620 cases on Python 3.11 and
5,737 on Python 3.14, including maintained notebook exports. Existing
core/facade coverage, the matrix warning, and 295 type errors remain.

The construction notebook computes both time-first STA frames and teaches
signed lookup plus the general-Gram boundary. The construction-exemption
ledger falls from ten files to nine; RGA and mixed legacy ownership remain.
See [ADR-104](../adrs/104-metric-derived-sta-names-and-public-blade-contracts.md).

### Phase 9 follow-through: RGA conventions and under-accent fallback

The five original function identities and eleven cases in
`test_rga_convention_layer.py` now use public presets, signed blade references,
generic expressions, explicit replay, and immutable notation. The archive
`tools/baselines/rga-convention-contracts-v1.json` retains every source test,
twenty-six observed value/rendering cases, all sixteen oriented basis values,
and source/runtime provenance.

Eleven of the original sixteen operation samples evaluate to zero. Keep them,
but add nonzero mixed-grade inputs across standard RGA, oblique-indefinite,
and singular-oblique metrics. Derive coefficient expectations from Gram
minors, exterior permutations, grade signs, and the forced core-reference
product tensor, before naming or rendering. All three targets, replay, grades,
hashes, scoped notation, and transwedge orders zero through four remain live
contracts. Corruption probes reject swapped dual sides, antiproduct sign
errors, lost order parameters, and invalid archived coefficients/output.

Explicit v2 differences include native basis enumeration, signed names,
numeric zero's absent homogeneous grade, ASCII functional fallback, wide
reverse accents, floor contractions, and removal of legacy phantom padding.
The custom LaTeX under-accent fallback is a real fix: non-command annotations
now use `\underset`, while recognized one-argument commands and other targets
remain unchanged. Regression cases also preserve over-accent behavior.

All 300 focused cases pass at 100% line and branch coverage in the four test
files. All 288 public cases pass from the wheel with origins verified and
legacy imports blocked. Every new emitter path is covered; its full-suite
coverage rises from 94% to 95%. Full package/release runs pass 5,910 cases on
Python 3.11 and 6,027 on Python 3.14, including maintained notebook exports.
Core/facade coverage, the existing matrix warning, and 295 type errors remain.

The RGA notebook teaches the signed-mask, numeric-zero, and under-accent
boundaries with computed examples. The construction ledger falls from nine
files to eight. Locals/naming and mixed legacy dependencies remain.
See [ADR-105](../adrs/105-public-rga-contracts-and-underaccent-fallback.md).

### Phase 9 follow-through: independent local-name contracts

All eleven original function identities and twelve cases in `test_locals.py`
now use the public facade. The archive `tools/baselines/locals-contracts-v1.json`
retains the complete source and digest, eleven ordered binding tables with
coefficients and Unicode values, historical STA basis enumeration, scalar
lookups and exception observations, with source/runtime provenance.

Explicit policies preserve the old keys and signed values without restoring
`prefix=`, `grades=`, `variable_hints` or `lazy=` factory behavior. Filtering
preserves signed references; a separate compact vocabulary keeps Python keys
independent of display styles. Native basis enumeration and gamma aliases
retain their positive orientations. Empty-string scalar parsing stays retired.

All archived tables replay in both expression modes. Coefficient-first tests
cover Euclidean, oblique-indefinite and singular-oblique metrics, both signs,
three styles/targets, and nonzero mixed grades. Named locals require symbol
environments; literalized blades replay independently. Scoped rebinding,
immutable snapshots, exact identifier filtering and validation remain live
contracts. Corruption probes reject altered keys, coefficient shape/finiteness,
numeric values, spelling, and a factory that drops orientation.

All 73 focused cases pass at 100% line/branch coverage in the three test files.
All 63 public cases pass directly from the wheel with origins verified and
legacy imports blocked. Full package/release suites pass 5,972 cases on
Python 3.11 and 6,089 on Python 3.14, including maintained notebook exports.
Core/facade coverage, the existing matrix warning, and 295 type errors remain.
No production code changes.

The presentation-contexts notebook teaches these boundaries with derived signs
and executable symbol/literal replay; generated display equations are inspected.
The construction-exemption ledger falls from eight files to seven. Remaining
mixed legacy suites, namespace/construction guards, engine deletion and final
release gates are still pending. See
[ADR-106](../adrs/106-independent-public-local-name-contracts.md).

### Phase 9 follow-through: complex and quaternion convention contracts

All fifteen original class/method identities in `test_quaternion.py` remain
live on the public facade. The archive `tools/baselines/quaternion-conventions-v1.json`
preserves the complete source and digest, nineteen observed values in three
targets, complete quaternion/complex/custom-`xyz` basis tables, signatures
and legacy presentation-ordered bivectors, with source/runtime provenance.

Use public presets, immutable label replacement, explicit semantic roles
instead of parsed metric-role text, and signed blade literals with `expr=True`.
Native enumeration remains `k,j,i` while semantic lookup selects `i,j,k`.
Custom labels preserve aliases, roles, numeric identity, and independent locals.
Single-character LaTeX names retain the original regression coverage.

Derive the native Hamilton coordinate embedding from exterior products.
Independent scalar/dot/cross formulas and Python complex numbers check
arithmetic, conjugation, inverse, right division and norm in both expression
modes and all display targets. Noncommuting dense inputs, zeros, scalars,
pure units and fractional coefficients supplement original examples.
Grade closure, replay, data shape/finiteness, hashes and rendering stay checked.

Three Gram matrices show why a name does not determine a blade's square.
Mixed-grade probes distinguish reverse from conjugation outside the even
subalgebra. Corruption tests reject altered archive data, wrong-side division,
conjugation substituted for reverse, and display-order numeric enumeration.
Fresh-process guards forbid the entire legacy engine/rendering import stack.

All 155 focused cases pass with 100% line/branch coverage in the three test
files. All 143 public cases also pass directly from the built wheel with
origins verified. Full package/release suites pass 6,113 cases on Python 3.11
and 6,230 on Python 3.14, including all maintained notebook exports.
Core/facade coverage, the matrix warning and 295 type errors remain unchanged.

The existing complex/quaternion notebook now computes before naming and
teaches native order, odd-grade conjugation and a Gram-derived counterexample.
Generated HTML/TeX is inspected. Runtime code is unchanged; two public
docstrings are corrected to describe the even subalgebra. The construction
ledger falls from seven files to six. Low-dimensional/transformation-helper
and other mixed legacy dependencies remain before engine deletion.
See [ADR-107](../adrs/107-public-complex-and-quaternion-convention-contracts.md).

### Phase 9 follow-through: low-dimensional and transformation compositions

All nineteen historical method identities and twenty-six collected cases in
`test_low_dim.py` and `test_chisolm_transformations.py` now use the public
facade. The archive `tools/baselines/transformation-contracts-v1.json` retains
both complete sources and digests, forty seeded observations with their original
vectors and spanning columns, seven low-dimensional values, and three retired
rotor-constructor errors. No seeded case was skipped.

Projection, rejection and reflection use explicit primitive compositions, not
restored helper aliases. Original rotor-validation identities now check the
retired constructor boundary and distinguish valid generic scalar/vector
exponentiation from a plane-angle API. Pseudoscalars use `expr=True` and explicit
symbol environments, preserving coefficients independently of provenance.

Coordinate projection and normal-reflection matrices independently verify the
archived observations. New probes cover oblique-indefinite and degenerate
metrics, restricted-subspace invertibility, blade scaling, negative-square
normals, null-input failures, both expression modes and all three display
targets. Gram-derived bivector squares select elliptic, hyperbolic or terminating
exponentials, checked against a separate vector-action matrix exponential.
Shape/finiteness, replay and hash checks remain live. Mutation probes reject
corrupt coefficients, wrong contraction side, inverse-to-reverse substitution
and reversed exponential orientation.

The 386 focused cases pass with 100% line/branch coverage in the four
numeric/boundary files. The three public suites also pass all 376 cases from
the built wheel with origins verified and legacy imports forbidden. Full
package/release suites pass 6,474 cases (60 skipped) on Python 3.11 and 6,606
(20 skipped) on Python 3.14, including the maintained gallery exports.
Core/facade coverage, the existing matrix warning and 295 type errors are
unchanged; no production package behavior changes.

Two existing notebook plot defects are fixed: the projector draws the rotated
XZ plane it actually computes, and the reflection notebook uses perpendicular
normals for its plotted mirrors. All arrows use computed multivectors. Fifteen
Python 3.14 runtime regressions check multiple slider configurations, surface
membership and arrow data; restoring either old geometry is rejected.
The migration guide's two executable recipes and the teaching text explain
restricted metrics, mirror versus normal-span conventions and inverse versus
reverse.

The construction ledger falls from six files to four: `test_coverage.py`,
`test_coverage_gaps.py`, `test_redesign.py` and `test_scalar_helpers.py`.
Their mixed contracts, namespace/construction guards, engine deletion and final
release gates remain pending. See
[ADR-108](../adrs/108-public-transformation-compositions-and-geometric-notebook-plots.md).

### Phase 9 follow-through: scalar compositions and small-value contracts

All 51 original method identities in `test_scalar_helpers.py` now execute
the public facade. The archive `tools/baselines/scalar-helpers-v1.json`
retains the complete source and digest, six fraction observations, seven
constants, four compositions, eight scientific-node and six coefficient-node
observations, three scientific styles and the old zero-denominator error.

Fraction and constant convenience members stay retired. Use public scalar
construction, division, explicit names and `scalar_sqrt`. Generic division
raises `ZeroDivisionError` for either signed zero. Literal arithmetic may
simplify in rendering; a fraction layout does not add exact rational storage.
Named operands in tracked expressions require explicit replay environments.
The supplied historical rounded `hbar` is preserved as data, not silently
replaced by `h/(2*pi)` or promoted into a new constants catalogue.

The original tiny-value assertions accepted zero under NumPy's default absolute
tolerance. Regression probes demonstrate that weakness and require the new
assertions to reject erased values. Archived numeric observations replay with
zero absolute tolerance, alongside Python fraction/float arithmetic, derived
rotor coefficients and an independent scientific-number parser. Corruption
probes reject malformed/nonfinite coefficients and changed constant magnitudes.

Additional coverage checks display-threshold neighbors, signed subnormals,
negative unit mantissas and tiny mixed-grade values under oblique-indefinite
and degenerate metrics. Display filtering is explicitly separate from exact
storage, equality and hashing. `zero_tolerance=0` exposes small coefficients;
significant-digit precision does not preserve fixed-decimal padding, and
legacy `cdot`/`raw` LaTeX switches remain unsupported.

All 273 focused cases pass on Python 3.14 with 100% line/branch coverage in
their three files. Both public suites pass all 260 cases directly from the
built wheel with origins verified and legacy imports blocked. Full suites
pass 6,695 cases (61 skipped) on Python 3.11 and 6,828 (20 skipped) on Python
3.14. Core/facade coverage is unchanged; emitter coverage rises to 96%.
The existing matrix warning and 295 type errors remain.

The eager-values notebook now teaches tiny-value display tolerance and literal
versus named fractions. A runtime test checks numeric coefficients, explicit
replay and actual generated math. The migration recipe also executes.
No production package behavior changes. The construction ledger falls from
four files to three: `test_coverage.py`, `test_coverage_gaps.py` and
`test_redesign.py`. Their mixed contracts, namespace/construction guards,
engine deletion and final release gates remain pending. See
[ADR-109](../adrs/109-public-scalar-compositions-and-small-value-contracts.md).

### Phase 9 follow-through: public factory and display edges

All thirty historical method identities in `test_coverage_gaps.py` now run
on the public facade. The archive `tools/baselines/factory-display-edges-v1.json`
preserves the complete source and digest, six lookup observations, four
errors, three complete pseudoscalar-labelled basis tables (32 blades), six
display samples and ten factory/flag observations. Display evidence includes
old result-object type, strings, repr, rich output, wrapping and fixed decimals.

The current public contracts remain explicit: `expr` replaces both retired
factory flags; unknown lookup text raises `KeyError`; mask `0` or `"1"`
selects the scalar. Signed names return their actual product, not the old
unsigned storage slot. Blade literalization preserves orientation while
dropping names and prior provenance. Indexed conventions override the
derived top-grade mask without changing its metric-dependent square.

Display methods return string snapshots. New calls observe scoped policies,
while stored strings and numeric values remain unchanged. Repr selects ASCII,
rich output selects LaTeX, and wrapping adds delimiters without bypassing
content. Request name-only content explicitly when wanted. Retired
`display_repr` and result-object numeric formatting are not restored;
formatting an ordinary string cannot set coefficient precision.

Archived values are recomputed from factories and exterior products, with
both expression modes and all three targets. Basis/factory comparisons do
not mistake legacy display order for native enumeration. Additional probes
derive vector products from Gram pairings and exterior determinants; signed
volumes use the dimension/Gram determinant identity. Degenerate named
volumes remain noninvertible. Nested scopes and exceptional exits restore
policy without changing coefficients, expression identity or hashes.

Corruption probes reject malformed/nonfinite or erased coefficients, unsigned
semantic lookup, wrong-target repr, non-string display wrappers and changed
pseudoscalar labels. Fresh-process tests block legacy imports. The existing
presentation notebook now teaches snapshots explicitly; its runtime test
checks numeric product coefficients and actual generated math.

All 211 focused cases pass on Python 3.14 with 100% line/branch coverage in
their three files. Both public suites pass all 199 cases directly from the
built wheel with origins verified. Full suites pass 6,875 cases (62 skipped)
on Python 3.11 and 7,009 (20 skipped) on Python 3.14, including maintained
notebook exports. Core/facade percentages remain unchanged with one extra
facade path covered; emitter coverage remains at 96%. The existing matrix
warning and 295 type errors remain.

No production package behavior changes. The construction ledger falls from
three files to two: `test_coverage.py` and `test_redesign.py`. Their mixed
contracts, namespace/construction guards, engine deletion and final release
gates remain pending. See
[ADR-110](../adrs/110-public-factory-and-display-edge-contracts.md).

### Phase 9 follow-through: architecture contracts and the public catalog

The seven `TestArchitecturalInvariants` identities are extracted from
`test_coverage.py` into `facade/test_architecture_contracts.py`. The other
192 method identities and all other mixed-file code remain unchanged.
`tools/baselines/architecture-contracts-v1.json` preserves the complete source,
its SHA-256 digest, all 199 source identities, the seven migrated identities
and owner, 45 operation/node declarations and 57 symbolic-handler names.
All seven original tests passed before migration.

Current checks enforce core/catalog import direction recursively, resolving
relative imports and scanning nested lexical scopes. Source resource traversal
also works in a zipped wheel. Catalog completeness follows the public core
manifest, documented exclusions and structural arithmetic entries rather than
the historical count. Generic calls use the same immutable schemas as numeric
dispatch; public aliases retain exact object identity.

All 71 current public numeric operations are checked with required parameters
alone and with optional controls. Real evaluator signatures and recorded
argument forwarding verify operand/parameter separation. Bad arities, unknown
keywords and missing required parameters fail. Negative controls reject
forbidden imports, incomplete catalogs, wrong IDs, overlapping or unexplained
exclusions, mismatched signatures and swapped operands.

Independent Gram pairings, exterior determinants and the vector triple-product
identity check eager arithmetic, grade/transwedge parameters, binary lowering,
norms and predicates under three metrics. Replay is independent of rendering
target and follows changed symbol bindings without mutating the eager value;
a cached-result mutation is rejected. The migration guide teaches the shared
schema with an executable example. Existing notebooks need no changes for
this internal architectural migration and continue to pass their export gates.

All 203 focused cases pass with 100% line/branch coverage in both files.
All 165 public cases pass directly from the built wheel with module origins
verified and legacy imports blocked. Full suites pass 7,071 cases (62 skipped)
on Python 3.11 and 7,205 (20 skipped) on Python 3.14. Core, facade and rendering
coverage percentages are unchanged. The existing matrix warning and 295 type
errors remain. No production package behavior changes.

The construction ledger still contains `test_coverage.py` and `test_redesign.py`:
extracting one coherent subgroup does not complete either mixed suite.
Their remaining contracts, namespace/construction guards, engine deletion
and final release gates remain pending. See
[ADR-111](../adrs/111-architecture-contracts-use-the-public-operation-catalog.md).

### Phase 9 follow-through: explicit inner-product contracts

All thirteen `TestIpFunction` and `TestSymbolicIp` identities are extracted
from `test_coverage.py` into `facade/test_inner_product_contracts.py`.
The other 179 methods and unrelated code remain unchanged. The archive
`tools/baselines/inner-products-v1.json` retains full source and digest,
all 192 source identities, the thirteen migrated identities and owner,
75 eager/symbolic mode observations, default/Dorst results, wrapper/node
types, original glyphs and both invalid-mode errors.

All thirteen original cases passed, but the method named Hestenes actually
called the Doran–Lasenby default, and several vector-only examples produced zero.
Current assertions distinguish the explicit named functions on nonzero scalar,
bivector and mixed-grade examples. The dispatcher and `inner_product` alias
remain absent; `|` retains its fixed Doran–Lasenby meaning. A local import
alias selects a function without changing the operator.

Independent Gram-minor oracles check metric and scalar pairings, including
the grade-dependent reversion sign. Grade-filtered reference left actions
check the four contraction/inner variants; coordinate formulas independently
check vector/bivector orientation. Tests cover every grade pair through grade
three and mixed inputs under Euclidean, oblique-indefinite and degenerate
metrics, across all targets and anonymous/literal/named provenance states.
Replay follows changed bindings. Mutation probes reject erased/nonfinite
coefficients, substituted conventions, reversed floors and cached results.

The existing inner-product notebook now teaches six contrasting operand
pairs under four selectable metrics. `MatrixRepr` displays the actual Gram
matrix; values and signs are computed, including nonzero null bivectors.
Runtime tests check all four metric inputs and actual generated math.
The migration guide includes an executable replacement recipe.

All 237 focused cases pass on Python 3.14 with 100% line/branch coverage in
both files. All 221 public cases pass directly from the wheel with origins
verified and legacy imports blocked. Full suites pass 7,291 cases (66 skipped)
on Python 3.11 and 7,429 (20 skipped) on Python 3.14, including notebook
exports. Numeric facade coverage rises to 98% through the reflected-pipe
regression; core and rendering percentages stay unchanged. The existing
matrix warning, 295 type errors and Markdown-formatting debt remain.

No production package behavior changes. The two mixed suites remain in the
construction ledger; their remaining contracts, namespace/construction guards,
engine deletion and final release gates are still pending. See
[ADR-112](../adrs/112-explicit-inner-product-contracts-outlive-mode-dispatch.md).

### Phase 9 follow-through: eager operation and provenance edges

All 42 identities in ten eager-operation classes are extracted from
`test_coverage.py` into `facade/test_eager_operation_contracts.py`.
The other 137 methods and unrelated code remain unchanged. The archive
`tools/baselines/eager-operation-edges-v1.json` retains complete source and
digest, all 179 source identities, extracted identities and owner, 46
nonzero operation observations, eight mixed-input observations, wrapper/node
types, display strings, scalar errors, normalization aliases and properties.

Public tests check 23 recipes across Euclidean, oblique-indefinite and
degenerate metrics and five provenance states. Gram minors, exterior
permutation signs, grade signs and forced-reference tensors independently
check coefficients. Linear solves and two-sided residuals check inverse;
metric determinants check duality. Null-value domain errors, plain scalar
result types, explicit replay, source order and presentation immutability
are permanent v2 contracts. Reviewed three-target strings are separate from
historical spelling; bare nodes, diagnostic repr and warning adapters retain
their intentional v2 boundaries.

Mutation controls reject erased/malformed/nonfinite coefficients, wrong unary
operations, changed return types, reversed provenance, cached replay, wrong
targets and silent aliases. The eager-values notebook teaches literal snapshots
versus symbol rebinding with nonzero mixed-grade output, explicit scalar-node
evaluation and mathematical rendering. Its runtime test checks coefficients,
literal/symbol structure and generated Markdown. The guide contains an
executable replacement recipe.

All 489 focused cases pass on Python 3.14 with 100% line/branch coverage in
both files. All 470 public cases pass from the wheel with origins verified
and legacy imports blocked. Full suites pass 7,737 cases (67 skipped) on
Python 3.11 and 7,876 (20 skipped) on Python 3.14, including notebook exports.
Core, facade and rendering coverage percentages are unchanged; the existing
matrix warning, 295 type errors and Markdown-formatting debt remain.
No production package behavior changes. This subgroup leaves
both mixed suites in the construction ledger; remaining contracts, engine
deletion and final release gates are still pending. See
[ADR-113](../adrs/113-eager-operation-contracts-outlive-mixed-symbolic-tests.md).

### Phase 9 follow-through: grade inspection and bounded simplification

All 48 identities in `TestSymbolicGradeEvenOdd`, `TestGradePropagation` and
`TestSimplify` now live in `facade/test_grade_simplification_contracts.py`.
The other 89 methods and unrelated code are unchanged. The archive
`tools/baselines/grade-simplification-v1.json` retains complete source and
digest, all 137 source identities, extracted owners, 30 grade observations,
eight parity projections, 60 simplification observations, automatic grades
and fourteen original scalar-context errors across two signatures. A separate
four-dimensional sample preserves the incorrect legacy self-wedge rewrite.

Public grade inspection follows actual coefficients, not cached assumptions.
Zero and mixed values report `None`; tiny-value tests distinguish diagnostic
tolerance from storage and exact equality. The original orthogonal-vector
product is a pure bivector, despite its misleading test comment. A separate
six-dimensional bivector inverse has both grades 2 and 6.

Bounded v2 simplification remains unchanged. Tests pin its supported reductions,
preserve numeric checks for other valid identities without promising those
rewrites, and replay under vector, bivector and mixed bindings. Self-wedge,
grade projection and rotor-value assumptions cannot be inferred from a name;
norm/unit and double-inverse calls retain invalid-binding domain errors.

Independent mask, permutation, Gram-minor and reference-action oracles cover
three metrics, provenance states, projection targets, involutions and inverses.
Mutation controls reject bad archives, stale grades, unsafe rewrites, single-pass
simplification and wrong replay/rendering. The involutions notebook teaches
the distinctions under three selectable Gram matrices shown with `MatrixRepr`.
Runtime tests check all metrics, decomposition, signs, bindings and actual math.

All 600 focused cases pass on Python 3.14 with 100% line/branch coverage in
both files. All 582 public cases pass from the wheel with origins verified
and legacy imports blocked. Full suites pass 8,286 cases (70 skipped) on
Python 3.11 and 8,428 (20 skipped) on Python 3.14, including notebook exports.
Core/facade coverage is unchanged; two additional rendering paths are covered.
The existing matrix warning, 295 type errors and Markdown-formatting debt
remain. No production package behavior changes. Both mixed suites remain
in the construction ledger; remaining helpers, rendering/transformation tests,
namespace guards, engine deletion and release gates are still pending. See
[ADR-114](../adrs/114-grade-inspection-and-bounded-simplification-contracts.md).

### Phase 9 follow-through: public expression-helper identity contracts

Seventeen `TestCoverageGaps` methods now live in
`facade/test_expression_helper_contracts.py`. The other 72 methods and unrelated
code are unchanged. The archive `tools/baselines/expression-helpers-v1.json`
retains complete source/digest, all 89 source identities, selected ownership,
four reflected products, fourteen known-grade observations, sixteen equality
comparisons and eight parity observations before/after simplification across
two signatures. Scalar rendering, invalid coercion, actual fallback equality
and the ignored `sym` grade keyword remain recorded.

The old override test passed because its supplied grade matched the value,
not because `sym` used that keyword. The named fallback test exercised `Dual`,
not an unknown node. Public replacements use explicit constructors, numeric
inspection and replay rather than preserving those misleading claims.

Tests separate numeric values, structural histories and rendered strings.
They check immutable snapshots, full-name identity, exact finite-float equality,
compatible signed-zero hashes and changed bindings. Constructor rounding of
large integers/fractions is distinct from exact numeric comparison with those
original inputs. Independent grade-sign, Gram-minor and reference-product
oracles check values across three metrics. Mutation controls reject bad
archives, swapped source order, stale replay, identity hashes, approximate
literal equality and ASCII-only name identity.

The eager-values notebook demonstrates all three equality questions, rebinding,
adjacent floats and signed-zero dictionary lookup. Its runtime regression
checks computed values, actual nodes and generated teaching text.
All 179 focused cases pass on Python 3.14 with 100% line/branch coverage in
both files. All 163 public cases pass from the wheel with origins verified
and legacy imports blocked.

Full suites pass 8,447 cases (71 skipped) on Python 3.11 and 8,590 (20 skipped)
on Python 3.14. Expression nodes and simplification have 100% line/branch
coverage; evaluation has 99%. An additional numeric-facade path and catalog
path are covered, with rounded production percentages otherwise unchanged.
The guide recipe executes and all 246 local links in the eight changed
Markdown files resolve. Ruff lint, configured Python formatting and
changed-file Markdown lint pass. The existing matrix warning, 295 type errors
and Markdown code-block formatting debt remain.

No production package behavior changes. Both mixed suites remain in the
construction ledger. The remaining display/naming/rotor tests, namespace
guards, engine deletion and release gates are still pending. See
[ADR-115](../adrs/115-public-expression-identity-and-helper-contracts.md).

### Phase 9 follow-through: public mixed-coverage LaTeX contracts

All 43 remaining rendering identities in `test_coverage.py` now live in
`rendering/test_coverage_latex_contracts.py`. The other 29 methods and
unrelated code are unchanged. The archive `tools/baselines/coverage-latex-v1.json`
retains complete source/digest, all 72 source identities, selected ownership
and 55 actual rendering calls with coefficients, bindings, signatures,
names, nodes, wrapping and old LaTeX.

Each public historical rendering retains exact spelling and numeric replay.
Permissive vector/custom-label assertions are now exact. Current wide accents,
overlines and floor contractions remain accepted v2 policy, not new defaults.
Naming without provenance, explicit symbol leaves, content selection, wrapper
validation and rich hooks are checked separately.

Twenty compositions cover all three targets in Euclidean, oblique-indefinite
and degenerate metrics. Reference product/grade/minor oracles check nonzero
contractions, accents, products, inverses, parity and grouping. Degenerate
dual/undual domain failures remain explicit. Mutation controls reject
corrupted archives, missing rendering calls, reversed products, stale replay
and rich hooks that ignore content.

The presentation notebook shows its Gram matrix through `MatrixRepr` and
teaches the shared normalization/involution hat alongside computed values and
opposite nonzero contraction directions. A runtime regression verifies both
mathematics and teaching output. All 329 focused cases pass on Python 3.14
with 100% line/branch coverage in both files.

All 313 public cases pass from the wheel with module origins verified and
legacy imports blocked. Full suites pass 8,732 cases (72 skipped) on Python
3.11 and 8,876 (20 skipped) on Python 3.14. Core, facade, expression and
rendering coverage are unchanged. Ruff lint, configured Python formatting
and changed-file Markdown lint pass; the guide recipe executes and all 246
local links in the seven changed Markdown files resolve. The existing matrix
warning, 295 type errors and Markdown code-block formatting debt remain.

No production behavior changes. Nine naming and twenty rotor/sandwich tests
remain in the mixed suite; both construction-ledger files remain. Namespace
guards, engine deletion and release gates are pending. See
[ADR-116](../adrs/116-public-latex-coverage-and-content-contracts.md).

### Phase 9 follow-through: public naming-preset and exterior-word contracts

All nine `TestNamingPresets` identities now live in
`presentation/test_naming_preset_contracts.py`. The other twenty mixed-suite
methods and unrelated code are unchanged. The archive
`tools/baselines/naming-presets-v1.json` retains full source/digest, all 29
source identities, selected ownership and five complete convention tables.
The 44 native labels retain coefficients, squares, three spellings, actual
renderings and 132 evaluated lookups. Three actual validation errors remain
recorded.

Public replay covers every label/target with and without expression literals.
Existing ASCII repr, safe sigma-script bracing and `KeyError` lookup behavior
remain explicit. Complete label tables preserve custom names and historical
sigma-xyz ASCII keys; configuration and spelling ambiguities are rejected.

Every named basis pair is checked against reference products in three metrics
and three indexed styles across all targets. Separate coefficient identities
show that word-like exterior labels do not absorb the scalar/vector terms of
geometric words in oblique frames. Signed lookup follows a computed reversed
exterior product, not its unsigned storage slot. Python locals remain an
independent policy; label containers are immutable snapshots.

The construction notebook displays its Gram matrix with `MatrixRepr` and
teaches these distinctions through calculated values and explicit local-name
configuration. A runtime regression verifies mathematics and teaching output.
All 109 focused cases pass on Python 3.14 with 100% line/branch coverage in
both files.

All 93 public cases pass from the wheel with module origins verified and
legacy imports blocked. Full suites pass 8,831 cases (73 skipped) on Python
3.11 and 8,976 (20 skipped) on Python 3.14. Core, facade, expression and
rendering coverage are unchanged. Ruff lint, configured Python formatting
and changed-file Markdown lint pass; the guide recipe executes and all 246
local links in the seven changed Markdown files resolve. The existing matrix
warning, 295 type errors and Markdown code-block formatting debt remain.

A separate full-suite production coverage checkpoint measures 100% for
`names.py`, 99% for `blades.py` and 96% for `presentation.py`, with branch
measurement enabled.

No production behavior changes. Only twenty rotor/sandwich methods remain in
the mixed suite. Both construction-ledger files remain; namespace guards,
engine deletion and release gates are pending. See
[ADR-117](../adrs/117-public-naming-presets-and-exterior-word-contracts.md).

### Phase 9 follow-through: public rotor recipes and sandwich contracts

All twenty remaining `test_coverage.py` identities now live in
`facade/test_rotor_sandwich_contracts.py`. They passed intact on v1 before
migration. The complete source/digest, twenty IDs, 27 rotation observations,
five constructor errors, five domain probes and four named sandwich
observations are retained in `tools/baselines/rotor-sandwich-v1.json`.
The archive includes actual coefficients, inputs, reverse products, predicate
results and typography, not inferred historical behavior.

| Historical group | Identities | Public responsibility |
|---|---|---|
| `TestRotorFromPlaneAngle` | 4 | Explicit exponential orientation, zero/quarter/half turns and reverse norm |
| `TestRotorValidation` | 7 | Retired constructor versus generic exponentials, explicit normalization, scaled rotors and STA phases |
| `TestSandwich` | 3 | Eager coefficients, named call provenance, changed-binding replay and `sw` |
| `TestCoverageGaps` rotor methods | 6 | Explicit degree conversion and retained alias/error/positional-angle evidence |

Generic `exp` accepts scalar/vector/trivector input without the old plane-angle
validation. A simple negative-square plane can be normalized explicitly;
positive-square planes use rapidity, while null planes retain their original
scale. Gram-derived coordinate matrices verify all three branches in
Euclidean, oblique positive/indefinite and degenerate frames. Three-target
rendering and replay preserve coefficients and hashes in both expression modes.

Nonsimple exponentials are checked against commuting-plane factorization and
a series of forced-reference linear actions across three signatures. Keep
the grade-four cross term and the whole reverse product. The archive records
v1's false positive for a trigonometric nonsimple construction; the current
predicate correctly rejects it. The existing logarithm's narrower
Study-number domain remains explicit.

STA phases are even but need not satisfy `P*reverse(P)==1`. Their reverse
sandwiches can fix vectors while inverse conjugation mixes grades. Scaled,
mixed-grade sandwich cases verify that `sandwich`/`sw` always use reverse,
not inverse. No production algorithm, API or equality semantics change.

The existing exponential notebook now teaches these distinctions with
`MatrixRepr` Gram displays, explicit degree conversion and computed values.
Four runtime cases check zero/55/90/180-degree slider settings, coordinate
actions, compound residuals and actual rendered coefficients.

All 153 focused cases pass on Python 3.14 with 100% line/branch coverage in
both new files. Corruption and mutation controls reject wrong coefficients,
orientation, the old scalar-only predicate and inverse substitution.
All 132 public cases pass from the built wheel with legacy imports blocked
and all 26 loaded Galaga module origins verified.

Full suites pass 8,960 cases (77 skipped) on Python 3.11 and 9,109 (20 skipped)
on Python 3.14. The line and arc sets for all nineteen measured core/facade/
expression/rendering files are identical to the previous checkpoint.
Ruff lint, Python formatting and changed-file Markdown lint pass. The type
baseline remains 295 errors and 18 warnings. The existing matrix conversion
warning and Markdown code-block formatting debt remain separate work.

At this checkpoint, an explicit six-dimensional counterexample recorded
that `is_rotor` was a unit-even predicate, not a general vector-preservation
certificate. [ADR-124](../adrs/124-rotor-predicate-requires-vector-preservation.md)
subsequently strengthened the predicate; that regression now requires rejection.
Both executable guide recipes and all 297 local file-link targets in the
eight changed Markdown files are checked.

`test_coverage.py` is now an import-free ownership record, kept for historical
migration guards. It collects no duplicate tests and is no longer exempt
from the legacy-construction guard or writable by the isolation codemod.
The construction ledger falls from two files to one: `test_redesign.py`.
Its substantial remaining presentation/expression contracts come next, before
namespace/construction guards, obsolete engine deletion and release gates.
See [ADR-118](../adrs/118-public-rotor-recipes-and-sandwich-contracts.md).

### Phase 9 follow-through: final redesign construction exemption

All 279 `test_redesign.py` identities now have explicit collected public owners.
Every original test passed before migration. The complete source, SHA-256,
ordered identities, final local observations and object aliases remain in
[redesign-v1.json](../../packages/galaga/tools/baselines/redesign-v1.json),
with 189 deduplicated snapshots. The
[v2 crosswalk](../../packages/galaga/tools/baselines/redesign-v2-owners.json)
assigns each historical identity exactly once to one of 27 responsibility
groups, documenting retained, replaced and retired behavior.

Following this inventory's consolidation policy, overlapping operations reuse
existing stronger mixed-grade/general-Gram, expression, scalar, inner-product,
rendering and rotor owners. Unique contracts have these public homes:

| Public tests | Responsibility |
|---|---|
| `presentation/test_redesign_state_contracts.py` | Immutable names, independent state transitions, complete blade labels and 9D/10D lookup |
| `facade/test_redesign_workflows.py` | All ten archived workflow results, corrected exponential rotation, rebound grades and explicit nodes |
| `rendering/test_redesign_display_contracts.py` | Content snapshots, reveal replacement, whole-operand powers, spacing and precision |
| `core/test_division_contracts.py` | Exact stored scalar support, tiny grades, subnormal quotients and right-division semantics |
| `facade/test_division_provenance.py` | Both denominator histories, changed-binding replay and fraction rendering |
| `facade/test_redesign_boundary.py` | Complete collected ownership, archive/crosswalk negative controls, legacy-free execution and teaching |

V1 naming mutated ordinary values but copied protected basis values. V2 uses
immutable wrappers throughout. `unnamed` removes a name; `without_expr` removes
provenance. A named operand can track again in subsequent arithmetic. Remove
both for a full numeric snapshot. Name conversion is explicit, whitespace is
preserved in plain variants, and complete labels replace high-dimensional
digit parsing. Display returns strings with explicit content/target selection,
not a lazy display-result object. Precision can affect displayed expression
literals without changing their stored values.

The old seventh “rotor” recipe omitted exponentiation. Its actual scaled
generator and sandwich result are archived and replayed honestly; a separate
public test verifies the exponential, reverse norm and rotation orientation.
Old `R * reverse(R)` simplification cannot rely on cached grade/rotor facts
when new bindings are supplied. No high-dimensional predicate change is made.

The migration exposed division defects, fixed with approval:

- multivector denominators retain both expression operands rather than a
  cached scalar parameter;
- exact scalar arithmetic dispatch never discards tiny nonscalar grades;
- direct scalar division avoids an overflowing reciprocal for finite
  subnormal quotients; and
- reflected scalar zero division now consistently raises `ZeroDivisionError`.

All 46 new division cases pass; 26 failed before the fix. Existing independent
right-inverse action oracles retain their numeric checks and now expect a
fraction display. CGA expanded homogenization/radius expressions also retain
their weight denominators. Six additional model regressions rebind coordinates,
positive/negative/fractional weights and zero/nonzero radii.

The eager-values notebook teaches rebindable denominator products, supplied
rounded physical inputs, and finite subnormal division. Headless execution
checks actual values, expressions, display thresholds and changed bindings.
The migration guide and ADRs document accepted API/presentation differences.

Validation at this checkpoint:

- 231 cases across the six new files pass with **100% line and branch coverage**
  in those files (660 statements, 84 branches).
- All 2,808 cases in sixteen public owner/CGA/division files pass from the
  newly built wheel with legacy imports blocked; all 27 loaded Galaga module
  origins resolve to that wheel.
- Full suites pass **8,921 cases, 78 skipped on Python 3.11**, and
  **9,071 cases, 20 skipped on Python 3.14**. The lower total reflects reviewed
  consolidation, not unowned historical tests.
- Comparing nineteen measured production files through source-line mapping
  loses no previously covered surviving line. The only old arc replaced is
  the catalog sequence now passing through the new `divide` entry; changed
  arithmetic lines are covered and an additional emitter line is exercised.
  Combined production line/branch coverage remains 95%.
- Ruff lint/format, changed-file Markdown lint, notebook compile/teaching
  guards and the notebook/isolation codemod check modes pass. The type
  baseline remains **295 errors and 18 warnings**, not a clean type check.
  The existing matrix complex-to-real warning remains unchanged.
- All 310 local Markdown file-link targets in the ten changed documentation
  files resolve, and the new division guide recipe executes successfully.

The construction ledger is **empty**. `test_redesign.py` is an import-free
ownership record collecting no duplicates, and neither check nor write mode
can re-isolate it. Namespace/construction guards, obsolete engine deletion
and release gates are next. The high-dimensional `is_rotor` limitation remains
a separate release decision.

See [ADR-119](../adrs/119-division-provenance-and-exact-scalar-dispatch.md) and
[ADR-120](../adrs/120-complete-redesign-contract-migration.md).

### Phase 9 follow-through: deletion-ready namespace and import guards

The test guard no longer imports the constructors it disables. A shared
test-only finder rejects fifteen retired roots and their descendants,
covering the manifest's twenty-one legacy paths. Pytest installs it before
collection; cache checks cover preloading, collection, tests and session
teardown without evicting modules. Retired `legacy_oracle` markers and any
nonempty construction ledger fail explicitly. Optional `ImportError` fallbacks
cannot swallow the guard's assertion error.

Seven selected source records retain twenty-nine historical identities in
[namespace-boundaries-v1.json](../../packages/galaga/tools/baselines/namespace-boundaries-v1.json).
Namespace, ownership, alias, facade and shared-symbolic tests now depend only
on public v2. Five renamed identities have an explicit crosswalk; the eleven
shared-symbolic identities retain their names and document accepted v2
semantics. Explicit names, immutable symbols/literals and catalog calls
replace private fields, implicit normalization and the mutable domain registry.
Products are checked against the actual Gram matrix, including oblique and
native-null cases.

The first guarded full-suite collection discovered `test_latex_tree.py` still
importing the old renderer. Constructor poisoning could not detect that
dependency because the suite constructs no algebras. All forty-five original
cases were executed and their source, digest, tree/output observations and
identities archived in
[latex-tree-v1.json](../../packages/galaga/tools/baselines/latex-tree-v1.json).
Every identity now has an immutable semantic-tree owner. The suite explicitly
documents existing v2 differences in escaped text versus mathematical names,
separator spacing, script braces, ordinary/compact fractions and preservation
of explicit grouping, negative numerators and denominators of one.

Recursive source-resource checks work with source directories and zipped
wheels. They reject outward core dependencies, retired facade imports,
private product-table access and inactive direct imports in tests/tools.
Negative controls cover nested scopes, source/owner corruption, cache
sentinels, finder ordering/cleanup and actual isolated pytest lifecycle
failures. The bridge remains an allowed same-object warning adapter.

Validation at this checkpoint:

- All **267 focused cases** pass. The ten measured changed test/helper files
  have **100% line and branch coverage** (814 statements, 54 branches).
- All **192 public cases** in seven migrated files pass from a fresh wheel
  with the shared guard installed before importing Galaga; all **28 loaded
  Galaga module origins** resolve to that wheel.
- Full suites pass **9,002 cases, 78 skipped on Python 3.11**, and
  **9,152 cases, 20 skipped on Python 3.14**, under the new collection guard.
- Compared with the immediately preceding redesign checkpoint, nineteen
  measured production files lose no covered line or arc; one additional line
  and three arcs execute. Combined production line/branch coverage remains 95%.
- Ruff lint, configured Python formatting and changed-file Markdown lint pass.
  All 335 local Markdown file links in the thirteen changed documents resolve.
  The existing type baseline remains **295 errors and 18 warnings**, and the
  matrix complex-to-real warning and Markdown code-block formatting debt remain.

No production code or notebook content changes in this unit. The migration
guide explains the accepted API differences; existing expression/presentation
lessons remain the teaching owners. There are no remaining live test-side
legacy imports, but the legacy files still ship. Physical engine deletion,
alias retirement and final release gates are next. The high-dimensional
`is_rotor` decision remains separate. See
[ADR-121](../adrs/121-deletion-ready-namespace-and-import-guards.md).

### Phase 9 follow-through: physical engine deletion

The twenty-one retired production modules are removed, including the
temporary symbol-conversion shim. Historical API dispositions and all
baseline data remain. Live module checks now enforce the supported/removed
partition, and fresh processes verify real import failure without relying on
the test guard. Empty retired namespace directories are rejected too.

The permanent artifact validator compares wheel/sdist runtime bytes with
source, rejects retired paths and private-table dependencies, and checks
metadata/dependencies. Both `make check` and the release script use it.
Notebook subprocesses now follow the packages under test rather than forcing
source-tree imports. No surviving numeric or rendering algorithm changes.

The [deletion gate report](legacy-engine-deletion-gate.md) records complete
source/wheel runs, branch-coverage preservation across all thirty-one surviving
production modules, artifacts, security and performance. Physical deletion
does not complete Phase 9: surviving type errors, scratch-demo disposition,
temporary aliases, the rotor contract, CI and release metadata remain open.
See [ADR-122](../adrs/122-remove-the-legacy-engine-and-verify-artifacts.md).
