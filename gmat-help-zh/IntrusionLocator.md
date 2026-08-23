# 侵入分析器（IntrusionLocator）
> 译自 GMAT R2026a 帮助文档 IntrusionLocator.html

**IntrusionLocator** —— 目标天体（CelestialBody）与观测航天器（Spacecraft）之间的视线（line-of-sight）事件定位器。

## 描述

> **注意**：`IntrusionLocator` 是基于 SPICE 的子系统，它使用的太阳系和天体配置与 GMAT 其他组件是并行的。对于精密应用，必须注意确保两套配置保持一致。详情请参阅"备注"。

`IntrusionLocator` 是一个事件定位器，基于安装在航天器上的 `Imager`（成像仪）的视场，查找航天器与天体之间的视线事件。默认情况下，`IntrusionLocator` 生成一份文本事件报告，列出每个视线事件的开始和结束时间，并按所选步长生成中间时刻的数据。每条数据还包含目标在用户选定坐标系中的坐标、目标的角直径以及目标的照明度。侵入定位可以在整个传播区间或其子区间上执行，并且可以选择对光行时延迟和恒星光行差进行修正。侵入定位可以配置为搜索其他可能阻挡视线的 `CelestialBody` 资源的掩食时刻，并可以将侵入事件限制为目标的指定最小照明度。

侵入定位可以在一个航天器成像仪（`Observer`，观测者）与任意数量的 `CelestialBody` 或 `Spacecraft` 资源（`Targets`，目标）之间执行。每个目标-观测者对单独搜索，并在结果报告中形成单独的部分。所有对必须使用相同的区间和搜索选项；若要按对定制选项，请使用多个 `IntrusionLocator` 资源。

通过在 `CentralBody`（中心天体）字段中列出一个 `CelestialBody` 资源，可以包含第三体掩食搜索。任何已配置的天体都可以用作掩食天体，包括用户自定义的天体。

默认情况下，`IntrusionLocator` 在应用端点光行时修正后，搜索 `IntrudingBodies`（侵入天体）的整个传播区间；详情请参阅"备注"。要搜索自定义区间，请将 `UseEntireInterval` 设为 `False` 并相应地设置 `InitialEpoch` 和 `FinalEpoch`。注意，这些历元被假定为观测者处的历元，因此当通过光行时延迟和恒星光行差（如已配置）换算到目标时必须有效。如果它们落在 `IntrudingBodies` 的传播区间之外，GMAT 将显示错误。

侵入定位器可以选择对光行时延迟和恒星光行差进行修正，使用沿接收方向（`Target to Observer`，目标到观测者）传播的信号。光行时方向通过限制区间末端附近的搜索来影响有效搜索区间。详情请参阅"备注"。恒星光行差仅应用于搜索的视线部分；它在掩食搜索期间没有影响。

事件搜索以固定步长遍历区间。你可以通过设置 `StepSize` 字段来控制步长（以秒为单位）。步长的合适选择是不大于视线函数周期的一半——即椭圆轨道的轨道周期的一半。详情请参阅"备注"。

GMAT 使用 SPICE 库作为基本的事件定位算法。因此，该子系统的所有天体数据都从 SPICE 内核加载，而不是使用 GMAT 自己的 `CelestialBody` 形状和定向配置。详情请参阅"备注"。

除非另有说明，`IntrusionLocator` 字段不能在任务序列中设置。

**另请参阅**：CelestialBody（天体）、Imager（成像仪）、Spacecraft（航天器）

## 字段

