---
status: accepted
date: 2026-03-28
deciders: edouard
---

# ADR-034: Three-Phase LaTeX Render Pipeline

## Context and Problem Statement

The original LaTeX renderer was a single recursive function that walked
the Expr tree and produced strings directly. Some typesetting decisions
depend on context that isn't available during a single walk — e.g.
`\frac` should become inline `/` when inside a superscript. A string-
replace hack was used initially but was fragile.

## Decision Outcome

LaTeX rendering uses a three-phase pipeline with an intermediate tree:

```
Expr  →  latex_build()   →  LNode tree
      →  latex_rewrite() →  LNode tree (transformed)
      →  latex_emit()    →  str
```

### Modules

| Module | Responsibility |
|--------|---------------|
| `latex_nodes.py` | LNode types: Text, Seq, Frac, Sup, Parens, Command |
| `latex_build.py` | Expr → LNode (precedence, notation rules) |
| `latex_rewrite.py` | Context-dependent transforms |
| `latex_emit.py` | LNode → string serialization |

### Current Rewrites

1. **Frac in Sup → inline slash**: `e^{a/b}` not `e^{\frac{a}{b}}`
2. **Collapse nested Parens**: `\left(\left(x\right)\right)` → `\left(x\right)`
3. **Hoist negation from Frac**: `\frac{-a}{b}` → `-\frac{a}{b}`
4. **Simplify Frac/1**: `\frac{a}{1}` → `a`

### Notation Kind: `superscript`

A new notation rule kind `superscript` emits `Sup(child, Text(symbol))`.
Users write just the symbol (e.g. `r"\dagger"`), not the `^{...}` wrapper.
The emitter auto-braces `Sup`-on-`Sup` to prevent double-superscript.

### Consequences

* Good, because context-dependent rewrites are clean and testable
* Good, because adding new rewrites is ~5 lines in `latex_rewrite.py`
* Good, because each module has a single responsibility
* Good, because the `superscript` kind hides LaTeX boilerplate from users
* Neutral, because unicode rendering still uses the single-pass approach
