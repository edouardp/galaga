from __future__ import annotations

import numpy as np
import pytest

from galaga import Algebra, AlgebraConfig, AlgebraDefinition, p_cga, squared
from galaga.cga import ConformalModel


def test_model_exposes_actual_native_null_basis_vectors_and_euclidean_roles() -> None:
    algebra = Algebra(config=p_cga(spatial_dim=3))
    cga = ConformalModel(algebra)
    e1, e2, e3 = cga.euclidean_basis_vectors()

    assert cga.algebra is algebra
    assert cga.spatial_dim == 3
    assert cga.null_pair == -1
    assert cga.origin == algebra.basis_vectors()[3]
    assert cga.infinity == algebra.basis_vectors()[4]
    assert float(squared(cga.origin)) == 0
    assert float(squared(cga.infinity)) == 0
    np.testing.assert_array_equal([e1.data, e2.data, e3.data], [value.data for value in algebra.basis_vectors()[:3]])


@pytest.mark.parametrize("null_pair", (-2.0, -1.0, -0.5, 0.75))
def test_round_point_formula_respects_any_nonzero_null_pair_scaling(null_pair: float) -> None:
    cga = ConformalModel(Algebra(config=p_cga(3, null_pair=null_pair)))

    point = cga.round_point((1.0, -2.0, 0.5))
    round_point = cga.round_point((1.0, -2.0, 0.5), radius_squared=2.25)

    assert float(squared(point)) == pytest.approx(0.0, abs=1e-12)
    assert float(squared(round_point)) == pytest.approx(-2.25, abs=1e-12)
    assert float(cga.weight(point)) == pytest.approx(1.0)
    assert float(cga.radius_squared(round_point)) == pytest.approx(2.25)
    np.testing.assert_allclose(cga.coordinates(point), (1.0, -2.0, 0.5), rtol=0.0, atol=1e-12)


def test_homogenize_down_and_coordinates_are_projectively_invariant() -> None:
    cga = ConformalModel(Algebra(config=p_cga()))
    point = cga.round_point((2.0, -3.0, 4.0), radius_squared=-1.5)

    normalized = cga.homogenize(-7.0 * point)

    assert float(cga.weight(normalized)) == pytest.approx(1.0)
    assert cga.down(normalized) == cga.euclidean_vector((2.0, -3.0, 4.0))
    np.testing.assert_allclose(cga.coordinates(-7.0 * point), (2.0, -3.0, 4.0), rtol=0.0, atol=1e-12)
    assert float(cga.radius_squared(-7.0 * point)) == pytest.approx(-1.5)
    assert not cga.coordinates(point).flags.writeable


def test_model_construction_and_embedding_retain_optional_expression_provenance() -> None:
    cga = ConformalModel(Algebra(config=p_cga()))
    radius_squared = cga.algebra.scalar(4.0).named("r^2")

    position = cga.euclidean_vector((1.0, 2.0, 3.0), expr=True)
    point = cga.round_point(position, radius_squared=radius_squared)

    assert position.expr is not None
    assert point.expr is not None
    assert float(cga.radius_squared(point)) == pytest.approx(4.0)


def test_model_rejects_orthogonal_and_untyped_cl41_algebras() -> None:
    with pytest.raises(ValueError, match="frame='null'"):
        ConformalModel(Algebra(config=p_cga(frame="orthogonal")))
    with pytest.raises(ValueError, match="frame='null'"):
        ConformalModel(Algebra(4, 1))
    with pytest.raises(TypeError, match="galaga Algebra"):
        ConformalModel(object())  # type: ignore[arg-type]


def test_model_validates_the_metric_behind_declared_semantic_roles() -> None:
    config = p_cga(2).build()
    malformed = [list(row) for row in config.definition.gram]
    malformed[0][0] = 2.0
    algebra = Algebra(
        config=AlgebraConfig(
            AlgebraDefinition(malformed, id="malformed-cga"),
            config.presentation,
            config.model,
        )
    )

    with pytest.raises(ValueError, match="identity Gram block"):
        ConformalModel(algebra)


def test_euclidean_vector_rejects_invalid_coordinates_subspaces_and_ownership() -> None:
    cga = ConformalModel(Algebra(config=p_cga()))
    other = ConformalModel(Algebra(config=p_cga()))

    with pytest.raises(ValueError, match="expected 3"):
        cga.euclidean_vector((1.0, 2.0))
    with pytest.raises(TypeError, match="real numbers"):
        cga.euclidean_vector((1.0, "two", 3.0))  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="finite"):
        cga.euclidean_vector((1.0, float("inf"), 3.0))
    with pytest.raises(ValueError, match="Euclidean subspace"):
        cga.euclidean_vector(cga.origin)
    with pytest.raises(ValueError, match="different numeric algebra"):
        cga.euclidean_vector(other.euclidean_basis_vectors()[0])


def test_point_operations_reject_nonvectors_zero_weight_and_invalid_radius() -> None:
    cga = ConformalModel(Algebra(config=p_cga()))
    e1, e2, _ = cga.euclidean_basis_vectors()

    with pytest.raises(ValueError, match="homogeneous conformal vector"):
        cga.weight(e1 ^ e2)
    with pytest.raises(ValueError, match="zero weight"):
        cga.homogenize(cga.infinity)
    with pytest.raises(ValueError, match="no finite round radius"):
        cga.radius_squared(cga.infinity)
    with pytest.raises(ValueError, match="scalar multivector"):
        cga.round_point((0.0, 0.0, 0.0), radius_squared=e1)
    with pytest.raises(TypeError, match="boolean"):
        cga.round_point((0.0, 0.0, 0.0), expr=1)  # type: ignore[arg-type]


def test_partner_rejects_a_nonstandard_null_pair_whose_wiki_polynomial_would_change() -> None:
    cga = ConformalModel(Algebra(config=p_cga(null_pair=-0.5)))

    with pytest.raises(ValueError, match="standard eo·einf"):
        cga.partner(cga.round_point((0.0, 0.0, 0.0), radius_squared=1.0))
