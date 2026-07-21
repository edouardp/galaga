from __future__ import annotations

import pytest

from galaga.expression import BladeLiteral, Call, ScalarLiteral, Symbol
from galaga.facade import Algebra
from galaga.names import Name


def test_all_four_name_and_expression_states_are_independent() -> None:
    algebra = Algebra(2)
    original = algebra.blade(1)

    named = original.named(Name("x", "𝑥", "x"))
    tracked = original.with_expr()
    named_tracked = named.with_expr()

    assert original.name is None and original.expr is None
    assert named.name is not None and named.expr is None
    assert tracked.name is None and isinstance(tracked.expr, BladeLiteral)
    assert named_tracked.name == named.name and named_tracked.expr == Symbol(named.name)


def test_state_transitions_are_new_wrappers_over_the_same_numeric_value() -> None:
    value = Algebra(2).vector([2, 3])
    transitions = (
        value.named("v"),
        value.unnamed(),
        value.with_expr(),
        value.without_expr(),
    )

    assert all(result is not value for result in transitions)
    assert all(result.numeric is value.numeric for result in transitions)


def test_removing_name_and_expression_do_not_affect_each_other() -> None:
    value = Algebra(2).scalar(3).named("s").with_expr()

    unnamed = value.unnamed()
    untracked = value.without_expr()

    assert unnamed.name is None and unnamed.expr == value.expr
    assert untracked.name == value.name and untracked.expr is None


def test_explicit_expression_can_be_attached() -> None:
    value = Algebra(1).scalar(4)
    expression = ScalarLiteral(2)

    result = value.with_expr(expression)

    assert result.expr is expression
    assert result.same_expression(value.with_expr(ScalarLiteral(2)))


def test_mathematical_equality_and_hash_ignore_name_and_expression() -> None:
    value = Algebra(2).blade(1)
    decorated = value.named("x").with_expr()

    assert decorated == value
    assert hash(decorated) == hash(value)
    assert len({value, decorated}) == 1


def test_naming_does_not_attach_an_expression_but_named_operations_are_tracked() -> None:
    algebra = Algebra(2)
    x = algebra.blade(1).named("x")
    y = algebra.blade(2).named("y")

    result = x * y

    assert x.expr is None
    assert y.expr is None
    assert result.expr == Call("geometric_product", (Symbol("x"), Symbol("y")))


def test_factories_support_names_and_explicit_tracking() -> None:
    algebra = Algebra(2)

    value = algebra.vector([1, 2], name=Name("v", "𝑣", "v"), expr=True)

    assert value.name == Name("v", "𝑣", "v")
    assert value.name is not None
    assert value.expr == Symbol(value.name)


def test_locals_are_named_without_implicitly_being_tracked() -> None:
    algebra = Algebra(2)

    values = algebra.locals()

    assert values
    assert all(value.name is not None and value.expr is None for value in values.values())


def test_invalid_state_inputs_fail_clearly() -> None:
    value = Algebra(1).scalar(1)

    with pytest.raises(TypeError, match="name"):
        value.named(1)  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="override"):
        value.named(Name("x"), unicode="𝑥")
    with pytest.raises(TypeError, match="expr"):
        Algebra(1).scalar(1, expr="yes")  # type: ignore[arg-type]
    with pytest.raises(TypeError, match="expr"):
        Algebra(1).basis_vectors(expr="yes")  # type: ignore[arg-type]
