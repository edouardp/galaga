# Galaga Version 2 Planning

This is the planning document for the changes that should be incorporated into a future version 2 release of Galaga.

## Current issues to assess

### Presets

Notation presets are done via `Notation.hestenes()`, but blade presets are done via `b_sta()`. We should have one consistent approach, not multiple.

```python
alg = Algebra([1,-1,-1,-1], notation=Notation.hestenes(), blades=b_sta())
```

Consider a unified preset system, e.g.:

```python
alg = Algebra(1, 3, preset="sta")  # sets notation + blades + display_order together
```

### Mutating vs non-mutating API

`.name()`, `.symbolic()`, `.numeric()`, `.anon()` all mutate in-place and return `self`. `.eval()`, `.reveal()`, `.copy_as()` return new copies. This split is documented (ADR-028) but still a footgun — users can accidentally mutate a basis vector that's shared across their code. Assess whether v2 should make all configuration methods non-mutating (return copies), or at least make basis vectors immutable.

A lightweight fix: add an `_is_basis` flag to multivectors created by factory methods (`basis_vectors`, `basis_blades`, `pseudoscalar`, `locals`). Then `.name()` checks the flag — if set, it copies first and names the copy instead of mutating the original. Other mutating methods (`.symbolic()`, `.numeric()`, `.anon()`) can keep returning `self` since they don't change the identity of a shared object in the same confusing way. This protects against the common footgun (`e1.name("x")` silently renaming a shared basis vector) without changing the ergonomics of naming computed results.

### Deprecated `lazy=` parameter

`basis_vectors(lazy=...)`, `basis_blades(lazy=...)`, `pseudoscalar(lazy=...)`, `locals(lazy=...)`, and `blade(lazy=...)` all accept the deprecated `lazy=` kwarg alongside `symbolic=`. The `.lazy()` and `.eager()` methods on Multivector are also deprecated shims. v2 should remove these entirely.

### Commutator / anti-commutator naming

The current decisions around `½[A,B]` vs `[A,B]` for the commutator, Lie bracket, anti-commutator, and Jordan product all feel easy to get wrong. The ½ factor is a silent convention difference that users may not notice. Consider making the naming more explicit:

- `commutator(a, b)` — `ab - ba`
- `half_commutator(a, b)` — `½(ab - ba)`
- `anticommutator(a, b)` — `ab + ba`
- `half_anticommutator(a, b)` — `½(ab + ba)`

This would replace the current `lie_bracket` (which is `half_commutator`) and `jordan_product` (which is `half_anticommutator`) with names that make the ½ factor obvious.

### Dual (and similar) conventions

Dual can mean `mv * I` or `mv * I⁻¹` depending on the author. We currently implement complement-based duality (ADR-010), and the Poincaré/Hodge dual is deferred (ADR-049). Assess whether the current convention is the right default, and whether the docs clearly call out which convention is in use and how it differs from other libraries.

### `scalar_part` property vs `float()` conversion

`mv.scalar_part` returns `float(self.data[0])` unconditionally (no grade check). `float(mv)` raises `TypeError` for non-scalar MVs. These are two ways to get the grade-0 coefficient with different safety guarantees. Assess whether `scalar_part` should also guard, or whether the distinction is intentional and just needs better documentation.

### Physical constants on Algebra

`alg.pi`, `alg.e`, `alg.h`, `alg.hbar`, `alg.c`, `alg.tau`, `alg.sqrt2` are properties on `Algebra`. Physical constants (`h`, `hbar`, `c`) feel out of scope for a math library — they couple the algebra to specific unit systems. Assess whether these should move to a separate constants module or be removed in v2.

### `__eq__` uses `allclose` but `__hash__` uses exact bytes

This is documented and acknowledged as a trade-off, but it violates the Python invariant that `a == b` implies `hash(a) == hash(b)`. This can cause subtle bugs with sets and dicts. Assess whether v2 should use quantised hashing, or make `__eq__` exact and provide a separate `approx_eq()` / `isclose()` method.

### No `vector()` constructor for higher grades

`alg.vector(coeffs)` creates a 1-vector, but there's no `alg.bivector(coeffs)` or `alg.grade_k(k, coeffs)`. Users must manually construct higher-grade elements via basis blade arithmetic. Assess whether a general `alg.element(grade, coeffs)` or grade-specific constructors would be useful.

### SymPy integration path

