# GMAT 架构解析（NASA General Mission Analysis Tool）

> 本目录是 NASA/GMAT（General Mission Analysis Tool）开源仓库的**全分层中文架构解析文档集**。
> 分析对象：`L:\gmat888`（https://github.com/nasa/GMAT 的 main 分支 depth-1 克隆，commit `ce6eba2`）。
> 仓库规模：约 14,340 个文件（含文档与数据），其中 C++ 源码约 2,700 个，插件 26 个。

## 总目录

| 章节 | 内容 | 覆盖范围 |
|------|------|----------|
| [第1章](CH01-build-system.md) | 仓库全景与构建系统 | 根目录文件、CMakeLists、depends、ThirdParty、build、Metrics |
| [第2章](CH02-foundation.md) | src/base 核心基类层 | foundation（GmatBase/GmatGlobal/GmatTime 等）、include |
| [第3章](CH03-math.md) | 数值算法与数学库 | src/base/math（插值/矩阵/积分系数/四元数） |
| [第4章](CH04-executive-factory.md) | 执行引擎、工厂与解释器 | executive（Moderator/Sequencer/Sandbox）、factory、interpreter、plugin |
| [第5章](CH05-command.md) | 命令系统 | src/base/command（Propagate/Target/Maneuver/控制流命令） |
| [第6章](CH06-dynamics.md) | 力模型、太阳系、航天器与硬件 | forcemodel、solarsys、spacecraft、hardware |
| [第7章](CH07-propagator.md) | 传播器、机动、姿态与停止条件 | propagator、burn、attitude、stopcond、event |
| [第8章](CH08-base-subsystems.md) | 参数、函数、求解器、订阅者等 | parameter、function、solver、subscriber、coordsystem、interface、spice、api、asset、configs |
| [第9章](CH09-gui-core.md) | GUI 框架、任务树与输出界面 | gui/foundation、app、view、mission、output、debugger、controllogic |
| [第10章](CH10-gui-dynamics.md) | GUI 动力学类面板 | gui/propagator、solarsys、spacecraft、forcemodel、hardware、burn、attitude、event、coordsystem |
| [第11章](CH11-gui-commands.md) | GUI 命令、求解器、函数与其余面板 | gui/command、function、solver、subscriber、rendering、resource、asset、plugin、include |
| [第12章](CH12-applications.md) | 可执行程序与样例脚本 | src/console、application/bin、samples、output、matlab、utilities |
| [第13章](CH13-plugins-a.md) | 插件体系（上） | 13 个接口/测量/估计/传播类插件 |
| [第14章](CH14-plugins-b.md) | 插件体系（下） | 13 个跨语言/重力/TLE/工具类插件 |
| [第15章](CH15-csalt-interop-tests.md) | CSALT、api-interop、gmatutil 与测试 | csalt、csaltTester、gmatutil、TestDrivers、UnitTests、api-interop、swig |
| [第16章](CH16-docs-data-prototype.md) | 文档体系、数据内核与 prototype | doc/、application/data、prototype、ThirdParty |

[附录：全仓库文件清单](APPENDIX-all-files.md)（机器生成，覆盖全部 14,340 个文件的完整清册）。

[撰写规范](GUIDELINES.md)（内部约定，读者可跳过）。

## 仓库分层全景

