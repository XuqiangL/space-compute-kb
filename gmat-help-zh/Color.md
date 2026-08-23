# 颜色（Color）
> 译自 GMAT R2026a 帮助文档 Color.html

Color —— GMAT 资源和命令中的颜色支持。

## 描述

GMAT 允许你为 `Spacecraft`（航天器）、`CelestialBody`（天体）、`LibrationPoint`（平动点）和 `Barycenter`（质心）资源绘制的轨道轨迹段指定不同的颜色。你也可以通过 `Propagate` 命令设置颜色，为 `Spacecraft` 的轨道轨迹段指定独特的颜色。这些资源的轨道轨迹使用 `OrbitView` 三维图形资源绘制。此外，GMAT 还允许你为 `GroundStation`（地面站）设施设置颜色，这些设施绘制在由 `GroundTrack` 二维图形资源创建的航天器地面轨迹图上。

除了可以为以下五个资源和一条命令——`Spacecraft`、`CelestialBody`、`LibrationPoint`、`Barycenter`、`GroundStation` 和 `Propagate`——的轨道轨迹段设置颜色之外，GMAT 还允许你为上述五个资源可能绘制的摄动轨迹指定颜色。这些摄动轨迹在差分校正或优化等迭代过程中绘制。上述五个资源和单条 `Propagate` 命令都有一个名为 `OrbitColor` 的公共字段。`OrbitColor` 字段用于设置这些资源和单条命令所绘制轨道轨迹段的颜色。同样，这五个资源还有一个名为 `TargetColor` 的公共字段（`Propagate` 命令没有 `TargetColor` 字段）。这五个资源的 `TargetColor` 字段可用于设置在迭代过程中可能绘制的摄动轨迹的颜色。

你可以通过 GMAT 的 GUI 或脚本接口为上述五个资源和 `Propagate` 命令设置颜色。通过 GUI 模式为这五个资源和单条命令设置颜色非常简单：打开这五个资源中的任意一个或 `Propagate` 命令后，你可以从 Orbit Color 选择框中单击任意可用颜色来为 `OrbitColor` 字段选择颜色。同样，对于这五个资源，你可以从 Target Color 选择框中选择任意可用颜色来为 `TargetColor` 字段选择颜色。参见下面的 GUI 一节，其中通过一个示例演示了如何通过 GUI 模式选择颜色。

通过 GMAT 的脚本模式为 `OrbitColor` 和 `TargetColor` 字段设置颜色有两种方式。可用颜色通过字符串或三位整数数组来标识。你可以输入颜色名（ColorName）或其对应的 RGB 三元组值来输入所选颜色。下表列出了可供选择的 75 种颜色。表中每一行列出一种可用颜色的 ColorName 和等效的 RGB 三元组值。请参阅上述五个资源的"字段"一节和 `Propagate` 命令的"选项"一节，进一步了解 `OrbitColor` 和 `TargetColor` 字段以及如何设置颜色。另请参阅下面的"备注"一节，其中提供了更多脚本片段，展示如何通过 ColorName 或 RGB 三元组值输入法为上述五个资源和单条命令指定颜色。

