# -*- coding: utf-8 -*-
"""
perturbations.py — OrbitLab 摄动力模型（J2 / 大气阻力 / 第三体 / 太阳光压）
===========================================================================

坐标系：地心 J2000 惯性系；单位 km / km/s / s
（阻力、光压内部走 SI：m / kg / N，注释中给出完整单位换算链）。

每个加速度函数注释给出：公式（含符号定义与单位）+ 物理讲解 + 对应 GMAT 源文件。

力模型总装（对应 GMAT ODEModel 对每个 ForceModel 的 GetDerivatives 求和）：
  a_total = -μr/r³ + Σ（勾选的摄动加速度）

零依赖：math + dataclasses + constants。
"""

import math
from dataclasses import dataclass
from constants import (MU_EARTH, RE_EARTH, J2_EARTH, OMEGA_EARTH,
                       AU_KM, MU_SUN, MU_MOON, P_SRP_1AU, atmos_density)


@dataclass
class PerturbConfig:
    """摄动开关与参数（UI 左栏控件直接映射到本结构）。"""
    use_j2: bool = True          # J2 带谐摄动开关
    j2: float = J2_EARTH         # J2 系数（滑块可调）
    use_drag: bool = False       # 大气阻力开关
    cd: float = 2.2              # 阻力系数 Cd（平板/钝体典型 2.0~2.3）
    drag_area_m2: float = 10.0   # 迎风面积 A [m^2]
    mass_kg: float = 150.0       # 卫星质量 m [kg]
    use_sun: bool = False        # 太阳第三体开关
    use_moon: bool = False       # 月球第三体开关
    use_srp: bool = False        # 太阳光压开关
    cr: float = 1.3              # 光压系数 Cr（1.0 全吸收 ~ 2.0 全反射）
    srp_area_m2: float = 10.0    # 受晒面积 [m^2]


def accel_j2(r, j2):
    """J2 带谐摄动加速度（惯性系 Vallado §10 形式），返回 [ax,ay,az] km/s^2。

    公式：记 r=|r|，c = -1.5·J2·(μ/r²)·(Re/r)²
      ax = c·(x/r)·(1 - 5(z/r)²)
      ay = c·(y/r)·(1 - 5(z/r)²)
      az = c·(z/r)·(3 - 5(z/r)²)
    物理：地球赤道隆起 → 引力势球谐展开 V = μ/r·[1 - J2(Re/r)²P₂(sinφ)]，
      勒让德多项式 P₂(sinφ) = ½(3sin²φ-1)，sinφ = z/r；本式即 ∇V 的 2 阶带谐项。
      宏观效果：轨道面进动（dΩ/dt<0）与近地点旋转（dω/dt），见 j2_secular_rates()。
    对应 GMAT：Harmonic.cpp Pines 递推在 n=2 的解析退化（EGM96 2 阶项逐位一致）。
    """
    rn = math.sqrt(r[0] * r[0] + r[1] * r[1] + r[2] * r[2])
    zr = r[2] / rn
    zr2 = zr * zr
    c = -1.5 * j2 * (MU_EARTH / (rn * rn)) * (RE_EARTH / rn) ** 2
    return [c * (r[0] / rn) * (1.0 - 5.0 * zr2),
            c * (r[1] / rn) * (1.0 - 5.0 * zr2),
            c * (r[2] / rn) * (3.0 - 5.0 * zr2)]


