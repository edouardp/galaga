# Rendering Snapshots

The rendering regression suite compares the public facade with reviewed
literal output and coefficient expectations. It exercises 73 expression
recipes in Euclidean and Lengyel RGA profiles.

## Where the contract lives

- `packages/galaga/tools/rendering_snapshots.py` defines expression recipes.
- `packages/galaga/tools/baselines/rendering-snapshots.json` stores reviewed
  expectations.
- `packages/galaga/tests/rendering/test_rendering_snapshots.py` compares each
  recipe with its snapshot.
- [Exact configured rendering contracts](exact-rendering-contracts.md) cover
  additional algebra, notation, and display configurations.

Each recipe compares its selected expression, value, full-display, and rich
LaTeX channels exactly. Coefficients must have the same shape, remain finite,
and agree within `rtol=1e-12, atol=1e-12`. This tolerance belongs to the tests;
it does not change multivector equality or hashing.

The recipes include nested precedence, complements and duals, contractions,
brackets, transcendental operations, named and anonymous values, near-zero
elision, and coefficient precision. Independent metric-derived coefficient
and basis transport tests complement the snapshots.

## Running the checks

From the repository root:

```shell
PYTHONPATH=packages/galaga uv run pytest \
  packages/galaga/tests/rendering/test_rendering_snapshots.py \
  packages/galaga/tests/rendering/test_compound_latex_contract.py \
  packages/galaga/tests/rendering/test_sta_latex_contract.py \
  packages/galaga/tests/rendering/test_rga_latex_contract.py -q
```

## Updating expectations

Review each changed mathematical expression, coefficient vector, and rendered
channel. Add a focused regression test for the behavior being changed before
updating its snapshot. A change to one expected channel does not permit
unreviewed changes to the others. There is no automatic snapshot acceptance
command.

New capabilities belong in these expression recipes, the configured contracts,
or dedicated rendering tests. Every snapshot key must have exactly one recipe.

## Historical review

The former v1/v2 differential auditor and difference ledger were retired under
[ADR-170](../adrs/170-retire-migration-scaffolding-before-stable-2.md). The
reviewed current outputs became these ordinary regression snapshots; no legacy
implementation is needed to exercise them. The
[July 2026 review report](rendering-parity-reports/latex-parity-20260719-184624+1200.md)
remains historical evidence. Its commands and decisions describe that checkout.
