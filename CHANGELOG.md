# Changelog

## 1.8.1 (2026-07-15)

### Changed

- **RGA demo cell scoping** — Uses private cell-local bindings for temporary
  bivectors so instructional symbols can be reused safely across Marimo cells.

### Fixed

- **Consistent Lengyel complement accents** — Right and left complements now
  include fixed-height LaTeX struts that account for superscripts and
  subscripts. Overlines and underlines therefore remain aligned across an
  equation even when operand glyphs have different ascenders or descenders.

## 1.8.0 (2026-07-14)

### Added

- **Terathon/Lengyel RGA convention layer** — Adds the Rigid Geometric
  Algebra basis convention `b_rga()` and the rendering preset
  `Notation.lengyel()`. The basis preserves Lengyel's ordering, orientation,
  and signed names such as `e31`, `e41`, and the antiscalar `𝟙`.

- **Exterior metric and antimetric operations** — Adds
  `extended_metric_matrix()`, `metric_antiexomorphism_matrix()`,
  `metric_apply()`, `antimetric_apply()`, `metric_inner_product()`, and the
  antiscalar-valued `antidot_product()`. The cached public metric matrices are
  read-only, and the operations remain meaningful for degenerate PGA metrics.

- **RGA complements, projections, duals, and products** — Adds explicit
  `left_complement()` and `right_complement()` names; bulk and weight parts;
  left and right bulk and weight duals; `antiwedge()`;
  `geometric_antiproduct()`; `antireverse()`; and the RGA left and right
  interior products.

- **Experimental transwedge products** — Adds `transwedge(a, b, k)` and
  `transwedge_antiproduct(a, b, k)`, including grade propagation, symbolic
  expression nodes, evaluation, simplification, and parameterized rendering.

- **Convention-aware local variable hints** — `BladeConvention` now accepts
  `variable_hints` independently of display overrides. `Algebra.locals()`
  gains `prefix=` for generated blade names and `pss=` as a convenient
  pseudoscalar-name override. Standard PGA, RGA, STA, CGA, complex, and
  quaternion conventions provide their idiomatic hints.

- **RGA documentation and executable Marimo demo** — Adds a convention guide,
  design ADR, reviewed implementation plan, expanded Terathon foundations
  review, and `examples/rga/rga_demo.py`. The demo introduces the RGA basis and
  exercises complements, metric operations, duals, interior products,
  antiwedge, geometric products and antiproducts, and transwedge products.

- **Matrix representation product fuzz coverage** — Adds randomized checks
  that left-regular and compact matrix representations preserve geometric
  products and round-trip across Euclidean, spacetime, and projective
  algebras.

### Changed

- **`Algebra.locals()` naming is separated from display naming** — Display
  overrides such as STA sigma names no longer become Python dictionary keys.
  Non-hinted blades consistently use the convention's ASCII prefix, or the
  call-site `prefix=` override, plus compact subscripts. Code relying on the
  previous generated keys may need updating.

- **Gamma locals now use `g`** — The default ASCII local prefix for `γ` is now
  `g` instead of `y`, matching common STA source-code conventions.

- **Lengyel rendering is KaTeX-compatible** — RGA glyphs are emitted with
  supported LaTeX constructs, including `\text{𝟙}` for the antiscalar and
  `\utilde{...}` for antireverse. RGA operations render with Lengyel's product,
  complement, dual, interior-product, and bulk/weight notation while existing
  Galaga operations with different semantics retain explicit names.

### Fixed

- **Compact letter-subscript local names** — Named axes such as `ex` and `ey`
  now combine as `exy`, rather than `exey`.

- **Blade-convention dimension errors** — A convention that references a
  vector outside the algebra dimension now raises a descriptive `ValueError`
  instead of an opaque `IndexError`.

## 1.7.6 (2026-07-11)

### Added

- **`BladeConvention(subscripts=)` parameter** — New clean API for named-subscript
  basis vectors. Bare label strings are combined structurally with the prefix:
  `subscripts=["x","y","z"]` with `prefix="e"` produces `e_{x}`, `e_{xy}`, etc.
  No regex parsing, no pre-formatted LaTeX needed.

- **`b_default(subscripts='xyz')`** — String shorthand accepted: each character
  becomes a subscript label. Makes the common case trivial:
  `Algebra(3, blades=b_default(subscripts='xyz', pss='i'))`.

### Fixed

- **Compact style LaTeX for single-char subscripts** — `vector_names` with
  pre-formatted LaTeX like `e_x` now correctly produce `e_{xy}` for bivectors
  (was producing `e_{e_xe_y}`).

- **`Algebra.locals()` keys are Python-safe** — Keys generated from blade names
  with non-identifier characters are now sanitized.

## 1.7.5 (2026-07-10)

### Added

- **Shared symbolic naming core** — Adds a reusable `galaga.symbolic_core`
  layer for name normalization, symbolic leaves, structural expression nodes,
  domain dispatch, and generic rendering. This lets future pedagogical value
  types share Galaga's naming and expression-tree behavior without duplicating
  the `Multivector` implementation.

