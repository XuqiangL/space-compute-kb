# 化学推力器（ChemicalThruster）
> 译自 GMAT R2026a 帮助文档 Thruster.html

**ChemicalThruster** —— 化学推力器模型

## 描述

ChemicalThruster 资源是化学推力器的模型，它使用多项式将推力和比冲（Isp）建模为贮箱压力和温度的函数。ChemicalThruster 模型还允许您指定工作占空比（Duty Cycle）和比例因子等属性，并将 ChemicalThruster 与 ChemicalTank 相关联。您可以通过在坐标系中指定推力分量来灵活定义推力方向，这些坐标系包括（局部定义的）SpacecraftBody 或 LVLH，也可以选择任何已配置的 CoordinateSystem 资源。

另请参阅：BeginFiniteBurn、ChemicalTank、FiniteBurn

## 字段

下面的常数 Ci 用于以下方程，计算推力 F_T（单位：牛顿）随压力 P（kPa）和温度 T（摄氏度）的变化关系。

> [图：推力多项式公式]

下面的常数 Ki 用于以下方程，计算比冲 Isp（单位：秒）随压力 P（kPa）和温度 T（摄氏度）的变化关系。

> [图：比冲多项式公式]

| 字段 | 描述 |
|------|------|
| **Axes** | 允许用户为 ChemicalThruster 定义一组以航天器为中心的坐标轴。此字段不能在任务序列（Mission Sequence）中修改。<br>数据类型：Reference Array；允许值：VNB、LVLH、MJ2000Eq、SpacecraftBody；访问：set；默认值：VNB；单位：N/A；接口：GUI、脚本 |
| **CoordinateSystem** | 确定方向参数 ThrustDirection1、ThrustDirection2 和 ThrustDirection3 所参照的坐标系。此字段不能在任务序列中修改。<br>数据类型：Reference Array；允许值：Local、EarthMJ2000Eq、EarthMJ2000Ec、EarthFixed 或任何用户自定义坐标系；访问：set；默认值：Local；单位：N/A；接口：GUI、脚本 |
| **C1** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：10；单位：N；接口：GUI、脚本 |
| **C2** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：N/kPa；接口：GUI、脚本 |
| **C3** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：N；接口：GUI、脚本 |
| **C4** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：N/kPa；接口：GUI、脚本 |
| **C5** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：N/kPa²；接口：GUI、脚本 |
| **C6** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：N/kPa^C7；接口：GUI、脚本 |
| **C7** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：无；接口：GUI、脚本 |
| **C8** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：N/kPa^C9；接口：GUI、脚本 |
| **C9** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：无；接口：GUI、脚本 |
| **C10** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：N/kPa^C11；接口：GUI、脚本 |
| **C11** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：无；接口：GUI、脚本 |
| **C12** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：N；接口：GUI、脚本 |
| **C13** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：无；接口：GUI、脚本 |
| **C14** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：1/kPa；接口：GUI、脚本 |
| **C15** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：无；接口：GUI、脚本 |
| **C16** | 推力系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：1/kPa；接口：GUI、脚本 |
| **DecrementMass** | 该标志决定 FuelMass 是否随使用而递减。此字段不能在任务序列中修改。<br>数据类型：Boolean；允许值：true、false；访问：set；默认值：false；单位：N/A；接口：GUI、脚本 |
| **DutyCycle** | 机动过程中推力器开机时间所占的比例。施加到航天器上的推力按此比例缩放。注意，该比例因子同时影响质量流量。<br>数据类型：实数；允许值：0 ≤ Real ≤ 1；访问：set、get；默认值：1；单位：N/A；接口：GUI、脚本 |
| **GravitationalAccel** | 引力加速度。<br>数据类型：实数；允许值：Real > 0；访问：set、get；默认值：9.81；单位：m/s²；接口：GUI、脚本 |
| **HWOriginInBCSX** | 硬件坐标系原点在航天器本体坐标系中表达的 X 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：meters；接口：脚本 |
| **HWOriginInBCSY** | 硬件坐标系原点在航天器本体坐标系中表达的 Y 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：meters；接口：脚本 |
| **HWOriginInBCSZ** | 硬件坐标系原点在航天器本体坐标系中表达的 Z 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：meters；接口：脚本 |
| **K1** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：300；单位：s；接口：GUI、脚本 |
| **K2** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：s/kPa；接口：GUI、脚本 |
| **K3** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：s；接口：GUI、脚本 |
| **K4** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：s/kPa；接口：GUI、脚本 |
| **K5** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：s/kPa²；接口：GUI、脚本 |
| **K6** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：s/kPa^C7；接口：GUI、脚本 |
| **K7** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：无；接口：GUI、脚本 |
| **K8** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：s/kPa^C9；接口：GUI、脚本 |
| **K9** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：无；接口：GUI、脚本 |
| **K10** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：s/kPa^C11；接口：GUI、脚本 |
| **K11** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：无；接口：GUI、脚本 |
| **K12** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：s；接口：GUI、脚本 |
| **K13** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：无；接口：GUI、脚本 |
| **K14** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：1/kPa；接口：GUI、脚本 |
| **K15** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：无；接口：GUI、脚本 |
| **K16** | 比冲（ISP）系数。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：1/kPa；接口：GUI、脚本 |
| **MixRatio** | 从多个贮箱抽取燃料时采用的混合比。例如，若有两个贮箱且 MixRatio 设为 [2 1]，则从 Tank 列表中贮箱 1 抽取的燃料量是贮箱 2 的两倍。注意，如果未提供 MixRatio，则从各贮箱等量抽取燃料（MixRatio 被设为与 Tank 列表等长的全 1 向量）。<br>数据类型：Array；允许值：与 Tank 数组中贮箱数量等长的实数数组；访问：set；默认值：[1]；单位：N/A；接口：GUI、脚本 |
| **Origin** | 此字段与 Axes 字段配合使用，允许用户为 ChemicalThruster 定义一组以航天器为中心的坐标轴。当使用 Local 坐标系且 Axes 设为 MJ2000Eq 或 SpacecraftBody 时，Origin 不起作用。此字段不能在任务序列中修改。<br>数据类型：Reference Array；允许值：Sun、Mercury、Venus、Earth、Luna、Mars、Jupiter、Saturn、Uranus、Neptune、Pluto；访问：set；默认值：Earth；单位：N/A；接口：GUI、脚本 |
| **Tank** | 推力器从中抽取推进剂的 ChemicalTank 列表。推力器至少需要指定一个贮箱。此字段不能在任务序列中修改。<br>数据类型：Reference Array；允许值：用户定义的贮箱列表；访问：set；默认值：N/A；单位：N/A；接口：GUI、脚本 |
| **ThrustDirection1** | 航天器推力矢量方向的 X 分量。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：1；单位：N/A；接口：GUI、脚本 |
| **ThrustDirection2** | 航天器推力矢量方向的 Y 分量。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：N/A；接口：GUI、脚本 |
| **ThrustDirection3** | 航天器推力矢量方向的 Z 分量。<br>数据类型：Real；允许值：实数；访问：set、get；默认值：0；单位：N/A；接口：GUI、脚本 |
| **ThrustScaleFactor** | ThrustScaleFactor 是一个比例因子，对于给定推力器，在推力矢量加入总加速度之前与其相乘。注意，该比例因子的值不影响质量流量。<br>数据类型：实数；允许值：Real ≥ 0；访问：set、get；默认值：1；单位：N/A；接口：GUI、脚本 |

