# 教程（Tutorials）
> 译自 GMAT R2026a 帮助文档 Tutorials.html

**教程（Tutorials）** 部分包含一系列深入教程，向你展示如何使用 GMAT 进行端到端的任务分析。这些教程旨在结合真实世界的分析场景教你使用 GMAT，完成每篇教程大约需要 30 分钟到数小时不等。每篇教程的引言中都标注了难度等级、大致时长以及先修要求，教程总体按难度由易到难排列。

以下是部分精选教程的摘要。完整教程列表请参阅**教程（Tutorials）**章节目录。

- **轨道仿真（Simulating an Orbit）** 教程是你学习使用 GMAT 解决任务设计问题的第一课。你将学习如何指定轨道，并将轨道传播（propagate）至近地点（periapsis）。
- **火星 B 平面目标求解（Mars B-Plane Targeting）** 教程展示如何使用 GMAT 通过瞄准火星处的期望 B 平面（B-Plane）条件来设计火星转移轨道。
- **目标求解有限推力机动以抬升远地点（Target Finite Burn to Raise Apogee）** 教程展示如何使用有限推力机动目标求解来抬升轨道远地点。

## 目录

### 第 5 章 轨道仿真（Simulating an Orbit）

- [目标与概述](SimulatingAnOrbit.md)
- [配置航天器（Spacecraft）](ch05s02.md)
  - 重命名航天器
  - 设置航天器历元（Epoch）
  - 设置开普勒轨道根数
- [配置传播器（Propagator）](ch05s03.md)
  - 重命名传播器
  - 配置力模型（Force Model）
  - 配置轨道视图（Orbit View）图
- [配置 Propagate 命令](ch05s04.md)
- [运行并分析结果](ch05s05.md)

### 第 6 章 简单轨道转移（Simple Orbit Transfer）

- [目标与概述](SimpleOrbitTransfer.md)
- [配置机动、微分修正器与图形](ch06s02.md)
  - 创建微分修正器（Differential Corrector）
  - 修改默认轨道视图（Default Orbit View）
  - 创建机动
- [配置任务序列（Mission Sequence）](ch06s03.md)
  - 配置初始 Propagate 命令
  - 创建 Target（目标求解）序列
  - 创建最终 Propagate 命令
  - 配置 Target 序列
- [运行任务](ch06s04.md)

### 第 7 章 目标求解有限推力机动以抬升远地点（Target Finite Burn to Raise Apogee）

- [目标与概述](Tut_TargetFiniteBurn.md)
- [创建并配置航天器硬件与有限推力机动（Finite Burn）](ch07s02.md)
  - 创建推力器（Thruster）与贮箱（Fuel Tank）
  - 修改 Thruster1 的推力系数
  - 将 ChemicalTank1 与 Thruster1 挂接到 DefaultSC
  - 创建有限推力机动
- [创建微分修正器与 Target 控制变量（Variable）](ch07s03.md)
- [配置任务序列](ch07s04.md)
  - 配置初始 Propagate 命令
  - 创建 Target 序列
  - 配置 Target 序列
- [运行任务](ch07s05.md)
  - 查看轨道视图与消息窗口
  - 查看命令摘要报告

### 第 8 章 火星 B 平面目标求解（Mars B-Plane Targeting）

- [目标与概述](Mars_B_Plane_Targeting.md)
- [配置贮箱、航天器属性、机动、传播器、微分修正器、坐标系与图形](ch08s02.md)
  - 创建贮箱（Fuel Tank）
  - 修改 DefaultSC 资源
  - 创建机动
  - 创建传播器
  - 创建微分修正器
  - 创建坐标系（Coordinate System）
  - 创建轨道视图（Orbit View）
- [配置任务序列](ch08s03.md)
  - 创建第一个 Target 序列
  - 配置第一个 Target 序列
  - 配置 Target desired B-plane Coordinates 命令
  - 配置 Prop 3 Days 命令
  - 配置 Prop 12 Days to TCM 命令
  - 配置 Vary TCM.V 命令
  - 配置 Vary TCM.N 命令
  - 配置 Vary TCM.B 命令
  - 配置 Apply TCM 命令
  - 配置 Prop 280 Days 命令
  - 配置 Prop to Mars Periapsis 命令
  - 配置 Achieve BdotT 命令
  - 配置 Achieve BdotR 命令
- [运行含第一个 Target 序列的任务](ch08s04.md)
  - 创建第二个 Target 序列
  - 创建最终 Propagate 命令
  - 配置第二个 Target 序列
  - 配置 Mars Capture 命令
  - 配置 Vary MOI.V 命令
  - 配置 Apply MOI 命令
  - 配置 Prop to Mars Apoapsis 命令
  - 配置 Achieve RMAG 命令
