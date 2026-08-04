# -*- coding: utf-8 -*-
"""main.py - engineering-grade 1:1 solar system simulator (stdlib only).

Bodies: 8 planets + Pluto, 21 moons, 4 named asteroids, 4 KBOs, Halley,
1500-object belt with Kirkwood gaps, ~30 bright stars.
Frames: heliocentric ecliptic J2000; star field on celestial sphere.
Physics: two-body Kepler (elliptic + hyperbolic), Hohmann designer,
KSP-style prograde/retrograde maneuver nodes, Sun-Earth Lagrange points,
SOI display, Saturn/Uranus rings, axial tilt poles, ISS & CalcSat-1 LEO.

Run:  py main.py
"""
import math
import time
import tkinter as tk
from tkinter import ttk

from kepler import (AU_KM, jd_now, jd_of_ymd, datetime_of_jd,
                    period_days, orbital_velocity_kms, elements_to_state)
from ephemeris import (PLANETS, CN, planet_state,
                       planet_elements_for_display, moon_state_helio, J2000)
from transfer import (hohmann, required_phase_deg, current_phase_deg,
                      wait_days, transfer_elements, transfer_pos_at,
                      miss_distance_km, synodic_days)
from bodies import (MOONS, ASTEROIDS, KBOS, COMETS, STARS, AXIAL_TILT,
                    SATURN_RINGS, soi_au, moon_pos, small_body_pos,
                    halley_pos, star_direction, belt_asteroids,
                    pole_direction, earth_orbit_pos, ISS, CALCSAT)
from conics import (state_to_elements, velocity_on_elements,
                    apply_prograde_dv, lagrange_points, leg_from_state,
                    pos_on_leg)
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
CN.update({"Phobos": "火卫一", "Deimos": "火卫二", "Io": "木卫一",
           "Europa": "木卫二", "Ganymede": "木卫三", "Callisto": "木卫四",
           "Mimas": "土卫一", "Enceladus": "土卫二", "Tethys": "土卫三",
           "Dione": "土卫四", "Rhea": "土卫五", "Titan": "土卫六",
           "Iapetus": "土卫八", "Miranda": "天卫五", "Ariel": "天卫一",
           "Umbriel": "天卫二", "Titania": "天卫三", "Oberon": "天卫四",
           "Triton": "海卫一", "Charon": "冥卫一", "Ceres": "谷神星",
           "Vesta": "灶神星", "Pallas": "智神星", "Hygiea": "健神星",
           "Eris": "阋神星", "Haumea": "妊神星", "Makemake": "鸟神星",
           "Sedna": "塞德娜", "Halley": "哈雷彗星"})


class Spacecraft:
    """Multi-leg conic vehicle: parks at departure, flies transfer arc,
    accepts prograde/retrograde burns that replace the future path."""
    def __init__(self, dep, arr, a_t, e_t, wbar, M0, jd_dep, jd_arr):
        self.dep, self.arr = dep, arr
        self.jd_dep = jd_dep
        self.jd_arr = jd_arr          # None after a burn (free flight)
        self.legs = [dict(a=a_t, e=e_t, wbar=wbar, M0=M0, jd0=jd_dep)]
        self.trail = []
        self.escaped = False

    def active_leg(self, jd):
        leg = self.legs[0]
        for lg in self.legs:
            if lg["jd0"] <= jd:
                leg = lg
        return leg

    def status(self, jd):
        if jd < self.jd_dep:
            return "waiting"
        if self.jd_arr is not None and jd >= self.jd_arr:
            return "arrived"
        if self.escaped:
            return "escaping"
        return "cruise"

    def pos_at(self, jd):
        st = self.status(jd)
        if st == "waiting":
            return planet_state(self.dep, jd)[0]
        if st == "arrived":
            return planet_state(self.arr, jd)[0]
        return pos_on_leg(self.active_leg(jd), jd)

    def burn(self, jd, dv_kms):
        """Prograde(+) / retrograde(-) impulsive burn at current time."""
        if self.status(jd) == "waiting":
            return None
        pos = self.pos_at(jd)
        leg = self.active_leg(jd)
        v = velocity_on_elements(leg["a"], leg["e"], leg["wbar"],
                                 leg["M0"], leg["jd0"], jd)
        v2 = apply_prograde_dv(pos, v, dv_kms)
        new_leg = leg_from_state(pos, v2, jd)
        self.legs.append(new_leg)
        self.jd_arr = None
        if new_leg["a"] < 0:
            self.escaped = True
        return new_leg

