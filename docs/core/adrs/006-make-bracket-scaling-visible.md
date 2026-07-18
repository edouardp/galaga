---
status: accepted
date: 2026-07-18
deciders: edouard
---

# ADR-006: Make Bracket Scaling Visible in Function Names

## Context and problem statement

The old Galaga commutator and anticommutator history mixed raw and half-scaled
conventions. A hidden factor of one half is especially easy to miss because GA
libraries often call the half-commutator the commutator product. Lie and Jordan
terminology also varies: an associative algebra's canonical Lie bracket is the
raw commutator, while many Jordan-algebra texts normalize the symmetric
product by one half.

The function name should disclose scaling rather than require a user to know a
library-specific convention.

## Decision drivers

- Match the ordinary mathematical commutator `AB - BA`.
- Avoid hidden numerical scaling.
- Provide the half-scaled GA operations explicitly.
- Avoid boolean flags that change algebraic definitions.
- Make the Galaga migration break visible.

## Considered options

1. Keep half scaling in `commutator` and `anticommutator`.
2. Use `half=True` mode flags.
3. Keep Lie/Jordan half-scaled but make only commutator names raw.
4. Make all unqualified family names raw and reserve half scaling for
   `half_...` names.

## Decision outcome

Define:

```text
commutator(A,B)          = AB - BA
lie_bracket(A,B)         = AB - BA
half_commutator(A,B)     = (AB - BA) / 2

anticommutator(A,B)      = AB + BA
jordan_product(A,B)      = AB + BA
half_anticommutator(A,B) = (AB + BA) / 2
```

This project convention intentionally uses an unnormalized `jordan_product`.
Code following the common half-scaled Jordan convention must call
`half_anticommutator` explicitly.

## Consequences

- Good, because scaling is visible and searchable.
- Good, because `lie_bracket` matches the canonical bracket induced by an
  associative algebra.
- Good, because vector metric pairing is visibly `half_anticommutator`.
- Breaking, because old Galaga Lie/Jordan expectations must be migrated.
- Neutral, because users following half-scaled GA conventions have longer but
  unambiguous function names.
