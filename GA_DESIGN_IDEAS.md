> **Historical design conversation.** Proposals and API examples below are
> brainstorming, not the implemented Galaga 2 contract. Start with the
> [current documentation](docs/README.md) for supported operations and naming.

This is a copy of a conversation between ChatGPT & Anonymous.

Report conversation

How to implement a python GA library? mThe existing ones all seem to change release to release, and don't use programmer first approaches (like giving everything a definitive function name, and then implementing helpers to make the syntax terser - e.g. for dot product, etc)

I’d treat it as two separate problems:

1. **a stable algebra engine**
2. **a friendly programmer-facing API**

Most GA libraries blur those together, which is why releases feel unstable: internal representation changes leak straight into user code.

## Core design idea

Make the **semantic operations** permanent and boring.

That means the public API should expose names like:

- `gp(a, b)` for geometric product
- `op(a, b)` for outer product
- `ip(a, b, mode="hestenes" | "left" | "right" | "scalar")`
- `dot(a, b)` if you want a specific fixed meaning
- `reverse(x)`
- `involute(x)`
- `conjugate(x)`
- `dual(x)`
- `undual(x)`
- `grade(x, k)`
- `grades(x)`
- `scalar(x)`
- `norm(x)`
- `unit(x)`

Then you can add sugar later:

- `a * b` → geometric product
- `a ^ b` → outer product
- `a | b` → chosen inner product

But the named functions must be the real contract. Operator overloads are convenience only.

That single decision solves a lot of pain:

- scripts remain readable after syntax changes
- docs can be precise
- users do not have to remember what `|` means in this release
- you can preserve compatibility even if internals change completely

------

## Recommended architecture

### Layer 1: Metric + basis description

A `Layout` or `Algebra` object should define:

- dimension
- signature / metric
- basis blade ordering
- multiplication tables
- pseudoscalar
- duality rules
- grade masks

Example sketch:

```
alg = Algebra(signature=(1, 1, 1))      # Cl(3,0)
sta = Algebra(signature=(1, -1, -1, -1)) # Cl(1,3)
```

This object should be immutable after creation.

It owns all algebra-specific tables, so multivectors themselves stay lightweight.

------

### Layer 2: Multivector data structure

A `Multivector` should just be:

- a reference to its algebra
- coefficients in a canonical basis-blade order

For example:

```
class Multivector:
    __slots__ = ("algebra", "data")
```

Where `data` is maybe:

- a NumPy array of length `2^n`
- or sparse dict for bigger algebras

For small and medium algebras, dense is much simpler and usually worth it.

For Cl(3,0), Cl(1,3), PGA/CGA-sized use, dense is fine.

------

### Layer 3: primitive operations

Implement the boring, canonical primitives first.

Do **not** start with “nice notation”. Start with:

- blade-blade geometric product
- multivector-multivector geometric product
- grade projection
- reverse / involution / conjugation
- scalar extraction
- metric-aware norm-like helpers

Everything else is built from these.

For example:

```
def gp(a: Multivector, b: Multivector) -> Multivector: ...
def op(a: Multivector, b: Multivector) -> Multivector: ...
def left_contraction(a, b): ...
def right_contraction(a, b): ...
def hestenes_inner(a, b): ...
def scalar_product(a, b): ...
```

This is the “programmer first” part: every operation has one definitive implementation point and one definitive name.

------

## Biggest design mistake to avoid

Do **not** make “inner product” ambiguous.

This has caused endless confusion in GA libraries and books. Different communities mean different things by it.

Instead:

- `left_contraction(a, b)`
- `right_contraction(a, b)`
- `hestenes_inner(a, b)`
- `scalar_product(a, b)`

Then maybe:

```
def ip(a, b, mode="hestenes"):
    ...
```

But never make the user guess what `inner(a, b)` means.

Same goes for `norm`. You probably want several:

- `magnitude(x)`
- `quadratic_form(x)` or `x * reverse(x)` scalar part
- `study_norm(x)` for PGA/CGA style contexts
- `rotor_norm(x)`

Names should reflect meaning.

------

## Internal representation choices

### Option A: bitset blade representation

This is the best foundation.

Represent each basis blade by an integer bitmask.

In Cl(3,0):

- `1` → scalar `0b000`
- `e1` → `0b001`
- `e2` → `0b010`
- `e3` → `0b100`
- `e12` → `0b011`
- etc.

Benefits:

- wedge/grade structure becomes natural
- blade multiplication can be computed algorithmically
- no string parsing in core logic
- fast lookup tables possible

