# 第6章 线性代数与矩阵运算数学

> 本章覆盖 GMAT 中所有**矩阵/向量数值算法**的公式级解析：稠密矩阵内核（`Rmatrix`/`Rvector` 及其定长特化 `Rmatrix33`/`Rmatrix66`/`Rvector3`/`Rvector6`）、分解与求逆族（LU/Cholesky/QR/Schur，`src/gmatutil/util/matrixoperations/`）、差分雅可比（`src/base/solver/Jacobian.*` 与 `src/gmatutil/util/NumericJacobian.*`）、CSALT 稀疏矩阵工具（`src/csalt/src/util/SparseMatrixUtil.*`）以及参数系统中的矩阵/向量参数类（`src/base/parameter/`）。
> 术语与调用链约定沿用 [../CH03-math.md](../CH03-math.md)（脚本表达式层 `Inverse/Determinant/Transpose` 等函数节点薄薄委托到本章内核，见该章 §2.4）与 [../CH15-csalt-interop-tests.md](../CH15-csalt-interop-tests.md)（CSALT 稀疏 NLP 装配链、`RSMatrix` 类型别名，见该章 §2.1.2）；本章只写公式与算法本身，不重复上述章节的类层次叙述。
> 所有行号均经 read 工具核实（仓库 commit ce6eba2）。

## 6.1 总览：矩阵栈的分层

GMAT 的线性代数自底向上分四层：

| 层 | 位置 | 职责 |
|---|---|---|
| 容器模板 | `TableTemplate<T>`（Rmatrix 父类）、`ArrayTemplate<T>`（Rvector 父类） | 行主序一维存储 `elementD[]`、尺寸 `rowsD/colsD`、边界检查 |
| 稠密代数内核 | `Rmatrix`/`Rvector`（`src/gmatutil/util/`） | 乘/除/转置/行列式/求逆/伪逆/对称分解 |
| 定长特化 | `Rmatrix33`/`Rmatrix66`/`Rvector3`/`Rvector6` | 固定维度、循环全展开、零动态分配 |
| 分解/求解器 | `matrixoperations/`（LU/Cholesky/QR/Schur） | 由 `EstimationPlugin` 批估计器按 `InversionType` 选用 |

消费关系（详见 6.12）：状态转移矩阵（STM）求逆（测距/测角光行时迭代 `phi = tSTM * tSTMtm.Inverse()`）、批估计信息矩阵求逆（`InversionType = Internal/Schur/Cholesky`）、微分校正器 `jac.Pseudoinverse()`、CSALT NLP 雅可比（稀疏形式）。

## 6.2 Rmatrix：稠密矩阵内核

### Rmatrix 存储模型（行主序一维数组）

- **公式**：$A$ 为 $m\times n$ 矩阵，元素 $a_{ij}$ 存储在 `elementD[i*n + j]`（行主序）；`GetElement(i,j)`/`operator()(i,j)` 均按此寻址。
- **代码位置**：`src/gmatutil/util/Rmatrix.cpp:486-491`（乘法内循环以 `elementD[i*colsD + k]` 取元素）、`:71-74`（构造时逐元素清零）、`src/gmatutil/util/Rmatrix.hpp:45`（`class Rmatrix : public TableTemplate<Real>`）。
- **深度讲解**：Rmatrix 是模板 `TableTemplate<Real>` 的实例化（`Rmatrix.cpp:49` `template class TableTemplate<Real>;`），继承 `rowsD/colsD/isSizedD/elementD` 等成员。所有算术运算（加减乘、转置、求逆）都直接对 `elementD` 做索引运算，避免二次间接。`operator==` 用 `REAL_TOL` 容差逐元素比较（`Rmatrix.cpp:267-268`），而非严格相等——这是数值软件与教科书实现的典型差异。维度不一致时抛 `TableTemplateExceptions::DimensionError()`（如 `Rmatrix.cpp:445`），未定尺寸抛 `UnsizedTable()`。

### Rmatrix 矩阵乘法 operator*

- **公式**：$\mathbf C = \mathbf A\mathbf B,\quad c_{ij}=\sum_{k=0}^{p-1} a_{ik}b_{kj}$，其中 $\mathbf A\in\mathbb R^{m\times p},\ \mathbf B\in\mathbb R^{p\times n}$，$\mathbf C\in\mathbb R^{m\times n}$。
- **代码位置**：`src/gmatutil/util/Rmatrix.cpp:418-499`；核心三重循环 `:486-497`。
- **深度讲解**：
  - 三重循环为教科书式 ijk 序（非缓存友好的 ikj 序），对 GMAT 常用的 3×3/6×6 规模开销可忽略；大矩阵（>9 阶）在行列式路径中已改走 LU（见 6.2.5 行列式条目）。
  - 支持 1×1 标量退化广播：`1x1 * MxN` 或 `MxN * 1x1` 时按标量乘法展开（`Rmatrix.cpp:454-483`），这是脚本表达式层 `Multiply` 节点（见 CH03 §2.3）依赖的行为。
  - 无任何并行/向量化；`operator*=` 走 `*this = *this * m`（`:505-512`）。
  - 消费方：几乎一切——姿态 DCM 合成（Rmatrix33 特化版）、STM 传播 `phi = tSTM * tSTMtm.Inverse()`（`plugins/EstimationPlugin/src/base/measurementmodel/GPSPointMeasureModel.cpp:1162`）、协方差传播 `P = phi*P*phi^T`。

### Rmatrix 矩阵×向量 operator*(Rvector)

- **公式**：$\mathbf y = \mathbf A\mathbf v,\quad y_i=\sum_{j=0}^{n-1} a_{ij}v_j$，$\mathbf v\in\mathbb R^{n}$，$\mathbf y\in\mathbb R^{m}$。
- **代码位置**：`src/gmatutil/util/Rmatrix.cpp:803-830`。
- **深度讲解**：`colsD != v.sizeD` 时抛 `DimensionError`（`:811-812`）。注意实现先把每个乘积写入 `prod.elementD[i]` 再累加到 `var`（`:823-824`），即每行内先乘后加、最后一次性赋值，等价于 $y_i=\sum_j a_{ij}v_j$。向量右乘矩阵的对称操作在 `Rvector::operator*(const Rmatrix&)`（`Rvector.cpp:667-694`，把向量视为 1×N 行向量，$v'_j=\sum_i m_{ji}v_i$），向量除以矩阵则先 `m.Inverse()` 再乘（`Rvector.cpp:717-738`）。

### Rmatrix 转置 Transpose()

- **公式**：$\mathbf T=\mathbf A^{\mathsf T},\quad t_{ji}=a_{ij}$。
- **代码位置**：`src/gmatutil/util/Rmatrix.cpp:1072-1091`。
- **深度讲解**：结果矩阵尺寸为 `(colsD, rowsD)`（`:1079`），逐元素 `tran(j, i) = elementD[i*colsD + j]`（`:1086`），即行主序下读取按原矩阵行推进、写入按转置矩阵行推进，无原地转置优化。与三个友元乘积函数配合可避免显式构造转置矩阵：`TransposeTimesMatrix(A,B)=AᵀB`、`MatrixTimesTranspose(A,B)=ABᵀ`、`TransposeTimesTranspose(A,B)=AᵀBᵀ`（见 6.2.10 友元乘积族条目），它们直接以 `m1(k,i)*m2(k,j)` 等下标组合求和（`:1548`、`:1580`、`:1612`），省一次整矩阵拷贝——最小二乘正规方程 $A^{\mathsf T}A$、协方差 $A A^{\mathsf T}$ 的常用实现路径。

### Rmatrix 行列式 Determinant() 与余子式 Cofactor()

- **公式**（按阶数分派）：
  - $n=1$：$\det A = a_{11}$（`Rmatrix.cpp:956`）
  - $n=2$：$\det A = a_{11}a_{22}-a_{12}a_{21}$（`:963`）
  - $n=3$：Sarrus 法则 $a_{11}a_{22}a_{33}+a_{12}a_{23}a_{31}+a_{13}a_{21}a_{32}-a_{13}a_{22}a_{31}-a_{12}a_{21}a_{33}-a_{11}a_{23}a_{32}$（`:970-975`）
  - $4\le n\le 9$：第一行拉普拉斯展开 $\det A=\sum_{j}a_{0j}C_{0j}$，$C_{0j}=(-1)^{0+j}\det M_{0j}$（`:994-1004`）
  - $n>9$：改调 `LUFactorization::Determinant`，$\det A=(-1)^n\prod_{i}u_{ii}$（`:979-988`；`LUFactorization.cpp:543-555`）
