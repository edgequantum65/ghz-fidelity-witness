# ghz-fidelity-witness

[![tests](https://github.com/edgequantum65/ghz-fidelity-witness/actions/workflows/tests.yml/badge.svg)](https://github.com/edgequantum65/ghz-fidelity-witness/actions/workflows/tests.yml)

**Proving entanglement by measurement, not by looking at "000" and "111".**

Seeing only `000` and `111` in the computational basis proves nothing. A classical 50/50 mixture of `|000>` and `|111>` gives exactly the same counts. That mixture is now one of the blank controls (an ancilla qubit in `|+>` copied by CNOT onto the qubits, then ignored), and it is not declared entangled. The tool also measures X/Y correlations, in two ways:

**Fidelity** F with the ideal Bell or GHZ-3 state, from the stabilizer expansion of the projector:

```
|Phi+><Phi+| = (II + XX - YY + ZZ) / 4                                   (3 settings)
|GHZ><GHZ|   = (III + ZZI + IZZ + ZIZ + XXX - XYY - YXY - YYX) / 8        (5 settings)
```

**ENTANGLED** only if F − 3σ > 0.5 (genuine three-party entanglement for GHZ-3).

**Two-setting witness** for any number of qubits n (G. Tóth and O. Gühne, Phys. Rev. Lett. 94, 060501 (2005)):

```
W   = 3·I − 2·[ (X…X + I)/2 + Π_{k=2..n} (Z_{k−1}Z_k + I)/2 ]
<W> = 2 − <X…X> − 2·[P(0…0) + P(1…1)]          (2 settings: X…X and Z…Z)
```

**GENUINELY ENTANGLED** only if ⟨W⟩ + 3σ < 0. Two settings for any n, instead of 2^(n−1)+1 for the full expansion (129 for n = 8).

Otherwise the verdict is **NOT DEMONSTRATED**, which is not a proof of separability. The rules and the expected results were written in [CRITERIA.md](CRITERIA.md) and committed before each run (v1, then v2: the git history shows the order).

Edge Quantum 65 — R&D lab, Lannemezan, France. Rule of the lab: nothing is published that was not measured.

## Results (Qiskit Aer, 20 000 shots per setting, seed 1234)

**Fidelity, v2.** Each measurement setting has its own simulator seed, and σ is exact: per-setting sample variance (covariances between terms sharing a setting kept), settings added in quadrature.

| Case | F | 3σ | Verdict |
|---|---:|---:|---|
| E1 Bell, ideal | 1.0000 | 0.0000 | ENTANGLED |
| E2 GHZ-3, ideal | 1.0000 | 0.0000 | ENTANGLED |
| E3 GHZ-3, noise p=0.02 | 0.9171 | 0.0032 | ENTANGLED |
| E4 GHZ-3, noise p=0.30 | 0.3678 | 0.0073 | NOT DEMONSTRATED |
| R1 GHZ-3, readout error | 0.8934 | 0.0039 | ENTANGLED |
| Control: product state 000 | 0.5014 | 0.0053 | NOT DEMONSTRATED |
| Control: product state +++ | 0.2507 | 0.0065 | NOT DEMONSTRATED |
| Control: mixture of 00 and 11 | 0.5022 | 0.0075 | NOT DEMONSTRATED |
| Control: mixture of 000 and 111 | 0.4986 | 0.0053 | NOT DEMONSTRATED |

v1 (same seed for every setting, σ added linearly) is kept and still regenerated digit for digit in [RESULTS.md](RESULTS.md). It had a flaw: with one seed for all settings, the settings were not independent experiments (for `000`, the counts of XYY, YXY and YYX were identical). The v2 3σ is smaller than the v1 one in every case with shot noise (both are 0 for the ideal states).

**Two-setting witness.** ⟨W⟩ ± 3σ. Bold: GENUINELY ENTANGLED. Depolarizing error p after every gate.

| n | Ideal | p = 0.02 | p = 0.10 |
|---:|---:|---:|---:|
| 3 | **−1.0000 ± 0.0000** | **−0.8364 ± 0.0119** | **−0.2883 ± 0.0227** |
| 4 | **−1.0000 ± 0.0000** | **−0.7749 ± 0.0138** | **−0.0604 ± 0.0253** |
| 5 | **−1.0000 ± 0.0000** | **−0.7134 ± 0.0154** | +0.1545 ± 0.0271 |
| 6 | **−1.0000 ± 0.0000** | **−0.6502 ± 0.0169** | +0.3382 ± 0.0283 |
| 7 | **−1.0000 ± 0.0000** | **−0.5838 ± 0.0183** | +0.5020 ± 0.0290 |
| 8 | **−1.0000 ± 0.0000** | **−0.5291 ± 0.0193** | +0.6396 ± 0.0295 |

More qubits means more CNOTs, so the witness degrades with n: at p = 0.10 it is lost from n = 5 on, as predicted before the run. GHZ-8 with readout error only: **−0.3036 ± 0.0227**. Blank controls `|0…0>`, `|+…+>` and the mixture, for n = 3, 5 and 8: all NOT DEMONSTRATED, each within 3σ of its exact value (0, 1 − 2^(2−n), 0). Full tables: [RESULTS.md](RESULTS.md).

All expectations written before the runs in [CRITERIA.md](CRITERIA.md) are met (v1: 6 of 6, v2: 13 of 13).

**Limits.** This is still a classical simulation on a laptop, not quantum hardware. No real device has been run yet: that needs an IBM Quantum account and is the next step. The noise models (depolarizing error on every gate, readout error P(1|0) = 0.02, P(0|1) = 0.03) are textbook models, not a real device. States exactly on the boundary (`000`, the mixture) are wrongly called entangled with probability about 0.13 % per case: that is the price of a one-sided 3σ rule. Inside a case the settings are independent, but every case uses the same base seed, so cases are not independent of each other: at p = 0.10 the measured P(all equal) sits 2 to 3σ below the hand model for n = 5 to 8, all in the same direction (still inside the tolerance fixed in advance).

## Run

```bash
pip install -r requirements.txt     # pinned: qiskit 2.3.0, qiskit-aer 0.17.2
python -m unittest -v test_reference_cases   # about 20 s
python ghz_witness.py                        # about 20 s, rewrites RESULTS.md next to the script
```

On every push, CI runs the tests, reruns `ghz_witness.py` and checks that `RESULTS.md` comes out identical: the published numbers regenerate from the committed code.

---

**FR** — Voir seulement « 000 » et « 111 » ne prouve pas l'intrication : un simple mélange classique donne les mêmes comptes, et ce mélange fait maintenant partie des témoins. L'outil mesure aussi les corrélations X/Y : fidélité à l'état GHZ (verdict « intriqué » seulement si F − 3σ > 0,5) et témoin de Tóth et Gühne à deux réglages pour n qubits (verdict seulement si ⟨W⟩ + 3σ < 0). Les états produits et le mélange servent de témoins et ne sont jamais déclarés intriqués. Critères écrits et déposés avant chaque essai. Simulation classique sur PC : aucun processeur quantique réel n'a encore été utilisé, c'est la prochaine étape.

License: MIT.
