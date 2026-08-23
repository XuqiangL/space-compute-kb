# 第7章 传播器、推进剂机动、姿态与停止条件

本章负责 GMAT 传播子系统的五个基础目录：`src/base/propagator/`（30 个文件）、`src/base/burn/`（16 个文件）、`src/base/attitude/`（22 个文件）、`src/base/stopcond/`（3 个文件）、`src/base/event/`（6 个文件），合计 **77 个代码文件**。

> 范围说明（以 glob 清单为准）：本 clone（depth-1）中 `src/base/propagator/` 目录**不含** `EphemerisPropagator`、`SPKPropagator`、`OrbitColor` 等文件——`PropSetup.hpp` 头注释（L64-66）明确写明「解析传播器与星历传播器尚未实现」；`OrbitColor` 是 `SpacePoint` 的属性（`src/base/foundation/SpacePoint.hpp`），不属于传播器目录。`stopcond/` 目录只有基类 `StopCondition`，任务描述中的 `ElapsedTime/Periapse/Apoapse/ModEqAnomaly` 在本 clone 里**不是独立类**，而是由 `StopCondition` 通过 `mStopParamType == "Periapsis"/"Apoapsis"` 标志（`StopCondition.cpp` L1123-1133）与时间参数类型（`ElapsedSecs`/`ElapsedDays`，`StopCondition.cpp` L1263-1272）在内部特判实现。此外，传播主循环位于 `src/base/command/Propagate.cpp`（不在本章五目录内，属命令章），本章只在时序图与停止条件定位处引用其行号，正文以 `stopcond/` 与 `event/` 目录自身代码为准。

## 一、本章目录树

```
src/base/
├── propagator/                        (30 文件：14 .cpp + 16 .hpp)
│   ├── Propagator.hpp / .cpp          传播器抽象基类（GmatBase 派生，纯虚 Step/RawStep）
│   ├── PropagationStateManager.hpp/.cpp  传播状态管理器（PSM，StateManager 派生）
│   ├── PropSetup.hpp / .cpp           传播配置容器（绑定 Propagator + ODEModel + PSM）
│   ├── PropSetupException.hpp         传播配置异常
│   ├── PropagatorException.hpp        传播器异常
│   ├── Integrator.hpp / .cpp          数值积分器抽象基类（Propagator 派生）
│   ├── RungeKutta.hpp / .cpp          自适应 Runge-Kutta 基类（Integrator 派生）
│   ├── RungeKutta89.hpp / .cpp        RK 8(9) 16 级（Verner 1978）
│   ├── PrinceDormand45.hpp / .cpp      RK 4(5) 7 级（Prince & Dormand 1981）
│   ├── PrinceDormand78.hpp / .cpp      RK 7(8) 13 级（Prince & Dormand 1981）
│   ├── RungeKuttaFehlberg56.hpp/.cpp   RK 5(6) 8 级（Fehlberg）
│   ├── RungeKuttaNystrom.hpp / .cpp    Runge-Kutta-Nystrom 基类（RungeKutta 派生，二阶）
│   ├── DormandElMikkawyPrince68.hpp/.cpp  RKN 6(8) 9 级（Dormand-ElMikkawy-Prince）
│   ├── PredictorCorrector.hpp / .cpp   预测-校正积分器基类（Integrator 派生）
│   ├── AdamsBashforthMoulton.hpp/.cpp  4 阶 AB 预测 + AM 校正（PredictorCorrector 派生）
│   └── Cowell.hpp / .cpp               Cowell 积分器（壳，未实现）
├── burn/                              (16 文件：8 .cpp + 8 .hpp)
│   ├── Burn.hpp / .cpp                机动基类（GmatBase 派生，纯虚 Fire）
│   ├── BurnException.hpp / .cpp       机动异常
│   ├── ImpulsiveBurn.hpp / .cpp       脉冲机动（Δv 瞬时施加）
│   ├── FiniteBurn.hpp / .cpp          有限推力机动（多推力器积分推力）
│   ├── ManeuverFrame.hpp / .cpp       机动参考系基类（纯虚 CalculateBasis）
│   ├── ManeuverFrameManager.hpp/.cpp  机动参考系管理器（工厂）
│   ├── InertialManeuverFrame.hpp/.cpp 惯性机动系
│   └── VnbManeuverFrame.hpp / .cpp    VNB（速度-法向-副法向）机动系
├── attitude/                          (22 文件：11 .cpp + 11 .hpp)
│   ├── Attitude.hpp / .cpp            姿态基类（GmatBase 派生，DCM/四元数/欧拉角表示）
│   ├── AttitudeException.hpp / .cpp   姿态异常
│   ├── Kinematic.hpp / .cpp           运动学姿态中间基类
│   ├── CSFixed.hpp / .cpp             坐标系固定姿态
│   ├── Spinner.hpp / .cpp             自旋姿态（欧拉轴/角速度）
│   ├── PrecessingSpinner.hpp / .cpp   进动自旋姿态
│   ├── NadirPointing.hpp / .cpp       对地（天底）指向姿态（TRIAD）
│   ├── CommandableNadirPointing.hpp/.cpp  命令模式可设的对地指向
│   ├── ThreeAxisKinematic.hpp / .cpp  三轴运动学（四元数传播）
│   ├── CCSDSAttitude.hpp / .cpp       CCSDS-AEM 星历姿态
│   └── SpiceAttitude.hpp / .cpp       SPICE CK 内核姿态
├── stopcond/                          (3 文件：1 .cpp + 2 .hpp)
│   ├── StopCondition.hpp / .cpp       停止条件基类（Evaluate/AddToBuffer/插值定位）
│   └── StopConditionException.hpp     停止条件异常
└── event/                             (6 文件：3 .cpp + 3 .hpp)
    ├── EventLocator.hpp / .cpp        事件定位器基类（蚀/接触等，纯虚 FindEvents）
    ├── LocatedEvent.hpp / .cpp        已定位事件（起止历元/时长）
    └── EventException.hpp / .cpp      事件异常
```

## 二、逐文件/逐类讲解

### 2.1 propagator/ —— 传播器与数值积分器

#### Propagator.hpp / Propagator.cpp —— 传播器抽象基类

**职责一句话**：所有传播器（数值积分器、未来的解析/星历传播器）的公共接口，定义状态推进协议、物理模型绑定与传播方向/步长控制。

**关键类/函数**：

- `class Propagator : public GmatBase`（`Propagator.hpp` L88）：构造时以 `Gmat::PROPAGATOR` 类型注册（`Propagator.cpp` L139），默认 `stepSize = 60.0` 秒、`centralBody = "Earth"`（L140-158）。
- 纯虚协议（`Propagator.hpp` L202/L210/L218）：

```cpp
virtual bool Step() = 0;            // 按 stepSize 推进一个（误差受控）步
virtual bool RawStep() = 0;         // 无误差控制的裸步
virtual Real GetStepTaken() = 0;    // 报告最近一步实际步长
```

`Step()` 是核心传播例程：自适应步长传播器在精度允许时取期望步，并把 `stepSize` 调整为估计的下一步最优值（注释 L192-200）。`GetStepTaken()` 用于多个传播器并发步进的对齐（`Integrator.cpp` L646-649）。

