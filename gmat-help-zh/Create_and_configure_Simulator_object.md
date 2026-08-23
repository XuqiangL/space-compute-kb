# 创建并配置测量仿真器对象（Create_and_configure_Simulator_object）

> 译自 GMAT R2026a 帮助文档 Create_and_configure_Simulator_object.html

（本小节属于"第 13 章 仿真 DSN 测距与多普勒数据"教程）

如下所示，我们创建并配置用于定义仿真的 `Simulator` 对象。

```
Create Simulator Sim;
Sim.AddData             = {DSNsimData};
Sim.EpochFormat         = UTCGregorian;
Sim.InitialEpoch        = '19 Aug 2015 00:00:00.000';
Sim.FinalEpoch          = '19 Aug 2015 00:12:00.000';
Sim.MeasurementTimeStep = 600;
Sim.Propagator          = Prop;
Sim.AddNoise            = Off;
```

**中文说明**：创建测量仿真器 Sim，关联跟踪文件集 DSNsimData，仿真时段为 2015-08-19 00:00 到 00:12 UTCG（12 分钟），测量时间步长 600 秒，使用积分器 Prop，不加噪声。

在上面第一行脚本中，我们创建了 `Simulator` 对象 `Sim`。下一个设置的字段是 `AddData`，用于指定应使用哪个 `TrackingFileSet`。回想一下，`TrackingFileSet` 指定要仿真的数据类型和指定数据存储位置的文件名。我们在"定义要仿真的测量类型"一节中创建的 `TrackingFileSet` `DSNsimData` 指定我们要仿真涉及 `CAN` `GroundStation` 的双向 DSN 测距和多普勒数据。

接下来三行脚本设置 `EpochFormat`、`InitialEpoch` 和 `FinalEpoch` 字段，指定仿真的时间段。这里我们选择 12 分钟的短时长。

下一行脚本设置 `MeasurementTimeStep` 字段，指定请求的测量间隔时间。我们选择 10 分钟。这意味着我们的数据文件最多包含两个测距测量和两个多普勒测量。

下一行脚本设置 `Propagator` 字段，指定应使用哪个 `Propagator` 对象。我们将此字段设为在"创建并配置力模型和积分器"一节中创建的 `Prop` `Propagator` 对象。

最后，在脚本片段的最后一行，我们设置 `AddNoise` 字段，指定是否要向仿真测量添加噪声。可添加的噪声由我们在"创建并配置地面站及相关参数"一节中创建的 `ErrorModel` 对象定义。如该节和"附录 A —— 测量噪声值的确定"所述，添加到测距测量的噪声将是 1 sigma 值为 10.63 测距单位的高斯噪声，添加到多普勒测量的噪声将是 1 sigma 值为 0.0282 Hz 的高斯噪声。对于本仿真，我们选择不添加噪声。
