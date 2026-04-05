# SPEC-010: Basis Blade Naming and Display System

## Status

Draft — specification for review before implementation.

## Problem

The current naming system has three intertwined concerns that need to be separated:

1. **Indexing** — What number does each basis vector get? (0-based vs 1-based, custom labels like ∞)
2. **Blade naming** — How are multi-grade blades named? (concatenation `e₁e₂`, compact subscript `e₁₂`, aliases like `I`)
3. **Display format** — How are blade products rendered? (`e₁₂` vs `e₁e₂` vs `e₁∧e₂`)

These are currently mixed together: the `names` parameter controls basis vector display, `BasisBlade.rename()` allows post-hoc overrides, and `blade()` lookup uses digit-parsing that assumes 1-based indexing. This creates issues #8 (0-based lookup fails) and #9 (no way to name all blades at construction).

## Design Principles

1. The tuple constructor `Algebra((0, 1, 1))` defines the metric. Naming is orthogonal to metric.
2. Every blade has three name variants: ASCII, Unicode, LaTeX. Always.
3. Partial overrides are allowed — unspecified blades fall back to a derivation rule.
4. `blade("name")` lookup must work with whatever naming scheme is active.
5. The system must handle 0-based indexing, custom symbols (∞, o), and compact subscripts.

## Architecture

Blade display is configured via a `BladeConvention` object passed to the `Algebra` constructor as `blades=`:

```python
from galaga import Algebra, b_gamma, b_pga, b_compact

Algebra(1, 3, blades=b_gamma())
Algebra(3, 0, 1, blades=b_pga())
Algebra((1,1,1), blades=b_compact(prefix="v"))
```

This cleanly separates metric (first arg) from display (`blades=`). The existing `names=` parameter is preserved as sugar — `names="gamma"` internally creates `b_gamma()`.

### BladeConvention

```python
@dataclass
class BladeConvention:
    vector_names: tuple | None = None   # per-vector (ascii, unicode, latex)
    blade_style: str = "juxtapose"      # "juxtapose", "compact", "wedge"
    blade_overrides: dict | None = None # specific blade renames
    index_base: int = 1                 # 0 or 1
    prefix: str = "e"                   # basis vector prefix
```

Three orthogonal concerns, one object:
- **`vector_names`** — what each basis vector is called
- **`blade_style`** — how multi-vector blades are derived from vector names
- **`blade_overrides`** — per-blade name overrides (e.g. pseudoscalar → `I`)

### Relationship to existing parameters

| Current | New equivalent | Status |
|---|---|---|
| `names="gamma"` | `blades=b_gamma()` | Sugar preserved, creates convention internally |
| `names="sigma"` | `blades=b_sigma()` | Sugar preserved |
| `names=(code, uni)` | `blades=BladeConvention(vector_names=...)` | Sugar preserved |
| `BasisBlade.rename()` | Still works | Post-hoc override, takes precedence |
| `Notation` | Unchanged | Controls operation rendering, not blade names |

## Specification

### 1. Blade Styles

```python
Algebra(3, blade_style="juxtapose")   # e₁e₂  (default, current behavior)
Algebra(3, blade_style="compact")     # e₁₂   (merged subscripts)
Algebra(3, blade_style="wedge")       # e₁∧e₂ (explicit wedge symbol)
```

Rules for `"compact"`:
- Only works when all basis vector names share a common prefix.
- Subscript digits/symbols are concatenated: `e₁` + `e₂` → `e₁₂`.
- For non-numeric subscripts (e.g. `eₒ`, `e∞`): concatenate as-is → `eₒ∞`.
- If the prefix differs across vectors, fall back to juxtaposition.

### 2. Blade Overrides

Override specific blade names via dict:

```python
blades=BladeConvention(blade_overrides={
    "e123": ("I", "I", "I"),          # (ascii, unicode, latex)
    "e12":  "B",                       # shorthand: same for all three
})
```

Keys are blade identifiers using internal code names. Values are:
- A string (applied to all three formats)
- A 2-tuple `(ascii, unicode)` — LaTeX derived from unicode
- A 3-tuple `(ascii, unicode, latex)` — full control

### 3. Blade Lookup

`blade("name")` searches in this order:

1. Exact match against any name variant (ascii, unicode, latex) of any blade
2. Parse as concatenation of basis vector code names (existing `_parse_blade_name`)
3. Parse as prefix + digits, using the active `index_base` (0 or 1)

This fixes issue #8: when `index_base=0`, `blade("e01")` correctly parses as e₀ ∧ e₁.

### 4. Built-in Convention Factories

