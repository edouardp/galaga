"""Independent conformance tests for the RGA convention layer.

These tests encode identities from the Rigid Geometric Algebra wiki and the
Terathon transwedge article. Wherever practical, expected coefficients are
computed directly from the vector metric instead of by restating the function
under test.
"""

from functools import reduce
from itertools import product
from math import prod

import numpy as np
import pytest

from galaga import (
    Algebra,
    Notation,
    antidot_product,
    antimetric_apply,
    antireverse,
    antiwedge,
    b_rga,
    bulk_part,
    complement,
    conjugate,
    geometric_antiproduct,
    gp,
    left_complement,
    left_hodge_dual,
    left_interior_product,
    left_weight_dual,
    metric_apply,
    metric_inner_product,
    op,
    reverse,
    right_complement,
    right_hodge_dual,
    right_interior_product,
    right_weight_dual,
    transwedge,
    transwedge_antiproduct,
    weight_part,
)
from galaga.algebra import Multivector
from galaga.ops import GA_OPS
from galaga.simplify import simplify

SIGNATURES = ((1, 1, 1), (1, -1, -1, -1), (0, 1, 1, 1))


def _basis_blades(alg):
    """Return canonical coefficient-positive basis blades, including 1."""
    return tuple(Multivector(alg, row) for row in np.eye(alg.dim))


def _wedge(vectors):
    return reduce(op, vectors)


@pytest.mark.parametrize("signature", SIGNATURES)
def test_metric_and_antimetric_diagonals_are_derived_from_signature(signature):
    """G uses present indices and G-bar uses absent indices."""
    alg = Algebra(signature)
    G = alg.extended_metric_matrix()
    Gbar = alg.metric_antiexomorphism_matrix()

    for mask in range(alg.dim):
        present = [signature[i] for i in range(alg.n) if mask & (1 << i)]
        absent = [signature[i] for i in range(alg.n) if not mask & (1 << i)]
        assert G[mask, mask] == prod(present)
        assert Gbar[mask, mask] == prod(absent)
    assert np.allclose(G @ Gbar, prod(signature) * np.eye(alg.dim))


@pytest.mark.parametrize("signature", SIGNATURES)
def test_metric_pairing_matches_direct_compound_metric(signature):
    """The exterior-algebra pairing is the direct compound-metric sum."""
    alg = Algebra(signature)
    rng = np.random.default_rng(20260713)

    for _ in range(20):
        a_data = rng.standard_normal(alg.dim)
        b_data = rng.standard_normal(alg.dim)
        expected = sum(
            a_data[mask] * b_data[mask] * prod(signature[i] for i in range(alg.n) if mask & (1 << i))
            for mask in range(alg.dim)
        )
        actual = metric_inner_product(Multivector(alg, a_data), Multivector(alg, b_data))
        assert actual.data[0] == pytest.approx(expected)
        assert np.count_nonzero(actual.data[1:]) == 0


@pytest.mark.parametrize("n", range(1, 6))
def test_left_and_right_complement_source_identities_exhaustively(n):
    """Every basis blade satisfies both exact complement wedge identities."""
    alg = Algebra(tuple(1 if i % 2 == 0 else -1 for i in range(n)))

    for mask, blade in enumerate(_basis_blades(alg)):
        grade = mask.bit_count()
        antigrade = n - grade
        assert op(blade, right_complement(blade)) == alg.I
        assert op(left_complement(blade), blade) == alg.I
        assert left_complement(blade) == ((-1) ** (grade * antigrade)) * right_complement(blade)
        assert left_complement(right_complement(blade)) == blade
        assert right_complement(left_complement(blade)) == blade


@pytest.mark.parametrize("signature", SIGNATURES)
def test_antidot_basis_table_is_computed_from_absent_metric_dimensions(signature):
    """The antidot table is diagonal and antiscalar-valued, including PGA."""
    alg = Algebra(signature)
    blades = _basis_blades(alg)

    for i, j in product(range(alg.dim), repeat=2):
        expected = 0 if i != j else prod(signature[k] for k in range(alg.n) if not i & (1 << k))
        actual = antidot_product(blades[i], blades[j])
        assert actual.data[-1] == expected
        assert np.count_nonzero(actual.data[:-1]) == 0


