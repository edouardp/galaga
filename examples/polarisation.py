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

    return (mo,)


@app.cell
def _():
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib

    matplotlib.rcParams.update({"figure.facecolor": "white"})

    from ga import Algebra, gp, scalar, norm, unit, exp, squared, grade
    from ga.symbolic import simplify, sym
    import galaga_marimo as gm

    return Algebra, exp, gm, grade, norm, np, plt, squared, sym, unit


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    # Polarisation Optics with Geometric Algebra

    Light polarisation lives in a 2D transverse plane. A polariser is a
    **projector** — it keeps the component of the electric field along its
    axis and discards the rest.
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1))
    e1, e2 = alg.basis_vectors(lazy=True)
    return e1, e2


@app.cell
def _(grade):
    def polarise(E, a):
        """Ideal linear polariser: keep component along unit axis a."""
        return grade((E * a) * a, 0)

    return (polarise,)


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Polarisation Axes

    $$P_a(E) = (E \\cdot a)\\,a$$
    """)
    return


@app.cell
def _(R, e1, e2, exp, gm, np, sym):
    H = sym(e1,'H')
    V = sym(e2,'V')
    #D = unit(e1 + e2).name("D")

    R_45 = exp(e1 ^ e2 * np.pi)

    D = R*H*~R

    gm.md(t"""
    - Horizontal: {H} = {H.eval()}
    - Vertical: {V} = {V.eval()}
    - Diagonal (45°): {D} = {D.eval()}
    """)
    return D, H, V


@app.cell
def _(D):
    D
    return


@app.cell
def _(e1):
    e1
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## H Blocks V")
    return


@app.cell
def _(H, V, gm, norm, polarise, squared, sym):
    _E0 = sym(H, 'E0').name(latex=r"E_0")
    _E1 = polarise(_E0, V).name(latex=r"E_1")
    _I1 = squared(norm(_E1))

    gm.md(t"""
    {_E0} = {_E0.eval()} (horizontal input)

    After vertical polariser: {_E1} = {_E1.eval()}

    Intensity: {_I1} = {_I1.eval()}  — **completely blocked**.
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## The Three-Polariser Trick")
    return


@app.cell
def _(D, H, V, gm, norm, polarise, squared, sym):
    _E0 = sym(H, 'E0').name(latex=r"E_0")
    _E1 = polarise(_E0, D).name(latex=r"E_1")
    _E2 = polarise(_E1, V).name(latex=r"E_2")
    _I1 = squared(norm(_E2))

    gm.md(t"""
    {_E0} = {_E0.eval()}

    After 45° polariser: {_E1} = {_E1.eval()}

    After vertical polariser: {_E2} = {_E2.eval()}

    Intensity: {_I1} = {_I1.eval()} — **quarter gets through!**
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Interactive: Vary the Middle Polariser")
    return


@app.cell
def _(mo):
    angle_slider = mo.ui.slider(
        start=0, stop=90, step=1, value=45,
        label="Middle polariser angle (degrees)"
    )
    angle_slider
    return (angle_slider,)


@app.cell
def _(
    E0,
    E1,
    E2,
    H,
    V,
    angle_slider,
    e1,
    e2,
    gm,
    norm,
    np,
    polarise,
    squared,
    sym,
    unit,
):
    _deg = angle_slider.value
    _rad = np.radians(_deg)
    _M = unit(np.cos(_rad) * e1 + np.sin(_rad) * e2).name("M")

    _E0 = sym(H, 'E0').name(latex=r"E_0")
    _E1 = polarise(_E0, _M).name(latex=r"E_1")
    _E2 = polarise(_E1, V).name(latex=r"E_2")
    _I_out = squared(norm(_E2))

    gm.md(t"""
    Middle polariser {_M} at **{_deg}°** $\\quad$ ({_M} = {_M.eval()})

    {E0} → {E1} = {E1.eval()} → {E2} = {E2.eval()}

    **Output intensity:** {_I_out} = {_I_out.eval()}

    Theory: $\\frac{{1}}{{4}}\\sin^2(2 \\times {_deg}°)$ = {0.25 * np.sin(2 * _rad)**2:.4f}
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Malus' Law — Full Curve")
    return


@app.cell
def _(H, V, e1, e2, norm, np, plt, polarise, unit):
    _angles = np.linspace(0, 90, 200)
    _intensities = []

    for _deg in _angles:
        _rad = np.radians(_deg)
        _mid = unit(np.cos(_rad) * e1.eval() + np.sin(_rad) * e2.eval())
        _E1 = polarise(H, _mid)
        _E2 = polarise(_E1, V)
        _intensities.append(norm(_E2.eval()) ** 2)

    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.plot(_angles, _intensities, 'b-', linewidth=2, label='GA computation')
    _ax.plot(_angles, 0.25 * np.sin(2 * np.radians(_angles))**2,
             'r--', linewidth=1.5, label=r'$\frac{1}{4}\sin^2(2\theta)$')
    _ax.set_xlabel('Middle polariser angle (degrees)')
    _ax.set_ylabel('Transmitted intensity')
    _ax.set_title("Three-Polariser Transmission (Malus' Law)")
    _ax.legend()
    _ax.set_xlim(0, 90)
    _ax.set_ylim(-0.01, 0.3)
    _ax.grid(True, alpha=0.3)
    _fig
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## GA Reflection Form

    $$P_a(E) = \\frac{{1}}{{2}}(E + aEa)$$

    The sandwich $aEa$ reflects $E$ in axis $a$. Averaging keeps the parallel component.
    """)
    return


@app.cell
def _(D, H, V, gm, norm):
    def polarise_ga(E, a):
        Ev, av = E.eval(), a.eval()
        return 0.5 * (Ev + av * Ev * av)

    E1 = polarise_ga(H, D).name(latex=r"E_1")
    E2 = polarise_ga(E1, V).name(latex=r"E_2")

    gm.md(t"""
    {E1} = {E1.eval()}

    {E2} = {E2.eval()}

    $|{E2.latex()}|^2$ = {norm(E2.eval())**2:.4f} — same result.
    """)
    return E1, E2


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Waveplates as Rotors

    A half-wave plate is a rotor $R = e^{{-B\\theta}}$ where $B = e_1 \\wedge e_2$.
    """)
    return


