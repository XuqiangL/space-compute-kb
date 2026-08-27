# 第11章 打靶求解器与优化器数学

> 本章范围：`src/base/solver/`（Solver 基类、DifferentialCorrector、Optimizer 家族、DerivativeModel/Gradient/Jacobian 差分工具、LineSearch）、`plugins/FminconOptimizerPlugin`（MATLAB fmincon SQP 接口）、`plugins/YukonOptimizerPlugin`（Yukonad 状态机 + Yukon SQP 主循环 + MinQP）、以及 VF13ad 外部求解器的集成点（源码不在本仓库，见 11.12 的说明）。
>
> 术语与类结构沿用 [第8章](../CH08-base-subsystems.md)（8.3 求解器家族）、[第13章](../CH13-plugins-a.md)（FminconOptimizerPlugin）、[第14章](../CH14-plugins-b.md)（14.13 YukonOptimizerPlugin）。本章只讲公式与数值算法，类结构、工厂与插件装载机制见对应架构章，不重复。
>
> 仓库：L:\gmat888（main，commit ce6eba2）。所有行号均经 read 工具核实。
>
> **版本说明**：本仓库中旧的 `Targeter` 与 `BoundaryValueSolver` 两个类已合并进 `DifferentialCorrector`——构造函数把 `"BoundaryValueSolver"` 同时注册为对象类型名（`DifferentialCorrector.cpp:114`），`SolverFactory` 也只创建 `"DifferentialCorrector"`（`SolverFactory.cpp:87-88`）。本章按当前结构编写，行文中"打靶器（Targeter）"即指 `DifferentialCorrector`。

## 11.0 求解器体系总览

GMAT 的求解器全部继承自 `Solver`（`Solver.hpp:57`），按用途分两支：

```
Solver (状态机 + 变量/结果双通道, src/base/solver/Solver.hpp)
├── DifferentialCorrector   打靶求解器（Newton-Raphson / Broyden / ModifiedBroyden）
└── Optimizer (纯虚 Optimize()=0)
    ├── InternalOptimizer   内嵌优化器接口
    │   └── Yukonad (插件)  梯度法/SQP 状态机适配器 → Yukon SQP 主循环
    └── ExternalOptimizer   外部优化器接口（MATLAB 服务器）
        └── FminconOptimizer (插件)  MATLAB fmincon active-set (SQP)
    （VF13ad 亦为 ExternalOptimizer 分支插件，源码未随仓库发布）
```

数值工具：`DerivativeModel`（差分模式基类）→ `Gradient`（目标梯度差分）/ `Jacobian`（约束雅可比差分），供 Yukonad 使用；`DifferentialCorrector` 自己实现了一套差分与求逆逻辑（`CalculateJacobian`/`InvertJacobian`）。`LineSearch` 是未实现的占位类。

## 11.1 Solver 基类：状态机与「变量/目标」双通道

### 条目名
Solver 基类状态机（SolverState/MachineMode/ExitMode）与变量-结果数据通道

### 公式
状态机不是数值公式，但定义了所有求解器迭代的外层驱动。核心映射：

$$
\texttt{AdvanceState}:\ \texttt{currentState} \mapsto
\begin{cases}
\texttt{INITIALIZING}\to\texttt{CompleteInitialization()}\\
\texttt{NOMINAL}\to\texttt{RunNominal()}\\
\texttt{PERTURBING}\to\texttt{RunPerturbation()}\\
\texttt{ITERATING}\to\texttt{RunIteration()}\\
\texttt{CALCULATING}\to\texttt{CalculateParameters()}\\
\texttt{CHECKINGRUN}\to\texttt{CheckCompletion()}\\
\texttt{RUNEXTERNAL}\to\texttt{RunExternal()}\\
\texttt{FINISHED}\to\texttt{RunComplete()}
\end{cases}
$$

变量缩放（Vary 命令写入，架构文档 Eq. 13.5，实现在 `Vary.cpp:1510-1517`）：

$$
x_{\text{scaled}} = \frac{x_{\text{unscaled}} + a_f}{m_f},\qquad
h_{\text{scaled}} = \frac{h_{\text{unscaled}}}{m_f},\qquad
\text{bounds/step 同样除以 } m_f
$$

其中 $a_f$=additiveScaleFactor、$m_f$=multiplicativeScaleFactor；反向取回（`Vary.cpp:1543-1545`）：$x_{\text{unscaled}} = x_{\text{scaled}}/m_f - a_f$。

### 代码位置
- `src/base/solver/Solver.hpp:61-78`（SolverState 枚举）、`:91-97`（MachineMode）、`:100-106`（ExitMode）
- `src/base/solver/Solver.cpp:657-700`（AdvanceState 分派）、`:1409-1426`（CompleteInitialization）、`:1545-1548`（ResetVariables）、`:130-131/344`（默认 maxIterations=25、perturbation=1e-4）
- `src/base/solver/Solver.cpp:405-459`（SetSolverVariables，数据数组 data[0..5]）、`:947-959`（SetIntegerParameter 校验 maxIterations>0）
- `src/base/command/Vary.cpp:1510-1517`、`:1543-1545`（变量缩放/反缩放）

### 深度讲解
**背景。** `Solver` 把"打靶/优化/扫描"共有的迭代骨架抽成状态机：外层命令序列（`Target`/`Optimize` 分支命令）每步调用一次 `AdvanceState()`，求解器推进一个状态并返回；命令解释器按状态决定"这次该跑名义轨道还是扰动轨道"。这样数值迭代（差分求导、矩阵求逆、更新变量）与任务传播解耦——传播永远发生在命令序列里，求解器只负责发号施令与收集结果。

**实现细节。** 关键代码（`Solver.cpp:657-700` 节选）：

```cpp
Solver::SolverState Solver::AdvanceState()
{
   switch (currentState) {
      case INITIALIZING:  CompleteInitialization(); break;   // 打开报告文件、复位变量
      case NOMINAL:       RunNominal();                      // 名义运行：跑整条控制序列
                         status = Gmat::RUN; break;
      case PERTURBING:    RunPerturbation(); break;          // 扰动运行：逐变量加/减 h
      case ITERATING:     RunIteration(); break;             // 迭代运行（打靶器不用）
      case CALCULATING:   CalculateParameters(); break;      // 差分建 Jacobian、求逆、更新变量
      case CHECKINGRUN:   CheckCompletion(); break;          // 收敛判定
      case RUNEXTERNAL:   RunExternal(); break;              // 外部优化器（fmincon/VF13ad）
      case FINISHED:      RunComplete(); break;
      default: throw SolverException("Undefined Solver state");
   };
   ReportProgress();                                          // 向 ISolverListener 派发进度
   return currentState;
}
```

逐行注释：每个 case 调用一个虚函数（默认实现只做 `currentState+1` 推进，`Solver.cpp:1438-1534`），派生类重写后填入真实算法；`ReportProgress()`（`Solver.cpp:1337-1350`）把进度字符串推给消息系统，另有按 `ISolverListener` 列表的重载（`Solver.cpp:1361-1381`）供 GUI 订阅变量/约束变化。

**与 Vary/Achieve 命令的耦合（数据通道）。** 变量的 6 元组数据经 `SetSolverVariables`（`Solver.cpp:405-459`）写入：

```cpp
variable.at(variableCount)           = data[0];   // 缩放后变量值 x_scaled
variableInitialValues.at(variableCount) = data[0]; // 初始值（用于 ResetVariables）
perturbation.at(variableCount)       = data[1];   // 缩放后差分步长 h_scaled
variableMinimum.at(variableCount)    = data[2];   // 缩放后下界
variableMaximum.at(variableCount)    = data[3];   // 缩放后上界
variableMaximumStep.at(variableCount)= data[4];   // 缩放后单步最大允许步长
unscaledVariable.at(variableCount)   = data[5];   // 未缩放初始值（仅报告用）
```

默认值（`Solver.cpp:339-346`）：min=−9.999e300、max=+9.999e300、maxStep=9.999e300、perturbation=1e-4、pertDirection=1。`RefreshSolverVariables`（`Solver.cpp:479-547`）在 `SaveAndContinue` 模式下允许脚本里 Variable 更新回写。`ResetVariables`（`Solver.cpp:1545-1548`）把 `variable` 复位为初始值，用于 DiscardAndContinue 退出模式（`CompleteInitialization`，`Solver.cpp:1417-1425`）。

**参数表（Solver 层真实参数名）。**

| 脚本参数 | ID（Solver.hpp:334-353） | 类型 | 默认 | 校验 |
|---|---|---|---|---|
| `MaximumIterations` | maxIterationsID | Integer | 25（Solver.cpp:130） | >0（Solver.cpp:952） |
| `ShowProgress` | ShowProgressID | Boolean | true | — |
| `ReportStyle` | ReportStyle | 枚举 | Normal | Normal/Concise/Verbose/Debug（Solver.cpp:1157-1172） |
| `ReportFile` | solverTextFileID | 文件名 | `<type><name>.data`（Solver.cpp:155-157） | 合法文件名（Solver.cpp:1178） |
| `Variables` | variableNamesID | StringArray | — | 由 Vary 填充 |
| `SolverMode` | SolverModeID | 字符串 | — | Solve/RunInitialGuess/RunCorrected（Solver.cpp:1192-1202） |
| `ExitMode` | ExitModeID | 字符串 | DiscardAndContinue | DiscardAndContinue/SaveAndContinue/Stop（Solver.cpp:1213-1222） |

**收敛状态机。** Solver 层只定义状态，收敛判定在各派生类的 `CheckCompletion()` 中实现（见 11.2 的 DC 版本与 11.8 的 Optimizer 版本）。`MachineMode`（INITIAL_GUESS/SOLVE/RUN_CORRECTED，`Solver.hpp:91-97`）与 `ExitMode`（DISCARD/RETAIN/HALT，`Solver.hpp:100-106`）决定循环结束后变量是保留、丢弃还是停机。

## 11.2 DifferentialCorrector：状态机、扰动差分与收敛判定

### 条目名
打靶器状态机（NOMINAL→PERTURBING→CALCULATING→CHECKINGRUN）与收敛判定

### 公式
收敛判据（每个目标独立检查，`DifferentialCorrector.cpp:1365-1369`）：

$$
\text{converged} \iff \left|y_i^{\text{nominal}} - y_i^{\text{goal}}\right| \le \varepsilon_i,\quad \forall i=1..m
$$

其中 $y^{\text{nominal}}$ 为名义运行的达到值、$y^{\text{goal}}$ 为 Achieve 命令设定的目标值、$\varepsilon_i$ 为各目标容差。不收敛且 `iterationsTaken < maxIterations-1` 时进入扰动状态；超限则 `FINISHED + status=EXCEEDED_ITERATIONS`（`DifferentialCorrector.cpp:1371-1391`）。

差分扰动模式（`diffMode`，`DifferentialCorrector.cpp:1043-1071`）：

$$
\text{diffMode}=1:\ x_j^{+}=x_j+h_j;\quad
\text{diffMode}=0:\ x_j^{+}=x_j+h_j,\ x_j^{-}=x_j-h_j;\quad
\text{diffMode}=-1:\ x_j^{-}=x_j-h_j
$$