- `virtual bool Initialize()`（`Propagator.hpp` L135；实现 `Propagator.cpp` L725）：若 `UsesODEModel()` 为真则调用 `physicalModel->Initialize()`，并把 `inState`/`outState` 都指向 `physicalModel->GetState()`（L748-749）；否则取 `GetAnalyticState()`。这是**传播器与力模型握手的入口**。
- `virtual void SetPhysicalModel(PhysicalModel*)`（`Propagator.cpp` L790）：把 `physicalModel` 成员接上（L792）。
- `virtual bool UsesODEModel()`（`Propagator.cpp` L895）：默认返回 `true`；解析/星历传播器覆写为 `false` 以告知 `PropSetup` 是否需要 ODEModel。
- 状态转发接口：`GetState()`（L989）、`GetJ2KState()`（L1009）、`GetDimension()`（L969）、`UpdateSpaceObject()`（L1029）、`BufferState()/RevertSpaceObject()`（L1097/L1074）——这些方法在 `physicalModel` 是 ODEModel 时直接转发，为「不用 ODEModel 的传播器」预留统一入口（注释 L938-947）。
- 参数表：`INITIAL_STEP_SIZE`（初值 `InitialStepSize`，见 `Propagator.cpp` L100-106 与 `PARAMETER_TEXT`），`AlwaysUpdateStepsize`、`ProcessNoiseTimeStep`、`TimeToNextNoiseStep`；`STEP_SIZE_TOLERANCE = 0.0001` 秒用于拒绝零步长（L117）。
- 有限推力联动：`SetBurning()/IsBurning()/SetLastBurn()/GetlastBurn()/GetHasFiniteBurn()/SetHasFiniteBurn()`（L1434-1514）——传播器用 `hasFiniteBurn` 标志「步内是否存在有限推力」，`burning/lastBurn` 用于被力模型缩短步后的接力步（见 `RungeKutta::Step()` 的 `followUpStep` 逻辑）。
- `FindTimeStep()`（L1529）/`SetNoiseStep()`（L1586）：进程噪声（ProcessNoiseModel）步长调度，在 `Propagate::TakeAStep()` 中调用（L1524 注释）。
- 历元有效性：`LoadSpans()`/`IsValidEpoch()`（L1203/L1225）为星历传播器的历元间隙（span gap）预留，默认返回真。

#### PropagationStateManager.hpp / .cpp —— 传播状态管理器（PSM）

**职责一句话**：`PropSetup` 与 GMAT 对象（航天器）之间的状态桥梁——负责把「需要传播的对象属性」组装成状态向量，传播后再把向量写回对象。

**关键类/函数**：

- `class PropagationStateManager : public StateManager`（`PropagationStateManager.hpp` L41）。
- `BuildState()`/`MapObjectsToVector()`/`MapVectorToObjects()`（L57-59）：构建状态向量、对象→向量、向量→对象的映射。
- `RequiresCompletion()`/`GetCompletionCount()`/`GetCompletionIndex()`（L60-64）：处理「叠加后需补算」的元素（如 STM、协方差）。
- 协方差传播：`PropagateCovarianceMatrix()`、`UpdateProcessNoiseCholesky()` 等（L67-70）。
- 在 `PropSetup::PrepareInternals()` 中被组装：`psm.BuildState()` → `mODEModel->SetPropStateManager(&psm)` → `mODEModel->SetState(psm.GetState())`（`PropSetup.cpp` L576-583）。

#### PropSetup.hpp / .cpp —— 传播配置容器

**职责一句话**：传播子系统对外的门面对象，聚合 `Propagator`、`ODEModel`（力模型容器）与 `PropagationStateManager`，是 GMAT 脚本中 `Create Propagator` 命令对应的配置实体。

**关键类/函数**：

- `class PropSetup : public GmatBase`（`PropSetup.hpp` L80）；成员 `mPropagator`、`mODEModel`、`psm`（L209-211）。
- 构造即建默认配置（`PropSetup.cpp` L172-183）：

```cpp
mPropagator = new RungeKutta89("RungeKutta89");   // 默认积分器
mODEModel   = new ODEModel(mODEModelName);          // 默认力模型容器
PhysicalModel *pmf = new PointMassForce;            // 默认质点引力
mODEModel->AddForce(pmf);
```

即默认 PropSetup 是「RK8(9) + 仅质点引力」的地球轨道传播器。

- `SetPropagator()`（L407）：替换积分器；若非 GUI 且已命名配置，禁止二次更换积分器类型（L420-428）；若新传播器 `UsesODEModel()==false` 则删除 ODEModel（L441-442）。
- `SetODEModel()`（L471）、`AddForce(PhysicalModel*)`（L501，转发 `mODEModel->AddForce`）、`GetForce()/GetNumForces()`（L514/L527）。
- `PrepareInternals()`（L573-600）：**组装核心**——构建 PSM 状态 → 把 PSM 交给 ODEModel → `mODEModel->Initialize()` → `BuildModelFromMap()` → `UpdateInitialData()` → `mPropagator->Initialize()`。
- `Initialize()`（L1463-1518）：校验积分器/力模型非空且至少一个力后，执行 `mPropagator->SetPhysicalModel(mODEModel)`（L1503），完成**物理模型向积分器的注入**。
- 参数透传：`ACCURACY/INITIAL_STEP_SIZE/MIN_STEP/MAX_STEP/...` 等参数通过 `GetOwnedObjectId(id, Gmat::PROPAGATOR)` 把 id 映射到积分器参数后转发（`GetRealParameter` L1132-1157、`SetRealParameter` L1176-1216）。

#### Integrator.hpp / .cpp —— 数值积分器抽象基类

**职责一句话**：为一阶常微分方程 `dr/dt = f(t,r)`（`Integrator.hpp` L86-98 注释）定义积分接口，并提供步长控制、容差与固定步长基础设施。

**关键类/函数**：

- `class Integrator : public Propagator`（`Integrator.hpp` L128）。
- 纯虚：`Initialize()`（L177）、`RawStep()`（L179）、`EstimateError()`（L209，返回最大的相对误差估计）、`AdaptStep(Real maxerror)`（L229，按误差调整步长）。
- 参数与默认值（`Integrator.cpp` L133-152）：`tolerance = 1.0e-11`（Accuracy）、`minimumStep = 0.001` s、`maximumStep = 2700.0` s（45 分钟）、`maxStepAttempts = 50`、`stopIfAccuracyViolated = true`、`errorThreshold = 0.10`、`derivativeOrder = 1`、`hasErrorControl = true`。
- `SetPhysicalModel()`（L629-637）：调用基类后，把本地 `errorThreshold` 同步进物理模型。
- `UsesErrorControl()`（L668）：返回 `hasErrorControl`（供 PropSetup 警告「无误差控制的积分器忽略 Accuracy」）。
- `TakeAction("PrepareForRun"/"ChangeTypeSourceString")`（L595-615）：复位精度告警标志、替换告警信息里的类型名（如「Starter for Predictor-Corrector」）。

#### RungeKutta.hpp / .cpp —— 自适应 Runge-Kutta 基类

**职责一句话**：实现通用显式 RK 步进与嵌入法误差估计/步长自适应骨架，具体系数由派生类 `SetCoefficients()` 提供。

**关键类/函数**：

- `class RungeKutta : public Integrator`（`RungeKutta.hpp` L151）。成员 `ai`（各阶段时刻份额）、`bij`（级间系数）、`cj`（累加系数）、`ee`（误差系数 `c - c*`），见 L170-187。
- 构造（`RungeKutta.cpp` L87-100）：

```cpp
sigma    (0.9),              // 安全因子
incPower (1.0/order),        // 放大步长指数 1/m
decPower (1.0/(order-1)),    // 缩小步长指数 1/(m-1)
```

