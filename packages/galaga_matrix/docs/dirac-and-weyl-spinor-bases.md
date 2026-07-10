# Dirac, Weyl, and Majorana Spinor Bases

## Short Version

The current `galaga_matrix` $Cl(1,3)$ compact representation uses the standard
Dirac basis. That is a reasonable default for users coming from introductory
relativistic quantum mechanics and the traditional Dirac equation.

For a broader conceptual map from common QM basis choices to pure STA thinking,
see [QM Spinor Bases and STA Translation](qm-bases-and-sta-translation.md).

A Weyl, or chiral, basis is also important. In that basis a Dirac spinor is
literally two stacked Weyl spinors:

$$
\psi =
\begin{pmatrix}
\psi_L\\
\psi_R
\end{pmatrix}.
$$

That form is clearer for chirality, massless fermions, weak interactions,
two-component spinor notation, and spinor-helicity methods.

A Majorana basis is another useful named basis. It does not make chirality
visible. Instead, it makes charge conjugation and the Majorana reality
condition visible. In the convention used here, charge conjugation becomes
ordinary componentwise complex conjugation, so a Majorana spinor is represented
by a real four-component column.

The recommendation is:

- keep the current Dirac basis as the default;
- add a named Weyl/chiral basis as an explicit alternative;
- add a named Majorana basis as an explicit alternative once charge
  conjugation helpers are public;
- use the Weyl basis in notebooks when the subject is chirality or Weyl
  spinors;
- use the Majorana basis in notebooks when the subject is charge conjugation,
  Majorana spinors, or real Lorentz spin representations;
- never identify "top two components" with Weyl spinors unless the selected
  basis is explicitly chiral.
- never call a generic Majorana-basis column a Majorana spinor unless it
  satisfies the Majorana reality condition.

## Four Related Objects

There are four closely related spinor columns that can look deceptively
similar:

| Object | Column size | Main group/action | Common use |
|---|---:|---|---|
| Pauli spinor | $2$ complex | spatial rotations, $SU(2)$ | nonrelativistic spin-$\frac12$ |
| Weyl spinor | $2$ complex | one chiral $SL(2,\mathbb C)$ representation | massless relativistic spin-$\frac12$ |
| Dirac spinor | $4$ complex | full Lorentz spin representation | massive relativistic spin-$\frac12$ |
| Majorana spinor | $4$ real in a Majorana basis | Lorentz spin representation with a reality condition | neutral relativistic spin-$\frac12$ |

A Pauli spinor and a Weyl spinor are both two-component complex columns, but
they are not the same concept. A Pauli spinor is naturally tied to spatial
rotations. A Weyl spinor transforms under one of the two inequivalent chiral
Lorentz spin representations.

A Dirac spinor combines both chiral pieces:

$$
\psi_D =
\begin{pmatrix}
\psi_L\\
\psi_R
\end{pmatrix}
$$

in a chiral basis. A mass term couples $\psi_L$ and $\psi_R$. In the massless
case, the two Weyl equations decouple.

A Majorana spinor is not a third independent chirality. It is a Dirac spinor
with an additional charge-conjugation reality condition:

$$
\psi^c = \psi.
$$

In a Majorana basis that condition becomes

$$
\psi_M^* = \psi_M.
$$

## What Users May Expect

There is no single basis that every quantum mechanics reader expects.

Readers coming from introductory relativistic quantum mechanics often expect
the standard Dirac representation because it makes $\Gamma^0$ diagonal:

$$
\Gamma^0_D =
\begin{pmatrix}
I_2 & 0_2\\
0_2 & -I_2
\end{pmatrix}
=
\begin{pmatrix}
1 & 0 & 0 & 0\\
0 & 1 & 0 & 0\\
0 & 0 & -1 & 0\\
0 & 0 & 0 & -1
\end{pmatrix}.
$$

That basis is useful for:

- rest-frame positive/negative energy intuition;
- the nonrelativistic limit;
- "large" and "small" components;
- older or introductory Dirac-equation treatments.

Readers coming from QFT, Standard Model chirality, Weyl/Majorana spinors,
neutrino physics, or spinor-helicity methods often expect the Weyl/chiral
representation because it makes $\Gamma^5$ diagonal:

$$
\Gamma^5_W =
\begin{pmatrix}
-I_2 & 0_2\\
0_2 & I_2
\end{pmatrix}
=
\begin{pmatrix}
-1 & 0 & 0 & 0\\
0 & -1 & 0 & 0\\
0 & 0 & 1 & 0\\
0 & 0 & 0 & 1
\end{pmatrix}.
$$