def accel_drag(r, v, cd, area_m2, mass_kg, jd):
    """大气阻力加速度，返回 [ax,ay,az] km/s^2。

    公式：a = -½·ρ·Cd·(A/m)·|v_rel|·v_rel
      符号/单位（SI）：ρ 大气密度 [kg/m^3]；Cd 阻力系数 [-]；
        A 迎风面积 [m^2]；m 质量 [kg]；v_rel 相对大气速度 [m/s]。
      单位链：kg/m^3 · (m^2/kg) · (m/s) · (m/s) = m/s^2，×1e-3 → km/s^2。
    大气共转：v_rel = v - ω⊕×r，ω⊕ = (0,0,OMEGA_EARTH) [rad/s]，
      叉积展开：ω×r = (-ω·y, ω·x, 0)（km/s，×1000 转 m/s 后代入）。
    密度：h = |r| - RE_EARTH [km]，ρ = atmos_density(h)（分段指数模型）。
    对应 GMAT：DragForce.cpp + Exponential 大气模型。
    注：jd 保留给更复杂的大气模型（本指数模型密度不随时间变化）。
    """
    wx = -OMEGA_EARTH * r[1]     # (ω×r)_x [km/s]
    wy = OMEGA_EARTH * r[0]      # (ω×r)_y [km/s]
    vrel = [(v[0] - wx) * 1000.0,   # → m/s
            (v[1] - wy) * 1000.0,
            v[2] * 1000.0]
    vn = math.sqrt(vrel[0] ** 2 + vrel[1] ** 2 + vrel[2] ** 2)
    rn = math.sqrt(r[0] * r[0] + r[1] * r[1] + r[2] * r[2])
    h = rn - RE_EARTH                       # 高度 [km]
    rho = atmos_density(h)                  # kg/m^3
    k = -0.5 * rho * cd * (area_m2 / mass_kg) * vn   # 系数 [1/s]
    return [k * vrel[0] * 1e-3, k * vrel[1] * 1e-3, k * vrel[2] * 1e-3]


def accel_third_body(r, r_body, mu_body):
    """第三体（日/月）摄动加速度，返回 [ax,ay,az] km/s^2。

    公式：a = -μ₃·( d/|d|³ + r_body/|r_body|³ )，d = r - r_body
      符号：r 卫星地心位置 [km]；r_body 第三体地心位置 [km]；
            μ₃ 第三体引力常数 [km^3/s^2]。
    物理：第一项 = 第三体对卫星的直接引力；第二项 = 第三体对地球的引力
      （地心非惯性系的惯性力修正，即"间接项"）。近地卫星上两者几乎抵消，
      残留为潮汐量级 ~μ₃·r/R³。
    对应 GMAT：PointMassForce.cpp 的 PointMasses 列表累加项。
    """
    d = [r[0] - r_body[0], r[1] - r_body[1], r[2] - r_body[2]]
    dn = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
    bn = math.sqrt(r_body[0] ** 2 + r_body[1] ** 2 + r_body[2] ** 2)
    dn3 = dn * dn * dn
    bn3 = bn * bn * bn
    return [-mu_body * (d[0] / dn3 + r_body[0] / bn3),
            -mu_body * (d[1] / dn3 + r_body[1] / bn3),
            -mu_body * (d[2] / dn3 + r_body[2] / bn3)]


def sun_pos_geo(jd):
    """地心 J2000 惯性系太阳位置（低精度解析式，~0.01° 量级），返回 [x,y,z] km。

    公式（n = JD - 2451545.0 为距 J2000.0 日数，角度单位度）：
      平黄经   L = 280.460° + 0.9856474°·n
      平近点角 g = 357.528° + 0.9856003°·n
      黄经     λ = L + 1.915°·sin g + 0.020°·sin 2g   （中心差：椭圆轨道改正）
      距离     R = 1.00014 - 0.01671·cos g - 0.00014·cos 2g   [AU]
      黄赤交角 ε = 23.439° - 0.0000004°·n
      黄道 → 赤道惯性系：
        x = R·cosλ；y = R·cosε·sinλ；z = R·sinε·sinλ（×AU_KM 得 km）
    """
    n = jd - 2451545.0
    L = math.radians((280.460 + 0.9856474 * n) % 360.0)
    g = math.radians((357.528 + 0.9856003 * n) % 360.0)
    lam = L + math.radians(1.915) * math.sin(g) + math.radians(0.020) * math.sin(2.0 * g)
    R = 1.00014 - 0.01671 * math.cos(g) - 0.00014 * math.cos(2.0 * g)
    eps = math.radians(23.439 - 0.0000004 * n)
    d = R * AU_KM
    return [d * math.cos(lam),
            d * math.cos(eps) * math.sin(lam),
            d * math.sin(eps) * math.sin(lam)]


