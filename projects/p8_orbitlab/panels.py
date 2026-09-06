# -*- coding: utf-8 -*-
"""
panels.py —— OrbitLab UI 面板层（左栏 / 右栏 / 底栏）

教学仿真器 OrbitLab 的全部控制与显示面板，零依赖（仅 tkinter + math）。
深色主题：背景 #141824 / 面板 #1c2230 / 文字 #d8dee9 / 强调色 #4da6ff。

面板职责（见 docs/ARCHITECTURE.md 第 5、6 节）：
  LeftPanel   左栏 300px：轨道六根数滑块 / 预设轨道 / 摄动开关 / 显示选项
  RightPanel  右栏 300px：osculating 实时数据 / 摄动理论速率 / 星下点 / 公式卡
  BottomPanel 底栏 70px ：播放控制 / 对数速度滑块 / 仿真时钟 / 周期进度条
"""
import tkinter as tk
import math

# ------------------------------------------------------------ 配色与字体
BG       = "#141824"   # 窗口深背景
PANEL    = "#1c2230"   # 面板背景
FG       = "#d8dee9"   # 正文文字
ACCENT   = "#4da6ff"   # 强调色（分节标题 / 高亮数值）
GRAY     = "#7c8598"   # 释义小字 / 单位
ENTRY_BG = "#0f1420"   # 输入框 / 滑块槽底色
BTN_BG   = "#2a3245"   # 按钮底色
LINE     = "#3a4358"   # 分节分隔线

UI_FONT   = ("Microsoft YaHei", 9)    # 中文界面字体
UI_FONT_S = ("Microsoft YaHei", 8)    # 小字（释义 / 单位）
MONO      = ("Consolas", 9)           # 等宽：数据表 / 时钟
MONO_S    = ("Consolas", 8)


def make_section(parent, title):
    """分节标题：加粗强调色文字 + 一条分隔线，返回外层 Frame。"""
    wrap = tk.Frame(parent, bg=PANEL)
    wrap.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(8, 2))
    tk.Label(wrap, text=title, bg=PANEL, fg=ACCENT,
             font=("Microsoft YaHei", 9, "bold"),
             anchor="w").pack(side=tk.TOP, fill=tk.X)
    tk.Frame(wrap, bg=LINE, height=1).pack(side=tk.TOP, fill=tk.X, pady=(2, 0))
    return wrap


def make_check(parent, text, var, on_change, fg=FG):
    """深色复选框工厂。var 为 tk.BooleanVar，on_change 为状态变化回调。"""
    return tk.Checkbutton(
        parent, text=text, variable=var, command=on_change,
        bg=PANEL, fg=fg, selectcolor=ENTRY_BG,
        activebackground=PANEL, activeforeground=fg,
        highlightthickness=0, bd=0, anchor="w", font=UI_FONT)


def _make_btn(parent, text, cmd):
    """深色按钮工厂（面板内部使用）。"""
    return tk.Button(parent, text=text, command=cmd,
                     bg=BTN_BG, fg=FG, activebackground=ACCENT,
                     activeforeground="#ffffff", relief=tk.FLAT, bd=0,
                     font=UI_FONT_S, padx=6, pady=2)


