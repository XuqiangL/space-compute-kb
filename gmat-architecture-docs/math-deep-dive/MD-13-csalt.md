# 第13章 CSALT 最优控制配点数学

本章范围：`src/csalt/src/collutils/` 的隐式 Runge-Kutta（IRK）配点一族（`ImplicitRungeKutta` 基类、`LobattoIIIA_2Order/4HSOrder/4Order/6Order/8Order/Separated` 六个 Butcher 表实现）、缺陷约束组装层（`NLPFuncUtil_Coll` / `NLPFuncUtil_ImplicitRK` / `NLPFuncUtilRadau` / `NLPFunctionData`）、`executive/` 的离散化装配（`ImplicitRKPhase` / `RadauPhase`）、以及 `util/` 的配点数学工具（`LobattoIIIaMathUtil`、`RadauMathUtil`、`BaryLagrangeInterpolator`）、稀疏矩阵（`SparseMatrixUtil`）与缩放工具（`ScaleUtility`、`ScalingUtility`）；另含 SNOPT 接口（`SnoptOptimizer` / `SNOPTFunctionWrapper`）的数学形式。共深入 20 个类/工具，覆盖约 19 个源文件。

> 术语、继承体系与装配流程与 [第15章](../CH15-csalt-interop-tests.md) 保持一致：本章只讲"配点公式本身"，不重复 CSALT 工程结构与测试体系。本章所有行号均经 read 逐行核实，公式全部从代码字面数值提炼，不凭记忆。

## 一、数学背景：直接配点法与三种正交网格

CSALT 是**直接法（配点/转写，transcription）最优控制求解器**：不求解两点边值问题（间接法 / 打靶法），而是把连续最优控制问题离散成有限维 NLP 交给稀疏 SQP 求解器（SNOPT）。连续问题的标准形式（Betts 记号）：

$$
\begin{aligned}
&\min J = \phi(x(t_0),x(t_f),t_0,t_f,s) + \int_{t_0}^{t_f} g(x,u,t,s)\,dt \\
&\text{s.t.}\quad \dot{x} = f(x,u,t,s),\qquad x(t_0)=x_0,\\
&\qquad\quad c_L \le c(x,u,t,s) \le c_U
\end{aligned}
$$

其中 $x\in\mathbb{R}^{n_x}$ 状态、$u\in\mathbb{R}^{n_u}$ 控制、$s$ 静态参数。直接配点法把 $t\in[t_0,t_f]$ 划成若干网格区间，在每个区间内用**多项式插值**近似状态/控制，把微分方程 $ \dot{x}=f $ 替换为代数**缺陷约束（defect constraints）** $\zeta_i=0$，积分代价用**求积公式**近似——于是无限维问题变成有限维 NLP。

CSALT 使用两类三种网格（区别在节点如何取、是否含端点）：

| 网格 | 节点定义（$\tau\in[-1,1]$ 或 $[0,1]$） | 含端点 | CSALT 用场 |
|---|---|---|---|
| LGL（Legendre-Gauss-**Lobatto**） | $(1-\tau^2)\,P'_{N-1}(\tau)=0$ 的根 | 两端都含 | IRK 阶段时间 $\rho_i$（`RungeKutta4/6/8`） |
| LGR（Legendre-Gauss-**Radau**） | $P_N(\tau)+P_{N+1}(\tau)=0$ 的根 | 只含左端 $-1$ | `RadauPhase` / `NLPFuncUtilRadau` |
| LG（Legendre-**Gauss**） | $P_N(\tau)=0$ 的根 | 都不含 | 仅背景对比，CSALT 未用 |

其中 $P_n$ 是 $n$ 阶 Legendre 多项式，满足三项递推 $P_{k+1}(x)=\frac{(2k+1)xP_k(x)-kP_{k-1}(x)}{k+1}$（该递推直接出现在 `RadauMathUtil.cpp` 的节点迭代中，见 3.2 节）。

CSALT 对"离散点"有一套统一簿记，定义在 `NLPFuncUtil_ImplicitRK.hpp` 头注释（第 39~51 行）：`|` 是 mesh/step 点（积分步端点），`x` 是内部 stage 点；`numSteps = numMeshPoints - 1`，总点数 `= numSteps*(numStages+1) + 1`。例如 6 阶 IRK、3 步：`MeshIdx 1 1 1 2 2 2 3 3 3 4`、`StageIdx 0 1 2 0 1 2 0 1 2 0`、`PointIdx 1..10`。

## 二、Butcher 表一族：ImplicitRungeKutta 基类与 LobattoIIIA_*

### ImplicitRungeKutta（隐式 RK 配点抽象基类：Butcher 表存储与依赖矩阵）

- **公式**：Butcher 表三元组 $(\rho,\Sigma,\beta)$ 定义为阶段时间 $\rho_i$、系数矩阵 $\Sigma_{ij}$、求积权重 $\beta_j$；隐式 RK 步的**分离形式缺陷约束**为

$$
\zeta_i \;=\; \sum_{j=0}^{S} A_{ij}\,y_j \;-\; h\sum_{j=0}^{S}\Sigma_{ij}\,f_j \;=\; 0,\qquad i=1,\dots,S
$$

其中 $S$ 为阶段数，$h$ 为有量纲步长，$y_0$ 为步首 mesh 点状态、$y_S$ 为步末 mesh 点状态（末行 $\Sigma_{Sj}=\beta_j$）。代码中系数被拆成"状态依赖阵" $A$（`paramDepArray`，含 $\pm1$）与"函数依赖阵" $B$（`funcConstArray=-Σ$`，乘步长后取负）：

$$
\zeta = A\,Z + B\,Q,\qquad B_{ij}=h\,\Sigma_{ij},\quad Q_j=-\Delta T\,f_j
$$

（$Q$ 即 `FillDynamicDefectConMatrices` 里填充的 $-\Delta T f$，见 4.3 节；两式联立即得上面的 $\zeta_i$。）

- **代码位置**：
  - `src/csalt/src/collutils/ImplicitRungeKutta.hpp:91-95`（`rhoVec/sigmaMatrix/betaVec` 成员）、`:100-103`（`paramDepArray/funcConstArray`）、`:74-76`（`GetDependencyChunk` 声明）、`:82-86`（纯虚 `InitializeData/LoadButcherTable/Clone`）
  - `src/csalt/src/collutils/ImplicitRungeKutta.cpp:389-432`（`GetDependencyChunk`：按 `defectIdx/pointIdx` 取出对角块）、`:442-466`（`ComputeDependencies`：`patternA=paramDepArray`、`patternB=funcConstArray`）、`:480-514`（`ComputeAandB`：把标量依赖按 `numVars` 复制成块对角阵）

- **深度讲解**：基类不实现任何具体方法阶，只负责"Butcher 表的载体 + 依赖抽取"。`GetDependencyChunk(defectIdx, pointIdx, numVars, aChunk, bChunk)` 的核心是第 410~425 行：把 `patternAMat(defectIdx, pointIdx)` 这一个标量放到 $n_x\times n_x$ 对角块上（`rowIdx==colIdx` 时赋值，否则置零），即假定**所有状态分量共享同一套缺陷系数**——这正是"分离形式（Separated form）"IRK 的关键约定：缺陷只把每个状态分量各自当作标量方程处理。`ComputeAandB`（第 480~514 行）做同样的块复制，把整个步的所有缺陷/点一次性铺成全局稀疏块的模板。子类只需实现 `LoadButcherTable()`（填 $\rho,\Sigma,\beta$）与 `InitializeData()`（据表填 `numDefectCons`、`numPointsPerStep`、`stageTimes`、`paramDepArray`、`funcConstArray`），构造时依次调用 `LoadButcherTable → InitializeData → ComputeDependencies`（例如 `LobattoIIIA_4Order.cpp:47-54`）。

```cpp
// ImplicitRungeKutta.cpp:410-425（GetDependencyChunk 的填块主体）
for (Integer rowIdx = 0; rowIdx < numVars; rowIdx++)
{
   for (Integer colIdx = 0; colIdx < numVars; colIdx++)
   {
      if (rowIdx == colIdx)
      {
         // 对角块上放入模式矩阵的标量系数：
         // patternA=paramDepArray（状态 ±1 系数），patternB=funcConstArray（=-Σ）
         aChunk(rowIdx, colIdx) = patternAMat(defectIdx, pointIdx);
         bChunk(rowIdx, colIdx) = patternBMat(defectIdx, pointIdx);
      }
      else
      {
         aChunk(rowIdx, colIdx) = 0.0;   // 非对角恒为零：缺陷按状态分量解耦
         bChunk(rowIdx, colIdx) = 0.0;
      }
   }
}
```

### LobattoIIIASeparated（分离形式 IRK 的中间基类）

- **公式**：分离形式把"步内函数值向量"按状态-点双重索引重排：$\hat{f}= \Delta T\cdot[f_0^T\ f_1^T\ \cdots\ f_S^T]^T$，即把每个 (点, 状态) 的动力学值乘上有量纲步长后压成列向量——`GetFuncVecFromArray` 实现 $ \hat{f}_{\,n_x\cdot j+i} = \Delta T\, f_{ij} $（$i$ 状态、$j$ 点）。类本身只持有一个布尔标志 `isSeparated`（默认 `false`，构造时置位）。

- **代码位置**：`src/csalt/src/collutils/LobattoIIIASeparated.cpp:46-51`（构造：`isSeparated(false)`）、`:111-114`（`GetIsSeparated`）、`:128-140`（`GetFuncVecFromArray`：把 `Rmatrix funcArray` 按列压成向量并乘 $\Delta T$）

- **深度讲解**：六个 `LobattoIIIA_*Order` 全部继承自本类（如 `LobattoIIIA_4Order.cpp:47-48` `: LobattoIIIASeparated()`），"Separated" 指缺陷公式把状态与动力学**分离**成 A 阵与 B 阵两项（见 `NLPFuncUtil_ImplicitRK.hpp:29-31` 头注释 "using implicite Runge Kutta methods of the Separated form"）。`GetFuncVecFromArray` 的逐元素乘积 `deltaT*funcArray(stateIdx, funcIdx)` 说明动力学列被按"状态优先"排列，与 `DecisionVector`（Betts 排布）里状态块的组织一致，方便 `NLPFuncUtil_ImplicitRK` 直接把 `FunctionOutputData` 的值灌进 B·Q 的 Q 向量。该类的存在使六个具体阶次只写表、不写装配逻辑。

### LobattoIIIA_2Order（梯形公式，S=1）

- **公式**：Butcher 表（Betts 书 S=1 表）：

$$
\rho = \begin{pmatrix}0\\1\end{pmatrix},\qquad
\Sigma = \begin{pmatrix}0&0\\ \tfrac12&\tfrac12\end{pmatrix},\qquad
\beta = \begin{pmatrix}\tfrac12\\ \tfrac12\end{pmatrix}
$$

依赖阵 $A=[-1\ \ 1]$、$-\Sigma$ 末行 $\Rightarrow$ 缺陷约束为梯形公式：

$$
\zeta = -y_0 + y_1 - \frac{h}{2}\bigl(f_0 + f_1\bigr) = 0
\;\Longleftrightarrow\;
y_1 = y_0 + \frac{h}{2}\bigl(f(t_0,y_0,u_0) + f(t_1,y_1,u_1)\bigr)
$$

- **代码位置**：`src/csalt/src/collutils/LobattoIIIA_2Order.cpp:110-131`（`InitializeData`：`numDefectCons=1`、`numPointsPerStep=2`、`paramDepArray=[-1,1]`、`funcConstArray=-σ(1,:)`）、`:141-167`（`LoadButcherTable`：$\rho=(0,1)$、$\beta=(1/2,1/2)$、`sigmaMatrix(1,:)=(1/2,1/2)`）

