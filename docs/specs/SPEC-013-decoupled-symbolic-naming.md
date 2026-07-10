# SPEC-013: Decoupled Symbolic Naming and Expression Trees

**Status: Accepted**

## Intent

Decouple the naming and symbolic expression-tree machinery that currently
lives inside `Multivector` so it can also be used by `galaga_matrix.MatrixRepr`
and future pedagogical value types.

The goal is not to replace Galaga's current symbolic behavior. The goal is to
factor the reusable parts into a small domain-neutral layer while preserving the
existing `Multivector` API, expression node identities, renderer behavior, and
MatrixRepr numeric behavior.

For `MatrixRepr`, this spec intentionally replaces the render-only `label=`
mechanism with `.name()`. The label field was a workaround for the absence of a
shared naming and expression-tree layer. Once that layer exists, MatrixRepr
should use the same naming vocabulary as Multivector.

This spec uses `/private/tmp/f/SPEC_GALAGA_INTEGRATION.md` and the
`/private/tmp/f/symbolic_engine/` cleanroom implementation as a proof-of-shape,
not as code to copy directly.

## Non-Goals

- Do not change the meaning of `Multivector.__mul__`. It remains the geometric
  product and builds `Gp` expression nodes.
- Do not make generic expression `*` mean an unqualified multiplication across
  all domains.
- Do not remove `galaga.ops.ga_op`, `GA_OPS`, or the existing GA operation
  registry contract in the first implementation.
- Do not break `from galaga.expr import Sym, Scalar, Add, Gp, ...`.
- Do not replace MatrixRepr's existing `algebra`, `mode`, `basis`, `kind`,
  `.mv`, `.quat`, `H`, `to_basis`, or numpy interop behavior.
- Do not preserve `MatrixRepr(label=...)` or `.label` as the target public
  naming API. Matrix names must be assigned with `.name()`.
- Do not treat `.name()` as render-only metadata for MatrixRepr. A named matrix
  is a symbolic leaf and participates in expression-tree construction.
- Do not add a new top-level package.

## Current Repo Constraints

### Existing `galaga.symbolic.py`

The external spec proposed a new `galaga/symbolic/` subpackage. This repo
already has `packages/galaga/galaga/symbolic.py`, a compatibility module for
symbolic decorators. A package and a module with the same import name would be
ambiguous and fragile.

Therefore the reusable layer must use a different package name.

Chosen name for this spec:

```text
packages/galaga/galaga/symbolic_core/
```

`galaga.symbolic` remains available for its current compatibility imports.

### Existing Symbolic Architecture

The current symbolic architecture is already split enough to avoid an
`algebra.py` to `expr.py` import cycle:

- `galaga.ops` is the GA operation registry leaf module.
- `@ga_op` handles symbolic dispatch and grade propagation.
- `galaga.expr` owns GA expression node classes.
- `galaga.render` and the LaTeX pipeline depend on concrete GA node classes.
- `Multivector` carries `_name`, `_name_latex`, `_name_unicode`,
  `_is_symbolic`, `_expr`, `_grade`, and `_is_basis`.

This is documented in [SPEC-012](SPEC-012-algebra-symbolic-split.md),
[ADR-018](../adrs/018-unified-naming-evaluation-semantics.md), and
[ADR-065](../adrs/065-operation-registry.md).

### Existing MatrixRepr Architecture

`MatrixRepr` is already more than a simple rendering wrapper:

- it wraps real, complex, and quaternion-block matrices;
- arithmetic returns `MatrixRepr` values;
- metadata currently includes `label`, `algebra`, `mode`, `basis`, and `kind`;
- `kind` drives ket/bra/operator propagation;
- `bra @ ket` returns a complex scalar, not a MatrixRepr;
- `.mv` converts back to a multivector when possible;
- `.quat` reads quaternion-mode matrices as quaternion grids;
- `.T`, `.H`, `.conj()`, `.inv()`, `.trace()`, `.det()`, `.kron()`, and
  `.to_basis()` have current behavior;
- `__array__` and `__array_ufunc__` support numpy interop;
- `.latex()` renders the matrix value, with an optional legacy label.

The symbolic extension must preserve the numeric and metadata behavior while
retiring `label` in favor of `.name()`. Existing label-era tests and docs are
expected to change as part of the implementation.

## Design Overview

Add a reusable symbolic core:

```text
packages/galaga/galaga/symbolic_core/
├── __init__.py
├── naming.py          # shared name normalization and symbolic-state mixin
├── expr.py            # domain-neutral expression nodes and domain dispatch
├── domain.py          # domain policy/registry for expression operators
└── render.py          # generic renderer for non-GA domains
```

The existing GA stack remains authoritative for GA semantics:

```text
galaga.ops          # keeps ga_op, GA_OPS, grade rules
galaga.expr         # keeps GA node names and compatibility exports
galaga.render       # keeps current unicode renderer for GA nodes
galaga.latex_*      # keeps current 3-phase LaTeX pipeline
```

`galaga_matrix` adds matrix-specific expression nodes and notation:

```text
packages/galaga_matrix/galaga_matrix/
├── repr.py          # MatrixRepr adopts shared naming mixin
├── expr.py          # matrix domain nodes: MatMul, Transpose, Adjoint, ...
└── notation.py      # matrix notation presets
```

## Core Rule: Products Are Domain-Specific

The shared expression tree may provide structural arithmetic:

- symbols;
- scalars;
- addition;
- subtraction;
- negation;
- scalar multiplication;
- scalar division;
- generic display/evaluation traversal.

It must not hardcode a universal meaning for non-scalar multiplication.

For GA:

```python
a * b  -> Gp(a, b)
a ^ b  -> Op(a, b)
a | b  -> Hi(a, b) or the configured GA pipe operation
~a     -> Reverse(a)
```

For matrices:

```python
A @ B  -> MatMul(A, B)
A * B  -> MatrixElementwiseMul(A, B) when both are matrices
A * k  -> ScalarMul(k, A)
A.T    -> Transpose(A)
A.H    -> Adjoint(A)
```

This preserves the meaning of every existing GA expression test while allowing
matrix expressions to use the same tree substrate.

## Symbolic Core

### `symbolic_core.naming`

Provide shared name-state machinery without importing `galaga.algebra` or
`galaga_matrix`.

Required public pieces:

```python
@dataclass(frozen=True)
class NameParts:
    ascii: str
    unicode: str
    latex: str

def normalize_name(
    label: str | None = None,
    *,
    latex: str | None = None,
    unicode: str | None = None,
    ascii: str | None = None,
) -> NameParts:
    ...

class SymbolicNamingMixin:
    _name: str | None
    _name_latex: str | None
    _name_unicode: str | None
    _is_symbolic: bool
    _expr: Expr | None

    def _init_symbolic_state(self) -> None: ...
    def name(...): ...
    def anon(self): ...
    def symbolic(self): ...
    def lazy(self): ...
    def numeric(self, name: str | None = None): ...
    def eager(self, name: str | None = None): ...
    def copy_as(...): ...
    def reveal(self): ...
    def eval(self): ...
```

Required subclass hooks:

```python
def _copy_with_symbolic(self, **overrides): ...
def _value_latex(self) -> str: ...
def _value_unicode(self) -> str: ...
def _symbolic_leaf_metadata(self) -> dict: ...
```

`normalize_name()` must preserve current Multivector behavior:

- at least one of `label` or `latex` is required;
- whitespace is stripped;
- `latex=` can derive unicode/ascii names through the existing
  `LatexSymbols` lookup;
- explicit `unicode=` and `ascii=` override derived values;
- unknown LaTeX commands fall back to the LaTeX string.

`Multivector.name()` may still override the mixin to protect basis vectors and
populate `_grade`.

### `symbolic_core.expr`

Provide a generic expression tree with compatibility-oriented attribute names.

Required structural nodes:

```python
Expr
Sym
Scalar
Add
Sub
Neg
ScalarMul
ScalarDiv
Div
```

Compatibility requirements:

- `Scalar` keeps `_value`.
- `Sym` keeps `_name`, `_name_latex`, `_name_ascii`, `_grade`,
  `_inner_expr`.
- `Sym` keeps `_mv` as a compatibility alias when the value is a Multivector.
- `Sym.eval()` returns the wrapped value.
- `Scalar.eval()` keeps the current GA behavior: by default it raises
  `TypeError` when evaluated without a domain context.
- `Sym.is_compound` and `Sym.has_superscript` preserve current behavior,
  including the brace-aware space check used for named expressions.

The generic `Expr` base uses a domain policy for non-structural operators:

```python
class Expr:
    def __add__(self, other): ...
    def __sub__(self, other): ...
    def __neg__(self): ...
    def __mul__(self, other):
        if scalar: return ScalarMul(other, self)
        return resolve_domain(self, other).build_operator("mul", self, other)
    def __xor__(self, other):
        return resolve_domain(self, other).build_operator("xor", self, other)
    def __or__(self, other):
        return resolve_domain(self, other).build_operator("or", self, other)
    def __matmul__(self, other):
        return resolve_domain(self, other).build_operator("matmul", self, other)
```

For current GA expressions, the GA domain maps:

```text
mul -> Gp
xor -> Op
or -> Hi
invert -> Reverse
inv -> Inverse
dag -> Reverse
sq -> Squared
```

For matrix expressions, the matrix domain maps:

```text
matmul -> MatMul
mul -> MatrixElementwiseMul
transpose -> Transpose
adjoint -> Adjoint
inverse -> MatrixInverse
```

Mixed-domain expressions are rejected unless a domain explicitly registers a
cross-domain operation.

### `symbolic_core.domain`

Provide a domain registry for expression semantics. This is not a replacement
for `galaga.ops.ga_op` in the first implementation.

Required responsibilities:

- map Python expression operators to node classes;
- map node classes to numeric evaluation functions;
- carry notation defaults for the generic renderer;
- reject mixed domains by default;
- support nodes with non-domain return values, such as matrix `bra @ ket`
  returning a complex scalar.

Sketch:

```python
class SymbolicDomain:
    name: str
    operators: dict[str, type[Expr]]
    evaluators: dict[type[Expr], Callable]
    notation: Notation

    def build_operator(self, op_key: str, *exprs) -> Expr: ...
    def evaluate(self, node: Expr): ...
```

`Multivector` exposes a GA domain adapter, but its numeric operations continue
to be registered through `@ga_op` and `GA_OPS`.

`MatrixRepr` exposes a matrix domain adapter.

### `symbolic_core.render`

Provide a generic renderer for domains that do not need Galaga's GA-specific
LaTeX pipeline.

The generic renderer must support:

- structural nodes;
- domain-specific nodes by notation rule;
- infix;
- juxtaposition;
- prefix;
- postfix;
- accent;
- superscript;
- function;
- wrap;
- precedence and associativity;
- explicit notation override;
- domain notation resolution by walking to `Sym` leaves.

The current GA renderers may use this renderer internally only where safe. The
first implementation should not replace the GA LaTeX pipeline.

## Multivector Integration

The first implementation should be conservative:

1. Keep `galaga.ops.ga_op`, `GA_OPS`, grade propagation, `make_sym`,
   `is_sym`, and `build_expr` working.
2. Keep `galaga.expr` public class names and class identities stable.
3. Optionally move structural node implementation into `symbolic_core.expr`,
   but re-export the exact same objects from `galaga.expr`.
4. Keep `Multivector.__mul__`, `__xor__`, `__or__`, and `__invert__`
   behavior unchanged.
5. Refactor `Multivector.name()` only after `normalize_name()` has tests that
   match existing behavior.
6. Keep `_grade` and `_is_basis` domain-specific.
7. Keep `display()` returning the current `_DisplayResult`, not a generic
   string.

The invariant tests from SPEC-012 must continue to pass:

- `ops.py` does not import `expr.py` or `render.py`;
- `algebra.py` does not import `expr.py`;
- every `GA_OPS` entry has a handler;
- operation arities stay consistent;
- grade propagation stays unchanged.

## MatrixRepr Integration

`MatrixRepr` adopts `SymbolicNamingMixin`, with the following target rules.

### `.name()` Replaces `label`

The target API removes MatrixRepr's render-only label concept:

```python
MatrixRepr(mat, label=r"\sigma_1")  # invalid target API
M.label                             # invalid target API
```

MatrixRepr naming is done with `.name()`:

```python
M = MatrixRepr(mat).name(latex=r"\sigma_1")
```

This is not a cosmetic rename. Calling `.name()` makes the matrix a symbolic
leaf. A named matrix has a concrete matrix value and a symbolic expression
identity, just like a named Multivector has a concrete multivector value and a
symbolic expression identity.

Derived matrices are symbolic when any operand is symbolic:

```python
A = MatrixRepr(mat).name("A", latex=r"\mathbf{A}")
B = MatrixRepr(mat2).name("B", latex=r"\mathbf{B}")
C = A @ B
```

`C` is symbolic, has a concrete matrix value, and carries a `MatMul(Sym(A),
Sym(B))` expression tree.

Because `galaga_matrix` is not yet published, the first implementation should
prefer a clean break over a long-lived compatibility alias. If a temporary shim
is needed while migrating notebooks, it must emit `DeprecationWarning`, be
private to the migration branch, and be removed before release.

### Matrix Constructor

Target constructor:

```python
class MatrixRepr:
    def __init__(
        self,
        data,
        *,
        algebra=None,
        mode: str = "left-regular",
        basis: str | None = None,
        kind: str = "operator",
    ): ...
```

`label` is not accepted. Naming is a second step, matching Multivector:

```python
M = MatrixRepr(mat, algebra=alg, mode="compact").name(latex=r"\rho(B)")
```

### Matrix Value Rendering

`MatrixRepr.latex()` is value-oriented by default: it renders the concrete
matrix body. If the matrix has a name, it may render the teaching form:

$$
\mathbf{A} = \begin{pmatrix} ... \end{pmatrix}
$$

Unnamed non-symbolic matrices render as bare matrix values.

When the matrix carries an algebra with `display_repr=True`,
`MatrixRepr.latex()` mirrors `Multivector.latex()` and delegates to
`MatrixRepr.display()`. This makes direct notebook interpolation render the
teaching form:

$$
\rho(a) = \begin{pmatrix} ... \end{pmatrix}
$$

or, for an unnamed symbolic matrix:

$$
\rho(a)\rho(b) = \begin{pmatrix} ... \end{pmatrix}
$$

Symbolic expression rendering is always available through:

```python
M.expr.latex()
M.display().latex()
```

`MatrixRepr.display()` should mirror Multivector's teaching shape:

```text
name = expression = value
```

but it returns a MatrixRepr-specific display object that renders the value as a
matrix, not as a multivector expansion.

### Matrix Operations That Build Trees

When any operand is symbolic, these operations should build expression trees
while preserving current numeric behavior:

| Operation | Current numeric behavior | Symbolic node |
|---|---|---|
| `A + B` | matrix addition | `MatrixAdd` or shared `Add` |
| `A - B` | matrix subtraction | `MatrixSub` or shared `Sub` |
| `-A` | negation | shared `Neg` |
| `k * A`, `A * k` | scalar multiplication | shared `ScalarMul` |
| `A * B` | elementwise multiplication | `MatrixElementwiseMul` |
| `A / k` | elementwise scalar division | shared `ScalarDiv` |
| `A @ B` | matrix multiplication with `kind` propagation | `MatMul` |
| `A.T` | transpose | `Transpose` |
| `A.H` | Hermitian adjoint with ket/bra conversion | `Adjoint` |
| `A.conj()` | elementwise conjugate | `ConjugateMatrix` |
| `A.inv()` | matrix inverse | `MatrixInverse` |
| `A.kron(B)` | Kronecker product | `KroneckerProduct` |
| `A.to_basis("weyl")` | basis transform | `MatrixBasisChange` |

`trace()` and `det()` currently return complex scalars. They may be made
symbolic later, but the first implementation should preserve the scalar return
type unless a scalar wrapper type is introduced.

### Matrix Kind Propagation

Symbolic `MatMul` must preserve current `kind` behavior:

- `operator @ ket -> ket`;
- `ket @ bra -> operator`;
- `bra @ ket -> complex scalar`;
- other cases keep existing behavior.

If the result is a raw scalar, no MatrixRepr expression tree is returned in the
first implementation. A future scalar-symbolic type can revisit this.

### Matrix Metadata Preservation

Symbolic results preserve the same metadata as numeric results:

- `algebra`;
- `mode`;
- `basis`;
- `kind`;
- quaternion mode behavior;
- numpy array dtype and shape.

Names are not blindly propagated as labels. A derived symbolic matrix carries
an expression tree. If the derived value should have its own display name, the
caller assigns one explicitly:

```python
C = (A @ B).name("C")
```

## Representation-Map Expressions

MatrixRepr should represent conversion from a named multivector as a symbolic
representation map. This replaces the old auto-labeling behavior.

When `B` is a named multivector:

```python
B = B.name("B")
M = to_matrix(B, mode="compact")
```

the result is a named symbolic MatrixRepr with the same concrete matrix value
as before. Its expression tree is:

```text
MatrixRepresentation(Sym(B), mode="compact", basis=<resolved basis>)
```

and its default rendered expression is:

$$
\rho(B)
$$

The default compact representation map is written as plain $\rho$, including
the Pauli compact representation of $Cl(3,0)$ and the Dirac compact
representation of $Cl(1,3)$:

$$
\rho(B)
$$

For explicit non-default Dirac-family basis views, use a roman superscript:

$$
\rho^{\mathrm{Weyl}}(S)
$$

or:

$$
\rho^{\mathrm{Majorana}}(S)
$$

Quaternion-block mode is a separate representation rather than a basis view of
the default Dirac-family complex representation. It uses a quaternion subscript:

$$
\rho_{\mathbb{H}}(S)
$$

For unnamed multivectors, `to_matrix()` returns an unnamed MatrixRepr with no
symbolic expression tree unless the caller explicitly names it.

`from_matrix(alg, M)` uses MatrixRepr naming rather than `.label`:

- unnamed matrix input produces an unnamed Multivector;
- named matrix input produces a Multivector named as:

$$
\rho^{-1}(M)
$$

  where $M$ is the matrix's symbolic name or expression;
- raw numpy arrays remain unnamed.

Example:

```python
sigma_1 = MatrixRepr(pauli_x, algebra=cl3, mode="compact").name(latex=r"\sigma_1")
e1 = from_matrix(cl3, sigma_1, mode="compact")
```

The recovered multivector is named:

$$
\rho^{-1}(\sigma_1)
```

Roundtripping a named multivector through a matrix may still produce verbose
provenance:

```text
\rho^{-1}(\rho(B))
```

That verbosity is intentional and mirrors the existing Multivector naming
model: users can call `.name()` again when they want a cleaner pedagogical
display name.

## Backward-Compatibility Assessment

The existing `packages/galaga` test suite should continue to pass unchanged if
the implementation follows this spec.

The existing `packages/galaga_matrix` test suite will not pass unchanged,
because this spec intentionally removes the label-era API. Tests that currently
assert `MatrixRepr(label=...)`, `.label`, and label propagation must be migrated
to `.name()` and symbolic-expression assertions.

The existing test suite would not continue to pass if the external tmp spec
were implemented literally, because:

- `galaga.symbolic` would collide with the existing `symbolic.py` module;
- generic `Expr.__mul__` would stop building GA `Gp` nodes;
- `ga_op` and `GA_OPS` deletion would break operation-registry invariants;
- MatrixRepr naming/provenance behavior would be incomplete;
- MatrixRepr metadata and ket/bra return semantics would be incomplete;
- GA renderer and LaTeX pipeline class identity assumptions would be violated.

With this local spec:

- current `galaga` tests should pass unchanged;
- current `galaga_matrix` numeric, metadata, conversion, and interop tests
  should pass after replacing label-era expectations with `.name()` semantics;
- changed behavior is limited to the intentional MatrixRepr label removal and
  must be covered by migration tests;
- existing matrix tests may change only where they were asserting the old
  `label` API or behavior directly superseded by this spec.

## Required New Tests

These tests should be added with the implementation. They are not executable
until the feature exists, so they are recorded here as the required test plan
rather than committed as failing tests.

### `packages/galaga/tests/test_symbolic_core.py`

#### Name Normalization

- `test_normalize_name_matches_multivector_label`
- `test_normalize_name_latex_derives_greek_unicode_ascii`
- `test_normalize_name_latex_derives_mathbf_unicode_ascii`
- `test_normalize_name_unknown_latex_falls_back`
- `test_normalize_name_strips_whitespace`
- `test_normalize_name_requires_label_or_latex`
- `test_explicit_unicode_ascii_override_derived_values`

These tests should duplicate representative expectations from
`test_redesign.py` so the common helper is pinned before Multivector uses it.

#### Generic Expression Core

- `test_sym_keeps_compatibility_attributes`
- `test_scalar_keeps_value_attribute`
- `test_structural_add_sub_neg_eval_with_toy_domain`
- `test_scalar_mul_and_scalar_div_render`
- `test_mixed_domains_raise_type_error`
- `test_domain_operator_maps_mul_to_domain_node`
- `test_domain_operator_maps_matmul_to_domain_node`
- `test_two_domains_can_register_same_operator_name_without_collision`
- `test_domain_renderer_uses_explicit_notation_override`
- `test_domain_renderer_falls_back_to_domain_notation`

Use toy value classes rather than Multivector or MatrixRepr where possible.

### Existing `packages/galaga` Tests That Must Remain Unchanged

Run the full suite. Pay special attention to:

- `test_symbolic.py`
- `test_render.py`
- `test_latex_build.py`
- `test_notation.py`
- `test_redesign.py`
- `test_coverage.py` operation-registry invariants

Specific compatibility tests that must keep passing:

- `Expr.__mul__` builds `Gp`;
- `Expr.__xor__` builds `Op`;
- `Expr.__or__` builds the current GA pipe node;
- `Scalar.eval()` raises without algebra context;
- `Sym._mv` remains available for tests and render helpers;
- `Sym.is_compound` and `Sym.has_superscript` behave unchanged;
- `display()` returns the current `_DisplayResult`;
- `numeric(name=...)`, `anon()`, `reveal()`, `eval()`, and `copy_as()` behave
  unchanged.

### `packages/galaga_matrix/tests/test_matrix_symbolic.py`

#### Naming

- `test_matrix_name_sets_symbolic_state`
- `test_matrix_name_latex_unicode_ascii`
- `test_matrix_copy_as_is_non_mutating`
- `test_matrix_anon_removes_name_preserves_symbolic`
- `test_matrix_numeric_clears_expr`
- `test_matrix_numeric_with_name_keeps_display_name`
- `test_matrix_constructor_rejects_label_keyword`
- `test_matrix_has_no_label_property`
- `test_matrix_latex_uses_name_for_teaching_display`
- `test_to_matrix_named_mv_uses_name_not_label`
- `test_from_matrix_named_matrix_uses_name_not_label`
- `test_to_spinor_column_named_mv_uses_name_not_label`

#### Expression Trees

- `test_named_matrix_add_builds_expr_and_preserves_value`
- `test_named_matrix_sub_builds_expr_and_preserves_value`
- `test_named_matrix_scalar_mul_builds_expr_and_preserves_value`
- `test_named_matrix_elementwise_mul_builds_matrix_elementwise_node`
- `test_named_matrix_matmul_builds_matmul_node`
- `test_named_matrix_transpose_builds_transpose_node`
- `test_named_matrix_adjoint_builds_adjoint_node`
- `test_named_matrix_inverse_builds_inverse_node`
- `test_named_matrix_kron_builds_kron_node`
- `test_named_matrix_to_basis_builds_basis_change_node`
- `test_matrix_expression_eval_matches_concrete_matrix`

#### Rendering

- `test_matrix_expr_unicode_renders_names`
- `test_matrix_expr_latex_renders_names`
- `test_matrix_expr_parenthesizes_add_before_matmul`
- `test_matrix_functional_notation`
- `test_matrix_display_renders_name_expr_and_matrix_value`
- `test_matrix_latex_remains_value_oriented`

#### Metadata and Interop

- `test_symbolic_matmul_preserves_algebra_mode_basis`
- `test_symbolic_operator_at_ket_returns_ket`
- `test_symbolic_ket_at_bra_returns_operator`
- `test_symbolic_bra_at_ket_returns_complex_scalar`
- `test_symbolic_adjoint_flips_ket_bra`
- `test_symbolic_quaternion_matrix_keeps_quaternion_mode`
- `test_symbolic_matrix_array_protocol_still_works`
- `test_symbolic_matrix_ufunc_still_wraps_matrix_results`
- `test_symbolic_from_matrix_roundtrip_still_works`

#### Non-Collision With Multivector

- `test_matrix_matmul_node_does_not_affect_ga_gp`
- `test_matrix_transpose_node_does_not_affect_ga_reverse`
- `test_import_order_galaga_then_galaga_matrix`
- `test_import_order_galaga_matrix_then_galaga`

### Example Test Sketches

These examples are illustrative, not final code.

```python
def test_matrix_constructor_rejects_label_keyword():
    with pytest.raises(TypeError):
        MatrixRepr(np.eye(2), label=r"\sigma_1")
