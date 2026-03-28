"""Benchmark: 100k rotor sandwich products in Cl(1,3)."""

import time

import numpy as np

from galaga import Algebra, exp, sandwich

alg = Algebra((1, -1, -1, -1))
rng = np.random.default_rng(42)

N = 100_000

# Build random rotors: exp(random bivector)
e1, e2, e3, e4 = [alg.blade(f"e{i}") for i in range(1, 5)]
bivectors = [alg.blade("e12"), alg.blade("e13"), alg.blade("e14"), alg.blade("e23"), alg.blade("e24"), alg.blade("e34")]

rotors = []
for _i in range(N):
    coeffs = rng.standard_normal(6)
    B = sum(c * b for c, b in zip(coeffs, bivectors))
    B = 0.5 * B  # keep angles moderate
    rotors.append(exp(B))

# Random vectors to rotate
vecs = [alg.vector(rng.standard_normal(4)) for _ in range(N)]

print(f"Rotating {N:,} vectors via sandwich product in Cl(1,3) ...")
t0 = time.perf_counter()
for i in range(N):
    sandwich(rotors[i], vecs[i])
elapsed = time.perf_counter() - t0

print(f"Time:  {elapsed:.3f} s")
print(f"Rate:  {N / elapsed:,.0f} sandwich/s")
print(f"Per op: {elapsed / N * 1e6:.1f} µs")
