<!-- rumdl-disable MD013 -->

# GA Library Operations Survey

Tested across 7 libraries in Cl(3,0,0) unless noted. All results verified by running actual code.

## `~` Operator (Tilde)

**ganja.js is the outlier here.** Most libraries map `~` to reverse; ganja maps it to Clifford conjugation.

| Library | `~` means | `~(1+e1+e12+e123)` |
|---|---|---|
| ganja.js | **Conjugation** | `1 - e1 - e12 + e123` |
| clifford | Reverse | `1 + e1 - e12 - e123` |
| kingdon | Reverse | `1 + e1 - e12 - e123` |
| galaga | Reverse | `1 + e1 - e12 - e123` |
| galgebra | Reverse | `1 + e1 - e12 - e123` |
| GeometricAlgebra.jl | Reverse | `1 + v1 - v12 - v123` |
| Grassmann.jl | Reverse | `1 + v1 - v12 - v123` |

Sign pattern reference:

| Grade | Reverse `(-1)^(k(k-1)/2)` | Involute `(-1)^k` | Conjugate `(-1)^(k(k+1)/2)` |
|---|---|---|---|
| 0 | +1 | +1 | +1 |
| 1 | +1 | -1 | -1 |
| 2 | -1 | +1 | -1 |
| 3 | -1 | -1 | +1 |

ganja.js provides `.Reverse`, `.Involute`, and `.Conjugate` as explicit methods. The `~` operator is just wired to conjugation instead of reverse.

## `|` Operator (Inner Product)

Libraries disagree on which inner product `|` maps to:

| Library | `|` maps to | `scalar \| vector` | `vec \| biv` | `biv \| vec` |
|---|---|---|---|---|
| ganja.js | Hestenes (kills scalars) | 0 | e2 | -e2 |
| clifford | Hestenes (kills scalars) | 0 | e2 | -e2 |
| kingdon | Doran–Lasenby (includes scalars) | 5e1 | e2 | -e2 |
| galaga | Doran–Lasenby (includes scalars) | 5e₁ | e₂ | -e₂ |
| galgebra | Hestenes (kills scalars) | 0 | e2 | -e2 |
| GeometricAlgebra.jl | Left contraction | 0 | v2 | 0 |
| Grassmann.jl | Right contraction | 0 | 0 | v2 |

Seven libraries, four different meanings for `|`.

For vector·vector and vector·bivector, all libraries agree. The difference only shows when a scalar is involved.

### Available Inner Product Variants

| Variant | ganja.js | clifford | kingdon | galaga | galgebra | GeometricAlgebra.jl | Grassmann.jl |
|---|---|---|---|---|---|---|---|
| Left contraction | `<<` | `.lc()` | `.lc()` | `left_contraction()` | `<` | `⨼` | `<` |
| Right contraction | `>>` | — | `.rc()` | `right_contraction()` | `>` | `⨽` | `>`, `\|`, `⋅` |
| Hestenes inner | `\|` | `\|` | — | `hestenes_inner()` | `\|` | — | — |
| Doran–Lasenby | — | — | `\|` | `\|`, `doran_lasenby_inner()`, `dorst_inner()` | — | `⋅` | — |
| Scalar product | `.Dot` | — | `.sp()` | `scalar_product()` | — | `⊙` | — |
| Conventional left | — | — | — | — | — | — | `<<` |
| Conventional right | — | — | — | — | — | — | `>>` |

Grassmann.jl's `<`/`>` (Grassmann contractions) apply a reverse to the left operand before contracting, while `<<`/`>>` (conventional contractions) do not. For vectors and bivectors these agree on left contraction, but right contraction differs by sign on some terms (e.g. `biv > vec` gives `+v2` in Grassmann style vs `-v2` in conventional).

### Left Contraction Comparison

All libraries agree on left contraction results:

| Test | galaga | kingdon | clifford | galgebra | ganja.js `<<` | GeometricAlgebra.jl `⨼` | Grassmann.jl `<` |
|---|---|---|---|---|---|---|---|
| vec ⌋ vec | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| vec ⌋ biv | e₂ | e₂ | e₂ | e₂ | e₂ | v₂ | v₂ |
| biv ⌋ vec | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| vec ⌋ tri | e₂₃ | e₂₃ | e₂₃ | e₂₃ | e₂₃ | v₂₃ | v₂₃ |
| biv ⌋ biv | -1 | -1 | -1 | -1 | -1 | -1 | **+1** |
| scl ⌋ vec | 5e₁ | 5e₁ | 5e₁ | 5e₁ | **0** | 5v₁ | 5v₁ |

Differences:

- **ganja.js** `<<` kills scalars (Hestenes-style left contraction), all others pass scalars through.
- **Grassmann.jl** `<` gives `+1` for `biv < biv` where all others give `-1`. This is because Grassmann's `<` applies a reverse to the left operand: `⟨ã·b⟩` instead of `⟨a·b⟩`. For `e12 < e12`: reverse of `e12` is `-e12`, so `(-e12)·(e12) = +1`.

### Right Contraction Comparison

| Test | galaga | kingdon | galgebra | GeometricAlgebra.jl `⨽` | Grassmann.jl `>` | Grassmann.jl `>>` |
|---|---|---|---|---|---|---|
| vec ⌊ vec | 0 | 0 | 0 | 0 | 0 | 0 |
| vec ⌊ biv | 0 | 0 | 0 | 0 | 0 | 0 |
| biv ⌊ vec | -e₂ | -e₂ | -e₂ | -v₂ | **+v₂** | -v₂ |
| vec ⌊ tri | 0 | 0 | 0 | 0 | 0 | 0 |
| biv ⌊ biv | -1 | -1 | -1 | -1 | **+1** | -1 |
| scl ⌊ vec | 0 | 0 | 0 | — | 0 | 0 |

Differences:

- **Grassmann.jl** `>` gives opposite signs on `biv ⌊ vec` and `biv ⌊ biv` compared to all other libraries, again due to the reverse on the left operand. Grassmann's `>>` (conventional) matches the others.
- **clifford** and **ganja.js** do not have a right contraction operator.

## Exponential

All libraries implement bivector exp via `cos(|B|) + sin(|B|)/|B| * B` for Euclidean bivectors. All produce identical numerical results.

| Library | Syntax | Handles null (B²=0) | Handles hyperbolic (B²>0) | Backend-agnostic |
|---|---|---|---|---|
| ganja.js | `Math.E**(B)` | ✓ | ✓ | No (JS only) |
| clifford | `np.e**(B)` | ✓ | ✓ | No (numpy) |
| kingdon | `B.exp()` | ✓ | ✓ | ✓ (injectable cosh/sinhc/sqrt) |
| galaga | `exp(B)` | ✓ | ✓ | No (numpy) |
| galgebra | `B.exp(hint)` | ✓ | ✓ (needs hint='+') | No (sympy) |
| GeometricAlgebra.jl | `exp(B)` | ✓ | ✓ | No (Julia native) |
| Grassmann.jl | `exp(B)` | ✓ | ✓ | No (Julia native) |

## Logarithm

| Library | Has log | Syntax |
|---|---|---|
| ganja.js | ✓ | `R.Log` |
| clifford | ✓ | `clifford.tools.log_rotor(R)` |
| kingdon | ✗ | Manual via underlying library's inverse trig |
| galaga | ✓ | `log(R)` |
| galgebra | ✗ | — |
| GeometricAlgebra.jl | ✓ | `log(R)` |
| Grassmann.jl | ✓ | `log(R)` |

## Inverse

