import marimo

__generated_with = "0.22.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from galaga import (
        Algebra,
        BladeConvention,
        b_cga,
        b_default,
        b_gamma,
        b_pga,
        b_sigma,
        b_sigma_xyz,
        b_sta,
    )

    return (
        Algebra,
        BladeConvention,
        b_cga,
        b_default,
        b_gamma,
        b_pga,
        b_sigma,
        b_sigma_xyz,
        b_sta,
    )


@app.cell
def _(mo):
    class Display:
        def __init__(self):
            self._lines = []

        def __call__(self, *p):
            parts = []
            for _p in p:
                if hasattr(_p, "latex"):
                    parts.append(f"${_p.latex()}$")
                else:
                    parts.append(str(_p))
            self._lines.append(" ".join(parts))

        def _repr_html_(self):
            return mo.md("\n\n".join(self._lines)).text

    return (Display,)


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    # Blade Convention Gallery

    A tour of galaga's blade naming system. Each cell constructs an algebra
    with a different `BladeConvention` to show the available options.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Default — compact subscripts, 1-based
    """)
    return


@app.cell
def _(Algebra, Display):
    _alg = Algebra(3)
    _e1, _e2, _e3 = _alg.basis_vectors()
    _d = Display()
    _d("Vectors:", _e1, _e2, _e3)
    _d("Bivector:", _e1 ^ _e2)
    _d("Pseudoscalar:", _alg.pseudoscalar())
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Default — 0-based indexing
    """)
    return


@app.cell
def _(Algebra, Display, b_default):
    _alg = Algebra(3, blades=b_default(start=0))
    _e0, _e1, _e2 = _alg.basis_vectors()
    _d = Display()
    _d("Vectors:", _e0, _e1, _e2)
    _d("Bivector:", _e0 ^ _e1)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Default — juxtapose style
    """)
    return


@app.cell
def _(Algebra, Display, b_default):
    _alg = Algebra(3, blades=b_default(style="juxtapose"))
    _e1, _e2, _e3 = _alg.basis_vectors()
    _d = Display()
    _d("Bivector:", _e1 ^ _e2)
    _d("Trivector:", _e1 ^ _e2 ^ _e3)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Default — wedge style
    """)
    return


@app.cell
def _(Algebra, Display, b_default):
    _alg = Algebra(3, blades=b_default(style="wedge"))
    _e1, _e2, _e3 = _alg.basis_vectors()
    _d = Display()
    _d("Bivector:", _e1 ^ _e2)
    _d("Trivector:", _e1 ^ _e2 ^ _e3)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Custom prefix — Julia-style `v`
    """)
    return


@app.cell
def _(Algebra, Display, b_default):
    _alg = Algebra(3, blades=b_default(prefix="v"))
    _v1, _v2, _v3 = _alg.basis_vectors()
    _d = Display()
    _d("Vectors:", _v1, _v2, _v3)
    _d("Bivector:", _v1 ^ _v2)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Gamma — STA basis vectors
    """)
    return


@app.cell
def _(Algebra, Display, b_gamma):
    _alg = Algebra(1, 3, blades=b_gamma())
    _g0, _g1, _g2, _g3 = _alg.basis_vectors()
    _d = Display()
    _d("Vectors:", _g0, _g1, _g2, _g3)
    _d("Bivector:", _g0 * _g1)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Sigma — Pauli algebra
    """)
    return


@app.cell
def _(Algebra, Display, b_sigma):
    _alg = Algebra(3, blades=b_sigma())
    _s1, _s2, _s3 = _alg.basis_vectors()
    _d = Display()
    _d("Vectors:", _s1, _s2, _s3)
    _d("Bivector:", _s1 * _s2)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Sigma xyz — letter subscripts
    """)
    return


@app.cell
def _(Algebra, Display, b_sigma_xyz):
    _alg = Algebra(3, blades=b_sigma_xyz())
    _sx, _sy, _sz = _alg.basis_vectors()
    _d = Display()
    _d("Vectors:", _sx, _sy, _sz)
    _d("Bivector:", _sx * _sy)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## PGA — 0-based compact with pseudoscalar I
    """)
    return


@app.cell
def _(Algebra, Display, b_pga):
    _alg = Algebra(3, 0, 1, blades=b_pga())
    _e0, _e1, _e2, _e3 = _alg.basis_vectors()
    _d = Display()
    _d("Vectors:", _e0, _e1, _e2, _e3)
    _d("Bivector:", _e0 ^ _e1)
    _d("Pseudoscalar:", _alg.pseudoscalar())
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## STA — plain gamma
    """)
    return


@app.cell
def _(Algebra, Display, b_sta):
    _alg = Algebra(1, 3, blades=b_sta())
    _g0, _g1, _g2, _g3 = _alg.basis_vectors()
    _d = Display()
    _d("Vectors:", _g0, _g1, _g2, _g3)
    _d("γ₀γ₁:", _g0 * _g1)
    _d("Pseudoscalar:", _alg.pseudoscalar())
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## STA — with sigma bivector aliases
    """)
    return


@app.cell
def _(Algebra, Display, b_sta):
    _alg = Algebra(1, 3, blades=b_sta(sigmas=True))
    _g0, _g1, _g2, _g3 = _alg.basis_vectors()
    _d = Display()
    _d("σ₁ = γ₁γ₀:", _g1 * _g0)
    _d("σ₂ = γ₂γ₀:", _g2 * _g0)
    _d("σ₃ = γ₃γ₀:", _g3 * _g0)
    _d("iσ₁ (γ₂γ₃):", _g2 * _g3)
    _d("iσ₂ (γ₁γ₃):", _g1 * _g3)
    _d("iσ₃ (γ₁γ₂):", _g1 * _g2)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## STA — with pseudovector aliases
    """)
    return


