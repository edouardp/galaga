# SPEC-011: Custom Basis Blade Display Ordering

## Status

Pending — not yet implemented.

## Problem

Multivector terms are displayed in bitmask order (ascending binary index).
This is deterministic and matches the internal `data[]` array layout, but
it does not always match conventional notation.

The primary example is quaternions via Cl(3,0) bivectors:

| Blade | Bitmask | Bitmask order | Conventional order |
|---|---|---|---|
| k = e₁₂ | 0b011 = 3 | 1st | 3rd |
| j = e₁₃ | 0b101 = 5 | 2nd | 2nd |
| i = e₂₃ | 0b110 = 6 | 3rd | 1st |

So `1 + 2i + 3j + 4k` displays as `1 + 4k + 3j + 2i`.

## Scope

This affects all three rendering paths:
- `Multivector._format()` (unicode/ascii `str()`)
- `Multivector.__format__()` (format specs)
- `Multivector.latex()` (LaTeX output)

## Proposed Design

Add an optional `display_order` field to `BladeConvention`:

```python
@dataclass
class BladeConvention:
    ...
    display_order: tuple[int, ...] | None = None  # bitmask sequence
```

When `display_order` is set, terms are emitted in that order instead of
ascending bitmask order. Bitmasks not listed are appended in their natural
order after the listed ones.

Convention factories would set this where it matters:

```python
def b_quaternion(...) -> BladeConvention:
    return BladeConvention(
        overrides={"+2+3": "i", "+1+3": "j", "+1+2": "k"},
        display_order=(0b000, 0b110, 0b101, 0b011, 0b001, 0b010, 0b100, 0b111),
        #              1       i      j      k      e1     e2     e3     e123
    )
```

## Impact

- Three rendering methods need to iterate in `display_order` instead of `range(dim)`
- `Algebra.basis_blades(k=...)` should return blades in the `display_order` sequence
  (filtered to the requested grade), not bitmask order — so that unpacking like
  `k, j, i = alg.basis_blades(k=2)` follows the convention's intended ordering
- `display_order` must be validated at algebra construction time (correct length, valid bitmasks)
- No impact on computation — only display and iteration order

## Why Not Now

- Only quaternions need it — complex, PGA, STA, CGA all display correctly in bitmask order
- The rendering paths are stable and well-tested; changing iteration order risks regressions
- A notebook-local formatting helper is a sufficient workaround

## Workaround

```python
def qformat(q):
    """Display a quaternion in conventional i, j, k order."""
    s = q.scalar_part
    ci = q.data[0b110]  # i = e23
    cj = q.data[0b101]  # j = e13
    ck = q.data[0b011]  # k = e12
    parts = []
    if s: parts.append(f"{s:g}")
    for c, name in [(ci, "i"), (cj, "j"), (ck, "k")]:
        if c: parts.append(f"{c:g}{name}")
    return " + ".join(parts).replace("+ -", "- ")
```

## Revisit When

- A second algebra (beyond quaternions) needs non-bitmask display ordering
- Users request it as a feature
