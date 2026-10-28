# Results

## v1: fidelity, same seed for every setting, σ added linearly

20 000 shots per setting, simulator seed 1234 (Qiskit Aer, classical simulation)

| Case | F | 3σ | Verdict |
|---|---:|---:|---|
| E1 Bell, ideal | 1.0000 | 0.0000 | ENTANGLED |
| E2 GHZ-3, ideal | 1.0000 | 0.0000 | ENTANGLED |
| E3 GHZ-3, noise p=0.02 | 0.9161 | 0.0075 | ENTANGLED |
| E4 GHZ-3, noise p=0.30 | 0.3641 | 0.0171 | NOT DEMONSTRATED |
| Control: product state 000 | 0.4995 | 0.0106 | NOT DEMONSTRATED |
| Control: product state +++ | 0.2500 | 0.0159 | NOT DEMONSTRATED |

## v2: fidelity, independent settings, exact σ

20 000 shots per setting, base seed 1234, one independent seed per setting (Qiskit Aer, classical simulation). Exact σ: per-setting sample variance, settings added in quadrature.

| Case | F | 3σ | Verdict | Seeds reported by Aer (one per setting) |
|---|---:|---:|---|---|
| E1 Bell, ideal | 1.0000 | 0.0000 | ENTANGLED | 1234, 3347, 5460 |
| E2 GHZ-3, ideal | 1.0000 | 0.0000 | ENTANGLED | 1234, 3347, 5460, 7573, 9686 |
| E3 GHZ-3, noise p=0.02 | 0.9171 | 0.0032 | ENTANGLED | 1234, 3347, 5460, 7573, 9686 |
| E4 GHZ-3, noise p=0.30 | 0.3678 | 0.0073 | NOT DEMONSTRATED | 1234, 3347, 5460, 7573, 9686 |
| Control: product state 000 | 0.5014 | 0.0053 | NOT DEMONSTRATED | 1234, 3347, 5460, 7573, 9686 |
| Control: product state +++ | 0.2507 | 0.0065 | NOT DEMONSTRATED | 1234, 3347, 5460, 7573, 9686 |
| Control: mixture of 00 and 11 | 0.5022 | 0.0075 | NOT DEMONSTRATED | 1234, 3347, 5460 |
| Control: mixture of 000 and 111 | 0.4986 | 0.0053 | NOT DEMONSTRATED | 1234, 3347, 5460, 7573, 9686 |
| R1 GHZ-3, readout error | 0.8934 | 0.0039 | ENTANGLED | 1234, 3347, 5460, 7573, 9686 |

## v2: two-setting witness (Tóth & Gühne, PRL 94, 060501, 2005)

Two settings (X…X, then Z…Z) for any n, 20 000 shots each, base seed 1234; seeds reported by Aer: 1234, 3347. ⟨W⟩ = 2 − ⟨X…X⟩ − 2·P(all equal). The full stabilizer expansion would need 2^(n−1)+1 settings (129 for n = 8).

| Case | n | ⟨X…X⟩ | P(all equal) | ⟨W⟩ | 3σ | Verdict |
|---|---:|---:|---:|---:|---:|---|
| GHZ-3, ideal | 3 | 1.0000 | 1.0000 | -1.0000 | 0.0000 | GENUINELY ENTANGLED |
| GHZ-4, ideal | 4 | 1.0000 | 1.0000 | -1.0000 | 0.0000 | GENUINELY ENTANGLED |
| GHZ-5, ideal | 5 | 1.0000 | 1.0000 | -1.0000 | 0.0000 | GENUINELY ENTANGLED |
| GHZ-6, ideal | 6 | 1.0000 | 1.0000 | -1.0000 | 0.0000 | GENUINELY ENTANGLED |
| GHZ-7, ideal | 7 | 1.0000 | 1.0000 | -1.0000 | 0.0000 | GENUINELY ENTANGLED |
| GHZ-8, ideal | 8 | 1.0000 | 1.0000 | -1.0000 | 0.0000 | GENUINELY ENTANGLED |
| GHZ-3, noise p=0.02 | 3 | 0.8884 | 0.9740 | -0.8364 | 0.0119 | GENUINELY ENTANGLED |
| GHZ-4, noise p=0.02 | 4 | 0.8534 | 0.9607 | -0.7749 | 0.0138 | GENUINELY ENTANGLED |
| GHZ-5, noise p=0.02 | 5 | 0.8187 | 0.9474 | -0.7134 | 0.0154 | GENUINELY ENTANGLED |
| GHZ-6, noise p=0.02 | 6 | 0.7836 | 0.9333 | -0.6502 | 0.0169 | GENUINELY ENTANGLED |
| GHZ-7, noise p=0.02 | 7 | 0.7499 | 0.9170 | -0.5838 | 0.0183 | GENUINELY ENTANGLED |
| GHZ-8, noise p=0.02 | 8 | 0.7259 | 0.9016 | -0.5291 | 0.0193 | GENUINELY ENTANGLED |
| GHZ-3, noise p=0.10 | 3 | 0.5347 | 0.8768 | -0.2883 | 0.0227 | GENUINELY ENTANGLED |
| GHZ-4, noise p=0.10 | 4 | 0.4421 | 0.8092 | -0.0604 | 0.0253 | GENUINELY ENTANGLED |
| GHZ-5, noise p=0.10 | 5 | 0.3510 | 0.7472 | +0.1545 | 0.0271 | NOT DEMONSTRATED |
| GHZ-6, noise p=0.10 | 6 | 0.2846 | 0.6886 | +0.3382 | 0.0283 | NOT DEMONSTRATED |
| GHZ-7, noise p=0.10 | 7 | 0.2271 | 0.6354 | +0.5020 | 0.0290 | NOT DEMONSTRATED |
| GHZ-8, noise p=0.10 | 8 | 0.1855 | 0.5875 | +0.6396 | 0.0295 | NOT DEMONSTRATED |
| GHZ-8, readout error | 8 | 0.6634 | 0.8201 | -0.3036 | 0.0227 | GENUINELY ENTANGLED |
| Control: product 0…0, n=3 | 3 | 0.0021 | 1.0000 | -0.0021 | 0.0212 | NOT DEMONSTRATED |
| Control: product 0…0, n=5 | 5 | -0.0073 | 1.0000 | +0.0073 | 0.0212 | NOT DEMONSTRATED |
| Control: product 0…0, n=8 | 8 | 0.0054 | 1.0000 | -0.0054 | 0.0212 | NOT DEMONSTRATED |
| Control: product +…+, n=3 | 3 | 1.0000 | 0.2506 | +0.4988 | 0.0184 | NOT DEMONSTRATED |
| Control: product +…+, n=5 | 5 | 1.0000 | 0.0624 | +0.8751 | 0.0103 | NOT DEMONSTRATED |
| Control: product +…+, n=8 | 8 | 1.0000 | 0.0089 | +0.9822 | 0.0040 | NOT DEMONSTRATED |
| Control: mixture 0…0 / 1…1, n=3 | 3 | -0.0144 | 1.0000 | +0.0144 | 0.0212 | NOT DEMONSTRATED |
| Control: mixture 0…0 / 1…1, n=5 | 5 | 0.0004 | 1.0000 | -0.0004 | 0.0212 | NOT DEMONSTRATED |
| Control: mixture 0…0 / 1…1, n=8 | 8 | -0.0009 | 1.0000 | +0.0009 | 0.0212 | NOT DEMONSTRATED |

Noise models are textbook models, not a device: depolarizing error p after every h, sdg and cx; readout error P(1|0) = 0.02, P(0|1) = 0.03 on every qubit.
