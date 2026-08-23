# 参考指南（Reference Guide）
> 译自 GMAT R2026a 帮助文档 RefGuide.html

《参考指南》包含描述 GMAT 各资源（Resource）与命令（Command）的独立主题。当您需要特定功能的详细语法信息或面向具体应用的示例时，请查阅此处。它还包括系统级参考，描述脚本语言语法、参数列表、外部接口与配置文件。

## 本部分目录

### 17. API（见 ch17.html）

- 用户指南（User Guide）

### 18. 动力学与建模（Dynamics and Modeling，见 ch18.html）

#### 资源（Resources）

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

#### 命令（Commands，见 ch18s02.html）

- [开始文件推力（BeginFileThrust）](BeginFileThrust.md)——应用分段连续的推力/加速度与质量流率剖面
- [开始有限推力机动（BeginFiniteBurn）](BeginFiniteBurn.md)——对有限推力机动建模
- [结束文件推力（EndFileThrust）](EndFileThrust.md)——应用分段连续的推力/加速度与质量流率剖面
- [结束有限推力机动（EndFiniteBurn）](EndFiniteBurn.md)——在任务序列中对有限推力机动建模
- [事件查找（FindEvents）](FindEvents.md)——执行事件定位搜索
- [机动（Maneuver）](Maneuver.md)——执行脉冲（瞬时）机动
- [传播（Propagate）](Propagate.md)——将航天器传播至指定的停止条件

### 19. 输入/输出（Input/Output，见 ch19.html）

#### 资源（Resources）

- [动态数据显示（DynamicDataDisplay）](DynamicDataDisplay.md)——用户自定义资源，与 UpdateDynamicData 命令配合使用，将参数当前值打印到图形界面上的表格中
- [星历文件（EphemerisFile）](EphemerisFile.md)——生成航天器的星历数据
- [文件接口（FileInterface）](FileInterface.md)——数据文件的接口
- [星下点轨迹（GroundTrack）](GroundTrack.md)——用户自定义资源，绘制航天器经度与纬度的时间历程
- [OpenFrames 接口（OpenFramesInterface）](OpenFramesInterface.md)——用户自定义资源，提供 GMAT 任务的高性能三维交互可视化
- [轨道视图（OrbitView）](OrbitView.md)——用户自定义资源，绘制三维轨迹
- [报告文件（ReportFile）](ReportFile.md)——将数据报告到文本文件
- [XY 曲线图（XYPlot）](XYPlot.md)——将数据绘制到图表的 X 与 Y 轴上

#### 命令（Commands，见 ch19s02.html）

- [清除绘图（ClearPlot）](ClearPlot.md)——清除 XYPlot 上的所有数据
- [获取星历状态（GetEphemStates()）](GetEphemStates_Function.md)——从星历文件输出航天器初始与最终状态的函数
- [标记点（MarkPoint）](MarkPoint.md)——在 XYPlot 上添加特殊标记点符号
- [抬笔/落笔（PenUpPenDown）](PenUpPenDown.md)——停止或开始在图上绘制数据
- [报告（Report）](Report.md)——将数据写入文本文件
- [设置（Set）](Set.md)——从数据接口配置资源
- [开关（Toggle）](Toggle.md)——关闭或打开数据输出
- [更新动态数据（UpdateDynamicData）](UpdateDynamicData.md)——与 DynamicDataDisplay 配合使用的命令，更新图形界面显示表格中正在显示的数据
- [写出（Write）](Write.md)——将数据写入以下三个目的地中的一个或多个：消息窗口、日志文件或 ReportFile 资源

#### 系统（System，见 ch19s03.html）

- [颜色（Color）](Color.md)——GMAT 资源与命令中的颜色支持

### 20. 目标求解/参数优化（Targeting/Parameter Optimization，见 ch20.html）

#### 资源（Resources）

- [微分修正器（DifferentialCorrector）](DifferentialCorrector.md)——数值求解器
- [fmincon 优化器（FminconOptimizer）](FminconOptimizer.md)——序列二次规划（SQP）优化器 fmincon
- [SNOPT 优化器（SNOPT）](SNOPTOptimizer.md)——序列二次规划（SQP）优化器 SNOPT
- [VF13ad 优化器（VF13ad）](VF13ad.md)——序列二次规划（SQP）优化器 VF13ad
- [Yukon 优化器（Yukon）](Yukon.md)——序列二次规划（SQP）优化器 Yukon

#### 命令（Commands，见 ch20s02.html）

- [达成（Achieve）](Achieve.md)——为 Target（目标求解）序列指定目标
- [最小化（Minimize）](Minimize.md)——定义待最小化的代价函数
- [非线性约束（NonlinearConstraint）](NonlinearConstraint.md)——指定优化过程中使用的约束，可带可选容差，用于检查物理约束值
- [优化（Optimize）](Optimize.md)——通过改变一个或多个参数求解条件
- [目标求解（Target）](Target.md)——通过改变一个或多个参数求解条件
- [变量（Vary）](Vary.md)——指定求解器使用的变量

### 21. 轨道确定（Orbit Determination，见 ch21.html）

#### 资源（Resources）

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

#### 命令（Commands，见 ch21s02.html）

- [运行估计器（RunEstimator）](RunEstimator.md)——读入导航测量并生成估计状态矢量
- [运行仿真器（RunSimulator）](RunSimulator.md)——生成仿真导航测量
- [运行平滑器（RunSmoother）](RunSmoother.md)——运行序贯平滑估计器

#### 系统（System，见 ch21s03.html）

- [轨道确定的跟踪数据类型（Tracking Data Types for Orbit Determination）](TrackingDataTypes.md)——本节描述轨道确定的跟踪数据类型与文件格式
- [轨道确定传播器的配置（Configuration of Propagators for Orbit Determination）](NavPropagatorConfiguration.md)——本节描述为 GMAT 估计器配置数值传播器与星历传播器的一些特殊注意事项
- [初始轨道确定（Initial Orbit Determination）](InitialOrbitDetermination.md)——一组支持早期轨道操作的 Python 函数

### 22. 编程（Programming，见 ch22.html）

#### 资源（Resources）

- [数组（Array）](Array.md)——用户自定义的一维或二维数组变量
- [GMAT 函数（GMATFunction）](GmatFunction.md)——GMAT 函数声明
- [MATLAB 函数（MatlabFunction）](MatlabFunction.md)——外部 MATLAB 函数声明
- [字符串（String）](String.md)——用户自定义字符串变量
- [变量（Variable）](Variable.md)——用户自定义数值变量

#### 命令（Commands，见 ch22s02.html）

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

#### 系统（System，见 ch22s03.html）

- [#Include 宏（#Include Macro）](IncludeMacro.md)——加载或导入脚本片段
- [MATLAB 接口（MATLAB Interface）](MatlabInterface.md)——MATLAB 系统接口
- [Python 接口（Python Interface）](PythonInterface.md)——Python 编程语言接口

### 23. 最优控制（Optimal Control，见 ch23.html）

- 用户指南（User Guide）

### 24. 系统（System，见 ch24.html）

#### 系统级组件（System Level Components）

- [计算参数（Calculation Parameters）](CalculationParameters.md)——可供命令与输出使用的资源属性
- [命令行用法（Command-Line Usage）](CommandLine.md)——从命令行启动 GMAT 应用程序
- [键盘快捷键（Keyboard Shortcuts）](KeyboardShortcuts.md)——图形用户界面中的键盘快捷键
- [脚本语言（Script Language）](ScriptLanguage.md)——GMAT 脚本语言
- [启动文件（Startup File）](StartupFile.md)——`gmat_startup_file.txt` 配置文件