- **深度讲解**：2 阶即**隐式梯形法**（`SetButcherTable` 里对应字符串 `"Trapezoid"`，见 `NLPFuncUtil_ImplicitRK.cpp:590-594`）。阶段时间 $\rho=(0,1)$ 只含两个 mesh 端点、无内部 stage，故 `InitializeData` 里 `numStagePointsPerMesh = 0`（第 128 行）。`sigmaMatrix` 第 0 行保持全零（`LoadButcherTable` 只填第 1 行），对应 $\rho_0=0$ 处"阶段即初值"的 Lobatto 结构。缺陷只有 1 条（每步 1 个方程），全局缺陷约束数 `= n_x·(numMeshPoints−1)`。

```cpp
// LobattoIIIA_2Order.cpp:156-161（LoadButcherTable 核心数值）
// The beta matrix
sigmaMatrix.SetSize(2, 2);
// Row 2 —— 只填第 1 行；第 0 行对应 ρ=0 的平凡阶段，保持全零
sigmaMatrix(1, 0) = 1.0 / 2.0;   // σ_10 = 1/2：f_0 的权重
sigmaMatrix(1, 1) = 1.0 / 2.0;   // σ_11 = 1/2：f_1 的权重
```

### LobattoIIIA_4Order（4 阶 Lobatto IIIA，Simpson 1/3，S=2）

- **公式**：

$$
\rho = \begin{pmatrix}0\\ \tfrac12\\ 1\end{pmatrix},\quad
\beta = \begin{pmatrix}\tfrac16\\ \tfrac46\\ \tfrac16\end{pmatrix},\quad
\Sigma = \begin{pmatrix}0&0&0\\ \tfrac{5}{24}&\tfrac{1}{3}&-\tfrac{1}{24}\\ \tfrac16&\tfrac46&\tfrac16\end{pmatrix},\quad
A = \begin{pmatrix}-1&1&0\\ -1&0&1\end{pmatrix}
$$

缺陷约束（阶段方程 + 步方程）：

$$
\zeta_1 = -y_0 + y_1 - h\Bigl(\tfrac{5}{24}f_0 + \tfrac{1}{3}f_1 - \tfrac{1}{24}f_2\Bigr) = 0
$$

$$
\zeta_2 = -y_0 + y_2 - \frac{h}{6}\bigl(f_0 + 4f_1 + f_2\bigr) = 0
$$

