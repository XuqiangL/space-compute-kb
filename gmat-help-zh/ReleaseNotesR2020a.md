# GMAT R2020a 发行说明（ReleaseNotesR2020a）

> 译自 GMAT R2026a 帮助文档 ReleaseNotesR2020a.html

GMAT R2020a 于 2020 年 5 月发布。这是自 2018 年 5 月以来的第一个公开版本，是本项目的第 13 个版本。这是一个重要的项目版本，在动力学建模和其他领域包含大量改进，并包含五个主要的新子系统和组件：

- 基于 OpenFrames 的新 3D 图形引擎。OpenFrames 是 NASA Copernicus 软件中使用的图形引擎。GMAT 和 Copernicus 现在共享图形能力，提高了开发效率，并为两个系统提供了更强的能力。
- Collocation Stand-Alone Library and Toolkit（CSALT，配点独立库与工具包）的第一个生产级 C++ 版本。CSALT 求解一般最优控制问题，支持伪谱法和 Lobatto IIIa 转录。CSALT 可独立于 GMAT 使用（尽管 CSALT 使用了一些 GMAT 底层数学库）。
- 支持有限推力优化的新最优控制子系统。最优控制插件使用 CSALT 优化库、电推进模型和 GMAT 的高保真动力学模型，支持高保真有限推力优化。该插件大量使用解析偏导数，并在未提供解析偏导数时采用最优有限差分。
- 一个新的（Beta）API，旨在为用户提供对 GMAT 功能的底层访问，并支持 NASA 的 GMAT、Copernicus 和 MONTE 软件应用之间的互操作性。
- 一个新的（Alpha）带过程噪声的扩展卡尔曼滤波平滑器。

以下为本版本关键变更的更详细摘要。完整清单见 JIRA 上的完整 R2020a 发行说明。

## 里程碑与成就

- 2018 年 5 月 1 日，月球勘测轨道飞行器（LRO）项目举行了业务就绪评审（ORR），评估 GMAT 作为 GTDS 的替代品、成为 LRO 主要业务轨道确定（OD）工具。GMAT 在此次 ORR 上获批用于该目的，LRO 于 2018 年 6 月开始使用 GMAT 进行业务 OD。
- 2018 年 4 月，凌日系外行星巡天卫星（TESS）任务发射。TESS 从提案开发到业务运行，一直使用 GMAT 作为任务设计和机动规划的主要工具。
- GMAT 团队当时正在开发扩展卡尔曼滤波平滑器（EKFS）轨道确定能力，供未来版本发布。2020 年底，一个使用 GPS 点解数据类型的 NASA 低地轨道任务将帮助业务测试新的 EKFS 能力。计划在 R2021a 版本中发布支持 GMAT 所有数据类型的 EKFS 能力的公开版本。
- GMAT 团队当时正在将 CSALT 集成到 GSFC 的核心飞行系统（cFS）中，以演示在星上执行最优控制的能力。

## 新功能

### 通用能力

R2020a 新增的通用能力：

- 力模型现在支持太阳辐射压（SRP）N 板（N-Plate）力建模（alpha/beta 级）。详见 ForceModel 一节。
- 姿态传播模型现在支持使用初始姿态和角速度的运动学姿态传播。详见"航天器姿态"（Spacecraft Attitude）一节。
- 硬件模型（如天线、太阳敏感器）扩展为支持视场，包括：
  - 硬件相对于航天器本体的定向
  - 圆锥形、矩形和自定义视场的视场掩膜
  - 以单位向量表示的点的可见性模型
  - OpenFrames 图形中传感器锥的可视化
- 力模型现在支持在数值传播期间使用连续推力文件。详见新的 `ThrustSegment` 和 `ThrustHistoryFile` 一节，示例脚本 `samples/Ex_Propagate_ThrustHistoryFile.script` 演示了传播中有限推力建模的使用。推力历史模型支持：
  - 有限推力（低、中或高连续推力）或加速度的插值
  - 传播中质量流率的可选积分
  - 输入推力/加速度的坐标系选择
  - 选定输入的缩放
  - 插值方法的选择
