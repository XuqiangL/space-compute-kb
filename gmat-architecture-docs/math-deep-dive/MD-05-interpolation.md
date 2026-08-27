# 第5章 插值、样条与切比雪夫数学

本章范围：GMAT 中全部插值数学的公式级解析。覆盖 `src/gmatutil/util/interpolator/` 的 Interpolator 基类与 LagrangeInterpolator / NotAKnotInterpolator / CubicSplineInterpolator / HermiteInterpolator / LinearInterpolator 五个派生类，`src/gmatutil/util/CubicSpline.*` 的 clamped 样条工具单例，`src/base/solarsys/DeFile.*` 的 DE 星历切比雪夫插值，`src/csalt/src/util/BaryLagrangeInterpolator.*` 的重心拉格朗日插值，`src/base/stopcond/StopCondition.*` 用样条反求穿越历元的部分，以及 `plugins/EphemPropagatorPlugin` 中 Code500 传播器对 NotAKnot 的使用。每条目严格按「公式 / 代码位置 / 深度讲解」三要素组织；所有行号均经 read 逐一核对。

> 术语约定：`ind`＝插值自变量（通常为 A1MJD 或秒），`bufferSize`＝环形缓冲容量，`requiredPoints`＝完成一次插值所需点数，`order`＝多项式阶数，`pointCount`＝已喂入点数。传播/停止条件层面的调用链见 [第7章](../CH07-propagator.md)，CSALT 配点法与 LGR 节点背景见 [第15章](../CH15-csalt-interop-tests.md)，本章只做公式与实现深挖，不重复那两章的大段流程描述。

## 5.0 导览：GMAT 的三大插值场景

| 场景 | 位置 | 选用的插值器 |
| --- | --- | --- |
| 星历读取（DE 切比雪夫 / SPK 多项式 / Code500 采样点） | `src/base/solarsys/DeFile.cpp`、`src/gmatutil/util/Ephemeris.cpp`、`plugins/EphemPropagatorPlugin/.../Code500Propagator.cpp` | 切比雪夫求和、Hermite/Lagrange、NotAKnot |
| 停止条件精确穿越历元 | `src/base/stopcond/StopCondition.cpp` | NotAKnot（默认） |
| 输出插值（EphemWriter / TextEphemFile / TrajectoryData） | `src/base/subscriber/EphemWriterWithInterpolator.cpp`、`src/base/subscriber/TextEphemFile.cpp`、`src/csalt/src/util/TrajectoryData.cpp` | Lagrange（dim=30）、CubicSpline、Linear 等 |

三个场景共享同一套 `Interpolator` 基类协议（`AddPoint` 喂点 → `Interpolate` 取值），但数学内核完全不同：多项式基（Lagrange）、分段多项式（样条）、正交多项式（切比雪夫）、重心形式（barycentric）。下面逐条展开。

## 5.1 gmatutil 插值器家族（`src/gmatutil/util/interpolator/`）

### 条目 5.1.1 Interpolator 基类：AddPoint / Interpolate 协议与环形缓冲

- **公式**：基类不承载具体插值公式（`Interpolate` 为纯虚函数，`Interpolator.hpp:83`），它定义的是数据组织协议与可行性检查框架。核心数据不变量：
  - 环形缓冲写入：$x[\text{latestPoint}\leftarrow\text{latestPoint}+1\ \bmod\ \text{bufferSize}] = \text{ind}$（`Interpolator.cpp:205-211`）；
  - 单调方向判定：$\text{dataIncreases} = (\text{ind} > \text{previousX})$（`Interpolator.cpp:208`）；
  - 有效范围：$\text{range}[0]=\min x_i,\ \text{range}[1]=\max x_i$（`Interpolator.cpp:460-481`）。

- **代码位置**：
  - 类声明：`src/gmatutil/util/interpolator/Interpolator.hpp:43-130`（协议方法 53-63 行，数据成员 90-130 行）
  - 环形缓冲写入：`src/gmatutil/util/interpolator/Interpolator.cpp:197-223`
  - 可行性默认实现：`src/gmatutil/util/interpolator/Interpolator.cpp:239-242`
  - 范围扫描：`src/gmatutil/util/interpolator/Interpolator.cpp:460-481`
  - 数组分配/释放：`src/gmatutil/util/interpolator/Interpolator.cpp:391-430`

- **深度讲解**：

  **数值分析背景**：基类是"插值器工厂协议"而非算法。它把三类职责固定下来：(a) 数据缓冲（喂点、计数、环回）；(b) 可行性（点数是否足够、`ind` 是否越界）；(c) 派生类数学（纯虚 `Interpolate`）。这种设计与数值分析无关，但与工程复用强相关——星历读取、停止条件、输出文件三处调用方只依赖 `Interpolator*` 接口，可在不改调用代码的前提下替换算法（见 `StopCondition::SetInterpolator`，`StopCondition.cpp:1539`）。

  **实现细节**：AddPoint 是全部后续算法的入口，关键片段（`Interpolator.cpp:197-223`）：

  ```cpp
  bool Interpolator::AddPoint(const Real ind, const Real *data)
  {
     Integer i;
     if (!independent)          // 首次调用时按 bufferSize 分配一维/二维数组
        AllocateArrays();
     if (latestPoint == bufferSize-1)   // 到达缓冲末尾则回绕（环形）
        latestPoint = -1;
     dataIncreases = (ind > previousX ? true : false);  // 判定数据递增/递减方向
     previousX = ind;
     independent[++latestPoint] = ind;          // 写入自变量
     for (i = 0; i < dimension; ++i)            // 逐维写入因变量
        dependent[latestPoint][i] = data[i];
     ++pointCount;                              // 有效点数计数
     rangeCalculated = false;                   // 范围缓存失效，下次 GetRange 重扫
     return true;
  }
  ```

  - `previousX` 初始化为 `-9.9999e65`（`Interpolator.cpp:54`），保证首个点的 `dataIncreases=true`；
  - `dataIncreases` 是向后传播支持的关键：样条类用它对环形缓冲做"按方向排序"（见 5.1.3 的 `LoadArrays`）；
  - `Clear()`（`Interpolator.cpp:308-314`）只重置指针与计数、不释放内存，以便复用缓冲；
  - 基类 `requiredPoints=2`、`bufferSize=2`（`Interpolator.cpp:56-57`），派生类各自改写（Lagrange 8/80、NotAKnot 5/5、CubicSpline 5/5、Hermite `pointsWanted+1`）。

  **节点管理（AddPoint/Interpolate 协议）**：调用方按时间顺序喂入 (ind, data) 对；插值时只保证缓冲内有 `requiredPoints` 个点，不保证 `ind` 在缓冲中央——"居中"是各派生类的内部优化（见 5.1.2 的 `FindStartingPoint` 与 5.5 的 sweet-spot 选择）。

  **阶数与精度**：基类不决定精度；精度由派生类阶数与数据密度决定（见各条目）。

  **使用场景**：所有插值器的共同祖先；`InterpolatorException`（`src/gmatutil/util/interpolator/InterpolatorException.hpp:37-44`）在点数不足等场景抛出，调用方（如 `StopCondition.cpp:189`、`LinearInterpolator.cpp:112`）可捕获或让其上抛。

### 条目 5.1.2 LagrangeInterpolator：居中窗口的拉格朗日插值

- **公式**：设窗口内节点 $x_{s}, x_{s+1}, \dots, x_{s+o}$（$o$ 为阶数，点数 $o+1$），拉格朗日基函数与插值多项式为

  $$
  L_i(x)=\prod_{\substack{j=s\\ j\neq i}}^{s+o}\frac{x-x_j}{x_i-x_j},\qquad
  P(x)=\sum_{i=s}^{s+o} y_i\,L_i(x)
  $$

  代码以连乘方式逐项构造（`LagrangeInterpolator.cpp:524`）：`products[dim] *= (ind - x[j]) / (x[i] - x[j])`，即每个 $y_i$ 依次乘以所有 $j\neq i$ 的基因子；最后累加 `estimates[dim] += products[dim]`（`LagrangeInterpolator.cpp:553`）。阶数 $o$ 默认 7（8 点），`requiredPoints = order + 1`（`LagrangeInterpolator.cpp:75`）。

- **代码位置**：
  - 构造函数与缓冲尺寸：`src/gmatutil/util/interpolator/LagrangeInterpolator.cpp:58-87`（`requiredPoints=order+1` 在 75 行，`bufferSize = requiredPoints*10` 封顶 `MAX_BUFFER_SIZE=80` 在 76-78 行）
  - 核心乘积求值：`src/gmatutil/util/interpolator/LagrangeInterpolator.cpp:494-555`（零分母警告 517-523，基因子连乘 524）
  - 居中窗口选择 `UpdateBeginAndEndIndex`：`src/gmatutil/util/interpolator/LagrangeInterpolator.cpp:764-821`
  - 起始点搜索 `FindStartingPoint`：`src/gmatutil/util/interpolator/LagrangeInterpolator.cpp:868-933`
  - 可行性检查 `IsInterpolationFeasible`：`src/gmatutil/util/interpolator/LagrangeInterpolator.cpp:177-280`
  - 降阶 `AdjustOrderToNumPoints`：`src/gmatutil/util/interpolator/LagrangeInterpolator.cpp:295-306`
  - 环形缓冲→有序数组 `BuildDataPoints`：`src/gmatutil/util/interpolator/LagrangeInterpolator.cpp:702-752`

