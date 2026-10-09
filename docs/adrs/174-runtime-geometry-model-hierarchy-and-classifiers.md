---
status: accepted
date: 2026-10-07
deciders: edouard
---

# ADR-174: Runtime Geometry Model Hierarchy and Classifiers

## Context

An algebra's Gram matrix determines its products but does not determine the
geometric meaning of its blades. Point-based RGA and plane-based PGA both use
$\operatorname{Cl}(3,0,1)$, yet assign points and planes to opposite ends of
the grade ladder and use dual products for joins, meets, and rigid motions.

Galaga already has a validated `RigidModel` for point-based RGA and a
`ConformalModel` for Euclidean CGA. The PGA preset declares semantic roles but
has no behavioral model. CSTA examples construct their semantic operations
locally. The two existing runtime models also duplicate algebra ownership,
role validation, expression tracking, and semantic-expression helpers.

The generic free `bulk_part()` and `weight_part()` functions currently alias
the exterior extensions of the metric and antimetric. Those maps are defined
for every algebra, but they are not a bulk/weight decomposition in every
algebra. In an all-null exterior algebra, the first preserves only the scalar
and the second only the pseudoscalar. In a general oblique metric they need not
be projections.

Object classification is also model-dependent. Grade one can mean an RGA
point, a PGA plane, a CGA dual sphere, or a CSTA signed-round hypersurface. The
existing CGA classifier lives in `galaga_annotation`, although its metric and
incidence decisions are geometry semantics rather than annotation behavior.

## Decision

Physical coordinate policies and conversion scales for CSTA are specified in
[ADR-175](175-csta-physical-units-and-coordinate-scale.md).

Create a runtime geometry model family under `galaga.models`.

Use an internal `_GeometryModel` base for algebra ownership, expression policy,
role lookup, value checks, and semantic-expression construction. Use internal
projective and conformal bases only where the mathematical implementation is
shared. Do not expose a public nominal base class. Public generic consumers use
capability protocols such as point construction, coordinate recovery,
bulk/weight decomposition, and conformal embedding.

The concrete public models are:

- `RigidModel` for point-based RGA;
- `PGAModel` for conventional plane-based PGA;
- `ConformalModel` for Euclidean CGA; and
- `ConformalSpacetimeModel` for CSTA.

`RigidModel` remains limited to three spatial dimensions initially. PGA and
CGA target two and three spatial dimensions. CSTA uses four-dimensional
spacetime with base signature $(+---)$.

Keep runtime construction explicit:

```python
from galaga.models import ConformalModel, ConformalSpacetimeModel, PGAModel, RigidModel
```

Do not add an `Algebra.geometry()` registry. A later
`presets.models.<name>(...)` factory may return a configured `(algebra, model)`
pair after the concrete APIs stabilize.

### Point and conformal APIs

Every concrete model provides `point()` and `coordinates()` with
model-specific representations. Preserve `up()` and `down()` for conformal
embedding only; do not use those names for homogeneous projective embedding.

The internal conformal base owns operations whose definitions depend only on
the base quadratic form and the origin and infinity roles:

- base-vector construction;
- origin, infinity, and null-pair access;
- `up`, `down`, `point`, and coordinates;
- weight and homogenization;
- signed radius squared;
- dual and antidual;
- round/flat and conformal bulk/weight splits;
- conformal conjugation; and
- attitude, carrier, and cocarrier incidence constructions.

Signature-bound norms, unsigned radii, distances, projections, partners,
containers, and classification remain on the concrete model until their
contracts are verified for that signature.

### Construction expression forms

CSTA constructions follow the CGA expression policy: `expr=True` retains
provenance, and `expression_form="operator"` (the default) or `"expanded"`
selects its form. `with_expression_form(...)` returns a model view sharing
the same algebra and tracking setting, with the requested default. A call's
`expression_form=` keyword overrides that default without changing the model.

Coordinate event construction retains four scalar operands, rendering as
$\operatorname{event}(t,x,y,z)$. A multivector input retains its vector
provenance, rendering as $\operatorname{event}(q)$ and supporting expression
replay with a replacement for a named $q$. `up`, `event_pair`, `flat_line`,
and `signed_round` also retain their construction names in operator form.
Expanded form exposes their algebraic definitions. Hidden semantic role
parameters make both forms executable against the same algebra; rendering
does not require a special CSTA formatter.

### Projective bulk and weight