- 阻力模型现在支持 SPAD 阻力模型的插值，用于姿态相关阻力建模。SPAD 文件通过对 CAD 模型进行光线追踪来创建，计算姿态相关的面积剖面，在数值传播期间进行插值。有关如何配置力模型和航天器以使用 SPAD 阻力模型的更多信息，分别见 ForceModel 和"航天器弹道/质量特性"（Spacecraft Ballistic/Mass Properties）一节，以及示例脚本 `samples/Navigation/Ex_Estimate_SPADDragScaleFactor.script`。

### 轨道确定（OD）增强

有大量 OD 增强，包括 5 个新资源 `KalmanFilter`、`Smoother`、`ProcessNoiseModel`、`EstimatedParameter` 和 `Plate`，以及对现有功能的大量改进：

- OD 子系统经历了重大重构，为未来发布带平滑器的扩展卡尔曼滤波做准备。
- 电离层介质校正模型通过校正缓存变得更快：当多个独立测量（如距离、距离变化率和角度）在同一历元来自同一站时，GMAT 重用已计算的光行时电离层校正。
- 批最小二乘（BLS）现在支持内循环 sigma 编辑。每次 BLS 迭代后，使用迭代线性化近似预测下一次 BLS 迭代中可能被编辑的测量，并相应校正状态。这可以加速收敛并帮助减少所需的 BLS 总迭代次数。见 `BatchEstimator` 资源的 `UseInnerLoopEditing` 选项。
- 批最小二乘（BLS）现在在尝试求逆之前从法方程矩阵中移除不可观测状态。例如，当用户配置估计测量偏差但该偏差的所有观测都被编辑剔除时这很有用。GMAT 现在会移除不可观测状态并继续处理，而不是以矩阵求逆错误终止。
- OD 仿真和估计支持几种新测量类型（详见用户指南"轨道确定的跟踪数据类型"一节）：
  - 方位角、仰角（Azimuth, Elevation angles）
  - XEast、YNorth 角度
  - XSouth、YEast 角度
  - Range_Skin（C 波段、非应答机测距）
- 批最小二乘（BLS）测量统计报告现在包括用户编辑数据的汇总统计。
- 估计子系统现在支持 `ThrustHistoryFile` 和 `ThrustSegment` 资源，用于在 BLS OD 的估计弧段中建模有限燃烧，并可选估计对标称有限燃烧剖面的比例因子校正。
- BLS MATLAB 数据文件的结构已更改。详见用户指南轨道确定部分 `BatchEstimator` 资源文档。
- 新的 `ExtendedKalmanFilter` 和 `Smoother` 资源在测试模式下可用。这些资源正在开发中，不应在业务支持中使用。
- 估计子系统现在支持用于太阳辐射压（SRP）的（Beta）N 板面积模型。用户可以为预测和估计配置详细的多板面积模型进行 SRP 建模。该模型包括镜面反射和漫反射率，支持运动面板（如太阳帆板），以及一个或多个 SRP 校正比例因子的估计。该模型正在开发中，不应在业务支持中使用。激活和配置详情见 `Plate` 资源。
- 估计子系统现在支持解算 SPAD 阻力/SRP 系数。

GMAT 的轨道确定（OD）能力已显著增强。与所有新版本一样，使用 GMAT OD 能力的任务在将新版本 GMAT OD 用于业务目的之前，应执行基线回归/性能测试。GMAT 随附多个演示本版本新轨道确定能力的示例，包括：

- 角度测量类型：见 `samples/Navigation/Ex_Estimate_AngleData.script`
- 表面测距（Skin range）测量类型：见 `samples/Navigation/Ex_Estimate_RangeSkin.script`
- SPAD 阻力估计：见 `samples/Navigation/Ex_Estimate_SPADDragScaleFactor.script`
- SPAD SRP 估计：见 `samples/Navigation/Ex_Estimate_SPADSRPScaleFactor.script`
- 有限推力估计：见 `samples/Navigation/Ex_Estimate_ThrustScaleFactor.script`
### 3D 可视化插件：OpenFramesInterface

GMAT 现在支持名为 OpenFramesInterface（OFI）的新 3D 图形组件，与 GMAT 旧版 3D 图形（`OrbitView`）能力相比，它实现了高性能交互式 3D 可视化，并具有大量附加功能。GMAT R2020a 包含 OFI v1.0，这是该插件第一个经过测试和文档化的版本。OFI 的完整文档见 OFI Wiki。关键 OFI 接口能力摘要如下：

