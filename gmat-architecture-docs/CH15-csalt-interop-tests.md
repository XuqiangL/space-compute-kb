# 第15章 CSALT 优化库、api-interop、gmatutil 与测试体系

本章范围：负责 `src/csalt/`（134 个文件）、`src/csaltTester/`（281 个文件）、`src/gmatutil/`（176 个文件）、`src/TestDrivers/`（21 个文件）、`src/UnitTests/`（143 个文件）、`api-interop/`（76 个文件）、`swig/`（11 个文件），共 **842 个文件**。主题依次为：CSALT 最优控制/配点法求解器、其独立测试驱动 csaltTester、GMAT 底层工具库 GmatUtil、两套传统测试目录（TestDrivers/UnitTests）、对外 API 互操作样例（api-interop）与 SWIG 语言绑定接口（swig）。

> 范围说明（重要）：`api-interop/` 在本快照中**不包含** C/C++ API 封装源码，而是一套“GMAT ↔ JPL Monte”Python 互操作样例与文档；真正的 C/C++ 对外 API 层位于 `src/base/api/`（`APIFunctions.hpp`/`APIException.hpp`）并被 `swig/GmatAPI.hpp` 聚合，属 base 章范围。本章对 api-interop 按“目录级说明 + 逐文件清单”覆盖，并把 API 层设计放到 swig 一节结合说明。

## 一、本章目录树

```
L:\gmat888
├─ src/csalt/                        (134)  CSALT：Collocation Stand Alone Library and Toolkit
│  ├─ CMakeLists.txt                       构建为共享库 libCSALT
│  └─ src/
│     ├─ Doxyfile                         Doxygen 配置
│     ├─ include/                   (2)  csalt.hpp / csaltdefs.hpp
│     ├─ collutils/                 (36) 决策向量、配点(transcription)数学、问题特性
│     ├─ executive/                 (20) 相位/轨迹装配、SNOPT/IPOPT 优化器封装
│     ├─ userfunutils/              (46) 用户函数(动力学/路径/点/代价)与容器、管理器
│     └─ util/                      (34) 稀疏矩阵、插值、轨迹数据、缩放、初始猜测、异常
├─ src/csaltTester/                  (281) CSALT 独立测试工程(独立可执行程序 CSALTTester)
│  ├─ CMakeLists.txt
│  └─ src/
│     ├─ HelperClasses/             (8)
│     ├─ TestOptCtrl/               (204) 核心测试壳 + drivers + pointpath + python 真值比对
│     ├─ Test{AlgNLPUtil,Barycentric...,DecisionVector,Guess,...}/  (若干独立小测试)
│     └─ python/                    (33) truth 真值文件 + 比对脚本
├─ src/gmatutil/                     (176) GmatUtil 共享库：基础类型/线性代数/时间系统/星历文件/插值/矩阵分解/数据写出
│  ├─ CMakeLists.txt
│  ├─ include/                      (2)  utildefs.hpp / DoxygenApiIntro.hpp
│  └─ util/                         (172) 含 datawriter/ interpolator/ matrixoperations/ 三个子目录
├─ src/TestDrivers/                  (21)  独立小型测试驱动(LU 分解/矩阵求逆/路径拼接)
├─ src/UnitTests/                    (143) 面向 gmatutil/base 的传统 makefile 单元测试(TestOutput 自研断言)
├─ api-interop/                      (76)  GMAT API 互操作文档 + GMAT↔Monte Python 样例
│  ├─ README-APIInteroperability.txt
│  ├─ doc/                          (31)  GmatMonte Sphinx 文档 / ModelShare 规划材料
│  └─ gmat-monte/                   (44) 数据共享:协方差/动力学/星历/机动规划 + Jupyter
└─ swig/                             (11)  SWIG 接口:Python/Java/MATLAB 三套绑定定义
```

## 二、逐文件/逐类讲解

### 2.1 CSALT 是什么（src/csalt）

CSALT 的全称写在其总入口 `src/csalt/src/include/csalt.hpp` 第 5 行的头注释里：

```cpp
// CSALT: Collocation Stand Alone Library and Toolkit
```

它是 GMAT 内嵌/并行的**直接法（配点法）最优控制求解器**：把连续时间最优控制问题（状态方程 ẋ=f(x,u,t)、路径/点约束、积分或 Mayer 代价）在离散网格上转写为有限维 NLP（非线性规划），交给稀疏 SQP 求解器 SNOPT（专有库，`src/csalt/CMakeLists.txt` 第 126~127 行链接 `SNOPT_CPPLIBRARY`/`SNOPT_LIBRARY`）求解，再经**网格细化（mesh refinement）**迭代加密网格，最后用插值把离散解还原为连续轨迹。

关键证据——`src/csalt/src/include/csalt.hpp` 第 54~59 行只暴露六个对外类，即库的“用户界面”：

```cpp
#include "ImplicitRKPhase.hpp"
#include "Phase.hpp"
#include "RadauPhase.hpp"
#include "Trajectory.hpp"
#include "UserPathFunction.hpp"
#include "UserPointFunction.hpp"
```

`csaltdefs.hpp` 第 31~45 行给出跨平台导出宏：Windows 下 `_DYNAMICLINK`+`CSALT_EXPORTS` 展开为 `__declspec(dllexport/dllimport)`，其余平台 `CSALT_API` 为空。`DEPRECATED(func)` 宏（第 57 行）在本版本被定义为恒等（弃用标注临时关闭）。

#### 2.1.1 executive 装配层（Trajectory / Phase / 优化器）

**Trajectory**（`src/csalt/src/executive/Trajectory.hpp`）是整库的“执行者”，对应 MATLAB 原型的 executive。类注释第 28~33 行明确了一条关键约定：

> Regarding Scaling: All data internally is stored in dimensional units. Scaling and unscaling is performed using the PUBLIC interface... All public interfaces assume dimensional data if flag is not passed in.

即**内部一律存有量纲数据，缩放/反缩放只发生在公共接口**。类成员一览（均经 read 确认行号）：

- `phaseList`（第 186 行）：`std::vector<Phase*>`，一个轨迹 = 多个相位；
- `decisionVector`（第 198 行）：拼接所有相位决策变量的总向量；
- `decVecStartIdx/decVecEndIdx`（第 208~210 行）：第 i 个相位的决策块起止下标；
- `totalNumConstraints`（第 220 行）与 `allConLowerBound/allConUpperBound`（第 225~228 行）：全问题约束及其界；
- `trajOptimizer`（第 279 行）：`SnoptOptimizer*`，实际求解器；
- `pointFunctionManager`（第 280 行）：`UserPointFunctionManager*`，点函数与偏导求值；
- `scaleHelper`（第 283 行）：`ScaleUtility*`，量纲/无量纲化辅助；
- `csaltExecInterface`（第 320 行）与 `csaltState`（第 322 行）：把求解状态（"Optimizing"/"MeshRefining"/"Finalizing" 等）通过 `ExecutionInterface::Publish` 推给 GMAT 的 Publisher，实现 GUI 进度回传。

公共方法分四组：初始化（`Initialize/InitializeScaleUtility/InitializePointFunctions`，第 63~65 行）、优化（`Optimize/PrepareMeshGuess/SetDecisionVector`，第 68~78 行）、访问器（`GetJacobian/GetCostConstraintFunctions/GetPhaseList`，第 81~120 行）、SNOPT 输入（`SetFeasibilityTolerances/SetMajorIterationsLimit`，第 139~146 行）。

优化主循环在 `src/csalt/src/executive/Trajectory.cpp`。调用求解器并写回决策向量的核心片段（第 780~794 行）：

```cpp
// Call the optimizer and set deciscion vector based on the output.
csaltState = "Optimizing";
if (csaltExecInterface)
   csaltExecInterface->Publish(csaltState);
SetSNOPTIterationDependentSettings(meshRefinementCount);
ResetBestFeasibleSolution();
isNewMesh = true;

// Optimize
trajOptimizer->Optimize(decVec, dvLower, dvUpper, funLower, funUpper,
                        sparsityPattern, F, xmul, Fmul, exitFlag);
SetDecisionVector(decVec);
```

- 先置 `csaltState="Optimizing"` 并 `Publish`（进度回调）；
- `SetSNOPTIterationDependentSettings(meshRefinementCount)` 按当前网格轮次选择松紧不同的容差；
- `trajOptimizer->Optimize(...)` 传入决策向量界 `dvLower/dvUpper`、目标+约束函数界 `funLower/funUpper` 与 Jacobian 稀疏模式 `sparsityPattern`，返回解 `decVec`、函数值 `F`、乘子 `xmul/Fmul` 与 `exitFlag`；
- `SetDecisionVector(decVec)` 把解写回各相位。

网格细化判定与再初始化（第 1005~1109 行）：若 `meshRefinementCount` 未达上限，逐相位调用 `phaseList.at(phaseIdx)->RefineMesh(ifUpdateMeshInterval, isMeshRefined)`（第 1023 行）；若还需细化则置 `csaltState="ReInitializingMesh"`、重新 `Initialize()` 并 `meshRefinementCount++`（第 1047/1098 行）；全部满足则 `csaltState="Finalizing"` 跳出。收敛后回退到“最可行解”并计算最大约束违反（第 1133~1141 行）：

```cpp
Integer simpleFlag = GetSimplifiedSNOPTExitFlag(optExitFlag);
if (simpleFlag != 1)
   for (UnsignedInt ii = 0; ii < numPhases; ++ii)
      phaseList.at(ii)->SetDecisionVector(bestFeasibleDecVec.at(ii));
ComputeMaxConstraintViolation(maxConViolation, costFunction);
```

**Phase**（`src/csalt/src/executive/Phase.hpp`，第 50 行）是单个相位（一段连续轨迹）的抽象基类，也是全库最核心的装配器。它持有一切单相位问题要素：`decVector`（`DecisionVector*`，第 267 行）、`config`（`ProblemCharacteristics*`，第 269 行）、`pathFunction`（`UserPathFunction*`，第 277 行）、`pathFunctionManager`（第 371 行）、`transUtil`（`NLPFuncUtil_Coll*`，第 384 行，配点数学助手）、`scaleUtil`（第 388 行）。其关键纯虚方法是 `InitializeTranscription() = 0`（第 425 行）——由子类决定“如何离散化”。Phase 提供海量 `Set/Get`（状态/控制/时间/静态参数上下界与猜测、网格区间 `SetMeshIntervalFractions` 第 122 行、`SetMeshIntervalNumPoints` 第 126 行），以及缺陷约束计算入口 `ComputeDefectConstraints`（第 208 行）、代价与雅可比访问（第 218~222 行）。

**RadauPhase**（`RadauPhase.hpp` 第 37 行）与 **ImplicitRKPhase**（`ImplicitRKPhase.hpp` 第 38 行）是两个具体离散化子类：

- RadauPhase 只重写 `InitializeTranscription()`（第 47 行），采用 **Legendre-Gauss-Radau (LGR) 配点**：每网格区间末点带状态、区间内配点带控制，其数学助手是 `NLPFuncUtilRadau`（`Phase.cpp` 内构造，`RadauPhase.cpp` 第 112 行注释 “Initialize the collocation helper class”）。
- ImplicitRKPhase 额外提供 `SetTranscription(std::string type)`（第 50 行）选择隐式 RK 变体；`ImplicitRKPhase.cpp` 第 93~99 行默认 "RungeKutta8"，并据此 `new NLPFuncUtil_ImplicitRK(collocationMethod)`，支持 RungeKutta8/6/4、HermiteSimpson、Trapezoid（见 `NLPFuncUtil_ImplicitRK.cpp` 第 565~599 行的 `SetButcherTable`）。

