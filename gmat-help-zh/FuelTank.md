# 贮箱（ChemicalTank）
> 译自 GMAT R2026a 帮助文档 FuelTank.html

**ChemicalTank** —— 化学燃料贮箱模型

## 描述

ChemicalTank 是贮箱的热力学模型，是有限推力弧段建模或使用质量消耗的脉冲机动所必需的。贮箱的热力学性质使用玻意耳定律（Boyle's Law）建模，并假设燃料消耗时贮箱内温度不变。要使用 ChemicalTank，必须先创建贮箱，然后将其挂接到所需的 Spacecraft 并与 ChemicalThruster 关联，如下例所示。

另请参阅：ImpulsiveBurn、ChemicalThruster

## 字段

| 字段 | 描述 |
|------|------|
| **AllowNegativeFuelMass** | 此字段允许 ChemicalTank 具有负的燃料质量，这在优化和定靶序列收敛之前可能有用。此字段不能在任务序列中修改。<br>数据类型：Boolean；允许值：true、false；访问：set；默认值：false；单位：N/A；接口：GUI、脚本 |
| **DirectionX** | ChemicalTank 方向主矢量在本体坐标系中的 X 分量。与次方向元素结合使用以计算方向。<br>数据类型：Real；允许值：实数；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **DirectionY** | ChemicalTank 方向主矢量在本体坐标系中的 Y 分量。与次方向元素结合使用以计算方向。<br>数据类型：Real；允许值：实数；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **DirectionZ** | ChemicalTank 方向主矢量在本体坐标系中的 Z 分量。与次方向元素结合使用以计算方向。<br>数据类型：Real；允许值：实数；访问：set；默认值：1；单位：N/A；接口：脚本 |
| **FuelCenterOfMassX** | 燃料质心在硬件坐标系中的 X 分量。<br>数据类型：Real；允许值：任意实数；访问：set、get；默认值：0.0；单位：meters；接口：GUI、脚本 |
| **FuelCenterOfMassY** | 燃料质心在硬件坐标系中的 Y 分量。<br>数据类型：Real；允许值：任意实数；访问：set、get；默认值：0.0；单位：meters；接口：GUI、脚本 |
| **FuelCenterOfMassZ** | 燃料质心在本体坐标系中的 Z 分量。<br>数据类型：Real；允许值：任意实数；访问：set、get；默认值：0.0；单位：meters；接口：GUI、脚本 |
| **FuelDensity** | 燃料的密度。<br>数据类型：Real；允许值：Real > 0；访问：set、get；默认值：1260；单位：kg/m^3；接口：GUI、脚本 |
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
| **Pressure** | 贮箱中的压力。<br>数据类型：Real；允许值：Real > 0；访问：set、get；默认值：1500；单位：kPa；接口：GUI、脚本 |
| **PressureModel** | 压力模型描述燃料消耗时 ChemicalTank 中压力的变化方式。此字段不能在任务序列中修改。<br>数据类型：枚举；允许值：PressureRegulated（压力调节）、BlowDown（落压式）；访问：set；默认值：PressureRegulated；单位：N/A；接口：GUI、脚本 |
| **RefTemperature** | 加注燃料时贮箱的温度。<br>数据类型：Real；允许值：Real > -273.15 且 \|Real\| > 0.01；访问：set、get；默认值：20；单位：C；接口：GUI、脚本 |
| **SecondDirectionX** | 在本体坐标系中表达的、用于确定硬件绕方向矢量姿态的矢量的 X 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **SecondDirectionY** | 在本体坐标系中表达的、用于确定硬件绕方向矢量姿态的矢量的 Y 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：-1；单位：N/A；接口：脚本 |
| **SecondDirectionZ** | 在本体坐标系中表达的、用于确定硬件绕方向矢量姿态的矢量的 Z 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **Temperature** | 贮箱中燃料和气枕（ullage）的温度。GMAT 目前假设气枕和燃料始终处于相同温度。<br>数据类型：Real；允许值：Real > -273.15；访问：set、get；默认值：20；单位：C；接口：GUI、脚本 |
| **Volume** | 贮箱的容积。GMAT 会检查输入的贮箱容积是否大于贮箱中所装燃料的计算容积，如果计算出的燃料容积大于输入的贮箱容积，则抛出异常。<br>数据类型：Real；允许值：Real > 0 且计算燃料容积 < 输入贮箱容积；访问：set、get；默认值：0.75；单位：m^3；接口：GUI、脚本 |