| ColorName | 等效 RGB 三元组值 |
|-----------|------------------|
| Aqua | 0 255 255 |
| AquaMarine | 127 55 212 |
| Beige | 245 245 220 |
| Black | 0 0 0 |
| Blue | 0 0 255 |
| BlueViolet | 138 43 226 |
| Brown | 165 42 42 |
| CadetBlue | 95 158 160 |
| Coral | 255 127 80 |
| CornflowerBlue | 100 149 237 |
| Cyan | 0 255 255 |
| DarkBlue | 0 0 139 |
| DarkGoldenRod | 184 134 11 |
| DarkGray | 169 169 169 |
| DarkGreen | 0 100 0 |
| DarkOliveGreen | 85 107 47 |
| DarkOrchid | 153 50 204 |
| DarkSlateBlue | 72 61 139 |
| DarkSlateGray | 47 79 79 |
| DarkTurquoise | 0 206 209 |
| DimGray | 105 105 105 |
| FireBrick | 178 34 34 |
| ForestGreen | 34 139 34 |
| Fuchsia | 255 0 255 |
| Gold | 255 215 0 |
| GoldenRod | 218 165 32 |
| Gray | 128 128 128 |
| Green | 0 128 0 |
| GreenYellow | 173 255 47 |
| IndianRed | 205 92 92 |
| Khaki | 240 230 140 |
| LightBlue | 173 216 230 |
| LightGray | 211 211 211 |
| Lime | 0 255 0 |
| LimeGreen | 50 205 50 |
| LightSteelBlue | 176 196 222 |
| Magenta | 255 0 255 |
| Maroon | 128 0 0 |
| MediumAquaMarine | 102 205 170 |
| MediumBlue | 0 0 205 |
| MediumOrchid | 186 85 211 |
| MediumSeaGreen | 60 179 113 |
| MediumSpringGreen | 0 250 154 |
| MediumTurquoise | 72 209 204 |
| MediumVioletRed | 199 21 133 |
| MidnightBlue | 25 25 112 |
| Navy | 0 0 128 |
| Olive | 128 128 0 |
| Orange | 255 165 0 |
| OrangeRed | 255 69 0 |
| Orchid | 218 112 214 |
| PaleGreen | 152 251 152 |
| Peru | 205 133 63 |
| Pink | 255 192 203 |
| Plum | 221 160 221 |
| Purple | 128 0 128 |
| Red | 255 0 0 |
| SaddleBrown | 244 164 96 |
| Salmon | 250 128 114 |
| SeaGreen | 46 139 87 |
| Sienna | 160 82 45 |
| Silver | 192 192 192 |
| SkyBlue | 135 206 235 |
| SlateBlue | 106 90 205 |
| SpringGreen | 0 255 127 |
| SteekBlue | 70 130 180 |
| Tan | 210 180 140 |
| Teal | 0 128 128 |
| Thistle | 216 191 216 |
| Turquoise | 64 224 208 |
| Violet | 238 130 238 |
| Wheat | 245 222 179 |
| White | 255 255 255 |
| Yellow | 255 255 0 |
| YellowGreen | 154 205 50 |

**另请参见**：Spacecraft Visualization Properties、CelestialBody、LibrationPoint、Barycenter、GroundStation、Propagate

## GUI

通过 GMAT 的 GUI 模式为 `Spacecraft`、`GroundStation`、`CelestialBody`、`LibrationPoint` 和 `Barycenter` 资源的 `OrbitColor` 和 `TargetColor` 字段设置颜色非常简单。由于这五个资源设置颜色的过程相同，因此下面仅以 `Spacecraft` 资源为例给出一个 GUI 示例：

打开 `Spacecraft` 资源后，单击 Visualization（可视化）选项卡。

> [图：Spacecraft 资源的 Visualization 选项卡，含 Orbit Color 和 Target Color 选择框]

在 Visualization 窗口中，你会看到 Orbit Color 和 Target Color 选择框。你可以分别单击 Orbit Color 和 Target Color 选择框来为 `OrbitColor` 和 `TargetColor` 字段选择颜色。例如，单击 Orbit Color 或 Target Color 选择框中的任意一个，都会打开下图所示的颜色面板。使用此颜色面板，你可以选择基本颜色、创建自定义颜色，并将自定义颜色添加到可用颜色列表中。

> [图：颜色选择面板，含基本颜色和自定义颜色]

通过 GUI 模式为 `Propagate` 命令的 `OrbitColor` 选项选择颜色也非常简单。打开任意 `Propagate` 命令。下图是 GMAT 默认 `Propagate` 命令的截图：

> [图：Propagate 命令的 GUI 面板，含 Override Color For This Segment 复选框]

在 GMAT 中，任何 `Propagate` 命令的默认轨道颜色都是 `Spacecraft` 资源的 `OrbitColor` 字段上设置的颜色（即 `Spacecraft.OrbitColor`）。只要你没有在 `Propagate` 命令的 `OrbitColor` 选项上设置独特颜色，`Propagate` 命令上的颜色就始终是 `Spacecraft` 对象的 `OrbitColor` 字段上设置的颜色。

要为 `Propagate` 命令设置自己的独特颜色，单击并勾选 **Override Color For This Segment**（覆盖此段颜色）复选框。这会激活 Orbit Color 选择框。单击 Orbit Color 选择框会打开下图所示的颜色面板：

> [图：颜色选择面板]

使用此颜色面板，你可以选择基本颜色、创建自定义颜色、将自定义颜色添加到可用颜色列表，并将其设置到 `Propagate` 命令的 `OrbitColor` 选项上。

## 备注

### 在 Spacecraft 资源上配置轨道颜色和目标颜色

