# 星历文件资源（EphemerisFile）
> 译自 GMAT R2026a 帮助文档 EphemerisFile.html

EphemerisFile —— 生成航天器的星历数据。

## 描述

`EphemerisFile` 是一个用户定义的资源，以报告格式生成航天器的星历。你可以在任何用户定义的坐标系中生成航天器的星历数据。GMAT 允许你以 CCSDS-OEM、SPK、Code-500 和 STK .e（STK-TimePosVel）格式输出星历数据。更多细节请参见"备注"一节。`EphemerisFile` 资源可配置为按默认积分步长生成星历数据，或通过输入用户选择的步长来生成。

GMAT 允许你通过创建多个 `EphemerisFile` 资源来生成任意数量的星历数据文件。`EphemerisFile` 资源可以使用 GUI 或脚本接口创建。GMAT 还提供了通过 `Toggle` `On`/`Off` 命令控制何时向文本文件写入和停止写入星历数据的选项。关于 `EphemerisFile` 资源与 `Toggle` 命令之间交互的详细讨论，请参见下面的"备注"一节。

**另请参见**：CoordinateSystem、Toggle

## 字段

| 字段 | 描述 |
|------|------|
| `CoordinateSystem` | 允许你相对于为此字段选择的坐标系生成航天器星历。星历也可以相对于用户指定的坐标系生成。此字段不能在任务序列中修改。关于坐标系和星历格式的限制，请参见下面的"备注"。<br>数据类型：枚举<br>允许的值：任何默认坐标系或用户定义的坐标系<br>访问方式：set、get<br>默认值：`EarthMJ2000Eq`<br>单位：N/A<br>接口：GUI、脚本 |
| `DistanceUnit` | 写入 STK 星历文件的距离量的单位。仅当 `FileFormat` 设置为 `STK-TimePosVel` 时有效。<br>数据类型：字符串<br>允许的值：Kilometers 或 Meters<br>访问方式：set<br>默认值：Kilometers<br>单位：N/A<br>接口：GUI、脚本 |
| `EpochFormat` | 此字段允许你设置选择为 `InitialEpoch` 和 `FinalEpoch` 字段输入的历元类型。此字段不能在任务序列中修改。<br>数据类型：枚举<br>允许的值：以下任一历元格式：`UTCGregorian`、`UTCModJulian`、`TAIGregorian`、`TAIModJulian`、`TTGregorian`、`TTModJulian`、`A1Gregorian`、`A1ModJulian`<br>访问方式：set<br>默认值：`UTCGregorian`<br>单位：N/A<br>接口：GUI、脚本 |
| `FileFormat` | 允许用户以四种可用星历格式生成星历文件：CCSDS-OEM、SPK、Code-500 或 STK-TimePosVel（即 STK .e 格式）。此字段不能在任务序列中修改。<br>数据类型：枚举<br>允许的值：`CCSDS-OEM`、`SPK`、`Code-500`、`STK-TimePosVel`<br>访问方式：set<br>默认值：`CCSDS-OEM`<br>单位：N/A<br>接口：GUI、脚本 |
| `Filename` | 允许用户为生成的星历文件命名。CCSDS-OEM、SPK、Code-500 和 STK-TimePosVel 星历类型的常用文件扩展名分别为 *.oem、*.bsp、*.eph 和 *.e。此字段不能在任务序列中修改。<br>数据类型：字符串<br>允许的值：合法的文件路径和名称<br>访问方式：set<br>默认值：`EphemerisFile1.eph`<br>单位：N/A<br>接口：GUI、脚本 |
| `FinalEpoch` | 允许用户指定星历文件的时间跨度。星历文件生成到 `FinalEpoch` 字段中指定的最终历元为止。此字段不能在任务序列中修改。<br>数据类型：字符串<br>允许的值：用户定义的最终历元或默认值<br>访问方式：set<br>默认值：`FinalSpacecraftEpoch`<br>单位：N/A<br>接口：GUI、脚本 |
| `IncludeCovariance` | 对于支持协方差输出的星历格式，可选地在输出星历中包含协方差数据的标志。目前仅允许用于 `STK-TimePosVel` 星历文件。选择 `Position` 只输出位置协方差值。选择 `PositionAndVelocity` 输出位置和速度协方差值。<br>数据类型：字符串<br>允许的值：`None`、`Position`、`PositionAndVelocity`<br>访问方式：set<br>默认值：`None`<br>单位：N/A<br>接口：脚本 |
| `IncludeEventBoundaries` | 可选地把事件数据和边界写入 STK 星历文件的标志。仅当 `FileFormat` 设置为 `STK-TimePosVel` 时有效。当设置为 true 时，如果星历数据中存在不连续点，则不连续点的时刻将连同不连续处的空行一起写入文件。<br>数据类型：布尔<br>允许的值：true、false<br>访问方式：set<br>默认值：true<br>单位：N/A<br>接口：GUI、脚本 |
| `InitialEpoch` | 允许用户指定星历文件的起始历元。星历文件从 `InitialEpoch` 字段中定义的历元开始生成。此字段不能在任务序列中修改。<br>数据类型：字符串<br>允许的值：用户定义的初始历元或默认值<br>访问方式：set<br>默认值：`InitialSpacecraftEpoch`<br>单位：N/A<br>接口：GUI、脚本 |
| `InterpolationOrder` | 允许你为任何星历类型的可用插值方法（`Lagrange` 或 `Hermite`）设置插值阶数。此字段不能在任务序列中修改。<br>数据类型：整数<br>允许的值：1 <= 整数 <= 10<br>访问方式：set<br>默认值：7<br>单位：N/A<br>接口：GUI、脚本 |
| `Interpolator` | 此字段定义用于生成星历文件的可用插值方法。可用的 `Interpolator` 为 `Lagrange` 或 `Hermite`。此字段不能在任务序列中修改。<br>数据类型：字符串<br>允许的值：`Lagrange` 用于 CCSDS-OEM、Code-500 和 STK-TimePosVel 星历类型；`Hermite` 用于 SPK 文件<br>访问方式：set<br>默认值：`Lagrange`<br>单位：N/A<br>接口：GUI、脚本 |
| `Maximized` | 允许用户最大化生成的星历文件窗口。此字段不能在任务序列中修改。<br>数据类型：布尔<br>允许的值：true、false<br>访问方式：set<br>默认值：false<br>单位：N/A<br>接口：脚本 |
| `OutputFormat` | 允许用户指定希望以何种格式生成 GSFC Code-500 星历。GSFC Code-500 星历可以按 Little-Endian（小端）或 Big-Endian（大端）格式生成。此字段不能在任务序列中修改。<br>数据类型：字符串<br>允许的值：`LittleEndian`、`BigEndian`<br>访问方式：set<br>默认值：`LittleEndian`<br>单位：N/A<br>接口：GUI、脚本 |
| `RelativeZOrder` | 允许用户选择哪个生成的星历文件显示窗口最先显示在屏幕上。`RelativeZOrder` 值最低的 `EphemerisFile` 资源最后显示，而 `RelativeZOrder` 值最高的 `EphemerisFile` 资源最先显示。此字段不能在任务序列中修改。<br>数据类型：整数<br>允许的值：整数 ≥ 0<br>访问方式：set<br>默认值：0<br>单位：N/A<br>接口：脚本 |
| `Size` | 允许用户控制生成的星历文件面板的显示大小。[0 0] 矩阵中的第一个值控制星历文件显示窗口的水平大小，第二个值控制垂直大小。此字段不能在任务序列中修改。<br>数据类型：实数数组<br>允许的值：任何实数<br>访问方式：set<br>默认值：[ 0 0 ]<br>单位：N/A<br>接口：脚本 |
| `Spacecraft` | 允许用户生成在 `Spacecraft` 字段中定义的航天器的星历数据。此字段不能在任务序列中修改。<br>数据类型：字符串<br>允许的值：默认航天器或任意数量的用户定义航天器或编队<br>访问方式：set、get<br>默认值：`DefaultSC`<br>单位：N/A<br>接口：GUI、脚本 |
| `StepSize` | 星历文件按为 `StepSize` 字段指定的步长生成。用户可以按默认积分步长（使用原始积分器步长）或通过定义固定步长来生成星历文件。对于 CCSDS-OEM 和 STK-TimePosVel 文件格式，你可以按积分器步长或固定步长生成星历。对于 SPK 文件格式，GMAT 只允许你按原始积分器步长生成星历。对于 Code-500 星历文件类型，你只能按固定步长生成星历。此字段不能在任务序列中修改。<br>数据类型：实数<br>允许的值：实数 > 0.0 或等于默认值<br>访问方式：set<br>默认值：`IntegratorSteps`（用于 CCSDS-OEM、SPK 和 STK-TimePosVel 文件格式）和 `60` 秒（用于 Code-500 文件格式）<br>单位：N/A<br>接口：GUI、脚本 |
| `UpperLeft` | 允许用户把生成的星历文件显示窗口向任意方向平移。[0 0] 矩阵中的第一个值帮助水平平移窗口，第二个值帮助垂直平移窗口。此字段不能在任务序列中修改。<br>数据类型：实数数组<br>允许的值：任何实数<br>访问方式：set<br>默认值：[ 0 0 ]<br>单位：N/A<br>接口：脚本 |
| `WriteEphemeris` | 允许用户可选地计算/写入或不计算/写入已创建和配置的星历。此字段不能在任务序列中修改。<br>数据类型：布尔<br>允许的值：true、false<br>访问方式：set<br>默认值：true<br>单位：Unit<br>接口：GUI、脚本 |

