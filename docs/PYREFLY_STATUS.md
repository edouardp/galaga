# Pyrefly Type Checking — Status and Remaining Work

Pyrefly (Meta's Rust-based Python type checker) was added in the linting branch.
It currently reports **138 errors** and runs as a non-blocking warning.

## Error Breakdown

| Category                  | Count | Description                                       |
| ------------------------- | ----- | ------------------------------------------------- |
| `missing-attribute`       | 117   | Accessing attributes on base `Expr`/`LNode` types |
| `bad-argument-type`       | 6     | Passing `str \| None` where `str` expected        |
| `bad-return`              | 4     | Return type mismatches                            |
| `bad-index`               | 4     | Indexing issues                                   |
| `unsupported-operation`   | 3     | Operators on union types                          |
| `bad-override`            | 2     | Method signature mismatches                       |
| `no-matching-overload`    | 1     | numpy overload resolution                         |
| `bad-function-definition` | 1     | Signature issue                                   |

## Root Causes

### 1. Expr subclass attributes accessed via base type (117 errors)

The `render.py`, `simplify.py`, and `latex_build.py` modules use `isinstance`
dispatch on `Expr` subclasses, then access subclass-specific attributes like
`.a`, `.b`, `.x`, `.k`. Pyrefly doesn't narrow the type after `isinstance`.

```python
# Current — pyrefly can't see that e.a exists after isinstance check
if isinstance(e, Add):
    return render(e.a) + " + " + render(e.b)  # error: Expr has no attribute 'a'
```

**Fix options:**
- Add type annotations to `Expr` base class (stub attributes)
- Use `match` statements (Python 3.10+) which pyrefly may narrow better
- Add `# type: ignore[missing-attribute]` comments

### 2. Optional fields used without narrowing (6 errors)

Fields like `_name_unicode: str | None` are passed to functions expecting `str`.
The code is correct (we check earlier), but pyrefly can't see the guard.

```python
# Current — pyrefly sees str | None
self._expr = Sym(self, self._name_unicode, ...)

# Fix — explicit narrowing
name = self._name_unicode or self._name
self._expr = Sym(self, name, ...)
```

### 3. Union parameter types (3 errors)

`grade(mv, k)` accepts `k: int | str` (for `"even"` / `"odd"`). Pyrefly
flags `k < 0` because `str` doesn't support `<` with `int`.

**Fix:** Split the function or narrow with `isinstance(k, int)` before comparison.

### 4. LNode subclass attributes (20 errors)

Same pattern as Expr — `latex_emit.py` and `latex_rewrite.py` dispatch on
`LNode` subclasses and access `.children`, `.sep`, `.num`, `.den`, etc.

### 5. numpy typing (1 error)

`np.radians(degrees)` where `degrees: float | None` — pyrefly sees the
`None` even though we've already handled it.

## Recommended Fix Order

1. **Expr/LNode base class stubs** — add `a`, `b`, `x`, `k` etc. as
   `Any`-typed attributes on the base class, or use Protocol types.
   Fixes ~137 of 138 errors in one go.

2. **Optional narrowing** — add explicit `assert x is not None` or
   `if x is not None` guards. Fixes 6 errors.

3. **Union splitting** — restructure `grade()` to handle `int` and `str`
   paths separately. Fixes 3 errors.

## Effort Estimate

~2-3 hours to reach zero errors. The Expr/LNode stub approach is the
fastest path — one change to each base class fixes 85% of errors.

## Goal

Make pyrefly a blocking check (fail the lint) once errors reach zero.
