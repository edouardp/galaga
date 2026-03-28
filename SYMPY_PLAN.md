# SymPy Integration Plan

## Goal

Enable symbolic scalar coefficients in multivectors, so that expressions like
`cos(θ/2) + sin(θ/2) * e₁₂` can be manipulated algebraically — trig identities,
collection, factoring — without evaluating to floats.

## Current Architecture

```
Multivector.data = np.ndarray[float64]   # dense, length 2^n
```

All operations (gp, op, grade, etc.) use NumPy arithmetic on these arrays.
The symbolic layer (`galaga.symbolic`) is a separate expression tree that wraps
concrete `Multivector` objects and renders them with display names. It cannot
simplify or manipulate the underlying algebra.

## Proposed Architecture

### Option A: Polymorphic Coefficients (Recommended)

Make `Multivector.data` accept either NumPy arrays (fast numeric) or Python
lists of SymPy expressions (symbolic). The multiplication tables stay the same —
only the coefficient arithmetic changes.

```python
# Numeric (current behavior, unchanged)
alg = Algebra((1, 1, 1))
R = alg.rotor_from_plane_angle(e1^e2, np.pi/4)
# R.data = np.array([0.924, 0, 0, 0.383, ...])

# Symbolic (new)
from sympy import Symbol, cos, sin
theta = Symbol('θ')
R = alg.symbolic_rotor(e1^e2, theta)
# R.data = [cos(θ/2), 0, 0, sin(θ/2), ...]

# Operations just work — SymPy handles the coefficient math
result = R * e1 * ~R
# result.data contains SymPy expressions
# sympy.simplify(result.data[1]) → cos(θ)
```

#### Implementation Steps

1. **Abstract coefficient operations** — Replace direct NumPy calls in `gp()`,
   `op()`, etc. with a thin dispatch layer:
   ```python
   def _coeff_mul(a, b):
       return a * b  # works for both float and sympy.Expr

   def _coeff_add(a, b):
       return a + b
   ```
   NumPy broadcasting already handles float×float. SymPy expressions support
   the same `+`, `*` operators.

2. **Dual storage** — `Multivector.data` becomes either `np.ndarray` (numeric)
   or `list[sympy.Expr]` (symbolic). Add a `.is_symbolic` property.

3. **Symbolic constructors** on `Algebra`:
   ```python
   alg.sym_scalar(expr)           # symbolic scalar
   alg.sym_vector([a, b, c])      # symbolic vector
   alg.sym_rotor(plane, angle)    # cos(θ/2) - sin(θ/2)*B
   alg.sym_multivector(name)      # fully symbolic: a + b*e1 + c*e2 + ...
   ```

4. **Simplification** — Delegate to `sympy.simplify()` on each coefficient:
   ```python
   def simplify(mv):
       return Multivector(mv.algebra, [sympy.simplify(c) for c in mv.data])
   ```

5. **Display** — SymPy expressions render naturally via `str()` and `.latex()`.
   A multivector with symbolic coefficients would print as:
   ```
   cos(θ/2) + sin(θ/2)e₁₂
   ```

6. **Evaluation** — `.subs({θ: np.pi/4}).to_numeric()` converts back to a
   float-based multivector.

#### What Changes

| Component | Change Required |
|---|---|
| `Multivector.__init__` | Accept list or ndarray |
| `gp()`, `op()`, etc. | Replace `out[k] += sign * a[i] * b[j]` — already works if data is list of sympy exprs |
| `reverse()`, `involute()`, etc. | Multiply by ±1 — works for both |
| `grade()` | Indexing — works for both |
| `norm()`, `unit()` | Need `sympy.sqrt` — add dispatch |
| `inverse()` | Needs symbolic division — add dispatch |
| Display (`__str__`) | Format sympy exprs — `str()` already works |
| `__eq__`, comparisons | `sympy.Eq` vs `==` — needs care |

#### What Doesn't Change

- Multiplication tables (bitmask-based, precomputed)
- Grade masks
- Algebra construction
- The existing expression tree layer (`galaga.symbolic`)
- All existing numeric tests

### Option B: SymPy as External Layer

Keep `Multivector` numeric-only. Instead, build a separate `SymbolicMultivector`
class that uses SymPy internally and converts to/from `Multivector` for evaluation.

```python
from galaga.sympy_ext import SymbolicMultivector

theta = Symbol('θ')
R = SymbolicMultivector.rotor(alg, e1^e2, theta)
result = R * e1 * ~R
print(result)           # cos(θ)e₁ + sin(θ)e₂
print(result.subs(theta, pi/4).to_multivector())  # 0.707e₁ + 0.707e₂
```

This avoids touching the core but duplicates all the product logic.

### Option C: galgebra Integration

[galgebra](https://github.com/pygae/galgebra) is an existing SymPy-based GA
library. Instead of reimplementing symbolic GA, provide a bridge:

```python
from galaga.bridges.galgebra import to_galgebra, from_galgebra

ga_mv = to_galgebra(mv, ga3d)   # convert to galgebra object
# ... use galgebra's full symbolic engine ...
mv2 = from_galgebra(result)     # convert back
```

## Tradeoffs

| | Option A (Polymorphic) | Option B (Separate class) | Option C (galgebra bridge) |
|---|---|---|---|
| **Effort** | Medium — refactor core arithmetic | Medium — duplicate product logic | Low — just conversion functions |
| **API cleanliness** | Best — same `Multivector` type everywhere | Awkward — two parallel types | Awkward — different API for symbolic |
| **Performance** | NumPy path unchanged; symbolic path slower (expected) | NumPy path unchanged | Depends on galgebra |
| **Simplification power** | Full SymPy | Full SymPy | Full SymPy + galgebra extras |
| **Dependency** | Optional (sympy) | Optional (sympy) | Optional (galgebra + sympy) |
| **Risk** | Highest — touching core code | Medium | Low |
| **Maintenance** | One codebase | Two parallel implementations | External dependency |

## Recommendation

**Option A** for v0.2. The core arithmetic is already simple enough that making
it coefficient-agnostic is straightforward. The key insight: Python's `*` and `+`
operators already dispatch correctly for both `float` and `sympy.Expr`, so most
of the product code works unchanged.

The main work is:
1. Replacing `np.zeros(dim)` with `[sympy.S.Zero] * dim` for symbolic mode
2. Adding `sqrt`/`abs` dispatch for `norm()` and `inverse()`
3. Symbolic constructors on `Algebra`
4. Display formatting for symbolic coefficients

SymPy would be an **optional dependency** — the library continues to work
without it, and `import sympy` only happens when symbolic constructors are used.

## Milestones

1. **v0.1.1** — `simplify()` on expression trees (done — pattern-matching rules)
2. **v0.2.0** — Polymorphic coefficients with SymPy support
   - Symbolic scalar/vector/rotor constructors
   - All products work with symbolic coefficients
   - `.simplify()` delegates to SymPy
   - `.subs()` for substitution
   - `.to_numeric()` for evaluation
3. **v0.2.1** — galgebra bridge (optional, if there's demand)

## Open Questions

- Should symbolic multivectors support NumPy interop (`np.array(mv)`)? Probably
  not — force explicit `.to_numeric()`.
- How to handle `==` comparison? SymPy equality is structural, not numeric.
  Probably need `.equals()` method that calls `sympy.simplify(a - b) == 0`.
- Should `Algebra` auto-detect symbolic mode from constructor args, or require
  explicit `alg.sym_vector(...)` calls? Explicit is safer.
- Mixed symbolic/numeric operations (e.g., symbolic rotor × numeric vector)?
  Could auto-promote numeric to symbolic via `sympy.Float`.
