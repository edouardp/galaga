---
status: accepted
date: 2026-09-06
deciders: edouard
---

# ADR-093: Benchmarks Use Core Reference Oracles

## Context and problem statement

Phase 9 removes the legacy engine, but the cutover microbenchmark still uses
it both to validate coefficients and to measure a fourth implementation. The
published Phase 8 timing table is useful historical evidence and must survive
without retaining an obsolete numeric implementation.

Using the timed default core operation as its own correctness oracle would
weaken validation. Comparing a fresh timing with an old timing as though both
were measured in one run would also misrepresent the evidence.

## Decision outcome

The benchmark retains its `tools.benchmark_phase8` invocation name, Cl(1,3)
metric, seed, sampling defaults, and dense input distribution. The coefficient
dimension is derived from the algebra. It measures only direct core, untracked
facade, and tracked facade operations.

Before any timing begins, every path must match an untimed oracle:

- geometric product is checked against a public left action from an algebra
  explicitly using the core's dense Chevalley `reference` backend; and
- reverse is checked against the exterior-grade law
  $(-1)^{k(k-1)/2}$, deriving each grade from its coefficient bitmask rather
  than reusing the implementation's cached signs.

The replacement oracles were computed against the retained engine before its
benchmark dependency was removed. With the original deterministic inputs, the
product residual was approximately $1.8\times10^{-15}$ and reverse agreed
exactly. Coefficient validation retains `rtol=0, atol=1e-12`; this does not
change public multivector equality or hashing.

The current report compares facade timings only with direct-core samples from
that same run. The original measurements in
[the Phase 8 baseline](../v2/phase8-performance.md) remain archived and are not
overwritten by the documented rerun command. Historical comparisons require
explicit attention to machine, Python, NumPy, and measurement conditions;
there is no cross-machine timing threshold in the unit tests.

The benchmark test leaves the legacy-execution allowlist. Regression tests
deliberately corrupt each of the six timed paths and require validation to
fail before sampling. A fresh process runs the command with legacy imports
blocked.

## Consequences

- Good, because correctness validation and useful performance measurements
  survive independently of the legacy engine.
- Good, because reference setup is outside the timed region and facade
  overhead remains visible separately from numeric work.
- Good, because no recorded v1 timing is presented as a new measurement.
- Cost, because a fresh same-run v1 comparison now requires a historical
  checkout rather than a compatibility implementation in the current package.
- Boundary, because this retires one legacy dependency; remaining legacy
  tests and the engine itself still need removal before the final release.
