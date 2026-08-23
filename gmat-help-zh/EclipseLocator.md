# 食分析器（EclipseLocator）
> 译自 GMAT R2026a 帮助文档 EclipseLocator.html

**EclipseLocator** —— 航天器食（阴影）事件定位器。

## 描述

> **注意**：`EclipseLocator` 是基于 SPICE 的子系统，它使用的太阳系和天体配置与 GMAT 其他组件是并行的。对于精密应用，必须注意确保两套配置保持一致。详情请参阅"备注"。

`EclipseLocator` 是一个事件定位器，用于查找航天器所观测到的日食事件。默认情况下，`EclipseLocator` 生成一份文本事件报告，列出每个事件的开始和结束时间，以及持续时间、掩食天体、阴影类型，以及关于同时发生和相邻嵌套事件的信息。食定位可以在整个传播区间或其子区间上执行，并且可以选择对光行时延迟和恒星光行差进行修正。

食定位可以使用一个或多个 `CelestialBody`（天体）资源作为掩食天体。任何已配置的天体都可以用作掩食天体，包括用户自定义的天体。可以找到任何类型的食，包括全食（本影，umbra）、偏食（半影，penumbra）和环食（伪本影，antumbra）。所有选定的掩食天体都使用相同的食类型、搜索区间和搜索选项进行搜索；若要按天体定制选项，请使用多个 `EclipseLocator` 资源。

默认情况下，`EclipseLocator` 搜索 `Spacecraft`（航天器）的整个传播区间。要搜索自定义区间，请将 `UseEntireInterval` 设为 `False` 并相应地设置 `InitialEpoch` 和 `FinalEpoch`。注意，这些历元被假定为航天器历元，因此必须有效且位于航天器历表区间内。如果它们落在航天器的传播区间之外，GMAT 将显示错误。

该定位器可以选择对光行时延迟和恒星光行差进行修正，但恒星光行差目前没有实际效果。

事件搜索以固定步长遍历区间。你可以通过设置 `StepSize` 字段来控制步长（以秒为单位）。步长的合适选择是：不大于你希望找到的最短事件持续时间，或你希望分辨的事件之间最小间隔，取两者中较小者。详情请参阅"备注"。

GMAT 使用 SPICE 库作为基本的事件定位算法。因此，该子系统的所有天体数据都从 SPICE 内核加载，而不是使用 GMAT 自己的 `CelestialBody` 形状和定向配置。详情请参阅"备注"。

除非另有说明，`EclipseLocator` 字段不能在任务序列中设置。

**另请参阅**：CelestialBody（天体）、Spacecraft（航天器）、ContactLocator（可见性分析器）、FindEvents（事件查找）

## 字段

