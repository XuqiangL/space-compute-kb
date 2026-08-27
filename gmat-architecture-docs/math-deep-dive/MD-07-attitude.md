# 第7章 姿态表示与运动学数学

本章范围：`src/base/attitude/`（22 个文件：11 .cpp + 11 .hpp）、`src/gmatutil/util/` 下的姿态换算工具（`AttitudeConversionUtility.*`、`AttitudeUtil.*`，4 个文件）、`src/base/parameter/AttitudeRmat33.*`（2 个文件，及其数据基类 `AttitudeData`），共 28 个代码文件。与传播器的分工见 [第7章 传播器、推进剂机动、姿态与停止条件](../CH07-propagator.md)：本章只写姿态数学本身（表示换算、运动学方程、指向几何），不重复传播器/PSM 的内容。

本章的叙述主线是 GMAT 姿态子系统的三层结构：

1. **表示换算层**（`AttitudeConversionUtility`、`AttitudeUtil`）：纯静态函数，实现四元数/DCM/欧拉角/MRP/欧拉轴角 5 种表示之间的互转，以及角速度↔欧拉角率变换。所有公式都直接对应本文件中的矩阵字面量，可逐元素核对。
2. **姿态基类层**（`Attitude` → `Kinematic`）：定义"姿态状态仓库"——内部只保存 DCM `dcm` 与角速度 `angVel` 两份"权威表示"，其余表示（四元数、欧拉角、MRP、欧拉角率）由 `UpdateState()` 按需换算；定义纯虚接口 `ComputeCosineMatrixAndAngularVelocity(atTime)`，由叶子类实现"某时刻的姿态从哪来"。
3. **叶子模型层**：`Spinner`（欧拉轴/角自旋）、`PrecessingSpinner`（3-1-3 进动自旋）、`ThreeAxisKinematic`（四元数运动学解析积分）、`CSFixed`（坐标系固定）、`NadirPointing`/`CommandableNadirPointing`（对地指向，TRIAD）、`CCSDSAttitude`（CCSDS-AEM 星历姿态）、`SpiceAttitude`（SPICE CK 内核姿态）。

符号约定（与代码一致，全文统一）：

- `dcm` = $R_{BI}$，即从惯性系 I 到本体系 B 的旋转矩阵（GMAT 内部权威姿态表示，`Attitude.cpp` L36-41 注释）。
- 四元数按 CCSDS 惯例存为 $(q_1,q_2,q_3,q_4)$，$q_4$ 为标量部分（`AttitudeConversionUtility.cpp` L649-651 注释）。
- 角度参数对外（脚本/GUI）用度，内部一律弧度（`Attitude.hpp` L36-38 注释）；本文章内公式全部用弧度。
- 欧拉角旋转序列为"主动旋转次序"，旋转矩阵按行主序填充（先填第 0 行）。

---

## 一、目录树

```
src/base/attitude/                     (22 文件)
├── Attitude.hpp / .cpp                姿态抽象基类：表示仓库、初始化、换算入口
├── AttitudeException.hpp / .cpp       姿态异常
├── Kinematic.hpp / .cpp               运动学姿态中间基类（Attitude 直系子类）
├── CSFixed.hpp / .cpp                 坐标系固定姿态（CoordinateSystemFixed）
├── Spinner.hpp / .cpp                 自旋姿态（欧拉轴/角，常角速度）
├── PrecessingSpinner.hpp / .cpp       进动自旋姿态（3-1-3 欧拉角）
├── NadirPointing.hpp / .cpp           对地指向姿态（TRIAD + LVLH）
├── CommandableNadirPointing.hpp/.cpp  命令模式可设的对地指向（GOES 需求）
├── ThreeAxisKinematic.hpp / .cpp      三轴运动学（四元数解析传播）
├── CCSDSAttitude.hpp / .cpp           CCSDS-AEM 星历姿态（读 AEM 文件）
└── SpiceAttitude.hpp / .cpp           SPICE CK 内核姿态（编译期开关 __USE_SPICE__）

src/gmatutil/util/                     (4 文件)
├── AttitudeConversionUtility.hpp/.cpp 静态换算工具（5 种表示互转）
└── AttitudeUtil.hpp / .cpp            GSS 移植工具（GmatAttUtil / FloatAttUtil 两套命名空间）

src/base/parameter/                    (2 文件)
├── AttitudeRmat33.hpp / .cpp          航天器姿态 DCM 系统参数（Rmat33Var + AttitudeData）
└── AttitudeData.hpp（引用，姿态数据基类，提供 GetRmatrix33）
```

---

## 二、表示换算层：`AttitudeConversionUtility`

静态类，不可实例化（`AttitudeConversionUtility.hpp` L89-92 私有构造）。所有换算函数既是姿态基类的内部工具，也被叶子模型（Spinner、PrecessingSpinner、ThreeAxisKinematic、CCSDSAttitude）直接调用。这是本章公式密度最高的文件。

### 条目 2.1 四元数 → DCM

- **公式**：设 $\mathbf q=(q_1,q_2,q_3)^\top$、标量 $q_4$，$[\mathbf q]_\times$ 为叉乘反对称矩阵，$c=\left(q_1^2+q_2^2+q_3^2+q_4^2\right)^{-1}$，则
  $$R_{BI}=c\left[\left(q_4^2-\mathbf q^\top\mathbf q\right)I_3+2\mathbf q\mathbf q^\top-2q_4[\mathbf q]_\times\right]$$
- **代码位置**：`src/gmatutil/util/AttitudeConversionUtility.cpp` L73-102（核心语句 L95-101）。
- **深度讲解**：
  - **几何意义**：四元数 $q=\cos(\theta/2)+\hat e\sin(\theta/2)$ 等价于绕单位轴 $\hat e$ 转 $\theta$；上式即把该"轴-角"信息展开成方向余弦矩阵。$c$ 因子使公式对未归一化四元数仍成立（代码在 L85-91 先检查模长 $\ge 1e-10$，但不强制归一化）。
  - **实现细节**（`AttitudeConversionUtility.cpp` L93-101）：
    ```cpp
    Rmatrix33 I3;  // 单位阵
    Rvector3  q1_3(quat1(0), quat1(1), quat1(2));   // 取矢量部分 q1,q2,q3
    Rmatrix33 q_x(     0.0, -q1_3(2),  q1_3(1),    // 构造 [q]× 反对称矩阵
                 q1_3(2),      0.0, -q1_3(0),
                -q1_3(1),  q1_3(0),     0.0);
    Real c = 1.0 / ((quat1(0)*quat1(0)) + (quat1(1)*quat1(1)) +  // 归一化因子 1/|q|²
                    (quat1(2)*quat1(2)) + (quat1(3)*quat1(3)));
    return Rmatrix33(c * ( (((quat1(3)*quat1(3)) - (q1_3*q1_3)) * I3)   // (q4²-q·q)I
          + (2.0 * Outerproduct(q1_3,q1_3)) - (2.0 * quat1(3) * q_x))); // +2qqᵀ-2q4[q]×
    ```
    逐行：① 取四元数矢量部分；② 由矢量部分构造反对称矩阵 `q_x`；③ 计算 $c=1/|\mathbf q|^2$；④ 按公式拼出三项：标量-内积项、外积项、反对称项。
  - **归一化/奇点**：无奇点（$|\mathbf q|=0$ 已在 L85-91 被 `UtilityException` 拦截）。
  - **接口**：`Attitude::Initialize()` 在四元数输入分支调用它（`Attitude.cpp` L689），`CommandableNadirPointing` 设置四元数命令时也调用（`CommandableNadirPointing.cpp` L550）。

### 条目 2.2 欧拉角+序列 → DCM（含 1-2-3、3-1-3、3-2-1 等 12 个序列）

- **公式**：对序列 $(i,j,k)$，$R_{BI}=R_i(\theta_3)\,R_j(\theta_2)\,R_k(\theta_1)$（按代码行主序逐元素展开）。代表性序列（$s_i=\sin\theta_i, c_i=\cos\theta_i$）：
  - 1-2-3（`L151-154`）：$$R=\begin{pmatrix}c_3c_2 & c_3s_2s_1+s_3c_1 & -c_3s_2c_1+s_1s_3\\ -s_3c_2 & -s_3s_2s_1+c_3c_1 & s_3s_2c_1+c_3s_1\\ s_2 & -c_2s_1 & c_2c_1\end{pmatrix}$$
  - 3-1-3（`L216-219`）：$$R=\begin{pmatrix}c_3c_1-s_3c_2s_1 & c_3s_1+s_3c_2c_1 & s_3s_2\\ -s_3c_1-c_3c_2s_1 & -s_3s_1+c_3c_2c_1 & c_3s_2\\ s_2s_1 & -s_2c_1 & c_2\end{pmatrix}$$
  - 3-2-1（`L225-228`）：$$R=\begin{pmatrix}c_2c_1 & c_2s_1 & -s_2\\ -c_3s_1+s_3s_2c_1 & c_3c_1+s_3s_2s_1 & s_3c_2\\ s_3s_1+c_3s_2c_1 & -s_3c_1+c_3s_2s_1 & c_3c_2\end{pmatrix}$$
- **代码位置**：`src/gmatutil/util/AttitudeConversionUtility.cpp` L120-244（12 个序列分支 L141-237）；`Real*` 重载 L262-380 内容相同。
- **深度讲解**：
  - **几何意义**：三次"绕当前新轴旋转"的复合。对称序列（首尾同轴，如 313）描述"章动/进动"类运动；非对称序列（首尾异轴，如 123/321）即飞行器常用的"偏航-俯仰-滚转"（3-2-1）或轨道系指向。
  - **实现细节**：矩阵按行主序逐元素手写，非运行时矩阵连乘——这是刻意为之：避免 12 次三角调用×9 元素的冗余，且便于验证。`Rmatrix33` 构造函数参数顺序即行主序（先第 0 行三个元素）。
  - **奇点处理**：正向（角度→矩阵）无奇点；奇点只出现在反向（矩阵→角度）与角速度换算，见条目 2.5、2.7。
  - **接口**：`Attitude::Initialize()` 欧拉角输入分支（`Attitude.cpp` L703-706）、`SetRealParameter`/`SetRvectorParameter`（`Attitude.cpp` L2071-2074、L2729-2732）均调用；`GmatAttUtil::ToEulerAngles`（条目 5.2）是同一公式的另一种实现（通用代数式）。

### 条目 2.3 欧拉序列全集（12 种）

