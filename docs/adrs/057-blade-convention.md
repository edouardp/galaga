# ADR-057: BladeConvention Replaces names= Parameter

## Status

Accepted

This records the v1 API. Public v2 ownership is now described by
[ADR-076](076-immutable-presentation-configuration.md) and
[ADR-104](104-metric-derived-sta-names-and-public-blade-contracts.md).
V2 uses immutable complete labels, explicit native masks and signed lookup;
it does not retain metric-role parsing, mutable rename, or `repr_unicode`.
All 107 historical blade-convention cases have public replacement contracts.

## Context

The `names=` parameter on `Algebra` mixed three concerns: basis vector naming,
blade display style, and indexing base. It couldn't express compact subscripts
(`e₁₂`), wedge notation (`e₁∧e₂`), per-blade overrides (pseudoscalar → `I`),
or 0-based indexing for PGA. Issue #8 (0-based blade lookup fails) and issue #9
(no way to name all blades at construction) were both symptoms of this limitation.

## Decision

Replace `names=` with a single `blades=` parameter accepting a `BladeConvention`
object. Convention factories (`b_default`, `b_gamma`, `b_pga`, `b_sta`, etc.)
provide one-call setup for common conventions. Override keys use metric-role
notation (`"+1-1"`, `"pss"`) that is independent of internal index ordering.

`b_cga()` defaults to the orthogonal e₊,e₋ frame because a
`BladeConvention` controls display only and cannot transform the diagonal
metric into the non-orthogonal null eₒ,e∞ frame. The legacy
`null_basis="origin_infinity"` option is explicit and display-only; a future
CGA layout is responsible for constructing and naming the actual null vectors.

See SPEC-010 for the full specification.

## Consequences

- Breaking change: `names=` is removed. Migration is mechanical (see SPEC-010).
- `repr_unicode` defaults to `True` (was `False`).
- Default blade style is compact (`e₁₂`) instead of juxtapose (`e₁e₂`).
- Every major GA library's naming convention is reproducible via factory parameters.
- `blade()` and `get_basis_blade()` accept metric-role strings.
- `BasisBlade.rename()` accepts the same value formats as override dicts.