- **深度讲解**：

  **数值分析背景（Runge 现象）**：等距节点上的高次拉格朗日多项式在区间端点附近会产生剧烈振荡（Runge 现象），误差不收敛。GMAT 的应对不是换节点，而是**限制阶数并保持 $x$ 居中**：(a) 默认 $o=7$（8 点窗口），阶数不随数据量增长；(b) 缓冲扩容到 10 倍阶数（`LagrangeInterpolator.cpp:76`），使窗口可以从更多候选中挑选"目标居中"的一段，把 Runge 振荡压到窗口之外；(c) 数据近两端时窗口被迫靠边，`IsDataNearCenter`（`LagrangeInterpolator.cpp:831-857`）与 `forceInterpolation` 标志配合，宁可返回 false 也不在病态位置强行插值（`LagrangeInterpolator.cpp:425-436`）。

  **实现细节**——居中窗口三连（数值核心）：

  ```cpp
  // UpdateBeginAndEndIndex 片段（LagrangeInterpolator.cpp:778-813）
  dataIndex = 0;
  Real distToDataIndex = fabs(x[dataIndex] - ind);
  for (Integer i = 1; i < actualSize; i++)
     if (fabs(x[i] - ind) < distToDataIndex) {   // 找离 ind 最近的节点
        dataIndex = i;  distToDataIndex = fabs(x[i] - ind); }
  if (requiredPoints % 2 == 0)                   // 偶数点数：目标落在窗口"中间偏右"
  {
     beginIndex = dataIndex - requiredPoints / 2;
     if (dataIncreases)
        if (x[dataIndex] < ind)  beginIndex += 1;
  }
  else                                           // 奇数点数：目标居中
     beginIndex = dataIndex - (requiredPoints - 1) / 2;
  if (beginIndex < 0)  beginIndex = 0;           // 越界钳制
  endIndex = beginIndex + requiredPoints - 1;
  if (endIndex >= actualSize)                    // 右侧越界则整体左移
  {  endIndex = actualSize - 1;
     beginIndex = endIndex - requiredPoints + 1; }
  ```

  偶数点数时 `beginIndex += 1` 是为了让 $x$ 落在窗口中心偏左的节点区间内（8 点窗口的"中心点"在 4、5 号节点之间，取偏右可让目标落入 4~5 之间的区间）。随后 `FindStartingPoint`（`LagrangeInterpolator.cpp:868-933`）在 `[beginIndex, beginIndex+order]` 内枚举 $q$，最小化 $|\frac{x_{q+o}+x_q}{2}-x|$（886-893 行），即选"节点均值最接近目标"的窗口起点；末尾再做越界钳制与 `startPoint = beginIndex` 兜底（920-924 行）。

  **节点管理（AddPoint/Interpolate 协议）**：`AddPoint` 直接复用基类环形缓冲（`LagrangeInterpolator.cpp:360`）；每次 `Interpolate` 先把环形缓冲按时间方向重排进有序数组 `x[]/y[]`（`BuildDataPoints`，`LagrangeInterpolator.cpp:702-752`，`actualSize = min(bufferSize, pointCount)` 在 713-715 行），再选窗求值。`Clear()`（`LagrangeInterpolator.cpp:315-325`）额外把 `x[]` 填回哨兵值 `-9.9999e75` 以便检测"空槽"（`Interpolate` 内 486-488 行据此收缩 `endPoint`）。

  **阶数与精度**：$o$ 阶多项式对充分光滑函数截断误差 $O(h^{o+1})$（$h$ 为节点间距）；默认 8 点窗口对位置/姿态这类随 A1MJD 平滑变化的数据，误差随 $h^{8}$ 衰减，实际量级由数据光滑度与节点密度共同决定。`AdjustOrderToNumPoints`（`LagrangeInterpolator.cpp:295-306`）在点数不足时临时降阶（`order = pointCount-1`），下次 `Interpolate` 自动恢复基准阶（`resetToBaseOrder` 机制，`LagrangeInterpolator.cpp:186-190, 395`）。

  **使用场景**：`src/gmatutil/util/Ephemeris.cpp:355`（SPK 风格星历、`useHermite=false` 时按 `maxOrder` 建 6 维 Lagrange）；`src/base/subscriber/EphemWriterWithInterpolator.cpp:271`（输出星历插值，dim=30＝位置/速度/加速度 9 + 协方差下三角 21，`SetForceInterpolation(false)` 在 278 行）；`src/base/coordsystem/IAUFile.cpp:205` 与 `ICRFFile.cpp:219`（IAU/ICRF 定向参数表插值）；`src/base/spacecraft/Spacecraft.cpp:2248,2449`（质心/MOI 曲线插值）；`src/csalt/src/util/TrajectoryData.cpp:1152`（CSALT 轨迹输出，`interpPoints=80`）。

### 条目 5.1.3 NotAKnotInterpolator：not-a-knot 边界条件的 5 点三次样条

- **公式**：5 个节点 $x_0<\cdots<x_4$ 构成 4 段三次样条，每段写成幂基：

  $$
  S_j(x)=a_j\,(x-x_j)^3 + b_j\,(x-x_j)^2 + c_j\,(x-x_j) + d_j,\quad j=0,\dots,3
  $$

  以二阶矩 $s_j=S''(x_j)$ 为未知量，节点间距 $h_j=x_{j+1}-x_j$、一阶差商 $\delta_j=(y_{j+1}-y_j)/h_j$。内点弯矩方程（$i=1,2,3$）：

  $$
  h_{i-1}s_{i-1}+2(h_{i-1}+h_i)s_i+h_i s_{i+1}=6(\delta_i-\delta_{i-1})
  $$

  not-a-knot 边界条件（端点处前两段/后两段共享同一三次多项式，即 $x_1$、$x_3$ 处三阶导数连续）：

  $$
  s_1=\frac{h_1 s_0+h_0 s_2}{h_0+h_1},\qquad
  s_3=\frac{h_3 s_2+h_2 s_4}{h_2+h_3}
  $$

  代入后得到只含 $(s_0,s_2,s_4)$ 的 3×3 线性系统（代码 `A[2][1]` 即推导出的组合系数），Cramer 法则求解（`NotAKnotInterpolator.cpp:447-455`）。最后反代系数（`NotAKnotInterpolator.cpp:461-468`）：

  $$
  a_j=\frac{s_{j+1}-s_j}{6h_j},\quad b_j=\frac{s_j}{2},\quad
  c_j=\frac{y_{j+1}-y_j}{h_j}-\frac{h_j(2s_j+s_{j+1})}{6},\quad d_j=y_j
  $$

  求值（`NotAKnotInterpolator.cpp:567-568`）：`results[i] = a[kl]*dx³ + b[kl]*dx² + c[kl]*dx + d[kl]`，$dx=x-x_{kl}$。

- **代码位置**：
  - 类声明（5 节点、4 段系数数组、3×3 系统）：`src/gmatutil/util/interpolator/NotAKnotInterpolator.hpp:53-85`
  - 构造（`bufferSize=5, requiredPoints=5`）：`src/gmatutil/util/interpolator/NotAKnotInterpolator.cpp:53-74`
  - 系数组装 `BuildSplines`：`src/gmatutil/util/interpolator/NotAKnotInterpolator.cpp:396-472`（h/δ 401-411，A 阵 413-429，B 与 Cramer 解 441-455，s1/s3 457-459，a/b/c/d 461-468）
  - 求值 `Estimate`：`src/gmatutil/util/interpolator/NotAKnotInterpolator.cpp:524-572`
  - 环形缓冲重排 `LoadArrays`：`src/gmatutil/util/interpolator/NotAKnotInterpolator.cpp:482-505`

