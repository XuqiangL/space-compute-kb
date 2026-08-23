# 坐标系（CoordinateSystem）
> 译自 GMAT R2026a 帮助文档 CoordinateSystem.html

**CoordinateSystem** —— 一对轴系与原点的组合。

## 描述

GMAT 中的 `CoordinateSystem`（坐标系）定义为原点与轴系的组合。你可以从各种点中选择 `CoordinateSystem` 的原点，例如 `CelestialBody`（天体）、`Spacecraft`（航天器）、`GroundStation`（地面站）或 `LibrationPoint`（天平动点）等。GMAT 支持众多轴系，如 J2000 赤道（J2000 equator）、J2000 黄道（J2000 ecliptic）、`ICRF`（国际天球参考架）、`ITRF`（国际地球参考架）、`Topocentric`（站心）和 `ObjectReferenced`（对象参考）等。`CoordinateSystem` 与 GMAT 深度集成，使你能够以与应用相关的坐标系定义、报告和可视化数据。该资源不能在任务序列（Mission Sequence）中修改。

**另请参阅**：Spacecraft（航天器）、Calculation Parameters（计算参数）、OrbitView（轨道视图）

## 字段

| 字段 | 描述 |
|------|------|
| **AlignmentVectorX** | `AlignmentVector`（对准向量）在本地坐标架中表达的 x 分量（例如，在 `LocalAlignedConstrained` 坐标架中表达）。用于以下轴系：`LocalAlignedConstrained`。<br>数据类型：实数<br>允许值：-∞ < 实数 < ∞（`AlignmentVector` 的模 >= 1e-9）<br>访问权限：set<br>默认值：`1`<br>单位：N/A<br>接口：GUI、脚本 |
| **AlignmentVectorY** | `AlignmentVector` 在本地坐标架中表达的 y 分量（例如，在 `LocalAlignedConstrained` 坐标架中表达）。用于以下轴系：`LocalAlignedConstrained`。<br>数据类型：实数<br>允许值：-∞ < 实数 < ∞（`AlignmentVector` 的模 >= 1e-9）<br>访问权限：set<br>默认值：`0`<br>单位：N/A<br>接口：GUI、脚本 |
| **AlignmentVectorZ** | `AlignmentVector` 在本地坐标架中表达的 z 分量（例如，在 `LocalAlignedConstrained` 坐标架中表达）。用于以下轴系：`LocalAlignedConstrained`。<br>数据类型：实数<br>允许值：-∞ < 实数 < ∞（`AlignmentVector` 的模 >= 1e-9）<br>访问权限：set<br>默认值：`0`<br>单位：N/A<br>接口：GUI、脚本 |
| **Axes** | `CoordinateSystem` 的轴系。<br>数据类型：字符串<br>允许值：`MJ2000Eq`、`MJ2000Ec`、`ICRF`、`MODEq`、`MODEc`、`TODEq`、`TODEc`、`MOEEq`、`MOEEc`、`TOEEq`、`TOEEc`、`TEME`、`ObjectReferenced`、`LocalAlignedConstrained`、`Equator`、`BodyFixed`、`BodyInertial`、`GSE`、`GSM`、`Topocentric`、`BodySpinSun`、`SPICE`<br>访问权限：set<br>默认值：`MJ2000Eq`<br>单位：N/A<br>接口：GUI、脚本 |
| **ConstraintVectorX** | `ConstraintVector`（约束向量）在本地坐标架中表达的 x 分量（例如，在 `LocalAlignedConstrained` 坐标架中表达）。用于以下轴系：`LocalAlignedConstrained`。<br>数据类型：实数<br>允许值：-∞ < 实数 < ∞（`ConstraintVector` 的模 >= 1e-9）<br>访问权限：set<br>默认值：`0`<br>单位：N/A<br>接口：GUI、脚本 |
| **ConstraintVectorY** | `ConstraintVector` 在本地坐标架中表达的 y 分量（例如，在 `LocalAlignedConstrained` 坐标架中表达）。用于以下轴系：`LocalAlignedConstrained`。<br>数据类型：实数<br>允许值：-∞ < 实数 < ∞（`ConstraintVector` 的模 >= 1e-9）<br>访问权限：set<br>默认值：`0`<br>单位：N/A<br>接口：GUI、脚本 |
| **ConstraintVectorZ** | `ConstraintVector` 在本地坐标架中表达的 z 分量（例如，在 `LocalAlignedConstrained` 坐标架中表达）。用于以下轴系：`LocalAlignedConstrained`。<br>数据类型：实数<br>允许值：-∞ < 实数 < ∞（`ConstraintVector` 的模 >= 1e-9）<br>访问权限：set<br>默认值：`1`<br>单位：N/A<br>接口：GUI、脚本 |
| **ConstraintReferenceVectorX** | `ConstraintReferenceVector`（约束参考向量）在 `ConstraintCoordinateSystem`（约束坐标系）中表达的 x 分量。用于以下轴系：`LocalAlignedConstrained`。<br>数据类型：实数<br>允许值：-∞ < 实数 < ∞（`ConstraintReferenceVector` 的模 >= 1e-9）<br>访问权限：set<br>默认值：`0`<br>单位：N/A<br>接口：GUI、脚本 |
| **ConstraintReferenceVectorY** | `ConstraintReferenceVector` 在 `ConstraintCoordinateSystem` 中表达的 y 分量。用于以下轴系：`LocalAlignedConstrained`。<br>数据类型：实数<br>允许值：-∞ < 实数 < ∞（`ConstraintReferenceVector` 的模 >= 1e-9）<br>访问权限：set<br>默认值：`0`<br>单位：N/A<br>接口：GUI、脚本 |
| **ConstraintReferenceVectorZ** | `ConstraintReferenceVector` 在 `ConstraintCoordinateSystem` 中表达的 z 分量。用于以下轴系：`LocalAlignedConstrained`。<br>数据类型：实数<br>允许值：-∞ < 实数 < ∞（`ConstraintReferenceVector` 的模 >= 1e-9）<br>访问权限：set<br>默认值：`1`<br>单位：N/A<br>接口：GUI、脚本 |
| **ConstraintCoordinateSystem** | `ConstraintReferenceVector` 所用的坐标系。用于以下轴系：`LocalAlignedConstrained`。<br>数据类型：资源<br>允许值：`CoordinateSystem`<br>访问权限：set<br>默认值：`EarthMJ2000Eq`<br>单位：N/A<br>接口：GUI、脚本 |
| **Epoch** | `CoordinateSystem` 的参考历元。该字段仅用于 `TOE` 和 `MOE` 轴类型。<br>数据类型：字符串<br>允许值：A1 修正儒略历元。<br>访问权限：set<br>默认值：21545<br>单位：修正儒略日（Modified Julian Date）<br>接口：GUI、脚本 |
| **Origin** | `CoordinateSystem` 的原点。<br>数据类型：字符串<br>允许值：`CelestialBody`（天体）、`Spacecraft`（航天器）、`LibrationPoint`（天平动点）、`Barycenter`（质心）、`SolarSystemBarycenter`（太阳系质心）、`GroundStation`（地面站）<br>访问权限：set<br>默认值：`Earth`<br>单位：N/A<br>接口：GUI、脚本 |
| **Primary** | `ObjectReferenced`（对象参考）轴系的主天体。该字段仅在 `Axes` = `ObjectReferenced` 时使用。有关 `Primary` 和 `Secondary` 如何用于计算 `ObjectReferenced` 轴系的更多信息，请参阅下文的讨论。<br>数据类型：字符串<br>允许值：`CelestialBody`、`Spacecraft`、`LibrationPoint`、`Barycenter`、`SolarSystemBarycenter`、`GroundStation`<br>访问权限：set<br>默认值：`Earth`<br>单位：N/A<br>接口：GUI、脚本 |
| **ReferenceObject** | `LocalAlignedConstrained` 轴系的参考对象。轴系的计算使得体固坐标架中的 `AlignmentVector` 与从 `Origin`（原点）指向 `ReferenceObject` 的向量对齐。<br>数据类型：资源<br>允许值：具有坐标的资源。例如：`CelestialBody`、`Spacecraft`、`LibrationPoint`、`Barycenter`、`SolarSystemBarycenter`、`GroundStation`。<br>访问权限：set<br>默认值：`Luna`<br>单位：N/A<br>接口：GUI、脚本 |
| **Secondary** | `ObjectReferenced` 轴系的次天体。该字段仅在 `Axes` = `ObjectReferenced` 时使用。有关 `Primary` 和 `Secondary` 如何用于计算 `ObjectReferenced` 轴系的更多信息，请参阅下文的讨论。<br>数据类型：字符串<br>允许值：`CelestialBody`、`Spacecraft`、`LibrationPoint`、`Barycenter`、`SolarSystemBarycenter`、`GroundStation`<br>访问权限：set<br>默认值：`Luna`<br>单位：N/A<br>接口：GUI、脚本 |
| **SpiceFrameId** | 坐标架的 SPICE 名称。该选项仅与 `SPICE` `Axes` 类型一起使用。该坐标架必须由分配给 `Origin` 天体或航天器的 SPICE 内核标识和定义。有关使用 SPICE 坐标架的更多详情，请参阅下文的备注。<br>数据类型：字符串<br>允许值：任何已定义的 SPICE 坐标架。<br>访问权限：set<br>默认值：`None`<br>单位：N/A<br>接口：脚本 |
| **XAxis** | `ObjectReferenced` 轴系的 x 轴定义。该字段仅在 `Axes` = `ObjectReferenced` 时使用。有关 `ObjectReferenced` 轴系如何计算的更多信息，请参阅下文的讨论。<br>数据类型：字符串<br>允许值：`R`、`V`、`N`、`-R`、`-V`、`-N` 或空<br>访问权限：set<br>默认值：`R`<br>单位：N/A<br>接口：GUI、脚本 |
| **YAxis** | `ObjectReferenced` 轴系的 y 轴定义。该字段仅在 `Axes` = `ObjectReferenced` 时使用。有关 `ObjectReferenced` 轴系如何计算的更多信息，请参阅下文的讨论。<br>数据类型：字符串<br>允许值：`R`、`V`、`N`、`-R`、`-V`、`-N` 或空<br>访问权限：set<br>默认值：无默认<br>单位：N/A<br>接口：GUI、脚本 |
| **ZAxis** | `ObjectReferenced` 轴系的 z 轴。该字段仅在 `Axes` = `ObjectReferenced` 时使用。有关 `ObjectReferenced` 轴系如何计算的更多信息，请参阅下文的讨论。<br>数据类型：字符串<br>允许值：`R`、`V`、`N`、`-R`、`-V`、`-N` 或空<br>访问权限：set<br>默认值：`N`<br>单位：N/A<br>接口：GUI、脚本 |

