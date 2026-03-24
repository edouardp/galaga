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


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
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
    return A, B, R, a, alg, b, e1, e2, e3, v


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
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
    mo.hstack([mo.md("Evaluating:"), sandwich_expr, mo.md("="), sandwich_expr.eval()], justify="start")
    return


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
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
        mo.hstack([mo.md(f"**{name}:**"), e, mo.md("="), e.eval()], justify="start")
        for name, e in exprs
    ])
    return


@app.cell(hide_code=True)
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
        mo.md(r"Rotate $v = e_1$ by $90°$ in the $e_1 e_2$ plane:"),
        mo.hstack([rotated, mo.md("="), rotated.eval()], justify="start"),
    ])
    return


@app.cell(hide_code=True)
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


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Simplification
    `simplify()` applies algebraic rewrite rules to expression trees.
    """)
    return


@app.cell
def _(R, a, grade, inverse, mo, norm, unit, v):
    from ga.symbolic import simplify

    _rules = [
        ("~~v", simplify(~~v)),
        ("inverse(inverse(v))", simplify(inverse(inverse(v)))),
        ("a ∧ a", simplify(a ^ a)),
        ("a + a", simplify(a + a)),
        ("3(2v)", simplify(3 * (2 * v))),
        ("R~R", simplify(R * ~R)),
        ("‖unit(v)‖", simplify(norm(unit(v)))),
        ("⟨v⟩₁ (v is grade-1)", simplify(grade(v, 1))),
        ("⟨v⟩₂ (v is grade-1)", simplify(grade(v, 2))),
        ("a − (−a)", simplify(a - (-a))),
    ]
    mo.md("\n".join(f"- `{name}` → ${result.latex()}$" for name, result in _rules))
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Extracting Components
    Use `.vector_part` and `.scalar_part` to get numpy-friendly data.
    """)
    return


@app.cell
def _(alg, e1, e2, e3, mo):
    _v = 3 * e1 + 4 * e2 + 5 * e3
    _mv = alg.scalar(7) + _v + (e1 ^ e2)
    mo.vstack([
        mo.md(f"`v = 3e₁ + 4e₂ + 5e₃`"),
        mo.md(f"`v.vector_part` → `{_v.vector_part}`"),
        mo.md(f"`v.scalar_part` → `{_v.scalar_part}`"),
        mo.md(f""),
        mo.md(f"`mv = 7 + v + e₁₂`"),
        mo.md(f"`mv.vector_part` → `{_mv.vector_part}`"),
        mo.md(f"`mv.scalar_part` → `{_mv.scalar_part}`"),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Interactive Rotor
    Drag the slider to rotate $e_1$ in the $e_1 e_2$ plane.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    angle_slider = mo.ui.slider(
        start=0, stop=360, step=1, value=90, label="Angle (degrees)"
    )
    angle_slider
    return (angle_slider,)


@app.cell
def _(alg, angle_slider, e1, e2, grade, mo, np, sym):
    _theta = np.radians(angle_slider.value)
    _R = alg.rotor_from_plane_angle(e1 ^ e2, _theta)

    _R_s = sym(_R, "R")
    _v_s = sym(e1, "v")
    _expr = grade(_R_s * _v_s * ~_R_s, 1)

    mo.vstack([
        mo.md(f"$\\theta = {angle_slider.value}°$"),
        mo.hstack([mo.md("Symbolic:"), _expr]),
        mo.hstack([mo.md("Result:"), _expr.eval()]),
    ])
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## 2D Rotation Visualizer
    Drag the slider to rotate $e_1$ (blue) → rotated vector (red) in the $e_1 e_2$ plane.
    """)
    return


@app.cell
def _(mo):
    plot_angle = mo.ui.slider(
        start=0, stop=360, step=1, value=45, label="θ (degrees)"
    )
    plot_angle
    return (plot_angle,)


@app.cell(hide_code=True)
def _(alg, e1, e2, grade, np, plot_angle, sym):
    import matplotlib.pyplot as plt
    import matplotlib
    matplotlib.rcParams.update({"figure.facecolor": "white"})

    _theta = np.radians(plot_angle.value)
    _R = alg.rotor_from_plane_angle(e1 ^ e2, _theta)
    _v_rot = _R * e1 * ~_R

    # Extract x,y components
    _vx, _vy, _ = _v_rot.vector_part

    fig, ax = plt.subplots(figsize=(5, 5))
    ax.set_xlim(-1.4, 1.4)
    ax.set_ylim(-1.4, 1.4)
    ax.set_aspect("equal")
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color="k", lw=0.5)
    ax.axvline(0, color="k", lw=0.5)

    # Draw unit circle
    _t = np.linspace(0, 2 * np.pi, 100)
    ax.plot(np.cos(_t), np.sin(_t), "k-", alpha=0.1)

    # Original vector (e1)
    ax.quiver(0, 0, 1, 0, angles="xy", scale_units="xy", scale=1, color="steelblue", width=0.02, label="$e_1$")
    # Rotated vector
    ax.quiver(0, 0, _vx, _vy, angles="xy", scale_units="xy", scale=1, color="crimson", width=0.02, label=f"$R e_1 \\tilde{{R}}$")

    # Arc showing angle
    _arc_t = np.linspace(0, _theta, 50)
    ax.plot(0.3 * np.cos(_arc_t), 0.3 * np.sin(_arc_t), "k-", alpha=0.4)

    ax.legend(loc="upper left", fontsize=12)
    ax.set_title(f"θ = {plot_angle.value}°", fontsize=14)

    # Symbolic expression
    _R_s = sym(_R, "R")
    _v_s = sym(e1, "v")
    _expr = grade(_R_s * _v_s * ~_R_s, 1)

    plt.tight_layout()
    fig
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