That basis is useful for:

- left- and right-handed Weyl spinors;
- massless fermions;
- weak interactions;
- chirality projectors;
- two-component spinor notation.

Readers discussing real relativistic spinors, charge conjugation, neutral
fermions, or supersymmetry may also expect a Majorana basis. That basis is
useful for:

- making charge conjugation simple;
- writing the Majorana condition as a real-column condition;
- showing that proper Lorentz rotor matrices can be represented by real
  matrices;
- separating "Majorana reality" from "Weyl chirality".

These named bases are related by unitary changes of basis, so they describe the
same Clifford algebra and the same physics.

## Current `galaga_matrix` Convention

For $Cl(1,3)$, the current compact basis is the standard Dirac basis for
signature $(+,-,-,-)$:

$$
\Gamma^0_D =
\begin{pmatrix}
I_2 & 0_2\\
0_2 & -I_2
\end{pmatrix}
=
\begin{pmatrix}
1 & 0 & 0 & 0\\
0 & 1 & 0 & 0\\
0 & 0 & -1 & 0\\
0 & 0 & 0 & -1
\end{pmatrix},
$$

and

$$
\Gamma^i_D =
\begin{pmatrix}
0_2 & \sigma_i\\
-\sigma_i & 0_2
\end{pmatrix},
\qquad
i=1,2,3.
$$

The chirality matrix is

$$
\Gamma^5_D
=
i_{\mathbb C}\Gamma^0_D\Gamma^1_D\Gamma^2_D\Gamma^3_D
=
\begin{pmatrix}
0_2 & I_2\\
I_2 & 0_2
\end{pmatrix}.
$$

Here $I_2$ is the $2\times2$ identity matrix, $0_2$ is the $2\times2$ zero
matrix, and $i_{\mathbb C}$ is the ordinary complex scalar imaginary unit. None
of these is the STA pseudoscalar $\gamma_0\gamma_1\gamma_2\gamma_3$.

Therefore, in the current basis, the top two and bottom two components are not
left- and right-handed Weyl spinors. They are eigenspaces of $\Gamma^0_D$, not
eigenspaces of $\Gamma^5_D$.

The current spinor-column conversion uses a fixed reference column:

$$
u_D =
\begin{pmatrix}
1\\0\\0\\0
\end{pmatrix},
$$

and maps an even STA multivector by

$$
\psi_D = \rho(\Psi)u_D.
$$

That convention is valid and roundtrips because the selected reference-column
map has full rank on $Cl^0(1,3)$.

## Weyl/Chiral Convention

For a Weyl-focused representation, we should choose a stack order and document
it. The recommended order is:

$$
\psi_W =
\begin{pmatrix}
\psi_L\\
\psi_R
\end{pmatrix}.
$$

With this order, define

$$
\sigma^\mu = (I_2,\sigma_1,\sigma_2,\sigma_3),
$$

and

$$
\bar\sigma^\mu = (I_2,-\sigma_1,-\sigma_2,-\sigma_3).
$$

The Weyl-basis gamma matrices are:

$$
\Gamma^\mu_W =
\begin{pmatrix}
0_2 & \sigma^\mu\\
\bar\sigma^\mu & 0_2
\end{pmatrix}.
$$

Equivalently:

$$
\Gamma^0_W =
\begin{pmatrix}
0_2 & I_2\\
I_2 & 0_2
\end{pmatrix},
$$

and

$$
\Gamma^i_W =
\begin{pmatrix}
0_2 & \sigma_i\\
-\sigma_i & 0_2
\end{pmatrix}.
$$

The chirality matrix becomes diagonal:

$$
\Gamma^5_W =
\begin{pmatrix}
-I_2 & 0_2\\
0_2 & I_2
\end{pmatrix}
=
\begin{pmatrix}
-1 & 0 & 0 & 0\\
0 & -1 & 0 & 0\\
0 & 0 & 1 & 0\\
0 & 0 & 0 & 1
\end{pmatrix}.
$$

The chiral projectors are then:

$$
P_L = \frac12(1-\Gamma^5_W)
=
\begin{pmatrix}
I_2 & 0_2\\
0_2 & 0_2
\end{pmatrix},
$$

and

$$
P_R = \frac12(1+\Gamma^5_W)
=
\begin{pmatrix}
0_2 & 0_2\\
0_2 & I_2
\end{pmatrix}.
$$

