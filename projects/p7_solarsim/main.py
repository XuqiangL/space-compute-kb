# -*- coding: utf-8 -*-
"""main.py - 1:1 Solar System orbital simulator (stdlib only).

Real-time synced to wall clock via Julian Date. Two-body Kepler mechanics,
JPL approximate elements, Hohmann transfer designer with launch windows.

Run:  py main.py
"""
import math
import time
import tkinter as tk
from tkinter import ttk

from kepler import (AU_KM, jd_now, jd_of_ymd, datetime_of_jd,
                    period_days, orbital_velocity_kms)
from ephemeris import (PLANETS, CN, planet_state,
                       planet_elements_for_display, moon_state_helio)
from transfer import (hohmann, required_phase_deg, current_phase_deg,
                      wait_days, transfer_elements, transfer_pos_at,
                      miss_distance_km, synodic_days)
from render3d import Camera

BODY_ORDER = ["Mercury", "Venus", "Earth", "Mars", "Jupiter",
              "Saturn", "Uranus", "Neptune", "Pluto"]
SIZE_PX = {"Mercury": 4, "Venus": 6, "Earth": 7, "Mars": 5, "Jupiter": 12,
           "Saturn": 11, "Uranus": 8, "Neptune": 8, "Pluto": 3,
           "Sun": 16, "Moon": 3}
SPEED_STEPS = [("实时 1:1", None), ("暂停", 0.0), ("×60", 60.0 / 86400.0),
               ("×1小时/秒", 3600.0 / 86400.0),
               ("×1天/秒", 1.0), ("×10天/秒", 10.0),
               ("×100天/秒", 100.0), ("倒放-1天/秒", -1.0)]


class Spacecraft:
    """Hohmann transfer vehicle: parks at departure until jd_dep, flies
    the transfer ellipse, then rides the arrival body."""
    def __init__(self, dep, arr, a_t, e_t, wbar, M0, jd_dep, jd_arr):
        self.dep, self.arr = dep, arr
        self.a_t, self.e_t = a_t, e_t
        self.wbar, self.M0 = wbar, M0
        self.jd_dep, self.jd_arr = jd_dep, jd_arr
        self.trail = []

    def status(self, jd):
        if jd < self.jd_dep:
            return "waiting"
        if jd < self.jd_arr:
            return "cruise"
        return "arrived"

    def pos_at(self, jd):
        st = self.status(jd)
        if st == "waiting":
            return planet_state(self.dep, jd)[0]
        if st == "arrived":
            return planet_state(self.arr, jd)[0]
        return transfer_pos_at(self.a_t, self.e_t, self.wbar,
                               self.M0, self.jd_dep, jd)