class ParamRow(tk.Frame):
    """一行"标签 + 滑块 + 数值框 + 单位"的参数控件。

    教学工具的核心交互件：拖滑块或直接键入数值都能改参数，两者双向同步；
    任何变化调用 on_change()。防递归：程序设值（set）时不触发回调，
    用 self._updating 标志挡住 Scale.set 引发的 command 回调。
    参数真实值保存在 self._value：滑块按 resolution 吸附显示，
    而 _value 始终保持精确（如 J2 初值 1.0826e-3 不被滑块吸附成 1.08e-3）。
    """

    def __init__(self, parent, label, vmin, vmax, init, resolution,
                 unit="", on_change=None, sci=False):
        super().__init__(parent, bg=PANEL)
        self.on_change = on_change or (lambda: None)
        self.vmin, self.vmax = vmin, vmax
        self.sci = sci              # 科学计数显示（J2 等小量）
        self._updating = False      # 防递归标志
        self._value = float(init)   # 参数真实值（get 的数据源）

        tk.Label(self, text=label, bg=PANEL, fg=FG, width=11,
                 anchor="w", font=UI_FONT_S).pack(side=tk.LEFT)

        self.scale = tk.Scale(
            self, from_=vmin, to=vmax, resolution=resolution,
            orient=tk.HORIZONTAL, showvalue=False, length=88,
            command=self._on_scale,
            bg=PANEL, fg=FG, troughcolor=ENTRY_BG,
            highlightthickness=0, activebackground=ACCENT, bd=0)
        self.scale.pack(side=tk.LEFT, padx=2)

        self.entry = tk.Entry(self, width=9, bg=ENTRY_BG, fg=FG,
                              insertbackground=FG, relief=tk.FLAT,
                              font=MONO, justify=tk.RIGHT)
        self.entry.pack(side=tk.LEFT, padx=2)
        self.entry.bind("<Return>", self._on_entry)
        self.entry.bind("<FocusOut>", self._on_entry)

        if unit:
            tk.Label(self, text=unit, bg=PANEL, fg=GRAY,
                     font=UI_FONT_S).pack(side=tk.LEFT)

        self.set(init)   # 程序设初值（不触发回调）

    # ---------------- 内部事件 ----------------
    def _on_scale(self, s):
        """滑块拖动：同步数值框并通知外部。"""
        if self._updating:
            return
        self._value = float(s)
        self._updating = True
        self._set_entry(self._value)
        self._updating = False
        self.on_change()

    def _on_entry(self, _evt):
        """数值框回车 / 失焦：解析文本写回滑块（越界自动夹取）。"""
        if self._updating:
            return
        try:
            v = float(self.entry.get())
        except ValueError:
            self._set_entry(self._value)   # 非法输入：回显当前值
            return
        v = max(self.vmin, min(self.vmax, v))
        self._value = v
        self._updating = True
        self.scale.set(v)          # 会触发 _on_scale，被 _updating 挡住
        self._set_entry(v)
        self._updating = False
        self.on_change()

    def _set_entry(self, v):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, self._fmt(v))

    def _fmt(self, v):
        """数值格式化：sci 用科学计数，否则给紧凑有效位。"""
        return f"{v:.4e}" if self.sci else f"{v:.6g}"

    # ---------------- 对外接口 ----------------
    def get(self):
        """当前参数值（float）。"""
        return self._value

    def set(self, v):
        """程序回写数值（不触发 on_change）。"""
        self._value = float(v)
        self._updating = True
        self.scale.set(v)          # 滑块显示按 resolution 吸附，_value 保持精确
        self._set_entry(self._value)
        self._updating = False

    def set_range(self, vmin, vmax):
        """动态修改滑块范围（不触发 on_change）。

        用途：物理边界联动——例如 e 的上限随 a 收缩
        （e_max = 1 − (RE+100km)/a，保证近地点不穿地）。
        当前值超出新范围时滑块显示自动夹取，_value 由调用方负责先行钳制。
        """
        self.vmin, self.vmax = float(vmin), float(vmax)
        self._updating = True
        self.scale.config(from_=self.vmin, to=self.vmax)
        self._updating = False


