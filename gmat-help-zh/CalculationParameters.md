# 计算参数（CalculationParameters）

> 译自 GMAT R2026a 帮助文档 CalculationParameters.html

计算参数 —— 可供命令和输出使用的资源属性。

## 说明（Description）

参数是命名的资源属性，用于获取数据，供任务序列（Mission Sequence）命令或输出资源使用。有些参数（如 Spacecraft 的 `Altitude` 参数）是计算值，只能用于读取数据，不能直接设置。另一些参数（如 ImpulsiveBurn 的 `Element1` 参数）与资源字段同名，既可设置数据也可读取数据。参数与资源字段的区别在于其额外的功能：字段是静态的资源属性，通常在初始化时（或在 GUI 的资源树中）设置；而参数可以即时计算，并可用于绘图、报告和数学表达式。

参数分为四类：依赖中心天体的参数（central-body-dependent）、依赖坐标系的参数（coordinate-system-dependent）、附属硬件参数（attached-hardware）和独立参数（standalone）。独立参数最简单，没有依赖项。Spacecraft 的 `ElapsedSecs` 参数即为一例，直接引用为 `Spacecraft.ElapsedSecs`。

顾名思义，依赖中心天体的参数，其值取决于所选的天体。Spacecraft 的 `Altitude` 参数即为一例。引用该参数时必须指定一个中心天体，如 `Spacecraft.Mars.Altitude`。任何内置中心天体，或用户定义的 Asteroid（小行星）、Comet（彗星）、Moon（卫星）、Planet（行星），都可作为依赖项。

类似地，依赖坐标系的参数，其值取决于所选的坐标系。Spacecraft 的 `DEC` 参数即为一例。引用该参数时必须指定 CoordinateSystem 资源的名称，如 `Spacecraft.EarthFixed.DEC`。任何默认的或用户自定义的 CoordinateSystem 资源都可作为依赖项。

如果在读取参数值时使用了依赖项（如下面的语句），则 `Altitude` 的值先在火星（Mars）处计算，再赋给变量 `x`。如果省略依赖项，除非另有说明，否则默认采用 Earth 和 EarthMJ2000Eq。

```gmat
x = DefaultSC.Mars.Altitude
```

如果在设置参数值时使用了依赖项，则先根据依赖项的值换算该参数，然后再赋值。例如在下面的语句中，`SMA` 的值先在火星（Mars）处计算，然后在该上下文中被设为 `10000`。如果设置时省略依赖项，则默认采用父资源的中心天体或坐标系（本例中为 DefaultSC）。

```gmat
DefaultSC.Mars.SMA = 10000
```

附属硬件参数没有依赖项，但其本身依赖于挂载到 Spacecraft 上。ChemicalTank 和 ChemicalThruster 的参数即属此类。ChemicalTank 的 `FuelMass` 参数，必须先将该 ChemicalTank 挂载到 Spacecraft 上才能引用。引用方式为：`Spacecraft.FuelTank.FuelMass`。

各个参数因资源而异，详见下文各表。GUI 提供了对所有参数通用的参数选择界面，见下文"GUI"一节。

**另请参阅**：Array、ChemicalTank、ImpulsiveBurn、FiniteBurn、Spacecraft、String、ChemicalThruster、Variable

## GUI

在 GMAT 中，参数可在多处用作输入，例如 ReportFile 和 XYPlot 资源，以及 If/Else、Propagate 和 Report 命令。在 GUI 中，这些都使用一个名为 ParameterSelectDialog 的通用界面，可交互式地选择参数。基本的 ParameterSelectDialog 窗口如下所示：

（图：ParameterSelectDialog 窗口，见原文档图片 `Resource_CalculationParameters_GUI.png`）

ParameterSelectDialog 窗口用于构建参数及其依赖项，供命令或资源使用。不同资源和命令对可用参数的类型有不同要求，因此 ParameterSelectDialog 会随使用位置的不同而略有差异。本节先介绍通用界面，再说明特定于资源或命令的例外情况。

### 通用用法（General Usage）

选择参数的第一步，是在左上方的 **Object Type**（对象类型）列表中选择对象（或资源）类型。该列表中可出现七种类型：Spacecraft、SpacePoint、ImpulsiveBurn、FiniteBurn、Variable、Array 和 String。

选定类型后，**Object List**（对象列表）框中会列出该类型的所有现有资源。在此列表中选择要引用的具体资源。

若选择 Spacecraft 类型，Object List 下方会出现 **Attached Hardware List**（附属硬件列表），显示挂载到所选 Spacecraft 上的硬件（如 ChemicalTank 或 ChemicalThruster 资源）。若选择 Array 类型，则出现 **Row**（行）和 **Col**（列）输入框，用于指定行和列以选择单个数组元素；勾选 **Select Entire Object**（选择整个对象）可选择整个数组。

选定资源后，**Object Properties**（对象属性）列表会列出该资源提供的所有可用参数。有些资源（如 Variable 或 Array 的实例）本身就是参数，因此该列表保持为空。

具有不同依赖类型的参数混合显示在 Object Properties 列表中。选中某个参数后，相应的依赖项（如有）会显示在列表下方。例如：选中 Spacecraft 的 `AOP` 参数后，会出现 CoordinateSystem 列表；选中 Spacecraft 的 `Apoapsis` 参数后，会出现 Central Body（中心天体）列表；而选中 Spacecraft 的 `Cd` 参数后，不会出现依赖列表。要从 Object Properties 列表中选择连续范围的参数，可按住 Shift 键并点击范围的另一端点；要选择多个不连续的参数，可按住 Ctrl 键逐个选择。

要选择参数，请依次选择适当的 Object Type、Object List 或 Attached Hardware List 中的具体资源、Object Properties 列表中所需的参数以及所需的依赖项，然后将其添加到右侧的 **Selected Value(s)**（已选值）列表中。有六个按钮可用于管理该列表：

- **UP**：将 Selected Value(s) 列表中的所选项上移一位（如允许）。
- **DN**：将 Selected Value(s) 列表中的所选项下移一位（如允许）。
- **->**：将 Object Properties 列表中的所选项添加到 Selected Value(s) 列表。
- **<-**：移除 Selected Value(s) 列表中的所选项。
- **=>**：将所有项添加到 Selected Value(s) 列表。
- **<=**：移除 Selected Value(s) 列表中的所有项。

完成后，Selected Value(s) 列表即为最终选定的参数。点击 **OK** 接受选择。

Selected Value(s) 列表的顺序在某些场合（如 ReportFile 的 Add 字段）是有意义的，在其他场合则无关。详见各资源或命令的文档。

### 特殊注意事项（Special Considerations）

有些资源和命令（如 Propagate 命令的 Parameter 参数）只接受单个参数作为输入；此时 ParameterSelectDialog 只允许 Selected Value(s) 列表中有一个参数，且不能使用 **UP**、**DN** 和 **=>** 按钮。

在某些情况下（如 Vary 命令中），只能使用同时也是字段的参数（即可在 Mission Sequence 中设置的参数）。此时 Object Properties 列表中只显示允许的参数。

在 Propagate 命令的 Parameter 参数中，只能使用 Spacecraft 的参数。此时 Object Type 列表中只显示 Spacecraft。

## 参数（Parameters）

各参数按资源类型分组列于下表。表中各列含义：