class SolarSim(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("太阳系轨道 1:1 实时仿真器 | Solar System Sim")
        self.geometry("1420x860")
        self.configure(bg="#060a12")

        self.cam = Camera()
        self.sim_jd = jd_now()
        self.offset = 0.0              # realtime anchor offset (days)
        self.speed = None              # None = realtime 1:1
        self.selected = "Earth"
        self.follow = False
        self.spacecraft = []
        self.transfer_plan = None      # dict from designer
        self.show_labels = True
        self._last_wall = time.time()
        self._drag = None

        self._build_ui()
        self.after(30, self._tick)

    # ---------------- UI layout ----------------
    def _build_ui(self):
        main = tk.Frame(self, bg="#060a12")
        main.pack(fill=tk.BOTH, expand=True)
        self.canvas = tk.Canvas(main, bg="#060a12", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        side = tk.Frame(main, bg="#0d1420", width=320)
        side.pack(side=tk.RIGHT, fill=tk.Y)
        side.pack_propagate(False)
        pad = dict(padx=8, pady=3)

        tk.Label(side, text="时间控制", fg="#7fd4ff", bg="#0d1420",
                 font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", **pad)
        tf = tk.Frame(side, bg="#0d1420")
        tf.pack(fill=tk.X, **pad)
        for i, (label, val) in enumerate(SPEED_STEPS):
            b = tk.Button(tf, text=label, width=9,
                          command=lambda v=val: self._set_speed(v),
                          bg="#16233a", fg="#cfe8ff", relief=tk.FLAT)
            b.grid(row=i // 3, column=i % 3, padx=2, pady=2)
        tk.Button(side, text="⏰ 对齐现在时间", command=self._sync_now,
                  bg="#1c4a6e", fg="white", relief=tk.FLAT).pack(fill=tk.X, **pad)

        jf = tk.Frame(side, bg="#0d1420")
        jf.pack(fill=tk.X, **pad)
        self.date_entry = tk.Entry(jf, width=12, bg="#16233a", fg="#cfe8ff",
                                   insertbackground="#cfe8ff")
        self.date_entry.insert(0, time.strftime("%Y-%m-%d"))
        self.date_entry.pack(side=tk.LEFT)
        tk.Button(jf, text="跳转到日期", command=self._jump_date,
                  bg="#16233a", fg="#cfe8ff", relief=tk.FLAT).pack(side=tk.LEFT, padx=4)

        tk.Label(side, text="天体信息（点击画面选择）", fg="#7fd4ff",
                 bg="#0d1420", font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", **pad)
        self.info = tk.Text(side, height=11, bg="#0a1220", fg="#bfe3c8",
                            font=("Consolas", 9), relief=tk.FLAT)
        self.info.pack(fill=tk.X, **pad)
        fl = tk.Frame(side, bg="#0d1420")
        fl.pack(fill=tk.X, **pad)
        self.follow_var = tk.IntVar(value=0)
        tk.Checkbutton(fl, text="跟随选中天体", variable=self.follow_var,
                       command=self._toggle_follow, bg="#0d1420",
                       fg="#cfe8ff", selectcolor="#16233a").pack(side=tk.LEFT)
        tk.Button(fl, text="重置视角", command=self._reset_cam,
                  bg="#16233a", fg="#cfe8ff", relief=tk.FLAT).pack(side=tk.LEFT, padx=6)

        tk.Label(side, text="转移轨道设计器（霍曼）", fg="#7fd4ff",
                 bg="#0d1420", font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", **pad)
        df = tk.Frame(side, bg="#0d1420")
        df.pack(fill=tk.X, **pad)
        self.dep_var = tk.StringVar(value="Earth")
        self.arr_var = tk.StringVar(value="Mars")
        names = BODY_ORDER
        tk.Label(df, text="出发", bg="#0d1420", fg="#cfe8ff").grid(row=0, column=0)
        ttk.OptionMenu(df, self.dep_var, "Earth", *names).grid(row=0, column=1, padx=2)
        tk.Label(df, text="到达", bg="#0d1420", fg="#cfe8ff").grid(row=0, column=2)
        ttk.OptionMenu(df, self.arr_var, "Mars", *names).grid(row=0, column=3, padx=2)
        tk.Button(side, text="计算 Δv 与发射窗口", command=self._design,
                  bg="#1c4a6e", fg="white", relief=tk.FLAT).pack(fill=tk.X, **pad)
        self.tresult = tk.Text(side, height=12, bg="#0a1220", fg="#ffd9a0",
                               font=("Consolas", 9), relief=tk.FLAT)
        self.tresult.pack(fill=tk.X, **pad)
        bf = tk.Frame(side, bg="#0d1420")
        bf.pack(fill=tk.X, **pad)
        tk.Button(bf, text="立即发射(演示)", command=lambda: self._launch(False),
                  bg="#5e3a1c", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(bf, text="等窗口发射", command=lambda: self._launch(True),
                  bg="#1c5e2e", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        tk.Label(side, text="操作: 左键拖拽=旋转 右键=平移 滚轮=缩放\n"
                            "点击=选天体 空格=暂停 R=对齐现在",
                 bg="#0d1420", fg="#5f7a96", justify=tk.LEFT).pack(anchor="w", **pad)

        self.canvas.bind("<ButtonPress-1>", self._on_down)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_up)
        self.canvas.bind("<ButtonPress-3>", self._on_rdown)
        self.canvas.bind("<B3-Motion>", self._on_rdrag)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.bind("<space>", lambda e: self._set_speed(0.0 if self.speed != 0.0 else None))
        self.bind("r", lambda e: self._sync_now())

    # ---------------- time & camera ----------------
    def _set_speed(self, v):
        if v is None:
            self.offset = self.sim_jd - jd_now()
        self.speed = v

    def _sync_now(self):
        self.speed = None
        self.offset = 0.0
        self.sim_jd = jd_now()

    def _jump_date(self):
        try:
            y, m, d = self.date_entry.get().split("-")
            self.sim_jd = jd_of_ymd(int(y), int(m), float(d))
            if self.speed is None:
                self.offset = self.sim_jd - jd_now()
        except Exception:
            pass

    def _toggle_follow(self):
        self.follow = bool(self.follow_var.get())

    def _reset_cam(self):
        self.cam.target = [0.0, 0.0, 0.0]
        self.cam.dist = 60.0
        self.follow_var.set(0)
        self.follow = False

    # ---------------- transfer designer ----------------
    def _design(self):
        dep, arr = self.dep_var.get(), self.arr_var.get()
        if dep == arr:
            return
        jd = self.sim_jd
        a1 = planet_elements_for_display(dep, jd)["a"]
        a2 = planet_elements_for_display(arr, jd)["a"]
        dv1, dv2, tof, a_t = hohmann(a1, a2)
        req = required_phase_deg(a1, a2)
        p1 = planet_state(dep, jd)[0]
        p2 = planet_state(arr, jd)[0]
        now = current_phase_deg(p1, p2)
        wt = wait_days(a1, a2, now)
        syn = synodic_days(a1, a2)

        lon_dep = math.degrees(math.atan2(p1[1], p1[0])) % 360.0
        a_tt, e_tt, wbar, M0, peri = transfer_elements(a1, a2, lon_dep)
        sc = transfer_pos_at(a_tt, e_tt, wbar, M0, jd, jd + tof)
        miss = miss_distance_km(sc, planet_state(arr, jd + tof)[0])

        self.transfer_plan = dict(dep=dep, arr=arr, a1=a1, a2=a2,
                                  dv1=dv1, dv2=dv2, tof=tof, wait=wt)
        jd_arr = jd + tof
        d_arr = datetime_of_jd(jd_arr).strftime("%Y-%m-%d")
        d_win = datetime_of_jd(jd + wt).strftime("%Y-%m-%d")
        txt = (f"{CN[dep]} → {CN[arr]}  (圆轨道共面近似)\n"
               f"转移半长轴 a_t = {a_t:.4f} AU\n"
               f"Δv₁ 出发加速 = {dv1:.2f} km/s\n"
               f"Δv₂ 到达加速 = {dv2:.2f} km/s\n"
               f"Δv 总计     = {dv1 + dv2:.2f} km/s\n"
               f"飞行时间    = {tof:.1f} 天 (到达 {d_arr})\n"
               f"─────────────\n"
               f"所需相位角  = {req:.1f}°\n"
               f"当前相位角  = {now:.1f}°\n"
               f"等待窗口    = {wt:.1f} 天 ({d_win})\n"
               f"会合周期    = {syn:.0f} 天\n"
               f"─────────────\n"
               f"⚠ 若现在发射, 到达时错过目标\n"
               f"   {miss / 1e6:.1f} 百万公里")
        self.tresult.delete("1.0", tk.END)
        self.tresult.insert("1.0", txt)

    def _launch(self, wait_for_window: bool):
        if not self.transfer_plan:
            self._design()
        tp = self.transfer_plan
        jd = self.sim_jd
        jd_dep = jd + (tp["wait"] if wait_for_window else 0.0)
        p_dep = planet_state(tp["dep"], jd_dep)[0]
        lon_dep = math.degrees(math.atan2(p_dep[1], p_dep[0])) % 360.0
        a_t, e_t, wbar, M0, peri = transfer_elements(tp["a1"], tp["a2"], lon_dep)
        sc = Spacecraft(tp["dep"], tp["arr"], a_t, e_t, wbar, M0,
                        jd_dep, jd_dep + tp["tof"])
        self.spacecraft.append(sc)

    # ---------------- events ----------------
    def _on_down(self, e):
        self._drag = ("L", e.x, e.y)

    def _on_drag(self, e):
        if self._drag and self._drag[0] == "L":
            dx, dy = e.x - self._drag[1], e.y - self._drag[2]
            self.cam.rotate(dx * 0.3, dy * 0.3)
            self._drag = ("L", e.x, e.y)

    def _on_up(self, e):
        if self._drag and self._drag[0] == "L":
            dx = abs(e.x - self._drag[1]) + abs(e.y - self._drag[2])
            if dx < 4:
                self._pick(e.x, e.y)
        self._drag = None

    def _on_rdown(self, e):
        self._drag = ("R", e.x, e.y)

    def _on_rdrag(self, e):
        if self._drag and self._drag[0] == "R":
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            self.cam.pan(e.x - self._drag[1], e.y - self._drag[2], w, h)
            self._drag = ("R", e.x, e.y)

    def _on_wheel(self, e):
        self.cam.zoom(0.9 if e.delta > 0 else 1.1)

    def _pick(self, x, y):
        best, best_d = None, 16.0
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        for name, pos in self._screen_positions():
            d = math.hypot(pos[0] - x, pos[1] - y)
            if d < best_d:
                best, best_d = name, d
        if best:
            self.selected = best

    # ---------------- simulation loop ----------------
    def _tick(self):
        now = time.time()
        dt = now - self._last_wall
        self._last_wall = now
        if self.speed is None:
            self.sim_jd = jd_now() + self.offset
        else:
            self.sim_jd += self.speed * dt
        if self.follow and self.selected in BODY_ORDER:
            p = planet_state(self.selected, self.sim_jd)[0]
            self.cam.target = [p[0], p[1], p[2]]
        self._draw()
        self.after(30, self._tick)

    def _screen_positions(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        out = []
        for name in BODY_ORDER:
            p = planet_state(name, self.sim_jd)[0]
            pr = self.cam.project(p, w, h)
            if pr:
                out.append((name, pr))
        return out

    def _draw_orbit(self, name, jd, color):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        el = planet_elements_for_display(name, jd)
        wbar = (el["wbar"]) % 360.0
        Om, inc = el["Om"], el["i"]
        warg = wbar - Om
        pts = []
        for k in range(73):
            M = k * 360.0 / 72.0
            from kepler import elements_to_state
            p, _ = elements_to_state(el["a"], el["e"], inc, Om, warg, M)
            pr = self.cam.project(p, w, h)
            if pr:
                pts.extend([pr[0], pr[1]])
        if len(pts) >= 6:
            self.canvas.create_line(*pts, fill=color, width=1)

    def _draw_grid(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        for r in (1, 2, 5, 10, 20, 40):
            pts = []
            for k in range(73):
                th = math.radians(k * 5.0)
                pr = self.cam.project((r * math.cos(th), r * math.sin(th), 0.0), w, h)
                if pr:
                    pts.extend([pr[0], pr[1]])
            if len(pts) >= 6:
                self.canvas.create_line(*pts, fill="#16202e", width=1)
        for k in range(12):
            th = math.radians(k * 30.0)
            p0 = self.cam.project((0, 0, 0), w, h)
            p1 = self.cam.project((40 * math.cos(th), 40 * math.sin(th), 0), w, h)
            if p0 and p1:
                self.canvas.create_line(p0[0], p0[1], p1[0], p1[1],
                                        fill="#101824", width=1)

    def _body_size(self, name, depth):
        base = SIZE_PX.get(name, 5)
        s = base * (30.0 / max(depth, 0.05)) ** 0.25
        return max(3.0, min(48.0, s))

    def _draw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        jd = self.sim_jd

        self._draw_grid()

        sun = self.cam.project((0, 0, 0), w, h)
        for name in BODY_ORDER:
            self._draw_orbit(name, jd, "#2a3a4e")

        if sun:
            r = self._body_size("Sun", sun[2])
            self.canvas.create_oval(sun[0] - r, sun[1] - r, sun[0] + r,
                                    sun[1] + r, fill="#ffd34d",
                                    outline="#ffedb0", width=2)
            if self.show_labels:
                self.canvas.create_text(sun[0] + r + 8, sun[1],
                                        text="太阳", fill="#ffd34d", anchor="w")

        for name, pr in self._screen_positions():
            r = self._body_size(name, pr[2])
            col = PLANETS[name][12]
            self.canvas.create_oval(pr[0] - r, pr[1] - r, pr[0] + r,
                                    pr[1] + r, fill=col, outline="")
            if name == self.selected:
                self.canvas.create_oval(pr[0] - r - 4, pr[1] - r - 4,
                                        pr[0] + r + 4, pr[1] + r + 4,
                                        outline="#7fd4ff", width=1)
            if self.show_labels:
                self.canvas.create_text(pr[0] + r + 6, pr[1] - r - 2,
                                        text=CN[name], fill=col, anchor="w",
                                        font=("Microsoft YaHei", 8))

        mp, mdist = moon_state_helio(jd)
        mpr = self.cam.project(mp, w, h)
        if mpr:
            r = max(2.0, self._body_size("Moon", mpr[2]) * 0.5)
            self.canvas.create_oval(mpr[0] - r, mpr[1] - r, mpr[0] + r,
                                    mpr[1] + r, fill="#c8c8c8", outline="")
            if self.cam.dist < 5.0:
                self.canvas.create_text(mpr[0] + 6, mpr[1] - 4, text="月球",
                                        fill="#c8c8c8", anchor="w",
                                        font=("Microsoft YaHei", 7))

        for sc in self.spacecraft:
            st = sc.status(jd)
            col = {"waiting": "#ffb060", "cruise": "#7fffd4",
                   "arrived": "#8fff8f"}[st]
            if st != "arrived":
                pts = []
                span = sc.jd_arr - sc.jd_dep
                for k in range(61):
                    t = sc.jd_dep + span * k / 60.0
                    p = transfer_pos_at(sc.a_t, sc.e_t, sc.wbar, sc.M0,
                                        sc.jd_dep, t)
                    pr = self.cam.project(p, w, h)
                    if pr:
                        pts.extend([pr[0], pr[1]])
                if len(pts) >= 6:
                    self.canvas.create_line(*pts, fill="#3d5a44", width=1,
                                            dash=(4, 3))
            p = sc.pos_at(jd)
            pr = self.cam.project(p, w, h)
            if pr:
                r = 5
                self.canvas.create_rectangle(pr[0] - r, pr[1] - r,
                                             pr[0] + r, pr[1] + r,
                                             fill=col, outline="white")
                sc.trail.append((p, jd))
                if len(sc.trail) > 400:
                    sc.trail.pop(0)
                tpts = []
                for tp, _ in sc.trail[::4]:
                    tpr = self.cam.project(tp, w, h)
                    if tpr:
                        tpts.extend([tpr[0], tpr[1]])
                if len(tpts) >= 6:
                    self.canvas.create_line(*tpts, fill=col, width=1)
                lbl = {"waiting": "等待窗口", "cruise": "巡航中",
                       "arrived": "已到达"}[st]
                self.canvas.create_text(pr[0] + 8, pr[1] - 8, text=f"探测器·{lbl}",
                                        fill=col, anchor="w",
                                        font=("Microsoft YaHei", 8))

        dt = datetime_of_jd(jd)
        mode = "实时 1:1" if self.speed is None else \
            dict((v, l) for l, v in SPEED_STEPS).get(self.speed, "?")
        self.canvas.create_text(12, 10, anchor="nw",
                                text=dt.strftime("UTC %Y-%m-%d %H:%M:%S"),
                                fill="#7fd4ff", font=("Consolas", 13, "bold"))
        self.canvas.create_text(12, 32, anchor="nw",
                                text=f"模式: {mode}   视角距离: {self.cam.dist:.2f} AU",
                                fill="#5f7a96", font=("Microsoft YaHei", 9))
        if jd_now() - 0.001 < jd < jd_now() + 0.001:
            self.canvas.create_text(12, 50, anchor="nw", text="● 与真实时间对齐",
                                    fill="#8fff8f", font=("Microsoft YaHei", 9))
        self._update_info()

    def _update_info(self):
        name = self.selected
        if name not in BODY_ORDER:
            return
        jd = self.sim_jd
        el = planet_elements_for_display(name, jd)
        p = planet_state(name, jd)[0]
        r_au = math.sqrt(p[0] ** 2 + p[1] ** 2 + p[2] ** 2)
        v = orbital_velocity_kms(r_au, el["a"])
        pe = planet_state("Earth", jd)[0]
        d_au = math.sqrt((p[0] - pe[0]) ** 2 + (p[1] - pe[1]) ** 2 +
                         (p[2] - pe[2]) ** 2)
        txt = (f"{CN[name]} ({name})\n"
               f"半长轴 a   = {el['a']:.5f} AU\n"
               f"偏心率 e   = {el['e']:.5f}\n"
               f"倾角 i     = {el['i']:.3f}°\n"
               f"升交点 Ω   = {el['Om']:.2f}°\n"
               f"近日点 ϖ   = {el['wbar']:.2f}°\n"
               f"平近点角 M = {el['M']:.1f}°\n"
               f"─────────────\n"
               f"日心距 r   = {r_au:.4f} AU\n"
               f"轨道速度   = {v:.2f} km/s\n"
               f"公转周期   = {period_days(el['a']):.1f} 天\n"
               f"距地球     = {d_au:.4f} AU ({d_au * AU_KM / 1e6:.1f} 百万km)")
        self.info.delete("1.0", tk.END)
        self.info.insert("1.0", txt)


if __name__ == "__main__":
    app = SolarSim()
    app.mainloop()