SYMPY_PLAN.md outlines Option A (polymorphic coefficients) for v0.2. This is the biggest architectural change on the horizon. Key decisions still open:

- Should `Multivector.data` accept `list[sympy.Expr]` alongside `np.ndarray`?
- How to handle mixed symbolic/numeric operations?
- Should SymPy be optional at import time or only at use time?
- How does this interact with the existing expression tree layer (`galaga.expr`)?

### `ip()` dispatcher vs named functions

`ip(a, b, mode)` exists alongside `left_contraction()`, `right_contraction()`, etc. The design philosophy (ADR-003) says "two named functions beat one function with a mode flag." Assess whether `ip()` should be removed in v2 to stay consistent with this principle, or whether it serves a legitimate convenience role.

### Operator overload discoverability

`^` for outer product and `|` for inner product are non-obvious to Python users (these are bitwise XOR and OR). The library documents this, but new users consistently stumble. Assess whether v2 should provide alternative syntax (e.g. `a @ b` for geometric product, freeing `*` for scalar-only), or whether the current approach with clear documentation is sufficient.

### Error messages for algebra mismatch

`_check_same()` raises `ValueError` when algebras differ, but the message only shows `Cl(p,q)` — it doesn't show blade conventions or notation differences. Two algebras with the same signature but different blade conventions will silently interoperate (same `_sig`), which could produce confusing results. Assess whether algebra identity should also consider blade conventions.

### `display()` and `display_repr` mode

ADR-061 added `display_repr=True` on `Algebra` to make `repr()` show `name = expr = value`. This is useful for notebooks but changes the semantics of `repr()` globally for all MVs in that algebra. Assess whether this should be per-MV rather than per-algebra, or whether a context manager approach would be cleaner.

The name `display_repr` is bad — it describes the mechanism, not the intent. Better options:

- `display="full"` — show name = expression = value (default could be `display="value"`)
- `display="result"` — similar, emphasises that you're showing the evaluated result alongside the name
- `display_full=True` — boolean variant if we don't want a string enum

### Simplification is pattern-matching only

`simplify()` uses fixed-point pattern matching on expression trees (ADR-014). It cannot do algebraic simplification (trig identities, collection of like terms in symbolic coefficients). This is fine for the current numeric-first design, but will become a limitation once SymPy integration lands. Assess the boundary between galaga's simplifier and SymPy's.

### No serialisation / persistence

There's no way to save/load an `Algebra` or `Multivector` to disk. For notebooks that do expensive computations, this means re-running everything. Assess whether v2 should support pickle, JSON, or a custom format.

### Long names as the primary API

`ip()`, `op()`, `gp()` are too aggressively shortened. The primary API should use the long names (`inner_product`, `outer_product`, `geometric_product`), with the short names as aliases. This is consistent with the existing pattern where `wedge = op` and `rev = reverse`, but currently the short names are what users encounter first.

### Variadic products

Since we use functions rather than operators, products can accept more than two arguments. e.g. `geometric_product(a, b, c)` instead of forcing `gp(gp(a, b), c)`. This would be cleaner for sandwich products and rotor chains.

### Test coverage of edge cases in degenerate algebras

The Chisolm test suite (ADR-060) covers non-degenerate algebras thoroughly. Degenerate algebras (r > 0, e.g. PGA) have less systematic coverage — particularly around `inverse()`, `sqrt()`, `exp()`, and `log()` where null elements cause special cases. Assess whether a PGA/CGA-specific test suite is needed.


## Ideas from other GA libraries

Survey of design decisions across clifford, kingdon, ganja.js, galgebra, GeometricAlgebra.jl, Grassmann.jl, Klein (C++), and SymbolicGA.jl. Focus is on choices galaga v2 could adopt.

### Sparse storage (kingdon, GeometricAlgebra.jl)

Galaga uses dense `np.ndarray` of length 2ⁿ for all multivectors. Kingdon stores only nonzero blade keys+values. GeometricAlgebra.jl parameterises the grade set in the type, so a pure bivector only allocates bivector-sized storage.

Dense is simple and fast for small n, but wasteful for PGA/CGA where most elements are low-grade. Consider a hybrid: dense for n ≤ 5, sparse or grade-aware for larger algebras. This would also help if we ever want to support n > 8.

### Functional coefficient API (kingdon)

