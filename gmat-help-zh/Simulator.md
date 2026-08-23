# 测量仿真器（Simulator）

> 译自 GMAT R2026a 帮助文档 Simulator.html

**Simulator** —— 配置仿真跟踪数据测量量的生成。

## 描述

`Simulator` 配置仿真跟踪数据测量量的生成。这些测量量随后可被 `BatchEstimator` 资源用于估计运行。

`Simulator` 对象需要指定一个或多个 `TrackingFileSet` 资源实例，用于标识具体的跟踪数据观测链（observation strands）、数据类型、所需的测量修正以及输出跟踪数据文件名。仿真数据将以 GMAT 测量数据（GMD）ASCII 跟踪数据格式写出。您还必须为仿真运行指定时间跨度以及仿真观测之间的时间间隔。只有当跟踪链满足链中所有对象的可见性约束时（例如，观测必须高于地面站最小仰角屏蔽角），才会生成仿真观测。此外，您必须为仿真器配置并指定一个 `Propagator` 实例。最后，您可以选择向生成的测量量添加随机高斯白噪声，或生成无噪声测量量。如果 `AddNoise` 选项设为 On，则按每条测量链的 `ErrorModel` 上指定的标准差向测量量添加噪声。

**另请参阅**：TrackingFileSet、RunEstimator

## 字段

| 字段 | 描述 |
|------|------|
| **AddData** | 一个或多个 `TrackingFileSet` 的列表。<br>数据类型：`TrackingFileSet` 对象；允许值：任何有效的 `TrackingFileSet` 对象；访问方式：set；默认值：**None**；单位：N/A；接口：脚本 |
| **AddNoise** | 若为 true，向仿真观测添加噪声。<br>数据类型：Boolean；允许值：true、false、on、off；访问方式：set；默认值：**false**；单位：N/A；接口：脚本 |
| **EpochFormat** | 初始历元和最终历元的历元格式。<br>数据类型：STRING_TYPE；允许值：A1ModJulian、TAIModJulian、UTCModJulian、TTModJulian、TDBModJulian、A1Gregorian、TAIGregorian、TTGregorian、UTCGregorian、TDBGregorian；访问方式：set；默认值：**TAIModJulian**；单位：N/A；接口：脚本 |
| **InitialEpoch** | 数据仿真弧段的初始（起始）历元。在 GMAT 脚本中，需要先设置 `EpochFormat` 字段，再设置此字段。<br>数据类型：STRING_TYPE；允许值：Gregorian：04 Oct 1957 12:00:00.000 <= Epoch <= 28 Feb 2100 00:00:00.000；Modified Julian：6116.0 <= Epoch <= 58127.5；访问方式：set；默认值：**21545**；单位：N/A；接口：脚本 |
| **FinalEpoch** | 数据仿真弧段的最终（结束）历元。在 GMAT 脚本中，需要先设置 `EpochFormat` 字段，再设置此字段。<br>数据类型：STRING_TYPE；允许值：Gregorian：04 Oct 1957 12:00:00.000 <= Epoch <= 28 Feb 2100 00:00:00.000；Modified Julian：6116.0 <= Epoch <= 58127.5；访问方式：set；默认值：**21545**；单位：N/A；接口：脚本 |
| **MeasurementTimeStep** | 指定两个相邻仿真观测之间的时间步长（秒）。<br>数据类型：Real；允许值：Real > 0；访问方式：set；默认值：**60**；单位：seconds；接口：脚本 |
| **Propagator** | 用于推动航天器随时间前进的 `Propagator` 对象名称。可选地，可以使用单独的 `Propagator` 字段为仿真器配置中的特定航天器指定积分器，如下所述。<br>数据类型：有效的 `Propagator` 对象，可选地后跟一组有效的 `Spacecraft` 对象；允许值：任何有效的 `Propagator` 对象，可选地后跟一个或多个 `Spacecraft` 对象，即 *Propagator* 或 *{Propagator, Spacecraft[, Spacecraft2, Spacecraft3, etc.]}*；访问方式：set；默认值：**None**；单位：N/A；接口：脚本 |

## 备注

> **注意**：为仿真器配置数值积分器时，必须使用定步长选项。与 `Simulator` 的 `Propagator` 关联的 `ForceModel` 资源所指定的 `ErrorControl` 参数必须设为 `None`。当然，使用定步长控制时，用户必须根据所选轨道类型和力模型剖面，选择合适的步长（由 `Propagator` 的 `InitialStepSize` 字段给出），以达到所需精度。

### 积分器设置

`Simulator` 资源有一个 `Propagator` 字段，其中包含仿真过程中将使用的 `Propagator` 资源名称。积分器的最小步长 `MinStep` 应始终设为 0。

如果仿真器包含引用多艘航天器的跟踪配置，`Simulator` 将把第一个被标识的 `Propagator` 用作被仿真航天器的默认积分器。您可以使用可选的航天器列表为特定航天器指定不同的 `Propagator`，将这些航天器分配给其他积分器组件。此用法的示例如下所示。

### 地球以外的中心天体

GMAT 仿真器会考虑环绕地球以外天体运行的航天器的中心天体遮挡。例如，对于以月球为中心的航天器，仿真测量将排除航天器与地面站之间视线被月球遮挡的任何时刻。但请注意，GMAT 目前在此遮挡检查中使用球形形状模型。GMAT 在执行遮挡检查时将使用中心天体的极半径，任何天体扁率都被忽略。

