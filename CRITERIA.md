# Criteria — written 2026-10-28, before the first run

**Tool**: `ghz_witness.py` estimates the fidelity F of a prepared state with the ideal Bell state (2 qubits) or GHZ state (3 qubits). It uses the stabilizer expansion of the projector and measures only Pauli settings. No access to the simulator's state vector.

**Decision rule** (fixed now):
- F − 3σ > 0.5: **ENTANGLED** (for GHZ-3: genuine three-party entanglement, since every biseparable state has F ≤ 0.5).
- otherwise: **NOT DEMONSTRATED**. This is not a proof of separability.
- σ is a conservative bound: the shot-noise standard errors of the measured terms, added linearly.

**Expected results** (20 000 shots per setting, simulator seed 1234):
- E1: ideal Bell state gives ENTANGLED, F ≥ 0.98.
- E2: ideal GHZ-3 state gives ENTANGLED, F ≥ 0.98.
- E3: GHZ-3 with depolarizing noise p = 0.02 on every gate gives ENTANGLED.
- E4: GHZ-3 with depolarizing noise p = 0.30 on every gate gives NOT DEMONSTRATED.
- **Blank controls**: the product state |000> gives F within 3σ of 0.5 and verdict NOT DEMONSTRATED; the product state |+++> gives F within 3σ of 0.25 and verdict NOT DEMONSTRATED.

All results are published whatever they show. A failed expectation is reported as failed.

## v2, 2026-10-28, written before the v2 run

Nothing above this line is changed. v1 stays as it was, with its outcomes. This section fixes the v2 methods, decision rules and expected results before any v2 case is run.

**Why a v2.** (1) In v1 every measurement setting used the same simulator seed, so the settings were not independent experiments (for the |000> control, the counts of XYY, YXY and YYX are identical). (2) The headline claim "a classical 50/50 mixture of |0…0> and |1…1> gives the same Z counts but is not entangled" was not among the controls. (3) The full stabilizer expansion needs 2^(n−1)+1 settings; a two-setting witness scales to any n.

**Methods (fixed now).**
- *Independent settings.* All settings of one case are sent to Qiskit Aer in one batch (`sim.run([...])`, `seed_simulator=1234`), in a fixed order: order of first appearance in the term list for the fidelity, X…X then Z…Z for the witness. Qiskit Aer 0.17.2 gives circuit i of a batch the seed 1234 + 2113·i (observed on a test circuit before this run, not a documented guarantee). The seeds Aer reports are checked to be pairwise distinct and printed in RESULTS.md.
- *Exact σ (fidelity v2).* For each setting s, every shot gives v = Σ (coefficient × ±1 parity) over the terms measured by s; σ_s² = sample variance of v (n−1 denominator) / shots. This keeps the covariances between terms that share a setting. Settings are independent, so σ = √(Σ_s σ_s²) / 2^n.
- *Two-setting witness* (G. Tóth and O. Gühne, Phys. Rev. Lett. 94, 060501 (2005)): W = 3·I − 2[(X^⊗n + I)/2 + Π_{k=2..n} (Z_{k−1}Z_k + I)/2]. The product is the projector on "all bits equal", so ⟨W⟩ = 2 − ⟨X^⊗n⟩ − 2·[P(0…0) + P(1…1)]: one setting X…X, one setting Z…Z, for any n. Ideal values (checked against an exact matrix computation before this section was written): GHZ −1; |0…0> 0; mixture 0; |+…+> 1 − 2^(2−n). Every biseparable state has ⟨W⟩ ≥ 0, and W ≥ I − 2|GHZ><GHZ|, so ⟨W⟩ < 0 also implies F > 1/2. σ_W² = Var(X…X parity)/shots + 4·Var(all-equal indicator)/shots (sample variances).
- *Mixture control* (kind "mixture"): an ancilla qubit (index n) is put in |+> and a CNOT copies it onto each of the n qubits. The ancilla is never rotated and is ignored in every term, so the n qubits hold ½(|0…0><0…0| + |1…1><1…1|): exactly the Z-basis counts of GHZ, no entanglement among the n qubits.
- *Noise models* (textbook models, not a device): depolarizing error p after every h, sdg (1 qubit) and cx (2 qubits), as in v1, basis-change gates included. Readout case: `ReadoutError([[0.98, 0.02], [0.03, 0.97]])` on every qubit (reads 1 for 0 with probability 2 %, reads 0 for 1 with probability 3 %), no gate noise.
- 20 000 shots per setting, base seed 1234, for every v2 case.