@pytest.mark.parametrize("signature", SIGNATURES)
def test_hodge_dual_wedge_pairings_and_double_duals(signature):
    """Bulk/Hodge duals obey their defining pairings and determinant square."""
    alg = Algebra(signature)
    det = prod(signature)
    blades = _basis_blades(alg)

    for i, a in enumerate(blades):
        grade = i.bit_count()
        square_factor = (-1) ** (grade * (alg.n - grade)) * det
        assert right_hodge_dual(a) == gp(reverse(a), alg.I)
        assert right_hodge_dual(right_hodge_dual(a)) == square_factor * a
        assert left_hodge_dual(left_hodge_dual(a)) == square_factor * a

        for j, b in enumerate(blades):
            if i.bit_count() != j.bit_count():
                continue
            pairing = metric_inner_product(a, b).data[0] * alg.I
            assert op(a, right_hodge_dual(b)) == pairing
            assert op(left_hodge_dual(a), b) == pairing


@pytest.mark.parametrize("signature", SIGNATURES)
def test_weight_duals_match_antiproduct_identity_and_double_dual(signature):
    """Weight duals satisfy the RGA geometric-constraint identities."""
    alg = Algebra(signature)
    det = prod(signature)

    for mask, a in enumerate(_basis_blades(alg)):
        grade = mask.bit_count()
        square_factor = (-1) ** (grade * (alg.n - grade)) * det
        assert right_weight_dual(a) == geometric_antiproduct(antireverse(a), alg.identity)
        assert right_weight_dual(right_weight_dual(a)) == square_factor * a
        assert left_weight_dual(left_weight_dual(a)) == square_factor * a
        assert geometric_antiproduct(a, antireverse(a)) == antidot_product(a, a)


@pytest.mark.parametrize("signature", SIGNATURES)
def test_antiwedge_and_geometric_antiproduct_basis_identities(signature):
    """De Morgan signs and the antiscalar identity hold on every basis pair."""
    alg = Algebra(signature)
    blades = _basis_blades(alg)

    for a, b in product(blades, repeat=2):
        assert antiwedge(a, b) == complement(op(left_complement(a), left_complement(b)))
        assert geometric_antiproduct(a, b) == complement(gp(left_complement(a), left_complement(b)))
    for a in blades:
        assert geometric_antiproduct(a, alg.I) == a
        assert geometric_antiproduct(alg.I, a) == a


