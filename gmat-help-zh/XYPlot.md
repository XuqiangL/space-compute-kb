# XY 曲线图（XYPlot）

> 译自 GMAT R2026a 帮助文档 XYPlot.html

**XYPlot** —— 将数据绘制到图的 X 轴和 Y 轴上。

## 描述

`XYPlot` 资源允许你把数据绘制到图的 X 轴和 Y 轴上。你可以选择把任意数量的参数绘制为单一自变量的函数。GMAT 允许绘制用户自定义变量、数组元素或航天器参数。你可以通过 GMAT 的 GUI 或脚本接口创建多个 `XYPlot`。GMAT 还提供 `Toggle On`/`Off` 命令，用于控制何时开始向 XYPlot 绘制或停止绘制数据。`XYPlot` 资源与 `Toggle` 命令的交互详见下文"备注"一节。GMAT 的 `Spacecraft` 和 `XYPlot` 资源在整个任务持续期间也会相互交互，相关讨论同样见"备注"一节。

**另请参阅**：`Toggle`、`Spacecraft`

## 字段

| 字段 | 描述 |
| --- | --- |
| `Maximized` | 允许用户最大化 `XYPlot` 窗口。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：true、false；**访问**：set；**默认值**：false；**单位**：N/A；**接口**：脚本 |
| `UpperLeft` | 允许用户沿任意方向平移 `XYPlot` 显示窗口。[0 0] 矩阵中第一个值水平平移窗口，第二个值垂直平移窗口。该字段不能在任务序列中修改。**数据类型**：实数数组；**允许值**：任意实数；**访问**：set；**默认值**：[0 0]；**单位**：N/A；**接口**：脚本 |
| `RelativeZOrder` | 允许用户选择哪个 `XYPlot` 窗口最先显示在屏幕上。`RelativeZOrder` 值最低的 `XYPlot` 最后显示，值最高的最先显示。该字段不能在任务序列中修改。**数据类型**：整数；**允许值**：整数 ≥ 0；**访问**：set；**默认值**：0；**单位**：N/A；**接口**：脚本 |
| `ShowGrid` | 设为 `True` 时在 XY 曲线图上绘制网格；设为 `False` 时不绘制网格。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：True、False；**访问**：set；**默认值**：True；**单位**：N/A；**接口**：GUI、脚本 |
| `ShowPlot` | 允许用户针对某次运行关闭绘图，而无需删除 XYPlot 资源或将其从脚本中移除。选 `True` 则显示图；选 `False` 则不显示。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：True、False；**访问**：set；**默认值**：True；**单位**：N/A；**接口**：GUI、脚本 |
| `Size` | 允许用户控制 `XYPlot` 窗口的显示尺寸。[0 0] 矩阵中第一个值控制水平尺寸，第二个值控制垂直尺寸。该字段不能在任务序列中修改。**数据类型**：实数数组；**允许值**：任意实数；**访问**：set；**默认值**：[ 0 0 ]；**单位**：N/A；**接口**：脚本 |
| `SolverIterations` | 决定在求解器（`Targeter`、`Optimize`）序列期间，与受扰轨迹关联的数据是否显示在 `XYPlot` 中。设为 `All` 时绘制所有扰动/迭代；设为 `Current` 时只绘制当前解或扰动；设为 `None` 时只绘制最终标称运行结果。**数据类型**：枚举；**允许值**：`All`、`Current`、`None`；**访问**：set；**默认值**：`Current`；**单位**：N/A；**接口**：GUI、脚本 |
| `XVariable` | 允许用户定义 `XYPlot` 的自变量。只能定义一个自变量。例如，`MyXYPlot.XVariable = DefaultSC.A1ModJulian` 把自变量设为 `DefaultSC` 的历元（A1 时间系统、修正儒略日格式）。该字段不能在任务序列中修改。**数据类型**：资源引用；**允许值**：`Variable`、`Array`、数组元素、求值为实数的 `Spacecraft` 参数；**访问**：get、set；**默认值**：`DefaultSC.A1ModJulian`；**单位**：N/A；**接口**：GUI、脚本 |
| `YVariables` | 允许用户向 XY 曲线图添加因变量。所有因变量都绘制在 Y 轴上，对应 `XVariable` 字段定义的自变量。因变量必须始终包含在花括号内，例如 `MyXYPlot.YVariables = {DefaultSC.EarthMJ2000Eq.Y, DefaultSC.EarthMJ2000Eq.Z}`。该字段不能在任务序列中修改。**数据类型**：引用数组；**允许值**：任何求值为实数的用户变量、数组元素或航天器参数；**访问**：get、set；**默认值**：`DefaultSC.EarthMJ2000Eq.X`；**单位**：N/A；**接口**：GUI、脚本 |

## GUI

下图显示 `XYPlot` 资源的默认设置：

> [图：XYPlot 资源 GUI 设置面板]

## 备注

