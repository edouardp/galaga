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
  manipulation. Wraps numeric multivectors with names (``sym(e1, "v")``) and
  builds lazy trees that render as Unicode/LaTeX. Every symbolic function is a
  drop-in replacement: it detects ``Expr`` arguments and builds trees, but
  passes plain ``Multivector`` arguments straight through to the numeric core.

This ``__init__`` re-exports the numeric API so users can write
``from ga import *`` and get everything they need for computation.
The symbolic layer is imported separately (``from ga.symbolic import sym, ...``)
because it's opt-in — most users only need it for notebooks and display.

Design Principles
-----------------
- **Named functions are the contract.** ``gp``, ``op``, ``grade``, ``reverse``
  never change meaning. Operators (``*``, ``^``, ``|``, ``~``) are sugar.
- **No ambiguity.** Every inner product variant has its own name. The ``|``
  operator maps to Hestenes inner, but ``left_contraction``,
  ``right_contraction``, and ``scalar_product`` are always available.
- **Aliases exist for convenience**, not as separate implementations.
  ``wedge`` is literally ``op``, ``rev`` is literally ``reverse``, etc.
"""

from ga.algebra import (
    Algebra,
    Multivector,
    # Core operations
    gp,
    op,
    left_contraction,
    right_contraction,
    hestenes_inner,
    scalar_product,
    commutator,
    anticommutator,
    # Unary
    reverse,
    involute,
    conjugate,
    grade,
    grades,
    scalar,
    dual,
    undual,
    complement,
    uncomplement,
    norm2,
    norm,
    unit,
    inverse,
    # Predicates
    is_scalar,
    is_vector,
    is_bivector,
    is_even,
    is_rotor,
    even_grades,
    odd_grades,
    squared,
    sandwich,
    sw,
    norm_squared,
    exp,
    log,
    project,
    reject,
    reflect,
    # Aliases
    geometric_product,
    wedge,
    outer_product,
    rev,
    normalize,
    normalise,
    ip,
    inner_product,
)

__all__ = [
    "Algebra",
    "Multivector",
    "gp",
    "op",
    "left_contraction",
    "right_contraction",
    "hestenes_inner",
    "scalar_product",
    "commutator",
    "anticommutator",
    "reverse",
    "involute",
    "conjugate",
    "grade",
    "grades",
    "scalar",
    "dual",
    "undual",
    "complement",
    "uncomplement",
    "norm2",
    "norm",
    "unit",
    "inverse",
    "is_scalar",
    "is_vector",
    "is_bivector",
    "is_even",
    "is_rotor",
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
    "ip",
    "inner_product",
]
