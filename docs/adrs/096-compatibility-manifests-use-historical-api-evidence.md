---
status: accepted
date: 2026-09-07
deciders: edouard
---

# ADR-096: Compatibility Manifests Use Historical API Evidence

> [ADR-130](130-retire-migration-only-api-adapters.md) completes the bridge
> retirement after `2.0.0a4`: the live/retired partition is now 12/24 rather
> than 15/21. The frozen historical evidence and completeness checks remain.

## Context and problem statement

The executable v1 disposition ledger proved completeness by importing and
introspecting the old classes and expression module. That served the overlap
period, but now keeps the obsolete implementation alive just to enumerate its
names. Its submodule import test also treated all migration-era modules as
supported entry points, including legacy implementation files and their
helpers. Importing a helper successfully does not prove v2 compatibility:
some old symbolic decorators defer their engine imports until invocation.

The compatibility policy in [ADR-079](079-curated-compatibility-without-redundant-helpers.md)
must survive deletion. Dropping its tests or deriving historical observations
from the disposition dictionary itself would lose the independent completeness
check.

## Decision outcome

Preserve Python's observed v1 surface in the development-only
[public-surface archive](../../packages/galaga/tools/baselines/public-surface-v1.json).
It was captured at `3dad1cf74be2fa60a9cd6bc3c7e87a005a4fba35`, before
removing introspection, with Python 3.14.4 and NumPy 2.5.2. It records:

- 99 exports, 28 public algebra members, and 20 public multivector members;
- two declared algebra special methods and 22 multivector special methods;
- six observed formatting hooks and seven constructor parameters;
- 59 public expression classes defined in the old expression module; and
- the transitional inventory of 27 top-level modules and 36 successful
  top-level or nested imports.

Exports, members, protocols, parameters, classes, and package files were read
from the implementation, not synthesized from the disposition ledger. The
known formatting-hook names and nested import paths were checked against
actual attributes and imports. Compiler-generated class metadata is omitted,
as in the preceding introspection test. Module importability records the
capture state, not a promise to support those paths in v2.

Tests compare each of the eight historical API groups with its independently
maintained disposition names. They retain archive provenance and count checks,
reject duplicate or malformed observations, and require historical module
paths to retain dispositions. There is no automatic snapshot acceptance or
fallback to live v1 introspection.

Separate the complete `SUBMODULE_DISPOSITIONS` ledger from 15 live
`SUPPORTED_SUBMODULES` and 21 explicitly `LEGACY_ONLY_SUBMODULES`. These
categories must be disjoint and exhaustive. Only current v2 entry points,
including the three warning-emitting bridges, have a live import contract.
The remaining legacy files retain non-importing filesystem presence and
classification checks until the explicit deletion step; those checks must be
updated with the reviewed deletion. Historical dispositions remain afterward.

Current behavior continues to be tested live: top-level facade identity,
constructor forms and invalid combinations, call shapes, exact aliases,
warning text and callsite, expression IDs, explicit removals, and private
dependency checks. All 25 required v2 special methods and the six formatting
hooks are checked on the current class rather than only checking the three
protocol additions to v1.

A fresh process executes the complete surface and deprecation contracts with
every legacy implementation root and its descendants forbidden at import
time. It replaces the ordinary parent conftest's temporary constructor guard
with a stronger import guard. Mutation tests show that missing or invented
dispositions, malformed evidence, lost v2 methods, namespace identity changes,
partition errors, and new or missing package modules are rejected.

## Consequences and boundaries

- Good, because the old API remains independently documented and checked
  without loading the implementation that is scheduled for deletion.
- Good, because archiving history does not freeze current v2 behavior or
  promote obsolete helper modules into supported compatibility APIs.
- Boundary, because this changes test evidence and inventory classification,
  not production imports, arithmetic, deprecation timing, or public exports.
- Boundary, because the archive is a development fixture, outside the wheel's
  `galaga` package, and requires deliberate review if corrected.
- Pending, because nineteen files still belong to the numeric-construction
  legacy ledger. This manifest was never on that list: removing its import
  dependency does not reduce the construction count. Other namespace guards,
  legacy tests, engine deletion, and release artifact gates remain separate.
