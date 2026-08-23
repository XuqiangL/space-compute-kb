# 用于轨道确定的传播器配置（NavPropagatorConfiguration）
> 译自 GMAT R2026a 帮助文档 NavPropagatorConfiguration.html

本节介绍为 GMAT 估计器配置数值传播器和星历传播器时的一些特殊注意事项。

## 传播器在估计中的使用

如本文档其他部分所述，所有估计器（`BatchEstimator`、`ExtendedKalmanFilter` 和 `Smoother`）目前都要求定步长积分。估计器所用力模型的 `ErrorControl` 参数必须设置为 `'None'`。定步长积分的步长在传播器的 `InitialStepSize` 和 `MaxStep` 字段上配置。这两个参数所赋的值中较小者将作为积分步长。为避免混淆，通常将两者设为相同的值较为方便。

在最常见的情形下，即对单个航天器运行估计，用户需按照[数值传播器](Propagator.md)资源文档中的说明和示例配置单个数值积分器。配置好的传播器随后被赋值到估计器的 `Propagator` 字段。GMAT 确实允许一些值得进一步说明的非常规配置：

- 对多个航天器进行同时估计，或使用星间（航天器间）跟踪进行估计，其中每个航天器都需要各自独立的力模型和传播器；
- 在估计中使用星历传播器。

这些选项将在接下来的章节中讨论。

> **注意**：星历传播器使用插值方法来获得星历文件中已有状态之间时刻的状态。这些插值方法在星历文件的起始和结束附近、以及星历文件的段边界附近通常精度较低。为获得最佳精度，用户应确保在数据处理区间前后有充足的星历数据，以避免在星历端点或段边界附近出现精度下降。

## 为多航天器同时估计配置传播器

> **注意**：多航天器同时传播仅适用于 `BatchEstimator` 和 `Simulator`，目前 `ExtendedKalmanFilter` 不支持此功能。

GMAT 现在支持对多个航天器进行同时估计，无论是否使用星间（或交叉链路）跟踪。这种场景的一个例子是：一颗处于地球同步轨道的航天器对一颗处于近地轨道的航天器进行跟踪。在这种情况下，近地航天器需要大气阻力建模和相对较小的积分步长，而地球同步航天器不需要大气阻力建模，可以使用较大的积分步长。

要在 GMAT 中配置此功能，用户应为每个航天器创建各自的力模型和传播器。估计器对象上赋值传播器的语法已经过修改，以支持将各个传播器分别赋给每个航天器。当估计过程中需要多个传播器时，现在可以使用以下语法（本示例以 `BatchEstimator` 资源为例进行说明，但该语法对 `Simulator` 同样适用）：

```
Create Spacecraft EstLEO, EstGEO1, EstGEO2, EstGEO3

%
%   ForceModels and Propagators
%

Create ForceModel LeoFM;

LeoFM.CentralBody                      = Earth;
LeoFM.PrimaryBodies                    = {Earth}
LeoFM.GravityField.Earth.Degree        = 30;
LeoFM.GravityField.Earth.Order         = 30;
LeoFM.GravityField.Earth.PotentialFile = 'JGM2.cof';
LeoFM.SRP                              = On;
LeoFM.SRP.Flux                         = 1370.052;
LeoFM.Drag.AtmosphereModel             = 'JacchiaRoberts';
LeoFM.Drag.HistoricWeatherSource       = 'CSSISpaceWeatherFile';
LeoFM.ErrorControl                     = None;

Create Propagator LeoProp;

LeoProp.FM                             = LeoFM;
LeoProp.Type                           = RungeKutta89;
LeoProp.InitialStepSize                = 60;
LeoProp.Accuracy                       = 1e-13;
LeoProp.MinStep                        = 0;
LeoProp.MaxStep                        = 60;
LeoProp.MaxStepAttempts                = 50;

Create ForceModel GeoFM;

GeoFM.CentralBody                      = Earth;
GeoFM.PrimaryBodies                    = {Earth}
GeoFM.PointMasses                      = {Luna, Sun}
GeoFM.GravityField.Earth.Degree        = 8;
GeoFM.GravityField.Earth.Order         = 8;
GeoFM.GravityField.Earth.PotentialFile = 'JGM2.cof';
GeoFM.Drag                             = None;
GeoFM.SRP                              = On;
GeoFM.ErrorControl                     = None;

Create Propagator GeoProp;

GeoProp.FM                             = GeoFM;
GeoProp.Type                           = RungeKutta89;
GeoProp.InitialStepSize                = 300;
GeoProp.Accuracy                       = 1e-13;
GeoProp.MinStep                        = 0;
GeoProp.MaxStep                        = 300;
GeoProp.MaxStepAttempts                = 50;

%
%   Estimator
%

Create BatchEstimator BLS

BLS.ShowProgress               = true;
BLS.Measurements               = {estData} 
BLS.AbsoluteTol                = 0.005;
BLS.RelativeTol                = 0.001;
BLS.MaximumIterations          = 10;
BLS.MaxConsecutiveDivergences  = 5;
BLS.Propagator                 = {LeoProp, EstLEO};
BLS.Propagator                 = {GeoProp, EstGEO1, EstGEO2, EstGEO3};
BLS.ShowAllResiduals           = On;
BLS.OLSEInitialRMSSigma        = 1000;
BLS.OLSEMultiplicativeConstant = 3;
BLS.OLSEUseRMSP                = False;
BLS.UseInitialCovariance       = False
BLS.ReportFile                 = 'bls_report.txt';

%
%   Mission Sequence
%

BeginMissionSequence
```

