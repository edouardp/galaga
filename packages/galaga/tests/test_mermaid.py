"""Tests for mermaid expression tree diagram generation."""

from galaga import Algebra
from galaga.expr import Scalar
from galaga.mermaid import expr_to_mermaid, mv_to_mermaid


def _alg():
    return Algebra(3)


class TestExprToMermaid:
    def test_sym_leaf(self):
        alg = _alg()
        v = alg.vector([1, 0, 0])
        v.name("v")
        result = expr_to_mermaid(v._to_expr())
        assert "graph TD" in result
        assert "Sym: v" in result

    def test_scalar_leaf(self):
        result = expr_to_mermaid(Scalar(3))
        assert "Scalar: 3" in result

    def test_binary_gp(self):
        alg = _alg()
        a = alg.vector([1, 0, 0])
        a.name("a")
        b = alg.vector([0, 1, 0])
        b.name("b")
        from galaga import gp

        c = gp(a, b)
        result = expr_to_mermaid(c._to_expr())
        assert "Gp" in result
        assert "Sym: a" in result
        assert "Sym: b" in result
        assert "-->" in result

    def test_unary_neg(self):
        alg = _alg()
        v = alg.vector([1, 0, 0])
        v.name("v")
        result = expr_to_mermaid((-v)._to_expr())
        assert "Neg" in result
        assert "Sym: v" in result

    def test_scalar_mul(self):
        alg = _alg()
        v = alg.vector([1, 0, 0])
        v.name("v")
        result = expr_to_mermaid((2 * v)._to_expr())
        assert "ScalarMul: k=2" in result

    def test_scalar_div(self):
        alg = _alg()
        v = alg.vector([1, 0, 0])
        v.name("v")
        result = expr_to_mermaid((v / 3)._to_expr())
        assert "ScalarDiv: k=3" in result

    def test_show_values(self):
        alg = _alg()
        v = alg.vector([1, 2, 3])
        v.name("v")
        result = expr_to_mermaid(v._to_expr(), show_values=True)
        assert "= " in result

    def test_no_values(self):
        alg = _alg()
        v = alg.vector([1, 0, 0])
        v.name("v")
        result = expr_to_mermaid(v._to_expr(), show_values=False)
        assert "\\n= " not in result

    def test_direction(self):
        result = expr_to_mermaid(Scalar(1), direction="LR")
        assert "graph LR" in result

    def test_compound_tree(self):
        """A + (b * c) should produce a tree with Add at root, edges to children."""
        alg = _alg()
        a = alg.vector([1, 0, 0])
        a.name("a")
        b = alg.vector([0, 1, 0])
        b.name("b")
        c = alg.vector([0, 0, 1])
        c.name("c")
        from galaga import gp

        expr = (a + gp(b, c))._to_expr()
        result = expr_to_mermaid(expr)
        assert "Add" in result
        assert "Gp" in result
        assert result.count("-->") >= 3  # Add->a, Add->Gp, Gp->b, Gp->c


class TestMvToMermaid:
    def test_named_mv(self):
        alg = _alg()
        v = alg.vector([1, 2, 3])
        v.name("v")
        result = mv_to_mermaid(v)
        assert "Sym: v" in result

    def test_lazy_expression(self):
        alg = _alg()
        a = alg.vector([1, 0, 0])
        a.name("a")
        b = alg.vector([0, 1, 0])
        b.name("b")
        from galaga import gp

        c = gp(a, b)
        result = mv_to_mermaid(c)
        assert "Gp" in result
        assert "-->" in result