| 字段 | 描述 |
|------|------|
| **CentralBody** | 将被检查是否介于 `Imager` 与目标之间、以及目标是否凌越该天体的天体名称。当掩食发生时，目标在传感器侵入报告中不显示为侵入。<br>数据类型：`CelestialBody` 资源（如 `Planet`、`Asteroid`、`Moon` 等）<br>允许值：任何现有的 `CelestialBody` 资源<br>访问权限：set<br>默认值：Earth<br>单位：N/A<br>接口：GUI、脚本 |
| **Filename** | 侵入报告文件的名称和路径。该字段可以在任务序列中设置。<br>数据类型：字符串<br>允许值：有效的文件路径<br>访问权限：set<br>默认值：`'IntrusionLocator.txt'`<br>单位：N/A<br>接口：GUI、脚本 |
| **FinalEpoch** | 搜索侵入的最后一个历元，格式由 `InputEpochFormat` 指定。该历元（包括任何光行时在内）必须映射到 `Spacecraft` 和目标侵入天体历表区间内的有效历元。该字段可以在任务序列中设置。<br>数据类型：字符串<br>允许值：可用航天器历表中的有效历元<br>访问权限：set<br>默认值：`'21545.138'`<br>单位：ModifiedJulian 历元格式：天；Gregorian 历元格式：N/A<br>接口：GUI、脚本 |
| **InitialEpoch** | 搜索侵入的第一个历元，格式由 `InputEpochFormat` 指定。该历元（包括任何光行时在内）必须映射到 `Spacecraft` 和目标侵入天体历表区间内的有效历元。该字段可以在任务序列中设置。<br>数据类型：字符串<br>允许值：可用航天器历表中的有效历元<br>访问权限：set<br>默认值：`'21545'`<br>单位：ModifiedJulian 历元格式：天；Gregorian 历元格式：N/A<br>接口：GUI、脚本 |
| **InputEpochFormat** | `InitialEpoch` 和 `FinalEpoch` 字段使用的历元格式。<br>数据类型：字符串<br>允许值：A1ModJulian、TAIModJulian、UTCModJulian、TTModJulian、TDBModJulian、A1Gregorian、TAIGregorian、TTGregorian、UTCGregorian、TDBGregorian<br>访问权限：set<br>默认值：`'TAIModJulian'`<br>单位：N/A<br>接口：GUI、脚本 |
| **IntrudingBodies** | 用作 `Sensors` 字段所列观测者目标的 `CelestialBody` 和/或 `Spacecraft` 资源列表。这些天体出现在 `Sensors` 视场中的事件将在输出文件中报告。注意，`CelestialBody` 在侵入计算中使用椭球形状，而 `Spacecraft` 用一个点表示。<br>数据类型：`CelestialBody` 资源列表（如 `Planet`、`Asteroid`、`Moon` 等）<br>允许值：任何现有的 `CelestialBody` 或 `Spacecraft` 资源<br>访问权限：set<br>默认值：N/A<br>单位：N/A<br>接口：GUI、脚本 |
| **MinimumPhase** | 设置目标在 `Sensors` 视场中被视为侵入所需的最小照明度。<br>数据类型：实数<br>允许值：0.0 < `MinimumPhase` < 1.0<br>访问权限：set<br>默认值：`'0.0'`<br>单位：N/A<br>接口：GUI、脚本 |
| **ReportCoordinates** | 设置侵入事件期间侵入天体报告所用坐标格式的字符串。SensorFrame 坐标使用 `Spacecraft` 字段中航天器的体固坐标架来构建星载仪器坐标架，生成的报告将使用该坐标架。FixedGrid 使用 `SpiceGridFrameFile` 字段提供的坐标架。<br>数据类型：字符串<br>允许值：SensorFrame、FixedGrid<br>访问权限：set<br>默认值：`SensorFrame`<br>单位：N/A<br>接口：GUI、脚本 |
| **RunMode** | 事件定位的执行模式。`'Automatic'` 触发事件定位在运行结束时自动执行。`'Manual'` 将执行限制为仅由 `FindEvents` 命令触发。`'Disabled'` 完全关闭事件定位。<br>数据类型：枚举<br>允许值：`Automatic`、`Manual`、`Disabled`<br>访问权限：set<br>默认值：`'Automatic'`<br>单位：N/A<br>接口：GUI、脚本 |
| **Sensors** | 用于检查侵入的 `Imager`（成像仪）资源列表。<br>数据类型：一个或多个 `Imager` 资源<br>允许值：安装在 `Spacecraft` 字段所输入航天器上的任何现有 `Imager` 资源<br>访问权限：set<br>默认值：N/A<br>单位：N/A<br>接口：GUI、脚本 |
| **Spacecraft** | 安装了所需 `Imager` 资源、用作观测者的 `Spacecraft` 的名称。<br>数据类型：`Spacecraft` 资源<br>允许值：任何现有的、至少安装有一个 `Imager` 资源的 `Spacecraft` 资源<br>访问权限：set<br>默认值：N/A<br>单位：N/A<br>接口：GUI、脚本 |
| **SpiceGridFrameFile** | 当 `ReportCoordinates` 字段选择 FixedGrid 坐标架时使用的坐标架内核文件。<br>数据类型：字符串<br>允许值：有效的文件路径和名称<br>访问权限：set<br>默认值：`N/A`<br>单位：N/A<br>接口：GUI、脚本 |
| **StepSize** | 事件定位器使用的时间步长。有关合适取值的讨论，请参阅"备注"。<br>数据类型：实数<br>允许值：`StepSize` > 0<br>访问权限：set<br>默认值：10<br>单位：s<br>接口：GUI、脚本 |
| **UseEntireInterval** | 在适当对端点进行光行时延迟修正后，搜索整个可用的历表区间。详情请参阅"备注"。该字段可以在任务序列中设置。<br>数据类型：布尔值<br>允许值：true、false<br>访问权限：set<br>默认值：true<br>单位：N/A<br>接口：GUI、脚本 |
| **UseLightTimeDelay** | 在事件查找算法中使用光行时延迟。时钟始终设在观测者（`Observer`）上。<br>数据类型：布尔值<br>允许值：true、false<br>访问权限：set<br>默认值：true<br>单位：N/A<br>接口：GUI、脚本 |
| **UseStellarAberration** | 在事件查找算法中，除光行时延迟外还使用恒星光行差。必须启用光行时延迟。恒星光行差只影响视线搜索，不影响掩食搜索。<br>数据类型：布尔值<br>允许值：true、false<br>访问权限：set<br>默认值：true<br>单位：N/A<br>接口：GUI、脚本 |
| **WriteReport** | 执行事件定位时写出事件报告。该字段可以在任务序列中设置。<br>数据类型：布尔值<br>允许值：true、false<br>访问权限：set<br>默认值：true<br>单位：N/A<br>接口：GUI、脚本 |

