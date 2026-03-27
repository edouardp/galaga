---
status: accepted
date: 2026-03-26
deciders: edouard
---

# ADR-027: Geometric Product Spacing for Multi-Character Names

## Context and Problem Statement

The geometric product renders as juxtaposition (no operator symbol).
With single-character names this is fine: `abc` clearly means `a*b*c`.
But with multi-character names, `pive` is ambiguous — is it `pi*ve`,
`p*i*v*e`, or a single name?

## Decision Outcome

Space between factors only when an immediate child `Sym` has a
multi-character name (ignoring combining diacriticals and sub/superscripts).

| Expression | Rendering | Why |
|---|---|---|
| `a * b * c` | `abc` | All single-char |
| `R * v * ~R` | `RvR̃` | All single-char (tilde is combining) |
| `e₁ * e₂` | `e₁e₂` | Subscripts don't count |
| `pi * ve` | `pi ve` | Multi-char names need separation |
| `a * pi` | `a pi` | Mixed: space for clarity |

The check uses `_has_multichar_name()` which walks through `Neg`,
`ScalarMul`, and postfix unary nodes to find the underlying `Sym`.

### Consequences

* Good, because `abc` and `RvR̃` stay compact
* Good, because `pi ve` is unambiguous
* Neutral, because the heuristic is name-based, not content-based
