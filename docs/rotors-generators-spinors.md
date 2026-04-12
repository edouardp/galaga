# Rotors, Generators, and Spinors: Definitions Across Communities

A survey of how the GA applied community, the mathematics community, and the physics community define these terms — and where they disagree.

## What is a rotor?

There are three definitions in active use.

### GA applied community (Hestenes, Doran & Lasenby, Dorst, Chisolm, Cohoe)

A rotor is an **even versor** (product of an even number of vectors) that is **normalized**: $R\tilde{R} = 1$.

Hestenes originally defined it as the product of two unit vectors, then broadened it. Chisolm follows this path — initially defining a rotor as an invertible biversor ($\S$ 1.3), then later ($\S$ 9.3) broadening to "any even invertible versor." Cohoe (Def 6.1) defines a spinor as a product of an even number of vectors, and a rotor as a normalized spinor.

A rotor is **not** "any element of the even subalgebra." It must be constructible as a product of vectors (a versor) and must be invertible/normalized. A general even multivector might not be expressible as a product of vectors.

### Pure mathematics (Clifford algebra / spin group literature)

A rotor is an element of $\mathrm{Spin}(V)$ — the subgroup of the even Clifford algebra $\mathrm{Cl}^0(V)$ consisting of elements $R$ with $R\tilde{R} = 1$.

Wikipedia states: "a rotor in the geometric algebra of $V$ is the same thing as an element of the spin group $\mathrm{Spin}(V)$." For $n > 2$, the rotor group is the identity component $\mathrm{Spin}^e(V)$.

### PGA / motor algebra community (Gunn, De Keninck)

In projective geometric algebra, the term **motor** replaces "rotor" for the general case (rotation + translation). A motor is an element of the even subalgebra satisfying appropriate normalization. Not every motor is the exponential of a single bivector — some are products of non-commuting exponentials.

### Key disagreement

Is every element of the even subalgebra with $R\tilde{R} = 1$ a rotor?  Mathematicians say yes — it's the definition of $\mathrm{Spin}(V)$. GA practitioners sometimes insist a rotor must be *constructible* as a product of vectors. For finite-dimensional real Clifford algebras these are the same set, but the conceptual framing differs.

## What is a "generator"?

The word **"generator" is not standard GA terminology.** It comes from Lie theory.

### Physics / Lie group community

A "generator" is an element of the Lie algebra $\mathfrak{g}$ that, when exponentiated, produces a group element. For rotations, the Lie algebra of $\mathrm{Spin}(r,s)$ is the space of bivectors $\bigwedge^2 V$ under the commutator bracket. So a bivector $B$ is a "generator" of the rotation $\exp(B)$. Physicists routinely call bivectors "generators of rotations."

### GA community

They avoid the word almost entirely. Instead they say "the bivector $B$ defines the plane of rotation" or "$B$ is the rotation plane." Doran & Lasenby, Hestenes, Chisolm, Dorst — none of them use "generator" in this sense.

Hestenes & Sobczyk (1984) and Doran & Lasenby (2003) both establish that the bivectors form the Lie algebra of the rotor group under the commutator product, but they frame this as a *consequence* rather than a definition.

### Mathematics community

Bivectors are elements of the Lie algebra $\mathfrak{spin}(V)$. The exponential map sends them to $\mathrm{Spin}(V)$. The term "generator" is used in the standard Lie algebra sense — an element of a basis for the Lie algebra.

## The anatomy of $\exp(-B\theta/2)$

### What are $B$, $\theta$, and the $\frac{1}{2}$?

Chisolm is very explicit about this ($\S$ 1.3 and $\S$ 9.3.1):

- $B$ is a *unit bivector* ($B^2 = -1$ in the Euclidean/elliptic case). It encodes the plane of rotation and its orientation (sense of rotation).
- $\theta$ is the rotation angle.
- $\theta/2$ is the half-angle. It arises because rotation = two reflections, and the angle between the two reflection axes is $\theta/2$. It's geometric, not a convention.

  The formula

$$
R = \cos(\theta/2) - B\sin(\theta/2) = \exp(-B\theta/2)
$$

only works when $B^2 = -1$.

Chisolm also handles the other cases in $\S$ 9.3.1:

| $B^2$ | Type               | Rotor form                         | Interpretation                 |
| ----- | ------------------ | ---------------------------------- | ------------------------------ |
| $-1$  | Euclidean/elliptic | $\cos(\theta/2) - B\sin(\theta/2)$ | Rotation by $\theta$           |
| $+1$  | Hyperbolic         | $\cosh(\phi/2) - B\sinh(\phi/2)$   | Lorentz boost                  |
| $0$   | Degenerate (PGA)   | $1 - B\delta/2$                    | Translation (series truncates) |

### Convention differences in what you pass to $\exp()$

| Convention                                        | What you exponentiate                                                 | Who uses it                                   |
| ------------------------------------------------- | --------------------------------------------------------------------- | --------------------------------------------- |
| $\exp(-B\theta/2)$                                | Unit bivector $B$, angle $\theta$, explicit half-angle                | Chisolm, Hestenes, Doran & Lasenby            |
| $\exp(B)$ where $B$ is a general bivector         | The bivector _is_ the full exponent; magnitude encodes the half-angle | Dorst, most software libraries, PGA community |
| $\exp(-\hat{B}\theta/2)$ with $\hat{B}^2 = \pm 1$ | Normalized bivector, separate angle                                   | Physics texts                                 |

The second convention is what most code uses (including galaga's `exp`). You pass a bivector whose magnitude already encodes the half-angle. The decomposition into "unit plane $\times$ angle / 2" is a human interpretation, not something the algebra requires.

## What does $\log()$ return?

Neither Chisolm nor Cohoe discuss logarithms.

In the wider literature:

- **Dorst** ($\S$ 7.4.3 of "GA for Computer Science") shows that in Euclidean and Minkowski spaces, any bivector $B$ decomposes into a sum of commuting 2-blades $B = B_1 + B_2 + \cdots$, so $\exp(B) = \exp(B_1)\exp(B_2)\cdots$. The logarithm reverses this.

- **For simple rotors** (single plane): $\log(\exp(-\hat{B}\theta/2)) = -\hat{B}\theta/2$. You get back the full exponent — the unit bivector scaled by the half-angle. To recover the angle: $2|\log(R)|$. To recover the plane: normalize $\log(R)$.

- **For compound rotors** (4D+, multiple planes): $\log(R)$ is a general bivector that is *not* a blade. It's the sum of the individual plane contributions. Dorst's invariant decomposition is needed to factor it.

- **For degenerate cases** (PGA translations): $\log(1 + \varepsilon B) = \varepsilon B$ (the series truncates). The "angle" is really a displacement.

## What is a spinor?

This is the most overloaded term. There are at least four incompatible definitions.

### Definition 1: GA / Hestenes — "even element that transforms single-sidedly"

Cohoe uses this (Def 6.1): a spinor is a product of an even number of vectors. A rotor is a normalized spinor.

The GA community generally treats spinors as elements of the even subalgebra $\mathrm{Cl}^0(V)$ that transform under rotations by single-sided multiplication: $\psi \to R\psi$, rather than the double-sided sandwich $R\psi\tilde{R}$ used for vectors.

The key insight: a spinor is *an element of the algebra itself*, not something living in a separate vector space. A rotor acts on vectors via sandwich product, but rotors compose with each other via ordinary (single-sided) multiplication. So a rotor is simultaneously an operator (when sandwiching) and a spinor (when being composed).

This is the simplest definition and the one most GA software uses. But it doesn't capture everything physicists mean by "spinor."

### Definition 2: Mathematics — "element of a minimal left ideal"

The Chevalley/Lounesto definition. Pick an idempotent $p$ — like $p = \frac{1}{2}(1 + e_n)$ — and form the minimal left ideal $\mathrm{Cl}(V)p$. Spinors are elements of this ideal.

This is more general than Definition 1. The even subalgebra and a minimal left ideal are not the same thing in general, though they are isomorphic as $\mathrm{Spin}(V)$ representations in many cases.

The advantage: it gives a concrete matrix-column representation. If you represent $\mathrm{Cl}(3,0)$ as $2 \times 2$ matrices (via Pauli matrices), then a minimal left ideal is the set of matrices with only one nonzero column — exactly the physicist's 2-component spinor.

### Definition 3: Physics — "element of an irreducible representation of $\mathrm{Spin}(V)$"

The standard physics definition. A spinor is a column vector that transforms under $\psi \to S\psi$ where $S \in \mathrm{Spin}(V)$ acts via a matrix representation. The spinor lives in a *separate* vector space from the Clifford algebra.

- 3D: 2-component complex vectors (Pauli spinors)
- 4D: 4-component complex vectors (Dirac spinors), decomposing into two 2-component Weyl spinors (chiral/semi-spinors)

  This definition is representation-theoretic — it doesn't care about the Clifford algebra construction, only about how the object transforms.

### Definition 4: Cartan — "square root of a null vector" (pure spinors)

Cartan's original definition: a spinor $\psi$ is *pure* if there exists a maximal totally isotropic subspace $S$ such that $x\psi = 0$ for all $x \in S$. A null vector can be "factored" into a product of a left spinor and a right spinor.

This is the most geometric definition but also the most restrictive. In low dimensions ($\leq 6$ for complex, $\leq 3{+}1$ for Lorentzian), all spinors happen to be pure. In $8+$ dimensions, not all spinors are pure.

### When the definitions coincide

| Dimension     | Def 1 (GA even) | Def 2 (minimal ideal) | Def 3 (physics rep) | Def 4 (pure/Cartan)          |
| ------------- | --------------- | --------------------- | ------------------- | ---------------------------- |
| 3D Euclidean  | All equivalent  | All equivalent        | All equivalent      | All equivalent               |
| 4D Lorentzian | All equivalent  | All equivalent        | All equivalent      | All equivalent               |
| 6D            | Equivalent      | Equivalent            | Equivalent          | Still all pure               |
| 8D+           | Still works     | Still works           | Still works         | **Not all spinors are pure** |

The coincidence in low dimensions is why people get away with treating these as "the same thing." The disagreements only bite in higher dimensions or degenerate signatures.

## How spinor definition affects rotor/generator meaning

The choice of spinor definition determines what "rotor" and "generator" mean:

- **If spinor = even element** (GA): a rotor is a normalized spinor, and the bivector you exponentiate is just "the thing in the exponent." No separate concept of "generator" is needed.

- **If spinor = column vector** (physics): a rotor is a *matrix* acting on spinors, the bivector is a *matrix* in the Lie algebra (a "generator"), and $\exp$ maps generators to group elements. The $\frac{1}{2}$ shows up because the Lie algebra representation has a factor of $\frac{1}{2}$ built in — the $\sigma_i/2$ for $\mathrm{SU}(2)$.

- **If spinor = ideal element** (Lounesto): a rotor acts by left multiplication on the ideal, and the bivector generates this action.

## The half-angle: everyone agrees

The $\frac{1}{2}$ in $\exp(-B\theta/2)$ is not a convention in any framework.  But *why* it's there gets explained differently:

- **GA**: because rotation = two reflections at half the angle
- **Physics**: because the spin representation has eigenvalues $\pm\frac{1}{2}$
- **Mathematics**: because $\mathrm{Spin}(V)$ is a double cover of $\mathrm{SO}(V)$

These are three descriptions of the same geometric fact.

## References

- Chisolm, "Geometric Algebra" (arXiv:1205.5935v1)
- Cohoe, "Rigorous Development of Geometric Algebra" (2024)
- Hestenes & Sobczyk, "Clifford Algebra to Geometric Calculus" (1984)
- Doran & Lasenby, "Geometric Algebra for Physicists" (2003)
- Dorst, Fontijne & Mann, "Geometric Algebra for Computer Science" (2007)
- Lounesto, "Clifford Algebras and Spinors" (2001)
- Cartan, "The Theory of Spinors" (1966, Dover reprint)
- Benn & Tucker, "An Introduction to Spinors and Geometry" (1987)
- Hestenes, "Lie groups as spin groups" (J. Math. Phys. 34, 1993)
- Wikipedia, "Rotor (mathematics)" — https://en.wikipedia.org/wiki/Rotor_(mathematics)
- Wikipedia, "Spinor" — https://en.wikipedia.org/wiki/Spinor
- Marsh, "Mathematics for Physics" — http://www.mathphysicsbook.com/?page_id=1867
- eigenchris, "Conflicting definitions of a spinor" — https://physics.stackexchange.com/questions/639161

## Appendix: Notation and Definitions

### Algebra notation

Different communities use different symbols for the same algebra:

| Notation                                                  | Used by                                                | Meaning                                                                             |
| --------------------------------------------------------- | ------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| $\mathrm{Cl}(V)$ or $\mathrm{Cl}(p,q)$                    | Mathematics (Lounesto, Lawson & Michelsohn, Chevalley) | Clifford algebra. The standard in pure maths                                        |
| $\mathcal{G}(V)$ or $\mathcal{G}(p,q)$ or $\mathcal{G}^n$ | GA community (Hestenes, Doran & Lasenby)               | Geometric algebra. Same object, different name emphasising geometric interpretation |
| $\mathcal{G}(B)$ or $G(B)$                                | Cohoe                                                  | Geometric algebra parametrised by bilinear form $B$                                 |
| $C\ell(V)$ or $C\ell_{p,q}$                               | Some European texts                                    | Variant typesetting of $\mathrm{Cl}$                                                |

These all denote the same mathematical object. "Clifford algebra" is the traditional name from mathematics; "geometric algebra" is the name popularised by Hestenes to emphasise the geometric (rather than purely algebraic) interpretation. The notation $\mathcal{G}^n$ typically means the geometric algebra of an $n$-dimensional vector space, leaving the signature implicit.

The even subalgebra follows the same pattern:

| Notation                                 | Meaning                 |
| ---------------------------------------- | ----------------------- |
| $\mathrm{Cl}^0(V)$ or $\mathrm{Cl}^+(V)$ | Even subalgebra (maths) |
| $\mathcal{G}^+(V)$ or $\mathcal{G}^0(V)$ | Even subalgebra (GA)    |

The superscript 0 means "grade mod 2 = 0" (i.e. even), not "grade 0." Some authors use $+$ instead of $0$ for the same thing.

### Symbol reference

| Symbol                     | Name                              | Meaning                                                                                                                                                             |
| -------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| $\mathrm{Cl}(V)$           | Clifford algebra                  | The full algebra generated by vector space $V$ with quadratic form $q$                                                                                              |
| $\mathrm{Cl}(p,q)$         | Clifford algebra (by signature)   | Clifford algebra of $\mathbb{R}^{p+q}$ with $p$ basis vectors squaring to $+1$ and $q$ to $-1$                                                                      |
| $\mathrm{Cl}^0(V)$         | Even subalgebra                   | Subspace of even-grade elements (grades 0, 2, 4, ...). Forms a subalgebra since even $\times$ even = even. The superscript 0 means "grade mod 2 = 0", not "grade 0" |
| $\mathrm{Cl}^1(V)$         | Odd subspace                      | Subspace of odd-grade elements (grades 1, 3, 5, ...). Not a subalgebra (odd $\times$ odd = even)                                                                    |
| $\bigwedge^k V$            | $k$-th exterior power             | The space of $k$-vectors (grade-$k$ elements)                                                                                                                       |
| $\bigwedge^2 V$            | Bivector space                    | The space of all bivectors; also the Lie algebra of $\mathrm{Spin}(V)$ under the commutator bracket                                                                 |
| $\tilde{R}$ or $R^\dagger$ | Reverse                           | Product of the same vectors in reversed order. On a $k$-vector: $\tilde{A}_k = (-1)^{k(k-1)/2} A_k$                                                                 |
| $\hat{A}$ or $A^*$         | Grade involution                  | Negates odd-grade components: $\hat{A}_k = (-1)^k A_k$                                                                                                              |
| $\bar{A}$ or $A^\ddagger$  | Clifford conjugate                | Composition of reverse and grade involution: $\bar{A} = \widehat{\tilde{A}}$                                                                                        |
| $\langle A \rangle_k$      | Grade projection                  | The grade-$k$ component of multivector $A$                                                                                                                          |
| $\langle A \rangle$        | Scalar part                       | Shorthand for $\langle A \rangle_0$                                                                                                                                 |
| $\mathrm{Spin}(V)$         | Spin group                        | $\{ R \in \mathrm{Cl}^0(V) \mid R\tilde{R} = 1 \}$. Double cover of $\mathrm{SO}(V)$                                                                                |
| $\mathrm{Spin}^e(V)$       | Spin group (identity component)   | The connected component of $\mathrm{Spin}(V)$ containing the identity. For $n > 2$, this is the rotor group                                                         |
| $\mathrm{Pin}(V)$          | Pin group                         | Like $\mathrm{Spin}(V)$ but includes odd versors (reflections). Double cover of $\mathrm{O}(V)$                                                                     |
| $\mathrm{SO}(V)$           | Special orthogonal group          | Rotations (determinant $+1$ orthogonal transformations)                                                                                                             |
| $\mathfrak{spin}(V)$       | Lie algebra of $\mathrm{Spin}(V)$ | The bivector space $\bigwedge^2 V$ with the commutator bracket $[A,B] = \frac{1}{2}(AB - BA)$                                                                       |

### Notation conflicts across communities

The same symbol can mean different things:

| Symbol      | GA convention                                                       | Physics convention                                  |
| ----------- | ------------------------------------------------------------------- | --------------------------------------------------- |
| $A^*$       | Grade involution (involute)                                         | Complex conjugate                                   |
| $A^\dagger$ | Reverse (reversion)                                                 | Hermitian conjugate                                 |
| $A \cdot B$ | Hestenes inner product ($= \langle AB \rangle_{\lvert r-s \rvert}$) | Scalar product ($= \langle AB \rangle_0$)           |
| $[A, B]$    | Commutator $AB - BA$ (galaga)                                       | Often $\frac{1}{2}(AB - BA)$ (Chisolm, Lie bracket) |
| $I$         | Unit pseudoscalar                                                   | Imaginary unit (physics)                            |

### Note on the commutator ½ factor

The commutator $[A, B]$ has a GA-specific convention that differs from both mathematics and physics:

| Community                               | $[A,B]$ means          | Name                     |
| --------------------------------------- | ---------------------- | ------------------------ |
| Mathematics                             | $AB - BA$              | Commutator / Lie bracket |
| Physics                                 | $AB - BA$              | Commutator               |
| GA (Hestenes, Chisolm, Doran & Lasenby) | $\frac{1}{2}(AB - BA)$ | Commutator product       |

The $\frac{1}{2}$ is a GA invention. Hestenes introduced it because it makes the three-way product decomposition work cleanly:

$$AB = A \cdot B + A \times B + A \wedge B$$

where $A \times B = \frac{1}{2}(AB - BA)$ is the "commutator product." Without the $\frac{1}{2}$, this identity would need an explicit factor.

galaga reflects this split: `commutator(A, B)` computes $AB - BA$ (maths/physics convention), while `lie_bracket(A, B)` computes $\frac{1}{2}(AB - BA)$ (GA convention). The name `lie_bracket` for the $\frac{1}{2}$ version is slightly ironic — mathematicians' Lie bracket on an associative algebra is $AB - BA$ without the $\frac{1}{2}$ — but it matches Chisolm's notation, which is what the reference test suite uses.

### galaga API mapping

| Mathematical notation                            | galaga function           |
| ------------------------------------------------ | ------------------------- |
| $\tilde{A}$ (reverse)                            | `reverse(A)`              |
| $\hat{A}$ (grade involution)                     | `involute(A)`             |
| $\bar{A}$ (Clifford conjugate)                   | `conjugate(A)`            |
| $\langle A \rangle_k$                            | `grade(A, k)`             |
| $A \lrcorner B$ (left contraction)               | `left_contraction(A, B)`  |
| $A \llcorner B$ (right contraction)              | `right_contraction(A, B)` |
| $A \wedge B$ (outer product)                     | `op(A, B)`                |
| $AB$ (geometric product)                         | `gp(A, B)`                |
| $AB - BA$ (commutator)                           | `commutator(A, B)`        |
| $\frac{1}{2}(AB - BA)$ (commutator product)      | `lie_bracket(A, B)`       |
| $\langle A^\dagger B \rangle_0$ (scalar product) | `scalar_product(A, B)`    |
| $A^\dagger A$ (norm squared)                     | `norm2(A)`                |
| $\exp(B)$                                        | `exp(B)`                  |
| $\log(R)$                                        | `log(R)`                  |
| $RAR^{-1}$ or $RA\tilde{R}$ (sandwich)           | `sandwich(R, A)`          |
