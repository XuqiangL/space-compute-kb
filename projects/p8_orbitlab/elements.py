# -*- coding: utf-8 -*-
"""
elements.py — 经典六根数 ↔ 惯性系状态矢量（OrbitLab 物理内核）
==============================================================

坐标系：地心 J2000 赤道惯性系（X→春分点，Z→北极，Y 构成右手系）。
单位：km / km/s / s；接口角度一律为度（deg），内部计算转弧度。

六根数定义（经典开普勒根数）：
  a  半长轴 [km]；e 偏心率 [-]；i 轨道倾角 [deg]
  Ω  升交点赤经 [deg]；ω 近地点幅角 [deg]；ν 真近点角 [deg]

变换原理（PQW→IJK）：
  近焦点坐标系 PQW：P 指向近地点，W 沿角动量方向，Q 在轨道面内构成右手系。
  惯性系矢量 = R3(-Ω)·R1(-i)·R3(-ω)·(PQW 矢量)，R1/R3 为基本旋转矩阵：
      R1(θ) = [1,0,0; 0,cosθ,sinθ; 0,-sinθ,cosθ]
      R3(θ) = [cosθ,sinθ,0; -sinθ,cosθ,0; 0,0,1]
  几何含义：把轨道面先绕 z 轴转 -ω、再绕 x 轴转 -i、再绕 z 轴转 -Ω，
  即把"近地点-轨道面"姿态嵌入惯性系。

零依赖：仅用 math 与 constants。
"""

import math
from constants import MU_EARTH


def _pqw_to_ijk_matrix(i_deg, Om_deg, w_deg):
    """组合旋转矩阵 R = R3(-Ω)·R1(-i)·R3(-ω)（3x3，按行存储）。

    展开（记 cΩ=cosΩ, sΩ=sinΩ, ci=cos i, si=sin i, cω=cosω, sω=sinω）：
      R[0] = [cΩcω - sΩsωci,  -cΩsω - sΩcωci,   sΩsi]
      R[1] = [sΩcω + cΩsωci,  -sΩsω + cΩcωci,  -cΩsi]
      R[2] = [sωsi,            cωsi,             ci  ]
    """
    i, Om, w = math.radians(i_deg), math.radians(Om_deg), math.radians(w_deg)
    cO, sO = math.cos(Om), math.sin(Om)
    ci, si = math.cos(i), math.sin(i)
    cw, sw = math.cos(w), math.sin(w)
    return [
        [cO * cw - sO * sw * ci, -cO * sw - sO * cw * ci,  sO * si],
        [sO * cw + cO * sw * ci, -sO * sw + cO * cw * ci, -cO * si],
        [sw * si,                 cw * si,                 ci],
    ]


def _mat_vec(R, u):
    """矩阵乘矢量 y = R·u（3x3 矩阵 · 3 维矢量）。"""
    return [R[0][0] * u[0] + R[0][1] * u[1] + R[0][2] * u[2],
            R[1][0] * u[0] + R[1][1] * u[1] + R[1][2] * u[2],
            R[2][0] * u[0] + R[2][1] * u[1] + R[2][2] * u[2]]


def elements_to_state(a, e, i_deg, Om_deg, w_deg, nu_deg, mu=MU_EARTH):
    """经典六根数 → 惯性系状态矢量 (r[3], v[3])，单位 km / km/s。

    公式（Vallado §2.5）：
      半通径 p = a(1-e²)
      近焦点坐标（PQW 系）：
        r_pqw = ( p·cosν/(1+e·cosν),  p·sinν/(1+e·cosν),  0 )
        v_pqw = √(μ/p)·( -sinν,  e+cosν,  0 )
      惯性系：r = R·r_pqw，v = R·v_pqw，R = R3(-Ω)R1(-i)R3(-ω)。
    原理：圆锥曲线极方程 r = p/(1+e·cosν) 给出到焦点（地心）的距离；
          速度公式由角动量守恒 h = √(μp) 与能量积分联合导出。
    """
    p = a * (1.0 - e * e)
    nu = math.radians(nu_deg)
    cn, sn = math.cos(nu), math.sin(nu)
    denom = 1.0 + e * cn
    r_pqw = [p * cn / denom, p * sn / denom, 0.0]
    k = math.sqrt(mu / p)
    v_pqw = [-k * sn, k * (e + cn), 0.0]
    R = _pqw_to_ijk_matrix(i_deg, Om_deg, w_deg)
    return _mat_vec(R, r_pqw), _mat_vec(R, v_pqw)


