# Propagate 命令（Propagate）
> 译自 GMAT R2026a 帮助文档 Propagate.html

Propagate —— 将航天器传播到请求的停止条件。

## 脚本语法

Propagate 命令是一个复杂的命令，支持多个传播器、多个航天器和多个停止条件。在下面的语法定义中，`SatList` 是以逗号分隔的航天器列表，`StopList` 是以逗号分隔的停止条件列表。Propagate 命令的一般语法为：

```
Propagate [Mode] [BackProp] Propagator1Name(SatList1,{StopList1})...
                 Propagator2Name(SatList2,{StopList2}

or

Propagate [Mode] [BackProp] Propagator1Name(SatList1)...
                 Propagator2Name(SatList2){StopList}
```

大多数应用是将单个航天器向前传播到单个停止条件。在这种情况下，语法简化为：

```
Propagate PropagatorName(SatName,{StopCond});

or

Propagate PropagatorName(SatName){StopCond};
```

在 GMAT 中，对于向前传播到单个停止条件的单个航天器，在 Propagate 命令上设置轨道颜色的语法可以通过 ColorName 指定轨道颜色，也可以通过 RGB 三元组值指定：

```
Propagate PropagatorName(SatName),{StopCond, OrbitColor = ColorName};

or

Propagate PropagatorName(SatName),{StopCond, OrbitColor = [RGB triplet value]};
```

## 描述

Propagate 命令控制航天器随时间的演化。GMAT 允许你在单个 Propagate 命令中传播单个航天器、多个非协作航天器以及编队（Formation）。Propagate 命令很复杂，控制航天器时间建模的以下方面：

- 要传播的航天器
- 用于传播的模型（数值积分、星历插值）
- 传播终止时要满足的条件
- 传播方向（时间上向前或向后）
- 多个航天器的时间同步
- STM 的传播和状态雅可比矩阵（A 矩阵）的计算
- 通过 Propagate 命令为不同航天器轨迹段设置独特的颜色

**另请参阅**：[Propagator](Propagator.md)、[Spacecraft](Spacecraft.md)、[Formation](Formation.md)、[Color](Color.md)

## 选项

### Mode
可选标志，用于在单个 Propagate 命令中对由多个传播器执行的航天器传播进行时间同步。更多细节请参见“备注”一节。

| 项目 | 内容 |
|------|------|
| 接受的数据类型 | String |
| 允许的值 | Synchronized |
| 默认值 | 未使用 |
| 是否必需 | 否 |
| 接口 | GUI、脚本 |

### BackProp
可选标志，用于将 Propagate 命令中的所有航天器沿时间向后传播。

| 项目 | 内容 |
|------|------|
| 接受的数据类型 | String |
| 允许的值 | BackProp |
| 默认值 | 未使用 |
| 是否必需 | 否 |
| 接口 | GUI、脚本 |

### StopList
以逗号分隔的停止条件列表。停止条件必须是 SatList 中被传播航天器的参数。更多细节请参见“备注”一节。

| 项目 | 内容 |
|------|------|
| 接受的数据类型 | Reference array（引用数组） |
| 允许的值 | 有效的停止条件列表 |
| 默认值 | ElapsedSecs = 12000 |
| 是否必需 | 否 |
| 接口 | GUI、脚本 |

### SatList
以逗号分隔的航天器列表。对于 SPK 类型的传播器，必须为航天器配置有效的 SPK 内核。

| 项目 | 内容 |
|------|------|
| 接受的数据类型 | Resource array（资源数组） |
| 允许的值 | 有效的航天器和/或编队列表 |
| 默认值 | DefaultSC |
| 是否必需 | 是 |
| 接口 | GUI、脚本 |

### PropagatorName
传播器名称。

| 项目 | 内容 |
|------|------|
| 接受的数据类型 | Propagator |
| 允许的值 | 有效的 Propagator 名称 |
| 默认值 | DefaultProp |
| 是否必需 | 是 |
| 接口 | GUI、脚本 |

