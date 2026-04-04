# galaga vs kingdon: Inner Product, Exp, Log, Inverse, and Square Root

## Inner Product

Both libraries agree on results for common cases (vector·vector, bivector·vector) but differ in architecture and API.

### galaga

Provides 5 named inner product variants plus a unified dispatcher:

```python
from galaga import ip
ip(a, b, 'doran_lasenby')  # |r-s| grade, includes scalars (default, also the | operator)
ip(a, b, 'hestenes')       # |r-s| grade, kills scalars
ip(a, b, 'left')           # s-r grade (zero if r > s)
ip(a, b, 'right')          # r-s grade (zero if s > r)
ip(a, b, 'scalar')         # grade-0 part only
```

The `|` operator maps to Doran–Lasenby. Each variant is a direct loop over nonzero coefficients using precomputed multiplication tables (`_mul_index`, `_mul_sign`), accumulating into a dense numpy array. Computation is eager.

### kingdon

Same variants, all implemented through a single `codegen_ip` with a `diff_func` parameter:

```python
a | b       # or a.ip(b) — symmetric inner product (abs grade diff)
a.lc(b)     # left contraction
a.rc(b)     # right contraction
a.sp(b)     # scalar product
```

Kingdon doesn't loop at runtime. It symbolically generates a Python function on first call (rational polynomials + CSE), caches it by type number, and subsequent calls execute the compiled function directly. First call ~130–300μs overhead, subsequent calls ~2μs.

### Behavioural comparison

| Test case | galaga `\|` (Doran–Lasenby) | kingdon `\|` (symmetric ip) |
|---|---|---|
| `scalar \| vector` | `5e₁` (passes through) | `5e₁` (passes through) |
| `e12 \| e1` | `-e₂` | `-e₂` |
| `e1 \| e12` | `e₂` | `e₂` |
| `hestenes(scalar, vector)` | `0` (kills scalars) | N/A (no separate hestenes) |

Both `|` operators use `|r-s|` grade selection and include scalars — same math, different names (galaga calls it "Doran–Lasenby", kingdon calls it "symmetric inner product"). Kingdon has no dedicated Hestenes mode that kills scalars.

## Exponential (exp)

Both require the input to square to a scalar ("simple" elements). Both handle three cases: Euclidean (B² < 0), hyperbolic (B² > 0), and null (B² = 0). Both produce identical numerical results.

### galaga

Straightforward branching with numpy:

```python
B2 = gp(B, B).scalar_part
if abs(B2) < 1e-15:       return 1 + B                              # null
if B2 < 0:                return cos(|B|) + sin(|B|)/|B| * B        # Euclidean
else:                      return cosh(|B|) + sinh(|B|)/|B| * B     # hyperbolic
```

Uses `np.cos`/`np.sin`/`np.cosh`/`np.sinh` directly. Handles the null case via an explicit epsilon check (`1e-15`).

### kingdon

Uses a `sinhc` formulation (sinh(x)/x, or sinc for the trig case):

```python
ll = (self * self).filter().e   # scalar part of self²
l = sqrt(ll)
return self * sinhc(l) + cosh(l)
```

Auto-detects input type and selects functions:

- `float/int, ll > 0` → numpy `cosh`/`sinh` (hyperbolic)
- `float/int, ll == 0` → identity, returns `1 + self` (null)
- `float/int, ll < 0` or numpy arrays → `cos`/`sinc` (Euclidean)
- SymPy expressions → sympy `cos`/`sinc`

Custom functions can be injected: `B.exp(cosh=torch.cos, sinhc=..., sqrt=...)` — this is how you'd use it with PyTorch or JAX.

The `sinhc` formulation avoids the `sin(x)/x` division-by-zero at the origin since `sinc(0) = 1` by definition. Galaga handles this with the explicit `abs(B2) < 1e-15` branch instead.

Kingdon also provides `outerexp`, `outersin`, `outercos`, `outertan` — the exterior exponential (truncated series `1 + x + x∧x/2! + ...`), a different operation for the outer algebra. Galaga doesn't have these.

## Logarithm (log)

### galaga — built-in `log()` function

galaga provides `log` as a first-class function that extracts the bivector B from a rotor R such that `exp(B) = R`:

```python
s = R.data[0]                    # scalar part
B = R - scalar(s)                # bivector part
B2 = gp(B, B).scalar_part
if abs(B2) < 1e-15: return 0     # pure scalar rotor
if B2 < 0:                       # Euclidean
    theta = arctan2(|B|, s)
    return (theta / |B|) * B
else:                            # hyperbolic
    phi = arctanh(|B|/s)
    return (phi / |B|) * B
```

Handles Euclidean, hyperbolic, and identity rotors. Integrates with galaga's lazy expression tree system for symbolic display.

### kingdon — no built-in `log()`, manual composition with underlying library

Kingdon has no `log()` method on `MultiVector` or `Algebra`. The design philosophy is that since coefficients can be any type (numpy arrays, PyTorch tensors, SymPy expressions, etc.), the user composes the log manually using the underlying library's inverse trig functions:

```python
# Extract scalar and bivector parts (works with any coefficient type)
s = R.grade(0).e          # scalar coefficient — float, numpy array, torch tensor, etc.
B = R - R.grade(0)         # bivector part as a kingdon MV

# Use the underlying library's inverse trig
theta = np.arccos(s)       # or torch.arccos(s), or sympy.acos(s)
log_R = B * (theta / np.sin(theta))
```

This works with batched numpy arrays too:

```python
angles = np.array([0.1, 0.5, 1.0])
Rs = alg.multivector(e=np.cos(angles), e12=np.sin(angles))
s = Rs.grade(0).e                    # numpy array of scalar parts
B = Rs - Rs.grade(0)
theta = np.arccos(s)                  # vectorised arccos
log_Rs = B.map(lambda v: v * theta / np.sin(theta))
# → recovers [0.1, 0.5, 1.0] * e12
```

This is consistent with kingdon's `exp()` design, which also dispatches to the underlying library's trig functions (and allows injecting custom `cosh`/`sinhc`/`sqrt`). The difference is that `exp()` wraps this dispatch in a method, while `log()` is left to the user.

### Comparison

```
galaga:  log(exp(0.7 * e12)) = 0.7 * e12  ✓  (one function call)
kingdon: manual — extract parts, apply np.arccos, rescale  ✓  (3–4 lines)
```

galaga's `log` additionally handles the hyperbolic case (`B² > 0`) and the identity rotor (`B ≈ 0`) with explicit branches. In kingdon, the user must handle these cases themselves.

## Inverse

The two libraries take fundamentally different approaches to multivector inversion.

### galaga — versor inverse only

Uses the versor inverse formula: `x⁻¹ = ~x / (x * ~x).scalar_part`.

```python
x_rev = reverse(x)
denom = gp(x, x_rev).scalar_part
return x_rev / denom
```

This works for versors (products of non-null vectors): vectors, rotors, and other elements where `x * ~x` is a pure scalar. It does **not** produce a correct inverse for arbitrary multivectors — the result of `mv * mv⁻¹` will not be 1.

This is a deliberate design choice — galaga's docstring says "if you need [a general inverse], you probably want a different approach."

**Importantly, galaga fails silently on non-versors.** No error is raised, no warning is emitted — it returns a wrong answer without any indication. The only case that does raise is when `x * ~x ≈ 0` (e.g. a null vector in PGA), which triggers `ValueError: Multivector is not invertible`.

```
>>> mv = 1 + e₁ + e₁₂ + e₁₂₃
>>> inverse(mv) * mv
1 + 0.5e₁ - 0.5e₂ + 0.5e₃    ← silently wrong, no error or warning
```

### kingdon — general inverse via Hitzer (≤5D) or Shirokov (any D)

Kingdon dispatches based on algebra dimension:

- **d ≤ 5**: Uses the Hitzer closed-form inverse (Hitzer & Sangwine 2017). Each dimension has a specific formula built from conjugation and grade selection:
  - d=0: trivial
  - d=1: grade involute
  - d=2: Clifford conjugate
  - d=3: `x̄ * ~(x * x̄)` where x̄ is the Clifford conjugate
  - d=4, d=5: progressively more complex compositions

- **d ≥ 6**: Falls back to the Shirokov iterative algorithm (Theorem 4 of [arXiv:2005.04015](https://arxiv.org/abs/2005.04015)), which works in any algebra but is more expensive. Uses addition chains for efficient power computation.

Both paths produce a true inverse for **any** invertible multivector:

```
kingdon: (1 + e₁ + e₁₂ + e₁₂₃) * inv(…) = 1.0  ✓
```

## Square Root

### galaga — scalar only

`scalar_sqrt(x)` only works on pure scalar multivectors or plain numbers:

```python
scalar_sqrt(ga.scalar(9.0))  # → 3.0
scalar_sqrt(2.0)             # → 1.414...
scalar_sqrt(e1 + e2)         # ValueError: requires pure scalar
scalar_sqrt(rotor)           # ValueError: requires pure scalar
```

No multivector square root is provided. Non-scalar inputs raise `ValueError`.

### kingdon — Study number square root

`x.sqrt()` uses the Study number decomposition (Roelfs & De Keninck, [doi:10.1002/mma.8639](https://doi.org/10.1002/mma.8639)):

```python
a, bI = x.grade(0), x - x.grade(0)
bI_sq = bI * bI
normS = (a * a - bI_sq).e
cp = (0.5 * (a.e + normS**0.5))**0.5
return (0.5 * bI / cp) + cp
```

This works for any element that decomposes as `a + bI` where `a` is scalar and `bI` squares to a scalar — which includes rotors and PGA translators:

```
kingdon: sqrt(rotor)² = rotor                   ✓
kingdon: sqrt(1 + 0.5*e01)² = 1 + 0.5*e01       ✓  (PGA translator)
```

For pure scalars it falls back to `v**0.5` on the coefficient.

## Summary

| | galaga | kingdon |
|---|---|---|
| `|` operator | Doran–Lasenby inner | Symmetric inner (same math) |
| Inner product variants | 5, via `ip(a, b, mode)` dispatcher | 4 methods: `ip`, `lc`, `rc`, `sp` |
| Hestenes inner (kills scalars) | Yes (`hestenes_inner`) | No dedicated function |
| Computation model | Eager numpy loops over nonzero coefficients | JIT codegen, cached by type |
| exp | numpy-only, explicit branching | Backend-agnostic, injectable functions, `sinhc` formulation |
| log | Yes — built-in, handles Euclidean + hyperbolic + identity | No built-in — user composes manually with underlying library's inverse trig |
| Outer exp/sin/cos/tan | No | Yes |
| Inverse algorithm | Versor inverse: `~x / (x*~x)` | Hitzer (d≤5) / Shirokov (d≥6) |
| Inverse on versors | ✓ | ✓ |
| Inverse on general MVs | ✗ (silently wrong) | ✓ |
| Error on non-invertible | Raises if `x*~x ≈ 0` | Raises `ZeroDivisionError` |
| Scalar sqrt | ✓ | ✓ |
| Rotor / translator sqrt | ✗ (raises ValueError) | ✓ (Study number) |
| Symbolic support | Lazy expression trees (display) | Full symbolic via SymPy/PyTorch/etc |
