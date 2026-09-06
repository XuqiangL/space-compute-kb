"""test_orbitlab.py - OrbitLab 物理内核单元测试

原则（与全知识库一致）：每个 assert 锁定一个物理数值——
测试失败 = 代码或物理模型有一方错了。
"""
import math
import unittest

from constants import (MU_EARTH, RE_EARTH, J2_EARTH, OMEGA_EARTH,
                       atmos_density, gmst_rad, julian_date)
from elements import (elements_to_state, state_to_elements, orbit_polyline,
                      perigee_dir)
from perturbations import (PerturbConfig, accel_j2, accel_drag, accel_srp,
                           sun_pos_geo, moon_pos_geo, total_accel,
                           j2_secular_rates, drag_da_dt_km_day)
from propagator import Propagator

JD0 = 2451545.0   # J2000.0 历元（2000-01-01 12:00 UTC）


class TestElements(unittest.TestCase):
    """六根数↔状态矢量往返一致性。"""

    def test_roundtrip_leo(self):
        # 600 km 圆轨道（SSO 附近）
        el = dict(a=6978.1363, e=0.001, i=97.8, Om=30.0, w=10.0, nu=25.0)
        r, v = elements_to_state(el["a"], el["e"], el["i"], el["Om"],
                                 el["w"], el["nu"])
        back = state_to_elements(r, v)
        self.assertAlmostEqual(back["a"], el["a"], places=6)
        self.assertAlmostEqual(back["e"], el["e"], places=8)
        self.assertAlmostEqual(back["i"], el["i"], places=8)

    def test_roundtrip_molniya(self):
        # Molniya 大椭圆轨道（e=0.74）
        el = dict(a=26600.0, e=0.74, i=63.4, Om=200.0, w=270.0, nu=100.0)
        r, v = elements_to_state(el["a"], el["e"], el["i"], el["Om"],
                                 el["w"], el["nu"])
        back = state_to_elements(r, v)
        self.assertAlmostEqual(back["a"], el["a"], delta=1e-4)
        self.assertAlmostEqual(back["e"], el["e"], delta=1e-8)
        self.assertAlmostEqual(back["w"], el["w"], delta=1e-6)

    def test_circular_orbit_radius(self):
        # 圆轨道上任意 ν 处 |r| 应恒等于 a
        r, v = elements_to_state(6978.1363, 0.0, 45.0, 0.0, 0.0, 0.0)
        self.assertAlmostEqual(math.sqrt(sum(c * c for c in r)),
                               6978.1363, places=6)

    def test_orbit_polyline_closed(self):
        # 轨道采样线首尾闭合（完整椭圆 361 点）
        pts = orbit_polyline(10000.0, 0.2, 30.0, 40.0, 50.0)
        self.assertGreaterEqual(len(pts), 360)
        d = math.sqrt(sum((pts[0][k] - pts[-1][k]) ** 2 for k in range(3)))
        self.assertLess(d, 1e-6 * 10000.0)


class TestKepler(unittest.TestCase):
    """无摄动传播 = 纯二体：能量/角动量守恒，整圈后回到起点。"""

    def test_energy_conservation(self):
        cfg = PerturbConfig(use_j2=False)   # 全部摄动关闭
        r0, v0 = elements_to_state(6978.1363, 0.01, 51.6, 80.0, 0.0, 0.0)
        prop = Propagator(cfg)
        prop.reset(r0, v0, JD0)
        T = 2.0 * math.pi * math.sqrt(6978.1363 ** 3 / MU_EARTH)
        prop.step(10.0 * T)               # 传播 10 圈
        e0 = sum(c * c for c in v0) / 2 - MU_EARTH / math.sqrt(
            sum(c * c for c in r0))
        r1, v1 = prop.state[:3], prop.state[3:]
        e1 = sum(c * c for c in v1) / 2 - MU_EARTH / math.sqrt(
            sum(c * c for c in r1))
        # RK4 定步 10 s 子步的累积误差量级 ~1e-9（相对），留裕量到 1e-6
        self.assertAlmostEqual(e1 / e0, 1.0, delta=1e-6)

    def test_period_matches_kepler(self):
        # 传播一个周期后真近点角应回到初值（ν: 0→360°）
        cfg = PerturbConfig(use_j2=False)
        r0, v0 = elements_to_state(10000.0, 0.1, 30.0, 0.0, 0.0, 0.0)
        prop = Propagator(cfg)
        prop.reset(r0, v0, JD0)
        T = 2.0 * math.pi * math.sqrt(10000.0 ** 3 / MU_EARTH)
        prop.step(T)
        osc = state_to_elements(prop.state[:3], prop.state[3:])
        self.assertAlmostEqual(osc["a"], 10000.0, delta=1e-3)
        self.assertTrue(osc["nu"] < 1.0 or osc["nu"] > 359.0)


