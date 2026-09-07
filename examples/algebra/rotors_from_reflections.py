import marimo

__generated_with = "0.23.14"
app = marimo.App()


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from galaga import Algebra
    import galaga_marimo as gm

    return Algebra, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Rotors from Reflections

    A Euclidean rotation can be built as two reflections. In geometric algebra this
    is not a trick or a special case: it is the basic construction behind rotors.
    The sliders specify the directions of the mirror lines. Their normals
    are perpendicular to those lines.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1), )
    e1, e2 = alg.basis_vectors(expr=True)
    return e1, e2


@app.cell
def _(mo):
    alpha = mo.ui.slider(start=0, stop=180, step=1, value=20, label="first mirror angle")
    beta = mo.ui.slider(start=0, stop=180, step=1, value=65, label="second mirror angle")
    vector_angle = mo.ui.slider(start=0, stop=180, step=1, value=15, label="input vector angle")
    mo.vstack([alpha, beta, vector_angle])
    return alpha, beta, vector_angle


@app.cell(hide_code=True)
def _(alpha, beta, e1, e2, gm, np, vector_angle):
    _a = np.radians(alpha.value)
    _b = np.radians(beta.value)
    _v = np.radians(vector_angle.value)
    _n1 = -np.sin(_a) * e1 + np.cos(_a) * e2
    _n2 = -np.sin(_b) * e1 + np.cos(_b) * e2
    _x = np.cos(_v) * e1 + np.sin(_v) * e2
    _x1 = -_n1 * _x * _n1
    _x2 = -_n2 * _x1 * _n2
    _R = _n2 * _n1
    assert np.allclose((_R * _x * ~_R).data, _x2.data, rtol=0, atol=1e-12)
    mirror_normals = (_n1, _n2)
    reflection_input = _x
    reflected_once, reflected_twice = _x1, _x2
    reflection_rotor = _R

    gm.md(rt"""
    ## Reflection Composition

    First unit normal: {_n1}

    Second unit normal: {_n2}

    After first reflection: {_x1}

    After second reflection: {_x2}

    Rotor from the mirror pair: {_R}
    """)
    return mirror_normals, reflected_once, reflected_twice, reflection_input, reflection_rotor


@app.cell
def _(alpha, beta, np, plt, reflected_once, reflected_twice, reflection_input):
    _a = np.radians(alpha.value)
    _b = np.radians(beta.value)
    _x = reflection_input.vector_part
    _once = reflected_once.vector_part
    _y = reflected_twice.vector_part

    reflection_figure, _ax = plt.subplots(figsize=(6, 6))
    _m1 = np.array([np.cos(_a), np.sin(_a)])
    _m2 = np.array([np.cos(_b), np.sin(_b)])
    _ax.plot([-2 * _m1[0], 2 * _m1[0]], [-2 * _m1[1], 2 * _m1[1]], color="steelblue", alpha=0.5, label="mirror 1")
    _ax.plot([-2 * _m2[0], 2 * _m2[0]], [-2 * _m2[1], 2 * _m2[1]], color="darkorange", alpha=0.5, label="mirror 2")
    _ax.quiver(0, 0, _x[0], _x[1], angles="xy", scale_units="xy", scale=1, color="black", width=0.012, label="input")
    _ax.quiver(0, 0, _once[0], _once[1], angles="xy", scale_units="xy", scale=1, color="darkorange", width=0.012, label="first reflection")
    _ax.quiver(0, 0, _y[0], _y[1], angles="xy", scale_units="xy", scale=1, color="crimson", width=0.012, label="second reflection")
    _ax.set_aspect("equal")
    _ax.set_xlim(-2, 2)
    _ax.set_ylim(-2, 2)
    _ax.set_title("Two reflections compose to a rotation")
    _ax.grid(True, alpha=0.2)
    _ax.legend()
    reflection_figure.tight_layout()
    reflection_figure
    return (reflection_figure,)


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Why the inverse matters

    The general normal-reflection formula is $-n v n^{-1}$. Here the normals
    have square $+1$, so their inverse equals the normal itself. For a scaled
    or negative-square normal, use `inverse(n)` explicitly. `sandwich(R,v)`
    always means $R v \widetilde R$; it does not substitute an inverse.

    Two reflections compose in the order $R=n_2n_1$. In a Euclidean unit
    plane, $R=\exp(-\theta B/2)$ rotates by $\theta$. Check $B^2$ before using
    sine/cosine: a positive square gives a hyperbolic exponential, while a
    null bivector gives a terminating exponential.
    """)
    return


if __name__ == "__main__":
    app.run()
