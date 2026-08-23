# 剔除滤波器（RejectFilter）

> 译自 GMAT R2026a 帮助文档 RejectFilter.html

**RejectFilter** —— 允许选择数据子集，使其不被批处理最小二乘估计器处理。

## 描述

`RejectFilter` 对象用于创建准则，基于跟踪站、观测对象、测量类型或时间，在估计过程中排除可用数据的子集。`RejectFilter` 实例在 `TrackingFileSet` 或 `BatchEstimator` 对象的 `DataFilters` 字段上指定使用。

GMAT 为估计实现了两级数据编辑。第一级编辑准则在 `TrackingFileSet` 实例的 `DataFilters` 字段上指定。在这一级，用户可以选择哪些数据被准许进入提供给估计器的总体观测池。在跟踪文件集级别被排除的任何数据将被立即丢弃，不可用于估计过程。

第二级数据编辑在 `BatchEstimator` 实例的 `DataFilters` 字段上指定。在这一级，用户可以选择哪些数据用于估计状态更新。通过第一级编辑准许的任何观测都会计算残差，但在估计器级别被排除的任何数据将被标记为用户编辑（user edited），并且不影响状态改正的计算。这使用户能够根据用可信测量集计算的解，评估不可信数据的质量。

单个剔除滤波器可采用多个选择准则（例如同时按时间和跟踪站抽稀）。单个滤波器上的多个准则按"与"（AND）关系处理。当在单个滤波器中指定多个准则时，观测必须满足所有指定准则才会被剔除。可以在单个 `TrackingFileSet` 或 `BatchEstimator` 上指定多个具有不同选择准则的滤波器。指定多个滤波器时，它们按"或"（OR）关系处理。满足任一指定滤波器准则的数据都将被剔除。

**另请参阅**：AcceptFilter、TrackingFileSet、BatchEstimator

## 字段

| 字段 | 描述 |
|------|------|
| **DataTypes** | 数据类型列表。<br>数据类型：String Array；允许值：任意受支持的 GMAT 测量类型集合，或 'All'；访问方式：set；默认值：**{All}**；单位：N/A；接口：脚本 |
| **EpochFormat** | 允许用户选择历元格式。<br>数据类型：String；允许值：UTCGregorian、UTCModJulian、TAIGregorian、TAIModJulian、TTGregorian、TTModJulian、A1Gregorian、A1ModJulian、TDBGregorian、TDBModJulian；访问方式：set；默认值：**TAIModJulian**；单位：N/A；接口：脚本 |
| **FileNames** | 包含要从处理中排除的跟踪数据的文件名列表（相关 `TrackingFileSet` 的 `FileName` 字段的子集）。此字段仅在 `RejectFilter` 用于 `TrackingFileSet` 时适用。<br>数据类型：StringArray；允许值：有效文件名或 'All'；访问方式：set；默认值：**{All}**；单位：N/A；接口：脚本 |
| **FinalEpoch** | 待处理所需数据的最终历元。<br>数据类型：String；允许值：任何有效历元；访问方式：set；默认值：**GMAT 中定义的最晚日期**；单位：N/A；接口：脚本 |
| **InitialEpoch** | 待处理所需数据的初始历元。<br>数据类型：String；允许值：任何有效历元；访问方式：set；默认值：**GMAT 中定义的最早日期**；单位：N/A；接口：脚本 |
| **ObservedObjects** | 用户创建的被跟踪对象列表（例如，被跟踪的 `Spacecraft` 资源名称）。<br>数据类型：Object Array；允许值：用户定义的观测对象或 'All'；访问方式：set；默认值：**{All}**；单位：N/A；接口：脚本 |
| **RecordNumbers** | 要剔除的一个或多个记录号或记录号区间的列表。观测记录号在 GMAT 估计器输出文件中报告。此字段仅在 `RejectFilter` 用于估计器级别时适用。<br>数据类型：String array；允许值：整数或整数区间（见示例）；访问方式：set；默认值：**{}**；单位：N/A；接口：脚本 |
| **Trackers** | 用户创建的跟踪站列表（例如，所用的 `GroundStation` 资源名称）。<br>数据类型：Object Array；允许值：任何有效的用户创建 Tracker 对象（如 `GroundStation`）或 'All'；访问方式：set；默认值：**{All}**；单位：N/A；接口：脚本 |