| Library | Algorithm | General MV inverse | Silent failure on non-versors |
|---|---|---|---|
| ganja.js | General (works on all) | ✓ | No |
| clifford | General (Shirokov-based) | ✓ | No |
| kingdon | Hitzer (d≤5) / Shirokov (d≥6) | ✓ | No |
| galaga | General (Hitzer d≤5, Shirokov d≥6) | ✓ | No |
| galgebra | Versor only (`~x/(x*~x)`) | ✗ (raises TypeError) | No (raises) |
| GeometricAlgebra.jl | General | ✓ | No |
| Grassmann.jl | Versor only | ✗ (raises "undefined") | No (raises) |

galgebra and Grassmann.jl are the only libraries that cannot invert arbitrary multivectors — both raise errors rather than failing silently.

## Square Root

| Library | Has MV sqrt | Rotor sqrt | Method |
|---|---|---|---|
| ganja.js | ✗ | ✗ | — |
| clifford | ✗ | ✗ | — |
| kingdon | ✓ | ✓ | Study number decomposition |
| galaga | ✓ | ✓ | Study number decomposition |
| galgebra | ✗ | ✗ | — |
| GeometricAlgebra.jl | ✓ | ✓ | `sqrt(R)` |
| Grassmann.jl | ✓ | ✓ | `sqrt(R)` |

## Outer Exponential

| Library | outerexp | outersin | outercos | outertan |
|---|---|---|---|---|
| ganja.js | ? | ? | ? | ? |
| clifford | ✗ | ✗ | ✗ | ✗ |
| kingdon | ✓ | ✓ | ✓ | ✓ |
| galaga | ✓ | ✓ | ✓ | ✓ |
| galgebra | ✗ | ✗ | ✗ | ✗ |
| GeometricAlgebra.jl | ✗ | ✗ | ✗ | ✗ |

## Duality

| Library | `dual()` in PGA | Complement | Hodge | Polarity |
|---|---|---|---|---|
| ganja.js | `.Dual` (works) | — | — | — |
| clifford | `dual()` (works) | — | — | — |
| kingdon | Auto-selects hodge for r=1 | — | `hodge()`/`unhodge()` | `polarity()`/`unpolarity()` |
| galaga | Raises (PSS not invertible) | `complement()`/`uncomplement()` | — | — |
| galgebra | — | — | — | — |
| GeometricAlgebra.jl | `ldual()`/`rdual()` | — | `hodgedual()` | — |
| Grassmann.jl | `⋆` (Hodge star) | — | `⋆` | — |

## Sandwich Product

All libraries agree on results. Syntax varies:

| Library | Dedicated sandwich | Manual `R*v*rev(R)` |
|---|---|---|
| ganja.js | `R >>> x` | `R * x * ~R` (but `~` is conjugate, not reverse — use `R * x * R.Reverse`) |
| clifford | — | `R * x * ~R` |
| kingdon | `R >> x` or `R.sw(x)` | `R * x * ~R` |
| galaga | `sandwich(R, x)` or `sw(R, x)` | `R * x * ~R` |
| galgebra | — | `R * x * R.rev()` |
| GeometricAlgebra.jl | `sandwich_prod(R, x)` | `R * x * ~R` |
| Grassmann.jl | `x ⊘ R` or `R >>> x` | `~R * x * R` (note: `>>>` uses `conj(R)*x*R`, and `⊘` uses `conj(R)⁻¹*x*R`) |

Note on `~` in manual sandwich: since ganja.js maps `~` to Clifford conjugation (not reverse), writing `R * x * ~R` in ganja.js gives a different result than in other libraries. Use `R * x * R.Reverse` for the correct manual sandwich. Similarly, Grassmann.jl's `>>>` uses Clifford conjugate rather than reverse, matching its documented definition `η >>> ω = η*ω*conj(η)⁻¹`.

## Commutator and Anticommutator

All results verified in Cl(3,0,0) with `a = e12`, `b = e23`. The raw algebraic result is `e12*e23 - e23*e12 = 2*e13`.

### Built-in Support

