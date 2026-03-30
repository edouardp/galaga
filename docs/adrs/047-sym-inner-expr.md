---
status: accepted
date: 2026-03-30
deciders: edouard
---

# ADR-047: Sym Inner Expression for Structural Rendering Decisions

## Context and Problem Statement

The renderers needed to detect whether a Sym node's name was "compound"
(e.g. `a \wedge b`) or "simple" (e.g. `B`) to decide whether to wrap it
in parentheses for postfix operations. Similarly, they needed to detect
superscripts in names to avoid double-superscript LaTeX errors.

These checks were implemented as string-scanning heuristics scattered
across render.py and latex_build.py — checking for `\wedge`, `∧`, `^`,
etc. in the name text. Each new edge case required adding another string
pattern, creating a whack-a-mole maintenance problem.

## Decision Outcome

Store the original expression tree inside Sym nodes as `inner_expr`.
Add two properties that use structural information:

- `Sym.is_compound` — True when inner_expr is a binary operation AND the
  name contains spaces (indicating the user didn't abbreviate it)
- `Sym.has_superscript` — True when the latex name contains `^`

### Fallback

When `inner_expr` is None (Sym created directly, not from a named MV),
`is_compound` falls back to scanning the name string for operator patterns.
This covers test helpers and anonymous eager MVs entering expression trees.

### Consequences

- Good, because rendering decisions use tree structure, not string patterns
- Good, because new operators are automatically handled (no pattern list)
- Good, because detection logic is centralised on Sym, not scattered
- Neutral, because `has_superscript` is still string-based (correct — it's
  about the name's rendering, not the expression structure)
- Neutral, because the fallback retains string scanning for edge cases
