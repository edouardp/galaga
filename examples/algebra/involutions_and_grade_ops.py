import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np
    from galaga_matrix import MatrixRepr

    import galaga as ga
    import galaga_marimo as gm
    from galaga import Algebra, DisplayPolicy

    return Algebra, DisplayPolicy, MatrixRepr, ga, gm, mo, np


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # Involutions, grades, and safe simplification

    A multivector can contain several exterior grades at once. We will separate
    them, derive the signs of three involutions, and distinguish a computed
    value's grade from a statement about a symbol.

    Four dimensions let us test an important limitation: a bivector need not be
    a single blade, and its wedge square need not vanish.
    """)
    return


@app.cell
def _(mo):
    metric_selector = mo.ui.dropdown(
        options={
            "Euclidean": ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1)),
            "Oblique indefinite": ((2, 0.5, 0, 0), (0.5, -1, 0, 0), (0, 0, 1, 0.25), (0, 0, 0.25, 3)),
            "Degenerate": ((1, 1, 0, 0), (1, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 0)),
        },
        value="Euclidean",
        label="Choose the Gram matrix",
    )
    mo.hstack([metric_selector])
    return (metric_selector,)


@app.cell
def _(Algebra, DisplayPolicy, MatrixRepr, metric_selector, np):
    gram = np.array(metric_selector.value, dtype=float)
    algebra = Algebra(gram=gram, display=DisplayPolicy(content="full"))
    gram_matrix = MatrixRepr(gram).name(latex="G")
    e1, e2, e3, e4 = algebra.basis_vectors(expr=True)
    e12, e34 = e1 ^ e2, e3 ^ e4
    x = (3 + e1 + 2 * e12 + (e12 ^ e3)).named("x")
    return algebra, e1, e12, e2, e3, e34, e4, gram, gram_matrix, x


@app.cell
def _(gm, gram_matrix, x):
    gm.md(rt"""
    Our metric is

    {gram_matrix}

    and our example has scalar, vector, bivector and trivector parts:

    {x}

    The Gram matrix affects geometric products. Exterior grade selection and
    the involution signs below depend on grade, not on a guessed signature.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Project first, then inspect

    `grade(x, k)` selects a component; `homogeneous_grade()` inspects the actual
    nonzero coefficients. A zero projection has no unique nonzero grade and
    reports `None`, just as a mixed-grade value does.

    Inspection uses a default tolerance of $10^{-12}$. Use
    `homogeneous_grade(atol=0)` to inspect every stored nonzero coefficient.
    This tolerance does not change storage or exact numeric equality.
    """)
    return


@app.cell
def _(algebra, ga, gm, mo, x):
    grade_parts = tuple(ga.grade(x, _k) for _k in range(algebra.n + 1))
    even_part, odd_part = ga.even_grades(x), ga.odd_grades(x)
    selected_parts = ga.grades(x, [0, 2])
    _rows = [gm.md(rt"""Grade {_k!s}: {_part}""") for _k, _part in enumerate(grade_parts)]
    mo.vstack(
        [
            *_rows,
            gm.md(rt"""
        Even and odd parts:

        {even_part}

        {odd_part}

        Selecting grades 0 and 2 explicitly:

        {selected_parts}

        Summing all grade projections recovers `x`; so does adding its even
        and odd parts. `grade(x, "even")` selects the same values as
        `even_grades(x)`, but records a parameterized `grade` call rather than
        an `even_grades` call. Prefer the named operation for the parity glyph.
        """),
        ]
    )
    return even_part, grade_parts, odd_part, selected_parts


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Three different involutions

    On a grade-$k$ component, the signs are:

    | Operation | Sign |
    |---|---|
    | Grade involution | $(-1)^k$ |
    | Reverse | $(-1)^{k(k-1)/2}$ |
    | Clifford conjugation | $(-1)^{k(k+1)/2}$ |

    Reverse counts the swaps needed to reverse $k$ vector factors.
    Conjugation combines reverse with grade involution. Apply any one twice
    and the numeric value returns to where it started.
    """)
    return


