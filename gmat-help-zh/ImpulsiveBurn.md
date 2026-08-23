# 脉冲机动（ImpulsiveBurn）

> 译自 GMAT R2026a 帮助文档 ImpulsiveBurn.html

**ImpulsiveBurn** —— 脉冲式机动。

## 描述

`ImpulsiveBurn` 资源允许航天器施加一个瞬时的速度增量 Delta-V（ΔV），而非像有限推力机动那样非瞬时作用。它通过指定 Delta-V 的三个矢量分量来定义。你可以通过定义坐标系和矢量分量值来配置该机动。对于 `Local`（局部）坐标系，用户可以选择 `Origin`（原点）和 `Axes`（坐标轴）类型。根据任务的不同，使用某一种坐标系可能比另一种更简单。

另请参阅：Maneuver（机动）、ChemicalTank（化学推进剂箱）、BeginFiniteBurn（开始有限推力机动）。

## 字段

| 字段 | 描述 |
|------|------|
| **Axes** | 允许你为脉冲机动定义一组以航天器为中心的坐标轴。该字段不能在任务序列（Mission Sequence）中修改。<br>• 数据类型：String<br>• 允许值：`VNB`、`LVLH`、`MJ2000Eq`、`SpacecraftBody`<br>• 访问权限：set<br>• 默认值：`VNB`<br>• 单位：N/A<br>• 接口：GUI、脚本 |
| **B** | 已废弃。所施加脉冲机动（Delta-V）的 Z 分量。<br>• 数据类型：Real<br>• 允许值：Real<br>• 访问权限：set、get<br>• 默认值：0<br>• 单位：km/s<br>• 接口：GUI、脚本 |
| **CoordinateSystem** | 确定方向参数 `Element1`、`Element2` 和 `Element3` 所参照的坐标系。该字段不能在任务序列中修改。<br>• 数据类型：Reference Array<br>• 允许值：`Local`、`EarthMJ2000Eq`、`EarthMJ2000Ec`、`EarthFixed`，或任何用户自定义坐标系<br>• 访问权限：set<br>• 默认值：`Local`<br>• 单位：N/A<br>• 接口：GUI、脚本 |
| **DecrementMass** | 标志位，决定 `FuelMass`（燃料质量）是否随使用而消耗扣减。该字段不能在任务序列中修改。<br>• 数据类型：String<br>• 允许值：true、false<br>• 访问权限：set<br>• 默认值：`false`<br>• 单位：N/A<br>• 接口：GUI、脚本 |
| **Element1** | 所施加脉冲机动（Delta-V）的 X 分量。<br>• 数据类型：Real<br>• 允许值：Real<br>• 访问权限：set、get<br>• 默认值：0<br>• 单位：km/s<br>• 接口：GUI、脚本 |
| **Element2** | 所施加脉冲机动（Delta-V）的 Y 分量。<br>• 数据类型：Real<br>• 允许值：Real<br>• 访问权限：set、get<br>• 默认值：0<br>• 单位：km/s<br>• 接口：GUI、脚本 |
| **Element3** | 所施加脉冲机动（Delta-V）的 Z 分量。<br>• 数据类型：Real<br>• 允许值：Real<br>• 访问权限：set、get<br>• 默认值：0<br>• 单位：km/s<br>• 接口：GUI、脚本 |
| **GravitationalAccel** | 用于计算燃料消耗的重力加速度值。<br>• 数据类型：Real<br>• 允许值：Real > `0`<br>• 访问权限：set、get<br>• 默认值：9.81<br>• 单位：m/s^2<br>• 接口：GUI、脚本 |
| **Isp** | 燃料的比冲值。<br>• 数据类型：Real<br>• 允许值：Real<br>• 访问权限：set、get<br>• 默认值：300<br>• 单位：s<br>• 接口：GUI、脚本 |
| **N** | 已废弃。所施加脉冲机动（Delta-V）的 Y 分量。<br>• 数据类型：Real<br>• 允许值：Real<br>• 访问权限：set、get<br>• 默认值：0<br>• 单位：km/s<br>• 接口：GUI、脚本 |
| **Origin** | `Origin` 字段与 `Axes` 字段配合使用，允许用户为脉冲机动定义一组以航天器为中心的坐标轴。该字段不能在任务序列中修改。<br>• 数据类型：Reference Array<br>• 允许值：`Sun`、`Mercury`、`Venus`、`Earth`、`Luna`、`Mars`、`Jupiter`、`Saturn`、`Uranus`、`Neptune`、`Pluto`<br>• 访问权限：set<br>• 默认值：`Earth`<br>• 单位：N/A<br>• 接口：GUI、脚本 |
| **Tank** | `ChemicalThruster`（化学推力器）从中抽取推进剂的 `ChemicalTank`（化学推进剂箱）。该字段不能在任务序列中修改。<br>• 数据类型：Reference Array<br>• 允许值：用户定义的 `ChemicalTank` 列表<br>• 访问权限：set<br>• 默认值：N/A<br>• 单位：N/A<br>• 接口：GUI、脚本 |
| **V** | 已废弃。所施加脉冲机动（Delta-V）的 X 分量。<br>• 数据类型：Real<br>• 允许值：Real<br>• 访问权限：set、get<br>• 默认值：0<br>• 单位：km/s<br>• 接口：GUI、脚本 |
| **VectorFormat** | 已废弃。允许你定义 `ImpulsiveBurn Delta-V Vector` 的格式。该字段无效。`ImpulsiveBurn Delta-V Vector` 始终以 `Cartesian`（笛卡尔）格式给出。<br>• 数据类型：Enumeration<br>• 允许值：`Cartesian`、`Spherical`<br>• 访问权限：set<br>• 默认值：`Cartesian`<br>• 单位：N/A<br>• 接口：脚本 |

