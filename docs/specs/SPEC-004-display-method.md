# SPEC-004: Display Method

## Intent

`Multivector.display()` shows the progression from name to expression to
numeric value, deduplicating identical parts. It returns a `_DisplayResult`
object that is auto-detected as LaTeX by galaga-marimo.

## Rules

### Rule 1: Three Parts

Display assembles up to three parts: name, reveal (expression), eval (value).

| Part | Source | When included |
|---|---|---|
| Name | `self.latex()` | When MV is named |
| Reveal | `self.reveal().latex()` | When lazy with expr, AND differs from name AND eval |
| Eval | `self.eval().latex()` | When differs from previous parts |

### Rule 2: Deduplication

Parts are compared as strings. If reveal == name or reveal == eval, it is
omitted. If eval matches any previous part, it is omitted.

| MV state | Parts shown |
|---|---|
| Named lazy with expr (e.g. `R = exp(-B/2)`) | `R = e^{-B/2} = 0.877 - 0.479 e_{12}` |
| Named eager (e.g. `v = e₁`) | `v = e_{1}` |
| Anonymous eager | `e_{1}` (just the value) |
| Anonymous lazy (e.g. `e₁ ∧ e₂`) | `e_{1} \wedge e_{2} = e_{12}` |
| Named with name == eval | `e_{1}` (single part) |

### Rule 3: Separator

| Mode | Separator |
|---|---|
| `display()` | ` \quad = \quad ` |
| `display(compact=True)` | ` = ` |

### Rule 4: coeff_format

`display().latex(coeff_format=...)` applies the format to the eval part
only. Name and reveal parts are unchanged.

### Rule 5: _DisplayResult Protocol

The returned object has:
- `.latex(coeff_format=None)` → raw LaTeX string
- `._repr_latex_()` → `$...$` wrapped (for Jupyter/marimo)
- `.__str__()` / `.__repr__()` → raw LaTeX string
- Detected as LaTeX by galaga-marimo via `.latex()` method
