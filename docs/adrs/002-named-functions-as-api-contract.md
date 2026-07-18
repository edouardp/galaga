---
status: partially superseded by 074
date: 2026-03-25
deciders: edouard
---

# ADR-002: Named Functions as the Stable API Contract

> ADR-074 retains named functions as the contract but makes long, explicit
> names canonical in Galaga 2. The short canonical-name examples below are the
> historical Galaga v1 decision.

## Context and Problem Statement

Geometric algebra has many operations (geometric product, outer product, inner
products, grade projection, etc.) and Python operators (`*`, `^`, `|`, `~`)
can only represent a few of them. How do we provide a stable, unambiguous API?

## Decision Drivers

* Operators are overloaded and their meaning varies across GA libraries
* Users need to know exactly which operation they're calling
* The API should be stable — renaming a function is a breaking change

## Considered Options

1. Operator-first API with named functions as fallback
2. Named functions as the contract, operators as sugar
3. Method-based API (`v.gp(w)`, `v.op(w)`)

## Decision Outcome

Chosen option: "Named functions as the contract, operators as sugar" because
it eliminates ambiguity and provides a stable surface that won't change.

`gp`, `op`, `grade`, `reverse`, `dual`, `inverse` — these names are the API.
`*`, `^`, `|`, `~` are convenience that maps to specific named functions.

### Consequences

* Good, because `gp(a, b)` is unambiguous — it's always the geometric product
* Good, because operators can be reassigned without breaking the named API
* Good, because the symbolic layer can provide drop-in replacements
* Bad, because `gp(a, b)` is more verbose than `a * b`