- **代码位置**：`src/csalt/src/collutils/LobattoIIIA_4Order.cpp:111-141`（`InitializeData`：`numDefectCons=2`、`numPointsPerStep=3`、`paramDepArray` 第 0 行 `[-1,1,0]`、第 1 行 `[-1,0,1]`、`funcConstArray` 第 0 行 `-σ(1,:)`、第 1 行 `-β`）、`:151-184`（`LoadButcherTable`：$\rho=(0,0.5,1)$、$\beta=(1/6,4/6,1/6)$、`σ(1,:)=(5/24,1/3,-1/24)`、`σ(2,:)=β$）

- **深度讲解**：这是 `SetButcherTable` 中 `"RungeKutta4"` 对应的方法（`NLPFuncUtil_ImplicitRK.cpp:581-584`）。`InitializeData` 中依赖阵的构造规律值得注意：第 $i$ 条缺陷的 $A$ 行 = `[-1, 0.., 1 在第 i 列, 0..]`，即"**每条缺陷都锚定步首状态 $y_0$（系数 −1），并锚定一个"目标状态"（内部 stage $y_i$ 或步末 $y_2$，系数 +1）**"。`funcConstArray` 第 0 行取 $\Sigma$ 第 1 行（内部 stage 点 $\rho_1=1/2$ 的求积系数），第 1 行取 $\beta$（步末点的求积系数）。于是 $\zeta_1$ 在 $\rho_1$ 处配点（隐式阶段方程），$\zeta_2$ 是整步的 Simpson 求积（步方程）。配合 `NLPFuncUtil_ImplicitRK::FillDynamicDefectConMatrices` 的 $Q=-\Delta T f$ 约定，最终实现 $y_1 = y_0 + h(\tfrac{5}{24}f_0+\tfrac{1}{3}f_1-\tfrac{1}{24}f_2)$ 与 $y_2 = y_0 + \tfrac{h}{6}(f_0+4f_1+f_2)$——标准的 4 阶 Lobatto IIIA（含 Simpson 1/3 步）。`numStagePointsPerMesh=1`（第 138 行）表示每网格区间有 1 个内部 stage。

```cpp
// LobattoIIIA_4Order.cpp:121-136（InitializeData 的依赖阵装配）
paramDepArray.SetSize(2, 3);
paramDepArray(0, 0) = -1;   // 缺陷0：步首状态 y_0 系数 -1
paramDepArray(1, 0) = -1;   // 缺陷1：同样锚定 y_0
paramDepArray(0, 1) = 1;    // 缺陷0 目标 = 内部 stage y_1
paramDepArray(1, 2) = 1;    // 缺陷1 目标 = 步末 mesh 状态 y_2
// 函数依赖阵：-Σ 与 -β（乘步长后即 h·Σ 与 h·β，见 4.3 节 B 阵）
funcConstArray(0, 0) = -sigmaMatrix(1, 0);  // -5/24
funcConstArray(0, 1) = -sigmaMatrix(1, 1);  // -1/3
funcConstArray(0, 2) = -sigmaMatrix(1, 2);  // +1/24
funcConstArray(1, 0) = -betaVec(0);         // -1/6
funcConstArray(1, 1) = -betaVec(1);         // -4/6
funcConstArray(1, 2) = -betaVec(2);         // -1/6
```

### LobattoIIIA_4HSOrder（Hermite-Simpson，S=2）

- **公式**：$\rho,\beta,\Sigma$ 与 4 阶完全相同，但缺陷公式改为 Hermite-Simpson 的"中点压缩"形式：

$$
A = \begin{pmatrix}-\tfrac12 & 1 & -\tfrac12\\ -1 & 0 & 1\end{pmatrix},\qquad
-\text{funcConstArray 第0行} = \begin{pmatrix}\tfrac18 & 0 & -\tfrac18\end{pmatrix}
$$

$$
\zeta_0 = -\tfrac12 y_0 + y_1 - \tfrac12 y_2 - \frac{h}{8}\bigl(f_0 - f_2\bigr) = 0
\;\Longleftrightarrow\;
y_1 = \frac{y_0+y_2}{2} + \frac{h}{8}\bigl(f_0 - f_2\bigr)
$$

$$
\zeta_1 = -y_0 + y_2 - \frac{h}{6}\bigl(f_0 + 4f_1 + f_2\bigr) = 0
$$

- **代码位置**：`src/csalt/src/collutils/LobattoIIIA_4HSOrder.cpp:111-145`（`InitializeData`：`paramDepArray` 第 0 行 `[-1/2,1,-1/2]`、第 1 行 `[-1,0,1]`；`funcConstArray` 第 0 行 `[-1/8,0,1/8]`、第 1 行 `-β`）、`:155-188`（`LoadButcherTable`：同 4 阶表）

- **深度讲解**：`SetButcherTable` 中 `"HermiteSimpson"` 对应本类（`NLPFuncUtil_ImplicitRK.cpp:585-589`）。与 `LobattoIIIA_4Order` 的关键差异在缺陷 0：$A$ 行从 $[-1,1,0]$ 变成 $[-\tfrac12,1,-\tfrac12]$，函数系数从 $-σ(1,:)$ 变成 $[-\tfrac18,0,\tfrac18]$。这两处同时改动，得到的是 Betts 书中的 **Hermite-Simpson 压缩形式**：中间点 $y_1$ 不再由隐式阶段方程决定，而是被"中点 + 端部导数修正"显式表达——这正是把三次 Hermite 插值多项式在 $t_{k+1/2}$ 求值得到的恒等式：

$$
y_{k+\tfrac12} = \frac{y_k + y_{k+1}}{2} + \frac{h}{8}\bigl(f_k - f_{k+1}\bigr)
$$

而 $\zeta_1$ 仍是整步 Simpson 求积。注意该中点关系**不含 $f_1$**（$\Sigma$ 第 1 行在代码里根本没被使用），所以 Hermite-Simpson 的缺陷耦合更稀疏：每条缺陷只依赖 $y_0,y_1,y_2$ 与 $f_0,f_2$（或 $f_0,f_1,f_2$），雅可比带宽更小。

```cpp
// LobattoIIIA_4HSOrder.cpp:122-136（Hermite-Simpson 的压缩缺陷系数）
paramDepArray(0, 0) = -1.0/2.0;  // 中点缺陷：y_0 系数 -1/2
paramDepArray(1, 0) = -1.0;      // 步缺陷  ：y_0 系数 -1
paramDepArray(0, 1) = 1.0;       // 中点缺陷：y_1 系数 +1
paramDepArray(1, 1) = 0.0;       // 步缺陷  ：不含 y_1（Simpson 只锚定端点）
paramDepArray(0, 2) = -1.0/2.0;  // 中点缺陷：y_2 系数 -1/2
paramDepArray(1, 2) = 1.0;       // 步缺陷  ：y_2 系数 +1
// 中点缺陷的函数系数：[-1/8, 0, 1/8] → B 阵后为 h·[1/8, 0, -1/8]
funcConstArray(0, 0) = -1.0 / 8.0;   // f_0 系数
funcConstArray(0, 1) = 0.0;          // 中点缺陷不含 f_1
funcConstArray(0, 2) = 1.0 / 8.0;    // f_2 系数（符号相反）
```

### LobattoIIIA_6Order（6 阶 Lobatto IIIA，S=3）

- **公式**：阶段时间为 Lobatto 点 $\rho = \bigl(0,\ \tfrac12-\tfrac{\sqrt5}{10},\ \tfrac12+\tfrac{\sqrt5}{10},\ 1\bigr)$，求积权重 $\beta = \bigl(\tfrac1{12},\tfrac5{12},\tfrac5{12},\tfrac1{12}\bigr)$，系数阵

$$
\Sigma = \begin{pmatrix}
0&0&0&0\\
\tfrac{11+\sqrt5}{120}&\tfrac{25-\sqrt5}{120}&\tfrac{25-13\sqrt5}{120}&\tfrac{-1+\sqrt5}{120}\\
\tfrac{11-\sqrt5}{120}&\tfrac{25+13\sqrt5}{120}&\tfrac{25+\sqrt5}{120}&\tfrac{-1-\sqrt5}{120}\\
\tfrac1{12}&\tfrac5{12}&\tfrac5{12}&\tfrac1{12}
\end{pmatrix},\qquad
A = \begin{pmatrix}-1&1&0&0\\ -1&0&1&0\\ -1&0&0&1\end{pmatrix}
$$

缺陷：$\zeta_i = -y_0 + y_i - h\sum_j \Sigma_{ij}f_j = 0$（$i=1,2$ 为内部阶段，$i=3$ 用 $\beta$ 行）。

- **代码位置**：`src/csalt/src/collutils/LobattoIIIA_6Order.cpp:110-150`（`InitializeData`：`numDefectCons=3`、`numPointsPerStep=4`、`paramDepArray` 三行 `[-1,1,0,0]`/`[-1,0,1,0]`/`[-1,0,0,1]`、`funcConstArray` 前三行 `-σ(1..2,:)` 与 `-β`）、`:160-203`（`LoadButcherTable`：第 165 行 `Real sqrt5 = sqrt(5.0)`，第 167-171 行 $\rho$，第 174-178 行 $\beta$，第 184-197 行 $\Sigma$）

- **深度讲解**：6 阶表内部点 $\rho_{1,2} = \tfrac12 \mp \tfrac{\sqrt5}{10}$ 正是 $(1-\rho^2)P'_3(\rho)=0$ 在 $(0,1)$ 内的两个根（Lobatto 配点）；$\beta$ 对应 4 点 Lobatto 求积（Gauss-Lobatto 求积：$\int_0^1 g\,d\rho \approx \tfrac1{12}g_0+\tfrac5{12}g_1+\tfrac5{12}g_2+\tfrac1{12}g_3$）。`InitializeData` 的 `numStagePointsPerMesh = 2`（第 147 行）即每区间 2 个内部 stage。依赖阵规律与 4 阶完全一致（锚定 $y_0$，逐行 +1 递增目标索引），`funcConstArray` 第 2 行取 $-\beta$ 作为步方程。`SetButcherTable` 中对应 `"RungeKutta6"`（`NLPFuncUtil_ImplicitRK.cpp:577-580`）。

```cpp
// LobattoIIIA_6Order.cpp:165-171 + 174-178（阶段时间与求积权重）
Real sqrt5 = sqrt(5.0);
// 阶段时间：Lobatto 点（两端点 + (0,1) 内两个根）
rhoVec(0) = 0.0;
rhoVec(1) = 0.5 - sqrt5 / 10.0;   // (5-√5)/10
rhoVec(2) = 0.5 + sqrt5 / 10.0;   // (5+√5)/10
rhoVec(3) = 1.0;
// 求积权重：4 点 Gauss-Lobatto 求积
betaVec(0) = 1.0 / 12.0;   // 端点权重
betaVec(1) = 5.0 / 12.0;   // 内部点 1 权重
betaVec(2) = 5.0 / 12.0;   // 内部点 2 权重
betaVec(3) = 1.0 / 12.0;   // 端点权重
```

### LobattoIIIA_8Order（8 阶 Lobatto IIIA，S=4）

- **公式**：$\rho = \bigl(0,\ \tfrac12-\tfrac{\sqrt{21}}{14},\ \tfrac12,\ \tfrac12+\tfrac{\sqrt{21}}{14},\ 1\bigr)$，$\beta = \bigl(\tfrac1{20},\tfrac{49}{180},\tfrac{16}{45},\tfrac{49}{180},\tfrac1{20}\bigr)$，系数阵（行 1~4）

$$
\Sigma = \begin{pmatrix}
\tfrac{119+3\sqrt{21}}{1960}&\tfrac{343-9\sqrt{21}}{2520}&\tfrac{392-96\sqrt{21}}{2205}&\tfrac{343-69\sqrt{21}}{2520}&\tfrac{-21+3\sqrt{21}}{1960}\\[2pt]
\tfrac{13}{320}&\tfrac{392+105\sqrt{21}}{2880}&\tfrac{8}{45}&\tfrac{392-105\sqrt{21}}{2880}&\tfrac{3}{320}\\[2pt]
\tfrac{119-3\sqrt{21}}{1960}&\tfrac{343+69\sqrt{21}}{2520}&\tfrac{392+96\sqrt{21}}{2205}&\tfrac{343+9\sqrt{21}}{2520}&\tfrac{-21-3\sqrt{21}}{1960}\\[2pt]
\tfrac1{20}&\tfrac{49}{180}&\tfrac{16}{45}&\tfrac{49}{180}&\tfrac1{20}
\end{pmatrix},\qquad
A = \begin{pmatrix}
-1&1&0&0&0\\ -1&0&1&0&0\\ -1&0&0&1&0\\ -1&0&0&0&1
\end{pmatrix}
$$

缺陷：$\zeta_i = -y_0 + y_i - h\sum_{j=0}^{4}\Sigma_{ij}f_j = 0$（$i=1,2,3$ 内部阶段，$i=4$ 用 $\beta$ 行）。

- **代码位置**：`src/csalt/src/collutils/LobattoIIIA_8Order.cpp:110-162`（`InitializeData`：`numDefectCons=4`、`numPointsPerStep=5`、`paramDepArray` 四行、`funcConstArray` 前四行 `-σ(1..3,:)` 与 `-β`）、`:172-226`（`LoadButcherTable`：第 177 行 `Real sqrt21 = sqrt(21)`，第 179-184 行 $\rho$，第 187-192 行 $\beta$，第 198-220 行 $\Sigma$）

- **深度讲解**：8 阶表是 `ImplicitRKPhase` 的**默认**配点（`ImplicitRKPhase.cpp:94-96` 空字符串时 `SetTranscription("RungeKutta8")`；`SetButcherTable` 中 `"RungeKutta8"` 分支 `NLPFuncUtil_ImplicitRK.cpp:573-576`）。$\rho$ 为 5 点 Lobatto 节点，$\beta$ 为 5 点 Gauss-Lobatto 求积权重；$\Sigma$ 各行满足行和 $=\rho_i$（Lobatto IIIA 的阶条件），末行恒等于 $\beta$。`numDefectCons=4`、`numPointsPerStep=5`、`numStagePointsPerMesh=3`。8 阶方法单步精度高，网格细化通常只需很少轮次；代价是每步 4 条缺陷、B 阵每行 5 个非零（带宽 $5n_x$），稀疏雅可比更大。

```cpp
// LobattoIIIA_8Order.cpp:198-202（Σ 第 1 行，内部 stage 1 的系数）
sigmaMatrix(1, 0) = (119.0 + 3.0 * sqrt21) / 1960.0;   // σ_10
sigmaMatrix(1, 1) = (343.0 - 9.0 * sqrt21) / 2520.0;   // σ_11
sigmaMatrix(1, 2) = (392.0 - 96.0 * sqrt21) / 2205.0;  // σ_12
sigmaMatrix(1, 3) = (343.0 - 69.0 * sqrt21) / 2520.0;  // σ_13
sigmaMatrix(1, 4) = (-21.0 + 3.0 * sqrt21) / 1960.0;   // σ_14
```

## 三、配点/求积数学工具（util）

### LobattoIIIaMathUtil（Hermite 插值：配点解到任意时刻的还原）

- **公式**：给定 $n$ 个数据点 $(t_i, y_i, \dot y_i)$，构造 **Hermite 插值多项式**（同时匹配函数值与导数值），用"重节点均差 + 牛顿形式"求系数 $c$：

$$
p(t) = \sum_{k=0}^{2n-1} c_k\, t^{2n-1-k},\qquad
\dot p(t) = \sum_{k=0}^{2n-2} (2n-1-k)\,c_k\, t^{2n-2-k}
$$

（代码即 MATLAB `polyval` 语义：`Y = P(1)X^N + P(2)X^(N-1) + ... + P(N)X + P(N+1)`。）

- **代码位置**：`src/csalt/src/util/LobattoIIIaMathUtil.cpp:252-263`（`ComputeFunctionValue`：霍纳式 `polyval`）、`:277-288`（`ComputeDerivativeValue`：逐项求导）、`:305-398`（`GetHermiteCoeff`：重节点均差构造 $z=[t_0,t_0,t_1,t_1,\dots]$、$f=[y_0,\dot y_0,\frac{y_1-y_0}{t_1-t_0},\dots]$，再牛顿前向递推）、`:412-467`（`Convolution`：多项式乘法卷积，用于牛顿插值的 $(t-t_i)$ 累积）、头文件 `LobattoIIIaMathUtil.hpp:52-79`（三个 `HermiteInterpolation` 重载）

- **深度讲解**：`GetHermiteCoeff` 第 322~356 行是核心：把每个数据点"复制"成两个重节点 $z_{2i}=z_{2i+1}=t_i$，函数值序列 $f$ 首项 $f_0=y_0$、奇偶间隔处放导数 $\dot y_i$ 与均差 $\frac{y_{i+1}-y_i}{t_{i+1}-t_i}$（第 325~337 行），然后按重节点均差表逐列递推（第 344~356 行），最后用卷积把 $(t-z_k)$ 因子逐步乘出牛顿多项式系数（第 362~392 行）。注释明确建议 `timeVec(0)=0`（第 310 行）以减少截断误差——调用方（`NLPFuncUtil_ImplicitRK::InterpolateInMesh` 第 2055~2066 行、`RombFuncWrapper` 第 1804~1811 行）都先把时间减去区间起点归一化。该工具在 CSALT 里的用途有二：**网格细化时把旧网格解插值到新网格点**（`InterpolateInMesh`），以及 **Romberg 误差估计时构造"伪动力学"**（`RombFuncWrapper`）。

```cpp
// LobattoIIIaMathUtil.cpp:325-337（GetHermiteCoeff 的重节点与均差初始化）
for (Integer idx = 0; idx < n; idx++)
{
   z(2 * idx)     = (*timeVec)(idx);   // 每个数据点复制为两个重节点
   z(1 + 2 * idx) = (*timeVec)(idx);
   f(1 + 2 * idx) = (dynValues)(idx);  // 奇数位放导数（动力学值）
}
f(0) = (funcValues)(0);                // 首位放函数值
for (Integer idx = 1; idx < n; idx++)
{
   // 偶数位放一阶均差：两点连线斜率
   f(idx * 2) = ((funcValues)(idx) - (funcValues)(idx-1)) /
                ((*timeVec)(idx) - (*timeVec)(idx-1));
}
```

### RadauMathUtil（LGR 节点、求积权重与微分矩阵）

- **公式**：单段 LGR 节点 $\tau_j\in[-1,1)$ 是 $P_N+P_{N+1}$ 的根（含 $\tau_0=-1$），用 Newton 迭代求（初值取 Chebyshev-Gauss-Radau 点 $-\cos\frac{2\pi j}{2N+1}$）：

$$
\tau_j^{(k+1)} = \tau_j^{(k)} - \frac{1-\tau_j^{(k)}}{N+1}\cdot\frac{P_N(\tau_j^{(k)})+P_{N+1}(\tau_j^{(k)})}{P_N(\tau_j^{(k)})-P_{N+1}(\tau_j^{(k)})}
$$

求积权重：$w_0=\dfrac{2}{(N+1)^2}$，$w_j=\dfrac{1-\tau_j}{\bigl((N+1)\,P_N(\tau_j)\bigr)^2}$。重心形式微分矩阵：$D_{ij}=\dfrac{w_j/w_i}{\tau_i-\tau_j}\ (i\ne j)$，$D_{ii}=1-\sum_{j\ne i}D_{ij}$，最后取负转置得到导数算子。

- **代码位置**：`src/csalt/src/util/RadauMathUtil.cpp:62-185`（`GetLagrangeDiffMatrix`：重心权重、$D_{ij}=\frac{w_j}{w_i(x_i-x_j)}$、对角修正与负转置）、`:208-309`（`ComputeMultiSegmentLGRNodes`：分段仿射映射 $x\mapsto \frac{a+b}{2}+\frac{b-a}{2}x$ 与分段微分矩阵块拼接）、`:325-428`（`ComputeSingleSegLGRNodes`：Newton 迭代求 LGR 节点与权重，第 338 行 Chebyshev 初值、第 388-398 行 Legendre 三项递推、第 401-405 行 Newton 更新、第 414-423 行权重公式）

- **深度讲解**：这是 `NLPFuncUtilRadau`（RadauPhase 的数学内核）的引擎。`ComputeSingleSegLGRNodes(N)` 求 $N+1$ 个节点：第 336~340 行用 $-\cos(2\pi j/(2N+1))$ 做初值（Chebyshev-Gauss-Radau 点，天然含 $-1$）；第 361~368 行把 $x(0)=-1$ 固定为"自由点之外"，仅对 $j\ge1$ 迭代；第 388~398 行用 Legendre 三项递推填 Vandermonde 型矩阵 $P$ 的列（$P_{k+1}=\frac{(2k+1)xP_k-kP_{k-1}}{k+1}$）；第 401~405 行的 Newton 更新式正是上面的 $\tau$ 迭代，收敛判据 $2.22\times10^{-16}$（机器精度，第 373 行）。权重公式（第 414~423 行）即 $w_0=2/(N+1)^2$ 与 $w_j=(1-\tau_j)/(N+1)^2P_N^2$。`GetLagrangeDiffMatrix` 用重心权重 $w_j=1/\prod_{k\ne j}(x_j-x_k)$（第 96~118 行）构造 $D_{ij}$，对角用"行和补 1"（第 134~166 行），最后负转置（第 171~178 行）使 $D$ 满足 $\frac{d}{d\tau}\ell_j(\tau_i)=D_{ij}$ 的求导方向约定。`ComputeMultiSegmentLGRNodes` 把每段的节点仿射映射到 $[-1,1]$ 内的分段（第 273~284 行），并调用 `SetSparseBLockMatrix` 把各段微分矩阵块拼进全局稀疏微分矩阵（第 293~297 行）。

```cpp
// RadauMathUtil.cpp:401-407（Newton 迭代核心：更新除 τ=-1 外的所有节点）
for (UnsignedInt idx = 1; idx < N1; ++idx)
{
   // 公式：τ_new = τ_old - (1-τ_old)/(N+1) * (P_N + P_{N+1})/(P_N - P_{N+1})
   x(idx) = xold(idx) - ((1 - xold(idx)) / N1)
            * (SparseMatrixUtil::GetElement(&P, idx, N)      // P_N(τ)
            + SparseMatrixUtil::GetElement(&P, idx, N1))     // P_{N+1}(τ)
            / (SparseMatrixUtil::GetElement(&P, idx, N)
            - SparseMatrixUtil::GetElement(&P, idx, N1));
   xAbsDiff[idx] = GmatMathUtil::Abs(x(idx) - xold(idx));    // 记录步进量
}
```

### BaryLagrangeInterpolator（重心拉格朗日插值）

- **公式**：给定互异节点 $x_j$ 与函数值 $f_j$，先算**重心权重**（第一形式）

$$
w_j = \frac{1}{\prod_{k\ne j}(x_j - x_k)}
$$

再对任意插值点 $y$ 用**第二形式**（数值稳定、$O(n)$ 求值）：

$$
L(y) = \frac{\displaystyle\sum_j f_j\,\frac{w_j}{y-x_j}}{\displaystyle\sum_k \frac{w_k}{y-x_k}}
$$

实现中预计算插值矩阵 $M_{r,j}=\dfrac{w_j}{y_r-x_j}\Big/\sum_k\dfrac{w_k}{y_r-x_k}$，一次求值即 $L(y_r)=\sum_j M_{r,j}f_j$。

- **代码位置**：`src/csalt/src/util/BaryLagrangeInterpolator.cpp:611-625`（`CalWeightVec`：$w_j=1/\prod_{k\ne j}(x_j-x_k)$）、`:574-602`（`CalBarycentricMatrix`：先填 $w_j/(y_r-x_j)$ 再按行归一化）、`:309-323`（`Interpolate`：`resultVec = barycentricMatrix*(*funcValueVec)`）、头文件 `BaryLagrangeInterpolator.hpp:98-100`（`weigthVec/barycentricMatrix` 成员）、`:24-26`（注释：刻意不继承 gmatutil 的 Interpolator 基类）

- **深度讲解**：`SetIndVarVec` 存入数据节点并触发 `CalWeightVec`（第 154~174 行）；`SetInterpPointVec` 触发 `CalBarycentricMatrix`（第 191~214 行），并拒绝插值点与数据点重合（`ChkInterpPointVecFeasibility` 第 523~530 行抛异常——因为第二形式在 $y=x_j$ 处奇异，CSALT 的策略是让调用方先查重、重合点直接用原值，见 `NLPFuncUtil_ImplicitRK::InterpolateInMesh` 第 2079~2101 行）。`CalBarycentricMatrix` 第 590~592 行填 $w_j/(y_r-x_j)$ 并累加行和，第 595~601 行按行除以行和完成归一化——即上式分母归一，使插值满足"常数保持性"（$\sum_j M_{rj}=1$）。该插值器同时服务 Radau 的网格细化插值（`NLPFuncUtilRadau.cpp:516-568`）与 IRK 的控制插值（`InterpolateInMesh`）。O(n) 求值 + 预计算矩阵使其适合配点解批量还原。

```cpp
// BaryLagrangeInterpolator.cpp:616-624（CalWeightVec：重心权重）
for (int idx1 = 0; idx1 < numIndVarVec; idx1++)
{
   weigthVec(idx1) = 1;
   for (int idx2 = 0; idx2 < numIndVarVec; idx2++)
   {
      if (idx1 != idx2)
         weigthVec(idx1) /= (indVar(idx1) - indVar(idx2));
      // w_j = 1/∏_{k≠j}(x_j - x_k)，连除即连乘倒数
   }
}
```

## 四、缺陷约束组装：NLPFuncUtil 一族

### NLPFuncUtil_Coll（配点 NLP 助手基类：Betts 公式的求值框架）

- **公式**：本类定义"两步初始化"流程并集中实现缺陷/代价的求值与雅可比入口。其子类填充的 $A,B,D,Q$ 满足（Betts 教科书形式，见 `NLPFunctionData.hpp:44-49` 头注释）

$$
\text{nlpFuncs} = A\,Z + B\,F,\qquad
\text{nlpJac} = A + B\,Q_{\text{mat}},\qquad
\text{sparsity} = A + B\,D
$$

其中 $Z$ 决策向量、$F$ 用户函数值向量、$Q_{\text{mat}}$ 用户函数对决策向量的雅可比（parQ 矩阵）、$D$ 用户函数雅可比稀疏模式矩阵。

- **代码位置**：`src/csalt/src/collutils/NLPFuncUtil_Coll.cpp:242-265`（`Initialize`：设 `ptrConfig` 后调纯虚 `InitializeTranscription()` 与 `InitNLPHelpers()`）、`:283-350`（两个 `PrepareToOptimize` 重载：调 `InitializeConstantDefectMatrices/InitializeConstantCostMatrices`）、`:435-492`（`ComputeDefectFunAndJac`：`FillDynamicDefectConMatrices` 后交 `DefectNLPData.ComputeFunctions/ComputeJacobian`）、`:509-539`（`ComputeCostFunAndJac`）、`:603-620`（`ComputeDefectSparsityPattern/ComputeCostSparsityPattern`）、头文件 `NLPFuncUtil_Coll.hpp:157-215`（纯虚：`GetdCurrentTimedTI/TF`、`RefineMesh`、`InitializeTranscription`、`FillDynamic*` 等）

- **深度讲解**：`NLPFuncUtil_Coll` 本身不实现任何配点公式，而是把"求值流水线"固定下来：`Initialize()` 先转写（算节点、权重、微分矩阵、维度），`PrepareToOptimize()` 依据用户函数属性把**常数矩阵** $A,B,D$ 一次性填好（`InitializeConstant*Matrices`），此后每次 SNOPT 迭代只需 `FillDynamic*` 填 $Q$ 向量与 parQ 矩阵、再做两次稀疏乘加。`ComputeDefectFunAndJac`（第 448~487 行）体现该分工：若 `isConMatInitialized==false` 先初始化常数阵，然后 `DefectNLPData.ComputeFunctions(&QVector, ptrDecVectorData, funcValues)` 计算 $A Z + B Q$，`DefectNLPData.ComputeJacobian(&parQMatrix, jacArray)` 计算 $A + B\cdot Q_{\text{mat}}$。注意 $Q$（小写、动态）与 $Q_{\text{mat}}$（parQ 矩阵、动态）是两个量：前者是用户函数值向量（$-\Delta T f$ 等），后者是用户函数对 $Z$ 的雅可比。

```cpp
// NLPFuncUtil_Coll.cpp:459-486（ComputeDefectFunAndJac 的求值主体）
Rvector QVector;
const Rvector *ptrDecVectorData;
ptrDecVectorData = DecVector->GetDecisionVectorPointer();  // 取当前决策向量 Z
RSMatrix parQMatrix;
FillDynamicDefectConMatrices(ptrFuncDataArray, QVector, parQMatrix);
// 填 Q（用户函数值×系数）与 parQ（用户函数雅可比×系数）
DefectNLPData.ComputeFunctions(&QVector, ptrDecVectorData, funcValues);
// nlpFuncs = A·Z + B·Q
DefectNLPData.ComputeJacobian(&parQMatrix, jacArray);
// nlpJac   = A + B·parQ
```

### NLPFunctionData（A/B/D 矩阵代数引擎）

- **公式**（头注释原话，`NLPFunctionData.hpp:44-49`）：

$$
\text{nlpFuncs} = A_{\text{con}}\,Z + B_{\text{con}}\,F_{\text{user}},\qquad
\text{sparsePattern} = A_{\text{con}} + B_{\text{con}}D_{\text{con}},\qquad
\text{nlpJac} = A_{\text{con}} + B_{\text{con}}Q_{\text{con}}
$$

实现上 `ComputeFunctions` 用 `fast_prod`（稀疏×稠密）依次算 $A Z$ 与 $B Q$ 并累加；`ComputeJacobian` 把 `parQMat` 稀疏乘进 $A$；`ComputeJacSparsityPattern` 用 $A$ 的模式加 $B\cdot D$ 的模式。

- **代码位置**：`src/csalt/src/collutils/NLPFunctionData.hpp:44-49`（三条公式的头注释）、`:118-125`（`ComputeFunctions/ComputeJacobian/ComputeJacSparsityPattern` 声明）、`src/csalt/src/collutils/NLPFunctionData.cpp:510-540`（`ComputeFunctions`：先 `fast_prod(&AMatrix, DecVector, ...)` 再 `fast_prod(&BMatrix, QVector, ..., false)` 累加）、`:579-591`（`ComputeJacobian`：`funcJacobianMatrix = AMatrix` 后 `fast_prod(&BMatrix, parQMat, ..., false)`）、`:602-617`（`ComputeJacSparsityPattern`：`BSPattern*DSPattern` 加进 `ASPattern`）

- **深度讲解**：这是 Betts 公式真正执行的地方。`ComputeFunctions` 第 527~538 行的两次 `fast_prod`：第一次 `isInitializing=true`（覆盖），第二次 `isInitializing=false`（累加），完成 $\zeta=A Z + B Q$。`ComputeJacobian` 第 582~585 行：先把雅可比初始化为 $A$，再累加 $B\cdot Q_{\text{mat}}$——稀疏模式下 $B$ 是"每缺陷行少数非零"、$Q_{\text{mat}}$ 是用户函数雅可比块，乘积自动继承两者的稀疏性。`ComputeJacSparsityPattern` 用模式矩阵（全 1/全 0）做同一乘法得到雅可比稀疏骨架，这正是 `Trajectory::SetSparsityPattern` 交给 SNOPT 的 `iGfun/jGvar` 的来源（见第 6.1 节）。$A,B,D,Q$ 四块矩阵通过 `InsertAMatPartition/InsertBMatPartition/InsertDMatPartition` 按行/列偏移拼装，各配点法（IRK/Radau）只负责"填哪几块、填什么值"。

### NLPFuncUtil_ImplicitRK（IRK 分离形式缺陷约束与代价求积）

- **公式**：设某步的无量纲步长 $h_s=\text{stepSizeVec}$、有量纲相位时长 $\Delta T=t_f-t_0$、有量纲步长 $h=h_s\Delta T$。缺陷约束（B 阵取自 `funcConstArray=-\Sigma$、Q 向量取 $-\Delta T f$，联立得）

