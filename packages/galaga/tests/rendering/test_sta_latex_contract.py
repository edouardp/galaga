"""Exact full-LaTeX contracts derived from maintained STA notebooks."""

from __future__ import annotations

from typing import Any

from tools.latex_contract import latex_test, testcase
from tools.rendering_contract import ExpressionContext


@latex_test(
    testcase(
        "legacy-v1/sta-mostly-minus/full-default",
        r"F^2 \quad = \quad 0.8",
    ),
    testcase(
        "core-facade-v2/sta-mostly-minus/full-default",
        r"F^2 \quad = \quad 0.8",
    ),
)
def test_sta_field_square_expression(context: ExpressionContext) -> Any:
    """From examples/spacetime/electromagnetism_lazy.py."""
    g0, g1, g2, _ = context.basis_vectors()
    electric = context.named(1.2 * (g1 * g0) + 0 * (g2 * g0), "E")
    magnetic = context.named(0.8 * (g1 * g2), "B")
    field = context.named(electric + magnetic, "F")
    return field**2


@latex_test(
    testcase(
        "legacy-v1/sta-mostly-minus/full-default",
        r"k_+^2 \quad = \quad k_+ k_+ \quad = \quad 0",
    ),
    testcase(
        "core-facade-v2/sta-mostly-minus/full-default",
        r"k_+^2 \quad = \quad k_+ k_+ \quad = \quad 0",
    ),
)
def test_sta_null_vector_square(context: ExpressionContext) -> Any:
    """From examples/spacetime/null_geometry_sta.py."""
    g0, g1, _, _ = context.basis_vectors()
    k_plus = context.named(g0 + g1, "k_plus", latex=r"k_+")
    return context.named(k_plus * k_plus, "k_plus_squared", latex=r"k_+^2")


@latex_test(
    testcase(
        "legacy-v1/sta-mostly-minus/full-default",
        r"""
        F \quad = \quad E + B \quad = \quad
        -1.2 \gamma_{0} \gamma_{1} + 0.8 \gamma_{1} \gamma_{2}
        """,
    ),
    testcase(
        "core-facade-v2/sta-mostly-minus/full-default",
        r"""
        F \quad = \quad E + B \quad = \quad
        -1.2 \gamma_{0} \gamma_{1} + 0.8 \gamma_{1} \gamma_{2}
        """,
    ),
)
def test_sta_faraday_bivector_assembly(context: ExpressionContext) -> Any:
    """From examples/spacetime/electromagnetism_lazy.py."""
    g0, g1, g2, _ = context.basis_vectors()
    electric = context.named(1.2 * (g1 * g0), "E")
    magnetic = context.named(0.8 * (g1 * g2), "B")
    return context.named(electric + magnetic, "F")


@latex_test(
    testcase(
        "legacy-v1/sta-mostly-minus/full-default",
        r"""
        \gamma_0' \quad = \quad \Lambda \gamma_{0} \tilde{\Lambda}
        \quad = \quad
        1.18547 \gamma_{0} - 0.636654 \gamma_{1}
        """,
    ),
    testcase(
        "core-facade-v2/sta-mostly-minus/full-default",
        r"""
        \gamma_0' \quad = \quad \Lambda \gamma_{0} \widetilde{\Lambda}
        \quad = \quad
        1.18547 \gamma_{0} - 0.636654 \gamma_{1}
        """,
    ),
)
def test_sta_boosted_time_axis(context: ExpressionContext) -> Any:
    """From examples/physics/special_relativity_lazy.py."""
    g0, g1, _, _ = context.basis_vectors()
    boost_plane = context.named(g0 * g1, "B_x", latex=r"B_x")
    rotor = context.named(context.call("exp", 0.3 * boost_plane), "Lambda", latex=r"\Lambda")
    return context.named(
        context.call("sandwich", rotor, g0),
        "boosted_g0",
        latex=r"\gamma_0'",
    )


@latex_test(
    testcase(
        "legacy-v1/sta-mostly-minus/full-default",
        r"I B_t \quad = \quad \gamma_{2} \gamma_{3}",
    ),
    testcase(
        "core-facade-v2/sta-mostly-minus/full-default",
        r"I B_t \quad = \quad \gamma_{2} \gamma_{3}",
    ),
)
def test_sta_pseudoscalar_times_timelike_plane(context: ExpressionContext) -> Any:
    """From galaga-marimo-demos/notebooks/sta/pseudoscalar_complex_structure.py."""
    g0, g1, g2, g3 = context.basis_vectors()
    pseudoscalar = context.named(g0 * g1 * g2 * g3, "I")
    timelike_plane = context.named(g0 * g1, "B_t", latex=r"B_t")
    return context.named(pseudoscalar * timelike_plane, "IB_t", latex=r"I B_t")


