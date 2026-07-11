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

- STA: display is `γ₀` but you type `y0` (why not `g0`?)
- `b_sta(sigmas=True)`: generates `s1`, `is1` — not discoverable from the
  vector naming pattern
- `b_default(subscripts="xyz")`: display is `e_{xy}` and local is `exy` —
  but a user might prefer `e_xy` or `bxy`
- PGA: `e₀` is the null vector, `e₁₂₃` is the pseudoscalar `I` — locals
  should reflect this

## Design Principles

1. **Display and typing are independent concerns** — display is for humans
   reading notebooks; typing is for humans writing code. They may differ.
2. **Helpers make common cases one-liners** — you shouldn't need to understand
   the full override system to use standard conventions.
3. **Overrides are explicit and local** — when the default isn't right,
   a single parameter fixes it without breaking the rest.
4. **Defaults match the most common textbook for that convention** — STA
   defaults match Doran & Lasenby; PGA defaults match Gunn/De Keninck.

## Architecture

### Layer 1: BladeConvention (display)

Controls rendering. Unchanged from current design except for the new
`subscripts` parameter.

```python
@dataclass
class BladeConvention:
    prefix: str = "e"
    subscripts: list | None = None       # NEW: bare labels
    vector_names: list | None = None     # DEPRECATED in 2.0
    style: str = "compact"               # "compact" | "wedge" | "juxtapose"
    overrides: dict | None = None
    display_order: tuple | None = None
    local_prefix: str | None = None      # NEW: override prefix for locals()
```

### Layer 2: Local naming (typing)

A separate system that derives Python variable names. Rules:

1. If a blade has an **explicit override** with a Python-safe ASCII name,
   use that name. (e.g., `"pss": "I"` → key is `"I"`)
2. Otherwise, derive from `local_prefix` + subscript labels.
3. `local_prefix` defaults to the ASCII form of `prefix` (from `_PREFIX_MAP`).
4. Multi-vector blades concatenate subscripts under the prefix: `e` + `xy` → `exy`.

### Layer 3: `locals()` parameters

```python
def locals(
    self,
    *,
    grades: list[int] | None = None,
    prefix: str | None = None,       # NEW: override local prefix at call time
    symbolic: bool | None = None,
) -> dict[str, Multivector]:
```