- **可设置**：该参数是否可直接赋值（Y=是，N=否）。
- **可绘图**：该参数是否可用于 XYPlot 等绘图输出。
- **依赖**：读取/计算该参数时必须指定的依赖项。"坐标系"表示需指定 CoordinateSystem 资源；"天体"表示需指定中心天体（CelestialBody）；"力模型"表示需指定 ForceModel 资源；"无"表示无依赖。省略依赖项时，默认采用 Earth 和 EarthMJ2000Eq（除非另有说明）。
- **单位**：单位符号保留英文原文，不作翻译。

### Spacecraft（航天器）

| 参数 | 可设置 | 可绘图 | 说明 | 数据类型 | 依赖 | 单位 |
| --- | --- | --- | --- | --- | --- | --- |
| `A1Gregorian` | 是 | 否 | A.1 时间系统、格里历（Gregorian）格式的航天器历元。 | String | 无 | (N/A) |
| `A1ModJulian` | 是 | 是 | A.1 时间系统、约化儒略日（Modified Julian）格式的航天器历元。 | Real | 无 | d |
| `Acceleration`（加速度） | 否 | 是 | 相对于惯性系的总加速度，使用依赖项所选的 ForceModel 计算。 | Real | 力模型 | km/s^2 |
| `AccelerationX` | 否 | 是 | 相对于惯性系的加速度 x 分量，使用依赖项所选的 ForceModel 计算。 | Real | 力模型 | km/s^2 |
| `AccelerationY` | 否 | 是 | 相对于惯性系的加速度 y 分量，使用依赖项所选的 ForceModel 计算。 | Real | 力模型 | km/s^2 |
| `AccelerationZ` | 否 | 是 | 相对于惯性系的加速度 z 分量，使用依赖项所选的 ForceModel 计算。 | String（原文如此） | 力模型 | km/s^2 |
| `AltEquinoctialP` | 是 | 是 | 参见 Spacecraft.AltEquinoctialP。 | Real | 坐标系 | 无 |
| `AltEquinoctialQ` | 是 | 是 | 参见 Spacecraft.AltEquinoctialQ。 | Real | 坐标系 | 无 |
| `Altitude`（高度） | 否 | 是 | 到指定天体表面在星下点（sub-satellite point）处切平面的距离。GMAT 假定天体为椭球体。 | Real | 天体 | km |
| `AngularVelocityX`（角速度 X 分量） | 是 | 是 | 参见 Spacecraft.AngularVelocityX。 | Real | 无 | deg/s |
| `AngularVelocityY`（角速度 Y 分量） | 是 | 是 | 参见 Spacecraft.AngularVelocityY。 | Real | 无 | deg/s |
| `AngularVelocityZ`（角速度 Z 分量） | 是 | 是 | 参见 Spacecraft.AngularVelocityZ。 | Real | 无 | deg/s |
| `AOP`（近地点幅角） | 是 | 是 | 参见 Spacecraft.AOP。输出范围：0° ≤ AOP < 360°。 | Real | 坐标系 | deg |
| `Apoapsis`（远拱点） | 否 | 是 | 当航天器位于轨道远拱点时等于零的参数。该参数只能用作 Propagate 命令的停止条件。 | Real | 天体 | 无 |
| `AtmosDensity`（大气密度） | 否 | 是 | 当前 Spacecraft 历元和位置处的大气密度，使用依赖项所选的 ForceModel 计算。 | String（原文如此） | 力模型 | kg/km^3 |
| `AZI`（方位角） | 是 | 是 | 参见 Spacecraft.AZI。输出范围：-180° ≤ AZI ≤ 180°。 | Real | 坐标系 | deg |
| `BdotR`（B 平面 B·R） | 否 | 是 | B 平面 B·R 的模。GMAT 在依赖项指定的坐标系中计算 B 平面坐标。在许多实现中，B 平面坐标是在伪旋转坐标系中计算的，变换速度矢量时不施加 ω×r 项；而 GMAT 在速度变换中会施加 ω×r 项。在惯性系中计算 B 平面坐标时，该项恒为零。对于旋转坐标系（如太阳-地球双体旋转系），包含 ω×r 的影响很小，但在不同坐标系间比较结果时可以察觉。当所选坐标系的旋转"很快"时，数值可能会有显著差异。 | Real | 坐标系 | km |
| `BdotT`（B 平面 B·T） | 否 | 是 | B 平面 B·T 的模。有关本计算的说明参见 `BdotR` 参数。 | Real | 坐标系 | km |
| `BetaAngle`（β 角） | 否 | 是 | 轨道面与天体指向太阳的矢量之间的夹角。输出范围：-90° ≤ BetaAngle ≤ 90°。 | Real | 天体 | deg |
| `BrouwerLongAOP`（Brouwer 长周期近地点幅角） | 是 | 是 | 参见 Spacecraft.BrouwerLongAOP。输出范围：0° ≤ BrouwerLongAOP ≤ 360°。 | Real | 坐标系 | deg |
| `BrouwerLongECC`（Brouwer 长周期偏心率） | 是 | 是 | 参见 Spacecraft.BrouwerLongECC。 | Real | 坐标系 | 无 |
| `BrouwerLongINC`（Brouwer 长周期轨道倾角） | 是 | 是 | 参见 Spacecraft.BrouwerLongINC。输出范围：0° ≤ BrouwerLongINC ≤ 180°。 | Real | 坐标系 | deg |
| `BrouwerLongMA`（Brouwer 长周期平近点角） | 是 | 是 | 参见 Spacecraft.BrouwerLongMA。输出范围：0° ≤ BrouwerLongMA ≤ 360°。 | Real | 坐标系 | deg |
| `BrouwerLongRAAN`（Brouwer 长周期升交点赤经） | 是 | 是 | 参见 Spacecraft.BrouwerLongRAAN。输出范围：0° ≤ BrouwerLongRAAN ≤ 360°。 | Real | 坐标系 | deg |
| `BrouwerLongSMA`（Brouwer 长周期半长轴） | 是 | 是 | 参见 Spacecraft.BrouwerLongSMA。 | Real | 坐标系 | km |
| `BrouwerShortAOP`（Brouwer 短周期近地点幅角） | 是 | 是 | 参见 Spacecraft.BrouwerShortAOP。输出范围：0° ≤ BrouwerShortAOP ≤ 360°。 | Real | 坐标系 | deg |
| `BrouwerShortECC`（Brouwer 短周期偏心率） | 是 | 是 | 参见 Spacecraft.BrouwerShortECC。 | Real | 坐标系 | 无 |
| `BrouwerShortINC`（Brouwer 短周期轨道倾角） | 是 | 是 | 参见 Spacecraft.BrouwerShortINC。输出范围：0° ≤ BrouwerShortINC ≤ 180°。 | Real | 坐标系 | deg |
| `BrouwerShortMA`（Brouwer 短周期平近点角） | 是 | 是 | 参见 Spacecraft.BrouwerShortMA。输出范围：0° ≤ BrouwerShortMA ≤ 360°。 | Real | 坐标系 | deg |
| `BrouwerShortRAAN`（Brouwer 短周期升交点赤经） | 是 | 是 | 参见 Spacecraft.BrouwerShortRAAN。输出范围：0° ≤ BrouwerShortRAAN ≤ 360°。 | Real | 坐标系 | deg |
| `BrouwerShortSMA`（Brouwer 短周期半长轴） | 是 | 是 | 参见 Spacecraft.BrouwerShortSMA。 | Real | 坐标系 | km |
| `BurnTorque`（推力力矩） | 否 | 否 | 推力器点火在航天器上产生的绕其质心的力矩。力矩在航天器本体系中报告。 | Real Array (1x3) | 力模型 | N*m |
| `BVectorAngle`（B 矢量角） | 否 | 是 | B 平面中 B 矢量与 T 单位矢量之间的夹角。有关本计算的说明参见 `BdotR` 参数。输出范围：-180° ≤ BVectorAngle ≤ 180°。 | Real | 坐标系 | deg |
| `BVectorMag`（B 矢量模） | 否 | 是 | B 平面 B 矢量的模。有关本计算的说明参见 `BdotR` 参数。 | Real | 坐标系 | km |
| `C3Energy`（C3 能量） | 否 | 是 | C3（特征）能量。 | Real | 天体 | MJ/kg (km^2/s^2) |
| `Cd`（阻力系数） | 是 | 是 | 参见 Spacecraft.Cd。 | Real | 无 | 无 |
| `Cr`（光压系数） | 是 | 是 | 参见 Spacecraft.Cr。 | Real | 无 | 无 |
| `CurrA1MJD` | 是 | 是 | 已弃用（Deprecated）。A.1 时间系统、约化儒略日格式的航天器历元。 | Real | 无 | d |
| `DCM11`（方向余弦矩阵元素 11） | 是 | 是 | 参见 Spacecraft.DCM11。 | Real | 无 | 无 |
| `DCM12`（方向余弦矩阵元素 12） | 是 | 是 | 参见 Spacecraft.DCM12。 | Real | 无 | 无 |
| `DCM13`（方向余弦矩阵元素 13） | 是 | 是 | 参见 Spacecraft.DCM13。 | Real | 无 | 无 |
| `DCM21`（方向余弦矩阵元素 21） | 是 | 是 | 参见 Spacecraft.DCM21。 | Real | 无 | 无 |
| `DCM22`（方向余弦矩阵元素 22） | 是 | 是 | 参见 Spacecraft.DCM22。 | Real | 无 | 无 |
| `DCM23`（方向余弦矩阵元素 23） | 是 | 是 | 参见 Spacecraft.DCM23。 | Real | 无 | 无 |
| `DCM31`（方向余弦矩阵元素 31） | 是 | 是 | 参见 Spacecraft.DCM31。 | Real | 无 | 无 |
| `DCM32`（方向余弦矩阵元素 32） | 是 | 是 | 参见 Spacecraft.DCM32。 | Real | 无 | 无 |
| `DCM33`（方向余弦矩阵元素 33） | 是 | 是 | 参见 Spacecraft.DCM33。 | Real | 无 | 无 |
| `DEC`（赤纬） | 是 | 是 | 参见 Spacecraft.DEC。输出范围：-90° ≤ DEC ≤ 90°。 | Real | 坐标系 | deg |
| `DECV`（速度赤纬） | 是 | 是 | 参见 Spacecraft.DECV。输出范围：-90° ≤ DECV ≤ 90°。 | Real | 坐标系 | deg |
| `Delaunayg`（德洛内变量 g） | 是 | 是 | 参见 Spacecraft.Delaunayg。输出范围：0° ≤ Delaunayg < 360°。 | Real | 坐标系 | deg |
| `DelaunayG`（德洛内变量 G） | 是 | 是 | 参见 Spacecraft.DelaunayG。 | Real | 坐标系 | km^2/s |
| `Delaunayh`（德洛内变量 h） | 是 | 是 | 参见 Spacecraft.Delaunayh。输出范围：0° ≤ Delaunayh < 360°。 | Real | 坐标系 | deg |
| `DelaunayH`（德洛内变量 H） | 是 | 是 | 参见 Spacecraft.DelaunayH。 | Real | 坐标系 | km^2/s |
| `Delaunayl`（德洛内变量 l） | 是 | 是 | 参见 Spacecraft.Delaunayl。输出范围：0° ≤ Delaunayl < 360°。 | Real | 坐标系 | deg |
| `DelaunayL`（德洛内变量 L） | 是 | 是 | 参见 Spacecraft.DelaunayL。 | Real | 坐标系 | km^2/s |
| `DLA`（出射渐近线赤纬） | 否 | 是 | 出射双曲线渐近线的赤纬（Declination of the outgoing hyperbolic asymptote）。输出范围：-90° ≤ DLA ≤ 90°。 | Real | 坐标系 | deg |
| `DragArea`（阻力面积） | 是 | 是 | 参见 Spacecraft.DragArea。 | Real | 无 | m^2 |
| `DryCenterOfMassX`（干质心 X） | 是 | 是 | 参见 Spacecraft.DryCenterOfMassX。 | Real | 无 | m |
| `DryCenterOfMassY`（干质心 Y） | 是 | 是 | 参见 Spacecraft.DryCenterOfMassY。 | Real | 无 | m |
| `DryCenterOfMassZ`（干质心 Z） | 是 | 是 | 参见 Spacecraft.DryCenterOfMassZ。 | Real | 无 | m |
| `DryMass`（干质量） | 是 | 是 | 参见 Spacecraft.DryMass。 | Real | 无 | kg |
| `DryMomentOfInertiaXX`（干转动惯量 XX） | 是 | 是 | 参见 Spacecraft.DryMomentOfInertiaXX。 | Real | 无 | kg-m^2 |
| `DryMomentOfInertiaXY`（干转动惯量 XY） | 是 | 是 | 参见 Spacecraft.DryMomentOfInertiaXY。 | Real | 无 | kg-m^2 |
| `DryMomentOfInertiaXZ`（干转动惯量 XZ） | 是 | 是 | 参见 Spacecraft.DryMomentOfInertiaXZ。 | Real | 无 | kg-m^2 |
| `DryMomentOfInertiaYY`（干转动惯量 YY） | 是 | 是 | 参见 Spacecraft.DryMomentOfInertiaYY。 | Real | 无 | kg-m^2 |
| `DryMomentOfInertiaYZ`（干转动惯量 YZ） | 是 | 是 | 参见 Spacecraft.DryMomentOfInertiaYZ。 | Real | 无 | kg-m^2 |
| `DryMomentOfInertiaZZ`（干转动惯量 ZZ） | 是 | 是 | 参见 Spacecraft.DryMomentOfInertiaZZ。 | Real | 无 | kg-m^2 |
| `EA`（偏近点角） | 否 | 是 | 偏近点角（Eccentric anomaly）。输出范围：0° ≤ EA < 360°。 | Real | 天体 | deg |
| `ECC`（偏心率） | 是 | 是 | 参见 Spacecraft.ECC。输出范围：（原文档空缺）。 | Real | 天体 | 无 |
| `ElapsedDays`（已耗天数） | 否 | 是 | 已耗时间，以天为单位。已耗时间根据上下文计算，详见"耗时参数（Elapsed Time Parameters）"一节。 | Real | 无 | d |
| `ElapsedSecs`（已耗秒数） | 否 | 是 | 已耗时间，以秒为单位。已耗时间根据上下文计算，详见"耗时参数（Elapsed Time Parameters）"一节。 | Real | 无 | s |
| `Energy`（能量） | 否 | 是 | 比轨道能（Specific orbital energy）。 | Real | 天体 | MJ/kg (km^2/s^2) |
| `EquinoctialH`（春分点要素 H） | 是 | 是 | 参见 Spacecraft.EquinoctialH。 | Real | 坐标系 | 无 |
| `EquinoctialHDot` | 否 | 是 | 由摄动力引起的航天器春分点 H 要素的时间变化率。 | Real | 力模型 | s^-1 |
| `EquinoctialK`（春分点要素 K） | 是 | 是 | 参见 Spacecraft.EquinoctialK。 | Real | 坐标系 | 无 |
| `EquinoctialKDot` | 否 | 是 | 由摄动力引起的航天器春分点 K 要素的时间变化率。 | Real | 力模型 | s^-1 |
| `EquinoctialP`（春分点要素 P） | 是 | 是 | 参见 Spacecraft.EquinoctialP。 | Real | 坐标系 | 无 |
| `EquinoctialPDot` | 否 | 是 | 由摄动力引起的航天器春分点 P 要素的时间变化率。 | Real | 力模型 | s^-1 |
| `EquinoctialQ`（春分点要素 Q） | 是 | 是 | 参见 Spacecraft.EquinoctialQ。 | Real | 坐标系 | 无 |
| `EquinoctialQDot` | 否 | 是 | 由摄动力引起的航天器春分点 Q 要素的时间变化率。 | Real | 力模型 | s^-1 |
| `EulerAngle1`（欧拉角 1） | 是 | 是 | 参见 Spacecraft.EulerAngle1。输出范围：0° ≤ EulerAngle1 < 360°。 | Real | 无 | deg |
| `EulerAngle2`（欧拉角 2） | 是 | 是 | 参见 Spacecraft.EulerAngle2。输出范围：0° ≤ EulerAngle2 < 360°。 | Real | 无 | deg |
| `EulerAngle3`（欧拉角 3） | 是 | 是 | 参见 Spacecraft.EulerAngle3。输出范围：0° ≤ EulerAngle3 < 360°。 | Real | 无 | deg |
| `EulerAngleRate1`（欧拉角速率 1） | 是 | 是 | 参见 Spacecraft.EulerAngleRate1。 | Real | 无 | deg/s |
| `EulerAngleRate2`（欧拉角速率 2） | 是 | 是 | 参见 Spacecraft.EulerAngleRate2。 | Real | 无 | deg/s |
| `EulerAngleRate3`（欧拉角速率 3） | 是 | 是 | 参见 Spacecraft.EulerAngleRate3。 | Real | 无 | deg/s |
| `FPA`（飞行路径角） | 是 | 是 | 参见 Spacecraft.FPA。输出范围：0° ≤ FPA ≤ 180°。 | Real | 坐标系 | deg |
| `GravityTorque`（重力力矩） | 否 | 否 | 所选力模型中的重力场和点质量在航天器上产生的绕其质心的力矩。力矩在航天器本体系中报告。 | Real Array (1x3) | 力模型 | N*m |
| `HA`（双曲线近点角） | 否 | 是 | 双曲线近点角（Hyperbolic anomaly）。输出范围：-∞ < HA < ∞。 | Real | 天体 | deg |
| `HMAG`（角动量模） | 否 | 是 | 角动量矢量的模。 | Real | 天体 | km^2/s |
| `HX`（角动量 X 分量） | 否 | 是 | 角动量矢量的 X 分量。 | Real | 坐标系 | km^2/s |
| `HY`（角动量 Y 分量） | 否 | 是 | 角动量矢量的 Y 分量。 | Real | 坐标系 | km^2/s |
| `HZ`（角动量 Z 分量） | 否 | 是 | 角动量矢量的 Z 分量。 | Real | 坐标系 | km^2/s |
| `INC`（轨道倾角） | 是 | 是 | 参见 Spacecraft.INC。输出范围：0° ≤ INC ≤ 180°。 | Real | 坐标系 | deg |
| `IncomingBVAZI`（入射 B 矢量方位角） | 是 | 是 | 参见 Spacecraft.IncomingBVAZI。输出范围：0° ≤ IncomingBVAZI < 360°。 | Real | 坐标系 | deg |
| `IncomingC3Energy`（入射 C3 能量） | 是 | 是 | 参见 Spacecraft.IncomingC3Energy。 | Real | 天体 | MJ/kg (km^2/s^2) |
| `IncomingDHA`（入射渐近线赤纬） | 是 | 是 | 参见 Spacecraft.IncomingDHA。输出范围：-90° ≤ IncomingDHA ≤ 90°。 | Real | 坐标系 | deg |
| `IncomingRadPer`（入射近拱点半径） | 是 | 是 | 参见 Spacecraft.IncomingRadPer。 | Real | 天体 | km |
| `IncomingRHA`（入射渐近线赤经） | 是 | 是 | 参见 Spacecraft.IncomingRHA。输出范围：0° ≤ IncomingRHA < 360°。 | Real | 坐标系 | deg |
| `Latitude`（纬度） | 否 | 是 | 行星测地纬度（Planetodetic latitude）。输出范围：-90° ≤ Latitude ≤ 90°。 | Real | 天体 | deg |
| `Longitude`（经度） | 否 | 是 | 行星测地经度（Planetodetic longitude）。输出范围：-180° ≤ Longitude ≤ 180°。 | Real | 天体 | deg |
| `LST`（地方恒星时） | 否 | 是 | 航天器相对于天体惯性 x 轴的地方恒星时（Local sidereal time）。输出范围：0° ≤ LST < 360°。 | Real | 天体 | deg |
| `MA`（平近点角） | 否 | 是 | 平近点角（Mean anomaly）。输出范围：0° ≤ MA < 360°。 | Real | 天体 | deg |
| `MHA`（子午线时角） | 否 | 是 | 天体固连轴与惯性轴之间的夹角。对地球而言，即格林尼治时角（Greenwich Hour Angle）。输出范围：0° ≤ MHA < 360°。 | Real | 天体 | deg |
| `MLONG`（平经度） | 是 | 是 | 参见 Spacecraft.MLONG。输出范围：0° ≤ MLONG < 360°。 | Real | 坐标系 | deg |
| `MM`（平均运动） | 否 | 是 | 平均运动（Mean motion）。输出范围：（原文档空缺）。 | Real | 天体 | rad/s |
| `ModEquinoctialF`（改进春分点要素 F） | 是 | 是 | 参见 Spacecraft.ModEquinoctialF。 | Real | 坐标系 | 无 |
| `ModEquinoctialG`（改进春分点要素 G） | 是 | 是 | 参见 Spacecraft.ModEquinoctialG。 | Real | 坐标系 | 无 |
| `ModEquinoctialH`（改进春分点要素 H） | 是 | 是 | 参见 Spacecraft.ModEquinoctialH。 | Real | 坐标系 | 无 |
| `ModEquinoctialK`（改进春分点要素 K） | 是 | 是 | 参见 Spacecraft.ModEquinoctialK。 | Real | 坐标系 | 无 |
| `MRP1`（修正罗德里格斯参数 1） | 是 | 是 | 参见 Spacecraft.MRP1。 | Real | 无 | 无 |
| `MRP2`（修正罗德里格斯参数 2） | 是 | 是 | 参见 Spacecraft.MRP2。 | Real | 无 | 无 |
| `MRP3`（修正罗德里格斯参数 3） | 是 | 是 | 参见 Spacecraft.MRP3。 | Real | 无 | 无 |
| `OrbitPeriod`（轨道周期） | 否 | 是 | 密切轨道周期（Osculating orbit period）。 | Real | 天体 | s |
| `OrbitSTM`（轨道状态转移矩阵） | 否 | 否 | 相对于与原点无关的 MJ2000Eq 轴系的状态转移矩阵。 | Array (6×6) | 无 | 无 |
| `OrbitSTMA` | 否 | 否 | 状态转移矩阵的左上象限，相对于与原点无关的 MJ2000Eq 轴系。 | Array (3×3) | 无 | 无 |
| `OrbitSTMB` | 否 | 否 | 状态转移矩阵的右上象限，相对于与原点无关的 MJ2000Eq 轴系。 | Array (3×3) | 无 | 无 |
| `OrbitSTMC` | 否 | 否 | 状态转移矩阵的左下象限，相对于与原点无关的 MJ2000Eq 轴系。 | Array (3×3) | 无 | 无 |
| `OrbitSTMD` | 否 | 否 | 状态转移矩阵的右下象限，相对于与原点无关的 MJ2000Eq 轴系。 | Array (3×3) | 无 | 无 |
| `OrbitTime`（轨道地方时） | 否 | 否 | 当前状态的地方时（Local Time）。 | Real | 坐标系 | 无 |
| `OutgoingBVAZI`（出射 B 矢量方位角） | 是 | 是 | 参见 Spacecraft.OutgoingBVAZI。输出范围：0° ≤ OutgoingBVAZI < 360°。 | Real | 坐标系 | deg |
| `OutgoingC3Energy`（出射 C3 能量） | 是 | 是 | 参见 Spacecraft.OutgoingC3Energy。 | Real | 天体 | MJ/kg (km^2/s^2) |
| `OutgoingDHA`（出射渐近线赤纬） | 是 | 是 | 参见 Spacecraft.OutgoingDHA。输出范围：-90° ≤ OutgoingRHA ≤ 90°（原文如此，范围标注中引用的是 OutgoingRHA）。 | Real | 坐标系 | deg |
| `OutgoingRadPer`（出射近拱点半径） | 是 | 是 | 参见 Spacecraft.OutgoingRadPer。 | Real | 天体 | km |
| `OutgoingRHA`（出射渐近线赤经） | 是 | 是 | 参见 Spacecraft.OutgoingRHA。输出范围：0° ≤ OutgoingRHA < 360°。 | Real | 坐标系 | deg |
| `Periapsis`（近拱点） | 否 | 是 | 当航天器位于轨道近拱点时等于零的参数。该参数只能用作 Propagate 命令的停止条件。 | Real | 天体 | 无 |
| `PlanetodeticAZI`（行星测地方位角） | 是 | 是 | 参见 Spacecraft.PlanetodeticAZI。本参数必须与具有 BodyFixed 轴系的坐标系配合使用。输出范围：-180° ≤ PlanetodeticAZI ≤ 180°。 | Real | 坐标系（BodyFixed 轴系） | deg |
| `PlanetodeticHFPA`（行星测地水平飞行路径角） | 是 | 是 | 参见 Spacecraft.PlanetodeticHFPA。本参数必须与具有 BodyFixed 轴系的坐标系配合使用。输出范围：-90° ≤ PlanetodeticHFPA ≤ 90°。 | Real | 坐标系（BodyFixed 轴系） | deg |
| `PlanetodeticLAT`（行星测地纬度） | 是 | 是 | 参见 Spacecraft.PlanetodeticLAT。本参数必须与具有 BodyFixed 轴系的坐标系配合使用。输出范围：-180° ≤ PlanetodeticLAT ≤ 180°。 | Real | 坐标系（BodyFixed 轴系） | deg |
| `PlanetodeticLON`（行星测地经度） | 是 | 是 | 参见 Spacecraft.PlanetodeticLON。本参数必须与具有 BodyFixed 轴系的坐标系配合使用。输出范围：-180° ≤ PlanetodeticLON ≤ 180°。 | Real | 坐标系（BodyFixed 轴系） | deg |
| `PlanetodeticRMAG`（行星测地位置模） | 是 | 是 | 参见 Spacecraft.PlanetodeticRMAG。本参数必须与具有 BodyFixed 轴系的坐标系配合使用。 | Real | 坐标系（BodyFixed 轴系） | km |
| `PlanetodeticVMAG`（行星测地速度模） | 是 | 是 | 参见 Spacecraft.PlanetodeticVMAG。本参数必须与具有 BodyFixed 轴系的坐标系配合使用。 | Real | 坐标系（BodyFixed 轴系） | km/s |
| `Q1`（四元数分量 1） | 否 | 是 | 参见 Spacecraft.Q1。 | Real | 无 | 无 |
| `Q2`（四元数分量 2） | 否 | 是 | 参见 Spacecraft.Q2。 | Real | 无 | 无 |
| `Q3`（四元数分量 3） | 否 | 是 | 参见 Spacecraft.Q3。 | Real | 无 | 无 |
| `Q4`（四元数分量 4） | 否 | 是 | 参见 Spacecraft.Q4。 | Real | 无 | 无 |
| `Quaternion`（姿态四元数） | 是 | 否 | 姿态四元数（Attitude quaternion）。 | Array (1×4) | 无 | 无 |
| `RA`（赤经） | 是 | 是 | 参见 Spacecraft.RA。输出范围：-180° ≤ RA ≤ 180°。 | Real | 坐标系 | deg |
| `RAAN`（升交点赤经） | 是 | 是 | 参见 Spacecraft.RAAN。输出范围：0° ≤ RAAN < 360°。 | Real | 坐标系 | deg |
| `RadApo`（远拱点半径） | 是 | 是 | 参见 Spacecraft.RadApo。 | Real | 天体 | km |
| `RadPer`（近拱点半径） | 是 | 是 | 参见 Spacecraft.RadPer。 | Real | 天体 | km |
| `RAV`（速度赤经） | 是 | 是 | 参见 Spacecraft.RAV。输出范围：-180° ≤ RAV ≤ 180°。 | Real | 坐标系 | deg |
| `RLA`（出射渐近线赤经） | 否 | 是 | 出射双曲线渐近线的赤经（Right ascension of the outgoing hyperbolic asymptote）。输出范围：-180° ≤ RLA ≤ 180°。 | Real | 坐标系 | deg |
| `RMAG`（位置模） | 是 | 是 | 参见 Spacecraft.RMAG。 | Real | 天体 | km |
| `SemilatusRectum`（半通径） | 是 | 是 | 参见 Spacecraft.SemilatusRectum。 | Real | 天体 | km |
| `SemilatusRectum`（半通径） | 否 | 是 | 密切轨道的半通径（Semilatus rectum）。（译注：该参数在原文档中重复出现两次，此处照原样保留。） | Real | 天体 | km |
| `SMA`（半长轴） | 是 | 是 | 参见 Spacecraft.SMA。 | Real | 天体 | km |
| `SMADot`（半长轴变化率） | 否 | 是 | 由摄动力引起的航天器半长轴的时间变化率。 | Real | 力模型 | km/s |
| `SRPArea`（光压面积） | 是 | 是 | 参见 Spacecraft.SRPArea。 | Real | 无 | m^2 |
| `SRPTorque`（光压力矩） | 否 | 否 | 所选力模型中的太阳光压（SRP）在航天器上产生的绕其质心的力矩。力矩在航天器本体系中报告。 | Real Array (1x3) | 力模型 | N*m |
| `SystemCenterOfMassX`（系统质心 X） | 否 | 是 | 系统总体质心在航天器本体坐标系中的 X 分量。包含航天器质量及所有挂载的燃料箱。 | Real | 无 | m |
| `SystemCenterOfMassY`（系统质心 Y） | 否 | 是 | 系统总体质心在航天器本体坐标系中的 Y 分量。包含航天器质量及所有挂载的燃料箱。 | Real | 无 | m |
| `SystemCenterOfMassZ`（系统质心 Z） | 否 | 是 | 系统总体质心在航天器本体坐标系中的 Z 分量。包含航天器质量及所有挂载的燃料箱。 | Real | 无 | m^2（原文如此） |
| `SystemMomentOfInertiaXX`（系统转动惯量 XX） | 否 | 是 | 系统总体转动惯量在航天器本体坐标系中的 XX 分量。包含航天器转动惯量及所有挂载的燃料箱。 | Real | 无 | kg-m^2 |
| `SystemMomentOfInertiaXY`（系统转动惯量 XY） | 否 | 是 | 系统总体转动惯量在航天器本体坐标系中的 XY 分量。包含航天器转动惯量及所有挂载的燃料箱。 | Real | 无 | kg-m^2 |
| `SystemMomentOfInertiaXZ`（系统转动惯量 XZ） | 否 | 是 | 系统总体转动惯量在航天器本体坐标系中的 XZ 分量。包含航天器转动惯量及所有挂载的燃料箱。 | Real | 无 | kg-m^2 |
| `SystemMomentOfInertiaYY`（系统转动惯量 YY） | 否 | 是 | 系统总体转动惯量在航天器本体坐标系中的 YY 分量。包含航天器转动惯量及所有挂载的燃料箱。 | Real | 无 | kg-m^2 |
| `SystemMomentOfInertiaYZ`（系统转动惯量 YZ） | 否 | 是 | 系统总体转动惯量在航天器本体坐标系中的 YZ 分量。包含航天器转动惯量及所有挂载的燃料箱。 | Real | 无 | kg-m^2 |
| `SystemMomentOfInertiaZZ`（系统转动惯量 ZZ） | 否 | 是 | 系统总体转动惯量在航天器本体坐标系中的 ZZ 分量。包含航天器转动惯量及所有挂载的燃料箱。 | Real | 无 | kg-m^2 |
| `TA`（真近点角） | 是 | 是 | 参见 Spacecraft.TA。输出范围：0° ≤ TA < 360°。 | Real | 天体 | deg |
| `TAIGregorian` | 是 | 否 | TAI 时间系统、格里历格式的航天器历元。 | String | 无 | (N/A) |
| `TAIModJulian` | 是 | 是 | TAI 时间系统、约化儒略日格式的航天器历元。 | Real | 无 | d |
| `TDBGregorian` | 是 | 否 | TDB 时间系统、格里历格式的航天器历元。 | String | 无 | (N/A) |
| `TDBModJulian` | 是 | 是 | TDB 时间系统、约化儒略日格式的航天器历元。 | Real | 无 | d |
| `TLONG`（真经度） | 是 | 是 | 参见 Spacecraft.TLONG。输出范围：0° ≤ TLONG < 360°。 | Real | 坐标系 | deg |
| `TLONGDot`（真经度变化率） | 否 | 是 | 由摄动力引起的航天器真惯性经度（RAAN + AOP + TA）的时间变化率。 | Real | 力模型 | deg/s |
| `TotalMass`（总质量） | 否 | 是 | 总质量，包含所挂 ChemicalTank 资源中的燃料质量。 | Real | 无 | kg |
| `TotalTorque`（总力矩） | 否 | 否 | 所选力模型中所有力在航天器上产生的绕其质心的力矩。力矩在航天器本体系中报告。 | Real Array (1x3) | 力模型 | N*m |
| `TTGregorian` | 是 | 否 | TT 时间系统、格里历格式的航天器历元。 | String | 无 | (N/A) |
| `TTModJulian` | 是 | 是 | TT 时间系统、约化儒略日格式的航天器历元。 | Real | 无 | d |
| `UTCGregorian` | 是 | 否 | UTC 时间系统、格里历格式的航天器历元。 | String | 无 | (N/A) |
| `UTCModJulian` | 是 | 是 | UTC 时间系统、约化儒略日格式的航天器历元。 | Real | 无 | d |
| `VelApoapsis`（远拱点速度） | 否 | 是 | 远拱点处的标量速度。 | Real | 天体 | km/s |
| `VelPeriapsis`（近拱点速度） | 否 | 是 | 近拱点处的标量速度。 | Real | 天体 | km/s |
| `VMAG`（速度大小） | 是 | 是 | 参见 Spacecraft.VMAG。输出范围：（原文档空缺）。 | Real | 坐标系 | km/s |
| `VX`（速度 X 分量） | 是 | 是 | 参见 Spacecraft.VX。 | Real | 坐标系 | km/s |
| `VY`（速度 Y 分量） | 是 | 是 | 参见 Spacecraft.VY。 | Real | 坐标系 | km/s |
| `VZ`（速度 Z 分量） | 是 | 是 | 参见 Spacecraft.VZ。 | Real | 坐标系 | km/s |
| `X`（位置 X 分量） | 是 | 是 | 参见 Spacecraft.X。 | Real | 坐标系 | km |
| `Y`（位置 Y 分量） | 是 | 是 | 参见 Spacecraft.Y。 | Real | 坐标系 | km |
| `Z`（位置 Z 分量） | 是 | 是 | 参见 Spacecraft.Z。 | Real | 坐标系 | km |