- [运行含第一、第二个 Target 序列的任务](ch08s05.md)

### 第 9 章 基于多重打靶法的最优月球飞掠（Optimal Lunar Flyby using Multiple Shooting）

- [目标与概述](OptimalLunarFlyby.md)
- [配置坐标系、航天器、优化器、传播器、机动、变量与图形](ch09s02.md)
  - 创建月心坐标系
  - 创建航天器
  - 创建传播器
  - 创建机动
  - 创建用户变量
  - 创建优化器（Optimizer）
  - 创建三维图形
  - 创建 XYPlot 与报告
- [配置任务序列](ch09s03.md)
  - 任务序列概览
  - 定义初始猜测值
  - 初始化变量
  - Vary 并设置航天器历元
  - Vary 控制点状态
  - 在控制点处施加约束
  - 传播各弧段
  - 计算若干量并施加拼接（Patch）约束
  - 施加拼接点约束
  - 施加任务轨道约束
  - 施加代价函数
- [设计轨道](ch09s04.md)
  - 概述
  - 第 1 步：验证你的配置
  - 第 2 步：寻找一条光滑轨道
  - 第 5 步：施加一项新约束

### 第 10 章 使用 GMAT 函数进行火星 B 平面目标求解（Mars B-Plane Targeting Using GMAT Functions）

- [目标与概述](Tut_UsingGMATFunctions.md)
- [配置贮箱、航天器属性、机动、传播器、微分修正器、坐标系与图形](ch10s02.md)
  - 创建贮箱
  - 修改 DefaultSC 资源
  - 创建机动
  - 创建传播器
  - 创建微分修正器
  - 创建坐标系
  - 创建轨道视图
  - 创建单个报告文件（Report File）
  - 创建一个 GMAT 函数（GmatFunction）
- [配置任务序列](ch10s03.md)
  - 创建用于启动第一个 Target 序列的命令
  - 配置任务树（Mission tree）以运行第一个 Target 序列
  - 配置 Make Objects Global 命令
  - 配置 Target Desired B-Plane Coord. From Inside Function 命令
  - 配置 Report Parameters 命令
- [运行含第一个 Target 序列的任务](ch10s04.md)
  - 创建第二个 Target 序列
  - 创建最终 Propagate 命令
  - 配置第二个 Target 序列
  - 配置 Mars Capture 命令
  - 配置 Vary MOI.V 命令
  - 配置 Apply MOI 命令
  - 配置 Prop to Mars Apoapsis 命令
  - 配置 Achieve RMAG 命令
- [运行含第一、第二个 Target 序列的任务](ch10s05.md)

### 第 11 章 查找日食与地面站接触（Finding Eclipses and Station Contacts）

- [目标与概述](Tut_EventLocation.md)
- [加载任务](ch11s02.md)
- [配置 GMAT 以进行事件定位（Event Location）](ch11s03.md)
  - 验证 SolarSystem 配置
  - 配置 CelestialBody（天体）资源
- [配置并运行日食定位器（Eclipse Locator）](ch11s04.md)
  - 创建并配置 EclipseLocator
  - 运行任务
- [配置并运行接触定位器（Contact Locator）](ch11s05.md)
  - 创建并配置地面站（GroundStation）
  - 创建并配置 ContactLocator
  - 运行任务
- [进阶练习](ch11s06.md)

### 第 12 章 电推进（Electric Propulsion）

- [目标与概述](Tut_ElectricPropulsion.md)
- [创建并配置航天器硬件与有限推力机动](ch12s02.md)
  - 创建推力器、贮箱与太阳能电源系统（Solar Power System）
  - 配置硬件
  - 将硬件挂接到航天器
  - 创建有限推力机动
- [配置任务序列](ch12s03.md)
  - 创建命令
  - 配置 Propagate 命令
- [运行任务](ch12s04.md)

### 第 13 章 仿真 DSN 测距与多普勒数据（Simulate DSN Range and Doppler Data）

- [目标与概述](Tut_Simulate_DSN_Range_and_Doppler_Data.md)
- [创建并配置航天器、航天器转发器（Transponder）及相关参数](Create_and_configure_the_spacecraft_spacecraft_transponder_and_related_parameters.md)
  - 创建一颗卫星并设置其历元与笛卡尔坐标
  - 创建 Transponder 对象并将其挂接到航天器
- [创建并配置地面站（Ground Station）及相关参数](Create_and_configure_the_Ground_Station_and_related_parameters.md)
  - 创建地面站发射机（Transmitter）、接收机（Receiver）与天线（Antenna）对象
  - 创建地面站
  - 创建地面站误差模型（Error Model）
