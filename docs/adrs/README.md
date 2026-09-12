# Architectural Decision Records

This directory contains Architectural Decision Records (ADRs) for the `galaga`
geometric algebra project.

## What are ADRs?

ADRs document significant architectural decisions made during the project. They
capture the context, options considered, decision made, and consequences. This
helps future contributors understand why certain choices were made.

## ADR Index

Statuses record acceptance at the time, not a promise that old modules or API
spellings remain available. Early Galaga 1 implementation records retain their
chronology; the [core specifications](../core/specs/README.md),
[v2 architecture](../v2/README.md) and later superseding ADRs define current
behavior. In particular, the table engine, mutable naming and legacy expression
classes are no longer production alternatives.

| ADR | Title | Status |
|-----|-------|--------|
| [001](001-use-architectural-decision-records.md) | Use Architectural Decision Records | Accepted |
| [002](002-named-functions-as-api-contract.md) | Named Functions as the Stable API Contract | Partially superseded by 074 |
| [003](003-explicit-inner-product-variants.md) | Explicit Inner Product Variants | Accepted |
| [004](004-two-layer-architecture.md) | Two-Layer Architecture (Numeric + Symbolic) | Superseded by 018 |
| [005](005-separate-marimo-helper-package.md) | Separate Marimo Notebook Helper Package | Accepted |
| [006](006-renderer-supports-repr-latex.md) | Renderer Supports Both .latex() and _repr_latex_() | Accepted |
| [007](007-integer-only-pow.md) | Integer-Only Multivector Exponentiation | Accepted |
| [008](008-commutator-family.md) | Commutator Family — Four Named Functions, No Flags | Accepted |
| [009](009-aliases-are-convenience.md) | Aliases Are Convenience, Not Separate Implementations | Partially superseded by 074 |
| [010](010-complement-vs-dual.md) | Complement vs Dual — Metric-Independent Duality | Accepted |
| [011](011-precomputed-multiplication-tables.md) | Precomputed Multiplication Tables | Accepted |
| [012](012-unicode-repr-opt-in.md) | Unicode Repr with Opt-In Flag | Superseded by 033 |
| [013](013-symbolic-drop-in-pattern.md) | Symbolic Drop-In Replacement Pattern | Superseded by 018 |
| [014](014-fixed-point-simplification.md) | Fixed-Point Simplification | Accepted |
| [015](015-uv-workspace-monorepo.md) | uv Workspace for Monorepo | Accepted |
| [016](016-t-string-rendering.md) | T-String Rendering in Marimo Notebooks | Accepted |
| [017](017-doran-lasenby-inner-as-pipe.md) | Doran–Lasenby Inner Product as the \| Operator | Accepted |
| [018](018-unified-naming-evaluation-semantics.md) | Unified Naming and Evaluation Semantics on Multivector | Partially superseded by 028 |
| [019](019-basis-blades-named-eager.md) | Basis Blades as Named Eager Multivectors | Accepted |
| [020](020-lazy-propagation-through-operators.md) | Lazy Propagation Through Operators | Accepted |
| [021](021-lazy-basis-blades.md) | Symbolic Basis Blades via basis_vectors(symbolic=True) | Accepted |
| [022](022-blade-lookup-dimension-guard.md) | Blade Lookup Rejects Digit-by-Digit Parsing Above 9D | Accepted |
| [023](023-squared-parenthesization.md) | Parenthesization in Squared Rendering | Accepted |
| [024](024-latex-driven-name-derivation.md) | LaTeX-Driven Name Derivation | Accepted |
| [025](025-standalone-renderer.md) | Standalone Precedence-Aware Renderer | Accepted |
| [026](026-expression-nodes-exp-div.md) | Expression Nodes for Exp, Div, ScalarDiv | Accepted |
| [027](027-gp-spacing.md) | Geometric Product Spacing for Multi-Character Names | Accepted |
| [028](028-mutating-configuration-methods.md) | Mutating Symbolic Configuration Methods | Superseded by 076 for Galaga 2 |
| [029](029-configurable-notation.md) | Configurable Notation System | Accepted |
| [030](030-topic-focused-example-notebooks.md) | Topic-Focused Example Notebooks | Accepted |
| [031](031-complement-based-regressive-product.md) | Complement-Based Regressive Product | Accepted |
| [032](032-dynamic-basis-blade-renaming.md) | Dynamic BasisBlade Renaming | Superseded by 057 |
| [033](033-unicode-repr-default.md) | Unicode repr() by Default | Accepted |
| [034](034-three-phase-latex-pipeline.md) | Three-Phase LaTeX Render Pipeline | Accepted |
| [035](035-ruff-linting.md) | Ruff for Python Linting and Formatting | Accepted |
| [036](036-shellcheck.md) | Shellcheck for Shell Script Linting | Accepted |
| [037](037-bandit-security.md) | Bandit for Security Scanning | Accepted |
| [038](038-rumdl-markdown.md) | Rumdl for Markdown Linting | Accepted |
| [039](039-pip-audit.md) | Pip-audit for Dependency Vulnerability Scanning | Accepted |
| [040](040-pyrefly-type-checking.md) | Pyrefly for Type Checking | Tool accepted; advisory policy superseded by 131 |
| [041](041-pre-commit-hooks.md) | Pre-commit Hooks for Automated Quality Gates | Accepted |
| [042](042-scalar-sqrt.md) | scalar_sqrt as a Symbolic-First Convenience | Accepted |
| [043](043-notation-first-rendering.md) | Notation-First Rendering Architecture | Accepted |
| [044](044-remove-standalone-scalar.md) | Remove Standalone scalar() Function | Accepted |
| [045](045-near-unit-display-tolerance.md) | Near-Unit Coefficient Display Tolerance | Accepted |
| [046](046-remove-symbolic-dropins.md) | Remove Symbolic Drop-in Function Replacements | Accepted |
| [047](047-sym-inner-expr.md) | Sym Inner Expression for Structural Rendering Decisions | Accepted |
| [048](048-unit-fraction-notation.md) | unit_fraction Notation Kind | Accepted |
| [049](049-defer-poincare-dual.md) | Defer Poincaré/Hodge Dual as Separate Function | Superseded by core ADR-005; rationale corrected |
| [050](050-latex-scientific-notation.md) | LaTeX Scientific Notation via LNodes and Notation Setting | Accepted |
| [051](051-scalar-constants.md) | Algebra Scalar Constants and Fractions | Accepted |
| [052](052-general-multivector-inverse.md) | General Multivector Inverse via Hitzer/Shirokov | Accepted |
| [053](053-general-sqrt-study-number.md) | General Square Root via Study Number Decomposition | Accepted |
| [054](054-outer-transcendentals.md) | Outer (Wedge) Transcendental Functions | Accepted |
| [055](055-dual-constructor-pqr.md) | Dual Constructor — Signature or Cl(p,q,r) | Accepted |
| [056](056-real-clifford-algebras-only.md) | Real Clifford Algebras Only | Accepted |
| [057](057-blade-convention.md) | BladeConvention Replaces names= Parameter | Accepted |
| [058](058-basis-blades-and-locals.md) | basis_blades(k) and locals() for Bulk Blade Access | Accepted |
| [059](059-display-ordering.md) | Custom Basis Blade Display Ordering | Accepted |
| [060](060-chisolm-reference-test-suite.md) | Chisolm Reference Test Suite | Accepted |
| [061](061-algebra-display-mode.md) | Algebra Display Mode | Accepted |
| [062](062-rename-lazy-to-symbolic.md) | Rename Lazy to Symbolic | Accepted |
| [063](063-suppress-unit-scalar-mul.md) | Suppress Unit Scalar Multiplication | Accepted |
| [064](064-relative-imports-in-packages.md) | Use Relative Imports Within Packages | Accepted |
| [065](065-operation-registry.md) | Operation Registry Breaks algebra↔expr Circular Dependency | Accepted |
| [066](066-grade-propagation-and-float.md) | Grade Propagation via @ga_op and \_\_float\_\_ Conversion | Accepted |
| [067a](067-basis-vector-protection.md) | Basis Vectors Are Protected from In-Place Mutation | Superseded by 077 |
| [067b](067-strip-whitespace-from-latex-names.md) | Strip Whitespace from LaTeX Names | Accepted |
| [068](068-recognize-known-mvs.md) | Recognize Known Multivectors in Display | Accepted |
| [069](069-quaternion-bivector-assignment.md) | Quaternion Bivector Assignment | Accepted |
| [070](070-pedagogical-convention-explicit-scope.md) | Pedagogical and Convention-Explicit Scope | Accepted |
| [071](071-exterior-algebra-convention-layer.md) | Terathon/RGA Exterior-Algebra Convention Layer | Accepted |
| [072](072-build-galaga-v2-over-gram.md) | Build Galaga 2.0 over the Gram Numeric Core | Superseded by 073 |
| [073](073-move-the-numeric-core-into-galaga.md) | Move the Numeric Core into the Galaga Package | Accepted |
| [074](074-long-operation-names-are-canonical.md) | Long Operation Names Are Canonical in Galaga 2 | Accepted |
| [075](075-promote-the-core-backed-facade.md) | Promote the Core-Backed Facade Namespace | Accepted |
| [076](076-immutable-presentation-configuration.md) | Immutable Presentation Configuration and Context-Local Overrides | Accepted |
| [077](077-optional-expression-provenance.md) | Optional Expression Provenance over Eager Facade Values | Accepted |
| [078](078-shared-semantic-rendering-pipeline.md) | Shared Semantic Rendering Pipeline | Accepted |
| [079](079-curated-compatibility-without-redundant-helpers.md) | Curated Compatibility without Redundant Generic Helpers | Accepted |
| [080](080-matrix-representations-use-public-linear-actions.md) | Matrix Representations Use Public Linear Actions | Accepted |
| [081](081-optional-integrations-consume-public-protocols.md) | Optional Integrations Consume Public Protocols | Accepted |
| [082](082-matrix-provenance-is-package-owned.md) | Matrix Provenance Is Package-Owned | Accepted |
| [083](083-maintained-notebooks-are-executable-integration-contracts.md) | Maintained Notebooks Are Executable Integration Contracts | Accepted |
| [084](084-exact-configured-rendering-contracts.md) | Exact Configured Rendering Contracts | Accepted |
| [085](085-top-level-api-is-the-facade-with-explicit-legacy-oracle.md) | Top-Level API Is the Facade with an Explicit Legacy Oracle | Accepted |
| [086](086-native-null-cga-is-a-validated-model-layer.md) | Native-Null CGA Is a Validated Model Layer | Accepted |
| [087](087-rga-semantics-are-a-validated-model-layer.md) | RGA Semantics Are a Validated Model Layer | Accepted |
| [088](088-explicit-versions-for-prereleases.md) | Explicit Versions for Prereleases | Accepted |
| [089](089-releases-use-any-clean-tracked-branch.md) | Releases Use Any Clean Tracked Branch | Accepted |
| [090](090-portable-notebooks-use-a-local-editable-launcher.md) | Portable Notebooks Use a Local Editable Launcher | Accepted |
| [091](091-cga-anywidget-synchronizes-semantic-coordinates.md) | CGA AnyWidget Synchronizes Semantic Coordinates | Accepted |
| [092](092-frozen-historical-rendering-oracles.md) | Frozen Historical Rendering Oracles | Accepted |
| [093](093-benchmarks-use-core-reference-oracles.md) | Benchmarks Use Core Reference Oracles | Accepted |
| [094](094-numeric-contracts-outlive-the-legacy-engine.md) | Numeric Contracts Outlive the Legacy Engine | Accepted |
| [095](095-exact-numeric-equality-and-compatible-hashes.md) | Exact Numeric Equality and Compatible Hashes | Accepted |
| [096](096-compatibility-manifests-use-historical-api-evidence.md) | Compatibility Manifests Use Historical API Evidence | Accepted |
| [097](097-concrete-display-contracts-outlive-legacy-rendering.md) | Concrete Display Contracts Outlive Legacy Rendering | Accepted |
| [098](098-expression-contracts-outlive-legacy-provenance.md) | Expression Contracts Outlive Legacy Provenance | Accepted |
| [099](099-symbolic-contracts-and-curated-unary-properties.md) | Symbolic Contracts and Curated Unary Properties | Accepted |
| [100](100-explicit-bounded-latex-name-conversion.md) | Explicit Bounded LaTeX Name Conversion | Accepted |
| [101](101-immutable-notation-contracts-and-unit-fraction-layout.md) | Immutable Notation Contracts and Unit-Fraction Layout | Accepted |
| [102](102-latex-contracts-and-script-safe-spelling.md) | LaTeX Contracts and Script-Safe Spelling | Accepted |
| [103](103-mixed-rendering-contracts-with-numeric-ownership.md) | Mixed Rendering Contracts with Numeric Ownership | Accepted |
| [104](104-metric-derived-sta-names-and-public-blade-contracts.md) | Metric-Derived STA Names and Public Blade Contracts | Accepted |
| [105](105-public-rga-contracts-and-underaccent-fallback.md) | Public RGA Contracts and Under-Accent Fallback | Accepted |
| [106](106-independent-public-local-name-contracts.md) | Independent Public Local-Name Contracts | Accepted |
| [107](107-public-complex-and-quaternion-convention-contracts.md) | Public Complex and Quaternion Convention Contracts | Accepted |
| [108](108-public-transformation-compositions-and-geometric-notebook-plots.md) | Public Transformation Compositions and Geometric Notebook Plots | Accepted |
| [109](109-public-scalar-compositions-and-small-value-contracts.md) | Public Scalar Compositions and Small-Value Contracts | Accepted |
| [110](110-public-factory-and-display-edge-contracts.md) | Public Factory and Display Edge Contracts | Accepted |
| [111](111-architecture-contracts-use-the-public-operation-catalog.md) | Architecture Contracts Use the Public Operation Catalog | Accepted |
| [112](112-explicit-inner-product-contracts-outlive-mode-dispatch.md) | Explicit Inner-Product Contracts Outlive Mode Dispatch | Accepted |
| [113](113-eager-operation-contracts-outlive-mixed-symbolic-tests.md) | Eager Operation Contracts Outlive Mixed Symbolic Tests | Accepted |
| [114](114-grade-inspection-and-bounded-simplification-contracts.md) | Grade Inspection and Bounded Simplification Contracts | Accepted |
| [115](115-public-expression-identity-and-helper-contracts.md) | Public Expression Identity and Helper Contracts | Accepted |
| [116](116-public-latex-coverage-and-content-contracts.md) | Public LaTeX Coverage and Content Contracts | Accepted |
| [117](117-public-naming-presets-and-exterior-word-contracts.md) | Public Naming Presets and Exterior-Word Contracts | Accepted |
| [118](118-public-rotor-recipes-and-sandwich-contracts.md) | Public Rotor Recipes and Sandwich Contracts | Accepted |
| [119](119-division-provenance-and-exact-scalar-dispatch.md) | Division Provenance and Exact Scalar Dispatch | Accepted |
| [120](120-complete-redesign-contract-migration.md) | Complete Redesign Contract Migration | Accepted |
| [121](121-deletion-ready-namespace-and-import-guards.md) | Deletion-Ready Namespace and Import Guards | Accepted |
| [122](122-remove-the-legacy-engine-and-verify-artifacts.md) | Remove the Legacy Engine and Verify Artifacts | Accepted |
| [123](123-migrate-remaining-teaching-notebooks-and-benchmark.md) | Migrate Remaining Teaching Notebooks and Benchmark | Accepted |
| [124](124-rotor-predicate-requires-vector-preservation.md) | Rotor Predicate Requires Vector Preservation | Accepted |
| [125](125-separate-algebra-logarithms-from-rotor-generators.md) | Separate Algebra Logarithms from Rotor Generators | Accepted |
| [126](126-align-static-types-with-existing-numeric-contracts.md) | Align Static Types with Existing Numeric Contracts | Accepted |
| [127](127-renderable-native-bilinear-form-tables.md) | Renderable Native Bilinear Form Tables | Accepted |
| [128](128-wedge-product-tables-and-grade-colours.md) | Wedge Product Tables and Grade Colours | Accepted |
| [129](129-concise-complete-and-resolvable-blade-presets.md) | Concise Complete and Resolvable Blade Presets | Accepted |
| [130](130-retire-migration-only-api-adapters.md) | Retire Migration-Only API Adapters | Accepted |
| [131](131-local-only-stable-release-validation.md) | Local-Only Stable Release Validation | Accepted |
| [132](132-algebra-expression-tracking-default.md) | Algebra-Level Expression Tracking Default | Accepted |
| [133](133-grade-lexicographic-default-display-order.md) | Grade-Then-Lexicographic Default Display Order | Accepted |

## Creating New ADRs

1. Copy the frontmatter and structure from any existing ADR
2. Number sequentially (e.g., `017-your-decision.md`)
3. Fill in all sections
4. Update this index

## Format

All ADRs follow the [MADR](https://adr.github.io/madr/) (Markdown Any Decision Records) format.
