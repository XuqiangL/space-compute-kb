# 电推力器（ElectricThruster）
> 译自 GMAT R2026a 帮助文档 ElectricThruster.html

**ElectricThruster** —— 电推力器模型

## 描述

ElectricThruster 资源是电推力器的模型，支持多种推力和质量流量计算模型。ElectricThruster 模型还允许您指定工作占空比（Duty Cycle）和比例因子等属性，并将 ElectricThruster 与 ElectricTank 相关联。您可以通过在坐标系中指定推力分量来灵活定义推力方向，这些坐标系包括（局部定义的）SpacecraftBody 或 LVLH，也可以选择任何已配置的 CoordinateSystem 资源。

有关电推进建模所需全部资源的完整配置说明，请参阅教程"第 12 章 电推进（Electric Propulsion）"。

另请参阅：ElectricTank、NuclearPowerSystem、SolarPowerSystem

## 字段

| 字段 | 描述 |
|------|------|
| **Axes** | 允许用户为 ElectricThruster 定义一组以航天器为中心的坐标轴。此字段不能在任务序列中修改。<br>数据类型：Reference Array；允许值：VNB、LVLH、MJ2000Eq、SpacecraftBody；访问：set；默认值：VNB；单位：N/A；接口：GUI、脚本 |
| **ConstantThrust** | 当 ThrustModel 设为 ConstantThrustAndIsp 时使用的推力值。<br>数据类型：Real；允许值：Real > 0；访问：set、get；默认值：0.237；单位：N；接口：GUI、脚本 |
| **CoordinateSystem** | 确定方向参数 ThrustDirection1、ThrustDirection2 和 ThrustDirection3 所参照的坐标系。此字段不能在任务序列中修改。<br>数据类型：Reference Array；允许值：Local、EarthMJ2000Eq、EarthMJ2000Ec、EarthFixed 或任何用户自定义坐标系；访问：set；默认值：Local；单位：N/A；接口：GUI、脚本 |
| **DecrementMass** | 该标志决定 FuelMass 是否随使用而递减。此字段不能在任务序列中修改。<br>数据类型：Boolean；允许值：true、false；访问：set；默认值：false；单位：N/A；接口：GUI、脚本 |
| **DutyCycle** | 机动过程中推力器开机时间所占的比例。施加到航天器上的推力按此比例缩放。注意，该比例因子同时影响质量流量。<br>数据类型：实数；允许值：0 ≤ Real ≤ 1；访问：set、get；默认值：1；单位：N/A；接口：GUI、脚本 |
| **FixedEfficiency** | 推力器效率。仅在 ThrustModel 为 FixedEfficiency 时使用。<br>数据类型：Real；允许值：Real > 0；访问：set、get；默认值：0.7；单位：小数百分比；接口：GUI、脚本 |
| **GravitationalAccel** | 用于 FuelTank/Thruster 计算的引力加速度值。<br>数据类型：实数；允许值：Real > 0；访问：set、get；默认值：9.81；单位：m/s²；接口：GUI、脚本 |
| **HWOriginInBCSX** | 硬件坐标系原点在航天器本体坐标系中表达的 X 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：meters；接口：脚本 |
| **HWOriginInBCSY** | 硬件坐标系原点在航天器本体坐标系中表达的 Y 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：meters；接口：脚本 |
| **HWOriginInBCSZ** | 硬件坐标系原点在航天器本体坐标系中表达的 Z 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：meters；接口：脚本 |
| **Isp** | 推力器比冲。仅在 ThrustModel 设为 FixedEfficiency 或 ConstantThrustAndIsp 时使用。<br>数据类型：Real；允许值：Real > 0；访问：set、get；默认值：4200；单位：seconds；接口：GUI、脚本 |
| **MassFlowCoeff1** | 质量流量系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：-0.004776；单位：见"数学模型"；接口：GUI、脚本 |
| **MassFlowCoeff2** | 质量流量系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0.05717；单位：见"数学模型"；接口：GUI、脚本 |
| **MassFlowCoeff3** | 质量流量系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：-0.09956；单位：见"数学模型"；接口：GUI、脚本 |
| **MassFlowCoeff4** | 质量流量系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0.03211；单位：见"数学模型"；接口：GUI、脚本 |
| **MassFlowCoeff5** | 质量流量系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：2.13781；单位：见"数学模型"；接口：GUI、脚本 |
| **MaximumUsablePower** | 推力器可用于产生推力的最大功率。超过 MaximumUsablePower 的供电功率不用于推力模型。<br>数据类型：Real；允许值：Real > 0 且 Real > MinimumUsablePower；访问：set、get；默认值：7.266；单位：kW；接口：GUI、脚本 |
| **MinimumUsablePower** | 推力器可用于产生推力的最小功率。如果提供给推力器的功率低于 MinimumUsablePower，则不产生推力。<br>数据类型：Real；允许值：Real > 0 且 Real < MaximumUsablePower；访问：set、get；默认值：0.638；单位：kW；接口：GUI、脚本 |
| **MixRatio** | 从多个贮箱抽取燃料时采用的混合比。例如，若有两个贮箱且 MixRatio 设为 [2 1]，则从 Tank 列表中贮箱 1 抽取的燃料量是贮箱 2 的两倍。注意，如果未提供 MixRatio，则从各贮箱等量抽取燃料（MixRatio 被设为与 Tank 列表等长的全 1 向量）。<br>数据类型：Array；允许值：与 Tank 数组中贮箱数量等长的实数数组；访问：set；默认值：[1]；单位：N/A；接口：GUI、脚本 |
| **Origin** | 此字段与 Axes 字段配合使用，允许用户为 ElectricThruster 定义一组以航天器为中心的坐标轴。当使用 Local 坐标系且 Axes 设为 MJ2000Eq 或 SpacecraftBody 时，Origin 不起作用。此字段不能在任务序列中修改。<br>数据类型：Reference Array；允许值：Sun、Mercury、Venus、Earth、Luna、Mars、Jupiter、Saturn、Uranus、Neptune、Pluto；访问：set；默认值：Earth；单位：N/A；接口：GUI、脚本 |
| **Tanks** | ElectricThruster 从中抽取推进剂的 ElectricTank。在脚本命令中，不允许使用空列表（例如 `Thruster1.Tank = {}`）。通过脚本，如果您想表示某个 ElectricThruster 没有关联任何 ElectricTank，请不要在脚本中包含诸如 `Thruster1.Tank = ...` 的命令。此字段不能在任务序列中修改。<br>数据类型：Reference Array；允许值：用户定义的 FuelTank 列表；访问：set；默认值：N/A；单位：N/A；接口：GUI、脚本 |
| **ThrustCoeff1** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：-5.19082；单位：见"数学模型"；接口：GUI、脚本 |
| **ThrustCoeff2** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：2.96519；单位：见"数学模型"；接口：GUI、脚本 |
| **ThrustCoeff3** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：-14.41789；单位：见"数学模型"；接口：GUI、脚本 |
| **ThrustCoeff4** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：54.05382；单位：见"数学模型"；接口：GUI、脚本 |
| **ThrustCoeff5** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：-0.00100092；单位：见"数学模型"；接口：GUI、脚本 |
| **ThrustDirection1** | 航天器推力矢量方向的 X 分量。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：1；单位：N/A；接口：GUI、脚本 |
| **ThrustDirection2** | 航天器推力矢量方向的 Y 分量。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：1；单位：N/A；接口：GUI、脚本 |
| **ThrustDirection3** | 航天器推力矢量方向的 Z 分量。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：N/A；接口：GUI、脚本 |
| **ThrustModel** | 推力器模型的类型。各选项的详细说明见"数学模型"。<br>数据类型：String；允许值：ThrustMassPolynomial、ConstantThrustAndIsp、FixedEfficiency；访问：set、get；默认值：ThrustMassPolynomial；单位：N/A；接口：GUI、脚本 |
| **ThrustScaleFactor** | ThrustScaleFactor 是一个比例因子，对于给定推力器，在推力矢量加入总加速度之前与其相乘。注意，该比例因子的值不影响质量流量。<br>数据类型：实数；允许值：Real ≥ 0；访问：set、get；默认值：1；单位：N/A；接口：GUI、脚本 |