越界反射（`DifferentialCorrector.cpp:1073-1105`）：对前向/后向差分，若 $x_j\pm h_j$ 越过 $[x_{\min},x_{\max}]$，则改向扰动 $x_j \mp 2h_j$ 且 `pertDirection=-1`；中心差分违反界时只发警告继续扰（为保证中心差分成对）。

### 代码位置
- `src/base/solver/DifferentialCorrector.hpp:121-154`（goal/tolerance/nominal/achieved/backAchieved/jacobian/inverseJacobian/diffMode/firstPert/incrementPert）
- `src/base/solver/DifferentialCorrector.cpp:853-1001`（AdvanceState）、`:1011-1016`（RunNominal）、`:1026-1108`（RunPerturbation）、`:1359-1400`（CheckCompletion）、`:661-671`（SetSolverResults）、`:738-769`（SetResultValue）
- `src/base/solver/DifferentialCorrector.cpp:492-524`（DerivativeMethod 枚举映射 ForwardDifference/CentralDifference/BackwardDifference → diffMode 1/0/−1）

### 深度讲解
**背景。** 打靶（shooting）的思想：把边值问题（BVP）转化为初值问题（IVP）+ 参数寻根。GMAT 的 `DifferentialCorrector` 中，变量 $x\in\mathbb{R}^n$ 由 `Vary` 命令声明，目标 $y\in\mathbb{R}^m$ 由 `Achieve` 命令声明（含目标值 $y^{\text{goal}}$ 与容差 $\varepsilon$）。每轮迭代需要一次名义运行 + $n$ 次（前向）或 $2n$ 次（中心）扰动运行，因此一次 Newton 迭代的成本是 $(1+n)$ 或 $(1+2n)$ 次完整轨道传播。

**实现细节（扰动调度，`DifferentialCorrector.cpp:1029-1107` 节选）：**

```cpp
if (pertNumber != -1)
   variable.at(pertNumber) = lastUnperturbedValue;   // 先撤销上一个扰动
if (incrementPert) ++pertNumber;                      // 中心差分两拍：正扰、负扰

if (pertNumber == variableCount) {                    // n 个变量全部扰动完毕
   currentState = CALCULATING;  pertNumber = -1;  return;
}

lastUnperturbedValue = variable.at(pertNumber);
if (diffMode == 1) {                                  // 前向差分
   firstPert = true;
   variable.at(pertNumber) += perturbation.at(pertNumber);   // x_j += h_j
   pertDirection.at(pertNumber) = 1.0;
}
else if (diffMode == 0) {                             // 中心差分：正/负两拍
   if (incrementPert) { firstPert = true;  incrementPert = false;
      variable.at(pertNumber) += perturbation.at(pertNumber); }  // 第一拍 +
   else { firstPert = false; incrementPert = true;
      variable.at(pertNumber) -= perturbation.at(pertNumber); }  // 第二拍 -
}
```

逐行注释：`firstPert` 决定 `SetResultValue` 把达到值写入 `achieved[pert][j]`（正扰）还是 `backAchieved[pert][j]`（负扰），见 `DifferentialCorrector.cpp:762-768`；`pertNumber==variableCount` 表示一轮扰动结束，转入 CALCULATING。

**收敛状态机（CheckCompletion，`DifferentialCorrector.cpp:1359-1400`）：**

```
CHECKINGRUN
   ├─ ∀i: |nominal[i]-goal[i]| ≤ tol[i] ──► FINISHED (status=CONVERGED)
   ├─ 未收敛 ∧ iterationsTaken < maxIterations-1 ──► PERTURBING（skipPerts 时直接 CALCULATING）
   └─ 未收敛 ∧ 达到上限 ──► FINISHED (status=EXCEEDED_ITERATIONS)
```

`skipPerts` 标志（`DifferentialCorrector.hpp:119`）供 Broyden/ModifiedBroyden 使用：首次迭代建完雅可比后，后续迭代直接用割线更新，跳过扰动运行（见 11.5/11.6）。`iterationsTaken` 在 CHECKINGRUN 状态入口自增并与 `maxIterations` 比较（`DifferentialCorrector.cpp:968-976`）。

**与 Achieve 命令的耦合。** `SetSolverResults(goalData, name)`（`DifferentialCorrector.cpp:661-671`）写入 `goal[goalCount]=data[0]`（目标值）、`tolerance[goalCount]=data[1]`（容差）；每次名义运行中 `Achieve` 命令执行 `SetResultValue(id, val)`（`DifferentialCorrector.cpp:738-769`）把达到值写入 `nominal[id]`（NOMINAL 态）或 `achieved/backAchieved`（PERTURBING 态），NaN/Inf 达到值直接抛 `SolverException`（`:748-755`）。浮点端点在名义运行中可用 `UpdateSolverGoal/UpdateSolverTolerance`（`:686-725`，仅 NOMINAL 态生效）动态改目标/容差。

**参数表。**

| 脚本参数 | 位置 | 默认 | 合法值 |
|---|---|---|---|
| `Algorithm` | DifferentialCorrector.cpp:526-557 | NewtonRaphson（构造 :88） | NewtonRaphson / Broyden / ModifiedBroyden |
| `DerivativeMethod` | DifferentialCorrector.cpp:492-524 | ForwardDifference（构造 :105） | ForwardDifference / CentralDifference / BackwardDifference（旧名 `UseCentralDifferences` 已废弃，`:269-279`） |
| `Goals` | DifferentialCorrector.cpp:486-490 | — | 由 Achieve 填充 |
| `MaximumIterations` | Solver（11.1） | 25 | >0 |

## 11.3 数值雅可比（差分）公式与雅可比求逆

### 条目名
DifferentialCorrector 的数值雅可比（前向/中心/后向差分）与求逆（Inverse/Pseudoinverse）

### 公式
前向/后向差分（`DifferentialCorrector.cpp:1543-1553`）：

$$
J_{ij} = \frac{\partial y_j}{\partial x_i} \approx
\frac{y_j(x_i + p_i^{+}) - y_j^{\text{nominal}}}{p_i^{+} d_i},\qquad
p_i^{+} = p_i,\ d_i=\texttt{pertDirection}_i\in\{+1,-1\}
$$

中心差分（`DifferentialCorrector.cpp:1555-1563`）：

$$
J_{ij} \approx \frac{y_j(x_i+p_i) - y_j(x_i-p_i)}{2p_i}
$$

矩阵按「变量 × 目标」排布（`jacobian[i][j]`，i=变量、j=目标），与常规约定转置（注释见 `DifferentialCorrector.cpp:1117-1124`）。求逆（`DifferentialCorrector.cpp:1596-1599`）：

$$
J_{\text{inv}} =
\begin{cases}
J^{-1} & n = m \quad (\texttt{Inverse})\\
J^{+}  & n \ne m \quad (\texttt{Pseudoinverse})
\end{cases}
$$

修正量（11.4 节）：$\Delta x_i = \sum_j J_{\text{inv},ji}\,(y_j^{\text{goal}}-y_j^{\text{nominal}})$。

### 代码位置
- `src/base/solver/DifferentialCorrector.cpp:1539-1565`（CalculateJacobian）
- `src/base/solver/DifferentialCorrector.cpp:1576-1633`（InvertJacobian）
- `src/gmatutil/util/Rmatrix.cpp:1097`（Inverse，Gauss-Jordan 全选主元）、`:1425`（Pseudoinverse）

### 深度讲解
**背景。** 差分步长 $p_i$ 由 Vary 命令的 `Perturbation` 字段给出（经缩放，11.1 节），默认 1e-4（`Solver.cpp:344`）。数值微分的截断误差：前向差分 $O(p)$、中心差分 $O(p^2)$，但中心差分每列多一次传播。当目标函数有噪声（数值积分器截断误差、事件定位离散）时，$p$ 过小会被舍入误差淹没——这是打靶问题雅可比"病态"的主要来源：$J$ 奇异时 `Inverse()` 抛异常，GMAT 将其包装为 SolverException 提示「Vary 变量不影响 Achieve 目标」（`DifferentialCorrector.cpp:1601-1606`）。

**实现细节（CalculateJacobian，`DifferentialCorrector.cpp:1543-1564` 节选）：**

```cpp
if (diffMode != 0) {                      // 前向或后向差分共用同一公式
   for (i = 0; i < variableCount; ++i)
      for (j = 0; j < goalCount; ++j) {
         jacobian[i][j] = achieved[i][j] - nominal[j];          // 扰动达到值 − 名义值
         jacobian[i][j] /= (pertDirection.at(i) * perturbation.at(i)); // 除以带符号步长
      }
}
else {                                    // 中心差分
   for (i = 0; i < variableCount; ++i)
      for (j = 0; j < goalCount; ++j) {
         jacobian[i][j] = achieved[i][j] - backAchieved[i][j];  // 正扰 − 负扰
         jacobian[i][j] /= (2.0 * perturbation.at(i));          // 除以 2h
      }
}
```

逐行注释：后向差分时扰动方向为 −h 且 `pertDirection=-1`，公式分子仍为「扰动 − 名义」，除以 `d·h` 后符号自动正确（等价于 $(y^{\text{nominal}}-y^{-})/h$）；越界反射（11.2 节）会改 `pertDirection`，同样被该公式吸收。

**实现细节（InvertJacobian，`DifferentialCorrector.cpp:1582-1599` 节选）：**

```cpp
Rmatrix jac(variableCount, goalCount);
for (i = 0; i < variableCount; ++i)
   for (j = 0; j < goalCount; ++j) jac(i,j) = jacobian[i][j];  // C 数组 → Rmatrix

Rmatrix inv;
try {
   if (variableCount == goalCount)
      inv = jac.Inverse();              // 方阵：Gauss-Jordan 全选主元求逆
   else
      inv = jac.Pseudoinverse();        // 矩形（变量≠目标）：伪逆
} catch (BaseException &ex) {
   throw SolverException("Error inverting the Differential Corrector "
         "Jacobian; it appears that the variables in the Vary command(s) do "
         "not affect the target parameters in the Achieve command(s)");
}
```

逐行注释：方阵情形用 `Rmatrix::Inverse()`（`Rmatrix.cpp:1097` 起，全选主元 Gauss-Jordan；无参版本内部以零值阈值 1e-12 调用带参版本，`Rmatrix.cpp:1234-1237`）；$n\ne m$ 情形用 `Pseudoinverse()`（`Rmatrix.cpp:1425`，零值阈值默认 1e-12，`Rmatrix.hpp:131`）。奇异/病态导致求逆异常时，错误消息明确指向「Vary 与 Achieve 不匹配」这一最常见原因。逆矩阵按「目标 × 变量」排布（`inverseJacobian[j][i]`，j=目标、i=变量，`DifferentialCorrector.cpp:1623-1632`）。

**数值特性。** 打靶雅可比是"黑箱有限差分"：无解析导数、无切比雪夫/STT 伴随传播，代价是 $n$~$2n$ 次额外传播。病态判据：$\kappa(J)$ 大时，`Inverse` 的舍入误差被放大，导致修正量振荡——此时应改用 Broyden（减少扰动次数）或减小 `Perturbation`/增大 `MaximumIterations`。矩阵求逆的数值细节见 [第8章](../CH08-base-subsystems.md) 8.3.2 与线性代数工具章节（MD-06 规划中）。

