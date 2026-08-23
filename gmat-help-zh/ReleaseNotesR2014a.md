# GMAT R2014a 发行说明（ReleaseNotesR2014a）

> 译自 GMAT R2026a 帮助文档 ReleaseNotesR2014a.html

GMAT R2014a 于 2014 年 5 月发布。这是自 2013 年 4 月以来的第一个公开版本，是本项目的第 8 个版本。以下为本版本关键变更摘要；完整清单见 JIRA 上的完整 R2014a 发行说明。

## 新功能

### 轨迹颜色和标签

在 GMAT R2014a 中，现在可以为轨迹的每个弧段独立指定颜色，从而清楚地看到弧段的开始和结束位置。这有助于定义轨迹的各个部分，例如机动前后。所有颜色处理也已从图形资源（`OrbitView` 和 `GroundTrackPlot`）移到控制轨迹的资源和命令（如 `Spacecraft`、`Planet`、`Propagate`）。

在 Spacecraft 上，颜色设置已移到 Visualization（可视化）选项卡（见下方截图中的圆圈区域）。天体（`Planet`、`Moon`、`Asteroid` 等）的颜色以类似方式指定。

> [图：Spacecraft 可视化选项卡中的颜色设置]

与特定轨迹弧段关联的轨迹颜色可以通过更改该特定 `Propagate` 命令的颜色来更改。它将仅在该弧段覆盖被传播航天器的颜色，之后恢复为默认颜色。

> [图：Propagate 命令的颜色设置]

此外，颜色现在可以按名称（`'Blue'`）或 RGB 值（`[0 0 255]`）指定。

本版本还在图形中添加了参与者标签。只要启用 `OrbitView`.`ShowLabels`，图中的每个天体或 `Spacecraft` 都会在其旁边显示其名称。

示例：

```
Create Spacecraft aSat
aSat.OrbitColor = 'Blue'

Create Propagator aProp

Create OrbitView aView
aView.Add = {aSat, Earth}
aView.XYPlane = off
aView.Axes = off
aView.EnableConstellations = off
aView.ShowLabels = on

BeginMissionSequence
% plots in blue
Propagate aProp(aSat) {aSat.ElapsedSecs = 900}                     
aSat.OrbitColor = 'Green'
% plots in green
Propagate aProp(aSat) {aSat.ElapsedSecs = 900}             
 % plots in red        
Propagate aProp(aSat) {aSat.ElapsedSecs = 900, OrbitColor = Red}
```

以上示例先以蓝色绘制 900 秒轨迹，然后将航天器轨道颜色改为绿色再绘制 900 秒，最后通过 Propagate 命令的 OrbitColor 选项以红色绘制 900 秒。

> [图：三段不同颜色的轨道视图示例]

更多信息见 Color 参考文档以及 Spacecraft、CelestialBody、Propagate 和 OrbitView 参考文档。

### 新轨道状态表示

GMAT 现在支持六种新的常用轨道状态表示，由韩国航空宇宙研究院（KARI）支持开发。新表示为：

- 长周期和短周期 Brouwer-Lyddane 平根数（`BrouwerMeanLong` 和 `BrouwerMeanShort`）
- 入射和出射双曲线渐近线根数（`IncomingAsymptote` 和 `OutgoingAsymptote`）
- 改进春分点根数（`ModifiedEquinoctial`）
- 另类春分点根数（`AlternateEquinoctial`）
- Delaunay 根数（`Delaunay`）
- 行面测地根数，使用体固坐标系时（`Planetodetic`）

新表示在 `Spacecraft` 的 "State Type"（状态类型）列表中作为选项提供，也可作为 `Spacecraft`.`DisplayStateType` 字段的选项。

> [图：Spacecraft 状态类型列表]

更多信息见"航天器轨道状态"（Spacecraft Orbit State）参考文档。

### 新姿态模型

GMAT 现在支持三种新的运动学姿态模型，由韩国航空宇宙研究院（KARI）支持开发：

- 进动自旋（Precessing spinner）
- 对地指向（Nadir pointing）
- CCSDS 姿态星历消息（AEM）

新表示在 `Spacecraft` 的 "Attitude"（姿态）列表中作为选项提供。

> [图：姿态类型列表]

更多信息见"航天器姿态"（Spacecraft Attitude）参考文档。

### 动力学和模型改进

GMAT 现在支持几种新的动力学模型和一种新的数值积分器：

- Prince Dormand 853 积分器。更多信息见 Propagator 参考文档。
- Mars-GRAM 密度模型。更多信息见 Propagator 参考文档。
- 高保真、姿态相关的 SRP 动力学模型。更多信息见 Propagator 参考文档和"航天器弹道与质量特性"（Spacecraft Ballistic and Mass Properties）参考文档。

### 打靶和优化改进

