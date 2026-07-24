# QM Spinor Bases and STA Translation

## Purpose

Quantum mechanics uses many different "bases". Some are bases for spin states,
some are bases for gamma matrices, and some are basis changes designed to make a
particular approximation or symmetry obvious.

In spacetime algebra (STA), the emphasis shifts. A spinor is represented by an
even multivector

$$
\Psi \in Cl^+(1,3),
$$

and many matrix-basis questions become questions about:

- which observer frame has been chosen;
- which reference spin direction has been chosen;
- which right-acting bivector is being used as the scalar complex imaginary;
- which real-linear operator represents chirality, charge conjugation, or
  energy projection;
- which geometric observables are being extracted from $\Psi$.

This document compares common quantum-mechanics bases with the corresponding
STA way to think about the same use case. It follows the broad Hestenes and
Doran/Lasenby/Gull point of view: spinors are real geometric objects, matrix
columns are coordinates for those objects, and observables should be expressed
as geometric quantities wherever possible.

## The Two Meanings of "Basis"

The word "basis" is overloaded.

### State Basis

A state basis is a basis of the Hilbert space or spin space. Examples:

- spin-up/spin-down along $z$;
- spin-up/spin-down along an arbitrary unit vector $\mathbf a$;
- momentum eigenstates;
- helicity eigenstates.

These are usually tied to measurement questions:

$$
\text{What are the possible outcomes of measuring } \mathbf S\cdot\mathbf a?
$$

### Representation Basis

A representation basis is a basis for the column coordinates and the matrices
acting on those coordinates. Examples:

- standard Dirac gamma matrices;
- Weyl/chiral gamma matrices;
- Majorana gamma matrices;
- Foldy-Wouthuysen transformed Hamiltonians.

These are usually tied to calculation questions:

$$
\text{Which structure do I want to make diagonal or simple?}
$$

STA keeps these ideas separate. A physical rotor is not the same kind of thing
as a matrix representation change.

## Coordinate Changes Versus Rotors

In matrix quantum mechanics, a change from a Dirac column to another column
basis is typically written:

$$
\psi_X = U_{X\leftarrow D}\psi_D,
$$

and operators transform as

$$
\Gamma^\mu_X =
U_{X\leftarrow D}\Gamma^\mu_DU_{X\leftarrow D}^\dagger.
$$

This is a coordinate change on the spinor representation space.

In STA, a physical Lorentz rotor $R$ acts geometrically:

$$
\Psi \mapsto R\Psi,
$$

and vectors transform by a sandwich product:

$$
a \mapsto Ra\widetilde R.
$$

A Dirac-to-Weyl or Dirac-to-Majorana matrix $U$ is not generally such a rotor.
It is better understood as a change of spinor coordinates. If

$$
F_D:\Psi\mapsto\psi_D
$$

is the Dirac-coordinate map, then the corresponding Weyl or Majorana coordinate
map is

$$
F_X = U_{X\leftarrow D}F_D.
$$

You can pull this back into GA:

$$
\mathcal U_X = F_D^{-1}U_{X\leftarrow D}F_D,
$$

but $\mathcal U_X$ is a linear map on the spinor module, not automatically a
spacetime rotor or a physical motion.

## Main STA Dictionary

In a Hestenes-style STA convention, the Dirac spinor is represented by a real
even multivector:

$$
\Psi \in Cl^+(1,3).
$$

Choose an observer vector $\gamma_0$ and define relative spatial basis bivectors

$$
\sigma_k = \gamma_k\gamma_0.
$$

The spacetime pseudoscalar is

$$
I = \gamma_0\gamma_1\gamma_2\gamma_3,
\qquad
I^2=-1.
$$

The scalar complex imaginary used in matrix QM is not automatically "just $I$".
In the common Hestenes dictionary, it is represented by right multiplication by
a fixed bivector, often written

$$
J = I\sigma_3.
$$

Thus

$$
i_{\mathbb C}|\psi\rangle
\quad\longleftrightarrow\quad
\Psi J.
$$

The fixed choice of $J$ is a convention. Changing $J$ is like changing the
reference spin quantization axis or the internal complex structure.

Useful geometric observables are then built without matrix components. For a
Dirac-Hestenes spinor $\Psi$:

$$
V = \Psi\gamma_0\widetilde\Psi
$$

is the probability-current direction/density vector, and

$$
S = \Psi\gamma_3\widetilde\Psi
$$

is the spin direction vector associated with the chosen reference axis. The
rotor part of $\Psi$ carries the physical frame orientation.

For a non-null spinor, Hestenes' polar form is often written schematically as

$$
\Psi = \rho^{1/2}R e^{I\beta/2},
$$

where $\rho$ is a density, $R$ is a Lorentz rotor, and $\beta$ is the
Yvon-Takabayasi angle. Different authors place factors and phases differently,
but the important point is that the degrees of freedom have geometric meaning.

## Comparison Table

| QM basis or representation | What it makes simple | Typical QM use | STA way to approach the same use |
|---|---|---|---|
| Pauli spin basis | spin along a chosen axis | Stern-Gerlach, qubits, Bloch sphere | rotor acting on a reference direction |
| Standard Dirac basis | $\Gamma^0$ diagonal | rest spinors, nonrelativistic limit, large/small components | observer split relative to $\gamma_0$ and rotor/boost geometry |
| Weyl/chiral basis | $\Gamma^5$ diagonal | massless fermions, weak interactions, chirality projectors | chiral projection as a real-linear STA operator |
| Majorana basis | charge conjugation as complex conjugation | real Majorana spinors, neutral fermions | fixed-point condition of a charge-conjugation involution |
| Helicity basis | spin along momentum | scattering, neutrinos, spinor-helicity | compare spin vector with momentum relative to an observer |
| Foldy-Wouthuysen basis | Hamiltonian block diagonalization | positive/negative energy separation, nonrelativistic expansion | energy projection and rest-frame/low-velocity expansion |

The matrix basis is a convenience. The STA question is usually:

$$
\text{Which geometric object or projection is this basis making visible?}
$$

## Pauli Spin Basis

### Matrix QM View

For a nonrelativistic spin-$\frac12$ system, the standard $z$-basis is

$$
|\uparrow_z\rangle =
\begin{pmatrix}
1\\0
\end{pmatrix},
\qquad
|\downarrow_z\rangle =
\begin{pmatrix}
0\\1
\end{pmatrix}.
$$

A general normalized Pauli spinor may be written

$$
|\psi\rangle =
\begin{pmatrix}
\cos(\theta/2)e^{-i\phi/2}\\
\sin(\theta/2)e^{i\phi/2}
\end{pmatrix}.
$$

This makes the Bloch-sphere direction

$$
\mathbf n =
(\sin\theta\cos\phi,\sin\theta\sin\phi,\cos\theta)
$$

easy to read.

### STA/GA View

In $Cl(3,0)$ or the even subalgebra of STA after a spacetime split, use a rotor
$R$ that rotates the reference direction $e_3$ into the measured spin direction:

$$
\mathbf n = R e_3 \widetilde R.
$$

The spinor is the rotor, not a mysterious two-component object. A phase is a
right multiplication by a rotor in the reference spin plane:

$$
R \mapsto R e^{\alpha e_{12}}.
$$

The global phase leaves $\mathbf n$ unchanged:

$$
R e^{\alpha e_{12}} e_3 \widetilde{(R e^{\alpha e_{12}})} =
R e_3\widetilde R.
$$

Example use case:

- QM notebook: show spinor components and compute
  $\langle\psi|\boldsymbol\sigma|\psi\rangle$.
- GA notebook: show $R$, compute $\mathbf n=Re_3\widetilde R$, then compare
  measurement probability
  $$
  P(+\mathbf a)=\frac12(1+\mathbf a\cdot\mathbf n).
  $$

This is the kind of translation Hestenes emphasizes in the real
Pauli-Schrodinger theory: the imaginary unit and Pauli matrices acquire
geometric roles instead of being opaque matrix artifacts.

## Standard Dirac Basis

### Matrix QM View

The standard Dirac basis makes

$$
\Gamma^0_D =
\begin{pmatrix}
I_2 & 0_2\\
0_2 & -I_2
\end{pmatrix}
$$

diagonal. This is useful for rest-frame positive/negative energy intuition. In
the rest frame, positive-energy spinors look like