## 11.4 Newton-Raphson 更新与步长阻尼（multiplier）

### 条目名
Newton-Raphson 修正：$\Delta x = J^{-1}(y^{\text{goal}}-y^{\text{nominal}})$ 与 MaxStep 阻尼、界截断

### 公式
牛顿迭代（`DifferentialCorrector.cpp:1294-1300`）：

$$
x_{k+1} = x_k + \Delta x,\qquad
\Delta x_i = \sum_{j=1}^{m} \left[J^{-1}\right]_{ji}\left(y_j^{\text{goal}} - y_j^{\text{nominal}}\right)
$$

阻尼（`DifferentialCorrector.cpp:1302-1313`）：

$$
\lambda = \min\left\{1,\ \min_{i:\,|\Delta x_i|>s_i^{\max}}\left|\frac{s_i^{\max}}{\Delta x_i}\right|\right\},\qquad
x_{k+1,i} = x_k + \lambda\,\Delta x_i
$$

其中 $s_i^{\max}=\texttt{variableMaximumStep}_i$（Vary 命令 `MaxStep` 字段）。界截断（`DifferentialCorrector.cpp:1335-1339`）：

$$
x_{k+1,i} \leftarrow \operatorname{clamp}(x_{k+1,i},\ x_i^{\min},\ x_i^{\max})
$$

### 代码位置
- `src/base/solver/DifferentialCorrector.cpp:1126-1138`（dcTypeId==1 分支：CalculateJacobian + InvertJacobian）
- `src/base/solver/DifferentialCorrector.cpp:1292-1349`（delta 组装、multiplier 阻尼、变量更新与截断）

### 深度讲解
**背景。** 打靶问题即求 $F(x)=y^{\text{nominal}}(x)-y^{\text{goal}}=0$ 的根。牛顿法 $x_{k+1}=x_k-J^{-1}F$ 在本代码中写成「先求逆再乘残差」的形式（`delta[i] += inverseJacobian[j][i]*(goal[j]-nominal[j])`），而不是解线性方程组 $J\,\Delta x = -F$。对 $n=m$ 两者数学等价，但解线性方程组在数值上更稳（避免显式求逆）；GMAT 选择显式求逆是为了同时支持 $n\ne m$ 的伪逆情形，并便于把逆矩阵写入报告文件（`DifferentialCorrector.cpp:2073-2081`）。

**实现细节（阻尼与更新，`DifferentialCorrector.cpp:1292-1345` 节选）：**

```cpp
std::vector<Real> delta;
for (i = 0; i < variableCount; ++i) {
   delta.push_back(0.0);
   for (j = 0; j < goalCount; j++)
      delta[i] += inverseJacobian[j][i] * (goal[j] - nominal[j]);  // Δx = J⁻¹(goal−nominal)
}

Real multiplier = 1.0, maxDelta;
for (i = 0; i < variableCount; ++i) {
   if (fabs(delta.at(i)) > variableMaximumStep.at(i)) {            // 有分量超过 MaxStep
      maxDelta = fabs(variableMaximumStep.at(i) / delta.at(i));    // 该分量的允许比例
      if (maxDelta < multiplier) multiplier = maxDelta;            // 取全局最小比例
   }
}

for (i = 0; i < variableCount; ++i) {
   variable.at(i) += delta.at(i) * multiplier;                     // x += λ·Δx
   if (variable.at(i) < variableMinimum.at(i))                     // 界截断
      variable.at(i) = variableMinimum.at(i);
   if (variable.at(i) > variableMaximum.at(i))
      variable.at(i) = variableMaximum.at(i);
}
currentState = NOMINAL;                                            // 进入下一轮名义运行
```

逐行注释：$\lambda$ 是**统一缩放的阻尼系数**——只要任一分量越出 `MaxStep`，整步按最紧比例收缩，保证方向不变（纯阻尼，不做 Armijo 线搜索）；截断到界是硬性投影，投影后残差与雅可比不再一致，下轮 Newton 步会补偿。这就是 GMAT 打靶器唯一的"线搜索"机制，`LineSearch` 类（11.7 节）在打靶路径中并未使用。

**参数表。** `MaximumIterations`（Solver 层，默认 25）、`Perturbation`（Vary，默认 1e-4）、`MaxStep`（Vary，默认 9.999e300 即不限）、`Lower`/`Upper`（Vary，默认 ±9.999e300）。

**收敛状态机。** Newton-Raphson 每轮都要差分建 $J$ 并求逆（`DifferentialCorrector.cpp:1134-1138`），即每轮 $1+n$（或 $1+2n$）次传播；`skipPerts=false` 保持。收敛判定见 11.2。

## 11.5 Broyden 割线更新（雅可比秩一修正）

### 条目名
Broyden 更新：$J_{k+1}=J_k+\dfrac{(y-\bar y-J_k s)\,s^{T}}{s^{T}s}$

### 公式
记 $s = x_k - x_{k-1}$（`savedVariable` 为上一轮变量）、$y = y_k^{\text{nominal}} - y_{k-1}^{\text{nominal}}$（`savedNominal` 为上一轮名义值）。秩一更新（`DifferentialCorrector.cpp:1163-1183`）：

$$
J_{k+1} = J_k + \frac{\left(y - J_k\,s\right)s^{T}}{s^{T}s}
$$

按代码的「变量×目标」索引逐元素写为：

$$
\left[J_{k+1}\right]_{ji} = \left[J_k\right]_{ji} +
\frac{\left(y_i - \sum_j \left[J_k\right]_{ji} s_j\right) s_j}{s^{T}s}
$$

首次迭代（`iterationsTaken==1`）仍用差分建 $J_0$ 并求逆，随后置 `skipPerts=true`（`DifferentialCorrector.cpp:1142-1147`），后续迭代不再扰动运行。

### 代码位置
- `src/base/solver/DifferentialCorrector.cpp:1140-1187`（dcTypeId==2 分支）
- `src/base/solver/DifferentialCorrector.cpp:1254-1290`（savedNominal/savedVariable/savedJacobian 保存）

### 深度讲解
**背景。** Broyden 是牛顿法的割线化：用相邻两次迭代的「变量差 $s$」与「残差差 $y$」构造满足割线方程 $J_{k+1}s=y$ 的秩一修正，避免每轮 $n$ 次扰动传播，代价是 $J$ 只在一阶精度上逼近真导数。收敛超线性（$q$ 阶介于 1 与 2 之间）。**存储**：GMAT 的实现保存整个 $J_k$（`savedJacobian`，$n\times m$ 稠密矩阵），更新后**重新求逆**（`InvertJacobian()`，`:1185`）——这是"Broyden 更新 $J$、但每次仍求逆"的变体，与经典的"逆 Broyden 更新 $J^{-1}$"（ModifiedBroyden，11.6 节）不同：经典逆更新省去每轮求逆，但秩一修正传播到逆矩阵。

**实现细节（`DifferentialCorrector.cpp:1155-1186` 节选）：**

```cpp
std::vector<Real> s, y, numerator;
s.resize(variableCount);  y.resize(goalCount);  numerator.resize(goalCount);

Real denom = 0.0;
for (i = 0; i < variableCount; ++i) {
   s[i] = variable[i] - savedVariable[i];      // s = x_k − x_{k−1}
   denom += s[i] * s[i];                        // denom = sᵀs
}
for (j = 0; j < goalCount; ++j)
   y[j] = nominal[j] - savedNominal[j];         // y = 残差差（名义值差）

for (i = 0; i < goalCount; ++i) {
   numerator[i] = y[i];                         // 分子 = y − J_old·s
   for (j = 0; j < variableCount; ++j)
      numerator[i] += -savedJacobian[j][i]*s[j];
}
for (i = 0; i < goalCount; ++i)
   for (j = 0; j < variableCount; ++j)
      jacobian[j][i] = savedJacobian[j][i] +    // J_new = J_old + numerator·sᵀ/sᵀs
            numerator[i] * s[j] / denom;
InvertJacobian();                               // 重新求逆后继续牛顿步
```

逐行注释：`numerator[i] = y[i] − Σ_j J_old[j][i]·s[j]` 即割线残差向量 $(y-Js)$ 的第 $i$ 个目标分量；秩一外积 `numerator[i]*s[j]/denom` 按列加到 `J_old`。注意与 `y_j = nominal - savedNominal` 配套：Broyden 更新用的是**名义值差**而非目标残差差，因为 $J$ 逼近的是 $y(x)$ 的导数。若 $s^Ts=0$（两步变量完全相同）则除零——由 `denom` 不设保护，工程上靠 `MaxStep` 阻尼与 `iterationsTaken` 上限兜底。

**收敛状态机。** `CalculateParameters` 中 `dcTypeId==2` 且 `iterationsTaken==1` 时差分建 $J_0$ 并置 `skipPerts=true`（`:1146`）；此后 `CheckCompletion` 不收敛时经 `skipPerts` 直接转 `CALCULATING`（`:1377-1384`），跳过 PERTURBING。每轮只做 1 次名义运行 + 1 次割线更新 + 1 次求逆，传播成本从 $O(n)$ 降到 $O(1)$。

## 11.6 ModifiedBroyden（逆雅可比秩一更新）

### 条目名
ModifiedBroyden 更新：$J^{-1}_{k+1}=J^{-1}_k+\dfrac{(s-J^{-1}_k y)\,(s^{T}J^{-1}_k)}{s^{T}J^{-1}_k y}$

### 公式
沿用 11.5 的 $s,y$ 记号，直接更新逆矩阵（`DifferentialCorrector.cpp:1199-1246`）：

$$
J^{-1}_{k+1} = J^{-1}_k + \frac{\left(s - J^{-1}_k y\right)\left(s^{T} J^{-1}_k\right)}{s^{T} J^{-1}_k y}
$$

代码分三步：$u = J^{-1}_k y$，$\text{denom}=u^{T}s$，$v = J^{-1}_k s / \text{denom}$，$\text{temp}=s-u$，然后 $\left[J^{-1}_{k+1}\right]_{ji} = \left[J^{-1}_k\right]_{ji} + \text{temp}_i\, v_j$。

### 代码位置
- `src/base/solver/DifferentialCorrector.cpp:1189-1248`（dcTypeId==3 分支）
- `src/base/solver/DifferentialCorrector.cpp:1281-1289`（savedInverseJacobian 保存）

### 深度讲解
**背景。** ModifiedBroyden 是 Broyden 的"good/Bad"系列中的逆更新（Broyden 的第二类更新，又称 Broyden-Bad 或逆秩一更新），直接保持 $J^{-1}$ 满足拟牛顿方程 $J^{-1}_{k+1} y = s$。它的好处是**省去每轮求逆**（`InvertJacobian` 只在首次迭代调用，`:1191-1195`），且与牛顿步 $\Delta x = J^{-1}(y^{\text{goal}}-y^{\text{nominal}})$ 天然衔接；代价是 $J^{-1}$ 的秩一修正不保证保持 $J$ 的割线方程，且对病态问题更敏感。**存储**：需要 `savedInverseJacobian`（$m\times n$）与 `savedNominal/savedVariable`，共 $mn$ 个 Real——即"无矩阵 $J$ 的存储、直接存逆"。