## GUI

> [图：New Coordinate System（新建坐标系）对话框]

当你在 **Resource Tree**（资源树）中添加新坐标系时，会出现上图所示的 **New Coordinate System** 对话框。你在 **Coordinate System Name**（坐标系名称）框中为新 `CoordinateSystem` 提供名称，并通过选择 `Origin`（原点）和 `Axes`（轴系）类型以及其他设置来配置 `CoordinateSystem`。某些设置（如 `Primary` 和 `Secondary`）仅对特定的 `Axes` 类型有效，这些依赖关系在下文中说明。

> [图：CoordinateSystem 编辑对话框的默认配置]

编辑现有 `CoordinateSystem` 时，使用 `CoordinateSystem` 对话框。默认配置如上图所示。

> [图：选择 ObjectReferenced 轴系类型时的对话框]

如果为 `Axes` 类型选择 `ObjectReferenced`，则 `Primary`、`Secondary`、`X`、`Y` 和 `Z` 字段被激活。你可以使用 `ObjectReferenced` 轴系基于两个空间对象（如 `Spacecraft`、`CelestialBody` 或 `Barycenter` 等）的运动来定义坐标。有关 `ObjectReferenced` 轴系的详细定义，请参阅下文的讨论。

> [图：选择 TOEEq/TOEEc/MOEEq/MOEEc 轴系类型时的对话框]

