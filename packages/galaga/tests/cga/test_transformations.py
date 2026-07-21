from __future__ import annotations

import math

import numpy as np

from galaga import (
    Algebra,
    antireverse,
    exp,
    geometric_antiproduct,
    p_cga,
    sandwich,
    squared,
)
from galaga.cga import ConformalModel


def _model() -> ConformalModel:
    return ConformalModel(Algebra(config=p_cga()))


def test_translation_is_an_existing_geometric_product_versor_action() -> None:
    cga = _model()
    displacement = cga.euclidean_vector((2.0, -1.0, 0.5))
    point = cga.round_point((1.0, 2.0, 3.0))
    translator = exp(-0.5 * displacement * cga.infinity)

    translated = sandwich(translator, point)

    np.testing.assert_allclose(cga.coordinates(translated), (3.0, 1.0, 3.5), rtol=0.0, atol=1e-12)
    assert abs(float(squared(translated))) < 1e-12


def test_wiki_translation_operator_uses_existing_sandwich_antiproduct_primitives() -> None:
    cga = _model()
    _, e2, e3 = cga.euclidean_basis_vectors()
    point = cga.round_point((1.0, 2.0, 3.0))
    operator = cga.algebra.I + 0.5 * (e2 ^ e3 ^ cga.infinity)

    translated = geometric_antiproduct(
        geometric_antiproduct(operator, point),
        antireverse(operator),
    )

    np.testing.assert_allclose(cga.coordinates(translated), (2.0, 2.0, 3.0), rtol=0.0, atol=1e-12)


def test_rotation_is_an_existing_geometric_product_versor_action() -> None:
    cga = _model()
    e1, e2, _ = cga.euclidean_basis_vectors()
    point = cga.round_point((1.0, 0.0, 0.0))
    rotor = exp(-0.25 * math.pi * (e1 ^ e2))

    rotated = sandwich(rotor, point)

    np.testing.assert_allclose(cga.coordinates(rotated), (0.0, 1.0, 0.0), rtol=0.0, atol=1e-12)


def test_origin_dilation_is_an_existing_geometric_product_versor_action() -> None:
    cga = _model()
    point = cga.round_point((1.0, 2.0, 3.0))
    dilator = exp(0.5 * math.log(2.0) * (cga.origin ^ cga.infinity))

    dilated = sandwich(dilator, point)

    np.testing.assert_allclose(cga.coordinates(dilated), (2.0, 4.0, 6.0), rtol=0.0, atol=1e-12)


def test_transversion_is_an_existing_geometric_product_versor_action() -> None:
    cga = _model()
    parameter = cga.euclidean_vector((0.2, 0.0, 0.0))
    source = np.array((1.0, 2.0, 3.0))
    point = cga.round_point(source)
    transversor = exp(0.5 * parameter * cga.origin)

    transformed = sandwich(transversor, point)

    parameter_coords = np.array((0.2, 0.0, 0.0))
    source_squared = float(np.dot(source, source))
    denominator = (
        1.0
        - float(np.dot(parameter_coords, source))
        + 0.25 * float(np.dot(parameter_coords, parameter_coords)) * source_squared
    )
    expected = (source - 0.5 * parameter_coords * source_squared) / denominator
    np.testing.assert_allclose(cga.coordinates(transformed), expected, rtol=0.0, atol=1e-12)
