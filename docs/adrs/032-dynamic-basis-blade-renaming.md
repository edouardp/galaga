---
status: superseded by ADR-057
date: 2026-03-27
deciders: edouard
---

# ADR-032: Dynamic BasisBlade Renaming

## Context and Problem Statement

Users need to rename basis blades after algebra construction — e.g.
calling the pseudoscalar "I", or naming bivectors as angular momentum
components. The rename must affect all existing multivectors immediately,
not just newly created ones.

## Decision Outcome

Each Algebra holds a dict of `BasisBlade` objects (one per bitmask).
Rendering reads from these at render time, not from cached names on
the Multivector. This means renaming a BasisBlade immediately affects
all existing MVs.

```python
alg.get_basis_blade(e1 ^ e2).rename(unicode="σ₁₂", latex=r"\sigma_{12}")
# All existing MVs containing e₁₂ now render with the new name
```

### Why not cache names on MVs?

If names were cached on the Multivector at construction time, renaming
a BasisBlade would only affect newly created MVs. Users would have to
re-fetch basis vectors after every rename — error-prone and surprising.

### Why no pseudoscalar special case?

The pseudoscalar is no longer auto-named "I". It renders as its blade
name (e₁₂₃) like any other blade. Users who want "I" rename it:

```python
alg.get_basis_blade(alg.pseudoscalar()).rename(unicode="𝑰", latex="I")
```

This is consistent and explicit.

### Consequences

* Good, because renames are live and global within an algebra
* Good, because no special cases for pseudoscalar
* Good, because `get_basis_blade()` accepts both MVs and bitmask ints
* Neutral, because basis vector MVs don't carry cached names
