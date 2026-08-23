# 误差模型（ErrorModel）

> 译自 GMAT R2026a 帮助文档 ErrorModel.html

**ErrorModel** —— 用于为仿真和估计指定测量噪声，并应用或估计测量偏差。

## 描述

`ErrorModel` 在 `GroundStation` 实例或星载 `Receiver` 的 `ErrorModels` 字段上指定，用于对偏差和噪声建模，并可选择对地面站或接收机提供的每种测量类型的偏差进行估计。每个跟踪站或接收机使用的每种数据类型都必须指定一个误差模型，但同一个 `ErrorModel` 实例可被多个地面站或航天器接收机使用。

仅当使用 `GPS_PosVec` 数据时，误差模型才指定给接收机。`GPS_PosVec` 观测类型对星载 GPS 接收机提供的位置估计进行建模。由于此类数据并非源自地面站测量建模，`GPS_PosVec` 数据的误差模型改为在 `Receiver` 资源的 `ErrorModels` 字段上指定。该接收机必须挂载到相应的 `Spacecraft` 对象上。所有其他观测类型的误差模型应在相关地面站资源的 `ErrorModels` 字段上指定。误差模型不能指定给挂载在地面站上的接收机。

`ErrorModel` 同时被仿真器和估计器使用。对于数据仿真运行，`ErrorModel` 指定生成仿真测量量时采用的测量类型和噪声，并可选择对仿真观测施加偏差。

对于估计运行，`ErrorModel` 指定观测类型、假定的观测噪声以及可选的施加于观测的偏差。通过向 `ErrorModel.SolveFors` 列表添加 `Bias` 或 `PassBiases` 关键字，还可以估计观测偏差。关于 `Bias` 与 `PassBiases` 估计的区别，请参见下文备注。如果 `SolveFors` 列表为空，则不估计任何偏差。仿真器忽略 `SolveFors` 列表。

> **注意**：在仿真和估计中，接收站的误差模型决定测量特性（偏差和噪声），发射站的误差模型特性被忽略。

`ErrorModel` 资源目前不支持对 `GPS_PosVec` 数据类型应用或估计偏差。

**另请参阅**：GroundStation、Receiver、Tracking Data Types for Orbit Determination

## 字段

| 字段 | 描述 |
|------|------|
| **Bias** | 与测量量相关的常值偏差。仿真时，此偏差被加到测量量上。如下文所示，所用单位取决于测量类型 `ErrorModel.Type`。<br>数据类型：Real；允许值：任意实数；访问方式：set；默认值：**0.0**；单位：见备注一节；接口：脚本 |
| **BiasSigma** | `Bias` 的标准差。此字段用于约束 `Bias` 的估计值，仅在以下两个条件同时满足时才起作用：(1) `BatchEstimator.UseInitialCovariance = True`，且 (2) `Bias` 是求解参数。如下文所示，所用单位取决于测量类型 `ErrorModel.Type`。此参数对 `GPS_PosVec` 数据未实现。<br>数据类型：Real；允许值：Real > 0；访问方式：set；默认值：**1e+70**；单位：见备注一节；接口：脚本 |
| **NoiseSigma** | 高斯噪声的 1-sigma 值。仿真时，若 `Sim.AddNoise = True`，此噪声被加到测量量上。估计时，此值作为批处理算法的一部分，用于计算测量类型权重。如下文所示，所用单位取决于测量类型 `ErrorModel.Type`。<br>数据类型：Real；允许值：Real > 0；访问方式：set；默认值：**103**；单位：见备注一节；接口：脚本 |
| **SolveFors** | 待估计参数的列表。用户可以为此 ErrorModel 的任何使用站在整个弧段上估计单个偏差，也可以估计"逐弧圈（pass-by-pass）"偏差。有关 PassBiases 选项的更多细节，请参见下文备注。`SolveFors` 选项对 `GPS_PosVec` 数据未实现。<br>数据类型：StringArray；允许值：{}、{Bias} 或 {PassBiases}；访问方式：set；默认值：**{}**；单位：N/A；接口：脚本 |
| **Type** | 测量数据类型。<br>数据类型：枚举；允许值：任何受支持的测量类型名称，参见《Tracking Data Types for Orbit Determination》；访问方式：set；默认值：**DSN_SeqRange**；单位：N/A；接口：脚本 |

