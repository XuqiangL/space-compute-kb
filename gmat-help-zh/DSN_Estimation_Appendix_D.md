# 附录 D —— 修改脚本以使用地面网（GN）数据（DSN_Estimation_Appendix_D）

> 译自 GMAT R2026a 帮助文档 DSN_Estimation_Appendix_D.html

**附录 D —— 修改脚本以使用地面网（GN）数据**

在本教程中，我们使用 DSN 数据进行了估计。在本附录中，我们看看如何修改上一教程中的仿真脚本 `Tut_Simulate_DSN_Range_and_Doppler_Data_3_weeks.script` 和本教程中的估计脚本 `Tut_Orbit_Estimation_using_DSN_Range_and_Doppler_Data.script`，以便处理 GN 数据而非 DSN 数据。注意，这两个脚本都可以在 GMAT "samples" 文件夹中找到。这些教程使用了与 DSN 数据相符的深空航天器状态。在下面的讨论中，我们将使用相同的航天器状态，尽管 GN 数据类型通常用于更靠近地球的航天器。

在下面的讨论中，我们将注释掉使用 DSN 数据的旧命令，替换为使用 GN 数据的新命令。首先从仿真脚本开始。在下文中，我们将继续使用先前创建的对象名，尽管对象名可能不再准确。例如，在仿真脚本中，我们创建了一个 `Antenna` 对象 `DSNAntenna`。我们将继续使用这个对象名，尽管显然 `GNAntenna` 会是更好的名字。先考虑航天器和地面站电子设备。对于 GN，通常使用 S 频段。我们修改航天器应答机转发比和地面站发射机频率的值以反映这一点。

```
SatTransponder.TurnAroundRatio = '240/221';       % was '880/749';

DSNTransmitter.Frequency       = 2067.5;   %MHz.  % was 7200
```

**中文说明**：应答机转发比从 X 频段的 880/749 改为 S 频段的 240/221；发射机频率从 7200 MHz 改为 2067.5 MHz。

现在考虑挂接到 3 个 `GroundStation` 对象、用于描述 DSN 噪声特性的 `ErrorModel` 对象。由于现在使用 GN，必须修改 `ErrorModel` 以描述 GN 噪声特性。如下所示，测距 1-sigma 噪声设为 10 米，测距变率 1-sigma 噪声设为 1 cm/s。

```
DSNrange.Type             = 'Range'       % was 'DSN_SeqRange';
DSNrange.NoiseSigma       = 0.010;        % was 10.63;

DSNdoppler.Type           = 'RangeRate';  %was 'DSN_TCP';
DSNdoppler.NoiseSigma     = 0.00001;      %was 0.0282;
```

**中文说明**：测量类型从 DSN_SeqRange/DSN_TCP 改为 Range/RangeRate；测距噪声 sigma 从 10.63 改为 0.010 km（10 米），多普勒噪声 sigma 从 0.0282 改为 0.00001 km/s（1 cm/s）。

如下所示，我们需要告诉 GMAT 仿真 Range 和 RangeRate 数据，而不是 DSN_SeqRange 和 DSN_TCP 数据。

```
DSNsimData.AddTrackingConfig = {{CAN, Sat, CAN},'Range'};      %was 'DSN_SeqRange'
DSNsimData.AddTrackingConfig = {{CAN, Sat, CAN},'RangeRate'};  %was 'DSN_TCP'
DSNsimData.AddTrackingConfig = {{GDS, Sat, GDS},'Range'};      %was 'DSN_SeqRange'
DSNsimData.AddTrackingConfig = {{GDS, Sat, GDS},'RangeRate'};  %was 'DSN_TCP'
DSNsimData.AddTrackingConfig = {{MAD, Sat, MAD},'Range'};      %was 'DSN_SeqRange'
DSNsimData.AddTrackingConfig = {{MAD, Sat, MAD},'RangeRate'};  %was 'DSN_TCP'
```

**中文说明**：三个地面站（CAN、GDS、MAD）的跟踪配置都改为 Range 和 RangeRate 类型。

