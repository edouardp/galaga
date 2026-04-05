import marimo

__generated_with = "0.22.4"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo

    return (mo,)


@app.cell
def _():
    from galaga import Algebra, BladeConvention, b_default, b_cga, b_gamma, b_pga, b_sigma, b_sigma_xyz, b_sta

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

        def __enter__(self):
            return self

        def __exit__(self, *_):
            pass

    def display(*p):
        _str = ""
        for _p in p:
            if hasattr(_p, "latex"):
                _str += f" ${_p.latex()}$"
            else:
                _str += f" {_p}"

        return mo.md(_str)

    return Display, display


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
def _(Algebra, display):
    _alg = Algebra(3)
    _e1, _e2, _e3 = _alg.basis_vectors()
    print("Vectors:", _e1, _e2, _e3)
    print("Bivector:", _e1 ^ _e2)
    print("Pseudoscalar:", _alg.pseudoscalar())
    display("Foo:", _e1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Default — 0-based indexing
    """)
    return


@app.cell
def _(Algebra, b_default):
    _alg = Algebra(3, blades=b_default(start=0))
    _e0, _e1, _e2 = _alg.basis_vectors()
    print("Vectors:", _e0, _e1, _e2)
    print("Bivector:", _e0 ^ _e1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Default — juxtapose style
    """)
    return


@app.cell
def _(Algebra, b_default):
    _alg = Algebra(3, blades=b_default(style="juxtapose"))
    _e1, _e2, _e3 = _alg.basis_vectors()
    print("Bivector:", _e1 ^ _e2)
    print("Trivector:", _e1 ^ _e2 ^ _e3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Default — wedge style
    """)
    return


@app.cell
def _(Algebra, b_default):
    _alg = Algebra(3, blades=b_default(style="wedge"))
    _e1, _e2, _e3 = _alg.basis_vectors()
    print("Bivector:", _e1 ^ _e2)
    print("Trivector:", _e1 ^ _e2 ^ _e3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Custom prefix — Julia-style `v`
    """)
    return


@app.cell
def _(Algebra, b_default):
    _alg = Algebra(3, blades=b_default(prefix="v"))
    _v1, _v2, _v3 = _alg.basis_vectors()
    print("Vectors:", _v1, _v2, _v3)
    print("Bivector:", _v1 ^ _v2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Gamma — STA basis vectors
    """)
    return


@app.cell
def _(Algebra, b_gamma):
    _alg = Algebra(1, 3, blades=b_gamma())
    _g0, _g1, _g2, _g3 = _alg.basis_vectors()
    print("Vectors:", _g0, _g1, _g2, _g3)
    print("Bivector:", _g0 * _g1)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Sigma — Pauli algebra
    """)
    return


@app.cell
def _(Algebra, b_sigma):
    _alg = Algebra(3, blades=b_sigma())
    _s1, _s2, _s3 = _alg.basis_vectors()
    print("Vectors:", _s1, _s2, _s3)
    print("Bivector:", _s1 * _s2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Sigma xyz — letter subscripts
    """)
    return


@app.cell
def _(Algebra, b_sigma_xyz):
    _alg = Algebra(3, blades=b_sigma_xyz())
    _sx, _sy, _sz = _alg.basis_vectors()
    print("Vectors:", _sx, _sy, _sz)
    print("Bivector:", _sx * _sy)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## PGA — 0-based compact with pseudoscalar I
    """)
    return


@app.cell
def _(Algebra, b_pga):
    _alg = Algebra(3, 0, 1, blades=b_pga())
    _e0, _e1, _e2, _e3 = _alg.basis_vectors()
    print("Vectors:", _e0, _e1, _e2, _e3)
    print("Bivector:", _e0 ^ _e1)
    print("Pseudoscalar:", _alg.pseudoscalar())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## STA — plain gamma
    """)
    return


@app.cell
def _(Algebra, b_sta):
    _alg = Algebra(1, 3, blades=b_sta())
    _g0, _g1, _g2, _g3 = _alg.basis_vectors()
    print("Vectors:", _g0, _g1, _g2, _g3)
    print("γ₀γ₁:", _g0 * _g1)
    print("Pseudoscalar:", _alg.pseudoscalar())
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
def _(Algebra, b_sta):
    _alg = Algebra(1, 3, blades=b_sta(pseudovectors=True))
    _g0, _g1, _g2, _g3 = _alg.basis_vectors()
    print("iγ₀ (γ₁γ₂γ₃):", _g1 * _g2 * _g3)
    print("iγ₁ (γ₀γ₂γ₃):", _g0 * _g2 * _g3)
    print("iγ₂ (γ₀γ₁γ₃):", _g0 * _g1 * _g3)
    print("iγ₃ (γ₀γ₁γ₂):", _g0 * _g1 * _g2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## STA — full naming (sigmas + pseudovectors)
    """)
    return