## GUI

下图显示了 `EphemerisFile` 资源的默认设置：

> [图：EphemerisFile 资源的默认 GUI 设置窗口]

GMAT 允许你修改 `EphemerisFile` 资源的 `InitialEpoch`、`FinalEpoch` 和 `StepSize` 字段。你可以定义自己的初始和最终历元，而不必总是按 `InitialSpacecraftEpoch` 和 `FinalSpacecraftEpoch` 的默认时间跨度设置生成星历文件。同样，你可以按自己选择的步长生成星历文件，而不必使用 `StepSize` 字段的默认 `IntegratorSteps` 设置。

下面的 GUI 图显示了将从初始历元 01 Jan 2000 14:00:00.000 到最终历元 01 Jan 2000 20:00:00.000 生成的星历文件，使用非默认步长 300 秒：

> [图：EphemerisFile 资源设置了自定义起止历元和 300 秒步长的 GUI 窗口]

## 备注

### CCSDS、Code 500 和 SPK 格式星历文件的坐标系字段行为

如果所选的 `CoordinateSystem` 使用 MJ2000Eq 轴，则根据 CCSDS 约定，CCSDS 星历文件的 REF_FRAME 为 "EME2000"。按 CCSDS 的要求，当在 ICD（接口控制文档）中记录时，允许使用非标准轴名称。用户指南中的 `CoordinateSystems` 规范文档就是 GMAT 支持的所有轴的 ICD。如果你创建一个原点为 Luna 的新坐标系，则 CCSDS 星历文件的 CENTER_NAME 为 "Moon"。

