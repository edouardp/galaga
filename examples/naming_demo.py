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

    return


@app.cell
def _():
    import numpy as np
    from ga import (
        Algebra, gp, op, grade, reverse, involute, conjugate,
        dual, norm, unit, inverse, exp, log, sandwich, scalar,
        left_contraction, hestenes_inner, even_grades, odd_grades,
        squared
    )
    from ga.symbolic import (
        sym, simplify, grade as sgrade, reverse as srev,
        norm as snorm, unit as sunit, inverse as sinverse,
    )
    import galaga_marimo as gm

    return Algebra, exp, gm, np, reverse, sandwich, simplify, squared, sym


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    # Naming and Evaluation — The New Symbolic API

    This notebook demonstrates the redesigned symbolic system where every
    `Multivector` can independently be **named** or **anonymous**, **lazy** or
    **eager**. No more separate `Expr` type — just multivectors with
    `.name()`, `.anon()`, `.lazy()`, `.eager()`.
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## 1. The Two Axes: Naming × Evaluation

    | | **Anonymous** | **Named** |
    |---|---|---|
    | **Eager** | Plain numeric MV | Basis blades, constants |
    | **Lazy** | Expression structure visible | Symbolic shorthand |
    """)
    return


@app.cell
def _(Algebra):
    alg = Algebra((1, 1, 1))
    e1, e2, e3 = alg.basis_vectors()
    return alg, e1, e2, e3


@app.cell
def _(e1, e2, gm):
    # Basis blades are named + eager by default
    gm.md(t"""
    ### Basis blades: named + eager

    `basis_vectors()` returns blades that print by name but compute eagerly:

    - `e1` prints as {e1} — named, but `_is_lazy = {e1._is_lazy}`
    - `e1 + e2` = {e1 + e2} — eager result, no symbolic overhead
    """)
    return


@app.cell
def _(e1, e2, gm):
    # Name a multivector — makes it lazy by default
    B = (e1 ^ e2).name("B")
    gm.md(t"""
    ### Naming: `.name()` makes things lazy

    ```python
    B = (e1 ^ e2).name("B")
    ```

    - `B` prints as: {B}
    - `B._is_lazy` = {B._is_lazy}
    - `B.anon()` reveals: {B.anon()} (the concrete value)
    - `B.eager()` stays named: {B.eager()} (but `_is_lazy = {B.eager()._is_lazy}`)
    """)
    return (B,)


@app.cell
def _(B, e3, gm):
    # Lazy propagation
    x = B + e3
    gm.md(t"""
    ### Lazy propagation

    When a lazy value enters an operation, the result is lazy:

    ```python
    x = B + e3
    ```

    - `x` = {x} — symbolic expression
    - `x.eager()` = {x.eval()} — concrete result
    - Names don't propagate: `x._name` = `{x._name}`
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## 2. Multi-Format Names

    `.name()` accepts `latex=`, `unicode=`, `ascii=` for per-format control:
    """)
    return


@app.cell
def _(e1, e2, gm):
    F = (e1 ^ e2).name("F", latex=r"\mathcal{F}", unicode="ℱ")
    gm.md(t"""
    ```python
    F = (e1 ^ e2).name("F", latex=r"\\mathcal{{F}}", unicode="ℱ")
    ```

    - `print(F)` → {F}
    - `F.latex()` → `{F.latex()}`
    - In LaTeX: {F}
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## 3. Rotation in 3D — Symbolic Rotor Workflow

    Rotors encode rotations as $R = e^{{-B\\theta/2}}$. With naming, we can
    build the rotor symbolically and see the structure, then evaluate for
    the concrete result.
    """)
    return


@app.cell
def _(e1, e2, exp, gm, np):
    theta = np.pi / 3  # 60 degrees

    B_rot = (e1 ^ e2).name("B")
    R_val = exp(-(e1 ^ e2) * theta / 2)
    R = R_val.name("R")

    v_in = e1
    v_out = R * v_in * ~R

    gm.md(t"""
    Rotate {e1} by 60° in the {B_rot} plane:

    ```python
    R = exp(-B * θ/2).name("R")
    v_out = R * e₁ * ~R
    ```

    - Symbolic: {v_out}
    - Concrete: {v_out.eval()}

    The rotor itself: {R.anon()}
    """)
    return (R,)


@app.cell
def _(R, e1, e2, e3, gm):
    # Rotate all three basis vectors
    with gm.doc() as _d:
        _d.md(t"### Rotating all basis vectors")
        _d.text("| Input | Symbolic | Result |")
        _d.line("|---|---|---|")
        for _v in [e1, e2, e3]:
            rotated = R * _v * ~R
            _d.line(f"| ${_v.latex()}$ | ${rotated.latex()}$ | ${rotated.eval().latex()}$ |")

    _d.render()
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## 3b. Named Scalars — Physical Parameters

    Scalars are multivectors too, so they can be named. This is great for
    physical constants and parameters that should appear symbolically.
    Division by integers renders as fractions.
    """)
    return