你可以通过为 `Spacecraft` 对象的 `OrbitColor` 字段指定颜色，为 `Spacecraft` 的轨道轨迹设置你选择的独特颜色。只要你没有在 `Propagate` 命令上重置或重新指定轨道颜色，GMAT 绘制的所有航天器轨迹颜色都将与你最初在 `Spacecraft` 对象的 `OrbitColor` 字段上设置的颜色相同。`Spacecraft` 对象的 `OrbitColor` 字段的默认颜色设置为红色。在此默认红色设置下，只要你没有在任何 `Propagate` 命令上重置轨道颜色，所有 `Spacecraft` 轨迹都将以红色绘制。例如，如果你希望所有 `Spacecraft` 轨道轨迹仅以黄色绘制，下面的脚本片段演示了为 `Spacecraft` 对象的 `OrbitColor` 字段设置黄色的两种可接受方法：

```
Create Spacecraft aSat
aSat.OrbitColor = Yellow       % ColorName method
% or
aSat.OrbitColor = [255 255 0]  % RGB triplet value method
```

说明：两种方法等价——直接写颜色名 Yellow，或写 RGB 三元组 [255 255 0]。

同样，为航天器在差分校正或优化等迭代过程中可能绘制的摄动轨迹设置所选颜色，可以通过为 `Spacecraft` 对象的 `TargetColor` 字段指定独特颜色来完成。只有当你想为迭代过程中生成的摄动轨迹指定颜色时，设置 `TargetColor` 字段才有用。`Spacecraft` 对象的 `OrbitColor` 和 `TargetColor` 字段也可以在任务序列中使用和修改。下面的示例脚本片段展示了为 `Spacecraft` 资源的 `TargetColor` 字段设置蓝紫色（BlueViolet）的两种可接受方法：

```
Create Spacecraft aSat
aSat.TargetColor = BlueViolet    % ColorName method
% or
aSat.TargetColor = [138 43 226]  % RGB triplet value method
```

说明：用颜色名 BlueViolet 或 RGB 值 [138 43 226] 设置摄动轨迹颜色。

你可以在 `Spacecraft` 对象的 `OrbitColor` 和 `TargetColor` 字段上设置的可用颜色列表已列于"描述"一节的表格中。你可以通过 ColorName 或 RGB 三元组值输入法指定颜色。另请参阅下面的"示例"一节，其中提供了完整的示例脚本，展示如何使用 `Spacecraft` 对象的 `OrbitColor` 和 `TargetColor` 字段。

### 在 GroundStation 资源上设置颜色

GMAT 允许你为 `GroundStation` 对象的 `OrbitColor` 或 `TargetColor` 字段设置你选择的独特颜色。可设置的可用颜色列表已列于"描述"一节的表格中。你可以通过 ColorName 或 RGB 三元组值方法指定颜色。你创建的自定义地面站设施会显示在航天器的地面轨迹图上，该图绘制在中心天体的二维纹理地图上。只有当 `GroundStation` 对象在差分校正或优化等迭代过程中被绘制时，才会使用在 `GroundStation` 对象的 `TargetColor` 字段上指定的颜色。下面的脚本片段展示了如何使用 ColorName 或 RGB 方法为 `GroundStation` 的 `OrbitColor` 和 `TargetColor` 字段设置颜色：

```
Create GroundStation aGroundStation 
aGroundStation.OrbitColor = Aqua          % ColorName method
% or
aGroundStation.OrbitColor = [0 255 255]   % RGB method
```

```
Create GroundStation aGroundStation 
aGroundStation.TargetColor = Black     % ColorName method
% or
aGroundStation.TargetColor = [0 0 0]   % RGB method
```

说明：分别为地面站的正常显示颜色（OrbitColor，Aqua 青色）和迭代过程显示颜色（TargetColor，Black 黑色）演示了颜色名与 RGB 两种输入法。

请参阅下面的"示例"一节，其中提供了展示如何使用 `GroundStation` 对象的 `OrbitColor` 字段的完整示例脚本。

### 在 CelestialBody 资源上配置轨道颜色和目标颜色

GMAT 允许你为内置或自定义天体的轨道设置可用颜色。GMAT 包含太阳、八大行星、地球月球和冥王星的内置模型。你可以创建自定义 `CelestialBody` 资源来建模行星、小行星、彗星或卫星。`CelestialBody` 对象的轨道颜色通过 `OrbitColor` 字段设置。你也可以为天体在差分校正或优化等迭代过程中生成的摄动轨迹设置颜色，这通过设置 `CelestialBody` 对象的 `TargetColor` 字段来完成。只有当你想为迭代过程中生成的摄动轨迹指定颜色时，设置 `TargetColor` 字段才有用。可在 `OrbitColor` 和 `TargetColor` 字段上设置的可用颜色列表已列于"描述"一节的表格中。指定颜色时，你可以使用 ColorName 或 RGB 三元组值方法。`CelestialBody` 对象的 `OrbitColor` 和 `TargetColor` 字段也可以在任务序列中使用和修改。下面的脚本片段展示了如何使用 ColorName 或 RGB 方法为自定义天体的 `OrbitColor` 和 `TargetColor` 字段设置颜色：

