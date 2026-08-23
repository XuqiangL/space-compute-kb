# 运行任务并查看输出（Run_the_mission_and_analyze_the_output）

> 译自 GMAT R2026a 帮助文档 Run_the_mission_and_analyze_the_output.html

（本小节属于"第 16 章 仿真与估计航天器间跟踪"教程）

## 查看仿真测量

用于运行任务的脚本片段如下所示。

```
BeginMissionSequence
 
RunSimulator sim
RunEstimator bat
```

**中文说明**：BeginMissionSequence 标志命令段开始；RunSimulator sim 执行测量仿真；RunEstimator bat 执行批处理估计。

第一行脚本 `BeginMissionSequence` 是必需命令，表示 GMAT 脚本的"命令"部分已开始。第二行脚本发出 `RunSimulator` 命令，以"创建测量仿真器对象"一节中定义的 `Sim` Simulator 资源为参数。这告诉 GMAT 执行 `sim` 资源指定的仿真。第三行脚本发出 `RunEstimator` 命令，以"创建批处理估计器对象"一节中定义的 `bat` 批处理估计器资源为参数。

我们现在已完成所有脚本片段。完整脚本清单请参见 GMAT samples 文件夹中的 `Tut_Inter_Spacecraft_Tracking.script` 文件。现在可以运行脚本了。点击 Save,Sync,Run 按钮。脚本需要运行片刻，GMAT 先仿真数据，然后尝试估计。

让我们看看创建的输出。创建的文件 `InterSpacecraft_Range_and_RangeRate.gmd` 在我们在"定义要仿真的测量类型及其关联误差模型"一节中创建的 `TrackingFileSet` 资源中指定。如果未指定目录，默认目录是 GMAT 安装的 'output' 目录。让我们分析这个"GMAT 测量数据"（GMD）文件的内容，如下所示。

```
% GMAT Internal Measurement Data File

25357.5003935185185185185190    Range    9029    TrackSat    ObservedSat    8.0745608409918510e+04
25357.5003935185185185185190    RangeRate    9030    { TrackSat    ObservedSat    TrackSat }    2    10    1.2080451949525264e+00
25357.5010879629629629629630    Range    9029    TrackSat    ObservedSat    8.0828956472718346e+04
25357.5010879629629629629630    RangeRate    9030    { TrackSat    ObservedSat    TrackSat }    2    10    1.5166696445321948e+00
```

**中文说明**：GMD 文件示例——每对记录为同一时刻的一条星间测距（Range，类型码 9029，单位 km）和一条星间测距变率（RangeRate，类型码 9030，路径 {TrackSat ObservedSat TrackSat}，上行频段 2=X 频段，计数区间 10 秒，单位 km/s）。

文件第一行是注释行，表明这是以 GMAT 内部格式存储测量数据的文件。有四行数据，代表两个连续时刻的测距数据和两个连续时刻的测距变率数据。第一行数据代表仿真开始时 '10 Jun 2010 00:00:00.000 UTCG' 的双向测距测量，对应输出的 TAI 约化儒略日 25357.5003935185... TAIMJD。第二和第三字段 Range 和 9029 只是 GMAT 内部代码，表示使用双向测距数据。第四字段 TrackSat 是跟踪航天器 ID，即我们给 `Spacecraft` `SimTrackSat` 对象的 ID。第五字段 ObservedSat 是被跟踪航天器 ID，即我们给创建的 `SimSat` `Spacecraft` 对象的 ID。第 6 字段 8.0745614120287588e+04 是实际的航天器间测距观测值（km）。注意，您的值会不同，因为我们向数据添加了随机噪声。

第二行数据代表仿真开始时 '10 Jun 2010 00:00:00.000 UTCG' 的双向测距变率测量，对应输出的 TAI 约化儒略日 25357.5003935185... TAIMJD。此测距变率测量与仿真测距测量同时。第二和第三字段 RangeRate 和 9030 只是 GMAT 内部代码，表示使用 RangeRate 观测类型。花括号中的字段代表测量路径——从航天器 TrackSat 到航天器 ObservedSat，再回到航天器 TrackSat。第五字段 2 是整数，代表来自 `Spacecraft` `SimTrackSat` 信号的上行频段，2 代表 X 频段。第六字段 10 是用于定义多普勒测量的多普勒计数区间（DCI）。这是我们在"定义要仿真的测量类型及其关联误差模型"一节中创建和配置 `TrackingFileSet` 对象时设置的值。回想以下脚本命令：

```
                DSNsimData.SimDopplerCountInterval = 10.0
```

**中文说明**：多普勒计数区间设为 10 秒。

第七字段 1.2080451949525264e+00 是实际的测距变率观测值（km/sec）。同样，您的值会与此处不同。

第三行数据代表 '10 Jun 2010 00:01:00.000 UTCG' 的第二个双向测距测量，对应输出的 TAI 约化儒略日时刻 25357.5010879629... TAIMJD。第四行数据代表 '10 Jun 2010 00:01:00.000 UTCG' 的第二个双向测距变率测量。后续所有行显示仿真期间每分钟（直到仿真结束 '11 Jun 2010 00:00:00.000'）的仿真测量。仿真数据中会有空缺，对应地球遮挡从地球同步轨道跟踪航天器到低地球轨道目标航天器信号的时段。

## 查看估计器结果

让我们看看 `BatchEstimator` 创建的输出。创建的文件 `InterSpacecraft_Range_and_RangeRate.txt` 在我们在"定义要仿真的测量类型及其关联误差模型"一节中创建的 `TrackingFileSet` 资源 `simData` 中指定（译注：实际在 BatchEstimator 的 ReportFile 字段指定）。如果未指定目录，默认目录是 GMAT 'output' 目录。此文件内容很多，但可归纳为三个部分。

第一部分是文件头，包含提供给估计器的初始信息以及估计中涉及对象的细节。示例如下：

```
********************  SPACECRAFT INITIAL CONDITIONS  *****************

 Spacecraft State at Beginning of Estimation :

 Spacecraft Name                            EstTrackSat                    EstSat 
 ID                                            TrackSat               ObservedSat 
                                                                                  
 Epoch (UTC)                   10 Jun 2010 00:00:00.000  10 Jun 2010 00:00:00.000 
 Coordinate System                        EarthMJ2000Eq             EarthMJ2000Eq 
 X  (km)                                -36517.05118900              576.87000000 
 Y  (km)                                -21083.12933400            -5701.14000000 
 Z  (km)                                     0.00000000            -4170.59000000 
 VX (km/s)                              -0.005964000000           -1.764508000000 
 VY (km/s)                               0.010330000000            4.181288000000 
 VZ (km/s)                               0.267968000000           -5.965790000000 
 Cr                                            1.800000                  1.800000 
 CrSigma                                  Not Estimated             Not Estimated 
 Cd                                            2.200000                  2.200000 
 CdSigma                                  Not Estimated             Not Estimated 
 DryMass  (kg)                               850.000000                850.000000 
 DragArea (m^2)                               15.000000                 15.000000 
 SRPArea  (m^2)                                1.000000                  1.000000 
```

**中文说明**：报告文件头回显两艘航天器（EstTrackSat 跟踪星、EstSat 被观测星）的初始状态——历元、坐标系、位置/速度、光压系数 Cr、阻力系数 Cd（及其 sigma，此处未估计）、干质量、阻力面积和光压面积。

第二部分是迭代部分，包含每个测量的计算估计值和所得残差。每次迭代末尾是批处理估计进展的信息，详述解是否收敛以及本次迭代与先前迭代的比较。最后一部分包含估计解，包括估计的笛卡尔坐标和解的协方差矩阵。
