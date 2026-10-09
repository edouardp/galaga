"""Both complex representations agree on arithmetic and expose local i."""

import cmath

import numpy as np
import pytest

from galaga import (
    Algebra,
    BladeRef,
    Presenter,
    clifford_conjugate,
    complex_blade_convention,
    evaluate,
    exp,
    grade_involution,
    inverse,
    log,
    norm2,
    presets,
    reverse,
    sqrt,
)
from galaga.presets import ComplexPreset

REPRESENTATIONS = ("bivector", "vector")


@pytest.fixture(params=REPRESENTATIONS)
def algebra(request):
    return Algebra(config=presets.complex(representation=request.param), user_config_files=False)


def as_complex(value):
    return complex(value.coefficient(0), value.coefficient(value.algebra.dim - 1))


def test_imaginary_name_and_role_agree_with_native_products(algebra):
    native = algebra.identity
    for vector in algebra.basis_vectors():
        native = native ^ vector
    imaginary = algebra.blade("imaginary")
    assert imaginary == native == algebra.I
    expected_square = (-1) ** (algebra.n * (algebra.n - 1) // 2) * np.linalg.det(algebra.gram)
    assert float(imaginary * imaginary) == pytest.approx(expected_square)
    assert expected_square == -1
    assert algebra.blade("i") == imaginary
    assert algebra.locals()["i"] == imaginary
    assert algebra.I.display("value/ascii") == "i"
    assert algebra.I.display("value/unicode") == "i"
    assert algebra.I.latex(content="value") == "i"
    assert algebra.model.id == "complex"
    assert dict(algebra.model.roles)["imaginary"] == BladeRef(algebra.dim - 1)


def test_default_representation_is_unchanged():
    assert presets.complex() == presets.complex(representation="bivector") == ComplexPreset()
    algebra = Algebra(config=presets.complex(), user_config_files=False)
    assert algebra.signature == (1, 1)
    assert algebra.numeric.id == "complex-cl2"
    assert list(algebra.locals()) == ["e1", "e2", "i"]
    e1, e2 = algebra.basis_vectors()
    assert algebra.locals()["i"] == e1 ^ e2
    assert algebra.blade("e12") == algebra.I
    # The ambient vectors remain available outside the complex even subalgebra.
    assert e1.homogeneous_grade() == e2.homogeneous_grade() == 1


def test_vector_representation_names_the_only_basis_vector_i():
    algebra = Algebra(config=presets.complex(representation="vector"), user_config_files=False)
    assert algebra.signature == (-1,)
    assert algebra.numeric.id == "complex-cl01"
    assert algebra.dim == 2
    assert list(algebra.locals()) == ["i"]
    (i,) = algebra.basis_vectors()
    assert i == algebra.I == algebra.locals()["i"] == algebra.blade("e1")
    assert i.display("value/ascii") == "i"
    assert i.latex(content="value") == "i"
    assert (2 + 3 * i).display("value/ascii") == "2 + 3i"
    assert "i" in algebra.basis_vectors().latex()
    assert i == algebra.basis_blades(1)[0]


@pytest.mark.parametrize("z,w", [(2 + 3j, 4 - 5j), (0j, 2j), (-2 + 0j, 3 - 0.5j), (0.25 - 1.5j, -2j)])
def test_arithmetic_matches_python_complex(algebra, z, w):
    i = algebra.locals()["i"]
    left, right = z.real + z.imag * i, w.real + w.imag * i
    assert as_complex(left + right) == pytest.approx(z + w)
    assert as_complex(left - right) == pytest.approx(z - w)
    assert as_complex(left * right) == pytest.approx(z * w)
    assert as_complex(left / right) == pytest.approx(z / w)
    assert as_complex(inverse(right)) == pytest.approx(1 / w)
    assert as_complex(clifford_conjugate(left)) == pytest.approx(z.conjugate())
    assert float(left * clifford_conjugate(left)) == pytest.approx(abs(z) ** 2)


def test_transcendentals_and_expression_replay(algebra):
    i = algebra.I
    z = (2 + 3 * i).named("z")
    assert as_complex(exp(z)) == pytest.approx(cmath.exp(2 + 3j))
    assert as_complex(log(z)) == pytest.approx(cmath.log(2 + 3j))
    assert as_complex(sqrt(z)) == pytest.approx(cmath.sqrt(2 + 3j))
    result = z * z
    assert evaluate(result.expr, algebra=algebra, environment={"z": z}) == result


def test_ga_involutions_and_norm_keep_their_representation_specific_meanings(algebra):
    i = algebra.I
    z = 2 + 3 * i
    assert (1 + i) * inverse(1 + i) == algebra.identity
    if algebra.n == 2:
        assert reverse(z) == clifford_conjugate(z)
        assert grade_involution(z) == z
        assert norm2(z) == 13
        assert norm2(1 + i) == 2
    else:
        assert reverse(z) == z
        assert grade_involution(z) == clifford_conjugate(z)
        assert norm2(z) == -5
        assert norm2(1 + i) == 0


def test_blade_only_recipe_and_presenter_follow_the_selected_representation(algebra):
    representation = "vector" if algebra.n == 1 else "bivector"
    recipe = presets.blades.complex(representation=representation)
    raw = Algebra(algebra.signature, blades=recipe, user_config_files=False)
    assert raw.presentation.blades == algebra.presentation.blades
    assert complex_blade_convention(representation=representation) == algebra.presentation.blades
    view = (presets.presenters.values() | recipe)(raw.I)
    assert view.ascii() == "i"
    assert Presenter(blades=recipe)(raw.I).ascii(content="value") == "i"
    with pytest.raises(ValueError, match="requires dimension"):
        Algebra(2 if algebra.n == 1 else 1, blades=recipe, user_config_files=False)


def test_blade_only_recipe_does_not_change_the_metric():
    algebra = Algebra(1, blades=presets.blades.complex(representation="vector"), user_config_files=False)
    assert algebra.blade("i") ** 2 == algebra.identity


@pytest.mark.parametrize("invalid", ["even", "direct", "", True, None, 1])
def test_unknown_representations_are_rejected(invalid):
    for factory in (presets.complex, ComplexPreset, presets.blades.complex, complex_blade_convention):
        with pytest.raises(ValueError, match="'bivector' or 'vector'"):
            factory(representation=invalid)