### FuelTank（燃料箱）

| 参数 | 可设置 | 可绘图 | 说明 | 数据类型 | 依赖 | 单位 |
| --- | --- | --- | --- | --- | --- | --- |
| `FuelDensity`（燃料密度） | 是 | 是 | 参见 ChemicalTank.FuelDensity。 | Real | 无 | kg/m^3 |
| `FuelMass`（燃料质量） | 是 | 是 | 参见 ChemicalTank.FuelMass。 | Real | 无 | kg |
| `Pressure`（压力） | 是 | 是 | 参见 ChemicalTank.Pressure。 | Real | 无 | kPa |
| `RefTemperature`（参考温度） | 是 | 是 | 参见 ChemicalTank.RefTemperature。 | Real | 无 | °C |
| `Temperature`（温度） | 是 | 是 | 参见 ChemicalTank.Temperature。 | Real | 无 | °C |
| `Volume`（体积） | 是 | 是 | 参见 ChemicalTank.Volume。 | Real | 无 | m^3 |

### 空间点参数（Space Point Parameters）

所有在空间中具有坐标的资源都具有笛卡尔位置和速度参数，因此可以访问其星历信息。这包括所有内置太阳系天体，以及其他资源，如 CelestialBody、Planet、Moon、Asteroid、Comet、Barycenter、LibrationPoint 和 GroundStation：

