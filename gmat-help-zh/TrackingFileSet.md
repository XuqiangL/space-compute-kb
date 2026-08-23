# 跟踪文件集（TrackingFileSet）

> 译自 GMAT R2026a 帮助文档 TrackingFileSet.html

**TrackingFileSet** —— 管理包含在一个或多个外部跟踪数据文件中的观测数据。

## 描述

仿真器运行和估计器运行都需要 `TrackingFileSet`。对于数据仿真运行，用户必须指定仿真数据所需的跟踪链（通过 `AddTrackingConfig`），并为仿真的跟踪观测提供输出文件名（通过 `FileName`）。在仿真模式下，用户可以根据所仿真跟踪数据的类型指定测距取模常数、多普勒计数区间等参数。更多细节见下文备注。对于仿真器和估计器，均可选择应用测量修正和介质修正。

运行估计器时，`FileName` 参数指定预先生成的外部跟踪数据文件的路径。运行估计器时不必显式指定跟踪配置；GMAT 将检查指定的外部跟踪数据文件并尝试自动确定跟踪配置。如果 GMAT 无法唯一识别跟踪数据文件中的所有对象，将抛出错误消息。

运行估计器时，可采用一个或多个 `AcceptFilter` 和/或 `RejectFilter`，从所有可用观测中选择较小的子集用于估计过程。

**另请参阅**：Simulator、BatchEstimator、AcceptFilter、RejectFilter、Tracking Data Types for Orbit Determination

## 字段

