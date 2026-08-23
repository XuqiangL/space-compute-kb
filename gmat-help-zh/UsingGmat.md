# 使用 GMAT（Using GMAT）
> 译自 GMAT R2026a 帮助文档 UsingGmat.html

《使用 GMAT》一章包含有关系统的高层次与入门信息。如果您需要有关如何安装和运行系统的信息、想要浏览系统全貌、想知道如何配置数据文件或 GMAT 的组织方式，请从这里开始。

《[欢迎使用 GMAT（Welcome to GMAT）](WelcomeToGmat.md)》包含简明的项目与软件概述，包括项目状态、许可授权与贡献者。

《[入门（Getting Started）](GettingStarted.md)》一节介绍如何获取并安装 GMAT、如何运行随附示例，以及从哪里获取进一步帮助。

《[GMAT 导览（Tour of GMAT）](TourOfGmat.md)》深入介绍一些关键界面特性，包括资源树（Resources tree）、任务树（Mission tree）、命令摘要（Command Summary）与脚本编辑器（Script Editor）。

《配置 GMAT（Configuring GMAT）》（见 ConfiguringGmat.html）描述 GMAT 安装目录树的内容，并提供配置 GMAT 以连接 MATLAB、Python 和自定义用户代码的说明。

> **备注（Note）**
>
> 我们认为《GMAT 导览》中的"用户界面概述（User Interfaces Overview）"一节是必读内容，因为它描述了 GMAT 工作方式的一些基本方面。

## 本部分目录

### 1. [欢迎使用 GMAT（Welcome to GMAT）](WelcomeToGmat.md)

- 功能概览（Features Overview）
  - 动力学与环境建模
  - 绘图、报告与产品生成
  - 优化与目标求解
  - 编程基础设施
  - 轨道确定基础设施
  - 接口
- 项目渊源（Heritage，见 ch01s02.html）
- 许可授权（Licensing，见 ch01s03.html）
- 平台支持（Platform Support，见 ch01s04.html）
- 组件状态（Component Status，见 ch01s05.html）
- 贡献者（Contributors，见 ch01s06.html）

### 2. [入门（Getting Started）](GettingStarted.md)

- 安装（Installation）
- [运行 GMAT（Running GMAT）](RunningGmat.md)
  - 启动 GMAT
  - 退出 GMAT
- [示例任务（Sample Missions）](SampleMissions.md)
- [获取帮助（Getting Help）](GettingHelp.md)

### 3. [GMAT 导览（Tour of GMAT）](TourOfGmat.md)

- 用户界面概述（User Interfaces Overview）
  - 图形界面概述（GUI Overview）
  - 脚本界面概述（Script Interface Overview）
  - 图形界面/脚本界面交互与规则（GUI/Script Interface Interactions and Rules）
- 资源树（Resources Tree，见 ResourceTree.html）
  - 组织结构（Organization）
  - 文件夹菜单（Folder Menus）
  - 资源菜单（Resource Menus）
- 任务树（Mission Tree，见 MissionTree.html）
  - 任务树显示（Mission Tree Display）
  - 视图过滤工具栏（View Filters Toolbar）
  - 任务序列菜单（Mission Sequence Menu）
  - 命令菜单（Command Menu）
  - 停靠/取消停靠/位置摆放（Docking/Undocking/Placement）
- 命令摘要（Command Summary，见 CommandSummary.html）
  - 数据可用性（Data Availability）
  - 数据内容（Data Contents）
  - 支持的命令（Supported Commands）
  - 坐标系（Coordinate Systems）
- 输出树（Output Tree，见 Output.html）
- 脚本编辑器（Script Editor，见 ScriptEditor.html）
  - 活动脚本（Active Script）
  - 图形界面/脚本同步（GUI/Script Synchronization）
  - 脚本列表（Scripts List）
  - 编辑窗口（Edit Window）
  - 查找与替换（Find and Replace）
  - 文件控制（File Controls）
  - 保存状态指示器（Save Status Indicator）

### 4. 配置 GMAT（Configuring GMAT，见 ConfiguringGmat.html）

- 文件结构（File Structure）
  - `api`
  - `bin`
  - `data`
  - `docs`
  - `extras`
  - `matlab`
  - `output`
  - `plugins`
  - `samples`
  - `userfunctions`
  - `userincludes`
  - `utilities`
- 配置数据文件（Configuring Data Files，见 ConfiguringGmat_DataFiles.html）
  - 加载自定义插件（Loading Custom Plugins）
  - 配置 MATLAB 接口（Configuring the MATLAB Interface）
  - 配置 Python 接口（Configuring the Python Interface）
  - 用户自定义函数路径（User-defined Function Paths）
