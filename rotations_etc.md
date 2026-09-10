> **Historical teaching conversation.** The current distinctions, including
> the limits of scalar-square intuition, are in
> [rotors, generators and spinors](docs/rotors-generators-spinors.md).
> This transcript is not an API or release checklist.

So vectors create bivectors. And bivectors are generators of rotors. And rotors apply rotations to objects via the sandwhich product.

Yes — that chain is essentially right. The nice thing is that **each step is doing something very specific geometrically**, not just algebraically.

Let’s tighten it slightly and make the roles really crisp.

------

## 1) Vectors → Bivectors (planes)

- Given two vectors $a, b$, the **outer product**
  $$
  B = a \wedge b
  $$
  produces a **bivector**.

- Geometrically:

  - It represents an **oriented plane segment**
  - Magnitude = area
  - Direction = the plane itself (not a normal vector!)

👉 Key idea:
 A bivector is not “two vectors glued together” — it is a **primitive object representing a plane with orientation**.

------

## 2) Bivectors → generators of rotations

A bivector $B$ defines **a plane of rotation**.

Then the exponential:
$$
R = e^{-\frac{\theta}{2} B}
$$

- This is a **rotor**
- It encodes a rotation of angle $\theta$ **in the plane $B$**

👉 Why bivectors?

Because rotations *happen in planes*, not around axes.

- The “axis” picture (cross product) is a 3D convenience
- The fundamental object is the **plane of rotation**

------

## 3) Rotors → act via sandwich product

To rotate a vector $v$:
$$
v' = R \, v \, \tilde{R}
$$

- $R$ = rotor
- $\tilde{R}$ = reverse (inverse for unit rotors)

This is **conjugation**.

👉 Important:

- This is not just “apply a matrix”
- It is a **coordinate-free geometric action**

------

## 4) What’s really happening under the hood

This chain:

> vectors → bivectors → rotors → sandwich

can be understood as:

| Level | Object    | Meaning                     |
| ----- | --------- | --------------------------- |
| 1     | vectors   | directions                  |
| 2     | bivectors | planes (rotation domains)   |
| 3     | rotors    | finite rotations            |
| 4     | sandwich  | applying the transformation |

------

## 5) Subtle corrections (worth knowing)

A few precise refinements:

### (a) “Vectors create bivectors”

✔ True, but:

- Not all bivectors come from a single wedge in higher dimensions
- But **every bivector is a sum of simple bivectors**

------

### (b) “Bivectors generate rotors”

✔ Exactly right — but more specifically:

- They are **Lie algebra elements**
- Rotors live in the **even subalgebra (Spin group)**

Analogy:

- bivectors ↔ $\mathfrak{so}(n)$
- rotors ↔ $\mathrm{Spin}(n)$

------

### (c) The sandwich product is deeper than it looks

It’s doing two reflections:
$$
R = ab \quad \Rightarrow \quad v' = (ab)v(ba)
$$
So:

👉 **Rotation = composition of reflections**

This is *the* core geometric insight.

------

## 6) The “mental model” that works best

If you compress everything down:

> **Vectors live in space
>  Bivectors describe planes in space
>  Rotors rotate within those planes
>  The sandwich applies that rotation**

------

## 7) One-liner version

If you want a very tight formulation:

> **Rotations are exponentials of planes, applied by conjugation.**

------

If you want, next step we can:

- map this directly to **Pauli matrices / SU(2)** (your earlier thread), or
- show how this extends cleanly to **translations → motors (CGA/PGA)**, which fixes the “translate → rotate → translate back” issue you hit earlier.

What is precise terminology for all those steps, objects, actions.

Good instinct — there *is* a precise vocabulary for each step, and using it consistently clears up a lot of confusion (especially around “rotation”, “generator”, etc.).

I’ll give you a clean, canonical naming stack, then a tighter “type system” view.

------

# The precise terminology

## 1) Vectors → bivectors

**Objects**

- **Vector**: grade-1 element
- **Bivector**: grade-2 element

**Operation**

