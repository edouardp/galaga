---
status: accepted
date: 2026-07-21
deciders: edouard
---

# ADR-086: Native-Null CGA Is a Validated Model Layer

## Context and problem statement

The Gram-matrix core can already represent conformal geometric algebra in the
native basis $(e_1,\ldots,e_n,e_o,e_\infty)$, where the final two basis
vectors are null and have a nonzero mutual inner product. The `p_cga` preset
also identifies the Euclidean, origin, and infinity roles. What was missing
was the model boundary that turns those numeric and semantic facts into safe
Euclidean embedding, extraction, and the established CGA geometry vocabulary.

Several tempting designs would weaken the architecture. A `CGAAlgebra`
subclass could duplicate the facade and product surface. Free functions could
guess the null pair from inertia or display names. Separate line, circle,
sphere, and transformation constructors could simply wrap existing wedges or
exponentials. Conversely, exposing only raw products would repeatedly force
users to rederive conformal weight, signed radius, carrier, cocarrier, and
related domain formulas.

## Decision drivers

- Keep the native Gram matrix as numeric truth.
- Treat `eo` and `einf` as actual basis vectors, not labels on an orthogonal
  frame.
- Require explicit semantic roles instead of guessing from dimension, inertia,
  or names.
- Keep algebra definition, model roles, and presentation independently
  configurable.
- Add operations when they provide CGA meaning and validation, not merely a
  second spelling of a generic primitive.
- Preserve the wiki's compact `att`, `car`, `ccr`, `cen`, `con`, and `par`
  notation without making abbreviations canonical implementation names.
- Represent transformations through the existing exponentials, products, and
  sandwich actions.

## Decision outcome

`p_cga(..., frame="null")` remains the default conformal configuration. It
constructs the exact native Gram matrix, including a configurable nonzero
`eo·einf`, and supplies signed basis roles through `ModelConfig`.

`galaga.cga.ConformalModel` is a composition layer over a facade `Algebra`.
Construction requires the `cga-null` model identity and validates that every
native vector is accounted for by one distinct semantic role, the Euclidean
roles have an identity Gram block, `origin` and `infinity` are null and
orthogonal to Euclidean space, and their mutual product is finite and nonzero.
It deliberately rejects the orthogonal CGA preset and an untyped
`Algebra(4, 1)` even though both have the same inertia.

The model owns Euclidean-vector construction, the generalized round-point
embedding for any declared null-pair scaling, conformal weight,
homogenization, Euclidean extraction, coordinates, and signed squared-radius
extraction.

The model also owns validated CGA semantic compositions: dual, antidual,
attitude, carrier, cocarrier, center, flat center, container, partner,
expansion, and projection. Descriptive names are primary. The wiki
abbreviations are exact class aliases and do not create duplicate
implementations.

The generalized embedding and scale-covariant semantic operations accept every
nonzero null-pair scale declared by the preset. The wiki's polynomial partner
identity is defined for `eo·einf == -1`; `partner` validates that normalization
instead of silently applying it at another scale.

Join, meet, exterior product, geometric product, geometric antiproduct,
complements, metric maps, and sandwich actions remain the existing generic
facade operations. Direct point, flat-point, dipole, line, circle, plane, and
sphere representations are ordinary variadic wedges. Translation, rotation,
dilation, and transversion remain exponentials followed by generic sandwich
actions. No constructors are added merely to hide those compositions.

The first model layer validates algebra ownership and homogeneous-grade
preconditions. It does not introduce typed geometry wrappers or prove every
coefficient constraint for a valid line, circle, plane, or sphere.

## Consequences

- Good, because the conformal implementation exercises the general Gram
  engine directly in its native nonorthogonal basis.
- Good, because presentation changes cannot alter the conformal model.
- Good, because arbitrary null-pair scaling is handled by one generalized
  embedding formula rather than hard-coded `1/2` coefficients.
- Good, because the model-specific helpers satisfy ADR-079's requirement that
  a helper add domain meaning or validation.
- Good, because the CGA wiki's direct and antiproduct formulations are
  expressible without a parallel numeric system.
- Good, because exact short aliases support formula-like code while long names
  remain discoverable and canonical.
- Cost, because users explicitly construct `ConformalModel(algebra)` instead
  of receiving an implicit algebra subclass.
- Cost, because direct geometries remain multivectors; invalid geometric
  coefficient combinations are not yet represented by a distinct type.
- Deferred, because comparing native and orthogonal frames through a public
  basis-change object still depends on the planned outermorphism facility.