如果选择 `TOEEq`、`TOEEc`、`MOEEq` 或 `MOEEc` 作为轴系类型，则 **A1MJd Epoch**（A1 修正儒略历元）字段被激活。使用 `A1MJd` `Epoch` 字段定义坐标系的参考历元。

> [图：选择 LocalAlignedConstrained 轴系类型时的对话框]

如果选择 `LocalAlignedConstrained` 作为轴系 **Type**（类型），则 `CoordinateSystem` 对话框显示上图所示的轴系配置字段。

## 备注

### 使用 IAU76/FK5 约化计算基于 J2000 的轴系

FK5 约化（FK5 reduction）是将 `MJ2000Eq` 系中表达的向量旋转到 `EarthFixed`（地球固定）`CoordinateSystem` 的变换。FK5 约化中有许多作为中间旋转的坐标系，本节说明以下轴系类型的计算方法：`MJ2000Eq`、`MJ2000Ec`、`EarthFixed`、`MODEq`、`MODEc`、`TODEq`、`TODEc` 轴系。

地球随时间变化的定向非常复杂，这是地球与其外部环境（太阳、月球和行星）之间的相互作用以及内部动力学造成的。其定向目前无法建模到许多空间应用所需的精度，因此 FK5 约化是动力学建模与来自经验观测的每日改正的结合。下图说明了地球相对于惯性空间的运动分量。地球相对于惯性空间运动的主要分量是岁差（Precession）、章动（Nutation）、恒星时（Sidereal time）和极移（Polar Motion）。