| Library | Has commutator | Has anticommutator | Syntax |
|---|---|---|---|
| ganja.js | ✗ | ✗ | Manual only |
| clifford | ✓ | ✓ | `a.commutator(b)`, `a.anticommutator(b)` |
| kingdon | ✓ | ✓ | `a.cp(b)`, `a.acp(b)` |
| galaga | ✓ | ✓ | `commutator(a,b)`, `anticommutator(a,b)`, `lie_bracket(a,b)`, `jordan_product(a,b)` |
| galgebra | ✗ | ✗ | Manual only |
| GeometricAlgebra.jl | ✗ | ✗ | Manual only |
| Grassmann.jl | ✗ | ✗ | Manual only |

### Commutator Scaling Convention

The key disagreement: does "commutator" mean `ab - ba` or `½(ab - ba)`?

| Library | `commutator(e12, e23)` | Definition | Factor |
|---|---|---|---|
| clifford | `e13` | ½(ab - ba) | ½ |
| kingdon | `e13` | ½(ab - ba) | ½ |
| galaga `commutator()` | `2*e13` | ab - ba | 1 |
| galaga `lie_bracket()` | `e13` | ½(ab - ba) | ½ |

clifford and kingdon both use the ½-scaled convention for their "commutator product" — matching the GA tradition where bivectors form a Lie algebra with clean structure constants. galaga splits this into two functions: `commutator()` gives the raw `ab - ba` (matching the standard mathematical definition), while `lie_bracket()` gives the ½-scaled version.

### Anticommutator Scaling Convention

| Library | `anticommutator(e1, e1)` | Definition | Factor |
|---|---|---|---|
| clifford | `1` | ½(ab + ba) | ½ |
| kingdon | `1` | ½(ab + ba) | ½ |
| galaga `anticommutator()` | `2` | ab + ba | 1 |
| galaga `jordan_product()` | `1` | ½(ab + ba) | ½ |

The same pattern: clifford and kingdon include the ½ factor in their anticommutator; galaga separates the raw operation from the ½-scaled Jordan product.

### Summary of Naming Across Libraries

| Operation | clifford | kingdon | galaga |
|---|---|---|---|
| ab - ba | (no function) | (no function) | `commutator(a, b)` |
| ½(ab - ba) | `.commutator()` | `.cp()` | `lie_bracket(a, b)` |
| ab + ba | (no function) | (no function) | `anticommutator(a, b)` |
| ½(ab + ba) | `.anticommutator()` | `.acp()` | `jordan_product(a, b)` |

galaga is the only library that exposes all four variants as named functions. clifford and kingdon each expose only the ½-scaled pair. The remaining libraries (ganja.js, galgebra, GeometricAlgebra.jl, Grassmann.jl) have no built-in commutator at all — users compute `a*b - b*a` manually.

## Regressive Product

| Library | Has regressive | Meet/Join | Implementation |
|---|---|---|---|
| ganja.js | ✓ (`&`) | — | Built-in |
| clifford | ✓ (`.vee()`) | ✓ (`.meet()`, `.join()`) | Via dual |
| kingdon | ✓ (`&` or `.rp()`) | — | Via sign tables in codegen |
| galaga | ✓ (`regressive_product()`, `metric_regressive_product()`) | ✓ (`meet`, `join`) | Via complement (metric-independent); also metric-based via dual |
| galgebra | ✗ | ✗ | — |
| GeometricAlgebra.jl | ✓ (`∨` or `antiwedge()`) | — | Built-in |
| Grassmann.jl | ✓ (`∨`) | — | Built-in |

## Unique Features by Library

### ganja.js

- Visualization (graphs, animations)
- `~` is conjugation (not reverse)
- Inline code transformation for `1e1` syntax

### clifford

- Numba JIT support
- Sparse multivector support
- Conformal model helpers (`ConformalLayout`)
- `log_rotor()` in `clifford.tools`
- `meet()`, `join()` methods
- `commutator()`, `anticommutator()` methods (½-scaled)
- Taylor expansion module (`sin`, `cos`, `tan`, `sinh`, `cosh`, `tanh` on MVs)