**中文说明**：上述脚本创建了一颗近地轨道航天器（EstLEO）和三颗地球同步轨道航天器（EstGEO1–3），并分别为近地轨道和地球同步轨道配置了各自的力模型（LeoFM、GeoFM）与传播器（LeoProp、GeoProp）。近地传播器使用 60 秒步长并启用大气阻力建模，地球同步传播器使用 300 秒步长且不建模大气阻力。随后在批处理估计器 BLS 上分别赋值传播器。

在上述示例中，请特别注意 `BLS.Propagator` 的赋值。

```
BLS.Propagator                 = {LeoProp, EstLEO};
BLS.Propagator                 = {GeoProp, EstGEO1, EstGEO2, EstGEO3};
```

**中文说明**：该语法将 LeoProp 传播器赋给 EstLEO 航天器，并将 GeoProp 传播器赋给航天器 EstGEO1、EstGEO2 和 EstGEO3。这使得估计器在执行估计时能够针对每个航天器使用合适的力模型和传播控制。

请注意，用于单航天器传播的旧语法仍可用于多航天器估计场景，如下所示。

```
BLS.Propagator                 = LeoProp;
```

**中文说明**：但请注意，当在多航天器估计运行中使用该语法时，将导致 LeoProp 力模型和传播器被用于本次运行中的所有航天器。

### 与传播器 MaxStepAttempts 的相互作用

当使用多个具有不同步长的传播器时，必须注意每个传播器的 `MaxStepAttempts` 参数。在传播过程中，GMAT 首先以步长最大的传播器的步长迈出一步。然后它查看其余传播器，并让每个传播器尽可能多地迈步，以追平较大步长传播器的步长，其中 `MaxStepAttempts` 参数用于指示允许尝试的步数。例如，如果一个传播器配置为使用 300 秒步长，另一个使用 5 秒步长，那么以 5 秒步长迈步的传播器需要 60 步才能匹配 300 秒步长传播器的每一步。若 `MaxStepAttempts` 参数为 50（默认值），5 秒步长的传播器在超过 `MaxStepAttempts` 之前无法达到 300 秒的目标步长，GMAT 将发出失败消息。在这种情况下，应将 5 秒传播器的 `MaxStepAttempts` 设置为 60 或更大。

## 星历传播器在估计中的使用

> **注意**：GMAT 目前支持将 SPK/SPICE、STK 和 CCSDS OEM 星历文件用作估计的星历传播器。Code500 星历格式不支持用作估计器的星历传播器。在估计过程中使用星历传播器仅允许在 `Simulator` 和 `BatchEstimator` 中进行。对于使用星历传播器的航天器，用户无法估计其任何轨道参数。

对于参与估计或仿真运行的任何航天器，都可以使用星历传播器来代替数值传播器。这种场景的一个用例是：使用跟踪与数据中继卫星系统（TDRSS）或其他中继或星间跟踪来估计一个或多个航天器，此时分析人员拥有跟踪航天器轨道的星历，并希望估计目标或用户航天器的轨道。GMAT 还允许同时估计 TDRS 和用户轨道，或根据给定的用户或目标航天器轨道来估计 TDRS 轨道。请注意，对于正在使用星历传播器的任何航天器，都无法估计其轨道。

用于估计的星历传播器可以按照 [Propagator](Propagator.md) 资源中的说明，配置为 SPICE/SPK、STK 或 CCSDS OEM 格式的星历文件。在上面所示的示例中，可以使用估计器 `Propagator` 参数上为多航天器传播所示的相同语法，将任何航天器赋给星历传播器。

### 使用星历文件进行 BatchEstimator“观测减计算”（OMC）运行

用户可以配置 `BatchEstimator`，使用星历传播器执行“观测减计算”（OMC）运行。这种用法的一个例子是：用户拥有一个对某次机动建模的预报星历，希望通过检查传入的机动前和机动后跟踪数据相对于星历机动预报的残差，来评估该机动的执行情况。（请注意，也可以使用状态矢量、数值传播器和对机动建模的 `ThrustHistoryFile` 来配置同样的运行。）类似地，用户也可能只想计算跟踪数据相对于自由飞行（无机动）星历的残差。

在上述任一情况下，用户都应按照 [Propagator](Propagator.md) 资源中的说明配置星历传播器，并将星历传播器赋到 `BatchEstimator` 的 `Propagator` 参数上。当使用星历传播器运行批处理估计器时，无法进行状态估计，用户在调用 `RunEstimator` 时还应将估计器的 `SolveMode` 设置为 `RunInitialGuess`。更多细节请参见 [RunEstimator](RunEstimator.md)。此功能目前不适用于 `ExtendedKalmanFilter`。