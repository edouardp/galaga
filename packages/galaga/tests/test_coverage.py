"""Ownership ledger for the completely migrated mixed coverage suite.

All historical tests now have public owners; this module constructs no v1
objects and collects no duplicate tests. Keep the path for migration guards
that verify historical class/method identities are absent here.

Public owners (relative to this test directory):
- facade/test_architecture_contracts.py
- facade/test_inner_product_contracts.py
- facade/test_eager_operation_contracts.py
- facade/test_grade_simplification_contracts.py
- facade/test_expression_helper_contracts.py
- facade/test_rotor_sandwich_contracts.py
- presentation/test_naming_preset_contracts.py
- rendering/test_coverage_latex_contracts.py

Complete historical sources and observed values are retained in the matching
tools/baselines archives. The final twenty identities and source are in
rotor-sandwich-v1.json. See ADR-118 and the numeric migration inventory.
"""
