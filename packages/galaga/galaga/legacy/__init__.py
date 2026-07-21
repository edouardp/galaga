"""Explicit Galaga 1 compatibility namespace for the Phase 8 cutover.

The ordinary :mod:`galaga` namespace exposes the Galaga 2 core-backed facade.
This module preserves the previous top-level API as a coherent, deliberately
selected test oracle and migration aid.  It is temporary and is scheduled for
removal with the legacy engine in Phase 9.

Values from this namespace must be used with operations from this namespace;
Galaga 1 and Galaga 2 multivectors are intentionally distinct value types.
"""

from __future__ import annotations

from .. import algebra as _algebra
from ..basis_blade import BasisBlade
from ..blade_convention import (
    BladeConvention,
    b_cga,
    b_complex,
    b_default,
    b_gamma,
    b_pga,
    b_quaternion,
    b_rga,
    b_sigma,
    b_sigma_xyz,
    b_sta,
)
from ..expr import sym
from ..notation import Notation
from .simplify import simplify

_ALGEBRA_EXPORTS = (
    "Algebra",
    "Multivector",
    "anticommutator",
    "antidot_product",
    "antimetric_apply",
    "antireverse",
    "antiwedge",
    "bulk_part",
    "commutator",
    "complement",
    "conjugate",
    "doran_lasenby_inner",
    "dorst_inner",
    "dual",
    "even_grades",
    "exp",
    "geometric_antiproduct",
    "geometric_product",
    "gp",
    "grade",
    "grade_involution",
    "grades",
    "hestenes_inner",
    "inner_product",
    "inverse",
    "involute",
    "ip",
    "is_basis_blade",
    "is_bivector",
    "is_even",
    "is_rotor",
    "is_scalar",
    "is_vector",
    "join",
    "jordan_product",
    "left_complement",
    "left_contraction",
    "left_hodge_dual",
    "left_interior_product",
    "left_weight_dual",
    "lie_bracket",
    "log",
    "mag2",
    "magnitude_squared",
    "meet",
    "metric_apply",
    "metric_inner_product",
    "metric_regressive_product",
    "norm",
    "norm2",
    "norm_squared",
    "normalise",
    "normalize",
    "odd_grades",
    "op",
    "outer_product",
    "outercos",
    "outerexp",
    "outersin",
    "outertan",
    "project",
    "reflect",
    "regressive_product",
    "reject",
    "rev",
    "reverse",
    "right_complement",
    "right_contraction",
    "right_hodge_dual",
    "right_interior_product",
    "right_weight_dual",
    "sandwich",
    "scalar_product",
    "scalar_sqrt",
    "sqrt",
    "squared",
    "sw",
    "transwedge",
    "transwedge_antiproduct",
    "uncomplement",
    "undual",
    "unit",
    "wedge",
    "weight_part",
)

for _name in _ALGEBRA_EXPORTS:
    globals()[_name] = getattr(_algebra, _name)

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
    "b_rga",
    "b_sigma",
    "b_sigma_xyz",
    "b_sta",
    "simplify",
    "sym",
    *[name for name in _ALGEBRA_EXPORTS if name not in {"Algebra", "Multivector"}],
]

del _name