**OrbitPhase**（`OrbitPhase.hpp` 第 37 行 `: public RadauPhase`）是 GMAT 轨道专属相位：构造即传入 `distanceUnit/massUnit/gravParam`（第 40 行），并有 `SetThrustMode/SetStateRep/SetControlRep/SetAvailableThrust/SetIsp`（第 46~50 行）——把 GMAT 的推力模式、状态表示（笛卡尔/球坐标/修正春分点）、控制表示（如单位推力方向）翻译给 CSALT。`OrbitTrajectory`（`OrbitTrajectory.hpp` 第 37 行 `: public Trajectory`）重写 `Initialize()`，在 `OrbitTrajectory.cpp` 第 92~103 行从每个 OrbitPhase 收集 `stateReps/controlReps/thrustModes/ispVals` 并交给 OrbitPathFunction/OrbitPointFunction 装配内建动力学。

**优化器抽象与封装**：

- `OptimizerBase`（`OptimizerBase.hpp` 第 40 行）是抽象基类，声明纯虚 `Optimize(decVec, decVecLB, decVecUB, funLB, funUB, spMat, F, xmul, Fmul)`（第 59~67 行）。注释（第 24 行）说明它是 “the base class for SNOPT/IPOPT optimizer classes”，但当前实现里 SnoptOptimizer/IpoptOptimizer 都**没有**从它继承（各自独立成类），属演进中的半成品。
- `SnoptOptimizer`（`SnoptOptimizer.hpp` 第 46 行）持有一个 `snoptProblemA Problem` 成员（第 103 行，来自专有头 `snoptProblem.hpp`），并有 `SetFeasibilityTolerance/SetMajorOptimalityTolerance/SetMajorIterationsLimit`（第 67~70 行）等，把 CSALT 的容差设置映射到 SNOPT。
- `IpoptOptimizer`（`IpoptOptimizer.hpp` 第 46 行）**名字具有误导性**：它同样 `#include "snoptProblem.hpp"/"snopt.h"`（第 39~40 行）且持有 `snoptProblemA Problem`（第 89 行），实际也是 SNOPT 封装（历史遗留命名）。真正的 IPOPT 接口在 `util/IPOPTWrapper.hpp`（`class IPOPTWrapper : public Ipopt::TNLP`，第 21 行，实现 `get_nlp_info/eval_f/eval_g/eval_jac_g/eval_h` 等 TNLP 虚函数）。
- 注意 `src/csalt/CMakeLists.txt` 的 `CSALT_SRCS` 列表**只编译了 `SnoptOptimizer.cpp` 与 `SNOPTFunctionWrapper.cpp`**，`IpoptOptimizer.cpp`、`IPOPTWrapper.cpp` 未列入——即本快照实际启用的求解器是 SNOPT，IPOPT 源码存在但未接入构建。
- `SNOPTFunctionWrapper`（`util/SNOPTFunctionWrapper.hpp` 第 35~49 行）是 SNOPT 的回调函数签名：`SNOPTFunctionWrapper(Status, n, x, needF, nF, F, needG, neG, G, cu, ...)`，即求解器在每次迭代回叫 CSALT 计算目标/约束值与梯度；`StopOptimizer`（第 51~75 行）是提前终止回调。

**ExecutionInterface**（`executive/ExecutionInterface.hpp` 第 36 行）是“求解状态发布”的抽象接口：纯虚 `Publish(std::string &currState)`（第 44 行）+ `GetStateArray/GetControlArray/GetTimeArray`（第 45~47 行）。GMAT 侧用具体子类把 CSALT 的中间态/状态-控制-时间数组桥接到 Publisher（该子类在 base/插件层，不在本目录）。

#### 2.1.2 collutils 决策向量与配点数学

**DecisionVector**（`collutils/DecisionVector.hpp` 第 40 行）管理“决策向量分块”。注释第 27~29 行：*“This class manages parts of a decision vector allowing you to create a decision vector, extract parts, or set parts of the vector.”* `Initialize(nStateVars, nControlVars, nIntegralParams, nStaticParams, nStateMeshPoints, ...)`（第 54~57 行）设定各维度。它把一类变量在总向量中的起止下标做成“chunk”（`integralStartIdx/timeStartIdx/staticStartIdx` 等，第 145~155 行）。抽象方法组（第 88~102 行）要求子类给出各类变量的下标集合：`GetFinalStateIdxs/GetInitialStateIdxs/GetStateIdxsAtMeshPoint/GetStaticIdxs/GetInitialTimeIdx` 等。

**DecVecTypeBetts**（`DecVecTypeBetts.hpp` 第 42 行）是 DecisionVector 的具体编排，采用 Betts 教科书式排布，头注释第 27~30 行给出了向量结构：

```cpp
// DecVecTypeBetts DecisionVector organized similar to that used by Bett's.
//  Z = [t_o t_f y_10 u_10 y_11 u_11 ... y_nm u_nm s_1 .. s_o w_1..w_p]
```

即先初末时间，再逐网格/逐阶段交织的状态 y 与控制 u，然后是静态参数 s 与积分参数 w。成员 `hasControlAtFinalMesh`（第 87 行）区分 Hermite-Simpson（末网格点有控制）与 Radau（末点无控制）的排布差异。

**ImplicitRungeKutta**（`collutils/ImplicitRungeKutta.hpp` 第 41 行）是隐式 RK 配点的抽象基类：成员为 Butcher 表的分量 `rhoVec/sigmaMatrix/betaVec`（第 91~95 行）、`stageTimes`（第 99 行）、依赖矩阵 `paramDepArray/funcConstArray`（第 101~103 行）。纯虚 `InitializeData/LoadButcherTable/Clone`（第 82~86 行）。`GetDependencyChunk`（第 74 行）按 Betts 公式把某缺陷约束对状态/控制的依赖块（A、B 矩阵）取出。`LobattoIIIA_*` 一族（`LobattoIIIA_2Order/4HSOrder/4Order/6Order/8Order/Separated`）是它的具体子类，各自实现不同阶的 Lobatto IIIA Butcher 表；`LobattoIIIaMathUtil`（在 util 目录）提供对应的配点/求积数学。

**NLPFuncUtil 一族**是“把离散化问题组装成 NLP 函数与 Jacobian”的核心数学层：

- `NLPFuncUtil`（`collutils/NLPFuncUtil.hpp`）基类；
- `NLPFuncUtil_Coll`（`NLPFuncUtil_Coll.hpp`）配点基类，`NLPFuncUtilRadau`（Radau 配点）与 `NLPFuncUtil_ImplicitRK`（隐式 RK，含 `SetButcherTable`）派生；
- `NLPFuncUtil_Path`/`NLPFuncUtil_AlgPath`/`NLPFuncUtil_MultiPoint` 分别处理路径函数、代数路径约束、多点函数；
- `NLPFunctionData`（`collutils/NLPFunctionData.hpp`）承载一次 NLP 求值的数据封装。

**ProblemCharacteristics**（`collutils/ProblemCharacteristics.hpp` 第 37 行）是“问题特性”纯数据类：记录最优控制变量维度（状态/控制/积分/静态/时间个数，第 53~67 行）、NLP 维度（第 72~84 行）、是否含缺陷/代数路径/积分约束/积分代价（第 87~97 行）、离散化网格（`meshIntervalFractions/meshIntervalNumPoints`，第 122~127 行；注释第 219~222 行举例 `[-1 -.5 0 .5 1]` 表示 Radau 下 4 个等长分段）。它集中做 `ValidateStateProperties/ValidateMeshConfig` 等一致性校验。

#### 2.1.3 userfunutils 用户函数与容器

这一子目录定义“用户如何把动力学/约束/代价喂给 CSALT”的类型系统与求值框架。

- `UserFunction`（`UserFunction.hpp` 第 32 行附近）是所有用户函数的基类，定义 `FunctionType{COST, ALGEBRAIC, ...}`/`JacobianType{STATE, TIME, ...}`/`FunctionBound{UPPER, LOWER}` 等枚举（被 UserPathFunction/UserPointFunction 复用）。
- `UserPathFunction`（`UserPathFunction.hpp` 第 38 行）是**沿轨迹连续路径上的函数**（动力学 f、代数路径约束、积分代价被积项）。关键虚函数：`Initialize(FunctionInputData*, PathFunctionContainer*)`（第 47 行）、`EvaluateUserFunction(...)`（第 49 行）、`EvaluateUserJacobian(...)`（第 52 行）、`EvaluateJacobianPattern()`（第 63 行）。一批 `SetDynFunctions/SetAlgFunctions/SetCostFunction` 旧接口被标 `DEPRECATED`（第 66~82 行），新的通用 `SetFunctions(FunctionType, Rvector)`（第 84 行）取代之。
- `UserPointFunction`（`UserPointFunction.hpp` 第 38 行）是**离散点上的函数**（Mayer 代价、事件/边界约束）。`Initialize(initData, finalData)`（第 52 行）接收初末点输入；`AddFunctions(std::vector<OptimalControlFunction*>)`（第 55 行）挂载若干 `OptimalControlFunction`；`EvaluateUserFunction/EvaluateUserJacobian`（第 57~58 行）。
- `OptimalControlFunction`（`OptimalControlFunction.hpp` 第 41 行）是“单个最优控制函数”抽象，最贴近配点法的依赖装配：`enum VariableType{ STATE, CONTROL, TIME, STATIC }`（第 49 行）；通过 `SetPhaseDependencies/SetPointDependencies/SetStateDepMap/SetControlDepMap/SetTimeDepMap/SetParamDepMap`（第 80~85 行）声明该函数依赖哪些相位/点/状态/控制/时间/参数；`HasAnalyticJacobian`（第 53 行）与 `EvaluateAnalyticJacobian`（第 89 行）支持解析雅可比或数值雅可比（`numjac*` 工作区第 140~144 行）。`OrbitPathFunction`（`OrbitPathFunction.hpp` 第 37 行）与 `OrbitPointFunction`（第 37 行）是 GMAT 轨道内建动力学/点函数的两个子类，`SetDynamics()`（第 50 行）与 `ComputeThrust(Rvector&, Real& mdot)`（第 52 行）填充推力与质量流率。
- 数据/容器类：`FunctionInputData`（一次函数求值的输入快照）、`FunctionOutputData`（输出）、`JacobianData`（雅可比元素）、`BoundData`（上下界）、`PathFunctionContainer`/`PointFunctionContainer`（函数值+雅可比容器）、`UserFunctionProperties`（依赖/稀疏模式属性）、`PathFuncProperties`（路径函数属性）。
- 管理器：`UserFunctionManager`（基类）、`UserPathFunctionManager`、`UserPointFunctionManager`、`UserFunctionProperties`——负责驱动容器按稀疏模式求值并拼装进 NLP 雅可比。

#### 2.1.4 util 工具层

- `SparseMatrixUtil`（`util/SparseMatrixUtil.hpp`）是**稀疏优化接口**。第 55~59 行定义全库的稀疏矩阵类型别名：

```cpp
using boost::numeric::ublas::compressed_matrix;
// define RSMatrix; they can be replaced with other data types.
typedef compressed_matrix<Real> RSMatrix;
```

