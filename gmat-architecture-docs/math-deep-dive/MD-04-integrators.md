# 第4章 数值积分器数学

> 本章范围：GMAT 全部数值积分器的**公式级**解析——显式 RK 骨架（`RungeKutta.*`）、五个一阶 RK 方法（`RungeKutta89`/`PrinceDormand45`/`PrinceDormand78`/`RungeKuttaFehlberg56` 及插件 `ProductionPropagatorPlugin` 的 `PrinceDormand853`）、二阶 Runge-Kutta-Nystrom 家族（`RungeKuttaNystrom` 基类 + `DormandElMikkawyPrince68`）、预测-校正多步法（`PredictorCorrector` 基类 + `AdamsBashforthMoulton` + 未实现的 `Cowell` 外壳），并含误差归一化与容差语义（`PhysicalModel::EstimateError`）。共 11 个源码类（22 个 .hpp/.cpp 文件）+ 2 个支撑类。
>
> 与[架构章 CH07](../CH07-propagator.md) 互补：CH07 讲类结构、继承体系与传播主循环；本章只讲**每个积分器的数学公式与系数来源**，每个条目按"公式 → 代码位置 → 深度讲解"展开，文末附公式索引表。文中所有行号均经 read 工具逐行核实。术语沿用 CH07：级（stage）、阶（order）、嵌入对（embedded pair）、步长控制（step-size control）、容差（tolerance）。

## 一、积分器体系总览

### 1.1 继承体系与脚本名

```
Propagator (基类, Propagator.hpp)
 └─ Integrator (Integrator.hpp:128)                    —— 容差/步长基础设施
     ├─ RungeKutta (RungeKutta.hpp:151)                —— 显式 RK 骨架（stages/ai/bij/cj/ee）
     │   ├─ RungeKutta89          ("RungeKutta89")     —— Verner 8(9)，16 级
     │   ├─ PrinceDormand45       ("PrinceDormand45")  —— DP 4(5)，7 级
     │   ├─ PrinceDormand78       ("PrinceDormand78")  —— PD 7(8)，13 级
     │   ├─ RungeKuttaFehlberg56  ("RungeKutta56")     —— Fehlberg 5(6)，8 级
     │   └─ RungeKuttaNystrom (RungeKuttaNystrom.hpp:93)—— 二阶 RKN 骨架（derivativeOrder=2）
     │       └─ DormandElMikkawyPrince68 ("RungeKutta68")—— DEP 6(8)，9 级
     └─ PredictorCorrector (PredictorCorrector.hpp:93) —— 多步法骨架（history/pweights/cweights）
         ├─ AdamsBashforthMoulton ("AdamsBashforthMoulton")—— AB4/AM3
         └─ Cowell                (工厂中未注册)         —— 未实现外壳
插件 ProductionPropagatorPlugin:
  RungeKutta → PrinceDormand853  ("PrinceDormand853")  —— HNW DOP853 8(5,3)，12 级
```

- 工厂注册见 `PropagatorFactory.cpp:83-106`（`CreatePropagator`）与 `:119-134`（`creatables`）：脚本可用名 `RungeKutta89`、`PrinceDormand78`、`PrinceDormand45`、`RungeKutta68`（=DEP68）、`RungeKutta56`（=Fehlberg56）、`AdamsBashforthMoulton`；`Cowell` 被注释（`:102-103, :133`）。`PrinceDormand853` 由 `ProductionPropagatorPlugin/src/base/factory/ProductionPropagatorFactory.cpp:71, :90` 注册。
- 默认传播器：`PropSetup::PropSetup()` 构造 `new RungeKutta89("RungeKutta89")` + `ODEModel` + `PointMassForce`（`PropSetup.cpp:173-183`），即默认配置是「RK8(9) + 仅质点引力」；类与调用链细节见 [CH07 §2.1](../CH07-propagator.md)。

### 1.2 记号约定

本章统一记号：状态向量 $\mathbf r\in\mathbb R^n$，右端项 $\dot{\mathbf r}=f(t,\mathbf r)$（由 `PhysicalModel::GetDerivatives` 提供，`PhysicalModel.hpp:188`）；积分步长 $h$（代码变量 `stepSize`）；级数 $s$（`stages`）；第 $i$ 级导数斜率 $\mathbf k_i$。各级节点时刻份额 $c_i$ 存 `ai[]`，级间系数矩阵 $A=(a_{ij})$ 存 `bij[][]`，解累加权重 $b_i$ 存 `cj[]`，误差系数 $\mathbf{ee}=b-\hat b$ 存 `ee[]`。

### 1.3 Butcher 表在代码中的存储约定

`RungeKutta::Initialize()`（`RungeKutta.cpp:203-289`）按级数分配内存：`bij` 是**下三角按行存储**，第 $i$ 行 `bij[i] = new Real[i+1]`（`RungeKutta.cpp:268`），即 `bij[i][j]` 只有 $j=0\ldots i$ 有效且 `bij[i][i]≡0`（对角线占位）；`ai/cj/ee` 各为长度 `stages` 的一维数组。级斜率存 `ki[i][j]`（$s\times n$ 矩阵，`RungeKutta.cpp:239, :265-279`）。误差系数 $\mathbf{ee}$ 恒为 $b-\hat b$（嵌入解之差），见 `RungeKutta.hpp:103-104` 注释；两种写法并存：直接给差值（如 RK89、Fehlberg56、DOP853），或先建 `cjhat[]` 再循环相减（PD78、DEP68）。

---

## 二、RungeKutta 基类：显式 RK 骨架

本类实现所有显式 RK 共用的三件事：**阶段推进**（`RawStep`）、**嵌入对误差估计**（`EstimateError`）、**步长自适应**（`AdaptStep`）；具体系数由派生类 `SetCoefficients()` 填充（纯虚，`RungeKutta.hpp:209`）。构造函数把步长控制指数固化下来（`RungeKutta.cpp:87-100`）：

```cpp
RungeKutta::RungeKutta(Integer st, Integer order, const std::string &typeStr,
                                           const std::string &nomme) :
    Integrator      (typeStr, nomme),
    stages          (st),
    ...
    sigma           (0.9),            // 安全因子 σ
    incPower        (1.0/order),      // 接受步长时的放大指数 1/m
    decPower        (1.0/(order-1)),  // 拒绝步长时的缩小指数 1/(m-1)
```

即 $m=$ 构造函数传入的 `order`（各方法的"主解阶数"）。

### 2.1 RK 阶段推进公式（RawStep）

- **公式**：第 $i$ 级（$i=0,\ldots,s-1$）先由前 $i$ 级的斜率线性组合出中间状态，再在该时刻求右端项并乘步长：

$$ \mathbf k_i = h\,f\!\left(t_0+c_i h,\ \mathbf r_0+\sum_{j=0}^{i-1} a_{ij}\mathbf k_j\right),\qquad c_i=\texttt{ai[i]},\ a_{ij}=\texttt{bij[i][j]} $$

一步终态为斜率加权和：

$$ \mathbf r(t_0+h)=\mathbf r_0+\sum_{i=0}^{s-1} b_i\,\mathbf k_i,\qquad b_i=\texttt{cj[i]} $$

（文献公式见 `RungeKutta.hpp:78-79` 与 `:86`；代码实现见 `RungeKutta.cpp:506-600`。）

- **代码位置**：`src/base/propagator/RungeKutta.cpp:527-588`（级循环与累加）；`src/base/propagator/RungeKutta.hpp:78-86`（文献公式）。
- **深度讲解**：
  - **实现要点**：`RawStep()` 中每级先把 `inState` 拷入 `stageState`（`RungeKutta.cpp:529`），非首级再累加 $\sum_j \texttt{bij[i][j]}\cdot\texttt{ki[j]}$（`:543-550`），然后调 `physicalModel->GetDerivatives(stageState, stepSize*ai[i])` 求 $f$（`:560`，第二个参数是"距步起点的 elapsed time"，供力模型内部推进），最后 `ki[i][j] = stepSize * ddt[j]`（`:576-577`）——斜率已含 $h$ 因子。终态 `candidateState = inState + Σ cj[i]·ki[i]`（`:581-588`）。
  - **为什么是显式**：$b_{ij}$ 只依赖 $j<i$ 的级，逐级串行计算；这与隐式 RK（见 [MD-13](../MD-13-csalt.md) 的配点法）本质不同，后者需解非线性方程组。
  - **代码片段**（`RungeKutta.cpp:543-588`，节选）：

```cpp
      if (i > 0) {                                // 非首级：由前 i 级斜率组合中间状态
         for (j = 0; j < i; j++)
            for (k = 0; k < dimension; k++)
               stageState[k] += bij[i][j] * ki[j][k];   // stageState = r0 + Σ a_ij·k_j
      }
      ...
      if (!physicalModel->GetDerivatives(stageState, stepSize * ai[i]))  // 在 t0+c_i·h 处求 f
         return false;
      for (j = 0; j < dimension; j++)
         ki[i][j] = stepSize * ddt[j];            // k_i = h·f(...)
   }
   // 终态累加
   memcpy(candidateState, inState, dimension*sizeof(Real));
   for (i = 0; i < stages; i++)
      for (j = 0; j < dimension; j++)
         candidateState[j] += cj[i] * ki[i][j];   // r(t0+h) = r0 + Σ b_i·k_i
```

  - **力模型限步**：`Step()` 主循环（`RungeKutta.cpp:304-497`）先用 `minimumStep/maximumStep` 夹逼 `stepSize`（`:320-323`），再查 `physicalModel->GetForceMaxStep(...)` 取力模型允许的最大步（`:334`），若请求步超限则 `stepSize = forceMaxStep` 并标记 `stepLimited`（`:335-365`），被缩短后以"接力步"递归补足剩余区间（`:468-484`）——这类控制流细节见 [CH07 §2.1](../CH07-propagator.md)。

