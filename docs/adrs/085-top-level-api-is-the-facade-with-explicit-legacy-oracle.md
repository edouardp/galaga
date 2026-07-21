---
status: accepted
date: 2026-07-21
deciders: edouard
---

# ADR-085: Top-Level API Is the Facade with an Explicit Legacy Oracle

## Context and problem statement

Phases 0 through 7 proved the Gram-matrix core, completed the composition
facade, rebuilt presentation and expression provenance, and ported semantic
rendering and companion integrations. Ordinary `import galaga` nevertheless
continued to construct the table-backed Galaga 1 types. The facade was proven
but was not yet the package users received by default.

Phase 8 still needs Galaga 1 as a behavioral and rendering oracle. Leaving it
at the top level would prevent a real cutover, while deleting it immediately
would remove the independent comparison surface before the shadow and
packaging gates complete.

Two old modules also used names that are public facade functions:
`galaga.render` and `galaga.simplify`. Python assigns an imported submodule to
its parent package attribute. Retaining either module at that path would make
`galaga.render` or `galaga.simplify` change from a function to a module based
only on import order.

## Decision drivers

- Make ordinary Galaga construction use the proven core-backed implementation.
- Keep exactly one owner for every Galaga 2 public object.
- Preserve a coherent Galaga 1 oracle during Phase 8 without implicit mixing.
- Make accidental legacy execution fail in tests.
- Keep the public export manifest mechanically synchronized.
- Eliminate package attribute behavior that depends on submodule import order.

## Decision outcome

The top-level `galaga` package re-exports every object in
`galaga.facade.__all__`. These are the same objects, not wrappers, subclasses,
or duplicated implementations. `galaga.facade` remains the permanent explicit
composition-layer namespace and `galaga.core` remains the presentation-free
numeric namespace.

Galaga 1 is available deliberately through `galaga.legacy` for Phase 8. It
exports the former 99-name top-level v1 surface as one coherent value domain.
Legacy algebras, multivectors, and operations must be used together and are
not implicitly coerced into Galaga 2 values. The namespace is scheduled for
removal with the table engine in Phase 9.

The old renderer and simplifier move to `galaga.legacy.render` and
`galaga.legacy.simplify`. This preserves oracle access while ensuring the
top-level `render` and `simplify` functions retain facade identity for every
import order. Legacy rendering is loaded lazily to keep the retained v1 module
cycle import-order independent.

The Phase 8 test boundary is executable:

- a LibCST codemod and allowlisted ledger move actual v1 test imports to
  `galaga.legacy` without changing strings or comments;
- ledgered oracle tests receive an explicit `legacy_oracle` marker;
- every other Galaga test poisons both legacy numeric constructors;
- subprocess tests prove plain `import galaga` loads no legacy engine module;
- import-contract tests prove every top-level export is identical to its
  facade owner; and
- maintained notebooks use the promoted top-level API, while internal
  integrations may retain an explicit facade import when that architectural
  dependency is intentional.

## Consequences

- Good, because `from galaga import Algebra` now constructs the Gram-based
  Galaga 2 facade.
- Good, because `galaga.Algebra is galaga.facade.Algebra` and the same identity
  rule covers the complete public manifest.
- Good, because the legacy oracle remains available without occupying the
  ordinary API or being loaded by a plain import.
- Good, because new tests use Galaga 2 by default and cannot silently fall back
  to the table engine.
- Good, because the `render` and `simplify` names no longer change type after a
  compatibility-module import.
- Cost, because v1-only tests and comparisons must opt into an executable
  ledger entry.
- Cost, because direct `galaga.render` and `galaga.simplify` module imports move
  to the explicitly temporary `galaga.legacy` namespace.
- Cost, because Galaga 1 and Galaga 2 values deliberately do not interoperate;
  migration code must choose one domain at each operation boundary.