- **公式**：非对称 6 种 `123, 231, 312, 132, 321, 213`；对称 6 种 `121, 232, 313, 131, 323, 212`。
- **代码位置**：`src/base/attitude/Attitude.cpp` L234-248（`EULER_SEQ_LIST[12]`）；`src/gmatutil/util/AttitudeConversionUtility.cpp` L45-59（`VALID_EULER_SEQUENCES[12]`，内容一致）。
- **深度讲解**：
  - **几何意义**：三轴中任选三轴的排列共 $3^3=27$ 种，但连续两次绕同一轴无意义，排除后余 $3\cdot2\cdot2=12$ 种；其中首尾同轴 6 种为对称序列。GMAT 默认 `EulerAngleSequence = 321`（`Attitude.cpp` L367，注释说明由 312 改为 321）。
  - **实现细节**：`ValidateEulerSequence`（`Attitude.cpp` L3507-3521）在 12 个字符串中查表，不在表内即抛 `AttitudeException`；`ExtractEulerSequence`（`Attitude.cpp` L320-340）把字符串逐字符拆成 `UnsignedIntArray{seq1,seq2,seq3}`。
  - **奇点分类依据**：对称序列在中角 $\theta_2=0$ 奇异（$s_2=0$），非对称序列在 $\theta_2=\pm90°$ 奇异（$c_2=0$）——这条规则在欧拉角率换算（条目 2.7）、`ValidateEulerAngles`（`Attitude.cpp` L3461、L3477）中一致使用。

### 条目 2.4 DCM → 四元数（Shepperd 最大分量分支法）

- **公式**：$t=\mathrm{tr}(R)$，取 $v=(R_{11},R_{22},R_{33},t)$ 的最大分量决定主分支；例如最大为 $t$（$q_4$ 分支）时：
  $$q_4=\tfrac12\sqrt{1+t},\qquad (q_1,q_2,q_3)=\tfrac{1}{4q_4}\big(R_{23}-R_{32},\ R_{31}-R_{13},\ R_{12}-R_{21}\big)$$
  其余分支（$q_1,q_2,q_3$ 为主）同理，最后整体 `Normalize()`。
- **代码位置**：`src/gmatutil/util/AttitudeConversionUtility.cpp` L585-639（`v[4]` 与 `maxI` 判定 L599-608；四个分支 L609-636；归一化 L638）。
- **深度讲解**：
  - **数值意义**：$1+t$、$1+R_{11}-R_{22}-R_{33}$ 等四项在"旋转接近 $180°$"时各有其最小化情形；若固定用 $\sqrt{1+t}$ 分支，$R$ 接近 $-I$ 时 $q_4\to0$，其余分量除以 $q_4$ 会放大舍入误差。按最大分量选主元（Shepperd 算法）保证除法稳定。
  - **实现细节**（`L597-638`）：
    ```cpp
    Real matT = cosMat.Trace();                 // 迹 t
    Real v[4] = {R11, R22, R33, matT};          // 四个候选主元
    Integer maxI = 0;  Real maxNum = v[0];
    for (Integer i = 1; i < 4; i++)             // 找最大者
       if (v[i] > maxNum) { maxNum = v[i]; maxI = i; }
    if (maxI == 0) {                            // q1 分支
       q1 = 2.0 * v[0] + 1.0 - matT;            // = 1+R11-R22-R33
       q2 = R12 + R21;  q3 = R13 + R31;  q4 = R23 - R32;
    } ...
    return (Rvector(4,q1,q2,q3,q4)).Normalize(); // 最后统一归一化
    ```
  - **归一化**：分支求出的四元数模长天然为 $2\sqrt{\text{主元}}$ 量级，最后 `Normalize()` 一次到位；`Rvector::Normalize` 若遇零向量会保护。
  - **接口**：`Attitude::GetQuaternion`（`Attitude.cpp` L872）、`UpdateState("Quaternion")`（`L3614`）、`ThreeAxisKinematic`（`L209`）等所有"DCM→四元数"路径都走它。

### 条目 2.5 DCM → 欧拉角（12 分支，含奇点判断）

- **公式**：对 1-2-3：$\theta_1=\mathrm{atan2}(-R_{32},R_{33})$，$\theta_2=\mathrm{asin}(R_{31})$，$\theta_3=\mathrm{atan2}\big(R_{13}s_1+R_{12}c_1,\ R_{23}s_1+R_{22}c_1\big)$；
  对 3-1-3：$\theta_1=\mathrm{atan2}(R_{31},-R_{32})$，$\theta_2=\mathrm{acos}(R_{33})$，$\theta_3=\mathrm{atan2}\big(-R_{22}s_1-R_{21}c_1,\ R_{12}s_1+R_{11}c_1\big)$；
  对 3-2-1：$\theta_1=\mathrm{atan2}(R_{12},R_{11})$，$\theta_2=\mathrm{asin}(-R_{13})$，$\theta_3=\mathrm{atan2}\big(R_{31}s_1-R_{32}c_1,\ -R_{21}s_1+R_{22}c_1\big)$。
- **代码位置**：`src/gmatutil/util/AttitudeConversionUtility.cpp` L420-548（1-2-3 在 L437-445，3-2-1 在 L482-490，3-1-3 在 L527-535）；四元数重载 L398-402 先转 DCM 再调本函数。
- **深度讲解**：
  - **几何意义**：逆问题——已知复合旋转矩阵，反解三次转角的幅度。中角 $\theta_2$ 由 `asin`/`acos` 直接提取（主值），首末角用 `atan2` 保证象限正确。
  - **实现细节**：先读九个元素到局部变量 `R11..R33`（L427-435），再按序列分支硬编码三角组合；首末角的公式利用已解出的 $\theta_1$ 的 `sin1/cos1` 消去耦合项。
  - **奇点处理**：本函数**不做奇点检查**——`acos/asin` 在主值域内总有定义；若 $\theta_2$ 接近奇点，解出的首末角噪声大，由调用侧（`ValidateEulerAngles`、GUI 面板）用 `EULER_ANGLE_TOLERANCE = 1e-10`（`src/gmatutil/util/GmatConstants.hpp` L243）预先拒绝。
  - **接口**：`Attitude::GetEulerAngles`（`Attitude.cpp` L912-915）、`UpdateState("EulerAngles")`（`L3627`）、`SpiceAttitude::GetEulerAngles`（`SpiceAttitude.cpp` L372-375）。

### 条目 2.6 MRP ↔ 四元数（Dunn 添加）

- **公式**：设 MRP 向量 $\boldsymbol\sigma=(\sigma_1,\sigma_2,\sigma_3)$，$P=\boldsymbol\sigma^\top\boldsymbol\sigma$：
  - MRP→四元数：$q_i=\dfrac{2\sigma_i}{1+P}\ (i=1,2,3)$，$q_4=\dfrac{1-P}{1+P}$；
  - 四元数→MRP：$\sigma_i=\dfrac{q_i}{1+q_4}$。
- **代码位置**：MRP→四元数 `src/gmatutil/util/AttitudeConversionUtility.cpp` L657-677（公式 L671-674）；四元数→MRP L694-709（公式 L704-706）。
- **深度讲解**：
  - **几何意义**：MRP 是"修正罗德里格斯参数"，几何上等于把单位四元数从 3-球面 $S^3$ 经**球极投影**（以 $q_4=-1$ 为投影极点）映到 $\mathbb R^3$，因此**无约束**的三维向量即可表示姿态——比四元数少一个约束，便于做无约束优化。代价是 $q_4\to-1$（旋转 $360°$ 附近）时 MRP 发散，这是它的奇点；GMAT 只把它当作输入/输出表示，不做传播（没有 MRP 运动学积分）。
  - **实现细节**（`L657-677`）：
    ```cpp
    Real PTP = MRP1*MRP1 + MRP2*MRP2 + MRP3*MRP3;  // P = σᵀσ
    q1 = 2.0 * MRP1 / (1 + PTP);                    // 矢量部分按比例放大
    q2 = 2.0 * MRP2 / (1 + PTP);
    q3 = 2.0 * MRP3 / (1 + PTP);
    qc = (1 - PTP) / (1 + PTP);                     // 标量部分
    return (Rvector(4,q1,q2,q3,qc)).Normalize();
    ```
  - **归一化/奇点**：$1+P\ge1$ 恒成立，正向无奇点；反向（`ToMRPs`）在 $q_4=-1$ 处除以零——GMAT 未在工具层拦截，依赖输入四元数质量。
  - **接口**：`Attitude::Initialize()` MRP 输入分支（`Attitude.cpp` L695-699）与 `SetRvectorParameter(MRPS)`（`L2765`）；参数面板 `AttitudeDisplayStateType` 允许 `"MRPs"` 显示（`Attitude.cpp` L3068）。

### 条目 2.7 角速度 ↔ 欧拉角率（$S$ 与 $S^{-1}$ 矩阵）

- **公式**：设中角 $\theta_2$、末角 $\theta_3$，$\omega=(\omega_x,\omega_y,\omega_z)^\top$ 为体坐标系角速度，$\dot\theta=(\dot\theta_1,\dot\theta_2,\dot\theta_3)^\top$ 为欧拉角率，则
  $$\omega=S(\theta_2,\theta_3)\,\dot\theta,\qquad \dot\theta=S^{-1}(\theta_2,\theta_3)\,\omega$$
  对 1-2-3 序列：
  $$S=\begin{pmatrix}c_3c_2 & s_3 & 0\\ -s_3c_2 & c_3 & 0\\ s_2 & 0 & 1\end{pmatrix},\qquad S^{-1}=\begin{pmatrix}c_3/c_2 & -s_3/c_2 & 0\\ s_3 & c_3 & 0\\ -c_3s_2/c_2 & s_3s_2/c_2 & 1\end{pmatrix}$$
  对 3-1-3 序列：
  $$S=\begin{pmatrix}s_3s_2 & c_3 & 0\\ c_3s_2 & -s_3 & 0\\ c_2 & 0 & 1\end{pmatrix},\qquad S^{-1}=\begin{pmatrix}s_3/s_2 & c_3/s_2 & 0\\ c_3 & -s_3 & 0\\ -s_3c_2/s_2 & -c_3c_2/s_2 & 1\end{pmatrix}$$