### 2.2 嵌入对误差估计公式（EstimateError）

- **公式**：同一组级斜率 $\mathbf k_i$ 上再定义一个**嵌入解** $\hat{\mathbf r}(t_0+h)=\mathbf r_0+\sum_i \hat b_i\mathbf k_i$，两者之差即局部误差估计：

$$ \mathbf\Delta = \sum_{i=0}^{s-1}(b_i-\hat b_i)\,\mathbf k_i,\qquad \texttt{ee[i]}=b_i-\hat b_i $$

（文献公式 `RungeKutta.hpp:94-104`；实现 `RungeKutta.cpp:679-694`。）

- **代码位置**：`src/base/propagator/RungeKutta.cpp:679-694`；`src/base/propagator/RungeKutta.hpp:94-104`。
- **深度讲解**：
  - **嵌入对思想**：$b$ 与 $\hat b$ 分别对应阶数 $p$ 与 $\hat p$ 的两个解，共用全部 $s$ 级斜率，因此误差估计**不增加任何额外右端项求值**——这是 RK 嵌入法的核心经济性。各方法的 $(p,\hat p)$ 见 §三。
  - **实现**：`errorEstimates[i] = Σ_j ee[j]·ki[j][i]`（分量级误差），随后交给 `physicalModel->EstimateError(errorEstimates, candidateState)` 做归一化并取最大值（`:693`）。
  - **特殊约定**：`Step()` 中若 `maxerror == 0.0` 视为"无误差控制"，直接采纳候选步（`RungeKutta.cpp:414-424`）——ABM 启动阶段正是靠此跳过启动器的误差检查（见 §5.2）。
  - **代码片段**（`RungeKutta.cpp:683-694`）：

```cpp
    for (i = 0; i < dimension; i++)
    {
        errorEstimates[i] = 0.0;
        for (j = 0; j < stages; j++)
            errorEstimates[i] += ee[j] * ki[j][i];   // Δ_i = Σ (b_j - b̂_j)·k_j,i
    }
    // 交给力模型归一化：返回最大相对误差
    return physicalModel->EstimateError(errorEstimates, candidateState);
```

### 2.3 步长控制公式（AdaptStep）

- **公式**：设期望精度 $\alpha$（`tolerance`，即脚本 `Accuracy`）、实测最大误差 $\epsilon$（`maxerror`）、安全因子 $\sigma=0.9$、方法阶 $m=$`order`，则

$$ \text{误差过大（拒绝重试）：}\quad h_{\text{new}}=\sigma\,h\left(\frac{\alpha}{\epsilon}\right)^{1/(m-1)},\qquad \text{（} \texttt{RungeKutta.cpp:750}\text{）} $$

$$ \text{误差可接受（采纳并放大）：}\quad h_{\text{new}}=\sigma\,h\left(\frac{\alpha}{\epsilon}\right)^{1/m},\qquad \text{（} \texttt{RungeKutta.cpp:761}\text{）} $$

（文献公式 `RungeKutta.hpp:114-115` 与 `:127-128`；$\sigma$ 讨论见 `:117-121`。）

- **代码位置**：`src/base/propagator/RungeKutta.cpp:718-767`；`src/base/propagator/RungeKutta.hpp:106-132`。
- **深度讲解**：
  - **幂指数的含义**：基类注释（`RungeKutta.hpp:106-128`）的约定是"$m$ 为截断阶数，拒绝分支取指数 $1/(m-1)$、放大分支取指数 $1/m$"——对 $0<\alpha/\epsilon<1$（拒绝情形）$1/(m-1)>1/m$ 使缩小更激进，对 $\alpha/\epsilon>1$（放大情形）$1/m<1/(m-1)$ 使增长更克制，**双向都偏保守**，配合 $\sigma=0.9$ 减少无谓试步。`incPower=1/order`、`decPower=1/(order-1)` 在构造函数固化（`RungeKutta.cpp:96-98`），因此各方法的实际指数由传入的 `order` 决定（见 §三各条目）。
  - **σ=0.9 安全因子**：刻意低估新步长，减少"试步失败再重试"的概率（`RungeKutta.hpp:117-121`）。
  - **容差语义**：$\alpha=$`tolerance`，默认 $1.0\times10^{-11}$（`Integrator.cpp:135`，参数文本 `"Accuracy"` 见 `:98`）；`maxerror` 是**相对**误差（见 §2.4）。步长再被 `minimumStep`（默认 0.001 s）与 `maximumStep`（默认 2700 s = 45 min，`Integrator.cpp:138-139`）夹逼。
  - **最小步长豁免 kludge**：当 `|stepSize| == minimumStep` 且误差仍超标时，若 `stopIfAccuracyViolated` 则抛异常，否则打印一次警告后**强制采纳**坏步（`RungeKutta.cpp:727-748`）——注释（`:702-712`）说明这是为跨越圆柱影模型 SRP 阴影边界不连续而设，属临时措施。
  - **代码片段**（`RungeKutta.cpp:721-767`，节选）：

```cpp
    if (maxerror > tolerance)  // 误差过大 → 缩小步长重试
    {
        if (GmatMathUtil::Abs(stepSize) == minimumStep) { ... }  // 最小步长豁免（L727-748）
        stepSize = sigma * stepSize * pow(tolerance/maxerror, decPower);  // h' = σh(α/ε)^{1/(m-1)}
        if (fabs(stepSize) < minimumStep)
            stepSize = ((stepSize < 0.0) ? -minimumStep : minimumStep);
        ++stepAttempts;                 // 记录一次失败试步
        return false;                   // 拒绝本步，外层 do-while 用新步长重试
    }
    // 采纳：把候选态拷出，并放大下一步
    stepSize = sigma * stepSize * pow(tolerance/maxerror, incPower);  // h' = σh(α/ε)^{1/m}
    memcpy(outState, candidateState, dimension*sizeof(Real));
    stepAttempts = 0;
    return true;
```

### 2.4 相对误差归一化与容差语义（PhysicalModel::EstimateError）

- **公式**：各分量的误差估计 $\mathrm{EE}_i$ 相对一步位移 $\Delta_i=r_i(t+h)-r_i(t)$ 归一化：

$$ \epsilon_i = \begin{cases} |\mathrm{EE}_i/\Delta_i| & \Delta_i > \theta \\[2pt] |\mathrm{EE}_i| & \Delta_i \le \theta \end{cases},\qquad \texttt{maxerror}=\max_i \epsilon_i,\ \theta=\texttt{relativeErrorThreshold}=0.10 $$

（`PhysicalModel.cpp:1496-1512`；阈值默认 0.10，`PhysicalModel.cpp:188`；公式注释 `:1461`。）

- **代码位置**：`src/base/forcemodel/PhysicalModel.cpp:1496-1512`；`ODEModel::EstimateError` 直接转发（`ODEModel.cpp:3805`）。
- **深度讲解**：
  - **相对误差语义**：`Accuracy`（`tolerance`）是"相对误差"的阈值：一步位移 $\Delta_i$ 超过 $\theta=0.1$ 时按相对误差 $\mathrm{EE}_i/\Delta_i$ 考核；$\Delta_i\le\theta$（比如某分量几乎不变）时退化为绝对误差 $\mathrm{EE}_i$。注释（`:1472-1487`）说明这样设计是为了让积分器能**平滑越过小幅不连续**（如圆柱地影阴影边界）而不卡死。
  - **积分器侧的唯一出口**：所有 RK 的 `EstimateError()` 都调用这个归一化函数，因此 §2.3 的 $\epsilon$（`maxerror`）即这里的返回值——一个无量纲相对误差，与 `tolerance` 直接可比。
  - **P-C 家族的差异**：`PredictorCorrector` 构造函数把 `tolerance` 覆盖为 $1.0\times10^{-10}$（`PredictorCorrector.cpp:138`），并另设 `targetError=1e-11`、`lowerError=1e-13` 双阈值（见 §5.1）。
  - **代码片段**（`PhysicalModel.cpp:1500-1511`）：

```cpp
   for (Integer i = 0; i < dimension; ++i)
   {
      delta = answer[i] - modelState[i];        // 一步位移 Δ_i
      if (delta > relativeErrorThreshold)       // 位移足够大 → 相对误差
         err = fabs(diffs[i] / delta);
      else                                      // 位移过小 → 绝对误差
         err = fabs(diffs[i]);
      if (err > retval)
         retval = err;                          // 取所有分量最大者
   }
```

---

## 三、一阶 RK 方法（Butcher 表条目）

