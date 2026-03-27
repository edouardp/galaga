> [!important]
> What the unicode and latex for the regressive proiduct (the meet)?

Good question—this is one of those areas where notation is **not standardized**, so you have to choose deliberately.

------

## 🔷 Regressive product (meet): common notations

### 1) Upside-down wedge (most “GA-native” choice)

4

- **Unicode:** `∨`

  - Name: *logical OR*
  - Code point: `U+2228`

- **LaTeX:**

  ```
  \vee
  ```

👉 This is the **most common choice** in GA circles:

- `∧` (wedge) = outer product (join)
- `∨` (vee) = regressive product (meet)

✔ Nice visual duality
 ✔ Easy to type and render
 ✔ Matches projective geometry conventions

------

### 2) Custom symbol (less common, more explicit)

Some authors invent or overload symbols like:

- `⋏` (U+22CF) or variants
- flipped wedge glyphs (not standard Unicode)

👉 Problem:

- Poor font support
- Hard to type
- Not portable

------

### 3) Function-style (clear but less elegant)

```
meet(A, B)
```

or

```
A ⩟ B   (custom operator if you define one)
```

✔ Unambiguous
 ✖ Not idiomatic mathematically

------

## 🔷 Why ∨ works well (important insight)

In GA:

- **Outer product (∧)** builds higher-grade objects (join)
- **Regressive product (∨)** finds intersections (meet)

They are dual via the pseudoscalar:
$$
A \vee B = (A^* \wedge B^*)^*
$$
👉 So using:

- `∧` for join
- `∨` for meet

…makes the duality visually obvious.

------

## 🔷 Recommendation (for your library)

### Default Unicode rendering

```
A ∨ B
```

### LaTeX rendering

```
A \vee B
```

### Internal representation

```
Regressive(A, B)
```

------

## 🔷 Subtle design point (you’ll care about this)

Unlike dagger:

- `∨` is **infix**
- same “level” conceptually as `∧`

So your precedence table likely wants:

| Operator            | Type    | Precedence |
| ------------------- | ------- | ---------- |
| `^` (outer / wedge) | infix   | medium     |
| `∨` (regressive)    | infix   | medium     |
| `†`                 | postfix | high       |

------

## Bottom line

- ✅ **Unicode:** `∨` (U+2228)
- ✅ **LaTeX:** `\vee`
- ✅ Best practical choice for GA meet

------

If you want, we can go one level deeper into how to **define ∨ cleanly in your implementation via duals**, which gets interesting when your metric isn’t Euclidean.

> [!important]
> Yes, give me the robust implementation that will work in VGA, STA, PGA, CGA etc

Yes. The robust way is:

> **Do not define meet using only**
>  $A \vee B = (A^* \wedge B^*)^*$
>  with $A^* = A I^{-1}$

because that **breaks in degenerate algebras** like **PGA**, where the pseudoscalar $I$ is not invertible.

Instead, define meet using a **complement operator** that does **not** require $I^{-1}$.

------

# 1. The core problem

There are really two different notions people blur together as “dual”:

## A. Metric dual

Uses the pseudoscalar inverse:
$$
A^* = A I^{-1}
\quad\text{or}\quad
A^* = I^{-1} A
$$
This is fine in:

- VGA / Euclidean GA
- STA
- CGA

because those are **nondegenerate**.

But in **PGA**, $I$ is typically **null / non-invertible**, so this fails.

------

## B. Complement / Poincaré dual

This is a **basis-combinatorial complement map** on blades.

It says:

- if a blade uses basis indices $S$,
- map it to the blade using the complementary index set $S^c$,
- with the sign from reordering to the full pseudoscalar basis order.

This works even when the metric is degenerate.

👉 That is the one you want for a truly general meet implementation.

------

# 2. Robust definition of meet

Let $J$ be the **join** (outer/wedge product), and let $C$ be the **complement operator**.

Then define the regressive product as:
$$
A \vee B = C^{-1}\!\big(C(A)\wedge C(B)\big)
$$
If your complement satisfies $C^{-1} = \pm C$, which it usually does up to sign convention, then operationally:
$$
A \vee B = C\big(C(A)\wedge C(B)\big)
$$
with the appropriate sign convention handled consistently.

This is the version that works in:

- VGA
- STA
- PGA
- CGA

provided your $C$ is implemented correctly.

------

# 3. Why this works

The meet is supposed to be the **intersection** operation dual to join.