- [定义待仿真的测量类型](Define_the_types_of_measurements_to_be_simulated.md)
- [创建并配置力模型与传播器](Create_and_configure_Force_model_and_propagator.md)
- [创建并配置测量仿真器（Simulator）对象](Create_and_configure_Simulator_object.md)
- [运行任务并分析结果](Run_the_mission_and_analyze_the_results.md)
- [创建更真实的 GMAT 测量数据（GMD）文件](Create_Realistic_GMD.md)
- [参考文献](ch13s09.md)
- [附录 A —— 测量噪声值的确定](Appendix_A_Determination_of_Measurement_Noise_Values.md)

### 第 14 章 使用 DSN 测距与多普勒数据进行轨道估计（Orbit Estimation using DSN Range and Doppler Data）

- [目标与概述](Orbit_Estimation_using_DSN_Range_and_Doppler_Data.md)
- [创建并配置航天器、航天器转发器及相关参数](DSN_Estimation_Create_and_configure_the_spacecraft_spacecraft_transponder_and_related_parameters.md)
  - 创建一颗卫星并设置其历元与笛卡尔坐标
  - 创建 Transponder 对象并将其挂接到航天器
- [创建并配置地面站及相关参数](DSN_Estimation_Create_and_configure_the_Ground_Station_and_related_parameters.md)
  - 创建地面站发射机、接收机与天线对象
  - 创建地面站
  - 创建地面站误差模型
- [定义待处理的测量类型](DSN_Estimation_Define_the_types_of_measurements_that_will_be_processed.md)
- [创建并配置力模型与传播器](DSN_Estimation_Create_and_configure_Force_model_and_propagator.md)
- [创建并配置批处理估计器（BatchEstimator）对象](DSN_Estimation_Create_and_configure_BatchEstimator_object.md)
- [运行任务并分析结果](DSN_Estimation_Run_the_mission_and_analyze_the_results.md)
  - 消息窗口输出
  - 观测残差图
  - 批处理估计器输出报告
  - Matlab 输出文件
- [参考文献](ch14s08.md)
- [附录 A —— GMAT 消息窗口输出](DSN_Estimation_Appendix_A.md)
- [附录 B —— 第 0 次迭代的观测残差图](DSN_Estimation_Appendix_B.md)
- [附录 C —— 第 1 次迭代的观测残差图](DSN_Estimation_Appendix_C.md)
- [附录 D —— 修改脚本以使用地面网（GN）数据](DSN_Estimation_Appendix_D.md)

### 第 15 章 使用 GPS_PosVec 数据进行滤波器与平滑器轨道确定（Filter and Smoother Orbit Determination using GPS_PosVec Data）

- [目标与概述](FilterSmoother_GpsPosVec.md)
- [仿真 GPS_PosVec 测量](ch15s02.md)
- [估计轨道](ch15s03.md)
- [检查并质控滤波器运行结果](ch15s04.md)
- [修改估计脚本以使用平滑器（smoother）改进估计](ch15s05.md)
- [检查并质控平滑器运行结果](ch15s06.md)
- [滤波器热启动（Warm-start）](ch15s07.md)
- [关于滤波器调参的几点说明](ch15s08.md)
- [参考文献](ch15s09.md)
- [附录 A：在运行滤波器与平滑器的同时生成星历](ch15s10.md)
- [附录 B：从命令行运行脚本](ch15s11.md)
- [附录 C：检查协方差矩阵的条件数](ch15s12.md)

### 第 16 章 仿真与估计星间跟踪（Simulate and Estimate Inter-Spacecraft Tracking）

- [目标与概述](Tut_Simulate_and_Estimate_Inter_Spacecraft_DSN_Range_and_Doppler_Data.md)
- [创建并配置航天器、航天器硬件及相关参数](Create_and_configure_the_spacecraft_spacecraft_hardware_and_related_parameters.md)
  - 创建仿真卫星，设置其历元与笛卡尔坐标
  - 创建估计卫星，设置其历元与笛卡尔坐标
  - 创建 Transponder 对象并将其挂接到航天器
  - 创建 Receiver 对象并将其挂接到测量航天器
- [定义待仿真的测量类型及其关联误差模型](Define_the_types_of_measurements_to_be_simulated_and_their_associated_error_models.md)
  - 为仿真与估计分别定义 TrackingFileSet（跟踪文件集）
  - 创建测量误差模型
- [创建并配置力模型与传播器](Create_and_configure_force_model_and_propagator.md)
- [创建并配置测量仿真器与批处理估计器对象](Create_and_configure_simulator_and_batch_estimator_Objects.md)
  - 创建测量仿真器对象
  - 创建批处理估计器对象
- [运行任务并查看输出](Run_the_mission_and_analyze_the_output.md)
  - 查看仿真测量
  - 查看估计器结果
- [参考文献](ch16s07.md)