- **深度讲解**：

  **数值分析背景（样条 C2 连续性与边界条件）**：4 段三次多项式共 16 个未知系数；插值条件（每段两端取值，8 个约束）＋内点一阶、二阶连续（各 3 个约束，共 6 个）＝14 个约束，还差 2 个条件，这就是边界条件。三种经典选择：自然样条（$s_0=s_n=0$，见 5.1.4）、clamped 样条（给定端点一阶导数，见 5.1.5）、not-a-knot（端点处三阶连续）。not-a-knot 的优点是无需额外导数信息，且端点附近保真度高于自然样条。**注意**：`BuildSplines` 的文档注释（`NotAKnotInterpolator.cpp:389-391`）声称"自然样条"，但代码实际求解的是 not-a-knot 系统（s1/s3 的加权平均式 457-459 行正是 not-a-knot 条件），属注释与实现不符的历史遗留，以代码为准。

  **实现细节**——not-a-knot 系统的组装（`NotAKnotInterpolator.cpp:413-429`）：

  ```cpp
  A[0][0] = 2.0 * h[1] + h[0];        // 弯矩方程 i=1 代入 s1 后 s0 的系数
  A[0][1] = 2.0 * h[0] + h[1];        // 同式 s2 的系数（s1 被消去）
  A[0][2] = 0.0;
  A[1][0] = 0.0;
  A[1][1] = h[2] + 2.0 * h[3];        // 弯矩方程 i=3 代入 s3 后 s2 的系数
  A[1][2] = 2.0 * h[2] + h[3];        // 同式 s4 的系数
  Real denom = h[0] + h[1];           // h0+h1，用于 s1 的 not-a-knot 平均
  Real denom2 = h[2] + h[3];          // h2+h3，用于 s3 的 not-a-knot 平均
  A[2][0] = h[1]*h[1] / denom;        // 弯矩方程 i=2 代入 s1、s3 后 s0 系数
  A[2][1] = h[0]*h[1]/denom + 2.0*(h[1]+h[2]) + h[2]*h[3]/denom2;  // s2 系数
  A[2][2] = h[2]*h[2] / denom2;       // s4 系数
  ```

  推导核对：以 $i=1$ 的弯矩方程 $h_0s_0+2(h_0+h_1)s_1+h_1s_2=6(\delta_1-\delta_0)$ 代入 $s_1=\frac{h_1s_0+h_0s_2}{h_0+h_1}$，即得 $(h_0+2h_1)s_0+(2h_0+h_1)s_2=6(\delta_1-\delta_0)$，与 `A[0][0]=2h_1+h_0`、`A[0][1]=2h_0+h_1` 完全一致。$i=2$ 行同时代入 $s_1,s_3$ 得到 `A[2][*]` 三系数。随后 441-445 行组装 $B_0=6(\delta_1-\delta_0),\ B_1=6(\delta_3-\delta_2),\ B_2=6(\delta_2-\delta_1)$，447-455 行用 Cramer 法则（行列式 `detA` 在 431-436 行）解出 $s_0,s_2,s_4$，457-459 行回代 $s_1,s_3$，最后 461-468 行按上述公式生成 4 组 (a,b,c,d) 幂基系数。全程对 `dimension` 逐维并行，即 6 维状态与 1 维标量共用同一套矩阵、不同右端。

  **节点管理（AddPoint/Interpolate 协议）**：`LoadArrays`（`NotAKnotInterpolator.cpp:482-505`）与 Lagrange 的 `BuildDataPoints` 同思路：按 `dataIncreases` 方向在环形缓冲中找最小元素作起点（488-495 行），再顺序拷贝 5 点（497-504 行）。每次 `Interpolate` 都重算样条（无缓存），`lastX` 成员虽在头文件声明（`NotAKnotInterpolator.hpp:75`）但未用于跳过（对比 5.1.4 的 `CubicSplineInterpolator.cpp:300-302` 有 `lastX` 短路）。

  **阶数与精度**：三次样条对光滑函数截断误差 $O(h^4)$（全局），且因 C2 连续，导数估计（一阶/二阶）也收敛；5 点窗口覆盖 4 个星历采样区间（采样步长由文件头 `timeIntervalBetweenPoints_SEC` 给出，`Code500Propagator.cpp:795`），局部误差 $O(h^4)$ 远小于采样点自身的数值精度，具体水平随数据光滑度变化。与 5.1.4 的关键区别：not-a-knot 的端点行为优于自然样条（自然样条在端点有 $O(h^2)$ 的边界层误差），因此停止条件与 Code500 都选它做默认。

  **使用场景**：`StopCondition` 默认插值器（`StopCondition.cpp:175`，见 5.4）；`Code500Propagator` 星历状态插值（`Code500Propagator.cpp:874`，见 5.5）；`TrajectoryData` 的 `NOTAKNOT` 选项（`TrajectoryData.cpp:1147`）。

### 条目 5.1.4 CubicSplineInterpolator：Numerical Recipes 自然样条（5 点）

- **公式**：同样 5 节点 4 段三次样条，但改用 NR 的"二阶导数组 $y''_k$"表述与三对角分解。NR splint 求值式（`CubicSplineInterpolator.cpp:451-453`）：

  $$
  S(x)=a\,y_k + b\,y_{k+1} + \big((a^3-a)\,y''_k + (b^3-b)\,y''_{k+1}\big)\frac{h^2}{6},\qquad
  a=\frac{x_{k+1}-x}{h},\quad b=\frac{x-x_k}{h}
  $$

  二阶导数由三对角系统解出：令 $\sigma_i=\frac{x_i-x_{i-1}}{x_{i+1}-x_{i-1}}$，则 NR 分解（`CubicSplineInterpolator.cpp:332-340`）

  $$
  y''_i=\frac{\sigma_i-1}{p_i},\quad p_i=\sigma_i y''_{i-1}+2,\qquad
  u_i=\frac{6\left(\frac{y_{i+1}-y_i}{x_{i+1}-x_i}-\frac{y_i-y_{i-1}}{x_i-x_{i-1}}\right)\Big/(x_{i+1}-x_{i-1})-\sigma_i u_{i-1}}{p_i}
  $$

  回代（347-350 行）$y''_k=y''_k y''_{k+1}+u_k$；**自然边界** $y''_0=y''_4=0$（329、344 行）。

- **代码位置**：
  - 类声明（`y2[5]` 二阶导数数组）：`src/gmatutil/util/interpolator/CubicSplineInterpolator.hpp:53-71`
  - 构造（`bufferSize=5, requiredPoints=5`）：`src/gmatutil/util/interpolator/CubicSplineInterpolator.cpp:53-67`
  - 三对角分解 `BuildSplines`：`src/gmatutil/util/interpolator/CubicSplineInterpolator.cpp:291-354`
  - splint 求值 `Estimate`：`src/gmatutil/util/interpolator/CubicSplineInterpolator.cpp:406-457`
  - 单调性检查：`src/gmatutil/util/interpolator/CubicSplineInterpolator.cpp:309-324`

- **深度讲解**：

  **数值分析背景**：这是 Numerical Recipes in C 2nd ed. §3.3 的 `spline`/`splint` 原版移植（类注释 `CubicSplineInterpolator.hpp:29`、`Estimate` 注释 `CubicSplineInterpolator.cpp:397-398` 明确点名）。NR 算法把三对角系统就地分解（免去显式矩阵），`y2[]` 即 $S''(x_k)$；`splint` 用 $a,b$ 线性混合端点值与二阶导数项，当 $x$ 恰好落在节点上时 $a^3-a=0$、$b^3-b=0$，自动还原节点值——这是该形式的优雅之处。

  **实现细节**——`Estimate` 的区间定位与求值（`CubicSplineInterpolator.cpp:413-453`）：

  ```cpp
  // 从尾部往前找区间（GMAT 数据多为正向推进，命中"最后一段"概率最高）
  for (i = 3; i >= 0; --i)
  {
     if (dataIncreases)
        if ((x[i] <= ind) && (x[i+1] >= ind)) { kl = i; break; }
     ...
  }
  if (kl == -1)                     // 越界 → 默认不做外推
  {  if (allowExtrapolation) kl = 0;  else return false; }
  kh = kl + 1;
  h = x[kh] - x[kl];
  if (h == 0) return false;         // 重合节点非法
  a = (x[kh] - ind) / h;            // 左权重
  b = (ind - x[kl]) / h;            // 右权重
  for (i = 0; i < dimension; ++i)
     results[i] = a * y[kl][i] + b * y[kh][i] +
        ((a*a*a - a) * y2[kl][i] + (b*b*b - b) * y2[kh][i]) * (h*h)/6.0;
  ```

  对照 5.1.3：本类用 $y''$ 表述＋自然边界，NotAKnot 用弯矩 $s_j$ 表述＋not-a-knot 边界；两者数学等价（都产生 C2 三次样条），差异只在边界条件与求解路径（三对角 vs 3×3 Cramer）。`BuildSplines` 开头还有 `lastX` 缓存短路（`CubicSplineInterpolator.cpp:300-302`）：末节点不变即跳过重算——这是 5.1.3 没有的优化。

  **节点管理**：同 5.1.3 的 `LoadArrays` 环形缓冲重排（`CubicSplineInterpolator.cpp:364-387`）；`AddPoint` 沿用基类。

  **阶数与精度**：同 $O(h^4)$ 三次样条；自然边界使端点二阶导数为零，若真实数据端点曲率不为零会有边界层误差——这是 5.5 中 Code500 选 not-a-knot 而非本类的原因之一（注释 `Code500Propagator.cpp:1396-1402` 亦说明居中窗口以抑制振荡）。

  **使用场景**：`TextEphemFile`（`src/base/subscriber/TextEphemFile.cpp:77`，输出历表在输出时刻插值，`IsTimeToWrite` 内 686-698 行取 5 点 `AddPoint` 后 `Interpolate(mOutputA1Mjd, ...)`）；`TrajectoryData` 的 `SPLINE` 选项（`TrajectoryData.cpp:1137`）；单元测试 `src/UnitTests/TestInterpolator/driver.cpp:115`。

### 条目 5.1.5 CubicSpline（gmatutil 工具单例）：clamped 样条 + Thomas 算法

- **公式**：对 $n+1$ 个节点、$n$ 段，clamped 边界（给定端点一阶导数 $y'(x_0), y'(x_n)$）的三弯矩系统（`CubicSpline.cpp:209-218`）：

  $$
  v_0=\frac{\Delta y_0}{h_0}-y'(x_0),\quad
  v_i=\frac{\Delta y_i}{h_i}-\frac{\Delta y_{i-1}}{h_{i-1}}\ (1\le i<n),\quad
  v_n=y'(x_n)-\frac{\Delta y_{n-1}}{h_{n-1}},\qquad \mathbf v \leftarrow 3\mathbf v
  $$

  对角元 $2h_0,\ 2(h_{i-1}+h_i),\ 2h_{n-1}$（228-232 行），次对角/上对角均为 $h_i$。Thomas 算法（追赶法）求解 $c_i=M_i$（二阶矩），再得幂基系数（252-260 行）：

  $$
  b_i=\frac{\Delta y_i}{h_i}-\frac{h_i(2M_i+M_{i+1})}{3},\qquad
  d_i=\frac{M_{i+1}-M_i}{3h_i},\qquad a_i=y_i,\ c_i=M_i
  $$

  求值（Horner 形式，`CubicSpline.cpp:157-159`）：

  $$
  y=a+\Delta x\big(b+\Delta x(c+\Delta x\,d)\big),\quad
  y'=b+\Delta x(2c+3\Delta x\,d),\quad
  y''=2(c+3\Delta x\,d)
  $$

  端点导数用四阶单边差分（`CubicSpline.cpp:332-345`）：

  $$
  y'(x_0)\approx\frac{1}{h}\left(-\frac{25}{12}y_0+4y_1-3y_2+\frac{4}{3}y_3-\frac{1}{4}y_4\right),\quad
  y'(x_n)\approx\frac{1}{h}\left(\frac{1}{4}y_{n-4}-\frac{4}{3}y_{n-3}+3y_{n-2}-4y_{n-1}+\frac{25}{12}y_n\right)
  $$

