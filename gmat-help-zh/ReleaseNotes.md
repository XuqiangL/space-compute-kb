# 发行说明（ReleaseNotes）

> 译自 GMAT R2026a 帮助文档 ReleaseNotes.html

本页为 GMAT 各版本发行说明的索引，并包含最新版本 R2026a 的发行说明。历史版本发行说明见对应文件：R2025a、R2022a、R2020a、R2018a、R2017a、R2016a、R2015a、R2014a、R2013b、R2013a、R2012a、R2011a。

## GMAT R2026a 发行说明

GMAT R2026a 于 2026 年 4 月发布，是本项目的第 16 个版本。上一个公开版本发布于 2025 年 4 月。这是一个重要的项目版本，在通用能力与模型、任务设计与轨道确定功能、可视化以及跨平台兼容性方面包含大量改进和增强。

以下为本版本关键变更摘要。

### 里程碑与成就

GMAT 在业务任务支持中的应用持续增长，令人振奋：

- GMAT 被 SOLAR-1（Space weather Observations at L1 to Advance Readiness – 1）飞行动力学团队用作机动规划的主要业务工具。
- GMAT 被罗曼空间望远镜（RST）飞行动力学团队用作机动规划的主要业务工具。
- GMAT 轨道确定是 NASA GSFC 飞行动力学设施（FDF）用于支持 LEO、GEO、月球、拉格朗日点及其他轨道领域各类任务的主要工具。

GMAT 发布史上首次：https://github.com/nasa/GMAT GitHub 仓库将很快用于在下一个公开版本之前向用户分发选定的代码更新。

### 主要改进与增强

#### 通用能力与模型

以下为 R2026a 新增的通用能力：

