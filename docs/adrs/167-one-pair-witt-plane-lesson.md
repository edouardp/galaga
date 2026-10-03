---
status: accepted
date: 2026-10-01
deciders: edouard
---

# ADR-167: One-Pair Witt Plane Lesson

## Context

ADR-136 introduced a broad Witt-basis notebook, including boosts, Doppler
shifts, several null pairs and a finite-mode operator example. A beginner
still needs a small plane-level account of what a single null pair can do in
ordinary coordinate calculations. The off-diagonal Gram sign may be either
$+1$ or $-1$; the latter connects naturally to the common CGA null-pair
convention. Both describe the same split signature after reversing one basis
direction.

## Decision

Add a maintained Marimo lesson using
$G_s=\begin{pmatrix}0&s\\s&0\end{pmatrix}$, with an interactive choice of
$s\in\{-1,+1\}$. Derive coordinate pairings, exterior area, the orthogonal
$(1,1)$ frame, and the difference from Euclidean $\mathrm{Cl}(2,0)$ from
Galaga's products. The even subalgebra has a square-$+1$ unit and
split-complex zero divisors; contrast it with the square-$-1$ Euclidean
bivector.

Keep the lesson's distinctive application on the two complementary
idempotents $pq/(2s)$ and $qp/(2s)$. Derive the real $2\times2$ matrix action
by left multiplication on the ideal spanned by $pq/(2s)$ and $q/\sqrt2$.
Obtain matrix entries by solving for coordinates in that ideal; do not insert
canonical raising/lowering matrices as unexplained constants. Leave the
detailed boost application to the existing Witt lesson.

## Consequences

The notebook provides a direct route from a non-diagonal Gram matrix to
coordinates, split-complex numbers, and the full $\mathrm{Cl}(1,1)$ matrix
algebra. Both Gram signs receive regression coverage. The example changes no
numeric or presentation API.
