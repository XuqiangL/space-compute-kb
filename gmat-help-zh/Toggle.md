# 开关命令（Toggle）
> 译自 GMAT R2026a 帮助文档 Toggle.html

Toggle —— 允许你关闭或打开数据输出。

## 脚本语法

```
Toggle OutputNames Arg
```

- `OutputNames`：要切换的订阅器（Subscriber）列表。当在 `OutputNames` 中切换多个订阅器时，它们需要用空格分隔。
- `Arg`：该选项允许你关闭或打开向 `OutputNames` 中所列订阅器的数据输出。

## 描述

`Toggle` 命令允许你关闭或打开向所选订阅器（如 `ReportFile`、`XYPlot`、`OrbitView`、`GroundTrack` 和 `EphemerisFile`）的数据输出。GMAT 允许你将 `Toggle` 命令插入到任务（Mission）树的任何位置，数据输出可以在任务的任何时刻被关闭或打开。`Toggle` 命令既可以通过 GMAT 的 GUI 使用，也可以通过脚本接口使用。

## 选项

| 选项 | 描述 |
|------|------|
| `OutputNames` | `Toggle` 选项允许用户指定要切换的订阅器，如 `ReportFile`、`XYPlot`、`OrbitView`、`GroundTrack` 或 `EphemerisFile`。切换多个订阅器时，它们需要用空格分隔。<br>接受的数据类型：资源引用<br>允许的值：`ReportFile`、`XYPlot`、`OrbitView`、`GroundTrack` 或 `EphemerisFile` 资源<br>默认值：`DefaultOrbitView`<br>是否必需：是<br>接口：GUI、脚本 |
| `Arg` | `Arg` 选项允许用户关闭或打开向所选订阅器的数据输出。<br>接受的数据类型：布尔值<br>允许的值：On、Off<br>默认值：On<br>是否必需：是<br>接口：GUI、脚本 |

## GUI

下图展示了 `Toggle` 命令的默认设置：

> [图：Toggle 命令的 GUI 面板默认设置]

## 备注

`ReportFile`、`XYPlot`、`OrbitView`、`GroundTrack` 和 `EphemerisFile` 等订阅器会在整个任务期间的每个传播步长上报告或绘制数据。如果你希望在任务中的特定点向这些订阅器报告数据，可以在任务序列中插入 `Toggle On`/`Off` 命令来控制订阅器何时报告或绘制数据。例如，当对一个 `XYPlot` 发出 `Toggle Off` 命令后，直到发出 `Toggle On` 命令之前，不会有数据绘制到图形的 X 和 Y 轴上。类似地，使用 `Toggle On` 命令后，数据会在每个积分步长上绘制到 X 和 Y 轴，直到使用 `Toggle Off` 命令为止。

当把 `Toggle` 命令与星历文件中的有限推力弧段建模结合使用时，必须遵守特定的操作顺序。星历的 Toggle 命令必须放在 BeginFileThrust 和 EndFileThrust 命令之内，如下例所示。无论在传播时，还是在运行 `BatchEstimator`、`ExtendedKalmanFilter` 或 `Smoother` 等估计器时，都必须遵守此操作顺序。

```
BeginFileThrust ThrustHistory(Sat);
Toggle Ephem On;
Propagate Prop(Sat) {Sat.ElapsedDays = 1};
Toggle Ephem Off;
EndFileThrust ThrustHistory(Sat);
```

说明：在记录推力历史（ThrustHistory）的弧段内，先 `Toggle Ephem On` 打开星历输出，传播 1 天后再 `Toggle Ephem Off` 关闭，最后结束推力弧段记录。

## 示例

本例展示如何在使用 `XYPlot` 资源时使用 `Toggle Off` 和 `Toggle On` 命令。将航天器位置模长和半长轴绘制为时间的函数。传播的前 2 天关闭 `XYPlot`：

```
Create Spacecraft aSat
Create Propagator aProp

Create XYPlot aPlot
aPlot.XVariable = aSat.ElapsedDays
aPlot.YVariables = {aSat.Earth.RMAG, aSat.Earth.SMA}

BeginMissionSequence

Toggle aPlot Off
Propagate aProp(aSat) {aSat.ElapsedDays = 2}
Toggle aPlot On
Propagate aProp(aSat) {aSat.ElapsedDays = 4}
```

说明：先关闭 aPlot，传播 2 天（此期间不绘图）；再打开 aPlot，继续传播 4 天（此期间每个积分步都绘图）。最终图上只有后 4 天的数据。

本例展示如何在使用 `ReportFile` 资源时使用 `Toggle Off` 和 `Toggle On` 命令。将航天器笛卡尔位置矢量报告到报告文件。传播的第 1 天关闭报告文件：

```
Create Spacecraft aSat
Create Propagator aProp

Create ReportFile aReport
aReport.Filename = 'ReportFile1.txt'
aReport.Add = {aSat.ElapsedDays aSat.EarthMJ2000Eq.X ...
aSat.EarthMJ2000Eq.Y aSat.EarthMJ2000Eq.Z}

BeginMissionSequence

Toggle aReport Off
Propagate aProp(aSat) {aSat.ElapsedDays = 1}
Toggle aReport On
Propagate aProp(aSat) {aSat.ElapsedDays = 4}
```

说明：先关闭 aReport，传播 1 天（不记录）；再打开 aReport，继续传播 4 天。报告文件中只包含后 4 天的数据。

本例展示如何切换多个订阅器。对 `ReportFile`、`XYPlot` 和 `EphemerisFile` 等多个订阅器使用 `Toggle Off` 和 `Toggle On` 命令。传播的前 3 天关闭这些订阅器：

```
Create Spacecraft aSat
Create Propagator aProp

Create ReportFile aReport
aReport.Filename = 'ReportFile1.txt'
aReport.Add = {aSat.ElapsedDays aSat.EarthMJ2000Eq.X ...
aSat.EarthMJ2000Eq.Y aSat.EarthMJ2000Eq.Z}

Create XYPlot aPlot
aPlot.XVariable = aSat.ElapsedDays
aPlot.YVariables = {aSat.Earth.RMAG, aSat.Earth.SMA}

Create EphemerisFile aEphemerisFile
aEphemerisFile.Spacecraft = aSat

BeginMissionSequence

Toggle aReport aPlot aEphemerisFile Off
Propagate aProp(aSat) {aSat.ElapsedDays = 3}
Toggle aReport aPlot aEphemerisFile On
Propagate aProp(aSat) {aSat.ElapsedDays = 1}
```

说明：一条 `Toggle` 命令同时关闭报告文件、XY 图和星历文件三个订阅器（名称以空格分隔），传播 3 天后再用一条命令同时打开，继续传播 1 天。
