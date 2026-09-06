# CGA API Contract

## Status

This document is the detailed contract for Galaga's implemented
`ConformalModel` boundary and its direct/OPNS and dual/IPNS representation
rules. [ADR-086](docs/adrs/086-native-null-cga-is-a-validated-model-layer.md)
records the architectural decision and its consequences.

Future typed geometry wrappers and semantic representation views remain
proposals. They must not change the shared-model and explicit-object-duality
rules specified here.

## Scope

Galaga has one numeric Clifford algebra for a conformal model and one
`ConformalModel` object that assigns meaning to its native null basis. Direct
and dual CGA are complementary interpretations of multivectors in that shared
algebra; they are not different metrics, bases, or model instances.

This contract defines:

- the conformal model boundary;
- canonical Euclidean point embedding and extraction;
- the relation between direct/OPNS and dual/IPNS object blades;
- the point special case;
- which products construct joins and intersections;
- expression-provenance behavior; and
- validation and conformance requirements.

It does not define typed `Point`, `Line`, `Circle`, `Plane`, or `Sphere`
classes.

## Terminology

### Numeric algebra

For an embedded Euclidean space of dimension (n), native-null CGA has
conformal vector-space dimension

$$
N=n+2
$$

with basis

$$
(e_1,\ldots,e_n,e_o,e_\infty).
$$

The Gram matrix is numeric truth. The standard normalization is

$$
e_o^2=e_\infty^2=0,
\qquad
e_o\mathbin{\cdot}e_\infty=-1,
$$

but `p_cga()` may declare any finite nonzero null-pair scale

$$
\kappa=e_o\mathbin{\cdot}e_\infty.
$$

### Conformal model

`ConformalModel` validates and exposes:

- the Euclidean basis roles;
- the native conformal origin (e_o);
- the point at infinity (e_\infty);
- the null-pair scale (\kappa); and
- operations whose meaning depends on those roles.

It does not store a direct/dual representation mode.

### Interpretation and conversion

Two distinct actions must not be conflated:

1. **Change interpretation.** Keep a multivector's coefficients and decide
   whether its grades are being read through the direct or dual geometric
   calculus.
2. **Convert the same geometric locus.** Apply the full conformal Hodge dual
   to the object's representing blade.

Changing interpretation is metadata or teaching context; conversion is a
real algebraic operation.

## Model construction

The public construction is:

```python
from galaga import Algebra, p_cga
from galaga.cga import ConformalModel

algebra = Algebra(config=p_cga(spatial_dim=3))
cga = ConformalModel(
    algebra,
    expr=False,
    expression_form="operator",
)
```

`ConformalModel` deliberately has no `representation=` constructor argument
and no `with_representation()` method. Constructing a second model would not
make raw multivectors remember a representation and would incorrectly make
canonical operations such as `up()` representation-dependent.

The model exposes:

```python
cga.algebra
cga.spatial_dim
cga.null_pair
cga.origin
cga.infinity
cga.euclidean_basis_vectors()
```

`origin` and `infinity` are always the actual native grade-one basis vectors.
They do not change grade when an object is interpreted or converted.

## Canonical point embedding

For a Euclidean vector (x), the canonical conformal embedding is

$$
P(x)
=e_o+x-\frac{x^2}{2\kappa}e_\infty.
$$

This is the meaning of `up()` in every workflow:

```python
P = cga.up(1.0, 2.0, 3.0)
Q = cga.up((1.0, 2.0, 3.0))
x = cga.euclidean_vector((1.0, 2.0, 3.0))
R = cga.up(x)

assert P == Q == R
```

`up()` accepts exactly one of:

- one real positional coordinate per spatial dimension;
- one coordinate iterable; or
- one Euclidean multivector owned by the same algebra.

Booleans, non-real coordinates, non-finite values, wrong coordinate counts,
mixed forms, and multiple multivectors are rejected.

The canonical embedding satisfies

$$
P(x)^2=0,
\qquad
P(x)\mathbin{\cdot}e_\infty=\kappa,
$$

and, independently of the configured nonzero (\kappa),

$$
P(x)\mathbin{\cdot}P(y)
=-\frac12\lVert x-y\rVert^2.
$$

`round_point(position, radius_squared=...)` uses the same input grammar and
the established signed-radius convention. `weight`, `homogenize`, `down`,
`coordinates`, and `radius_squared` operate on canonical conformal vectors;
they do not silently Hodge-dualize their inputs.

