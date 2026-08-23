# 电推进贮箱（ElectricTank）
> 译自 GMAT R2026a 帮助文档 ElectricTank.html

**ElectricTank** —— 电推进系统燃料贮箱模型

## 描述

ElectricTank 是贮箱模型，是采用电推进系统的有限推力弧段所必需的。要使用 ElectricTank，必须先创建贮箱，然后将其挂接到所需的 Spacecraft 并与 ElectricThruster 关联，如下例所示。此外，还必须创建 SolarPowerSystem 或 NuclearPowerSystem 并将其挂接到 Spacecraft。

有关电推进建模所需全部资源的完整配置说明，请参阅教程"第 12 章 电推进（Electric Propulsion）"。

另请参阅：ElectricThruster、NuclearPowerSystem、SolarPowerSystem

## 字段

| 字段 | 描述 |
|------|------|
| **AllowNegativeFuelMass** | 此字段允许 ElectricTank 具有负的燃料质量，这在优化和定靶序列收敛之前可能有用。此字段不能在任务序列中修改。<br>数据类型：Boolean；允许值：true、false；访问：set；默认值：false；单位：N/A；接口：GUI、脚本 |
| **DirectionX** | ElectricTank 方向主矢量在本体坐标系中的 X 分量。与次方向元素结合使用以计算方向。<br>数据类型：Real；允许值：实数；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **DirectionY** | ElectricTank 方向主矢量在本体坐标系中的 Y 分量。与次方向元素结合使用以计算方向。<br>数据类型：Real；允许值：实数；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **DirectionZ** | ElectricTank 方向主矢量在本体坐标系中的 Z 分量。与次方向元素结合使用以计算方向。<br>数据类型：Real；允许值：实数；访问：set；默认值：1；单位：N/A；接口：脚本 |
| **FuelCenterOfMassX** | 燃料质心在硬件坐标系中的 X 分量。<br>数据类型：Real；允许值：任意实数；访问：set、get；默认值：0.0；单位：meters；接口：GUI、脚本 |
| **FuelCenterOfMassY** | 燃料质心在硬件坐标系中的 Y 分量。<br>数据类型：Real；允许值：任意实数；访问：set、get；默认值：0.0；单位：meters；接口：GUI、脚本 |
| **FuelCenterOfMassZ** | 燃料质心在硬件坐标系中的 Z 分量。<br>数据类型：Real；允许值：任意实数；访问：set、get；默认值：0.0；单位：meters；接口：GUI、脚本 |
| **FuelMass** | 贮箱中燃料的质量。<br>数据类型：Real；允许值：Real > 0；访问：set、get；默认值：756；单位：kg；接口：GUI、脚本 |
| **FuelMomentOfInertiaXX** | 燃料转动惯量的 XX 分量。<br>数据类型：Real；允许值：Real ≥ 0；访问：set、get；默认值：99；单位：Kg-m^2；接口：GUI、脚本 |
| **FuelMomentOfInertiaXY** | 燃料转动惯量的 XY 分量。<br>数据类型：Real；允许值：Real ≥ 0；访问：set、get；默认值：0；单位：Kg-m^2；接口：GUI、脚本 |
| **FuelMomentOfInertiaXZ** | 燃料转动惯量的 XZ 分量。<br>数据类型：Real；允许值：Real ≥ 0；访问：set、get；默认值：0；单位：Kg-m^2；接口：GUI、脚本 |
| **FuelMomentOfInertiaYY** | 燃料转动惯量的 YY 分量。<br>数据类型：Real；允许值：Real ≥ 0；访问：set、get；默认值：99；单位：Kg-m^2；接口：GUI、脚本 |
| **FuelMomentOfInertiaYZ** | 燃料转动惯量的 YZ 分量。<br>数据类型：Real；允许值：Real ≥ 0；访问：set、get；默认值：0；单位：Kg-m^2；接口：GUI、脚本 |
| **FuelMomentOfInertiaZZ** | 燃料转动惯量的 ZZ 分量。<br>数据类型：Real；允许值：Real ≥ 0；访问：set、get；默认值：99；单位：Kg-m^2；接口：GUI、脚本 |
| **HWOriginInBCSX** | 硬件坐标系原点在航天器本体坐标系中表达的 X 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **HWOriginInBCSY** | 硬件坐标系原点在航天器本体坐标系中表达的 Y 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **HWOriginInBCSZ** | 硬件坐标系原点在航天器本体坐标系中表达的 Z 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **SecondDirectionX** | 在本体坐标系中表达的、用于确定硬件绕方向矢量姿态的矢量的 X 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **SecondDirectionY** | 在本体坐标系中表达的、用于确定硬件绕方向矢量姿态的矢量的 Y 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：-1；单位：N/A；接口：脚本 |
| **SecondDirectionZ** | 在本体坐标系中表达的、用于确定硬件绕方向矢量姿态的矢量的 Z 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：N/A；接口：脚本 |

## GUI

ElectricTank 对话框允许您指定燃料贮箱的属性。ElectricTank 对话框的布局如下所示。

> [图：ElectricTank 对话框布局]

## 备注

### ElectricTank 资源与机动的配合使用

ElectricTank 与有限推力机动结合使用。要实现有限推力机动，必须首先创建 ElectricThruster 和 FiniteBurn 资源。还必须将 ElectricTank 与 ElectricThruster 资源关联，并将 ElectricThruster 与 FiniteBurn 资源关联。有限推力机动使用 BeginFiniteBurn/EndFiniteBurn 命令实现。有关 ElectricTank 资源如何与有限推力机动结合使用的完整示例，请参阅 BeginFiniteBurn/EndFiniteBurn 命令文档。