| 字段 | 描述 |
|------|------|
| **EclipseTypes** | 要搜索的食（阴影）类型。可以是 `Umbra`（全食/本影）、`Penumbra`（偏食/半影）或 `Antumbra`（环食/伪本影）。<br>数据类型：枚举数组<br>允许值：`Antumbra`、`Penumbra`、`Umbra`<br>访问权限：set<br>默认值：`{Antumbra, Penumba, Umbra}`<br>单位：N/A<br>接口：GUI、脚本 |
| **Filename** | 食报告文件的名称和路径。该字段可以在任务序列中设置。<br>数据类型：字符串<br>允许值：有效的文件路径<br>访问权限：set<br>默认值：`'EclipseLocator.txt'`<br>单位：N/A<br>接口：GUI、脚本 |
| **FinalEpoch** | 搜索食的最后一个历元，格式由 `InputEpochFormat` 指定。该历元必须是航天器历表区间内的有效历元。该字段可以在任务序列中设置。<br>数据类型：字符串<br>允许值：可用航天器历表中的有效历元<br>访问权限：set<br>默认值：`'21545.138'`<br>单位：ModifiedJulian 历元格式：天；Gregorian 历元格式：N/A<br>接口：GUI、脚本 |
| **InitialEpoch** | 搜索食的第一个历元，格式由 `InputEpochFormat` 指定。该历元必须是航天器历表区间内的有效历元。该字段可以在任务序列中设置。<br>数据类型：字符串<br>允许值：可用航天器历表中的有效历元<br>访问权限：set<br>默认值：`'21545'`<br>单位：ModifiedJulian 历元格式：天；Gregorian 历元格式：N/A<br>接口：GUI、脚本 |
| **OccultingBodies** | 要搜索食的掩食天体列表。可以是任意数量的 GMAT `CelestialBody` 类型资源，如 `Planet`（行星）、`Moon`（卫星）、`Asteroid`（小行星）等。注意，掩食天体必须有质量（例如不能是 `LibrationPoint`（天平动点）或 `Barycenter`（质心））。<br>数据类型：`CelestialBody` 资源列表（如 `Planet`、`Asteroid`、`Moon` 等）<br>允许值：任何现有的 `CelestialBody` 类资源<br>访问权限：set<br>默认值：空列表<br>单位：N/A<br>接口：GUI、脚本 |
| **RunMode** | 事件定位的执行模式。`'Automatic'` 触发事件定位在运行结束时自动执行。`'Manual'` 将执行限制为仅由 `FindEvents` 命令触发。`'Disabled'` 完全关闭事件定位。<br>数据类型：枚举<br>允许值：`Automatic`、`Manual`、`Disabled`<br>访问权限：set<br>默认值：`'Automatic'`<br>单位：N/A<br>接口：GUI、脚本 |
| **Spacecraft** | 用于搜索食的观测 `Spacecraft`（航天器）资源。<br>数据类型：`Spacecraft` 资源<br>允许值：任何现有的 `Spacecraft` 资源<br>访问权限：set<br>默认值：第一个已配置的 `Spacecraft` 资源<br>单位：N/A<br>接口：GUI、脚本 |
| **StepSize** | 事件定位器的步长。有关合适取值的讨论，请参阅"备注"。<br>数据类型：实数<br>允许值：`StepSize` > 0<br>访问权限：set<br>默认值：10<br>单位：s<br>接口：GUI、脚本 |
| **UseEntireInterval** | 搜索整个可用的 `Target`（目标）历表区间。该字段可以在任务序列中设置。<br>数据类型：布尔值<br>允许值：true、false<br>访问权限：set<br>默认值：true<br>单位：N/A<br>接口：GUI、脚本 |
| **UseLightTimeDelay** | 在事件查找算法中使用光行时延迟。<br>数据类型：布尔值<br>允许值：true、false<br>访问权限：set<br>默认值：true<br>单位：N/A<br>接口：GUI、脚本 |
| **UseStellarAberration** | 在事件查找算法中，除光行时延迟外还使用恒星光行差。必须启用光行时延迟。恒星光行差目前对食搜索没有影响。<br>数据类型：布尔值<br>允许值：true、false<br>访问权限：set<br>默认值：true<br>单位：N/A<br>接口：GUI、脚本 |
| **WriteReport** | 执行事件定位时写出事件报告。该字段可以在任务序列中设置。<br>数据类型：布尔值<br>允许值：true、false<br>访问权限：set<br>默认值：true<br>单位：N/A<br>接口：GUI、脚本 |

## GUI

> [图：EclipseLocator 默认 GUI 面板]

上图显示了新资源的默认 `EclipseLocator` GUI。你可以从列表中选择一个 `Spacecraft`，该列表由任务中当前配置的所有 `Spacecraft` 资源填充。在 **Occulting Bodies**（掩食天体）列表中，你可以勾选要搜索食的所有 `CelestialBody` 资源旁边的复选框。该列表显示任务中当前配置的所有天体。

在 **Eclipse Types**（食类型）列表中，选择要搜索的食类型。注意，每项选择都会增加搜索的耗时。

你可以通过底部的 **Filename**、**Run Mode**（运行模式）和 **Write Report**（写报告）来配置输出。如果启用了 **Write Report**，文本报告将写入 **Filename** 指定的文件。根据 **Run Mode** 的不同，搜索将在 `FindEvents` 命令期间执行（`Manual` 或 `Automatic` 模式），并在任务结束时自动执行（`Automatic` 模式）。

你可以通过右上角的选项配置搜索区间。取消勾选 **Use Entire Interval**（使用整个区间）可手动设置搜索区间。设置搜索区间时的注意事项请参阅"备注"一节。

你可以通过右下角的选项控制搜索算法。通过各复选框配置光行时和恒星光行差，并通过 **Light-time direction**（光行时方向）选择信号方向。

要控制搜索的保真度和执行时间，请适当设置 **Step size**（步长）。详情请参阅"备注"一节。

## 备注

### 数据配置