$$
\zeta_i = \sum_{j=0}^{S}A_{ij}\,y_j - h\sum_{j=0}^{S}\Sigma_{ij}\,f_j = 0,\qquad i=1,\dots,S
$$

即 $A$（`paramDepArray`）作用在决策向量状态块、$-\Sigma\cdot h$ 作用在动力学块。积分代价用 Butcher 权重求积：

$$
J = \sum_{j=0}^{S}\beta_j\,h\,f_j = \frac{h}{6}(f_0+4f_1+f_2)\ \text{（4 阶时）}
$$

时间对决策变量的偏导：$\dfrac{\partial t_k}{\partial t_0}=1-\rho_k$、$\dfrac{\partial t_k}{\partial t_f}=\rho_k$（`GetdCurrentTimedTI/TF`）。

- **代码位置**：
  - `src/csalt/src/collutils/NLPFuncUtil_ImplicitRK.cpp:196-251`（`InitializeTranscription`：`numDefectConNLP = n_x·(numMeshPoints−1)` 第 236 行、`pValue = numPointsPerStep−1` 第 245 行、`maxAddNodeNumPerIntv=15`/`relErrorTol=1e-5`/`maxTotalNodeNumPerIntv=20` 第 248~250 行）
  - `:565-605`（`SetButcherTable`：按字符串 `RungeKutta8/6/4/HermiteSimpson/Trapezoid` 选表，第 573~594 行）
  - `:632-757`（`InitializeConstantDefectMatrices`：拼 $A$ 块（第 662~679 行 `InsertAMatPartition` + `negBChunk=(-bChunk)*stepSizeVec` 第 677 行）与 $D$ 块（第 696~749 行））
  - `:774-871`（`FillDynamicDefectConMatrices`：`valueVec = -timeStep*funcValues` 第 806 行、状态/控制/静态/时间雅可比块第 813~856 行）
  - `:886-1003`（`InitializeConstantCostMatrices`：代价 B 阵 `+quadratureWeights*stepSize` 第 933~934 行）
  - `:360-383` + `:397-402`（`GetdCurrentTimedTI/TF` 与 `MeshPointIdxToNonDimTime`）
  - `:450-516`（`ComputeStepSizeVector`：按区间分数与每区间点数生成离散点）
  - `:86`（`quadratureType = 1`：IRK 求积类型标记）