- **代码位置**：
  - 类声明（单例 + 四个工具方法）：`src/gmatutil/util/CubicSpline.hpp:41-71`
  - 向量化求值 `EvaluateClampedCubicSplineVectorized`：`src/gmatutil/util/CubicSpline.cpp:102-162`
  - clamped 系数 `CalculateClampedCubicSplineCoefficients`：`src/gmatutil/util/CubicSpline.cpp:184-262`
  - Thomas 算法：`src/gmatutil/util/CubicSpline.cpp:280-308`
  - 端点有限差分 `FiniteDifferenceAtEdge`：`src/gmatutil/util/CubicSpline.cpp:327-346`

- **深度讲解**：

  **数值分析背景**：与 5.1.3/5.1.4 的 5 点固定窗口不同，本类是**任意节点数**的通用 clamped 样条工具（Python 原型作者 N. Hatten，头注释 `CubicSpline.hpp:23-31`）。clamped 边界比自然/not-a-knot 多一个优势：端点斜率若已知，整条样条的端点区域精度提升到与内部一致（消除 $O(h^2)$ 边界层）。Thomas 算法是三对角系统的 $O(n)$ 解法（消元 292-299 行＋回代 302-305 行），数值稳定（对角占优）。

  **实现细节**——Thomas 消元（`CubicSpline.cpp:280-308`）：

  ```cpp
  Rvector CubicSpline::ThomasAlgorithm(const Rvector &a, const Rvector &b,
                                       const Rvector &c, const Rvector &d)
  {
     Integer n = d.GetSize();
     Rvector w(n-1);   // 上三角化后的超对角
     Rvector g(n);     // 变换后的右端
     Rvector p(n);     // 解
     w(0) = c(0) / b(0);
     g(0) = d(0) / b(0);
     for (Integer i = 1; i < n-1; i++)
        w(i) = c(i) / (b(i) - a(i-1) * w(i-1));      // 前向消元
     for (Integer i = 1; i < n; i++)
        g(i) = (d(i) - a(i-1)*g(i-1)) / (b(i) - a(i-1) * w(i-1));
     p(n-1) = g(n-1);
     for (Integer i = n-1; i > 0; i--)
        p(i-1) = g(i-1) - w(i-1) * p(i);              // 后向回代
     return p;
  }
  ```

  调用约定：`ThomasAlgorithm(h, bThomas, h, v)`（`CubicSpline.cpp:235`）——三对角矩阵的次对角/上对角都是步长向量 `h`。求出 $M_i$ 后按上页公式生成 a/b/c/d；`EvaluateClampedCubicSplineVectorized` 用 Horner 法同时给出 $y, y', y''$（`CubicSpline.cpp:153-160`），供需要速度/加速度的调用方一次取齐。

  **节点管理**：本类**不**走 `Interpolator` 的 AddPoint 协议（不继承 `Interpolator`），而是"系数矩阵 + 节点数组"整体传入、整体求值的一次性工具接口（`CubicSpline.hpp:47-60`）。

  **阶数与精度**：三次样条 $O(h^4)$；端点斜率来自四阶单边差分（5 点、系数精确到 $O(h^4)$），故整体保持四阶。`FiniteDifferenceAtEdge` 要求等距（`h = xArray(1)-xArray(0)`，`CubicSpline.cpp:332`）。

  **使用场景**：`EphemSmoother`（`src/base/solarsys/EphemSmoother.cpp`）：对 SPICE 星历构造平滑轨迹——`CreateSmoothedEphem` 先取节点状态（280-289 行），用 `FiniteDifferenceAtEdge` 求端点导数（337-338 行），`CalculateClampedCubicSplineCoefficients` 生成系数（357-359 行），`GetState` 时 `EvaluateClampedCubicSplineVectorized` 一次给出位置/速度/加速度（211-213 行）。

### 条目 5.1.6 LinearInterpolator：线性插值

- **公式**：相邻两点 $(x_k,y_k),(x_{k+1},y_{k+1})$ 间（`LinearInterpolator.cpp:136-142`）：

  $$
  y(x)=y_k+\frac{x-x_k}{x_{k+1}-x_k}\,(y_{k+1}-y_k)
  $$

  代码以 `delta = (ind - independent[previousPoint]) / (independent[index]-independent[previousPoint])` 形式实现（`LinearInterpolator.cpp:136-139`）。

- **代码位置**：
  - 类声明：`src/gmatutil/util/interpolator/LinearInterpolator.hpp:41-54`
  - 求值：`src/gmatutil/util/interpolator/LinearInterpolator.cpp:109-153`
  - 区间查找（从最新点向旧点回溯）：`src/gmatutil/util/interpolator/LinearInterpolator.cpp:117-150`

- **深度讲解**：

  **数值分析背景**：一阶（$o=1$）插值，连续但不光滑（导数不连续），误差 $O(h^2)$。它不追求精度，追求**稳健与零开销**：无矩阵、无窗口搜索，仅需 2 点。

  **实现细节**：`Interpolate` 从 `latestPoint` 向旧点回溯找包围区间（`LinearInterpolator.cpp:123-150`），环形缓冲索引越界时回绕（125-127 行）；`delta==0`（重合节点）返回 false（137-138 行）；越界时仅当 `allowExtrapolation` 才用端段延长（130-133 行）。

  **节点管理**：完全继承基类环形缓冲（`requiredPoints=2, bufferSize=2`，构造见 `LinearInterpolator.cpp:45-48`），是最小配置的 AddPoint/Interpolate 实现。

  **阶数与精度**：$O(h^2)$ 截断误差，仅适合粗粒度场合或作为降级回退。

  **使用场景**：`TrajectoryData` 的 `LINEAR` 选项（`TrajectoryData.cpp:1142`，`interpPoints=2`）；单元测试 `src/UnitTests/TestStopCond/TestStopCond.cpp:171`。注释（`CubicSplineInterpolator.cpp:306-308`）表明线性插值常作为样条失败时的备用方案。

### 条目 5.1.7 HermiteInterpolator：Hermite–Newton 差商插值

- **公式**：给定 $m$ 个点及其一阶导数，构造 $2m-1$ 次 Hermite 多项式，采用 Newton 形式（节点重复出现两次：$x_0,x_0,x_1,x_1,\dots$）：

  $$
  P(x)=\sum_{k=0}^{2m-1} q_k \prod_{j=0}^{k-1}(x-x_j),\qquad
  q_k=f[x_0,x_0,\dots]=\text{差商表顶行}
  $$

  差商递推（`HermiteInterpolator.cpp:414-420`）：

  $$
  f[x_j,\dots,x_{j+k}]=\frac{f[x_{j+1},\dots]-f[x_j,\dots]}{x_{j+k}-x_j},\qquad
  \text{节点重合时}\ f[x_j,x_j]=f'(x_j)
  $$

  导数求值（`HermiteInterpolator.cpp:552-564`）：$\frac{d}{dx}\prod_{j=0}^{k-1}(x-x_j)=\sum_{i=0}^{k-1}\prod_{\substack{j=0\\j\neq i}}^{k-1}(x-x_j)$。

- **代码位置**：
  - 类声明（`pointsWanted`、差商表 `qCoeffs`、`tValues`）：`src/gmatutil/util/interpolator/HermiteInterpolator.hpp:67-117`
  - 构造（`bufferSize = pointsWanted+1`）：`src/gmatutil/util/interpolator/HermiteInterpolator.cpp:45-52`
  - 导数喂入 `AddDerivative`（`-9.99999e99` 哨兵表示无导数）：`src/gmatutil/util/interpolator/HermiteInterpolator.cpp:158-217`
  - 差商表 `BuildQCoefficients`：`src/gmatutil/util/interpolator/HermiteInterpolator.cpp:346-455`（阶数 393 行，重复节点 378-391 行，递推 409-436 行）
  - 求值 `EvaluatePolynomial`：`src/gmatutil/util/interpolator/HermiteInterpolator.cpp:470-499`
  - 导数求值 `EvaluatePolynomialDerivative` / `EvaluateDerivativeIndependentTerm`：`src/gmatutil/util/interpolator/HermiteInterpolator.cpp:514-569`
  - 6 维状态专用接口 `InterpolateCartesianState`：`src/gmatutil/util/interpolator/HermiteInterpolator.cpp:296-326`

