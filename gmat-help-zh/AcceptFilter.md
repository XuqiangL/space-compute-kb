# 接收滤波器（AcceptFilter）

> 译自 GMAT R2026a 帮助文档 AcceptFilter.html

**AcceptFilter** —— 允许选择数据子集供批处理最小二乘估计器处理。

## 描述

`AcceptFilter` 对象用于创建准则，基于观测频率、跟踪站、测量类型、记录号或时间，将可用数据的子集纳入估计过程。`AcceptFilter` 实例在 `TrackingFileSet` 或 `BatchEstimator` 对象的 `DataFilters` 字段上指定使用。

GMAT 为估计实现了两级数据编辑。第一级编辑准则在 `TrackingFileSet` 实例的 `DataFilters` 字段上指定。在这一级，用户可以选择哪些数据被准许进入提供给估计器的总体观测池。在跟踪文件集级别被排除的任何数据将被立即丢弃，不可用于估计过程。

第二级数据编辑在 `BatchEstimator` 实例的 `DataFilters` 字段上指定。在这一级，用户可以选择哪些数据用于估计状态更新。通过第一级编辑准许的任何观测都会计算残差，但在估计器级别被排除的任何数据将被标记为用户编辑（user edited），并且不影响状态改正的计算。这使用户能够根据用可信测量集计算的解，评估不可信数据的质量。

单个 `AcceptFilter` 可采用多个选择准则（例如同时按不同间隔对不同站或数据类型进行抽稀）。单个滤波器上的多个准则按"与"（AND）关系处理。当在单个滤波器上指定多个准则时，观测必须满足所有指定准则才会被接收。

可以在单个 `TrackingFileSet` 或 `BatchEstimator` 上指定多个具有不同选择准则的 `AcceptFilter`。指定多个滤波器时，它们按"或"（OR）关系处理。满足任一指定滤波器准则的数据都将被接收。

**另请参阅**：RejectFilter、TrackingFileSet、BatchEstimator

## 字段

| 字段 | 描述 |
|------|------|
| **DataTypes** | 数据类型列表。<br>数据类型：String Array；允许值：任意受支持的 GMAT 测量类型集合，或 'All'；访问方式：set；默认值：**{All}**；单位：N/A；接口：脚本 |
| **EpochFormat** | 允许用户选择历元格式。<br>数据类型：String；允许值：UTCGregorian、UTCModJulian、TAIGregorian、TAIModJulian、TTGregorian、TTModJulian、A1Gregorian、A1ModJulian、TDBGregorian、TDBModJulian；访问方式：set；默认值：**TAIModJulian**；单位：N/A；接口：脚本 |
| **FileNames** | 包含跟踪数据的文件名列表（相关 `TrackingFileSet` 的 `FileName` 字段的子集）。如果此字段等于 From_AddTrackingConfig，则发生两件事：(1) 相关 `TrackingFileSet` 中的所有文件用作起点；(2) 在所有文件的数据中，仅使用由相关 `TrackingFileSet` 的 `AddTrackingConfig` 字段定义的数据。此字段仅在 `AcceptFilter` 用于 `TrackingFileSet` 时适用。<br>数据类型：StringArray；允许值：有效文件名、'All' 或 'From_AddTrackingConfig'；访问方式：set；默认值：**{All}**；单位：N/A；接口：脚本 |
| **FinalEpoch** | 待处理所需数据的最终历元。<br>数据类型：String；允许值：任何有效历元；访问方式：set；默认值：**GMAT 中定义的最晚日期**；单位：N/A；接口：脚本 |
| **InitialEpoch** | 待处理所需数据的初始历元。<br>数据类型：String；允许值：任何有效历元；访问方式：set；默认值：**GMAT 中定义的最早日期**；单位：N/A；接口：脚本 |
| **ObservedObjects** | 用户创建的被跟踪对象列表（例如，被跟踪的 `Spacecraft` 资源名称）。<br>数据类型：Object Array；允许值：用户定义的观测对象或 'All'；访问方式：set；默认值：**{All}**；单位：N/A；接口：脚本 |
| **RecordNumbers** | 要接收的一个或多个记录号或记录号区间的列表。观测记录号在 GMAT 估计器输出文件中报告。此字段仅在 `AcceptFilter` 用于估计器级别时适用。<br>数据类型：String array；允许值：整数或整数区间（见示例）；访问方式：set；默认值：**{All}**；单位：N/A；接口：脚本 |
| **ThinMode** | 'Frequency' 表示记录计数频率模式，'Time' 表示时间间隔模式。此字段仅在 `AcceptFilter` 用于 `TrackingFileSet` 时适用。<br>数据类型：String；允许值：'Frequency' 或 'Time'；访问方式：set；默认值：**Frequency**；单位：N/A；接口：脚本 |
| **ThinningFrequency** | 若 `ThinMode` 为 Frequency，整数 'n' 用于指定每第 n 个数据点被接收。例如，3 表示每第三个满足所有接收准则的数据点被接收，1 表示每个满足所有接收准则的数据点都被接收。若 `ThinMode` 为 Time，整数 'n' 为接收观测之间的秒数，以第一个可用观测作为锚点历元。例如，值 300 表示从第一个可用观测开始，每 300 秒接收一次观测。此字段仅在 `AcceptFilter` 用于 `TrackingFileSet` 时适用。<br>数据类型：Integer；允许值：正整数；访问方式：set；默认值：**1**；单位：取决于 `ThinMode` 值；接口：脚本 |
| **Trackers** | 用户创建的跟踪站列表（例如，所用的 `GroundStation` 资源名称）。<br>数据类型：Object Array；允许值：任何有效的用户创建 Tracker 对象（如 `GroundStation`）或 'All'；访问方式：set；默认值：**{All}**；单位：N/A；接口：脚本 |