- `Initialize()`（L203-289）：`Propagator::Initialize()` 后按 `stages` 分配 `ai/bij/cj/ki/ee`，`derivativeOrder==1` 时调 `SetCoefficients()`（L281-285）。
- `Step()`（L304-497）：**步进主循环**。要点：
  1. 用 `minimumStep/maximumStep` 夹逼 `stepSize`（L320-323）；
  2. `physicalModel->GetForceMaxStep(stepSize>0.0)` 取力模型允许的最大步（L334），若请求步大于力模型最大步则 `stepSize = forceMaxStep` 并标记 `stepLimited`（L335-365）；
  3. `do { RawStep(); maxerror = EstimateError(); AdaptStep(maxerror) }` 直到 `goodStepTaken`（L407-432）；
  4. `physicalModel->IncrementTime(stepTaken)`（L442）；
  5. 若步被力模型缩短（`stepLimited`），把剩余时间作为「接力步」递归 `Step()` 补齐（L468-484），有限推力则返回 false 交由上层处理（L449-462）。
- `RawStep()`（L506-600）：经典 RK 级计算——每级先把 `inState` 拷入 `stageState`，累加 `bij[i][j]*ki[j]`（L543-550），调 `physicalModel->GetDerivatives(stageState, stepSize*ai[i])` 取导数（L560），`ki[i][j] = stepSize * ddt[j]`（L577）；最后 `candidateState = inState + Σ cj[i]*ki[i]`（L581-588）。
- `EstimateError()`（L679-694）：`errorEstimates[i] = Σ ee[j]*ki[j][i]`，再交给 `physicalModel->EstimateError(errorEstimates, candidateState)` 归一化取最大。
- `AdaptStep()`（L718-767）：

```cpp
if (maxerror > tolerance) {                 // 误差过大 → 缩小重试
   stepSize = sigma * stepSize * pow(tolerance/maxerror, decPower);
   ++stepAttempts; return false;            // 拒绝本步
}
stepSize = sigma * stepSize * pow(tolerance/maxerror, incPower);  // 接受并放大
memcpy(outState, candidateState, ...); return true;
```

  L727-748 有一个「最小步长时豁免误差控制」的 kludge，用于跨过圆柱影模型的 SRP 不连续（注释 L702-712）。

#### RungeKutta89.hpp / .cpp —— RK 8(9)

**职责一句话**：16 级 9 阶 RK 积分器，8 阶嵌入误差控制。

**关键点**：

- 构造 `RungeKutta(16, 9, "RungeKutta89", nomme)`（`RungeKutta89.cpp` L79-80）。
- `SetCoefficients()`（L152-364）填 16 级 Butcher 表：`ai[]`（L161-176）、`bij[][]`（L179-329）、`cj[]`（L331-346）、`ee[]`（L348-363）。注释 L148-149 注明系数来自 **Verner 1978（SIAM J. Numer. Anal. 15(4)）**。以 `rt6 = sqrt(6.0)` 符号化大量无理系数。
- 是 `PropSetup` 的默认积分器，也是 ABM/P-C 的启动器（`starter`）。

#### PrinceDormand45.hpp / .cpp —— RK 4(5)

**职责一句话**：7 级 5 阶 RK，4 阶嵌入误差控制。

**关键点**：

- 构造 `RungeKutta(7, 5, "PrinceDormand45", nomme)`（`PrinceDormand45.cpp` L67-68）。
- `SetCoefficients()`（L143-209）：`ai[]`（L150-156）、`bij[][]`（L158-191）、`cj[]`（L194-200）、`ee[]`（L202-208，显式写出 `c - c*` 差，如 `19/200 - 431/5000`）。系数来自 **Prince & Dormand 1981**（注释 L140）。该表最后一个 `cj[6]=0`、`ee[6]=1/50` 是 FSAL（First Same As Last）结构特征。

#### PrinceDormand78.hpp / .cpp —— RK 7(8)

**职责一句话**：13 级 8 阶 RK，7 阶嵌入误差控制。

**关键点**：

- 构造 `RungeKutta(13, 8, "PrinceDormand78", nomme)`（`PrinceDormand78.cpp` L62-63）。
- `SetCoefficients()`（L141-286）：`ai[]`（L148-160，含大整数有理数如 `ai[8]=5490023248/9719169821`）、`bij[][]`（L162-252）、`cj[]`（L254-266）。误差系数采用**两套累加系数之差**：局部数组 `cjhat[13]`（L270-282）后 `ee[i] = cj[i] - cjhat[i]`（L284-285）。注释 L135-139 注明系数源自 GSFC 提供、Thinking Systems 整理。

#### RungeKuttaFehlberg56.hpp / .cpp —— RK 5(6)

**职责一句话**：8 级 RK，6 阶积分 + 5 阶误差控制（Fehlberg 系数）。

**关键点**：

- `SetCoefficients()`（`RungeKuttaFehlberg56.cpp` 中）：`bij[][]`（L125-160）、`cj[]`（L162-169）、`ee[]`（L171-178，如 `7/1408 - 31/384`）。头注释（`RungeKuttaFehlberg56.hpp` L60-62）说明「六阶积分、五阶误差控制」。

#### RungeKuttaNystrom.hpp / .cpp —— Runge-Kutta-Nystrom 基类

**职责一句话**：为二阶方程 `d²r/dt² = g(t,r)`（`RungeKuttaNystrom.hpp` L53-92 注释）定制的 RK 变体，直接用加速度（而非速度）作为阶段量。

**关键点**：

- `class RungeKuttaNystrom : public RungeKutta`（L93）；构造 `derivativeOrder = 2`（`RungeKuttaNystrom.cpp` L91），`GetPropagatorOrder()` 返回 2（L454）。
- `Initialize()` 中通过 `physicalModel->GetComponentMap(derivativeMap)` 获取「分量 ↔ 一阶导」映射（L241）。
- 额外系数 `cdotj`（推进一阶导/速度的系数）、`derivativeMap/inverseMap`（L114-118 头）、`eeDeriv`（导数误差系数，L122）。
- `RawStep()` 用 `cdotj` 与 `inverseMap` 推进速度分量（L436-437）。
- 子类 `DormandElMikkawyPrince68` 与（未在本目录的）其他 Nystrom 方法共享此骨架。

#### DormandElMikkawyPrince68.hpp / .cpp —— RKN 6(8)

**职责一句话**：9 级 RKN 积分器，8 阶积分 + 6 阶误差控制，对因变量与其一阶导（速度）同时做误差控制。

**关键点**：

- `class DormandElMikkawyPrince68 : public RungeKuttaNystrom`（`DormandElMikkawyPrince68.hpp` L62）；拷贝构造设 `derivativeError = true`（`DormandElMikkawyPrince68.cpp` L71）。
- `SetCoefficients()`（L98-…）：9 级 Butcher 表 `ai[0..8]`（L107-115）、`bij[][]`（L117 起）。头注释 L57-60 注明源自 **Dormand, El-Mikkawy & Prince 1987**（1991 修正），是 GMAT 里唯一同时控制位置与速度误差的积分器。

#### PredictorCorrector.hpp / .cpp —— 预测-校正积分器基类

**职责一句话**：多步法骨架——用历史状态「预测」下一状态，再用预测态导数「校正」，误差取自预测/校正之差。

**关键类/函数**（`PredictorCorrector.hpp`）：