## 交互关系

| 命令或资源 | 描述 |
|------|------|
| BeginFiniteBurn/EndFiniteBurn 命令 | 使用这些命令（需要 Spacecraft 和 FiniteBurn 名称作为输入）来实现有限推力弧段。 |
| ElectricTank 资源 | 该资源包含为 FiniteBurn 资源所指定的 ElectricThruster 提供动力的燃料。 |
| FiniteBurn 资源 | 使用 BeginFiniteBurn/EndFiniteBurn 命令时，必须指定要实现哪个 FiniteBurn 资源。FiniteBurn 资源指定有限推力弧段使用哪些 ElectricThruster。 |
| Spacecraft 资源 | 使用 BeginFiniteBurn/EndFiniteBurn 命令时，必须指定将有限推力弧段施加到哪个 Spacecraft。 |
| Propagate 命令 | 要实现非零的有限推力弧段，必须在 BeginFiniteBurn 和 EndFiniteBurn 语句之间出现一条 Propagate 语句。 |

## GUI

ElectricThruster 对话框允许您指定 ElectricThruster 的属性，包括推力加速度方向矢量的坐标系（Coordinate System）、推力量级和 Isp 系数以及 ElectricTank 的选择。ElectricThruster 对话框的布局如下所示。

> [图：ElectricThruster 对话框布局]

