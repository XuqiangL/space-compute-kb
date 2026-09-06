# -*- coding: utf-8 -*-
"""
constants.py — OrbitLab 物理常量 / 分段指数大气 / 时间系统
==========================================================

职责：
  1) 地心 J2000 惯性系（X→春分点，Z→北极）所需物理常量；
  2) GMAT Exponential 风格分段指数大气密度模型 atmos_density()；
  3) 时间系统：julian_date() / gmst_rad() / jd_to_datetime_str()。

物理约定：
  - 单位制：km / km/s / s（大气、光压涉及 SI 的量在函数注释中给出换算链）；
  - 时间：浮点儒略日 JD（按 UTC 处理，教学精度足够）；
  - 角度：本模块内部一律弧度，对外接口（elements.py 等）一律角度。

常量来源（NASA/GMAT 源码，commit ce6eba2）：
  MU_EARTH : src/gmatutil/util/GmatDefaults.hpp:186
  RE_EARTH : src/gmatutil/util/GmatDefaults.hpp:159
  MU_MOON  : src/gmatutil/util/GmatDefaults.hpp:314
  J2_EARTH : EGM96.cof 归一化 C̄20 = -4.84165371736e-04 → J2 = -√5·C̄20

零依赖：仅用标准库 math。
"""

import math

# ===========================================================================
# 1. 天体常量
# ===========================================================================
MU_EARTH = 398600.4415      # km^3/s^2 地球引力常数 μ（GmatDefaults.hpp:186）
RE_EARTH = 6378.1363        # km 地球赤道半径（GmatDefaults.hpp:159）
J2_EARTH = 1.0826269269e-3  # 地球 J2 = -√5·C̄20（EGM96: C̄20 = -4.84165371736e-04）
OMEGA_EARTH = 7.2921159e-5  # rad/s 地球自转角速度 ≈ 2π/86164.0905（恒星日）

AU_KM = 149597870.7         # km 天文单位（IAU 2012 定义值）
MU_SUN = 1.32712440018e11   # km^3/s^2 太阳引力常数
MU_MOON = 4902.8005821478   # km^3/s^2 月球引力常数（GmatDefaults.hpp:314）

P_SRP_1AU = 4.56e-6         # N/m^2 1 AU 处太阳光压（全吸收面，GMAT 默认值）

# ===========================================================================
# 2. 分段指数大气模型（GMAT Exponential 模型风格）
# ---------------------------------------------------------------------------
# 表项 (h0, ρ0, H)：高度 h ∈ [h0, 下一段 h0) 内
#     ρ(h) = ρ0 · exp(-(h - h0) / H)
# 符号/单位：h0 分段基准高度 [km]；ρ0 基准密度 [kg/m^3]；H 密度标高 [km]。
# 物理：流体静力学平衡 + 分段等温假设 → 密度随高度指数衰减；
#       标高 H = kT/mg 随温度层结变化，故各段给不同 H。
# ===========================================================================
ATMOS_TABLE = [
    (0,    1.225,     8.5),    # 海平面标准大气
    (100,  5.604e-7,  5.9),
    (150,  2.130e-9,  24.1),
    (200,  2.789e-10, 35.4),
    (300,  2.418e-11, 47.4),
    (400,  2.803e-12, 58.3),
    (500,  5.215e-13, 68.8),
    (600,  1.137e-13, 79.0),
    (700,  3.070e-14, 88.7),
    (800,  1.136e-14, 98.5),
    (900,  5.759e-15, 108.3),
    (1000, 3.561e-15, 118.1),
]

def atmos_density(h_km):
    """分段指数大气密度 ρ(h)。

    参数：h_km — 距地表高度 [km]（= |r| - RE_EARTH）
    返回：ρ [kg/m^3]

    规则：
      h < 0    → 返回地表值 1.225 kg/m^3；
      否则找到 h 所在分段 (h0, ρ0, H)，ρ = ρ0·exp(-(h-h0)/H)；
      h > 1000 → 用最后一段（1000 km）外推。
    """
    if h_km < 0.0:
        return ATMOS_TABLE[0][1]
    seg = ATMOS_TABLE[-1]
    for k in range(len(ATMOS_TABLE) - 1):
        if ATMOS_TABLE[k][0] <= h_km < ATMOS_TABLE[k + 1][0]:
            seg = ATMOS_TABLE[k]
            break
    h0, rho0, H = seg
    return rho0 * math.exp(-(h_km - h0) / H)