## 备注

### Bias、BiasSigma 和 NoiseSigma 的单位

GMAT 支持的每种测量数据类型的 `Bias`、`BiasSigma` 和 `NoiseSigma` 所用单位，列于《Tracking Data Types for Orbit Determination》中的测量类型描述表。

### 随弧圈变化的偏差估计（Pass-dependent Bias Estimation）

GMAT 提供两种测量偏差估计选项，在 ErrorModel 的 SolveFor 参数上设置：`Bias` 和 `PassBiases`。每个 ErrorModel 实例只能选择一种选项，但一次估计运行可以对不同的误差模型同时执行 Bias 和 PassBiases 估计。

`Bias` 求解选项指示 GMAT 对使用该误差模型的每个站和每艘航天器，在整个估计弧段上估计单个偏差。由于同一个 ErrorModel 实例可应用于多个跟踪站，将为该误差模型所应用的每个跟踪站和每艘航天器分别估计一个单独的偏差。

`PassBiases` 求解选项指示 GMAT 将测量弧段分割为若干独立的跟踪弧圈（tracking pass），并为每个跟踪弧圈估计独立的偏差。此选项要求用户同时在适用的 `TrackingFileSet` 上指定 `TimeGapForPassBreak`。TimeGapForPassBreak 的值表示跟踪测量之间标志新弧圈开始的时间间隔。时间间隔大于 TimeGapForPassBreak 的测量被假定来自不同的弧圈。一个典型的合适值可以是 30 分钟左右。在这种情况下，相隔 30 分钟或更久的成批跟踪测量被假定为独立的跟踪弧圈，并将为每个跟踪弧圈估计单独的偏差。此过程仅应用于那些使用以 PassBiases SolveFors 配置的误差模型的站。其他采用 Bias SolveFors 选项的误差模型仍将只为整个跟踪弧段估计单个偏差。GMAT 将在估计报告文件和 GMAT 日志文件中标明为每个偏差弧圈识别的弧段。使用 PassBiases 估计时，用户应检查这些文件，以确认弧圈的识别符合用户预期。

## 示例

此示例展示如何为 DSN 序列测距（DSN Sequential Range）观测创建误差模型，并说明测距偏差参数的估计。

```
%   Create an ErrorModel
%   Measurement noise is in Range Units
 
Create ErrorModel RangeModel;
  
RangeModel.Type       = 'DSN_SeqRange';
RangeModel.NoiseSigma = 11.;
RangeModel.Bias       = 0.;
RangeModel.SolveFors  = {Bias};
 
%   Assign it to a ground station
 
Create GroundStation DSN;
 
DSN.ErrorModels = {RangeModel};

BeginMissionSequence;
```

**中文说明**：创建误差模型 RangeModel，类型为 DSN_SeqRange（测量噪声以测距单位 RU 计），噪声 sigma 为 11，常值偏差为 0，并将 Bias 列为求解参数（即估计测距偏差）；然后将该误差模型指定给地面站 DSN。

此示例展示如何为星载 GPS 观测创建误差模型。

```
%   Create an ErrorModel
%   Measurement noise is in kilometers. Bias estimation is not permitted.
 
Create ErrorModel PosVecModel;
  
PosVecModel.Type       = 'GPS_PosVec';
PosVecModel.NoiseSigma = 0.010;
 
%   Assign the error model to a receiver and add that receiver to a spacecraft.
 
Create Antenna GpsAntenna;
Create Receiver GpsReceiver;

GpsReceiver.Id             = 800;
GpsReceiver.PrimaryAntenna = GpsAntenna;
GpsReceiver.ErrorModels    = {PosVecModel};

Create Spacecraft Sat;

Sat.AddHardware = {GpsReceiver, GpsAntenna};

BeginMissionSequence;
```

**中文说明**：创建 GPS_PosVec 类型的误差模型 PosVecModel（测量噪声以 km 计，sigma 为 0.010，不允许偏差估计），将其指定给接收机 GpsReceiver，再把接收机和天线挂载到航天器 Sat 上。