```

```python
def test_matrix_name_sets_symbolic_state():
    M = MatrixRepr(np.eye(2)).name(latex=r"\sigma_1")

    assert M._name_latex == r"\sigma_1"
    assert M._is_symbolic
    assert M._expr is not None
    assert r"\sigma_1 =" in M.latex()
```

```python
def test_named_matrix_matmul_builds_matmul_node():
    A = MatrixRepr(np.array([[1, 2], [3, 4]], dtype=complex)).name("A")
    B = MatrixRepr(np.array([[0, 1], [-1, 0]], dtype=complex)).name("B")

    C = A @ B

    assert C._is_symbolic
    assert type(C._expr).__name__ == "MatMul"
    assert np.allclose(C.mat, A.mat @ B.mat)
    assert C._expr.latex() in {"A B", r"A B"}
```

```python
def test_expr_mul_still_builds_ga_gp(cl3):
    from galaga.expr import Gp, Sym

    e1, e2, _ = cl3.basis_vectors()
    a = Sym(e1, "a")
    b = Sym(e2, "b")

    assert isinstance(a * b, Gp)
```

```python
def test_symbolic_bra_at_ket_returns_complex_scalar():
    ket = MatrixRepr(np.array([[1], [0]], dtype=complex), kind="ket").name(r"\psi")
    bra = ket.H

    result = bra @ ket

    assert isinstance(result, complex | np.complexfloating)
    assert result == 1
```

## Migration Plan

### Phase 0: Pin Current Behavior

Before implementation:

1. Run the current `galaga` and `galaga_matrix` suites.
2. Add characterization tests for any MatrixRepr behavior not already covered:
   label removal, `kind`, `basis`, quaternion mode, and numpy interop.
3. Add name-normalization tests that mirror current Multivector behavior.

### Phase 1: Add `galaga.symbolic_core`

Add the new package without changing Multivector or MatrixRepr.

Tests:

- symbolic core tests only;
- no existing tests should change.

### Phase 2: MatrixRepr Symbolic Naming

Add symbolic fields and `.name()`/`.anon()`/`.symbolic()`/`.numeric()` to
MatrixRepr, and remove `label=`/`.label` from the public API.

Tests:

- MatrixRepr naming tests;
- full `galaga_matrix` suite.

### Phase 3: MatrixRepr Expression Trees

Add matrix expression nodes and symbolic-aware operation wrappers.

Tests:

- MatrixRepr expression tree tests;
- metadata and interop tests;
- import-order tests.

### Phase 4: Multivector Reuse

Only after MatrixRepr support is stable, refactor Multivector to reuse shared
name-normalization and structural expression code where it does not change
public behavior.

Tests:

- full `galaga` suite;
- explicit class identity/import compatibility checks;
- SPEC-012 invariants.

### Phase 5: Representation-Map Symbolics

Implement symbolic representation-map nodes such as:

```python
MatrixRepresentation(Sym(B), mode="pauli")
```

This phase replaces auto-labeling with auto-naming for `to_matrix()` and
`from_matrix()`.

## Documentation Requirements

If implemented, update:

- `docs/DESIGN_DECISIONS.md` with the shared symbolic-core principle;
- an ADR recording the accepted design;
- `docs/specs/README.md`;
- `packages/galaga_matrix/README.md` MatrixRepr section;
- `packages/galaga_matrix/docs/adrs/004-matrix-repr-rendering-wrapper.md`
  label references;
- `packages/galaga_matrix/docs/adrs/007-auto-labeling-rho.md`, superseding
  auto-labeling with auto-naming;
- relevant notebooks showing named MatrixRepr expression trees.

The ADR should state that Galaga's symbolic core is pedagogical and
convention-explicit, not a performance-first abstraction.

## Acceptance Criteria

Implementation is complete only when:

1. Current `packages/galaga/tests` pass unchanged.
2. Current `packages/galaga_matrix/tests` pass after label-era expectations are
   migrated to `.name()` and symbolic-expression expectations.
3. New `symbolic_core` tests pass.
4. New `MatrixRepr` symbolic tests pass.
5. `MatrixRepr(label=...)` is rejected and `.label` is absent from the public
   API.
6. `MatrixRepr(...).name(...)` builds symbolic trees for supported operations.
7. Matrix symbolic operations preserve concrete matrix values and metadata.
8. GA expression semantics are unchanged.
9. Import order does not affect registered operations or renderers.
10. The implementation has an accepted ADR before release.
