# 使用 DSN 测距与多普勒数据进行轨道估计（Orbit_Estimation_using_DSN_Range_and_Doppler_Data）

> 译自 GMAT R2026a 帮助文档 Orbit_Estimation_using_DSN_Range_and_Doppler_Data.html

**第 14 章 使用 DSN 测距与多普勒数据进行轨道估计**

- **适用读者**：中级水平
- **时长**：60 分钟
- **先修内容**：仿真 DSN 测距与多普勒数据教程（Simulate DSN Range and Doppler Data Tutorial）
- **脚本文件**：`Tut_Orbit_Estimation_using_DSN_Range_and_Doppler_Data.script`

## 目标与概述

> **注意**：GMAT 目前实现了多种用于轨道确定的数据类型。GMAT 目前支持的所有测量类型的细节请参见《轨道确定的跟踪数据类型》（Tracking Data Types for Orbit Determination）。此处考虑的测量量是 DSN 双向测距和 DSN 双向多普勒测速。

在本教程中，我们将使用 GMAT 读入一艘环绕太阳运行的示例航天器的仿真 DSN 测距和多普勒测量数据，并确定其轨道。该航天器处于一条距太阳约 1 AU、距地球近 3 亿 km 的地球"漂移远离"型轨道。本教程与"仿真 DSN 测距与多普勒数据教程"有许多相似之处，因为大多数相同的 GMAT 资源都需要创建和配置。但 GMAT 使用这些资源的方式存在差异，我们将在讲解过程中指出。

本教程的基本步骤为：

1. 创建并配置航天器、航天器应答机及相关参数
2. 创建并配置地面站及相关参数
3. 定义要处理的测量类型
4. 创建并配置力模型和积分器
5. 创建并配置批处理估计器（BatchEstimator）对象
6. 运行任务并分析结果

注意，本教程与大多数任务设计教程不同，将完全基于脚本。这是因为大多数与导航相关的资源和命令未在 GUI 中实现，只能通过脚本接口使用。

在学习下面的教程时，建议您边学边将脚本片段粘贴到 GMAT 中。每次粘贴到 GMAT 后，应点击 Save, Sync 按钮进行语法检查。为避免语法错误，在需要时不要忘记在您正在检查的脚本片段的最后一行添加以下命令：

```
BeginMissionSequence
```

**中文说明**：在脚本片段末尾加上 BeginMissionSequence 以便通过语法检查。

请注意，除了此处介绍的内容外，您还应查阅我们在此创建和使用的所有对象和命令的单独帮助资源。例如，`Spacecraft`、`Transponder`、`Transmitter`、`GroundStation`、`ErrorModel`、`TrackingFileSet`、`RunEstimator` 等都有各自的帮助页面。

## 本教程包含的小节

- 创建并配置航天器、航天器应答机及相关参数
  - 创建卫星并设置其历元和笛卡尔坐标
  - 创建应答机（Transponder）对象并挂接到航天器
- 创建并配置地面站及相关参数
  - 创建地面站发射机、接收机和天线对象
  - 创建地面站
  - 创建地面站误差模型
- 定义要处理的测量类型
- 创建并配置力模型和积分器
- 创建并配置批处理估计器对象
- 运行任务并分析结果
  - 消息窗口输出
  - 观测残差图
  - 批处理估计器输出报告
  - Matlab 输出文件
- 参考文献
- 附录 A —— GMAT 消息窗口输出
- 附录 B —— 第 0 次迭代的观测残差图
- 附录 C —— 第 1 次迭代的观测残差图
- 附录 D —— 修改脚本以使用地面网（GN）数据