## Direct and dual object representations

### Direct/OPNS

A direct blade (A) describes its conformal point locus through

$$
X\wedge A=0.
$$

Direct objects are constructed by joining points with the outer product. A
flat additionally includes (e_\infty).

### Dual/IPNS

The strict dual blade representing the same locus is

$$
A^\star=H(A),
$$

and its incidence equation is

$$
X\mathbin{\rfloor}A^\star=0.
$$

When (A^\star) is a vector, this reduces to

$$
X\mathbin{\cdot}A^\star=0.
$$

IPNS objects are intersected with the outer product. Thus the same generic
operation has complementary geometric meanings:

| Interpretation | Outer product     | Regressive product |
| -------------- | ----------------- | ------------------ |
| direct/OPNS    | join              | meet/intersection  |
| dual/IPNS      | meet/intersection | join               |

These remain generic Galaga operations. `ConformalModel` does not provide a
state-dependent `join()` or `meet()` method while values remain unbranded.

### Grades in 2D CGA

The conformal dimension is (N=4).

| Geometry   | Direct/OPNS                         | Strict dual/IPNS                                     |
| ---------- | ----------------------------------- | ---------------------------------------------------- |
| point      | (P), grade 1                        | (H(P)), grade 3; also the zero-circle shortcut below |
| point pair | (P\wedge Q), grade 2                | (H(P\wedge Q)), grade 2                              |
| line       | (P\wedge Q\wedge e_\infty), grade 3 | grade 1 line vector                                  |
| circle     | (P\wedge Q\wedge R), grade 3        | grade 1 circle vector                                |

### Grades in 3D CGA

The conformal dimension is (N=5).

| Geometry   | Direct/OPNS | Strict dual/IPNS                             |
| ---------- | ----------- | -------------------------------------------- |
| point      | grade 1     | grade 4; also the zero-sphere shortcut below |
| point pair | grade 2     | grade 3                                      |
| line       | grade 3     | grade 2                                      |
| circle     | grade 3     | grade 2                                      |
| plane      | grade 4     | grade 1                                      |
| sphere     | grade 4     | grade 1                                      |

The grade map is always

$$
k\longmapsto N-k=n+2-k.
$$

It is not a dual taken only over the (n) Euclidean directions.

## The full conformal Hodge operation

`ConformalModel.dual()` follows the CGA wiki/Lengyel right-Hodge convention:

$$
H(A)=\overline{G(A)},
$$

where (G) is the metric exomorphism and the overline is right complement.
For Galaga's native CGA conventions this is equivalently

$$
H(A)=\widetilde A I_C,
\qquad
I_C=I_E\wedge(e_o\wedge e_\infty).
$$

The API is:

```python
A_ipns = cga.dual(A_opns)
```

The full conformal pseudoscalar proves that (e_o) and (e_\infty) take part
in conversion even though their basis values remain shared. For example, in
2D CGA,

$$
H(e_1)\propto e_2\wedge e_o\wedge e_\infty.
$$

### Projective round trip

For a grade-(k) blade in conformal dimension (N), Galaga verifies

$$
H(H(A_k))
=(-1)^{k(N-k)}\det(G)A_k.
$$

Therefore applying `cga.dual()` twice recovers the same homogeneous geometry
projectively. Exact coefficients can be recovered with the derived factor:

```python
k = A_opns.homogeneous_grade()
N = cga.algebra.n
factor = (-1) ** (k * (N - k)) * cga.algebra.metric_determinant
A_exact = cga.dual(cga.dual(A_opns)) / factor
```

Mixed-grade values require this calculation grade by grade. Representation
conversion is primarily defined for homogeneous geometry blades.

### `dual`, `antidual`, and generic `undual`

`ConformalModel.antidual()` is the right weight dual

$$
\overline{\mathbb G(A)}.
$$

It is not the inverse of `ConformalModel.dual()`. Under the standard CGA
metric, dual and antidual differ only by the model's documented sign.

The generic Galaga `dual()`/`undual()` pair uses the conventional inverse-
pseudoscalar definition. It is an exact algebraic inverse pair and is
projectively equivalent to the right-Hodge convention on homogeneous CGA
blades, with grade-dependent signs. Code requiring exact coefficients must
not mix the conventions without accounting for those signs.

