---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-121: Deletion-Ready Namespace and Import Guards

Subsequent physical deletion and wheel/sdist gates are recorded in
[ADR-122](122-remove-the-legacy-engine-and-verify-artifacts.md).

## Context and problem statement

[ADR-120](120-complete-redesign-contract-migration.md) emptied the legacy
construction ledger, but the guard itself still imported the old classes to
poison their constructors. Namespace, alias and shared-symbolic tests also
depended on live v1 modules. A collection-time import guard exposed one more
dependency: `test_latex_tree.py` constructs no algebras, so constructor
poisoning never detected its old renderer imports.

These dependencies must have permanent public owners before deleting the
engine. Removing tests or silently retaining optional-import fallbacks would
not establish that boundary.

## Decision outcome

### Reject imports without loading the retired implementation

Use the test-only
[legacy_import_boundary.py](../../packages/galaga/tools/legacy_import_boundary.py)
helper. Its fifteen root prefixes cover all twenty-one retired paths in the
compatibility manifest. Exact roots and descendants are rejected; similarly
named supported modules are not.

Pytest installs the finder before collection and removes its own installation
at configuration cleanup. Cache checks reject already-loaded modules,
including failed-import sentinels, before installation, after collection,
around tests and after session-fixture teardown. They never evict modules or
rewrite another finder's state. Raise an assertion error, not `ImportError`,
so an optional-import fallback cannot mask a dependency.

The construction ledger must stay empty. Any `legacy_oracle` marker, including
an inherited module marker, is a collection error, not an exemption.
A recursive AST check additionally rejects direct retired imports in test
and test-tool code, including inactive or nested scopes.
This is a regression guard, not a security boundary against arbitrary Python.

Namespace tests assert actual core ownership, Gram-derived products and
explicit replay. Foreign objects cannot cross the typed value boundary.
Recursive resource-based architecture checks work with source directories
and zipped wheels: the core stays inward-only; the facade may use its planned
v2 presentation/expression layers but not retired layers or private product
tables. `galaga.gram_bridge` remains the existing same-object warning adapter.

### Preserve evidence and make replacement contracts explicit

[namespace-boundaries-v1.json](../../packages/galaga/tools/baselines/namespace-boundaries-v1.json)
retains seven selected source records with digests and twenty-nine historical
test identities, plus namespace, alias and symbolic observations. Five renamed
tests have an explicit owner mapping; the eleven symbolic identities remain
collected under their historical names with corrected contract descriptions.

- `Name` variants are explicit; plain whitespace is preserved and bounded
  LaTeX conversion is opt-in.
- `Symbol` owns an identifier/name, not a cached value or private v1 fields.
  `ScalarLiteral.value` is immutable. Both need explicit evaluation contexts.
- Declared `Call` nodes and the immutable catalog replace the private
  `SymbolicDomain` registry. Arbitrary node subclasses are not extension hooks.
- Public alias identity follows the curated v2 catalog, not the archived v1
  function pairs; `antiwedge` retains its own operation identity.

[latex-tree-v1.json](../../packages/galaga/tools/baselines/latex-tree-v1.json)
retains the complete source, digest, forty-five historical identities and
actual tree/output observations, captured after executing every original
case. Each identity has a collected immutable semantic-tree replacement.

Existing v2 layout choices are intentional: `Text` escapes literal text;
`Identifier(Name(...))` supplies mathematical spelling. Semantic products,
sums and explicit separators replace untyped sequences. Fractions use
ordinary bars outside scripts and compact slash layout inside exponents,
without a `small` flag or separate rewrite pass. Emission preserves explicit
nested groups, a negative numerator and a denominator of one. It does not
perform the old sign-hoisting, group-collapse or fraction-one rewrites.
Script braces and separator spacing may differ from v1.

This refines the executable migration boundary from
[ADR-075](075-promote-the-core-backed-facade.md) and completes the remaining
low-level tree ownership under
[ADR-078](078-shared-semantic-rendering-pipeline.md), without changing the
production renderer, numeric engine or expression model.

## Verification and consequences

Positive and negative tests exercise real isolated pytest collection, test
bodies, fixture setup/teardown, cached modules, optional fallbacks, retired
markers, ledger drift, finder cleanup and source/owner corruption.
Full source suites run under the new guard; fresh-wheel checks verify loaded
module origins. Exact results and coverage are recorded in the
[migration inventory](../v2/numeric-test-migration-inventory.md).

No production behavior or notebook changes are needed for this infrastructure
unit. The existing eager-value and presentation lessons remain the teaching
owners; the migration guide documents the low-level API differences.
Legacy files still ship. Physical engine deletion, alias retirement and final
release gates remain separate work. The high-dimensional `is_rotor` release
decision in [ADR-118](118-public-rotor-recipes-and-sandwich-contracts.md) is
unchanged.