**实现细节（`DifferentialCorrector.cpp:1199-1246` 节选）：**

```cpp
for (i = 0; i < variableCount; ++i) s[i] = variable[i] - savedVariable[i];
for (j = 0; j < goalCount; ++j)    y[j] = nominal[j] - savedNominal[j];

Real denom = 0.0;
for (i = 0; i < variableCount; ++i) {               // u = J⁻¹_old·y
   temp[i] = 0.0;
   for (j = 0; j < goalCount; ++j) temp[i] += savedInverseJacobian[j][i] * y[j];
}
for (i = 0; i < variableCount; ++i) denom += temp[i] * s[i];   // denom = uᵀs

for (i = 0; i < goalCount; ++i) {                   // v = J⁻¹_old·s / denom
   v[i] = 0.0;
   for (j = 0; j < variableCount; ++j) v[i] += savedInverseJacobian[i][j] * s[j];
   v[i] /= denom;
}

for (i = 0; i < variableCount; ++i) {               // temp = s − u
   temp[i] = s[i];
   for (j = 0; j < goalCount; ++j) temp[i] -= savedInverseJacobian[j][i] * y[j];
}
for (i = 0; i < variableCount; ++i)                 // J⁻¹_new = J⁻¹_old + temp·vᵀ
   for (j = 0; j < goalCount; ++j)
      inverseJacobian[j][i] = savedInverseJacobian[j][i] + temp[i] * v[j];
```

逐行注释：`temp = s - J^{-1}y` 是拟牛顿方程的残差，`v = J^{-1}s/(s^{T}J^{-1}y)` 使 $(s-J^{-1}y)v^{T}$ 作用在 $y$ 上恰好为零（保割线）；若 `denom→0`（$s$ 与 $J^{-1}y$ 正交，或两步无进展）则更新爆炸——与 Broyden 一样无显式保护，工程上由 MaxStep 阻尼与迭代上限兜底。更新后直接进入牛顿步组装（11.4 的 delta 公式），无需再 `InvertJacobian`。

**收敛状态机。** 与 Broyden 相同：首次迭代差分建 $J_0$、求逆、置 `skipPerts=true`；后续 `skipPerts` 直接 CALCULATING。三者（Newton/Broyden/ModifiedBroyden）的传播成本对比：Newton 每轮 $O(n)$ 次扰动；Broyden 每轮 1 次传播 + 1 次求逆（$O(n^3)$，但 $n$ 通常很小）；ModifiedBroyden 每轮 1 次传播、无求逆。

## 11.7 DerivativeModel / Gradient / Jacobian：通用差分工具与 LineSearch 占位

### 条目名
DerivativeModel 差分模式基类、Gradient 梯度差分、Jacobian 雅可比差分、LineSearch（未实现）

### 公式
三种差分模式（`DerivativeModel.hpp:44-49` 枚举 FORWARD/CENTRAL/BACKWARD/USER_SUPPLIED）。

梯度（标量目标函数 $f(x)$，`Gradient.cpp:202-275`）：

$$
\nabla f_i \approx
\begin{cases}
\dfrac{f(x_i+h_i)-f(x)}{h_i} & \text{前向}\\[2mm]
\dfrac{f(x_i+h_i)-f(x_i-h_i)}{2h_i} & \text{中心}\\[2mm]
\dfrac{f(x)-f(x_i-h_i)}{h_i} & \text{后向}
\end{cases}
$$

雅可比（$m$ 个分量函数，`Jacobian.cpp:215-303`，按 `j*varCount+i` 压平存储）：

$$
J_{ji} = \dfrac{\partial g_j}{\partial x_i} \approx
\begin{cases}
\dfrac{g_j^{+}-g_j^{\text{nom}}}{h_i} & \text{前向}\\[2mm]
\dfrac{g_j^{+}-g_j^{-}}{2h_i} & \text{中心}\\[2mm]
\dfrac{g_j^{\text{nom}}-g_j^{-}}{h_i} & \text{后向}
\end{cases}
$$

### 代码位置
- `src/base/solver/DerivativeModel.hpp:40-80`、`DerivativeModel.cpp:149-181`（Initialize）、`:206-231`（Achieved）
- `src/base/solver/Gradient.cpp:202-275`（Calculate）
- `src/base/solver/Jacobian.cpp:130-151`（Initialize）、`:173-190`（Achieved）、`:215-303`（Calculate）
- `src/base/solver/LineSearch.hpp:39-44`、`LineSearch.cpp:46-60`（"not yet implemented" 占位）

### 深度讲解
**背景。** 这套类是为优化器准备的通用差分框架（2008 年随优化器原型加入，`Gradient.hpp:24` 创建日期 2008/03/28），与 `DifferentialCorrector` 内建的差分（11.3 节）功能重叠但接口不同：它以 `Achieved(pertNumber, componentId, dx, value, plusEffect)` 回调收集结果，由 `Calculate(vec)` 一次性组装，`pert` 向量自动从回调的 `dx` 记录（`DerivativeModel.cpp:226`）。当前唯一使用者是 Yukonad（11.9 节）。

**实现细节（Jacobian::Calculate 中心差分分支，`Jacobian.cpp:246-258` 节选）：**

```cpp
case CENTRAL_DIFFERENCE:
   jacobian[rowStart+i] = (plusPertEffect[rowStart+i] -   // 正扰动结果
                           minusPertEffect[rowStart+i]) / // 减负扰动结果
                          (2.0 * pert[i]);                // 除以 2h
   break;
case FORWARD_DIFFERENCE:
   jacobian.at(rowStart+i) = (plusPertEffect.at(rowStart+i) - nominal.at(j)) /
                             pert.at(i);                  // (g⁺ − g_nom)/h
   break;
```

逐行注释：`nominal` 在 `Achieved(-1,...)` 时记录（`Jacobian.cpp:176-185`）；`pert[i]==0` 直接抛异常防除零（`Jacobian.cpp:219-221`）；`USER_SUPPLIED` 模式未实现（`:276-279`）。Gradient 版本结构相同（`Gradient.cpp:227-253`），只是目标为标量、`nominal` 为单个 Real。

**LineSearch。** `LineSearch` 只有构造/析构，头注释明确 "This class is not yet implemented"（`LineSearch.hpp:37`）——GMAT 打靶与优化路径当前都不使用该类：打靶用 MaxStep 阻尼（11.4 节），Yukon 用自己的线搜索（11.10 节），fmincon 在 MATLAB 内部做线搜索。

**参数表。** 模式由 `SetDifferenceMode` 设置（`DerivativeModel.cpp:130-133`）；差分步长 `pert` 不是脚本参数，而是由调用方（Yukonad 的 `Perturbation` 数组，`Solver.cpp:344` 默认 1e-4）经 `Achieved` 的 `dx` 传入。

## 11.8 Optimizer 抽象：约束注册、目标代价与物理容差收敛

### 条目名
Optimizer 基类的目标/约束数据通道与 PerformToleranceCheck 收敛判据

### 公式
优化问题（代码结构隐含）：$\min_x f(x)$ 受约束 $g_{\text{eq}}(x)=0$（`condition==0`）、$g_{\text{ineq}}(x)\ge 0$（`condition!=0`）。

物理容差收敛（`Optimizer.cpp:1322-1493`，`PerformToleranceCheck`）：

$$
\text{收敛} \iff \underbrace{|f_{\text{new}}-f_{\text{old}}| \le \texttt{tolerance}}_{\text{目标静止（Optimizer.cpp:1363）}} \ \land\ \underbrace{\forall i:\ |g^{\text{desired}}_i-g^{\text{achieved}}_i| \le \varepsilon^{\text{eq}}_i}_{\text{等式约束（Optimizer.cpp:1417）}} \ \land\ \underbrace{\forall i:\ t_i \le \varepsilon^{\text{ineq}}_i}_{\text{不等式约束（Optimizer.cpp:1449）}}
$$

其中不等式测试值 $t_i = \pm(g^{\text{desired}}_i-g^{\text{achieved}}_i)$，`ineqConstraintOp[i]==-1` 时取负（`:1435-1437`）。

### 代码位置
- `src/base/solver/Optimizer.hpp:38-234`（类定义、参数枚举 `:145-155`、`Optimize()=0` `:141`）
- `src/base/solver/Optimizer.cpp:260-321`（SetSolverResults 注册 Objective/EqConstraint/IneqConstraint）、`:333-366`（SetResultValue）、`:383-418`（SetConstraintValues）、`:1322-1493`（PerformToleranceCheck）
- `src/base/solver/InternalOptimizer.hpp:41-58`、`ExternalOptimizer.hpp:43-150`、`ExternalOptimizer.cpp:65-80`（sourceType="MATLAB"、isInternal=false、requiresVariables=false、needsServerStartup=true）

### 深度讲解
**背景。** `Optimizer` 是纯抽象层：不实现任何数值算法，只定义目标函数与约束如何从命令（`Minimize`/`NonlinearConstraint`）流入、以及"收敛"的通用语义。`Optimize()=0`（`Optimizer.hpp:141`）由插件实现。ID 约定：等式约束 ID 从 1000 起、不等式从 2000 起（`Optimizer.cpp:73-74`，`EQ_CONST_START/INEQ_CONST_START`），命令按此路由。

**实现细节（约束注册，`Optimizer.cpp:285-314` 节选）：**

```cpp
else if (type == "EqConstraint") {                      // NonlinearConstraint 命令登记等式约束
   eqConstraintNames.push_back(name);
   eqConstraintValues.push_back(data[0]);               // 当前约束值（delta）
   eqConstraintDesiredValues.push_back(-1);             // 期望值（稍后由 SetConstraintValues 填）
   eqConstraintAchievedValues.push_back(-1);            // 达到值
   eqConstraintOp.push_back(0);                         // 0=等式
   eqConstraintTolerances.push_back(-1.0);              // 容差（稍后填）
   ++eqConstraintCount;
   return EQ_CONST_START + eqConstraintCount - 1;       // 返回 1000+i
}
```

逐行注释：`SetConstraintValues(id, desired, achieved, condition, within)`（`:383-418`）随后用 NonlinearConstraint 命令的 `Lower/Upper/Value/Within` 填充 desired/achieved/op/tolerance，`within<=0` 时回退到 `feasibilityTolerance`（`:400-403`、`:413-416`）。

**实现细节（物理容差收敛，`Optimizer.cpp:1363-1378` 与 `:1404-1458` 节选）：**

```cpp
if (objectiveDefined) {
   if (fabs(cost - oldCost) <= tolerance)   // 目标函数两步之差 ≤ Tolerance
      isMinimal = true;
   oldCost = cost;                          // 更新历史值
} else isMinimal = true;                    // 未定义目标则跳过该条件

// 等式约束：任意一条超差即失败
if (fabs(eqConstraintDesiredValues[i] - eqConstraintAchievedValues[i])
      > eqConstraintTolerances[i]) { eqSatisfied = false; break; }

// 不等式约束：测试值（按 op 取符号）超差即失败
Real testValue = ineqConstraintDesiredValues[i] - ineqConstraintAchievedValues[i];
if (ineqConstraintOp[i] == -1) testValue *= -1.0;      // “≤/≥” 方向翻转
if (testValue > ineqConstraintTolerances[i]) { ineqSatisfied = false; break; }
```

