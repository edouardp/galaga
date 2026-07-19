"""Readable expression functions with exact configured LaTeX test cases."""

from __future__ import annotations

import math
from typing import Any

import pytest
from tools.latex_contract import latex_test, testcase
from tools.rendering_contract import NAMED_ALGEBRAS, ExpressionContext, context_for


@latex_test(
    testcase(
        "legacy-v1/cl3/full-default",
        r"e_{1} \wedge e_{2} \quad = \quad e_{12}",
    ),
    testcase(
        "core-facade-v2/cl3/full-default",
        r"e_{1} \wedge e_{2} \quad = \quad e_{12}",
    ),
)
def test_simple_wedge_expression(context: ExpressionContext) -> Any:
    """The minimal full-rendering example."""
    e1, e2, _ = context.basis_vectors()
    return e1 ^ e2


@latex_test(
    testcase(
        "legacy-v1/cl3/full-default",
        r"1 + v \quad = \quad 1 - 0.5 e_{1}",
    ),
    testcase(
        "core-facade-v2/cl3/full-default",
        r"1 + v \quad = \quad 1 - 0.5 e_{1}",
    ),
)
def test_named_negative_vector_is_a_symbolic_boundary(context: ExpressionContext) -> Any:
    """Naming a negative value keeps its name, rather than leaking its value into syntax."""
    e1, _, _ = context.basis_vectors()
    v = context.named(-0.5 * e1, "v")
    return 1 + v


@latex_test(
    testcase(
        "legacy-v1/cl3/full-default",
        r"1 - 0.5 v \quad = \quad 1 - 0.5 e_{1}",
    ),
    testcase(
        "core-facade-v2/cl3/full-default",
        r"1 - 0.5 v \quad = \quad 1 - 0.5 e_{1}",
    ),
)
def test_add_negative_scaled_named_vector(context: ExpressionContext) -> Any:
    """A negative term added to a sum renders as subtraction, following v1."""
    e1, _, _ = context.basis_vectors()
    v = context.named(e1, "v")
    return 1 + (-0.5 * v)


@latex_test(
    testcase(
        "legacy-v1/cl3/full-default",
        r"1 - v \quad = \quad 1 - e_{1}",
    ),
    testcase(
        "core-facade-v2/cl3/full-default",
        r"1 - v \quad = \quad 1 - e_{1}",
    ),
)
def test_add_negative_unit_scaled_named_vector(context: ExpressionContext) -> Any:
    """The v1 oracle suppresses a unit coefficient after absorbing its sign."""
    e1, _, _ = context.basis_vectors()
    v = context.named(e1, "v")
    return 1 + (-1 * v)


@latex_test(
    testcase(
        "legacy-v1/cl3/full-default",
        r"""
        x
        \quad = \quad
        3 + e_{1} + 2 e_{1} \wedge e_{2} + e_{1} \wedge e_{2} \wedge e_{3}
        \quad = \quad
        3 + e_{1} + 2 e_{12} + e_{123}
        """,
    ),
    testcase(
        "core-facade-v2/cl3/full-default",
        r"""
        x
        \quad = \quad
        3 + e_{1} + 2 e_{1} \wedge e_{2} + e_{1} \wedge e_{2} \wedge e_{3}
        \quad = \quad
        3 + e_{1} + 2 e_{12} + e_{123}
        """,
    ),
)
def test_mixed_grade_expression(context: ExpressionContext) -> Any:
    """From examples/algebra/involutions_and_grade_ops.py."""
    e1, e2, e3 = context.basis_vectors()
    return context.named(3 + e1 + 2 * (e1 ^ e2) + (e1 ^ e2 ^ e3), "x")


@latex_test(
    testcase(
        "legacy-v1/cl3/full-default",
        r"u \wedge v \quad = \quad 3.1 e_{12}",
    ),
    testcase(
        "core-facade-v2/cl3/full-default",
        r"u \wedge v \quad = \quad 3.1 e_{12}",
    ),
)
def test_exterior_area_expression(context: ExpressionContext) -> Any:
    """From examples/algebra/exterior_algebra_intuition.py."""
    e1, e2, _ = context.basis_vectors()
    u = context.named(2 * e1 + e2, "u")
    v = context.named(0.5 * e1 + 1.8 * e2, "v")
    return u ^ v


@latex_test(
    testcase(
        "legacy-v1/cl3/full-default",
        r"u \wedge v \wedge w \quad = \quad 3.72 e_{123}",
    ),
    testcase(
        "core-facade-v2/cl3/full-default",
        r"u \wedge v \wedge w \quad = \quad 3.72 e_{123}",
    ),
)
def test_exterior_volume_expression(context: ExpressionContext) -> Any:
    """From examples/algebra/exterior_algebra_intuition.py."""
    e1, e2, e3 = context.basis_vectors()
    u = context.named(2 * e1 + e2, "u")
    v = context.named(0.5 * e1 + 1.8 * e2, "v")
    w = context.named(e1 + 0.5 * e2 + 1.2 * e3, "w")
    return u ^ v ^ w