- **代码位置**：$\omega=S\dot\theta$：`src/gmatutil/util/AttitudeConversionUtility.cpp` L941-1047（1-2-3 的 $S$ 在 L967-969，3-1-3 在 L1027-1029）；$\dot\theta=S^{-1}\omega$：L732-918（1-2-3 的 $S^{-1}$ 在 L763-765，3-1-3 在 L867-869）。
- **深度讲解**：
  - **几何意义**：欧拉角率定义在"中间轴"上（每次旋转的瞬时轴是前一次旋转后的新轴），而 $\omega$ 定义在本体轴上；$S$ 正是把中间轴角率投影到本体轴坐标的矩阵。$S^{-1}$ 由代码显式硬编码（非运行时求逆），且对对称/非对称序列形态不同。
  - **实现细节**（`L758-766`，1-2-3 分支）：
    ```cpp
    if ((seq1 == 1) && (seq2 == 2) && (seq3 == 3)) {   // 1-2-3
       if (c2 == 0.0)   singularity = true;            // 非对称序列奇点: cos(θ2)=0
       else {
          Si.Set(    c3/c2,   -s3/c2, 0.0,             // S^{-1} 第一行
                        s3,       c3, 0.0,
                 -c3*s2/c2, s3*s2/c2, 1.0);
       }
    } ...
    return Si * angularVel;                             // θ̇ = S^{-1} ω
    ```
    逐行：① 非对称序列判奇点 $\cos\theta_2=0$；② 填入 $S^{-1}$；③ 矩阵乘角速度。对称序列（如 1-2-1，`L818-826`）判奇点改为 $\sin\theta_2=0$，矩阵元素分母为 $s_2$。
  - **奇点处理**：`singularity=true` 时抛 `UtilityException`（`L885-902`），错误消息明确区分"对称序列 EulerAngle2 ≠ 0 / 非对称序列 EulerAngle2 ≠ 90°"，容差 `EULER_ANGLE_TOLERANCE`。
  - **接口**：`Attitude::SetRealParameter` 输入欧拉角率时用 $S$（`Attitude.cpp` L2319-2322），`GetEulerAngleRates` 输出时用 $S^{-1}$（`L1072-1076`）；`SpiceAttitude::GetEulerAngleRates`（`SpiceAttitude.cpp` L465-469）同。

### 条目 2.8 欧拉轴/角 ↔ DCM（罗德里格斯公式）

- **公式**：绕单位轴 $\hat e$ 转 $\theta$（$c=\cos\theta, s=\sin\theta$）：
  $$R=cI_3+(1-c)\,\hat e\hat e^\top-s\,[\hat e]_\times$$
  反向：$\theta=\mathrm{acos}\!\left(\tfrac12(\mathrm{tr}\,R-1)\right)$，$\hat e=\dfrac{1}{2\sin\theta}\big(R_{23}-R_{32},\ R_{31}-R_{13},\ R_{12}-R_{21}\big)^\top$。
- **代码位置**：正向 `src/gmatutil/util/AttitudeConversionUtility.cpp` L1064-1074；反向 L1091-1121。
- **深度讲解**：
  - **几何意义**：与四元数公式（条目 2.1）同源（令 $q_4=\cos\frac\theta2$ 代入即得），是自旋类姿态模型（Spinner/PrecessingSpinner）的核心原语。
  - **实现细节**（正向 L1066-1073）：
    ```cpp
    Rmatrix33 a_x(      0.0, -eAxis(2),  eAxis(1),   // [ê]×
                   eAxis(2),       0.0, -eAxis(0),
                  -eAxis(1),  eAxis(0),      0.0);
    Rmatrix33 I33(true);                            // 单位阵
    Real c = GmatMathUtil::Cos(eAngle);
    Real s = GmatMathUtil::Sin(eAngle);
    return Rmatrix33((c*I33) + ((1.0 - c)*Outerproduct(eAxis, eAxis)) - s*a_x);
    ```
  - **反向奇点处理**（L1104-1119）：先对 $\tfrac12(\mathrm{tr}-1)$ 做 $\pm1$ 截断（浮点误差下 $\mathrm{tr}$ 可越界到 $[1.01,-1.01]$ 之外，`L1104-1108`）；若 $|\sin\theta|<1e-14$（`TOL`，零旋转附近），轴不可辨识，直接返回 $\hat e=(1,0,0)$ 避免除以零（`L1113-1117`）。
  - **接口**：`Spinner::ComputeCosineMatrixAndAngularVelocity`（`Spinner.cpp` L236-237）、`PrecessingSpinner` 的四个旋转（`PrecessingSpinner.cpp` L251、L270、L273、L276）。

---

## 三、姿态基类层：`Attitude` 与 `Kinematic`

### 条目 3.1 姿态状态类型与默认值

- **公式**：`AttitudeStateType ∈ {QUATERNION, DIRECTION_COSINE_MATRIX, EULER_ANGLES_AND_SEQUENCE, MODIFIED_RODRIGUES_PARAMETERS}`；`AttitudeRateStateType ∈ {ANGULAR_VELOCITY, EULER_ANGLE_RATES}`。默认：四元数 $(0,0,0,1)$、欧拉序列 `"321"`、参考系 `"EarthMJ2000Eq"`、`PrecessionRate=5°/s`、`NutationAngle=15°`、`SpinRate=10°/s`、章动参考矢量与自旋轴均 $(0,0,1)$、对准矢量 $(1,0,0)$、约束矢量 $(0,0,1)$。
- **代码位置**：枚举 `src/base/attitude/Attitude.hpp` L58-73；参数表 L252-314；构造函数默认值 `Attitude.cpp` L354-425（序列 L367、四元数 L372、参考系 L365、PrecessingSpinner 默认角 L387-391、矢量 L420-424）。
- **深度讲解**：
  - **设计意图**：头文件注释（`Attitude.hpp` L39-42）说明"姿态对象尚未进入已配置状态，命令模式要允许运行时改姿态，因此所有子类的数据都声明在基类里"——这就是 `NUTATION_REFERENCE_VECTOR_*`、`BODY_ALIGNMENT_VECTOR_*` 等"其他模型字段"全挂在 `Attitude` 上的原因，叶子类不新增数据成员（`Spinner.hpp` L64-67 等 `ParamCount` 均与父类相等）。
  - **实现细节**：`inputAttitudeType`/`inputAttitudeRateType` 记录用户脚本设定的输入表示；`Initialize()` 之后被强制切到 `DIRECTION_COSINE_MATRIX_TYPE`/`ANGULAR_VELOCITY_TYPE`（`Attitude.cpp` L738-739）——从此 DCM 与角速度成为唯一权威表示。

### 条目 3.2 `Initialize()`：输入表示统一为 DCM 与角速度

- **公式**：按输入表示分别换算：四元数→`quaternion.Normalize()` 后转 DCM；MRP→先转四元数再转 DCM；欧拉角→按序列转 DCM；欧拉角率→`angVel = ToAngularVelocity(eulerAngleRates, eulerAngles, seq)`。随后固化 $R_{Bi}=dcm,\ \omega_{IBi}=angVel$。
- **代码位置**：`src/base/attitude/Attitude.cpp` L658-746（换算分支 L683-727，固化 L729-732，类型切换 L738-739）。
- **深度讲解**：
  - **几何意义**：$R_{Bi}$ 与 $\omega_{IBi}$ 是"历元时刻 $t_0$ 的初始姿态/角速度"，叶子模型（Spinner 的 $R_{B0I}$、ThreeAxisKinematic 的四元数初值）都从这里取初值。
  - **实现细节**（四元数分支，L687-689）：
    ```cpp
    case GmatAttitude::QUATERNION_TYPE:
       quaternion.Normalize();                                        // 输入四元数先归一化
       dcm = AttitudeConversionUtility::ToCosineMatrix(quaternion);   // 再转成权威 DCM
       break;
    ```
    欧拉角率分支（L716-723）在换算前先 `UpdateState("EulerAngles")` 把欧拉角同步出来（因为 $\omega=S\dot\theta$ 需要当前角度）。
  - **奇点处理**：进入各分支前由 `Validate()`（`Attitude.cpp` L599-643）按 `inputAttitudeType` 分发校验；`ValidateEulerAngles` 用 $1e-10$ 容差拒绝对称序列 $\sin\theta_2\approx0$ 与非对称序列 $\cos\theta_2\approx0$。
  - **接口**：所有 Get/Set 入口在 `!isInitialized || needsReinit` 时先调 `Initialize()`（如 `GetCosineMatrix` L974-980），保证"改参数→needsReinit→重算"的一致性。

### 条目 3.3 `GetCosineMatrix`/`GetQuaternion`/`GetEulerAngles` 惰性求值

- **公式**：四个 Getter 的公共模式：
  ```
  if (!isInitialized || needsReinit) Initialize();
  ComputeCosineMatrixAndAngularVelocity(atTime);   // 纯虚，叶子类实现
  attitudeTime = atTime;
  return 相应表示;   // 四元数/欧拉角在返回前经 AttitudeConversionUtility 换算
  ```
- **代码位置**：`src/base/attitude/Attitude.cpp`：`GetCosineMatrix` L965-993、`GetQuaternion` L864-874、`GetEulerAngles` L889-917、`GetAngularVelocity` L1007-1031、`GetEulerAngleRates` L1046-1078。
- **深度讲解**：
  - **设计意图**：姿态是"按需计算"而非主动积分——任何时刻要 DCM 就打一次 `ComputeCosineMatrixAndAngularVelocity`，内部由叶子模型决定如何从当前时刻算出 $R(t)$ 与 $\omega(t)$。
  - **实现细节**（`GetEulerAngleRates` L1071-1076）：
    ```cpp
    eulerAngles   = GetEulerAngles(atTime);           // 先要欧拉角（会触发一次 Compute）
    eulerAngleRates = AttitudeConversionUtility::ToEulerAngleRates(angVel,
                        eulerAngles,
                        (Integer) eulerSequenceArray.at(0),   // 用户序列
                        (Integer) eulerSequenceArray.at(1),
                        (Integer) eulerSequenceArray.at(2));
    ```
    注意 `GetAngularVelocity`/`GetEulerAngleRates` 先检查 `modelComputesRates`（L1015-1022）：`NadirPointing`/`CCSDS-AEM` 不计算角速度，请求时直接抛 `AttitudeException`。
  - **奇点处理**：`GetEulerAngles` 的反向换算奇点由条目 2.5 所述容差机制兜底；`GetEulerAngleRates` 的 $S^{-1}$ 奇点抛 `UtilityException`（条目 2.7）。

