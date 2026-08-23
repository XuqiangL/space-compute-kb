# 运行任务并分析结果（Run_the_mission_and_analyze_the_results）

> 译自 GMAT R2026a 帮助文档 Run_the_mission_and_analyze_the_results.html

（本小节属于"第 13 章 仿真 DSN 测距与多普勒数据"教程）

用于运行任务的脚本片段如下所示。

```
BeginMissionSequence
 
RunSimulator Sim
```

**中文说明**：BeginMissionSequence 标志命令段开始，RunSimulator Sim 用测量仿真器 Sim 执行仿真。

第一行脚本 `BeginMissionSequence` 是必需命令，表示 GMAT 脚本的"命令"部分已开始。第二行脚本发出 `RunSimulator` 命令，以"创建并配置测量仿真器对象"一节中定义的 `Sim` Simulator 资源为参数。这告诉 GMAT 执行 `Sim` 资源指定的仿真。

我们现在已完成所有脚本片段。完整脚本清单请参见 GMAT samples 文件夹中的 `Tut_Simulate_DSN_Range_and_Doppler_Data.script` 文件。现在可以运行脚本了。点击 Save,Sync,Run 按钮。由于我们只仿真少量数据，脚本应在约一秒内执行完毕。

让我们看看创建的输出。创建的文件 `Sat_dsn_range_and_doppler_measurements.gmd` 在我们在"定义要仿真的测量类型"一节中创建的 `TrackingFileSet` 资源 `DSNsimData` 中指定。如果未指定目录，默认目录是 GMAT 'output' 目录。让我们分析这个"GMAT 测量数据"（GMD）文件的内容，如下所示。

```
% GMAT Internal Measurement Data File

27253.5004166666666666666665    DSN_SeqRange    9004    22222    11111    2.6025689337646484e+07    2    7.200000000000000e+09    3.355443200000000e+07
27253.5004166666666666666665    DSN_TCP    9006    22222    11111    2    10    -8.4593363231570539e+09
27253.5073611111111111115728    DSN_SeqRange    9004    22222    11111    2.1736962852050781e+07    2    7.200000000000000e+09    3.355443200000000e+07
27253.5073611111111111115728    DSN_TCP    9006    22222    11111    2    10    -8.4593356106484509e+09
```

**中文说明**：GMD 文件示例——两个时刻各一对记录：DSN_SeqRange 序列测距（类型码 9004，观测值以测距单位计）和 DSN_TCP 总计数相位导出多普勒（类型码 9006，观测值以 Hz 计）。

文件第一行是注释行，表明这是以 GMAT 内部格式存储测量数据的文件。有 4 行数据，代表两个连续时刻的测距数据和两个连续时刻的多普勒数据。如预期，我们总共不超过 4 个测量。测距和多普勒 GMD 文件格式的描述请参见《轨道确定的跟踪数据类型》帮助。

我们现在分析第一行数据，它代表仿真开始时 '19 Aug 2015 00:00:00.000 UTCG' 的 DSN 双向测距测量，对应输出的 TAI 约化儒略日 27253.500416666... TAIMJD。

第二和第三字段 DSN_SeqRange 和 9004 只是 GMAT 内部代码，表示使用 DSN 测距（Trk 2-34 类型 7）数据。

第 4 字段 22222 是下行站 ID。这是我们在"创建并配置地面站及相关参数"一节中给创建的 `CAN` `GroundStation` 对象的 ID。第 5 字段 11111 是航天器 ID。这是我们在"创建并配置航天器、航天器应答机及相关参数"一节中给 `Sat` `Spacecraft` 对象的 ID。

第 6 字段 2.6025689337646484e+07 是实际的 DSN 测距观测值（RU）。

第 7 字段 2 是整数，代表上行 `GroundStation` `CAN` 的上行频段。代号 2 代表 X 频段。GMAT 如何确定此处应写值的详细讨论请参见 `RunSimulator` 帮助。如帮助中所述，由于我们不使用斜坡表，GMAT 通过查看挂接到 `CAN` 地面站的 `Transmitter` 对象的发射频率来确定上行频段。GMAT 知道我们赋给 `CAN` 的 `Transmitter` 资源 `DSNTransmitter` 的 7200 MHz 值对应 X 频段频率。

第 8 字段 7.2e+009 是测量时刻 `CAN` 的发射频率。由于我们不使用斜坡表，此值对所有测量都是恒定的，由我们挂接到 `CAN` 地面站的 `Transmitter` 对象 `DSNTransmitter` 的频率值给出。回想"创建并配置地面站及相关参数"一节中的脚本片段 `DSNTransmitter.Frequency = 7200; %MHz`。

第 9 字段 3.3554432e+07 代表帮助定义 DSN 测距测量的整数测距模数。这是我们在"定义要仿真的测量类型"一节中创建和配置 `TrackingFileSet` `DSNsimData` 对象时设置的值。回想以下脚本命令：

```
                 DSNsimData.SimRangeModuloConstant = 3.3554432e+07;
```

**中文说明**：测距模常数设为 33554432 测距单位。

此测距模数在"附录 A —— 测量噪声值的确定"中讨论，定义为 M，即以 RU 计的测距码长度。

我们现在分析第二行数据，它代表仿真开始时 '19 Aug 2015 00:00:00.000 UTCG' 的 DSN 双向多普勒测量，对应输出的 TAI 约化儒略日 27253.500416666... TAIMJD。

第二和第三字段 Doppler 和 9006 只是 GMAT 内部代码，表示使用 DSN 多普勒（由两个连续 Trk 2-34 类型 17 总计数相位测量导出）数据。

第 4 字段 22222 是下行站 ID。这是我们在"创建并配置地面站及相关参数"一节中给 CAN GroundStation 对象的 ID。第 5 字段 11111 是航天器 ID。这是我们在"创建并配置航天器、航天器应答机及相关参数"一节中给 `Sat` `Spacecraft` 对象的 ID。

第 6 字段 2 是整数，代表上行 `GroundStation` `CAN` 的上行频段。如讨论测距测量时所述，代号 2 代表 X 频段。

第 7 字段 10 是用于帮助定义多普勒测量的多普勒计数区间（DCI）。这是我们在"定义要仿真的测量类型"一节中创建和配置 `TrackingFileSet` `DSNsimData` 对象时设置的值。回想以下脚本命令：

```
                DSNsimData.SimDopplerCountInterval = 10.0;
```

**中文说明**：多普勒计数区间设为 10 秒。

DCI 也在"附录 A —— 测量噪声值的确定"中讨论。

第 8 字段 -8.4593363231570539e+09 是实际的 DSN 多普勒观测值（Hz）。

第三行数据代表 '19 Aug 2015 00:10:00.000 UTCG' 的第二个 DSN 双向测距测量，对应输出的 TAI 约化儒略日时刻 27253.507361111... TAIMJD。第四行数据代表 '19 Aug 2015 00:10:00.000 UTCG' 的第二个 DSN 双向多普勒测量。
