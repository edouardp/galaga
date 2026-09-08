"""Ownership record for the completed Galaga 1 redesign-test migration.

All 279 historical identities and their complete source are preserved in
../tools/baselines/redesign-v1.json. The explicit redesign-v2-owners.json
crosswalk assigns every identity to collected public tests and documents
retained, replaced and retired behavior (ADR-120).

Unique state, workflow and display contracts live in:
- presentation/test_redesign_state_contracts.py
- facade/test_redesign_workflows.py
- rendering/test_redesign_display_contracts.py

Division regressions live in core/test_division_contracts.py and
facade/test_division_provenance.py (ADR-119). Existing stronger numeric,
expression, rendering and rotor suites own overlapping operation contracts.
facade/test_redesign_boundary.py verifies complete ownership, archive integrity,
negative controls, executable teaching and legacy-free execution.

This file intentionally collects no tests and has no construction exemption.
"""
