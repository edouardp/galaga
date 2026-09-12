"""Native-order changes are exterior basis maps, never rendering sign fixes."""

from __future__ import annotations

import numpy as np
import pytest

from galaga import (
    Algebra,
    DisplayOrder,
    complement,
    dual,
    exp,
    left_hodge_dual,
    outer_product,
    presets,
    right_hodge_dual,
    sandwich,
    scalar_product,
    uncomplement,
    undual,
)
from galaga.blades import null_cga_blade_convention
from galaga.cga import ConformalModel
from galaga.display import emit

ORDERS = ("origin-first", "euclidean-first")


def _exterior_columns(target, images):
    """Compute the exterior extension of the supplied vector correspondence."""
    columns = []
    for mask in range(target.dim):
        blade = target.identity
        for index, image in enumerate(images):
            if mask & (1 << index):
                blade = blade ^ image
        columns.append(blade.data)
    return np.column_stack(columns)


@pytest.mark.parametrize("spatial_dim", (1, 2, 3, 4))
@pytest.mark.parametrize("basis_order", ORDERS)
@pytest.mark.parametrize("null_pair", (-2.0, -1.0, -0.5, 0.75))
def test_sign_consistency_metric_roles_and_semantic_pseudoscalar(spatial_dim, basis_order, null_pair):
    recipe = presets.cga(spatial_dim, basis_order=basis_order, null_pair=null_pair)
    algebra = Algebra(config=recipe)
    model = ConformalModel(algebra)
    spatial = model.euclidean_basis_vectors()
    expected_basis = (
        (model.origin, *spatial, model.infinity)
        if basis_order == "origin-first"
        else (*spatial, model.origin, model.infinity)
    )
    assert algebra.basis_vectors() == expected_basis
    for row, left in enumerate(expected_basis):
        for column, right in enumerate(expected_basis):
            computed = scalar_product(left, right)
            assert float(computed) == algebra.gram[row, column]
            expected = null_pair if {row, column} == {expected_basis.index(model.origin), algebra.n - 1} else 0
            if row == column and left in spatial:
                expected = 1
            assert computed == expected
    ie = outer_product(*spatial)
    ic = model.origin ^ ie ^ model.infinity
    native = outer_product(*expected_basis)
    assert native == algebra.I
    assert ic == (1 if basis_order == "origin-first" else (-1) ** spatial_dim) * native
    assert model.origin * model.origin == model.infinity * model.infinity == 0
    assert ic * ic == native * native
    assert recipe.build() == recipe.build()
    named = Algebra(gram=algebra.gram, blades=presets.blades.cga(spatial_dim, basis_order=basis_order))
    assert named.presentation.blades == algebra.presentation.blades
    np.testing.assert_array_equal(named.gram, algebra.gram)


@pytest.mark.parametrize("spatial_dim", (1, 2, 3, 4))
@pytest.mark.parametrize("null_pair", (-2.0, -1.0, 0.5))
def test_exterior_basis_map_preserves_products_and_exposes_duality_orientation(spatial_dim, null_pair):
    source = Algebra(config=presets.cga(spatial_dim, basis_order="euclidean-first", null_pair=null_pair))
    target = Algebra(config=presets.cga(spatial_dim, null_pair=null_pair))
    old = ConformalModel(source)
    new = ConformalModel(target)
    images = (*new.euclidean_basis_vectors(), new.origin, new.infinity)
    columns = _exterior_columns(target, images)

    def convert(value):
        return target.multivector(columns @ value.data)

    # Derive orientation from the actual mapped native pseudoscalar.
    orientation = float(convert(source.I) / target.I)
    assert orientation == (-1) ** spatial_dim
    np.testing.assert_array_equal(columns.T @ columns, np.eye(source.dim))
    # Every grade, multiplied on either side by every generator.
    for mask in range(source.dim):
        blade = source.blade(mask)
        mapped = convert(blade)
        for vector in source.basis_vectors():
            assert convert(blade * vector) == mapped * convert(vector)
            assert convert(vector * blade) == convert(vector) * mapped
            assert convert(blade ^ vector) == mapped ^ convert(vector)
        for operation in (dual, undual, complement, uncomplement, right_hodge_dual, left_hodge_dual):
            assert convert(operation(blade)).almost_equal(orientation * operation(mapped))
        assert convert(old.dual(blade)).almost_equal(orientation * new.dual(mapped))
        assert convert(old.antidual(blade)).almost_equal(orientation * new.antidual(mapped))
    rng = np.random.default_rng(134)
    left, right = (source.multivector(rng.normal(size=source.dim)) for _ in range(2))
    assert convert(left * right).almost_equal(convert(left) * convert(right), atol=1e-10)
    assert convert(left ^ right).almost_equal(convert(left) ^ convert(right), atol=1e-10)
    point = old.up(tuple(range(1, spatial_dim + 1)))
    assert convert(point) == new.up(tuple(range(1, spatial_dim + 1)))