## GUI

ChemicalTank 对话框允许您指定燃料贮箱的属性，包括质心、转动惯量、燃料质量、密度和温度，以及贮箱压力和容积。ChemicalTank 对话框的布局如下所示。

> [图：ChemicalTank 对话框布局]

ChemicalThruster 资源与 ChemicalTank 资源密切相关，因此也在此讨论。ChemicalThruster 对话框允许您指定推力器的属性，包括推力加速度方向矢量的坐标系、推力量级和 Isp。ChemicalThruster 对话框的布局如下所示。

> [图：ChemicalThruster 对话框布局]

执行有限推力弧段时，通常需要建模燃料消耗。为此，选中 Decrement Mass 按钮，然后选择先前创建的 ChemicalTank，如下所示。

> [图：在 ChemicalThruster 对话框中勾选 Decrement Mass 并选择贮箱]

至此，我们已创建了 ChemicalTank 和 ChemicalThruster，并将 ChemicalTank 与 ChemicalThruster 关联。但还没有完成。我们必须告诉 GMAT 要将 ChemicalTank 和 ChemicalThruster 挂接到特定的航天器上。为此，双击 Spacecraft 资源下所需的航天器，打开相应的 GUI 面板。然后点击 Tanks 选项卡，显示以下 GUI 界面。

> [图：Spacecraft 对话框的 Tanks 选项卡]

接下来，选择所需的 ChemicalTank，使用右箭头按钮将 ChemicalTank 挂接到航天器。然后点击 Apply 按钮，如下所示。

> [图：将贮箱挂接到航天器]

类似地，要将 ChemicalThruster 挂接到航天器，双击 Spacecraft 资源下所需的航天器，然后选择 Actuators 选项卡。接着选择所需的推力器，使用右箭头将推力器挂接到航天器。最后点击 Apply 按钮，如下所示。

> [图：将推力器挂接到航天器]

## 备注

### ChemicalTank 资源与机动的配合使用

ChemicalTank 与脉冲机动和有限推力机动均可结合使用。要实现脉冲机动，必须先创建 ImpulsiveBurn 资源，并（可选地）将 ChemicalTank 与其关联。实际的脉冲机动使用 Maneuver 命令实现。有关 ChemicalTank 资源如何与脉冲机动结合使用的完整示例，请参阅 Maneuver 命令文档。

要实现有限推力机动，必须首先创建 ChemicalThruster 和 FiniteBurn 资源。还必须将 ChemicalTank 与 ChemicalThruster 资源关联，并将 Thruster 与 FiniteBurn 资源关联。实际的有限推力机动使用 BeginFiniteBurn/EndFiniteBurn 命令实现。有关 ChemicalTank 资源如何与有限推力机动结合使用的完整示例，请参阅 BeginFiniteBurn/EndFiniteBurn 命令文档。

### ChemicalTank 资源的方向

ChemicalTank 支持方向和位置设置。位置是硬件坐标系原点的位置，在航天器本体坐标系中表达。方向表示为方向余弦矩阵，最初由用户以 Direction 和 SecondDirection 分量提供的两个不共线矢量计算得出。以本体坐标表达的硬件坐标系的三个轴按如下方式计算：

1. 归一化 **z** 和 **v**，其中 **z** 由 Direction 表示，**v** 为 SecondDirection 矢量。
2. 计算法向 N = z × v 及其模 m。
3. 验证 **N** 的模不为 0.0，如果过于接近则发出消息。当输入矢量之一为零矢量，或两个矢量共线（包括它们指向相反方向的情况）时，会出现这种情况。
4. **x** = **N** / m
5. **y** = **z** × **x**
6. 旋转矩阵 **R**sb 由 **x** 为第一行、**y** 为第二行、**z** 为第三行构成。该矩阵将矢量从本体坐标系旋转到硬件坐标系。

### 配置贮箱及已挂接贮箱属性时的行为

创建一个默认的 ChemicalTank 并将其挂接到 Spacecraft 和 ChemicalThruster。

