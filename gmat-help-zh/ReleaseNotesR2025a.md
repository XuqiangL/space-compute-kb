# GMAT R2025a 发行说明（ReleaseNotesR2025a）

> 译自 GMAT R2026a 帮助文档 ReleaseNotesR2025a.html

GMAT R2025a 于 2025 年 4 月发布。这是自 2023 年 1 月以来的第一个公开版本，是本项目的第 15 个版本。这是一个重要的项目版本，在通用能力与模型、导航与轨道确定、脚本与 API 接口以及可视化方面包含大量重大改进和增强。以下为本版本关键变更摘要。

## 里程碑与成就

GMAT 在业务任务支持中的应用持续增长：

- GMAT 被空间天气后续任务（SWFO）飞行动力学团队用作机动规划的主要业务工具。
- GMAT 被罗曼空间望远镜（RST）飞行动力学团队用作机动规划的主要业务工具。
- GMAT 轨道确定被 NASA GSFC 飞行动力学设施（FDF）用于支持各类任务。

GMAT 在 Spark 期刊 2024 年秋季刊（第 22 卷第 4 期）的 GMAT 专题文章中被报道。

## 主要改进与增强

### 通用能力与模型

R2025a 新增的通用能力：

- **支持月球平均地球（ME）参考架**（GMT-8201/GMT-7604）：GMAT 现在允许用户把月球平均地球（ME）参考架指定为月球（Luna）的体固参考架。计算月球经纬度时，或为以 Luna 为原点的用户自定义 CoordinateSystem 指定 BodyFixed 轴时，将使用月球 ME 参考架。配置和使用示例见用户指南 CelestialBody 资源一章中的代码片段。
- **从用户提供的 BPC 内核添加月球固定参考架**（GMT-8000）：用于计算月面测地坐标和 Luna BodyFixed 轴的月球固定参考架定义，可使用 SPICE 内核和 GMAT 中 Luna 天体上适当的 SPICE 参考架名称来指定。使用二进制 SPICE 定向内核提供月球定向模型的示例见用户指南 CelestialBody 资源一章。
- **向 CoordinateSystem 资源添加真赤道平均地球（TEME）轴**（GMT-8166）：CoordinateSystem 资源现在提供 TEME 轴。
- **扩展用于阻力预测的 CSSI 空间天气文件选项**（GMT-7777/GMT-7772）：用户现在可以在传播器的 Drag.PredictedWeatherSource 参数上指定 'CSSISpaceWeatherFile'，从而使用最新的太阳活动预测来建模预测阻力。示例见用户指南 Force Model 一章的 "CSSI Space Weather Data" 小节。
- **在生产模式下添加用于任务设计的多体谐波重力**（GMT-8254）：GMAT 现在接受并同时建模多个天体的全阶重力场。该能力可用于任务设计和机动规划任务。示例见 samples 文件夹中的 Ex_MultibodySphericalHarmonicGravity 脚本。
- **允许用户设置负的 Cd 和 Cr**（GMT-8181）：GMAT 现在允许 Spacecraft 资源上的 Cd 和 Cr 取负值。虽然这些值取负并不典型也不符合物理，但负值可用于别名化其他未建模的力，或者在用作优化参数时有时可能为负。
- **额外的优化器监控和控制**（GMT-8151）：GMAT 的 VF13ad 和 SNOPT 优化器现在提供对优化过程逐迭代的可选监控。这使用户能够在优化器执行的缩放之外，对约束值定义物理容差。另见 samples/NeedVF13ad 文件夹中的示例脚本 Ex_MonitoredLunarTransfer.script。
- **Contact Locator 报告中新增 AzimuthElevationRangeRangeRate 输出**（GMT-7810）：新的 AzimuthElevationRangeRangeRate ContactLocator 报告类型提供一种输出格式，在每个计算出的过境弧段内，按指定时间步逐行报告过境编号、站名、方位角、仰角、距离和距离变化率。
- **解析质量特性建模**（GMT-7983）：GMAT 现在包含航天器对象质心和惯性矩的解析建模。质量特性在有限机动等质量损失事件期间动态计算，并可用于报告。示例见 samples 文件夹中的 Ex_AnalyticMassProperties 脚本。
- **外部力模型插件更新**（GMT-8022）：使用该能力需要正确配置 GMAT Python 接口。它新增了在外部用户创建的 Python 文件中定义和使用加速度的能力。提供加速度模型的 Python 代码必须遵循特定约定。细节见用户指南 ForceModel 一章中的 External Force Model 备注。示例见 samples 文件夹中的 Ex_ExternalForceModel 和 Ex_ExternalForceModel_NoAPI 脚本。
- **GMAT 的工厂管理系统现在允许用 GMAT 插件中提供的自定义替换对象替换内部组件**（GMT-8265）：使用该能力的用户负责测试任何使用此新支持的基于插件的替换。

#### Beta 和 Alpha 级能力

