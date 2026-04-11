---
status: accepted
date: 2026-03-25
deciders: edouard
---

# ADR-019: Basis Blades as Named Eager Multivectors

## Context and Problem Statement

Basis blades like `e1`, `e2`, `e12` are fundamental values. They need stable
display names (`e₁`, `e₁₂`) and should behave as concrete numeric objects.
But with the new naming/evaluation semantics (ADR-018), calling `.name()`
makes objects lazy by default. How should basis blades work?

## Decision Drivers

* Basis blades must print by name: `e₁`, not `[0, 1, 0, 0, 0, 0, 0, 0]`
* They must be eager — no symbolic overhead for basic arithmetic
* `e1 ^ e2` between two eager blades must stay eager and produce `e₁₂`
* Naming a blade differently (`e1.name("x")`) should work naturally
* Basis blades should carry correct names for all three formats (ascii,
  unicode, latex) based on the algebra's naming scheme

## Decision Outcome

`Algebra.basis_vectors()`, `pseudoscalar()`, and `blade()` return multivectors
that are **named + numeric**: `_name` is set, `_is_symbolic` is `False`.

```python
alg = Algebra((1, 1, 1))
e1, e2, e3 = alg.basis_vectors()

e1._name          # "e1"
e1._name_unicode  # "e₁"
e1._name_latex    # "e_{1}"
e1._is_symbolic       # False
```

The special display behavior of basis blades (coefficient elision, `e12`
notation) is preserved through the existing `_format()` method, which is
used when a blade is anonymous + eager. When named, the name takes precedence.

Named eager blades participate in lazy operations naturally: when combined
with a lazy operand, they appear by name in the expression tree.

```python
B = (e1 ^ e2).name("B")
print(B + e3)    # B + e₃  (e₃ appears by its blade name)
```

### Consequences

* Good, because `print(e1)` shows `e₁` without any user action
* Good, because `e1 + e2` stays eager (no symbolic overhead)
* Good, because `e1.name("x")` works naturally (override the name)
* Good, because custom naming schemes (gamma, sigma) propagate correctly
* Neutral, because basis blades are slightly heavier than before (name fields)
