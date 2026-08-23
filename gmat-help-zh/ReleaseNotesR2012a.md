# GMAT R2012a 发行说明（ReleaseNotesR2012a）

> 译自 GMAT R2026a 帮助文档 ReleaseNotesR2012a.html

GMAT R2012a 于 2012 年 5 月 23 日发布。这是一年多以来的第一个公开版本，是本项目的第 5 个公开版本。在本版本中：

- 新增了 52,000 行代码
- 代码和文档由来自 2 个组织的 9 名开发者贡献
- 每个工作日夜间运行 6,847 个系统测试

这是一个 beta 版本。它在许多领域经过了广泛测试，但不被认为已可用于生产。

## 新功能

### 星下点轨迹图（Ground Track Plot）

GMAT 现在可以使用新的 `GroundTrackPlot` 资源显示航天器的星下点轨迹。该视图将一个或多个航天器的轨道路径投影到天体的二维地图上，可以使用你配置的任何天体。下面是默认任务中创建的图示例：

> [图：默认任务的星下点轨迹图]

### 轨道设计器（Orbit Designer）

有时你需要创建处于特定轨道上的航天器，但不知道确切的轨道根数值。以前，你必须粗略估计或回到数学计算。现在，GMAT R2012a 配备了新的 `Orbit Designer`（轨道设计器）为你完成这些计算。

轨道设计器帮助你创建六种不同的地心轨道类型之一，每种都有灵活的输入选项：

- 太阳同步（sun-synchronous）
- 回归太阳同步（repeat sun-synchronous）
- 回归星下点轨迹（repeat ground track）
- 地球静止（geostationary）
- 闪电轨道（molniya）
- 冻结轨道（frozen）

创建所需轨道后，它会自动导入到 Spacecraft 资源中以供后续使用。要打开轨道设计器，点击 `Spacecraft` 属性窗口上的按钮。

> [图：使用轨道设计器创建太阳同步轨道]

### 食定位器（Eclipse Locator）[alpha]

我们已在 GMAT 中实现强大的食定位工具方面做了大量工作，但这项工作尚未完成。本版本附带一个 alpha 阶段插件（默认禁用）`libEventLocator`。启用后，该插件添加一个新的 `EclipseLocator` 资源，可配置为计算相对于任何已配置航天器和天体的食进入和退出时间及持续时间。食数据可以报告到文本文件或以图形方式绘制。一些已知限制包括假设天体为球形以及缺少光行时校正。此功能未经过严格测试，可能不稳定。我们将其包含在此，作为未来版本的预览。

> [图：食定位器界面]

### C 接口 [alpha]

同样，我们包含了一个实验性库和插件，向 GMAT 的内部动力学模型功能暴露纯 C 接口。该接口旨在满足一个非常特定的需求：将 GMAT 的力模型导数暴露给外部软件（尤其是 MATLAB），以便与外部积分器一起使用（不过如果需要，GMAT 也可以进行传播）。该接口目前由 API 参考文档记录。

## 改进

### 动力学模型

我们对 GMAT 本已强大的力模型套件做了许多改进。亮点包括：

- GMAT 现在建模地球海潮和极潮。这是一个仅脚本选项，可与地球谐波重力模型一起开启；用如下行开启：

```
ForceModel.GravityField.Earth.EarthTideModel = 'SolidAndPole'
```

- 现在可以使用 `Propagator` 属性上的复选框应用相对论校正。

### 太阳系

GMAT 现在可以使用 DE421 和 DE424 星历。这些文件包含在安装程序中，但默认未激活。要使用这些星历之一，双击 `SolarSystem` 文件夹并从 `Ephemeris Source`（星历来源）列表中选择，或包含以下脚本行：

```
SolarSystem.EphemerisSource = 'DE421'
```

还有一个新的 `SolarSystem` 资源 `SolarSystemBarycenter`（太阳系质心），表示由所选星历源（DE405、DE421、SPICE 等）给出的质心。该资源可直接在报告中使用，或作为用户自定义坐标系的原点。

### TDB 输入

现在可以以 TDB 时间系统（修正儒略和格里高利两种格式）输入 `Spacecraft` 轨道的历元。

### 任务树（Mission Tree）

