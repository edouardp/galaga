# SPEC-008: Symbolic/Numeric Propagation Rules

## Intent

Every multivector is either symbolic (carries an expression tree for
rendering and simplification) or numeric (concrete numeric data only).
Operations must propagate symbolic status correctly so expression trees
build automatically.

Note: the expression tree is a provenance record — numeric results are
computed immediately at every step. "Symbolic" means the MV additionally
carries a tree showing how it was derived.

## Rules

### Rule 1: Symbolic is Contagious

If ANY operand is symbolic, the result is symbolic.

| Left | Right | Result |
|---|---|---|
| symbolic | symbolic | symbolic |
| symbolic | numeric | symbolic |
| numeric | symbolic | symbolic |
| numeric | numeric | numeric |

### Rule 2: Symbolic Results Carry Both Data and Expr

A symbolic result has:
- `.data` — concrete NumPy array (computed immediately)
- `._expr` — expression tree node (for display/simplification)
- `._is_symbolic = True`

This means `.eval()` is instant (data already computed) and `.data` is
always valid.

### Rule 3: Names Don't Propagate

When a named MV participates in an operation, the result is anonymous.
The named operand appears by name in the expression tree, but the result
has no name.

| Expression | Result name | Result expr |
|---|---|---|
| `R * v` (both named) | None | `Gp(Sym("R"), Sym("v"))` |
| `a + b` (both named) | None | `Add(Sym("a"), Sym("b"))` |

### Rule 4: .name() Sets Symbolic

Calling `.name()` on any MV sets `_is_symbolic = True`.

### Rule 5: .eval() Returns Anonymous Numeric

`.eval()` returns a NEW multivector that is anonymous and numeric.
The original is not modified.

### Rule 6: .numeric() Mutates In-Place

`.numeric()` sets `_is_symbolic = False` and clears `_expr` and name
(unless a name argument is provided). `.eager()` is a deprecated alias.

### Rule 7: Scalar Coercion

When a plain number (int/float) is used with a symbolic MV, it is coerced
to a scalar MV in the same algebra. The result is symbolic.

| Expression | Result |
|---|---|
| `3 * symbolic_v` | symbolic (ScalarMul) |
| `symbolic_v + 5` | symbolic (Add) |
