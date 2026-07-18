---
status: accepted
date: 2026-07-18
deciders: edouard
---

# ADR-001: Use Architectural Decision Records

## Context and problem statement

Gram makes choices that are not obvious from code alone: whether a Gram matrix
or signature is canonical, what a bitmask blade means in a nonorthogonal basis,
which inner-product convention an operator selects, and when product storage
changes strategy. Analytic functions add branch and convergence choices that
are equally invisible in a function name. Several decisions deliberately
depart from old Galaga behavior or from one common mathematical convention.

Without a durable rationale, future refactoring could accidentally restore an
orthogonal-basis assumption or change a public operation while preserving its
name.

## Decision drivers

- Mathematical conventions need explicit definitions.
- Performance choices must remain separate from semantics.
- The Galaga migration needs a record of intentional incompatibilities.
- Design rationale should be reviewed and versioned with code.

## Considered options

1. Explain decisions only in code comments.
2. Maintain one continuously edited design document.
3. Keep lightweight, numbered ADRs alongside guides and specifications.

## Decision outcome

Use numbered Markdown ADRs in `docs/adrs`. Each significant decision records
its context, selected outcome, and consequences. Superseding decisions receive
new numbers rather than rewriting history.

## Consequences

- Good, because code review can assess behavior and rationale together.
- Good, because convention changes become visible migration events.
- Good, because specifications can remain focused on observable behavior.
- Cost, because architectural changes require documentation maintenance.