逐行注释：三者全满足时置 `currentState=FINISHED; converged=true; status=IN_TOLERANCE; physicalTolerancesMet=true`（`:1468-1479`）；否则内嵌优化器回到 `NOMINAL` 继续迭代（`:1487-1489`）。该检查由插件在每轮名义运行后调用，供"仿真与脚本容差分离"的场景使用（脚本容差在算法内部，物理容差在此处校验真实约束/代价）。

**参数表（Optimizer 层）。**

| 脚本参数 | 位置 | 类型 | 说明 |
|---|---|---|---|
| `ObjectiveFunction` | Optimizer.cpp:775-779 | 字符串 | Minimize 命令注册 |
| `Tolerance` | Optimizer.cpp:718-733 | Real>0 | 目标收敛容差；`feasibilityTolerance` 默认跟随它（:729-730） |
| `EqualityConstraintNames` / `InequalityConstraintNames` | Optimizer.cpp:837-841 | StringArray | 只读 |
| `PlotCost` | Optimizer.hpp:151 | Boolean | 只读（预留） |
| `SourceType` | Optimizer.cpp:752-753 | 字符串 | "None"/"MATLAB"（ExternalOptimizer 置 "MATLAB"，ExternalOptimizer.cpp:76） |
| `CheckPhysicalTolerances` | Optimizer.cpp:879-883 | Boolean | 受 `supportsPhysicalToleranceCheck` 约束（Optimizer.cpp:210-211） |

**InternalOptimizer / ExternalOptimizer。** `InternalOptimizer`（`InternalOptimizer.hpp:41`）参数计数即 `OptimizerParamCount`（`:54-57`），是内嵌算法（如 Yukonad）的基座；`ExternalOptimizer`（`ExternalOptimizer.hpp:43`）增加 `FunctionPath`（`ExternalOptimizer.cpp:47`）、持有 `GmatInterface`/`GmatServer`（`ExternalOptimizer.hpp:123-125`），构造时设 `isInternal=false; requiresVariables=false; needsServerStartup=true`（`ExternalOptimizer.cpp:76-79`）——外部优化器经 MATLAB 服务器反向往回调用 GMAT 执行控制序列。

## 11.9 Yukonad：梯度法状态机适配器与差分梯度/雅可比采集

### 条目名
Yukonad（InternalOptimizer 适配器）：有限差分梯度/雅可比采集 → Yukon 反向通信状态机

### 公式
无独立迭代公式；Yukonad 负责用 11.7 节的 `Gradient`/`Jacobian` 类把「名义运行 + 扰动运行」的达到值组装成 $\nabla f$ 与 $J_g$（`Yukonad.cpp:1344-1367`）：

$$
\nabla f = \texttt{gradientCalculator.Calculate(gradient)},\qquad
J_g = \texttt{jacobianCalculator.Calculate(jacobian)}
$$

差分模式由 `UseCentralDifferences` 开关选择（`Yukonad.cpp:518-538`）：false→FORWARD、true→CENTRAL。

反向通信状态（`Yukonad.cpp:1420-1427` 注释的 retCode 语义）：`-1`=需要新数据；`0`=计算中；`1`=收敛；`2`=超迭代；`3`=超函数评估；`4`=步长过小；`5`=找不到好方向；`6`=不可行。

### 代码位置
- `plugins/YukonOptimizerPlugin/src/base/solver/Yukonad.hpp:54-219`（类定义、参数枚举 `:136-147`）
- `plugins/YukonOptimizerPlugin/src/base/solver/Yukonad.cpp:96-121`（构造默认值）、`:518-538`（差分模式）、`:907-1010`（AdvanceState）、`:1234-1241`（RunNominal）、`:1251-1334`（RunPerturbation）、`:1344-1367`（CalculateParameters）、`:1377-1458`（CheckCompletion）、`:1064-1145`（SetResultValue 采集）、`:1544-1596`（InterpretRetCode）

### 深度讲解
**背景。** Yukonad 是 NASA Yukon SQP 算法（见 11.10）接入 GMAT 求解器状态机的适配层：它自己不迭代，而是把「GMAT 侧的名义/扰动运行」翻译成 Yukon 需要的函数值与导数，再以反向通信（reverse communication）方式驱动 `Yukon` 内核。`Gradient`/`Jacobian` 差分工具在此首次真正投入使用。

**实现细节（SetResultValue 采集差分数据，`Yukonad.cpp:1072-1090` 节选）：**

```cpp
bool plusEffect = true;
if (useCentralDifferences && (currentPertState == -1))
   plusEffect = false;                                  // 中心差分的负扰动拍

if (resultType == "Objective") {                        // 目标函数 → Gradient
   if (currentState == NOMINAL) {
      cost = value;                                     // 记录当前代价
      gradientCalculator.Achieved(-1, 0, 0.0, value, plusEffect); // 名义值
   }
   if (currentState == PERTURBING)
      gradientCalculator.Achieved(pertNumber, 0,
         (pertNumber < 0 ? 0.0 : perturbation[pertNumber]), value, plusEffect);
} else {                                                // 约束 → Jacobian（EqCon id-1000 / IneqCon id-2000）
   ...
   if (currentState == NOMINAL)
      jacobianCalculator.Achieved(-1, idToUse, 0.0, value, plusEffect);
   if (currentState == PERTURBING)
      jacobianCalculator.Achieved(pertNumber, idToUse,
         (pertNumber < 0 ? 0.0 : perturbation[pertNumber]), value, plusEffect);
}
```

逐行注释：`plusEffect` 决定结果进 `plusPertEffect` 还是 `minusPertEffect`（`DerivativeModel.cpp:227-230`）；`currentPertState` 在 `RunPerturbation` 中按 +1/−1 交替（`Yukonad.cpp:1285-1325`），中心差分每变量跑两拍。约束达到值还会经 `gmatProblem->SetConFunction(...)` 同步给 Yukon 的问题接口（`:1104-1110`）。

**实现细节（CheckCompletion 反向通信驱动，`Yukonad.cpp:1381-1455` 节选）：**

```cpp
if (iterationsTaken == 0) {                             // 首个 CHECKINGRUN：构造 Yukon 内核
   runOptimizer = new Yukon(gmatProblem, hessianUpdateMethod, maxIterations,
      maximumFunctionEvals, feasibilityTolerance, optimalityTolerance,
      functionTolerance, maximumElasticWeight);
   runOptimizer->PrepareToOptimize();
   runOptimizer->PrepareLineSearch();
}
runOptimizer->RespondToData();                          // 推进 Yukon 内部状态机
runOptimizer->CheckStatus(retCode, funTypes, optIterations, decVector,
   isNewX, userFunPointer);                             // 问 Yukon：下一步要什么
if (retCode == -1) { currentState = CHECKINGRUN; return; }  // 需要新函数数据
if (retCode == 0) {                                     // 计算中：把新变量写回 GMAT
   for (i = 0; i < variableCount; ++i) variable.at(i) = decVector[i];
   currentState = NOMINAL;                              // 再跑一轮控制序列
} else {                                                // 终止：映射 retCode → GMAT 状态
   currentState = FINISHED;
   if (retCode == 1) { status = Gmat::CONVERGED; converged = true; }
   else if (retCode == 2 || retCode == 3) { status = Gmat::EXCEEDED_ITERATIONS; }
   else { status = Gmat::FAILED; }
}
```

逐行注释：这是标准的 reverse-communication 循环——GMAT 执行控制序列（NOMINAL/PERTURBING）→ `CheckCompletion` 把数据喂给 Yukon → Yukon 返回新变量或终止码。`funTypes` 是 `CheckStatus` 的输出标志（`Yukon.cpp:453-569`），区分本轮需要"仅函数值"（1，线搜索阶段）还是"函数+导数"（2，迭代点求导阶段）；Yukonad 实际只按 `retCode` 分支（`:1402-1455`），`funTypes` 供驱动方观察传播成本。

**参数表（Yukonad 脚本字段，`Yukonad.cpp:50-81` 与构造默认值 `:96-121`）。**

| 脚本参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `FeasibilityTolerance` | Real>0 | 1e-4 | 约束可行性容差 → Yukon 的 tolCon |
| `OptimalityTolerance` | Real>0 | 1e-4 | 拉格朗日梯度 ∞-范数容差 → tolGrad |
| `FunctionTolerance` | Real>0 | 1e-4 | 目标变化容差 → tolF |
| `MaximumFunctionEvals` | Integer>0 | 1000 | 函数评估上限 |
| `MaximumElasticWeight` | Integer>0 | 10000 | 弹性模式权重上限 |
| `HessianUpdateMethod` | 枚举 | SelfScaledBFGS | DampedBFGS / SelfScaledBFGS（Yukonad.cpp:857-862） |
| `UseCentralDifferences` | Boolean | false | false=前向差分 |
| `MaximumIterations` | Integer | 200（Yukonad.cpp:115） | 继承自 Solver |
| `Tolerance` | Real | — | 显式拒绝：抛异常提示改用三种容差（Yukonad.cpp:678-683） |

**收敛状态机。** `retCode` 到 GMAT 状态映射：1→`CONVERGED`、2/3→`EXCEEDED_ITERATIONS`、其余→`FAILED`（`:1438-1452`）；`InterpretRetCode`（`:1544-1596`）给出各码的文字解释。差分模式在 `Initialize` 中按 `useCentralDifferences` 重设（`:1168-1181`）。

## 11.10 Yukon：SQP 主循环（QP 子问题、L1 罚线搜索、BFGS、收敛判据、弹性模式）

### 条目名
Yukon SQP：QP 子问题 + 非单调线搜索（L1 精确罚函数）+ Damped/SelfScaled BFGS + 收敛判据 + 弹性模式

### 公式
**QP 子问题**（Nocedal & Wright 2nd Ed. Eqs. 18.11，注释见 `Yukon.cpp:1197-1205`）：

$$
\min_{p}\ \tfrac{1}{2}p^{T}W_k p + \nabla f_k^{T}p
\quad\text{s.t.}\quad
\nabla c_{e}^{T}p = -c_{e},\quad
\nabla c_{i}^{T}p \ge -c_{i}
$$

其中 $W_k$ 为拉格朗日 Hessian 近似、$c_e/c_i$ 为等式/不等式约束在当前点的值。GMAT 把上下界写成 `conLowerBounds - conFunctions` / `conUpperBounds - conFunctions` 传入 MinQP（`Yukon.cpp:1224-1226`），由 MinQP 活动集方法求解（`Yukon.cpp:1267-1269`）。

**步长与边界缩放**（`Yukon.cpp:822-852`）：$\alpha_{\text{scale}}=\min_i\min\left\{\left|\frac{s_i^{\max}}{p_i}\right|, \left|\frac{x_i^{\text{bound}}-x_{k,i}}{p_i}\right|\right\}$，保证 $x_{k}+\alpha_{\text{scale}}p$ 不越出 `maxVarStepSize` 与变量界。

