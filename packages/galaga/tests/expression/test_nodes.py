from __future__ import annotations

import ast
from pathlib import Path

import pytest

from galaga.expression import BladeLiteral, Call, Expr, MultivectorLiteral, ScalarLiteral, Symbol
from galaga.names import Name


@pytest.mark.parametrize(
    "node",
    [
        Symbol(Name("x", "𝑥", "x")),
        ScalarLiteral(2),
        BladeLiteral(3, -1),
        MultivectorLiteral((1, 2, 3, 4)),
        Call("add", (Symbol("x"), ScalarLiteral(1))),
        Call("grade", (Symbol("x"),), {"target": 2}),
    ],
)
def test_nodes_have_structural_equality_and_hashing(node: Expr) -> None:
    assert node == node
    assert hash(node) == hash(node)
    assert len({node, node}) == 1


def test_symbol_preserves_all_target_spellings_without_selecting_one() -> None:
    name = Name("alpha", "α", r"\alpha")

    symbol = Symbol(name)

    assert symbol.name is name
    assert symbol.identifier == "alpha"
    assert not hasattr(symbol, "format")
    assert not hasattr(symbol, "target")


@pytest.mark.parametrize(
    ("factory", "error"),
    [
        (lambda: Symbol(1), TypeError),
        (lambda: ScalarLiteral(True), TypeError),
        (lambda: ScalarLiteral(float("inf")), ValueError),
        (lambda: BladeLiteral("1"), TypeError),
        (lambda: BladeLiteral(-1), ValueError),
        (lambda: BladeLiteral(1, "positive"), TypeError),
        (lambda: BladeLiteral(1, 0), ValueError),
        (lambda: MultivectorLiteral("12"), TypeError),
        (lambda: MultivectorLiteral(()), ValueError),
        (lambda: MultivectorLiteral((1, 2, 3)), ValueError),
        (lambda: Call("missing", (ScalarLiteral(1),)), ValueError),
        (lambda: Call("", (ScalarLiteral(1),)), ValueError),
        (lambda: Call("add", (ScalarLiteral(1),)), ValueError),
        (lambda: Call("add", (object(), ScalarLiteral(1))), TypeError),
        (lambda: Call("grade", (ScalarLiteral(1),)), ValueError),
        (lambda: Call("grade", (ScalarLiteral(1),), {"target": []}), TypeError),
        (lambda: Call("grade", (ScalarLiteral(1),), {"target": 1, "extra": 2}), ValueError),
    ],
)
def test_invalid_nodes_are_rejected(factory: object, error: type[Exception]) -> None:
    with pytest.raises(error):
        factory()  # type: ignore[operator]


def test_call_parameters_are_normalized_and_hashable() -> None:
    call = Call("grades", (Symbol("x"),), {"targets": [3, 1]})

    assert call.parameters == (("targets", (3, 1)),)
    assert hash(call)


def test_node_module_has_no_direct_numeric_or_rendering_import() -> None:
    source_path = Path(__file__).parents[2] / "galaga" / "expression" / "_nodes.py"
    tree = ast.parse(source_path.read_text())
    imports = {
        alias.name for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)) for alias in node.names
    }

    assert "core" not in imports
    assert "numpy" not in imports
    assert "render" not in imports
