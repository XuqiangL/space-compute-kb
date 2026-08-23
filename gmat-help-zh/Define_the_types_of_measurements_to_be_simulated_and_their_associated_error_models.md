# 定义要仿真的测量类型及其关联误差模型（Define_the_types_of_measurements_to_be_simulated_and_their_associated_error_models）

> 译自 GMAT R2026a 帮助文档 Define_the_types_of_measurements_to_be_simulated_and_their_associated_error_models.html

（本小节属于"第 16 章 仿真与估计航天器间跟踪"教程）

## 定义仿真和估计器的跟踪文件集

现在我们将创建并配置一个 `TrackingFileSet` 资源。此资源定义要仿真的数据类型、将使用的地面站，以及将包含仿真数据的输出 GMD 文件的文件名。此外，`TrackingFileSet` 资源将定义各种数据类型所需的仿真参数。估计也创建一个类似的 `TrackingFileSet`，其输入对应于估计用航天器。

```
%
%   Tracking file sets
%

Create TrackingFileSet simData

simData.AddTrackingConfig       = {{SimTrackSat, SimSat, SimTrackSat}, 'Range', 'RangeRate'}
simData.FileName                = {'InterSpacecraft_Range_and_RangeRate.gmd'}
simData.UseLightTime            = True
simData.UseRelativityCorrection = True
simData.UseETminusTAI           = True
simData.SimDopplerCountInterval = 10.

Create TrackingFileSet estData

estData.AddTrackingConfig       = {{EstTrackSat, EstSat, EstTrackSat}, 'Range', 'RangeRate'}
estData.FileName                = {'InterSpacecraft_Range_and_RangeRate.gmd'}
estData.UseLightTime            = True
estData.UseRelativityCorrection = True
estData.UseETminusTAI           = True
```

**中文说明**：创建两个跟踪文件集——simData（仿真用，跟踪链路 SimTrackSat→SimSat→SimTrackSat，测量类型 Range 和 RangeRate，多普勒计数区间 10 秒）和 estData（估计用，跟踪链路 EstTrackSat→EstSat→EstTrackSat），两者读写同一个 GMD 文件 InterSpacecraft_Range_and_RangeRate.gmd。

对于每个 `TrackingFileSet`，脚本行分为三个部分。第一部分（每个 `TrackingFileSet` 的前两行）声明资源名，定义数据类型，并指定输出文件名。`AddTrackingConfig` 是用于定义数据类型的字段。`AddTrackingConfig` 行告诉 GMAT 仿真 TrackSat 到 Sat 到 TrackSat 测量链路的 Range 和 RangeRate 双向测量。

第二部分（接下来三行）设置一些同时适用于测距和多普勒测量的仿真参数。我们将 `UseLightTime` 设为 True，以生成 GMAT 考虑光速有限性的真实测量。本节的最后两个参数 `UseRelativityCorrection` 和 `UseETminusTAI` 设为 True，以便将 Moyer [2000] 中描述的广义相对论修正施加于光行时方程。

上面第三部分（`simData` 配置的最后一行）设置适用于特定测量类型的仿真参数。`SimDopplerCountInterval` 仅适用于 RangeRate 测量。注意，字段名中的"Sim"用于表明这些字段仅在 GMAT 处于仿真模式（即使用 `RunSimulator` 命令）时适用，在 GMAT 处于估计模式（即使用 `RunEstimator` 命令）时不适用。`SimDopplerCountInterval`（多普勒计数区间）设为 10 秒。此参数仅适用于仿真器使用的跟踪文件集，不在估计器使用的跟踪文件集上设置。此参数如何用于计算测量值的描述请参见 `RunSimulator` 帮助。

## 创建测量误差模型

所有测量类型都有与之关联的随机噪声和/或偏差。对于航天器间测量，这些效应用跟踪航天器接收机上的误差模型建模。由于我们已经创建了 `Spacecraft` 对象及其相关硬件，现在创建接收机误差模型。由于我们希望仿真 Range 和 RangeRate 数据，需要创建两个误差模型，如下所示，一个用于测距测量，一个用于测距变率测量。

```
%
%   Spacecraft error models
%

Create ErrorModel Range

Range.Type           = 'Range'
Range.NoiseSigma     = 0.010
Range.Bias           = 0.0
Range.SolveFors      = {}

Create ErrorModel RangeRate

RangeRate.Type       = 'RangeRate'
RangeRate.NoiseSigma = 0.000001
RangeRate.Bias       = 0.0
RangeRate.SolveFors  = {}

MeasurementReceiver.ErrorModels = {Range, RangeRate}
```

**中文说明**：创建两个误差模型——Range（噪声 sigma 0.010 km 即 10 米，偏差 0）和 RangeRate（噪声 sigma 0.000001 km/s 即 1 mm/s，偏差 0），不求解偏差（SolveFors 为空），并挂接到 MeasurementReceiver 接收机。

上面的脚本片段分为三个部分。第一部分定义名为 `Range` 的 `ErrorModel`。误差模型 Type 为 Range，表明它是双向测距测量的误差模型。高斯白噪声的 1-sigma 标准差设为 10 米（0.010 km），测量偏差设为 0 km。

上面第二部分定义名为 `RangeRate` 的 `ErrorModel`。误差模型 Type 为 RangeRate，表明它是双向平均测距变率测量的误差模型。高斯白噪声的 1-sigma 标准差设为 1 mm/sec，测量偏差设为 0 km/sec。

上面第三部分将我们刚创建的两个 `ErrorModel` 资源挂接到 `MeasurementReceiver` `Receiver`。对于航天器间测量，测量噪声或偏差定义在接收机硬件上。包含该接收机的航天器执行的每个测量必须有关联的误差模型。因此，任何涉及带有 `MeasurementReceiver` `Receiver` 的 `Spacecraft` 的测距测量误差由 `Range` `ErrorModel` 定义，任何涉及带有该接收机的 `Spacecraft` 的测距变率测量误差由 `RangeRate` `ErrorModel` 定义。注意，由于 GMAT 目前只建模发射和接收航天器相同的双向测量，我们不必考虑发射和接收航天器不同的情况。