- **深度讲解**：本类是本章公式密度最高的实现。`InitializeConstantDefectMatrices` 第 647~683 行的循环结构是：外层区间 → 中层步 → 内层缺陷 `defectIdx` → 最内层点 `subStepIdx`，每缺陷取 `GetDependencyChunk` 得到 $A,B$ 标量块后：$A$ 块按状态索引 `InsertAMatPartition`（第 673~674 行），$B$ 块乘上区间步长取负后 `InsertBMatPartition`（第 677~679 行）——`negBChunk = (-bChunk)*stepSizeVec(intervalIdx)` 正是把 `funcConstArray=-Σ` 变成 $B=+h_s\Sigma$。随后（第 696~749 行）填 $D$ 阵：每个 ODE RHS 分量在 $D$ 中为 1（第 743~745 行时间列），并把用户函数对状态/控制/静态的雅可比稀疏模式块放进去（第 705~738 行），初末时间列各为 1——$D$ 阵描述"$f$ 依赖哪些决策变量"，供稀疏模式 $A+BD$ 使用。`FillDynamicDefectConMatrices` 第 806 行 `tmpVec = -timeStep*funcValues` 说明 Q 向量每项是 $-\Delta T f_j$；第 848~856 行的时间雅可比块：

$$
\frac{\partial \zeta}{\partial t_0} = f_j - \Delta T(1-\rho_j)\frac{\partial f_j}{\partial t},\qquad
\frac{\partial \zeta}{\partial t_f} = -f_j - \Delta T\,\rho_j\frac{\partial f_j}{\partial t}
$$

（时间被当作决策变量 $t_0,t_f$，动力学 $f(x,u,t)$ 对时间的偏导经链式法则进入雅可比。）

```cpp
// NLPFuncUtil_ImplicitRK.cpp:655-679（InitializeConstantDefectMatrices 填 A、B 块）
for (Integer defectIdx = 0; defectIdx < numStages; defectIdx++)
{
   for (Integer subStepIdx = 0; subStepIdx < numStages + 1; subStepIdx++)
   {
      // 步内点索引：前 S 个是内部 stage，最后一个是下一 mesh 点（stage 0）
      if (subStepIdx < numStages)
         pointIdx = GetPointIdxGivenMeshAndStageIdx(stepIdx, subStepIdx);
      else
         pointIdx = GetPointIdxGivenMeshAndStageIdx(stepIdx + 1, 0);

      Rmatrix aChunk, bChunk, negBChunk;
      // 取该缺陷-点的 A（状态 ±1 系数）与 B（-Σ 系数）标量块
      butcherTableData->GetDependencyChunk(defectIdx, subStepIdx,
                        numStateVars, aChunk, bChunk);
      IntegerArray stateIdxs = dynFunVector.at(pointIdx)->GetStateIdxs();
      DefectNLPData.InsertAMatPartition(defectStartIdx, stateIdxs[0], &aChunk);
      // 关键符号：B 块取负再乘无量纲步长 → 得到 +h_s·Σ
      negBChunk = (-bChunk)*stepSizeVec(intervalIdx);
      Integer odeStartIdx = pointIdx*numStateVars;
      DefectNLPData.InsertBMatPartition(defectStartIdx, odeStartIdx, &negBChunk);
   }
   defectStartIdx = defectStartIdx + numStateVars;   // 缺陷行推进 n_x 行
}
```

### NLPFuncUtilRadau（LGR 缺陷约束与代价求积）

- **公式**：设 LGR 微分矩阵 $D\in\mathbb{R}^{N\times(N+1)}$（$N$ 个配点、含步末增广点）、状态向量 $Y\in\mathbb{R}^{N+1}$、动力学 $f\in\mathbb{R}^N$，LGR 缺陷约束（$A=D$、$B=I$、$Q=-\tfrac{\Delta T}{2}f$）：

$$
D\,Y - \frac{\Delta T}{2}\,f \;=\; 0
$$

（$\tfrac{\Delta T}{2}$ 是 $[-1,1]\to[t_0,t_f]$ 仿射映射 $t=\tfrac{\Delta T}{2}(\tau+1)+t_0$ 的导数因子。）积分代价为 LGR 求积：

$$
J = \frac{\Delta T}{2}\sum_{j=0}^{N-1}w_j\,g_j,\qquad
\frac{\partial t_k}{\partial t_0}=\frac{1-\tau_k}{2},\quad
\frac{\partial t_k}{\partial t_f}=\frac{1+\tau_k}{2}
$$

- **代码位置**：
  - `src/csalt/src/collutils/NLPFuncUtilRadau.cpp:240-314`（`InitializeTranscription`：`ComputeMultiSegmentLGRNodes` 第 252~257 行、`numMeshPoints=quadratureWeights.GetSize()` 第 268 行、`numStatePoints=numMeshPoints+1` 第 269 行、末点无控制 `timeVectorType=2` 第 306 行）
  - `:819-1079`（`InitializeConstantDefectMatrices`：A 阵 = 微分矩阵元素 `radauDiffSMatrix(lowIdx+rowIdx, lowIdx+pointIdx)` 第 930~933 行、B 阵 = 单位阵 `InsertBMatElement(conIdx, conIdx, 1)` 第 942 行）
  - `:1532-1681`（`FillDynamicDefectConMatrices`：`QVector = -dtBy2*funcValueVec` 第 1616 行、`dtBy2=0.5*deltaTime` 第 1544 行）
  - `:720-804`（`InitializeConstantCostMatrices`：`InsertBMatElement(0, funcIdx, -quadratureWeights(meshIdx))` 第 756 行）
  - `:206-229`（`GetdCurrentTimedTI/TF`：$\frac{1\mp\tau}{2}$）
  - `:326-336`（`SetTimeVector`：$t=\frac{\Delta T}{2}(\tau+1)+t_0$ 第 333 行）
  - `:70`（`quadratureType = 2`：Radau 不用末点）

- **深度讲解**：Radau 的缺陷装配比 IRK 简洁得多：A 阵直接是分段的 LGR 微分矩阵（每段 $N_k\times(N_k+1)$ 块，见 `RadauMathUtil::ComputeMultiSegmentLGRNodes` 的拼接），B 阵是单位阵（第 942 行）——因为缺陷写成 $D Y = \tfrac{\Delta T}{2}f$ 时动力学系数为 1。`FillDynamicDefectConMatrices` 第 1616~1631 行逐约束填入：

$$
Q_i = -\frac{\Delta T}{2}f_i,\qquad
\frac{\partial Q_i}{\partial t_0} = \tfrac12 f_i - \tfrac{\Delta T}{2}\tfrac{1-\tau_i}{2}\tfrac{\partial f_i}{\partial t},\qquad
\frac{\partial Q_i}{\partial t_f} = -\tfrac12 f_i - \tfrac{\Delta T}{2}\tfrac{1+\tau_i}{2}\tfrac{\partial f_i}{\partial t}
$$

（第 1618~1631 行），状态/控制/静态雅可比均乘 $-\tfrac{\Delta T}{2}$（第 1633~1674 行）。Radau 的**末点特殊处理**贯穿始终：$N$ 个配点带状态+控制，末 mesh 点只带状态（`timeVectorType[numStatePoints-1]=2`，第 299~306 行），缺陷数 `= n_x·numMeshPoints`（第 277 行）。代价 B 阵第 756 行为 $-w_j$，与 Q 向量 $-\tfrac{\Delta T}{2}g$ 相乘得 $+\tfrac{\Delta T}{2}\sum w_j g_j$。`GetdCurrentTimedTI/TF` 的 $\tfrac{1\mp\tau}{2}$ 因子正来自仿射映射——与 IRK 的 $1-\rho$、$\rho$ 形成对照。

```cpp
// NLPFuncUtilRadau.cpp:930-942（InitializeConstantDefectMatrices 填 A、B 块）
DefectNLPData.InsertAMatElement(
   conIdx,
   stateIdxs[stateIdx],
   radauDiffSMatrix(lowIdx + rowIdx, lowIdx + pointIdx));
   // A 阵元素 = LGR 微分矩阵 D 的分段块元素 D_{rowIdx, pointIdx}
// ...
DefectNLPData.InsertBMatElement(conIdx, conIdx, 1);
// B 阵 = 单位阵：缺陷方程中动力学系数为 1（D·Y = (ΔT/2)·f 的右端）
```

### 缺陷约束的稀疏雅可比结构与依赖矩阵

- **公式**：两类配点的全局雅可比都写成 $A + B\cdot Q_{\text{mat}}$，其中 $B$ 的列块结构与"缺陷依赖哪些动力学点"一一对应：

$$
\frac{\partial\zeta}{\partial Z} = A + B\,Q_{\text{mat}},\qquad
\underbrace{B}_{(n_x N_\text{def})\times(n_x N_\text{pts})}\ \text{每行非零} =
\begin{cases}
\text{IRK: } S+1\ \text{个} \ h\Sigma_{ij}\ \text{块} & (j=0..S)\\
\text{Radau: } 1\ \text{个} \ 1\ \text{块} & (j=i)
\end{cases}
$$

- **代码位置**：`src/csalt/src/collutils/NLPFunctionData.cpp:579-591`（`ComputeJacobian`）、`:602-617`（`ComputeJacSparsityPattern`）；`src/csalt/src/collutils/NLPFuncUtil_ImplicitRK.cpp:696-749`（$D$ 阵：状态/控制/静态雅可比稀疏模式块 + 时间列 1）；`src/csalt/src/collutils/NLPFuncUtilRadau.cpp:990-1052`（$D$ 阵填法）；`src/csalt/src/executive/SnoptOptimizer.cpp:422-448`（`iGfun/jGvar` 导出）

- **深度讲解**：稀疏结构的三个层次：**(1) 常数层**——$A,B,D$ 由 Butcher 表 / 微分矩阵与网格唯一确定，网格不变就不重算（`isConMatInitialized` 标志，`NLPFuncUtil_ImplicitRK.cpp:756`、`NLPFuncUtilRadau.cpp:1074`）；**(2) 动态层**——$Q_{\text{mat}}$（用户函数雅可比块）每次迭代由 `UserPathFunctionManager` 按稀疏模式求值，位置由 `dynFunProps->GetStateJacobianPattern()` 等给出（`NLPFuncUtil_ImplicitRK.cpp:705-738`）；**(3) 导出层**——`ComputeJacSparsityPattern` 做 $A+BD$ 的模式乘法得到总骨架，SNOPT 用 `iGfun/jGvar` 三向量接收。IRK 每缺陷行依赖 $S+1$ 个点的状态/动力学（块带宽 $(S+1)n_x$），Radau 每缺陷行只依赖 1 个动力学点但经微分矩阵耦合 $N_k+1$ 个状态（微分矩阵行稠密、列按分段局部）。两类都在"每行非零数"与"数值精度"之间取平衡：IRK 用高阶 Butcher 表换取大步长，Radau 用谱精度微分矩阵换取少节点。

## 五、离散化装配与网格细化

### ImplicitRKPhase / RadauPhase（离散化装配入口）

