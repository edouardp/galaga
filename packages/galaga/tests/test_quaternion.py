"""Tests for quaternion algebra via Cl(3,0) bivectors with BladeConvention.

The quaternion units i, j, k are identified with the three bivectors of
Cl(3,0). The correct mapping is:

    i = e₂∧e₃ = e₂₃   (bitmask 0b110)
    j = e₁∧e₃ = e₁₃   (bitmask 0b101)
    k = e₁∧e₂ = e₁₂   (bitmask 0b011)

All BasisBlade signs are +1 because the defining products e_a∧e_b with
a < b match the canonical bitmask ordering.

Hamilton's identities:
    i² = j² = k² = ijk = -1
    ij = k,  jk = i,  ki = j
    ji = -k, kj = -i, ik = -j
"""

import unittest

import numpy as np

from galaga import Algebra, b_complex, b_quaternion


def _make_quaternion_algebra(lazy=False):
    """Build Cl(3,0) with quaternion bivector names."""
    alg = Algebra(
        (1, 1, 1),
        blades=b_quaternion(),
    )
    return alg, alg.basis_vectors(lazy=lazy)


class TestQuaternionSigns(unittest.TestCase):
    """Verify BasisBlade signs are computed correctly from the metric."""

    def test_all_signs_are_positive(self):
        """All quaternion bivector signs should be +1 (canonical ordering)."""
        alg, _ = _make_quaternion_algebra()
        assert alg._blades[0b110].sign == 1, "i (e23) sign"
        assert alg._blades[0b101].sign == 1, "j (e13) sign"
        assert alg._blades[0b011].sign == 1, "k (e12) sign"

    def test_blade_names(self):
        """Verify the complete blade name table."""
        alg, _ = _make_quaternion_algebra()
        names = {bm: alg._blades[bm].unicode_name for bm in range(8)}
        assert names == {
            0b000: "1",
            0b001: "e₁",
            0b010: "e₂",
            0b011: "k",
            0b100: "e₃",
            0b101: "j",
            0b110: "i",
            0b111: "e₁₂₃",
        }


class TestQuaternionIdentities(unittest.TestCase):
    """Verify Hamilton's identities hold numerically."""

    def setUp(self):
        self.alg, (self.e1, self.e2, self.e3) = _make_quaternion_algebra()
        self.i = self.e2 ^ self.e3  # e23
        self.j = self.e1 ^ self.e3  # e13
        self.k = self.e1 ^ self.e2  # e12

    def test_squares(self):
        """i² = j² = k² = -1."""
        assert (self.i * self.i).scalar_part == -1.0
        assert (self.j * self.j).scalar_part == -1.0
        assert (self.k * self.k).scalar_part == -1.0

    def test_ijk(self):
        """ijk = -1."""
        assert (self.i * self.j * self.k).scalar_part == -1.0

    def test_cyclic_products(self):
        """ij = k, jk = i, ki = j."""
        assert self.i * self.j == self.k
        assert self.j * self.k == self.i
        assert self.k * self.i == self.j

    def test_anticyclic_products(self):
        """ji = -k, kj = -i, ik = -j."""
        assert self.j * self.i == -self.k
        assert self.k * self.j == -self.i
        assert self.i * self.k == -self.j


class TestQuaternionDisplay(unittest.TestCase):
    """Verify that products display with correct names and signs."""

    def setUp(self):
        self.alg, (self.e1, self.e2, self.e3) = _make_quaternion_algebra()

    def test_cyclic_display(self):
        """Cyclic products display as positive named blades."""
        e1, e2, e3 = self.e1, self.e2, self.e3
        assert str(e2 * e3) == "i"
        assert str(e1 * e3) == "j"
        assert str(e1 * e2) == "k"

    def test_anticyclic_display(self):
        """Anti-cyclic products display as negative named blades."""
        e1, e2, e3 = self.e1, self.e2, self.e3
        assert str(e3 * e2) == "-i"
        assert str(e3 * e1) == "-j"
        assert str(e2 * e1) == "-k"

    def test_quaternion_product_display(self):
        """Named bivector products display correctly."""
        i = self.e2 ^ self.e3
        j = self.e1 ^ self.e3
        k = self.e1 ^ self.e2
        assert str(i * j) == "k"
        assert str(j * i) == "-k"
        assert str(j * k) == "i"
        assert str(k * j) == "-i"
        assert str(k * i) == "j"
        assert str(i * k) == "-j"


class TestQuaternionBladeLookup(unittest.TestCase):
    """Verify blade() returns canonical basis blades and accepts lazy=."""

    def setUp(self):
        self.alg, (self.e1, self.e2, self.e3) = _make_quaternion_algebra()

    def test_lookup_by_name(self):
        """blade('i') returns the canonical blade at that bitmask."""
        i = self.alg.blade("i")
        # Quaternion signs are all +1, so canonical = named
        assert str(i) == "i"
        assert (i * i).scalar_part == -1.0

    def test_lookup_by_metric_role(self):
        """blade('+2+3') returns the same as blade('i')."""
        i_name = self.alg.blade("i")
        i_role = self.alg.blade("+2+3")
        assert np.allclose(i_name.data, i_role.data)

    def test_lookup_by_multivector(self):
        """blade(mv) returns the canonical blade at that bitmask."""
        bv = self.e2 ^ self.e3
        i = self.alg.blade(bv)
        # canonical data=+1, sign=+1, so displays as "i"
        assert str(i) == "i"

    def test_lookup_all_quaternion_units(self):
        """All three quaternion units look up correctly."""
        i = self.alg.blade("i")
        j = self.alg.blade("j")
        k = self.alg.blade("k")
        # Hamilton's identity via looked-up blades
        assert i * j == k
        assert j * k == i
        assert k * i == j

    def test_lazy_blade_lookup(self):
        """blade('i', lazy=True) returns a lazy multivector."""
        i = self.alg.blade("i", lazy=True)
        assert i._is_symbolic
        assert str(i) == "i"


if __name__ == "__main__":
    unittest.main()


class TestComplexFactory(unittest.TestCase):
    """Verify b_complex() convention for Cl(2,0) even subalgebra."""

    def setUp(self):
        self.alg = Algebra(2, blades=b_complex())
        e1, e2 = self.alg.basis_vectors()
        self.i = e1 ^ e2

    def test_i_squared(self):
        """i² = -1."""
        assert (self.i * self.i).scalar_part == -1.0

    def test_display(self):
        """Bivector e12 displays as i."""
        assert str(self.i) == "i"

    def test_complex_arithmetic(self):
        """(3 + 4i)² = -7 + 24i."""
        z = self.alg.scalar(3) + 4 * self.i
        z2 = z * z
        assert z2.scalar_part == -7.0
        assert str(z) == "3 + 4i"

    def test_complex_conjugate_via_reverse(self):
        """Reverse acts as complex conjugation for bivectors: ~(a + bi) = a - bi."""
        from galaga import reverse

        z = self.alg.scalar(3) + 4 * self.i
        zc = reverse(z)
        assert str(zc) == "3 - 4i"
