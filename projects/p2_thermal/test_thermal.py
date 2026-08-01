"""Tests for p2_thermal, cross-checking module 01/05 worked examples."""
import unittest

from thermal_sim import (
    equilibrium_plate, equilibrium_sphere, radiator_capacity,
    radiator_area, ThermalNode, simulate_network, conduction_r,
    contact_r, junction_temp, pcm_mass, heat_pipe_capillary_pressure,
    solder_fatigue_life,
)


class TestEquilibrium(unittest.TestCase):
    def test_gray_plate_facing_sun(self):
        # module 01: gray plate -> 393 K
        t = equilibrium_plate(alpha=1.0, eps=1.0)
        self.assertAlmostEqual(t, 393.0, delta=2.0)

    def test_white_paint(self):
        # module 01: alpha=0.2 eps=0.9 -> ~270 K (corrected)
        t = equilibrium_plate(alpha=0.2, eps=0.9)
        self.assertAlmostEqual(t, 270.0, delta=2.0)

    def test_osr(self):
        # module 01: alpha=0.08 eps=0.8 -> ~221 K
        t = equilibrium_plate(alpha=0.08, eps=0.8)
        self.assertAlmostEqual(t, 221.0, delta=3.0)

    def test_gray_sphere(self):
        # module 01: gray sphere -> 278 K
        t = equilibrium_sphere(alpha=1.0, eps=1.0)
        self.assertAlmostEqual(t, 278.0, delta=2.0)

    def test_suanxing_panel(self):
        # module 01 sec 3.2.5: OSR panel, 150 W internal + ~30 W env -> ~283 K
        t = equilibrium_plate(alpha=0.08, eps=0.80,
                              q_internal=150.0, q_extra=30.0)
        self.assertAlmostEqual(t, 283.0, delta=3.0)


class TestRadiator(unittest.TestCase):
    def test_capacity_313K(self):
        # module 05: eps=0.85 at 313 K -> ~462 W/m^2
        cap = radiator_capacity(0.85, 313.0)
        self.assertAlmostEqual(cap, 462.0, delta=8.0)

    def test_area_1kw(self):
        # module 05 sec 5.2: 1 kW, eps=0.8, 313 K, env 0.9, margin 1.2 -> ~3.1 m^2
        a = radiator_area(1000.0, 0.8, 313.0, env_factor=0.9, margin=1.2)
        self.assertAlmostEqual(a, 3.1, delta=0.2)

    def test_t4_scaling(self):
        # doubling temperature -> 16x capacity (deep space sink)
        c1 = radiator_capacity(0.85, 200.0)
        c2 = radiator_capacity(0.85, 400.0)
        self.assertAlmostEqual(c2 / c1, 16.0, delta=0.3)


class TestResistanceChain(unittest.TestCase):
    def test_junction_temp(self):
        # module 05 sec 5.3: 350 W, R_total=0.145 -> 51 K rise
        tj = junction_temp(313.0, 350.0, 0.145)
        self.assertAlmostEqual(tj - 313.0, 50.75, delta=0.5)

    def test_derated_case(self):
        # after derating to 300 W: rise = 43.5 K -> Tj = 356.5 K (83.5 C)
        tj = junction_temp(313.0, 300.0, 0.145)
        self.assertAlmostEqual(tj - 273.15, 83.35, delta=0.5)

    def test_conduction(self):
        r = conduction_r(0.01, 167.0, 0.01)   # 1 cm Al plate, 100 cm^2
        self.assertAlmostEqual(r, 0.006, delta=0.001)

    def test_contact(self):
        r = contact_r(0.5, 50.0)              # 0.5 K cm2/W over 50 cm2
        self.assertAlmostEqual(r, 0.01, places=6)


class TestTransient(unittest.TestCase):
    def test_single_node_cooling(self):
        # node radiating to space should cool monotonically
        n = ThermalNode("panel", capacity_j_per_k=50e3, t0_k=350.0)
        hist = simulate_network([n], 3600.0, 10.0, radiators=[(n, 0.85)])
        t_end = hist[-1][1]["panel"]
        self.assertLess(t_end, 350.0)
        self.assertGreater(t_end, 200.0)

    def test_two_node_equilibration(self):
        # two linked nodes converge toward each other
        a = ThermalNode("a", 10e3, 350.0)
        b = ThermalNode("b", 10e3, 250.0)
        a.connect(b, 5.0)
        hist = simulate_network([a, b], 7200.0, 10.0)
        ta, tb = hist[-1][1]["a"], hist[-1][1]["b"]
        self.assertAlmostEqual(ta, tb, delta=15.0)


class TestAux(unittest.TestCase):
    def test_pcm(self):
        # module 05: 1 kW x 20 min -> ~6 kg paraffin
        m = pcm_mass(1000.0, 1200.0)
        self.assertAlmostEqual(m, 6.0, delta=0.1)

    def test_capillary(self):
        # ammonia heat pipe: sigma~0.02 N/m, r_eff~0.1 mm -> ~400 Pa
        p = heat_pipe_capillary_pressure(0.02, 1e-4)
        self.assertAlmostEqual(p, 400.0, delta=20.0)

    def test_fatigue_scaling(self):
        # module 01: dT 60->30 doubles life x4 (m=2)
        n = solder_fatigue_life(3000.0, 60.0, 30.0)
        self.assertAlmostEqual(n, 12000.0, delta=1.0)


if __name__ == "__main__":
    unittest.main()