- `CelestialBody.CoordinateSystem.X`
- `CelestialBody.CoordinateSystem.Y`
- `CelestialBody.CoordinateSystem.Z`
- `CelestialBody.CoordinateSystem.VX`
- `CelestialBody.CoordinateSystem.VY`
- `CelestialBody.CoordinateSystem.VZ`

> **警告**：注意，要使用这些参数，必须先将资源的历元设置为希望获取数据的目标历元。此外，历元应在 BeginMissionSequence 命令之后设置。参见下面的示例。

```gmat
Create ReportFile rf

BeginMissionSequence

Luna.A1ModJulian = 21545
Report rf Luna.EarthMJ2000Eq.X Luna.EarthMJ2000Eq.Y Luna.EarthMJ2000Eq.Z ...
       Luna.EarthMJ2000Eq.VX Luna.EarthMJ2000Eq.VY Luna.EarthMJ2000Eq.VZ
```

> **注意**：Spacecraft 参数的处理与空间点（Space Point）参数略有不同，主要是因为 Spacecraft 的笛卡尔状态参数是可设置的，而所有其他空间点的笛卡尔参数只能读取。当请求 Spacecraft 以外的空间点的状态信息时，坐标根据为该资源配置的模型计算。此外，并非所有 Spacecraft 支持的历元配置选项都支持空间点（如 Epoch 和 DateFormat）。