**线搜索步**（`Yukon.cpp:905-910`）：

$$
x_{k+1} = x_k + \alpha_{\text{scale}}\,\alpha\,p
$$

**L1 精确罚函数**（`Yukon.cpp:1566-1579`）：

$$
\phi(x) = f(x) + \sum_i \mu_i\, c_i^{+}(x),\qquad
c_i^{+} = \begin{cases} |c_i - b_i| & \text{等式}\\ \max(0,\ b_i^{\text{low}}-c_i,\ c_i-b_i^{\text{up}}) & \text{不等式}\end{cases}
$$

（违反量计算见 `Yukon.cpp:1612-1634`）。$\mu$ 按 N&W Eq. 18.36 思路自适应（`Yukon.cpp:729-779`）：若 $p^{T}\nabla f + \tfrac12 p^{T}W p > 0$ 则 $\sigma=2|p^{T}\nabla f|$、$\mu_i \ge \sigma|\lambda_i|$ 更新。

**充分下降条件**（`Yukon.cpp:957-982`）：预测下降 $\phi_{\text{pred}}=f_k + \nabla f^{T}(x_{k+1}-x_k) + \sum_i\mu_i(c_i^{+} + \nabla c_i^{T}(x_{k+1}-x_k))$，接受步当

$$
\phi(x_{k+1}) \le \phi(x_k) - \eta\left(\phi(x_k)-\phi_{\text{pred}}\right),\quad \eta=0.1
$$

否则二次回溯 $\alpha \leftarrow \alpha\cdot\alpha_{\text{red}}$，$\alpha_{\text{red}}=\dfrac{0.5}{1-\dfrac{\phi(x_k)-\phi(x_{k+1})}{\phi(x_k)-\phi_{\text{pred}}}}$，下限 $\alpha\leftarrow\alpha\cdot\tau$（$\tau=0.1$，`:974-982`）。

**Damped BFGS**（N&W Procedure 18.2，`Yukon.cpp:1385-1429`）：

$$
\theta = \begin{cases}1 & s^{T}y \ge 0.1\, s^{T}W s\\[1mm]
\dfrac{0.9\,s^{T}Ws}{s^{T}Ws - s^{T}y} & \text{否则}\end{cases},\qquad
r = \theta y + (1-\theta)Ws
$$

$$
W_{k+1} = W_k - \frac{W_k s s^{T}W_k}{s^{T}W_k s} + \frac{r r^{T}}{r^{T}s}
$$

（代码 `:1413-1421`；0.2/0.8 改为 0.1/0.9 系经验调整，注释 `:1387-1390`）。**SelfScaled BFGS**（Eldersveld §4.3.3，`Yukon.cpp:1431-1485`）：$\gamma = \frac{y^{T}s}{s^{T}Ws}$（当 $s^{T}y>0$ 且 $\le s^{T}Ws$ 时缩放 $W$）。更新后强制对称化 $W\leftarrow\frac{W+W^{T}}{2}$（`:1486`）。

**收敛判据**（`Yukon.cpp:1657-1804`，`CheckConvergence`）：

$$
\text{conv} \iff \underbrace{\| \nabla \mathcal{L} \|_{\infty} < \texttt{tolGrad}}_{\text{（Yukon.cpp:1722）}}\ \text{或}\ \underbrace{|\Delta f|_{\text{rel/abs}} < \texttt{tolF}}_{\text{（Yukon.cpp:1748）}},\quad \text{且约束满足 } \max c^{+} < \texttt{tolCon}\ (\texttt{Yukon.cpp:1695})
$$

（相对变化 $\frac{|f_{k+1}-f_k|}{|f_k|}$ 当 $|f_k|>10^{-7}$，否则绝对变化，`:1711-1719`。）

**弹性模式**（`Yukon.cpp:1328-1363` + `NLPFunctionGenerator.cpp:288-`）：QP 失败时引入弹性变量 $v,w\ge0$，代价加 $w_{\text{elastic}}\sum_i(v_i+w_i)$，约束改写为 $c_i - v_i + w_i \in [b^{\text{low}},b^{\text{up}}]$（`NLPFunctionGenerator.cpp:778-782`）；`maxElasticVar>1e-10` 且未达 `maxElasticWeight` 时 $w_{\text{elastic}}\gets 10\,w_{\text{elastic}}$ 继续（`Yukon.cpp:1674-1681`）。

### 代码位置
- `plugins/YukonOptimizerPlugin/src/base/solver/Yukon.hpp:46-262`（类与全部成员）
- `plugins/YukonOptimizerPlugin/src/base/solver/Yukon.cpp:56-133`（构造/选项默认）、`:307-350`（PrepareToOptimize，Hessian 初始化为单位阵 `:330-332`）、`:586-618`（Optimize 主循环）、`:670-860`（PrepareLineSearch：QP + μ 更新 + 步长缩放）、`:870-918`（TakeStep）、`:931-1038`（TestStepTaken：线搜索）、`:1048-1138`（PrepareForNextIteration：乘子更新与梯度差）、`:1147-1183`（CheckIfFinished）、`:1216-1318`（ComputeSearchDirection）、`:1328-1363`（PrepareElasticMode）、`:1375-1495`（UpdateHessian）、`:1566-1579`（CalcMeritFunction）、`:1595-1637`（CalcConViolations）、`:1657-1804`（CheckConvergence）
- `plugins/YukonOptimizerPlugin/src/base/solver/YukonOptions.hpp:41-69`（OptionsList 全字段）
- `plugins/YukonOptimizerPlugin/src/base/solver/MinQP.hpp:91-102`（活动集 QP 类）、`:30-34`（退出码：-1 不可行/-2 超迭代/-3 奇异/-4 零空间失败/-5 乘子失败）

### 深度讲解
**背景。** Yukon 是 SQP（序列二次规划）算法：每轮用当前点的二次近似（拉格朗日 Hessian $W_k$ 由 BFGS 族维护）求解一个凸 QP 得到搜索方向 $p$，再沿 $p$ 做带 L1 罚函数的线搜索保证全局收敛，乘子 $\lambda$ 从 QP 对偶解更新（`lagMultipliers += alpha*plam`，`:1071`）。SQP 的收敛速率：局部二次（Hessian 精确时）到超线性（BFGS 近似时）。与打靶器（11.2-11.6）的差别：SQP 天然处理不等式约束与目标极值，打靶器只能解等式型边值。

**实现细节（QP 子问题装配，`Yukon.cpp:1216-1232` 与 `:1267-1302` 节选）：**

```cpp
Rvector W(0);
MinQP qpOpt(0 * decVec, hessLagrangian, costJac, conJac,
   (conLowerBounds - conFunctions), (conUpperBounds - conFunctions), W, 2,
   checkForDuplicateCons);          // 构造 QP：Hessian=W_k, 梯度=costJac, 约束 A=conJac,
                                    // 右端 = 界 − 当前约束值（等价于 ∇cᵀp ≥ −c 的移动形式）
...
qpOpt.Optimize(px, f, lambdaQP, exitFlag, qpIter, activeSet);  // 活动集法求解
...
plam.SetSize(lambdaQP.GetSize());
plam = lambdaQP - lagMultipliers;   // 乘子增量（旧乘子在新迭代点不再适用）
```

逐行注释：`0*decVec` 是零初猜；`W` 传空向量表示无额外 Hessian 修正（MinQP 用传入的 hessianLagrangian）；`exitFlag!=1` 时进入弹性模式重解（`:1279-1291`）。`activeSet` 返回活动约束索引，Yukon 用它判断是否删除线性相关约束（`RemoveLinearlyDependentCons`，`:1816-1996`）并合并 MinQP 报告的重复约束界（`modifiedConIdxs`，`:1293-1298`）。

**实现细节（线搜索回溯，`Yukon.cpp:957-1000` 节选）：**

```cpp
Real meritPred = fold + costJac*(decVec - xk);            // 一阶预测代价变化
for (i = 0; i < totalNumCon; ++i)
   meritPred += mu[i]*(cViolOld[i] + conJac.GetRow(i)*(decVec - xk)); // 预测约束违反
Real decreaseCond = eta*(meritF - meritPred);             // η·(φ(x) − φ_pred)

if (meritFalpha > meritF - decreaseCond) {                // 未满足充分下降
   Real alphaRed = 0.5 / (1.0 - (meritF - meritFalpha) /
                         (meritF - meritPred));           // 二次插值回溯比
   if (alphaRed > tau && alphaRed <= 1.0) alpha = alpha*alphaRed;  // 用插值比
   else alpha = alpha*tau;                                // 否则用 τ=0.1 兜底
   ++stepAttempts;
   currentState = "LineSearchIteration";                  // 缩短 α 重试
} else {
   foundStep = true; currentState = "LineSearchConverged";
}
```

逐行注释：`alphaRed` 是经典 Armijo 二次插值公式（令 $\phi(x+\alpha p)\approx\phi(x)+\alpha\phi'+\tfrac12\alpha^2\phi''$ 反解使下降条件取等的 $\alpha$）；允许最多 `srchCount<10`（`Optimize` 主循环 `:606`）/ 20 次（`TakeStep` `:879`）收缩，连续两次方向失败（`failedSrchCount>=2`）则重置 Hessian 为单位阵重来（`:882-903`）。非单调放松：`allowSkippedReduction` 允许在 $\phi(x_{k+1})\le\phi_{\min}-\text{decreaseCond}$ 的弱条件下接受步（`:994-997`），连续 3 次放松不降则回到历史最小点并强制 10 轮严格线搜索（`:697-716`）。

**收敛状态机（CheckIfFinished，`Yukon.cpp:1147-1183`）。**

```
CheckConvergence(gradLag, fold, fnew, x, xold, alpha, maxConViolation)
   ├─ ‖∇L‖∞ < tolGrad ∧ 约束满足 ──► isConverged=1（收敛）
   ├─ |Δf| < tolF     ∧ 约束满足 ──► isConverged=2（收敛）
   ├─ 弹性模式达 maxElasticWeight 且违反不可消除 ──► isConverged=-1（不可行）
   └─ 否则 0（继续）→ 更新 Hessian → 下一轮
```

`isConverged!=0` 或超 `maxIter/maxFunEvals` 时 `isFinished=true`（`:1161-1176`）；`PrepareOutput` 把 `isConverged` 作为 exitFlag 返回（`:652`）。**与 Yukonad 的耦合**：`CheckStatus`（`Yukon.cpp:453-569`）把内部状态串（"Instantiated/ReadyToOptimize/ReadyForLineSearch/StepTaken/LineSearchConverged/Finished/MaxFuncEvalsReached/MaxIterCountReached/StepTooSmall/FailedStepDirection/InfeasibleProblem"）翻译成 Yukonad 可读的 `status/funTypes/isNewX`，构成 11.9 节的反向通信闭环。

**参数表（Yukon 内核 OptionsList，`YukonOptions.hpp:41-69`；构造时从 Yukonad 传入，`Yukon.cpp:98-111`）。**

