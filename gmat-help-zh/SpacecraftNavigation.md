# 航天器导航（Spacecraft Navigation）
> 译自 GMAT R2026a 帮助文档 SpacecraftNavigation.html

**Spacecraft Navigation —— 航天器（Spacecraft）上有多个字段专门用于支持 GMAT 的导航（轨道确定）能力**

## 描述

使用 GMAT 的导航（navigation，即轨道确定 orbit determination）功能时，某些航天器参数可以被估计，即作为"待解参数"（solve-for）。如"航天器弹道/质量特性（Spacecraft Ballistic/Mass Properties）"一节所述，航天器的弹道与质量特性包括反射系数 `Cr` 和阻力系数 `Cd`。作为 GMAT 导航能力的一部分，GMAT 可以接入测量数据并估计（"解算"）`CartesianState`（笛卡尔状态）或 `KeplerianState`（开普勒状态），以及一组相关的力模型参数。完整的待估参数列表见下文 `SolveFors` 参数。

**另请参阅**：`BatchEstimator`（批处理估计器）

## 字段

### AddHardware

挂接到 `Spacecraft` 上的 `Antenna`（天线）、`Transmitter`（发射机）、`Receiver`（接收机）和 `Transponder`（应答机）对象列表。

- 数据类型：`Antenna`、`Transmitter`、`Receiver` 或 `Transponder` 对象
- 允许值：任何用户定义的 `Antenna`、`Transmitter`、`Receiver` 或 `Transponder` 对象
- 访问权限：仅可设置（set）
- 默认值：None
- 单位：N/A
- 接口：脚本

### AtmosDensityScaleFactorSigma

大气密度比例因子 `AtmosDensityScaleFactor` 的标准差（standard deviation）。对于批处理估计器，仅当 `BatchEstimator` 资源的 `UseInitialCovariance` 字段设为 True 且 `AtmosDensityScaleFactor` 被估计时，才使用此字段。

- 数据类型：实数（Real）
- 允许值：Real > 0
- 访问权限：仅可设置（set）
- 默认值：1.0E+70
- 单位：无量纲（dimensionless）
- 接口：脚本

### CdSigma

阻力系数 `Cd` 的标准差。对于批处理估计器，仅当 `BatchEstimator` 资源的 `UseInitialCovariance` 字段设为 True 且 `Cd` 被估计时，才使用此字段。

- 数据类型：实数（Real）
- 允许值：Real > 0
- 访问权限：仅可设置（set）
- 默认值：1.0E+70
- 单位：无量纲（dimensionless）
- 接口：脚本

### CrSigma

反射系数 `Cr` 的标准差。对于批处理估计器，仅当 `BatchEstimator` 资源的 `UseInitialCovariance` 字段设为 True 且 `Cr` 被估计时，才使用此字段。

- 数据类型：实数（Real）
- 允许值：Real > 0
- 访问权限：仅可设置（set）
- 默认值：1.0E+70
- 单位：无量纲（dimensionless）
- 接口：脚本

### Id

GMD 跟踪数据文件中使用的航天器 Id。该值必须与 GMD 跟踪数据记录中出现的航天器 ID 一致。一般情况下允许任意值，但关于 TDRS 航天器 ID 的重要规则请参阅下文备注。

- 数据类型：字符串（String）
- 允许值：String
- 访问权限：仅可设置（set）
- 默认值：SatId
- 单位：N/A
- 接口：脚本

### OrbitErrorCovariance

状态 6x6 误差协方差矩阵。如果估计 `CartesianState`，则必须是笛卡尔协方差；如果估计 `KeplerianState`，则必须是开普勒协方差。无论航天器坐标系如何选择，协方差都必须在 EarthMJ2000Eq 坐标系中指定。

对于批处理估计器，仅当 `BatchEstimator` 资源的 `UseInitialCovariance` 设为 True 时才使用此字段。

对于扩展卡尔曼滤波（Extended Kalman Filter），此字段在冷启动（cold-start）模式下设置航天器初始协方差；在暖启动（warm-start）模式下运行时，扩展卡尔曼滤波会忽略此字段。

对于 `Propagate` 命令，协方差可以在任何以 MJ2000Eq 轴定义的坐标系中指定，其中将包含传播后的笛卡尔协方差。协方差也可以使用语法 **Spacecraft.CoordinateSystem.OrbitErrorCovariance** 在用户定义的坐标系（包括非 MJ2000Eq 系统）中输出。

- 数据类型：实数矩阵（Real Matrix）
- 允许值：6x6 正定对称 `Array`（数组）
- 访问权限：set、get
- 默认值：所有对角线元素均为 1e70 的 6x6 对角矩阵
- 单位：对于笛卡尔元素：位置以 km、速度以 km/s 表示的协方差矩阵（因此前三个对角元素单位为 km^2，后三个对角元素单位为 (km/s)^2）。对于开普勒元素：以 km 和度表示的协方差矩阵（例如，矩阵的 SMA 元素单位为 km^2，INC 元素单位为 deg^2）。开普勒元素的顺序为 (SMA, ECC, INC, RAAN, AOP, MA)。其他说明见"备注"一节。
- 接口：脚本

### ProcessNoiseModel

`ProcessNoiseModel`（过程噪声模型）的一个实例。`ExtendedKalmanFilter` 以及 `Propagate` 命令的 `Covariance` 选项使用它来计入一般的力建模误差。

- 数据类型：资源（Resource）
- 允许值：任何用户定义的 `ProcessNoiseModel` 资源
- 访问权限：仅可设置（set）
- 默认值：None
- 单位：N/A
- 接口：脚本

### SolveFors

