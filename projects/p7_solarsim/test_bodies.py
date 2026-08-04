"""Tests for extended bodies, conics, maneuvers, Lagrange points."""
import math
import unittest

from kepler import jd_of_ymd, period_days, elements_to_state
from ephemeris import planet_state, J2000
from bodies import (MOONS, ASTEROIDS, KBOS, COMETS, STARS, soi_au,
                    moon_pos, small_body_pos, halley_pos, star_direction,
                    belt_asteroids, AXIAL_TILT, pole_direction,
                    earth_orbit_pos, ISS, CALCSAT)
from conics import (state_to_elements, velocity_on_elements,
                    apply_prograde_dv, lagrange_points)


class TestMoons(unittest.TestCase):
    def test_laplace_resonance(self):
        # Io:Europa:Ganymede ~ 1:2:4 (Laplace resonance)
        io = MOONS["Jupiter"]["Io"][1]
        eu = MOONS["Jupiter"]["Europa"][1]
        ga = MOONS["Jupiter"]["Ganymede"][1]
        self.assertAlmostEqual(eu / io, 2.007, delta=0.01)
        self.assertAlmostEqual(ga / eu, 2.015, delta=0.01)

    def test_triton_retrograde(self):
        # Triton inclination > 90 deg = retrograde
        self.assertGreater(MOONS["Neptune"]["Triton"][2], 90.0)
        self.assertAlmostEqual(MOONS["Neptune"]["Triton"][1], 5.877,
                               delta=0.01)

    def test_moon_keeps_distance(self):
        # moon-planet distance must equal its semi-major axis (circular)
        pj = planet_state("Jupiter", J2000)[0]
        a_km, p_d, i_d, n_d, ph, _ = MOONS["Jupiter"]["Ganymede"]
        m = moon_pos(pj, a_km, p_d, i_d, n_d, ph, J2000)
        d = math.sqrt(sum((m[k] - pj[k]) ** 2 for k in range(3)))
        self.assertAlmostEqual(d * 149597870.7, a_km, delta=a_km * 0.01)

    def test_galilean_coverage(self):
        self.assertEqual(len(MOONS["Jupiter"]), 4)
        self.assertIn("Titan", MOONS["Saturn"])
        self.assertIn("Charon", MOONS["Pluto"])


class TestSmallBodies(unittest.TestCase):
    def test_ceres_period(self):
        a = ASTEROIDS["Ceres"][0]
        self.assertAlmostEqual(period_days(a) / 365.256, 4.60, delta=0.02)

    def test_halley(self):
        c = COMETS["Halley"]
        self.assertAlmostEqual(period_days(c["a"]) / 365.256, 75.3, delta=0.5)
        # perihelion Feb 1986: position near perihelion distance 0.586 AU
        p = halley_pos(jd_of_ymd(1986, 2, 9.0))
        r = math.sqrt(sum(x * x for x in p))
        self.assertAlmostEqual(r, 0.586, delta=0.03)
        # next return July 2061
        p2 = halley_pos(jd_of_ymd(2061, 7, 28.0))
        r2 = math.sqrt(sum(x * x for x in p2))
        self.assertAlmostEqual(r2, 0.586, delta=0.05)

    def test_sedna_extreme(self):
        a, e = KBOS["Sedna"][0], KBOS["Sedna"][1]
        q, Q = a * (1 - e), a * (1 + e)
        self.assertAlmostEqual(q, 80.0, delta=5.0)      # perihelion ~80 AU
        self.assertGreater(Q, 900.0)                    # aphelion ~930 AU

    def test_kirkwood_gaps(self):
        belt = belt_asteroids(1500)
        for a, *_ in belt:
            for g, w in ((2.50, 0.05), (2.82, 0.04), (2.95, 0.03),
                         (3.27, 0.05)):
                self.assertFalse(abs(a - g) < w, f"asteroid in gap {a}")
        self.assertEqual(len(belt), 1500)
        for a, *_ in belt:
            self.assertGreaterEqual(a, 2.06)
            self.assertLessEqual(a, 3.30)

    def test_stars_unit_vectors(self):
        for name, ra, dec, mag in STARS:
            d = star_direction(ra, dec)
            self.assertAlmostEqual(math.sqrt(sum(x * x for x in d)), 1.0,
                                   places=9, msg=name)
        # Sirius: ecliptic lon ~104 deg (Gemini), lat ~ -39.6 deg
        sx, sy, sz = star_direction(6.752, -16.72)
        lon = math.degrees(math.atan2(sy, sx)) % 360.0
        lat = math.degrees(math.asin(sz))
        self.assertAlmostEqual(lon, 104.0, delta=1.0)
        self.assertAlmostEqual(lat, -39.6, delta=1.0)

    def test_pole_vector(self):
        p = pole_direction(AXIAL_TILT["Earth"])
        self.assertAlmostEqual(p[2], math.cos(math.radians(23.44)), places=6)
        u = pole_direction(AXIAL_TILT["Uranus"])   # rolls on its side
        self.assertLess(u[2], 0.2)


