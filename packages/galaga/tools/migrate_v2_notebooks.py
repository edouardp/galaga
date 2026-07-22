"""Migrate the maintained Marimo gallery to the Galaga 2 public API.

The notebook list is an executable migration ledger as well as a write guard:
the codemod refuses to edit any other path.  Rewrites are deliberately limited
to mechanical v1-to-v2 API changes.  Geometry helpers removed from Galaga 2 and
algebra-specific presentation choices remain visible for manual review.
"""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

import libcst as cst
from libcst.helpers import get_full_name_for_node

MIGRATED_NOTEBOOKS = (
    "cga/native_null_foundations.py",
    "cga/direct_objects_and_semantics.py",
    "cga/lengyel_cga_transformations.py",
    "galaga_v2/algebra_construction.py",
    "galaga_v2/eager_values_and_expressions.py",
    "galaga_v2/presentation_contexts.py",
    "galaga_v2/custom_functional_notation.py",
    "galaga_v2/numeric_core.py",
    "matrix/representations_and_roundtrips.py",
    "matrix/pauli_and_dirac.py",
    "matrix/spinor_columns.py",
    "mermaid/mermaid_diagram.py",
    "basics/complex_and_quaternions.py",
    "basics/spinor_column_conversions.py",
    "spacetime/dirac_bilinears_sta.py",
    "spacetime/weyl_chiral_basis.py",
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
    "algebra/rotations_from_bivectors.py",
    "rga/rga_demo.py",
)

_MIGRATED_NOTEBOOK_SET = frozenset(MIGRATED_NOTEBOOKS)

_RENAMED_IMPORTS = {
    "b_rga": "rga_blade_convention",
    "b_sta": "spacetime_blade_convention",
    "involute": "grade_involution",
}

_EXPRESSION_FACTORIES = {
    "basis_blades",
    "basis_vectors",
    "blade",
    "locals",
    "multivector",
    "pseudoscalar",
    "scalar",
    "vector",
}

_NON_GALAGA_NAMING_CALLS = {
    "MatrixRepr",
    "QuatMatrixRepr",
    "to_matrix",
}


def _call_name(node: cst.BaseExpression) -> str | None:
    full_name = get_full_name_for_node(node)
    if full_name is None:
        return None
    return full_name.rsplit(".", 1)[-1]


def _zero_argument_method_receiver(node: cst.BaseExpression, method: str) -> cst.BaseExpression | None:
    if (
        isinstance(node, cst.Call)
        and not node.args
        and isinstance(node.func, cst.Attribute)
        and node.func.attr.value == method
    ):
        return node.func.value
    return None


def _is_zero_argument_method_call(node: cst.BaseExpression, method: str) -> bool:
    return _zero_argument_method_receiver(node, method) is not None


def _is_non_galaga_naming_receiver(node: cst.BaseExpression) -> bool:
    return isinstance(node, cst.Call) and _call_name(node.func) in _NON_GALAGA_NAMING_CALLS


def _is_python_scalar_expression(node: cst.BaseExpression) -> bool:
    receiver = _zero_argument_method_receiver(node, "eval")
    if receiver is not None:
        return _is_python_scalar_expression(receiver)
    if isinstance(node, (cst.Float, cst.Imaginary, cst.Integer)):
        return True
    if isinstance(node, cst.UnaryOperation):
        return _is_python_scalar_expression(node.expression)
    if isinstance(node, cst.BinaryOperation):
        return _is_python_scalar_expression(node.left) and _is_python_scalar_expression(node.right)
    return isinstance(node, cst.Call) and _call_name(node.func) in {"float", "norm"}