### 交互关系

| 资源 | 描述 |
|------|------|
| `TrackingFileSet` 资源 | 必须创建，以便通过 `AddData` 字段告知 `Simulator` 资源将仿真哪些数据类型，并指定输出跟踪数据文件的名称（通过 `FileName`） |
| `Propagator` 资源 | GMAT 用它来生成仿真轨道 |
| `RunSimulator` 命令 | 必须使用 `RunSimulator` 命令来实际创建由 `Simulator` 资源定义的数据 |

## 示例

下面的示例说明如何使用仿真器生成 DSN 测距测量量。此示例比通常示例更详细，因为它可以实际运行并生成文件 `simData.gmd`，其中包含一个虚构 DSN 地面站的单条测距测量量。更全面的测量仿真示例，请参见第 13 章《Simulate DSN Range and Doppler Data》教程。

```
%Create and Configure Spacecraft
Create Spacecraft SimSat

SimSat.DateFormat  = UTCGregorian
SimSat.Epoch       = '19 Aug 2015 00:00:00.000'
SimSat.X           = -126544963
SimSat.Y           = 61978518
SimSat.Z           = 24133225
SimSat.VX          = -13.789
SimSat.VY          = -24.673
SimSat.VZ          = -10.662
SimSat.AddHardware = {SatTransponder, SatTranponderAntenna}

%Create and configure RF hardware
Create Antenna SatTranponderAntenna DSNReceiverAntenna DSNTransmitterAntenna

Create Transponder SatTransponder
SatTransponder.PrimaryAntenna = SatTranponderAntenna

Create Transmitter DSNTransmitter
DSNTransmitter.PrimaryAntenna = DSNTransmitterAntenna
DSNTransmitter.Frequency      = 7200

Create Receiver DSNReceiver
DSNReceiver.PrimaryAntenna = DSNReceiverAntenna

%Create and configure ground station and related error model
Create GroundStation DSN
DSN.AddHardware = ...
  {DSNTransmitter, DSNReceiver, DSNTransmitterAntenna, DSNReceiverAntenna}
DSN.ErrorModels = {DSNrange}

Create ErrorModel DSNrange
DSNrange.Type       = 'DSN_SeqRange'
DSNrange.NoiseSigma = 10

%Define data types
Create TrackingFileSet simData
simData.AddTrackingConfig = {{DSN,SimSat,DSN}, DSN_SeqRange}
simData.FileName          = {'simData.gmd'}

%   Create and configure the Simulator object
Create ForceModel FM1
FM1.ErrorControl = None   %Fixed step integration required for Navigation

Create Propagator prop
prop.FM      = FM1
prop.MinStep = 0          %For Navigation, allow propagator to take arbitrarily small steps   

Create Simulator Sim
Sim.AddData             = {simData}
Sim.Propagator          = prop
Sim.EpochFormat         = UTCGregorian
Sim.InitialEpoch        = '19 Aug 2015 08:00:00.000'
Sim.FinalEpoch          = '19 Aug 2015 08:00:01.000'
Sim.MeasurementTimeStep = 60
Sim.AddNoise            = On

%  Mission Sequence - run the simulator.

BeginMissionSequence

RunSimulator sim
```

**中文说明**：此示例创建航天器 SimSat 并设置其初始轨道状态；创建射频硬件（天线、应答机、发射机、接收机）；创建地面站 DSN 并挂载硬件和误差模型（DSN_SeqRange 类型，噪声 sigma 为 10）；定义 TrackingFileSet 指定跟踪配置和输出文件；创建力模型（ErrorControl 必须为 None，导航要求定步长积分）和积分器（MinStep=0 允许任意小步长）；最后创建 Simulator 配置仿真弧段和步长并加噪声，运行仿真生成 simData.gmd。

下一个示例展示如何在仿真器上编写多个积分器的脚本。此示例仅说明积分器的脚本编写，不包含其他对象设置。在此示例中，TDRS 航天器使用基于星历的 SPICE 积分器进行积分。仿真器中使用的任何其他航天器使用 SatProp 积分器进行积分。

```
% Create and Configure Spacecraft
Create Spacecraft SimSat

% This example assumes these BSP files exist in the GMAT output directory
Create Spacecraft TDRS6
TDRS6.OrbitSpiceKernelName = {'TDRS6Ephem.bsp'}

Create Spacecraft TDRS10
TDRS10.OrbitSpiceKernelName = {'TDRS10Ephem.bsp'}

%   Create and configure the Simulator object
Create ForceModel FM

Create Propagator SatProp
SatProp.FM      = FM
SatProp.MinStep = 0

Create Propagator TdrsProp
TdrsProp.Type   = SPK

Create Simulator Sim

Sim.Propagator = SatProp
Sim.Propagator = {TdrsProp, TDRS6, TDRS10}
```

**中文说明**：此示例假定 BSP 星历文件已存在于 GMAT 输出目录中。TDRS6 和 TDRS10 使用 SPK 类型积分器 TdrsProp（基于星历），其余航天器使用默认的 SatProp 积分器。通过两次给 `Sim.Propagator` 赋值实现：第一次设默认积分器，第二次用花括号列表将 TdrsProp 绑定到 TDRS6 和 TDRS10。
