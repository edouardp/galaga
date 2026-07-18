from __future__ import annotations

import asyncio

import pytest

from galaga.display import build_tree, render
from galaga.facade import Algebra, geometric_product
from galaga.presentation import DisplayPolicy, Notation
from galaga.rendering import Equality


@pytest.fixture
def documented_value():
    algebra = Algebra(2)
    x, y = (value.named(name) for value, name in zip(algebra.basis_vectors(expr=True), ("x", "y"), strict=True))
    return (x + y).named("z")


@pytest.mark.parametrize(
    ("content", "target", "expected"),
    (
        ("name", "ascii", "z"),
        ("expr", "ascii", "x + y"),
        ("value", "ascii", "e1 + e2"),
        ("full", "ascii", "z = x + y = e1 + e2"),
        ("name", "unicode", "z"),
        ("expr", "unicode", "x + y"),
        ("value", "unicode", "e₁ + e₂"),
        ("full", "unicode", "z = x + y = e₁ + e₂"),
        ("name", "latex", "z"),
        ("expr", "latex", "x + y"),
        ("value", "latex", r"e_{1} + e_{2}"),
        ("full", "latex", r"z = x + y = e_{1} + e_{2}"),
    ),
)
def test_content_and_target_are_independent_axes(
    documented_value: object,
    content: str,
    target: str,
    expected: str,
) -> None:
    assert render(documented_value, content=content, target=target) == expected
    assert render(documented_value, f"{content}/{target}") == expected


def test_automatic_content_uses_names_for_teaching_equalities_but_not_provenance_alone() -> None:
    algebra = Algebra(1)
    anonymous = algebra.blade(1)
    named = anonymous.named("x")
    tracked = anonymous.with_expr()
    named_and_tracked = named.with_expr()

    assert str(anonymous) == "e₁"
    assert str(named) == "x = e₁"
    assert str(tracked) == "e₁"
    assert str(named_and_tracked) == "x = x = e₁"


def test_explicit_content_has_a_sensible_value_fallback_when_metadata_is_absent() -> None:
    value = Algebra(1).blade(1)

    assert value.display(content="name", target="ascii") == "e1"
    assert value.display(content="expr", target="ascii") == "e1"
    assert value.display(content="full", target="ascii") == "e1"


def test_all_public_hooks_share_content_policy_and_the_semantic_pipeline(documented_value: object) -> None:
    value = documented_value

    assert str(value) == format(value, "") == value.unicode()
    assert repr(value) == value.ascii()
    assert format(value, "full/latex") == value.latex()
    assert value._repr_latex_() == f"${value.latex()}$"
    tree, target = build_tree(value, "full/latex")
    assert isinstance(tree, Equality)
    assert target == "latex"


def test_explicit_then_scoped_then_persistent_presentation_precedence() -> None:
    algebra = Algebra(2)
    x, y = (value.named(name) for value, name in zip(algebra.basis_vectors(expr=True), ("x", "y"), strict=True))
    value = geometric_product(x, y)
    scoped = algebra.default_presentation.with_notation(Notation.functional())
    explicit = algebra.default_presentation.with_notation(Notation.default())

    assert value.display("expr/ascii") == "xy"
    with algebra.use_presentation(scoped):
        assert value.display("expr/ascii") == "geometric_product(x, y)"
        assert value.display("expr/ascii", notation=Notation.functional(short=True)) == "gp(x, y)"
        assert value.display("expr/ascii", presentation=explicit) == "xy"
    assert value.display("expr/ascii") == "xy"


def test_scoped_rendering_is_isolated_between_interleaved_async_tasks() -> None:
    algebra = Algebra(2)
    x, y = (value.named(name) for value, name in zip(algebra.basis_vectors(expr=True), ("x", "y"), strict=True))
    value = geometric_product(x, y)

    async def worker(notation: Notation) -> tuple[str, str]:
        presentation = algebra.default_presentation.with_notation(notation)
        with algebra.use_presentation(presentation):
            await asyncio.sleep(0)
            inside = value.display("expr/ascii")
            await asyncio.sleep(0)
        return inside, value.display("expr/ascii")

    async def run_workers() -> list[tuple[str, str]]:
        return await asyncio.gather(
            worker(Notation.functional()),
            worker(Notation.functional(short=True)),
        )

    assert asyncio.run(run_workers()) == [
        ("geometric_product(x, y)", "xy"),
        ("gp(x, y)", "xy"),
    ]


def test_display_policy_can_persist_either_axis_without_affecting_numeric_identity() -> None:
    algebra = Algebra(1)
    value = algebra.blade(1).named("x")
    configured = algebra.with_display(DisplayPolicy(content="name", target="ascii"))
    configured_value = configured.blade(1).named("x")

    assert str(configured_value) == "x"
    assert configured_value == value
    assert configured_value.numeric == value.numeric


@pytest.mark.parametrize(
    "operation",
    (
        lambda value: format(value, "everything"),
        lambda value: format(value, "name/html"),
        lambda value: format(value, "name/ascii/extra"),
        lambda value: value.display("name/ascii", target="latex"),
        lambda value: value.latex(wrap="markdown"),
    ),
)
def test_invalid_display_requests_fail_at_the_public_boundary(operation: object) -> None:
    value = Algebra(1).identity
    with pytest.raises(ValueError):
        operation(value)  # type: ignore[operator]