### 使用 XYPlot 资源与 Toggle 命令时的行为

`XYPlot` 资源在整个任务持续期间的每个传播步向图的 X 轴和 Y 轴绘制数据。如果你只想在任务的特定点向 `XYPlot` 报告数据，可以在任务序列中插入 `Toggle On`/`Off` 命令来控制 `XYPlot` 何时绘制数据。对某个 `XYPlot` 发出 `Toggle Off` 命令后，在发出 `Toggle On` 命令之前不会向图的 X 轴和 Y 轴绘制任何数据；同样，使用 `Toggle On` 命令后，每个积分步都会向 X 轴和 Y 轴绘制数据，直到使用 `Toggle Off` 命令为止。

下面的脚本片段示例展示了如何在使用 `XYPlot` 资源时使用 `Toggle Off` 和 `Toggle On` 命令。航天器的位置模值和半长轴被绘制为时间的函数：

```
Create Spacecraft aSat
Create Propagator aProp

Create XYPlot aXYPlot
aXYPlot.XVariable = aSat.ElapsedDays
aXYPlot.YVariables = {aSat.Earth.RMAG, aSat.Earth.SMA}

BeginMissionSequence

Toggle aXYPlot Off
Propagate aProp(aSat) {aSat.ElapsedDays = 2}
Toggle aXYPlot On
Propagate aProp(aSat) {aSat.ElapsedDays = 4}
```

说明：前 2 天关闭绘图，之后打开并继续传播 4 天，绘制 RMAG 与 SMA 随时间变化曲线。

### 使用 XYPlot 与 Spacecraft 资源时的行为

`Spacecraft` 资源包含航天器轨道、姿态、物理参数（如质量和阻力系数）以及任何挂载硬件（包括推力器和燃料贮箱）的信息。`Spacecraft` 资源在整个任务持续期间与 `XYPlot` 交互。在每个传播步，从航天器检索到的数据就是绘制到图的 X 轴和 Y 轴上的数据。

### 在 XYPlot 的 YVariables 字段中指定空括号时的行为

使用 `XYPlot.YVariables` 字段时，GMAT 不允许括号留空。括号必须始终填入你希望与 `XVariable` 字段中的变量对应绘制的值。如果括号留空，GMAT 会抛出异常。下面的示例脚本片段展示了空括号的情形。如果运行该脚本，GMAT 会抛出异常，提醒你 `YVariables` 字段的括号不能留空：

```
Create Spacecraft aSat
Create Propagator aProp
Create XYPlot aXYPlot

aXYPlot.XVariable = aSat.ElapsedDays
aXYPlot.YVariables = {}

BeginMissionSequence
Propagate aProp(aSat) {aSat.ElapsedDays = 2}
```

说明：`YVariables` 为空集合，运行时会抛出异常。

### 在迭代过程中报告数据时的行为

GMAT 允许你指定在差分校正或优化等迭代过程中如何向图绘制数据。`XYPlot` 资源的 `SolverIterations` 字段支持三个选项：

| SolverIterations 选项 | 描述 |
| --- | --- |
| `Current` | 只显示迭代过程中的当前迭代/扰动，并把当前迭代绘制到图上 |
| `All` | 显示迭代过程中的所有迭代/扰动，并把所有迭代/扰动绘制到图上 |
| `None` | 只显示迭代过程结束后的最终解，并只把该最终解绘制到图上 |

## 示例

传播一条轨道，并在每个积分步把航天器高度绘制为时间的函数：

```
Create Spacecraft aSat
Create Propagator aProp

Create XYPlot aXYPlot
aXYPlot.XVariable = aSat.ElapsedSecs
aXYPlot.YVariables = {aSat.Earth.Altitude}

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 4}
```

说明：以经过秒数为自变量绘制地球高度曲线，传播 4 天。

在迭代过程中绘制数据。注意 `SolverIterations` 字段选为 `All`，即所有迭代/扰动都会被绘制：

```
Create Spacecraft aSat
Create Propagator aProp

Create ImpulsiveBurn TOI
Create DifferentialCorrector aDC

Create XYPlot aXYPlot
aXYPlot.SolverIterations = All
aXYPlot.XVariable = aSat.ElapsedDays
aXYPlot.YVariables = {aSat.Earth.RMAG}

BeginMissionSequence

Propagate aProp(aSat) {aSat.Earth.Periapsis}
Target aDC
 Vary aDC(TOI.Element1 = 0.24, {Perturbation = 0.001, Lower = 0.0, ...
 Upper = 3.14159, MaxStep = 0.5})
 Maneuver TOI(aSat)
 Propagate aProp(aSat) {aSat.Earth.Apoapsis}
 Achieve aDC(aSat.Earth.RMAG = 42165)
EndTarget
```

说明：在差分校正目标定位过程中绘制每次迭代的 RMAG 曲线，目标为 RMAG = 42165 km。