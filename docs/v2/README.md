# Galaga 2 Architecture, Migration, and Release Status

## Start here

- [Galaga 1 to 2 migration guide](migration-guide.md) is the concise
  user-facing source migration path.
- [Core cutover plan](core-cutover-plan.md) is the normative execution plan
  for replacing the legacy `Algebra` and `Multivector`, completing the facade,
  and performing the Galaga 2.0 cutover. It defines numbered work units, tests,
  and phase exit gates.
- [Numeric test migration inventory](numeric-test-migration-inventory.md)
  identifies, by existing file and test class, which Galaga tests move to
  `galaga.core`, which become facade contracts, and which remain in outer
  layers.
- [Public API migration matrix](public-api-migration-matrix.md) is the
  human-readable Phase 1 contract for every v1 export, type member, expression
  constructor, protocol, supported module, and known private dependency.
- [Presentation and expression layer plan](presentation-symbolic-layer-plan.md)
  explains the composition-facade, operation-catalog, configuration,
  expression-provenance, and rendering architecture.
- [Presentation configuration implementation](presentation-configuration.md)
  decomposes the implemented immutable components, presets, signed blade
  lookup, facade factories, and context-local override behavior.
- [Expression provenance implementation](expression-provenance.md) explains
  the immutable nodes, independent value state, catalog-driven propagation and
  evaluation, variadic lowering, and conservative simplifier.
- [Semantic rendering implementation](rendering-implementation.md) decomposes
  the shared render tree, precedence model, immutable notation rules, emitters,
  content policy, rich hooks, and scoped teaching presentations.
- [Legacy/facade LaTeX rendering parity](rendering-parity.md) explains the
  frozen historical oracle, reviewed v2 output gate, executable difference
  ledger, and structured Markdown reports used to review the cutover.
- [Exact configured rendering contracts](exact-rendering-contracts.md) explain
  the facade algebra/display/expression matrix, archived v1 observations, and
  reviewed literal LaTeX strings that make rendering decisions permanent tests.
- [Compatibility shims](compatibility-shims.md) records permanent same-object
  aliases, temporary warning adapters, ambiguous-name guidance, and bridge
  retirement policy.
- [Matrix migration](matrix-migration.md) explains how left-regular
  representations now consume public facade linear actions and general Gram
  metadata.
- [Integration migration](integration-migration.md) records the public
  expression, display, and naming boundaries used by Mermaid, Marimo, and the
  maintained v2 examples.
- [Migration engineering techniques](migration-engineering-techniques.md)
  records the reusable LibCST, executable-ledger, architecture-fitness,
  guarded-facade, oracle-ownership, and staged-validation methods used by the
  cutover.
- [Phase 8 performance baseline](phase8-performance.md) preserves historical
  direct-core, facade, expression-provenance, and retained-v1 costs. The current
  benchmark measures v2 layers using independent untimed correctness oracles.
- [Release process](../RELEASE_PROCESS.md) gives the operational alpha, beta,
  release-candidate, and final Galaga 2 publication train.
- [Numeric-algebra replacement roadmap](galaga-replacement-roadmap.md) records
  post-2.0 numeric capabilities and release-blocking migration work
  separately.
- [Native-null conformal geometric algebra](../cga/README.md) documents the
  `p_cga` Gram model, `ConformalModel`, direct objects, semantic CGA operations,
  and transformations.
- [Rigid geometric algebra](../rga-convention-layer.md) documents Eric
  Lengyel's algebraic convention, the validated `RigidModel`, measurements,
  projections, constraints, and the dual relationship with plane-based PGA.

## Current status

