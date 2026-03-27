import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
EXAMPLES = ROOT / "examples"


NOTEBOOKS = [
    "special_relativity_lazy.py",
    "electromagnetism_lazy.py",
    "quantum_spin_lazy.py",
    "optics_polarisation_lazy.py",
    "pga_geometry_constructions.py",
    "planar_kinematics_lazy.py",
    "pauli_equation_toy.py",
    "coupled_oscillators_modes.py",
    "exterior_algebra_intuition.py",
    "duality_and_complements.py",
    "aharonov_bohm.py",
    "one_g_travel_calculator.py",
    "twin_paradox.py",
    "relativistic_rocket_equation.py",
    "thomas_precession.py",
    "em_waves_sta.py",
    "robot_kinematics_pga.py",
    "rotors_from_reflections.py",
    "pauli_matrices_vs_ga.py",
    "dirac_matrices_vs_sta.py",
    "maxwell_equations_sta.py",
    "thin_lens_and_rays_pga.py",
    "quantum_gates_ga.py",
    "kepler_orbits_ga.py",
    "qubits_and_superposition_ga.py",
    "measurement_and_interference_ga.py",
    "single_qubit_circuits_ga.py",
    "grover_search_ga.py",
    "deutsch_jozsa_ga.py",
    "bell_states_and_correlations.py",
    "lorentz_force_sta.py",
    "camera_geometry_pga.py",
    "null_geometry_sta.py",
    "quantum_teleportation_ga.py",
    "phase_estimation_geometry.py",
    "screw_motion_pga.py",
    "fresnel_polarisation_ga.py",
    "projectors_ga.py",
    "inner_product_family.py",
    "involutions_and_grade_ops.py",
    "norms_units_inverses.py",
    "commutator_lie_jordan.py",
    "duality_and_subspaces.py",
    "exp_log_rotors.py",
    "sandwich_products.py",
    "meets_joins_pga.py",
]


def test_new_example_notebooks_compile():
    for notebook in NOTEBOOKS:
        source = (EXAMPLES / notebook).read_text()
        if sys.version_info >= (3, 14):
            compile(source, str(EXAMPLES / notebook), "exec")
        else:
            assert 'app = marimo.App()' in source
            assert '__generated_with = "0.21.1"' in source


def test_new_example_notebooks_use_lazy_teaching_pattern():
    for notebook in NOTEBOOKS:
        source = (EXAMPLES / notebook).read_text()
        assert "basis_vectors(lazy=True)" in source
        assert "import galaga_marimo as gm" in source
        assert ".eval()" in source
        assert "gm.md(t\"\"\"" in source or "gm.md(t'''" in source