即 RSMatrix = Boost.uBLAS 的按行压缩矩阵。类为静态工具（第 70 行 `class SparseMatrixUtil`，构造私有不可实例化），提供 `SetElement/SetSize/SetSparsityPattern`（第 77~93 行，先置零模式后填值以避免反复 rehash）、`SetSparseBLockMatrix`（第 112~143 行，把相位 Jacobian 块拼进总矩阵）、`GetThreeVectorForm`（第 163 行，导出 row/col/value 三向量给 SNOPT 的 iGfun/jGvar）、`fast_prod`（第 207 行，稀疏×稠密向量积）、`RSMatrixToRmatrix` 转换等。
- `BaryLagrangeInterpolator`（`util/BaryLagrangeInterpolator.hpp` 第 38 行）是**插值输出**核心：`Interpolate(funcValueVec, interpPointVec, resultVec)`（第 76 行）用重心拉格朗日权重 `weigthVec`（第 99 行）与 `barycentricMatrix`（第 100 行）把配点解插到任意时刻。头注释（第 24 行）注明它刻意不继承 gmatutil 的 Interpolator 基类。
- 轨迹数据族：`TrajectoryData`（抽象轨迹数据基类）、`ArrayTrajectoryData`（数组式）、`OCHTrajectoryData`（OCH 最优控制历史文件，`.och`）、`TrajectorySegment`/`OCHTrajectorySegment`（分段）。
- 缩放：`ScaleUtility`（量纲/无量纲 + 代价/约束权重）与 `ScalingUtility`（各相位的单位换算）。
- 初始猜测：`GuessGenerator`（按 LinearNoControl/LinearUnityControl/Propagated/File 等模式生成初猜）。
- 数学：`LobattoIIIaMathUtil`/`RadauMathUtil`（配点权重/微分矩阵）、`ModEqDynamics`（修正春分点动力学）。
- 其他：`SNOPTFunctionWrapper`（见 2.1.1）、`IPOPTWrapper`（Ipopt::TNLP 实现）、`LowThrustException`（`LowThrustException.hpp` 第 38 行 `: public BaseException`，CSALT 统一异常）、`DummyPathFunction/DummyPathFunction2`（测试占位路径函数）、`SparseMatrixLibraryHeader.hpp`（稀疏头聚合）。

#### 2.1.5 “离散化 → 优化 → 插值输出”文字流程图

1. **装配**：用户派生 `UserPathFunction`/`UserPointFunction`，构造若干 `RadauPhase`（或 `ImplicitRKPhase`/`OrbitPhase`），设置网格（`SetMeshIntervalFractions/SetMeshIntervalNumPoints`）与状态/控制/时间上下界，`phaseList.push_back` 后交给 `Trajectory`。
2. **离散化（InitializeTranscription）**：每个 Phase 调用纯虚 `InitializeTranscription()`，用 `NLPFuncUtilRadau`/`NLPFuncUtil_ImplicitRK` 生成配点、求积权重与微分矩阵，构造 `DecisionVector`（Betts 排布）并算好各 chunk 下标，同时填 `ProblemCharacteristics`。
3. **NLP 装配**：`Phase::InitializeNLPHelpers`/`ComputeSparsityPattern` 依据 `UserFunctionProperties` 的依赖映射计算 Jacobian 稀疏模式；`Trajectory::SetChunkIndexes/SetBounds/SetSparsityPattern` 把所有相位拼接成总决策向量、总约束向量与总 `sparsityPattern`。
4. **优化**：`Trajectory::Optimize` 循环调用 `trajOptimizer->Optimize(...)`（SNOPT 经 `SNOPTFunctionWrapper` 回调 `GetCostConstraintFunctions`/`GetJacobian`），解出 `decVec` 后 `SetDecisionVector`。
5. **网格细化**：`Phase::RefineMesh` 依据 `ComputeMaxMeshError` 的区间相对误差决定是否加密/重配点；需要则 `Initialize()` 重来并 `meshRefinementCount++`，直到满足或达 `maxMeshRefinementCount`。
6. **插值输出**：收敛后用 `BaryLagrangeInterpolator` 或 `DecisionVector::GetInterpolatedStateVector/GetInterpolatedControlVector`（`DecisionVector.hpp` 第 84~85 行）把离散解插值成连续状态/控制；`OCHTrajectoryData::WriteToFile` 可写出 `.och` 轨迹文件。

### 2.2 csaltTester：CSALT 测试驱动

`src/csaltTester/` 是 CSALT 的**独立测试工程**，构建为可执行程序 `CSALTTester`（`CMakeLists.txt` 第 25 行 `SET(TargetName CSALTTester)`，第 132 行 `ADD_EXECUTABLE`），链接 `CSALT + GmatUtil + SNOPT`（第 147~148 行）。

它不是一个用 CppUnit 的框架，而是**自研的“驱动类 + 菜单选择”**结构：`TestOptCtrl.cpp` 的 `main()`（第 56 行）解析 `-run <用例名>` 参数，逐个 `new XxxDriver(); driver->Run(); delete driver;`（第 93~120 行展示 Brachistochrone/HyperSensitive/Rayleigh/... 22 个 driver 的“All”分支）。文件头第 25~38 行给出了**新增用例的标准步骤**（改 `testcases.hpp` 加 include、加菜单项、在 All 分支加三行）。

每个 driver 遵循统一模板（以 `drivers/HyperSensitiveDriver.cpp` 为例）：

- `SetPointPathAndProperties()`（第 52 行）设置代价下界、网格细化轮数、各轮 SNOPT 容差序列（`majorOptimalityTolerances/feasibilityTolerances/majorIterationsLimits`，第 59~77 行）；
- `SetupPhases()`（第 81 行）构造 `RadauPhase`、设 `meshIntervalFractions` 与 `meshIntervalNumPoints`（第 87~92 行）、状态/控制/时间上下界与猜测（第 101~132 行）。

`drivers/` 下每个经典最优控制基准问题对应一个 Driver + 一对 Point/Path Object：Brachistochrone（最速降线）、BrysonDenham、BrysonMaxRange、GoddardRocket（含三相位版）、HyperSensitive、Rayleigh、MoonLander、HohmannTransfer、LinearTangentSteering（含静态参数版）、ObstacleAvoidance、Hull95、BangBang、Schwartz、InteriorPoint、RauAutomatica、ConwayOrbitExample(RK)、CatalyticGasOilCracker、Tutorial、OrbitRaising(MultiPhase) 等——覆盖配点法教材中的标准验证算例。

`src/python/` 是**真值比对测试**：`SetupTruth.py` 生成 `truth/*.truth` 与 `truth/*Data.snopt` 基准（共 21 组），`TestCSALT.py`/`SNOPTComparator.py`/`OCHComparator.py`/`SetupCompare.py` 把 CSALT 输出与基准对比；`LagrangeInterpolator.py`/`TestInterpolator.py` 验证插值器；`StringUtil.py`/`DataFileReader.py` 是辅助工具。

其余目录为历史遗留的小型独立测试（各有独立 `Makefile`，不在主 CMake 工程内）：`TestDecisionVector`、`TestBrachistichrone`、`TestHyperSensitive`、`TestGuess`、`TestInterpolation`、`TestOptimizer`、`TestPhase`、`TestOrbitRaisingMultiPhase`、`TestRauAutomatica`、`TestRayleigh`、`TestTrajectoryData`、`TestUserPathFunction`、`TestIpoptInterface`、`TestLobattoIIIaMathUtil`、`TestNLPFunctionData` 等（详见附录表）。

### 2.3 gmatutil：GmatUtil 应用（工具集）

`src/gmatutil/` 构建为共享库 **GmatUtil**（`CMakeLists.txt` 第 16 行 `SET(TargetName GmatUtil)`，第 128 行 `ADD_LIBRARY(... SHARED ...)`）。它不是“应用”而是 GMAT 最底层的**无 GUI、无依赖基础工具库**（只依赖标准库，可选 Boost.Variant），供 base/csalt/插件等所有上层链接。源码分四个功能子目录（`UTIL_DIRS` 第 24~30 行）：`include`、`util`、`util/datawriter`、`util/interpolator`、`util/matrixoperations`。

