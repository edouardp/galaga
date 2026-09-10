# Changelog

## 2.0.0a4 (2026-09-10)

This fourth Galaga 2 alpha adds notebook-ready bilinear and wedge product
tables, concise presets for complete configurations, blade names and notation,
and executable lessons on metrics, exterior products and inner-product
conventions.

### Added

- **Labelled Gram tables** — `Algebra.bilinear_form_table()` returns an
  immutable, rich-display snapshot of the native Gram matrix with basis labels
  on both axes. It supports LaTeX, Unicode, ASCII and Marimo interpolation
  without requiring the matrix companion. Exact zeros render in grey
  (`#bbbbbb`); small nonzero metric entries are not hidden by display tolerance.

- **Wedge product tables** — `Algebra.wedge_product_table()` displays basis
  vector exterior products. `full=True` includes every exterior basis blade,
  starting with scalar `1` and ordered by grade. Either `color=True` or
  `colour=True` enables LaTeX colouring by result grade; zeros remain grey.
  Tables preserve signed blade labels and capture the active presentation.
  Full tables contain `4**n` result cells, so vector-only tables remain the
  default.

- **Concise complete presets** — Adds `from galaga import presets` with
  `euclidean`, `sta`, `pga`, `cga`, `rga`, `lengyel_cga`, `complex`,
  `quaternion` and `exterior` factories. For example,
  `Algebra(config=presets.euclidean(3))` selects a complete immutable
  configuration.

- **Independent blade-name recipes** — Adds `presets.blades` for use with
  `Algebra(..., blades=...)` and `.with_blades()`, including
  `Algebra(1, 3, blades=presets.blades.sta())`. Immutable recipes resolve
  against the target algebra without changing its metric, model or notation.
  Metric-aware STA names derive their signs from the actual ordered metric;
  CGA frame recipes validate compatibility with the target Gram matrix.

- **Named notation presets** — Adds `presets.notation.default()`,
  `functional()`, `functional_short()`, `doran_lasenby()`, `hestenes()`,
  `lengyel()` and `lengyel_rga()`. These delegate to the existing immutable
  notation configurations and can be passed directly to
  `Algebra(..., notation=presets.notation.functional())`; numerical operations
  are unchanged.

- **Executable teaching notebooks** — Adds three maintained Marimo lessons:
  [preset namespaces](examples/galaga_v2/preset_namespaces.py),
  [bilinear and wedge tables](examples/galaga_v2/bilinear_and_wedge_tables.py),
  and [inner products](examples/galaga_v2/inner_products.py). They teach
  configuration versus vocabulary, coordinate bilinear forms, metric-independent
  exterior products, null versus degenerate metrics, and the intent and grade
  rules of scalar products, metric pairings, contractions and Hestenes and
  Doran–Lasenby products. Interactive examples include mixed grades, Gram
  determinants and related RGA operations, with references explaining differing
  author conventions.

### Changed

- **Clean preset discovery** — `galaga.presets` is now a package whose
  advertised namespace and wildcard exports contain only the concise factories,
  `blades` and `notation`. Implementation helpers no longer clutter notebook
  autocomplete. Existing `p_*` factories and concrete preset classes remain
  available through explicit compatibility imports; root-level `p_*` imports
  are unchanged and no deprecation warnings are introduced.

- **Expanded presentation documentation and examples** — Documents table
  rendering and composable presets in the package guide, presentation guide
  and ADRs. The existing CGA-via-Gram notebook now demonstrates labelled
  bilinear and wedge tables, including a small full table and graded
  commutation. Gram-matrix lessons link to the new teaching notebooks and
  distinguish the reversion-based metric pairing from the scalar part of a
  geometric product.

- **Regression and notebook coverage** — Adds algebra-derived table checks,
  preset compatibility and metric-validation tests, and headless tests of the
  new lessons and their interactive choices. Matrix dtype-conversion tests now
  explicitly expect NumPy's complex-to-real warning and verify both the real
  result and preservation of the original complex matrix; runtime conversion
  behaviour is unchanged.

## 2.0.0a3 (2026-09-10)

This third Galaga 2 alpha removes the retired Galaga 1 runtime, extends compact
matrix representations to general nondegenerate Gram metrics, and separates
mathematical logarithms from checked rotor generators. It also fixes exact
numeric key semantics, division provenance, and high-dimensional rotor
validation, with expanded executable teaching examples.

Code still importing `galaga.legacy` or other retired implementation modules
must migrate to the public Galaga 2 API. See the
[migration guide](docs/v2/migration-guide.md) for replacements.

