# SPEC-006: Polynomial Multivector Inverse in Dimensions up to Six

**Status:** Proposed for future implementation.

## Purpose and scope

Provide a complete implementation specification for a Jones polynomial fast
path inside the existing `inverse(value, rtol=1e-10, atol=1e-12)` operation.
Galaga's current inverse already supports six-dimensional algebras. This
proposal seeks to avoid constructing and solving the left-regular system on
inputs for which a checked algebraic formula succeeds.

The proposed path operates on `galaga.core.Multivector`. It covers vector
dimensions $0\leq n\leq6$, where $n$ is `algebra.n`, not the coefficient
dimension `algebra.dim` ($2^n$). Inputs may have mixed grades and arbitrary
real symmetric Gram matrices, including degenerate metrics. CSTA has $n=6$
and 64 coefficients and is within this domain.

Keep the public operation name, parameters, result ownership, expression
operation ID, and exception contract. The existing left-regular solve remains
the fallback for dimensions above six and for rejected numerical candidates.
No new runtime dependency or public algorithm selector is required.

## Sources

The mathematical algorithm is David Arthur Jones's scalar-rescaling inverse.
These sources provide its provenance and related inverse constructions:

1. David Arthur Jones, *Another 6D Multivector Inverse Algorithm*,
   **Advances in Applied Clifford Algebras 36, 43 (2026)**,
   [DOI and publisher page](https://doi.org/10.1007/s00006-026-01455-5).
   Appendices B and C give polynomial expansions; Appendix E gives Python
   implementations. The article was published on 13 August 2026.
2. [Clifford6D source repository](https://github.com/dajonesy/Clifford6D)
   and [release v1.0](https://github.com/dajonesy/Clifford6D/releases/tag/v1.0).
   The inspected tag points to commit
   `af9e1358461d0ab546918232b655afc1ceb41538`.
   The [Jones implementation](https://github.com/dajonesy/Clifford6D/blob/af9e1358461d0ab546918232b655afc1ceb41538/jones_6D_inverse.py)
   supplies the successive scalar factors $-3,-1,-1/3$ and the lower-dimensional
   branch. The [Acus comparison implementation](https://github.com/dajonesy/Clifford6D/blob/af9e1358461d0ab546918232b655afc1ceb41538/acus_6D_inverse.py)
   gives an alternative expression for comparison.
3. David's [recorded AGACSE 2026 talk](http://www.mmrc.iss.ac.cn/agacse2026/videos/662_0265.mp4)
   (MP4). This is supplementary material; implementing this specification does
   not require watching the recording.
4. A. Acus and A. Dargys, *The Inverse of a Multivector: Beyond the Threshold
   $p+q=5$*, **Advances in Applied Clifford Algebras 28, 65 (2018)**,
   [published paper](https://doi.org/10.1007/s00006-018-0885-4),
   [open preprint, arXiv:1712.05204v2](https://arxiv.org/abs/1712.05204v2).
   This is the grade-negation construction preceding Jones's formulation.
5. E. Hitzer and S. J. Sangwine, *Multivector and multivector matrix inverses
   in real Clifford algebras*, **Applied Mathematics and Computation 311,
   375–389 (2017)**,
   [DOI](https://doi.org/10.1016/j.amc.2017.05.027).
6. D. Shirokov, *On computing the determinant, other characteristic polynomial
   coefficients, and inverse in Clifford algebras of arbitrary dimension*,
   **Computational and Applied Mathematics 40, 173 (2021)**,
   [DOI](https://doi.org/10.1007/s40314-021-01536-0).
   This provides context for polynomial inverses beyond the dimension limit
   of the proposed Jones path.

The Python below expresses the mathematics using Galaga's immutable numeric
objects. Its scaling, candidate checks, and fallback policy are Galaga design
choices, distinct from the source implementation's fixed `SMALL` threshold.

## Mathematical conventions

All juxtaposed multivectors are multiplied with the **geometric product**.
Neither wedge products nor coefficient-wise multiplication may be substituted.
Let $\widetilde X$ denote reversion and $\langle X\rangle_0$ the scalar
coefficient, identified with its scalar multiple of the identity $1$.

Define scalar rescaling by

$$
T_\lambda(X)=X+(\lambda-1)\langle X\rangle_0\,1.
$$

Only the scalar coefficient changes. In particular,

$$
T_{-1}(X)=X-2\langle X\rangle_0\,1.
$$

This negates the scalar part, not the nonscalar part. The source's `bar(X)`
instead means $2\langle X\rangle_0\,1-X=-T_{-1}(X)$; confusing these
definitions changes the signs of intermediate expressions.

Scalar projection returns a real number in the reference Python. Scalar
addition to a core multivector supplies the central scalar identity implicitly.
The implementation may copy `data` and replace `data[0]` to perform
$T_\lambda$ without cancellation from subtracting and re-adding the scalar.
It must never mutate an input's read-only coefficient array.

## Form the self-reverse product

For the input $A$, compute

$$
H=A\widetilde A.
$$

Reversion reverses product order, so

$$
\widetilde H=\widetilde{A\widetilde A}=A\widetilde A=H.
$$

The reversion sign on grade $k$ is $(-1)^{k(k-1)/2}$. Consequently, for
$n\leq6$, $H$ can contain only grades $0,1,4,5$ that exist in the algebra.
It need not be scalar, positive, or even. Do not replace $H$ by `norm2(A)`.

### Exactly scalar shortcut

If $H=h\,1$ exactly and $h\neq0$, then

$$
A^{-1}=\widetilde A/h.
$$

This works for either sign of $h$. The reference path requires all stored
nonscalar coefficients of $H$ to be exactly zero. A tolerance-based
`is_scalar(H)` must not silently discard small grades. Every shortcut result
still undergoes both residual checks.

An exactly scalar shortcut is mathematically valid in higher dimensions too.
For a simple initial integration, this proposal attempts all optimized
branches only when $n\leq6$; larger dimensions go directly to the baseline.

## Dimensions zero through four

For nonscalar $H$ and $n\leq4$, set

$$
C=T_{-1}(H),\qquad D=CH=d\,1.
$$

Writing $H=h+V$, the available nonscalar grades are one and, only when
$n=4$, four. A vector anticommutes with the four-dimensional pseudoscalar;
the square of each is scalar. Thus $V^2$ is scalar, including for degenerate
metrics, and

$$
CH=(-h+V)(h+V)=V^2-h^2=d\,1.
$$

When $d\neq0$, the inverse is

$$
A^{-1}=\widetilde A\,C/d.
$$

Dimension zero and other scalar-only inputs normally take the scalar shortcut.
The general formula here needs three geometric products: form $H$, form
$D$, and multiply $\widetilde A$ by the scaled $C$.

## Dimensions five and six

For nonscalar $H$ and $5\leq n\leq6$, evaluate these steps in order:

$$
\begin{aligned}
P &= T_{-3}(H)H,\\
Q &= T_{-1}(P)H,\\
C &= T_{-1/3}(Q),\\
D &= CH=d\,1.
\end{aligned}
$$

The proposed inverse candidate is

$$
X=\widetilde A\,(C/d).
$$

This needs five geometric products: $A\widetilde A$, the products forming
$P$ and $Q$, $CH$, and the final multiplication. Scalar rescaling and scalar
division are not geometric products. Residual validation adds two more
geometric products.

### Polynomial expansion and inverse argument

Introduce $h_j=\langle H^j\rangle_0$. Expanding the scalar-rescaling steps gives

$$
P=H^2-4h_1H,
$$

$$
Q=H^3-4h_1H^2+(8h_1^2-2h_2)H,
$$

$$
C=H^3-4h_1H^2+(8h_1^2-2h_2)H
  -\frac43h_3+8h_1h_2-\frac{32}{3}h_1^3.
$$

All terms in $C$ are powers of the same $H$ with central scalar
coefficients, so $CH=HC$. Jones's six-dimensional self-reverse polynomial
identity states that this product has no nonscalar part. Equivalently,

$$
H^4-4h_1H^3+(8h_1^2-2h_2)H^2
+\left(-\frac43h_3+8h_1h_2-\frac{32}{3}h_1^3\right)H-d\,1=0,
$$

where taking the scalar part yields

$$
d=h_4-\frac{16}{3}h_1h_3+16h_1^2h_2-2h_2^2
  -\frac{32}{3}h_1^4.
$$

The polynomial identity is the substantive dimension-specific result; the
expansion alone does not prove that $CH$ is scalar. See
[Jones, Appendix C](https://doi.org/10.1007/s00006-026-01455-5).
The scalar-rescaling evaluation avoids computing the powers separately.

For $d\neq0$,

$$
AX=A\widetilde A C/d=HC/d=1.
$$

In a finite-dimensional unital algebra a right inverse is a left inverse:
$AX=1$ makes left multiplication by $A$ surjective and therefore injective;
$A(XA-1)=0$ then forces $XA=1$. This argument does not require a
nondegenerate metric. In floating-point arithmetic, verify both equations
explicitly rather than relying on this exact argument.

Use $d$ as the algorithm's denominator, not as the public
`metric_determinant`, not as $\det L_A$, and not as a norm. Its sign and
normalization depend on the formula; for scalar $A=a$ the unshortened
five/six-dimensional formula gives $d=-a^8$.

### General Gram matrices and degeneracy

The operations above are basis-independent Clifford operations. An invertible
linear change of basis preserves grades, scalar projection, reversion, and
geometric products. No orthogonal basis conversion is needed at runtime.

The scalar identity is polynomial in the entries of $A$ and of the symmetric
Gram matrix. Its validity for nonsingular symmetric metrics extends to
singular symmetric metrics by continuity: nonsingular symmetric matrices are
dense. This concerns the identity $CH=d\,1$, not the assertion that every
element of a degenerate algebra is invertible.

For the all-null exterior algebra, an independent inverse is available when
$A=a+N$ has $a\neq0$:

$$
A^{-1}=\frac1a\sum_{k=0}^{n}(-N/a)^k,
\qquad N^{n+1}=0.
$$

This is a useful independent oracle. Negative $a$ is allowed for inversion;
the positive-scalar restrictions on noninteger powers do not apply here.

## Numerical acceptance and fallback

### Scale before taking products

Let $s=\max_i|A_i|$ in the native coefficient array and compute $B=A/s$.
Zero has no inverse. For nonzero finite $s$, compute a candidate $Y$ for
$B^{-1}$ and return the candidate $X=Y/s$ for $A^{-1}$.

This coefficient scale is positive, requires no metric assumption, and is not
the GA norm. For the unshortened formulas,

$$
d(tA)=t^4d(A)\quad(n\leq4),\qquad
d(tA)=t^8d(A)\quad(n=5,6).
$$

Therefore a fixed absolute cutoff on $d$ is unsuitable. For example, in
Euclidean dimension six, $A=2+e_1$ has inverse $(2-e_1)/3$ and denominator
$d=-81$. For $0.01A$, the denominator is $-8.1\times10^{-15}$: the source's
`SMALL=1e-12` rejects it despite unchanged relative conditioning.

Divide arrays directly by $s$ and $d$; do not form their reciprocals or the
combined product $sd$ first. Those intermediate scalars can overflow or
underflow even when the desired quotient is representable. If normalization
turns any nonzero stored coefficient into zero, decline the fast path.
Scaling coefficients cannot prevent every failure caused by an extreme Gram
matrix; nonfinite intermediates must decline the path too.

### Check the denominator's scalar identity

For the nonscalar branch, retain the entire computed $D=CH$. Define

$$
m=\max_i|D_i|,\qquad
\eta=\frac{\max_{i>0}|D_i|}{m}.
$$

The proposed initial guard accepts the denominator only if $m>0$,
$d=D_0\neq0$, all coefficients are finite, and
$\eta\leq64\epsilon$, where $\epsilon$ is float64 machine epsilon.
The maximum of an empty nonscalar slice is zero. This conservative internal
guard detects unresolved cancellation; it is not a singularity criterion.
It may send otherwise invertible values to the fallback. Do not use the
caller's `atol` as an absolute determinant threshold.

### Check the inverse itself

Require finite candidate coefficients and verify on the **original** input

$$
AX\approx1,\qquad XA\approx1.
$$

Both complete coefficient arrays must satisfy `np.allclose` against the
identity with the caller's existing `rtol` and `atol`. Thus a nonscalar
residual has absolute allowance `atol`, while the scalar identity coefficient
has allowance `atol + rtol`. Keep this existing convention; do not replace
it with average error or a residual bound multiplied by the input's norm.

A zero denominator, excessive nonscalar denominator residue, overflow,
unrepresentable candidate, or failed inverse check declines the fast path.
The public operation then runs the existing solve on the original input.
Failure of that solve or its checks raises the existing
`ValueError("multivector is not invertible")`. Never return `None`, a
pseudoinverse, or a projected answer from the public operation.

## Complete reference Python

This block is executable against the current numeric core. `inverse_with_jones`
is a reference name for this document, not a proposed additional public API.
In production, keep the dispatcher named `inverse` and extract its present
solve into a private helper. The fallback below performs the solve directly,
so it cannot recursively re-enter the proposed dispatcher.

```python
import numpy as np

from galaga.core import Multivector


def scalar_rescale(value: Multivector, factor: float) -> Multivector:
    data = value.data.copy()
    data[0] *= factor
    return value.algebra.multivector(data)


def verified_inverse(value, candidate, *, rtol, atol):
    if not np.all(np.isfinite(candidate.data)):
        return False
    try:
        with np.errstate(over="raise", divide="raise", invalid="raise"):
            left = value * candidate
            right = candidate * value
        identity = value.algebra.identity.data
        return bool(
            np.allclose(left.data, identity, rtol=rtol, atol=atol)
            and np.allclose(right.data, identity, rtol=rtol, atol=atol)
        )
    except (FloatingPointError, OverflowError, ValueError):
        return False


def jones_candidate(value, *, rtol, atol):
    if value.algebra.n > 6:
        return None
    scale = float(np.max(np.abs(value.data)))
    if scale == 0.0 or not np.isfinite(scale):
        return None

    try:
        with np.errstate(
            over="raise", divide="raise", invalid="raise", under="ignore"
        ):
            normalized = value / scale
            if np.any((value.data != 0.0) & (normalized.data == 0.0)):
                return None
            reversed_value = ~normalized
            h = normalized * reversed_value

            if not np.any(h.data[1:] != 0.0):
                denominator = float(h.scalar_part)
                if denominator == 0.0:
                    return None
                candidate = reversed_value / denominator
            else:
                if value.algebra.n <= 4:
                    c = scalar_rescale(h, -1.0)
                else:
                    p = scalar_rescale(h, -3.0) * h
                    q = scalar_rescale(p, -1.0) * h
                    c = scalar_rescale(q, -1.0 / 3.0)

                d = c * h
                denominator = float(d.scalar_part)
                magnitude = float(np.max(np.abs(d.data)))
                tail = float(np.max(np.abs(d.data[1:]), initial=0.0))
                if not np.all(np.isfinite(d.data)):
                    return None
                if magnitude == 0.0 or denominator == 0.0:
                    return None
                if tail / magnitude > 64.0 * np.finfo(np.float64).eps:
                    return None
                candidate = reversed_value * (c / denominator)

            candidate = candidate / scale
    except (FloatingPointError, OverflowError, ValueError, ZeroDivisionError):
        return None

    if verified_inverse(value, candidate, rtol=rtol, atol=atol):
        return candidate
    return None


def left_regular_inverse(value, *, rtol, atol):
    try:
        with np.errstate(over="raise", divide="raise", invalid="raise"):
            coefficients = np.linalg.solve(
                value.algebra.left_action(value),
                value.algebra.identity.data,
            )
            candidate = value.algebra.multivector(coefficients)
    except (
        np.linalg.LinAlgError,
        FloatingPointError,
        OverflowError,
        TypeError,
        ValueError,
    ):
        raise ValueError("multivector is not invertible") from None
    if not verified_inverse(value, candidate, rtol=rtol, atol=atol):
        raise ValueError("multivector is not invertible")
    return candidate


def inverse_with_jones(value, *, rtol=1e-10, atol=1e-12):
    if not isinstance(value, Multivector):
        raise TypeError("inverse expects a Multivector")
    candidate = jones_candidate(value, rtol=rtol, atol=atol)
    if candidate is not None:
        return candidate
    return left_regular_inverse(value, rtol=rtol, atol=atol)
```

Tolerance arguments have the same intended finite, nonnegative values as
the existing inverse. This proposal does not add a new tolerance-validation
API. `np.errstate` is local and must not change the process-wide NumPy policy.
Do not catch resource failures or arbitrary exceptions as numerical misses.

### Desk examples

Execute this block after the reference implementation:

```python
from galaga.core import Algebra

euclidean = Algebra(6)
e1 = euclidean.basis_vectors()[0]
a = 2 + e1
expected = (2 - e1) / 3
assert inverse_with_jones(a).almost_equal(expected)
assert inverse_with_jones(0.01 * a).almost_equal(expected / 0.01)

exterior = Algebra(0, 0, 6)
u, v, w, *_ = exterior.basis_vectors()
n = u + (v ^ w)
a = 2 + n
expected = 0.5 - n / 4 + (n * n) / 8
assert n * n == 2 * (u ^ v ^ w)
assert inverse_with_jones(a).almost_equal(expected)
assert a * expected == expected * a == exterior.identity
```

## Alternative polynomial for cross-checking the factorization

For the five/six-dimensional branch, define the nonscalar-negation operation
$\operatorname{bar}(X)=2\langle X\rangle_0\,1-X$. The Acus comparison
expression in the pinned source can be evaluated as follows:

```python
def acus_terms(h):
    def bar(x):
        return 2 * x.scalar_part - x

    hb = bar(h)
    s = h * bar(h * h) + 2 * bar(hb * bar(hb * hb))
    return s, s * h
```

Algebraic expansion gives $S_{\mathrm{Acus}}=-3C$ and
$S_{\mathrm{Acus}}H=-3d\,1$, so the ratio defining the inverse agrees.
Compare these intermediate identities, not just the final quotient: the two
formulations have different denominator signs and factors. This checks the
factorization; it is not an independent numeric product implementation.

## Required implementation validation

Adding the runtime path requires unit tests, not just notebook output.
Acceptance checks must exercise the real algebra and retain the solve as an
independent algorithmic oracle. Do not require every near-singular input to
produce identical acceptance decisions from differently conditioned methods.

| Area                       | Required cases and checks                                                                                                                                                                     |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dimensions                 | Every $n=0,\ldots,6$; scalars, exact scalar $A\widetilde A$, nonscalar lower-dimensional branch, and five/six-dimensional branch                                                              |
| Six-dimensional signatures | All 28 triples $(p,q,r)$ with $p+q+r=6$, multiple seeded dense inputs per triple, and permutations of diagonal entries                                                                        |
| General Gram matrices      | Scaled diagonal, oblique nondegenerate, oblique degenerate, native-null CSTA, and native-null CGA                                                                                             |
| Algebraic intermediates    | Derive $H$ from products; check its reversion; compare factored $C$ with its power expansion; check the nonscalar part of $CH$; compare the Acus sign/factor identities                       |
| Inverse correctness        | Check both products against identity; compare coefficients with the independently called solve on well-conditioned accepted inputs                                                            |
| Exterior oracle            | Positive and negative nonzero scalar parts; mixed-grade nilpotents with nonzero nonscalar square; compare with the terminating geometric series                                               |
| Singular inputs            | Zero, nonzero all-null values with zero scalar part, null vectors, and the Euclidean zero divisor $1+e_1$                                                                                     |
| Scale behavior             | Fixed well-conditioned values scaled by $\pm10^k$, including $k=\pm2,\pm100,\pm200$ when their inverses are representable; the deterministic $0.01(2+e_1)$ regression                         |
| Numerical misses           | Exactly zero or underflowed denominator, nonscalar denominator residue, extreme Gram entries, coefficient loss on normalization, unrepresentable output, and failure of either residual check |
| Fallback dispatch          | Prove a validated fast result avoids `left_action`/solve; prove each numerical miss invokes the baseline exactly once without recursive dispatch                                              |
| Larger dimensions          | A generic seven-dimensional input uses the baseline; demonstrate that blindly applying the six-dimensional formula need not give scalar $CH$                                                  |
| Product backends           | Exercise every backend supporting each chosen metric; no private Euclidean multiplication tables or basis-order assumptions                                                                   |
| Public integration         | Facade `inverse`, division, negative integer powers, dependent duality calls, tracked operation IDs, named values, and annotation rendering retain their contracts                            |
| Ownership and environment  | Inputs and Gram matrices remain unchanged; result uses the same numeric algebra; Python 3.11 and 3.14; no dependency additions                                                                |

For basis changes, construct an invertible vector transformation, derive its
exterior lift from minors, and transport both the Gram matrix and coefficients.
Compute products before comparing the transported inverse. Renaming blades or
changing presentation order alone is not a numeric basis-change test.

The denominator guard and inverse checks are separate: a scalar-looking $D$
does not establish that a floating-point inverse is accurate. Tests must
include candidates whose denominator passes but whose two-sided check fails.
Check error behavior and fallback ownership as well as successful outputs.

## Performance and activation

Benchmark the checked path, including normalization, scalar-identity checks,
and both inverse residuals. Compare with the current checked solve, reporting
dimension, metric, backend, dense/sparse coefficients, warm/cold caches, and
fallback frequency. Five algebra products do not guarantee a speedup on every
backend. Automatic activation must be justified by measured workloads.

The optimized Euclidean tables in the source's `InverseSupport_6D.py` are not
part of this initial implementation. The algorithm above is complete using
ordinary backend products. Any later specialized multiplication must derive
its signs and metric factors and receive its own correctness and timing review.

Before activation, update [ADR-008](../adrs/008-left-regular-general-inverse.md)
to record the selected dispatch policy and update
[SPEC-003](SPEC-003-product-and-duality-conventions.md#norm-and-inverse)
to describe the implemented path.
