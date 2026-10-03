"""A metric-aware classification worksheet for selected CSTA objects."""

import marimo

__generated_with = "0.24.2"
app = marimo.App(width="medium")


@app.cell
def _():
    import marimo as mo
    import numpy as np

    import galaga_marimo as gm
    from galaga import Algebra, BladeConvention, Name, metric_inner_product

    return Algebra, BladeConvention, Name, gm, metric_inner_product, mo, np


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    # A CSTA object classifier, built in layers

    In $\mathrm{Cl}(2,4)$ an event, a flat line, and a signed round can all
    be represented by blades. Their **grade and incidence** describe the
    structure; the induced metric gives causal meaning. This worksheet
    implements a deliberately small classifier for objects with known
    constructors and witnesses. It is a notebook prototype, not a public
    Galaga classifier for arbitrary multivectors.

    We use the ordered basis
    $\{\gamma_0,\gamma_1,\gamma_2,\gamma_3,n_o,n_\infty\}$,
    physical metric $(+---)$, and $n_o\cdot n_\infty=-1$.
    """)
    return


@app.cell
def _(Algebra, BladeConvention, Name, metric_inner_product, np):
    gram = np.zeros((6, 6))
    gram[:4, :4] = np.diag([1, -1, -1, -1])
    gram[4, 5] = gram[5, 4] = -1
    _vector_names = tuple(Name(f"g{_i}", f"γ{'₀₁₂₃'[_i]}", rf"\gamma_{_i}") for _i in range(4)) + (
        Name("n_o", "nₒ", r"n_o"),
        Name("n_inf", "n∞", r"n_\infty"),
    )
    _labels = {}
    for _mask in range(1 << 6):
        _parts = [_name for _i, _name in enumerate(_vector_names) if _mask & (1 << _i)]
        _labels[_mask] = Name(
            "".join(_name.ascii for _name in _parts) or "1",
            "∧".join(_name.unicode for _name in _parts) or "1",
            r" \wedge ".join(_name.latex for _name in _parts) or "1",
        )
    csta = Algebra(gram=gram, blades=BladeConvention(6, _labels), expr=True)
    g0, g1, g2, g3, origin, infinity = csta.basis_vectors(expr=True)

    def spacetime(t, x=0.0, y=0.0, z=0.0):
        return t * g0 + x * g1 + y * g2 + z * g3

    def event(t, x=0.0, y=0.0, z=0.0):
        _x = spacetime(t, x, y, z)
        return origin + _x + 0.5 * (_x * _x) * infinity

    def causal_kind(squared_interval, *, tolerance=1e-10):
        if squared_interval > tolerance:
            return "timelike"
        if squared_interval < -tolerance:
            return "spacelike"
        return "null"

    assert not csta.is_degenerate
    assert metric_inner_product(origin, infinity) == -1
    return causal_kind, csta, event, infinity


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 1. Point pairs: use the conformal pairing

    Two normalized event vectors give the OPNS point pair $P=X(a)\wedge X(b)$.
    Its grade is two. We recover their squared Minkowski separation without
    inspecting coordinates:

    $$(a-b)^2=-2X(a)\cdot X(b).$$

    The sign supplies the causal class. The point-pair blade alone does not
    choose which event is first in time.
    """)
    return


@app.cell
def _(causal_kind, csta, event, gm, metric_inner_product):
    _anchor = event(0)
    _pair_cases = (("time step", event(1)), ("light step", event(1, 1)), ("space step", event(0, 1)))
    pair_rows = []
    for _name, _other in _pair_cases:
        _pair = _anchor ^ _other
        _separation = -2 * float(metric_inner_product(_anchor, _other))
        assert _pair.homogeneous_grade() == 2
        assert not _pair.almost_equal(csta.scalar(0))
        pair_rows.append((_name, _pair.homogeneous_grade(), _separation, causal_kind(_separation)))
    _rows = "\n".join(f"| {name} | {grade} | {interval:g} | {kind} |" for name, grade, interval, kind in pair_rows)
    gm.md(rt"""
    | Pair | OPNS grade | Interval² | Causal class |
    |:--|--:|--:|:--|
    {_rows}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 2. Flats: test incidence with infinity

    The OPNS line through two events is
    $L=X(a)\wedge X(b)\wedge n_\infty$. Its grade is three and
    $L\wedge n_\infty=0$. The carrier direction is the ordinary displacement
    between the two witnesses. Its one-dimensional induced Gram matrix is
    simply $[(a-b)^2]$, so its sign classifies the line as timelike,
    spacelike, or null.

    A timelike line **can** model an inertial massive-particle worldline;
    that interpretation requires additional physical context.
    """)
    return