这些是尚未经过完整测试、可能存在 bug 的新功能。要访问其中某些功能，你可能需要编辑 `bin/gmat_startup_file.txt` 文件以加载所需的 alpha 插件，和/或激活仅在测试模式下可用的功能（设置 RUN_MODE = TESTING）。这些功能应谨慎使用。

- 包含用于二进制 UTDF 和 CCSDS TDM 跟踪数据格式的 GMD 格式化工具（GMT-7992）：utilities/python/navigation 文件夹中提供 Python 脚本，可将有限选择的 UTDF 和 CCSDS TDM 数据类型转换为 GMD 格式。utdf_to_gmd.py 脚本支持把 UTDF 三向 RangeRate、TDRS 单向返回多普勒和 TDRS DOWD 转换为 GMD；tdm_to_gmd.py 脚本支持把 CCSDS TDM DOPPLER_INTEGRATED 转换为 GMAT RangeRate、TRANSMIT_FREQUENCY 转换为 GMAT 斜坡（ramp）记录、RECEIVE_FREQUENCY 转换为 GMAT DSN_TCP、RANGE 转换为 GMAT Range 或 DSN_SeqRange 记录。

### 导航与轨道确定（OD）

R2025a 新增的导航与轨道确定能力：

- 轨道确定（导航）的新业务数据类型：
  - 新增 GN/DTE 三向距离变化率测量（GMT-8222）：使用 RangeRate 数据类型支持发射站和接收站不同的地基跟踪测量（km/sec）。示例见 samples/Navigation 文件夹中的 Ex_Estimate_RangeRangeRate。
  - 新增 DSN 伪噪声（PN）测距测量（GMT-8218）：支持以距离单位表示的 DSN PN 测距测量（DSN 数据类型 14）。
  - 新增 DSN 三向总计数相位（TCP）多普勒测量（GMT-8136）：支持接收站和发射站不同的平均相位差测量（源自 DSN 数据类型 17，单位 Hz）。
  - 新增 TDRS 用户单向返回多普勒测量（GMT-8068）：支持跟踪与数据中继卫星（TDRS）用户单向返回多普勒测量。示例见 samples/Navigation 文件夹中的 Ex_Estimate_TDRSOneWayReturnDoppler。
  - 新增 TDRS 用户测距和多普勒测量（GMT-7549）：支持 TDRS 用户双向返回测距和多普勒测量。示例见 samples/Navigation 文件夹中的 Ex_Estimate_TDRSUserTracking 和 Ex_Estimate_TDRSAndUser。
  - 新增 TDRS 差分单向多普勒（DOWD）（GMT-7467）：支持 TDRS 用户差分单向返回多普勒（DOWD）测量。DOWD 测量通过对同时单向返回多普勒跟踪事件的测量求差来构建。
  - 新增 TDRS 双边应答机测距系统（BRTS）测距和多普勒（GMT-7327）：支持 TDRS BRTS 测距和多普勒跟踪。BRTS 跟踪类似于 TDRS 用户测距和多普勒跟踪，BRTS 应答机相当于固定在地球上已知位置的 TDRS 用户。BRTS 跟踪用于精确确定 TDRS 航天器的轨道。示例见 samples/Navigation 文件夹中的 Ex_Estimate_BRTSTracking。
- 为包含观测和残差数据记录的 BLS 估计器数据文件新增 JSON 输出选项（GMT-7899）：新增 JSON 格式数据文件，以完整数值精度包含批估计器测量、残差和其他数据。该新能力取代了批估计器 MatlabFile 选项，使该能力不受 MATLAB 许可证限制而免费可用。此次更新后 MatlabFile 选项已弃用，但目前仍可用。示例见 samples/Navigation 文件夹中的 Ex_Estimate_RangeRangeRate。
- K 波段频率支持（GMT-6339）：现在支持 K 波段频率，用于计算地对空或空对地跟踪链路的电离层校正。

R2025a 中发生变化的导航与轨道确定能力：

- 仅在测试模式下允许把 DSN_SeqRange 和 DSN_TCP 用作交叉链路跟踪类型。
- 为支持三向跟踪路径，RangeRate 和 DSN_TCP 测量类型的 GMD 跟踪数据记录格式已更改。旧格式目前仍可使用。变更详情请见用户指南参考指南 > 轨道确定 > 系统 > 轨道确定的跟踪数据类型。

自 R2025a 起弃用的导航与轨道确定能力：

- BatchEstimator 的 MatlabFile 输出选项已弃用，由新的 JSON 格式 DataFile 选项取代。JSON 批估计器数据文件生成示例见 samples/Navigation 文件夹中的 Ex_Estimate_RangeRangeRate。

### 脚本与 API 接口

R2025a 中实现的脚本与 API 接口改进：

