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

## Geometric square root

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
with positive scalar part.

When the entire stored Gram matrix is zero, the geometric product equals the
exterior product. Every positive-grade $N$ is nilpotent, with $N^{n+1}=0$.
For $a>0$, `sqrt(a + N)` evaluates the finite principal-branch polynomial

$$
\sqrt{a+N}=\sqrt a\sum_{k=0}^{n}\binom{1/2}{k}(N/a)^k.
$$

Its result is the unique square root with positive scalar coefficient. Zero
returns zero. An all-null input with negative scalar coefficient has no real
root; a nonzero input with zero scalar coefficient has no selected principal
branch, even when roots exist. Both cases raise `ValueError`. On other metrics,
a non-Study input, a negative pure scalar, a branch with no real result, or a
singular selected branch raises `ValueError`. See [ADR-164](../../adrs/164-exterior-algebra-square-roots.md)
for the mathematical proof and branch rationale.

## Real powers in all-null algebras

Integer `x ** k` remains available for every metric; negative integers use
the geometric inverse. For a finite real exponent supplied as a non-integer
numeric type, `**` is supported only when the entire stored Gram matrix is
zero. If $x=a+N$ has $a>0$ and positive-grade $N$, then

$$
x^\alpha=a^\alpha\sum_{k=0}^{n}\binom{\alpha}{k}(N/a)^k.
$$

The sum terminates because $N^{n+1}=0$. The $\alpha=1/2$ case is the
all-null branch of `sqrt(x)`; the $\alpha=-1$ case agrees with the existing
integer inverse path. In exact arithmetic, powers of the same positive-scalar
value obey $x^\alpha x^\beta=x^{\alpha+\beta}$.

For the zero multivector, a positive real exponent returns zero, exponent
zero returns identity, and a negative exponent raises. Nonzero all-null
values with nonpositive scalar part raise for noninteger exponents. Other
metrics continue to reject noninteger `**` with `TypeError`; `sqrt` retains
its separate Study-number domain on those metrics. See
[ADR-165](../../adrs/165-real-powers-in-all-null-algebras.md).

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

## Algebra logarithm

`log(A, atol=1e-12)` is the real principal algebra logarithm. It does not
require a rotor, evenness, normalization, or Study-number shape. Like `exp`,
it requires a multivector so the algebra is explicit.

For a positive scalar, return the ordinary real logarithm. For $A=a+N$
with exactly scalar $N^2=q$, use these closed forms:

| Nonscalar square | Result and branch |
|---|---|
| $q<0$ | $\log\sqrt{a^2-q}+\frac{\operatorname{atan2}(\sqrt{-q},a)}{\sqrt{-q}}N$ |
| $q=0$, $a>0$ | $\log a+N/a$ |
| $q>0$, $a>\sqrt q$ | $\tfrac12\log(a^2-q)+\frac{\operatorname{atanh}(\sqrt q/a)}{\sqrt q}N$ |

General inputs use the principal resolvent integral of the native
left-regular action. Increasing Gauss-Legendre orders 8 through 256 provide
convergence estimates, without requiring diagonalizability. Recover the
multivector from the action on the scalar identity and verify exponentiation
in the original algebra. Positive scalar scaling retains its scalar log.
No SciPy dependency or alternate geometric-product backend is introduced.

The branch excludes singular inputs and the nonpositive-real spectral axis.
In particular, scalar `-1` is rejected, even in an algebra where nonprincipal
real logarithms exist. Numerically unresolved spectra, ill-conditioned
actions, failed solves or convergence failures also raise. No complex
coefficients, invented planes or alternative branches are returned.

`atol` bounds successive candidate differences in native coefficients. The
exponential round-trip residual is bounded by
`atol * max(1, max(abs(A.data)))`, without an additional relative term. This
backward-error check is not a forward-error bound near the branch cut.

## Geometric rotor generator

`rotor_generator(R, atol=1e-12)` requires a normalized vector-preserving
rotor and returns its principal algebra logarithm only if the result passes
`is_rotor_generator`. Otherwise it raises; it never normalizes, projects
away grades, or searches alternative branches. The returned exponent has
the full scale, including a half-angle when that convention is used.

`is_rotor_generator(B, atol=1e-12)` checks evenness, $B+\widetilde B=0$,
and grade-one commutators $Be_i-e_iB$ for every native basis vector. All
checks use absolute coefficient tolerance. These infinitesimal conditions
match the group checked by `is_rotor`; in nondegenerate metrics they
characterize bivectors, including zero. Degenerate metrics may additionally
admit generators acting trivially on vectors.

In Euclidean dimension six, the pseudoscalar $I$ is a rotor but
$\log I=\pi I/2$ is not a rotor generator: its half-exponential is the
nonrotor $(1+I)/\sqrt2$. Therefore `log(I)` succeeds and
`rotor_generator(I)` raises. A different bivector logarithm exists, but
finding it automatically is outside the current branch-selection policy.

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
existing functions. They belong, if needed, in a validated model-specific
layer rather than this numeric-function surface.

The architectural rationale and implementation strategy are recorded in
[ADR-010](../adrs/010-separate-numeric-functions-from-geometry-helpers.md) and
[ADR-011](../adrs/011-evaluate-numeric-functions-with-explicit-real-branches.md),
with the logarithm/generator split refined by
[ADR-125](../../adrs/125-separate-algebra-logarithms-from-rotor-generators.md).
