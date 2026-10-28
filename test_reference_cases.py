"""Reference cases with known answers. The product states and the classical mixture
are blank controls: they must never be declared entangled."""
import unittest
from functools import reduce

import numpy as np
from qiskit.quantum_info import DensityMatrix, partial_trace

from ghz_witness import READOUT, fidelity, prepare, witness

SHOTS = 4000


class ReferenceCases(unittest.TestCase):
    """v1 method (same seed for every setting, sigma added linearly)."""

    def test_bell_ideal(self):
        r = fidelity("bell", 2, "ghz", shots=SHOTS)
        self.assertGreaterEqual(r.fidelity, 0.98)
        self.assertEqual(r.verdict, "ENTANGLED")

    def test_ghz_ideal(self):
        r = fidelity("ghz", 3, "ghz", shots=SHOTS)
        self.assertGreaterEqual(r.fidelity, 0.98)
        self.assertEqual(r.verdict, "ENTANGLED")

    def test_ghz_noise_002(self):  # E3; F ~ 0.92, margin far above 3 sigma at 4000 shots
        r = fidelity("E3", 3, "ghz", 0.02, shots=SHOTS)
        self.assertGreater(r.fidelity - 3 * r.sigma, 0.85)
        self.assertEqual(r.verdict, "ENTANGLED")

    def test_ghz_noise_030(self):  # E4; F ~ 0.36, far below 0.5
        r = fidelity("E4", 3, "ghz", 0.30, shots=SHOTS)
        self.assertLess(r.fidelity + 3 * r.sigma, 0.45)
        self.assertEqual(r.verdict, "NOT DEMONSTRATED")

    def test_control_product_000(self):
        r = fidelity("000", 3, "zeros", shots=SHOTS)
        self.assertLessEqual(abs(r.fidelity - 0.5), 3 * r.sigma + 1e-9)
        self.assertEqual(r.verdict, "NOT DEMONSTRATED")

    def test_control_product_plus(self):
        r = fidelity("+++", 3, "plus", shots=SHOTS)
        self.assertLessEqual(abs(r.fidelity - 0.25), 3 * r.sigma + 1e-9)
        self.assertEqual(r.verdict, "NOT DEMONSTRATED")

    def test_control_mixture(self):
        for n in (2, 3):
            r = fidelity("mix", n, "mixture", shots=SHOTS)
            self.assertLessEqual(abs(r.fidelity - 0.5), 3 * r.sigma + 1e-9)
            self.assertEqual(r.verdict, "NOT DEMONSTRATED")

    def test_v1_settings_not_independent(self):
        """Documents the v1 flaw fixed in v2: same seed, identical counts."""
        c = fidelity("000", 3, "zeros", shots=SHOTS).counts
        self.assertTrue(c["XYY"] == c["YXY"] == c["YYX"])


class FidelityV2(unittest.TestCase):
    """v2 method: one seed per setting, exact sigma."""

    def test_ideal(self):
        for n in (2, 3):
            r = fidelity("ghz", n, "ghz", shots=SHOTS, method="v2")
            self.assertAlmostEqual(r.fidelity, 1.0, places=12)
            self.assertAlmostEqual(r.sigma, 0.0, places=12)
            self.assertEqual(r.verdict, "ENTANGLED")

    def test_noise(self):
        r = fidelity("E3", 3, "ghz", 0.02, shots=SHOTS, method="v2")
        self.assertGreater(r.fidelity - 3 * r.sigma, 0.85)
        self.assertEqual(r.verdict, "ENTANGLED")
        r = fidelity("E4", 3, "ghz", 0.30, shots=SHOTS, method="v2")
        self.assertLess(r.fidelity + 3 * r.sigma, 0.45)
        self.assertEqual(r.verdict, "NOT DEMONSTRATED")

    def test_readout(self):  # hand model: F = 0.8922
        r = fidelity("R1", 3, "ghz", shots=SHOTS, method="v2", readout=READOUT)
        self.assertLess(abs(r.fidelity - 0.8922), 0.02)
        self.assertEqual(r.verdict, "ENTANGLED")

    def test_controls(self):
        for n, kind, target in [(3, "zeros", 0.5), (3, "plus", 0.25),
                                (2, "mixture", 0.5), (3, "mixture", 0.5)]:
            r = fidelity(kind, n, kind, shots=SHOTS, method="v2")
            self.assertLessEqual(abs(r.fidelity - target), 3 * r.sigma + 1e-9, (n, kind))
            self.assertEqual(r.verdict, "NOT DEMONSTRATED", (n, kind))

    def test_settings_independent(self):
        r = fidelity("000", 3, "zeros", shots=SHOTS, method="v2")
        self.assertEqual(len(set(r.seeds)), 5)
        c = r.counts
        self.assertFalse(c["XYY"] == c["YXY"] == c["YYX"])

    def test_exact_sigma_not_larger(self):
        for n, kind in [(3, "zeros"), (3, "plus"), (3, "mixture")]:
            r1 = fidelity(kind, n, kind, shots=SHOTS)
            r2 = fidelity(kind, n, kind, shots=SHOTS, method="v2")
            self.assertLess(r2.sigma, r1.sigma, kind)

    def test_reproducible(self):
        a = fidelity("E3", 3, "ghz", 0.02, shots=SHOTS, method="v2")
        b = fidelity("E3", 3, "ghz", 0.02, shots=SHOTS, method="v2")
        self.assertEqual((a.fidelity, a.sigma, a.counts), (b.fidelity, b.sigma, b.counts))