```
Create Planet aPlanet 
aPlanet.OrbitColor = CornflowerBlue   % ColorName method
% or
aPlanet.OrbitColor = [100 149 237]    % RGB method
```

```
Create Planet aPlanet 
aPlanet.TargetColor = DarkBlue     % ColorName method
% or
aPlanet.TargetColor = [0 0 139]    % RGB method
```

说明：为自定义行星 aPlanet 的轨道颜色（矢车菊蓝）和目标颜色（深蓝）分别演示颜色名与 RGB 两种输入法。

请参阅下面的"示例"一节，其中提供了展示如何使用 `CelestialBody` 对象的 `OrbitColor` 字段的完整示例脚本。

### 在 LibrationPoint 资源上配置轨道颜色和目标颜色

GMAT 允许你为平动点绘制的轨道设置可用颜色。要看到平动点在空间中绘制的轨道轨迹，必须在惯性空间中绘制拉格朗日点。`LibrationPoint` 资源的轨道颜色通过 `OrbitColor` 字段设置。GMAT 还允许你为平动点在差分校正或优化等迭代过程中绘制的摄动轨迹设置颜色。为摄动平动点轨迹设置颜色通过 `TargetColor` 字段完成。只有当迭代过程中生成摄动平动点轨迹时，设置 `TargetColor` 字段才有用。可在 `OrbitColor` 和 `TargetColor` 字段上设置的可用颜色已列于"描述"一节的表格中。你可以使用 ColorName 或 RGB 三元组值方法为 `OrbitColor` 和 `TargetColor` 字段指定颜色。`LibrationPoint` 资源的这两个字段也可以在任务序列中使用和修改以设置颜色。下面的脚本片段展示了如何使用 ColorName 或 RGB 方法为 `OrbitColor` 和 `TargetColor` 字段设置颜色：

```
Create LibrationPoint ESL1 
ESL1.OrbitColor = Magenta           % ColorName method
% or
ESL1.OrbitColor = [255 0 255]       % RGB method
```

```
Create LibrationPoint ESL1 
ESL1.TargetColor = Orchid           % ColorName method
% or
ESL1.TargetColor = [218 112 214]    % RGB method
```

说明：为日地 L1 平动点 ESL1 的轨道颜色（品红）和目标颜色（兰花紫）分别演示颜色名与 RGB 两种输入法。

请参阅下面的"示例"一节，其中提供了展示如何使用 `LibrationPoint` 对象的 `OrbitColor` 字段的完整示例脚本。

### 在 Barycenter 资源上配置轨道颜色和目标颜色

在 GMAT 中，你可以为质心点绘制的轨道指定可用颜色。由于质心是一组天体的质量中心，因此要看到它的轨道轨迹，必须在惯性空间中绘制质心。你可以在 GMAT 内置的 `SolarSystemBarycenter` 资源或通过 `Barycenter` 对象创建的自定义质心上设置轨道颜色。`Barycenter` 资源的轨道颜色通过 `OrbitColor` 字段设置。GMAT 还允许你为质心在差分校正或优化等迭代过程中绘制的摄动轨迹设置颜色。为摄动质心轨迹设置颜色通过 `TargetColor` 字段完成。只有当你想为摄动轨迹设置不同颜色时，设置 `TargetColor` 字段才有用。可在 OrbitColor 和 `TargetColor` 字段上设置的可用颜色已列于"描述"一节的表格中。你可以使用 ColorName 或 RGB 三元组值颜色输入法为 `OrbitColor` 和 `TargetColor` 字段指定颜色。`Barycenter` 资源的这两个字段也可以在任务序列中使用和修改。下面的脚本片段展示了如何使用 ColorName 或 RGB 方法为 `OrbitColor` 和 `TargetColor` 字段设置颜色：

```
Create Barycenter EarthMoonBarycenter
EarthMoonBarycenter.OrbitColor = Violet         % ColorName method
% or
EarthMoonBarycenter.OrbitColor = [238 130 238]  % RGB method
```

```
Create Barycenter EarthMoonBarycenter
EarthMoonBarycenter.TargetColor = Silver         % ColorName method
% or
EarthMoonBarycenter.TargetColor = [192 192 192]  % RGB method
```

