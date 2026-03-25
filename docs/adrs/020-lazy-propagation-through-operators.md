---
status: accepted
date: 2026-03-25
deciders: edouard
---

# ADR-020: Lazy Propagation Through Operators

## Context and Problem Statement

With the unified naming/evaluation model (ADR-018), multivectors can be lazy
or eager. When a lazy MV participates in an operation with an eager MV, what
should the result be? And how should the expression tree be built?

## Decision Drivers

* Lazy values exist to preserve symbolic structure — that structure should
  survive through operations
* Eager-only operations should have zero overhead (no tree building)
* The result must always have correct numeric data (for `.eager()` / `.eval()`)
* Named operands should appear by name in expression trees

## Decision Outcome

### Propagation Rule

**Lazy is contagious**: if any operand is lazy, the result is lazy.

| Left | Right | Result |
|------|-------|--------|
| Eager | Eager | Eager |
| Lazy | Eager | Lazy |
| Eager | Lazy | Lazy |
| Lazy | Lazy | Lazy |

### Dual Representation

Lazy results carry both:
1. **Concrete data** — the numeric result, computed eagerly for `.data` access
2. **Expression tree** — the symbolic structure, for display and simplification

This means `.eager()` on a lazy result is instant (data is already computed),
and `.anon()` reveals the expression tree without evaluation.

### Name Handling in Trees

Names do **not** propagate through operations — the result is always anonymous.
But named operands appear by name in the expression tree:

```python
B = (e1 ^ e2).name("B")
x = B + e3
x._name       # None (anonymous)
str(x)        # "B + e₃" (B appears by name in the tree)
```

Named eager blades (like `e3`) also appear by name when they enter a lazy
expression, using their blade display name.

### Eager Fast Path

When all operands are eager, the operator overloads take the existing fast
path — no imports from `ga.symbolic`, no tree construction, no overhead.

### Consequences

* Good, because symbolic structure is preserved through chains of operations
* Good, because eager arithmetic has zero overhead
* Good, because `.eager()` is instant (data pre-computed)
* Good, because named values appear naturally in expression trees
* Neutral, because lazy results use ~2x memory (data + tree)
