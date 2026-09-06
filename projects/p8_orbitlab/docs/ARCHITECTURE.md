# OrbitLab（p8_orbitlab）开发架构 —— 卫星轨道动力学教学仿真器

> 定位：工业级物理内核 + 教学级可视化的卫星轨道动力学软件。
> 物理常量与公式迁移自 GMAT 源码（见 transfer-sim 与 math-deep-dive），全部代码中文注释、公式就地标注。
> 零依赖：纯 Python 标准库（tkinter + math），任何机器可跑。

## 1. 总体架构图

```mermaid
graph TD
    subgraph UI[表现层 tkinter]
        LP[panels.LeftPanel<br/>六根数滑块/预设/摄动开关/显示开关]
        VP[3D 视口 Canvas<br/>地球+轨道+角度弧]
        RP[panels.RightPanel<br/>实时数据/摄动率/公式卡]
        BP[panels.BottomPanel<br/>时间轴:播放/暂停/步进/速度]
        GT[groundtrack.GroundTrackCanvas<br/>星下点轨迹图]
    end

    subgraph APP[应用层]
        MAIN[main.OrbitLab<br/>状态机+动画循环 after 33ms]
    end

    subgraph PHYS[物理内核层]
        EL[elements.py<br/>六根数↔状态矢量/轨道采样]
        PB[perturbations.py<br/>J2/阻力/第三体/光压]
        PG[propagator.py<br/>Cowell RK4+DP45 传播器]
        CT[constants.py<br/>GMAT 常量/大气表/GMST]
    end

    subgraph GEO[几何渲染层]
        G3[geometry3d.py<br/>轨道面/角度弧/标记点采样]
        R3[render3d.py<br/>相机+透视投影+地球绘制]
    end

    LP -->|on_elements_changed| MAIN
    LP -->|on_perturb_changed| MAIN
    BP -->|on_time_control| MAIN
    MAIN -->|当前状态 y[6], jd| PG
    PG -->|加速度调用| PB
    MAIN -->|参考轨道六根数| EL
    EL --> G3
    G3 --> R3
    R3 --> VP
    MAIN -->|osculating 根数+摄动率| RP
    MAIN -->|惯性系位置序列| GT
```

## 2. 核心设计：双轨显示（教学灵魂）

| 显示对象 | 来源 | 视觉 | 物理意义 |
|---|---|---|---|
| 参考轨道 | 左栏六根数 → 开普勒椭圆解析采样 | 白色实线 + 青色轨道面 | "你设定的轨道" |
| 真实轨迹 | Cowell 数值积分（含勾选摄动） | 黄色轨迹线 + 红色卫星 | "摄动下实际走的轨道" |
| 角度弧 | 六根数几何采样 | i 绿 / Ω 紫 / ω 橙 / ν 红 | 六根数的几何定义 |

拖滑块 → 参考轨道/轨道面/角度弧**立即**重绘，卫星重置到新轨道 ν 处重新传播。

## 3. 坐标系与时间

- 惯性系：地心 J2000 赤道惯性系（X→春分点，Z→北极），单位 km / km/s / s
- 地固转换：GMST 近似（IAU 1982）：θ = 280.4606° + 360.9856473°·(JD−2451545.0)
- 历元：默认系统当前 UTC；内部用 JD 浮点

## 4. 物理模型（全部真实参数可调）

| 摄动 | 公式 | 来源 | 可调参数 |
|---|---|---|---|
| 中心引力 | a = −μr/r³ | PointMassForce.cpp | — |
| J2 带谐 | Vallado §10 惯性系三分量形式 | Harmonic.cpp n=2 退化 | 开关 + J2 值滑块 |
| 大气阻力 | a = −½ρ(h)Cd(A/m)v_rel²·v̂_rel，v_rel = v − ω⊕×r | DragForce.cpp + 指数大气 | 开关 + Cd + A/m |
| 第三体日/月 | a = −μ₃(d/d³ + r₃/r₃³)，d = r−r₃ | PointMassForce.cpp 间接项 | 日开关 + 月开关 |
| 太阳光压 | a = ν·P☉(AU/r)²·Cr(A/m)·r̂☉，圆柱阴影 ν∈{0,1} | SolarRadiationPressure.cpp | 开关 + Cr + A/m |