- **公式**：装配即"把用户网格变成 NLP 维度"：IRK 每步 $S$ 条缺陷、步数 $=\sum_i(\text{点数}_i-1)$、`numMeshPoints = numStepsInPhase*numPointsPerMesh + 1`、`numDefectConNLP = n_x·(numMeshPoints−1)`（见 4.3 节公式）；Radau `numMeshPoints = N_\text{LGR}`、`numDefectConNLP = n_x·numMeshPoints`、末点无控制（见 4.4 节）。

- **代码位置**：`src/csalt/src/executive/ImplicitRKPhase.cpp:43-49`（构造：`constraintTimeOffset = 1`）、`:91-109`（`InitializeTranscription`：默认 `"RungeKutta8"`、`new NLPFuncUtil_ImplicitRK(collocationMethod)` 后 `transUtil->Initialize(config)`）、`:121-124`（`SetTranscription`）；`src/csalt/src/executive/RadauPhase.cpp:48-54`（构造：同样 `constraintTimeOffset=1`）、`:107-121`（`InitializeTranscription`：`new NLPFuncUtilRadau()` 后 `transUtil->Initialize(config)`）

- **深度讲解**：两个 Phase 子类只重写 `InitializeTranscription()`（`Phase.hpp` 的纯虚，见 [第15章](../CH15-csalt-interop-tests.md) 2.1.1 节），把 `ProblemCharacteristics`（网格分数 `meshIntervalFractions`、每区间点数 `meshIntervalNumPoints`、维度）交给配点助手：IRK 走 `NLPFuncUtil_ImplicitRK::InitializeTranscription`（填 `discretizationPoints`、`stepSizeVec`、NLP 维度），Radau 走 `NLPFuncUtilRadau::InitializeTranscription`（生成 LGR 节点与微分矩阵）。`constraintTimeOffset=1` 表示"缺陷约束数 = 时间点数 − 1"这一两法共有的特性。`transUtil->Initialize(config)` 触发 `NLPFuncUtil_Coll::Initialize` 的两步初始化（第 242~265 行），此后 `Phase` 通过 `transUtil` 的虚接口取 `GetDiscretizationPoints/GetNumStatePoints/ComputeDefectSparsityPattern` 等完成 `DecisionVector` 与 `ProblemCharacteristics` 的最终装配。

```cpp
// ImplicitRKPhase.cpp:91-109（InitializeTranscription：按方法字符串实例化助手）
void ImplicitRKPhase::InitializeTranscription()
{
   // 默认配点是 RungeKutta 8（8 阶 Lobatto IIIA）
   if (strcmp(collocationMethod.c_str(),"") == 0)
   {
      SetTranscription("RungeKutta8");
      if (transUtil)
         delete transUtil;                          // 清掉旧助手（网格重配时）
      transUtil = new NLPFuncUtil_ImplicitRK(collocationMethod);
      transUtil->Initialize(config);                // 转写 + NLP 助手初始化
   }
   else
   {
      if (transUtil)
         delete transUtil;
      transUtil = new NLPFuncUtil_ImplicitRK(collocationMethod);
      transUtil->Initialize(config);
   }
}
```

### DecVecTypeBetts（Betts 排布的决策向量）

- **公式**：决策向量排布（头注释原话）

$$
Z = \bigl[\,t_0\ \ t_f\ \ y_{10}\ u_{10}\ \ y_{11}\ u_{11}\ \cdots\ y_{nm}\ u_{nm}\ \ s_1\cdots s_o\ \ w_1\cdots w_p\,\bigr]
$$

即初末时间在前，随后按"网格点 × 阶段"交织的状态 $y$ 与控制 $u$，最后静态参数 $s$ 与积分参数 $w$。`hasControlAtFinalMesh` 区分 Hermite-Simpson（末网格点带控制）与 Radau（末点无控制）。

- **代码位置**：`src/csalt/src/collutils/DecVecTypeBetts.hpp:27-30`（排布注释）、`:56-57`（`GetStateVector/GetControlVector` 实现声明）；`src/csalt/src/collutils/DecisionVector.hpp:54-57`（`Initialize(nStateVars, nControlVars, nIntegralParams, nStaticParams, ...)`）、`:88-89`（抽象 `GetStateVector(meshIdx, stageIdx)/GetControlVector`）、`:84-85`（`GetInterpolatedStateVector/GetInterpolatedControlVector`）

- **深度讲解**：`NLPFuncUtil_ImplicitRK::GetStateAndControlInMesh` 与 `NLPFuncUtilRadau::GetStateAndControlInMesh` 都按此排布取数据：前者用 `ptrDecVector->GetStateVector(meshIdx, stageIdx)`（`NLPFuncUtil_ImplicitRK.cpp:1444`），后者用 `GetStateVector(stateIdxs[idx1], 0)`（`NLPFuncUtilRadau.cpp:1217-1218`）——Radau 的 stage 恒为 0。Betts 排布使"缺陷锚定 $y_0$"（A 阵的 −1 列）在索引上就是相邻块，`InsertAMatPartition` 只需状态索引偏移即可定位。`GetInterpolatedStateVector(atTime)` 是求解收敛后还原连续轨迹的接口（配合 `BaryLagrangeInterpolator`，见 [第15章](../CH15-csalt-interop-tests.md) 2.1.5 节流程 6）。

### 网格细化策略（IRK：误差估计 + 加节点；Radau：升阶 / 分裂区间）

- **公式**：IRK 每步误差 $e_k$ 用 Romberg 积分估计"伪动力学与真实动力学之差"并归一化：

$$
e_k = \max_i \frac{1}{1+\max(|y_i|,|\dot y_i|)}\int_{t_k}^{t_{k+1}}\Bigl|\frac{\dot y_{\text{pseudo}}(t)-\Delta T f(t)}{\Delta T}\Bigr|\,dt
$$

（`RombFuncWrapper` 第 1844~1850 行：被积函数 $=|\dot y_{\text{pseudo}}-\Delta T f|/\Delta T$；`GetCollocErrorVec` 第 1720~1721 行乘权重 $1/(1+\max|\cdot|)$。）若某区间误差超容差，按"误差随节点数按阶衰减"估计所需新增节点数 $\Delta N$：

$$
e_{\text{new}} = e_{\max}\left(\frac{N}{N+\Delta N}\right)^{p-\text{ordRed}+1}\le \text{tol}
$$

（`GetNewMeshPoints` 第 2174~2179 行，$p=$ 多项式阶、$\text{ordRed}$ 为阶降；上限 `maxAddNodeNumPerIntv=15`、区间总节点上限 `maxTotalNodeNumPerIntv=20`，超限则分裂区间——第 2198~2254 行。）Radau 侧误差（`GetMaxRelErrorInMesh` 第 1468~1478 行）：

$$
e = \max_i \frac{\max_k\bigl|y_i(\tau_k)-y_i(\tau_0)-\tfrac{\Delta T}{2}\sum_j (D^{-1})_{kj} f_{ij}\bigr|}{1+\max_k|y_i(\tau_k)|}
$$

细化决策：误差≤tol 保持；否则新多项式阶 $N' = N + \lceil \log(e/\text{tol})/\log N \rceil$（`RefineMesh` 第 466~471 行）；$N' > N_{\max}=14$ 时把区间均分为若干子区间、每段用最低阶（第 487~514 行）。

- **代码位置**：`src/csalt/src/collutils/NLPFuncUtil_ImplicitRK.cpp:1705-1761`（`GetCollocErrorVec`：逐步误差 + 每区间最大误差）、`:1628-1685`（`GetCollocError`：`GetRombergIntegration` 装配）、`:1785-1854`（`RombFuncWrapper`：Hermite 插值伪状态/伪动力学 + 被积函数）、`:1886-1975`（`GetRombergIntegration`：Romberg 积分表 $R_{k,m}=\frac{4^m R_{k,m-1}-R_{k-1,m-1}}{4^m-1}$）、`:2127-2265`（`GetNewMeshPoints`：加节点/分裂）、`:1142-1349`（`RefineMesh`：新网格与初猜插值）、`src/csalt/src/collutils/NLPFuncUtilRadau.cpp:1247-1486`（`GetMaxRelErrorInMesh`：新 LGR 点插值 + 微分矩阵求逆积分）、`:395-626`（`RefineMesh`：升阶/分裂 + 重心插值新初猜）

- **深度讲解**：两种策略体现"h 型"与"p 型"细化的分野：IRK 固定阶数、**加节点**（h 型），Radau 固定每区间节点数的上下限、**升阶或分裂**（p/h 混合）。IRK 的误差估计是"事后"的：先用 `LobattoIIIaMathUtil::HermiteInterpolation` 从当前解构造伪动力学 $\dot y_{\text{pseudo}}$（`RombFuncWrapper` 第 1809~1811 行），再用 Romberg 积分把 $|\dot y_{\text{pseudo}}-\Delta T f|$ 积分出来并与真实动力学之差作比较——谱方法的意义是"插值多项式导数与动力学残差即离散化误差"。`GetNewMeshPoints` 的幂律 $e\propto (N/(N+\Delta N))^{p+1}$ 来自"p 阶方法误差随步长 $h^{p+1}$ 衰减"，是 Betts 书的标准做法；`orderReduction`（`GetOrderReduction` 第 1574~1612 行）用上一轮误差比反推实际阶，但注释明确说明因接口问题当前被屏蔽（第 1164~1185 行）。Radau 的误差积分用**微分矩阵求逆**（`integrationMatrix = newLagDiffMat2.Inverse()` 第 1417 行）把动力学积分回状态差，再与插值状态比较——这是 LGR 谱方法的自然误差量。网格细化由 `Phase::RefineMesh` 驱动、`Trajectory` 循环调用直至满足或达上限（见 [第15章](../CH15-csalt-interop-tests.md) 2.1.1 节）。

```cpp
// NLPFuncUtil_ImplicitRK.cpp:2170-2179（GetNewMeshPoints：按误差幂律加节点）
Real newDError = relErrorTol*1000.0;
AddNodeNum = 0;
while (AddNodeNum < maxAddNodeNumPerIntv && newDError > relErrorTol)
{
   AddNodeNum = AddNodeNum + 1;
   // 假设误差按 (N/(N+ΔN))^(p-ordRed+1) 衰减，反解所需新增节点数 ΔN
   Real tmp = double(meshNumPoints[intvIdx])
            / double(meshNumPoints[intvIdx] + AddNodeNum);
   newDError = maxError*(pow(tmp, (pValue - orderReduction + 1)));
}
totalAddNodeNum = AddNodeNum;
```

## 六、SNOPT 接口与 NLP 缩放

### SnoptOptimizer / SNOPTFunctionWrapper（非线性规划形式与回调）

- **公式**：CSALT 把问题写成 SNOPT 的标准 NLP 形式：

$$
\min_{x}\ F_1(x)\quad \text{s.t.}\quad \ell \le F(x) \le u,\ \ x_L\le x\le x_U
$$

其中 $x=$ 缩放后的决策向量、$F=(F_1,\dots,F_{m+1})^T$ 第 1 行为目标（"Objective row"=1）、其余为约束（缺陷/代数路径/多点）；雅可比按稀疏三向量 $(iGfun, jGvar, G)$ 提交，$G_k = \partial F_{iGfun_k}/\partial x_{jGvar_k}$。

- **代码位置**：`src/csalt/src/executive/SnoptOptimizer.cpp:109-140`（`Initialize`：`Derivative Option=2`、`Scale Option=1`、`Objective row=1`、`setUserFun(SNOPTFunctionWrapper)` 第 115~138 行）、`:322-538`（`Optimize`：Rvector→std::vector 拷贝第 371~398 行、`setX/setF` 第 401~406 行、`GetSparsityPattern` 填 `iGfun/jGvar` 第 422~448 行、`setProblemSize` 第 450 行、`Problem.solve(0)` 第 456 行、退出码分类第 475~504 行）；`src/csalt/src/util/SNOPTFunctionWrapper.cpp:57-194`（回调：反缩放决策向量第 93~96 行 → `SetDecisionVector` 第 107 行 → `GetCostConstraintFunctions` 第 110 行 → 缩放第 119~122 行 → 填 F 第 129~132 行 → `GetJacobian` 第 144 行 → 缩放第 146~154 行 → 按 `iGfun/jGvar` 填 G 第 174~178 行）；`src/csalt/src/executive/SnoptOptimizer.hpp:97-98`（`iGfun/jGvar` 成员）

