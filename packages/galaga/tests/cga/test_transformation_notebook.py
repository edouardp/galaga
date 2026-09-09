"""The Lengyel teaching notebook renders its computed Euclidean lowering."""

import runpy
import sys
from pathlib import Path

import numpy as np
import pytest

import galaga as ga


@pytest.mark.skipif(sys.version_info < (3, 14), reason="notebook uses Python 3.14 t-strings")
def test_antiproduct_translation_displays_the_computed_lowered_point():
    path = Path(__file__).parents[4] / "examples/cga/lengyel_cga_transformations.py"
    outputs, definitions = runpy.run_path(str(path))["app"].run()
    cga = definitions["cga"]
    point = definitions["translated_by_antiproduct"]
    source = definitions["source_point"]
    e1 = definitions["e1"]
    # Compare with the independently constructed geometric-product action,
    # deriving its normalization from the model's actual null pairing.
    pairing = float(ga.scalar_product(cga.origin, cga.infinity))
    translator = ga.exp((e1 ^ cga.infinity) / (2 * pairing))
    expected = ga.sandwich(translator, source)
    np.testing.assert_allclose(point.data, expected.data, rtol=0, atol=1e-12)
    lowered = cga.down(point)
    np.testing.assert_allclose(lowered.data, (cga.down(source) + e1).data, rtol=0, atol=1e-12)
    markup = next(
        output.text
        for output in outputs
        if "Lowering the translated point gives its Euclidean vector" in getattr(output, "text", "")
    )
    assert lowered.latex(content="value") in markup
    assert r"\operatorname{down}(P^{\prime})" in markup
    assert "{cga.down" not in markup