### 3.1 RungeKutta89 —— Verner 8(9)，16 级

- **公式**：16 级显式 RK。节点（`ai`，`RungeKutta89.cpp:161-176`，记 $\rho=\sqrt6$）：

$$ c_i = \left[0,\ \tfrac{1}{12},\ \tfrac{1}{9},\ \tfrac{1}{6},\ \tfrac{2+2\rho}{15},\ \tfrac{6+\rho}{15},\ \tfrac{6-\rho}{15},\ \tfrac{2}{3},\ \tfrac{1}{2},\ \tfrac{1}{3},\ \tfrac{1}{4},\ \tfrac{4}{3},\ \tfrac{5}{6},\ 1,\ \tfrac{1}{6},\ 1\right] $$

解累加权重（`cj`，`:331-346`，9 阶主解）：

$$ b = \left[\tfrac{23}{525},\,0,\,0,\,0,\,0,\,0,\,0,\,\tfrac{171}{1400},\,\tfrac{86}{525},\,\tfrac{93}{280},\,-\tfrac{2048}{6825},\,-\tfrac{3}{18200},\,\tfrac{39}{175},\,0,\,\tfrac{9}{25},\,\tfrac{233}{4200}\right] $$

误差系数（`ee`，`:348-363`，8 阶嵌入解之差 $b-\hat b$）：

$$ \mathbf{ee} = \left[-\tfrac{7}{400},\,0,\,0,\,0,\,0,\,0,\,0,\,\tfrac{63}{200},\,-\tfrac{14}{25},\,\tfrac{21}{20},\,-\tfrac{1024}{975},\,-\tfrac{21}{36400},\,-\tfrac{3}{25},\,-\tfrac{9}{280},\,\tfrac{9}{25},\,\tfrac{233}{4200}\right] $$

级间矩阵 $A$ 按行（`bij`，`:179-329`；行内末位 $a_{ii}=0$ 占位省略）：

$$
\begin{aligned}
A_1&=[0],\quad A_2=\left[\tfrac{1}{12},0\right],\quad A_3=\left[\tfrac{1}{27},\tfrac{2}{27},0\right],\quad A_4=\left[\tfrac{1}{24},0,\tfrac{1}{8},0\right],\\
A_5&=\left[\tfrac{4+94\rho}{375},0,\tfrac{-94-84\rho}{125},\tfrac{328+208\rho}{375},0\right],\\
A_6&=\left[\tfrac{9-\rho}{150},0,0,\tfrac{312+32\rho}{1425},\tfrac{69+29\rho}{570},0\right],\\
A_7&=\left[\tfrac{927-347\rho}{1250},0,0,\tfrac{-16248+7328\rho}{9375},\tfrac{-489+179\rho}{3750},\tfrac{14268-5798\rho}{9375},0\right],\\
A_8&=\left[\tfrac{2}{27},0,0,0,0,\tfrac{16-\rho}{54},\tfrac{16+\rho}{54},0\right],\\
A_9&=\left[\tfrac{19}{256},0,0,0,0,\tfrac{118-23\rho}{512},\tfrac{118+23\rho}{512},-\tfrac{9}{256},0\right],\\
A_{10}&=\left[\tfrac{11}{144},0,0,0,0,\tfrac{266-\rho}{864},\tfrac{266+\rho}{864},-\tfrac{1}{16},-\tfrac{8}{27},0\right],\\
A_{11}&=\left[\tfrac{5034-271\rho}{61440},0,0,0,0,0,\tfrac{7859-1626\rho}{10240},\tfrac{-2232+813\rho}{20480},\tfrac{-594+271\rho}{960},\tfrac{657-813\rho}{5120},0\right],\\
A_{12}&=\left[\tfrac{5996-3794\rho}{405},0,0,0,0,\tfrac{-4342-338\rho}{9},\tfrac{154922-40458\rho}{135},\tfrac{-4176+3794\rho}{45},\tfrac{-340864+242816\rho}{405},\tfrac{26304-15176\rho}{45},-\tfrac{26624}{81},0\right],\\
A_{13}&=\left[\tfrac{3793+2168\rho}{103680},0,0,0,0,\tfrac{4042+2263\rho}{13824},\tfrac{-231278+40717\rho}{69120},\tfrac{7947-2168\rho}{11520},\tfrac{1048-542\rho}{405},\tfrac{-1383+542\rho}{720},\tfrac{2624}{1053},\tfrac{3}{1664},0\right],\\
A_{14}&=\left[-\tfrac{137}{1296},0,0,0,0,\tfrac{5642-337\rho}{864},\tfrac{5642+337\rho}{864},-\tfrac{299}{48},\tfrac{184}{81},-\tfrac{44}{9},-\tfrac{5120}{1053},-\tfrac{11}{468},\tfrac{16}{9},0\right],\\
A_{15}&=\left[\tfrac{33617-2168\rho}{518400},0,0,0,0,\tfrac{-3846+31\rho}{13824},\tfrac{155338-52807\rho}{345600},\tfrac{-12537+2168\rho}{57600},\tfrac{92+542\rho}{2025},\tfrac{-1797-542\rho}{3600},\tfrac{320}{567},-\tfrac{1}{1920},\tfrac{4}{105},0,0\right],\\
A_{16}&=\left[\tfrac{-36487-30352\rho}{279600},0,0,0,0,\tfrac{-29666-4499\rho}{7456},\tfrac{2779182-615973\rho}{186400},\tfrac{-94329+91056\rho}{93200},\tfrac{-232192+121408\rho}{17475},\tfrac{101226-22764\rho}{5825},-\tfrac{169984}{9087},-\tfrac{87}{30290},\tfrac{492}{1165},0,\tfrac{1260}{233},0\right].
\end{aligned}
$$

（节点行 $A_i$ 即 `bij[i][0..i]`，末位 0 为对角线占位。）

- **代码位置**：`src/base/propagator/RungeKutta89.cpp:152-364`（`SetCoefficients`：ai `:161-176`，bij `:179-329`，cj `:331-346`，ee `:348-363`）；构造 `RungeKutta(16, 9, "RungeKutta89")` 于 `:79-80`；系数来源注释 `:148-149`。
- **深度讲解**：
  - **方法与文献**：注释（`:144-149`）明确：系数取自 **Verner 1978**（*SIAM J. Numer. Anal.* **15**(4)，"Explicit Runge-Kutta methods with estimates of the local truncation error"），注释记号 "RK 8(9)"。GMAT 以 **9 阶解推进**（`cj` 含第 15、16 级权重，构造函数 `order=9` → `incPower=1/9`、`decPower=1/8`），8 阶嵌入解 `b̂=b−ee` 只用到前 14 级（$\hat b_{14}=\hat b_{15}=0$）——"9 阶积分 + 8 阶误差控制"，与 [CH07](../CH07-propagator.md) 的表述一致。
  - **系数结构**：大量无理系数以 `rt6 = sqrt(6.0)` 符号化表达（`:159`），体现 Verner 方法"$\sqrt6$ 节点"的设计（节点集中在 $[0,1]$ 的 5/6 分点附近，含 $c_{12}=4/3>1$ 的超界节点）。16 级中 $b_1=b_2=\cdots=b_7=0$，即前 7 级斜率不直接进入终态。
  - **角色**：`PropSetup` 默认积分器（`PropSetup.cpp:173`）；同时是预测-校正族的启动器（`starter`，见 §5）。
  - **代码片段**（`RungeKutta89.cpp:159-176`）：

```cpp
    Real rt6 = sqrt(6.0);          // 系数统一以 √6 表示，避免小数截断
    ai[0] = 0.0;
    ai[1] = 1.0 / 12.0;
    ai[2] = 1.0 / 9.0;
    ai[3] = 1.0 / 6.0;
    ai[4] = (2.0 + 2.0 * rt6) / 15.0;    // c5 = (2+2√6)/15
    ai[5] = (6.0 + rt6) / 15.0;          // c6 = (6+√6)/15
    ai[6] = (6.0 - rt6) / 15.0;          // c7 = (6-√6)/15
    ai[7] = 2.0 / 3.0;
    ...
    ai[15] = 1.0;                        // 末级节点 c16 = 1
```

### 3.2 PrinceDormand45 —— DP 4(5)，7 级（FSAL）

- **公式**：7 级。节点（`PrinceDormand45.cpp:150-156`）：

$$ c_i=\left[0,\ \tfrac{2}{9},\ \tfrac{1}{3},\ \tfrac{5}{9},\ \tfrac{2}{3},\ 1,\ 1\right] $$

解累加权重（`cj`，`:194-200`，5 阶主解）与嵌入 4 阶解之差（`ee`，`:202-208`，代码直接写 $b-\hat b$ 的展开式）：

$$ b=\left[\tfrac{19}{200},\,0,\,\tfrac{3}{5},\,-\tfrac{243}{400},\,\tfrac{33}{40},\,\tfrac{7}{80},\,0\right],\qquad \hat b=\left[\tfrac{431}{5000},\,0,\,\tfrac{333}{500},\,-\tfrac{7857}{10000},\,\tfrac{957}{1000},\,\tfrac{193}{2000},\,-\tfrac{1}{50}\right] $$

