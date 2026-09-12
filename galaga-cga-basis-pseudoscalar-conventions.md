# CGA Basis Ordering and Pseudoscalar Conventions

## Context

For a conformal geometric algebra (CGA) preset, Galaga needs sensible
defaults for:

1. The ordered basis, especially the Euclidean vectors, origin null vector
   $e_o$, and infinity null vector $e_\infty$.
2. The orientation and sign of the pseudoscalar associated with that basis.
3. The relationship to duality, particularly OPNS/IPNS conversion.
4. The display order, which is independent of all three mathematical choices.

Different CGA sources use different conventions. The goal is a coherent,
recognizable convention that is convenient for teaching and does not introduce
unexplained signs.

**Status:** the model convention discussed here is

$$
\boxed{I_C=e_o\wedge I_E\wedge e_\infty},
\qquad
I_E=e_1\wedge\cdots\wedge e_n.
$$

The default native-null preset now uses the actual origin-first basis.
`presets.cga(n, basis_order="euclidean-first")` retains the former coordinates.
See [ADR-134](docs/adrs/134-origin-first-native-null-cga.md) for the accepted
implementation decision. No new model-pseudoscalar API is introduced:
the quantities below are derived with existing model roles and wedges.

The naming follow-up is implemented in
[ADR-135](docs/adrs/135-cga-pseudoscalar-names-and-exact-orientations.md):
default native `I`; paired model names via `model_pseudoscalars=True`;
`E = eo ^ einf` via `pseudoscalar_null=True`; and an explicit native `pss`
name override. These are signed blade labels and aliases, not new model
properties. Python/ASCII names are `IE` and `IC`, with $I_E$ and $I_C$ in
LaTeX. In 1D the axis remains `e1` and `IE` is lookup-only.
The exact identity is $I_E\wedge E=(-1)^n I_C$, never an equality with an
unspecified sign.

## 1. Survey of CGA basis-order conventions

There is no universal conformal basis order. Two natural null-basis orders are

$$
(e_1,\ldots,e_n,e_o,e_\infty)
$$

and

$$
(e_o,e_1,\ldots,e_n,e_\infty).
$$

A third family starts from an orthogonal pair $(e_+,e_-)$ and derives the null
vectors from it.

### Euclidean-first ordering

Presentations that start with the Euclidean algebra and then introduce two
conformal dimensions naturally suggest

$$
(e_1,\ldots,e_n,e_o,e_\infty).
$$

This makes the relationship to the underlying Euclidean algebra immediate.
It is the current native order of Galaga's standard CGA presets.

### Origin-first ordering