- **深度讲解**：

  **数值分析背景**：Hermite 插值在节点上同时匹配函数值与导数，把"数据点"扩展为"数据点＋切触条件"，阶数翻倍（$m$ 点 $2m-1$ 次）而不增加节点数。实现采用 Newton 差商表：把每个点重复 $(dvSize+1)$ 次（`HermiteInterpolator.cpp:378-391`），相邻相同节点的一阶差商退化为导数（420 行），从而把 Hermite 问题**机械地**化为普通 Newton 插值——这是 PSU 讲义（头注释 `HermiteInterpolator.hpp:47-49` 引用的课件）的经典技巧。

  **实现细节**——差商表构建（`HermiteInterpolator.cpp:409-436`）：

  ```cpp
  Integer point = 0, tindex = 1;
  for (UnsignedInt t = 0; t < order; ++t)         // order = m*(dvSize+1)-1
  {
     for (UnsignedInt j = 0; j < prevCol.size()-1; ++j)
     {
        Real deriv;
        if (x[j+tindex] != x[j])                  // 普通差商
           deriv = (prevCol[j+1] - prevCol[j]) / (x[j+tindex] - x[j]);
        else                                       // 重复节点：用导数数据
           deriv = derivatives[i][point][0];
        tableau.push_back(deriv);
     }
     qCoeffs[i].push_back(tableau[0]);            // 取每列顶行作 Newton 系数
     prevCol = tableau;
     tableau.clear();
     ++tindex;
  }
  ```

  初列 `prevCol` 为 $y$ 值按节点重复展开（378-391 行）；第 $t$ 列用跨度 $x_{j+tindex}-x_j$ 计算差商。`qCoeffs[i]` 存每列首元素（Newton 系数 $q_k$），`tValues[i]` 存重复节点序列。求值（`HermiteInterpolator.cpp:477-495`）用累积乘积 `tProduct *= (ind - tValues[i][j-1])` 后 `results += qCoeffs[j]*tProduct`，即标准的 Newton 多项式 Horner 求值。

  **节点管理**：不走基类 `AddPoint` 的"纯函数值"通道——先 `AddPoint` 喂函数值，再 `AddDerivative(ind, data, 1)` 喂一阶导数（`HermiteInterpolator.cpp:158-217`；`derivatives[element][point][deriv]` 三维结构在 169-181 行按需分配）；**逐元素可选**：`data[i] <= -9.99999e99` 的元素视为无导数（196 行），实现"部分元素有导数"的混合插值（类注释 `HermiteInterpolator.hpp:39-42`）。`Clear()`（`HermiteInterpolator.cpp:131-137`）清空三个容器。

  **阶数与精度**：$m$ 点 $2m-1$ 次多项式，误差 $O(h^{2m})$；对含导数信息的星历数据（位置＋速度），同点数下精度远超纯 Lagrange。限制：仅支持一阶导数（`HermiteInterpolator.cpp:164-166` 抛异常）、要求各点导数阶数一致（类注释 `HermiteInterpolator.hpp:52-65`）。

  **使用场景**：`src/gmatutil/util/Ephemeris.cpp`（SPK 风格星历读取）：`useHermite=true` 时按 `maxOrder` 建 6 维 Hermite（353 行），阶数不足 7 时补充速度导数（380-394 行，`vel[j]=v[j+3]*SECS_PER_DAY` 把速度从 天⁻¹ 缩放到 秒⁻¹ 与自变量一致），并用 `InterpolateCartesianState` 同时还原位置/速度（399-406 行）；构造函数 63 行处有 `TEST_HERMITE_INTERP` 开关的演示代码。

## 5.2 切比雪夫插值：DE 星历内核（`src/base/solarsys/DeFile.*`）

### 条目 5.2.1 DeFile：切比雪夫多项式求值与递推（位置/速度/加速度/章动/天平动/状态差分）

- **公式**：DE 星历把每个记录（record）按"粒"（granule）分段，每段内用切比雪夫多项式逼近（代码源自 JPL/JSC D. Hoffman 的 `ephem_read.c`，`DeFile.cpp:1028-1041` 头注释）。归一化时间：

  $$
  T_c=2\,\frac{t-T_{seg}}{T_{sub}}-1\in[-1,1]
  $$

  其中 $T_{sub}=T_{span}/G$ 为粒长（$G$ 为该记录粒数，`DeFile.cpp:1366/1847`）。切比雪夫基与一阶、二阶导数递推（`DeFile.cpp:1874-1893`）：

  $$
  T_0=1,\ T_1=T_c,\ T_2=2T_c^2-1,\qquad T_j=2T_c\,T_{j-1}-T_{j-2}
  $$

  $$
  U_j\equiv\frac{dT_j}{dT_c}:\ U_0=0,\ U_1=1,\ U_2=4T_c,\quad
  U_j=2T_c\,U_{j-1}+2T_{j-1}-U_{j-2}
  $$

  $$
  W_j\equiv\frac{d^2T_j}{dT_c^2}:\ W_0=W_1=0,\ W_2=4,\quad
  W_j=2T_c\,W_{j-1}+4U_{j-1}-W_{j-2}
  $$

  状态还原（`DeFile.cpp:1899-1909`）：

  $$
  \mathbf r=\sum_{j=0}^{N-1}\mathbf A_j T_j(T_c),\qquad
  \mathbf v=\left(\sum_{j=1}^{N-1}\mathbf A_j U_j(T_c)\right)\frac{dT_c}{dt},\qquad
  \mathbf a=\left(\sum_{j=1}^{N-1}\mathbf A_j W_j(T_c)\right)\left(\frac{dT_c}{dt}\right)^2
  $$

  链式因子 $dT_c/dt=2G/(T_{span}\cdot 86400)$（`DeFile.cpp:1906`）。章动（2 分量，`DeFile.cpp:1640-1652`）与天平动（3 分量＋速率，`DeFile.cpp:1392-1415`）只做 $T_j$ 与 $U_j$ 求和。状态差分 $\Delta t=t_2-t_1$ 用系数差 $T_j(T_{c2})-T_j(T_c)$（`DeFile.cpp:2201-2209`）：

  $$
  \Delta T_0=0,\ \Delta T_1=\Delta t_c,\ \Delta T_2=2T_{c2}\Delta t_c+2\Delta t_c\,T_c,\qquad
  \Delta T_j=2T_{c2}\,\Delta T_{j-1}+2\Delta t_c\,T_{j-1}-\Delta T_{j-2}
  $$

- **代码位置**：
  - 记录定位 `Read_Coefficients`（按记录跨度跳转、读入 `Coeff_Array`）：`src/base/solarsys/DeFile.cpp:1054-1119`（偏移计算 1075-1085，`T_beg = Coeff_Array[0]-baseEpoch` 1115-1117）；GmatTime 版本 1122-1187
  - 归一化时间与粒选择：`src/base/solarsys/DeFile.cpp:1840-1863`（`Interpolate_State` 内）、`1982-2014`（GmatTime 版）
  - 位置＋速度＋加速度求值：`src/base/solarsys/DeFile.cpp:1872-1910`、`2023-2062`
  - 仅位置 `Interpolate_Position`：`src/base/solarsys/DeFile.cpp:1715-1761`
  - 章动 `Interpolate_Nutation`：`src/base/solarsys/DeFile.cpp:1607-1655`
  - 天平动＋速率 `Interpolate_Libration`：`src/base/solarsys/DeFile.cpp:1359-1415`
  - 状态差分 `Interpolate_State_Delta`：`src/base/solarsys/DeFile.cpp:2150-2216`
  - 常量与数组尺寸（`ARRAY_SIZE_405=1018` 等，`MAX_ARRAY_SIZE=1018`）：`src/base/solarsys/DeFile.hpp:134-139`；系数指针 `coeffPtr[12][3]` 头部结构 `DeFile.hpp:206-283`；`libratPtr` 同结构

