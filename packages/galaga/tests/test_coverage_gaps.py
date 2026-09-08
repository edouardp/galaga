"""Public factory/display edges retaining all 30 historical test identities.

ADR-110 records the deliberate keyword, lookup, and rendered-string boundaries.
"""

import numpy as np
import pytest

import galaga as ga
from galaga.expression import BladeLiteral, ScalarLiteral, evaluate


def pss_convention(kind):
    dimension = 4 if kind == "gamma" else 3
    prefix = ga.Name("g", "γ", r"\gamma") if kind == "gamma" else ga.Name("s", "σ", r"\sigma")
    subscripts = (ga.Name("x", "ₓ", "x"), ga.Name("y", "ᵧ", "y"), ga.Name("z")) if kind == "sigma_xyz" else None
    return ga.indexed_blade_convention(
        dimension,
        prefix=prefix,
        start=0 if kind == "gamma" else 1,
        subscripts=subscripts,
        style="juxtapose",
        overrides={(1 << dimension) - 1: ga.Name("I")},
    )


def check_pss(kind):
    convention = pss_convention(kind)
    signature = (1, -1, -1, -1) if kind == "gamma" else (1, 1, 1)
    algebra = ga.Algebra(signature, blades=convention)
    volume = algebra.scalar(1)
    for vector in algebra.basis_vectors():
        volume = volume ^ vector
    value = algebra.pseudoscalar(expr=True)
    np.testing.assert_array_equal(value.data, volume.data)
    assert value.unicode() == value.latex() == "I"
    assert evaluate(value.expr, algebra=algebra) == volume


class TestBladeLazyPaths:
    def test_metric_role_lazy(self):
        algebra = ga.Algebra(3)
        with pytest.raises(KeyError, match="unknown blade"):
            algebra.blade("+1+2", expr=True)
        e1, e2, _ = algebra.basis_vectors()
        value = algebra.blade(e1 ^ e2, expr=True)
        assert value.expr == BladeLiteral(3)
        np.testing.assert_array_equal(value.data, (e1 ^ e2).data)

    def test_display_name_lazy(self):
        algebra = ga.Algebra(config=ga.p_sta(sigmas=True))
        g0, g1, _, _ = algebra.basis_vectors()
        value = algebra.blade("σ₁", expr=True)
        np.testing.assert_array_equal(value.data, (g1 * g0).data)
        assert value == -algebra.blade("g0g1")
        assert evaluate(value.expr, algebra=algebra) == value

    def test_scalar_blade_lazy(self):
        value = ga.Algebra(3).blade("1", expr=True)
        assert value.expr == ScalarLiteral(1)
        assert float(value) == 1

    def test_empty_string_blade(self):
        algebra = ga.Algebra(3)
        with pytest.raises(KeyError, match="unknown blade"):
            algebra.blade("")
        assert algebra.blade(0) == algebra.blade("1") == 1

    def test_prefix_digits_lazy(self):
        algebra = ga.Algebra(3)
        e1, e2, _ = algebra.basis_vectors()
        value = algebra.blade("e12", expr=True)
        assert value.expr == BladeLiteral(3)
        assert value == e1 ^ e2

    def test_prefix_digits_out_of_range(self):
        with pytest.raises(KeyError, match="unknown blade"):
            ga.Algebra(3).blade("e9")

    def test_blade_mv_not_basis(self):
        algebra = ga.Algebra(3)
        e1, e2, _ = algebra.basis_vectors()
        with pytest.raises(ValueError, match="signed unit basis blade"):
            algebra.blade(e1 + e2)

    def test_blade_mv_lazy(self):
        algebra = ga.Algebra(3)
        e1, e2, _ = algebra.basis_vectors(expr=True)
        plane = (e1 ^ e2).named("B")
        value = algebra.blade(plane, expr=True)
        assert value.expr == BladeLiteral(3) and value.name is None
        assert evaluate(value.expr, algebra=algebra) == plane


class TestDisplayResultEdgeCases:
    def test_display_str(self):
        algebra = ga.Algebra(3)
        value = algebra.vector([1, 1, 0]).named("v")
        snapshot = value.display("full/latex")
        assert type(snapshot) is str
        assert str(snapshot) == value.latex(content="full")
        with pytest.raises(AttributeError):
            snapshot.latex()

    def test_display_repr(self):
        value = ga.Algebra(3).vector([1, 1, 0]).named("v")
        snapshot = value.display("full/ascii")
        assert repr(snapshot) == "'v = e1 + e2'"
        assert str(snapshot) == "v = e1 + e2"


class TestGammaFactoryPss:
    def test_gamma_with_pss(self):
        check_pss("gamma")

    def test_sigma_with_pss(self):
        check_pss("sigma")

    def test_sigma_xyz_with_pss(self):
        check_pss("sigma_xyz")


