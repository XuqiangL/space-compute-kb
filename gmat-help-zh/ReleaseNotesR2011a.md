# GMAT R2011a 发行说明（ReleaseNotesR2011a）

> 译自 GMAT R2026a 帮助文档 ReleaseNotesR2011a.html

GMAT R2011a 于 2011 年 4 月 29 日在以下平台发布：

| 平台 | 状态 |
| --- | --- |
| Windows（XP、Vista、7） | Beta |
| Mac OS X（10.6） | Alpha |
| Linux | Alpha |

这是自 2008 年 9 月以来的第一个版本，是本项目的第 4 个公开版本。在本版本中：

- 新增了 100,000 行代码
- 打开了 798 个 bug，关闭了 733 个
- 代码由来自 4 个组织的 9 名开发者贡献
- 编写了 6,216 个系统测试并每晚运行

## 新功能

### OrbitView（轨道视图）

GMAT 旧的 OpenGLPlot 3D 图形视图被彻底改造并重命名为 OrbitView。新的 OrbitView 图支持 OpenGLPlot 的所有功能，并增加了几个新功能：

- 透视视图而非正交视图
- 恒星和星座（带名称）
- 新的默认地球纹理
- 精确的光照
- 支持用户提供的 3ds 和 POV 格式航天器模型

所有现有脚本将自动使用新的 OrbitView 对象，无需更改脚本。

> [图：新图形功能示例]

### 用户自定义天体

用户现在可以通过 GMAT 界面定义自己的天体（行星、卫星、小行星和彗星），方法是右键单击 Sun 资源（用于行星、小行星和彗星）或任何其他太阳系资源（用于卫星）。用户自定义天体可以在许多方面进行定制：

- Mu（用于传播）、半径和扁率（用于计算高度）
- 用户提供的纹理文件，用于 OrbitView
- 来自初始开普勒状态二体传播或 SPICE 内核的星历
- 定向和自旋状态

> [图：用户自定义天体界面]

### 星历输出

GMAT 现在可以使用 EphemerisFile 资源以 CCSDS-OEM 和 SPK 格式输出航天器星历文件。对于每个星历，你可以定制：

- 坐标系
- 插值阶数
- 步长
- 历元范围

> [图：EphemerisFile 资源配置]

### 航天器的 SPICE 集成

GMAT 中的航天器现在可以使用 SPICE 内核的数据而非数值积分进行传播。这可以在 Spacecraft 资源的 SPICE 选项卡上或通过脚本激活。支持以下 SPICE 内核：

- SPK/BSP（轨道）
- CK（姿态）
- FK（参考架）
- SCLK（航天器时钟）

### 插件

现在可以通过插件向 GMAT 添加新功能，而不必编译进 GMAT 可执行文件本身。本版本包含以下插件及其发布状态：

| 插件 | 状态 |
| --- | --- |
| libMatlabPlugin | Beta |
| libFminconOptimizer（仅 Windows） | Beta |
| libGmatEstimation | Alpha（预览） |

插件可以通过位于 GMAT bin 目录中的启动文件（`gmat_startup_file.txt`）启用或禁用。所有插件默认禁用。

### GUI/脚本同步

对于同时使用脚本和图形界面的用户，GMAT 现在明确指出两者是否同步，以及哪个脚本处于活动状态（如果加载了多个）。可能的状态为：

- Synchronized（已同步：界面和脚本具有相同数据）
- GUI or Script Modified（GUI 或脚本已修改：其中一个相对于另一个已被修改）
- Unsynchronized（未同步：两处存在不同的更改）

唯一需要手动干预的状态是 Unsynchronized，必须手动合并（或必须丢弃一组更改）。Windows 和 Linux 上提供状态指示器（在 Mac 上，它们以单个字符显示在 GMAT 工具栏上）。

> [图：同步状态指示器（已同步、GUI 已修改、脚本已修改、未同步）]

### 估计 [Alpha]

