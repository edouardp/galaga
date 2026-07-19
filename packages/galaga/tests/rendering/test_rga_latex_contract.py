"""Exact rendering contracts for Eric Lengyel's RGA presentation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import pytest
from tools.latex_contract import latex_test, testcase
from tools.rendering_contract import ExpressionContext, context_for

LEGACY_RGA = "legacy-v1/lengyel-rga/full-default"
FACADE_RGA = "core-facade-v2/lengyel-rga/full-default"


@dataclass(frozen=True, slots=True)
class NotationExpectation:
    """One Lengyel operation's exact expression rendering in every supported channel."""

    operation: str
    arity: int
    legacy_unicode: str
    legacy_latex: str
    facade_ascii: str
    facade_unicode: str
    facade_latex: str
    order: int | None = None


def notation(
    operation: str,
    arity: int,
    *,
    legacy_unicode: str,
    legacy_latex: str,
    facade_ascii: str,
    facade_unicode: str,
    facade_latex: str,
    order: int | None = None,
) -> NotationExpectation:
    """Keep one operation's target spellings together for human review."""
    return NotationExpectation(
        operation,
        arity,
        legacy_unicode,
        legacy_latex,
        facade_ascii,
        facade_unicode,
        facade_latex,
        order,
    )


LENGYEL_NOTATION = (
    notation(
        "geometric_product",
        2,
        legacy_unicode="a ⟑ b",
        legacy_latex=r"a \mathbin{\text{⟑}} b",
        facade_ascii="gp(a, b)",
        facade_unicode="a ⟑ b",
        facade_latex=r"a \mathbin{\text{⟑}} b",
    ),
    notation(
        "outer_product",
        2,
        legacy_unicode="a∧b",
        legacy_latex=r"a \wedge b",
        facade_ascii="a ^ b",
        facade_unicode="a ∧ b",
        facade_latex=r"a \wedge b",
    ),
    notation(
        "geometric_antiproduct",
        2,
        legacy_unicode="a ⟇ b",
        legacy_latex=r"a \mathbin{\text{⟇}} b",
        facade_ascii="geometric_antiproduct(a, b)",
        facade_unicode="a ⟇ b",
        facade_latex=r"a \mathbin{\text{⟇}} b",
    ),
    notation(
        "metric_inner_product",
        2,
        legacy_unicode="a • b",
        legacy_latex=r"a \mathbin{\bullet} b",
        facade_ascii="metric_inner_product(a, b)",
        facade_unicode="a • b",
        facade_latex=r"a \mathbin{\bullet} b",
    ),
    notation(
        "antidot_product",
        2,
        legacy_unicode="a ∘ b",
        legacy_latex=r"a \mathbin{\circ} b",
        facade_ascii="antidot_product(a, b)",
        facade_unicode="a ∘ b",
        facade_latex=r"a \mathbin{\circ} b",
    ),
    notation(
        "antiwedge",
        2,
        legacy_unicode="a∨b",
        legacy_latex=r"a \vee b",
        facade_ascii="antiwedge(a, b)",
        facade_unicode="a ∨ b",
        facade_latex=r"a \vee b",
    ),
    notation(
        "regressive_product",
        2,
        legacy_unicode="a∨b",
        legacy_latex=r"a \vee b",
        facade_ascii="a vee b",
        facade_unicode="a ∨ b",
        facade_latex=r"a \vee b",
    ),
    notation(
        "left_interior_product",
        2,
        legacy_unicode="a ⌋ b",
        legacy_latex=r"a \mathbin{\rfloor} b",
        facade_ascii="left_interior_product(a, b)",
        facade_unicode="a ⌋ b",
        facade_latex=r"a \mathbin{\rfloor} b",
    ),
    notation(
        "right_interior_product",
        2,
        legacy_unicode="a ⌊ b",
        legacy_latex=r"a \mathbin{\lfloor} b",
        facade_ascii="right_interior_product(a, b)",
        facade_unicode="a ⌊ b",
        facade_latex=r"a \mathbin{\lfloor} b",
    ),
    notation(
        "transwedge",
        2,
        order=1,
        legacy_unicode="a ⩓₁ b",
        legacy_latex=r"a \mathbin{\underset{1}{\text{⩓}}} b",
        facade_ascii="transwedge(a, b, 1)",
        facade_unicode="a ⩓₁ b",
        facade_latex=r"a \mathbin{\underset{1}{\text{⩓}}} b",
    ),
    notation(
        "transwedge_antiproduct",
        2,
        order=1,
        legacy_unicode="a ⩔₁ b",
        legacy_latex=r"a \mathbin{\underset{1}{\text{⩔}}} b",
        facade_ascii="transwedge_antiproduct(a, b, 1)",
        facade_unicode="a ⩔₁ b",
        facade_latex=r"a \mathbin{\underset{1}{\text{⩔}}} b",
    ),
    notation(
        "complement",
        1,
        legacy_unicode="a̅",
        legacy_latex=r"\overline{\vphantom{Aft^6}a}",
        facade_ascii="complement(a)",
        facade_unicode="a̅",
        facade_latex=r"\overline{a}",
    ),
    notation(
        "right_complement",
        1,
        legacy_unicode="a̅",
        legacy_latex=r"\overline{\vphantom{Aft^6}a}",
        facade_ascii="right_complement(a)",
        facade_unicode="a̅",
        facade_latex=r"\overline{a}",
    ),
    notation(
        "left_complement",
        1,
        legacy_unicode="a̲",
        legacy_latex=r"\underline{\vphantom{gy_7}a}",
        facade_ascii="left_complement(a)",
        facade_unicode="a̲",
        facade_latex=r"\underline{a}",
    ),
    notation(
        "reverse",
        1,
        legacy_unicode="ã",
        legacy_latex=r"\tilde{a}",
        facade_ascii="~a",
        facade_unicode="ã",
        facade_latex=r"\widetilde{a}",
    ),
    notation(
        "antireverse",
        1,
        legacy_unicode="a̰",
        legacy_latex=r"\utilde{a}",
        facade_ascii="antireverse(a)",
        facade_unicode="a̰",
        facade_latex=r"\utilde{a}",
    ),
    notation(
        "right_hodge_dual",
        1,
        legacy_unicode="a^★",
        legacy_latex=r"a^{\text{★}}",
        facade_ascii="right_hodge_dual(a)",
        facade_unicode="a^★",
        facade_latex=r"a^{\text{★}}",
    ),
    notation(
        "left_hodge_dual",
        1,
        legacy_unicode="a_★",
        legacy_latex=r"{a}_{\text{★}}",
        facade_ascii="left_hodge_dual(a)",
        facade_unicode="a_★",
        facade_latex=r"a_{\text{★}}",
    ),
    notation(
        "right_weight_dual",
        1,
        legacy_unicode="a^☆",
        legacy_latex=r"a^{\text{☆}}",
        facade_ascii="right_weight_dual(a)",
        facade_unicode="a^☆",
        facade_latex=r"a^{\text{☆}}",
    ),
    notation(
        "left_weight_dual",
        1,
        legacy_unicode="a_☆",
        legacy_latex=r"{a}_{\text{☆}}",
        facade_ascii="left_weight_dual(a)",
        facade_unicode="a_☆",
        facade_latex=r"a_{\text{☆}}",
    ),
    notation(
        "bulk_part",
        1,
        legacy_unicode="a_●",
        legacy_latex=r"{a}_{\text{●}}",
        facade_ascii="bulk_part(a)",
        facade_unicode="a_●",
        facade_latex=r"a_{\text{●}}",
    ),
    notation(
        "weight_part",
        1,
        legacy_unicode="a_○",
        legacy_latex=r"{a}_{\text{○}}",
        facade_ascii="weight_part(a)",
        facade_unicode="a_○",
        facade_latex=r"a_{\text{○}}",
    ),
    notation(
        "metric_apply",
        1,
        legacy_unicode="Ga",
        legacy_latex=r"\mathbf{G}a",
        facade_ascii="metric_apply(a)",
        facade_unicode="Ga",
        facade_latex=r"\mathbf{G}a",
    ),
    notation(
        "antimetric_apply",
        1,
        legacy_unicode="𝔾a",
        legacy_latex=r"\mathbb{G}a",
        facade_ascii="antimetric_apply(a)",
        facade_unicode="𝔾a",
        facade_latex=r"\mathbb{G}a",
    ),
    notation(
        "conjugate",
        1,
        legacy_unicode="conjugate(a)",
        legacy_latex=r"\operatorname{conjugate}(a)",
        facade_ascii="conjugate(a)",
        facade_unicode="conjugate(a)",
        facade_latex=r"\operatorname{conjugate}(a)",
    ),
    notation(
        "hestenes_inner",
        2,
        legacy_unicode="a·b",
        legacy_latex=r"a \cdot b",
        facade_ascii="hestenes_inner(a, b)",
        facade_unicode="hestenes_inner(a, b)",
        facade_latex=r"\operatorname{hestenes\_inner}(a,\, b)",
    ),
)


