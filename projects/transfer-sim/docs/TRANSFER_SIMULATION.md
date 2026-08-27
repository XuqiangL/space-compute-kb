# 地月转移轨道仿真：从公式到 CPU/GPU 实现（完整链路讲解）

> 本文档回答三个问题：
> 1. **输入是什么** → 2. **用了哪些公式/模型、对应哪些代码** → 3. **如何输出一条完整转移轨道**；
> 以及第四个问题：**输入输出是不是时序空间坐标系张量（3D/4D/5D/6D）**。
> 全部公式来自 `gmat-architecture-docs/math-deep-dive/`（MD-01~MD-14），代码把 GMAT 源码中的
> 封装**逐公式迁移**为独立函数（注释内含公式原文与讲解），CPU 实现即 golden，
> CUDA 版逐公式给出对应 kernel，并做了 CPU/GPU 数值对比与真实 GMAT 交叉验证。

---

## 一、输入是什么（场景定义）

本仿真是 **patched-conic（拼接圆锥曲线）地月转移**，与 GMAT 的实际任务完全同构：

| 输入项 | 值 | 来自哪个公式/常量 |
|---|---|---|
| 停泊轨道要素 `el[6]` | a=6578.1363 km（200 km 圆轨道），e=0，i=28.5°，Ω=ω=θ=0 | 用户定义（6 维矢量） |
| TLI 冲量 Δv | +3.14 km/s（顺向，沿速度方向） | MD-10 机动模型 |
| 航天器质量 m0 | 1000 kg（仅 `--finite-burn` 模式使用） | MD-10 |
| 发动机 T/Isp | 500 N / 300 s（有限推力模式） | MD-10 |
| 力模型配置 | 地球点质量 + J2 + 月球第三体；大气/光压关闭 | MD-08/09 |
| 积分器 | PrinceDormand45（7 级 RK 4(5)，系数逐字取自 GMAT 源码） | MD-04 |
| 容差/步长 | tol=1e-11，h0=60 s，自适应步长 | MD-04 |
| 历元 | MJD_A1 = 21544.50037（J2000，= GmatDefaults `TWO_BODY_EPOCH`） | MD-01 |
| 天体常数 | μ⊕=398600.4415，R⊕=6378.1363，μ☾=4902.8005821478，a☾=384400 km | `GmatDefaults.hpp:159/186/299/314` |

**输入本质上就是一个 1 维张量（标量集合）+ 一个 6 维状态矢量**：所有标量参数与
初始状态 `(r0, v0)`（km, km/s）共同构成积分初值问题 `ẋ = f(x, t; θ)`，θ 为参数张量。

## 二、公式与代码清单（每个公式 = 一个函数 = 一个单元测试）

