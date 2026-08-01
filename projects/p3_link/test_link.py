"""Tests for p3_link, cross-checking module 07 worked examples."""
import unittest

from link_budget import (
    db, fspl_db, antenna_gain_db, rf_link_budget,
    optical_beam_divergence_urad, optical_antenna_gain_db,
    optical_link_budget, point_ahead_urad, cloud_availability,
    daily_downlink_tb,
)


class TestRF(unittest.TestCase):
    def test_fspl_xband(self):
        # module 07 (corrected): X-band 8.4 GHz, 800 km -> ~169 dB
        l = fspl_db(800e3, 8.4e9)
        self.assertAlmostEqual(l, 169.0, delta=0.5)

    def test_xband_downlink_budget(self):
        # module 07 sec 1.4: 10 W, 8 dBi, 11 m station G/T=32 dB/K,
        # 300 Mbps 16APSK -> margin ~23 dB
        r = rf_link_budget(
            p_tx_w=10.0, g_tx_db=8.0, g_t_dbk=32.0,
            distance_m=800e3, freq_hz=8.4e9,
            data_rate_bps=300e6, modcod="16APSK_3/4",
            misc_loss_db=3.5,
        )
        self.assertAlmostEqual(r["ebn0_db"], 21.3, delta=1.0)
        self.assertGreater(r["margin_db"], 10.0)

    def test_small_station_needs_robust_modcod(self):
        # 3 m class station G/T ~ 22 dB/K: 16APSK margin < 3 dB rule
        # -> drop to 8PSK_2/3 for a healthy margin
        r16 = rf_link_budget(
            p_tx_w=10.0, g_tx_db=8.0, g_t_dbk=22.0,
            distance_m=800e3, freq_hz=8.4e9,
            data_rate_bps=300e6, modcod="16APSK_3/4",
            misc_loss_db=3.5,
        )
        self.assertLess(r16["margin_db"], 3.0)
        r8 = rf_link_budget(
            p_tx_w=10.0, g_tx_db=8.0, g_t_dbk=22.0,
            distance_m=800e3, freq_hz=8.4e9,
            data_rate_bps=300e6, modcod="8PSK_2/3",
            misc_loss_db=3.5,
        )
        self.assertGreater(r8["margin_db"], 3.0)

    def test_antenna_gain(self):
        # 11 m dish at 8.4 GHz ~ 57-58 dBi
        g = antenna_gain_db(11.0, 8.4e9)
        self.assertAlmostEqual(g, 57.5, delta=1.0)


class TestOptical(unittest.TestCase):
    def test_divergence(self):
        # module 07: 1550 nm, 10 cm aperture -> ~10 urad full-angle scale
        th = optical_beam_divergence_urad(1550e-9, 0.10)
        self.assertAlmostEqual(th, 9.9, delta=1.0)

    def test_optical_gain(self):
        # module 07: 10 cm at 1550 nm -> ~106 dB
        g = optical_antenna_gain_db(0.10, 1550e-9)
        self.assertAlmostEqual(g, 106.0, delta=0.5)

    def test_oisl_budget(self):
        # module 07 sec 2.2: 1 W, 10 cm apertures, 4500 km -> ~-32 dBm
        r = optical_link_budget(1.0, 0.10, 0.10, 1550e-9, 4500e3)
        self.assertAlmostEqual(r["p_rx_dbm"], -32.0, delta=3.0)
        self.assertGreater(r["p_rx_uw"], 0.2)

    def test_point_ahead(self):
        # module 07: v_rel 7 km/s -> ~23 urad
        pa = point_ahead_urad(7000.0, 4500e3)
        self.assertAlmostEqual(pa, 23.3, delta=0.5)

    def test_point_ahead_distance_independent(self):
        # elegant result: independent of distance
        pa1 = point_ahead_urad(7000.0, 1000e3)
        pa2 = point_ahead_urad(7000.0, 5000e3)
        self.assertAlmostEqual(pa1, pa2, places=9)


class TestAvailability(unittest.TestCase):
    def test_single_site(self):
        self.assertAlmostEqual(cloud_availability(1, 0.35), 0.35)

    def test_six_sites(self):
        # module 07: 6-10 sites -> >95%
        self.assertGreater(cloud_availability(6, 0.35), 0.92)
        self.assertGreater(cloud_availability(10, 0.35), 0.98)

    def test_daily_volume(self):
        # module 09: 1 Gbps x 10 passes x 600 s = 0.75 TB/day
        v = daily_downlink_tb(1e9, 10, 600.0)
        self.assertAlmostEqual(v, 0.75, delta=0.01)


if __name__ == "__main__":
    unittest.main()