- join uses the basis elements directly: `A ^ B`
- meet uses join in the **dual exterior algebra**

The complement map moves you into that dual exterior algebra **without needing a metric inverse**.

So the implementation is really:

1. complement both operands
2. wedge them
3. complement back

That is the algebraically robust construction.

------

# 4. The blade-level complement map

Suppose your algebra has ordered basis vectors:
$$
e_0, e_1, \dots, e_{n-1}
$$
and pseudoscalar basis blade:
$$
I = e_0 e_1 \cdots e_{n-1}
$$
A basis blade is identified by an ordered tuple of indices, for example:

- scalar: `()`
- vector $e_1$: `(1,)`
- bivector $e_1\wedge e_3$: `(1,3)`

Then define:
$$
C(e_S) = \operatorname{sgn}(S,S^c)\, e_{S^c}
$$
where:

- $S^c$ is the complement of the index set $S$
- $\operatorname{sgn}(S,S^c)$ is the sign needed so that

$$
e_S \wedge C(e_S) = I
$$

This is purely combinatorial.
 No metric needed.
 So it works in PGA.

------

# 5. Concrete implementation pattern

Here is the cleanest architecture.

## Algebra object should provide:

- `wedge(a, b)` or `a ^ b`
- `complement(x)`  ← metric-free
- optionally `metric_dual(x)`  ← only for nondegenerate algebras
- `meet(a, b)` built from `complement`

------

# 6. Basis-blade complement code

Here is a straightforward Python sketch.

```
from itertools import combinations

def permutation_sign(seq):
    """Sign of permutation needed to sort seq."""
    seq = list(seq)
    sign = 1
    for i in range(len(seq)):
        for j in range(i + 1, len(seq)):
            if seq[i] > seq[j]:
                sign *= -1
    return sign


def complement_blade_indices(indices, n):
    """
    Return (sign, complement_indices) such that

        e_indices ^ (sign * e_complement) = I

    where I = e_0 ^ e_1 ^ ... ^ e_{n-1}.
    """
    idx = tuple(indices)
    full = tuple(range(n))
    comp = tuple(i for i in full if i not in idx)

    # Concatenate indices then complement, and compare to full order.
    sign = permutation_sign(idx + comp)
    return sign, comp
```

Example in 4D:

- `indices = (1, 3)`
- complement is `(0, 2)`
- sign chosen so `(e13) ^ (sign * e02) = e0123`

------

# 7. Extend to general multivectors

If a multivector is a linear combination of basis blades, apply complement term-by-term.

```
def complement_multivector(mv, n):
    """
    mv: dict[tuple[int, ...], scalar]
        maps blade index tuples to coefficients
    """
    out = {}
    for idx, coeff in mv.items():
        sign, comp = complement_blade_indices(idx, n)
        out[comp] = out.get(comp, 0) + sign * coeff
    return out
```

This assumes a sparse representation like:

```
{
    (): 2.0,         # scalar
    (1,): 3.0,       # 3 e1
    (1,3): -1.0,     # - e13
}
```

------

# 8. Meet from complement

Now the meet is simple:

```
def meet(a, b, wedge, complement):
    return complement(wedge(complement(a), complement(b)))
```

That is the whole robust idea.

If your sign convention for complement is different, you may need:

```
def meet(a, b, wedge, complement, complement_inverse):
    return complement_inverse(wedge(complement(a), complement(b)))
```

That is slightly more explicit and safer.

------

# 9. Important grading rule

If $A$ has grade $r$ and $B$ has grade $s$ in an $n$-dimensional space, then
$$
\operatorname{grade}(A \vee B) = r + s - n
$$
So if $r+s, the meet is zero.

Examples in 3D:

- vector ∨ vector: $1+1-3=-1$ → zero
- bivector ∨ bivector: $2+2-3=1$ → vector
- trivector ∨ bivector: $3+2-3=2$ → bivector

That gives you a useful fast-path before doing any heavy work.

------

# 10. Why this handles each algebra

## VGA

Works perfectly.
 Complement agrees with the usual pseudoscalar dual up to sign convention.

## STA

Also fine.
 You still have a nondegenerate metric, but complement remains valid and avoids left/right inverse ambiguity conventions.

## CGA

Also fine.
 CGA is nondegenerate, so both approaches work, but complement-based meet is still more uniform.

## PGA