- `class PredictorCorrector : public Integrator`（L93）；`stepCount`（历史步数）、`history`（历史导数矩阵）、`pweights/cweights`（预测/校正权）、`predictorState/correctorState`（L134-149）。
- 纯虚 `SetWeights()/FireStartupStep()/Predict()/Correct()/Reset()`（L176-216）——派生类实现具体算法。
- `starter`（L163）：启动传播器（`RungeKutta89`），用于填充初始历史。
- `Initialize()`（`PredictorCorrector.cpp` L256-447）：校验 `LowerError < TargetError < Accuracy`（L269-275），分配历史/权数组，配置 `starter`（`new RungeKutta89` L418-419），并把 `starter->SetPhysicalModel(physicalModel)`（L421）。
- `Step(Real dt)`（L460-526）：把目标区间切分为整数个 `stepSize` 子步后循环 `Step()`。
- `Step()`（L564 起）：启动期调用 `FireStartupStep()`，完成后按 `Predict()`→`Correct()`→`EstimateError()`→`AdaptStep()` 推进。
- `BufferHistory()`（L538-552）：回退一步历史，供 `RevertSpaceObject()` 清理最后一步（`Propagator.cpp` L1080-1083 会调用它）。

#### AdamsBashforthMoulton.hpp / .cpp —— ABM 预测-校正

**职责一句话**：4 阶 Adams-Bashforth 预测 + Adams-Moulton 校正。

**关键点**：

- 头注释给出公式（`AdamsBashforthMoulton.hpp` L63-79）：预测 `h/24·[55fₙ - 59fₙ₋₁ + 37fₙ₋₂ - 9fₙ₋₃]`，校正 `h/24·[9f*ₙ₊₁ + 19fₙ - 5fₙ₋₁ + fₙ₋₂]`，误差 `19/270·|r⁽C⁾ - r⁽P⁾|`。
- 构造 `PredictorCorrector(4, 4, "AdamsBashforthMoulton", nomme)`，`eeFactor = 19.0/270.0`，`starter = new RungeKutta89`（`AdamsBashforthMoulton.cpp` L68-72）。
- `SetWeights()`（L146-162）：`pweights = {55,-59,37,-9}/24`、`cweights = {9,19,-5,1}/24`。
- `Predict()`（L224-269）：求当前导数，滚动历史，`predictorState = inState + stepSize·Σ pweights·history`。
- `Correct()`（L280-307）：用预测态求导，`correctorState = inState + stepSize·(cweights·ddt + Σ cweights·history)`。
- `EstimateError()`（L330-340）：`eeFactor·|corrector - predictor|`。
- `FireStartupStep()`（L173-213）：用 RK89 走 3 步填充历史后 `startupComplete = true`。

#### Cowell.hpp / .cpp —— Cowell 积分器（壳）

**职责一句话**：Cowell 预测-校正积分器的**未实现外壳**。

**关键点**：头注释（`Cowell.hpp` L23-24、L37-38）明确「shell … not currently implemented」。`Step()` 仅返回 `true` 不推进（`Cowell.cpp` L192-198），`Step(Real dt)` 同样空转（L149-157），`AdaptStep()` 恒返回 `true`（L240-243）。保留它是为将来的二阶（位置-加速度）多步法占位。

#### PropagatorException.hpp / PropSetupException.hpp —— 异常

**职责一句话**：传播子系统专用异常，均派生自 `BaseException`。

- `PropagatorException`（`PropagatorException.hpp` L36）：前缀 `"Propagator Exception: "`。
- `PropSetupException`（`PropSetupException.hpp` L36）：前缀 `"PropSetup Exception: "`。

### 2.2 burn/ —— 机动

#### Burn.hpp / .cpp —— 机动基类

**职责一句话**：脉冲/有限推力机动的公共基类，定义 Δv 的坐标系表达、惯性系转换与「点火」接口。

**关键类/函数**：

- `class Burn : public GmatBase`（`Burn.hpp` L44）。
- 纯虚 `virtual bool Fire(Real *burnData, Real epoch, bool backwards) = 0`（L121）：派生类实现具体点火数学。
- 成员（L129-180）：`deltaV[3]`（含脉冲 Δv 幅值的机动态矢量）、`deltaVInertial[3]`（惯性系 Δv）、`totalAccel[3]/totalThrust[3]`（有限推力）、`frameBasis[3][3]`（机动系基矢）、`isFiring/hasFired`。
- `ConvertDeltaVToInertial(Real *dv, Real *dvInertial, Real epoch)`（L188）：用 `frameBasis` 把机动态矢量旋到惯性系。
- 参数：`CoordinateSystem/BurnOrigin/BurnAxes/DeltaV1..3/SatName`（enum L192-203）。

#### ImpulsiveBurn.hpp / .cpp —— 脉冲机动

**职责一句话**：瞬时 Δv 机动，把 Δv 一次性加到航天器速度上，并按 Isp 消耗燃料质量。

**关键类/函数**：

- `class ImpulsiveBurn : public Burn`（`ImpulsiveBurn.hpp` L44）；成员 `isp/gravityAccel/deltaTankMass/decrementMass`（L109-118）。
- `Fire()`（`ImpulsiveBurn.cpp` L218）：
  1. 若无显式 epoch，取航天器 `A1Epoch`（L246-247）；
  2. `ConvertDeltaVToInertial(deltaV, deltaVInertial, epoch)`（L266）把 Δv 从机动系旋到惯性系；
  3. **正向**：`satState[3..5] += deltaVInertial` 直接加到速度分量（L317-319 之后的正向路径）；
  4. **反向传播**：迭代校正——先施加 `-deltaVInertial`，再前向点火 `ConvertDeltaVToInertial` 得到终态，反复调整直到「反向点火 + 正向点火 = 0」收敛（L268-329 的 `do/while`）。
- `TransformDeltaVToJ2kFrame()`（L469）：另一次 J2000 系转换入口。

#### FiniteBurn.hpp / .cpp —— 有限推力机动

**职责一句话**：多推力器有限推力模型，把各推力器的推力/质量流率累计成总加速度，供传播期间积分。

**关键类/函数**：

- `class FiniteBurn : public Burn`（`FiniteBurn.hpp` L42）；成员 `thrusterNames/thrusterMap`（推力器列表，L112-114）、`isElectricBurn`、`burnEpoch/burnState/burnMass`。
- `Fire()`（`FiniteBurn.cpp` L262-…）：
  1. 若电推进，`ComputeThrottleLogic(availablePower)` 先分配功率（L305-309）；
  2. 遍历推力器：`current->ComputeInertialDirection(epoch)` 取惯性方向，`dm += current->CalculateMassFlow()`，`tOverM = thrust·thrustScaleFactor·dutyCycle/(tMass·norm·1000)`（L350-351）；
  3. `deltaV[] += dir·tOverM` 累加加速度（L354-356），`totalThrust[] += dir/norm·appliedThrustMag`（L364-366）。
- 与力模型联动：`FiniteBurn` 是 `Thruster` 的友元（L328 注释），其累计的 `totalAccel` 由力模型（`TransientForce`/推力模型）在 `GetDerivatives` 时消费，从而在积分步内叠加推力加速度。`Propagator::hasFiniteBurn` 标志由 `RungeKutta::Step()` 检测力模型中的 `FileThrust` 类型设置（`RungeKutta.cpp` L340-347）。

#### ManeuverFrame.hpp / .cpp + 派生系 + ManeuverFrameManager

**职责一句话**：机动参考系——把「体轴系/VNB/惯性」等坐标系表达为 3×3 基矢矩阵，供 `Burn::ConvertDeltaVToInertial` 使用。

- `class ManeuverFrame`（`ManeuverFrame.hpp` L41）：`SetState(Real *pos, Real *vel)`（L49）、`CalculateBasis()` 纯虚（L80）、`basisMatrix[3][3]` 缓冲（L55）。
- `InertialManeuverFrame`（`InertialManeuverFrame.hpp` L38）：惯性系基矢（单位阵）。
- `VnbManeuverFrame::CalculateBasis()`（`VnbManeuverFrame.cpp` L110-149）：**V 轴 = 速度方向**（L116-123），**N 轴 = r×v 归一**（L126-134），**B 轴 = v×n**（L137-148）；`GetFrameLabel` 返回 "V"/"N"/"B"（L163-177）。
- `ManeuverFrameManager`（`ManeuverFrameManager.hpp` L45）：`GetSupportedFrames()`/`GetFrameInstance()`（L51-52）——轻量工厂，按字符串创建机动系实例。

