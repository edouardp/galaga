---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-107: Public Complex and Quaternion Convention Contracts

## Context and problem statement

The remaining `test_quaternion.py` keeps fifteen convention, lookup and
rendering cases on the legacy engine. Core tests already own Hamilton's
identities, but do not own the presentation contracts. All fifteen historical
cases and the two direct core cases pass before migration.

Compute the defining products in Euclidean `Cl(3,0)` before assigning names:
`i=e23`, `j=e13`, `k=e12` have positive native coefficients and satisfy
`ij=k`, `jk=i`, `ki=j` and `ijk=-1`. Choosing `e31` for `j` would reverse
that orientation. Scalars plus these bivectors form the quaternion even
subalgebra. The bivectors alone are not closed under multiplication.

## Decision outcome

Retain all fifteen original class/method identities using the public facade,
`p_quaternion`, `p_complex`, immutable conventions and explicit expression
replay. No numeric, rendering, or public API behavior changes. Correct the
two public quaternion factory/preset docstrings from “bivector subalgebra”
to “even subalgebra.”

The [archive](../../packages/galaga/tools/baselines/quaternion-conventions-v1.json)
was captured at `8f14835` on 2026-09-08 with Python 3.14.4 and NumPy 2.5.2.
It retains the complete source and SHA-256, all fifteen identities, nineteen
observed products/lookups/complex values in three targets, and complete
quaternion, complex and custom-`xyz` basis tables. Each table includes the
actual ordered signature, native coefficients and legacy bivector enumeration.

### Preserve values while making existing v2 differences explicit

- Quaternion integer-mask enumeration remains `k,j,i`. Semantic roles
  `quaternion_i`, `quaternion_j` and `quaternion_k` select conventional
  order, independently of the preset's display order.
- Native aliases `e23`, `e13` and `e12` remain valid. Replace parsed
  metric-role text such as `"+2+3"` with declared roles or integer masks;
  undeclared text raises `KeyError`.
- Replace `lazy=True` with `expr=True`. Signed unit-blade literalization
  preserves coefficients, discards prior names/provenance and attaches a
  self-contained `BladeLiteral`. Negative computed blades retain their sign.
- Replace `b_quaternion(vector_names=...)` with immutable label replacement.
  Preserve aliases, roles and signed references; explicitly choose compound
  labels such as `xyz`. Local-name policy remains independent. Single-character
  names render literally, never as invented `z_{z}` subscripts.
- `p_complex()` and `p_quaternion()` supply matching Euclidean metrics.
  Blade conventions alone do not validate or change an algebra's Gram matrix.
  In another frame, compute a coordinate bivector's square as
  `G_ab**2 - G_aa*G_bb`; the label `i` does not guarantee a square of `-1`.
- Reverse and Clifford conjugation agree on the even subalgebra. They are
  different operations on ambient multivectors with odd grades. The full
  `Cl(3,0)` algebra is not itself the four-dimensional quaternion algebra.

These follow [ADR-076](076-immutable-presentation-configuration.md),
[ADR-097](097-concrete-display-contracts-outlive-legacy-rendering.md), and
[ADR-106](106-independent-public-local-name-contracts.md). No legacy parsing
is restored. Core numeric factories retain native mask order; public basis
collections follow presentation order as revised in
[ADR-158](158-renderable-basis-factory-sequences.md). In particular, quaternion
bivectors unpack as `i, j, k` under the preset's conventional order.

### Add independent numeric and deletion evidence

Replay all nineteen observations and all three complete basis tables in
ASCII, Unicode and LaTeX. Derive the Hamilton coordinate embedding from actual
exterior products, then compare sum, product, reverse, conjugation, inverse,
right division and norm against the scalar/dot/cross Hamilton formula.
Check complex arithmetic against Python's built-in complex numbers.
Inputs include noncommuting dense values, zeros, scalars, pure units and
fractional coefficients; division denominators remain nonzero.

Both expression modes, coefficient finiteness/shape, even-grade closure,
evaluation, hashing and display stability remain checked. Three Gram matrices
cover Euclidean, oblique-indefinite and singular-oblique blade squares.
Mixed-grade probes distinguish reverse from conjugation. Corruption probes
reject altered archive identities, shapes, nonfinite or incorrect values,
wrong rendering, wrong-side division, swapped conjugation, and display-order
enumeration in a native factory.

The existing complex/quaternion notebook now computes before naming, teaches
native versus semantic order, actually uses reverse in the complex-conjugation
lesson, and demonstrates odd-grade and non-Euclidean metric boundaries.
Generated HTML/TeX is inspected, alongside the gallery's headless exports.

## Consequences

### Select the complex representation explicitly