def moon_pos_geo(jd):
    """地心 J2000 惯性系月球位置（简化星历），返回 [x,y,z] km。

    精度：~千公里级（取平均距离 + 主黄经改正项），教学演示足够。

    公式（n = JD - 2451545.0，角度单位度）：
      平黄经   L' = 218.316° + 13.176396°·n
      平近点角 M' = 134.963° + 13.064993°·n
      黄经改正（最大二均差项）：λ = L' + 6.289°·sin M'
      升交点经度 Ω_m = 125.045° - 0.0529539°·n（交点西退，周期 18.6 年）
      轨道面内纬度幅角 u = λ - Ω_m，白道倾角 i_m = 5.145°
      球面公式：轨道面矢量 (cos u, sin u, 0) 经 R3(-Ω_m)·R1(-i_m) 转到黄道系，
               再绕 x 轴转黄赤交角 ε 到赤道惯性系；
      距离取均值 R_m = 384400 km。
    """
    n = jd - 2451545.0
    Lp = math.radians((218.316 + 13.176396 * n) % 360.0)
    Mp = math.radians((134.963 + 13.064993 * n) % 360.0)
    lam = Lp + math.radians(6.289) * math.sin(Mp)
    Om = math.radians((125.045 - 0.0529539 * n) % 360.0)
    im = math.radians(5.145)
    eps = math.radians(23.439 - 0.0000004 * n)
    u = lam - Om
    cu, su = math.cos(u), math.sin(u)
    cO, sO = math.cos(Om), math.sin(Om)
    ci, si = math.cos(im), math.sin(im)
    # 白道面 → 黄道系（R3(-Ω_m)·R1(-i_m) 作用于 (cos u, sin u, 0)）
    xe = cO * cu - sO * su * ci
    ye = sO * cu + cO * su * ci
    ze = su * si
    # 黄道系 → 赤道惯性系（绕 x 轴转 +ε）
    ce, se = math.cos(eps), math.sin(eps)
    Rm = 384400.0     # 地月平均距离 [km]
    return [Rm * xe,
            Rm * (ce * ye - se * ze),
            Rm * (se * ye + ce * ze)]


def accel_srp(r, r_sun, cr, area_m2, mass_kg):
    """太阳光压加速度（含圆柱阴影因子），返回 [ax,ay,az] km/s^2。

    公式：a = ν·P_1AU·(AU/|d|)²·Cr·(A/m)·d̂
      符号/单位（SI）：P_1AU = 4.56e-6 N/m^2；d = r_sun - r（星→日矢量）；
        Cr 光压系数 [-]；A 受晒面积 [m^2]；m 质量 [kg]；d̂ 星→日单位矢量。
      单位链：N/m^2 · m^2/kg = N/kg = m/s^2，×1e-3 → km/s^2。
      平方反比：(AU/|d|)² 把 1 AU 处光压缩放到实际日距。
    圆柱阴影判据（几何）：
      若 r·d̂ < 0（卫星在背阳半球）
         且横向距离 |r - (r·d̂)d̂| < Re（进入地球阴影圆柱）
      则 ν = 0（地影，无光压），否则 ν = 1（全日照）。
    对应 GMAT：SolarRadiationPressure.cpp（ShadowState 的圆柱近似）。
    """
    d = [r_sun[0] - r[0], r_sun[1] - r[1], r_sun[2] - r[2]]
    dn = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2)
    dh = [d[0] / dn, d[1] / dn, d[2] / dn]      # 星→日方向（≈地→日方向）
    proj = r[0] * dh[0] + r[1] * dh[1] + r[2] * dh[2]          # r·d̂
    perp2 = ((r[0] - proj * dh[0]) ** 2 + (r[1] - proj * dh[1]) ** 2
             + (r[2] - proj * dh[2]) ** 2)                     # 横向距离²
    if proj < 0.0 and perp2 < RE_EARTH ** 2:
        return [0.0, 0.0, 0.0]                # ν = 0：地影内
    k = P_SRP_1AU * (AU_KM / dn) ** 2 * cr * (area_m2 / mass_kg)   # m/s^2
    return [k * dh[0] * 1e-3, k * dh[1] * 1e-3, k * dh[2] * 1e-3]


