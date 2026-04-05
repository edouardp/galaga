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

## Specification

### 1. Basis Vector Naming (existing, extended)

Basis vectors are named at construction. This is the foundation — blade names are derived from these unless overridden.

```python
# Current: works, no change
Algebra(3)                                          # e1, e2, e3 (1-based default)
Algebra(1, 3, names="gamma")                        # γ₀, γ₁, γ₂, γ₃
Algebra((1,1,1), names=(["x","y","z"], ["x","y","z"]))  # custom

# New: 0-based indexing preset
Algebra(3, 0, 1, names="e0")                        # e₀, e₁, e₂, e₃

# New: CGA-style with special symbols
Algebra(4, 1, names=(
    ["e1","e2","e3","eo","einf"],
    ["e₁","e₂","e₃","eₒ","e∞"],
    [r"e_1", r"e_2", r"e_3", r"e_o", r"e_\infty"],
))
```

The `names` parameter accepts:
- A preset string: `"e"` (1-based, default), `"e0"` (0-based), `"gamma"`, `"sigma"`, `"sigma_xyz"`
- A 2-tuple `(ascii_names, unicode_names)` — LaTeX derived from unicode
- A 3-tuple `(ascii_names, unicode_names, latex_names)` — full control

### 2. Blade Derivation Rule

By default, multi-grade blade names are derived by concatenating basis vector names:

```
e₁ ∧ e₂  →  "e₁e₂"   (current default: juxtaposition)
```

A new `blade_style` parameter controls this:

```python
Algebra(3, blade_style="juxtapose")   # e₁e₂  (default, current behavior)
Algebra(3, blade_style="compact")     # e₁₂   (merged subscripts)
Algebra(3, blade_style="wedge")       # e₁∧e₂ (explicit wedge symbol)
```

`blade_style` only affects the *derived* names. Explicit overrides (see §3) take precedence.

Rules for `"compact"`:
- Only works when all basis vector names share a common prefix (e.g. all start with `e` or `γ`).
- Subscript digits/symbols are concatenated: `e₁` + `e₂` → `e₁₂`.
- If the prefix differs across vectors, fall back to juxtaposition.

### 3. Blade Name Overrides

A new `blade_names` parameter allows overriding specific blade names:

```python
Algebra(3, blade_names={
    "e123": ("I", "I", "I"),          # (ascii, unicode, latex) — all three
    "e12":  "B",                       # shorthand: same string for all three
})
```

The dict keys are blade identifiers using the *internal* code names (e.g. `"e12"`, `"e123"`). The values are either:
- A string (applied to all three formats)
- A 2-tuple `(ascii, unicode)` — LaTeX derived from unicode
- A 3-tuple `(ascii, unicode, latex)` — full control

Unspecified blades use the derivation rule from §2.

### 4. Blade Lookup

`blade("name")` searches in this order:

1. Exact match against any of the three name variants (ascii, unicode, latex) of any blade
2. Exact match against override names from `blade_names`
3. Parse as concatenation of basis vector code names (current `_parse_blade_name`)
4. Parse as prefix + digits, using the active indexing base (0-based or 1-based)

Step 4 is where issue #8 lives. The fix: when `names="e0"` or custom names start at index 0, digit parsing uses 0-based indexing. The base is inferred from the basis vector names, not hardcoded to 1.

### 5. Interaction with `get_basis_blade().rename()`

Post-hoc renaming via `get_basis_blade(e1^e2).rename(unicode="B")` continues to work. It modifies the same `BasisBlade` object that the derivation rule populated. The rename is live — it affects all future rendering.

`blade_names` at construction time is equivalent to calling `rename()` on each specified blade immediately after construction. The two mechanisms are not in conflict.

### 6. Notation (unchanged)

The `Notation` object controls how *operations* are rendered (reverse as `~x` vs `x†`, wedge as `∧` vs `^`, etc.). It does NOT control blade names — that's the `BasisBlade` system.