- **深度讲解**：

  **数值分析背景（切比雪夫在 DE 内核中的压缩原理）**：DE 系列星历（DE405/421/430 等）由 JPL 数值积分产生，发布为**若干天一个记录**（跨度 $T_{span}$ 写在记录头，`DeFile.cpp:1117`）内若干"粒"（granule）上的切比雪夫系数（G 粒、每分量 N 个系数，N 由文件头 `coeffPtr[Target][1]` 给出，`DeFile.cpp:1830`）。切比雪夫系数的优势：(a) 在 $[-1,1]$ 上以 $T_c=\cos\theta$ 为基，级数截断误差**均匀**分布（等幅振荡），不出现 Runge 现象；(b) 对解析函数系数随阶数快速衰减，故每个分量只需文件头给出的 N 个系数（代码数组容量 50，实际 N 视文件格式而定）即可达到文件自身精度；(c) 递推 $T_j=2T_cT_{j-1}-T_{j-2}$ 每点仅 O(N) 次乘法，比等阶多项式求值便宜。速度/加速度不求导系数，而是用 $U_j,W_j$ 递推（切比雪夫导数递推），比数值差分更精确。

  **实现细节**——`Interpolate_State` 的求值核心（`DeFile.cpp:1872-1910`）：

  ```cpp
  for ( i=0 ; i<3 ; i++ )                // 三个笛卡尔分量并行
  {
     Cp[0] = 1.0;  Cp[1] = Tc;  Cp[2] = 2.0 * Tc*Tc - 1.0;
     Up[0] = 0.0;  Up[1] = 1.0;  Up[2] = 4.0 * Tc;      // U_j = dT_j/dTc
     Wp[0] = 0.0;  Wp[1] = 0.0;  Wp[2] = 4.0;           // W_j = d²T_j/dTc²
     for ( j=3 ; j<N ; j++ )
     {
        Cp[j] = 2.0 * Tc * Cp[j-1] - Cp[j-2];           // 切比雪夫三递推
        Up[j] = 2.0 * Tc * Up[j-1] + 2.0 * Cp[j-1] - Up[j-2];
        Wp[j] = 2.0 * Tc * Wp[j-1] + 4.0 * Up[j-1] - Wp[j-2];
     }
     P_Sum[i] = V_Sum[i] = A_Sum[i] = 0.0;
     for ( j=N-1 ; j>-1 ; j-- )  P_Sum[i] += A[j+i*N] * Cp[j];   // 位置
     for ( j=N-1 ; j>0  ; j-- )  V_Sum[i] += A[j+i*N] * Up[j];   // 速度（j=0 项 U_0=0）
     for ( j=N-1 ; j>0  ; j-- )  A_Sum[i] += A[j+i*N] * Wp[j];   // 加速度（W_0=W_1=0）
     X.Position[i] = P_Sum[i];
     X.Velocity[i] = V_Sum[i] * 2.0 * ((double) G) / (T_span * GmatTimeConstants::SECS_PER_DAY);
     double dTcdt = 2.0 * ((double) G) / (T_span * GmatTimeConstants::SECS_PER_DAY);
     X.Acceleration[i] = A_Sum[i] * dTcdt * dTcdt;      // 二阶链式法则
  }
  ```

  - 系数布局：分量 i 的 N 个系数在 `Coeff_Array` 中连续存放（`A[j+i*N]`），入口 `C = coeffPtr[Target][0]-1`（`DeFile.cpp:1829`）；多粒时 `C += 3*offset*N` 跳到目标粒（`DeFile.cpp:1860`）；
  - 粒选择：从 `j=G` 向下找第一个满足 `Time > T_beg + (j-1)*T_sub` 的粒（`DeFile.cpp:1848-1857`）；
  - 记录定位：`Read_Coefficients` 用 `Offset = ±ceil(T_delta/T_span)` 与 `fseek` 跳记录（`DeFile.cpp:1075-1099`），并校验读取长度（1105-1113 行）；时间系统上，`GetPosVel` 先把 A1MJD 转 TDBMJD（`DeFile.cpp:383-387`），内部以 Julian Date 计算（`JD_MJD_OFFSET=JD_JAN_5_1941`，`DeFile.cpp:104`），`T_beg = Coeff_Array[0]-baseEpoch`（1115 行）剥离文件头纪元；
  - `Interpolate_State_Delta`（`DeFile.cpp:2150-2216`）用同一组系数一次性给出 $\mathbf r(t_2)-\mathbf r(t_1)$（`Cp_Delta` 递推即 $T_j(T_{c2})-T_j(T_c)$ 的精确表达式，2201-2209 行），避免两次求值相减的消去误差——适合高速飞行器短时差位置差计算。

  **节点管理（AddPoint/Interpolate 协议）**：DeFile **不**使用 `Interpolator` 协议，而是"按时间定位记录→读系数→就地求值"的流式接口（`Interpolate_State`/`Interpolate_Position`/`Interpolate_Nutation`/`Interpolate_Libration`/`Interpolate_State_Delta` 五个入口，`DeFile.hpp:378-414`）。"节点"就是记录内每个粒的切比雪夫系数，而非采样点；粒内求值是解析级数，粒间切换由 `T_seg`/`T_sub` 完成。

  **阶数与精度**：每分量 N 阶切比雪夫（N 由文件头决定，`DeFile.cpp:1830`，数组容量 50，`A[50]` 在 1783 行）；插值引入的误差远小于 DE 文件自身的标定精度（JPL 发布时给出各天体误差界）。粒长 $T_{sub}=T_{span}/G$（$T_{span}$ 由文件头给出，`DeFile.cpp:1117`），G 大则粒内多项式阶数低、每粒误差小。

  **使用场景**：GMAT 全部 JPL DE 星历读取（`src/base/solarsys/` 内 `PlanetaryEphem` 家族，DeFile 为其中之一）；`GetPosVel` 内嵌 Earth-Moon 质心组合（`DeFile.cpp:432-454`，用 `R1.EMRAT` 质量比从地月系质心还原地球状态）与月心状态直接返回（409-430 行）；章动/天平动供姿态与坐标转换使用。相关调用链见 [第7章](../CH07-propagator.md) 星历部分。

## 5.3 重心拉格朗日：CSALT（`src/csalt/src/util/`）

### 条目 5.3.1 BaryLagrangeInterpolator：重心权重与重心矩阵

- **公式**：重心权重（`BaryLagrangeInterpolator.cpp:616-624`）：

  $$
  w_j=\frac{1}{\prod_{k\neq j}(x_j-x_k)}
  $$

  重心基函数与插值（矩阵形式，`BaryLagrangeInterpolator.cpp:586-601, 321`）：

  $$
  L_j(t)=\frac{w_j/(t-x_j)}{\sum_k w_k/(t-x_k)},\qquad
  p(t_i)=\sum_j L_j(t_i)\,f_j\ \Longleftrightarrow\ \mathbf p=\mathbf B\,\mathbf f,\quad
  B_{ij}=\frac{w_j/(t_i-x_j)}{\sum_k w_k/(t_i-x_k)}
  $$

- **代码位置**：
  - 类声明（`weigthVec`/`barycentricMatrix` 成员，三档 `Interpolate` 重载）：`src/csalt/src/util/BaryLagrangeInterpolator.hpp:38-125`
  - 权重计算 `CalWeightVec`：`src/csalt/src/util/BaryLagrangeInterpolator.cpp:611-625`
  - 矩阵组装 `CalBarycentricMatrix`：`src/csalt/src/util/BaryLagrangeInterpolator.cpp:574-602`
  - 矩阵-向量求值：`src/csalt/src/util/BaryLagrangeInterpolator.cpp:309-323`（`resultVec = barycentricMatrix*(*funcValueVec)`）
  - 严格递增/可行性检查：`src/csalt/src/util/BaryLagrangeInterpolator.cpp:429-562`

- **深度讲解**：

  **数值分析背景**：经典拉格朗日基（5.1.2）对每个新 $t$ 都要 O(n²) 重算基函数，且数值上随 n 增长退化。重心形式把与 $t$ 无关的部分（$w_j$）一次性预计算，之后每个 $t$ 只需 O(n) 次操作：

  $$
  p(t)=\frac{\sum_j \frac{w_j}{t-x_j}f_j}{\sum_j \frac{w_j}{t-x_j}}
  $$

  该形式对插值点的**任意**分布都数值稳定（只要 $t$ 不落在节点上），是配点法（collocation）场景的标准选择——CSALT 的 LGR 节点（Gauss–Legendre–Radau）正好满足"节点在 $[-1,1]$ 内且端点包含 +1"的分布，详见 [第15章](../CH15-csalt-interop-tests.md)。

  **实现细节**——权重与矩阵（`BaryLagrangeInterpolator.cpp:611-625, 586-601`）：

  ```cpp
  void BaryLagrangeInterpolator::CalWeightVec()
  {
     weigthVec.SetSize(numIndVarVec);
     for (int idx1 = 0; idx1 < numIndVarVec; idx1++)
     {
        weigthVec(idx1) = 1;
        for (int idx2 = 0; idx2 < numIndVarVec; idx2++)
           if (idx1 != idx2)
              weigthVec(idx1) /= (indVar(idx1) - indVar(idx2));   // 连乘取倒数
     }
  }
  // CalBarycentricMatrix 关键片段（586-601 行）
  for (colIdx = 0; colIdx < numIndVarVec; colIdx++)
     for (rowIdx = 0; rowIdx < numInterpPoints; rowIdx++)
     {
        barycentricMatrix(rowIdx,colIdx) =
           weigthVec(colIdx)/((*interpPointVec)(rowIdx) - indVar(colIdx));
        normalizationVec(rowIdx) += barycentricMatrix(rowIdx,colIdx);  // 分母累加
     }
  for (rowIdx = 0; rowIdx < numInterpPoints; rowIdx++)
     for (colIdx = 0; colIdx < numIndVarVec; colIdx++)
        barycentricMatrix(rowIdx,colIdx) /= normalizationVec(rowIdx);  // 行归一化
  ```

  注意 `BaryLagrangeInterpolator` **不继承** `Interpolator` 基类（头注释 `BaryLagrangeInterpolator.hpp:25` 明说），协议改为三段式：`SetIndVarVec`（喂节点并触发 `CalWeightVec`，154-174 行）→ `SetInterpPointVec`（喂插值点并触发 `CalBarycentricMatrix`，191-214 行）→ `Interpolate(funcValueVec, resultVec)`（纯矩阵乘法，392-415 行）；另有把三段合并的一次性重载（309-323 行）。要求：节点与插值点均严格递增（`IsStrictlyIncreasing`，429-442 行），且**插值点不得与节点重合**（`ChkInterpPointVecFeasibility` 516-532 行，避免 $w/(t-x_j)$ 除零）——这就是 `NLPFuncUtilRadau.cpp:526-531` 在网格细化时"剔除端点"的原因。

  **节点管理**：与 5.1 家族的最大差异是**批处理**：节点集与插值点集一次性给定，权重/矩阵缓存复用（`isIndVarVecDefined`/`isInterpPointVecDefined` 标志，`BaryLagrangeInterpolator.cpp:46-47`），适合"同一节点集上反复插值不同函数值"的配点迭代。

  **阶数与精度**：n 点多项式精确复现 n-1 次多项式；对 LGR 节点上的光滑函数，配点误差呈谱收敛（指数收敛）。重心形式的舍入误差与节点 Lebesgue 常数相关，对 LGR 节点远好于等距节点。

  **使用场景**：`src/csalt/src/collutils/NLPFuncUtilRadau.cpp:516-568`（Radau 配点网格细化时把状态/控制列向量插值到新网格，`interp.SetIndVarVec(&normMeshPts); interp.SetInterpPointVec(&interpPts)` 在 533-534 行）；`src/csalt/src/collutils/NLPFuncUtil_ImplicitRK.cpp:1677, 2073`（隐式 Runge-Kutta 配点的控制插值）。

