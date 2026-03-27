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
    mo.md("""
    # PGA Geometry Constructions

    This notebook focuses on projective geometry rather than rigid-motion motors.
    Points, lines, and joins are written with lazy blades first so the construction
    is legible, then evaluated for coordinates and plotting.
    """)
    return


@app.cell
def _(Algebra):
    pga = Algebra((1, 1, 1, 0), repr_unicode=True)
    e1, e2, e3, e0 = pga.basis_vectors(lazy=True)
    e123 = (e1 ^ e2 ^ e3).name(latex=r"e_{123}")
    E1 = (e2 ^ e3 ^ e0).name("E_1", latex=r"E_1")
    E2 = (-(e1 ^ e3 ^ e0)).name("E_2", latex=r"E_2")
    E3 = (e1 ^ e2 ^ e0).name("E_3", latex=r"E_3")
    return E1, E2, E3, e0, e1, e123, e2


@app.cell
def _(E1, E2, E3, complement, e0, e1, e123, e2, np):
    def point(x, y, z=0.0):
        return (e123 + x * E1 + y * E2 + z * E3).name(latex=rf"P({x:.1f},{y:.1f},{z:.1f})")

    def opns_point(P):
        return complement(P)

    def blade_coefficient(mv, blade):
        _mv = mv.eval()
        _blade = blade.eval()
        _nz = np.flatnonzero(np.abs(_blade.data) > 1e-12)
        if len(_nz) != 1:
            raise ValueError("blade_coefficient expects a single basis blade")
        _idx = int(_nz[0])
        return _mv.data[_idx] / _blade.data[_idx]

    def join_line(P, Q):
        return (opns_point(P) ^ opns_point(Q)).name("ℓ", latex=r"\ell")

    def line_equation(join):
        _c = blade_coefficient(join, e1 ^ e2)
        _a = blade_coefficient(join, e2 ^ e0)
        _b = -blade_coefficient(join, e1 ^ e0)
        return _a, _b, -_c

    def join_triangle(P, Q, R):
        return (opns_point(P) ^ opns_point(Q) ^ opns_point(R)).name("Π", latex=r"\Pi")

    def triangle_area(join):
        return 0.5 * abs(blade_coefficient(join, e1 ^ e2 ^ e0))

    def coords(P):
        _P = P.eval()
        _w = _P.data[7]
        return np.array([_P.data[14] / _w, -_P.data[13] / _w, _P.data[11] / _w])

    return (
        coords,
        join_line,
        join_triangle,
        line_equation,
        point,
        triangle_area,
    )


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Join Two Points to Make a Line

    These notebook points are stored as trivectors, so we first convert them to
    their OPNS 1-vector form with `complement(...)`. Then the outer product gives
    the projective join.

    In the plane `z=0`, the joined line can still be read as `ax + by + c = 0`.
    """)
    return


@app.cell
def _(mo):
    ax = mo.ui.slider(start=-3.0, stop=3.0, step=0.1, value=-1.2, label="A_x")
    ay = mo.ui.slider(start=-3.0, stop=3.0, step=0.1, value=-0.4, label="A_y")
    bx = mo.ui.slider(start=-3.0, stop=3.0, step=0.1, value=1.8, label="B_x")
    by = mo.ui.slider(start=-3.0, stop=3.0, step=0.1, value=1.2, label="B_y")
    mo.vstack([ax, ay, bx, by])
    return ax, ay, bx, by


@app.cell
def _(ax, ay, bx, by, gm, join_line, line_equation, point):
    A = point(ax.value, ay.value).name("A")
    B = point(bx.value, by.value).name("B")
    line = join_line(A, B)
    _a, _b, _c = line_equation(line)
    gm.md(t"""
    {A} = {A.eval()}

    {B} = {B.eval()}

    {line} = {line.eval()}

    Plane coordinates of $\\ell$: {_a:.3f}x + {_b:.3f}y + {_c:.3f} = 0
    """)
    return A, B, line


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Triangle Area from the Join Structure

    Joining the OPNS forms of three points produces an ideal trivector in the
    `xy` slice. Its coefficient on $e_1 e_2 e_0$ is twice the oriented area.
    """)
    return


@app.cell
def _(A, B, gm, join_triangle, point, triangle_area):
    C = point(0.3, 2.1).name("C")
    triangle = join_triangle(A, B, C)
    area = triangle_area(triangle)

    gm.md(t"""
    {C} = {C.eval()}

    {triangle} = {triangle.eval()}

    Triangle area = {area:.3f}
    """)
    return (C,)


@app.cell
def _(A, B, C, coords, line, line_equation, np, plt):
    _pts = np.array([coords(A), coords(B), coords(C)])
    _fig, _ax = plt.subplots(figsize=(6, 6))
    _ax.fill(_pts[:, 0], _pts[:, 1], color="goldenrod", alpha=0.25)
    _ax.plot([_pts[0, 0], _pts[1, 0]], [_pts[0, 1], _pts[1, 1]], color="crimson", linewidth=2)
    _ax.scatter(_pts[:, 0], _pts[:, 1], color="black", zorder=5)
    for _label, _pt in zip(["A", "B", "C"], _pts):
        _ax.text(_pt[0] + 0.07, _pt[1] + 0.07, _label)
    _x = np.linspace(-3.5, 3.5, 200)
    _a, _b, _c = line_equation(line)
    if abs(_b) > 1e-9:
        _y = -(_a * _x + _c) / _b
        _ax.plot(_x, _y, "k--", alpha=0.5)
    _ax.set_xlim(-3.5, 3.5)
    _ax.set_ylim(-3.0, 3.0)
    _ax.set_aspect("equal")
    _ax.grid(True, alpha=0.2)
    _ax.set_title("Points, line join, and oriented triangle in PGA")
    _fig.tight_layout()
    _fig


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