@app.cell
def _(alg, e1, e2, exp, gm, np, reverse):
    theta_s = alg.scalar(np.pi / 3).name("θ", latex=r"\theta")
    B_s = (e1 ^ e2).name("B")

    # Build rotor with named scalar — renders as fraction
    half_angle = -B_s * (theta_s / 2)
    _R_s = exp(half_angle.eval()).name("R")

    gm.md(t"""
    Named angle: {theta_s}

    Half-angle bivector: {half_angle} = {half_angle.eval()}

    Rotor: {_R_s} = {exp(half_angle)} = {_R_s.eval()}

    Reverse: {reverse(_R_s)} = {reverse(_R_s).eval()}
    """)
    return


@app.cell
def _(alg, gm):
    # Named physical constants
    c = alg.scalar(3e8).name("c", latex=r"c")
    m = alg.scalar(9.109e-31).name("mₑ", latex=r"m_e")
    hbar = alg.scalar(1.055e-34).name("ℏ", latex=r"\hbar")

    # Compton wavelength: λ = ℏ / (m c)
    lam_val = (hbar / (m * c))

    gm.md(t"""
    ### Named physical constants

    - Speed of light: {c} = {c.eval():.3e} m/s
    - Electron mass: {m} = {m.eval():.3e} kg
    - Reduced Planck: {hbar} = {hbar.eval():.3e} J·s

    Compton wavelength: {lam_val} = {lam_val.eval():.4e} m
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## 4. Electromagnetic Field in Spacetime Algebra

    In the Spacetime Algebra Cl(1,3), the electromagnetic field is a bivector
    $F = \\mathbf{{E}} + I\\mathbf{{B}}$ where $\\mathbf{{E}}$ and $\\mathbf{{B}}$
    are the electric and magnetic fields encoded as spacetime bivectors.
    """)
    return


@app.cell
def _(Algebra, gm, squared):
    sta = Algebra((1, -1, -1, -1), names="gamma")
    g0, g1, g2, g3 = sta.basis_vectors()

    # Electric field in x-direction: E = γ₁γ₀
    E_field = (g1 * g0).name("E", latex=r"\mathbf{E}")

    # Magnetic field in z-direction: B = γ₁γ₂ (spatial bivector)
    B_field = (g1 * g2).name("B", latex=r"\mathbf{B}")

    # Full EM field bivector: F = E + IB
    I_sta = sta.pseudoscalar()
    F_val = E_field + I_sta * B_field
    F_em = F_val.name("F", latex=r"\mathcal{F}")

    # Lorentz invariant: F² = E² - B² (in natural units)
    F_sq = squared(F_val)

    gm.md(t"""
    The electromagnetic field bivector:

    {F_em} = {E_field} + {I_sta*B_field} = {F_em.eval()}

    The field squared (Lorentz invariant):

    {F_sq} = {F_sq:g}

    This invariant tells us whether the field is electric-dominated
    (positive) or magnetic-dominated (negative).
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## 5. Simplification Still Works

    `simplify()` operates on the expression trees inside lazy multivectors.
    Named values participate naturally:
    """)
    return


