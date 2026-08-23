# 第 13 章 仿真 DSN 测距与多普勒数据（Simulate DSN Range and Doppler Data）
> 译自 GMAT R2026a 帮助文档 Tut_Simulate_DSN_Range_and_Doppler_Data.html

| 项目 | 内容 |
| --- | --- |
| 适用读者（Audience） | 中级 |
| 时长（Length） | 40 分钟 |
| 先修要求（Prerequisites） | 基础任务设计教程 |
| 脚本文件（Script Files） | `Tut_Simulate_DSN_Range_and_Doppler_Data.script`、`Tut_Simulate_DSN_Range_and_Doppler_Data_3_weeks.script` |

## 本章目录

- 目标与概述（本节）
- [创建并配置航天器、航天器转发器及相关参数](Create_and_configure_the_spacecraft_spacecraft_transponder_and_related_parameters.md)
- [创建并配置地面站及相关参数](Create_and_configure_the_Ground_Station_and_related_parameters.md)
- [定义待仿真的测量类型](Define_the_types_of_measurements_to_be_simulated.md)
- [创建并配置力模型与传播器](Create_and_configure_Force_model_and_propagator.md)
- [创建并配置测量仿真器（Simulator）对象](Create_and_configure_Simulator_object.md)
- [运行任务并分析结果](Run_the_mission_and_analyze_the_results.md)
- [创建更真实的 GMAT 测量数据（GMD）文件](Create_Realistic_GMD.md)
- [参考文献](ch13s09.md)
- [附录 A —— 测量噪声值的确定](Appendix_A_Determination_of_Measurement_Noise_Values.md)

## 目标与概述（Objective and Overview）

> **注意**
>
> GMAT 目前为轨道确定实现了多种不同的数据类型。关于 GMAT 当前支持的所有测量类型的详细信息，请参阅《用于轨道确定的跟踪数据类型（Tracking Data Types for Orbit Determination）》。本教程考虑的测量是 DSN 双向测距（two way range）和 DSN 双向多普勒测速（two way Doppler）。

在本教程中，我们将使用 GMAT 为一颗绕太阳运行的示例航天器生成仿真的 DSN 测距（Range）与多普勒（Doppler）测量数据。本教程中的航天器位于一条绕太阳的地球“漂离（drift away）”型轨道上，距太阳约 1 AU，距地球接近 3 亿 km。

本教程的基本步骤如下：

1. 创建并配置航天器、航天器转发器（transponder）及相关参数。
2. 创建并配置地面站（Ground Station）及相关参数。
3. 定义待仿真的测量类型。
4. 创建并配置力模型（Force model）与传播器（propagator）。
5. 创建并配置测量仿真器（Simulator）对象。
6. 运行任务并分析结果。
7. 创建一个真实的 GMAT 测量数据（GMAT Measurement Data，GMD）文件。

请注意，与大多数任务设计教程不同，本教程将完全基于脚本。这是因为大多数与导航（navigation）相关的资源和命令尚未在 GUI 中实现，只能通过脚本接口使用。

在学习下面的教程时，建议你边学边把脚本片段粘贴到 GMAT 中。每次粘贴后，都应点击 Save, Sync（保存并同步）按钮进行一次语法检查。为避免语法错误，在需要时，别忘了在你正在检查的脚本片段的最后一行添加以下命令：

```
BeginMissionSequence
```

**说明：** `BeginMissionSequence` 是 GMAT 脚本中标志任务序列（Mission Sequence）开始的命令。在分段粘贴脚本做语法检查时补上这一行，可以让 GMAT 正确解析仅含资源定义的片段，避免误报语法错误。

我们还要指出，除了这里介绍的内容外，你还应查阅本教程中创建和使用的所有对象与命令各自的帮助资源页面。例如，`Spacecraft`（航天器）、`Transponder`（转发器）、`Transmitter`（发射机）、`GroundStation`（地面站）、`ErrorModel`（误差模型）、`TrackingFileSet`（跟踪文件集）、`RunSimulator` 等都有各自的帮助页面。
