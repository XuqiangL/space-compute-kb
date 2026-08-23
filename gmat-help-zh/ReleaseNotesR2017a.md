# GMAT R2017a 发行说明（ReleaseNotesR2017a）

> 译自 GMAT R2026a 帮助文档 ReleaseNotesR2017a.html

GMAT R2017a 于 2017 年 6 月发布。这是自 2016 年 10 月以来的第一个公开版本，是本项目的第 11 个版本。这是 Windows 上第一个 64 位版本的 GMAT（Mac 和 Linux 仅 64 位）。以下为本版本关键变更摘要；完整清单见 JIRA 上的完整 R2017a 发行说明。

## 新功能

### 轨道确定增强

GMAT 新增以下功能：

- GMAT 现在可以处理三种新数据类型：GPS 点解（GPS_PosVec）、距离数据（Range）和距离变化率（RangeRate）数据。注意，所有这些数据类型都经过了回归测试，但只有 DSN 距离数据类型经过了充分的业务测试。因此，DSN 距离数据类型是 GMAT 中验证最充分的数据类型。
- 一个经过最少测试和文档化的扩展卡尔曼滤波算法的 alpha 版本现在可供实验使用。该插件可用但默认关闭。要使用，请在启动文件中启用 "libEKF" 插件。
- 新增了二级数据编辑能力。该功能允许你选择被计算和报告但不用于估计状态更新的观测。

### STK .e 星历传播器

GMAT 现在支持使用 AGI 的 .e 星历文件格式的传播器。更多信息见 Propagator 参考文档。

### 文件管理实用程序

现在可以使用 Python 文件管理器管理经验数据更新。该实用程序允许你轻松更新闰秒、EOP、空间天气等文件，并可选归档旧版本。更多信息见"配置 GMAT 数据文件"（Configuring GMAT Data Files）一节。运行该实用程序时，你会看到类似如下的输出（以下为部分摘要）：

```
--------UPDATING GMAT LEAP SECOND FILE ------------------------------
Process Began At 2017-06-01-11:23:55
--------Downloading tai-utc.dat
tai-utc.dat downloaded successfully 
tai-utc.dat archived successfully to 2017-06-01-11h23m55s_tai-utc.dat
tai-utc.dat updated successfully
Process Finished At 2017-06-01-11:23:55

--------UPDATING GMAT EOP FILE --------------------------------
Process Began At 2017-06-01-11:23:55
--------Downloading eopc04_08.62-now
eopc04_08.62-now downloaded successfully 
eopc04_08.62-now archived successfully to 
                          2017-06-01-11h23m57s_eopc04_08.62-now
eopc04_08.62-now updated successfully

---------UPDATING SPICE LEAP SECOND FILE -----------------------
Process Began At 2017-06-01-11:23:57
--------Downloading naif0011.tls
SPICELeapSecondKernel.tls downloaded successfully
--------Downloading naif0012.tls
SPICELeapSecondKernel.tls downloaded successfully
SPICELeapSecondKernel.tls archived successfully to 
                      2017-06-01-11h24m00s_SPICELeapSecondKernel.tls
SPICELeapSecondKernel.tls updated successfully
Process Finished At 2017-06-01-11:24:00
```

以上为文件管理器依次更新 GMAT 闰秒文件、EOP 文件和 SPICE 闰秒内核时的输出：下载、归档旧版本、更新，并记录各步骤时间。

### Collocation Stand Alone Library and Toolkit（CSALT）

GMAT 现在有一个通过配点法求解最优控制问题的独立 C++ 库（CSALT）。该库经过充分测试、可用于应用，目前正在集成到 GMAT 中。CSALT 库未通过 GMAT 接口公开，但熟悉 C++ 编程的用户现在就可以用 CSALT 求解最优控制问题。源代码将通过 SourceForge 提供。CSALT 集成到 GMAT 的工作正在进行中，计划在下一个 GMAT 版本中完成。有关 CSALT 库的更多信息，见 GMAT 发行版 docs 文件夹中的 `CSALT_CollocationBenchmarkingResults.pdf` 论文。

### 初步 API 接口

一个初步的 API 正在开发中。该 API 在生产版本中不可用，在 SourceForge 上以标题中带有 "Alpha" 的包单独分发。该 API 使用 SWIG 将 GMAT 暴露给多种语言。已对从 MATLAB 调用的 JAVA 接口进行了初步测试。下面的代码片段演示了如何从 MATLAB 通过 JAVA 接口调用来计算航天器的轨道加速度。也对 Python 绑定进行了一些测试。