#### BurnException.hpp / .cpp —— 机动异常

**职责一句话**：机动子系统异常，派生自 `BaseException`。

### 2.3 attitude/ —— 姿态模型

#### Attitude.hpp / .cpp —— 姿态基类

**职责一句话**：姿态表示的公共基类，维护「惯性系 → 体轴系」方向余弦阵（DCM）与角速度，并提供四元数/欧拉角/DCM/MRP 之间的换算。

**关键类/函数**：

- `class Attitude : public GmatBase`（`Attitude.hpp` L78）。表示类型枚举 `QUATERNION_TYPE / DIRECTION_COSINE_MATRIX_TYPE / EULER_ANGLES_AND_SEQUENCE_TYPE / MODIFIED_RODRIGUES_PARAMETERS_TYPE`（L60-66）。
- 核心成员：`RBi`（初始 Fi→Fb 旋转阵，L380）、`dcm`（当前惯性→体 DCM，L386）、`angVel`（相对惯性系角速度，L389）、`quaternion/eulerAngles/mrps`（各表示缓存，L396-403）。
- 关键接口：`GetCosineMatrix(Real atTime)`（L137）、`GetQuaternion()/GetEulerAngles()/GetAngularVelocity()/GetEulerAngleRates()`（L127-140）、`GetRotationMatrix(const GmatTime&)`（L245）。
- 纯虚 `ComputeCosineMatrixAndAngularVelocity(Real/GmatTime&)`（L463-464）——**叶子姿态类实现具体姿态运动学**，更新 `dcm` 与 `angVel`。
- `Initialize()`（`Attitude.cpp` L658-746）：根据输入表示换算 DCM——四元数 `ToCosineMatrix`（L689）、欧拉角+序列 `ToCosineMatrix`（L703-706）、MRP `ToQuaternion→ToCosineMatrix`（L697-698）；再据角速度/欧拉角率初始化 `angVel`（L712-726）；最后 `RBi=dcm; wIBi=angVel`（L729-730）。
- `GetRotationMatrix()`（L4056-4067）：调用 `ComputeCosineMatrixAndAngularVelocity` 后返回 DCM——**这是力模型消费姿态的入口**（太阳光压/阻力需要体轴系相对惯性系的方向余弦阵来投影面积/法向）。

**姿态被力模型消费**：`Spacecraft` 持有 `Attitude`，SRP/阻力等力模型在 `GetDerivatives` 时调用 `GetCosineMatrix(epoch)` 把体固定面积/法向旋到惯性系，从而得到正确的截面与光压合力（`GetRotationMatrix` 即此类调用的包装）。

#### Kinematic.hpp / .cpp —— 运动学姿态中间基类

**职责一句话**：`CSFixed/Spinner/PrecessingSpinner/NadirPointing/ThreeAxisKinematic/CommandableNadirPointing` 的共同基类，本身不新增成员（`KinematicParamCount = AttitudeParamCount`，`Kinematic.hpp` L56-59）。

#### CSFixed.hpp / .cpp —— 坐标系固定姿态

**职责一句话**：体轴相对惯性系**固定不动**的姿态（DCM 恒定，角速度为零）。

- `class CSFixed : public Kinematic`（`CSFixed.hpp` L47）。`ComputeCosineMatrixAndAngularVelocity` 直接沿用初始化得到的 `RBi`，角速度保持 0。

#### Spinner.hpp / .cpp —— 自旋姿态

**职责一句话**：绕固定欧拉轴以恒定角速度自旋的姿态。

**关键点**：

- `class Spinner : public Kinematic`（`Spinner.hpp` L45）；成员 `RB0I`（t0 时刻 Fi→Fb）、`initialwMag`、`initialeAxis`（L70-74）。
- `Initialize()`（`Spinner.cpp` L150-178）：`RB0I = RBi`（L161）、`initialwMag = angVel.GetMagnitude()`、`initialeAxis = angVel/initialwMag`（L175-176）。
- `ComputeCosineMatrixAndAngularVelocity`（L214-244）：

```cpp
Real theEAngle = initialwMag * dt;                       // 绕轴转角
Rmatrix33 RBB0t = AttitudeConversionUtility::EulerAxisAndAngleToDCM(initialeAxis, theEAngle);
dcm = RBB0t * RB0I;                                       // 组合旋转
```

#### PrecessingSpinner.hpp / .cpp —— 进动自旋姿态

**职责一句话**：在自旋基础上叠加章动/进动（`nutationReferenceVector/bodySpinAxis/initialPrecessionAngle/precessionRate/nutationAngle/initialSpinAngle/spinRate`，`Attitude.hpp` L430-436）。

- `class PrecessingSpinner : public Kinematic`（`PrecessingSpinner.hpp` L45）；成员 `xAxis/yAxis/bodySpinAxisNormalized/nutationReferenceVectorNormalized`（L70-73）。

#### NadirPointing.hpp / .cpp —— 对地（天底）指向姿态

**职责一句话**：体轴 +Z 指向天底、-Y 指向轨道面法向的对地姿态，用 TRIAD 算法构造 DCM。

**关键点**：

- `class NadirPointing : public Kinematic`（`NadirPointing.hpp` L42）；成员 `bodyAlignmentVector/bodyConstraintVector`（继承自 Attitude，见 `Attitude.hpp` L443）。
- `TRIAD(V1,V2,W1,W2)`（`NadirPointing.cpp` L180）：双矢量定姿算法，返回 A→B 旋转阵。
- `ComputeCosineMatrixAndAngularVelocity`（L270-…）：由位置/速度构造参考系（LVLH 类）矢量，然后 `RiB = TRIAD(bodyAlignmentVector, bodyConstraintVector, referenceVector, constraintVector)`（L381）。

#### CommandableNadirPointing.hpp / .cpp —— 命令模式可设对地指向

**职责一句话**：允许在任务序列运行中（Command mode）修改四元数/姿态参数的对地指向变体。

- `class CommandableNadirPointing : public Kinematic`（`CommandableNadirPointing.hpp` L41）；覆写 `SetRvectorParameter/SetRmatrixParameter` 以支持运行中设置四元数（L83-86），`IsParameterCommandModeSettable` 放行相应参数（L89）。

#### ThreeAxisKinematic.hpp / .cpp —— 三轴运动学

**职责一句话**：用角速度矢量对四元数做时间传播的姿态模型（`ṗ = ½ Ω p` 形式）。

- `class ThreeAxisKinematic : public Kinematic`（`ThreeAxisKinematic.hpp` L46）；成员 `I44`（4×4 单位阵）、`Omega`（4×4 斜对称阵，L80）、`wMag`。头注释 L29-30 说明「用角速度矢量传播四元数」。

#### CCSDSAttitude.hpp / .cpp —— CCSDS-AEM 姿态

**职责一句话**：从 CCSDS Attitude Ephemeris Message（AEM）文件读取姿态数据的姿态模型。

- `class CCSDSAttitude : public Attitude`（`CCSDSAttitude.hpp` L47）；成员 `reader`（`CCSDSAEMReader*`，L71）。`ComputeCosineMatrixAndAngularVelocity` 由 reader 内插/查表给出。

#### SpiceAttitude.hpp / .cpp —— SPICE CK 姿态

