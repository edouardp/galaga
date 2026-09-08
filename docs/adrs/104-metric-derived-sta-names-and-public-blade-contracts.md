---
status: accepted
date: 2026-09-08
deciders: edouard
---

# ADR-104: Metric-Derived STA Names and Public Blade Contracts

The remaining mixed-suite naming presets now have public owners.
[ADR-117](117-public-naming-presets-and-exterior-word-contracts.md) records
complete vocabulary replay and general-Gram checks distinguishing exterior
blade labels from geometric vector words, without changing this design.

## Context and problem statement

The remaining legacy blade-convention suite has 102 methods and 107 collected
cases. It covers indexed vocabulary, complete STA name/sign tables, styles,
overrides, lookup, mutation, and numeric independence. All 107 cases pass
before migration. The public immutable convention already owns most of these
responsibilities, but lacks optional sigma and pseudovector vocabulary.

Compute the products before selecting labels. In particular, `Algebra(3, 1)`
has ordered squares `(+,+,+,-)`, not the time-first mostly-plus `(-,+,+,+)`.
Inertia alone cannot determine the signs of named products. The old lookup
test also equates `blade("σ₁")` with the positive canonical bivector even
though its displayed name denotes the negative of that blade.

## Decision outcome

### Derive optional STA vocabulary from explicit ordered squares

Extend `spacetime_blade_convention` with keyword-only `signature`, `sigmas`,
and `pseudovectors`. The no-argument convention remains unchanged: gamma
words, pseudoscalar `i`, positive native orientations, and time/space roles.
Both naming flags default to false and require actual Python booleans.

With $I=\gamma_0\gamma_1\gamma_2\gamma_3$, the optional names mean:

| Option | ASCII names | Defined products |
|---|---|---|
| `sigmas=True` | `s1` … `s3` | $\gamma_k\gamma_0$ |
| `sigmas=True` | `is1` … `is3` | $I\gamma_k\gamma_0$ |
| `pseudovectors=True` | `ig0` … `ig3` | $I\gamma_k$ |

Signed options require an explicit ordered four-entry real unit-diagonal
signature. Accept ±1, including NumPy real basis squares; reject booleans,
nonfinite, complex, null, scaled, wrong-length, and matrix inputs.
This is a diagonal-signature contract, not a general Gram parser. A caller
passing an algebra's diagonal must first know that the frame is orthogonal.
Applying a convention remains a presentation operation: it does not validate
that a different algebra has the metric used to derive its labels.

All sixteen unit-diagonal sign patterns have well-defined word reductions.
The low-level factory supports them without inferring a physical time axis.
The complete `SpacetimePreset`/`p_sta` remain time-first Lorentzian setups;
their new flags derive labels from their own actual ordered metric.

A bounded standard-library helper reduces each fixed vector word using
anticommutation and repeated-vector squares. Do not hardcode sign tables,
import the numeric engine into presentation, or duplicate a general geometric
product backend. General Gram products can mix blades or acquire non-unit
scale: use ordinary computed multivectors and immutable names there.

### Preserve signed lookup and independent presentation components

Store each derived result as `BladeRef(mask, orientation)`. Looking up any
canonical target spelling returns the actual signed product. Rendering a
positive native mask accounts for that orientation. Retain the displaced
gamma spellings as positive-native aliases, so `s1` means $\gamma_1\gamma_0$
while `g0g1` means $\gamma_0\gamma_1$. Expression literals, replay, equality,
and hashes retain the same numeric meaning.

Presets generate Python locals from canonical ASCII names, including the
correct orientations. A standalone `with_blades` still changes only labels:
changing local bindings requires an explicit `LocalNamePolicy` replacement.
The default convention, numeric definition, storage order, and core sharing
do not change. Follow through ADR-076; do not restore mutable conventions.

### Keep every historical responsibility, documenting deliberate differences

The [archive](../../packages/galaga/tools/baselines/blade-convention-contracts-v1.json)
records all 102 original method sources, the original case count, and twelve
complete legacy STA tables: three ordered metrics × four flag combinations.
It was captured at `a502b30` on 2026-09-08 with Python 3.14.4 and NumPy 2.5.2;
the full source hash is stored. All 102 class/method identities and 107 cases
remain live against public APIs, with the complete literal STA tables retained.

Existing v2 differences are explicit contracts, not hidden compatibility
adapters:

- Replace `b_*` setup with complete presets or `indexed_blade_convention`;
  supply target-aware `Name` objects for Greek prefixes/custom subscripts.
- Override native masks with strings, `Name`, or signed `BladeLabel` objects,
  not metric-role strings or legacy name tuples.
- Use `blade_label` for frozen metadata. Replace labels in a new convention
  and view; use scoped presentation for existing values, not live mutation.
- Unknown names raise `KeyError`. `pss` can be an explicit alias; signed
  lookup must not reproduce the old unsigned sigma behavior.
- ASCII pseudovectors use `ig0` … `ig3`, not v1's `iy0` … `iy3`. This is the
  only spelling adjustment in archive-table replay.
- Repr remains ASCII with explicit Unicode display available.
- PGA presets remain Euclidean-first with a final null vector. Preserve
  historical null-first examples using explicit signatures and indexed names.
  PGA/CGA pseudoscalar labels are customizable, not automatically `I`.
- Renaming orthogonal CGA vectors does not make them null. Use the native-null
  preset for an actual null-pair Gram matrix.

Historical “cross-library” tests preserve spelling examples only; they do not
claim that another library was executed.

## Verification and consequences

New tests compare actual products before naming for all sixteen unit-diagonal
metrics and all three non-default option combinations. They cover all target
spellings, native aliases, signed literals, replay, hashes, preset locals,
immutability, and invalid inputs. Archive replay checks every old STA label
and sign against public values using a forced reference-backend algebra.
Corruption probes reject altered signs, names, masks, and unsigned lookup.
Fresh-process tests prohibit all legacy imports.
All 224 public blade cases also pass directly from the built wheel, with
package origins verified and test/tool directories excluded from the artifact.

The 739-case presentation/blade run passes. Every new production path is
covered; both production modules measure 98%, and all four blade test files
measure 100% line and branch coverage. Full package/release suites pass
5,620 cases on Python 3.11 and 5,737 on Python 3.14, including the maintained
gallery's headless exports. Existing core/facade coverage and the matrix
warning remain unchanged; type checking still reports 295 errors.

The construction notebook teaches both time-first metrics, computed signed
products, native-versus-named lookup, and the general-Gram boundary.
Remove `test_blade_convention.py` from the construction-exemption ledger,
reducing it from ten files to nine. RGA and mixed legacy dependencies, engine
deletion, and final stable-release gates remain separate unfinished work.