$$ \mathbf{ee}=b-\hat b=\left[\tfrac{19}{200}-\tfrac{431}{5000},\ 0,\ \tfrac{3}{5}-\tfrac{333}{500},\ -\tfrac{243}{400}+\tfrac{7857}{10000},\ \tfrac{33}{40}-\tfrac{957}{1000},\ \tfrac{7}{80}-\tfrac{193}{2000},\ \tfrac{1}{50}\right] $$

级间矩阵 $A$（`bij`，`:158-191`）：

$$ A_2=\left[\tfrac{2}{9},0\right],\quad A_3=\left[\tfrac{1}{12},\tfrac{1}{4},0\right],\quad A_4=\left[\tfrac{55}{324},-\tfrac{25}{108},\tfrac{50}{81},0\right],\quad A_5=\left[\tfrac{83}{330},-\tfrac{13}{22},\tfrac{61}{66},\tfrac{9}{110},0\right],\quad A_6=\left[-\tfrac{19}{28},\tfrac{9}{4},\tfrac{1}{7},-\tfrac{27}{7},\tfrac{22}{7},0\right],\quad A_7=\left[\tfrac{19}{200},0,\tfrac{3}{5},-\tfrac{243}{400},\tfrac{33}{40},\tfrac{7}{80},0\right] $$

- **代码位置**：`src/base/propagator/PrinceDormand45.cpp:143-209`；构造 `RungeKutta(7, 5, "PrinceDormand45")` 于 `:67-68`；来源注释 `:139-140`；头注释 `PrinceDormand45.hpp:57-61`（"fifth order integrator with fourth order error control"）。
- **深度讲解**：
  - **方法与文献**：7 级 5 阶主解 + 4 阶嵌入误差估计（局部外推）。代码注释标 "Prince and Dormand, 1981"（`:139-140`）；该 $c_2=\tfrac29$ 的 7 级嵌入对即 Dormand–Prince 方法族的经典 4(5) 表（与 [MD-00 索引](MD-00-index.md) 中"PD45"的称谓一致）。
  - **FSAL 结构**：$c_7=1$ 且 $A_7=b$——第 7 级恰好在 $t_0+h$、以终态候选为参数重新求一次 $f$（`ki[6] = h·f(t+h, candidate)`），属 **FSAL（First Same As Last）**：该斜率本可作为下一步的第 1 级复用。但基类 `RawStep` 每步从 $i=0$ 重算全部级（§2.1），**未利用 FSAL 省一次右端项求值**；FSAL 的意义保留在表结构层面（$b_7=0$、$\hat b_7=-\tfrac1{50}$ 使第 7 级只贡献误差项）。
  - **代码片段**（`PrinceDormand45.cpp:194-208`，$b$ 与 $b-\hat b$ 的直接表达）：

```cpp
    cj[0] =  19.0 / 200.0;      // b1：5 阶主解权重
    cj[1] =  0.0;
    cj[2] =  3.0 / 5.0;
    cj[3] = -243.0 / 400.0;
    cj[4] =  33.0 / 40.0;
    cj[5] =  7.0 / 80.0;
    cj[6] =  0.0;               // b7=0：FSAL 级不贡献终态
    ee[0] =  19.0 / 200.0  - 431.0 / 5000.0;   // ee = b - b̂，逐项展开
    ...
    ee[6] =                  1.0 / 50.0;       // ee7 = 0 - (-1/50) = 1/50
```

### 3.3 PrinceDormand78 —— PD 7(8)，13 级

- **公式**：13 级。节点（`PrinceDormand78.cpp:148-160`）：

$$ c_i=\left[0,\ \tfrac{1}{18},\ \tfrac{1}{12},\ \tfrac{1}{8},\ \tfrac{5}{16},\ \tfrac{3}{8},\ \tfrac{59}{400},\ \tfrac{93}{200},\ \tfrac{5490023248}{9719169821},\ \tfrac{13}{20},\ \tfrac{1201146811}{1299019798},\ 1,\ 1\right] $$

解累加权重（`cj`，`:254-266`，8 阶主解，末级权重 $\tfrac14$）与嵌入 7 阶解（`cjhat`，`:270-282`，末级权重 0）：

$$ b=\left[\tfrac{14005451}{335480064},\,0,\,0,\,0,\,0,\,-\tfrac{59238493}{1068277825},\,\tfrac{181606767}{758867731},\,\tfrac{561292985}{797845732},\,-\tfrac{1041891430}{1371343529},\,\tfrac{760417239}{1151165299},\,\tfrac{118820643}{751138087},\,-\tfrac{528747749}{2220607170},\,\tfrac{1}{4}\right] $$

$$ \hat b=\left[\tfrac{13451932}{455176623},\,0,\,0,\,0,\,0,\,-\tfrac{808719846}{976000145},\,\tfrac{1757004468}{5645159321},\,\tfrac{656045339}{265891186},\,-\tfrac{3867574721}{1518517206},\,\tfrac{465885868}{322736535},\,\tfrac{53011238}{667516719},\,\tfrac{2}{45},\,0\right] $$

误差系数在代码中由循环生成：$\texttt{ee[i]}=\texttt{cj[i]}-\texttt{cjhat[i]}$（`:284-285`）。级间矩阵 $A$（`bij`，`:162-252`）以分数形式存储，例如：

$$ A_7=\left[\tfrac{29443841}{614563906},0,0,\tfrac{77736538}{692538347},-\tfrac{28693883}{1125000000},\tfrac{23124283}{1800000000},0\right],\quad A_8=\left[\tfrac{16016141}{946692911},0,0,\tfrac{61564180}{158732637},\tfrac{22789713}{633445777},\tfrac{545815736}{2771057229},-\tfrac{180193667}{1043307555},0\right],\ldots $$

其余行（$A_9$–$A_{13}$，`bij[8][0..8]`–`bij[12][0..12]`）为 8~12 项的大整数分数，完整值见 `PrinceDormand78.cpp:199-252`。

- **代码位置**：`src/base/propagator/PrinceDormand78.cpp:141-286`；构造 `RungeKutta(13, 8, "PrinceDormand78")` 于 `:62-63`；来源注释 `:129-139`；头注释 `PrinceDormand78.hpp:50-54`（"eighth order integrator with seventh order error control"）。
- **深度讲解**：
  - **方法与文献**：13 级 8 阶主解（`cj`，含 $b_{13}=\tfrac14$）+ 7 阶嵌入解（`cjhat`，$b_{13}=0$）做误差估计。类名/注释沿用文献记号 "7(8)"（`Prince and Dormand, 1981`，*High order embedded Runge-Kutta formulae*, J. Comput. Appl. Math. 7(1):67-75 中 13 级 7(8) 方法族），GMAT 实际以 8 阶解推进（局部外推），步长控制 `order=8` → `incPower=1/8`、`decPower=1/7`。注释（`:135-139`）说明系数表由 **GSFC 提供、Thinking Systems 于 2002 年 9 月整理**。
  - **误差系数实现方式**：与 RK89/Fehlberg56 直接写差不同，本类先填局部数组 `cjhat[13]`（`:268-282`）再 `ee[i]=cj[i]-cjhat[i]`（`:284-285`）——这是"两套累加系数之差"写法的代表（`RungeKutta.hpp:100-104` 的 $\Delta=\left|\sum(c_j-c_j^*)\,k_j\right|$ 即此）。
  - **节点精度**：$c_9$、$c_{11}$ 用 10 位大整数分数（如 `5490023248/9719169821`）而非小数，保证中间节点时刻与文献一致到机器精度。
  - **代码片段**（`PrinceDormand78.cpp:268-285`）：

```cpp
    Real cjhat[13];                        // 7 阶嵌入解权重（局部数组）
    cjhat[0] = 13451932.0 / 455176623.0;
    ...
    cjhat[11] = 2.0 / 45.0;                // 第 12 级权重 2/45
    cjhat[12] = 0.0;                       // 第 13 级不进入 7 阶解
    for (int i = 0; i < stages; i++)
        ee[i] = cj[i] - cjhat[i];          // 误差系数 = b(8阶) - b̂(7阶)
```

### 3.4 RungeKuttaFehlberg56 —— Fehlberg 5(6)，8 级

- **公式**：8 级。节点（`RungeKuttaFehlberg56.cpp:109-116`）：

$$ c_i=\left[0,\ \tfrac{1}{6},\ \tfrac{4}{15},\ \tfrac{2}{3},\ \tfrac{4}{5},\ 1,\ 0,\ 1\right] $$

解累加权重（`cj`，`:162-169`，6 阶主解）与误差系数（`ee`，`:171-178`）：

$$ b=\left[\tfrac{7}{1408},\,0,\,\tfrac{1125}{2816},\,\tfrac{9}{32},\,\tfrac{125}{768},\,0,\,\tfrac{5}{66},\,\tfrac{5}{66}\right],\qquad \hat b=b-\mathbf{ee}=\left[\tfrac{31}{384},\,0,\,0,\,0,\,0,\,\tfrac{5}{66},\,0,\,0\right] $$

级间矩阵 $A$（`bij`，`:118-160`）：

