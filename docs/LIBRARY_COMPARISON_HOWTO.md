# Cross-Library Testing Howto

How to quickly test GA computations across different libraries without
polluting your environment. Uses `uvx` (Python), `bunx` (JS), and
`podman`/`docker` (Julia).

## Python libraries via `uvx`

`uvx` runs a Python package in an isolated temporary environment.
Use `--from <pkg> --with <pkg> python3 -c "..."`.

### clifford

```sh
uvx --from clifford --with clifford python3 -c "
from clifford import Cl
layout, blades = Cl(3)
e1, e2, e3 = blades['e1'], blades['e2'], blades['e3']
print((e1 ^ e2).dual())
"
```

### kingdon

```sh
uvx --from kingdon --with kingdon python3 -c "
from kingdon import Algebra
alg = Algebra(3)
locals().update(alg.blades)
print((e1 * e2).dual())
"
```

### galgebra

```sh
uvx --from galgebra --with galgebra python3 -c "
from galgebra.ga import Ga
g = Ga('e1 e2 e3', g=[1, 1, 1])
e1, e2, e3 = g.mv()
print((e1 ^ e2).dual())
"
```

### galaga (this library)

```sh
uv run python3 -c "
from galaga import Algebra, dual
alg = Algebra(3)
e1, e2, e3 = alg.basis_vectors()
print(dual(e1 ^ e2))
"
```

## JavaScript via `node`

ganja.js uses an `inline()` wrapper that rewrites expressions to use
the algebra's elements. This is powerful but fragile — avoid comparisons
and array indexing inside `inline()`.

### ganja.js

Install once in a temp directory (use `bun add` for speed), then run
with `node`:

```sh
cd /tmp && bun add ganja.js
node -e "
var Algebra = require('ganja.js');
Algebra(3, 0, 0).inline(function() {
  console.log((1e12).Dual);
})();
"
```

**Gotcha**: ganja's `inline()` rewrites JavaScript operators (`+`, `<`,
array access) to work with multivectors. This breaks normal JS idioms
like `for` loops and `Array.from()` inside the inline block. Keep the
inline block minimal — extract results and process them outside.

**Bun incompatibility**: `bun -e` does not work with ganja.js. The
`inline()` trick parses `Function.toString()` output to rewrite basis
element literals like `1e12`. Bun's JavaScriptCore engine produces
different `.toString()` output than V8, so the rewriting fails silently.
Always use `node` to execute ganja.js scripts.

## Julia via `podman` / `docker`

Use the official `julia` image. Packages are installed fresh each run
(slow but isolated). Replace `podman` with `docker` if needed.

### Grassmann.jl

```sh
podman run --rm julia:latest julia -e '
using Pkg; Pkg.add("Grassmann"; io=devnull)
using Grassmann
basis"3"
println(⋆(v1 ∧ v2))
'
```

**Tip**: the first run downloads and precompiles packages (~60s). For
repeated testing, create a persistent container or a Dockerfile with
packages pre-installed:

```dockerfile
FROM julia:latest
RUN julia -e 'using Pkg; Pkg.add("Grassmann")'
```

```sh
podman build -t julia-ga .
podman run --rm julia-ga julia -e '
using Grassmann
basis"3"
println(⋆(v1 ∧ v2))
'
```

## Tips

- **Quick sign checks**: test `dual(e1∧e2)` in Cl(3,0) — it's the
  simplest case that reveals sign convention differences.
- **Degenerate algebras**: test in PGA Cl(3,0,1) to see which libraries
  support degenerate pseudoscalars.
- **Compare numerically**: when symbolic output formats differ, compare
  coefficient arrays instead of string representations.
- **Pin versions**: for reproducible comparisons, pin the package version:
  `uvx --from 'clifford==1.4.0' --with clifford python3 -c "..."`.
