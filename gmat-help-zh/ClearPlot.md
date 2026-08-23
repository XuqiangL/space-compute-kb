# 清除图形命令（ClearPlot）
> 译自 GMAT R2026a 帮助文档 ClearPlot.html

ClearPlot —— 允许你清除 XYPlot 中的所有数据。

## 脚本语法

```
ClearPlot OutputNames
```

`OutputNames` 是要清除数据的订阅器列表。当要清除多个订阅器的数据时，它们需要用空格分隔。

## 描述

`ClearPlot` 命令允许你在数据绘制之后清除 `XYPlot` 中的所有数据。`ClearPlot` 命令只对 `XYPlot` 资源有效，可以一次清除多个 `XYPlot` 资源的数据。`ClearPlot` 命令既可以通过 GMAT 的 GUI 使用，也可以通过脚本接口使用。

## 选项

| 选项 | 描述 |
|------|------|
| `OutputNames` | `ClearPlot` 命令允许用户清除 `XYPlot` 订阅器中的数据。使用多个订阅器时，订阅器之间需要用空格分隔。<br>接受的数据类型：资源引用<br>允许的值：`XYPlot` 资源<br>默认值：`DefaultXYPlot`<br>是否必需：是<br>接口：GUI、脚本 |

## GUI

下图展示了 `ClearPlot` 命令的默认设置。

> [图：ClearPlot 命令的 GUI 面板默认设置]

## 备注

GMAT 允许你将 `ClearPlot` 命令插入到任务（Mission）树的任何位置，这样你就可以在任务的任何时刻清除 `XYPlot` 中的数据输出。`XYPlot` 订阅器会在整个任务期间的每个传播步长上绘制数据。如果你希望在任务中的特定点向 `XYPlot` 报告数据，可以在任务序列中插入 `ClearPlot` 命令来控制订阅器何时绘制数据。请参阅下面的"示例"一节，了解 `ClearPlot` 命令在任务树中的用法。

## 示例

本例展示如何对多个订阅器使用 `ClearPlot` 命令。传播 2 天后清除各 `XYPlot` 订阅器中的数据：

```
Create Spacecraft aSat
Create Propagator aProp

Create XYPlot aPlot1 aPlot2 aPlot3

aPlot1.XVariable = aSat.ElapsedSecs
aPlot1.YVariables = {aSat.EarthMJ2000Eq.X}

aPlot2.XVariable = aSat.ElapsedSecs
aPlot2.YVariables = {aSat.EarthMJ2000Eq.Y}

aPlot3.XVariable = aSat.ElapsedSecs
aPlot3.YVariables = {aSat.EarthMJ2000Eq.VX, aSat.EarthMJ2000Eq.VY, ...
aSat.EarthMJ2000Eq.VZ}

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 2}
ClearPlot aPlot1 aPlot2 aPlot3
```

说明：创建三个 XY 图分别绘制 X 位置、Y 位置和速度三分量；传播 2 天后用一条 `ClearPlot` 命令同时清空三个图中的数据。

本例展示如何对单个订阅器使用 `ClearPlot` 命令。传播前 3 天的数据被清除，只有最后 1 天传播获得的数据被绘制：

```
Create Spacecraft aSat
Create Propagator aProp

Create XYPlot aPlot1

aPlot1.XVariable = aSat.ElapsedDays
aPlot1.YVariables = {aSat.EarthMJ2000Eq.X, aSat.EarthMJ2000Eq.Y}

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 3}
ClearPlot aPlot1
Propagate aProp(aSat) {aSat.ElapsedDays = 1}
```

说明：先传播 3 天（数据正常绘制到 aPlot1），然后 `ClearPlot aPlot1` 清空图中全部数据，再传播 1 天。最终图中只显示最后 1 天的 X、Y 位置曲线。
