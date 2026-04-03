# SPEC-007: Unicode Coefficient Formatting

## Intent

The unicode/str rendering path uses Python's native `:g` format for
coefficients. This spec documents the behaviour for completeness — it
is deliberately simpler than the LaTeX path (SPEC-001).

## Rules

### Rule 1: Format

Coefficients use Python's `:g` format (6 significant digits, automatic
scientific notation for large/small numbers).

| Input | Output |
|---|---|
| 42.0 | `42` |
| 3.14159 | `3.14159` |
| 299792458.0 | `2.99792e+08` |
| 1.2e-6 | `1.2e-06` |

### Rule 2: Unit Coefficient Suppression

Same as SPEC-001 Rule 5: ±1 coefficients suppressed when blade present.
Uses `np.isclose(abs(c), 1.0)`.

### Rule 3: Near-Zero Suppression

Same as SPEC-001 Rule 6: |c| < 1e-12 treated as zero.

### Rule 4: Multi-Term Assembly

Same as SPEC-001 Rule 9: terms joined with ` + `, negative terms use ` - `.

### Rule 5: No Scientific Notation Conversion

Unlike the LaTeX path, scientific notation is NOT converted. `2.99792e+08`
renders as-is. This matches Python's default behaviour in terminals.
