---
status: accepted
date: 2026-09-07
deciders: edouard
---

# ADR-095: Exact Numeric Equality and Compatible Hashes

## Context and problem statement

Boundary checks after numeric-contract retirement found that equal immutable
values could fail dictionary lookup. Equality ignores the sign of zero, but
the core hashed raw coefficient bytes. Scalar multivectors also compare equal
to Python real numbers, whose hashes do not include an algebra identity.

Comparison had a separate loss of precision: constructing a scalar from
`float(other)` rounded large integers and exact fractions before comparing.
For example, a stored coefficient of `2**53` compared equal to `2**53 + 1`,
and stored `0.1` compared equal to `Fraction(1, 10)`. Huge integers and
nonfinite numbers could raise during comparison. These cases were computed
against the running core and facade before changing the implementation.

Simply comparing a Python float with a NumPy scalar is insufficient: NumPy
promotion can round the float to the operand's narrower precision or convert
a large integer to a float. The policy must preserve actual numeric values,
not just remove the original conversion.

## Decision outcome

Multivector-to-multivector equality retains exact parent-algebra identity and
exact coefficient equality. Positive and negative zero are numerically equal;
every nonzero coefficient, including a subnormal, remains significant.
Names, presentation, and expression provenance do not participate.

Only a value with exactly zero nonscalar coefficients can equal a real number.
Compare its stored Python float coefficient without narrowing the operand:

- normalize integral operands, including NumPy integers, to Python integers;
- compare finite NumPy floating scalars by their exact integer ratios;
- use Python numeric equality for other real operands, including floats and
  exact fractions; and
- accept NumPy booleans alongside Python booleans so comparison is symmetric.

Comparison with NaN or infinity returns `False`; finite-only construction is
unchanged. This does not add NumPy array protocols or extend constructors and
arithmetic to new scalar types. Constructor conversion to `float64` still
rounds unrepresentable inputs; equality no longer repeats that rounding on
the comparison operand.

An exactly scalar multivector uses its Python float coefficient's hash. Other
multivectors hash a tuple of the parent algebra identity and the numeric
coefficient tuple. Python numeric hashing equates signed zeros without
mutating storage or discarding any nonzero coefficient. Hashes are not a
serialization format or promised stable across processes.

Neither comparison nor hashing calls tolerance-sensitive grade inspection or
`float(multivector)`. Approximate comparison remains explicitly
`almost_equal`; no rounding tolerance is introduced into key semantics.

The facade delegates this policy to the core, including the NumPy boolean
comparison boundary. This refines the immutable-value decision in
[core ADR-003](../core/adrs/003-exterior-bitmasks-and-immutable-dense-values.md)
and corrects the raw-byte hash description in
[SPEC-002](../core/specs/SPEC-002-multivector-representation-and-operators.md).

## Consequences and boundaries

- Equal values have equal hashes, including supported real-number peers.
  Dictionary lookup works in both insertion directions and sets deduplicate
  signed-zero peers. Stored zero signs and read-only arrays are preserved.
- Unequal values may share a hash. Tests require correct lookup and equality,
  not collision-free hashing or specific hash integers.
- The existing algebra scope remains: scalars from different algebra objects
  are unequal even when each equals the same Python number. Thus equality
  across this mixed domain is not transitive, and mixing such keys can give
  insertion-order-dependent deduplication. This repair does not silently
  change that compatibility policy. Use explicitly algebra-qualified keys,
  such as `(algebra, value)`, when the algebra must distinguish scalar keys.
- Numeric tuples allocate Python objects when hashing nonscalars, unlike the
  old raw-byte hash. The operation remains linear in the coefficient count;
  hash caching and storage normalization are outside this correction.
- Core and public facade regressions cover signed zeros across Euclidean,
  degenerate, oblique, and native-null metrics; scalar numeric keys; large
  integers; exact fractions; NumPy precision boundaries; nonfinite operands;
  subnormals; and independence from presentation and tolerant conversion.
  The extended-precision case runs only where NumPy's `longdouble` is wider
  than `float64`.
- Verification, because all changed equality/hash lines and branches are
  covered in the full Python 3.11 run. Both full runtime suites and the
  isolated installed-wheel regression run pass; current counts and remaining
  release gates are recorded in the
  [cutover plan](../v2/core-cutover-plan.md#immediate-release-blocker-equalityhash-consistency).
- Production arithmetic, scalar conversion, the legacy engine, and release
  packaging policy are unchanged. Legacy deletion remains a separate gate.