### Added

- **Compact matrices for general Gram metrics** — Explicit
  `to_matrix(value, mode="compact")` now supports numerically suitable
  nondegenerate scaled and nonorthogonal real symmetric Gram matrices,
  including native-null CGA. Metric congruence and an exterior-power lift
  preserve native blade coefficients and geometric products; inverse
  conversion recovers coefficients when the selected representation is
  injective. Automatic dispatch remains left-regular for these metrics.

- **Explicit rotor-generator APIs** — Adds `rotor_generator(R)` to obtain a
  checked geometric exponent from a rotor's principal logarithm, and
  `is_rotor_generator(B)` to validate an independent candidate. The predicate
  checks evenness, reverse skewness, and vector-valued commutators. Returned
  generators retain their full scale, including any half-angle.

- **Opt-in LaTeX name conversion** — Adds `Name.from_latex(...)` and exposes
  `LatexSymbols` through `galaga.names`. Supported symbols derive ASCII and
  Unicode spellings; explicit overrides are preserved, and unsupported LaTeX
  requires an explicit ASCII fallback. Ordinary name construction remains
  literal rather than guessing spellings.

- **Metric-derived STA names** — Adds `sigmas=True` and
  `pseudovectors=True` options to `p_sta()` and its blade convention. Sigma
  and pseudoscalar-product labels derive their signs from the ordered native
  signature for both mostly-minus and mostly-plus conventions, while original
  gamma blade spellings remain available.

- **Unary multivector conveniences** — Adds `.bar`, `.dag`, `.inv`, and
  `.sq` properties as provenance-preserving forms of grade involution,
  reverse, inverse, and geometric square. `.dag` means reverse, not an
  additional Hermitian adjoint.

- **Configurable unit-fraction rendering** — Adds the opt-in
  `RenderRule("unit_fraction")` for displaying normalization as a value
  divided by its norm. This changes presentation only; non-default operation
  controls remain visible through functional notation.

- **General-Gram, CGA, and logarithm notebooks** — Adds pedagogical compact
  matrix foundations and workflow notebooks, CGA constructed from its Gram
  matrix, a CGA complex/quaternion comparison, and a dedicated logarithms and
  rotor-generators lesson. Examples include rendered Gram matrices, `4x4`
  compact complex and `32x32` real left-regular CGA matrices, mixed-grade
  quaternion-pair encodings, branch cuts, nilpotent logarithms, and interactive
  comparisons of paths to the same rotor. Quaternion CGA examples use explicit
  notebook-local coordinate maps; general native CGA quaternion conversion is
  not introduced by this release.

### Changed

- **`log` is the real principal algebra logarithm** — Removes the normalized
  rotor and scalar-square nonscalar-part restrictions. Positive scalar,
  nonrotor, compound, and nilpotent inputs are supported where the principal
  branch can be resolved. Closed forms handle scalar-square cases, with
  native left-action quadrature for general inputs. Scalar magnitude and all
  stored grades are retained, and nonscalar results must pass an exponential
  round-trip check. Singular inputs, the nonpositive-real spectral branch
  cut, and unresolved numerical cases raise explicitly; no complexification
  or alternative-branch search is performed. Use `rotor_generator` when the
  result must generate a path of rotors.

- **Contraction symbols** — Default LaTeX rendering now uses
  `\mathbin{\rfloor}` for left contraction and `\mathbin{\lfloor}` for right
  contraction. ASCII and Unicode spellings and numerical operations are
  unchanged.

- **Shared matrix representation plans** — Forward, inverse, and spinor
  conversions reuse bounded, immutable cached plans for algebra-derived
  generators, blade matrices, and reconstruction systems. Presentation-only
  algebra views share plans, while returned matrices remain independent.
  `MatrixRepr.domain` records whether the source coefficient domain is full
  or even.

- **Teaching and migration coverage** — Migrates the remaining scratch and
  teaching files to the public facade, including quantum physics, dynamic
  notation, LaTeX layouts, Marimo helpers, Mermaid examples, and the batched
  benchmark. The maintained gallery now contains 85 notebooks with dependency
  validation and headless execution checks. Guides distinguish exterior
  blades from geometric words, exact values from display rounding, and
  algebraic logarithms from geometric generators.

- **Legacy-free validation and packaging** — Historical compatibility tests
  and benchmarks now use frozen observations, public contracts, and independent
  algebraic reference checks instead of executing the old engine. Wheel and
  sdist validation rejects retired runtime files, source mismatches, and
  metadata drift before publication. Fresh installed-wheel tests verify
  package origins and exercise companion integrations outside runtime source
  paths.

