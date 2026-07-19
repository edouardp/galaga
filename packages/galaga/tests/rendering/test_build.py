from __future__ import annotations

import pytest

from galaga.expression import BladeLiteral, Call, MultivectorLiteral, ScalarLiteral, Symbol
from galaga.facade import Algebra, OperationSpec
from galaga.names import Name
from galaga.presentation import Notation, RenderRule, default_presentation
from galaga.presets import LengyelRGAPreset
from galaga.rendering import (
    Accent,
    Fraction,
    Group,
    Identifier,
    Infix,
    Literal,
    Power,
    Prefix,
    Product,
    Subscript,
    Sum,
    SumTerm,
    Wrapper,
    _build,
    expression_tree,
    value_tree,
)
from galaga.rendering import (
    Call as RenderCall,
)


def test_expression_leaves_translate_without_selecting_an_output_syntax() -> None:
    presentation = default_presentation(2)
    name = Name("alpha", "α", r"\alpha")

    assert expression_tree(Symbol(name), presentation) == Identifier(name)
    assert expression_tree(ScalarLiteral(2), presentation) == Literal(2)
    assert expression_tree(ScalarLiteral(-2), presentation) == Prefix("-", Literal(2), precedence=40)
    assert expression_tree(BladeLiteral(1), presentation) == Identifier(presentation.blades.label(1).name)
    assert expression_tree(MultivectorLiteral((1, -2, 0, 3)), presentation) == Sum(
        (
            SumTerm(Literal(1)),
            SumTerm(Product((Literal(2), Identifier(presentation.blades.label(1).name))), negative=True),
            SumTerm(Product((Literal(3), Identifier(presentation.blades.label(3).name)))),
        )
    )


def test_signed_rga_blade_labels_round_trip_into_the_semantic_tree() -> None:
    presentation = LengyelRGAPreset().build().presentation

    # Canonical native E13 is displayed as -e31 because the convention's e31
    # label denotes -E13.  The expression orientation composes with that sign.
    assert expression_tree(BladeLiteral(0b0101), presentation) == Prefix(
        "-",
        Identifier(presentation.blades.label(0b0101).name),
        precedence=40,
    )
    assert expression_tree(BladeLiteral(0b0101, -1), presentation) == Identifier(presentation.blades.label(0b0101).name)


def test_default_call_rules_build_semantic_layout_nodes() -> None:
    presentation = default_presentation(2)
    x = Symbol("x")
    y = Symbol("y")

    assert expression_tree(Call("add", (x, y)), presentation) == Sum(
        (SumTerm(Identifier("x")), SumTerm(Identifier("y")))
    )
    assert expression_tree(Call("scalar_divide", (x,), {"scalar": 2}), presentation) == Fraction(
        Identifier("x"), Literal(2)
    )
    assert expression_tree(Call("power", (x,), {"exponent": 2}), presentation) == Power(Identifier("x"), Literal(2))
    assert expression_tree(Call("grade", (x,), {"target": 2}), presentation) == Subscript(
        Wrapper(
            Identifier("x"),
            Name("<", "⟨", r"\langle "),
            Name(">", "⟩", r" \rangle"),
            scalable=False,
        ),
        Literal(2),
    )
    reverse = expression_tree(Call("reverse", (x,)), presentation)
    assert isinstance(reverse, Accent)
    assert reverse.body == Identifier("x")


def test_expression_tree_applies_conservative_display_identities_without_mutating_provenance() -> None:
    expression = Call(
        "add",
        (
            Call("scalar_multiply", (Symbol("x"),), {"scalar": 1}),
            Call("scalar_multiply", (Symbol("y"),), {"scalar": 0}),
        ),
    )

    tree = expression_tree(expression, default_presentation(2))

    assert tree == Identifier("x")
    assert expression.operation_id == "add"
    assert expression.operands[0] == Call("scalar_multiply", (Symbol("x"),), {"scalar": 1})
    assert expression.operands[1] == Call("scalar_multiply", (Symbol("y"),), {"scalar": 0})