@pytest.mark.parametrize("basis_order", ORDERS)
def test_signed_opns_ipns_examples_and_translation(basis_order):
    algebra = Algebra(config=presets.cga(2, basis_order=basis_order))
    model = ConformalModel(algebra)
    e1, e2 = model.euclidean_basis_vectors()
    line = model.up(0, 0) ^ model.up(1, 0) ^ model.infinity
    circle = model.up(1, 0) ^ model.up(0, 1) ^ model.up(-1, 0)
    for operation in (dual, right_hodge_dual, model.dual):
        assert operation(line) == e2
        assert operation(circle) == 2 * model.origin - model.infinity
    translated = sandwich(exp(-0.5 * e1 * model.infinity), model.up(0, 2))
    np.testing.assert_allclose(model.coordinates(translated), (1, 2), rtol=0, atol=1e-12)


@pytest.mark.parametrize("spatial_dim", (2, 3))
def test_familiar_orthogonal_realization_derives_the_orientation(spatial_dim):
    algebra = Algebra(config=presets.cga(spatial_dim, frame="orthogonal"))
    *spatial, plus, minus = algebra.basis_vectors()
    origin = (minus - plus) / 2
    infinity = minus + plus
    ie = outer_product(*spatial)
    ic = origin ^ ie ^ infinity
    assert origin * origin == infinity * infinity == 0
    assert scalar_product(origin, infinity) == -1
    assert origin ^ infinity == -(plus ^ minus)
    assert ic == (-1) ** (spatial_dim + 1) * algebra.I
    native = Algebra(config=presets.cga(spatial_dim))
    columns = _exterior_columns(algebra, (origin, *spatial, infinity))
    for mask in range(native.dim):
        value = native.blade(mask)
        for index, vector in enumerate(native.basis_vectors()):
            np.testing.assert_allclose(
                columns @ (value * vector).data,
                (algebra.multivector(columns @ value.data) * algebra.multivector(columns[:, 1 << index])).data,
                rtol=0,
                atol=1e-12,
            )


@pytest.mark.parametrize("basis_order", ORDERS)
def test_display_overrides_do_not_reorient_values_or_tables(basis_order):
    algebra = Algebra(config=presets.cga(3, basis_order=basis_order))
    order = DisplayOrder(5, tuple(reversed(range(32))))
    view = algebra.with_display_order(order)
    assert view.numeric is algebra.numeric
    assert view.I == algebra.I
    assert dual(view.blade("e1")) == dual(algebra.blade("e1"))
    assert view.display_order == order.masks
    assert view.bilinear_form_table() == algebra.bilinear_form_table()
    assert view.wedge_product_table() == algebra.wedge_product_table()
    table = view.wedge_product_table(full=True)
    for index, mask in enumerate(order.masks):
        assert emit(table.tree.headings[index], "ascii") == view.blade(mask).display(target="ascii", content="value")


def test_default_ids_and_protected_lengyel_coordinates():
    default = presets.cga(3).build()
    explicit = presets.cga(3, basis_order="origin-first").build()
    previous = presets.cga(3, basis_order="euclidean-first").build()
    assert default == explicit
    assert default.definition.id == "cga-3d-null-origin-first"
    assert previous.definition.id == "cga-3d-null"
    assert default.model.id == previous.model.id == "cga-null"
    lengyel = Algebra(config=presets.lengyel_cga())
    np.testing.assert_array_equal(lengyel.gram, previous.definition.gram)
    assert lengyel.blade("origin") == lengyel.basis_vectors()[3]
    assert lengyel.blade("infinity") == lengyel.basis_vectors()[4]


@pytest.mark.parametrize("invalid", ("reversed", "", True, 1, []))
def test_invalid_native_orders_are_rejected(invalid):
    for factory in (presets.cga, presets.blades.cga, null_cga_blade_convention):
        with pytest.raises(ValueError, match="basis_order"):
            factory(3, basis_order=invalid)


@pytest.mark.parametrize("basis_order", ORDERS)
def test_null_order_option_is_rejected_on_orthogonal_frames(basis_order):
    for factory in (presets.cga, presets.blades.cga):
        with pytest.raises(ValueError, match="only applies"):
            factory(3, frame="orthogonal", basis_order=basis_order)


@pytest.mark.parametrize("basis_order", ORDERS)
def test_blade_recipe_rejects_opposite_coordinate_order(basis_order):
    other_order = next(order for order in ORDERS if order != basis_order)
    algebra = Algebra(config=presets.cga(3, basis_order=other_order))
    before = algebra.gram.copy()
    with pytest.raises(ValueError, match="CGA"):
        algebra.with_blades(presets.blades.cga(3, basis_order=basis_order))
    np.testing.assert_array_equal(algebra.gram, before)
