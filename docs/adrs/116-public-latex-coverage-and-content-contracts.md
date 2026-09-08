---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-116: Public LaTeX Coverage and Content Contracts

## Context and problem statement

The mixed `test_coverage.py` still contains 43 rendering identities: 29
expression/LaTeX tests, twelve concrete multivector tests and two display
edges. All pass against v1. Some pin older typography, some use zero-valued
orthogonal contractions, and the bare-vector assertion accepts either a
wrong bivector string or a substring of the actual vector output.

[ADR-078](078-shared-semantic-rendering-pipeline.md) separates values,
provenance, content selection and notation. These responsibilities must
survive without restoring the legacy renderer or silently changing v2 defaults.

## Decision outcome

### Preserve historical ownership and computed evidence

Move all 43 original class/method identities to
`tests/rendering/test_coverage_latex_contracts.py`. The other 29 methods
remain in their existing mixed-file owners. No production behavior changes.

The [archive](../../packages/galaga/tools/baselines/coverage-latex-v1.json)
retains the complete source and SHA-256, all 72 source identities, selected
owners and 55 actual rendering calls. Each call records its signature,
coefficients, symbol bindings, node type, name, wrapper and LaTeX output.
Capture provenance is `506cb83`, 2026-09-08, Python 3.14.4 and NumPy 2.5.2.

Every public historical rendering is checked against the archived numeric
result and explicit expression replay. Every archived observation retains a
live owner, including wrappers and repeated calls. The exact bare-vector
assertion removes one redundant rendering from its old permissive `or`;
all other call counts are preserved. Supply complete public blade conventions
for gamma, sigma and custom-label cases, with exact custom-blade assertions.

### Retain explicit content selection and current typography

The accepted spelling differences remain v2's existing wide tilde, wide
hat, overline and floor-shaped contractions. Keep the old output in the
archive and literal accepted strings in the public tests. Do not choose new
defaults or use the archive as a runtime renderer.

`named(...)` preserves provenance, which may be absent. The legacy symbol
examples therefore use `named(...).with_expr()` and explicitly select
expression content. A name alone does not make `content="expr"` display
that name. Automatic content is a teaching equality for named values and
the concrete value for unnamed ones.

Wrapping only adds inline/display math delimiters to the selected content.
Rich LaTeX hooks observe that policy; Python repr selects ASCII. Invalid
wrappers are rejected. Nested notation scopes restore their source context,
including exceptional exits, and cannot change coefficients, hashes or nodes.

### Derive numeric meaning independently of the glyph

Twenty compositions have literal ASCII, Unicode and LaTeX contracts across
Euclidean, oblique-indefinite and degenerate Gram matrices. Derive expected
coefficients from the forced core reference product, grade signs and Gram
minors; solve a left action for inverses. This is independent of facade
composition/replay, not a separate Clifford-algebra implementation.

Nondegenerate samples must be nonzero, including both contraction directions.
Degenerate norm/scalar/sandwich examples retain their actual zeros. Both dual
and undual reject a singular pseudoscalar even though an unbound expression
can still be rendered. A successful rendering does not prove evaluability.

Unit normalization and grade involution retain their conventional shared
hat. Equal notation does not imply equal nodes or values. Functional notation
disambiguates these operations without changing their meaning.

The [presentation notebook](../../examples/galaga_v2/presentation_contexts.py)
teaches these distinctions using a `MatrixRepr` Gram display, computed
normalization/involution values and opposite nonzero vector/bivector
contractions. Its runtime test checks the matrix, coefficients, expression
IDs, replay and generated teaching text. Corruption controls reject altered
archives, lost rendering calls, wrong products, wrong replay and rich hooks
that ignore content selection. A fresh process blocks all legacy imports.

## Verification and consequences

All 329 focused cases pass on Python 3.14 with 100% line/branch coverage in
both files. All 313 public cases pass from the wheel with module origins
verified and legacy imports blocked. Full suites pass 8,732 cases (72 skipped)
on Python 3.11 and 8,876 (20 skipped) on Python 3.14.

Core, facade, expression and rendering coverage are unchanged. Ruff lint,
configured Python formatting and changed-file Markdown lint pass. The guide
recipe executes and all 246 local links in the seven changed Markdown files
resolve. The existing matrix warning, 295 type errors and Markdown code-block
formatting debt remain separate work.

This completes the rendering subgroup, not engine deletion or a release.
The mixed suite retains nine naming cases and twenty rotor/sandwich cases.
It and `test_redesign.py` remain in the construction ledger; namespace
guards, engine deletion and final release gates remain pending.