`EclipseLocator` 的实现基于 [NAIF SPICE 工具包](https://naif.jpl.nasa.gov/naif/)，它对环境数据（如天体形状和定向、行星星历、天体专用坐标架定义和闰秒）使用不同的机制。因此，必须维护两套并行的配置，以确保事件定位结果与 GMAT 自身的传播和其他参数保持一致。需要维护的具体数据为：

- 行星形状和定向：
  - GMAT 核心：`CelestialBody`.`EquatorialRadius`（赤道半径）、`Flattening`（扁率）、`SpinAxisRAConstant`（自转轴赤经常数项）、`SpinAxisRARate`（自转轴赤经变化率）等。
  - EclipseLocator：`SolarSystem`.`PCKFilename`、`CelestialBody`.`PlanetarySpiceKernelName`
- 行星星历：
  - GMAT 核心：`SolarSystem`.`DEFilename`，或（`SolarSystem`.`SPKFilename`、`CelestialBody`.`OrbitSpiceKernelName`、`CelestialBody`.`NAIFId`）
  - EclipseLocator：`SolarSystem`.`SPKFilename`、`CelestialBody`.`OrbitSpiceKernelName`、`CelestialBody`.`NAIFId`
- 星固坐标架（Body-fixed frame）：
  - GMAT 核心：内置
  - EclipseLocator：`CelestialBody`.`SpiceFrameId`、`CelestialBody`.`FrameSpiceKernelName`
- 闰秒：
  - GMAT 核心：启动文件 `LEAP_SECS_FILE` 设置
  - EclipseLocator：`SolarSystem`.`LSKFilename`

更多详情请参阅 SolarSystem 和 CelestialBody。

### 搜索区间

`EclipseLocator` 的搜索区间可以指定为航天器的整个历表区间，也可以指定为用户自定义区间。如果 `UseEntireInterval` 为 true，搜索将在航天器的整个历表区间上执行，包括任何空隙或不连续段。如果 `UseEntireInterval` 为 false，则直接使用提供的 `InitialEpoch` 和 `FinalEpoch` 构成搜索区间。用户必须确保所提供的区间对应有效的 `Spacecraft` 和 `CelestialBody` 历表历元。

### 运行模式

`EclipseLocator` 与 `FindEvents` 命令协同工作：`EclipseLocator` 资源定义事件搜索的配置，`FindEvents` 命令在任务序列的特定位置执行搜索。交互模式由 `EclipseLocator`.`RunMode` 定义，它有三个选项：

- `Automatic`：所有 `FindEvents` 命令照常执行，另外在任务序列末尾自动执行一次额外的 `FindEvents`。
- `Manual`：所有 `FindEvents` 命令照常执行。
- `Disabled`：`FindEvents` 命令被忽略。

### 搜索算法

`EclipseLocator` 使用 NAIF SPICE GF（几何查找器，geometry finder）子系统执行事件定位。具体来说，搜索使用以下调用：

- `gfoclt_c`：用于第三体掩食搜索

该函数实现了在区间上的定步长搜索方法，并在发现事件时嵌入求根定位步骤。`StepSize` 应设为要找到的最短事件持续时间，或事件之间最短间隔的长度，取两者中较小者。要保证能定位 10 秒的食或相邻食之间 10 秒的间隔，请设 `StepSize` = 10。

详情请参阅上面链接函数的参考文档。

### 报告格式

当启用 `WriteReport` 时，`EclipseLocator` 在每次搜索执行结束时输出事件报告。报告包含以下数据：

- 航天器名称
- 对于每个事件：
  - 事件开始时间（UTC）
  - 事件结束时间（UTC）
  - 事件持续时间（s）
  - 掩食天体名称
  - 食类型
  - 总事件编号
  - 总持续时间
- 单独事件（individual events）的数量
- 总事件（total events）的数量
- 最大总持续时间
- 总持续时间对应的食编号

报告区分*单独*事件和*总*事件：

- *单独事件*（individual event）是来自单个掩食天体的单一类型（本影、半影等）的单个连续事件。单独事件可以针对单个掩食天体嵌套，例如半影事件紧跟着一个本影事件；也可以跨多个掩食天体嵌套，例如在地球食的中途发生一次月球食。
- *总事件*（total event）是嵌套单独事件的整个集合。总事件被赋予一个编号，其总持续时间在输出文件中报告。

### 使用 SPK 传播器进行事件定位

使用 SPK 传播器时，你通过 Spacecraft.OrbitSpiceKernelName 字段加载一个或多个 SPK 历表文件。就事件定位而言，该字段会使相应的历表文件在运行时自动加载，因此不需要使用 Propagate 命令。这是在现有 SPK 历表文件上执行事件定位的简便方法。请参阅下面的示例。

## 示例

在 LEO（近地轨道）中执行基本的食搜索：

```
SolarSystem.EphemerisSource = 'DE421'

Create Spacecraft sat
sat.DateFormat = UTCGregorian
sat.Epoch = '15 Sep 2010 16:00:00.000'
sat.CoordinateSystem = EarthMJ2000Eq
sat.DisplayStateType = Keplerian
sat.SMA = 6678.14
sat.ECC = 0.001
sat.INC = 0
sat.RAAN = 0
sat.AOP = 0
sat.TA = 180

Create ForceModel fm
fm.CentralBody = Earth
fm.PrimaryBodies = {Earth}
fm.GravityField.Earth.PotentialFile = 'JGM2.cof'
fm.GravityField.Earth.Degree = 0
fm.GravityField.Earth.Order = 0
fm.GravityField.Earth.TideModel = 'None'
fm.Drag.AtmosphereModel = None
fm.PointMasses = {}
fm.RelativisticCorrection = Off
fm.SRP = Off

Create Propagator prop
prop.FM = fm
prop.Type = RungeKutta89

Create EclipseLocator el
el.Spacecraft = sat
el.Filename = 'Simple.report'
el.OccultingBodies = {Earth}
el.EclipseTypes = {'Umbra', 'Penumbra', 'Antumbra'}

BeginMissionSequence

Propagate prop(sat) {sat.ElapsedSecs = 10800}
```

说明：使用 DE421 历表创建一颗近地轨道卫星，配置以地球为掩食天体、搜索本影/半影/伪本影三类食的食分析器；传播 3 小时（10800 秒），运行结束时自动执行食搜索并输出报告。

从火星轨道器执行食事件搜索，包含火卫一（Phobos）、地球和月球的食：

```
% Mars orbiter with annular eclipses of Earth and Moon.

SolarSystem.EphemerisSource = 'SPICE'
SolarSystem.SPKFilename = 'de421.bsp'

Mars.NAIFId = 499
Mars.OrbitSpiceKernelName = {'../data/planetary_ephem/spk/mar063.bsp'}

Create Spacecraft sat
sat.DateFormat = UTCGregorian
sat.Epoch = '10 May 1984 00:00:00.000'
sat.CoordinateSystem = MarsMJ2000Eq
sat.DisplayStateType = Keplerian
sat.SMA = 6792.38
sat.ECC = 0
sat.INC = 45
sat.RAAN = 0
sat.AOP = 0
sat.TA = 0

Create ForceModel fm
fm.CentralBody = Mars
fm.PrimaryBodies = {Mars}
fm.GravityField.Mars.PotentialFile = 'Mars50c.cof'
fm.GravityField.Mars.Degree = 0
fm.GravityField.Mars.Order = 0
fm.Drag.AtmosphereModel = None
fm.PointMasses = {}
fm.RelativisticCorrection = Off
fm.SRP = Off

Create Propagator prop
prop.FM = fm
prop.Type = RungeKutta89

Create CoordinateSystem MarsMJ2000Eq
MarsMJ2000Eq.Origin = Mars
MarsMJ2000Eq.Axes = MJ2000Eq

Create Moon Phobos
Phobos.CentralBody = 'Mars'
Phobos.PosVelSource = 'SPICE'
Phobos.NAIFId = 401
Phobos.OrbitSpiceKernelName = {'mar063.bsp'}
Phobos.SpiceFrameId = 'IAU_PHOBOS'
Phobos.EquatorialRadius = 13.5
Phobos.Flattening = 0.3185185185185186
Phobos.Mu = 7.093399e-004

Create Moon Deimos
Deimos.CentralBody = 'Mars'
Deimos.PosVelSource = 'SPICE'
Deimos.NAIFId = 402
Deimos.OrbitSpiceKernelName = {'mar063.bsp'}
Deimos.EquatorialRadius = 7.5
Deimos.SpiceFrameId = 'IAU_DEIMOS'
Deimos.Flattening = 0.30666666666666664
Deimos.Mu = 1.588174e-004

Create EclipseLocator ec
ec.Spacecraft = sat
ec.OccultingBodies = {Mercury, Venus, Earth, Luna, Mars, Phobos, Deimos}
ec.Filename = 'EarthTransit.report'

BeginMissionSequence

Propagate prop(sat) {sat.ElapsedDays = 2}
```

说明：使用 SPICE 历表配置火星轨道器，并定义火卫一和火卫二两个卫星（含 NAIF ID、轨道内核、形状和引力参数）；食分析器以水星、金星、地球、月球、火星、火卫一、火卫二为掩食天体，传播 2 天并输出食报告。

在现有 SPK 历表文件上执行食定位：

```
SolarSystem.EphemerisSource = 'DE421'

Create Spacecraft sat
sat.OrbitSpiceKernelName = {'../data/vehicle/ephem/spk/Events_Simple.bsp'}

Create EclipseLocator cl
cl.Spacecraft = sat
cl.OccultingBodies = {Earth}
cl.Filename = 'SPKPropagation.report'

BeginMissionSequence
```

说明：通过 `sat.OrbitSpiceKernelName` 直接加载已有的 SPK 历表文件，无需 Propagate 命令即可执行食定位。
