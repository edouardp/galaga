---
status: accepted
date: 2026-09-06
deciders: edouard
---

# ADR-011: Cached Immutable Representation Plans

## Context and Problem Statement

Compact, Pauli, Dirac, and quaternion conversions repeatedly rebuilt the same
generator matrices, exterior-blade matrices, real reconstruction system, and
rank. Besides wasting work, independent construction in the forward, inverse,
and spinor paths risks allowing those paths to drift apart.

The planned native-null and general-Gram representations also need more
identity than the existing `mode` string. Their conversion and inversion rules
depend on a source coefficient domain, basis convention, dtype, injectivity,
and eventually a metric-congruence policy. Presentation state and individual
multivector values must not influence that identity.

## Decision Outcome

Represent reusable algebra-derived conversion data with an internal frozen
`MatrixRepresentationPlan`. Identify each plan with a frozen
`RepresentationDescriptor` containing:

- mode;
- source coefficient domain (`"full"` or `"even"`);
- named basis when applicable;
- stable convention identifier; and
- numeric dtype.

Each compact-family plan owns read-only snapshots of its generators, complete
exterior-blade matrix stack, represented coefficient indices, real
reconstruction system, measured rank, and current rank/inverse tolerances.
Forward conversion, inverse conversion, and spinor-system construction consume
this shared plan.

Cache plans in a bounded 64-entry least-recently-used cache. A Galaga 2 facade
algebra is keyed by its public numeric algebra identity, so cheap presentation
views share the same plan. Names, symbolic provenance, presentation settings,
and multivector coefficients never enter the key or cached value.

Left-regular mode has a lightweight plan containing descriptor, shape, domain,
and injectivity metadata. It deliberately does not materialize or cache the
potentially large stack of all regular-action matrices: conversion continues
to call the algebra's public `left_action` method directly.

`MatrixRepr` exposes and propagates `domain` metadata. Ordinary matrix
representations use `"full"`; spinor columns use `"even"`. Matrix expression
provenance records the same domain without changing rendered output.

This first work unit does not expand metric support or alter automatic mode
selection. Compact conversion still requires a normalized orthogonal basis,
and general Gram matrices still select left-regular mode.

## Consequences

- Good, because repeated conversions reuse one validated immutable basis.
- Good, because forward, inverse, and spinor paths share algebraic data and
  measured rank.
- Good, because cached arrays cannot be mutated through private diagnostics or
  accidentally corrupted by conversion results.
- Good, because representation identity now has room for native-null,
  even-domain, and general-congruence plans.
- Good, because presentation-only facade views do not duplicate numerical
  plans.
- Cost, because the package owns a bounded process-local cache and private
  cache-reset diagnostics for deterministic tests.
- Neutral, because public matrix values gain additive `domain` metadata while
  all existing numerical and rendering behavior remains unchanged.

## Verification

Tests compute generator anticommutators against the source Gram matrix and pin
the measured real ranks for representative simple, double, and quaternionic
algebras. They verify plan reuse, bounded cache behavior, sharing across facade
presentation views, frozen descriptors, read-only numeric arrays, domain
propagation, and continued rejection of unsupported general-Gram compact mode.