| Factory | Vectors | Style | Overrides | Index | Use case |
|---|---|---|---|---|---|
| `b_default()` | e₁, e₂, … | juxtapose | — | 1 | Current behavior |
| `b_compact()` | e₁, e₂, … | compact | — | 1 | clifford-style |
| `b_e0()` | e₀, e₁, … | compact | — | 0 | 0-based compact |
| `b_gamma()` | γ₀, γ₁, … | juxtapose | — | 0 | STA vectors |
| `b_sigma()` | σ₁, σ₂, … | juxtapose | — | 1 | Pauli algebra |
| `b_sigma_xyz()` | σₓ, σᵧ, σ_z | juxtapose | — | 1 | Pauli (xyz) |
| `b_pga()` | e₀, e₁, … | compact | PSS → `I` | 0 | Standard PGA |
| `b_sta()` | γ₀, γ₁, … | juxtapose | σ₁/σ₂/σ₃, PSS → `i` | 0 | Spacetime algebra |
| `b_cga()` | e₁…e₃, eₒ, e∞ | compact | null pair → `E₀`, PSS → `I` | 1 | Conformal GA |

Factories accept optional keyword overrides:

```python
b_compact(prefix="v")           # v₁₂ instead of e₁₂
b_gamma(start=1)                # γ₁, γ₂, γ₃, γ₄ (1-based)
b_pga(pseudoscalar="𝐈")         # custom pseudoscalar name
```

### 5. Interaction with `names=`

The existing `names=` parameter continues to work. When both `names=` and `blades=` are provided, `blades=` takes precedence. When only `names=` is given:

- String presets (`"gamma"`, `"sigma"`, etc.) create the corresponding convention factory internally
- Tuple form `(code, unicode)` or `(code, unicode, latex)` creates a `BladeConvention` with those vector names and default blade_style

### 6. Post-hoc Renaming

`get_basis_blade(mv).rename(...)` and `BasisBlade.rename()` continue to work. They modify the live `BasisBlade` object, overriding whatever the convention set. This is the escape hatch for one-off renames that don't fit any convention.

## Examples

```python
# PGA — one parameter
pga = Algebra(3, 0, 1, blades=b_pga())
e0, e1, e2, e3 = pga.basis_vectors()
print(e0 ^ e1)       # → e₀₁
print(e1 ^ e2 ^ e3)  # → I

# STA — gamma + sigma aliases
sta = Algebra(1, 3, blades=b_sta())
g0, g1, g2, g3 = sta.basis_vectors()
print(g0)             # → γ₀
print(g0 * g1)        # → σ₁

# Custom: Julia-style v prefix
alg = Algebra(3, blades=b_compact(prefix="v"))
v1, v2, v3 = alg.basis_vectors()
print(v1 ^ v2)        # → v₁₂

# Backward compatible
sta = Algebra(1, 3, names="gamma")  # still works, same as blades=b_gamma()
```

## Migration

- All existing code continues to work unchanged.
- `names=` is preserved as sugar.
- `BasisBlade.rename()` is preserved.
- `Notation` is unchanged (controls operations, not blades).
- `blades=` is the new recommended way to configure blade display.
- Issue #8 is fixed by `index_base` in `BladeConvention`.
- Issue #9 is addressed by `blade_overrides`.

## Cross-Library Conventions

Based on the survey in `docs/ga-library-conventions.md`, every major library's convention is reproducible:

| Convention | Configuration |
|---|---|
| ganja.js (`e01, e12`) | `blades=b_e0()` |
| clifford (`e12, e13`) | `blades=b_compact()` |
| kingdon (`e01, e12`) | `blades=b_e0()` |
| galaga current (`e₁e₂`) | `blades=b_default()` or omit |
| galgebra (`e1^e2`) | `blades=BladeConvention(blade_style="wedge")` |
| GeometricAlgebra.jl (`v12`) | `blades=b_compact(prefix="v")` |
| Grassmann.jl (`v₁₂`) | `blades=b_compact(prefix="v")` |
| STA (γ₀γ₁, σ₁) | `blades=b_sta()` |
| PGA (e₀₁, I) | `blades=b_pga()` |
| CGA (e₁₂, eₒ∞, I) | `blades=b_cga()` |

## Open Questions

1. Should `b_compact()` be the default instead of `b_default()`? Compact subscripts are more conventional in GA literature, but it's a breaking change to display output.
2. Should `blade_overrides` accept bitmask ints as keys (e.g. `{0b011: "B"}`) in addition to strings?
3. Should there be a `b_custom()` factory that takes a full dict of all 2^n blade names?