@pytest.mark.parametrize("expectation", LENGYEL_NOTATION, ids=lambda item: item.operation)
def test_every_lengyel_operation_has_exact_target_rendering(expectation: NotationExpectation) -> None:
    """Every special rule is asserted through the same cross-version context."""
    renderings = (
        (LEGACY_RGA, "unicode", expectation.legacy_unicode),
        (LEGACY_RGA, "latex", expectation.legacy_latex),
        (FACADE_RGA, "ascii", expectation.facade_ascii),
        (FACADE_RGA, "unicode", expectation.facade_unicode),
        (FACADE_RGA, "latex", expectation.facade_latex),
    )
    for configuration, target, expected in renderings:
        context = context_for(configuration)
        e1, e2, _, _ = context.basis_vectors()
        a = context.named(e1, "a")
        b = context.named(e2, "b")
        arguments = (a,) if expectation.arity == 1 else (a, b)
        if expectation.order is not None:
            arguments = (*arguments, expectation.order)
        value = context.call(expectation.operation, *arguments)

        assert context.render(value, target=target, content="expr") == expected, (
            expectation.operation,
            configuration,
            target,
        )


RGA_BLADE_TABLE = (
    ("1", "1", "1", "1"),
    ("e1", "e1", "e₁", r"\mathbf{e}_{1}"),
    ("e2", "e2", "e₂", r"\mathbf{e}_{2}"),
    ("e3", "e3", "e₃", r"\mathbf{e}_{3}"),
    ("e4", "e4", "e₄", r"\mathbf{e}_{4}"),
    ("e23", "e23", "e₂₃", r"\mathbf{e}_{23}"),
    ("e31", "e31", "e₃₁", r"\mathbf{e}_{31}"),
    ("e12", "e12", "e₁₂", r"\mathbf{e}_{12}"),
    ("e41", "e41", "e₄₁", r"\mathbf{e}_{41}"),
    ("e42", "e42", "e₄₂", r"\mathbf{e}_{42}"),
    ("e43", "e43", "e₄₃", r"\mathbf{e}_{43}"),
    ("e423", "e423", "e₄₂₃", r"\mathbf{e}_{423}"),
    ("e431", "e431", "e₄₃₁", r"\mathbf{e}_{431}"),
    ("e412", "e412", "e₄₁₂", r"\mathbf{e}_{412}"),
    ("e321", "e321", "e₃₂₁", r"\mathbf{e}_{321}"),
    ("I", "I", "𝟙", r"\text{𝟙}"),
)


