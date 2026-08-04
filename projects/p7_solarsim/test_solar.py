"""Tests for p7_solarsim against textbook/JPL reference values."""
import math
import unittest

from kepler import (solve_kepler, period_days, jd_of_ymd, datetime_of_jd,
                    jd_now, orbital_velocity_kms, elements_to_state)
from ephemeris import (planet_state, planet_elements_for_display,
                       moon_state_geo, J2000)
from transfer import (hohmann, required_phase_deg, synodic_days,
                      current_phase_deg, wait_days, transfer_elements,
                      transfer_pos_at, miss_distance_km)


class TestKepler(unittest.TestCase):
    def test_jd_j2000(self):
        self.assertAlmostEqual(jd_of_ymd(2000, 1, 1.5), 2451545.0, places=6)

    def test_jd_roundtrip(self):
        dt = datetime_of_jd(J2000)
        self.assertEqual(dt.year, 2000)
        self.assertEqual(dt.month, 1)
        self.assertEqual(dt.day, 1)

    def test_kepler_solver(self):
        # M=1.0, e=0.5 -> E = 1.49870113... (standard test vector)
        E = solve_kepler(1.0, 0.5)
        self.assertAlmostEqual(E, 1.49870113, places=6)

    def test_kepler_circular(self):
        self.assertAlmostEqual(solve_kepler(2.0, 0.0), 2.0, places=10)

    def test_period_earth(self):
        self.assertAlmostEqual(period_days(1.0), 365.256, delta=0.01)

    def test_vis_viva_earth(self):
        self.assertAlmostEqual(orbital_velocity_kms(1.0, 1.0), 29.78,
                               delta=0.01)


class TestEphemeris(unittest.TestCase):
    def test_earth_j2000_near_perihelion(self):
        # J2000 = Jan 1.5, Earth close to perihelion (Jan ~3)
        p = planet_state("Earth", J2000)[0]
        r = math.sqrt(sum(c * c for c in p))
        self.assertGreater(r, 0.975)
        self.assertLess(r, 0.995)

    def test_mars_distance_bounds(self):
        p = planet_state("Mars", J2000)[0]
        r = math.sqrt(sum(c * c for c in p))
        self.assertGreater(r, 1.38)    # perihelion 1.381
        self.assertLess(r, 1.67)       # aphelion 1.666

    def test_all_planets_periods(self):
        refs = {"Mercury": 87.97, "Venus": 224.70, "Earth": 365.26,
                "Mars": 686.98, "Jupiter": 4332.6, "Saturn": 10759.2,
                "Uranus": 30688.5, "Neptune": 60182.0}
        for name, pref in refs.items():
            a = planet_elements_for_display(name, J2000)["a"]
            self.assertAlmostEqual(period_days(a), pref, delta=pref * 0.002,
                                   msg=name)

    def test_orbit_is_closed_ellipse(self):
        # M=0 and M=360 must give the same point
        el = planet_elements_for_display("Mars", J2000)
        wbar, Om, inc = el["wbar"], el["Om"], el["i"]
        p1, _ = elements_to_state(el["a"], el["e"], inc, Om, wbar - Om, 0.0)
        p2, _ = elements_to_state(el["a"], el["e"], inc, Om, wbar - Om, 360.0)
        for c1, c2 in zip(p1, p2):
            self.assertAlmostEqual(c1, c2, places=8)

    def test_moon_distance(self):
        lon, lat, dist = moon_state_geo(J2000)
        self.assertGreater(dist, 356000.0)   # perigee ~356400
        self.assertLess(dist, 407000.0)      # apogee ~406700
        self.assertGreaterEqual(lat, -7.0)
        self.assertLessEqual(lat, 7.0)

    def test_realtime_sync(self):
        # jd_now must track wall clock within 2 seconds
        import time
        j1 = jd_now()
        time.sleep(0.2)
        j2 = jd_now()
        self.assertAlmostEqual((j2 - j1) * 86400.0, 0.2, delta=0.05)


class TestTransfer(unittest.TestCase):
    def test_hohmann_earth_mars(self):
        dv1, dv2, tof, a_t = hohmann(1.0, 1.5237)
        self.assertAlmostEqual(dv1, 2.95, delta=0.05)
        self.assertAlmostEqual(dv2, 2.66, delta=0.05)
        self.assertAlmostEqual(tof, 258.9, delta=1.0)
        self.assertAlmostEqual(a_t, 1.26185, delta=0.001)

    def test_phase_angle_earth_mars(self):
        # classic: Mars must lead Earth by ~44 deg at departure
        self.assertAlmostEqual(required_phase_deg(1.0, 1.5237), 44.3,
                               delta=1.0)

    def test_synodic_earth_mars(self):
        self.assertAlmostEqual(synodic_days(1.0, 1.5237), 779.9, delta=2.0)

    def test_wait_is_bounded(self):
        jd = J2000
        p1 = planet_state("Earth", jd)[0]
        p2 = planet_state("Mars", jd)[0]
        ph = current_phase_deg(p1, p2)
        wt = wait_days(1.0, 1.5237, ph)
        self.assertGreaterEqual(wt, 0.0)
        self.assertLess(wt, synodic_days(1.0, 1.5237))

    def test_transfer_arc_endpoints(self):
        # arc must start at r1 and end at r2
        a_t, e_t, wbar, M0, peri = transfer_elements(1.0, 1.5237, 40.0)
        p_start = transfer_pos_at(a_t, e_t, wbar, M0, J2000, J2000)
        dv1, dv2, tof, _ = hohmann(1.0, 1.5237)
        p_end = transfer_pos_at(a_t, e_t, wbar, M0, J2000, J2000 + tof)
        r_start = math.sqrt(sum(c * c for c in p_start))
        r_end = math.sqrt(sum(c * c for c in p_end))
        self.assertAlmostEqual(r_start, 1.0, delta=0.001)
        self.assertAlmostEqual(r_end, 1.5237, delta=0.001)

    def test_perfect_phase_zero_miss(self):
        # if phase is exactly right, miss distance ~ 0 (circular approx)
        jd = J2000
        a1, a2 = 1.0, 1.5237
        req = required_phase_deg(a1, a2)
        # construct synthetic geometry: dep at lon 0, arr at lon req
        lon_dep = 0.0
        a_t, e_t, wbar, M0, peri = transfer_elements(a1, a2, lon_dep)
        _, _, tof, _ = hohmann(a1, a2)
        sc = transfer_pos_at(a_t, e_t, wbar, M0, jd, jd + tof)
        # target on circle r2 at departure lon + 180 (Hohmann geometry)
        ang = math.radians((lon_dep + 180.0) % 360.0)
        tgt = (a2 * math.cos(ang), a2 * math.sin(ang), 0.0)
        miss = miss_distance_km(sc, tgt)
        self.assertLess(miss, 1e5)   # < 100k km in ideal geometry


if __name__ == "__main__":
    unittest.main()
