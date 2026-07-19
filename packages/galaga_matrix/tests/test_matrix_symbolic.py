"""Tests for MatrixRepr symbolic naming and expression trees."""

import asyncio
from dataclasses import FrozenInstanceError
from pathlib import Path

import numpy as np
import pytest
from galaga_matrix import MatrixRepr, from_matrix, to_matrix, to_spinor_column
from galaga_matrix.expr import (
    Adjoint,
    Expr,
    MatMul,
    MatrixRepresentation,
    SpinorColumnRepresentation,
    multivector_operand,
)

from galaga.facade import Algebra
from galaga.presentation import DisplayPolicy, Notation


def test_matrix_constructor_rejects_label_keyword():
    with pytest.raises(TypeError):
        MatrixRepr(np.eye(2), label=r"\sigma_1")


def test_matrix_has_no_label_property():
    matrix = MatrixRepr(np.eye(2))

    assert not hasattr(matrix, "label")


def test_matrix_name_sets_symbolic_state():
    matrix = MatrixRepr(np.eye(2)).name(latex=r"\sigma_1")

    assert matrix.symbolic_name is not None
    assert matrix.symbolic_name.latex == r"\sigma_1"
    assert matrix.is_symbolic
    assert matrix.expr is not None
    assert r"\sigma_1 \quad = \quad" in matrix.latex()
    assert r"\sigma_1 =" not in matrix.latex()


def test_matrix_copy_as_is_non_mutating():
    matrix = MatrixRepr(np.eye(2)).name("A")

    renamed = matrix.copy_as("B")

    assert matrix.symbolic_name is not None
    assert renamed.symbolic_name is not None
    assert matrix.symbolic_name.latex == "A"
    assert renamed.symbolic_name.latex == "B"
    assert np.allclose(renamed.mat, matrix.mat)


def test_named_matrix_matmul_builds_expr_and_preserves_value():
    A = MatrixRepr(np.array([[1, 2], [3, 4]], dtype=complex)).name("A")
    B = MatrixRepr(np.array([[0, 1], [-1, 0]], dtype=complex)).name("B")

    C = A @ B

    assert isinstance(C.expr, MatMul)
    assert np.allclose(C.mat, A.mat @ B.mat)
    assert np.allclose(C.expr.eval(), C.mat)
    assert C.expr.latex() == "A B"


@pytest.mark.parametrize(
    "operation",
    (
        lambda A, B: A + B,
        lambda A, B: A - B,
        lambda A, B: -A,
        lambda A, B: 2 * A,
        lambda A, B: A / 2,
        lambda A, B: A * B,
        lambda A, B: A @ B,
        lambda A, B: A.T,
        lambda A, B: A.H,
        lambda A, B: A.conj(),
        lambda A, B: A.inv(),
        lambda A, B: A.kron(B),
    ),
)
def test_matrix_expression_evaluation_matches_every_supported_eager_operation(operation):
    A = MatrixRepr(np.array([[2, 1j], [-1j, 1]], dtype=complex)).name("A")
    B = MatrixRepr(np.array([[0, 2], [3, 1]], dtype=complex)).name("B")

    result = operation(A, B)

    assert result.expr is not None
    np.testing.assert_allclose(result.expr.eval(), result.mat)


def test_matrix_expression_nodes_and_leaf_snapshots_are_immutable():
    A = MatrixRepr(np.eye(2, dtype=complex)).name("A")
    expression = (A @ A).expr

    assert isinstance(expression, MatMul)
    assert isinstance(expression, Expr)
    with pytest.raises(FrozenInstanceError):
        expression.a = expression.b
    with pytest.raises(ValueError, match="read-only"):
        expression.a.value[0, 0] = 2


def test_matrix_expression_implementation_is_owned_by_galaga_matrix():
    expression = (MatrixRepr(np.eye(2)).name("A") + MatrixRepr(np.eye(2)).name("B")).expr

    assert expression is not None
    assert type(expression).__module__ == "galaga_matrix.expr"
    package = Path(__file__).parents[1] / "galaga_matrix"
    assert all("galaga.symbolic_core" not in source.read_text() for source in package.glob("*.py"))


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
    e1, e2, _ = alg.basis_vectors(expr=True)
    blade = (e1 * e2).named("B")

    matrix = to_matrix(blade, mode="compact")

    assert not hasattr(matrix, "label")
    assert matrix.symbolic_name is not None
    assert matrix.symbolic_name.latex == r"\rho(B)"
    assert isinstance(matrix.expr, MatrixRepresentation)
    assert matrix.expr.latex() == r"\rho(B)"


def test_to_matrix_unnamed_symbolic_mv_preserves_expression_for_display_repr():
    alg = Algebra(1, 3).with_display(DisplayPolicy(content="full", target="latex"))
    g0, g1, g2, g3 = alg.basis_vectors(expr=True)
    a = (2 * g0 + g1).named("a")
    b = (g2 - 3 * g3).named("b")

    matrix = to_matrix(a * b, mode="compact")

    assert matrix.symbolic_name is None
    assert isinstance(matrix.expr, MatrixRepresentation)
    assert matrix.expr.latex() == r"\rho(a b)"
    assert r"\rho(None)" not in matrix.latex()
    assert r"\rho(a b) \quad = \quad \begin{pmatrix}" in matrix.latex()


def test_matrix_adapter_honors_context_local_facade_notation_at_render_time():
    alg = Algebra(2)
    e1, e2 = alg.basis_vectors(expr=True)
    value = e1.named("x") * e2.named("y")
    matrix = to_matrix(value, mode="compact")
    functional = alg.default_presentation.with_notation(Notation.functional())

    assert matrix.expr is not None
    assert "geometric_product" not in matrix.expr.render("ascii")
    with alg.use_presentation(functional):
        assert matrix.expr.render("ascii") == "ρ(geometric_product(x, y))"
    assert "geometric_product" not in matrix.expr.render("ascii")


