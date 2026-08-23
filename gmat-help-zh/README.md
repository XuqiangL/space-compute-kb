# GMAT R2026a 帮助文档 · 中文全译本（导读）

> 本目录是 NASA 开源任务设计软件 **GMAT（General Mission Analysis Tool，通用任务分析工具）R2026a** 官方帮助文档（`docs/help/html`，249 个 HTML 页面）的完整中文翻译，共 249 篇 Markdown + 1 篇术语表。
> 原文版权：NASA / GMAT 项目（Apache License 2.0）。本译文仅供学习参考，以英文原文为准。

## 这套文档是什么

GMAT 是 NASA 戈达德航天中心主导开发的开源任务设计与轨道分析软件，已支持 8+ 个 NASA 真实任务（含 LRO、OSIRIS-REx、Lucy 等）。这套帮助文档是它的**权威参考手册**，覆盖：

- 轨道力学建模（力模型、传播器、坐标系、姿态）
- 任务设计（脉冲/有限推力机动、目标求解、轨迹优化）
- 轨道确定（批处理估计、扩展卡尔曼滤波、平滑器、DSN 测量仿真）
- 脚本语言与 GUI 完整参考

与本知识库 `gmat-architecture-docs/`（GMAT **源码架构**解析）互补：那边讲"代码怎么写"，这边讲"软件怎么用、模型怎么算"。

## 阅读路线建议

**零基础入门（按顺序读）：**
1. `WelcomeToGmat.md` → `GettingStarted.md` → `TourOfGmat.md`（GMAT 是什么、怎么装、界面长什么样）
2. `Tutorials.md` → `SimulatingAnOrbit.md`（第 5 章：第一个轨道仿真）
3. `SimpleOrbitTransfer.md`（第 6 章：霍曼转移 + Target 目标求解）
4. `Tut_TargetFiniteBurn.md`（第 7 章：有限推力机动）
5. `Mars_B_Plane_Targeting.md`（第 8 章：火星 B 平面瞄准，深空任务设计核心技能）

**进阶（任务分析工程师）：**
- `OptimalLunarFlyby.md`（多重打靶优化月球飞掠）
- `Tut_EventLocation.md`（食/可见性事件定位）
- `Tut_ElectricPropulsion.md`（电推进建模）
- `Tut_Simulate_DSN_Range_and_Doppler_Data.md` + `Orbit_Estimation_using_DSN_Range_and_Doppler_Data.md`（DSN 测量仿真与定轨全流程）
- `FilterSmoother_GpsPosVec.md`（EKF/平滑器定轨）

**参考手册（用时查阅）：**
- 轨道状态表示法：`SpacecraftOrbitState.md`（12 种状态类型、63 个字段）
- 姿态模型：`SpacecraftAttitude.md`（8 种姿态模型）
- 力模型：`ForceModel.md`（重力场/大气阻力/光压/潮汐/相对论修正）
- 传播器：`Propagator.md`（数值积分器 + 5 类星历传播器）
- 坐标系：`CoordinateSystem.md`（22 种轴系类型）
- 全部可计算参数：`CalculationParameters.md`（259 个参数条目）
- 脚本语言：`ScriptLanguage.md` + 全部命令参考
- 完整目录：`index.md`（总索引）、`BookIndex.md`（字母索引）

## 翻译约定

- 参数名/字段名/命令名保留英文，首次出现加中文释义，如 `OrbitColor`（轨道颜色）
- GMAT 脚本示例保留英文原文，段后附中文说明
- 图片以 `> [图：描述]` 占位（原图为软件截图，见 GMAT 安装目录）
- 术语统一遵循 `00-术语表.md`
- 译文中标注了原文档的若干笔误（以"译注"标明）
