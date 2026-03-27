import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent / "packages" / "gamo")
    for p in [_root, _gamo]:
        if p not in sys.path:
            sys.path.insert(0, p)
    return


@app.cell
def _():
    import marimo as mo
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from ga import Algebra, complement
    import galaga_marimo as gm

    return Algebra, complement, gm, mo, np, plt


@app.cell(hide_code=True)
def _(mo):
    mo.md(
        """
        # Thin Lens and Rays in PGA

        PGA is good for teaching optics because rays and image geometry are projective
        objects. This notebook uses a paraxial thin-lens model but keeps the geometry
        front and center: object point, lens plane, focal plane, and image point.
        """
    )
    return


@app.cell
def _(Algebra):
    pga = Algebra((1, 1, 1, 0), repr_unicode=True)
    e1, e2, e3, e0 = pga.basis_vectors(lazy=True)
    e123 = e1 ^ e2 ^ e3
    E1 = e2 ^ e3 ^ e0
    E2 = -(e1 ^ e3 ^ e0)
    E3 = e1 ^ e2 ^ e0
    return E1, E2, E3, complement, e0, e1, e2, e123


@app.cell
def _(E1, E2, E3, e123, np):
    def point(x, y, z=0.0):
        return e123 + x * E1 + y * E2 + z * E3

    def coords(P):
        _P = P.eval()
        _w = _P.data[7]
        return np.array([_P.data[14] / _w, -_P.data[13] / _w, _P.data[11] / _w])

    return coords, point


@app.cell
def _(mo):
    object_distance = mo.ui.slider(start=1.0, stop=12.0, step=0.1, value=6.0, label="object distance")
    focal_length = mo.ui.slider(start=0.5, stop=8.0, step=0.1, value=2.0, label="focal length")
    object_height = mo.ui.slider(start=0.2, stop=3.0, step=0.1, value=1.2, label="object height")
    mo.vstack([object_distance, focal_length, object_height])
    return focal_length, object_distance, object_height


@app.cell(hide_code=True)
def _(coords, focal_length, gm, object_distance, object_height, point):
    s = object_distance.value
    f = focal_length.value
    h = object_height.value
    sp = np.inf if abs(s - f) < 1e-9 else 1.0 / (1.0 / f - 1.0 / s)
    m = -sp / s if np.isfinite(sp) else np.nan

    object_tip = point(-s, h, 0)
    lens_center = point(0, 0, 0)
    focus_right = point(f, 0, 0)
    image_tip = point(sp, m * h, 0) if np.isfinite(sp) else point(20, 0, 0)

    gm.md(t"""
    ## Lens Equation

    Object tip {object_tip} = {object_tip.eval()}

    Lens center {lens_center} = {lens_center.eval()}

    Right focal point {focus_right} = {focus_right.eval()}

    Image tip {image_tip} = {image_tip.eval()}

    Thin-lens formula:

    $$
    \\frac{{1}}{{f}} = \\frac{{1}}{{s}} + \\frac{{1}}{{s'}}
    $$

    Here $s = {s:.3f}$, $f = {f:.3f}$, and $s' = {sp if np.isfinite(sp) else np.inf:.3f}$.
    """)
    return image_tip, lens_center, object_tip, sp


@app.cell
def _(focal_length, image_tip, lens_center, np, object_distance, object_height, plt, sp):
    s = object_distance.value
    f = focal_length.value
    h = object_height.value
    _fig, _ax = plt.subplots(figsize=(10, 4.5))

    _ax.axvline(0, color="black", linewidth=2, alpha=0.5)
    _ax.plot([-s, -s], [0, h], color="steelblue", linewidth=3, label="object")
    if np.isfinite(sp):
        _img = image_tip.eval()
        _ix = _img.data[14]
        _iy = -_img.data[13]
        _ax.plot([_ix, _ix], [0, _iy], color="crimson", linewidth=3, label="image")
    _ax.plot([-f, f], [0, 0], "ko", ms=6)
    _ax.text(-f, -0.25, "F", ha="center")
    _ax.text(f, -0.25, "F'", ha="center")

    _ax.plot([-s, 0], [h, h], color="darkorange", linewidth=2)
    if np.isfinite(sp):
        _ax.plot([0, sp], [h, 0], color="darkorange", linewidth=2)
        _ax.plot([-s, sp], [h, 0], color="seagreen", linewidth=2)

    _ax.set_xlim(-max(1.5 * s, 2), max(1.5 * (sp if np.isfinite(sp) else s), 4))
    _ax.set_ylim(-3.0, 3.0)
    _ax.set_xlabel("optical axis")
    _ax.set_ylabel("height")
    _ax.set_title("Thin lens image construction")
    _ax.grid(True, alpha=0.2)
    _ax.legend()
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
