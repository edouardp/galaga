"""CGA names and local bindings agree with computed oriented volumes."""

import numpy as np
import pytest

from galaga import Algebra, DisplayOrder, LocalNamePolicy, Name, dual, outer_product, presets
from galaga.blades import null_cga_blade_convention, orthogonal_cga_blade_convention
from galaga.cga import ConformalModel
from galaga.display import emit
from galaga.presets import CGAPreset, p_cga
from galaga.rendering import GradeColor

FRAMES = (("null", "origin-first"), ("null", "euclidean-first"), ("orthogonal", None))


def volumes(algebra, frame):
    if frame == "null":
        model = ConformalModel(algebra)
        spatial = model.euclidean_basis_vectors()
        origin, infinity = model.origin, model.infinity
    else:
        *spatial, plus, minus = algebra.basis_vectors()
        origin, infinity = (minus - plus) / 2, minus + plus
    euclidean = outer_product(*spatial)
    return euclidean, origin ^ euclidean ^ infinity


@pytest.mark.parametrize("spatial_dim", (1, 2, 3, 4))
@pytest.mark.parametrize("frame,basis_order", FRAMES)
@pytest.mark.parametrize("named", (False, True))
def test_sign_consistency_names_aliases_and_locals(spatial_dim, frame, basis_order, named):
    recipe = presets.cga(spatial_dim, frame=frame, basis_order=basis_order, model_pseudoscalars=named)
    algebra = Algebra(config=recipe)
    euclidean, conformal = volumes(algebra, frame)
    assert algebra.I == outer_product(*algebra.basis_vectors())
    assert algebra.blade("I") == algebra.I
    bindings = algebra.locals()
    if named:
        assert algebra.blade("I_E") == euclidean
        assert algebra.blade("I_C") == conformal
        assert bindings["IC"] == conformal
        assert algebra.blade("IE") == euclidean
        assert algebra.blade("IC") == conformal
        assert "I_E" not in bindings and "I_C" not in bindings
        assert "I" not in bindings  # locals includes canonical names, not every alias.
        if spatial_dim == 1:
            assert euclidean.latex(content="value") == r"e_{1}"
            assert bindings["e1"] == euclidean
            assert "IE" not in bindings
        else:
            assert euclidean.latex(content="value") == "I_E"
            assert bindings["IE"] == euclidean
            assert euclidean.display(target="ascii", content="value") == "IE"
        factor = float(conformal / algebra.I)
        assert algebra.I.latex(content="value") == ("-" if factor < 0 else "") + "I_C"
        assert algebra.I.display(target="ascii", content="value") == ("-" if factor < 0 else "") + "IC"
    else:
        assert algebra.I.latex(content="value") == "I"
        assert bindings["I"] == algebra.I
        assert not {"IE", "IC", "I_E", "I_C"} & bindings.keys()
    expected_vectors = {f"e{i}" for i in range(1, spatial_dim + 1)}
    expected_vectors |= {"eo", "einf"} if frame == "null" else {"ep", "em"}
    assert expected_vectors <= bindings.keys()

    # All original ASCII/Unicode/LaTeX spellings keep positive native meaning.
    plain = (
        null_cga_blade_convention(spatial_dim, basis_order=basis_order)
        if frame == "null"
        else orthogonal_cga_blade_convention(spatial_dim)
    )
    for label in plain.labels:
        for spelling in label.name.variants:
            assert algebra.blade(spelling) == algebra.blade(label.ref)
    blade_only = Algebra(
        gram=algebra.gram,
        blades=presets.blades.cga(spatial_dim, frame=frame, basis_order=basis_order, model_pseudoscalars=named),
    )
    assert blade_only.presentation.blades == algebra.presentation.blades
    assert recipe == p_cga(spatial_dim, frame=frame, basis_order=basis_order, model_pseudoscalars=named)
    assert recipe.build() == recipe.build()


@pytest.mark.parametrize("basis_order", ("origin-first", "euclidean-first"))
@pytest.mark.parametrize("null_pair", (-2.0, -0.5, 0.75))
def test_names_are_independent_of_null_pair_normalization(basis_order, null_pair):
    algebra = Algebra(config=presets.cga(3, basis_order=basis_order, null_pair=null_pair, model_pseudoscalars=True))
    euclidean, conformal = volumes(algebra, "null")
    assert algebra.blade("I_E") == euclidean
    assert algebra.blade("I_C") == conformal


@pytest.mark.parametrize("frame,basis_order", FRAMES)
@pytest.mark.parametrize("named", (False, True))
def test_full_table_reuses_names_signs_and_order_for_every_cell(frame, basis_order, named):
    algebra = Algebra(config=presets.cga(2, frame=frame, basis_order=basis_order, model_pseudoscalars=named))
    for masks in (algebra.display_order, tuple(reversed(algebra.display_order))):
        view = algebra.with_display_order(DisplayOrder(algebra.n, masks))
        table = view.wedge_product_table(full=True, colour=True)
        assert view.locals().keys() == algebra.locals().keys()
        for name, value in view.locals().items():
            assert value == algebra.locals()[name]
        for i, left in enumerate(masks):
            assert emit(table.tree.headings[i], "latex") == view.blade(left).latex(content="value")
            for j, right in enumerate(masks):
                cell = table.tree.rows[i][j]
                body = cell.body if isinstance(cell, GradeColor) else cell
                computed = view.blade(left) ^ view.blade(right)
                for target in ("ascii", "unicode", "latex"):
                    assert emit(body, target) == computed.display(target=target, content="value")
        assert view.I == algebra.I
        assert dual(view.I) == dual(algebra.I)