- **深度讲解**：SNOPT 是稀疏 SQP：每次主迭代回调 `SNOPTFunctionWrapper` 求 $F$ 与 $G$。回调的"缩放对称性"值得注意：SNOPT 内部工作在缩放空间，CSALT 内部存有量纲数据（[第15章](../CH15-csalt-interop-tests.md) 2.1.1 节引用的 Trajectory 注释），所以回调入口先 `UnScaleDecisionVector`（第 95 行）把 $x$ 还原成量纲决策向量，出口再 `ScaleCostConstraintVector` / `ScaleJacobian`（第 121、153 行）把 $F,G$ 缩放回 SNOPT 空间。`Optimize` 里 `GetSparsityPattern(&sPatternMat, iGfun, jGvar)`（第 428 行）把 RSMatrix 稀疏模式导出成行/列索引，`setG`（第 447~448 行）告知 SNOPT 非线性雅可比的非零位置；由于 CSALT 假定全部约束非线性（第 408~414 行注释），线性矩阵 A 为空（`lenA=0`）。`setProblemSize(decVec.GetSize(), F.GetSize())`（第 450 行）给出 $n$ 与 $m+1$。退出码按 SNOPT 惯例映射（第 475~504 行：1~9 最优、31~39 资源受限、41~49 数值困难、71/74 用户终止），`exitFlag` 直接透传，供 `Trajectory` 决定是否进入网格细化分支。

```cpp
// SNOPTFunctionWrapper.cpp:93-153（回调：缩放空间 ↔ 量纲空间的双向转换）
if (Opt->traj->GetIfScaling())
{
   // SNOPT 给的 x 是缩放后的 → 先还原成量纲决策向量
   Opt->traj->GetScaleHelper()->UnScaleDecisionVector(DecVec);
}
Opt->traj->SetDecisionVector(DecVec);            // 写回决策向量（触发重算）
CostConstraint = Opt->traj->GetCostConstraintFunctions();  // 量纲 F
if (Opt->traj->GetIfScaling())
{
   // 目标+约束统一缩放（首元素按 costWeight、其余按 conVecWeight）
   Opt->traj->GetScaleHelper()->ScaleCostConstraintVector(CostConstraint);
}
for (int k = 0; k < *nF; k++) F[k] = CostConstraint[k];   // 填 F
Jacobian = Opt->traj->GetJacobian();             // 量纲雅可比
if (Opt->traj->GetIfScaling())
   Opt->traj->GetScaleHelper()->ScaleJacobian(Jacobian);
for (UnsignedInt k = 0; k < Opt->iGfun.size(); k++)
   G[k] = Jacobian(Opt->iGfun[k]-1, Opt->jGvar[k]-1);     // 按稀疏索引填 G
```

### ScaleUtility（NLP 缩放：决策向量 / 约束 / 代价 / 雅可比）

- **公式**：仿射缩放 $x_s = w\odot x + s$，其中由上下界确定的权重/平移把 $[x_L,x_U]$ 映射到 $[-\tfrac12,\tfrac12]$：

$$
w_i = \frac{1}{x_{U,i}-x_{L,i}},\qquad s_i = \tfrac12 - x_{U,i}\,w_i
$$

约束缩放 $c_s = w_c\odot c$（$w_c$ 取雅可比行范数倒数 $1/\|J_{i,:}\|$，或缺陷行取对应状态分量的 $w$）；代价缩放 $J_s = w_{\text{cost}} J$；雅可比缩放（链式法则）：

$$
J_s(i,j) = J(i,j)\,\frac{w_c(i)}{w(j)}
$$

- **代码位置**：`src/csalt/src/util/ScaleUtility.cpp:144-178`（`Initialize`：权重置 1、平移置 0）、`:191-197`（`ScaleDecisionVector`：$w x + s$）、`:210-216`（`UnScaleDecisionVector`：$(x-s)/w$）、`:229-242`（`ScaleConstraintVector`：`conVec·conVecWeight(conIdx+1)`）、`:281-284`（`ScaleCostFunction`：`cost*costWeight`）、`:341-363`（`ScaleJacobian`：`jac·conVecWeight(funIdx)/decVecWeight(varIdx)`）、`:411-423`（`SetDecVecScalingBounds`：上式）、`:475-513`（`SetConstraintScalingJacobian`：行范数倒数，`normRow=1/rowVec.GetMagnitude()` 第 502 行）、`:530-579`（`SetConstraintScalingDefectAndUser`：缺陷行用 `decVecWeight(whichStateVar+2)`、非缺陷行用行范数，第 550~574 行）

- **深度讲解**：CSALT 的缩放分三层：**(1) 决策向量**用上下界仿射映射（`SetDecVecScalingBounds`），保证每个决策分量缩放后量级 $O(1)$；**(2) 约束**按雅可比行范数归一（`SetConstraintScalingJacobian`），使缩放后每行雅可比范数 ≈1，改善 SNOPT 的罚函数与步长；缺陷约束特殊处理（`SetConstraintScalingDefectAndUser`）：缺陷行的量纲与对应状态分量一致，直接用该状态的缩放权重（第 550~554 行），避免行范数在稀疏行上失真；**(3) 雅可比**在 `ScaleJacobian` 里按"函数权重/变量权重"逐非零元缩放（第 356~362 行）——这正是 $J_s=\partial(c_s)/\partial x_s$ 的链式法则。缩放权重存放在 `conVecWeight(0)=costWeight`、`conVecWeight(1..numCons)` 的错位数组里（第 161~168 行），`ScaleCostConstraintVector` 统一处理"代价+约束"混合向量（第 316~328 行）。注意 `SetDecVecScalingBounds` 须先于约束缩放调用（注释第 468 行），因为约束行范数是在决策向量已缩放的前提下计算的。

```cpp
// ScaleUtility.cpp:416-422（SetDecVecScalingBounds：上下界 → 权重/平移）
for (Integer varIdx = 0; varIdx < numVars; varIdx++)
{
   // w = 1/(ub-lb)：把区间宽度归一
   decVecWeight(varIdx) = 1.0 / (decVecUpper(varIdx) - decVecLower(varIdx));
   // s = 0.5 - ub·w：把上界平移到 0.5（区间映射到 [-0.5, 0.5]）
   decVecShift(varIdx)  = 0.5 - decVecUpper(varIdx) * decVecWeight(varIdx);
}
```

### ScalingUtility（单位制缩放：DU/TU/VU 等）

- **公式**：按命名单位缩放 $x_s = (x - \text{shift})/\text{factor}$，反缩放 $x = x_s\cdot\text{factor}+\text{shift}$；雅可比缩放为因子比：

$$
J_s(i,j) = J(i,j)\,\frac{\text{factor}_{\text{var},j}}{\text{factor}_{\text{fun},i}}
$$

内置七个无量纲单位 `DU/TU/VU/MU/ACCU/MFU`（初值 factor=1、shift=0），`SetUnit/SetShift` 按需修改，`AddUnitAndShift` 支持新增单位。

- **代码位置**：`src/csalt/src/util/ScalingUtility.cpp:47-56`（构造：注册 6 个默认单位）、`:122-136`（`SetUnit`）、`:183-203`（`AddUnitAndShift`：不存在则插入）、`:222-231`（`ScaleParameter`：$(x-\text{shift})/\text{factor}$）、`:236-245`（`UnscaleParameter`）、`:315-356`（`ScaleJacobian`：`unscaled·factor_var/factor_fun` 第 346~347 行）、`:434-476`（`UnscaleJacobian` 逆操作）、头文件 `ScalingUtility.hpp:80-81`（`unitFactors/unitShifts` 两个 map）

- **深度讲解**：`ScaleUtility` 处理"数值缩放"，`ScalingUtility` 处理"单位换算"——后者维护一个 `<单位名 → (factor, shift)>` 表，供 `OrbitPhase` 等把 GMAT 的有量纲量（如距离 DU、时间 TU）换算成无量纲决策变量。`ScaleParameter` 的仿射式与 `ScaleUtility` 决策向量缩放同构但语义不同：这里是"物理单位→规范化单位"，shift 用于温度等非零基准。`ScaleJacobian` 的因子比公式正是 $d(\text{fun})/d(\text{var})$ 的单位换算：分子乘变量因子、分母除函数因子（第 346~347 行）；`ScaleJacobianByVars/ByFun` 提供单侧缩放变体（第 362~392、398~428 行）。

```cpp
// ScalingUtility.cpp:222-231（ScaleParameter：单位制缩放）
Real ScalingUtility::ScaleParameter(const Real &unscaled,
                                    const std::string &unit)
{
   Real scaled;
   if (ValidateUnit(unit))
      scaled = (unscaled - unitShifts.at(unit)) / unitFactors.at(unit);
      // 仿射单位换算：先平移（去基准）再除以因子（去量纲）
   else // unit invalid - no scaling
      scaled = unscaled;
   return scaled;
}
```

## 七、稀疏矩阵工具

### SparseMatrixUtil（RSMatrix 稀疏矩阵工具集）

- **公式**：全库稀疏矩阵类型别名（`SparseMatrixUtil.hpp:55-59`）：

$$
\text{RSMatrix} \equiv \texttt{boost::numeric::ublas::compressed\_matrix<Real>}
$$

核心操作：稀疏×稠密向量积 $r = M\,v$（`fast_prod`，第 1209 行 `result[i1.index1()] += (*i2)*(*vec)[i2.index2()]`）；稀疏块装配 $M(r_{\text{off}}+i,\ c_{\text{off}}+j) \mathrel{+}= B_{ij}$（`SetSparseBLockMatrix`，`isNotAdding=false` 时累加）；三向量导出 $(i,j,v)$ 集合（`GetThreeVectorForm`，供 SNOPT `iGfun/jGvar`）；模式矩阵（全 1）提取（`GetSparsityPattern`）。

- **代码位置**：`src/csalt/src/util/SparseMatrixUtil.hpp:55-59`（类型别名）、`:77-93`（`SetElement/SetSize/SetSparsityPattern`）、`:112-143`（`SetSparseBLockMatrix` 重载）、`:163-180`（`GetThreeVectorForm`）、`:207-226`（`fast_prod` 声明）；`src/csalt/src/util/SparseMatrixUtil.cpp:342-405`（`SetSparseBLockMatrix`：偏移寻址 + `isNotAdding` 分支）、`:842-872`（`GetThreeVectorForm`：遍历迭代器导出三向量）、`:1168-1212`（`fast_prod` 稠密向量版）、`:1294-1318`（`fast_prod` 稀疏×稀疏，用 `axpy_prod`）

- **深度讲解**：CSALT 的"稀疏"完全建立在 Boost.uBLAS 的 `compressed_matrix` 上（`SparseMatrixLibraryHeader.hpp` 聚合头），`SparseMatrixUtil` 是静态工具类（构造私有，不可实例化）。`fast_prod` 不调用 uBLAS 的 `prod`，而是手写迭代器双重循环——只访问非零元，复杂度 $O(\text{nnz})$，避免稠密临时量；`SetSparseBLockMatrix` 的 `isNotAdding` 语义（注释第 328~339 行）约定：`true` 覆盖、`false` 累加，且"覆盖不清除已有非零"——依赖"稀疏模式在整个 NLP 求解过程中不变"的假设（网格细化后才重设模式）。`GetThreeVectorForm` 是 SNOPT 接口的桥梁：`SnoptOptimizer.cpp:428` 用它把 `sPatternMat` 变成 `iGfun/jGvar`。Radau 微分矩阵的构造也大量依赖本工具（`RadauMathUtil.cpp` 的 `ReplicateSparseMatrix/SetSparseBLockMatrix`）。