So, in this convention:

$$
P_L\psi_W =
\begin{pmatrix}
\psi_L\\
0
\end{pmatrix},
\qquad
P_R\psi_W =
\begin{pmatrix}
0\\
\psi_R
\end{pmatrix}.
$$

Some authors use the opposite stack order,

$$
\psi =
\begin{pmatrix}
\psi_R\\
\psi_L
\end{pmatrix}.
$$

That is also valid, but it changes the signs and labels of the projectors. The
API and docs should avoid ambiguity by choosing one order.

## The Exact Change of Basis

For the current `galaga_matrix` Dirac basis, the unitary transform from Dirac
coordinates to the recommended Weyl coordinates is:

$$
U_{W\leftarrow D}
=
\frac{1}{\sqrt2}
\begin{pmatrix}
I_2 & -I_2\\
I_2 & I_2
\end{pmatrix}.
$$

The spinor column changes by:

$$
\psi_W = U_{W\leftarrow D}\psi_D.
$$

The gamma matrices change by:

$$
\Gamma^\mu_W
=
U_{W\leftarrow D}\Gamma^\mu_DU_{W\leftarrow D}^\dagger.
$$

The inverse transform is:

$$
\psi_D = U_{W\leftarrow D}^\dagger\psi_W.
$$

The current reference column becomes:

$$
u_W
=
U_{W\leftarrow D}u_D
=
\frac{1}{\sqrt2}
\begin{pmatrix}
1\\0\\1\\0
\end{pmatrix}.
$$

So moving to a Weyl basis does not change the abstract spinor. It changes the
coordinate representation of the same column and the corresponding gamma
matrices.

## Majorana Convention

A Majorana basis is chosen to simplify charge conjugation, not chirality. For
the current Dirac basis, use the charge-conjugation convention

$$
\psi_D^c = B_D\psi_D^*,
\qquad
B_D = i_{\mathbb C}\Gamma^2_D.
$$

Here $i_{\mathbb C}$ is the ordinary scalar complex imaginary unit. It is not
the STA pseudoscalar.

The Majorana transform used in the example notebook is:

$$
U_{M\leftarrow D}
=
\frac{1}{\sqrt2}
\begin{pmatrix}
i_{\mathbb C} & 0 & 0 & -i_{\mathbb C}\\
0 & i_{\mathbb C} & i_{\mathbb C} & 0\\
1 & 0 & 0 & 1\\
0 & 1 & -1 & 0
\end{pmatrix}.
$$

It is unitary and satisfies

$$
U_{M\leftarrow D}B_DU_{M\leftarrow D}^T = I_4.
$$

The spinor column changes by:

$$
\psi_M = U_{M\leftarrow D}\psi_D.
$$

The gamma matrices change by:

$$
\Gamma^\mu_M
=
U_{M\leftarrow D}\Gamma^\mu_DU_{M\leftarrow D}^\dagger.
$$

In this convention the Majorana-basis gamma matrices are pure imaginary. The
bivector generators $\Gamma^\mu_M\Gamma^\nu_M$ are therefore real for
$\mu\ne\nu$, so proper Lorentz rotor matrices are real in this basis.

Charge conjugation becomes:

$$
\psi_M^c = \psi_M^*.
$$

Therefore a Majorana spinor is exactly the special case:

$$
\psi_M = \psi_M^*.
$$

A generic Dirac spinor transformed into the Majorana basis is still a complex
four-component column. It should not be called a Majorana spinor unless this
reality condition holds.

## What Happens to the Dirac Equation

In a Weyl basis, the Dirac equation

$$
(i\Gamma^\mu\partial_\mu - m)\psi = 0
$$

becomes a pair of coupled two-component equations:

$$
i\sigma^\mu\partial_\mu\psi_R - m\psi_L = 0,
$$

and

$$
i\bar\sigma^\mu\partial_\mu\psi_L - m\psi_R = 0.
$$

When $m=0$, the equations decouple:

$$
i\sigma^\mu\partial_\mu\psi_R = 0,
$$

and

$$
i\bar\sigma^\mu\partial_\mu\psi_L = 0.
$$

These are the right- and left-handed Weyl equations. This is why the Weyl basis
is the natural basis for massless fermions and chirality-first explanations.

In the Dirac basis, the same split exists, but it is hidden inside the
projectors:

$$
P_L = \frac12(1-\Gamma^5_D),
\qquad
P_R = \frac12(1+\Gamma^5_D).
$$

Since $\Gamma^5_D$ is off-diagonal, the chiral components are linear
combinations of the top and bottom Dirac-basis blocks.

## Chirality Is Not Helicity

Weyl spinors are often discussed together with helicity, but the two ideas are
not identical.

Chirality is the eigenvalue of $\Gamma^5$:

$$
\Gamma^5\psi_L = -\psi_L,
\qquad
\Gamma^5\psi_R = +\psi_R.
$$

Helicity is the projection of spin along momentum. For massless particles,
chirality and helicity are tied together in a Lorentz-invariant way. For massive
particles, helicity depends on the observer frame, while chirality is still the
left/right representation label.

This distinction matters in notebooks. A Weyl-basis column makes chirality
visible, but helicity still requires momentum and a spin projection operator.

## Relation to STA

In the current `galaga_matrix` spinor conversion, an STA spinor is an even
multivector:

$$
\Psi \in Cl^0(1,3).
$$

The complex Dirac column is a coordinate representation:

$$
\Psi
\longleftrightarrow
\psi_D \in \mathbb C^4.
$$

The Weyl split is a further projection of that coordinate representation:

$$
\psi_D
\longleftrightarrow
\psi_W =
\begin{pmatrix}
\psi_L\\
\psi_R
\end{pmatrix}.
$$

It is not the same as the even/odd grade split. The full STA spinor is already
even. Chirality is a representation-level projection using $\Gamma^5$.

The Majorana view is another coordinate representation:

$$
\psi_D
\longleftrightarrow
\psi_M.
$$

It is not a grade projection either. It exposes an anti-linear reality
structure. In the chosen Majorana basis, a real column $\psi_M$ corresponds to a
Dirac-basis column satisfying $\psi_D^c=\psi_D$.

It is also not the same as the quaternionic spinor split. The quaternion APIs
use a separate $M(2,\mathbb H)$ block convention. Those two quaternion entries
should not be identified with left- and right-handed Weyl spinors unless a
specific chiral convention has been chosen and documented.

## Bilinears Are Basis Independent

Changing from the Dirac basis to the Weyl basis should not change physical
bilinears if all objects are transformed consistently.

The Dirac adjoint is:

$$
\bar\psi = \psi^\dagger\Gamma^0.
$$

The scalar bilinear is:

$$
\bar\psi\psi.
$$

The current is:

$$
j^\mu = \bar\psi\Gamma^\mu\psi.
$$

If

$$
\psi_X = U\psi_D,
\qquad
\Gamma^\mu_X = U\Gamma^\mu_DU^\dagger,
$$

then:

$$
\bar\psi_X\psi_X = \bar\psi_D\psi_D,
$$

and

$$
j^\mu_X = j^\mu_D.
$$

This gives a useful test rule for implementation: every basis-transform feature
must preserve the already-tested Dirac bilinears.

## Naming Guidance

Use these names carefully:

| Name | Meaning |
|---|---|
| Dirac basis | current standard gamma-matrix basis with diagonal $\Gamma^0$ |
| Weyl basis | gamma-matrix basis with diagonal $\Gamma^5$ |
| chiral basis | synonym for Weyl basis in this context |
| Majorana basis | gamma-matrix basis where charge conjugation is ordinary complex conjugation |
| Weyl spinor | one two-component chiral piece, $\psi_L$ or $\psi_R$ |
| Dirac spinor | four-component column containing both chiral pieces |
| Majorana spinor | Dirac spinor satisfying $\psi^c=\psi$, represented by a real column in a Majorana basis |
| Pauli spinor | nonrelativistic or spatial-rotation two-component spinor |

Avoid saying "the upper two components are the Weyl spinor" unless the current
column is explicitly in the Weyl/chiral basis.

Avoid saying "Majorana column" when the intended meaning is "any column written
in the Majorana basis." A generic Majorana-basis column can be complex. A
Majorana spinor is the real-column special case.

## Recommended Notebook Usage

For notebooks about the Dirac equation, boosts, rest-frame spinors, positive
and negative energy branches, and the nonrelativistic limit, the current Dirac
basis is a good teaching default.

For notebooks about Weyl spinors, chirality, massless fermions, neutrinos, weak
interactions, or spinor-helicity, use the Weyl basis.

For notebooks about charge conjugation, Majorana spinors, neutral fermions, or
real Lorentz spin representations, use the Majorana basis.

