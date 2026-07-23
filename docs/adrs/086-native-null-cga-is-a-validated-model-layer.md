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
- Preserve Eric Lengyel's four CGA component families and weighted norms
  without redefining the general core's RGA metric operations.
- Represent transformations through the existing exponentials, products, and
  sandwich actions.

## Decision outcome

`p_cga(..., frame="null")` remains the default conformal configuration. It
constructs the exact native Gram matrix, including a configurable nonzero
`eo·einf`, and supplies signed basis roles through `ModelConfig`.

`p_lengyel_cga()` is the complete Eric Lengyel presentation of the standard
three-dimensional conformal model. It retains the same native-null metric and
model roles while composing `Notation.lengyel()` with bold compact
$\mathbf e_1,\ldots,\mathbf e_5$ blades, signed non-ascending labels, Eric's
basis-table display order, and $\text{𝟙}$ as the unit antiscalar. Keeping this
as a separate preset prevents Eric-specific presentation choices from leaking
into ordinary `p_cga()`.

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

The model owns the role-dependent round-bulk, round-weight, flat-bulk, and
flat-weight projections. It derives round/flat and CGA bulk/weight families
from them and defines conformal conjugation as round minus flat. These remain
model methods: the free `galaga.bulk_part` and `galaga.weight_part` retain
their general RGA meanings as metric and antimetric application.

The model also implements Eric's center, radius, and four component norms.
The homogeneous numerator codomains are preserved rather than coerced
indiscriminately to floats: `weighted_center_norm` and the round-bulk norm are
scalar, `weighted_radius_norm` and the flat-weight norm are antiscalar, the
round-weight norm lies on the complement of infinity, and the flat-bulk norm
lies on infinity. `center_norm` and `radius_norm` compare those numerator
coefficients with round weight and return projectively normalized scalar
multivectors; `center_distance` and `radius` are descriptive aliases. A
negative radius-norm square is not representable in the real numeric core and
raises; signed `radius_squared` remains available for round points. Eric's
antidot radius formula is tied to the standard null-pair scale, so
`weighted_radius_norm`, `radius_norm`, and `radius` validate
`eo·einf == -1`.

The generalized embedding and scale-covariant semantic operations accept every
nonzero null-pair scale declared by the preset. The wiki's polynomial partner
identity is defined for `eo·einf == -1`; `partner` validates that normalization
instead of silently applying it at another scale.

Join, meet, exterior product, geometric product, geometric antiproduct,
complements, metric maps, and sandwich actions remain the existing generic
facade operations. Direct point, flat-point, dipole, line, circle, plane, and
sphere representations are ordinary variadic wedges. Translation, rotation,
dilation, and transversion remain exponentials followed by generic sandwich
actions. Plane reflection and sphere inversion remain the ordinary
odd-versor action $-aXa^{-1}$; inverting a line into a circle likewise needs
no special numeric operation. No constructors are added merely to hide those
compositions.

The first model layer validates algebra ownership and homogeneous-grade
preconditions. It does not introduce typed geometry wrappers or prove every
coefficient constraint for a valid line, circle, plane, or sphere.

Expression provenance is an orthogonal model-construction policy.
`ConformalModel(algebra, expr=True)` makes model-owned values expression-aware
by default, while an explicit `expr=True` or `expr=False` on an individual
factory overrides that default. The numeric default remains `False`.

Expression shape is a second, independent model policy.
`expression_form="operator"` is the default and retains the domain operation
as an executable expression node. `expression_form="expanded"` exposes the
generic GA composition used to calculate the same eager value.
`with_expression_form(...)` returns an immutable view sharing the original
`Algebra`, and individual semantic methods accept `expression_form=` as a
non-mutating override. This separates the question “does this value retain
provenance?” from “which explanation should that provenance present?”.

Expansion is truthful rather than forced. Operations implemented by a generic
GA formula expose that formula. Model-level coefficient projections such as
`down` and the four native-null component selectors have no lower generic
algebra expression and therefore remain atomic semantic calls even under the
expanded policy.

The named semantic operations attach canonical expression nodes for
`attitude`, `carrier`, `cocarrier`, `center`, `flat_center`, `container`, and
`partner`, as well as the component and norm families. Their origin/infinity
role references and numeric tolerances are non-rendered expression parameters:
this makes evaluation independent of display labels while letting the Lengyel
notation render `att`, `car`, `ccr`, `cen`, `con`, `par`, the ●/○/■/□
subscripts, and the weighted norm subscripts. The expanded policy recursively
retains the generic-operation provenance for expansion, projection, and the
other compositional helpers.

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
- Good, because model names disambiguate Eric's CGA component projections from
  the core's general metric/antimetric RGA operations.
- Good, because operator and expanded forms let teaching material change its
  level of explanation without changing values, algebras, or global display
  state.
- Cost, because users explicitly construct `ConformalModel(algebra)` instead
  of receiving an implicit algebra subclass.
- Cost, because direct geometries remain multivectors; invalid geometric
  coefficient combinations are not yet represented by a distinct type.
- Deferred, because comparing native and orthogonal frames through a public
  basis-change object still depends on the planned outermorphism facility.
