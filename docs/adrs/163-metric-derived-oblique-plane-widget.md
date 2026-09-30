---
status: accepted
date: 2026-09-30
deciders: edouard
---

# ADR-163: Metric-Derived Oblique Plane Widget

## Context

The oblique-plane preset exposes a nonorthogonal Gram matrix, but algebra and
product tables alone do not show the geometry of its vectors and bivectors.
A plane drawing must preserve the metric instead of treating basis
coefficients as ordinary Cartesian coordinates.

## Decision

Provide `galaga_anywidget.oblique2d(algebra, values)` for two-dimensional,
positive-definite algebras. Compute a Euclidean embedding from the Gram
matrix using a Cholesky factor, so basis-vector lengths and pairwise products
match the algebra. Draw homogeneous grade-one values as arrows and grade-two
values as oriented parallelograms. Compute the signed bivector area from the
coefficient and Gram determinant. Reject other dimensions, non-positive
metrics, scalars, and mixed-grade values.

The widget is an optional integration. The algebra and multivector objects
remain the source of metric and coefficient data; the JavaScript view only
draws their prepared coordinates. User-supplied labels are escaped before
insertion into SVG.

## Consequences

The oblique-plane notebook can vary the basis angle while the drawing,
algebra display, and bilinear table update together. The plot makes no claim
to depict indefinite or degenerate metrics as ordinary Euclidean geometry.