| 选项 | 类型 | 默认（Yukon 构造） | 来源 |
|---|---|---|---|
| `hessUpdateMethod` | string | 传入（Yukonad 默认 SelfScaledBFGS） | Yukonad.HessianUpdateMethod |
| `meritFunction` | string | "NocWright"（Yukon.cpp:99） | 固定 L1 |
| `derivativeMethod` | string | "Analytic"（:103） | 预留；实际导数由 Yukonad 差分提供 |
| `finiteDiffVector` | Rvector(5) | 全 1e-9（:100-102） | 预留（未使用） |
| `maxIter` | Integer | 传入 maxIterations | Yukonad.MaximumIterations |
| `maxFunEvals` | Integer | 传入 maximumFunctionEvals | Yukonad.MaximumFunctionEvals |
| `tolCon` | Real | 传入 feasibilityTolerance | Yukonad.FeasibilityTolerance |
| `tolF` | Real | 传入 functionTolerance | Yukonad.FunctionTolerance |
| `tolGrad` | Real | 传入 optimalityTolerance | Yukonad.OptimalityTolerance |
| `maxVarStepSize` | Rvector | 用户问题 EvaluateMaxVarStep（:132） | 每变量最大步长 |
| `QPMethod` | string | "minQP"（:109） | 活动集 QP |
| `display` | string | "iter"（:110） | 迭代输出 |
| `maxElasticWeight` | Integer | 传入 maximumElasticWeight | Yukonad.MaximumElasticWeight |

## 11.11 FminconOptimizer：MATLAB fmincon（SQP active-set）外部接口

### 条目名
FminconOptimizer：options 透传、X0/Lower/Upper 传递、回调求值（F/GradF/约束）与 exitFlag 收敛映射

### 公式
数值迭代由 MATLAB Optimization Toolbox 的 `fmincon` 完成（**active-set 算法**，SQP 型），GMAT 侧只做数据交换。核心接口公式（`GmatFminconOptimizationDriver.m:43-45`）：

```matlab
GMAToptions = optimset(GMAToptions,'Algorithm','active-set');
[X, fVal, exitFlag] = fmincon(@EvaluateGMATObjective, X0, [], [], [], [], ...
   Lower, Upper, @EvaluateGMATConstraints, GMAToptions)
```

收敛映射（`FminconOptimizer.cpp:527-531`）：`exitFlag>0 ⟹ converged=true`。exitFlag 的文字解释（`FminconOptimizer.cpp:1316-1362`）：1=一阶最优性满足；2=变量已到最优邻域；3=目标变化小于收敛阈；4=搜索方向过小；5=目标变化小于准则；0=超函数评估/迭代；−1=被输出函数中止；−2=无可行点；−3=无界。

### 代码位置
- `plugins/FminconOptimizerPlugin/src/base/solver/FminconOptimizer.hpp:48-154`（`ExternalOptimizer` 派生，OPTIONS/OPTION_VALUES 参数）
- `plugins/FminconOptimizerPlugin/src/base/solver/FminconOptimizer.cpp:76-94`（ALLOWED_OPTIONS/DEFAULT_OPTION_VALUES）、`:226-272`（AdvanceState：INITIALIZING→RUNEXTERNAL→FINISHED）、`:278-390`（AdvanceNestedState：回调返回 F/GradF/NonLinearEqCon/NonLinearIneqCon）、`:396-535`（Optimize：optimset 组装、X0/Lower/Upper、驱动、exitFlag）、`:409-465`（optimset 字符串组装）、`:473-506`（数组传递）、`:513-525`（运行驱动与 exitFlag 读取）
- `application/matlab/gmat_fmincon/GmatFminconOptimizationDriver.m:41-48`（MATLAB 侧驱动脚本）
- `application/matlab/gmat_fmincon/EvaluateGMATObjective.m`、`EvaluateGMATConstraints.m`、`CallGMATfminconSolver.m`（回调，经 GMAT 服务器反向调用 GMAT）

### 深度讲解
**背景。** fmincon 的 active-set 算法本质是 SQP：每轮解 QP 子问题求搜索方向、做线搜索、用 BFGS 更新拉格朗日 Hessian（MATLAB 内部实现，GMAT 不接触其矩阵）。GMAT 的角色是"黑箱函数提供者"：`Optimize()` 把变量写进 MATLAB 工作区，运行驱动脚本，fmincon 通过回调函数反查 GMAT（经 `CallGMATfminconSolver` 调 GMAT 服务器执行控制序列），得到目标值、梯度（若 GradObj 开启）与约束值。

**实现细节（Optimize 的 optimset 组装，`FminconOptimizer.cpp:409-465` 节选）：**

```cpp
std::string optionsStr = "GMAToptions = optimset(";
std::string defaultOptions = optionsStr + "\'fmincon\');";   // 无选项时用 fmincon 默认
// 注入 MaximumIterations → MaxIter
options.push_back("MaxIter");  optionValues.push_back(maxIter.str());
for (i = 0; i < options.size(); i++) {
   if (optionValues.at(i) != "") {
      if (i != 0) optS << ",";
      optS << "\'" << options.at(i) << "\',";
      if ((7 <= i) && (i <= 11))               // 字符串型选项加单引号
         optS << "\'" << optionValues.at(i) << "\'";
      else
         optS << optionValues.at(i);
   }
}
optionsStr += optS.str() + ");";
EvalMatlabString(optionsStr);                  // MATLAB 中执行 optimset(...)
```

逐行注释：脚本允许的选项固定为 6 个（`DiffMaxChange/DiffMinChange/MaxFunEvals/TolX/TolFun/TolCon`，`FminconOptimizer.cpp:76-84`），`MaxIter` 由 `MaximumIterations` 注入（`:426-440`）；所有选项以字符串拼进 MATLAB 表达式，经 `EvalMatlabString`（`:1889-1924`）执行，MATLAB 引擎异常时可自动关闭重开。

**实现细节（回调数据组装，`FminconOptimizer.cpp:322-382` 节选）：**

```cpp
// AdvanceNestedState(CALCULATING) —— fmincon 每轮求值后向 GMAT 索要结果
outS << cost;                                  // F = 目标值
results.push_back("F = " + outS.str() + ";");
outS.str("");
for (i = 0; i < gradient.size(); i++)          // GradF = 梯度向量（fmincon 差分或用户给）
   outS << gradient.at(i) << ";";
results.push_back("GradF = [" + outS.str() + "];");
// 等式/不等式约束同理 → "NonLinearEqCon = [...]" / "NonLinearIneqCon = [...]"
// 约束雅可比暂未实现：JacNonLinearEqCon = []; JacNonLinearIneqCon = []; (:370-382)
```

逐行注释：返回的 `StringArray` 由 `AdvanceNestedState`（`FminconOptimizer.cpp:278-390`）生成，MATLAB 侧 `CallGMATfminconSolver` 解析后填入 fmincon 回调工作区；`nestedState` 在 `INITIALIZING→NOMINAL→CALCULATING→NOMINAL` 间循环（`:288-388`），NOMINAL 态把 MATLAB 传来的新变量写回 `variable`（`:294-302`）并触发一次完整控制序列传播。

**收敛状态机（AdvanceState，`FminconOptimizer.cpp:226-272`）。** 只有三态：`INITIALIZING →（CompleteInitialization）→ RUNEXTERNAL →（Optimize 阻塞至 fmincon 返回）→ FINISHED`。`RunExternal`（`:930-935`）调用 `Optimize()` 后直接置 FINISHED；`RunComplete`（`:960-968`）置 `status=RUN`（"Apply corrections" 语义）与 `hasFired=true`。收敛状态在 `GetProgressString` 的 FINISHED 分支按 `converged`/`iterationsTaken` 写 `CONVERGED`/`FAILED`/`EXCEEDED_ITERATIONS`（`:1131-1156`）。

**参数表（FminconOptimizer 脚本字段，`FminconOptimizer.cpp:76-94`）。**

| 脚本参数 | 默认 | 校验（IsAllowedValue，:1811-1833） |
|---|---|---|
| `DiffMaxChange` | 0.1000 | Real>0 |
| `DiffMinChange` | 1.0000e-08 | Real>0 |
| `MaxFunEvals` | 1000 | 整数>0 |
| `TolX` | 1.0000e-04 | Real>0 |
| `TolFun` | 1.0000e-04 | Real>0 |
| `TolCon` | 1.0000e-04 | Real>0 |
| `MaximumIterations`（→MaxIter） | Solver 默认 25 | Integer>0 |

其余细节（OpenConnection 检查 fmincon 存在性与支持文件、路径管理）见 [第13章](../CH13-plugins-a.md) 的 FminconOptimizerPlugin 一节与 `FminconOptimizer.cpp:1426-1646`。

## 11.12 VF13ad：外部 HSL SQP 优化器（接口与配置，源码不在本仓库）

### 条目名
VF13ad（Harwell Subroutine Library SQP 优化器）：参数面与插件加载机制

### 公式
VF13ad 是 HSL 的 SQP 非线性规划求解器（支持线性/非线性约束）。其迭代公式（QP 子问题 + 线搜索 + 拟牛顿 Hessian）属于 HSL 闭源实现，**本仓库不含 VF13ad 源码**，无法给出代码级公式；可确认的只有 GMAT 侧接口（脚本参数）与装载机制。

### 代码位置
- `src/base/executive/Moderator.cpp:843-848`（LoadPlugins 注释：当前代码只查找 VF13ad 库并加载）、`:848-880`（LoadPlugins 实现）
- `application/data/gui_config/VF13ad.ini:1-50`（GUI 面板布局：MaximumIterations/FeasibilityTolerance/Tolerance/DerivativeMethod/ShowProgress/ReportStyle/ReportFile/UseCentralDifferences）
- `docs_cn/_tmp/VF13ad.txt`（用户手册：字段与默认值）
- `doc/SystemDocs/ArchitecturalSpecification/Images/originals/VF13adSolverClasses.png`（架构图：VF13ad 属 Optimizer 派生插件类）
- 源码未发布：`src/gui/app/ResourceTree.cpp:1586`（GUI 按类型名 "VF13ad" 建节点）、`plugins/NewParameterPlugin/src/base/factory/NewParameterFactory.cpp:29`（注释提及 HSL VF13ad 优化器）

### 深度讲解
**背景。** VF13ad 是 Harwell Subroutine Library 的 SQP 优化器，GMAT 把它做成 `ExternalOptimizer` 分支插件：通过 `Optimize`/`EndOptimize` + `Vary` + `Minimize` + `NonlinearConstraint` 命令使用（`docs_cn/_tmp/VF13ad.txt:46-57`）。`Moderator::LoadPlugins` 的注释（`Moderator.cpp:843-845`）明示"当前代码只查找 VF13ad 库并加载"，即插件库由启动文件 `PLUGIN = ...` 声明、经 `LoadAPlugin`（`Moderator.cpp:896-`）动态装载。

**参数表（VF13ad 脚本字段，来自 `docs_cn/_tmp/VF13ad.txt` 与 `VF13ad.ini`）。**

