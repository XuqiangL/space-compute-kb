"""geometry3d.py - OrbitLab 几何采样层：纯几何计算，不 import tkinter。

职责：把轨道六根数翻译成 3D 折线/点列（单位 km，地心 J2000 赤道惯性系），
供 render3d 投影绘制。所有函数零副作用，只返回点或折线列表。
"""
import math

RE_EARTH = 6378.1363  # 地球赤道半径 km（与 constants.py 同值；此处重定义避免循环依赖）


def _pqw(i_deg, Om_deg, w_deg):
    """PQW 基矢量（轨道面坐标系 → 惯性系旋转矩阵的三列）。

    P = 近地点方向单位矢量；Q = 轨道面内真近点角 90° 方向；W = 轨道角动量方向。
    公式（经典 PQW→IJK 旋转，Vallado §2.4）：
        Px = cosΩ·cosω − sinΩ·sinω·cosi   Qx = −cosΩ·sinω − sinΩ·cosω·cosi
        Py = sinΩ·cosω + cosΩ·sinω·cosi   Qy = −sinΩ·sinω + cosΩ·cosω·cosi
        Pz = sinω·sini                    Qz =  cosω·sini
        W  = P × Q = (sinΩ·sini, −cosΩ·sini, cosi)
    轨道面内任意点：r(ν) = r·(cosν·P + sinν·Q)。
    """
    i, Om, w = math.radians(i_deg), math.radians(Om_deg), math.radians(w_deg)
    ci, si = math.cos(i), math.sin(i)
    cO, sO = math.cos(Om), math.sin(Om)
    cw, sw = math.cos(w), math.sin(w)
    P = (cO * cw - sO * sw * ci, sO * cw + cO * sw * ci, sw * si)
    Q = (-cO * sw - sO * cw * ci, -sO * sw + cO * cw * ci, cw * si)
    W = (sO * si, -cO * si, ci)
    return P, Q, W


def _ring(center, u, v, radius, n_seg):
    """在 (u,v) 张成的平面内、以 center 为圆心采样闭合圆环折线（n_seg+1 点）。"""
    pts = []
    for k in range(n_seg + 1):
        t = 2.0 * math.pi * k / n_seg
        c, s = math.cos(t), math.sin(t)
        pts.append((center[0] + radius * (c * u[0] + s * v[0]),
                    center[1] + radius * (c * u[1] + s * v[1]),
                    center[2] + radius * (c * u[2] + s * v[2])))
    return pts


def orbit_plane_disc(a, e, i_deg, Om_deg, w_deg, n_rings=3, n_seg=72):
    """轨道面可视化圆盘：以地心（轨道焦点）为中心、半径 R = 1.15·a·(1+e) 的
    n_rings 个同心圆环 + 8 条径向辐条，全部位于轨道面（P,Q 平面）内。
    1.15·a·(1+e) 保证圆盘略大于远地点，能完整托住整条椭圆轨道。
    返回折线列表 [polyline, ...]。
    """
    P, Q, _ = _pqw(i_deg, Om_deg, w_deg)
    R = 1.15 * a * (1.0 + e)
    O = (0.0, 0.0, 0.0)
    lines = []
    for k in range(1, n_rings + 1):            # 同心圆环，半径均分
        lines.append(_ring(O, P, Q, R * k / n_rings, n_seg))
    for j in range(8):                          # 8 条径向辐条，每 45° 一条
        t = math.pi * j / 4.0
        c, s = math.cos(t), math.sin(t)
        lines.append([O, (R * (c * P[0] + s * Q[0]),
                          R * (c * P[1] + s * Q[1]),
                          R * (c * P[2] + s * Q[2]))])
    return lines


def equator_disc(radius, n_rings=3, n_seg=72):
    """赤道面（惯性系 XY 平面）同心圆环网格：半径从 RE_EARTH 到 radius 均分。"""
    X, Y = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)
    O = (0.0, 0.0, 0.0)
    return [_ring(O, X, Y, RE_EARTH + (radius - RE_EARTH) * k / n_rings, n_seg)
            for k in range(1, n_rings + 1)]


def orbit_plane_ring(a, e, i_deg, Om_deg, w_deg, n_seg=96):
    """轨道面圆盘**外环**点列（供 render3d.draw_filled_disc 半透明填充）。

    半径与 orbit_plane_disc 一致：R = 1.15·a·(1+e)，圆心在地心（轨道焦点）。
    """
    P, Q, _ = _pqw(i_deg, Om_deg, w_deg)
    return _ring((0.0, 0.0, 0.0), P, Q, 1.15 * a * (1.0 + e), n_seg)


