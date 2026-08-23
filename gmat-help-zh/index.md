# 总索引（General Mission Analysis Tool (GMAT)）
> 译自 GMAT R2026a 帮助文档 index.html

**用户指南（User Guide）**

**GMAT 开发团队（The GMAT Development Team）**

## 目录（Table of Contents）

### [文档概述（Documentation Overview）](Preface.md)

- 使用 GMAT（Using GMAT）
- 教程（Tutorials，见 pr01s02.html）
- 参考指南（Reference Guide，见 pr01s03.html）

### 第一部分：[使用 GMAT（Using GMAT）](UsingGmat.md)

#### 1. [欢迎使用 GMAT（Welcome to GMAT）](WelcomeToGmat.md)

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

#### 2. [入门（Getting Started）](GettingStarted.md)

- 安装（Installation）
- [运行 GMAT（Running GMAT）](RunningGmat.md)
  - 启动 GMAT（Starting GMAT）
  - 退出 GMAT（Exiting GMAT）
- [示例任务（Sample Missions）](SampleMissions.md)
- [获取帮助（Getting Help）](GettingHelp.md)

#### 3. [GMAT 导览（Tour of GMAT）](TourOfGmat.md)

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

#### 4. 配置 GMAT（Configuring GMAT，见 ConfiguringGmat.html）

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

### 第二部分：教程（Tutorials，见 Tutorials.html）

#### 5. 仿真一条轨道（Simulating an Orbit，见 SimulatingAnOrbit.html）

- 目标与概述（Objective and Overview）
- 配置航天器（Configure the Spacecraft，见 ch05s02.html）
  - 重命名航天器（Rename the Spacecraft）
  - 设置航天器历元（Set the Spacecraft Epoch）
  - 设置开普勒轨道根数（Set the Keplerian Orbital Elements）
- 配置传播器（Configure the Propagator，见 ch05s03.html）
  - 重命名传播器（Rename the Propagator）
  - 配置力模型（Configure the Force Model）
  - 配置轨道视图绘图（Configuring the Orbit View Plot）
- 配置 Propagate 命令（Configure the Propagate Command，见 ch05s04.html）
- 运行并分析结果（Run and Analyze the Results，见 ch05s05.html）

#### 6. 简单轨道转移（Simple Orbit Transfer，见 SimpleOrbitTransfer.html）

- 目标与概述（Objective and Overview）
- 配置机动、微分修正器与图形（Configure Maneuvers, Differential Corrector, and Graphics，见 ch06s02.html）
  - 创建微分修正器（Create the Differential Corrector）
  - 修改默认轨道视图（Modify the Default Orbit View）
  - 创建机动（Create the Maneuvers）
- 配置任务序列（Configure the Mission Sequence，见 ch06s03.html）
  - 配置初始 Propagate 命令（Configure the Initial Propagate Command）
  - 创建 Target 序列（Create the Target Sequence）
  - 创建最终 Propagate 命令（Create the Final Propagate Command）
  - 配置 Target 序列（Configure the Target Sequence）
- 运行任务（Run the Mission，见 ch06s04.html）

#### 7. 目标求解有限推力机动以抬高远地点（Target Finite Burn to Raise Apogee，见 Tut_TargetFiniteBurn.html）

- 目标与概述（Objective and Overview）
- 创建并配置航天器硬件与有限推力机动（Create and Configure Spacecraft Hardware and Finite Burn，见 ch07s02.html）
  - 创建推力器与燃料箱（Create a Thruster and a Fuel Tank）
  - 修改 Thruster1 推力系数（Modify Thruster1 Thrust Coefficients）
  - 将 ChemicalTank1 与 Thruster1 挂接到 DefaultSC（Attach ChemicalTank1 and Thruster1 to DefaultSC）
  - 创建有限推力机动（Create the Finite Burn Maneuver）
- 创建微分修正器与目标控制变量（Create the Differential Corrector and Target Control Variable，见 ch07s03.html）
- 配置任务序列（Configure the Mission Sequence，见 ch07s04.html）
  - 配置初始 Propagate 命令（Configure the Initial Propagate Command）
  - 创建 Target 序列（Create the Target Sequence）
  - 配置 Target 序列（Configure the Target Sequence）
- 运行任务（Run the Mission，见 ch07s05.html）
  - 检查轨道视图与消息窗口（Inspect Orbit View and Message Window）
  - 查看命令摘要报告（Explore the Command Summary Reports）

#### 8. 火星 B 平面目标求解（Mars B-Plane Targeting，见 Mars_B_Plane_Targeting.html）

- 目标与概述（Objective and Overview）
- 配置燃料箱、航天器属性、机动、传播器、微分修正器、坐标系与图形（Configure Fuel Tank, Spacecraft properties, Maneuvers, Propagators, Differential Corrector, Coordinate Systems and Graphics，见 ch08s02.html）
  - 创建燃料箱（Create Fuel Tank）
  - 修改 DefaultSC 资源（Modify the DefaultSC Resource）
  - 创建机动（Create the Maneuvers）
  - 创建传播器（Create the Propagators）
  - 创建微分修正器（Create the Differential Corrector）
  - 创建坐标系（Create the Coordinate Systems）
  - 创建轨道视图（Create the Orbit Views）
- 配置任务序列（Configure the Mission Sequence，见 ch08s03.html）
  - 创建第一个 Target 序列（Create the First Target Sequence）
  - 配置第一个 Target 序列（Configure the First Target Sequence）
  - 配置 "Target desired B-plane Coordinates" 命令（Configure the Target desired B-plane Coordinates Command）
  - 配置 "Prop 3 Days" 命令（Configure the Prop 3 Days Command）
  - 配置 "Prop 12 Days to TCM" 命令（Configure the Prop 12 Days to TCM Command）
  - 配置 "Vary TCM.V" 命令（Configure the Vary TCM.V Command）
  - 配置 "Vary TCM.N" 命令（Configure the Vary TCM.N Command）
  - 配置 "Vary TCM.B" 命令（Configure the Vary TCM.B Command）
  - 配置 "Apply TCM" 命令（Configure the Apply TCM Command）
  - 配置 "Prop 280 Days" 命令（Configure the Prop 280 Days Command）
  - 配置 "Prop to Mars Periapsis" 命令（Configure the Prop to Mars Periapsis Command）
  - 配置 "Achieve BdotT" 命令（Configure the Achieve BdotT Command）
  - 配置 "Achieve BdotR" 命令（Configure the Achieve BdotR Command）
- 带第一个 Target 序列运行任务（Run the Mission with first Target Sequence，见 ch08s04.html）
  - 创建第二个 Target 序列（Create the Second Target Sequence）
  - 创建最终 Propagate 命令（Create the Final Propagate Command）
  - 配置第二个 Target 序列（Configure the second Target Sequence）
  - 配置 "Mars Capture" 命令（Configure the Mars Capture Command）
  - 配置 "Vary MOI.V" 命令（Configure the Vary MOI.V Command）
  - 配置 "Apply MOI" 命令（Configure the Apply MOI Command）
  - 配置 "Prop to Mars Apoapsis" 命令（Configure the Prop to Mars Apoapsis Command）
  - 配置 "Achieve RMAG" 命令（Configure the Achieve RMAG Command）
