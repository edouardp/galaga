"""Compute the named products first, then verify every stored STA sign."""

from dataclasses import FrozenInstanceError
from itertools import product

import numpy as np
import pytest

import galaga as ga
from galaga.expression import BladeLiteral, evaluate


@pytest.mark.parametrize("signature", tuple(product((-1, 1), repeat=4)))
@pytest.mark.parametrize("sigmas, pseudovectors", ((True, False), (False, True), (True, True)))
def test_named_blade_signs_match_actual_products_for_every_unit_diagonal_metric(signature, sigmas, pseudovectors):
    algebra = ga.Algebra(signature)
    vectors = algebra.basis_vectors()
    pseudoscalar = algebra.I
    products = {}
    if sigmas:
        for index in range(1, 4):
            products[f"s{index}"] = vectors[index] * vectors[0]
            products[f"is{index}"] = pseudoscalar * vectors[index] * vectors[0]
    if pseudovectors:
        for index in range(4):
            products[f"ig{index}"] = pseudoscalar * vectors[index]

    convention = ga.spacetime_blade_convention(
        signature=algebra.basis_squares, sigmas=sigmas, pseudovectors=pseudovectors
    )
    view = algebra.with_blades(convention)
    plain = ga.spacetime_blade_convention()
    for name, actual in products.items():
        occupied = np.flatnonzero(actual.data)
        assert occupied.shape == (1,)
        mask = occupied.item()
        orientation = int(actual.data[mask])
        label = convention.label(mask)
        assert label.ref == ga.BladeRef(mask, orientation)
        assert label.name.ascii == name
        assert orientation in (-1, 1)
        for target in ("ascii", "unicode", "latex"):
            spelling = label.name.for_target(target)
            assert view.blade(spelling) == actual
            assert view.blade(spelling).display(f"value/{target}") == spelling
            expected_native = spelling if orientation == 1 else "-" + spelling
            assert view.blade(mask).display(f"value/{target}") == expected_native
            # The original gamma word continues to mean the native blade.
            assert view.blade(plain.label(mask).name.for_target(target)) == algebra.blade(mask)
        tracked = view.blade(name, expr=True)
        assert tracked.expr == BladeLiteral(mask, orientation)
        np.testing.assert_array_equal(evaluate(tracked.expr, algebra=view).data, actual.data)
        assert hash(tracked) == hash(actual)
    assert view.numeric is algebra.numeric
    np.testing.assert_array_equal(view.gram, algebra.gram)


@pytest.mark.parametrize("signature", ("mostly-minus", "mostly-plus"))
@pytest.mark.parametrize("sigmas, pseudovectors", tuple(product((False, True), repeat=2)))
def test_preset_derives_names_from_its_own_ordered_metric(signature, sigmas, pseudovectors):
    preset = ga.p_sta(signature, sigmas=sigmas, pseudovectors=pseudovectors)
    config = preset.build()
    algebra = ga.Algebra(config=preset)
    expected = ga.spacetime_blade_convention(
        signature=algebra.basis_squares, sigmas=sigmas, pseudovectors=pseudovectors
    )
    assert config.presentation.blades == expected
    assert preset == ga.SpacetimePreset(signature, sigmas=sigmas, pseudovectors=pseudovectors)
    assert config.presentation.local_names == ga.LocalNamePolicy.from_convention(expected)
    assert algebra.blade("time") == algebra.blade(1)
    if sigmas:
        assert algebra.locals()["s1"] == algebra.blade(2) * algebra.blade(1)
    if pseudovectors:
        assert algebra.locals()["ig0"] == algebra.I * algebra.blade(1)
    with pytest.raises(FrozenInstanceError):
        preset.sigmas = not sigmas


def test_plain_convention_is_unchanged_and_needs_no_metric():
    plain = ga.spacetime_blade_convention()
    assert plain == ga.spacetime_blade_convention(sigmas=False, pseudovectors=False)
    assert plain.aliases == ()
    assert plain.label(3).name == ga.Name("g0g1", "γ₀γ₁", r"\gamma_{0} \gamma_{1}")
    assert plain.label(15).name == ga.Name("i")
    assert all(label.ref.orientation == 1 for label in plain.labels)


@pytest.mark.parametrize("kwargs", ({"sigmas": True}, {"pseudovectors": True}, {"sigmas": True, "pseudovectors": True}))
def test_metric_dependent_names_require_an_explicit_signature(kwargs):
    with pytest.raises(ValueError, match="signature"):
        ga.spacetime_blade_convention(**kwargs)


@pytest.mark.parametrize(
    "signature",
    (
        (),
        (1, -1, -1),
        (1, -1, -1, -1, -1),
        (1, 0, -1, -1),
        (2, -1, -1, -1),
        (True, -1, -1, -1),
        (np.bool_(True), -1, -1, -1),
        (np.nan, -1, -1, -1),
        (np.inf, -1, -1, -1),
        (1j, -1, -1, -1),
        "++++",
        4,
        np.eye(4),
    ),
)
def test_signed_convention_rejects_nonunit_or_non_diagonal_signature_inputs(signature):
    with pytest.raises(ValueError, match="signature"):
        ga.spacetime_blade_convention(signature=signature, sigmas=True)


@pytest.mark.parametrize("flag", ("sigmas", "pseudovectors"))
@pytest.mark.parametrize("value", (1, None, "yes", np.bool_(True)))
def test_options_require_actual_booleans(flag, value):
    with pytest.raises(TypeError, match="boolean"):
        ga.spacetime_blade_convention(signature=(1, -1, -1, -1), **{flag: value})
    with pytest.raises(TypeError, match="boolean"):
        ga.p_sta(**{flag: value})