@app.cell
def _(Algebra, b_sta):
    _alg = Algebra(1, 3, blades=b_sta(sigmas=True, pseudovectors=True))
    _g0, _g1, _g2, _g3 = _alg.basis_vectors()
    print("Grade 1:", _g0, _g1, _g2, _g3)
    print("Grade 2:", _g1*_g0, _g2*_g0, _g3*_g0, _g2*_g3, _g1*_g3, _g1*_g2)
    print("Grade 3:", _g1*_g2*_g3, _g0*_g2*_g3, _g0*_g1*_g3, _g0*_g1*_g2)
    print("Grade 4:", _alg.pseudoscalar())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## STA Cl(3,1) — same factories, different metric
    """)
    return


@app.cell
def _(Algebra, b_sta):
    _alg = Algebra(3, 1, blades=b_sta(sigmas=True))
    _g0, _g1, _g2, _g3 = _alg.basis_vectors()
    print("Signature:", _alg.signature)
    print("σ₁ = γ₁γ₀:", _g1 * _g0)
    print("iσ₁ (γ₂γ₃):", _g2 * _g3)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## CGA — origin/infinity basis
    """)
    return


@app.cell
def _(Algebra, b_cga):
    _alg = Algebra(4, 1, blades=b_cga())
    _e1, _e2, _e3, _eo, _ei = _alg.basis_vectors()
    print("Euclidean:", _e1, _e2, _e3)
    print("Null pair:", _eo, _ei)
    print("E₀ (eₒ∧e∞):", _eo ^ _ei)
    print("Pseudoscalar:", _alg.pseudoscalar())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## CGA — plus/minus basis
    """)
    return


@app.cell
def _(Algebra, b_cga):
    _alg = Algebra(4, 1, blades=b_cga(null_basis="plus_minus"))
    _e1, _e2, _e3, _ep, _em = _alg.basis_vectors()
    print("Euclidean:", _e1, _e2, _e3)
    print("Null pair:", _ep, _em)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Custom overrides — naming the pseudoscalar
    """)
    return


@app.cell
def _(Algebra, b_default):
    _alg = Algebra(3, blades=b_default(overrides={"pss": "I"}))
    _e1, _e2, _e3 = _alg.basis_vectors()
    print("Pseudoscalar:", _alg.pseudoscalar())
    print("Bivector:", _e1 ^ _e2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Custom overrides — naming a specific bivector
    """)
    return


@app.cell
def _(Algebra, b_default):
    _alg = Algebra(3, blades=b_default(overrides={"+1+2": "B", "pss": "I"}))
    _e1, _e2, _e3 = _alg.basis_vectors()
    print("e₁∧e₂:", _e1 ^ _e2)
    print("e₁∧e₃:", _e1 ^ _e3)
    print("Pseudoscalar:", _alg.pseudoscalar())
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Post-hoc renaming
    """)
    return


@app.cell
def _(Algebra):
    _alg = Algebra(3)
    _e1, _e2, _e3 = _alg.basis_vectors()
    print("Before:", _e1 ^ _e2)
    _alg.get_basis_blade("+1+2").rename("B")
    print("After:", _e1 ^ _e2)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md("""
    ## Custom vector names
    """)
    return


@app.cell
def _(Algebra, BladeConvention):
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
    print("Vectors:", _x, _y, _z)
    print("Bivector:", _x ^ _y)
    return


if __name__ == "__main__":
    app.run()
