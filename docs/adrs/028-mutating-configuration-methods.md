---
status: accepted
date: 2026-03-26
deciders: edouard
supersedes: partially supersedes ADR-018
---

# ADR-028: Mutating Symbolic Configuration Methods

## Context and Problem Statement

The methods `.name()`, `.anon()`, `.lazy()`, and `.eager()` configure how a
multivector participates in symbolic expressions. Should they mutate the
object in-place or return copies?

## Decision Outcome

All four methods **mutate in-place** and return `self`. In addition,
`.name()` also enables lazy (symbolic) mode by default.

`.eval()` is the sole non-mutating method — it returns a new anonymous
eager copy.

```python
R = (e1 ^ e2).name("R")   # mutates, sets lazy
v = e1.name("v")
expr = R * v * ~R          # symbolic expression

concrete = expr.eval()     # new copy, does not mutate expr
```

## Rationale

### 1. Align with Python's object model

Python uses reference semantics (`A = B` binds names, not values). Mutating
these methods follows that model, avoiding surprising "looks like a mutation
but returns a copy" behavior. It keeps the API honest and predictable for
Python users.

### 2. Optimize for interactive, symbolic workflows

These methods are primarily used to configure how an object participates in
symbolic expressions (naming, propagation, display). Treating them as state
changes enables a clean, fluent style:

```python
R = (e1 ^ e2).name("R")
v = e1.name("v")
expr = R * v * ~R
```

This reduces rebinding noise and reads like manipulating mathematical objects.

### 3. `.name()` as the common entry to symbolic mode

In practice, naming is the dominant way users introduce symbols. Making
`.name()` also set the lazy flag:

- matches user intent ("this is now a symbol"),
- avoids extra calls (`.name(...).lazy()`),
- keeps the common path concise.

An override for the implicit lazy is simply `.name("foo").eager()`.

### 4. Clear separation of concerns

- **State/configuration methods mutate:** `.name()`, `.anon()`, `.lazy()`, `.eager()`
- **Computation does not mutate:** `.eval()` returns a new concrete value

This keeps side effects localized and predictable.

### 5. Provide an explicit escape hatch

Because mutation implies shared references, a cheap, explicit cloning method
is provided:

```python
R2 = sym(R, "R2")   # copy with new name
```

This restores value-like workflows when needed, without complicating the
default model.

### 6. Consistency over purity

A consistent mutating model is simpler than a mixed model. It avoids
ambiguity about which methods copy vs mutate and keeps mental overhead low.

## Consequences

* Good, because the API is fluent and concise for the common case
* Good, because it aligns with Python's reference semantics
* Good, because `.eval()` provides a clear non-mutating escape
* Good, because `sym()` provides explicit cloning when needed
* Neutral, because users must be aware of shared references
* Bad, because mutation can surprise users expecting functional style
