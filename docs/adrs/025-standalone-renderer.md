---
status: accepted
date: 2026-03-26
deciders: edouard
---

# ADR-025: Standalone Precedence-Aware Renderer

## Context and Problem Statement

The original rendering approach had each `Expr` node implement its own
`__str__()` and `_latex()` methods. This led to 16 parenthesization bugs
because each node had to independently decide whether its children needed
wrapping — a never-ending source of errors, especially for postfix unary
operators (reverse, dual, inverse) on compound expressions.

## Decision Outcome

A standalone tree-walking renderer (`ga.render`) with a data-driven
`OpInfo` registry. Each node type declares its precedence, associativity,
and whether it's flattenable (associative):

```python
INFO = {
    Sym:  OpInfo(prec=100),
    Gp:   OpInfo(prec=80, assoc=Assoc.LEFT, flat=True),
    Op:   OpInfo(prec=70, assoc=Assoc.LEFT, flat=True),
    Add:  OpInfo(prec=60, assoc=Assoc.LEFT, flat=True),
    ...
}
```

A single `_needs_wrap` function handles all parenthesization decisions
by comparing child precedence to parent threshold. Flattenable ops
(Gp, Op, Add) skip wrapping when the child is the same type.

Both `render()` (unicode) and `render_latex()` (LaTeX) use the same
precedence logic. `Multivector.__str__()` and `.latex()` delegate to
the renderer for lazy expressions.

### Consequences

* Good, because parenthesization is correct by construction
* Good, because adding a new op is one registry entry, no rendering code
* Good, because LaTeX uses wide accents (`\widetilde`) for compound expressions
* Good, because associative ops flatten: `(a∧b)∧c` → `a∧b∧c`