- 新的 OFI 图形组件支持 GMAT 旧版 3D 图形中的所有功能，以及大量新功能。
- 系统现在支持任何航天器或天体的用户自定义视图。视图可以是体固的、坐标系固定的，或从一个天体看向另一个天体。此外，用户可以在单个图形窗口中切换视图。
- 多线程可视化现在利用多个处理器核心，与 OrbitView 相比，GMAT 整体计算速度普遍提升。
- 3D 图形现在支持对仿真时间的完全控制：可在任意时间查看场景、以各种时间尺度动画播放，并在多个 OpenFramesInterface 窗口之间同步时间。
- 系统支持对显示对象的精细控制，包括可选绘制轴、天体、轨迹或许多其他按天体设置的图形选项。
- 图形选项更改不再需要重新运行任务，包括在用户自定义视图之间切换以及启用/禁用显示对象。
- 图形现在支持高保真渲染，包括多重采样抗锯齿（MSAA）、光照、带星等颜色和大小的精确星图（HYGv3 数据库）。
- 系统现在支持 3D 图形中指向对象的向量：体固方向或指向另一对象。
- OFI 接口现在支持可视化传感器视场，包括圆锥形、矩形和自定义视场。
- 系统支持通过 OpenVR 进行虚拟现实可视化。任何场景都可以在 OpenVR 兼容硬件上可视化，包括 Oculus Rift 或 HTC Vive。

GMAT 在 `samples/NeedOpenFramesInterface` 中提供了大量演示如何使用新图形能力的示例脚本。特别值得关注的几个脚本：

- 近实时图形：见 `samples/NeedOpenFramesInterface/Ex_OFI_RealTimeMOC.script`
- 传感器锥可视化：见 `samples/NeedOpenFramesInterface/Ex_OFI_FieldOfView.script`
- 日食可视化：见 `samples/NeedOpenFramesInterface/Ex_OFI_VR_2017SolarEclipse.script`
- 自定义弧段颜色：见 `samples/NeedOpenFramesInterface/Ex_OFI_CustomSegmentColors.script`

> **注意**：OFI 现在是 GMAT 中默认的 3D 可视化组件。`OrbitView` 将出于向后兼容目的继续受支持，但只会进行关键 bug 修复。

### 轨迹优化插件

GMAT 有一个新的轨迹优化子系统，包括新技术和新的 C++ 与脚本接口（旧版参数优化功能仍受支持）。GMAT 的轨迹优化能力扩展为支持使用配点法求解最优控制问题的独立库，称为 Collocation Stand Alone Library and Toolkit（CSALT）。CSALT 求解一般最优控制问题，支持伪谱法和 Lobatto IIIa 转录及自动网格细化。CSALT 可独立于 GMAT 使用（尽管使用了一些 GMAT 底层数学库）。

有两个新的专有插件——CsaltInterface 和 EMTGModels——用于航天器轨迹优化。它们与 CSALT 库一起构成新的 GMAT 最优控制能力。CsaltInterface 插件包含 GMAT 与 CSALT 中配点转录和优化能力的接口。EMTGModels 插件允许 GMAT 使用在 Evolutionary Mission Trajectory Generator（EMTG）中实现的航天器电源和发动机模型。这些组件共同为最优控制函数（包括轨道动力学和推力模型）提供广泛的解析偏导数支持。未提供解析导数时，系统使用最优有限差分。

最优控制组件（包括 CSALT 和 GMAT 最优控制）的用户指南位于 GMAT 发行版的 `gmat/docs/GMAT_OptimalControl_Specification.pdf`。新能力简要摘要如下：

