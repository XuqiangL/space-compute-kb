# 扩展卡尔曼滤波器（ExtendedKalmanFilter）

> 译自 GMAT R2026a 帮助文档 ExtendedKalmanFilter.html

**ExtendedKalmanFilter** —— 扩展卡尔曼滤波轨道确定估计器。

## 描述

实现扩展卡尔曼滤波(EKF)的序贯估计器。

**另请参阅**：BatchEstimator、TrackingFileSet、RunEstimator

## 字段

| 字段 | 描述 |
|------|------|
| **AddPredictToMatlabFile** | 设为 True 时，在 MATLAB 文件中包含扩展卡尔曼滤波器预测弧段的数据。仅当 `PredictTimeSpan` 非零时才会生成预测数据。将此参数设为 True 会把预测状态、协方差、过程噪声和状态转移矩阵(STM)添加到滤波器 MATLAB 数据文件中。<br>数据类型：True/False；允许值：True 或 False；访问方式：Set；默认值：**False**；单位：N/A；接口：脚本 |
| **DataFilters** | 定义应用于观测池的数据选择滤波器。可指定任一类型（`AcceptFilter`、`RejectFilter`）的一个或多个滤波器。`ExtendedKalmanFilter` 上的数据滤波器所指定的规则用于确定哪些测量被接收或被排除在状态更新计算之外。<br>数据类型：Resource array；允许值：用户定义的 `AcceptFilter` 和 `RejectFilter` 资源实例；访问方式：Set；默认值：**None**；单位：N/A；接口：脚本 |
| **DelayRectifyTimeSpan** | 定义一段时间（从热启动或初始化开始），在此期间参考轨迹由先验状态或初始状态生成。与通常一样，所有测量量仍用于更新估计状态，但不会应用于用于线性化的参考轨迹。延迟修正时间跨度结束后，先验状态被丢弃，当前滤波器估计状态被用作线性化的参考轨迹，这符合扩展卡尔曼滤波器的正常运行方式。<br>当初始状态协方差很大且测量噪声很小时，此参数可有助于收敛。将修正延迟到处理了足够多的测量量、确保状态估计已改进之后，可以防止滤波器因状态协方差过快收缩而立即发散。<br>修正将从 `DelayRectifyTimeSpan` 到期之前的最后一个测量量开始。在延迟修正生效期间，不会向指定的 `OutputWarmStartFile` 写入热启动记录。<br>数据类型：Real；允许值：Real >= 0；访问方式：Set；默认值：**0**；单位：Seconds；接口：脚本 |
| **InputWarmStartFile** | 包含状态和协方差记录的 CSV 格式文件。此文件应是先前 `ExtendedKalmanFilter` 运行的 `OutputWarmStartFile`。有关此文件的更多细节，请参见 `OutputWarmStartFile` 和下文备注。如果未指定 `InputWarmStartFile`，`ExtendedKalmanFilter` 将以"冷启动"（初始化）模式开始处理，使用资源对象设置。<br>数据类型：String；允许值：空，或有效热启动文件的路径；访问方式：Set；默认值：**None**；单位：N/A；接口：脚本 |
| **MatlabFile** | 输出 MATLAB 文件的文件名。不设置此参数则不会生成 MATLAB 文件。仅当 GMAT 正确连接到 MATLAB 时才能生成此文件。估计器 MATLAB 文件内容的细节见下文备注。<br>数据类型：String；允许值：任何有效文件名；访问方式：Set；默认值：**None**；单位：N/A；接口：脚本 |
| **MeasDeweightingCoefficient** | 测量量降权（Measurement Underweighting）所用的系数。使用默认值时，测量量降权实际上被关闭。如备注所示，我们采用参考文献 1 中式 (4.36) 描述的 Lear 测量量降权方法。<br>数据类型：Real；允许值：Real >= 0；访问方式：Set；默认值：**0.0**；单位：N/A；接口：脚本 |
| **MeasDeweightingSigmaThreshold** | 测量量降权处理所用的 1-sigma RSS 位置阈值。仅当由误差协方差矩阵导出的 1-sigma RSS 位置不确定度大于此阈值，**且** `MeasDeweightingCoefficient` 大于 0 时，才执行测量量降权。<br>数据类型：Real；允许值：Real >= 0；访问方式：Set；默认值：**1.0**；单位：km；接口：脚本 |
| **Measurements** | 指定标识估计所用测量量的 `TrackingFileSet` 列表。<br>数据类型：Resource array；允许值：一个或多个有效的 `TrackingFileSet` 实例；访问方式：Set；默认值：**空列表**；单位：N/A；接口：脚本 |
| **OutputWarmStartFile** | 用于存储热启动记录的输出文件的路径和名称。此文件在处理期间的所有滤波器时间更新和测量更新处接收完整状态和平方根协方差矩阵的下三角。此文件随后可被指定为 `InputWarmStartFile`，强制滤波器以热启动模式开始处理。建议此文件使用 ".csv" 后缀，但非必需。<br>数据类型：String；允许值：空，或任何有效文件名；访问方式：Set；默认值：**None**；单位：N/A；接口：脚本 |
| **PredictTimeSpan** | 处理完最后一个测量量之后，滤波器星历预测的时间跨度（秒）。<br>数据类型：Real；允许值：Real >= 0；访问方式：Set；默认值：**0**；单位：Seconds；接口：脚本 |
| **Propagator** | 指定估计所用的积分器资源实例。<br>数据类型：Object；允许值：有效的 `Propagator` 对象；访问方式：Set；默认值：**None**；单位：N/A；接口：脚本 |
| **ReportFile** | 指定输出估计报告文件的名称。<br>数据类型：String；允许值：包含有效文件名的字符串；访问方式：Set；默认值：**'ExtendedKalmanFilter' + 实例名 + '.data'**；单位：N/A；接口：脚本 |
| **ReportStyle** | 指定估计报告的类型。`Normal` 样式不包含观测 TAI、偏导数和频率信息的报告。选择 `Verbose` 模式要求用户在 GMAT 启动文件中设置 RUN_MODE = Testing。<br>数据类型：String；允许值：Normal、Verbose；访问方式：Set；默认值：**Normal**；单位：N/A；接口：脚本 |
| **ScaledResidualThreshold** | 缩放残差编辑准则。缩放残差是一个无量纲值，表示原始残差除以状态噪声（经适当变换）与测量噪声之和。示意公式：Scaled Residual = Raw Residual / (HPH' + R)。如果计算出的缩放残差大于指定阈值，任何测量都将被编辑剔除（且不用于估计）。<br>数据类型：Integer；允许值：任意正整数；访问方式：Set；默认值：**3**；单位：N/A；接口：脚本 |
| **ShowAllResiduals** | 允许在 GMAT GUI 中显示残差图。<br>数据类型：On/Off；允许值：On 或 Off；访问方式：Set；默认值：**On**；单位：N/A；接口：脚本 |
| **ShowProgress** | 切换估计器输出报告文件的生成以及 GUI 控制台窗口中的附加详细输出。<br>数据类型：True/False；允许值：True 或 False；访问方式：Set；默认值：**True**；单位：N/A；接口：脚本 |
| **WarmStartEpoch** | 以热启动模式处理时开始处理的初始历元。GMAT 将在 `InputWarmStartFile` 中查找该时刻的记录。如果 `InputWarmStartFile` 中不存在指定历元的记录，将使用最接近但早于指定历元的热启动记录。默认设置为 'FirstMeasurement'，表示 GMAT 将自动选择早于本次运行第一个可用测量量的、最接近的输入热启动记录。用户也可以指定 'LastWarmStartRecord'，自动使用输入热启动文件中的最后一条记录。<br>数据类型：String 或 Real；允许值：有效的 GMAT 历元字符串或数值、'FirstMeasurement' 或 'LastWarmStartRecord'；访问方式：Set；默认值：**FirstMeasurement**；单位：N/A；接口：脚本 |
| **WarmStartEpochFormat** | 指定热启动历元的格式和时间系统。<br>数据类型：String；允许值：UTCGregorian、UTCModJulian、TAIGregorian、TAIModJulian、TTGregorian、TTModJulian、A1Gregorian、A1ModJulian、TDBGregorian、TDBModJulian；访问方式：Set；默认值：**TAIModJulian**；单位：N/A；接口：脚本 |

## 备注

> **注意**：为卡尔曼滤波器配置数值积分器时，必须使用定步长选项。`ExtendedKalmanFilter` 所用的 `ForceModel` 的 `ErrorControl` 参数必须设为 `None`。当然，使用定步长控制时，用户必须选择合适的步长（由 `Propagator` 的 `InitialStepSize` 字段给出），使其对所选轨道类型和力模型剖面达到所需精度。

### 滤波器启动模式

`ExtendedKalmanFilter` 可以以首次初始化（此处称为"冷启动"）模式运行，也可以作为先前运行的延续（此处称为"热启动"模式）运行。

在冷启动模式下，脚本中配置的资源上所指定的状态和协方差用作滤波器初始状态和协方差。航天器初始协方差取自 Spacecraft 的 `OrbitErrorCovariance` 参数，其他估计参数的初始不确定度取自各参数关联的 "sigma" 值。例如，初始阻力系数在 Spacecraft 的 `Cd` 参数上指定，Cd 的初始不确定度在 Spacecraft 的 `CdSigma` 参数上指定。只要 ExtendedKalmanFilter 资源上未指定 `InputWarmStart` 文件，滤波器就以冷启动模式运行。

在热启动模式下，来自先前运行的滤波器完整状态和协方差用作滤波器初始状态和协方差。此模式允许用户以使滤波器在完全收敛状态下连续运行的方式停止和启动滤波器。要启用热启动，用户应在 EKF 资源上指定 `InputWarmStartFile`。用户还可以选择指定 `WarmStartEpoch`，以标识滤波器应开始处理的时刻。如果给出热启动历元，滤波器将忽略热启动历元之前的所有测量量。如果未给出热启动历元，滤波器将从第一个测量时刻启动，使用最接近但早于第一个测量时刻的输入热启动记录。热启动历元必须在输入热启动文件的时间跨度内。输入热启动文件理想情况下应是先前滤波器运行的输出热启动文件。

### 从扩展卡尔曼滤波运行生成星历文件

可以在卡尔曼滤波运行期间创建星历文件。星历文件按通常方法配置（参见 EphemerisFile）。此文件将包含测量更新步和时间更新步处的卡尔曼滤波估计状态。如果 KalmanFilter 的 `PredictTimeSpan` 非零，星历文件还将包含预测状态。测量更新通常不以恒定时间间隔发生，且每次测量更新处的估计状态至少有轻微不连续。出于这些原因，卡尔曼滤波器仅允许使用支持变步长的星历格式。在卡尔曼滤波运行期间不能生成 Code500 星历。

> **注意**：在滤波器或平滑器运行期间生成 STK 星历时，STK 星历资源上的 `IncludeEventBoundaries` 应始终设为 `True`。滤波器星历在每次测量处总是至少有轻微不连续，包含事件边界可确保 STK 星历的用户不会试图在这些不连续处进行不当插值。

### 在卡尔曼滤波器中使用 ReportFile 资源

可以配置一个 `ReportFile` 资源（参见 ReportFile）在滤波运行期间使用。这允许用户在估计运行期间将航天器状态、OrbitErrorCovariance、Cd、CdSigma 和其他估计参数等数据输出到自定义报告文件。自定义报告文件的内容取决于 `ReportFile` 的 `SolverIterations` 参数设置，如下所示：

- 如果 `SolverIterations` 为 `None`，仅写出运行中的最后一个状态。如果此时刻有测量量，报告的状态为测量更新前状态。
- 如果 `SolverIterations` 为 `Current`（默认值），在每次测量更新和时间更新处写出数据。每次测量更新处报告的状态为更新前状态。
- 如果 `SolverIterations` 为 `All`，在每次测量更新和时间更新处写出数据。在每次测量更新处同时报告更新前和更新后状态。

### 积分器设置

`ExtendedKalmanFilter` 资源有一个 `Propagator` 字段，其中包含估计过程中将使用的 `Propagator` 资源名称。积分器的最小步长 `MinStep` 应始终设为 0。

### 卡尔曼滤波器报告文件

滤波器测量统计报告（Filter Measurement Statistics）中为每种数据类型报告的加权 RMS 统计量是更新前残差的加权 RMS。

### 卡尔曼滤波器 MATLAB 数据文件

如果已安装 MATLAB 并正确配置了与 GMAT 的接口（参见 MATLAB Interface），用户可以生成包含 `ExtendedKalmanFilter` 运行有用分析数据的 mat 文件。通过在已配置的 `ExtendedKalmanFilter` 资源的 `MatlabFile` 字段上指定输出文件的路径和文件名即可启用此选项。该文件包含四个顶层数据结构——`EstimationConfig`、`Observed`、`Computed` 和 `Filter`。除下表注明的情况外，mat 文件中数据的单位与卡尔曼滤波器输出文件相同：秒、km、km/sec、DSN 测距单位、Hz 和度。

`EstimationConfig` 包含估计运行配置的一般信息。`EstimationConfig` 结构的内容如下表所示。

| 变量 | 描述 |
|------|------|
| InitialEpochUTC | 1x2 列向量，第一行为 MATLAB datenum 形式的滤波器起始历元，第二行为 GMAT TAIModJulian 形式。 |
| FinalEpochUTC | 1x2 列向量，第一行为 MATLAB datenum 形式的滤波器结束历元，第二行为 GMAT TAIModJulian 形式。 |
| GravitationalParameter | 本次运行主中心天体的引力参数，单位 km^3/sec^2。 |
| StateNames | 本次运行估计参数的名称。 |

`Observed` 结构包含跟踪数据观测的测量数据。`Observed` 结构的内容如下表所示。

| 变量 | 描述 |
|------|------|
| DopplerCountInterval | 每个多普勒类型测量量的多普勒计数区间。其他数据类型设为 NaN。 |
| EpochTAI | 每个测量量的 TAI 历元。每个成员是一个列向量，第一行为 MATLAB datenum 形式的历元，第二行为 GMAT TAIModJulian 日期形式的历元。 |
| EpochUTC | 每个测量量的 UTC 历元。每个成员是一个列向量，第一行为 MATLAB datenum 形式的历元，第二行为 GMAT UTCModJulian 日期形式的历元。 |
| Frequency | 信号接收频率（Hz）。GPS_PosVec 数据设为 NaN。 |
| Measurement | 观测测量量。对于 GPS_PosVec，每个单元保存一个 1x3 的 X、Y、Z 测量量列向量。 |
| MeasurementNumber | 测量记录编号。 |
| MeasurementType | GMAT 观测类型名称。 |
| MeasurementWeight | 测量权重 (1/noise^2)。对于 GPS_PosVec，每个单元保存一个 1x3 的 X、Y、Z 权重列向量。 |
| Participants | 对于每个测量量，一个元胞数组，其成员为测量路径中各参与方的 ID。 |
| RangeModulo | 对于每个 DSN_SeqRange 测量量，以测距单位计的测距模糊区间。其他数据类型设为 NaN。 |

**Computed** 结构存储滤波器测量更新的信息。`Computed` 结构的内容如下表所示。某些字段不适用于某些测量类型（例如 Elevation、Frequency 和 FrequencyBand 不适用于 GPS_PosVec 测量），并被设为 NaN 或零。`Computed` 结构中记录的历元可以通过将计算 `MeasurementNumber` 与 `Observed` 结构中相同的测量编号匹配来确定。

| 变量 | 描述 |
|------|------|
| Elevation | 测量历元处的计算仰角（度）。不适用于 GPS_PosVec 数据（设为 0）。 |
| IonosphericCorrection | 电离层测量修正的大小。单位与测量量相同。关于 X/Y 角度测量的介质修正，请参见下方说明。 |
| KalmanGain | 卡尔曼增益矩阵。 |
| Measurement | 计算测量量。对于 GPS_PosVec，每个单元保存一个 1x3 的 X、Y、Z 计算测量量列向量。 |
| MeasurementEditFlag | 字符串观测编辑标志。'N' 表示未编辑/被接收的观测。 |
| MeasurementNumber | 测量记录编号。 |
| MeasurementPartials | 矩阵元胞数组。每个成员是测量量对状态各元素的偏导数矩阵。偏导数针对 Spacecraft `SolveFors` 字段上选择的元素类型求取。例如，若用户选择估计 KeplerianState，则偏导数针对开普勒元素求取。元素顺序与 EstimationConfig 状态名称中给出的一致。对于 GPS_PosVec 数据，每个单元保存一个 3xN 矩阵，其中 N 为估计状态数。每行依次包含对 X、Y、Z GPS_PosVec 测量量的偏导数。 |
| PreUpdateCovariance | 测量更新前的滤波器状态协方差。 |
| PreUpdateCovarianceVNB | 测量更新前的滤波器状态协方差（VNB 参考系）。 |
| PreUpdateResidual | 测量更新前的滤波器状态残差。 |
| PreUpdateState | 测量更新前的滤波器状态。 |
| ScaledResidual | 无量纲值，表示原始残差除以状态噪声（经适当变换）与测量噪声之和。示意公式：Scaled Residual = Raw Residual / (HPH' + R)。 |
| TroposphericCorrection | 对流层测量修正的大小。单位与测量量相同。关于 X/Y 角度测量的介质修正，请参见下方说明。 |

**Filter** 结构存储在测量更新和时间更新处发生的处理信息。`Filter` 结构的内容如下表所示。

| 变量 | 描述 |
|------|------|
| Covariance | 测量更新或时间更新后的滤波器状态协方差（笛卡尔坐标）。 |
| CovarianceVNB | 测量更新或时间更新后的滤波器状态协方差（VNB 坐标）。 |
| EpochTAI | 每条滤波器记录的 TAI 历元。每个成员是一个列向量，第一行为 MATLAB datenum 形式的历元，第二行为 GMAT TAIModJulian 日期形式的历元。 |
| EpochUTC | 每条滤波器记录的 UTC 历元。每个成员是一个列向量，第一行为 MATLAB datenum 形式的历元，第二行为 GMAT UTCModJulian 日期形式的历元。 |
| MeasurementNumber | 测量记录编号。时间更新步设为 NaN。 |
| ProcessNoise | 滤波器过程噪声矩阵。 |
| State | 测量更新或时间更新后的滤波器状态。 |
| StateTransitionMatrix | 从 **t_(i-1)** 到 **t_i** 的状态转移矩阵 Φ_i，即 Φ_i = Φ(t_(i-1), t_i)。 |
| UpdateType | 滤波器更新模式（Initial、Time 或 Measurement）。 |

### MATLAB 文件中 X/Y 角度数据的介质修正

在构建计算角度测量量时，GMAT 将电离层和对流层修正作为对地面站到航天器斜距矢量的仰角调整来应用。所有计算角度观测量随后由斜距矢量导出。此过程给出应用于仰角的精确修正，但对其他角度测量类型的修正不会被直接计算和存储。为了向用户提供 X/Y 角度这些修正的估计值，GMAT 通过另一种方法由仰角修正计算近似的 X/Y 角度修正，并存储在 MATLAB 文件中。用户应注意，MATLAB 文件中存储的 X/Y 数据介质修正与构建 X/Y 计算测量量所用的方法并不完全一致。仰角大于 5 度时差异小于 1%，但仰角低于 5 度时差异可能达到 100% 量级。

### 测量量降权（Measurement Underweighting）

测量量降权改变扩展卡尔曼滤波器计算增益 K 的方式。

令某时刻 t_i 的卡尔曼增益为：

　　K_i = P_i^(−) · H_i^T · W_i^(−1)，其中 W_i ≡ (1 + MeasDeweightingCoefficient) · H_i · P_i^(−) · H_i^T + R_i

为 MeasDeweightingCoefficient 使用正值会使增益"变小"，并实际上使 t_i 时刻的测量量在计算 t_i 时刻估计状态时的重要性降低。注意，若 MeasDeweightingCoefficient = 0，则 K_i 为正常的卡尔曼增益。

令 3x3 矩阵 P̃_i^(−) 为状态估计误差协方差中与笛卡尔位置误差状态关联的分块。如果 sqrt(trace(P̃_i^(−))) > MeasDeweightingSigmaThreshold，GMAT 使用用户输入的 MeasDeweightingCoefficient 值计算卡尔曼增益；否则，GMAT 使用 MeasDeweightingCoefficient = 0。

## 示例

下面是一个已配置的扩展卡尔曼滤波估计器实例示例。在此示例中，`EstData` 是一个 `TrackingFileSet` 实例，`Prop` 是一个 `Propagator` 实例。此处未指定输入热启动文件，因此滤波器从冷启动（初始化）运行，但会生成输出热启动文件，可在后续运行中使用。

```
Create ExtendedKalmanFilter EKF;

EKF.ShowProgress            = True;
EKF.Measurements            = {EstData};
EKF.Propagator              = Prop;
EKF.ShowAllResiduals        = On;
EKF.ScaledResidualThreshold = 3.;
EKF.DataFilters             = {}
EKF.PredictTimeSpan         = 86400.;
EKF.ReportFile              = 'filter_report.txt';
EKF.MatlabFile              = 'filter.mat';
EKF.OutputWarmStartFile     = 'warm_start.csv';

BeginMissionSequence;
```

**中文说明**：创建扩展卡尔曼滤波器 EKF，指定测量数据 EstData 和积分器 Prop，缩放残差编辑阈值 3，预测时间跨度 1 天，输出报告文件、MATLAB 文件和热启动文件 warm_start.csv（供下次热启动使用）。

## 参考文献

1. Carpenter, Russell and Chris D'Souza. *Navigation Filter Best Practices*. Technical Report TP-2018-219822, NASA, April 2018.（NASA 技术报告《导航滤波器最佳实践》）
