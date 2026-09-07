"""Public RGA presentation contracts retaining all five historical test IDs.

Numeric kernels are independently covered in core/test_metric_rga.py; this
suite owns signed vocabulary, native versus display order, provenance, exact
notation, and facade mismatch errors. ADR-105 records the v1 differences.
"""

import numpy as np
import pytest

import galaga as ga
from galaga.expression import BladeLiteral, Call, evaluate, simplify

UNARY = (
    "metric_apply",
    "antimetric_apply",
    "bulk_part",
    "weight_part",
    "right_hodge_dual",
    "left_hodge_dual",
    "right_weight_dual",
    "left_weight_dual",
    "antireverse",
)
BINARY = (
    "metric_inner_product",
    "antidot_product",
    "geometric_antiproduct",
    "left_interior_product",
    "right_interior_product",
    "transwedge",
    "transwedge_antiproduct",
)


def test_rga_basis_metric_orientation_names_and_display_order():
    algebra = ga.Algebra(config=ga.p_rga())
    e1, e2, e3, e4 = algebra.basis_vectors()
    # Derive the values before looking up names or stored orientations.
    products = {
        "e23": e2 ^ e3,
        "e31": e3 ^ e1,
        "e12": e1 ^ e2,
        "e41": e4 ^ e1,
        "e42": e4 ^ e2,
        "e43": e4 ^ e3,
        "e423": e4 ^ e2 ^ e3,
        "e431": e4 ^ e3 ^ e1,
        "e412": e4 ^ e1 ^ e2,
        "e321": e3 ^ e2 ^ e1,
        "I": e1 ^ e2 ^ e3 ^ e4,
    }
    values = algebra.locals()
    assert algebra.signature == (1, 1, 1, 0)
    assert e4 * e4 == algebra.scalar(algebra.gram[3, 3]) == algebra.scalar(0)
    for name, actual in products.items():
        mask = np.flatnonzero(actual.data).item()
        ref = ga.BladeRef(mask, int(actual.data[mask]))
        assert algebra.blade_label(mask).ref == ref
        assert values[name] == actual
        assert algebra.blade(name) == algebra.blade(actual) == actual
    assert ga.complement(e1) == values["e423"]

    displayed = [str(algebra.blade(algebra.blade_label(mask).ref)) for mask in algebra.presentation.display_order.masks]
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
    # Enumeration is numeric, unlike v1's oriented presentation ordering.
    for grade in range(5):
        expected_masks = [mask for mask in range(16) if mask.bit_count() == grade]
        actual = tuple(algebra.basis_blades(grade))
        assert [np.flatnonzero(blade.data).item() for blade in actual] == expected_masks
        assert all(blade.data[mask] == 1 for mask, blade in zip(expected_masks, actual, strict=True))
    assert str(algebra.multivector(np.ones(16))) == (
        "1 + e₁ + e₂ + e₃ + e₄ + e₂₃ - e₃₁ + e₁₂ - e₄₁ - e₄₂ - e₄₃ + e₄₂₃ - e₄₃₁ + e₄₁₂ - e₃₂₁ + 𝟙"
    )


def test_rga_projective_roles_have_the_source_grades():
    algebra = ga.Algebra(config=ga.p_rga())
    values = algebra.locals()
    assert {name: values[name].homogeneous_grade() for name in ("e1", "e23", "e423", "I")} == {
        "e1": 1,
        "e23": 2,
        "e423": 3,
        "I": 4,
    }
    assert algebra.blade("projective") == values["e4"]
    assert algebra.blade("antiscalar") == values["I"] == algebra.I


def test_rga_operations_preserve_symbolic_trees_values_and_grades():
    algebra = ga.Algebra(config=ga.p_rga())
    e1, e2, _, _ = algebra.basis_vectors(expr=True)
    for name in (*UNARY, *BINARY):
        operation = getattr(ga, name)
        operands = (e1,) if name in UNARY else (e1, e2)
        parameters = (1,) if name.startswith("transwedge") else ()
        numeric_operands = tuple(algebra.multivector(value.data) for value in operands)
        expected = operation(*numeric_operands, *parameters)
        result = operation(*operands, *parameters)
        assert isinstance(result.expr, Call)
        assert result.expr.operation_id == name
        assert result.expr.operands == tuple(BladeLiteral(1 << index) for index in range(len(operands)))
        np.testing.assert_array_equal(result.data, expected.data)
        assert evaluate(result.expr, algebra=algebra) == result
        assert result.homogeneous_grade() == expected.homogeneous_grade()
        assert expected.expr is None
        if parameters:
            assert result.expr.parameters == (("order", 1),)
            assert simplify(result.expr).parameters == (("order", 1),)
            assert result.homogeneous_grade() is None  # Both old vector examples are zero.
            spec = ga.get_operation(name)
            assert spec.arity == 3 and spec.expression_arity == 2
            assert spec.parameters[0].name == "order"
        else:
            assert result.expr.parameters == ()