- **代码位置**：`src/gmatutil/util/Rmatrix.cpp:937-1011`（Determinant）、`:1017-1066`（Cofactor）。
- **深度讲解**：
  - `Cofactor(r,c)` 先构造删去第 r 行第 c 列的 $(n-1)\times(n-1)$ 子矩阵（`:1036-1055`），递归调 `Determinant()`（`:1060`），再按 `(r+c)%2==1` 取负号（`:1063-1064`）——即教科书 $C_{ij}=(-1)^{i+j}\det M_{ij}$。
  - 数值上，4~9 阶的拉普拉斯展开是 $O(n!)$ 灾难，代码注释明确承认 "Currently limited by inefficiencies in the algorithm"（`:979`），故 9 阶以上强制走 LU（$O(n^3)$），`Cofactor` 对 $n>9$ 直接抛异常（`:1030-1035`）。这解释了为何 Rmatrix::Determinant 对 >9 阶与 ≤9 阶采用截然不同的算法——前者是为了避免阶乘级爆炸。
  - 消费方：脚本表达式 `Determinant` 函数节点（CH03 §2.4，`src/base/math/Determinant.cpp:160-173` 调 `MatrixEvaluate().Determinant()`）；Rmatrix::Pseudoinverse 用它做奇异性预检（`Rmatrix.cpp:1440`、`:1449`）。

### Rmatrix 求逆 Inverse(Real zeroValue)

- **公式**：对一般方阵使用**全选主元 Gauss-Jordan 消元**（complete pivoting）：
  1. 第 $n$ 步在未被占用的行/列集合中选主元 $a_{pq}$ 满足 $|a_{pq}|=\max_{i,j\ \text{可用}}|a_{ij}|$（`:1164-1181`）；
  2. 交换行 $p\leftrightarrow q$ 使主元落在"对角"位置，并归一化 $a_{q,:}\leftarrow a_{p,:}/a_{pq}$（`:1194-1199`，代码中交换后旧主元行写入 $A(q,j)$）；
  3. 消元：对 $i\ne q$，$a_{i,:}\leftarrow a_{i,:}-a_{iq}\,a_{q,:}$，同时置 $a_{iq}=0$（`:1202-1213`）；
  4. 全部 $n$ 步完成后，按记录的 `PivotRowList/PivotColumnList` 反向交换列，把单位阵列位置还原（`:1217-1226`），最终 $A$ 即 $A^{-1}$。
  另外对**对角矩阵**走快速路径：$A^{-1}=\mathrm{diag}(1/a_{ii})$（`:1110-1141`）。
- **代码位置**：`src/gmatutil/util/Rmatrix.cpp:1097-1228`（带零阈值版）、`:1234-1237`（默认 `zeroValue = 1e-12`）。
- **深度讲解**：
  - 奇异判定：主元绝对值小于 `zeroValue`（默认 $10^{-12}$）即抛 `Rmatrix::IsSingular`（`:1183-1184`）。`zeroValue` 由 `Inverse(zeroValue)` 传入，EKF/批估计对病态信息矩阵可放宽此阈值（见 6.12 消费链总结中 BatchEstimator 一项）。
  - 全选主元（行列都搜）比部分选主元（只搜列）更稳：每一步保证 $|a_{pq}|\ge |a_{ij}|$（剩余子矩阵），增长因子被严格压制；代价是 $O(n^2)$ 的额外搜索与列交换记录。对估计协方差（近奇异、量级差异大）这是最稳妥的通用路径。
  - 若 `isDiagonal` 检测（`:1110-1123`）发现非对角元非零，则回落到全选主元消元；该快速路径服务于信息矩阵为对角阵的特殊情形（如无耦合参数的估计）。
  - 代码片段（消元核心，`:1194-1213`）：
    ```cpp
    // 归一化并交换行: 主元行(旧 p)内容换到 q 行并除以主元
    for (j = 0; j < IndexRange; j++) {
       tmp = A(PivotRow, j);
       A(PivotRow, j) = A(PivotColumn, j);   // 行 p ← 行 q（主元行占位）
       A(PivotColumn, j) = tmp / PivotElement; // 行 q ← 行 p / 主元
    }
    // 消元: 除主元行(现位于 q)外所有行减去主元列倍数的 q 行
    for (i = 0; i < IndexRange; i++) {
       if (i != PivotColumn) {              // 跳过已主元化的行
          tmp = A(i, PivotColumn);          // 保存待消元素 a_iq
          A(i, PivotColumn) = 0.0;          // 该列直接置零
          for (j = 0; j < IndexRange; j++)
             A(i, j) = A(i, j) - A(PivotColumn, j)*tmp; // 行消元
       }
    }
    ```
  - 消费方：脚本 `Inverse` 节点（`src/base/math/Inverse.cpp:159-192`）；批估计默认 `InversionType = "Internal"` 路径 `reducedCovMatrix = reducedInfMatrix.Inverse()`（`plugins/EstimationPlugin/src/base/estimator/BatchEstimator.cpp:1770`）；STIM 求逆 `solv2KeplMatrix.Inverse()`（`plugins/EstimationPlugin/src/base/estimator/Estimator.cpp:5163`）；Rmatrix 除法 `operator/` 即 `this * m.Inverse()`（`Rmatrix.cpp:579`）。

### Rmatrix 伪逆 Pseudoinverse(Real zeroValue)

- **公式**（按形状分派）：
  - 行数 < 列数（宽矩阵，欠定）：$\mathbf A^+=\mathbf A^{\mathsf T}(\mathbf A\mathbf A^{\mathsf T})^{-1}$（`Rmatrix.cpp:1439-1441`）
  - 行数 > 列数（高矩阵，超定）：$\mathbf A^+=(\mathbf A^{\mathsf T}\mathbf A)^{-1}\mathbf A^{\mathsf T}$（`:1448-1450`）
  - 方阵：$\mathbf A^+=\mathbf A^{-1}$（`:1456`）
- **代码位置**：`src/gmatutil/util/Rmatrix.cpp:1425-1458`。
- **深度讲解**：
  - 这是**左/右逆形态的 Moore–Penrose 伪逆**，仅当对应的 Gram 矩阵 $AA^{\mathsf T}$ 或 $A^{\mathsf T}A$ 可逆时有效（即 A 满行秩或满列秩）。实现先调 `LUFactorization::Determinant` 预检（`:1440`、`:1449`，`accuracyRequired = 0.005`），但**无论检测结果如何都照常求逆**（两个分支代码相同，`:1440-1443` 与 `:1448-1452`，原抛奇异异常的行被注释掉）——即秩亏时行为退化为"仍计算普通逆，可能得到巨大数值"。
  - 数值稳定性：构造 $A^{\mathsf T}A$ 会把条件数平方（$\kappa(A^{\mathsf T}A)=\kappa(A)^2$），对病态雅可比损失精度；这正是微分校正器中处理奇异/欠定雅可比的路径，见 6.12 消费链总结。
  - 消费方：`DifferentialCorrector.cpp:1599` 用 `jac.Pseudoinverse()` 计算校正步（见 [MD-11-solvers.md](MD-11-solvers.md)）；`GmatMathUtil` 无对应函数，脚本层不直接暴露。

### Rmatrix::PsuedoInverseOfSymmetricMatrix(Real zeroValue)

- **公式**（对称矩阵的满/亏秩伪逆，分 7 步）：
  1. 用修正 Gram–Schmidt 识别 $n$ 个列中 $r$ 个独立列（索引集 $R$）与 $n-r$ 个相关列（$D$）：$\mathbf u_i=\mathbf c_i-\sum_{j}(\mathbf e_j^{\mathsf T}\mathbf c_i)\mathbf e_j$，若 $\|\mathbf u_i\|/\max A< \text{zeroValue}$ 判为相关（`Rmatrix.cpp:1261-1279`）；
  2. 构造置换矩阵 $\mathbf P$ 使独立列排前（`:1300-1311`），$\mathbf A=\mathbf P\mathbf M\mathbf P^{\mathsf T}$（`:1327-1339`）分块为 $\mathbf A=\begin{bmatrix}\mathbf A_1 & \mathbf A_2\\ \mathbf A_2^{\mathsf T} & \mathbf A_3\end{bmatrix}$，$\mathbf A_1\in\mathbb R^{r\times r}$（`:1352-1355`）；
  3. $\boldsymbol\alpha=\mathbf A_1^{-1}\mathbf A_2$（`:1370-1377`）；
  4. $\mathbf W=\begin{bmatrix}\mathbf I_r & \boldsymbol\alpha\\ \mathbf 0 & \mathbf I_{n-r}\end{bmatrix}$，$\mathbf M^+=\begin{bmatrix}\mathbf A_1^{-1} & \mathbf 0\\ \mathbf 0 & \mathbf 0\end{bmatrix}$（`:1391-1409`）；
  5. $\mathbf V=\mathbf W\mathbf P^{\mathsf T}$，$\mathbf U=\mathbf P^{\mathsf T}\mathbf W^{\mathsf T}$，$\mathbf U^+=(\mathbf U^{\mathsf T}\mathbf U)^{-1}\mathbf U^{\mathsf T}$，$\mathbf V^+=(\mathbf V^{\mathsf T}\mathbf V)^{-1}\mathbf V^{\mathsf T}$（`:1412-1415`）；
  6. $\mathbf M^+=\mathbf V^+\mathbf M^+\mathbf U^+$（`:1416`）。