## 备注

`RejectFilter` 的某些字段在第一级（跟踪文件集）或第二级（估计器）编辑阶段不适用。`RecordNumbers` 字段在应用于跟踪文件集级别的剔除滤波器时无作用。`FileNames` 字段在应用于估计器级别的剔除滤波器时无作用。

允许在两个级别上组合使用 `AcceptFilter` 和 `RejectFilter` 实例。

## 示例

### 第一级（TrackingFileSet）数据编辑

以下示例说明使用 `RejectFilter` 进行第一级数据编辑。在这一级，`RejectFilter` 实例应指定给 `TrackingFileSet` 的 `DataFilters` 字段。在这些示例中，满足剔除滤波器指定准则的数据将被立即丢弃，所有其他数据被准许进入。

此示例展示如何创建一个 `RejectFilter`，剔除来自 GDS 站的所有观测。

```
Create GroundStation GDS;
Create RejectFilter rf;

rf.Trackers = {'GDS'};
 
Create TrackingFileSet estData;
 
estData.DataFilters = {rf};

BeginMissionSequence;
```

**中文说明**：创建剔除滤波器 rf，指定剔除 GDS 站的数据，并将其指定给跟踪文件集 estData 的 DataFilters。

下一个示例将剔除来自 GDS 站的所有 DSN 多普勒（即 DSN_TCP）跟踪测量，以及来自 CAN 站的任何类型的所有跟踪数据。所有其他跟踪测量将被接收。

```
Create GroundStation GDS CAN;

Create RejectFilter rf1;
Create RejectFilter rf2;
 
rf1.Trackers  = {'GDS'}; 
rf1.DataTypes = {'DSN_TCP'};
rf2.Trackers  = {'CAN'};
 
Create TrackingFileSet estData;
 
estData.DataFilters = {rf1, rf2};

BeginMissionSequence;
```

**中文说明**：rf1 剔除 GDS 站的 DSN_TCP 数据（站内多准则为"与"关系），rf2 剔除 CAN 站全部数据；两个滤波器按"或"关系组合。

### 第二级（估计器）数据编辑

以下示例说明使用 `RejectFilter` 进行第二级数据编辑。在这一级，`RejectFilter` 实例应指定给 `BatchEstimator` 的 `DataFilters` 字段。在这些示例中，满足剔除滤波器指定准则的数据将被排除在估计状态更新之外。所有可用数据（第一级准许的所有数据）都会计算残差，但在估计器级别被剔除的数据将被标记为用户编辑。

此示例展示如何创建 `RejectFilter`，按记录号剔除特定观测。

```
Create RejectFilter rf;

rf.RecordNumbers = {13, 25, 75-87};
 
Create BatchEstimator bls;
 
bls.DataFilters = {rf};

BeginMissionSequence;
```

**中文说明**：剔除记录号为 13、25 以及 75 至 87 的观测记录。

下一个示例展示如何同时使用多个剔除滤波器。在此示例中：

- MAD 站在 10 Jun 2012 02:56 至 13:59 弧段内的测距数据被剔除
- 所有 CAN 站的 DSN_TCP 数据被剔除
- 所有 RangeRate 数据（来自任何站）被剔除

```
Create RejectFilter rf1 rf2 rf3;
Create GroundStation MAD CAN;

rf1.Trackers     = {'MAD'};
rf1.DataTypes    = {'Range'};
rf1.EpochFormat  = UTCGregorian;
rf1.InitialEpoch = '10 Jun 2012 02:56:00.000';
rf1.FinalEpoch   = '10 Jun 2012 13:59:00.000';

rf2.Trackers     = {'CAN'};
rf2.DataTypes    = {'DSN_TCP'};

rf3.DataTypes    = {'RangeRate'};

Create BatchEstimator bls;

bls.DataFilters = {rf1, rf2, rf3};

BeginMissionSequence;
```

**中文说明**：rf1 按"站=MAD 且类型=Range 且历元在区间内"（与关系）剔除；rf2 剔除 CAN 站 DSN_TCP；rf3 剔除所有站的 RangeRate；三个滤波器按"或"关系组合。
