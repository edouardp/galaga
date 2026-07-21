"""Low-dimensional facade-helper and legacy expression contracts.

Low-dimensional numeric mathematics now lives in ``core/test_low_dim.py``.
These cases remain above core because they exercise optional transformation
helpers, the legacy rotor constructor, or legacy expression provenance.
"""

from __future__ import annotations

import numpy as np
import pytest

from galaga.legacy import Algebra, op, project, reflect, reject, sandwich


class TestCl0Helpers:
    def test_rotor_rejects_scalar(self):
        algebra = Algebra(())

        with pytest.raises(ValueError, match="bivector"):
            algebra.rotor(algebra.scalar(1), radians=0.5)


class TestCl1Helpers:
    @pytest.fixture
    def cl1(self):
        return Algebra((1,))

    def test_project_onto_self(self, cl1):
        (e1,) = cl1.basis_vectors()

        assert np.allclose(project(e1, e1).data, e1.data)

    def test_reject_from_self(self, cl1):
        (e1,) = cl1.basis_vectors()

        assert np.allclose(reject(e1, e1).data, cl1.scalar(0).data, atol=1e-12)

    def test_reflect_in_self(self, cl1):
        (e1,) = cl1.basis_vectors()

        assert np.allclose(reflect(e1, e1).data, (-e1).data)

    def test_rotor_rejects_vector(self, cl1):
        (e1,) = cl1.basis_vectors()

        with pytest.raises(ValueError):
            cl1.rotor(e1, radians=0.5)

    def test_rotor_rejects_scalar(self, cl1):
        with pytest.raises(ValueError, match="bivector"):
            cl1.rotor(cl1.scalar(1), radians=0.5)


class TestCl2Helpers:
    def test_rotor_constructor_applies_expected_rotation(self):
        algebra = Algebra((1, 1))
        e1, e2 = algebra.basis_vectors()

        rotor = algebra.rotor(op(e1, e2), radians=np.pi / 2)

        assert np.allclose(sandwich(rotor, e1).data, e2.data, atol=1e-12)


class TestPseudoscalarLazy:
    """Legacy input to the expression-provenance factory migration."""

    def test_default_eager(self):
        algebra = Algebra((1, 1, 1))

        assert not algebra.pseudoscalar()._is_symbolic

    def test_lazy_flag(self):
        algebra = Algebra((1, 1, 1))

        assert algebra.pseudoscalar(lazy=True)._is_symbolic

    def test_lazy_in_expression(self):
        algebra = Algebra((1, 1, 1))
        e1, _, _ = algebra.basis_vectors(lazy=True)
        pseudoscalar = algebra.pseudoscalar(lazy=True).name(latex="I")

        expression = e1 * pseudoscalar

        assert expression._is_symbolic
        assert "I" in str(expression)

    def test_lazy_data_matches_eager(self):
        algebra = Algebra((1, 1, 1))

        assert np.allclose(
            algebra.pseudoscalar(lazy=True).data,
            algebra.pseudoscalar().data,
        )