说明：为地月质心的轨道颜色（紫罗兰色）和目标颜色（银色）分别演示颜色名与 RGB 两种输入法。

请参阅下面的"示例"一节，其中提供了展示如何使用 `Barycenter` 对象的 `OrbitColor` 字段的完整示例脚本。

### 在 Propagate 命令上配置轨道颜色

在 GMAT 中，你可以通过在 `Propagate` 命令上设置轨道颜色，为不同的 `Spacecraft` 轨迹段设置独特颜色。如果你没有在每条 `Propagate` 命令上选择独特颜色，则默认情况下，所有 `Propagate` 命令的颜色都取自 `Spacecraft` 对象的 `OrbitColor` 字段上设置的颜色。你可以通过 `OrbitColor` 选项为每条 `Propagate` 命令设置轨道颜色。可在 `Propagate` 命令的 `OrbitColor` 选项上设置的可用颜色已列于"描述"一节的表格中。你可以使用 ColorName 或 RGB 三元组值输入法为 `OrbitColor` 选项指定颜色。下面的脚本片段展示了如何使用 ColorName 或 RGB 方法为 `OrbitColor` 选项设置颜色：

```
% ColorName method:
Propagate aProp(aSat) {aSat.ElapsedSecs = 500, OrbitColor = Gold}
% or RGB method:
Propagate aProp(aSat) {aSat.ElapsedSecs = 500, OrbitColor = [255 215 0]}
```

说明：在 Propagate 的停止条件花括号内追加 `OrbitColor = ...` 选项即可覆盖该段轨迹颜色；颜色名 Gold 与 RGB 值 [255 215 0] 等价。

请参阅下面的"示例"一节，其中提供了展示如何使用 `Propagate` 命令的 `OrbitColor` 选项的完整示例脚本。

## 示例

通过 ColorName 和 RGB 三元组值两种方法为 `Spacecraft` 对象的 `OrbitColor` 字段设置非默认的天蓝色。两种方法都将航天器轨道轨迹绘制为天蓝色。注意：由于轨道颜色没有在 `Propagate` 命令中重新设置，因此整条航天器轨道轨迹都以天蓝色绘制：

```
Create Spacecraft aSat
aSat.OrbitColor = SkyBlue   % ColorName method
Create Propagator aProp

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1}

% or

Create Spacecraft aSat
aSat.OrbitColor = [135 206 235]   % RGB triplet value method
Create Propagator aProp

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1}
```

说明：两段脚本等价，分别以颜色名 SkyBlue 和 RGB 值 [135 206 235] 设置航天器轨道颜色；Propagate 未覆盖颜色，所以整段轨迹均为天蓝色。

通过 ColorName 和 RGB 方法的组合，多次为 `Spacecraft` 对象的 `OrbitColor` 字段设置独特颜色。注意 `Spacecraft.OrbitColor` 也在任务序列中被使用和修改：

```
Create Spacecraft aSat
aSat.OrbitColor = Yellow   % ColorName method
Create Propagator aProp

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedSecs = 1000}
aSat.OrbitColor = Green   % ColorName method
Propagate aProp(aSat) {aSat.ElapsedSecs = 1000}
aSat.OrbitColor = [255 165 0 ]   % RGB value for Orange
Propagate aProp(aSat) {aSat.ElapsedSecs = 2000}
```

说明：初始颜色为黄色；任务序列中每传播一段后修改 aSat.OrbitColor（黄色→绿色→橙色），使三段轨迹分别呈现不同颜色。

为 `Spacecraft` 对象的 `TargetColor` 字段设置非默认的黄色。只有在差分校正等迭代过程中生成摄动轨迹时，设置 `TargetColor` 字段才有用。注意此处黄色通过 ColorName 方法设置，同样也可以通过 RGB 三元组值方法设置。

```
Create Spacecraft aSat
aSat.OrbitColor = Red       % Default OrbitColor
aSat.TargetColor = Yellow  % ColorName method

Create Propagator aProp

Create ImpulsiveBurn TOI

Create DifferentialCorrector aDC

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}
anOrbitView.SolverIterations = All
anOrbitView.ViewScaleFactor = 2


BeginMissionSequence

Propagate aProp(aSat) {aSat.Earth.Periapsis}

Target aDC;
Vary aDC(TOI.Element1 = 0.24, {Perturbation = 0.001, Lower = 0.0, ...
 Upper = 3.14159, MaxStep = 0.5})
 Maneuver TOI(aSat);
 Propagate aProp(aSat) {aSat.Earth.Apoapsis}
 Achieve aDC(aSat.Earth.RMAG = 20000)
EndTarget

Propagate aProp(aSat) {aSat.ElapsedDays = 0.25}
```