配置 Coordinate System 字段时，您可以在已有坐标系或局部定义的坐标系之间选择。Axes 字段仅在 Coordinate System 设为 Local 时有效。Origin 字段仅在 Coordinate System 设为 Local 且 Axes 设为 VNB 或 LVLH 时有效。

点击 Configure Polynomials 按钮会弹出以下对话框，可在其中输入 ElectricThruster 多项式的系数。

> [图：推力多项式系数配置对话框]

类似地，点击 Configure Polynomials 还可以编辑质量流量系数，如下所示。

> [图：质量流量系数配置对话框]

## 备注

### 数学模型

ElectricThruster 模型支持多种推力和质量流量计算模型，所使用的模型由 ThrustModel 字段设置。当 ThrustModel 设为 ThrustMassPolynomial 时，使用以下多项式计算推力和质量流量：

> [图：ThrustMassPolynomial 模型的推力与质量流量多项式]

其中 P 是提供给推力器的功率（使用 FiniteBurn 资源上定义的功率逻辑计算），f_d 为工作占空比，f_s 为推力比例因子，R_iT 为从推力坐标系到惯性系的旋转矩阵，T_hat 为推力单位矢量。按照行业惯例，质量流量和推力多项式方程的单位分别为 mg/s 和毫牛顿（milli-Newtons）。GMAT 内部会转换单位，使其与运动方程一致。

当 ThrustModel 设为 ConstantThrustAndIsp 时，使用以下多项式计算推力和质量流量：

> [图：ConstantThrustAndIsp 模型的推力与质量流量方程]

其中 C_t1 通过 ConstantThrust 字段设置，Isp 通过 Isp 字段设置，f_d 为工作占空比，f_s 为推力比例因子，R_iT 为从推力坐标系到惯性系的旋转矩阵，T_hat 为推力单位矢量。注意，按照行业惯例，质量流量和推力多项式方程的单位分别为 mg/s 和毫牛顿。GMAT 内部会转换单位，使其与运动方程一致。

当 ThrustModel 设为 FixedEfficiency 时，使用以下多项式计算推力和质量流量：

> [图：FixedEfficiency 模型的推力与质量流量方程]

其中 P 是提供给推力器的功率（由 FiniteBurn 资源上定义的功率逻辑计算），"Eta"为 FixedEfficiency 设置值，f_d 为工作占空比，f_s 为推力比例因子，R_iT 为从推力坐标系到惯性系的旋转矩阵，T_hat 为推力单位矢量。

### 推力器资源与机动的配合使用

ElectricThruster 资源仅与有限推力机动结合使用。要实现有限推力机动，必须首先创建 ElectricTank 和 FiniteBurn 资源。还必须将 ElectricTank 与 ElectricThruster 资源关联，并将 ElectricThruster 与 FiniteBurn 资源关联。实际的有限推力机动使用 BeginFiniteBurn/EndFiniteBurn 命令实现。

有关电推进建模所需全部资源的完整配置说明，请参阅教程"第 12 章 电推进（Electric Propulsion）"。

### 局部坐标系

这里的 Local（局部）坐标系是指通过 ElectricThruster 资源界面"局部"配置的坐标系，而不是通过资源树（Resources Tree）中 Coordinate Systems 文件夹定义的坐标系。

