# 批处理估计器（BatchEstimator）

> 译自 GMAT R2026a 帮助文档 BatchEstimator.html

**BatchEstimator** —— 批处理最小二乘估计器。

## 描述

批处理最小二乘估计器是一种获取参数向量 x0 估计值的方法，使得作为该参数函数的性能指标 J = J(x0) 最小化。对于我们的应用，x0 通常包括航天器在特定历元的位置和速度，性能指标是测量残差的加权平方和。

**另请参阅**：TrackingFileSet、RunEstimator

## 字段

| 字段 | 描述 |
|------|------|
| **AbsoluteTol** | 绝对加权 RMS 收敛准则容差。<br>数据类型：Real；允许值：Real > 0；访问方式：set；默认值：**0.001**；单位：无量纲；接口：脚本 |
| **DataFilters** | 定义应用于数据的滤波器。可指定任一类型（`AcceptFilter`、`RejectFilter`）的一个或多个滤波器。`BatchEstimator` 上的数据滤波器所指定的规则用于确定哪些数据被接收或被排除在状态更新计算之外。<br>数据类型：Resource array；允许值：用户定义的 `AcceptFilter` 和 `RejectFilter` 资源实例；访问方式：set；默认值：**None**；单位：N/A；接口：脚本 |
| **DataFile** | 输出 JSON 文件的路径和文件名，其中包含本次运行的观测、残差和其他数据的全精度记录。此文件内容的描述见下文**备注**。<br>数据类型：String；允许值：不设置，或有效路径和文件名；访问方式：set；默认值：**None**；单位：N/A；接口：脚本 |
| **EstimationEpoch** | 估计历元。这是与"求解参数"关联的历元。唯一允许的设置是 FromParticipants，它将估计历元定义为待估计卫星的当前（先验）历元。用户应在 `RunEstimator` 命令之前使用 `Propagate` 命令将待估卫星推进到所需的估计历元。<br>数据类型：String；允许值：'FromParticipants'；访问方式：set；默认值：**'FromParticipants'**；单位：N/A；接口：脚本 |
| **EstimationEpochFormat** | 估计历元格式。这是 `EstimationEpoch` 字段所需的输入格式。目前无功能。<br>数据类型：String；允许值：'FromParticipants'；访问方式：set；默认值：**'FromParticipants'**；单位：N/A；接口：脚本 |
| **FreezeIteration** | 指定在第几次迭代冻结被编辑剔除的测量选择。<br>数据类型：integer；允许值：任意正整数；访问方式：set；默认值：**4**；单位：N/A；接口：脚本 |
| **FreezeMeasurementEditing** | 允许冻结被编辑剔除的测量选择。<br>数据类型：true/false；允许值：true 或 false；访问方式：set；默认值：**false**；单位：N/A；接口：脚本 |
| **ILSEMaximumIterations** | 指定内环 sigma 编辑器（ILSE）允许的最大迭代次数。<br>数据类型：integer；允许值：任意正整数；访问方式：set；默认值：**15**；单位：N/A；接口：脚本 |
| **ILSEMultiplicativeConstant** | 内环 sigma 编辑（ILSE）所用的乘性常数。<br>数据类型：Real；允许值：Real > 0.0；访问方式：set；默认值：**3.0**；单位：无量纲；接口：脚本 |
| **InversionAlgorithm** | 用于求逆法方程的算法。<br>数据类型：String；允许值：Internal、Cholesky、Schur；访问方式：set；默认值：**Internal**；单位：N/A；接口：脚本 |
| **MatlabFile** | （已弃用）输出 MATLAB 文件的文件名。不设置此参数则不会生成 MATLAB 文件。仅当 GMAT 配置为连接到 MATLAB 实例时才能生成 MATLAB 数据文件。<br>此参数已弃用，由 `DataFile` 参数和 JSON 输出取代，后者不需要 MATLAB。JSON 文件可在 MATLAB 中读取，更多细节见下文**备注**。<br>数据类型：String；允许值：任何有效文件名；访问方式：set；默认值：**（未设置）**；单位：N/A；接口：脚本 |
| **MaxConsecutiveDivergences** | 指定批处理估计处理停止前允许的最大连续发散迭代次数。<br>数据类型：integer；允许值：任意正整数；访问方式：set；默认值：**3**；单位：N/A；接口：脚本 |
| **MaximumIterations** | 指定批处理估计允许的最大迭代次数。<br>数据类型：integer；允许值：任意正整数；访问方式：set；默认值：**15**；单位：N/A；接口：脚本 |
| **Measurements** | 指定用于批处理估计的测量量列表。<br>数据类型：ObjectArray；允许值：一个或多个有效的 `TrackingFileSet` 对象；访问方式：set；默认值：**空列表**；单位：N/A；接口：脚本 |
| **OLSEAdditiveConstant** | 外环 sigma 编辑（OLSE）所用的加性常数。详见**备注**一节中的"外环 sigma 编辑（OLSE）的行为"。<br>数据类型：Real；允许值：任意实数；访问方式：set；默认值：**0.0**；单位：N/A；接口：脚本 |
| **OLSEInitialRMSSigma** | 外环 sigma 编辑（OLSE）所用的初始预测均方根值。<br>数据类型：Real；允许值：Real > 0.0；访问方式：set；默认值：**3000.0**；单位：无量纲；接口：脚本 |
| **OLSEMultiplicativeConstant** | 外环 sigma 编辑（OLSE）所用的乘性常数。<br>数据类型：Real；允许值：Real > 0.0；访问方式：set；默认值：**3.0**；单位：无量纲；接口：脚本 |
| **OLSEUseRMSP** | 用于指定第一次迭代之后各次迭代的外环 sigma 编辑（OLSE）所用编辑算法的标志。详见**备注**一节中的"外环 sigma 编辑（OLSE）的行为"。<br>数据类型：true/false；允许值：true 或 false；访问方式：set；默认值：**true**；单位：无量纲；接口：脚本 |
| **Propagator** | 批处理估计中用于推动航天器随时间前进的 `Propagator` 对象。对于使用多艘航天器的估计运行，可以使用单独的 `Propagator` 字段为估计器配置中的每艘航天器指定积分器，如下所述。另见本节末尾的示例。<br>数据类型：Object；允许值：有效的 `Propagator` 对象，可选地后跟一组有效的 `Spacecraft` 对象，即 *Propagator* 或 *{Propagator, Spacecraft[, Spacecraft2, Spacecraft3, ...]}*；访问方式：set；默认值：**None**；单位：N/A；接口：脚本 |
| **RelativeTol** | 相对加权 RMS 收敛准则容差。<br>数据类型：Real；允许值：Real > 0；访问方式：set；默认值：**0.0001**；单位：无量纲；接口：脚本 |
| **ReportFile** | 指定估计报告文件的名称。<br>数据类型：String；允许值：包含有效文件名的字符串；访问方式：set；默认值：**'BatchEstimator' + 实例名 + '.data'**；单位：N/A；接口：脚本 |
| **ReportStyle** | 指定估计报告的类型。`Normal` 样式不包含观测 TAI、偏导数和频率信息的报告。选择 `Verbose` 模式要求用户在 GMAT 启动文件中设置 RUN_MODE = Testing。<br>数据类型：String；允许值：Normal、Verbose；访问方式：set；默认值：**Normal**；单位：N/A；接口：脚本 |
| **ResetBestRMSIfDiverging** | 若设为 true 且估计过程已发散，则将 Best RMS 重置为当前 RMS。<br>数据类型：true/false；允许值：true 或 false；访问方式：set；默认值：**false**；单位：N/A；接口：脚本 |
| **ShowAllResiduals** | 允许显示残差图。<br>数据类型：On/Off；允许值：On 或 Off；访问方式：set；默认值：**On**；单位：N/A；接口：脚本 |
| **ShowProgress** | 允许在消息窗口中显示批处理估计器的详细输出。<br>数据类型：true/false；允许值：true 或 false；访问方式：set；默认值：**true**；单位：N/A；接口：脚本 |
| **UseInitialCovariance** | 若设为 true，则将*先验*误差协方差项加入估计代价函数。当使用已应用的 `Spacecraft.OrbitErrorCovariance`、`Spacecraft.CdSigma`、`Spacecraft.CrSigma` 或 `ErrorModel.BiasSigma` 进行估计时，此选项应设为 true。使用此字段的一些限制见下文**备注**一节。<br>数据类型：true/false；允许值：true 或 false；访问方式：set；默认值：**false**；单位：N/A；接口：脚本 |
| **UseInnerLoopEditing** | 若设为 true，则启用迭代残差编辑过程，以剔除预测在未来迭代中会被 sigma 编辑的测量。详见**备注**一节中的"内环 sigma 编辑（ILSE）的行为"。<br>数据类型：true/false；允许值：true 或 false；访问方式：set；默认值：**false**；单位：N/A；接口：脚本 |