> [图：地球相对于惯性空间的运动分量示意图]

主惯性矩轴定义为天球历表极（Celestial Ephemeris Pole）。由于地球的质量分布随时间变化，天球历表极相对于地球表面不是恒定的。岁差定义为天球历表极绕北黄极的锥形运动。天球历表极运动的另一个主要分量称为章动，是天球历表极与北黄极之间夹角的振荡。岁差和章动理论来自地球运动的动力学模型。恒星时是地球绕天球历表极的自转。恒星时模型是理论与观测的结合。地球自转轴方向相对于地壳不是恒定的，其运动称为极移。极移的一部分源于复杂的动力学，一部分源于章动中未建模的误差。极移由观测确定。

真瞬时（True of Date，TOD）系和平瞬时（Mean of Date，MOD）系是 FK5 约化中的中间坐标系，常用于分析。计算细节包含在 GMAT 数学规范中，下图仅作总结之用。图中使用以下缩写：PM：极移（Polar Motion），ST：恒星时（Sidereal Time），NUT：章动（Nutation），PREC：岁差（Precession），ITRF：国际地球参考架（International Terrestrial Reference Frame，地球固定），PEF：伪地球固定系（Pseudo Earth Fixed），TODEq：真瞬时赤道（True of Date Equator），TODEc：真瞬时黄道（True of Date Ecliptic），MODEc：平瞬时黄道（Mean of Date Ecliptic），MODEq：平瞬时赤道（Mean of Date Equator），FK5：J2000 赤道惯性系（J2000 Equatorial Inertial，IAU-1976/1980）。

> [图：FK5 约化中各坐标系之间的变换关系图]

### 使用 IAU2000 约定计算 ICRF 和 ITRF 轴系

国际天球参考架（`ICRF`）和国际地球参考架（ITRF）的计算采用 IAU 2000A 理论及 2006 年岁差更新。GMAT 使用天球中间原点（Celestial Intermediate Origin，CIO）变换方法，该方法避免了与岁差和章动相关的问题。在 CIO 模型中，天球中间极（Celestial Intermediate Pole）单位向量使用变量 X 和 S 以及 CIO 定位量 s 建模。出于性能考虑，GMAT 从随 GMAT 分发的 ICRF_Table.txt 文件中存储的预计算值插值 X、Y 和 s。

GMAT 通过绕 `EarthFixed` 坐标架旋转来建模从 `ICRF` 到 `MJ2000Eq` 的旋转，该坐标架在旧（1976）新（2000）两套理论中是相同的。出于性能考虑，从 `ICRF` 到 `MJ2000Eq` 的转换由这些坐标架之间欧拉轴和欧拉角的预计算值插值得到。注意，GMAT 目前不支持地球的 IAU2000 体固坐标架，该模型将包含在未来版本中。

### ObjectReferenced 轴系的计算

`ObjectReferenced`（对象参考）轴系由一个对象相对于另一个对象的运动定义。下图定义了 `ObjectReferenced` 轴系的六个主方向。第一个是次对象相对于主对象的相对位置，记为 r，在惯性系中表达。第二个是次对象相对于主对象的相对速度，记为 v，在惯性系中表达。第三个方向是垂直于运动方向的向量，记为 n，由 n = r × v 计算。其余三个方向是前三个的负方向，得到完整集合：{`R`、-`R`、`V`、-`V`、`N`、-`N`}。

> [图：ObjectReferenced 轴系六个主方向的定义图]

定义 `ObjectReferenced` 轴系时，从三个可用轴 [X、Y 和 Z] 中选取两个，并使用六个可用选项 {`R`、-`R`、`V`、-`V`、`N`、-`N`} 进行定义。给定两个方向后，GMAT 构建一个正交的右手 `CoordinateSystem`。例如，如果你选择 x 轴沿 `R` 方向、z 轴沿 `N` 方向，GMAT 通过将 y 轴设为 `N`×`R` 方向来完成右手系。如果你选择的排列导致非正交或左手 `CoordinateSystem`，GMAT 将抛出错误消息。