### 条目 3.4 `UpdateState()`：表示同步与读写互斥

- **公式**：按目标表示 `rep ∈ {Quaternion, EulerAngles, DirectionCosineMatrix, MRPs, EulerAngleRates, AngularVelocity}`，从当前 `inputAttitudeType` 出发做最短换算链（如 MRP→四元数→DCM、欧拉角→DCM→四元数→MRP）。
- **代码位置**：`src/base/attitude/Attitude.cpp` L3609-3725。
- **深度讲解**：
  - **实现细节**（`rep=="EulerAngles"` 的 MRP 分支，L3631-3638）：
    ```cpp
    else if (inputAttitudeType == GmatAttitude::MODIFIED_RODRIGUES_PARAMETERS_TYPE) {
       quaternion = AttitudeConversionUtility::ToQuaternion(mrps);   // MRP → 四元数
       eulerAngles = AttitudeConversionUtility::ToEulerAngles(quaternion,
                                      seq1, seq2, seq3);             // 四元数 → 欧拉角
    }
    ```
    该链式写法保证任一表示读写后，其余表示下次访问时仍一致。
  - **用途**：`SetRealParameter(Q1)` 等"单分量写"路径先 `UpdateState("Quaternion")` 把当前 DCM 转回四元数、改一个分量、再整体回写 DCM（`L1987-1989`）；脚本里四元数必须整向量设置，防止单分量归一化/换算错乱（`L1975-1978` 抛异常）。

### 条目 3.5 校验三件套：四元数模长、欧拉角奇点、DCM 正交性

- **公式**：$|\mathbf q|\ge 1e-10$；对称序列 $|\sin\theta_2|\ge 1e-10$、非对称序列 $|\cos\theta_2|\ge 1e-10$；DCM 满足正交性（$R^\top R-I$ 逐元素 $\le 1e-14$）。
- **代码位置**：`ValidateQuaternion` `src/base/attitude/Attitude.cpp` L3559-3572（模长检查 L3566）；`ValidateEulerAngles` L3450-3493（L3461、L3477）；`ValidateCosineMatrix` L3385-3433（正交性 L3397）；容差常量 `src/gmatutil/util/GmatConstants.hpp` L236-246（`QUAT_MIN_MAG=1e-10` L242、`EULER_ANGLE_TOLERANCE=1e-10` L243、`DCM_ORTHONORMALITY_TOLERANCE=1e-14` L244）。
- **深度讲解**：
  - **数值意义**：三档容差分别对应三种失效模式——四元数近零向量不可归一化；欧拉角反向解在中角奇点处噪声爆炸；DCM 漂离正交群后一切换算失真。
  - **实现细节**（`ValidateCosineMatrix` L3392-3397）：
    ```cpp
    for (Integer ii = 0; ii < 3; ii++)                // 逐元素范围检查 [-1,1]
       for (Integer jj = 0; jj < 3; jj++)
          if ((mat(ii,jj) < -1.0 || mat(ii,jj) > 1.0)) elementOutOfRange = true;
    if (!mat.IsOrthonormal(GmatAttitudeConstants::DCM_ORTHONORMALITY_TOLERANCE))
       notOrthonormal = true;                          // 正交性检查 1e-14
    ```
    错误消息逐项说明违例原因（`L3416-3428`），方便用户定位是超界还是非正交。
  - **奇点处理**：`ValidateEulerAngles` 在中角检查处直接抛异常，错误文本给出"对称序列 EulerAngle2 ≠ 0 / 非对称序列 EulerAngle2 ≠ 90°"与容差数值（`L3463-3490`）。

### 条目 3.6 `GetRotationMatrix` / `GetRotationMatrixDerivative`（B→I 矩阵供力模型）

- **公式**：$[M]^\top = R_{BI}^\top = R_{IB}$（本体→惯性）；其关于轨道状态的偏导 $\partial[M]^\top/\partial X$ 由 `CoordinateConverter` 的旋转矩阵导数模式计算。
- **代码位置**：`src/base/attitude/Attitude.cpp` L4056-4065（`GetRotationMatrix`：先算 `dcm` 再 `dcm.Transpose()`，L4059-4064）；L4080-4104（`GetRotationMatrixDerivative`：置 `cv.SetToCalculateRotMatrixDeriv(true)` 后 `cv.Convert(...)`，取 `GetLastRotationMatrixDerivative()`，L4097-4101）。
- **深度讲解**：
  - **几何意义**：`dcm` 是惯性→本体（$R_{BI}$），转置即本体→惯性 $R_{IB}$；太阳矢量、推力方向等惯性量要进本体坐标系求面元法向点乘时用 $R_{BI}$，而"本体轴在惯性系里的指向"（如 SRP 面元光照）用 $R_{IB}$。
  - **接口（力模型耦合的关键路径）**：`Spacecraft::GetAttitude(Real)`（`src/base/spacecraft/Spacecraft.cpp` L1766-1779，L1771 `return attitude->GetCosineMatrix(a1mjdTime)`）是力模型取姿态的唯一入口；`SolarRadiationPressure.cpp` L3093-3103 取 `scAttitude = sc->GetAttitude(t)`（L3102）后 L3119 用 `scAttitude * sunToSCUnitVec` 把日向单位矢量转到本体系，再与平板法向求光照；`BodyFixedAxes.cpp` L467、`Burn.cpp` L1254、`Thruster.cpp` L2050、`EphemerisWriter.cpp` L1280 同理。`GetRotationMatrixDerivative` 的输出（6 个 `Rmatrix33`：$\partial M^\top/\partial r$ 与 $\partial M^\top/\partial v$ 各三行）供需要姿态-状态偏导的模型（如 SRP 力矩线性化）使用。
  - **耦合方式**：姿态传播与轨道传播是**单向弱耦合**——本 clone 中姿态四元数不进 PSM 状态向量（`src/base/propagator/` 下无 attitude/QUATERNION 相关代码，传播状态仅位置/速度/STM/协方差，见 [CH07-propagator](../CH07-propagator.md)）；姿态模型按"当前传播时刻"被力模型反复查询，指向类模型（NadirPointing/CSFixed）则反过来读取航天器已传播的轨道状态（`GetMJ2000State`）或坐标系旋转矩阵，实现"轨道决定指向、指向决定力、力再推进轨道"的闭环节拍。

### 条目 3.7 Kinematic：运动学姿态中间基类（无新增数学）与 AttitudeException

- **公式**：无新增公式——`Kinematic` 只是 `Attitude` 与叶子模型之间的纯标记层，全部数学（表示换算、初始化、校验、惰性求值）继承自 `Attitude`；`AttitudeException` 只是带固定前缀的异常类型。
- **代码位置**：`src/base/attitude/Kinematic.cpp` L56-106（构造 L56-61、拷贝 L73-76、赋值 L90-94、析构 L103-106）；`Kinematic.hpp` L44-67（`KinematicParamCount = AttitudeParamCount`，L56-59，确认不新增参数）；`src/base/attitude/AttitudeException.cpp` L44-48（`BaseException("Attitude exception: ", details)` 前缀）；`AttitudeException.hpp` L37-43。
- **深度讲解**：
  - **设计意图**：`Kinematic` 把"运动学姿态"（仅几何、不涉及姿态动力学）与将来的"动力学姿态"（转动惯量/力矩积分）在继承树上分层——所有当前叶子模型（Spinner、PrecessingSpinner、NadirPointing、CommandableNadirPointing、ThreeAxisKinematic、CSFixed）都挂在它下面，`Attitude` 头注释（`Attitude.hpp` L32-33）也声明"当前构建只含运动学姿态建模"。
  - **实现细节**：`Kinematic` 无任何数据成员与虚函数实现，`ParamCount` 与 `AttitudeParamCount` 相等（`Kinematic.hpp` L56-59）——这保证了参数 ID 空间在整棵树下连续。
  - **异常体系**：`AttitudeException`（`AttitudeException.hpp` L37-43）继承 `BaseException`，消息统一加 `"Attitude exception: "` 前缀；姿态子系统中所有校验失败（欧拉角奇点、DCM 非正交、Nadir 奇异构型、速率模型未配置）都抛它，调用方（Spacecraft、力模型）按 `BaseException` 捕获。

---

## 四、运动学叶子模型

### 条目 4.1 Spinner：绕固定欧拉轴等速自旋

- **公式**：设 $t_0$ 时刻自旋轴 $\hat e=\omega_{IBi}/|\omega_{IBi}|$、角速率 $\omega=|\omega_{IBi}|$，$\Delta t=t-t_0$，则
  $$R_{BI}(t)=R_{\hat e}(\omega\Delta t)\,R_{BI}(t_0),\qquad R_{\hat e}(\theta)=cI+(1-c)\hat e\hat e^\top-s[\hat e]_\times$$
- **代码位置**：`src/base/attitude/Spinner.cpp`：初值固化 `Initialize()` L147-181（$R_{B0I}=R_{Bi}$ L161，$\omega=|\omega|$ L175，$\hat e=\omega/|\omega|$ L176）；传播 `ComputeCosineMatrixAndAngularVelocity` L214-252。
- **深度讲解**：
  - **几何意义**：自旋轴在本体系内固定（$\hat e$ 由初始角速度方向决定），本体绕自身轴匀速转——典型的"消旋后自旋稳定"航天器模型。**关键近似**：代码注释（L162）明确按 Steve 2006 规范，自旋轴取输入角速度方向，且 $\omega_{IBi}$ 全程不变（不随体轴转动），因此 $\Delta t$ 内转过的总角就是 $\omega\Delta t$。
  - **实现细节**（L228-244）：
    ```cpp
    Real dt = (atTime - epoch) * GmatTimeConstants::SECS_PER_DAY;  // MJD 差 → 秒
    Real theEAngle = initialwMag * dt;                             // θ = ω·Δt
    Rmatrix33 RBB0t = AttitudeConversionUtility::EulerAxisAndAngleToDCM(
                         initialeAxis, theEAngle);                 // 本体绕 ê 转 θ 的矩阵
    dcm = RBB0t * RB0I;                                            // R_BI(t) = R_ê(θ)·R_BI(t0)
    epoch = epoch + dt/GmatTimeConstants::SECS_PER_DAY;            // 滑动历元（增量式）
    RB0I  = dcm;                                                   // 更新基准，避免大 Δt 累积
    ```
    逐行：① MJD 差换算成秒；② 总转角；③ 罗德里格斯公式生成增量旋转；④ 左乘到基准 DCM；⑤⑥ 把历元与基准矩阵滑到当前时刻——这是**增量式传播**：每次调用只转"距上次调用的 Δt"，防止大时间跨度下角度模 $2\pi$ 精度损失。
  - **归一化/奇点**：$\omega=0$ 时 $\hat e$ 无定义，代码置零向量（L177-178）；此时 `EulerAxisAndAngleToDCM` 仍返回单位阵（角度为 0）。
  - **接口**：角速度在 `Initialize` 后一直保持 `angVel`（不重算，L240 注释"currentwIBB already computed"），因此 Spinner 的 `GetAngularVelocity` 恒返回初值。

