# 定义要处理的测量类型（DSN_Estimation_Define_the_types_of_measurements_that_will_be_processed）

> 译自 GMAT R2026a 帮助文档 DSN_Estimation_Define_the_types_of_measurements_that_will_be_processed.html

现在我们将创建并配置一个 `TrackingFileSet` 资源。此资源定义要处理的数据类型、将使用的地面站，以及包含测量数据的输入 GMD 文件的文件名。注意，为了直接从仿真教程复制粘贴，我们将资源命名为 `DSNsimData`。但由于在此脚本中我们是在估计，也许 `DSNestData` 会是更好的名字。

```
Create TrackingFileSet DSNsimData;
DSNsimData.AddTrackingConfig         = {{CAN, Sat, CAN}, 'DSN_SeqRange'};   
DSNsimData.AddTrackingConfig         = {{CAN, Sat, CAN}, 'DSN_TCP'};                 
DSNsimData.AddTrackingConfig         = {{GDS, Sat, GDS}, 'DSN_SeqRange'};   
DSNsimData.AddTrackingConfig         = {{GDS, Sat, GDS}, 'DSN_TCP'};                 
DSNsimData.AddTrackingConfig         = {{MAD, Sat, MAD}, 'DSN_SeqRange'};   
DSNsimData.AddTrackingConfig         = {{MAD, Sat, MAD}, 'DSN_TCP'};                 
DSNsimData.FileName                  = ...
      {'../output/Simulate DSN Range and Doppler Data 3 weeks.gmd'};
DSNsimData.RampTable                 = ... 
      {'../output/Simulate DSN Range and Doppler Data 3 weeks.rmp'};

DSNsimData.UseLightTime              = true;
DSNsimData.UseRelativityCorrection   = true;
DSNsimData.UseETminusTAI             = true;
```

**中文说明**：创建跟踪文件集 DSNsimData，为三个地面站（CAN、GDS、MAD）各配置 DSN_SeqRange 和 DSN_TCP 两种测量类型，指定输入 GMD 文件和斜坡表文件，并开启光行时、相对论修正和 ET-TAI 修正。

上面的脚本行分为三个部分。第一部分声明资源名 `DSNsimData`，定义数据类型，并指定输入 GMD 文件和斜坡表名称。`AddTrackingConfig` 是用于定义数据类型的字段。第一条 `AddTrackingConfig` 行告诉 GMAT 处理 CAN 到 Sat 到 CAN 测量链路的 DSN 双向测距测量。第二条 `AddTrackingConfig` 行告诉 GMAT 处理 CAN 到 Sat 到 CAN 测量链路的 DSN 双向多普勒测量。其余 4 条 `AddTrackingConfig` 脚本行告诉 GMAT 也处理 GDS 和 MAD 的测距和多普勒测量。注意，我们指定的输入 GMD 和斜坡表文件是我们在**仿真 DSN 测距与多普勒数据教程**中创建的文件。不要忘记将这些文件放在 GMAT "output" 目录中。

上面第二部分设置一些同时适用于测距和多普勒测量的处理参数。我们将 `UseLightTime` 设为 True，以生成考虑光速有限性的真实计算测量值 C。本节的最后两个参数 `UseRelativityCorrection` 和 `UseETminusTAI` 设为 True，以便将 Moyer [2000] 中描述的广义相对论修正施加于光行时方程。

注意，在仿真教程中，我们设置了另外两个 `DSNsimData` 字段 `SimDopplerCountInterval` 和 `SimRangeModuloConstant`。由于这些字段仅适用于仿真，此处无需设置，因为它们的值只会被忽略。