$$
u_s(0) =
\begin{pmatrix}
\chi_s\\
0
\end{pmatrix},
$$

and negative-energy spinors look like

$$
v_s(0) =
\begin{pmatrix}
0\\
\chi_s
\end{pmatrix}.
$$

This is why introductory relativistic QM often talks about "large" and "small"
components.

### STA/GA View

In STA, the corresponding structure is the choice of an observer vector
$\gamma_0$. The split into time and space is observer-relative, not fundamental.

A rest spin-up electron in the chosen frame can be represented by the identity
spinor, up to density and phase:

$$
\Psi = 1.
$$

A boosted spinor is obtained by a Lorentz rotor:

$$
\Psi' = R\Psi,
\qquad
R = e^{-\varphi\gamma_1\gamma_0/2}.
$$

The physical velocity/current vector is

$$
V = \Psi'\gamma_0\widetilde{\Psi'} =
R\gamma_0\widetilde R.
$$

So the GA teaching path is not "upper components become large and lower
components become small". It is:

1. choose an observer $\gamma_0$;
2. choose a rest spin frame;
3. apply a boost rotor;
4. compute $V$ and $S$ geometrically.

Example use case:

- QM notebook: derive positive-energy Dirac spinors $u_s(p)$ in the standard
  basis.
- STA notebook: build $R(p)$ as the boost from $\gamma_0$ to $p/m$, then compute
  $R\gamma_0\widetilde R$ and $R\gamma_3\widetilde R$.

## Weyl/Chiral Basis

### Matrix QM View

The Weyl basis makes chirality diagonal:

$$
\Gamma^5_W =
\begin{pmatrix}
-I_2 & 0_2\\
0_2 & I_2
\end{pmatrix}.
$$

Then a Dirac spinor is written as

$$
\psi_W =
\begin{pmatrix}
\psi_L\\
\psi_R
\end{pmatrix},
$$

with projectors

$$
P_L=\frac12(1-\Gamma^5),
\qquad
P_R=\frac12(1+\Gamma^5).
$$

This is the natural basis for massless fermions, weak interactions, and
two-component spinor notation. In the massless limit, the Dirac equation splits
into separate Weyl equations. With mass, the left and right pieces couple.

### STA/GA View

Chirality is not the same thing as grade. The STA Dirac spinor $\Psi$ is already
even. Chirality is a representation-level projection.

If the matrix-to-STA dictionary is

$$
i_{\mathbb C}|\psi\rangle \longleftrightarrow \Psi J,
\qquad
\Gamma^\mu|\psi\rangle \longleftrightarrow \gamma^\mu\Psi\gamma_0,
$$

with

$$
J=I\sigma_3,
$$

then the matrix chirality operator

$$
\Gamma^5 = i_{\mathbb C}\Gamma^0\Gamma^1\Gamma^2\Gamma^3
$$

pulls back to the STA real-linear operator

$$
\chi(\Psi)=I\Psi J.
$$

This operator satisfies

$$
\chi^2=1,
$$

so the chiral projections are

$$
\Psi_L=\frac12(\Psi-\chi(\Psi)),
\qquad
\Psi_R=\frac12(\Psi+\chi(\Psi)).
$$

The sign labels depend on the chosen $\Gamma^5$ and stack-order convention, but
the method is stable: define the real-linear chirality operator, then project.

Example use case:

- QM notebook: show $\psi_W=(\psi_L,\psi_R)^T$ and verify
  $\Gamma^5\psi_L=-\psi_L$.
- STA notebook: compute $\chi(\Psi)=I\Psi J$, then verify
  $\chi(\Psi_L)=-\Psi_L$ and $\chi(\Psi_R)=+\Psi_R$.

The Dirac-Hestenes equation is often written, with units and signs depending on
convention, in the form

$$
\nabla\Psi J - eA\Psi = m\Psi\gamma_0.
$$

The mass term is geometrically visible: it couples the parts that the chirality
operator separates. This is the STA analogue of the Weyl-basis statement that
mass couples $\psi_L$ and $\psi_R$.

## Majorana Basis

### Matrix QM View

A Majorana basis is chosen so charge conjugation is simple. In the convention
used in this repo's example notebook,

$$
\psi_D^c = B_D\psi_D^*,
\qquad
B_D=i_{\mathbb C}\Gamma^2_D.
$$