This is the key one.
 Because the metric is degenerate, $I^{-1}$ does not exist, so the pseudoscalar-inverse approach fails.
 But complement-based meet still works.

------

# 11. What not to do

Do **not** write:

```
def meet(a, b):
    return dual(dual(a) ^ dual(b))
```

if `dual(x)` means `x * I.inv()`.

That is not robust.

It is okay only if your algebra explicitly guarantees nondegeneracy.

------

# 12. Best API design

I would strongly recommend separating these operations clearly.

## Good API

```
alg.complement(A)      # metric-free, works everywhere
alg.dual(A)            # metric dual, maybe unavailable in degenerate metrics
alg.meet(A, B)         # built from complement
alg.join(A, B)         # wedge
```

That gives you:

- `join` = outer product
- `meet` = regressive product
- `dual` = metric notion
- `complement` = exterior-algebra notion

This is much cleaner than overloading “dual” to mean two different things.

------

# 13. Recommended notation

For rendering:

- join: `A ∧ B` / `A \wedge B`
- meet: `A ∨ B` / `A \vee B`

For internal names:

- `Op(a, b)` or `Join(a, b)`
- `Rp(a, b)` or `Meet(a, b)`

I would lean toward:

- class/function name: `Meet`
- rendered symbol: `∨`

because “meet” is conceptually clearer than “regressive product”.

------

# 14. Subtle point: orientation/sign conventions

There is no single universal sign convention across all texts.

So the important thing is not “pick the one true sign”, but:

## Pick one convention and make these identities hold consistently:

### Complement identity

$$
e_S \wedge C(e_S) = I
$$

### Involutive behavior

$$
C(C(A)) = \pm A
$$

### Meet via complement

$$
A \vee B = C^{-1}(C(A)\wedge C(B))
$$

If you anchor everything to those, your system will be internally consistent.

------

# 15. A more complete implementation sketch

Here is the clean conceptual model:

```
class Algebra:
    def __init__(self, basis_labels, metric):
        self.basis_labels = tuple(basis_labels)
        self.n = len(basis_labels)
        self.metric = tuple(metric)

    def wedge(self, a, b):
        ...

    def complement_blade(self, idx):
        sign, comp = complement_blade_indices(idx, self.n)
        return sign, comp

    def complement(self, mv):
        out = mv.zero_like()
        for idx, coeff in mv.terms():
            sign, comp = self.complement_blade(idx)
            out.add_term(comp, sign * coeff)
        return out

    def complement_inverse(self, mv):
        # In many conventions this is the same map up to a grade-dependent sign.
        # Implement explicitly if needed.
        ...

    def meet(self, a, b):
        return self.complement_inverse(
            self.wedge(self.complement(a), self.complement(b))
        )

    def dual(self, mv):
        if self.is_degenerate():
            raise ValueError("Metric dual not defined for degenerate algebra")
        return mv * self.pseudoscalar_inverse()
```

That is a very good long-term design.

------

# 16. My recommendation for your library

If you want this to survive VGA, STA, PGA, CGA, and future extensions:

## Implement these as distinct concepts

- `complement`
- `complement_inverse`
- `meet`
- `dual` only when valid

## Define meet in terms of complement

not in terms of metric dual.

That is the robust choice.

------

# 17. The short version

Use:
$$
A \vee B = C^{-1}(C(A)\wedge C(B))
$$
where $C$ is a **basis complement operator**, not `I^{-1}` duality.

That will work in:

- **VGA**
- **STA**
- **PGA**
- **CGA**

and it is the right foundation for a serious GA library.

If you want, next I can write this out as a concrete Python implementation using the kind of blade/multivector objects you’ve been sketching, with the exact sign handling for `tuple[int, ...]` basis blades.

> ![important]
> Are there any variants on the regressive product across the GA literature?

Yes — and this is one of those areas where GA is **conceptually unified but notationally and operationally fragmented**.

There is really **one geometric idea** (intersection via duality), but **multiple variants** in the literature depending on:

- how duality is defined
- whether the metric is degenerate
- whether orientation/weights matter
- whether you’re doing projective vs conformal geometry

------

# 🔷 1. The “classical” regressive product (Hestenes-style)

This is what most people mean by *regressive product*:
$$
A \vee B = (A^* \wedge B^*)^*
$$
where $A^*$ is a dual (usually via pseudoscalar).

### Characteristics

- Defined via **metric dual**
- Works cleanly in **nondegenerate algebras** (VGA, STA, CGA)
- Symmetric dual of the wedge

