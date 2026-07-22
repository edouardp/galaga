# Galaga 2 Planning

## Start here

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
  dual-algebra audit, executable difference ledger, permanent Pytest gate, and
  structured Markdown reports used to review the top-level cutover.
- [Exact configured rendering contracts](exact-rendering-contracts.md) explain
  the parameterized algebra/display/expression matrix and reviewed literal
  LaTeX strings that make rendering decisions permanent unit tests.
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
- [Phase 8 performance baseline](phase8-performance.md) separates direct-core,
  facade, expression-provenance, and retained-v1 costs for representative
  diagonal operations.
- [Numeric-algebra replacement roadmap](galaga-replacement-roadmap.md) records
  remaining numeric capabilities and companion-package work.
- [Native-null conformal geometric algebra](../cga/README.md) documents the
  `p_cga` Gram model, `ConformalModel`, direct objects, semantic CGA operations,
  and transformations.

## Current status

Phases 0 through 7 of the core cutover plan are complete on `galaga_v2`. The
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

Phase 7 is complete. Its compatibility policy is implemented: permanent
concise aliases are exact canonical objects, temporary v1 spellings and the
`gram_bridge` paths warn with executable replacement guidance, ambiguous inner
products remain absent, and redundant generic geometry helpers are classified
for removal. `galaga_matrix` now uses public core-backed linear actions,
basis-independent inertia, and general-Gram-safe mode selection without private
multiplication tables. Mermaid and Marimo now consume public expression,
display, and naming protocols, and the first maintained v2 examples are
executable. `MatrixRepr` now owns frozen matrix-domain provenance and adapts
only public facade names, expressions, and presentations. Installed-wheel
integration gates pass. The 64 maintained Marimo notebooks now use the
promoted top-level API, pass Marimo dependency validation, and execute
headlessly under Python 3.14.

Phase 8 is complete. `galaga.Algebra`,
`galaga.Multivector`, and every other top-level public export are the exact
objects owned by `galaga.facade`. The old table engine is available only as
the explicit `galaga.legacy` oracle; plain `import galaga` does not load it,
and unledgered tests poison its constructors. Clean Python 3.11 wheel tests,
the complete Python 3.11 and 3.14 package suites, and the layer-separated
performance baseline pass. Phase 9 removal of the retained legacy engine is
the next cutover work.

The post-cutover native CGA model layer is also implemented. It validates the
actual `eo`/`einf` Gram basis supplied by `p_cga`, embeds and extracts round
points for arbitrary null-pair scaling, and provides the established CGA
attitude/carrier/center/container vocabulary as model-specific compositions
over the existing generic products.

## Supporting documents

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
- [Historical v2 issue inventory](../../V2-PLANNING.md)

The historical issue inventory predates the Gram-matrix core. It remains useful
for design context, but the core cutover plan and accepted ADRs take precedence
for implementation sequencing.