`prefix` overrides `local_prefix` from the convention, allowing the same
algebra to be unpacked with different variable names in different contexts.

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
alg = Algebra(3, blades=b_default(subscripts="xyz", pss="I"))
ex, ey, ez = alg.basis_vectors()
locals().update(alg.locals())  # ex, ey, ez, exy, exz, eyz, I
```

**Justification**: Jackson (EM), Goldstein (mechanics), and most engineering
texts use x, y, z. The `e` prefix keeps them distinct from scalar variables.

### Case 3: Bare axis names (minimal notation)

Some pedagogical contexts prefer just `x, y, z` without prefix.

```python
alg = Algebra(3, blades=BladeConvention(
    prefix="",
    subscripts=["x", "y", "z"],
    overrides={"pss": "I"},
))
# locals: x, y, z, xy, xz, yz, I
```

**Justification**: Spinors for Beginners (eigenchris), some graphics papers.
Works when there's no ambiguity with scalar variables.

### Case 4: STA — Spacetime Algebra

Doran & Lasenby use γ₀, γ₁, γ₂, γ₃ with juxtaposition for products.
The relative vectors σₖ = γₖγ₀ and pseudoscalar i = γ₀γ₁γ₂γ₃.

```python
sta = Algebra(1, 3, blades=b_sta(sigmas=True, pss="i"))
g0, g1, g2, g3 = sta.basis_vectors()
locals().update(sta.locals())
# g0, g1, g2, g3, s1, s2, s3, is1, is2, is3, i
# OR with local_prefix="y": y0, y1, ...
```

**Current**: prefix is `γ` → ASCII `y` → locals are `y0`, `y1`.
**Proposed**: add `local_prefix` parameter to `b_sta`:

```python
b_sta(local_prefix="g")  # → g0, g1, g2, g3, g01, g02, ...
b_sta(local_prefix="y")  # → y0, y1, y2, y3 (current default)
```

**Justification**: `g` is the most common ASCII shorthand for gamma in physics
code. `y` comes from the `_PREFIX_MAP` but is less intuitive. Default should
be `"g"` in a future release (breaking change for 2.0).

### Case 5: PGA — Projective Geometric Algebra

De Keninck and Gunn use e₀ (null), e₁, e₂, e₃, with pseudoscalar I.
The null vector is the "extra" dimension.

```python
pga = Algebra(3, 0, 1, blades=b_pga())
e0, e1, e2, e3 = pga.basis_vectors()
locals().update(pga.locals())  # e0, e1, e2, e3, e01, ..., I
```

**Justification**: ganja.js, Klein, PGA4CS all use this convention.
Zero-indexed because e₀ is special (the null direction).

### Case 6: CGA — Conformal Geometric Algebra

Dorst uses e₁, e₂, e₃, eₒ (origin), e∞ (infinity) or e₊, e₋.

```python
cga = Algebra(4, 1, blades=b_cga())
e1, e2, e3, eo, ei = cga.basis_vectors()
locals().update(cga.locals())  # e1, e2, e3, eo, ei, e12, ..., I
```

**Justification**: Dorst "GA for Computer Science", Hitzer, Hildenbrand.
The null basis names (eo, ei) are standard in the literature.

### Case 7: Quaternions

Hamilton's i, j, k with display order matching convention.

```python
alg = Algebra(3, blades=b_quaternion())
i, j, k = alg.basis_blades(k=2)
locals().update(alg.locals())  # e1, e2, e3, i, j, k, e123
```

**Justification**: Standard quaternion convention. Bivector names override
to `i, j, k`; vector names stay as `e1, e2, e3` since they're rarely used
directly in quaternion work.

## Proposed `local_prefix` Behavior

### On BladeConvention

```python
BladeConvention(prefix="γ", local_prefix="g")
```

- `prefix` controls display: LaTeX renders as `\gamma_{0}`, unicode as `γ₀`
- `local_prefix` controls variable names: `g0`, `g1`, `g01`, `g012`
- If `local_prefix` is None, falls back to `_PREFIX_MAP[prefix]` (current behavior)

### On helpers

```python
b_sta(local_prefix="g")    # gamma vectors as g0, g1, g2, g3
b_default(local_prefix="v")  # default vectors as v1, v2, v3
b_pga(local_prefix="e")   # explicit (same as default for PGA)
```

### On `locals()`

```python
alg.locals(prefix="g")  # override at extraction time
```

This allows the SAME algebra to produce different variable names:

```python
sta = Algebra(1, 3, blades=b_sta())
sta.locals()              # y0, y1, ... (convention default)
sta.locals(prefix="g")    # g0, g1, ... (user preference)
```

## Interaction Matrix

| Concern | Set by | When |
|---------|--------|------|
| LaTeX rendering | `prefix` + `subscripts`/`vector_names` | Convention construction |
| Unicode rendering | `prefix` + `subscripts`/`vector_names` | Convention construction |
| ASCII display name | `prefix` (via `_PREFIX_MAP`) + subscripts | Convention construction |
| `locals()` key | `local_prefix` (or fallback to ASCII prefix) + subscripts | `locals()` call |
| Explicit override name | `overrides` dict | Convention construction |

## Defaults for Each Helper

| Helper | Display prefix | local_prefix (proposed default) | Justification |
|--------|---------------|----------------------------------|---------------|
| `b_default()` | `e` | `"e"` | Universal default |
| `b_sigma()` | `σ` | `"s"` | Standard shorthand |
| `b_gamma()` | `γ` | `"g"` | Most common in code |
| `b_sta()` | `γ` | `"g"` | Physics code convention |
| `b_pga()` | `e` | `"e"` | Matches display |
| `b_cga()` | `e` | `"e"` | Matches display |
| `b_quaternion()` | `e` | `"e"` | Vectors rarely used directly |

**Note**: changing `b_sta` default from `"y"` to `"g"` is a breaking change.
Schedule for 2.0 with deprecation warning in 1.x.

## Migration Path

### 1.x (now)
- Add `local_prefix` to `BladeConvention` (optional, None = current behavior)
- Add `local_prefix` to helpers (optional)
- Add `prefix` parameter to `locals()` (optional)
- Deprecation warning when `b_sta` falls back to `"y"` without explicit choice

### 2.0
- `b_sta` defaults to `local_prefix="g"`
- Remove `vector_names` (replaced by `subscripts`)
- `locals()` uses `local_prefix` as the primary source for key generation

## Edge Cases

- `local_prefix=""` with `subscripts=["x","y","z"]` → keys are `x`, `y`, `xy`, `xyz`
- `local_prefix` on override blades: overrides always win (e.g., `"pss": "I"`)
- Collision: if `local_prefix="e"` and subscripts produce a key that matches
  a Python keyword, sanitize with trailing underscore (`in_` etc.)
- Multi-character subscripts: `subscripts=["tx","ty","tz"]` → `etx`, `ety`,
  `etxty`, etc. Works but less ergonomic.

## Non-Goals

- Automatic inference of "good" variable names from arbitrary LaTeX
- Supporting every possible textbook convention as a built-in
- Making `locals()` keys match display names exactly (they serve different purposes)
