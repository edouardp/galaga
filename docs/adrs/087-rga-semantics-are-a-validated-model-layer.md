---
status: accepted
date: 2026-07-22
deciders: edouard
---

# ADR-087: RGA Semantics Are a Validated Model Layer

## Context and problem statement

The Gram-matrix core and the RGA convention layer already implement Eric
Lengyel's complements, metric and antimetric maps, dot and antidot products,
dual families, geometric antiproduct, interior products, and transwedge
families. Those algebraic operations do not by themselves identify which null
basis vector is projective, whether vectors represent points or planes, or
whether an arbitrary homogeneous element satisfies the constraints of rigid
geometry.

Eric's RigidAlgebra3D package also defines model-dependent operations:
attitude, paired norms, homogeneous distance and angle, contractions,
expansions, projections, support, and constraints for lines, motors, and
flectors. Reimplementing these as methods on `Algebra` would make the generic
facade depend on one interpretation of $\mathrm{Cl}(3,0,1)$. Free functions
that infer roles from dimension or basis labels would be ambiguous because
point-based RGA and plane-based PGA deliberately reverse those meanings.

## Decision drivers

- Keep the generic Gram algebra independent of geometric interpretation.
- Require declared model roles rather than infer semantics from a signature.
- Preserve Eric's scalar and antiscalar result codomains.
- Retain semantic expression provenance without adding duplicate public
  numeric operations.
- Make projective validity constraints observable and testable.
- Avoid constructors and helpers that merely abbreviate existing products or
  exponentials.
- Keep point-based RGA and plane-based PGA simultaneously available.

## Decision outcome

`galaga.rga.RigidModel` is a composition layer over a facade `Algebra`.
Construction requires the `lengyel-rga` model identity supplied by `p_rga()`.
It validates three orthonormal Euclidean vector roles, one orthogonal null
projective vector, and the oriented antiscalar role. A bare algebra with the
same diagonal metric is rejected because its geometric interpretation is not
declared.

The model owns homogeneous point construction, point weight,
homogenization, and coordinate extraction. `RigidModel(..., expr=True)` sets
the default expression policy for model-owned factories, with per-call
overrides where construction occurs.

The model implements Eric's attitude; bulk, weight, and geometric norms;
unitization; bulk and weight contractions and expansions; homogeneous distance
and angle; orthogonal and central projections and antiprojections; support;
and antisupport. Descriptive long names are primary. Established concise names
such as `att`, `distance`, and `angle` are aliases of those methods rather than
separate implementations.

These operations attach canonical expression nodes backed by evaluators in
the facade operation catalog. The catalog entries are expression operations,
not additions to the free numeric API. Projective basis roles and tolerances
are stored as hidden expression parameters, so evaluation is independent of
blade spelling and rendering policy. Lengyel notation renders the paired
norms with ● and ○ subscripts.

The model exposes `line_constraint`, `motor_constraint`, and
`flector_constraint`, plus scale-aware predicates. A finite invalid line may
be corrected explicitly with `orthogonalize_line`, which preserves its
direction and removes the component of its moment parallel to that direction.
The correction is not automatically applied by `transwedge_antiproduct`:
ambient exterior-algebra operations remain algebraic, while model validity
remains an explicit semantic concern.

Point-based RGA and plane-based PGA remain distinct presets. They share the
same metric but reverse the point/plane grade ladder and use dual incidence and
transformation products. No runtime flag silently changes the meaning of an
existing multivector.

## Consequences

- Good, because model-dependent formulas cannot leak into the numeric core.
- Good, because invalid lines and transformation elements can be detected
  instead of being accepted solely because they have the expected parity or
  grade.
- Good, because expression rendering can show semantic operations while their
  evaluation still lowers to tested generic primitives.
- Good, because the two dual PGA conventions can be taught and tested side by
  side.
- Good, because transwedge constraint correction is deliberate and visible.
- Cost, because users construct `RigidModel(algebra)` explicitly.
- Cost, because the first model is specifically three-dimensional and tied to
  Eric's declared RGA convention.
- Deferred, because typed point, line, plane, motor, and flector wrappers would
  require a broader decision about constrained geometry types.
- Deferred, because general constraint projection for CGA transwedge circle
  constructions remains research territory rather than a numeric-core helper.
