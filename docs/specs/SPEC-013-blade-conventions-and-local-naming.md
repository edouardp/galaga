# SPEC: Blade Conventions and Local Naming Redesign

## Status

Proposed — design document for discussion.

## Problem

The current system conflates three concerns:

1. **Display rendering** — how blades appear in LaTeX/unicode output
2. **Python variable names** — what users type in code
3. **Blade identity** — the mathematical object (bitmask + sign)

`BladeConvention` controls (1), and `locals()` tries to derive (2) from (1)
via heuristics (common prefix extraction, digit splitting). This breaks down
when display names don't map cleanly to Python identifiers, or when users
want different typing conventions than the display suggests.

### Specific pain points

- STA: display is `γ₀` but you type `g0` (default maps γ → g)
- `b_sta(sigmas=True)`: generates `s1`, `is1` — not discoverable from the
  vector naming pattern, and no real library uses this convention
- `b_default(subscripts="xyz")`: display is `e_{xy}` and local is `exy` —
  but a user might prefer `e_xy` or `bxy`
- PGA: `e₀` is the null vector, `e₁₂₃` is the pseudoscalar `I` — locals
  should reflect this

## Design Principles

1. **Display and typing are independent concerns** — display is for humans
   reading notebooks; typing is for humans writing code. They may differ.
2. **`prefix=` applies to all blades uniformly** — when you say `prefix="g"`,
   every blade gets a `g`-prefixed name. No surprise exceptions.
3. **Variable hints for special blades** — some blades have idiomatic names
   that differ from the prefix+subscript pattern (e.g. pseudoscalar `I`,
   quaternion `i, j, k`). These are declared as `variable_hints` on the
   convention and respected by `locals()`.
4. **Helpers make common cases one-liners** — you shouldn't need to understand
   the full override system to use standard conventions.
5. **Defaults match the most common textbook for that convention** — STA
   defaults match Doran & Lasenby; PGA defaults match Gunn/De Keninck.

## Architecture

### Layer 1: BladeConvention (display + variable hints)

Controls rendering. `subscripts` is the preferred API for generated blade
labels. `variable_hints` declares preferred Python variable names for
specific blades that have idiomatic names differing from prefix+subscript.

```python
@dataclass
class BladeConvention:
    prefix: str = "e"
    subscripts: list | None = None       # bare labels
    vector_names: list | None = None     # DEPRECATED in 2.0
    style: str = "compact"               # "compact" | "wedge" | "juxtapose"
    overrides: dict | None = None        # display overrides
    display_order: tuple | None = None
    variable_hints: dict | None = None   # NEW: preferred local names for specific blades
```

`variable_hints` maps blade keys (like `"pss"`, bitmask ints, or grade-index
tuples) to Python-safe variable names:

```python
variable_hints = {
    "pss": "I",          # pseudoscalar → I
}

# For quaternions:
variable_hints = {
    "e12": "i",
    "e13": "j",
    "e23": "k",
}

# For complex numbers:
variable_hints = {
    "e12": "i",
}
```

Variable hints are **independent of display overrides**. A blade can display
as σ₁ in LaTeX but have no variable hint (it just gets `prefix + subscript`),
or it can display as `e₁₂₃` but have a variable hint of `"I"`.

### Layer 2: Local naming (typing)

The system that derives Python variable names. Rules:

1. If a blade has a **variable hint** (from convention or call-site override),
   use that name.
2. Otherwise, use `prefix` + concatenated subscripts derived from the blade's
   index structure.
3. `prefix=` on `locals()` overrides the convention's default prefix.
4. Without `prefix=`, the local prefix defaults to the ASCII form of the
   display prefix (from `_PREFIX_MAP`, so `γ` → `g`).

**Key change from 1.x**: `prefix=` applies to ALL blades that don't have a
variable hint. Display overrides (like σ for bivectors) affect rendering only,
not local variable names.

### Layer 3: `locals()` parameters

```python
def locals(
    self,
    *,
    grades: list[int] | None = None,
    prefix: str | None = None,       # override local prefix for all non-hinted blades
    pss: str | None = None,          # shorthand for variable_hints={"pss": name}
    symbolic: bool | None = None,
) -> dict[str, Multivector]:
```

`prefix` overrides the generated local prefix for all blades that don't have
a variable hint. Every blade without a hint gets `prefix` + its canonical
subscript.

`pss` is syntactic sugar for the most common variable hint override — naming
the pseudoscalar. It's equivalent to passing a variable hint for the PSS blade
at call time. If the convention already declares a PSS variable hint,
`pss=` at call time wins.

```python
alg = Algebra(3)
alg.locals()              # e1, e2, e3, e12, e13, e23, e123
alg.locals(pss="I")       # e1, e2, e3, e12, e13, e23, I
alg.locals(prefix="b")    # b1, b2, b3, b12, b13, b23, b123
alg.locals(prefix="b", pss="I")  # b1, b2, b3, b12, b13, b23, I
```

