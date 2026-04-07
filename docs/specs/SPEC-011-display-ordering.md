# SPEC-011: Custom Basis Blade Display Ordering

## Status

Accepted — implemented.

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

## Rules

### Rule 1: BladeConvention Field

`BladeConvention` has an optional `display_order` field:

```python
@dataclass
class BladeConvention:
    ...
    display_order: tuple[int, ...] | None = None
```

The value is a tuple of bitmask indices specifying the order in which
terms are emitted during rendering.

### Rule 2: Default (None)

When `display_order` is `None`, terms are emitted in ascending bitmask
order (`range(dim)`). This is the current behaviour and the default for
all existing factories.

### Rule 3: Validation

When `display_order` is provided, `build_blades()` validates that it is
a permutation of `range(dim)` — same length, same elements, no duplicates.
Raises `ValueError` otherwise.

### Rule 4: Rendering

All three concrete rendering paths iterate in `display_order` instead of
`range(dim)`:

- `Multivector._format()` (unicode/ascii `str()`)
- `Multivector.__format__()` (numeric format specs)
- `Multivector.latex()` (coefficient rendering)

Symbolic/lazy rendering is unaffected — it renders the expression tree,
not the coefficient array.

### Rule 5: basis_blades()

`Algebra.basis_blades(k=...)` returns blades in `display_order` sequence
(filtered to the requested grade), not bitmask order. This means
unpacking like `i, j, k = alg.basis_blades(k=2)` follows the convention.

### Rule 6: Unaffected Methods

The following are NOT affected by `display_order`:
- `Algebra.locals()` — returns a dict, ordering is irrelevant
- `Algebra.basis_vectors()` — always returns vectors in index order
- `Multivector.data` — always indexed by bitmask
- All computation (products, grades, norms, etc.)

## Impact

- `Algebra` stores the resolved `display_order` (a tuple of ints)
- Three rendering methods replace `range(alg.dim)` with `alg._display_order`
- `basis_blades()` iterates `_display_order` instead of `range(dim)`
- `build_blades()` validates the permutation

## Factories

Only `b_quaternion()` sets `display_order`. All other factories leave it
as `None`.

```python
def b_quaternion(...) -> BladeConvention:
    return BladeConvention(
        overrides={"...": "..."},
        display_order=(0b000, 0b110, 0b101, 0b011, 0b001, 0b010, 0b100, 0b111),
        #              1       i      j      k      e1     e2     e3     e123
    )
```