GMAT R2011a 在 libGmatEstimation 插件中包含重要的新状态估计能力。包含的功能有：

- 测量模型：
  - 几何（Geometric）
  - TDRSS 测距
  - USN 双向测距
- 估计器：
  - 批处理（Batch）
  - 扩展卡尔曼（Extended Kalman）
- 资源：
  - GroundStation（地面站）
  - Antenna（天线）
  - Transmitter（发射机）
  - Receiver（接收机）
  - Transponder（应答机）

> **注意**：此功能为 alpha 状态，仅作为预览包含在本版本中，未经过严格测试。

> [图：估计功能界面]

### 用户文档

GMAT 的用户文档已彻底改版。取代旧的 wiki，我们的正式文档现在用 DocBook 实现，GMAT 随附 HTML、PDF 和 Windows 帮助格式。本版本的文档资源包括：

- 帮助（随 GMAT 提供，通过 Help > Contents 菜单项访问）
- 在线帮助（频繁更新）
- 视频教程
- 帮助论坛
- Wiki（用于非正式和用户贡献的文档、示例和技巧）

### 屏幕截图

GMAT 现在可以将 OrbitView 面板的屏幕截图以 PNG 格式导出到输出文件夹。

## 改进

### MATLAB 自动检测

如果在 gmat_startup_file.txt 中启用，MATLAB 连接现在通过 libMatlabInterface 插件自动建立。我们不再分别发布带和不带 MATLAB 集成的可执行文件。支持大多数最新的 MATLAB 版本，但需要配置。

### 动力学模型数值

所有包含的动力学模型都已针对真值软件（主要是 AGI STK 和 A.I. Solutions FreeFlyer）进行了全面测试，所有已知数值问题都已更正。

### 脚本编辑器 [Windows]

GMAT 在 Windows 上的集成脚本编辑器在本版本中有了很大改进，现在具有：

- GMAT 关键字的语法高亮
- 行号
- 查找和替换
- 活动脚本指示器和 GUI 同步按钮

> [图：改进的脚本编辑器]

### 回归测试

GMAT 项目开发了一个全新的测试系统，允许我们每晚在整个系统上、跨多个平台进行自动化测试。新系统具有以下特点：

- 专注于 GMAT 脚本测试
- 用 MATLAB 语言编写
- 包含 6,216 个测试，覆盖 GMAT 的大部分功能需求
- 允许对每晚构建进行自动回归测试
- 与所有支持的平台兼容

项目还定期使用 SmartBear TestComplete 工具在 Windows 上测试 GMAT 图形界面。此测试大约每周进行两次，专注于通过界面输入和运行完整任务，并检查结果是否与脚本模式下生成的结果一致。

### 视觉改进

本版本包含大量视觉改进，包括：

- 新的应用程序图标和启动画面
- 许多新的专业制作的图标
- 面向新用户的欢迎页面

> [图：GMAT 启动画面]

## 兼容性变更

### 平台支持

GMAT 支持以下平台：

- Windows XP
- Windows Vista
- Windows 7
- Mac OS X Snow Leopard（10.6）
- Linux（Intel 64 位）

除 Linux 版本外，GMAT 是 32 位应用程序，但将在 64 位平台上以 32 位模式运行。MATLAB 接口在 Windows 上用 32 位 MATLAB 2010b 测试，预计支持 R2006b 到 R2011a 的 32 位 MATLAB 版本。

- **Mac**：测试了 MATLAB 2010a，预计版本覆盖与 Windows 相同。
- **Linux**：测试了 MATLAB 2009b 64 位，需要 64 位 MATLAB。其他方面预计版本覆盖与 Windows 相同。

### 脚本语法变更

`BeginMissionSequence` 命令很快将成为所有脚本的必需项。在本版本中，如果缺少此语句会生成警告。

以下语法元素已弃用，将在未来版本中移除：