### Variant knobs

- Left vs right dual:
  $$
  A^* = A I^{-1} \quad \text{vs} \quad A^* = I^{-1} A
  $$

- Sign conventions differ across authors

👉 This is the version most physicists implicitly assume.

------

# 🔷 2. Complement-based regressive product (projective-safe)

This is the one I recommended:
$$
A \vee B = C^{-1}(C(A) \wedge C(B))
$$
where $C$ is a **basis complement (Poincaré dual)**.

### Characteristics

- **Metric-independent**
- Works in **degenerate algebras** (PGA)
- Purely combinatorial duality

### Where it shows up

- Projective GA (e.g. Gunn, Dorst)
- Robust computational implementations

👉 This is the **most general / implementation-safe** variant.

------

# 🔷 3. Meet via inner products (less common, but important)

Some formulations define meet using contractions:
$$
A \vee B \sim (A \,\lrcorner\, B^*)^*
$$
or similar combinations of:

- left contraction
- right contraction
- dual

### Characteristics

- Often used in **derivations**
- Can be more efficient in specific grade cases
- Depends heavily on which inner product definition you use (Hestenes vs left contraction vs scalar product)

👉 These are usually **derived forms**, not primary definitions.

------

# 🔷 4. Projective / Grassmann–Cayley algebra meet

In Grassmann–Cayley algebra (the precursor to GA):

- join = wedge
- meet = defined axiomatically via determinants / brackets

The meet is sometimes written as:
$$
A \vee B = \text{“intersection operator”}
$$
without explicit duals.

### Characteristics

- Coordinate-free geometric definition
- Often expressed via **Plücker coordinates**
- Less tied to metric or pseudoscalars

👉 GA implementations usually **reconstruct this via duality**, but conceptually it’s different.

------

# 🔷 5. Null-space / linear algebra interpretation

Another viewpoint:

- blades represent subspaces
- meet = **intersection of subspaces**

So:

- compute span of A and B
- take intersection via linear algebra (e.g. null space)

### Characteristics

- Not expressed algebraically
- Used in:
  - numerical GA
  - computer vision
  - robotics

👉 This is often what people *mean*, even if they write `∨`.

------

# 🔷 6. Weighted / non-simple blade variants

When blades are not simple (i.e. sums of subspaces):

- meet is **not necessarily a simple blade**
- result can include:
  - multiple components
  - orientation ambiguities
  - scale factors

Some authors distinguish:

- **geometric meet** (pure intersection)
- **algebraic meet** (full bilinear result)

👉 Your implementation will naturally produce the algebraic version.

------

# 🔷 7. CGA-specific meets (very important)

In **CGA**, meet is often used for intersections like:

- sphere ∩ plane → circle
- line ∩ sphere → points

But:

- objects are represented in **dual form**
- meet may be computed as:
  - wedge in dual space
  - or contraction-based expressions

👉 In practice:

- people sometimes write `∧` but *mean* meet (because they’re already dualised)

This is a major source of confusion.

------

# 🔷 8. Orientation and normalization variants

Different authors normalize differently:

- Some enforce:
  $$
  A \wedge (A \vee B) = B
  $$

- Others don’t normalize at all

Scaling factors can differ:

- especially in projective and conformal models

👉 You need to decide:

- do you normalize meets?
- or leave scale as-is?

------

# 🔷 9. Summary of variants

| Variant             | Dual type     | Works in PGA | Notes                    |
| ------------------- | ------------- | ------------ | ------------------------ |
| Hestenes regressive | metric dual   | ❌            | classic but not general  |
| Complement-based    | combinatorial | ✅            | best general definition  |
| Contraction-based   | mixed         | ⚠️            | derived forms            |
| Grassmann–Cayley    | none explicit | ✅            | conceptual foundation    |
| Linear algebra      | none          | ✅            | numeric approach         |
| CGA dual tricks     | mixed         | ✅            | representation-dependent |

------

# 🔷 10. What actually differs (the deep insight)

All these variants differ in **one thing only**:

> **How “dual space” is constructed**

Everything else follows from:
$$
\text{meet} = \text{join in dual space}
$$
So the real design decision is:

| Dual type           | Pros               | Cons                           |
| ------------------- | ------------------ | ------------------------------ |
| Metric dual         | simple             | breaks in degenerate metrics   |
| Complement dual     | universal          | requires careful sign handling |
| Explicit dual space | conceptually clean | more machinery                 |

