# SPEC-010: Basis Blade Naming and Display System

## Status

Accepted — implemented on `feature/blade-convention` branch.

## Problem

The current naming system has three intertwined concerns mixed into one `names` parameter:

1. **Indexing** — What number does each basis vector get? (0-based vs 1-based, custom labels like ∞)
2. **Blade naming** — How are multi-grade blades named? (concatenation `e₁e₂`, compact subscript `e₁₂`, aliases like `I`)
3. **Display format** — How are blade products rendered? (`e₁₂` vs `e₁e₂` vs `e₁∧e₂`)

Additionally, `blade()` lookup uses digit-parsing that assumes 1-based indexing (issue #8), and there's no way to name all blades at construction (issue #9).

## Design Principles

1. The first argument defines the metric. Display is orthogonal — controlled entirely by `blades=`.
2. Every blade has three name variants: ASCII, Unicode, LaTeX. Always.
3. Partial overrides are allowed — unspecified blades fall back to a derivation rule.
4. `blade("name")` lookup must work with whatever naming scheme is active.
5. One parameter, one concern: `blades=` handles all blade display.

## Constructor

```python
Algebra(p_or_signature, q=0, r=0, *, blades=None, repr_unicode=True, notation=None)
```

The `names=` parameter is removed. All blade display configuration goes through `blades=`:

```python
from galaga import Algebra, b_gamma, b_pga, b_sta

Algebra(1, 3, blades=b_gamma())
Algebra(3, 0, 1, blades=b_pga())
Algebra((1,1,1), blades=b_default(style="compact"))
```

When `blades=None` (default), `b_default()` is used internally — compact style, 1-based, `e` prefix.

`repr_unicode` controls whether `__repr__` uses unicode or ascii blade names. Default is `True` (unicode). This is orthogonal to the `BladeConvention` — it selects which name variant to use during non-LaTeX rendering.

## BladeConvention

```python
@dataclass
class BladeConvention:
    vector_names: tuple | None = None   # see format below
    style: str = "compact"              # "juxtapose", "compact", "wedge"
    overrides: dict | None = None       # per-blade name overrides (metric-role keys)
    index_base: int = 1                 # 0 or 1
    prefix: str = "e"                   # basis vector prefix
```

Three orthogonal concerns, one object:
- **`vector_names`** — what each basis vector is called
- **`style`** — how multi-vector blades are derived from vector names
- **`overrides`** — per-blade name overrides using metric-role keys (see Blade Overrides section)

`vector_names` format — an iterable of n entries, one per basis vector. Each entry is either:
- A string (used for all three formats: ascii, unicode, latex)
- A 3-tuple `(ascii, unicode, latex)` for full control

If `None`, names are generated from `prefix` and `index_base` (e.g. `e₁, e₂, …`).

### Building blades

The Algebra constructor calls `build_blades(convention, signature)` passing the metric signature. This is needed to:
- Resolve metric-role override keys (`"+1-1"` → bitmask) against the actual signature
- Validate that overrides reference vectors that exist in the algebra

If an override references a vector that doesn't exist (e.g. `"+3"` in a 2D algebra), `build_blades` raises `ValueError`.

### Blade name generation by style

`build_blades` generates three name variants (ascii, unicode, latex) for each blade:

- `"compact"`: merge subscripts under a shared prefix → ascii `e12`, unicode `e₁₂`, latex `e_{12}`
- `"juxtapose"`: concatenate vector names → ascii `e1e2`, unicode `e₁e₂`, latex `e_{1} e_{2}`
- `"wedge"`: join with wedge symbol → ascii `e1^e2`, unicode `e₁∧e₂`, latex `e_{1} \wedge e_{2}`

LaTeX rendering reads from `BasisBlade.latex_name` as before — no changes to `latex_build.py`.

## Blade Styles

```python
Algebra(3, blades=b_default(style="juxtapose"))   # e₁e₂
Algebra(3, blades=b_default(style="compact"))      # e₁₂   (default)
Algebra(3, blades=b_default(style="wedge"))        # e₁∧e₂
```

Rules for `"compact"`:
- Only works when all basis vector names share a common prefix.
- The prefix is the longest common leading substring of all unicode vector names (e.g. `e` from `e₁, e₂`; `γ` from `γ₀, γ₁`). The subscript is everything after the prefix.
- Subscripts are concatenated: `e` + `₁` + `₂` → `e₁₂`.
- For non-numeric subscripts (e.g. `eₒ`, `e∞`): concatenate as-is → `eₒ∞`.
- If no common prefix exists (e.g. `x` and `γ₁`), fall back to juxtaposition with a warning.

## Blade Overrides

Override specific blade names via the `overrides` dict. Keys use metric-role notation — each basis vector is identified by its metric sign and position within that group:

- `+n` — the nth positive-squaring vector (1-indexed)
- `-n` — the nth negative-squaring vector (1-indexed)
- `_n` — the nth null/degenerate vector (1-indexed)
- `pss` — shorthand for the pseudoscalar (all vectors)

Spaces between components are optional. Multi-vector blades list their constituent vectors:

```python
"+1-1"      # blade from 1st positive ∧ 1st negative
"+1 -1"     # same, with space (equivalent)
"+1+2"      # blade from 1st positive ∧ 2nd positive
"_1+1+2+3"  # null ∧ three positives
"pss"       # pseudoscalar (any dimension)
```

Values are either:
- A string (applied to all three formats: ascii, unicode, latex)
- A 2-tuple `(ascii, unicode)` — LaTeX derived from unicode
- A 3-tuple `(ascii, unicode, latex)` — full control

### STA — Cl(1,3): 1 positive, 3 negative

```python
b_sta()  # just gamma vectors + pseudoscalar:
overrides = {
    "pss": "i",          # pseudoscalar → i
}

# With sigma bivector aliases:
b_sta(sigmas=True)  # adds:
overrides = {
    "+1-1": "σ₁",       # γ₀γ₁ bivector → σ₁
    "+1-2": "σ₂",       # γ₀γ₂ bivector → σ₂
    "+1-3": "σ₃",       # γ₀γ₃ bivector → σ₃
    "pss":  "i",
}

# With pseudovectors (implies sigmas):
b_sta(pseudovectors=True)  # adds:
overrides = {
    "+1-1":    "σ₁",
    "+1-2":    "σ₂",
    "+1-3":    "σ₃",
    "-1-2-3":  "iσ₁",   # trivector → iσ₁
    "+1-2-3":  "iσ₂",   # trivector → iσ₂
    "+1-1-3":  "iσ₃",   # trivector → iσ₃
    "pss":     "i",
}
```

### PGA — Cl(3,0,1): 3 positive, 0 negative, 1 null

```python
b_pga()  # internally uses:
overrides = {
    "pss": "I",          # pseudoscalar → I
}

# Custom: also name the ideal line
b_pga(overrides={
    "pss":    "I",
    "_1+1+2": "I∞",     # null ∧ two positives
})
```

### CGA — Cl(4,1): 4 positive, 1 negative

```python
b_cga()  # internally uses:
overrides = {
    "+4-1":  ("E0", "E₀", "E_0"),   # null pair
    "pss":   "I",
}

# With plus/minus basis instead of origin/infinity:
b_cga(null_basis="plus_minus")
# vectors named e₁, e₂, e₃, e₊, e₋ instead of e₁, e₂, e₃, eₒ, e∞
```

### VGA — Cl(3,0): simple overrides

```python
# Name the pseudoscalar
Algebra(3, blades=b_default(overrides={
    "pss": "I",
}))

# Name a specific bivector
Algebra(3, blades=b_default(overrides={
    "+1+2": "B",         # e₁₂ → B
    "pss":  "I",
}))
```

### Custom algebra — Cl(2,2)

```python
Algebra((1, 1, -1, -1), blades=b_default(overrides={
    "+1-1":       "J₁",
    "+2-2":       "J₂",
    "+1+2-1-2":   "I",
}))
```

### Mixed with LaTeX

```python
b_sta(overrides={
    "+1-1": ("s1", "σ₁", r"\sigma_1"),
    "+1-2": ("s2", "σ₂", r"\sigma_2"),
    "+1-3": ("s3", "σ₃", r"\sigma_3"),
    "pss":  ("i", "i", "i"),
})
```

## Blade Lookup

`blade("name")` returns a Multivector. It searches in this order:

1. Metric-role string (e.g. `"+1-1"`, `"pss"`)
2. Exact match against any name variant (ascii, unicode, latex) of any blade
3. Parse as prefix + digits, using the active `index_base` (0 or 1)

To get the `BasisBlade` naming object (for renaming etc.), use `get_basis_blade()` which accepts metric-role strings, Multivectors, bitmask ints, and `"pss"`.

```python
sta = Algebra(1, 3, blades=b_sta(sigmas=True))

sta.blade("+1-1")     # metric-role → σ₁ bivector
sta.blade("σ₁")       # display name match → same blade
sta.blade("pss")      # pseudoscalar shorthand
```

This fixes issue #8: when `index_base=0`, `blade("e01")` correctly parses as e₀ ∧ e₁.

## Built-in Convention Factories

Factories configure *what* blades are called. The `style=` parameter controls *how* they're joined and is orthogonal — every factory accepts it as an override.

| Factory | Vectors | Default style | Overrides | Index | Use case |
|---|---|---|---|---|---|
| `b_default()` | e₁, e₂, … | compact | — | 1 | Current behavior |
| `b_gamma()` | γ₀, γ₁, … | juxtapose | — | 0 | STA vectors |
| `b_sigma()` | σ₁, σ₂, … | juxtapose | — | 1 | Pauli algebra |
| `b_sigma_xyz()` | σₓ, σᵧ, σ_z | juxtapose | — | 1 | Pauli (xyz) |
| `b_pga()` | e₀, e₁, … | compact | PSS → `I` | 0 | Standard PGA |
| `b_sta()` | γ₀, γ₁, … | juxtapose | PSS → `i` | 0 | Spacetime algebra |
| `b_cga()` | e₁…e₃, eₒ, e∞ | compact | null pair → `E₀`, PSS → `I` | 1 | Conformal GA |

### Factory Signatures

All factories are keyword-only — no positional args, so call sites are always readable.

```python
def b_default(
    *,
    prefix: str = "e",
    start: int = 1,
    style: str = "compact",
    overrides: dict[str, str | tuple] | None = None,
) -> BladeConvention:
    """Default: e₁, e₂, … (1-based, compact)."""

def b_gamma(
    *,
    start: int = 0,
    style: str = "juxtapose",
    overrides: dict[str, str | tuple] | None = None,
) -> BladeConvention:
    """Gamma: γ₀, γ₁, … (0-based, juxtapose)."""

def b_sigma(
    *,
    start: int = 1,
    style: str = "juxtapose",
    overrides: dict[str, str | tuple] | None = None,
) -> BladeConvention:
    """Sigma: σ₁, σ₂, … (1-based, juxtapose)."""

def b_sigma_xyz(
    *,
    style: str = "juxtapose",
    overrides: dict[str, str | tuple] | None = None,
) -> BladeConvention:
    """Sigma xyz: σₓ, σᵧ, σ_z."""

def b_pga(
    *,
    style: str = "compact",
    pseudoscalar: str | tuple | None = "I",
    overrides: dict[str, str | tuple] | None = None,
) -> BladeConvention:
    """PGA: e₀, e₁, … (0-based, compact, PSS → I)."""

def b_sta(
    *,
    style: str = "juxtapose",
    sigmas: bool = False,
    pseudovectors: bool = False,
    overrides: dict[str, str | tuple] | None = None,
) -> BladeConvention:
    """STA: γ₀…γ₃, PSS → i.
    If sigmas=True, also names timelike bivectors as σ₁, σ₂, σ₃.
    If pseudovectors=True, also names trivectors as iσ₁, iσ₂, iσ₃ (implies sigmas)."""

def b_cga(
    *,
    euclidean: int = 3,
    null_basis: str = "origin_infinity",  # or "plus_minus"
    style: str = "compact",
    pseudoscalar: str | tuple | None = "I",
    overrides: dict[str, str | tuple] | None = None,
) -> BladeConvention:
    """CGA: e₁…eₙ, eₒ, e∞ (compact, PSS → I).
    Expects Cl(euclidean+1, 1). First `euclidean` positive vectors are
    Euclidean (e₁…eₙ). The remaining positive vector and the negative
    vector form the null pair: eₒ/e∞ or e₊/e₋ depending on null_basis."""
```

Notes:
- `overrides` is on every factory — lets you tweak any blade without building a full `BladeConvention` by hand.
- When a factory has built-in overrides (e.g. `b_pga` has `{"pss": "I"}`), user-supplied `overrides` are merged with the factory's defaults. User entries win on conflict (last one wins).
- `b_pga` and `b_cga` have `pseudoscalar=` since naming the PSS is the most common override.
- `b_cga` has `euclidean=` (3 or 4) and `null_basis=` to switch between `eₒ/e∞` and `e₊/e₋`.
- `b_sigma_xyz` has no `start=` since the subscripts are letters, not numbers.

### Factory Name Generation

Each factory generates three name variants (ascii, unicode, latex) per basis vector:

| Factory | ASCII | Unicode | LaTeX |
|---|---|---|---|
| `b_default(prefix="e", start=1)` | `e1, e2, e3` | `e₁, e₂, e₃` | `e_{1}, e_{2}, e_{3}` |
| `b_default(start=0)` | `e0, e1, e2` | `e₀, e₁, e₂` | `e_{0}, e_{1}, e_{2}` |
| `b_default(prefix="v")` | `v1, v2, v3` | `v₁, v₂, v₃` | `v_{1}, v_{2}, v_{3}` |
| `b_gamma(start=0)` | `y0, y1, y2, y3` | `γ₀, γ₁, γ₂, γ₃` | `\gamma_{0}, \gamma_{1}, …` |
| `b_gamma(start=1)` | `y1, y2, y3, y4` | `γ₁, γ₂, γ₃, γ₄` | `\gamma_{1}, \gamma_{2}, …` |
| `b_sigma(start=1)` | `s1, s2, s3` | `σ₁, σ₂, σ₃` | `\sigma_{1}, \sigma_{2}, …` |
| `b_sigma_xyz()` | `x, y, z` | `σₓ, σᵧ, σ_z` | `\sigma_x, \sigma_y, \sigma_z` |
| `b_pga()` | `e0, e1, e2, …` | `e₀, e₁, e₂, …` | `e_{0}, e_{1}, e_{2}, …` |
| `b_sta()` | `y0, y1, y2, y3` | `γ₀, γ₁, γ₂, γ₃` | `\gamma_{0}, …, \gamma_{3}` |
| `b_cga(euclidean=3)` | `e1, e2, e3, eo, ei` | `e₁, e₂, e₃, eₒ, e∞` | `e_{1}, …, e_{o}, e_{\infty}` |
| `b_cga(null_basis="plus_minus")` | `e1, e2, e3, ep, em` | `e₁, e₂, e₃, e₊, e₋` | `e_{1}, …, e_{+}, e_{-}` |

### Usage Examples

```python
b_pga()                          # compact (default for PGA)
b_pga(style="wedge")             # e₀∧e₁ instead of e₀₁
b_gamma(style="compact")         # γ₀₁ instead of γ₀γ₁
b_default(style="compact")       # e₁₂ instead of e₁e₂
b_default(prefix="v")            # v₁, v₂, … instead of e₁, e₂, …
b_default(start=0)               # e₀, e₁, … (0-based)
b_gamma(start=1)                 # γ₁, γ₂, γ₃, γ₄ (1-based)
b_pga(pseudoscalar="𝐈")          # custom pseudoscalar name
b_cga(null_basis="plus_minus")   # e₊, e₋ instead of eₒ, e∞
```

## Post-hoc Modification

### Accessing blades for renaming

`get_basis_blade()` accepts metric-role strings, Multivectors, bitmask ints, and `"pss"`:

```python
alg = Algebra(1, 3, blades=b_sta())
g0, g1, g2, g3 = alg.basis_vectors()

alg.get_basis_blade("+1-1")          # metric-role string
alg.get_basis_blade(g0 ^ g1)        # multivector
alg.get_basis_blade(0b0011)          # bitmask int
alg.get_basis_blade("pss")           # pseudoscalar shorthand
```

### Single blade rename

`rename()` on a `BasisBlade` accepts the same value formats as override values:

```python
alg.get_basis_blade("+1-1").rename("σ₁")                          # string → all three formats
alg.get_basis_blade("+1-1").rename(("s1", "σ₁"))                  # 2-tuple → ascii, unicode (latex from unicode)
alg.get_basis_blade("+1-1").rename(("s1", "σ₁", r"\sigma_1"))     # 3-tuple → ascii, unicode, latex
alg.get_basis_blade("+1-1").rename(unicode="σ₁", latex=r"\sigma_1")  # keyword form still works
```

Renaming is live — affects all future rendering of existing Multivectors.

### Replacing the entire convention

Not supported after construction. The `BladeConvention` is applied once during `__init__` to populate all `BasisBlade` objects. To change the entire naming scheme, create a new Algebra:

```python
# Don't try to swap conventions on an existing algebra.
# Instead, create a new one:
sta_plain = Algebra(1, 3, blades=b_sta())
sta_sigma = Algebra(1, 3, blades=b_sta(sigmas=True))
```

Rationale: swapping the convention would mean regenerating all blade names, potentially invalidating display output that's already been computed. A new Algebra is cheap (just precomputing tables) and avoids this class of bugs.

For incremental changes to an existing algebra, use `rename()` — it's the same parameters, same formats, just applied to one blade at a time.

## Examples

```python
# PGA — one parameter
pga = Algebra(3, 0, 1, blades=b_pga())
e0, e1, e2, e3 = pga.basis_vectors()
print(e0 ^ e1)       # → e₀₁
print(e1 ^ e2 ^ e3)  # → I

# STA — gamma + sigma aliases
sta = Algebra(1, 3, blades=b_sta(sigmas=True))
g0, g1, g2, g3 = sta.basis_vectors()
print(g0)             # → γ₀
print(g0 * g1)        # → σ₁

# Custom: Julia-style v prefix
alg = Algebra(3, blades=b_default(prefix="v", style="compact"))
v1, v2, v3 = alg.basis_vectors()
print(v1 ^ v2)        # → v₁₂

# Default (no blades= needed)
alg = Algebra(3)      # e₁, e₂, e₃, blades: e₁₂, e₁₃, …
```

## Migration from `names=`

```python
# Before                                    # After
Algebra(1, 3, names="gamma")                Algebra(1, 3, blades=b_gamma())
Algebra(3, names="sigma")                   Algebra(3, blades=b_sigma())
Algebra(3, names="sigma_xyz")               Algebra(3, blades=b_sigma_xyz())
Algebra((1,1), names=(code, uni))           Algebra((1,1), blades=BladeConvention(vector_names=(code, uni)))
Algebra((1,1), names=(code, uni, latex))    Algebra((1,1), blades=BladeConvention(vector_names=(code, uni, latex)))
```

`BasisBlade.rename()` is unchanged. `Notation` is unchanged (controls operation rendering, not blade names).

## Cross-Library Conventions

Every major library's convention is reproducible:

| Convention | Configuration |
|---|---|
| ganja.js (`e01, e12`) | `blades=b_default(start=0, style="compact")` |
| clifford (`e12, e13`) | `blades=b_default(style="compact")` |
| kingdon (`e01, e12`) | `blades=b_default(start=0, style="compact")` |
| galaga current (`e₁e₂`) | `blades=b_default(style="juxtapose")` for old behavior |
| galgebra (`e1^e2`) | `blades=b_default(style="wedge")` |
| GeometricAlgebra.jl (`v12`) | `blades=b_default(prefix="v", style="compact")` |
| Grassmann.jl (`v₁₂`) | `blades=b_default(prefix="v", style="compact")` |
| STA (γ₀γ₁, σ₁) | `blades=b_sta()` |
| PGA (e₀₁, I) | `blades=b_pga()` |
| CGA (e₁₂, eₒ∞, I) | `blades=b_cga()` |

## Open Questions

1. ~~Should `style="compact"` be the default instead of `"juxtapose"`?~~ Yes — `b_default()` uses `style="compact"`. Use `style="juxtapose"` explicitly for the old behavior.
2. ~~Should `overrides` accept bitmask ints as keys?~~ No — metric-role strings are the only key format. Bitmasks are an internal detail.
3. ~~Should there be a `b_custom()` factory?~~ No — `b_default(overrides={...})` covers this. Override every blade if you want full control.

## Implementation Impact

### Files to change

**`algebra.py` — Algebra class**

The constructor currently has these blade-related parameters and slots:

```python
# Parameters to remove:
names: str | tuple[list[str], list[str]] | None = None

# Slots to remove:
"_names", "_latex_names"

# Parameter to add:
blades: BladeConvention | None = None

# Slot to add:
"_blades_convention"   # store the BladeConvention for blade() lookup

# Kept unchanged:
repr_unicode: bool = True   # selects unicode vs ascii for __repr__
```

The `__init__` method currently has ~30 lines resolving `names` into `_names`/`_latex_names` and ~20 lines building `BasisBlade` objects by concatenating vector names. This entire block is replaced by:

1. If `blades is None`, create `b_default()` internally.
2. Ask the `BladeConvention` to generate all `BasisBlade` objects for the algebra's dimension.
3. Store the convention for `blade()` lookup.

**`algebra.py` — BasisBlade construction (lines ~248–266)**

Currently builds blade names by concatenating basis vector names (juxtapose style). This logic moves into `BladeConvention.build_blades(n)`, which applies the active `style`:

- `"juxtapose"`: concatenate vector names (current behavior)
- `"compact"`: extract common prefix, merge subscripts
- `"wedge"`: join with `∧` / `\wedge`

**`algebra.py` — `_blade_name()`, `_blade_latex()` (lines ~499–508)**

Unchanged — they already read from `BasisBlade` objects. The convention just changes how those objects are populated.

**`algebra.py` — `blade()` lookup (lines ~410–445)**

Currently has two paths: custom name parsing and 1-based digit parsing. Replace with the search order from the spec, using `index_base` from the convention.

**`algebra.py` — `Multivector.__repr__()` (line ~1145)**

Currently always returns unicode (same as `__str__`). With `repr_unicode` defaulting to `True` and kept as a parameter, `__repr__` should check `self.algebra._repr_unicode`:

- If `True` (default): `__repr__` returns unicode (using `BasisBlade.unicode_name`)
- If `False`: `__repr__` returns ascii (using `BasisBlade.ascii_name`)
- `__str__` always returns unicode regardless

**`algebra.py` — `Multivector._format()` (lines ~1121–1143)**

Takes `unicode: bool` and calls `alg._blade_name(i, unicode=unicode)`. This continues to work — `_blade_name` reads from `BasisBlade` which is populated by the convention.

**`algebra.py` — `PRESETS` dict (lines ~126–142)**

Remove entirely. The preset logic (`"gamma"`, `"sigma"`, etc.) moves into the convention factories (`b_gamma()`, `b_sigma()`, etc.).

**`algebra.py` — `Algebra.__repr__()` (line ~531)**

Shows `Cl(3,0)` etc. Unchanged — this reads from the signature, not from blade names.

### New file: `blade_convention.py`

Contains:
- `BladeConvention` dataclass
- `build_blades(convention, n)` → generates all `BasisBlade` objects
- Factory functions: `b_default()`, `b_gamma()`, `b_sigma()`, `b_sigma_xyz()`, `b_pga()`, `b_sta()`, `b_cga()`

### `__init__.py`

Remove `names` from any re-exports. Add exports for `BladeConvention` and all `b_*` factories.

### `basis_blade.py`

`BasisBlade.rename()` gains a positional first argument matching the override value format:

```python
def rename(self, name=None, /, *, ascii=None, unicode=None, latex=None):
    # name can be: str (all three), 2-tuple, or 3-tuple
    # keyword args override individual formats
```

### `notation.py`

Unchanged — controls operation rendering, not blade names.

### `expr.py`, `render.py`, `latex_build.py`

Unchanged — these read blade names from `BasisBlade` objects at render time, which are populated by the convention.

### Tests

- All tests using `names="gamma"` etc. must migrate to `blades=b_gamma()`.
- All tests using `names=(code, uni)` must migrate to `blades=BladeConvention(...)`.
- All tests using `repr_unicode=True` — keep as-is (now the default). Tests using `repr_unicode=False` still work.
- New tests for each factory, each style, blade lookup with 0-based indexing, and overrides.

### Examples

All example notebooks using `names=` must be updated. Grep shows ~37 occurrences across tests and examples.

## Test Strategy

### 1. Factory defaults — each factory produces correct blade names

```python
# b_default: 1-based, compact
alg = Algebra(3)
e1, e2, e3 = alg.basis_vectors()
assert str(e1 ^ e2) == "e₁₂"
assert (e1 ^ e2).latex() contains "e_{12}"

# b_gamma: 0-based, juxtapose
alg = Algebra(1, 3, blades=b_gamma())
g0, g1, _, _ = alg.basis_vectors()
assert str(g0) == "γ₀"
assert str(g0 * g1) contains "γ₀γ₁"

# b_pga: 0-based, compact, PSS → I
alg = Algebra(3, 0, 1, blades=b_pga())
assert str(alg.pseudoscalar()) == "I"
e0, e1, _, _ = alg.basis_vectors()
assert str(e0 ^ e1) == "e₀₁"

# b_sta: gamma vectors, PSS → i
alg = Algebra(1, 3, blades=b_sta())
assert str(alg.pseudoscalar()) == "i"

# b_sta(sigmas=True): adds σ bivector aliases
alg = Algebra(1, 3, blades=b_sta(sigmas=True))
g0, g1, _, _ = alg.basis_vectors()
assert str(g0 * g1) == "σ₁"

# b_sta(pseudovectors=True): implies sigmas, adds iσ trivectors
alg = Algebra(1, 3, blades=b_sta(pseudovectors=True))
# verify trivector names contain "iσ"

# b_sigma, b_sigma_xyz: correct prefixes
# b_cga: eₒ, e∞ names, E₀ for null pair
# b_cga(null_basis="plus_minus"): e₊, e₋ names
```

### 2. Style variations — each style renders correctly in ascii, unicode, and latex

```python
for style in ("compact", "juxtapose", "wedge"):
    alg = Algebra(3, blades=b_default(style=style))
    e1, e2, _ = alg.basis_vectors()
    blade = e1 ^ e2
    str(blade)           # unicode
    format(blade, "a")   # ascii
    blade.latex()        # latex
# compact:    e₁₂,   e12,   e_{12}
# juxtapose:  e₁e₂,  e1e2,  e_{1} e_{2}
# wedge:      e₁∧e₂, e1^e2, e_{1} \wedge e_{2}
```

### 3. Overrides — metric-role keys resolve correctly

```python
# Basic override
alg = Algebra(3, blades=b_default(overrides={"pss": "I"}))
assert str(alg.pseudoscalar()) == "I"

# Bivector override
alg = Algebra(3, blades=b_default(overrides={"+1+2": "B"}))
e1, e2, _ = alg.basis_vectors()
assert str(e1 ^ e2) == "B"

# Override with 3-tuple (ascii, unicode, latex)
alg = Algebra(3, blades=b_default(overrides={
    "+1+2": ("B12", "B₁₂", r"B_{12}")
}))
e1, e2, _ = alg.basis_vectors()
assert format(e1 ^ e2, "a") == "B12"
assert str(e1 ^ e2) == "B₁₂"

# Spaces in key are optional
alg1 = Algebra(3, blades=b_default(overrides={"+1+2": "X"}))
alg2 = Algebra(3, blades=b_default(overrides={"+1 +2": "X"}))
# both produce same result

# Null vector override in PGA
alg = Algebra(3, 0, 1, blades=b_pga(overrides={"_1+1": "L"}))
```

### 4. Error cases

```python
# Override references nonexistent vector
with pytest.raises(ValueError):
    Algebra(2, blades=b_default(overrides={"+3+4": "X"}))

# Invalid metric-role string
with pytest.raises(ValueError):
    Algebra(3, blades=b_default(overrides={"foo": "X"}))

# Incompatible convention (e.g. b_sta on wrong dimension)
# b_sta hardcodes sigma overrides for Cl(1,3) — error on Cl(3,0)?
with pytest.raises(ValueError):
    Algebra(3, blades=b_sta(sigmas=True))  # no negative vectors to form σ

# compact style with mixed prefixes falls back to juxtapose
alg = Algebra((1, 1), blades=BladeConvention(
    vector_names=("x", "γ₁"),
    style="compact",
))
# can't merge subscripts — different prefixes → falls back to juxtapose
assert "x" in str(alg.basis_vectors()[0] ^ alg.basis_vectors()[1])
```

### 5. Blade lookup — all search paths

```python
sta = Algebra(1, 3, blades=b_sta(sigmas=True))
g0, g1, _, _ = sta.basis_vectors()
blade = g0 ^ g1

# Metric-role string
assert sta.blade("+1-1") == blade

# Display name match
assert sta.blade("σ₁") == blade

# pss shorthand
assert sta.blade("pss") == sta.pseudoscalar()

# 0-based digit parsing
pga = Algebra(3, 0, 1, blades=b_pga())
e0, e1, _, _ = pga.basis_vectors()
assert pga.blade("e01") == e0 ^ e1   # fixes issue #8

# 1-based digit parsing
alg = Algebra(3)
e1, e2, _ = alg.basis_vectors()
assert alg.blade("e12") == e1 ^ e2

# Invalid name raises
with pytest.raises(ValueError):
    alg.blade("e99")

with pytest.raises(ValueError):
    alg.blade("nonsense")
```

### 6. get_basis_blade — all input types

```python
alg = Algebra(1, 3, blades=b_sta())
g0, g1, _, _ = alg.basis_vectors()
blade = g0 ^ g1

assert alg.get_basis_blade("+1-1") is alg.get_basis_blade(blade)
assert alg.get_basis_blade(0b0011) is alg.get_basis_blade(blade)
assert alg.get_basis_blade("pss") is alg.get_basis_blade(alg.pseudoscalar())
```

### 7. Post-hoc rename — same formats as overrides

```python
alg = Algebra(3)
e1, e2, _ = alg.basis_vectors()

# String → all three
alg.get_basis_blade("+1+2").rename("B")
assert str(e1 ^ e2) == "B"
assert format(e1 ^ e2, "a") == "B"

# 3-tuple
alg.get_basis_blade("+1+2").rename(("B12", "B₁₂", r"B_{12}"))
assert str(e1 ^ e2) == "B₁₂"
assert format(e1 ^ e2, "a") == "B12"

# Keyword form
alg.get_basis_blade("+1+2").rename(unicode="X")
assert str(e1 ^ e2) == "X"

# Rename is live — affects existing multivectors
mv = e1 ^ e2
alg.get_basis_blade("+1+2").rename("Z")
assert str(mv) == "Z"
```

### 8. repr_unicode — selects ascii vs unicode for repr

```python
alg_u = Algebra(3, repr_unicode=True)
alg_a = Algebra(3, repr_unicode=False)
e1_u, e2_u, _ = alg_u.basis_vectors()
e1_a, e2_a, _ = alg_a.basis_vectors()

assert "₁₂" in repr(e1_u ^ e2_u)    # unicode subscripts
assert "12" in repr(e1_a ^ e2_a)     # ascii digits
assert "₁₂" in str(e1_a ^ e2_a)     # str always unicode
```

### 9. Factory keyword overrides

```python
# prefix
alg = Algebra(3, blades=b_default(prefix="v"))
assert str(alg.basis_vectors()[0]) == "v₁"

# start
alg = Algebra(3, blades=b_default(start=0))
assert str(alg.basis_vectors()[0]) == "e₀"

# gamma with start=1
alg = Algebra(4, blades=b_gamma(start=1))
assert str(alg.basis_vectors()[0]) == "γ₁"

# pga with custom pseudoscalar
alg = Algebra(3, 0, 1, blades=b_pga(pseudoscalar="𝐈"))
assert str(alg.pseudoscalar()) == "𝐈"
```

### 10. Cross-library compatibility — verify each convention matches

```python
# clifford style
alg = Algebra(3, blades=b_default(style="compact"))
e1, e2, _ = alg.basis_vectors()
assert str(e1 ^ e2) == "e₁₂"

# ganja.js / kingdon style
alg = Algebra(3, blades=b_default(start=0, style="compact"))
e0, e1, _ = alg.basis_vectors()
assert str(e0 ^ e1) == "e₀₁"

# galgebra style
alg = Algebra(3, blades=b_default(style="wedge"))
e1, e2, _ = alg.basis_vectors()
assert "∧" in str(e1 ^ e2)

# Julia style
alg = Algebra(3, blades=b_default(prefix="v", style="compact"))
v1, v2, _ = alg.basis_vectors()
assert str(v1 ^ v2) == "v₁₂"
```
