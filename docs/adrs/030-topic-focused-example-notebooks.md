---
status: accepted
date: 2026-03-27
deciders: edouard
---

# ADR-030: Topic-Focused Example Notebooks for GA Teaching

## Context and Problem Statement

The repository already has broad marimo demonstrations, but users also need
examples that work as self-contained teaching notebooks for a single domain
topic. How should educational examples in `examples/` be organized?

## Decision Drivers

* Readers should be able to open one notebook and stay on one topic
* The notebooks should teach both the domain idea and the GA library workflow
* The lazy-basis-blade API is now a core part of the teaching story
* Interactive plots and controls are easier to follow in smaller notebooks

## Considered Options

1. Keep adding material to a few large omnibus notebooks
2. Prefer one-topic-per-notebook teaching examples in `examples/`
3. Move teaching content out of notebooks into prose docs only

## Decision Outcome

Chosen option: "Prefer one-topic-per-notebook teaching examples in `examples/`"
because it keeps each notebook coherent, makes topic discovery simpler, and
lets the examples consistently foreground lazy symbolic construction followed
by `.eval()` to show the concrete multivector result.

### Consequences

* Good, because users can study relativity, electromagnetism, optics, quantum
  spin, geometry, or kinematics independently
* Good, because each notebook can include interactive controls and visuals
  without becoming structurally overloaded
* Good, because the examples now consistently demonstrate `basis_vectors(symbolic=True)`
  as the preferred teaching entry point
* Bad, because there is some overlap between notebooks in related domains