要配置局部坐标系，必须指定输入推力加速度方向矢量 ThrustDirection1-3 的坐标系。如果选择局部坐标系，Axes 子字段给出的四个可选项为 VNB、LVLH、MJ2000Eq 和 SpacecraftBody。VNB（速度-法向-副法向，Velocity-Normal-Binormal）是基于航天器相对于 Origin 子字段运动的非惯性坐标系。例如，若 Origin 选择为 Earth，则该坐标系的 X 轴沿航天器相对于地球的速度方向，Y 轴沿航天器（相对于地球的）瞬时轨道法向，Z 轴完成右手系。

类似地，LVLH（局部垂线-局部水平，Local Vertical Local Horizontal）也是基于航天器相对于 Origin 子字段运动的非惯性坐标系。同样，若选择 Earth 为原点，则该坐标系的 X 轴为航天器相对于地球的位置方向，Z 轴为航天器（相对于地球的）瞬时轨道法向，Y 轴完成右手系。

MJ2000Eq 是基于 J2000 的地心地球平赤道惯性坐标系。注意，定义该坐标系不需要 Origin 子字段。

SpacecraftBody 是航天器的姿态坐标系。由于推力在该坐标系中施加，GMAT 使用航天器的姿态（航天器属性）来确定惯性推力方向。注意，定义该坐标系不需要 Origin 子字段。

### 关于力模型不连续性的注意事项

注意，当在 SolarPowerSystem 资源上对阴影进行建模时，可能会出现可用功率不足以驱动 ElectricThruster 的情况。当 SolarPowerSystem 提供的可用功率或分配给推力器的功率小于 MinimumUsablePower 时就会发生这种情况。此时推力器模型会关闭推力，这可能导致力模型出现不连续。为避免这种情况，您必须传播到边界并切换传播器，或者配置 Propagator 使其在出现不良步长时继续传播。

## 示例

创建一个默认的 ElectricTank 和一个允许燃料消耗的 ElectricThruster，为 ElectricThruster 指定默认的 ElectricTank，并将两者都挂接到 Spacecraft 上。

```
%  Create an ElectricTank Resource
Create ElectricTank anElectricTank

%  Create an Electric Thruster Resource
Create ElectricThruster anElectricThruster
anElectricThruster.CoordinateSystem = Local
anElectricThruster.Origin = Earth
anElectricThruster.Axes = VNB
anElectricThruster.ThrustDirection1 = 1
anElectricThruster.ThrustDirection2 = 0
anElectricThruster.ThrustDirection3 = 0
anElectricThruster.DutyCycle = 1
anElectricThruster.ThrustScaleFactor = 1
anElectricThruster.DecrementMass = true
anElectricThruster.Tank = {anElectricTank}
anElectricThruster.GravitationalAccel = 9.810000000000001
anElectricThruster.ThrustModel = ThrustMassPolynomial
anElectricThruster.MaximumUsablePower = 7.266
anElectricThruster.MinimumUsablePower = 0.638
anElectricThruster.ThrustCoeff1 = -5.19082
anElectricThruster.ThrustCoeff2 = 2.96519
anElectricThruster.ThrustCoeff3 = -14.4789
anElectricThruster.ThrustCoeff4 = 54.05382
anElectricThruster.ThrustCoeff5 = -0.00100092
anElectricThruster.MassFlowCoeff1 = -0.004776
anElectricThruster.MassFlowCoeff2 = 0.05717
anElectricThruster.MassFlowCoeff3 = -0.09956
anElectricThruster.MassFlowCoeff4 = 0.03211
anElectricThruster.MassFlowCoeff5 = 2.13781
anElectricThruster.FixedEfficiency = 0.7
anElectricThruster.Isp = 4200
anElectricThruster.ConstantThrust = 0.237

%  Create a SolarPowerSystem Resource
Create SolarPowerSystem aSolarPowerSystem

%  Create a Spacecraft Resource and attach hardware
Create Spacecraft DefaultSC
DefaultSC.Tanks = {anElectricTank}
DefaultSC.Thrusters = {anElectricThruster}
DefaultSC.PowerSystem = aSolarPowerSystem

BeginMissionSequence
```

说明：本示例创建电推进贮箱 anElectricTank 和电推力器 anElectricThruster（采用局部 VNB 坐标系、ThrustMassPolynomial 推力模型，并给定可用功率范围、推力系数、质量流量系数、固定效率、比冲和常值推力等参数），再创建太阳电源系统 aSolarPowerSystem，最后将贮箱、推力器和电源系统挂接到航天器 DefaultSC。