@app.cell
def _(causal_kind, csta, event, gm, infinity, metric_inner_product):
    _anchor = event(0)
    _line_cases = (("time axis", event(1)), ("right light ray", event(1, 1)), ("space axis", event(0, 1)))
    line_rows = []
    for _name, _other in _line_cases:
        _line = _anchor ^ _other ^ infinity
        _interval = -2 * float(metric_inner_product(_anchor, _other))
        assert _line.homogeneous_grade() == 3
        assert not _line.almost_equal(csta.scalar(0))
        assert (_line ^ infinity).almost_equal(csta.scalar(0))
        assert (_anchor ^ _line).almost_equal(csta.scalar(0))
        assert (_other ^ _line).almost_equal(csta.scalar(0))
        line_rows.append((_name, _line.homogeneous_grade(), _interval, causal_kind(_interval)))
    _rows = "\n".join(f"| {name} | {grade} | {interval:g} | {kind} |" for name, grade, interval, kind in line_rows)
    gm.md(rt"""
    | Flat line | OPNS grade | Carrier Gram entry | Causal class |
    |:--|--:|--:|:--|
    {_rows}
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## 3. Rounds: use signed radius squared

    The normalized IPNS vector

    $$S(c,\rho^2)=X(c)-\tfrac12\rho^2n_\infty$$

    obeys $S\cdot n_\infty=-1$ and $S^2=\rho^2$. Its incidence locus is
    $(x-c)^2=\rho^2$. In $(+---)$, positive radius squared gives a
    proper-time hyperboloid, negative gives a proper-distance hyperboloid,
    and zero gives a light cone. A null IPNS vector is therefore **not**
    automatically a tangent object.
    """)
    return


@app.cell
def _(causal_kind, event, gm, infinity, metric_inner_product):
    def signed_round(center, radius_squared):
        return event(*center) - 0.5 * radius_squared * infinity

    _round_cases = (
        ("proper-time hyperboloid", 1.0, event(1)),
        ("light cone", 0.0, event(1, 1)),
        ("proper-distance hyperboloid", -1.0, event(0, 1)),
    )
    round_rows = []
    for _name, _radius_squared, _witness in _round_cases:
        _round = signed_round((0, 0, 0, 0), _radius_squared)
        _recovered = float(_round * _round)
        assert _round.homogeneous_grade() == 1
        assert metric_inner_product(_round, infinity) == -1
        assert abs(_recovered - _radius_squared) < 1e-12
        assert abs(float(metric_inner_product(_witness, _round))) < 1e-12
        assert (_round ^ infinity).homogeneous_grade() == 2
        round_rows.append((_name, _recovered, causal_kind(_recovered)))
    _rows = "\n".join(f"| {name} | {radius:g} | {kind} |" for name, radius, kind in round_rows)
    gm.md(rt"""
    | IPNS hypersurface | Computed $S^2=\rho^2$ | Interval class |
    |:--|--:|:--|
    {_rows}

    The zero-radius row contains every event null-separated from the center,
    in both future and past directions.
    """)
    return


@app.cell(hide_code=True)
def _(mo):
    mo.md(r"""
    ## Boundary of this worksheet

    These three cases are classified from their **known constructions**:
    event pairs have two normalized point witnesses; flats include
    $n_\infty$; signed rounds have an IPNS vector normalized by
    $S\cdot n_\infty=-1$. An arbitrary multivector needs further checks for
    homogeneity, blade simplicity, representation, and induced carrier
    signature. Those checks are needed before a general CSTA classifier
    could safely attach physical names.

    In particular, grade alone does not tell a flat from a round, and a
    vanishing squared norm does not tell a light ray from a light cone or a
    tangent object. The same structural tests apply in conformal Euclidean
    geometry; the causal interpretation comes from the physical metric.
    """)
    return


if __name__ == "__main__":
    app.run()
