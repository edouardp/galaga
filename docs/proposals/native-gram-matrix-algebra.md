# Proposal: Native Gram-Matrix Algebras

## Status

Implemented by `galaga.core` under ADR-073. This proposal remains as the
original problem statement and design analysis for native Gram matrices.

## Summary

Make a real symmetric Gram matrix the canonical metric representation owned by
`Algebra`. Keep the existing signature and `Cl(p, q, r)` constructors as
convenience APIs that construct diagonal Gram matrices.

This permits non-orthogonal bases to be represented directly. In particular,
3D conformal geometric algebra can use native null basis vectors `e4` and `e5`
with

$$
e_4^2 = e_5^2 = 0,
\qquad
e_4 \mathbin{\cdot} e_5 = -1,
$$

instead of storing an orthogonal $e_+,e_-$ pair and constructing the null
vectors as linear combinations.

The proposal does **not** make each basis vector a $5\times5$ matrix. A Gram
matrix describes the scalar products among all basis vectors. Multivectors
remain dense arrays of $2^n$ real coefficients, and exterior basis blades
remain bitmasks.

## Motivation

Galaga currently treats a signature tuple as both:

1. the algebra's metric; and
2. proof that the stored basis is orthogonal.

For an orthogonal basis, the geometric product of two exterior basis blades is
always either zero or a scalar multiple of one other basis blade. This enables
the current pair of multiplication tables:

```python
_mul_index[a, b]  # one result bitmask
_mul_sign[a, b]   # one scalar coefficient
```

That representation cannot describe a non-orthogonal basis. If $i \ne j$ and
$g_{ij}\ne0$, then

$$
e_i e_j = g_{ij} + e_i \wedge e_j,
$$

which contains two basis-blade components. More general blade products can
contain several components at different grades.

The limitation is visible in CGA. Galaga currently constructs
`Algebra(4, 1)` in an orthogonal basis:

$$
e_+^2=1,
\qquad
e_-^2=-1,
$$

then derives the null vectors:

```python
eo = (em - ep) / 2
einf = em + ep
```

This is mathematically correct, but `eo` and `einf` are not native exterior
basis vectors: each has two nonzero multivector coefficients. A native Gram
matrix would make them one-hot basis vectors while retaining the same Clifford
algebra.

Gram-matrix support also enables arbitrary oblique frames, reciprocal-frame
work, and direct transcription of literature that specifies a non-orthogonal
basis.

## Proposed semantics

### The Gram matrix is canonical

Every `Algebra` stores a private, immutable `float64` matrix `_gram` of shape
`(n, n)`. The public `gram` property returns a read-only view.

The matrix satisfies

$$
G_{ij}=e_i\mathbin{\cdot}e_j
      =\frac12(e_i e_j+e_j e_i).
$$

The `Cl(p, q, r)` constructor remains a convenience front end. Explicit
diagonal metrics move to the keyword-only `signature=` form, with `sig=` as a
short alias:

```python
Algebra(3)                    # gram = diag(1, 1, 1)
Algebra(1, 3)                 # gram = diag(1, -1, -1, -1)
Algebra(3, 0, 1)              # gram = diag(0, 1, 1, 1)
Algebra(signature=[1, 1, 1, 0])  # gram = diag(1, 1, 1, 0)
Algebra(sig=[1, 1, 1, 0])        # equivalent short form
```

The new explicit form is:

```python
Algebra(gram=G, blades=...)
```

The first implementation should require `gram=` as a keyword. This avoids
confusing a two-dimensional nested sequence with the existing explicit
signature form and makes non-orthogonal construction visible at the call site.

Positional arguments are reserved for `p, q, r`; a sequence in the first
position is rejected with guidance to use `signature=` or `sig=`. This removes
the polymorphic `p_or_signature` parameter from the constructor. Passing more
than one of `signature=`, `sig=`, `gram=`, or `p, q, r` is an error.

### Validation and immutability

`Algebra(gram=G)` must:

- require a square, non-empty, finite, real numeric matrix;
- require symmetry within a documented construction tolerance;
- copy the input so later caller mutation cannot affect the algebra;
- canonicalize accepted floating-point asymmetry with
  `(G + G.T) / 2`;
- store the resulting array as read-only; and
- permit singular matrices.

The construction tolerance is only for validating symmetry and determining
metric inertia. It must not silently round small Gram entries to zero. A small
nonzero $g_{ij}$ still changes the algebra.

### Basis vectors and basis blades do not change representation

The coefficient basis remains the exterior basis

$$
1, e_1, e_2, e_1\wedge e_2, e_3, \ldots,
e_1\wedge\cdots\wedge e_n.
$$

Bit $i$ still records whether vector $e_i$ is present. For example, in five
dimensions:

```text
e1      -> 0b00001
e4      -> 0b01000
e5      -> 0b10000
e4 ^ e5 -> 0b11000
```

Every multivector still stores a length-$2^n$ `float64` coefficient array.
Thus native CGA `e4` is still represented as:

```text
[0, 0, 0, 0, 0, 0, 0, 0, 1, 0, ..., 0]
```

The distinction is in multiplication: `e4 * e5` is allowed to produce both a
scalar coefficient and an `e45` coefficient.

For a non-orthogonal basis, a bitmask blade always means an **exterior** blade.
`0b11000` means $e_4\wedge e_5$, not the geometric word $e_4e_5$. These are
the same in an orthogonal basis but not in general.

## Native CGA example

The null-basis Gram matrix for 3D CGA is:

```python
G = np.array(
    [
        [1, 0, 0,  0,  0],
        [0, 1, 0,  0,  0],
        [0, 0, 1,  0,  0],
        [0, 0, 0,  0, -1],
        [0, 0, 0, -1,  0],
    ],
    dtype=float,
)

cga = Algebra(gram=G)
e1, e2, e3, e4, e5 = cga.basis_vectors()
```

The expected algebra is:

```python
e4 * e4 == 0
e5 * e5 == 0
e4 | e5 == -1
e4 * e5 == -1 + (e4 ^ e5)
e5 * e4 == -1 - (e4 ^ e5)
```

With a CGA blade convention, the final two vectors may instead render as
$e_o$ and $e_\infty$:

```python
cga = Algebra(
    gram=G,
    blades=b_cga(null_basis="origin_infinity"),
)
e1, e2, e3, eo, einf = cga.basis_vectors()
```

Under this proposal, those names describe the actual metric rather than being
display-only aliases for $e_+$ and $e_-$.

The native null basis is related to the existing orthogonal basis by

$$
e_o=\frac12(e_- - e_+),
\qquad
e_\infty=e_-+e_+.
$$

This change of basis provides an exact reference against which the new engine
can be tested.

## Geometric-product implementation

### Why XOR alone is insufficient

XOR remains the correct operation for the exterior product of basis blades.
It is not sufficient for the geometric product in a non-orthogonal basis.
Consequently, the current `_mul_index`/`_mul_sign` pair cannot be the general
product representation.

The general table must map a pair of input blades to a sparse linear
combination:

```text
(left bitmask, right bitmask)
    -> [(output bitmask, coefficient), ...]
```

### Ground-truth construction

The reference implementation should use the Chevalley action on the exterior
algebra. Left multiplication by a basis vector is wedge plus contraction:

$$
C_i(e_{j_1}\wedge\cdots\wedge e_{j_k})
=e_i\wedge e_{j_1}\wedge\cdots\wedge e_{j_k}
+\sum_{r=1}^{k}(-1)^{r-1}G_{i j_r}
 e_{j_1}\wedge\cdots\widehat{e_{j_r}}\cdots\wedge e_{j_k}.
$$

These operators obey the defining Clifford relation:

$$
C_iC_j+C_jC_i=2G_{ij}I.
$$

For a higher-grade exterior blade, its left-multiplication operator is the
antisymmetrized product of the vector operators:

$$
L_{i_1\ldots i_k}
=\frac{1}{k!}
\sum_{\pi\in S_k}\operatorname{sgn}(\pi)
C_{i_{\pi(1)}}\cdots C_{i_{\pi(k)}}.
$$

