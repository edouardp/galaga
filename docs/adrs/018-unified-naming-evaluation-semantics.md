---
status: accepted (partially superseded by ADR-028)
date: 2026-03-25
deciders: edouard
supersedes: partially supersedes ADR-004, ADR-013
---

# ADR-018: Unified Naming and Evaluation Semantics on Multivector

## Context and Problem Statement

The library had two separate worlds: `Multivector` (numeric/eager) in
`galaga.algebra` and `Expr`/`Sym` (symbolic/lazy) in `galaga.symbolic`. Users had to
choose upfront which world to work in, and `sym()` returned an `Expr` — a
completely different type from `Multivector`. This created friction:

- Named symbolic values couldn't participate in numeric APIs
- Switching between symbolic and numeric required type conversions
- The two types had different operator behavior and properties

## Decision Drivers

* Naming (display identity) and evaluation strategy (lazy vs eager) are
  independent concerns — they should be controllable independently
* Users shouldn't need to choose between "numeric" and "symbolic" upfront
* Basis blades should be displayable by name without becoming symbolic
* The existing `Expr` tree infrastructure works well and should be preserved

## Considered Options

1. **Enrich Multivector** — Add `.name()`, `.anon()`, `.symbolic()`, `.numeric()`
   directly to `Multivector`, with an optional internal `Expr` tree
2. **New unified class** — Replace both `Multivector` and `Expr` with a new type
3. **Keep separate types** — Improve interop but maintain the type boundary

## Decision Outcome

Chosen option: "Enrich Multivector" — every multivector can independently be
named or anonymous, symbolic or numeric.

### The Two Axes

| | **Anonymous** | **Named** |
|---|---|---|
| **Numeric** | Plain numeric MV (default) | Basis blades, named constants |
| **Symbolic** | Expression structure visible | `B = (e1^e2).name("B")` |

### API

```python
mv.name("B")                    # named + symbolic (default)
mv.name("B", latex=r"\mathbf{B}")  # with format overrides
mv.anon()                       # remove name, keep symbolic/numeric
mv.symbolic()                       # prefer symbolic representation
mv.numeric()                      # force numeric in-place, strip name
mv.numeric("B")                   # force numeric in-place, keep/set name
mv.eval()                       # return new anonymous numeric copy
```

### Internal Representation

`Multivector` gains optional fields: `_name`, `_name_latex`, `_name_unicode`,
`_is_symbolic`, `_expr`, `_grade`. The `Expr` class hierarchy remains as the
internal expression tree — it's now an implementation detail, not a public type
that users need to work with directly.

### Consequences

* Good, because there's one type (`Multivector`) for everything
* Good, because naming and evaluation are orthogonal — mix freely
* Good, because `sym()` still works as a convenience alias
* Good, because the `Expr` tree is preserved for simplification
* Good, because `Multivector` operators build trees when needed
* Neutral, because `Multivector` is slightly heavier (7 extra slots)
* Bad, because `Expr` objects still exist internally — two representations