| 脚本参数 | 类型 | 默认 | 说明 |
|---|---|---|---|
| `FeasibilityTolerance` | Real>0 | 1e-3 | 约束满足精度 |
| `UseFeasibility` | Boolean | true | 是否施加约束 |
| `MaximumIterations` | Integer>0 | 200 | 名义通过数上限 |
| `Tolerance` | Real>0 | 1e-5 | Minimize 目标收敛度量 |
| `UseCentralDifferences` | Boolean | false | false=前向差分 |
| `MaximumLineSearches` | Integer>0 | 20 | 每轮下坡搜索次数上限 |
| `CheckPhysicalTolerances` | Boolean | false | 启用 Optimizer::PerformToleranceCheck（11.8 节） |
| `ReportFile` / `ReportStyle` / `ShowProgress` | — | `VF13adVF13ad1.data` / Normal / true | 报告 |

**与核心的耦合。** 约束/目标经 `Optimizer::SetSolverResults`/`SetConstraintValues`（11.8 节）注册，梯度方法由 `UseCentralDifferences` 选择（同 Yukonad 的 `Gradient/Jacobian` 差分工具链）；`CheckPhysicalTolerances` 直接调用基类 `PerformToleranceCheck`。VF13ad 与 SNOPT 同属"外部商用/闭源 SQP"家族，详见 [第8章](../CH08-base-subsystems.md) 8.3.3 的 ExternalOptimizer 小节；Yukon 的 SQP 四层结构对比见 [第14章](../CH14-plugins-b.md) 14.13 与 3.7。

## 11.13 本章要点小结

1. **打靶（DifferentialCorrector）**：牛顿法 $x_{k+1}=x_k+\lambda J^{-1}(y^{\text{goal}}-y^{\text{nom}})$，$J$ 用前向/中心/后向差分（`CalculateJacobian`），方阵求逆、矩形伪逆（`InvertJacobian`）；阻尼 $\lambda$ 由 `MaxStep` 统一缩放，更新后按 `Lower/Upper` 截断。Broyden/ModifiedBroyden 用秩一割线更新省去每轮 $n$ 次扰动传播（`skipPerts`），前者更新 $J$ 后仍求逆、后者直接更新 $J^{-1}$。
2. **优化器抽象（Optimizer 族）**：只定义目标/约束数据通道与物理容差收敛；`InternalOptimizer`（Yukonad）与 `ExternalOptimizer`（fmincon、VF13ad）是两条实现路线。
3. **Yukon（SQP）**：QP 子问题（N&W 18.11）+ L1 罚线搜索（二次回溯）+ Damped/SelfScaled BFGS + 弹性模式；收敛判据 $\|\nabla\mathcal L\|_\infty<\texttt{tolGrad}$ 或 $|\Delta f|<\texttt{tolF}$ 且约束满足。
4. **fmincon/VF13ad**：迭代在 MATLAB/HSL 闭源库内完成，GMAT 只做数据交换与收敛状态映射；VF13ad 源码不在本仓库，仅能给出参数面与加载机制。
5. 差分工具链（DerivativeModel/Gradient/Jacobian）与打靶器内建差分并存，前者服务优化器（Yukonad），后者内嵌于打靶器。

## 11.14 公式索引表

| 公式 | 文件:行 | 所属类 |
|---|---|---|
| 状态机映射 AdvanceState（8 态分派） | src/base/solver/Solver.cpp:657-700 | Solver |
| 变量缩放 $x_{\text{scaled}}=(x+a_f)/m_f$ | src/base/command/Vary.cpp:1510-1517 | Vary 命令 |
| 变量反缩放 $x=x_{\text{scaled}}/m_f-a_f$ | src/base/command/Vary.cpp:1543-1545 | Vary 命令 |
| 变量/步长/界/初值 6 元组写入 | src/base/solver/Solver.cpp:405-459 | Solver |
| 打靶收敛判据 $\lvert y^{\text{nom}}-y^{\text{goal}}\rvert\le\varepsilon$ | src/base/solver/DifferentialCorrector.cpp:1365-1369 | DifferentialCorrector |
| 扰动模式（前向/中心/后向，diffMode） | src/base/solver/DifferentialCorrector.cpp:1043-1071 | DifferentialCorrector |
| 越界扰动反射 $x\mp2h$、pertDirection 翻转 | src/base/solver/DifferentialCorrector.cpp:1073-1105 | DifferentialCorrector |
| 雅可比前向/后向 $J_{ij}=(y^{\text{pert}}-y^{\text{nom}})/(d h)$ | src/base/solver/DifferentialCorrector.cpp:1543-1553 | DifferentialCorrector |
| 雅可比中心 $J_{ij}=(y^{+}-y^{-})/(2h)$ | src/base/solver/DifferentialCorrector.cpp:1555-1563 | DifferentialCorrector |
| 方阵 Inverse / 矩形 Pseudoinverse | src/base/solver/DifferentialCorrector.cpp:1596-1599；src/gmatutil/util/Rmatrix.cpp:1097/1425 | DifferentialCorrector / Rmatrix |
| Newton 修正 $\Delta x=J^{-1}(y^{\text{goal}}-y^{\text{nom}})$ | src/base/solver/DifferentialCorrector.cpp:1294-1300 | DifferentialCorrector |
| MaxStep 阻尼 $\lambda=\min_i\lvert s_i^{\max}/\Delta x_i\rvert$ | src/base/solver/DifferentialCorrector.cpp:1302-1313 | DifferentialCorrector |
| 更新与界截断 $x\gets\operatorname{clamp}(x+\lambda\Delta x)$ | src/base/solver/DifferentialCorrector.cpp:1320-1345 | DifferentialCorrector |
| Broyden 秩一更新 $J\gets J+(y-Js)s^{T}/s^{T}s$ | src/base/solver/DifferentialCorrector.cpp:1163-1183 | DifferentialCorrector |
| ModifiedBroyden 逆更新 $J^{-1}\gets J^{-1}+(s-J^{-1}y)(s^{T}J^{-1})/(s^{T}J^{-1}y)$ | src/base/solver/DifferentialCorrector.cpp:1199-1246 | DifferentialCorrector |
| saved 数据（Broyden/ModifiedBroyden）保存 | src/base/solver/DifferentialCorrector.cpp:1254-1290 | DifferentialCorrector |
| 梯度前向/中心/后向差分 | src/base/solver/Gradient.cpp:227-253 | Gradient |
| 雅可比（工具类）前向/中心/后向差分 | src/base/solver/Jacobian.cpp:233-274 | Jacobian |
| 差分数据采集 Achieved（pert/dx/plusEffect） | src/base/solver/DerivativeModel.cpp:206-231 | DerivativeModel |
| 优化器物理容差收敛（目标/等/不等约束） | src/base/solver/Optimizer.cpp:1363/1417/1449 | Optimizer |
| 约束注册与 ID 路由（1000/2000 起） | src/base/solver/Optimizer.cpp:285-314 | Optimizer |
| QP 子问题 $\min\tfrac12p^{T}Wp+\nabla f^{T}p$，s.t. $\nabla c^{T}p=-c$ | plugins/YukonOptimizerPlugin/src/base/solver/Yukon.cpp:1216-1232（公式注释 :1197-1205） | Yukon |
| 步长/边界缩放 $\alpha_{\text{scale}}=\min_i\min(\lvert s^{\max}/p\rvert,\lvert(x^{\text{bound}}-x)/p\rvert)$ | plugins/YukonOptimizerPlugin/src/base/solver/Yukon.cpp:822-852 | Yukon |
| 线搜索步 $x_{k+1}=x_k+\alpha_{\text{scale}}\alpha p$ | plugins/YukonOptimizerPlugin/src/base/solver/Yukon.cpp:905-910 | Yukon |
| L1 罚函数 $\phi=f+\sum\mu_i c_i^{+}$ | plugins/YukonOptimizerPlugin/src/base/solver/Yukon.cpp:1566-1579 | Yukon |
| 约束违反量计算（等/不等） | plugins/YukonOptimizerPlugin/src/base/solver/Yukon.cpp:1612-1634 | Yukon |
| μ 自适应（N&W 18.36）$\mu_i\ge\sigma\lvert\lambda_i\rvert$ | plugins/YukonOptimizerPlugin/src/base/solver/Yukon.cpp:729-779 | Yukon |
| 充分下降条件与二次回溯 $\alpha_{\text{red}}=0.5/(1-\Delta\phi/\Delta\phi_{\text{pred}})$ | plugins/YukonOptimizerPlugin/src/base/solver/Yukon.cpp:957-1000 | Yukon |
| Damped BFGS（θ、r、$W_{k+1}$ 更新） | plugins/YukonOptimizerPlugin/src/base/solver/Yukon.cpp:1385-1429 | Yukon |
| SelfScaled BFGS（γ 缩放） | plugins/YukonOptimizerPlugin/src/base/solver/Yukon.cpp:1431-1485 | Yukon |
| 收敛判据 $\|\nabla\mathcal{L}\|_\infty<\texttt{tolGrad}$、$\lvert\Delta f\rvert<\texttt{tolF}$、$\max c^{+}<\texttt{tolCon}$ | plugins/YukonOptimizerPlugin/src/base/solver/Yukon.cpp:1657-1804 | Yukon |
| 弹性模式代价 $\rho\sum(v_i+w_i)$ 与约束改写 | plugins/YukonOptimizerPlugin/src/base/solver/Yukon.cpp:1328-1363；NLPFunctionGenerator.cpp:288-/778-782 | Yukon / NLPFunctionGenerator |
| 乘子更新 $λ\gets λ+\alpha λ_{\text{QP}}$、梯度差 | plugins/YukonOptimizerPlugin/src/base/solver/Yukon.cpp:1071/1089-1090 | Yukon |
| 反向通信 retCode 语义（-1..6） | plugins/YukonOptimizerPlugin/src/base/solver/Yukonad.cpp:1420-1455/1544-1596 | Yukonad |
| 差分梯度/雅可比采集（Gradient/Jacobian 馈入） | plugins/YukonOptimizerPlugin/src/base/solver/Yukonad.cpp:1064-1145/1344-1367 | Yukonad |
| 差分模式开关 UseCentralDifferences | plugins/YukonOptimizerPlugin/src/base/solver/Yukonad.cpp:518-538 | Yukonad |
| fmincon 驱动（active-set SQP） | application/matlab/gmat_fmincon/GmatFminconOptimizationDriver.m:43-45 | FminconOptimizer（MATLAB 侧） |
| optimset 组装与 MaxIter 注入 | plugins/FminconOptimizerPlugin/src/base/solver/FminconOptimizer.cpp:409-465 | FminconOptimizer |
| X0/Lower/Upper 数组传递 | plugins/FminconOptimizerPlugin/src/base/solver/FminconOptimizer.cpp:473-506 | FminconOptimizer |
| exitFlag 收敛映射（>0 ⇒ converged） | plugins/FminconOptimizerPlugin/src/base/solver/FminconOptimizer.cpp:527-531 | FminconOptimizer |
| 回调数据组装 F/GradF/约束 | plugins/FminconOptimizerPlugin/src/base/solver/FminconOptimizer.cpp:322-382 | FminconOptimizer |
| VF13ad 插件加载（唯一外部库） | src/base/executive/Moderator.cpp:843-848 | Moderator |
| VF13ad GUI 参数布局 | application/data/gui_config/VF13ad.ini:12-49 | VF13ad（插件） |
