---
status: superseded
date: 2026-03-31
deciders: edouard
---

# ADR-049: Defer Poincaré/Hodge Dual as Separate Function

## Historical decision and correction

The original decision deferred a separate `poincare_dual()` function. Its
rationale incorrectly claimed that contraction into the inverse pseudoscalar
and geometric multiplication by it differed on mixed-grade multivectors.
That claim is corrected here on 2026-09-11.

For homogeneous grade $r$, $A_rI^{-1}$ has only grade $n-r$, so
$A_r\mathbin{\lfloor}I^{-1}=A_rI^{-1}$ under Galaga's contraction convention.
By linearity the identity also holds for mixed grades. There are no additional
cross-grade terms that would justify a second function for this distinction.

Neither expression defines a metric-independent Poincaré complement. Both
require an invertible pseudoscalar; exterior complementation does not.

## Current Galaga 2 decision

The implemented [core ADR-005](../core/adrs/005-explicit-product-and-duality-families.md)
supersedes this deferral:

- `dual(A)` uses contraction into the inverse pseudoscalar.
- `complement(A)` and `uncomplement(A)` are metric-independent exterior maps.
- `right_hodge_dual(A)` and `left_hodge_dual(A)` apply the metric extension
  before the corresponding complement, and are distinct named operations.
- There is no separate `poincare_dual()` alias.

See the [duality guide](../what_is_dual.md) for the general-Gram identities,
Euclidean special case and degenerate-metric behavior. Core and facade tests
cover homogeneous and mixed-grade values; no numeric implementation changed
as part of this documentation correction.
