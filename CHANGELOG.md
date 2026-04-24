# Changelog

## 1.6.2 (2026-04-24)

### Fixed

- **Scientific notation in expression trees** — Symbolic expressions with small
coefficients (|c| < 1e-6) now render as `1.2 \times 10^{-7}` in LaTeX instead
of raw `1.2e-07`. Affects `Scalar`, `ScalarMul`, and `ScalarDiv` expression
nodes. Respects `alg.notation.scientific` setting (`"times"`, `"cdot"`, `"raw"`).

### Changed

- **`fmt_coeff` / `sci_lnode` moved to `latex_nodes.py`** — Coefficient formatting
helpers are now shared between the eager MV path (`algebra.py`) and the expression
tree path (`latex_build.py`). No API change — these are internal functions.

## 1.6.1 (2026-04-19)

### Fixed

- **`recognize=` uses MV's own LaTeX name** — Labels are now pulled from each known MV's
`.name(latex=...)` instead of requiring explicit dict keys. Pass any collection (list, tuple,
dict) of named MVs — no label duplication needed.

- **`recognize=` shows all matching labels** — When multiple known MVs match a result, all are
shown (e.g. `(≡ \uparrow ≡ |0⟩)`) instead of only the first.

## 1.6.0 (2026-04-19)

### Added

- **Basis vector protection** — Basis vectors returned by `basis_vectors()`, `basis_blades()`,
`locals()`, `pseudoscalar()`, and `blade()` are now protected from in-place mutation. Calling
`.name()` on a basis vector returns a named copy instead of mutating the original. The common
pattern `v = e1.name("v")` continues to work unchanged. (ADR-067)

- **`recognize=` for known MV annotation** (galaga-marimo) — `gm.md()` and `Doc.md()` accept a
`recognize={label: mv, ...}` dict. When a rendered multivector's numeric value matches a known,
`(≡ label)` is appended in LaTeX. Useful for identifying computed results as named states in
quantum/physics notebooks. (ADR-068)

## 1.5.0 (2026-04-19)

### Added

- **Basis vector protection** — Basis vectors returned by `basis_vectors()`, `basis_blades()`,
`locals()`, `pseudoscalar()`, and `blade()` are now protected from in-place mutation. Calling
`.name()` on a basis vector returns a named copy instead of mutating the original. The common
pattern `v = e1.name("v")` continues to work unchanged. (ADR-067)

## 1.4.3 (2026-04-15)

### Fixed

- **`latex()` respects `display_repr=True`** — `Multivector.latex()` now delegates to `display()`
  when the algebra has `display_repr=True`, so `galaga_marimo.md(t"{v}")` renders the
  full `name = expression = value` form without needing `{v.display()}`. Previously only `__repr__`,
  `__str__`, and `_repr_latex_` honoured the flag. (ADR-061)

## 1.4.2 (2026-04-13)

### Added

- **`norm2()` renders symbolically** — `norm2(v)` now displays as `‖v‖²` (unicode) and `\lVert v \rVert^{2}` (LaTeX) instead of expanding to `⟨v~v⟩₀`.

## 1.4.0 (2026-04-13)

### Added

- **`__float__()` and `__abs__()` on Multivector** — `float(mv)` returns the scalar coefficient for grade-0
  multivectors, raises `TypeError` with a descriptive message otherwise. `abs(mv)` delegates to
  `abs(float(mv))`. (ADR-066)
- **Automatic grade propagation** — 18 of 29 GA operations now propagate `_grade` through the `@ga_op`
  wrapper. Factory methods (`scalar()`, `basis_vectors()`, `pseudoscalar()`, `vector()`, `basis_blades()`,
  `locals()`) and `grade(x, k)` also set `_grade` on results. (ADR-066)
- **`ops.py` operation registry** — all 29 GA operations registered via `@ga_op` with algebraic metadata
  (name, arity, grade rule). The symbolic layer registers handlers at import time. (ADR-065)

### Changed

- **`norm2()` returns a scalar Multivector** instead of a bare `float`. Use `float(norm2(x))` where a
  float is needed. (ADR-066)
- **Circular dependency broken** — `algebra.py` no longer imports `expr.py`. The dependency graph is now
  `algebra.py → ops.py ← expr.py` with no cycles. (ADR-065, SPEC-012)
- **Bare `Expr` operands no longer accepted** — `Multivector + Expr` and similar mixed operations now
  return `NotImplemented`, letting Python's operator dispatch handle fallback. This was an internal-only
  pattern with no public API impact.