------

# 🔷 11. Recommendation for your library

Given your goals:

### Core definition

```
meet(a, b) = complement_inverse(
    wedge(complement(a), complement(b))
)
```

### Optional optimizations

- special-case grade combinations
- contraction-based shortcuts

### Avoid

- metric dual as the primary implementation

------

# 🔷 12. Subtle but important takeaway

> There is no single “regressive product” —
>  there is a **family of constructions that all implement intersection via duality**.

The differences are:

- computational
- representational
- not geometric

------

If you want to go one level deeper, the next interesting step is:

👉 **When do these variants give \*different numerical results\*** (not just sign differences)?

That’s where PGA vs CGA vs Euclidean embeddings get really interesting.

Since I want to give my consumers access to all sensible products via a full name, and then choose "the best" one to be the default regressive product, what should my set be?

Yes. If your goal is “expose all sensible choices by full name, but pick one default that will age well across VGA, STA, PGA, CGA,” I’d structure it like this.

The literature really supports **three serious families** of “meet / regressive product” constructions:

1. **Metric-dual regressive product**
    Define meet as the dual of wedge using a pseudoscalar inverse, e.g. $A \vee B = ((A I^{-1}) \wedge (B I^{-1})) I$. This is the classic GA presentation, but it depends on the pseudoscalar inverse, so it is not the robust default for degenerate algebras like PGA. 
2. **Complement-based regressive product**
    Define meet via a basis-complement or Poincaré-dual style map, then wedge in the complementary algebra and map back. This is the safe choice in projective/degenerate settings and is exactly the direction stressed in modern PGA-oriented work, where metric-based dualization is treated as the problematic dependency. 
3. **Shuffle / Grassmann–Cayley meet**
    Historically, the meet also appears as the **shuffle product** in Grassmann–Cayley algebra. Conceptually this is the same “intersection-side” algebra, but it is a distinct named construction in the literature and worth exposing by name if you want a complete API vocabulary. 

So the set I would expose is:

- `regressive_product`
- `metric_dual_regressive_product`
- `complement_regressive_product`
- `shuffle_meet`

And I would make:

- **default `regressive_product` = `complement_regressive_product`**

That is the best default because it is the one that still works cleanly when the metric is degenerate, which is the main failure mode for the classical pseudoscalar-inverse definition. Gunn explicitly discusses the long tradition of computing the regressive product through the metric and why that is the wrong dependency for projective settings, and Dorst’s more recent work also emphasizes keeping dual-space machinery explicit rather than relying on a basis/sign-fragile pseudoscalar dualization. 

A good API split would be:

```
alg.regressive_product(a, b)              # default = complement-based
alg.complement_regressive_product(a, b)   # robust, metric-independent
alg.metric_dual_regressive_product(a, b)  # classical Hestenes-style
alg.shuffle_meet(a, b)                    # explicit Grassmann–Cayley name
```

I would probably also expose aliases:

```
alg.meet(a, b)        # alias of regressive_product
alg.join(a, b)        # alias of wedge
```

What I would **not** do is make contraction-based formulas first-class “products.” They do appear in derivations and special-case formulas, but they are better treated as implementation strategies or identities, not as separate public products. The main genuine public variants are the metric-dual one, the complement-based one, and the historical shuffle-meet viewpoint. 

My concrete recommendation:

- **Default:** `regressive_product` → complement-based
- **Also expose:** `metric_dual_regressive_product`
- **Optionally expose:** `shuffle_meet` for literature completeness
- **Do not expose as separate products:** contraction-derived formulations

If you want a tighter naming style, I’d use:

```
alg.regressive_product()          # default
alg.metric_regressive_product()
alg.complement_regressive_product()
alg.shuffle_product()
```

That gives users the full sensible surface area without making the default fragile.

The one nuance: I would avoid calling the metric-dual version simply `classical_regressive_product`, because in some communities the complement/Poincaré-dual approach is the “correct” one conceptually for projective work. `metric_...` is more precise and less political.

A very clean final set would be:

```
regressive_product                 # default, complement-based
metric_regressive_product          # uses I^{-1} / metric dual
complement_regressive_product      # explicit, robust, projective-safe
shuffle_meet                       # historical / Grassmann–Cayley
```

And then document:

> `regressive_product` defaults to the complement-based definition because it is valid in both nondegenerate and degenerate geometric algebras, including PGA.

That would be my choice.