"""Tests for p6_mission: the end-to-end gates of Suangxing-1."""
import unittest

from mission_sim import (
    CONFIG, phase_launch_and_raise, phase_power_check,
    phase_thermal_check, phase_radiation_check, phase_operations,
    phase_deorbit, run_mission,
)


class TestPhases(unittest.TestCase):
    def setUp(self):
        self.cfg = dict(CONFIG)

    def test_launch_raise(self):
        r = phase_launch_and_raise(self.cfg)
        # 400 -> 550 km Hohmann ~ 84 m/s (module 02, corrected)
        self.assertAlmostEqual(r["dv_raise_ms"], 84.0, delta=2.0)
        self.assertLess(r["propellant_kg"], 10.0)

    def test_power_gate(self):
        r = phase_power_check(self.cfg)
        # 7 m2 x 300 W/m2 x 0.85 = 1785 W EOL vs ~925 W load
        self.assertTrue(r["ok"])
        self.assertGreater(r["margin_pct"], 15.0)

    def test_thermal_gate(self):
        r = phase_thermal_check(self.cfg)
        self.assertTrue(r["ok"])
        self.assertLessEqual(r["junction_c_derated"], 85.0)

    def test_radiation_gate(self):
        r = phase_radiation_check(self.cfg)
        self.assertTrue(r["cots_ok"])
        self.assertGreater(r["seu_per_day_8gb"], 1000.0)
        self.assertAlmostEqual(r["checkpoint_s"], 3219.0, delta=30.0)

    def test_operations(self):
        r = phase_operations(self.cfg, days=2, tasks_per_day=10)
        self.assertGreater(r["success_rate"], 0.95)
        # downlink capacity must exceed daily output (module 09 rule)
        self.assertGreater(r["daily_downlink_tb"], r["daily_output_tb"])

    def test_deorbit(self):
        r = phase_deorbit(self.cfg)
        self.assertAlmostEqual(r["dv_deorbit_ms"], 99.0, delta=2.0)
        self.assertLess(r["propellant_kg"], 10.0)


class TestFullMission(unittest.TestCase):
    def test_mission_go(self):
        out = run_mission(sim_days=2)
        self.assertTrue(out["mission_go"])

    def test_mission_no_go_if_underpowered(self):
        cfg = dict(CONFIG)
        cfg["solar_area_m2"] = 2.0      # too small -> power gate fails
        out = run_mission(cfg, sim_days=1)
        self.assertFalse(out["mission_go"])
        self.assertFalse(out["power"]["ok"])

    def test_mission_no_go_if_unshielded(self):
        cfg = dict(CONFIG)
        cfg["shield_mm_al"] = 0.5       # too thin -> TID gate fails
        out = run_mission(cfg, sim_days=1)
        self.assertFalse(out["mission_go"])
        self.assertFalse(out["radiation"]["cots_ok"])


if __name__ == "__main__":
    unittest.main()
