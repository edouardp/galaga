"""Coverage gap tests for uncovered paths."""

import unittest

from galaga import Algebra, b_gamma, b_pga, b_sta


class TestBladeLazyPaths(unittest.TestCase):
    """Cover blade() lazy= paths for all lookup strategies."""

    def test_metric_role_lazy(self):
        """blade(metric_role, lazy=True) returns lazy MV."""
        alg = Algebra(3)
        mv = alg.blade("+1+2", lazy=True)
        assert mv._is_lazy

    def test_display_name_lazy(self):
        """blade(display_name, lazy=True) returns lazy MV."""
        sta = Algebra(1, 3, blades=b_sta(sigmas=True))
        mv = sta.blade("σ₁", lazy=True)
        assert mv._is_lazy

    def test_scalar_blade_lazy(self):
        """blade('1', lazy=True) returns lazy scalar."""
        alg = Algebra(3)
        mv = alg.blade("1", lazy=True)
        assert mv._is_lazy
        assert mv.scalar_part == 1.0

    def test_empty_string_blade(self):
        """blade('') returns scalar 1."""
        alg = Algebra(3)
        mv = alg.blade("")
        assert mv.scalar_part == 1.0

    def test_prefix_digits_lazy(self):
        """blade('e12', lazy=True) returns lazy MV."""
        alg = Algebra(3)
        mv = alg.blade("e12", lazy=True)
        assert mv._is_lazy

    def test_prefix_digits_out_of_range(self):
        """blade('e9') raises ValueError for 3D algebra."""
        alg = Algebra(3)
        with self.assertRaises(ValueError):
            alg.blade("e9")

    def test_blade_mv_not_basis(self):
        """blade(non_basis_mv) raises ValueError."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        with self.assertRaises(ValueError):
            alg.blade(e1 + e2)

    def test_blade_mv_lazy(self):
        """blade(mv, lazy=True) returns lazy MV."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        mv = alg.blade(e1 ^ e2, lazy=True)
        assert mv._is_lazy


class TestDisplayResultEdgeCases(unittest.TestCase):
    """Cover _DisplayResult str/repr paths."""

    def test_display_str(self):
        """_DisplayResult.__str__() returns LaTeX."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        v = (e1 + e2).name("v")
        d = v.display()
        assert isinstance(str(d), str)
        assert len(str(d)) > 0

    def test_display_repr(self):
        """_DisplayResult.__repr__() returns LaTeX."""
        alg = Algebra(3)
        e1, e2, e3 = alg.basis_vectors()
        v = (e1 + e2).name("v")
        d = v.display()
        assert isinstance(repr(d), str)


class TestDualErrorMessage(unittest.TestCase):
    """Cover the improved dual() error path."""

    def test_dual_degenerate_error(self):
        """dual() in PGA gives helpful error mentioning complement()."""
        from galaga import dual

        pga = Algebra(3, 0, 1, blades=b_pga())
        e0, e1, e2, e3 = pga.basis_vectors()
        with self.assertRaises(ValueError) as ctx:
            dual(e1)
        assert "complement()" in str(ctx.exception)


class TestRtruedivNotImplemented(unittest.TestCase):
    """Cover __rtruediv__ NotImplemented path."""

    def test_non_scalar_rtruediv(self):
        """MV / MV where left is not scalar returns NotImplemented internally."""
        alg = Algebra(3)
        e1, e2, _ = alg.basis_vectors()
        # This goes through __truediv__, not __rtruediv__
        # __rtruediv__ is hit when a non-int/float is on the left
        # In practice this returns NotImplemented and Python raises TypeError
        result = e1.__rtruediv__("not_a_number")
        assert result is NotImplemented


class TestGammaFactoryPss(unittest.TestCase):
    """Cover factory pss= parameter paths."""

    def test_gamma_with_pss(self):
        """b_gamma(pss='I') names the pseudoscalar."""
        alg = Algebra(1, 3, blades=b_gamma(pss="I"))
        assert str(alg.pseudoscalar()) == "I"

    def test_sigma_with_pss(self):
        """b_sigma(pss='I') names the pseudoscalar."""
        from galaga import b_sigma

        alg = Algebra(3, blades=b_sigma(pss="I"))
        assert str(alg.pseudoscalar()) == "I"

    def test_sigma_xyz_with_pss(self):
        """b_sigma_xyz(pss='I') names the pseudoscalar."""
        from galaga import b_sigma_xyz

        alg = Algebra(3, blades=b_sigma_xyz(pss="I"))
        assert str(alg.pseudoscalar()) == "I"


if __name__ == "__main__":
    unittest.main()