有关电推进建模所需全部资源的完整配置说明，请参阅教程"第 12 章 电推进（Electric Propulsion）"。

### ElectricTank 资源的方向

ElectricTank 支持方向和位置设置。位置是硬件坐标系原点的位置，在航天器本体坐标系中表达。方向表示为方向余弦矩阵，最初由用户以 Direction 和 SecondDirection 分量提供的两个不共线矢量计算得出。以本体坐标表达的硬件坐标系的三个轴按如下方式计算：

1. 归一化 **z** 和 **v**，其中 **z** 由 Direction 表示，**v** 为 SecondDirection 矢量。
2. 计算法向 N = z × v 及其模 m。
3. 验证 **N** 的模不为 0.0，如果过于接近则发出消息。当输入矢量之一为零矢量，或两个矢量共线（包括它们指向相反方向的情况）时，会出现这种情况。
4. **x** = **N** / m
5. **y** = **z** × **x**
6. 旋转矩阵 **R**sb 由 **x** 为第一行、**y** 为第二行、**z** 为第三行构成。该矩阵将矢量从本体坐标系旋转到硬件坐标系。

### 配置贮箱及已挂接贮箱属性时的行为

创建一个默认的 ElectricTank 并将其挂接到 Spacecraft 和 ElectricThruster。

```
%  Create the ElectricTank Resource
Create ElectricTank aTank
aTank.AllowNegativeFuelMass = false
aTank.FuelMass = 756

%  Create an ElectricThruster and assign it a ElectricTank
Create ElectricThruster aThruster
aThruster.Tank = {aTank}

%  Add the ElectricTank and Thruster to a Spacecraft
Create Spacecraft aSpacecraft
aSpacecraft.Tanks = {aTank}
aSpacecraft.Thrusters = {aThruster}
```

说明：上述脚本创建电推进贮箱 aTank、电推力器 aThruster（关联 aTank），并将二者挂接到航天器 aSpacecraft。

如下所示，设置和获取父资源与克隆资源的属性时有一些细微差别。在上例中，`aTank` 是父 ElectricTank 资源，而字段 `aSpacecraft.Tanks` 中填充的是 `aTank` 的克隆副本。

创建第二个航天器，并使用与上例相同的过程挂接一个燃料贮箱。将父资源 `aTank` 中的 FuelMass 设为 900 kg。

```
%  Add the ElectricTank and ElectricThruster to a second Spacecraft
Create Spacecraft bSpacecraft
bSpacecraft.Tanks = {aTank}
bSpacecraft.Thrusters = {aThruster}
aTank.FuelMass = 900    %Can be performed in both resource and 
                        %command modes
```

说明：创建第二个航天器 bSpacecraft 并挂接同一贮箱/推力器，然后将父贮箱 FuelMass 改为 900 kg（可在资源模式或命令模式下执行）。

注意，在上例中，设置父资源 `aTank` 的值会同时改变两个克隆燃料贮箱资源中的燃料质量值。更具体地说，`aSpacecraft.aTank.FuelMass` 和 `bSpacecraft.aTank.FuelMass` 的值现在都等于新值 900 kg。注意，父资源的赋值命令 `aTank.FuelMass` 可在资源模式和命令模式下执行。

要仅更改第一个创建的航天器 aSpacecraft 中的燃料质量值，执行以下操作。

```
%  Create the Fuel Tank Resource
BeginMissionSequence
aTank.FuelMass = 756   %Fuel tank mass in both s/c set back to default
aSpacecraft.aTank.FuelMass = 1000 %Can only be performed in command mode.
```

说明：先将父贮箱 FuelMass 恢复为 756（两个航天器中的克隆贮箱随之恢复默认值），再单独将 aSpacecraft 上克隆贮箱的燃料质量设为 1000 kg（只能在命令模式下执行）。

执行上例中的命令后，`aSpacecraft.aTank.FuelMass` 的值为 1000 kg，而 `bSpacecraft.aTank.FuelMass` 的值为 756 kg。注意，克隆资源的赋值命令 `aSpacecraft.aTank.FuelMass` 只能在命令模式下执行。

#### 注意：AllowNegativeFuelMass 标志的值会影响迭代过程

默认情况下，GMAT 不允许燃料质量为负。但是，在定靶等迭代过程中，求解器偶尔会尝试导致燃料完全耗尽的机动参数值。使用默认贮箱设置时，这将抛出异常并停止运行，除非将 AllowNegativeFuelMass 标志设为 true。GMAT 不允许航天器总质量为负。如果 DryMass + FuelMass 为负，GMAT 将抛出异常并停止。

## 示例

创建一个默认的 ElectricTank 并将其挂接到 Spacecraft 和 ElectricThruster。

```
%  Create the ElectricTank Resource
Create ElectricTank aTank
aTank.AllowNegativeFuelMass = false
aTank.FuelMass = 756

%  Create an ElectricThruster and assign it a ElectricTank
Create ElectricThruster aThruster
aThruster.Tank = {aTank}

%  Add the ElectricTank and ElectricThruster to a Spacecraft
Create Spacecraft aSpacecraft
aSpacecraft.Tanks = {aTank}
aSpacecraft.Thrusters = {aThruster}   

BeginMissionSequence
```

说明：本示例创建默认电推进贮箱 aTank，创建电推力器 aThruster 并关联 aTank，最后将贮箱和推力器挂接到航天器 aSpacecraft。