### 条目 4.2 PrecessingSpinner：3-1-3 进动-章动-自旋

- **公式**：定义三个欧拉角（绕 3-轴进动 $\phi$、绕 1-轴章动 $\theta$、绕 3-轴自旋 $\psi$）：
  $$\phi(t)=\dot\phi\,t+\phi_0,\quad \theta(t)=\theta_0,\quad \psi(t)=\dot\psi\,t+\psi_0$$
  $$R_{BI}=R_3(\psi)\,R_1(\theta)\,R_3(\phi)\,R_{init}$$
  角速度在本体 1-2-3 轴系中：
  $$\omega_{123}=\big(\dot\phi\sin\theta\sin\psi,\ \dot\phi\sin\theta\cos\psi,\ \dot\phi\cos\theta+\dot\psi\big)^\top$$
  再经基变换 $R_{Bb}$（列向量为本体轴）转到本体 xyz：$\omega_{xyz}=R_{Bb}\,\omega_{123}$。
- **代码位置**：`src/base/attitude/PrecessingSpinner.cpp` L173-299：角度推进 L236-237，初始对准 L240-252，体轴构造 L255-267，三个旋转 L270-276，DCM 合成 L279，角速度 L282-298。
- **深度讲解**：
  - **几何意义**：自旋轴 $\hat s$（BodySpinAxis）相对惯性系中的章动参考矢量 $\hat n$（NutationReferenceVector）倾斜章动角 $\theta$；$\hat s$ 绕 $\hat n$ 以进动率 $\dot\phi$ 画圆锥，本体再绕 $\hat s$ 以自旋率 $\dot\psi$ 自转——即"自旋+进动"的双锥运动，对应实际自旋稳定航天器受章动激励后的运动学。默认参数（`Attitude.cpp` L387-391）：进动率 $5°/s$、章动角 $15°$、自旋率 $10°/s$。
  - **实现细节**（L236-279）：
    ```cpp
    Real spinAngle       = ( spinRate * dt ) + initialSpinAngle;      // ψ = ψ̇t + ψ0
    Real precessionAngle = ( precessionRate * dt ) + initialPrecessionAngle;  // φ
    // 先构造把体自旋轴对齐到章动参考矢量的初始旋转
    Rvector3 rvectorAlign = Cross(bodySpinAxisNormalized, nutationReferenceVectorNormalized);
    Real angleAlign = GmatMathUtil::ACos(bodySpinAxisNormalized * nutationReferenceVectorNormalized);
    if (angleAlign < 1.0e-16) rmatrixInit 保持单位阵;                    // 已对齐
    else rmatrixInit = EulerAxisAndAngleToDCM(rvectorAlign/|..|, angleAlign);
    // 本体 1-2-3 轴：3-轴取自旋轴，1-轴取自旋轴与 x 轴的叉积（平行时退回 y 轴）
    xAxis.Set(1,0,0);  yAxis.Set(0,1,0);
    bodyAxis1 = Cross(bodySpinAxisNormalized, xAxis);
    if (bodyAxis1.GetMagnitude() < 1.0e-5) bodyAxis1.Set(0,1,0);        // 自旋轴∥x 的退化情形
    bodyAxis3 = bodySpinAxisNormalized;  bodyAxis2 = Cross(bodyAxis3, bodyAxis1);
    bodyAxis1/=|..|; bodyAxis2/=|..|; bodyAxis3/=|..|;                  // 归一化构成右手系
    rmatrixPrecession = EulerAxisAndAngleToDCM(bodyAxis3, precessionAngle);  // 绕 3-轴
    rmatrixNutation   = EulerAxisAndAngleToDCM(bodyAxis1, nutationAngle);    // 绕 1-轴
    rmatrixSpin       = EulerAxisAndAngleToDCM(bodyAxis3, spinAngle);        // 绕 3-轴
    dcm = rmatrixSpin * rmatrixNutation * rmatrixPrecession * rmatrixInit;   // R3(ψ)R1(θ)R3(φ)Rinit
    ```
    逐行解读：① 推进两个随时间变化的角；② 初始旋转把体自旋轴搬到 $\hat n$；③ 在体轴系内建立"3-1-3"中间轴（3-轴=自旋轴，1-轴=自旋轴⊥分量，2-轴补齐右手系）；④ 三个基本旋转按 3-1-3 次序复合。
  - **角速度推导**（L282-298）：进动率在 1-2-3 系中的投影即 $\omega_{123}$；`RBb` 的列是 `bodyAxis1/2/3` 在本体 xyz 中的坐标，故 $\omega_{xyz}=R_{Bb}\,\omega_{123}$。
  - **归一化/奇点**：`bodySpinAxis`/`nutationReferenceVector` 模长 $<1e-5$ 抛异常（L190-205）；自旋轴∥本体 x 轴时 `bodyAxis1` 退化，代码退回 $(0,1,0)$（L258-261）；`angleAlign<1e-16` 时初始旋转取单位阵（L244-247）。

### 条目 4.3 ThreeAxisKinematic：四元数运动学解析积分

- **公式**：对常角速度 $\omega$，四元数运动学 $\dot q=\tfrac12\Omega(\omega)q$ 的解析解：
  $$q(t)=\left[\cos\frac{\omega\Delta t}{2}I_4+\frac{1}{\omega}\sin\frac{\omega\Delta t}{2}\,\Omega\right]q(t_0),\qquad
  \Omega=\begin{pmatrix}0 & \omega_3 & -\omega_2 & \omega_1\\ -\omega_3 & 0 & \omega_1 & \omega_2\\ \omega_2 & -\omega_1 & 0 & \omega_3\\ -\omega_1 & -\omega_2 & -\omega_3 & 0\end{pmatrix}$$
- **代码位置**：`src/base/attitude/ThreeAxisKinematic.cpp`：$\Omega$ 构造 `Initialize()` L214-218；传播 `ComputeCosineMatrixAndAngularVelocity` L304-360（角度 L333、四元数更新 L341-342、归一化 L343、DCM 回写 L348）。
- **深度讲解**：
  - **几何意义**：这是本章唯一的"显式运动学积分"条目。$\dot q=\tfrac12\Omega q$ 是四元数运动学方程的标准矩阵形式；$\Omega^2=-\omega^2 I_4$ 使指数映射 $e^{\Omega\Delta t/2}$ 闭合为"余弦×单位阵 + 正弦×$\Omega/\omega$"，得到与 Spinner（条目 4.1）等价的精确一步解——只是把"轴-角旋转"搬到了四元数代数里，且**每一步重新归一化**，数值上更稳。
  - **实现细节**（L333-349）：
    ```cpp
    Real angle = wMag * (SECS_PER_DAY * (atTime - epoch)) / 2;   // θ/2 = ωΔt/2
    if (wMag != 0.0) {
       quaternion = (cos(angle) * I44 + (1.0/wMag) * sin(angle) * Omega) * quaternion;
       quaternion = quaternion.Normalize();                        // 每步归一化防漂移
    }
    dcm   = AttitudeConversionUtility::ToCosineMatrix(quaternion); // 权威 DCM 同步
    epoch = atTime;                                                // 增量式：历元滑动
    ```
    与 Spinner 相同的"增量式 + 历元滑动"策略（L349），保证长时间传播不累积 $2\pi$ 折叠误差；$\omega=0$ 时跳过更新（L339）。
  - **归一化/奇点**：无奇点；每步 `Normalize()` 是四元数传播的标配（漂移来自浮点误差，不归一化会在数百步后破坏单位模长）。
  - **命令模式接口**：`IsParameterCommandModeSettable`（L272-284）允许任务段内直接改角速度（`ANGULAR_VELOCITY*`），用于模拟姿态机动——改后 `needsReinit` 触发 `Initialize()` 重建 $\Omega$ 与 $wMag$（L210-218）。

---

## 五、指向类叶子模型

### 条目 5.1 CSFixed：坐标系固定姿态

- **公式**：设参考坐标系 CS 相对惯性系的旋转矩阵为 $R_{CS}$（`GetLastRotationMatrix`），则
  $$R_{BI}=R_{CS}^\top,\qquad [\tilde\omega]_\times=-\dot R_{CS}^\top R_{BI},\qquad \omega=(\tilde\omega_{21},\tilde\omega_{02},\tilde\omega_{10})$$
- **代码位置**：`src/base/attitude/CSFixed.cpp` L164-211（`RiI` L183、`dcm` L185、`RiIDot` L188、`wxIBB` L194、角速度提取 L196-198）。
- **深度讲解**：
  - **几何意义**：本体坐标架与某个命名坐标系（如 `EarthFixed`、`SunFixed`、`LVLH`）完全固连——航天器姿态 = 该坐标系相对惯性的姿态。这是对地静止/太阳定向等"姿态被外部几何锁定"场景的建模，姿态本身无独立动力学。
  - **实现细节**（L181-198）：
    ```cpp
    Rvector bogus(6,100.0,200.0,300.0,400.0,500.0,600.0);   // 占位状态：仅触发坐标转换
    Rvector bogus2 = refCS->FromBaseSystem(A1Mjd(atTime), bogus, true);
    Rmatrix33 RiI  = (refCS->GetLastRotationMatrix()).Transpose();  // 惯性→CS 的旋转
    dcm              = RiI;                                         // 本体=CS，故 R_BI = RiI
    Rmatrix33 RiIDot = (refCS->GetLastRotationDotMatrix()).Transpose(); // 旋转矩阵时间导数
    Rmatrix33 wxIBB  = - (RiIDot * (dcm.Transpose()));              // [ω̃]× = -Ṙ·Rᵀ
    angVel(0) = wxIBB(2,1);  angVel(1) = wxIBB(0,2);  angVel(2) = wxIBB(1,0);
    ```
    逐行：① 用假状态向量调 `FromBaseSystem`，纯粹为了让坐标系内部算出并缓存最新旋转矩阵与导数；② 取缓存矩阵转置得 $R_{BI}$；③④ 由 $\dot R$ 与 $R$ 拼出反对称阵（注意负号对应"$\dot R=-[\omega]_\times R$"，即 $R=R_{CS\gets I}$ 的转动方向约定）；⑤ 从反对称阵的 $(2,1),(0,2),(1,0)$ 三个位置取回 $\omega$ 分量（与 $[\omega]_\times$ 的标准排列一致）。
  - **奇点**：无数学奇点；若参考坐标系不支持导数计算则 `RiIDot` 无意义，属配置错误。
  - **接口**：`refCS` 由 `Attitude::SetRefObject` 注入（`Attitude.cpp` L1335-1368），并做"BodyFixed 系含航天器循环引用"的防环检查（L1356-1365）。

