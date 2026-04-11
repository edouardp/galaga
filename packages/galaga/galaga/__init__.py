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
  numeric functions that detect symbolic ``Multivector`` arguments and build
  expression trees. The ``Expr`` class hierarchy is an internal implementation
  detail.

Naming and Evaluation
---------------------
Every ``Multivector`` independently controls two orthogonal axes:

- **Identity / display** — ``.name("B")`` assigns a display name;
  ``.anon()`` removes it.
- **Evaluation strategy** — ``.symbolic()`` preserves expression trees;
  ``.numeric()`` forces concrete evaluation in-place (strips name by default,
  or ``.numeric("B")`` to keep it); ``.eval()`` returns a new anonymous numeric
  copy without mutating the original.

Basis blades from ``Algebra.basis_vectors()`` are **named + numeric** by default:
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
- **Symbolic is contagious.** When a symbolic MV operates with a numeric one, the
  result is symbolic. When all operands are numeric, the fast numeric path is taken.
"""

from .algebra import (
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
    outercos,
    outerexp,
    outersin,
    outertan,
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
from .basis_blade import BasisBlade
from .blade_convention import (
    BladeConvention,
    b_cga,
    b_complex,
    b_default,
    b_gamma,
    b_pga,
    b_quaternion,
    b_sigma,
    b_sigma_xyz,
    b_sta,
)
from .expr import sym
from .notation import Notation
from .simplify import simplify

__all__ = [
    "Algebra",
    "BasisBlade",
    "BladeConvention",
    "Multivector",
    "Notation",
    "b_cga",
    "b_complex",
    "b_default",
    "b_gamma",
    "b_pga",
    "b_quaternion",
    "b_sigma",
    "b_sigma_xyz",
    "b_sta",
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
    "outercos",
    "outerexp",
    "outersin",
    "outertan",
    "rev",
    "normalize",
    "normalise",
    "norm_squared",
    "magnitude_squared",
    "mag2",
    "ip",
    "inner_product",
]