## 交互关系

| 命令或资源 | 描述 |
|------|------|
| BeginFiniteBurn/EndFiniteBurn 命令 | 使用这些命令（需要 Spacecraft 和 FiniteBurn 名称作为输入）来实现有限推力弧段。 |
| ChemicalTank 资源 | 该资源包含为 FiniteBurn 资源所指定的 ChemicalThruster 提供动力的燃料。 |
| FiniteBurn 资源 | 使用 BeginFiniteBurn/EndFiniteBurn 命令时，必须指定要实现哪个 FiniteBurn 资源。FiniteBurn 资源指定有限推力弧段使用哪些 ChemicalThruster。 |
| Spacecraft 资源 | 使用 BeginFiniteBurn/EndFiniteBurn 命令时，必须指定将有限推力弧段施加到哪个 Spacecraft。 |
| Propagate 命令 | 要实现非零的有限推力弧段，必须在 BeginFiniteBurn 和 EndFiniteBurn 语句之间出现一条 Propagate 语句。 |

## GUI

ChemicalThruster 对话框允许您指定 ChemicalThruster 的属性，包括推力加速度方向矢量的坐标系（Coordinate System）、推力量级和 Isp 系数以及 ChemicalTank 的选择。ChemicalThruster 对话框的布局如下所示。