@app.cell
def _(e1, e2, gm, simplify, sym):
    v = sym(e1, "v")
    R_s = sym(e1 * e2, "R")

    with gm.doc() as _d:
        _d.md(t"### Algebraic identities")
        _d.text("| Expression | Simplified |")
        _d.line("|---|---|")

        cases = [
            ("Double reverse", ~~v),
            ("Self-subtraction", v - v),
            ("Self-addition", v + v),
            ("Rotor normalisation", R_s * ~R_s),
        ]
        for label, expr in cases:
            _d.line(f"| {label}: ${expr.latex()}$ | ${simplify(expr).latex()}$ |")

    _d.render()
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## 6. Projective GA — Points, Lines, Planes

    In PGA Cl(3,0,1), we can represent geometric primitives and
    use the naming system to keep track of what's what.
    """)
    return


@app.cell
def _(Algebra, gm):
    pga = Algebra((1, 1, 1, 0))
    pe1, pe2, pe3, pe0 = pga.basis_vectors()

    # Points in PGA: p = x*e1 + y*e2 + z*e3 + e0
    P = (1 * pe1 + 0 * pe2 + 0 * pe3 + pe0).name("P")
    Q = (0 * pe1 + 1 * pe2 + 0 * pe3 + pe0).name("Q")
    R_pt = (0 * pe1 + 0 * pe2 + 1 * pe3 + pe0).name("R")

    # Line through two points: L = P ∧ Q
    L = (P ^ Q).name("L", latex=r"\ell")

    # Plane through three points: π = P ∧ Q ∧ R
    pi = (P ^ Q ^ R_pt).name("π", latex=r"\pi")

    gm.md(t"""
    Three points on the unit axes:

    - {P} = {P.eval()}
    - {Q} = {Q.eval()}
    - {R_pt} = {R_pt.eval()}

    Line through {P} and {Q}: {L} = {L.eval()}

    Plane through all three: {pi} = {pi.eval()}
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## 7. Quantum Spin-½ with Pauli Algebra

    The Pauli algebra Cl(3,0) models spin-½ particles. Spin states are
    even-graded elements (rotors), and measurements are sandwich products.
    """)
    return


@app.cell
def _(Algebra, exp, gm, np, sandwich):
    pauli = Algebra((1, 1, 1), names="sigma")
    s1, s2, s3 = pauli.basis_vectors()

    # Spin-up state along z: |↑⟩ = 1 (identity rotor)
    psi_up = pauli.scalar(1.0).name("ψ↑", latex=r"\psi_\uparrow")

    # Rotate to spin-up along x: rotate 90° from z to x
    psi_x = exp(-(s2 * s3) * np.pi / 4).name("ψₓ", latex=r"\psi_x")

    # Spin expectation: the vector part of ψ σ₃ ψ̃ gives the spin direction
    spin_up = sandwich(psi_up, s3)
    spin_x = sandwich(psi_x, s3)

    gm.md(t"""
    Spin-up along z: {psi_up} = {psi_up.eval()}

    Spin-up along x: {psi_x} = {psi_x.eval()}

    **Spin measurement** (sandwich ψσ₃ψ̃):

    - {psi_up}: ψσ₃ψ̃ = {spin_up.eval()} → spin points along +z ✓
    - {psi_x}: ψσ₃ψ̃ = {spin_x.eval()} → no z-component (spin along x)

    The sandwich product rotates the measurement axis into the spin
    frame — a purely geometric operation, no matrices needed.
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## 8. Chaining: Name → Compute → Rename

    The four methods compose freely. Here's a workflow where we build up
    a complex expression, name intermediate results, and evaluate step by step.
    """)
    return


@app.cell
def _(alg, e1, e2, e3, exp, gm, np):
    # Build a rotation in two steps
    _pi = alg.scalar(np.pi).name("π", latex=r"\pi")

    B1 = (e1 ^ e2).name("B₁", latex=r"B_1")
    B2 = (e2 ^ e3).name("B₂", latex=r"B_2")

    R1 = exp(-B1 * np.pi / 6).name("R₁", latex=r"R_1")
    R2 = exp(-B2 * np.pi / 4).name("R₂", latex=r"R_2")

    # Compose rotors
    R_total = (R2 * R1).name("R", latex=r"R_{\text{total}}")

    # Apply to a vector
    v_start = e1
    v_result = R_total * v_start * ~R_total

    gm.md(t"""
    Two successive rotations:

    1. {R1} = {exp(-B1 * (_pi/6))} — 30° in the {B1} plane
    2. {R2} = {exp(-B2 * (_pi/4))} — 45° in the {B2} plane

    Composed rotor: {R_total} = {R2}{R1}

    Apply to {e1}:

    - Symbolic: {v_result}
    - Concrete: {v_result.eval()}
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## 9. Old API vs New API

    `sym()` still works — it's now an alias for `.name()`. Both return
    `Multivector` objects:
    """)
    return


@app.cell
def _(e1, gm, sym):
    # Old way
    v_old = sym(e1, "v")

    # New way
    v_new = e1.name("v")

    # They're equivalent
    gm.md(t"""
    ```python
    # Old: sym(e1, "v")
    # New: e1.name("v")
    ```

    - `sym(e1, "v")` → {v_old} (type: `{type(v_old).__name__}`)
    - `e1.name("v")` → {v_new} (type: `{type(v_new).__name__}`)
    - Equal? {v_old == v_new}

    The new API adds format control:
    ```python
    e1.name("v", latex=r"\\mathbf{{v}}", unicode="𝐯")
    ```
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## 10. The Four Quadrants in Action
    """)
    return


@app.cell
def _(e1, e2, gm):
    # Anonymous + Eager (default arithmetic)
    ae = e1 + e2

    # Named + Eager (basis blades, or .name().eager())
    ne = (e1 + e2).name("w").eager()

    # Named + Lazy (the common symbolic case)
    nl = (e1 ^ e2).name("B")

    # Anonymous + Lazy (.anon() on a named lazy, or .lazy())
    al = nl.anon()

    with gm.doc() as _d:
        _d.md(t"### All four quadrants")
        _d.text("| | Anonymous | Named |")
        _d.line("|---|---|---|")
        _d.line(f"| **Eager** | `e1 + e2` → ${ae.latex()}$ | `(e1+e2).name(\"w\").eager()` → ${ne.latex()}$ |")
        _d.line(f"| **Lazy** | `B.anon()` → ${al.latex()}$ | `(e1^e2).name(\"B\")` → ${nl.latex()}$ |")

    _d.render()
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## 11. Special Relativity — Lorentz Boost

    In the Spacetime Algebra, a Lorentz boost is a rotor built from a
    timelike bivector. The naming system lets us track the physics.
    """)
    return


