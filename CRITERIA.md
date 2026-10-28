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