## GUI

`ImpulsiveBurn` 对话框允许你指定脉冲机动的属性，包括 Delta-V 分量值以及坐标系（Coordinate System）的选择。如果你选择对与脉冲机动相关的燃料损耗进行建模，则必须指定燃料箱，以及用于计算燃料消耗的比冲（ISP）值和重力加速度。`ImpulsiveBurn` 对话框的布局如下图所示。

> [图：ImpulsiveBurn 对话框界面]

`Origin` 和 `Axes` 字段仅在坐标系设置为 Local 时才有效。有关局部坐标系的更多细节，请参阅"备注"部分。

如果勾选了 `Decrement Mass`（质量消耗），则可以选择所需的 `ChemicalTank` 作为质量消耗的燃料供应来源。

## 备注

### 局部坐标系

这里的局部坐标系（Local Coordinate System）是指使用 `ImpulsiveBurn` 资源接口在"局部"配置的坐标系，而不是通过资源树（Resources Tree）中的 `Coordinate Systems` 文件夹定义的坐标系。

要配置局部坐标系，必须指定输入 Delta-V 矢量 `Element1-3` 的坐标系。如果选择局部坐标系，`Axes` 子字段提供的四个选项为 `VNB`、`LVLH`、`MJ2000Eq` 和 `SpacecraftBody`。`VNB`（Velocity-Normal-Binormal，速度-法向-副法向）是一种非惯性坐标系，基于航天器相对于 `Origin` 子字段所指定天体的运动。例如，如果 `Origin` 选择为 Earth，则该坐标系的 X 轴沿航天器相对于地球的速度方向，Y 轴沿航天器（相对于地球的）瞬时轨道法线方向，Z 轴在保持与其他两轴正交的前提下尽可能指向远离地球的方向，从而构成右手坐标系。

