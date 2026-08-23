# 平滑器（Smoother）

> 译自 GMAT R2026a 帮助文档 Smoother.html

**Smoother** —— 一种反向滤波器，通过对前向与反向序贯估计结果进行加权组合，给出改进的状态估计。

## 描述

一种固定区间、反向运行的序贯估计器，采用 Fraser-Potter 算法融合前向与反向的估计状态。

**另请参阅**：ExtendedKalmanFilter、RunSmoother

## 字段

| 字段 | 描述 |
|------|------|
| **AddPredictToMatlabFile** | 设为 True 时，在 MATLAB 文件中包含平滑器预测弧段的数据。仅当 `PredictTimeSpan` 非零时才会生成预测数据。将此参数设为 True 会把预测状态、协方差、过程噪声和状态转移矩阵(STM)添加到平滑器 MATLAB 数据文件中。<br>数据类型：True/False；允许值：True 或 False；访问方式：Set；默认值：**False**；单位：N/A；接口：脚本 |
| **DelayRectifyTimeSpan** | 定义一段时间（从热启动或初始化开始），在此期间参考轨迹由先验状态或初始状态生成。与通常一样，所有测量量仍用于更新估计状态，但不会应用于用于线性化的参考轨迹。延迟修正时间跨度结束后，先验状态被丢弃，当前滤波器估计状态被用作线性化的参考轨迹，这符合扩展卡尔曼滤波(EKF)的正常运行方式。<br>此参数在使用 Fraser-Potter 平滑算法时作用于反向滤波器。`ExtendedKalmanFilter` 资源上的前向滤波器存在一个类似参数。有关此参数的更多说明，请参见下文"备注"。<br>数据类型：Real；允许值：Real >= 0；访问方式：Set；默认值：**0**；单位：Seconds；接口：脚本 |
| **Filter** | 前向运行的 `Filter` 实例，其中包含平滑器要处理的状态和协方差。<br>数据类型：Resource；允许值：用户定义的 `ExtendedKalmanFilter` 资源实例；访问方式：Set；默认值：**None**；单位：N/A；接口：脚本 |
| **MatlabFile** | 输出 MATLAB 数据文件的文件名。不设置此参数则不会生成 MATLAB 文件。<br>数据类型：String；允许值：包含有效文件名的字符串；访问方式：Set；默认值：**None**；单位：N/A；接口：脚本 |
| **MeasDeweightingCoefficient** | 平滑器所用的反向传播 EKF 的测量量降权（Measurement Underweighting）系数。使用默认值时，测量量降权实际上被关闭。我们采用参考文献 1 中式 (4.36) 描述的 Lear 测量量降权方法。更多细节请参见 `ExtendedKalmanFilter` 资源的"备注"。<br>数据类型：Real；允许值：Real >= 0；访问方式：Set；默认值：**0.0**；单位：N/A；接口：脚本 |
| **MeasDeweightingSigmaThreshold** | 用于测量量降权处理的 1-sigma RSS 位置阈值。仅当由误差协方差矩阵导出的 1-sigma RSS 位置阈值大于此阈值，**且** `MeasDeweightingCoefficient` 大于 0 时，才执行测量量降权。<br>数据类型：Real；允许值：Real >= 0；访问方式：Set；默认值：**1.0**；单位：km；接口：脚本 |
| **PredictTimeSpan** | 处理完最后一个测量量之后，平滑器星历预测的时间跨度（秒）。<br>数据类型：Real；允许值：Real >= 0；访问方式：Set；默认值：**0**；单位：Seconds；接口：脚本 |
| **ReportFile** | 平滑器输出报告文件名。<br>数据类型：String；允许值：包含有效文件名的字符串；访问方式：Set；默认值：**'Smoother' + 实例名 + '.data'**；单位：N/A；接口：脚本 |
| **ReportStyle** | 指定平滑器报告输出的级别。若选择 Normal 模式，仅生成平滑器报告文件。若选择 Verbose 模式，将额外生成平滑器反向滤波运行的输出报告文件。选择 Verbose 模式要求用户在 GMAT 启动文件中设置 RUN_MODE = Testing。<br>数据类型：String；允许值：Normal、Verbose；访问方式：Set；默认值：**Normal**；单位：N/A；接口：脚本 |

## 备注

### Fraser-Potter 平滑器

`Smoother` 资源实现了参考文献 1 和参考文献 2 所描述的 Fraser-Potter（FP）固定区间平滑器。FP 平滑器首先在与滤波器"前向"运行相同的弧段上反向（从最新到最早测量量）运行一个滤波器。反向滤波器的初始状态设为前向滤波器的最终状态。反向滤波器的初始协方差设为前向滤波器末端协方差的对角元素，其中位置和速度方差乘以 1e+10 的比例因子，其他估计参数方差乘以 1e+4 的因子。反向滤波器初始协方差的非对角元素被置零。每个时间更新或测量更新处的平滑器估计，由前向滤波器估计与反向平滑器估计的加权线性组合构成。更多数学细节请参见参考文献。

反向滤波器初始协方差的膨胀使其在收敛弧段内容易发散并出现其他数值误差。如果平滑器运行失败，强烈建议将 `DelayRectifyTimeSpan` 设置为通常足以使滤波器收敛的时间跨度后再次尝试平滑运行。在 Normal 模式下，平滑器输出报告文件不包含反向滤波过程的结果，但您可以将平滑器 `ReportStyle` 设为 `Verbose`（需要在 gmat_startup_file.txt 中设置 RUN_MODE = TESTING），以生成反向滤波运行的报告，协助故障排查。

### 导航要求使用定步长数值积分

