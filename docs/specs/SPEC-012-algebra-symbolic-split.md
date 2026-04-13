# SPEC-012: Algebraic/Symbolic Split

## Intent

Break the circular dependency between `algebra.py` and `expr.py` by
introducing an operation registry that the algebraic side owns and the
symbolic side consumes. This makes cross-cutting concerns (grade tracking,
notation metadata, documentation) additive rather than invasive.

## Problem

Today, `algebra.py` and `expr.py` import each other:

```
algebra.py  →  from . import expr as _sym     (to build expression trees)
expr.py     →  from . import algebra as _alg   (to evaluate expression trees)
```

This creates several problems:

1. **Circular dependency.** Python handles it via deferred resolution, but
   it's fragile and confusing. Adding a new operation requires changes in
   both modules.

2. **Scattered symbolic dispatch.** Every operation in `algebra.py` has
   interleaved `if x._is_symbolic` branches that build `_sym.NodeClass`
   trees. This is ~40 references to `_sym.*` spread across the file.

3. **Duplicated operation tables.** The same set of operations is declared
   in three places that must stay in sync:
   - `algebra.py`: the numeric implementation + symbolic dispatch
   - `expr.py`: the expression node classes (`_make_binary_expr`, etc.)
   - `notation.py` / `render.py`: display rules keyed by node class name

4. **Cross-cutting concerns are invasive.** Adding grade tracking required
   touching every operation body. Any future concern (linearity metadata,
   cost hints, documentation generation) would face the same problem.

## Current Architecture

```
┌─────────────────────────────────────────────────┐
│  algebra.py                                     │
│                                                 │
│  @symbolic_binary("Op")    ←── decorator from   │
│  def op(a, b):                  symbolic.py     │
│      # numeric impl                             │
│      # (decorator handles symbolic dispatch)    │
│                                                 │
│  def commutator(a, b):                          │
│      if a._is_symbolic:   ←── manual dispatch   │
│          ...build _sym.Commutator...            │
│      return gp(a,b) - gp(b,a)                   │
│                                                 │
│  Multivector._symbolic_result()                 │
│      # builds symbolic MV, references _sym.*    │
│                                                 │
├──────────── imports ───────────────────────────►│
│                                                 │
│  expr.py                                        │
│                                                 │
│  Gp = _make_binary_expr("Gp", "gp")             │
│  # eval() calls _alg.gp()  ←── back-reference   │
│                                                 │
├──────────── imports ───────────────────────────►│
│                                                 │
│  render.py / notation.py                        │
│  # keyed by expr node class names               │
└─────────────────────────────────────────────────┘
```

### Operations by dispatch style

**Decorated** (24 ops — symbolic dispatch handled by `@symbolic_unary`/`@symbolic_binary`):
`gp`, `op`, `left_contraction`, `right_contraction`, `hestenes_inner`,
`doran_lasenby_inner`, `scalar_product`, `involute`, `conjugate`, `dual`,
`undual`, `complement`, `uncomplement`, `regressive_product`, `unit`,
`inverse`, `even_grades`, `odd_grades`, `exp`, `log`, `outerexp`,
`outersin`, `outercos`, `outertan`

**Manual** (8 ops — inline `if symbolic` branches in the function body):
`commutator`, `anticommutator`, `lie_bracket`, `jordan_product`,
`grade`, `norm`, `reverse` (via `__invert__`), `sandwich`

**Operator overloads** (10 — inline symbolic dispatch in Multivector methods):
`__add__`, `__radd__`, `__sub__`, `__rsub__`, `__neg__`, `__mul__`,
`__rmul__`, `__xor__`, `__or__`, `__truediv__`

## Proposed Architecture

```
┌──────────────────────────────────────────────────┐
│  ops.py  (NEW — operation registry)              │
│                                                  │
│  @ga_op("op", arity=2, sym_node="Op",            │
│         grade=lambda g,h,n: g+h if g+h<=n ...)   │
│  def op(a, b):                                   │
│      # pure numeric implementation               │
│                                                  │
│  GA_OPS = { "op": OpInfo(...), ... }             │
│  # inspectable registry of all operations        │
│                                                  │
│  No symbolic imports. No expr imports.           │
├──────────────────────────────────────────────────┤
│  algebra.py  (slimmed down)                      │
│                                                  │
│  class Algebra: ...                              │
│  class Multivector: ...                          │
│      # operator overloads delegate to ops.py     │
│      # no _sym.* references                      │
│                                                  │
│  No expr imports.                                │
├──────────────────────────────────────────────────┤
│  expr.py  (consumer only)                        │
│                                                  │
│  # imports ops.py to read the registry           │
│  # auto-generates node classes from registry     │
│  # registers symbolic handlers back into ops.py  │
│                                                  │
│  Dependency: expr → ops → (nothing)              │
│              expr → algebra (for Multivector)    │
│              algebra → ops (for implementations) │
│              algebra ✗ expr  (BROKEN)            │
├──────────────────────────────────────────────────┤
│  render.py / notation.py                         │
│                                                  │
│  # can read ops registry for metadata            │
│  # still keyed by node class name                │
└──────────────────────────────────────────────────┘
```

### Dependency graph (target)

```
render.py ──► expr.py ──► ops.py
                │              │
                ▼              ▼
           algebra.py ──► ops.py
```

No cycles. `ops.py` is a leaf — it depends on nothing except NumPy.

## Design

### The `@ga_op` decorator

```python
@ga_op(
    name="op",                    # registry key, matches function name
    arity=2,                      # 1 or 2
    grade=lambda g, h, n: ...,   # grade propagation rule (optional)
)
def op(a, b):
    """Outer (wedge) product."""
    # pure numeric — no symbolic awareness
    ...
```

