import asyncio
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest

from galaga import Algebra, DisplayPolicy, Notation, RenderRule, metric_inner_product, presets


def test_notation_scope_renders_metric_pairing_without_changing_the_value():
    algebra = Algebra(config=presets.euclidean(3), expr=True)
    e1, _, _ = algebra.basis_vectors()
    expected = metric_inner_product(e1, e1)
    original = algebra.presentation
    original_latex = expected.latex()
    with algebra.use_notation(presets.notation.lengyel()) as scoped:
        assert scoped is algebra
        actual = metric_inner_product(e1, e1)
        assert actual == expected == algebra.scalar(algebra.gram[0, 0])
        assert hash(actual) == hash(expected)
        assert expected.latex() == actual.latex() == r"e_{1} \mathbin{\bullet} e_{1} \quad = \quad 1"
        assert actual.latex(presentation=original) == original_latex
    assert algebra.presentation is original
    assert actual.latex() == original_latex


def test_notation_scope_preserves_enclosing_components_and_restores_nested_scopes():
    algebra = Algebra(config=presets.cga(2), expr=True)
    original = algebra.presentation
    outer = original.with_display(DisplayPolicy(content="value", coefficient_precision=3))
    # Constructing the context manager must not capture an earlier presentation.
    scope = algebra.use_notation(presets.notation.lengyel())
    with algebra.use_presentation(outer):
        with scope:
            selected = algebra.presentation
            for component in ("blades", "local_names", "display_order", "display"):
                assert getattr(selected, component) is getattr(outer, component)
            assert algebra.expr is True
            with algebra.use_notation(presets.notation.functional()):
                assert algebra.presentation.notation.id == "functional-long"
            assert algebra.presentation is selected
            with algebra.use_presentation(original):
                assert algebra.presentation is original
            assert algebra.presentation is selected
        assert algebra.presentation is outer
    assert algebra.presentation is original


def test_notation_scope_restores_after_exception():
    algebra = Algebra(2)
    original = algebra.presentation
    with pytest.raises(RuntimeError, match="stop"):
        with algebra.use_notation(presets.notation.lengyel()):
            raise RuntimeError("stop")
    assert algebra.presentation is original


@pytest.mark.parametrize("invalid", [None, "lengyel", 3, presets.euclidean(2)])
def test_notation_scope_rejects_invalid_input_without_changing_presentation(invalid):
    algebra = Algebra(2)
    original = algebra.presentation
    with pytest.raises(TypeError, match="notation must be a Notation"):
        with algebra.use_notation(invalid):
            pytest.fail("invalid notation entered the scope")
    assert algebra.presentation is original


def test_notation_scope_is_thread_local():
    algebra = Algebra(2)
    original = algebra.presentation
    barrier = Barrier(2)

    def worker(name):
        with algebra.use_notation(Notation(name)):
            barrier.wait(timeout=10)
            assert algebra.presentation.notation.id == name
        assert algebra.presentation is original

    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(worker, ("first", "second")))
    assert algebra.presentation is original


def test_notation_scope_is_async_task_local():
    algebra = Algebra(2)
    original = algebra.presentation

    async def worker(name):
        with algebra.use_notation(Notation(name)):
            await asyncio.sleep(0)
            assert algebra.presentation.notation.id == name
        assert algebra.presentation is original

    async def run():
        await asyncio.gather(worker("first"), worker("second"))

    asyncio.run(run())
    assert algebra.presentation is original


def test_custom_notation_renders_to_marimo_html_before_scope_exits():
    mo = pytest.importorskip("marimo")
    algebra = Algebra(config=presets.euclidean(3), expr=True)
    e1, _, _ = algebra.basis_vectors()
    value = metric_inner_product(e1, e1)
    original = value.latex()
    notation = algebra.presentation.notation.with_rule(
        "metric_inner_product",
        RenderRule("infix", symbol=r"\bullet", precedence=30),
        target="latex",
    )
    with algebra.use_notation(notation):
        assert value.latex() == r"e_{1} \bullet e_{1} \quad = \quad 1"
        rendered = mo.as_html(value)
    assert r"\bullet" in rendered.text
    assert value.latex() == original
