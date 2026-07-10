"""Tests for MatrixRepr symbolic naming and expression trees."""

import numpy as np
import pytest
from galaga_matrix import MatrixRepr, from_matrix, to_matrix, to_spinor_column
from galaga_matrix.expr import (
    Adjoint,
    MatMul,
    MatrixRepresentation,
    SpinorColumnRepresentation,
)

from galaga import Algebra


def test_matrix_constructor_rejects_label_keyword():
    with pytest.raises(TypeError):
        MatrixRepr(np.eye(2), label=r"\sigma_1")


def test_matrix_has_no_label_property():
    matrix = MatrixRepr(np.eye(2))

    assert not hasattr(matrix, "label")


def test_matrix_name_sets_symbolic_state():
    matrix = MatrixRepr(np.eye(2)).name(latex=r"\sigma_1")

    assert matrix._name_latex == r"\sigma_1"
    assert matrix._is_symbolic
    assert matrix.expr is not None
    assert r"\sigma_1 \quad = \quad" in matrix.latex()
    assert r"\sigma_1 =" not in matrix.latex()


def test_matrix_copy_as_is_non_mutating():
    matrix = MatrixRepr(np.eye(2)).name("A")

    renamed = matrix.copy_as("B")

    assert matrix._name_latex == "A"
    assert renamed._name_latex == "B"
    assert np.allclose(renamed.mat, matrix.mat)


def test_named_matrix_matmul_builds_expr_and_preserves_value():
    A = MatrixRepr(np.array([[1, 2], [3, 4]], dtype=complex)).name("A")
    B = MatrixRepr(np.array([[0, 1], [-1, 0]], dtype=complex)).name("B")

    C = A @ B

    assert isinstance(C.expr, MatMul)
    assert np.allclose(C.mat, A.mat @ B.mat)
    assert C.expr.latex() == "A B"


def test_named_matrix_elementwise_mul_builds_distinct_node():
    A = MatrixRepr(np.array([[1, 2], [3, 4]], dtype=complex)).name("A")
    B = MatrixRepr(np.array([[4, 3], [2, 1]], dtype=complex)).name("B")

    C = A * B

    assert type(C.expr).__name__ == "MatrixElementwiseMul"
    assert np.allclose(C.mat, A.mat * B.mat)
    assert r"\odot" in C.expr.latex()


def test_matrix_expr_parenthesizes_add_before_matmul():
    A = MatrixRepr(np.eye(2, dtype=complex)).name("A")
    B = MatrixRepr(np.eye(2, dtype=complex)).name("B")
    C = MatrixRepr(np.eye(2, dtype=complex)).name("C")

    expr = ((A + B) @ C).expr

    assert expr.latex() == "(A + B) C"


def test_matrix_display_renders_name_expr_and_matrix_value():
    A = MatrixRepr(np.eye(2, dtype=complex)).name("A")
    B = MatrixRepr(np.eye(2, dtype=complex)).name("B")

    display = (A @ B).name("C").display(compact=True).latex()

    assert "C = A B = " in display
    assert r"\begin{pmatrix}" in display


def test_symbolic_adjoint_flips_ket_bra_and_builds_expr():
    ket = MatrixRepr(np.array([[1], [0]], dtype=complex), kind="ket").name(latex=r"\left|\psi\right\rangle")

    bra = ket.H

    assert bra.kind == "bra"
    assert isinstance(bra.expr, Adjoint)
    assert bra.expr.latex() == r"\left\langle \psi\right|"


def test_symbolic_bra_at_ket_returns_complex_scalar():
    ket = MatrixRepr(np.array([[1], [0]], dtype=complex), kind="ket").name(latex=r"\left|\psi\right\rangle")
    bra = ket.H

    result = bra @ ket

    assert np.isclose(result, 1)


def test_to_matrix_named_mv_uses_name_not_label():
    alg = Algebra(3)
    e1, e2, _ = alg.basis_vectors()
    blade = (e1 * e2).name("B")

    matrix = to_matrix(blade, mode="compact")

    assert not hasattr(matrix, "label")
    assert matrix._name_latex == r"\rho(B)"
    assert isinstance(matrix.expr, MatrixRepresentation)
    assert matrix.expr.latex() == r"\rho(B)"