For the normalized Euclidean projective metric, let $\Lambda G$ be the
exterior extension of the metric and $\mathbb G$ its complementary-compound
antimetric. The projective models define

$$
\operatorname{bulk}(A)=(\Lambda G)A
$$

and

$$
\operatorname{weight}(A)=\mathbb G A,
$$

with

$$
\operatorname{bulk}(A)+\operatorname{weight}(A)=A.
$$

`RigidModel` and `PGAModel` expose these as `bulk_part()` and `weight_part()`.
Retire the generic algebra-level aliases with those names. Keep
`metric_apply()` and `antimetric_apply()` as the general algebra operations.

### Generic alias retirement implemented

As of 2026-10-09, remove the generic `bulk_part` and `weight_part` exports
from `galaga`, `galaga.facade`, and `galaga.core`, their catalog operation IDs,
and built-in notation rules and autocomplete keywords. Keep `metric_apply`
and `antimetric_apply` as the explicit algebra operations. Existing CGA model
component methods and their distinct semantic expression IDs remain available.
Projective model methods are described below.

Update examples and current contracts to call the explicit metric maps.
Historical captures retain their original keys and observations; their live
comparisons use the corresponding metric-map operations and reviewed rendering
spellings. Do not provide a compatibility wrapper or restore a generic semantic
operation ID through expression replay.

Regression tests reject the removed imports and expression IDs, verify the
metric maps against Gram minors, and demonstrate the all-null exterior case
where their sum omits intermediate grades. CGA component reconstruction and
expression replay remain covered independently.

### Model-owned classification

Each concrete model owns `classify(value, atol=...)` and returns immutable
structured data. Classification proceeds through algebra ownership,
homogeneous grade, simplicity, representation, incidence with distinguished
null roles, finiteness, and metric invariants. It does not assign an object
name from grade alone.

The supported scope is:

- 2D and 3D PGA;
- 3D RGA initially, with 2D reserved until `RigidModel` is generalized;
- 2D and 3D CGA; and
- fixed 4D $(+---)$ CSTA.

CSTA classification distinguishes events, event pairs, causal flats, signed
rounds, light cones, proper-time and proper-distance hyperboloids, ideal
objects, and supported direct or dual forms. It combines structural incidence
with causal invariants. A null square alone is insufficient to distinguish
an event, light ray, light cone, tangent object, or degenerate blade.

Use one object classifier for OPNS and IPNS descriptions. A direct grade-five
round is classified through its metric Hodge-dual vector, giving the same
light-cone or hyperboloid kind as an explicit IPNS input. Dual inputs of
higher grade are converted before structural classification. Event-pair
causal classes come from the carrier obtained by wedging with infinity,
since the pair's square does not retain the sign of the endpoint interval.

For a nonflat simple grade-three blade $B$, compute its vector span as the
kernel of $v\mapsto v\wedge B$. Let $W_0$ be a weight-one vector in this
span and let the columns of $U$ span its weight-zero directions. With the
actual conformal Gram matrix $G$, form $M=U^TGU$. If $M$ is nonsingular,
the stationary weight-one vector is

$$
W=W_0-U M^{-1}U^TGW_0,
\qquad \rho^2=-W^TGW.
$$

The null condition for $W+U\lambda$ becomes
$\lambda^TM\lambda=\rho^2$. A negative-definite carrier and negative
$\rho^2$ give a circle. A carrier of inertia $(1,1,0)$ gives a hyperbola
when $\rho^2\ne0$ and a null line pair when $\rho^2=0$. Hyperbola tangents
have the opposite squared-norm sign to the radius vector.
[ADR-176](176-csta-object-and-operator-classification.md) extends this
construction to surfaces and distinguishes parabolic and cylindrical
sections in singular carriers without choosing an arbitrary centre.

For curves, the returned causal field describes tangents. For signed-round
hypersurfaces, it describes the interval from the centre. Include carrier
inertia, centre coordinates, and signed squared radius as properties when
they are determined. The classifier does not infer a selected branch or
proper-time parametrization, so an accelerated-trajectory sample yields a
hyperbola with timelike tangents, rather than a motion-specific worldline
label.

Transformation multivectors use a later, separate versor classifier because
they need not be homogeneous blades.

Move the geometric classification logic currently owned by
`galaga_annotation` into the runtime models. The annotation package consumes
classification results and retains highlighting and rendering policy.

### Runtime implementation and compatibility

The implementation places concrete models in `galaga.models.rga`,
`galaga.models.pga`, `galaga.models.cga`, and `galaga.models.csta`.
`galaga.cga` and `galaga.rga` retain identity-preserving reexports for established
imports. Numeric products remain owned by the facade and core.