### 条目 5.2 NadirPointing：LVLH 轨道系 + TRIAD 对地指向

- **公式**：以参考天体为原点，$\mathbf r=\mathbf r_{sc}-\mathbf r_{ref}$、$\mathbf v=\dot{\mathbf r}$：
  $$\hat x=\frac{\mathbf r}{|\mathbf r|},\quad \hat y=\frac{\mathbf r\times\mathbf v}{|\mathbf r\times\mathbf v|},\quad \hat z=\hat x\times\hat y,\qquad R_{I\gets LVLH}=(\hat x\ \hat y\ \hat z)$$
  本体与 LVLH 之间的常值姿态由 TRIAD 求得：给定体坐标系两矢量 $V_1,V_2$ 与 LVLH 系两矢量 $W_1,W_2$，
  $$\mathbf r_1=\frac{V_1}{|V_1|},\ \mathbf r_2=\frac{V_1\times V_2}{|V_1\times V_2|},\ \mathbf r_3=\frac{V_1\times(V_1\times V_2)}{|V_1\times(V_1\times V_2)|}$$
  （$W$ 侧同理得 $\mathbf s_1,\mathbf s_2,\mathbf s_3$），则 $R_{LVLH\gets B}=\sum_i \mathbf s_i\mathbf r_i^\top$，最终
  $$R_{BI}=\big(R_{I\gets LVLH}\,R_{LVLH\gets B}\big)^\top$$
- **代码位置**：`src/base/attitude/NadirPointing.cpp`：TRIAD L180-254（$\mathbf r_1$ L193、$\mathbf r_2$ L202、$\mathbf r_3$ L211、$R$ 矩阵 L213-215、$\mathbf s_i$ L226-248、合成 L251）；`ComputeCosineMatrixAndAngularVelocity(Real)` L270-395（状态差 L299-303、奇点检查 L316-323、$\hat x\hat y\hat z$ L328-332、$R_{I\gets LVLH}$ L347-356、约束矢量 L359-378、TRIAD 调用 L381、$R_{BI}$ L384-386）。
- **深度讲解**：
  - **几何意义（对地指向的轨道系定义）**：$\hat x$ 沿航天器→参考天体方向的反向（即**天顶**方向；体 $-x$ 轴指向天底/地心），$\hat y$ 沿轨道角动量方向（轨道法向），$\hat z=\hat x\times\hat y$ 补成右手系——这就是标准的 LVLH（Local Vertical Local Horizontal）径向-法向-切向构型。姿态约束两种模式（L359-378）：`OrbitNormal` 模式体 $-x$ 对准 $\hat x$、体 $+y$ 对准 $\hat y$；`Velocity` 模式体 $-x$ 对准 $\hat x$、体 $-z$ 对准 $\hat y$。用户可另行设置 `BodyAlignmentVector`/`BodyConstraintVector`（默认 $(1,0,0)$ 与 $(0,0,1)$，`Attitude.cpp` L423-424）定义"体上哪两个矢量去对准轨道系的哪两个矢量"。
  - **实现细节**（`ComputeCosineMatrixAndAngularVelocity` L328-386）：
    ```cpp
    Rvector3 normal = Cross(pos,vel);                                  // h = r×v 轨道法向
    Rvector3 xhat = pos/pos.GetMagnitude();                            // 径向上（天顶）
    Rvector3 yhat = normal/normal.GetMagnitude();                      // 轨道法向
    Rvector3 zhat = Cross(xhat,yhat);                                  // 右手系第三轴
    // RIi: 惯性 → LVLH（列向量 = xhat,yhat,zhat 在惯性系的坐标）
    RIi(0,0)=xhat(0); RIi(1,0)=xhat(1); RIi(2,0)=xhat(2); ...
    // 依约束模式设定 LVLH 参考矢量（ref）与约束矢量（con）
    referenceVector = (-1, 0, 0);  constraintVector = (0, 1, 0);       // OrbitNormal
    // 或 constraintVector = (0, 0, -1)                                // Velocity
    Rmatrix33 RiB = TRIAD( bodyAlignmentVector, bodyConstraintVector,   // LVLH→本体
                           referenceVector,     constraintVector );
    dcm = RIi*RiB;                                                     // 本体→惯性
    dcm = dcm.Transpose();                                             // 惯性→本体
    ```
  - **TRIAD 实现要点**（L180-254）：两系各取两个观测矢量构正交基 $\{\mathbf r_i\}$、$\{\mathbf s_i\}$，旋转矩阵 $R=\sum\mathbf s_i\mathbf r_i^\top$ 即"把 A 系基映到 B 系基"的旋转。代码在每个归一化处检查分母 $<1e-15$（`DENOMINATOR_TOLERANCE`，L51）——对应"位置零、速度零、r∥v（共线轨道）、体矢量零、体矢量平行"五种奇异构型（L316-323 还叠加了 $1e-5$ 的预检查）。
  - **角速度**：`modelComputesRates=false`（构造 L77），角速度不计算（L388-394 注释掉的计算留作 TODO）；因此 SRP 力矩等需要 $\omega$ 的模型不能配 NadirPointing。
  - **状态耦合**：`pos/vel` 来自 `owningSC->GetMJ2000State(theTime)` 与 `refBody->GetMJ2000State(theTime)`（L299-303）——**姿态每查询一次就读一次已传播的轨道状态**，是"轨道→姿态"单向耦合的典型（见条目 3.6 的耦合讨论）。

### 条目 5.3 NadirPointing 旋转矩阵偏导（`GetRotationMatrixDerivative`）

- **公式**：对 $[M]^\top=R_{IB}$（本体→惯性）关于状态 $X=(\mathbf r,\mathbf v)$ 的偏导：
  $$\frac{\partial\hat x}{\partial\mathbf r}=\frac{I-\hat x\hat x^\top}{|\mathbf r|},\quad
  \frac{\partial\hat v}{\partial\mathbf v}=\frac{I-\hat v\hat v^\top}{|\mathbf v|},\quad
  \frac{\partial\hat u}{\partial\mathbf u}=\frac{I-\hat u\hat u^\top}{|\mathbf u|}\ (\mathbf u=\hat x\times\hat v),\quad
  \frac{\partial\hat y}{\partial\mathbf r}=\frac{\partial\hat y}{\partial\mathbf u}\frac{\partial\mathbf u}{\partial\mathbf r},\dots$$
  返回 $[\tfrac{\partial\hat x}{\partial r}R_{iB},\ \tfrac{\partial\hat y}{\partial r}R_{iB},\ \tfrac{\partial\hat z}{\partial r}R_{iB},\ \tfrac{\partial\hat x}{\partial v}R_{iB},\ \tfrac{\partial\hat y}{\partial v}R_{iB},\ \tfrac{\partial\hat z}{\partial v}R_{iB}]$（每项 $3\times3$）。
- **代码位置**：`src/base/attitude/NadirPointing.cpp` L550-740（$\partial\hat x/\partial r$ L628、$\partial\hat v/\partial v$ L634、$\partial\hat y/\partial u$ L641、链式 $\partial u/\partial r$ L644-654、$\partial u/\partial v$ L658-668、$\partial\hat z/\partial r$ L670-685、$\partial\hat z/\partial v$ L687-701、结果压栈 L731-737）。`CommandableNadirPointing.cpp` L1085-1275 为逐行相同的实现。
- **深度讲解**：
  - **几何意义**：LVLH 三轴是 $\mathbf r,\mathbf v$ 的非线性函数，其偏导即"姿态矩阵对轨道状态的灵敏度"，用于把姿态变化线性化进力/力矩模型的变分方程（姿态随轨道摄动的一阶响应）。
  - **实现细节**（L628-641）：
    ```cpp
    Rmatrix33 dxHatdr = (I - Outerproduct(xhat, xhat))/ posMag;   // d(r/|r|)/dr = (I-x̂x̂ᵀ)/|r|
    Rmatrix33 dxHatdv = Zero;                                     // x̂ 不显含 v
    Rvector3  vhat = vel / velMag;                                // 相对速度单位矢量
    Rmatrix33 dvHatdv = (I - Outerproduct(vhat, vhat)) / velMag;  // d(v/|v|)/dv
    Rvector3 u = Cross(xhat,vhat);                                // u = x̂×v̂
    Rmatrix33 dyHatdu = (I - Outerproduct(uHat, uHat)) / uMag;    // d(û)/du，Û=û/|u|
    ```
    逐行：① 单位矢量的导数恒为"垂射投影 $(I-\hat a\hat a^\top)$ 除以模长"；② $\partial\hat y/\partial\mathbf r$ 走链式法则 $\tfrac{\partial\hat y}{\partial\mathbf u}\tfrac{\partial\mathbf u}{\partial\mathbf r}$，其中 $\partial\mathbf u/\partial\mathbf r$ 用叉乘矩阵逐列构造（L646-653）；③ $\hat z=\hat x\times\hat y$ 的偏导用莱布尼茨法则展开（L670-685）。
  - **奇点**：与条目 5.2 相同的分母检查；$|\mathbf u|\to0$（$\hat x\parallel\hat v$）时该项退化。

### 条目 5.4 CommandableNadirPointing：命令模式可设的对地指向