Origin-first has literature precedent. Dorst's
[projective-duality paper, section 7.1](https://onlinelibrary.wiley.com/doi/10.1002/mma.9754)
explicitly writes

$$
I_c=n_o\wedge I_d\wedge n_\infty.
$$

This suggests the structural order

$$
\text{origin}\ \longrightarrow\
\text{Euclidean dimensions}\ \longrightarrow\
\text{infinity}.
$$

That source also explicitly uses $pI_c$, without the inverse, in its CGA
comparison. Its pseudoscalar convention therefore cannot be imported as
evidence that Galaga's existing dual operations have the same signs.

The Hrdina–Návrat material and introductory notes listed in section 13 are additional
leads for the survey. Precise page/equation references should be established
before making stronger claims about a community-wide convention.

### Orthogonal implementation bases

The [Python `clifford` CGA tutorial](https://clifford.readthedocs.io/en/latest/tutorials/cga/index.html)
uses an orthogonal extension and derives `eo` and `einf` from it.

Such implementation choices do not determine a preferred null-basis
orientation. Galaga's general Gram matrices permit $e_o$ and $e_\infty$ to
be native basis vectors instead.

### What orthogonal-basis users may mean by their pseudoscalar

For a concrete comparison, take the documented Python `clifford` definitions

$$
e_+^2=1,\qquad e_-^2=-1,\qquad e_+\cdot e_-=0,
$$

$$
e_o=\frac12(e_--e_+),\qquad e_\infty=e_-+e_+.
$$

Define the orthogonal pseudoscalar, with the positive extra vector first, by

$$
I_{\mathrm{orth}}=I_Ee_+e_-=I_E\wedge e_+\wedge e_-.
$$

The null-pair change of basis has determinant $-1$:

$$
\begin{pmatrix}
-\tfrac12&1\\
\tfrac12&1
\end{pmatrix},
\qquad
e_o\wedge e_\infty=-e_+\wedge e_-.
$$

Combining that sign with the permutation moving $e_o$ past the $n$ Euclidean
vectors gives

$$
\boxed{
I_C=e_o\wedge I_E\wedge e_\infty
=(-1)^{n+1}I_{\mathrm{orth}}.
}
$$

| Euclidean dimension | Compatibility Euclidean-first null $I_{\mathrm{native}}$ | Origin-first model $I_C$ |
|---|---|---|
| 2 | $-I_{\mathrm{orth}}$ | $-I_{\mathrm{orth}}$ |
| 3 | $-I_{\mathrm{orth}}$ | $+I_{\mathrm{orth}}$ |

Thus, in 3D, our origin-first native pseudoscalar agrees with
this familiar orthogonal pseudoscalar. The two sign changes cancel. This is
not a universal claim about all orthogonal-basis libraries: reversing the
order of $e_+$ and $e_-$, changing null-vector definitions, or defining an
explicit opposite pseudoscalar changes the comparison.

The same tutorial defines $E_0=e_\infty\wedge e_o=e_+\wedge e_-$. A user
forming $I_EE_0$ obtains $I_{\mathrm{orth}}$, whereas one forming
$I_E\wedge e_o\wedge e_\infty$ obtains its negative. Those users can disagree
on the symbol `I` while using exactly the same library and null vectors.

The convention is therefore sometimes hidden in helper functions or copied
formulas, but it is not mathematically opaque. Recover it by specifying the
ordered orthogonal basis, exact null-vector definitions, the value called
`I`, and the dual operation. No conclusion about an individual library user's
choice follows just from their use of $e_+$ and $e_-$.

### Normalization can introduce scale as well as sign

Galaga permits a nonzero null pairing $\kappa=e_o\cdot e_\infty$ in native-null
presets. One possible orthogonal realization is

$$
e_o=\frac{\kappa}{2}(e_+-e_-),\qquad e_\infty=e_++e_-.
$$

Then

$$
e_o\wedge e_\infty=\kappa e_+\wedge e_-,
\qquad
I_C=(-1)^n\kappa I_{\mathrm{orth}}.
$$

The preceding sign table uses $\kappa=-1$. With other normalizations, importing
an orthogonal convention may require a volume scale as well as a sign.
Reciprocal rescaling $e_o\mapsto a e_o$, $e_\infty\mapsto a^{-1}e_\infty$
leaves their wedge and pairing unchanged for nonzero real $a$.

## 2. Why this is especially relevant to Galaga

Galaga accepts non-diagonal Gram matrices. For the origin-first 2D CGA basis

$$
(e_o,e_1,e_2,e_\infty),
$$

the standard normalization $e_o\cdot e_\infty=-1$ gives

$$
G=
\begin{pmatrix}
0&0&0&-1\\
0&1&0&0\\
0&0&1&0\\
-1&0&0&0
\end{pmatrix}.
$$

There is no need for a hidden orthogonal implementation basis.

However, three distinct concepts must not be conflated:

| Concept | What it controls | Can changing it change the pseudoscalar? |
|---|---|---|
| Display order | The sequence of terms and full wedge-table axes | No |
| Native ordered basis | Gram rows/columns, coordinate masks, basis enumeration | Yes, when the chosen basis orientation changes |
| Model's ordered semantic frame | The meaning and order of roles such as origin and Euclidean axes | Its derived model pseudoscalar can differ from `algebra.I` |

`DisplayOrder` does not permute Gram coordinates, redefine basis vectors, or
change duality. It also does not reorder the factors inside a blade label:
moving a term labelled $e_{1o}$ does not turn it into $e_{o1}$.

A genuine coordinate permutation requires corresponding changes to the Gram
matrix, vector-role masks, blade coordinates and labels. If $P$ expresses
the new basis in old coordinates, then

$$
G_{\mathrm{new}}=P^\mathsf{T}G_{\mathrm{old}}P.
$$

Multivector coordinates must transform through the induced exterior map.
An existing `data` array must not simply be reused with the new preset.

## 3. The pseudoscalar is an orientation choice

For an actual ordered basis $(b_1,\ldots,b_N)$, define

$$
I=b_1\wedge\cdots\wedge b_N.
$$

An odd permutation produces the opposite associated pseudoscalar when both
are compared in the same underlying space:

$$
I_{\mathrm{new}}=-I_{\mathrm{old}}.
$$

There is no uniquely correct choice between $I$ and $-I$. The full top-grade
space is one-dimensional; its nonzero elements differ by scale. For
non-unit bases, the wedge also records the basis's volume scale, not just
its orientation.

### The even-dimensional coincidence

For two Euclidean dimensions,

$$
e_1\wedge e_2\wedge e_o\wedge e_\infty
=
e_o\wedge e_1\wedge e_2\wedge e_\infty.
$$

Moving $e_o$ across two vectors contributes $(-1)^2=+1$. In three dimensions,

$$
e_o\wedge e_1\wedge e_2\wedge e_3\wedge e_\infty
=
-\,e_1\wedge e_2\wedge e_3\wedge e_o\wedge e_\infty.
$$

In general, for the compatibility Euclidean-first preset,

$$
\boxed{I_C=(-1)^n\,I_{\mathrm{native}}}.
$$

Here $n$ is the Euclidean dimension, not the full algebra dimension $n+2$.
The sign is derived from the ordered wedge, not independently configured.

## 4. Use an explicit wedge in a null basis

Because $e_o\cdot e_\infty=-1$,

$$
e_oe_\infty=-1+e_o\wedge e_\infty.
$$

Consequently, in 2D CGA,

$$
e_1e_2e_oe_\infty
=
-\,e_1\wedge e_2
+
e_1\wedge e_2\wedge e_o\wedge e_\infty.
$$

That geometric product is not purely the top-grade blade. The unambiguous
pseudoscalar definition uses wedges.

Compact labels such as $e_{12o\infty}$ may still denote exterior basis blades,
as they do in Galaga. A compact blade label is not an instruction to multiply
its displayed vector factors geometrically.

Changing the factor order requires its actual exterior sign:

$$
e_{o1}=e_o\wedge e_1=-\,e_1\wedge e_o=-e_{1o}.
$$

A renderer must not hide that sign by silently renaming the blade.

## 5. Several related pseudoscalars occur in CGA

The model contains several relevant spaces:

| Space | Orientation element | Grade |
|---|---|---|
| Euclidean subspace | $I_E=e_1\wedge\cdots\wedge e_n$ | $n$ |
| Null plane | $E_{o\infty}=e_o\wedge e_\infty$ | $2$ |
| Full conformal space | $I_C=e_o\wedge I_E\wedge e_\infty$ | $n+2$ |

The null-plane bivector is a pseudoscalar of that plane, not of the full CGA.
The full model pseudoscalar and `algebra.I` belong to the same top-grade line,
but their orientations can differ.

Some sources instead use

$$
E_{\infty o}=e_\infty\wedge e_o=-E_{o\infty}.
$$

With our chosen $I_C$, the precise relationships are

$$
I_EE_{o\infty}=(-1)^nI_C,
\qquad
I_EE_{\infty o}=(-1)^{n+1}I_C.
$$

Thus an unqualified statement $I_C=I_EE$ is not dimension-independent without
specifying $E$ and the pseudoscalar convention.

A model may expose all these quantities as derived values. That does not
require changing `algebra.I` or adding an independently stored sign flag.

## 6. What is the full CGA pseudoscalar used for?

An important use is duality between two representations:

- OPNS: outer product null space, or direct representation.
- IPNS: inner product null space, or dual representation.

For four suitable conformal points in 3D, an OPNS sphere is

$$
S_{\mathrm{OPNS}}=P_1\wedge P_2\wedge P_3\wedge P_4.
$$

Writing $C=X(c)$ for the normalized conformal embedding of its Euclidean
center, a normalized IPNS sphere is

$$
S_{\mathrm{IPNS}}=C-\frac12r^2e_\infty.
$$

These formulas assume $e_o\cdot e_\infty=-1$. A dual of the raw point wedge
is generally proportional to the normalized vector, not equal to it:

$$
D(S_{\mathrm{OPNS}})=\lambda S_{\mathrm{IPNS}},
\qquad \lambda\ne0.
$$

The selected dual convention and point order affect $\lambda$, including its
sign. Coplanar, repeated, or otherwise degenerate point configurations require
separate treatment.

The traditional right Clifford dual is

$$
D_I(A)=AI^{-1}.
$$

Changing $I$ to $-I$ negates this dual for a fixed $A$. Changing coordinate
basis additionally changes the coefficient representation of $A$ itself.

## 7. Why signs matter even for homogeneous geometry

For a nonzero homogeneous blade, multiplying by a nonzero real scalar
preserves its unoriented null-space locus. For example,

$$
X\cdot S=0
\quad\Longleftrightarrow\quad
X\cdot(-S)=0.
$$

But sign remains important for:

- Plane normal orientation.
- Oriented circles and spheres.
- Inside/outside and side tests.
- Signed distances.
- Exact algebraic equality rather than equivalence up to scale.

Under the sphere normalization in section 6,

$$
X(x)\cdot S_{\mathrm{IPNS}}
=
\frac12\bigl(r^2-\lVert x-c\rVert^2\bigr).
$$

That fixes an explicit inside/outside convention. A negative rescaling reverses
the sign test even though the surface itself is unchanged.

Galaga must preserve signs. Normalizing a representation, changing its
orientation, and changing its display are separate operations.

## 8. Hodge duality does not remove the orientation choice

For homogeneous $A,B$ of the same grade, a right metric Hodge map can be
characterized relative to a chosen volume element by

$$
A\wedge\star B=\langle A,B\rangle_G\,\mathrm{vol}.
$$

Here the pairing is the metric-induced pairing on exterior powers, not an
unspecified inner-product operation. Reversing the volume orientation reverses
$\star$. For a general non-unit Gram basis, one must also state whether
$\mathrm{vol}$ is the raw basis wedge or the metric-normalized volume.

### Current Galaga operations

These operations already exist and must not be conflated:

| API | Current convention |
|---|---|
| `algebra.I` / `algebra.pseudoscalar()` | Wedge of the native ordered basis |
| `dual(A)` | $AI^{-1}$ with $I=\texttt{algebra.I}$; requires invertible $I$ |
| `undual(A)` | $AI$; inverse of the preceding metric dual |
| `right_hodge_dual(A)` | `complement(metric_apply(A))` |
| `left_hodge_dual(A)` | `uncomplement(metric_apply(A))` |
| `ConformalModel.dual(A)` | The existing right Hodge dual, not a separate $I_C$-based Clifford dual |
| `complement(A)` / `uncomplement(A)` | Metric-independent right/left complements of the native exterior basis |

For the standard native-null CGA normalization, direct checks give

$$
H_R(A)=\widetilde A\,I.
$$

For homogeneous grade $r$, this implies

$$
H_R(A)=(-1)^{r(r-1)/2}I^2D_I(A).
$$

In both 2D and 3D CGA, $I^2=-1$: the two operations differ on vectors but
agree on bivectors. A single global pseudoscalar sign cannot make them
identical on every grade.

Exposing a model pseudoscalar does not automatically retarget any of these
existing operations. Such a change would require an explicit API decision.

### CGA versus PGA

A native null basis need not have a degenerate metric. The standard CGA Gram
matrix has determinant $-1$, so its pseudoscalar is invertible.

PGA has a degenerate metric. Its inverse-pseudoscalar dual is unavailable.
Galaga's metric-applied Hodge maps remain defined but are noninvertible; a
null basis vector can map to zero. Metric-independent complements remain
available. This differs from an invertible, nondegenerate metric Hodge star.

## 9. Test natural OPNS/IPNS reading order

A useful design criterion is:

> Ordered OPNS constructions should have documented, reproducible orientation
> when converted to IPNS.

This is not a proof that one pseudoscalar sign is universally superior. The
dual operation, construction order, normalization and intended orientation
must all be fixed.

For a 2D line,

$$
L=P_1\wedge P_2\wedge e_\infty,
$$

define whether the desired normal points left or right of the direction from
$P_1$ to $P_2$. Do not merely call one sign "natural."

With the current preset and `dual`, direct checks give:

- $P_1=X(0,0)$ and $P_2=X(1,0)$ produce $\operatorname{dual}(L)=e_2$,
  the left normal.
- The counterclockwise unit-circle points $(1,0),(0,1),(-1,0)$ produce
  $2(e_o-\tfrac12e_\infty)$ under the dual, not the normalized sphere vector.

Before a native-basis change, test lines, planes, circles and spheres in
both 2D and 3D, with explicit orientation conventions. Include swapped point
order, exact scale factors, reversed orientation, and inverse conversions.

Dorst's cited paper distinguishes Hodge/projective dualization from metric
polarity and notes a reading-order difference. Its origin-first pseudoscalar
is precedent for a convention, not a substitute for these checks.

## 10. Considered Galaga conventions

This section records the alternatives considered before implementation.
Option B is now the default; the earlier order remains explicitly selectable.

### Option A: Keep the earlier Euclidean-first native basis

Keep

$$
(e_1,\ldots,e_n,e_o,e_\infty).
$$

Advantages include unchanged coefficient indexing, role masks and existing
duality contracts. Its native pseudoscalar differs from our model $I_C$ in odd
Euclidean dimensions. Origin-first display alone does not remove that sign.

### Option B: Make the default native-null basis origin-first

Use

$$
(e_o,e_1,\ldots,e_n,e_\infty)
$$

as the actual ordered basis of newly constructed default native-null presets.
Then

$$
\boxed{\texttt{algebra.I}=I_C=e_o\wedge I_E\wedge e_\infty}.
$$

This aligns semantic roles, basis enumeration, Gram rows and the displayed
wedge definition. In 3D CGA, its native pseudoscalar maps to the negative of
the old native pseudoscalar under the corresponding basis identification.
That is an orientation change, not a renderer correction.

It is a breaking coordinate/convention change. It requires coordinated
updates to Gram construction, roles, blade labels and masks, coordinate
conversion, notebooks and tests. Existing raw arrays must not be reinterpreted.

The proposal concerns the standard native-null preset. Orthogonal-frame
presets and deliberate Lengyel conventions need separate treatment; their
contracts must not be silently replaced.

### Option C: Change display order only

Present $e_o$ before the Euclidean vectors, but keep the native basis.

This preserves arithmetic and coordinate compatibility. It cannot honestly
make `algebra.I` equal the origin-first wedge in 3D. With existing labels,
moving the scalar or blade terms does not even change the factor ordering
inside a compact label. Signed relabelling is a separate presentation choice
and must retain the true coefficient sign.

This option is appropriate for a visual preference, not for redefining the
model's orientation.

### Option D: Keep native coordinates and expose derived model pseudoscalars

Retain the current algebra, but define the model quantities from semantic
roles:

$$
I_E=e_1\wedge\cdots\wedge e_n,
\qquad
I_C=e_o\wedge I_E\wedge e_\infty.
$$

This is coherent. Different oriented frames can define different pseudoscalars
in the same algebra without contradictory stored state. The benefit is
coordinate compatibility; the cost is explaining $I_C=-\texttt{algebra.I}$
in 3D and making every model dual convention explicit.

An independently mutable `pseudoscalar_sign` flag is unnecessary: derive
these quantities from their declared frames.

### The null-plane convention is a separate choice

Writing $I_EE$ is useful once $E$ is explicitly defined. It is not a
dimension-independent replacement for the chosen definition of $I_C$.
Neither a convenience name nor its display should silently set the algebra's
orientation.

## 11. Chosen model definition and implemented native order

The model definition is

$$
\boxed{I_C=e_o\wedge I_E\wedge e_\infty}.
$$

**Accepted and implemented:** Option B, with an explicit compatibility option.
A user can then unpack the actual basis in the advertised order and take its
wedge to obtain both `algebra.I` and the model $I_C$ with no extra sign.

If compatibility takes precedence, Option D is mathematically sound.
Display-only Option C must not be presented as achieving the same semantic
alignment.

The implementation preserves these boundaries:

- Changing `DisplayOrder` must never change mathematical values or dual signs.
- A model pseudoscalar is derived from ordered semantic vectors, not from the
  order in which a table happens to display them.
- Changing the native preset basis is a coordinated, documented migration.
- No silent sign correction belongs in the renderer.
- This proposal does not authorize changing existing dual API conventions.

## 12. Implementation contract and verification

Keep the current algebra-level pseudoscalar contract:

$$
\text{actual ordered basis}
\ \Longrightarrow\
I_{\mathrm{native}}.
$$

For model-level pseudoscalars:

$$
\text{ordered semantic frame}
\ \Longrightarrow\
I_E,\ E,\ I_C.
$$

Proposed names such as `euclidean_pseudoscalar` and `conformal_pseudoscalar`
are not yet implemented. The current `ConformalModel` already exposes
`origin`, `infinity` and `euclidean_basis_vectors()`. New quantities should be
computed from those roles, not hardcoded blade indices or dimension-specific
signs.

The implementation adds executable checks for:

1. The ordered basis and Gram entries, including scaled null pairs.
2. $I_C=e_o\wedge I_E\wedge e_\infty$, in both even and odd dimensions.
3. Basis-coordinate conversion, including the induced exterior signs and
   product preservation.
4. Exact OPNS/IPNS signs and scale under each supported dual operation.
5. Display-only overrides preserving all numerical results.
6. Matrix roundtrips and intended preset-specific exceptions.

The chosen migration and unchanged dual semantics are recorded in
[ADR-134](docs/adrs/134-origin-first-native-null-cga.md).
This change does not introduce a `basis=` or `orientation=` constructor option.

### Concrete Galaga implementation boundaries

The following table records the **pre-change implementation and migration
work**. Those native-order changes are now implemented; the role-based model,
display-only overrides and existing dual definitions remain intact.

| Component | Pre-change behavior | Migration work for origin-first native CGA |
|---|---|---|
| `CGAPreset.build()` and `_native_null_cga_gram()` | Euclidean coordinates precede the null pair | Move the origin Gram row/column together with its coordinate position |
| `null_cga_blade_convention()` | Origin mask is `1 << n`; infinity mask is `1 << (n + 1)` | Derive every label, alias and role from the selected actual basis order |
| `presets.blades.cga()` resolution | Metric validation assumes the Euclidean block comes first and the null pair last | Update validation and naming together; a blade-only preset must not pretend to change coordinates |
| `AlgebraConfig` | Bundles the numeric definition, presentation and model metadata | Keep those three components consistent; do not encode orientation only in presentation |
| `ConformalModel` | Resolves ordered Euclidean roles plus native origin/infinity `BladeRef` values | Audit role-based construction under permutation; do not assume every helper is free of index assumptions |
| `DisplayOrder` and full wedge tables | Reorder displayed terms and both full-table axes only | Preserve these presentation-only semantics |
| Gram and vector-only wedge tables | Use native vector order | Origin-first rows follow naturally only from a real native-basis change |
| Matrix conversion | Uses the native Gram basis and conversion plans | Verify coordinate transformations, products and roundtrips, not equality of raw arrays from different frames |

In an origin-first basis, origin has mask `1`, Euclidean role $e_i$
has mask `1 << i`, and infinity retains `1 << (n + 1)`. Even in
2D, where the top-grade orientation agrees, lower-grade coordinates move and
can acquire exterior permutation signs. This is not merely a top-grade fix.

### Scope decisions

ADR-134 accepts the parameterized origin-first default and compatibility
route below. The new definition ID includes `-origin-first`; the compatibility
order retains the old ID. Model metadata stays `cga-null`.
Protected presets and dual definitions are unchanged.
New model-pseudoscalar factories (item 4) and orthogonal model support
(item 6) are explicitly deferred. The following checklist records why these
are distinct design decisions rather than one implied API expansion.

1. **Parameterized native order.** Prefer a preset parameter that selects
   origin-first by default for the native-null frame and permits an explicit
   Euclidean-first override. This combines a natural new default with an
   intentional compatibility route. The parameter grammar is implemented
   below; do not overload `DisplayOrder` or quietly change the
   meaning of `frame="orthogonal"`.
2. **Compatibility route.** If the default changes, decide how users request
   the former Euclidean-first native convention. Persisted arrays need their
   original basis convention and a defined conversion, not just a signature
   or dimension. Preset IDs and saved configuration examples also need review.
3. **Protected presets.** Keep the deliberate Lengyel CGA/RGA and quaternion
   conventions intact. Orthogonal CGA continues to have actual plus/minus
   coordinates unless separately redesigned.
4. **Model pseudoscalar names and behavior.** Choose explicit properties or
   factories for $I_E$, $I_C$ and the chosen null-plane element. The general
   `algebra.I` contract stays unchanged. Model values should follow the
   existing `expr` inheritance and per-factory override policy; do not add
   unrelated mutable orientation state.
5. **Duality scope.** Adding $I_C$ does not switch `ConformalModel.dual` from
   right Hodge duality to $AI_C^{-1}$. A native reorientation will affect
   orientation-dependent operations under the basis identification, including
   complements. Test all relevant operations, not only top-level `dual`.
6. **Orthogonal model support.** The orthogonal preset exists, but the current
   `ConformalModel` requires `cga-null` metadata and roles naming individual
   native basis vectors. It does not presently accept derived linear
   combinations for origin/infinity. Supporting the same model on an
   orthogonal preset is a separate extension, not an automatic consequence
   of adding model pseudoscalars.

These boundaries are recorded explicitly in the implementation ADR.
The preference for origin-first is not permission to bundle all these API
changes into one undocumented compatibility break.

### Implemented factory shape: a default with explicit overrides

Presets already accept parameters and resolve to immutable configurations.
The native-order choice belongs in the complete CGA recipe, because it affects
the metric coordinates and roles, not just rendering. The spelling is
`basis_order="origin-first"` or `basis_order="euclidean-first"` for the
native-null frame.

```python
# Working-tree API (the next release will include this change):
from galaga import Algebra, DisplayOrder, presets

# Default: native-null, origin-first.
preferred = Algebra(config=presets.cga(3))

# Explicit compatibility convention, including its original orientation.
euclidean_first = Algebra(
    config=presets.cga(3, basis_order="euclidean-first"),
)

# Presentation remains independently overridable using the existing API.
native_storage_display = Algebra(
    config=presets.cga(3, basis_order="origin-first"),
    display_order=DisplayOrder(5, range(32)),
)
```

An omitted order should resolve according to the selected frame: origin-first
for the native-null default, unchanged Euclidean/plus/minus order for
the existing orthogonal frame. Explicit null-basis order choices on an
orthogonal frame are rejected, not silently ignored. The signature uses
`None` to distinguish omission from an explicit incompatible choice.

The selected native order must survive `.build()` in the numeric definition,
blade convention and model roles; it cannot be reconstructed from a display
permutation. The blade-only CGA recipe should be able to describe either
supported native-null order, but must validate the supplied Gram coordinates
and must never transform them itself.

No new display keyword on every preset is required. The existing
`Algebra(config=..., display_order=...)` and `with_display_order(...)` APIs
already override presentation without altering the selected numeric basis.
Grade-then-lexicographic remains the general display default, interpreted in
the selected native basis. Existing deliberate preset display overrides keep
their precedence.

Consequently, selecting Euclidean-first intentionally retains
$I_C=-\texttt{algebra.I}$ in 3D. A parameterized preset makes that choice
explicit; it cannot eliminate the mathematical difference between the two
orientations. Ordinary display overrides never create or remove that sign.

### Cross-library and matrix verification

Include a small executable comparison using Galaga's existing orthogonal
preset. Construct $e_o=(e_--e_+)/2$ and $e_\infty=e_-+e_+$ there, derive $I_E$
and $I_C$ by wedges, and verify the sign table in both 2D and 3D. This needs
no external GA dependency; external formulas must still be cited and checked.

For an actual basis conversion, test its exterior extension at every grade:

$$
F(A\wedge B)=F(A)\wedge F(B),
\qquad
F(AB)=F(A)F(B),
$$

where the source and target metrics are related by the stated basis map.
Then separately verify the orientation factor in duality. An
orientation-reversing identification does not make the respective native
dual operations commute with $F$ without the corresponding sign.

The compact matrix machinery already factors general Gram metrics; that
does not promise identical displayed matrices for independently chosen
representation plans. Preserve numeric roundtrips and products, and compare
representations only after an explicitly defined basis correspondence.
Matrix similarity changes such as Dirac/Weyl representation choices are not
the same thing as reordering the native GA generators.

The resulting teaching notebook should show all three pseudoscalars side by
side, the corresponding bases/Gram matrices, and a signed geometric example.
This makes the convention visible for both native-null and orthogonal-basis
users instead of asking either group to memorize an unexplained minus sign.

## 13. Sources and precedents

- Leo Dorst, Daniel Fontijne and Stephen Mann, *Geometric Algebra for Computer
  Science*. Book-level background; exact convention claims need page references.
- Leo Dorst, [Projective duality encodes complementary orientations in geometric
  algebras](https://onlinelibrary.wiley.com/doi/10.1002/mma.9754), first published
  in 2023, journal volume in 2024. See section 7.1 for the conformal pseudoscalar and
  the explicit choice not to invert it; see footnote 3 for reading order.
- [Hrdina–Návrat-related material](https://www.vut.cz/en/board/habilitation?action=priloha&priloha=247618).
  Retained as a survey lead; precise title, authorship and page references
  remain to be verified.
- [Introductory notes based on Dorst et al.](https://kazkojima.github.io/c3ga-intro.html).
  Supporting explanatory material, not evidence of a universal convention.
- [Python `clifford` CGA documentation](https://clifford.readthedocs.io/en/latest/tutorials/cga/index.html).
  An orthogonal-extension implementation with derived null vectors.
- [Ben Lynn's CGA notes](https://theory.stanford.edu/~blynn/haskell/cga.html).
  A further reference for explicit sphere and plane formulas.
- Bayro-Corrochano, GAigen and `ganja.js` remain useful survey leads, but this
  note does not yet provide precise sources for their individual conventions.

The survey supports genuine variation. Our design should be justified by
explicit semantics and computed examples, not by claiming a single community
standard.