@latex_test(
    testcase(
        "legacy-v1/sta-mostly-minus/full-default",
        r"M^2 \quad = \quad 2 i",
    ),
    testcase(
        "core-facade-v2/sta-mostly-minus/full-default",
        r"M^2 \quad = \quad 2 i",
    ),
)
def test_sta_mixed_bivector_square(context: ExpressionContext) -> Any:
    """From galaga-marimo-demos/notebooks/sta/pseudoscalar_complex_structure.py."""
    g0, g1, g2, g3 = context.basis_vectors()
    timelike_plane = context.named(g0 * g1, "B_t", latex=r"B_t")
    spacelike_plane = context.named(g2 * g3, "B_s", latex=r"B_s")
    mixed = context.named(timelike_plane + spacelike_plane, "M")
    return context.named(mixed**2, "M_squared", latex=r"M^2")


@latex_test(
    testcase(
        "legacy-v1/sta-mostly-minus/full-default",
        r"""
        \langle F^2 \rangle_4 \quad = \quad
        \langle F^2 \rangle_{4} \quad = \quad 1.92 i
        """,
    ),
    testcase(
        "core-facade-v2/sta-mostly-minus/full-default",
        r"""
        \langle F^2 \rangle_4 \quad = \quad
        \langle F^2 \rangle_{4} \quad = \quad 1.92 i
        """,
    ),
)
def test_sta_parallel_field_pseudoscalar_invariant(context: ExpressionContext) -> Any:
    """From galaga-marimo-demos/notebooks/sta/em_invariants.py."""
    g0, g1, g2, g3 = context.basis_vectors()
    pseudoscalar = context.named(g0 * g1 * g2 * g3, "I")
    sigma1 = context.named(g1 * g0, "sigma_1", latex=r"\sigma_1")
    electric = context.named(1.2 * sigma1, "E")
    magnetic = context.named(0.8 * sigma1, "B")
    field = context.named(electric + pseudoscalar * magnetic, "F")
    field_square = context.named(field**2, "F_squared", latex=r"F^2")
    return context.named(
        context.call("grade", field_square, 4),
        "F2_grade4",
        latex=r"\langle F^2 \rangle_4",
    )


@latex_test(
    testcase(
        "legacy-v1/sta-mostly-minus/full-default",
        r"""
        R \quad = \quad R_y R_x \quad = \quad
        1.17122 + 0.39397 \gamma_{0} \gamma_{1}
        + 0.494136 \gamma_{0} \gamma_{2}
        + 0.166215 \gamma_{1} \gamma_{2}
        """,
    ),
    testcase(
        "core-facade-v2/sta-mostly-minus/full-default",
        r"""
        R \quad = \quad R_y R_x \quad = \quad
        1.17122 + 0.39397 \gamma_{0} \gamma_{1}
        + 0.494136 \gamma_{0} \gamma_{2}
        + 0.166215 \gamma_{1} \gamma_{2}
        """,
    ),
)
def test_sta_noncollinear_boost_composition(context: ExpressionContext) -> Any:
    """From galaga-marimo-demos/notebooks/sta/thomas_wigner_rotation.py."""
    g0, g1, g2, _ = context.basis_vectors()
    boost_x = context.named(g0 * g1, "B_x", latex=r"B_x")
    boost_y = context.named(g0 * g2, "B_y", latex=r"B_y")
    rotor_x = context.named(context.call("exp", 0.35 * boost_x), "R_x", latex=r"R_x")
    rotor_y = context.named(context.call("exp", 0.45 * boost_y), "R_y", latex=r"R_y")
    return context.named(rotor_y * rotor_x, "R")


@latex_test(
    testcase(
        "legacy-v1/sta-mostly-minus/full-default",
        r"""
        u \quad = \quad R \gamma_{0} \tilde{R} \quad = \quad
        1.79877 \gamma_{0} - 0.758584 \gamma_{1} - 1.28845 \gamma_{2}
        """,
    ),
    testcase(
        "core-facade-v2/sta-mostly-minus/full-default",
        r"""
        u \quad = \quad R \gamma_{0} \widetilde{R} \quad = \quad
        1.79877 \gamma_{0} - 0.758584 \gamma_{1} - 1.28845 \gamma_{2}
        """,
    ),
)
def test_sta_noncollinear_boosted_time_axis(context: ExpressionContext) -> Any:
    """From galaga-marimo-demos/notebooks/sta/thomas_wigner_rotation.py."""
    g0, g1, g2, _ = context.basis_vectors()
    boost_x = context.named(g0 * g1, "B_x", latex=r"B_x")
    boost_y = context.named(g0 * g2, "B_y", latex=r"B_y")
    rotor_x = context.named(context.call("exp", 0.35 * boost_x), "R_x", latex=r"R_x")
    rotor_y = context.named(context.call("exp", 0.45 * boost_y), "R_y", latex=r"R_y")
    rotor = context.named(rotor_y * rotor_x, "R")
    return context.named(context.call("sandwich", rotor, g0), "u")
