"""Execute convention lessons under every control choice and check the algebra."""

import re
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from tools.migrate_v2_notebooks import migrated_notebook_paths

from galaga import dual, outer_product, scalar_product
from galaga.display import emit
from galaga.rendering import GradeColor

ROOT = Path(__file__).resolve().parents[4]
LESSON = ROOT / "examples/cga/basis_order_and_orientation.py"
pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook t-strings require Python 3.14")


@pytest.fixture(
    scope="module",
    params=[
        (dimension, order, display)
        for dimension in (2, 3)
        for order in ("origin-first", "euclidean-first")
        for display in ("grade-lexicographic", "native-mask")
    ],
)
def lesson(request):
    pytest.importorskip("marimo")
    dimension, order, display = request.param
    outputs, values = runpy.run_path(str(LESSON))["app"].run(
        defs={
            "dimension_control": SimpleNamespace(value=dimension),
            "order_control": SimpleNamespace(value=order),
            "display_control": SimpleNamespace(value=display),
        }
    )
    return outputs, values, dimension, order


def test_orientation_lesson_is_in_executable_gallery():
    assert LESSON in migrated_notebook_paths(ROOT)


def test_native_volume_and_display_claims_are_computed(lesson):
    _, values, dimension, order = lesson
    algebra, model = values["algebra"], values["model"]
    computed = outer_product(model.origin, *model.euclidean_basis_vectors(), model.infinity)
    assert computed == values["conformal_volume"]
    assert values["orientation_ratio"] == (1 if order == "origin-first" else (-1) ** dimension)
    assert computed == values["orientation_ratio"] * algebra.I
    natural, storage = values["natural_display_value"], values["storage_display_value"]
    np.testing.assert_array_equal(natural.data, storage.data)
    assert dual(natural) == dual(storage)
    assert values["origin_axis_blade"] == model.origin ^ model.euclidean_basis_vectors()[0]


def test_conversion_is_an_exterior_map_not_a_coefficient_copy(lesson):
    _, values, _, _ = lesson
    transform = values["exterior_map"]
    np.testing.assert_array_equal(transform.T @ transform, np.eye(len(transform)))
    assert values["converted_mixed"] == values["other_mixed"]
    assert values["copied_mixed"] != values["other_mixed"]
    assert values["conversion_residual"] == 0
    for name, other_name in (("flat", "other_flat"), ("round_blade", "other_round")):
        source, target = values[name], values[other_name]
        np.testing.assert_array_equal(transform @ source.data, target.data)
        np.testing.assert_array_equal(
            transform @ dual(source).data, (values["orientation_map_factor"] * dual(target)).data
        )


def test_signed_normals_and_spheres_not_just_projective_loci(lesson):
    _, values, dimension, order = lesson
    # Explicit analytic signed oracles for the stated point order.
    native_sign = 1 if order == "origin-first" else (-1) ** dimension
    assert values["flat_dual_factor"] == (-1) ** dimension * native_sign
    assert values["flat_hodge_factor"] == native_sign
    assert values["round_dual_factor"] == 2 * native_sign
    assert values["round_hodge_factor"] == 2 * (-1) ** dimension * native_sign
    assert values["signed_probe"] == values["flat_dual_factor"]
    model = values["model"]
    normal = model.euclidean_basis_vectors()[-1]
    assert values["flat_dual"] == values["flat_dual_factor"] * normal
    assert values["round_dual"] == values["round_dual_factor"] * values["normalized_sphere"]
    for name in ("flat_dual", "flat_hodge"):
        assert scalar_product(model.origin, values[name]) == 0
    for point in (*model.euclidean_basis_vectors(), -model.euclidean_basis_vectors()[0]):
        assert scalar_product(model.up(point), values["round_dual"]) == 0