- **Expression node classes auto-generated** — `expr.py` generates node classes from a `_NODE_NAMES` table
  instead of 31 manual declarations. (SPEC-012 Phase 6)
- **Architecture updated to three layers** — `ops.py` (registry) → `algebra.py` (numeric) → `expr.py`
  (symbolic). Documented in DESIGN_DECISIONS.md.

## 1.3.1 (2026-04-11)

### Changed

- **Renamed `display=` to `display_repr=`** on `Algebra.__init__` — the parameter name now says exactly what it changes. (ADR-061)

## 1.3.0 (2026-04-11)

### Added

- **`symbolic=` alias for `lazy=`** — all basis-returning methods (`basis_vectors()`, `basis_blades()`,
  `pseudoscalar()`, `blade()`, `locals()`) now accept `symbolic=True` as a clearer alternative to
  `lazy=True`. Both work; `symbolic=` is preferred going forward. (ADR-062)
- **`display_repr=True` on `Algebra`** — `Algebra(3, display_repr=True)` makes `repr()` show the
  `.display()` form by default, useful for REPL exploration. Renamed from `display=` for clarity. (ADR-061)
- **`vector_names=` parameter on `b_quaternion()`** — customise the vector basis names
- **Chisolm reference test suite** — 2062+ identities from Chisolm's *Geometric Algebra*
  (arXiv:1205.5935v1) covering products, involutions, duality, commutator identities, projections,
  reflections, rotations, and Lorentz boosts. (ADR-060)

### Fixed

- **Symbolic `ScalarMul(1, x)` no longer renders as `1x`** — both unicode and LaTeX renderers now suppress the unit coefficient for `k == +1`, matching the existing `k == -1` suppression. (ADR-063)
- **Compact-style LaTeX for single-char vector names** — `z` now renders as `z`, not `z_{z}`

### Changed

- **Renamed `lazy` internals to `symbolic`** throughout the codebase. The `lazy=` parameter continues to work as an alias. (ADR-062)

### Docs

- ADR-060: Chisolm paper as reference test suite
- ADR-061: Algebra-level display mode
- ADR-062: Rename lazy to symbolic
- ADR-063: Suppress unit coefficient in symbolic ScalarMul rendering
- Updated SPEC-004, SPEC-008, SPEC-010, README, and all ADRs to use symbolic/numeric terminology
- Clarified `lie_bracket` vs `commutator` convention in docstrings

### Tests

- 5 new Chisolm-derived test files (309 parametrized test cases)
- Regression tests for `ScalarMul(1, x)` suppression
- 1975+ tests passing

## 1.2.0 (2026-04-07)

### Changed

- **`b_complex()` now uses Cl(2,0) even subalgebra** — `i = e₁₂` (bivector),
  consistent with `b_quaternion()`. Use `Algebra(2, blades=b_complex())`
  instead of `Algebra(0, 1, blades=b_complex())`. Complex conjugation is
  now `reverse()` (not `involute()`).

### Added

- **`.bar` property** — shortcut for `conjugate(x)`, alongside `.inv`, `.dag`, `.sq`

### Fixed

- Removed unnecessary `display_order` from `b_complex()` (bitmask order is already correct for Cl(2,0))

## 1.1.1 (2026-04-07)

### Added

