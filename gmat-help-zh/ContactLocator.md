# 可见性分析器（ContactLocator）
> 译自 GMAT R2026a 帮助文档 ContactLocator.html

**ContactLocator** —— 目标航天器（Spacecraft）与地面站（GroundStation）或行星表面区域（PlanetographicRegion）之间的视线（line-of-sight）事件定位器。

## 描述

> **注意**：`ContactLocator` 是基于 SPICE 的子系统，它使用的太阳系和天体配置与 GMAT 其他组件是并行的。对于精密应用，必须注意确保两套配置保持一致。详情请参阅"备注"。

`ContactLocator` 是一个事件定位器，用于查找 `Spacecraft`（航天器）与 `GroundStation`（地面站）或 `PlanetographicRegion`（行星表面区域）之间的视线可见（contact）事件。默认情况下，`ContactLocator` 生成一份文本事件报告，列出每个视线事件的开始和结束时间以及持续时间。可见性定位可以在整个传播区间或其子区间上执行，并且可以选择对光行时延迟和恒星光行差进行修正。可见性定位可以配置为搜索其他可能阻挡视线的 `CelestialBody`（天体）资源的掩食时刻，并可以将可见事件限制为地面站上配置的指定最小仰角。

可见性定位可以在一个 `Spacecraft`（`Target`，目标）与任意数量的 `GroundStation` 资源（`Observers`，观测者）之间执行。每个目标-观测者对单独搜索，并在结果报告中形成单独的部分。所有对必须使用相同的区间和搜索选项；若要按对定制选项，请使用多个 `ContactLocator` 资源。

通过在 `OccultingBodies`（掩食天体）列表中列出一个或多个 `CelestialBody` 资源，可以包含第三体掩食搜索。任何已配置的天体都可以用作掩食天体，包括用户自定义的天体。默认情况下不执行掩食搜索；地面站的中心天体会自动包含在基本视线算法中。

默认情况下，`ContactLocator` 在应用某些端点光行时修正后，搜索 `Target` 的整个传播区间；详情请参阅"备注"。要搜索自定义区间，请将 `UseEntireInterval` 设为 `False` 并相应地设置 `InitialEpoch` 和 `FinalEpoch`。注意，这些历元被假定为观测者处的历元，因此当通过光行时延迟和恒星光行差（如已配置）换算到目标时必须有效。如果它们落在 `Target` 的传播区间之外，GMAT 将显示错误。

可见性定位器可以选择对光行时延迟和恒星光行差进行修正，根据 `LightTimeDirection`（光行时方向）的值，使用发射方向（`Observer`→`Target`）或接收方向（`Observer`←`Target`）。光行时方向通过限制区间起点附近（发射方向）或区间终点附近（接收方向）的搜索来影响有效搜索区间。详情请参阅"备注"。恒星光行差仅应用于搜索的视线部分；它在掩食搜索期间没有影响。

事件搜索以固定步长遍历区间。你可以通过设置 `StepSize` 字段来控制步长（以秒为单位）。步长的合适选择是不大于视线函数周期的一半——即椭圆轨道的轨道周期的一半。如果使用第三体掩食，最大步长不大于你希望找到的最短掩食事件持续时间。详情请参阅"备注"。

GMAT 使用 SPICE 库作为基本的事件定位算法。因此，该子系统的所有天体数据都从 SPICE 内核加载，而不是使用 GMAT 自己的 `CelestialBody` 形状和定向配置。详情请参阅"备注"。

除非另有说明，`ContactLocator` 字段不能在任务序列中设置。

**另请参阅**：CelestialBody（天体）、GroundStation（地面站）、Spacecraft（航天器）、EclipseLocator（食分析器）、FindEvents（事件查找）

## 字段