**include/**

- `utildefs.hpp` 是全库的“类型宪法”。第 102~105 行定义基础标量：

```cpp
typedef double          Real;              // 8 byte float
typedef int             Integer;           // 4 byte signed integer
typedef unsigned char   Byte;              // 1 byte
typedef unsigned int    UnsignedInt;       // 4 byte unsigned integer
```

第 107~111 行定义 `RealArray/IntegerArray/UnsignedIntArray/StringArray/BooleanArray` 等容器别名；第 136~137 行用 `std::variant`（或 Boost.Variant，由 `GMAT_USE_BOOST_VARIANT` 切换，第 47~57 行）定义 `Generic` 泛型值。`Gmat::ParameterType` 枚举（第 149~177 行）枚举 GMAT 全部参数类型（`REAL_TYPE/RVECTOR_TYPE/TIME_TYPE/OBJECT_TYPE/...`），注释要求与 `GmatBase::PARAM_TYPE_STRING` 同步。`Gmat::SolverStatus`（第 202~216 行）给出求解器状态码（CONVERGED/IN_TOLERANCE/EXCEEDED_ITERATIONS=-1/...）。
- `DoxygenApiIntro.hpp` 是面向 API 文档的 Doxygen 说明页头（`\ingroup API` 分组入口）。

**util/ 根目录（线性代数 + 时间系统 + 文件 + 消息）**

- 线性代数：`Rvector/Rvector3/Rvector6`（向量及其定长特化）、`Rmatrix/Rmatrix33/Rmatrix66`（矩阵及其定长特化）、`ArrayTemplate<T>`（定长数组模板基类，Rvector/Rmatrix 的公共父）、`TableTemplate<T>`（二维表模板，Rmatrix 的父）、`Linear`（线性代数辅助）、`RealUtilities`（实数比较/容差）、`RgbColor/ColorTypes/ColorDatabase`（颜色）。
- 时间系统：`Date`（抽象日期基类）→ `A1Date`（A1 原子时历法）与 `GregorianDate`/`UtcDate`；`A1Mjd`（修正儒略日纪元，`typedef Real GmatEpoch` 的实际载体）；`ElapsedTime`（秒/日换算）；`GmatTime`（高精度时间，纳秒级整数+小数）；`OrbitDesignerTime`（OrbitDesigner 兼容时间）；`TimeTypes`（时间枚举）；`TimeSystemConverter`（`TimeSystemConverter.hpp` 第 84 行，单例 `Instance()` 第 88 行，TAI/TT/UTC/TDB 等系统互转，依赖 `EopFile` 与 `LeapSecsFileReader`）；`DateUtil`（日期工具）；`TimeTypes`。
- 星历文件：`CCSDSEphemerisFile`（CCSDS 星历抽象）、`CCSDSOEMReader/Writer`（OEM 轨道星历）、`CCSDSAEMReader`（AEM 姿态星历，派生自 `CCSDSEMReader`）、`CCSDSEMReader/Writer`（星历元数据读/写）、`CCSDSAEMSegment/CCSDSAEMEulerAngleSegment/CCSDSAEMQuaternionSegment`（姿态分段：欧拉角/四元数）、`CCSDSEMSegment/CCSDSOEMSegment`（分段基类与轨道分段）；`Code500EphemerisFile`（Code-500 二进制星历）、`STKEphemerisFile`（STK 星历）、`SPADFileReader`（SPAD）、`Ephemeris`（星历辅助）、`NPlateHistoryFileReader`（NPlate 历史）。
- 文件与系统：`FileManager`（全局单例，管理 GMAT 各目录路径与 `GmatFunctionPath`，见第 224~229 行）、`FileUtil`（路径/文件工具）、`FileTypes`（文件类型枚举）、`IFileUpdater`（文件更新接口）、`EopFile`（地球定向参数文件）、`LeapSecsFileReader`（闰秒表）、`GravityFileUtil`（重力场文件工具）、`GmatGlobal`（全局运行标志单例）。
- 消息与内存：`MessageInterface`（`MessageInterface.hpp` 消息输出，`ShowMessage` 族）、`MessageReceiver`（接收器接口，ConsoleMessageReceiver 在其上）、`MemoryTracker`（调试内存跟踪）、`BaseException`（异常基类，全库异常根）、`UtilityException.hpp`（工具异常）。
- 姿态/状态转换：`AttitudeConversionUtility`（姿态四元数/欧拉角/DCM 互转）、`AttitudeUtil`、`BodyFixedStateConverter`（地固↔惯性状态转换，`BodyFixedStateConvert`）。
- 数值：`NumericJacobian`（数值雅可比/有限差分）、`CalculationUtilities`、`AngleUtil`（角度换算）、`CubicSpline`（三次样条）、`StateConversionUtil`（轨道状态表示互转：笛卡尔/开普勒/春分点等）、`RepeatGroundTrack`/`RepeatSunSync`/`SunSync`（回归轨道/太阳同步轨道设计）、`RandomNumber`（随机数）、`StringTokenizer`/`StringUtil`/`TextParser`（字符串/文本解析）、`Frozen`（冻结轨道参数）。

**util/interpolator/（插值框架）**

`Interpolator`（`Interpolator.hpp` 第 43 行）是抽象基类：`AddPoint(ind, data)` 喂点、纯虚 `Interpolate(ind, results)`（第 83 行）与 `Clone()`（第 85 行），采用环形缓冲 `bufferSize/latestPoint`（第 104~108 行）。派生：`LinearInterpolator`（线性）、`LagrangeInterpolator`（拉格朗日）、`CubicSplineInterpolator`（三次样条）、`HermiteInterpolator`（埃尔米特）、`NotAKnotInterpolator`（非节点三次样条）；`BrentDekkerZero`（Brent-Dekker 求根）；`InterpolatorException`（插值异常）。

**util/matrixoperations/（矩阵分解）**

`MatrixFactorization`（抽象基类）派生 `LUFactorization`、`QRFactorization`、`CholeskyFactorization`、`SchurFactorization`——供解算器（DifferentialCorrector/Target 等）使用。

**util/datawriter/（数据写出）**

`DataWriter`（写文件主类）、`DataWriterInterface`（抽象接口）、`DataWriterMaker`（工厂，按类型创建写出器）、`WriterData`（写出数据单元）、`DataBucket`（数据桶）。这是 GMAT 报表/星历写出后端的可插拔框架。

### 2.4 TestDrivers / UnitTests：传统测试体系

GMAT 的测试**不是 CppUnit**，而是两套自研、基于 makefile/IDE 工程的独立测试程序，用 `Common/TestOutput.hpp` 的自研 `Validate` 断言：

- `src/TestDrivers/`（21 文件）：针对**单个算法**的小驱动。`matrixinvert/`（矩阵求逆，含 `TestDriver_BigMatrix.cpp` 大矩阵测试，有 `CMakeLists.txt`）、`pathconcatenator/`（路径拼接，含 `CMakeLists.txt`）、`LUFactorization/`（LU 分解，含 VS `.sln/.vcxproj`，`LUTestDriver.cpp` 为驱动）、`build/`（`GmatUnitTests.sln` 与 `TestMatrixInversion.vcxproj` 等构建产物）。
- `src/UnitTests/`（143 文件）：面向 gmatutil/base 的**批量**单元测试，每个功能一个 `TestXxx/` 目录。`README.txt` 说明 Windows GCC 用法：拷贝 `build/windows/BuildEnv.mk` 到测试目录并改 `GMAT_BASE` 路径；`BuildEnv.mk` 第 7~9 行给出 `GMAT_BASE = c:/Projects/GmatDevelopment/src/base` 等硬编码路径。各目录用 `Makefile.win/.gcc/.mac/.eclipse` 组织编译。

**测试框架剖析**：`Common/TestOutput.hpp` 第 41 行 `class TestOutput`，构造传入输出文件名，`Put/PutLine` 写日志，`Validate(actual, expect, tol=TEST_TOL, validate)`（第 105~114 行）做浮点容差断言并输出 PASS/FAIL。它是“无注册、无 runner”的朴素风格：每个测试 `.cpp` 自带 `main()`，顺序执行断言并把结果写 `.txt`。

**代表性测试深读**：

1. `TestRmatrix/TestRmatrix.cpp`：Rmatrix 线性代数测试，`OutputRmatrix`（第 51 行）打印矩阵，`Validate` 逐项比对矩阵运算（转置/求逆/乘法）结果。
2. `TestTime/TestTime.cpp`：时间系统与 TimeSystemConverter 的换算测试（配合 `Makefile.win`）。
3. `TestCoordSystem/`（13 个 .cpp + 12 个 Makefile）：坐标系/轴系/历元（TOD/MOD/TOE/Ec/Eq/ITRF）转换测试，`TestTODEq.cpp`/`TestTOEEq.cpp`/`TestItrf.cpp` 等逐一验证轴系转换；对应 `MakeGS.mac/MakeTODEq.mac` 等按 mac 环境分构建。
4. `TestParam/`（7 个 .cpp）：参数系统测试——`TestParam.cpp`、`TestParamDatabase.cpp`、`TestExpParser.cpp`（表达式解析）、`TestBplaneParam.cpp`/`TestBurnParam.cpp`、自定义参数 `MyEtParam.hpp/cpp`。
5. `TestInterpolator/driver.cpp`：插值框架驱动的入口，验证各 Interpolator 子类插值精度。

其余目录覆盖力模型（`TestForceModel/TestForces.cpp`）、太阳系/质心（`TestSolarSystem/TestBary.cpp`）、推进与机动（`TestBurn/TestImpulsiveBurn.cpp`、`TestManeuvers/TestManeuvers.cpp`）、星历文件（`TestEphemerisFile/TestEphemerisFile.cpp`、`TestCode500EphemFile/`、`TestGravityFile/`、`TestSPK/TestSpiceKernelWriter.cpp`）、脚本（`TestScriptInterpreter/`、`TestScriptReadWriter/`）、函数（`TestFunction/`、`TestGmatFunctionParsing/`）、SPICE/Matlab 接口（`TestMatlabInterface/`）等，见附录表。

### 2.5 api-interop：对外 API 互操作层

`api-interop/README-APIInteroperability.txt`（第 1~11 行）说明：自 R2020a 起 GMAT 提供原生 Python/MATLAB API，本目录给出**连接 GMAT 与其他系统（重点是 JPL Monte）的文档与样例**；`gmat-monte/` 全部为 Python，需在 Monte 的 `mpython` 环境运行，测试于 Monte 140.1 + Python 3。

真实 C/C++ API 层不在本目录，而在 `src/base/api/`：`APIFunctions.hpp`（`GMAT_API` 导出的 `Setup/LoadScript/RunScript/Execute/Construct/Copy/GetObject/UseLogFile/...`，如 `swig/gmat.swg` 第 792 行 `%include "APIFunctions.hpp"`）、`APIException.hpp`（`BaseException` 的 API 异常子类）。`swig/GmatAPI.hpp` 把这层与 gmatutil/base 所有头一次性聚合，是 SWIG 的输入。

api-interop 各子目录：

- `doc/GmatMonte/`：Sphinx 文档（`conf.py`、`index.rst`、`introduction.rst`、`ephemerissharing.rst`、`maneuverplansharing.rst`）与 `ExampleCode/*.mpy/*.py/*.script`（月地转移示例）及 `images/*.png` 插图。
- `doc/ModelShare/`：模型共享规划材料（`DynamicsSharing.pdf/.odp`、PPTX 计划、xlsx 预算）；`doc/Requirements/ManeuverSharingReqs.xlsx` 需求；`doc/NotesEphemSharing.txt` 笔记。
- `gmat-monte/datasharing/CovarianceShare/`：协方差互操作——`MonteToGMATCovariance.mpy` + `inputs/`（`.boa` 二进制轨道、`.gmd` 测量、`.csv` 协方差、`.script` 暖启动脚本）。
- `gmat-monte/datasharing/DynamicsSharing/`：动力学共享——`SimpleExternalForceModel.py`（Monte 侧外部力模型）、`getExternalMonteForces.py`、`BasicStart.mpy`、`SimpleGmatScript.script`。
- `gmat-monte/datasharing/ephemshare/`：星历共享——`ReadWriteBasics/readSPK.script`（GMAT 用 SPK 传播器读 `traj.bsp`，`OrbitSpiceKernelName = {'traj.bsp'}` 见第 12 行）与 `writeSPK.py`（Monte 用 `DivaPropagator` 传播后 `cristo.convert(boa, "traj.bsp")` 写 SPK，第 57/68 行），`LunarTransferExample/`。
- `gmat-monte/datasharing/mnvrshare/`：机动规划共享——`hohmann/`（`ManeuverPlanSharing_ImpulsiveBurns.py`、`GmatFunctions.py`、`GmatMonte.py` 等）、`lunartransfer/`、`raiseApogee/`。
- `gmat-monte/jupyter/`：三个 notebook（`EphemerisSharing.ipynb`、`GMAT_HohmannTransfer.ipynb`、`ImpulsiveBurn.ipynb`）。

### 2.6 swig：SWIG 接口定义

`swig/`（11 文件）用 SWIG 从 C++ 头生成 **Python / Java（供 MATLAB）** 两套绑定，并提供 MATLAB 静态封装。

生成流程（`swig/CMakeLists.txt`）：若 `_GMATAPI_GENERATE_PYTHON`，则 `_SETUPSWIG("gmat","Python","gmat_py.i","GmatUtil;GmatBase")`（第 46 行）生成 Python 模块并安装 `gmatpy/__init__.py`；若 `_GMATAPI_GENERATE_JAVA`，则 `_SETUPSWIG("gmat","Java","gmat.i","GmatUtil;GmatBase")`（第 67 行），并把 `gmat_matlab_loadlibrary.java` 作为额外 Java 文件；`INSTALL(FILES GMATAPI.m DESTINATION bin)`（第 71 行）安装 MATLAB 封装。`_SETUPSWIG` 定义于 `build/cmake_modules/GmatSwigConfig.cmake`。

- `gmat.i`（`%module gmat`，第 1 行）：Java/MATLAB 主接口。手工处理 `ArrayTemplate<Real>::GetDataVector`/`TableTemplate<Real>::GetDataVector` 的 out typemap（第 9~35 行），把 `double*` 转为 Java 数组；`%typemap(javacode) SWIGTYPE` 注入 `setSwigOwnership/getSwigOwnership`（第 39~47 行）；`%rename` 把 `ToString`→`toString`、运算符→`add/sub/mul/getitem` 等（第 50~74 行）；`BaseException`→`java.lang.Exception`（第 76~77 行）；最后 `%include "gmat.swg"`。
- `gmat_py.i`（`%module gmat_py`，第 1 行）：Python 主接口。同款 `GetDataVector` out typemap（第 9~33 行）；`Moderator::GetInternalObject` 按类型名动态 downcast（第 38~42 行）；`%rename(__str__)`→`ToString`、`__getitem__`→`operator()/[]`（第 45~48 行）；`%feature("shadow")` 为 `ArrayTemplate<Real>`/`TableTemplate<Real>` 的 `__getitem__/__setitem__` 加 slice/负索引/tuple 索引（第 51~178 行）；`%pythonappend` 让 `Construct/Copy/GetObject` 返回后自动 `SetClass` 下转型（第 220~260 行）；最后 `%include "gmat.swg"`（第 265 行）+ 一段 `%pythoncode` 提供 `Help/GetRunSummary/ShowObjects/ShowClasses` 顶层函数。
- `gmat.swg`（第 1 行起）：**公共主文件**。第 79 行 `#include "GmatAPI.hpp"` 聚合全部头；第 42 行 `EXCEPTION()` 启用 C++→目标语言异常映射；第 45~76 行 `%ignore` 各嵌套异常类；第 78 行 `%ignore *::operator=`；第 83~115 行 `VECTORCONVERT` 把 `RealArray/ObjectArray/...` 等 `std::vector` 实例化并加 `ToArray()`；第 119 行起 `// GmatUtil` 段 include gmatutil 全类；第 254 行起 `// GmatBase` 段按 `DOWNCAST(Derived, Base)`（生成 `SetClass` 动态转换）逐类 include base 对象体系（坐标系/力模型/命令/硬件/求解器/传播器等）；第 792 行 `%include "APIFunctions.hpp"` 与 `APIException.hpp`/`HelpSystem.hpp`/`Moderator.hpp` 导出 API 函数。
- `JavaSwigUtil.swg`：Java 专用宏。`DOWNCAST`（第 35~50 行）用 `dynamic_cast` 做安全下转型，失败抛 `ClassCastException`；`EXCEPTION`（第 54~64 行）把 `BaseException` 转成 `gmat/APIException` Java 异常；`ARRAYRETURN/ARRAYRETURNSIZE`（第 68~101 行）把 `double*/int*` 转 Java 数组；`VECTORCONVERT`（第 105~127 行）加 `ToArray()`。
- `PythonSwigUtil.swg`：Python 专用宏，功能镜像：`DOWNCAST`（第 41~54 行，失败 `PyExc_RuntimeError`）、`EXCEPTION`（第 58~68 行，`GMAT_PyException` 抛 `APIException`）、`ARRAYRETURN/ARRAYRETURNSIZE`（第 72~104 行，`SWIG_PyArrayOut*`）、`VECTORCONVERT`（第 108~125 行）。运行时辅助 `GMAT_PyException`（第 25~35 行）从 `gmatpy._py...` 模块取 `APIException` 类实例化。
- `arrays_python.i`：Python 数组 typemap 实现，`SWIG_PyArrayIn/Out/Argout` 在 `int[]/double[]` 与 PyList 间转换（第 54~82 行），`%typecheck` 校验输入为同类型列表（第 86~105 行）。
- `gmatutil_py.i`（`%module gmat_py`，第 1 行）：**仅 gmatutil 子集**的轻量 Python 绑定（用于无需整个 base 的场景），`%ignore` 掉 Windows 不链接的 `GmatRealUtil::ToString/Rmatrix::ToString` 等（第 33~34 行）与友元函数 `SkewSymmetric*/TransposeTimes*`（第 78~101 行）。
- `GmatAPI.hpp`：纯 `#include` 聚合头（gmatutil 第 24~87 行 → base 第 91 行起），供 `gmat.swg` 第 79 行引用，确保 SWIG 看到完整声明。
- `GMATAPI.m`：MATLAB 静态类 `classdef GMATAPI (methods(Static))`，逐一把 `gmat.gmat.*` 转发为 MATLAB 函数，并在 `Construct/Command/Copy/GetObject/GetRuntimeObject` 后调 `GMATAPI.SetClass(val)`（第 88~126 行）做动态下转型（ForceModel→ODEModel 特判第 116~118 行）。
- `gmat_matlab_loadlibrary.java`：MATLAB 经 Java 加载 GMAT 的引导类。`loadGMAT(debug, pluginDir)`（第 108~112 行）按顺序 `loadLibrary({"gmat","station","navigation"})`，Windows 下先 `System.load` 依赖 DLL（`libGmatUtil(d).dll/libGmatBase(d).dll` 等，第 42~68 行），再 `setGMATPath()` 用 `FileManager.Instance().SetBinDirectory` 设路径（第 85~98 行）。

