"""Tests for p1_orbit against the worked examples in module 02.

Every assertion here cross-checks a number that appears in the KB text;
if a test fails, either the code or the book chapter is wrong.
"""
import math
import unittest

from orbit_sim import (
    MU, R_EARTH, orbital_period, circular_velocity, vis_viva,
    hohmann_transfer, plane_change_dv, j2_nodal_regression,
    sso_inclination, drag_decay_per_day, lifetime_years,
    phasing_drift_rate_deg_per_day, propellant_mass, deorbit_dv,
)


class TestBasicOrbit(unittest.TestCase):
    def test_period_550km(self):
        # module 02 example: 550 km -> ~95.5 min
        a = R_EARTH + 550.0
        t_min = orbital_period(a) / 60.0
        self.assertAlmostEqual(t_min, 95.5, delta=0.6)

    def test_circular_velocity_550km(self):
        v = circular_velocity(R_EARTH + 550.0)
        self.assertAlmostEqual(v, 7.59, delta=0.02)

    def test_geo_period(self):
        # GEO semi-major axis ~42164 km -> sidereal day
        t_h = orbital_period(42164.0) / 3600.0
        self.assertAlmostEqual(t_h, 23.93, delta=0.05)

    def test_vis_viva_leo(self):
        a = R_EARTH + 550.0
        self.assertAlmostEqual(vis_viva(a, a), circular_velocity(a), places=9)


class TestManeuvers(unittest.TestCase):
    def test_hohmann_400_to_550(self):
        # module 02 example (corrected): total ~84 m/s
        dv1, dv2, t_t = hohmann_transfer(R_EARTH + 400.0, R_EARTH + 550.0)
        self.assertAlmostEqual((dv1 + dv2) * 1000.0, 83.5, delta=2.0)
        self.assertAlmostEqual(t_t / 60.0, 47.0, delta=2.0)  # ~half period

    def test_plane_change_expensive(self):
        # 1 deg at 7.59 km/s ~ 132 m/s (module 02)
        dv = plane_change_dv(7.59, 1.0)
        self.assertAlmostEqual(dv * 1000.0, 132.0, delta=2.0)

    def test_deorbit_dv(self):
        # 550 km -> 200 km perigee ~ 99 m/s (module 02 section 6.3, corrected)
        dv = deorbit_dv(550.0, 200.0)
        self.assertAlmostEqual(dv, 99.0, delta=2.0)

    def test_propellant_fraction(self):
        # 300 m/s, Isp 220 s -> ~13% of mass (module 02 section 2.3)
        m_prop = propellant_mass(300.0, 150.0, 220.0)
        self.assertAlmostEqual(m_prop / 150.0, 0.13, delta=0.01)


class TestSSO(unittest.TestCase):
    def test_sso_inclination_550(self):
        # module 02 derivation: i ~ 97.55 deg at 550 km
        i = sso_inclination(R_EARTH + 550.0)
        self.assertAlmostEqual(i, 97.55, delta=0.15)

    def test_sso_regression_matches_sun(self):
        a = R_EARTH + 550.0
        i = sso_inclination(a)
        rate = j2_nodal_regression(a, 0.0, i)  # rad/s
        deg_per_day = math.degrees(rate) * 86400.0
        self.assertAlmostEqual(deg_per_day, 360.0 / 365.25, delta=0.002)

    def test_sso_impossible_too_high(self):
        with self.assertRaises(ValueError):
            sso_inclination(R_EARTH + 6000.0)


class TestDrag(unittest.TestCase):
    def test_decay_550km(self):
        # module 02 example (corrected): B=45 -> ~ -5 m/day at rho=5e-14
        d = drag_decay_per_day(R_EARTH + 550.0, 150.0, 1.5, 5e-14)
        self.assertAlmostEqual(d * 1000.0, -5.0, delta=1.0)

    def test_lifetime_ordering(self):
        # lower orbit must decay faster
        lt_low = lifetime_years(400.0, 150.0, 1.5, 1e-12)
        lt_high = lifetime_years(550.0, 150.0, 1.5, 5e-14)
        self.assertLess(lt_low, lt_high)

    def test_phasing_drift(self):
        # module 02 example: da=20 km at 6921 km -> ~23.5 deg/day
        d = phasing_drift_rate_deg_per_day(R_EARTH + 550.0, 20.0)
        self.assertAlmostEqual(d, 23.5, delta=1.0)


if __name__ == "__main__":
    unittest.main()
