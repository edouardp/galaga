# Specifications Index

These specifications define `galaga.core`'s externally observable numeric behavior.
They are intentionally separate from guides, which explain concepts, and ADRs,
which explain why a design was selected.

## Specifications

| Specification | Status | Scope |
|---|---|---|
| [SPEC-001](SPEC-001-algebra-construction-and-metric.md) | Implemented | Constructor forms, metric validation, invariants, and factories |
| [SPEC-002](SPEC-002-multivector-representation-and-operators.md) | Implemented | Coefficient storage, immutability, arithmetic, scalar conversion, equality, and operators |
| [SPEC-003](SPEC-003-product-and-duality-conventions.md) | Implemented | Clifford, exterior, inner, bracket, duality, and RGA conventions |
| [SPEC-004](SPEC-004-product-backends.md) | Implemented | Backend contract, automatic selection, caching, and diagnostics |
| [SPEC-005](SPEC-005-numeric-functions.md) | Implemented | Square roots, exponential, Study-rotor logarithm, and outer transcendental functions |

## Language

The words **must**, **must not**, **should**, and **may** are normative:

- **must** or **must not** describes behavior required for conformance;
- **should** describes the intended default, with deviations requiring a
  documented reason;
- **may** describes optional behavior that does not change the mathematical
  result.

When implementation behavior intentionally changes, update the corresponding
specification and tests in the same change. If the change selects among
architectural or mathematical alternatives, add or supersede an ADR as well.