The production table should build the same operators by a dynamic recurrence,
avoiding factorial work. Applying `L_A` to exterior basis blade `B` gives all
coefficients of `A * B`.

This construction is preferable to diagonalizing the Gram matrix as the core
algorithm. Diagonalization introduces a hidden basis, floating-point
eigenvectors, and avoidable round-off into products whose input Gram entries
may be exact integers or simple rationals. It would also undermine the goal
that the user-supplied basis is native.

### Storage

A dense coefficient tensor of shape `(2^n, 2^n, 2^n)` scales as $O(8^n)$ and
must not be the only representation. Store general products in a CSR-like
layout over flattened input pairs:

```python
_mul_offsets   # length dim * dim + 1
_mul_outputs   # output bitmask for each stored term
_mul_factors   # coefficient for each stored term
```

The terms for `(a, b)` occupy:

```python
row = a * dim + b
start, stop = _mul_offsets[row : row + 2]
```

No tolerance-based coefficient pruning should occur. Exact zero coefficients
may be omitted; small nonzero coefficients must remain.

### Preserve the diagonal fast path

A diagonal Gram matrix still gives at most one output blade per input pair.
For that case, retain the current compact `_mul_index` and `_mul_sign` tables
and vectorized product loop. This preserves existing performance and memory
use for VGA, PGA, STA, and orthogonal CGA.

The metric's **semantic** representation is always the Gram matrix. Selecting
a monomial or sparse multiplication backend is an internal optimization.

The initial implementation should benchmark three strategies for general
metrics:

1. sparse pair expansions;
2. dense left-regular matrices for small `n`; and
3. on-demand cached blade products for larger `n`.

The sparse pair expansion should be the default unless benchmarks show a
clear dimension-dependent crossover.

## Construction-time precomputation plan

`Algebra` should leave construction with everything required for scalar,
exterior, geometric, and grade-selected products. Operations must not perform
metric factorization or rebuild blade products on every call.

Construction has four stages: normalize the metric, prepare metric-independent
exterior metadata, classify the metric, and build one multiplication backend.

### Stage 1: Normalize the metric input

Resolve every constructor form to the same read-only Gram matrix before any
other algebra state is built:

```python
Algebra(3, 0, 1)       -> diag(0, 1, 1, 1)
Algebra(signature=[1, 1, 1, 0]) -> diag(1, 1, 1, 0)
Algebra(sig=[1, 1, 1, 0])       -> diag(1, 1, 1, 0)
Algebra(gram=G)        -> validated symmetric copy of G
```

Store eagerly:

```python
_gram             # read-only float64[n, n]
_basis_squares    # read-only diagonal of _gram
_n
_dim              # 1 << n
```

The diagonal-backend decision must use an exact check after Gram
canonicalization:

```python
_is_diagonal = np.array_equal(_gram, np.diag(_basis_squares))
```

It must not use `allclose`, because treating a small nonzero off-diagonal entry
as zero changes the Clifford algebra requested by the caller.

Also record whether the matrix is a normalized legacy signature matrix:

```python
_has_legacy_signature = (
    _is_diagonal
    and all(square in (-1.0, 0.0, 1.0) for square in _basis_squares)
)
```

This controls whether the compatibility `signature` property is available; it
does not select product semantics.

### Stage 2: Prepare the exterior-basis structure

The following data depends only on `n`, not on the Gram matrix:

```python
_blade_grades      # uint8[dim], popcount of each bitmask
_grade_masks       # one bool[dim] mask per grade
_wedge_factor      # int8[dim, dim], 0 or exterior permutation sign
_complement_index  # uint/uintp[dim], full_mask ^ blade
_complement_sign   # int8[dim]
```

The exterior product of bitmasks `a` and `b` then uses:

```python
factor = _wedge_factor[a, b]
output = a ^ b
```

where `factor == 0` when `a & b != 0`. No metric table is involved.

These arrays should be held in an immutable module-level cache keyed by `n`
and shared among `Algebra` instances. Algebra construction fetches the cache
entry, building it once for a dimension. This avoids duplicating the same
grade, wedge, and complement data for every metric of the same dimension.