class TestAlgebraDisplayMode:
    def setup_method(self):
        self.alg = ga.Algebra(3, display=ga.DisplayPolicy(content="full"))
        self.e1, self.e2, self.e3 = self.alg.basis_vectors(expr=True)

    def test_named_repr_uses_display(self):
        value = (2 * self.e1 + 3 * self.e2).named("v")
        assert repr(value) == "v = 2e1 + 3e2"

    def test_named_str_uses_display(self):
        value = (2 * self.e1 + 3 * self.e2).named("v")
        assert str(value) == "v = 2e₁ + 3e₂"

    def test_named_repr_latex_uses_display(self):
        value = (2 * self.e1 + 3 * self.e2).named("v")
        assert value._repr_latex_() == r"$v \quad = \quad 2 e_{1} + 3 e_{2}$"

    def test_unnamed_no_equals(self):
        value = 2 * self.e1 + 3 * self.e2
        assert repr(value) == "2e1 + 3e2"

    def test_default_display_false(self):
        algebra = ga.Algebra(3)
        value = algebra.vector([2, 3, 0]).named("v")
        assert repr(value) == "v = 2e1 + 3e2"
        with algebra.use_presentation(algebra.presentation.with_display(ga.DisplayPolicy(content="name"))):
            assert repr(value) == "v" and value._repr_latex_() == "$v$"
        with pytest.raises(TypeError, match="display_repr"):
            ga.Algebra(3, display_repr=False)

    def test_display_result_format_spec(self):
        value = (2.123456 * self.e1 + 3.789012 * self.e2).named("v")
        snapshot = value.display("full/ascii")
        with pytest.raises(ValueError, match="format code"):
            format(snapshot, ".2f")
        assert format(snapshot, ".2") == snapshot[:2]  # String truncation, not numeric precision.
        precise = self.alg.presentation.with_display(ga.DisplayPolicy(coefficient_precision=3))
        assert value.display("full/ascii", presentation=precise) == "v = 2.12e1 + 3.79e2"

    def test_display_result_format_empty(self):
        value = (2 * self.e1).named("v")
        snapshot = value.display()
        assert format(snapshot, "") == str(snapshot) == snapshot

    def test_named_latex_uses_display(self):
        value = (2 * self.e1 + 3 * self.e2).named("v")
        assert value.latex() == r"v \quad = \quad 2 e_{1} + 3 e_{2}"

    def test_latex_coeff_format_bypasses_display(self):
        value = (2 * self.e1 + 3 * self.e2).named("v")
        with pytest.raises(TypeError, match="coeff_format"):
            value.latex(coeff_format=".1f")
        assert value.latex(content="value") == r"2 e_{1} + 3 e_{2}"

    def test_latex_wrap_bypasses_display(self):
        value = (2 * self.e1 + 3 * self.e2).named("v")
        assert value.latex(wrap="$") == "$" + value.latex() + "$"
        assert value.latex(content="name", wrap="$") == "$v$"


class TestSymbolicAlias:
    def setup_method(self):
        self.alg = ga.Algebra(3)

    def test_basis_vectors_symbolic(self):
        values = self.alg.basis_vectors(expr=True)
        assert all(isinstance(value.expr, BladeLiteral) for value in values)
        with pytest.raises(TypeError, match="symbolic"):
            self.alg.basis_vectors(symbolic=True)

    def test_basis_blades_symbolic(self):
        values = self.alg.basis_blades(2, expr=True)
        assert all(isinstance(value.expr, BladeLiteral) for value in values)
        with pytest.raises(TypeError, match="symbolic"):
            self.alg.basis_blades(2, symbolic=True)

    def test_locals_symbolic(self):
        values = self.alg.locals(expr=True)
        assert all(value.expr is not None for value in values.values())
        with pytest.raises(TypeError, match="symbolic"):
            self.alg.locals(symbolic=True)

    def test_pseudoscalar_symbolic(self):
        value = self.alg.pseudoscalar(expr=True)
        assert value.expr == BladeLiteral(self.alg.dim - 1)
        with pytest.raises(TypeError, match="symbolic"):
            self.alg.pseudoscalar(symbolic=True)

    def test_blade_symbolic(self):
        value = self.alg.blade("e1", expr=True)
        assert value.expr == BladeLiteral(1)
        with pytest.raises(TypeError, match="symbolic"):
            self.alg.blade("e1", symbolic=True)

    def test_conflict_raises(self):
        for flag in (False, True):
            with pytest.raises(TypeError, match="lazy"):
                self.alg.basis_vectors(lazy=flag, symbolic=flag)

    def test_symbolic_false_is_eager(self):
        assert all(value.expr is None for value in self.alg.basis_vectors(expr=False))
        with pytest.raises(TypeError, match="symbolic"):
            self.alg.basis_vectors(symbolic=False)