def equator_ring(radius, n_seg=96):
    """赤道面圆盘外环点列（惯性系 XY 平面，供半透明填充）。"""
    return _ring((0.0, 0.0, 0.0), (1.0, 0.0, 0.0), (0.0, 1.0, 0.0),
                 radius, n_seg)

def _slerp(u1, u2, t):
    """球面线性插值（两单位矢量间的大圆弧）：
        u(t) = [sin((1−t)·θ)·u1 + sin(t·θ)·u2] / sinθ，θ = arccos(u1·u2)，t∈[0,1]
    两矢量几乎同向时 sinθ→0，退化为直接返回 u1 避免除零。
    """
    d = max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1] + u1[2] * u2[2]))
    th = math.acos(d)
    if th < 1e-12:
        return u1
    s = math.sin(th)
    a1 = math.sin((1.0 - t) * th) / s
    a2 = math.sin(t * th) / s
    return (a1 * u1[0] + a2 * u2[0],
            a1 * u1[1] + a2 * u2[1],
            a1 * u1[2] + a2 * u2[2])


def _arc(u1, u2, radius, n=48):
    """两单位矢量之间、给定半径的圆弧点列（slerp 采样 n+1 点）。"""
    return [tuple(radius * c for c in _slerp(u1, u2, k / n)) for k in range(n + 1)]


def angle_arcs(a, e, i_deg, Om_deg, w_deg, nu_deg):
    """4 条教学角度弧（每条是 3D 点列），弧半径取 0.25·a 量级并随轨道大小自适应。

    返回 dict(i=..., Om=..., w=..., nu=...)：
      'i'  倾角弧：在升交点处，从赤道面法线 Z 转向轨道角动量方向 h（=W）。
           i = arccos(hz/|h|) = arccos(W·Z)；Z 与 W 张成的平面 ⊥ 升交线，
           所以弧正好立在升交点上空。
      'Om' 升交点赤经弧：赤道面内从 X 轴（春分点）到升交线方向 N。
      'w'  近地点幅角弧：轨道面内从升交线 N 到近地点方向 P。
      'nu' 真近点角弧：轨道面内从近地点方向 P 到卫星当前方向 r̂ = cosν·P + sinν·Q。
    退化情形（对应弧返回空列表）：
      i = 0：轨道面与赤道面重合，升交线无定义 → 'i'、'Om'、'w' 弧为空；
      e = 0：圆轨道近地点无定义 → 'w'、'nu' 弧为空（nu 从近地点量起）。
    """
    P, Q, W = _pqw(i_deg, Om_deg, w_deg)
    Z = (0.0, 0.0, 1.0)
    X = (1.0, 0.0, 0.0)
    N = (math.cos(math.radians(Om_deg)), math.sin(math.radians(Om_deg)), 0.0)
    r1, r2 = 0.25 * a, 0.30 * a   # i/Ω 弧与 ω/ν 弧错开半径，避免视觉重叠
    arcs = {'i': [], 'Om': [], 'w': [], 'nu': []}
    if abs(i_deg) > 1e-9:
        arcs['i'] = _arc(Z, W, r1)
        arcs['Om'] = _arc(X, N, r1)
        if e > 1e-9:
            arcs['w'] = _arc(N, P, r2)
    if e > 1e-9:
        nu = math.radians(nu_deg)
        sat = (math.cos(nu) * P[0] + math.sin(nu) * Q[0],
               math.cos(nu) * P[1] + math.sin(nu) * Q[1],
               math.cos(nu) * P[2] + math.sin(nu) * Q[2])
        arcs['nu'] = _arc(P, sat, r2)
    return arcs


def all_angle_arcs(a, e, i_deg, Om_deg, w_deg, nu_deg, scale=None):
    """ARCHITECTURE.md §5 契约别名：等价 angle_arcs（弧半径已随 a 自适应，scale 忽略）。"""
    return angle_arcs(a, e, i_deg, Om_deg, w_deg, nu_deg)


def axes_lines(L):
    """惯性坐标轴 X/Y/Z 三条线段（原点 → L），返回 dict(X=..., Y=..., Z=...)。"""
    O = (0.0, 0.0, 0.0)
    return {'X': [O, (L, 0.0, 0.0)],
            'Y': [O, (0.0, L, 0.0)],
            'Z': [O, (0.0, 0.0, L)]}


def vernal_equinox_line(L):
    """春分点方向线（X 轴延长线，供虚线绘制）。"""
    return [(0.0, 0.0, 0.0), (L, 0.0, 0.0)]