def test_lengyel_notation_rendering_snapshot():
    algebra = ga.Algebra(config=ga.p_rga(), display=ga.DisplayPolicy(content="expr"))
    e1, e2, _, _ = algebra.basis_vectors(expr=True)
    assert str(ga.geometric_product(e1, e2)) == "e₁ ⟑ e₂"
    assert str(ga.geometric_antiproduct(e1, e2)) == "e₁ ⟇ e₂"
    assert str(ga.metric_inner_product(e1, e2)) == "e₁ • e₂"
    assert str(ga.antidot_product(e1, e2)) == "e₁ ∘ e₂"
    assert str(ga.transwedge(e1, e2, 1)) == "e₁ ⩓₁ e₂"
    assert str(ga.transwedge_antiproduct(e1, e2, 1)) == "e₁ ⩔₁ e₂"
    assert str(ga.right_hodge_dual(e1)) == "e₁^★"
    assert str(ga.left_hodge_dual(e1)) == "e₁_★"
    assert str(ga.complement(e1)) == "e₁̅"
    assert str(ga.left_complement(e1)) == "e₁̲"
    assert str(ga.reverse(e1)) == "e₁̃"
    assert str(ga.conjugate(e1)) == "conjugate(e₁)"
    assert ga.geometric_product(e1, e2).latex() == r"\mathbf{e}_{1} \mathbin{\text{⟑}} \mathbf{e}_{2}"
    assert ga.complement(e1).latex() == r"\overline{\mathbf{e}_{1}}"
    assert ga.left_complement(e1).latex() == r"\underline{\mathbf{e}_{1}}"
    assert ga.right_hodge_dual(e1).latex() == r"\mathbf{e}_{1}^{\text{★}}"
    assert ga.antireverse(e1).latex() == r"\utilde{\mathbf{e}_{1}}"
    assert ga.antireverse(ga.antiwedge(ga.complement(e1), ga.complement(e2))).latex() == (
        r"\utilde{\overline{\mathbf{e}_{1}} \vee \overline{\mathbf{e}_{2}}}"
    )
    assert algebra.I.latex() == r"\text{𝟙}"

    fallback = ga.Notation.lengyel().with_rule(
        "antireverse", ga.RenderRule("underaccent", symbol=ga.Name("sim", "\u0330", r"\sim")), target="latex"
    )
    view = algebra.with_notation(fallback)
    fallback_e1, _, _, _ = view.basis_vectors(expr=True)
    assert ga.antireverse(fallback_e1).latex() == r"\underset{\sim}{\mathbf{e}_{1}}"
    assert ga.antireverse(e1).latex() == r"\utilde{\mathbf{e}_{1}}"
    assert view.numeric is algebra.numeric

    for name in (*UNARY, *BINARY):
        arguments = (e1,) if name in UNARY else ((e1, e2, 1) if name.startswith("transwedge") else (e1, e2))
        assert r"\unicode{" not in getattr(ga, name)(*arguments).latex()
    default = algebra.with_notation(ga.Notation.default())
    d1, d2, _, _ = default.basis_vectors(expr=True)
    assert str(ga.metric_inner_product(d1, d2)) == "metric_inner_product(e₁, e₂)"


@pytest.mark.parametrize("operation", BINARY)
def test_binary_rga_operations_reject_mixed_algebras(operation):
    for right_algebra in (ga.Algebra(3), ga.Algebra(signature=(1, -1))):
        left = ga.Algebra(2).basis_vectors(expr=True)[0]
        right = right_algebra.basis_vectors(expr=True)[0]
        arguments = (left, right, 0) if operation.startswith("transwedge") else (left, right)
        with pytest.raises(ValueError, match="different algebras"):
            getattr(ga, operation)(*arguments)