class LeftPanel(tk.Frame):
    """左栏（300px）：轨道六根数 / 预设轨道 / 摄动开关 / 显示选项。

    任何控件变化都会调用 on_change()，由 main 重算参考轨道并重置传播器。
    """

    def __init__(self, parent, on_change):
        super().__init__(parent, bg=PANEL, width=300)
        self.pack_propagate(False)
        self.on_change = on_change

        # ================= 1. 轨道六根数（开普勒要素） =================
        make_section(self, "轨道六根数（开普勒要素）")
        # (键, 标签, 下限, 上限, 初值, 分辨率, 单位, 几何释义)
        # a 初值 6978 km ≈ 600 km 高度的近地圆轨道（太阳同步典型高度）
        specs = [
            ("a",  "a 半长轴",     6500, 45000, 6978,  1.0,   "km", "轨道大小：椭圆长轴的一半"),
            ("e",  "e 偏心率",     0,    0.9,   0.001, 0.001, "",   "轨道形状：0=圆，越接近1越扁"),
            ("i",  "i 轨道倾角",   0,    180,   97.8,  0.1,   "°",  "轨道面与赤道面的夹角"),
            ("Om", "Ω 升交点赤经", 0,    360,   30,    0.1,   "°",  "轨道面在赤道面内的指向"),
            ("w",  "ω 近地点幅角", 0,    360,   0,     0.1,   "°",  "近地点在轨道面内的位置"),
            ("nu", "ν 真近点角",   0,    360,   0,     0.1,   "°",  "卫星当前在轨道上的位置"),
        ]
        self.rows = {}
        for key, label, lo, hi, init, res, unit, hint in specs:
            row = ParamRow(self, label, lo, hi, init, res, unit,
                           on_change=self.on_change)
            row.pack(side=tk.TOP, fill=tk.X, padx=6, pady=0)
            tk.Label(self, text=hint, bg=PANEL, fg=GRAY, font=UI_FONT_S,
                     anchor="w").pack(side=tk.TOP, fill=tk.X, padx=28)
            self.rows[key] = row

        # 物理边界警告条（近地点穿地时由 main 置红字提示，平时隐藏）
        self.warn_label = tk.Label(self, text="", bg=PANEL, fg="#ff5252",
                                   font=UI_FONT_S, anchor="w",
                                   wraplength=280, justify=tk.LEFT)
        self.warn_label.pack(side=tk.TOP, fill=tk.X, padx=6, pady=(2, 0))

        # ================= 2. 预设轨道 =================
        make_section(self, "预设轨道")
        # 点击预设 → 回写六根数滑块并触发一次 on_change；数值出处见各行注释
        presets = [
            # 国际空间站：约 420 km 高度，倾角 51.6°（NASA 公开轨道参数）
            ("LEO/ISS",   dict(a=6798,  e=0.001, i=51.6, Om=30, w=0,   nu=0)),
            # 太阳同步晨昏轨道：600 km 高度，i≈97.8°（J2 使 Ω 每天 +0.985° 跟随太阳）
            ("SSO晨昏",   dict(a=6978,  e=0.001, i=97.8, Om=30, w=0,   nu=0)),
            # GPS 导航星：a≈26560 km（约 20200 km 高度），倾角 55°
            ("MEO/GPS",   dict(a=26560, e=0.001, i=55.0, Om=30, w=0,   nu=0)),
            # 地球静止轨道：a=42164 km（35786 km 高度），近赤道圆轨道
            ("GEO",       dict(a=42164, e=0.001, i=0.1,  Om=30, w=0,   nu=0)),
            # 闪电轨道（苏联 Molniya 通信星）：e=0.74，i=63.4° 临界倾角冻结 ω，
            # ω=270° 使远地点悬于北半球上空
            ("Molniya闪电", dict(a=26600, e=0.74, i=63.4, Om=30, w=270, nu=0)),
            # 地球同步转移轨道：a≈24505 km，e=0.725，i=28.5°（卡纳维拉尔角纬度）
            ("GTO",       dict(a=24505, e=0.725, i=28.5, Om=30, w=0,   nu=0)),
        ]
        btn_grid = tk.Frame(self, bg=PANEL)
        btn_grid.pack(side=tk.TOP, fill=tk.X, padx=8, pady=2)
        for idx, (name, p) in enumerate(presets):
            _make_btn(btn_grid, name,
                      lambda p=p: self._apply_preset(p)).grid(
                row=idx // 3, column=idx % 3, padx=2, pady=2, sticky="ew")
        for c in range(3):
            btn_grid.columnconfigure(c, weight=1)

        # ================= 3. 摄动模型（物理开关） =================
        make_section(self, "摄动模型（物理开关）")
        # J2 地球扁率摄动（默认开）；J2 初值取 EGM96 实测 1.0826e-3
        self.var_j2 = tk.BooleanVar(value=True)
        make_check(self, "J2 地球扁率摄动", self.var_j2,
                   self.on_change).pack(side=tk.TOP, fill=tk.X, padx=8)
        self.row_j2 = ParamRow(self, "J2 值", 0, 2e-3, 1.0826e-3, 1e-5,
                               on_change=self.on_change, sci=True)
        self.row_j2.pack(side=tk.TOP, fill=tk.X, padx=6)

        # 大气阻力（默认关）：Cd 典型 2.2；
        # A/m 初值 0.067 m²/kg ≈ 150 kg 卫星 / 10 m² 迎风面积
        self.var_drag = tk.BooleanVar(value=False)
        make_check(self, "大气阻力", self.var_drag,
                   self.on_change).pack(side=tk.TOP, fill=tk.X, padx=8)
        self.row_cd = ParamRow(self, "Cd 阻力系数", 1.0, 4.0, 2.2, 0.1,
                               on_change=self.on_change)
        self.row_cd.pack(side=tk.TOP, fill=tk.X, padx=6)
        self.row_drag_am = ParamRow(self, "A/m 面质比", 0.001, 0.1, 0.067,
                                    0.001, "m²/kg", on_change=self.on_change)
        self.row_drag_am.pack(side=tk.TOP, fill=tk.X, padx=6)

        # 第三体引力（默认关）
        self.var_sun = tk.BooleanVar(value=False)
        make_check(self, "太阳第三体引力", self.var_sun,
                   self.on_change).pack(side=tk.TOP, fill=tk.X, padx=8)
        self.var_moon = tk.BooleanVar(value=False)
        make_check(self, "月球第三体引力", self.var_moon,
                   self.on_change).pack(side=tk.TOP, fill=tk.X, padx=8)

        # 太阳光压（默认关）：Cr 典型 1.3（部分吸收部分反射），A/m 独立一个
        self.var_srp = tk.BooleanVar(value=False)
        make_check(self, "太阳光压", self.var_srp,
                   self.on_change).pack(side=tk.TOP, fill=tk.X, padx=8)
        self.row_cr = ParamRow(self, "Cr 光压系数", 1.0, 2.0, 1.3, 0.01,
                               on_change=self.on_change)
        self.row_cr.pack(side=tk.TOP, fill=tk.X, padx=6)
        self.row_srp_am = ParamRow(self, "A/m 面质比", 0.001, 0.1, 0.067,
                                   0.001, "m²/kg", on_change=self.on_change)
        self.row_srp_am.pack(side=tk.TOP, fill=tk.X, padx=6)

        # ================= 4. 显示选项（默认全开） =================
        make_section(self, "显示选项")
        disp = [
            ("ref_orbit",     "参考轨道"),
            ("orbit_plane",   "轨道面"),
            ("equator_plane", "赤道面"),
            ("arcs",          "角度弧(i/Ω/ω/ν)"),
            ("trail",         "卫星轨迹"),
            ("earth_spin",    "地球自转"),
            ("axes",          "坐标轴"),
            ("vernal",        "春分点方向"),
        ]
        self.disp_vars = {}
        chk_grid = tk.Frame(self, bg=PANEL)
        chk_grid.pack(side=tk.TOP, fill=tk.X, padx=8, pady=2)
        for idx, (key, text) in enumerate(disp):
            var = tk.BooleanVar(value=True)
            self.disp_vars[key] = var
            make_check(chk_grid, text, var, self.on_change).grid(
                row=idx // 2, column=idx % 2, sticky="w", padx=2)

    # ---------------- 对外接口 ----------------
    def _apply_preset(self, p):
        """预设按钮：回写六根数滑块（set 不逐行触发），最后统一通知一次。"""
        self.set_elements(**p)
        self.on_change()

    def get_elements(self):
        """当前六根数 dict(a,e,i,Om,w,nu)：a 单位 km，角度单位度。"""
        return {k: row.get() for k, row in self.rows.items()}

    def get_perturb(self):
        """摄动配置 dict（A/m 单位 m²/kg）。"""
        return dict(
            use_j2=self.var_j2.get(), j2=self.row_j2.get(),
            use_drag=self.var_drag.get(), cd=self.row_cd.get(),
            drag_am=self.row_drag_am.get(),
            use_sun=self.var_sun.get(), use_moon=self.var_moon.get(),
            use_srp=self.var_srp.get(), cr=self.row_cr.get(),
            srp_am=self.row_srp_am.get())

    def get_display(self):
        """显示开关 dict(ref_orbit/orbit_plane/equator_plane/arcs/trail/earth_spin/axes/vernal)。"""
        return {k: v.get() for k, v in self.disp_vars.items()}

    def set_elements(self, a, e, i, Om, w, nu):
        """程序回写六根数滑块（不触发 on_change）。"""
        for key, val in (("a", a), ("e", e), ("i", i),
                         ("Om", Om), ("w", w), ("nu", nu)):
            self.rows[key].set(val)

    def set_warning(self, text):
        """显示物理边界警告（红字）。"""
        self.warn_label.config(text=text)

    def clear_warning(self):
        """清除物理边界警告。"""
        self.warn_label.config(text="")


# 公式卡文本（等宽字体显示，公式出处见 docs/ARCHITECTURE.md 第 4 节）
FORMULA_TEXT = """\
活力公式    v² = μ(2/r − 1/a)
周期        T = 2π√(a³/μ)
J2节点漂移  dΩ/dt = −(3/2)J2·n(Re/p)²cos i
近地点进动  dω/dt = (3/4)J2·n(Re/p)²(5cos²i − 1)
大气阻力    a = −½ρCd(A/m)v²
p = a(1−e²) 半通径
n = √(μ/a³) 平均运动
Re 地球赤道半径"""


class RightPanel(tk.Frame):
    """右栏（300px）：osculating 实时数据 / 摄动理论速率 / 星下点 / 公式卡。

    全部只读，由 main 周期性调用 update_data() 刷新。
    """

    def __init__(self, parent):
        super().__init__(parent, bg=PANEL, width=300)
        self.pack_propagate(False)

        # 顶部仿真时钟（update_data 刷新）
        self.lbl_clock = tk.Label(self, text="—", bg=PANEL, fg=ACCENT,
                                  font=MONO, anchor="w")
        self.lbl_clock.pack(side=tk.TOP, fill=tk.X, padx=8, pady=(6, 0))
        # 右下角 FPS 小字
        self.lbl_fps = tk.Label(self, text="", bg=PANEL, fg=GRAY,
                                font=MONO_S, anchor="e")
        self.lbl_fps.pack(side=tk.BOTTOM, fill=tk.X, padx=8)

        # ============ 1. 当前轨道数据（osculating 瞬时值） ============
        make_section(self, "当前轨道数据（osculating 瞬时值）")
        self.osc_labels = {}
        for key, name, unit in [
            ("a",      "a 半长轴",   "km"),   ("e",  "e 偏心率",   ""),
            ("i",      "i 倾角",     "°"),    ("Om", "Ω 升交点",   "°"),
            ("w",      "ω 近地点",   "°"),    ("nu", "ν 真近点角", "°"),
            ("period", "轨道周期",   "min"),  ("rp", "近地点",     "km"),
            ("ra",     "远地点",     "km"),   ("energy", "轨道能量", "km²/s²"),
            ("h",      "角动量",     "km²/s"), ("v",  "卫星速度",  "km/s"),
            ("alt",    "高度",       "km"),
        ]:
            self.osc_labels[key] = self._table_row(name, unit)

        # ============ 2. 摄动效应（理论速率） ============
        make_section(self, "摄动效应（理论速率）")
        self.rate_labels = {}
        for key, name, unit in [
            ("dOm",   "dΩ/dt 升交点漂移", "°/day"),
            ("dw",    "dω/dt 近地点进动", "°/day"),
            ("dM",    "dM/dt 平近点修正", "°/day"),
            ("da_dt", "da/dt 阻力衰减",   "km/day"),
        ]:
            self.rate_labels[key] = self._table_row(name, unit)

        # ============ 3. 星下点 ============
        make_section(self, "星下点")
        self.sub_labels = {}
        for key, name, unit in (("lat", "纬度", "°"),
                                ("lon", "经度", "°"),
                                ("alt", "高度", "km")):
            self.sub_labels[key] = self._table_row(name, unit)
        # 星下点轨迹图容器：main 会把 GroundTrackCanvas 挂载到这里
        self.gt_frame = tk.Frame(self, bg=PANEL)
        self.gt_frame.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)

        # ============ 4. 物理公式 ============
        make_section(self, "物理公式")
        self.formula = tk.Text(self, height=8, bg=ENTRY_BG, fg=FG,
                               font=MONO_S, relief=tk.FLAT, wrap=tk.NONE)
        self.formula.pack(side=tk.TOP, fill=tk.X, padx=8, pady=4)
        self.formula.insert(tk.END, FORMULA_TEXT)
        self.formula.config(state=tk.DISABLED)   # 只读公式卡

    def _table_row(self, name, unit=""):
        """只读表格行：名称 + 等宽数值 + 灰色单位，返回数值 Label。"""
        f = tk.Frame(self, bg=PANEL)
        f.pack(side=tk.TOP, fill=tk.X, padx=10, pady=0)
        tk.Label(f, text=name, bg=PANEL, fg=FG, width=15, anchor="w",
                 font=UI_FONT_S).pack(side=tk.LEFT)
        val = tk.Label(f, text="—", bg=PANEL, fg=ACCENT, anchor="e", font=MONO)
        val.pack(side=tk.LEFT, fill=tk.X, expand=True)
        if unit:
            tk.Label(f, text=" " + unit, bg=PANEL, fg=GRAY,
                     anchor="w", font=UI_FONT_S).pack(side=tk.LEFT)
        return val

    @staticmethod
    def _set(lbl, v, fmt):
        """写数值 Label；None 显示 "—"（如未开启的摄动速率）。"""
        lbl.config(text="—" if v is None else fmt.format(v))

    def update_data(self, osc, rates, latlon, jd_str, fps):
        """刷新全部只读显示。

        osc    : dict(a,e,i,Om,w,nu,period_s,rp,ra,energy,h[,v,alt]) osculating 瞬时值
        rates  : dict(dOm,dw,dM,da_dt) 理论速率；None → 显示 "—"
        latlon : (lat_deg, lon_deg, alt_km) 星下点
        jd_str : 仿真时钟字符串；fps : 帧率
        """
        self.lbl_clock.config(text=jd_str)
        self.lbl_fps.config(text=f"FPS {fps:.0f}")

        L = self.osc_labels
        self._set(L["a"],  osc.get("a"),  "{:.1f}")
        self._set(L["e"],  osc.get("e"),  "{:.5f}")
        self._set(L["i"],  osc.get("i"),  "{:.2f}")
        self._set(L["Om"], osc.get("Om"), "{:.2f}")
        self._set(L["w"],  osc.get("w"),  "{:.2f}")
        self._set(L["nu"], osc.get("nu"), "{:.2f}")
        ps = osc.get("period_s")
        self._set(L["period"], None if ps is None else ps / 60.0, "{:.1f}")
        self._set(L["rp"], osc.get("rp"), "{:.1f}")
        self._set(L["ra"], osc.get("ra"), "{:.1f}")
        self._set(L["energy"], osc.get("energy"), "{:.3f}")
        self._set(L["h"],  osc.get("h"),  "{:.1f}")
        self._set(L["v"],  osc.get("v"),  "{:.3f}")
        self._set(L["alt"], osc.get("alt"), "{:.1f}")

        R = self.rate_labels
        self._set(R["dOm"],   rates.get("dOm"),   "{:+.4f}")
        self._set(R["dw"],    rates.get("dw"),    "{:+.4f}")
        self._set(R["dM"],    rates.get("dM"),    "{:+.4f}")
        self._set(R["da_dt"], rates.get("da_dt"), "{:.4f}")

        lat, lon, alt = latlon
        self._set(self.sub_labels["lat"], lat, "{:+.2f}")
        self._set(self.sub_labels["lon"], lon, "{:+.2f}")
        self._set(self.sub_labels["alt"], alt, "{:.1f}")


class BottomPanel(tk.Frame):
    """底栏（70px）：播放控制 / 对数速度滑块 / 仿真时钟 / 周期进度条。

    on_control(cmd, value)：cmd ∈ {'play','pause','step','reset','speed'}；
    仅 speed 时 value 为倍率（float），其余 cmd 的 value 为 None。
    """

    def __init__(self, parent, on_control):
        super().__init__(parent, bg=PANEL, height=70)
        self.pack_propagate(False)
        self.on_control = on_control
        self._playing = False

        # ---- 播放控制按钮（▶/⏸ 同一个按钮切换文本） ----
        self.btn_play = _make_btn(self, "▶ 开始", self._toggle_play)
        self.btn_play.pack(side=tk.LEFT, padx=(10, 4), pady=8)
        _make_btn(self, "⏭ 单步",
                  lambda: self.on_control("step", None)).pack(side=tk.LEFT, padx=4)
        _make_btn(self, "⟲ 重置",
                  lambda: self.on_control("reset", None)).pack(side=tk.LEFT, padx=4)

        # ---- 速度滑块：对数刻度 1× ~ 100000× ----
        # 滑块位置 s ∈ [0,5] 线性滑动，倍率 = 10**s（对数映射）：
        # 每滑动 1 格倍率 ×10，符合仿真"时间尺度"的数量级直觉。
        tk.Label(self, text="速度", bg=PANEL, fg=FG,
                 font=UI_FONT).pack(side=tk.LEFT, padx=(18, 2))
        self.speed_scale = tk.Scale(
            self, from_=0, to=5, resolution=0.01, orient=tk.HORIZONTAL,
            showvalue=False, length=150, command=self._on_speed,
            bg=PANEL, fg=FG, troughcolor=ENTRY_BG,
            highlightthickness=0, activebackground=ACCENT, bd=0)
        self.speed_scale.set(0)   # 初始 1×（set 不触发 command）
        self.speed_scale.pack(side=tk.LEFT, pady=4)
        self.lbl_speed = tk.Label(self, text="1×", bg=PANEL, fg=ACCENT,
                                  font=MONO, width=10, anchor="w")
        self.lbl_speed.pack(side=tk.LEFT, padx=4)

        # ---- 仿真时钟（UTC 时间 + 已流逝天数，等宽字体） ----
        self.lbl_time = tk.Label(self, text="—", bg=PANEL, fg=FG,
                                 font=MONO, anchor="w")
        self.lbl_time.pack(side=tk.LEFT, padx=18)

        # ---- 周期进度条：ν 在一个轨道周期中的位置（0~360° 填充比例） ----
        prog = tk.Frame(self, bg=PANEL)
        prog.pack(side=tk.LEFT, padx=12, fill=tk.X, expand=True)
        tk.Label(prog, text="周期进度 ν", bg=PANEL, fg=GRAY,
                 font=UI_FONT_S, anchor="w").pack(side=tk.TOP, fill=tk.X)
        self.prog_canvas = tk.Canvas(prog, height=8, bg=ENTRY_BG,
                                     highlightthickness=0)
        self.prog_canvas.pack(side=tk.TOP, fill=tk.X, pady=2)
        self._prog_rect = self.prog_canvas.create_rectangle(
            0, 0, 0, 8, fill=ACCENT, width=0)

    # ---------------- 内部事件 ----------------
    def _toggle_play(self):
        """▶/⏸ 切换：更新状态与按钮文本，并通知外部 play/pause。"""
        self.set_playing(not self._playing)
        self.on_control("play" if self._playing else "pause", None)

    def _on_speed(self, s):
        """速度滑块：对数映射 10^s 得倍率，刷新标签并通知外部。"""
        mult = 10 ** float(s)
        self.lbl_speed.config(text=self._fmt_mult(mult))
        self.on_control("speed", mult)

    @staticmethod
    def _fmt_mult(m):
        """倍率紧凑显示：1.0× / 2.5× / 1000×。"""
        return f"{m:.1f}×" if m < 10 else f"{m:.0f}×"

    # ---------------- 对外接口 ----------------
    def set_time(self, jd_str, elapsed_days):
        """刷新仿真时钟：UTC 时间串 + 已流逝天数。"""
        self.lbl_time.config(text=f"{jd_str}   +{elapsed_days:.2f} 天")

    def set_progress(self, nu_deg):
        """周期进度条：按 ν（0~360°）填充比例。"""
        frac = math.fmod(nu_deg, 360.0) / 360.0
        w = max(self.prog_canvas.winfo_width(), 2)
        self.prog_canvas.coords(self._prog_rect, 0, 0, w * frac, 8)

    def set_playing(self, playing):
        """设置播放状态，切换 ▶/⏸ 按钮文本。"""
        self._playing = bool(playing)
        self.btn_play.config(text="⏸ 暂停" if self._playing else "▶ 开始")