`presets.complex(representation="bivector")` remains the default and
constructs full Euclidean $\mathrm{Cl}(2,0)$, with complex values occupying
grades zero and two and $i=e_1\wedge e_2$. The additional
`representation="vector"` constructs full $\mathrm{Cl}(0,1)$, where $i=e_1$
and every multivector represents a complex number. The option describes the
grade of the imaginary unit; it does not restrict construction to a subalgebra.

`ComplexPreset`, `presets.blades.complex()`, and
`complex_blade_convention()` accept the same two representation names. Blade-only
selection names the vocabulary and validates its dimension; it continues to
leave the target metric unchanged. Complete presets supply the appropriate
metric, native-blade alias (`e12` or `e1`), and `imaginary` role. Both derive
local names from their convention, expose the pseudoscalar under Python key
`i`, and display it as `i`. In the vector representation the only basis vector
is the same blade and therefore also displays as `i`.

Operation semantics remain determined by the ambient metric and grades. For
$z=a+bi$, the definition

$$
\operatorname{norm2}(z)=\langle z\widetilde z\rangle_0
$$

gives $a^2+b^2$ for the bivector representation, because reversion negates
the bivector, and $a^2-b^2$ for the vector representation, because reversion
fixes a vector. Clifford conjugation supplies ordinary complex conjugation
in both cases, so $z\operatorname{clifford\_conjugate}(z)=a^2+b^2$ in either
representation. No preset-specific norm or reversion dispatch is introduced.
In the vector representation this squared norm can vanish for a nonzero
invertible value such as $1+i$; it is not a complex-modulus or invertibility test.
Existing square-root, logarithm, power, and rotor domain rules remain intact.

Tests derive the top blade from the exterior product of the actual basis
vectors and check its square against the Gram determinant. Both representations
are compared with Python complex arithmetic and `cmath` on supported inputs;
tests also cover aliases, roles, locals, basis display, expression replay,
presenter and annotation views, invalid options, and unchanged default behavior.

### Select the quaternion representation explicitly

`presets.quaternion(representation="bivector")` remains the default, constructing
full $\mathrm{Cl}(3,0)$ with quaternion values in its even subalgebra and the
existing positive native blades $i=e_{23}$, $j=e_{13}$, $k=e_{12}$.
The additional `representation="direct"` constructs full $\mathrm{Cl}(0,2)$,
where $i=e_1$, $j=e_2$, and $k=e_1\wedge e_2=e_1e_2$.
Every multivector of this four-dimensional algebra represents a quaternion.
The name `direct` describes this full-algebra representation; its imaginary
units occupy both grades one and two.

Computing the native products before assigning labels confirms in both cases

$$
i^2=j^2=k^2=ijk=-1,\qquad ij=k,\quad jk=i,\quad ki=j.
$$

`QuaternionPreset`, `presets.blades.quaternion()`,
`quaternion_blade_convention()`, and `quaternion_display_order()` accept the
same representation choices. Complete presets provide the metric, roles,
local names, and scalar/$i$/$j$/$k$ display order; the existing default order
continues with the remaining ambient blades. Blade-only recipes preserve the
target metric and order and validate the selected dimension. In the direct
representation `basis_vectors()` exposes $i,j$, `locals()` exposes $i,j,k$,
and the pseudoscalar is $k$. Native aliases remain available in both layouts.

For $q=a+bi+cj+dk$, GA reversion gives

$$
\widetilde q=
\begin{cases}
a-bi-cj-dk & \text{bivector representation},\\
a+bi+cj-dk & \text{direct representation}.
\end{cases}
$$

Consequently $\langle q\widetilde q\rangle_0$ is $a^2+b^2+c^2+d^2$ in
the bivector representation and $a^2-b^2-c^2+d^2$ in the direct representation.
Clifford conjugation sends $q$ to $a-bi-cj-dk$ in either representation, and
its product with $q$ is $a^2+b^2+c^2+d^2$. Operation semantics remain those
of the ambient geometric algebra; no quaternion-specific dispatch is added.

Regression tests derive named units from actual basis products and compare
arithmetic, inverse, right division, conjugation, and powers with independent
Hamilton coordinates. They check supported exponential/logarithm/square-root
identities, representation-specific involutions and norms, expression replay,
aliases, roles, default compatibility, presentation composition, annotation
views, TOML configuration, and invalid representation choices.

### Historical validation

All 155 focused cases pass with 100% line/branch coverage in the three test
files. All 143 public cases pass directly from the built wheel with package
origins verified and legacy imports forbidden. Full package/release suites
pass 6,113 cases on Python 3.11 and 6,230 on Python 3.14. Core/facade coverage,
the existing matrix warning, and 295 type errors are unchanged.

The construction-exemption ledger falls from seven files to six. Remaining
mixed legacy suites, namespace/construction guards, engine deletion and final
release gates remain separate work. This is a completed test-dependency unit,
not a completed release.
