# 有限推力机动（FiniteBurn）

> 译自 GMAT R2026a 帮助文档 FiniteBurn.html

**FiniteBurn** —— 有限推力机动。

## 描述

当需要连续推进时，使用 `FiniteBurn` 资源。脉冲机动通过 `Maneuver` 命令瞬时发生，而有限推力机动则从 `BeginFiniteBurn` 命令开始持续作用，直到任务序列中遇到 `EndFiniteBurn` 命令为止。要施加非零的有限推力机动，必须在 `BeginFiniteBurn` 和 `EndFiniteBurn` 命令之间存在一个 `Propagate` 命令。

另请参阅：ChemicalTank（化学推进剂箱）、ChemicalThruster（化学推力器）、Spacecraft（航天器）、BeginFiniteBurn（开始有限推力机动）、EndFiniteBurn（结束有限推力机动）、Calculation Parameters（计算参数）。

## 字段

| 字段 | 描述 |
|------|------|
| **Thrusters** | `Thruster` 字段允许从先前创建的推力器列表中选择在施加有限推力机动时使用哪个推力器。目前，使用 GUI 只能选择一个推力器挂载到 `FiniteBurn` 资源上。使用脚本接口，可以将多个推力器挂载到一个 `FiniteBurn` 资源上。在脚本命令中，允许使用空列表，例如 `FiniteBurn1.Thruster={}`，但用途有限，因为如果已创建了 `ChemicalThruster`，GUI 会自动将其与 `FiniteBurn` 关联。该字段不能在任务序列中修改。<br>• 数据类型：Reference Array<br>• 允许值：用户创建的推力器列表。可以是 `ChemicalThruster` 列表或 `ElectricThruster` 列表，但不能混合使用化学推力器和电推力器。<br>• 访问权限：set<br>• 默认值：无默认值<br>• 单位：N/A<br>• 接口：GUI、脚本，或仅其一 |
| **VectorFormat** | 已废弃。允许你定义有限推力机动推力方向的格式。该字段无效。在 `Thruster` 资源中指定的有限推力机动推力方向始终以 `Cartesian`（笛卡尔）格式给出。注意：你可以使用 GMAT 脚本将其他表示形式转换为笛卡尔格式，然后再设置笛卡尔格式。<br>• 数据类型：Enumeration<br>• 允许值：`Cartesian`、`Spherical`<br>• 访问权限：set<br>• 默认值：`Cartesian`<br>• 单位：N/A<br>• 接口：脚本 |

## GUI

`FiniteBurn` 对话框允许你指定有限推力机动使用哪个推力器。`FiniteBurn` 对话框的布局如下图所示。

> [图：FiniteBurn 对话框界面]

## 备注

### 配置 FiniteBurn

要执行有限推力机动，必须正确配置 `FiniteBurn` 资源本身以及若干相关资源和命令。必须将特定的 `ChemicalThruster` 硬件资源与已创建的 `FiniteBurn` 关联；必须将特定的 `ChemicalTank` 硬件资源与所选的 `ChemicalThruster` 关联；最后，必须将所选的推力器（Thrusters）和推进剂箱（Tanks）都挂载到所需的 `Spacecraft` 上。更多细节请参阅下面的示例。

### 使用多个推力器的 FiniteBurn

使用 GUI 时，一个 `FiniteBurn` 资源必须恰好与一个推力器关联。

使用脚本接口时，可以将多个推力器指派给单个 `FiniteBurn` 资源。

## 交互关系

| 字段 | 描述 |
|------|------|
| `Spacecraft` 资源 | 必须创建航天器才能施加任何机动。 |
| `Thruster` 资源 | 如"备注"中所述，每个 `FiniteBurn` 资源必须至少与一个 `ChemicalThruster` 或 `ElectricThruster` 关联。资源树中创建的任何推力器都可以纳入 `FiniteBurn`，但不能混合使用不同类型的推力器。 |
| `ChemicalTank` 资源 | 要执行有限推力机动，必须将 `Tank` 挂载到 `Spacecraft` 上。（需要 `ChemicalTank` 来提供建模推力和比冲时所用的压力和温度数据。如果要建模质量消耗，也需要 `Tank`。） |
| `BeginFiniteBurn` 和 `EndFiniteBurn` 命令 | 创建 `FiniteBurn` 后，要在任务序列中施加它，必须将 `BeginFiniteBurn` 和 `EndFiniteBurn` 命令附加到任务树中。 |
| `Propagate` 命令 | 要施加非零的有限推力机动，必须在 `BeginFiniteBurn` 和 `EndFiniteBurn` 命令之间存在一个 `Propagate` 命令。 |
### 报告 FiniteBurn 参数