说明：正常轨迹为红色（OrbitColor），差分校正迭代中的摄动轨迹为黄色（TargetColor）；`anOrbitView.SolverIterations = All` 使求解器的所有迭代轨迹都被画出。Target 循环通过调整脉冲机动 TOI 的第一个分量，使远地点半径达到 20000 km。

通过 `OrbitColor` 字段为多个 `GroundStation` 对象设置非默认颜色。颜色通过 ColorName 和 RGB 输入方法的组合指定：

```
Create Spacecraft aSat
Create Propagator aProp

Create GroundStation aGroundStation aGroundStation2 aGroundStation3

aGroundStation.StateType = Spherical
aGroundStation.Latitude = 45
aGroundStation.OrbitColor = Black

aGroundStation2.StateType = Spherical
aGroundStation2.Longitude = 20
aGroundStation2.OrbitColor = [165 42 42]  % RGB value for Brown

aGroundStation3.StateType = Spherical
aGroundStation3.Latitude = 30
aGroundStation3.Longitude = 45
aGroundStation3.OrbitColor = [255 127 80]  % RGB value for Coral

Create GroundTrack aGroundTrack
aGroundTrack.Add = {aSat, aGroundStation, aGroundStation2, ...
aGroundStation3 }

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 0.25 }
```

说明：创建三个地面站，分别以球坐标设置经纬度，并把显示颜色设为黑色（颜色名）、棕色（RGB）和珊瑚色（RGB）；GroundTrack 资源把三个地面站加入显示列表，传播 0.25 天后即可在地面轨迹图上看到三种颜色的站点标记。

为内置天体轨道设置非默认颜色。本例中，`CelestialBody` 对象的 `OrbitColor` 字段通过 ColorName 和 RGB 三元组值方法的组合指定颜色。默认情况下，GMAT 把 `Spacecraft` 轨道颜色设为红色：

```
Create Spacecraft aSat
aSat.CoordinateSystem = SunMJ2000Ec
aSat.DisplayStateType = Keplerian
aSat.SMA = 150000000

Mercury.OrbitColor = Orange
Venus.OrbitColor = [255 255 0]  % RGB value for Yellow
Earth.OrbitColor = Cyan
Mars.OrbitColor = [0 128 0]  % RGB value for Green

Create CoordinateSystem SunMJ2000Ec
SunMJ2000Ec.Origin = Sun
SunMJ2000Ec.Axes = MJ2000Ec

Create ForceModel aFM
aFM.CentralBody = Sun
aFM.PointMasses = {Sun}

Create Propagator aProp
aProp.FM = aFM

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth, Venus, Mars, Mercury}
anOrbitView.CoordinateSystem = SunMJ2000Ec
anOrbitView.ViewPointReference = Sun
anOrbitView.ViewPointVector = [0 0 150000000]
anOrbitView.ViewDirection = Sun
anOrbitView.ViewScaleFactor = 6
anOrbitView.ViewUpCoordinateSystem = SunMJ2000Ec

BeginMissionSequence
Propagate aProp(aSat) {aSat.ElapsedDays = 150}
```

说明：在日心 MJ2000 黄道坐标系中传播 150 天；水星轨道设为橙色（颜色名）、金星黄色（RGB）、地球青色（颜色名）、火星绿色（RGB），航天器保持默认红色；OrbitView 以太阳为视点中心俯视整个内太阳系。

通过 ColorName 和 RGB 三元组值方法的组合，多次为内置 `CelestialBody` 对象的 `OrbitColor` 字段设置独特的非默认轨道颜色。注意 `CelestialBody.OrbitColor` 也在任务序列中被使用和修改：

```
Create Spacecraft aSat
aSat.CoordinateSystem = SunMJ2000Ec
aSat.DisplayStateType = Keplerian
aSat.SMA = 150000000

Mars.OrbitColor = Orange

Create CoordinateSystem SunMJ2000Ec
SunMJ2000Ec.Origin = Sun
SunMJ2000Ec.Axes = MJ2000Ec

Create ForceModel aFM
aFM.CentralBody = Sun
aFM.PointMasses = {Sun}

Create Propagator aProp
aProp.FM = aFM
aProp.MaxStep = 20000

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Mars}
anOrbitView.CoordinateSystem = SunMJ2000Ec
anOrbitView.ViewPointReference = Sun
anOrbitView.ViewPointVector = [0 0 150000000]
anOrbitView.ViewDirection = Sun
anOrbitView.ViewScaleFactor = 6
anOrbitView.ViewUpCoordinateSystem = SunMJ2000Ec

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 150}
Mars.OrbitColor = [255 255 0]  % RGB value for Yellow
Propagate aProp(aSat) {aSat.ElapsedDays = 150}
Mars.OrbitColor = Cyan
Propagate aProp(aSat) {aSat.ElapsedDays = 150}
Mars.OrbitColor = [0 128 0]   % RGB value for Green
Propagate aProp(aSat) {aSat.ElapsedDays = 150}
```

