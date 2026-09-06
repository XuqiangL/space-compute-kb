"""main.py - OrbitLab 卫星轨道动力学教学仿真器 · 应用主程序

职责：组装三栏 UI（panels）+ 3D 视口（render3d/geometry3d）+ 物理内核
（elements/perturbations/propagator），驱动动画主循环。

核心设计（教学灵魂）——双轨显示：
  · 参考轨道：左栏六根数 → 开普勒椭圆解析采样（白色实线 + 青色轨道面）
  · 真实轨迹：Cowell 数值积分（含勾选摄动）的实际路径（黄色轨迹 + 红色卫星）
两者对比直观呈现"摄动如何使真实轨道偏离理想开普勒椭圆"。

坐标系：地心 J2000 赤道惯性系（X→春分点，Z→北极）；单位 km / km/s / s。
零依赖：纯 Python 标准库（tkinter + math）。
"""
import math
import time
import tkinter as tk
from datetime import datetime, timezone

from constants import (MU_EARTH, RE_EARTH, J2_EARTH, julian_date,
                       jd_to_datetime_str)
from elements import (elements_to_state, state_to_elements, orbit_polyline,
                      perigee_dir, node_dir)
from perturbations import PerturbConfig, j2_secular_rates, drag_da_dt_km_day
from propagator import Propagator
import geometry3d
import render3d
from groundtrack import GroundTrackCanvas, inertial_to_latlon
from panels import LeftPanel, RightPanel, BottomPanel

# ---- 视觉配色（与教学效果图一致） --------------------------------------------
C_BG       = "#0a0e1a"   # 深空黑背景
C_ORBIT    = "#ffffff"   # 参考轨道线：白
C_PLANE    = "#00bcd4"   # 轨道面：青
C_EQUATOR  = "#5a6270"   # 赤道面：灰
C_ARC_I    = "#4caf50"   # 倾角 i 弧：绿
C_ARC_OM   = "#9c27b0"   # 升交点赤经 Ω 弧：紫
C_ARC_W    = "#ff9800"   # 近地点幅角 ω 弧：橙
C_ARC_NU   = "#f44336"   # 真近点角 ν 弧：红
C_SAT      = "#ff5252"   # 卫星：红
C_TRAIL    = "#ffd54f"   # 真实轨迹：黄
C_AXIS     = {"X": "#ef5350", "Y": "#66bb6a", "Z": "#42a5f5"}  # 轴配色
C_VERNAL   = "#8e24aa"   # 春分点方向：紫虚线

MASS_KG = 150.0   # 卫星质量（算星一号级别，供 A/m 换算）