## 5.4 样条反求穿越历元：停止条件（`src/base/stopcond/`）

### 条目 5.4.1 StopCondition：以"交换自变量"的三次样条反求目标历元

- **公式**：停止条件求解方程 $g(t)=g^*$（$g$ 为 LHS 参数，$g^*$ 为目标值）。GMAT 不迭代求根，而是**交换自变量与因变量**：以 $g$ 为自变量、$t$ 为因变量构造 5 点三次样条，然后直接求

  $$
  t^*=\hat S(g^*)\quad\text{s.t.}\quad \hat S \text{ 是 } \{(g_i,t_i)\}_{i=0}^{4} \text{ 上的 not-a-knot 样条}
  $$

  即先 `AddPoint(lhsValueBuffer[i], &mEpochBuffer[i])`（`StopCondition.cpp:845`），再 `Interpolate(currentGoalValue, &stopEpoch)`（`StopCondition.cpp:849`）。数学上这是"反函数插值"：若 $g(t)$ 单调，$\hat S(g^*)$ 给出 $t^*$ 的 O(h⁴) 近似（样条阶 4），亚步长精度无需缩小积分步长。

- **代码位置**：
  - 默认插值器创建（NotAKnot）：`src/base/stopcond/StopCondition.cpp:172-181`
  - 环形缓冲喂点与目标括入检查：`src/base/stopcond/StopCondition.cpp:802-860`（括入判定 834 行，AddPoint 845 行，Interpolate 849 行）
  - `GetStopEpoch` 的插值反求：`src/base/stopcond/StopCondition.cpp:909-924`
  - 缓冲尺寸取自插值器：`src/base/stopcond/StopCondition.cpp:1169-1181`
  - 插值器可替换接口 `SetInterpolator`：`src/base/stopcond/StopCondition.cpp:1539-1546`
  - 成员声明（`mInterpolator`、三组环形缓冲）：`src/base/stopcond/StopCondition.hpp:163, 182-190`

- **深度讲解**：

  **数值分析背景**：穿越历元定位是"求 $g(t)-g^*=0$ 的根"。经典做法（二分/Newton）需要反复求值且可能不收敛；GMAT 的替代方案是**局部反函数样条**：用最近的 5 个样本 $(g_i,t_i)$ 拟合 $t=\hat S(g)$，一次求值得到 $t^*$。其成立前提是 $g$ 在窗口内单调（工程上传播步长内穿越参数通常单调）；非单调时样条可能给出窗外伪根，因此 `AddToBuffer` 先做**括入检查**（`StopCondition.cpp:834`）：仅当 $g^*\in[\min g_i,\max g_i]$ 才插值。上层 `Propagate` 命令的 `RefineFinalStep`/`BisectFinalStep` 再对结果做二分精化，形成两层精度结构（详见 [第7章](../CH07-propagator.md) 停止条件一节，不在此重复）。

  **实现细节**——括入判定与反求（`StopCondition.cpp:816-853`）：

  ```cpp
  // 仅当环形缓冲填满（mNumValidPoints >= mBufferSize）才尝试
  if (mNumValidPoints >= mBufferSize)
  {
     Real minVal = lhsValueBuffer[0], maxVal = lhsValueBuffer[mBufferSize - 1];
     for (int i = 0; i < mBufferSize; ++i)        // 求 LHS 窗口极值
     {  if (minVal > lhsValueBuffer[i]) minVal = lhsValueBuffer[i];
        if (maxVal < lhsValueBuffer[i]) maxVal = lhsValueBuffer[i]; }
     // 目标必须被 LHS 值括住（g* ∈ [min, max]）
     if ((currentGoalValue >= minVal) && (currentGoalValue <= maxVal))
     {
        mInterpolator->Clear();
        for (int i=0; i<mBufferSize; i++)
           // 关键：自变量= LHS 值，因变量= 历元（反函数插值）
           mInterpolator->AddPoint(lhsValueBuffer[i], &mEpochBuffer[i]);
        if (mInterpolator->Interpolate(currentGoalValue, &stopEpoch))
        {  mStopEpoch = stopEpoch;  retval = true; }
     }
  }
  ```

  时间条件（`IsTimeCondition`）不走插值，直接线性换算 `dt = (goal - prev) * GetTimeMultiplier()`（`StopCondition.cpp:898`）；非时间条件统一走上述反求（`GetStopEpoch` 的 909-924 行与 `Evaluate` 内的 845-853 行是同一模式，后者失败仅置 retval，前者失败抛 `StopConditionException`，924 行）。

  **节点管理（AddPoint/Interpolate 协议）**：窗口大小为 `mInterpolator->GetBufferSize()`（`StopCondition.cpp:1171`），默认 NotAKnot 即 5 点；样本在 `AddToBuffer` 内滚动（802-814 行：旧值左移、新值入尾），`isInitialPoint` 时重置并预填首点（780-799 行）。插值器可被外部替换（`SetInterpolator`，`StopCondition.cpp:1539`；命令层 `Propagate` 通过参数传入，如 `Propagate.cpp` 中 `SetInterpolator` 调用链），替换后窗口尺寸自动跟随新插值器。

  **阶数与精度**：not-a-knot 三次样条 → $t^*$ 误差 $O(h^4)$，$h$ 为传播步长；对线性穿越参数（如近点角、高度）误差极小，对强非线性参数（如真近点角过拱点）窗口需足够密。括入检查保证只在与目标同号的单调段内反求，规避伪根。

  **使用场景**：全部非时间停止条件（高度、真近点角、ΔV、质量等）的穿越历元定位；GUI 与命令层（`While`/`Target`/`Propagate`）共用同一 `StopCondition` 基类。调用链细节见 [第7章](../CH07-propagator.md) 的 `CheckStopConditions` 与 `AddToBuffer` 描述。

## 5.5 Code500 中的 NotAKnot（`plugins/EphemPropagatorPlugin`）

### 条目 5.5.1 Code500Propagator：星历采样点上的 5 点 not-a-knot 样条传播

- **公式**：无新公式——直接调用 5.1.3 的 `NotAKnotInterpolator`，对 Code500 星历文件按 50 点/记录采样（`firstStateVector_DULT`/`stateVector2Thru50_DULT`，`Code500Propagator.cpp:1539-1545`）构造 5 点窗口，做 6 维状态（位置＋速度）的三次样条插值。窗口选择准则（`UpdateInterpolator` 注释，`Code500Propagator.cpp:1395-1402`）：**把插值历元放在第 2 与第 3 个星历点之间**，使样条求值区落在窗口中央，抑制端点振荡。

- **代码位置**：
  - 插值器创建（dim=6）：`plugins/EphemPropagatorPlugin/src/base/propagator/Code500Propagator.cpp:871-874`
  - 成员声明：`plugins/EphemPropagatorPlugin/src/base/propagator/Code500Propagator.hpp:105-106`
  - 窗口填充 `UpdateInterpolator`（GmatEpoch 版）：`plugins/EphemPropagatorPlugin/src/base/propagator/Code500Propagator.cpp:1408-1558`（5 记录选择 1471-1482，居中起点调整 1484-1491，UTC 闰秒修正 1510-1524，DUL 单位换算与 AddPoint 1535-1549）
  - GmatTime 版：`plugins/EphemPropagatorPlugin/src/base/propagator/Code500Propagator.cpp:1561-1688`
  - 状态更新 `UpdateState`：`plugins/EphemPropagatorPlugin/src/base/propagator/Code500Propagator.cpp:1187-1191`
  - 对外取状态 `GetState`：`plugins/EphemPropagatorPlugin/src/base/propagator/Code500Propagator.cpp:1331-1355`、`1368-1387`

