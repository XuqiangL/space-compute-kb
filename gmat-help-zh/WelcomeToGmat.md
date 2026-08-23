# 欢迎使用 GMAT（Welcome to GMAT）
> 译自 GMAT R2026a 帮助文档 WelcomeToGmat.html

**第 1 章（Chapter 1）**

## 本章目录

- 功能概览（Features Overview）
  - 动力学与环境建模（Dynamics and Environment Modeling）
  - 绘图、报告与产品生成（Plotting, Reporting and Product Generation）
  - 优化与目标求解（Optimization and Targeting）
  - 编程基础设施（Programming Infrastructure）
  - 轨道确定基础设施（Orbit Determination Infrastructure）
  - 接口（Interfaces）
- 项目渊源（Heritage，见 ch01s02.html）
- 许可授权（Licensing，见 ch01s03.html）
- 平台支持（Platform Support，见 ch01s04.html）
- 组件状态（Component Status，见 ch01s05.html）
- 贡献者（Contributors，见 ch01s06.html）

通用任务分析工具（General Mission Analysis Tool，GMAT）是世界上唯一的企业级、多任务、开源软件系统，用于航天任务设计、优化与导航。该系统支持从低地球轨道到月球、平动点（libration point）及深空任务的各类飞行状态。GMAT 由 NASA、私营工业界以及公共和私人贡献者组成的团队开发，用于真实任务支持、工程研究，并作为教育与公众参与的工具。本版本的完整变更列表请参阅发行说明（release notes）。

## 功能概览（Features Overview）

GMAT 是一个功能丰富的系统，包含高保真航天系统模型、优化与目标求解、内置脚本与编程基础设施，以及可定制的绘图、报告和数据产品，从而为定制化和独特的应用提供灵活的分析与解决方案。GMAT 可通过功能完备的交互式图形界面（GUI）、自定义脚本语言或 API 驱动。下面按功能组列出 GMAT 的一些关键特性。

### 动力学与环境建模（Dynamics and Environment Modeling）

- 高保真动力学模型，包括谐波引力、大气阻力、潮汐、依赖姿态的阻力与太阳光压（SRP）、N 板 SRP 以及相对论修正
- 高保真航天器建模
- 编队与星座
- 脉冲与有限推力机动建模，以及低推力与高推力系统的优化
- 推进系统建模，包括化学推力器与电推力器
- 太阳系建模，包括高保真星历、自定义天体、平动点与质心
- 丰富的坐标系，包括 J2000、ICRF、固连坐标系、旋转坐标系、站心坐标系等
- 使用 CCSDS、SPICE、STK 与 Code 500 星历文件进行传播
- 传播器可自然同步多艘航天器的历元，避免定步长积分与插值

### 绘图、报告与产品生成（Plotting, Reporting and Product Generation）

- 交互式三维图形
- 可定制的数据绘图与报告
- 计算后动画
- CCSDS、SPK 与 Code-500 星历生成
- 食（eclipse）与地面站接触定位

### 优化与目标求解（Optimization and Targeting）

- 边值问题目标求解器
- 非线性约束优化
- 高阶配点法（collocation）
- 自定义、可脚本化的代价函数
- 自定义、可脚本化的非线性等式与不等式约束函数
- 自定义目标求解器控制量与约束

### 编程基础设施（Programming Infrastructure）

- 用户自定义变量、数组与字符串
- 使用 MATLAB 语法的用户自定义方程（即重载的数组运算）
- 用于自定义应用的控制流，如 If、For 与 While 循环
- Matlab 接口
- Python 接口
- 用户自定义函数（子例程）
- 多种坐标系下的内置参数与计算

### 轨道确定基础设施（Orbit Determination Infrastructure）

- 批处理估计器（Batch estimator）
- 扩展卡尔曼滤波器（Extended Kalman Filter）与平滑器（Smoother）
- 详尽的统计结果报告
- DSN、GN、TDRS、GPS 点解与角度数据类型
- 测量数据编辑
- 介质修正
- 过程噪声建模
- 误差建模
- 初始轨道确定（IOD）例程
- 使用 `Propagate`（传播）命令进行协方差传播

### 接口（Interfaces）

- 功能完备的交互式图形界面（GUI），使简单分析快捷易行
- 自定义脚本语言，使复杂的定制分析成为可能
- Matlab 接口，用于自定义外部仿真与计算
- Python 接口，用于自定义外部仿真与计算
- TCOPS Vector Hold File 格式的文件接口，用于加载航天器初始数据
- Python、MATLAB 与 JAVA API
- 用于批处理分析的命令行接口