类似地，LVLH（Local Vertical Local Horizontal，当地垂线当地水平）也是一种非惯性坐标系，基于航天器相对于 Origin 子字段所指定天体的运动。如果选择地球为原点，则该坐标系的 X 轴从地心指向航天器，Z 轴沿航天器（相对于地球的）瞬时轨道法线方向，Y 轴构成右手坐标系。对于典型的束缚轨道，Y 轴近似与速度矢量对齐。在完美圆轨道的情况下，Y 轴恰好沿速度矢量方向。

`MJ2000Eq` 是基于 J2000 的地心地球平赤道惯性坐标系。注意，定义该坐标系不需要 `Origin` 子字段。

`SpacecraftBody` 是航天器使用的坐标系。由于推力在该坐标系中施加，GMAT 使用航天器的姿态（航天器的一个属性）来确定惯性系中的推力方向。注意，定义该坐标系不需要 `Origin` 子字段。

### ImpulsiveBurn 的已废弃字段名

注意，指定 ImpulsiveBurn 分量的标准方法（如下所示）是使用 `Element1`、`Element2` 和 `Element3` 字段名。

```
Create ImpulsiveBurn DefaultIB
DefaultIB.Element1 = -3
DefaultIB.Element2 = 7
DefaultIB.Element3 = -2
```

在当前版本的 GMAT 中，你也可以分别使用字段名 `V`、`N` 和 `B` 来代替 `Element1`、`Element2` 和 `Element3`。下面的命令与上面的命令等效。

```
Create ImpulsiveBurn DefaultIB
DefaultIB.V = -3
DefaultIB.N = 7
DefaultIB.B = -2
```

需要特别注意，`V`、`N`、`B` 字段名并不一定对应某个速度-法向-副法向（Velocity, Normal, Binormal）坐标系。任何 `ImpulsiveBurn` 的坐标系始终由 `CoordinateSystem`、`Origin` 和 `Axes` 字段指定。由于 `V`、`N`、`B` 字段名可能引起的混淆，未来版本的 GMAT 将不再允许使用它们。如果你在当前版本的 GMAT 中使用 `V`、`N`、`B` 字段名，将会收到一条警告消息。

### 使用航天器速度定义的、向后传播的脉冲机动

使用航天器速度定义的坐标轴的例子包括上面讨论的 `VNB` 和 `LVLH` 坐标轴，以及一些用户自定义的坐标轴。在向后传播（backwards-propagation）过程中使用这类坐标轴施加脉冲机动时的行为较为微妙，需要加以说明。在下面的示例中，我们将集中讨论 `VNB` 机动。

如下面的脚本示例所示，在向后传播期间施加脉冲机动需使用 'BackProp' 关键字。你为向后传播指定的机动分量会被用来计算实际施加的机动分量。参考下面的脚本示例：先施加一个向后传播的脉冲机动，然后以正常的前向传播方式施加同一机动。该脉冲机动的定义使得脚本运行后航天器的速度保持不变。

```
Create Spacecraft Sat;
Create ImpulsiveBurn myImpulsiveBurn;
myImpulsiveBurn.CoordinateSystem = Local;
myImpulsiveBurn.Origin           = Earth;
myImpulsiveBurn.Axes             = VNB;
myImpulsiveBurn.Element1         = 3.1
myImpulsiveBurn.Element2         = -0.1
myImpulsiveBurn.Element3         = 0.2

BeginMissionSequence
Maneuver BackProp myImpulsiveBurn(Sat);
Maneuver myImpulsiveBurn(Sat);
```

为了计算实际施加的机动分量，GMAT 在内部使用迭代计算方法。该迭代方法最适用于机动量值不占航天器总体速度显著比例的情况。此外，对于 `VNB` 机动，当 'N' 和 'B' 分量量值相对于 'V' 分量量值较小时，迭代方法效果最佳。如果 GMAT 内部迭代方法未能收敛，将生成一条警告消息。目前，用户没有简便的方法输出实际施加的向后传播机动分量。（机动报告输出的是用户提供的 `VNB` 坐标。）然而，在向后传播机动施加之后，我们确实知道机动的分量是什么。如果 `VNB` 机动的用户提供分量为 (Vx, Vy, Vz)，那么在向后传播机动施加之后，该机动的 `VNB` 分量为 (-Vx, -Vy, -Vz)。

