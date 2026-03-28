import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
EXAMPLES = ROOT / "examples"


NOTEBOOKS = [
    "physics/special_relativity_lazy.py",
    "spacetime/electromagnetism_lazy.py",
    "quantum/quantum_spin_lazy.py",
    "physics/optics_polarisation_lazy.py",
    "pga/pga_geometry_constructions.py",
    "physics/planar_kinematics_lazy.py",
    "quantum/pauli_equation_toy.py",
    "physics/coupled_oscillators_modes.py",
    "algebra/exterior_algebra_intuition.py",
    "algebra/duality_and_complements.py",
    "quantum/aharonov_bohm.py",
    "physics/one_g_travel_calculator.py",
    "physics/twin_paradox.py",
    "physics/relativistic_rocket_equation.py",
    "physics/thomas_precession.py",
    "spacetime/em_waves_sta.py",
    "physics/robot_kinematics_pga.py",
    "algebra/rotors_from_reflections.py",
    "spacetime/pauli_matrices_vs_ga.py",
    "spacetime/dirac_matrices_vs_sta.py",
    "spacetime/maxwell_equations_sta.py",
    "pga/thin_lens_and_rays_pga.py",
    "quantum/quantum_gates_ga.py",
    "physics/kepler_orbits_ga.py",
    "quantum/qubits_and_superposition_ga.py",
    "quantum/measurement_and_interference_ga.py",
    "quantum/single_qubit_circuits_ga.py",
    "quantum/grover_search_ga.py",
    "quantum/deutsch_jozsa_ga.py",
    "quantum/bell_states_and_correlations.py",
    "spacetime/lorentz_force_sta.py",
    "pga/camera_geometry_pga.py",
    "spacetime/null_geometry_sta.py",
    "quantum/quantum_teleportation_ga.py",
    "quantum/phase_estimation_geometry.py",
    "pga/screw_motion_pga.py",
    "physics/fresnel_polarisation_ga.py",
    "algebra/projectors_ga.py",
    "algebra/inner_product_family.py",
    "algebra/involutions_and_grade_ops.py",
    "algebra/norms_units_inverses.py",
    "algebra/commutator_lie_jordan.py",
    "algebra/duality_and_subspaces.py",
    "algebra/exp_log_rotors.py",
    "algebra/sandwich_products.py",
    "algebra/meets_joins_pga.py",
]


def test_new_example_notebooks_compile():
    """Verify every listed example notebook is valid Python and has marimo boilerplate."""
    for notebook in NOTEBOOKS:
        source = (EXAMPLES / notebook).read_text()
        if sys.version_info >= (3, 14):
            compile(source, str(EXAMPLES / notebook), "exec")
        else:
            assert "app = marimo.App()" in source
            assert '__generated_with = "0.21.1"' in source


def test_new_example_notebooks_use_lazy_teaching_pattern():
    """Check notebooks use lazy basis vectors, galaga_marimo import, eval(), and gm.md."""
    for notebook in NOTEBOOKS:
        source = (EXAMPLES / notebook).read_text()
        assert "basis_vectors(lazy=True)" in source
        assert "import galaga_marimo as gm" in source
        assert ".eval()" in source
        assert 'gm.md(t"""' in source or "gm.md(t'''" in source
