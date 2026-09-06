# Frozen Rendering Observations

`rendering-v1-v2.json` is development-only reference data for
`tools.rendering_parity`. It is outside the shipped `galaga` package.

The initial capture used the unchanged audit at commit
`d98c9f463ecd532e7d9c5b3bdc82aa471ecad1bc`, Python 3.14.4, and NumPy 2.5.2.
Every legacy and facade observation was reproduced against that commit's
original audit before retiring its live legacy adapter. There are 73 cases,
45 shared registered operations, and ten reviewed differences, including the
two contraction-symbol changes.

## Data contract

- `schema_version` identifies the fixture format.
- `source_commit`, `python_version`, and `numpy_version` identify the initial
  capture, not the environment running today's audit.
- `shared_operations` records the historical common catalog; removing an
  operation from the current facade cannot silently shrink this set.
- Each stable case key retains its intent and compared channels, the original
  `legacy` observation, and the `reviewed_facade` observation.
- Each observation contains the implementation identifier, four LaTeX
  channels, coefficients, and an error field. The four legacy outer-function
  rendering errors are retained honestly; no output is invented for them.

Strings compare exactly. Numeric coefficients compare with equal lengths and
`rtol=1e-12, atol=1e-12`, matching the previous differential audit. This does
not change the public equality/hash contract.

## Maintenance

Historical v1 observations are not regenerated from the current facade. They
are evidence of the old implementation, not desired new output. Changes to a
reviewed v2 observation require a reviewed rendering decision and a focused
regression test; update the difference ledger too if the v1/v2 classification
changes. There is deliberately no automatic command to accept current output.

New v2-only capabilities belong in the exact configured rendering contracts
or dedicated rendering tests. Do not fabricate a legacy baseline for a new
capability or drop an old case simply because the legacy engine is gone.

Run the retained historical audit with:

```shell
PYTHONPATH=packages/galaga python -m tools.audit_rendering_parity \
  --repository . --output /tmp/galaga-latex-parity.md --check
```

See [the rendering audit guide](../../../../docs/v2/rendering-parity.md)
and [ADR-092](../../../../docs/adrs/092-frozen-historical-rendering-oracles.md).
