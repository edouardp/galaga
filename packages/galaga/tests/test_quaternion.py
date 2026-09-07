"""Public complex/quaternion conventions with historical test identities.

The scalar-plus-bivector even subalgebra of Euclidean Cl(3,0) is quaternionic:
i=e23, j=e13, k=e12. Compute those products before inspecting names or signs.
Native basis enumeration and semantic unit lookup are intentionally distinct.
See ADR-107 and tools/baselines/quaternion-conventions-v1.json.
"""

import unittest
from dataclasses import replace

import numpy as np
import pytest

import galaga as ga
from galaga.expression import BladeLiteral, evaluate


def _make_quaternion_algebra(expr=False):
    algebra = ga.Algebra(config=ga.p_quaternion())
    return algebra, algebra.basis_vectors(expr=expr)


def _make_xyz_algebra():
    algebra = ga.Algebra(config=ga.p_quaternion())
    original = algebra.presentation.blades
    labels = list(original.labels)
    for mask, name in ((1, "x"), (2, "y"), (4, "z"), (7, ga.Name("xyz", "xyz", "x y z"))):
        labels[mask] = replace(labels[mask], name=name if isinstance(name, ga.Name) else ga.Name(name))
    return algebra.with_blades(ga.BladeConvention(3, labels, aliases=original.aliases, roles=original.roles))


class TestQuaternionSigns(unittest.TestCase):
    def test_all_signs_are_positive(self):
        algebra, (e1, e2, e3) = _make_quaternion_algebra()
        for name, product in (("i", e2 ^ e3), ("j", e1 ^ e3), ("k", e1 ^ e2)):
            (mask,) = np.flatnonzero(product.data)
            label = algebra.blade_label(int(mask))
            assert label.ref.orientation == product.coefficient(int(mask)) == 1
            assert label.name.ascii == name
            assert algebra.blade(name) == product
            assert product * product == -1

    def test_blade_names(self):
        algebra, _ = _make_quaternion_algebra()
        assert {mask: algebra.blade_label(mask).name.unicode for mask in range(8)} == {
            0: "1",
            1: "e₁",
            2: "e₂",
            3: "k",
            4: "e₃",
            5: "j",
            6: "i",
            7: "e₁₂₃",
        }


class TestQuaternionDisplay(unittest.TestCase):
    def setUp(self):
        self.alg, (self.e1, self.e2, self.e3) = _make_quaternion_algebra()

    def test_cyclic_display(self):
        e1, e2, e3 = self.e1, self.e2, self.e3
        assert str(e2 * e3) == "i"
        assert str(e1 * e3) == "j"
        assert str(e1 * e2) == "k"

    def test_anticyclic_display(self):
        e1, e2, e3 = self.e1, self.e2, self.e3
        assert str(e3 * e2) == "-i"
        assert str(e3 * e1) == "-j"
        assert str(e2 * e1) == "-k"

    def test_quaternion_product_display(self):
        i, j, k = self.e2 ^ self.e3, self.e1 ^ self.e3, self.e1 ^ self.e2
        assert i * j == k and j * k == i and k * i == j
        assert str(i * j) == "k"
        assert str(j * i) == "-k"
        assert str(j * k) == "i"
        assert str(k * j) == "-i"
        assert str(k * i) == "j"
        assert str(i * k) == "-j"


class TestQuaternionBladeLookup(unittest.TestCase):
    def setUp(self):
        self.alg, (self.e1, self.e2, self.e3) = _make_quaternion_algebra()

    def test_lookup_by_name(self):
        i = self.alg.blade("i")
        assert str(i) == "i"
        assert ga.scalar_part(i * i) == -1.0
        assert i == self.e2 ^ self.e3

    def test_lookup_by_metric_role(self):
        assert self.alg.blade("quaternion_i") == self.alg.blade("i")
        assert self.alg.blade("e23") == self.e2 ^ self.e3
        # V2 resolves declared roles/aliases, not metric-role text.
        with pytest.raises(KeyError, match="unknown blade"):
            self.alg.blade("+2+3")

    def test_lookup_by_multivector(self):
        computed = (self.e2 ^ self.e3).named("computed").with_expr()
        i = self.alg.blade(computed)
        assert str(i) == "i"
        assert i == computed
        assert i.name is None and i.expr is None
        assert self.alg.blade(-computed) == -i

    def test_lookup_all_quaternion_units(self):
        i, j, k = self.alg.blades("i", "j", "k")
        assert i * j == k
        assert j * k == i
        assert k * i == j
        assert i * j * k == -1

    def test_lazy_blade_lookup(self):
        i = self.alg.blade("i", expr=True)
        assert i.expr == BladeLiteral(6)
        assert str(i) == "i"
        assert evaluate(i.expr, algebra=self.alg) == self.e2 ^ self.e3
        with pytest.raises(TypeError, match="lazy"):
            self.alg.blade("i", lazy=True)


class TestQuaternionVectorNames(unittest.TestCase):
    def test_custom_vector_names(self):
        algebra = _make_xyz_algebra()
        assert [str(value) for value in algebra.basis_vectors()] == ["x", "y", "z"]
        assert [str(value) for value in algebra.basis_blades(2)] == ["k", "j", "i"]
        assert [str(value) for value in algebra.blades("quaternion_i", "quaternion_j", "quaternion_k")] == [
            "i",
            "j",
            "k",
        ]

    def test_custom_vector_names_latex(self):
        algebra = _make_xyz_algebra()
        x, y, z = algebra.basis_vectors()
        assert (x.latex(), y.latex(), z.latex()) == ("x", "y", "z")
        assert (x ^ y ^ z).latex() == "x y z"
        assert list(algebra.locals()) == ["e1", "e2", "k", "e3", "j", "i", "e123"]


class TestComplexFactory(unittest.TestCase):
    def setUp(self):
        self.alg = ga.Algebra(config=ga.p_complex())
        e1, e2 = self.alg.basis_vectors()
        self.i = e1 ^ e2

    def test_display(self):
        assert str(self.i) == "i"
        assert self.i == self.alg.blade("imaginary") == self.alg.blade("e12")
        assert self.i * self.i == -1

    def test_complex_number_display(self):
        z = self.alg.scalar(3) + 4 * self.i
        assert str(z) == "3 + 4i"
        np.testing.assert_array_equal(z.data, [3, 0, 0, 4])

    def test_complex_conjugate_via_reverse(self):
        z = self.alg.scalar(3) + 4 * self.i
        zc = ga.reverse(z)
        assert str(zc) == "3 - 4i"
        np.testing.assert_array_equal(zc.data, [3, 0, 0, -4])
        assert zc == ga.conjugate(z)