- **公式**：姿态合成公式与 NadirPointing 完全相同（LVLH + TRIAD，$R_{BI}=(R_{I\gets LVLH}R_{LVLH\gets B})^\top$），差异在**参数设置入口**：允许任务段内直接改写姿态（四元数、DCM、对准/约束矢量）并立即生效。
- **代码位置**：`src/base/attitude/CommandableNadirPointing.cpp`：`IsParameterCommandModeSettable` L616-646（`QUATERNION`/`DIRECTION_COSINE_MATRIX`/对准约束矢量均返回 true，L627-640）；`SetRvectorParameter(QUATERNION)` L537-560（赋值→归一化→回写 DCM→`needsReinit=false`）；`SetRmatrixParameter(DIRECTION_COSINE_MATRIX)` L582-610；`SetRealParameter(DCM_ij)` L372-430；姿态计算 L1291-1416；TRIAD L1563-1637（与 NadirPointing 相同）。
- **深度讲解**：
  - **设计意图**：GOES 任务需要"任务段内切换姿态"（对地观测→天底指向切换），而基类 `Attitude::SetRealParameter` 对已初始化对象禁止单分量写四元数（`Attitude.cpp` L1973-1978）。本类覆写 Set 系列，使四元数/DCM 可在 `CommandMode` 被直接赋值（L70 注释：`setInitialAttitudeAllowed = true` 覆盖 NadirPointing 的禁令）。
  - **实现细节**（`SetRvectorParameter` L537-560）：
    ```cpp
    if (id == QUATERNION) {
       for (int i=0;i<4;i++) quaternion(i) = value(i);   // 整向量赋值
       quaternion.Normalize();                            // 归一化
       dcm = AttitudeConversionUtility::ToCosineMatrix(quaternion);  // 同步权威 DCM
       needsReinit = false;                               // 不重初始化，直接生效
       return quaternion;
    }
    ```
    DCM 单元素设置（`SetRealParameter` L372-430）在每次写后检查 `dcm.IsOrthonormal(1e-14)`，正交时才回算四元数（L417-427）——避免用户分 9 次赋值中间态触发换算错误。
  - **归一化/奇点**：四元数赋值即归一化；DCM 元素越界（$<-1$ 或 $>1$）抛异常（L375-383）。
  - **注意**：与 NadirPointing 一样 `modelComputesRates=false`，不计算角速度（L1409 注释）。

---

## 六、星历姿态读取模型

### 条目 6.1 CCSDSAttitude：CCSDS-AEM 星历姿态

- **公式**：$R_{BI}(t)=\text{AEM}(t)$——按 CCSDS 附件 AEM（Attitude Ephemeris Message）文件插值出的姿态矩阵；不计算角速度。
- **代码位置**：`src/base/attitude/CCSDSAttitude.cpp`：`Initialize` L141-169（文件路径检查 L151-155、`reader->SetFile(aemFileFullPath)` L162、`reader->Initialize()` L163）；`ComputeCosineMatrixAndAngularVelocity` L201-213（`dcm = reader->GetState(atTime)` L208）。
- **深度讲解**：
  - **几何意义**：姿态来自外部生成的星历文件（任务规划输出的 AEM），GMAT 只做插值回放，不参与姿态动力学。文件路径在 `SetStringParameter(AEM_FILE_NAME)` 时解析为全路径（`Attitude.cpp` L3193-3205，经 `VEHICLE_EPHEM_CCSDS_PATH` 路径变量）。
  - **实现细节**（L201-213）：
    ```cpp
    void CCSDSAttitude::ComputeCosineMatrixAndAngularVelocity(Real atTime) {
       if (!isInitialized || needsReinit)  Initialize();
       dcm = reader->GetState(atTime);     // AEM 读取器按时刻插值出 DCM
       // 不计算角速度（模型不支持）
    }
    ```
    读取器 `CCSDSAEMReader` 位于 `src/gmatutil/util/CCSDSAEMReader.*`（本章外，只引用）：内部处理 AEM 文件解析、四元数/欧拉角→DCM 转换与时间插值。
  - **归一化/奇点**：文件内容决定；`aemFileFullPath==""` 时抛异常（L151-155）。
  - **接口**：`modelComputesRates=false`（L68），`GetAngularVelocity` 抛异常（基类 L1015-1022）；AEM 姿态适用于"姿态已定，只需轨道仿真"的场景。

### 条目 6.2 SpiceAttitude：SPICE CK 内核姿态

- **公式**：$R_{BI}(t),\ \omega_{IB}(t)=\mathrm{ckp}\big(\mathrm{scName}, \mathrm{naifId}, \mathrm{refFrameNaifId}, t\big)$——由 NAIF ID 标识的 CK 指向内核在 $t$ 时刻的指向与角速度；GMAT 侧只做内核装配与时间转换。
- **代码位置**：`src/base/attitude/SpiceAttitude.cpp`：`Initialize` L205-296（CK/SCLK 必选检查 L218-229、FK 可选警告 L230-235、内核装载 L241-263、NAIF ID 解析 L265-283）；`ComputeCosineMatrixAndAngularVelocity` L789-801（`reader->GetTargetOrientation(scName, naifId, refFrameNaifId, atTime, dcm, angVel)` L794）。
- **深度讲解**：
  - **几何意义**：姿态由 NAIF/SPICE 工具链提供——CK 内核存指向（四元数+角速度采样），SCLK 内核做航天器时钟↔TDB 转换，FK 内核定义参考框。GMAT 的 `SpiceAttitudeKernelReader`（`src/base/spice/SpiceAttitudeKernelReader.*`，本章外）封装 `ckgp` 系列调用。
  - **实现细节**（`Initialize` 装配段 L241-263）：
    ```cpp
    for (StringArray::iterator j = ckFullPath.begin(); j != ckFullPath.end(); ++j)
       reader->LoadKernel(*j);        // 逐条装载 CK 指向内核（全路径）
    for (j = sclkFullPath.begin(); ...) reader->LoadKernel(*j);   // SCLK 时钟内核
    for (j = fkFullPath.begin(); ...)  reader->LoadKernel(*j);    // FK 框架内核（可选）
    ...
    if (naifId == UNDEFINED_NAIF_ID)  naifId = reader->GetNaifID(scName);  // 名字→NAIF ID
    ```
    内核文件路径在 `SetStringParameter`（L623-724）经 `VEHICLE_EPHEM_SPK_PATH` 解析为全路径并检查存在性。
  - **覆盖 Getter 的原因**：SpiceAttitude 覆写全部 Getter（`GetQuaternion` L347-353、`GetEulerAngles` L368-406、`GetCosineMatrix` L420-426、`GetAngularVelocity` L440-445、`GetEulerAngleRates` L460-471）——**每次调用无条件重算**（不检查 `attitudeTime` 容差），因为 CK 内核是稀疏采样，两次查询之间插值结果必须新鲜；头文件 L73-74 注释明言"regardless of the delta time since the last attitude update"。
  - **编译开关**：`#ifdef __USE_SPICE__`（`SpiceAttitude.hpp` L47-49、L118-120）——非 SPICE 构建下 `ComputeCosineMatrixAndAngularVelocity` 抛"SPICE not included"异常（L795-799）。
  - **接口**：`SetObjectID`（L327-333）由航天器装配时注入 `scName/naifId/refFrameNaifId`；`naifId` 未设时从内核按名字查询（L265-283）。

---

## 七、工具与参数封装

### 条目 7.1 `GmatAttUtil`：GSS 移植的换算（双命名空间）

- **公式**：四元数（矢量 $\mathbf q_v$、标量 $q_s$）→DCM 的显式展开：
  $$R=\frac{1}{q_v^\top q_v+q_s^2}\begin{pmatrix}q_0^2-q_1^2-q_2^2+q_3^2 & 2(q_0q_1+q_2q_3) & 2(q_0q_2-q_1q_3)\\ 2(q_0q_1-q_2q_3) & -q_0^2+q_1^2-q_2^2+q_3^2 & 2(q_1q_2+q_0q_3)\\ 2(q_0q_2+q_1q_3) & 2(q_1q_2-q_0q_3) & -q_0^2-q_1^2+q_2^2+q_3^2\end{pmatrix}$$
  （$q_0..q_3$ 即代码里的 `q00..q33` 乘积项）。
- **代码位置**：`src/gmatutil/util/AttitudeUtil.cpp`：`GmatAttUtil::ToCosineMatrix(qVec,qScalar)` L153-190（元素 L178-186）；`GmatAttUtil::ToCosineMatrix(rotAngle,rotAxis)` L200-214（轴-角→四元数→上式）；`GmatAttUtil::ToEulerAngles(cosMat,seq)` L76-143（通用代数式，与条目 2.5 的 12 分支等价）；`GmatAttUtil::ToEulerAngles(rotAngle,rotAxis,seq)` L48-65。
- **深度讲解**：
  - **与 AttitudeConversionUtility 的关系**：同一数学、两套实现——`AttitudeConversionUtility`（2013 年重写，条目 2.x 全部使用）是姿态子系统的主路径；`GmatAttUtil` 是从 GSS 移植的旧工具（头文件 L27-30 注释），`FloatAttUtil` 是 OpenGL 轨迹球风格的 float 工具，二者目前主要供 GUI 三轴视图（trackball）等使用。
  - **实现细节**（`ToEulerAngles(cosMat,seq)` 的对称序列分支，L117-140）：先算 $\ell=6-i-j$ 补出第三轴，中角 $\theta_2=\mathrm{acos}(R_{kk})$，首末角用 `atan2` 从 $R$ 的对应元素对提取，符号由 `((k-j+3)%3)*2-3` 的 $-3/+3$ 技巧决定——用模运算自动生成"叉积顺序导致的符号翻转"，避免 12 个手写分支。
  - **数值注意**：`FloatAttUtil::NormalizeQuat`（L475-482）用 $\sum q_i^2$（**非开方**）做除法，是一个已知的宽松实现（仅在 GUI 展示路径使用，不影响仿真精度）。
  - **四元数乘法**：`FloatAttUtil::AddQuats`（L442-469）实现 Hamilton 积 $\mathbf q=\mathbf q_1\otimes\mathbf q_2$（标量 $q_1q_2-\mathbf q_1\cdot\mathbf q_2$，矢量 $q_2\mathbf q_1+q_1\mathbf q_2+\mathbf q_2\times\mathbf q_1$，L449-457），并每 97 次调用归一化一次（`RENORMCOUNT`，L437、L464-468）。

### 条目 7.2 `AttitudeRmat33`：姿态 DCM 系统参数