> [图：ChemicalThruster 对话框布局]

配置 Coordinate System 字段时，您可以在已有坐标系或局部定义的坐标系之间选择。Axes 字段仅在 Coordinate System 设为 Local 时有效。Origin 字段仅在 Coordinate System 设为 Local 且 Axes 设为 VNB 或 LVLH 时有效。

如下图所示，如果勾选了 Decrement Mass，则可以输入用于计算燃料消耗的引力加速度值。此处输入的引力加速度值仅影响燃料消耗，不影响力模型。

> [图：勾选 Decrement Mass 后的 ChemicalThruster 对话框]

点击 Edit Thruster Coef. 按钮会弹出以下对话框，可在其中输入 ChemicalThruster 多项式的系数。

> [图：推力系数编辑对话框]

类似地，点击 Edit Impulse Coef. 按钮会弹出以下对话框，可在其中输入比冲（ISP）多项式的系数。

> [图：比冲系数编辑对话框]

## 备注

### ChemicalThruster 资源与机动的配合使用

ChemicalThruster 资源仅与有限推力机动结合使用。要实现有限推力机动，必须首先创建 ChemicalTank 和 FiniteBurn 资源。还必须将 ChemicalTank 与 ChemicalThruster 资源关联，并将 ChemicalThruster 与 FiniteBurn 资源关联。有限推力机动使用 BeginFiniteBurn/EndFiniteBurn 命令实现。有关 ChemicalThruster 资源如何与有限推力机动结合使用的完整示例，请参阅 BeginFiniteBurn/EndFiniteBurn 命令文档。

### 推力与比冲的计算

未缩放的推力 F_T 和比冲 Isp 随压力（kPa）和温度（摄氏度）的变化由以下多项式计算。

> [图：推力多项式公式]

> [图：比冲多项式公式]

输出的推力 T（单位：牛顿）按 Duty Cycle 和 Thrust Scale Factor 缩放。推力加速度方向矢量（实际加速度的方向，而非推力器喷管的方向）由 ThrustDirection1-3 给出，并在输入的 Coordinate System 中施加。Isp 以秒为单位输出。

质量流量和推力方程如下所示，其中 F_T 和 Isp 定义如上，f_d 为工作占空比，f_s 为推力比例因子，R_iT 为从推力坐标系到惯性系的旋转矩阵，T_d 为单位化推力方向。

> [图：质量流量与推力方程]

### 局部坐标系

这里的 Local（局部）坐标系是指通过 ChemicalThruster 资源界面"局部"配置的坐标系，而不是通过资源树（Resources Tree）中 Coordinate Systems 文件夹定义的坐标系。

要配置局部坐标系，必须指定输入推力加速度方向矢量 ThrustDirection1-3 的坐标系。如果选择局部坐标系，Axes 子字段给出的四个可选项为 VNB、LVLH、MJ2000Eq 和 SpacecraftBody。VNB（速度-法向-副法向，Velocity-Normal-Binormal）是基于航天器相对于 Origin 子字段运动的非惯性坐标系。例如，若 Origin 选择为 Earth，则该坐标系的 X 轴沿航天器相对于地球的速度方向，Y 轴沿航天器（相对于地球的）瞬时轨道法向，Z 轴完成右手系。

类似地，LVLH（局部垂线-局部水平，Local Vertical Local Horizontal）也是基于航天器相对于 Origin 子字段运动的非惯性坐标系。同样，若选择 Earth 为原点，则该坐标系的 X 轴为航天器相对于地球的位置方向，Z 轴为航天器（相对于地球的）瞬时轨道法向，Y 轴完成右手系。

MJ2000Eq 是基于 J2000 的地心地球平赤道惯性坐标系。注意，定义该坐标系不需要 Origin 子字段。

SpacecraftBody 是航天器的姿态坐标系。由于推力在该坐标系中施加，GMAT 使用航天器的姿态（航天器属性）来确定惯性推力方向。注意，定义该坐标系不需要 Origin 子字段。

### 设置 ChemicalTank 温度和参考温度时的注意事项

注意，推力和 ISP 多项式都包含涉及比值（温度 / 参考温度）的项。在 GMAT 中，该温度比以摄氏度为单位计算，因此当参考温度等于零时存在不连续。为此，GMAT 要求输入的参考温度的绝对值大于 0.01。

