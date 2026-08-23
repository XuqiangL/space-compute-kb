# GMAT R2016a 发行说明（ReleaseNotesR2016a）

> 译自 GMAT R2026a 帮助文档 ReleaseNotesR2016a.html

GMAT R2016a 于 2016 年 10 月发布。这是自 2015 年 11 月以来的第一个公开版本，是本项目的第 10 个版本。注意，这将是 Windows 上最后一个 32 位版本的 GMAT（Mac 和 Linux 仅 64 位）。以下为本版本关键变更摘要；完整清单见 JIRA 上的完整 R2016a 发行说明。

## 新功能

### 轨道确定

GMAT 现在支持轨道确定，重点关注 DSN 数据类型（包括距离和多普勒）的批估计。我们在导航功能上已工作多个版本，但这是第一个包含导航功能的生产版本。轨道确定功能经过了严格的质量保证流程，包括在 GSFC 飞行动力学设施的影子测试，并在教程和参考材料中有详尽文档。导航组件包括 BatchEstimator、Simulator、ErrorModel、StatisticsAcceptFilter、StatisticsRejectFilter、TrackingDataSet 以及 RunEstimator 和 RunSimulator 命令。我们建议先学习教程，然后查阅轨道确定组件的参考材料。

更多信息见"仿真 DSN 距离和多普勒数据"（Simulation）和"使用 DSN 距离和多普勒数据进行轨道估计"（Estimation）教程。

### Code 500 星历传播器

GMAT 现在支持使用 GSFC Code 500 星历文件格式的传播器。Code 500 文件格式是 GSFC 一些系统仍在使用的旧格式。该功能允许 GSFC 旧系统的用户仿真和分析在 GTDS 等系统中计算的轨迹。更多信息见 Propagator 参考文档。

### Write 命令

现在可以在任务序列执行期间将 GMAT 资源导出到文件。这是一个强大的功能，允许你在会话的任何点保存配置，供以后的会话或其他用户使用。更多信息见 Write 命令参考文档。

### #Include 宏

现在可以在脚本初始化和任务执行期间从外部文件加载 GMAT 资源和脚本片段。这是一个强大的功能，允许你在多个用户和/或脚本之间重用配置。该功能还可以大大简化业务运行以及 Monte-Carlo 和参数扫描的自动化——这些用例有大量公共数据，但每次执行之间有一些数据会变化。更多信息见 #Include 参考文档。

### GetEphemStates 内置函数

使用内置的 GetEphemStates 函数，现在可以查询 SPICE、Code-500 和 STK .e 星历类型，以任何 GMAT 支持的历元格式和坐标系获取航天器的初始历元、初始状态、最终历元和最终状态。这允许你使用星历文件上的状态进行数值传播，以进行比较和其他分析。更多信息见 GetEphemStates 参考文档。

## 改进

- 现在可以在脚本中定义 EOP 文件位置。
- 系统现在支持报告有限燃烧的推力分量数据的有限燃烧参数。这些参数包括三个坐标方向上所有推力器的总推力、三个坐标方向上所有推力器的总加速度以及总质量流率。此外，现在还可以报告单个推力器参数，如推力大小、Isp 和质量流率。
- GMAT 现在包含内置字符串操作函数 sprintf、strcmp、strcat、strfind、strrep。
- 实现了几个新的内置数学函数，包括内置叉积函数。数值数据操作方面实现了 mod、ceil、floor、fix；随机数生成方面实现了 rand、randn 和 SetSeed。
- 现在可以建模使用多个贮箱的有限燃烧。以前版本仅限于单个贮箱。
- GMAT 现在除了支持以前支持的 CCSDS-OEM、SPK 和 Code-500 格式外，还支持生成 STK 的 ".e" 星历格式。
- 我们编写了 130 多页新的高质量用户文档！
- 使用大字体时 GUI 的行为得到改进。

## 兼容性变更

- 现在可以覆盖 `CelestialBody` 上的默认 `NAIFId`，以允许使用天体中心或质心作为内置天体的参考。以前此字段是只读的。

## 开发与工具

### 开发者工具和依赖

我们更新了所有平台上使用的基于 CMake 的构建系统。CMake 配置由 GMAT 团队维护并随源代码分发。得益于 CMake，编译 GMAT 变得容易得多。详见 wiki 文档。注意，旧的构建文件不再受支持，被视为已过时。

## 已修复与已知问题

本版本关闭了 100 多个 bug。关键 bug 及解决方案清单见 "Critical Issues Fixed in R2016a" 报告；次要问题见 "Minor Issues Fixed for R2016a" 报告。

### 已知问题

影响此版本 GMAT 的所有已知问题见 JIRA 中的 "Known Issues in R2016a" 报告。本版本中几个重要的已知问题：

| ID | 描述 |
| --- | --- |
| GMT-5269 | 大气模型影响 GEO 处的传播。 |
| GMT-2561 | 闰秒期间的 UTC 历元输入和报告不正确。 |
| GMT-3043 | 创建遮蔽内置数学函数的变量时验证不一致。 |
| GMT-3289 | 使用 SPK 传播器向后传播时首步算法失败。 |
| GMT-3350 | 单引号要求在不同对象和模式间不一致。 |
| GMT-3669 | 优化期间 OrbitView 中不绘制行星。 |
| GMT-3738 | 无法在 CallMatlabFunction 中设置独立的 FuelTank、Thruster 字段。 |
| GMT-4520 | Optimize 中无关的脚本行会改变结果（导致崩溃）。 |
| GMT-4398 | 坐标系固定姿态在 SPAD SRP 模型的传播步内被保持为常数。 |