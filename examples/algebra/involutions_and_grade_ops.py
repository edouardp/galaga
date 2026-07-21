import marimo

__generated_with = "0.23.11"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent.parent / "packages" / "galaga_marimo")
    for _p in [_root, _gamo]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
    return


@app.cell
def _():
    import marimo as mo
    from galaga import Algebra, DisplayPolicy, conjugate, even_grades, grade, grade_involution, odd_grades, reverse, grades
    import galaga_marimo as gm

    return (
        Algebra,
        DisplayPolicy,
        conjugate,
        even_grades,
        gm,
        grade,
        grade_involution,
        grades,
        mo,
        odd_grades,
        reverse,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Involutions and Grade Operations

    Reverse, involute, and conjugate are distinct algebraic symmetries. Grade
    projection and even/odd decomposition let you peel a multivector apart.
    """)
    return


@app.cell
def _(Algebra, DisplayPolicy):
    alg = Algebra((1, 1, 1), display=DisplayPolicy(content="full"))
    e1, e2, e3 = alg.basis_vectors(expr=True)
    e12, e123 = alg.blades(e1^e2, e1^e2^e3, expr=True)
    return e1, e12, e123


@app.cell
def _(
    conjugate,
    e1,
    e12,
    e123,
    even_grades,
    gm,
    grade,
    grade_involution,
    grades,
    odd_grades,
    reverse,
):
    x = (3 + e1 + 2 * e12 + e123).named("x")

    gm.md(rt"""
    {x}

    {reverse(x)}

    {grade_involution(x)}

    {conjugate(x)}

    {grade(x, 0)}

    {grade(x, 1)}

    {grade(x, 2)}

    {grade(x, 3)}

    {even_grades(x)}

    {odd_grades(x)}

    {grades(x, [0,2])}
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
