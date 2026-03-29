---
status: accepted
date: 2026-03-29
deciders: edouard
---

# ADR-042: scalar_sqrt as a Symbolic-First Convenience

## Context and Problem Statement

Users building physics notebooks need expressions like `E = √(m² + p_x²)` to
render symbolically in LaTeX (`\sqrt{m^2 + p_{x}^2}`) and unicode (`√(m² + p_x²)`).
Without this, they must either take a dependency on SymPy for symbolic rendering
or manually construct LaTeX strings.

## Decision Outcome

Add `scalar_sqrt()` as a symbolic-aware function with a `Sqrt` expression node,
notation rules, and rendering in both unicode and LaTeX.

### Code Smell Acknowledgement

This function fits poorly into the library's architecture:

- **Not a GA operation.** Square root is a scalar function, not a geometric
  algebra operation. Every other function in the library (`gp`, `op`, `grade`,
  `reverse`, etc.) is a genuine GA operation on multivectors.
- **Inconsistent return type.** Accepts both `Multivector` and plain `int`/`float`,
  returning the same type back. No other function in the library does this.
- **Validation is domain-specific.** The "must be scalar, must be non-negative"
  checks are arithmetic constraints, not algebraic ones.

### Why It's Justified

The symbolic rendering payoff is significant:

- `scalar_sqrt(m**2 + p_x**2)` renders as `√(m² + p_x²)` / `\sqrt{m^2 + p_{x}^2}`
  with zero user effort — it just works in `display()` and `gm.md()`.
- The alternative is taking a dependency on SymPy, which is a 50MB+ package
  with its own expression system that would need bridging to our Expr trees.
- Physics notebooks use `√` constantly (energy-momentum, norms, uncertainties).
  Making users manually construct `$\sqrt{...}$` strings defeats the purpose
  of the symbolic layer.

### Consequences

- Good, because physics expressions render naturally without SymPy
- Good, because it follows the existing `@lazy_unary` / Expr node pattern
- Bad, because it's not a GA operation — sets a precedent for scalar math functions
- Bad, because the plain number acceptance is architecturally inconsistent
- Acceptable, because the scope is deliberately narrow (one function, not a
  general scalar math library)

### Future Considerations

If more scalar math functions are needed (abs, sin, cos, etc.), consider
whether they belong in galaga or in a separate thin rendering layer. The
current decision is to keep it to just `scalar_sqrt` and reassess if the
pattern grows.