对于 Code-500 文件格式，GMAT 可以为 `CoordinateSystem` 字段下引用任何中心天体的 MJ2000Eq、BodyFixed 或 TOD 轴的坐标系写入星历。

对于 SPK 文件格式，GMAT 只能为 `CoordinateSystem` 字段下引用任何中心天体的 MJ2000Eq 轴类型的坐标系写入星历。但请注意，为符合 SPICE 文件约定，状态在写入 SPICE 文件之前会被转换到 ICRF 参考架。

GMAT 与 IAU 约定之间有一个重要区别。按 IAU 约定，IAU2000 轴没有独立于原点的名称。GCRF 是以地球为中心、采用 IAU2000 轴的坐标系，ICRF 是以太阳系质心为中心、采用 IAU2000 轴的坐标系。我们选择把 IAU2000 轴命名为 ICRF，而不论原点如何。请参阅 `CoordinateSystems` 规范文档，进一步了解 GMAT 支持的内置坐标系和轴类型的描述。

### STK 格式星历文件的坐标系字段行为

GMAT 不允许在中心天体不是地球的 STK 格式星历文件中使用（读取或写入）TrueOfDate 参考架。GMAT 通过把地球 TrueOfDate 参考架平移到其他中心天体的原点，来定义围绕地球以外中心天体的 TrueOfDate 参考架。STK 则为每个中心天体定义唯一的 TrueOfDate 参考架。GMAT 和 STK 的定义仅对地球一致。