Blade names, convention overrides, local-name hints, and display order are
then constructed per algebra. They are not part of the shared cache because
they depend on user configuration and, for metric-role keys, on
`_basis_squares`.

### Stage 3: Classify and cache metric metadata

Compute and store:

```python
_inertia           # (p, q, r), using a documented scale-aware tolerance
_metric_rank       # consistent with the inertia tolerance
_metric_det        # unthresholded numerical determinant
```

Inertia is needed by `repr`, compact matrix classification, and algorithms
that distinguish degenerate from nondegenerate algebras. It should be computed
once, not by repeatedly counting a signature or diagonalizing the matrix.

The tolerance affects only classification. It does not alter `_gram`, product
coefficients, or `_metric_det`. If applications require control over a nearly
singular metric, the eventual constructor API may expose an `inertia_tol=`
argument; the prototype should first establish a stable default based on
matrix scale and machine epsilon.

Do not eagerly compute or retain an orthogonalizing eigendecomposition. Core
products do not require one, and an eigenbasis may be non-unique. The compact
matrix package can lazily factor the metric when a compact representation is
requested.

### Stage 4A: Precompute the diagonal backend

When `_is_diagonal` is true, eagerly build the current monomial product tables:

```python
_mul_index[a, b]   # a ^ b
_mul_factor[a, b]  # reorder sign times repeated-vector metric factors
```

This path works for arbitrary diagonal entries, not only `-1`, `0`, and `1`.
For example, a diagonal basis vector with square `2.5` contributes that exact
factor when its bit is repeated.

The table builder reads `_basis_squares`; `_gram` remains the authoritative
metric. `_mul_factor` is a clearer eventual name than `_mul_sign`, because a
general diagonal metric factor need not be a sign. A compatibility alias for
the private name is unnecessary once all monorepo consumers migrate together.

### Stage 4B: Precompute the general-Gram backend

For a non-diagonal Gram matrix, eagerly generate the sparse expansion of every
basis-blade pair when it fits the construction budget.

First build the sparse vector-action operators $C_i$. For each basis vector
`i` and exterior blade `B`, the Chevalley formula gives the complete expansion
of `ei * B`. These operators contain only wedge and single-contraction terms
and can be generated directly from `_wedge_factor` and `_gram`.

Then build the left-action operator $L_A$ for every exterior blade `A` in
increasing grade. A dynamic recurrence avoids antisymmetrizing over all
permutations. If `i` is the lowest set bit of `A` and `C = A without i`, then

$$
L_A=C_iL_C-L_{e_i\mathbin{\lrcorner}C}.
$$

For $C=e_{j_1}\wedge\cdots\wedge e_{j_k}$, expand the contraction using

$$
e_i\mathbin{\lrcorner}C
=\sum_{r=1}^{k}(-1)^{r-1}G_{i j_r}
e_{j_1}\wedge\cdots\widehat{e_{j_r}}\cdots\wedge e_{j_k}.
$$

All operators referenced on the right have lower grade and are already
available. This recurrence must be verified against the direct
antisymmetrization formula in tests before becoming the production builder.

Each column `B` of $L_A$ is the expansion of `A * B`. During construction:

1. combine contributions with the same output bitmask;
2. remove coefficients that are exactly zero after combination;
3. sort remaining outputs by bitmask for deterministic tables;
4. count the terms for every flattened pair `(A, B)`;
5. prefix-sum the counts into `_mul_offsets`; and
6. allocate and fill `_mul_outputs` and `_mul_factors` exactly once.

The temporary $C_i$ and $L_A$ builders should be released after packing. The
packed table already contains the same left-action information, and retaining
both forms would double memory. A companion package that needs dense
left-regular matrices can materialize and cache them lazily from the packed
table.

Store no separate multiplication table for each inner-product convention.
At runtime, `gp` consumes every packed term, while contractions and inner
products select terms using `_blade_grades[output]`. The grade lookup is small,
shared, and cheaper than duplicating product coefficients.

### Construction budget and fallback

