---
status: accepted
date: 2026-03-27
deciders: edouard
supersedes: ADR-012
---

# ADR-033: Unicode repr() by Default

## Context and Problem Statement

ADR-012 made `repr()` use ASCII by default, with `repr_unicode=True` as
opt-in. But with lazy basis blades, this created an inconsistency:
eager `e1^e2` showed `e12` (ASCII) while lazy `e1^e2` showed `e₁∧e₂`
(unicode from the expression tree).

## Decision Outcome

`repr()` now returns the same as `str()` — unicode everywhere.
The `repr_unicode` parameter on Algebra is accepted but ignored.

```python
>>> e1 ^ e2
e₁₂           # was: e12
>>> e1
e₁            # was: e1
```

### Why?

- Consistency: eager and lazy render the same way
- Modern terminals and editors handle unicode fine
- The REPL experience is much better with subscripts and Greek letters
- ASCII is still available via `format(mv, 'a')` when needed

### Consequences

* Good, because eager and lazy rendering are consistent
* Good, because the REPL shows the same output as print()
* Breaking, because `repr()` output changed from ASCII to unicode
* Neutral, because `repr_unicode` parameter is silently accepted