> **警告**：GMAT 目前在计算 `ObjectReferenced` 旋转矩阵时，假定涉及加速度叉积和点积的项为零。

### SPICE 坐标系的配置

通过使用 `SPICE` `Axes` 类型创建坐标系，可以在 GMAT 中使用 SPICE 工具包中定义的参考架。有用的例子包括月球主轴（Principal Axes，PA）坐标架和平地球（Mean Earth，ME）坐标架，但通过分配适当的内核，也可以定义和使用其他天体的 IAU 坐标架，以及 SPICE 的地球 ITRF 坐标架。定义坐标架的内核必须在 `Planet` 或其他天体上使用 `PlanetarySpiceKernelName` 列表指定。然后通过设置坐标系的 `SpiceFrameId` 来选择 SPICE 坐标架。有关如何使用 SPICE 坐标架的说明，请参阅下面的示例。GMAT 目前要求使用 `SPICE` `Axes` 类型时坐标系的 `Origin` 必须是 CelestialBody（天体）。SPICE 轴系不能以航天器、地面站或天体以外的对象为中心。

我们建议 SPICE 坐标架的用户通过查阅 JPL 导航与辅助信息设施（NAIF）网站（naif.jpl.nasa.gov）提供的文档来熟悉 SPICE 系统的基础知识。特别重要的是要认识到，SPICE 工具包中定义为 'J2000' 的参考架（在创建 GMAT SPICE 坐标架时也是如此）实际上是 ICRF 坐标架。就坐标变换而言，GMAT 将把 'J2000' `SpiceFrameId` 识别为 ICRF 坐标架，而不是 J2000 平坐标架（Mean of J2000）。

理解"内核池"（kernel pool）的概念也很重要。所有 SPICE 对象（包括坐标架）都在各种文本或二进制内核文件中定义，这些对象在全局内核池中进行管理。一个坐标架定义可能（有意或无意地）在加载到内核池的多个内核文件中定义。内核加载的顺序决定优先级，最后加载的定义将是生效的定义。内核文件的加载顺序可以通过查看 GMAT 日志文件确定。为避免错误或混淆，推荐的最佳实践是确保每个对象或坐标架只在一个内核文件中定义。

### 内置坐标系概述

| 名称 | 原点 | 轴系 | 描述 |
|------|------|------|------|
| `EarthMJ2000Eq` | `Earth` | `MJ2000Eq` | 基于 IAU-1976/FK5 理论及 1980 年章动更新的地球赤道惯性系。 |
| `EarthMJ2000Ec` | `Earth` | `MJ2000Ec` | 基于 IAU-1976/FK5 理论及 1980 年章动更新的地球黄道惯性系。 |
| `EarthFixed` | `Earth` | `BodyFixed` | 基于 IAU-1976/FK5 理论及 1980 年章动更新的地球固定系。 |
| `EarthICRF` | `Earth` | `ICRF` | 基于 IAU-2000 理论及 2006 年岁差更新的地球赤道惯性系。 |

### 轴系类型说明