| 资源 | 字段 | 替换 |
| --- | --- | --- |
| `DifferentialCorrector` | `TargeterTextFile` | `ReportFile` |
| `DifferentialCorrector` | `UseCentralDifferences` | `DerivativeMethod = "CentralDifference"` |
| `EphemerisFile` | `FileName` | `Filename` |
| `FiniteBurn` | `Axes` | （无） |
| `FiniteBurn` | `BurnScaleFactor` | （无） |
| `FiniteBurn` | `CoordinateSystem` | （无） |
| `FiniteBurn` | `Origin` | （无） |
| `FiniteBurn` | `Tanks` | （无） |
| `FiniteBurn`/`ImpulsiveBurn` | `CoordinateSystem = "Inertial"` | `CoordinateSystem = "MJ2000Eq"` |
| `FiniteBurn`/`ImpulsiveBurn` | `VectorFormat` | （无） |
| `FiniteBurn`/`ImpulsiveBurn` | `V`、`N`、`B` | `Element1`、`Element2`、`Element3` |
| `FuelTank` | `PressureRegulated` | `PressureModel = PressureRegulated` |
| `OpenGLPlot` | （整体） | `OrbitView` |
| `OrbitView` | `EarthSunLines` | `SunLine` |
| `OrbitView` | `ViewDirection = Vector` + `ViewDirection = [0 0 1]` | `ViewDirection = [0 0 1]` |
| `OrbitView` | `ViewPointRef` | `ViewPointReference` |
| `OrbitView` | `ViewPointRef = Vector` + `ViewPointRefVector = [0 0 1]` | `ViewPointReference = [0 0 1]` |
| `OrbitView` | `ViewPointVector = Vector` + `ViewPointVectorVector = [0 0 1]` | `ViewPointVector = [0 0 1]` |
| `SolarSystem` | `Ephemeris` | `EphemerisSource` |
| `Spacecraft` | `StateType` | `DisplayStateType` |
| `Thruster` | `X_Direction`/`Y_Direction`/`Z_Direction`/`Element1`/`Element2`/`Element3` | `ThrustDirection1`/`ThrustDirection2`/`ThrustDirection3` |
| `XYPlot` | `Add` | `YVariable` |
| `XYPlot` | `Grid` | `ShowGrid` |
| `XYPlot` | `IndVar` | `XVariable` |

命令语法变更：

| 命令 | 旧语法 | 新语法 |
| --- | --- | --- |
| `Propagate` | `Propagate -DefaultProp(sc)` | `Propagate BackProp DefaultProp(sc)` |

## 已修复问题

本版本关闭了 733 个 bug，其中 368 个标记为"重大"或"严重"。详见完整报告。

## 已知问题

项目的 Bugzilla 数据库中仍有 268 个未解决的 bug，其中 42 个标记为"重大"或"严重"。按平台分类概述如下（完整清单见原文 Bugzilla 数据库）：

- **多平台**：包括多次 MATLAB 运行 bug、Linux 和 Mac 上的 MATLAB 回调问题、两种报告方法的最终轨道状态不匹配、批量与单独运行结果不同、双曲线轨道的开普勒转换错误、GMAT 函数中的重大性能问题、星历传播器的大数值误差、使用非 EarthMJ2000Eq 坐标系时 STM 参数错误等。
- **Windows**：包括 MATLAB 连接问题、与 MATLAB R14 及更早版本不兼容、以 "function" 为前缀的某些行被忽略、使用大量 Propagate 命令时的潜在性能问题、GMAT 尝试写入无写权限文件夹时崩溃等。
- **Mac OS X**：包括 MATLAB→GMAT 不工作、OrbitView 纹理贴图在 Mac 上不显示、MATLAB 引擎未打开时 GMAT 崩溃、打开绘图运行 RoutineTests 时崩溃等。
- **Linux**：包括关闭时 STC 编辑器导致 GMAT 崩溃、无 MDI 子窗口打开时 Ctrl-C 导致 GMAT 崩溃。