```cpp
// SparseMatrixUtil.cpp:1203-1211（fast_prod：稀疏 × 稠密向量）
for (RSMatrix::const_iterator1 i1 = (*spMat).begin1();
     i1 != (*spMat).end1(); ++i1)
{
   for (RSMatrix::const_iterator2 i2 = i1.begin();
        i2 != i1.end(); ++i2)
   {
      // 只遍历非零元：r[i] += M(i,j)·v[j]
      result[i1.index1()] += (*i2)*(*vec)[i2.index2()];
   }
}
```

## 八、公式索引表

| 公式 | 文件:行 | 所属类 |
|---|---|---|
| Butcher 表三元组 $(\rho,\Sigma,\beta)$ 成员 | `collutils/ImplicitRungeKutta.hpp:91-95` | ImplicitRungeKutta |
| 依赖块抽取 $aChunk=\text{patternA}\cdot I,\ bChunk=\text{patternB}\cdot I$ | `collutils/ImplicitRungeKutta.cpp:410-425` | ImplicitRungeKutta |
| 依赖模式 $\text{patternA}=\text{paramDepArray},\ \text{patternB}=\text{funcConstArray}$ | `collutils/ImplicitRungeKutta.cpp:442-466` | ImplicitRungeKutta |
| 分离形式函数向量 $\hat f=\Delta T\,f$ 压列 | `collutils/LobattoIIIASeparated.cpp:128-140` | LobattoIIIASeparated |
| 梯形表 $\rho=(0,1),\ \beta=(1/2,1/2),\ \sigma(1,:)=(1/2,1/2)$ | `collutils/LobattoIIIA_2Order.cpp:141-167` | LobattoIIIA_2Order |
| 梯形缺陷 $A=[-1,1]$、$-\sigma$ 函数系数 | `collutils/LobattoIIIA_2Order.cpp:119-127` | LobattoIIIA_2Order |
| 4 阶表 $\rho=(0,1/2,1)$、$\beta=(1/6,4/6,1/6)$ | `collutils/LobattoIIIA_4Order.cpp:151-184` | LobattoIIIA_4Order |
| 4 阶缺陷 $A=[-1,1,0;-1,0,1]$、$-\sigma/-\beta$ | `collutils/LobattoIIIA_4Order.cpp:121-136` | LobattoIIIA_4Order |
| Hermite-Simpson 压缩缺陷 $A=[-1/2,1,-1/2;-1,0,1]$、函数系数 $[-1/8,0,1/8]$ | `collutils/LobattoIIIA_4HSOrder.cpp:121-140` | LobattoIIIA_4HSOrder |
| Hermite-Simpson 表（同 4 阶） | `collutils/LobattoIIIA_4HSOrder.cpp:155-188` | LobattoIIIA_4HSOrder |
| 6 阶表 $\rho=(0,\tfrac12\mp\tfrac{\sqrt5}{10},1)$、$\beta=(1/12,5/12,5/12,1/12)$ | `collutils/LobattoIIIA_6Order.cpp:160-203` | LobattoIIIA_6Order |
| 6 阶缺陷三行依赖阵 | `collutils/LobattoIIIA_6Order.cpp:121-145` | LobattoIIIA_6Order |
| 8 阶表 $\rho=(0,\tfrac12\mp\tfrac{\sqrt{21}}{14},\tfrac12,1)$、$\beta=(1/20,49/180,16/45,49/180,1/20)$ | `collutils/LobattoIIIA_8Order.cpp:172-226` | LobattoIIIA_8Order |
| 8 阶缺陷四行依赖阵 | `collutils/LobattoIIIA_8Order.cpp:122-157` | LobattoIIIA_8Order |
| Hermite 系数求值 $p(t)=\sum c_k t^{n-1-k}$、$p'(t)=\sum (n-1-k)c_k t^{n-2-k}$ | `util/LobattoIIIaMathUtil.cpp:252-288` | LobattoIIIaMathUtil |
| 重节点均差构造 $z=[t_0,t_0,\dots]$、牛顿多项式 | `util/LobattoIIIaMathUtil.cpp:305-398` | LobattoIIIaMathUtil |
| LGR 节点 Newton 迭代 $\tau\leftarrow\tau-\frac{1-\tau}{N+1}\frac{P_N+P_{N+1}}{P_N-P_{N+1}}$ | `util/RadauMathUtil.cpp:401-405` | RadauMathUtil |
| Legendre 三项递推 $P_{k+1}=\frac{(2k+1)xP_k-kP_{k-1}}{k+1}$ | `util/RadauMathUtil.cpp:388-398` | RadauMathUtil |
| LGR 权重 $w_0=2/(N+1)^2,\ w_j=(1-\tau_j)/((N+1)P_N)^2$ | `util/RadauMathUtil.cpp:414-423` | RadauMathUtil |
| 重心微分矩阵 $D_{ij}=\frac{w_j/w_i}{x_i-x_j}$、对角 $1-\sum$ | `util/RadauMathUtil.cpp:96-166` | RadauMathUtil |
| 分段 LGR 仿射映射 $x\mapsto\frac{a+b}{2}+\frac{b-a}{2}x$ 与块拼接 | `util/RadauMathUtil.cpp:263-301` | RadauMathUtil |
| 重心权重 $w_j=1/\prod_{k\ne j}(x_j-x_k)$ | `util/BaryLagrangeInterpolator.cpp:616-624` | BaryLagrangeInterpolator |
| 插值矩阵 $M_{rj}=\frac{w_j}{y_r-x_j}/\sum_k\frac{w_k}{y_r-x_k}$ | `util/BaryLagrangeInterpolator.cpp:586-601` | BaryLagrangeInterpolator |
| 插值 $L(y_r)=\sum_j M_{rj}f_j$ | `util/BaryLagrangeInterpolator.cpp:309-323` | BaryLagrangeInterpolator |
| 两步初始化 + 求值流水线 | `collutils/NLPFuncUtil_Coll.cpp:242-265,435-492` | NLPFuncUtil_Coll |
| $\text{nlpFuncs}=AZ+BQ$、$\text{nlpJac}=A+BQ_{\text{mat}}$、稀疏 $=A+BD$ | `collutils/NLPFunctionData.hpp:44-49` | NLPFunctionData |
| $A Z + B Q$ 两次 `fast_prod` 累加 | `collutils/NLPFunctionData.cpp:526-539` | NLPFunctionData |
| 雅可比 $A + B\cdot Q_{\text{mat}}$ | `collutils/NLPFunctionData.cpp:579-591` | NLPFunctionData |
| 稀疏模式 $A + B\cdot D$ | `collutils/NLPFunctionData.cpp:602-617` | NLPFunctionData |
| IRK 缺陷 $\zeta_i=\sum_j A_{ij}y_j-h\sum_j\Sigma_{ij}f_j$（$B=-bChunk\cdot h_s$、$Q=-\Delta T f$） | `collutils/NLPFuncUtil_ImplicitRK.cpp:662-679,806` | NLPFuncUtil_ImplicitRK |
| IRK 维度 $N_\text{def}=n_x(N_\text{mesh}-1)$、$p=N_\text{ptsPerStep}-1$ | `collutils/NLPFuncUtil_ImplicitRK.cpp:219-250` | NLPFuncUtil_ImplicitRK |
| Butcher 表选择（RungeKutta8/6/4、HermiteSimpson、Trapezoid） | `collutils/NLPFuncUtil_ImplicitRK.cpp:565-605` | NLPFuncUtil_ImplicitRK |
| IRK 时间偏导 $\partial t_k/\partial t_0=1-\rho_k$、$\partial t_k/\partial t_f=\rho_k$ | `collutils/NLPFuncUtil_ImplicitRK.cpp:360-383` | NLPFuncUtil_ImplicitRK |
| IRK 代价求积 $J=\sum_j\beta_j h f_j$ | `collutils/NLPFuncUtil_ImplicitRK.cpp:931-947` | NLPFuncUtil_ImplicitRK |
| LGR 缺陷 $D\,Y-\frac{\Delta T}{2}f=0$（A=微分矩阵、B=I） | `collutils/NLPFuncUtilRadau.cpp:930-942` | NLPFuncUtilRadau |
| LGR Q 向量 $Q=-\frac{\Delta T}{2}f$ 与时间偏导项 | `collutils/NLPFuncUtilRadau.cpp:1544,1616-1631` | NLPFuncUtilRadau |
| LGR 时间映射 $t=\frac{\Delta T}{2}(\tau+1)+t_0$、$\partial t/\partial t_{0,f}=\frac{1\mp\tau}{2}$ | `collutils/NLPFuncUtilRadau.cpp:326-336,206-229` | NLPFuncUtilRadau |
| LGR 维度 $N_\text{state}=N_\text{mesh}+1$、末点无控制 | `collutils/NLPFuncUtilRadau.cpp:268-306` | NLPFuncUtilRadau |
| IRK 网格细化幂律 $e_{\text{new}}=e_{\max}(N/(N+\Delta N))^{p+1}$ | `collutils/NLPFuncUtil_ImplicitRK.cpp:2174-2179` | NLPFuncUtil_ImplicitRK |
| IRK 误差被积函数 $\|\dot y_{\text{pseudo}}-\Delta T f\|/\Delta T$ | `collutils/NLPFuncUtil_ImplicitRK.cpp:1844-1850` | NLPFuncUtil_ImplicitRK |
| Romberg 积分外推 $R_{k,m}=\frac{4^mR_{k,m-1}-R_{k-1,m-1}}{4^m-1}$ | `collutils/NLPFuncUtil_ImplicitRK.cpp:1945-1950` | NLPFuncUtil_ImplicitRK |
| Radau 误差 $e=\frac{\max|y_i-y_{i0}-\frac{\Delta T}{2}D^{-1}f_i|}{1+\max|y_i|}$ | `collutils/NLPFuncUtilRadau.cpp:1440-1478` | NLPFuncUtilRadau |
| Radau 升阶 $N'=N+\lceil\log(e/\text{tol})/\log N\rceil$ | `collutils/NLPFuncUtilRadau.cpp:466-471` | NLPFuncUtilRadau |
| IRK 装配入口（默认 RungeKutta8） | `executive/ImplicitRKPhase.cpp:91-109` | ImplicitRKPhase |
| Radau 装配入口 | `executive/RadauPhase.cpp:107-121` | RadauPhase |
| Betts 排布 $Z=[t_0\ t_f\ y_{10}\ u_{10}\ \cdots\ s\ w]$ | `collutils/DecVecTypeBetts.hpp:27-30` | DecVecTypeBetts |
| NLP 形式 $\min F_1,\ \ell\le F\le u$、Objective row=1 | `executive/SnoptOptimizer.cpp:115-138,400-456` | SnoptOptimizer |
| 回调的缩放空间↔量纲空间双向转换 | `util/SNOPTFunctionWrapper.cpp:93-153` | SNOPTFunctionWrapper |
| 决策向量缩放 $x_s=wx+s$、$w=1/(u-l)$、$s=0.5-uw$ | `util/ScaleUtility.cpp:191-197,411-423` | ScaleUtility |
| 雅可比缩放 $J_s=J\cdot w_c/w_v$ | `util/ScaleUtility.cpp:341-363` | ScaleUtility |
| 约束行范数缩放 $w_c=1/\|J_{i,:}\|$、缺陷行用状态权重 | `util/ScaleUtility.cpp:475-513,530-579` | ScaleUtility |
| 单位缩放 $x_s=(x-\text{shift})/\text{factor}$、$J_s=J\cdot f_v/f_f$ | `util/ScalingUtility.cpp:222-231,315-356` | ScalingUtility |
| RSMatrix 类型别名、`fast_prod` $r=Mv$ | `util/SparseMatrixUtil.hpp:55-59`、`util/SparseMatrixUtil.cpp:1203-1211` | SparseMatrixUtil |
| 稀疏块装配与三向量导出 | `util/SparseMatrixUtil.cpp:342-405,842-872` | SparseMatrixUtil |