- **Outer product** (aka **wedge product**):
  $$
  B = a \wedge b
  $$

**Meaning**

- Produces a **simple bivector** (a *blade*)
- Represents an **oriented 2D subspace**

**Correct terms**

- “bivector”
- “2-blade”
- “simple bivector” (if decomposable as $a \wedge b$)

------

## 2) Bivectors → generators

This is where people get sloppy — this step has *very specific* terminology.

**Object**

- **Bivector (as a generator)**

**Precise term**

- **Infinitesimal generator of rotations**
- or:
  - **Lie algebra element**
  - specifically: element of $\mathfrak{so}(n)$

**Key idea**

- A bivector defines:

  > a **plane of rotation** + an **infinitesimal rotation operator**

------

## 3) Exponentiation → rotor

**Operation**

- **Exponential map**
  $$
  R = e^{-\frac{\theta}{2} B}
  $$

**Object**

- **Rotor**

**Precise classification**

- **Even multivector**
- **Unit rotor**
- **Spin element**

**Group name**

- Rotors form:
  - **Spin group**: $\mathrm{Spin}(n)$

------

## 4) Rotor action

**Operation**

- **Sandwich product**
  $$
  v' = R v \tilde{R}
  $$

**Precise names**

- **Conjugation**
- **Versor action**
- **Adjoint action** (in Lie theory language)

------

## 5) Underlying structure (often unstated)

**Rotor construction**

- A rotor is a:
  - **versor** (product of invertible vectors)

**Deeper fact**

- Any rotation = **composition of reflections**

So:

- vectors → reflections
- versors → compositions of reflections
- rotors → even versors (pure rotations)

------

# Clean terminology chain (canonical form)

Here’s the precise version of your sentence:

> **Vectors generate bivectors via the outer product;
>  bivectors act as infinitesimal generators of rotations;
>  their exponential gives rotors (elements of Spin(n));
>  rotors act on multivectors via conjugation (the sandwich product).**

------

# A more “type-theoretic” view (useful for API design)

This matches very well to how you’re thinking about your library.

| Layer       | Type       | Role           | Operation     |
| ----------- | ---------- | -------------- | ------------- |
| Geometry    | Vector     | direction      | —             |
| Subspace    | Bivector   | plane          | outer product |
| Lie algebra | Bivector   | generator      | commutator    |
| Lie group   | Rotor      | transformation | exponential   |
| Action      | Rotor × MV | transformation | sandwich      |

------

# Subtle but important distinctions

## 1) “Bivector” vs “generator”

Not every bivector is *used* as a generator, but:

- Every bivector **can be interpreted** as one

So:

- “bivector” → geometric object
- “generator” → functional role

------

## 2) “Rotor” vs “rotation”

These are not the same thing:

- **Rotor** = algebraic object
- **Rotation** = geometric transformation

Two rotors $R$ and $-R$ represent the same rotation.

------

## 3) “Sandwich product” vs “conjugation”

Same operation, different emphasis:

- **Sandwich product** → GA terminology
- **Conjugation / adjoint action** → algebra / Lie theory

------

## 4) “Blade” vs “basis blade”

- **Blade** = wedge of independent vectors
- **Basis blade** = canonical basis element (e.g. $e_1 \wedge e_2$)

------

# Minimal “correct vocabulary” set

If you want a tight, disciplined naming scheme (good for your library):

- `vector`
- `bivector`
- `blade`
- `outer_product`
- `generator`
- `exponential`
- `rotor`
- `reverse`
- `conjugation` (or `sandwich`)
- `versor`

------

# Ultra-compact version

If you compress everything:

> **Bivectors are Lie algebra elements;
>  rotors are their exponentials;
>  rotation is implemented via conjugation.**

------

# One last refinement (important for your mental model)

The *real* hierarchy is:

```
Vectors → reflections
Reflections → versors
Even versors → rotors
Rotors → rotations (via conjugation)
```

Your version is correct, but this one is **more fundamental**.

------

If you want next, we can:

- map each of these directly to **SU(2), Pauli matrices, and QM objects**, or
- turn this into a **clean API naming scheme** for your library (this maps *very* nicely to what you're building).

"They are Lie algebra elements" yes, so what does that mean

Good — this is the point where the words can either stay abstract or suddenly “click”.

Let’s make **“bivectors are Lie algebra elements”** precise in a way that’s actually useful (especially for your library).

------

# 1) What a Lie algebra *is* (in concrete terms)

A **Lie algebra** is:

- A vector space (you can add and scale things)
- Equipped with a special product: the **Lie bracket**

$$
[X, Y]
$$

that satisfies:

- antisymmetry: $[X,Y] = -[Y,X]$
- Jacobi identity

👉 That’s it. No exponentials yet, no groups — just:

> **“things you can add, plus a bracket that tells you how they interact.”**

------

# 2) In geometric algebra: what is the Lie algebra?

In GA, the Lie algebra of rotations is:

> **the space of bivectors, with the commutator**

$$
[B_1, B_2] = B_1 B_2 - B_2 B_1
$$

(you can include the $\tfrac{1}{2}$ or not — just convention)

------

# 3) What the bracket *means* geometrically

This is the key insight:

> The commutator measures how two infinitesimal rotations fail to commute.

If:

- $B_1$ = rotation in plane 1
- $B_2$ = rotation in plane 2

then:
$$
[B_1, B_2]
$$
is:
 👉 the **new infinitesimal rotation you get from doing them in different orders**

------

## Concrete example (Cl(3,0))

Let:

- $B_1 = e_1 \wedge e_2$
- $B_2 = e_2 \wedge e_3$

Then:
$$
[B_1, B_2] \propto e_1 \wedge e_3
$$
👉 Interpretation:

- rotating in XY, then YZ ≠ YZ then XY
- the mismatch is a rotation in XZ

This is exactly the structure of $\mathfrak{so}(3)$

------

# 4) Why bivectors are the Lie algebra

Because they satisfy:

### (a) Closed under commutator

- commutator of two bivectors is another bivector

### (b) Linear space

- sums of bivectors are still bivectors

### (c) They encode infinitesimal rotations

------

# 5) “Infinitesimal generator” — what that actually means

Take a small rotation:
$$
R \approx 1 - \frac{\epsilon}{2} B
$$
Apply it:
$$
v' = R v \tilde{R}
$$
Expand to first order:
$$
v' \approx v + \epsilon (B \cdot v)
$$
👉 So:

> **B tells you how the vector starts to move under rotation**

That’s what “generator” means:

- It gives the **direction of change**
- It is the **derivative of the transformation**

------

# 6) From Lie algebra → Lie group

Now the key bridge:

- **Lie algebra (bivectors)** = infinitesimal rotations
- **Lie group (rotors)** = finite rotations

Connected by:
$$
R = e^{-\frac{\theta}{2} B}
$$
👉 So when you say:

> “bivectors are Lie algebra elements”

you are saying:

> **they are the things you exponentiate to get rotations**

------

# 7) Why this matters (not just terminology)

This gives you:

### Structure

- rotations form a group (Spin(n))
- bivectors form its tangent space at identity

### Computation

- interpolation (slerp) uses exponentials/logs
- composition uses group multiplication

### API design insight (very relevant for you)

You actually have two distinct types:

- **Generator type** (bivector)
- **Transformation type** (rotor)

That’s a *real* distinction, not just naming.

------

# 8) Clean mental model

Here’s the most useful way to think about it:

> **Bivectors are velocities of rotation
>  Rotors are positions after integrating that velocity**

------

# 9) One-line summary

> **A bivector is a Lie algebra element because it describes an infinitesimal rotation, and the commutator of bivectors captures how rotations interact.**

------

# 10) If you want to push it one level deeper

We can go further into:

- why the commutator = cross product in 3D
- how this maps exactly to **Pauli matrices / su(2)**
- or how to encode this cleanly in your library (e.g. `.exp()`, `.log()`, generator vs rotor types)

That next step is where it really becomes *usable*, not just understood.