Kingdon provides `map(func)`, `filter(func)`, and iteration over coefficients. These are useful for batch operations (e.g. rounding, thresholding, applying a function to all coefficients). Galaga has no equivalent — users must access `.data` directly.

Consider adding:
- `mv.map(func)` — apply func to each nonzero coefficient, return new MV
- `mv.filter(func)` — zero out coefficients where func returns False
- `mv.coefficients()` — iterator of `(blade_index, value)` pairs

### Matrix representation (kingdon)

`asmatrix()` / `frommatrix()` converts between multivectors and their matrix representations. Useful for interfacing with linear algebra libraries, verifying identities, and educational notebooks. Galaga has no equivalent.

### Backend-agnostic coefficients (kingdon)

Kingdon's core MV operations work over any type supporting `+`, `-`, `*`, `/`. This enables PyTorch tensors (differentiable GA), SymPy expressions, batched numpy arrays, and even other kingdon algebras (for automatic differentiation). The `wrapper` parameter (`Algebra(3, 0, 1, wrapper=numba.njit)`) applies a decorator to all generated functions.

This is more ambitious than our SYMPY_PLAN.md Option A (polymorphic coefficients). Worth studying whether galaga's precomputed multiplication tables can be made coefficient-agnostic without losing the numpy fast path.

### Conformal model helpers (clifford)

Clifford's `ConformalLayout` provides `up(x)` (embed point in CGA), `down(x)` (project back), and `homo(x)` (homogenise). These are the most common CGA operations and having them built-in saves users from re-deriving the embedding formula. Galaga's `b_cga()` handles naming but not the geometric operations.

Consider adding CGA convenience methods, either on Algebra or as a separate module:
- `alg.up(point)` / `alg.down(mv)` / `alg.homo(mv)`
- Point/line/plane/circle/sphere constructors for PGA and CGA

### Geometric entity constructors (ganja.js, Klein)

Ganja.js uses user-defined patterns (`point = (x,y) => 1e12 + x*(-1e02) + y*1e01`). Klein goes further with dedicated types: `point`, `line`, `plane`, `rotor`, `translator`, `motor`. The call operator applies the sandwich product: `r(p)` applies rotor to point.

Galaga is algebra-first, not geometry-first. But for PGA/CGA users, having `alg.point(x, y, z)` and `alg.line(p, q)` would reduce boilerplate significantly. These could be provided by the preset system (only available when `preset="pga"` or `preset="cga"`).

### Trig functions on multivectors (clifford)

Clifford provides `sin`, `cos`, `tan`, `sinh`, `cosh`, `tanh` via Taylor expansion (configurable `max_order`). Also exposed as MV methods and via numpy dispatch (`np.sin(mv)`). Galaga only has `exp` and `log` with closed-form implementations for simple elements.

Taylor expansion is general but slow. Closed-form implementations for specific element types (bivectors, rotors) are better. Consider adding `sin`/`cos` for bivectors using the same B²-branching pattern as `exp`.

### Operator precedence workarounds (galgebra)

Python's fixed operator precedence means `a ^ b | c` parses as `a ^ (b | c)`, not `(a ^ b) | c`. Galgebra works around this with `def_prec()` and `GAeval()` which evaluate string expressions with custom precedence. This is a real pain point for GA in Python.

Not clear there's a good solution. Options:
1. Do nothing — document the precedence issue and recommend parentheses
2. Provide a string-based evaluator like galgebra (fragile, loses IDE support)
3. Use `@` for geometric product (higher precedence than `^` and `|`) — but `@` is left-associative and conventionally matrix multiply

### Multiple duality operations (GeometricAlgebra.jl, Grassmann.jl)

GeometricAlgebra.jl provides four distinct duality operations:
- `ldual(a)` / `rdual(a)` — metric-independent left/right complements (work in degenerate algebras)
- `hodgedual(a)` — metric-dependent Hodge dual
- `A * I` — pseudoscalar multiplication

Grassmann.jl similarly distinguishes Grassmann complements (metric-independent) from Hodge complements (metric-dependent).

Galaga has `complement`/`uncomplement` (metric-independent) and `dual`/`undual` (which raises in degenerate algebras). This is close to GeometricAlgebra.jl's approach but with less explicit naming. Consider whether v2 should:
- Rename `dual` → `hodge_dual` to make the metric-dependence obvious
- Keep `complement` as the metric-independent operation
- Add `ldual`/`rdual` if left vs right complement matters (it does in even dimensions)

