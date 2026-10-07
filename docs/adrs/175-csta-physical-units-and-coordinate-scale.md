---
status: accepted
date: 2026-10-07
deciders: edouard
---

# ADR-175: CSTA Physical Units and Coordinate Scale

## Context

The CSTA model introduced in ADR-174 uses a normalized $(+---)$ base metric.
Real spacetime applications need times in seconds, distances in metres, speeds
in metres per second or fractions of $c$, and accelerations in standard gravities.
Users should be able to enter physical coordinates and recover readable values
without changing the algebra or adding a general units dependency.

## Decision

Keep the normalized algebra and perform physical conversions at the model's
numeric coordinate boundary. Export the immutable `SpacetimeUnits` backend from
`galaga.models`. Its scale $T_0>0$ specifies seconds per natural time unit, and
the corresponding natural length unit is $L_0=cT_0$.

$$
t_{\mathrm{SI}}=T_0t,\qquad
\mathbf{x}_{\mathrm{SI}}=cT_0\mathbf{x},\qquad
v_{\mathrm{SI}}=c\beta,\qquad
a_{\mathrm{SI}}=\frac{c}{T_0}a.
$$

The acceleration conversion scales a supplied dimensionless acceleration; it
does not derive proper acceleration from a trajectory or equate it with coordinate
acceleration. `for_acceleration(a, unit="g")` chooses $T_0=c/a_{\mathrm{SI}}$, so
unit natural proper acceleration has the requested physical magnitude.

### Coordinate policies

`ConformalSpacetimeModel` accepts:

- `units="natural"`, the default;
- `units="si"` for seconds and metres; or
- `units=(time_unit, distance_unit)`, for example `("min", "km")`.

Set the scale using `time_scale_seconds` (default one second) or an existing
`unit_scale=SpacetimeUnits(...)`. Supplying both is an error. Model expression
views preserve the scale and coordinate policy.

`event`, `point`, `up`, and `spacetime_vector` accept a per-call `units` override
for numeric coordinates. `coordinates` accepts the same policy for output,
defaulting to the model's policy rather than remembering the event's input units.
Coordinates remain ordered $(t,x,y,z)$. Speed units such as `"m/s"` do not describe
this mixed-dimensional tuple and are rejected as a coordinate policy.

Multivectors already contain normalized algebra coordinates. They are never
converted a second time, even on a model whose default policy is SI. A nonnatural
explicit policy on multivector input is rejected. `down()` always returns a
natural-coordinate multivector.

Numeric centres passed to `signed_round` use the same coordinate boundary.
Its signed `radius_squared` is measured in the square of the selected distance
unit. A multivector centre is natural, but its radius still uses the selected
policy; `units="natural"` selects a wholly natural construction.

### Numbers and display strings

The backend's `time_from`, `distance_from`, `speed_from`, and `acceleration_from`
convert physical numbers to natural values. Its corresponding `*_in` methods
convert natural values to physical numbers. The model delegates the `*_in`
methods and `format_*` helpers to its backend.

`format_time`, `format_distance`, and `format_speed` select a useful unit by
magnitude or accept an explicit unit. `format_acceleration` defaults to standard
gravities. They return strings with a configurable number of significant digits;
numeric methods always return numbers. Negative values retain their sign.

The bounded registry includes:

| Quantity | Units |
|:--|:--|
| Time | ns, μs, ms, s, min, h, day, week, month, year |
| Distance | nm, μm, mm, cm, m, km, light-second, AU, ly |
| Speed | m/s, km/h, km/s, c, %c |
| Acceleration | m/s², g |

Common English spellings and ASCII micro-unit aliases are accepted. Automatic
distance display prefers astronomical units from 0.01 AU and light-years from
0.1 ly; smaller distances use everyday units. Automatic speed display uses
percent of $c$ from 1% of $c$. Months are one twelfth of a Julian year, not calendar
months; years are exactly 365.25 days. The backend uses no additional dependency.

### Algebra and expression ownership

The stored Gram matrix remains unchanged. For physical input, the actual vector is

$$
q=\frac{t_{\mathrm{SI}}}{T_0}\gamma_0+
\sum_{i=1}^3\frac{x^i_{\mathrm{SI}}}{cT_0}\gamma_i,
\qquad X(q)=n_o+q+\frac12q^2n_\infty.
$$

Thus a light signal with $x_{\mathrm{SI}}=ct_{\mathrm{SI}}$ still has zero
interval, derived by the actual algebra. `separation_squared` and classifier
properties such as centres and signed radii remain in natural units. Physical
conversion does not alter classification rules or attach unit metadata to every
multivector. Models sharing an algebra can assign different physical scales;
the caller must choose the model that gives a value its intended interpretation.

Compact numeric event expressions preserve the supplied coordinates, visible
unit labels, and hidden conversion factors. Replaying an expression applies
those factors without requiring access to its original model instance. Expanded
expressions use the normalized vector and ordinary embedding products.

`velocity_between` returns the average coordinate velocity vector in the model's
inertial frame, and `speed_between` its magnitude. Neither is proper velocity,
nor the instantaneous tangent speed of a curved worldline. Equal-time inputs
are rejected; spacelike displacements are allowed and are not clamped to $c$.

## Consequences

Physical input/output is convenient while metric arithmetic remains consistent
with existing CSTA operations. A 1g rotor example can use the same dimensionless
trajectory and convert its proper time, coordinate time, distance, and speed.

Float64 tolerances apply to natural values. The default one-second scale is
suited to light-second examples; metre-sized geometry can use $T_0=1/c$ seconds
to keep distances near unity. Unit conversion alone does not solve conditioning
problems or restore information lost through cancellation. Inputs, scales, and
numeric conversion results must be finite.

Tests compare physical constructions against natural constructions and actual
metric products, including event nullity, signed intervals, round radii,
classification, expression replay, scale preservation, formatting, and invalid
unit or scale boundaries.

## References

1. [BIPM, SI defining constants](https://www.bipm.org/en/measurement-units/si-defining-constants): the exact speed of light is 299,792,458 m/s.
2. [JPL, Astrodynamic Parameters](https://ssd.jpl.nasa.gov/astro_par.html): the astronomical unit is 149,597,870,700 m, a day is 86,400 s, and a Julian year is 365.25 days.
3. [NIST, SI conversion factors](https://www.nist.gov/pml/special-publication-811/nist-guide-si-appendix-b-conversion-factors/nist-guide-si-appendix-b9): standard gravity is 9.80665 m/s².
