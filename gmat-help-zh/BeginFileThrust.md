# 开始文件推力（BeginFileThrust）

> 译自 GMAT R2026a 帮助文档 BeginFileThrust.html

**BeginFileThrust** —— 施加分段连续的推力/加速度和质量流率剖面。

## 脚本语法

```
BeginFileThrust aThrustHistoryFile(aSpacecraft)

EndFileThrust aThrustHistoryFile(aSpacecraft)
```

其中 `aThrustHistoryFile` 为推力历史文件对象，`aSpacecraft` 为航天器对象。

## 描述

当施加 `BeginFileThrust` 命令时，将打开指定的 `ThrustHistoryFile`（推力历史文件）中给出的、施加到指定 `Spacecraft` 的推力/加速度和质量流率剖面。类似地，当施加 `EndFileThrust` 命令时，将关闭指定的 `ThrustHistoryFile` 中给出的、施加到指定 `Spacecraft` 的推力/加速度和质量流率剖面。要真正施加推力/加速度和质量流率剖面，必须在 `BeginFileThrust` 和 `EndFileThrust` 命令之间存在一个 `Propagate` 命令。

要施加 `BeginFileThrust` 和 `EndFileThrust` 命令，必须配置一个 `ThrustHistoryFile` 对象。而该 `ThrustHistoryFile` 对象又需要配置一个或多个 `ThrustSegment`（推力段）对象。更详细的说明请参阅"备注"部分和下面的示例。

另请参阅：Spacecraft（航天器）、ThrustHistoryFile（推力历史文件）、ThrustSegment（推力段）、ChemicalTank（化学推进剂箱）。

## 选项

| 选项 | 描述 |
|------|------|
| **BeginFileThrust - ThrustHistoryFile** | 指定由 `BeginFileThrust` 命令激活的 `ThrustHistoryFile` 对象。<br>• 接受的数据类型：`ThrustHistoryFile`<br>• 允许值：`ThrustHistoryFile` 对象<br>• 默认值：N/A<br>• 是否必需：是<br>• 接口：脚本 |
| **BeginFileThrust - Spacecraft** | 指定受 `BeginFileThrust` 命令作用的 `Spacecraft`。由 `ThrustHistoryFile` 指定并施加到 `Spacecraft` 的推力/加速度和质量流率剖面将被激活。<br>• 接受的数据类型：`Spacecraft`<br>• 允许值：`Spacecraft` 对象<br>• 默认值：N/A<br>• 是否必需：是<br>• 接口：脚本 |
| **EndFileThrust - ThrustHistoryFile** | 指定由 `EndFileThrust` 命令停用的 `ThrustHistoryFile` 对象。<br>• 接受的数据类型：`ThrustHistoryFile`<br>• 允许值：`ThrustHistoryFile` 对象<br>• 默认值：N/A<br>• 是否必需：是<br>• 接口：脚本 |
| **EndFileThrust - Spacecraft** | 指定受 `EndFileThrust` 命令作用的 `Spacecraft`。由 `ThrustHistoryFile` 指定并施加到 `Spacecraft` 的推力/加速度和质量流率剖面将被停用。<br>• 接受的数据类型：`Spacecraft`<br>• 允许值：`Spacecraft` 对象<br>• 默认值：N/A<br>• 是否必需：是<br>• 接口：脚本 |
## 备注

### 使用 BeginFileThrust 和 EndFileThrust 命令

要在任务序列中使用 `BeginFileThrust` 和 `EndFileThrust` 命令，必须配置一个 `ThrustHistoryFile` 对象以及一个或多个 `ThrustSegment` 对象。此外，如果你希望施加质量流率剖面，还必须创建一个 `ChemicalTank` 对象。更多细节见下面的步骤。

1. 创建一个 `Spacecraft` 对象，你希望修改其推力/加速度和/或质量流率剖面。
2. 如果你希望施加质量流率剖面，创建并配置一个 `ChemicalTank` 模型。将该 `ChemicalTank` 添加到第 1 步中创建的 `Spacecraft`。该 `ChemicalTank` 的质量将按照我们将要创建的 `ThrustHistoryFile` 和 `ThrustSegment` 对象所指定的剖面变化。
3. 创建一个或多个 `ThrustSegment` 对象。推力段是 `ThrustHistoryFile` 对象所指定文件内的一块数据，封装在 "BeginThrust {ThrustSegment 对象名}" 和 "EndThrust {ThrustSegment 对象名}" 关键字之间。一个给定的推力历史文件可以包含一个或多个推力段。如 ThrustSegment（推力段）帮助中所述，`ThrustSegment` 对象描述将如何使用段数据。应采取以下步骤：
   a. 设置 `ThrustSegment` 的参数（比例因子相关参数、求解参数等）；
   b. （如果建模质量流）将 `ThrustSegment` 配置为使用第 2 步中创建的 `ChemicalTank`。