### StopTolerance
停止条件根定位的容差。更多细节请参见“备注”一节。

| 项目 | 内容 |
|------|------|
| 接受的数据类型 | Real |
| 允许的值 | 实数 > 0 |
| 默认值 | 0.0000001 |
| 是否必需 | 否 |
| 接口 | GUI、脚本 |

### STM
可选标志，用于传播轨道 STM。STM 传播仅对数值积分器类型的传播器发生。

| 项目 | 内容 |
|------|------|
| 接受的数据类型 | String |
| 允许的值 | STM |
| 默认值 | 未使用 |
| 是否必需 | 否 |
| 接口 | GUI、脚本 |

### AMatrix
轨道加速度的雅可比矩阵，即一阶加速度矢量对状态矢量的偏导数。

| 项目 | 内容 |
|------|------|
| 接受的数据类型 | String |
| 允许的值 | AMatrix |
| 默认值 | 未使用 |
| 是否必需 | 否 |
| 接口 | GUI、脚本 |

### Covariance
可选标志，用于传播轨道协方差。协方差传播仅对数值积分器类型的传播器发生。选择此选项还会同时传播 STM。

| 项目 | 内容 |
|------|------|
| 接受的数据类型 | String |
| 允许的值 | Covariance |
| 默认值 | 未使用 |
| 是否必需 | 否 |
| 接口 | 脚本 |

### OrbitColor
在 Propagate 命令上设置轨道颜色。Propagate 段的默认颜色取自 `Spacecraft.OrbitColor` 字段上设置的颜色。要在脚本模式下为 Propagate 命令设置独特的颜色：输入你所选颜色的 ColorName 或 RGB 三元组值。在 GUI 模式下，通过点击 Orbit Color 选择框在 Propagate 命令上选择你所选的独特颜色。例如：在脚本模式下将 Propagate 段设置为黄色，可以用以下两种方式之一：`Propagate DefaultProp(DefaultSC) {DefaultSC.Earth.Apoapsis, OrbitColor = Yellow}` 或 `Propagate DefaultProp(DefaultSC) {DefaultSC.Earth.Apoapsis, OrbitColor = [255 255 0]}`。

| 项目 | 内容 |
|------|------|
| 接受的数据类型 | Integer Array 或 String |
| 允许的值 | GUI 中 Orbit Color Picker 可用的任何颜色。有效的预定义颜色名称或 0 到 255 之间的 RGB 三元组值 |
| 默认值 | Propagate 命令的默认颜色是最先在 `Spacecraft.OrbitColor` 字段上设置的颜色。`Spacecraft.OrbitColor` 的默认颜色为红色。因此 Propagate 命令的默认颜色为红色 |
| 是否必需 | 否 |
| 接口 | GUI、脚本 |

## GUI

### 简介

Propagate 命令的 GUI 提供了一个接口，用于将航天器分配给用于传播的传播器，并定义一组终止传播的条件。GUI 还允许你定义传播方向、多航天器的同步模式，以及是否传播 STM 和计算 A 矩阵。

要跟随下面的示例，你可以加载以下脚本片段，或创建一个包含三个航天器（名为 sat1、sat2 和 sat3）和两个传播器（名为 prop1 和 prop2）的新任务。

```
Create Spacecraft sat1 sat2 sat3
Create Propagator prop1 prop2
BeginMissionSequence
```

### 定义航天器和传播器

为演示如何定义一组用于传播的传播器和航天器，你将设置一个 Propagate 命令：使用名为 prop1 的传播器传播名为 sat1 的航天器，并使用名为 prop2 的传播器传播名为 sat2 和 sat3 的航天器。你将把该命令配置为传播 1 天，或直到 sat2 到达近拱点，以先到者为准。你需要按照“简介”一节所述配置 GMAT，并向你的任务序列添加一个新的 Propagate 命令。当你添加新的 Propagate 命令时，GMAT 会自动用 GUI 列表中的第一个传播器和第一个航天器填充 Propagate 命令 GUI，因此你应从这一点开始。