- 带第一、二个 Target 序列运行任务（Run the Mission with first and second Target Sequences，见 ch08s05.html）

#### 9. 使用多重打靶法的最优月球飞越（Optimal Lunar Flyby using Multiple Shooting，见 OptimalLunarFlyby.html）

- 目标与概述（Objective and Overview）
- 配置坐标系、航天器、优化器、传播器、机动、变量与图形（Configure Coordinate Systems, Spacecraft, Optimizer, Propagators, Maneuvers, Variables, and Graphics，见 ch09s02.html）
  - 创建月心坐标系（Create a Moon-centered Coordinate System）
  - 创建航天器（Create the Spacecraft）
  - 创建传播器（Create the Propagators）
  - 创建机动（Create the Maneuvers）
  - 创建用户变量（Create the User Variables）
  - 创建优化器（Create the Optimizer）
  - 创建三维图形（Create the 3-D Graphics）
  - 创建 XY 曲线图与报告（Create XYPlots and Reports）
- 配置任务序列（Configure the Mission Sequence，见 ch09s03.html）
  - 任务序列概览（Overview of the Mission Sequence）
  - 定义初始猜测（Define Initial Guesses）
  - 初始化变量（Initialize Variables）
  - 可变并设置航天器历元（Vary and Set Spacecraft Epochs）
  - 可变控制点状态（Vary Control Point States）
  - 在控制点施加约束（Apply Constraints at Control Points）
  - 传播各弧段（Propagate the Segments）
  - 计算若干量并施加拼接约束（Compute Some Quantities and Apply Patch Constraints）
  - 施加拼接点约束（Apply Patch Point Constraints）
  - 对任务轨道施加约束（Apply Constraints on Mission Orbit）
  - 应用代价函数（Apply Cost Function）
- 设计轨迹（Design the Trajectory，见 ch09s04.html）
  - 概述（Overview）
  - 第 1 步：验证您的配置（Step 1: Verify Your Configuration）
  - 第 2 步：寻找光滑轨迹（Step 2: Find a Smooth Trajectory）
  - 第 5 步：应用新约束（Step 5: Apply a New Constraint）

#### 10. 使用 GMAT 函数的火星 B 平面目标求解（Mars B-Plane Targeting Using GMAT Functions，见 Tut_UsingGMATFunctions.html）

- 目标与概述（Objective and Overview）
- 配置燃料箱、航天器属性、机动、传播器、微分修正器、坐标系与图形（Configure Fuel Tank, Spacecraft properties, Maneuvers, Propagators, Differential Corrector, Coordinate Systems and Graphics，见 ch10s02.html）
  - 创建燃料箱（Create Fuel Tank）
  - 修改 DefaultSC 资源（Modify the DefaultSC Resource）
  - 创建机动（Create the Maneuvers）
  - 创建传播器（Create the Propagators）
  - 创建微分修正器（Create the Differential Corrector）
  - 创建坐标系（Create the Coordinate Systems）
  - 创建轨道视图（Create the Orbit Views）
  - 创建单个报告文件（Create single Report File）
  - 创建一个 GMAT 函数（Create a GMAT Function）
- 配置任务序列（Configure the Mission Sequence，见 ch10s03.html）
  - 创建启动第一个 Target 序列的命令（Create Commands to Initiate the First Target Sequence）
  - 配置任务树以运行第一个 Target 序列（Configure the Mission Tree to Run the First Target Sequence）
  - 配置 "Make Objects Global" 命令（Configure the Make Objects Global Command）
  - 配置 "Target Desired B-Plane Coord. From Inside Function" 命令（Configure the Target Desired B-Plane Coord. From Inside Function Command）
  - 配置 "Report Parameters" 命令（Configure the Report Parameters Command）
- 带第一个 Target 序列运行任务（Run the Mission with first Target Sequence，见 ch10s04.html）
  - 创建第二个 Target 序列（Create the Second Target Sequence）
  - 创建最终 Propagate 命令（Create the Final Propagate Command）
  - 配置第二个 Target 序列（Configure the second Target Sequence）
  - 配置 "Mars Capture" 命令（Configure the Mars Capture Command）
  - 配置 "Vary MOI.V" 命令（Configure the Vary MOI.V Command）
  - 配置 "Apply MOI" 命令（Configure the Apply MOI Command）
  - 配置 "Prop to Mars Apoapsis" 命令（Configure the Prop to Mars Apoapsis Command）
  - 配置 "Achieve RMAG" 命令（Configure the Achieve RMAG Command）
- 带第一、二个 Target 序列运行任务（Run the Mission with first and second Target Sequences，见 ch10s05.html）

#### 11. 查找食与地面站接触（Finding Eclipses and Station Contacts，见 Tut_EventLocation.html）

- 目标与概述（Objective and Overview）
- 加载任务（Load the Mission，见 ch11s02.html）
- 配置 GMAT 进行事件定位（Configure GMAT for Event Location，见 ch11s03.html）
  - 验证太阳系配置（Verify SolarSystem Configuration）
  - 配置天体资源（Configure CelestialBody Resources）
- 配置并运行食定位器（Configure and Run the Eclipse Locator，见 ch11s04.html）
  - 创建并配置 EclipseLocator（Create and Configure the EclipseLocator）
  - 运行任务（Run the Mission）
- 配置并运行接触定位器（Configure and Run the Contact Locator，见 ch11s05.html）
  - 创建并配置地面站（Create and Configure a Ground Station）
  - 创建并配置 ContactLocator（Create and Configure the ContactLocator）
  - 运行任务（Run the Mission）
- 进一步练习（Further Exercises，见 ch11s06.html）

#### 12. 电推进（Electric Propulsion，见 Tut_ElectricPropulsion.html）

- 目标与概述（Objective and Overview）
- 创建并配置航天器硬件与有限推力机动（Create and Configure Spacecraft Hardware and Finite Burn，见 ch12s02.html）
  - 创建推力器、燃料箱与太阳能电源系统（Create a Thruster, Fuel Tank, and Solar Power System）
  - 配置硬件（Configure the Hardware）
  - 将硬件挂接到航天器（Attach Hardware to the Spacecraft）
  - 创建有限推力机动（Create the Finite Burn Maneuver）
- 配置任务序列（Configure the Mission Sequence，见 ch12s03.html）
  - 创建命令（Create the Commands）
  - 配置 Propagate 命令（Configure the Propagate Command）
- 运行任务（Run the Mission，见 ch12s04.html）

#### 13. 仿真 DSN 测距与多普勒数据（Simulate DSN Range and Doppler Data，见 Tut_Simulate_DSN_Range_and_Doppler_Data.html）

- 目标与概述（Objective and Overview）
- 创建并配置航天器、航天器应答机及相关参数（Create and configure the spacecraft, spacecraft transponder, and related parameters，见 Create_and_configure_the_spacecraft_spacecraft_transponder_and_related_parameters.html）
  - 创建卫星并设置其历元与笛卡尔坐标（Create a satellite and set its epoch and Cartesian coordinates）
  - 创建应答机对象并挂接到航天器（Create a Transponder object and attach it to our spacecraft）