待解算字段的列表。该列表必须至少包含 `CartesianState` 或 `KeplerianState` 之一（但不能同时包含两者）。例如，`Cr` 不能是唯一被解算的参数。

使用批处理估计器时，不能同时估计 `Cd` 和 `AtmosDensityScaleFactor`，因为它们是线性相关的参数。在扩展卡尔曼滤波中，可以将它们配置为单独的 `EstimatedParameter` 资源来实现同时估计。

`ExtendedKalmanFilter` 估计器目前不支持对开普勒元素（KeplerianElements）的估计。

- 数据类型：字符串数组（StringArray）
- 允许值：`CartesianState`、`KeplerianState`（仅 BatchEstimator）、`Cr`、`Cd`、`SPADDragScaleFactor`、`SPADSRPScaleFactor`、`AtmosDensityScaleFactor`
- 访问权限：仅可设置（set）
- 默认值：None
- 单位：N/A
- 接口：脚本

### SPADDragScaleFactorSigma

SPAD 阻力比例因子（SPAD drag scale factor）的标准差。对于批处理估计器，仅当 `BatchEstimator` 资源的 `UseInitialCovariance` 字段设为 True 且 `SPADDragScaleFactor` 被估计时，才使用此字段。

- 数据类型：实数（Real）
- 允许值：Real > 0
- 访问权限：仅可设置（set）
- 默认值：1.0E+70
- 单位：无量纲（dimensionless）
- 接口：脚本

### SPADSRPScaleFactorSigma

SPAD 光压（SRP）比例因子的标准差。对于批处理估计器，仅当 `BatchEstimator` 资源的 `UseInitialCovariance` 字段设为 True 且 `SPADSRPScaleFactor` 被估计时，才使用此字段。

- 数据类型：实数（Real）
- 允许值：Real > 0
- 访问权限：仅可设置（set）
- 默认值：1.0E+70
- 单位：无量纲（dimensionless）
- 接口：脚本

## 备注

估计 `CartesianState` 时，输入的 `OrbitErrorCovariance` 矩阵必须表示笛卡尔协方差；估计 `KeplerianState` 时，`OrbitErrorCovariance` 必须表示开普勒协方差。注意，开普勒协方差输入使用平近点角（Mean Anomaly，MA）而不是真近点角（True Anomaly，TA）。GMAT 当前版本仅支持使用 TA 输入开普勒轨道元素，不允许显式设置初始 MA。估计完成后，`OrbitErrorCovariance` 会更新为估计所得协方差矩阵的值。

更多细节请参阅 Batch Estimator 资源中的"UseInitialCovariance Restrictions（UseInitialCovariance 限制）"一节。

### 跟踪与数据中继卫星系统（TDRSS）航天器 Id 规则

TDRSS 测量模型中的某些常数取决于用户服务（SA1、SA2 或 MA）和 TDRS 航天器 ID。用户服务在 GMD 文件跟踪数据记录中明确给出。GMAT 会尝试从 `Spacecraft` 资源的 `Id` 参数确定 TDRS 航天器 ID。为使 TDRS 测量在所有情况下都能正常工作，为 TDRS 航天器指定 `Spacecraft.Id` 参数时，用户必须遵守以下约定之一：

- 用户可以将 TDRS SIC 指定为 TDRS 航天器 Id。GMAT 将从相应的 TDRS 航天器 SIC 推断出 TDRS ID。
- 或者，用户可以按照 "`<字符串><nn>`" 的格式指定 TDRS `Spacecraft.Id`，其中 `<nn>` 是一位或两位数字，表示 TDRS ID。`<字符串>` 部分可以是任意字符串。例如，将航天器 `Id` 参数设置为 "TDRS09"、"TD09" 或 "TDRS9"，都能正确地将航天器标识为 TDRS-9（TDRS ID = 9）。

不遵守上述约定之一，可能导致某些多普勒（Doppler）测量计算错误。如果 GMAT 无法从航天器 `Id` 参数确定 TDRS ID，将在日志文件中发出警告消息。

## 示例

解算 `Cr` 和航天器笛卡尔状态。

```
Create Spacecraft Sat
Create BatchEstimator bat
Sat.SolveFors = {CartesianState, Cr}
%User must create a TrackingFileSet
%and set up bat appropriately

BeginMissionSequence
RunEstimator bat
```

**中文说明**：创建航天器 `Sat` 和批处理估计器 `bat`，将 `SolveFors` 设为 `{CartesianState, Cr}`，即同时解算笛卡尔状态与反射系数；用户还需创建 `TrackingFileSet` 并正确配置 `bat`，最后执行 `RunEstimator`。

解算 `Cd` 和航天器笛卡尔状态，假设先验（a priori）信息已包含在估计状态向量中。

```
Create Spacecraft Sat
Sat.SolveFors = {CartesianState, Cd}

Create BatchEstimator bat
bat.UseInitialCovariance= True  
%User must create a TrackingFileSet
%and set up bat appropriately

Create Array Initial_6x6_covariance[6,6]

BeginMissionSequence
Initial_6x6_covariance = ...
       diag([1e-6 1e70 1e70 1e70 1e70 1e70]) %X pos known very well
Sat.OrbitErrorCovariance = Initial_6x6_covariance
Sat.CrSigma = 1e-6   %Cr known very well

RunEstimator bat
```

**中文说明**：该示例将 `UseInitialCovariance` 设为 True 以启用初始协方差；构造 6x6 对角矩阵作为初始轨道误差协方差（X 位置方差取 1e-6 表示已知得很精确，其余取 1e70 表示几乎未知），并设 `CrSigma = 1e-6` 表示 Cr 已知得很精确，最后运行估计器。