空间点资源的参数表如下：

| 参数 | 可设置 | 可绘图 | 说明 | 数据类型 | 依赖 | 单位 |
| --- | --- | --- | --- | --- | --- | --- |
| `A1Gregorian` | 是 | 否 | A.1 时间系统、格里历格式的资源历元。 | String | 无 | (N/A) |
| `A1ModJulian` | 是 | 是 | A.1 时间系统、约化儒略日格式的资源历元。 | Real | 无 | d |
| `TAIGregorian` | 是 | 否 | TAI 时间系统、格里历格式的资源历元。 | String | 无 | (N/A) |
| `TAIModJulian` | 是 | 是 | TAI 时间系统、约化儒略日格式的资源历元。 | Real | 无 | d |
| `TDBGregorian` | 是 | 否 | TDB 时间系统、格里历格式的资源历元。 | String | 无 | (N/A) |
| `TDBModJulian` | 是 | 是 | TDB 时间系统、约化儒略日格式的资源历元。 | Real | 无 | d |
| `TTGregorian` | 是 | 否 | TT 时间系统、格里历格式的资源历元。 | String | 无 | (N/A) |
| `TTModJulian` | 是 | 是 | TT 时间系统、约化儒略日格式的资源历元。 | Real | 无 | d |
| `UTCGregorian` | 是 | 否 | UTC 时间系统、格里历格式的资源历元。 | String | 无 | (N/A) |
| `UTCModJulian` | 是 | 是 | UTC 时间系统、约化儒略日格式的资源历元。 | Real | 无 | d |
| `VX`（速度 X 分量） | 否 | 是 | 相对于依赖项所选 CoordinateSystem 的速度 x 分量。未选择依赖项时使用 EarthMJ2000Eq。 | Real | 坐标系 | km/s |
| `VY`（速度 Y 分量） | 否 | 是 | 相对于依赖项所选 CoordinateSystem 的速度 y 分量。未选择依赖项时使用 EarthMJ2000Eq。 | Real | 坐标系 | km/s |
| `VZ`（速度 Z 分量） | 否 | 是 | 相对于依赖项所选 CoordinateSystem 的速度 z 分量。未选择依赖项时使用 EarthMJ2000Eq。 | Real | 坐标系 | km/s |
| `X`（位置 X 分量） | 否 | 是 | 相对于依赖项所选 CoordinateSystem 的位置 x 分量。未选择依赖项时使用 EarthMJ2000Eq。 | Real | 坐标系 | km |
| `Y`（位置 Y 分量） | 否 | 是 | 相对于依赖项所选 CoordinateSystem 的位置 y 分量。未选择依赖项时使用 EarthMJ2000Eq。 | Real | 坐标系 | km |
| `Z`（位置 Z 分量） | 否 | 是 | 相对于依赖项所选 CoordinateSystem 的位置 z 分量。未选择依赖项时使用 EarthMJ2000Eq。 | Real | 坐标系 | km |