4. 创建一个 `ThrustHistoryFile` 对象：
   a. 使用 `ThrustHistoryFile.AddThrustSegment` 参数指定我们新的 `ThrustHistoryFile` 对象将使用第 3 步中创建的哪些 `ThrustSegment`；
   b. 指定实际的推力历史文件名。
5. 创建第 4 步 b 部分所指定的推力历史文件。根据需要参阅 ThrustHistoryFile（推力历史文件）帮助，其中包含文件格式的描述。

当将 `Toggle` 命令与星历文件中的有限推力机动建模结合使用时，必须遵守一定的操作顺序。星历 Toggle 命令必须放在 BeginFileThrust 和 EndFileThrust 命令之内，如下例所示。在传播时，以及在运行诸如 `BatchEstimator`（批处理估计器）、`ExtendedKalmanFilter`（扩展卡尔曼滤波器）或 `Smoother`（平滑器）之类的估计器时，都必须遵守此操作顺序。

```
BeginFileThrust ThrustHistory(Sat);
Toggle Ephem On;
Propagate Prop(Sat) {Sat.ElapsedDays = 1};
Toggle Ephem Off;
EndFileThrust ThrustHistory(Sat);
```

上述脚本：在 BeginFileThrust/EndFileThrust 之间先打开星历（Toggle Ephem On），传播 1 天，再关闭星历——演示了星历 Toggle 命令必须置于文件推力命令之内的正确顺序。

### BeginFileThrust 和 EndFileThrust 命令不是分支命令

`BeginFileThrust` 和 `EndFileThrust` 命令不是分支命令，这意味着 `BeginFileThrust` 命令可以在没有 `EndFileThrust` 命令的情况下存在。

类似地，由于 `BeginFileThrust` 和 `EndFileThrust` 命令用于打开或关闭推力/质量和质量流率剖面，在脚本中多次施加同一命令而没有其逆命令，与施加一次的效果相同。换句话说，如果你这样做：

```
BeginFileThrust aThrustHistoryFile(aSat);
BeginFileThrust aThrustHistoryFile(aSat);
BeginFileThrust aThrustHistoryFile(aSat);
```

其效果与只施加一次 `BeginFileThrust` 命令相同。`EndFileThrust` 命令也是如此。
## 示例

### 向航天器施加推力和质量流率剖面

我们将创建一个示例脚本，向 `Spacecraft` 对象施加推力和质量流率剖面。在脚本中，我们将创建一个初始历元为 '01 Jan 2010 00:00:00.000' 的 `Spacecraft` 对象 `aSat`。我们决定从 '01 Jan 2010 00:01:00.000' 开始，在地心惯性（ECI）X 方向施加 3 牛顿的力，持续 100 秒。在同一时间段内，我们还希望施加一个以 0.01 kg/s 的速率消耗燃料的质量流率剖面。在运行脚本之前，我们需要创建一个推力历史文件，其内容如下所示。用户应将该文件命名为 'SampleThrustFile.thrust' 并放在 GMAT 的 'data' 目录中。

```
BeginThrust {aThrustSegment}
Start_Epoch = 01 Jan 2010 00:00:00.000
Thrust_Vector_Coordinate_System = EarthMJ2000Eq   
Thrust_Vector_Interpolation_Method  = None
Mass_Flow_Rate_Interpolation_Method = None
ModelThrustAndMassRate
60.0      3.0 0.0 0.0  0.01
160.0     3.0 0.0 0.0  0.01
EndThrust {aThrustSegment}
```

上述推力历史文件：定义名为 aThrustSegment 的推力段，起始历元为 2010 年 1 月 1 日 00:00:00（UTC），推力矢量坐标系为 EarthMJ2000Eq，推力矢量与质量流率均不插值，同时建模推力和质量流率；数据行表示从历元起 60 秒到 160 秒之间施加推力矢量 (3.0, 0.0, 0.0) N 和质量流率 0.01 kg/s。

下面，我们创建一个脚本，它将：

