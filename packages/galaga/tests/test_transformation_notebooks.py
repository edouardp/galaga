"""Execute the teaching plots and compare their geometry to the actual algebra."""

import runpy
import sys
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest

import galaga as ga

pytestmark = pytest.mark.skipif(sys.version_info < (3, 14), reason="teaching notebooks use Python 3.14 t-strings")
EXAMPLES = Path(__file__).parents[3] / "examples/algebra"


@pytest.fixture(scope="module", params=(0, 30, 90))
def projection_notebook(request):
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    previous = set(plt.get_fignums())
    with mpl.rc_context():
        app = runpy.run_path(str(EXAMPLES / "projectors_ga.py"))["app"]
        _, definitions = app.run(
            defs={
                name: SimpleNamespace(value=value)
                for name, value in (("angle", request.param), ("vx", 1.6), ("vy", 1.1), ("vz", 0.8))
            }
        )
        yield definitions
    for number in set(plt.get_fignums()) - previous:
        plt.close(number)


@pytest.fixture(scope="module", params=((20, 65, 15), (0, 45, 30), (35, 35, 5)))
def reflection_notebook(request):
    import matplotlib as mpl
    import matplotlib.pyplot as plt

    previous = set(plt.get_fignums())
    with mpl.rc_context():
        app = runpy.run_path(str(EXAMPLES / "rotors_from_reflections.py"))["app"]
        _, definitions = app.run(
            defs={
                name: SimpleNamespace(value=value)
                for name, value in zip(("alpha", "beta", "vector_angle"), request.param, strict=True)
            }
        )
        yield definitions
    for number in set(plt.get_fignums()) - previous:
        plt.close(number)


def assert_mesh_matches_blade(definitions):
    algebra, blade = definitions["alg"], definitions["B"]
    vertices = definitions["plane_mesh"].reshape(3, -1).T
    assert np.linalg.matrix_rank(vertices) == 2
    for coordinates in vertices:
        vertex = algebra.vector(coordinates)
        np.testing.assert_allclose((vertex ^ blade).data, 0, rtol=0, atol=1e-12)
        projection = ga.left_contraction(vertex, blade) * ga.inverse(blade)
        np.testing.assert_allclose(projection.data, vertex.data, rtol=0, atol=1e-12)


def assert_mirrors_match_normals(definitions):
    for key, normal in zip(("alpha", "beta"), definitions["mirror_normals"], strict=True):
        angle = np.radians(definitions[key].value)
        tangent = np.array([np.cos(angle), np.sin(angle)])
        assert np.dot(tangent, normal.vector_part) == pytest.approx(0, abs=1e-12)
        assert float(normal * normal) == pytest.approx(1, abs=1e-12)


def test_projected_surface_is_the_computed_blade_at_multiple_angles(projection_notebook):
    assert_mesh_matches_blade(projection_notebook)
    columns = projection_notebook["plane_spanners"]
    matrix = columns @ np.linalg.solve(columns.T @ columns, columns.T)
    expected = matrix @ projection_notebook["v"].vector_part
    np.testing.assert_allclose(projection_notebook["p_plane"].vector_part, expected, rtol=0, atol=1e-12)
    np.testing.assert_allclose(
        (projection_notebook["p_plane"] + projection_notebook["r_plane"]).data,
        projection_notebook["v"].data,
        rtol=0,
        atol=1e-12,
    )


def test_plane_regression_rejects_the_old_fixed_xy_surface(projection_notebook):
    broken = dict(projection_notebook)
    x, y = np.meshgrid((-2.5, 2.5), (-2.5, 2.5))
    broken["plane_mesh"] = np.array([x, y, np.zeros_like(x)])
    with pytest.raises(AssertionError):
        assert_mesh_matches_blade(broken)


def test_mirror_directions_single_reflections_and_rotor_composition_agree(reflection_notebook):
    definitions = reflection_notebook
    assert_mirrors_match_normals(definitions)
    matrices = []
    for key in ("alpha", "beta"):
        angle = np.radians(definitions[key].value)
        tangent = np.array([np.cos(angle), np.sin(angle)])
        matrices.append(2 * np.outer(tangent, tangent) - np.eye(2))
    original = definitions["reflection_input"]
    first = matrices[0] @ original.vector_part
    second = matrices[1] @ first
    np.testing.assert_allclose(definitions["reflected_once"].vector_part, first, rtol=0, atol=1e-12)
    np.testing.assert_allclose(definitions["reflected_twice"].vector_part, second, rtol=0, atol=1e-12)
    rotated = ga.sandwich(definitions["reflection_rotor"], original)
    np.testing.assert_allclose(rotated.vector_part, second, rtol=0, atol=1e-12)


def test_plot_arrows_are_the_computed_reflection_values(reflection_notebook):
    definitions = reflection_notebook
    figure = definitions["reflection_figure"]
    arrows = {artist.get_label(): artist for artist in figure.axes[0].collections}
    for label, key in (
        ("input", "reflection_input"),
        ("first reflection", "reflected_once"),
        ("second reflection", "reflected_twice"),
    ):
        arrow = arrows[label]
        np.testing.assert_allclose(
            [arrow.U.item(), arrow.V.item()],
            definitions[key].vector_part,
            rtol=0,
            atol=1e-12,
        )


def test_mirror_regression_rejects_using_the_tangent_as_a_normal(reflection_notebook):
    definitions = reflection_notebook
    broken = dict(definitions)
    algebra = definitions["reflection_input"].algebra
    normals = []
    for key in ("alpha", "beta"):
        angle = np.radians(definitions[key].value)
        normals.append(algebra.vector([np.cos(angle), np.sin(angle)]))
    broken["mirror_normals"] = normals
    with pytest.raises(AssertionError):
        assert_mirrors_match_normals(broken)