- `DifferentialCorrector` 上有新的边值求解器选项（`Broyden` 和 `ModifiedBroyden`）。Broyden 方法和改进 Broyden 方法通常比 `NewtonRaphson` 需要更多迭代但更少函数评估，因此通常更快。更多信息见 Differential Corrector 参考文档。
- 有检查求解器收敛的新参数。更多信息见"计算参数"（Calculation Parameters）参考文档。

下面是演示新算法和参数选项的脚本示例：

```
Create Spacecraft aSat
Create Propagator aPropagator

Create ImpulsiveBurn aBurn
Create DifferentialCorrector aDC
%  This algorithm is often faster, as is ModifiedBroyden
aDC.Algorithm = Broyden  

Create OrbitView EarthView
EarthView.Add = {Earth,aSat}
EarthView.ViewScaleFactor = 5

Create ReportFile aReport 

BeginMissionSequence

%  Report targeter status here
Report aReport aDC.SolverStatus aDC.SolverState
Target aDC
    Vary aDC(aBurn.Element1 = 1.0, {Upper = 3, MaxStep = 0.4})
    Maneuver aBurn(aSat)
    Propagate aPropagator(aSat,{aSat.Apoapsis})
    Achieve aDC(aSat.RMAG = 42164)
EndTarget
%  Report targeter status here
Report aReport aDC.SolverStatus aDC.SolverState
```

以上示例使用 Broyden 算法的微分修正器，通过调整脉冲机动的第一个元素，使航天器在远拱点的半径达到 42164 km，并在打靶前后报告求解器状态。

## 改进

### 赋值命令中的依赖

现在可以在赋值命令的左侧（LHS）使用依赖来定义可设置参数：

```
Create Spacecraft aSat

BeginMissionSequence

aSat.EarthFixed.X = 7000
aSat.EarthMJ2000Eq.VZ = 1
```

以上示例在赋值命令左侧使用坐标系依赖（EarthFixed、EarthMJ2000Eq）直接设置航天器状态分量。

### 其他改进

- 使用开普勒表示时现在可以设置真正的逆行轨道。
- 现在可以在赋值命令右侧使用四元数 Rvector 参数。
- 现在可以使用 `Spacecraft` 体固坐标系作为 `OrbitView` 的坐标系。
- `OrbitView` 中可显示的 `Spacecraft` 数量不再限于 30 个。
- `OrbitView` 的文档已显著扩充。详见 Orbit View 参考文档。
- 现在可以将 XY 曲线图图形窗口保存为图像文件。
- 支持的键盘快捷键集已大大扩展。更多信息见"键盘快捷键"（Keyboard Shortcuts）参考文档。
- 现在可以在 GMAT 字符串中使用更多常见 ASCII 字符。
- 现在可以使用所选坐标系原点为任意点类型的坐标系生成轨道状态命令摘要报告。以前原点必须是天体（Celestial Body）。

## 兼容性变更

- 图形中显示的 `Resources` 的颜色设置现在在 `Resource` 上并通过 `Propagate` 命令配置。图形资源上的 `OrbitColor` 和 `TargetColor` 字段不再使用。详见"航天器可视化"（Spacecraft Visualization）参考文档和 Propagate 命令参考文档。
- AtmosDensity 现在以 kg/km^3 为单位报告。详见"计算参数"（Calculation Parameter）参考文档。

## 已修复与已知问题

本版本关闭了 123 多个 bug。关键 bug 及解决方案清单见 "Critical Issues Fixed in R2014a" 报告；次要问题见 "Minor Issues Fixed for R2014a" 报告。

### 已知问题

影响此版本 GMAT 的所有已知问题见 JIRA 中的 "Known Issues in R2014a" 报告。本版本中几个重要的已知问题：

| ID | 描述 |
| --- | --- |
| GMT-2561 | 闰秒期间的 UTC 历元输入和报告不正确。 |
| GMT-3043 | 创建遮蔽内置数学函数的变量时验证不一致。 |
| GMT-3108 | 带 STM 和 Propagate Synchronized 的 OrbitView 不能在正确位置显示航天器。 |
| GMT-3289 | 使用 SPK 传播器向后传播时首步算法失败。 |
| GMT-3350 | 单引号要求在不同对象和模式间不一致。 |
| GMT-3556 | 无法在命令模式中将贮箱与推力器关联。 |
| GMT-3629 | 以 --minimize 启动时 GUI 进入错误状态。 |
| GMT-3669 | 优化期间 OrbitView 中不绘制行星。 |
| GMT-3738 | 无法在 CallMatlabFunction 中设置独立的 FuelTank、Thruster 字段。 |
| GMT-4520 | Optimize 中无关的脚本行会改变结果（导致崩溃）。 |
| GMT-4408 | 无法加载图标文件和打开 DE 文件。 |
| GMT-4398 | 坐标系固定姿态在 SPAD SRP 模型的传播步内被保持为常数。 |