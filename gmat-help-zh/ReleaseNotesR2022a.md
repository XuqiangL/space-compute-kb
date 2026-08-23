# GMAT R2022a 发行说明（ReleaseNotesR2022a）

> 译自 GMAT R2026a 帮助文档 ReleaseNotesR2022a.html

GMAT R2022a 于 2022 年 12 月发布。这是自 2020 年 5 月以来的第一个公开版本，是本项目的第 14 个版本。这是一个重要的项目版本，在通用能力与模型、导航与轨道确定、脚本与 API 接口、最优控制和可视化方面包含大量重大改进和增强。以下为本版本关键变更摘要。

## 里程碑与成就

- 使用 GPS 点解数据类型进行地基轨道确定的 NASA 低地轨道 Fermi 任务，于 2021 年 7 月开始在业务中使用 GMAT 的扩展卡尔曼滤波平滑器（EKFS）。

## 主要改进与增强

### 通用能力与模型

R2022a 新增的通用能力：

- 全面支持太阳辐射压（SRP）N 板（N-Plate）力建模（不再是 alpha/beta 级）。详见 ForceModel 一节。
- 能够生成地面站（G/S）到航天器的可见性报告，并可选指定地面站掩膜。详见 GroundStation 一节中的 `HorizonMaskFileName` 参数描述和"地面站掩膜文件"备注。另见 `samples/Ex_Contact_Location_Station_Mask.script`。
- 支持读写第 1 版 CCSDS 轨道星历消息（OEM）数据。使用 OEM 传播器详见 `Propagator` 资源的"CCSDS OEM 星历配置传播器"一节。另见 `samples/Ex_OEMPropagation.script`。
- 广义行面测地区域进出时间计算，包括南大西洋异常区（SAA）检测和报告。详见 PlanetographicRegion 资源一节。另见 `samples/Ex_PlanetographicRegion.script`。
- 库更新为 JPL 的新 CSPICE 067 版本。
- 使用 SPICE 第 67 版中 SGP4 传播器的 SPICE 实现进行两行根数（TLE）建模。见 `samples/Ex_TLE_Propagation.script`。

#### Beta 和 Alpha 级能力

这些是尚未经过完整测试、可能存在 bug 的新功能。要访问这些功能，你可能需要编辑 `bin/gmat_startup_file.txt` 文件以加载所需的 alpha 插件，和/或激活仅在测试模式下可用的功能（设置 RUN_MODE = TESTING）。这些功能应谨慎使用。

- Beta 级：传播和力报告期间多个全阶重力场扰动的力建模（多体球谐）。见 `samples/Ex_MultibodySphericalHarmonicGravity.script`。
- Beta 级：支持选定的力矩建模和入侵检测能力，重点关注地球同步轨道：
  - Beta 级：推力器、重力梯度和基于板的太阳辐射压力矩建模。详见"计算参数"（Calculation Parameters）一节。
  - Beta 级：向航天器模型添加质心和惯性矩。详见"航天器弹道/质量特性"（Spacecraft Ballistic/Mass Properties）一节。
  - Beta 级：入侵检测模型，用于确定太阳或月球何时进入传感器视场。详见 Intrusion Locator 一节。
- Alpha 级能力：给定 `Spacecraft` 的 GMAT `ForceModel` 可以使用 Python 函数替换或增强。见 `samples/Ex_ExternalForceModel.script`。

### 导航与轨道确定（OD）

为 R2022a 开发的导航与轨道确定能力：