> [图：Propagate 命令 GUI 初始界面，已自动填充第一个传播器和航天器]

要添加第二个传播器以使用 prop2 传播 sat2 和 sat3：

1. 在 Propagator 列表中，点击第二行的省略号按钮，打开 Propagator Select 对话框。

> [图：Propagator Select 对话框]

2. 在 Available Propagators 列表中，点击 prop2，然后点击 OK。
3. 在 Spacecraft List 中，点击第二行的省略号按钮，打开 Space Object Select 对话框。
4. 点击右箭头两次，将 sat2 和 sat3 添加到所选航天器列表中，然后点击 Ok。

> [图：配置好两个传播器及各自航天器后的 Propagate 命令 GUI]

### 停止条件

继续上面的示例，现在你将配置 GMAT 传播一个完整历元日，或直到 sat2 到达近拱点。

1. 在 Parameter 列表中，点击第一行的省略号按钮，调出 Parameter Select 对话框。
2. 在 ObjectProperties 列表中，双击 ElapsedDays，然后点击 OK。

> [图：Parameter Select 对话框，选择 ElapsedDays]

3. 在 Condition 列表中，双击包含 12000 的第一行，输入 1，然后点击 OK。
4. 在 Parameter 列表中，点击第二行的省略号按钮，调出 Parameter Select 对话框。
5. 在 Object 列表中，点击 Sat2。
6. 在 ObjectProperties 列表中，双击 Periapsis，然后点击 OK。

Propagate1 对话框现在应如下图所示。

> [图：配置好停止条件后的 Propagate1 对话框]

## 备注

### 简介

下面的 Propagate 命令文档介绍了如何将单个和多个航天器沿时间向前和向后传播到所需条件。为精简脚本示例，假定对象 `numSat`、`spkSat`、`numProp` 和 `spkProp` 已按如下所示配置。GMAT 随附了示例中使用的 SPK 内核。

```
Create Spacecraft spkSat;
spkSat.Epoch.UTCGregorian   = '02 Jun 2004 12:00:00.000'
spkSat.NAIFId               = -123456789;
spkSat.OrbitSpiceKernelName = {'..\data\vehicle\ephem\spk\GEOSat.bsp'};

Create Spacecraft numSat
numSat.Epoch.UTCGregorian = '02 Jun 2004 12:00:00.000'

Create Propagator spkProp;
spkProp.Type       = SPK;
spkProp.StartEpoch = FromSpacecraft

Create Propagator numProp
numProp.Type = PrinceDormand78

BeginMissionSequence
```

**中文说明**：上述脚本配置了示例所用的对象：`spkSat` 是使用 SPK 内核 `GEOSat.bsp` 的航天器；`numSat` 是数值积分航天器；`spkProp` 是 SPK 类型传播器；`numProp` 是 PrinceDormand78 数值积分传播器。

### 如何传播单个航天器

注意：有关配置 GMAT 以执行本节示例的脚本片段，请参见“简介”一节。

Propagate 命令提供了一个简单的接口，用于将航天器传播到停止条件，或执行单个传播步。要传播单个航天器，你必须指定所需的传播器、要传播的航天器，以及（如果需要）停止条件。Propagate 命令支持数值积分器和星历类型的传播器。对于单航天器传播，无论传播器类型如何，语法都是相同的。例如，要使用数值积分器传播航天器，可以使用以下脚本片段：

```
Propagate numProp(numSat){numSat.Periapsis}
% or
Propagate numProp(numSat,{numSat.Periapsis})
```

要使用配置为 SPK 内核的传播器传播单个航天器，使用以下语句：

```
Propagate spkProp(spkSat){spkSat.TA = 90}
% or
Propagate spkProp(spkSat,{spkSat.TA = 90})
```

