"""Legacy expression-provenance contracts for numeric functions."""

from __future__ import annotations

import numpy as np

from galaga import Algebra, exp, gp, norm2, scalar_sqrt, sqrt


def test_sqrt_of_expression_rotor_preserves_provenance_and_value():
    algebra = Algebra((1, 1, 1))
    e1, e2, _ = algebra.basis_vectors(lazy=True)
    rotor = exp(0.7 * (e1 ^ e2))

    root = sqrt(rotor)

    assert root._is_symbolic
    assert np.allclose(gp(root, root).data, rotor.data)


def test_scalar_sqrt_builds_and_renders_an_expression():
    algebra = Algebra((1, 1, 1))
    scalar = algebra.scalar(9).name("s")

    result = scalar_sqrt(scalar)

    assert result._is_symbolic
    assert result._expr is not None
    assert "√" in str(result)
    assert r"\sqrt{s}" in result.latex()


def test_scalar_sqrt_compound_expression_evaluates_and_displays():
    algebra = Algebra((1, 1, 1))
    mass = algebra.scalar(3).name("m")
    momentum = algebra.scalar(4).name("p")

    energy = scalar_sqrt(mass**2 + momentum**2).name("E")
    rendered = energy.display().latex()

    assert np.isclose(energy.eval().scalar_part, 5)
    assert "E" in rendered
    assert r"\sqrt" in rendered
    assert "5" in rendered


def test_norm2_expression_has_semantic_text_and_latex_rendering():
    algebra = Algebra((1, 1, 1))
    e1, _, _ = algebra.basis_vectors()
    vector = e1.name("v")

    assert str(norm2(vector)) == "‖v‖²"
    assert norm2(vector).latex() == r"\lVert v \rVert^{2}"
