"""Notebook-ready operation-notation overview for an algebra."""

import inspect

import pytest

from galaga import Algebra, Name, RenderRule, presets, right_hodge_dual
from galaga.facade.catalog import OPERATIONS


def test_show_presentation_compact_view_uses_actual_basis_and_custom_rules():
    right_star = RenderRule(
        "prefix",
        symbol=Name("star_R", "★ᴿ", r"\mathord{\stackrel{\mathrm R}{\star}}"),
    )
    algebra = Algebra(
        config=presets.euclidean(3),
        expr=True,
        presentation=(
            presets.notation.override(left_hodge_dual=r"prefix:\star")
            | presets.notation.override(right_hodge_dual=right_star)
        ),
        user_config_files=False,
    )

    table = algebra.show_presentation()

    assert tuple(row[0] for row in table.rows) == ("left_hodge_dual", "right_hodge_dual")
    assert r"\begin{array}{l|ll}" in table.latex()
    assert (
        r"\texttt{left\_hodge\_dual} & \star e_{1} & "
        r"\star \left(e_{1} \wedge e_{2}\right)"
    ) in table.latex()
    assert r"\texttt{right\_hodge\_dual} & " in table.latex()
    assert r"\mathord{\stackrel{\mathrm R}{\star}}e_{1}" in table.latex()
    assert right_hodge_dual(algebra.basis_vectors()[0]).latex(content="expr") == table.rows[1][3][0]
    assert table._repr_latex_() == f"$${table.latex()}$$"
    assert "★ᴿe₁" in table.unicode()
    assert "Operation | Example 1 | Example 2" in table.unicode()


def test_show_presentation_selects_grade_and_scalar_examples_for_catalog_operations():
    algebra = Algebra(config=presets.euclidean(3), user_config_files=False)
    rows = {name: latex for name, _ascii, _unicode, latex in algebra.show_presentation(all=True).rows}

    assert r"e_{1} \wedge e_{2}" in rows["left_hodge_dual"][1]
    assert r"e_{1} \wedge e_{2}" in rows["left_contraction"][0]
    assert r"e_{1} \wedge e_{2}" in rows["right_contraction"][0]
    assert rows["power"] == (r"e_{1}^2", r"\left(e_{1} \wedge e_{2}\right)^3")
    assert rows["scalar_sqrt"] == (r"\sqrt{2}", r"\sqrt{3}")
    assert r"\operatorname{rotor\_generator}" in rows["rotor_generator"][0]
    assert r"e^{e_{1} \wedge e_{2}}" in rows["rotor_generator"][0]
    assert "is_bivector" not in rows
    for operation_id in ("transwedge", "transwedge_antiproduct"):
        assert rows[operation_id][0].endswith(r",\, 1)")
        assert rows[operation_id][1].endswith(r",\, 2)")


def test_show_presentation_distinguishes_lengyel_interior_products_from_contractions():
    algebra = Algebra(config=presets.rga(), user_config_files=False)
    rows = {name: latex for name, _ascii, _unicode, latex in algebra.show_presentation(all=True).rows}

    for side in ("left", "right"):
        assert rows[f"{side}_interior_product"][0].startswith(rf"\operatorname{{{side}\_interior\_product}}(")
        assert rows[f"{side}_interior_product"] != rows[f"{side}_contraction"]


def test_show_presentation_can_use_symbolic_abc_examples_instead_of_basis_blades():
    algebra = Algebra(
        config=presets.euclidean(3),
        presentation=presets.notation.override(left_hodge_dual="prefix:star"),
        user_config_files=False,
    )

    compact = algebra.show_presentation(basis=False)
    rows = {name: latex for name, _ascii, _unicode, latex in algebra.show_presentation(all=True, basis=False).rows}

    assert r"\texttt{left\_hodge\_dual} & \star A & \star \left(A \wedge B\right)" in compact.latex()
    assert "e_{1}" not in compact.latex()
    assert rows["geometric_product"] == ("A B", r"\left(A \wedge B\right) C")
    assert rows["power"] == ("A^2", r"\left(A \wedge B\right)^3")
    assert rows["sandwich"] == (
        r"R A \widetilde{R}",
        r"\left(A B\right) C \left(\widetilde{A B}\right)",
    )
    assert rows["scalar_sqrt"] == (r"\sqrt{A}", r"\sqrt{B}")
    with pytest.raises(TypeError, match="basis must be a boolean"):
        algebra.show_presentation(basis=1)  # type: ignore[arg-type]


def test_show_presentation_all_covers_every_catalog_operation_and_validates_flag():
    algebra = Algebra(config=presets.euclidean(2), user_config_files=False)

    empty = algebra.show_presentation()
    assert empty.rows == ()
    assert "because all=False" in empty.unicode()
    assert "alg.show_presentation(all=True)" in empty.ascii()
    assert r"\texttt{alg.show\_presentation(all=True)}" in empty.latex()
    assert tuple(row[0] for row in algebra.show_presentation(all=True).rows) == tuple(
        name for name, operation in OPERATIONS.items() if operation.result_kind != "predicate"
    )
    with pytest.raises(TypeError, match="all must be a boolean"):
        algebra.show_presentation(all=1)  # type: ignore[arg-type]


def test_notation_override_signature_lists_every_catalog_operation_for_autocomplete():
    parameters = set(inspect.signature(presets.notation.override).parameters)
    controls = {"rules", "ascii", "unicode", "latex", "operations"}

    assert parameters - controls == set(OPERATIONS)
