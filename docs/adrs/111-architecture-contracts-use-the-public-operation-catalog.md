---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-111: Architecture Contracts Use the Public Operation Catalog

## Context and problem statement

The two remaining construction-ledger files contain unrelated legacy
contracts. In `test_coverage.py`, seven architecture tests still inspect the
v1 `GA_OPS`, `_SYMBOLIC_HANDLERS` and `_NODE_NAMES` registries. They all pass,
but pin the historical count of 45 operations and use line-based import
checks that miss some relative and nested imports.

[ADR-073](073-move-the-numeric-core-into-galaga.md) keeps the core numeric.
[ADR-077](077-optional-expression-provenance.md) already replaces v1's
operation-specific node classes and callbacks with one shared schema and
generic `Call` nodes. Keeping the old registry checks alive does not guard
that replacement architecture.

## Decision outcome

Extract the seven methods into
`tests/facade/test_architecture_contracts.py`, retaining their class/method
identities. Leave the other 192 methods and all other code in the mixed file
unchanged. No production package behavior changes.

The [archive](../../packages/galaga/tools/baselines/architecture-contracts-v1.json)
retains the complete mixed-file source and SHA-256 digest, its 199 method
identities, the seven migrated identities and new owner, all 45 operation
and node declarations, and all 57 symbolic-handler names. Capture provenance
is `62a9f98`, 2026-09-08, Python 3.14.4 and NumPy 2.5.2. This is historical
evidence, not a runtime registry or a fixed size for the current API.

### Enforce the existing v2 boundaries

- Scan core Python resources recursively and the facade catalog directly,
  resolving absolute and relative imports at every lexical scope. Their
  Galaga imports must point into `galaga.core`. Comments and string literals
  are not imports. Resource traversal also works inside zipped wheels.
- Keep import direction separate from package initialization: this is a
  source-dependency rule, not a promise that Python bypasses `galaga.__init__`
  when importing a submodule. Static checks do not claim to prove arbitrary
  dynamic imports; a fresh-process gate blocks legacy imports on exercised
  paths.
- Check catalog completeness against `core.__all__`, with reasoned exclusions
  and the six structural arithmetic entries. Check operation IDs, callable
  evaluators, immutable specs, facade exports and exact public aliases.
  Do not replace the old magic count with a new magic count.
- Construct generic `Call` nodes for every public numeric operation.
  The catalog also resolves model-specific semantic calls; their separate
  model suites remain the owners of those contracts.
- Distinguish evaluator arity, expression operands and positional parameters.
  For example, `grade` takes one expression operand and a `target` parameter
  but has evaluator arity two; transwedge has two operands plus an order.
  Variadic products still lower to binary left-associated calls.

The tests cover all 71 current public numeric entries with required parameters
alone and with optional controls. They bind the real evaluator signature,
record argument forwarding with a substituted evaluator, and reject missing
parameters, unknown keywords and wrong operand counts. Negative controls
reject catalog omissions, unowned entries, ID mismatches, incomplete
exclusions, incompatible evaluator signatures and reversed operand routing.

### Compute values independently of schema checks

Schema consistency alone cannot establish mathematical correctness. Additional
probes derive `xy` from the Gram pairing and exterior determinant and `xyx`
from `2(x.G.y)x - (x.G.x)y`. They check eager coefficients, parameterized grade
and transwedge calls, binary lowering, scalar norm and predicate result kinds.
Euclidean, oblique-indefinite and degenerate metrics are exercised.

Replay agrees with those values across all three rendering targets and a
temporary functional notation. Changed symbol bindings reverse the product's
exterior part while leaving the original eager value unchanged. A cached-result
mutation is rejected. These refine the existing expression contract without
adding a new teaching API; the migration guide includes an executable
schema/replay example, and existing pedagogical notebooks remain unchanged.

## Consequences

All 203 focused cases pass with 100% line and branch coverage in both files.
The 165 public cases also pass directly from the wheel, including resource
scanning, with all Galaga module origins verified and legacy imports blocked.
Full suites pass 7,071 cases (62 skipped) on Python 3.11 and 7,205 (20 skipped)
on Python 3.14, including maintained notebook exports. Core, facade and
rendering coverage percentages remain unchanged. The existing matrix warning
and 295-error type-check baseline remain.

Markdown lint passes. The repository-wide Ruff 0.16.5 format check additionally
reports code-block formatting in 40 existing Markdown files; checking their
HEAD contents reproduces every finding. This unit does not reformat unrelated
documentation. Python formatting remains checked with the configured exclusions.

This completes one architectural subgroup, not either mixed suite or a release.
The construction ledger therefore remains at two files, `test_coverage.py`
and `test_redesign.py`. Their remaining contracts, namespace/construction
guards, engine deletion and final release gates remain pending.
