# Exact Configured Rendering Contracts

The exact rendering suite treats LaTeX as a function of the complete rendering
input:

```text
named implementation/algebra/display configuration + expression test function
    -> exact LaTeX
```

This complements the historical legacy/facade audit. The golden contract
records what the current facade is required to emit; captured v1 observations
preserve the comparison evidence without executing the legacy engine.

## Where the contract lives

- `packages/galaga/tools/rendering_contract.py` contains reusable algebra
  profiles, display profiles, named complete configurations, and the public
  facade context adapter.
- `packages/galaga/tools/latex_contract.py` contains the small Pytest decorator
  and readable `testcase(...)` value.
- `packages/galaga/tests/rendering/test_compound_latex_contract.py` contains
  algebra-independent and PGA expression contracts.
- `packages/galaga/tests/rendering/test_sta_latex_contract.py` contains the
  notebook-derived spacetime-algebra contracts.
- `packages/galaga/tests/rendering/test_rga_latex_contract.py` contains the
  Lengyel notation matrix, complete RGA blade table, and source-derived RGA
  compound expressions.
- `packages/galaga/tools/baselines/configured-rendering-v1.json` preserves
  computed historical outputs, coefficients, basis order, and capture provenance.
- `packages/galaga/tests/rendering/test_configured_rendering_boundary.py`
  verifies the facade boundary, historical numeric samples, and execution of
  all three exact suites with legacy imports blocked.

One test looks like:

```python
@latex_test(
    testcase(
        "core-facade-v2/cl3/full-default",
        r"e_{1} \wedge e_{2} \quad = \quad e_{12}",
    ),
)
def test_simple_wedge_expression(context):
    e1, e2, _ = context.basis_vectors()
    return e1 ^ e2
```

This makes the mathematical construction, configured algebras, and expected
LaTeX readable in one place. Pytest expands the decorator into regular
parameterized cases whose IDs contain the named implementation/algebra/display
configuration.

Long expectations can use raw triple-quoted strings:

```python
testcase(
    "core-facade-v2/lengyel-rga/full-default",
    r"""
    u \wedge v + u \mathbin{\bullet} v \quad = \quad -1
    + 2 \mathbf{e}_{23} - \mathbf{e}_{31} - 3 \mathbf{e}_{12}
    + \mathbf{e}_{41} - \mathbf{e}_{42} + \mathbf{e}_{43}
    """,
)
```

`testcase()` dedents this authoring form and joins physical lines with one
space. It does not collapse whitespace within a line or make the actual
emitter comparison generally whitespace-insensitive.

## Why test functions use a context

`ExpressionContext` selects a fresh, explicit facade configuration for each
case and supplies a small public vocabulary:

- basis vectors are selected by semantic names;
- canonical operation IDs call the public facade directly; and
- naming uses the immutable facade operation, preserving shared inputs.

Only `core-facade-v2` configurations execute. Retired `legacy-v1` IDs are
rejected rather than silently mapped to a different implementation.

Test functions otherwise use normal multivector operators and multi-line
Python. They do not inject values into `locals()`. Facade
`Algebra.locals(expr=True)` returns named symbolic values, which is useful
interactively but can change a blade literal such as `e_{1}` into an expression
symbol such as `e1`. Explicit basis lookup preserves the provenance used by the
source notebook.

Python bindings inside a test function disappear when it returns. The returned v2
multivector retains its algebra, eager numeric value, name, and immutable
expression graph. The decorator retains the context and calls the public full
LaTeX path after the expression function returns, so the suite continuously
checks that rendering has no hidden dependency on a dead builder scope.

## Current representative matrix

The live default-display cases cover:

- Euclidean Cl(3): mixed grades, exterior area and volume, and projection;
- Euclidean Cl(2): rotor construction and sandwich action;
- mostly-minus STA: null-vector cancellation, Faraday-bivector assembly,
  field invariants, pseudoscalar products, and collinear and non-collinear
  Lorentz rotors;
- three-dimensional PGA: complement-based point join; and
- Lengyel RGA: all special operation spellings, every configured blade and
  signed orientation, product decomposition, plane meet, bulk/weight split,
  dual reconstruction, nested complements, and both transwedge order sums.

A display-sensitive Cl(3) expression is rendered with:

- full teaching display, six significant digits, and the default `1e-12`
  cutoff;
- full display at three significant digits; and
- full display at twelve significant digits with approximate-zero elision
  disabled.

The STA cases are drawn from maintained notebooks in both `galaga` and
`galaga-marimo-demos`; their source paths are recorded in each test docstring.
The RGA compounds are drawn from `examples/rga/rga_demo.py` and the
source-derived tables in `core/test_metric_rga.py`. The RGA notation matrix
checks expression rendering through the same context in ASCII, Unicode, and
LaTeX. Historical Unicode and LaTeX outputs are retained separately as data.
Together the matrix covers exact-zero removal, unit coefficient suppression,
retained near-zero expression terms, concrete near-zero elision, full-display
deduplication, target-specific notation, and blade-convention output.

## Historical evidence after legacy retirement

The archive was computed and checked against the original exact expectations
at commit `af3c167c188f2174fad65948e17d9b2706ee755b`, before removing the adapter.
It retains 32 compound full-LaTeX observations and the 26 RGA operations'
Unicode and LaTeX observations, with Python and NumPy capture versions. The
live suites retain all 34 facade full-LaTeX cases, including additional
precision settings, and all RGA notation and blade-table assertions.

The numeric samples continue to be checked against current computations. For
compound cases, the test derives the exterior basis transport from wedge
products of semantic vectors before comparing coefficients. This preserves
PGA signs when moving from v1's e0-first storage to v2's e0-last storage. All
32 capture-time comparisons had zero residual after transport; regression
checks use `rtol=0, atol=1e-12`, independently of public equality and hashing.

Historical strings do not dictate current rendering: the live literals still
pin reviewed changes such as floor contraction symbols and wide reverse
accents. Do not regenerate v1 history from v2 output. New v2-only cases need no
historical counterpart. See
[ADR-084](../adrs/084-exact-configured-rendering-contracts.md).

## Adding a regression

When a notebook or user expression renders incorrectly:

1. reduce it to the smallest value-returning test function that retains the
   failure;
2. add a `testcase(...)` for each named algebra/display configuration for which
   the result is meaningful;
3. keep the expression body and exact strings together under `@latex_test`;
4. compute the numeric result before choosing presentation output;
5. add a literal expected string for each relevant facade configuration;
6. run the exact suite and inspect the complete string diff;
7. fix the semantic builder, notation, or emitter at its owning layer; and
8. run both the golden suite and the historical legacy/facade audit.

New configurations are facade-only. Preserve their exact expectations without
weakening them into nominal historical parity cases or adding invented v1 data.
