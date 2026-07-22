---
status: accepted
date: 2026-07-19
deciders: edouard
---

# ADR-083: Maintained Notebooks Are Executable Integration Contracts

## Context and problem statement

The older Marimo gallery was written for Galaga 1's mutable names, lazy or
symbolic values, explicit `.eval()`/`.reveal()`, mutable notation, and top-level
imports. Its existing test compiled a manually maintained list but also
required those legacy patterns, so it characterized the old architecture
rather than proving Galaga 2 integration.

Notebook migration is riskier than a textual API rename. Python compilation
cannot detect Marimo dependency cycles or private cross-cell values, and it
cannot prove that a rendered cell executes. Matrix rendering objects also own
a valid `.name()` protocol that must not be confused with the removed
multivector method.

## Decision drivers

- Make the exact maintained gallery visible and executable.
- Prevent an automated rewrite from touching unrelated historical examples.
- Automate only structural transformations and preserve semantic review.
- Keep matrix-domain naming independent of multivector naming.
- Validate Python 3.14 t-strings without raising Galaga's Python 3.11 minimum.
- Treat cell execution, not compilation alone, as integration evidence.

## Decision outcome

`tools.migrate_v2_notebooks.MIGRATED_NOTEBOOKS` is the single 64-file gallery
ledger. The migration command refuses paths outside that tuple and supports a
non-writing `--check` mode.

A tested, idempotent LibCST transformation moves the ledger to
`galaga.facade`, eager values with optional expression provenance, immutable
semantic names, explicit Marimo `:expr`/`:value` content, and raw t-strings.
Negative-space tests preserve `MatrixRepr`, `QuatMatrixRepr`, and matrix
conversion naming.

Semantic changes remain reviewed source edits. Notebooks use complete presets
where their presentation matters, compose removed geometry helpers from core
operations, configure notation immutably, and expose intentional Marimo
cross-cell dependencies with public names.

Repository tests validate the same ledger in four stages: Python 3.11
architecture and codemod checks, Python 3.14 compilation, Marimo dependency
validation, and headless execution of every notebook. Any failed cell fails
the runtime gate.

## Consequences

- Good, because “maintained notebook” now means the file executes against the
  Galaga 2 facade.
- Good, because the ledger, codemod scope, architecture checks, and runtime
  gate cannot silently drift to different file sets.
- Good, because runtime checks catch reactive-program errors that Python's
  compiler cannot see.
- Good, because `MatrixRepr` keeps its own coherent naming API.
- Good, because Python 3.14 remains isolated to notebook validation and the
  optional Marimo package.
- Cost, because the Python 3.14 gate executes 64 notebooks and is heavier than
  a compile-only test.
- Cost, because additions to the maintained gallery must satisfy facade,
  Marimo structure, and headless runtime contracts.