@app.cell
def _(Algebra, Display, b_sta):
    _alg = Algebra(1, 3, blades=b_sta(pseudovectors=True))
    _g0, _g1, _g2, _g3 = _alg.basis_vectors()
    _d = Display()
    _d("iγ₀ (γ₁γ₂γ₃):", _g1 * _g2 * _g3)
    _d("iγ₁ (γ₀γ₂γ₃):", _g0 * _g2 * _g3)
    _d("iγ₂ (γ₀γ₁γ₃):", _g0 * _g1 * _g3)
    _d("iγ₃ (γ₀γ₁γ₂):", _g0 * _g1 * _g2)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## STA — full naming (sigmas + pseudovectors)
    """)
    return


@app.cell
def _(Algebra, Display, b_sta):
    _alg = Algebra(1, 3, blades=b_sta(sigmas=True, pseudovectors=True))
    _g0, _g1, _g2, _g3 = _alg.basis_vectors()
    _d = Display()
    _d("Grade 1:", _g0, _g1, _g2, _g3)
    _d("Grade 2:", _g1 * _g0, _g2 * _g0, _g3 * _g0, _g2 * _g3, _g1 * _g3, _g1 * _g2)
    _d("Grade 3:", _g1 * _g2 * _g3, _g0 * _g2 * _g3, _g0 * _g1 * _g3, _g0 * _g1 * _g2)
    _d("Grade 4:", _alg.pseudoscalar())
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## STA Cl(3,1) — same factories, different metric
    """)
    return


@app.cell
def _(Algebra, Display, b_sta):
    _alg = Algebra(3, 1, blades=b_sta(sigmas=True))
    _g0, _g1, _g2, _g3 = _alg.basis_vectors()
    _d = Display()
    _d("Signature:", str(_alg.signature))
    _d("σ₁ = γ₁γ₀:", _g1 * _g0)
    _d("iσ₁ (γ₂γ₃):", _g2 * _g3)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## CGA — origin/infinity basis
    """)
    return


@app.cell
def _(Algebra, Display, b_cga):
    _alg = Algebra(4, 1, blades=b_cga())
    _e1, _e2, _e3, _eo, _ei = _alg.basis_vectors()
    _d = Display()
    _d("Euclidean:", _e1, _e2, _e3)
    _d("Null pair:", _eo, _ei)
    _d("E₀ (eₒ∧e∞):", _eo ^ _ei)
    _d("Pseudoscalar:", _alg.pseudoscalar())
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## CGA — plus/minus basis
    """)
    return


@app.cell
def _(Algebra, Display, b_cga):
    _alg = Algebra(4, 1, blades=b_cga(null_basis="plus_minus"))
    _e1, _e2, _e3, _ep, _em = _alg.basis_vectors()
    _d = Display()
    _d("Euclidean:", _e1, _e2, _e3)
    _d("Null pair:", _ep, _em)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Custom overrides — naming the pseudoscalar
    """)
    return


@app.cell
def _(Algebra, Display, b_default):
    _alg = Algebra(3, blades=b_default(overrides={"pss": "I"}))
    _e1, _e2, _e3 = _alg.basis_vectors()
    _d = Display()
    _d("Pseudoscalar:", _alg.pseudoscalar())
    _d("Bivector:", _e1 ^ _e2)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Custom overrides — naming a specific bivector
    """)
    return


@app.cell
def _(Algebra, Display, b_default):
    _alg = Algebra(3, blades=b_default(overrides={"+1+2": "B", "pss": "I"}))
    _e1, _e2, _e3 = _alg.basis_vectors()
    _d = Display()
    _d("e₁∧e₂:", _e1 ^ _e2)
    _d("e₁∧e₃:", _e1 ^ _e3)
    _d("Pseudoscalar:", _alg.pseudoscalar())
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Post-hoc renaming
    """)
    return


@app.cell
def _(Algebra, Display):
    _alg = Algebra(3)
    _e1, _e2, _e3 = _alg.basis_vectors()
    _d = Display()
    _d("Before:", _e1 ^ _e2)
    _alg.get_basis_blade("+1+2").rename("B")
    _d("After:", _e1 ^ _e2)
    _d
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Custom vector names
    """)
    return


@app.cell
def _(Algebra, BladeConvention, Display):
    _alg = Algebra(
        (1, 1, 1),
        blades=BladeConvention(
            vector_names=[
                ("x", "𝐱", r"\mathbf{x}"),
                ("y", "𝐲", r"\mathbf{y}"),
                ("z", "𝐳", r"\mathbf{z}"),
            ],
            style="wedge",
        ),
    )
    _x, _y, _z = _alg.basis_vectors()
    _d = Display()
    _d("Vectors:", _x, _y, _z)
    _d("Bivector:", _x ^ _y)
    _d
    return


if __name__ == "__main__":
    app.run()