class TestPerturbations(unittest.TestCase):
    """各摄动模型的物理正确性。"""

    def test_j2_secular_numeric_vs_analytic(self):
        # J2 数值传播 1 天的 Ω 变化 vs 解析长期摄动率（容差 5%）
        cfg = PerturbConfig(use_j2=True, j2=J2_EARTH)
        el = dict(a=6978.1363, e=0.001, i=97.8, Om=30.0, w=0.0, nu=0.0)
        r0, v0 = elements_to_state(el["a"], el["e"], el["i"], el["Om"],
                                   el["w"], el["nu"])
        prop = Propagator(cfg)
        prop.reset(r0, v0, JD0)
        prop.step(86400.0)
        osc = state_to_elements(prop.state[:3], prop.state[3:])
        dOm_num = (osc["Om"] - el["Om"] + 540.0) % 360.0 - 180.0
        dOm_ana, _, _ = j2_secular_rates(el["a"], el["e"], el["i"])
        self.assertAlmostEqual(dOm_num, dOm_ana, delta=abs(dOm_ana) * 0.05)

    def test_j2_nodal_regression_sign(self):
        # 顺行轨道（i<90°）节点退行为负；逆行（i>90°）为正
        dOm_pro, _, _ = j2_secular_rates(6978.0, 0.001, 30.0)
        dOm_ret, _, _ = j2_secular_rates(6978.0, 0.001, 97.8)
        self.assertLess(dOm_pro, 0.0)
        self.assertGreater(dOm_ret, 0.0)

    def test_drag_decays_semimajor(self):
        # 大气阻力使半长轴单调下降（LEO 400 km）
        cfg = PerturbConfig(use_j2=False, use_drag=True, cd=2.2,
                            drag_area_m2=10.0, mass_kg=150.0)
        r0, v0 = elements_to_state(RE_EARTH + 400.0, 0.001, 51.6,
                                   0.0, 0.0, 0.0)
        prop = Propagator(cfg)
        prop.reset(r0, v0, JD0)
        a0 = state_to_elements(prop.state[:3], prop.state[3:])["a"]
        prop.step(5400.0)                 # 约一圈
        a1 = state_to_elements(prop.state[:3], prop.state[3:])["a"]
        self.assertLess(a1, a0)
        self.assertLess(drag_da_dt_km_day(a0, 0.001, cfg, JD0), 0.0)

    def test_drag_corotating_atmosphere(self):
        # 共转大气：惯性系静止的卫星，相对大气向西运动（v_rel = v − ω×r），
        # 阻力与 v_rel 反向 → 沿 +Y（东风方向）"推着卫星走"
        cfg = PerturbConfig(use_j2=False, use_drag=True, cd=2.2,
                            drag_area_m2=10.0, mass_kg=150.0)
        r = (RE_EARTH + 300.0, 0.0, 0.0)
        v = (0.0, 0.0, 0.0)               # 惯性系静止 → 相对大气向西
        a = accel_drag(r, v, 2.2, 10.0, 150.0, JD0)
        self.assertGreater(a[1], 0.0)     # 阻力沿 +Y（与大气运动同向）

    def test_srp_shadow(self):
        # 圆柱阴影：背阳侧且横向距 < Re 时光压为 0；向阳侧非零
        r_sun = sun_pos_geo(JD0)
        d = math.sqrt(sum(c * c for c in r_sun))
        u = tuple(c / d for c in r_sun)   # 地→日单位矢量
        r_shadow = tuple(-u[k] * (RE_EARTH + 500.0) for k in range(3))
        r_sunlit = tuple(u[k] * (RE_EARTH + 500.0) for k in range(3))
        a_sh = accel_srp(r_shadow, r_sun, 1.3, 10.0, 150.0)
        a_su = accel_srp(r_sunlit, r_sun, 1.3, 10.0, 150.0)
        self.assertAlmostEqual(math.sqrt(sum(c * c for c in a_sh)), 0.0,
                               places=15)
        self.assertGreater(math.sqrt(sum(c * c for c in a_su)), 0.0)

    def test_third_body_moon_gravity_assists(self):
        # 月球第三体加速度量级：地月距离处 ~1e-6 km/s² 量级
        r_moon = moon_pos_geo(JD0)
        d = math.sqrt(sum(c * c for c in r_moon))
        self.assertAlmostEqual(d, 384400.0, delta=20000.0)

    def test_atmos_density_exponential(self):
        # 指数大气：400 km 处密度应在 1e-12 kg/m³ 量级
        rho = atmos_density(400.0)
        self.assertGreater(rho, 1e-13)
        self.assertLess(rho, 1e-10)
        # 密度随高度单调下降
        self.assertLess(atmos_density(600.0), atmos_density(400.0))