说明：火星轨道初始为橙色；任务序列中每传播 150 天修改一次 Mars.OrbitColor（橙→黄→青→绿），使火星轨道在不同时间段呈现不同颜色。

为日地 L1 平动点轨道设置独特的非默认轨道颜色。为了看到 ESL1 平动点绕太阳的轨道，必须在惯性空间中绘制它。`LibrationPoint` 对象的 `OrbitColor` 字段通过 ColorName 和 RGB 三元组值输入方法的组合多次设置。注意本例中 `LibrationPoint.OrbitColor` 也在任务序列中设置。默认情况下，GMAT 把 `Spacecraft` 轨道颜色设为红色：

```
Create Spacecraft aSat
aSat.CoordinateSystem = SunMJ2000Ec
aSat.DisplayStateType = Keplerian
aSat.SMA = 150000000

Create LibrationPoint ESL1
ESL1.OrbitColor = Orange
ESL1.Primary = Sun
ESL1.Secondary = Earth
ESL1.Point = L1

Create CoordinateSystem SunMJ2000Ec
SunMJ2000Ec.Origin = Sun
SunMJ2000Ec.Axes = MJ2000Ec

Create ForceModel aFM
aFM.CentralBody = Sun
aFM.PointMasses = {Sun}

Create Propagator aProp
aProp.FM = aFM

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, ESL1}
anOrbitView.CoordinateSystem = SunMJ2000Ec
anOrbitView.ViewPointReference = Sun
anOrbitView.ViewPointVector = [0 0 150000000]
anOrbitView.ViewDirection = Sun
anOrbitView.ViewScaleFactor = 3
anOrbitView.ViewUpCoordinateSystem = SunMJ2000Ec

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 75}
ESL1.OrbitColor = [255 255 0]  % RGB value for Yellow
Propagate aProp(aSat) {aSat.ElapsedDays = 75}
ESL1.OrbitColor = Cyan
Propagate aProp(aSat) {aSat.ElapsedDays = 75}
ESL1.OrbitColor = [0 128 0]   % RGB value for Green
Propagate aProp(aSat) {aSat.ElapsedDays = 75}
```

说明：创建日地 L1 平动点 ESL1（主天体 Sun、次天体 Earth），初始轨道颜色为橙色；任务序列中每传播 75 天修改一次 ESL1.OrbitColor（橙→黄→青→绿）。

为地月质心设置独特的非默认轨道颜色。为了看到地月质心绕太阳的轨道，必须在惯性空间中绘制它。`Barycenter` 对象的 `OrbitColor` 字段通过 ColorName 和 RGB 三元组值输入方法的组合多次设置。注意本例中 `Barycenter.OrbitColor` 也在任务序列中设置。默认情况下，GMAT 把 `Spacecraft` 轨道颜色设为红色：

```
Create Spacecraft aSat
aSat.CoordinateSystem = SunMJ2000Ec
aSat.DisplayStateType = Keplerian
aSat.SMA = 150000000

Create Barycenter EarthMoonBarycenter
EarthMoonBarycenter.OrbitColor = Cyan
EarthMoonBarycenter.BodyNames = {Earth, Luna}

Create CoordinateSystem SunMJ2000Ec
SunMJ2000Ec.Origin = Sun
SunMJ2000Ec.Axes = MJ2000Ec

Create ForceModel aFM
aFM.CentralBody = Sun
aFM.PointMasses = {Sun}

Create Propagator aProp
aProp.FM = aFM

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, EarthMoonBarycenter}
anOrbitView.CoordinateSystem = SunMJ2000Ec
anOrbitView.ViewPointReference = Sun
anOrbitView.ViewPointVector = [0 0 150000000]
anOrbitView.ViewDirection = Sun
anOrbitView.ViewScaleFactor = 4
anOrbitView.ViewUpCoordinateSystem = SunMJ2000Ec

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 75}
EarthMoonBarycenter.OrbitColor = [255 255 0]  % RGB value for Yellow
Propagate aProp(aSat) {aSat.ElapsedDays = 75}
EarthMoonBarycenter.OrbitColor = Orange
Propagate aProp(aSat) {aSat.ElapsedDays = 75}
EarthMoonBarycenter.OrbitColor = [250 128 114]   % RGB value for Salmon
Propagate aProp(aSat) {aSat.ElapsedDays = 75}
```

