# SPEC-001: LaTeX Coefficient Rendering

## Intent

When a concrete multivector is rendered to LaTeX, its floating-point
coefficients must produce valid, readable LaTeX. Python's default number
formatting (`1.2e-06`) is not valid LaTeX — the `e` and `-` render
incorrectly. This spec defines how coefficients are formatted in the
LaTeX rendering path.

The unicode/str rendering path is NOT covered by this spec — it uses
Python's native `:g` format unchanged.

## Scope

This spec covers:
- Default coefficient rendering in `Multivector.latex()`
- Explicit `coeff_format` rendering in `Multivector.latex(coeff_format=...)`
- The `Notation.scientific` style setting
- The `_fmt_coeff`, `_sci_lnode`, and `_coeff_lnode` functions

This spec does NOT cover:
- Symbolic expression rendering (handled by the Expr → LNode pipeline)
- Unicode/str coefficient rendering (uses Python `:g` directly)
- The `display()` method (covered by SPEC-004)

## Rules

### Rule 1: Default Precision

Default coefficient rendering uses 6 significant digits, matching Python's
`:g` format.

| Input | Output |
|---|---|
| 3.14159265358979 | `3.14159` |
| 42.0 | `42` |
| 0.5 | `0.5` |
| 0.001 | `0.001` |
| -1.0 | `-1` |

### Rule 2: No Scientific Notation for |c| ≥ 1e-6

When the default `:g` format would produce scientific notation for a
number with |c| ≥ 1e-6, the coefficient is reformatted using `:.6f`
with trailing zeros stripped.

| Input | Python `:g` | LaTeX output |
|---|---|---|
| 299792458.0 | `2.99792e+08` | `299792458` |
| 0.0000012 | `1.2e-06` | `0.000001` |

### Rule 3: Scientific Notation for |c| < 1e-6

Numbers with |c| < 1e-6 use scientific notation, rendered as LNodes
using `Sup(Text("10"), Text(exponent))`.

| Input | Python `:g` | LaTeX output (times) | LaTeX output (cdot) |
|---|---|---|---|
| 1.2e-7 | `1.2e-07` | `1.2 \times 10^{-7}` | `1.2 \cdot 10^{-7}` |
| 1.054e-34 | `1.054e-34` | `1.054 \times 10^{-34}` | `1.054 \cdot 10^{-34}` |

When the mantissa is 1, it is suppressed:

| Input | LaTeX output |
|---|---|
| 1e-10 | `10^{-10}` |

### Rule 4: Notation.scientific Style

The `Notation.scientific` property controls the separator in scientific
notation. Default is `"times"`.

| Style | Separator | Example |
|---|---|---|
| `"times"` | `\times` | `1.2 \times 10^{-7}` |
| `"cdot"` | `\cdot` | `1.2 \cdot 10^{-7}` |
| `"raw"` | none | `1.2e-07` (Python format, no conversion) |

### Rule 5: Unit Coefficient Suppression

Coefficients of ±1 are suppressed when a blade name is present.
Uses `np.isclose(abs(c), 1.0)` to handle floating-point noise from
trig operations.

| Coefficient | Blade | Output |
|---|---|---|
| 1.0 | `e_{1}` | `e_{1}` |
| -1.0 | `e_{1}` | `-e_{1}` |
| -0.9999999999999998 | `e_{1}` | `-e_{1}` |
| 1.0 | (none) | `1` |
| 2.5 | `e_{1}` | `2.5 e_{1}` |

### Rule 6: Near-Zero Suppression

Coefficients with |c| < 1e-12 are treated as zero and omitted from
the output. This threshold is NOT configurable.

| Coefficient | Output |
|---|---|
| 1e-13 | (omitted) |
| 1e-12 | (omitted) |
| 1.1e-12 | shown |

### Rule 7: Explicit coeff_format Override

When `coeff_format` is provided, ALL coefficients are shown (no ±1
suppression, no near-zero suppression except exact 0.0). The format
string is passed to Python's `format()`, then scientific notation
conversion (Rules 3-4) is applied.

| coeff_format | Input | Output |
|---|---|---|
| `.3f` | 1.0 | `1.000 e_{1}` |
| `.3e` | 1.2e-6 | `1.200 \times 10^{-6} e_{1}` |
| `.3e` | 42.0 | `4.200 \times 10^{1} e_{1}` |

### Rule 8: Zero Multivector

A multivector with all coefficients below the near-zero threshold
renders as `0`. With `coeff_format`, it renders as `format(0.0, coeff_format)`.

| coeff_format | Output |
|---|---|
| None | `0` |
| `.3f` | `0.000` |
| `.3e` | `0.000e+00` |

### Rule 9: Multi-Term Assembly

Terms are joined with ` + `. Negative terms use ` - ` (the leading
minus is absorbed into the separator).

| Terms | Output |
|---|---|
| `3 e_{1}`, `4 e_{2}` | `3 e_{1} + 4 e_{2}` |
| `3 e_{1}`, `-4 e_{2}` | `3 e_{1} - 4 e_{2}` |

## Implementation

| Function | Responsibility |
|---|---|
| `_fmt_coeff(c)` | Rule 1, 2: format float with 6 digits, force non-scientific ≥ 1e-6 |
| `_sci_lnode(s, style)` | Rule 3, 4: parse scientific notation string → LNode with Sup |
| `_coeff_lnode(c, blade, coeff_format, style)` | Rule 5, 7: assemble coefficient + blade as LNode |
| `Multivector.latex()` | Rule 6, 8, 9: threshold, zero, multi-term assembly |

## Edge Cases

- Coefficient exactly at threshold: `abs(c) == 1e-6` → non-scientific (≥ boundary)
- Coefficient exactly at near-zero: `abs(c) == 1e-12` → omitted (< boundary uses `<`)
- `coeff_format` with non-scientific format (`.3f`): no `\times` conversion
- `Notation.scientific = "raw"` with small number: passes through as `1.2e-07`
- Negative zero: `-0.0` → treated as zero, omitted
