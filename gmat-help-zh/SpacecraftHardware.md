# 航天器硬件（Spacecraft Hardware）
> 译自 GMAT R2026a 帮助文档 SpacecraftHardware.html

**Spacecraft Hardware —— 为航天器添加硬件**

## 描述

硬件（Hardware）字段允许你将预先配置好的硬件模型挂接到航天器（Spacecraft）上。目前的模型包括 `ChemicalTank`（化学燃料箱）、`ChemicalThruster`（化学推力器）、`ElectricTank`（电推进燃料箱）和 `ElectricThruster`（电推力器）。在将硬件模型挂接到 `Spacecraft` 之前，必须先创建该模型。

**另请参阅**：`ChemicalTank`、`ChemicalThruster`、`ElectricTank`、`ElectricThruster`

## 字段

### Tanks

该字段用于将 `FuelTank`（燃料箱，可多个）挂接到 `Spacecraft`。在脚本命令中允许使用空列表，例如 `DefaultSC.Tanks={}`，表示该航天器未挂接任何燃料箱。

- 数据类型：引用数组（Reference Array）
- 允许值：`ChemicalTank` 和 `ChemicalThruster` 组成的列表（原文如此）
- 访问权限：仅可设置（set）
- 默认值：N/A
- 单位：N/A
- 接口：GUI、脚本

### Thrusters

该字段用于将 `Thruster`（推力器，可多个）挂接到 `Spacecraft`。在脚本命令中允许使用空列表，例如 `DefaultSC.Thrusters={}`，表示该航天器未挂接任何推力器。

- 数据类型：引用数组（Reference Array）
- 允许值：`ChemicalThruster` 和 `ElectricThruster` 组成的列表
- 访问权限：仅可设置（set）
- 默认值：N/A
- 单位：N/A
- 接口：GUI、脚本

## GUI

可挂接到航天器的硬件有两类：`FuelTank`（燃料箱）和 `Thruster`（推力器）。下面介绍创建这些硬件并将它们挂接到 `Spacecraft` 的方法。有关如何配置 `FuelTank` 和 `Thruster` 资源的详细信息，请参阅各硬件项的帮助文档。注意，下面的讨论以化学推进系统为例，但同样适用于电推进系统。

如下图所示，要在脚本中添加 `ChemicalTank`，先高亮选中 `Hardware`（硬件）资源，然后右键单击并选择添加 `ChemicalTank`。

> [图：在资源树中右键 Hardware 添加 ChemicalTank]

要在脚本中添加 `Thruster`，先高亮选中 `Hardware` 资源，然后右键单击并选择添加 `Thruster`。

> [图：在资源树中右键 Hardware 添加 Thruster]

至此，我们已经创建了一个 `ChemicalTank` 和一个 `ChemicalThruster`。接下来，将二者挂接到某个特定的 `Spacecraft` 上。操作方法：在 `Spacecraft` 资源下双击目标航天器，打开对应的 GUI 面板，然后单击 `Tanks`（燃料箱）选项卡，显示如下界面。

> [图：Spacecraft 编辑面板的 Tanks 选项卡]

接着，选中所需的 `ChemicalTank`，使用右箭头按钮将该 `ChemicalTank` 挂接到 `Spacecraft`，如下图所示。然后单击 `Apply`（应用）按钮。

> [图：用右箭头把 ChemicalTank 加入已挂接列表]

类似地，要将 `ChemicalThruster` 挂接到 `Spacecraft`，双击 `Spacecraft` 资源下的目标航天器，选择 `Actuators`（执行机构）选项卡。然后选中所需的 `ChemicalThruster`，使用右箭头将其挂接到 `Spacecraft`，如下图所示。最后单击 `Apply` 按钮。

> [图：在 Actuators 选项卡中挂接 ChemicalThruster]

## 备注

若要使用 `Thruster` 对 `Spacecraft` 施加有限推力弧段（finite burn），还需要额外的步骤。例如，创建 `ChemicalThruster` 资源时，必须将一个 `ChemicalTank` 与该 `ChemicalThruster` 相关联。有关此问题及相关事项的详细信息，请参阅 `ChemicalTank`、`ChemicalThruster` 和 `FiniteBurn` 资源的帮助文档。

## 示例

创建一个默认 `Spacecraft`，创建 `ChemicalTank` 和 `ChemicalThruster` 资源，并将它们挂接到该航天器上。

```
% Create default Spacecraft, ChemicalTank, and Thruster Resources
Create Spacecraft DefaultSC
Create ChemicalTank FuelTank1
Create ChemicalThruster Thruster1

%  Attach ChemicalTank and Thruster to the spacecraft
DefaultSC.Thrusters = {Thruster1}
DefaultSC.Tanks = {FuelTank1}

BeginMissionSequence
```

**中文说明**：该示例先创建默认航天器 `DefaultSC`、化学燃料箱 `FuelTank1` 和化学推力器 `Thruster1`，然后通过 `Thrusters` 和 `Tanks` 字段把推力器和燃料箱挂接到航天器上。