@app.cell
def _(Algebra, exp, gm, reverse, sandwich):
    sta2 = Algebra((1, -1, -1, -1), names="gamma")
    t0, x1, x2, x3 = sta2.basis_vectors()

    # Boost rapidity
    rapidity = sta2.scalar(0.5).name("φ", latex=r"\varphi")  # corresponds to v ≈ 0.46c

    # Boost bivector (timelike — squares to +1)
    boost_plane = (t0 * x1).name("B", latex=r"\hat{B}")

    # Boost rotor: exp(B * φ/2) — note: no minus sign for timelike bivectors
    Lambda = exp((t0 * x1) * rapidity / 2).name("Λ", latex=r"\Lambda")

    # Boost a particle at rest: p = m*γ₀
    p_rest = t0.name("p", latex=r"p_{\text{rest}}")
    p_boosted = sandwich(Lambda, p_rest)

    gm.md(t"""
    Boost in the {t0}{x1} plane with rapidity {rapidity} = {rapidity.eval()}:

    {Lambda} = exp({boost_plane} · {rapidity/2}) = {Lambda.eval()}

    Particle at rest: {p_rest} = {t0}

    After boost: {Lambda}{p_rest}{reverse(Lambda)} = {p_boosted.eval()}

    The boosted 4-momentum has both time and space components — the
    particle is now moving!
    """)
    return


@app.cell(hide_code=True)
def _(gm):
    gm.md(t"""
    ## Summary

    The four methods on `Multivector`:

    | Method | Effect |
    |---|---|
    | `.name("B")` | Set display name, make lazy |
    | `.name("B", latex=r"\\mathcal{{B}}")` | With format overrides |
    | `.anon()` | Remove name, keep lazy/eager |
    | `.lazy()` | Prefer symbolic display |
    | `.eager()` | Force eager in-place, strip name |
    | `.eager("B")` | Force eager in-place, keep/set name |
    | `.eval()` | Return new anonymous eager copy |

    **Key rules:**
    - Lazy is contagious — lazy + anything = lazy
    - Names don't propagate — results are anonymous
    - Named operands appear by name in expression trees
    - Eager + eager = eager (zero overhead)
    - `sym()` still works — it's an alias for `.name()`
    - Division by scalars renders as fractions: `φ/2` not `0.5φ`
    - Named scalars work too: `alg.scalar(π).name("θ")`
    """)
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