## GUI

> [图：IntrusionLocator 默认 GUI 面板]

上图显示了新资源的默认 `IntrusionLocator` GUI。可以从 **Spacecraft** 下拉菜单中选择一个 `Spacecraft`，该菜单由任务中当前配置的所有 `Spacecraft` 填充。接下来，从填充了所有当前已加载 `CelestialBody` 资源的下拉菜单中选择 **Central Body**（中心天体）。

**Intruding Bodies**（侵入天体）复选列表用于设置传感器在任务序列期间将检查哪些 `CelestialBody` 的侵入。可以进行多项选择。随后的 **Sensors**（传感器）复选列表用于选择此 `IntrusionLocator` 使用哪些传感器。注意，这些传感器还需要挂载到所选 `Spacecraft` 的硬件列表中。

你可以通过底部的 **Filename**、**Run Mode** 和 **Write Report** 来配置输出。如果启用了 **Write Report**，文本报告将写入 **Filename** 指定的文件。根据 **Run Mode** 的不同，搜索将在 `FindEvents` 命令期间执行（`Manual` 或 `Automatic` 模式），并在任务结束时自动执行（`Automatic` 模式）。

你可以通过右上角的选项配置搜索区间。取消勾选 **Use Entire Interval** 可手动设置搜索区间。设置搜索区间时的注意事项请参阅"备注"一节。