| 轴系名称 | 原点限制 | 基础类型 | 描述 |
|----------|----------|----------|------|
| `BodyFixed` | 天体或航天器 | IAU-1976 FK5 | `BodyFixed`（星固系）轴系参考于天体赤道和天体的本初子午线。有关天体的轴系定义，请参阅天体模型的备注。当 `Origin` 是 `Spacecraft` 时，轴系使用 `Spacecraft` 的姿态模型计算。注意：并非所有姿态模型都计算体固角速度。如果航天器上没有可用的体固角速度，使用 `BodyFixed` 轴系请求速度变换将导致错误。 |
| `BodyInertial` | 天体 | IAU-1976 FK5 | 参考于作为 `CoordinateSystem` 原点所选天体的赤道（在 J2000 历元）的惯性系。由于 `BodyInertial` 轴系对不同天体使用不同的理论，以下定义仅说明标称轴配置。x 轴指向天体赤道与地球在 J2000 的平赤道相交形成的线。z 轴指向天体在 J2000 历元的自转轴方向。y 轴完成右手系。对于地球，`BodyInertial` 轴系与 `MJ2000Eq` 系相同。有关所有其他天体的轴系定义，请参阅天体模型的备注。 |
| `BodySpinSun` | 天体 | IAU-1976 FK5 | 天体自转轴参考系。x 轴从天体指向太阳。y 轴由 x 轴与天体自转轴的叉积计算。z 轴完成右手系。 |
| `Equator` | 天体 | IAU-1976 FK5 | 作为原点所选天体的真瞬时赤道轴系。`Equator` 系由天体的赤道面及其与黄道面在当前历元的交线定义。当前历元由使用上下文定义，通常来自航天器或图形历元。有关天体的轴系定义，请参阅天体模型的备注。 |
| `GSE` | 无 | IAU-1976 FK5 | 地心太阳黄道系（Geocentric Solar Ecliptic）。x 轴从地球指向太阳。z 轴定义为叉积 R×V，其中 R 和 V 分别为地球相对于太阳的位置和速度。y 轴完成右手系。即使原点不是地球，`GSE` 轴也使用地球和太阳的相对运动计算。 |
| `GSM` | 无 | IAU-1976 FK5 | 地心太阳磁层系（Geocentric Solar Magnetic）。x 轴从地球指向太阳。z 轴定义为与 x 轴正交，并位于 x 轴与地球磁偶极向量所张的平面内。y 轴完成右手系。即使原点不是地球，`GSM` 轴也使用地球和太阳的相对运动计算。 |
| `ICRF` | 无 | IAU-2000 | 惯性坐标系。其轴接近 J2000 历元的地球平赤道和平极，在地球表面，`MJ2000Eq` 与 `ICRF` 中表达的向量之间的 RSS 差异小于 1 m。注意，由于 `MJ2000Eq` 和 `ICRF` 都是惯性系的不完美实现，它们之间的变换是随时间变化的。该轴系使用 IAU-2000A 理论及 2006 年岁差更新计算。 |
| `LocalAlignedConstrained` | 无 | IAU-1976 FK5 | `LocalAlignedConstrained`（本地对准-约束）轴系是基于 `ReferenceObject`（参考对象）相对于 `Origin`（原点）位置的对准-约束系，使用著名的 Triad 算法计算。轴系的计算使得 `AlignmentVector`（定义为在 `LocalAlignedConstrained` 系中表达的对准向量分量）与 `ReferenceBody` 相对于原点的位置对齐。绕 `AlignmentVector` 的旋转通过最小化 `ConstraintVector`（定义为在 `LocalAlignedConstrained` 系中表达的约束向量）与 `ConstraintReferenceVector`（定义为在 `ConstraintCoordinateSystem` 中表达的约束参考向量）之间的夹角来确定。对准向量和约束向量的长度不能为零。同样，约束向量与对准向量的叉积长度也不能为零。 |
| `MJ2000Ec` | 无 | IAU-1976 FK5 | 惯性坐标系。x 轴指向 J2000 历元地球平赤道与平黄道面相交形成的线。z 轴垂直于 J2000 历元的平黄道面，y 轴完成右手系。该系使用 IAU-1976/FK5 理论及 1980 年章动更新计算。 |
| `MJ2000Eq` | 无 | IAU-1976 FK5 | 惯性坐标系。标称 x 轴指向（J2000 历元）地球平赤道面与平黄道面相交形成的线，指向白羊宫（Aries）方向。z 轴垂直于 J2000 历元的地球平赤道，y 轴完成右手系。J2000 历元的黄道和赤道平面的位置使用 IAU-1976/FK5 理论及 1980 年章动更新计算。 |
| `MODEc` | 无 | IAU-1976 FK5 | 参考于当前历元平黄道的准惯性坐标系。当前历元由使用上下文定义，通常来自航天器或图形历元。该系使用 IAU-1976/FK5 理论及 1980 年章动更新计算。 |
| `MODEq` | 无 | IAU-1976 FK5 | 参考于当前历元地球平赤道的准惯性坐标系。当前历元由使用上下文定义，通常来自航天器或图形历元。该系使用 IAU-1976/FK5 理论及 1980 年章动更新计算。 |
| `MOEEc` | 无 | IAU-1976 FK5 | 参考于参考历元平黄道的准惯性坐标系。参考历元在 `CoordinateSystem` 对象上定义。该系使用 IAU-1976/FK5 理论及 1980 年章动更新计算。 |
| `MOEEq` | 无 | IAU-1976 FK5 | 参考于参考历元地球平赤道的准惯性坐标系。参考历元在 `CoordinateSystem` 对象上定义。该系使用 IAU-1976/FK5 理论及 1980 年章动更新计算。 |
| `ObjectReferenced` | 无 | IAU-1976 FK5 | `ObjectReferenced`（对象参考）系是其轴由一个对象相对于另一个对象的运动定义的 `CoordinateSystem`。有关 `ObjectReferenced` 轴系的详细描述，请参阅上文的讨论。 |
| `SPICE` | 天体 | 不适用 | 由分配给天体的二进制或文本行星常数内核在 SPICE 系统中定义的坐标架。 |
| `TEME` | 无 | IAU-1976 FK5 | 参考于当前历元地球真赤道和平春分点的准惯性坐标系。当前历元由使用上下文定义，通常来自航天器或图形历元。该系使用 IAU-1976/FK5 理论及 1980 年章动更新计算。TEME 轴只能用于以地球为中心的坐标系。 |
| `TODEc` | 无 | IAU-1976 FK5 | 参考于当前历元地球真黄道的准惯性坐标系。当前历元由使用上下文定义，通常来自航天器或图形历元。该系使用 IAU-1976/FK5 理论及 1980 年章动更新计算。 |
| `TOEEc` | 无 | IAU-1976 FK5 | 参考于参考历元真黄道的准惯性坐标系。参考历元在 `CoordinateSystem` 对象上定义。该系使用 IAU-1976/FK5 理论及 1980 年章动更新计算。 |
| `TODEq` | 无 | IAU-1976 FK5 | 参考于当前历元地球真赤道的准惯性坐标系。当前历元由使用上下文定义，通常来自航天器或图形历元。该系使用 IAU-1976/FK5 理论及 1980 年章动更新计算。 |
| `TOEEq` | 无 | IAU-1976 FK5 | 参考于参考历元真赤道的准惯性坐标系。参考历元在 `CoordinateSystem` 对象上定义。该系使用 IAU-1976/FK5 理论及 1980 年章动更新计算。 |
| `Topocentric` | Earth | IAU-1976 FK5 | 基于 `GroundStation`（地面站）的坐标系。y 轴指向正东，z 轴垂直于本地地平线。x 轴完成右手系。 |