| 字段 | 描述 |
|------|------|
| **AberrationCorrection** | 对角度测量量应用光行差修正。此修正仅适用于角度测量类型。<br>Diurnal（周日）修正仅考虑因中心天体自转引起的观测者速度。Annual（周年）修正仅考虑因中心天体轨道运动引起的观测者速度。AnnualAndDiurnal 修正同时考虑两种效应。<br>数据类型：String；允许值：None、Annual、Diurnal、AnnualAndDiurnal；访问方式：set；默认值：**None**；单位：N/A；接口：脚本 |
| **AddTrackingConfig** | 用于仿真或估计的一个或多个信号路径和测量类型。跟踪链规格的详细信息见下文备注一节。<br>数据类型：String；允许值：{{Tracking Strand}, MeasurementType1[, MeasurementType2, ...]}；访问方式：set；默认值：**None**；单位：N/A；接口：脚本 |
| **DataFilters** | 定义应用于数据的滤波器。可指定任一类型（`AcceptFilter`、`RejectFilter`）的一个或多个滤波器。`TrackingFileSet` 上的数据滤波器所指定的规则用于确定哪些数据被准许或拒绝作为估计过程的输入。<br>数据类型：Resource array；允许值：用户定义的 `AcceptFilter` 和 `RejectFilter` 资源实例；访问方式：set；默认值：**None**；单位：N/A；接口：脚本 |
| **FileName** | 仿真时，指定仿真测量数据的输出文件。估计时，指定一个或多个已存在的 GMD 格式跟踪数据输入文件。<br>数据类型：String；允许值：有效文件路径；访问方式：set；默认值：**None**；单位：N/A；接口：脚本 |
| **MaxCentralAngleOfRayPath** | 仅用于空-空跟踪。指定以中心天体中心为顶点、跟踪卫星与目标卫星之间的夹角。如果空-空跟踪测量（如 TDRS 跟踪）的参与方分离角在此角度以内，无论计算出的射线路径高度如何，测量都将被接收。如果参与方分离角大于此值，则应用 `MinHeightOfRayPath` 准则来决定接收与否。此参数通常与 `MinHeightOfRayPath` 结合使用，以指定剔除可能经历过度大气折射的空-空跟踪信号的准则。<br>数据类型：Real；允许值：0 <= MaxCentralAngleOfRayPath <= 180；访问方式：set；默认值：**70 度（对地心轨道）**；对于环绕地球以外天体的轨道，默认忽略此约束，见下文备注；单位：Degrees；接口：脚本 |
| **MinHeightOfRayPath** | 仅用于空-空跟踪。指定空-空跟踪信号路径在地球表面以上（采用赤道半径的球形模型）被接收的最小高度。仅当计算出的射线路径中心角超过 `MaxCentralAngleOfRayPath` 时才检验此参数。因此准则被剔除的任何测量，在估计器输出报告中以 HORP 编辑标志标记。<br>数据类型：Real；允许值：Real >= 0；访问方式：set；默认值：**500 km（对地心轨道）**；对于环绕地球以外天体的轨道，默认忽略此约束，见下文备注；单位：Kilometers；接口：脚本 |
| **RampTable** | 指定在仿真和估计中计算测量量时使用的发射频率斜坡表。<br>数据类型：String；允许值：有效文件路径；访问方式：set；默认值：**None**；单位：N/A；接口：脚本 |
| **SimDopplerCountInterval** | 指定仿真多普勒和测距变率测量时使用的多普勒计数区间。运行估计时不使用此参数。估计时，多普勒计数区间应已在 GMD 文件中指定。<br>数据类型：Real；允许值：Real > 0；访问方式：set；默认值：**1.0**；单位：Seconds；接口：脚本 |
| **SimRangeModuloConstant** | 指定仿真用的 DSN 测距模糊区间值。运行估计时不使用此参数。估计时，测距模数（需要时）应已在 GMD 文件中指定。<br>数据类型：Real；允许值：Real > 0；访问方式：set；默认值：**1.00E+18**；单位：Range Units (RU)；接口：脚本 |
| **SimTDRSServiceAccessList** | 仿真用的 TDRS 业务接入列表。将从列表中提供的业务中随机选择一种业务。运行估计时不使用此参数。估计时，TDRS 业务 ID 应已在 GMD 文件中指定。<br>数据类型：String list；允许值：'SA1'、'SA2' 或 'MA'；访问方式：set；默认值：**{SA1}**；单位：None；接口：脚本 |
| **SimTDRSSmarId** | 仿真用的 S 频段多址返向（SMAR）下行频率 ID。运行估计时不使用此参数。估计时，SMAR ID 应已在 GMD 文件中指定。<br>数据类型：Integer；允许值：1 至 30（含）之间的整数；访问方式：set；默认值：**1**；单位：None；接口：脚本 |
| **SimTDRSTrackerType** | 仿真 TDRS MA 业务的跟踪器类型指示符。运行估计时不使用此参数。估计时，TDRS 跟踪器类型应已在 GMD 文件中指定。<br>数据类型：Integer；允许值：0 = STGT/传统型，1 = TDRS-K；访问方式：set；默认值：**0**；单位：None；接口：脚本 |
| **TimeGapForPassBreak** | 测量之间表示新跟踪弧圈开始的时间间隔（秒）。相隔大于此时间跨度的连续测量被假定来自不同的跟踪弧圈。这与 ErrorModel 的 PassBiases 求解选项结合使用。更多细节见 ErrorModel 资源的备注一节。<br>数据类型：Real；允许值：Real > 0；访问方式：set；默认值：**1e70**；单位：Seconds；接口：脚本 |
| **UseETminusTAI** | 指定是否对测量量进行广义相对论时间修正的标志。若设置此标志，GMAT 在求解计算测量量的光行时方程时，将应用从 TAI 到星历时（Ephemeris Time）的调整。<br>我们强烈建议：对于任何包含发射节点与接收节点不同的跟踪链的跟踪文件集，无论测量路径的总光行时或其距太阳的距离如何，都将此标志设为 True。更多细节见下文备注。<br>数据类型：Boolean；允许值：True、False；访问方式：set；默认值：**False**；单位：N/A；接口：脚本 |
| **UseLightTime** | 指定是否对计算测量量应用光行时修正的标志。<br>数据类型：Boolean；允许值：True、False；访问方式：set；默认值：**True**；单位：N/A；接口：脚本 |
| **UseRelativityCorrection** | 指定是否对计算测量量进行广义相对论修正的标志。若设置此标志，GMAT 将调整计算光行时，以包含光的坐标速度效应和信号路径弯曲效应。更多细节见下文备注。<br>数据类型：Boolean；允许值：True、False；访问方式：set；默认值：**False**；单位：N/A；接口：脚本 |