我们原来的仿真脚本使用斜坡表指定地面站发射频率。由于 GN 不使用斜坡表，如下所示，我们要注释掉读入斜坡文件的命令。为脚本清晰起见，我们还注释掉一条不适用于 GN 数据的命令。

```
%DSNsimData.RampTable  = ...
             {'../data/navdata/Simulate DSN Range and Doppler Data 3 weeks.rmp'};

%DSNsimData.SimRangeModuloConstant  = 3.3554432e+07;
```

**中文说明**：注释掉斜坡表文件设置和测距模常数设置（GN 数据不需要）。

完成对脚本 `Tut_Simulate_DSN_Range_and_Doppler_Data_3_weeks` 的上述所有修改后，将脚本另存为新名字，比如 `Simulate_GN_data`。然后运行这个新脚本。如我们从仿真教程所知，名为 `Simulate DSN Range and Doppler Data 3 weeks.gmd` 的文件将被写入本地 GMAT 安装的 "output" 文件夹。

现在我们来看估计脚本。打开教程中的估计脚本，另存为新名字，比如 `Estimation_GN_data`。与仿真脚本一样，我们修改航天器应答机转发比和地面站发射机频率的值，以反映我们使用的是 GN。

```
SatTransponder.TurnAroundRatio = '240/221';      % was '880/749';
DSNTransmitter.Frequency       = 2067.5;   %MHz.  % was 7200
```

**中文说明**：与仿真脚本相同的修改——S 频段转发比和发射频率。

与仿真脚本一样，我们配置 `ErrorModel` 对象以描述 GN 数据而非 DSN 数据。

```
DSNrange.Type             = 'Range'       % was 'DSN_SeqRange';
DSNrange.NoiseSigma       = 0.010;        % was 10.63;

DSNdoppler.Type           = 'RangeRate';  %was 'DSN_TCP';
DSNdoppler.NoiseSigma     = 0.00001;      %was 0.0282;
```

**中文说明**：误差模型改为 GN 的 Range/RangeRate 类型和相应噪声水平。

接下来，我们需要告诉 GMAT 使用 Range 和 RangeRate 数据进行估计，而不是 DSN_SeqRange 和 DSN_TCP 数据。注意，如果需要，下面的新行可以删除，脚本仍能工作。GMAT 会直接读入 GMD 文件并自动检测正在使用哪些地面站和数据类型。

```
DSNsimData.AddTrackingConfig = {{CAN, Sat, CAN},'Range'};      %was 'DSN_SeqRange'
DSNsimData.AddTrackingConfig = {{CAN, Sat, CAN},'RangeRate'};  %was 'DSN_TCP'
DSNsimData.AddTrackingConfig = {{GDS, Sat, GDS},'Range'};      %was 'DSN_SeqRange'
DSNsimData.AddTrackingConfig = {{GDS, Sat, GDS},'RangeRate'};  %was 'DSN_TCP'
DSNsimData.AddTrackingConfig = {{MAD, Sat, MAD},'Range'};      %was 'DSN_SeqRange'
DSNsimData.AddTrackingConfig = {{MAD, Sat, MAD},'RangeRate'};  %was 'DSN_TCP'
```

**中文说明**：跟踪配置改为 Range/RangeRate；这些行其实可省略，GMAT 会自动从 GMD 文件检测配置。

回想一下，我们新的 GN 仿真脚本配置为将 GMD 文件输出到 GMAT "output" 目录。让我们相应地修改将读入此文件的估计脚本。

```
% DSNsimData.FileName = {'../data/navdata/Simulate DSN Range and Doppler Data 3 weeks.gmd'};
DSNsimData.FileName   = {'../output/Simulate DSN Range and Doppler Data 3 weeks.gmd'};
```

**中文说明**：GMD 文件路径从 data/navdata 改为 output 目录。

与仿真脚本一样，我们注释掉读入斜坡表的行。

```
%DSNsimData.RampTable  = {'../data/navdata/Simulate DSN Range and Doppler Data 3 weeks.rmp'};
```

**中文说明**：注释掉斜坡表设置。

最后一步是运行我们新的 `Estimation_GN_data` 脚本，然后以与估计教程类似的方式分析结果。