- **深度讲解**：

  **数值分析背景**：Code500 星历以固定间隔（`timeIntervalBetweenPoints_SEC`，`Code500Propagator.cpp:795`）每记录 50 点（`NUM_STATES_PER_RECORD=50`，`Code500EphemerisFile.hpp:104`）存储状态，而传播器需要在任意历元取状态。三次样条比线性插值平滑（C2）、比 8 点 Lagrange 更省点；5 点窗口覆盖 4 个采样区间，局部误差 $O(h^4)$，对光滑近地轨道数据远小于文件自身量化精度。窗口**居中**是关键——样条插值误差的最小点在区间中央，端点附近误差最大，故 `UpdateInterpolator` 特意让目标落在第 2、3 点之间（与 5.1.2 的 Lagrange 居中思想一致，只是实现为"记录游标"而非"枚举窗口起点"）。代码注释同时说明这是"目前唯一支持"的插值器（`Code500Propagator.cpp:35`）。

  **实现细节**——窗口游标与回绕（`Code500Propagator.cpp:1427-1482`）：

  ```cpp
  Integer usedRecords[5][2];            // 5 个 (记录号, 记录内行号) 对
  Integer block = record, line = stateIndex - 1;   // 从目标前一点起
  if (line < 0)                         // 目标在记录首行
  {
     if (block == 0) line = 0;          // 文件首点：就地取
     else { --block; line = 49; }       // 跨记录：回退上一记录末行
  }
  // 文件末尾处理：末块行数不定，按实际数据钳制（1443-1469 行）
  ...
  for (UnsignedInt i = 0; i < 5; ++i)
  {
     usedRecords[i][0] = block;
     usedRecords[i][1] = line;
     ++line;
     if (line == 50) { ++block; line = 0; }   // 记录内 50 点满则进下一记录
  }
  Integer startIndex = 1;                // 默认窗口起点在目标前 1 行
  Integer endIndex   = 2;                //   使目标落在第 2、3 点之间
  if (stateIndex == 0)      startIndex = 0;       // 文件起点特例
  if (stateIndex > 45)      startIndex = stateIndex - 45;  // 靠文件尾时右移
  ```

  随后逐点换算单位（`DUL_TO_KM`、`DUL_DUT_TO_KM_SEC`，`Code500Propagator.cpp:1539-1545`；Code500 用距离/距离-时间单位，见 `ephempropagator_defs.hpp`）与 UTC→A1 闰秒修正（1510-1524 行），`interp->Clear()` 后 5 次 `AddPoint`（1549 行）。传播主循环 `UpdateState` 每步 `interp->Interpolate(currentEpoch, theState)`（1189-1191 行）得到 MJ2000Eq 状态，必要时再经 `CoordinateConverter` 转到当前坐标（1199-1216 行）。

  **节点管理（AddPoint/Interpolate 协议）**：每次传播步都重填 5 点窗口（"Brute force for now"注释，1496 行），没有增量更新——因为采样点随时间滑动，重填最直接；`FindRecord`（1255-1286 行）先定位记录/行号，越界（`stateIndex==-1`）抛"epoch outside span"异常（1422-1424 行）。

  **阶数与精度**：三次样条 $O(h^4)$（h 为文件采样步长，`Code500Propagator.cpp:795`）；与 5.4 的停止条件共用 NotAKnot 但用途相反——这里是"时间→状态"正插值，那里是"参数→时间"反插值。速度分量由样条导数隐含给出（样条在节点上匹配位置与一阶导连续性），无需单独处理。

  **使用场景**：Code500 星历文件驱动的航天器传播（`EphemerisPropagator` 家族成员，`Code500Propagator.cpp:33-35`）；SPK/CCSDS 传播器（同插件内 `SPKPropagator.cpp`、`CcsdsEphPropagator.cpp`）使用各自的插值路径（SPK 用 `Ephemeris.cpp` 的 Hermite/Lagrange 路径，见 5.1.7）。插件整体结构见 [第7章](../CH07-propagator.md) 与 [第13章](../CH13-plugins-a.md)。

## 5.6 公式索引表

| 公式 | 文件:行 | 所属类 |
| --- | --- | --- |
| 拉格朗日基函数连乘 $P(x)=\sum y_i\prod_{j\neq i}\frac{x-x_j}{x_i-x_j}$ | `src/gmatutil/util/interpolator/LagrangeInterpolator.cpp:524` | LagrangeInterpolator |
| 居中窗口：最近节点搜索与 begin/end 钳制 | `src/gmatutil/util/interpolator/LagrangeInterpolator.cpp:778-813` | LagrangeInterpolator |
| 起始点：最小化 $\|\frac{x_{q+o}+x_q}{2}-x\|$ | `src/gmatutil/util/interpolator/LagrangeInterpolator.cpp:886-893` | LagrangeInterpolator |
| 降阶 `order=pointCount-1` | `src/gmatutil/util/interpolator/LagrangeInterpolator.cpp:299` | LagrangeInterpolator |
| 三次样条幂基 $S_j=a_j\Delta x^3+b_j\Delta x^2+c_j\Delta x+d_j$ | `src/gmatutil/util/interpolator/NotAKnotInterpolator.cpp:567-568` | NotAKnotInterpolator |
| not-a-knot 条件 $s_1=(h_1s_0+h_0s_2)/(h_0+h_1)$ | `src/gmatutil/util/interpolator/NotAKnotInterpolator.cpp:457` | NotAKnotInterpolator |
| not-a-knot 3×3 系统 A 阵 | `src/gmatutil/util/interpolator/NotAKnotInterpolator.cpp:413-429` | NotAKnotInterpolator |
| Cramer 解 $s_0,s_2,s_4$ | `src/gmatutil/util/interpolator/NotAKnotInterpolator.cpp:447-455` | NotAKnotInterpolator |
| 弯矩→幂基系数 a/b/c/d | `src/gmatutil/util/interpolator/NotAKnotInterpolator.cpp:461-468` | NotAKnotInterpolator |
| NR spline 三对角分解（$\sigma_i,p_i,u_i$） | `src/gmatutil/util/interpolator/CubicSplineInterpolator.cpp:332-340` | CubicSplineInterpolator |
| 自然边界 $y''_0=y''_4=0$ | `src/gmatutil/util/interpolator/CubicSplineInterpolator.cpp:329,344` | CubicSplineInterpolator |
| splint 求值 $a y_k+b y_{k+1}+((a^3-a)y''_k+(b^3-b)y''_{k+1})h^2/6$ | `src/gmatutil/util/interpolator/CubicSplineInterpolator.cpp:451-453` | CubicSplineInterpolator |
| clamped 系统右端 v（3× 差商差） | `src/gmatutil/util/CubicSpline.cpp:212-218` | CubicSpline |
| Thomas 消元 $w_i,g_i,p_i$ | `src/gmatutil/util/CubicSpline.cpp:289-305` | CubicSpline |
| clamped 系数 $b_i,d_i$ | `src/gmatutil/util/CubicSpline.cpp:254-256` | CubicSpline |
| Horner 求值 $y,y',y''$ | `src/gmatutil/util/CubicSpline.cpp:157-159` | CubicSpline |
| 四阶单边差分系数 $(-25/12,4,-3,4/3,-1/4)/h$ | `src/gmatutil/util/CubicSpline.cpp:335` | CubicSpline |
| 线性插值 $\Delta=(x-x_k)/(x_{k+1}-x_k)$ | `src/gmatutil/util/interpolator/LinearInterpolator.cpp:136-142` | LinearInterpolator |
| Hermite 阶数 $m(dv+1)-1$ | `src/gmatutil/util/interpolator/HermiteInterpolator.cpp:393` | HermiteInterpolator |
| 差商递推（重复节点用导数） | `src/gmatutil/util/interpolator/HermiteInterpolator.cpp:414-420` | HermiteInterpolator |
| Newton 求值 $P=\sum q_k\prod(x-x_j)$ | `src/gmatutil/util/interpolator/HermiteInterpolator.cpp:483-490` | HermiteInterpolator |
| 导数项 $\sum_i\prod_{j\neq i}(x-x_j)$ | `src/gmatutil/util/interpolator/HermiteInterpolator.cpp:552-564` | HermiteInterpolator |
| 切比雪夫归一化 $T_c=2(t-T_{seg})/T_{sub}-1$ | `src/base/solarsys/DeFile.cpp:1842/1859` | DeFile |
| 切比雪夫递推 $T_j=2T_cT_{j-1}-T_{j-2}$ | `src/base/solarsys/DeFile.cpp:1890` | DeFile |
| 一阶导数递推 $U_j=2T_cU_{j-1}+2T_{j-1}-U_{j-2}$ | `src/base/solarsys/DeFile.cpp:1891` | DeFile |
| 二阶导数递推 $W_j=2T_cW_{j-1}+4U_{j-1}-W_{j-2}$ | `src/base/solarsys/DeFile.cpp:1892` | DeFile |
| 位置/速度/加速度求和与链式因子 $2G/(T_{span}\cdot86400)$ | `src/base/solarsys/DeFile.cpp:1899-1909` | DeFile |
| 章动求和（2 分量） | `src/base/solarsys/DeFile.cpp:1640-1652` | DeFile |
| 天平动＋速率（3 分量） | `src/base/solarsys/DeFile.cpp:1392-1415` | DeFile |
| 状态差分递推 $\Delta T_j=2T_{c2}\Delta T_{j-1}+2\Delta t_c T_{j-1}-\Delta T_{j-2}$ | `src/base/solarsys/DeFile.cpp:2201-2209` | DeFile |
| 记录定位偏移 $\pm\lceil T_{\Delta}/T_{span}\rceil$ | `src/base/solarsys/DeFile.cpp:1075-1085` | DeFile |
| 重心权重 $w_j=1/\prod_{k\neq j}(x_j-x_k)$ | `src/csalt/src/util/BaryLagrangeInterpolator.cpp:616-624` | BaryLagrangeInterpolator |
| 重心矩阵 $B_{ij}=w_j/(t_i-x_j)$ 行归一化 | `src/csalt/src/util/BaryLagrangeInterpolator.cpp:586-601` | BaryLagrangeInterpolator |
| 矩阵求值 $\mathbf p=\mathbf B\mathbf f$ | `src/csalt/src/util/BaryLagrangeInterpolator.cpp:321` | BaryLagrangeInterpolator |
| 反函数样条：`AddPoint(lhs, &epoch)`＋`Interpolate(goal, &stopEpoch)` | `src/base/stopcond/StopCondition.cpp:845,849` | StopCondition |
| 括入判定 $g^*\in[\min g_i,\max g_i]$ | `src/base/stopcond/StopCondition.cpp:834` | StopCondition |
| 时间条件线性换算 $dt=(goal-prev)\cdot k$ | `src/base/stopcond/StopCondition.cpp:898` | StopCondition |
| 默认插值器 NotAKnot（5 点） | `src/base/stopcond/StopCondition.cpp:175` | StopCondition |
| Code500 窗口：目标落在第 2、3 点之间 | `plugins/EphemPropagatorPlugin/src/base/propagator/Code500Propagator.cpp:1484-1491` | Code500Propagator |
| Code500 5 点 AddPoint（DUL→km 换算） | `plugins/EphemPropagatorPlugin/src/base/propagator/Code500Propagator.cpp:1535-1549` | Code500Propagator |
| Code500 插值取状态 | `plugins/EphemPropagatorPlugin/src/base/propagator/Code500Propagator.cpp:1189-1191` | Code500Propagator |