说明：创建由地球和月球组成的地月质心，初始轨道颜色为青色；任务序列中每传播 75 天修改一次颜色（青→黄→橙→鲑鱼粉）。

通过 `Propagate` 命令的 `OrbitColor` 选项为航天器的各个轨迹段设置独特颜色。颜色通过 ColorName 和 RGB 输入方法的组合设置。注意，尽管默认情况下 `aSat.OrbitColor` 字段设置为红色，但由于所有 `Propagate` 命令都重置了轨道颜色，因此红色从未被绘制：

```
Create Spacecraft aSat
aSat.OrbitColor = Red
aSat.X = 10000

Create Propagator aProp

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedSecs = 1000, OrbitColor = Yellow}
Propagate aProp(aSat) {aSat.ElapsedSecs = 1000, OrbitColor = Cyan}
Propagate aProp(aSat) {aSat.ElapsedSecs = 1000, OrbitColor = [154 205 50]}
Propagate aProp(aSat) {aSat.ElapsedSecs = 1000, OrbitColor = [255 0 255]}
```

说明：四条 Propagate 命令各自用 OrbitColor 选项覆盖颜色——黄（颜色名）、青（颜色名）、黄绿（RGB）、品红（RGB），因此默认的红色不会出现。

通过 `Propagate` 命令的 `OrbitColor` 选项为航天器的各个轨迹段设置颜色。这次颜色仅通过 ColorName 输入法设置。`aSat.OrbitColor` 字段上设置的默认颜色为红色。注意轨道颜色只在前三条 `Propagate` 命令上被重置。然而由于最后一条 `Propagate` 命令没有使用 `OrbitColor` 选项，因此最后一条 `Propagate` 命令绘制的轨迹为红色，即 `aSat.OrbitColor` 字段上指定的颜色：

```
Create Spacecraft aSat
aSat.OrbitColor = Red
aSat.X = 10000

Create Propagator aProp

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedSecs = 1000, OrbitColor = Orange}
Propagate aProp(aSat) {aSat.ElapsedSecs = 1000, OrbitColor = Blue}
Propagate aProp(aSat) {aSat.ElapsedSecs = 1000, OrbitColor = Yellow}
Propagate aProp(aSat) {aSat.ElapsedSecs = 1000}
```

说明：前三段轨迹分别为橙、蓝、黄；最后一段未指定 OrbitColor，回退到 aSat.OrbitColor 的红色。

在与 `Target` 资源配合使用及差分校正迭代过程中，为 `Propagate` 命令设置颜色。这次由于所有 `Propagate` 命令都设置了颜色，因此 `aSat.OrbitColor` 字段上设置的默认红色从未被绘制。还要注意，尽管 `aSat.TargetColor` 设置为黄色，但由于 `anOrbitView.SolverIterations` 设置为 None，迭代过程中绘制的摄动轨迹不会被画出，只绘制最终解：

```
Create Spacecraft aSat
aSat.OrbitColor = Red       
aSat.TargetColor = Yellow  

Create Propagator aProp

Create ImpulsiveBurn TOI

Create DifferentialCorrector aDC

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}
anOrbitView.SolverIterations = None %Set to 'All' to see perturbations
anOrbitView.ViewScaleFactor = 2


BeginMissionSequence

Propagate aProp(aSat) {aSat.Earth.Periapsis, OrbitColor = Salmon}

Target aDC;
Vary aDC(TOI.Element1 = 0.24, {Perturbation = 0.001, Lower = 0.0, ...
 Upper = 3.14159, MaxStep = 0.5})
 Maneuver TOI(aSat);
 Propagate aProp(aSat) {aSat.Earth.Apoapsis, OrbitColor = Blue}
 Achieve aDC(aSat.Earth.RMAG = 20000)
EndTarget

Propagate aProp(aSat) {aSat.Earth.Periapsis, OrbitColor = Orange}
```

说明：三段 Propagate 分别用 OrbitColor 指定鲑鱼粉、蓝、橙；Target 差分校正循环调整机动使远地点半径达 20000 km。因 SolverIterations=None，黄色的摄动轨迹（TargetColor）不显示；改为 'All' 即可看到迭代过程轨迹。
