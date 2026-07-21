"""Facade-helper tests derived from Chisolm, arXiv:1205.5935v1.

The source-derived reflection, rotation, rotor, complex, quaternion,
cross-product, and boost identities live in
``core/test_chisolm_transformations.py`` and ``core/test_quaternion.py``.
This retained suite tests only the optional ``project``, ``reject``, and
``reflect`` helpers against compositions of numeric primitives.
"""

from __future__ import annotations

import numpy as np
import pytest

from galaga.legacy import Algebra, gp, inverse, is_vector, left_contraction, norm2, op, project, reflect, reject


@pytest.fixture
def cl3():
    return Algebra(3)


@pytest.fixture(params=((1, 1), (1, 1, 1)), ids=("Cl2", "Cl3"))
def eucl(request):
    return Algebra(request.param)


def _rvec(algebra, generator):
    return algebra.vector(generator.standard_normal(algebra.n))


def _rblade(algebra, generator, blade_grade):
    if blade_grade == 0:
        return algebra.scalar(generator.standard_normal())
    blade = _rvec(algebra, generator)
    for _ in range(blade_grade - 1):
        blade = op(blade, _rvec(algebra, generator))
    return blade


class TestThm15ProjPlusRejEqualsOriginal:
    """Theorem 15 (§7.1): ``project(a, A) + reject(a, A) == a``."""

    def test_vector_onto_blade(self, eucl):
        generator = np.random.default_rng(100)
        for blade_grade in range(1, eucl.n + 1):
            vector = _rvec(eucl, generator)
            blade = _rblade(eucl, generator, blade_grade)
            if abs(norm2(blade)) < 1e-10:
                continue

            assert np.allclose((project(vector, blade) + reject(vector, blade)).data, vector.data, atol=1e-10)


class TestProjectionLiesInSubspace:
    """After Theorem 15 (§7.1): ``project(a, A) ^ A == 0``."""

    def test_vector_projection(self, eucl):
        generator = np.random.default_rng(101)
        for blade_grade in range(1, eucl.n + 1):
            vector = _rvec(eucl, generator)
            blade = _rblade(eucl, generator, blade_grade)
            if abs(norm2(blade)) < 1e-10:
                continue

            assert np.allclose(op(project(vector, blade), blade).data, 0, atol=1e-10)


class TestRejectionIsOrthogonal:
    """After Theorem 15 (§7.1): ``reject(a, A) << A == 0``."""

    def test_vector_rejection(self, eucl):
        generator = np.random.default_rng(102)
        for blade_grade in range(1, eucl.n + 1):
            vector = _rvec(eucl, generator)
            blade = _rblade(eucl, generator, blade_grade)
            if abs(norm2(blade)) < 1e-10:
                continue

            assert np.allclose(left_contraction(reject(vector, blade), blade).data, 0, atol=1e-10)


class TestEq322ReflectionPreservesInnerProduct:
    """Equation 3.22 (§7.2): reflection preserves the vector pairing."""

    def test_vector_reflection(self, eucl):
        generator = np.random.default_rng(103)
        for _ in range(5):
            left = _rvec(eucl, generator)
            right = _rvec(eucl, generator)
            normal = _rvec(eucl, generator)
            if abs(norm2(normal)) < 1e-10:
                continue

            original = gp(left, right).scalar_part
            transformed = gp(reflect(left, normal), reflect(right, normal)).scalar_part
            assert original == pytest.approx(transformed, abs=1e-10)


class TestEq128ReflectionFormula:
    """Equation 1.28 (§1.1): ``reflect(v, n) == -n v inverse(n)``."""

    def test_matches_primitive_composition(self, eucl):
        generator = np.random.default_rng(104)
        for _ in range(5):
            vector = _rvec(eucl, generator)
            normal = _rvec(eucl, generator)
            if abs(norm2(normal)) < 1e-10:
                continue

            expected = gp(gp(-normal, vector), inverse(normal))
            assert np.allclose(reflect(vector, normal).data, expected.data, atol=1e-12)

    def test_result_is_vector(self, eucl):
        generator = np.random.default_rng(105)
        vector = _rvec(eucl, generator)
        normal = _rvec(eucl, generator)
        if abs(norm2(normal)) >= 1e-10:
            assert is_vector(reflect(vector, normal))


class TestEq324ReflectionInSubspace:
    """Equation 3.24 (§7.2.1), retained for helper decomposition."""

    def test_plane_reflection_matches_projection_and_rejection(self, cl3):
        generator = np.random.default_rng(106)
        vector = _rvec(cl3, generator)
        blade = _rblade(cl3, generator, 2)
        if abs(norm2(blade)) < 1e-10:
            return

        reflected = gp(gp(blade, vector), inverse(blade))
        expected = -project(vector, blade) + reject(vector, blade)
        assert np.allclose(reflected.data, expected.data, atol=1e-10)


class TestRotorProperties:
    """The retained helper case for Hamilton's double-reflection theorem."""

    def test_double_reflection_is_rotation(self, eucl):
        generator = np.random.default_rng(109)
        first_normal, second_normal = eucl.basis_vectors()[:2]
        vector = _rvec(eucl, generator)

        twice_reflected = reflect(reflect(vector, first_normal), second_normal)
        rotor = gp(second_normal, first_normal)
        rotated = gp(gp(rotor, vector), inverse(rotor))

        assert np.allclose(twice_reflected.data, rotated.data, atol=1e-10)