def test_matrix_adapter_presentation_is_isolated_between_async_tasks():
    alg = Algebra(2)
    e1, e2 = alg.basis_vectors(expr=True)
    matrix = to_matrix(e1.named("x") * e2.named("y"), mode="compact")
    assert matrix.expr is not None

    async def worker(notation: Notation) -> str:
        presentation = alg.default_presentation.with_notation(notation)
        with alg.use_presentation(presentation):
            await asyncio.sleep(0)
            return matrix.expr.render("ascii")

    async def run_workers() -> list[str]:
        return await asyncio.gather(
            worker(Notation.functional()),
            worker(Notation.functional(short=True)),
        )

    assert asyncio.run(run_workers()) == [
        "ρ(geometric_product(x, y))",
        "ρ(gp(x, y))",
    ]
    assert matrix.expr.render("ascii") == "ρ(xy)"


def test_matrix_direct_latex_uses_display_when_algebra_display_repr_is_enabled():
    alg = Algebra(1, 3).with_display(DisplayPolicy(content="full", target="latex"))
    g0, g1, g2, g3 = alg.basis_vectors(expr=True)
    a = (2 * g0 + g1).named("a")
    b = (g2 - 3 * g3).named("b")

    product = to_matrix(a, mode="compact") @ to_matrix(b, mode="compact")

    assert product.symbolic_name is None
    assert product.expr.latex() == r"\rho(a) \rho(b)"
    assert r"\rho(a) \rho(b) \quad = \quad \begin{pmatrix}" in product.latex()


def test_named_matrix_direct_latex_in_display_repr_shows_name_expr_and_value():
    alg = Algebra(1, 3).with_display(DisplayPolicy(content="full", target="latex"))
    g0, g1, _, _ = alg.basis_vectors(expr=True)
    a = (2 * g0 + g1).named("a")

    matrix = to_matrix(a, mode="compact")

    assert r"\rho(a) \quad = \quad \begin{pmatrix}" in matrix.latex()
    assert r"\rho_D" not in matrix.latex()


def test_matrix_representation_latex_marks_non_default_bases():
    alg = Algebra(1, 3)
    g0 = alg.basis_vectors(expr=True)[0].named("g0", latex=r"\gamma_0")

    matrix = to_matrix(g0, mode="compact")
    operand = multivector_operand(g0)
    assert operand is not None
    weyl = MatrixRepresentation(operand, mode="compact", basis="weyl", value=matrix)
    majorana = MatrixRepresentation(operand, mode="compact", basis="majorana", value=matrix)

    assert matrix.expr.latex() == r"\rho(\gamma_0)"
    np.testing.assert_allclose(matrix.expr.eval(), matrix.mat)
    assert weyl.latex() == r"\rho^{\mathrm{Weyl}}(\gamma_0)"
    assert majorana.latex() == r"\rho^{\mathrm{Majorana}}(\gamma_0)"


def test_quaternion_matrix_representation_uses_quaternion_rho():
    alg = Algebra(1, 3)
    g0 = alg.basis_vectors(expr=True)[0].named("g0", latex=r"\gamma_0")

    matrix = to_matrix(g0, mode="quaternion")

    assert matrix.symbolic_name is not None
    assert matrix.symbolic_name.latex == r"\rho_{\mathbb{H}}(\gamma_0)"
    assert matrix.expr.latex() == r"\rho_{\mathbb{H}}(\gamma_0)"


def test_auto_matrix_basis_change_renders_basis_marked_rho():
    alg = Algebra(1, 3)
    g0 = alg.basis_vectors(expr=True)[0].named("g0", latex=r"\gamma_0")

    weyl = to_matrix(g0, mode="compact").to_basis("weyl")
    majorana = to_matrix(g0, mode="compact").to_basis("majorana")

    assert weyl.expr.latex() == r"\rho^{\mathrm{Weyl}}(\gamma_0)"
    assert majorana.expr.latex() == r"\rho^{\mathrm{Majorana}}(\gamma_0)"
    np.testing.assert_allclose(weyl.expr.eval(), weyl.mat)
    np.testing.assert_allclose(majorana.expr.eval(), majorana.mat)


def test_manual_matrix_name_basis_change_preserves_manual_name():
    alg = Algebra(1, 3)
    g0 = alg.basis_vectors(expr=True)[0].named("g0", latex=r"\gamma_0")

    matrix = to_matrix(g0, mode="compact").copy_as("M")
    weyl = matrix.to_basis("weyl")

    assert weyl.expr.latex() == r"M^{(\mathrm{Weyl})}"


def test_from_matrix_named_matrix_uses_name_not_label():
    alg = Algebra(3)
    matrix = MatrixRepr(np.array([[0, 1], [1, 0]], dtype=complex), algebra=alg, mode="compact").name(latex=r"\sigma_1")

    mv = from_matrix(alg, matrix)

    assert mv.name is not None
    assert mv.name.latex == r"\rho^{-1}(\sigma_1)"


def test_to_spinor_column_named_mv_uses_name_not_label():
    alg = Algebra(3)
    rotor = alg.scalar(1.0).named("psi", latex=r"\psi")

    ket = to_spinor_column(rotor)

    assert not hasattr(ket, "label")
    assert ket.symbolic_name is not None
    assert ket.symbolic_name.latex == r"\left|\rho(\psi)\right\rangle"
    assert isinstance(ket.expr, SpinorColumnRepresentation)
    np.testing.assert_allclose(ket.expr.eval(), ket.mat)