The diagonal table always has exactly `dim * dim` monomial entries. A general
Gram table can grow much larger, with a dense worst case approaching
$O(8^n)$. Construction must therefore have an explicit memory policy.

The prototype should measure packed term counts for representative sparse and
dense metrics and define an internal byte budget. In `auto` mode:

1. diagonal metrics always use the full monomial table;
2. general metrics use the fully packed table while its predicted or measured
   size is within budget; and
3. larger tables retain the vector-action operators and generate/cache
   $L_A$ one left blade at a time on demand.

The fallback cache should be bounded and keyed by the left blade bitmask. One
cached $L_A$ supplies `A * B` for every right blade `B`, which gives better
reuse than caching individual pairs.

The first production release may instead apply a clear dimension/term-count
guard to general metrics if the lazy fallback is not yet ready. It must fail
before a large allocation with an actionable error; it must not exhaust memory
or silently diagonalize the metric.

Do not expose backend selection in the first public API. Keep enough internal
instrumentation to report construction time, term count, and packed bytes in
benchmarks. Add a public tuning option only if real workloads demonstrate a
need.

### Keep derived full-algebra matrices lazy

The following values are useful but can each require $O(4^n)$ or more memory,
so they should remain lazy read-only caches:

```python
extended_metric_matrix()          # compound matrices of G
metric_antiexomorphism_matrix()   # complementary compound matrices
left-regular dense matrices       # companion matrix package
compact metric factorization      # companion matrix package
```

Algebra construction precomputes the product kernel, not every matrix that can
be derived from it.

## Effects on existing operations

### Exterior product and grade operations

The outer product is metric-independent and should keep a direct bitmask/XOR
implementation. It need not compute a full geometric product and discard
terms.

Grade masks, grade projection, reverse, grade involution, Clifford
conjugation, complements, coefficient storage, and rendering remain based on
the exterior bitmask basis and are unchanged in principle.

Inner products and contractions must iterate over every output term of a
basis-blade product and apply their existing grade-selection rules to each
term. They can no longer inspect one `_mul_index[i, j]` value.

### Metric and antimetric extensions

`extended_metric_matrix()` is currently diagonal because the metric is
diagonal. For a general Gram matrix, it becomes the exterior extension
$\bigwedge G$. Its grade-$k$ block is the $k$th compound matrix of `G`; its
entries are the corresponding $k\times k$ minors.

`metric_antiexomorphism_matrix()` becomes the complementary-compound matrix.
For invertible `G`, it is equivalently

$$
\det(G)(\bigwedge G)^{-1},
$$

but it must be constructed from complementary minors rather than an inverse
so that degenerate metrics remain supported. The existing identity

$$
(\bigwedge G)\,\overline{\bigwedge G}=\det(G)I
$$

must continue to hold.

This part of the migration is required to preserve the RGA convention layer;
it is not an optional follow-up.

### Matrix representations

The left-regular representation naturally consumes the new product expansion
table and continues to work for all metrics.

Compact matrix representations depend on the algebra's inertia rather than on
the coordinates of its basis. They should:

1. classify `G` by Sylvester inertia `(p, q, r)`;
2. construct matrices for an orthogonal canonical frame; and
3. transform those generator matrices into the user basis so that
   `gamma[i] @ gamma[j] + gamma[j] @ gamma[i] == 2 * G[i, j] * I`.

Until that transformation is implemented and tested, compact mode should
reject a non-diagonal Gram matrix with an explicit error. Left-regular mode is
a correct fallback.

## Signature, inertia, and compatibility APIs

A non-orthogonal metric exposes three different concepts that the current
`signature` property conflates:

- `gram`: all basis-vector scalar products;
- `basis_squares`: `tuple(np.diag(gram))`; and
- `inertia`: the basis-independent counts `(p, q, r)`.

Add all three concepts explicitly:

```python
alg.gram           # read-only n x n array
alg.basis_squares  # tuple of e_i**2 in the current basis
alg.inertia        # (positive, negative, null eigenvalue counts)
alg.is_orthogonal_basis
```