GMAT 导航要求使用定步长积分。`ExtendedKalmanFilter` 资源有一个 `Propagator` 字段，其中包含估计过程中将使用的 `Propagator` 资源名称。如下方**注意**所示，对与您积分器关联的 `ForceModel` 资源所指定的误差控制存在一些硬性限制。

> **注意**：与 `ExtendedKalmanFilter` 的 `Propagator` 关联的 `ForceModel` 资源所指定的 `ErrorControl` 参数必须设为 `None`。当然，使用定步长控制时，用户必须根据所选轨道类型和力模型剖面，选择合适的步长（由 `Propagator` 的 `InitialStepSize` 字段给出），以达到所需精度。

### 平滑器 MATLAB 数据文件

如果已安装 MATLAB 并正确配置了与 GMAT 的接口（参见 MATLAB Interface），用户可以生成包含 `Smoother` 运行有用分析数据的 mat 文件。通过在已配置的 `Smoother` 资源的 `MatlabFile` 字段上指定输出文件的路径和文件名即可启用此选项。除下表注明的情况外，mat 文件中数据的单位与平滑器输出文件相同：秒、km、km/sec、DSN 测距单位、Hz 和度。

平滑器 MATLAB 文件的 `EstimationConfig` 和 `Observed` 结构与滤波器资源中的相同，在滤波器资源文档中有描述（参见"Kalman Filter MATLAB Data File"一节）。平滑器反向滤波运行的输出存储在平滑器输出文件的 `BackwardComputed` 和 `BackwardFilter` 结构中。它们与前向滤波 MATLAB 文件中的 `Computed` 和 `Filter` 结构具有相同的结构和内容，同样在滤波器资源文档中有描述。

平滑器 MATLAB 文件的 `Computed` 结构与滤波器中的对应结构略有不同。平滑器 `Computed` 结构的内容如下表所示。

| 变量 | 描述 |
|------|------|
| Elevation | 测量历元处的计算仰角（度）。不适用于 GPS_PosVec 数据（设为 0）。 |
| IonosphericCorrection | 电离层测量修正的大小。单位与测量量相同。关于 X/Y 角度测量的介质修正，请参见下方说明。 |
| Measurement | 计算测量量。对于 GPS_PosVec，每个单元保存一个 1x3 的 X、Y、Z 计算测量量列向量。 |
| MeasurementEditFlag | 字符串观测编辑标志。'N' 表示未编辑/被接收的观测。 |
| MeasurementNumber | 测量记录编号。 |
| MeasurementPartials | 矩阵元胞数组。每个成员是测量量对状态各元素的偏导数矩阵。偏导数针对 Spacecraft `SolveFors` 字段上选择的元素类型求取。例如，若用户选择估计 KeplerianState，则偏导数针对开普勒元素求取。元素顺序与 EstimationConfig 状态名称中给出的一致。对于 GPS_PosVec 数据，每个单元保存一个 3xN 矩阵，其中 N 为估计状态数。每行依次包含对 X、Y、Z GPS_PosVec 测量量的偏导数。 |
| PreUpdateCovariance | 测量更新前的平滑器状态协方差。 |
| PreUpdateCovarianceVNB | 测量更新前的平滑器状态协方差（VNB 参考系）。 |
| Residual | 测量更新前的平滑器状态残差。 |
| PreUpdateState | 测量更新前的平滑器状态。 |
| ScaledResidual | 无量纲值，表示原始残差除以状态噪声（经适当变换）与测量噪声之和。示意公式：Scaled Residual = Raw Residual / (HPH' + R)。 |
| TroposphericCorrection | 对流层测量修正的大小。单位与测量量相同。关于 X/Y 角度测量的介质修正，请参见下方说明。 |

`Smoother` 结构的内容如下表所示。

| 变量 | 描述 |
|------|------|
| Covariance | 测量更新或时间更新后的平滑器状态协方差（笛卡尔坐标）。 |
| CovarianceVNB | 测量更新或时间更新后的平滑器状态协方差（VNB 坐标）。 |
| EpochTAI | 每条平滑器记录的 TAI 历元。每个成员是一个列向量，第一行为 MATLAB datenum 形式的历元，第二行为 GMAT TAIModJulian 日期形式的历元。 |
| EpochUTC | 每条平滑器记录的 UTC 历元。每个成员是一个列向量，第一行为 MATLAB datenum 形式的历元，第二行为 GMAT UTCModJulian 日期形式的历元。 |
| MeasurementNumber | 测量记录编号。初始步或时间更新步设为 NaN。 |
| State | 测量更新或时间更新后的平滑器状态。 |
| UpdateType | 滤波器更新模式（Initial、Time 或 Measurement）。 |

## 示例

下面是一个已配置的 `Smoother` 实例示例。在此示例中，`EKF` 是一个 `ExtendedKalmanFilter` 实例。

```
Create Smoother SMO;

SMO.Filter          = EKF;
SMO.PredictTimeSpan = 86400.;
SMO.ReportFile      = 'smoother_run.txt';
SMO.MatlabFile      = 'smoother_run.mat';

BeginMissionSequence;

RunSmoother SMO;
```

**中文说明**：创建名为 SMO 的平滑器，将其前向滤波器设为 EKF，预测时间跨度设为 1 天（86400 秒），指定报告文件和 MATLAB 输出文件，然后在任务序列中运行平滑器。

## 参考文献

1. Carpenter, Russell and Chris D'Souza. *Navigation Filter Best Practices*. Technical Report TP-2018-219822, NASA, April 2018.（NASA 技术报告《导航滤波器最佳实践》）
2. D. C. Fraser and J. E. Potter, "The Optimum Linear Smoother as a Combination of Two Optimum Linear Filters", *IEEE Trans. Automat. Contr.*, vol. AC-14, no. 4, pp. 387-390, Aug. 1969.（《作为两个最优线性滤波器组合的最优线性平滑器》）