- **代码位置**：`src/gmatutil/util/Rmatrix.cpp:1247-1419`。
- **深度讲解**：
  - 该算法把秩亏对称矩阵经置换降维到 $r\times r$ 满秩块再求逆，避免奇异；`zeroValue` 默认 $10^{-12}$，控制"相关列"的判定阈值（`:1270`）。
  - 数值注意：步骤 5 中 $U^{\mathsf T}U$、$V^{\mathsf T}V$ 的求逆同样存在条件数平方问题；且 `u.GetMagnitude()/maxA < zeroValue` 使用**相对**阈值（除以历史最大列模 `maxA`，`:1270-1276`），对量级差异大的估计矩阵更稳。
  - 该拼写 `Psuedo...`（缺一个 u）为源码原样，勿"纠正"。当前仓库未见直接调用点，属于为估计器预留的能力。

### Rmatrix Symmetric() / AntiSymmetric() / Trace() / IsOrthogonal() / IsOrthonormal()

- **公式**：
  - $\mathrm{Sym}(\mathbf A)=\frac{1}{2}(\mathbf A+\mathbf A^{\mathsf T})$（`Rmatrix.cpp:1474`）；$\mathrm{AntiSym}(\mathbf A)=\frac{1}{2}(\mathbf A-\mathbf A^{\mathsf T})$（`:1491`）
  - $\mathrm{tr}(\mathbf A)=\sum_i a_{ii}$（`:927`）
  - 正交性：$\mathbf c_i\cdot\mathbf c_j=0\ (i\ne j)$，列两两点积为零（`:170-177`）；标准正交额外要求 $\|\mathbf c_i\|=1$（`:221-225`，再叠加 `IsOrthogonal` 结果 `:231`）
- **代码位置**：`src/gmatutil/util/Rmatrix.cpp:913-931`（Trace）、`:1464-1475`（Symmetric）、`:1481-1492`（AntiSymmetric）、`:141-185`（IsOrthogonal）、`:192-232`（IsOrthonormal）。
- **深度讲解**：正交性检测把列拷贝进 `Rvector` 数组后两两做点积，容差由 `accuracyRequired`（默认 `REAL_EPSILON`）经 `GmatMathUtil::IsZero` 判定。消费方：姿态库验证 DCM 合法性、估计器协方差对称性检查（对称化 $P\leftarrow (P+P^T)/2$）。

### Rmatrix 友元乘积族：TransposeTimesMatrix / MatrixTimesTranspose / TransposeTimesTranspose / SkewSymmetric4by4

- **公式**：
  - $\mathbf C=\mathbf A^{\mathsf T}\mathbf B:\ c_{ij}=\sum_k a_{ki}b_{kj}$（`Rmatrix.cpp:1548`），要求 $\mathrm{row}(A)=\mathrm{row}(B)$
  - $\mathbf C=\mathbf A\mathbf B^{\mathsf T}:\ c_{ij}=\sum_k a_{ik}b_{jk}$（`:1580`），要求 $\mathrm{row}(A)=\mathrm{row}(B)$
  - $\mathbf C=\mathbf A^{\mathsf T}\mathbf B^{\mathsf T}:\ c_{ij}=\sum_k a_{ki}b_{jk}$（`:1612`）
  - 4×4 歪对称矩阵（`SkewSymmetric4by4`）：$\begin{bmatrix}0 & v_3 & -v_2 & v_1\\ -v_3 & 0 & v_1 & v_2\\ v_2 & -v_1 & 0 & v_3\\ -v_1 & -v_2 & -v_3 & 0\end{bmatrix}$（`:1499-1522`）
- **代码位置**：`src/gmatutil/util/Rmatrix.cpp:1529-1554`、`:1561-1586`、`:1593-1618`、`:1499-1522`；声明见 `src/gmatutil/util/Rmatrix.hpp:137-140`。
- **深度讲解**：三个转置乘积友元避免了"先构造 $A^{\mathsf T}$ 再乘"的整矩阵拷贝与两次 $O(n^3)$ 扫描，直接合并为一次求和，是正规方程 $A^{\mathsf T}WA$、协方差 $AA^{\mathsf T}$ 的推荐实现（`Pseudoinverse` 即用它们，`Rmatrix.cpp:1439/1448`）。Rmatrix33/Rmatrix66 有同名的 9 元素/36 元素全展开版本（见 6.3）。`SkewSymmetric4by4` 服务于 4 参数姿态表示的微分代数（对应四元数运动学中的 $\Omega(\omega)$ 矩阵），3×3 版本在 `Rmatrix33.cpp:511-525`。

### Rmatrix 元素级运算与标量运算

- **公式**：
  - 元素级乘/除：$(A\circ B)_{ij}=a_{ij}b_{ij}$、$(A\oslash B)_{ij}=a_{ij}/b_{ij}$（`Rmatrix.cpp:600-631`）
  - 标量加/减/乘/除：$(A+s)_{ij}=a_{ij}+s$ 等（`:636-776`），除零检查 `GmatMathUtil::IsZero(scalar)` 抛 `Rmatrix::DivideByZero`（`:749-750`）
  - 取负：$(-A)_{ij}=-a_{ij}$（`:782-797`）
- **代码位置**：`src/gmatutil/util/Rmatrix.cpp:600-631`、`:636-797`。
- **深度讲解**：元素级运算要求两矩阵同尺寸（`:606-607`），用于协方差逐元素缩放（如单位换算）；标量除法先 `IsZero` 守卫再逐元素除，`IsZero` 的容差语义（相对机器精度）避免除极小值溢出。`Identity(size)`/`Diagonal(size, data)` 工厂方法（`:108-126`）为估计器构造单位/对角先验协方差服务。

### Rmatrix 行/列视图与向量互转

- **公式**：`GetRow(r)`/`GetColumn(c)` 返回 `Rvector`（拷贝语义，`Rmatrix.cpp:1641-1663`）；`MakeOneRowMatrix(v)`/`MakeOneColumnMatrix(v)` 把向量扩为 1×N / N×1 矩阵（`:1698-1724`）；`GetRowOrColumn()` 对 1×N 或 N×1 取唯一非平凡行/列（`:1672-1687`）。
- **代码位置**：`src/gmatutil/util/Rmatrix.cpp:1641-1724`。
- **深度讲解**：返回的是值拷贝而非视图，保证调用方修改不污染原矩阵；`PsuedoInverseOfSymmetricMatrix` 依赖 `GetColumn` 提取各列做独立性判定（`:1264`）。`Rvector` 侧对应外积 `Outerproduct(v1,v2) = v1·v2ᵀ`（`Rvector.cpp:935-948`）。

## 6.3 定长特化：Rmatrix33 / Rmatrix66 / Rvector3 / Rvector6

### Rmatrix33 3×3 求逆（伴随矩阵法）

- **公式**：$\mathbf A^{-1}=\dfrac{1}{\det A}\,\mathrm{adj}(\mathbf A)$，其中 $\det A=a_{00}(a_{11}a_{22}-a_{12}a_{21})-a_{01}(a_{10}a_{22}-a_{12}a_{20})+a_{02}(a_{10}a_{21}-a_{11}a_{20})$（`Rmatrix33.cpp:437-444`），伴随阵元素为各 $2\times2$ 余子式转置：
  $$A^{-1}=\frac{1}{D}\begin{bmatrix}a_{11}a_{22}-a_{12}a_{21} & a_{02}a_{21}-a_{01}a_{22} & a_{01}a_{12}-a_{02}a_{11}\\ a_{12}a_{20}-a_{10}a_{22} & a_{00}a_{22}-a_{02}a_{20} & a_{02}a_{10}-a_{00}a_{12}\\ a_{10}a_{21}-a_{11}a_{20} & a_{01}a_{20}-a_{00}a_{21} & a_{00}a_{11}-a_{01}a_{10}\end{bmatrix}$$
- **代码位置**：`src/gmatutil/util/Rmatrix33.cpp:460-483`（Inverse）、`:437-444`（Determinant）、`:449-455`（Transpose）。
- **深度讲解**：这是**显式伴随矩阵公式**而非消元法——注释（`:462-467`）说明奇数 $i+j$ 处通过调换 $2\times2$ 行列式项序省掉一元负号。$\det A$ 为零（`GmatMathUtil::IsZero(D)`）时抛 `Rmatrix::IsSingular`（`:470-471`）。3×3 固定维度使所有运算（乘 `:268-280`、转置乘积族 `:532-579`、对称化 `:488-505`）都写成 9 元素的展开表达式，无循环、无堆分配、可内联——姿态动力学中每积分步大量调用（DCM 合成、坐标系转换、惯性张量求逆），这是"固定维度优化"的核心收益。`Rmatrix33(bool IdentityRmatrix=true)` 构造默认给单位阵（`:61-70`），便于链式初始化。

### Rmatrix66 6×6 运算（委托内核）

