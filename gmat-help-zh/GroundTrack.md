# 星下点轨迹（GroundTrack）

> 译自 GMAT R2026a 帮助文档 GroundTrack.html

**GroundTrack** —— 用户自定义资源，用于绘制航天器经度和纬度的时间历程。

## 描述

`GroundTrack` 资源允许你将航天器的经度和纬度时间历程绘制到用户所选中心天体的纹理地图上。GMAT 允许把任意数量航天器的星下点轨迹绘制到同一张纹理地图上。你可以通过 GMAT 的 GUI 或脚本接口创建多个 `GroundTrack` 资源。GMAT 还提供 `Toggle On`/`Off` 命令，用于控制何时开始向 `GroundTrack` 绘制或停止绘制航天器的星下点轨迹。`GroundTrack` 资源与 `Toggle` 命令的交互详见下文"备注"一节。`GroundTrack` 资源还允许你在中心天体的纹理地图上显示任意数量的用户自定义地面站。

**另请参阅**：`Toggle`、`GroundStation`、`Color`

## 字段

| 字段 | 描述 |
| --- | --- |
| `Add` | 允许用户挑选所选资源，如 `Spacecraft`（航天器）或 `GroundStation`（地面站）。`GroundTrack` 对象用于在你选择的中心天体二维纹理地图上绘制航天器的经纬度时间历程。创建 `GroundStation` 对象后，也可以把地面站添加到中心天体的纹理地图上。要选择多个航天器或地面站，用逗号分隔列表并用花括号括起，例如：`DefaultGroundTrack.Add = {aSat, bSat, aGroundStaton, bGroundStation}`。该字段不能在任务序列中修改。**数据类型**：引用数组；**允许值**：`Spacecraft`、`GroundStation`；**访问**：set；**默认值**：`DefaultSC`；**单位**：N/A；**接口**：GUI、脚本 |
| `CentralBody` | 星下点轨迹图的中心天体。该字段不能在任务序列中修改。**数据类型**：资源引用；**允许值**：`CelestialBody`；**访问**：set；**默认值**：`Earth`；**单位**：N/A；**接口**：GUI、脚本 |
| `DataCollectFrequency` | 绘图点之间跳过的积分步数。该字段不能在任务序列中修改。**数据类型**：整数；**允许值**：整数 >= 1；**访问**：set；**默认值**：1；**单位**：N/A；**接口**：GUI、脚本 |
| `Maximized` | 允许用户最大化 `GroundTrack` 窗口。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：true、false；**访问**：set；**默认值**：false；**单位**：N/A；**接口**：脚本 |
| `NumPointsToRedraw` | 在传播和动画过程中保留并重绘的绘图点数量。0 表示全部重绘。该字段不能在任务序列中修改。**数据类型**：整数；**允许值**：整数 >= 0；**访问**：set；**默认值**：0；**单位**：N/A；**接口**：GUI、脚本 |
| `RelativeZOrder` | 允许用户选择哪个 `GroundTrack` 窗口最先显示在屏幕上。`RelativeZOrder` 值最低的 `GroundTrack` 最后显示，值最高的最先显示。该字段不能在任务序列中修改。**数据类型**：整数；**允许值**：整数 ≥ 0；**访问**：set；**默认值**：0；**单位**：N/A；**接口**：脚本 |
| `ShowPlot` | 指定在任务运行期间是否显示星下点轨迹图。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：True、False；**访问**：set；**默认值**：True；**单位**：N/A；**接口**：GUI、脚本 |
| `Size` | 允许用户控制 `GroundTrack` 窗口的显示尺寸。[0 0] 矩阵中第一个值控制水平尺寸，第二个值控制垂直尺寸。该字段不能在任务序列中修改。**数据类型**：实数数组；**允许值**：任意实数；**访问**：set；**默认值**：[ 0 0 ]；**单位**：N/A；**接口**：脚本 |
| `SolverIterations` | 决定在求解器（`Targeter`、`Optimize`）序列期间，与受扰轨迹关联的星下点轨迹数据是否显示在 `GroundTrack` 中。设为 `All` 时，所有扰动/迭代都绘制到 `GroundTrack`；设为 `Current` 或 `None` 时，只绘制最终标称运行结果。**数据类型**：枚举；**允许值**：`All`、`Current`、`None`；**访问**：set；**默认值**：`Current`；**单位**：N/A；**接口**：GUI、脚本 |
| `TextureMap` | 允许你输入或选择中心天体的任意用户自定义纹理地图图像。该字段不能在任务序列中修改。**数据类型**：字符串；**允许值**：有效的文件路径和文件名；**访问**：set；**默认值**：`../data/graphics/texture/ModifiedBlueMarble.jpg`；**单位**：N/A；**接口**：GUI、脚本 |
| `UpdatePlotFrequency` | 更新星下点轨迹图之前要收集的绘图点数量。该字段不能在任务序列中修改。**数据类型**：整数；**允许值**：整数 > 1；**访问**：set；**默认值**：50；**单位**：N/A；**接口**：GUI、脚本 |
| `UpperLeft` | 允许用户沿任意方向平移 `GroundTrack` 显示窗口。[0 0] 矩阵中第一个值水平平移窗口，第二个值垂直平移窗口。该字段不能在任务序列中修改。**数据类型**：实数数组；**允许值**：任意实数；**访问**：set；**默认值**：[ 0 0 ]；**单位**：无；**接口**：脚本 |