def test_requested_default_full_table_contains_I():
    algebra = Algebra(config=presets.cga(2))
    table = algebra.wedge_product_table(full=True)
    assert emit(table.tree.headings[-1], "latex") == "I"
    i, j = (algebra.display_order.index(mask) for mask in (1, 14))
    assert emit(table.tree.rows[i][j], "latex") == "I"
    assert emit(table.tree.rows[j][i], "latex") == "-I"


def test_blade_only_overrides_preserve_local_policy_and_numeric_values():
    algebra = Algebra(config=presets.cga(3, basis_order="euclidean-first"), expr=True)
    view = algebra.with_blades(presets.blades.cga(3, basis_order="euclidean-first", model_pseudoscalars=True))
    assert view.numeric is algebra.numeric
    assert view.presentation.local_names == algebra.presentation.local_names
    assert view.locals()["I"] == algebra.I
    assert view.locals()["I"].expr is not None
    assert view.locals(expr=False)["I"].expr is None
    custom = view.with_local_names(LocalNamePolicy(5, {"native": view.presentation.blades.resolve("I")}))
    assert tuple(custom.locals()) == ("native",)
    assert custom.locals()["native"] == algebra.I


@pytest.mark.parametrize("invalid", (None, 0, 1, "yes", np.bool_(True)))
def test_model_naming_requires_a_real_boolean(invalid):
    for factory in (presets.cga, presets.blades.cga, CGAPreset):
        with pytest.raises(TypeError, match="model_pseudoscalars must be a boolean"):
            factory(2, model_pseudoscalars=invalid)


@pytest.mark.parametrize("spatial_dim", (1, 2, 3, 4))
@pytest.mark.parametrize("frame,basis_order", FRAMES)
@pytest.mark.parametrize("named", (False, True))
@pytest.mark.parametrize("pss", (None, "I", Name("J", "Ω", r"\Omega")))
def test_null_plane_custom_pss_and_exact_factorization(spatial_dim, frame, basis_order, named, pss):
    options = dict(frame=frame, basis_order=basis_order, model_pseudoscalars=named, pss=pss, pseudoscalar_null=True)
    algebra = Algebra(config=presets.cga(spatial_dim, **options))
    euclidean, conformal = volumes(algebra, frame)
    if frame == "null":
        model = ConformalModel(algebra)
        origin, infinity = model.origin, model.infinity
    else:
        *_, plus, minus = algebra.basis_vectors()
        origin, infinity = (minus - plus) / 2, minus + plus
    null_plane = origin ^ infinity
    assert algebra.blade("E") == null_plane
    assert algebra.locals()["E"] == null_plane
    assert euclidean ^ null_plane == (-1) ** spatial_dim * conformal
    assert conformal ^ euclidean == 0
    assert algebra.blade("I") == algebra.I
    if named:
        assert algebra.blade("I_C") == conformal
        assert algebra.blade("I_E") == euclidean
    if pss is not None:
        name = pss if isinstance(pss, Name) else Name(pss)
        for target in ("ascii", "unicode", "latex"):
            assert algebra.I.display(target=target, content="value") == name.for_target(target)
            assert algebra.blade(name.for_target(target)) == algebra.I
        assert algebra.locals()[name.ascii] == algebra.I
        if named and name.ascii != "IC":
            assert "IC" not in algebra.locals()
    blade_only = Algebra(gram=algebra.gram, blades=presets.blades.cga(spatial_dim, **options))
    assert blade_only.presentation.blades == algebra.presentation.blades
    # Every renamed heading still denotes the actual native blade with its sign.
    table = algebra.wedge_product_table(full=True)
    for index, mask in enumerate(algebra.display_order):
        assert emit(table.tree.headings[index], "latex") == algebra.blade(mask).latex(content="value")
    assert algebra.blade("e1").latex(content="value") == r"e_{1}"


@pytest.mark.parametrize(
    "option",
    (
        {"pss": 1},
        {"pss": False},
        {"pss": []},
        {"pseudoscalar_null": 1},
        {"pseudoscalar_null": None},
        {"pseudoscalar_null": np.bool_(True)},
    ),
)
def test_invalid_naming_parameters_are_rejected_at_recipe_creation(option):
    for factory in (presets.cga, presets.blades.cga, CGAPreset):
        with pytest.raises(TypeError):
            factory(2, **option)


@pytest.mark.parametrize("pss", ("e1", "E", "IE", "I_E", Name("J", "e₁", "J"), "origin"))
def test_custom_pss_cannot_reinterpret_an_existing_vector_role_or_semantic_volume(pss):
    with pytest.raises(ValueError):
        Algebra(config=presets.cga(3, pss=pss))


@pytest.mark.parametrize("spelling", ("IC", "I_C", Name("custom", latex="I_C")))
def test_custom_IC_name_is_rejected_when_it_would_hide_an_orientation_reversal(spelling):
    for named in (False, True):
        with pytest.raises(ValueError, match="different signed blades"):
            Algebra(config=presets.cga(3, basis_order="euclidean-first", model_pseudoscalars=named, pss=spelling))
        algebra = Algebra(config=presets.cga(3, model_pseudoscalars=named, pss=spelling))
        name = spelling if isinstance(spelling, str) else spelling.ascii
        assert algebra.blade(name) == algebra.I


def test_custom_pss_can_reselect_the_original_native_blade_spelling():
    algebra = Algebra(config=presets.cga(2, model_pseudoscalars=True, pss="eo12inf"))
    assert algebra.I.latex(content="value") == "eo12inf"
    assert algebra.blade("I") == algebra.blade("I_C") == algebra.I


def test_empty_pss_is_rejected_instead_of_making_an_invisible_blade():
    with pytest.raises(ValueError, match="non-empty"):
        presets.cga(2, pss="")
