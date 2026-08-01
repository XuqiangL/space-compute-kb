"""Tests for p5_scheduler, cross-checking module 01/09 quantitative claims."""
import unittest

from scheduler_sim import (
    ORBIT_PERIOD_MIN, Scheduler, Task, make_constellation,
    saa_windows, ground_windows, in_any_window,
)


class TestWindows(unittest.TestCase):
    def test_saa_count_and_duration(self):
        # module 01: 5-7 SAA crossings/day, 5-15 min each
        w = saa_windows()
        self.assertEqual(len(w), 6)
        for a, b in w:
            self.assertAlmostEqual(b - a, 10.0)

    def test_saa_daily_exposure(self):
        # module 01: 40-80 min/day total
        total = sum(b - a for a, b in saa_windows())
        self.assertGreaterEqual(total, 40.0)
        self.assertLessEqual(total, 80.0)

    def test_ground_windows(self):
        # 3 stations x 4 passes = 12 contacts/day, each 10 min
        w = ground_windows(3)
        self.assertEqual(len(w), 12)

    def test_window_membership(self):
        w = [(100.0, 110.0)]
        self.assertTrue(in_any_window(105.0, w))
        self.assertFalse(in_any_window(115.0, w))


class TestScheduling(unittest.TestCase):
    def setUp(self):
        self.sats = make_constellation(3)
        self.sched = Scheduler(self.sats)

    def test_task_assigned(self):
        t = Task("job1", tops_needed=5000.0, data_in_gb=10.0,
                 data_out_gb=1.0, deadline_min=600.0)
        sat = self.sched.assign(t, 0.0)
        self.assertIsNotNone(sat)
        self.assertEqual(t.assigned, sat.name)

    def test_thermal_guard(self):
        # hot satellites must not receive new tasks (module 09 rule 3)
        for s in self.sats[:2]:
            s.temp_c = 85.0
        t = Task("hot", 1000.0, 1.0, 1.0, 300.0)
        sat = self.sched.assign(t, 0.0)
        self.assertEqual(sat.name, "SX-3")

    def test_soc_guard(self):
        for s in self.sats[:2]:
            s.battery_wh = 1000.0    # SOC ~ 17%
        t = Task("lowpower", 1000.0, 1.0, 1.0, 300.0)
        sat = self.sched.assign(t, 0.0)
        self.assertEqual(sat.name, "SX-3")

    def test_saa_blocks_execution(self):
        # a task starting right before an SAA window must finish after it
        sat = self.sats[0]
        t = Task("saa-victim", tops_needed=500.0, data_in_gb=0.1,
                 data_out_gb=0.1, deadline_min=1000.0)
        start = self.sched.saa[0][0] - 2.0    # 2 min before SAA entry
        end = self.sched.run_task(sat, t, start)
        self.assertGreaterEqual(end, self.sched.saa[0][1])

    def test_downlink_capacity(self):
        # 12 contacts x 10 min x 1 Gbps = 0.9 TB/day (module 09 scale)
        vol = self.sched.downlink_volume_tb(0.0, 1440.0)
        self.assertAlmostEqual(vol, 0.85, delta=0.1)

    def test_deadline_met(self):
        t = Task("urgent", tops_needed=1000.0, data_in_gb=1.0,
                 data_out_gb=0.5, deadline_min=300.0)
        sat = self.sched.assign(t, 0.0)
        end = self.sched.run_task(sat, t, 0.0)
        self.assertLessEqual(end, 300.0)


if __name__ == "__main__":
    unittest.main()