以下坐标系允许用于读取和写入 STK 星历文件：

- J2000 和 ICRF 允许用于所有中心天体
- 读取 STK TrueOfDate 星历文件，或写入使用 GMAT TODEq 轴的坐标系的星历文件，仅允许用于地心文件
- 读取 STK J2000_Ecliptic 星历文件，或写入使用 GMAT MJ2000Ec 轴的坐标系的星历文件，仅允许用于日心文件

所有其他坐标系均不允许。这些规则同样适用于 `GetEphemStates()` 函数调用。

### 不连续与迭代过程中星历文件的行为

当为任务序列生成星历文件时，GMAT 对由不连续或离散任务事件界定的星历段分别进行插值。不连续或离散的任务序列事件范围包括脉冲或有限推力机动、动力学模型的更改或使用赋值命令时。此外，当任务序列采用差分校正或优化等迭代过程时，GMAT 只写入迭代过程最终解的星历。请参见下面的"示例"一节，了解在脉冲机动等不连续事件和差分校正等迭代过程中星历文件是如何生成的。

CCSDS 轨道数据电文（ODM）文档的第 1 版曾要求星历必须按时间递增顺序生成且只能向前。然而 CCSDS ODM 文档的第 2 版现在也允许向后生成星历文件。目前在 GMAT 中，当你向后传播航天器时，CCSDS 星历也会向后生成。

> **警告**：Code500 星历文件要求固定时间步长，并具有预定义的处理星历数据块的格式。该格式不允许数据块在脉冲机动处发生的状态不连续点停止和重新开始。GMAT 当前的行为是跨越这些不连续点进行插值，因为 Code 500 格式不能优雅地支持带不连续点的星历。这对于小机动是可以接受的，但随着机动量级的增大，精度会降低。因此，我们建议使用更现代的星历文件格式。如果必须对不连续轨迹使用 Code500 星历文件，我们建议使用小固定时间步长的传播器，并在星历文件上设置较小的 `StepSize`，以减少不连续点附近的插值误差。

与 CCSDS 星历格式类似，每当发生脉冲或有限机动等事件或动力学模型发生变化时，STK-TimePosVel 星历也会以独立的星历数据块生成。然而，与 CCSDS 星历不同，STK-TimePosVel 星历不会在向后传播期间生成，只报告向前传播的星历。

### 星历文件不满足 CCSDS 文件格式要求时的行为

生成星历文件时，需要遵循 CCSDS 制定的 ODM 推荐标准。该推荐标准中描述的一组轨道数据电文是 CCSDS 各机构之间交叉支持的数据交换应用中轨迹表示的基准概念。CCSDS-ODM 推荐标准文档建立了通用框架，为轨道数据的交换提供了共同基础。

目前，GMAT 生成的星历文件满足 CCSDS 规定的大部分推荐标准。然而，每当 GMAT 的星历违反 CCSDS 文件格式要求时，生成的星历文件将在星历文件的头部（Header）部分显示一条警告。更具体地说，此警告将在 COMMENT 下给出，让你知道此星历文件不完全满足 CCSDS 文件格式要求。

### 各星历文件格式的插值阶数字段行为

对于 CCSDS 文件格式，每当没有足够的原始数据支持所请求的插值类型和阶数时，GMAT 会抛出错误消息并停止插值。GMAT 仍会生成星历文件，但不会向文件写入航天器星历数据，只保留文件的头部（Header）部分。在头部部分的 COMMENT 下，会给出一条消息，说明没有足够的原始数据按所请求的插值阶数生成航天器星历数据。

对于 SPK 文件格式，原始数据始终在每个积分步为每个弧段收集，然后发送给 SPK 内核写入器。GMAT 不对 SPK 文件执行任何插值，因为 SPK 包含其自身的插值。因此，`InitialEpoch` 和 `FinalEpoch` 字段对 SPK 星历的行为有所不同。文件上的第一个历元是 `InitialEpoch` 之后的第一个步。文件上的最后一个历元是 `FinalEpoch` 之前的最后一个步。

