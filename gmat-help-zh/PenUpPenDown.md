# 抬笔/落笔命令（PenUpPenDown）
> 译自 GMAT R2026a 帮助文档 PenUpPenDown.html

PenUpPenDown —— 允许你停止或开始在图形上绘制数据。

## 脚本语法

```
PenUp OutputNames
```

`OutputNames` 是 `PenUp` 命令作用的订阅器列表。当 `PenUp` 命令作用于多个订阅器时，订阅器之间需要用空格分隔。

```
PenDown OutputNames
```

`OutputNames` 是 `PenDown` 命令作用的订阅器列表。当 `PenDown` 命令作用于多个订阅器时，订阅器之间需要用空格分隔。

## 描述

`PenUp` 和 `PenDown` 命令允许你停止或开始在图形上绘制数据。`PenUp` 和 `PenDown` 命令作用于 `XYPlot`、`OrbitView` 和 `GroundTrack` 订阅器。GMAT 允许你将 `PenUp` 和 `PenDown` 命令插入到任务（Mission）树的任何位置，这样你就可以在任务的任何时刻停止或开始在图形上绘制数据输出。`PenUp` 和 `PenDown` 命令既可以通过 GMAT 的 GUI 使用，也可以通过脚本接口使用。

## 选项

| 选项 | 描述 |
|------|------|
| `OutputNames`（PenUp） | 当对某个图形发出 `PenUp` 命令后，直到对该图形发出 `PenDown` 命令之前，不会有数据绘制到该图形上。<br>接受的数据类型：资源引用<br>允许的值：`XYPlot`、`OrbitView` 或 `GroundTrack` 资源<br>默认值：`DefaultOrbitview`<br>是否必需：是<br>接口：GUI、脚本 |
| `OutputNames`（PenDown） | 当对某个图形发出 `PenDown` 命令后，数据会在每个积分步长上绘制，直到对该图形发出 `PenUp` 命令为止。<br>接受的数据类型：资源引用<br>允许的值：`XYPlot`、`OrbitView` 或 `GroundTrack` 资源<br>默认值：`DefaultOrbitview`<br>是否必需：是<br>接口：GUI、脚本 |

## GUI

下图展示了 `PenUp` 和 `PenDown` 命令的默认设置：

> [图：PenUp 命令的 GUI 面板默认设置]

> [图：PenDown 命令的 GUI 面板默认设置]

## 备注

`XYPlot`、`OrbitView` 和 `GroundTrack` 订阅器会在整个任务期间的每个积分步长上绘制数据。如果你希望在任务中的特定点绘制数据，可以在任务序列中插入 `PenUp` 和 `PenDown` 命令来控制订阅器何时绘制数据。例如，当对 `XYPlot`、`OrbitView` 或 `GroundTrack` 发出 `PenUp` 命令后，直到对同一图形发出 `PenDown` 命令之前，不会有数据绘制到该图形上。类似地，当对这三个订阅器中的任何一个发出 `PenDown` 命令后，数据会在每个积分步长上绘制，直到对该特定订阅器发出 `PenUp` 命令为止。请参阅下面的"示例"一节，了解如何在任务树中使用 `PenUp` 和 `PenDown` 命令。

## 示例

本例展示如何对多个订阅器使用 `PenUp` 和 `PenDown` 命令。对 `XYPlot`、`OrbitView` 和 `GroundTrack` 使用 `PenUp` 和 `PenDown` 命令。传播的第 1 天绘制数据，第 2 天关闭绘制，第 3 天再次绘制数据：

```
Create Spacecraft aSat
Create Propagator aProp

Create XYPlot aPlot
aPlot.XVariable = aSat.ElapsedDays
aPlot.YVariables = {aSat.Earth.SMA}

Create OrbitView anOrbitViewPlot
anOrbitViewPlot.Add = {aSat, Earth}

Create GroundTrack aGroundTrack
aGroundTrack.Add = {aSat, Earth}

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1}
PenUp aGroundTrack anOrbitViewPlot aPlot
Propagate aProp(aSat) {aSat.ElapsedDays = 1}
PenDown aGroundTrack anOrbitViewPlot aPlot
Propagate aProp(aSat) {aSat.ElapsedDays = 1}
```

说明：第 1 天的传播正常绘图；随后 `PenUp` 同时作用于三个订阅器（名称以空格分隔），第 2 天传播期间不绘制任何曲线（轨迹不连线）；`PenDown` 恢复绘制后，第 3 天的传播再次正常显示。

本例展示如何对单个 `XYPlot` 订阅器使用 `PenUp` 和 `PenDown` 命令。一天的三分之一时间绘制数据，中间三分之一关闭绘制，最后三分之一再次绘制数据：

```
Create Spacecraft aSat
Create Propagator aProp

Create XYPlot aPlot1
aPlot1.XVariable = aSat.ElapsedDays
aPlot1.YVariables = {aSat.Earth.Altitude}

Create Variable I
I = 0

BeginMissionSequence

While aSat.ElapsedDays < 1.0
   
 Propagate aProp(aSat) {aSat.ElapsedSecs = 60}
 If I == 480
 PenUp aPlot1
 EndIf
   
 If I == 960
 PenDown aPlot1
 EndIf
   
 GMAT I = I +1

EndWhile
```

说明：`While` 循环以 60 秒为步长传播一整天，计数器 I 每步加 1。当 I 达到 480（即 480×60 秒 = 8 小时，一天的三分之一）时执行 `PenUp aPlot1` 停止绘图；当 I 达到 960（16 小时，三分之二处）时执行 `PenDown aPlot1` 恢复绘图。最终高度曲线只在前 8 小时和最后 8 小时有数据。