### kingdon

- Backend-agnostic (numpy, PyTorch, SymPy)
- JIT codegen with CSE
- `map()`, `filter()`, `itermv()` for functional coefficient manipulation
- `asmatrix()`/`frommatrix()` for matrix representations
- `@alg.register` for compiling custom expressions

### galaga

- Eager immutable values with optional expression provenance and shared
  ASCII/Unicode/LaTeX semantic rendering
- Immutable `Notation` rules: conventional, functional long/short, Hestenes,
  Doran–Lasenby, and Lengyel presentations
- Explicit Doran–Lasenby, Hestenes, metric, scalar, contraction, and RGA
  interior products; no unqualified `ip()` dispatcher
- `dorst_inner` alias for `doran_lasenby_inner`
- Left/right complements and metric Hodge/weight dual families
- `meet`/`join` aliases for regressive/outer products
- Unscaled `commutator`, `lie_bracket`, `anticommutator`, and
  `jordan_product`, plus explicit half-scaled forms
- Type predicates: `is_scalar`, `is_vector`, `is_bivector`, `is_even`, `is_rotor`, `is_basis_blade`
- Grade utilities: `grades()`, `even_grades()`, `odd_grades()`
- Immutable `BladeConvention` builders for indexed, Euclidean, STA, PGA,
  native-null/orthogonal CGA, Lengyel CGA/RGA, complex, quaternion, and
  exterior presentations
- 3 blade styles: `"compact"` (`e₁₂`), `"juxtapose"` (`e₁e₂`), `"wedge"` (`e₁∧e₂`)
- Complete presets for metric, blade vocabulary, display order, notation, and
  semantic model roles, with independent component overrides
- Native Gram matrices, including actual oblique and native-null bases
- `ConformalModel` and `RigidModel` validated semantic layers
- Numeric square root, exponential, logarithm, and outer transcendental
  families with explicit real domains
- Conservative immutable expression simplification rather than a general CAS

### galgebra

- Full symbolic computation via SymPy
- Differential operators (grad, div, curl)
- Non-orthogonal metrics
- LaTeX output
- Coordinate-dependent multivector functions

### GeometricAlgebra.jl

- Grade-aware types (only stores needed components)
- Compile-time symbolic codegen via MiniCAS
- `@symbolicga` macro for zero-allocation code generation
- Extensive `BasisDisplayStyle` customization
- Three duality operations (`ldual`, `rdual`, `hodgedual`) plus `flipdual`, `invhodgedual`
- `sandwich_prod()` built-in
- `outermorphism()` for linear maps

### Grassmann.jl

- Extensive differential geometry support (manifolds, fiber bundles, connections)
- `D"..."` diagonal metric for arbitrary signatures including degenerate
- Projective geometry via `∅` (origin point) — different model from standard PGA
- Named basis via `@basis (t=+1, x=-1)`
- `⋅` is scalar product; `<`/`>` for left/right contraction
- `exp`, `log`, `sqrt` all built-in
- `⋆` for Hodge star duality

## Complex Coefficients (Complexified Clifford Algebras)

Tested with `v = (1+2i)e1 + (3+4i)e2` in Cl(2,0,0). Correct result: `v*v = -10+28i`.

| Library | Complex support | Result |
|---|---|---|
| ganja.js | ✗ (Float32Array, no complex type in JS) | N/A |
| clifford | ✓ (numpy complex arrays) | `-10+28j` ✓ |
| kingdon | ✓ (type-agnostic, accepts any coefficient) | `-10+28j` ✓ |
| galaga | ✗ (coerces via `float()`, rejects complex) | `TypeError` |
| galgebra | ✓ (via SymPy `I`) | `-10+28*I` ✓ |
| GeometricAlgebra.jl | ✓ (Julia native `Complex{T}`) | `-10+28im` ✓ |
| Grassmann.jl | ✓ (Julia native `Complex{T}`) | `-10+28im` ✓ |
