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

    def earth_occluded(self, p):
        """点 p 是否被地球遮挡（射线-球体求交，教学级精确遮挡）。

        原理：从相机 C 向 p 发射线，若射线在到达 p 之前先击中地球球体
        （球心 O 为原点、半径 RE），则 p 被地球挡住。
        公式：u = (p−C)/|p−C|；t_ca = (O−C)·u（球心在射线上的投影距离）；
        d² = |O−C|² − t_ca²（球心到射线的垂直距离²）；
        d² > RE² → 射线与球不相交；否则近侧交点 t_hit = t_ca − √(RE²−d²)，
        0 < t_hit < |p−C| → 遮挡。
        """
        (cx, cy, cz), _, _, _ = self._basis()
        dx, dy, dz = p[0] - cx, p[1] - cy, p[2] - cz
        dist = math.sqrt(dx * dx + dy * dy + dz * dz)
        if dist < 1e-12:
            return False
        ux, uy, uz = dx / dist, dy / dist, dz / dist
        # O − C = (−cx, −cy, −cz)
        t_ca = -(cx * ux + cy * uy + cz * uz)
        if t_ca < 0.0:
            return False                      # 地球在相机视线反方向
        oc2 = cx * cx + cy * cy + cz * cz
        d2 = oc2 - t_ca * t_ca
        re2 = RE_EARTH * RE_EARTH
        if d2 > re2:
            return False                      # 射线从地球旁掠过
        t_hit = t_ca - math.sqrt(re2 - d2)    # 球体近侧交点
        return 0.0 < t_hit < dist             # 交点在 p 之前 → p 被遮挡

def draw_polylines(canvas, cam, lines, w, h, color, width=1, dash=None,
                   occlude=False):
    """批量画 3D 折线：逐点投影后 canvas.create_line；
    被相机裁掉（投影返回 None）的点处断线，自动分段处理。
    occlude=True 时，被地球遮挡的点同样断线——轨道/轨迹在地球背面
    的部分不再"透视"显示（修复卫星看似在地球里面的问题）。"""
    for line in lines:
        seg = []
        for p in line:
            pr = cam.project(p, w, h)
            if pr is None or (occlude and cam.earth_occluded(p)):
                if len(seg) >= 4:               # 至少 2 个屏幕点（4 个坐标）
                    canvas.create_line(*seg, fill=color, width=width, dash=dash)
                seg = []
            else:
                seg.append(pr[0])
                seg.append(pr[1])
        if len(seg) >= 4:
            canvas.create_line(*seg, fill=color, width=width, dash=dash)


def draw_earth(canvas, cam, w, h, jd, rotate_on=True, texture=None,
               img_holder=None):
    """绘制地球：世界地图贴图球（优先）或蓝色球兜底 + 经纬网 + 极点标记。

    ① 贴图球：EarthTexture.render_photo 按当前相机基矢量与 GMST 渲染
       RGBA 球面图（圆盘外透明），create_image 放在地心投影处。
       物理意义：纹理随 GMST 旋转 = 地固系相对 J2000 惯性系的自转，
       用户可直接看到本初子午线相对春分点方向（X 轴）的方位。
    ② 兜底蓝球：投影地心得 (sx, sy, zc)，屏幕半径 R_px = f·RE/zc
       （与点投影 sx = w/2 + f·xc/zc 同源：半径同样按 1/zc 缩放）。
    ③ 经纬网：地固系经度 λ、纬度 φ 的点在惯性系中的坐标为
       r = RE·(cosφ·cos(λ+θ), cosφ·sin(λ+θ), sinφ)，θ = GMST(jd)。
    ④ 极点标记 N/S（极点在自转轴上，不受 GMST 影响）。
    """
    c = cam.project((0.0, 0.0, 0.0), w, h)
    if c is None:
        return
    sx, sy, zc = c
    r_px = cam.f * RE_EARTH / zc
    img = None
    if texture is not None and texture.available:
        img = texture.render_photo(cam, jd, r_px)
    if img is not None:
        # 贴图球（带透明通道，不遮挡背后轨道线）；holder 持有引用防 GC
        canvas.create_image(sx, sy, image=img)
        if img_holder is not None:
            img_holder.append(img)
    else:
        canvas.create_oval(sx - r_px, sy - r_px, sx + r_px, sy + r_px,
                           fill='#1a4d8f', outline='')
    # 地球边缘高亮圈（大气层亮环）：让轨道与地球的分界一眼可辨
    canvas.create_oval(sx - r_px, sy - r_px, sx + r_px, sy + r_px,
                       fill='', outline='#7fd4ff', width=2)
    canvas.create_oval(sx - r_px - 3, sy - r_px - 3, sx + r_px + 3,
                       sy + r_px + 3, fill='', outline='#2a5a8f', width=1)
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


def draw_marker(canvas, cam, p, w, h, color, label, size=4, occlude=False):
    """画圆点 + 文字标签（点在相机后方或被地球遮挡则不画）。"""
    if occlude and cam.earth_occluded(p):
        return
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


def draw_filled_disc(canvas, cam, ring_pts, w, h, color, stipple='gray25'):
    """半透明圆盘填充（轨道面/赤道面着色，教学上确认"面"的几何）。

    tkinter 无 alpha 通道填充，用 stipple 抖动图案模拟半透明：
    'gray25' = 25% 像素着色，底下场景隐约透出，视觉上即"透明色盘面"。
    ring_pts：圆盘外环 3D 点列（闭合前采样），投影为多边形。
    任一点在相机后方则放弃填充（退化情形，网格线仍照常绘制）。
    """
    pts = []
    for p in ring_pts:
        pr = cam.project(p, w, h)
        if pr is None:
            return
        pts += [pr[0], pr[1]]
    if len(pts) >= 6:
        canvas.create_polygon(*pts, fill=color, outline='',
                              stipple=stipple)
