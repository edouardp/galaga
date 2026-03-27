---
status: superseded
date: 2026-03-25
deciders: edouard
superseded-by: ADR-033
---

# ADR-012: Unicode Repr with Opt-In Flag

## Context and Problem Statement

Multivectors can be displayed as ASCII (`e12`, `e1 + e2`) or Unicode
(`e₁₂`, `e₁ + e₂`). Which should be the default?

## Decision Drivers

* ASCII is safe everywhere — terminals, logs, CI output
* Unicode is much more readable for interactive use and notebooks
* Named algebras (gamma, sigma) look best in Unicode (`γ₀`, `σₓ`)
* Changing the default would break existing output expectations

## Decision Outcome

ASCII is the default. Unicode is opt-in via `Algebra(sig, repr_unicode=True)`.

When enabled, `str()` and `repr()` both produce Unicode output with subscript
digits, Greek letters for named bases, and `𝑰` for the pseudoscalar.

### Consequences

* Good, because default output is safe for all environments
* Good, because notebook users get beautiful output with one flag
* Good, because the flag is per-algebra, not global state
