# 标记点命令（MarkPoint）
> 译自 GMAT R2026a 帮助文档 MarkPoint.html

允许你在 XYPlot（XY 曲线图）上添加特殊的标记点符号。

## 脚本语法

```
MarkPoint OutputNames
```

`OutputNames` 为订阅器（输出）列表，每个订阅器的 XYPlot 上都会添加一个特殊标记点。需要给多个订阅器添加标记点时，订阅器之间用空格分隔。

## 说明

`MarkPoint` 命令允许你在 XYPlot 上添加特殊标记点符号，以突出显示单个数据点。`MarkPoint` 命令仅对 XYPlot 订阅器有效。该命令也允许你在多个 XYPlot 资源上添加标记点。`MarkPoint` 命令可通过 GMAT 的 GUI（图形界面）或脚本接口使用。

## 选项

| 选项 | 说明 |
|---|---|
| `OutputNames` | `MarkPoint` 命令允许用户添加特殊标记点符号，以突出显示 XYPlot 上的单个数据点。<br>· 接受的数据类型：资源引用<br>· 允许的值：XYPlot 资源<br>· 默认值：DefaultXYPlot<br>· 是否必需：是<br>· 接口：GUI、脚本 |

## GUI

> [图：MarkPoint 命令的默认设置界面]

## 备注

GMAT 允许你把 `MarkPoint` 命令插入到 Mission（任务）树的任意位置，从而可以在任务的任意时刻在 XYPlot 上添加标记点。XYPlot 订阅器会在整个任务期间的每个传播步绘制数据；如果你只想在特定点放置标记点，可以把 `MarkPoint` 命令插入任务序列中，控制标记点何时落到 XYPlot 上。参见下方"示例"了解 `MarkPoint` 命令在 Mission 树中的用法。

## 示例

本例展示如何在多个订阅器上使用 `MarkPoint` 命令：通过迭代循环，每 0.2 天在两个 XYPlot 上各添加一个标记点：

```
Create Spacecraft aSat
Create Propagator aProp

Create XYPlot aPlot1 aPlot2

aPlot1.XVariable = aSat.A1ModJulian
aPlot1.YVariables = {aSat.EarthMJ2000Eq.X}

aPlot2.XVariable = aSat.A1ModJulian
aPlot2.YVariables = {aSat.EarthMJ2000Eq.VX}

BeginMissionSequence;

While aSat.ElapsedDays < 1.0
 MarkPoint aPlot1 aPlot2
 Propagate aProp(aSat) {aSat.ElapsedDays = 0.2}
EndWhile
```

中文说明：创建航天器 aSat、传播器 aProp 和两张 XY 曲线图 aPlot1（X 位置随时间）、aPlot2（X 方向速度随时间）；While 循环每传播 0.2 天执行一次 `MarkPoint aPlot1 aPlot2`，即在两张图上同时打标记点，直到累计 1 天。

本例展示在单个订阅器上使用 `MarkPoint`：当航天器高度低于 750 km 的瞬间在 XYPlot 上放置标记点。注意标记点会在每个积分步都放置到 XYPlot 上：

```
Create Spacecraft aSat
Create Propagator aProp

Create XYPlot aPlot1

aPlot1.XVariable = aSat.A1ModJulian
aPlot1.YVariables = {aSat.Earth.Altitude}

BeginMissionSequence

While aSat.ElapsedDays < 2
 Propagate aProp(aSat)
 If aSat.Earth.Altitude < 750
 MarkPoint aPlot1
 EndIf
EndWhile
```

中文说明：XY 图绘制高度随时间曲线；自由传播过程中，一旦高度低于 750 km 即执行 `MarkPoint aPlot1` 打标记。由于判断在每个积分步执行，低于阈值期间每个积分步都会打一个标记点。