## GUI

`GroundTrack` 资源的默认名称和设置：

> [图：GroundTrack 资源 GUI 设置面板]

## 备注

### 使用 GroundTrack 资源与 Toggle 命令时的行为

`GroundTrack` 资源在整个任务持续期间的每个传播步绘制航天器的经纬度时间历程。如果你只想在任务的特定点向 `GroundTrack` 报告数据，可以在任务序列中插入 `Toggle On`/`Off` 命令来控制 `GroundTrack` 何时绘制数据。对某个 `GroundTrack` 发出 `Toggle Off` 命令后，在发出 `Toggle On` 命令之前不会绘制任何星下点轨迹数据；同样，使用 `Toggle On` 命令后，每个积分步都会绘制星下点轨迹数据，直到使用 `Toggle Off` 命令为止。

下面的脚本片段示例展示了如何在使用 `GroundTrack` 资源时使用 `Toggle Off` 和 `Toggle On` 命令。传播的前 2 天关闭 `GroundTrack`：

```
Create Spacecraft aSat
Create Propagator aProp

Create GroundTrack aGroundTrack
aGroundTrack.Add = {aSat}

BeginMissionSequence

Toggle aGroundTrack Off
Propagate aProp(aSat) {aSat.ElapsedDays = 2}
Toggle aGroundTrack On
Propagate aProp(aSat) {aSat.ElapsedDays = 4}
```

说明：先关闭星下点轨迹绘制，传播 2 天后再打开，继续传播 4 天。

### 在迭代过程中绘制数据时的行为

GMAT 允许你指定在差分校正或优化等迭代过程中如何向图绘制数据。`GroundTrack` 资源的 `SolverIterations` 字段支持 3 个选项：

| SolverIterations 选项 | 描述 |
| --- | --- |
| `Current` | 只显示迭代过程中的当前迭代/扰动，并把当前迭代绘制到图上 |
| `All` | 显示迭代过程中的所有迭代/扰动，并把所有迭代/扰动绘制到图上 |
| `None` | 只显示迭代过程结束后的最终解，并只把最终解绘制到图上 |

### 绘制航天器经纬度时间历程时的行为

GMAT 的 `GroundTrack` 资源允许你绘制航天器的经纬度时间历程。你可以选择把多个航天器的星下点轨迹绘制到中心天体的同一张纹理地图上。

> **警告**：航天器的经纬度是以包含直线段的近似方式绘制的，经纬度数据不考虑中心天体的形状或其扁率。

### 在 GroundTrack 的 Add 字段中指定空括号时的行为

使用 `GroundTrack.Add` 字段时，如果括号内没有填入用户自定义的航天器，GMAT 会关闭 `GroundTrack` 资源，不生成任何图。如果在 `Add` 字段为空括号的情况下运行脚本，GMAT 会在消息窗口中抛出警告，提示由于没有向图添加任何 SpacePoint，`GroundTrack` 资源将被关闭。会产生此类警告消息的示例脚本片段：

```
Create Spacecraft aSat aSat2
Create Propagator aProp
Create GroundTrack aGroundTrack

aGroundTrack.Add = {}

BeginMissionSequence;
Propagate aProp(aSat, aSat2) {aSat.ElapsedDays = 1}
```

说明：`Add` 字段为空集合，运行时 GMAT 将给出警告并关闭该星下点轨迹图。

## 示例

本例展示如何使用 `GroundTrack` 资源。向 `GroundTrack` 添加一个航天器和一个地面站，绘制航天器传播一天的星下点轨迹：

```
Create Spacecraft aSat
Create Propagator aProp

Create GroundStation aGroundStation

Create GroundTrack aGroundTrack
aGroundTrack.Add = {aSat, aGroundStation}

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1}
```

说明：创建航天器、传播器、地面站和星下点轨迹图，将航天器与地面站加入图中，传播 1 天。

围绕非默认中心天体传播航天器两天。航天器的星下点轨迹绘制在火星上：

```
Create Spacecraft aSat
aSat.CoordinateSystem = MarsJ2000Eq
aSat.SMA = 8000
aSat.ECC = 0.0003

Create ForceModel aFM
aFM.CentralBody = Mars
aFM.PointMasses = {Mars}

Create Propagator aProp
aProp.FM = aFM

Create CoordinateSystem MarsJ2000Eq
MarsJ2000Eq.Origin = Mars
MarsJ2000Eq.Axes = MJ2000Eq

Create GroundTrack aGroundTrack
aGroundTrack.Add = {aSat}
aGroundTrack.CentralBody = Mars

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 2}
```

说明：定义以火星为中心的坐标系与力模型，将星下点轨迹图的中心天体设为火星，传播 2 天。