**职责一句话**：从 SPICE CK/SCLK/FK 内核读取航天器指向的姿态模型。

- `class SpiceAttitude : public Attitude`（`SpiceAttitude.hpp` L52）；成员 `reader`（`SpiceAttitudeKernelReader*`，L119）、`scName/naifId/refFrameNaifId`（L123-127）、`ck/sclk/fk` 内核名数组（L129-133）。在 `__USE_SPICE__` 编译宏下生效；`GetCosineMatrix` 等被覆写以保证「与上次更新间隔无关地取到内核值」（L76-89）。

#### AttitudeException.hpp / .cpp —— 姿态异常

**职责一句话**：姿态子系统异常，派生自 `BaseException`。

### 2.4 stopcond/ —— 停止条件

#### StopCondition.hpp / .cpp —— 停止条件基类

**职责一句话**：传播停止条件的统一实现——每步求值 LHS/RHS 参数、检测穿越、并用插值器精确定位穿越历元。

**关键类/函数**：

- `class StopCondition : public GmatBase`（`StopCondition.hpp` L45）；`static const Real STOP_COND_TOL = 1.0e-11`（`StopCondition.cpp` L73）。
- 参数：`BaseEpoch/Epoch/EpochVar/StopVar/Goal/Repeat`（L75-95）。
- 默认插值器：`mInterpolator = new NotAKnotInterpolator("InternalInterpolator")`（构造 L173-181）——非「节点（Not-a-knot）三次样条」。
- `Evaluate()`（L462-677）：**每步求值核心**——取 `mStopParam->EvaluateReal()`（L509）与 goal（`rhsWrapper->EvaluateReal()` 或 goal 参数，L485-500），然后：
  - 非时间参数：若 goal 落在 `[prev, curr]` 之间则 `goalMet = true` 并记 `mStopInterval`（L565-589）；
  - 时间参数：`prevGoalDiff/currGoalDiff` 方向测试判定穿越（L617-655）。
- 特殊条件在 `Initialize()`（L1075-1200）设置：`mStopParamType == "Apoapsis"/"Periapsis"` 时 `currentGoalValue = 0.0` 并置 `isApoapse/isPeriapse`（L1123-1133）；`ElapsedSecs/ElapsedDays` 等时间参数置 `isCyclicTimeCondition`（L1263-1272）。
- `CheckOnPeriapsis()`（L958-997）/`CheckOnApoapsis()`（L1003-1029）：用「R·V 穿越」判据——正向传播近拱点要求 `previousAchievedValue <= currentGoalValue`（R·V 由负转正），远拱点反之（注释 L978-981、L1015-1018）。
- `CheckCyclicCondition()`（L1045-1070）：把角度类参数 `PutInRange` 映射到目标附近，消除 0/360° 折叠。
- `AddToBuffer(bool isInitialPoint)`（L708-874）：**插值定位核心**——把 (LHS 值, epoch) 点滚入环形缓冲，当 `mNumValidPoints >= mBufferSize` 且 goal 被括在 [min,max] 内时，`mInterpolator->AddPoint(lhsValueBuffer[i], &mEpochBuffer[i])` 后 `mInterpolator->Interpolate(currentGoalValue, &stopEpoch)`（L845-853），得到精确穿越历元。
- `GetStopEpoch()`（L886-932）：对时间参数直接 `dt = (goal - prev)·GetTimeMultiplier()`（L898）；否则复用插值器反求 `mStopEpoch`。
- `IsTimeCondition()`（L689）：`mStopParam->IsTimeParameter()`。

> 说明：精确穿越时刻的「二分/插值」分两层——`StopCondition` 用三次样条插值（`NotAKnotInterpolator`）给出亚步长精度历元；上层 `Propagate::RefineFinalStep`/`BisectFinalStep`（`Propagate.cpp` L5970/L6427）再对最后一步做缩小步长/二分逼近。停止条件本身每步由 `Propagate::CheckStopConditions()`（`Propagate.cpp` L5163）查询。

#### StopConditionException.hpp —— 停止条件异常

**职责一句话**：停止条件异常，派生自 `BaseException`（`StopConditionException.hpp` L36）。

### 2.5 event/ —— 事件定位

> 注意：本目录的 `EventLocator` 是**蚀/接触类几何事件**（penumbra/umbra/contact）的定位器基类，与 `stopcond` 的停止条件穿越定位是两套独立机制——它按 `StepSize` 扫描 + `EphemManager`/SPICE 内核，`FindEvents()` 为纯虚（在 `EclipseLocator`/`ContactLocator` 等派生类实现，不在本目录）。

#### EventLocator.hpp / .cpp —— 事件定位器基类

**职责一句话**：确定某类事件（如蚀）发生时刻与持续时间的容器基类，依赖 SPICE 内核与航天器星历记录。

**关键类/函数**：

- `class EventLocator : public GmatBase`（`EventLocator.hpp` L64）。
- 参数（L249-265）：`Spacecraft/Filename/OccultingBodies/InputEpochFormat/InitialEpoch/StepSize/FinalEpoch/UseLightTimeDelay/UseStellarAberration/WriteReport/RunMode/UseEntireInterval`；`runMode` 枚举 `Automatic/Manual/Disabled`（`EventLocator.cpp` L104-109）。
- 默认值（`EventLocator.cpp` L140-155）：`useLightTimeDelay=true`、`useStellarAberration=true`、`stepSize=10.0`、`runMode="Automatic"`；`STEP_MULTIPLE=0.5`（L118，用于光时计算）。
- `LocateEvents()`（L1795-1934）：`sat->ProvideEphemerisData()` 停止记录并装载内核（L1824）→ `em->GetCoverage(...)` 取星历覆盖区间（L1829）→ 校验历元范围 → 调纯虚 `FindEvents()`（L1913）→ `ReportEventData()` 写报告（L1921-1929）。
- `Initialize()`（L1633-1749）：校验目标（航天器或星表区域）、NAIF ID 为负（L1688-1696）、光时/光行差约束（L1704-1711）；`runMode != "Disabled"` 时 `sat->RecordEphemerisData()` 开始记录（L1737-1741）。
- `GetAbcorrString()`（L2139-2151）：把光时/光行差开关映射成 CSPICE 的 `abcorr` 串（"NONE"/"CN"/"CN+S"）。
- `FindEvents() = 0`（`EventLocator.hpp` L287）：派生类实现具体事件判据与扫描。

#### LocatedEvent.hpp / .cpp —— 已定位事件

**职责一句话**：单个已定位事件的起止历元与时长容器。

- `class LocatedEvent`（`LocatedEvent.hpp` L41）；`GetDuration()/GetStart()/GetEnd()`（L52-54）、纯虚 `GetReportString()`（L58，派生类输出报告串）、`SetStart()/SetEnd()`（L62-63）。成员 `start/end/duration`（L67-73）。

#### EventException.hpp / .cpp —— 事件异常

**职责一句话**：事件定位子系统异常，派生自 `BaseException`（`EventException.hpp` L42）。

## 三、关键设计模式与数据流

### 3.1 继承体系