@app.cell
def _(e1, e2, exp, gm, norm, np, sym):
    B = (e1 ^ e2)
    R = exp(-B * np.pi / 4).name("R")

    E0 = sym(e1).name(latex=r"E_0")
    E_rot = (R * E0 * ~R).name(latex=r"E_{rot}")

    gm.md(t"""
    Half-wave plate at 45°: {R} = {R.eval()}

    Input: {E0} = {E0.eval()}

    Output: {E_rot} = {E_rot.eval()}

    Intensity preserved: $|{E_rot.latex()}|^2$ = {norm(E_rot.eval())**2:.4f}
    """)
    return E0, R


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"## Polarisation State Diagram")
    return


@app.cell
def _(D, H, V, np, plt, polarise):
    _E0 = H.eval()
    _E1 = polarise(H, D).eval()
    _E2 = polarise(_E1, V).eval()

    _fig, _ax = plt.subplots(figsize=(6, 6))

    for _E, _label, _color in [(_E0, "E₀ (H)", "blue"), (_E1, "E₁ (45°)", "green"), (_E2, "E₂ (V)", "red")]:
        _x, _y = _E.data[1], _E.data[2]
        _ax.annotate("", xy=(_x, _y), xytext=(0, 0),
                     arrowprops=dict(arrowstyle="->", color=_color, lw=2.5))
        _ax.annotate(_label, xy=(_x, _y), fontsize=10, color=_color,
                     xytext=(5, 5), textcoords="offset points")

    for _a, _name, _ls in [(H.eval(), "H", "--"), (D.eval(), "D", ":"), (V.eval(), "V", "-.")]:
        _ax.plot([-_a.data[1]*1.2, _a.data[1]*1.2],
                 [-_a.data[2]*1.2, _a.data[2]*1.2],
                 color="gray", linestyle=_ls, alpha=0.5, label=_name)

    _t = np.linspace(0, 2 * np.pi, 100)
    _ax.plot(np.cos(_t), np.sin(_t), "k-", alpha=0.1)
    _ax.set_xlim(-1.3, 1.3)
    _ax.set_ylim(-1.3, 1.3)
    _ax.set_aspect("equal")
    _ax.set_xlabel("Horizontal (e₁)")
    _ax.set_ylabel("Vertical (e₂)")
    _ax.set_title("Polarisation States Through Three Polarisers")
    _ax.legend(loc="lower right")
    _ax.grid(True, alpha=0.3)
    _fig
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## N Equally-Spaced Polarisers — Rotating H to V

    Each polariser is rotated by $90°/N$ from the previous.
    As $N \\to \\infty$, transmission → 100% (quantum Zeno analogue).
    """)
    return


@app.cell
def _(mo):
    n_slider = mo.ui.slider(
        start=2, stop=90, step=1, value=10,
        label="Number of polarisers"
    )
    n_slider
    return (n_slider,)


@app.cell
def _(e1, e2, n_slider, norm, np, plt, polarise, unit):
    N = n_slider.value
    step_deg = 90.0 / N

    E = e1.eval()
    states = [(E, 0.0)]
    for i in range(1, N + 1):
        deg = step_deg * i
        axis = unit(np.cos(np.radians(deg)) * e1 + np.sin(np.radians(deg)) * e2)
        E = polarise(E, axis).eval()
        states.append((E, deg))

    I_out = norm(E) ** 2
    theory = np.cos(np.radians(step_deg)) ** (2 * N)

    # --- Plots ---
    _fig, (_ax1, _ax2) = plt.subplots(1, 2, figsize=(12, 5))

    _cmap = plt.cm.viridis
    for idx, (Ev, deg) in enumerate(states):
        frac = idx / max(len(states) - 1, 1)
        x, y = Ev.data[1], Ev.data[2]
        _ax1.annotate("", xy=(x, y), xytext=(0, 0),
                      arrowprops=dict(arrowstyle="->", color=_cmap(frac), lw=1.5))
        if N <= 20 or idx % max(1, N // 10) == 0 or idx == len(states) - 1:
            _ax1.annotate(f"{deg:.0f}°", xy=(x, y), fontsize=7,
                          color=_cmap(frac), xytext=(3, 3), textcoords="offset points")

    t = np.linspace(0, 2 * np.pi, 100)
    _ax1.plot(np.cos(t), np.sin(t), "k-", alpha=0.1)
    _ax1.set_xlim(-1.3, 1.3)
    _ax1.set_ylim(-0.2, 1.3)
    _ax1.set_aspect("equal")
    _ax1.set_xlabel("Horizontal (e₁)")
    _ax1.set_ylabel("Vertical (e₂)")
    _ax1.set_title(f"{N} polarisers, {step_deg:.1f}° each")
    _ax1.grid(True, alpha=0.3)

    intensities = [norm(Ev) ** 2 for Ev, _ in states]
    degs = [d for _, d in states]
    _ax2.plot(degs, intensities, "o-", markersize=3, color="steelblue")
    _ax2.set_xlabel("Polariser angle (°)")
    _ax2.set_ylabel("Intensity")
    _ax2.set_title(f"Output: {I_out:.4f}")
    _ax2.set_xlim(0, 90)
    _ax2.set_ylim(0, 1.05)
    _ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    _fig
    return


@app.cell
def _(e1, e2, gm, n_slider, norm, np, polarise, unit):
    N = n_slider.value
    step_deg = 90.0 / N

    E = e1.eval()
    for i in range(1, N + 1):
        axis = unit(np.cos(np.radians(step_deg * i)) * e1.eval() + np.sin(np.radians(step_deg * i)) * e2.eval())
        E = polarise(E, axis).eval()

    I_out = norm(E) ** 2
    theory = np.cos(np.radians(step_deg)) ** (2 * N)
    loss = (1 - np.cos(np.radians(step_deg))**2) * 100

    gm.md(t"""
    **{N} polarisers**, step = **{step_deg:.2f}°**, loss/step = {loss:.4f}%

    Output intensity: **{I_out:.6f}** (theory: {theory:.6f})
    """)
    return


@app.cell
def _(e1, e2, norm, np, plt, polarise, unit):
    _Ns = list(range(2, 91))
    _intensities = []

    for _N in _Ns:
        _step = 90.0 / _N
        _E = e1.eval()
        for _i in range(1, _N + 1):
            _axis = unit(np.cos(np.radians(_step * _i)) * e1.eval() + np.sin(np.radians(_step * _i)) * e2.eval())
            _E = polarise(_E, _axis).eval()
        _intensities.append(norm(_E) ** 2)

    _theory = [np.cos(np.radians(90.0 / N)) ** (2 * N) for N in _Ns]

    _fig, _ax = plt.subplots(figsize=(8, 4))
    _ax.plot(_Ns, _intensities, 'b-', linewidth=2, label='GA computation')
    _ax.plot(_Ns, _theory, 'r--', linewidth=1.5, label=r'$\cos^{2N}(90°/N)$')
    _ax.axhline(y=1.0, color='gray', linestyle=':', alpha=0.5)
    _ax.set_xlabel('Number of polarisers')
    _ax.set_ylabel('Transmitted intensity')
    _ax.set_title('H → V via N Equally-Spaced Polarisers')
    _ax.legend()
    _ax.set_xlim(2, 90)
    _ax.set_ylim(0, 1.05)
    _ax.grid(True, alpha=0.3)
    _fig
    return


if __name__ == "__main__":
    app.run()