还需注意，当参考温度接近 0 摄氏度时，推力和 ISP 多项式的形式具有一些您需要了解的行为。由于上述不连续性，当参考温度接近零时，多项式不平滑变化。例如，考虑两个参考温度 -0.011 和 +0.011 摄氏度。这两个温度数值接近，人们可能期望它们具有大致相似的推力和 ISP 值。但情况可能并非如此（取决于您对推力/ISP 系数的选择），因为与这两个参考温度相关联的温度比具有相同的量级但符号相反。您可以选择将输入的参考温度设为等于输入温度，从而在使用当前实现的基于玻意耳定律（Boyle's Law）的 ChemicalTank 模型（其中燃料温度不随燃料消耗而变化）时，消除推力和 ISP 对温度的任何依赖。

## 示例

创建一个默认的 ChemicalTank 和一个允许燃料消耗的 ChemicalThruster，为 ChemicalThruster 指定默认的 ChemicalTank，并将 ChemicalThruster 和 ChemicalTank 都挂接到 Spacecraft 上。

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

%  Create a ChemicalThruster, that allows fuel depletion, and assign it a ChemicalTank
Create ChemicalThruster Thruster1
Thruster1.CoordinateSystem = Local
Thruster1.Origin = Earth
Thruster1.Axes = VNB
Thruster1.ThrustDirection1 = 1
Thruster1.ThrustDirection2 = 0
Thruster1.ThrustDirection3 = 0
Thruster1.DutyCycle = 1
Thruster1.ThrustScaleFactor = 1
Thruster1.DecrementMass = true
Thruster1.Tank = {FuelTank1}
Thruster1.GravitationalAccel = 9.810000000000001
Thruster1.C1 = 10
Thruster1.C2 = 0
Thruster1.C3 = 0
Thruster1.C4 = 0
Thruster1.C5 = 0
Thruster1.C6 = 0
Thruster1.C7 = 0
Thruster1.C8 = 0
Thruster1.C9 = 0
Thruster1.C10 = 0
Thruster1.C11 = 0
Thruster1.C12 = 0
Thruster1.C13 = 0
Thruster1.C14 = 0
Thruster1.C15 = 0
Thruster1.C16 = 0
Thruster1.K1 = 300
Thruster1.K2 = 0
Thruster1.K3 = 0
Thruster1.K4 = 0
Thruster1.K5 = 0
Thruster1.K6 = 0
Thruster1.K7 = 0
Thruster1.K8 = 0
Thruster1.K9 = 0
Thruster1.K10 = 0
Thruster1.K11 = 0
Thruster1.K12 = 0
Thruster1.K13 = 0
Thruster1.K14 = 0
Thruster1.K15 = 0
Thruster1.K16 = 0

%  Add the ChemicalThruster and the ChemicalTank to a Spacecraft
Create Spacecraft DefaultSC
DefaultSC.Tanks = {FuelTank1}
DefaultSC.Thrusters = {Thruster1}

BeginMissionSequence
```

说明：本示例先创建贮箱 FuelTank1 并设置其燃料质量、压力、温度、容积、密度和压力模型；然后创建推力器 Thruster1，采用局部 VNB 坐标系，推力沿 X 方向，允许质量递减，并关联 FuelTank1；C1=10、K1=300 给定常值推力和比冲，其余系数置零；最后将贮箱和推力器挂接到航天器 DefaultSC。

创建两个 ChemicalTank（名为 aTank1 和 aTank2）和一个 ChemicalThruster，将 ChemicalThruster 和两个 ChemicalTank 都挂接到 Spacecraft 上，并配置推力器从 aTank1 抽取的燃料量为 aTank2 的四倍。

```
%  Create the ChemicalTank Resource
Create Spacecraft aSat
aSat.Tanks = {aTank1,aTank2}
aSat.Thrusters = {aThruster}

% Create two tanks
Create ChemicalTank aTank1 aTank2

%  Configure thruster to draw four times as much fuel 
%  from aTank1 than aTank2
Create ChemicalThruster aThruster
aThruster.Tank = {aTank1,aTank2}
aThruster.MixRatio = [4 1]

BeginMissionSequence
```

说明：本示例通过 MixRatio = [4 1] 设置混合比，使推力器从 aTank1 抽取的燃料量是 aTank2 的四倍。
