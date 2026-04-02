# Changelog

## 0.4.3 (2026-04-03)

### Added

- `Algebra.fraction(a, b)` / `.frac(a, b)` — named scalar fractions that
  render symbolically as `\frac{a}{b}`.
- `Algebra.pi`, `.tau`, `.e`, `.h`, `.hbar`, `.c` — named lazy scalar
  constants with proper LaTeX rendering.
- `SlashFrac` LNode — disambiguates inline fractions in superscripts:
  `e^{(a/2) b}` not `e^{a/2 b}`.

### Fixed

- LaTeX scientific notation: `1.2e-06` now renders as `1.2 \times 10^{-6}`.
- `\frac` no longer wrapped in `\left(...\right)` parens in products —
  the fraction bar provides visual grouping.
- `\frac` before superscript postfix correctly brace-wraps: `{\frac{1}{2}}^2`.

## 0.4.2 (2026-03-31)

### Added

- `unit_fraction` notation kind — renders `unit(x)` as `x/‖x‖` (unicode)
  or `\frac{x}{\lVert x \rVert}` (LaTeX). Opt-in via notation override.
- `Sym.is_compound` and `Sym.has_superscript` properties for structural
  rendering decisions, replacing string-scanning heuristics.

### Fixed

- Postfix operations on compound-named Syms now wrap correctly:
  `dual(a ∧ b)` renders as `(a ∧ b)⋆` not `a ∧ b⋆`.
- LaTeX double-superscript on named Syms: `undual(B^\star)` renders as
  `{B^\star}^{*^{-1}}` not `B^\star^{*^{-1}}`.

## 0.4.1 (2026-03-30)

### Added

- `Notation` exported from main package: `from galaga import Notation`.

### Fixed

- LaTeX double-superscript error when applying postfix operations (dual, undual,
  inverse, etc.) to names containing `^` (e.g. `B^\star`). The inner expression
  is now brace-wrapped: `{B^\star}^{*^{-1}}`.

## 0.4.0 (2026-03-30)

### Breaking Changes

- Removed `galaga.symbolic` module. Import functions from `galaga` directly,
  Expr nodes from `galaga.expr`, and `simplify` from `galaga` or `galaga.simplify`.
- Removed standalone `scalar()` function. Use `.scalar_part` property instead.
- `Notation.functional()` now uses long-form names (`geometric_product`, `outer_product`).
  Use `Notation.functional_short()` for short names (`gp`, `op`, `rev`, etc.).

### Added

- `Notation.functional_short()` preset with short-form function names.
- `Notation` exported from main package: `from galaga import Notation`.
- `sym` and `simplify` exported from main package: `from galaga import sym, simplify`.
- `pseudoscalar(lazy=True)` flag for lazy pseudoscalar.
- `scalar_sqrt()` is now symbolic — renders as `√(...)` / `\sqrt{...}`.
- `scalar_sqrt()` accepts plain `int`/`float` as well as `Multivector`.
- `Multivector.copy_as()` — non-mutating named copy.
- `display(compact=True)` for tight `=` separator.
- `display().latex(coeff_format=)` applies format to eval part only.

### Fixed

- Near-unit coefficients (e.g. `-0.9999999999999998`) display as `-e₂` not `-1e₂`.
- Expression rendering: `a + (-3)b` renders as `a - 3b` in unicode and LaTeX.
- LaTeX accents: `\widetilde` for multi-char names, `\tilde` for single glyphs.
- LaTeX `\operatorname` escapes underscores in function names.
- `Notation.functional()` now correctly overrides all wrap operations
  (exp, log, norm, unit, grade, sqrt, even, odd).
- Notation-first rendering: notation rules drive all rendering decisions,
  eliminating special cases that bypassed the notation system.

## 0.3.12 (2026-03-30)

### Breaking Changes

- Removed standalone `scalar()` function. Use `.scalar_part` property instead:
  `scalar(mv)` → `mv.scalar_part`. `alg.scalar(value)` (the algebra method) is unchanged.

### Added

- `Notation.functional_short()` preset — short-form function names (`gp`, `op`, etc.).
  `Notation.functional()` now uses long-form names (`geometric_product`, `outer_product`, etc.).
- `display().latex(coeff_format=)` — format spec applies to the numeric eval part only,
  preserving symbolic name and expression parts.

### Fixed

- Near-unit coefficients (e.g. `-0.9999999999999998`) now display as `-e₂` not `-1e₂`.
  Affects both unicode and LaTeX rendering after floating-point trig operations.
- Notation-first rendering refactor: notation rules now drive all rendering decisions,
  eliminating special cases that bypassed the notation system.

## 0.3.11 (2026-03-30)

### Added

- `Notation.functional()` preset — renders all operations as function calls
  (e.g. `gp(a, b)`, `op(a, b)`, `reverse(a)`) in unicode and LaTeX.

## 0.3.10 (2026-03-29)

### Added

- `display(compact=True)` — uses `=` instead of `\quad = \quad` for tighter layout.

### Fixed

- LaTeX accents now use `\widetilde` / `\overline` for multi-character names
  (e.g. `SR`) and `\tilde` / `\bar` for single glyphs (including LaTeX commands
  like `\theta`).

## 0.3.9 (2026-03-29)

### Added

- `Multivector.copy_as()` — non-mutating named copy. Same signature as
  `.name()` but returns a new object instead of mutating in place.

## 0.3.8 (2026-03-29)

### Added

- `scalar_sqrt()` is now symbolic — renders as `√(...)` in unicode and
  `\sqrt{...}` in LaTeX. Works with `display()` and `gm.md()`.
- `scalar_sqrt()` accepts plain `int`/`float` as well as `Multivector`.
- Release process documentation (`docs/RELEASE_PROCESS.md`).

### Fixed

- Auto-fix markdown lint in release script after changelog edit.

## 0.3.7 (2026-03-29)

### Added

- `scalar_sqrt()` — square root of scalar multivectors, returns a Multivector.
  Raises ValueError for non-scalar or negative inputs.

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
