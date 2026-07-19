"""Readable decorator support for exact configured rendering tests."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from textwrap import dedent
from typing import Any

import pytest

from tools.rendering_contract import ExpressionContext, context_for

ExpressionTest = Callable[[ExpressionContext], Any]


@dataclass(frozen=True, slots=True)
class RenderingTestCase:
    """One configured implementation and exact rendering expectation."""

    algebra: str
    expected: str
    target: str = "latex"
    content: str = "full"


def testcase(
    algebra: str,
    expected: str,
    *,
    target: str = "latex",
    content: str = "full",
) -> RenderingTestCase:
    """Declare one expectation, allowing readable multiline source text."""
    lines = dedent(expected).strip().splitlines()
    return RenderingTestCase(
        algebra,
        " ".join(line.strip() for line in lines),
        target,
        content,
    )


# Keep the deliberately readable public spelling from looking like a test to
# Pytest's name-based collector.
testcase.__test__ = False


def render_test(*cases: RenderingTestCase) -> Callable[[ExpressionTest], Any]:
    """Turn a value-returning expression function into parameterized Pytest cases."""
    if not cases:
        raise ValueError("render_test requires at least one testcase")

    def decorate(expression: ExpressionTest) -> Any:
        def execute(_rendering_case: RenderingTestCase) -> None:
            context = context_for(_rendering_case.algebra)
            value = expression(context)

            # The expression function has returned and its locals are gone.
            # The value and context must retain everything required to render.
            actual = context.render(
                value,
                target=_rendering_case.target,
                content=_rendering_case.content,
            )
            assert actual == _rendering_case.expected  # nosec B101 - this is a Pytest assertion helper

        execute.__name__ = expression.__name__
        execute.__qualname__ = expression.__qualname__
        execute.__doc__ = expression.__doc__
        return pytest.mark.parametrize(
            "_rendering_case",
            cases,
            ids=_case_id,
        )(execute)

    return decorate


def latex_test(*cases: RenderingTestCase) -> Callable[[ExpressionTest], Any]:
    """Readable alias for full-LaTeX rendering contracts."""
    if any(case.target != "latex" or case.content != "full" for case in cases):
        raise ValueError("latex_test cases must use target='latex' and content='full'")
    return render_test(*cases)


def _case_id(case: RenderingTestCase) -> str:
    if case.target == "latex" and case.content == "full":
        return case.algebra
    return f"{case.algebra}/{case.content}-{case.target}"


__all__ = [
    "ExpressionTest",
    "RenderingTestCase",
    "latex_test",
    "render_test",
    "testcase",
]