要执行单个传播步，只需省略停止条件，如下所示。传播器将根据其步长控制算法迈出一步。有关步长控制的更多信息，请参见 [Propagator](Propagator.md) 文档。

```
Propagate numProp(numSat)
% or
Propagate spkProp(spkSat) 
```

### 如何传播多个航天器

Propagate 命令允许你通过以下方式传播多个航天器：在单个传播器中包含航天器列表、在传播器中包含编队（Formation），和/或在单个命令中包含多个传播器。作为示例，下面是一个传播多个航天器的脚本片段。

```
Propagate Synchronized Prop1(Sat1,Sat2) Prop2(Sat3,Sat4)...
Prop3(aFormation){Sat1.Earth.Periapsis}
```

在上面的脚本行中，Sat1 和 Sat2 使用 Prop1 传播；Prop2 用于传播 Sat3 和 Sat4；添加到 aFormation 的所有航天器使用 Prop3 传播。上面配置的 Propagate 命令传播所有航天器，直到 Sat1 到达地球近拱点。

由同一传播器传播的所有航天器在传播过程中是时间同步的。所谓时间同步，是指所有航天器跨越相同的时间步长进行传播。`Synchronized` 关键字告诉 GMAT 在传播过程中使由不同传播器传播的航天器在时间上保持同步。多个传播器之间的时间同步是这样实现的：先为第一个传播器（上例中的 Prop1）控制的所有航天器迈出一步，然后让所有其他传播器步进到该时刻。当省略 `Synchronized` 关键字时，由不同传播器传播的航天器在时间上不同步。在这种情况下，每个传播器按照其步长控制算法决定的步长迈步，而不考虑 Propagate 命令中的其他传播器。如果你需要为多个航天器生成时间标签一致的星历文件，或者在 OrbitView 中可视化多个航天器，时间同步尤其有用。

> **警告**：当使用配置为 SPK 内核的传播器时，每个传播器只能有一个航天器。
>
> 这是支持的：`Propagate numProp(numSat) spkProp(spkSat1) spkProp(spkSat2)`
>
> 这是**不**支持的！`Propagate numProp(numSat) spkProp(spkSat1,spkSat2)`

### 停止条件的行为

GMAT 允许你在传播航天器时定义一组停止条件，这些条件定义了在 Propagate 命令终止时必须满足的条件。例如，传播到某个轨道位置（如远地点）通常很有用。当未提供停止条件时，Propagate 命令只迈出一步。当给定一组停止条件时，Propagate 命令将航天器传播到在已流逝传播时间中最先发生的条件，并终止传播。通过脚本接口定义停止条件有多种方式。一种是在每个传播器中包含以逗号分隔的停止条件列表，像这样：

```
Propagate Prop1(Sat1,{Sat1.Periapsis}) Prop2(Sat2,{Sat2.Periapsis}) 
```

第二种方法是在 Propagate 命令的末尾定义以逗号分隔的停止条件列表，像这样：

```
Propagate Prop1(Sat1) Prop2(Sat2) {Sat1.Periapsis,Sat2.Periapsis}
```

请注意，上述两种方法产生相同的停止历元。当你提供一组停止条件时，无论停止条件在命令中的何处定义，GMAT 都会构建所有条件的列表，并跟踪它们直到第一个条件发生。

Propagate 命令目前要求停止条件的左侧是有效的航天器参数。例如，下面示例中的第一行是支持的，第二行则不支持。

```
Propagate Prop1(Sat1) {Sat1.TA = 45}  % Supported
Propagate Prop1(Sat1) {45 = Sat1.TA}  % Not supported 
```

GMAT 支持用于远拱点和近拱点的特殊内置停止条件，像这样：

```
Propagate Prop1(Sat1) {Sat1.Apoapsis}
Propagate Prop1(Sat1) {Sat1.Mars.Periapsis} 
```

