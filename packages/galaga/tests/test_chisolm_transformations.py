"""Public transformation compositions retaining Chisolm-derived identities.

Historical source attribution and seeded observations remain in
tools/baselines/transformation-contracts-v1.json. Helpers stay retired:
coordinate projection and Householder matrices independently check the
public primitive compositions. No sampled case silently skips or returns.
"""

import numpy as np
import pytest

import galaga as ga


@pytest.fixture
def cl3():
    return ga.Algebra(3)


@pytest.fixture(params=((1, 1), (1, 1, 1)), ids=("Cl2", "Cl3"))
def eucl(request):
    return ga.Algebra(request.param)


def _rvec(algebra, generator):
    return algebra.vector(generator.standard_normal(algebra.n))


def _rblade(algebra, generator, blade_grade):
    columns = np.column_stack([generator.standard_normal(algebra.n) for _ in range(blade_grade)])
    blade = algebra.scalar(1)
    for column in columns.T:
        blade = blade ^ algebra.vector(column)
    assert abs(float(ga.norm2(blade))) >= 1e-10
    return blade, columns


def _projection_matrix(gram, columns):
    return columns @ np.linalg.solve(columns.T @ gram @ columns, columns.T @ gram)


def _reflection_matrix(gram, normal):
    return np.eye(len(normal)) - 2 * np.outer(normal, normal @ gram) / (normal @ gram @ normal)


class TestThm15ProjPlusRejEqualsOriginal:
    def test_vector_onto_blade(self, eucl):
        generator = np.random.default_rng(100)
        for blade_grade in range(1, eucl.n + 1):
            vector = _rvec(eucl, generator)
            blade, columns = _rblade(eucl, generator, blade_grade)
            expected = _projection_matrix(eucl.gram, columns) @ vector.vector_part
            projection = ga.left_contraction(vector, blade) * ga.inverse(blade)
            rejection = vector - projection
            np.testing.assert_allclose(projection.vector_part, expected, rtol=0, atol=1e-10)
            np.testing.assert_allclose((projection + rejection).data, vector.data, rtol=0, atol=1e-10)


class TestProjectionLiesInSubspace:
    def test_vector_projection(self, eucl):
        generator = np.random.default_rng(101)
        for blade_grade in range(1, eucl.n + 1):
            vector = _rvec(eucl, generator)
            blade, columns = _rblade(eucl, generator, blade_grade)
            projection = ga.left_contraction(vector, blade) * ga.inverse(blade)
            expected = _projection_matrix(eucl.gram, columns) @ vector.vector_part
            np.testing.assert_allclose(projection.vector_part, expected, rtol=0, atol=1e-10)
            np.testing.assert_allclose((projection ^ blade).data, 0, rtol=0, atol=1e-10)


class TestRejectionIsOrthogonal:
    def test_vector_rejection(self, eucl):
        generator = np.random.default_rng(102)
        for blade_grade in range(1, eucl.n + 1):
            vector = _rvec(eucl, generator)
            blade, columns = _rblade(eucl, generator, blade_grade)
            projection = ga.left_contraction(vector, blade) * ga.inverse(blade)
            rejection = vector - projection
            expected = (np.eye(eucl.n) - _projection_matrix(eucl.gram, columns)) @ vector.vector_part
            np.testing.assert_allclose(rejection.vector_part, expected, rtol=0, atol=1e-10)
            np.testing.assert_allclose(ga.left_contraction(rejection, blade).data, 0, rtol=0, atol=1e-10)


class TestEq322ReflectionPreservesInnerProduct:
    def test_vector_reflection(self, eucl):
        generator = np.random.default_rng(103)
        for _ in range(5):
            left, right, normal = (_rvec(eucl, generator) for _ in range(3))
            assert abs(float(ga.norm2(normal))) >= 1e-10
            matrix = _reflection_matrix(eucl.gram, normal.vector_part)
            reflected_left = -normal * left * ga.inverse(normal)
            reflected_right = -normal * right * ga.inverse(normal)
            np.testing.assert_allclose(reflected_left.vector_part, matrix @ left.vector_part, rtol=0, atol=1e-10)
            np.testing.assert_allclose(reflected_right.vector_part, matrix @ right.vector_part, rtol=0, atol=1e-10)
            assert float(ga.scalar_product(left, right)) == pytest.approx(
                float(ga.scalar_product(reflected_left, reflected_right)), abs=1e-10
            )


class TestEq128ReflectionFormula:
    def test_matches_primitive_composition(self, eucl):
        generator = np.random.default_rng(104)
        for _ in range(5):
            vector, normal = (_rvec(eucl, generator) for _ in range(2))
            assert abs(float(ga.norm2(normal))) >= 1e-10
            expected = _reflection_matrix(eucl.gram, normal.vector_part) @ vector.vector_part
            reflected = -normal * vector * ga.inverse(normal)
            np.testing.assert_allclose(reflected.vector_part, expected, rtol=0, atol=1e-12)

    def test_result_is_vector(self, eucl):
        generator = np.random.default_rng(105)
        vector, normal = (_rvec(eucl, generator) for _ in range(2))
        assert abs(float(ga.norm2(normal))) >= 1e-10
        result = -normal * vector * ga.inverse(normal)
        assert ga.is_vector(result)


class TestEq324ReflectionInSubspace:
    def test_plane_reflection_matches_projection_and_rejection(self, cl3):
        generator = np.random.default_rng(106)
        vector = _rvec(cl3, generator)
        blade, columns = _rblade(cl3, generator, 2)
        projector = _projection_matrix(cl3.gram, columns)
        expected = (np.eye(cl3.n) - 2 * projector) @ vector.vector_part
        reflected = blade * vector * ga.inverse(blade)
        projection = ga.left_contraction(vector, blade) * ga.inverse(blade)
        rejection = vector - projection
        np.testing.assert_allclose(reflected.vector_part, expected, rtol=0, atol=1e-10)
        np.testing.assert_allclose(reflected.data, (-projection + rejection).data, rtol=0, atol=1e-10)


class TestRotorProperties:
    def test_double_reflection_is_rotation(self, eucl):
        generator = np.random.default_rng(109)
        first_normal, second_normal = eucl.basis_vectors()[:2]
        vector = _rvec(eucl, generator)
        expected = (
            _reflection_matrix(eucl.gram, second_normal.vector_part)
            @ _reflection_matrix(eucl.gram, first_normal.vector_part)
            @ vector.vector_part
        )
        first = -first_normal * vector * ga.inverse(first_normal)
        twice = -second_normal * first * ga.inverse(second_normal)
        rotor = second_normal * first_normal
        rotated = rotor * vector * ga.inverse(rotor)
        np.testing.assert_allclose(twice.vector_part, expected, rtol=0, atol=1e-10)
        np.testing.assert_allclose(twice.data, rotated.data, rtol=0, atol=1e-10)