@pytest.mark.parametrize(
    ("blade_name", "ascii_expected", "unicode_expected", "latex_expected"),
    RGA_BLADE_TABLE,
    ids=[row[0] for row in RGA_BLADE_TABLE],
)
def test_complete_rga_blade_table_has_exact_target_rendering(
    blade_name: str,
    ascii_expected: str,
    unicode_expected: str,
    latex_expected: str,
) -> None:
    context = context_for(FACADE_RGA)
    blade = context.algebra.blade(blade_name)

    assert blade.ascii(content="value") == ascii_expected
    assert blade.unicode(content="value") == unicode_expected
    assert blade.latex(content="value") == latex_expected


def test_native_and_named_rga_blade_orientations_render_with_opposite_signs() -> None:
    context = context_for(FACADE_RGA)
    native_e13 = context.algebra.blade(0b0101)
    named_e31 = context.algebra.blade("e31")

    assert native_e13.ascii(content="value") == "-e31"
    assert native_e13.unicode(content="value") == "-e₃₁"
    assert native_e13.latex(content="value") == r"-\mathbf{e}_{31}"
    assert named_e31.latex(content="value") == r"\mathbf{e}_{31}"


@latex_test(
    testcase(
        LEGACY_RGA,
        r"""
        u \wedge v + u \mathbin{\bullet} v
        \quad = \quad -1
        + 2 \mathbf{e}_{23} - \mathbf{e}_{31} - 3 \mathbf{e}_{12}
        + \mathbf{e}_{41} - \mathbf{e}_{42} + \mathbf{e}_{43}
        """,
    ),
    testcase(
        FACADE_RGA,
        r"""
        u \wedge v + u \mathbin{\bullet} v
        \quad = \quad -1
        + 2 \mathbf{e}_{23} - \mathbf{e}_{31} - 3 \mathbf{e}_{12}
        + \mathbf{e}_{41} - \mathbf{e}_{42} + \mathbf{e}_{43}
        """,
    ),
)
def test_rga_product_decomposition_expression(context: ExpressionContext) -> Any:
    """From examples/rga/rga_demo.py."""
    e1, e2, e3, e4 = context.basis_vectors()
    u = context.named(e1 + 2 * e2 + e4, "u")
    v = context.named(e1 - e2 + e3, "v")
    return context.call("outer_product", u, v) + context.call("metric_inner_product", u, v)


