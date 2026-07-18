# Correctness Strategy

## Why several oracles are necessary

A general-Gram product is easy to implement in a way that passes vector-square
tests but fails for higher exterior blades. A test suite that constructs its
expected values with the same recurrence as production can repeat the same
mistake. `galaga.core` therefore uses several independent checks whose assumptions
overlap as little as practical.

## The proof ladder

Tests progress from representation facts to model-specific examples.

1. **Construction and immutability** verify metric normalization, constructor
   exclusivity, coefficient shape, and read-only arrays.
2. **Generator relations** verify every basis-vector pair against the supplied
   Gram entry:

   $$
   e_i e_j+e_j e_i=2G_{ij}.
   $$
3. **Algebra laws** check associativity, bilinearity, exterior alternation,
   distributivity, involution identities, and grade decomposition on dense
   values.
4. **Backend agreement** compares diagonal, packed, lazy, and dense-reference
   implementations.
5. **Metric-derived identities** check compound matrices, complementary
   minors, complements, duals, antidot, regressive products, interiors, and
   transwedge decompositions.
6. **Numeric-function identities** check closed forms, convergent general
   series, inverse operations, real branch failures, and backend agreement.
7. **Recognizable models** exercise Euclidean algebras, STA, PGA, orthogonal
   CGA, and native-null CGA.

## Independent product oracles

### Dense Chevalley action

The `reference` backend constructs dense vector actions and higher left-action
matrices. It is intentionally unsuitable for large dimensions. Its value is
that it follows a direct matrix construction distinct from the sparse packed
layout and lazy cache.

### Diagonal closed form

For an exactly diagonal metric, two exterior basis blades have a monomial
product: XOR determines the output mask and repeated vectors contribute their
basis squares. This gives an independent closed form against which general
backend behavior can be checked.

### Exhaustive conformal basis change

Native-null CGA is compared with orthogonal `Cl(4,1)` through the documented
outermorphism. All 32 native exterior blades are mapped, and all 1,024
basis-blade product pairs are compared after the map. This checks contractions,
orientation, and higher-blade recurrence signs at once.

The derivation is documented in
[From an orthogonal CGA basis to a native null basis](cga-null-basis-change.md).

## Numeric-function oracles

Analytic functions need different checks from bilinear products:

- scalar and scalar-square exponentials are compared with `exp`, `cos`,
  `sin`, `cosh`, and `sinh` closed forms;
- an exponential of commuting disjoint-plane generators is compared with the
  product of their individual exponentials;
- general exponentials in one Gram basis are compared across packed, lazy,
  and reference product backends;
- Study square roots are squared back to their inputs;
- elliptic, hyperbolic, and null generators satisfy `log(exp(B)) == B` on the
  documented principal branches;
- outer-series identities are compared across different Gram matrices using
  identical exterior coefficients.

Failure cases are part of correctness. Negative real scalar roots, non-Study
square roots, non-rotors, non-Study rotor logarithms, the plane-ambiguous
logarithm of scalar `-1`, and noninvertible outer cosine values must fail
explicitly.

Tiny nonzero generators receive regression coverage so scalar classification
tolerances do not erase meaningful coefficients.

## Exactness and tolerances

Exact decisions are used where they determine algebra semantics:

- backend selection treats a Gram matrix as diagonal only under exact array
  equality after symmetry canonicalization;
- product construction removes only exact zero coefficients;
- bitmask grades, wedge signs, and complement signs are integral and exact.

Numerical tolerances are used where floating-point algorithms require them:

- constructor symmetry validation;
- inertia classification relative to metric scale;
- inverse residual verification;
- Study-number classification and result verification;
- rotor normalization and logarithm branch classification;
- tests involving determinants, linear solves, transcendental functions, or
  random dense products.

Tests use fixed random seeds. A random-looking regression must be reproducible
and must report enough context to identify the algebra and operation.

## Degenerate and nonorthogonal coverage

Every foundational family should include all of the following where its
mathematics permits:

- a normalized diagonal metric;
- a scaled diagonal metric;
- a degenerate metric;
- a dense oblique metric;
- the native CGA null-pair Gram matrix.

Operations that require nondegeneracy must test both their valid result and
their explicit failure on a singular metric.

Numeric functions must additionally distinguish generator squares of all
three signs. The zero-square case must include a null PGA translator, not only
the zero multivector.

## Verification commands

The normal local verification pass is:

```sh
.venv/bin/python -m pytest -q
.venv/bin/python -m compileall -q src tests
uvx ruff check src tests
uvx rumdl check README.md docs
git diff --check
```

The reproducible statement-and-branch coverage pass is:

```sh
uv run pytest packages/galaga/tests/core --cov=galaga.core --cov-report=term-missing -q
```

Coverage configuration lives in `pyproject.toml`. `pytest-cov` is a development
dependency, while generated data, XML, and HTML reports are ignored. The
project currently reports coverage but does not impose a `fail_under`
threshold; adopting one should be based on risk and meaningful branch tests,
not preserving a headline percentage with low-value assertions.

The product benchmark smoke test should record constructor backend, packed-byte
estimate, construction time, representative multiplication time, and cache
state. Benchmark numbers are diagnostic observations, not contractual limits,
unless a dedicated performance specification is added.

## Adding a new operation

A new finite algebraic operation should normally include:

1. a definition for homogeneous grades;
2. explicit scalar and mixed-grade behavior;
3. diagonal, oblique, and degenerate examples where applicable;
4. an identity against existing primitive operations;
5. a failure test for invalid algebras or arguments;
6. documentation in the relevant specification;
7. an ADR when it chooses among competing mathematical conventions.

A new analytic numeric function should additionally include:

1. its real domain and branch convention;
2. closed-form or independent-series oracle cases;
3. small-input and nonconvergence/unsupported-domain behavior;
4. backend agreement when it uses geometric products or left actions;
5. round-trip identities when an inverse function exists.