def total_accel(r, v, jd, cfg):
    """力模型总加速度 = 中心点质量 + 勾选摄动之和，返回 [ax,ay,az] km/s^2。

    中心引力：a = -μ·r/r³（PointMassForce.cpp 主项）。
    求和语义对应 GMAT ODEModel::GetDerivativesForState。
    """
    rn = math.sqrt(r[0] * r[0] + r[1] * r[1] + r[2] * r[2])
    k = -MU_EARTH / (rn * rn * rn)
    ax, ay, az = k * r[0], k * r[1], k * r[2]
    if cfg.use_j2:
        a = accel_j2(r, cfg.j2)
        ax += a[0]; ay += a[1]; az += a[2]
    if cfg.use_drag:
        a = accel_drag(r, v, cfg.cd, cfg.drag_area_m2, cfg.mass_kg, jd)
        ax += a[0]; ay += a[1]; az += a[2]
    if cfg.use_sun:
        a = accel_third_body(r, sun_pos_geo(jd), MU_SUN)
        ax += a[0]; ay += a[1]; az += a[2]
    if cfg.use_moon:
        a = accel_third_body(r, moon_pos_geo(jd), MU_MOON)
        ax += a[0]; ay += a[1]; az += a[2]
    if cfg.use_srp:
        a = accel_srp(r, sun_pos_geo(jd), cfg.cr, cfg.srp_area_m2, cfg.mass_kg)
        ax += a[0]; ay += a[1]; az += a[2]
    return [ax, ay, az]


def j2_secular_rates(a, e, i_deg, j2=J2_EARTH):
    """J2 长期摄动率解析式，返回 (dΩ/dt, dω/dt, dM/dt)，单位 deg/day。

    公式（Vallado §9.6；p = a(1-e²) 半通径，n = √(μ/a³) 平均运动 [rad/s]）：
      dΩ/dt = -(3/2)·J2·n·(Re/p)²·cos i          （轨道面进动：赤道隆起力矩）
      dω/dt =  (3/4)·J2·n·(Re/p)²·(5cos²i - 1)   （近地点旋转；
                                                   i=63.4° 临界倾角时为零）
      dM/dt =  n·[1 + (3/4)·J2·(Re/p)²·√(1-e²)·(3cos²i - 1)]  （平运动改正）
    换算：rad/s × (180/π) × 86400 = deg/day。
    教学对照：右栏显示本解析值，与数值传播算出的 osculating 变化率互验。
    """
    i = math.radians(i_deg)
    p = a * (1.0 - e * e)
    n = math.sqrt(MU_EARTH / a ** 3)                # rad/s
    f = j2 * n * (RE_EARTH / p) ** 2
    ci = math.cos(i)
    dOm = -1.5 * f * ci
    dw = 0.75 * f * (5.0 * ci * ci - 1.0)
    dM = n * (1.0 + 0.75 * j2 * (RE_EARTH / p) ** 2
              * math.sqrt(1.0 - e * e) * (3.0 * ci * ci - 1.0))
    s = 86400.0 * 180.0 / math.pi                   # rad/s → deg/day
    return dOm * s, dw * s, dM * s


def drag_da_dt_km_day(a, e, cfg, jd):
    """阻力导致的半长轴衰减率（圆轨道近似），返回 km/day（恒为负）。

    推导（能量法）：比能 ε = -μ/(2a) → dε/da = μ/(2a²)；
      阻力功率（单位质量）dε/dt = F·v/m = -½ρv²·Cd·(A/m)·v = -½ρv³·Cd·A/m；
      联立 da/dt = (dε/dt)/(dε/da) = -ρv³(CdA/m)·a²/μ，
      圆轨道 v² = μ/a 化简得 da/dt = -ρ·v·a/B，弹道系数 B = m/(Cd·A)。
    单位链（SI）：ρ [kg/m^3]·v [m/s]·a [m] / B [kg/m^2] = m/s，
      ×86.4（=86400 s/day ÷ 1000 m/km）→ km/day。
    注：e 参数保留（圆近似下不使用）；密度取 h = a - Re；jd 保留备用。
    """
    a_m = a * 1000.0                                # m
    mu_si = MU_EARTH * 1e9                          # m^3/s^2
    v = math.sqrt(mu_si / a_m)                      # m/s（圆轨道速度）
    rho = atmos_density(a - RE_EARTH)               # kg/m^3
    B = cfg.mass_kg / (cfg.cd * cfg.drag_area_m2)   # 弹道系数 kg/m^2
    da_dt = -rho * v * a_m / B                      # m/s
    return da_dt * 86400.0 / 1000.0                 # → km/day