- **公式**：乘法 $C_{ij}=\sum_k a_{ik}b_{kj}$（`Rmatrix66.cpp:315-329`）；行列式 $n=6$ 时走第一行拉普拉斯展开 $D=\sum_i a_{0i}C_{0i}$（`:496-501`）；**求逆直接委托** `Rmatrix::Inverse()`（`:525-528`，即 6.2.6 的全选主元 Gauss-Jordan）。
- **代码位置**：`src/gmatutil/util/Rmatrix66.cpp:315-329`、`:479-504`、`:525-528`；4 个 3×3 子块视图 `UpperLeft/UpperRight/LowerLeft/LowerRight`（`:158-200`）。
- **深度讲解**：Rmatrix66 复用内核算法，但提供 36 元素展开的乘/加/标量运算与 `SetUndefined()`（`:149-153`，元素填 `REAL_UNDEFINED` 供协方差"未定义块"标记）。默认构造为单位阵（`:53-61`）。6×6 是 GMAT 轨道状态（位置+速度）的标准维度：STM（状态转移矩阵）为 6×6，`Rvector6`（`Rvector6.hpp:44`）与 `OrbitRvec6` 参数配合。注意 `operator-(Rmatrix66)` 有一处既存 bug：减法分支误写成加法（`:294-295` `diff.elementD[i] = elementD[i] + m.elementD[i]`），使用 `A - B`（Rmatrix66 版）时请留意。

### Rvector3 / Rvector6 定长向量

- **公式**：模长 $\|\mathbf v\|=\sqrt{v_1^2+v_2^2+v_3^2}$（`Rvector3.cpp` 覆写 `GetMagnitude`）；单位化 $\hat v=v/\|v\|$。
- **代码位置**：`src/gmatutil/util/Rvector3.hpp:41-56`（类声明、`GetMagnitude`/`GetUnitVector`/`Normalize`）、`src/gmatutil/util/Rvector6.hpp:44-60`（`Rvector3` 拼接构造 `Rvector6(r, v)`、`GetR()/GetV()`）。
- **深度讲解**：`Rvector3` 继承 `Rvector` 但以三个显式成员承载，`GetMagnitude` 用专用公式省掉 `GetSize` 循环（`Rvector3.cpp`）；`Rvector6` 支持 `Rvector6(Rvector3 r, Rvector3 v)` 组合构造（`Rvector6.hpp:51`），对应轨道状态 $\mathbf x=(r_x,r_y,r_z,v_x,v_y,v_z)$。消费方：`Rmatrix33*Rvector3`（姿态旋转，`Rmatrix33.cpp:400-406`）、`Rmatrix66*Rvector6`（STM 传播，`Rmatrix66.cpp:426-443`）。

## 6.4 分解族基类 MatrixFactorization 与信息矩阵压缩

### MatrixFactorization 抽象基类

- **公式**：纯虚接口 `Invert(Rmatrix&)` 与 `Factor(A, out1, out2)`（`MatrixFactorization.hpp:48-50`）；三个静态工具：
  - `CompressNormalMatrix(inf, removedIdx, auxVec, numRemoved, tol)`：删掉全零行/列，$N\times N \to (N-k)\times(N-k)$（`MatrixFactorization.cpp:118-212`）
  - `ExpandNormalMatrixInverse(cov, auxVec, numRemoved)`：把 $(N-k)\times(N-k)$ 逆扩张回 $N\times N$，删去处填 0（`:236-289`）
  - `PackedArrayIndex(N, i, j)`：对称矩阵上三角压缩存储的线性索引 $=iN-\frac{i(i+1)}{2}+j$（`:312-324`，代码形式 `(2*N*row - row*row + row)/2 + col - row`）
- **代码位置**：`src/gmatutil/util/matrixoperations/MatrixFactorization.hpp:48-57`、`MatrixFactorization.cpp:118-212`、`:236-289`、`:312-324`。
- **深度讲解**：`CompressNormalMatrix` 以 `fabs(a_ij) > epsilon` 判定零行/列（`:150-154`，默认 `tol=0`，批估计传入 `1e-50` 见 6.12），`auxVector[i]=-1` 标记被删维度、否则记录前面删了多少（`:161-168`）；重排时新索引为 `row - auxVector[row]`（`:181`）。`ExpandNormalMatrixInverse` 反向填充零行/列（`:263-273`），保证压缩-求逆-扩张三步得到与直接求逆（对带零行/列矩阵）一致的结果。批估计正是用这一机制处理"从未被测量激励的估计参数"（对应正规方程中恒零的行/列），见 6.12。

## 6.5 LUFactorization：Gauss 消元分解（Golub–Van Loan 算法 3.4.1）

### LU 分解 Factor()

- **公式**（$A=LU$，$L$ 单位下三角，$U$ 上三角；可选部分选主元 $PA=LU$）：
  - 选主元：$\mu_k=\arg\max_{\mu\ge k}|a_{\mu k}|$，交换行 $k\leftrightarrow \mu_k$（`LUFactorization.cpp:156-176`）
  - 归一化：$l_{ik}=a_{ik}/a_{kk},\ i>k$（`:178-187`）
  - 更新：$a_{ij}\leftarrow a_{ij}-l_{ik}a_{kj},\ i,j>k$（`:188-200`）
- **代码位置**：`src/gmatutil/util/matrixoperations/LUFactorization.cpp:111-257`；构造 `LUFactorization(bool pivotOption = true)`（`LUFactorization.hpp:43`，`usePivot` 默认开）。
- **深度讲解**：实现是 Golub–Van Loan *Matrix Computations* 算法 3.4.1 的直接移植（注释 `:104-105`），**就地**分解到副本 `A`，支持矩形矩阵（$k_{\max}=\min(m,n)$，`:130-149`），随后按形状提取 L/U（`:206-235`），并把 $L$ 下三角填 0、对角填 1（`:237-246`），$U$ 上三角以下清零（`:250-256`）——显式构造完整 $L,U$ 矩阵而非压缩存储。`usePivot=true` 时记录置换向量 `permuVector[k]=muMax`（`:175`）。数值稳定性：部分选主元保证 $|l_{ik}|\le 1$，增长因子有界；构造注释建议仅当对角可能接近 0 时开选主元（`:44-47`），但类默认开。确定性行列式（见下）依赖分解后 $U$ 对角。

### LU 求逆 Invert() 与求解 SolveSystem()

- **公式**：
  - 求逆：$A^{-1}$ 的第 $j$ 列 $\mathbf x_j$ 解 $A\mathbf x_j=\mathbf e_j$，即 $L\mathbf y=\mathbf e_j$（前代，`LUFactorization.cpp:320-330`）后 $U\mathbf x=\mathbf y$（回代，`:337-343`）；选主元时先按 `permuVector` 置换 $\mathbf e_j$（`:303-318`）
  - 方阵求解：同上，右端为 $\mathbf b$（`:366-422`）
  - 超定系统（$m>n$）：转 QR 分解路径求最小二乘（`:426-474`，见 6.7）
  - 欠定系统（$m<n$）：算法 5.7.2 求最小 2-范数解（`:476-527`）
- **代码位置**：`src/gmatutil/util/matrixoperations/LUFactorization.cpp:269-346`（Invert）、`:364-530`（SolveSystem）。
- **深度讲解**：`Invert` 先算 `determinant` 并检查为零即抛奇异（`:277-284`）——注意这是**分解前**的预检（`Determinant` 内部会再分解一次，`Invert` 随后又 `Factor` 一次，共 2~3 次分解，性能上有冗余）。前代循环 `y[i] -= L(i,j)*y[j]`（`:327`）与回代 `x[i] = (x[i]-ΣU(i,j)x[j])/U(i,i)`（`:337-343`）都是教科书形式。欠定路径用 $A^T$ 的 QR 分解：$A^{\mathsf T}=QR$，解得 $x=Q\,(R^{\mathsf T})^{-1}b$（`:480-513`，代码中 `partR = Rᵀ` 为下三角），并借 `paramMatrix`（列置换记录）把解映回原变量顺序（`:518-525`）。

### LU 行列式 Determinant()

- **公式**：$\det A=(-1)^n\prod_{i=0}^{n-1}u_{ii}$（`LUFactorization.cpp:543-555`）。
- **代码位置**：`src/gmatutil/util/matrixoperations/LUFactorization.cpp:543-555`。
- **深度讲解**：$A=LU$ 且 $L$ 单位下三角（$\det L=1$），故 $\det A=\det U=\prod u_{ii}$；代码用 `pow(-1, n)` 施加符号（`:553`），对应 $n$ 次行交换的奇偶性（严格说符号应来自实际交换次数，此实现以 $n$ 近似）。`Rmatrix::Determinant` 对 $n>9$ 与 `QRFactorization::Determinant` 都委托到这里（`Rmatrix.cpp:979-988`、`QRFactorization.cpp:891-899`）。

## 6.6 CholeskyFactorization：对称正定分解（GEODYN 移植）

### Cholesky 分解 Factor()

- **公式**（上三角存储 $A=R^{\mathsf T}R$ 或取上三角 $R$，逐行递归）：
  - 对角元：$r_{kk}=\sqrt{a_{kk}-\sum_{l<k}r_{lk}^{2}}$（`CholeskyFactorization.cpp:183-188`，`dsum > tolerance` 时 `dPivot=sqrt(dsum)` 并存根）
  - 非对角元：$r_{ki}=\left(a_{ki}-\sum_{l<k}r_{lk}r_{li}\right)/r_{kk}$（`:181-182`，`dsum*dPivot`，`dPivot=1/r_{kk}`）
  - 容差：$\mathrm{tol}=|\varepsilon\cdot a_{kk}|$，$\varepsilon=10^{-10}$（`:160`、`:167`）