### Fixed

- **Exact equality and compatible hashes** — Equal immutable multivectors
  now hash alike across positive and negative zero, and exactly scalar values
  hash like equal Python real numbers. Scalar comparisons no longer round
  large integers, exact fractions, or NumPy scalar operands through `float64`;
  nonfinite comparisons return false without raising. Every stored nonzero
  coefficient remains significant. No tolerance-based equality is introduced,
  and multivector-to-multivector equality retains its algebra-identity scope.

- **Division preserves values and both operand histories** — Multivector
  denominators retain their names and expressions for rendering and replay,
  including CGA weight denominators. Scalar dispatch now requires exactly zero
  nonscalar coefficients, preventing tiny grades from being discarded. Direct
  scalar division avoids an overflowing reciprocal when the quotient is
  finite, and exact scalar zero denominators consistently raise
  `ZeroDivisionError`. General division remains right multiplication by the
  denominator's inverse.

- **High-dimensional rotor validation** — `is_rotor` now requires the
  reverse sandwich to preserve every native basis vector, in addition to
  evenness and the full unit reverse product. Unit even multivectors that mix
  vectors into higher grades are no longer accepted as rotors. Tests cover
  nonorthogonal and degenerate metrics, compound rotors, and explicit
  floating-point tolerances.

- **Matrix inverse and convention boundaries** — Normalizes reconstruction
  columns before rank checks so uniform metric scaling does not create false
  rank deficiency. Genuine information loss and matrices outside the image
  still fail inverse conversion. Named Dirac/Weyl/Majorana basis changes no
  longer accept unrelated `4x4` matrices or infer a textbook convention from
  general-Gram inertia alone; spinor and named-mode restrictions remain
  explicit.

- **Unicode symbol conversion** — Corrects lowercase mathematical-font
  mappings, Unicode block exceptions, and supported digit mappings. Unsupported
  non-ASCII bodies, nested commands, and invalid font/digit combinations are
  rejected instead of producing unrelated or unassigned characters.

- **LaTeX grouping and accents** — Protects already-scripted and compound
  names when adding superscripts or subscripts, separates control-word
  prefixes from following identifiers, and renders custom under-accents with
  a KaTeX-compatible fallback. Hestenes reversal consistently uses its dagger
  rule in LaTeX as well as plain-text targets. Notebook regressions also guard
  computed scalar equations against nested math delimiters.

- **Production type checking** — Resolves the remaining production type
  errors while preserving accepted numeric inputs and model keyword
  contracts. No type-check exclusions, ignores, or relaxed rules were added.

### Removed

- **Galaga 1 runtime and legacy import paths** — Deletes `galaga.legacy`,
  the table-backed engine, old operation registries, lazy/symbolic adapters,
  and the legacy rendering and simplification pipeline. Retired paths such
  as `galaga.algebra`, `galaga.ops`, `galaga.symbolic_core`, and
  `galaga.notation` are no longer importable. Use `galaga` or numeric-only
  `galaga.core`, with `galaga.expression`, `galaga.presentation`, and
  `galaga.rendering` for their respective public contracts.

- **Old symbol-converter path and matrix fallbacks** — Removes the
  `galaga.latex_symbols` shim; use `galaga.names.LatexSymbols` or
  `Name.from_latex(...)`. Matrix conversion no longer probes legacy private
  product tables or legacy multivector factories.

The warning-only `galaga.gram_bridge` paths and six temporary function
spellings remain available during the prerelease migration; their retirement
is still scheduled before stable `2.0.0`. Degenerate metrics continue to
require left-regular matrices, and a rejected principal logarithm or generator
does not prove that no alternative real logarithm or geometric generator
exists.

## 2.0.0a2 (2026-09-06)

This second Galaga 2 alpha expands the conformal and projective workflows,
introduces interactive CGA visualization, and makes the maintained examples
portable outside a source checkout. It also incorporates API, rendering, and
release-process feedback from the first alpha.

### Added

- **Interactive CGA visualization package** — Introduces
  `galaga-anywidget`, a Python 3.11+ AnyWidget integration for synchronized 2D
  conformal points, dipoles, lines, and circles. Browser drags update semantic
  point coordinates while derived multivectors remain ordinary Python and
  Marimo computations.

