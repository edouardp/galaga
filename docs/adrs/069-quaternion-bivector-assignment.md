---
status: accepted
date: 2026-07-02
deciders: edouard
---

# ADR-069: Quaternion Bivector Assignment — i=e₂₃, j=e₁₃, k=e₁₂

## Context and Problem Statement

`b_quaternion()` maps the three Cl(3,0) bivectors to Hamilton's quaternion
units i, j, k. There are exactly three valid assignments (cyclic rotations
of the positive product cycle e₁₂ → e₂₃ → e₁₃) that satisfy Hamilton's
identities without needing sign compensation:

1. i=e₁₂, j=e₂₃, k=e₁₃
2. i=e₂₃, j=e₁₃, k=e₁₂  ← chosen
3. i=e₁₃, j=e₁₂, k=e₂₃

The other three permutations (the anti-cyclic direction) all produce
ij = −k, jk = −i, ki = −j, violating Hamilton.

## Decision Drivers

* Hamilton's identities: i² = j² = k² = ijk = −1, ij = k, jk = i, ki = j
* Standard physics convention: quaternion units correspond to rotation axes
* All BasisBlade signs should be +1 (no sign tricks needed)
* Familiar to users coming from physics/graphics quaternion literature

## Considered Options

### Option 1: i=e₁₂, j=e₂₃, k=e₁₃

Maps the "first" bivector (lowest bitmask) to the first quaternion unit.
Feels natural from a pure algebra perspective ("i is the simplest bivector").

However, this gives:
- i = e₁₂ → rotation in xy-plane → rotation about **z**-axis
- j = e₂₃ → rotation in yz-plane → rotation about **x**-axis
- k = e₁₃ → rotation in xz-plane → rotation about **y**-axis

The axis correspondence is scrambled: i↔z, j↔x, k↔y.

### Option 2: i=e₂₃, j=e₁₃, k=e₁₂ (chosen)

Matches the standard physics/graphics convention:
- i = e₂₃ → rotation in yz-plane → rotation about **x**-axis
- j = e₁₃ → rotation in xz-plane → rotation about **y**-axis
- k = e₁₂ → rotation in xy-plane → rotation about **z**-axis

This is the Doran & Lasenby / Hestenes identification. Note j = e₁₃ rather
than the sometimes-written e₃₁; galaga uses canonical ascending index order
for basis blades, and e₃₁ = −e₁₃. The sign is absorbed because `j = e₁₃`
(with BasisBlade.sign = +1) satisfies Hamilton directly in this cyclic
position — no sign flip is needed.

### Option 3: i=e₁₃, j=e₁₂, k=e₂₃

Valid algebraically but matches no standard convention.

## Decision Outcome

Option 2: **i=e₂₃, j=e₁₃, k=e₁₂**.

This aligns with the standard physics convention where quaternion i, j, k
generate rotations about the x, y, z axes respectively. Users familiar with
quaternion rotation libraries (Unity, Unreal, ROS, aerospace) will find the
correspondence unsurprising.

## Why the "obvious" e₃₁ assignment doesn't work directly

Many texts write i=e₂₃, j=e₃₁, k=e₁₂ using the cyclic notation e₃₁.
In galaga, e₃₁ is not a basis blade — e₁₃ is, and e₃₁ = −e₁₃. One might
expect this requires a sign = −1 on j, but it does not: the positive product
cycle in canonical order is e₁₂ → e₂₃ → e₁₃, not e₁₂ → e₂₃ → e₃₁.
The assignment i=e₂₃, j=e₁₃, k=e₁₂ is a rotation of this cycle and all
products come out positive with sign = +1 on every blade.

## Consequences

* Good, because quaternion i↔x, j↔y, k↔z matches standard rotation convention
* Good, because all BasisBlade signs are +1 — no sign compensation logic
* Good, because `exp(−θ/2 · i)` directly gives rotation about x by angle θ
* Neutral, because the assignment looks "shuffled" from a pure index perspective
  (i is not the lowest-bitmask bivector), but this is invisible to users who
  only see the names i, j, k