对于 Code 500 文件格式，你可以设置插值阶数，目前 GMAT 支持 Lagrange 作为可用的插值方法。对于 Code 500 文件格式，如果没有足够的原始数据支持插值类型和阶数，GMAT 将抛出错误消息并停止插值。

对于 STK-TimePosVel 星历格式，每当没有足够的原始数据按所请求的插值阶数和固定步长生成星历时，GMAT 会在内部调整插值阶数，使得至少星历的起点和最后一个点被报告到 STK .e 星历文件中。这个新的插值阶数将在 STK .e 星历的头部数据中报告。

### 使用 EphemerisFile 资源和 Toggle 命令时的行为

`EphemerisFile` 资源在整个任务持续时间的每个传播步生成星历文件。如果你想在任务的特定时段生成星历数据，可以把 `Toggle` `On/Off` 命令插入任务树中，以控制 `EphemerisFile` 资源何时写入数据。当对一个 `EphemerisFile` 订阅器（输出）发出 `Toggle` `Off` 命令时，在发出 `Toggle` `On` 命令之前不会有数据发送到文件。同样，当使用 `Toggle` `On` 命令时，星历数据在每个积分步发送到文件，直到使用 `Toggle` `Off` 命令为止。Toggle 命令可用于 GMAT 支持的全部四种星历类型。

下面的示例脚本片段展示了如何在使用 `EphemerisFile` 资源时使用 `Toggle Off/On` 命令。传播的前两天不发送星历数据，只有传播最后四天期间收集的数据被发送到名为 'EphemerisFile1.eph' 的文本文件：

```
Create Spacecraft aSat
Create Propagator aProp

Create EphemerisFile anEphmerisFile

anEphmerisFile.Spacecraft = aSat
anEphmerisFile.Filename = 'EphemerisFile1.eph'

BeginMissionSequence

Toggle anEphmerisFile Off
Propagate aProp(aSat) {aSat.ElapsedDays = 2}
Toggle anEphmerisFile On
Propagate aProp(aSat) {aSat.ElapsedDays = 4}
```

说明：先 Toggle Off 关闭星历输出，传播 2 天；再 Toggle On 打开输出，传播 4 天——只有后 4 天的数据写入星历文件。

当把 `Toggle` 命令与星历文件中的有限推力机动建模结合使用时，必须遵守一定的操作顺序。星历 Toggle 命令必须放在 BeginFileThrust 和 EndFileThrust 命令内部，如下例所示。在传播时以及运行 `BatchEstimator`、`ExtendedKalmanFilter` 或 `Smoother` 等估计器时，都必须遵守此操作顺序。

```
BeginFileThrust ThrustHistory(Sat);
Toggle Ephem On;
Propagate Prop(Sat) {Sat.ElapsedDays = 1};
Toggle Ephem Off;
EndFileThrust ThrustHistory(Sat);
```

说明：在有限推力弧段（BeginFileThrust/EndFileThrust）内部先 Toggle On、传播 1 天、再 Toggle Off，确保星历开关与推力历史记录正确配合。

### 不连续与迭代过程中 Code 500 星历文件的行为

Code 500 星历文件遵循《Flight Dynamics Division (FDD) Generic Data Product Formats Interface Control Document》（飞行动力学部（FDD）通用数据产品格式接口控制文档）中定义的星历格式和定义。

与 CCSDS 星历文件不同，每当发生脉冲/有限机动、动力学变化或赋值命令等不连续或离散任务事件时，Code 500 星历格式不支持在数据块中分成独立的块。相反，无论星历文件初始和最终历元之间发生多少任务事件，Code 500 星历都以一个连续的数据块生成。此外，当任务序列采用差分校正或优化等迭代过程时，GMAT 只写入迭代过程最终解的星历。Code 500 星历不允许非单调的星历生成，如果传播方向发生变化将抛出异常。此外，由赋值产生的任何不连续都可能导致 Code 500 文件无效。

### Code 500 星历头部记录