**Decision rules v2.**
- Fidelity v2: **ENTANGLED** iff F − 3σ > 0.5 with the exact σ above; otherwise **NOT DEMONSTRATED**.
- Witness: **GENUINELY ENTANGLED** iff ⟨W⟩ + 3σ_W < 0; otherwise **NOT DEMONSTRATED** (not a proof of separability).
- For states sitting exactly on the boundary (F = 0.5, or ⟨W⟩ = 0: |0…0>, the mixture), a one-sided 3σ rule still gives a false "entangled" verdict with probability about 0.13 % per case. This is accepted, not hidden.

**Predictions for the noisy witness cases** come from a hand model, not from running the code: ⟨X^⊗n⟩ = (1−p)^(2n) (the X string touches n measurement H, n−1 CNOT and 1 preparation H, each noisy gate scales it by 1−p); P(all equal) from the classical Markov chain of the Z-basis bits (each CNOT copies the bit, then with probability p both of its qubits are randomized). Readout: ⟨X^⊗n⟩ = 0.95^n + 0.01^n, P(all equal) = ½(0.98^n + 0.02^n + 0.97^n + 0.03^n). More qubits means more CNOTs, so the witness degrades with n.

**Expected results v2.**
- V1. The v1 table is regenerated identically (same six rows, same digits) by `method="v1"`.
- V2. Fidelity v2, E1 (Bell) and E2 (GHZ-3) ideal: F = 1.0000, 3σ = 0.0000, ENTANGLED.
- V3. Fidelity v2, E3 (GHZ-3, p = 0.02): ENTANGLED, |F − 0.9161| ≤ 0.02. E4 (p = 0.30): NOT DEMONSTRATED, |F − 0.3641| ≤ 0.03.
- V4. Fidelity v2 blank controls: |000>, mixture n = 2, mixture n = 3 give |F − 0.5| ≤ 3σ and NOT DEMONSTRATED; |+++> gives |F − 0.25| ≤ 3σ and NOT DEMONSTRATED.
- V5. Fidelity v2, R1 (GHZ-3, readout error only): ENTANGLED, |F − 0.892| ≤ 0.01 (hand model: 0.8922).
- V6. For each of the six v1 cases, v2 3σ ≤ v1 3σ (exact σ is never larger than the linear sum, up to sampling).
- V7. In v2 the per-setting seeds of a case are pairwise distinct, and for |000> the counts of XYY, YXY and YYX are not all identical.
- W1. Witness, ideal GHZ, n = 3…8: ⟨W⟩ = −1.0000, 3σ = 0.0000, GENUINELY ENTANGLED.
- W2. Witness, GHZ with p = 0.02, n = 3…8: all GENUINELY ENTANGLED, |⟨W⟩ − model| ≤ 0.03, model −0.836, −0.772, −0.710, −0.649, −0.590, −0.533.
- W3. Witness, GHZ with p = 0.10: n = 3 and 4 GENUINELY ENTANGLED, n = 5, 6, 7, 8 NOT DEMONSTRATED; |⟨W⟩ − model| ≤ 0.03, model −0.291, −0.060, +0.143, +0.322, +0.479, +0.618.
- W4. At p = 0.02 and at p = 0.10, ⟨W⟩ increases strictly with n.
- W5. Witness, GHZ-8 with readout error only: GENUINELY ENTANGLED, |⟨W⟩ − (−0.298)| ≤ 0.03.
- W6. Witness blank controls for n = 3, 5, 8: |0…0> and the mixture give |⟨W⟩| ≤ 3σ and NOT DEMONSTRATED; |+…+> gives |⟨W⟩ − (1 − 2^(2−n))| ≤ 3σ (0.5, 0.875, 0.984375) and NOT DEMONSTRATED.

All v2 results are published whatever they show. A failed expectation is reported as failed; the criteria are not changed after the run.