指数大气表（GMAT Exponential 模型同款分段）：h<100 不下延；100/150/200/…/1000 km 分段 (ρ0, H)。

右栏解析摄动率（与数值结果对照教学）：
- dΩ/dt = −(3/2)J2·n·(Re/p)²·cos i
- dω/dt = (3/4)J2·n·(Re/p)²·(5cos²i − 1)
- Ṁ = n·[1 + (3/4)J2·(Re/p)²·√(1−e²)·(3cos²i − 1)]

## 5. 模块 API 契约（并行开发接口，签名冻结）

### constants.py
```python
MU_EARTH = 398600.4415      # km^3/s^2（GmatDefaults.hpp:186）
RE_EARTH = 6378.1363        # km（GmatDefaults.hpp:159）
J2_EARTH = 1.0826269269e-3  # EGM96 −√5·C̄20
OMEGA_EARTH = 7.2921159e-5  # rad/s
AU_KM, MU_SUN, MU_MOON, P_SRP_1AU = 4.56e-6  # N/m^2
ATMOS_TABLE: list[(h0_km, rho0_kg_m3, H_km)]  # 分段指数大气
def atmos_density(h_km) -> float              # kg/m^3
def julian_date(y, mo, d, h=0, mi=0, s=0.0) -> float
def gmst_rad(jd) -> float                     # GMST 弧度
def jd_to_datetime_str(jd) -> str
```

### elements.py
```python
def elements_to_state(a, e, i_deg, Om_deg, w_deg, nu_deg, mu=MU_EARTH) -> (r3, v3)
def state_to_elements(r, v, mu=MU_EARTH) -> dict(a,e,i,Om,w,nu,rp,ra,period_s,energy,h)
def orbit_polyline(a, e, i_deg, Om_deg, w_deg, n=361) -> list[(x,y,z)]  # 全椭圆
def perigee_dir(i_deg, Om_deg, w_deg) -> (x,y,z)      # 近地点单位矢量
def node_dir(Om_deg) -> (x,y,z)                        # 升交线单位矢量
def angle_arc(center, u1, u2, radius, n=64) -> list    # 两方向间圆弧采样
```

### perturbations.py
```python
@dataclass PerturbConfig:
    use_j2: bool; j2: float
    use_drag: bool; cd: float; drag_area_m2: float; mass_kg: float
    use_sun: bool; use_moon: bool
    use_srp: bool; cr: float; srp_area_m2: float
def accel_j2(r, j2) -> a3
def accel_drag(r, v, cd, area_m2, mass_kg, jd) -> a3
def accel_third_body(r, r_body, mu_body) -> a3
def accel_srp(r, r_sun, cr, area_m2, mass_kg) -> a3   # 含阴影因子
def sun_pos_geo(jd) -> r3      # 地心惯性系太阳位置（低精度黄经公式）
def moon_pos_geo(jd) -> r3     # 地心惯性系月球位置（圆轨道+倾角近似）
def total_accel(r, v, jd, cfg: PerturbConfig) -> a3
def j2_secular_rates(a, e, i_deg, j2=J2_EARTH) -> (dOm, dw, dM)  # deg/day
def drag_da_dt_km_day(a, e, cfg, jd) -> float
```

### propagator.py
```python
def rk4_step(f, t, y, h) -> y_new           # 经典 4 阶
class Propagator:
    def __init__(self, cfg: PerturbConfig)
    def reset(self, r3, v3, jd)             # 设初值
    def step(self, dt_s)                    # RK4 定步推进（内部子步长 ≤10s 自适应）
    state: list[6]; jd: float               # 当前状态/历元
```

### geometry3d.py（纯几何采样，不碰 tkinter）
```python
def orbit_plane_disc(a, e, i, Om, w, n_rings=4, n_seg=72) -> list[polyline]
def equator_disc(radius, n_rings=4, n_seg=72) -> list[polyline]
def all_angle_arcs(a, e, i, Om, w, nu, scale) -> dict(i=..., Om=..., w=..., nu=...)
def axes_lines(L) -> dict(X=..., Y=..., Z=...)
```