你可以通过在 Propagate 命令中包含 `StopTolerance` 关键字来定义停止条件的容差，如下所示。在此示例中，GMAT 将传播到 Sat1 的真近点角为 90 度，误差在 +/- 1e-5 度以内。

```
Propagate Prop1(Sat1) {Sat1.TA = 90, StopTolerance = 1e-5}
```

> **警告**：GMAT 目前将航天器传播到几微秒的时间量化精度。根据停止条件函数的变化率，可能无法将停止条件定位到所请求的 `StopTolerance`。在这种情况下，GMAT 会抛出警告，提醒你容差未满足，并提供有关实际达到的停止值和所请求容差的信息。
>
> 注意：GMAT 目前不支持按每个停止条件单独设置容差。如果你在单个 Propagate 命令中多次包含 `StopTolerance`，GMAT 将使用最后提供的值。

Propagate 命令在连续发生两次传播、且两次传播至少有一个在两个命令中相同的停止条件时，使用一种称为首步算法（First Step Algorithm，FSA）的算法。例如：

```
Propagate prop1(Sat1) {Sat1.TA = 90}
Propagate prop1(Sat1) {Sat1.TA = 90, StopTolerance = 1e-4}
```

当对航天器执行的上一次传播是使用当前命令中列出的停止条件终止时，FSA 决定首步的行为。如果在第二个 Propagate 命令的初始历元处停止条件的误差小于 SafetyFactor*`StopTolerance`，则 Propagate 命令会先迈出一个积分步，然后再尝试重新定位停止条件。在 FSA 中，SafetyFactor = 10，`StopTolerance` 来自第二个 Propagate 命令。继续上面的示例，如果 abs(TA_Achieved - TA_Desired) < 1e-3——其中 TA_Achieved 是第一个 Propagate 命令之后的 TA，TA_Desired 是第二个 Propagate 命令中请求的 TA 值——那么 Propagate 命令将先迈出一步，然后再尝试定位停止条件。首步算法对向前传播、向后传播以及改变传播方向的工作方式相同。

> **警告**：有可能指定一个停止条件根定位器无法满足的 `StopTolerance`，在这种情况下会抛出警告。然而，后续使用相同停止条件的 Propagate 命令可能无法按预期工作。要使 FSA 算法按设计工作，你必须提供可实现的 `StopTolerance` 值。

### 如何向后传播

要使用脚本接口向后传播，请在 Propagate 命令和命令中的第一个传播器之间包含关键字 `BackProp`，如下所示。命令中的所有传播器都将向后传播。

```
Propagate Synchronized BackProp Prop1(Sat1,Sat2) Prop2(Sat3,Sat4)...
           Prop3(aFormation){Sat1.Earth.Periapsis}

Propagate Backprop numProp(numSat){numSat.Periapsis}
```

### 如何传播 STM、协方差并计算雅可比矩阵（A 矩阵）

通过在 Propagate 命令中包含 `STM` 和 `Covariance` 关键字（如下所示），GMAT 为所有使用数值积分器传播的航天器传播 STM 和协方差。如果在 Propagate 命令的任何位置包含 `STM` 或 `Covariance` 关键字，则所有使用数值传播器的航天器都会传播 STM 和协方差。当传播多个分配了 ProcessNoiseModels 的航天器时，每个 ProcessNoiseModel 必须具有相同的 `UpdateTimeStep` 参数值。

```
Propagate Backprop numProp(numSat, 'STM', 'Covariance') {numSat.Periapsis}
```

当传播编队（Formation）资源或使用星历类型传播器时，GMAT 目前不支持传播 STM 或协方差。

### 协方差传播的特殊注意事项

协方差使用与扩展卡尔曼滤波器资源中采用的线性化模型相同的模型进行传播。初始协方差在航天器的 `OrbitErrorCovariance` 参数上指定。如果没有为航天器对象分配过程噪声模型，则协方差传播步即为积分器步，且初始协方差的传播不包含过程噪声。要在协方差传播中包含过程噪声，请定义一个 `ProcessNoiseModel` 并将其赋到航天器的 `ProcessNoiseModel` 参数上。