- 创建并配置地面站及相关参数（Create and configure the Ground Station and related parameters，见 Create_and_configure_the_Ground_Station_and_related_parameters.html）
  - 创建地面站发射机、接收机与天线对象（Create Ground Station Transmitter, Receiver, and Antenna objects）
  - 创建地面站（Create Ground Station）
  - 创建地面站误差模型（Create Ground Station Error Models）
- 定义待仿真的测量类型（Define the types of measurements to be simulated，见 Define_the_types_of_measurements_to_be_simulated.html）
- 创建并配置力模型与传播器（Create and configure Force model and propagator，见 Create_and_configure_Force_model_and_propagator.html）
- 创建并配置仿真器对象（Create and configure Simulator object，见 Create_and_configure_Simulator_object.html）
- 运行任务并分析结果（Run the mission and analyze the results，见 Run_the_mission_and_analyze_the_results.html）
- 创建更真实的 GMAT 测量数据（GMD）（Create a more realistic GMAT Measurement Data (GMD)，见 Create_Realistic_GMD.html）
- 参考文献（References，见 ch13s09.html）
- 附录 A——测量噪声值的确定（Appendix A – Determination of Measurement Noise Values，见 Appendix_A_Determination_of_Measurement_Noise_Values.html）

#### 14. 使用 DSN 测距与多普勒数据进行轨道估计（Orbit Estimation using DSN Range and Doppler Data，见 Orbit_Estimation_using_DSN_Range_and_Doppler_Data.html）

- 目标与概述（Objective and Overview）
- 创建并配置航天器、航天器应答机及相关参数（Create and configure the spacecraft, spacecraft transponder, and related parameters，见 DSN_Estimation_Create_and_configure_the_spacecraft_spacecraft_transponder_and_related_parameters.html）
  - 创建卫星并设置其历元与笛卡尔坐标（Create a satellite and set its epoch and Cartesian coordinates）
  - 创建应答机对象并挂接到航天器（Create a Transponder object and attach it to our spacecraft）
- 创建并配置地面站及相关参数（Create and configure the Ground Station and related parameters，见 DSN_Estimation_Create_and_configure_the_Ground_Station_and_related_parameters.html）
  - 创建地面站发射机、接收机与天线对象（Create Ground Station Transmitter, Receiver, and Antenna objects）
  - 创建地面站（Create Ground Station）
  - 创建地面站误差模型（Create Ground Station Error Models）
- 定义待处理的测量类型（Define the types of measurements that will be processed，见 DSN_Estimation_Define_the_types_of_measurements_that_will_be_processed.html）
- 创建并配置力模型与传播器（Create and configure Force model and propagator，见 DSN_Estimation_Create_and_configure_Force_model_and_propagator.html）
- 创建并配置批处理估计器对象（Create and configure BatchEstimator object，见 DSN_Estimation_Create_and_configure_BatchEstimator_object.html）
- 运行任务并分析结果（Run the mission and analyze the results，见 DSN_Estimation_Run_the_mission_and_analyze_the_results.html）
  - 消息窗口输出（Message Window Output）
  - 观测残差图（Plots of Observation Residuals）
  - 批处理估计器输出报告（Batch Estimator Output Report）
  - Matlab 输出文件（Matlab Output File）
- 参考文献（References，见 ch14s08.html）
- 附录 A——GMAT 消息窗口输出（Appendix A – GMAT Message Window Output，见 DSN_Estimation_Appendix_A.html）
- 附录 B——第零次迭代观测残差图（Appendix B – Zeroth Iteration Plots of Observation Residuals，见 DSN_Estimation_Appendix_B.html）
- 附录 C——第一次迭代观测残差图（Appendix C – First Iteration Plots of Observation Residuals，见 DSN_Estimation_Appendix_C.html）
- 附录 D——修改脚本以使用地面网（GN）数据（Appendix D – Change Scripts to use Ground Network (GN) Data，见 DSN_Estimation_Appendix_D.html）

#### 15. 使用 GPS_PosVec 数据的滤波与平滑轨道确定（Filter and Smoother Orbit Determination using GPS_PosVec Data，见 FilterSmoother_GpsPosVec.html）

- 目标与概述（Objective and Overview）
- 仿真 GPS_PosVec 测量（Simulate GPS_PosVec measurements，见 ch15s02.html）
- 估计轨道（Estimate the orbit，见 ch15s03.html）
- 检查并质控滤波运行（Review and quality check the filter run，见 ch15s04.html）
- 修改估计脚本以使用平滑器改进估计（Modify the estimation script to use a smoother to improve the estimates，见 ch15s05.html）
- 检查并质控平滑运行（Review and quality check the smoother run，见 ch15s06.html）
- 热启动滤波器（Warm-start the filter，见 ch15s07.html）
- 关于滤波调参的几点说明（A few words about filter tuning，见 ch15s08.html）
- 参考文献（References，见 ch15s09.html）
- 附录 A：在运行滤波与平滑时生成星历（Appendix A. Generate an ephemeris while running the filter and smoother，见 ch15s10.html）
- 附录 B：从命令行运行脚本（Appendix B. Run the script from the command-line，见 ch15s11.html）
- 附录 C：检查协方差矩阵条件数（Appendix C. Check covariance matrix conditioning，见 ch15s12.html）

#### 16. 仿真并估计星间跟踪（Simulate and Estimate Inter-Spacecraft Tracking，见 Tut_Simulate_and_Estimate_Inter_Spacecraft_DSN_Range_and_Doppler_Data.html）

- 目标与概述（Objective and overview）
- 创建并配置航天器、航天器硬件及相关参数（Create and configure the spacecraft, spacecraft hardware, and related parameters，见 Create_and_configure_the_spacecraft_spacecraft_hardware_and_related_parameters.html）
  - 创建仿真卫星，设置其历元与笛卡尔坐标（Create the simulation satellites, set their epoch and Cartesian coordinates）
  - 创建估计卫星，设置其历元与笛卡尔坐标（Create the estimation satellites, set their epoch and Cartesian coordinates）
  - 创建应答机对象并挂接到航天器（Create a Transponder object and attach it to the spacecraft）
  - 创建接收机对象并挂接到测量航天器（Create a Receiver object and attach it to the measurement spacecraft）
- 定义待仿真的测量类型及其相关误差模型（Define the types of measurements to be simulated and their associated error models，见 Define_the_types_of_measurements_to_be_simulated_and_their_associated_error_models.html）
  - 为仿真与估计器定义跟踪文件集（Define the TrackingFileSets for the simulation and the estimator）
  - 创建测量误差模型（Create the measurement error models）
- 创建并配置力模型与传播器（Create and configure force model and propagator，见 Create_and_configure_force_model_and_propagator.html）
- 创建并配置仿真器与批处理估计器对象（Create and configure the simulator and batch estimator objects，见 Create_and_configure_simulator_and_batch_estimator_Objects.html）
  - 创建仿真器对象（Create the simulator object）
  - 创建批处理估计器对象（Create the batch estimator object）
- 运行任务并查看输出（Run the mission and review the output，见 Run_the_mission_and_analyze_the_output.html）
  - 查看仿真测量（Review the simulated measurements）
  - 查看估计器结果（Review the estimator results）
- 参考文献（References，见 ch16s07.html）

### 第三部分：[参考指南（Reference Guide）](RefGuide.md)

#### 17. API（见 ch17.html）

