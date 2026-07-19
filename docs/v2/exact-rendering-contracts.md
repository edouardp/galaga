# Exact Configured Rendering Contracts

The exact rendering suite treats LaTeX as a function of the complete rendering
input:

```text
named implementation/algebra/display configuration + expression test function
    -> exact LaTeX
```

This complements the legacy/facade differential audit. Parity asks whether two
implementations agree; the golden contract records what each implementation is
actually required to emit.

## Where the contract lives

- `packages/galaga/tools/rendering_contract.py` contains reusable algebra
  profiles, display profiles, named complete configurations, and the v1/v2
  context adapter.
- `packages/galaga/tools/latex_contract.py` contains the small Pytest decorator
  and readable `testcase(...)` value.
- `packages/galaga/tests/rendering/test_compound_latex_contract.py` contains
  algebra-independent and PGA expression contracts.
- `packages/galaga/tests/rendering/test_sta_latex_contract.py` contains the
  notebook-derived spacetime-algebra contracts.
- `packages/galaga/tests/rendering/test_rga_latex_contract.py` contains the
  Lengyel notation matrix, complete RGA blade table, and source-derived RGA
  compound expressions.

One test looks like:

```python
@latex_test(
    testcase(
        "legacy-v1/cl3/full-default",
        r"e_{1} \wedge e_{2} \quad = \quad e_{12}",
    ),
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

The same test body must execute against two public APIs. `ExpressionContext`
normalizes only the differences needed by the examples:

- basis vectors are selected by semantic names;
- canonical operation IDs are translated to retained v1 spellings where
  necessary; and
- immutable v2 naming and non-mutating legacy naming are presented as one
  helper.

Test functions otherwise use normal multivector operators and multi-line
Python. They do not inject values into `locals()`. Facade
`Algebra.locals(expr=True)` returns named symbolic values, which is useful
interactively but can change a blade literal such as `e_{1}` into an expression
symbol such as `e1`. Explicit basis lookup preserves the provenance used by the
source notebook.

Python bindings inside a test function disappear when it returns. The returned v2
multivector retains its algebra, eager numeric value, name, and immutable
expression graph; the retained legacy value likewise owns its algebra and
expression. The decorator retains the context and calls the normalized full
LaTeX path after the expression function returns, so the suite continuously
checks that rendering has no hidden dependency on a dead builder scope.

## Current representative matrix

The paired default-display cases cover:

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
checks expression rendering through the same context at every channel that v1
can faithfully expose (Unicode and LaTeX) and all three v2 channels.
Together the matrix covers exact-zero removal, unit coefficient suppression,
retained near-zero expression terms, concrete near-zero elision, full-display
deduplication, target-specific notation, and blade-convention output.

## Adding a regression

When a notebook or user expression renders incorrectly:

1. reduce it to the smallest value-returning test function that retains the
   failure;
2. add a `testcase(...)` for each named algebra/display configuration for which
   the result is meaningful;
3. keep the expression body and exact strings together under `@latex_test`;
4. compute the numeric result before choosing presentation output;
5. add a literal expected string for each supported implementation;
6. run the exact suite and inspect the complete string diff;
7. fix the semantic builder, notation, or emitter at its owning layer; and
8. run both the golden suite and the legacy/facade differential audit.

If a new configuration is not faithfully representable in v1, mark it as an
explicit facade-only display profile. Do not weaken it into a nominal parity
case.