## The point special case

Let

$$
P=P(p)=\operatorname{up}(p).
$$

Its uniform strict dual representation is the complementary-grade blade

$$
P^\star=H(P).
$$

However, the original null vector (P) can also be used directly as an IPNS
zero-radius sphere because

$$
X\mathbin{\cdot}P
=-\frac12\lVert x-p\rVert^2.
$$

For real embedded conformal points, this vanishes exactly at (x=p). Hence
both of the following describe the same point locus:

$$
X\mathbin{\rfloor}P^\star=0,
\qquad
X\mathbin{\cdot}P=0.
$$

This is why CGA literature can state that the point representation is the
same in OPNS and IPNS. It is a special zero-sphere interpretation, not the
identity (H(P)=P), and it must not make `up()` representation-dependent.

## Analytic IPNS forms

### Circle or sphere

For center (c) and real radius (r), the IPNS hypersphere vector under the
configured null-pair scale is

$$
S=P(c)+\frac{r^2}{2\kappa}e_\infty.
$$

It satisfies

$$
X\mathbin{\cdot}S
=\frac12\left(r^2-\lVert x-c\rVert^2\right).
$$

In 2D, three points on that circle produce a projectively equal vector:

```python
P = cga.up(-1.0, 0.0)
Q = cga.up(0.0, 1.0)
R = cga.up(1.0, 0.0)

C_opns = outer_product(P, Q, R)
C_ipns = cga.dual(C_opns)

C_analytic = cga.up(0.0, 0.0) + (
    1.0 / (2.0 * cga.null_pair)
) * cga.infinity
```

`C_ipns` and `C_analytic` differ only by a nonzero homogeneous scale.

### Line or plane

An IPNS hyperplane has the form

$$
\pi=n+d e_\infty,
$$

with the sign of (d) fixed by the selected plane-equation convention. In
2D, the direct x-axis

$$
P(-1,0)\wedge P(1,0)\wedge e_\infty
$$

dualizes to a vector proportional to (e_2).

## API ownership

`ConformalModel` owns operations that require conformal roles or add validated
CGA meaning:

| Group                     | Operations                                                                           |
| ------------------------- | ------------------------------------------------------------------------------------ |
| model data                | `algebra`, `spatial_dim`, `null_pair`, `origin`, `infinity`                          |
| Euclidean values          | `euclidean_basis_vectors`, `euclidean_vector`                                        |
| conformal vectors         | `round_point`, `up`, `weight`, `homogenize`, `down`, `coordinates`, `radius_squared` |
| object duality            | `dual`, `antidual`                                                                   |
| components                | round/flat and bulk/weight projections                                               |
| norms                     | weighted and normalized center/radius/component norms                                |
| direct geometry semantics | `attitude`, `carrier`, `cocarrier`, `center`, `flat_center`, `container`, `partner`  |
| direct binary semantics   | `expansion`, `projection`                                                            |
| provenance                | `expr`, `expression_form`, `with_expression_form`                                    |

The established geometry helpers retain their documented direct formulas.
They do not inspect an ambient representation mode and do not silently
dualize values.

The following remain generic Galaga operations:

- outer and regressive products;
- geometric product and geometric antiproduct;
- metric and antimetric maps;
- complement and uncomplement;
- generic dual and undual;
- versor construction and sandwich actions; and
- transformations.

No constructor is added merely to hide a wedge.

## Expression provenance

Expression tracking and expression shape are independent of geometric
interpretation:

```python
cga = ConformalModel(algebra, expr=True, expression_form="operator")
expanded = cga.with_expression_form("expanded")
```

`expr=` selects whether model-created results retain executable provenance.
`expression_form="operator"` retains a semantic model call;
`expression_form="expanded"` exposes the generic GA composition when one
exists. Neither option changes numeric coefficients.

`cga.dual(A)` must retain the right-Hodge operation rather than render as a
metadata cast. Its expanded form is

$$
\operatorname{complement}(\operatorname{metric\_apply}(A)).
$$

Representation is not an expression-policy axis and is not stored as a
hidden parameter on model calls.

## Validation

The model distinguishes these failures:

