# Architectural Decision Records

This directory contains Architectural Decision Records (ADRs) for the `galaga`
geometric algebra project.

## What are ADRs?

ADRs document significant architectural decisions made during the project. They
capture the context, options considered, decision made, and consequences. This
helps future contributors understand why certain choices were made.

## ADR Index

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
| [040](040-pyrefly-type-checking.md) | Pyrefly for Type Checking | Accepted |
| [041](041-pre-commit-hooks.md) | Pre-commit Hooks for Automated Quality Gates | Accepted |
| [042](042-scalar-sqrt.md) | scalar_sqrt as a Symbolic-First Convenience | Accepted |
| [043](043-notation-first-rendering.md) | Notation-First Rendering Architecture | Accepted |
| [044](044-remove-standalone-scalar.md) | Remove Standalone scalar() Function | Accepted |
| [045](045-near-unit-display-tolerance.md) | Near-Unit Coefficient Display Tolerance | Accepted |
| [046](046-remove-symbolic-dropins.md) | Remove Symbolic Drop-in Function Replacements | Accepted |
| [047](047-sym-inner-expr.md) | Sym Inner Expression for Structural Rendering Decisions | Accepted |
| [048](048-unit-fraction-notation.md) | unit_fraction Notation Kind | Accepted |
| [049](049-defer-poincare-dual.md) | Defer Poincaré/Hodge Dual as Separate Function | Deferred |
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
| [067](067-strip-whitespace-from-latex-names.md) | Strip Whitespace from LaTeX Names | Accepted |
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

## Creating New ADRs

1. Copy the frontmatter and structure from any existing ADR
2. Number sequentially (e.g., `017-your-decision.md`)
3. Fill in all sections
4. Update this index

## Format

All ADRs follow the [MADR](https://adr.github.io/madr/) (Markdown Any Decision Records) format.