```
GmatBase
├── Propagator                          (传播器抽象：Step/RawStep/GetStepTaken = 0)
│   └── Integrator                      (积分器抽象：EstimateError/AdaptStep = 0)
│       ├── RungeKutta                  (RK 骨架：SetCoefficients = 0)
│       │   ├── RungeKutta89            (16 级 8(9))
│       │   ├── PrinceDormand45         (7 级 4(5))
│       │   ├── PrinceDormand78         (13 级 7(8))
│       │   ├── RungeKuttaFehlberg56    (8 级 5(6))
│       │   └── RungeKuttaNystrom       (RKN 骨架，二阶)
│       │       └── DormandElMikkawyPrince68  (9 级 6(8))
│       └── PredictorCorrector          (P-C 骨架：SetWeights/Predict/Correct = 0)
│           ├── AdamsBashforthMoulton   (4 阶 AB/AM)
│           └── Cowell                  (壳，未实现)
├── Burn                                (机动抽象：Fire = 0)
│   ├── ImpulsiveBurn
│   └── FiniteBurn
├── Attitude                            (姿态抽象：ComputeCosineMatrixAndAngularVelocity = 0)
│   ├── Kinematic                       (运动学中间层)
│   │   ├── CSFixed / Spinner / PrecessingSpinner
│   │   ├── NadirPointing / CommandableNadirPointing
│   │   └── ThreeAxisKinematic
│   ├── CCSDSAttitude
│   └── SpiceAttitude
├── StopCondition                       (停止条件，具体判据由参数类型内部特判)
├── EventLocator                        (事件定位器：FindEvents = 0)
└── (PropSetup / StateManager 等为配置/状态管理类)
```

### 3.2 工厂与克隆模式

- **积分器选择**：`PropSetup::SetPropagator` 接收 `Propagator*`，`ClonePropagator` 内部按具体类型 `Clone()`；默认工厂化构造在 `PropSetup` 构造函数中（`RungeKutta89` + `ODEModel` + `PointMassForce`）。
- **机动参考系工厂**：`ManeuverFrameManager::GetFrameInstance(frameType)` 按字符串返回 `InertialManeuverFrame`/`VnbManeuverFrame`。
- **停止条件插值器**：`StopCondition` 构造时若无外部插值器，则 `new NotAKnotInterpolator`（默认工厂）。
- **P-C 启动器**：`PredictorCorrector::Initialize` 中 `if (starter == NULL) starter = new RungeKutta89`，再 `SetPhysicalModel` 共享同一力模型。

### 3.3 传播主循环时序图（文字版）

以下为一次 `Propagate` 命令推进的完整调用链（`→` 表示调用；行号为真实源文件行号）：

```
Propagate::Execute / TakeAStep                (Propagate.cpp L4951)
  └─ propagator->Step()                        (Propagate.cpp L4976 / L5048)
      └─ RungeKutta::Step()                    (RungeKutta.cpp L304)
          ├─ physicalModel->GetForceMaxStep()  (RungeKutta.cpp L334；ODEModel.cpp L6504)
          │    └─ 各 PhysicalModel::GetForceMaxStep() 求和 → 力模型限制最大步长
          ├─ do {
          │     RawStep()                       (RungeKutta.cpp L506)
          │       └─ physicalModel->GetDerivatives(stageState, stepSize*ai[i])  (L560)
          │            └─ ODEModel::GetDerivatives()        (ODEModel.cpp L3107)
          │                 └─ 逐 ForceModel::GetDerivatives() 累加加速度（引力/阻力/光压/推力）
          │     EstimateError()                 (RungeKutta.cpp L679)
          │       └─ physicalModel->EstimateError(errorEstimates, candidateState)  (L693)
          │     AdaptStep(maxerror)             (RungeKutta.cpp L718)
          │       └─ stepSize = σ·h·(tol/err)^(1/(m-1 或 m))  (L750 / L761)
          │  } while (!goodStepTaken)
          └─ physicalModel->IncrementTime(stepTaken)         (RungeKutta.cpp L442)
  └─ CheckStopConditions(epochID)               (Propagate.cpp L4724 / L5163)
       └─ StopCondition::Evaluate()             (StopCondition.cpp L462)  ← 每步查询
            ├─ mStopParam->EvaluateReal()       (L509)
            └─ 检测 goal ∈ [prev, curr] → goalMet (L576-589)
  └─ 若触发 → TakeFinalStep / RefineFinalStep   (Propagate.cpp L4901 / L5970)
       └─ BisectFinalStep(stopper)              (Propagate.cpp L6427)  ← 二分逼近
            └─ StopCondition::AddToBuffer / GetStopEpoch (StopCondition.cpp L708 / L886)
                 └─ NotAKnotInterpolator::Interpolate(goal, &stopEpoch)  ← 样条插值
```

要点：
1. **积分器不直接查停止条件**——停止条件由 `Propagate` 命令在每步后统一查询（`CheckStopConditions`）。
2. **ODEModel 是加速度的叠加器**——`GetDerivatives` 把各 `PhysicalModel`（含有限推力的 `TransientForce`）贡献相加，写入 PSM 提供的状态向量。
3. **步长被两层限制**——`Integrator` 的 `minimumStep/maximumStep` 硬限 + 力模型 `GetForceMaxStep`（有限推力在步内开关时把步长截到机动边界）。
4. **精确穿越历元**由「停止条件的样条插值 + 命令层二分/缩小步长」联合确定。

### 3.4 关键数据流

- **状态向量数据流**：`PropagationStateManager.BuildState()` 组装 → `ODEModel.SetState(psm.GetState())` → 积分器 `inState/outState = physicalModel->GetState()` → 步进后 `UpdateSpaceObject()` 写回航天器。
- **姿态数据流**：`Spacecraft` 持 `Attitude` → 力模型（SRP/阻力）`GetCosineMatrix(epoch)` 取 Fi→Fb 的 DCM → 投影体轴面积/法向 → 得出正确截面合力。
- **推力数据流**：`FiniteBurn::Fire` 累计 `totalAccel/totalThrust` → 推力 `TransientForce` 在 `GetDerivatives` 中把 `totalAccel` 注入加速度 → 积分器推进。
- **脉冲 Δv 数据流**：`ImpulsiveBurn::Fire` `ConvertDeltaVToInertial` 旋转 → 直接加 `satState[3..5]`（瞬时速度跳变，不经积分）。

## 四、文件清单附录

