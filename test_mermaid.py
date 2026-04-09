import marimo

__generated_with = "0.22.5"
app = marimo.App(width="medium")


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent)
    _gamo = str(Path(__file__).resolve().parent / "packages" / "galaga_marimo")
    for p in [_root, _gamo]:
        if p not in sys.path:
            sys.path.insert(0, p)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np

    from galaga import Algebra, exp, op, sandwich
    from galaga.mermaid import mv_to_mermaid

    return Algebra, exp, mo, mv_to_mermaid, np, op, sandwich


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Mermaid Expression Tree Demo

    Build a rotor from two vectors, apply it via sandwich product,
    then visualise the full expression tree as a Mermaid diagram.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra(3, repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    return alg, e1, e2, e3


@app.cell
def _(mo):
    d_slider = mo.ui.slider(start=0, stop=360, step=5, value=60, label="angle d (degrees)")
    d_slider  # noqa: B018
    return (d_slider,)


@app.cell
def _(alg, d_slider, e1, e2, e3, exp, np, op):
    a = (e1 + e2).name("a")
    b = e3.name("b")
    B = op(a, b).name("B")
    d = alg.scalar(np.radians(d_slider.value)).name("d")
    R = exp(-B * d / 2).name("R")
    return (R,)


@app.cell
def _(R, e1, e2, e3, mo, sandwich):
    v = (3 * e1 + e2 - 2 * e3).name("v")
    v_rot = sandwich(R, v)

    mo.md(
        f"""
    ## Sandwich Product: R v R̃

    **v** = `{v.eval()}`

    **v′** = `{v_rot.eval()}`
    """
    )
    return (v_rot,)


@app.cell
def _(mo):
    mo.md("""
    ## Expression Tree for v′ = R v R̃
    """)
    return


@app.cell
def _(mo, mv_to_mermaid, v_rot):
    _diagram = mv_to_mermaid(v_rot)
    mo.mermaid(_diagram)
    return


if __name__ == "__main__":
    app.run()
