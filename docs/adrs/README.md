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
| [002](002-named-functions-as-api-contract.md) | Named Functions as the Stable API Contract | Accepted |
| [003](003-explicit-inner-product-variants.md) | Explicit Inner Product Variants | Accepted |
| [004](004-two-layer-architecture.md) | Two-Layer Architecture (Numeric + Symbolic) | Superseded by 018 |
| [005](005-separate-marimo-helper-package.md) | Separate Marimo Notebook Helper Package | Accepted |
| [006](006-renderer-supports-repr-latex.md) | Renderer Supports Both .latex() and _repr_latex_() | Accepted |
| [007](007-integer-only-pow.md) | Integer-Only Multivector Exponentiation | Accepted |
| [008](008-commutator-family.md) | Commutator Family — Four Named Functions, No Flags | Accepted |
| [009](009-aliases-are-convenience.md) | Aliases Are Convenience, Not Separate Implementations | Accepted |
| [010](010-complement-vs-dual.md) | Complement vs Dual — Metric-Independent Duality | Accepted |
| [011](011-precomputed-multiplication-tables.md) | Precomputed Multiplication Tables | Accepted |
| [012](012-unicode-repr-opt-in.md) | Unicode Repr with Opt-In Flag | Accepted |
| [013](013-symbolic-drop-in-pattern.md) | Symbolic Drop-In Replacement Pattern | Superseded by 018 |
| [014](014-fixed-point-simplification.md) | Fixed-Point Simplification | Accepted |
| [015](015-uv-workspace-monorepo.md) | uv Workspace for Monorepo | Accepted |
| [016](016-t-string-rendering.md) | T-String Rendering in Marimo Notebooks | Accepted |
| [017](017-doran-lasenby-inner-as-pipe.md) | Doran–Lasenby Inner Product as the \| Operator | Accepted |
| [018](018-unified-naming-evaluation-semantics.md) | Unified Naming and Evaluation Semantics on Multivector | Accepted |
| [019](019-basis-blades-named-eager.md) | Basis Blades as Named Eager Multivectors | Accepted |
| [020](020-lazy-propagation-through-operators.md) | Lazy Propagation Through Operators | Accepted |
| [021](021-lazy-basis-blades.md) | Lazy Basis Blades via basis_vectors(lazy=True) | Accepted |
| [022](022-blade-lookup-dimension-guard.md) | Blade Lookup Rejects Digit-by-Digit Parsing Above 9D | Accepted |
| [023](023-squared-parenthesization.md) | Parenthesization in Squared Rendering | Accepted |
| [024](024-latex-driven-name-derivation.md) | LaTeX-Driven Name Derivation | Accepted |
| [025](025-standalone-renderer.md) | Standalone Precedence-Aware Renderer | Accepted |
| [026](026-expression-nodes-exp-div.md) | Expression Nodes for Exp, Div, ScalarDiv | Accepted |
| [027](027-gp-spacing.md) | Geometric Product Spacing for Multi-Character Names | Accepted |
| [028](028-mutating-configuration-methods.md) | Mutating Symbolic Configuration Methods | Accepted |
| [029](029-configurable-notation.md) | Configurable Notation System | Accepted |
| [030](030-topic-focused-example-notebooks.md) | Topic-Focused Example Notebooks for GA Teaching | Accepted |

## Creating New ADRs

1. Copy the frontmatter and structure from any existing ADR
2. Number sequentially (e.g., `017-your-decision.md`)
3. Fill in all sections
4. Update this index

## Format

All ADRs follow the [MADR](https://adr.github.io/madr/) (Markdown Any Decision Records) format.
