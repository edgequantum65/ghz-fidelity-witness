"""Entanglement proof by measurement: Bell / GHZ fidelity from Pauli settings.

Seeing only "000" and "111" in the computational basis does NOT prove entanglement:
a classical 50/50 mixture of |000> and |111> gives the same counts. This tool also
measures the X/Y correlations and estimates the fidelity F with the ideal state:

  |Phi+><Phi+| = (II + XX - YY + ZZ) / 4
  |GHZ><GHZ|   = (III + ZZI + IZZ + ZIZ + XXX - XYY - YXY - YYX) / 8

F > 1/2 certifies entanglement (genuine 3-party entanglement for GHZ-3).
"""
from __future__ import annotations

import math
from dataclasses import dataclass

from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

# (coefficient, Pauli string), qubit 0 is the leftmost letter
TERMS = {
    2: [(1, "II"), (1, "XX"), (-1, "YY"), (1, "ZZ")],
    3: [(1, "III"), (1, "ZZI"), (1, "IZZ"), (1, "ZIZ"),
        (1, "XXX"), (-1, "XYY"), (-1, "YXY"), (-1, "YYX")],
}


def prepare(n: int, kind: str) -> QuantumCircuit:
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


def measure_setting(prep: QuantumCircuit, setting: str, sim, shots: int, seed: int) -> dict:
    qc = prep.copy()
    for q, basis in enumerate(setting):
        if basis == "X":
            qc.h(q)
        elif basis == "Y":
            qc.sdg(q)
            qc.h(q)
    qc.measure_all()
    job = sim.run(transpile(qc, sim, optimization_level=0), shots=shots, seed_simulator=seed)
    return job.result().get_counts()


def expectation(counts: dict, pauli: str) -> tuple[float, float]:
    """<P> and its shot-noise standard error. Qiskit bitstrings are little-endian."""
    shots = sum(counts.values())
    support = [q for q, p in enumerate(pauli) if p != "I"]
    if not support:
        return 1.0, 0.0
    total = 0
    for bits, c in counts.items():
        b = bits.replace(" ", "")[::-1]
        parity = sum(int(b[q]) for q in support) % 2
        total += c * (1 if parity == 0 else -1)
    e = total / shots
    return e, math.sqrt(max(0.0, 1.0 - e * e) / shots)


@dataclass
class Result:
    label: str
    fidelity: float
    sigma: float
    verdict: str


def fidelity(label: str, n: int, kind: str, noise_p: float = 0.0,
             shots: int = 20000, seed: int = 1234) -> Result:
    if noise_p > 0:
        nm = NoiseModel()
        nm.add_all_qubit_quantum_error(depolarizing_error(noise_p, 1), ["h", "sdg"])
        nm.add_all_qubit_quantum_error(depolarizing_error(noise_p, 2), ["cx"])
        sim = AerSimulator(noise_model=nm)
    else:
        sim = AerSimulator()
    prep = prepare(n, kind)
    cache: dict[str, dict] = {}
    f, sigma = 0.0, 0.0
    for coef, pauli in TERMS[n]:
        s = setting_for(pauli)
        if s not in cache:
            cache[s] = measure_setting(prep, s, sim, shots, seed)
        e, se = expectation(cache[s], pauli)
        f += coef * e
        sigma += se
    d = 2 ** n
    f, sigma = f / d, sigma / d
    verdict = "ENTANGLED" if f - 3 * sigma > 0.5 else "NOT DEMONSTRATED"
    return Result(label, f, sigma, verdict)


CASES = [
    ("E1 Bell, ideal", 2, "ghz", 0.0),
    ("E2 GHZ-3, ideal", 3, "ghz", 0.0),
    ("E3 GHZ-3, noise p=0.02", 3, "ghz", 0.02),
    ("E4 GHZ-3, noise p=0.30", 3, "ghz", 0.30),
    ("Control: product state 000", 3, "zeros", 0.0),
    ("Control: product state +++", 3, "plus", 0.0),
]


def main() -> None:
    lines = [
        "20 000 shots per setting, simulator seed 1234 (Qiskit Aer, classical simulation)",
        "",
        "| Case | F | 3σ | Verdict |",
        "|---|---:|---:|---|",
    ]
    for label, n, kind, p in CASES:
        r = fidelity(label, n, kind, p)
        lines.append(f"| {r.label} | {r.fidelity:.4f} | {3 * r.sigma:.4f} | {r.verdict} |")
    out = "\n".join(lines)
    print(out)
    with open("RESULTS.md", "w", encoding="utf-8") as f:
        f.write("# Results\n\n" + out + "\n")


if __name__ == "__main__":
    main()
