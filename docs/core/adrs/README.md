# Architectural Decision Records

These scoped Architectural Decision Records explain why the numeric core is
built this way. They preserve the decision sequence from the original
Gram-native proof repository now that its implementation lives in
`galaga.core`.

The sequence now covers metric and representation choices, product execution,
operation conventions, scalar/array boundaries, inversion, metric extensions,
the geometry-helper boundary, analytic numeric-function evaluation, and the
numeric boundary inherited by the Galaga facade.

## Index

| ADR | Title | Status |
|---|---|---|
| [001](001-use-architectural-decision-records.md) | Use architectural decision records | Accepted |
| [002](002-canonical-native-gram-matrix.md) | Make the native Gram matrix canonical | Accepted |
| [003](003-exterior-bitmasks-and-immutable-dense-values.md) | Use exterior bitmasks and immutable dense values | Accepted |
| [004](004-scalable-product-backend-strategy.md) | Select scalable product backends behind one contract | Accepted |
| [005](005-explicit-product-and-duality-families.md) | Expose explicit product and duality families | Accepted |
| [006](006-make-bracket-scaling-visible.md) | Make bracket scaling visible in function names | Accepted |
| [007](007-keep-the-core-numeric.md) | Keep the algebra core numeric and presentation-independent | Accepted |
| [008](008-left-regular-general-inverse.md) | Use the left-regular solve as the general inverse baseline | Accepted |
| [009](009-build-metric-extensions-from-minors.md) | Build metric extensions directly from ordinary and complementary minors | Accepted |
| [010](010-separate-numeric-functions-from-geometry-helpers.md) | Separate numeric functions from geometry helpers | Accepted |
| [011](011-evaluate-numeric-functions-with-explicit-real-branches.md) | Evaluate numeric functions with explicit real branches | Accepted |

## Format

Each record contains status metadata, context, the selected outcome, and
consequences. A later decision does not rewrite the historical rationale of an
accepted ADR. It adds a new ADR and marks the old one superseded.

ADRs describe decisions, not every implementation detail. Observable behavior
belongs in the [specifications](../specs/README.md), and explanatory tours
belong in the [implementation overview](../implementation-overview.md) and
[architecture guide](../architecture.md).
