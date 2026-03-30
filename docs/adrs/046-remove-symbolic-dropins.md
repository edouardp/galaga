---
status: accepted
date: 2026-03-30
deciders: edouard
---

# ADR-046: Remove Symbolic Drop-in Function Replacements

## Context and Problem Statement

The `galaga.symbolic` module contained drop-in replacements for every function
in `galaga.algebra` (gp, grade, reverse, norm, etc.). These detected lazy
Multivector arguments and built expression trees. However, the `@lazy_unary`
and `@lazy_binary` decorators on the algebra functions already do the same
thing — making the drop-ins redundant.

Users had two ways to get lazy behaviour:
```python
from galaga import grade          # works with lazy MVs (via decorator)
from galaga.symbolic import grade # works with lazy MVs (via drop-in)
```

Both produced identical results. The drop-ins were the original mechanism
before the decorators were added, and were never removed.

## Decision Outcome

Remove all drop-in function replacements from `galaga.symbolic`. Keep:
- Expr node class re-exports (Gp, Add, Sym, etc.)
- `simplify()` and related helpers
- `sym()` convenience function
- `_is_symbolic()` helper

### Consequences

- Good, because one way to do things, not two
- Good, because -148 lines of code
- Good, because `from galaga import grade` is the only import users need
- Bad, because breaking change for `from galaga.symbolic import grade` users
- Acceptable, because pre-1.0 and the migration is mechanical
