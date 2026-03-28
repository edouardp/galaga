---
status: accepted
date: 2026-03-27
deciders: edouard
---

# ADR-029: Configurable Notation System

## Context and Problem Statement

Geometric algebra has many competing notations. Reverse alone can be
written as `~x`, `x̃`, `x†`, `x^†`, `x^R`, or `rev(x)`. Different
textbooks, fields, and communities use different conventions. The
renderer needs to support all of them without hardcoding any single choice.

## Decision Outcome

A `Notation` class holds rendering rules for every expression node type,
in three formats (ascii, unicode, latex). The renderer queries the
`Notation` object instead of hardcoded tables. Each `Algebra` holds its
own `Notation` instance.

### Rule Kinds

| Kind | Example | Use |
|------|---------|-----|
| `prefix` | `-x`, `inv(x)` | Symbol prepended |
| `postfix` | `x†`, `x⁻¹` | Symbol appended |
| `accent` | `x̃` / `~(a+b)` | Combining char for atoms, fallback for compounds |
| `infix` | `a∧b`, `a·b` | Symbol between operands |
| `wrap` | `⟨x⟩₁`, `exp(x)` | Open/close delimiters |
| `juxtaposition` | `ab` | No symbol, smart spacing |

### Override API

```python
from galaga.notation import NotationRule

# Per-algebra override
alg.notation.set("Reverse", "unicode", NotationRule(kind="postfix", symbol="†"))
alg.notation.set("Reverse", "latex", NotationRule(kind="postfix", symbol="^\\dagger"))

# Copy for isolation
custom = alg.notation.copy()
custom.set("Dual", "unicode", NotationRule(kind="prefix", symbol="*"))
alg2 = Algebra((1,1,1), notation=custom)
```

### Consequences

* Good, because any notation convention can be expressed
* Good, because defaults match the current rendering (no breaking change)
* Good, because overrides are per-algebra (different algebras can use different conventions)
* Good, because `Notation.copy()` enables safe preset sharing
* Neutral, because the rule dataclass has many fields (most unused per rule)
