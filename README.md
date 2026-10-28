# ghz-fidelity-witness

[![tests](https://github.com/edgequantum65/ghz-fidelity-witness/actions/workflows/tests.yml/badge.svg)](https://github.com/edgequantum65/ghz-fidelity-witness/actions/workflows/tests.yml)

**Proving entanglement by measurement, not by looking at "000" and "111".**

Seeing only `000` and `111` in the computational basis proves nothing. A classical 50/50 mixture of `|000>` and `|111>` gives exactly the same counts. This tool also measures X/Y correlations and estimates the fidelity F with the ideal Bell or GHZ state, using the stabilizer expansion of the projector:

```
|Phi+><Phi+| = (II + XX - YY + ZZ) / 4                                   (3 settings)
|GHZ><GHZ|   = (III + ZZI + IZZ + ZIZ + XXX - XYY - YXY - YYX) / 8        (5 settings)
```

F > 1/2 certifies entanglement (genuine three-party entanglement for GHZ-3). Verdict rule, fixed before the run: **ENTANGLED** only if F − 3σ > 0.5, otherwise **NOT DEMONSTRATED** (which is not a proof of separability).

Edge Quantum 65 — R&D lab, Lannemezan, France. Rule of the lab: nothing is published that was not measured.

## Result (Qiskit Aer, 20 000 shots per setting, seed 1234)

| Case | F | 3σ | Verdict |
|---|---:|---:|---|
| E1 Bell, ideal | 1.0000 | 0.0000 | ENTANGLED |
| E2 GHZ-3, ideal | 1.0000 | 0.0000 | ENTANGLED |
| E3 GHZ-3, noise p=0.02 | 0.9161 | 0.0075 | ENTANGLED |
| E4 GHZ-3, noise p=0.30 | 0.3641 | 0.0171 | NOT DEMONSTRATED |
| Control: product state 000 | 0.4995 | 0.0106 | NOT DEMONSTRATED |
| Control: product state +++ | 0.2500 | 0.0159 | NOT DEMONSTRATED |

All six expectations written before the run in [CRITERIA.md](CRITERIA.md) are met. The two product states are blank controls: they must never be declared entangled, and they are not. The product state `000` sits right at the 0.5 boundary, which is why the rule asks for a 3σ margin.

**Limits.** This is a classical simulation on a laptop, not quantum hardware. The noise model (depolarizing error on every gate) is a textbook model, not a real device. σ is a conservative bound: the shot-noise errors of the measured terms, added linearly.

## Run

```bash
pip install qiskit qiskit-aer
python -m unittest test_reference_cases
python ghz_witness.py        # a few seconds, writes RESULTS.md
```

---

**FR** — Voir seulement « 000 » et « 111 » ne prouve pas l'intrication : un simple mélange classique donne les mêmes comptes. L'outil mesure aussi les corrélations X/Y et estime la fidélité à l'état GHZ. Verdict « intriqué » seulement si F − 3σ > 0,5. Les états produits servent de témoins et ne sont jamais déclarés intriqués. Critères écrits avant l'essai, simulation classique sur PC.

License: MIT.