$$ A_2=\left[\tfrac{1}{6},0\right],\quad A_3=\left[\tfrac{4}{75},\tfrac{16}{75},0\right],\quad A_4=\left[\tfrac{5}{6},-\tfrac{8}{3},\tfrac{5}{2},0\right],\quad A_5=\left[-\tfrac{8}{5},\tfrac{144}{25},-4,\tfrac{16}{25},0\right],\quad A_6=\left[\tfrac{361}{320},-\tfrac{18}{5},\tfrac{407}{128},-\tfrac{11}{80},\tfrac{55}{128},0\right],\quad A_7=\left[-\tfrac{11}{640},0,\tfrac{11}{256},-\tfrac{11}{160},\tfrac{11}{256},0,0\right],\quad A_8=\left[\tfrac{93}{640},-\tfrac{18}{5},\tfrac{803}{256},-\tfrac{11}{160},\tfrac{99}{256},0,1,0\right] $$

- **代码位置**：`src/base/propagator/RungeKuttaFehlberg56.cpp:102-179`；构造 `RungeKutta(8, 6, "RungeKutta56")` 于 `:54-55`（脚本名用 `RungeKutta56`，见 `PropagatorFactory.cpp:98-99`）；来源注释 `:93-100`（*Numerical Algorithms with C*, 1996）；头注释 `RungeKuttaFehlberg56.hpp:58-63`（"sixth order integrator with fifth order error control"）。
- **深度讲解**：
  - **方法与文献**：Fehlberg 系数，8 级、6 阶主解 + 5 阶嵌入误差控制（`order=6` → `incPower=1/6`、`decPower=1/5`）。注释称来源为 *Numerical Algorithms with C* (1996)。类名 "56" 沿用文献记号 5(6)；注意构造函数 doxygen 残留注释写 "Fehlberg's 4(5)"（`:53`），与类文档（`RungeKuttaFehlberg56.hpp:58-63`"sixth order integrator with fifth order error control"）及系数不一致，应以 `SetCoefficients` 注释与系数表为准。
  - **表结构特点**：$c_7=0$——第 7 级仍在 $t_0$ 时刻求值（`ai[6]=0`），其斜率 $k_7$ 不进 $b$ 也不进 $\hat b$，仅作为 $k_8$ 的组合成分（$A_8$ 中 $a_{8,7}=1$）；$c_8=1$ 末级在 $t_0+h$ 求值。$\hat b$ 只含 $k_1$、$k_6$ 两项（权重 $\tfrac{31}{384}$、$\tfrac{5}{66}$），嵌入解极简。
  - **代码片段**（`RungeKuttaFehlberg56.cpp:162-178`）：

```cpp
    cj[0] =  7.0 / 1408.0;       // b1：6 阶主解权重
    cj[1] =  0.0;
    cj[2] =  1125.0 / 2816.0;    // b3 = 1125/2816
    cj[3] =  9.0 /  32.0;        // b4
    cj[4] =  125.0 / 768.0;      // b5
    cj[5] =  0.0;
    cj[6] =  5.0 / 66.0;         // b7 = 5/66
    cj[7] =  5.0 / 66.0;         // b8 = 5/66
    ee[0] =  7.0 / 1408.0 - 31.0 / 384.0;  // ee1 = b1 - b̂1（b̂1 = 31/384）
    ...
    ee[5] = -5.0 / 66.0;         // ee6 = 0 - 5/66
    ee[6] =  5.0 / 66.0;         // ee7 = b7 - 0
    ee[7] =  5.0 / 66.0;         // ee8 = b8 - 0
```

### 3.5 PrinceDormand853 —— HNW DOP853 8(5,3)，12 级（ProductionPropagatorPlugin）

- **公式**：12 级。节点（`PrinceDormand853.cpp:124-144`，十进制存储）：

$$ c_i=[0,\ 0.0526001519587677,\ 0.0789002279381515,\ 0.118350341907227,\ 0.281649658092772,\ \tfrac{1}{3},\ \tfrac{1}{4},\ 0.307692307692307,\ 0.651282051282051,\ 0.6,\ 0.857142857142857,\ 1] $$

解累加权重（`cj`，`:286-303`，8 阶主解）与误差系数（`ee`，`:305-316`）：

$$ b=[0.0542937341165687,\ 0,\ 0,\ 0,\ 0,\ 4.45031289275240,\ 1.89151789931450,\ -5.80120396001058,\ 0.311164366957819,\ -0.152160949662516,\ 0.201365400804030,\ 0.0447106157277725] $$

$$ \mathbf{ee}=[0.0131200449941948,\ 0,\ 0,\ 0,\ 0,\ -1.22515644637620,\ -0.495758949657250,\ 1.66437718245498,\ -0.350328848749973,\ 0.334179118713017,\ 0.0819232064851157,\ -0.0223553078638862] $$

（注意 $\texttt{ee[11]}=-\tfrac12 b_{12}$，即嵌入 5 阶解 $\hat b_{12}=\tfrac32 b_{12}$。）级间矩阵 $A$（`bij`，`:146-284`）为 12 行十进制系数，例如：

$$ A_8=[0.624110958716075,\ 0,\ 0,\ -3.36089262944694,\ -0.868219346841726,\ 27.5920996994467,\ 20.1540675504778,\ -43.4898841810699,\ 0],\quad A_{12}=[2.27331014751653,\ 0,\ 0,\ -10.5344954667372,\ -2.00087205822486,\ -17.9589318631187,\ 27.9488845294199,\ -2.85899827713502,\ -8.87285693353062,\ 12.3605671757943,\ 0.643392746015763,\ 0] $$

- **代码位置**：`plugins/ProductionPropagatorPlugin/src/base/propagator/PrinceDormand853.cpp:117-323`；构造 `RungeKutta(12, 8, "PrinceDormand853")` 于 `:44-48`（`:45` 保留被注释的 16 级原型）；HNW 出处注释 `:135-136`；头注释 `PrinceDormand853.hpp:34-38`。
- **深度讲解**：
  - **方法与文献**：即 Hairer–Norsett–Wanner《Solving Ordinary Differential Equations I》§II.5 的 **DOP853**：8 阶主解推进，误差估计来自嵌入 **5 阶**解（另有 3 阶解专用于刚性检测，本章未存）。代码注释（`:135-136`）明示 "Per Hairer, Norsett and Wanner, ai[11] = 1.0 (eq 5.25b; their C_12 is GMAT's ai[11])"。`order=8` → `incPower=1/8`、`decPower=1/7`。
  - **注意 hpp 注释与实际不符**：`PrinceDormand853.hpp:36-37` 沿用 PD78 的模板文字 "eighth order integrator with seventh order error control"，但实际 `ee` 是 DOP853 相对 **5 阶嵌入解**的误差系数——读代码时应以 `SetCoefficients` 的系数与 `:135` 的注释为准。
  - **16 级残留与稠密输出**：`:138-144`、`:225-284`、`:299-303`、`:318-322` 中 `if (stages == 16)` 分支保留了原始 16 级 DOP853 的稠密输出（interpolant）附加级（$c_{13}=0,\ c_{14}=0.1,\ c_{15}=0.2,\ c_{16}=\tfrac79$ 等），且 `cj[12..15]=ee[12..15]=0`；但构造硬编码 12 级（`:46`），这些分支为死代码——除非改回 16 级，否则稠密输出不可用。
  - **代码片段**（`PrinceDormand853.cpp:124-138`）：

```cpp
    ai[0] = 0.0;
    ai[1] = 0.0526001519587677;          // c2 = 19/361 的小数形式
    ...
    ai[10] = 0.857142857142857;          // c11 = 6/7
    ai[11] = 1.0; //0.0;      // Per Hairer, Norsett and Wanner, ai[11] = 1.0
                              // (eq 5.25b; their C_12 is GMAT's ai[11])
```

---

## 四、Runge-Kutta-Nystrom 二阶方法

### 4.1 RungeKuttaNystrom 基类 —— 二阶方程专用 RK

- **公式**：求解 $\ddot{\mathbf r}=\mathbf g(t,\mathbf r)$（右端项为**加速度**，与速度无关或弱相关，`RungeKuttaNystrom.hpp:53-68` 注释强调这是 Nystrom 方法的必要条件）。级公式（代码 `RungeKuttaNystrom.cpp:385-422`，文献式 `RungeKuttaNystrom.hpp:73-74`）：

$$ \mathbf k_i=\mathbf g\!\left(t_0+c_i h,\ \mathbf r_0+c_i h\,\dot{\mathbf r}_0+h^2\sum_{j=0}^{i-1}a_{ij}\mathbf k_j\right) $$

位置（因变量）与速度（一阶导）分量分开累加（代码 `:424-440`，文献式 `:79-86`）：

$$ \mathbf r(t_0+h)=\mathbf r_0+h\,\dot{\mathbf r}_0+h^2\sum_{i=0}^{s-1} b_i\,\mathbf k_i,\qquad \dot{\mathbf r}(t_0+h)=\dot{\mathbf r}_0+h\sum_{i=0}^{s-1}\dot b_i\,\mathbf k_i $$

误差估计（`EstimateError`，`:479-499`）：位置误差用 $h^2\sum \mathbf{ee}_i\mathbf k_i$，速度误差（`derivativeError==true` 时）用 $h\sum \mathbf{eeDeriv}_i\mathbf k_i$。

