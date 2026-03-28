"""Benchmark: 100k geometric products in Cl(1,3)."""

import time

import numpy as np

from galaga import Algebra, Multivector, gp

alg = Algebra((1, -1, -1, -1))
rng = np.random.default_rng(42)

# Pre-generate 100k random multivectors (all 16 components)
N = 100_000
data = rng.standard_normal((N, alg.dim))
mvs = [Multivector(alg, data[i]) for i in range(N)]

# Time 100k pairwise geometric products: mvs[0]*mvs[1], mvs[2]*mvs[3], ...
pairs = N // 2
print(f"Computing {pairs:,} geometric products in Cl(1,3) ...")

t0 = time.perf_counter()
for i in range(0, N, 2):
    gp(mvs[i], mvs[i + 1])
elapsed = time.perf_counter() - t0

print(f"Time:  {elapsed:.3f} s")
print(f"Rate:  {pairs / elapsed:,.0f} gp/s")
print(f"Per gp: {elapsed / pairs * 1e6:.1f} µs")