## 三、关键设计模式与数据流

### 3.1 继承体系

```
csalt:
  UserFunction ─┬─ UserPathFunction ─── OrbitPathFunction
                └─ UserPointFunction ── OrbitPointFunction
  DecisionVector ── DecVecTypeBetts
  ImplicitRungeKutta ── LobattoIIIA_2Order / _4HSOrder / _4Order / _6Order / _8Order / Separated
  NLPFuncUtil ── NLPFuncUtil_Coll ── NLPFuncUtilRadau / NLPFuncUtil_ImplicitRK
  Phase ── RadauPhase ── OrbitPhase
         └─ ImplicitRKPhase
  Trajectory ── OrbitTrajectory
  ExecutionInterface (抽象, Publish 纯虚)
  OptimizerBase (抽象)  ← 但 SnoptOptimizer/IpoptOptimizer 实际未继承(演进遗留)
  IPOPTWrapper : Ipopt::TNLP

gmatutil:
  Date ── A1Date / GregorianDate / UtcDate
  Interpolator ── Linear / Lagrange / CubicSpline / Hermite / NotAKnot
  MatrixFactorization ── LU / QR / Cholesky / Schur
  ArrayTemplate<Real> ── Rvector / Rvector3 / Rvector6
  TableTemplate<Real> ── Rmatrix / Rmatrix33 / Rmatrix66
  BaseException ── 各工具异常(InterpolatorException/TimeFormatException/...)
```

### 3.2 工厂/单例模式

- **单例**：`TimeSystemConverter::Instance()`、`FileManager::Instance()`、`GmatGlobal::Instance()`、`MemoryTracker::Instance()`（gmatutil）；`ColorDatabase` 为静态色表。
- **工厂**：`DataWriterMaker`（gmatutil/datawriter，按类型名创建 DataWriter 子类）；CSALT 侧配点助手按 `collocationMethod` 字符串在 `ImplicitRKPhase.cpp` 第 94~106 行 `if/else` 选 `RungeKutta8/6/4/HermiteSimpson/Trapezoid` 实例化 `NLPFuncUtil_ImplicitRK`。
- **抽象工厂式装配**：`Phase` 通过纯虚 `InitializeTranscription()` 让子类决定离散化策略（Radau vs ImplicitRK），`DecisionVector` 通过纯虚下标方法让 `DecVecTypeBetts` 决定排布。

### 3.3 数据流（一次 CSALT 求解）

用户函数对象 → `UserPathFunctionManager/UserPointFunctionManager`（按 `UserFunctionProperties` 稀疏模式求函数值+雅可比）→ `Phase`（`NLPFuncUtilRadau/ImplicitRK` 装配缺陷约束、代数路径约束、积分代价）→ `Trajectory`（拼接总决策向量/总约束/总 `sparsityPattern`）→ `SnoptOptimizer::Optimize`（`SNOPTFunctionWrapper` 回调 `GetCostConstraintFunctions/GetJacobian`）→ 解写回 `Phase::SetDecisionVector` → `RefineMesh` 迭代 → `BaryLagrangeInterpolator`/`OCHTrajectoryData` 输出连续轨迹与 `.och` 文件；期间 `csaltState` 经 `ExecutionInterface::Publish` 通知 GMAT 前端。

### 3.4 调用链（SWIG → GMAT API）

Python/Java 用户脚本 → SWIG 生成绑定（`gmat_py`/`gmat` 模块）→ `Moderator`（`src/base/executive/Moderator.hpp`，脚本解释执行入口）→ `GmatBase` 对象体系（工厂 `FactoryManager::CreateEventLocator` 等）→ 底层 `GmatUtil` 工具库。`APIFunctions.hpp` 的 `GMAT_API` 自由函数（Setup/LoadScript/Execute）是绑定层与 Moderator 的边界；异常统一经 `BaseException → APIException` 映射回目标语言。

## 四、文件清单附录

> 所有路径均经 glob 验证存在。csaltTester 的 `drivers/*/pointpath/*` 采用“每个问题 = 1 Driver + 1 PathObject + 1 PointObject”的固定三重奏，表中合并列出以压缩篇幅，文件名全部真实。