### 4.1 src/base/propagator/（30 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| Propagator.hpp | 传播器抽象基类声明 | `Propagator`；纯虚 `Step/RawStep/GetStepTaken` |
| Propagator.cpp | 传播器抽象基类实现 | `Initialize/SetPhysicalModel/Step(dt)/FindTimeStep/SetNoiseStep/IsValidEpoch` |
| PropagationStateManager.hpp | PSM 声明 | `PropagationStateManager`；`BuildState/MapObjectsToVector/MapVectorToObjects` |
| PropagationStateManager.cpp | PSM 实现 | 状态组装/映射/协方差传播 |
| PropSetup.hpp | 传播配置容器声明 | `PropSetup`；`SetPropagator/SetODEModel/AddForce` |
| PropSetup.cpp | 传播配置容器实现 | 构造默认 RK89+ODEModel+PointMassForce；`PrepareInternals/Initialize` |
| PropSetupException.hpp | 传播配置异常 | `PropSetupException` |
| PropagatorException.hpp | 传播器异常 | `PropagatorException` |
| Integrator.hpp | 积分器抽象基类声明 | `Integrator`；纯虚 `EstimateError/AdaptStep` |
| Integrator.cpp | 积分器抽象基类实现 | 默认容差/步长参数；`SetPhysicalModel/GetStepTaken/UsesErrorControl` |
| RungeKutta.hpp | RK 基类声明 | `RungeKutta`；纯虚 `SetCoefficients` |
| RungeKutta.cpp | RK 基类实现 | `Step/RawStep/EstimateError/AdaptStep/SetupAccumulator` |
| RungeKutta89.hpp | RK8(9) 声明 | `RungeKutta89` |
| RungeKutta89.cpp | RK8(9) 实现 | `SetCoefficients`（16 级 Verner 1978 系数） |
| PrinceDormand45.hpp | RK4(5) 声明 | `PrinceDormand45` |
| PrinceDormand45.cpp | RK4(5) 实现 | `SetCoefficients`（7 级 Prince&Dormand 1981） |
| PrinceDormand78.hpp | RK7(8) 声明 | `PrinceDormand78` |
| PrinceDormand78.cpp | RK7(8) 实现 | `SetCoefficients`（13 级，cj/cjhat 差得 ee） |
| RungeKuttaFehlberg56.hpp | RK5(6) 声明 | `RungeKuttaFehlberg56` |
| RungeKuttaFehlberg56.cpp | RK5(6) 实现 | `SetCoefficients`（Fehlberg 系数） |
| RungeKuttaNystrom.hpp | RKN 基类声明 | `RungeKuttaNystrom`；`cdotj/derivativeMap/eeDeriv` |
| RungeKuttaNystrom.cpp | RKN 基类实现 | `GetComponentMap`；二阶 `RawStep/EstimateError` |
| DormandElMikkawyPrince68.hpp | RKN6(8) 声明 | `DormandElMikkawyPrince68` |
| DormandElMikkawyPrince68.cpp | RKN6(8) 实现 | `SetCoefficients`（9 级 DEP 1987） |
| PredictorCorrector.hpp | P-C 基类声明 | `PredictorCorrector`；纯虚 `SetWeights/Predict/Correct/Reset` |
| PredictorCorrector.cpp | P-C 基类实现 | `Initialize/Step/Predict/Correct/BufferHistory` |
| AdamsBashforthMoulton.hpp | ABM 声明 | `AdamsBashforthMoulton` |
| AdamsBashforthMoulton.cpp | ABM 实现 | `SetWeights/Predict/Correct/EstimateError/Reset` |
| Cowell.hpp | Cowell 壳声明 | `Cowell`（未实现） |
| Cowell.cpp | Cowell 壳实现 | 空转 `Step/RawStep/AdaptStep` |

### 4.2 src/base/burn/（16 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| Burn.hpp | 机动基类声明 | `Burn`；纯虚 `Fire`；`ConvertDeltaVToInertial` |
| Burn.cpp | 机动基类实现 | Δv 惯性转换、坐标系/参考系处理 |
| BurnException.hpp | 机动异常声明 | `BurnException` |
| BurnException.cpp | 机动异常实现 | — |
| ImpulsiveBurn.hpp | 脉冲机动声明 | `ImpulsiveBurn`；`isp/gravityAccel/decrementMass` |
| ImpulsiveBurn.cpp | 脉冲机动实现 | `Fire`（瞬时 Δv + 反向迭代）；`TransformDeltaVToJ2kFrame` |
| FiniteBurn.hpp | 有限推力声明 | `FiniteBurn`；`thrusterNames/ComputeThrottleLogic` |
| FiniteBurn.cpp | 有限推力实现 | `Fire`（累计推力/质量流率）；`SetThrustersFromSpacecraft` |
| ManeuverFrame.hpp | 机动参考系基类 | `ManeuverFrame`；纯虚 `CalculateBasis` |
| ManeuverFrame.cpp | 机动参考系基类实现 | `SetState/CalculateBasis(basis)` |
| ManeuverFrameManager.hpp | 机动参考系管理器 | `ManeuverFrameManager`；`GetFrameInstance` |
| ManeuverFrameManager.cpp | 机动参考系管理器实现 | 帧工厂 |
| InertialManeuverFrame.hpp | 惯性机动系声明 | `InertialManeuverFrame` |
| InertialManeuverFrame.cpp | 惯性机动系实现 | `CalculateBasis`（单位阵） |
| VnbManeuverFrame.hpp | VNB 机动系声明 | `VnbManeuverFrame` |
| VnbManeuverFrame.cpp | VNB 机动系实现 | `CalculateBasis`（V=v, N=r×v, B=v×n） |

### 4.3 src/base/attitude/（22 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| Attitude.hpp | 姿态基类声明 | `Attitude`；纯虚 `ComputeCosineMatrixAndAngularVelocity` |
| Attitude.cpp | 姿态基类实现 | `Initialize/GetCosineMatrix/GetRotationMatrix` |
| AttitudeException.hpp | 姿态异常声明 | `AttitudeException` |
| AttitudeException.cpp | 姿态异常实现 | — |
| Kinematic.hpp | 运动学姿态中间层 | `Kinematic` |
| Kinematic.cpp | 运动学姿态中间层实现 | — |
| CSFixed.hpp | 坐标系固定姿态声明 | `CSFixed` |
| CSFixed.cpp | 坐标系固定姿态实现 | `ComputeCosineMatrixAndAngularVelocity`（DCM 恒定） |
| Spinner.hpp | 自旋姿态声明 | `Spinner`；`RB0I/initialwMag/initialeAxis` |
| Spinner.cpp | 自旋姿态实现 | `ComputeCosineMatrixAndAngularVelocity`（EulerAxisAndAngleToDCM） |
| PrecessingSpinner.hpp | 进动自旋声明 | `PrecessingSpinner` |
| PrecessingSpinner.cpp | 进动自旋实现 | `ComputeCosineMatrixAndAngularVelocity` |
| NadirPointing.hpp | 对地指向声明 | `NadirPointing`；`TRIAD` |
| NadirPointing.cpp | 对地指向实现 | `ComputeCosineMatrixAndAngularVelocity`（TRIAD 定姿） |
| CommandableNadirPointing.hpp | 命令可设对地指向 | `CommandableNadirPointing` |
| CommandableNadirPointing.cpp | 命令可设对地指向实现 | 覆写 `GetCosineMatrix/SetRvectorParameter` |
| ThreeAxisKinematic.hpp | 三轴运动学声明 | `ThreeAxisKinematic`；`Omega`（4×4 斜对称） |
| ThreeAxisKinematic.cpp | 三轴运动学实现 | 四元数传播 |
| CCSDSAttitude.hpp | CCSDS-AEM 姿态声明 | `CCSDSAttitude`；`CCSDSAEMReader` |
| CCSDSAttitude.cpp | CCSDS-AEM 姿态实现 | 读 AEM 文件 |
| SpiceAttitude.hpp | SPICE CK 姿态声明 | `SpiceAttitude`；`SpiceAttitudeKernelReader` |
| SpiceAttitude.cpp | SPICE CK 姿态实现 | 读 CK/SCLK/FK 内核 |

### 4.4 src/base/stopcond/（3 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| StopCondition.hpp | 停止条件基类声明 | `StopCondition`；`Evaluate/AddToBuffer/GetStopEpoch` |
| StopCondition.cpp | 停止条件基类实现 | `Evaluate/AddToBuffer/GetStopEpoch/CheckOnPeriapsis/CheckOnApoapsis/CheckCyclicCondition` |
| StopConditionException.hpp | 停止条件异常 | `StopConditionException` |

### 4.5 src/base/event/（6 文件）

| 相对路径 | 职责 | 关键类/函数 |
| --- | --- | --- |
| EventLocator.hpp | 事件定位器基类声明 | `EventLocator`；纯虚 `FindEvents` |
| EventLocator.cpp | 事件定位器基类实现 | `Initialize/LocateEvents/GetAbcorrString` |
| LocatedEvent.hpp | 已定位事件声明 | `LocatedEvent`；`GetDuration/GetStart/GetEnd` |
| LocatedEvent.cpp | 已定位事件实现 | 起止历元/时长 |
| EventException.hpp | 事件异常声明 | `EventException` |
| EventException.cpp | 事件异常实现 | — |