## 备注

`AcceptFilter` 的某些字段在第一级（跟踪文件集）或第二级（估计器）编辑阶段不适用。`RecordNumbers` 字段在应用于跟踪文件集级别的接收滤波器时无作用。`FileNames`、`ThinningFrequency` 和 `ThinMode` 字段在应用于估计器级别的接收滤波器时无作用。

允许在两个级别上组合使用 `AcceptFilter` 和 `RejectFilter` 实例。

## 示例

### 第一级（TrackingFileSet）数据编辑

以下示例说明使用 `AcceptFilter` 进行第一级数据编辑。在这一级，`AcceptFilter` 实例应指定给 `TrackingFileSet` 的 `DataFilters` 字段。在这些示例中，只有满足接收滤波器指定准则的数据才会被准许通过，所有其他数据将被立即丢弃。

此示例展示如何创建一个 `AcceptFilter`，以 1:10 的频率对数据抽样（将数据抽稀至其数量的十分之一）。

```
Create AcceptFilter af;
  
af.ThinningFrequency = 10;

Create TrackingFileSet estData;

estData.DataFilters = {af};

BeginMissionSequence;
```

**中文说明**：创建接收滤波器 af，设置抽稀频率为 10（每 10 个点接收 1 个），并将其指定给跟踪文件集 estData 的 DataFilters。

下一个示例将接收来自 GDS 站的所有数据，并接收来自 CAN 站的每第 5 个观测。只有来自 GDS 和 CAN 站的数据会被接收。

```
Create AcceptFilter af1;
Create AcceptFilter af2;
 
Create GroundStation GDS CAN;

af1.Trackers          = {'GDS'}; 
af2.Trackers          = {'CAN'};
af2.ThinningFrequency = 5;
 
Create TrackingFileSet estData;
 
estData.DataFilters = {af1, af2};

BeginMissionSequence;
```

**中文说明**：两个滤波器按"或"关系组合：af1 接收 GDS 站全部数据，af2 接收 CAN 站每第 5 个观测。

最后一个示例说明按时间间隔抽稀数据，使用 300 秒抽稀间隔。

```
Create AcceptFilter saf;
 
af.ThinMode          = 'Time'; 
af.ThinningFrequency = 300;
 
Create TrackingFileSet estData;
 
estData.DataFilters = {af};

BeginMissionSequence;
```

**中文说明**：将抽稀模式设为 'Time'，抽稀频率 300 表示每 300 秒接收一个观测（以首个可用观测为锚点）。注意：原文脚本中创建的对象名为 saf 而后续引用为 af，存在笔误，实际使用时两者应一致。

### 第二级（估计器）数据编辑

以下示例说明使用 `AcceptFilter` 进行第二级数据编辑。在这一级，`AcceptFilter` 实例应指定给 `BatchEstimator` 的 `DataFilters` 字段。在这些示例中，只有满足接收滤波器指定准则的数据才会用于估计状态更新。所有可用数据（第一级准许的所有数据）都会计算残差，但在估计器级别未被接收的数据将被标记为用户编辑。

此示例展示如何创建 `AcceptFilter`，按记录号接收特定数据记录。

```
Create AcceptFilter af;
  
af.RecordNumbers = {10, 11, 20-150, 155-300};

Create BatchEstimator bls;

bls.DataFilters = {af};

BeginMissionSequence;
```

**中文说明**：接收记录号为 10、11、20 至 150、155 至 300 的观测记录，用于批处理估计器 bls 的状态更新。

下一个示例将仅接收 MAD 站在 10 Jun 2012 02:56 至 13:59 时间段内的测距数据。

```
Create AcceptFilter af;
Create GroundStation MAD;

af.Trackers     = {'MAD'};
af.DataTypes    = {'Range'};
af.EpochFormat  = UTCGregorian;
af.InitialEpoch = '10 Jun 2012 02:56:00.000';
af.FinalEpoch   = '10 Jun 2012 13:59:00.000';

Create BatchEstimator bls;

bls.DataFilters = {af};

BeginMissionSequence;
```

**中文说明**：单个滤波器上的多个准则按"与"关系组合：必须同时满足站为 MAD、数据类型为 Range、历元在指定区间内，观测才会被接收。

最后一个示例说明接收 MAD 站的所有数据，以及 CAN 站的仅测距数据。

```
Create AcceptFilter af1 af2;
Create GroundStation MAD CAN;
 
af1.Trackers         = {'MAD'}; 
af2.Trackers         = {'CAN'};
af2.DataTypes        = {'Range'};
 
Create BatchEstimator bls;
 
bls.DataFilters = {af1, af2};

BeginMissionSequence;
```

**中文说明**：af1 接收 MAD 站全部数据，af2 接收 CAN 站的测距数据；两个滤波器按"或"关系组合。