### 表 4.1 CSALT（src/csalt，134 文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| CMakeLists.txt | 构建共享库 libCSALT | `TargetName CSALT`；链接 SNOPT/GmatUtil |
| src/Doxyfile | Doxygen 配置 | — |
| src/include/csalt.hpp | 库总入口头 | include 六个对外类 |
| src/include/csaltdefs.hpp | 导出宏 | `CSALT_API`/`DEPRECATED` |
| src/collutils/DecisionVector.{hpp,cpp} | 决策向量分块管理 | `Initialize/SetDecisionVector/GetStateAtMeshPoint`，抽象下标方法 |
| src/collutils/DecVecTypeBetts.{hpp,cpp} | Betts 排布决策向量 | `GetInitialStateIdxs/GetFinalTimeIdx` 等实现 |
| src/collutils/ImplicitRungeKutta.{hpp,cpp} | 隐式 RK Butcher 表基类 | `LoadButcherTable/GetDependencyChunk/Clone` |
| src/collutils/LobattoIIIA_2Order.{hpp,cpp} | 2 阶 Lobatto IIIA | `InitializeData/LoadButcherTable` |
| src/collutils/LobattoIIIA_4Order.{hpp,cpp} | 4 阶 Lobatto IIIA | 同上 |
| src/collutils/LobattoIIIA_4HSOrder.{hpp,cpp} | 4 阶 Hermite-Simpson | 同上 |
| src/collutils/LobattoIIIA_6Order.{hpp,cpp} | 6 阶 Lobatto IIIA | 同上 |
| src/collutils/LobattoIIIA_8Order.{hpp,cpp} | 8 阶 Lobatto IIIA | 同上 |
| src/collutils/LobattoIIIASeparated.{hpp,cpp} | 分离形式 Lobatto IIIA | 同上 |
| src/collutils/NLPFuncUtil.{hpp,cpp} | NLP 函数工具基类 | 缺陷/代数/积分函数求值框架 |
| src/collutils/NLPFuncUtilRadau.{hpp,cpp} | Radau 配点 NLP 助手 | `InitializeTranscription/ComputeDefectConstraints` |
| src/collutils/NLPFuncUtil_Coll.{hpp,cpp} | 配点 NLP 助手基类 | 微分矩阵/求积装配 |
| src/collutils/NLPFuncUtil_AlgPath.{hpp,cpp} | 代数路径约束助手 | `ComputeAlgPathFunctions` |
| src/collutils/NLPFuncUtil_Path.{hpp,cpp} | 路径函数助手 | 路径函数/雅可比 |
| src/collutils/NLPFuncUtil_ImplicitRK.{hpp,cpp} | 隐式 RK NLP 助手 | `SetButcherTable(collocationMethod)` |
| src/collutils/NLPFuncUtil_MultiPoint.{hpp,cpp} | 多点函数助手 | 多点依赖装配 |
| src/collutils/NLPFunctionData.{hpp,cpp} | NLP 求值数据封装 | 函数值/雅可比容器 |
| src/collutils/ProblemCharacteristics.{hpp,cpp} | 问题特性纯数据 | 维度/网格/界与 `Validate*` |
| src/executive/ExecutionInterface.{hpp,cpp} | 求解状态发布接口 | `Publish/GetStateArray` |
| src/executive/ImplicitRKPhase.{hpp,cpp} | 隐式 RK 相位 | `SetTranscription/InitializeTranscription` |
| src/executive/RadauPhase.{hpp,cpp} | Radau 配点相位 | `InitializeTranscription` |
| src/executive/OrbitPhase.{hpp,cpp} | GMAT 轨道相位 | `SetThrustMode/SetStateRep/SetIsp` |
| src/executive/Phase.{hpp,cpp} | 相位抽象基类 | 全量 Set/Get + 纯虚 `InitializeTranscription` |
| src/executive/Trajectory.{hpp,cpp} | 轨迹执行者 | `Optimize/PrepareMeshGuess/SetDecisionVector` |
| src/executive/OrbitTrajectory.{hpp,cpp} | 轨道轨迹 | `Initialize` 收集各相位推力/表示 |
| src/executive/OptimizerBase.{hpp,cpp} | 优化器抽象基类 | 纯虚 `Optimize` |
| src/executive/SnoptOptimizer.{hpp,cpp} | SNOPT 封装 | `snoptProblemA Problem`、`Optimize` |
| src/executive/IpoptOptimizer.{hpp,cpp} | 命名遗留的 SNOPT 封装 | 同 SnoptOptimizer（未入 CSALT_SRCS） |
| src/executive/OptimizerConfig.hpp.in | 优化器配置模板 | 构建期替换宏 |
| src/userfunutils/BoundData.{hpp,cpp} | 上下界数据 | 函数界载体 |
| src/userfunutils/FunctionContainer.{hpp,cpp} | 函数容器基类 | 函数值/名称容器 |
| src/userfunutils/FunctionInputData.{hpp,cpp} | 求值输入快照 | 状态/控制/时间/静态 |
| src/userfunutils/FunctionOutputData.{hpp,cpp} | 求值输出 | 函数值+雅可比 |
| src/userfunutils/JacobianData.{hpp,cpp} | 雅可比元素 | 状态/控制/时间雅可比块 |
| src/userfunutils/OptimalControlFunction.{hpp,cpp} | 单最优控制函数抽象 | 依赖映射 + `EvaluateFunctions/EvaluateJacobian` |
| src/userfunutils/OrbitPathFunction.{hpp,cpp} | 轨道内建路径函数 | `SetDynamics/ComputeThrust` |
| src/userfunutils/OrbitPointFunction.{hpp,cpp} | 轨道内建点函数 | 相位推力/表示配置 |
| src/userfunutils/PathFuncProperties.{hpp,cpp} | 路径函数属性 | 函数个数/类型 |
| src/userfunutils/PathFunctionContainer.{hpp,cpp} | 路径函数容器 | 动力学/代数/代价值+雅可比 |
| src/userfunutils/PointFunctionContainer.{hpp,cpp} | 点函数容器 | 代价/代数点函数 |
| src/userfunutils/UserFunction.{hpp,cpp} | 用户函数基类 | 枚举 FunctionType/JacobianType |
| src/userfunutils/UserFunctionManager.{hpp,cpp} | 用户函数管理器基类 | 稀疏模式驱动求值 |
| src/userfunutils/UserFunctionProperties.{hpp,cpp} | 函数依赖/稀疏属性 | 依赖映射 |
| src/userfunutils/UserPathFunction.{hpp,cpp} | 路径函数抽象 | `EvaluateUserFunction/Jacobian` |
| src/userfunutils/UserPathFunctionManager.{hpp,cpp} | 路径函数管理器 | 驱动 PathFunctionContainer |
| src/userfunutils/UserPointFunction.{hpp,cpp} | 点函数抽象 | `Initialize/AddFunctions/Evaluate` |
| src/userfunutils/UserPointFunctionManager.{hpp,cpp} | 点函数管理器 | 驱动 PointFunctionContainer |
| src/util/ArrayTrajectoryData.{hpp,cpp} | 数组式轨迹数据 | 状态/控制/时间数组 |
| src/util/BaryLagrangeInterpolator.{hpp,cpp} | 重心拉格朗日插值 | `Interpolate/CalBarycentricMatrix` |
| src/util/DummyPathFunction.{hpp,cpp} | 测试占位路径函数 | 空实现 |
| src/util/DummyPathFunction2.{hpp,cpp} | 测试占位路径函数 2 | 空实现 |
| src/util/GuessGenerator.{hpp,cpp} | 初始猜测生成 | LinearNoControl/File 等模式 |
| src/util/IPOPTWrapper.{hpp,cpp} | Ipopt::TNLP 实现 | `eval_f/eval_g/eval_jac_g/eval_h`（未入构建） |
| src/util/LobattoIIIaMathUtil.{hpp,cpp} | Lobatto IIIA 数学 | 配点权重/微分矩阵 |
| src/util/LowThrustException.{hpp,cpp} | CSALT 异常 | `: public BaseException` |
| src/util/ModEqDynamics.{hpp,cpp} | 修正春分点动力学 | 状态导数 |
| src/util/OCHTrajectoryData.{hpp,cpp} | OCH 轨迹数据(.och) | `WriteToFile` |
| src/util/OCHTrajectorySegment.{hpp,cpp} | OCH 分段 | 分段读/写 |
| src/util/RadauMathUtil.{hpp,cpp} | Radau 配点数学 | LGR 点/权重 |
| src/util/ScaleUtility.{hpp,cpp} | 量纲/无量纲化 | 代价/约束权重 |
| src/util/ScalingUtility.{hpp,cpp} | 单位换算 | 状态/控制单位换算 |
| src/util/SNOPTFunctionWrapper.{hpp,cpp} | SNOPT 回调 | `SNOPTFunctionWrapper/StopOptimizer` |
| src/util/SparseMatrixLibraryHeader.hpp | 稀疏头聚合 | include ublas 头 |
| src/util/SparseMatrixUtil.{hpp,cpp} | 稀疏矩阵静态工具 | `typedef ... RSMatrix`、`SetSparsityPattern` |
| src/util/TrajectoryData.{hpp,cpp} | 轨迹数据抽象基类 | 状态/控制访问 |
| src/util/TrajectorySegment.{hpp,cpp} | 轨迹分段 | 分段数据 |