```
gmat888/  (GMAT main, commit ce6eba2)
├── CMakeLists.txt ................ 顶级构建脚本（总装入口）
├── README.txt / License.txt ...... 构建说明 / NASA 开源许可
├── src/ .......................... 全部 C++ 源码
│   ├── base/       (944 文件) .... 与界面无关的核心引擎（GUI 与 Console 共用）
│   │   ├── foundation/  核心基类：GmatBase、GmatGlobal、GmatTime…
│   │   ├── executive/   执行引擎：Moderator、Sequencer、Sandbox、Publisher/Subscriber
│   │   ├── factory/     对象工厂：GmatFactory、FactoryManager、ObjectInitializer
│   │   ├── interpreter/ 脚本解释器：ScriptInterpreter、ObjectMap
│   │   ├── command/     任务命令：Propagate、Maneuver、Target、Solve、While、If…
│   │   ├── forcemodel/  力模型：ODEModel、PointMassForce、DragForce、SRP、HarmonicGravity
│   │   ├── solarsys/    太阳系：SolarSystem、CelestialBody、星历
│   │   ├── spacecraft/  航天器：Spacecraft、SpaceObject、Formation
│   │   ├── hardware/    硬件：FuelTank、Thruster、Antenna、Transmitter/Receiver…
│   │   ├── propagator/  传播器与积分器：RungeKutta89、PrinceDormand78、ABM…
│   │   ├── burn/        机动：ImpulsiveBurn、FiniteBurn
│   │   ├── attitude/    姿态：Spinner、NadirPointing…
│   │   ├── stopcond/    停止条件：Periapse、Apoapse、ElapsedTime…
│   │   ├── event/       事件定位：EventLocator
│   │   ├── parameter/   参数：Variable、Array、CalculatedParameter
│   │   ├── function/    GMAT 函数：GmatFunction、FunctionManager
│   │   ├── solver/      求解器：Targeter、DifferentialCorrector、Optimizer
│   │   ├── subscriber/  订阅者：ReportFile、EphemerisFile、XYPlot、OrbitView…
│   │   ├── coordsystem/ 坐标系：CoordinateSystem、AxisSystem
│   │   ├── math/        数值算法：插值、矩阵、旋转、积分器系数
│   │   ├── interface/   参数包装器：ElementWrapper（脚本文本 ↔ 参数值）
│   │   ├── configs/、spice/、api/、asset/、plugin/、include/ …
│   ├── gui/        (558 文件) .... wxWidgets 图形界面（所有面板）
│   ├── console/    ( 9 文件) ..... GmatConsole 控制台应用
│   ├── gmatutil/   (176 文件) .... GmatUtil 工具应用源码
│   ├── csalt/      (134 文件) .... CSALT 最优控制求解器（配点法）
│   ├── csaltTester/、TestDrivers/、UnitTests/ ...
├── application/ (890 文件)
│   ├── bin/ .......... 运行期配置：GMAT.ini、gmat_startup_file.txt、load_gmat.m、gmatpy
│   ├── data/ ......... 行星历表、EOP、大气模型、引力场等数据内核
│   ├── samples/ ...... 样例任务脚本（88 个 .script + 6 个 CSALT C++ 示例）
│   ├── output/ ....... 示例任务输出
│   ├── matlab/、utilities/、userfunctions/、userincludes/、api/、extras/ …
├── plugins/ (26 个插件, 773 文件)
│   ├── EstimationPlugin、ExtendedKalmanFilterPlugin、TLEPropagatorPlugin、
│   ├── PythonInterfacePlugin、MatlabInterfacePlugin、PolyhedronGravityPlugin、
│   ├── ProductionPropagatorPlugin、Msise00Plugin、YukonOptimizerPlugin …
├── api-interop/ (76 文件) ......... 对外 C/C++ API
├── swig/  (11 文件) ............... 脚本语言绑定
├── doc/   (8,183 文件) ............ 用户帮助 + 开发者/系统/流程文档 + 论文
├── prototype/ (1,909 文件) ........ 历史原型/实验代码
├── depends/、ThirdParty/、build/、Metrics/、moredata/ …
```

## 逻辑分层（自底向上）

```
┌────────────────────────────────────────────────────────────┐
│ 应用层     GMAT GUI (wxWidgets) / GmatConsole / GmatUtil / API │
├────────────────────────────────────────────────────────────┤
│ 任务层     脚本 .script ── ScriptInterpreter ── 命令序列        │
├────────────────────────────────────────────────────────────┤
│ 执行层     Moderator/Sequencer/Sandbox/Publisher-Subscriber │
├────────────────────────────────────────────────────────────┤
│ 领域层     传播器·力模型·航天器·坐标系·求解器·参数·订阅者        │
├────────────────────────────────────────────────────────────┤
│ 基础层     GmatBase 参数系统 · 工厂 · 时间/单位 · 数学库        │
├────────────────────────────────────────────────────────────┤
│ 数据层     DE 星历 · EOP · 大气模型 · 引力场 · 跳秒表           │
└────────────────────────────────────────────────────────────┘
```

**程序入口**：GUI 主程序由 `src/gui/app/GmatApp.cpp:87` 的 wxWidgets 宏 `IMPLEMENT_APP(GmatApp)` 生成 main；控制台版入口在 `src/console/driver.cpp:556` 的 `main()`；两者共用同一套 core 引擎。

**核心数据流**：脚本（或 GUI 面板）创建并配置对象 → Moderator 按 MissionSequence 逐个命令 Initialize/Execute → 传播器用积分器步进，力模型给出加速度 → 停止条件/事件定位决定步进终止 → 订阅者（报告/星历/绘图/3D）消费每一步状态 → Publisher 向 GUI 广播以刷新显示。

## 阅读建议

- **想快速看懂 GMAT 怎么跑起来**：先读 [第1章](CH01-build-system.md)（构建）→ [第4章](CH04-executive-factory.md)（执行引擎）→ [第5章](CH05-command.md)（命令）。
- **想研究轨道动力学**：[第6章](CH06-dynamics.md) → [第7章](CH07-propagator.md) → [第3章](CH03-math.md)。
- **想做插件/扩展**：[第4章](CH04-executive-factory.md) 的工厂与插件机制 → [第13章](CH13-plugins-a.md)/[第14章](CH14-plugins-b.md) 看 26 个真实插件范例。
- **想改 GUI**：[第9章](CH09-gui-core.md) → [第10章](CH10-gui-dynamics.md) → [第11章](CH11-gui-commands.md)。
- **想做轨道优化/参数估计**：[第8章](CH08-base-subsystems.md) 的 solver → [第15章](CH15-csalt-interop-tests.md) 的 CSALT → [第13章](CH13-plugins-a.md) 的估计插件。

## 说明

1. 本分析基于 depth-1 克隆，无 git 提交历史信息。
2. 所有行号引用以分析时的源码为准（commit `ce6eba2`）；引用代码前已用工具核实。
3. 代码文件逐文件讲解；数据/文档类文件按目录级 + 代表性深读 + 清单表覆盖（约 1.2 万文件不可能全部逐文件展开）。
4. 二进制资源（.exe/.dll/.png/.bsp 等）仅说明用途。