@latex_test(
    testcase(
        LEGACY_RGA,
        r"""
        \pi_x \vee \pi_y
        \quad = \quad -\mathbf{e}_{43}
        """,
    ),
    testcase(
        FACADE_RGA,
        r"""
        \pi_x \vee \pi_y
        \quad = \quad -\mathbf{e}_{43}
        """,
    ),
)
def test_rga_coordinate_planes_meet_in_their_common_line(
    context: ExpressionContext,
) -> Any:
    """From the join-and-meet section of examples/rga/rga_demo.py."""
    e1, e2, e3, e4 = context.basis_vectors()
    plane_x = context.named(e4 ^ e2 ^ e3, "pi_x", latex=r"\pi_x")
    plane_y = context.named(e4 ^ e3 ^ e1, "pi_y", latex=r"\pi_y")
    return context.call("antiwedge", plane_x, plane_y)


@latex_test(
    testcase(
        LEGACY_RGA,
        r"""
        {L}_{\text{●}} + {L}_{\text{○}}
        \quad = \quad
        2 \mathbf{e}_{23} - \mathbf{e}_{31}
        + 3 \mathbf{e}_{41} - \mathbf{e}_{42}
        """,
    ),
    testcase(
        FACADE_RGA,
        r"""
        L_{\text{●}} + L_{\text{○}}
        \quad = \quad
        2 \mathbf{e}_{23} - \mathbf{e}_{31}
        + 3 \mathbf{e}_{41} - \mathbf{e}_{42}
        """,
    ),
)
def test_rga_bulk_and_weight_parts_reconstruct_a_line(
    context: ExpressionContext,
) -> Any:
    """From the metric/antimetric section of examples/rga/rga_demo.py."""
    e1, e2, e3, e4 = context.basis_vectors()
    line = context.named(
        2 * (e2 ^ e3) - (e3 ^ e1) + 3 * (e4 ^ e1) - (e4 ^ e2),
        "L",
    )
    return context.call("bulk_part", line) + context.call("weight_part", line)


@latex_test(
    testcase(
        LEGACY_RGA,
        r"""
        P^{\text{★}} + P^{\text{☆}}
        \quad = \quad
        2 \mathbf{e}_{423} - 3 \mathbf{e}_{431}
        + 5 \mathbf{e}_{412} + 7 \mathbf{e}_{321}
        """,
    ),
    testcase(
        FACADE_RGA,
        r"""
        P^{\text{★}} + P^{\text{☆}}
        \quad = \quad
        2 \mathbf{e}_{423} - 3 \mathbf{e}_{431}
        + 5 \mathbf{e}_{412} + 7 \mathbf{e}_{321}
        """,
    ),
)
def test_rga_bulk_and_weight_duals_reconstruct_the_complementary_plane(
    context: ExpressionContext,
) -> Any:
    """Use the complete source-table point from core/test_metric_rga.py."""
    e1, e2, e3, e4 = context.basis_vectors()
    point = context.named(2 * e1 - 3 * e2 + 5 * e3 + 7 * e4, "P")
    return context.call("right_hodge_dual", point) + context.call(
        "right_weight_dual",
        point,
    )


def _rga_demo_bivectors(context: ExpressionContext) -> tuple[Any, Any]:
    e1, e2, e3, e4 = context.basis_vectors()
    left = context.named((e2 ^ e3) + 2 * (e3 ^ e1) + (e4 ^ e1), "A")
    right = context.named((e1 ^ e2) - (e3 ^ e1) + 3 * (e4 ^ e2), "B")
    return left, right