| Failure                             | Required behavior                                |
| ----------------------------------- | ------------------------------------------------ |
| wrong Python type                   | `TypeError`                                      |
| different numeric algebra           | `ValueError` identifying algebra ownership       |
| incompatible CGA model              | construction-time or operation-time `ValueError` |
| wrong homogeneous grade             | `ValueError` identifying the grade contract      |
| invalid conformal roles or metric   | construction-time `ValueError`                   |
| zero homogeneous weight             | operation-specific `ValueError`                  |
| unsupported null-pair normalization | operation-specific `ValueError`                  |
| negative real square-root domain    | operation-specific `ValueError`                  |

Raw multivectors do not carry a representation tag, so there is no generic
"wrong representation" error. A future interpreted wrapper may add one.

Error messages must not claim that every homogeneous blade of an accepted
grade is a valid geometric object unless the corresponding coefficient
constraints were checked.

## Conformance tests

The maintained test suite must cover:

1. metric and stored-sign consistency before semantic expectations;
2. canonical point embedding for every supported spatial dimension and
   null-pair scale;
3. equivalence of positional, iterable, and Euclidean-vector point input;
4. point inner products reproducing Euclidean squared distance;
5. right-Hodge grade mapping (k\mapsto N-k);
6. the double-Hodge factor derived from grade and the actual Gram determinant;
7. equality of right Hodge with (\widetilde A I_C) on the native CGA basis;
8. OPNS circle duality against the independently derived analytic IPNS
   circle vector;
9. OPNS line duality against its independently derived IPNS normal;
10. equivalent OPNS and IPNS incidence results for on- and off-locus probes;
11. the point's strict dual and zero-sphere descriptions;
12. expression evaluation in operator and expanded forms;
13. standard and Lengyel rendering of dual and antidual; and
14. executable Marimo notebook dependency and headless-runtime checks.

External identities must be evaluated against Galaga's algebra before display
or naming code is written.

## Future semantic views

A future API may provide optional `opns` and `ipns` helpers or interpreted
geometry wrappers. Such an API is justified only if it adds provenance,
geometry-kind validation, or meaningfully safer join/meet/transform behavior.

It must preserve these invariants:

- one shared `ConformalModel` and numeric algebra;
- one canonical `up()` result;
- unchanged `origin` and `infinity` basis values;
- explicit full conformal Hodge conversion for the same locus;
- no implicit conversion of existing multivectors; and
- generic products retaining their fixed numeric definitions.

A wrapper-only representation enum is insufficient if ordinary
`Multivector` operations immediately discard it.

## Literature basis

The contract follows the common CGA distinction between OPNS and IPNS in the
[Eurographics CGA tutorial by Hildenbrand, Fontijne, Perwass, and
Dorst](https://citeseerx.ist.psu.edu/document?doi=6ad4d5c5b9c826f5956fc844a50499f78bda00f5&repid=rep1&type=pdf),
including its documented point special case.

Eric Lengyel's [CGA duals
reference](https://conformalgeometricalgebra.org/wiki/index.php?title=Duals)
defines the right Hodge dual as metric exomorphism followed by complement.
His [Dual Approaches to Projective Geometric
Algebra](https://terathon.com/blog/dual-pga.html) concerns PGA, but its general
distinction between one algebra and two geometric interpretations also guides
this CGA architecture.

The PGA and CGA implementation details are not identical: PGA is degenerate,
whereas native CGA is nondegenerate. In both cases, however, changing the
geometric interpretation does not create a second basis or coefficient
storage system.

## Accepted decision summary

| ID  | Decision                                                                                                               |
| --- | ---------------------------------------------------------------------------------------------------------------------- |
| C1  | `ConformalModel` represents one shared conformal model, not a direct or dual mode.                                     |
| C2  | `up()`, (e_o), and (e_\infty) are representation-independent.                                                          |
| C3  | The same-locus OPNS/IPNS conversion is `cga.dual(A)`.                                                                  |
| C4  | The dual uses all (N=n+2) conformal dimensions.                                                                        |
| C5  | Applying the dual twice is projectively involutive with a derived grade/metric factor.                                 |
| C6  | A point has both a strict complementary-grade dual and a grade-one zero-sphere interpretation.                         |
| C7  | Outer and regressive products remain generic; model-level representation-dependent `join()` and `meet()` are deferred. |
| C8  | Existing CGA helpers retain their direct formulas and never consult hidden representation state.                       |
| C9  | `CGA_API.md` is the detailed contract; ADR-086 records the architectural choice.                                       |