## 备注

> **注意**：为批处理估计器配置数值积分器时，必须使用定步长选项。`BatchEstimator` 所用的 `ForceModel` 的 `ErrorControl` 参数必须设为 `None`。当然，使用定步长控制时，用户必须选择合适的步长，使其对所选轨道类型和力模型剖面达到所需精度。定步长积分的步长在 `Propagator.InitialStepSize` 和 `Propagator.MaxStep` 字段上配置。这两个参数所赋的较小值将作为积分步长。通常将两者设为相同值较为方便，以避免混淆。

### 收敛准则的行为

GMAT 有四个输入字段 `RelativeTol`、`AbsoluteTol`、`MaximumIterations` 和 `MaxConsecutiveDivergences`，用于在每次新迭代后确定估计器是否已收敛。与这些输入字段相关的是以下两个收敛检验：

**绝对加权 RMS 收敛准则**

　　当前加权 RMS <= AbsoluteTol

**相对加权均方根（RMS）收敛准则**

　　|RMSP − RMSB| / RMSB <= RelativeTol

其中：

　　RMSB = 当前及之前各次迭代中取得的最小加权 RMS

　　RMSP = 下一次迭代的预测加权 RMS

当上述两个准则之一或两者在不超过 `MaximumIterations` 次迭代内满足时，认为批处理估计已收敛。