class TestSOI(unittest.TestCase):
    def test_earth_soi(self):
        self.assertAlmostEqual(soi_au("Earth", 1.0), 0.00618, delta=0.0003)

    def test_jupiter_soi(self):
        self.assertAlmostEqual(soi_au("Jupiter", 5.2029), 0.322, delta=0.02)


class TestConics(unittest.TestCase):
    def test_elements_roundtrip(self):
        # coplanar arc: state -> elements recovers a, e
        from kepler import elements_to_state
        pos, nu = elements_to_state(1.5, 0.2, 0.0, 0.0, 120.0, 100.0)
        v = velocity_on_elements(1.5, 0.2, 120.0, 100.0, J2000, J2000)
        el = state_to_elements(pos, v)
        self.assertAlmostEqual(el["a"], 1.5, delta=0.01)
        self.assertAlmostEqual(el["e"], 0.2, delta=0.01)
        self.assertAlmostEqual(el["i"], 0.0, delta=0.1)  # coplanar arc

    def test_prograde_dv_raises_apo(self):
        pos, _ = elements_to_state(1.26, 0.207, 0.0, 0.0, 0.0, 0.0)
        v = velocity_on_elements(1.26, 0.207, 0.0, 0.0, J2000, J2000)
        el0 = state_to_elements(pos, v)
        v2 = apply_prograde_dv(pos, v, 1.0)
        el1 = state_to_elements(pos, v2)
        apo0 = el0["a"] * (1 + el0["e"])
        apo1 = el1["a"] * (1 + el1["e"])
        self.assertGreater(apo1, apo0)
        v3 = apply_prograde_dv(pos, v, -1.0)
        el2 = state_to_elements(pos, v3)
        self.assertLess(el2["a"] * (1 + el2["e"]), apo0)

    def test_escape_threshold(self):
        # enough prograde dV at 1 AU -> hyperbolic (a < 0)
        pos, _ = elements_to_state(1.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        v = velocity_on_elements(1.0, 0.0, 0.0, 0.0, J2000, J2000)
        v_esc = apply_prograde_dv(pos, v, 12.5)   # > (sqrt2-1)*29.78=12.34
        el = state_to_elements(pos, v_esc)
        self.assertLess(el["a"], 0.0)             # hyperbolic
        self.assertGreater(el["e"], 1.0)

    def test_hyperbolic_propagation_escapes(self):
        from conics import leg_from_state, pos_on_leg
        pos, _ = elements_to_state(1.0, 0.0, 0.0, 0.0, 0.0, 0.0)
        v = velocity_on_elements(1.0, 0.0, 0.0, 0.0, J2000, J2000)
        v_esc = apply_prograde_dv(pos, v, 12.5)
        leg = leg_from_state(pos, v_esc, J2000)
        p1 = pos_on_leg(leg, J2000 + 500.0)
        r1 = math.sqrt(sum(c * c for c in p1))
        self.assertGreater(r1, 2.0)   # leaves the inner system
        # hyperbolic speed approaches v_inf: never returns (M grows, r grows)
        p2 = pos_on_leg(leg, J2000 + 1000.0)
        r2 = math.sqrt(sum(c * c for c in p2))
        self.assertGreater(r2, r1)


class TestLagrange(unittest.TestCase):
    def test_l4_l5_equilateral(self):
        ep = planet_state("Earth", J2000)[0]
        lp = lagrange_points(ep)
        for key in ("L4", "L5"):
            p = lp[key]
            d_sun = math.sqrt(sum(c * c for c in p))
            d_earth = math.sqrt(sum((p[k] - ep[k]) ** 2 for k in range(3)))
            self.assertAlmostEqual(d_sun, d_earth, delta=1e-6, msg=key)

    def test_l1_l2_placement(self):
        ep = planet_state("Earth", J2000)[0]
        R = math.sqrt(sum(c * c for c in ep))
        lp = lagrange_points(ep)
        d1 = math.sqrt(sum(c * c for c in lp["L1"]))
        d2 = math.sqrt(sum(c * c for c in lp["L2"]))
        self.assertAlmostEqual(R - d1, 0.01, delta=0.002)   # 1.5M km sunward
        self.assertAlmostEqual(d2 - R, 0.01, delta=0.002)


class TestEarthOrbit(unittest.TestCase):
    def test_iss_period(self):
        ep = planet_state("Earth", J2000)[0]
        p0 = earth_orbit_pos(ep, ISS["a_km"], ISS["i_deg"], J2000)
        # after one period (~92.9 min) position repeats
        p1 = earth_orbit_pos(ep, ISS["a_km"], ISS["i_deg"],
                             J2000 + 92.93 / 1440.0)
        d = math.sqrt(sum((p1[k] - p0[k]) ** 2 for k in range(3)))
        self.assertLess(d * 149597870.7, 3000.0)

    def test_calcsat_sso_inclination(self):
        self.assertAlmostEqual(CALCSAT["i_deg"], 97.6, delta=0.1)


if __name__ == "__main__":
    unittest.main()
