# 机动（Maneuver）

> 译自 GMAT R2026a 帮助文档 Maneuver.html

**Maneuver** —— 执行脉冲（瞬时）机动。

## 脚本语法

```
Maneuver BurnName (SpacecraftName)
```

其中 `BurnName` 为脉冲机动对象名，`SpacecraftName` 为航天器名。

## 描述

`Maneuver` 命令将选定的 `ImpulsiveBurn`（脉冲机动）施加到选定的 `Spacecraft`（航天器）上。要使用 `Maneuver` 命令执行脉冲机动，必须创建一个 `ImpulsiveBurn`。如果希望建模燃料消耗，必须将特定的 `ChemicalTank` 硬件对象与该 `ImpulsiveBurn` 关联，并将该 `ChemicalTank` 挂载到所需的 `Spacecraft` 上。更多细节请参阅下面的"备注"和示例。

另请参阅：ChemicalTank（化学推进剂箱）、ImpulsiveBurn（脉冲机动）、Spacecraft（航天器）。

## 选项

| 选项 | 描述 |
|------|------|
| **ImpulsiveBurnName** | 允许用户选择施加哪个 `ImpulsiveBurn`。例如，要使用 DefaultIB 对 DefaultSC 进行机动，脚本行将写作 Maneuver DefaultIB(DefaultSC)。<br>• 接受的数据类型：Reference Array<br>• 允许值：资源树中存在的任何 `ImpulsiveBurn`<br>• 默认值：`DefaultIB`<br>• 是否必需：是<br>• 接口：GUI、脚本 |
| **SpacecraftName** | 允许用户选择对哪艘 `Spacecraft` 进行机动。所施加的机动由上面的 `ImpulsiveBurnName` 选项指定。<br>• 接受的数据类型：Reference Array<br>• 允许值：`Spacecraft` 资源<br>• 默认值：`DefaultSC`<br>• 是否必需：是<br>• 接口：GUI、脚本 |

## GUI

`Maneuver` 命令对话框（如下图所示）允许你选择应将哪个先前创建的 `ImpulsiveBurn` 施加到哪艘 `Spacecraft` 上。

> [图：Maneuver 命令对话框界面]

## 备注

### 燃料消耗

要建模与所选 `ImpulsiveBurn` 相关的燃料消耗，必须按如下方式配置 `ImpulsiveBurn` 对象：

- 将 `ImpulsiveBurn` 参数 `Decrement Mass`（质量消耗）设置为 true。
- 为 `ImpulsiveBurn` 对象选择一个 `ChemicalTank`，并将所选的 `ChemicalTank` 挂载到 `Spacecraft` 上。
- 为 `ImpulsiveBurn` 参数 `Isp`（比冲）和 `GravitationalAccel`（重力加速度）设置数值，它们用于通过火箭方程计算所消耗的质量。

### 交互关系

| 资源 | 描述 |
|------|------|
| `ImpulsiveBurn` | `Maneuver` 命令将指定的 `ImpulsiveBurn` 施加到指定的 Spacecraft 上。 |
| `ChemicalTank` | 由 `ImpulsiveBurn` 对象指定的 `ChemicalTank`（可选地）用于为 `ImpulsiveBurn` 提供燃料。 |
| `Spacecraft` | 这是 `ImpulsiveBurn` 所施加的对象。 |

## 示例

创建一个默认的 `Spacecraft` 和 `ChemicalTank`，并将 `ChemicalTank` 挂载到 `Spacecraft` 上。沿地球 VNB 坐标系的 V 方向执行 100 m/s 的脉冲机动。

```
%  Create default Spacecraft and ChemicalTank and attach the ChemicalTank 
%  to the Spacecraft.
Create Spacecraft DefaultSC
Create ChemicalTank FuelTank1
DefaultSC.Tanks = {FuelTank1}

%  Set ChemicalTank1 parameters to default values
FuelTank1.AllowNegativeFuelMass = false
FuelTank1.FuelMass = 756
FuelTank1.Pressure = 1500
FuelTank1.Temperature = 20
FuelTank1.RefTemperature = 20
FuelTank1.Volume = 0.75
FuelTank1.FuelDensity = 1260
FuelTank1.PressureModel = PressureRegulated

%  Create ImpulsiveBurn associated with the created ChemicalTank
Create ImpulsiveBurn IB
IB.CoordinateSystem = Local
IB.Origin = Earth
IB.Axes = VNB
IB.Element1 = 0.1
IB.Element2 = 0
IB.Element3 = 0
IB.DecrementMass = true
IB.Tank = {FuelTank1}
IB.Isp = 300
IB.GravitationalAccel = 9.810000000000001

BeginMissionSequence
%  Apply impulsive maneuver to DefaultSC
Maneuver IB(DefaultSC)
```

上述脚本：创建默认航天器 DefaultSC 和燃料箱 FuelTank1 并挂载；设置燃料箱的燃料质量、压力、温度等参数；创建脉冲机动 IB（局部 VNB 坐标系、原点为地球，X 分量 Delta-V 为 0.1 km/s，即 100 m/s，开启质量消耗并指定燃料箱、比冲与重力加速度）；在任务序列中用 Maneuver 命令将该脉冲机动施加到 DefaultSC。
