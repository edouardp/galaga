# Galaga

Galaga is a Python geometric-algebra library built around an immutable,
Gram-matrix numeric core. Galaga 2 adds general symmetric metrics, explicit
product conventions, optional expression provenance, configurable
presentation, native-null CGA, RGA semantics, and shared ASCII, Unicode, and
LaTeX rendering.

This repository is a monorepo:

| Package | Purpose | Python |
|---|---|---:|
| [`galaga`](packages/galaga/README.md) | Numeric core, public multivectors, expressions, rendering, CGA, and RGA | 3.11+ |
| [`galaga-matrix`](packages/galaga_matrix/README.md) | Left-regular, compact, quaternion, and spinor representations | 3.11+ |
| [`galaga-marimo`](packages/galaga_marimo/README.md) | Marimo t-string rendering helpers | 3.14+ |
| [`galaga-mermaid`](packages/galaga_mermaid/README.md) | Experimental expression-tree diagrams | 3.11+ |

## Install Galaga 2

During the prerelease train:

```bash
python -m pip install --pre "galaga>=2.0.0a1,<3"
```

After the stable release:

```bash
python -m pip install "galaga>=2,<3"
```

```python
from galaga import Algebra, DisplayPolicy, outer_product

algebra = Algebra((1, 1, 1), display=DisplayPolicy(content="full"))
e1, e2, e3 = algebra.basis_vectors(expr=True)

u = (2 * e1 + e2).named("u")
v = (e2 + e3).named("v")
area = outer_product(u, v)

print(area.latex())
```

See the [Galaga package guide](packages/galaga/README.md) for the public API and
the [documentation index](docs/README.md) for mathematical, architectural,
migration, and release documentation.

## Develop locally

```bash
uv sync
make test
make run-marimo
```

`make run-marimo` launches the portable example gallery against editable local
copies of all four packages. The notebooks themselves contain ordinary package
imports, so the same files also run against installed releases.