# ===========================================================================
# 3. 时间系统
# ===========================================================================
def julian_date(y, mo, d, h=0, mi=0, s=0.0):
    """公历 UTC → 儒略日 JD（标准天文算法，Meeus《Astronomical Algorithms》§7）。

    公式（格里历）：
      若 mo <= 2：Y = y-1，M = mo+12；否则 Y = y，M = mo
      A = floor(Y/100)，B = 2 - A + floor(A/4)              （格里历改正项）
      JD = floor(365.25·(Y+4716)) + floor(30.6001·(M+1)) + d + B - 1524.5
           + (h + mi/60 + s/3600)/24
    校验：2000-01-01 12:00:00 UTC → JD 2451545.0（J2000.0 历元）。
    """
    if mo <= 2:
        Y, M = y - 1, mo + 12
    else:
        Y, M = y, mo
    A = Y // 100
    B = 2 - A + A // 4
    jd = (math.floor(365.25 * (Y + 4716)) + math.floor(30.6001 * (M + 1))
          + d + B - 1524.5)
    return jd + (h + mi / 60.0 + s / 3600.0) / 24.0


def gmst_rad(jd):
    """格林尼治平恒星时 GMST，返回弧度 ∈ [0, 2π)。

    公式（IAU 1982 近似）：
      GMST[deg] = 280.46061837 + 360.98564736629·(JD - 2451545.0)
      其中 360.98564736629°/day 为地球相对春分点的周日角速度；
      JD - 2451545.0 = 距 J2000.0 的日数。结果 mod 360° 后转弧度。
    用途：惯性系 → 地固系旋转（画地球自转、星下点轨迹）。
    """
    d = jd - 2451545.0
    deg = (280.46061837 + 360.98564736629 * d) % 360.0
    return math.radians(deg)


def jd_to_datetime_str(jd):
    """JD → "YYYY-MM-DD HH:MM:SS UTC" 显示字符串（Meeus §7 反算）。

    公式：JD+0.5 拆为整数 Z 与小数 F；
      Z >= 2299161 时 α = floor((Z-1867216.25)/36524.25)，A = Z+1+α-floor(α/4)；
      否则 A = Z；
      B = A+1524；C = floor((B-122.1)/365.25)；D = floor(365.25·C)；
      E = floor((B-D)/30.6001)；
      日 = B-D-floor(30.6001·E)+F；月 = E-1（E<14）否则 E-13；
      年 = C-4716（月>2）否则 C-4715。小数日 ×24/60/60 拆出时分秒。
    """
    jd2 = jd + 0.5
    Z = int(math.floor(jd2))
    F = jd2 - Z
    if Z >= 2299161:
        alpha = int((Z - 1867216.25) / 36524.25)
        A = Z + 1 + alpha - alpha // 4
    else:
        A = Z
    B = A + 1524
    C = int((B - 122.1) / 365.25)
    D = int(365.25 * C)
    E = int((B - D) / 30.6001)
    day_f = B - D - int(30.6001 * E) + F
    month = E - 1 if E < 14 else E - 13
    year = C - 4716 if month > 2 else C - 4715
    day = int(day_f)
    frac = (day_f - day) * 24.0
    hh = int(frac)
    frac = (frac - hh) * 60.0
    mm = int(frac)
    ss = int(round((frac - mm) * 60.0))
    if ss >= 60:        # 四舍五入进位保护
        ss -= 60
        mm += 1
    if mm >= 60:
        mm -= 60
        hh += 1
    return "%04d-%02d-%02d %02d:%02d:%02d UTC" % (year, month, day, hh, mm, ss)