当包含过程噪声时，协方差传播步同时取决于积分器步长和 `ProcessNoiseModel` 的 `UpdateTimeStep` 参数。如果 `UpdateTimeStep` 设为 0，协方差仅以积分步长传播。如果 `UpdateTimeStep` 非零，则各 `UpdateTimeStep` 构成积分器的一组停止点网格。状态和协方差的传播将使用积分器步长设置推进到每个 `UpdateTimeStep` 停止点。特别地，例如，如果 `UpdateTimeStep` 小于积分器步长，积分器将仅以 `UpdateTimeStep` 间隔迈步。如果 `UpdateTimeStep` 大于积分步长，积分器将以等于或小于积分器步长的步长步进到每个 `UpdateTimeStep` 停止点，具体取决于当前传播历元与下一个停止点之间的差值。

目前协方差传播尚未实现任何 consider 参数。GMAT 只传播 6x6 位置/速度协方差。目前仅当在使用 J2000Eq 轴的参考系中指定初始状态和初始 `OrbitErrorCovariance` 时，才允许进行协方差传播。

### Propagate 命令的限制

- 使用 SPK 类型传播器时，给定传播器只能传播单个航天器。
- 当传播编队（Formation）对象时，GMAT 目前不支持传播 STM。编队对象无法传播协方差。
- 在传播过程中计算 A 矩阵时，A 矩阵的值只能通过 C 接口访问。

### 在 Propagate 命令上设置颜色

GMAT 允许你通过在每个 Propagate 命令上设置轨道颜色，为航天器轨迹段分配独特的颜色。如果你不在每个 Propagate 命令上设置独特的颜色，则默认情况下，每个传播段的颜色取自 `Spacecraft.OrbitColor` 字段上设置的颜色。有关在 Propagate 命令上设置颜色的 `OrbitColor` 选项，请参见“选项”一节。另请参见 [Color](Color.md) 文档，了解如何通过 GMAT 的 Propagate 命令在轨道轨迹段上设置独特颜色的讨论和示例。

## 示例

将单个航天器传播到地球近拱点：

```
Create Spacecraft numSat
numSat.Epoch.UTCGregorian = '02 Jun 2004 12:00:00.000'

Create Propagator numProp
numProp.Type = PrinceDormand78

BeginMissionSequence

Propagate numProp(numSat) {numSat.Earth.Periapsis}
```

将单个航天器传播一天：

```
Create Spacecraft numSat
numSat.Epoch.UTCGregorian = '02 Jun 2004 12:00:00.000'

Create Propagator numProp
numProp.Type = PrinceDormand78

BeginMissionSequence

Propagate numProp(numSat) {numSat.ElapsedDays = 1}
```

将单个航天器向后传播到真近点角 90 度：

```
Create Spacecraft numSat
numSat.Epoch.UTCGregorian = '02 Jun 2004 12:00:00.000'

Create Propagator numProp
numProp.Type = PrinceDormand78

BeginMissionSequence

Propagate BackProp numProp(numSat) {numSat.TA = 90}
```

传播两个航天器，每个使用不同的传播器，但保持航天器在时间上同步。传播直到任一航天器到达平近点角 45 度：

```
Create Spacecraft aSat1 aSat2
aSat1.Epoch.UTCGregorian = '02 Jun 2004 12:00:00.000'
aSat2.Epoch.UTCGregorian = '02 Jun 2004 12:00:00.000'
aSat2.TA = 0;

Create Propagator aProp1
aProp1.Type = PrinceDormand78
Create Propagator aProp2
aProp2.Type = PrinceDormand78

BeginMissionSequence

Propagate Synchronized aProp1(aSat1) aProp2(aSat2) ...
                      {aSat1.MA = 45,aSat2.MA = 45} 
```