| 字段 | 描述 |
|------|------|
| **Filename** | 可见性报告文件的名称和路径。该字段可以在任务序列中设置。<br>数据类型：字符串<br>允许值：有效的文件路径<br>访问权限：set<br>默认值：`'ContactLocator.txt'`<br>单位：N/A<br>接口：GUI、脚本 |
| **FinalEpoch** | 搜索可见事件的最后一个历元，格式由 `InputEpochFormat` 指定。该历元相对于 `Observer`（观测者），并且（包括任何光行时在内）必须映射到 `Target`（目标）历表区间内的有效历元。该字段可以在任务序列中设置。<br>数据类型：字符串<br>允许值：可用航天器历表中的有效历元<br>访问权限：set<br>默认值：`'21545.138'`<br>单位：ModifiedJulian 历元格式：天；Gregorian 历元格式：N/A<br>接口：GUI、脚本 |
| **InitialEpoch** | 搜索可见事件的第一个历元，格式由 `InputEpochFormat` 指定。该历元相对于 `Observer`，并且（包括任何光行时在内）必须映射到 `Target` 历表区间内的有效历元。该字段可以在任务序列中设置。<br>数据类型：字符串<br>允许值：可用航天器历表中的有效历元<br>访问权限：set<br>默认值：`'21545'`<br>单位：ModifiedJulian 历元格式：天；Gregorian 历元格式：N/A<br>接口：GUI、脚本 |
| **InputEpochFormat** | 该字段允许你设置选择为 `InitialEpoch` 和 `FinalEpoch` 字段输入的历元类型。该字段不能在任务序列中修改。<br>数据类型：枚举<br>允许值：以下任意历元格式：`UTCGregorian`、`UTCModJulian`、`TAIGregorian`、`TAIModJulian`、`TTGregorian`、`TTModJulian`、`A1Gregorian`、`A1ModJulian`<br>访问权限：set<br>默认值：`TAIModJulian`<br>单位：N/A<br>接口：GUI、脚本 |
| **IntervalStepSize** | 确定中间步长报告的时间区间分辨率。如果设为 0，则只记录可见时段的开始和结束。<br>数据类型：实数<br>允许值：正实数<br>访问权限：set<br>默认值：`0.0`<br>单位：秒<br>接口：脚本 |
| **LeftJustified** | 修改可见性报告，使各列左对齐或右对齐。<br>数据类型：布尔值<br>允许值：true、false<br>访问权限：set<br>默认值：false<br>单位：N/A<br>接口：脚本 |
| **LightTimeDirection** | 光行时计算的方向：从观测者发射或在观测者处接收。<br>数据类型：枚举<br>允许值：`Transmit`（发射）、`Receive`（接收）<br>访问权限：set<br>默认值：`Transmit`<br>单位：N/A<br>接口：GUI、脚本 |
| **Observers** | 可见性观测者对象的列表。可以是任意数量的 GMAT `GroundStation` 资源。观测将使用地面站的最小仰角，以及其天线上挂载的任何视场（FOV，如果有）来计算。这些地面站的中心天体必须是 `Planet`（行星）或 `Moon`（卫星）。对于到 `PlanetographicRegion` 的可见性定位，观测者是飞越所定义区域的航天器。<br>数据类型：`GroundStation` 资源列表，或单个 `Spacecraft` 资源（仅限 `PlanetographicRegion` 飞越查找）<br>允许值：任何现有的 `GroundStation` 或 `Spacecraft` 资源<br>访问权限：set<br>默认值：空列表<br>单位：N/A<br>接口：GUI、脚本 |
| **OccultingBodies** | 要搜索掩食的掩食天体列表。可以是任意数量的 GMAT `CelestialBody` 类型资源，如 `Planet`、`Moon`、`Asteroid` 等。注意，掩食天体必须有质量（例如不能是 `LibrationPoint`（天平动点）或 `Barycenter`（质心））。<br>数据类型：`CelestialBody` 资源列表（如 `Planet`、`Asteroid`、`Moon` 等）<br>允许值：任何现有的 `CelestialBody` 类资源<br>访问权限：set<br>默认值：空列表<br>单位：N/A<br>接口：GUI、脚本 |
| **ReportPrecision** | 修改可见性报告中除时间以外字段的精度。<br>数据类型：整数<br>允许值：正整数<br>访问权限：set<br>默认值：`6`<br>单位：N/A<br>接口：脚本 |
| **ReportFormat** | 定义 ContactLocator 返回的报告样式。<br>数据类型：枚举<br>允许值：`SiteViewMaxElevationReport`、`ContactRangeReport`、`AzimuthElevationRangeReport`、`AzimuthElevationRangeRangeRateReport`、`SiteViewMaxElevationRangeReport`、`Legacy`<br>访问权限：set<br>默认值：`Legacy`<br>单位：N/A<br>接口：脚本 |
| **ReportTimeFormat** | 确定 ContactLocator 报告文件中写入的时间格式。不影响 'Legacy' 格式的报告。<br>数据类型：枚举<br>允许值：`UTCGregorian`、`UTCMJD`、`ISOYD`<br>访问权限：set<br>默认值：`UTCGregorian`<br>单位：N/A<br>接口：脚本 |
| **RunMode** | 事件定位的执行模式。`'Automatic'` 触发事件定位在运行结束时自动执行。`'Manual'` 将执行限制为仅由 `FindEvents` 命令触发。`'Disabled'` 完全关闭事件定位。<br>数据类型：枚举<br>允许值：`Automatic`、`Manual`、`Disabled`<br>访问权限：set<br>默认值：`'Automatic'`<br>单位：N/A<br>接口：GUI、脚本 |
| **StepSize** | 事件定位器的步长。有关合适取值的讨论，请参阅"备注"。<br>数据类型：实数<br>允许值：`StepSize` > 0<br>访问权限：set<br>默认值：10<br>单位：s<br>接口：GUI、脚本 |
| **Target** | 要搜索可见事件的目标 `Spacecraft` 或 `PlanetographicRegion` 资源。<br>数据类型：`Spacecraft` 或 `PlanetographicRegion` 资源<br>允许值：任何现有的 `Spacecraft` 或 `PlanetographicRegion` 资源<br>访问权限：set<br>默认值：第一个已配置的 `Spacecraft` 资源<br>单位：N/A<br>接口：GUI、脚本 |
| **UseEntireInterval** | 在适当对端点进行光行时延迟修正后，搜索整个可用的 `Target` 历表区间。详情请参阅"备注"。该字段可以在任务序列中设置。<br>数据类型：布尔值<br>允许值：true、false<br>访问权限：set<br>默认值：true<br>单位：N/A<br>接口：GUI、脚本 |
| **UseLightTimeDelay** | 在事件查找算法中使用光行时延迟。时钟始终设在观测者（`Observer`）上。有关计算方法的更多信息，请参阅参考文献中 SPICE 光行差修正文档的链接。<br>数据类型：布尔值<br>允许值：true、false<br>访问权限：set<br>默认值：true<br>单位：N/A<br>接口：GUI、脚本 |
| **UseStellarAberration** | 在事件查找算法中，除光行时延迟外还使用恒星光行差。必须启用光行时延迟。恒星光行差只影响视线搜索，不影响掩食搜索。<br>数据类型：布尔值<br>允许值：true、false<br>访问权限：set<br>默认值：true<br>单位：N/A<br>接口：GUI、脚本 |
| **WriteReport** | 执行事件定位时写出事件报告。该字段可以在任务序列中设置。<br>数据类型：布尔值<br>允许值：true、false<br>访问权限：set<br>默认值：true<br>单位：N/A<br>接口：GUI、脚本 |

