# SPEC-005: Numeric Functions

**Status:** Implemented

## Intent

`galaga.core` provides numeric functions that require infinite-series, transcendental,
or branch-selection machinery in addition to the finite Clifford and exterior
operations. Geometry conveniences that merely compose existing operations are
not part of this surface.

The functions in this specification operate on immutable real `float64`
multivectors. They do not opt into NumPy ufunc dispatch or introduce complex
coefficients to satisfy an unsupported branch.

## Scalar square root

`scalar_sqrt(x)` accepts a finite real number or a pure scalar multivector. It
returns the nonnegative real square root as a `float` or as a scalar
multivector in the same algebra, respectively.

Negative inputs, nonscalar multivectors, and non-real values must raise. The
function does not introduce complex coefficients.

## Study-number square root

For

$$
x = a + N,
$$

where $a$ is scalar and $N^2=q$ is scalar, `sqrt(x)` uses the principal real
Study-number branch

$$
c = \sqrt{\frac{a + \sqrt{a^2-q}}{2}},
\qquad
\sqrt{x}=c+\frac{N}{2c}.
$$

The result must square back to the input within the numeric tolerance. This
domain includes simple elliptic and hyperbolic rotors and null PGA translators
with positive scalar part. A non-Study input, a negative pure scalar, a branch
with no real result, or a singular selected branch must raise `ValueError`.

## Geometric exponential

`exp(X)` is the geometric-product power series

$$
\exp(X)=\sum_{k=0}^{\infty}\frac{X^k}{k!}.
$$

If $X^2=q$ is scalar, the following closed forms apply:

| Generator square | Result |
|---|---|
| $q<0$ | $\cos(\sqrt{-q}) + \operatorname{sinc}(\sqrt{-q})X$ |
| $q=0$ | $1+X$ |
| $q>0$ | $\cosh(\sqrt q) + \frac{\sinh(\sqrt q)}{\sqrt q}X$ |

Here `sinc(t)` means $\sin(t)/t$. General inputs use a convergent
scaling-and-squaring series. The infinity norm of the backend-neutral left
action selects the scale; Taylor terms use the ordinary geometric product,
and repeated squaring restores the original scale. The result must be
independent of the selected product backend and valid in a native
nonorthogonal Gram basis.

Unlike `scalar_sqrt`, `exp` requires a multivector so its output algebra is
unambiguous.

## Rotor logarithm

`log(R)` is the principal real logarithm for a normalized Study-number rotor

$$
R=a+N,\qquad N^2=q\in\mathbb R.
$$

Its branches are:

| Nonscalar square | Result |
|---|---|
| $q<0$ | $\frac{\operatorname{atan2}(\sqrt{-q},a)}{\sqrt{-q}}N$ |
| $q=0$, $a=1$ | $N$ |
| $q>0$, principal real branch | $\frac{\operatorname{atanh}(\sqrt q/a)}{\sqrt q}N$ |

Consequently, `log(exp(N)) == N` also holds for a null PGA translator
generator. The identity maps to zero. The scalar rotor `-1` must raise because
its logarithm cannot select a plane from the input.

A non-rotor, a general non-Study rotor, or a rotor outside the principal real
hyperbolic branch must raise instead of returning a partial bivector answer.

## Outer transcendental family

Write $x=a+X$, where $a$ is scalar and $X$ has zero scalar part. Define the
finite positive-grade wedge series

$$
E_0(X)=\sum_j\frac{X^{\wedge 2j}}{(2j)!},
\qquad
E_1(X)=\sum_j\frac{X^{\wedge(2j+1)}}{(2j+1)!}.
$$

Because every term of $X$ has positive grade, both sums terminate by exterior
degree `n`. `galaga.core` defines:

$$
\begin{aligned}
\operatorname{outerexp}(x)
  &= e^a(E_0(X)+E_1(X)),\\
\operatorname{outercos}(x)
  &= \cosh(a)E_0(X)+\sinh(a)E_1(X),\\
\operatorname{outersin}(x)
  &= \sinh(a)E_0(X)+\cosh(a)E_1(X).
\end{aligned}
$$

Thus `outercos` and `outersin` mean the even- and odd-power parts of the outer
exponential; they are not alternating-sign trigonometric series. In
particular,

```python
outerexp(x) == outercos(x) + outersin(x)
```

for every input. Factoring the scalar part makes scalar behavior exact instead
of incorrectly truncating its non-nilpotent power series at `n`.

`outertan(x)` is `outersin(x) * inverse(outercos(x))` and propagates the normal
noninvertibility error. The wedge-series results must be metric-independent.

## Deliberately excluded conveniences

`Algebra.rotor`, `project`, `reject`, `reflect`, and compatibility aliases add
names but no new numerical capability: each is a short composition of
existing functions. They belong in a future geometry-helper or Galaga facade
layer rather than this numeric-function surface.

The architectural rationale and implementation strategy are recorded in
[ADR-010](../adrs/010-separate-numeric-functions-from-geometry-helpers.md) and
[ADR-011](../adrs/011-evaluate-numeric-functions-with-explicit-real-branches.md).