你可以通过右下角的选项控制搜索算法。通过各复选框配置光行时和恒星光行差。

要控制搜索的保真度和执行时间，请适当设置 **Step size**（步长）。详情请参阅"备注"一节。

要设置将目标计为侵入所需的最小相位（照明度），请适当设置 **Minimum Phase**。

使用 **Report Coordinates**（报告坐标）下拉菜单选择输出侵入报告中使用的坐标。如果选择 **FixedGrid**，则 **Spice Grid Frame File** 变为可用，用于设置要使用的坐标架内核。可直接输入完整路径或使用字段旁边的浏览按钮进行设置。

## 备注

### 数据配置

`IntrusionLocator` 的实现基于 [NAIF SPICE 工具包](https://naif.jpl.nasa.gov/naif/)，它对环境数据（如天体形状和定向、行星星历、天体专用坐标架定义和闰秒）使用不同的机制。因此，必须维护两套并行的配置，以确保事件定位结果与 GMAT 自身的传播和其他参数保持一致。需要维护的具体数据为：

- 行星形状和定向：
  - GMAT 核心：`CelestialBody`.`EquatorialRadius`（赤道半径）、`Flattening`（扁率）、`SpinAxisRAConstant`（自转轴赤经常数项）、`SpinAxisRARate`（自转轴赤经变化率）等。
  - IntrusionLocator：`SolarSystem`.`PCKFilename`、`CelestialBody`.`PlanetarySpiceKernelName`
- 行星星历：
  - GMAT 核心：`SolarSystem`.`DEFilename`，或（`SolarSystem`.`SPKFilename`、`CelestialBody`.`OrbitSpiceKernelName`、`CelestialBody`.`NAIFId`）
  - IntrusionLocator：`SolarSystem`.`SPKFilename`、`CelestialBody`.`OrbitSpiceKernelName`、`CelestialBody`.`NAIFId`
- 星固坐标架（Body-fixed frame）：
  - GMAT 核心：内置
  - IntrusionLocator：`CelestialBody`.`SpiceFrameId`、`CelestialBody`.`FrameSpiceKernelName`
- 闰秒：
  - GMAT 核心：启动文件 `LEAP_SECS_FILE` 设置
  - IntrusionLocator：`SolarSystem`.`LSKFilename`

更多详情请参阅 SolarSystem 和 CelestialBody。

### 搜索区间

`IntrusionLocator` 的搜索区间可以指定为航天器的整个历表区间，也可以指定为用户自定义区间。如果 `UseEntireInterval` 为 true，搜索将在航天器的整个历表区间上执行，包括任何空隙或不连续段。如果 `UseEntireInterval` 为 false，则直接使用提供的 `InitialEpoch` 和 `FinalEpoch` 构成搜索区间。用户必须确保所提供的区间对应有效的 `Spacecraft` 和 `CelestialBody` 历表历元。

### 运行模式

`IntrusionLocator` 与 `FindEvents` 命令协同工作：`IntrusionLocator` 资源定义事件搜索的配置，`FindEvents` 命令在任务序列的特定位置执行搜索。交互模式由 `IntrusionLocator`.`RunMode` 定义，它有三个选项：

- `Automatic`：所有 `FindEvents` 命令照常执行，另外在任务序列末尾自动执行一次额外的 `FindEvents`。
- `Manual`：所有 `FindEvents` 命令照常执行。
- `Disabled`：`FindEvents` 命令被忽略。

### 搜索算法

`IntrusionLocator` 使用 NAIF SPICE GF（几何查找器，geometry finder）子系统执行事件定位。具体来说，搜索使用以下调用：

- `gftfov_c`：用于侵入事件搜索
- `gfoclt_c`：用于第三体掩食和凌越（transit）搜索

这些函数实现了在区间上的定步长搜索方法，并在发现事件时嵌入求根定位步骤。`StepSize` 应设为要找到的最短事件持续时间，或事件之间最短间隔的长度，取两者中较小者。要保证能定位 10 秒的侵入或相邻侵入之间 10 秒的间隔，请设 `StepSize` = 10。

详情请参阅上面所列函数的参考文档。

### 报告格式

当启用 `WriteReport` 时，`IntrusionLocator` 在每次搜索执行结束时输出事件报告。报告包含以下数据：

- 航天器名称
- 传感器名称
- 坐标系名称
- 对于侵入事件期间的每个时间步：
  - 当前时间（UTC）
  - 侵入天体名称
  - 侵入天体的角直径（deg）。注意，对于航天器目标，该值为零，因为航天器用一个点表示。
  - 侵入天体在指定坐标系中的 "X" 坐标（deg）。对于 SensorFrame，这是传感器本地坐标系 X 方向上的角度。对于 FixedGrid，这是 EW（东西向）坐标。
  - 侵入天体在指定坐标系中的 "Y" 坐标（deg）。对于 SensorFrame，这是传感器本地坐标系 Y 方向上的角度。对于 FixedGrid，这是 NS（南北向）坐标。
  - 侵入事件类型（Intrusion 侵入、Transit 凌越、Occultation 掩食）。侵入和凌越显示完整事件，而掩食的开始和结束只有在落在同一侵入事件内时才显示，从而将其拆分为两个事件。

报告区分*单独*事件和*总*事件：

- *单独事件*（individual event）是在传感器视场内检测到侵入天体的单个事件。包括侵入的开始、结束以及其间按所提供 `StepSize` 发生的事件。
- *总事件*（total event）是嵌套单独事件的整个集合。每次侵入的开始都是一个新的总事件。换句话说，总事件的数量描述了侵入天体进入传感器视场的次数。

### 使用 SPK 传播器进行事件定位

使用 SPK 传播器时，你通过 Spacecraft.OrbitSpiceKernelName 字段加载一个或多个 SPK 历表文件。就事件定位而言，该字段会使相应的历表文件在运行时自动加载，因此不需要使用 Propagate 命令。这是在现有 SPK 历表文件上执行事件定位的简便方法。请参阅下面的示例。

## 示例

在 LEO（近地轨道）中执行基本的侵入搜索：

```
Create Spacecraft sat
sat.AddHardware = {camera}

Create ForceModel fm;

Create Propagator prop;
prop.FM = fm;
prop.Type = RungeKutta89;

Create Imager camera;
camera.FieldOfView = cameraFOV;
camera.DirectionX = 1.0;

Create ConicalFOV cameraFOV;
cameraFOV.FieldOfViewAngle = 11.50;

Create IntrusionLocator il;
il.CentralBody = Earth;
il.Spacecraft = sat;
il.Sensors = {camera};
il.IntrudingBodies = {Luna, Sun};
il.MinimumPhase = 0.6;
il.StepSize = 30.0;
il.UseLightTimeDelay = true;
il.UseStellarAberration = true;
il.WriteReport = true;
il.RunMode = Automatic;
il.UseEntireInterval = true;
il.Filename = 'ExampleIntrusionReport.txt';
il.ReportCoordinates = 'FixedGrid';
il.SpiceGridFrameFile = '../data/hardware/FixedGridFile.tf';

BeginMissionSequence;
Propagate prop(sat) {sat.ElapsedDays = 60.0};
```

说明：创建一颗装有成像仪（锥形视场，视场角 11.50 度）的卫星；侵入分析器以地球为中心天体，以月球和太阳为侵入天体，最小照明度 0.6，步长 30 秒，启用光行时延迟和恒星光行差，报告坐标采用 FixedGrid（使用指定的 SPICE 坐标架内核文件）；传播 60 天并自动执行侵入搜索。
