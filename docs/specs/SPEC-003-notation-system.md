# SPEC-003: Notation System

## Intent

The notation system controls how GA operations render in unicode, LaTeX,
and ASCII. It is configurable per-algebra, with presets for common
conventions and per-operation overrides.

## Rules

### Rule 1: Notation Kinds

Each operation's rendering is controlled by a `NotationRule` with a `kind`:

| Kind | Description | Example (unicode) | Example (LaTeX) |
|---|---|---|---|
| `accent` | Combining char for atoms, wide/fallback for compounds | `ã` | `\tilde{a}` |
| `postfix` | Symbol after operand | `a⋆` | `a^*` |
| `prefix` | Symbol before operand | `-a` | `-a` |
| `infix` | Symbol between operands | `a∧b` | `a \wedge b` |
| `juxtaposition` | Operands side by side, smart spacing | `ab` | `a b` |
| `wrap` | Delimiters around content | `⟨a⟩₁` | `\langle a \rangle_{1}` |
| `function` | Function call style | `reverse(a)` | `\operatorname{reverse}(a)` |
| `superscript` | Symbol in `^{...}` | — | `a^\dagger` |
| `unit_fraction` | `x/‖x‖` fraction form | `a/‖a‖` | `\frac{a}{\lVert a \rVert}` |

### Rule 2: Dispatch Order

The renderer looks up the notation rule FIRST, then dispatches on `rule.kind`.
Structural nodes (Sym, Scalar, Neg, ScalarMul, ScalarDiv, Add, Sub, Div)
are handled before the notation lookup — they have no configurable notation.

### Rule 3: Valid Formats

`set()` accepts formats: `"unicode"`, `"latex"`, `"ascii"`. Others raise `ValueError`.

### Rule 4: Valid Kinds

`set()` accepts the 9 kinds listed in Rule 1. Others raise `ValueError`.

### Rule 5: Node Names

Node names are not validated — unknown names are accepted for extensibility.
Known names match Expr class names: `Reverse`, `Gp`, `Op`, `Grade`, etc.

### Rule 6: Presets

| Preset | Reverse | Gp | Op |
|---|---|---|---|
| `default()` | `ã` / `\tilde{a}` | `ab` | `a∧b` |
| `hestenes()` | `a†` / `a^\dagger` | `ab` | `a∧b` |
| `doran_lasenby()` | `ã` / `\tilde{a}` | `ab` | `a∧b` |
| `functional()` | `reverse(a)` | `geometric_product(a, b)` | `outer_product(a, b)` |
| `functional_short()` | `rev(a)` | `gp(a, b)` | `op(a, b)` |

### Rule 7: Scientific Notation Style

`Notation.scientific` controls LaTeX scientific notation (see SPEC-001).
Values: `"times"` (default), `"cdot"`, `"raw"`.

### Rule 8: Chaining

`set()` and `with_scientific()` return `self` for fluent chaining.

### Rule 9: Copy Independence

`notation.copy()` returns an independent copy. Changes to the copy
do not affect the original.

### Rule 10: Per-Algebra Isolation

Each algebra has its own notation instance. Overriding one algebra's
notation does not affect another.
