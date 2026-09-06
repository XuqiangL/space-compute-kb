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

def _arc_in_plane(u_start, u_perp, angle_rad, radius, n=48):
    """在 (u_start, u_perp) 张成的平面内、从 u_start 扫 angle_rad 的圆弧采样。

    公式：p(t) = radius·(cos t·u_start + sin t·u_perp)，t ∈ [0, angle_rad]
    u_perp 必须 ⊥ u_start 且同为单位矢量（由调用方用平面法线叉积构造）。
    直接按角度采样——对任意扫角（含 180°/接近 360°）均无奇异，
    取代 slerp（slerp 在 u1≈−u2 时 sinθ→0 数值爆炸，已弃用）。
    """
    if abs(angle_rad) < 1e-12:
        return []
    steps = max(2, int(n * abs(angle_rad) / math.pi) + 1)   # 弧长正比点数
    pts = []
    for k in range(steps + 1):
        t = angle_rad * k / steps
        c, s = math.cos(t), math.sin(t)
        pts.append((radius * (c * u_start[0] + s * u_perp[0]),
                    radius * (c * u_start[1] + s * u_perp[1]),
                    radius * (c * u_start[2] + s * u_perp[2])))
    return pts


def _cross(a, b):
    """三维叉积 a×b。"""
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _normalize(v):
    n = math.sqrt(v[0] ** 2 + v[1] ** 2 + v[2] ** 2)
    if n < 1e-15:
        return None
    return (v[0] / n, v[1] / n, v[2] / n)


def angle_arcs(a, e, i_deg, Om_deg, w_deg, nu_deg):
    """4 条教学角度弧（每条是 3D 点列），全部按角度直接采样（无奇异）。

    弧半径：r = RE + k·(a − RE)（k=0.30/0.55）——弧始终浮在地球表面之上、
    轨道之下，任意轨道高度（LEO 仅 600 km 间隙）都清晰可见；
    角度定义点本就在地心附近，弧贴近地球在几何上也最自然。

    返回 dict(i=..., Om=..., w=..., nu=...)：
      'i'  倾角弧：在升交点处，从赤道面法线 Z 转向轨道角动量方向 W，
           采样平面 ⊥ 升交线 N，扫角 = i（i = arccos(W·Z)）。
      'Om' 升交点赤经弧：赤道面内从 X 轴（春分点）扫 Ω 到升交线 N。
      'w'  近地点幅角弧：轨道面内从升交线 N 扫 ω 到近地点方向 P。
      'nu' 真近点角弧：轨道面内从近地点 P 扫 ν 到卫星方向。
    退化情形（返回空列表）：i=0 时 'i'/'Om'/'w' 无定义；e=0 时 'w'/'nu' 无定义。
    """
    P, Q, W = _pqw(i_deg, Om_deg, w_deg)
    Z = (0.0, 0.0, 1.0)
    X, Y = (1.0, 0.0, 0.0), (0.0, 1.0, 0.0)
    N = (math.cos(math.radians(Om_deg)), math.sin(math.radians(Om_deg)), 0.0)
    gap = max(a - RE_EARTH, 0.05 * RE_EARTH)   # 轨道距地表间隙（兜底防负）
    r1 = RE_EARTH + 0.30 * gap                # i/Ω 弧半径
    r2 = RE_EARTH + 0.55 * gap                # ω/ν 弧半径（错开防视觉重叠）
    arcs = {'i': [], 'Om': [], 'w': [], 'nu': []}
    if abs(i_deg) > 1e-9:
        # i 弧：法线 = N；起始 Z；面内垂直方向 = N×Z 归一化（指向 W 一侧）
        zp = _normalize(_cross(N, Z))
        if zp is not None:
            # 保证 zp 指向 W 所在侧（点积为正），否则取反
            if zp[0] * W[0] + zp[1] * W[1] + zp[2] * W[2] < 0:
                zp = (-zp[0], -zp[1], -zp[2])
            arcs['i'] = _arc_in_plane(Z, zp, math.radians(i_deg), r1)
        # Ω 弧：赤道面内 X→N，垂直方向 = Y（Z×X = Y 保证扫向正确）
        arcs['Om'] = _arc_in_plane(X, Y, math.radians(Om_deg), r1)
        if e > 1e-9:
            # ω 弧：轨道面内 N→P，面内垂直方向 = W×N
            np_ = _normalize(_cross(W, N))
            if np_ is not None:
                arcs['w'] = _arc_in_plane(N, np_, math.radians(w_deg), r2)
    if e > 1e-9:
        # ν 弧：轨道面内 P→卫星方向，面内垂直方向即 Q，扫角 = ν
        arcs['nu'] = _arc_in_plane(P, Q, math.radians(nu_deg), r2)
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