当连续发散迭代次数等于或大于 `MaxConsecutiveDivergences`，或迭代次数超过 `MaximumIterations` 时，认为批处理估计已发散。

### 外环 sigma 编辑（OLSE）的行为

GMAT 有四个输入字段 `OLSEMultiplicativeConstant`、`OLSEAdditiveConstant`、`OLSEUseRMSP` 和 `OLSEInitialRMSSigma`，用于"编辑"（即剔除或丢弃）坏测量数据。此编辑过程按迭代逐次进行。被编辑的数据不用于计算当前迭代的状态向量估计，但该数据可作为后续迭代的候选测量。在第一次外环迭代中，满足以下条件的数据被编辑：

　　|加权测量残差| > `OLSEInitialRMSSigma`

其中，单个给定测量的加权测量残差由下式给出：

　　(O−C) / `NoiseSigma`

其中 `NoiseSigma` 是与给定测量关联的测量类型的输入噪声（1 sigma）。在后续外环迭代中，满足以下条件的数据被编辑：

　　|加权测量残差| > `OLSEMultiplicativeConstant` * RMS + `OLSEAdditiveConstant`

上述编辑算法取决于用户输入的 `OLSEUseRMSP` 值。若 `OLSEUseRMSP` = True，则 RMS = `WRMSP`，其中 `WRMSP` 是上一次迭代结束时计算的预测加权 RMS。否则，若 `OLSEUseRMSP` = False，则 RMS = `WRMS`，其中 `WRMS` 是上一次迭代结束时计算的实际加权 RMS。

在许多情况下，特别是初始状态估计较差时，预测的 WRMS 可能过小，在编辑过程中使用预测 WRMS 可能导致后续迭代中过度的数据剔除。如果您因第二次或以后迭代中过度的数据编辑而遇到收敛困难，请尝试将 `OLSEUseRMSP` 设为 False。

### 内环 sigma 编辑（ILSE）的行为