Keep `signature` unchanged for legacy normalized diagonal algebras. For a
non-diagonal Gram matrix, accessing `signature` should raise a clear error
directing callers to `gram`, `basis_squares`, or `inertia`. Returning the
diagonal would discard cross terms; returning a canonical diagonal signature
would pretend that it described the current basis. Either behavior would be a
dangerous lie.

Internal and companion-package code that only counts positive, negative, and
null directions must migrate from `signature` to `inertia`. Code that needs
$e_i^2$ must use `basis_squares[i]`. Code that performs products must use the
Gram matrix or product backend.

`repr(alg)` may continue to lead with `Cl(p,q,r)`, because inertia classifies
the abstract real Clifford algebra, but it should mark a non-orthogonal basis,
for example:

```text
Cl(4,1; non-orthogonal basis)
```

It should not print the full matrix in the short representation.

## Blade conventions

Metric-role keys such as `+1`, `-1`, and `_1` should continue to describe the
squares of the **stored basis vectors**, using the signs of `diag(G)`. They do
not describe the inertia of the full metric. This preserves existing behavior
for diagonal metrics and gives null native CGA vectors the roles `_1` and
`_2`.

Convention factories whose structure is positional should prefer tuple keys
such as `(3, 4)` over metric-role keys. In particular, `b_cga()` should no
longer locate its Minkowski-plane bivector by searching for a positive and a
negative basis vector when used with the null Gram matrix.

Any convention feature that derives a sign from a sequence of distinct vector
indices should derive the exterior permutation sign, independent of the
metric. A geometric word in non-orthogonal vectors is not generally a single
basis blade. Repeated-vector `NamedBlade` specifications should therefore
require an explicit sign or be rejected for a general Gram matrix.

## Correctness strategy

The implementation must follow the project's compute-first rule. Build and
test the Chevalley reference product before changing display conventions or
CGA convenience functions.

### Foundational metric tests

For every pair of native basis vectors, test against the supplied matrix:

```python
scalar_product(ei, ej) == G[i, j]
ei * ej + ej * ei == 2 * G[i, j]
```

This is the general-Gram equivalent of `TestSignConsistency` and must be the
first correctness layer.

### Native CGA regression tests

For the proposed null CGA matrix, verify directly:

```python
e4 * e4 == 0
e5 * e5 == 0
e4 | e5 == -1
e4 * e5 == -1 + e45
e5 * e4 == -1 - e45
```

Also verify that `e4`, `e5`, and `e45` are one-hot native exterior blades.

### Change-of-basis equivalence

Use the existing orthogonal `Algebra(4, 1)` implementation as an independent
reference. Define

```python
eo = (em - ep) / 2
einf = em + ep
```

and construct the induced outermorphism on all 32 exterior basis blades. Every
pair of native-null-basis blade products must agree with the transformed
orthogonal-basis product. Test the full $32\times32$ basis-blade product table,
not just selected CGA identities.

### General algebra laws

For random symmetric Gram matrices, including dense, sparse, nondegenerate,
and degenerate examples, test:

- bilinearity;
- associativity of the geometric product;
- the Clifford relation;
- metric independence and antisymmetry of the wedge product;
- all inner-product grade-selection rules;
- reverse and conjugation identities; and
- metric/antimetric complementary-minor identities.

Cross-check small non-orthogonal examples against another implementation such
as kingdon when it supports the same basis convention. The Chevalley reference
implementation and orthogonal change-of-basis tests remain mandatory even if
an external library is used.

### Diagonal compatibility and performance

Run the complete existing suite unchanged against legacy constructors. Add a
test that all diagonal products agree with the current XOR/sign algorithm.
Benchmark representative dimensions before merging and set explicit
regression thresholds for the diagonal fast path.

## Migration plan

### Phase 1: Algebraic prototype

1. Implement the Chevalley vector action in a test/reference module.
2. Generate general basis-blade products by antisymmetrization.
3. Verify native CGA against the existing orthogonal model.
4. Decide the sparse-table layout from measured term counts.

This phase should not alter public APIs.

### Phase 2: Canonical metric model

