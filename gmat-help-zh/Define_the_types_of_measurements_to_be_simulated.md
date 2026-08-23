# 定义要仿真的测量类型（Define_the_types_of_measurements_to_be_simulated）

> 译自 GMAT R2026a 帮助文档 Define_the_types_of_measurements_to_be_simulated.html

（本小节属于"第 13 章 仿真 DSN 测距与多普勒数据"教程）

现在我们将创建并配置一个 `TrackingFileSet` 资源。此资源定义要仿真的数据类型、将使用的地面站，以及将包含仿真数据的输出 GMD 文件的文件名。此外，`TrackingFileSet` 资源将定义各种数据类型所需的仿真参数。

```
Create TrackingFileSet DSNsimData;
DSNsimData.AddTrackingConfig        = {{CAN, Sat, CAN}, 'DSN_SeqRange'};   
DSNsimData.AddTrackingConfig        = {{CAN, Sat, CAN}, 'DSN_TCP'};                 
DSNsimData.FileName                 = ...
                     {'Sat_dsn_range_and_doppler_measurements.gmd'};

DSNsimData.UseLightTime             = true;
DSNsimData.UseRelativityCorrection  = true;
DSNsimData.UseETminusTAI            = true;

DSNsimData.SimDopplerCountInterval  = 10.0;
DSNsimData.SimRangeModuloConstant   = 3.3554432e+07;
```

**中文说明**：创建跟踪文件集 DSNsimData，配置 CAN 站对 Sat 的 DSN_SeqRange 和 DSN_TCP 两种测量，指定输出 GMD 文件，开启光行时、相对论和 ET-TAI 修正，多普勒计数区间 10 秒，测距模常数 33554432。

上面的脚本行分为三个部分。第一部分声明资源名 `DSNsimData`，定义数据类型，并指定输出文件名。`AddTrackingConfig` 是用于定义数据类型的字段。第一条 `AddTrackingConfig` 行告诉 GMAT 仿真 CAN 到 Sat 到 CAN 测量链路的 DSN 双向测距测量。第二条 `AddTrackingConfig` 行告诉 GMAT 仿真 CAN 到 Sat 到 CAN 测量链路的 DSN 双向多普勒测量。

上面第二部分设置一些同时适用于测距和多普勒测量的仿真参数。我们将 `UseLightTime` 设为 True，以生成 GMAT 考虑光速有限性的真实测量。本节的最后两个参数 `UseRelativityCorrection` 和 `UseETminusTAI` 设为 True，以便将 Moyer [2000] 中描述的广义相对论修正施加于光行时方程。

上面第三部分设置适用于特定测量类型的仿真参数。`SimDopplerCountInterval` 仅适用于多普勒测量，`SimRangeModuloConstant` 仅适用于测距测量。注意，字段名中的"Sim"用于表明这些字段仅在 GMAT 处于仿真模式（即使用 `RunSimulator` 命令）时适用，在 GMAT 处于估计模式（即使用 `RunEstimator` 命令）时不适用。`SimDopplerCountInterval`（多普勒计数区间）设为 10 秒，`SimRangeModuloConstant`（最大可能测距值）设为 33554432。这些参数如何用于计算测量值的描述请参见 `RunSimulator` 帮助和"附录 A —— 测量噪声值的确定"。
