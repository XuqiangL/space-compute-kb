# 创建更真实的 GMAT 测量数据文件（GMD）（Create_Realistic_GMD）

> 译自 GMAT R2026a 帮助文档 Create_Realistic_GMD.html

（本小节属于"第 13 章 仿真 DSN 测距与多普勒数据"教程）

我们已经运行了一个简短的简单仿真并生成了示例 GMD 文件。我们的下一个目标是生成一个真实的 GMD 文件，供另一个脚本读入并生成轨道确定解。为增加真实性，我们将做以下工作：

- 从更多地面站生成数据
- 添加斜坡表的使用
- 执行更长时间的仿真
- 添加测量噪声

为了从更多地面站生成测量数据，我们必须首先创建和配置额外的 `GroundStation` 对象。下面，我们创建并配置两个新地面站 `GDS` 和 `MAD`。

```
Create GroundStation GDS;  
GDS.CentralBody           = Earth;
GDS.StateType             = Cartesian;
GDS.HorizonReference      = Ellipsoid;
GDS.Location1             = -2353.621251;
GDS.Location2             = -4641.341542;
GDS.Location3             = 3677.052370;
GDS.Id                    = '33333';
GDS.AddHardware           = {DSNTransmitter, DSNAntenna, DSNReceiver};
GDS.MinimumElevationAngle = 7.0;
GDS.IonosphereModel       = 'IRI2007';
GDS.TroposphereModel      = 'HopfieldSaastamoinen';

Create GroundStation MAD;  
MAD.CentralBody           = Earth;
MAD.StateType             = Cartesian;
MAD.HorizonReference      = Ellipsoid;
MAD.Location1             = 4849.519988;
MAD.Location2             = -0360.641653;
MAD.Location3             = 4114.504590;
MAD.Id                    = '44444';
MAD.AddHardware           = {DSNTransmitter, DSNAntenna, DSNReceiver};
MAD.MinimumElevationAngle = 7.0;
MAD.IonosphereModel       = 'IRI2007';
MAD.TroposphereModel      = 'HopfieldSaastamoinen';
```

**中文说明**：创建 GDS（戈德斯通，ID 33333）和 MAD（马德里，ID 44444）两个地面站，配置与 CAN 相同。

现在我们定义了两个额外的地面站，必须指定与这些新地面站关联的测量噪声。可以使用先前创建的 `ErrorModel` 资源完成，如下所示。

```
GDS.ErrorModels           = {DSNrange, DSNdoppler};
MAD.ErrorModels           = {DSNrange, DSNdoppler};
```

**中文说明**：将测距和多普勒误差模型挂接到 GDS 和 MAD。

接下来，我们必须将与新地面站对应的双向测距和多普勒测量添加到 `TrackingFileSet` 对象 `DSNsimData`，如下所示。

```
DSNsimData.AddTrackingConfig = {{GDS, Sat, GDS}, 'DSN_SeqRange'};   
DSNsimData.AddTrackingConfig = {{GDS, Sat, GDS}, 'DSN_TCP'};

DSNsimData.AddTrackingConfig = {{MAD, Sat, MAD}, 'DSN_SeqRange'};   
DSNsimData.AddTrackingConfig = {{MAD, Sat, MAD}, 'DSN_TCP'};
```

**中文说明**：为 GDS 和 MAD 各添加 DSN_SeqRange 和 DSN_TCP 跟踪配置。

我们现在创建斜坡表——许多（但不是所有）任务都使用它。斜坡表是允许 GMAT 计算仿真中涉及的所有地面站发射频率的表。回想一下，GMAT 需要知道随时间变化的发射频率才能计算观测值。使用"斜坡"（ramp）一词是因为发射频率随时间线性增长，发射频率对时间的图通常呈现斜坡形状。不使用斜坡表的任务只需对给定地面站使用恒定发射频率。

要修改脚本以使用斜坡表，我们修改 `TrackingFileSet` 对象 `DSNsimData`，如下所示。

```
DSNsimData.RampTable = ...
{'../output/Simulate DSN Range and Doppler Data 3 weeks.rmp'};
```

**中文说明**：指定斜坡表文件路径。

我们现在必须在 GMAT 'output' 目录中创建具有上述名称的文件。斜坡表文件格式的描述请参见 `TrackingFileSet` 帮助。为使 GMAT 能确定所有地面站的发射频率，斜坡表必须对提供测量数据的每个地面站至少有一行数据。我们斜坡表的内容如下所示。