def test_conventional_addition_absorbs_a_negative_scaled_rhs_into_a_sum_term() -> None:
    expression = Call(
        "add",
        (
            ScalarLiteral(1),
            Call("scalar_multiply", (Symbol("v"),), {"scalar": -0.5}),
        ),
    )

    assert expression_tree(expression, default_presentation(1)) == Sum(
        (
            SumTerm(Literal(1.0)),
            SumTerm(
                Product(
                    (Literal(0.5), Identifier("v")),
                    precedence=25,
                    associativity="none",
                    operation_id="scalar_multiply",
                ),
                negative=True,
            ),
        )
    )


def test_custom_addition_rule_remains_an_infix_operation() -> None:
    notation = Notation.default().with_rule(
        "add",
        RenderRule("infix", symbol="@", precedence=25, associativity="left"),
    )
    presentation = default_presentation(1).with_notation(notation)

    assert expression_tree(Call("add", (Symbol("x"), Symbol("y"))), presentation) == Infix(
        (Identifier("x"), Identifier("y")),
        "@",
        precedence=25,
        associativity="left",
        operation_id="add",
    )


def test_subtracting_from_a_sum_keeps_the_left_associative_sum_flat() -> None:
    presentation = default_presentation(1)

    tree = expression_tree(
        Call("subtract", (Call("add", (Symbol("a"), Symbol("b"))), Symbol("c"))),
        presentation,
    )

    assert tree == Sum(
        (
            SumTerm(Identifier("a")),
            SumTerm(Identifier("b")),
            SumTerm(Identifier("c"), negative=True),
        )
    )


def test_nested_operations_use_one_parenthesization_model_before_emission() -> None:
    presentation = default_presentation(2)
    expression = Call(
        "geometric_product",
        (
            Call("add", (Symbol("a"), Symbol("b"))),
            Call("outer_product", (Symbol("c"), Symbol("d"))),
        ),
    )

    tree = expression_tree(expression, presentation)

    assert isinstance(tree, Product)
    assert isinstance(tree.factors[0], Group)
    # A different operation at equal product precedence is grouped even though
    # each operation is independently associative.
    assert isinstance(tree.factors[1], Group)


def test_functional_notation_is_the_format_neutral_canonical_fallback() -> None:
    presentation = default_presentation(1).with_notation(Notation.functional())

    assert expression_tree(Call("outer_product", (Symbol("a"), Symbol("b"))), presentation) == RenderCall(
        "outer_product", (Identifier("a"), Identifier("b"))
    )


def test_builder_resolves_operation_identity_but_never_calls_its_evaluator(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls = 0

    def unexpected_evaluation(*args: object) -> object:
        nonlocal calls
        calls += 1
        raise AssertionError("semantic-tree construction evaluated an operation")

    operation = OperationSpec("add", 2, unexpected_evaluation)
    monkeypatch.setattr(_build, "_get_operation", lambda operation_id: operation)

    tree = expression_tree(Call("add", (Symbol("a"), Symbol("b"))), default_presentation(1))

    assert isinstance(tree, Sum)
    assert calls == 0


def test_unknown_operation_fails_in_the_builder_before_an_emitter_is_involved(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    expression = Call("add", (Symbol("a"), Symbol("b")))
    monkeypatch.setattr(
        _build,
        "_get_operation",
        lambda operation_id: (_ for _ in ()).throw(KeyError(f"unknown {operation_id}")),
    )

    with pytest.raises(KeyError, match="unknown add"):
        expression_tree(expression, default_presentation(1), target="latex")


def test_value_tree_reads_display_order_and_coefficients_without_expression_state() -> None:
    algebra = Algebra(config=LengyelRGAPreset())
    value = algebra.multivector((1, 0, 0, 2, 0, 3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0))

    tree = value_tree(value)

    assert isinstance(tree, Sum)
    assert tree.terms[0] == SumTerm(Literal(1))
    # RGA's cyclic bivector order puts mask 5 (e31) before mask 3 (e12).
    # The signed label changes +3 E13 into -3 e31.
    assert tree.terms[1].body == Product((Literal(3), Identifier(algebra.presentation.blades.label(5).name)))
    assert tree.terms[1].negative
    assert tree.terms[2].body == Product((Literal(2), Identifier(algebra.presentation.blades.label(3).name)))
    assert not tree.terms[2].negative


def test_multivector_literal_dimension_mismatch_is_reported_by_presentation_boundary() -> None:
    with pytest.raises(ValueError, match="does not match presentation dimension"):
        expression_tree(MultivectorLiteral((1, 2)), default_presentation(2))