The decorator:
1. Registers the function in `GA_OPS` with all metadata
2. Wraps it to handle symbolic dispatch (if a symbolic handler is registered)
3. Wraps it to apply the grade rule to the result

The decorator carries only algebraic metadata. It does not reference
symbolic node class names — that mapping is owned by `expr.py`.

### The `GA_OPS` registry

```python
@dataclass
class OpInfo:
    name: str
    func: Callable          # the numeric implementation
    arity: int              # 1 or 2
    grade_rule: Callable | None  # grade propagation function
```

Inspectable, iterable, testable:
```python
for name, info in GA_OPS.items():
    print(f"{name}: arity={info.arity}")
```

### Symbolic handler registration

The symbolic layer owns the mapping from operation name to expression node
class. It registers handlers at import time:

```python
# In expr.py (or a setup function called at import)
from .ops import register_symbolic_handler

# The op name → node class mapping lives here, not in ops.py
register_symbolic_handler("op", Op)
register_symbolic_handler("gp", Gp)
register_symbolic_handler("reverse", Reverse)
# ...or auto-derived from a naming convention / table
```

### Which operations get symbolic nodes?

Not every registered operation needs a symbolic node. The criterion is
**notational identity**: does the operation have its own symbol that a
reader of the mathematics would recognise as a single concept?

| Has symbolic node | Why | Examples |
|---|---|---|
| Yes | Own notation — displays as a named concept | `commutator` → `[a, b]`, `lie_bracket` → `½[a, b]`, `op` → `a ∧ b` |
| No | Decomposes naturally in the expression tree | `sandwich(r, x)` → `rx~r`, `norm(x)` → `√⟨xx̃⟩₀` |

Every `@ga_op` gets a registry entry (for grade tracking, arity, etc.),
but the symbolic node mapping in `expr.py` is a **subset** of `GA_OPS`,
not a 1:1 correspondence. Operations without a symbolic node simply let
their composed sub-expressions appear in the tree.

The `@ga_op` wrapper checks for a registered handler:

```python
def wrapper(*args):
    result = func(*args)  # numeric computation
    if any(a._is_symbolic for a in args if isinstance(a, Multivector)):
        handler = _SYMBOLIC_HANDLERS.get(name)
        if handler:
            # build expression tree, attach to result
            ...
    if grade_rule:
        result._grade = grade_rule(...)
    return result
```

### Operator overloads

Multivector operator overloads become thin dispatchers:

```python
def __xor__(self, other):
    """Outer product (a ^ b)."""
    return op(self, other)  # ops.py handles everything
```

The current complexity (checking `isinstance(other, _sym.Expr)`, building
symbolic results manually) moves into the `@ga_op` wrapper.

### Operations that don't fit the pattern

Some operations have non-standard signatures:

| Operation | Issue | Solution |
|---|---|---|
| `grade(x, k)` | Extra int parameter | `@ga_op(arity="1+param")` or keep manual |
| `sandwich(r, x)` | Asymmetric binary | Standard binary, no special handling needed |
| `norm(x)` | Returns float, not MV | Keep manual (it's a derived quantity) |
| `scalar_sqrt(x)` | Accepts int/float too | Keep manual |

A small number of operations (~4) may remain outside the registry. This is
acceptable — the registry covers the ~30 standard GA operations.

## Migration Plan

### Phase 1: Create `ops.py` with registry infrastructure

- Define `OpInfo`, `GA_OPS`, `@ga_op`, `register_symbolic_handler`
- No changes to existing code yet
- Test the registry in isolation

### Phase 2: Migrate decorated operations

- Move the 24 `@symbolic_binary`/`@symbolic_unary` operations from
  `algebra.py` to `ops.py`, replacing `@symbolic_*` with `@ga_op`
- `algebra.py` imports and re-exports them
- `symbolic.py` decorators become unused (keep for backward compat)
- Tests should pass unchanged

### Phase 3: Migrate manual operations

- Move `commutator`, `anticommutator`, `lie_bracket`, `jordan_product`
  to `ops.py` with `@ga_op`
- Remove inline `if symbolic` branches from their bodies

### Phase 4: Slim down operator overloads

- Simplify Multivector `__add__`, `__mul__`, etc. to delegate to `ops.py`
- Remove `from . import expr as _sym` from `algebra.py`
- The circular dependency is broken

### Phase 5: Add grade tracking

- Add `grade=...` parameter to each `@ga_op` call
- The `@ga_op` wrapper applies it automatically
- Re-implement `__float__`/`__abs__`/`norm2`-as-MV from the parked branch

### Phase 6: Auto-generate expr nodes

- `expr.py` reads `GA_OPS` and generates node classes automatically
- The current `_make_binary_expr("Gp", "gp")` calls become derived from
  the registry instead of being a parallel declaration
- Single source of truth for the operation set

## Invariants

1. `ops.py` never imports `expr.py` or `render.py`
2. `algebra.py` never imports `expr.py` (after Phase 4)
3. Every operation in `GA_OPS` has a corresponding expr node class
4. Every expr node class corresponds to an operation in `GA_OPS`
5. `len(GA_OPS)` is tested — adding an op without registering it fails

## Risks

- **Large refactor.** ~40 `_sym.*` references in `algebra.py` need to move.
  Mitigated by phased migration — each phase is independently shippable.

- **Operator overload complexity.** The current overloads handle `Expr`
  operands (e.g. `Multivector + Expr`). This interaction needs careful
  handling in the new architecture.

- **Performance.** Dict lookups and handler checks on the hot path.
  Mitigated by: the symbolic check (`_is_symbolic`) is already paid today;
  the dict lookup is O(1) and negligible compared to NumPy array operations.

- **Backward compatibility.** Public API (`from galaga import op, gp, ...`)
  must not change. `algebra.py` re-exports everything from `ops.py`.