For bridge notebooks, show both:

$$
\psi_D
\xrightarrow{U_{W\leftarrow D}}
\psi_W =
\begin{pmatrix}
\psi_L\\
\psi_R
\end{pmatrix}.
$$

and

$$
\psi_D
\xrightarrow{U_{M\leftarrow D}}
\psi_M.
$$

Then explicitly show that bilinears and roundtrips are unchanged.

## Future Implementation Plan

The implementation should be incremental and convention-first.

### 1. Add a documented basis convention

Add an explicit internal convention for the $Cl(1,3)$ complex spinor basis:

```text
dirac: current default, diagonal Gamma^0
weyl: chiral basis, diagonal Gamma^5, stack order (psi_L, psi_R)
majorana: charge conjugation is complex conjugation, real columns are Majorana spinors
```

This should be recorded in an ADR before changing public APIs.

### 2. Keep the current default

Do not silently change `compact_basis(sta)`, `to_matrix(..., mode="compact")`,
or `to_spinor_column`.

The current Dirac basis should remain the default so existing examples and tests
continue to mean the same thing.

### 3. Add explicit transforms first

Before adding broad API parameters, add small helpers:

```text
dirac_to_weyl_column(column)
weyl_to_dirac_column(column)
dirac_to_weyl_gamma_matrices(gammas)
dirac_to_majorana_column(column)
majorana_to_dirac_column(column)
dirac_to_majorana_gamma_matrices(gammas)
charge_conjugate_column(column, basis="dirac" | "majorana")
chiral_projectors(gammas)
left_weyl_component(column)
right_weyl_component(column)
```

These helpers make the convention visible and are easy to test.

### 4. Add optional basis-aware APIs

After the helpers are proven, consider adding a named basis argument:

```text
compact_basis(alg, basis="dirac" | "weyl")
to_matrix(mv, mode="compact", basis="dirac" | "weyl" | "majorana")
to_spinor_column(mv, basis="dirac" | "weyl" | "majorana")
from_spinor_column(alg, column, basis="dirac" | "weyl" | "majorana")
```

The default should remain `basis="dirac"` unless there is a deliberate future
ADR to change it.

### 5. Add tests

Tests should cover:

- Weyl gamma matrices satisfy the Clifford relation;
- $\Gamma^5_W$ is diagonal with eigenvalues $(-1,-1,+1,+1)$;
- $P_L$ and $P_R$ are idempotent and complementary;
- the unitary transform maps current Dirac gammas to Weyl gammas;
- `dirac_to_weyl_column` and `weyl_to_dirac_column` roundtrip;
- spinor-column roundtrips still work in the Weyl basis;
- scalar, pseudoscalar, and current bilinears match between bases;
- top/bottom Weyl components match $P_L\psi_W$ and $P_R\psi_W$;
- the Majorana transform maps $B_D=i_{\mathbb C}\Gamma^2_D$ to $I_4$;
- Majorana-basis gamma matrices are pure imaginary;
- real Majorana-basis columns satisfy $\psi^c=\psi$ after conversion back to
  the Dirac basis;
- current quaternion spinor APIs are not mislabeled as Weyl/chiral splits.

### 6. Add notebooks

Add or update examples in this order:

1. Extend the Dirac bilinear notebook with a "same bilinears in Weyl basis"
   section.
2. Add a Weyl spinor notebook showing:
   $$
   \psi_D \to (\psi_L,\psi_R),
   $$
   chirality projectors, and the massless decoupling.
3. Add a mass-coupling notebook showing how the Dirac mass term couples
   $\psi_L$ and $\psi_R$.
4. Add or extend a Majorana notebook showing charge conjugation,
   $\psi_M=\psi_M^*$, and real Lorentz rotor matrices.

### 7. Revisit public naming

If basis-aware spinor APIs are added, the docs should distinguish:

- `to_spinor_column(..., basis="dirac")`: four-component Dirac-basis column;
- `to_spinor_column(..., basis="weyl")`: four-component chiral-basis column;
- `to_spinor_column(..., basis="majorana")`: four-component Majorana-basis
  column, not necessarily a Majorana spinor;
- `left_weyl_component(...)`: two-component Weyl spinor;
- `right_weyl_component(...)`: two-component Weyl spinor.
- `is_majorana_spinor(column, basis=...)`: checks the Majorana reality
  condition under the documented charge-conjugation convention.

This avoids overloading "spinor" and keeps the GA/QM dictionary readable.
