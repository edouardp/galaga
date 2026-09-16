---
status: accepted
date: 2026-09-16
deciders: edouard
---

# ADR-140: Shift Operators for Contractions

## Context and Problem Statement

Galaga exposes left and right contractions as separate named operations because
their grade selection and operand order are distinct. The named functions are
unambiguous, but contractions are common enough to benefit from concise Python
operators.

Libraries use several conventions. Some use `<<` and `>>` as a pair, while
others use `<` and `>`, only provide `<<`, or assign `>>` to another operation.

## Decision Outcome

Galaga adopts the paired Python convention:

```python
a << B  # left_contraction(a, B)
A >> b  # right_contraction(A, b)
```

The explicit functions remain the canonical spelling for code where the
contraction convention should be immediately visible:

```python
left_contraction(a, B)
right_contraction(A, b)
```

Both operators preserve expression provenance as the corresponding named
operation. They support the same multivector/scalar coercion policy as the
existing binary product operators.

## Consequences

* The two contractions have a compact, symmetric Python spelling.
* The choice is deliberately documented because `>>` is not universal across
  geometric-algebra libraries.
* Users migrating from libraries that use `>>` for sandwich products must use
  Galaga's explicit `sandwich(...)` operation instead.
* Python shift precedence remains lower than multiplication and should be
  considered when writing compound expressions.
