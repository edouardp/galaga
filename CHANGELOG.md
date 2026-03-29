# Changelog

## 0.3.6 (2026-03-29)

### Fixed

- Expression tree rendering: `a + (-3)b` now renders as `a - 3b` in both
  unicode and LaTeX, instead of `a + -3b`. Fixes spurious duplicates in
  `display()` where reveal and eval differed only by sign formatting.

## 0.3.5 (2026-03-29)

### Added

- `pseudoscalar(lazy=True)` flag for lazy pseudoscalar in symbolic workflows
- Ruff, shellcheck, bandit, rumdl, pip-audit, pyrefly linting toolchain
- Pre-commit hooks for automated quality gates
- Low-dimensional algebra tests (Cl(0), Cl(1), Cl(2), degenerate)
- Docstrings on all 1259 test methods
- Examples reorganised into subfolders: basics, algebra, physics, quantum, pga, spacetime

### Fixed

- `rotor()` now rejects pure scalars — must have a grade-2 component
- README: corrected `|` operator docs, commutator/anticommutator definitions,
  install instructions, test paths, repr docs

## 0.3.3 (2026-03-28)

### Fixed

- README: corrected `|` operator documentation (is Doran–Lasenby inner, not left contraction)
- README: fixed commutator/anticommutator definitions (were showing halved Lie/Jordan forms)
- README: fixed LaTeX example output, install instructions, test paths and counts
- README: updated title and references from `ga` to `galaga`
- README: repr now documented as unicode-by-default

## 0.3.2 (2026-03-28)

### Fixed

- Expression trees now use proper LaTeX names for all basis vectors and blades
  (e.g. `e_{1}`, `e_{12}`, `\sigma_1`, `\gamma_0`) instead of unicode names.
  This fixes `display()` showing duplicate entries like `e₁ + e₂ = e_{1} + e_{2}`
  and ensures consistent LaTeX rendering throughout symbolic expressions.

## 0.3.1 (2026-03-28)

### Fixed

- `Multivector.display()` now returns a LaTeX-renderable object instead of a
  plain string, so it works correctly with `gm.md(t"{mv.display()}")` in
  galaga-marimo notebooks. The result has `.latex()` and `._repr_latex_()`
  methods for automatic detection.

## 0.2.1 (2026-03-28)

### Added

- `Multivector.display()` — returns a LaTeX string showing the progression
  from name to expression to numeric value (e.g. `R = e^{-B/2} = 0.878 - 0.479 e_{12}`),
  automatically omitting duplicate parts.

## 0.2.0 (2026-03-28)

### Breaking Changes

- **Module renamed from `ga` to `galaga`** — all imports must be updated:
  - `from ga import Algebra` → `from galaga import Algebra`
  - `from ga.symbolic import sym` → `from galaga.symbolic import sym`
  - `from ga.notation import Notation` → `from galaga.notation import Notation`
  - `import ga` → `import galaga`

The package name on PyPI (`galaga`) now matches the Python import name.

## 0.1.1 (2026-03-28)

### Packaging & Infrastructure

- Renamed `packages/gamo` to `packages/galaga_marimo` for consistency
- Fixed project URLs to point to correct GitHub repository
- Lowered numpy minimum to `>=1.24` for broader compatibility
- Pinned galaga-marimo dependencies (`galaga>=0.1.0`, `marimo>=0.21.1`)
- Removed workspace-only `[tool.uv.sources]` from galaga-marimo
- Added `py.typed` marker for type checker support
- Added publish scripts, Makefile, and automated release workflow

## 0.1.0 (2026-03-28)

Initial release.

### galaga

- Algebra construction from signature tuples
- Full product suite: gp, op, left/right contraction, Doran–Lasenby inner,
  Hestenes inner, scalar product, commutator, anticommutator, lie_bracket,
  jordan_product
- Unary operations: reverse, involute, conjugate, grade, dual, undual,
  complement, norm, unit, inverse, exp, log
- Symbolic expression trees with LaTeX/Unicode rendering
- Simplification engine with fixed-point iteration
- Unicode pretty-printing with opt-in flag
- Rotor construction with validation and auto-normalisation

### galaga-marimo

- Marimo notebook helpers with t-string powered LaTeX rendering
- Dynamic markdown rendering via `gm.md()`
