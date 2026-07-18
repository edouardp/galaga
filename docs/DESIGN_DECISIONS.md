# Design Decisions

High-level principles that guide the `galaga` geometric algebra library.

> **Galaga 2 migration:** [`galaga.core`](core/README.md) is now the numeric
> engine of record. It coexists with the legacy `galaga.algebra` implementation
> until the composition facade passes the compatibility suite and becomes the
> top-level API. ADR-073 records this additive migration boundary. Sections
> describing `galaga.algebra` and its expression behavior document the legacy
> implementation during that transition.

## Project posture

Galaga is primarily a pedagogical geometric algebra library. It is not trying
to be the highest-performance GA implementation. Correctness, clarity,
inspectability, and explicit mathematical choices matter more than minimizing
the number of operations or choosing a single convention for speed.

Its secondary goal is to make the range of differing opinions in the GA
community usable from one codebase. When a convention is contested, Galaga
chooses a documented default and exposes other coherent conventions under
explicit names. Multiple named operations for similar-looking ideas are a
feature, not a failure, when they help users see exactly which mathematics they
are using.

## 1. Named functions are the contract

Every operation has a stable, named function: `gp`, `op`, `grade`, `reverse`, `dual`, `inverse`, etc. These names never change meaning.

Operators (`*`, `^`, `|`, `~`) are sugar — convenient, but not the API you depend on. If there's ever ambiguity about what an operator does, the named function resolves it.

## 2. No ambiguity

Galaga uses geometric-algebra terminology as its primary vocabulary. Where the
GA literature has competing conventions, Galaga chooses one documented default
and exposes the other conventions under explicit names.

For example, in linear algebra "inner product" usually means a scalar-valued
metric pairing such as `<x, y>`. In geometric algebra, "inner product" commonly
means a grade-selecting part of the geometric product, and it may return a
multivector rather than only a scalar. Galaga, as a geometric algebra library,
uses the geometric algebra approach to inner products while naming each
competing GA convention explicitly.

- Inner products: `left_contraction`, `right_contraction`, `hestenes_inner`, `doran_lasenby_inner`, `scalar_product` — all available, all named.
- Commutator family: `commutator` and `lie_bracket` are $ab-ba$;
  `anticommutator` and `jordan_product` are $ab+ba$. The explicitly named
  `half_commutator` and `half_anticommutator` introduce the factor of one half.
- The `|` operator maps to Doran–Lasenby inner, but that's documented sugar, not a hidden choice.

## 3. Explicit over implicit

Two named functions beat one function with a mode flag. `half_commutator(a,
b)` is self-documenting; `commutator(a, b, half=True)` is not.

The factor in `half_commutator` versus `commutator` is not a formatting choice;
it changes the algebraic convention. That distinction deserves its own name.

## 4. Aliases exist for convenience, not as separate implementations

`wedge` is literally `op`. `rev` is literally `reverse`. `normalize` is literally `unit`. They share the same function object — no divergence, no maintenance burden.

## 5. Layered architecture

The Galaga 2 target separates the layers as follows:

- **`galaga.core`** — Immutable numeric algebras and multivectors, product
  backends, metric extensions, and named numeric functions. It imports no
  presentation or expression code.
- **Galaga facade and operation catalog** — Composition wrappers that delegate
  numeric work to `galaga.core` while coordinating conventions, names, and
  optional expression provenance.
- **Presentation and integrations** — Blade conventions, notation, semantic
  rendering, and optional notebook or companion packages.

The following modules describe the legacy implementation retained during the
additive migration:

- **`galaga.ops`** — The operation registry. A leaf module with no internal dependencies. Every GA operation is registered here via `@ga_op` with algebraic metadata (name, arity, grade rule). The symbolic layer registers handlers against operation names. This breaks the circular dependency between algebra and expr.
- **`galaga.algebra`** — The numeric core. `Algebra` (factory), `Multivector` (value type), and every named operation. Computation happens here via precomputed multiplication tables and dense NumPy arrays. Never imports `expr`.
- **`galaga.expr`** — An expression-tree layer for pretty-printing and symbolic manipulation. The `Expr` class hierarchy is an internal implementation detail — users interact with `Multivector` objects that may optionally carry an expression tree. Node classes are auto-generated from a table that mirrors the operation registry.

`Multivector` is the single public type. It can be named or anonymous, symbolic or numeric — these are orthogonal axes controlled by `.name()`, `.anon()`, `.symbolic()`, `.numeric()`.

## 6. Naming and evaluation are orthogonal

Every multivector independently controls two things:

- **Identity / display** — named (prints as `B`) or anonymous (prints as `e₁₂`)
- **Evaluation strategy** — symbolic (carries expression tree) or numeric (concrete coefficients only)

`.name("B")` makes an object named + symbolic by default. `.numeric()` forces concrete evaluation in-place and strips the name (or `.numeric("B")` to keep it). `.eval()` returns a new anonymous numeric copy without mutating the original. `.anon()` removes the name while preserving the symbolic/numeric state.

Basis blades are **named + numeric** by default — they have display names (`e₁`) but behave as concrete numeric objects with no symbolic overhead. Use `basis_vectors(symbolic=True)` for fully symbolic workflows where every operation builds an expression tree.

## 7. Symbolic is contagious

When a symbolic multivector participates in an operation with a numeric one, the result is symbolic. The result carries both concrete data (for `.eval()`) and an expression tree (for display). Names don't propagate — the result is anonymous, but named operands appear by name in the tree.

When all operands are eager, the fast numeric path is taken with zero symbolic overhead.

## 8. Operators build expression trees transparently

In the symbolic layer, `R * v * ~R` builds a `Gp(Gp(R, v), Reverse(R))` tree — no special syntax needed. The same code that does numeric computation also builds symbolic expressions when any input is lazy.

## 9. Rendering protocol

Objects that can render as LaTeX expose `.latex()` (raw LaTeX content) and `_repr_latex_()` (Jupyter/IPython protocol with `$...$` wrapping). Named objects return their name in all formats; anonymous lazy objects delegate to the expression tree; anonymous eager objects render coefficients.

The `.name()` method accepts `latex=`, `unicode=`, `ascii=` keyword arguments for per-format name overrides.

## 10. Stable public surface

The `__init__.py` re-exports the numeric API so `from galaga import *` gives you everything for computation. The `__all__` list is the contract. New operations are added; existing ones don't change meaning.

## 11. Separate notebook helper

The marimo integration (`galaga_marimo` / `gamo`) is a separate package, not part of the core. It depends on marimo and uses Python 3.14 t-strings for automatic LaTeX rendering. This keeps the core library dependency-free (only NumPy) and framework-agnostic.

## 12. ADRs for specific decisions

Individual architectural decisions are recorded in [`docs/adrs/`](adrs/). Each ADR captures the context, decision, and consequences for a specific choice.
