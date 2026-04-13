# Branches

Parked feature branches and their status.

## feature/grade-tracking-float

**Goal:** Make scalar multivectors usable as Python floats (`float(mv)`, `abs(mv)`, `np.isclose(mv, x)`). Enable `norm2()` to return a scalar MV instead of a bare float, preserving `.display()` for notebooks.

**Where we got to:**

- `__float__` and `__abs__` on Multivector, with lazy `homogeneous_grade()` fallback
- Constructors (`scalar`, `vector`, `basis_vectors`, `basis_blades`, `pseudoscalar`, `locals`) set `_grade` eagerly
- `grade(x, k)` sets `_grade = k`
- `norm2()` returns a grade-0 Multivector
- `half_commutator` alias for `lie_bracket`
- ADR 065 documents the design
- 2098 tests pass, 0 failures

**Why we parked it:**

We initially tried eager grade propagation through all operations — fragile, required touching every op and every code path that constructs a Multivector. We simplified to constructors + lazy fallback, which works but doesn't solve the deeper problem: cross-cutting concerns (grade tracking, symbolic dispatch, notation) are scattered across every operation body.

**How to revisit:**

The right path is to first do the algebraic/symbolic split:

1. Create an algebraic op registry (`@ga_op` decorator) that owns the numeric computation and metadata (grade rule, arity, display name).
2. Make the symbolic layer a consumer that registers handlers against op names, breaking the circular dependency between `algebra.py` and `expr.py`.
3. Grade tracking becomes a one-line `grade=...` parameter on each `@ga_op` decorator — no manual propagation, no fragility.

Once that architecture is in place, re-implementing `__float__`/`__abs__`/`norm2`-as-MV is trivial on top of it. The branch has working tests and an ADR that can be reused.