class OrbitLab:
    """应用主类：状态机 + 动画循环。

    状态机：
      参数变化 → 六根数转状态 → Propagator.reset → 重建参考几何 → 清轨迹
      播放中   → 数值积分推进 → 轨迹追加 → 反算 osculating 根数 → 右栏刷新
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("OrbitLab 卫星轨道动力学教学仿真器")
        self.root.configure(bg=C_BG)
        try:
            self.root.state("zoomed")     # Windows 最大化（面板较多，小屏会溢出）
        except tk.TclError:
            self.root.geometry("1500x900")

        # ---- 三栏布局 ------------------------------------------------------
        self.left = LeftPanel(self.root, self.on_params_changed)
        self.left.pack(side=tk.LEFT, fill=tk.Y)

        self.right = RightPanel(self.root)
        self.right.pack(side=tk.RIGHT, fill=tk.Y)

        self.bottom = BottomPanel(self.root, self.on_control)
        self.bottom.pack(side=tk.BOTTOM, fill=tk.X)

        # 中央 3D 视口
        self.canvas = tk.Canvas(self.root, bg=C_BG, highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # 星下点轨迹图挂载到右栏容器
        self.gt = GroundTrackCanvas(self.right.gt_frame)
        self.gt.pack(padx=6, pady=4)

        # ---- 相机与鼠标交互 -------------------------------------------------
        self.cam = render3d.Camera()
        self._mouse = None
        self.canvas.bind("<ButtonPress-1>", self._on_press)
        self.canvas.bind("<B1-Motion>", self._on_drag)          # 左键旋转
        self.canvas.bind("<ButtonPress-3>", self._on_press3)
        self.canvas.bind("<B3-Motion>", self._on_pan)           # 右键平移
        self.canvas.bind("<MouseWheel>", self._on_wheel)        # 滚轮缩放

        # ---- 仿真状态 -------------------------------------------------------
        self.playing = False
        self.speed = 60.0                 # 时间倍率（仿真秒/真实秒）
        now = datetime.now(timezone.utc)  # 历元对齐真实 UTC 时钟
        self.jd0 = julian_date(now.year, now.month, now.day,
                               now.hour, now.minute,
                               now.second + now.microsecond * 1e-6)
        self.elapsed_s = 0.0              # 已流逝仿真时间（秒）
        self.trail = []                   # 真实轨迹点列（惯性系）
        self.gt_points = []               # 星下点轨迹 [(lat, lon), ...]
        self.prop = None                  # Cowell 传播器
        self.ref_lines = []               # 参考轨道折线
        self.plane_lines = []             # 轨道面网格
        self.eq_lines = []                # 赤道面网格
        self.arcs = {}                    # 角度弧 dict
        self._fps_t = time.perf_counter()
        self._fps = 0.0

        self.on_params_changed()          # 初始构建
        # 演示/冒烟模式：ORBITLAB_AUTOPLAY=1 时自动以高倍率播放
        import os
        if os.environ.get("ORBITLAB_AUTOPLAY") == "1":
            self.playing = True
            self.speed = 3600.0
            self.bottom.set_playing(True)
        self._loop()

    # ------------------------------------------------------------------ 回调
    def on_params_changed(self):
        """左栏任何参数变化：重建参考轨道几何，卫星重置到新轨道 ν 处。"""
        el = self.left.get_elements()
        self.ref_el = el
        # 摄动配置：A/m（m²/kg）× 质量 = 面积（m²）
        p = self.left.get_perturb()
        cfg = PerturbConfig(
            use_j2=p["use_j2"], j2=p["j2"],
            use_drag=p["use_drag"], cd=p["cd"],
            drag_area_m2=p["drag_am"] * MASS_KG, mass_kg=MASS_KG,
            use_sun=p["use_sun"], use_moon=p["use_moon"],
            use_srp=p["use_srp"], cr=p["cr"],
            srp_area_m2=p["srp_am"] * MASS_KG)
        r, v = elements_to_state(el["a"], el["e"], el["i"], el["Om"],
                                 el["w"], el["nu"])
        self.prop = Propagator(cfg)
        self.prop.reset(r, v, self.jd0 + self.elapsed_s / 86400.0)
        self.trail = [tuple(r)]
        self.gt_points = []
        self._rebuild_geometry(el)
        self.bottom.set_progress(el["nu"])

    def on_control(self, cmd, value=None):
        """底栏时间轴控制：播放/暂停/单步/重置/速度。"""
        if cmd == "play":
            self.playing = True
        elif cmd == "pause":
            self.playing = False
        elif cmd == "step":               # 单步：推进 60 s × 当前倍率
            self._advance(60.0 * self.speed)
        elif cmd == "reset":              # 重置：回到滑块设定的初始状态
            self.elapsed_s = 0.0
            self.on_params_changed()
        elif cmd == "speed":
            self.speed = value
        self.bottom.set_playing(self.playing)

    # ------------------------------------------------------------------ 几何
    def _rebuild_geometry(self, el):
        """由当前六根数重建全部静态几何层（参考轨道/轨道面/赤道面/角度弧）。"""
        a, e = el["a"], el["e"]
        i, Om, w, nu = el["i"], el["Om"], el["w"], el["nu"]
        self.ref_lines = [orbit_polyline(a, e, i, Om, w)]
        R = max(a * (1.0 + e) * 1.15, RE_EARTH * 1.8)   # 盘面半径覆盖远地点
        self.plane_lines = geometry3d.orbit_plane_disc(a, e, i, Om, w)
        self.eq_lines = geometry3d.equator_disc(R)
        self.arcs = geometry3d.angle_arcs(a, e, i, Om, w, nu)
        self.axes = geometry3d.axes_lines(R * 1.1)
        self.vernal = geometry3d.vernal_equinox_line(R * 1.25)
        # 近/远地点三维位置（近地点 = P·a(1−e)，远地点 = −P·a(1+e)）
        P = perigee_dir(i, Om, w)
        self.r_peri = tuple(P[k] * a * (1.0 - e) for k in range(3))
        self.r_apo = tuple(-P[k] * a * (1.0 + e) for k in range(3))
        # 相机距离自适应轨道尺度
        self.cam.dist = max(3.0 * a * (1.0 + e), 15000.0)

    # ------------------------------------------------------------------ 推进
    def _advance(self, dt_sim_s):
        """数值传播 dt_sim_s 秒，并追加轨迹/星下点（抽稀控制点数）。"""
        self.prop.step(dt_sim_s)
        self.elapsed_s += dt_sim_s
        r = self.prop.state[:3]
        if len(self.trail) == 0 or self._dist(self.trail[-1], r) > \
                max(self.ref_el["a"] * 0.002, 5.0):     # 空间抽稀
            self.trail.append(tuple(r))
            if len(self.trail) > 4000:                  # 点数上限防卡顿
                self.trail = self.trail[-3000:]
            lat, lon, _ = inertial_to_latlon(r, self.prop.jd)
            self.gt_points.append((lat, lon))
            if len(self.gt_points) > 3000:
                self.gt_points = self.gt_points[-2000:]

    @staticmethod
    def _dist(p, q):
        return math.sqrt(sum((p[k] - q[k]) ** 2 for k in range(3)))

    # ------------------------------------------------------------------ 主循环
    def _loop(self):
        t0 = time.perf_counter()
        if self.playing:
            dt_wall = min(t0 - self._fps_t, 0.25)     # 防卡顿后跳变
            self._advance(dt_wall * self.speed)
        # FPS（滑动平均）
        dt = t0 - self._fps_t
        self._fps_t = t0
        if dt > 0:
            self._fps = 0.9 * self._fps + 0.1 * (1.0 / dt)
        self._draw()
        self._update_panels()
        self.root.after(33, self._loop)               # ~30 FPS

    # ------------------------------------------------------------------ 绘制
    def _draw(self):
        c = self.canvas
        c.delete("all")
        w = max(c.winfo_width(), 400)
        h = max(c.winfo_height(), 300)
        disp = self.left.get_display()
        cam = self.cam

        if disp["equator_plane"]:
            render3d.draw_polylines(c, cam, self.eq_lines, w, h,
                                    C_EQUATOR, width=1)
        if disp["orbit_plane"]:
            render3d.draw_polylines(c, cam, self.plane_lines, w, h,
                                    C_PLANE, width=1)
        if disp["axes"]:
            for name, line in self.axes.items():
                render3d.draw_polylines(c, cam, [line], w, h,
                                        C_AXIS[name], width=2)
                render3d.draw_marker(c, cam, line[-1], w, h,
                                     C_AXIS[name], name, size=3)
        if disp["vernal"]:
            render3d.draw_dashed_line3d(c, cam, self.vernal[0],
                                        self.vernal[1], w, h, C_VERNAL)
            render3d.draw_marker(c, cam, self.vernal[-1], w, h,
                                 C_VERNAL, "春分点 ♈", size=3)
        # 地球（含经纬网自转）
        render3d.draw_earth(c, cam, w, h, self.prop.jd,
                            rotate_on=disp["earth_spin"])
        # 参考轨道（开普勒椭圆）
        if disp["ref_orbit"]:
            render3d.draw_polylines(c, cam, self.ref_lines, w, h,
                                    C_ORBIT, width=2)
        # 近/远地点标记
        render3d.draw_marker(c, cam, self.r_peri, w, h, "#80deea",
                             "近地点", size=4)
        render3d.draw_marker(c, cam, self.r_apo, w, h, "#b0bec5",
                             "远地点", size=4)
        # 角度弧（i/Ω/ω/ν 教学核心）
        if disp["arcs"]:
            for key, color, label in (("i", C_ARC_I, "i"),
                                      ("Om", C_ARC_OM, "Ω"),
                                      ("w", C_ARC_W, "ω"),
                                      ("nu", C_ARC_NU, "ν")):
                arc = self.arcs.get(key) or []
                if len(arc) >= 2:
                    render3d.draw_polylines(c, cam, [arc], w, h,
                                            color, width=3)
                    mid = arc[len(arc) // 2]
                    render3d.draw_marker(c, cam, mid, w, h, color,
                                         label, size=2)
        # 真实轨迹（摄动传播的实际路径）
        if disp["trail"] and len(self.trail) >= 2:
            render3d.draw_polylines(c, cam, [self.trail], w, h,
                                    C_TRAIL, width=1)
        # 卫星当前位置
        render3d.draw_marker(c, cam, tuple(self.prop.state[:3]), w, h,
                             C_SAT, "卫星", size=6)

    def _update_panels(self):
        """右栏数据 + 底栏时钟刷新（每帧）。"""
        r = self.prop.state[:3]
        v = self.prop.state[3:]
        osc = state_to_elements(r, v)
        p = self.left.get_perturb()
        if p["use_j2"]:
            dOm, dw, dM = j2_secular_rates(osc["a"], osc["e"],
                                           osc["i"], p["j2"])
        else:
            dOm = dw = dM = None
        da_dt = (drag_da_dt_km_day(osc["a"], osc["e"],
                                   self.prop.cfg, self.prop.jd)
                 if p["use_drag"] else None)
        latlon = inertial_to_latlon(r, self.prop.jd)
        jd_str = jd_to_datetime_str(self.prop.jd)
        self.right.update_data(osc, dict(dOm=dOm, dw=dw, dM=dM,
                                         da_dt=da_dt),
                               latlon, jd_str, self._fps)
        self.bottom.set_time(jd_str, self.elapsed_s / 86400.0)
        self.bottom.set_progress(osc["nu"])
        self.gt.set_track(self.gt_points, (latlon[0], latlon[1]))

    # ------------------------------------------------------------------ 鼠标
    def _on_press(self, ev):
        self._mouse = (ev.x, ev.y)

    def _on_press3(self, ev):
        self._mouse = (ev.x, ev.y)

    def _on_drag(self, ev):
        if self._mouse:
            self.cam.rotate((ev.x - self._mouse[0]) * 0.4,
                            (ev.y - self._mouse[1]) * 0.4)
            self._mouse = (ev.x, ev.y)

    def _on_pan(self, ev):
        if self._mouse:
            w = max(self.canvas.winfo_width(), 400)
            h = max(self.canvas.winfo_height(), 300)
            self.cam.pan(ev.x - self._mouse[0], ev.y - self._mouse[1], w, h)
            self._mouse = (ev.x, ev.y)

    def _on_wheel(self, ev):
        self.cam.zoom(0.9 if ev.delta > 0 else 1.1)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    OrbitLab().run()
