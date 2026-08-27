# GMAT 公式与模型深度解析（Math Deep-Dive）

> 本目录是 GMAT 中**所有数学公式与物理模型的公式级深度解析**：每个条目给出
> ① 公式（LaTeX）② 真实代码位置（文件:行）③ 深度讲解（背景/推导/实现/数值特性）。
> 与父目录 `gmat-architecture-docs/` 的架构章节互补：架构章讲"类与调用链"，本目录讲"公式与算法"。
> 仓库：L:\gmat888（main，commit ce6eba2）。所有行号均经 read 工具核实。

## 章节目录

| 章 | 内容 | 源码范围 |
|---|---|---|
| [第1章](MD-01-time.md) | 时间系统与历元数学 | GmatTime、TimeSystemConverter、DateUtil、TimeTypes（TAI/TT/TDB/UTC、儒略日、闰秒） |
| [第2章](MD-02-coordsystems.md) | 坐标系与参考架旋转数学 | coordsystem/、Planet IAU 2000 定向、EopFile、ICRF↔FK5 旋转 |
| [第3章](MD-03-orbitelements.md) | 轨道要素与状态转换数学 | StateConversionUtil、Anomaly、OrbitData、SpacecraftOrbitState、平动点 |
| [第4章](MD-04-integrators.md) | 数值积分器数学 | RK89/PD45/PD78/Fehlberg56/RKN/DEP68/ABM/Cowell（Butcher 表、步长控制） |
| [第5章](MD-05-interpolation.md) | 插值、样条与切比雪夫数学 | Interpolator 族、NotAKnot 样条、DE 星历切比雪夫、CSALT 重心插值 |
| [第6章](MD-06-linearalgebra.md) | 线性代数与矩阵运算数学 | Rmatrix/Rvector、求逆/分解、Jacobian 差分、CSALT 稀疏工具 |
| [第7章](MD-07-attitude.md) | 姿态表示与运动学数学 | 四元数/DCM/欧拉角/MRP 换算、运动学、自旋/对地指向 |
| [第8章](MD-08-gravity.md) | 引力场模型数学 | 点质量、球谐（Pines 递推）、潮汐、多面体重力（Werner-Scheeres） |
| [第9章](MD-09-atmosphere-srp.md) | 大气阻力与太阳光压模型数学 | 指数大气、Jacchia-Roberts、MSIS、锥形地影、SPAD/N-Plate、相对论 |
| [第10章](MD-10-burns-thrust.md) | 机动与推力模型数学 | 脉冲/有限机动、Isp 与质量流、推力表格插值 |
| [第11章](MD-11-solvers.md) | 打靶求解器与优化器数学 | DifferentialCorrector（Newton/Broyden）、fmincon、Yukon、VF13ad |
| [第12章](MD-12-estimation-measurements.md) | 轨道估计滤波与测量模型数学 | 批估计最小二乘、EKF、测距/测速/测角、误差模型 |
| [第13章](MD-13-csalt.md) | CSALT 最优控制配点数学 | Lobatto/Radau 配点、隐式 RK Butcher 表、缺陷约束、重心插值 |
| [第14章](MD-14-mathexpressions.md) | 脚本数学表达式引擎数学 | MathNode 表达式树与全部内置函数公式 |

## 与架构章节的对应关系

| 数学域 | 架构章（类与调用链） | 本目录章（公式与算法） |
|---|---|---|
| 力模型/太阳系 | [CH06](../CH06-dynamics.md) | MD-08 引力、MD-09 大气光压、MD-02 参考架 |
| 传播器/积分器/姿态/停止条件 | [CH07](../CH07-propagator.md) | MD-04 积分器、MD-07 姿态、MD-05 插值 |
| 求解器/参数/订阅者 | [CH08](../CH08-base-subsystems.md) | MD-11 求解器、MD-06 线性代数 |
| 估计/测量插件 | [CH13](../CH13-plugins-a.md) | MD-12 估计滤波与测量 |
| 多面体重力/TLE/推力文件 | [CH14](../CH14-plugins-b.md) | MD-08 多面体重力、MD-10 推力表格 |
| CSALT | [CH15](../CH15-csalt-interop-tests.md) | MD-13 配点数学 |
| 脚本数学引擎 | [CH03](../CH03-math.md) | MD-14 表达式引擎 |
| 基础层 | [CH02](../CH02-foundation.md) | MD-01 时间、MD-03 要素转换、MD-06 矩阵 |

## 每个条目的固定格式

```
### <条目名>
- **公式**：LaTeX（从代码实现中提炼）
- **代码位置**：src/... 真实相对路径 + 行号
- **深度讲解**：物理/数学背景、推导要点、实现细节（代码片段+中文注释）、数值特性、使用场景
```
每章末尾附「公式索引表」：| 公式 | 文件:行 | 所属类 |，可快速检索。

## 阅读建议
- 轨道动力学主线：MD-03 要素 → MD-04 积分器 → MD-08 引力 → MD-09 大气光压 → MD-02 参考架
- 姿态链：MD-07 →（被 MD-09 消费）
- 任务设计/优化链：MD-11 求解器 → MD-12 估计 → MD-13 CSALT
- 底层数学工具：MD-01 时间、MD-05 插值、MD-06 线性代数、MD-14 表达式引擎