Galaga `2.0.0a1` has been published from the `galaga_v2` release line. Phases
0 through 8 of the core cutover plan are complete. The
proven Gram-matrix implementation lives in `galaga.core`; the exhaustive v1
replacement contract is checked in and executable; `galaga.facade` owns the
complete eager numeric facade; and the applicable legacy numeric contract has
been migrated to or rerun against that facade. `galaga.gram_bridge` is now
only a compatibility re-export of the same facade objects. The facade now
also owns immutable presentation configuration, signed blade lookup, complete
inspectable presets, fine-grained presentation views, and thread- and
async-safe scoped overrides. Optional immutable expression provenance now
records eager operation history through the same catalog, supports independent
name/tracking state, replays across every supported metric family, and
constructs no expression object on the disabled path.
Numeric values and expressions now pass through one format-neutral semantic
tree, one precedence model, immutable operation-ID notation, and shared ASCII,
Unicode, and LaTeX emitters. Content and target are independently selectable,
and facade string, format, and rich-display hooks use the same context-safe
pipeline.

The Phase 7 compatibility policy is implemented: permanent
concise aliases are exact canonical objects, temporary v1 spellings and the
`gram_bridge` paths warn with executable replacement guidance, ambiguous inner
products remain absent, and redundant generic geometry helpers are classified
for removal. `galaga_matrix` now uses public core-backed linear actions,
basis-independent inertia, and general-Gram-safe mode selection without private
multiplication tables. Mermaid and Marimo now consume public expression,
display, and naming protocols, and the first maintained v2 examples are
executable. `MatrixRepr` now owns frozen matrix-domain provenance and adapts
only public facade names, expressions, and presentations. Installed-wheel
integration gates pass. The 68 maintained Marimo notebooks now use the
promoted top-level API, pass Marimo dependency validation, and execute
headlessly under Python 3.14.

The Phase 8 top-level cutover is complete. `galaga.Algebra`,
`galaga.Multivector`, and every other top-level public export are the exact
objects owned by `galaga.facade`. The old table engine is available only as
the explicit `galaga.legacy` oracle; plain `import galaga` does not load it,
and unledgered tests poison its constructors. Clean Python 3.11 wheel tests,
the complete Python 3.11 and 3.14 package suites, and the layer-separated
performance baseline pass.

Phase 9 is the stable `2.0.0` release gate. It removes the retained table-backed
legacy engine and migration-only bridge paths, finalizes the public export
surface, runs the full supported-version and artifact gates, and records all
removals in the migration guide and release changelog. Alpha releases may
retain the explicit `galaga.legacy` oracle for comparison; the stable release
must not ship it.

