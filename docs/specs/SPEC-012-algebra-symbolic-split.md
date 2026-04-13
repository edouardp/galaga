# SPEC-012: Algebraic/Symbolic Split

**Status: ✅ Complete (2026-04-13)**

## Intent

Break the circular dependency between `algebra.py` and `expr.py` by
introducing an operation registry that the algebraic side owns and the
symbolic side consumes. This makes cross-cutting concerns (grade tracking,
notation metadata, documentation) additive rather than invasive.

## Problem

`algebra.py` and `expr.py` imported each other:

```
algebra.py  →  from . import expr as _sym     (to build expression trees)
expr.py     →  from . import algebra as _alg   (to evaluate expression trees)
```

This created several problems:

1. **Circular dependency.** Python handled it via deferred resolution, but
   it was fragile and confusing.

2. **Scattered symbolic dispatch.** Every operation in `algebra.py` had
   interleaved `if x._is_symbolic` branches that built `_sym.NodeClass`
   trees. This was ~40 references to `_sym.*` spread across the file.

3. **Duplicated operation tables.** The same set of operations was declared
   in three places that had to stay in sync.

4. **Cross-cutting concerns were invasive.** Adding grade tracking required
   touching every operation body.

## Architecture (Implemented)

```
render.py ──► expr.py ──► ops.py
                │              │
                ▼              ▼
           algebra.py ──► ops.py
```

No cycles. `ops.py` is a leaf — it depends on nothing except stdlib.

### `ops.py` — Operation Registry

```python
@dataclass
class OpInfo:
    name: str
    func: Callable
    arity: int
    grade_rule: Callable | None = None

GA_OPS: dict[str, OpInfo] = {}
_SYMBOLIC_HANDLERS: dict[str, Any] = {}
```

Key functions:
- `@ga_op(name, arity, grade=...)` — registers an operation, wraps it with
  symbolic dispatch and grade propagation
- `register_symbolic_handler(name, handler)` — called by expr.py to map
  operation names to expression node classes
- `register_sym_factory(factory, sym_class)` — callback for Sym node
  construction without importing expr.py
- `make_sym(...)` / `is_sym(...)` — build and type-check Sym nodes
- `build_expr(name, *args)` — look up a handler by name and call it

### `algebra.py` — Pure Numeric + Delegation

- 29 operations decorated with `@ga_op`
- Operator overloads use `build_expr()` for symbolic node construction
- `_to_expr()` uses `make_sym()` / `is_sym()` callbacks
- Zero imports from `expr.py`
- Bare `Expr` operands are not accepted — `NotImplemented` is returned

### `expr.py` — Consumer Only

- `_NODE_NAMES` table maps `op_name → (class_name, arity)`
- Loop auto-generates node classes via `_make_binary_expr` / `_make_unary_expr`
- `_HANDLER_MAP` registers all handlers (GA ops + arithmetic nodes) at import time
- `_EXTRA_UNARY` handles `Norm` and `Sqrt` which aren't `@ga_op` operations
- Hand-written nodes for `Add`, `Sub`, `Neg`, `ScalarMul`, `ScalarDiv`,
  `Div`, `Grade`, `Squared`, `Scalar` (custom eval or extra fields)

### Grade Propagation

18 of 29 `@ga_op` operations have `grade=` rules:

| Rule | Operations |
|---|---|
| `r + s` (if ≤ n) | `op` |
| `s - r` (if ≥ 0) | `left_contraction` |
| `r - s` (if ≥ 0) | `right_contraction` |
| `\|r - s\|` | `doran_lasenby_inner` |
| `\|r - s\|` (if both > 0) | `hestenes_inner` |
| `0` | `scalar_product` |
| `k` (preserves) | `reverse`, `involute`, `conjugate`, `unit`, `inverse` |
| `n - k` | `dual`, `undual`, `complement`, `uncomplement` |
| `r + s - n` (if ≥ 0) | `regressive_product` |
| `k` if even/odd | `even_grades`, `odd_grades` |

The remaining 11 (`gp`, `commutator`, `anticommutator`, `lie_bracket`,
`jordan_product`, `exp`, `log`, `outerexp`, `outersin`, `outercos`,
`outertan`) produce mixed grades — no rule.

Factory methods (`scalar()`, `basis_vectors()`, `pseudoscalar()`, `vector()`,
`basis_blades()`, `locals()`) and `grade(x, k)` set `_grade` on results.

### `__float__` and `__abs__`

`float(mv)` returns the grade-0 coefficient for scalar MVs. Raises
`TypeError` for non-scalar MVs. `norm2()` returns a scalar MV (grade-0)
instead of a bare float.

## Invariants (Enforced by Tests)

1. `ops.py` never imports `expr.py` or `render.py`
2. `algebra.py` never imports `expr.py`
3. Every operation in `GA_OPS` has a registered symbolic handler
4. `len(GA_OPS) == 29`
5. Every `GA_OPS` entry has a corresponding `_NODE_NAMES` entry with matching arity

## Implementation Notes

### Import Order Constraint

`expr.py` cannot read `GA_OPS` at import time because `algebra.py` imports
`render.py` (line 67), which imports `expr.py`, before the `@ga_op`
decorators have run. Therefore `_NODE_NAMES` carries its own arity values
rather than reading them from `GA_OPS`. The invariant tests verify
consistency at test time.

### Divergences from Original Spec

- **Sym factory callbacks** (`make_sym`, `is_sym`, `register_sym_factory`)
  were not in the original spec. They were needed to eliminate `_sym.Sym`
  references from `_to_expr()`, `name()`, and `anon()`.

- **`build_expr()`** was not in the original spec. It replaced all remaining
  `_sym.NodeClass(...)` calls in operator overloads and standalone functions.

- **Phase 6** did not fully auto-generate from `GA_OPS` at import time due
  to the import order constraint. Instead, `_NODE_NAMES` is a parallel table
  with invariant tests enforcing consistency.

- **Bare `Expr` operands** (`MV + Expr`, `MV ^ Expr`) were removed rather
  than handled. `Expr` has `__radd__`/`__rsub__`/`__rmul__` for the cases
  that matter; `__rxor__`/`__ror__` don't exist on `Expr` and the pattern
  was never exposed to end users.

## Migration History

| Phase | Description | Status |
|---|---|---|
| 1 | Create `ops.py` with registry infrastructure | ✅ |
| 2 | Migrate 24 decorated operations to `@ga_op` | ✅ |
| 3 | Migrate 8 manual operations to `@ga_op` | ✅ |
| 4 | Slim operator overloads, delete `from . import expr` | ✅ |
| 5 | Grade tracking on 18 ops, `__float__`/`__abs__`, `norm2` as MV | ✅ |
| 6 | Auto-generate expr nodes from `_NODE_NAMES` table | ✅ |

## Related ADRs

- [ADR-065](../adrs/065-operation-registry.md) — Operation Registry
- [ADR-066](../adrs/066-grade-propagation-and-float.md) — Grade Propagation and `__float__`