- **Symbolic MatrixRepr expressions** — `MatrixRepr` values can now be named
  with `.name()` and participate in symbolic expression trees while preserving
  concrete matrix values. Matrix operations such as `@`, `+`, `-`, scalar
  arithmetic, adjoints, and basis changes retain displayable provenance.

- **Matrix representation expression nodes** — `to_matrix(named_mv)` and
  `to_spinor_column(named_mv)` now produce symbolic representation-map
  expressions such as `\rho(B)` and spinor-column expressions, rather than
  render-only labels.

- **SPEC-013 and ADR-010** — Documents the accepted design for decoupled
  symbolic naming and records the decision to replace `MatrixRepr.label` with
  `.name()`.

### Changed

- **`MatrixRepr.label` replaced by `.name()`** — `label=` is no longer accepted
  as the public MatrixRepr naming API. Matrix naming now matches multivector
  naming and creates a symbolic leaf rather than display-only metadata.

- **Representation notation clarified** — Default compact/Dirac-family
  representation maps render as plain `\rho(...)`; explicit Weyl and Majorana
  basis views render as `\rho^{\mathrm{Weyl}}(...)` and
  `\rho^{\mathrm{Majorana}}(...)`; quaternion mode renders as
  `\rho_{\mathbb{H}}(...)`.

- **Matrix examples updated** — Matrix, spinor-column, Dirac bilinear, and
  Weyl/chiral notebooks now demonstrate `.name()`-based matrix displays and
  symbolic matrix expression trees.

### Fixed

- **`galaga_matrix` package metadata** — Adds the package README, author,
  classifiers, keywords, and project URLs so `twine check` passes without
  missing long-description warnings.

- **Release lint hygiene** — Removes unused imports from Chisolm reference tests
  and formats the new symbolic-core and MatrixRepr test files so the configured
  lint target passes cleanly.

## 1.7.4 (2026-07-08)

### Changed

- **Quaternion mode unified storage** — `to_matrix(mv, mode="quaternion")` now
  stores the matrix as a numpy complex array internally (quaternion-block
  embedding). All arithmetic operations (`@`, `+`, `.inv()`, `.trace()`, etc.)
  now work on quaternion matrices. The `.quat` property extracts the
  quaternion grid on demand for display. `from_matrix` roundtrips quaternion
  mode. Backward compatible: constructing from `list[list[Quat]]` still works.

### Added

- **`.quat` property on MatrixRepr** — Returns the `list[list[Quat]]` view of
  the underlying complex matrix. Only available when `mode="quaternion"`.

- **Docs: Spinors — Pauli vs Dirac explainer** — Covers how spinor columns
  relate to the "square root of a vector" picture, the rank-1 vs rank-2
  idempotent difference, and the Weyl decomposition.

- **ADR-070: Pedagogical and convention-explicit scope** — Documents that
  galaga prioritises correctness, clarity, and exposing multiple conventions
  over raw performance.

- **Review: Terathon GA foundations posts** — Literature review of Eric
  Lengyel's posts on GA foundations.

## 1.7.3 (2026-07-04)

### Added

- **`MatrixRepr.to_basis()`** — Transform between Dirac, Weyl (chiral), and
  Majorana matrix bases via unitary similarity. Basis-aware: `from_matrix`
  automatically transforms back before recovering the MV. Chain-safe:
  `M.to_basis("weyl").to_basis("majorana").to_basis("dirac") == M`.

- **Spinor columns as MatrixRepr with ket/bra semantics** —
  `to_spinor_column` now returns `MatrixRepr` with `kind="ket"`, carrying
  algebra, basis, and ket-notation labels (`|ρ(ψ)⟩`). Conjugate transpose
  (`.H`) converts ket↔bra. `bra @ ket` gives a scalar (inner product).
  `operator @ ket` gives a ket. Basis changes on kets use single-sided
  transforms (S·ψ, not S·M·S†).

- **`to_matrix` mode aliases** — `mode="pauli"` (validates Cl(3,0)/Cl(0,3)),
  `mode="dirac"` (validates Cl(1,3)/Cl(3,1)), `mode="quaternion"` (returns
  quaternion-entry MatrixRepr). Wrong algebra raises `TypeError`.

- **`MatrixRepr.kind` attribute** — tracks `"operator"`, `"ket"`, or `"bra"`
  for correct dispatch of basis transforms, product semantics, and labeling.

- **`MatrixRepr.basis` attribute** — tracks which named basis the matrix is in
  (`"dirac"`, `"weyl"`, `"majorana"`, `"pauli"`, or `None`).

### Changed

- **`to_matrix` defaults to compact** — Non-degenerate algebras now default to
  `mode="compact"` (was `"left-regular"`). PGA/degenerate still default to
  `"left-regular"`.

- **`from_matrix(MatrixRepr)` single-arg form** — No need to pass algebra when
  the `MatrixRepr` already carries one.

- **`from_spinor_column(MatrixRepr)` single-arg form** — Same convenience for
  spinor roundtrips.

### Removed