- CSALT 求解通用最优控制问题，支持动力学、Lagrange 形式代价函数、路径约束和边界约束。CSALT 不假设问题是低推力的，可求解一般问题，包括但不限于 6 自由度优化、经典最优控制问题、低推力、高有限推力、编队与星座以及再入问题。CSALT 随附有限的模型集；一般而言，使用 CSALT 时用户必须提供动力学、代价和约束函数的模型。（注：GMAT 最优控制子系统用于在 GMAT 中求解低推力轨迹问题。）
- GMAT 插件 CsaltInterface 和 EMTGModels 支持低推力轨迹优化。
- GMAT 与 CSALT 的接口完全包含在 GMAT 脚本语言中，GMAT 脚本用户无需编写底层 C++ 代码（熟悉 C++ 的用户也可通过 C++ 接口直接调用 CSALT）。
- 系统可以使用多种配点转录之一（带网格细化）优化受约束的航天器轨迹。
- 系统支持由多个"相位"（phase）组成的轨迹，每个相位可由不同的动力学模型定义。相位可通过用户可设置的约束"链接"（例如一个相位末端与另一相位开端之间的全状态/时间链接以强制连续性）。
- 用户可以在 GMAT 脚本内设置优化设置，例如可行性/最优性容差、状态上下界和初始配点网格设置。
- 用户可以从多个常用价值函数中选择（如最大末质量、最短飞行时间）。
- 推力模型现在包括恒定推力和比冲（Isp）、固定效率、多项式和平滑节流表。
- 用户可以在轨迹中包含多个常用航天器轨迹约束，如集成飞越（integrated flyby）或天体交会。
- 最优控制函数中的标量内联表达式有 alpha 级支持，即当内置约束不满足需求时，用户可以在脚本中基于 GMAT 变量指定约束。
- 新示例脚本和支持文件示例包含在发行版的 gmat/samples/OptimalControl（示例脚本）以及 gmat/data/misc 和 gmat/data/emtg（支持文件）中。

> **注意**：GMAT 最优控制和 CSALT 的源代码可以分发，但目前未包含在公开版本中，因为它们依赖于非线性规划求解器软件 SNOPT。这些组件的源代码可应要求提供，但用户必须从 Stanford Business Software 获得 SNOPT 才能编译这些组件。

GMAT 在 `samples/OptimalControl/` 文件夹中随附大量演示最优控制功能的示例脚本（CSALT C++ 示例和教程见上述用户指南）。特别值得关注的几个脚本：

- 低推力行星际转移：见 `samples/OptimalControl/Ex_EarthToMarsSOI_C3Eq0_CSALTTutorial.script`
- 发射模型：见 `samples/OptimalControl/Ex_PCLaunch_ConstrainedC3AndDLA_EarthLaunch_EarthOrigin.script`
- 配置 Lobatto IIIa 转录：见 `samples/OptimalControl/Ex_Phase_Type_ImplicitRKOrder6.script`
- 集成飞越模型：见 `samples/OptimalControl/Ex_IntegratedFlyby_MarsFlyby.script`
- 推力模型配置：见 `samples/OptimalControl/Ex_EMTGSpacecraft_SCOpt_*.script`

### API

GMAT 现在提供从 Python 和 Java 以及从 MATLAB（使用基于 Java 的 API）访问其许多内部组件的能力。这个新的 Beta 级功能实现了 NASA 的 GMAT、Copernicus 和 MONTE 软件应用之间的互操作性。API 用户指南位于 GMAT 发行版的 `docs/GMAT_API_UsersGuide.pdf`。关键 API 功能摘要如下：

- 用户现在可以通过 API 接口加载 GMAT 脚本、修改参数并执行加载的脚本。
- 运行脚本后，用户可以访问运行中的对象并检索运行结果。
- 用户现在可以直接通过 API 创建 GMAT 对象：
  - 创建的对象可以使用类似 GMAT 脚本的语法进行配置。
  - 对象间连接通过调用初始化函数建立。
  - 初始化后的对象提供与 GMAT 运行期间执行的计算相匹配的数据。
- 用户可以从其平台的控制台接口与 GMAT 对象交互——即从 MATLAB 控制台、Python 控制台（Spyder、ipython 或默认 Python 控制台应用程序）。
- API 可以使用 Jupyter notebooks 访问。
- GMAT API 在使用期间提供实时帮助。
- 所有这些功能的示例都包含在发行版的 api 文件夹中。

> **注意**：Python 的编译 API 资源在 Windows 和 Mac 上使用 Python 3.7 构建，在 Linux 上使用平台提供的 Python 3.6 库构建。