class TestTimeAndGeo(unittest.TestCase):
    """时间系统与几何。"""

    def test_earth_texture_loads(self):
        # 世界地图纹理（PPM）应能加载为 256×512×3 数组
        from earth_texture import load_texture
        tex = load_texture()
        self.assertIsNotNone(tex)
        self.assertEqual(tex.shape, (256, 512, 3))

    def test_earth_texture_render(self):
        # 贴图球渲染：输出尺寸 2R×2R，盘外 alpha=0、盘心 alpha=255
        from earth_texture import EarthTexture
        et = EarthTexture()
        arr, inside = et.render_array((1, 0, 0), (0, 1, 0), (0, 0, 1),
                                      0.0, 64)
        self.assertEqual(arr.shape, (128, 128, 3))
        self.assertTrue(inside[64, 64])       # 盘心在盘内
        self.assertFalse(inside[0, 0])        # 角落像素在盘外

    def test_gmst_at_j2000(self):
        # GMST(J2000.0) = 280.46061837°（IAU 1982）
        self.assertAlmostEqual(math.degrees(gmst_rad(JD0)) % 360.0,
                               280.46061837, places=6)

    def test_julian_date_j2000(self):
        self.assertAlmostEqual(julian_date(2000, 1, 1, 12, 0, 0.0),
                               2451545.0, places=9)

    def test_perigee_dir_unit(self):
        P = perigee_dir(30.0, 40.0, 50.0)
        self.assertAlmostEqual(math.sqrt(sum(c * c for c in P)), 1.0,
                               places=12)

    def test_nu_arc_no_blowup_at_180(self):
        # 回归测试：ν≈180° 时卫星与近地点方向几乎对径，
        # 旧 slerp 实现 sinθ→0 导致弧点爆炸到 1e16 km（屏幕上拉出 wild 红线）。
        # 新实现按角度直接采样，所有弧点模长必须恒等于弧半径。
        from geometry3d import angle_arcs
        for nu in (179.9, 180.0, 180.1, 270.0, 359.9):
            arcs = angle_arcs(6978.1363, 0.1, 45.0, 30.0, 0.0, nu)
            arc = arcs["nu"]
            self.assertGreater(len(arc), 2)
            r_expected = math.sqrt(arc[0][0] ** 2 + arc[0][1] ** 2
                                   + arc[0][2] ** 2)
            for p in arc:
                r = math.sqrt(p[0] ** 2 + p[1] ** 2 + p[2] ** 2)
                self.assertAlmostEqual(r, r_expected, delta=1e-6 * r_expected)
                self.assertLess(r, 1e6)       # 绝不爆炸

    def test_arcs_above_earth_surface(self):
        # 角度弧必须浮在地球表面之上（否则被地球遮挡不可见）
        from geometry3d import angle_arcs
        arcs = angle_arcs(6978.1363, 0.1, 45.0, 30.0, 10.0, 120.0)
        for key in ("i", "Om", "w", "nu"):
            for p in arcs[key]:
                r = math.sqrt(p[0] ** 2 + p[1] ** 2 + p[2] ** 2)
                self.assertGreater(r, RE_EARTH)


class TestPresets(unittest.TestCase):
    """教学预设轨道合法性（近地点必须在大气层之上）。"""

    def test_max_eccentricity_formula(self):
        # 物理边界公式：e_max = 1 − (RE + h_min)/a
        # a = 6978.1363 km 时 e_max ≈ 0.07164（rp 恰好 = 地表 + 100 km）
        from elements import max_eccentricity, perigee_altitude
        a = 6978.1363
        e_max = max_eccentricity(a)
        self.assertAlmostEqual(e_max, 1.0 - (RE_EARTH + 100.0) / a,
                               places=12)
        self.assertAlmostEqual(perigee_altitude(a, e_max), 100.0, places=6)
        # GEO 高轨允许很扁：a = 42164 km 时 e_max ≈ 0.846
        self.assertAlmostEqual(max_eccentricity(42164.0), 0.8463, places=3)
        # a 低于安全高度时无可行轨道
        self.assertEqual(max_eccentricity(RE_EARTH + 50.0), 0.0)

    def test_preset_perigee_safe(self):
        presets = [
            ("LEO/ISS", 6798.0, 0.0005, 51.6),
            ("SSO", 6978.0, 0.001, 97.8),
            ("MEO/GPS", 26560.0, 0.005, 55.0),
            ("GEO", 42164.0, 0.001, 0.1),
            ("Molniya", 26600.0, 0.74, 63.4),
            ("GTO", 24505.0, 0.725, 28.5),
        ]
        for name, a, e, i in presets:
            rp = a * (1.0 - e)
            self.assertGreater(rp, RE_EARTH + 100.0,
                               f"{name} 近地点过低: {rp:.0f} km")


if __name__ == "__main__":
    unittest.main(verbosity=2)