def exact_witness(n: int, kind: str) -> tuple[float, float]:
    """<W> from the operator definition, and from 2 - <X..X> - 2 P(all equal),
    both on the exact density matrix of the n system qubits."""
    rho = DensityMatrix(prepare(n, kind))
    if kind == "mixture":
        rho = partial_trace(rho, [n])
    m = rho.data
    eye, x, z = np.eye(2), np.array([[0, 1], [1, 0]]), np.diag([1, -1])

    def op(single):  # qiskit order: qubit 0 is the rightmost tensor factor
        return reduce(np.kron, [single.get(q, eye) for q in reversed(range(n))])

    d = 2 ** n
    xs = op({q: x for q in range(n)})
    prod = np.eye(d)
    for k in range(1, n):
        prod = prod @ (op({k - 1: z, k: z}) + np.eye(d)) / 2
    w = 3 * np.eye(d) - 2 * ((xs + np.eye(d)) / 2 + prod)
    from_operator = float(np.real(np.trace(w @ m)))
    from_formula = float(np.real(2 - np.trace(xs @ m) - 2 * (m[0, 0] + m[-1, -1])))
    return from_operator, from_formula


class Witness(unittest.TestCase):
    """Toth-Guhne two-setting witness."""

    def test_algebra_exact(self):
        for n in range(2, 7):
            for kind, target in [("ghz", -1.0), ("zeros", 0.0), ("mixture", 0.0),
                                 ("plus", 1 - 2 ** (2 - n))]:
                a, b = exact_witness(n, kind)
                self.assertAlmostEqual(a, target, places=10, msg=(n, kind))
                self.assertAlmostEqual(b, target, places=10, msg=(n, kind))

    def test_ideal_ghz(self):
        for n in (3, 5, 8):
            w = witness("ghz", n, "ghz", shots=SHOTS)
            self.assertAlmostEqual(w.value, -1.0, places=12)
            self.assertAlmostEqual(w.sigma, 0.0, places=12)
            self.assertEqual(w.verdict, "GENUINELY ENTANGLED")

    def test_controls(self):
        for n in (3, 5, 8):
            for kind, target in [("zeros", 0.0), ("mixture", 0.0), ("plus", 1 - 2 ** (2 - n))]:
                w = witness(kind, n, kind, shots=SHOTS)
                self.assertLessEqual(abs(w.value - target), 3 * w.sigma + 1e-9, (n, kind))
                self.assertEqual(w.verdict, "NOT DEMONSTRATED", (n, kind))

    def test_noise_and_readout(self):
        w = witness("p002", 8, "ghz", 0.02, shots=SHOTS)  # model -0.53
        self.assertLess(w.value + 3 * w.sigma, -0.4)
        self.assertEqual(w.verdict, "GENUINELY ENTANGLED")
        w = witness("p010", 8, "ghz", 0.10, shots=SHOTS)  # model +0.62
        self.assertGreater(w.value - 3 * w.sigma, 0.5)
        self.assertEqual(w.verdict, "NOT DEMONSTRATED")
        w = witness("ro", 8, "ghz", shots=SHOTS, readout=READOUT)  # model -0.30
        self.assertLess(w.value + 3 * w.sigma, -0.2)
        self.assertEqual(w.verdict, "GENUINELY ENTANGLED")


if __name__ == "__main__":
    unittest.main()