## 示例

在 `EarthFixed`（地球固定）坐标中定义 `Spacecraft`（航天器）的状态。

```
Create Spacecraft aSpacecraft
aSpacecraft.CoordinateSystem = EarthFixed
aSpacecraft.X = 7100
aSpacecraft.Y = 0
aSpacecraft.Z = 1300
aSpacecraft.VX = 0
aSpacecraft.VY = 7.35
aSpacecraft.VZ = 1
```

说明：将航天器的坐标系设为内置的 EarthFixed（地球固定系，星固系的一种），并以笛卡尔分量给出其位置和速度。

在 `GroundStation`（地面站）`Topocentric`（站心）坐标中报告 `Spacecraft` 的状态。

```
Create Spacecraft aSat
Create Propagator aProp
Create GroundStation aStation

Create CoordinateSystem stationTopo
stationTopo.Origin = aStation
stationTopo.Axes   = Topocentric

Create ReportFile aReport
aReport.Filename = 'ReportFile1.txt'
aReport.Add = {aSat.stationTopo.X aSat.stationTopo.Y aSat.stationTopo.Z ... 
               aSat.stationTopo.VX aSat.stationTopo.VY aSat.stationTopo.VZ}

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedSecs = 8640.0}
```

说明：创建一个以地面站 aStation 为原点、Topocentric（站心）为轴系的坐标系 stationTopo；传播 8640 秒并在报告中输出航天器在该站心系中的位置和速度分量。

在 `ObjectReferenced`（对象参考）旋转天平动点系中查看轨迹。

