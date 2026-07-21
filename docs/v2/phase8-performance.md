# Phase 8 Performance Baseline

This is a local microbenchmark, not a cross-machine release threshold. It
separates the numeric engine from facade wrapping and optional expression
provenance. Every timed path is first checked against the same legacy
Cl(1,3) coefficients.

- Python: 3.11.15 (CPython)
- Platform: macOS-26.5.2-arm64-arm-64bit
- NumPy: 2.4.6
- Samples: median of 7 repeats × 2000 calls
- Seed: `20260721`

| Operation | Implementation | Median µs | vs direct core | vs legacy v1 |
|---|---|---:|---:|---:|
| geometric product | legacy-v1 | 15.534 | 0.92× | 1.00× |
| geometric product | direct-core | 16.947 | 1.00× | 1.09× |
| geometric product | facade-untracked | 18.518 | 1.09× | 1.19× |
| geometric product | facade-tracked | 20.576 | 1.21× | 1.32× |
| reverse | legacy-v1 | 3.004 | 1.64× | 1.00× |
| reverse | direct-core | 1.836 | 1.00× | 0.61× |
| reverse | facade-untracked | 2.574 | 1.40× | 0.86× |
| reverse | facade-tracked | 6.832 | 3.72× | 2.27× |

## Interpretation

- `direct-core` measures the Gram-matrix numeric engine without facade work.
- `facade-untracked` isolates public wrapping, coercion, and catalog dispatch.
- `facade-tracked` additionally creates immutable expression provenance.
- `legacy-v1` is the retained table-engine reference during Phase 8.
- In this run, direct-core geometric product is 1.09× the retained diagonal table engine; the untracked facade is 1.09× direct core.
- Direct-core reverse is 0.61× the legacy time; tracked results additionally pay for immutable expression provenance.

Re-run from the repository root with:

```shell
PYTHONPATH=packages/galaga uv run --python 3.11 python -m tools.benchmark_phase8 \
  --output docs/v2/phase8-performance.md
```