@latex_test(
    testcase(
        "legacy-v1/cl2/full-default",
        r"""
        r' \quad = \quad R r \tilde{R}
        \quad = \quad 0.839999 e_{1} + 1.48809 e_{2}
        """,
    ),
    testcase(
        "core-facade-v2/cl2/full-default",
        r"""
        r' \quad = \quad R r \widetilde{R}
        \quad = \quad 0.839999 e_{1} + 1.48809 e_{2}
        """,
    ),
)
def test_rotor_sandwich_expression(context: ExpressionContext) -> Any:
    """From examples/physics/planar_kinematics_lazy.py."""
    e1, e2 = context.basis_vectors()
    plane = context.named(e1 * e2, "B", latex=r"e_1 e_2")
    rotor = context.named(context.call("exp", (-math.radians(40) / 2) * plane), "R")
    arm = context.named(1.6 * e1 + 0.6 * e2, "r")
    return context.named(rotor * arm * ~rotor, "r'", latex=r"r'")


@latex_test(
    testcase(
        "legacy-v1/cl3/full-default",
        r"\left(v \;\lrcorner\; B\right) B^{-1} \quad = \quad e_{1} + e_{2}",
    ),
    testcase(
        "core-facade-v2/cl3/full-default",
        r"\left(v \;\lrcorner\; B\right) B^{-1} \quad = \quad e_{1} + e_{2}",
    ),
)
def test_projection_expression(context: ExpressionContext) -> Any:
    """From examples/algebra/duality_and_subspaces.py."""
    e1, e2, e3 = context.basis_vectors()
    plane = context.named(e1 ^ e2, "B")
    vector = context.named(e1 + e2 + e3, "v")
    return context.call("left_contraction", vector, plane) * context.call("inverse", plane)


@latex_test(
    testcase(
        "legacy-v1/pga3/full-default",
        r"""
        A^{\complement} \wedge B^{\complement}
        \quad = \quad
        -2 e_{01} - e_{02} - e_{12}
        """,
    ),
    testcase(
        "core-facade-v2/pga3/full-default",
        r"""
        A^{\complement} \wedge B^{\complement}
        \quad = \quad
        -e_{12} + 2 e_{10} + e_{20}
        """,
    ),
)
def test_pga_join_expression(context: ExpressionContext) -> Any:
    """From examples/algebra/meets_joins_pga.py."""
    e1, e2, e3, e0 = context.basis_vectors()
    e123 = context.named(e1 ^ e2 ^ e3, "i")
    E1 = context.named(e2 ^ e3 ^ e0, "E_1")
    E2 = context.named(-e1 ^ e3 ^ e0, "E_2")
    first = context.named(e123 - E1, "A")
    second = context.named(e123 + E1 + E2, "B")
    return context.call("complement", first) ^ context.call("complement", second)


@latex_test(
    testcase(
        "legacy-v1/pga3/full-default",
        r"""
        C \quad = \quad i - 0.5 E_1 + 1.5 E_2
        \quad = \quad
        -1.5 e_{013} - 0.5 e_{023} + e_{123}
        """,
    ),
    testcase(
        "core-facade-v2/pga3/full-default",
        r"""
        C \quad = \quad i - 0.5 E_1 + 1.5 E_2
        \quad = \quad
        e_{123} - 1.5 e_{130} - 0.5 e_{230}
        """,
    ),
)
def test_pga_point_with_negative_coordinate(context: ExpressionContext) -> Any:
    """The point expression uses subtraction for a negative coordinate."""
    e1, e2, e3, e0 = context.basis_vectors()
    e123 = context.named(e1 ^ e2 ^ e3, "i")
    E1 = context.named(e2 ^ e3 ^ e0, "E_1")
    E2 = context.named((-e1) ^ e3 ^ e0, "E_2")
    return context.named(e123 + (-0.5 * E1) + (1.5 * E2), "C")


@latex_test(
    testcase(
        "legacy-v1/cl3/full-default",
        r"""
        x
        \quad = \quad
        1.23457 e_{1} + 1.4524 \times 10^{-16} e_{2}
        + e_{3} + 0 e_{1} \wedge e_{2}
        \quad = \quad 1.23457 e_{1} + e_{3}
        """,
    ),
    testcase(
        "core-facade-v2/cl3/full-default",
        r"""
        x
        \quad = \quad
        1.23457 e_{1} + 1.4524 \times 10^{-16} e_{2} + e_{3}
        \quad = \quad
        1.23457 e_{1} + e_{3}
        """,
    ),
    testcase(
        "core-facade-v2/cl3/full-precision-3",
        r"""
        x
        \quad = \quad
        1.23 e_{1} + 1.45 \times 10^{-16} e_{2} + e_{3}
        \quad = \quad
        1.23 e_{1} + e_{3}
        """,
    ),
    testcase(
        "core-facade-v2/cl3/full-unfiltered-12",
        r"""
        x
        \quad = \quad
        1.23456789 e_{1} + 1.4524 \times 10^{-16} e_{2} + e_{3}
        """,
    ),
)
def test_display_sensitive_expression(context: ExpressionContext) -> Any:
    """Coefficient zero, unit, cutoff, and precision boundaries."""
    e1, e2, e3 = context.basis_vectors()
    return context.named(
        1.23456789 * e1 + 1.4524e-16 * e2 + 1 * e3 + 0 * (e1 ^ e2),
        "x",
    )


@pytest.mark.parametrize("configuration", NAMED_ALGEBRAS)
def test_every_named_algebra_configuration_can_be_constructed(configuration: str) -> None:
    assert context_for(configuration).configuration is NAMED_ALGEBRAS[configuration]


def test_multiline_expected_latex_is_dedented_and_joined_for_readability() -> None:
    case = testcase(
        "core-facade-v2/cl3/full-default",
        r"""
        a \wedge b
        \quad = \quad e_{12}
        """,
    )

    assert case.expected == r"a \wedge b \quad = \quad e_{12}"