| # | 公式（LaTeX） | 我们的函数 | GMAT 源码出处 | 章 |
|---|---|---|---|---|
| 1 | $a=-\mu\,r/\|r\|^3$ | `accel_point_mass` | `PointMassForce.cpp` | MD-08 |
| 2 | $a_{J2}=-\frac32 J_2\frac{\mu}{r^2}\left(\frac{R_e}{r}\right)^2\left[\frac xr(1-5\frac{z^2}{r^2}),\frac yr(1-5\frac{z^2}{r^2}),\frac zr(3-5\frac{z^2}{r^2})\right]$ | `accel_j2` | `Harmonic.cpp`（Pines 递推 n=2 特例） | MD-08 |
| 3 | $a_{3b}=-\mu_b\left(\frac{d}{\|d\|^3}+\frac{r_b}{\|r_b\|^3}\right),\ d=r_{sc}-r_b$ | `accel_third_body` | `PointMassForce.cpp` 第三体间接项 | MD-08 |
| 4 | $\dot r=v,\ \dot v=a_{pm}+a_{J2}+a_{3b}$ | `derivatives_keplerian` | `ODEModel::GetDerivativesForState` | MD-08 |
| 5 | 3-1-3 旋转 + 近焦点系状态（$p=a(1-e^2), r=p/(1+e\cos\theta), h=\sqrt{\mu p}$） | `cartesian_from_kepler` | `StateConversionUtil.cpp` | MD-03 |
| 6 | 角动量/偏心率矢量反解 + 象限修正 | `kepler_from_cartesian` | `StateConversionUtil.cpp` | MD-03 |
| 7 | $M=E-e\sin E$（Newton 迭代） | `anomaly_E_from_M` | `StateConversionUtil.cpp` | MD-03 |
| 8 | $\tan\frac{\theta}{2}=\sqrt{\frac{1+e}{1-e}}\tan\frac E2$ | `anomaly_TA_from_E` | `StateConversionUtil.cpp` | MD-03 |
| 9 | $\varepsilon=v^2/2-\mu/r$ | `orbital_energy` | 轨道能量（检验量） | MD-03 |
| 10 | $r_{SOI}=a(\mu_b/\mu_p)^{2/5}$ | `soi_radius` | patched-conic 判据 | MD-03 |
| 11 | $\dot m=-T/(I_{sp}g_0)$ | `mdot_from_isp` | `ChemicalThruster.cpp` | MD-10 |
| 12 | $m_f=m_0\exp(-\Delta v/(I_{sp}g_0))$ | `mass_after_dv` | `ImpulsiveBurn` 燃耗 | MD-10 |
| 13 | $a=T/m\cdot\hat u$ | `accel_finite_thrust` | `FiniteBurn/FiniteThrust` | MD-10 |
| 14 | $k_i=f(t+a_ih,\ y+h\sum_j b_{ij}k_j);\ y_{n+1}=y+h\sum c_i k_i;\ err=h\sum e_i k_i$ | `rk45_step` | `PrinceDormand45.cpp:143-209` **系数逐字迁移** | MD-04 |
| 15 | $h_{new}=h\cdot\max(0.2,\min(5,0.9(tol/\|err\|)^{1/5}))$ | `rk45_adaptive` | `RungeKutta::AdaptStep` | MD-04 |
| 16 | $JD=MJD+2430000.5$（A.1 约定） | `jd_from_mjd` | `GmatTime/TimeTypes` | MD-01 |
| 17 | Fliegel–Van Flandern 公历→儒略日 | `jd_from_ymdhms` | `DateUtil.cpp` | MD-01 |
| 18 | $\|v\|,\ a\cdot b,\ a\times b$ | `norm/dot/cross` | `Rvector`（MD-06） | MD-06 |

代码位置：`transfer-sim/include/gmath/*.hpp`（每函数注释含公式原文、推导要点、
GMAT 对应实现位置）；单元测试 `transfer-sim/tests/test_formulas.cpp`（47 个用例，
每公式至少一个解析参照测试）。

## 三、完整数据流：如何输出一条转移轨道

```
 输入(标量+要素)                    Phase-0 要素→状态
   el[6], Δv, 力模型参数 ──► cartesian_from_kepler ──► (r0,v0) 停泊轨道状态
                                                     │ +3.14 km/s 顺向冲量（burn_direction_velocity）
                                                     ▼
  Phase-1 定相跑（无月球）                     Phase-2 地心段（点质量+J2+月球）
   rk45_adaptive 积分至 r=384400 km ──► 飞行时间/到达经度 ──► 月球初始相位对齐
                                                     ▼
                                    rk45_adaptive 积分，每步:
                                    a = accel_point_mass + accel_j2 + accel_third_body
                                    判据: |r_sc - r_moon| ≤ r_SOI(66183 km) ──► SOI 入口状态
                                                     ▼
  Phase-3 月心段                                输出
   切中心体 μ☾，转月心状态 ──► 积分至近月点 ──► (rp=7798.4 km, alt=6060 km,
                                               vp=1.438 km/s, T=2.93 天)
```

**实际运行结果**（`transfer-sim/data/summary.txt`）：
- 无月定相飞行时间 3.761 天（到 384400 km）；含月球 SOI 进入 2.927 天（月球引力提前拉近）
- 近月点 rp = 7798.4 km（高度 6060.2 km），vp = 1.4380 km/s（v∞ ≈ 0.9 km/s，经典量级）
- 输出文件：`trajectory_earth.csv`（N×13 张量：t, s/c 状态 6, 月球位置 3, 距月 1）、
  `trajectory_moon.csv`（N×7）、`summary.txt`

