---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-123: Migrate Remaining Teaching Notebooks and Benchmark

## Context and problem statement

Physical engine deletion found five tracked teaching notebooks and one
NumPy benchmark still depending on removed APIs. They were outside the
maintained notebook ledger, not established to be disposable. The user chose
to migrate all six, preserving their existing paths and teaching material.

## Decision outcome

Migrate `test_mermaid.py`, `examples/basics/dynamic_notation.py`,
`examples/basics/latex_rewrites_demo.py`,
`examples/basics/galaga_marimo_demo.py`,
`examples/quantum/quantum_physics.py`, and `bench_batched.py` in place.
Do not restore a symbolic adapter, private multiplication table, or old
rendering engine to keep an example running.

### One executable notebook inventory

The existing example-relative ledger gains four notebooks. An explicit
root-notebook allowlist contains only `test_mermaid.py`; the shared
`migrated_notebook_paths(...)` function supplies all 84 notebooks to source
checks, Marimo dependency validation, headless execution, and codemod checks.
The codemod still rejects arbitrary root files and symlinks escaping the
repository. The root notebook uses installed packages without path mutation.
Ruff gives that file a Python 3.14 syntax target without raising the numeric
package's Python requirement. Root pytest collection ignores exactly this
notebook so older Python versions do not parse its t-strings as a test module;
the notebook ledger still executes it on Python 3.14. A subprocess regression
and negative control verify this collection boundary.

### Teach v2 semantics and verify the mathematics

Use eager facade values with optional expression provenance and immutable
names. Replace rotor conveniences with explicit bivector exponentials and
compute the orientation and normalization before writing labels.

- Normalise the Mermaid rotation plane so its slider controls the stated
  angle. Check the EM-field invariant and boost/Wigner factorisation.
- Render reversal with explicit immutable rules. A dagger in this lesson
  means reversal, not an additional conjugation operation.
- Distinguish semantic layout emission from explicit expression
  simplification. Script fractions compact during emission; explicit nested
  groups, negative numerators, and denominator-one fractions remain intact.
  Simplifying a named expression can leave a symbol requiring an environment.
- Use semantic t-string content specs for multivectors and display-policy
  significant-digit precision. Convert a scalar result or query a coefficient
  before using fixed-decimal Python formatting.
- Check spin-state signs, Bloch coordinates, measurement half-angles,
  conditional Stern–Gerlach probabilities, precession direction, reference
  phase invariance, and the double cover against computed values. Qualify the
  SLERP statement to the chosen phase-aligned, same-plane endpoints.

The notebook explanations no longer claim that concrete numeric checks prove
universal symbolic identities. Static prose uses Markdown cells; dynamic
prose uses `galaga_marimo` t-strings.

### Derive batching data from public linear actions

The benchmark constructs `T[i,j,k]` from column `j` of
`algebra.left_action(algebra.blade(i))`. This supports multi-term products for
general Gram matrices as well as the benchmark's spacetime metric. Cached
arrays are read-only. Document the exponential memory cost of this dense
small-algebra technique; it is not a new high-dimensional runtime backend.

## Verification and consequences

Dedicated tests run the actual notebooks at multiple control settings and
check their returned geometric values, including negative controls for the
old unnormalised plane and reversed spin sign. Benchmark tests compare every
basis product, reverse signs, and mixed-grade batched operations against the
public algebra, including oblique, degenerate and null-pair metrics.

This resolves the six-file migration decision recorded in
[ADR-122](122-remove-the-legacy-engine-and-verify-artifacts.md). It does not
change runtime algorithms, the stable-release compatibility retirement,
high-dimensional rotor policy, or publication authority. Validation results
are recorded in the [deletion gate report](../v2/legacy-engine-deletion-gate.md).
