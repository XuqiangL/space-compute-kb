---
name: aerospace-engineering
description: 航天工程全域知识库与仿真工具集——覆盖空间环境、轨道力学与星座设计、卫星平台（OBDH/AOCS/EPS/推进）、算力载荷与太空服务器、热控散热、辐射可靠性、通信与星间组网、结构与发射环境、地面系统与星座运营、工程流程法规、商业模式、全流程任务案例，以及 GMAT 工业级参照（249 页中文文档 + 架构/公式解析）和 9 个可运行仿真项目（p1-p8 Python + transfer-sim C++/CUDA）。当涉及卫星/航天器设计、太空算力、轨道计算、热/辐射/链路/结构分析、星座运营、航天合规、任务仿真、GMAT 使用或二次开发时使用。
---

# 航天工程（aerospace-engineering）

本技能是 space-compute-kb 的总入口：12 个知识模块 + 9 个仿真项目 + GMAT 工业参照。
**所有路径相对仓库根目录；内容文件原地使用，不移动。**

## 一、领域导航（问题 → 文档）

| 领域 | 文档 | 何时查 |
|---|---|---|
| 空间环境与总体 | `01-航天总体与空间环境.md` | 真空/热/辐射/原子氧/碎片机理、四大预算表、余量管理 |
| 轨道力学与星座 | `02-轨道力学与星座设计.md` | 活力公式、霍曼转移、J2/SSO、Walker 星座、ISL 几何、离轨 |
| 卫星平台 | `03-卫星平台分系统.md` | OBDH/FDIR、AOCS 姿控、电源 sizing、推进选型 |
| 算力载荷（主线） | `04-算力载荷与太空服务器.md` | 器件三路线、四层容错栈、存算传一体、SWaP-C 权衡 |
| 热控散热 | `05-热控与散热.md` | 辐射排散、热阻网络、热管/LHP、1 kW 算力舱热设计实例 |
| 辐射可靠性 | `06-辐射环境与抗辐射可靠性.md` | TID/SEE/DDD、Weibull-LET 错误率链、FMEA/降额 |
| 通信与组网 | `07-通信与星间组网.md` | 链路预算、激光 APT/提前瞄准、DTN/CGR、带宽反推 |
| 结构与发射 | `08-结构机构与发射环境.md` | 四类力学载荷、一阶频率约束、展开机构、试验矩阵 |
| 地面与运营 | `09-地面系统与星座运营.md` | 站网、自动化分级、四维调度、PHM、碰撞规避 |
| 流程与法规 | `10-工程流程标准与法规.md` | 研制裁剪、AIT、ITU 频率、碎片合规、ITAR/EAR |
| 产业与商业 | `11-产业格局与商业模式.md` | 玩家详卡、三种模式经济账、太空 vs 地面 TCO |
| 全流程案例 | `12-全流程项目案例.md` | 星链 V0.9→V2 拆解、算星一号端到端全闸门 |

## 二、仿真项目（projects/）

原则：**零依赖纯 Python 标准库；测试即验证——每个 assert 锁定文档一个数值，改书必改测试**。

| 项目 | 功能 | 测试 | 运行 |
|---|---|---|---|
| p1_orbit | 轨道公式（活力/霍曼/J2/阻力/火箭方程） | 14 | `py -m unittest test_orbit -v` |
| p2_thermal | 热（平衡温度/辐射器/热阻/PCM） | 17 | `py -m unittest test_thermal -v` |
| p3_link | 链路（Friis/DVB-S2/激光/分集） | 12 | `py -m unittest test_link -v` |
| p4_radiation | 辐射（Weibull/SEU 率/TID/checkpoint） | 15 | `py -m unittest test_radiation -v` |
| p5_scheduler | 运营调度（SAA/窗口/四维约束） | 10 | `py -m unittest test_scheduler -v` |
| p6_mission | 端到端任务仿真（六闸门 go/no-go） | 9 | `py mission_sim.py` |
| p7_solarsim | 太阳系工程仿真器（tkinter 3D，实时 UTC） | 38 | `py main.py` 或 `启动仿真器.bat` |
| transfer-sim | 地月转移 C++/CUDA（GMAT 交叉验证 ≤15 m） | 47 | 需 VS2022+CUDA 12.9：`build_cpu.bat`/`build_gpu.bat` |
| p8_orbitlab | 卫星轨道动力学教学仿真器（六根数滑块联动 3D 角度弧、五大摄动、星下点轨迹） | 17 | `py main.py` |

方案改动后跑 `p6_mission` 确认 `mission_go=true`；`mission_sim.CONFIG` 即算星一号参数表，改参数即做 trade study。

## 三、GMAT 工业参照

- **怎么用**：`gmat-help-zh/`（R2026a 帮助文档 249 页中译；入口 `README.md` 导读、`index.md` 总索引、`00-术语表.md`）。高频：SpacecraftOrbitState / ForceModel / Propagator / CoordinateSystem / CalculationParameters / Tutorials
- **怎么实现**：`gmat-architecture-docs/`（16 章架构，入口 CH00-README.md）+ `math-deep-dive/`（14 章公式，LaTeX+源码行号，入口 MD-00-index.md）
- 公式迁移范例：`projects/transfer-sim/`

## 四、工作约定

1. 测试锁定文档数值：改文档必须同步改测试，反之亦然（已借此修正 5 处勘误）
2. 编辑中文 Markdown 用 PowerShell here-string + `Set-Content -Encoding UTF8`（本机 Write 工具会产出 UTF-16）
3. 新增内容先归入对应模块/项目，并在本 SKILL.md 的导航表中登记
