# 第 7 章 目标求解有限推力机动以抬升远地点（Target Finite Burn to Raise Apogee）
> 译自 GMAT R2026a 帮助文档 Tut_TargetFiniteBurn.html

| 项目 | 内容 |
| --- | --- |
| 适用读者（Audience） | 中级 |
| 时长（Length） | 45 分钟 |
| 先修要求（Prerequisites） | 完成“轨道仿真”与“简单轨道转移” |
| 脚本文件（Script File） | `Tut_Target_Finite_Burn_to_Raise_Apogee.script` |

## 本章目录

- 目标与概述（本节）
- [创建并配置航天器硬件与有限推力机动](ch07s02.md)：创建推力器与贮箱；修改 Thruster1 推力系数；将 ChemicalTank1 与 Thruster1 挂接到 DefaultSC；创建有限推力机动
- [创建微分修正器与 Target 控制变量](ch07s03.md)
- [配置任务序列](ch07s04.md)：配置初始 Propagate 命令；创建 Target 序列；配置 Target 序列
- [运行任务](ch07s05.md)：查看轨道视图与消息窗口；查看命令摘要报告

## 目标与概述（Objective and Overview）

> **注意**
>
> 空间任务设计中最常见的操作问题之一，是设计一个能达成给定轨道目标的有限推力机动（finite burn）。与初步设计中使用的理想化脉冲机动（impulsive burn）模型不同，要精确建模航天器的真实机动，必须使用有限推力机动模型。

在本教程中，我们将使用 GMAT 为一颗低地球轨道航天器执行一次有限推力机动。这次有限推力机动的目标是达到某个期望的远地点半径。由于影响远地点最高效的轨道位置在近地点处，因此本教程的第一步是将航天器传播至近地点（perigee）。

为了计算达到 12000 km 期望远地点半径所需的近地点点火时长，我们必须创建相应的目标求解序列。该目标求解序列的主体部分采用一对 `Begin/End FiniteBurn`（开始/结束有限推力机动）命令，执行一次沿速度方向的机动，随后用一条命令将航天器传播至轨道远地点（apogee）。

本教程的基本步骤如下：

1. 创建并配置 `Spacecraft`（航天器）硬件和 `FiniteBurn`（有限推力机动）资源。
2. 创建 `DifferentialCorrector`（微分修正器）和 Target 控制 `Variable`（变量）。
3. 配置任务序列（Mission Sequence）。为此，我们将：
   1. 使用默认设置创建 `Begin/End FiniteBurn` 命令。
   2. 创建一个 `Target` 序列，以达到 12000 km 的远地点半径。
4. 运行任务并分析结果。