```
%  Create the ChemicalTank Resource
Create ChemicalTank aTank
aTank.AllowNegativeFuelMass = false
aTank.FuelMass = 756
aTank.Pressure = 1500
aTank.Temperature = 20
aTank.RefTemperature = 20
aTank.Volume = 0.75
aTank.FuelDensity = 1260
aTank.PressureModel = PressureRegulated
%  Create a ChemicalThruster and assign it a ChemicalTank
Create ChemicalThruster aThruster
aThruster.Tank = {aTank}

%  Add the ChemicalTank and ChemicalThruster to a Spacecraft
Create Spacecraft aSpacecraft
aSpacecraft.Tanks = {aTank}
aSpacecraft.Thrusters = {aThruster}
```

说明：上述脚本创建贮箱 aTank、推力器 aThruster（关联 aTank），并将二者挂接到航天器 aSpacecraft。

如下所示，设置和获取父资源与克隆资源的属性时有一些细微差别。在上例中，`aTank` 是父 ChemicalTank 资源，而字段 `aSpacecraft.Tanks` 中填充的是 `aTank` 的克隆副本。

创建第二个航天器，并使用与上例相同的过程挂接一个燃料贮箱。将父资源 `aTank` 中的 FuelMass 设为 900 kg。

```
%  Add the ChemicalTank and ChemicalThruster to a second Spacecraft
Create Spacecraft bSpacecraft
bSpacecraft.Tanks = {aTank}
bSpacecraft.Thrusters = {aThruster}
aTank.FuelMass = 900    %Can be performed in both resource and 
                        %command modes
```

说明：将父贮箱 FuelMass 改为 900 kg（可在资源模式或命令模式下执行）。

注意，在上例中，设置父资源 `aTank` 的值会同时改变两个克隆燃料贮箱资源中的燃料质量值。更具体地说，`aSpacecraft.aTank.FuelMass` 和 `bSpacecraft.aTank.FuelMass` 的值现在都等于新值 900 kg。注意，父资源的赋值命令 `aTank.FuelMass` 可在资源模式和命令模式下执行。

要仅更改第一个创建的航天器 aSpacecraft 中的燃料质量值，执行以下操作。

```
%  Create the Fuel Tank Resource
aTank.FuelMass = 756   %Fuel tank mass in both s/c set back to default
aSpacecraft.aTank.FuelMass = 1000 %Can only be performed in command mode.
```

说明：先将父贮箱 FuelMass 恢复为 756（两个航天器中的克隆贮箱随之恢复默认值），再单独将 aSpacecraft 上克隆贮箱的燃料质量设为 1000 kg（只能在命令模式下执行）。

执行上例中的命令后，`aSpacecraft.aTank.FuelMass` 的值为 1000 kg，而 `bSpacecraft.aTank.FuelMass` 的值为 756 kg。注意，克隆资源的赋值命令 `aSpacecraft.aTank.FuelMass` 只能在命令模式下执行。

#### 注意：AllowNegativeFuelMass 标志的值会影响迭代过程

默认情况下，GMAT 不允许燃料质量为负。但是，在定靶等迭代过程中，求解器偶尔会尝试导致燃料完全耗尽的机动参数值。使用默认贮箱设置时，这将抛出异常并停止运行，除非将 AllowNegativeFuelMass 标志设为 true。GMAT 不允许航天器总质量为负。如果 DryMass + FuelMass 为负，GMAT 将抛出异常并停止。

## 示例

创建一个默认的 ChemicalTank 并将其挂接到 Spacecraft 和 ChemicalThruster。

```
%  Create the Fuel Tank Resource
Create ChemicalTank aTank
aTank.AllowNegativeFuelMass = false
aTank.FuelMass = 756
aTank.Pressure = 1500
aTank.Temperature = 20
aTank.RefTemperature = 20
aTank.Volume = 0.75
aTank.FuelDensity = 1260
aTank.PressureModel = PressureRegulated

%  Create a ChemicalThruster and assign it a ChemicalTank
Create ChemicalThruster aThruster
aThruster.Tank = {aTank}

%  Add the ChemicalTank and ChemicalThruster to a Spacecraft
Create Spacecraft aSpacecraft
aSpacecraft.Tanks = {aTank}
aSpacecraft.Thrusters = {aThruster}

BeginMissionSequence
```

说明：本示例创建默认贮箱 aTank（设置燃料质量、压力、温度、参考温度、容积、密度和压力模型），创建推力器 aThruster 并关联 aTank，最后将贮箱和推力器挂接到航天器 aSpacecraft。
