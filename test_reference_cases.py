"""Reference cases with known answers. The product states are blank controls:
they must never be declared entangled."""
import unittest

from ghz_witness import fidelity


class ReferenceCases(unittest.TestCase):
    def test_bell_ideal(self):
        r = fidelity("bell", 2, "ghz", shots=4000)
        self.assertGreaterEqual(r.fidelity, 0.98)
        self.assertEqual(r.verdict, "ENTANGLED")

    def test_ghz_ideal(self):
        r = fidelity("ghz", 3, "ghz", shots=4000)
        self.assertGreaterEqual(r.fidelity, 0.98)
        self.assertEqual(r.verdict, "ENTANGLED")

    def test_control_product_000(self):
        r = fidelity("000", 3, "zeros", shots=4000)
        self.assertLessEqual(abs(r.fidelity - 0.5), 3 * r.sigma + 1e-9)
        self.assertEqual(r.verdict, "NOT DEMONSTRATED")

    def test_control_product_plus(self):
        r = fidelity("+++", 3, "plus", shots=4000)
        self.assertLessEqual(abs(r.fidelity - 0.25), 3 * r.sigma + 1e-9)
        self.assertEqual(r.verdict, "NOT DEMONSTRATED")


if __name__ == "__main__":
    unittest.main()
