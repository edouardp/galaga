"""Tests for shared symbolic naming and expression helpers."""

import pytest

from galaga.symbolic_core import Add, Scalar, ScalarDiv, ScalarMul, Sym, normalize_name
from galaga.symbolic_core.domain import SymbolicDomain
from galaga.symbolic_core.expr import Expr


class ToyMul(Expr):
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def eval(self):
        return self.a.eval() * self.b.eval()


def test_normalize_name_matches_multivector_label_style():
    parts = normalize_name("  v  ")

    assert parts.ascii == "v"
    assert parts.unicode == "v"
    assert parts.latex == "v"


def test_normalize_name_latex_derives_greek_unicode_ascii():
    parts = normalize_name(latex=r"\theta")

    assert parts.ascii == "theta"
    assert parts.unicode == "θ"
    assert parts.latex == r"\theta"


def test_normalize_name_latex_derives_mathbf_unicode_ascii():
    parts = normalize_name(latex=r"\mathbf{v}")

    assert parts.ascii == "v"
    assert parts.unicode == "𝐯"
    assert parts.latex == r"\mathbf{v}"


def test_normalize_name_unknown_latex_falls_back():
    parts = normalize_name(latex=r"\weirdthing")

    assert parts.ascii == r"\weirdthing"
    assert parts.unicode == r"\weirdthing"
    assert parts.latex == r"\weirdthing"


def test_normalize_name_requires_label_or_latex():
    with pytest.raises(ValueError, match="At least one"):
        normalize_name()


def test_explicit_unicode_ascii_override_derived_values():
    parts = normalize_name(latex=r"\theta", unicode="theta-u", ascii="theta-a")

    assert parts.ascii == "theta-a"
    assert parts.unicode == "theta-u"
    assert parts.latex == r"\theta"


def test_sym_keeps_compatibility_attributes():
    sym = Sym(3, "α", name_latex=r"\alpha", name_ascii="alpha")

    assert sym._value == 3
    assert sym._mv == 3
    assert sym._name == "α"
    assert sym._name_latex == r"\alpha"
    assert sym._name_ascii == "alpha"
    assert sym.eval() == 3


def test_scalar_keeps_value_attribute():
    scalar = Scalar(2)

    assert scalar._value == 2
    assert scalar.eval() == 2


def test_structural_add_scalar_mul_and_scalar_div_eval():
    x = Sym(4, "x")

    assert isinstance(x + 2, Add)
    assert (x + 2).eval() == 6
    assert isinstance(3 * x, ScalarMul)
    assert (3 * x).eval() == 12
    assert isinstance(x / 2, ScalarDiv)
    assert (x / 2).eval() == 2


def test_domain_operator_maps_to_registered_node():
    domain = SymbolicDomain("toy")
    domain.register_operator("mul", ToyMul)

    expr = domain.build_operator("mul", Sym(2, "a"), Sym(5, "b"))

    assert isinstance(expr, ToyMul)
    assert expr.eval() == 10


def test_missing_domain_operator_raises_type_error():
    domain = SymbolicDomain("toy")

    with pytest.raises(TypeError, match="no symbolic operator"):
        domain.build_operator("mul", Sym(2, "a"), Sym(5, "b"))
