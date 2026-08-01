"""Tests for p4_radiation, cross-checking module 04/06 worked examples."""
import math
import unittest

from radiation_sim import (
    weibull_sigma, seu_rate_per_bit_day, memory_upsets_per_day,
    tid_shielding, checkpoint_interval_young, checkpoint_overhead,
    expected_lost_work, r_series, r_parallel, r_k_of_n, availability,
    derating_junction_limit,
)


class TestWeibull(unittest.TestCase):
    def test_below_threshold_zero(self):
        self.assertEqual(weibull_sigma(1.0, 1e-7, 2.0, 20.0, 1.5), 0.0)

    def test_saturates(self):
        s = weibull_sigma(100.0, 1e-7, 2.0, 20.0, 1.5)
        self.assertAlmostEqual(s / 1e-7, 1.0, delta=0.02)

    def test_midpoint_rise(self):
        # at LET = L0 + W the curve is at 1-exp(-1) ~ 63% of saturation
        s = weibull_sigma(22.0, 1e-7, 2.0, 20.0, 1.0)
        self.assertAlmostEqual(s / 1e-7, 1.0 - math.exp(-1.0), delta=0.01)


class TestRates(unittest.TestCase):
    def test_leo_sram_rate(self):
        # module 06 sec 2.2: sigma_sat=1e-7, flux(LET>2)~1e-4
        # -> ~1e-11 upsets/(bit s) scale -> 1 GB ~ thousands/day
        r = seu_rate_per_bit_day(1e-7, 2.0, 20.0, 1.5, 1e-4)
        self.assertAlmostEqual(r, 0.5 * 1e-11 * 86400.0, delta=1e-6)
        per_day = memory_upsets_per_day(r, 1e9)   # 1 GB
        self.assertGreater(per_day, 1000.0)
        self.assertLess(per_day, 10000.0)


class TestShielding(unittest.TestCase):
    def test_3mm(self):
        # module 01/06: surface 100 krad class environment -> 3 mm cuts
        # to ~1/3 with t0=3 mm
        d = tid_shielding(100.0, 3.0)
        self.assertAlmostEqual(d, 100.0 / math.e, delta=0.5)

    def test_10mm(self):
        d = tid_shielding(100.0, 10.0)
        self.assertAlmostEqual(d, 100.0 * math.exp(-10.0 / 3.0), delta=0.5)


class TestCheckpoint(unittest.TestCase):
    def test_young_formula(self):
        # module 04: delta=60 s, M=24 h -> T_opt ~ 3200 s
        t = checkpoint_interval_young(60.0, 86400.0)
        self.assertAlmostEqual(t, 3219.0, delta=20.0)

    def test_overhead_reasonable(self):
        t = checkpoint_interval_young(60.0, 86400.0)
        self.assertLess(checkpoint_overhead(60.0, t), 0.02)

    def test_lost_work(self):
        t = checkpoint_interval_young(60.0, 86400.0)
        self.assertAlmostEqual(expected_lost_work(t, 86400.0), t / 2.0)


class TestReliability(unittest.TestCase):
    def test_series(self):
        # module 06: ten 99% units in series -> 90.4%
        self.assertAlmostEqual(r_series([0.99] * 10), 0.904, delta=0.001)

    def test_parallel(self):
        # module 06: two 90% in parallel -> 99%
        self.assertAlmostEqual(r_parallel([0.9, 0.9]), 0.99, delta=1e-9)

    def test_gpu_pair(self):
        # module 06 example: two GPU modules R=0.85 -> 0.9775
        self.assertAlmostEqual(r_parallel([0.85, 0.85]), 0.9775, delta=1e-9)

    def test_tmr(self):
        # 2oo3 with R=0.9 -> 0.972
        self.assertAlmostEqual(r_k_of_n(2, 3, 0.9), 0.972, delta=1e-9)

    def test_availability(self):
        self.assertAlmostEqual(availability(1000.0, 10.0), 0.990, delta=0.001)

    def test_derating(self):
        self.assertEqual(derating_junction_limit(105.0), 85.0)


if __name__ == "__main__":
    unittest.main()