@latex_test(
    testcase(
        LEGACY_RGA,
        r"""
        A \mathbin{\underset{0}{\text{⩓}}} B
        + A \mathbin{\underset{1}{\text{⩓}}} B
        - A \mathbin{\underset{2}{\text{⩓}}} B
        \quad = \quad
        2 - 2 \mathbf{e}_{23} + \mathbf{e}_{31} + \mathbf{e}_{12}
        + \mathbf{e}_{42} - 2 \mathbf{e}_{43} - 6 \text{𝟙}
        """,
    ),
    testcase(
        FACADE_RGA,
        r"""
        A \mathbin{\underset{0}{\text{⩓}}} B
        + A \mathbin{\underset{1}{\text{⩓}}} B
        - A \mathbin{\underset{2}{\text{⩓}}} B
        \quad = \quad
        2 - 2 \mathbf{e}_{23} + \mathbf{e}_{31} + \mathbf{e}_{12}
        + \mathbf{e}_{42} - 2 \mathbf{e}_{43} - 6 \text{𝟙}
        """,
    ),
)
def test_rga_transwedge_orders_reconstruct_the_geometric_product(
    context: ExpressionContext,
) -> Any:
    """From the transwedge section of examples/rga/rga_demo.py."""
    left, right = _rga_demo_bivectors(context)
    return (
        context.call("transwedge", left, right, 0)
        + context.call("transwedge", left, right, 1)
        - context.call("transwedge", left, right, 2)
    )


@latex_test(
    testcase(
        LEGACY_RGA,
        r"""
        A \mathbin{\underset{0}{\text{⩔}}} B
        + A \mathbin{\underset{1}{\text{⩔}}} B
        - A \mathbin{\underset{2}{\text{⩔}}} B
        \quad = \quad
        -6 - \mathbf{e}_{31} + 2 \mathbf{e}_{12} + 3 \mathbf{e}_{43}
        """,
    ),
    testcase(
        FACADE_RGA,
        r"""
        A \mathbin{\underset{0}{\text{⩔}}} B
        + A \mathbin{\underset{1}{\text{⩔}}} B
        - A \mathbin{\underset{2}{\text{⩔}}} B
        \quad = \quad
        -6 - \mathbf{e}_{31} + 2 \mathbf{e}_{12} + 3 \mathbf{e}_{43}
        """,
    ),
)
def test_rga_transwedge_antiproduct_orders_reconstruct_the_antiproduct(
    context: ExpressionContext,
) -> Any:
    """From the transwedge-antiproduct section of the RGA demo."""
    left, right = _rga_demo_bivectors(context)
    return (
        context.call("transwedge_antiproduct", left, right, 0)
        + context.call("transwedge_antiproduct", left, right, 1)
        - context.call("transwedge_antiproduct", left, right, 2)
    )


@latex_test(
    testcase(
        LEGACY_RGA,
        r"""
        \utilde{\overline{\vphantom{Aft^6}u} \vee \overline{\vphantom{Aft^6}v}}
        \quad = \quad
        \mathbf{e}_{23} - \mathbf{e}_{31} + \mathbf{e}_{12}
        + 2 \mathbf{e}_{41} - \mathbf{e}_{42} - 3 \mathbf{e}_{43}
        """,
    ),
    testcase(
        FACADE_RGA,
        r"""
        \utilde{\overline{u} \vee \overline{v}}
        \quad = \quad
        \mathbf{e}_{23} - \mathbf{e}_{31} + \mathbf{e}_{12}
        + 2 \mathbf{e}_{41} - \mathbf{e}_{42} - 3 \mathbf{e}_{43}
        """,
    ),
)
def test_rga_nested_complements_meet_and_antireverse_remain_legible(
    context: ExpressionContext,
) -> Any:
    """From the reversed-join identity in core/test_metric_rga.py."""
    e1, e2, e3, e4 = context.basis_vectors()
    left = context.named(e1 + 2 * e2 + e4, "u")
    right = context.named(e1 - e2 + e3, "v")
    meet = context.call(
        "antiwedge",
        context.call("right_complement", left),
        context.call("right_complement", right),
    )
    return context.call("antireverse", meet)