- **代码位置**：`src/base/propagator/RungeKuttaNystrom.cpp:82-92`（构造，`:91` 置 `derivativeOrder=2`）、`:165-289`（`Initialize`）、`:379-443`（`RawStep`）、`:479-499`（`EstimateError`）、`:454-457`（`GetPropagatorOrder` 返回 2）；头文件公式 `RungeKuttaNystrom.hpp:70-87`。
- **深度讲解**：
  - **为什么是二阶**：Nystrom 方法直接把 $\ddot r=g(t,r)$ 当作对象，级量 $\mathbf k_i$ 是**加速度**而非一阶导数斜率，因此位置更新含 $h^2$ 因子、速度更新含 $h$ 因子——对"位置+速度"状态天然比把系统降阶成一阶后再 RK 更省右端项求值（每级只求一次 $g$，而一阶化需同时对位置和速度求 $f$）。
  - **状态映射**：`derivativeMap`/`inverseMap` 记录"位置分量 ↔ 速度分量"的索引映射（`GetComponentMap`，`RungeKuttaNystrom.cpp:241`，接口见 `PhysicalModel.hpp:192-193`）；例如 6 维状态 (X,Y,Z,Vx,Vy,Vz) 的映射为 (3,4,5,−1,−1,−1)（`PhysicalModel.cpp:1533-1537` 注释）。级间状态只对因变量组装：`stageState[k] = inState[k] + ai[i]·h·inState[derivativeMap[k]] + h²·Σ bij·ki`（`:388-397`）。
  - **级斜率赋值**：`ki[i][j]=ddt[j]`（二阶导数）仅对因变量分量（`:408-411`）；速度分量位置不存级斜率，仅通过 `inverseMap` 在累加阶段读取（`:434-439`）。`derivativeError` 标志（默认 false，DEP68 置 true）决定速度分量是否参与误差控制。
  - **注意头文件公式笔误**：`RungeKuttaNystrom.hpp:79` 写 $\mathbf r(t_0+h)=\mathbf r_0+\sum c_j\mathbf k_j$ 漏掉了 $h\dot{\mathbf r}_0$ 与 $h^2$ 因子，实际实现见上（`:424-440`）——以代码为准。
  - **代码片段**（`RungeKuttaNystrom.cpp:424-440`，累加阶段）：

```cpp
    // 因变量（位置）分量：r = r0 + h·v0 + h²·Σ b_i·k_i
    memcpy(candidateState, inState, dimension*sizeof(double));
    for (i = 0; i < dimension; i++) {
        if (derivativeMap[i] >= 0) {                 // 位置分量
            candidateState[i] += stepSize * inState[derivativeMap[i]];  // h·v0
            for (j = 0; j < stages; j++) {
                if (cj[j] != 0.0)
                    candidateState[i] += h2 * cj[j] * ki[j][i];         // h²·Σb_i·k_i
            }
        }
        else {                                       // 速度分量：v = v0 + h·Σċ_i·k_i
            for (j = 0; j < stages; j++) {
                if (cdotj[j] != 0.0)
                    candidateState[i] += stepSize * cdotj[j] * ki[j][inverseMap[i]];
            }
        }
    }
```

### 4.2 DormandElMikkawyPrince68 —— DEP 6(8)，9 级

- **公式**：9 级 RKN。节点（`DormandElMikkawyPrince68.cpp:107-115`）：

$$ c_i=\left[0,\ \tfrac{1}{20},\ \tfrac{1}{10},\ \tfrac{3}{10},\ \tfrac{1}{2},\ \tfrac{7}{10},\ \tfrac{9}{10},\ 1,\ 1\right] $$

位置累加权重（`cj`，`:171-179`，8 阶主解）与速度累加权重（`cdotj`，`:183-191`）：

$$ b=\left[\tfrac{223}{7938},\,0,\,\tfrac{1175}{8064},\,\tfrac{925}{6048},\,\tfrac{41}{448},\,\tfrac{925}{14112},\,\tfrac{1175}{72576},\,0,\,0\right],\qquad \dot b=\left[\tfrac{223}{7938},\,0,\,\tfrac{5875}{36288},\,\tfrac{4625}{21168},\,\tfrac{41}{224},\,\tfrac{4625}{21168},\,\tfrac{5875}{36288},\,\tfrac{223}{7938},\,0\right] $$

位置误差系数（`ee`，`:194-202`，6 阶嵌入解之差）与速度误差系数（`eeDeriv`，`:204-212`）：

$$ \mathbf{ee}=\left[\tfrac{223}{7938}-\tfrac{7987313}{109941300},\,0,\,\tfrac{1175}{8064}-\tfrac{1610737}{44674560},\,\tfrac{925}{6048}-\tfrac{10023263}{33505920},\,\tfrac{41}{448}+\tfrac{497221}{12409600},\,\tfrac{925}{14112}-\tfrac{10023263}{78180480},\,\tfrac{1175}{72576}-\tfrac{1610737}{402071040},\,0,\,0\right] $$

$$ \mathbf{eeDeriv}=\left[\tfrac{223}{7938}-\tfrac{7987313}{109941300},\,0,\,\tfrac{5875}{36288}-\tfrac{1610737}{40207104},\,\tfrac{4625}{21168}-\tfrac{10023263}{23454144},\,\tfrac{41}{224}+\tfrac{497221}{6204800},\,\tfrac{4625}{21168}-\tfrac{10023263}{23454144},\,\tfrac{5875}{36288}-\tfrac{1610737}{40207104},\,\tfrac{223}{7938}+\tfrac{4251941}{54970650},\,-\tfrac{3}{20}\right] $$

级间矩阵 $A$（`bij`，`:117-169`）：$A_2=[\tfrac{1}{800},0]$，$A_3=[\tfrac{1}{600},\tfrac{1}{300},0]$，$A_4=[\tfrac{9}{200},-\tfrac{9}{100},\tfrac{9}{100},0]$，$A_5=[-\tfrac{66701}{197352},\tfrac{28325}{32892},-\tfrac{2665}{5482},\tfrac{2170}{24669},0]$，$A_6=[\tfrac{227015747}{304251000},-\tfrac{54897451}{30425100},\tfrac{12942349}{10141700},-\tfrac{9499}{304251},\tfrac{539}{9250},0]$，$A_7=[-\tfrac{1131891597}{901789000},\tfrac{41964921}{12882700},-\tfrac{6663147}{3220675},\tfrac{270954}{644135},-\tfrac{108}{5875},\tfrac{114}{1645},0]$，$A_8=[\tfrac{13836959}{3667458},-\tfrac{17731450}{1833729},\tfrac{1063919505}{156478208},-\tfrac{33213845}{39119552},\tfrac{13335}{28544},-\tfrac{705}{14272},\tfrac{1645}{57088},0]$，$A_9=[\tfrac{223}{7938},0,\tfrac{1175}{8064},\tfrac{925}{6048},\tfrac{41}{448},\tfrac{925}{14112},\tfrac{1175}{72576},0,0]=b$。

- **代码位置**：`src/base/propagator/DormandElMikkawyPrince68.cpp:98-213`（`SetCoefficients`：ai `:107-115`，bij `:117-169`，cj `:171-179`，cdotj `:183-191`，ee `:194-202`，eeDeriv `:204-212`）；构造 `RungeKuttaNystrom(9, 8, "RungeKutta68")` 于 `:52-57`（`:56` 置 `derivativeError=true`）；头注释 `DormandElMikkawyPrince68.hpp:55-61`。
- **深度讲解**：
  - **方法与文献**：头注释（`:55-61`）注明：**Dormand, El-Mikkawy & Prince 1987** 论文的 RKN 6(8) 方法（1991 年有勘误）；9 级、8 阶主解（`order=8` → `incPower=1/8`、`decPower=1/7`）、6 阶嵌入解做误差估计，且**对位置与速度同时误差控制**（`derivativeError=true`）——GMAT 唯一这样的积分器（[CH07](../CH07-propagator.md) 亦注明）。
  - **RKN 表结构约束**：行和满足 $\sum_j a_{ij}=c_i^2/2$（如 $A_2$ 行和 $=\tfrac1{800}=\tfrac{(1/20)^2}{2}$、$A_3$ 行和 $=\tfrac{1}{200}=\tfrac{(1/10)^2}{2}$），位置权行和 $\sum b_i=\tfrac12$、速度权行和 $\sum\dot b_i=1$——RKN 方法的阶条件在代码系数中的体现。$A_9=b$ 且 $c_9=1$：末级在 $t_0+h$ 处对候选位置求一次加速度，但 $b_9=0$、$\dot b_9=0$，该级只经 $\mathbf{eeDeriv}_9=-\tfrac3{20}$ 进入速度误差项（FSAL 风格的残余结构）。
  - **代码片段**（`DormandElMikkawyPrince68.cpp:183-212`，速度权重与双误差系数）：