### Thruster（推力器）

| 参数 | 可设置 | 可绘图 | 说明 | 数据类型 | 依赖 | 单位 |
| --- | --- | --- | --- | --- | --- | --- |
| `C1` | 是 | 是 | 参见 ChemicalThruster.C1。 | Real | 无 | N |
| `C2` | 是 | 是 | 参见 ChemicalThruster.C2。 | Real | 无 | N/kPa |
| `C3` | 是 | 是 | 参见 ChemicalThruster.C3。 | Real | 无 | N |
| `C4` | 是 | 是 | 参见 ChemicalThruster.C4。 | Real | 无 | N/kPa |
| `C5` | 是 | 是 | 参见 ChemicalThruster.C5。 | Real | 无 | N/kPa^2 |
| `C6` | 是 | 是 | 参见 ChemicalThruster.C6。 | Real | 无 | N/kPa^C7 |
| `C7` | 是 | 是 | 参见 ChemicalThruster.C7。 | Real | 无 | 无 |
| `C8` | 是 | 是 | 参见 ChemicalThruster.C8。 | Real | 无 | N/kPa^C9 |
| `C9` | 是 | 是 | 参见 ChemicalThruster.C9。 | Real | 无 | 无 |
| `C10` | 是 | 是 | 参见 ChemicalThruster.C10。 | Real | 无 | N/kPa^C11 |
| `C11` | 是 | 是 | 参见 ChemicalThruster.C11。 | Real | 无 | 无 |
| `C12` | 是 | 是 | 参见 ChemicalThruster.C12。 | Real | 无 | N |
| `C13` | 是 | 是 | 参见 ChemicalThruster.C13。 | Real | 无 | 无 |
| `C14` | 是 | 是 | 参见 ChemicalThruster.C14。 | Real | 无 | 1/kPa |
| `C15` | 是 | 是 | 参见 ChemicalThruster.C15。 | Real | 无 | 无 |
| `C16` | 是 | 是 | 参见 ChemicalThruster.C16。 | Real | 无 | 1/kPa |
| `DutyCycle`（占空比） | 是 | 是 | 参见 ChemicalThruster.DutyCycle。 | Real | 无 | 无 |
| `GravitationalAccel`（重力加速度） | 是 | 是 | 参见 ChemicalThruster.GravitationalAccel。 | Real | 无 | m/s^2 |
| `Isp`（比冲） | 是 | 是 | 单个推力器的比冲。当推力器未开机时，GMAT 向报告文件输出零。 | Real | 无 | s |
| `K1` | 是 | 是 | 参见 ChemicalThruster.K1。 | Real | 无 | s |
| `K2` | 是 | 是 | 参见 ChemicalThruster.K2。 | Real | 无 | s/kPa |
| `K3` | 是 | 是 | 参见 ChemicalThruster.K3。 | Real | 无 | s |
| `K4` | 是 | 是 | 参见 ChemicalThruster.K4。 | Real | 无 | s/kPa |
| `K5` | 是 | 是 | 参见 ChemicalThruster.K5。 | Real | 无 | s/kPa^2 |
| `K6` | 是 | 是 | 参见 ChemicalThruster.K6。 | Real | 无 | s/kPa^C7 |
| `K7` | 是 | 是 | 参见 ChemicalThruster.K7。 | Real | 无 | 无 |
| `K8` | 是 | 是 | 参见 ChemicalThruster.K8。 | Real | 无 | s/kPa^C9 |
| `K9` | 是 | 是 | 参见 ChemicalThruster.K9。 | Real | 无 | 无 |
| `K10` | 是 | 是 | 参见 ChemicalThruster.K10。 | Real | 无 | s/kPa^C11 |
| `K11` | 是 | 是 | 参见 ChemicalThruster.K11。 | Real | 无 | 无 |
| `K12` | 是 | 是 | 参见 ChemicalThruster.K12。 | Real | 无 | s |
| `K13` | 是 | 是 | 参见 ChemicalThruster.K13。 | Real | 无 | 无 |
| `K14` | 是 | 是 | 参见 ChemicalThruster.K14。 | Real | 无 | 1/kPa |
| `K15` | 是 | 是 | 参见 ChemicalThruster.K15。 | Real | 无 | 无 |
| `K16` | 是 | 是 | 参见 ChemicalThruster.K16。 | Real | 无 | 1/kPa |
| `MassFlowRate`（质量流率） | 否 | 是 | 单个推力器的质量流率。当推力器未开机时，GMAT 向报告文件输出零。 | Real | 无 | kg/s |
| `ThrustDirection1`（推力方向 1） | 是 | 是 | 参见 ChemicalThruster.ThrustDirection1。 | Real | 无 | 无 |
| `ThrustDirection2`（推力方向 2） | 是 | 是 | 参见 ChemicalThruster.ThrustDirection2。 | Real | 无 | 无 |
| `ThrustDirection3`（推力方向 3） | 是 | 是 | 参见 ChemicalThruster.ThrustDirection3。 | Real | 无 | 无 |
| `ThrustMagnitude`（推力大小） | 是 | 是 | 单个推力器的推力大小。当推力器未开机时，GMAT 向报告文件输出零。 | Real | 无 | Newtons |
| `ThrustScaleFactor`（推力比例因子） | 是 | 是 | 参见 ChemicalThruster.ThrustScaleFactor。 | Real | 无 | 无 |

