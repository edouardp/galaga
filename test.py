import marimo

__generated_with = "0.22.4"
app = marimo.App(width="medium")


@app.cell
def _():
    from packages.galaga.galaga import Algebra

    return (Algebra,)


@app.cell
def _(Algebra):
    alg = Algebra([1,1,1,1], display=True)
    return (alg,)


@app.cell
def _(alg):
    e1,e2,e3,e4 = alg.basis_vectors(lazy=True)

    return e1, e2, e3, e4


@app.cell
def _(e1, e2):
    A = (e1^e2).name("A")
    return (A,)


@app.cell
def _(e1, e2, e3, e4):
    B = ((e1^e2) +( e2^e3) + (e3^e4)).name("B")
    return (B,)


@app.cell
def _(A, B):
    (A*B).display()
    return


@app.cell
def _(A, B):
    A*B
    return


@app.cell
def _():
    return


@app.cell
def _():
    return


if __name__ == "__main__":
    app.run()