### 表 4.2 csaltTester（src/csaltTester，281 文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| CMakeLists.txt | 构建可执行 CSALTTester | `ADD_EXECUTABLE CSALTTester` |
| src/.gitignore | 忽略规则 | — |
| src/HelperClasses/BrachistichronePathObject.{hpp,cpp} | 最速降线路径函数 | `: public UserPathFunction` |
| src/HelperClasses/BrachistichronePointObject.{hpp,cpp} | 最速降线点函数 | `: public UserPointFunction` |
| src/HelperClasses/BreakwellPathObject.{hpp,cpp} | Breakwell 路径函数 | `: public UserPathFunction` |
| src/HelperClasses/BreakwellPointObject.{hpp,cpp} | Breakwell 点函数 | `: public UserPointFunction` |
| src/TestAlgNLPUtil/TestAlgNLPUtil.hpp | 代数路径约束测试头 | — |
| src/TestBarycentricLagrangeInterpolator/TestBarycentricLagrangeInterpolator.hpp | 重心插值测试 | — |
| src/TestBrachistichrone/{Makefile,MakefileLinux,TestBrachistichrone.cpp} | 最速降线独立测试 | main |
| src/TestDecisionVector/{Makefile,TestDecisionVector.cpp} | 决策向量独立测试 | main |
| src/TestGuess/{ExampleUserGuessClass.hpp,Makefile,SchwartzInitialGuess.och,SchwartzPathObject.{hpp,cpp},SchwartzPointObject.{hpp,cpp},TestGuess.cpp,TestGuessDriver.{hpp,cpp}} | 初始猜测测试 | TestGuessDriver |
| src/TestHyperSensitive/{Makefile,TestHyperSensitive.cpp} | 超敏感独立测试 | main |
| src/TestInterpolation/{.gitignore,Makefile,TestInterpMain.{hpp,cpp},TestInterpolator} | 插值独立测试 | TestInterpMain |
| src/TestIpoptInterface/TestIpoptOptimizer.cpp | IPOPT 接口测试 | main |
| src/TestLobattoIIIaMathUtil/TestLobattoIIIaMathUtil.cpp | Lobatto IIIA 数学测试 | main |
| src/TestNLPFuncUtil/TestNLPFuncUtil.hpp | NLP 函数工具测试头 | — |
| src/TestNLPFuncUtilRadau/TestNLPFuncUtilRadau.hpp | Radau NLP 测试头 | BrysonMaxPathObject/HypSenPathObject |
| src/TestNLPFunctionData/TestNLPFunctionData.{hpp,cpp} | NLP 数据测试 | main |
| src/TestOptCtrl/Comparison.txt | 比对说明 | — |
| src/TestOptCtrl/DataFileReader.py | 数据文件读取器 | — |
| src/TestOptCtrl/Debug/** (7) | Eclipse 调试构建产物 | makefile/objects.mk/sources.mk/.d |
| src/TestOptCtrl/Hypersensitive_Radau.och, Hypersensitive_Radau_2.och | 超敏感输出样本 | .och 轨迹 |
| src/TestOptCtrl/Makefile | 主测试 Makefile | — |
| src/TestOptCtrl/src/ConsoleMessageReceiver.{hpp,cpp} | 控制台消息接收 | `: public MessageReceiver` |
| src/TestOptCtrl/src/ConwaySpiralDriver.{hpp,cpp} | Conway 螺旋用例驱动 | `: public CsaltTestDriver` |
| src/TestOptCtrl/src/DecisionVectorDriver.{hpp,cpp} | 决策向量用例驱动 | — |
| src/TestOptCtrl/src/PhaseDriver.{hpp,cpp} | 相位用例驱动 | — |
| src/TestOptCtrl/src/TrajectoryDriver.{hpp,cpp} | 轨迹用例驱动 | — |
| src/TestOptCtrl/src/TestOptCtrl.{hpp,cpp} | 测试壳 main | 菜单 + `-run` 参数分发 |
| src/TestOptCtrl/src/testcases.hpp | 用例注册头 | include 全部 driver |
| src/TestOptCtrl/src/Shell/ShellDriver.{hpp,cpp} | 新增用例模板驱动 | — |
| src/TestOptCtrl/src/Shell/ShellPathObject.{hpp,cpp} | 模板路径函数 | `: public UserPathFunction` |
| src/TestOptCtrl/src/Shell/ShellPointObject.{hpp,cpp} | 模板点函数 | `: public UserPointFunction` |
| src/TestOptCtrl/src/drivers/CsaltTestDriver.{hpp,cpp} | 驱动基类 | `SetPointPathAndProperties/SetupPhases/Run` |
| src/TestOptCtrl/src/drivers/{BangBang,Brachistochrone,BrysonDenham,BrysonMaxRange,CatalyticGasOilCracker,ConwayOrbitExample,ConwayOrbitExampleRK,GoddardRocket,GoddardRocketThreePhase,HohmannTransfer,Hull95,HyperSensitive,InteriorPoint,LinearTangentSteering,LinearTangentSteeringStaticVar,MoonLander,ObstacleAvoidance,RauAutomatica,Rayleigh,RayleighControlStateConstraint,Schwartz,Tutorial}Driver.{hpp,cpp} (22×2) | 22 个基准问题驱动 | 各 `: public CsaltTestDriver` |
| src/TestOptCtrl/src/pointpath/*.{hpp,cpp} (约 30 对 Path/Point) | 各问题的路径/点函数对象 | 各 `: public UserPathFunction/UserPointFunction`（BangBang、Brachistichrone、BrysonDenham、BrysonMaxRange、CatalyticGasOilCracker、ConwayOrbitExample、ConwaySpiral、GoddardRocket、GoddardRocketThreePhase、HohmannTransfer、Hull95、HyperSensitive、InteriorPoint、LinearTangentSteering(StaticVar)、MoonLander、ObstacleAvoidance、OrbitRaising(MultiPhase)、RauAutomatica、Rayleigh(ControlStateConstraint)、Schwartz、Tutorial） |
| src/TestOptimizer/{Makefile,TestOptimizer.cpp} | 优化器独立测试 | main |
| src/TestOrbitRaisingMultiPhase/{Makefile,TestOrbitRaisingMultiPhase.cpp,TestOrbitRaisingMultiPhase_2.cpp} | 多相位升轨测试 | main |
| src/TestPhase/{Makefile,MakefileLinux,TestPhase.cpp} | 相位独立测试 | main |
| src/TestProblemCharacteristics/TestProblemCharacteristics.hpp | 问题特性测试头 | — |
| src/TestRadauMathUtil/TestRadauMathUtil.hpp | Radau 数学测试头 | — |
| src/TestRauAutomatica/TestRauAutomatica.cpp | RauAutomatica 测试 | main |
| src/TestRayleigh/TestRayleigh.cpp | Rayleigh 测试 | main |
| src/TestSparseMatrixUtil/TestSparseMatrixUtil.hpp | 稀疏矩阵工具测试头 | — |
| src/TestTrajectoryData/{Makefile,OCHistoryFileExample.och,TestTrajectoryData.cpp} | 轨迹数据(.och)测试 | main |
| src/TestUserPathFunction/{Makefile,Makefile_Point,TestUserPathFunction.cpp,old_TestUserFunctionData.cpp,TestUserPointFunction.cpp,old_TestUserFunctionData.mac} | 用户路径/点函数测试 | main |
| src/bin/DataFileReader.py | 数据文件读取器 | — |
| src/python/.gitignore | 忽略规则 | — |
| src/python/{Comparison.txt,DataFileReader.py,LagrangeInterpolator.py,OCHComparator.py,SetupCompare.py,SetupTruth.py,SNOPTComparator.py,StringUtil.py,TestCSALT.py,TestInterpolator.py} (10) | 真值比对测试框架 | 生成/比对 .truth/.snopt |
| src/python/truth/*.{truth,snopt} (23) | 21 组基准真值 + 2 组数据 | BangBang/Brachistochrone/BrysonDenham/BrysonMaxRange/ConwayOrbitExample(RK)/GoddardRocket(ThreePhase)/Hull95/HyperSensitive/InteriorPoint/LinearTangentSteering/MoonLander/ObstacleAvoidance/RauAutomatica/Rayleigh(RCS)/Schwartz |

### 表 4.3 gmatutil（src/gmatutil，176 文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| CMakeLists.txt | 构建共享库 libGmatUtil | `TargetName GmatUtil` |
| include/utildefs.hpp | 类型宪法 | `Real/Integer`、`Gmat::ParameterType` |
| include/DoxygenApiIntro.hpp | API 文档分组页 | `\ingroup API` |
| util/A1Date.{hpp,cpp} | A1 日期 | `: public Date` |
| util/A1Mjd.{hpp,cpp} | A1 修正儒略日 | 纪元表示 |
| util/AngleUtil.{hpp,cpp} | 角度换算 | 度/弧度 |
| util/ArrayTemplate.{hpp,cpp} | 定长数组模板 | Rvector 基类 |
| util/AttitudeConversionUtility.{hpp,cpp} | 姿态换算 | 四元数/欧拉角/DCM |
| util/AttitudeUtil.{hpp,cpp} | 姿态工具 | — |
| util/BaseException.{hpp,cpp} | 异常基类 | `GetFullMessage` |
| util/BodyFixedStateConverter.{hpp,cpp} | 地固↔惯性状态 | `BodyFixedStateConvert` |
| util/CalculationUtilities.{hpp,cpp} | 计算工具 | — |
| util/CCSDSAEMEulerAngleSegment.{hpp,cpp} | AEM 欧拉角分段 | `: public CCSDSAEMSegment` |
| util/CCSDSAEMQuaternionSegment.{hpp,cpp} | AEM 四元数分段 | `: public CCSDSAEMSegment` |
| util/CCSDSAEMReader.{hpp,cpp} | AEM 姿态星历读取 | `: public CCSDSEMReader` |
| util/CCSDSAEMSegment.{hpp,cpp} | AEM 分段 | `: public CCSDSEMSegment` |
| util/CCSDSEMReader.{hpp,cpp} | 星历元数据读取 | CCSDS 星历 |
| util/CCSDSEMSegment.{hpp,cpp} | 星历分段基类 | — |
| util/CCSDSEMWriter.{hpp,cpp} | 星历元数据写出 | — |
| util/CCSDSEphemerisFile.{hpp,cpp} | CCSDS 星历文件 | OEM/AEM 工厂 |
| util/CCSDSOEMReader.{hpp,cpp} | OEM 轨道星历读取 | — |
| util/CCSDSOEMSegment.{hpp,cpp} | OEM 分段 | — |
| util/CCSDSOEMWriter.{hpp,cpp} | OEM 写出 | — |
| util/Code500EphemerisFile.{hpp,cpp} | Code-500 二进制星历 | 字节序处理 |
| util/ColorDatabase.{hpp,cpp} | 颜色表 | 静态色名映射 |
| util/ColorTypes.hpp | 颜色类型 | — |
| util/CubicSpline.{hpp,cpp} | 三次样条 | — |
| util/Date.{hpp,cpp} | 日期抽象基类 | — |
| util/DateUtil.{hpp,cpp} | 日期工具 | — |
| util/ElapsedTime.{hpp,cpp} | 历元时间换算 | 秒↔日 |
| util/EopFile.{hpp,cpp} | 地球定向参数文件 | 极移/UT1 |
| util/Ephemeris.{hpp,cpp} | 星历辅助 | — |
| util/FileManager.{hpp,cpp} | 文件/目录单例 | `GetGmatFunctionPath` 等 |
| util/FileTypes.hpp | 文件类型枚举 | — |
| util/FileUtil.{hpp,cpp} | 文件工具 | `GetGmatPath/IsValidFileName` |
| util/Frozen.{hpp,cpp} | 冻结轨道 | — |
| util/GmatConstants.hpp | 物理/数学常量 | `GmatMathConstants/GmatPhysicalConstants` |
| util/GmatDefaults.hpp | 默认值 | 默认天体/参数 |
| util/GmatGlobal.{hpp,cpp} | 全局标志单例 | `Instance` |
| util/GmatTime.{hpp,cpp} | 高精度时间 | 纳秒级 |
| util/GravityFileUtil.{hpp,cpp} | 重力场文件工具 | — |
| util/GregorianDate.{hpp,cpp} | 公历日期 | `: public Date` |
| util/IFileUpdater.{hpp,cpp} | 文件更新接口 | — |
| util/LeapSecsFileReader.{hpp,cpp} | 闰秒表 | — |
| util/Linear.{hpp,cpp} | 线性代数辅助 | `Cross/SkewSymmetric` |
| util/MemoryTracker.{hpp,cpp} | 内存跟踪 | `Add/Remove` |
| util/MessageInterface.{hpp,cpp} | 消息输出 | `ShowMessage` |
| util/MessageReceiver.{hpp,cpp} | 消息接收接口 | 控制台/日志 |
| util/NPlateHistoryFileReader.{hpp,cpp} | NPlate 历史读取 | — |
| util/NumericJacobian.{hpp,cpp} | 数值雅可比 | 有限差分 |
| util/OrbitDesignerTime.{hpp,cpp} | OrbitDesigner 时间 | — |
| util/RandomNumber.{hpp,cpp} | 随机数 | — |
| util/RealUtilities.{hpp,cpp} | 实数工具 | `GmatRealUtil` 比较/取整 |
| util/RepeatGroundTrack.{hpp,cpp} | 回归轨道设计 | — |
| util/RepeatSunSync.{hpp,cpp} | 太阳同步回归轨道 | — |
| util/RgbColor.{hpp,cpp} | RGB 颜色 | — |
| util/Rmatrix.{hpp,cpp} | 稠密矩阵 | `: public TableTemplate<Real>` |
| util/Rmatrix33.{hpp,cpp} | 3×3 矩阵 | — |
| util/Rmatrix66.{hpp,cpp} | 6×6 矩阵 | — |
| util/Rvector.{hpp,cpp} | 向量 | `: public ArrayTemplate<Real>` |
| util/Rvector3.{hpp,cpp} | 3 维向量 | — |
| util/Rvector6.{hpp,cpp} | 6 维状态向量 | — |
| util/SPADFileReader.{hpp,cpp} | SPAD 文件读取 | — |
| util/STKEphemerisFile.{hpp,cpp} | STK 星历 | — |
| util/StateConversionUtil.{hpp,cpp} | 轨道状态表示互转 | 笛卡尔/开普勒/春分点 |
| util/StringTokenizer.{hpp,cpp} | 字符串分词 | — |
| util/StringUtil.{hpp,cpp} | 字符串工具 | `ToRealArray/ToString` |
| util/SunSync.{hpp,cpp} | 太阳同步轨道 | — |
| util/TableTemplate.{hpp,cpp} | 二维表模板 | Rmatrix 基类 |
| util/TextParser.{hpp,cpp} | 文本解析 | — |
| util/TimeSystemConverter.{hpp,cpp} | 时间系统互转 | 单例 `Instance` |
| util/TimeTypes.{hpp,cpp} | 时间类型 | 时间枚举 |
| util/UtcDate.{hpp,cpp} | UTC 日期 | `: public Date` |
| util/UtilityException.hpp | 工具异常 | — |
| util/datawriter/DataBucket.{hpp,cpp} | 数据桶 | — |
| util/datawriter/DataWriter.{hpp,cpp} | 数据写出主类 | — |
| util/datawriter/DataWriterInterface.{hpp,cpp} | 写出接口 | — |
| util/datawriter/DataWriterMaker.{hpp,cpp} | 写出器工厂 | `CreateDataWriter` |
| util/datawriter/WriterData.{hpp,cpp} | 写出数据单元 | — |
| util/interpolator/BrentDekkerZero.{hpp,cpp} | Brent-Dekker 求根 | — |
| util/interpolator/CubicSplineInterpolator.{hpp,cpp} | 三次样条插值 | `: public Interpolator` |
| util/interpolator/HermiteInterpolator.{hpp,cpp} | 埃尔米特插值 | `: public Interpolator` |
| util/interpolator/Interpolator.{hpp,cpp} | 插值抽象基类 | `AddPoint/Interpolate/Clone` |
| util/interpolator/InterpolatorException.{hpp,cpp} | 插值异常 | — |
| util/interpolator/LagrangeInterpolator.{hpp,cpp} | 拉格朗日插值 | `: public Interpolator` |
| util/interpolator/LinearInterpolator.{hpp,cpp} | 线性插值 | `: public Interpolator` |
| util/interpolator/NotAKnotInterpolator.{hpp,cpp} | 非节点样条插值 | `: public Interpolator` |
| util/matrixoperations/CholeskyFactorization.{hpp,cpp} | Cholesky 分解 | `: public MatrixFactorization` |
| util/matrixoperations/LUFactorization.{hpp,cpp} | LU 分解 | `: public MatrixFactorization` |
| util/matrixoperations/MatrixFactorization.{hpp,cpp} | 矩阵分解基类 | `Factor` |
| util/matrixoperations/QRFactorization.{hpp,cpp} | QR 分解 | `: public MatrixFactorization` |
| util/matrixoperations/SchurFactorization.{hpp,cpp} | Schur 分解 | `: public MatrixFactorization` |

### 表 4.4 TestDrivers（src/TestDrivers，21 文件）

| 相对路径 | 职责 |
|---|---|
| .gitignore | 忽略规则 |
| LUFactorization/LUFactorization.{opensdf,sdf,sln,v12.suo} | VS 工程文件（LU 分解） |
| LUFactorization/LUFactorization/LUFactorization.{cpp,vcxproj,vcxproj.filters} | LU 分解源码/工程 |
| LUFactorization/LUFactorization/LUTestDriver.cpp | LU 分解测试驱动 main |
| build/GmatUnitTests/{.gitignore,GmatUnitTests.sln} | 单元测试 VS 解决方案 |
| build/TestMatrixInversion/TestMatrixInversion.{vcxproj,vcxproj.filters} | 矩阵求逆 VS 工程 |
| matrixinvert/{.gitignore,CMakeLists.txt,TestDriver.hpp,TestDriver.cpp,TestDriver_BigMatrix.cpp} | 矩阵求逆测试（含大矩阵） |
| pathconcatenator/{CMakeLists.txt,TestDriver.hpp,TestDriver.cpp} | 路径拼接测试 |

### 表 4.5 UnitTests（src/UnitTests，143 文件）

| 相对路径 | 职责 |
|---|---|
| README.txt | Windows GCC 运行说明 |
| BuildEnv.mk | 顶层构建环境（GMAT_BASE 路径等） |
| build/windows/BuildEnv.mk | Windows 版构建环境副本 |
| Common/TestOutput.{hpp,cpp} | 自研断言/输出类 |
| TestAnomaly/TestAnomaly.cpp | 真近点角异常测试 |
| TestArray/TestArray.cpp | ArrayTemplate 测试 |
| TestAttitude/{MakeAttitude.eclipse,MakeConvert.mac,TestConvert.cpp,testAttitude} | 姿态转换测试 |
| TestBurn/{Makefile.win,TestImpulsiveBurn.cpp,TestImpulsiveBurn.dev,TestImpulsiveBurnOut.txt} | 脉冲点火测试 |
| TestCode500EphemFile/{MakeCode500EphemFile.gcc,TestByteSwapping.cpp,TestCode500EphemFile.cpp} | Code-500 星历测试（字节序） |
| TestCommandUtil/{Makefile.win,TestCommandUtil.cpp} | 命令工具测试 |
| TestConsoleApp/{Makefile.win,TestConsoleApp.cpp} | 控制台应用测试 |
| TestCoordSystem/*.{cpp,Make*}（约 13 .cpp + 12 Makefile） | 坐标系/轴系/历元转换测试（TestCoord/TestCoord2/TestCoord3/TestEcSystems/TestGS/TestGS_2/TestItrf/TestTime/TestTODEq/TestTOEEq/TestBodyInertial） |
| TestDirectoryReader/TestDirectoryReader.cpp | 目录读取测试 |
| TestElementConversion/TestElementConversion.cpp | 轨道要素转换测试 |
| TestEop/{MakeEop.mac,TestEOP.cpp} | EOP 文件测试 |
| TestEphemerisFile/{Makefile.win,TestEphemerisFile.cpp} | 星历文件测试 |
| TestFileManager/{Makefile.win,MakeFileManager.gcc,TestFileManager.cpp} | FileManager 测试 |
| TestFileUtil/{Makefile.win,MakeFileUtil.gcc,TestFileUtil.cpp} | FileUtil 测试 |
| TestForceModel/{ConsoleAppException.{hpp,cpp},Makefile.linux,MakeForce.mac,TestForces.cpp,TestForcesAgain.cpp} | 力模型测试 |
| TestFunction/{Makefile.win,TestFunction.cpp} | 函数测试 |
| TestGmatFunctionParsing/{Makefile.win,TestGmatFunctionParsing.cpp,TestGmatFunctionParsingIn.txt,TestGmatFunctionParsingOut.txt} | GmatFunction 解析测试 |
| TestGravityFile/{TestGravityFile.cpp,TestGravityFileIn.txt} | 重力场文件测试 |
| TestImpBurn/TestImpulsiveBurn.cpp | 脉冲点火测试（副本） |
| TestInterpolator/{driver.cpp,Makefile.linux} | 插值驱动 |
| TestLagrangeInterpolator/{Makefile.win,TestLagrangeInterpolator.cpp} | 拉格朗日插值测试 |
| TestLinearAlgebra/TestLinearAlgebra.cpp | 线性代数测试 |
| TestManeuvers/{Makefile.linux,TestManeuvers.cpp} | 机动测试 |
| TestMath/{Makefile.win,SimpleMathNode.{hpp,cpp},TestMath.cpp} | 数学节点测试 |
| TestMathParser/{MakeMathParser.gcc,TestMathParser.cpp} | 数学解析器测试 |
| TestMatlabInterface/{Makefile.win,TestMatlabInterface.cpp} | MATLAB 接口测试 |
| TestModerator/{Makefile.win,TestModerator.cpp} | Moderator 测试 |
| TestParam/{Makefile.win,MyEtParam.{hpp,cpp},TestBplaneParam.cpp,TestBurnParam.cpp,TestExpParser.cpp,TestParam.cpp,TestParamDatabase.cpp,TestVariable.cpp} | 参数系统测试 |
| TestPropSetup/{Makefile.win,TestPropSetup.cpp} | 传播配置测试 |
| TestPropagators/{Makefile.linux,TestGators.cpp} | 传播器测试 |
| TestRealUtil/{MakeRealUtil.gcc,TestRealUtil.cpp} | RealUtilities 测试 |
| TestRepConversion/{Makefile.mac,TestRepConversion.cpp} | 报告转换测试 |
| TestRmatrix/TestRmatrix.cpp | Rmatrix 测试 |
| TestRmatrix66/{Makefile.win,TestRmatrix66.cpp} | Rmatrix66 测试 |
| TestSPK/{Makefile.mac_intel,TestSpiceKernelWriter.cpp} | SPICE 内核写出测试 |
| TestScriptInterpreter/{MakeConsole.eclipse,driver.cpp,Makefile.linux,Makefile.mac,Makefile.win,driver.hpp} | 脚本解释器测试 |
| TestScriptReadWriter/{Makefile.win,TestScriptReadWriter.cpp,TestScriptReadWriterIn.txt} | 脚本读写测试 |
| TestSolarSystem/{MakeBary.mac,MakeLibBary.mac,MakeLibration.mac,MakeLow.mac,TestBary.cpp,TestLibWithBary.cpp,TestLibration.cpp,TestLow.cpp} | 太阳系/质心/平动点测试 |
| TestSpacecraft/{Makefile.mac,TestFunction.{hpp,cpp},TestSpacecraft.cpp} | 航天器测试 |
| TestStopCond/{Makefile.win,TestStopCond.cpp} | 停止条件测试 |
| TestStringUtil/{Makefile.win,MakeStringUtil.gcc,TestStringUtil.cpp} | StringUtil 测试 |
| TestTextParser/{Makefile.win,TestTextParser.cpp} | TextParser 测试 |
| TestTime/{Makefile.win,TestTime.cpp} | 时间系统测试 |
| TestToString/{Makefile.win,TestToString.cpp} | ToString 测试 |

### 表 4.6 api-interop（76 文件）

| 相对路径 | 职责 |
|---|---|
| README-APIInteroperability.txt | 目录说明（Python/MATLAB API + Monte 互操作） |
| doc/GmatMonte/make.bat, Makefile, source/conf.py | Sphinx 文档构建 |
| doc/GmatMonte/source/index.rst, introduction.rst, ephemerissharing.rst, maneuverplansharing.rst | 文档正文 |
| doc/GmatMonte/source/ExampleCode/{BuildLunarTransfer.mpy,BuildLunarTransferOrbit.mpy,EnterLunarOrbit.script,lunartransferstart.py,MinimalLunarTransfer.script,PropagateMonteLunarTransfer.script,PropagateToPerilune.script,ReadAndShowGMATEphem.mpy,ReadGMATEphem.mpy,RunLunarTransfer.mpy,settings.mpy,settings.py,ShowTrajectories.py,.gitignore} (14) | 月地转移示例代码 |
| doc/GmatMonte/source/images/*.png (6) | 文档插图 |
| doc/ModelShare/DynamicsSharing.{odp,pdf} | 动力学共享讲稿 |
| doc/ModelShare/Images/GmatPropagation.jpg, GmatPropagationWithMonte.jpg | 插图 |
| doc/ModelShare/PrevPlan/*.pptx, *.xlsx | 前期规划材料 |
| doc/NotesEphemSharing.txt | 星历共享笔记 |
| doc/Requirements/ManeuverSharingReqs.xlsx | 机动共享需求 |
| gmat-monte/datasharing/CovarianceShare/MonteToGMATCovariance.mpy | 协方差互操作主脚本 |
| gmat-monte/datasharing/CovarianceShare/inputs/{computed-final.boa,LEOSATMeasEarth.gmd,monteCovWarmStartLEOSAT.csv,warmstartLEOSAT.script} | 协方差输入数据 |
| gmat-monte/datasharing/CovarianceShare/ReadMe.txt | 说明 |
| gmat-monte/datasharing/DynamicsSharing/{BasicStart.mpy,getExternalMonteForces.py,ReadMe.txt,SimpleExternalForceModel.py,SimpleGmatScript.script} | 动力学共享样例 |
| gmat-monte/datasharing/ephemshare/.gitignore | 忽略规则 |
| gmat-monte/datasharing/ephemshare/LunarTransferExample/{EnterLunarOrbit.script,RunLunarTransfer.mpy,ShowTrajectories.py} | 月地转移星历共享 |
| gmat-monte/datasharing/ephemshare/ReadWriteBasics/{readSPK.script,writeSPK.py} | SPK 读写基础 |
| gmat-monte/datasharing/mnvrshare/hohmann/{.gitignore,GmatFunctions.py,GmatMonte.py,HohmannImpulseSharing.py,HohmannImpulseSharing_Setup.py,HohmannMonte.py,ManeuverPlanSharing_ImpulsiveBurns.py,ManeuverPlanSharing_Setup.py,PlotOrbit.py} | Hohmann 机动规划共享 |
| gmat-monte/datasharing/mnvrshare/lunartransfer/{.gitignore,EnterLunarOrbit.script,FinalLunarOrbit.script,RefineLunarTransfer.mpy,ShowTrajectories.py} | 月地转移机动共享 |
| gmat-monte/datasharing/mnvrshare/raiseApogee/{RaiseApogee.script,ReadMe.txt,RefineRaiseApogee.mpy,ShowTrajectories.py} | 升远地点机动共享 |
| gmat-monte/jupyter/{.gitignore,EphemerisSharing.ipynb,GMAT_HohmannTransfer.ipynb,ImpulsiveBurn.ipynb} | Jupyter notebook 示例 |

### 表 4.7 swig（11 文件）

| 相对路径 | 职责 | 关键内容 |
|---|---|---|
| CMakeLists.txt | SWIG 生成配置 | `_SETUPSWIG` Python/Java |
| arrays_python.i | Python 数组 typemap | `SWIG_PyArrayIn/Out/Argout` |
| gmat.i | Java/MATLAB 主接口 | `%module gmat` + `%include gmat.swg` |
| gmat.swg | 公共接口主体 | `#include "GmatAPI.hpp"` + 全类 DOWNCAST |
| gmat_py.i | Python 主接口 | `%module gmat_py` + shadow/slice 支持 |
| gmatutil_py.i | gmatutil 子集轻量绑定 | `%module gmat_py`（仅 gmatutil） |
| GmatAPI.hpp | C++ 头聚合 | include gmatutil + base 全部 |
| GMATAPI.m | MATLAB 静态封装 | `classdef GMATAPI` + SetClass |
| gmat_matlab_loadlibrary.java | MATLAB 引导 | `loadGMAT/loadLibrary/setGMATPath` |
| JavaSwigUtil.swg | Java 宏 | `DOWNCAST/EXCEPTION/ARRAYRETURN/VECTORCONVERT` |
| PythonSwigUtil.swg | Python 宏 | `DOWNCAST/EXCEPTION/ARRAYRETURN/VECTORCONVERT` |