- **公式**：系统参数 `Spacecraft.AttitudeRmat33`（或类似名）在求值时返回航天器当前姿态 DCM：$R_{BI}(t_{sc})$；数据链路为 `EvaluateRmatrix() → Evaluate() → mSpacecraft->GetAttitude(epoch) → Attitude::GetCosineMatrix`。
- **代码位置**：`src/base/parameter/AttitudeRmat33.cpp` L88-92（`EvaluateRmatrix`）；L40-50（构造，`AddRefObject(obj)` L49）；引用对象管理委托给 `AttitudeData`（`Validate` L129-132、`Initialize` L138-152、`GetRefObject` L215-235 等）；数据枚举与取值入口 `src/base/parameter/AttitudeData.hpp` L57（`GetRmatrix33`）、L77-113（`DCM_11..DCM_33`、`QUATERNION`、`EULER_ANGLE_*`、`MRP_*`、`ANGULAR_VELOCITY_*` 等姿态项）。`AttitudeData.cpp` L120（`Rmatrix33 cosMat = mSpacecraft->GetAttitude(epoch)`）是具体取值点。
- **深度讲解**：
  - **设计模式**：`AttitudeRmat33` 多重继承 `Rmat33Var`（参数类型基类）+ `AttitudeData`（航天器引用数据）；`AttitudeData` 持 `mSpacecraft` 指针（`AttitudeData.hpp` L72）并维护 `mEpochId` 以在正确时刻取姿态。参数创建后 `AddRefObject` 立即登记航天器（L49）。
  - **实现细节**（`EvaluateRmatrix` L88-92）：
    ```cpp
    const Rmatrix& AttitudeRmat33::EvaluateRmatrix() {
       Evaluate();            // AttitudeData::Evaluate：按 epoch 调 mSpacecraft->GetAttitude
       return mRmat33Value;   // 缓存 DCM 结果
    }
    ```
    `Evaluate()` 内部先 `InitializeRefObjects()` 保证 `mSpacecraft` 就位（`Initialize` L138-152），再按 `mEpochId` 取航天器当前历元调用 `GetAttitude`。
  - **接口（参数→姿态的桥）**：这条链路让报告器/副本地表（Report、Ephemeris 等）能以矩阵参数形式输出实时姿态；与条目 3.6 的 `Spacecraft::GetAttitude`（`Spacecraft.cpp` L1766-1779）共用同一入口，保证"力模型看到的 DCM"与"报告输出的 DCM"完全一致。

---

## 八、公式索引表

| 公式 | 文件:行 | 所属类 |
|---|---|---|
| 四元数→DCM：$R=c[(q_4^2-\mathbf q\cdot\mathbf q)I+2\mathbf q\mathbf q^\top-2q_4[\mathbf q]_\times]$ | `src/gmatutil/util/AttitudeConversionUtility.cpp:73-102` | AttitudeConversionUtility |
| 欧拉角+序列→DCM（12 分支，含 1-2-3/3-1-3/3-2-1 字面量） | `src/gmatutil/util/AttitudeConversionUtility.cpp:120-244` | AttitudeConversionUtility |
| 欧拉序列全集（12 种，默认 321） | `src/base/attitude/Attitude.cpp:234-248`；`AttitudeConversionUtility.cpp:45-59` | Attitude |
| DCM→四元数（Shepperd 最大分量分支） | `src/gmatutil/util/AttitudeConversionUtility.cpp:585-639` | AttitudeConversionUtility |
| DCM→欧拉角（12 分支，1-2-3/3-1-3/3-2-1 公式） | `src/gmatutil/util/AttitudeConversionUtility.cpp:420-548` | AttitudeConversionUtility |
| MRP→四元数：$q_i=2\sigma_i/(1+\sigma^\top\sigma), q_4=(1-\sigma^\top\sigma)/(1+\sigma^\top\sigma)$ | `src/gmatutil/util/AttitudeConversionUtility.cpp:657-677` | AttitudeConversionUtility |
| 四元数→MRP：$\sigma_i=q_i/(1+q_4)$ | `src/gmatutil/util/AttitudeConversionUtility.cpp:694-709` | AttitudeConversionUtility |
| 角速度→欧拉角率：$\dot\theta=S^{-1}\omega$（12 分支，奇点 $s_2/c_2=0$） | `src/gmatutil/util/AttitudeConversionUtility.cpp:732-918` | AttitudeConversionUtility |
| 欧拉角率→角速度：$\omega=S\dot\theta$（12 分支） | `src/gmatutil/util/AttitudeConversionUtility.cpp:941-1047` | AttitudeConversionUtility |
| 欧拉轴/角→DCM：$R=cI+(1-c)\hat e\hat e^\top-s[\hat e]_\times$ | `src/gmatutil/util/AttitudeConversionUtility.cpp:1064-1074` | AttitudeConversionUtility |
| DCM→欧拉轴/角：$\theta=\mathrm{acos}(\tfrac12(\mathrm{tr}R-1))$，$|\sin\theta|<1e-14$ 截断 | `src/gmatutil/util/AttitudeConversionUtility.cpp:1091-1121` | AttitudeConversionUtility |
| 姿态状态类型枚举（四元数/DCM/欧拉角/MRP + 角速度/欧拉角率） | `src/base/attitude/Attitude.hpp:58-73` | Attitude |
| 初始化统一表示：$R_{Bi}=dcm,\ \omega_{IBi}=angVel$，类型切 DCM | `src/base/attitude/Attitude.cpp:658-746` | Attitude |
| 惰性求值协议：Initialize→Compute→换算返回 | `src/base/attitude/Attitude.cpp:864-1078` | Attitude |
| 表示同步链 `UpdateState`（MRP→四元数→DCM→欧拉角…） | `src/base/attitude/Attitude.cpp:3609-3725` | Attitude |
| 校验：$|\mathbf q|\ge1e-10$、欧拉中角奇点 $1e-10$、DCM 正交 $1e-14$ | `src/base/attitude/Attitude.cpp:3385-3596`；`GmatConstants.hpp:236-246` | Attitude |
| B→I 旋转矩阵：$[M]^\top=dcm^\top$ 及其状态偏导 | `src/base/attitude/Attitude.cpp:4056-4104` | Attitude |
| Spinner 自旋：$R_{BI}(t)=R_{\hat e}(\omega\Delta t)R_{BI}(t_0)$，增量历元 | `src/base/attitude/Spinner.cpp:214-252`（初值 L147-181） | Spinner |
| PrecessingSpinner 3-1-3：$R=R_3(\psi)R_1(\theta)R_3(\phi)R_{init}$ | `src/base/attitude/PrecessingSpinner.cpp:236-279` | PrecessingSpinner |
| PrecessingSpinner 角速度：$\omega_{123}=(\dot\phi s_\theta s_\psi,\dot\phi s_\theta c_\psi,\dot\phi c_\theta+\dot\psi)$，$\omega_{xyz}=R_{Bb}\omega_{123}$ | `src/base/attitude/PrecessingSpinner.cpp:282-298` | PrecessingSpinner |
| 四元数运动学解析解：$q(t)=(\cos\frac{\omega\Delta t}{2}I+\frac1\omega\sin\frac{\omega\Delta t}{2}\Omega)q_0$ | `src/base/attitude/ThreeAxisKinematic.cpp:214-218`（Ω）、`304-360`（传播） | ThreeAxisKinematic |
| 坐标系固定：$R_{BI}=R_{CS}^\top$，$[\tilde\omega]_\times=-\dot R_{CS}^\top R_{BI}$ | `src/base/attitude/CSFixed.cpp:164-211` | CSFixed |
| LVLH 三轴：$\hat x=\hat r,\ \hat y=\hat h,\ \hat z=\hat x\times\hat y$ | `src/base/attitude/NadirPointing.cpp:328-356` | NadirPointing |
| 约束模式矢量（OrbitNormal/Velocity） | `src/base/attitude/NadirPointing.cpp:359-378` | NadirPointing |
| TRIAD：$\mathbf r_2=\widehat{V_1\times V_2},\ \mathbf r_3=\widehat{V_1\times(V_1\times V_2)}$，$R=\sum\mathbf s_i\mathbf r_i^\top$ | `src/base/attitude/NadirPointing.cpp:180-254`；`CommandableNadirPointing.cpp:1563-1637` | NadirPointing / CommandableNadirPointing |
| 对地指向合成：$R_{BI}=(R_{I\gets LVLH}R_{LVLH\gets B})^\top$ | `src/base/attitude/NadirPointing.cpp:381-386`；`CommandableNadirPointing.cpp:1402-1407` | NadirPointing / CommandableNadirPointing |
| LVLH 偏导：$\partial\hat x/\partial r=(I-\hat x\hat x^\top)/|r|$、链式 $\partial\hat y/\partial r$、$\partial\hat z/\partial r$ | `src/base/attitude/NadirPointing.cpp:628-737`；`CommandableNadirPointing.cpp:1163-1274` | NadirPointing / CommandableNadirPointing |
| 命令模式可设：四元数/DCM/对准矢量任务段内改写 | `src/base/attitude/CommandableNadirPointing.cpp:372-646` | CommandableNadirPointing |
| AEM 读取：$dcm=\mathrm{reader.GetState}(t)$ | `src/base/attitude/CCSDSAttitude.cpp:201-213` | CCSDSAttitude |
| SPICE CK：$dcm,\omega=\mathrm{GetTargetOrientation}(scName,naifId,refFrameNaifId,t)$ | `src/base/attitude/SpiceAttitude.cpp:789-801`（装配 L205-296） | SpiceAttitude |
| GSS 移植四元数→DCM 显式展开（9 元素公式） | `src/gmatutil/util/AttitudeUtil.cpp:153-190` | GmatAttUtil |
| GSS 移植通用 DCM→欧拉角（模 3 符号技巧） | `src/gmatutil/util/AttitudeUtil.cpp:76-143` | GmatAttUtil |
| float 四元数乘法 AddQuats 与每 97 步重归一化 | `src/gmatutil/util/AttitudeUtil.cpp:437-469` | FloatAttUtil |
| 参数求值：$R_{BI}(t_{sc})$，`Evaluate()→mSpacecraft->GetAttitude(epoch)` | `src/base/parameter/AttitudeRmat33.cpp:88-92`（引用链 `AttitudeData.hpp:57,72`；`AttitudeData.cpp:120`） | AttitudeRmat33 / AttitudeData |
| 力模型接口：`Spacecraft::GetAttitude→attitude->GetCosineMatrix` | `src/base/spacecraft/Spacecraft.cpp:1766-1779` | Spacecraft（引用） |
| SRP 用姿态旋转日向矢量到本体系 | `src/base/forcemodel/SolarRadiationPressure.cpp:3093-3119` | SolarRadiationPressure（引用） |