- **在所有太阳系天体上启用指数大气**（GMT-8449、GMT-8160）：GMAT 的阻力建模现在可以对任何太阳系天体的大气建模，使用基于 David Vallado《Fundamentals of Astrodynamics and Applications》中指数阻力模型的指数模型。用户需要提供包含模型系数的文件，发行版 data/atmosphere 文件夹中有地球和火星的示例文件。示例见应用程序 samples 目录中的 `Ex_ForceModels.script`。
- **升级星下点轨迹组件，使其可扩展并支持 macOS**（GMT-8451、GMT-8507）：GMAT 的 GroundTrackPlot 组件已被自定义的 GroundTrack 组件取代。新组件的脚本编写方式与旧组件完全相同，在脚本中以对象名 GroundTrack 标识。以 GroundTrackPlot 为对象类型创建的脚本现在会创建替代组件而非旧类型。GroundTrack 对象会完全填满其窗口，而不再保持 2:1 的宽高比。
- **将 MSISE-00 大气模型加入公开版本**（GMT-8487）：GMAT 现在包含 2001 年美国海军研究实验室质谱仪与非相干散射雷达外层大气（NRLMSISE00）大气模型，用于阻力建模。示例见 samples 目录中的 `Ex_ForceModels` 脚本。
- **用 OpenFramesInterface（OFI）替代 OrbitView**（GMT-8322）：GMAT 通过新的默认 libOVtoOFI 插件，自动把 OrbitView 3D 可视化对象映射到 OpenFramesInterface 窗口。OrbitView 已弃用并可能在未来版本中移除，但用户目前可在启动文件中禁用 libOVtoOFI 插件以继续使用已弃用的 OrbitView。
- **更新 SPICE 输入读写器以正确处理 MJ2000Eq 和 ICRF 坐标系**（GMT-5211、GMT-8468、GMT-8300）：GMAT 现在会把 SPICE 行星历表文件和其他 SPICE 历表文件正确解释为 ICRF，并在写 SPICE 文件时把状态转换到 ICRF。因此，用户可能会注意到计算结果有轻微差异，包括使用多点质量的传播、轨道确定以及涉及平移到其他天体的坐标转换。
- **修复 Lagrange 插值器对中间点和升序/降序数据的处理**（GMT-8443）：更新了内嵌的 Lagrange 插值器，可正确插值自变量（如星历的时间或质心文件的质量）为升序或降序的数据。
- **当用户指定不存在的启动文件时报错并退出**（GMT-7802）：使用 –startup_file 命令行参数时，如果指定的启动文件不存在，GMAT 会报错并退出。
- **为 SRP 阴影计算启用第三体**（GMT-6543、GMT-8403）：新增 ForceModel 参数 SRP.ExtraShadowBodies，可用于对除力模型中心天体（中心天体始终纳入阴影建模）之外的天体造成的 SRP 阴影效应建模。示例见 samples 目录中的 `Ex_ForceModel_ExtraShadowBodies` 脚本。
- **重构 ShadowState 代码**（GMT-8077）：与阴影百分比计算相关的 GMAT 代码已重构，更易维护。
- **增加用户在任务序列中可 "Get" 的参数**（GMT-8111、GMT-8363）：虽然 GMAT 允许用户在任务序列开始前配置资源对象（如 Spacecraft、Propagator、DC、Optimizers、Impulsive 或 FiniteBurns）参数，但用户此前无法在任务序列中获取所有这些对象参数。本工作扩展了用户在任务序列运行期间可检索的参数，受影响参数详见 GMT-8111 和 GMT-8363。
- **推广入侵定位器（Intrusion Locator）的使用**（GMT-7572、GMT-8332、GMT-8482）：GMAT R2022a 引入的入侵定位器已增强，允许对非模型中心天体的天体进行传感器入侵计算。该能力可计算航天器所见的凌日和掩星。示例见 samples 目录中的 `Ex_IntrusionLocator_Mercury_Sun_Transit` 脚本。
- **修复地面站掩膜文件 NAIF ID 冲突问题**（GMT-8416）：ContactLocator 中地面站所用 FOV 参考架的内部 NAIF ID 生成已更新，确保使用大量地面站时 ID 唯一，防止 SPICE 中一个 FOV 因 ID 相同被另一个覆盖。
- **为段内步数少于插值阶数时的星历生成添加逻辑**（GMT-8238）：GMAT 的星历传播代码现在会降低状态插值器的阶数，以匹配每个星历段中可用的点数，从而为点数不足以满足脚本指定插值阶数的段生成插值状态。当插值使用的点数少于脚本指定插值所需点数时，GMAT 会在消息窗口发布消息，指明该段及该段使用的插值阶数。
- **更新 CSALT 接口脚本并添加教程**（GMT-8298）：新增指导内容，向用户展示如何在 Visual Studio 中创建 CSALT 项目，介绍使用该工具必须继承的主要 CSALT C++ 基类，并提供六个示例教程。每个教程依次增加可用于创建和求解最优控制问题的 CSALT 特性。
- **添加内置四元数函数**（GMT-8110、GMT-8371）：GMAT 新增三个四元数函数：QuaternionRotation、QuaternionProduct 和 QuaternionToDCM。用法见用户指南。
- **增强使用 SPICE 进行坐标系转换的能力**（GMT-8255、GMT-8300）：现在可以通过使用 SPICE Axes 类型创建坐标系，在 GMAT 中使用 SPICE 工具包中定义的参考架。有用的例子包括月球主轴（PA）和平均地球（ME）参考架，其他天体的 IAU 参考架也可以通过指定相应内核来定义和使用。示例见 samples 目录中的 `Ex_SPICECoordinateAxes` 脚本。
- **更新帮助系统，用 .html 取代 .chm 文件**（教程/用户指南）（GMT-8500）：以前版本的 GMAT 使用编译 HTML 帮助（CHM）文件，但该文件格式已过时且不受支持，因此今后的 GMAT 版本将指向所提供的 HTML 文件。

##### Beta 和 Alpha 级能力

这些是尚未经过完整测试、可能存在 bug 的新功能。要访问其中某些功能，你可能需要编辑 `bin/gmat_startup_file.txt` 文件以加载所需的 alpha 插件，和/或激活仅在测试模式下可用的功能（在文件中设置 RUN_MODE = TESTING）。这些功能应谨慎使用。

- 用于 UTDF 单向下行链路距离变化率跟踪的 Python GMD 编写器（GMT-8228、GMT-8229）：位于 "\utilities\python\navigation\utdf_to_gmd.py" 的 Python 工具已更新，新增对单向下行链路距离变化率跟踪的支持。该工具读取原始 UTDF 跟踪数据并转换为 GMAT 可摄取的 GMD 格式。

#### 导航与轨道确定（OD）

R2026a 新增的导航与轨道确定能力：