def test_tables_use_computed_products_in_the_stated_axis_order(lesson):
    _, values, _, _ = lesson
    algebra = values["table_algebra"]
    for table, masks in (
        (values["vector_table"], tuple(1 << i for i in range(algebra.n))),
        (values["full_table"], algebra.display_order),
    ):
        for i, left in enumerate(masks):
            assert emit(table.tree.headings[i], "latex") == algebra.blade(left).latex(content="value")
            for j, right in enumerate(masks):
                cell = table.tree.rows[i][j]
                body = cell.body if isinstance(cell, GradeColor) else cell
                assert emit(body, "latex") == (algebra.blade(left) ^ algebra.blade(right)).latex(content="value")


def test_equations_do_not_contain_nested_delimiters_or_literal_interpolations(lesson):
    outputs, _, _, _ = lesson
    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    assert "<pre>" not in markup
    equations = re.findall(r"<marimo-tex[^>]*>(.*?)</marimo-tex>", markup, flags=re.S)
    assert equations
    assert all("$" not in equation for equation in equations)
    assert "{conformal_volume" not in markup and "{flat_dual" not in markup


def test_foundations_lesson_compares_three_computed_orientations():
    pytest.importorskip("marimo")
    outputs, values = runpy.run_path(str(ROOT / "examples/cga/native_null_foundations.py"))["app"].run()
    assert values["conformal_volume"] == values["algebra"].I
    assert values["compatibility_orientation"] == -1
    assert values["orthogonal_orientation"] == 1
    assert values["null_plane"] == values["cga"].origin ^ values["cga"].infinity
    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    assert "<pre>" not in markup
    equations = re.findall(r"<marimo-tex[^>]*>(.*?)</marimo-tex>", markup, flags=re.S)
    assert all("$" not in equation for equation in equations)


@pytest.mark.parametrize("dimension", (2, 3))
@pytest.mark.parametrize("order", ("origin-first", "euclidean-first"))
@pytest.mark.parametrize("model_names", (False, True))
@pytest.mark.parametrize("null_name", (False, True))
@pytest.mark.parametrize("pss", ("Automatic", "I", "J"))
def test_naming_controls_keep_exact_signs_bindings_and_readable_equations(
    dimension, order, model_names, null_name, pss
):
    pytest.importorskip("marimo")
    outputs, values = runpy.run_path(str(LESSON))["app"].run(
        defs={
            "dimension_control": SimpleNamespace(value=dimension),
            "order_control": SimpleNamespace(value=order),
            "display_control": SimpleNamespace(value="grade-lexicographic"),
            "model_names_control": SimpleNamespace(value=model_names),
            "null_name_control": SimpleNamespace(value=null_name),
            "pss_control": SimpleNamespace(value=pss),
        }
    )
    algebra = values["naming_algebra"]
    ie, ic, plane = (values[key] for key in ("named_euclidean_volume", "named_conformal_volume", "named_null_plane"))
    assert ie ^ plane == (-1) ** dimension * ic == values["named_volume_product"]
    assert ic ^ ie == 0
    assert algebra.blade("I") == algebra.I
    if model_names:
        assert algebra.blade("IE") == algebra.blade("I_E") == ie
        assert algebra.blade("IC") == algebra.blade("I_C") == ic
        assert algebra.locals()["IE"] == ie
        if pss == "Automatic":
            assert algebra.locals()["IC"] == ic
        else:
            assert "IC" not in algebra.locals()
    if null_name:
        assert algebra.blade("E") == plane
        assert algebra.locals()["E"] == plane
    if pss != "Automatic":
        assert algebra.I.latex(content="value") == pss
        assert algebra.locals()[pss] == algebra.I
    small = values["naming_small_algebra"]
    assert small.blade("e1").latex(content="value") == r"e_{1}"
    assert "e1" in small.locals() and not {"IE", "I_E"} & small.locals().keys()
    if model_names:
        assert small.blade("IE") == small.blade("e1")
    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    assert "<pre>" not in markup
    equations = re.findall(r"<marimo-tex[^>]*>(.*?)</marimo-tex>", markup, flags=re.S)
    assert all("$" not in equation for equation in equations)
