# 报告命令（Report）
> 译自 GMAT R2026a 帮助文档 Report.html

Report —— 允许你将数据写入文本文件。

## 脚本语法

```
Report ReportName DataList
```

- `ReportName`：该选项允许你指定用于数据输出的 ReportFile（报告文件）。
- `DataList`：该选项允许你将数据输出到由 `ReportName` 指定的文件中。多个对象可以用空格分隔写在 `DataList` 中。

## 描述

`Report` 命令允许你在任务序列的特定点报告数据。GMAT 允许你将 `Report` 命令插入到任务（Mission）树的任何位置。`Report` 命令既可以通过 GMAT 的 GUI 使用，也可以通过脚本接口使用。由 `Report` 命令报告的参数会被放入一个报告文件中，该文件可在任务运行结束后访问。

**另请参见**：ReportFile

## 选项

| 选项 | 描述 |
|------|------|
| `ReportName` | `ReportName` 选项允许用户指定用于数据输出的 `ReportFile`。<br>接受的数据类型：资源引用<br>允许的值：`ReportFile` 资源<br>默认值：`DefaultReportFile`<br>是否必需：是<br>接口：GUI、脚本 |
| `DataList` | `DataList` 选项允许用户将数据输出到由 `ReportName` 指定的文件名。多个对象可以用空格分隔放在 `DataList` 中。<br>接受的数据类型：引用数组<br>允许的值：`Spacecraft`、`ImpulsiveBurn` 的可报告参数、`Array`、数组元素、`Variable` 或 `String`<br>默认值：`DefaultSC.A1ModJulian`<br>是否必需：是<br>接口：GUI、脚本 |

## GUI

下图展示了 `Report` 命令的默认设置：

> [图：Report 命令的 GUI 面板默认设置]

## 备注

`Report` 命令可用于在任务中的特定点向报告文件报告数据。如果你希望在整个任务期间的每个传播步长上都报告数据，则不应使用 `Report` 命令，而应使用 `ReportFile` 资源。关于在每个原始积分步长上报告数据的语法，请参见《用户指南》的 `ReportFile` 资源一节。

## 示例

传播轨道两天，并使用 `Report` 命令将历元和选定的轨道根数报告到报告文件：

```
Create Spacecraft aSat
Create ReportFile aReport

Create Propagator aProp

BeginMissionSequence

Report aReport aSat.UTCGregorian aSat.Earth.SMA aSat.Earth.ECC ...
aSat.EarthMJ2000Eq.RAAN
Propagate aProp(aSat) {aSat.ElapsedDays = 2}
Report aReport aSat.UTCGregorian aSat.Earth.SMA aSat.Earth.ECC ...
aSat.EarthMJ2000Eq.RAAN
```

说明：在传播前后各执行一次 `Report`，分别把初始时刻和传播 2 天后的 UTC 公历时间、半长轴、偏心率和升交点赤经写入报告文件 aReport。

使用 `Report` 命令将用户自定义参数（如变量、数组元素和字符串）报告到报告文件：

```
Create ReportFile aReport

Create Variable aVar aVar2
aVar = 100
aVar2 = 2000

Create Array aArray[2,2]
aArray(1, 1) = 2
aArray(1, 2) = 3
aArray(2, 1) = 4
aArray(2, 2) = 5

Create String aString
aString = 'GMAT is awesome'

BeginMissionSequence

Report aReport aVar aVar2 aArray(1,1) aArray(1,2) aArray(2,1) ...
aArray(2,2) aString
```

说明：创建两个变量、一个 2×2 数组和一个字符串并赋初值；任务序列中一条 `Report` 命令把两个变量、数组的四个元素和字符串一次性写入报告文件（用续行符 `...` 分两行书写）。

当航天器传播不足一天时，每隔 3600 秒使用 `Report` 命令报告航天器的真近点角、偏心率和高度：

```
Create Spacecraft aSat
Create ReportFile aReport
Create Propagator aProp 

BeginMissionSequence

While aSat.ElapsedDays < 1
 Propagate aProp(aSat) {aSat.ElapsedSecs = 3600 }
 Report aReport aSat.Earth.TA aSat.Earth.ECC aSat.Earth.Altitude
EndWhile
```

说明：`While` 循环在已流逝时间不足 1 天时重复执行：每次先把航天器传播 3600 秒，然后把真近点角（TA）、偏心率（ECC）和高度（Altitude）写入报告文件，直到累计传播满 1 天。
