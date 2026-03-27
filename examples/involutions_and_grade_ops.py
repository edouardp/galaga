import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent / "packages" / "gamo")
    for _p in [_root, _gamo]:
        if _p not in sys.path:
            sys.path.insert(0, _p)
    return


@app.cell
def _():
    import marimo as mo
    from ga import Algebra, conjugate, even_grades, grade, involute, odd_grades, reverse
    import galaga_marimo as gm

    return Algebra, conjugate, even_grades, gm, grade, involute, mo, odd_grades, reverse


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # Involutions and Grade Operations

        Reverse, involute, and conjugate are distinct algebraic symmetries. Grade
        projection and even/odd decomposition let you peel a multivector apart.
        """
    )
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return e1, e2, e3


@app.cell
def _(conjugate, e1, e2, e3, even_grades, gm, grade, involute, odd_grades, reverse):
    x = 3 + e1 + 2 * (e1 ^ e2) + (e1 ^ e2 ^ e3)
    gm.md(t"""
    {x} = {x.eval()}

    {reverse(x)} = {reverse(x).eval()}

    {involute(x)} = {involute(x).eval()}

    {conjugate(x)} = {conjugate(x).eval()}

    {grade(x, 0)} = {grade(x, 0).eval()}

    {grade(x, 1)} = {grade(x, 1).eval()}

    {grade(x, 2)} = {grade(x, 2).eval()}

    {grade(x, 3)} = {grade(x, 3).eval()}

    {even_grades(x)} = {even_grades(x).eval()}

    {odd_grades(x)} = {odd_grades(x).eval()}
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
