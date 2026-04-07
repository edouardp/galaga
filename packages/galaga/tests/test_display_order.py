"""Tests for SPEC-011: Custom Basis Blade Display Ordering."""

import unittest

from galaga import Algebra, b_quaternion
from galaga.blade_convention import BladeConvention


class TestDisplayOrderValidation(unittest.TestCase):
    """Rule 3: display_order must be a valid permutation of range(dim)."""

    def test_valid_permutation_accepted(self):
        """A correct permutation is accepted without error."""
        alg = Algebra(
            (1, 1),
            blades=BladeConvention(display_order=(0, 2, 1, 3)),
        )
        assert alg._display_order == (0, 2, 1, 3)

    def test_none_gives_bitmask_order(self):
        """None defaults to ascending bitmask order."""
        alg = Algebra(3)
        assert alg._display_order == tuple(range(8))

    def test_wrong_length_raises(self):
        """display_order with wrong length raises ValueError."""
        with self.assertRaises(ValueError):
            Algebra((1, 1), blades=BladeConvention(display_order=(0, 1, 2)))

    def test_duplicate_raises(self):
        """display_order with duplicates raises ValueError."""
        with self.assertRaises(ValueError):
            Algebra((1, 1), blades=BladeConvention(display_order=(0, 0, 1, 3)))

    def test_out_of_range_raises(self):
        """display_order with out-of-range bitmask raises ValueError."""
        with self.assertRaises(ValueError):
            Algebra((1, 1), blades=BladeConvention(display_order=(0, 1, 2, 99)))


class TestDisplayOrderRendering(unittest.TestCase):
    """Rules 2 and 4: rendering respects display_order."""

    def test_default_order_unchanged(self):
        """Without display_order, bitmask order is used (no regression)."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        mv = e1 + 2 * e2 + 3 * e3
        assert str(mv) == "e₁ + 2e₂ + 3e₃"

    def test_quaternion_display_order(self):
        """Quaternion terms display in i, j, k order."""
        alg = Algebra(3, blades=b_quaternion())
        e1, e2, e3 = alg.basis_vectors()
        i, j, k = e2 ^ e3, e1 ^ e3, e1 ^ e2
        q = alg.scalar(1) + 2 * i + 3 * j + 4 * k
        assert str(q) == "1 + 2i + 3j + 4k"

    def test_quaternion_latex_order(self):
        """Quaternion LaTeX also respects display_order."""
        alg = Algebra(3, blades=b_quaternion())
        e1, e2, e3 = alg.basis_vectors()
        i, j, k = e2 ^ e3, e1 ^ e3, e1 ^ e2
        q = alg.scalar(1) + 2 * i + 3 * j + 4 * k
        lat = q.latex()
        # i term should come before j, j before k
        assert lat.index("i") < lat.index("j") < lat.index("k")

    def test_quaternion_format_spec_order(self):
        """Numeric format spec also respects display_order."""
        alg = Algebra(3, blades=b_quaternion())
        e1, e2, e3 = alg.basis_vectors()
        i, j, k = e2 ^ e3, e1 ^ e3, e1 ^ e2
        q = alg.scalar(1) + 2 * i + 3 * j + 4 * k
        s = format(q, ".1f")
        assert s.index("i") < s.index("j") < s.index("k")

    def test_negative_terms_display_correctly(self):
        """Negative coefficients still render with minus sign."""
        alg = Algebra(3, blades=b_quaternion())
        e1, e2, e3 = alg.basis_vectors()
        i, j, k = e2 ^ e3, e1 ^ e3, e1 ^ e2
        q = alg.scalar(1) - 2 * i + 3 * j - 4 * k
        s = str(q)
        assert "- 2i" in s
        assert "3j" in s
        assert "- 4k" in s


class TestDisplayOrderBasisBlades(unittest.TestCase):
    """Rule 5: basis_blades() respects display_order."""

    def test_quaternion_basis_blades_order(self):
        """basis_blades(k=2) returns i, j, k in that order."""
        alg = Algebra(3, blades=b_quaternion())
        blades = alg.basis_blades(k=2)
        names = [str(b) for b in blades]
        assert names == ["i", "j", "k"]

    def test_default_basis_blades_unchanged(self):
        """Without display_order, basis_blades returns bitmask order."""
        alg = Algebra(3)
        blades = alg.basis_blades(k=2)
        names = [str(b) for b in blades]
        assert names == ["e₁₂", "e₁₃", "e₂₃"]

    def test_grade_0_and_grade_3(self):
        """display_order works for scalar and pseudoscalar grades too."""
        alg = Algebra(3, blades=b_quaternion())
        scalars = alg.basis_blades(k=0)
        assert len(scalars) == 1
        trivectors = alg.basis_blades(k=3)
        assert len(trivectors) == 1


class TestDisplayOrderUnaffected(unittest.TestCase):
    """Rule 6: computation and data are unaffected."""

    def test_data_array_unchanged(self):
        """data[] is still indexed by bitmask, not display_order."""
        alg = Algebra(3, blades=b_quaternion())
        e1, e2, e3 = alg.basis_vectors()
        i = e2 ^ e3  # bitmask 0b110 = 6
        assert i.data[0b110] == 1.0

    def test_products_unchanged(self):
        """Geometric products are unaffected by display_order."""
        alg = Algebra(3, blades=b_quaternion())
        e1, e2, e3 = alg.basis_vectors()
        i, j, k = e2 ^ e3, e1 ^ e3, e1 ^ e2
        assert i * j == k
        assert (i * i).scalar_part == -1.0

    def test_basis_vectors_unchanged(self):
        """basis_vectors() is unaffected by display_order."""
        alg = Algebra(3, blades=b_quaternion())
        e1, e2, e3 = alg.basis_vectors()
        assert str(e1) == "e₁"
        assert str(e2) == "e₂"
        assert str(e3) == "e₃"


if __name__ == "__main__":
    unittest.main()
