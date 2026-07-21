"""Presentation and facade contracts for the RGA convention layer.

The source-derived metric, antimetric, product, duality, and transwedge
kernels live in ``core/test_metric_rga.py``. This suite owns semantic role
names, expression propagation, Lengyel notation, and facade mismatch errors.
"""

from __future__ import annotations

from functools import reduce

import numpy as np
import pytest

from galaga.legacy import (
    Algebra,
    Notation,
    antidot_product,
    antimetric_apply,
    antireverse,
    antiwedge,
    b_rga,
    bulk_part,
    complement,
    conjugate,
    geometric_antiproduct,
    gp,
    left_complement,
    left_hodge_dual,
    left_interior_product,
    left_weight_dual,
    metric_apply,
    metric_inner_product,
    op,
    reverse,
    right_hodge_dual,
    right_interior_product,
    right_weight_dual,
    transwedge,
    transwedge_antiproduct,
    weight_part,
)
from galaga.legacy.simplify import simplify
from galaga.notation import NotationRule
from galaga.ops import GA_OPS


def _wedge(vectors):
    return reduce(op, vectors)


def test_rga_basis_metric_orientation_names_and_display_order():
    """The RGA convention attaches source roles without changing wedge signs."""
    algebra = Algebra((1, 1, 1, 0), blades=b_rga())
    values = algebra.locals()
    e1, e2, e3, e4 = algebra.basis_vectors()
    factorizations = {
        "e23": (e2, e3),
        "e31": (e3, e1),
        "e12": (e1, e2),
        "e41": (e4, e1),
        "e42": (e4, e2),
        "e43": (e4, e3),
        "e423": (e4, e2, e3),
        "e431": (e4, e3, e1),
        "e412": (e4, e1, e2),
        "e321": (e3, e2, e1),
        "I": (e1, e2, e3, e4),
    }

    assert algebra.signature == (1, 1, 1, 0)
    assert gp(e4, e4) == algebra.scalar(0)
    for name, vectors in factorizations.items():
        assert values[name] == _wedge(vectors)
        assert algebra.blade(name) == algebra.blade(values[name])
    assert complement(e1) == values["e423"]

    displayed = [str(blade) for grade in range(algebra.n + 1) for blade in algebra.basis_blades(grade)]
    assert displayed == [
        "1",
        "e₁",
        "e₂",
        "e₃",
        "e₄",
        "e₂₃",
        "e₃₁",
        "e₁₂",
        "e₄₁",
        "e₄₂",
        "e₄₃",
        "e₄₂₃",
        "e₄₃₁",
        "e₄₁₂",
        "e₃₂₁",
        "𝟙",
    ]


def test_rga_projective_roles_have_the_source_grades():
    """Point, line, plane, and pseudoscalar local roles remain discoverable."""
    algebra = Algebra((1, 1, 1, 0), blades=b_rga())
    values = algebra.locals()

    assert {name: values[name].homogeneous_grade() for name in ("e1", "e23", "e423", "I")} == {
        "e1": 1,
        "e23": 2,
        "e423": 3,
        "I": 4,
    }


def test_rga_operations_preserve_symbolic_trees_values_and_grades():
    """Every convention-layer operation follows Galaga's symbolic contract."""
    algebra = Algebra((1, 1, 1, 0), blades=b_rga(), notation=Notation.lengyel())
    e1, e2, _, _ = algebra.basis_vectors(symbolic=True)
    numeric_e1, numeric_e2 = e1.eval(), e2.eval()
    unary = (
        metric_apply,
        antimetric_apply,
        bulk_part,
        weight_part,
        right_hodge_dual,
        left_hodge_dual,
        right_weight_dual,
        left_weight_dual,
        antireverse,
    )
    binary = (
        metric_inner_product,
        antidot_product,
        geometric_antiproduct,
        left_interior_product,
        right_interior_product,
    )

    for operation in unary:
        result = operation(e1)
        assert result._is_symbolic
        assert np.allclose(result.data, operation(numeric_e1).data)
        assert np.allclose(result._expr.eval().data, result.data)
    for operation in binary:
        result = operation(e1, e2)
        assert result._is_symbolic
        assert np.allclose(result.data, operation(numeric_e1, numeric_e2).data)
        assert np.allclose(result._expr.eval().data, result.data)
    for operation in (transwedge, transwedge_antiproduct):
        result = operation(e1, e2, 1)
        assert result._is_symbolic
        assert result._grade is not None
        assert np.allclose(result.data, operation(numeric_e1, numeric_e2, 1).data)
        assert np.allclose(result._expr.eval().data, result.data)
        assert simplify(result._expr).k == 1

    assert GA_OPS["transwedge"].arity == 3
    assert GA_OPS["transwedge_antiproduct"].arity == 3