Code 500 星历文件的标准格式具有 2800 字节的逻辑记录长度。Code 500 文件有两个头部记录——星历头部记录 1 和星历记录 2，随后是文件时间跨度所需的任意数量的星历数据记录。星历文件头部记录中的许多参数是必填的，而一些字段是可选的。GMAT 的 Code 500 星历头部记录只指定必填字段，可选字段未包含在内。Code 500 的星历头部记录 1 是必填的，而星历记录 2 是可选的。星历格式的完整描述以及必填和可选星历头部记录参数的列表定义于《Flight Dynamics Division (FDD) Generic Data Product Formats Interface Control Document》。在 GMAT 中，头部记录 1 只写入了必填字段，而头部记录 2 留空。下表列出了头部记录 1 的必填字段以及与该字段相关的任何附加注释。

| 必填字段 | 注释 |
|----------|------|
| `productId` | 'EPHEM ' |
| `satId` | 123.000000 |
| `timeSystemIndicator` | 2.000000 |
| `StartDateOfEphem_YYYMMDD` | 值取决于运行时间 |
| `startDayCountOfYear` | 值取决于运行时间 |
| `startSecondsOfDay` | 值取决于运行时间 |
| `endDateOfEphem_YYYMMDD` | 值取决于运行时间 |
| `endDayCountOfYear` | 值取决于运行时间 |
| `endSecondsOfDay` | 值取决于运行时间 |
| `stepSize_SEC` | 值取决于运行时间 |
| `startYYYYMMDDHHMMSSsss.` | 值取决于运行时间 |
| `endYYYYMMDDHHMMSSsss.` | 值取决于运行时间 |
| `tapeId` | 'STANDARD' |
| `sourceId` | 'GTDS ' |
| `headerTitle` | ' |
| `centralBodyIndicator` | 设置为坐标系的中心天体。注意 GMAT 允许用户更改积分的中心天体。 |
| `refTimeForDUT_YYMMDD` | 570918.000000 |
| `coordSystemIndicator1` | '2000' |
| `coordSystemIndicator2` | 4 |
| `orbitTheory` | 'COWELL ' |
| `timeIntervalBetweenPoints_DUT` | 值取决于运行时间 |
| `timeIntervalBetweenPoints_SEC` | 值取决于运行时间 |
| `outputIntervalIndicator` | 1 |
| `epochTimeOfElements_DUT` | 值取决于运行时间 |
| `epochTimeOfElements_DAY.` | 值取决于运行时间 |
| `epochA1Greg.` | 值取决于运行时间 |
| `epochUtcGreg.` | 值取决于运行时间 |
| `yearOfEpoch_YYY` | 值取决于运行时间 |
| `monthOfEpoch_MM` | 值取决于运行时间 |
| `dayOfEpoch_DD` | 值取决于运行时间 |
| `hourOfEpoch_HH` | 值取决于运行时间 |
| `minuteOfEpoch_MM` | 值取决于运行时间 |
| `secondsOfEpoch_MILSEC` | 值取决于运行时间 |
| `keplerianElementsAtEpoch_RAD[0]` | 值取决于运行时间 |
| `keplerianElementsAtEpoch_RAD[1]` | 值取决于运行时间 |
| `keplerianElementsAtEpoch_RAD[2]` | 值取决于运行时间 |
| `keplerianElementsAtEpoch_RAD[3]` | 值取决于运行时间 |
| `keplerianElementsAtEpoch_RAD[4]` | 值取决于运行时间 |
| `keplerianElementsAtEpoch_RAD[5]` | 值取决于运行时间 |
| `cartesianElementsAtEpoch_DULT[0]` | 值取决于运行时间 |
| `cartesianElementsAtEpoch_DULT[1]` | 值取决于运行时间 |
| `cartesianElementsAtEpoch_DULT[2]` | 值取决于运行时间 |
| `cartesianElementsAtEpoch_DULT[3]` | 值取决于运行时间 |
| `cartesianElementsAtEpoch_DULT[4]` | 值取决于运行时间 |
| `cartesianElementsAtEpoch_DULT[5]` | 值取决于运行时间 |
| `startTimeOfEphemeris_DUT` | 值取决于运行时间 |
| `endTimeOfEphemeris_DUT` | 值取决于运行时间 |
| `timeIntervalBetweenPoints_DUT` | 值取决于运行时间 |
| `dateOfInitiationOfEphemComp_YYYMMDD` | 值取决于运行时间 |
| `timeOfInitiationOfEphemComp_HHMMSS` | 值取决于运行时间 |
| `utcTimeAdjustment_SEC` | 0.000000 |
| `Pecession/Nutation indicator`（岁差/章动指示符） | 1 |