- **`to_quaternion_matrix`** — Removed from public API. Use
  `to_matrix(mv, mode="quaternion")` instead. Internal helper remains.

### Fixed

- **Release script** — `uv lock` after version bump (no more dirty lockfile).
  PyPI token fetched once at start (one password prompt, not six).

## 1.7.2 (2026-07-04)

### Changed

- **`to_matrix()` defaults to compact mode** — Non-degenerate algebras (r=0)
  now default to `"compact"` instead of `"left-regular"`. `to_matrix(e1)` in
  Cl(3,0) gives the 2×2 Pauli matrix directly. Degenerate algebras (PGA, etc.)
  still default to `"left-regular"`. Explicit `mode=` still works as before.

- **`from_matrix(MatrixRepr)` works without explicit algebra** — When a
  `MatrixRepr` carries an algebra reference (as it does from `to_matrix()`),
  you can call `from_matrix(M)` directly. Raw ndarrays still require
  `from_matrix(alg, array)`.

## 1.7.1 (2026-07-04)

### Added

- **`MatrixRepr` transparent numpy proxy** — All arithmetic operations (`@`, `+`,
  `-`, `*`, `/`, `**`) now return `MatrixRepr` instances, preserving algebra and
  mode metadata. Includes `.T`, `.H`, `.conj()`, `.trace()`, `.det()`, `.inv()`,
  and factory methods `MatrixRepr.identity(k)`, `.zeros(shape)`, `.kron(other)`.

- **`to_matrix()` returns `MatrixRepr`** — No longer returns a bare numpy array.
  The result carries algebra/mode metadata and supports chained operations.
  Existing code using `np.allclose(to_matrix(v), ...)` still works via `__array__`.

- **`from_matrix()` accepts `MatrixRepr` or ndarray** — Passing a `MatrixRepr`
  auto-inherits its mode; passing a raw array works as before.

- **Auto-labeling with ρ notation** — `to_matrix(named_mv)` labels the result
  as `\rho(name)`. `from_matrix(alg, labeled_matrix)` names the recovered MV
  as `\rho^{-1}(label)`. Unnamed inputs pass through without labeling.

- **`MatrixRepr(MatrixRepr)` copy construction** — Wrapping an existing
  `MatrixRepr` copies the underlying data (not a reference) and inherits
  label/algebra/mode, with optional overrides via keyword args.

- **`__array_ufunc__` interception** — numpy operations like `np.add(M, N)`,
  `np.conj(M)` return `MatrixRepr` instead of bare arrays.

## 1.7.0 (2026-07-03)

### Added

- **`galaga_matrix` package published to PyPI** — Matrix representations for
  Clifford algebras, now released alongside galaga and galaga-marimo.

- **Spinor column conversions** — `to_spinor_column()` / `from_spinor_column()`
  convert even-grade multivectors to/from complex spinor column vectors (Pauli
  spinors for Cl(3,0), Dirac spinors for Cl(1,3)). Full roundtrip guaranteed
  for complex and quaternionic algebras.

- **Quaternionic spinor conversions** — `to_spinor_quaternion()` /
  `from_spinor_quaternion()` for algebras classified as M(k,ℍ). Cl(1,3) Dirac
  spinors can be represented as 2-component quaternion columns.

- **`to_quaternion_matrix()` for Cl(1,3)** — Uses an explicit M(2,ℍ) basis
  with proper quaternion-block structure.

- **New example notebooks** — Spinor column conversions, Dirac/Weyl/Majorana
  bases, STA Dirac bilinears, matrix representations.

- **ADR-069: Quaternion bivector assignment** — Documents why `b_quaternion()`
  uses i=e₂₃, j=e₁₃, k=e₁₂ (rotation axis convention).

- **CGA convenience functions proposal** — Design doc for future conformal GA
  helpers.

### Fixed

- **`exp()` for non-simple bivectors** (#11) — Previously used the simple-bivector
  formula unconditionally, producing wrong results for compound bivectors in n≥4
  (e.g., `exp(0.3·e₁₂ + 0.5·e₃₄)` was missing the e₁₂₃₄ cross term and wasn't
  a valid rotor). Now checks whether B² is purely scalar; falls back to Taylor
  series for non-simple inputs.

- **`exp()` for mixed-grade inputs** — `exp(1 + e₁)` and similar mixed-grade
  elements now produce correct results in all dimensions. The n≤3 shortcut that
  skipped the B² check has been removed.

### Changed

- **Display order defaults to grade-sorted** — Multivector terms now render in
  grade order (scalar, vectors, bivectors, ...) instead of raw bitmask order.

- **`b_sta()` compound blade naming** — Uses the pseudoscalar name as prefix for
  compound blades (e.g., `iσ₁` instead of `Iσ₁`).

- **Makefile overhauled** — `make help` shows all targets; added `test-galaga-matrix`,
  `test-galaga-mermaid`, `update-deps` (with 7-day supply chain lag), `security`,
  `validate`, and interactive `make release`.

## 1.6.5 (2026-04-24)

### Fixed

- **Versioning in CHANGELOG** - now back in sync

## 1.6.4 (2026-04-24)

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