- **Coordinate-first conformal points** — `ConformalModel.up()` and
  `round_point()` now accept positional Cartesian coordinates or one coordinate
  iterable in addition to Euclidean multivectors. Validation rejects ambiguous,
  mixed, and dimensionally invalid forms.

- **Explicit CGA representation workflows** — Adds tested direct and dual
  construction examples, full-conformal-metric duality checks, and guidance for
  distinguishing points from dual zero-radius spheres without storing a
  representation mode on the model.

- **Dual PGA and space-antispace workflows** — Adds executable RGA notebooks
  and algebra-derived regression tests for dual projective reflections,
  complementary models, and space-antispace correspondence.

- **Executable CGA constructions** — Adds maintained notebooks for circles
  through three points, circle-circle meets, coordinate-first construction, and
  interactive derived geometry. Notebook tests execute these examples as
  integration contracts.

### Changed

- **Portable example notebooks** — Maintained Marimo notebooks now contain
  ordinary package imports without repository discovery or `sys.path`
  mutation. `make run-marimo` supplies editable local packages, while the same
  files run unchanged against installed distributions.

- **CGA and matrix documentation** — Expands the conformal API guide,
  representation conventions, native-null blade presentation rules, and the
  plan for matrix representations over general Gram metrics. Corrects the
  native-null translator example and marks superseded implementation plans as
  historical.

- **Release topology** — Adds `galaga-anywidget` to the uv workspace and the
  coordinated versioning, test, build, artifact-check, and publication
  workflow. Release-topology tests keep companion versions and Galaga
  dependency floors synchronized.

- **Release and migration guidance** — Refreshes the package guides,
  documentation index, Galaga 1-to-2 migration guide, release checklist, and
  architectural decision records for the current public facade.

### Fixed

- **Stable reactive identity semantics** — Reactive multivectors now use
  identity equality and hashing, so mutation cannot invalidate dictionary or
  set membership and value-equal snapshots cannot violate Python's equality
  and hash contract. Exact and tolerance-based numeric comparisons remain
  explicit snapshot operations.

- **Notebook template-string preservation** — The migration tooling no longer
  rewrites template strings as ordinary strings, preserving dynamic Marimo
  Markdown interpolation.

- **Native-null presentation consistency** — Aligns displayed native-null
  blade dimensions and juxtaposed basis notation with the underlying conformal
  metric and configured presentation policy.

- **Lint-tool compatibility** — Keeps Ruff formatting scoped to Python while
  Rumdl remains responsible for Markdown, preserving a stable full-repository
  lint gate after the dependency update.

## 2.0.0a1 (2026-07-25)

This is the first alpha of Galaga 2. It makes the Gram-matrix numeric
implementation the foundation of the public API and moves the former Galaga 1
implementation to the temporary `galaga.legacy` namespace.

### Added

- **Native Gram-matrix numeric core** — Adds `galaga.core`, an immutable dense
  multivector implementation whose algebra is defined by a general symmetric
  Gram matrix. Diagonal signatures remain convenient, while native nonorthogonal
  and null bases no longer require a hidden change of basis.

- **Canonical Galaga 2 facade** — Promotes the core-backed `Algebra`,
  `Multivector`, presets, products, involutions, dualities, norms, and numeric
  functions to the top-level `galaga` namespace. The facade preserves optional
  expression provenance without coupling the numeric core to symbolic concerns.

- **Explicit operation vocabulary** — Makes descriptive names such as
  `geometric_product`, `outer_product`, `grade_involution`,
  `doran_lasenby_inner_product`, and `metric_inner_product` canonical. Familiar
  short functional forms remain available as aliases, including configurable
  notation aliases for presentation-oriented code.

- **Presentation configuration** — Adds immutable `DisplayPolicy`,
  `Notation`, `BladeConvention`, and preset configuration. Algebra, blade
  naming, operation notation, and display content can be configured
  independently, overridden per algebra, and changed temporarily with
  context-local presentation scopes that are safe across threads and async
  tasks.

- **Semantic expression and rendering pipeline** — Adds optional symbolic
  expression nodes over concrete multivectors, evaluation and simplification,
  exact configured rendering contracts, full `name = expression = value`
  display, selective display parts, numeric precision and small-value elision,
  and KaTeX-compatible LaTeX emission.

- **Blade construction helpers** — Adds expression-aware `Algebra.blade()` and
  variadic `Algebra.blades()` construction from blade names, indices, or
  existing blade multivectors. This supports explicit notebook bindings without
  dynamic-local mutations that interfere with Marimo dependency tracking.