Then basis blade product is:

1. combine masks with XOR
2. compute sign from swaps needed to reorder
3. apply metric factors for repeated basis vectors

That gives you the blade-blade geometric product.

------

### Option B: dense array over all blades

Best for user-facing multivectors in low dimensions.

```
data.shape == (2 ** n,)
```

Simple, predictable, vectorizable.

### Option C: sparse dict

Useful for large dimensions or symbolic work, but I would not make it the primary representation for a first library. It complicates everything.

My recommendation:

- use **bitmasks for blade identity**
- use **dense NumPy arrays for coefficients**
- maybe add sparse later

------

## How the multiplication should work

Precompute a full multiplication table at algebra creation time.

For basis blades `i, j`, precompute:

- result blade index
- sign/metric coefficient

Then geometric product becomes a table-driven bilinear operation.

Pseudo-idea:

```
mul_sign[i, j]
mul_index[i, j]
```

Then:

```
for i, ai in enumerate(a.data):
    if ai == 0:
        continue
    for j, bj in enumerate(b.data):
        if bj == 0:
            continue
        out[mul_index[i, j]] += ai * bj * mul_sign[i, j]
```

Later you can optimize with:

- NumPy broadcasting
- Numba
- C extension
- Rust backend

But the semantic model stays unchanged.

That stability matters more than cleverness.

------

## API shape I would recommend

### Functional core

```
gp(a, b)
op(a, b)
left_contraction(a, b)
right_contraction(a, b)
hestenes_inner(a, b)
scalar_product(a, b)

reverse(x)
involute(x)
conjugate(x)

grade(x, k)
grades(x, ks)
scalar(x)
vector(x)
bivector(x)

dual(x, pseudoscalar=None)
undual(x, pseudoscalar=None)

norm2(x)
norm(x)
unit(x)
inverse(x)
```

### Method wrappers

```
a.gp(b)
a.op(b)
a.reverse()
a.grade(2)
a.dual()
```

### Optional operator sugar

```
a * b
a ^ b
a | b
~a
```

But document the named functions first, not the operators.

------

## Strong recommendation: separate semantic names from aliases

For example:

```
def gp(a, b): ...
def geometric_product(a, b): return gp(a, b)

def op(a, b): ...
def wedge(a, b): return op(a, b)

def reverse(x): ...
def rev(x): return reverse(x)
```

So you give:

- short names for experienced users
- explicit names for readability and IDE completion
- stable names for long-term codebases

This is how mature numerical libraries usually win trust.

------

## Type design

You probably want at least:

- `Algebra`
- `Multivector`
- maybe specific views/helpers:
  - `Blade`
  - `Rotor`
  - `Versor`
  - `Vector`

But I would be careful about too many subclasses. They often create friction.

Better approach:

- one `Multivector` type
- validation helpers

```
is_scalar(x)
is_vector(x)
is_bivector(x)
is_even(x)
is_rotor(x)
```

And constructors:

```
alg.scalar(3)
alg.vector([1, 2, 3])
alg.bivector(e12=1.0, e23=2.0)
alg.rotor_from_plane_angle(B, theta)
```

This avoids brittle inheritance hierarchies.

------

## Symbol naming and basis access

Users need predictable basis access.

I would provide:

```
e1, e2, e3 = alg.basis_vectors()
e12 = e1 * e2
I = alg.pseudoscalar()
```

And also named lookup:

```
alg.blade("e1")
alg.blade("e12")
alg.blade("e123")
```

But string parsing should be a convenience layer, not the core.

------

## Different products: be explicit

A lot of frustration in GA comes from overloaded words.

I’d define these distinctly in the docs and code:

- **geometric product**: full product
- **outer/wedge product**
- **left contraction**
- **right contraction**
- **scalar product**
- **commutator product**
- **anticommutator product**

Example:

```
def commutator(a, b):
    return 0.5 * (gp(a, b) - gp(b, a))

def anticommutator(a, b):
    return 0.5 * (gp(a, b) + gp(b, a))
```

Again: stable names.

------

## Numeric vs symbolic

Decide early whether the library is:

- numeric first
- symbolic first
- mixed

I would strongly recommend **numeric first**.

Use:

- `float64` by default
- optionally `complex128`
- maybe symbolic support later through SymPy adapters

Trying to do both from the start often makes everything worse.

------

## Exact places to prioritize ergonomics

### 1. Construction

Should be dead simple.

```
alg = Algebra((1, 1, 1))
e1, e2, e3 = alg.basis_vectors()

x = 3 + 2*e1 - e23
```