- 创建并配置所需的 `Spacecraft`、`ChemicalTank`、`Propagator`、`ThrustSegment` 和 `ThrustHistoryFile` 对象。
- 使用 `BeginFileThrust` 和 `EndFileThrust` 命令将所需的推力和质量流率剖面施加到 `Spacecraft` 对象 `aSat`。
- 创建并配置一个 `ReportFile` 对象，以便我们能够确定所创建的 `ChemicalTank` 对象在施加所需推力和质量流率剖面前后的燃料质量。

```
%  Create and configure objects
Create Spacecraft aSat
aSat.DateFormat = UTCGregorian;
aSat.Epoch = '01 Jan 2010 00:00:00.000';

Create ChemicalTank aTank 
aSat.Tanks = {aTank}

Create Propagator aPropagator

Create ThrustSegment aThrustSegment
aThrustSegment.ThrustScaleFactor = 1.2;
aThrustSegment.ApplyThrustScaleToMassFlow = false;
aThrustSegment.MassFlowScaleFactor = 2.0;
aThrustSegment.MassSource = {'aTank'};

Create ThrustHistoryFile aThrustHistoryFile

aThrustHistoryFile.AddThrustSegment = {'aThrustSegment'};
aThrustHistoryFile.FileName = '../data/SampleThrustFile.thrust';

Create ReportFile aReportFile

BeginMissionSequence

Report aReportFile aSat.aTank.FuelMass

BeginFileThrust aThrustHistoryFile(aSat);
  Propagate aPropagator(aSat) {aSat.ElapsedSecs = 180.0};
EndFileThrust aThrustHistoryFile(aSat);

Report aReportFile aSat.aTank.FuelMass
```

上述脚本：创建航天器 aSat（初始历元 2010-01-01 00:00:00 UTC）、燃料箱 aTank 并挂载到航天器；创建传播器；创建推力段 aThrustSegment（推力比例因子 1.2，推力比例不作用于质量流，质量流比例因子 2.0，质量来源为 aTank）；创建推力历史文件对象并添加推力段、指定文件名；任务序列中先报告燃料质量，然后在 BeginFileThrust/EndFileThrust 之间传播 180 秒，最后再次报告燃料质量。

运行上述脚本后，查看 `aTank` 燃料质量的前后值，注意质量减少了 2 kg。这是预期结果。回想一下，我们从 '01 Jan 2010 00:01:00.000' 开始到 '01 Jan 2010 00:02:40.000' 结束，施加 100 秒的 0.01 kg/s 质量流率剖面。100 秒乘以 0.01 kg/s 对应 1 kg 的质量减少，但我们需要记住 aThrustSegment.MassFlowScaleFactor=2.0。因此，文件中指定的质量流率被加倍，得到预期的 2 kg 质量减少。

### 导航应用

在上面的示例中，我们重点介绍了在任务设计轨道传播上下文中向航天器施加推力和质量流率剖面。我们通过在 `BeginFileThrust` 和 `EndFileThrust` 命令之间夹入一个 `Propagate` 命令来实现这一点。你也可以在轨道确定的上下文中使用 `BeginFileThrust` 和 `EndFileThrust` 命令。这是通过在 `BeginFileThrust` 和 `EndFileThrust` 命令之间夹入一个 `RunSimulator` 或 `RunEstimator` 命令来实现的。

请参阅 sample/Navigation 文件夹中的脚本 Simulate_Continuous_thrust_SolveFor_ScaleFactor.script，它在轨道确定上下文中使用了 `BeginFileThrust` 和 `EndFileThrust` 命令。在该脚本中：

- 我们配置了两颗低地球轨道的 `Spacecraft`——`SimSat` 和 `EstSat`，使用来自三个地面站（GroundStation）的测距（Range）测量来获得导航解。
- `SimSat` 航天器用于在 12 小时内生成仿真测距测量。在整个期间，施加沿速度方向 20 N 的推力历史剖面。施加该推力时，我们使用 ThrustScaleFactor 为 1.0。对于这个简化情形，我们不施加质量流率剖面。
- `EstSat` 航天器读入由 `SimSat` 航天器生成的仿真测距测量。在整个 12 小时期间，同样施加沿速度方向 20 N 的推力历史剖面，但 ThrustScaleFactor 使用不同的起始值。我们希望求解 EstSat 的 ThrustScaleFactor。我们从先验猜测 ThrustScaleFactor = 0.75 开始，这会导致较大的初始残差。我们运行估计过程，结果表明：我们既收敛到具有低测量残差的良好轨道解，又求解出接近真实值 1.0 的 ThrustScaleFactor。