我们对任务树做了重大改进，使其对重度用户更加友好。最大的改进是现在可以以不同方式过滤任务序列，使复杂任务更容易理解，例如隐藏非物理事件或将树折叠到仅顶层元素。

> [图：任务树过滤器]

GMAT 现在还允许你为任务序列命令命名。因此，你可以将 "Optimize1" 和 "Propagate3" 这样的命令标记为 "Optimize LOI" 和 "Prop to Periapsis"。

> [图：带标签命令的 Ex_HohmannTransfer.script 示例]

最后，我们添加了取消停靠任务树的功能，这样你可以将它和资源树并排放置，同时查看两者。要取消停靠，右键单击 `Mission` 选项卡并将其从停靠位置拖出；要重新停靠，只需关闭新的 `Mission` 窗口。

> [图：取消停靠的任务树]

### 任务摘要（Mission Summary）

现在可以即时更改 `Mission Summary` 中显示的坐标系：只需更改窗口顶部的 `Coordinate System` 列表，数字就会更新。此功能可以使用 GMAT 中当前定义的任何坐标系，包括用户自定义的坐标系。

还有一个新的 `Mission Summary - Physics-Based Commands`（任务摘要 - 基于物理的命令），仅显示物理事件（`Propagate` 命令、机动等），并且两种任务摘要类型都添加了更多数据。

### 窗口持久性

输出窗口的位置现在随任务一起保存在脚本文件中。这意味着运行任务时，上次保存任务时打开的所有输出窗口将在其原来的位置重新出现。

此外，某些 GMAT 窗口（如任务树、脚本编辑器和应用程序窗口本身）的位置保存到用户首选项文件（`MyGMAT.ini`）中。

### Windows 上切换到 Visual Studio

从此版本开始，Windows 的官方 GMAT 二进制文件使用 Microsoft Visual Studio 2010 而非 GCC 编译。最大的好处是性能；在非官方测试中，我们在某些情况下看到了高达 50% 的性能提升。它还使 Windows 上的开发流程更符合行业标准，因为不再需要 MinGW 套件。

### 新图标

上一个版本对 GMAT 的 GUI 图标进行了重大改版。这次我们修订了一些图标并添加了更多图标，特别是在任务树中。

### 培训手册

GMAT 用户指南中的非参考材料已经过改版、部分重写和重新格式化，形成新的 GMAT 培训手册。这包括"入门"材料、一些简短的操作指南文章和一些较长的教程。所有这些信息也包含在 GMAT 用户指南中，此外还有将于今年晚些时候进行类似重写的参考材料。

### 基础设施

GMAT 项目在去年实施了几项基础设施改进。其中最大的是从旧的 Bugzilla 系统切换到 JIRA 进行问题跟踪。今年还创建了 GMAT 博客和 GMAT 插件与扩展博客，并对 wiki 和论坛进行了重组。我们重新激活了两个邮件列表 gmat-developers 和 gmat-users，并创建了一个新的邮件列表 gmat-buildtest，用于自动化的每日构建和测试更新。

## 兼容性变更

### 应用程序控制变更

GMAT 可执行文件的命令行参数已更改。替换关系见下表：

| 旧 | 新 | 描述 |
| --- | --- | --- |
| `-help` | `--help`, `-h` | 显示可用选项 |
| `-date` | `--version`, `-v` | 显示 GMAT 构建日期 |
| `-ms` | `--start-server` | 启动时启动 GMAT 服务器 |
| `-br <文件名>` | `--run`, `-r <脚本名>` | 构建并运行脚本 |
| `-minimize` | `--minimize`, `-m` | 最小化 GMAT 窗口 |
| `-exit` | `--exit`, `-x` | 脚本运行后退出 GMAT |

### 脚本语法变更

| 资源 | 字段 | 替换 |
| --- | --- | --- |
| `ForceModel` | `Drag` | `Drag.AtmosphereModel` |
| `Propagator` | `MinimumTolerance`（BulirschStoer） | （无） |

## 已修复与已知问题

本版本关闭了许多 bug，但由于从 Bugzilla 迁移到 JIRA，难以创建完整清单。部分清单见 "Bugs closed in R2012a" 报告。影响此版本 GMAT 的所有已知问题见 JIRA 中的 "Known issues in R2012a" 报告。