# 第 16 章 仿真与估计星间跟踪（Simulate and Estimate Inter-Spacecraft Tracking）
> 译自 GMAT R2026a 帮助文档 Tut_Simulate_and_Estimate_Inter_Spacecraft_DSN_Range_and_Doppler_Data.html

| 项目 | 内容 |
| --- | --- |
| 适用读者（Audience） | 中级 |
| 时长（Length） | 40 分钟 |
| 先修要求（Prerequisites） | 基础任务设计教程 |
| 脚本文件（Script Files） | `Tut_Inter_Spacecraft_Tracking.script` |

## 本章目录

- 目标与概述（本节）
- [创建并配置航天器、航天器硬件及相关参数](Create_and_configure_the_spacecraft_spacecraft_hardware_and_related_parameters.md)：创建仿真卫星与估计卫星并设置历元和笛卡尔坐标；创建 Transponder 并挂接到航天器；创建 Receiver 并挂接到测量航天器
- [定义待仿真的测量类型及其关联误差模型](Define_the_types_of_measurements_to_be_simulated_and_their_associated_error_models.md)：为仿真与估计分别定义 TrackingFileSet；创建测量误差模型
- [创建并配置力模型与传播器](Create_and_configure_force_model_and_propagator.md)
- [创建并配置测量仿真器与批处理估计器对象](Create_and_configure_simulator_and_batch_estimator_Objects.md)
- [运行任务并查看输出](Run_the_mission_and_analyze_the_output.md)：查看仿真测量；查看估计器结果
- [参考文献](ch16s07.md)

## 目标与概述（Objective and overview）

> **注意**
>
> GMAT 目前为轨道确定实现了多种不同的数据类型。关于 GMAT 当前支持的所有测量类型的详细信息，请参阅《用于轨道确定的跟踪数据类型（Tracking Data Types for Orbit Determination）》。本教程考虑的测量是双向测距（two way range）和距离变化率（range-rate）。

在本教程中，我们将使用 GMAT 生成两颗航天器之间的仿真测距（range）与距离变化率（range-rate）测量数据。其中一颗航天器称为跟踪航天器（tracking Spacecraft），它对另一颗航天器——称为被观测航天器（observed Spacecraft）——进行观测。跟踪航天器位于地球同步轨道，被观测航天器位于低地球轨道。随后，这些仿真测量将被用于对被观测航天器进行状态估计（state estimation）。

本教程的基本步骤如下：

1. 创建并配置航天器、航天器硬件及相关参数。
2. 定义待仿真的测量类型及其关联误差模型。
3. 创建并配置力模型（force model）与传播器（propagator）。
4. 创建并配置测量仿真器（simulator）与批处理估计器（batch estimator）对象。
5. 运行任务并查看结果。

请注意，与大多数任务设计教程不同，本教程将完全基于脚本。这是因为大多数与导航相关的资源和命令尚未在 GUI 中实现，只能通过脚本接口使用。

在学习下面的教程时，建议你边学边把脚本片段粘贴到 GMAT 中。每次粘贴后，都应点击 Save, Sync（保存并同步）按钮进行一次语法检查。为避免语法错误，在需要时，别忘了在你正在检查的脚本片段的最后一行添加以下命令：

```
BeginMissionSequence
```

**说明：** `BeginMissionSequence` 是 GMAT 脚本中标志任务序列（Mission Sequence）开始的命令。在分段粘贴脚本做语法检查时补上这一行，可以让 GMAT 正确解析仅含资源定义的片段，避免误报语法错误。

我们还要指出，除了这里介绍的内容外，你还应查阅本教程中创建和使用的所有对象与命令各自的帮助资源页面。例如，`Spacecraft`（航天器）、`Transponder`（转发器）、`Transmitter`（发射机）、`Receiver`（接收机）、`ErrorModel`（误差模型）、`TrackingFileSet`（跟踪文件集）、`RunSimulator` 等都有各自的帮助页面。