- `ExtendedKalmanFilter` 和 `Smoother`（EKFS）资源现在可用于业务（不再是 alpha/beta 级）。在 GPS 点解数据类型上使用 EKFS 的示例见 `samples/Navigation/Ex_FilterSmoother_GpsPosVec.script`。与所有新版本一样，使用 GMAT 批处理和/或 EKFS 能力的任务在用于业务目的之前应执行基线回归/性能测试。
- 估计子系统现在支持（不再是 Beta）用于太阳辐射压（SRP）的 N 板面积模型。用户可以为预测和估计配置详细的多板面积模型进行 SRP 建模。该模型包括镜面反射和漫反射率，支持运动面板（如太阳帆板），以及一个或多个 SRP 校正比例因子的估计。激活和配置该模型的更多细节见 `Plate` 资源。另见 `samples/Navigation/Ex_Estimate_NPlateSRP_AreaCoefficient.script`。
- 新的协方差传播能力，带可选的状态噪声补偿（SNC）过程噪声，使用 `Propagate` 命令的 `Covariance` 参数。见 `samples/Ex_Propagate_Covariance.script`。
- 使用 GMAT Python 接口实现 Vallado 初轨确定（IOD）例程的示例脚本。见 `samples/Ex_IOD.script`。
- Range、Doppler、DSN_SeqRange 和 DSN_TCP 测量类型已增强，支持航天器间（有时称为"交叉链路"）跟踪。这些测量类型现在可用于建模在轨航天器之间的测距和多普勒测量。详见"航天器间跟踪测量"一节及 `samples/Tut_Inter_Spacecraft_Tracking.script`。
- `BatchEstimator` 中的多航天器同时估计：单个批估计器实例可用于在单次估计运行中估计多个航天器。该能力适用于以某种方式耦合的航天器——通过航天器间跟踪或对共享跟踪资源的偏差估计。见 `samples/Navigation/Ex_MultiSpacecraft_Simultaneous_BatchEstimation.script`。
- 对 DSN 跟踪数据使用 DSN TRK-2-23 电离层和对流层介质校正。详见"TRK-2-23 模型实现"一节。
- 批估计器"按过境弧段"估计测量偏差：该能力允许用户针对单个站在批估计器弧段上估计多个分段测量偏差。此功能未在扩展卡尔曼滤波中实现。详见"随弧段变化的偏差估计"（Pass-dependent Bias Estimation）一节。
- 有限机动的多项式推力角估计：`ThrustHistoryFile` 提供的有限推力标称方向误差可作为一对角度估计。这些角度可建模为常数或时间多项式。详见"推力角校正概述"一节。另见 `samples/Navigation/Ex_Estimate_ThrustAngles.script`。
- 在 `Simulator` 和 `BatchEstimator` 中使用星历传播器：星历文件可用作仿真测量数据的轨道来源，或用于单迭代"观测减计算"批估计器运行。使用星历传播器的航天器无法进行状态估计。星历传播器尚未在扩展卡尔曼滤波中实现。配置星历文件用作传播器的详情见 `Propagator`。
- 能够以单迭代"观测减计算"配置运行 `BatchEstimator`：在该模式下，批估计器运行单次迭代，计算并报告相对于初始状态的残差，不尝试状态估计。见 `RunEstimator` 命令的 SolveMode 选项。

### 脚本与 API 接口

R2022a 中实现的脚本与 API 接口改进：

- API 能力不再是 Beta 功能，现已可用于业务。示例脚本见 `api` 目录；API 能力的完整描述见 `docs/GMAT_API_UsersGuide.pdf`。
- 允许用户从 Python 例程调用 GMAT 的 Python API 现在支持多个 Python 3 版本。
- 允许用户在 GMAT 脚本内调用 Python 例程的 Python 接口插件现在支持多个 Python 3 版本。

### 最优控制

GMAT 最优控制能力在 R2022a 中仍为 Beta 功能。R2022a 的最优控制改进包括：

- Beta 级：CSALT 输出最优控制历史文件中描述优化器性能的附加元数据。
- Beta 级：改进 CSALT 非线性规划（NLP）求解器的封装，可保存可行但非最优的解。
- Beta 级：基于先前网格细化迭代中可行但非最优的解，为 CSALT 添加新的初始猜测类型。

### OpenFramesInterface 可视化

> **注意**：OFI 继续作为 GMAT 中的主要 3D 可视化组件。`OrbitView` 将出于向后兼容目的继续受支持，但只会进行关键 bug 修复。

R2022a 中 OpenFramesInterface 插件实现的可视化改进（OFI 完整文档见 OFI Wiki）：

- 新增对 Windows 和 Linux 上使用在线来源的高保真天体地形和影像的支持（macOS 尚不支持）。使用在线来源获取高保真地球地形和影像以及高保真月球影像的示例见 `samples/NeedOpenFramesInterface/Ex_OFI_HiFiEarthMoon.script`。
- 新增对航天器和天体使用 DXF 3D 格式的支持。

## 其他改进

- GMAT R2022a 包含一个可在 GMAT GUI 中使用的基本脚本级调试器。该新功能让用户在任务控制序列中设置 `Breakpoint`（断点）。脚本运行时，GMAT 在断点处暂停并打开一个面板，显示运行中定义的所有对象。用户随后可以检查每个对象、单步执行序列中的下一条命令并查看该命令对对象的影响、继续执行运行或结束运行。

## 兼容性变更

- `ExtendedKalmanFilter` 的 `ProcessNoiseTimeStep` 选项已移至 `ProcessNoise` 资源并重命名为 `UpdateTimeStep`。ExtendedKalmanFilter 资源上的 ProcessNoiseTimeStep 选项在当前版本中仍可使用。当 `ProcessNoiseModel.UpdateTimeStep` 和 `ExtendedKalmanFilter.ProcessNoiseTimeStep` 都为非零值时，将使用 `ExtendedKalmanFilter.ProcessNoiseTimeStep` 参数。

## 已修复与已知问题

### 已修复问题

本版本关闭了 100 多个高优先级 bug。详见 "Critical Issues Fixed in R2022a" 报告。R2022a 中一些重要修复包括：

| ID | 描述 |
| --- | --- |
| GMT-7742 | 不使用斜坡表时 DSN_SeqRange 发射频率处理不正确 |

### 已知问题

所有已知主要问题见 "All Known Critical Issues for R2022a" 报告。本版本中重要的已知问题：

| ID | 描述 |
| --- | --- |
| GMT-7768 | 对以月球为中心的 OD 使用星历传播器时，Simulator 资源中的月球掩星未被正确考虑 |