## 备注

有关 GMAT 支持的所有轨道确定跟踪数据类型和跟踪数据文件格式的详细列表，请参见《Tracking Data Types for Orbit Determination》。

将 `UseETminusTAI` 设为 True，对应于在计算的往返光行时中包含 Moyer 所著《Formulation of Observed and Computed Values of Deep Space Network Data Types for Navigation》（JPL 出版物 00-7，2000 年 10 月）式 11-7 中的 ET-TAI 上行和下行项。当像 GMAT 那样选择在太阳系质心系中构建光行时时，对于发射站与接收站相同的测量路径，ET-TAI 修正大部分相互抵消。然而，如果发射站与接收站不同，即使光行时很短，ET-TAI 修正也可能很显著，为获得最高精度的测量处理应将其包含在内。

将 `UseRelativityCorrection` 设为 True，对应于包含 Moyer 式 11-7 中的 RLT（相对论光行时）上行和下行项。

`SimRangeModuloConstant` 字段仅用于 DSN 测距跟踪数据的仿真。用户可以为此字段指定值，也可以省略（此时使用默认值）。此字段不适用于估计。估计时，该值在输入跟踪数据文件中提供。

`SimDopplerCountInterval` 用于 DSN_TCP 和 RangeRate 跟踪数据的仿真。用户可以为此字段指定值，也可以省略（此时使用默认值 1 秒）。此字段不适用于估计。估计时，该值在输入跟踪数据文件中提供。

### 射线路径编辑准则

与射线路径高度（HORP）测量编辑相关的约束 `MinHeightOfRayPath` 和 `MaxCentralAngleOfRayPath` 的默认值仅适用于地心轨道。默认情况下，对于环绕地球以外天体的航天器所涉及的空-空跟踪，不应用 HORP 约束。用户可以在脚本中为这些约束指定显式值，从而对非地心轨道应用 HORP 约束。若要对地球轨道禁用 HORP 约束，将 `MinHeightOfRayPath` 设为 0 km。

上述射线路径编辑准则对仿真和估计同样适用。在仿真情况下，准则决定仿真测量量将被写入跟踪数据文件还是被忽略。在估计情况下，准则决定测量量将在批处理估计器或卡尔曼滤波器中被接收还是被排除在状态更新之外。

### 跟踪链规格

仿真跟踪数据时，必须使用 `AddTrackingConfig` 参数指定至少一条跟踪链。跟踪链必须用花括号括起。跟踪链的格式取决于所生成的测量数据类型。请以下表为指南。使用真实跟踪数据进行估计时，不必指定跟踪链；此时 GMAT 将检查输入跟踪数据文件并自动确定文件中存在的跟踪链。

> **注意**：在仿真和估计中，接收站的误差模型决定测量特性（偏差和噪声），发射站的误差模型特性被忽略。