Phase 9 has removed the rendering audit's live legacy dependency: all 73
historical cases remain, and reviewed v2 outputs are pinned even for accepted
differences. The benchmark now uses independent untimed correctness oracles
and measures only v2 layers, preserving the historical v1 timing table. Matrix
conversion's v1 compatibility fallbacks are also removed. The compound, STA,
and RGA exact-rendering suites now execute only the facade, retaining their
v2 literal assertions and checking numeric samples against archived v1 data
after algebraic basis transport where necessary. The shared numeric protocol
contract also runs only the facade; all 146 original seeded operation results
remain checked as historical data alongside core-reference and algebraic
checks. Compatibility-manifest introspection is also retired: the captured
v1 API remains checked against its disposition ledger, while current facade
behavior and the 15 supported v2 module imports remain live contracts.
Concrete display-order and numeric-formatting tests now use the facade too,
with v1 output preserved as data and existing formatting differences documented
explicitly. Numeric-function provenance and parenthesization contracts also
run on the facade, retaining all 29 original observations and adding explicit
replay, three-target grouping, and Gram-derived rotor-root checks.
The remaining symbolic suite now runs on the facade too, with explicit
half-scaling and structural-simplification boundaries. The ledgered `bar`,
`dag`, `inv`, and `sq` properties are implemented as read-only canonical
delegates. Symbol conversion now uses `galaga.names` and the explicit
`Name.from_latex` factory, retaining all 108 original tests and correcting
font mappings with exhaustive Unicode checks. Notation contracts now use
immutable public rules, preserve evidence for all 239 original cases, restore
unit-fraction teaching layout, and fix the Hestenes preset's LaTeX dagger.
The custom-notation notebook demonstrates both presentation capabilities.
The LaTeX pipeline suite also has public owners for its 112 archived cases.
The emitter now separates command prefixes and protects nested scripts and
compound labels, with independent numeric/replay checks.
All 141 mixed-precedence rendering tests now use public expressions too,
with archived bindings and numeric replay. Nonzero mixed-grade compositions
check scope across three metrics and all three targets without production
changes. Blade-convention contracts now retain all 107 cases on the public
facade, with all 102 method sources and twelve complete STA tables archived.
Opt-in sigma and pseudovector names derive signs from the ordered metric;
signed lookup, native aliases, and both time-first presets are tested.
The construction notebook teaches these distinctions. Fresh-process tests
block legacy imports in these paths. The remaining RGA convention suite also
retains all eleven cases on the facade. Its archived evidence is supplemented
by nonzero coefficient checks across three metrics, and custom LaTeX
under-accent fallback is fixed and taught in the RGA notebook. All twelve
locals cases now use independent public policies, preserving archived bindings
while testing signed filtering, symbol environments, and native enumeration.
The presentation notebook teaches these distinctions. All fifteen quaternion
and complex convention cases now use public presets and immutable labels.
Their archived tables and observations are checked alongside independent
Hamilton-coordinate and Python complex arithmetic. The notebook teaches
even-subalgebra, native-order, conjugation, and Gram-metric boundaries.
All twenty-six low-dimensional/transformation cases now use explicit public
compositions, retaining nineteen historical identities and forty seeded
observations. Coordinate matrix oracles cover oblique/indefinite projection,
scaled normals, null failures, and metric-dependent bivector exponentials.
The projector and reflection notebooks now draw the computed subspaces and
values, with multi-angle runtime regressions for both geometry defects.
All 51 scalar-helper identities now use public compositions, with archived
values and rendering evidence. Strict tiny-value checks replace assertions
that accepted zero; subnormal storage, display thresholds, named replay and
fraction/formatting boundaries are tested and taught in the eager-values notebook.
All thirty factory/display edge identities now use the public facade, with
complete archived basis tables, factory results and display observations.
Signed lookup, native volume orientation, rendered-string snapshots, explicit
content/wrapping and retired flags are checked. The presentation notebook
demonstrates snapshots and numeric identity across scope changes.
The seven architecture identities from the mixed coverage suite now have
public owners too. Recursive import checks enforce core/catalog boundaries;
catalog completeness follows the API rather than a fixed operation count,
and generic calls share checked evaluator/parameter routing. Complete v1
source and registry evidence is archived. The other mixed-file code is unchanged.
The thirteen inner-product dispatch identities now use explicit public
functions, retaining 75 archived mode observations. Gram-minor and
grade-selection oracles distinguish scalar handling, contraction direction
and higher-grade signs. The existing inner-product notebook compares six
operand pairs under four selectable metrics, displaying its Gram matrix
with `MatrixRepr`. No mode dispatcher is restored.
The remaining eager-operation, grade/simplification, expression-helper,
coverage-LaTeX and naming-preset groups also have permanent public owners.
All twenty final mixed-coverage rotor/sandwich identities now use public
exponentials and explicit replay. Their complete historical evidence includes
the old nonsimple-rotor false positive. The exponential notebook teaches
metric-dependent branches, compound grade-four terms and even STA phases.
All thirty completed dependency groups have fresh-process legacy-import gates.
The full suite now also rejects retired imports during collection and execution.
Engine deletion, alias retirement, and final release gates are still pending.