- **代码位置**：`src/gmatutil/util/matrixoperations/CholeskyFactorization.cpp:129-228`；输入按上三角压缩到 `sum1[0..n(n+1)/2-1]`（`:146-156`，复用 `PackedArrayIndex` 的布局约定）。
- **深度讲解**：
  - 这是 GEODYN 求逆代码的移植（注释 `:237-238`），1 基索引、压缩上三角数组、`rowCountIf` 等是 FORTRAN 遗产；`j` 的推进（`:203-205`）逐行扫过上三角。
  - 正定性守卫：`dsum <= 0.0` 抛 "Matrix must be positive definite"（`:197-202`）；`0 < dsum <= tol` 时仍取平方根但发 WARNING（`:189-196`），提示对角元可能极小——这是病态（半正定）信息矩阵的早期预警，批估计用它做 Schur 求逆前的"可逆性探针"（见 6.12）。
  - 数值：$\kappa(A)$ 与 $\kappa(R)$ 呈平方根关系（$\kappa(A)=\kappa(R)^2$），分解本身比 $A^{-1}$ 稳定得多；但无选主元，要求 SPD。
- **代码片段**（对角/非对角主循环，`:168-204`）：
  ```cpp
  for (i = k; i <= rowCount; ++i) {
     dsum = 0.0;
     if (k != 1)                       // 累加已分解行的点积 Σ r_lk * r_li
        for (il = 1; il <= iLeRowCount; ++il) {
           kl = k - il;
           il1 = (kl - 1)*rowCount - (kl - 1)*kl/2;   // 压缩上三角寻址
           dsum = dsum + sum1[il1 + k - 1]*sum1[il1 + i - 1];
        }
     dsum = sum1[j - 1] - dsum;        // 剩余平方和 a_ki - Σ
     if (i > k)  sum1[j - 1] = dsum * dPivot;          // 非对角: r_ki = dsum / r_kk
     else if (dsum > tolerance) {                       // 对角: 取平方根
        dPivot = GmatMathUtil::Sqrt(dsum);
        sum1[j - 1] = dPivot;
        dPivot = 1.0 / dPivot;
     }
     else if (dsum <= 0.0)                              // 非正定即报错
        throw UtilityException("Matrix must be positive definite for Cholesky decomposition.");
     j = j + 1;
  }
  ```

### Cholesky 求逆 Invert()

- **公式**：$A^{-1}=(R^{-1})(R^{-1})^{\mathsf T}$，其中 $R^{-1}$ 为上三角逆（先对角线倒数、再逐列向上回代，`CholeskyFactorization.cpp:252-280`），最终按 $[A^{-1}]_{ij}=\sum_{k\ge\max(i,j)}[R^{-1}]_{ik}[R^{-1}]_{jk}$ 累乘（`:283-298`）。
- **代码位置**：`src/gmatutil/util/matrixoperations/CholeskyFactorization.cpp:243-313`（Rmatrix 版）、`:331-457`（裸数组版 `Invert(Real*, size)`，供既有 GEODYN 风格调用）。
- **深度讲解**：$\det$ 预检不存在（分解本身即正定校验），求逆仅在压缩数组上做两次遍历（$R^{-1}$ 计算与 $R^{-1}R^{-T}$ 合成），比通用 Gauss-Jordan 约省一半浮点运算。对称性利用：只算上三角再镜像回下三角（`:300-311`）。批估计 `InversionType = "Cholesky"` 路径直接调用（`BatchEstimator.cpp:1758-1765`）；协方差/信息矩阵求逆（正规方程 $P=(A^{\mathsf T}WA)^{-1}$）是该类的主消费场景。

## 6.7 QRFactorization：Givens 旋转分解（算法 5.2.2 选项 3）

### QR 分解 Factor()（含列选主元）

- **公式**：$A=QR$，$Q$ 正交、$R$ 上三角。逐列对行对 $(j,i)$（$i=j+1,\dots,m-1$）施加 Givens 旋转：
  $$c=\frac{a_{jj}}{\sqrt{a_{jj}^2+a_{ij}^2}},\quad s=-\frac{a_{ij}}{\sqrt{a_{jj}^2+a_{ij}^2}}$$
  等价实现（`QRFactorization.cpp:855-878`，方程集 5.1.10）：若 $|b|>|a|$：$\tau=-a/b,\ s=1/\sqrt{1+\tau^2},\ c=s\tau$；否则 $\tau=-b/a,\ c=1/\sqrt{1+\tau^2},\ s=c\tau$。行对旋转：
  $$a'_{jj}=c\,a_{jj}-s\,a_{ij},\quad a'_{ij}=s\,a_{jj}+c\,a_{ij}$$
  （`:244-266`，对 $R$ 的 $jj\ge j$ 列与 $Q$ 的对应列同时作用）。列选主元（类似算法 5.4.1）：$c_j=\sum_i a_{ij}^2$ 最大列优先（`:191-217`、`:269-290`），置换记录在 `permuMatrix`。
- **代码位置**：`src/gmatutil/util/matrixoperations/QRFactorization.cpp:125-343`（Factor）、`:855-878`（Givens）。
- **深度讲解**：
  - Givens 旋转避免了 Householder 反射的显式构造，适合逐元素消零；实现中 $m<n$（宽矩阵）先扩成 $n\times n$ 再在末尾裁回（`:137-148`、`:317-321`）。
  - **符号规范化**：强制 $R$ 对角元为正（`signChangeMat`，`:293-303`），保证分解唯一性（$Q$ 随之右乘符号阵）——这是数值库与教科书实现的常见差异点。
  - 选主元模式下 `permuMatrix`（`GetParameterMatrix()`，`:909-912`）记录列交换，`Invert` 用它把逆矩阵的行换回原顺序（`:826-840`）。
  - 数值：Givens 公式在 $|a|,|b|$ 相差悬殊时仍稳定（除以 $\sqrt{1+\tau^2}$ 归一化），无溢出风险；QR 是 $A^{\mathsf T}A$ 正规方程的高条件数替代（不平方条件数），但本实现仅被 `LUFactorization::SolveSystem` 的超定/欠定分支使用（`LUFactorization.cpp:431`、`:483`）。

### QR 求逆与 QR 更新

- **公式**：$A^{-1}=R^{-1}Q^{\mathsf T}$（`QRFactorization.cpp:752-841`，$R^{-1}$ 逐列回代 `:778-795`，$Q^{\mathsf T}$ 转置拷贝 `:797-806`）。
- **公式**（增删行列，Golub–Van Loan §12.5）：删列 12.5.2（`:365-440`）：删列后对新引入的次对角元逐对 Givens 消零并同步 $Q$；删行 12.5.3（`:444-519`）：先用 Givens 把被删行在 $Q$ 中的行向量旋转到只剩末元，再裁掉；加列/加行（`:550-737`）为反向操作，新元素经 $Q^{\mathsf T}$ 投影进 $R$ 再旋转。
- **代码位置**：`src/gmatutil/util/matrixoperations/QRFactorization.cpp:752-841`（Invert）、`:365-528`（RemoveFromQR）、`:550-737`（AddToQR）。
- **深度讲解**：增删更新允许 $O(n^2)$ 维护 QR，而非每次 $O(n^3)$ 重分解——设计目标是估计器的序贯信息矩阵维护，但当前仓库未见直接调用点（预留能力）。`RemoveFromQR` 的 `Q1` 行拷贝存在下标边界隐患（`:509-516` 中 `j < 0` 恒假分支），使用时以测试用例为准。

## 6.8 SchurFactorization：QR 迭代与 GTDS 分块求逆

### Schur 分解 Factor()（QR 迭代）

- **公式**：迭代 $A_{k}\to Q_k R_k$（QR 分解），$A_{k+1}=R_k Q_k$，$Q=\prod_k Q_k$；收敛后 $A_\infty=U$ 上三角，$Q^{\mathsf T}AQ=U$（`SchurFactorization.cpp:115-176`）。
- **代码位置**：`src/gmatutil/util/matrixoperations/SchurFactorization.cpp:115-176`；收敛容差 `tol = 1e-6`（`:135`）。
- **深度讲解**：这是无位移（no-shift）QR 算法的朴素实现：每次迭代对当前 $A$ 做一次完整 QR 分解再乘回去（`:143-145`、`:149-154`），收敛判据为 $\max|\Delta A|$ 与 $\max|\Delta Q|$ 均小于 $10^{-6}$（`:160-169`）。无位移 QR 对特征值比接近 1 的矩阵收敛很慢（线性收敛），且不处理复特征值（实 Schur 形要求 $2\times2$ 块），故该 `Factor` 仅作为教学/验证用途；实际求逆走下面的 GTDS 移植路径。

### Schur 求逆 Invert()（GTDS 移植，分块增广法）