### Differential operators (galgebra)

Galgebra's three-tier differential operator system (`Pdop`, `Sdop`, `Dop`) enables `grad * F`, `F * rgrad`, `grad ^ F`, `grad | F` etc. This is galgebra's killer feature — no other library does geometric calculus.

This is out of scope for galaga's numeric-first design, but if SymPy integration lands, a lightweight `grad` operator that works on symbolic multivector fields would be valuable. Defer to post-v2.

### Non-orthogonal metrics (galgebra)

Galgebra supports full symmetric metric tensors and symbolic coordinate-dependent metrics. All other libraries (including galaga) require diagonal metrics.

Non-orthogonal metrics are rare in practice but important for general relativity and differential geometry. If galaga ever supports them, the precomputed multiplication tables would need to become metric-tensor-aware rather than signature-based. This is a fundamental architecture change — defer unless there's demand.

### Codegen / JIT compilation (kingdon, GeometricAlgebra.jl)

Kingdon generates optimised Python functions per operation per type-number pair (bitmask of nonzero blades). First call pays codegen cost, subsequent calls are 2-3 orders of magnitude faster. GeometricAlgebra.jl's `@symbolicga` macro generates zero-allocation code at compile time.

Galaga's precomputed multiplication tables are already fast for small algebras. For larger algebras or hot loops, a `@compile` decorator (like kingdon's `@alg.register`) that generates specialised code could help. Lower priority than correctness and API issues.

### Visualisation (ganja.js, kingdon)

Ganja.js has first-class visualisation: pass multivectors to `graph()` and it renders points, lines, planes, circles based on grade and algebra type. Kingdon bridges to ganja.js via anywidget for Jupyter.

Galaga has no visualisation. For v2, consider a `galaga_viz` package (like `galaga_marimo`) that bridges to ganja.js or provides matplotlib-based 2D/3D PGA rendering. Not a core library concern but high impact for adoption.

### Named symbolic multivectors (galgebra)

`ga.mv('V', 'vector')` creates `V^x e_x + V^y e_y + V^z e_z` with auto-generated symbolic coefficients. This is extremely useful for deriving identities and proving theorems.

If SymPy integration lands, galaga should support something similar:
```python
V = alg.symbolic_vector('V')  # V_1 e₁ + V_2 e₂ + V_3 e₃
R = alg.symbolic_rotor('R')   # R_0 + R_12 e₁₂ + R_13 e₁₃ + R_23 e₂₃
```

### Grade-aware types (GeometricAlgebra.jl, Klein)

GeometricAlgebra.jl encodes grade in the type parameter, so the compiler knows a bivector only has grade-2 components. Klein goes further with named geometric types (`point`, `line`, `motor`).

Python can't do this at the type level without runtime overhead. But galaga could track grade metadata more aggressively (ADR-066 started this with `_grade` propagation). Consider whether v2 should expose grade as a public property and use it for optimisation (skip zero-grade components in products).

### `is_blade()` and `is_versor()` predicates (galgebra, clifford)

Galgebra 0.6.0 added `is_blade()` and `is_versor()`. Clifford has similar. Galaga has `is_scalar`, `is_vector`, `is_bivector`, `is_even`, `is_rotor`, `is_basis_blade` but no general `is_blade()` (is this MV a simple k-blade?) or `is_versor()`.

### Custom operator precedence via `@` (not yet used by any library)

No GA library currently uses Python's `@` operator (`__matmul__`). It has higher precedence than `*`, `^`, and `|`, and is left-associative. Potential mappings:
- `a @ b` for geometric product (frees `*` for scalar-only)
- `a @ b` for sandwich product
- `a @ b` for some other frequently-used operation

The precedence advantage is real: `a @ b ^ c` would parse as `(a @ b) ^ c`, which is usually what GA users want. Worth prototyping.

### Interoperability conventions (galgebra 0.6.0)

Galgebra 0.6.0 added `galgebra.interop.Cl(p, q, r)` explicitly designed for cross-library portability with ganja.js and kingdon conventions. As the GA ecosystem matures, having a standard interchange format (even just agreeing on constructor conventions and blade ordering) becomes more valuable.

Galaga already matches the `Algebra(p, q, r)` convention with r-first internal ordering. Consider whether v2 should also provide import/export to clifford and kingdon multivector formats for users who work across libraries.