- 用户指南（User Guide）

#### 18. 动力学与建模（Dynamics and Modeling，见 ch18.html）

- 资源（Resources）
  - [质心（Barycenter）](Barycenter.md)——选定天体集合的质心
  - [天体（CelestialBody）](CelestialBody.md)——月球、行星、小行星与彗星对象的建模
  - [化学燃料箱（ChemicalTank）](FuelTank.md)——化学燃料箱模型
  - [化学推力器（ChemicalThruster）](Thruster.md)——化学推力器模型
  - [接触定位器（ContactLocator）](ContactLocator.md)——目标航天器（Spacecraft）与地面站（GroundStation）或行星表面区域（PlanetographicRegion）之间视线事件的定位器
  - [坐标系（CoordinateSystem）](CoordinateSystem.md)——一组坐标轴与原点的组合
  - [食定位器（EclipseLocator）](EclipseLocator.md)——航天器（Spacecraft）食事件定位器
  - [电推进燃料箱（ElectricTank）](ElectricTank.md)——电推进系统燃料贮箱模型
  - [电推力器（ElectricThruster）](ElectricThruster.md)——电推力器模型
  - [有限推力机动（FiniteBurn）](FiniteBurn.md)——一次有限推力机动
  - [视场（FieldOfView）](FieldOfView.md)——对硬件资源（Resource）的遮蔽（即视场）建模
  - [力模型（ForceModel）](ForceModel.md)——用于指定传播时的力建模选项，如引力、大气阻力、太阳光压及非中心天体
  - [编队（Formation）](Formation.md)——一组航天器的集合
  - [地面站（GroundStation）](GroundStation.md)——地面站模型
  - [成像仪（Imager）](Imager.md)——具有定义视场的成像仪
  - [脉冲机动（ImpulsiveBurn）](ImpulsiveBurn.md)——一次脉冲机动
  - [侵入定位器（IntrusionLocator）](IntrusionLocator.md)——目标天体（CelestialBody）与观测航天器（Spacecraft）之间视线事件的定位器
  - [平动点（LibrationPoint）](LibrationPoint.md)——圆型限制性三体问题中的平衡点
  - [核电源系统（NuclearPowerSystem）](NuclearPowerSystem.md)——核电源系统
  - [行星表面区域（PlanetographicRegion）](PlanetographicRegion.md)——将天体表面某一区域定义为观测航天器（Spacecraft）的目标
  - [板元（Plate）](Plate.md)——用于指定航天器单个表面（体板、太阳翼侧面或其他表面）的属性，以进行高保真太阳光压建模，包括镜面反射、漫反射与吸收效应
  - [传播器（Propagator）](Propagator.md)——传播器对航天器运动建模
  - [太阳能电源系统（SolarPowerSystem）](SolarPowerSystem.md)——太阳能电源系统模型
  - [太阳系（SolarSystem）](SolarSystem.md)——太阳系高层配置选项
  - [航天器（Spacecraft）](Spacecraft.md)——航天器模型
  - [航天器姿态（Spacecraft Attitude）](SpacecraftAttitude.md)——航天器姿态模型
  - [航天器弹道/质量特性（Spacecraft Ballistic/Mass Properties）](SpacecraftBallisticMass.md)——航天器的物理特性
  - [航天器历元（Spacecraft Epoch）](SpacecraftEpoch.md)——航天器历元
  - [航天器硬件（Spacecraft Hardware）](SpacecraftHardware.md)——为航天器添加硬件
  - [航天器轨道状态（Spacecraft Orbit State）](SpacecraftOrbitState.md)——轨道初始条件
  - [航天器可视化属性（Spacecraft Visualization Properties）](SpacecraftVisualizationProperties.md)——航天器的可视化属性
  - [推力历史文件（ThrustHistoryFile）](ThrustHistoryFile.md)——输入推力/加速度矢量与质量流率的时间历程
  - [推力段（ThrustSegment）](ThrustSegment.md)——一个或多个推力段（ThrustSegment）定义推力历史文件中数据的使用方式
- 命令（Commands，见 ch18s02.html）
  - [开始文件推力（BeginFileThrust）](BeginFileThrust.md)——应用分段连续的推力/加速度与质量流率剖面
  - [开始有限推力机动（BeginFiniteBurn）](BeginFiniteBurn.md)——对有限推力机动建模
  - [结束文件推力（EndFileThrust）](EndFileThrust.md)——应用分段连续的推力/加速度与质量流率剖面
  - [结束有限推力机动（EndFiniteBurn）](EndFiniteBurn.md)——在任务序列中对有限推力机动建模
  - [事件查找（FindEvents）](FindEvents.md)——执行事件定位搜索
  - [机动（Maneuver）](Maneuver.md)——执行脉冲（瞬时）机动
  - [传播（Propagate）](Propagate.md)——将航天器传播至指定的停止条件

#### 19. 输入/输出（Input/Output，见 ch19.html）

- 资源（Resources）
  - [动态数据显示（DynamicDataDisplay）](DynamicDataDisplay.md)——用户自定义资源，与 UpdateDynamicData 命令配合使用，将参数当前值打印到图形界面上的表格中
  - [星历文件（EphemerisFile）](EphemerisFile.md)——生成航天器的星历数据
  - [文件接口（FileInterface）](FileInterface.md)——数据文件的接口
  - [星下点轨迹（GroundTrack）](GroundTrack.md)——用户自定义资源，绘制航天器经度与纬度的时间历程
  - [OpenFrames 接口（OpenFramesInterface）](OpenFramesInterface.md)——用户自定义资源，提供 GMAT 任务的高性能三维交互可视化
  - [轨道视图（OrbitView）](OrbitView.md)——用户自定义资源，绘制三维轨迹
  - [报告文件（ReportFile）](ReportFile.md)——将数据报告到文本文件
  - [XY 曲线图（XYPlot）](XYPlot.md)——将数据绘制到图表的 X 与 Y 轴上
- 命令（Commands，见 ch19s02.html）
  - [清除绘图（ClearPlot）](ClearPlot.md)——清除 XYPlot 上的所有数据
  - [获取星历状态（GetEphemStates()）](GetEphemStates_Function.md)——从星历文件输出航天器初始与最终状态的函数
  - [标记点（MarkPoint）](MarkPoint.md)——在 XYPlot 上添加特殊标记点符号
  - [抬笔/落笔（PenUpPenDown）](PenUpPenDown.md)——停止或开始在图上绘制数据
  - [报告（Report）](Report.md)——将数据写入文本文件
  - [设置（Set）](Set.md)——从数据接口配置资源
  - [开关（Toggle）](Toggle.md)——关闭或打开数据输出
  - [更新动态数据（UpdateDynamicData）](UpdateDynamicData.md)——与 DynamicDataDisplay 配合使用的命令，更新图形界面显示表格中正在显示的数据
  - [写出（Write）](Write.md)——将数据写入以下三个目的地中的一个或多个：消息窗口、日志文件或 ReportFile 资源
- 系统（System，见 ch19s03.html）
  - [颜色（Color）](Color.md)——GMAT 资源与命令中的颜色支持

#### 20. 目标求解/参数优化（Targeting/Parameter Optimization，见 ch20.html）