def test_lengyel_notation_rendering_snapshot():
    """The preset renders KaTeX-safe RGA symbols without changing semantics."""
    algebra = Algebra((1, 1, 1, 0), blades=b_rga(), notation=Notation.lengyel())
    e1, e2, _, _ = algebra.basis_vectors(symbolic=True)

    assert str(gp(e1, e2)) == "e₁ ⟑ e₂"
    assert str(geometric_antiproduct(e1, e2)) == "e₁ ⟇ e₂"
    assert str(metric_inner_product(e1, e2)) == "e₁ • e₂"
    assert str(antidot_product(e1, e2)) == "e₁ ∘ e₂"
    assert str(transwedge(e1, e2, 1)) == "e₁ ⩓₁ e₂"
    assert str(transwedge_antiproduct(e1, e2, 1)) == "e₁ ⩔₁ e₂"
    assert str(right_hodge_dual(e1)) == "e₁^★"
    assert str(left_hodge_dual(e1)) == "e₁_★"
    assert str(complement(e1)) == "e₁̅"
    assert str(left_complement(e1)) == "e₁̲"
    assert str(reverse(e1)) == "e₁̃"
    assert str(conjugate(e1)) == "conjugate(e₁)"
    assert gp(e1, e2).latex() == r"\mathbf{e}_{1} \mathbin{\text{⟑}} \mathbf{e}_{2}"
    assert complement(e1).latex() == r"\overline{\vphantom{Aft^6}\mathbf{e}_{1}}"
    assert left_complement(e1).latex() == r"\underline{\vphantom{gy_7}\mathbf{e}_{1}}"
    assert right_hodge_dual(e1).latex() == r"\mathbf{e}_{1}^{\text{★}}"
    assert antireverse(e1).latex() == r"\utilde{\mathbf{e}_{1}}"
    assert antireverse(antiwedge(complement(e1), complement(e2))).latex() == (
        r"\utilde{\overline{\vphantom{Aft^6}\mathbf{e}_{1}} \vee "
        r"\overline{\vphantom{Aft^6}\mathbf{e}_{2}}}"
    )
    assert algebra.I.latex() == r"\text{𝟙}"

    fallback_notation = Notation.lengyel()
    fallback_notation.set("Antireverse", "latex", NotationRule(kind="underaccent", symbol=r"\sim"))
    fallback_algebra = Algebra((1, 1, 1, 0), blades=b_rga(), notation=fallback_notation)
    fallback_e1, _, _, _ = fallback_algebra.basis_vectors(symbolic=True)
    assert antireverse(fallback_e1).latex() == r"\underset{\sim}{\mathbf{e}_{1}}"

    katex_rendered = (
        gp(e1, e2),
        geometric_antiproduct(e1, e2),
        metric_inner_product(e1, e2),
        antidot_product(e1, e2),
        left_interior_product(e1, e2),
        right_interior_product(e1, e2),
        transwedge(e1, e2, 1),
        transwedge_antiproduct(e1, e2, 1),
        right_hodge_dual(e1),
        left_hodge_dual(e1),
        right_weight_dual(e1),
        left_weight_dual(e1),
        bulk_part(e1),
        weight_part(e1),
        antireverse(e1),
    )
    assert all(r"\unicode{" not in value.latex() for value in katex_rendered)

    default_algebra = Algebra((1, 1, 1, 0), blades=b_rga())
    d1, d2, _, _ = default_algebra.basis_vectors(symbolic=True)
    assert str(metric_inner_product(d1, d2)) == "metric_inner_product(e₁, e₂)"


@pytest.mark.parametrize(
    "operation",
    (
        metric_inner_product,
        antidot_product,
        geometric_antiproduct,
        left_interior_product,
        right_interior_product,
        transwedge,
        transwedge_antiproduct,
    ),
)
def test_binary_rga_operations_reject_mixed_algebras(operation):
    left = Algebra(2).basis_vectors()[0]
    right = Algebra(3).basis_vectors()[0]
    arguments = (left, right, 0) if operation in (transwedge, transwedge_antiproduct) else (left, right)

    with pytest.raises(ValueError, match="different algebras"):
        operation(*arguments)
