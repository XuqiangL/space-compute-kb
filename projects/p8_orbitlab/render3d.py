"""render3d.py - OrbitLab 3D 渲染层：相机 + 透视投影 + 地球/折线/标记绘制。

坐标系：地心 J2000 赤道惯性系（X→春分点，Z→北极），单位 km。
相机算法沿用 p7_solarsim：球坐标（方位角/仰角/距离）绕目标点 + 针孔透视投影。
"""
import math

from constants import RE_EARTH, gmst_rad   # 单一数据源：GMAT 常量与时间系统


class Camera:
    """球坐标相机：方位角 az / 仰角 el / 距离 dist / 目标点 target / 焦距 f。

    透视投影（针孔模型）：把世界点 p 换到相机坐标系 (xc, yc, zc)
    （zc = 沿视线方向的深度，xc/yc = 相机右/上方向分量），则
        sx = w/2 + f·xc/zc，  sy = h/2 − f·yc/zc
    即“近大远小”：屏幕偏移与深度 zc 成反比。zc ≤ 0 的点在相机后方，返回 None。
    """

    def __init__(self):
        self.az = math.radians(-90.0)     # 方位角
        self.el = math.radians(25.0)      # 仰角
        self.dist = 30000.0               # 到目标点距离 km
        self.target = [0.0, 0.0, 0.0]     # 观察目标点
        self.f = 600.0                    # 焦距（像素）

    def _basis(self):
        """相机位置 + 右/上/前三个正交基矢量（世界系表示）。"""
        ca, sa = math.cos(self.az), math.sin(self.az)
        ce, se = math.cos(self.el), math.sin(self.el)
        # 相机位于目标点周围的球面上
        cx = self.target[0] + self.dist * ce * ca
        cy = self.target[1] + self.dist * ce * sa
        cz = self.target[2] + self.dist * se
        # forward = 相机 → 目标
        fx, fy, fz = (self.target[0] - cx, self.target[1] - cy,
                      self.target[2] - cz)
        fn = math.sqrt(fx * fx + fy * fy + fz * fz)
        fx, fy, fz = fx / fn, fy / fn, fz / fn
        # right = forward × 世界上方向 Z（视线与 Z 平行退化时取 X）
        rx, ry, rz = fy, -fx, 0.0
        rn = math.sqrt(rx * rx + ry * ry + rz * rz)
        if rn < 1e-9:
            rx, ry, rz, rn = 1.0, 0.0, 0.0, 1.0
        rx, ry, rz = rx / rn, ry / rn, rz / rn
        # up = right × forward
        ux = ry * fz - rz * fy
        uy = rz * fx - rx * fz
        uz = rx * fy - ry * fx
        return (cx, cy, cz), (rx, ry, rz), (ux, uy, uz), (fx, fy, fz)

    def project(self, p, w, h):
        """世界点 → (sx, sy, depth)；相机后方（zc≤0）返回 None。"""
        (cx, cy, cz), (rx, ry, rz), (ux, uy, uz), (fx, fy, fz) = self._basis()
        dx, dy, dz = p[0] - cx, p[1] - cy, p[2] - cz
        zc = dx * fx + dy * fy + dz * fz
        if zc <= 1e-6:
            return None
        xc = dx * rx + dy * ry + dz * rz
        yc = dx * ux + dy * uy + dz * uz
        return w * 0.5 + self.f * xc / zc, h * 0.5 - self.f * yc / zc, zc

    def rotate(self, daz_deg, del_deg):
        """拖拽旋转：方位角/仰角增量（度），仰角限制 ±89° 防万向锁。"""
        self.az += math.radians(daz_deg)
        self.el = max(math.radians(-89.0),
                      min(math.radians(89.0), self.el + math.radians(del_deg)))

    def zoom(self, factor):
        """滚轮缩放：dist ×= factor，限制 8000 ~ 5e8 km（近看地球，远看 GEO/月球轨道）。"""
        self.dist = max(8000.0, min(5e8, self.dist * factor))

    def pan(self, dx_px, dy_px, w, h):
        """平移：屏幕像素位移换算成目标点在 right/up 平面内的世界位移，
        比例 scale = dist/f（1 像素对应的世界长度随距离线性增长）。"""
        _, (rx, ry, rz), (ux, uy, uz), _ = self._basis()
        scale = self.dist / self.f
        self.target[0] += (-dx_px * scale) * rx + (dy_px * scale) * ux
        self.target[1] += (-dx_px * scale) * ry + (dy_px * scale) * uy
        self.target[2] += (-dx_px * scale) * rz + (dy_px * scale) * uz