The Majorana basis is chosen so that

$$
B_M=I_4,
$$

and therefore

$$
\psi_M^c=\psi_M^*.
$$

A Majorana spinor is then represented by a real column:

$$
\psi_M=\psi_M^*.
$$

This is useful for neutral fermions, charge-conjugation discussions, and
showing a real form of the Lorentz spin representation.

### STA/GA View

STA spinors already have real coefficients, but that does not mean every STA
spinor is a Majorana spinor. A general even STA spinor has 8 real degrees of
freedom, matching a complex Dirac column. A Majorana spinor has 4 real degrees
of freedom.

The pure GA statement is:

$$
\mathcal C(\Psi)=\Psi,
$$

where $\mathcal C$ is the charge-conjugation involution in the chosen STA
dictionary.

If you already have a matrix convention, the robust way to derive the GA
operation is:

$$
\mathcal C =
F_D^{-1}B_D K F_D,
$$

where $K$ is componentwise complex conjugation. In a fully worked
Hestenes/Doran/Lasenby convention, $\mathcal C$ becomes a specific real-linear
operation on $\Psi$, often expressible through right multiplication and
involutions. The important point is that it is an operator with a fixed-point
subspace, not merely "real coefficients".

Once $\mathcal C$ is known, the Majorana and anti-Majorana parts are:

$$
\Psi_+ = \frac12(\Psi+\mathcal C(\Psi)),
\qquad
\Psi_- = \frac12(\Psi-\mathcal C(\Psi)).
$$

Example use case:

- QM notebook: transform $\psi_D$ to $\psi_M$ and check whether
  $\psi_M=\psi_M^*$.
- STA notebook: define $\mathcal C$, then check whether
  $\mathcal C(\Psi)=\Psi$.

This is exactly the same mathematical test, but the STA version makes clear
that Majorana-ness is a reality condition under charge conjugation, not a
choice of "real-looking notation".

## Helicity Basis

### Matrix QM View

The helicity basis diagonalizes spin along momentum:

$$
h = \frac{\mathbf S\cdot\mathbf p}{|\mathbf p|}.
$$

It is especially useful for scattering, neutrinos, and spinor-helicity methods.
For massless particles, chirality and helicity are tightly related: for
positive-energy massless fermions, chirality matches helicity up to convention.

### STA/GA View

STA treats helicity as a relation between two geometric objects:

- the momentum vector $p$;
- the spin direction or spin bivector derived from $\Psi$.

Relative to an observer $\gamma_0$, decompose momentum into energy and spatial
momentum:

$$
p\gamma_0 = E + \mathbf p.
$$

Compute the spin direction from the spinor:

$$
S = \Psi\gamma_3\widetilde\Psi.
$$

Then helicity is the sign of spin alignment with spatial momentum in that
observer split:

$$
h \sim \operatorname{sign}(\mathbf p\cdot\mathbf s).
$$

For massive particles this depends on the observer frame. For massless
particles the link between helicity and chirality becomes invariant.

Example use case:

- QM notebook: build helicity eigenspinors for a momentum direction
  $\hat{\mathbf p}$.
- STA notebook: build a rotor taking $\gamma_3$ into the spin direction and a
  null or timelike momentum $p$, then compute their relative alignment.

## Foldy-Wouthuysen / Energy Basis

### Matrix QM View

The Foldy-Wouthuysen transformation is not a gamma-matrix basis in the same
sense as Dirac/Weyl/Majorana. It is a transformation chosen to block-diagonalize
the Hamiltonian, separating positive and negative energy sectors order by
order.

It is useful for:

- nonrelativistic expansions;
- identifying Pauli terms;
- comparing Dirac theory with the Schrodinger-Pauli limit;
- suppressing positive/negative energy interference terms.

### STA/GA View

The GA analogue is to work with energy projection and rest-frame geometry
directly.

For a free massive particle, the physically preferred direction is the momentum
or velocity vector:

$$
v = \frac{p}{m}.
$$

A rotor $R$ takes the observer rest vector $\gamma_0$ to $v$:

$$
v=R\gamma_0\widetilde R.
$$

The nonrelativistic limit is then a small-boost expansion:

$$
R = e^{-\varphi\hat{\mathbf p}/2}
\approx 1-\frac{\varphi}{2}\hat{\mathbf p}+\cdots.
$$

Instead of asking "which matrix block is small?", the STA notebook can ask:

- how large is the boost rapidity $\varphi$?
- how does the spin bivector precess?
- what Pauli Hamiltonian terms appear after the observer split?

This is close in spirit to Hestenes' and Doran/Lasenby's treatment of Pauli and
Dirac theory as real geometric equations with the imaginary unit and spin
couplings represented by geometric operations.

## What Basis Changes Do Not Mean In STA

Dirac-to-Weyl and Dirac-to-Majorana changes do not mean the particle physically
rotated or boosted. They mean the coordinate description of the same spinor was
changed.

The physical operations are things like:

$$
\Psi \mapsto R\Psi,
\qquad
a\mapsto Ra\widetilde R.
$$

The representation-basis operations are things like:

$$
\Psi \mapsto F_D^{-1}U_{X\leftarrow D}F_D(\Psi).
$$

Both are useful, but they answer different questions.

## Practical Notebook Pattern

For learning notebooks, a useful structure is:

1. Show the matrix-QM version first.
2. Name the basis and explain what it makes diagonal or simple.
3. Convert the same object to STA.
4. Replace component statements with geometric statements.
5. Verify a roundtrip or invariant.

Examples:

| Notebook topic | Matrix-side check | STA-side check |
|---|---|---|
| Pauli spin | $\langle\sigma\rangle$ matches Bloch vector | $n=Re_3\widetilde R$ |
| Dirac boost | $u_s(p)$ solves Dirac equation | $R\gamma_0\widetilde R=p/m$ |
| Weyl split | $P_L^2=P_L$, $P_R^2=P_R$ | $\chi^2=1$, $\Psi_{L/R}$ are eigenparts |
| Majorana condition | $\psi_M=\psi_M^*$ | $\mathcal C(\Psi)=\Psi$ |
| Bilinears | $\bar\psi\Gamma^\mu\psi$ basis-invariant | $\Psi\gamma^\mu\widetilde\Psi$ geometric |
| Helicity | helicity operator eigenvalue | spin direction aligned with momentum |

## Common Traps

Do not identify upper/lower Dirac components with Weyl spinors unless the basis
is explicitly Weyl/chiral.

Do not say a generic Majorana-basis column is a Majorana spinor. It is a
Majorana spinor only if it satisfies the Majorana reality condition.

Do not treat $i_{\mathbb C}$ as automatically equal to the STA pseudoscalar
$I$. In Hestenes-style STA, the scalar imaginary is usually represented by
right multiplication by a chosen bivector such as $J=I\sigma_3$.

Do not treat a representation-basis change as a Lorentz rotor. A rotor changes
geometric vectors by sandwiching. A basis change changes coordinates.

Do not confuse chirality with grade. The STA Dirac spinor is already even;
chirality is a separate real-linear projection.

## References and Starting Points

- David Hestenes, *Space-Time Algebra*, Gordon and Breach, 1966.
- David Hestenes, "Spacetime Physics with Geometric Algebra", American Journal
  of Physics 71, 691-714, 2003.
- David Hestenes, "Reforming the Mathematical Language of Physics", American
  Journal of Physics 71, 104-121, 2003.
- David Hestenes, "Zitterbewegung in Quantum Mechanics -- a research program",
  [arXiv:0802.2728](https://arxiv.org/abs/0802.2728).
- Chris Doran and Anthony Lasenby, *Geometric Algebra for Physicists*,
  Cambridge University Press, 2003.
- C. J. L. Doran, A. N. Lasenby, S. F. Gull, S. Somaroo, and A. D. Challinor,
  "Spacetime algebra and electron physics",
  [arXiv:quant-ph/0509178](https://arxiv.org/abs/quant-ph/0509178).
- S. Gull, A. Lasenby, and C. Doran, "Imaginary Numbers are not Real: The
  Geometric Algebra of Spacetime", a useful
  [tutorial](https://geometry.mrao.cam.ac.uk/1993/01/imaginary-numbers-are-not-real-the-geometric-algebra-of-spacetime/)
  on replacing opaque matrix imaginaries with geometric structure.
