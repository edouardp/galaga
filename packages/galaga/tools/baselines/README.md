# Regression Fixtures

These development-only fixtures live outside the shipped `galaga` package.
They provide independent coefficient, naming, expression, and rendering
observations for ordinary runtime tests.

`rendering-snapshots.json` contains the reviewed output of the expression
recipes in `tools.rendering_snapshots`. Its expectations cover selected LaTeX
expression, value, full-display, and rich-display channels, plus coefficients.
Strings compare exactly. Coefficients require equal shapes, finite values,
and `rtol=1e-12, atol=1e-12`.

Other fixtures retain useful observations captured during development. Their
capture metadata describes the original environment, not the environment
running today's tests. Historical errors and deliberately changed spellings
are evidence rather than desired current behavior. Tests use independent
algebraic or coordinate oracles when the current contract differs.

## Maintenance

Review rendering and numeric changes before editing expectations. Add a focused
regression test for changed behavior. Do not regenerate old observations from
the current implementation or accept new output automatically.

Migration ownership ledgers, unused source captures, and the differential
rendering auditor have been retired under
[ADR-170](../../../../docs/adrs/170-retire-migration-scaffolding-before-stable-2.md).
Their original versions remain available in Git history.

See [the rendering snapshot guide](../../../../docs/v2/rendering-parity.md)
for current test commands.