考虑下面的脚本示例，其中机动的 'N' 和 'B' 分量为零，'V' 分量为 +5 km/s。如果航天器速度在 J2000 惯性坐标系中为 (7,0,0) km/s，那么在向后传播的脉冲机动之后，航天器的速度将为 (2,0,0) km/s。

```
Create Spacecraft Sat;
Create ImpulsiveBurn myImpulsiveBurn;
myImpulsiveBurn.CoordinateSystem = Local;
myImpulsiveBurn.Origin           = Earth;
myImpulsiveBurn.Axes             = VNB;

myImpulsiveBurn.Element1 = 5
myImpulsiveBurn.Element2 = 0.0
myImpulsiveBurn.Element3 = 0.0

BeginMissionSequence
Maneuver BackProp myImpulsiveBurn(Sat);
```

最后，我们注意到，当为向后传播的脉冲机动建模质量变化时，质量会被添加到燃料箱中。这样做是为了使得"向后传播的脉冲机动后接同一机动的正常前向传播"时质量不发生变化。

### 交互关系

| 资源 | 描述 |
|------|------|
| `Spacecraft` 资源 | 必须创建航天器才能施加任何 `ImpulsiveBurn`。 |
| `ChemicalTank` 资源 | 如果要为 `ImpulsiveBurn` 建模质量消耗，请将 `ChemicalTank` 挂载到被机动的 `Spacecraft` 上，作为燃料质量来源。 |
| `Maneuver` 命令 | 必须使用 `Maneuver` 命令将 `ImpulsiveBurn` 施加到 `Spacecraft` 上。 |
| `Vary` 命令 | 如果希望允许 `ImpulsiveBurn` 的分量变化以达成某个目标，则必须使用 `Vary` 命令，作为 `Target` 或 `Optimize` 命令序列的一部分。 |

## 示例

创建一个默认的 `ChemicalTank` 和一个允许燃料消耗的 `ImpulsiveBurn`，将该默认 `ChemicalTank` 指派给 `ImpulsiveBurn`，把 `ChemicalTank` 挂载到 `Spacecraft` 上，并将 `ImpulsiveBurn` 施加到该 `Spacecraft`。

```
%  Create the ChemicalTank Resource
Create ChemicalTank FuelTank1
FuelTank1.AllowNegativeFuelMass = false
FuelTank1.FuelMass = 756
FuelTank1.Pressure = 1500
FuelTank1.Temperature = 20
FuelTank1.RefTemperature = 20
FuelTank1.Volume = 0.75
FuelTank1.FuelDensity = 1260
FuelTank1.PressureModel = PressureRegulated

Create ImpulsiveBurn DefaultIB
DefaultIB.CoordinateSystem = Local
DefaultIB.Origin = Earth
DefaultIB.Axes = VNB
DefaultIB.Element1 = 0.001
DefaultIB.Element2 = 0
DefaultIB.Element3 = 0
DefaultIB.DecrementMass = true
DefaultIB.Tank = {FuelTank1}
DefaultIB.Isp = 300
DefaultIB.GravitationalAccel = 9.810000000000001

%  Add the the ChemicalTank to a Spacecraft
Create Spacecraft DefaultSC
DefaultSC.Tanks = {FuelTank1}

BeginMissionSequence
Maneuver DefaultIB(DefaultSC)
```

上述脚本：先创建化学推进剂箱 FuelTank1 并设置其燃料质量、压力、温度等属性；然后创建脉冲机动 DefaultIB，采用局部 VNB 坐标系（原点为地球），X 分量 Delta-V 为 0.001 km/s，开启质量消耗并指定燃料箱、比冲与重力加速度；最后创建航天器 DefaultSC 并挂载燃料箱，在任务序列中用 Maneuver 命令施加该脉冲机动。
