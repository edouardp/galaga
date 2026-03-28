import marimo

__generated_with = "0.21.1"
app = marimo.App()


@app.cell
def _():
    import sys
    from pathlib import Path

    _root = str(Path(__file__).resolve().parent.parent)
    _gamo = str(Path(__file__).resolve().parent.parent / "packages" / "galaga_marimo")
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

    from galaga import Algebra, exp, norm, sandwich
    from galaga.notation import Notation, NotationRule
    import galaga_marimo as gm

    return Algebra, NotationRule, exp, gm, mo, norm, np, plt, sandwich


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Kepler Orbits with Geometric Algebra

    The Kepler problem is naturally planar. Geometric algebra makes the angular
    momentum plane and the oriented area structure explicit instead of hiding them
    inside cross products and coordinate determinants.
    """)
    return


@app.cell
def _(Algebra, NotationRule):
    alg = Algebra((1, 1, 1), repr_unicode=True)
    e1, e2, e3 = alg.basis_vectors(lazy=True)
    alg.notation.set("Reverse", "latex", NotationRule(kind="superscript", symbol=r"\dagger"))
    return alg, e1, e2


@app.cell
def _(mo):
    eccentricity = mo.ui.slider(start=0.0, stop=0.95, step=0.01, value=0.45, label="eccentricity")
    semilatus = mo.ui.slider(start=1.0, stop=10.0, step=0.1, value=4.0, label="semilatus rectum")
    anomaly = mo.ui.slider(start=0, stop=360, step=1, value=80, label="true anomaly")
    mo.vstack([eccentricity, semilatus, anomaly])
    return anomaly, eccentricity, semilatus


@app.cell(hide_code=True)
def _(alg, anomaly, e1, e2, eccentricity, exp, gm, np, sandwich, semilatus):
    _theta = alg.scalar(np.radians(anomaly.value)).name(latex=r'\theta')
    _plane = (e1 ^ e2).name(latex=r"B_{o}")
    _rotor = exp(-(_theta / 2) * _plane)
    _radial = sandwich(_rotor, e1)
    _tangent = sandwich(_rotor, e2)
    _r = semilatus.value / (1 + eccentricity.value * np.cos(_theta.scalar_part))
    _position = _r * _radial
    gm.md(t"""
    ## Orbital Plane

    Rotor for the true anomaly: {_rotor} = {_rotor.eval()}

    Orbital plane bivector: {_plane} = {_plane.eval()}

    Radial unit vector: {_radial} = {_radial.eval()}

    Tangential unit vector: {_tangent} = {_tangent.eval()}

    Current orbital position: {_position} = {_position.eval()}
    """)
    return


@app.cell
def _(alg, anomaly, e1, e2, eccentricity, exp, gm, norm, np, semilatus):
    _e = eccentricity.value
    _p = semilatus.value
    _theta = alg.scalar(np.radians(anomaly.value)).name(latex=r"\theta")
    _plane = (e1 * e2).name("B")
    _R = exp(-(_theta / 2) * _plane)
    _radial = (_R * e1 * ~_R).name(latex=r"\hat{v_{\theta}}")
    _tangent = _R * e2 * ~_R
    _r = alg.scalar(_p / (1 + _e * np.cos(_theta.scalar_part))).name("r")
    _hodograph_center = ((_e / np.sqrt(_p)) * e2).name(latex=r"c_{hodograph}")
    _position = _r * _radial
    _velocity = _hodograph_center + _tangent / np.sqrt(_p)
    _L = _position ^ _velocity

    gm.md(t"""
    Orbital Plane: {_plane} = {_plane.eval()}

    {_radial} = {_radial.reveal()} = {_radial.eval()} <br/>
    **Position vector**: {_position} = {_position.eval()} <br/>
    **Velocity vector**: {_velocity} = {_velocity.eval()}

    The hodograph is a circle because

    $$
    v(\\theta) = \\frac{{1}}{{\\sqrt{{p}}}}\\,\\hat{{\\theta}}(\\theta) + \\frac{{e}}{{\\sqrt{{p}}}} e_2,
    $$

    so the velocity tip is a unit rotor orbit translated by the fixed vector
    {_hodograph_center} = {_hodograph_center.reveal()} = {_hodograph_center.eval()}.

    Angular momentum bivector: {_L} = {_L.eval()}

    Its magnitude is {norm(_L.eval()):.6f}.
    """)
    return


@app.cell(hide_code=True)
def _(anomaly, e1, e2, eccentricity, exp, np, plt, sandwich, semilatus):
    _e = eccentricity.value
    _p = semilatus.value
    _e1 = e1.eval()
    _e2 = e2.eval()

    def _sample(theta):
        _rotor = exp(-(theta / 2) * (_e1 * _e2))
        _radial = sandwich(_rotor, _e1).eval()
        _tangent = sandwich(_rotor, _e2).eval()
        _radius = _p / (1 + _e * np.cos(theta))
        _position = _radius * _radial
        _velocity = (_e / np.sqrt(_p)) * _e2 + _tangent / np.sqrt(_p)
        return _position, _velocity

    _ths = np.linspace(0, 2 * np.pi, 500)
    _positions, _velocities = zip(*[_sample(_theta) for _theta in _ths])
    _x = np.array([_pos.vector_part[0] for _pos in _positions])
    _y = np.array([_pos.vector_part[1] for _pos in _positions])

    _th = np.radians(anomaly.value)
    _position_now, _velocity_now = _sample(_th)
    _xp, _yp = _position_now.vector_part[:2]

    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(11, 4.5))
    _ax1.plot(_x, _y, color="steelblue", linewidth=2.5)
    _ax1.plot([0], [0], "yo", ms=10)
    _ax1.plot([_xp], [_yp], "ko", ms=7)
    _ax1.set_aspect("equal")
    _ax1.set_title("Kepler orbit in configuration space")
    _ax1.grid(True, alpha=0.2)

    _vxs = np.array([_vel.vector_part[0] for _vel in _velocities])
    _vys = np.array([_vel.vector_part[1] for _vel in _velocities])
    _vx, _vy = _velocity_now.vector_part[:2]
    _ax2.plot(_vxs, _vys, color="crimson", linewidth=2.5)
    _ax2.plot([0], [_e / np.sqrt(_p)], "yo", ms=10)
    _ax2.plot([_vx], [_vy], "ko", ms=7)
    _ax2.set_aspect("equal")
    _ax2.set_title("Velocity-space hodograph")
    _ax2.grid(True, alpha=0.2)
    _fig.tight_layout()
    _fig
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