- 资源（Resources）
  - [微分修正器（DifferentialCorrector）](DifferentialCorrector.md)——数值求解器
  - [fmincon 优化器（FminconOptimizer）](FminconOptimizer.md)——序列二次规划（SQP）优化器 fmincon
  - [SNOPT 优化器（SNOPT）](SNOPTOptimizer.md)——序列二次规划（SQP）优化器 SNOPT
  - [VF13ad 优化器（VF13ad）](VF13ad.md)——序列二次规划（SQP）优化器 VF13ad
  - [Yukon 优化器（Yukon）](Yukon.md)——序列二次规划（SQP）优化器 Yukon
- 命令（Commands，见 ch20s02.html）
  - [达成（Achieve）](Achieve.md)——为 Target（目标求解）序列指定目标
  - [最小化（Minimize）](Minimize.md)——定义待最小化的代价函数
  - [非线性约束（NonlinearConstraint）](NonlinearConstraint.md)——指定优化过程中使用的约束，可带可选容差，用于检查物理约束值
  - [优化（Optimize）](Optimize.md)——通过改变一个或多个参数求解条件
  - [目标求解（Target）](Target.md)——通过改变一个或多个参数求解条件
  - [变量（Vary）](Vary.md)——指定求解器使用的变量

#### 21. 轨道确定（Orbit Determination，见 ch21.html）

- 资源（Resources）
  - [接受滤波器（AcceptFilter）](AcceptFilter.md)——允许选择数据子集供批处理最小二乘估计器处理
  - [天线（Antenna）](Antenna.md)——发射或接收射频（RF）信号
  - [批处理估计器（BatchEstimator）](BatchEstimator.md)——批处理最小二乘估计器
  - [误差模型（ErrorModel）](ErrorModel.md)——用于指定仿真与估计的测量噪声，并应用或估计测量偏差
  - [待估参数（EstimatedParameter）](EstimatedParameter.md)——用于扩展卡尔曼滤波器中动态估计参数的建模
  - [扩展卡尔曼滤波器（ExtendedKalmanFilter）](ExtendedKalmanFilter.md)——扩展卡尔曼滤波轨道确定估计器
  - [过程噪声模型（ProcessNoiseModel）](ProcessNoiseModel.md)——使用 ExtendedKalmanFilter 估计器时指定估计用过程噪声
  - [接收机（Receiver）](Receiver.md)——接收射频信号的硬件
  - [拒绝滤波器（RejectFilter）](RejectFilter.md)——允许选择数据子集供批处理最小二乘估计器处理
  - [仿真器（Simulator）](Simulator.md)——配置仿真跟踪数据测量的生成
  - [平滑器（Smoother）](Smoother.md)——一种后向滤波器，通过正向与反向序贯估计的加权组合得到改进的状态估计
  - [航天器导航（Spacecraft Navigation）](SpacecraftNavigation.md)——航天器（Spacecraft）资源中有若干字段专门用于支持 GMAT 的导航（轨道确定）能力
  - [跟踪文件集（TrackingFileSet）](TrackingFileSet.md)——管理一个或多个外部跟踪数据文件中包含的观测数据
  - [发射机（Transmitter）](Transmitter.md)——定义附着于地面站（GroundStation）或航天器（Spacecraft）资源上、用于发射射频信号的电子硬件
  - [应答机（Transponder）](Transponder.md)——定义通常附着于航天器上、接收并自动转发来波信号的电子硬件
- 命令（Commands，见 ch21s02.html）
  - [运行估计器（RunEstimator）](RunEstimator.md)——读入导航测量并生成估计状态矢量
  - [运行仿真器（RunSimulator）](RunSimulator.md)——生成仿真导航测量
  - [运行平滑器（RunSmoother）](RunSmoother.md)——运行序贯平滑估计器
- 系统（System，见 ch21s03.html）
  - [轨道确定的跟踪数据类型（Tracking Data Types for Orbit Determination）](TrackingDataTypes.md)——本节描述轨道确定的跟踪数据类型与文件格式
  - [轨道确定传播器的配置（Configuration of Propagators for Orbit Determination）](NavPropagatorConfiguration.md)——本节描述为 GMAT 估计器配置数值传播器与星历传播器的一些特殊注意事项
  - [初始轨道确定（Initial Orbit Determination）](InitialOrbitDetermination.md)——一组支持早期轨道操作的 Python 函数

#### 22. 编程（Programming，见 ch22.html）

- 资源（Resources）
  - [数组（Array）](Array.md)——用户自定义的一维或二维数组变量
  - [GMAT 函数（GMATFunction）](GmatFunction.md)——GMAT 函数声明
  - [MATLAB 函数（MatlabFunction）](MatlabFunction.md)——外部 MATLAB 函数声明
  - [字符串（String）](String.md)——用户自定义字符串变量
  - [变量（Variable）](Variable.md)——用户自定义数值变量
- 命令（Commands，见 ch22s02.html）
  - [赋值（Assignment，=）](Assignment.md)——将变量或资源字段设置为某值，可使用数学表达式
  - [开始任务序列（BeginMissionSequence）](BeginMissionSequence.md)——开始脚本的任务序列部分
  - [开始脚本块（BeginScript）](BeginScript.md)——执行自由形式的脚本命令
  - [断点（Breakpoint）](Breakpoint.md)——暂停运行并让用户检查对象状态
  - [调用 GMAT 函数（CallGmatFunction）](CallGmatFunction.md)——调用 GMAT 函数
  - [调用 MATLAB 函数（CallMatlabFunction）](CallMatlabFunction.md)——调用 MATLAB 函数
  - [调用 Python 函数（CallPythonFunction）](CallPythonFunction.md)——调用 Python 函数
  - [命令回显（CommandEcho）](CommandEcho.md)——切换 Echo（回显）命令的使用
  - [For 循环（For）](For.md)——将一系列命令执行指定次数
  - [全局声明（Global）](Global.md)——将对象声明为全局
  - [If 条件（If）](If.md)——有条件地执行一系列命令
  - [停止（Stop）](Stop.md)——停止任务执行
  - [While 循环（While）](While.md)——当条件满足时重复执行一系列命令