1. Add immutable `_gram`, `gram`, `basis_squares`, and `inertia`.
2. Make all existing constructors produce diagonal Gram matrices.
3. Add the keyword-only `gram=` constructor.
4. Retain the current diagonal multiplication backend.
5. Migrate internal signature consumers to the property they actually need.

### Phase 3: General product backend

1. Add sparse product expansions.
2. Route geometric and grade-selected products through the appropriate
   backend.
3. Keep wedge on its metric-independent bitmask path.
4. Add the full foundational, associativity, and change-of-basis tests.

### Phase 4: Metric-derived operations

1. Generalize metric and antimetric exterior extensions using minors.
2. Audit duals, inverse, norms, rotor construction, and RGA operations.
3. Generalize the left-regular matrix representation.
4. Either transform compact matrix generators or reject non-diagonal metrics
   until that work is complete.

### Phase 5: Native CGA surface

1. Make the origin/infinity `b_cga()` convention semantically metric-aware.
2. Update the CGA convenience-functions proposal to consume native `eo` and
   `einf` directly when available.
3. Add examples and a notebook comparing orthogonal and null CGA frames.
4. Update the affected specifications and accepted ADRs.

## Alternatives considered

### Continue deriving null vectors in an orthogonal CGA basis

This is correct and remains a useful representation, but it does not make the
null vectors native and does not support arbitrary non-orthogonal frames.

### Store a $5\times5$ matrix for each CGA basis vector

This confuses a vector representation with the metric. Five coordinate basis
vectors require five coordinates each; in Galaga they are embedded as one-hot
vectors in the 32-dimensional exterior coefficient space. There is one shared
$5\times5$ Gram matrix that defines their scalar products.

Matrix representations of the Clifford algebra are a separate concern. A
faithful representation of $\mathrm{Cl}(4,1)$ is not obtained by assigning an
arbitrary $5\times5$ matrix to each basis vector.

### Diagonalize every supplied Gram matrix internally

Sylvester's law guarantees an orthogonal form, so this can implement the
abstract algebra. It does not preserve the supplied basis as the native
coefficient basis and introduces change-of-basis round-off into every value.
It remains useful for compact matrix construction, not as the core storage
model.

### Store a dense rank-3 multiplication tensor

This is simple and reasonable for a prototype or very small dimensions, but
its $O(8^n)$ memory growth is incompatible with the current design envelope.

### Compute every product on demand

This minimizes construction time but repeats expensive contraction work in
the hottest operation. A cached on-demand backend may be useful above a
dimension threshold, but it should not be the initial default for the small
algebras Galaga targets.

## Non-goals

- Complex-valued metrics or coefficients.
- Non-symmetric bilinear forms.
- Symbolic Gram-matrix entries.
- Mutable metrics.
- Replacing dense multivector coefficient arrays.
- Replacing exterior-blade bitmasks.
- Adding CGA primitives such as `up`, `down`, spheres, or lines in the same
  change; those build on this foundation.

## Documentation and ADR impact if accepted

Acceptance changes existing design decisions and therefore requires updates
to at least:

- ADR-011, because a basis-blade product is no longer always monomial;
- ADR-055, because `Cl(p,q,r)` becomes one constructor for a Gram-native
  algebra;
- ADR-057, because `b_cga(null_basis="origin_infinity")` can describe a real
  native null frame;
- ADR-071, because the metric and antimetric extensions become compound
  matrices rather than diagonal matrices;
- the blade-convention and algebra representation specifications; and
- the `galaga_matrix` representation ADRs.

The accepted ADR should record both the Gram-native semantic model and the
diagonal/sparse backend split. This proposal itself does not change those
accepted decisions.

## Recommendation

Adopt the Gram matrix as the native metric representation while preserving
bitmask exterior blades, dense $2^n$ multivector coefficients, and the current
diagonal multiplication path as an optimization.

Prototype the Chevalley product and validate the complete native-CGA product
table before committing to the sparse storage format. This isolates the main
mathematical risk—the expansion of non-orthogonal blade products—from the API,
rendering, and performance migrations that follow.