class SolarSim(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("太阳系工程仿真器 v2 | Solar System Engineering Sim")
        self.geometry("1560x900")
        self.configure(bg="#060a12")

        self.cam = Camera()
        self.sim_jd = jd_now()
        self.offset = 0.0
        self.speed = None
        self.selected = "Earth"
        self.follow = False
        self.spacecraft = []
        self.transfer_plan = None
        self.layers = dict(orbits=1, labels=1, grid=1, stars=1, belt=1,
                           moons=1, lagrange=1, soi=0, rings=1, poles=1,
                           trails=1)
        self._belt = belt_asteroids(1500)
        self._belt_cache = []
        self._last_wall = time.time()
        self._drag = None
        self._frame = 0
        self._fps_t = time.time()
        self._fps = 0.0

        self._build_ui()
        self.after(30, self._tick)

    # ---------------- UI ----------------
    def _build_ui(self):
        main = tk.Frame(self, bg="#060a12")
        main.pack(fill=tk.BOTH, expand=True)

        left = tk.Frame(main, bg="#0b1119", width=190)
        left.pack(side=tk.LEFT, fill=tk.Y)
        left.pack_propagate(False)
        tk.Label(left, text="天体目录", fg="#7fd4ff", bg="#0b1119",
                 font=("Microsoft YaHei", 10, "bold")).pack(anchor="w", padx=6, pady=4)
        self.tree = ttk.Treeview(left, show="tree")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=4)
        st = ttk.Style()
        st.configure("Treeview", background="#0b1119", foreground="#cfe8ff",
                     fieldbackground="#0b1119", font=("Microsoft YaHei", 9))
        sun = self.tree.insert("", "end", iid="Sun", text="☉ 太阳")
        for p in BODY_ORDER:
            pid = self.tree.insert("", "end", iid=p, text=CN[p])
            for m in MOONS.get(p, {}):
                self.tree.insert(pid, "end", iid=m, text=CN.get(m, m))
        belt = self.tree.insert("", "end", iid="_belt", text="小行星带")
        for a in ASTEROIDS:
            self.tree.insert(belt, "end", iid=a, text=CN.get(a, a))
        kui = self.tree.insert("", "end", iid="_kui", text="柯伊伯带")
        for k in KBOS:
            self.tree.insert(kui, "end", iid=k, text=CN.get(k, k))
        self.tree.insert("", "end", iid="Halley", text="哈雷彗星")
        self.tree.bind("<<TreeviewSelect>>", self._on_tree)
        self.tree.bind("<Double-1>", self._on_tree_focus)

        self.canvas = tk.Canvas(main, bg="#060a12", highlightthickness=0)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        side = tk.Frame(main, bg="#0d1420", width=330)
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

        tk.Label(side, text="天体信息", fg="#7fd4ff", bg="#0d1420",
                 font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", **pad)
        self.info = tk.Text(side, height=10, bg="#0a1220", fg="#bfe3c8",
                            font=("Consolas", 9), relief=tk.FLAT)
        self.info.pack(fill=tk.X, **pad)
        fl = tk.Frame(side, bg="#0d1420")
        fl.pack(fill=tk.X, **pad)
        self.follow_var = tk.IntVar(value=0)
        tk.Checkbutton(fl, text="跟随", variable=self.follow_var,
                       command=self._toggle_follow, bg="#0d1420",
                       fg="#cfe8ff", selectcolor="#16233a").pack(side=tk.LEFT)
        tk.Button(fl, text="聚焦选中 (F)", command=self._focus_selected,
                  bg="#16233a", fg="#cfe8ff", relief=tk.FLAT).pack(side=tk.LEFT, padx=4)
        tk.Button(fl, text="复位视角", command=self._reset_cam,
                  bg="#16233a", fg="#cfe8ff", relief=tk.FLAT).pack(side=tk.LEFT)

        lf = tk.LabelFrame(side, text="图层", bg="#0d1420", fg="#7fd4ff",
                           font=("Microsoft YaHei", 9))
        lf.pack(fill=tk.X, **pad)
        layer_names = [("orbits", "轨道线"), ("labels", "标签"), ("grid", "黄道网格"),
                       ("stars", "星空"), ("belt", "小行星带"), ("moons", "卫星"),
                       ("lagrange", "拉格朗日点"), ("soi", "SOI"), ("rings", "行星环"),
                       ("poles", "自转轴"), ("trails", "航迹")]
        for i, (key, label) in enumerate(layer_names):
            var = tk.IntVar(value=self.layers[key])
            tk.Checkbutton(lf, text=label, variable=var,
                           command=lambda k=key, v=var: self._set_layer(k, v.get()),
                           bg="#0d1420", fg="#cfe8ff",
                           selectcolor="#16233a").grid(row=i // 3, column=i % 3,
                                                       sticky="w", padx=4)

        tk.Label(side, text="转移轨道设计器（霍曼）", fg="#7fd4ff",
                 bg="#0d1420", font=("Microsoft YaHei", 11, "bold")).pack(anchor="w", **pad)
        df = tk.Frame(side, bg="#0d1420")
        df.pack(fill=tk.X, **pad)
        self.dep_var = tk.StringVar(value="Earth")
        self.arr_var = tk.StringVar(value="Mars")
        tk.Label(df, text="出发", bg="#0d1420", fg="#cfe8ff").grid(row=0, column=0)
        ttk.OptionMenu(df, self.dep_var, "Earth", *BODY_ORDER).grid(row=0, column=1, padx=2)
        tk.Label(df, text="到达", bg="#0d1420", fg="#cfe8ff").grid(row=0, column=2)
        ttk.OptionMenu(df, self.arr_var, "Mars", *BODY_ORDER).grid(row=0, column=3, padx=2)
        tk.Button(side, text="计算 Δv 与发射窗口", command=self._design,
                  bg="#1c4a6e", fg="white", relief=tk.FLAT).pack(fill=tk.X, **pad)
        self.tresult = tk.Text(side, height=11, bg="#0a1220", fg="#ffd9a0",
                               font=("Consolas", 9), relief=tk.FLAT)
        self.tresult.pack(fill=tk.X, **pad)
        bf = tk.Frame(side, bg="#0d1420")
        bf.pack(fill=tk.X, **pad)
        tk.Button(bf, text="立即发射(演示)", command=lambda: self._launch(False),
                  bg="#5e3a1c", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)
        tk.Button(bf, text="等窗口发射", command=lambda: self._launch(True),
                  bg="#1c5e2e", fg="white", relief=tk.FLAT).pack(side=tk.LEFT, expand=True, fill=tk.X, padx=2)

        mf = tk.LabelFrame(side, text="机动节点 (选中巡航探测器)", bg="#0d1420",
                           fg="#7fd4ff", font=("Microsoft YaHei", 9))
        mf.pack(fill=tk.X, **pad)
        tk.Label(mf, text="Δv (km/s)", bg="#0d1420", fg="#cfe8ff").grid(row=0, column=0)
        self.dv_entry = tk.Entry(mf, width=8, bg="#16233a", fg="#cfe8ff",
                                 insertbackground="#cfe8ff")
        self.dv_entry.insert(0, "1.0")
        self.dv_entry.grid(row=0, column=1, padx=4)
        tk.Button(mf, text="顺行点火", command=lambda: self._burn(1),
                  bg="#1c5e2e", fg="white", relief=tk.FLAT).grid(row=0, column=2, padx=2)
        tk.Button(mf, text="逆行点火", command=lambda: self._burn(-1),
                  bg="#5e1c1c", fg="white", relief=tk.FLAT).grid(row=0, column=3, padx=2)
        self.burn_info = tk.Label(mf, text="", bg="#0d1420", fg="#ffd9a0",
                                  font=("Consolas", 8), justify=tk.LEFT)
        self.burn_info.grid(row=1, column=0, columnspan=4, sticky="w")

        tk.Label(side, text="操作: 左键=旋转/选择 右键=平移 滚轮=缩放\n"
                            "树双击=聚焦 F=聚焦 空格=暂停 R=实时",
                 bg="#0d1420", fg="#5f7a96", justify=tk.LEFT).pack(anchor="w", **pad)

        self.canvas.bind("<ButtonPress-1>", self._on_down)
        self.canvas.bind("<B1-Motion>", self._on_drag)
        self.canvas.bind("<ButtonRelease-1>", self._on_up)
        self.canvas.bind("<ButtonPress-3>", self._on_rdown)
        self.canvas.bind("<B3-Motion>", self._on_rdrag)
        self.canvas.bind("<MouseWheel>", self._on_wheel)
        self.bind("<space>", lambda e: self._set_speed(0.0 if self.speed != 0.0 else None))
        self.bind("r", lambda e: self._sync_now())
        self.bind("f", lambda e: self._focus_selected())

    # ---------------- time / camera ----------------
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

    def _set_layer(self, key, val):
        self.layers[key] = val

    def _body_pos(self, name, jd):
        if name in BODY_ORDER:
            return planet_state(name, jd)[0]
        for parent, moons in MOONS.items():
            if name in moons:
                pp = planet_state(parent, jd)[0]
                a_km, p_d, i_d, n_d, ph, _ = moons[name]
                return moon_pos(pp, a_km, p_d, i_d, n_d, ph, jd)
        if name in ASTEROIDS:
            return small_body_pos(*ASTEROIDS[name][:6], jd)
        if name in KBOS:
            return small_body_pos(*KBOS[name][:6], jd)
        if name == "Halley":
            return halley_pos(jd)
        return (0.0, 0.0, 0.0)

    def _focus_selected(self):
        name = self.selected
        p = self._body_pos(name, self.sim_jd)
        self.cam.target = [p[0], p[1], p[2]]
        if name in MOONS.get(self._parent_of(name), {}):
            self.cam.dist = 0.01
        elif name in BODY_ORDER:
            self.cam.dist = {  # nice framing incl. moon system
                "Mercury": 0.15, "Venus": 0.2, "Earth": 0.02, "Mars": 0.01,
                "Jupiter": 0.2, "Saturn": 0.4, "Uranus": 0.1,
                "Neptune": 0.08, "Pluto": 0.02}[name]
        else:
            self.cam.dist = 0.5

    def _parent_of(self, name):
        for parent, moons in MOONS.items():
            if name in moons:
                return parent
        return None

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
        d_arr = datetime_of_jd(jd + tof).strftime("%Y-%m-%d")
        d_win = datetime_of_jd(jd + wt).strftime("%Y-%m-%d")
        txt = (f"{CN[dep]} → {CN[arr]}  (圆轨道共面近似)\n"
               f"a_t = {a_t:.4f} AU   飞行 {tof:.1f} 天\n"
               f"Δv₁ = {dv1:.2f}  Δv₂ = {dv2:.2f}  总 {dv1 + dv2:.2f} km/s\n"
               f"所需相位 {req:.1f}°  当前 {now:.1f}°\n"
               f"等待 {wt:.1f} 天 ({d_win})\n"
               f"会合周期 {syn:.0f} 天   到达 {d_arr}\n"
               f"─────────────\n"
               f"⚠ 现在发射脱靶 {miss / 1e6:.1f} 百万 km")
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
        self.spacecraft.append(
            Spacecraft(tp["dep"], tp["arr"], a_t, e_t, wbar, M0,
                       jd_dep, jd_dep + tp["tof"]))

    def _burn(self, sign):
        cruise = [s for s in self.spacecraft
                  if s.status(self.sim_jd) in ("cruise", "escaping")]
        if not cruise:
            self.burn_info.config(text="无巡航中的探测器")
            return
        try:
            dv = float(self.dv_entry.get()) * sign
        except ValueError:
            return
        leg = cruise[-1].burn(self.sim_jd, dv)
        if leg["a"] > 0:
            apo = leg["a"] * (1 + leg["e"])
            peri = leg["a"] * (1 - leg["e"])
            self.burn_info.config(
                text=f"新轨道: a={leg['a']:.3f}AU e={leg['e']:.3f}\n"
                     f"近日点 {peri:.3f} 远日点 {apo:.3f} AU")
        else:
            self.burn_info.config(
                text=f"⚠ 双曲线逃逸! e={leg['e']:.2f} — 离开太阳系")

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

    def _on_tree(self, e):
        sel = self.tree.selection()
        if sel and not sel[0].startswith("_"):
            self.selected = sel[0]

    def _on_tree_focus(self, e):
        self._focus_selected()

    def _pick(self, x, y):
        best, best_d = None, 16.0
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
        if self.follow:
            p = self._body_pos(self.selected, self.sim_jd)
            self.cam.target = [p[0], p[1], p[2]]
        self._frame += 1
        if self._frame % 30 == 0:
            self._fps = 30.0 / max(time.time() - self._fps_t, 1e-6)
            self._fps_t = time.time()
        self._draw()
        self.after(30, self._tick)

    def _screen_positions(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        out = []
        for name in BODY_ORDER:
            pr = self.cam.project(planet_state(name, self.sim_jd)[0], w, h)
            if pr:
                out.append((name, pr))
        if self.layers["moons"] and self.cam.dist < 2.0:
            for parent, moons in MOONS.items():
                pp = planet_state(parent, self.sim_jd)[0]
                for m, (a_km, p_d, i_d, n_d, ph, _) in moons.items():
                    pr = self.cam.project(
                        moon_pos(pp, a_km, p_d, i_d, n_d, ph, self.sim_jd), w, h)
                    if pr:
                        out.append((m, pr))
        for grp in (ASTEROIDS, KBOS):
            for nm, el in grp.items():
                pr = self.cam.project(small_body_pos(*el[:6], self.sim_jd), w, h)
                if pr:
                    out.append((nm, pr))
        pr = self.cam.project(halley_pos(self.sim_jd), w, h)
        if pr:
            out.append(("Halley", pr))
        return out

    # ---------------- drawing ----------------
    def _poly(self, pts3d, color, width=1, dash=None):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        pts = []
        for p in pts3d:
            pr = self.cam.project(p, w, h)
            if pr:
                pts.extend([pr[0], pr[1]])
        if len(pts) >= 6:
            self.canvas.create_line(*pts, fill=color, width=width, dash=dash)

    def _draw_stars(self):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        R = self.cam.dist * 60.0
        t = self.cam.target
        for name, ra, dec, mag in STARS:
            d = star_direction(ra, dec)
            pr = self.cam.project((t[0] + d[0] * R, t[1] + d[1] * R,
                                   t[2] + d[2] * R), w, h)
            if pr and 0 <= pr[0] < w and 0 <= pr[1] < h:
                s = max(1.0, 3.5 - mag)
                self.canvas.create_oval(pr[0] - s, pr[1] - s, pr[0] + s,
                                        pr[1] + s, fill="#dfe8ff", outline="")
                if mag < 0.5 and self.layers["labels"]:
                    self.canvas.create_text(pr[0] + 5, pr[1] - 5, text=name,
                                            fill="#8a9ab8", anchor="w",
                                            font=("Microsoft YaHei", 7))

    def _draw_grid(self):
        for r in (1, 2, 5, 10, 20, 40):
            self._poly([(r * math.cos(math.radians(k * 5.0)),
                         r * math.sin(math.radians(k * 5.0)), 0.0)
                        for k in range(73)], "#16202e")
        for k in range(12):
            th = math.radians(k * 30.0)
            self._poly([(0, 0, 0), (40 * math.cos(th), 40 * math.sin(th), 0)],
                       "#101824")
        # vernal equinox arrow + ecliptic label
        self._poly([(0, 0, 0), (8, 0, 0)], "#2e4a3a", width=2)
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        pr = self.cam.project((8.3, 0, 0), w, h)
        if pr:
            self.canvas.create_text(pr[0], pr[1], text="♈ 春分点方向 (J2000)",
                                    fill="#4a8a6a", anchor="w",
                                    font=("Microsoft YaHei", 8))
        pr2 = self.cam.project((20 * math.cos(2.4), 20 * math.sin(2.4), 0), w, h)
        if pr2:
            self.canvas.create_text(pr2[0], pr2[1], text="黄道面 Ecliptic J2000",
                                    fill="#3a5a78", anchor="center",
                                    font=("Microsoft YaHei", 9))

    def _draw_orbit(self, name, jd):
        el = planet_elements_for_display(name, jd)
        col = "#2a3a4e" if name != self.selected else "#4a7a9e"
        warg = el["wbar"] - el["Om"]
        self._poly([elements_to_state(el["a"], el["e"], el["i"], el["Om"],
                                      warg, k * 5.0)[0] for k in range(73)],
                   col, width=1)
        if name == self.selected:
            # perihelion / aphelion markers + node line
            pp, _ = elements_to_state(el["a"], el["e"], el["i"], el["Om"], warg, 0.0)
            pa, _ = elements_to_state(el["a"], el["e"], el["i"], el["Om"], warg, 180.0)
            w = self.canvas.winfo_width()
            h = self.canvas.winfo_height()
            for p, lbl in ((pp, "近日点"), (pa, "远日点")):
                pr = self.cam.project(p, w, h)
                if pr:
                    self.canvas.create_oval(pr[0] - 3, pr[1] - 3, pr[0] + 3,
                                            pr[1] + 3, outline="#8ab8d8")
                    self.canvas.create_text(pr[0] + 5, pr[1] + 6, text=lbl,
                                            fill="#6a8aa8", anchor="w",
                                            font=("Microsoft YaHei", 7))
            n1 = (math.cos(math.radians(el["Om"])),
                  math.sin(math.radians(el["Om"])), 0.0)
            self._poly([tuple(-el["a"] * 1.3 * c for c in n1),
                        tuple(el["a"] * 1.3 * c for c in n1)],
                       "#3a4a5a", dash=(2, 4))

    def _draw_belt(self, jd):
        if self._frame % 3 == 0 or not self._belt_cache:
            self._belt_cache = [small_body_pos(*el, jd) for el in self._belt]
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        for p in self._belt_cache:
            pr = self.cam.project(p, w, h)
            if pr and 0 <= pr[0] < w and 0 <= pr[1] < h:
                self.canvas.create_rectangle(pr[0], pr[1], pr[0] + 1.5,
                                             pr[1] + 1.5, fill="#5a6a7a",
                                             outline="")

    def _draw_small_named(self, jd):
        for grp, col in ((ASTEROIDS, "#c8d0e0"), (KBOS, "#e0c8d8")):
            for nm, el in grp.items():
                p = small_body_pos(*el[:6], jd)
                self._poly([elements_to_state(el[0], el[1], el[2], el[3],
                                              el[4] - el[3], k * 5.0)[0]
                            for k in range(73)], "#33302e")
                w = self.canvas.winfo_width()
                h = self.canvas.winfo_height()
                pr = self.cam.project(p, w, h)
                if pr:
                    self.canvas.create_oval(pr[0] - 3, pr[1] - 3, pr[0] + 3,
                                            pr[1] + 3, fill=col, outline="")
                    if self.layers["labels"]:
                        self.canvas.create_text(pr[0] + 6, pr[1] - 4,
                                                text=CN.get(nm, nm), fill=col,
                                                anchor="w",
                                                font=("Microsoft YaHei", 7))
        # Halley with sunward tail
        hp = halley_pos(jd)
        c = COMETS["Halley"]
        self._poly([elements_to_state(c["a"], c["e"], c["i"], c["Om"],
                                      c["w"], k * 5.0)[0] for k in range(73)],
                   "#1e3a44")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        pr = self.cam.project(hp, w, h)
        if pr:
            r_au = math.sqrt(sum(x * x for x in hp))
            self.canvas.create_oval(pr[0] - 3, pr[1] - 3, pr[0] + 3,
                                    pr[1] + 3, fill=c["color"], outline="")
            if r_au < 3.0:   # tail appears near perihelion, points anti-sun
                d = math.sqrt(sum(x * x for x in hp))
                tp = tuple(-x / d * min(r_au * 0.5, 1.0) for x in hp)
                end = (hp[0] + tp[0], hp[1] + tp[1], hp[2] + tp[2])
                pr2 = self.cam.project(end, w, h)
                if pr2:
                    self.canvas.create_line(pr[0], pr[1], pr2[0], pr2[1],
                                            fill="#7ac8e8", width=2)
            if self.layers["labels"]:
                self.canvas.create_text(pr[0] + 6, pr[1] - 4, text="哈雷彗星",
                                        fill=c["color"], anchor="w",
                                        font=("Microsoft YaHei", 7))

    def _draw_planet_extras(self, name, pr, jd):
        """Rings, axial pole, SOI circle, moon system."""
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        p = planet_state(name, jd)[0]
        depth = pr[2]
        disp_r = self._body_size(name, depth)
        world_r = disp_r * depth / self.cam.f

        if self.layers["poles"] and disp_r > 5:
            pole = pole_direction(AXIAL_TILT[name])
            p1 = tuple(p[k] + pole[k] * world_r * 2.2 for k in range(3))
            p2 = tuple(p[k] - pole[k] * world_r * 2.2 for k in range(3))
            self._poly([p1, p2], "#5a7a6a", width=1)

        if self.layers["rings"] and name == "Saturn" and disp_r > 4:
            pole = pole_direction(AXIAL_TILT["Saturn"])
            u = (1.0, 0.0, 0.0)
            ux = u[1] * pole[2] - u[2] * pole[1]
            uy = u[2] * pole[0] - u[0] * pole[2]
            uz = u[0] * pole[1] - u[1] * pole[0]
            un = math.sqrt(ux * ux + uy * uy + uz * uz) or 1.0
            ux, uy, uz = ux / un, uy / un, uz / un
            vx = pole[1] * uz - pole[2] * uy
            vy = pole[2] * ux - pole[0] * uz
            vz = pole[0] * uy - pole[1] * ux
            for rn, r_in, r_out, col in SATURN_RINGS:
                rr = (r_in + r_out) / 2.0 * world_r
                self._poly([tuple(p[k] + rr * (math.cos(t) * (ux, uy, uz)[k] +
                                  math.sin(t) * (vx, vy, vz)[k])
                                  for k in range(3))
                            for t in [math.radians(a) for a in range(0, 361, 6)]],
                           col, width=2 if rn == "B" else 1)
        if self.layers["rings"] and name == "Uranus" and disp_r > 4:
            pole = pole_direction(AXIAL_TILT["Uranus"])
            rr = 1.95 * world_r
            self._poly([tuple(p[k] + rr * math.cos(t) * 1.0
                              for k in range(3)) for t in
                        [math.radians(a) for a in range(0, 361, 10)]],
                       "#3a5a5a", width=1)

        if self.layers["soi"] and self.cam.dist < 2.0:
            el = planet_elements_for_display(name, jd)
            r_soi = soi_au(name, el["a"])
            self._poly([tuple(p[k] + (r_soi * math.cos(t) if k == 0 else
                                      r_soi * math.sin(t) if k == 1 else 0.0)
                              for k in range(3))
                        for t in [math.radians(a) for a in range(0, 361, 6)]],
                       "#3a3a2a", dash=(3, 4))

        if self.layers["moons"]:
            moons = MOONS.get(name, {})
            if moons and self.cam.dist < 2.0:
                for m, (a_km, p_d, i_d, n_d, ph, col) in moons.items():
                    a = a_km / AU_KM
                    if self.cam.dist < 0.5:
                        self._poly([moon_pos(p, a_km, p_d, i_d, n_d,
                                             k * 7.5, J2000)
                                    for k in range(49)], "#2e3a3a")
                    mp = moon_pos(p, a_km, p_d, i_d, n_d, ph, jd)
                    mpr = self.cam.project(mp, w, h)
                    if mpr:
                        mr = 2.5
                        self.canvas.create_oval(mpr[0] - mr, mpr[1] - mr,
                                                mpr[0] + mr, mpr[1] + mr,
                                                fill=col, outline="")
                        if self.layers["labels"] and self.cam.dist < 0.3:
                            self.canvas.create_text(mpr[0] + 5, mpr[1] - 4,
                                                    text=CN.get(m, m), fill=col,
                                                    anchor="w",
                                                    font=("Microsoft YaHei", 7))

    def _draw_lagrange(self, jd):
        ep = planet_state("Earth", jd)[0]
        lp = lagrange_points(ep)
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        for name, p in lp.items():
            pr = self.cam.project(p, w, h)
            if pr:
                self.canvas.create_line(pr[0] - 4, pr[1], pr[0] + 4, pr[1],
                                        fill="#8a6a9a")
                self.canvas.create_line(pr[0], pr[1] - 4, pr[0], pr[1] + 4,
                                        fill="#8a6a9a")
                if self.layers["labels"]:
                    self.canvas.create_text(pr[0] + 6, pr[1], text=name,
                                            fill="#8a6a9a", anchor="w",
                                            font=("Consolas", 8))

    def _draw_earth_local(self, jd):
        """Moon orbit, ISS, CalcSat-1 when zoomed to Earth."""
        if self.cam.dist > 0.02:
            return
        ep = planet_state("Earth", jd)[0]
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        self._poly([moon_pos(ep, 384400.0, 27.321661, 5.14, 125.0,
                             k * 7.5, J2000) for k in range(49)], "#3a4a4a")
        for craft, col, lbl in ((ISS, ISS["color"], "ISS"),
                                (CALCSAT, CALCSAT["color"], "算星一号")):
            p = earth_orbit_pos(ep, craft["a_km"], craft["i_deg"], jd)
            pr = self.cam.project(p, w, h)
            if pr:
                self.canvas.create_rectangle(pr[0] - 2, pr[1] - 2, pr[0] + 2,
                                             pr[1] + 2, fill=col, outline="")
                self.canvas.create_text(pr[0] + 5, pr[1] - 4, text=lbl,
                                        fill=col, anchor="w",
                                        font=("Microsoft YaHei", 7))

    def _draw_spacecraft(self, jd):
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        for sc in self.spacecraft:
            st = sc.status(jd)
            col = {"waiting": "#ffb060", "cruise": "#7fffd4",
                   "arrived": "#8fff8f", "escaping": "#ff7a9a"}[st]
            if st in ("cruise", "escaping"):
                leg = sc.active_leg(jd)
                pts = []
                if leg["a"] > 0:
                    span = period_days(leg["a"])
                    for k in range(73):
                        pts.append(pos_on_leg(leg, leg["jd0"] + span * k / 72.0))
                else:
                    for k in range(40):
                        pts.append(pos_on_leg(leg, jd + k * 20.0))
                self._poly(pts, "#3d5a44", dash=(4, 3))
            p = sc.pos_at(jd)
            pr = self.cam.project(p, w, h)
            if pr:
                self.canvas.create_rectangle(pr[0] - 5, pr[1] - 5, pr[0] + 5,
                                             pr[1] + 5, fill=col,
                                             outline="white")
                if self.layers["trails"]:
                    sc.trail.append(p)
                    if len(sc.trail) > 500:
                        sc.trail.pop(0)
                    tpts = []
                    for tp in sc.trail[::4]:
                        tpr = self.cam.project(tp, w, h)
                        if tpr:
                            tpts.extend([tpr[0], tpr[1]])
                    if len(tpts) >= 6:
                        self.canvas.create_line(*tpts, fill=col, width=1)
                lbl = {"waiting": "等待窗口", "cruise": "巡航中",
                       "arrived": "已到达", "escaping": "逃逸中"}[st]
                self.canvas.create_text(pr[0] + 8, pr[1] - 8,
                                        text=f"探测器·{lbl}", fill=col,
                                        anchor="w", font=("Microsoft YaHei", 8))

    def _body_size(self, name, depth):
        base = SIZE_PX.get(name, 5)
        s = base * (30.0 / max(depth, 0.05)) ** 0.25
        return max(3.0, min(48.0, s))

    def _draw(self):
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        jd = self.sim_jd

        if self.layers["stars"]:
            self._draw_stars()
        if self.layers["grid"]:
            self._draw_grid()
        if self.layers["belt"] and self.cam.dist > 3.0:
            self._draw_belt(jd)
        if self.layers["orbits"]:
            for name in BODY_ORDER:
                self._draw_orbit(name, jd)
        self._draw_small_named(jd)

        sun = self.cam.project((0, 0, 0), w, h)
        if sun:
            r = self._body_size("Sun", sun[2])
            self.canvas.create_oval(sun[0] - r, sun[1] - r, sun[0] + r,
                                    sun[1] + r, fill="#ffd34d",
                                    outline="#ffedb0", width=2)
            if self.layers["labels"]:
                self.canvas.create_text(sun[0] + r + 8, sun[1], text="太阳",
                                        fill="#ffd34d", anchor="w")

        for name in BODY_ORDER:
            pr = self.cam.project(planet_state(name, jd)[0], w, h)
            if not pr:
                continue
            r = self._body_size(name, pr[2])
            col = PLANETS[name][12]
            self.canvas.create_oval(pr[0] - r, pr[1] - r, pr[0] + r,
                                    pr[1] + r, fill=col, outline="")
            if name == self.selected:
                self.canvas.create_oval(pr[0] - r - 4, pr[1] - r - 4,
                                        pr[0] + r + 4, pr[1] + r + 4,
                                        outline="#7fd4ff", width=1)
            if self.layers["labels"]:
                self.canvas.create_text(pr[0] + r + 6, pr[1] - r - 2,
                                        text=CN[name], fill=col, anchor="w",
                                        font=("Microsoft YaHei", 8))
            self._draw_planet_extras(name, pr, jd)

        if self.layers["lagrange"] and self.cam.dist < 30.0:
            self._draw_lagrange(jd)
        self._draw_earth_local(jd)
        self._draw_spacecraft(jd)

        dt = datetime_of_jd(jd)
        mode = "实时 1:1" if self.speed is None else \
            dict((v, l) for l, v in SPEED_STEPS).get(self.speed, "?")
        self.canvas.create_text(12, 10, anchor="nw",
                                text=dt.strftime("UTC %Y-%m-%d %H:%M:%S"),
                                fill="#7fd4ff", font=("Consolas", 13, "bold"))
        self.canvas.create_text(12, 32, anchor="nw",
                                text=f"模式: {mode}   视距: {self.cam.dist:.3f} AU"
                                     f"   FPS: {self._fps:.0f}",
                                fill="#5f7a96", font=("Microsoft YaHei", 9))
        if jd_now() - 0.001 < jd < jd_now() + 0.001:
            self.canvas.create_text(12, 50, anchor="nw", text="● 与真实时间对齐",
                                    fill="#8fff8f", font=("Microsoft YaHei", 9))
        self._update_info()

    def _update_info(self):
        name = self.selected
        jd = self.sim_jd
        if name in BODY_ORDER:
            el = planet_elements_for_display(name, jd)
            p = planet_state(name, jd)[0]
            r_au = math.sqrt(sum(c * c for c in p))
            v = orbital_velocity_kms(r_au, el["a"])
            pe = planet_state("Earth", jd)[0]
            d_au = math.sqrt(sum((p[k] - pe[k]) ** 2 for k in range(3)))
            txt = (f"{CN[name]} ({name})\n"
                   f"a={el['a']:.5f}AU e={el['e']:.5f} i={el['i']:.3f}°\n"
                   f"Ω={el['Om']:.2f}° ϖ={el['wbar']:.2f}° M={el['M']:.1f}°\n"
                   f"r={r_au:.4f}AU  v={v:.2f}km/s\n"
                   f"周期={period_days(el['a']):.1f}天\n"
                   f"SOI={soi_au(name, el['a']):.4f}AU\n"
                   f"距地球={d_au:.4f}AU ({d_au * AU_KM / 1e6:.1f}百万km)")
        elif self._parent_of(name):
            parent = self._parent_of(name)
            a_km, p_d, i_d, _, _, _ = MOONS[parent][name]
            txt = (f"{CN.get(name, name)} ({name})\n母行星: {CN[parent]}\n"
                   f"轨道半径 = {a_km:,.0f} km\n周期 = {p_d:.3f} 天\n"
                   f"倾角(对黄道) ≈ {i_d:.1f}°")
        elif name in ASTEROIDS or name in KBOS:
            el = (ASTEROIDS | KBOS)[name]
            txt = (f"{CN.get(name, name)}\na={el[0]:.3f}AU e={el[1]:.3f} "
                   f"i={el[2]:.1f}°\n周期={period_days(el[0]) / 365.256:.2f} 年")
        elif name == "Halley":
            c = COMETS["Halley"]
            txt = (f"哈雷彗星 1P/Halley\na={c['a']:.2f}AU e={c['e']:.4f} "
                   f"i={c['i']:.1f}°(逆行)\n周期={period_days(c['a']) / 365.256:.2f} 年\n"
                   f"上次近日点 1986-02-09\n下次回归 2061-07-28")
        else:
            return
        self.info.delete("1.0", tk.END)
        self.info.insert("1.0", txt)


if __name__ == "__main__":
    app = SolarSim()
    app.mainloop()
