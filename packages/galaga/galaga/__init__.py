"""ga — Geometric Algebra for Python.

A numeric Clifford algebra library with a stable, programmer-first API.

Architecture
------------
The library is split into two modules:

- ``ga.algebra``   — The numeric core. Defines ``Algebra`` (the Clifford algebra
  factory) and ``Multivector`` (the value type), plus every named operation
  (``gp``, ``op``, ``grade``, ``reverse``, etc.). All computation happens here
  via precomputed multiplication tables and dense NumPy coefficient arrays.

- ``ga.symbolic``  — An expression-tree layer for pretty-printing and symbolic
  manipulation. Provides ``simplify()`` and drop-in replacements for all
  numeric functions that detect lazy ``Multivector`` arguments and build
  expression trees. The ``Expr`` class hierarchy is an internal implementation
  detail.

Naming and Evaluation
---------------------
Every ``Multivector`` independently controls two orthogonal axes:

- **Identity / display** — ``.name("B")`` assigns a display name;
  ``.anon()`` removes it.
- **Evaluation strategy** — ``.lazy()`` preserves expression trees;
  ``.eager()`` forces concrete evaluation in-place (strips name by default,
  or ``.eager("B")`` to keep it); ``.eval()`` returns a new anonymous eager
  copy without mutating the original.

Basis blades from ``Algebra.basis_vectors()`` are **named + eager** by default:
they have display names (``e₁``) but behave as concrete numeric objects.

``sym(mv, "R")`` is a convenience alias for ``mv.name("R")``.

This ``__init__`` re-exports the numeric API so users can write
``from galaga import *`` and get everything they need for computation.
The symbolic layer is imported separately (``from galaga import sym, ...``)
because it's opt-in — most users only need it for notebooks and display.

Design Principles
-----------------
- **Named functions are the contract.** ``gp``, ``op``, ``grade``, ``reverse``
  never change meaning. Operators (``*``, ``^``, ``|``, ``~``) are sugar.
- **No ambiguity.** Every inner product variant has its own name. The ``|``
  operator maps to Doran–Lasenby inner, but ``left_contraction``,
  ``right_contraction``, ``hestenes_inner``, and ``scalar_product`` are
  always available.
- **Aliases exist for convenience**, not as separate implementations.
  ``wedge`` is literally ``op``, ``rev`` is literally ``reverse``, etc.
- **Lazy is contagious.** When a lazy MV operates with an eager one, the
  result is lazy. When all operands are eager, the fast numeric path is taken.
"""

from galaga.algebra import (
    Algebra,
    Multivector,
    anticommutator,
    commutator,
    complement,
    conjugate,
    doran_lasenby_inner,
    dorst_inner,
    dual,
    even_grades,
    exp,
    # Aliases
    geometric_product,
    # Core operations
    gp,
    grade,
    grade_involution,
    grades,
    hestenes_inner,
    inner_product,
    inverse,
    involute,
    ip,
    is_basis_blade,
    is_bivector,
    is_even,
    is_rotor,
    # Predicates
    is_scalar,
    is_vector,
    join,
    jordan_product,
    left_contraction,
    lie_bracket,
    log,
    mag2,
    magnitude_squared,
    meet,
    metric_regressive_product,
    norm,
    norm2,
    norm_squared,
    normalise,
    normalize,
    odd_grades,
    op,
    outer_product,
    project,
    reflect,
    regressive_product,
    reject,
    rev,
    # Unary
    reverse,
    right_contraction,
    sandwich,
    scalar_product,
    scalar_sqrt,
    sqrt,
    squared,
    sw,
    uncomplement,
    undual,
    unit,
    wedge,
)
from galaga.basis_blade import BasisBlade
from galaga.expr import sym
from galaga.notation import Notation
from galaga.simplify import simplify

__all__ = [
    "Algebra",
    "BasisBlade",
    "Multivector",
    "Notation",
    "simplify",
    "sym",
    "gp",
    "op",
    "left_contraction",
    "right_contraction",
    "hestenes_inner",
    "doran_lasenby_inner",
    "dorst_inner",
    "scalar_product",
    "commutator",
    "anticommutator",
    "lie_bracket",
    "jordan_product",
    "reverse",
    "involute",
    "grade_involution",
    "conjugate",
    "grade",
    "grades",
    "scalar_sqrt",
    "sqrt",
    "dual",
    "undual",
    "complement",
    "uncomplement",
    "regressive_product",
    "metric_regressive_product",
    "meet",
    "join",
    "norm2",
    "norm",
    "unit",
    "inverse",
    "is_scalar",
    "is_vector",
    "is_bivector",
    "is_even",
    "is_rotor",
    "is_basis_blade",
    "even_grades",
    "odd_grades",
    "squared",
    "sandwich",
    "sw",
    "exp",
    "log",
    "project",
    "reject",
    "reflect",
    "geometric_product",
    "wedge",
    "outer_product",
    "rev",
    "normalize",
    "normalise",
    "norm_squared",
    "magnitude_squared",
    "mag2",
    "ip",
    "inner_product",
]
