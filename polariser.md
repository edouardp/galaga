Can we use a geometric algebra library to do things like polarisation equations (H blocks V, but adding a 45 degree one between them let light through)? https://github.com/edouardp/ga/tree/symbolic_redesign being the lib I'd use

Yes — absolutely, at least at the level of **ideal polarization optics**.

A geometric algebra library is a very natural fit for this, because an ideal linear polarizer is basically a **projection** onto a direction in the transverse plane, and projection is one of the things GA expresses very cleanly. Your branch already has a symbolic expression tree sitting on top of a numeric core, with lazy operator-built trees and `eval()` for concrete multivector results, so it is a reasonable base for this kind of work. 

The key distinction is this:

- **Waveplates / rotations** are naturally modeled by **rotors**.
- **Polarizers** are **not** rotors, because they are not invertible rotations; they **discard** part of the field.

So for the “H blocks V, but H then 45° then V lets some through” story, the right GA object is mainly a **projector**, not a rotor.

## Minimal GA picture

Work in the 2D transverse plane with orthonormal basis $e_1, e_2$:

- $e_1$ = horizontal polarization
- $e_2$ = vertical polarization

Let a unit polarization axis be $a$. Then the ideal linear polarizer along $a$ maps a field vector $E$ to:
$$
P_a(E) = (E \cdot a)\,a
$$
That is just “keep the component of $E$ along $a$, throw away the rest”.

In GA form, the same projector can also be written as:
$$
P_a(E) = \frac{1}{2}(E + aEa)
$$
because $aEa$ is reflection in the axis $a$, and averaging the vector with its reflection leaves only the component parallel to $a$.

That already gives you Malus’ law:
$$
|P_a(E)|^2 = |E|^2 \cos^2\theta
$$
where $\theta$ is the angle between $E$ and $a$.

## The classic three-polarizer result

Let

- $H = e_1$
- $V = e_2$
- $D = \frac{e_1 + e_2}{\sqrt{2}}$  (45°)

Start with horizontally polarized light after the first polarizer:
$$
E_0 = e_1
$$
Now apply the 45° polarizer:
$$
E_1 = P_D(E_0)
= (e_1 \cdot D)D
= \frac{1}{\sqrt{2}}D
$$
Then apply the vertical polarizer:
$$
E_2 = P_V(E_1)
= \left(\frac{1}{\sqrt{2}}D \cdot e_2\right)e_2
= \frac{1}{2}e_2
$$
So the **field amplitude** is reduced by $1/2$, and the **intensity** is reduced by $1/4$ relative to the light *after the first H polarizer*. That is exactly the usual result.

Without the 45° polarizer:
$$
P_V(P_H(E)) = 0
$$
for a horizontally polarized field entering a vertical polarizer.

## Why GA is nice here

Jones calculus usually writes this with $2\times2$ matrices. GA lets you keep it geometric:

- polarization states as vectors in a plane
- polarizers as projectors
- waveplates as rotors
- intensity as squared magnitude

That is conceptually cleaner than starting with matrices unless you specifically need the standard optics formalism.

## Where your library seems suitable

Your symbolic layer is explicitly designed to build lazy trees for GA operations, pretty-print them, and then `eval()` them back to concrete multivectors. It also wraps the numeric core so the same API can be used for symbolic and numeric work. 

So this kind of workflow should fit the direction of the library well:

- define basis vectors
- define a polarization direction $a$
- define `project(E, a)`
- optionally keep the composed optical chain symbolic
- evaluate at the end

## Likely shape of the code

I have not verified the exact final public API on that branch for every helper name, so treat this as the intended pattern rather than guaranteed copy-paste code.

```
from math import sqrt
from ga import Algebra

alg = Algebra((1, 1))   # transverse plane
e1, e2 = alg.blades     # or basis_vectors(), depending on final API

def project(E, a):
    # assumes a is unit length
    return (E | a) * a   # or dot(E, a) * a depending on operator choices

H = e1
V = e2
D = (e1 + e2) / sqrt(2)

E0 = H
E1 = project(E0, D)
E2 = project(E1, V)

print(E2)
```

If you want the “reflection average” form instead:

```
def project(E, a):
    return 0.5 * (E + a * E * a)
```

That is very GA-native.

## What else you could model

This approach extends nicely to:

- **Malus’ law**
- **chains of ideal polarizers**
- **waveplates / retarders** via rotor-like phase operations
- **symbolic derivations** of transmission expressions

## Where it gets trickier

If you want full real optics rather than simple classroom polarization:

- complex phase between components
- circular / elliptical polarization
- birefringence
- partial polarization
- Mueller/Stokes style depolarizing systems

then you need either:

- a complexified GA treatment,
- a spacetime/Pauli-style even subalgebra treatment,
- or a hybrid approach that intentionally mirrors Jones/Mueller calculus.

Still doable, but more design work.

## Bottom line

Yes: for the specific “H, then 45°, then V” effect, a GA library is not just usable — it is a very good fit.

The main modeling choice is:

- **polarizer = projector**
- **waveplate/rotation = rotor**

and your `symbolic_redesign` branch looks like a good foundation for expressing those chains symbolically and evaluating them numerically. 