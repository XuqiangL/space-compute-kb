# 第 12 章 电推进（Electric Propulsion）
> 译自 GMAT R2026a 帮助文档 Tut_ElectricPropulsion.html

| 项目 | 内容 |
| --- | --- |
| 适用读者（Audience） | 初学者 |
| 时长（Length） | 15 分钟 |
| 先修要求（Prerequisites） | 完成[轨道仿真](SimulatingAnOrbit.md) |
| 脚本文件（Script File） | `Tut_ElectricPropulsionModelling.script` |

## 本章目录

- 目标与概述（本节）
- [创建并配置航天器硬件与有限推力机动](ch12s02.md)：创建推力器、贮箱与太阳能电源系统；配置硬件；将硬件挂接到航天器；创建有限推力机动
- [配置任务序列](ch12s03.md)：创建命令；配置 Propagate 命令
- [运行任务](ch12s04.md)

## 目标与概述（Objective and Overview）

在本教程中，我们将使用 GMAT 为一颗使用电推进（Electric Propulsion）系统的航天器执行一次有限推力机动（finite burn）。请注意，使用电推进进行目标求解与设计的方法和化学推进完全相同；关于目标求解配置，请参阅教程[目标求解有限推力机动以抬升远地点](Tut_TargetFiniteBurn.md)。本教程仅聚焦于电推进系统的配置与建模。

本教程的基本步骤如下：

1. 创建并配置 `Spacecraft`（航天器）硬件和 `FiniteBurn`（有限推力机动）资源。
2. 配置任务序列（Mission Sequence）。为此，我们将：
   1. 使用默认设置创建 `Begin/End FiniteBurn`（开始/结束有限推力机动）命令。
   2. 创建一个 `Propagate` 命令，在传播的同时施加来自电推进系统的推力。
3. 运行任务。