```
          27252   22222   11111   2   1   7.2e09   0.2
          27252   33333   11111   2   1   7.3e09   0.3
          27252   44444   11111   2   1   7.4e09   0.4
```

**中文说明**：三行斜坡记录分别对应 CAN（22222）、GDS（33333）、MAD（44444）对 Sat（11111）的上行链路，X 频段，新斜坡开始，起始频率分别为 7.2/7.3/7.4 GHz，斜坡率 0.2/0.3/0.4 Hz/s。

上面每行数据称为一条斜坡记录。让我们分析第一条斜坡记录。第一个字段 27252 是斜坡记录的 TAIMJD 日期。

第二个字段 22222 是指定频率的 `GroundStation` 对象的地面站 ID。注意 ID 22222 对应 `CAN` 地面站。第三个字段 11111 是 `CAN` 地面站正在向其发射的航天器 ID。我们知道 11111 是 `Sat` 航天器的 ID。

第 4 个字段 2 是表示发射上行频段的整数。整数 2 代表 X 频段。第 5 个字段 1 是描述斜坡类型的整数。整数 1 代表新斜坡的开始。

第 6 个字段 7.2e9 是在第一字段给定时刻从 `CAN` 到 `Sat` 的发射频率（Hz）。第 7 个输入是斜坡率（Hz/s）。

我们现在描述 GMAT 如何使用斜坡记录确定给定时刻 `CAN` 到 `Sat` 的发射频率。令 TAIMJD 为斜坡记录关联的时刻。则 GMAT 将按如下方式计算 t = 27252.5 TAIMJD 处的发射频率值：

　　f(t) = f(t_o) + RampRate * 86400 * (t − t_o)

其中：

- f(t_o) = 斜坡记录起始时刻的发射频率
- f(t) = 稍后时刻 t > t_o 的发射频率

注意，在有许多斜坡记录的典型情况下，假定选择 t_o < t 且尽可能接近时刻 t。对于我们上面的情况，时刻 t 从 `CAN` 到 `Sat` 的发射频率为：

　　f(t) = 7.2e9 + 0.2 * 86400 * (27252.5 − 27252) = 7200008640 Hz

斜坡表的第二行和第三行使 GMAT 能分别计算从 `GDS` 到 `Sat` 和从 `MAD` 到 `Sat` 的发射频率。我们现在创建名为 `Simulate DSN Range and Doppler Data Realistic GMD.rmp` 的文件，内容为上述内容，并将其放在 GMAT 的 'output' 文件夹中。

关于斜坡表的使用，我们最后说明一点。注意，当使用斜坡表时，GMAT 以不同方式使用各脚本输入（例如 `SatTransponder.TurnAroundRatio` 和 `DSNTransmitter.Frequency`）。细节请参见 `RunSimulator` 帮助。

要创建生成更真实测量数据的脚本，只剩两个步骤。第一步是将仿真时间从 10 分钟增加到更真实的三周数据量——这是对这类深空轨道航天器生成轨道确定解通常所需的。第二步是打开测量噪声。这两个步骤通过对 `TrackingFileSet` 对象 `DSNsimData` 进行以下更改来完成（译注：实际修改的是 Simulator 对象 Sim）。

```
Sim.FinalEpoch          = '09 Sep 2015 00:00:00.000';
Sim.AddNoise            = On;
Sim.MeasurementTimeStep = 3600;
```

**中文说明**：仿真结束历元延至 2015-09-09（三周），开启噪声，测量时间步长改为 3600 秒。

注意，上面除了实现所需的两个步骤外，我们还将测量时间步长从 600 秒改为 3600 秒。这不是真实的步长，因为许多任务可能使用甚至小于 600 秒的步长。我们使用这个较大的步长仅出于教程目的，以便脚本运行不会太久。

包含我们在本节中所做全部更改的完整脚本在文件 `Tut_Simulate_DSN_Range_and_Doppler_Data_3_weeks.script` 中。注意，在此文件中，除上述更改外，我们还将 GMD 输出文件名改为 `Simulate DSN Range and Doppler Data 3 weeks.gmd`。

现在运行脚本，由于生成的数据比以前多得多，大约需要 2-3 分钟。我们将把在此创建的 GMD 文件用作下一个教程**使用 DSN 测距与多普勒数据进行轨道估计**中将构建的估计脚本的输入。