def test_to_matrix_unnamed_symbolic_mv_preserves_expression_for_display_repr():
    alg = Algebra(1, 3, display_repr=True)
    g0, g1, g2, g3 = alg.basis_vectors(symbolic=True)
    a = (2 * g0 + g1).name(latex="a")
    b = (g2 - 3 * g3).name(latex="b")

    matrix = to_matrix(a * b, mode="compact")

    assert matrix._name_latex is None
    assert isinstance(matrix.expr, MatrixRepresentation)
    assert matrix.expr.latex() == r"\rho(a b)"
    assert r"\rho(None)" not in matrix.latex()
    assert r"\rho(a b) \quad = \quad \begin{pmatrix}" in matrix.latex()


def test_matrix_direct_latex_uses_display_when_algebra_display_repr_is_enabled():
    alg = Algebra(1, 3, display_repr=True)
    g0, g1, g2, g3 = alg.basis_vectors(symbolic=True)
    a = (2 * g0 + g1).name(latex="a")
    b = (g2 - 3 * g3).name(latex="b")

    product = to_matrix(a, mode="compact") @ to_matrix(b, mode="compact")

    assert product._name_latex is None
    assert product.expr.latex() == r"\rho(a) \rho(b)"
    assert r"\rho(a) \rho(b) \quad = \quad \begin{pmatrix}" in product.latex()


def test_named_matrix_direct_latex_in_display_repr_shows_name_expr_and_value():
    alg = Algebra(1, 3, display_repr=True)
    g0, g1, _, _ = alg.basis_vectors(symbolic=True)
    a = (2 * g0 + g1).name(latex="a")

    matrix = to_matrix(a, mode="compact")

    assert r"\rho(a) \quad = \quad \begin{pmatrix}" in matrix.latex()
    assert r"\rho_D" not in matrix.latex()


def test_matrix_representation_latex_marks_non_default_bases():
    alg = Algebra(1, 3)
    g0 = alg.basis_vectors()[0].name(latex=r"\gamma_0")

    matrix = to_matrix(g0, mode="compact")
    weyl = MatrixRepresentation(g0._to_expr(), mode="compact", basis="weyl", value=matrix)
    majorana = MatrixRepresentation(g0._to_expr(), mode="compact", basis="majorana", value=matrix)

    assert matrix.expr.latex() == r"\rho(\gamma_0)"
    assert weyl.latex() == r"\rho^{\mathrm{Weyl}}(\gamma_0)"
    assert majorana.latex() == r"\rho^{\mathrm{Majorana}}(\gamma_0)"


def test_quaternion_matrix_representation_uses_quaternion_rho():
    alg = Algebra(1, 3)
    g0 = alg.basis_vectors()[0].name(latex=r"\gamma_0")

    matrix = to_matrix(g0, mode="quaternion")

    assert matrix._name_latex == r"\rho_{\mathbb{H}}(\gamma_0)"
    assert matrix.expr.latex() == r"\rho_{\mathbb{H}}(\gamma_0)"


def test_auto_matrix_basis_change_renders_basis_marked_rho():
    alg = Algebra(1, 3)
    g0 = alg.basis_vectors()[0].name(latex=r"\gamma_0")

    weyl = to_matrix(g0, mode="compact").to_basis("weyl")
    majorana = to_matrix(g0, mode="compact").to_basis("majorana")

    assert weyl.expr.latex() == r"\rho^{\mathrm{Weyl}}(\gamma_0)"
    assert majorana.expr.latex() == r"\rho^{\mathrm{Majorana}}(\gamma_0)"


def test_manual_matrix_name_basis_change_preserves_manual_name():
    alg = Algebra(1, 3)
    g0 = alg.basis_vectors()[0].name(latex=r"\gamma_0")

    matrix = to_matrix(g0, mode="compact").copy_as("M")
    weyl = matrix.to_basis("weyl")

    assert weyl.expr.latex() == r"M^{(\mathrm{Weyl})}"


def test_from_matrix_named_matrix_uses_name_not_label():
    alg = Algebra(3)
    matrix = MatrixRepr(np.array([[0, 1], [1, 0]], dtype=complex), algebra=alg, mode="compact").name(latex=r"\sigma_1")

    mv = from_matrix(alg, matrix)

    assert mv._name_latex == r"\rho^{-1}(\sigma_1)"


def test_to_spinor_column_named_mv_uses_name_not_label():
    alg = Algebra(3)
    rotor = alg.scalar(1.0).name(latex=r"\psi")

    ket = to_spinor_column(rotor)

    assert not hasattr(ket, "label")
    assert ket._name_latex == r"\left|\rho(\psi)\right\rangle"
    assert isinstance(ket.expr, SpinorColumnRepresentation)