## Common Cases and How They're Served

### Case 1: Standard 3D Euclidean (textbook default)

Most introductory texts use `e₁, e₂, e₃` with subscript notation.

```python
alg = Algebra(3)  # uses b_default() implicitly
e1, e2, e3 = alg.basis_vectors()
locals().update(alg.locals())  # e1, e2, e3, e12, e13, e23, e123
```

**Justification**: Doran & Lasenby, Dorst et al., Hestenes all use numbered
`e` basis vectors. This is the most common starting point.

### Case 2: Named axes (physics/engineering)

Electromagnetics, mechanics, and graphics often label axes x, y, z.

```python
alg = Algebra(3, blades=b_default(subscripts="xyz"))
ex, ey, ez = alg.basis_vectors()
locals().update(alg.locals(pss="I"))  # ex, ey, ez, exy, exz, eyz, I
```

**Justification**: Jackson (EM), Goldstein (mechanics), and most engineering
texts use x, y, z. The `e` prefix keeps them distinct from scalar variables.

### Case 3: Bare axis names (minimal notation)

Some pedagogical contexts prefer just `x, y, z` without prefix.

```python
alg = Algebra(3, blades=BladeConvention(
    prefix="",
    subscripts=["x", "y", "z"],
    variable_hints={"pss": "I"},
))
locals().update(alg.locals())  # x, y, z, xy, xz, yz, I
```

**Justification**: Spinors for Beginners (eigenchris), some graphics papers.
Works when there's no ambiguity with scalar variables.

### Case 4: STA — Spacetime Algebra

Doran & Lasenby use γ₀, γ₁, γ₂, γ₃ with juxtaposition for products.
The relative vectors σₖ = γₖγ₀ are bivectors. The pseudoscalar i = γ₀₁₂₃.

```python
sta = Algebra(1, 3, blades=b_sta(sigmas=True))
locals().update(sta.locals(pss="i"))
# g0, g1, g2, g3, g01, g02, g03, g12, g13, g23, g012, g013, g023, i
```

Since γ maps to `"g"` by default, no `prefix=` override is needed. The
display still renders σ₁, σ₂, σ₃ for the timelike bivectors in notebooks,
but typing uses the predictable `g` + subscript pattern. Only the pseudoscalar
gets a special name via `pss="i"`.

If you prefer the visual resemblance of `y` to γ:

```python
sta.locals(prefix="y", pss="i")
# y0, y1, y2, y3, y01, y02, y03, y12, y13, y23, y012, y013, y023, i
```

This matches how real STA code works across all GA libraries: people type
uniform prefix+subscript names and compute σ inline (`sigma_1 = g1 * g0`).

**Justification**: Survey of clifford, kingdon, ganja.js, galgebra,
GeometricAlgebra.jl, and Grassmann.jl shows that NO library uses `s1, is1`
style names. Everyone uses uniform prefix+subscript for all blades.

### Case 5: PGA — Projective Geometric Algebra

De Keninck and Gunn use e₀ (null), e₁, e₂, e₃, with pseudoscalar I.
The null vector is the "extra" dimension.

```python
pga = Algebra(3, 0, 1, blades=b_pga())
e0, e1, e2, e3 = pga.basis_vectors()
locals().update(pga.locals())  # e0, e1, e2, e3, e01, ..., I
```

`b_pga()` declares `variable_hints={"pss": "I"}` so the pseudoscalar is
named `I` by default without needing `pss=` at call time.

**Justification**: ganja.js, Klein, PGA4CS all use this convention.
Zero-indexed because e₀ is special (the null direction).

### Case 6: CGA — Conformal Geometric Algebra

Dorst uses e₁, e₂, e₃, eₒ (origin), e∞ (infinity) or e₊, e₋.

```python
cga = Algebra(4, 1, blades=b_cga())
e1, e2, e3, eo, ei = cga.basis_vectors()
locals().update(cga.locals())  # e1, e2, e3, eo, ei, e12, ..., I
```

Here `b_cga()` uses `variable_hints` for the null basis vectors (`eo`, `ei`)
and the pseudoscalar (`I`).

**Justification**: Dorst "GA for Computer Science", Hitzer, Hildenbrand.
The null basis names (eo, ei) are standard in the literature.

### Case 7: Quaternions

Hamilton's i, j, k with display order matching convention.

```python
alg = Algebra(0, 2, blades=b_quaternion())
locals().update(alg.locals())  # e1, e2, i, j, k
```

`b_quaternion()` declares `variable_hints={"e12": "i", "e13": "j", "e23": "k"}`
so the bivectors get their quaternion names automatically.

**Justification**: Standard quaternion convention. The variable hints give
idiomatic names without affecting how other blades are named.

### Case 8: Complex numbers

```python
alg = Algebra(0, 1, blades=b_complex())
locals().update(alg.locals())  # e1, i
```

