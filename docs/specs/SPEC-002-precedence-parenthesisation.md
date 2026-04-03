# SPEC-002: Precedence and Parenthesisation Rules

## Intent

When rendering expression trees to unicode or LaTeX, child expressions
must be wrapped in parentheses when their precedence is lower than the
parent's threshold. This prevents ambiguous readings like `a∧b⋆` (is it
`(a∧b)⋆` or `a∧(b⋆)`?).

## Rules

### Rule 1: Precedence Table

Each Expr node type has a precedence level. Higher = binds tighter.

| Prec | Node types |
|---|---|
| 100 | Sym, Scalar, Grade, Norm, Unit, Exp, Log, Sqrt, Even, Odd, Commutator, Anticommutator, LieBracket, JordanProduct |
| 95 | Reverse, Involute, Conjugate, Dual, Undual, Complement, Uncomplement, Inverse, Squared |
| 90 | Neg |
| 80 | ScalarMul, ScalarDiv, Gp |
| 70 | Op, Lc, Rc, Hi, Dli, Sp, Div, Regressive |
| 60 | Add, Sub |

### Rule 2: Wrapping Threshold

A child is wrapped in parens if `child.prec < parent_threshold`.
Parent thresholds:

| Parent | Threshold | Effect |
|---|---|---|
| Gp | 80 | Wraps Add, Sub, Op, contractions |
| Op | 81 | Wraps Add, Sub, ScalarMul (but not other Op — flat) |
| Contractions (Lc, Rc, Hi, Dli, Sp) | 71 | Wraps Add, Sub |
| Postfix (Dual, Inverse, etc.) | 96 | Wraps everything except atoms and other postfix |
| Accent (Reverse, Conjugate) | 95 | Wraps everything except atoms |

### Rule 3: Flat (Associative) Operations

Operations marked `flat=True` skip wrapping for same-type children:
- `Gp(Gp(a,b),c)` → `abc` (not `(ab)c`)
- `Op(Op(a,b),c)` → `a∧b∧c`
- `Add(Add(a,b),c)` → `a + b + c`
- `Regressive(Regressive(a,b),c)` → `a∨b∨c`

### Rule 4: Frac Nodes Skip Parens

In LaTeX, `Frac` LNodes are never wrapped in `\left(...\right)` parens
because the fraction bar provides visual grouping. They ARE brace-wrapped
`{...}` when followed by a superscript postfix (Rule 5 in SPEC-006).

## Examples

| Expression | Rendered |
|---|---|
| `Gp(Add(a,b), c)` | `(a + b)c` |
| `Gp(a, Add(b,c))` | `a(b + c)` |
| `Op(ScalarMul(2,a), b)` | `(2a)∧b` |
| `ScalarMul(2, Op(a,b))` | `2a∧b` |
| `Dual(Add(a,b))` | `(a + b)⋆` |
| `Dual(a)` | `a⋆` |
| `Gp(Gp(a,b),c)` | `abc` |