### ImpulsiveBurn（脉冲机动）

| 参数 | 可设置 | 可绘图 | 说明 | 数据类型 | 依赖 | 单位 |
| --- | --- | --- | --- | --- | --- | --- |
| `B` | 是 | 是 | 参见 ImpulsiveBurn.B。 | Real | 无 | 无 |
| `Element1`（元素 1） | 是 | 是 | 参见 ImpulsiveBurn.Element1。 | Real | 坐标系 | 无 |
| `Element2`（元素 2） | 是 | 是 | 参见 ImpulsiveBurn.Element2。 | Real | 坐标系 | 无 |
| `Element3`（元素 3） | 是 | 是 | 参见 ImpulsiveBurn.Element3。 | Real | 坐标系 | 无 |
| `N` | 是 | 是 | 参见 ImpulsiveBurn.N。 | Real | 无 | 无 |
| `V` | 是 | 是 | 参见 ImpulsiveBurn.V。 | Real | 无 | 无 |

### FiniteBurn（有限推力机动）

| 参数 | 可设置 | 可绘图 | 说明 | 数据类型 | 依赖 | 单位 |
| --- | --- | --- | --- | --- | --- | --- |
| `TotalAcceleration1`（总加速度分量 1） | 否 | 是 | 所有推力器产生的总加速度在 J2000 坐标系三个坐标方向上的第一个分量。推力器未开机时输出零。 | Real | 无 | Km/s^2 |
| `TotalAcceleration2`（总加速度分量 2） | 否 | 是 | 所有推力器产生的总加速度在 J2000 坐标系三个坐标方向上的第二个分量。推力器未开机时输出零。 | Real | 无 | Km/s^2 |
| `TotalAcceleration3`（总加速度分量 3） | 否 | 是 | 所有推力器产生的总加速度在 J2000 坐标系三个坐标方向上的第三个分量。推力器未开机时输出零。 | Real | 无 | Km/s^2 |
| `TotalMassFlowRate`（总质量流率） | 否 | 是 | 所有推力器的总质量流率。推力器未开机时输出零。 | Real | 无 | Kg/s |
| `TotalThrust1`（总推力分量 1） | 否 | 是 | 所有推力器产生的总推力在 J2000 坐标系三个坐标方向上的第一个分量。推力器未开机时输出零。 | Real | 无 | Newtons |
| `TotalThrust2`（总推力分量 2） | 否 | 是 | 所有推力器产生的总推力在 J2000 坐标系三个坐标方向上的第二个分量。推力器未开机时输出零。 | Real | 无 | Newtons |
| `TotalThrust3`（总推力分量 3） | 否 | 是 | 所有推力器产生的总推力在 J2000 坐标系三个坐标方向上的第三个分量。推力器未开机时输出零。 | Real | 无 | Newtons |

