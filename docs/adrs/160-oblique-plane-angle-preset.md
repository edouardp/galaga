---
status: accepted
date: 2026-09-29
deciders: edouard
---

# ADR-160: Angle-Based Oblique Plane Preset

## Context

A two-dimensional oblique Euclidean basis can be specified by the angle
between its unit vectors. Requiring callers to enter the Gram matrix by hand
obscures this useful geometric input and invites inconsistent entries.

## Decision

Expose `presets.oblique_plane(angle=...)` in radians or
`presets.oblique_plane(degrees=...)` in degrees, requiring exactly one input.
The immutable `ObliquePlanePreset` retains the supplied unit and builds a
complete configuration with Gram matrix `((1, cos(angle)), (cos(angle), 1))`,
ordinary indexed Euclidean blade names, and Euclidean model roles. Accept
finite angles strictly between zero and pi radians (or zero and 180 degrees),
and reject values whose cosine rounds to magnitude one, since they collapse
the basis numerically. The exact right angle maps to a zero off-diagonal.

This is a frame choice for the Euclidean plane, not a distinct signature.
The geometric product follows the metric: `e1 * e2 = cos(angle) + e1 ^ e2`.

## Consequences

The factory makes the geometry readable while preserving access to the
expanded `AlgebraConfig` and its Gram matrix. More general oblique frames
continue to use an explicit Gram matrix.