The equality/hash release blocker is resolved: signed-zero peers and scalar
multivectors equal to real numbers now have matching hashes. Comparison also
preserves large-integer, exact-fraction, and NumPy floating-point distinctions
without rounding the operand. Core and facade regressions cover dictionary
and set behavior without introducing a tolerance. Existing cross-algebra
scalar semantics and their mixed-numeric limitation are documented in
[ADR-095](../adrs/095-exact-numeric-equality-and-compatible-hashes.md).
The construction-only legacy ledger is empty. `test_redesign.py` and
`test_coverage.py` are import-free ownership records. All 279 redesign identities
have an explicit public-owner crosswalk; unique state/workflow/display tests
complement the existing operation contracts. Division now preserves denominator
provenance and tiny stored grades, including finite subnormal quotients.
Namespace/construction guards are complete: no guard needs live v1 classes,
and retired markers cannot reintroduce exemptions. The remaining shared-symbolic
and low-level LaTeX-tree contracts have public owners and archived evidence.
Obsolete engine deletion is next; the old files still ship in the wheel.
See [ADR-120](../adrs/120-complete-redesign-contract-migration.md),
[ADR-121](../adrs/121-deletion-ready-namespace-and-import-guards.md),
and the [cutover plan](core-cutover-plan.md#w91-delete-legacy-numeric-storage-and-tables).

The post-cutover native CGA model layer is also implemented. It validates the
actual `eo`/`einf` Gram basis supplied by `p_cga`, embeds and extracts round
points for arbitrary null-pair scaling, and provides the established CGA
attitude/carrier/center/container vocabulary, four-way component projections,
conformal conjugation, and weighted/normalized norms as model-specific
compositions over the existing generic products.

The point-based RGA model layer is implemented as the parallel validated
composition. It provides homogeneous points, paired norms, distance, angle,
projections, support, and explicit line/motor/flector constraints over the
existing RGA operation family. Transwedge remains an ambient algebraic
operation; geometric line correction is model-owned and explicit.

## Supporting documents

- [Documentation index](../README.md)
- [Galaga 1 to 2 migration guide](migration-guide.md)
- [Numeric core documentation](../core/README.md)
- [ADR-073: Move the numeric core into Galaga](../adrs/073-move-the-numeric-core-into-galaga.md)
- [ADR-075: Promote the core-backed facade](../adrs/075-promote-the-core-backed-facade.md)
- [ADR-076: Immutable presentation configuration](../adrs/076-immutable-presentation-configuration.md)
- [ADR-077: Optional expression provenance](../adrs/077-optional-expression-provenance.md)
- [ADR-078: Shared semantic rendering pipeline](../adrs/078-shared-semantic-rendering-pipeline.md)
- [ADR-082: Matrix provenance is package-owned](../adrs/082-matrix-provenance-is-package-owned.md)
- [ADR-083: Maintained notebooks are executable integration contracts](../adrs/083-maintained-notebooks-are-executable-integration-contracts.md)
- [ADR-084: Exact configured rendering contracts](../adrs/084-exact-configured-rendering-contracts.md)
- [ADR-085: Top-level API is the facade with an explicit legacy oracle](../adrs/085-top-level-api-is-the-facade-with-explicit-legacy-oracle.md)
- [ADR-086: Native-null CGA is a validated model layer](../adrs/086-native-null-cga-is-a-validated-model-layer.md)
- [ADR-087: RGA semantics are a validated model layer](../adrs/087-rga-semantics-are-a-validated-model-layer.md)
- [ADR-088: Explicit versions for prereleases](../adrs/088-explicit-versions-for-prereleases.md)
- [ADR-092: Frozen historical rendering oracles](../adrs/092-frozen-historical-rendering-oracles.md)
- [ADR-093: Benchmarks use core reference oracles](../adrs/093-benchmarks-use-core-reference-oracles.md)
- [ADR-094: Numeric contracts outlive the legacy engine](../adrs/094-numeric-contracts-outlive-the-legacy-engine.md)
- [Historical v2 issue inventory](../../V2-PLANNING.md)

The historical issue inventory predates the Gram-matrix core. It remains useful
for design context, but the core cutover plan and accepted ADRs take precedence
for implementation sequencing.