- **Native-null conformal model** — Adds `galaga.cga.ConformalModel` over the
  native `e_o`/`e_\infty` Gram basis, with validated point embedding,
  homogenization, coordinate and radius recovery, duals, attitudes, carriers,
  cocarriers, centers, containers, partners, component families, projections,
  reflections, inversions, and model-level expression-form controls.

- **Rigid Geometric Algebra model** — Adds a validated Lengyel-style
  `RigidModel` with projective measurements, geometry constraints, projections,
  support operations, complements, bulk/weight decomposition, antiproducts,
  transwedge products, and convention-specific semantic rendering.

- **Executable Galaga 2 examples** — Migrates the maintained Marimo notebooks
  to the public facade and adds focused v2, RGA, native-null CGA, STA,
  `galaga_matrix`, and `galaga_mermaid` examples. The maintained notebook set is
  now exercised as an integration contract.

- **Audited migration infrastructure** — Adds executable API manifests,
  numeric contracts, rendering parity cases, architectural tests, LibCST
  codemods, migration ledgers, clean-wheel checks, coverage gates, and
  performance benchmarks used to validate the cutover.

### Changed

- **Top-level API now uses the Galaga 2 implementation** — `galaga.Algebra`
  and related public values and functions are now the core-backed facade.
  Code that intentionally needs the previous implementation during the alpha
  migration window must import it from `galaga.legacy`.

- **Long operation names are primary** — Documentation, expression catalogs,
  integrations, and examples now use the explicit long names. Short names are
  conveniences rather than a separate competing API.

- **Bracket-family scaling is explicit** — `commutator`,
  `anticommutator`, `lie_bracket`, and `jordan_product` are unscaled.
  `half_commutator` and `half_anticommutator` provide the explicitly scaled
  operations.

- **Numeric scalar conversion is strict** — `float(multivector)` and NumPy
  scalar conversion succeed only for scalar-only multivectors; they no longer
  silently discard nonscalar grades. Use `grade(value, 0)` or the optional
  `scalar_part(value)` helper when projection is intended.

- **Scalar-valued numeric functions preserve the domain** — Operations such as
  `norm()` return scalar Galaga multivectors, retaining algebra ownership,
  naming, expression provenance, and display behavior. Explicit conversion to
  a Python or NumPy scalar remains available for scalar-only results.

- **Products support variadic functional notation** — Associative operations
  can accept multiple operands while expression provenance records their
  semantic operation and evaluation order.

- **Rendering follows semantic structure** — Full display separates equal
  parts with readable spacing, omits a duplicated value only when its rendered
  expression is identical, preserves explicitly requested parts, simplifies
  signs and unit coefficients, and avoids unnecessary grouping where operator
  precedence is sufficient.

- **Companion packages use public protocols** — `galaga_marimo`,
  `galaga_matrix`, and `galaga_mermaid` now consume Galaga 2 public protocols
  instead of legacy internals. Matrix representations use public linear
  actions, and `galaga_matrix` owns its matrix-specific symbolic provenance.

- **Supported Python baseline is 3.11** — Galaga, `galaga_matrix`, and
  `galaga_mermaid` target Python 3.11 and later. `galaga_marimo` retains its
  newer Python requirement for t-string notebook support.

### Fixed

- **Expression provenance through numeric functions** — Compound operations
  such as `exp`, `log`, norms, sandwiches, and conformal-model helpers retain
  named operands instead of prematurely replacing them with evaluated
  coefficients.

- **Stable full rendering** — Restores the six-decimal default, suppresses
  insignificant floating-point residue, renders subtraction without `+ -`,
  drops unit blade coefficients, and retains expression/value output for
  unnamed compound expressions.

- **LaTeX compatibility and grouping** — Corrects complement, dual,
  antireverse, fraction, exponential, unary-negation, antiproduct, and
  native-null CGA rendering for KaTeX and Marimo.

- **CGA convention consistency** — Native conformal blade conventions now
  follow the actual Gram metric, with scale-aware coordinate, weight, center,
  and signed-radius calculations.

- **General-metric fast-path validation** — Numeric fast paths are checked
  against their algebra and metric assumptions so diagonal optimizations
  cannot silently produce incorrect results for general Gram matrices.

### Deprecated

- **`galaga.legacy` is transitional** — The Galaga 1 implementation remains
  available as an explicit migration and rendering-parity oracle during the
  alpha period. It is not the Galaga 2 compatibility surface and is scheduled
  for removal before the final 2.0 release.

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
