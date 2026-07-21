"""Build conformal geometry directly in a native eo/einf Gram basis."""

from __future__ import annotations

import numpy as np

from galaga.cga import ConformalModel
from galaga.facade import Algebra, exp, outer_product, p_cga, sandwich, scalar_product


def run() -> None:
    algebra = Algebra(config=p_cga(spatial_dim=3))
    cga = ConformalModel(algebra)

    assert cga.null_pair == -1
    assert float(cga.origin * cga.origin) == 0
    assert float(cga.infinity * cga.infinity) == 0

    a = cga.round_point((0.0, 0.0, 0.0))
    b = cga.round_point((1.0, 0.0, 0.0))
    c = cga.round_point((0.0, 1.0, 0.0))
    line_ab = outer_product(a, b, cga.infinity)
    circle_abc = outer_product(a, b, c)
    plane_abc = outer_product(a, b, c, cga.infinity)

    assert line_ab.homogeneous_grade() == circle_abc.homogeneous_grade() == 3
    assert plane_abc.homogeneous_grade() == 4
    assert cga.car(circle_abc) == plane_abc
    assert cga.ccr(circle_abc).homogeneous_grade() == 3

    point = cga.round_point((0.25, 0.5, 2.0))
    projected = cga.project(point, plane_abc)
    np.testing.assert_allclose(cga.coordinates(projected), (0.25, 0.5, 0.0), rtol=0.0, atol=1e-12)
    assert float(cga.radius_squared(projected)) == 4

    displacement = cga.euclidean_vector((2.0, -1.0, 0.5))
    translator = exp(-0.5 * displacement * cga.infinity)
    translated = sandwich(translator, point)
    np.testing.assert_allclose(cga.coordinates(translated), (2.25, -0.5, 2.5), rtol=0.0, atol=1e-12)

    expected_distance_squared = float(np.dot(displacement.data, displacement.data))
    translated_origin = sandwich(translator, a)
    assert float(scalar_product(a, translated_origin)) == -0.5 * expected_distance_squared


if __name__ == "__main__":
    run()
