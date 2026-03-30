---
status: accepted
date: 2026-03-30
deciders: edouard
---

# ADR-045: Near-Unit Coefficient Display Tolerance

## Context and Problem Statement

Floating-point arithmetic from trig operations (e.g. `cos(π/2)`) produces
coefficients like `-0.9999999999999998` instead of exactly `-1.0`. The
display convention of suppressing ±1 coefficients (`-e₂` not `-1e₂`) used
exact comparison (`abs(c) == 1.0`), causing these near-unit values to render
with the coefficient shown.

## Decision Outcome

Use `np.isclose(abs(c), 1.0)` instead of `abs(c) == 1.0` for the ±1
suppression check in both unicode and LaTeX rendering.

### Why np.isclose

- Default tolerance is `rtol=1e-9, atol=1e-8` — tight enough to only catch
  genuine floating-point noise, not intentional non-unit coefficients.
- Consistent with how the library already handles near-zero suppression
  (`abs(c) < 1e-12`).

### What This Affects

- `str()`, `repr()`, `latex()` default rendering — ±1 suppression
- Does NOT affect explicit format specs (`:g`, `:.3f`, `coeff_format=`) —
  those always show the actual coefficient value.

### Consequences

- Good, because rotations by common angles (90°, 180°) display cleanly
- Good, because format specs still show exact values when needed
- Risk, because a coefficient of 1.00000001 (from intentional scaling) would
  also be suppressed — acceptable since the tolerance is very tight