内环启用时，在每次外环迭代计算出要编辑哪些测量之后立即运行。内环的好处在于它可以快速迭代，因为不需要在每次迭代中推进航天器。它利用测量导数计算下一次外环迭代残差的线性化近似。这通常会增加运行中被 sigma 编辑的数据量，但结果是：在许多情况下，解收敛所需的外环迭代次数更少，因此总体上可能运行得更快。

GMAT 有三个输入字段 `ILSEMaximumIterations`、`ILSEMultiplicativeConstant` 和 `UseInnerLoopEditing`，供内环预测哪些测量将被随后的外环迭代 sigma 编辑。在每次内环迭代中，满足以下条件的数据被编辑：

　　|预测加权测量残差| > `ILSEMultiplicativeConstant` * WRMSP

其中 WRMSP 是当前迭代残差的预测加权均方根。无论 `OLSEUseRMSP` 如何设置，内环编辑器始终使用 WRMSP 进行数据编辑。

当被编辑测量的选择与上一次内环迭代编辑的测量完全一致时，内环收敛。`ILSEMaximumIterations` 的值也提供了执行迭代次数的上界。与外环一样，被编辑的数据不用于计算当前迭代的状态向量估计，但可作为后续迭代的候选测量。内环只能从估计中移除测量，不会重新引入先前被编辑的测量。

### 冻结测量编辑的行为

GMAT 有两个输入字段 `FreezeMeasurementEditing` 和 `FreezeIteration`，用于确定是否以及何时"冻结"（即不再改变）由外环 sigma 编辑器编辑剔除的测量选择。仅当 `FreezeMeasurementEditing` 为 true 时才会发生测量编辑冻结。

如果启用冻结，被编辑测量的选择在 `FreezeIteration` 指定的迭代之后锁定。如果 `FreezeIteration` 的值为 1，估计器使用上文定义的 `OLSEInitialRMSSigma` 值来确定哪些测量用于计算第一次迭代的状态向量偏差向量。此后，由初始 RMS sigma 滤波器编辑剔除的相同测量在其余迭代中保持被编辑剔除。如果 `FreezeIteration` 的值为 2 或更大，估计器使用上文定义的外环 sigma 编辑来确定状态向量偏差向量，直到 `FreezeIteration` 指定的迭代为止；此时，凡是被外环 sigma 编辑器编辑剔除的测量，在其余迭代中都保持被编辑剔除。如果启用了内环 sigma 编辑，由内环 sigma 编辑器最后一次迭代编辑剔除的测量也将被冻结。被冻结的被编辑剔除的测量，将保留其被编辑剔除那次迭代时外环和内环 sigma 编辑器所用的编辑标志。

在解需要过多迭代才能收敛、且后续迭代仅编辑少量数据的情况下，冻结测量编辑可能很有用。如果是这种情况，在适当的迭代上启用编辑冻结通常会迫使解在到达冻结迭代后快速收敛。

### 积分器设置

`BatchEstimator` 资源有一个 `Propagator` 字段，其中包含估计过程中将使用的 `Propagator` 资源名称。积分器的最小步长 `MinStep` 应始终设为 0。

`BatchEstimator` 资源将第一个被标识的 `Propagator` 用作被仿真航天器的默认积分器。用户可以使用可选的航天器列表为特定航天器指定不同的 `Propagator`，将这些航天器分配给其他积分器组件。此用法的示例见下方示例。此能力在《Configuration of Propagators for Orbit Determination》中也有更详细的描述。

### 法矩阵降阶

如果某个估计状态不可观测（通常由于测量数据编辑），法矩阵将包含与不可观测状态对应的一行和一列零，因此是奇异的。在运行中可能发生这种情况，例如：用户尝试估计观测偏差，但与该偏差关联的所有测量都被 sigma 编辑排除在解之外。这种情况会在偏差状态的行和列上产生奇异法矩阵。然而，GMAT 不会以矩阵求逆错误终止，而是检测此状况，通过在求逆前从法矩阵中移除不可观测状态来进行补偿。求逆后将恢复该不可观测状态，以防它在后续迭代中变得可观测。当 GMAT 采取此动作时，将向 GMAT 日志文件和批处理估计器报告文件的 State Information 报告都报告一条消息，指明在求逆前从法矩阵中移除了哪个状态分量。

