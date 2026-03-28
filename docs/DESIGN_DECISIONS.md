# Design Decisions

High-level principles that guide the `galaga` geometric algebra library.

## 1. Named functions are the contract

Every operation has a stable, named function: `gp`, `op`, `grade`, `reverse`, `dual`, `inverse`, etc. These names never change meaning.

Operators (`*`, `^`, `|`, `~`) are sugar — convenient, but not the API you depend on. If there's ever ambiguity about what an operator does, the named function resolves it.

## 2. No ambiguity

Where mathematics has competing conventions, we expose each one explicitly rather than picking a default.

- Inner products: `left_contraction`, `right_contraction`, `hestenes_inner`, `doran_lasenby_inner`, `scalar_product` — all available, all named.
- Commutator family: `commutator` (ab − ba), `lie_bracket` (½(ab − ba)), `anticommutator` (ab + ba), `jordan_product` (½(ab + ba)) — four functions, no boolean flags.
- The `|` operator maps to Doran–Lasenby inner, but that's documented sugar, not a hidden choice.

## 3. Explicit over implicit

Two named functions beat one function with a mode flag. `lie_bracket(a, b)` is self-documenting; `commutator(a, b, half=True)` is not.

The ½ in `lie_bracket` vs `commutator` is not a formatting choice — it changes the algebraic convention. That distinction deserves its own name.

## 4. Aliases exist for convenience, not as separate implementations

`wedge` is literally `op`. `rev` is literally `reverse`. `normalize` is literally `unit`. They share the same function object — no divergence, no maintenance burden.

## 5. Two-layer architecture

- **`galaga.algebra`** — The numeric core. `Algebra` (factory), `Multivector` (value type), and every named operation. Computation happens here via precomputed multiplication tables and dense NumPy arrays.
- **`galaga.symbolic`** — An expression-tree layer for pretty-printing and symbolic manipulation. The `Expr` class hierarchy is an internal implementation detail — users interact with `Multivector` objects that may optionally carry an expression tree.

`Multivector` is the single public type. It can be named or anonymous, lazy or eager — these are orthogonal axes controlled by `.name()`, `.anon()`, `.lazy()`, `.eager()`.

## 6. Naming and evaluation are orthogonal

Every multivector independently controls two things:

- **Identity / display** — named (prints as `B`) or anonymous (prints as `e₁₂`)
- **Evaluation strategy** — lazy (preserves expression tree) or eager (concrete coefficients)

`.name("B")` makes an object named + lazy by default. `.eager()` forces concrete evaluation in-place and strips the name (or `.eager("B")` to keep it). `.eval()` returns a new anonymous eager copy without mutating the original. `.anon()` removes the name while preserving the lazy/eager state.

Basis blades are **named + eager** by default — they have display names (`e₁`) but behave as concrete numeric objects with no symbolic overhead. Use `basis_vectors(lazy=True)` for fully symbolic workflows where every operation builds an expression tree.

## 7. Lazy is contagious

When a lazy multivector participates in an operation with an eager one, the result is lazy. The result carries both concrete data (for `.eval()`) and an expression tree (for display). Names don't propagate — the result is anonymous, but named operands appear by name in the tree.

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