@pytest.mark.parametrize("signature", SIGNATURES)
def test_antireverse_sign_on_every_basis_blade(signature):
    """Antireverse signs depend on antigrade, for every grade component."""
    alg = Algebra(signature)
    rng = np.random.default_rng(71)
    data = rng.standard_normal(alg.dim)
    expected = data.copy()

    for mask in range(alg.dim):
        antigrade = alg.n - mask.bit_count()
        expected[mask] *= (-1) ** (antigrade * (antigrade - 1) // 2)
    assert np.allclose(antireverse(Multivector(alg, data)).data, expected)


@pytest.mark.parametrize("signature", SIGNATURES)
def test_transwedge_signed_sum_reconstructs_geometric_product_exhaustively(signature):
    """Terathon's signed order sum reconstructs GP for every basis pair."""
    alg = Algebra(signature)

    for a, b in product(_basis_blades(alg), repeat=2):
        total = np.zeros(alg.dim)
        for k in range(alg.n + 1):
            total += (-1) ** (k * (k - 1) // 2) * transwedge(a, b, k).data
        assert np.allclose(total, gp(a, b).data)
        assert transwedge(a, b, a.homogeneous_grade()) == right_interior_product(b, a)


@pytest.mark.parametrize("signature", SIGNATURES)
def test_transwedge_antisum_reconstructs_geometric_antiproduct_exhaustively(signature):
    """The De Morgan transwedge family reconstructs GAP for every basis pair."""
    alg = Algebra(signature)

    for a, b in product(_basis_blades(alg), repeat=2):
        total = np.zeros(alg.dim)
        for k in range(alg.n + 1):
            total += (-1) ** (k * (k - 1) // 2) * transwedge_antiproduct(a, b, k).data
        assert np.allclose(total, geometric_antiproduct(a, b).data)


@pytest.mark.parametrize("bad_k, error", [(-1, ValueError), (0.5, TypeError), (True, TypeError)])
def test_transwedge_rejects_invalid_orders(bad_k, error):
    alg = Algebra(3)
    e1, e2, _ = alg.basis_vectors()
    with pytest.raises(error):
        transwedge(e1, e2, bad_k)
    with pytest.raises(error):
        transwedge_antiproduct(e1, e2, bad_k)


@pytest.mark.parametrize("signature", SIGNATURES)
def test_interior_products_match_dot_and_vector_gp_decompositions(signature):
    """RGA interior products have the documented order and signs."""
    alg = Algebra(signature)
    blades = _basis_blades(alg)

    for a, b in product(blades, repeat=2):
        if a.homogeneous_grade() == b.homogeneous_grade():
            dot = metric_inner_product(a, b)
            assert left_interior_product(a, b) == dot
            assert right_interior_product(a, b) == dot

    for vector, b in product(alg.basis_vectors(), blades):
        assert gp(vector, b) == op(vector, b) + right_interior_product(b, vector)
        assert gp(b, vector) == op(b, vector) + left_interior_product(vector, b)


def test_rga_basis_metric_orientation_names_and_display_order():
    """The RGA convention is algebraic: names retain their wedge signs."""
    alg = Algebra((1, 1, 1, 0), blades=b_rga())
    values = alg.locals()
    e1, e2, e3, e4 = alg.basis_vectors()
    factorizations = {
        "e23": (e2, e3),
        "e31": (e3, e1),
        "e12": (e1, e2),
        "e41": (e4, e1),
        "e42": (e4, e2),
        "e43": (e4, e3),
        "e423": (e4, e2, e3),
        "e431": (e4, e3, e1),
        "e412": (e4, e1, e2),
        "e321": (e3, e2, e1),
        "I": (e1, e2, e3, e4),
    }

    assert alg.signature == (1, 1, 1, 0)
    assert gp(e4, e4) == alg.scalar(0)
    for name, vectors in factorizations.items():
        assert values[name] == _wedge(vectors)
    assert complement(e1) == values["e423"]

    displayed = [str(blade) for grade in range(alg.n + 1) for blade in alg.basis_blades(grade)]
    assert displayed == [
        "1",
        "e₁",
        "e₂",
        "e₃",
        "e₄",
        "e₂₃",
        "e₃₁",
        "e₁₂",
        "e₄₁",
        "e₄₂",
        "e₄₃",
        "e₄₂₃",
        "e₄₃₁",
        "e₄₁₂",
        "e₃₂₁",
        "𝟙",
    ]


def test_rga_antivector_squares_match_vector_metric_table():
    """The geometric antiproduct applies the vector metric to antivectors."""
    alg = Algebra((1, 1, 1, 0), blades=b_rga())
    antivectors = tuple(complement(vector) for vector in alg.basis_vectors())

    for i, j in product(range(alg.n), repeat=2):
        actual = geometric_antiproduct(antivectors[i], antivectors[j])
        if i == j:
            assert actual == alg.signature[i] * alg.I
        else:
            assert actual == antiwedge(antivectors[i], antivectors[j])


def test_rga_coordinate_plane_meet_has_exact_line_sign():
    """The antiwedge meet of two coordinate planes is their common line."""
    alg = Algebra((1, 1, 1, 0), blades=b_rga())
    b = alg.locals()
    assert antiwedge(b["e423"], b["e431"]) == -b["e43"]


def test_pga_bulk_weight_decomposition_is_derived_from_null_metric():
    """A line splits into its spatial bulk and e4-containing weight pieces."""
    alg = Algebra((1, 1, 1, 0), blades=b_rga())
    b = alg.locals()
    bulk = 2 * b["e23"] - 3 * b["e31"] + 5 * b["e12"]
    weight = 7 * b["e41"] + 11 * b["e42"] - 13 * b["e43"]
    line = bulk + weight

    assert bulk_part(line) == bulk
    assert weight_part(line) == weight
    assert bulk_part(line) + weight_part(line) == line


def test_rga_point_line_plane_duals_match_source_table():
    """The published 4D RGA dual table fixes every projective sign."""
    alg = Algebra((1, 1, 1, 0), blades=b_rga())
    b = alg.locals()
    point = 2 * b["e1"] - 3 * b["e2"] + 5 * b["e3"] + 7 * b["e4"]
    line = 2 * b["e23"] - 3 * b["e31"] + 5 * b["e12"] + 7 * b["e41"] + 11 * b["e42"] - 13 * b["e43"]
    plane = 2 * b["e423"] - 3 * b["e431"] + 5 * b["e412"] + 7 * b["e321"]

    assert right_hodge_dual(point) == 2 * b["e423"] - 3 * b["e431"] + 5 * b["e412"]
    assert right_weight_dual(point) == 7 * b["e321"]
    assert right_hodge_dual(line) == -2 * b["e41"] + 3 * b["e42"] - 5 * b["e43"]
    assert right_weight_dual(line) == -7 * b["e23"] - 11 * b["e31"] + 13 * b["e12"]
    assert right_hodge_dual(plane) == -7 * b["e4"]
    assert right_weight_dual(plane) == -2 * b["e1"] + 3 * b["e2"] - 5 * b["e3"]


def test_antiproduct_sandwich_is_de_morgan_dual_of_rotor_sandwich():
    """The complement transform uses GAP and antireverse with exact signs."""
    alg = Algebra((1, 1, 1, 0), blades=b_rga())
    e1, e2, _, e4 = alg.basis_vectors()
    rotor = alg.rotor(e1 ^ e2, degrees=40)
    complement_rotor = complement(rotor)
    complement_point = complement(2 * e1 - 3 * e2 + e4)

    actual = geometric_antiproduct(
        geometric_antiproduct(complement_rotor, complement_point),
        antireverse(complement_rotor),
    )
    expected = complement(
        gp(
            gp(rotor, left_complement(complement_point)),
            reverse(rotor),
        )
    )
    assert np.allclose(actual.data, expected.data)


def test_rga_operations_preserve_symbolic_trees_values_and_grades():
    """Every convention-layer operation follows Galaga's symbolic contract."""
    alg = Algebra((1, 1, 1, 0), blades=b_rga(), notation=Notation.lengyel())
    e1, e2, _, _ = alg.basis_vectors(symbolic=True)
    numeric_e1, numeric_e2 = e1.eval(), e2.eval()
    unary = (
        metric_apply,
        antimetric_apply,
        bulk_part,
        weight_part,
        right_hodge_dual,
        left_hodge_dual,
        right_weight_dual,
        left_weight_dual,
        antireverse,
    )
    binary = (
        metric_inner_product,
        antidot_product,
        geometric_antiproduct,
        left_interior_product,
        right_interior_product,
    )

    for operation in unary:
        result = operation(e1)
        assert result._is_symbolic
        assert np.allclose(result.data, operation(numeric_e1).data)
        assert np.allclose(result._expr.eval().data, result.data)
    for operation in binary:
        result = operation(e1, e2)
        assert result._is_symbolic
        assert np.allclose(result.data, operation(numeric_e1, numeric_e2).data)
        assert np.allclose(result._expr.eval().data, result.data)
    for operation in (transwedge, transwedge_antiproduct):
        result = operation(e1, e2, 1)
        assert result._is_symbolic
        assert result._grade is not None
        assert np.allclose(result.data, operation(numeric_e1, numeric_e2, 1).data)
        assert np.allclose(result._expr.eval().data, result.data)
        assert simplify(result._expr).k == 1

    assert GA_OPS["transwedge"].arity == 3
    assert GA_OPS["transwedge_antiproduct"].arity == 3


def test_lengyel_notation_rendering_snapshot():
    """The preset renders RGA symbols without changing existing semantics."""
    alg = Algebra((1, 1, 1, 0), blades=b_rga(), notation=Notation.lengyel())
    e1, e2, _, _ = alg.basis_vectors(symbolic=True)

    assert str(gp(e1, e2)) == "e₁ ⟑ e₂"
    assert str(geometric_antiproduct(e1, e2)) == "e₁ ⟇ e₂"
    assert str(metric_inner_product(e1, e2)) == "e₁ • e₂"
    assert str(antidot_product(e1, e2)) == "e₁ ∘ e₂"
    assert str(transwedge(e1, e2, 1)) == "e₁ ⩓₁ e₂"
    assert str(transwedge_antiproduct(e1, e2, 1)) == "e₁ ⩔₁ e₂"
    assert str(right_hodge_dual(e1)) == "e₁^★"
    assert str(left_hodge_dual(e1)) == "e₁_★"
    assert str(complement(e1)) == "e₁̅"
    assert str(left_complement(e1)) == "e₁̲"
    assert str(reverse(e1)) == "e₁̃"
    assert str(conjugate(e1)) == "conjugate(e₁)"
    assert "unicode{x27D1}" in gp(e1, e2).latex()
    assert r"\overline" in complement(e1).latex()
    assert right_hodge_dual(e1).latex() == r"\mathbf{e}_{1}^{\unicode{x2605}}"
    assert r"\underset{\Large\unicode{x7E}}" in antireverse(e1).latex()

    default_alg = Algebra((1, 1, 1, 0), blades=b_rga())
    d1, d2, _, _ = default_alg.basis_vectors(symbolic=True)
    assert str(metric_inner_product(d1, d2)) == "metric_inner_product(e₁, e₂)"


@pytest.mark.parametrize(
    "operation",
    (
        metric_inner_product,
        antidot_product,
        geometric_antiproduct,
        left_interior_product,
        right_interior_product,
        transwedge,
        transwedge_antiproduct,
    ),
)
def test_binary_rga_operations_reject_mixed_algebras(operation):
    a = Algebra(2).basis_vectors()[0]
    b = Algebra(3).basis_vectors()[0]
    args = (a, b, 0) if operation in (transwedge, transwedge_antiproduct) else (a, b)
    with pytest.raises(ValueError, match="different algebras"):
        operation(*args)