### UseInitialCovariance 限制

如上文字段规格所述，如果此字段设为 true，则*先验*误差协方差项被加入估计代价函数。对于当前 GMAT 版本，此字段的使用有如下限制：

1. 用户必须在 EarthMJ2000Eq 坐标系中输入*先验*轨道状态协方差。
2. 如果用户求解笛卡尔轨道状态（例如 Sat.SolveFors = {CartesianState}），则输入的*先验*轨道状态协方差必须以笛卡尔元素表示。同样，如果用户求解开普勒轨道状态（例如 Sat.SolveFors = {KeplerianState}），则输入的*先验*轨道状态协方差必须以开普勒元素表示。
3. 如果用户求解开普勒轨道状态（例如 Sat.SolveFors = {KeplerianState}），则输入的*先验*轨道状态协方差必须以航天器平近点角（MA）而非真近点角（TA）表示。更具体地说，在这种情况下，6x6 轨道状态误差协方差的对角元素为：半长轴 SMA 的方差 (km^2)、偏心率（无量纲）、倾角 INC (deg^2)、升交点赤经 RAAN (deg^2)、近地点幅角 AOP (deg^2) 和平近点角 MA (deg^2)。注意，在这种情况下，我们要求*先验*协方差以 MA 输入，尽管对于当前 GMAT 版本，相关轨道状态不能用 MA 设置。

### 批处理估计器 MATLAB 数据文件

> **注意**：MATLAB 数据文件输出已弃用，由 `DataFile` JSON 输出文件取代。希望继续使用 MATLAB 的用户可以使用以下代码示例在 MATLAB 中加载 JSON 文件。

```
str = fileread(json_file_path); 
bls_data = jsondecode(str);
```

如果已安装 MATLAB 并正确配置了与 GMAT 的接口（参见 MATLAB Interface），用户可以生成包含 `BatchEstimator` 运行有用分析数据的 mat 文件。通过在已配置的 `BatchEstimator` 资源的 `MatlabFile` 字段上指定输出文件的路径和文件名即可启用此选项。该文件包含三个顶层数据结构——`EstimationConfig`、`Iteration` 和 `Observed`。除下表注明的情况外，mat 文件中数据的单位与 BatchEstimator 输出文件相同：km、km/sec、DSN 测距单位、Hz 和度。

`EstimationConfig` 包含估计运行配置的一般信息。`EstimationConfig` 结构的内容如下表所示。

| 变量 | 描述 |
|------|------|
| CartesianStateNames | 估计参数名称；航天器元素名称为笛卡尔元素 |
| FinalEpochUTC | 1x2 列向量，第一行为 MATLAB datenum 形式的测量结束历元，第二行为 GMAT TAIModJulian 形式 |
| GravitationalParameter | 本次运行主中心天体的引力参数，单位 km^3/sec^2 |
| InitialEpochUTC | 1x2 列向量，第一行为 MATLAB datenum 形式的测量起始历元，第二行为 GMAT TAIModJulian 形式 |
| KeplerianStateNames | 估计参数名称；航天器元素名称为开普勒元素 |

`Observed` 结构包含跟踪数据观测的测量数据。`Observed` 结构的内容如下表所示。使用 mat 文件时，最好记住：GMAT 输出文件对迭代、观测和残差从 0 开始索引，而 MATLAB 从 1 开始索引。

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

`Iteration` 结构的内容如下表所示。Iteration 结构是一个数组，每个元素对应估计器执行的一次迭代。每次迭代具有以下字段。某些字段不适用于某些测量类型（例如 Elevation、Frequency 和 FrequencyBand 不适用于 GPS_PosVec 测量），并被设为 NaN 或零。