GMAT 现在支持报告有限推力机动的推力分量数据的参数。这些参数包括：所有推力器在三个坐标方向上的总推力、所有推力器在三个坐标方向上的总加速度，以及所有推力器的总质量流率。目前，默认情况下，三个坐标方向上的总推力和总加速度参数仅在 J2000 坐标系中报告，不支持任何其他坐标系依赖。此外，你现在还可以报告任何推力器的个体参数，例如推力量值、比冲（Isp）和质量流率。这些有限推力机动和推力器特有参数的定义请参阅 Calculation Parameters（计算参数）参考。另请参阅"示例"部分，其中展示了如何将有限推力机动和单个推力器特有参数报告到报告文件中。

## 示例

配置一个化学有限推力机动。创建默认的 `Spacecraft` 和 `ChemicalTank` 资源；创建一个默认的 `ChemicalThruster`，允许从默认的 `ChemicalTank` 消耗燃料；将 `ChemicalTank` 和 `ChemicalThruster` 挂载到 `Spacecraft` 上；创建默认的 `ForceModel` 和 `Propagator`；创建一个使用默认推力器的有限推力机动，并对航天器施加 30 分钟的有限推力机动。

```
% Create a default Spacecraft and ChemicalTank Resource
Create Spacecraft DefaultSC
Create ChemicalTank FuelTank1

% Create a default ChemicalThruster.  Allow for fuel depletion from 
% the default ChemicalTank.
Create ChemicalThruster Thruster1
Thruster1.DecrementMass = true
Thruster1.Tank = {FuelTank1}

%  Attach ChemicalTank and ChemicalThruster to the spacecraft
DefaultSC.Thrusters = {Thruster1}
DefaultSC.Tanks = {FuelTank1}

%  Create default ForceModel and Propagator
Create ForceModel DefaultProp_ForceModel
Create Propagator DefaultProp
DefaultProp.FM = DefaultProp_ForceModel

%  Create a Finite Burn that uses the default thruster
Create FiniteBurn FiniteBurn1
FiniteBurn1.Thrusters = {Thruster1}

BeginMissionSequence

%  Implement 30 minute finite burn
BeginFiniteBurn FiniteBurn1(DefaultSC)
Propagate DefaultProp(DefaultSC) {DefaultSC.ElapsedSecs = 1800}
EndFiniteBurn FiniteBurn1(DefaultSC)
```

上述脚本：创建航天器、推进剂箱和化学推力器（开启质量消耗并指定燃料箱），将推力器与燃料箱挂载到航天器；创建力模型与传播器；创建使用 Thruster1 的有限推力机动 FiniteBurn1；在任务序列中通过 BeginFiniteBurn/Propagate/EndFiniteBurn 实现 1800 秒（30 分钟）的连续推力机动。

本示例展示如何报告有限推力机动参数，例如三个坐标方向上的总加速度（来自所有推力器）、总推力（来自所有推力器）。我们还报告所有推力器的总质量流率。此外，还报告单个推力器的特有参数，例如推力器质量流率、推力量值和推力器比冲。注意，在生成的报告中，当推力器未开机时，所有有限推力机动和推力器参数都报告为零。

```
Create Spacecraft aSat

Create ChemicalTank aFuelTank

Create ChemicalThruster aThruster
aThruster.DecrementMass = true
aThruster.Tank = {aFuelTank}
aThruster.C1 = 1000  % Constant Thrust
aThruster.K1 = 300 % Constant Isp

aSat.Thrusters = {aThruster}
aSat.Tanks = {aFuelTank}

Create ForceModel aFM
aFM.CentralBody = Earth
aFM.PointMasses = {Earth}

Create Propagator aProp
aProp.FM = aFM

Create FiniteBurn aFB
aFB.Thrusters = {aThruster}

Create ReportFile rf
rf.Add = {aSat.UTCGregorian, aFB.TotalAcceleration1, aFB.TotalAcceleration2, ...
aFB.TotalAcceleration3, aFB.TotalMassFlowRate, aFB.TotalThrust1, ...
aFB.TotalThrust2, aFB.TotalThrust3, aSat.aThruster.MassFlowRate, ...
aSat.aThruster.ThrustMagnitude, aSat.aThruster.Isp}

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedSecs = 1000}

% Do a Finite-Burn for 1800 Secs
BeginFiniteBurn aFB(aSat)
Propagate aProp(aSat) {aSat.ElapsedSecs = 1800}
EndFiniteBurn aFB(aSat)

Propagate aProp(aSat) {aSat.ElapsedSecs = 1000}
```

上述脚本：创建航天器 aSat、燃料箱 aFuelTank 和推力器 aThruster（恒定推力 1000、恒定比冲 300），配置仅含地球点质量的力模型与传播器；创建有限推力机动 aFB 和报告文件 rf（添加总加速度三分量、总质量流率、总推力三分量以及单个推力器的质量流率、推力量值、比冲等参数）；任务序列先传播 1000 秒，再进行 1800 秒有限推力机动，最后再传播 1000 秒，从而对比机动前后的参数报告。