@app.cell
def _(ga, gm, mo, x):
    involution_results = {
        "Grade involution": ga.grade_involution(x),
        "Reverse": ga.reverse(x),
        "Clifford conjugation": ga.conjugate(x),
    }
    mo.vstack([gm.md(rt"""{_label!s}: {_value}""") for _label, _value in involution_results.items()])
    return (involution_results,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## A name does not promise a grade

    `Symbol("v")` carries no coefficients or inferred grade. Although our first
    binding is a vector, the same symbol can later represent a bivector.
    Therefore `simplify(grade(v, 1))` cannot replace the projection with `v`.

    Likewise, v2's deliberately small structural simplifier does not promise
    every algebraically valid rewrite. A double reverse evaluates to the
    original value but its call tree currently remains explicit. Numeric
    equality and structural equality answer different questions.
    """)
    return


@app.cell
def _(algebra, e1, e12, ga, gm):
    projection_node = ga.Call("grade", (ga.Symbol("v"),), {"target": 1})
    simplified_projection = ga.simplify(projection_node)
    vector_projection = ga.evaluate(simplified_projection, algebra=algebra, environment={"v": e1})
    bivector_projection = ga.evaluate(simplified_projection, algebra=algebra, environment={"v": e12})
    _expression = ga.render(simplified_projection, presentation=algebra.presentation, target="latex")
    _vector_value = vector_projection.display("value/latex")
    _bivector_value = bivector_projection.display("value/latex")
    _zero_grade = bivector_projection.homogeneous_grade()
    _fixed_point = ga.Call(
        "scalar_multiply",
        (ga.Call("add", (ga.Call("negate", (ga.Symbol("v"),)), ga.ScalarLiteral(0))),),
        {"scalar": -1},
    )
    structural_reduction = ga.simplify(_fixed_point)

    gm.md(rt"""
    The saved projection remains ${_expression!s}$.

    Bind `v` to a vector: ${_vector_value!s}$.

    Bind `v` to a bivector: ${_bivector_value!s}$.

    The zero result's inspected grade is `{_zero_grade!s}`. The node itself
    remains a grade-1 projection under both bindings.

    A supported fixed-point reduction is `-1 * (-v + 0)` to `v`, without
    consulting any binding. Its final node is:

    ```text
    {repr(structural_reduction)!s}
    ```
    """)
    return bivector_projection, projection_node, simplified_projection, structural_reduction, vector_projection


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Why a wedge square cannot always become zero

    A vector wedges with itself to zero. A simple bivector (one wedge of two
    vectors) does too. But the sum of two independent plane blades need not
    be simple.

    For $B=e_{12}+e_{34}$, the two cross terms add: swapping two grade-2
    factors has sign $(-1)^{2\cdot2}=+1$. Thus $B\wedge B$ is a nonzero
    grade-4 value. This is an exterior-algebra fact and survives a degenerate
    metric. Try the selector above.
    """)
    return


@app.cell
def _(algebra, e1, e12, e34, ga, gm):
    nonsimple_bivector = (e12 + e34).named("B")
    wedge_square = nonsimple_bivector ^ nonsimple_bivector
    wedge_node = ga.simplify(wedge_square.expr)
    wedge_replay = ga.evaluate(wedge_node, algebra=algebra, environment={"B": nonsimple_bivector})
    vector_wedge_replay = ga.evaluate(wedge_node, algebra=algebra, environment={"B": e1})
    _zero = vector_wedge_replay.display("value/latex")

    gm.md(rt"""
    {nonsimple_bivector}

    {wedge_square}

    Replaying the same saved expression with `B` bound to a vector gives
    ${_zero!s}$. The symbol name alone cannot justify replacing its wedge
    square by zero.

    Normalization and inversion have domain constraints too. V2 keeps
    `norm(unit(v))` and `inverse(inverse(v))` explicit, so those expressions
    still report a domain error for an invalid binding rather than assuming
    that every symbol is normalizable or invertible.
    """)
    return nonsimple_bivector, vector_wedge_replay, wedge_node, wedge_replay, wedge_square


if __name__ == "__main__":
    app.run()