- **公式**：把 $n\times n$ 矩阵按左上 $(n-1)\times(n-1)$ 分块递归增广：已知 $A_{n-1}^{-1}$，则
  $$A_n=\begin{bmatrix}A_{n-1} & \mathbf b\\ \mathbf c^{\mathsf T} & d\end{bmatrix},\quad
  \delta = A_{n-1}^{-1}\mathbf b,\quad
  A_n^{-1}=\begin{bmatrix}A_{n-1}^{-1}+\dfrac{\delta\delta^{\mathsf T}}{w} & -\dfrac{\delta}{w}\\ -\dfrac{\delta^{\mathsf T}}{w} & \dfrac{1}{w}\end{bmatrix},\ w=d-\mathbf c^{\mathsf T}\delta$$
  其中 $w=d-\mathbf c^{\mathsf T}\boldsymbol\delta$ 为对角修正后的 Schur 补（`SchurFactorization.cpp:235-313`：先算 delta 工作数组 `:241-267`，再算 $W$（Schur 补）`:273-277`，$Y$（$-\delta/w$）`:291-297`，$X$（修正 $A_{n-1}^{-1}$）`:299-311`）。
- **代码位置**：`src/gmatutil/util/matrixoperations/SchurFactorization.cpp:192-343`（Rmatrix 版）、`:359-477`（裸数组版）；辅助 `RemoveRowCol`（`:501-595`，未启用）与 `RestoreAllRowCols`（`:618-708`，未启用）处理压缩数组的行列删除/恢复。
- **深度讲解**：
  - 输入被压成上三角数组 `sum1`（`:195-205`），**仅使用上三角**——即该方法约定输入为对称矩阵（求逆结果自动对称镜像，`:329-340`）；非对称输入会被静默截断，与批估计"信息矩阵对称"的前提一致。
  - 与 Cholesky 不同，Schur 分块法允许主对角元素为 0 的情况（`sum1[0]==0` 才抛异常，`:320-327`），对**病态但不奇异**的矩阵更宽容——这正是 `BatchEstimator` 注释所言"Schur 能逆病态矩阵而 Cholesky 会抛异常"（`BatchEstimator.cpp:1738-1739`）。
  - 递归从 1×1 开始（`sum1[0]=1/sum1[0]`，`:227`），每步 $O(n^2)$，总 $O(n^3)$；无选主元，对角小元素会放大误差。
  - 消费方：批估计 `InversionType = "Schur"`（`BatchEstimator.cpp:1736-1757`），求逆前先用 Cholesky 做可逆性探针（见 6.12）。

## 6.9 差分雅可比：Jacobian 与 NumericJacobian

### Jacobian 类（求解器用，前向/中心/后向差分）

- **公式**（三种模式，`Jacobian.cpp:231-279`）：
  - 前向差分：$J_{ji}=\dfrac{f_j(\mathbf x+\delta_i\mathbf e_i)-f_j(\mathbf x)}{\delta_i}$（`:233-235`）
  - 中心差分：$J_{ji}=\dfrac{f_j(\mathbf x+\delta_i\mathbf e_i)-f_j(\mathbf x-\delta_i\mathbf e_i)}{2\delta_i}$（`:246-249`）
  - 后向差分：$J_{ji}=\dfrac{f_j(\mathbf x)-f_j(\mathbf x-\delta_i\mathbf e_i)}{\delta_i}$（`:261-264`）
  其中 $i$ 遍历变量（扰动 $pert[i]=\delta_i$）、$j$ 遍历分量。
- **代码位置**：注意 `src/gmatutil/util/` 下没有 Jacobian 实现——本类位于 `src/base/solver/Jacobian.cpp:215-303`（Calculate）、`:130-151`（Initialize）；模式枚举 `src/base/solver/DerivativeModel.hpp:44-49`。
- **深度讲解**：
  - 数据流：`Achieved`（`:173-190`）接收名义运行（`pertNumber == -1`，存 `nominal`）与扰动运行（存 `plusPertEffect`/`minusPertEffect`，由基类 `DerivativeModel::Achieved` 按 `plusEffect` 分拣，`DerivativeModel.hpp:75-79`）；`Calculate` 一次性按行主序组装 `jacobian`（`jac = [df0/dv0 df0/dv1 ... df1/dv0 ...]`，`:201-207` 注释）。
  - 数值：扰动 $\delta_i=0$ 抛异常（`:219-221`）；中心差分误差 $O(\delta^2)$、前/后向 $O(\delta)$，但中心差分需 2n 次函数求值（n 为变量数），求解器默认前向（`DifferentialCorrector` 配置见 [MD-11-solvers.md](MD-11-solvers.md)）。
  - 截断 vs 舍入：$\delta$ 过小使 $(f(x+\delta)-f(x))$ 淹没在舍入误差中，过大则截断误差主导；Jacobian 类不自动选步长（步长由调用方配置），`NumericJacobian` 则专门解决该问题。
  - 消费方：`DifferentialCorrector`（打靶求解器，`jac.Pseudoinverse()` 校正步）、`TargetRunner` 等；相关求解器算法见 [MD-11-solvers.md](MD-11-solvers.md)。

### NumericJacobian 类（MATLAB numjac 移植，自适应步长）

- **公式**：
  - 扰动步长：$\delta_i=\mathrm{fac}_i\cdot yscale_i$，其中 $yscale_i=\max(|y_i|,\mathrm{thresh}_i,\mathrm{typicalY}_i)$（`NumericJacobian.cpp:428-446`），$\mathrm{fac}_i$ 初值 $\sqrt{\varepsilon_{\mathrm{mach}}}$（`:404`），上下限 $\mathrm{facmin}=\varepsilon^{0.78}$、$\mathrm{facmax}=0.1$（`:57-58`）
  - 雅可比：$\dfrac{\partial F_i}{\partial y_j}\approx\dfrac{F_i(\mathbf y+\delta_j\mathbf e_j)-F_i(\mathbf y)}{\delta_j}$，矩阵形式 $\mathbf J=(\mathbf F_{del}-\mathbf F_{ty})\,\mathrm{diag}(1/\boldsymbol\delta)$（`:545-553`）
  - 细化判据：列最大差分 $\mathrm{diffMax}_j\le \mathrm{br}\cdot Fscale_j$（$\mathrm{br}=\varepsilon^{0.875}$）时认为该列可能是纯舍入，用 $\delta'_j=\sqrt{\mathrm{fac}_j}\,yscale_j$ 重算（`:640-647`、`:659-684`）；重算后按 $\mathrm{diffMax}$ 相对 $bl\cdot Fscale$（$bl=\varepsilon^{0.75}$）/ $bu\cdot Fscale$（$bu=\varepsilon^{0.25}$）的落点放大/缩小 $\mathrm{fac}_j$（`:760-779`）
- **代码位置**：`src/gmatutil/util/NumericJacobian.cpp:394-510`（CalculatePerturbations）、`:537-614`（CalculateJacobian）、`:624-648`（PrepareForRefinement）、`:659-684`（CalcRefinement）、`:694-782`（RefineJacColumn）；状态机 `AdvanceState`（`:148-221`）。
- **深度讲解**：
  - 这是 MATLAB `numjac` 的逐行移植（注释 `:29-31`）：把整个差分过程建模为**状态机**（INITIALIZING→PERTURBING→CALCULATING→REFINING→FINISHED），外部积分器每步推进一次状态、喂回新的函数值（`SetDerivs`，`:303-322`），适合嵌入微分方程数值求解（与 ODE 求解器配合复用函数求值）。
  - 步长自适应逻辑是核心价值：前一调用学到的 $\mathrm{fac}$ 作为工作存储传入（`GetWorkingStorage`/`SetInitialValues` 的 `inputfac`，`:254-276`、`:348-351`），对"敏感/不敏感"列分别维持合适的相对扰动。
  - `del` 符号处理（`:473-487`）：$nF==ny$ 时按 $F(y)$ 的符号保持扰动"指向函数增大一侧"，避免差分步穿过符号翻转点。
  - 消费方：目前 gmatutil 内无生产调用（预留），其设计目标场景是 CSALT/ODE 右端项雅可比；生产路径的稀疏雅可比由 CSALT `SparseMatrixUtil` + NLP 求解器承担（见 6.10）。

## 6.10 CSALT 稀疏矩阵工具：SparseMatrixUtil

### RSMatrix 类型与存储模型

- **公式**：`typedef boost::numeric::ublas::compressed_matrix<Real> RSMatrix`（`SparseMatrixUtil.hpp:55-59`）——按行压缩的稀疏矩阵（CSR 变体），仅存非零元（含显式 0）。
- **代码位置**：`src/csalt/src/util/SparseMatrixUtil.hpp:55-59`；类为静态工具、构造私有（`:70-72`、`:256-262`）。
- **深度讲解**：CSALT 的 NLP 雅可比/海森矩阵维度可达数万（配点离散后），稀疏存储是 SNOPT 接口的硬性要求（`iGfun/jGvar` 三向量形式）；`SparseMatrixUtil` 是**唯一**的稀疏入口，稠密 `Rmatrix` 只在转换时出现。设计约定（头文件 `:85-88` 注释）：先 `SetSparsityPattern` 固定非零结构、再填值，避免反复 rehash——配点法的稀疏模式在网格细化间不变量化时保持不变。更多装配链见 [../CH15-csalt-interop-tests.md](../CH15-csalt-interop-tests.md) §2.1.2。

### SetElement / SetSize / SetSparsityPattern / SetSparseMatrix

