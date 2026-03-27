"""Tests for the LaTeX intermediate render tree."""

from ga.latex_nodes import Text, Seq, Frac, Sup, Parens, Command
from ga.latex_emit import emit
from ga.latex_rewrite import rewrite


# ── emit: Text ──

class TestEmitText:
    def test_plain(self):
        assert emit(Text("x")) == "x"

    def test_latex_command(self):
        assert emit(Text(r"\alpha")) == r"\alpha"

    def test_empty(self):
        assert emit(Text("")) == ""


# ── emit: Seq ──

class TestEmitSeq:
    def test_two_children(self):
        assert emit(Seq([Text("a"), Text("b")])) == "ab"

    def test_separator(self):
        assert emit(Seq([Text("a"), Text("b")], sep=" + ")) == "a + b"

    def test_three_children(self):
        assert emit(Seq([Text("a"), Text("b"), Text("c")], sep=", ")) == "a, b, c"

    def test_single_child(self):
        assert emit(Seq([Text("x")])) == "x"

    def test_empty(self):
        assert emit(Seq([])) == ""

    def test_nested(self):
        inner = Seq([Text("x"), Text("y")], sep=" ")
        assert emit(Seq([inner, Text("z")], sep="+")) == "x y+z"


# ── emit: Frac ──

class TestEmitFrac:
    def test_simple(self):
        assert emit(Frac(Text("a"), Text("b"))) == r"\frac{a}{b}"

    def test_small(self):
        assert emit(Frac(Text("a"), Text("b"), small=True)) == r"\tfrac{a}{b}"

    def test_nested_num(self):
        inner = Seq([Text("x"), Text("+"), Text("y")])
        assert emit(Frac(inner, Text("2"))) == r"\frac{x+y}{2}"


# ── emit: Sup ──

class TestEmitSup:
    def test_simple(self):
        assert emit(Sup(Text("e"), Text("x"))) == "e^{x}"

    def test_complex_base(self):
        base = Parens(Text("a+b"))
        assert emit(Sup(base, Text("2"))) == r"\left(a+b\right)^{2}"

    def test_complex_exp(self):
        exp = Seq([Text("-"), Text(r"\theta")])
        assert emit(Sup(Text("e"), exp)) == r"e^{-\theta}"


# ── emit: Parens ──

class TestEmitParens:
    def test_simple(self):
        assert emit(Parens(Text("x"))) == r"\left(x\right)"

    def test_nested(self):
        inner = Parens(Text("a"))
        assert emit(Parens(inner)) == r"\left(\left(a\right)\right)"


# ── emit: Command ──

class TestEmitCommand:
    def test_tilde(self):
        assert emit(Command(r"\tilde", Text("x"))) == r"\tilde{x}"

    def test_widetilde(self):
        assert emit(Command(r"\widetilde", Text("a+b"))) == r"\widetilde{a+b}"

    def test_hat(self):
        assert emit(Command(r"\hat", Text("v"))) == r"\hat{v}"

    def test_operatorname(self):
        assert emit(Command(r"\operatorname", Text("rev"))) == r"\operatorname{rev}"


# ── emit: deep nesting ──

class TestEmitDeepNesting:
    def test_frac_in_sup(self):
        """Before rewrite: frac inside sup."""
        f = Frac(Text(r"\theta"), Text("2"))
        s = Sup(Text("e"), f)
        assert emit(s) == r"e^{\frac{\theta}{2}}"

    def test_command_around_frac(self):
        f = Frac(Text("a"), Text("b"))
        c = Command(r"\widetilde", f)
        assert emit(c) == r"\widetilde{\frac{a}{b}}"


# ── rewrite: frac→tfrac in superscripts ──

class TestRewriteFracInSup:
    def test_frac_becomes_tfrac_in_sup(self):
        f = Frac(Text(r"\theta"), Text("2"))
        s = Sup(Text("e"), f)
        result = rewrite(s)
        assert emit(result) == r"e^{\tfrac{\theta}{2}}"

    def test_frac_outside_sup_unchanged(self):
        f = Frac(Text("a"), Text("b"))
        result = rewrite(f)
        assert emit(result) == r"\frac{a}{b}"

    def test_nested_frac_in_sup(self):
        """Frac inside a Seq inside a Sup."""
        f = Frac(Text(r"-\theta"), Text("2"))
        body = Seq([f, Text(" B")])
        s = Sup(Text("e"), body)
        result = rewrite(s)
        assert emit(result) == r"e^{\tfrac{-\theta}{2} B}"

    def test_frac_in_sup_in_frac_outer_unchanged(self):
        """Outer frac stays full-size, inner frac in sup becomes tfrac."""
        inner_frac = Frac(Text("a"), Text("2"))
        sup = Sup(Text("e"), inner_frac)
        outer_frac = Frac(sup, Text("b"))
        result = rewrite(outer_frac)
        # Outer frac: full-size. Inner frac in sup: tfrac.
        assert emit(result) == r"\frac{e^{\tfrac{a}{2}}}{b}"

    def test_already_small_unchanged(self):
        f = Frac(Text("a"), Text("b"), small=True)
        s = Sup(Text("e"), f)
        result = rewrite(s)
        assert emit(result) == r"e^{\tfrac{a}{b}}"

    def test_deeply_nested_sup(self):
        """Frac inside Parens inside Sup."""
        f = Frac(Text("x"), Text("y"))
        p = Parens(f)
        s = Sup(Text("e"), p)
        result = rewrite(s)
        assert emit(result) == r"e^{\left(\tfrac{x}{y}\right)}"

    def test_no_sup_no_change(self):
        """Complex tree with no Sup — nothing changes."""
        tree = Seq([
            Frac(Text("a"), Text("b")),
            Text(" + "),
            Command(r"\tilde", Text("x")),
        ])
        result = rewrite(tree)
        assert emit(result) == r"\frac{a}{b} + \tilde{x}"


# ── rewrite: idempotent ──

class TestRewriteIdempotent:
    def test_double_rewrite(self):
        f = Frac(Text(r"\theta"), Text("2"))
        s = Sup(Text("e"), f)
        r1 = rewrite(s)
        r2 = rewrite(r1)
        assert emit(r1) == emit(r2)