GMAT 在 `gmat/api` 文件夹中随附大量演示 API 功能的示例脚本。特别值得关注的几个：

- 调用 GMAT 力模型：见 `gmat/api/Ex_R2020a_CompleteForceModel.*`
- 调用 GMAT 传播器：见 `gmat/api/Ex_R2020a_RangeMeasurement.*`

## 改进

- 新增多个内置 GMAT 函数：`Pause`、`SystemTime`、`ConvertTime`、`Num2str`、`Str2num`、`RotationMatrix` 和 `Sign`。
- 有一个使用 GMAT Python 接口和 Python sockets 将原始遥测数据引入 GMAT 的初步接口。
- 新的图形界面 DynamicDataDisplay（动态数据显示）允许在系统执行期间显示数值和文本数据，并可基于用户定义的约束对数据进行可选的颜色编码。
- 有一个新的、经过最少测试的 SNOPT 接口，允许用户提供预编译的 SNOPT 7.5 版本。以前版本的 GMAT 将 SNOPT 直接编译进 SNOPT 插件，这阻碍了发布。
- Beta 多面体重力模型的更新允许非均匀密度的多面体区域。
- 脚本编辑器现在支持语法高亮。
- 地面站现在可以放置在任何天体上（以前版本只能是地球）。
- 编译 GMAT 时，依赖配置现在通过 Python 3 脚本在所有平台上统一。以前版本使用 bash 和 Windows .bat 文件。
- GMAT 构建系统有大量改进：更容易集成外部插件（如 OpenFramesInterface），CMake 自动下载一些依赖（目前是 Boost）。这使开发者更容易编译 GMAT。
- SPAD SRP 模型支持改进的插值。

## 兼容性变更

- `BatchEstimatorInv` 资源已重命名为 `BatchEstimator`。`BatchEstimatorInv` 在 R2020a 中仍会被识别，但将在下一个主要版本中弃用。
- `BatchEstimator` MATLAB 数据文件的结构已更改。详见 `BatchEstimator` 资源文档。

## 已修复与已知问题

### 已修复问题

本版本关闭了 150 多个 bug。关键 bug 及解决方案清单见 "Critical Issues Fixed in R2020a" 报告；次要问题见 "Minor Issues Fixed for R2020a" 报告。R2020a 中的一些修复包括：

- 仿真器现在在中心天体不是地球时也考虑轨道中心天体的掩星（GMT-6134）。
- 修正了影响仿真超过三周时长数据能力的错误（GMT-6649）。
- 解算参数现在可以在 `Spacecraft.SolveFors` 字段上以任意顺序指定（GMT-6658）。
- `BatchEstimator` 的 `ResetBestRMSIfDiverging` 设置现在可以工作（GMT-7036）。
- MarsGRAM 大气模型现在对 Mac 和 Linux 用户正确工作（GMT-5044）。
- GMAT 现在在闰秒当天正确插值 UT1-UTC（GMT-5954）。

### 已知问题

所有已知问题清单见 "All Known Issues for R2020a" 报告。本版本中几个重要的已知问题：

| ID | 描述 |
| --- | --- |
| GMT-5417 | 自适应步长控制在 GMAT 导航系统中使用时表现不一致。仿真和估计目前需要定步长积分。 |
| GMT-6202 | 某些情况下 DSN_TCP 和 Doppler 电离层校正中可能观察到高达 1 mm/sec 的尖峰。IRI2007 模型的电子密度随时间变化存在一些跳变，当起始和结束信号路径位于这些跳变的不同侧时会产生尖峰。 |
| GMT-7207 | GMAT Python 接口仅设计为与 python.org 的标准 Python 安装一起工作（Mac 和 Windows 推荐 Python 3.7；Linux 推荐 Python 3.6 或 3.7）。初步测试表明 Windows 用户可能可以通过删除对 python.org Python 的系统变量引用并创建指向 python.exe 所在文件夹的系统变量 PYTHONHOME 来使用 Anaconda Python 接口，但这未经过完整测试。 |

## 附录：选定新图形能力的屏幕截图

> [图：传感器锥的可视化]

> [图：从月球看地球升起]

> [图：带阴影的复杂天体渲染]

> [图：带惯性视图和本体视图以及动态数据显示的近实时图形示例]