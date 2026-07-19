import marimo

__generated_with = "0.21.1"
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
    from galaga.facade import Algebra, conjugate, even_grades, grade, grade_involution, odd_grades, reverse
    import galaga_marimo as gm

    return (
        Algebra,
        conjugate,
        even_grades,
        gm,
        grade,
        grade_involution,
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
def _(Algebra):
    alg = Algebra((1, 1, 1), )
    e1, e2, e3 = alg.basis_vectors(expr=True)
    return e1, e2, e3


@app.cell
def _(
    conjugate,
    e1,
    e2,
    e3,
    even_grades,
    gm,
    grade,
    grade_involution,
    odd_grades,
    reverse,
):
    x = 3 + e1 + 2 * (e1 ^ e2) + (e1 ^ e2 ^ e3)
    gm.md(rt"""
    {x} = {x:value}

    {reverse(x)} = {reverse(x):value}

    {grade_involution(x)} = {grade_involution(x):value}

    {conjugate(x)} = {conjugate(x):value}

    {grade(x, 0)} = {grade(x, 0):value}

    {grade(x, 1)} = {grade(x, 1):value}

    {grade(x, 2)} = {grade(x, 2):value}

    {grade(x, 3)} = {grade(x, 3):value}

    {even_grades(x)} = {even_grades(x):value}

    {odd_grades(x)} = {odd_grades(x):value}
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