```cpp
    // 速度累加权重 ċ_i（推进一阶导/速度分量）
    cdotj[0] = 223.0 / 7938.0;
    ...
    cdotj[7] = 223.0 / 7938.0;
    cdotj[8] = 0.0;
    // 位置误差系数：ee = b - b̂（6 阶嵌入解）
    ee[0] = cj[0] - 7987313.0 / 109941300.0;
    ...
    // 速度误差系数：eeDeriv = ċ - ĉ̂
    eeDeriv[0] = cdotj[0] - 7987313.0 / 109941300.0;
    ...
    eeDeriv[8] = cdotj[8] - 3.0 / 20.0;   // 末级加速度只用于速度误差
```

---

## 五、预测-校正多步法

### 5.1 PredictorCorrector 基类 —— 多步法骨架与双阈值步长控制

- **公式**：通用 PECE 流程（预测 → 用预测态求导 → 校正 → 误差估计 → 自适应）。历史导数 $\mathbf f_{n-k}$ 存 `history[k][·]`（滚动缓冲，`PredictorCorrector.hpp:139`），预测/校正权重由派生类 `SetWeights()` 填充。步长控制公式（`AdaptStep`，`PredictorCorrector.cpp:692`）：

$$ h_{\text{new}}=h\left(\frac{\texttt{targetError}}{\texttt{maxError}}\right)^{\texttt{invOrder}},\qquad \texttt{invOrder}=\frac{1}{\texttt{order}}=\frac14\ \text{（ABM）} $$

变步模式：误差过大（$\epsilon>\alpha$）拒绝并取 $h_{\text{new}}$；误差过小（$\epsilon<\texttt{lowerError}$）也调整——放大步长但**每次至多翻倍**（`newStep >= 2h` 时 `stepSize *= 2`，`PredictorCorrector.cpp:755-759`）；固定步模式按 2 的幂缩/放（`:766-792`）。变步后调用 `Reset()` 重建历史（`:794`）。

- **代码位置**：`src/base/propagator/PredictorCorrector.cpp:117-139`（构造：`lowerError=1e-13` `:128`、`targetError=1e-11` `:129`、`invOrder=1/order` `:134`、`tolerance=1e-10` `:138`）、`:269-275`（容差关系校验）、`:418-436`（启动器装配）、`:564-661`（`Step()`）、`:690-795`（`AdaptStep`）；头文件 `PredictorCorrector.hpp:93, :134-165, :176-216`。
- **深度讲解**：
  - **容差语义（P-C 专属）**：P-C 用**三个**阈值：`Accuracy`（`tolerance`，默认 $1\times10^{-10}$）为接受上限，`TargetError`（默认 $1\times10^{-11}$）为步长控制目标，`LowerError`（默认 $1\times10^{-13}$）为"过精度"下限；初始化强制要求 $ \texttt{LowerError}<\texttt{TargetError}<\texttt{Accuracy}$（`:269-275`，且相互至少差一个量级更佳）。与 RK 的单阈值 `Accuracy`（§2.3）不同：P-C 在 $\epsilon<\texttt{lowerError}$ 时**主动放大步长**，避免"过分精确"浪费计算量（`Step()` 中 `:641-644` 的条件 `(maxError > tolerance) || (maxError < lowerError)`）。
  - **多步法启动**：需要 $s$ 个历史导数点，靠内置单步启动器 `starter`（默认 `new RungeKutta89`，`:418-419`）逐点填充；`starter` 继承积分器参数（Accuracy/MinStep/MaxStep）并把类型名改为 "Starter for Predictor-Corrector"（`:428-435`，该字符串被 `RungeKutta::Step` 的有限推力检测排除，`RungeKutta.cpp:343`）。
  - **误差估计约定**：`EstimateError()` 返回负值表示错误（`Integrator.hpp:197-199` 注释），`Step()` 据此拒绝（`PredictorCorrector.cpp:626-627`）。
  - **为什么变步要 Reset**：多步法历史依赖于固定步长网格，步长一旦改变，历史缓冲必须清空并用新步长重新启动（`Reset()`，纯虚 `PredictorCorrector.hpp:216`；ABM 实现见 §5.2）。这与单步 RK"随时可改步长"形成鲜明对比。
  - **代码片段**（`PredictorCorrector.cpp:690-700`）：

```cpp
bool PredictorCorrector::AdaptStep(Real maxError)
{
   Real newStep = stepSize * pow(targetError / maxError, invOrder);  // h' = h(TargetError/ε)^{1/order}
   // 最小步长豁免：|stepSize| == minimumStep 时按 stopIfAccuracyViolated 决定抛错或警告放行
   if (GmatMathUtil::Abs(stepSize) == minimumStep) { ... }
   if (fabs(newStep) < minimumStep) newStep = minimumStep * stepSign;
   if (fabs(newStep) > maximumStep) newStep = maximumStep * stepSign;
   ...
```

### 5.2 AdamsBashforthMoulton —— AB4/AM3 预测-校正

- **公式**：4 阶 Adams-Bashforth 预测 + 4 阶 Adams-Moulton 校正（PECE，1 次校正）。预测（`Predict()`，`AdamsBashforthMoulton.cpp:231-250`；文献式 `AdamsBashforthMoulton.hpp:67-68`）：

$$ \mathbf r^{(P)}_{n+1}=\mathbf r_n+\frac{h}{24}\left[55\,\mathbf f_n-59\,\mathbf f_{n-1}+37\,\mathbf f_{n-2}-9\,\mathbf f_{n-3}\right],\qquad \texttt{pweights}=\tfrac1{24}[-9,\ 37,\ -59,\ 55] $$

校正（`Correct()`，`:288-297`；文献式 `:74-75`）：

$$ \mathbf r^{(C)}_{n+1}=\mathbf r_n+\frac{h}{24}\left[9\,\mathbf f^{(P)}_{n+1}+19\,\mathbf f_n-5\,\mathbf f_{n-1}+1\,\mathbf f_{n-2}\right],\qquad \texttt{cweights}=\tfrac1{24}[1,\ -5,\ 19,\ 9] $$

误差估计（`EstimateError`，`:330-340`；文献式 `:79`，Bate–Mueller–White pp. 415-417）：

$$ \mathrm{EE}_i=\frac{19}{270}\left|r^{(C)}_i(t+h)-r^{(P)}_i(t+h)\right|,\qquad \texttt{eeFactor}=19/270 $$

- **代码位置**：`src/base/propagator/AdamsBashforthMoulton.cpp:68-72`（构造：`PredictorCorrector(4,4,...)`、`eeFactor=19.0/270.0`、`starter=new RungeKutta89`）、`:146-162`（`SetWeights`）、`:173-213`（`FireStartupStep`）、`:224-269`（`Predict`）、`:280-307`（`Correct`）、`:330-340`（`EstimateError`）、`:355-366`（`Reset`）；公式注释 `AdamsBashforthMoulton.hpp:63-79`。
- **深度讲解**：
  - **方法背景**：经典 4 阶 PECE。预测用 4 点外插（AB4：插值多项式在区间外推），校正用 3 点 + 新点内插（AM3）；校正阶与预测阶同为 4，但**隐式校正的误差常数更小**，一次校正即可把局部误差从预测阶提升到校正阶（PECE 惯例）。
  - **历史滚动与权重对应**：`Predict()` 先把 `history[0..2]←history[1..3]` 滚动，最新导数 `f(t_n)` 写入 `history[3]`（`:238-240`），于是 `history[0..3] = f(t−3h),…,f(t_n)`，与 `pweights[0..3]={−9,37,−59,55}/24` 逐位相乘（`:243-250`）即上式。`Correct()` 用 `physicalModel->GetDerivatives(predictorState, stepSize)` 求 $f^{(P)}_{n+1}$（`:288`），`cweights[3]=9/24` 乘新点、`cweights[0..2]={1,−5,19}/24` 乘 `history[1..3]`（`:290-297`）。
  - **误差常数 19/270**：4 阶 AB 预测器与 AM 校正器的局部截断误差主项系数分别为 $251/720$ 与 $-19/720$（均乘 $h^5\,y^{(5)}$），两者之差为 $270/720=\tfrac38$，故 $\lvert y^{(C)}-y^{(P)}\rvert\approx\tfrac38 h^5y^{(5)}$，代入校正器误差 $-19/720\,h^5y^{(5)}$ 即得估计式 $EE=\tfrac{19}{270}\lvert y^{(C)}-y^{(P)}\rvert$（Bate, Mueller & White 415-417 页，hpp `:61` 引用），代码以 `eeFactor` 固化（`:70`）。
  - **启动（3 步）**：`FireStartupStep()` 调 `starter->Step(stepSize)`（RK89 误差受控推进，`:182`）；`Step()` 主循环在启动期每轮先把当前导数写入 `history[startupCount+1]`（首轮额外写 `history[0]`，`PredictorCorrector.cpp:583-601`），三轮后 `startupComplete=true`（`AdamsBashforthMoulton.cpp:194-196`），此后 `maxError=0` 使 RK 步的误差检查被跳过（"assume it is good enough for startup purposes"，`PredictorCorrector.cpp:611-613`）。
  - **代码片段**（`AdamsBashforthMoulton.cpp:243-250` 与 `:334-336`）：