| 变量 | 描述 |
|------|------|
| CartesianCorrelation | 迭代结束时的笛卡尔相关矩阵。行和列的顺序由 EstimationConfig.CartesianStateNames 给出。 |
| CartesianCovariance | 迭代结束时的笛卡尔协方差矩阵。行和列的顺序由 EstimationConfig.CartesianStateNames 给出。 |
| CartesianState | 迭代结束时的航天器笛卡尔元素和其他估计参数。元素顺序与 EstimationConfig.CartesianStateNames 中给出的一致。 |
| Elevation | 测量历元处的计算仰角（度）。不适用于 GPS_PosVec 数据（设为 0）。 |
| IonosphericCorrection | 电离层测量修正的大小。单位与测量量相同。关于 X/Y 角度测量的介质修正，请参见下方说明。 |
| IterationNumber | 数值迭代计数编号，从 0 开始。 |
| KeplerianCorrelation | 迭代结束时的开普勒相关矩阵。行和列的顺序由 EstimationConfig.KeplerianStateNames 给出。 |
| KeplerianCovariance | 迭代结束时的开普勒协方差矩阵。行和列的顺序由 EstimationConfig.KeplerianStateNames 给出。 |
| KeplerianState | 迭代结束时的航天器开普勒元素和其他估计参数。元素顺序与 EstimationConfig.KeplerianStateNames 中给出的一致。 |
| Measurement | 计算测量量。对于 GPS_PosVec，每个单元保存一个 1x3 的 X、Y、Z 计算测量量列向量。 |
| MeasurementEditFlag | 字符串观测编辑标志。'N' 表示未编辑/被接收的观测。 |
| MeasurementNumber | 测量记录编号。 |
| MeasurementPartials | 矩阵元胞数组。每个成员是测量量对状态各元素的偏导数矩阵。偏导数针对 Spacecraft `SolveFors` 字段上选择的元素类型求取。例如，若用户选择估计 KeplerianState，则偏导数针对开普勒元素求取。元素顺序与 EstimationConfig 状态名称中给出的一致。对于 GPS_PosVec 数据，每个单元保存一个 3xN 矩阵，其中 N 为估计状态数。每行依次包含对 X、Y、Z GPS_PosVec 测量量的偏导数。 |
| PreviousCartesianState | 迭代开始时的航天器笛卡尔元素和其他估计参数。元素顺序与 EstimationConfig.CartesianStateNames 中给出的一致。 |
| PreviousKeplerianState | 迭代开始时的航天器开普勒元素和其他估计参数。元素顺序与 EstimationConfig.KeplerianStateNames 中给出的一致。 |
| Residual | 测量残差。对于 GPS_PosVec，每个单元保存一个 1x3 的 X、Y、Z 残差列向量。 |
| TroposphericCorrection | 对流层测量修正的大小。单位与测量量相同。关于 X/Y 角度测量的介质修正，请参见下方说明。 |

Iteration 和 Observations 结构中的许多字段是元胞数组。在大多数情况下，只需一些简单的 MATLAB 命令即可将元胞数组数据提取到数组中，用于绘图和分析。下面的代码展示了几个示例。

```
% We assume a BatchEstimator mat-file has already been loaded

%   Plot scalar residuals

t = Observed.EpochUTC(1,:);
y = cell2mat(Iteration(1).Residual);

plot(t, y, 'ko');
datetick;

%   Plot measurement partials

parts = Iteration(1).MeasurementPartials;
parts = cat(1, parts{:});

plot(t, parts);
datetick;

%   Compute WRMS

iter = Iteration(1);

IACC = find(strcmp(iter.MeasurementEditFlag, 'N'));

dy = cell2mat(iter.Residual(IACC));
w  = diag(cell2mat(Observed.MeasurementWeight(IACC)));
m  = length(IACC);

wrms = sqrt((1/m) * dy * w * dy');
```

**中文说明**：第一段绘制标量残差随时间变化；第二段将各测量的偏导数矩阵纵向拼接后绘制；第三段找出编辑标志为 'N'（被接收）的观测，提取其残差和权重，计算加权 RMS（WRMS）。

用户可能会发现将 ObsEditFlag 或 Type 作为 MATLAB 分类数组（categorical array）处理很有用。更多细节请参见 MATLAB 帮助中的 `categorical` 命令。

处理包含 GPS_PosVec 数据的 MATLAB 文件需要多加注意。下面展示一些示例。