### 2. Grade projection

Users do this constantly.

```
grade(x, 2)
x.grade(2)
```

### 3. Pretty printing

This matters more than library authors think.

Bad printing makes GA feel unusable.

Need:

- deterministic blade order
- configurable coefficient precision
- no weird hidden basis order changes
- readable zero suppression

### 4. Errors

If a user mixes algebras, error clearly:

```
ValueError: cannot multiply multivectors from different algebras: Cl(3,0) vs Cl(1,3)
```

Not some NumPy broadcast nonsense.

------

## Versioning strategy

The reason these libraries feel unstable is often because:

- operators change meaning
- basis ordering changes
- helper names appear/disappear
- return types change subtly
- symbolic vs numeric behavior shifts

To avoid that:

### Promise a stable semantic core

For example:

- `gp`, `op`, `grade`, `reverse`, `dual`, `inverse` never change meaning
- basis blade ordering is fixed per algebra
- named basis strings are canonical

### Add sugar as optional

Anything cute or clever:

- parsing mini-languages
- shorthand operators
- magic constructors
- automatic promotion rules

should sit outside the core contract.

------

## Testing strategy

This is absolutely crucial for a GA library.

### Property tests

Use Hypothesis heavily.

Test algebraic laws like:

- associativity of geometric product
- distributivity
- grade projection idempotence
- reverse reverses product order
- involution parity behavior
- pseudoscalar duality behavior where valid

Example:

```
reverse(gp(a, b)) == gp(reverse(b), reverse(a))
```

within tolerance.

### Golden tests

Have fixed examples for:

- Cl(2,0)
- Cl(3,0)
- Cl(1,3)

Check known identities.

### Cross-release compatibility tests

Keep a suite of old user-facing examples and run them unchanged.

That’s how you stop the “every release breaks my intuition” problem.

------

## Minimal viable library design

If I were starting today, version 0.1 would have only:

- `Algebra(signature)`
- `Multivector`
- basis blade construction
- `gp`, `op`
- `left_contraction`, `right_contraction`, `scalar_product`
- `reverse`, `involute`, `conjugate`
- `grade`
- `dual`, `inverse`
- pretty printing
- dense numeric backend
- stable named API

No symbolic mode.
 No fancy parser.
 No automatic theorem layer.
 No huge hierarchy of special object types.

Then later:

- rotors/versors helpers
- exp/log for bivectors
- outermorphisms
- linear map representation
- PGA/CGA convenience APIs
- symbolic adapter
- JAX/Numba backend

------

## A concrete philosophy

I’d build it more like:

- **NumPy / SciPy internally**
- **PyTorch/JAX style predictable API**
- **SymPy-style named operations**
- **without leaning too hard on magical operator cleverness**

In other words:

- boring core
- elegant shell
- no ambiguity in semantics

------

## Example of a user-facing API I think would feel good

```
from pyga import Algebra, gp, op, grade, reverse, dual

g3 = Algebra((1, 1, 1))
e1, e2, e3 = g3.basis_vectors()
I = g3.pseudoscalar()

a = 1 + 2*e1 + 3*(e1*e2)
b = e2 + e3

print(gp(a, b))
print(op(a, b))
print(grade(a, 2))
print(reverse(a))
print(dual(e1))
```

And then optional sugar:

```
R = g3.rotor_from_plane_angle(e1 ^ e2, 0.3)
v = e1 + 2*e2
v2 = R * v * reverse(R)
```

That feels readable, but the real contract remains the named functions.

------

## My strongest recommendations

If you want this to feel “programmer first”:

- make **named functions** the primary API
- fix **one precise meaning** per function
- avoid ambiguous words like `inner`
- use **bitmask blades + dense coefficient arrays**
- keep `Algebra` immutable and central
- keep `Multivector` simple
- add syntax sugar only after the semantic core is stable
- write property tests for algebraic identities
- treat backward compatibility as a feature, not an afterthought

------

## One more thing: docs should teach operations, not notation tricks

Most GA libraries over-document notation and under-document behavior.

Good docs should answer things like:

- What exactly does `dot()` mean here?
- How is it different from `left_contraction()`?
- What does `dual()` assume about the pseudoscalar?
- When does `inverse()` fail?
- What is the coefficient ordering?
- Does `norm()` mean Euclidean magnitude or rotor norm?

That alone would make a new library feel much better than many existing ones.

If you want, I can sketch a concrete Python package layout for this, with class names, module names, and a first-pass implementation plan.