## 四、回答：输入输出是不是"时序空间坐标系张量"？

**是。** 轨道仿真的核心数据全部是**沿时间轴排列的坐标系张量**，按维度展开：

| 维度 | 形状 | 本仿真/ GMAT 中的实例 |
|---|---|---|
| 1D | N | 质量时间序列、能量时间序列、仰角序列（标量轨迹） |
| 2D | N×7 | **单条转移轨道**（t, x, y, z, vx, vy, vz）——本仿真的主输出 `trajectory_*.csv` |
| 3D | M×N×7 | GPU 批量轨迹（256 条蒙特卡洛轨迹的 3D 张量，`tensors.hpp::traj3d_offset`） |
| 3D | N×6×6 | 状态转移矩阵/协方差沿时间的 3D 张量（GMAT `PropagationStateManager` STM、估计协方差） |
| 4D | M×N×6×6 | 批量 STM/协方差系综（蒙特卡洛 OD），`tensors.hpp::stm4d_offset` |
| 5D | K×M×N×6×D | 测量偏导张量：K 测站 × M 轨迹 × N 时刻 × 6 状态 × D 参数（MD-12 的 H 矩阵族） |
| 6D | S×N×6×(6+p)×B×C | 积分器级张量：RK 级 × 步 × 状态 × (状态+参数) 导数（MD-04 k[7][6] 的批量化） |

存储约定与 GMAT 的 `Rmatrix` 完全一致：**行主序一维扁平数组**，
元素 `(i,j,k)` 偏移 = `((i·d2+j)·d3+k)`（MD-06 §6.2）。CUDA 版直接用同一索引公式
（`tensors.hpp` 的 `traj3d_offset/stm4d_offset`）把张量平铺进显存，
因此"轨迹 = 3D/4D 张量"在 GPU 上就是 `double* traj` 的批量读写。

## 五、CPU golden / GPU CUDA / 真实 GMAT 三方对比

| 对比 | 方法 | 结果 |
|---|---|---|
| 单元测试 | 47 个解析参照用例 | **47/47 通过** |
| 逐公式 CPU vs GPU | 1048576 个随机输入，同一份公式源码（`__host__ __device__`） | max\|diff\| = 1.3e-15 ~ 5.8e-11（机器精度级） |
| 定步权威对比 | CPU/GPU 相同 h、相同 20000 步 PD45 | 位置差 **2.9e-8 km**（0.03 mm），速度差 1.3e-13 km/s |
| 轨迹级对比 | GPU 名义轨迹 vs CPU golden 逐点插值 | 位置差 ≤ 6.2e-3 km（受 30 s 采样插值限制，米级） |
| **真实 GMAT 交叉验证** | `GmatConsole` 跑同场景 `reference_1day.script`（点质量+JGM2 2×0+PD45 1e-11，1 天） | 位置差 **最大 15 m**（相对尺度 4e-8），速度差 1e-7 km/s |
| 性能 | CPU 单轨迹 5.37 ms（20 次平均） vs GPU 批量 256 轨迹 196 ms（0.76 ms/轨迹） | GPU 单轨迹 **7×**，批量吞吐 **1308 轨迹/秒** |

## 六、如何复现

```bat
cd L:\gmat888\transfer-sim
build_cpu.bat          :: MSVC 编译 CPU golden + 单元测试
build\test_formulas.exe:: 47 个公式单元测试
build\main_cpu.exe --out data      :: 地月转移 golden 输出
build_gpu.bat          :: nvcc 编译 CUDA（每公式 kernel + 批量传播）
build\main_gpu.exe --M 256 --out data   :: 逐公式对比 + 批量传播 + 报告
python scripts\compare_trajectories.py  :: CPU/GPU 轨迹逐点对比
:: GMAT 交叉验证：
copy gmat\reference_1day.script C:\Users\Administrator.000\Downloads\gmat-win-R2026a\bin
GmatConsole --run reference_1day.script   （输出在 ...\output\gmat_ref_1day.txt）
build\main_cpu.exe --ref --out data       （同场景 CPU 输出，对比末行）
```
