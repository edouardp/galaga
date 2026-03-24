# Spacetime Algebra Notebook — Design

## Purpose

An interactive marimo notebook that teaches Spacetime Algebra (STA) through
the `ga` library. The audience is someone who knows some linear algebra and
special relativity but is new to geometric algebra. Every concept should have
a computed example, and the key physics should be interactive.

## Structure

### 1. What is STA?

Brief intro: Cl(1,3), one timelike basis vector (γ₀² = +1), three spacelike
(γᵢ² = −1). Show the basis vectors, their squares, and the pseudoscalar I.
Mention that STA unifies rotations, boosts, and electromagnetism in one algebra.

### 2. The Bivector Zoo

STA has six bivectors. They split into two families:

- **Timelike bivectors** (γ₀γᵢ): square to +1, generate Lorentz boosts
- **Spacelike bivectors** (γᵢγⱼ): square to −1, generate spatial rotations

Show all six with their squares. This is the key insight: the *sign of the
square* tells you whether a bivector generates a hyperbolic or circular
transformation.

### 3. Spatial Rotations

Interactive: slider for angle θ, rotate γ₁ in the γ₁γ₂ plane.
Show the rotor R = cos(θ/2) − sin(θ/2) γ₁γ₂, the sandwich product,
and the result. This should feel familiar from 3D rotations.

### 4. Lorentz Boosts

Interactive: slider for rapidity φ. Boost γ₀ along the γ₁ direction.
Show the rotor R = cosh(φ/2) + sinh(φ/2) γ₀γ₁.

Key points to demonstrate:
- The boosted timelike vector has both γ₀ and γ₁ components
- β = v/c = tanh(φ), γ = cosh(φ)
- The rotor is normalized: RR̃ = 1

### 5. Minkowski Diagram

Interactive matplotlib plot tied to the boost rapidity slider.
Show rest-frame axes (γ₀, γ₁), boosted axes (γ₀', γ₁'), and the light cone.
As rapidity increases, the boosted axes tilt toward the light cone but never
reach it.

### 6. Velocity Addition

Two rapidity sliders. Demonstrate that:
- Rapidities add: φ_total = φ₁ + φ₂
- Velocities compose via Einstein's formula: v = (v₁+v₂)/(1+v₁v₂)
- The speed of light is never exceeded

Include a matplotlib plot showing Einstein addition vs classical addition,
with the c ceiling visible.

### 7. Thomas-Wigner Rotation

Compose two boosts along *different* axes (x then y). Show that:
- R₁R₂ ≠ R₂R₁ (boosts don't commute)
- The difference (R₁R₂)(R₂R₁)⁻¹ is a pure spatial rotation
- This is the Thomas-Wigner rotation, with a γ₁γ₂ component

This is a result that's painful to derive with matrices but falls out
naturally from the algebra.

### 8. Electromagnetic Field

The EM field is a single bivector F = E + IB where:
- E = Eⁱ γᵢγ₀ (electric part, timelike bivectors)
- IB (magnetic part, spacelike bivectors)

Show a concrete example (E in x-direction, B in z-direction).
Compute F² and show the two Lorentz invariants:
- Scalar part: E² − B²
- Pseudoscalar part: 2E·B

### 9. Boosting the EM Field

Interactive: boost rapidity slider applied to the EM field F → RFR̃.
Demonstrate that:
- The electric and magnetic components mix under boosts
- F² is invariant (same scalar and pseudoscalar parts)
- A pure electric field in one frame has a magnetic component in another

### 10. Relative Vectors (Pauli Algebra)

The relative vectors σᵢ = γᵢγ₀ are bivectors in STA but form a
subalgebra isomorphic to the Pauli algebra:
- σᵢ² = 1
- σᵢσⱼ = −σⱼσᵢ for i ≠ j
- σ₁σ₂σ₃ = I (the pseudoscalar)

Show the multiplication table. Mention that this is how 3D vectors
"live inside" spacetime.

### 11. Symbolic Identities

Use the symbolic layer + simplify() to verify identities:
- ~~R = R (double reverse)
- RR̃ = 1 (rotor normalization)
- F + F = 2F (linearity)

This demonstrates the symbolic layer's usefulness for checking algebra.

## Design Principles

- Every formula should be computed, not just stated
- Interactive sliders for continuous parameters (angles, rapidities)
- matplotlib for geometric visualization (Minkowski diagrams, velocity plots)
- Use `_repr_latex_` for clean rendering — pass objects directly to mo.hstack
- Use `mo.hstack([label, value], justify="start")` for label-value pairs
- Use single `mo.md()` with joined strings for lists (avoid vstack spacing)
- Static LaTeX in `r"""..."""` blocks for explanatory text
- Keep cells small and focused — one concept per cell