```cpp
   for (j = 0; j < dimension; j++)
   {
      predictorState[j] = inState[j];                 // 从当前状态出发
      for (i = 0; i < stepCount; i++)
      {
         predictorState[j] += stepSize * pweights[i] * history[i][j];  // + h·Σp_i·f_{n-i}
      }
   }
   ...
   for (i = 0; i < dimension; i++)
      errorEstimates[i] = fabs(eeFactor*(correctorState[i]-predictorState[i]));  // (19/270)|C−P|
```

### 5.3 Cowell —— 未实现外壳

- **公式**：无（未实现）。头注释（`Cowell.hpp:22-25, :34-39`）与源注释（`Cowell.cpp:22-25`）明示 "This code is a shell for the Cowell integrator. The integrator is not currently implemented." 构造甚至以字面 `?` 占位（`Cowell.cpp:52`：`PredictorCorrector(?, ?, "Cowell", nomme)`，不可编译，故工厂中 `Cowell` 注册被注释，`PropagatorFactory.cpp:102-103, :133`）。
- **代码位置**：`src/base/propagator/Cowell.cpp:51-55`（构造）、`:126-138`（`Initialize`，分配 `estimatedState` 后置 `initialized=false`）、`:149-157`（`Step(Real dt)` 空转返回 true）、`:192-198`（`Step()` 空转）、`:225-228`（`EstimateError` 直接归一化空数组）、`:240-243`（`AdaptStep` 恒返回 true）。
- **深度讲解**：
  - **设计意图**：`Step()` 的文档注释（`:159-191`）描述了完整的 Cowell 方案——中点法外推 + 多项式外推 + 误差估计 + 步长自适应的 9 步流程（与 Bulirsch–Stoer 同构），但实现全部为空壳。`Cowell.hpp:41` 声明 `class Cowell : public PredictorCorrector`，预留了"位置-加速度二阶多步法"的落点。
  - **现状结论**：GMAT 中没有可用的 Cowell 积分器；脚本中创建 `Cowell` 会因工厂未注册而失败。文档覆盖到此为止（公式级解析无对象），细节同 [CH07](../CH07-propagator.md) §2.1 所述。
  - **代码片段**（`Cowell.cpp:192-198`）：

```cpp
bool Cowell::Step(void)
{
    if (!initialized)
        return false;
    return true;     // 空壳：不做任何状态推进
}
```

---

## 六、公式索引表

| 公式 | 文件:行 | 所属类 |
|---|---|---|
| RK 级公式 $k_i=h f(t_0+c_i h,\ r_0+\sum a_{ij}k_j)$ | src/base/propagator/RungeKutta.hpp:78-79；RungeKutta.cpp:527-578 | RungeKutta |
| RK 终态 $r(t_0+h)=r_0+\sum b_i k_i$ | src/base/propagator/RungeKutta.hpp:86；RungeKutta.cpp:581-588 | RungeKutta |
| 嵌入对误差 $\Delta=\sum (b_i-\hat b_i)k_i$，`ee=b−b̂` | src/base/propagator/RungeKutta.hpp:94-104；RungeKutta.cpp:679-694 | RungeKutta |
| 步长缩小 $h'=\sigma h(\alpha/\epsilon)^{1/(m-1)}$ | src/base/propagator/RungeKutta.hpp:114-115；RungeKutta.cpp:750 | RungeKutta |
| 步长放大 $h'=\sigma h(\alpha/\epsilon)^{1/m}$，$\sigma=0.9$ | src/base/propagator/RungeKutta.hpp:127-128；RungeKutta.cpp:761 | RungeKutta |
| 相对误差归一化 $\epsilon_i=\max_i\|\mathrm{EE}_i/\Delta_i\|$（阈值 0.10） | src/base/forcemodel/PhysicalModel.cpp:1496-1512（:188） | PhysicalModel |
| Verner 8(9) 节点 $c_i$（16 级，$\rho=\sqrt6$） | src/base/propagator/RungeKutta89.cpp:161-176 | RungeKutta89 |
| Verner 8(9) 解权 $b$（9 阶主解） | src/base/propagator/RungeKutta89.cpp:331-346 | RungeKutta89 |
| Verner 8(9) 误差系数 $ee=b-\hat b$（8 阶嵌入） | src/base/propagator/RungeKutta89.cpp:348-363 | RungeKutta89 |
| DP 4(5) 节点 $c_i$（7 级，FSAL） | src/base/propagator/PrinceDormand45.cpp:150-156 | PrinceDormand45 |
| DP 4(5) 解权 $b$ 与 $b-\hat b$（5 阶主解/4 阶嵌入） | src/base/propagator/PrinceDormand45.cpp:194-208 | PrinceDormand45 |
| PD 7(8) 节点 $c_i$（13 级） | src/base/propagator/PrinceDormand78.cpp:148-160 | PrinceDormand78 |
| PD 7(8) 解权 $b$（8 阶，$b_{13}=1/4$）与 $\hat b$（7 阶） | src/base/propagator/PrinceDormand78.cpp:254-282 | PrinceDormand78 |
| PD 7(8) 误差系数 $ee_i=c_i-\hat c_i$（循环相减） | src/base/propagator/PrinceDormand78.cpp:284-285 | PrinceDormand78 |
| Fehlberg 5(6) 节点 $c_i$（8 级，含 $c_7=0$） | src/base/propagator/RungeKuttaFehlberg56.cpp:109-116 | RungeKuttaFehlberg56 |
| Fehlberg 5(6) 解权 $b$（6 阶）与 $ee=b-\hat b$（5 阶嵌入） | src/base/propagator/RungeKuttaFehlberg56.cpp:162-178 | RungeKuttaFehlberg56 |
| RKN 级公式 $k_i=g(t_0+c_i h,\ r_0+c_i h\dot r_0+h^2\sum a_{ij}k_j)$ | src/base/propagator/RungeKuttaNystrom.hpp:73-74；RungeKuttaNystrom.cpp:385-422 | RungeKuttaNystrom |
| RKN 位置 $r=r_0+h\dot r_0+h^2\sum b_i k_i$ / 速度 $\dot r=\dot r_0+h\sum\dot b_i k_i$ | src/base/propagator/RungeKuttaNystrom.cpp:424-440 | RungeKuttaNystrom |
| RKN 误差 $h^2\sum ee_i k_i$（位置）、$h\sum eeDeriv_i k_i$（速度） | src/base/propagator/RungeKuttaNystrom.cpp:479-499 | RungeKuttaNystrom |
| DEP 6(8) 节点 $c_i$（9 级） | src/base/propagator/DormandElMikkawyPrince68.cpp:107-115 | DormandElMikkawyPrince68 |
| DEP 6(8) 位置权 $b$ / 速度权 $\dot b$ | src/base/propagator/DormandElMikkawyPrince68.cpp:171-191 | DormandElMikkawyPrince68 |
| DEP 6(8) 位置误差 $ee$ / 速度误差 $eeDeriv$（6 阶嵌入） | src/base/propagator/DormandElMikkawyPrince68.cpp:194-212 | DormandElMikkawyPrince68 |
| P-C 步长 $h'=h(\texttt{TargetError}/\epsilon)^{1/\texttt{order}}$ | src/base/propagator/PredictorCorrector.cpp:692 | PredictorCorrector |
| P-C 容差链 $\texttt{LowerError}<\texttt{TargetError}<\texttt{Accuracy}$ | src/base/propagator/PredictorCorrector.cpp:269-275 | PredictorCorrector |
| AB4 预测 $r^{(P)}=r_n+\frac h{24}(55f_n-59f_{n-1}+37f_{n-2}-9f_{n-3})$ | src/base/propagator/AdamsBashforthMoulton.hpp:67-68；AdamsBashforthMoulton.cpp:151-154, :243-250 | AdamsBashforthMoulton |
| AM3 校正 $r^{(C)}=r_n+\frac h{24}(9f^{(P)}_{n+1}+19f_n-5f_{n-1}+f_{n-2})$ | src/base/propagator/AdamsBashforthMoulton.hpp:74-75；AdamsBashforthMoulton.cpp:156-159, :288-297 | AdamsBashforthMoulton |
| ABM 误差 $\mathrm{EE}=\frac{19}{270}\lvert r^{(C)}-r^{(P)}\rvert$ | src/base/propagator/AdamsBashforthMoulton.hpp:79；AdamsBashforthMoulton.cpp:70, :330-340 | AdamsBashforthMoulton |
| ABM 启动（RK89 3 步填充历史） | src/base/propagator/AdamsBashforthMoulton.cpp:173-213；PredictorCorrector.cpp:583-614 | AdamsBashforthMoulton / PredictorCorrector |
| Cowell（未实现，无公式） | src/base/propagator/Cowell.cpp:192-198, :52 | Cowell |
| DOP853 节点 $c_i$（12 级，HNW eq 5.25b） | plugins/ProductionPropagatorPlugin/src/base/propagator/PrinceDormand853.cpp:124-144 | PrinceDormand853 |
| DOP853 解权 $b$（8 阶主解） | plugins/ProductionPropagatorPlugin/src/base/propagator/PrinceDormand853.cpp:286-303 | PrinceDormand853 |
| DOP853 误差系数 $ee=b-\hat b$（5 阶嵌入） | plugins/ProductionPropagatorPlugin/src/base/propagator/PrinceDormand853.cpp:305-316 | PrinceDormand853 |
