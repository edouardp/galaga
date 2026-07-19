from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from galaga.names import Name
from galaga.rendering.tree import (
    Associativity,
    Call,
    Delimited,
    Group,
    Identifier,
    Infix,
    Literal,
    MathClass,
    Precedence,
    Product,
    Sum,
    SumTerm,
    Wrapper,
    grouped_child,
)


def test_semantic_nodes_are_immutable_structural_values() -> None:
    node = Product((Literal(2), Identifier(Name("e1", "e₁", r"e_{1}"))))

    assert node == Product((Literal(2), Identifier(Name("e1", "e₁", r"e_{1}"))))
    assert hash(node)
    with pytest.raises(FrozenInstanceError):
        node.factors = ()  # type: ignore[misc]


def test_shared_precedence_groups_lower_binding_and_foreign_equal_operations() -> None:
    addition = Infix(
        (Identifier("a"), Identifier("b")),
        "+",
        precedence=Precedence.SUM,
        associativity=Associativity.ASSOCIATIVE,
        operation_id="add",
    )
    outer = Infix(
        (Identifier("a"), Identifier("b")),
        Name("^", "∧", r"\wedge"),
        precedence=Precedence.PRODUCT,
        associativity=Associativity.ASSOCIATIVE,
        operation_id="outer_product",
    )

    assert grouped_child(addition, parent_precedence=Precedence.PRODUCT) == Group(addition)
    assert (
        grouped_child(
            outer,
            parent_precedence=Precedence.PRODUCT,
            associativity=Associativity.ASSOCIATIVE,
            operation_id="outer_product",
        )
        is outer
    )
    assert grouped_child(
        outer,
        parent_precedence=Precedence.PRODUCT,
        associativity=Associativity.ASSOCIATIVE,
        operation_id="geometric_product",
    ) == Group(outer)


def test_left_associativity_preserves_only_the_matching_left_spine() -> None:
    subtraction = Infix(
        (Identifier("a"), Identifier("b")),
        "-",
        precedence=Precedence.SUM,
        associativity=Associativity.LEFT,
        operation_id="subtract",
    )

    assert (
        grouped_child(
            subtraction,
            parent_precedence=Precedence.SUM,
            associativity=Associativity.LEFT,
            side="left",
            operation_id="subtract",
        )
        is subtraction
    )
    assert grouped_child(
        subtraction,
        parent_precedence=Precedence.SUM,
        associativity=Associativity.LEFT,
        side="right",
        operation_id="subtract",
    ) == Group(subtraction)


def test_invalid_tree_shapes_fail_at_construction() -> None:
    with pytest.raises(ValueError, match="at least one"):
        Sum(())
    with pytest.raises(TypeError, match="SumTerm"):
        Sum((Identifier("x"),))
    with pytest.raises(TypeError, match="render node"):
        SumTerm(object())  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="at least 2"):
        Infix((Identifier("x"),), "+")
    with pytest.raises(ValueError, match="associativity"):
        Product((Identifier("x"),), associativity="sometimes")
    with pytest.raises(TypeError, match="literal precision must be an integer"):
        Literal(1, precision=True)
    with pytest.raises(ValueError, match="literal precision must be between 1 and 17"):
        Literal(1, precision=18)
    with pytest.raises(TypeError, match="call scalable flag"):
        Call("f", scalable=1)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="wrapper scalable flag"):
        Wrapper(Identifier("x"), "(", ")", scalable=1)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="delimiter scalable flag"):
        Delimited((), scalable=1)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="math class"):
        MathClass(Identifier("x"), "relation")
