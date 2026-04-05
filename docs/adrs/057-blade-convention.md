# ADR-057: BladeConvention Replaces names= Parameter

## Status

Accepted

## Context

The `names=` parameter on `Algebra` mixed three concerns: basis vector naming, blade display style, and indexing base. It couldn't express compact subscripts (`e₁₂`), wedge notation (`e₁∧e₂`), per-blade overrides (pseudoscalar → `I`), or 0-based indexing for PGA. Issue #8 (0-based blade lookup fails) and issue #9 (no way to name all blades at construction) were both symptoms of this limitation.

## Decision

Replace `names=` with a single `blades=` parameter accepting a `BladeConvention` object. Convention factories (`b_default`, `b_gamma`, `b_pga`, `b_sta`, etc.) provide one-call setup for common conventions. Override keys use metric-role notation (`"+1-1"`, `"pss"`) that is independent of internal index ordering.

See SPEC-010 for the full specification.

## Consequences

- Breaking change: `names=` is removed. Migration is mechanical (see SPEC-010).
- `repr_unicode` defaults to `True` (was `False`).
- Default blade style is compact (`e₁₂`) instead of juxtapose (`e₁e₂`).
- Every major GA library's naming convention is reproducible via factory parameters.
- `blade()` and `get_basis_blade()` accept metric-role strings.
- `BasisBlade.rename()` accepts the same value formats as override dicts.