- **公式**：`spMat(row, col) = value`（`SparseMatrixUtil.cpp:49-53`）；`spMat.resize(rows, cols, false)`（`:66-70`）；按 (rowIdx, colIdx) 列表把模式填 0 或 1（`:140-146`）；按 (rowIdx, colIdx, value) 三向量整体填充（`:219-222`）。
- **代码位置**：`src/csalt/src/util/SparseMatrixUtil.cpp:49-53`、`:66-70`、`:93-147`、`:167-223`、`:244-301`。
- **深度讲解**：所有填值函数先做三项校验：非零元数不超过 $rows\cdot cols$（`:104-110`）、三向量等长（`:111-118`）、索引不越界（`:131-138`），越界抛 `LowThrustException`。`SetSparsityPattern(..., hasZeros=false)` 填 1 是为了"预分配"非零槽位；`SetSparseMatrix` 的 Rvector 重载（`:244-301`）与 `std::vector<Real>` 重载逻辑相同，只是取值来源不同。

### SetSparseBLockMatrix（相位块拼装）

- **公式**：$spMat(rowOffSet+i,\ colOffSet+j)\ {=}\ \text{或}\ {+=}\ v_{ij}$，其中 $(i,j)$ 为块内非零坐标（`SparseMatrixUtil.cpp:396-404`、`:470-484`、`:581-589`、`:666-682`）。
- **代码位置**：`src/csalt/src/util/SparseMatrixUtil.cpp:342-405`（三向量版）、`:443-485`（稀疏块版，迭代器遍历）、`:526-590`（Rvector 版）、`:630-686`（稠密 Rmatrix 版）。
- **深度讲解**：这是把各相位（Phase）的 Jacobian 子块拼进总稀疏矩阵的装配原语。`isNotAdding=false` 时做 `+=`（叠加），用于"雅可比矩阵可分解为多来源贡献"的场合；`isNotAdding=true` 时直接赋值但**不清除既有非零元**（头文件 `:328-339` 的例示注释）。稠密版逐元素跳过 0（`:671`），避免把稠密块的零写进稀疏结构造成存储膨胀。消费方：`Phase::ComputeSparsityPattern`/`NLPFuncUtil_*` 组装 NLP 约束雅可比（见 CH15）。

### GetSparsityPattern / GetThreeVectorForm / GetNumNonZeroElements

- **公式**：导出非零元三元组 $(i_1,i_2,v)$（行主序遍历，`SparseMatrixUtil.cpp:859-871`、`:991-1003`）；带子块边界的版本（`:900-951`、`:1033-1092`）；非零元计数（`:1106-1121`）；$\sum|v|$（`GetAbsTotalSum`，`:1136-1150`）。
- **代码位置**：`src/csalt/src/util/SparseMatrixUtil.cpp:757-775`、`:794-820`、`:842-872`、`:900-951`、`:974-1004`、`:1033-1092`、`:1106-1121`、`:1136-1150`。
- **深度讲解**：`GetThreeVectorForm` 的输出正是 SNOPT `iGfun/jGvar/A` 所需的 row/col/value 三向量接口格式（`SnoptOptimizer`/`SNOPTFunctionWrapper` 消费，见 CH15 §2.1.1）；`GetSparsityPattern` 返回 0/1 模式矩阵供 IPOPT 的 `TNLP::get_jacobian_structure` 使用。所有遍历都用 uBLAS 双层迭代器（`begin1()/begin2()`），不推荐外部直接用迭代器（头文件 `:61-68` 注释）。

### fast_prod（稀疏×稠密乘积）

- **公式**：$result_i\mathrel{+}=\sum_{j:\,a_{ij}\ne 0} a_{ij}v_j$，仅遍历非零元（`SparseMatrixUtil.cpp:1203-1211`、`:1265-1274`）；矩阵版委托 `boost::numeric::ublas::axpy_prod`（`:1317`）。
- **代码位置**：`src/csalt/src/util/SparseMatrixUtil.cpp:1168-1212`（std::vector 版）、`:1231-1275`（Rvector 版）、`:1294-1318`（稀疏×稀疏版）。
- **深度讲解**：`initialize=true` 时先清空/置零结果再累加（`result = A v`），`initialize=false` 时做 `result += A v`（累积多块贡献）；维度不匹配抛 `LowThrustException`（`:1192-1202`、`:1256-1264`）。复杂度 $O(\mathrm{nnz}(A))$ 而非 $O(mn)$，是 NLP 求值内循环（约束值 + 雅可比×方向向量）的性能关键。

### ReplicateSparseMatrix / IsZeroMatrix / RSMatrixToRmatrix / CopySparseMatrix

- **公式**：块重复 $M(i_r + k\cdot r,\ j_c + l\cdot c)=B(i_r,j_c)$（`SparseMatrixUtil.cpp:1395-1413`）；零矩阵判定（`:1430-1446`）；稠密转换 $R(i,j)=S(i,j)$（`:1502-1519`，含子块版 `:1465-1489`）；拷贝（`:1532-1576`）。
- **代码位置**：`src/csalt/src/util/SparseMatrixUtil.cpp:1380-1415`、`:1430-1446`、`:1465-1489`、`:1502-1519`、`:1532-1547`、`:1560-1576`。
- **深度讲解**：`ReplicateSparseMatrix` 用于从单段配点模式构造多段模式（按行重复，注释 `:1375-1378` 说明 CSR 行主序下必须逐行插入否则极慢）；`RSMatrixToRmatrix` 把稀疏块转稠密供数值验证/调试比对（跨库互操作测试见 CH15 §3）。

## 6.11 参数系统中的矩阵/向量参数类

### Rmat33Var / Rmat66Var：矩阵型 Parameter

- **公式**：无数值公式——参数容器语义：`mReturnType = Gmat::RMATRIX_TYPE`（`Rmat33Var.cpp:70`、`Rmat66Var.cpp:70`），承载 `mRmat33Value`/`mRmat66Value`，`EvaluateRmatrix()` 对 `SYSTEM_PARAM` 要求派生类实现、用户参数直接返回缓存值（`Rmat33Var.cpp:191-203`）。
- **代码位置**：`src/base/parameter/Rmat33Var.cpp:62-71`、`:168-172`、`:177-181`、`:191-203`；`src/base/parameter/Rmat66Var.cpp:62-71`、`:168-172`、`:177-181`、`:191-203`。
- **深度讲解**：这两类是"Rmatrix 作为 Parameter 值"的基类：`GetRmatrix`/`SetRmatrix`/`EvaluateRmatrix` 构成取值-赋值-求值三接口，`SetRmatrix` 不做尺寸校验（注释 `@todo check the size`，`Rmat33Var.cpp:179`）。派生类 `OrbitRmat33`/`OrbitRmat66`（轨道）与 `AttitudeRmat33`（姿态）实现 `EvaluateRmatrix`（如 `OrbitRmat33.cpp:91-94` 返回缓存的 `mRmat33Value`），把本体的姿态/轨道量物化为矩阵参数供 Report/GUI 使用。

### Rvec3Var / Rvec6Var / RvectorVar：向量型 Parameter

- **公式**：`mReturnType = Gmat::RVECTOR_TYPE`（`Rvec3Var.cpp:69`、`Rvec6Var.cpp:69`、`RvectorVar.cpp:86`），承载 `Rvector3`/`Rvector6`/`Rvector`，接口 `GetRvector3/SetRvector3/EvaluateRvector3` 等（`Rvec3Var.cpp:167-203`、`Rvec6Var.cpp:167-203`、`RvectorVar.cpp:186-221`）。
- **代码位置**：`src/base/parameter/Rvec3Var.cpp:69`、`:167-175`、`:188-192`；`Rvec6Var.cpp:69`、`:167-175`、`:188-192`；`RvectorVar.cpp:86`、`:186-194`、`:217-221`。
- **深度讲解**：向量参数把 `Rvector` 家族的定长/变长类型统一挂进 `Parameter` 体系，与 `Array` 参数（矩阵脚本对象，见 CH03）区分：`Array` 是脚本可见的矩阵对象，`Rmat33Var` 族是系统内部参数。消费方：`OrbitRvec6`（轨道状态 6 向量）、`AttitudeRvector` 等派生类，以及 `Report`/`Assignment` 命令的取值通道。

## 6.12 消费链总结：谁在吃这些矩阵算法

