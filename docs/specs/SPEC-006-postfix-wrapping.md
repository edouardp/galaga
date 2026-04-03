# SPEC-006: Postfix Wrapping Rules

## Intent

When a postfix operation (dual, inverse, squared, etc.) is applied to an
expression, the inner expression may need wrapping to avoid ambiguity or
invalid LaTeX. Three distinct wrapping cases exist.

## Rules

### Rule 1: Compound Sym Names

When a Sym's name represents a compound expression (e.g. `a \wedge b`),
postfix operations wrap it in parens.

Detection uses `Sym.is_compound`:
- If `inner_expr` is available: True when inner_expr is binary AND name contains spaces
- Fallback (no inner_expr): True when name contains `\wedge`, `\vee`, `\cdot`, ` + `, ` - `

| Expression | Without wrapping | With wrapping |
|---|---|---|
| `dual(a ∧ b)` | `a ∧ b⋆` ❌ | `(a ∧ b)⋆` ✅ |
| `dual(B)` | `B⋆` ✅ | — |

### Rule 2: Superscript-on-Superscript

When a `^`-based postfix is applied to a node that already has a superscript,
brace-wrap to avoid double-superscript LaTeX errors.

Detection: `isinstance(inner, Sup)` or `Sym.has_superscript` (name contains `^`).

| Expression | Without wrapping | With wrapping |
|---|---|---|
| `inverse(e^{x})` | `e^{x}^{-1}` ❌ | `{e^{x}}^{-1}` ✅ |
| `undual(B^\star)` | `B^\star^{*^{-1}}` ❌ | `{B^\star}^{*^{-1}}` ✅ |
| `dual(a)` | `a^*` ✅ | — |

### Rule 3: Frac Before Superscript

When a `^`-based postfix is applied to a `Frac` node, brace-wrap.

| Expression | Without wrapping | With wrapping |
|---|---|---|
| `squared(1/2)` | `\frac{1}{2}^2` ❌ | `{\frac{1}{2}}^2` ✅ |
| `inverse(a/b)` | `\frac{a}{b}^{-1}` ❌ | `{\frac{a}{b}}^{-1}` ✅ |

### Rule 4: Frac in Products (No Parens)

`Frac` nodes are NOT wrapped in `\left(...\right)` parens when they appear
in products or sums. The fraction bar provides visual grouping.

| Expression | Output |
|---|---|
| `(1/2) * e₁` | `\frac{1}{2} e_{1}` (no parens) |
| `(1/2) + a` | `\frac{1}{2} + a` (no parens) |

### Rule 5: Priority

The checks are applied in order:
1. Compound Sym → Parens
2. Superscript-on-superscript → brace-wrap
3. Frac before superscript → brace-wrap

If compound Sym wrapping applies, the superscript checks are skipped
(the Parens already resolves the ambiguity).