- 系统（System，见 ch22s03.html）
  - [#Include 宏（#Include Macro）](IncludeMacro.md)——加载或导入脚本片段
  - [MATLAB 接口（MATLAB Interface）](MatlabInterface.md)——MATLAB 系统接口
  - [Python 接口（Python Interface）](PythonInterface.md)——Python 编程语言接口

#### 23. 最优控制（Optimal Control，见 ch23.html）

- 用户指南（User Guide）

#### 24. 系统（System，见 ch24.html）

- 系统级组件（System Level Components）
  - [计算参数（Calculation Parameters）](CalculationParameters.md)——可供命令与输出使用的资源属性
  - [命令行用法（Command-Line Usage）](CommandLine.md)——从命令行启动 GMAT 应用程序
  - [键盘快捷键（Keyboard Shortcuts）](KeyboardShortcuts.md)——图形用户界面中的键盘快捷键
  - [脚本语言（Script Language）](ScriptLanguage.md)——GMAT 脚本语言
  - [启动文件（Startup File）](StartupFile.md)——`gmat_startup_file.txt` 配置文件

### 附录：发行说明（Release Notes，见 ReleaseNotes.html）

- GMAT R2026a 发行说明（GMAT R2026a Release Notes）
  - 里程碑与成果（Milestones and Accomplishments）
  - 主要改进与增强（Major Improvements and Enhancements）
  - 其他改进（Other Improvements）
  - 兼容性变更（Compatibility Changes）
  - 已修复与已知问题（Fixed & Known Issues）
- GMAT R2025a 发行说明（GMAT R2025a Release Notes，见 ReleaseNotesR2025a.html）
  - 里程碑与成果（Milestones and Accomplishments）
  - 主要改进与增强（Major Improvements and Enhancements）
  - 其他改进（Other Improvements）
  - 兼容性变更（Compatibility Changes）
  - 已修复与已知问题（Fixed & Known Issues）
- GMAT R2022a 发行说明（GMAT R2022a Release Notes，见 ReleaseNotesR2022a.html）
  - 里程碑与成果（Milestones and Accomplishments）
  - 主要改进与增强（Major Improvements and Enhancements）
  - 其他改进（Other Improvements）
  - 兼容性变更（Compatibility Changes）
  - 已修复与已知问题（Fixed & Known Issues）
- GMAT R2020a 发行说明（GMAT R2020a Release Notes，见 ReleaseNotesR2020a.html）
  - 里程碑与成果（Milestones and Accomplishments）
  - 新特性（New Features）
  - 改进（Improvements）
  - 兼容性变更（Compatibility Changes）
  - 已修复与已知问题（Fixed & Known Issues）
- GMAT R2018a 发行说明（GMAT R2018a Release Notes，见 ReleaseNotesR2018a.html）
  - 里程碑与成果（Milestones and Accomplishments）
  - 新特性（New Features）
  - 改进（Improvements）
  - 兼容性变更（Compatibility Changes）
  - R2019a 即将发生的变更（Upcoming Changes in R2019a）
  - 已知与已修复问题（Known & Fixed Issues）
- GMAT R2017a 发行说明（GMAT R2017a Release Notes，见 ReleaseNotesR2017a.html）
  - 新特性（New Features）
  - 改进（Improvements）
  - 兼容性变更（Compatibility Changes）
  - GMAT 杂项（GMAT Stuff）
  - 已知与已修复问题（Known & Fixed Issues）
- GMAT R2016a 发行说明（GMAT R2016a Release Notes，见 ReleaseNotesR2016a.html）
  - 新特性（New Features）
  - 改进（Improvements）
  - 兼容性变更（Compatibility Changes）
  - 开发与工具（Development and Tools）
  - 已知与已修复问题（Known & Fixed Issues）
- GMAT R2015a 发行说明（GMAT R2015a Release Notes，见 ReleaseNotesR2015a.html）
  - 新特性（New Features）
  - 改进（Improvements）
  - 兼容性变更（Compatibility Changes）
  - 开发与工具（Development and Tools）
  - 已知与已修复问题（Known & Fixed Issues）
- GMAT R2014a 发行说明（GMAT R2014a Release Notes，见 ReleaseNotesR2014a.html）
  - 新特性（New Features）
  - 改进（Improvements）
  - 兼容性变更（Compatibility Changes）
  - 已知与已修复问题（Known & Fixed Issues）
- GMAT R2013b 发行说明（GMAT R2013b Release Notes，见 ReleaseNotesR2013b.html）
  - 新特性（New Features）
  - 改进（Improvements）
  - 兼容性变更（Compatibility Changes）
  - 已知与已修复问题（Known & Fixed Issues）
- GMAT R2013a 发行说明（GMAT R2013a Release Notes，见 ReleaseNotesR2013a.html）
  - 许可授权（Licensing）
  - 主要改进（Major Improvements）
  - 次要增强（Minor Enhancements）
  - 兼容性变更（Compatibility Changes）
  - 已知与已修复问题（Known & Fixed Issues）
- GMAT R2012a 发行说明（GMAT R2012a Release Notes，见 ReleaseNotesR2012a.html）
  - 新特性（New Features）
  - 改进（Improvements）
  - 兼容性变更（Compatibility Changes）
  - 已知与已修复问题（Known & Fixed Issues）
- GMAT R2011a 发行说明（GMAT R2011a Release Notes，见 ReleaseNotesR2011a.html）
  - 新特性（New Features）
  - 改进（Improvements）
  - 兼容性变更（Compatibility Changes）
  - 已修复问题（Fixed Issues）
  - 已知问题（Known Issues）

### [索引（Index）](BookIndex.md)

## 插图目录（List of Figures）

- 3.1 [GMAT 桌面（Windows）（GMAT Desktop (Windows)）](TourOfGmat.md)
- 3.2 [取消停靠的任务树（Undocked Mission Tree）](TourOfGmat.md)
- 3.3 [GMAT 脚本编辑器（GMAT Script Editor）](TourOfGmat.md)
- 3.4 [默认资源树（Default Resources tree）](ResourceTree.md)
- 3.5 [Spacecraft（航天器）的文件夹菜单（Folder menu for Spacecraft）](ResourceTree.md)
- 3.6 [Hardware（硬件）的文件夹菜单（Folder menu for Hardware）](ResourceTree.md)
- 3.7 [资源菜单（Resource menu）](ResourceTree.md)
- 3.8 [脚本编辑器的组成部分（Parts of the script editor）](ScriptEditor.md)
- 3.9 [活动脚本指示器（Active script indicators）](ScriptEditor.md)
- 4.1 [GMAT 根目录结构（GMAT Root Directory Structure）](ConfiguringGmat.md)
- 4.2 [GMAT 数据目录结构（GMAT Data Directory Structure）](ConfiguringGmat.md)
- 5.1 [航天器状态设置（Spacecraft State Setup）](ch05s02.md)
- 5.2 [力模型配置（Force Model Configuration）](ch05s03.md)
- 5.3 [DefaultOrbitView 配置（DefaultOrbitView Configuration）](ch05s03.md)
- 5.4 [Propagate 命令参数选择对话框配置（Propagate Command ParameterSelectDialog Configuration）](ch05s04.md)
- 5.5 [Propagate 命令配置（Propagate Command Configuration）](ch05s04.md)
- 5.6 [任务运行后的轨道视图绘图（Orbit View Plot after Mission Run）](ch05s05.md)
- 6.1 [霍曼转移的最终任务序列（Final Mission Sequence for the Hohmann Transfer）](ch06s03.md)
- 6.2 ["Prop One Day" 命令配置（Prop One Day Command Configuration）](ch06s03.md)
- 6.3 ["Vary TOI" 命令配置（Vary TOI Command Configuration）](ch06s03.md)
- 6.4 ["Perform TOI" 命令配置（Perform TOI Command Configuration）](ch06s03.md)
- 6.5 ["Prop to Apoapsis" 命令配置（Prop to Apoapsis Command Configuration）](ch06s03.md)
- 6.6 ["Achieve RMAG = 42165" 命令配置（Achieve RMAG = 42165 Command Configuration）](ch06s03.md)
- 6.7 ["Vary GOI" 参数选择（Vary GOI Parameter Selection）](ch06s03.md)
- 6.8 ["Vary GOI" 命令配置（Vary GOI Command Configuration）](ch06s03.md)
- 6.9 ["Perform GOI" 命令配置（Perform GOI Command Configuration）](ch06s03.md)
- 6.10 ["Achieve ECC = 0.005" 命令配置（Achieve ECC = 0.005 Command Configuration）](ch06s03.md)
- 6.11 [霍曼转移三维视图（3D View of Hohmann Transfer）](ch06s04.md)
- 7.1 [ChemicalTank1 配置（ChemicalTank1 Configuration）](ch07s02.md)
- 7.2 [ChemicalThruster1 配置（ChemicalThruster1 Configuration）](ch07s02.md)
- 7.3 [ChemicalThruster1 推力系数（ChemicalThruster1 Thrust Coefficients）](ch07s02.md)
- 7.4 [将 ChemicalTank1 挂接到 DefaultSC（Attach ChemicalTank1 to DefaultSC）](ch07s02.md)
- 7.5 [将 ChemicalThruster1 挂接到 DefaultSC（Attach ChemicalThruster1 to DefaultSC）](ch07s02.md)
- 7.6 [创建 FiniteBurn 资源 FiniteBurn1（Creation of FiniteBurn Resource FiniteBurn1）](ch07s02.md)
- 7.7 [创建变量资源 BurnDuration（Creation of Variable Resource, BurnDuration）](ch07s03.md)
- 7.8 ["Prop To Perigee" 命令配置（Prop To Perigee Command Configuration）](ch07s04.md)
- 7.9 [最终任务序列（Final Mission Sequence）](ch07s04.md)
- 7.10 ["Raise Apogee" 命令配置（Raise Apogee Command Configuration）](ch07s04.md)
- 7.11 ["Vary Burn Duration" 命令配置（Vary Burn Duration Command Configuration）](ch07s04.md)
- 7.12 ["Turn Thruster On" 命令配置（Turn Thruster On Command Configuration）](ch07s04.md)
- 7.13 ["Prop BurnDuration" 命令配置（Prop BurnDuration Command Configuration）](ch07s04.md)
- 7.14 ["Turn Thruster Off" 命令配置（Turn Thruster Off Command Configuration）](ch07s04.md)
- 7.15 ["Prop To Apogee" 命令配置（Prop To Apogee Command Configuration）](ch07s04.md)
- 7.16 ["Achieve Apogee Radius = 12000" 命令配置（Achieve Apogee Radius = 12000 Command Configuration）](ch07s04.md)
- 7.17 [抬高远地点有限推力机动的三维视图（3D View of Finite Burn to Raise Apogee）](ch07s05.md)
- 8.1 [从垂直于 B 平面的视点看 B 平面几何（Geometry of the B-Plane）](Mars_B_Plane_Targeting.md)
- 8.2 [从垂直于轨道面的视点看 B 矢量（The B-vector）](Mars_B_Plane_Targeting.md)
- 8.3 [第一个 Target 序列的任务序列（Mission Sequence for the First Target sequence）](ch08s03.md)
- 8.4 ["Target desired B-plane Coordinates" 命令配置](ch08s03.md)
- 8.5 ["Prop 3 Days" 命令配置（Prop 3 Days Command Configuration）](ch08s03.md)
- 8.6 ["Prop 12 Days to TCM" 命令配置（Prop 12 Days to TCM Command Configuration）](ch08s03.md)
- 8.7 ["Vary TCM.V" 命令配置（Vary TCM.V Command Configuration）](ch08s03.md)
- 8.8 ["Vary TCM.N" 参数选择（Vary TCM.N Parameter Selection）](ch08s03.md)
- 8.9 ["Vary TCM.N" 命令配置（Vary TCM.N Command Configuration）](ch08s03.md)
- 8.10 ["Vary TCM.B" 参数选择（Vary TCM.B Parameter Selection）](ch08s03.md)
- 8.11 ["Vary TCM.N" 命令配置（Vary TCM.N Command Configuration）](ch08s03.md)
- 8.12 ["Apply TCM" 命令配置（Apply TCM Command Configuration）](ch08s03.md)
- 8.13 ["Prop 280 Days" 命令配置（Prop 280 Days Command Configuration）](ch08s03.md)
- 8.14 ["Prop to Mars Periapsis" 命令配置（Prop to Mars Periapsis Command Configuration）](ch08s03.md)
- 8.15 ["Achieve BdotT" 命令配置（Achieve BdotT Command Configuration）](ch08s03.md)
- 8.16 ["Achieve BdotR" 命令配置（Achieve BdotR Command Configuration）](ch08s03.md)
- 8.17 [离开双曲线轨迹三维视图（EarthView）（3D View of departure hyperbolic trajectory）](ch08s04.md)
- 8.18 [日心转移轨迹三维视图（SolarSystemView）（3D View of heliocentric transfer trajectory）](ch08s04.md)
- 8.19 [接近双曲线轨迹三维视图，MAVEN 停在近火点（MarsView）（3D View of approach hyperbolic trajectory）](ch08s04.md)
- 8.20 [显示第一与第二个 Target 序列的任务序列（Mission Sequence showing first and second Target sequences）](ch08s04.md)
- 8.21 ["Prop for 1 day" 命令配置（Prop for 1 day Command Configuration）](ch08s04.md)
- 8.22 ["Mars Capture" 命令配置（Mars Capture Command Configuration）](ch08s04.md)
- 8.23 ["Vary MOI" 参数选择（Vary MOI Parameter Selection）](ch08s04.md)
- 8.24 ["Vary MOI" 命令配置（Vary MOI Command Configuration）](ch08s04.md)
- 8.25 ["Apply MOI" 命令配置（Apply MOI Command Configuration）](ch08s04.md)
- 8.26 ["Prop to Mars Apoapsis" 命令配置（Prop to Mars Apoapsis Command Configuration）](ch08s04.md)
- 8.27 ["Achieve RMAG" 命令配置（Achieve RMAG Command Configuration）](ch08s04.md)
- 8.28 [MOI 机动后火星捕获轨道三维视图（MarsView）（3D view of Mars Capture orbit after MOI maneuver）](ch08s05.md)
- 9.1 [从地球赤道法向看月球飞越（View of Lunar Flyby from Normal to Earth Equator）](OptimalLunarFlyby.md)
- 9.2 [月球飞越几何视图（View of Lunar Flyby Geometry）](OptimalLunarFlyby.md)
- 9.3 [控制点与拼接点的定义（Definition of Control and Patch Points）](OptimalLunarFlyby.md)
- 9.4 [不连续轨迹视图（View of Discontinuous Trajectory）](ch09s04.md)
- 9.5 [不连续轨迹备选视图（1）（Alternate View (1) of Discontinuous Trajectory）](ch09s04.md)
- 9.6 [不连续轨迹备选视图（2）（Alternate View (2) of Discontinuous Trajectory）](ch09s04.md)
- 9.7 [光滑轨迹解（Smooth Trajectory Solution）](ch09s04.md)
- 9.8 [最优轨迹解（Optimal Trajectory Solution）](ch09s04.md)
- 9.9 [使用新猜测的解（Solution Using New Guess）](ch09s04.md)
- 10.1 [从垂直于 B 平面的视点看 B 平面几何（Geometry of the B-Plane）](Tut_UsingGMATFunctions.md)
- 10.2 [从垂直于轨道面的视点看 B 矢量（The B-vector）](Tut_UsingGMATFunctions.md)
- 10.3 [第一个 Target 序列的任务序列（Mission Sequence for the First Target sequence）](ch10s03.md)
- 10.4 ["Make Objects Global" 命令配置（Make Objects Global Command Configuration）](ch10s03.md)
- 10.5 ["Target Desired B-Plane Coord. From Inside Function" 命令配置](ch10s03.md)
- 10.6 ["Report Parameters" 命令配置（Report Parameters Command Configuration）](ch10s03.md)
- 10.7 [离开双曲线轨迹三维视图（EarthView）（3D View of departure hyperbolic trajectory）](ch10s04.md)
- 10.8 [日心转移轨迹三维视图（SolarSystemView）（3D View of heliocentric transfer trajectory）](ch10s04.md)
- 10.9 [接近双曲线轨迹三维视图，MAVEN 停在近火点（MarsView）（3D View of approach hyperbolic trajectory）](ch10s04.md)
- 10.10 [显示第一与第二个 Target 序列的任务序列（Mission Sequence showing first and second Target sequences）](ch10s04.md)
- 10.11 ["Prop for 1 day" 命令配置（Prop for 1 day Command Configuration）](ch10s04.md)
- 10.12 ["Mars Capture" 命令配置（Mars Capture Command Configuration）](ch10s04.md)
- 10.13 ["Vary MOI" 参数选择（Vary MOI Parameter Selection）](ch10s04.md)
- 10.14 ["Vary MOI" 命令配置（Vary MOI Command Configuration）](ch10s04.md)
- 10.15 ["Apply MOI" 命令配置（Apply MOI Command Configuration）](ch10s04.md)
- 10.16 ["Prop to Mars Apoapsis" 命令配置（Prop to Mars Apoapsis Command Configuration）](ch10s04.md)
- 10.17 ["Achieve RMAG" 命令配置（Achieve RMAG Command Configuration）](ch10s04.md)
- 10.18 [MOI 机动后火星捕获轨道三维视图（MarsView）（3D view of Mars Capture orbit after MOI maneuver）](ch10s05.md)
- 11.1 [DefaultOrbitView 窗口（DefaultOrbitView window）](ch11s02.md)
- 11.2 [SolarSystem 面板（SolarSystem Panel）](ch11s03.md)
- 11.3 [Earth 面板（Earth Panel）](ch11s03.md)
- 11.4 [EclipseLocator 的位置（Location of EclipseLocator）](ch11s04.md)
- 11.5 [EclipseLocator 配置（EclipseLocator Configuration）](ch11s04.md)
- 11.6 [EclipseLocator 报告（EclipseLocator Report）](ch11s04.md)
- 11.7 [GroundStation 面板（GroundStation Panel）](ch11s05.md)
- 11.8 [星下点轨迹绘图窗口（Ground Track Plot Window）](ch11s05.md)
- 11.9 [ContactLocator 配置窗口（ContactLocator Configuration Window）](ch11s05.md)
- 11.10 [ContactLocator 报告（ContactLocator Report）](ch11s05.md)
- 12.1 [ElectricThruster1 配置（ElectricThruster1 Configuration）](ch12s02.md)
- 12.2 [ElectricTank1 配置（ElectricTank1 Configuration）](ch12s02.md)
- 12.3 [SolarPowerSystem1 配置（SolarPowerSystem1 Configuration）](ch12s02.md)
- 12.4 [将 ElectricTank1 挂接到 DefaultSC（Attach ElectricTank1 to DefaultSC）](ch12s02.md)
- 12.5 [将 ElectricThruster1 挂接到 DefaultSC（Attach ElectricThruster1 to DefaultSC）](ch12s02.md)
- 12.6 [将 SolarPowerSystem1 挂接到 DefaultSC（Attach SolarPowerSystem1 to DefaultSC）](ch12s02.md)
- 12.7 [创建 FiniteBurn 资源 FiniteBurn1（Creation of FiniteBurn Resource FiniteBurn1）](ch12s02.md)
- 12.8 [最终任务序列（Final Mission Sequence）](ch12s03.md)
- 12.9 ["Prop To Perigee" 命令配置（Prop To Perigee Command Configuration）](ch12s03.md)
- 12.10 [有限电推力机动三维视图（3D View of Finite Electric Maneuver）](ch12s04.md)
- 121 [敏感器锥可视化（Visualization of sensor cones）](ReleaseNotesR2020a.md)
- 122 [从月球看地球升起（Earth rise from the Moon）](ReleaseNotesR2020a.md)
- 123 [带阴影的复杂天体渲染（Rendering of complex bodies with shadows）](ReleaseNotesR2020a.md)
- 124 [近实时图形示例：惯性系与体固系视图及动态数据显示（Near real-time graphics example）](ReleaseNotesR2020a.md)

## 表格目录（List of Tables）

- 5.1 [Sat 轨道状态设置（Sat Orbit State Settings）](ch05s02.md)
- 6.1 [DefaultOrbitView 设置（DefaultOrbitView settings）](ch06s02.md)
- 6.2 [其他 Target 序列命令（Additional Target Sequence Commands）](ch06s03.md)
- 7.1 [其他 Target 序列命令（Additional Target Sequence Commands）](ch07s04.md)
- 8.1 [MainTank 设置（MainTank settings）](ch08s02.md)
- 8.2 [MAVEN 设置（MAVEN settings）](ch08s02.md)
- 8.3 [NearEarth 设置（NearEarth settings）](ch08s02.md)
- 8.4 [DeepSpace 设置（DeepSpace settings）](ch08s02.md)
- 8.5 [NearMars 设置（NearMars settings）](ch08s02.md)
- 8.6 [EarthView 设置（EarthView settings）](ch08s02.md)
- 8.7 [SolarSystemView 设置（SolarSystemView settings）](ch08s02.md)
- 8.8 [MarsView 设置（MarsView settings）](ch08s02.md)
- 8.9 [其他第一个 Target 序列命令（Additional First Target Sequence Commands）](ch08s03.md)
- 8.10 [其他第二个 Target 序列命令（Additional Second Target Sequence Commands）](ch08s04.md)
- 10.1 [MainTank 设置（MainTank settings）](ch10s02.md)
- 10.2 [MAVEN 设置（MAVEN settings）](ch10s02.md)
- 10.3 [NearEarth 设置（NearEarth settings）](ch10s02.md)
- 10.4 [DeepSpace 设置（DeepSpace settings）](ch10s02.md)
- 10.5 [NearMars 设置（NearMars settings）](ch10s02.md)
- 10.6 [EarthView 设置（EarthView settings）](ch10s02.md)
- 10.7 [SolarSystemView 设置（SolarSystemView settings）](ch10s02.md)
- 10.8 [MarsView 设置（MarsView settings）](ch10s02.md)
- 10.9 [其他第二个 Target 序列命令（Additional Second Target Sequence Commands）](ch10s04.md)
- 24 [多平台（Multiple platforms）](ReleaseNotesR2011a.md)
- 25 [Windows](ReleaseNotesR2011a.md)
- 26 [Mac OS X](ReleaseNotesR2011a.md)
- 27 [Linux](ReleaseNotesR2011a.md)