### render3d.py
```python
class Camera:  # 球坐标+透视投影（沿用 p7，dist 单位 km）
    project(p, w, h) -> (sx, sy, depth) | None
    rotate(daz, del_); zoom(factor); pan(dx, dy, w, h)
def draw_polylines(canvas, cam, lines, w, h, color, width=1, dash=None)
def draw_earth(canvas, cam, w, h, jd, rotate_on)   # 蓝球+经纬网+自转
def draw_marker(canvas, cam, p, w, h, color, label)
```

### groundtrack.py
```python
def inertial_to_latlon(r3, jd) -> (lat_deg, lon_deg, alt_km)
class GroundTrackCanvas(tk.Canvas):
    def set_track(points_latlon, current)  # 网格+赤道+轨迹+当前点
```

### panels.py
```python
class LeftPanel(tk.Frame):
    def __init__(self, parent, on_change: callable)   # 任何控件变化→on_change()
    def get_elements() -> dict(a,e,i,Om,w,nu)         # 当前六根数
    def get_perturb() -> PerturbConfig
    def get_display() -> dict(参考轨道/轨道面/赤道面/角度弧/轨迹/地球自转/地影)
class RightPanel(tk.Frame):
    def update_data(elements_osc, rates, latlon, jd, fps)
class BottomPanel(tk.Frame):
    def __init__(self, parent, on_control: callable)  # play/pause/step/reset/speed
    def set_time(jd, elapsed_s, speed)
```

## 6. UI 布局（对照效果图）

```
┌──────────────┬────────────────────────────────┬──────────────┐
│ 左栏 300px    │                                │ 右栏 300px    │
│ 轨道六根数     │                                │ 当前轨道数据   │
│  a/e/i/Ω/ω/ν │         3D 视口                 │  osculating  │
│  滑块+数值框   │   地球/轨道/轨道面/角度弧         │ 摄动速率       │
│ 预设轨道按钮   │   卫星+轨迹                     │  dΩ/dt dω/dt  │
│ 摄动开关+参数  │                                │  阻力 da/dt   │
│ 显示开关      │                                │ 星下点轨迹图   │
│              │                                │ 物理公式卡     │
├──────────────┴────────────────────────────────┴──────────────┤
│ 底栏: ▶/⏸/步进/重置 │ 速度滑块 1×~10000× │ 仿真时钟 │ 周期进度 │
└──────────────────────────────────────────────────────────────┘
```

配色（与效果图一致）：轨道面青 #00BCD4 半透明网格、赤道面灰网格、i 绿 #4CAF50、
Ω 紫 #9C27B0、ω 橙 #FF9800、ν 红 #F44336、卫星红、地球蓝、背景深空黑 #0a0e1a。

## 7. 主循环状态机（main.py）

```
拖动滑块/开关变化 → 读六根数 → elements_to_state → Propagator.reset
                 → 重算参考轨道线/轨道面/角度弧 → 清轨迹
播放中（after 33ms）→ dt_sim = dt_wall × speed
                 → Propagator.step(dt_sim)（内部子步 ≤10 s）
                 → 轨迹追加当前点（抽稀）
                 → state_to_elements 反算 osculating → 右栏刷新
                 → 星下点追加 → 地面轨迹图刷新
                 → 3D 视口重绘（地球自转随 jd）
```

## 8. 测试计划（test_orbitlab.py）

| 测试 | 锁定数值 |
|---|---|
| 六根数↔状态往返 | 误差 <1e-8 |
| 开普勒传播 10 圈 | 能量/角动量守恒 <1e-9，回到起点 |
| J2 数值 vs 解析 | 传播 1 天 dΩ 与解析式偏差 <5% |
| 阻力单调衰减 | da/dt < 0 且 a 单调降 |
| 光压阴影 | 阴影内 SRP 加速度 = 0 |
| GMST | J2000 时刻 θ = 280.4606° |
| 周期 | 开普勒第三定律 T=2π√(a³/μ) |
| 预设轨道合法性 | 全部 rp > Re+100 km（Molniya 等） |

## 9. 分工与集成

- Agent A（物理内核）：constants / elements / perturbations / propagator
- Agent B（几何渲染）：render3d / geometry3d / groundtrack
- Agent C（UI 面板）：panels.py
- 主代理集成：main.py + test_orbitlab.py + README.md + 全测试 + 冒烟运行