- **新增 API Cookbook**（GMT-8268）：GMAT 现在在新文档《GMAT API Cookbook》中提供 Python API 的用例和示例。另见 GMAT "api" 文件夹中的示例 API 用例。
- **API 中支持命令**（GMT-7003）：GMAT API 现在提供通过 API 访问任务控制序列的能力。示例见 GMAT "api" 文件夹中的 Ex_R2025a_BasicTarget 和 Ex_MarsBPlane。
- **使用 GetNumber 扩展 Python 对向量和矩阵数据的访问**（GMT-8083）：在 R2020a 和 R2022a 中，GMAT 字段和变量可在 GMAT API 中作为浮点值访问；R2025a 中该能力也可用于向量和矩阵。示例见 GMAT "api" 文件夹。
- **强制要求力模型对象的"三段式"语法**（GMT-7685）：R2025a 之前的 GMAT 版本会忽略 "ForceModel.InnerDelimiter.FieldName" 形式字段的内部分隔符。现在内部分隔符被正确解析，因此可以把多个重力场的设置（如谐波的次数和阶数）赋给正确的力。示例见 samples 文件夹中的 Ex_MultibodySphericalHarmonicGravity。
- **扩展 Include 命令以允许字符串作为路径**（GMT-8075）：用户现在可以把包含文件的名称脚本化到 GMAT 字符串中，随后用这些字符串指定被包含的文件。
- **更改脚本创建，默认不包含 "GMAT" 前缀**（GMT-8034）：字段指定和赋值的可选 "GMAT" 前缀不再是 GMAT 脚本中的默认设置。新默认脚本编写方式示例见 R2025a 示例脚本。
- **增强 Python 脚本接口以支持多维数组**（GMT-7965）：GMAT 现在可以通过脚本 Python 接口与外部 Python 代码交换多维数组。
- **扩展 Write/Report 命令以支持追加到现有文件**（GMT-7813）：新增 ReportFile 参数 AppendToExistingFile。该参数可设为 True，允许 GMAT 以追加模式写入报告文件，而不是每次覆盖文件。

### 最优控制

GMAT 最优控制能力在 R2025a 中仍为 Beta 功能。

### OpenFramesInterface 可视化

> **注意**：OFI 继续作为 GMAT 中的主要 3D 可视化组件。`OrbitView` 将出于向后兼容目的继续受支持，但只会进行关键 bug 修复。

OFI 的完整文档见 OFI Wiki。

## 其他改进

- 移除了数组维度限制（GMT-8108）：GMAT 向量和数组此前有 1000 个元素（向量）和 1000 行 1000 列（数组）的大小上限，该限制已移除。
- 改进错误消息输出（GMT-8104）。
- GMAT 用户指南（以前称为 help-letter）移至 <GMAT 顶层文件夹>/docs/ 并重命名为 GMAT_UsersGuide，以与其他用户指南保持一致。
- Help 下拉菜单已更改（GMT-8067）：此前 Help->Online Help 会带你到在线用户指南；现已重命名为 Help->User Guide，并链接到随 GMAT 打包的本地 HTML 版用户指南。

## 兼容性变更

- 支持 wxWidgets 3.2.6（GMT-5612）和 Apple Silicon 工作站：GMAT R2022a 使用 wxWidgets 3.0.4 构建，GUI 组件已更新为使用 wxWidgets 3.2.6 构建。该工具包更新增加了对运行较新 MacOS 的 Apple Silicon 工作站的支持。
- GMAT R2025a 兼容 Python 3.10、3.11 和 3.12（GMT-8277）：GMAT 构建包现在包含 Python 3.6 至 3.12 的绑定。

## 已修复与已知问题

### 已修复问题

本版本关闭了 50 多个高优先级 bug。详见 "Critical Issues Fixed in R2025a" 报告。R2025a 中一些重要修复包括：

| ID | 描述 |
| --- | --- |
| GMT-8153 | 优化器错误地声称收敛 |
| GMT-8023 | 交叉链路测量期间硬件延迟应用不正确 |

### 已知问题

所有已知主要问题见 "All Known Critical Issues for R2025a" 报告。本版本中几个重要的已知问题：

| ID | 描述 |
| --- | --- |
| GMT-8024 | 可能出现 Windows Defender 弹窗，阻止用户首次打开 GMAT 应用程序 |
| GMT-8243 | Windows 帮助内容可能显示为空白，需要额外的用户操作 |
| GMT-8322 | 用 OFI 替代 OrbitView 并重做星下点轨迹（OrbitView 和 GroundTrack 绘图组件在 MacOS 14 及更高版本上不能正常工作） |
| GMT-8339 | R2025a 在 Mac 上未公证，部分用户可能无法打开 R2025a 的 GMAT GUI（脚本可在终端窗口中通过 GMAT 控制台正常运行） |
| GMT-8340 | 支持 Mac Intel 机器（Mac 系统可能使用 Intel 或 Apple Silicon 芯片组，目前 GMAT 开发团队支持 Silicon 芯片组构建） |