```
% We assume a BatchEstimator mat-file from a GPS_PosVec data 
% run has already been loaded

%   Plot GPS_PosVec residuals

t = Observed.EpochUTC(1,:);
y = cell2mat(Iteration(2).Residual);

plot(t, y, '.');
datetick;

%   Extract partials with respect to the GPS_PosVec 
%   X-component measurement

parts = Iteration(1).MeasurementPartials;
parts = cat(3, parts{:});

part_x = parts(1,:,:);
part_x = squeeze(part_x);

plot(t, part_x);
```

**中文说明**：第一段绘制 GPS_PosVec 残差（每个观测含 X、Y、Z 三个分量）；第二段将 3xN 偏导数矩阵沿第三维拼接后，提取对 X 分量测量量的偏导数并绘图。

### 批处理估计器 JSON 数据文件

用户可以生成 JSON 格式的文件，其中包含 `BatchEstimator` 运行的有用分析数据。通过在已配置的 `BatchEstimator` 资源的 `DataFile` 字段上指定输出文件的路径和文件名即可启用此选项。此文件的内容如下表所示。

| 元素 | 描述 |
|------|------|
| CartesianStateNames | 所有估计参数的名称；航天器元素名称为笛卡尔元素 |
| EstimationEpoch | BLS 估计历元，UTCGregorian 格式 |
| InitialState | 完整的初始（先验）估计状态，单位 km 和 km/sec |
| KeplerianStateNames | 所有估计参数的名称；航天器元素名称为开普勒元素 |
| Observations | 本次运行包含的所有观测的列表；细节见下 |
| Iterations | 本次运行每次迭代的数据列表；细节见下 |

`Observations` 结构包含跟踪数据观测测量记录。`Observations` 结构的内容如下表所示。

| 元素 | 描述 |
|------|------|
| Epoch | 测量历元，UTCGregorian 格式 |
| Participants | 逗号分隔的字符串，包含测量路径中 GMAT 对象的 ID |
| Type | GMAT 观测类型名称 |
| Value | 观测测量量；对于 GPS_PosVec，每条记录有一个 X、Y、Z 测量量列表。单位如跟踪数据类型描述中所述。 |

`Iterations` 列表的内容如下表所示。估计器执行的每次迭代对应一个列表元素。每次迭代具有以下元素。

| 元素 | 描述 |
|------|------|
| CartesianCovariance | 迭代结束时的笛卡尔协方差矩阵；行和列的顺序由 CartesianStateNames 给出。 |
| CartesianState | 迭代结束时的航天器笛卡尔元素和其他估计参数；元素顺序由 CartesianStateNames 给出。 |
| ComputedMeasurements | 包含本次迭代中每个计算测量量数据的对象列表；细节见下。 |
| KeplerianCovariance | 迭代结束时的开普勒协方差矩阵；元素顺序由 KeplerianStateNames 给出。 |
| KeplerianState | 迭代结束时的航天器开普勒元素和其他估计参数；元素顺序由 KeplerianStateNames 给出。 |

ComputedMeasurements 记录的字段描述如下。计算测量量和残差的单位在跟踪数据类型描述中说明。

| 元素 | 描述 |
|------|------|
| EditFlag | 字符串观测编辑标志；值为 **null** 表示未编辑/被接收的观测。 |
| Elevation | 测量计算仰角（度）。 |
| Epoch | 残差历元，UTCGregorian 格式。 |
| Participants | 逗号分隔的字符串，包含测量路径中 GMAT 对象的 ID。 |
| Residual | 测量残差；对于 GPS_PosVec，每条记录保存一个 X、Y、Z 残差列表。单位如跟踪数据类型描述中所述。 |
| Type | GMAT 观测类型名称。 |
| Value | 计算测量量；对于 GPS_PosVec，每条记录保存一个 X、Y、Z 计算测量量列表。 |

### X/Y 角度数据的数据文件介质修正

在构建计算角度测量量时，GMAT 将电离层和对流层修正作为对地面站到航天器斜距矢量的仰角调整来应用。所有计算角度观测量随后由斜距矢量导出。此过程给出应用于仰角的精确修正，但对其他角度测量类型的修正不会被直接计算和存储。为了向用户提供 X/Y 角度这些修正的估计值，GMAT 通过另一种方法由仰角修正计算近似的 X/Y 角度修正，并存储在数据文件中。用户应注意，数据文件中存储的 X/Y 数据介质修正与构建 X/Y 计算测量量所用的方法并不完全一致。仰角大于 5 度时差异小于 1%，但仰角低于 5 度时差异可能达到 100% 量级。

