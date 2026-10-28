# ghz-fidelity-witness

[![tests](https://github.com/edgequantum65/ghz-fidelity-witness/actions/workflows/tests.yml/badge.svg)](https://github.com/edgequantum65/ghz-fidelity-witness/actions/workflows/tests.yml)

**Proving entanglement by measurement, not by looking at "000" and "111".**

Seeing only `000` and `111` in the computational basis proves nothing. A classical 50/50 mixture of `|000>` and `|111>` gives exactly the same counts. That mixture is now one of the blank controls (an ancilla qubit in `|+>` copied by CNOT onto the qubits, then ignored): it must never be declared entangled. The tool also measures X/Y correlations, in two ways:

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

v2 results (independent seed per setting, exact σ, mixture control, readout error, two-setting witness for n = 3 to 8): run pending, expectations fixed in CRITERIA.md v2.

**Limits.** This is still a classical simulation on a laptop, not quantum hardware. No real device has been run yet: that needs an IBM Quantum account and is the next step. The noise models (depolarizing error on every gate, readout error P(1|0) = 0.02, P(0|1) = 0.03) are textbook models, not a real device. States exactly on the boundary (`000`, the mixture) are wrongly called entangled with probability about 0.13 % per case: that is the price of a one-sided 3σ rule.

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