## GUI

> [图：ContactLocator 默认 GUI 面板]

上图显示了新资源的默认 `ContactLocator` GUI。你可以从 **Target**（目标）中选择一个 `Spacecraft`，该列表由任务中当前配置的所有 `Spacecraft` 资源填充。在 **Observers**（观测者）列表中，你可以勾选要在可见性搜索中使用的所有 `GroundStation` 旁边的复选框。

要搜索第三体掩食，请勾选 **Occulting Bodies**（掩食天体）列表中任何适用的 `CelestialBody` 资源旁边的复选框。该列表显示任务中当前配置的所有天体。注意，每项掩食搜索都会增加整体搜索的执行时间。

你可以通过底部的 **Filename**、**Run Mode**（运行模式）和 **Write Report**（写报告）来配置输出。如果启用了 **Write Report**，文本报告将写入 **Filename** 指定的文件。根据 **Run Mode** 的不同，搜索将在 `FindEvents` 命令期间执行（`Manual` 或 `Automatic` 模式），并在任务结束时自动执行（`Automatic` 模式）。

你可以通过右上角的选项配置搜索区间。取消勾选 **Use Entire Interval**（使用整个区间）可手动设置搜索区间。设置搜索区间时的注意事项请参阅"备注"一节。

你可以通过右下角的选项控制搜索算法。通过各复选框配置光行时和恒星光行差，并通过 **Light-time direction**（光行时方向）选择信号方向。

要控制搜索的保真度和执行时间，请适当设置 **Step size**（步长）。详情请参阅"备注"一节。

注意，用于 `PlanetographicRegion` 飞越搜索的 `ContactLocator` 配置目前不能通过 GUI 面板完成，只能在脚本中完成。