`b_complex()` declares `variable_hints={"e12": "i"}` (or the PSS equivalent
for the 2D algebra).

## `locals(prefix=..., pss=...)` Behavior

```python
alg.locals(prefix="g")         # all blades use g + subscripts (except hinted ones)
alg.locals(pss="I")            # override the pseudoscalar name
alg.locals(prefix="g", pss="i")  # both at once
```

The rule is simple:
1. Blades with variable hints (from convention or call-site `pss=`) use
   their hinted name.
2. All other blades use `prefix` + canonical subscript.

```python
sta = Algebra(1, 3, blades=b_sta(sigmas=True))
sta.locals(pss="i")
# g0, g1, g2, g3, g01, g02, g03, g12, g13, g23, g012, g013, g023, i
#                 ^^^ these display as σ₁ σ₂ σ₃ — but typing is uniform g + subscript

pga = Algebra(3, 0, 1, blades=b_pga())
pga.locals()
# e0, e1, e2, e3, e01, e02, e03, e12, e13, e23, e012, e013, e023, e123, I
#                                                                         ^ from variable_hint
```

## Interaction Matrix

| Concern | Set by | When |
|---------|--------|------|
| LaTeX/Unicode rendering | `prefix` + `subscripts` + `overrides` | Convention construction |
| Display of σ, γ, etc. | `overrides` on convention | Convention construction |
| `locals()` key (default) | ASCII prefix + subscripts | `locals()` call |
| `locals()` key (override) | `locals(prefix=...)` | `locals()` call |
| Special blade names | `variable_hints` on convention | Convention construction |
| PSS name (call-site) | `locals(pss=...)` | `locals()` call |

## Variable Hints: Design Details

Variable hints are a lightweight mechanism for declaring "this blade has
an idiomatic Python name". They differ from display overrides:

| | Display overrides | Variable hints |
|---|---|---|
| Purpose | Control rendering | Control `locals()` keys |
| Affects LaTeX | Yes | No |
| Affects `locals()` | No (in new design) | Yes |
| Example | σ₁ for γ₁γ₀ | `"I"` for pseudoscalar |

This separation means:
- `b_sta(sigmas=True)` can render σₖ beautifully in notebooks
- `locals(prefix="g")` still gives you `g01, g02, g03` for typing
- Only explicitly hinted blades (like `pss="i"`) deviate from the prefix pattern

### Built-in variable hints by convention helper

| Helper | Variable hints | Default prefix | Effect |
|--------|----------------|----------------|--------|
| `b_default()` | None | `"e"` | All blades are e + subscript |
| `b_pga()` | `{"pss": "I"}` | `"e"` | PSS is `I` |
| `b_cga()` | `{"pss": "I", "eo": "eo", "ei": "ei"}` | `"e"` | Null vectors + PSS |
| `b_quaternion()` | `{"e12": "i", "e13": "j", "e23": "k"}` | `"e"` | Bivectors are i, j, k |
| `b_complex()` | `{"pss": "i"}` | `"e"` | PSS is `i` |
| `b_sta()` | `{"pss": "i"}` | `"g"` | γ→g; only PSS hinted |
| `b_gamma()` | None | `"g"` | γ→g; all prefix + subscript |
| `b_sigma()` | None | `"s"` | σ→s; all prefix + subscript |

### Default prefix mapping (ASCII)

| Display prefix | ASCII local prefix | Rationale |
|----------------|--------------------|-----------|
| `e` | `"e"` | Universal |
| `γ` | `"g"` | Standard code shorthand for gamma |
| `σ` | `"s"` | Standard |

## Migration Path

### 1.x (now)
- `variable_hints` available on `BladeConvention`
- `locals(prefix=...)` applies to all non-hinted blades
- `locals(pss=...)` as call-site hint override
- gamma ASCII prefix defaults to `"g"`

### 2.0
- `prefix=` is the only mechanism for local naming (no more deriving from
  display overrides)
- Remove `vector_names` (replaced by `subscripts`)

## Edge Cases

- `locals(prefix="")` with `subscripts=["x","y","z"]` → keys are `x`, `y`, `xy`, `xyz`
- Variable hints always win over prefix+subscript derivation
- `locals(pss="I")` when convention has `variable_hints={"pss": "omega"}`:
  call-site wins
- Collision: if prefix + subscript produces a Python keyword, sanitize with
  a leading underscore (`_class` etc.)
- Multi-character subscripts: `subscripts=["tx","ty","tz"]` → `etx`, `ety`,
  `etxty`, etc. Works but less ergonomic.
- Variable hints for non-existent blades are silently ignored.
- A blade can have BOTH a display override (for rendering) AND a variable hint
  (for locals). They're independent.

## Non-Goals

- Automatic inference of "good" variable names from arbitrary LaTeX
- Supporting every possible textbook convention as a built-in
- Making `locals()` keys match display names exactly (they serve different purposes)
- Deriving local variable names from display overrides (the 1.x behavior we're removing)