### 交互关系

| 资源 | 描述 |
|------|------|
| `TrackingFileSet` 资源 | 必须创建，以便告知 `BatchEstimator` 资源将处理哪些数据 |
| `Propagator` 资源 | GMAT 用它来生成预测轨道 |
| `RunEstimator` 命令 | 必须使用 `RunEstimator` 命令来实际处理由 `BatchEstimator` 资源定义的数据 |

## 示例

下面是一个已配置的批处理估计器实例示例。在此示例中，`estData` 是一个 `TrackingFileSet` 实例，`ODProp` 是一个 `Propagator` 实例。

```
Create BatchEstimator bat;

bat.ShowProgress               = true;
bat.Measurements               = {estData} 
bat.AbsoluteTol                = 0.000001;
bat.RelativeTol                = 0.001;
bat.MaximumIterations          = 10;
bat.MaxConsecutiveDivergences  = 3;
bat.Propagator                 = ODProp;
bat.ShowAllResiduals           = On;
bat.OLSEInitialRMSSigma        = 3000;
bat.OLSEMultiplicativeConstant = 3;
bat.OLSEAdditiveConstant       = 0;
bat.UseInnerLoopEditing        = True;
bat.ILSEMaximumIterations      = 15;
bat.ILSEMultiplicativeConstant = 3;
bat.InversionAlgorithm         = 'Internal';
bat.EstimationEpochFormat      = 'FromParticipants';
bat.EstimationEpoch            = 'FromParticipants'; 
bat.ReportStyle                = 'Normal';
bat.ReportFile                 = 'BatchEstimator_Report.txt';

BeginMissionSequence;
```

**中文说明**：创建批处理估计器 bat，指定测量数据 estData 和积分器 ODProp，设置绝对/相对收敛容差、最大迭代次数、外环 sigma 编辑参数（初始 RMS sigma 3000、乘性常数 3、加性常数 0），启用内环编辑（最多 15 次迭代、乘性常数 3），法方程求逆算法为 Internal，估计历元取参与方当前历元，报告样式 Normal。

下一个示例展示如何在估计器上编写多个积分器的脚本。此示例仅说明积分器的脚本编写，不包含其他对象设置。在此示例中，TDRS 航天器使用基于星历的 SPICE 积分器进行积分。仿真器中使用的任何其他航天器使用 satprop 积分器进行积分。此示例对 TDRS6 和 TDRS10 轨道使用星历积分器，但使用带力模型的独立数值积分器时，BatchEstimator 的 Propagator 赋值语法完全相同。

```
%Create and Configure Spacecraft
Create Spacecraft SimSat;

Create Spacecraft TDRS6;
TDRS6.OrbitSpiceKernelName = {'TDRS6Ephem.bsp'};

Create Spacecraft TDRS10;
TDRS10.OrbitSpiceKernelName = {'TDRS10Ephem.bsp'};

%   Create and configure the Simulator object
Create ForceModel FM1

Create Propagator satprop;
satprop.FM = FM1
satprop.MinStep = 0

Create Propagator tdrsprop;
tdrsprop.Type = SPK
tdrsprop.EpochFormat = 'A1ModJulian';
tdrsprop.StartEpoch = 'FromSpacecraft';

Create BatchEstimator bat;
bat.Propagator          = satprop;
bat.Propagator          = {tdrsprop, TDRS6, TDRS10};
```

**中文说明**：TDRS6/TDRS10 使用 SPK 星历积分器 tdrsprop，其余航天器使用默认的 satprop 数值积分器（MinStep=0）。第一次赋值设默认积分器，第二次用花括号列表将 tdrsprop 绑定到 TDRS6 和 TDRS10。

若要查看读入测量量并运行估计器的综合示例，请参见第 14 章《Orbit Estimation using DSN Range and Doppler Data》教程。
