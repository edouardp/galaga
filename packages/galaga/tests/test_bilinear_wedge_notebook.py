"""Execute the table lesson and verify its displayed claims against the algebra."""

import re
import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

from galaga.display import emit
from galaga.rendering import GradeColor

ROOT = Path(__file__).resolve().parents[3]
pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="Notebook t-strings require Python 3.14")


@pytest.fixture(
    scope="module",
    params=[
        (-0.9, "Euclidean", False),
        (0.0, "STA", True),
        (0.5, "PGA", False),
        (0.9, "CGA", True),
        (-0.5, "RGA", True),
        (0.5, "Complex", True),
    ],
)
def lesson(request):
    pytest.importorskip("marimo")
    pairing, geometry, full = request.param
    with pytest.MonkeyPatch.context() as patch:
        patch.syspath_prepend(str(ROOT / "packages/galaga_marimo"))
        app = runpy.run_path(str(ROOT / "examples/galaga_v2/bilinear_and_wedge_tables.py"))["app"]
        outputs, definitions = app.run(
            defs={
                "metric_slider": SimpleNamespace(value=pairing),
                "geometry_selector": SimpleNamespace(value=geometry),
                "full_toggle": SimpleNamespace(value=full),
            }
        )
    return outputs, definitions, full


def test_coordinate_pairing_and_geometric_decomposition_follow_slider(lesson):
    _, values, _ = lesson
    a, b = values["vector_a"], values["vector_b"]
    symmetric = (a * b + b * a) / 2
    assert float(symmetric) == pytest.approx(values["coordinate_pairing"])
    assert float(symmetric) == pytest.approx(float(values["algebra_pairing"]))
    assert values["algebra_pairing"].expr.operation_id == "metric_inner_product"
    assert values["symmetric_part"].expr.operation_id == "scalar_product"
    x, z = values["e1"], values["e3"]
    np.testing.assert_allclose(values["wedge"].data, ((x * z - z * x) / 2).data, atol=1e-12)
    np.testing.assert_allclose(values["geometric"].data, (values["symmetric_part"] + values["wedge"]).data, atol=1e-12)
    assert values["wedge_table"].latex() == values["euclidean"].wedge_product_table(colour=True).latex()


def test_bivector_pairings_follow_reversion_and_restricted_metric(lesson):
    _, values, _ = lesson
    blade = values["pairing_blade"]
    scalar = values["blade_scalar_pairing"]
    metric = values["blade_metric_pairing"]
    assert scalar.expr.operation_id == "scalar_product"
    assert metric.expr.operation_id == "metric_inner_product"
    np.testing.assert_allclose(scalar.data, (blade * blade).data, atol=1e-12)
    np.testing.assert_allclose(metric.data, (blade * ~blade).data, atol=1e-12)
    gram = values["oblique"].gram
    expected = gram[0, 0] * gram[2, 2] - gram[0, 2] * gram[2, 0]
    assert float(metric) == pytest.approx(expected)
    assert values["restricted_determinant"] == pytest.approx(expected)
    assert float(scalar) == pytest.approx(-expected)


def test_full_table_and_selected_table_entries_match_native_products(lesson):
    _, values, selected_full = lesson
    for algebra, table, full in (
        (values["euclidean"], values["full_wedge"], True),
        (values["selected_algebra"], values["selected_wedge"], selected_full),
    ):
        masks = (
            sorted(range(algebra.dim), key=lambda m: (m.bit_count(), m))
            if full
            else [1 << index for index in range(algebra.n)]
        )
        assert len(table.tree.headings) == len(masks)
        for row, left in zip(table.tree.rows, masks, strict=True):
            for cell, right in zip(row, masks, strict=True):
                body = cell.body if isinstance(cell, GradeColor) else cell
                product = algebra.blade(left) ^ algebra.blade(right)
                assert emit(body, "latex") == product.latex(content="value")
    assert values["vector_bivector"] == values["bivector_vector"]
    assert np.count_nonzero(values["vector_bivector"].data) == 1


def test_null_vector_lesson_renders_scalars_without_nested_delimiters(lesson):
    outputs, values, _ = lesson
    assert values["pga_rank"] < values["pga"].n
    assert values["cga_rank"] == values["cga"].n
    assert float(values["null_origin_square"]) == float(values["null_infinity_square"]) == 0
    assert float(values["null_pair_product"]) != 0
    markup = "\n".join(getattr(output, "text", "") for output in outputs)
    assert "<pre>" not in markup, "Lesson prose or equations were rendered as an indented code block"
    equations = re.findall(r"<marimo-tex[^>]*>(.*?)</marimo-tex>", markup, flags=re.S)
    null_equation = next("".join(equation.split()) for equation in equations if "e_o^2" in equation)
    assert "$" not in null_equation
    assert "e_o^2=0" in null_equation
    assert r"e_\infty^2=0" in null_equation
    assert r"e_o\cdote_\infty=-1" in null_equation