def state_to_elements(r, v, mu=MU_EARTH):
    """惯性系状态矢量 → 六根数字典（角度一律度，Ω/ω/ν 归一化到 [0,360)）。

    公式（Vallado §2.5，h-n-e 矢量法）：
      比角动量  h_vec = r × v，h = |h_vec|
      交线矢量  n_vec = ẑ × h_vec = (-h_y, h_x, 0)，n = |n_vec|（指向升交点）
      偏心率矢量 e_vec = [(v²-μ/r)·r - (r·v)·v]/μ，e = |e_vec|（指向近地点）
      比机械能  ε = v²/2 - μ/r  →  a = -μ/(2ε)      （椭圆轨道 ε<0）
      倾角  i = arccos(h_z/h)
      升交点赤经 Ω = arccos(n_x/n)，若 n_y<0 则 Ω = 360°-Ω
      近地点幅角 ω = arccos(n·e/(n·e))，若 e_z<0 则 ω = 360°-ω
      真近点角 ν = arccos(e·r/(e·r))，若 r·v<0 则 ν = 360°-ν
    退化处理（避免除零，教学场景足够）：
      圆轨道 e≈0：ω 取 0，ν 用纬度幅角 u（相对交线）；
      赤道轨道 i≈0（n≈0）：Ω 取 0，ω 用近地点经度。
    返回 dict(a, e, i, Om, w, nu, rp, ra, period_s, energy, h)：
      rp = a(1-e) 近地点半径 [km]；ra = a(1+e) 远地点半径 [km]；
      period_s = 2π√(a³/μ) 开普勒第三定律周期 [s]；
      energy = ε 比机械能 [km^2/s^2]；h 比角动量模 [km^2/s]。
    """
    r_n = math.sqrt(r[0] ** 2 + r[1] ** 2 + r[2] ** 2)
    v_n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    # h 矢量 = r × v（叉积展开）
    h_vec = [r[1] * v[2] - r[2] * v[1],
             r[2] * v[0] - r[0] * v[2],
             r[0] * v[1] - r[1] * v[0]]
    h_n = math.sqrt(h_vec[0] ** 2 + h_vec[1] ** 2 + h_vec[2] ** 2)
    # n 矢量 = ẑ × h（指向升交点）
    n_vec = [-h_vec[1], h_vec[0], 0.0]
    n_n = math.sqrt(n_vec[0] ** 2 + n_vec[1] ** 2)
    # e 矢量（Laplace-Runge-Lenz 矢量 / μ）
    rv = r[0] * v[0] + r[1] * v[1] + r[2] * v[2]
    coef = v_n * v_n - mu / r_n
    e_vec = [(coef * r[k] - rv * v[k]) / mu for k in range(3)]
    e = math.sqrt(e_vec[0] ** 2 + e_vec[1] ** 2 + e_vec[2] ** 2)
    # 比机械能与半长轴
    energy = 0.5 * v_n * v_n - mu / r_n
    a = -mu / (2.0 * energy)
    # 倾角 i
    i = math.degrees(math.acos(max(-1.0, min(1.0, h_vec[2] / h_n))))
    # 升交点赤经 Ω
    if n_n > 1e-12:
        Om = math.degrees(math.acos(max(-1.0, min(1.0, n_vec[0] / n_n))))
        if n_vec[1] < 0.0:
            Om = 360.0 - Om
    else:
        Om = 0.0
    # 近地点幅角 ω
    if n_n > 1e-12 and e > 1e-12:
        w = math.degrees(math.acos(max(-1.0, min(1.0,
            (n_vec[0] * e_vec[0] + n_vec[1] * e_vec[1] + n_vec[2] * e_vec[2])
            / (n_n * e)))))
        if e_vec[2] < 0.0:
            w = 360.0 - w
    elif e > 1e-12:   # 赤道轨道：近地点经度 ϖ = arccos(e_x/e)
        w = math.degrees(math.acos(max(-1.0, min(1.0, e_vec[0] / e))))
        if e_vec[1] < 0.0:
            w = 360.0 - w
    else:
        w = 0.0
    # 真近点角 ν
    if e > 1e-12:
        nu = math.degrees(math.acos(max(-1.0, min(1.0,
            (e_vec[0] * r[0] + e_vec[1] * r[1] + e_vec[2] * r[2])
            / (e * r_n)))))
        if rv < 0.0:
            nu = 360.0 - nu
    elif n_n > 1e-12:  # 圆轨道：纬度幅角 u = arccos(n·r/(n·r))
        nu = math.degrees(math.acos(max(-1.0, min(1.0,
            (n_vec[0] * r[0] + n_vec[1] * r[1]) / (n_n * r_n)))))
        if r[2] < 0.0:
            nu = 360.0 - nu
    else:              # 圆赤道轨道：真经度
        nu = math.degrees(math.acos(max(-1.0, min(1.0, r[0] / r_n))))
        if r[1] < 0.0:
            nu = 360.0 - nu
    rp = a * (1.0 - e)
    ra = a * (1.0 + e)
    period_s = 2.0 * math.pi * math.sqrt(a ** 3 / mu)
    return dict(a=a, e=e, i=i, Om=Om, w=w, nu=nu,
                rp=rp, ra=ra, period_s=period_s, energy=energy, h=h_n)