| 测量类型名称 | 跟踪链规格格式 |
|--------------|----------------|
| 所有角度类型、Range_Skin、DSN_SeqRange、DSN_PNRange、DSN_TCP | {XmitGroundStation, Spacecraft, RecvGroundStation} |
| Range、RangeRate（地对空） | 双向或三向链：{XmitGroundStation, Spacecraft, RecvGroundStation}；单向链：{Spacecraft, RecvGroundStation} |
| Range、RangeRate（空对空） | {XmitSpacecraft, Spacecraft, RecvSpacecraft} |
| BRTS_Doppler、BRTS_Range | {XmitGroundStation, ForwardTDRS, BRTSGroundStation, ReturnTDRS, RecvGroundStation} |
| GPS_PosVec | {Spacecraft.Receiver} |
| SN_Doppler、SN_Range | {XmitGroundStation, ForwardTDRS, SNUserSpacecraft, ReturnTDRS, RecvGroundStation} |
| SN_Doppler_Rtn | {SNUserSpacecraft, ReturnTDRS, RecvGroundStation} |
| SN_DOWD | {SNUserSpacecraft, ReturnTDRS1, RecvGroundStation1, ReturnTDRS2, RecvGroundStation2} |

### 测量修正

`TrackingFileSet` 对象用于指定 GMAT 在推导计算测量量时可应用的各种修正。某些修正不适用于某些测量类型。光行差修正仅适用于角度测量类型，而 GPS_PosVec 不适用任何修正。选择不适用的修正不会导致错误，但不会应用任何修正。

## 示例

此示例说明使用 `TrackingFileSet` 对象仿真 DSN 跟踪数据。运行估计器时，跟踪配置（`AddTrackingConfig`）的指定是可选的；若省略，GMAT 将尝试自动检测跟踪数据文件中存在的跟踪配置。

在此示例中，频率斜坡表文件 `dsn.ramp` 必须是已存在的斜坡表。GMAT 不会仿真斜坡表记录。或者，用户在仿真数据时可以省略斜坡表的指定。若省略斜坡表，仿真器将使用挂载到每个 `GroundStation` 的 `Transmitter` 对象上指定的频率。

```
Create TrackingFileSet dsnObs;

%Create objects referenced by dnsObs
Create GroundStation GDS CAN MAD;
Create Spacecraft EstSat;
Create AcceptFilter af;
  
dsnObs.AddTrackingConfig       = {{GDS, EstSat, GDS}, 'DSN_TCP'};
dsnObs.AddTrackingConfig       = {{CAN, EstSat, CAN}, 'DSN_TCP'};
dsnObs.AddTrackingConfig       = {{MAD, EstSat, MAD}, 'DSN_TCP', 'DSN_SeqRange'};
dsnObs.FileName                = {'dsn.gmd'};
dsnObs.RampTable               = {'dsn.ramp'};
dsnObs.UseLightTime            = True;
dsnObs.UseRelativityCorrection = False;
dsnObs.UseETminusTAI           = False;
dsnObs.SimRangeModuloConstant  = 67108864;
dsnObs.SimDopplerCountInterval = 10.; 
dsnObs.DataFilters             = {af};

BeginMissionSequence;
```

**中文说明**：创建跟踪文件集 dsnObs，配置三条跟踪链（GDS/CAN/MAD 三站各自收发，MAD 站同时仿真 DSN_TCP 多普勒和 DSN_SeqRange 测距），输出文件 dsn.gmd，使用斜坡表 dsn.ramp，启用光行时修正，测距模数 67108864 RU，多普勒计数区间 10 秒，并应用接收滤波器 af。

此示例说明使用 `TrackingFileSet` 对象仿真 GPS_PosVec 跟踪数据。此示例假定 `GpsReceiver` 是先前创建的 `Receiver` 实例，并已使用 `AddHardware` 方法挂载到 `SimSat`。

```
Create TrackingFileSet PosVecObs;

PosVecObs.FileName          = {'posvec_obs.gmd'};
PosVecObs.AddTrackingConfig = {{SimSat.GpsReceiver}, 'GPS_PosVec'};
SimMeas.DataFilters         = {};

BeginMissionSequence;
```

**中文说明**：创建跟踪文件集 PosVecObs，输出文件 posvec_obs.gmd，跟踪链为 {SimSat.GpsReceiver}（星载 GPS 接收机），数据类型 GPS_PosVec，不使用数据滤波器。