- **`b_complex()` convention factory** — Cl(0,1) with basis vector named `i`
- **`b_quaternion()` convention factory** — Cl(3,0) with bivectors `i`, `j`, `k` satisfying Hamilton's identities
- **Custom display ordering** (SPEC-011) — `BladeConvention.display_order` controls term order in rendering and `basis_blades()`; quaternions now display as `1 + 2i + 3j + 4k`
- **`blade()` accepts Multivector and `lazy=`** — `alg.blade(e1^e2, lazy=True)` works
- Improved `dual()` error message in degenerate algebras — guides users to `complement()`
- Hodge star recipe in README
- Example notebook: complex numbers and quaternions (arithmetic, conjugation, Euler's formula, division, log/exp, SLERP, rotation)

### Fixed

- Removed dead code (`_reorder_sign`, unreachable return in `_fmt_coeff`)

### Tests

- 1652 tests, 98% coverage
- 18 quaternion/complex identity and display tests
- 16 display ordering tests
- 14 coverage gap tests

## 1.1.0 (2026-04-06)

### Breaking Changes

- **`pseudoscalar=` renamed to `pss=`** on `b_pga` and `b_cga` factory
  functions, matching the metric-role key used in overrides.

### Added

- `pss=` parameter on all 7 blade convention factories (`b_default`,
  `b_gamma`, `b_sigma`, `b_sigma_xyz`, `b_pga`, `b_sta`, `b_cga`) for
  naming the pseudoscalar without reaching for `overrides=`.

## 1.0.2 (2026-04-06)

### Added

- `Algebra.basis_blades(k)` — returns all basis blades of grade `k` as a
  tuple in canonical order. Complements `basis_vectors()` for higher grades.
  `e12, e13, e23 = alg.basis_blades(2)`.
- `Algebra.locals()` — returns a dict of all basis blades keyed by ASCII
  name, designed for `locals().update(alg.locals())` in notebooks. Supports
  `grades=` filter and `lazy=` flag. Keys follow the blade convention
  (`e1`, `e12`, `y0y1`, `s1`, etc.).

### Fixed

- `basis_blades()` and `locals()` now apply `BasisBlade.sign`, so signed
  conventions (e.g. `b_sta(sigmas=True)` where σ₁ = γ₁γ₀) produce blades
  with the correct coefficient.

## 1.0.1 (2026-04-05)

### Fixed

- `b_sta(sigmas=True)`: blade signs are now computed from the metric via
  `_product_sign()` instead of hardcoded. This fixes incorrect display of
  iσₖ products and makes `b_sta` work correctly for both Cl(1,3) and Cl(3,1).
- `b_sta(pseudovectors=True)`: trivector names are now `iγₖ` (not `iσₖ`),
  with signs computed from the metric.

### Added

- `BasisBlade.sign` field for signed blade names. The display coefficient is
  multiplied by the sign, so `σₖ = γₖγ₀` displays correctly as `σₖ` even
  though the canonical blade `γ₀γₖ` has the opposite sign.
- `TestSignConsistency`: parametrized test that mechanically verifies all
  blade signs against the algebra's geometric product for both Cl(1,3) and
  Cl(3,1).

## 1.0.0 (2026-04-05)

### Breaking Changes

- **`names=` parameter removed** — All blade display configuration now goes
  through `blades=` accepting a `BladeConvention` object. Migration:
  - `names="gamma"` → `blades=b_gamma()`
  - `names="sigma"` → `blades=b_sigma()`
  - `names="sigma_xyz"` → `blades=b_sigma_xyz()`
  - `names=(code, uni)` → `blades=BladeConvention(vector_names=[...])`
- **Default blade style is now compact** — `e₁₂` instead of `e₁e₂`. Use
  `blades=b_default(style="juxtapose")` for the old behavior.
- **`repr_unicode` defaults to `True`** — `repr()` now returns unicode by
  default. Use `repr_unicode=False` for ASCII.

### Added

- **`BladeConvention` system** — New `blades=` parameter on `Algebra` with
  7 convention factories: `b_default`, `b_gamma`, `b_sigma`, `b_sigma_xyz`,
  `b_pga`, `b_sta`, `b_cga`.
- **3 blade styles** — `"compact"` (`e₁₂`), `"juxtapose"` (`e₁e₂`),
  `"wedge"` (`e₁∧e₂`), configurable per factory via `style=`.
- **Metric-role override keys** — Name specific blades using `"+1-1"`, `"_1"`,
  `"pss"` notation that is independent of internal index ordering.
- **`blade()` lookup** — Now accepts metric-role strings, display name matches,
  and prefix+digits with 0-based or 1-based indexing. (Fixes #8)
- **`get_basis_blade()` accepts strings** — Metric-role keys and `"pss"`.
- **`BasisBlade.rename()` positional arg** — Accepts string, 2-tuple, or
  3-tuple matching the override value format.
- **`b_sta(sigmas=True)`** — Opt-in σ₁/σ₂/σ₃ bivector aliases for STA.
- **`b_sta(pseudovectors=True)`** — Opt-in iσ₁/iσ₂/iσ₃ trivector aliases.
- **`b_cga(null_basis="plus_minus")`** — Switch between eₒ/e∞ and e₊/e₋.
- **Full blade naming at construction** — Override any blade via `overrides=`
  dict on any factory. (Fixes #9)

## 0.6.2 (2026-04-05)

### Fixed

- `Algebra(p, q, r)` basis ordering now matches clifford, kingdon, and ganja.js:
  degenerate (r) basis vectors first, then positive (p), then negative (q).
  `Algebra(3, 0, 1)` now produces `(0, 1, 1, 1)` instead of `(1, 1, 1, 0)`.
  The tuple constructor `Algebra((1, 1, 1, 0))` is unchanged — it preserves
  the user's explicit ordering. (Fixes #10)

## 0.6.1 (2026-04-05)

### Added

- **Cl(p,q,r) constructor** — `Algebra(3)`, `Algebra(1, 3)`, `Algebra(3, 0, 1)`
  now work alongside the existing `Algebra((1, 1, 1))` signature form.
- Input validation on `Algebra` constructor: rejects strings, floats, bools,
  negative counts, and invalid signature values (not +1/-1/0) with clear error
  messages.

## 0.6.0 (2026-04-05)

### Added

- **General multivector inverse** — `inverse()` now works for any invertible
  multivector, not just versors. Uses Hitzer closed-form (d ≤ 5) and Shirokov
  iterative algorithm (d ≥ 6). Non-invertible elements raise `ValueError`
  instead of silently returning wrong answers.
- **General square root** — `sqrt()` via Study number decomposition (Roelfs &
  De Keninck 2022). Works for rotors, PGA translators, and any element whose
  non-scalar part squares to a scalar. `scalar_sqrt()` is preserved for
  backward compatibility.
- **Outer transcendental functions** — `outerexp()`, `outersin()`, `outercos()`,
  `outertan()`: wedge-product analogues of the standard transcendentals. The
  series always terminates at grade n.

### Changed

- `inverse()` no longer uses the versor formula `~x / (x * ~x)`. The new
  general inverse produces identical results for versors but now also handles
  arbitrary mixed-grade multivectors correctly.

## 0.5.3 (2026-04-03)

### Added

- `alg.sqrt2` — uses `Sqrt` expression node, displays as `√2 = 1.41421`.
- `alg.tau` — uses `2 * pi` expression tree, displays as `τ = 2π = 6.28319`.
- `Notation.set()` returns `self` for fluent chaining.
- `Notation.with_scientific()` for chaining scientific notation style.
- Input validation on `Notation.set()`: rejects unknown formats and kinds.

### Fixed

- Default LaTeX coefficients use 6 significant digits (matching Python's `:g`)
  instead of 15.

## 0.5.2 (2026-04-03)

### Fixed

- LaTeX default rendering no longer uses scientific notation for coefficients
  with |c| ≥ 1e-6. `alg.c.eval().latex()` now gives `299792458` not
  `2.99792 \times 10^{8}`. Explicit format specs (`:g`, `.3e`) still
  produce scientific notation when appropriate.

## 0.5.1 (2026-04-03)

### Added

- `Notation.set()` now returns `self` for fluent chaining.
- `Notation.with_scientific()` for chaining scientific notation style.
- Input validation on `Notation.set()`: rejects unknown formats and kinds.

## 0.5.0 (2026-04-03)

### Added

- `Algebra.fraction(a, b)` / `.frac(a, b)` — named scalar fractions that
  render symbolically as `\frac{a}{b}`.
- `Algebra.pi`, `.tau`, `.e`, `.h`, `.hbar`, `.c` — named lazy scalar
  constants with proper LaTeX rendering.
- `Notation.scientific` setting — controls LaTeX scientific notation style:
  `"times"` (default), `"cdot"`, or `"raw"`.
- `SlashFrac` LNode — disambiguates inline fractions in superscripts:
  `e^{(a/2) b}` not `e^{a/2 b}`.
- `unit_fraction` notation kind — renders `unit(x)` as `x/‖x‖`. Opt-in.
- `Sym.is_compound` and `Sym.has_superscript` properties for structural
  rendering decisions via inner expression tree.

### Fixed

- LaTeX scientific notation rendered via LNode pipeline: `1.2e-06` becomes
  `1.2 \times 10^{-6}` using proper `Sup(10, exp)` nodes.
- `\frac` no longer wrapped in `\left(...\right)` in products.
- `\frac` before superscript postfix correctly brace-wraps: `{\frac{1}{2}}^2`.
- Postfix on compound-named Syms wraps correctly: `(a ∧ b)⋆` not `a ∧ b⋆`.
- LaTeX double-superscript on named Syms with `^` in name.
- `.gitignore` catches all vim swap files.

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