```matlab
% Load GMAT
scriptFileName = fullfile(pwd, 'gmat.script');
[myMod, gmatBinPath, result] = load_gmat(scriptFileName);

% Get the SolarSystem object from GMAT
ss = myMod.GetDefaultSolarSystem();

% Prepare the force model to be used for dynamics
fm = myMod.GetODEModel('DefaultProp_ForceModel');
state = gmat.GmatState(6+6^2);
fm.SetSolarSystem(ss); % Set solar system pointer in force model
fm.SetState(state); % Provide force model with the state placeholder

% Create new Spacecraft
sat = gmat.Spacecraft('Sat'); 

% Create PropagationStateManager to manage calculation of derivatives
propManager = gmat.PropagationStateManager();
propManager.SetObject(sat); % Add sat PropagationStateManager
propManager.SetProperty('AMatrix', sat); % Want to calculate Jacobian
propManager.BuildState(); 

% Tell force model to use propmanager
fm.SetPropStateManager(propManager);
fm.UpdateInitialData(); % Update model with changes
fm.BuildModelFromMap(); % Sets up the models in the force model
state = gmat.gmat.convertJavaDoubleArray(x(:,tIndex));

% Compute the orbital accelerations including variational terms
fm.GetDerivatives(state, t(tIndex), 1); % Calculate derivatives
deriv = fm.GetDerivativeArray(); % Get calculated derivatives
derivArray = gmat.gmat.convertDoubleArray(deriv, 42);
```

以上为 MATLAB 代码示例：加载 GMAT、获取太阳系对象和力模型、创建航天器和传播状态管理器，最后计算包含变分项的轨道加速度导数。

## 改进

- 现在可以通过命令行接口定义 GMAT 启动文件和日志文件的名称和位置。这在同时运行多个 GMAT 会话或有复杂的自定义文件配置时很有用。
- 现在可以写出以米（meters）为单位的 STK 星历文件（以前仅支持 km）。
- 现在可以写出不带离散事件边界的 STK 星历文件。

## 兼容性变更

- GMAT 现在要求 Python 3.6.x 版本。
- Schatten 文件不再要求文件顶部的 "PREDICTED SOLAR DATA" 关键字。
- GMAT 使用的几个数据文件的名称和位置不再硬编码，其名称和位置在 `bin` 目录中的 `gmat_startup_file.txt` 文件中设置。如果你使用自定义启动文件，必须在启动文件中添加以下行，GMAT 才能启动（GMAT 随附的启动文件已添加这些行；此向后兼容性问题仅影响自定义启动文件的用户）：

```
EARTH_LATEST_PCK_FILE    = PLANETARY_COEFF_PATH/earth_latest_high_prec.bpc
EARTH_PCK_PREDICTED_FILE = PLANETARY_COEFF_PATH/SPICEEarthPredictedKernel.bpc
EARTH_PCK_CURRENT_FILE   = PLANETARY_COEFF_PATH/SPICEEarthCurrentKernel.bpc
LUNA_PCK_CURRENT_FILE    = PLANETARY_COEFF_PATH/SPICELunaCurrentKernel.bpc
LUNA_FRAME_KERNEL_FILE   = PLANETARY_COEFF_PATH/SPICELunaFrameKernel.tf
```

- 导航功能的语法已显著更改，以在整个系统中保持一致。详见"轨道确定的跟踪数据类型"帮助中的"已弃用的测量类型名称"（Deprecated Measurement Type Names）一节。

## 已修复与已知问题

本版本关闭了 70 多个 bug。关键 bug 及解决方案清单见 "Critical Issues Fixed in R2017a" 报告；次要问题见 "Minor Issues Fixed for R2017a" 报告。

### 已知问题

影响此版本 GMAT 的所有已知问题见 JIRA 中的 "Known Issues in R2017a" 报告。本版本中几个重要的已知问题：

| ID | 描述 |
| --- | --- |
| GMT-5269 | 大气模型影响 GEO 处的传播。 |
| GMT-2561 | 闰秒期间的 UTC 历元输入和报告不正确。 |
| GMT-3043 | 创建遮蔽内置数学函数的变量时验证不一致。 |
| GMT-3289 | 使用 SPK 传播器向后传播时首步算法失败。 |
| GMT-3350 | 单引号要求在不同对象和模式间不一致。 |
| GMT-3669 | 优化期间 OrbitView 中不绘制行星。 |
| GMT-3738 | 无法在 CallMatlabFunction 中设置独立的 FuelTank、Thruster 字段。 |
| GMT-4520 | Optimize 中无关的脚本行会改变结果（导致崩溃）。 |
| GMT-4398 | 坐标系固定姿态在 SPAD SRP 模型的传播步内被保持为常数。 |
| GMT-5600 | 计算观测残差时的数值问题。 |
| GMT-6040 | 更正 RunSimulator 和 RunEstimator 命令的代码，使其遵循脚本化的传播器设置。 |
| GMT-5881 | 电离层建模中的错误。 |