```
%  Create the Earth-Moon Barycenter and Libration Point
Create Barycenter EarthMoonBary
EarthMoonBary.BodyNames = {Earth,Luna};

Create LibrationPoint SunEarthMoonL1
SunEarthMoonL1.Primary   = Sun;
SunEarthMoonL1.Secondary = EarthMoonBary
SunEarthMoonL1.Point     = L1;

%  Create the coordinate system
Create CoordinateSystem RotatingSEML1Coord
RotatingSEML1Coord.Origin    = SunEarthMoonL1
RotatingSEML1Coord.Axes      = ObjectReferenced
RotatingSEML1Coord.XAxis     = R
RotatingSEML1Coord.ZAxis     = N
RotatingSEML1Coord.Primary   = Sun
RotatingSEML1Coord.Secondary = EarthMoonBary

%  Create the spacecraft and propagator
Create Spacecraft aSpacecraft
aSpacecraft.DateFormat       = UTCGregorian
aSpacecraft.Epoch            = '09 Dec 2005 13:00:00.000'
aSpacecraft.CoordinateSystem = RotatingSEML1Coord
aSpacecraft.X  = -32197.88223741966
aSpacecraft.Y  = 211529.1500044117
aSpacecraft.Z  = 44708.57017366499
aSpacecraft.VX = 0.03209516489451751
aSpacecraft.VY = 0.06100386504053736
aSpacecraft.VZ = 0.0550442738917212

Create Propagator aPropagator
aPropagator.FM           = aForceModel
aPropagator.MaxStep = 86400
Create ForceModel aForceModel
aForceModel.PointMasses = {Earth,Sun,Luna}

% Create a 3-D graphic
Create OrbitView anOrbitView
anOrbitView.Add                  = {aSpacecraft,  Earth, Sun, Luna}
anOrbitView.CoordinateSystem     = RotatingSEML1Coord
anOrbitView.ViewPointReference   = SunEarthMoonL1
anOrbitView.ViewPointVector      = [-1500000 0 0 ]
anOrbitView.ViewDirection        = SunEarthMoonL1
anOrbitView.ViewUpCoordinateSystem = RotatingSEML1Coord
anOrbitView.Axes                 = Off
anOrbitView.XYPlane              = Off

BeginMissionSequence

Propagate aPropagator(aSpacecraft, {aSpacecraft.ElapsedDays = 180})
```

说明：创建地月质心和日-地月 L1 天平动点；以该天平动点为原点、ObjectReferenced 为轴系（X 轴沿 R、Z 轴沿 N，主天体为太阳、次天体为地月质心）建立旋转坐标系；在该坐标系中定义航天器，传播 180 天并在三维轨道视图中显示。

配置并使用 SPICE 坐标架。

```
%  The required SPICE kernels can be found here:
%    https://naif.jpl.nasa.gov/pub/naif/generic_kernels/pck/moon_pa_de440_200625.bpc
%    https://naif.jpl.nasa.gov/pub/naif/generic_kernels/fk/satellites/moon_de440_220930.tf

%  Set the Luna fixed frame as the MOON_PA frame

Luna.PlanetarySpiceKernelName = {'../data/planetary_coeff/moon_pa_de440_200625.bpc'}
Luna.FrameSpiceKernelName     = {'../data/planetary_coeff/moon_de440_220930.tf'}
Luna.RotationDataSource       = 'SPICE'
Luna.SpiceFrameId             = 'MOON_PA'

%  Principal Axes coordinates of the Apollo 11 landing site, 
%  from Table 1 of https://doi.org/10.3847/1538-3881/abd414

Create GroundStation Apollo11

Apollo11.CentralBody      = Luna
Apollo11.StateType        = Cartesian
Apollo11.HorizonReference = Ellipsoid
Apollo11.Location1        =  1591.967049
Apollo11.Location2        =   690.698573
Apollo11.Location3        =    21.004461

%  Create the Moon Mean Earth coordinate system

Create CoordinateSystem MoonME

MoonME.Origin       = Luna
MoonME.Axes         = 'SPICE'
MoonME.SpiceFrameId = 'MOON_ME'

%  Transform the Apollo 11 landing site coordinates from Moon PA to Moon ME

Create String LineOut

BeginMissionSequence

LineOut = sprintf('%.9f %.9f %.9f %.9f %.9f %.9f', ...
    Apollo11.MoonME.X, Apollo11.MoonME.Y, Apollo11.MoonME.Z, ...
    Apollo11.MoonME.VX, Apollo11.MoonME.VY, Apollo11.MoonME.VZ)

Write LineOut
```

说明：为月球（Luna）指定 SPICE 行星常数内核和坐标架内核，将其自转数据源设为 SPICE、星固坐标架设为 MOON_PA（月球主轴坐标架）；以笛卡尔坐标创建阿波罗 11 号登月点地面站；再创建一个原点为月球、轴系类型为 SPICE、坐标架为 MOON_ME（月球平地球坐标架）的坐标系 MoonME；最后将登月点坐标从 Moon PA 转换到 Moon ME 并输出。
