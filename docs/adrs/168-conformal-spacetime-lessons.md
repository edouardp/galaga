---
status: accepted
date: 2026-10-01
deciders: edouard
---

# ADR-168: Conformal Spacetime Teaching Notebooks

## Context

The CSTA notes supplied for the notebook gallery connect the null-pair
construction to causal intervals, signed rounds, uniform acceleration,
conformal transformations, and a future object classifier. Galaga supports
arbitrary Gram matrices and the required products, but has no public CSTA
object classifier. Some physical descriptions in the notes need qualifiers:
a signed-radius equation in full $3+1$ spacetime specifies a hypersurface,
not one accelerated worldline, and an algebraic intersection does not select
the future branch.

## Decision

Add three maintained Marimo lessons using the common ordered basis
$\{\gamma_0,\gamma_1,\gamma_2,\gamma_3,n_o,n_\infty\}$, spacetime
metric $(+---)$, null pairing $n_o\cdot n_\infty=-1$, and normalized event
embedding $X(x)=n_o+x+\frac12x^2n_\infty$. The stored Gram matrix has
signature $(2,4)$.
Each lesson derives numerical claims from the Galaga product and checks them
against independently specified coordinates or incidence conditions.

The event lesson treats causal pairings, signed-radius incidence, and an
accelerating observer's radar reception. It distinguishes the full
signed-radius hypersurface from the observer's selected worldline and
filters algebraic intersections by future direction. The transformation
lesson checks translation and dilation versors against direct event
embedding, including conformal-weight normalization after dilation. The
classifier lesson demonstrates a **scoped worksheet** for known point pairs,
flat lines, and normalized IPNS rounds. It reports structural information
before causal interpretation and explicitly does not classify arbitrary
multivectors or introduce a library API.

The event lesson keeps the geometric calculation in natural units and uses
acceleration measured in standard gravities to supply the scales $T_0=c/a$
and $L_0=c^2/a$. Notebook-local converters return numeric values in selected
units or human-readable strings. Years are Julian years; months are defined
as one twelfth of a Julian year. Astronomical landmarks are approximate
distance comparisons, not modeled rendezvous targets.

Present the boost rotor, event embedding, three-event wedge, and each meet
in short code cells alongside their mathematical equations. Explain the
connection to three-point circles in Euclidean CGA: Alice's conformally
embedded samples determine a hyperbolic round in a timelike plane. The
rotor constructs the samples and independently agrees with the hyperbolic
coordinate formulas. The plane–round meet gives the same curve up to scale.
The reception and immediate-echo examples both verify the physically selected
event against the computed intersection blade. Numeric clock calculations
select the future roots; the meet itself does not extract a timestamp.

The notes' twistor and spinor interpretations are left to separate work
because the present examples do not construct or verify that representation.

## Consequences

The gallery gains a reproducible CSTA path from the Witt pair to events,
actions, and metric-aware object names. The lesson checks guard against sign
changes in conformal embedding, round radius, translation, dilation, and
causal labeling. The work changes no public Galaga API.
