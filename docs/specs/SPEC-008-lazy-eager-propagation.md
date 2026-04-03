# SPEC-008: Lazy/Eager Propagation Rules

## Intent

Every multivector is either lazy (carries an expression tree for symbolic
rendering) or eager (concrete numeric data only). Operations must propagate
laziness correctly so symbolic expressions build automatically.

## Rules

### Rule 1: Lazy is Contagious

If ANY operand is lazy, the result is lazy.

| Left | Right | Result |
|---|---|---|
| lazy | lazy | lazy |
| lazy | eager | lazy |
| eager | lazy | lazy |
| eager | eager | eager |

### Rule 2: Lazy Results Carry Both Data and Expr

A lazy result has:
- `.data` — concrete NumPy array (computed eagerly)
- `._expr` — expression tree node (for display/simplification)
- `._is_lazy = True`

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

### Rule 4: .name() Sets Lazy

Calling `.name()` on any MV sets `_is_lazy = True`.

### Rule 5: .eval() Returns Anonymous Eager

`.eval()` returns a NEW multivector that is anonymous and eager.
The original is not modified.

### Rule 6: .eager() Mutates In-Place

`.eager()` sets `_is_lazy = False` and clears `_expr` and name (unless
a name argument is provided).

### Rule 7: Scalar Coercion

When a plain number (int/float) is used with a lazy MV, it is coerced
to a scalar MV in the same algebra. The result is lazy.

| Expression | Result |
|---|---|
| `3 * lazy_v` | lazy (ScalarMul) |
| `lazy_v + 5` | lazy (Add) |