These are orthogonal:
- `Notation` → how operations look
- `names` / `blade_style` / `blade_names` → how blades look

## Examples

### PGA with 0-based indexing and compact subscripts

```python
pga = Algebra(3, 0, 1, names="e0", blade_style="compact", blade_names={
    "e0123": "I",
})
e0, e1, e2, e3 = pga.basis_vectors()
print(e0 ^ e1)      # → e₀₁
print(e1 ^ e2)      # → e₁₂
pga.blade("e01")     # → works (0-based digit parsing)
```

### STA with gamma notation and named bivectors

```python
sta = Algebra(1, 3, names="gamma", blade_names={
    "e12": ("s1", "σ₁", r"\sigma_1"),
    "e13": ("s2", "σ₂", r"\sigma_2"),
    "e14": ("s3", "σ₃", r"\sigma_3"),
    "e1234": ("i", "i", "i"),
})
```

### CGA with special basis names

```python
cga = Algebra(4, 1, names=(
    ["e1","e2","e3","eo","ei"],
    ["e₁","e₂","e₃","eₒ","e∞"],
    [r"e_1",r"e_2",r"e_3",r"e_o",r"e_\infty"],
), blade_style="compact")
```

## Migration

- All existing code continues to work unchanged. `names`, `repr_unicode`, `Notation`, and `BasisBlade.rename()` behave exactly as before.
- `blade_style` defaults to `"juxtapose"` (current behavior).
- `blade_names` defaults to `None` (no overrides).
- The `"e0"` preset is new but does not affect existing presets.
- Issue #8 is fixed by making digit parsing respect the active indexing base.
- Issue #9 is addressed by `blade_names`.

## Open Questions

1. Should `blade_style="compact"` be the default? It's more conventional in GA literature, but it's a breaking change to display output.
2. Should `blade_names` accept bitmask ints as keys (e.g. `{0b011: "B"}`) in addition to strings?
3. For `blade_style="compact"`, how should non-numeric subscripts be handled? E.g. `γ₀` + `γ₁` → `γ₀₁`? Or `γ₀γ₁`?
4. Should there be a `blade_names` preset for common patterns (e.g. `"pga_standard"` that names the pseudoscalar `I` and uses 0-based compact subscripts)?

## Cross-Library Conventions to Support

Based on the survey in `docs/ga-library-conventions.md`, the naming system should be able to reproduce the conventions of every major GA library. The following table shows the target configurations:

| Convention | Indexing | Bivector style | Example | Configuration |
|---|---|---|---|---|
| ganja.js | 0-based | compact | `e01, e12` | `names="e0", blade_style="compact"` |
| clifford | 1-based | compact | `e12, e13` | `blade_style="compact"` (default names) |
| kingdon | 0-based (PGA) / 1-based | compact | `e01, e12` | `names="e0", blade_style="compact"` |
| galaga current | 1-based | juxtapose | `e₁e₂, e₁e₃` | default (no change) |
| galgebra | user-defined | wedge | `e1^e2, x^y` | `blade_style="wedge"` |
| GeometricAlgebra.jl | 1-based, `v` prefix | compact | `v12, v13` | `names=(["v1","v2",...], ...)`, `blade_style="compact"` |
| Grassmann.jl | 1-based, `v` prefix | compact | `v₁₂, v₂₃` | same as above |
| STA (Doran-Lasenby) | 0-based, γ prefix | juxtapose | `γ₀γ₁, σ₁` | `names="gamma"`, with `blade_names` for σ aliases |
| PGA (standard) | 0-based, compact | compact + I | `e₀₁, e₁₂, I` | `names="e0", blade_style="compact", blade_names={"e0123": "I"}` |
| CGA | 1-based + special | compact | `e₁₂, eₒ∞` | custom `names` with `eₒ`, `e∞` |

All of these should be achievable with the three parameters: `names`, `blade_style`, and `blade_names`. No configuration should require subclassing or monkey-patching.
