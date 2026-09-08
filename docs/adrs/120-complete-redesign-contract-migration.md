---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-120: Complete Redesign Contract Migration

The subsequent namespace/guard unit is complete in
[ADR-121](121-deletion-ready-namespace-and-import-guards.md): the empty ledger
is enforced by an import guard that no longer loads the legacy engine.

## Context and problem statement

`test_redesign.py` is the final construction-only legacy exemption. All 279
tests pass before migration. They mix numeric operations already owned by
stronger public tests with mutable naming, implicit symbolic state and old
rendering contracts. Preserving 279 duplicate wrappers would obscure which
v2 contracts actually replace those behaviors.

## Decision outcome

### Preserve evidence and consolidate by public responsibility

Archive the complete source, SHA-256, ordered 279 identities, final local
observations and object-alias relationships in
[redesign-v1.json](../../packages/galaga/tools/baselines/redesign-v1.json).
Its 189 deduplicated snapshots retain actual values, names and rendering,
including errors. Capture used commit `0499fa4`, Python 3.14.4 and NumPy 2.5.2
on 2026-09-08. Earlier intermediate states remain documented in the complete
source; the snapshots do not claim to trace every intermediate operation.

Use an explicit
[ownership crosswalk](../../packages/galaga/tools/baselines/redesign-v2-owners.json):
every historical identity occurs once in one of 27 reviewed responsibility
groups, each with a decision and exact collected public test owners. Existing
stronger mixed-grade/Gram, expression, scalar, inner-product, rendering and
rotor tests consolidate overlapping operations. New tests own the unique
state/display contracts and replay all ten archived workflow results.
This follows the consolidation policy in the numeric migration inventory;
test counts need not remain one-to-one.

Validate the crosswalk against archived source identities and actual pytest
collection, then execute all its owner files with legacy imports blocked.
Negative controls reject missing/duplicate/fictitious ownership and corrupted
coefficients. Do not equate a surviving filename with tested behavior.

### Make accepted semantic differences explicit

- All values use immutable wrappers. There is no protected-basis versus
  in-place-arithmetic naming split. `named` preserves numeric storage and
  existing provenance; `unnamed` and `without_expr` remove different metadata.
  A named operand can track again after `without_expr`. Remove both for a
  full numeric snapshot. `with_expr` chooses a name leaf when named.
- Explicit `Name` variants preserve whitespace; bounded `Name.from_latex`
  conversion is opt-in. Lazy flags, `Sym/sym`, grade promises and mutating
  `name/eager/anon/reveal/copy_as` are not restored.
- Blade labels live in complete immutable conventions and scoped views.
  Default ten-dimensional `e110` lookup resolves a complete label; it is
  not the old digit parser. Invalid/ambiguous conventions remain errors.
- Display content is explicit. Auto shows full named values and concrete
  anonymous values; `display` returns a string snapshot, not an object with
  a `latex` method. Numeric precision also applies to literals in expression
  rendering, without changing their stored coefficients or structure.
- Integer powers have a `power` call. Whole product operands are grouped.
  Default plain-text products juxtapose even multicharacter names; use an
  explicit infix rule when a visible separator is needed.
- Bare nodes need explicit calls and replay contexts. Simplification cannot
  use old bindings to assume grades or replace `R * reverse(R)` with one.
  The old seventh “rotor” recipe omitted `exp`; retain its scaled-generator
  observation and separately test the actual exponential and its rotation.

The discovered division defects are fixed and documented separately in
[ADR-119](119-division-provenance-and-exact-scalar-dispatch.md).
The high-dimensional `is_rotor` limitation and release decision in
[ADR-118](118-public-rotor-recipes-and-sandwich-contracts.md) are unchanged.

### Close the exemption, not the entire cutover

Keep `test_redesign.py` as an import-free ownership record with no collected
duplicates. The construction ledger is now empty, and the isolation codemod
cannot rewrite that path in either check or write mode. Empty-ledger
execution is a no-op even for a nonexistent repository.

Do not remove the guard or legacy engine in this unit. Namespace/construction
guards, obsolete engine deletion and release gates are next. Extend the
existing eager-values notebook rather than adding another introduction.
No release or changelog update is implied.

## Verification and consequences

New public contracts cover state transitions across three Gram matrices and
both expression modes, all ten historical workflows, actual rotation,
rebound grades, three-target content and scope, power and name separation.
Archive/crosswalk corruption tests and a headless notebook test guard the
migration itself. Full source/wheel, lint and coverage results are recorded
in the [migration inventory](../v2/numeric-test-migration-inventory.md).
