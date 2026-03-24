import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    if _root not in sys.path:
        sys.path.insert(0, _root)
    return


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _(mo):
    mo.md("""
    # Geometric Algebra — Symbolic Expressions
    This notebook demonstrates the symbolic layer of the `ga` library.
    """)
    return


@app.cell
def _():
    import numpy as np
    from ga import Algebra
    from ga.symbolic import (
        sym, gp, op, grade, reverse, involute, conjugate,
        dual, undual, norm, unit, inverse, squared,
        left_contraction, right_contraction, hestenes_inner, scalar_product,
        even_grades, odd_grades,
    )

    return (
        Algebra,
        conjugate,
        dual,
        even_grades,
        gp,
        grade,
        hestenes_inner,
        inverse,
        involute,
        left_contraction,
        norm,
        np,
        odd_grades,
        op,
        reverse,
        right_contraction,
        scalar_product,
        squared,
        sym,
        undual,
        unit,
    )


@app.cell
def _(mo):
    mo.md("""
    ## Setup — 3D Euclidean Algebra
    """)
    return


@app.cell
def _(Algebra, sym):
    alg = Algebra((1, 1, 1))
    e1, e2, e3 = alg.basis_vectors()

    # Wrap numeric multivectors as named symbols
    R = sym(e1 * e2, "R")
    v = sym(e1 + 2 * e2, "v")
    a = sym(e1, "a")
    b = sym(e2, "b")
    A = sym(e1 * e2, "A")
    B = sym(e2 * e3, "B")
    return A, B, R, a, alg, b, e1, e2, v


@app.cell
def _(mo):
    mo.md("""
    ## Products
    """)
    return


@app.cell
def _(a, b, gp):
    # Each expression renders as LaTeX automatically in marimo
    gp(a, b)
    return


@app.cell
def _(a, b, op):
    op(a, b)
    return


@app.cell
def _(a, b, left_contraction):
    left_contraction(a, b)
    return


@app.cell
def _(a, b, right_contraction):
    right_contraction(a, b)
    return


@app.cell
def _(A, B, hestenes_inner):
    hestenes_inner(A, B)
    return


@app.cell
def _(A, B, scalar_product):
    scalar_product(A, B)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Sandwich Product & Grade Projection
    """)
    return


@app.cell
def _(R, grade, v):
    # The classic rotor sandwich: grade-1 projection of R v R̃
    sandwich_expr = grade(R * v * ~R, 1)
    sandwich_expr
    return (sandwich_expr,)


@app.cell
def _(mo, sandwich_expr):
    mo.md(f"""
    Evaluating: {sandwich_expr.latex(wrap='$')} = `{sandwich_expr.eval()}`
    """)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Unary Operations
    """)
    return


@app.cell
def _(R, reverse):
    reverse(R)
    return


@app.cell
def _(involute, v):
    involute(v)
    return


@app.cell
def _(conjugate, v):
    conjugate(v)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Dual, Norm, Unit, Inverse
    """)
    return


@app.cell
def _(dual, v):
    dual(v)
    return


@app.cell
def _(undual, v):
    undual(v)
    return


@app.cell
def _(norm, v):
    norm(v)
    return


@app.cell
def _(unit, v):
    unit(v)
    return


@app.cell
def _(inverse, v):
    inverse(v)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Even / Odd Grades, Squared
    """)
    return


@app.cell
def _(A, even_grades):
    even_grades(A)
    return


@app.cell
def _(odd_grades, v):
    odd_grades(v)
    return


@app.cell
def _(R, squared):
    squared(R)
    return


@app.cell
def _(mo):
    mo.md("""
    ## Arithmetic & Operator Sugar
    """)
    return


@app.cell
def _(a, b):
    a + b
    return


@app.cell
def _(a, b):
    a - b
    return


@app.cell
def _(a):
    3 * a
    return


@app.cell
def _(R, a, b):
    # Parenthesization is automatic
    (a + b) * R
    return


@app.cell
def _(mo):
    mo.md("""
    ## Evaluating Expressions
    """)
    return


@app.cell
def _(R, a, b, grade, inverse, mo, norm, op, v):
    exprs = [
        ("Wedge", op(a, b)),
        ("Norm", norm(v)),
        ("Inverse", inverse(a)),
        ("Sandwich", grade(R * v * ~R, 1)),
    ]
    mo.vstack([
        mo.md(f"**{name}:** {e.latex(wrap='$')} = `{e.eval()}`")
        for name, e in exprs
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ## Rotation Demo
    """)
    return


@app.cell
def _(alg, e1, e2, grade, mo, np, sym):
    theta = np.pi / 2
    Bplane = e1 ^ e2
    Rot = alg.rotor_from_plane_angle(Bplane, theta)

    R_sym = sym(Rot, "R")
    v_sym = sym(e1, "v")
    rotated = grade(R_sym * v_sym * ~R_sym, 1)

    mo.vstack([
        mo.md(f"Rotate $v = e_1$ by $90°$ in the $e_1 e_2$ plane:"),
        rotated,
        mo.md(f"Result: `{rotated.eval()}`"),
    ])
    return


@app.cell
def _(mo):
    mo.md("""
    ## LaTeX Output
    Every expression has `.latex()` for raw LaTeX and `.latex(wrap='$')` for inline math.
    """)
    return


@app.cell
def _(R, grade, mo, v):
    sandwich = grade(R * v * ~R, 1)
    mo.vstack([
        mo.md(f"`.latex()` → `{sandwich.latex()}`"),
        mo.md(f"`.latex(wrap='$')` → {sandwich.latex(wrap='$')}"),
    ])
    return


@app.cell
def _():
    return


@app.cell
def _(mo):
    mo.md("""
    ## Interactive Rotor
    Drag the slider to rotate $e_1$ in the $e_1 e_2$ plane.
    """)
    return


@app.cell
def _(mo):
    angle_slider = mo.ui.slider(
        start=0, stop=360, step=1, value=90, label="Angle (degrees)"
    )
    angle_slider
    return (angle_slider,)


@app.cell
def _(alg, angle_slider, e1, e2, grade, mo, np, sym):
    _theta = np.radians(angle_slider.value)
    _B = e1 ^ e2
    _R = alg.rotor_from_plane_angle(_B, _theta)
    _v = e1

    R_s = sym(_R, "R")
    v_s = sym(_v, "v")
    _expr = grade(R_s * v_s * ~R_s, 1)
    _result = _expr.eval()

    mo.vstack([
        mo.md(f"$\\theta = {angle_slider.value}°$"),
        mo.md(f"Symbolic: {_expr.latex(wrap='$')}"),
        mo.md(f"Result: $\\;$ `{_result}`"),
    ])
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