The internal root validates facade ownership, expression defaults, model
identity, immutable signed roles, and finite coefficients. Model operations
require the same facade `Algebra` instance, including when another presentation
view shares its numeric algebra. Projective validation requires an exactly
normalized Euclidean block and one orthogonal null vector: approximately
normalized metrics do not give exactly complementary metric-map projections.
The conformal base validates its base Gram block, orthogonality, null roles, and
pairing using actual signed role vectors. CSTA retains its normalized pairing
of $-1$ and physical-unit wrappers. Coordinate grammars and unit policies live
in concrete `up`/`point` wrappers; they share signed coordinate construction,
embedding, normalization, role validation, and semantic provenance. Shared
normalization keeps its weight as a tracked scalar multivector, even though the
CSTA public `weight()` convenience method returns a float. Expanded expressions
therefore replay correctly when a named input is rebound at another weight.
The shared base exposes this calculation internally as `_weight_value()`;
each concrete model defines its public `weight()` return contract. This avoids
an incompatible override between CGA's tracked scalar and CSTA's float result.

PGA points are defined by the right complement of the homogeneous vector
$x+w e_0$. Left complement recovers that vector. A plane with coefficients
$(a_1,\ldots,a_d,b)$ has equation $a\cdot x+bw=0$, as verified by exterior
incidence with the point. This determines signs from the configured roles,
rather than copying a coefficient layout from another blade convention.
RGA and PGA `transform(value, motor)` require a normalized even motor and use
the geometric antiproduct/antireverse and geometric product/reverse respectively.

Projective points, joins, meets, and component splits retain distinct executable
semantic operation IDs. Hidden role parameters and a dual-representation flag
make point expressions replayable without importing runtime models into the
facade catalog. CGA `point` retains its own construction ID; CSTA `point`
continues to use the event construction and its unit policy.

Preserve CGA's established `round_point` and `radius_squared` convention:
a vector encoding radius $r$ has square $-r^2$. CSTA's `signed_round` encodes
square $+\rho^2$. The shared radius implementation therefore takes a concrete
model sign, recorded in executable provenance. CGA classifier IPNS radius
properties use $S^2/w^2$, as required by incidence, independently of the
`round_point` constructor's radius convention.

Object classifiers normalize every nonzero input before tolerance decisions.
Only an exactly zero coefficient array is the zero object; scaling a blade
below an absolute tolerance must not erase its projective meaning. Simplicity
is tested by the dimension of the kernel of $v\mapsto v\wedge B$, which must
equal the blade grade. The self-wedge of an odd-grade value is not a simplicity
test. Finite projective geometry has a weight-bearing direction in that span.
CGA finite rounds expose derived center and signed radius properties; an
unresolved or singular round returns a diagnostic `degenerate` result.

PGA/RGA return `ObjectClassification`; CGA returns `CGAClassification`, adding
flat incidence. Existing `CSTAClassification` keeps its construction contract
and causal fields and gains a fixed `model="csta"` field. All results share
model, kind, grade, representation, simplicity, finiteness, and properties.
RGA mixed-grade motor/flector names require verified reciprocal versor actions;
homogeneous values keep their geometric blade interpretation.

`galaga_annotation.classify_cga` retains its four-field `CGAObject` result as
an adapter to the runtime classifier. Annotation component targets and styling
remain in that package. Its established highlighting scope remains 3D; the
runtime classifier independently supports 2D and 3D.

## Consequences

Users gain one discoverable `galaga.models` namespace and consistent point and
coordinate operations while each geometry retains its own mathematical
semantics. Internal inheritance removes duplicated mechanics without exposing
a base class that applications would need to subclass.

PGA receives a behavioral model rather than accumulating notebook-local
constructors. CSTA receives a validated model over the $(+---)$ base signature
rather than inheriting Euclidean CGA interpretations accidentally.

Bulk and weight become explicitly model-owned terms. Code that needs the raw
algebra maps uses `metric_apply()` and `antimetric_apply()`.

Classifiers become reusable by notebooks, annotation, and visualization
without making presentation packages the source of geometric truth. Unknown,
general, and degenerate results remain explicit, and classification tolerances
must be scale-aware so nonzero projective rescaling does not change a kind.

The complete implementation and test plan is recorded in
[Runtime Geometry Model Architecture](../v2/runtime-geometry-models.md).