### Solver（求解器）

| 参数 | 可设置 | 可绘图 | 说明 | 数据类型 | 依赖 | 单位 |
| --- | --- | --- | --- | --- | --- | --- |
| `SolverStatus`（求解器状态） | 否 | 否 | SolverStatus 参数包含求解器（Solver）的状态。若求解器尚未执行，SolverStatus 为 Initialized（已初始化）；若求解器已执行并收敛，为 Converged（已收敛）；若求解器正在迭代，为 Running（运行中）；若求解器已执行且在收敛前达到最大迭代次数，为 ExceededIterations（超出迭代次数）；若求解器已执行但未能收敛、且未超过最大迭代次数，为 DidNotConverge（未收敛）。 | String | 无 | 无 |
| `SolverState`（求解器状态码） | 否 | 是 | SolverState 参数包含求解器的状态。若求解器尚未执行，SolverState 为 0；若求解器已执行并收敛，为 1；若求解器正在迭代，为 0；若求解器已执行且在收敛前达到最大迭代次数，为 -1；若求解器已执行但未能收敛、且未超过最大迭代次数，为 -2。 | Integer | 无 | 无 |

### Array、String、Variable

Array、String 和 Variable 资源本身就是参数，可以像任何其他参数一样使用。它们都是可写参数，但只有 Variable 资源和 Array 资源的单个元素可以用于绘图。

### 耗时参数（Elapsed Time Parameters）

耗时参数（如 `ElapsedSecs` 和 `ElapsedDays`）根据参考历元计算，而参考历元取决于使用场合。一般来说，参考历元由使用该参数的命令决定。下面的示例展示了参考历元如何根据上下文确定。

```gmat
Create Spacecraft Sat
Create Propagator Prop

BeginMissionSequence

Sat.TAIModJulian = 35000
% The reference epoch for While is TAIModJuian = 35000.
% The ref. epoch is held constant as the while loop executes
While Sat.ElapsedDays <= 1
    % The reference epoch for Propagate changes every pass.
    % It is set to the epoch at start of propagation
    Propagate Prop(Sat){Sat.ElapsedDays = .1}
EndWhile
```

（译注：示例中注释的大意是——While 循环的参考历元为 TAIModJulian = 35000，在循环执行期间保持不变；而 Propagate 的参考历元每轮都会变化，被设为每次推进开始时的历元。）

## 示例（Examples）

在任务序列（Mission Sequence）中使用参数：

```gmat
Create Spacecraft aSat
Create Propagator aProp
Create ReportFile aReport
Create Variable i

BeginMissionSequence

% propagate for 100 steps
For i=1:100
    Propagate aProp(aSat)
    % write four parameters (one standalone, three coordinate-system-dependent) to a file
    Report aReport aSat.TAIGregorian aSat.EarthFixed.X aSat.EarthFixed.Y aSat.EarthFixed.Z
EndFor
```

（译注：示例注释的大意是——推进 100 步；将四个参数写入文件，其中一个为独立参数，三个为依赖坐标系的参数。）

将参数用作绘图数据：

```gmat
Create Spacecraft aSat
Create Propagator aProp

Create XYPlot aPlot
aPlot.XVariable  = aSat.TAIModJulian
aPlot.YVariables = {aSat.Earth.Altitude, aSat.Earth.ECC}

Create Variable i

BeginMissionSequence

% propagate for 100 steps
For i=1:100
    Propagate aProp(aSat)
EndFor
```

将参数用作停止条件：

```gmat
Create Spacecraft aSat
aSat.SMA = 6678

Create ForceModel anFM
anFM.Drag.AtmosphereModel = MSISE90

Create Propagator aProp
aProp.FM = anFM

BeginMissionSequence

Propagate aProp(aSat) {aSat.Earth.Altitude = 100, aSat.ElapsedDays = 365}
```