def draw_polylines(canvas, cam, lines, w, h, color, width=1, dash=None):
    """批量画 3D 折线：逐点投影后 canvas.create_line；
    被相机裁掉（投影返回 None）的点处断线，自动分段处理。"""
    for line in lines:
        seg = []
        for p in line:
            pr = cam.project(p, w, h)
            if pr is None:                      # 相机后方 → 结束当前段
                if len(seg) >= 4:               # 至少 2 个屏幕点（4 个坐标）
                    canvas.create_line(*seg, fill=color, width=width, dash=dash)
                seg = []
            else:
                seg.append(pr[0])
                seg.append(pr[1])
        if len(seg) >= 4:
            canvas.create_line(*seg, fill=color, width=width, dash=dash)


def draw_earth(canvas, cam, w, h, jd, rotate_on=True):
    """绘制地球：蓝色球体 + 随 GMST 自转的经纬网 + 极点标记。

    ① 球体：投影地心得 (sx, sy, zc)，屏幕半径 R_px = f·RE/zc
       （与点投影 sx = w/2 + f·xc/zc 同源：半径也是长度，同样按 1/zc 缩放）。
    ② 经纬网：地固系经度 λ、纬度 φ 的点在惯性系中的坐标为
       r = RE·(cosφ·cos(λ+θ), cosφ·sin(λ+θ), sinφ)，θ = GMST(jd)
       —— 地球自转 = 地固系相对惯性系绕 Z 轴转 GMST 角。
       赤道圆 + ±30°/±60° 纬线圈 + 6 条经线圈（0/60/…/300°）。
    ③ 极点标记 N/S（极点在自转轴上，不受 GMST 影响）。
    """
    c = cam.project((0.0, 0.0, 0.0), w, h)
    if c is None:
        return
    sx, sy, zc = c
    r_px = cam.f * RE_EARTH / zc
    canvas.create_oval(sx - r_px, sy - r_px, sx + r_px, sy + r_px,
                       fill='#1a4d8f', outline='#4da6ff')
    th = gmst_rad(jd) if rotate_on else 0.0
    lines = []
    n = 72
    for phi_deg in (0.0, 30.0, -30.0, 60.0, -60.0):       # 纬线圈
        phi = math.radians(phi_deg)
        cp, sp = math.cos(phi), math.sin(phi)
        pts = []
        for k in range(n + 1):
            lam = 2.0 * math.pi * k / n + th
            pts.append((RE_EARTH * cp * math.cos(lam),
                        RE_EARTH * cp * math.sin(lam),
                        RE_EARTH * sp))
        lines.append(pts)
    for lam0_deg in (0.0, 60.0, 120.0, 180.0, 240.0, 300.0):  # 经线圈（完整大圆）
        lam0 = math.radians(lam0_deg) + th
        cl, sl = math.cos(lam0), math.sin(lam0)
        pts = []
        for k in range(n + 1):
            t = 2.0 * math.pi * k / n
            pts.append((RE_EARTH * math.cos(t) * cl,
                        RE_EARTH * math.cos(t) * sl,
                        RE_EARTH * math.sin(t)))
        lines.append(pts)
    draw_polylines(canvas, cam, lines, w, h, '#2a6db5')
    for p, t in (((0.0, 0.0, RE_EARTH), 'N'), ((0.0, 0.0, -RE_EARTH), 'S')):
        pr = cam.project(p, w, h)
        if pr is not None:
            canvas.create_text(pr[0], pr[1], text=t, fill='#9fd0ff',
                               font=('', 9, 'bold'))


def draw_marker(canvas, cam, p, w, h, color, label, size=4):
    """画圆点 + 文字标签（点在相机后方则不画）。"""
    pr = cam.project(p, w, h)
    if pr is None:
        return
    sx, sy = pr[0], pr[1]
    canvas.create_oval(sx - size, sy - size, sx + size, sy + size,
                       fill=color, outline='')
    if label:
        canvas.create_text(sx + size + 4, sy - size - 4, text=label,
                           fill=color, anchor='w')


def draw_dashed_line3d(canvas, cam, p1, p2, w, h, color, dash=(4, 4)):
    """两点间 3D 虚线（任一端在相机后方则不画）。"""
    a = cam.project(p1, w, h)
    b = cam.project(p2, w, h)
    if a is None or b is None:
        return
    canvas.create_line(a[0], a[1], b[0], b[1], fill=color, dash=dash)