对于星历头部记录 1，有一些必填字段未被列入 GMAT 的 Code 500 星历头部记录 1 的表格中。这些未列入头部记录 1 的字段列于下表。0.0 表示"已使用"，1.0 表示"未使用"。

| 必填字段 | 注释 |
|----------|------|
| `Zonal and tesseral harmonics indicator`（带谐和田谐项指示符） | 1.0 |
| `Lunar gravitation perturbation indicator`（月球引力摄动指示符） | 1.0 |
| `Solar radiation perturbation indicator`（太阳光压摄动指示符） | 1.0 |
| `Solar gravitation perturbation indicator`（太阳引力摄动指示符） | 1.0 |
| `Atmospheric drag perturbation indicator`（大气阻力摄动指示符） | 1.0 |
| `Greenwich hour angle at epoch`（历元格林尼治时角） | 1.0 |

## 示例

本例展示如何生成一个简单的星历文件。星历文件按两天的传播生成。在默认设置下，星历文件在每个积分步生成，并采用 CCSDS 文件格式。星历数据被发送到名为 'EphemerisFile2.eph' 的文本文件：

```
Create Spacecraft aSat
Create Propagator aProp

Create EphemerisFile anEphmerisFile

anEphmerisFile.Spacecraft = aSat
anEphmerisFile.Filename = 'EphemerisFile2.eph'

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 2}
```

说明：创建航天器、传播器和星历文件资源，指定星历文件对应的航天器和文件名（默认 CCSDS-OEM 格式、按积分器步长输出），传播 2 天即生成星历文件。

本例展示在包含脉冲机动等不连续事件的差分校正迭代过程中星历文件是如何生成的。星历数据被发送到名为 'EphemerisFile3.eph' 的文本文件：

```
Create Spacecraft aSat
Create Propagator aProp

Create ImpulsiveBurn TOI
Create DifferentialCorrector aDC

Create EphemerisFile anEphmerisFile

anEphmerisFile.Spacecraft = aSat
anEphmerisFile.Filename = 'EphemerisFile3.eph'

BeginMissionSequence

Propagate aProp(aSat) {aSat.Earth.Periapsis}

Target aDC
 Vary aDC(TOI.Element1 = 0.24, {Perturbation = 0.001, Lower = 0.0, ...
 Upper = 3.14159, MaxStep = 0.5})
 Maneuver TOI(aSat)
 Propagate aProp(aSat) {aSat.Earth.Apoapsis}
 Achieve aDC(aSat.Earth.RMAG = 42165)
EndTarget

Propagate aProp(aSat) {aSat.ElapsedDays = 1}
```

说明：传播到近地点后进入 Target 差分校正循环，调整脉冲机动 TOI 的第一个分量使远地点半径达到 42165 km；星历文件只写入迭代最终解对应的轨迹，脉冲机动处的不连续由 GMAT 分段插值处理；循环结束后再传播 1 天。

本例展示如何生成一个简单的 STK-TimePosVel（即 STK .e）星历文件。星历文件按 1 天的传播生成，然后发生一次简单的脉冲机动，航天器再传播一天。此星历按原始积分器步长生成。

```
Create Spacecraft aSat
Create Propagator aProp

Create ImpulsiveBurn IB
IB.Element1 = 0.5

Create EphemerisFile anEphmerisFile

anEphmerisFile.Spacecraft = aSat
anEphmerisFile.Filename = 'EphemerisFile.e'
anEphmerisFile.FileFormat = STK-TimePosVel


BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1}
Maneuver IB(aSat)
Propagate aProp(aSat) {aSat.ElapsedDays = 1}
```

说明：FileFormat 设为 STK-TimePosVel 后输出 .e 格式星历；传播 1 天、施加 0.5 km/s 脉冲机动、再传播 1 天，机动前后两段星历在文件中分成独立的数据块。