| 算法 | 主要消费者（代码证据） |
|---|---|
| `Rmatrix::Inverse`（全选主元 Gauss-Jordan） | 批估计 `InversionType="Internal"`（`BatchEstimator.cpp:1770`）；STM 相关逆（`GPSPointMeasureModel.cpp:1162`、`AngleAdapterDeg.cpp:1926-1927`、`Estimator.cpp:5163`）；脚本 `Inverse` 节点（`src/base/math/Inverse.cpp`）；`Rmatrix::operator/`、`Rvector::operator/(Rmatrix)` |
| `Rmatrix::Pseudoinverse` | 微分校正器 `jac.Pseudoinverse()`（`DifferentialCorrector.cpp:1599`） |
| LU 分解/行列式/求解 | `Rmatrix::Determinant`（>9 阶）、`QRFactorization::Determinant` 委托；`SolveSystem` 被分解器相关工具调用 |
| Cholesky 分解/求逆 | 批估计 `InversionType="Cholesky"`（`BatchEstimator.cpp:1758-1765`）及 Schur 路径前的可逆性探针（`:1742-1749`）；EKF 协方差平方根形式 |
| QR 分解（Givens） | `LUFactorization::SolveSystem` 超定/欠定分支（`LUFactorization.cpp:431/483`） |
| Schur 分块求逆 | 批估计 `InversionType="Schur"`（`BatchEstimator.cpp:1736-1757`） |
| `CompressNormalMatrix`/`ExpandNormalMatrixInverse` | 批估计信息矩阵零行/列压缩（`BatchEstimator.cpp:1684-1685`，`tol=1e-50`） |
| `Jacobian` 三模式差分 | `DifferentialCorrector` 等求解器的有限差分雅可比（`Jacobian.cpp:215-303`） |
| `SparseMatrixUtil` | CSALT NLP 雅可比/海森矩阵的稀疏装配与 SNOPT/IPOPT 接口（见 CH15） |
| `Rmatrix33`/`Rvector3` | 姿态 DCM 合成、坐标系旋转、引力/加速度计算内循环（6.3） |
| `Rmatrix66`/`Rvector6` | STM 传播、状态协方差 6×6 块运算（6.3） |

批估计正规方程路径（信息矩阵 $N=A^{\mathsf T}WA$ 求逆得协方差 $P=N^{-1}$，零行/列压缩后按 `InversionType` 分派）与估计滤波公式详见 [MD-12-estimation-measurements.md](MD-12-estimation-measurements.md)；求解器牛顿步 $(\mathbf J^{\mathsf T}\mathbf J)^{-1}\mathbf J^{\mathsf T}\mathbf r$ 的伪逆用法见 [MD-11-solvers.md](MD-11-solvers.md)。

## 6.13 公式索引表

| 公式 | 文件:行 | 所属类 |
|---|---|---|
| $\mathbf C=\mathbf A\mathbf B,\ c_{ij}=\sum_k a_{ik}b_{kj}$ | src/gmatutil/util/Rmatrix.cpp:486-497 | Rmatrix |
| $\mathbf y=\mathbf A\mathbf v,\ y_i=\sum_j a_{ij}v_j$ | src/gmatutil/util/Rmatrix.cpp:818-827 | Rmatrix |
| $\mathbf T=\mathbf A^{\mathsf T},\ t_{ji}=a_{ij}$ | src/gmatutil/util/Rmatrix.cpp:1072-1091 | Rmatrix |
| $\det A$（1/2/3 阶显式、拉普拉斯展开、LU） | src/gmatutil/util/Rmatrix.cpp:937-1011 | Rmatrix |
| $C_{ij}=(-1)^{i+j}\det M_{ij}$ | src/gmatutil/util/Rmatrix.cpp:1017-1066 | Rmatrix |
| $A^{-1}$：全选主元 Gauss-Jordan | src/gmatutil/util/Rmatrix.cpp:1097-1228 | Rmatrix |
| $A^{-1}=\mathrm{diag}(1/a_{ii})$（对角快速路径） | src/gmatutil/util/Rmatrix.cpp:1125-1141 | Rmatrix |
| $A^+=A^{\mathsf T}(AA^{\mathsf T})^{-1}$ / $(A^{\mathsf T}A)^{-1}A^{\mathsf T}$ | src/gmatutil/util/Rmatrix.cpp:1439-1450 | Rmatrix |
| 对称矩阵伪逆 7 步（置换+分块） | src/gmatutil/util/Rmatrix.cpp:1247-1419 | Rmatrix |
| $\mathrm{Sym}=\tfrac12(A+A^{\mathsf T})$、$\mathrm{AntiSym}=\tfrac12(A-A^{\mathsf T})$ | src/gmatutil/util/Rmatrix.cpp:1464-1492 | Rmatrix |
| $\mathrm{tr}A=\sum_i a_{ii}$ | src/gmatutil/util/Rmatrix.cpp:913-931 | Rmatrix |
| 正交/标准正交列判据 | src/gmatutil/util/Rmatrix.cpp:141-232 | Rmatrix |
| $A^{\mathsf T}B$、$AB^{\mathsf T}$、$A^{\mathsf T}B^{\mathsf T}$ | src/gmatutil/util/Rmatrix.cpp:1529-1618 | 友元函数 |
| $A^{-1}=\mathrm{adj}(A)/\det A$（3×3 显式） | src/gmatutil/util/Rmatrix33.cpp:460-483 | Rmatrix33 |
| $\det A$（Sarrus） | src/gmatutil/util/Rmatrix33.cpp:437-444 | Rmatrix33 |
| $A^{-1}$ 委托 Rmatrix::Inverse | src/gmatutil/util/Rmatrix66.cpp:525-528 | Rmatrix66 |
| 上三角压缩索引 $iN-i(i+1)/2+j$ | src/gmatutil/util/matrixoperations/MatrixFactorization.cpp:312-324 | MatrixFactorization |
| 信息矩阵零行/列压缩/扩张 | src/gmatutil/util/matrixoperations/MatrixFactorization.cpp:118-212, 236-289 | MatrixFactorization |
| $A=LU$：选主元、归一化、更新 | src/gmatutil/util/matrixoperations/LUFactorization.cpp:154-202 | LUFactorization |
| $A^{-1}$：前代+回代逐列 | src/gmatutil/util/matrixoperations/LUFactorization.cpp:293-344 | LUFactorization |
| $\det A=(-1)^n\prod u_{ii}$ | src/gmatutil/util/matrixoperations/LUFactorization.cpp:543-555 | LUFactorization |
| $A=R^{\mathsf T}R$：sqrt 主元、正定守卫 | src/gmatutil/util/matrixoperations/CholeskyFactorization.cpp:164-206 | CholeskyFactorization |
| $A^{-1}=R^{-1}R^{-{\mathsf T}}$ | src/gmatutil/util/matrixoperations/CholeskyFactorization.cpp:252-298 | CholeskyFactorization |
| Givens $c,s$（5.1.10） | src/gmatutil/util/matrixoperations/QRFactorization.cpp:855-878 | QRFactorization |
| $A=QR$ 旋转消零 + 列选主元 + 符号规范化 | src/gmatutil/util/matrixoperations/QRFactorization.cpp:244-303 | QRFactorization |
| $A^{-1}=R^{-1}Q^{\mathsf T}$ | src/gmatutil/util/matrixoperations/QRFactorization.cpp:752-841 | QRFactorization |
| QR 增删行列（§12.5） | src/gmatutil/util/matrixoperations/QRFactorization.cpp:365-737 | QRFactorization |
| Schur 迭代 $A_{k+1}=R_kQ_k$ | src/gmatutil/util/matrixoperations/SchurFactorization.cpp:143-173 | SchurFactorization |
| Schur 分块增广求逆（GTDS） | src/gmatutil/util/matrixoperations/SchurFactorization.cpp:235-313 | SchurFactorization |
| 前向差分 $J_{ji}=(f^+-f^0)/\delta_i$ | src/base/solver/Jacobian.cpp:233-235 | Jacobian |
| 中心差分 $J_{ji}=(f^+-f^-)/(2\delta_i)$ | src/base/solver/Jacobian.cpp:246-249 | Jacobian |
| 后向差分 $J_{ji}=(f^0-f^-)/\delta_i$ | src/base/solver/Jacobian.cpp:261-264 | Jacobian |
| $\delta_i=\mathrm{fac}_i\cdot yscale_i$（numjac 步长） | src/gmatutil/util/NumericJacobian.cpp:428-446 | NumericJacobian |
| $\mathbf J=(\mathbf F_{del}-\mathbf F_{ty})\,\mathrm{diag}(1/\boldsymbol\delta)$ | src/gmatutil/util/NumericJacobian.cpp:545-553 | NumericJacobian |
| 步长细化/自适应（br/bl/bu） | src/gmatutil/util/NumericJacobian.cpp:640-647, 760-779 | NumericJacobian |
| $spMat(r,c)=v$ 稀疏赋值 | src/csalt/src/util/SparseMatrixUtil.cpp:49-53 | SparseMatrixUtil |
| 稀疏模式填充（0/1） | src/csalt/src/util/SparseMatrixUtil.cpp:93-147 | SparseMatrixUtil |
| 稀疏块拼装（= 或 +=） | src/csalt/src/util/SparseMatrixUtil.cpp:342-686 | SparseMatrixUtil |
| 三向量导出（row,col,value） | src/csalt/src/util/SparseMatrixUtil.cpp:842-1092 | SparseMatrixUtil |
| $result\mathrel{+}=Av$（仅非零元） | src/csalt/src/util/SparseMatrixUtil.cpp:1168-1318 | SparseMatrixUtil |
| 稀疏块行/列重复复制 | src/csalt/src/util/SparseMatrixUtil.cpp:1380-1415 | SparseMatrixUtil |
| 稀疏→稠密转换 | src/csalt/src/util/SparseMatrixUtil.cpp:1465-1519 | SparseMatrixUtil |
| 参数容器：RMATRIX_TYPE/RVECTOR_TYPE 返回类型 | src/base/parameter/Rmat33Var.cpp:70、Rvec3Var.cpp:69 等 | Rmat33Var/Rvec3Var 族 |
