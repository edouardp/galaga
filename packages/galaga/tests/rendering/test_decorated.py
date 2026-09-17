"""Decoration wrapper emission and its plain-text transparency."""

from __future__ import annotations

import pytest

from galaga import Name
from galaga.rendering import Decorated, Fraction, Group, Identifier, Precedence, Sum, SumTerm, emit, grouped_child


def _e1() -> Identifier:
    return Identifier(Name(ascii="e1", unicode="e₁", latex=r"e_{1}"))


def test_decorated_emits_its_latex_wrapper_and_plain_body_elsewhere() -> None:
    node = Decorated(_e1(), r"\textcolor{red}{", "}")
    assert emit(node, "latex") == r"\textcolor{red}{e_{1}}"
    for target in ("ascii", "unicode"):
        rendered = emit(node, target)
        assert r"\textcolor" not in rendered
        assert "red" not in rendered


def test_decorated_preserves_body_precedence_when_composed() -> None:
    inner = Sum(
        (
            SumTerm(_e1()),
            SumTerm(Identifier(Name(ascii="e2", unicode="e₂", latex=r"e_{2}"))),
        )
    )
    node = Decorated(inner, r"\boxed{", "}")
    assert node.precedence == Precedence.SUM
    assert emit(node, "latex") == r"\boxed{e_{1} + e_{2}}"
    assert isinstance(grouped_child(node, parent_precedence=Precedence.PRODUCT), Group)
    fraction = Fraction(_e1(), grouped_child(node, parent_precedence=Precedence.PRODUCT))
    assert emit(fraction, "ascii") == "e1 / (e1 + e2)"
    assert emit(fraction, "unicode") == "e₁ / (e₁ + e₂)"


def test_decorated_validates_its_fields() -> None:
    with pytest.raises(TypeError, match="strings"):
        Decorated(_e1(), 1, "}")
    with pytest.raises(TypeError, match="decoration body"):
        Decorated("e1", "{", "}")