class _MigrateNotebook(cst.CSTTransformer):
    def leave_Name(self, original_node: cst.Name, updated_node: cst.Name) -> cst.Name:
        replacement = _RENAMED_IMPORTS.get(original_node.value)
        if replacement is None:
            return updated_node
        return updated_node.with_changes(value=replacement)

    def leave_ImportFrom(self, original_node: cst.ImportFrom, updated_node: cst.ImportFrom) -> cst.ImportFrom:
        if get_full_name_for_node(original_node.module) not in {"galaga", "galaga.facade"}:
            return updated_node
        return updated_node.with_changes(module=cst.parse_expression("galaga"))

    def leave_Call(self, original_node: cst.Call, updated_node: cst.Call) -> cst.BaseExpression:
        if _is_zero_argument_method_call(original_node, "eval"):
            receiver = _zero_argument_method_receiver(updated_node, "eval")
            if receiver is None:
                raise ValueError("updated eval call no longer has the expected method-call shape")
            return receiver

        if isinstance(original_node.func, cst.Attribute) and original_node.func.attr.value in {"name", "named"}:
            if not _is_non_galaga_naming_receiver(original_node.func.value):
                if not isinstance(updated_node.func, cst.Attribute):
                    raise ValueError("updated naming call no longer has the expected method-call shape")
                args = list(updated_node.args)
                if not any(arg.keyword is None for arg in original_node.args):
                    latex = next(
                        (
                            arg.value
                            for arg in updated_node.args
                            if arg.keyword is not None and arg.keyword.value == "latex"
                        ),
                        None,
                    )
                    if latex is not None:
                        args.insert(0, cst.Arg(latex))
                return updated_node.with_changes(
                    func=updated_node.func.with_changes(attr=cst.Name("named")),
                    args=tuple(args),
                )

        call_name = _call_name(original_node.func)
        if call_name not in _EXPRESSION_FACTORIES:
            return updated_node

        args: list[cst.Arg] = []
        for arg in updated_node.args:
            if arg.keyword is not None and arg.keyword.value in {"lazy", "symbolic"}:
                args.append(arg.with_changes(keyword=cst.Name("expr")))
            else:
                args.append(arg)
        return updated_node.with_changes(args=tuple(args))

    def leave_Attribute(
        self,
        original_node: cst.Attribute,
        updated_node: cst.Attribute,
    ) -> cst.BaseExpression:
        if original_node.attr.value != "scalar_part":
            return updated_node

        # Galaga 2's norm is already a Python scalar.  All other legacy
        # ``.scalar_part`` uses become an explicit coefficient query without
        # introducing another Marimo cell dependency.
        if _is_python_scalar_expression(original_node.value):
            return updated_node.value
        return cst.Call(
            func=cst.Attribute(value=updated_node.value, attr=cst.Name("coefficient")),
            args=(cst.Arg(cst.Integer("0")),),
        )

    def leave_Arg(self, original_node: cst.Arg, updated_node: cst.Arg) -> cst.Arg | cst.RemovalSentinel:
        if updated_node.keyword is not None and updated_node.keyword.value in {
            "display_repr",
            "repr_unicode",
        }:
            return cst.RemoveFromParent()
        return updated_node

    def leave_TemplatedStringExpression(
        self,
        original_node: cst.TemplatedStringExpression,
        updated_node: cst.TemplatedStringExpression,
    ) -> cst.TemplatedStringExpression:
        if _is_zero_argument_method_call(original_node.expression, "reveal"):
            receiver = _zero_argument_method_receiver(updated_node.expression, "reveal")
            if receiver is None:
                raise ValueError("updated reveal call no longer has the expected method-call shape")
            return updated_node.with_changes(
                expression=receiver,
                format_spec=(cst.TemplatedStringText("expr"),),
            )
        if not _is_zero_argument_method_call(original_node.expression, "eval"):
            return updated_node
        if original_node.format_spec is not None:
            return updated_node

        receiver = _zero_argument_method_receiver(original_node.expression, "eval")
        if receiver is None:
            raise ValueError("original eval call no longer has the expected method-call shape")
        if isinstance(receiver, cst.Call) and _call_name(receiver.func) == "norm":
            return updated_node
        return updated_node.with_changes(format_spec=(cst.TemplatedStringText("value"),))

    def leave_TemplatedString(
        self,
        original_node: cst.TemplatedString,
        updated_node: cst.TemplatedString,
    ) -> cst.TemplatedString:
        if original_node.start.startswith("t"):
            return updated_node.with_changes(start=f"rt{updated_node.start[1:]}")
        return updated_node


def migrate_source(source: str) -> str:
    """Return one mechanically migrated notebook source file."""
    # LibCST accepts Python's ``rt`` spelling but not the equivalent ``tr``.
    # Normalize output from the first raw-t-string implementation before parse
    # so already-migrated notebooks remain repairable and idempotent.
    source = source.replace('tr"""', 'rt"""').replace("tr'''", "rt'''")
    return cst.parse_module(source).visit(_MigrateNotebook()).code


def _notebook_relative_path(path: Path, *, repository: Path) -> str:
    examples = (repository / "examples").resolve()
    try:
        relative = path.resolve().relative_to(examples)
    except ValueError as error:
        raise ValueError(f"refusing to rewrite a file outside {examples}: {path}") from error
    return relative.as_posix()


def migrate_path(path: Path, *, repository: Path, check: bool) -> bool:
    """Migrate one ledgered notebook and return whether it required a change."""
    relative = _notebook_relative_path(path, repository=repository)
    if relative not in _MIGRATED_NOTEBOOK_SET:
        raise ValueError(f"refusing to rewrite an unledgered notebook: {relative}")

    source = path.read_text()
    migrated = migrate_source(source)
    changed = source != migrated
    if changed and not check:
        path.write_text(migrated)
    return changed


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="report changes without writing them")
    parser.add_argument("--repository", type=Path, default=Path.cwd())
    parser.add_argument("paths", nargs="*", type=Path)
    args = parser.parse_args(argv)

    paths = args.paths or [args.repository / "examples" / relative for relative in MIGRATED_NOTEBOOKS]
    changed = [path for path in paths if migrate_path(path, repository=args.repository, check=args.check)]
    for path in changed:
        print(path)
    return int(args.check and bool(changed))


if __name__ == "__main__":
    raise SystemExit(main())