- 轨道确定（导航）的新业务数据类型：
  - GN/DTE 单向下行链路距离变化率跟踪（GMT-8226、GMT-8227）：GMAT 现在支持以 km/sec 为单位的单向下行链路距离变化率测量用于轨道确定。这在现有双向、三向 RangeRate 测量之外，把现有 RangeRate 数据类型扩展到单向下行链路 RangeRate。示例见 samples/Navigation 目录中的 `Ex_Estimate_RangeRangeRate` 脚本。
- 批估计器报告主机名值无法识别（GMT-8275）：在某些情况下，GMAT 主机名未能正确显示在估计器报告文件中。现在与计算机主机名关联的文本已能正确打印到估计器报告文件中。
- 改进导航电离层建模性能（GMT-8459、GMT-8168）：把原先的 FORTRAN 转 C（f2c）电离层代码重构，提高使用电离层校正计算时的速度。

R2026a 中发生变化的导航与轨道确定能力：

- 修正了内层循环数据编辑方案中的一个 bug（GMT-7281）：影响批估计器内层循环编辑方案的 bug 已修正。BatchEstimator 内层循环现在可正常工作。用户可能会发现内层循环编辑器可通过减少收敛所需迭代次数来缩短估计运行时间。

自 R2026a 起弃用的导航与轨道确定能力：无。

#### 脚本与 API 接口

R2026a 中实现的脚本与 API 接口变更：

- 以下参数已被禁止在任务序列（MissionSequence）中设置：NAIFIdReferenceFrame、SPADSRPInterpolationMethod、SPADDragInterpolationMethod、ModelFile、ModelOffsetX、ModelOffsetY、ModelOffsetZ、ModelRotationX、ModelRotationY、ModelRotationZ、ModelScale、NAIFId、Id。

#### 最优控制

GMAT 最优控制能力在 R2026a 中仍为 Beta 功能。

#### OpenFramesInterface 可视化

> **注意**：OFI 继续作为 GMAT 中的主要 3D 可视化组件。`OrbitView` 已弃用，将不再受支持。建议用户把脚本从 `OrbitView` 迁移到 `OpenFramesInterface`。

OFI 的完整文档见 OFI Wiki（https://gitlab.com/EmergentSpaceTechnologies/OpenFramesInterface/-/wikis/home）。

### 其他改进

- 修正问题 GMT-8427：OpenFramesInterface 新建 Vector 视图面板不能正确调整大小。
- 修正问题 GMT-8355：OpenFramesView 面板显示不正确。
- 启用 OpenFramesInterface 字体选项（GMT-8536）。
- 修正问题 GMT-6571：首次运行被中断后，SystemTime() 在重新运行时失败。

### 兼容性变更

- 启用对 Mac Intel 机器的支持（GMT-8340）：在 macOS 上，GMAT 现在以通用应用程序分发。由于第三方依赖限制（如 MATLAB 接口），未来的 GMAT Mac 应用程序可能不再完全支持 Intel 芯片组。
- 修复 Mac 应用程序的公证（notarization）（GMT-8339）。
- 由于 WxWidgets 限制，GUI 项在高 DPI 显示器上无法缩放（变通方案）（GMT-6125）。
- 更新 SWIG 到当前版本（GMT-8299）。
- 更新构建系统以使用 CMake 4（GMT-8434）。
- 解决 OSG 插件缺失问题（GMT-8242/GMT-8523）。
- 在依赖配置中移除或重新配置 PCRE（GMT-8530）。
- 已停止对 Python 3.6 至 3.8 的支持。

### 已修复与已知问题

#### 已修复问题

本版本关闭了 29 个高优先级 bug。详见 "Critical Issues Fixed in R2026a" 报告。R2026a 中一些重要修复包括：

| ID | 描述 |
| --- | --- |
| GMT-8357 | Linux 上的 GMAT 崩溃，外部力模型脚本的报告生成失败 |
| GMT-8160 | 火星指数大气无效果 |

#### 已知问题

所有已知主要问题见 "All Known Critical Issues for R2026a" 报告。本版本中有几个我们认为重要的已知问题：

| ID | 描述 |
| --- | --- |
| GMT-8024 | 可能出现 Windows Defender 弹窗，阻止用户首次打开 GMAT 应用程序，需要额外的用户操作 |