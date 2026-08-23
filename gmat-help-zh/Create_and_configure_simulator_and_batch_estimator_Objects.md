# 创建并配置测量仿真器和批处理估计器对象（Create_and_configure_simulator_and_batch_estimator_Objects）

> 译自 GMAT R2026a 帮助文档 Create_and_configure_simulator_and_batch_estimator_Objects.html

（本小节属于"第 16 章 仿真与估计航天器间跟踪"教程）

## 创建测量仿真器对象

如下所示，我们创建并配置用于定义仿真的 `Simulator` 对象。

```
%
%   Simulator
%

Create Simulator sim

sim.AddData                    = {simData}
sim.EpochFormat                = 'UTCGregorian'
sim.InitialEpoch               = '10 Jun 2010 00:00:00.000'
sim.FinalEpoch                 = '11 Jun 2010 00:00:00.000'
sim.MeasurementTimeStep        = 60
sim.Propagator                 = Prop
sim.AddNoise                   = On
```

**中文说明**：创建测量仿真器 sim，关联跟踪文件集 simData，仿真时段为 2010-06-10 至 2010-06-11（两天），测量时间步长 60 秒，使用积分器 Prop，开启噪声添加。

在上面第一行脚本中，我们创建了 `Simulator` 对象 `sim`。下一个设置的字段是 `AddData`，用于指定应使用哪个 `TrackingFileSet`。回想一下，`TrackingFileSet` 指定要仿真的数据类型和指定数据存储位置的文件名。我们在"定义要仿真的测量类型及其关联误差模型"一节中创建的 `TrackingFileSet` `simData`，指定我们要仿真涉及 `SimMeasureSat` `Spacecraft` 的双向测距和测距变率数据。

接下来三行脚本设置 `EpochFormat`、`InitialEpoch` 和 `FinalEpoch` 字段，指定仿真的时间段。这里我们选择两天的时长。

下一行脚本设置 `MeasurementTimeStep` 字段，指定请求的测量间隔时间。我们选择 1 分钟。

下一行脚本设置 `Propagator` 字段，指定应使用哪个 `Propagator` 对象。我们将此字段设为在"创建并配置力模型和积分器"一节中创建的 `Prop` 对象。

最后，在脚本片段的最后一行，我们设置 `AddNoise` 字段，指定是否要向仿真测量添加噪声。添加的噪声由我们在"创建测量误差模型"一节中创建的 `ErrorModel` 对象定义。如该节所述，添加到测距测量的噪声将是 1-sigma 值为 10 米的高斯噪声，添加到测距变率测量的噪声将是 1 sigma 值为 1 mm/sec 的高斯噪声。

## 创建批处理估计器对象

为了估计被观测航天器的真实初始状态，我们在下面的脚本中定义 `BatchEstimator bat`。

```
%
%   Estimator
%

Create BatchEstimator bat

bat.ShowProgress               = True
bat.Measurements               = {estData} 
bat.AbsoluteTol                = 0.000001
bat.RelativeTol                = 0.005
bat.MaximumIterations          = 10
bat.MaxConsecutiveDivergences  = 3
bat.Propagator                 = Prop
bat.ShowAllResiduals           = On
bat.OLSEInitialRMSSigma        = 3000
bat.OLSEMultiplicativeConstant = 3
bat.OLSEAdditiveConstant       = 0
bat.ReportFile                 = 'InterSpacecraft_Range_and_RangeRate.txt'
```

**中文说明**：创建批处理估计器 bat，使用跟踪文件集 estData，绝对收敛容差 1e-6，相对容差 0.005，最多 10 次迭代，最多连续发散 3 次，使用积分器 Prop，显示所有残差图，OLSE 初始 RMS sigma 3000、乘性常数 3、加性常数 0，报告文件为 InterSpacecraft_Range_and_RangeRate.txt。

有关定义批处理估计器对象所涉及参数的更多信息，请参见 BatchEstimator 文档。
