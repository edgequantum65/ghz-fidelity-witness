"""Entanglement proof by measurement: Bell / GHZ fidelity from Pauli settings.

Seeing only "000" and "111" in the computational basis does NOT prove entanglement:
a classical 50/50 mixture of |000> and |111> gives the same counts. This tool also
measures the X/Y correlations and estimates the fidelity F with the ideal state:

  |Phi+><Phi+| = (II + XX - YY + ZZ) / 4
  |GHZ><GHZ|   = (III + ZZI + IZZ + ZIZ + XXX - XYY - YXY - YYX) / 8

F > 1/2 certifies entanglement (genuine 3-party entanglement for GHZ-3).

v2 (see CRITERIA.md) adds an independent seed per setting, the exact standard error,
and the two-setting witness of Toth and Guhne (Phys. Rev. Lett. 94, 060501 (2005)):

  W   = 3 I - 2 [ (X...X + I)/2 + prod_{k=2..n} (Z_{k-1} Z_k + I)/2 ]
  <W> = 2 - <X...X> - 2 [P(0...0) + P(1...1)]

<W> < 0 certifies genuine n-party entanglement, with only two settings for any n.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from pathlib import Path

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, ReadoutError, depolarizing_error

# (coefficient, Pauli string), qubit 0 is the leftmost letter
TERMS = {
    2: [(1, "II"), (1, "XX"), (-1, "YY"), (1, "ZZ")],
    3: [(1, "III"), (1, "ZZI"), (1, "IZZ"), (1, "ZIZ"),
        (1, "XXX"), (-1, "XYY"), (-1, "YXY"), (-1, "YYX")],
}

# Textbook readout model, not a device: P(read 1 | 0) = 2 %, P(read 0 | 1) = 3 %.
READOUT = [[0.98, 0.02], [0.03, 0.97]]


def prepare(n: int, kind: str) -> QuantumCircuit:
    """kind "mixture": an ancilla (index n) in |+> is copied by CNOT onto the n qubits.
    Every term ignores the ancilla, so the n qubits hold the classical mixture
    1/2 (|0..0><0..0| + |1..1><1..1|): same Z counts as GHZ, no entanglement."""
    if kind == "mixture":
        qc = QuantumCircuit(n + 1)
        qc.h(n)
        for q in range(n):
            qc.cx(n, q)
        return qc
    qc = QuantumCircuit(n)
    if kind == "ghz":
        qc.h(0)
        for q in range(1, n):
            qc.cx(q - 1, q)
    elif kind == "zeros":
        pass
    elif kind == "plus":
        for q in range(n):
            qc.h(q)
    else:
        raise ValueError(kind)
    return qc


def setting_for(pauli: str) -> str:
    """Measurement basis per qubit; identity qubits are measured in Z (ignored)."""
    return "".join("Z" if p == "I" else p for p in pauli)


def make_simulator(noise_p: float = 0.0, readout: list | None = None) -> AerSimulator:
    """Depolarizing error p after every h, sdg (1 qubit) and cx (2 qubits); optional
    readout error on every qubit. Textbook models, not a device."""
    if noise_p <= 0 and readout is None:
        return AerSimulator()
    nm = NoiseModel()
    if noise_p > 0:
        nm.add_all_qubit_quantum_error(depolarizing_error(noise_p, 1), ["h", "sdg"])
        nm.add_all_qubit_quantum_error(depolarizing_error(noise_p, 2), ["cx"])
    if readout is not None:
        nm.add_all_qubit_readout_error(ReadoutError(readout))
    return AerSimulator(noise_model=nm)


def setting_circuit(prep: QuantumCircuit, setting: str) -> QuantumCircuit:
    qc = prep.copy()
    for q, basis in enumerate(setting):
        if basis == "X":
            qc.h(q)
        elif basis == "Y":
            qc.sdg(q)
            qc.h(q)
    qc.measure_all()
    return qc


def measure_setting(prep: QuantumCircuit, setting: str, sim, shots: int, seed: int) -> dict:
    """v1 path: one job per setting, the same seed for every setting."""
    qc = setting_circuit(prep, setting)
    job = sim.run(transpile(qc, sim, optimization_level=0), shots=shots, seed_simulator=seed)
    return job.result().get_counts()


def measure_settings(prep: QuantumCircuit, settings: list[str], sim, shots: int,
                     seed: int) -> tuple[list[dict], list[int]]:
    """v2 path: all settings of a case in one batch. Aer gives each circuit of a batch
    its own seed (Aer 0.17.2: seed + 2113 * index, observed, not documented). The seeds
    Aer reports are returned and must be distinct: the settings are independent."""
    circuits = [transpile(setting_circuit(prep, s), sim, optimization_level=0)
                for s in settings]
    result = sim.run(circuits, shots=shots, seed_simulator=seed).result()
    counts = [result.get_counts(i) for i in range(len(settings))]
    seeds = [r.seed_simulator for r in result.results]
    if len(set(seeds)) != len(seeds):
        raise RuntimeError(f"settings share a simulator seed: {seeds}")
    return counts, seeds


def _bits(key: str) -> str:
    """Qiskit bitstrings are little-endian: return them with qubit 0 first."""
    return key.replace(" ", "")[::-1]


def parity_sign(bits: str, pauli: str) -> int:
    """+1/-1 parity of the qubits where pauli is not I (bits: qubit 0 first)."""
    parity = sum(int(bits[q]) for q, p in enumerate(pauli) if p != "I") % 2
    return 1 if parity == 0 else -1


def expectation(counts: dict, pauli: str) -> tuple[float, float]:
    """<P> and its shot-noise standard error. Qiskit bitstrings are little-endian.
    Qubits beyond len(pauli) (e.g. the mixture ancilla) are ignored."""
    shots = sum(counts.values())
    support = [q for q, p in enumerate(pauli) if p != "I"]
    if not support:
        return 1.0, 0.0
    total = 0
    for bits, c in counts.items():
        b = _bits(bits)
        parity = sum(int(b[q]) for q in support) % 2
        total += c * (1 if parity == 0 else -1)
    e = total / shots
    return e, math.sqrt(max(0.0, 1.0 - e * e) / shots)


def mean_and_var_of_mean(counts: dict, value) -> tuple[float, float]:
    """Mean of a per-shot value and the variance of that mean (sample variance / shots)."""
    shots = sum(counts.values())
    vals = [(value(_bits(k)), c) for k, c in counts.items()]
    mean = sum(v * c for v, c in vals) / shots
    var = sum(c * (v - mean) ** 2 for v, c in vals) / (shots - 1)
    return mean, var / shots


@dataclass
class Result:
    label: str
    fidelity: float
    sigma: float
    verdict: str
    method: str = "v1"
    seeds: list[int] = field(default_factory=list)
    counts: dict[str, dict] = field(default_factory=dict)  # setting -> counts


def fidelity(label: str, n: int, kind: str, noise_p: float = 0.0,
             shots: int = 20000, seed: int = 1234, method: str = "v1",
             readout: list | None = None) -> Result:
    sim = make_simulator(noise_p, readout)
    prep = prepare(n, kind)
    d = 2 ** n
    if method == "v1":
        # Original method, unchanged: same seed for every setting, sigma added linearly.
        cache: dict[str, dict] = {}
        f, sigma = 0.0, 0.0
        for coef, pauli in TERMS[n]:
            s = setting_for(pauli)
            if s not in cache:
                cache[s] = measure_setting(prep, s, sim, shots, seed)
            e, se = expectation(cache[s], pauli)
            f += coef * e
            sigma += se
        f, sigma = f / d, sigma / d
        seeds = [seed] * len(cache)
    elif method == "v2":
        # One seed per setting; per-shot value of each setting = sum of its terms, so the
        # covariances between terms sharing a setting are kept; settings independent.
        groups: dict[str, list[tuple[int, str]]] = {}
        for coef, pauli in TERMS[n]:
            groups.setdefault(setting_for(pauli), []).append((coef, pauli))
        settings = list(groups)
        counts, seeds = measure_settings(prep, settings, sim, shots, seed)
        cache = dict(zip(settings, counts))
        f, var = 0.0, 0.0
        for s in settings:
            m, v = mean_and_var_of_mean(
                cache[s], lambda b, t=groups[s]: sum(c * parity_sign(b, p) for c, p in t))
            f += m
            var += v
        f, sigma = f / d, math.sqrt(var) / d
    else:
        raise ValueError(method)
    verdict = "ENTANGLED" if f - 3 * sigma > 0.5 else "NOT DEMONSTRATED"
    return Result(label, f, sigma, verdict, method, seeds, cache)


@dataclass
class WitnessResult:
    label: str
    n: int
    value: float      # <W>
    sigma: float
    verdict: str
    x_mean: float     # <X...X>
    p_equal: float    # P(0...0) + P(1...1)
    seeds: list[int] = field(default_factory=list)


def witness(label: str, n: int, kind: str, noise_p: float = 0.0,
            shots: int = 20000, seed: int = 1234, readout: list | None = None) -> WitnessResult:
    """Toth-Guhne two-setting witness: <W> = 2 - <X...X> - 2 P(all n bits equal).
    GENUINELY ENTANGLED iff <W> + 3 sigma < 0."""
    sim = make_simulator(noise_p, readout)
    prep = prepare(n, kind)
    (cx, cz), seeds = measure_settings(prep, ["X" * n, "Z" * n], sim, shots, seed)
    x_mean, x_var = mean_and_var_of_mean(cx, lambda b: parity_sign(b, "X" * n))
    p_eq, p_var = mean_and_var_of_mean(cz, lambda b: 1.0 if len(set(b[:n])) == 1 else 0.0)
    value = 2.0 - x_mean - 2.0 * p_eq
    sigma = math.sqrt(x_var + 4.0 * p_var)
    verdict = "GENUINELY ENTANGLED" if value + 3 * sigma < 0 else "NOT DEMONSTRATED"
    return WitnessResult(label, n, value, sigma, verdict, x_mean, p_eq, seeds)


CASES = [
    ("E1 Bell, ideal", 2, "ghz", 0.0),
    ("E2 GHZ-3, ideal", 3, "ghz", 0.0),
    ("E3 GHZ-3, noise p=0.02", 3, "ghz", 0.02),
    ("E4 GHZ-3, noise p=0.30", 3, "ghz", 0.30),
    ("Control: product state 000", 3, "zeros", 0.0),
    ("Control: product state +++", 3, "plus", 0.0),
]

# (label, n, kind, depolarizing p, readout)
CASES_V2 = [(label, n, kind, p, None) for label, n, kind, p in CASES] + [
    ("Control: mixture of 00 and 11", 2, "mixture", 0.0, None),
    ("Control: mixture of 000 and 111", 3, "mixture", 0.0, None),
    ("R1 GHZ-3, readout error", 3, "ghz", 0.0, READOUT),
]

WITNESS_CASES = (
    [(f"GHZ-{n}, ideal", n, "ghz", 0.0, None) for n in range(3, 9)]
    + [(f"GHZ-{n}, noise p=0.02", n, "ghz", 0.02, None) for n in range(3, 9)]
    + [(f"GHZ-{n}, noise p=0.10", n, "ghz", 0.10, None) for n in range(3, 9)]
    + [("GHZ-8, readout error", 8, "ghz", 0.0, READOUT)]
    + [(f"Control: product 0…0, n={n}", n, "zeros", 0.0, None) for n in (3, 5, 8)]
    + [(f"Control: product +…+, n={n}", n, "plus", 0.0, None) for n in (3, 5, 8)]
    + [(f"Control: mixture 0…0 / 1…1, n={n}", n, "mixture", 0.0, None) for n in (3, 5, 8)]
)


def main() -> None:
    v1 = [
        "20 000 shots per setting, simulator seed 1234 (Qiskit Aer, classical simulation)",
        "",
        "| Case | F | 3σ | Verdict |",
        "|---|---:|---:|---|",
    ]
    for label, n, kind, p in CASES:
        r = fidelity(label, n, kind, p)
        v1.append(f"| {r.label} | {r.fidelity:.4f} | {3 * r.sigma:.4f} | {r.verdict} |")

    v2 = [
        "20 000 shots per setting, base seed 1234, one independent seed per setting "
        "(Qiskit Aer, classical simulation). Exact σ: per-setting sample variance, "
        "settings added in quadrature.",
        "",
        "| Case | F | 3σ | Verdict | Seeds reported by Aer (one per setting) |",
        "|---|---:|---:|---|---|",
    ]
    for label, n, kind, p, ro in CASES_V2:
        r = fidelity(label, n, kind, p, method="v2", readout=ro)
        seeds = ", ".join(str(s) for s in r.seeds)
        v2.append(f"| {r.label} | {r.fidelity:.4f} | {3 * r.sigma:.4f} | {r.verdict} | {seeds} |")

    rows, seed_sets = [], set()
    for label, n, kind, p, ro in WITNESS_CASES:
        w = witness(label, n, kind, p, readout=ro)
        seed_sets.add(", ".join(str(s) for s in w.seeds))
        rows.append(f"| {w.label} | {w.n} | {w.x_mean:.4f} | {w.p_equal:.4f} | "
                    f"{w.value:+.4f} | {3 * w.sigma:.4f} | {w.verdict} |")
    tw = [
        "Two settings (X…X, then Z…Z) for any n, 20 000 shots each, base seed 1234; seeds "
        f"reported by Aer: {' / '.join(sorted(seed_sets))}. "
        "⟨W⟩ = 2 − ⟨X…X⟩ − 2·P(all equal). The full stabilizer expansion would need "
        "2^(n−1)+1 settings (129 for n = 8).",
        "",
        "| Case | n | ⟨X…X⟩ | P(all equal) | ⟨W⟩ | 3σ | Verdict |",
        "|---|---:|---:|---:|---:|---:|---|",
    ] + rows

    out = "\n".join(
        ["## v1: fidelity, same seed for every setting, σ added linearly", ""] + v1
        + ["", "## v2: fidelity, independent settings, exact σ", ""] + v2
        + ["", "## v2: two-setting witness (Tóth & Gühne, PRL 94, 060501, 2005)", ""] + tw
        + ["", "Noise models are textbook models, not a device: depolarizing error p after "
           "every h, sdg and cx; readout error P(1|0) = 0.02, P(0|1) = 0.03 on every qubit."])
    print(out)
    path = Path(__file__).resolve().parent / "RESULTS.md"
    path.write_text("# Results\n\n" + out + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
