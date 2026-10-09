# Galaga Capability Roadmap

This roadmap lists possible extensions beyond the implemented Galaga 2
architecture. It is not a release checklist or a commitment to particular
versions. Use the [architecture guide](README.md) for current responsibilities
and the [release process](../RELEASE_PROCESS.md#quality-gates) for candidate
validation. Completed replacement work is indexed in the [history](history.md).

## Current capabilities

| Area | Implemented capability | Guide |
|---|---|---|
| Numeric algebra | Real symmetric Gram matrices; diagonal and general-Gram products in the native exterior basis | [Numeric core](../core/README.md) |
| Numeric functions | Integer powers, checked inverse, general exponential, principal logarithm, supported square-root branches, and finite real powers in all-null algebras | [Core specifications](../core/specs/README.md) |
| Presentation | Immutable, composable blade, notation, ordering and display settings; reusable presenters; layered user preferences | [Presentation configuration](presentation-configuration.md) |
| Expressions | Optional executable provenance, naming, rebinding and semantic rendering | [Expression provenance](expression-provenance.md) |
| Geometry | PGA, RGA, CGA and CSTA models with role validation and model-owned classifiers | [Runtime geometry models](runtime-geometry-models.md) |
| Matrix integration | Public linear actions, compact and left-regular representations, general-Gram basis conversion, matrix arithmetic and provenance | [Matrix integration](matrix-migration.md) |
| Companion integration | Notebook rendering, annotations, interactive views and expression graphs through public APIs | [Integration guide](integration-migration.md) |

## Linear maps and basis changes

A public outermorphism facility could extend the existing test helpers into a
validated API:

- extend a vector map to every exterior grade;
- support source and target algebras with different native bases;
- materialize exterior-map matrices on request;
- validate metric-preserving maps; and
- provide inverse basis changes, followed by adjoints and reciprocal frames.

This would give native Gram metrics a reusable interoperability surface and
support an explicit native/orthogonal-frame CGA comparison. Matrix integration
already performs its own validated metric congruence and exterior-power lift;
a general algebra-to-algebra map would serve broader consumers.

## Numerical and performance improvements

These are candidates for measurement and design work, rather than outstanding
migration tasks:

- Add a verified versor fast path to `inverse`, retaining the left-regular
  solve and residual checks for general inputs.
- Use a cheaper certified bound to scale general exponentials before targeting
  larger dimensions.
- Measure difficult conditioning and branch-cut cases for the principal
  logarithm's native resolvent quadrature.
- Investigate general multivector square roots and alternative rotor-generator
  branches under explicit domain and branch contracts. All-null values with
  positive scalar part already have finite-series roots and real powers.
- Add memory guards or operator forms for dense compound metric matrices.
- Measure dense-multivector workloads on the lazy product backend before
  changing cache or packed-backend selection.

New numerical paths need independent algebraic checks and residual tests.
Historical performance measurements remain useful context, but the retired
Phase 8 benchmark is not a current release gate.

## Model extensions

Possible extensions include:

- factories that return a configured algebra and runtime model together;
- two-dimensional RGA support, with its point/plane conventions and
  transformation contracts validated independently;
- further model-specific transformation classifiers where they add useful
  semantics beyond the existing CSTA operator traits; and
- broader classifier dimensions where there is a concrete consumer need.

The current `RigidModel` is three-dimensional. PGA and CGA classifiers cover
2D and 3D; CSTA uses the fixed four-dimensional $(+---)$ spacetime signature.
Conformal embedding itself supports other positive spatial dimensions.

The native-CGA quaternion/Vahlen proposal is separate matrix work. It must not
be confused with the existing generic compact representation or the named
Euclidean quaternion convention; see the
[native-CGA matrix proposal](../../packages/galaga_matrix/docs/specs/native-null-cga-matrix-representations.md).

## Extension boundaries

The numeric core remains responsible for real arithmetic in the declared
native basis. Expression construction, notation, rendering, and geometric
interpretation belong to their respective outer layers.

The following would require separate design decisions:

- symbolic Gram entries or coefficients;
- complexified Clifford algebras;
- nonsymmetric bilinear forms;
- sparse multivector coefficient storage;
- serialization contracts; and
- implicit NumPy array or ufunc interpretation of multivectors.

Basis conversion should be explicit: a numeric operation must not silently
replace the user's native basis with an orthogonal one.
