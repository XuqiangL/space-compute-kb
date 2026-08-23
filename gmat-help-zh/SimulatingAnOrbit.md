# 第 5 章 轨道仿真（Simulating an Orbit）
> 译自 GMAT R2026a 帮助文档 SimulatingAnOrbit.html

| 项目 | 内容 |
| --- | --- |
| 适用读者（Audience） | 初学者 |
| 时长（Length） | 30 分钟 |
| 先修要求（Prerequisites） | 无 |
| 脚本文件（Script File） | `Tut_SimulatingAnOrbit.script` |

## 本章目录

- 目标与概述（本节）
- [配置航天器（Spacecraft）](ch05s02.md)：重命名航天器；设置航天器历元；设置开普勒轨道根数
- [配置传播器（Propagator）](ch05s03.md)：重命名传播器；配置力模型；配置轨道视图（Orbit View）图
- [配置 Propagate 命令](ch05s04.md)
- [运行并分析结果](ch05s05.md)

## 目标与概述（Objective and Overview）

> **注意**
>
> GMAT 最基本的能力是传播（propagate）航天器，即仿真航天器的轨道运动。航天器传播能力几乎应用于空间任务分析的每一个实际环节：从简单的轨道预报（例如：国际空间站什么时候会经过我家上空？），到确定将航天器送往月球或火星所需推力器点火序列的复杂分析，都离不开它。

本教程将教你如何使用 GMAT 传播一颗航天器。你将学习如何配置 `Spacecraft`（航天器）和 `Propagator`（传播器）资源，以及如何使用 `Propagate` 命令将航天器传播至轨道近地点（periapsis）——即航天器与地球之间距离最小的点。本教程的基本步骤如下：

1. 配置一个 `Spacecraft`，并定义其历元（Epoch）与轨道根数。
2. 配置一个 `Propagator`。
3. 修改默认的 `OrbitView`（轨道视图）图，以可视化航天器轨迹。
4. 修改 `Propagate` 命令，将航天器传播至近地点。
5. 运行任务并分析结果。