def orbit_polyline(a, e, i_deg, Om_deg, w_deg, n=361):
    """整条椭圆轨道的惯性系采样点列（画参考轨道线用）。

    做法：真近点角 ν 从 0° 到 360° 均匀取 n 个点，
    逐点调 elements_to_state 取位置部分。
    返回 list[(x, y, z)]（km，惯性系）。
    """
    pts = []
    for k in range(n):
        nu = 360.0 * k / (n - 1)
        r, _v = elements_to_state(a, e, i_deg, Om_deg, w_deg, nu)
        pts.append((r[0], r[1], r[2]))
    return pts


def perigee_dir(i_deg, Om_deg, w_deg):
    """近地点方向单位矢量 = R3(-Ω)R1(-i)R3(-ω)·(1,0,0)（旋转矩阵第 1 列）。

    分量：(cosΩcosω - sinΩsinωcosi,  sinΩcosω + cosΩsinωcosi,  sinωsini)
    """
    R = _pqw_to_ijk_matrix(i_deg, Om_deg, w_deg)
    return (R[0][0], R[1][0], R[2][0])


def node_dir(Om_deg):
    """升交线方向单位矢量 (cosΩ, sinΩ, 0)——轨道面与赤道面交线指向升交点。"""
    Om = math.radians(Om_deg)
    return (math.cos(Om), math.sin(Om), 0.0)


def angle_arc(u1, u2, radius, n=64):
    """两个单位矢量 u1→u2 之间、在它们张成平面内的圆弧采样点列。

    球面线性插值（slerp）公式：
      θ = arccos(u1·u2)（两矢量夹角）
      q(t) = u1·sin((1-t)θ)/sinθ + u2·sin(tθ)/sinθ，t ∈ [0,1]
      采样点 P(t) = radius·q(t)
    原理：q(t) 恒为单位矢量且始终位于 u1/u2 张成平面内，角速度均匀——
      正是球面大圆弧（这里用于画 i/Ω/ω/ν 的角度弧标记）。
    退化：θ≈0 时两方向重合，返回 radius·u1 的重复点列。
    """
    dot = u1[0] * u2[0] + u1[1] * u2[1] + u1[2] * u2[2]
    th = math.acos(max(-1.0, min(1.0, dot)))
    if th < 1e-9:
        return [(radius * u1[0], radius * u1[1], radius * u1[2])] * n
    sth = math.sin(th)
    pts = []
    for k in range(n):
        t = k / (n - 1)
        c1 = math.sin((1.0 - t) * th) / sth
        c2 = math.sin(t * th) / sth
        pts.append((radius * (c1 * u1[0] + c2 * u2[0]),
                    radius * (c1 * u1[1] + c2 * u2[1]),
                    radius * (c1 * u1[2] + c2 * u2[2])))
    return pts


def kepler_pos_at(a, e, i, Om, w, M0_deg, jd0, jd, mu=MU_EARTH):
    """给定历元平近点角 M0（度）@ jd0，开普勒传播到 jd 的惯性系位置。

    步骤/公式：
      平均角速度 n = √(μ/a³)  [rad/s]
      平近点角  M = M0 + n·(jd-jd0)·86400   （M 随时间线性增长）
      开普勒方程 E - e·sinE = M
        牛顿迭代：E ← E - (E - e·sinE - M)/(1 - e·cosE)，初值 e<0.8 取 M 否则 π
      真近点角 ν = 2·atan2(√(1+e)·sin(E/2), √(1-e)·cos(E/2))
      位置 = elements_to_state(a,e,i,Ω,ω,ν) 的位置部分。
    返回 r[3]（km，惯性系）。
    """
    n = math.sqrt(mu / a ** 3)                          # rad/s
    M = math.radians(M0_deg) + n * (jd - jd0) * 86400.0
    M = math.fmod(M, 2.0 * math.pi)
    E = M if e < 0.8 else math.pi                       # 牛顿迭代初值
    for _ in range(50):
        dE = (E - e * math.sin(E) - M) / (1.0 - e * math.cos(E))
        E -= dE
        if abs(dE) < 1e-12:
            break
    nu = 2.0 * math.atan2(math.sqrt(1.0 + e) * math.sin(E / 2.0),
                          math.sqrt(1.0 - e) * math.cos(E / 2.0))
    nu_deg = math.degrees(nu) % 360.0
    r, _v = elements_to_state(a, e, i, Om, w, nu_deg, mu)
    return r