## 脚本编写

除了 GUI 提供的基本 ContactLocator 选项外，GMAT 还提供了许多只能通过脚本界面访问的附加报告定制选项。要创建在可见时段内按设定区间给出信息的报告，用户可以将 **IntervalStepSize** 设为以秒为单位的正值。最后，使用 **ReportPrecision** 和 **LeftJustified** 可以更精细地配置高级输出。

## 备注

### 数据配置

`ContactLocator` 的实现基于 [NAIF SPICE 工具包](https://naif.jpl.nasa.gov/naif/)，它对环境数据（如天体形状和定向、行星星历、天体专用坐标架定义和闰秒）使用不同的机制。因此，必须维护两套并行的配置，以确保事件定位结果与 GMAT 自身的传播和其他参数保持一致。需要维护的具体数据为：

- 行星形状和定向：
  - GMAT 核心：`CelestialBody`.`EquatorialRadius`（赤道半径）、`Flattening`（扁率）、`SpinAxisRAConstant`（自转轴赤经常数项）、`SpinAxisRARate`（自转轴赤经变化率）等。
  - ContactLocator：`SolarSystem`.`PCKFilename`、`CelestialBody`.`PlanetarySpiceKernelName`
- 行星星历：
  - GMAT 核心：`SolarSystem`.`DEFilename`，或（`SolarSystem`.`SPKFilename`、`CelestialBody`.`OrbitSpiceKernelName`、`CelestialBody`.`NAIFId`）
  - ContactLocator：`SolarSystem`.`SPKFilename`、`CelestialBody`.`OrbitSpiceKernelName`、`CelestialBody`.`NAIFId`
- 星固坐标架（Body-fixed frame）：
  - GMAT 核心：内置
  - ContactLocator：`CelestialBody`.`SpiceFrameId`、`CelestialBody`.`FrameSpiceKernelName`
- 闰秒：
  - GMAT 核心：启动文件 `LEAP_SECS_FILE` 设置
  - ContactLocator：`SolarSystem`.`LSKFilename`

> **注意**：对于精密应用，`CelestialBody` 的形状必须在两个子系统中保持一致，以确保 `GroundStation` 的位置一致。以下脚本行使地球的两种定义保持一致。

```
SolarSystem.PCKFilename = '..\data\planetary_coeff\pck00010.tpc'
Earth.EquatorialRadius = 6378.1366
Earth.Flattening = 0.00335281310845547
```

更多详情请参阅 SolarSystem 和 CelestialBody。

### 搜索区间

`ContactLocator` 的搜索区间可以指定为 `Target`（目标）的整个历表区间，也可以指定为用户自定义区间。每种模式在处理光行时延迟和不连续区间方面都有特定的行为。

如果 `UseEntireInterval` 为 true，搜索将在 `Target` 的整个历表区间上执行，包括任何空隙或不连续段。如果启用了光行时延迟，搜索区间将被截去近似光行时长度，以便 SPICE 在搜索期间确定参与者之间的精确光行时延迟。如果 `LightTimeDirection` 为 `Transmit`（发射），则截去区间的起点；如果 `LightTimeDirection` 为 `Receive`（接收），则截去区间的终点。无论哪种情况，区间的另一端都会通过二分法稍作裁剪，以避免因数值精度问题而超出历表末端。这种裁剪通常小于 1 s。空隙或不连续段的端点不会被修改，因此在启用光行时延迟时不完全支持这些情况。如果禁用光行时延迟，则直接使用整个区间，不做任何端点处理。

如果 `UseEntireInterval` 为 false，则直接使用提供的 `InitialEpoch` 和 `FinalEpoch` 构成搜索区间。该区间与 `Observer`（观测者）时钟一致，不支持包含 `Target` 历表中的空隙或不连续段。用户必须确保所提供的区间在应用光行时延迟和恒星光行差之后对应有效的 `Target` 历表历元。

这些规则总结在下表中，其中 t₀ 和 t_f 分别为 `Target` 历表的起点和终点，lt 为 `Target` 与 `Observer` 之间的光行时。

| | **UseEntireInterval** = true | **UseEntireInterval** = false |
|---|---|---|
| **UseLightTimeDelay** = true | 有效区间：`LightTimeDirection` = `'Transmit'`：[t₀+lt, t_f]；`LightTimeDirection` = `'Receive'`：[t₀, t_f-lt]<br>不连续区间：不支持，行为未定义。 | 有效区间：[InitialEpoch, FinalEpoch]<br>不连续区间：不支持，行为未定义。 |
| **UseLightTimeDelay** = false | 有效区间：[t₀, t_f]<br>不连续区间：完全支持 | 有效区间：[InitialEpoch, FinalEpoch]<br>不连续区间：完全支持 |

### 运行模式

`ContactLocator` 与 `FindEvents` 命令协同工作：`ContactLocator` 资源定义事件搜索的配置，`FindEvents` 命令在任务序列的特定位置执行搜索。交互模式由 `ContactLocator`.`RunMode` 定义，它有三个选项：

- `Automatic`：所有 `FindEvents` 命令照常执行，另外在任务序列末尾自动执行一次额外的 `FindEvents`。
- `Manual`：所有 `FindEvents` 命令照常执行。
- `Disabled`：`FindEvents` 命令被忽略。

### 观测者视场

可见性定位器有两种确定观测者视场的方法。最基本的方法是初始化一个定义了 `MinimumElevationAngle`（最小仰角）的 `GroundStation`。这种方法使用距地平线恒定仰角作为可见性阈值。如果为地面站定义了 `HorizonMaskFileName`（地平线遮蔽文件），则使用遮蔽文件中定义的遮蔽剖面来确定可见性。对于更复杂的观测者，用户可以为地面站挂载带有 CircularFOV（圆形视场）、RectangularFOV（矩形视场）或 CustomFOV（自定义视场）的成像仪。对于 ContactLocator 中的每个观测者，GMAT 将对每个带有 FOV 的 Imager 单独进行搜索，并在报告中分别列出可见事件。

### 搜索算法

`ContactLocator` 使用 NAIF SPICE GF（几何查找器，geometry finder）子系统执行事件定位。具体来说，为找到初始可见窗口，GMAT 使用以下两个函数所找到窗口的交集：

- `gfposc_c`：用于在 `GroundStation.MinimumElevationAngle`（最小仰角）以上的视线搜索
- `gftfov_c`：用于在任何挂载的 **Imager** 的 **FOV**（视场）内的视线搜索（如果没有可用视场则忽略）

执行掩食计算时使用以下调用：

- `gfoclt_c`：用于第三体掩食搜索

所有函数都实现了在区间上的定步长搜索方法，并在发现事件时嵌入求根定位步骤。两类搜索的 `StepSize` 正确选择方式不同。

对于不含第三体掩食的基本视线搜索，`StepSize` 最高可设为事件函数周期的一半。对于椭圆轨道，最高可达轨道周期的一半。但请注意，当计算对使用地平线遮蔽（通过 `GroundStation` 的 `HorizonMaskFileName` 或传感器 `FieldOfView`）的 `GroundStation` 的可见时段时，`StepSize` 应根据地平线遮蔽的分辨率来定。如果步长太大，GMAT 可能会完全跨过遮蔽的某些部分，导致可见时段不正确或遗漏某些事件。

对于第三体掩食，`StepSize` 应设为要找到的最短事件持续时间，或事件之间最短间隔的长度，取两者中较小者。要保证能定位 10 秒的掩食，请设 `StepSize` = 10。

如果不需要查找第三体掩食，可以按照上述说明增大 `StepSize` 来提高搜索性能。

更多详情请参阅上面链接的两个函数的参考文档。

### 报告格式

当启用 `WriteReport` 时，`ContactLocator` 在每次搜索执行结束时输出事件报告。共有六种报告类型。"Legacy"（传统）报告包含以下数据：

- 目标名称
- 对于每个观测者：
  - 观测者名称
  - 对于每个事件：
    - 事件开始时间（UTC）
    - 事件结束时间（UTC）
    - 持续时间（s）
  - 事件总数

Legacy 格式的示例报告如下所示。

```
Target: DefaultSC

Observer: GroundStation1
Start Time (UTC)            Stop Time (UTC)               Duration (s)         
01 Jan 2000 13:18:45.268    01 Jan 2000 13:29:54.824      669.55576907    
01 Jan 2000 15:06:44.752    01 Jan 2000 15:18:22.762      698.01023654    


Number of events : 2


Observer: GroundStation2
Start Time (UTC)            Stop Time (UTC)               Duration (s)         
01 Jan 2000 13:36:13.792    01 Jan 2000 13:47:51.717      697.92488540    


Number of events : 1
```

"SiteViewMaxElevationReport" 报告包含以下数据：

- 目标名称
- 对于每次观测：
  - 观测者名称
  - 对于每个事件：
    - 事件开始时间（ReportTimeFormat）
    - 事件结束时间（ReportTimeFormat）
    - 持续时间（s）
    - 最大仰角（度）
    - 最大仰角时刻（ReportTimeFormat）

"SiteViewMaxElevationRangeReport" 报告包含以下数据：

- 目标名称
- 对于每次观测：
  - 观测者名称
  - 对于每个事件：
    - 事件开始时间（ReportTimeFormat）
    - 事件结束时间（ReportTimeFormat）
    - 持续时间（s）
    - 最大仰角（度）
    - 最大仰角时刻（ReportTimeFormat）
    - 开始时刻的距离
    - 结束时刻的距离

"AzimuthElevationRangeReport" 报告使用 IntervalStepSize 参数生成以下数据：

- 目标名称
- 对于每次观测：
  - 过境（Pass）编号
  - 观测者名称
  - 对于每个时间戳：
    - 方位角（度）
    - 仰角（度）
    - 距离（km）

"AzimuthElevationRangeRangeRateReport" 报告使用 IntervalStepSize 参数生成以下数据：

- 目标名称
- 对于每次观测：
  - 过境（Pass）编号
  - 观测者名称
  - 对于每个时间戳：
    - 方位角（度）
    - 仰角（度）
    - 距离（km）
    - 距离变化率（km/s）

"ContactRangeReport" 报告包含以下数据：

- 目标名称
- 对于每个观测者：
  - 观测者名称
  - 对于每个事件：
    - 持续时间（s）
    - 事件开始时间
    - 事件结束时间
    - 开始时刻的距离
    - 结束时刻的距离

### 使用 SPK 传播器进行事件定位

使用 SPK 传播器时，你通过 `Spacecraft`.`OrbitSpiceKernelName` 字段加载一个或多个 SPK 历表文件。就事件定位而言，该字段会使相应的历表文件在运行时自动加载，因此不需要使用 `Propagate` 命令。这是在现有 SPK 历表文件上执行事件定位的简便方法。请参阅下面的示例。

## 示例

在 LEO（近地轨道）中执行基本的可见性搜索：

```
SolarSystem.EphemerisSource = 'DE421'

Earth.EquatorialRadius = 6378.1366
Earth.Flattening       = 0.00335281310845547

Create Spacecraft sat

sat.DateFormat       = UTCGregorian
sat.Epoch            = '15 Sep 2010 16:00:00.000'
sat.CoordinateSystem = EarthMJ2000Eq
sat.DisplayStateType = Keplerian
sat.SMA              = 6678.14
sat.ECC              = 0.001
sat.INC              = 0
sat.RAAN             = 0
sat.AOP              = 0
sat.TA               = 180

Create ForceModel fm

fm.CentralBody = Earth
fm.PointMasses = {Earth}

Create Propagator prop

prop.FM   = fm
prop.Type = RungeKutta89

Create GroundStation GS

GS.CentralBody      = Earth
GS.StateType        = Spherical
GS.HorizonReference = Ellipsoid
GS.Location1        = 0
GS.Location2        = 0
GS.Location3        = 0

Create ContactLocator cl

cl.Target    = sat
cl.Observers = {GS}
cl.Filename  = 'Simple.report'

BeginMissionSequence

Propagate prop(sat) {sat.ElapsedSecs = 10800}
```

说明：使用 DE421 历表并显式设置地球赤道半径和扁率（与 SPICE 配置保持一致）；创建近地轨道卫星和位于赤道本初子午线的地面站；可见性分析器以卫星为目标、地面站为观测者；传播 3 小时并输出可见性报告。

执行从地球地面站到火星轨道器的可见性事件搜索，包含火卫一（Phobos）掩食。所需的 mar063.bsp 文件可在 https://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/a_old_versions/mar063.cmt 找到。

```
% Mars orbiter, 2 days, Mars and Phobos eclipses

SolarSystem.EphemerisSource = 'SPICE'
SolarSystem.SPKFilename     = 'de421.bsp'

Mars.OrbitSpiceKernelName = '../data/planetary_ephem/spk/mar063.bsp'

Earth.EquatorialRadius = 6378.1366
Earth.Flattening       = 0.00335281310845547

Create CoordinateSystem MarsMJ2000Eq

MarsMJ2000Eq.Origin = Mars
MarsMJ2000Eq.Axes   = MJ2000Eq

Create Spacecraft sat

sat.DateFormat       = UTCGregorian
sat.Epoch            = '11 Mar 2004 12:00:00.000'
sat.CoordinateSystem = MarsMJ2000Eq
sat.DisplayStateType = Cartesian
sat.X                = -1.436997966893255e+003
sat.Y                = 2.336077717512823e+003
sat.Z                = 2.477821416108639e+003
sat.VX               = -2.978497667195258e+000
sat.VY               = -1.638005864673213e+000
sat.VZ               = -1.836385137438366e-001

Create ForceModel fm

fm.CentralBody = Mars
fm.PointMasses = {Mars}

Create Propagator prop

prop.FM   = fm
prop.Type = RungeKutta89

Create Moon Phobos

Phobos.CentralBody          = 'Mars'
Phobos.PosVelSource         = 'SPICE'
Phobos.NAIFId               = 401
Phobos.OrbitSpiceKernelName = {'mar063.bsp'}
Phobos.SpiceFrameId         = 'IAU_PHOBOS'
Phobos.EquatorialRadius     = 13.5
Phobos.Flattening           = 0.3185185185185186
Phobos.Mu                   = 7.093399e-004

Create Moon Deimos

Deimos.CentralBody          = 'Mars'
Deimos.PosVelSource         = 'SPICE'
Deimos.NAIFId               = 402
Deimos.OrbitSpiceKernelName = {'mar063.bsp'}
Deimos.SpiceFrameId         = 'IAU_DEIMOS'
Deimos.EquatorialRadius     = 7.5
Deimos.Flattening           = 0.30666666666666664
Deimos.Mu                   = 1.588174e-004

Create GroundStation GS

GS.CentralBody      = Earth
GS.StateType        = Spherical
GS.HorizonReference = Ellipsoid
GS.Location1        = 36.3269
GS.Location2        = 127.433
GS.Location3        = 0.081

Create ContactLocator cl

cl.Target          = sat
cl.Observers       = {GS}
cl.OccultingBodies = {Sun, Mercury, Venus, Luna, Mars, Phobos, Deimos}
cl.Filename        = 'Martian.report'
cl.StepSize        = 5

BeginMissionSequence

Propagate prop(sat) {sat.ElapsedDays = 2}
```

说明：使用 SPICE 历表配置火星轨道器；定义火卫一、火卫二；地面站位于北纬 36.3269°、东经 127.433°、高程 0.081 km；可见性搜索包含太阳、水星、金星、月球、火星、火卫一、火卫二的第三体掩食，步长 5 秒，传播 2 天。

在现有 SPK 历表文件上执行可见性定位：

```
SolarSystem.EphemerisSource = 'DE421'

Earth.EquatorialRadius = 6378.1366
Earth.Flattening       = 0.00335281310845547

Create Spacecraft sat

sat.OrbitSpiceKernelName = {'../data/vehicle/ephem/spk/MoonTransfer.bsp'}
sat.NAIFId               = -123456789

Create GroundStation GS

GS.CentralBody      = Earth
GS.StateType        = Spherical
GS.HorizonReference = Ellipsoid
GS.Location1        = 0
GS.Location2        = 0
GS.Location3        = 0

Create ContactLocator cl

cl.Target    = sat
cl.Observers = {GS}
cl.Filename  = 'SPKPropagation.report'

BeginMissionSequence
```

说明：通过 `sat.OrbitSpiceKernelName` 直接加载已有的 SPK 历表文件并指定 NAIF ID，无需 Propagate 命令即可执行可见性定位。

在 LEO 中使用台站遮蔽（station mask）执行可见性搜索：

```
Create Spacecraft sat

sat.DateFormat       = UTCGregorian
sat.Epoch            = '15 Sep 2010 16:00:00.000'
sat.CoordinateSystem = EarthMJ2000Eq
sat.DisplayStateType = Keplerian
sat.SMA              = 6678.14
sat.ECC              = 0.001
sat.INC              = 0
sat.RAAN             = 0
sat.AOP              = 0
sat.TA               = 180

Create ForceModel fm

fm.CentralBody = Earth
fm.PointMasses = {Earth}

Create Propagator prop

prop.FM   = fm
prop.Type = RungeKutta89

Create CustomFOV ArrowFOV

ArrowFOV.Elevation = [ 75 75 82 75 75 82 75 ]
ArrowFOV.Azimuth   = [ 0 90 90.09999999999999 150 210 270 270.1 ]

Create Antenna CustomAntenna

CustomAntenna.FieldOfView = ArrowFOV
CustomAntenna.DirectionX  = 0
CustomAntenna.DirectionY  = 0
CustomAntenna.DirectionZ  = 1

Create GroundStation GS

GS.CentralBody      = Earth
GS.StateType        = Spherical
GS.HorizonReference = Ellipsoid
GS.Location1        = 0
GS.Location2        = 0
GS.Location3        = 0
GS.AddHardware      = {CustomAntenna}

Create ContactLocator cl

cl.Target    = sat
cl.Observers = {GS}
cl.Filename  = 'Simple.report'

BeginMissionSequence

Propagate prop(sat) {sat.ElapsedSecs = 10800}
```

说明：为地面站挂载一个带自定义视场（CustomFOV，按方位角/仰角点定义的箭头形遮蔽剖面）的天线，可见性搜索将使用该视场作为可见性判据。

在 LEO 中使用高级报告执行可见性搜索：

```
Create Spacecraft sat

sat.DateFormat       = UTCGregorian
sat.Epoch            = '15 Sep 2010 16:00:00.000'
sat.CoordinateSystem = EarthMJ2000Eq
sat.DisplayStateType = Keplerian
sat.SMA              = 6678.14
sat.ECC              = 0.001
sat.INC              = 0
sat.RAAN             = 0
sat.AOP              = 0
sat.TA               = 180

Create ForceModel fm

fm.CentralBody = Earth
fm.PointMasses = {Earth}

Create Propagator prop

prop.FM   = fm
prop.Type = RungeKutta89

Create GroundStation GS

GS.CentralBody      = Earth
GS.StateType        = Spherical
GS.HorizonReference = Ellipsoid
GS.Location1        = 0
GS.Location2        = 0
GS.Location3        = 0

Create ContactLocator cl

cl.Target           = sat
cl.Filename         = 'Advanced.report'
cl.Observers        = {GS}
cl.LeftJustified    = false
cl.ReportPrecision  = 6
cl.IntervalStepSize = 60
cl.ReportTimeFormat = 'UTCGregorian'
cl.ReportFormat     = 'AzimuthElevationRangeReport'

BeginMissionSequence

Propagate prop(sat) {sat.ElapsedSecs = 10800}
```

说明：使用 `AzimuthElevationRangeReport` 报告格式，在可见时段内每 60 秒输出一次方位角、仰角和距离，报告精度为 6 位有效数字，时间格式为 UTCGregorian。

在 LEO 中使用区间报告执行可见性搜索：

```
Create Spacecraft sat

sat.DateFormat       = UTCGregorian
sat.Epoch            = '15 Sep 2010 16:00:00.000'
sat.CoordinateSystem = EarthMJ2000Eq
sat.DisplayStateType = Keplerian
sat.SMA              = 6678.14
sat.ECC              = 0.001
sat.INC              = 0
sat.RAAN             = 0
sat.AOP              = 0
sat.TA               = 180

Create ForceModel fm

fm.CentralBody = Earth
fm.PointMasses = {Earth}

Create Propagator prop

prop.FM   = fm
prop.Type = RungeKutta89

Create GroundStation GS

GS.CentralBody      = Earth
GS.StateType        = Spherical
GS.HorizonReference = Ellipsoid
GS.Location1        = 0
GS.Location2        = 0
GS.Location3        = 0

Create ContactLocator cl

cl.Target             = sat
cl.Filename           = 'Interval.report'
cl.Observers          = {GS}
cl.LightTimeDirection = Transmit
cl.LeftJustified      = true
cl.ReportPrecision    = 6
cl.IntervalStepSize   = 60
cl.ReportTimeFormat   = 'UTCGregorian'
cl.ReportFormat       = 'AzimuthElevationRangeReport'

BeginMissionSequence

Propagate prop(sat) {sat.ElapsedSecs = 10800}
```

说明：与上例类似，但光行时方向设为 Transmit（从观测者发射），并将报告列设为左对齐（`LeftJustified = true`）。

## 参考文献

1. SPICE Toolkit Documentation, [Aberration Corrections Required Reading](https://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/abcorr.html)（光行差修正必读）
