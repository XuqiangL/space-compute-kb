# 第8章 引力场模型数学

> 本章是《公式与模型深度解析》系列第 8 章，把 GMAT 引力模型家族的全部数学公式从源码中逐条提炼并深讲。范围：`src/base/forcemodel/` 下引力相关——`PointMassForce.{hpp,cpp}`（点质量加速度、间接项、时间雅可比、STM 的 A-tilde）、`harmonic/Harmonic.{hpp,cpp}`（Pines 递推、归一化勒让德、`CalculateField`）、`harmonic/HarmonicGravity.{hpp,cpp}`（球谐引擎 + 固体潮/极潮）、`HarmonicField.{hpp,cpp}`（度/阶截断与坐标系）、`GravityField.{hpp,cpp}`（JGM/EGM 系数读取、满 360×360、旋转链）、`GravityBase.{hpp,cpp}`（仅标记基类，无数学公式）；以及 `plugins/PolyhedronGravityPlugin/src/base/gravitymodel/`（Werner-Scheeres 多面体引力：边/面求和、立体角、变分项）与 `PolyhedronBody` 几何预处理。
>
> 类体系、继承链与参数表见 [第6章](../CH06-dynamics.md)（`PhysicalModel → GravityBase → HarmonicField → GravityField`，球谐纯数值内核 `Harmonic → HarmonicGravity`）；多面体插件的工厂与参数类见 [第14章](../CH14-plugins-b.md)。本章**只讲公式**：每个条目给出从代码提炼的 LaTeX 公式、经过 read 验证的代码位置、物理背景与逐行注释的代码片段，不重复第 6/14 章的架构叙述。
>
> 单位约定（与全库一致）：内部状态为 km / km·s⁻¹；`mu`（μ）为 km³·s⁻²；`FieldRadius`（a，参考赤道半径）为 km；球谐系数为**全归一化**（fully normalized，EGM96 约定）；潮汐/极移输入来自 EOP 文件。所有代码行号均已用 read 工具核对。

## 一、公式总图与文件清单

```
引力计算数据流（加速度单位 km/s²）：
  状态（inputCS，惯性 MJ2000Eq）
    │  GravityField::Calculate        ┌─ Harmonic::CalculateField（Pines 递推）┐
    │  cc.Convert → 固连系 tmpState   ├─ HarmonicGravity::CalculatePointField   ├→ rotacc, rotgrad（固连系）
    │  └→ CalculateFullField(度,阶,潮汐) └─ IncrementSolidTide/EarthTide（ΔC,ΔS）┘
    │  InverseRotate(rotMatrix, rotacc, acc)      acc = rotᵀ·rotacc
    │  grad = rotᵀ·rotgrad·rot                    （相似变换回惯性系）
    ▼
  ODEModel::GetDerivatives：对 forceList 逐力 deriv[j] += ddt[j]（线性叠加）
    └  PointMassForce（每摄动天体一个实例）：a = μ·(r_bb−r_sat)/|r_bb−r_sat|³ − μ·r_bb/|r_bb|³
  PolyhedronGravityModel（插件，独立于球谐链）：
    a = (G·10⁹·ρ)·(−Σ_edges E_e·r_e·L_e + Σ_faces F_f·R₁·ω_f)，Dᵀ 转回惯性系
```

涉及文件（行号均为 read 验证后的引用基准）：

| 文件 | 内容 | 公式条数 |
| --- | --- | --- |
| src/base/forcemodel/PointMassForce.hpp/.cpp | 点质量引力（含间接项/时间雅可比/A-tilde） | 5 |
| src/base/forcemodel/harmonic/Harmonic.hpp/.cpp | Pines 均匀表示递推内核 | 9 |
| src/base/forcemodel/harmonic/HarmonicGravity.hpp/.cpp | 球谐引擎 + 固体潮/频率潮/极潮 | 8 |
| src/base/forcemodel/HarmonicField.hpp/.cpp | 度/阶截断、坐标系与 EOP | 2 |
| src/base/forcemodel/GravityField.hpp/.cpp | 系数读取、旋转链、原点偏移、缓存 | 6 |
| src/base/forcemodel/GravityBase.hpp/.cpp | 标记基类（`GravityBaseParamCount = PhysicalModelParamCount`，`.hpp:59`），无数学公式 | — |
| plugins/PolyhedronGravityPlugin/src/base/gravitymodel/PolyhedronGravityModel.hpp/.cpp | Werner-Scheeres 多面体引力 | 6 |
| plugins/PolyhedronGravityPlugin/src/base/gravitymodel/PolyhedronBody.hpp/.cpp | 多面体几何预处理（法向/内心/边） | 3 |
| application/data/gravity/earth/EGM96low.cof 等 | .cof 位势系数数据（POTFIELD/RECOEF） | 样例 |
| application/data/gravity/luna/grgm900c.tide | .tide 潮汐 Love 数数据 | 样例 |

---

## 二、PointMassForce —— 点质量引力与第三体摄动

### 牛顿点质量加速度 a = −μr/r³

- **公式**：对航天器相对引力体的位置 $\vec r = \vec r_{body} - \vec r_{sat}$，加速度

$$ \ddot{\vec r} = -\frac{GM\,\vec r}{r^{3}} = -\mu\,\frac{\vec r}{|\vec r|^3} $$

（源码文档注释，`PointMassForce.cpp:312-313` 的 Doxygen 公式；实现见下）。

- **代码位置**：`src/base/forcemodel/PointMassForce.cpp:492-521`（`GetDerivatives` 主循环），`PointMassForce.hpp:155`（成员 `mu`，注释 `G*M`）。
- **深度讲解**：`GetDerivatives` 对每个航天器（`satCount` 个）计算相对位置 `relativePosition = rv − state[i6..i6+2]`（第492-494行，`rv` 是"引力体 − 力模型原点"的位置），然后：

```cpp
496:            r3 = relativePosition[0]*relativePosition[0] +
497:                 relativePosition[1]*relativePosition[1] +
498:                 relativePosition[2]*relativePosition[2];
500:            radius = sqrt(r3);
501:            r3 *= radius;            // r3 = |r|³，纯乘法避免 pow 调用
502:            mu_r = mu / r3;
...
519:               deriv[3 + i6] = relativePosition[0] * mu_r - a_indirect[0];
520:               deriv[4 + i6] = relativePosition[1] * mu_r - a_indirect[1];
521:               deriv[5 + i6] = relativePosition[2] * mu_r - a_indirect[2];
```

- 第496-501行：先算 $r^2$，乘 $\sqrt{r^2}$ 得 $r^3$——省一次 `pow`，且避免大指数下的舍入差异。
- 第519-521行：`d(vel)/dt = (μ/r³)·r − a_indirect`。`relativePosition` 定义为"引力体 − 航天器"（第492-494行），所以 `(μ/r³)·relativePosition` 就是指向引力体的加速度，即 $-\mu \vec r/r^3$ 的另一种写法；`a_indirect` 见下一条目。位置导数 `deriv[i6..i6+2] = 0`（第532行），运动学项 `d(pos)/dt = v` 由 `ODEModel` 统一填充（见 [第6章](../CH06-dynamics.md) 第3380-3391行的容器实现）。
- 物理背景：这是二体问题的标准加速度。当力模型原点就是引力体时退化为纯二体；当原点不是引力体（如以地心为原点摄动月球引力）时需扣除间接项。第三体摄动的"累加"语义：`ODEModel` 的 `forceList` 里对每个摄动天体挂一个 `PointMassForce`（[第6章](../CH06-dynamics.md) 第250行），`ODEModel::GetDerivatives` 第3262-3318行把各力导数逐元素累加进 `deriv`，即 $\vec a_{total}=\vec a_{central}+\sum_i \vec a_i$，是纯线性叠加。`mu` 在 `Initialize` 里取自 `body->GetGravitationalConstant()`（第249行）。

### 第三体间接项 a_indirect = μ·r_bb/|r_bb|³

- **公式**：令 $\vec r_{bb}$ = 引力体位置 − 力模型原点位置（`rv`），则原点自身被该体吸引的加速度为

$$ \vec a_{indirect} = \mu\,\frac{\vec r_{bb}}{|\vec r_{bb}|^3} $$

实际施加的加速度 $\vec a = \mu(\vec r_{bb}-\vec r_{sat})/|\vec r_{bb}-\vec r_{sat}|^3 - \vec a_{indirect}$（第519-521行已减去）。

- **代码位置**：`src/base/forcemodel/PointMassForce.cpp:440-453`（`rbb3`/`mu_rbb`/`a_indirect` 预计算）。
- **深度讲解**：

```cpp
442:       rbb3 = rv[0]*rv[0]+rv[1]*rv[1]+rv[2]*rv[2];
443:       if (rbb3 != 0.0)
444:       {
446:          rbb3 = sqrt(rbb3 * rbb3 * rbb3);      // |r_bb|³
447:          mu_rbb = mu / rbb3;
448:          a_indirect[0] = mu_rbb * rv[0];       // μ·r_bb/|r_bb|³
449:          a_indirect[1] = mu_rbb * rv[1];
450:          a_indirect[2] = mu_rbb * rv[2];
451:       }
```

- 物理背景：力模型坐标系以 `forceOrigin`（如地心、日心）为原点。若某 `PointMassForce` 的引力体不在原点（例如以月球为中心天体、力模型原点设在地心），那么"原点"本身也在被该体加速；积分的是相对运动，必须把原点的牵连加速度扣掉，否则得到的相对加速度是错的。这正是 N 体相对运动方程里的"间接项"：$\ddot{\vec r}_{rel} = -\mu(\vec r_{sat}-\vec r_{bb})/|\cdot|^3 - (-\mu\vec r_{bb}/|\vec r_{bb}|^3)$。
- 实现要点：`rbb3==0`（原点即引力体）时 `a_indirect=0`（第452-453行），自动退化为纯二体；间接项只需每步算一次（在航天器循环外，第442-453行），多个航天器共享。
- 注意 `GetDerivativesForSpacecraft`（第793-883行）是同一公式的快捷版本：`relativePosition = −state`（第854-856行，状态相对原点），`dv[3..5] = (μ/r³)·(−state) − a_indirect`（第866-868行）。

### 点质量时间雅可比 ∂a/∂t

- **公式**：加速度显式依赖时间仅通过运动的天体位置 $\vec r_{bb}(t)$（与 $\vec r_{bb}-\vec r_{sat}$），故

$$ \frac{\partial a_i}{\partial t} = \mu\sum_{j=1}^{3}\Big[\frac{\delta_{ij}-3\hat u^{rel}_i\hat u^{rel}_j}{r_{rel}^3} - \frac{\delta_{ij}-3\hat u^{bb}_i\hat u^{bb}_j}{r_{bb}^3}\Big]\,v^{bb}_j $$

其中 $\vec u^{rel}=(\vec r_{bb}-\vec r_{sat})/r_{rel}$、$\vec u^{bb}=\vec r_{bb}/r_{bb}$，$v^{bb}_j$ 是天体速度分量。

- **代码位置**：`src/base/forcemodel/PointMassForce.cpp:387-438`（`fillTimeJacobian` 分支）。
- **深度讲解**：

```cpp
389:          Real rvmag = sqrt(rv[0]*rv[0]+rv[1]*rv[1]+rv[2]*rv[2]);
391:          rvunit[0] = rv[0] / rvmag; ...              // û_bb
398:          rvrel[0] = rv[0] - state[0]; ...            // r_bb − r_sat
402:          Real rvrelmag = sqrt(...); rvrelunit[...];  // û_rel
414:          if (rvmag != 0.0)
415:          {
417:             for (Integer i = 0; i < 3; ++i)
418:                for (Integer j = 0; j < 3; ++j)
419:                {
421:                   if (i == j)
422:                      timeJacElement = (1.0 - 3.0*rvrelunit[i]*rvrelunit[j]) / pow(rvrelmag,3)
423:                                     - (1.0 - 3.0*rvunit[i]*rvunit[j]) / pow(rvmag,3);
428:                   else
429:                      timeJacElement = (-3.0*rvrelunit[i]*rvrelunit[j]/pow(rvrelmag,3))
431:                                    - (-3.0*rvunit[i]*rvunit[j]) / pow(rvmag,3);
434:                   timeJacobian[i + 3] += mu * timeJacElement * rv[j + 3];
435:                }
436:             }
```

- 数学来源：$\partial(\mu x_j/r^3)/\partial x_i = \mu(\delta_{ij}-3\hat u_i\hat u_j)/r^3$，这正是第422-431行的结构（对角 $i=j$ 带 $\delta_{ij}$ 项，非对角只有 $-3\hat u_i\hat u_j$）。两项相减 = 相对项对 $\vec r_{bb}$ 的偏导 − 间接项对 $\vec r_{bb}$ 的偏导；再点乘天体速度 $v^{bb}_j$（第434行 `rv[j+3]`，`rv[3..5]` 是天体速度）得到 $\partial a_i/\partial t$，写入 `timeJacobian[i+3]`（下标 +3 表示加速度分量）。
- 用途：时间雅可比是变分方程/协方差传播中"显式时间依赖"部分（$\dot\Phi = \tilde A\Phi$ 之外还需 $\partial a/\partial t$ 项），由 `ODEModel` 汇总（`ODEModel.cpp:3336`，见 [第6章](../CH06-dynamics.md) 第125-135行）。第409-410行先把本行清零，第414行 `rvmag != 0` 判定：原点即引力体时跳过（纯二体时间无关）。

### 点质量 A-tilde（∂a/∂r）与状态转移矩阵

- **公式**：位置部分（速度部分为 $I_{3\times3}$）的雅可比为

$$ \tilde A_{(3+i,\,j)} = \frac{\mu}{r^3}\left(\delta_{ij} - 3\,\frac{r_i r_j}{r^2}\right) ,\qquad i,j = 1..3 $$

其余块为零；$\dot\Phi = \tilde A\,\Phi$。

- **代码位置**：`src/base/forcemodel/PointMassForce.cpp:606-636`（注释 "Math spec, equ 6.69"）；`PointMassForce.cpp:638-654` 注释说明矩阵乘法上移到 `ODEModel`。
- **深度讲解**：

```cpp
608:            ix = stmRowCount * 3;
609:            aTilde[ix] = - mu_r + 3.0 * mu_r / (radius*radius) *
610:                             relativePosition[0] * relativePosition[0];
612:            aTilde[ix+1] = 3.0 * mu_r / (radius*radius) *
613:                             relativePosition[0] * relativePosition[1];
...
618:            ix = stmRowCount * 4;
619:            aTilde[ix] = 3.0 * mu_r / (radius*radius) *
620:                             relativePosition[1] * relativePosition[0];
622:            aTilde[ix+1] = - mu_r + 3.0 * mu_r / (radius*radius) *
623:                             relativePosition[1] * relativePosition[1];
...
635:            aTilde[ix+2] = - mu_r + 3.0 * mu_r / (radius*radius) *
636:                             relativePosition[2] * relativePosition[2];
```

- 第609-636行：对角元 `−μ/r³ + 3μ·r_i²/r⁵`，非对角 `3μ·r_i r_j/r⁵`，即 $(\mu/r^3)(\delta_{ij}-3\hat r_i\hat r_j)$。`aTilde` 是 $N\times N$ 全尺寸矩阵（`stmRowCount` 来自航天器 `FullSTMRowCount`，第596行），只填左下 6×6 的 (3:6,0:3) 块，其余置零（第599-604行）。
- 第655-666行把 `aTilde` 直接拷入 `deriv[s6+element]` / `deriv[a6+element]`——注意这里填的是 $\tilde A$ **本身**而非 $\tilde A\Phi$：注释（第638-654行）说明 $\dot\Phi=\tilde A\Phi$ 的乘法已移到 `ODEModel`，由它管理 STM 上半部分（位置行）的正确填充。用途：状态转移矩阵（STM）与 A-Matrix 的变分传播，供估计（Batch/UKF）与协方差分析使用；点质量的 $\tilde A$ 是球谐场梯度（见 `Harmonic` 梯度条目）在 $n=0$（无谐波）时的特例。

### 重力梯度力矩（点质量）

- **公式**：航天器质心处的重力梯度力矩

$$ \vec T = \frac{3\mu}{r^3}\,\hat r \times (I\,\hat r) $$

其中 $\hat r = -\hat n$（`nadirVec`，由航天器指向天体），$I$ 为系统惯量张量。

- **代码位置**：`src/base/forcemodel/PointMassForce.cpp:1283-1292`（`GetTorquesForSpacecraft`）。
- **深度讲解**：

```cpp
1283:   dist = GmatMathUtil::Sqrt(satState[0]*satState[0] +
1284:      satState[1]*satState[1] + satState[2]*satState[2]);
1287:   Rvector3 nadirVec(-satState[0] / dist, -satState[1] / dist,
1288:      -satState[2] / dist);                       // 指向天体的单位向量 = −r̂
1291:   Rvector3 gravityTorque = Cross(((3.0 * body->GetGravitationalConstant() /
1292:      pow(dist, 3.0)) * nadirVec), scMOITensor * nadirVec);
```

- 第1283-1288行：`dist=|r|`，`nadirVec = −r̂`（由航天器指向引力体的单位向量）。
- 第1291-1292行：$T=(3\mu/r^3)(-\hat r)\times\big(I(-\hat r)\big)=(3\mu/r^3)\,\hat r\times(I\hat r)$。这就是"哑铃模型"重力梯度力矩：惯量主轴偏离重力梯度方向时产生恢复力矩，是低轨航天器姿态稳定的主要机制之一。`scMOITensor` 为航天器系统惯量（`GetSystemMOI`，第1246行）。`GravityField` 同名方法公式相同（见后文），`ODEModel::GetTorquesForSpacecraft` 对每个点质量累加（`ODEModel.cpp:6577-6579`）。

---

## 三、Harmonic —— Pines 均匀表示递推内核

### 球谐引力势展开（物理背景）

- **公式**：中心天体引力势的球谐展开（全归一化系数）

$$ U(r,\phi,\lambda) = \frac{\mu}{r}\sum_{n=0}^{\infty}\sum_{m=0}^{n}\Big(\frac{a}{r}\Big)^{n}\,\bar P_{nm}(\sin\phi)\big[\bar C_{nm}\cos(m\lambda)+\bar S_{nm}\sin(m\lambda)\big] $$

$n$ 为**度**（degree），$m$ 为**阶**（order）；$m=0$ 的项只含 $\bar C_{n0}$（$\bar S_{n0}\equiv0$），称**带谐**（zonal，如 $J_n=-\bar C_{n0}$，$J_2=-\bar C_{20}$）；$m>0$ 称**田谐**（tesseral，$m=n$ 时称扇谐 sectorial）。加速度 $\vec a=\nabla U$。

- **代码位置**：递推出处见 `src/base/forcemodel/harmonic/Harmonic.hpp:31-51`（引用 Lundberg-Schutz 1988、Heiskanen-Moritz 1967、Pines 1973 三篇文献）；计算入口 `Harmonic::CalculateField`，`harmonic/Harmonic.cpp:91`。
- **深度讲解**：GMAT 不用"先算非归一化 $P_{nm}$ 再乘归一化因子"的朴素做法，而是把**归一化吸收进递推系数**（`A` 数组与 `N1/N2`），配合 Pines 1973 的"均匀表示"（uniform representation）：将 $\cos(m\lambda),\sin(m\lambda)$ 换成 $(s+it)^m$ 的实部/虚部（$s=x/r,\,t=y/r,\,u=z/r$ 为方向余弦）。关键收益有二：
  1. **极点无奇性**：经典递推含 $1/\cos\phi$（或 $1/\sqrt{x^2+y^2}$）因子，在极区退化；方向余弦表示把 $(\rho_{xy}/r)^m$ 吸收进递推，全场正则。
  2. **数值稳定**：全归一化使 $A[n][m]\sim O(1)$，避免 360 阶递推中量级爆炸与灾难性消去；$(\rho_{xy}/r)^m$ 与 $\rho^n=(a/r)^n$（高空快速衰减）分开累加，避免中间量过大。
  第6章对类结构已有叙述（[CH06](../CH06-dynamics.md) 第186-191行），本章聚焦各条递推公式本身。

### 场点几何量与方向余弦 (r, s, t, u)

- **公式**：对固连系场点 $\vec r=(x,y,z)$，

$$ r=|\vec r|,\qquad s=\frac{x}{r},\quad t=\frac{y}{r},\quad u=\frac{z}{r}=\sin\phi $$

- **代码位置**：`src/base/forcemodel/harmonic/Harmonic.cpp:95-100`。
- **深度讲解**：`s,t,u` 是 Pines 递推的基本自变量（单位方向余弦）。`XS`（第95行）在需要梯度时取 2：因为二阶偏导需要 $\bar P$ 的 $n+2,\,m+2$ 项，数组（及后面所有递推）都要多算两"层"（`AllocateArray(..., NN, 3)` 的 excess 参数，`Harmonic.cpp:267-272`）。第100行注释 `u = sin(phi), phi = geocentric latitude`——地心纬度 $\phi$ 的正弦就是 $z/r$。

```cpp
97:    Real r = sqrt (pos[0]*pos[0] + pos[1]*pos[1] + pos[2]*pos[2]);    // Naming scheme from ref [3]
98:    Real s = pos[0]/r;
99:    Real t = pos[1]/r;
100:   Real u = pos[2]/r; // sin(phi), phi = geocentric latitude
```

### 归一化派生勒让德递推（对角项 + 列填充）

- **公式**：$A[n][m]$ 是归一化派生关联勒让德多项式在 $u$ 处的值。对角项（初值 $A[0][0]=1$）：

$$ A[n][n] = \sqrt{\frac{2n+1}{2n}}\,A[n-1][n-1] $$

次对角与列填充（Lundberg-Schutz 递推，Table 2 Row I）：

$$ A[n+1][n] = u\sqrt{2n+3}\,A[n][n] ,\qquad A[n][m] = u\,N_1[n][m]\,A[n-1][m] - N_2[n][m]\,A[n-2][m] $$

$$ N_1[n][m]=\sqrt{\frac{(2n+1)(2n-1)}{(n-m)(n+m)}},\qquad N_2[n][m]=\sqrt{\frac{(2n+1)(n-m-1)(n+m-1)}{(2n-3)(n+m)(n-m)}} $$

- **代码位置**：对角项 `Harmonic.cpp:280-282`；次对角 `Harmonic.cpp:104-106`；列填充 `Harmonic.cpp:109-112`；`N1/N2` 预计算 `Harmonic.cpp:317-325`。
- **深度讲解**：

```cpp
280:    A[0][0] = 1.0;
281:    for (Integer n=1;  n<=NN+2;  ++n)
282:       A[n][n] = sqrt (Real(2*n+1)/Real(2*n)) * A[n-1][n-1];
...
104:    A[1][0] = u*sqrt(Real(3.0));
105:    for (Integer n=1;  n<=NN+XS && n<=nn+XS;  ++n)
106:       A[n+1][n] = u*sqrt(Real(2*n+3))*A[n][n];
...
109:    for (Integer m=0;  m<=MM+XS && m<=mm+XS;  ++m)
110:       {
111:       for (Integer n=m+2;  n<=NN+XS && n<=nn+XS;  ++n)
112:          A[n][m] = u * N1[n][m] * A[n-1][m] - N2[n][m] * A[n-2][m];
```

- 第280-282行：对角项是 $\bar P_{nn}(\sin\phi)$ 在 $u=1$ 处的值——它们只依赖 $n$，与场点无关，故在 `Allocate()` 里一次性算好（只算一次，而非每步递推）。
- 第104-106行：次对角 $A[m+1][m]$ 需要 $\bar P_{mm}$ 的相邻项，用 $u\sqrt{2m+3}$ 递推（这是归一化 Legendre 的升阶关系 $P_{m+1,m}\propto u\,P_{m,m}$ 的归一化版本）。
- 第111-112行：列填充递推沿固定 $m$、递增 $n$ 进行——只依赖同列前两行，是"三点递推"；`N1/N2`（第321-323行）把归一化系数 $\sqrt{(2n+1)(2n-1)/((n-m)(n+m))}$ 等吸收进递推，使 $A$ 的幅值保持在 $O(1)$，这是 360 阶能稳定递推的关键。注意循环上限同时受数组容量（`NN+XS`）与调用方请求的截断（`nn+XS`）约束。

### 归一化因子 V(n,m)

- **公式**：全归一化 Legendre 的归一化因子

$$ V(n,0)=\sqrt{2n+1},\qquad V(n,m)=\sqrt{\frac{2(2n+1)(n-m)!}{(n+m)!}}\ (m>0),\qquad \bar P_{nm}=V(n,m)\,P_{nm} $$

- **代码位置**：`src/base/forcemodel/harmonic/Harmonic.cpp:284-297`。
- **深度讲解**：

```cpp
289:    for (Integer n=0;  n<=NN+2;  ++n)
290:       {
291:       V[n][0] = sqrt(Real(2*(2*n+1)));   // Temporary, to make following loop work
292:        for (Integer m=1;  m<=n+2 && m<=MM+2;  ++m)
293:          {
294:          V[n][m] = V[n][m-1] / sqrt(Real((n+m)*(n-m+1)));
295:          }
296:       V[n][0] = sqrt(Real(2*n+1));       // Now set true value
297:       }
```

- 第291行先用"临时值" $V=\sqrt{2(2n+1)}$ 播种递推（对应 $m=0$ 的公式 $\sqrt{2(2n+1)}$ 形式，见 `Harmonic.hpp:286` 注释），第294行用相邻阶关系 $V(n,m)=V(n,m-1)/\sqrt{(n+m)(n-m+1)}$ 逐阶外推（避免每阶算一次阶乘），第296行再把 $V[n][0]$ 改回真值 $\sqrt{2n+1}$。验证：$V(n,1)=\sqrt{2(2n+1)}/\sqrt{n(n+1)}$，与 $m=1$ 的定义一致。
- 用途：① 递推初值与归一化校正；② 读取**非归一化**系数文件时，`LM_SetCoefficients` 用 `c /= V[n][m]` 把系数归一化（见 HarmonicGravity 条目）；③ 文件自带的归一化标志（POTFIELD 行第4个数）决定是否做此换算。

### Re/Im 递推（(s+it)^m 的实部与虚部）

- **公式**：令 $s+it = \rho_{xy}e^{i\lambda}/r$，则

$$ \mathrm{Re}_m = \Re\big[(s+it)^m\big] = s\,\mathrm{Re}_{m-1} - t\,\mathrm{Im}_{m-1},\qquad \mathrm{Im}_m = \Im\big[(s+it)^m\big] = s\,\mathrm{Im}_{m-1} + t\,\mathrm{Re}_{m-1} $$

初值 $\mathrm{Re}_0=1,\ \mathrm{Im}_0=0$。与 $\cos(m\lambda),\sin(m\lambda)$ 只差因子 $(\rho_{xy}/r)^m$。

- **代码位置**：`src/base/forcemodel/harmonic/Harmonic.cpp:113-115`（注释 "Ref.[3], Eq.(24)"）。
- **深度讲解**：`Re[m]/Im[m]` 用复数乘法 $(s+it)^m=(s+it)(s+it)^{m-1}$ 的实虚部分解递推，每阶一次复数乘（4 次实数乘加），比调用三角函数快得多，且与勒让德递推共用 $s,t,u$——这正是 Pines"均匀表示"的核心：把经度部分 $(e^{im\lambda})$ 和纬度部分 $\bar P_{nm}(u)$ 统一成关于 $(x,y,z)$ 的齐次多项式（solid harmonic），全场无 $\lambda$ 处的奇性。`m=0` 时 $\mathrm{Re}_0=1,\mathrm{Im}_0=0$（第114-115行的三元表达式）。

### rho 递推（Pines Eq.26）

- **公式**：$\rho = a/r$（$a=$ `FieldRadius`），以及带符号的递推初值

$$ \rho_{n+1}^{(0)} = -\frac{Factor}{r}\,\rho = \frac{\mu}{r}\,\frac{a}{r},\qquad \rho_{n+2}^{(0)} = \rho_{n+1}^{(0)}\rho,\qquad \rho_{n+1}^{(k)}=\rho_{n+1}^{(k-1)}\,\rho $$

`Factor = -μ`（重力；磁场时为 1，`Harmonic.hpp:92`）。

- **代码位置**：`src/base/forcemodel/harmonic/Harmonic.cpp:120-122`（初值）与 `Harmonic.cpp:137-140`（每度累乘）。
- **深度讲解**：

```cpp
120:    Real rho = FieldRadius/r;
121:    Real rho_np1 = -Factor/r * rho;   // rho(0) ,Ref[3], Eq 26 , factor = mu for gravity
122:    Real rho_np2 = rho_np1 * rho;
...
137:    for (Integer n=1;  n<=NN && n<=nn;  ++n)
138:       {
139:       rho_np1 *= rho;
140:       rho_np2 *= rho;
```

- 由于 `Factor=-μ`，第121行实为 $+\mu a/r^2$；每进一度 $n$ 乘一个 $\rho=a/r$（第139-140行），故第 $n$ 度时 $\rho_{n+1}=\mu a^{n+1}/r^{n+2}$。加速度的度 $n$ 项按 $\mu(a/r)^n/r$ 衰减（$=\mu a^n/r^{n+2}$），所以 `rr = rho_np1/FieldRadius = μa^n/r^{n+2}`（第214行）正是第 $n$ 度加速度的**量纲前置因子**（km/s²），与勒让德求和项相乘即得该度加速度贡献。
- 数值注意：$\rho<1$（场点在参考球外）时逐度乘 $\rho$ 自动衰减，高空收敛快；即使 360 阶，$\rho^n$ 与 $A\sim O(1)$、$(\bar C,\bar S)\sim 10^{-3}\sim10^{-7}$ 相乘也在浮点安全范围。

### 系数组合 D/E/F 与一阶和（Pines Eq.27/30）

- **公式**：对每对 $(n,m)$，用归一化系数 $\bar C_{nm},\bar S_{nm}$ 与 $\mathrm{Re}/\mathrm{Im}$ 组合

$$ D_m = \sqrt2\big(\bar C_{nm}\mathrm{Re}_m+\bar S_{nm}\mathrm{Im}_m\big),\quad
   E_m = \sqrt2\big(\bar C_{nm}\mathrm{Re}_{m-1}+\bar S_{nm}\mathrm{Im}_{m-1}\big),\quad
   F_m = \sqrt2\big(\bar S_{nm}\mathrm{Re}_{m-1}-\bar C_{nm}\mathrm{Im}_{m-1}\big) $$

（$m=0$ 时 $E=F=0$），再累加一阶和

$$ sum_1=\sum_m m\,A_{nm}\,E_m,\quad sum_2=\sum_m m\,A_{nm}\,F_m,\quad sum_3=\sum_m V_{01}\,A_{n,m+1}\,D_m,\quad sum_4=\sum_m V_{11}\,A_{n+1,m+1}\,D_m $$

其中 $V_{01}=\sqrt{(n-m)(n+m+1)}$、$V_{11}=\sqrt{(2n+1)(n+m+2)(n+m+1)/(2n+3)}$（$m=0$ 时各除以 $\sqrt2$）。最终按 Pines Eq.30 累加速度系数：

$$ a_1=\sum_n \frac{\rho_{n+1}}{a}\,sum_1,\quad a_2=\sum_n \frac{\rho_{n+1}}{a}\,sum_2,\quad a_3=\sum_n \frac{\rho_{n+1}}{a}\,sum_3,\quad a_4=-\sum_n \frac{\rho_{n+1}}{a}\,sum_4 $$

- **代码位置**：`Harmonic.cpp:157-171`（D/E/F 与 sum1..sum4）、`Harmonic.cpp:213-218`（`rr` 与 a1..a4 累加）；`VR01/VR11` 定义 `Harmonic.cpp:302-303`。
- **深度讲解**：

```cpp
157:          Real Cval = Cnm (jday,n,m);
158:          Real Sval = Snm (jday,n,m);
159:          // Pines Equation 27 (Part of)
160:          Real D =            (Cval*Re[m]   + Sval*Im[m]) * sqrt2;
161:          Real E = m==0 ? 0 : (Cval*Re[m-1] + Sval*Im[m-1]) * sqrt2;
162:          Real F = m==0 ? 0 : (Sval*Re[m-1] - Cval*Im[m-1]) * sqrt2;
163:          // Correct for normalization
164:          Real Avv00 = A[n][m];
165:          Real Avv01 = VR01[n][m] * A[n][m+1];
166:          Real Avv11 = VR11[n][m] * A[n+1][m+1];
167:          // Pines Equation 30 and 30b (Part of)
168:          sum1 += m * Avv00 * E;
169:          sum2 += m * Avv00 * F;
170:          sum3 +=     Avv01 * D;
171:          sum4 +=     Avv11 * D;
...
214:       Real rr = rho_np1/FieldRadius;
215:       a1 += rr*sum1;
216:       a2 += rr*sum2;
217:       a3 += rr*sum3;
218:       a4 -= rr*sum4;
```

- 第160-162行：`sqrt2`（第136行）处理归一化约定中 $m=0$ 与 $m>0$ 的 $\sqrt2$ 因子差（全归一化定义里 $\bar P_{n0}$ 与 $\bar P_{nm}(m>0)$ 归一化不同），`E,F` 用 $m-1$ 阶的 Re/Im 是递推的相邻阶耦合，`m==0` 时置零（带谐无经度导数）。
- 第164-166行：`Avv01/Avv11` 把 $\bar P$ 的 $u$-导数（关联 $\bar P_{n,m\pm1}$）通过 $V_{01},V_{11}$ 表示——这是把"势对 $u$ 求导"转化为"对相邻阶勒让德求值"的归一化校正，见 VR 条目。
- 第168-171行：Pines Eq.30 的四个和分别对应加速度在"方向余弦基"下的四个分量生成元（$m E$ 项来自对经度角求导，$D$ 项来自对 $u$ 求导）。
- 第214-218行：乘以量纲前置因子 $rr=\rho_{n+1}/a=\mu a^n/r^{n+2}$ 累加；`a4` 带负号（第218行），因为 $u$-方向的贡献在 Pines 表示里与其它分量反号（Eq.30b 的符号约定）。

### 加速度合成（Pines Eq.31）

- **公式**：固连系加速度三分量

$$ \begin{pmatrix} a_x \\ a_y \\ a_z \end{pmatrix} = \begin{pmatrix} a_1+a_4\,s \\ a_2+a_4\,t \\ a_3+a_4\,u \end{pmatrix} $$

- **代码位置**：`src/base/forcemodel/harmonic/Harmonic.cpp:242-245`（注释 "Pines Equation 31"）。
- **深度讲解**：

```cpp
243:    acc[0] = a1+a4*s;
244:    acc[1] = a2+a4*t;
245:    acc[2] = a3+a4*u;
```

- 这是 Pines 均匀表示的最后一步：`a1,a2,a3` 是在"经度/纬度混合基"下的分量，`a4` 是 $u$-方向（极轴方向）分量的公共部分，乘方向余弦 $s,t,u$ 投影回笛卡尔分量。之所以能这样拆，是因为 $\partial U/\partial r$ 的径向部分与 $\partial U/\partial \phi$ 的经度部分在均匀表示里都归结为 $a_1..a_4$ 的线性组合。此 `acc` 在固连系中（`CalculateField` 的输入 `pos` 是固连系坐标），由 `GravityField::Calculate` 负责转回惯性系（见后文旋转链条目）。

### 梯度合成（Pines Eq.36/37）—— STM 用

- **公式**：势的二阶偏导（加速度的梯度 $\partial a_i/\partial r_j$）对角项

$$ g_{xx}=a_{11}+s^2a_{44}+\frac{a_4}{r}+2s\,a_{14},\quad g_{yy}=-a_{11}+t^2a_{44}+\frac{a_4}{r}+2t\,a_{24},\quad g_{zz}=a_{33}+u^2a_{44}+\frac{a_4}{r}+2u\,a_{34} $$

非对角 $g_{xy}=a_{12}+st\,a_{44}+s\,a_{24}+t\,a_{14}$，$g_{xz},g_{yz}$ 同理（第254-257行）。其中

$$ a_{11}=\sum_n \frac{\rho_{n+2}}{a^2}\,sum_{11},\ \ldots\ ,\ a_{44}=\sum_n \frac{\rho_{n+2}}{a^2}\,sum_{44} $$

$$ sum_{11}=\sum_m m(m-1)A_{nm}G_m,\quad sum_{12}=\sum_m m(m-1)A_{nm}H_m,\quad sum_{13}=\sum_m m\,A_{nm}V_{01}E_m,\ \ldots $$

$$ G_m=\sqrt2\big(\bar C_{nm}\mathrm{Re}_{m-2}+\bar S_{nm}\mathrm{Im}_{m-2}\big),\quad H_m=\sqrt2\big(\bar S_{nm}\mathrm{Re}_{m-2}-\bar C_{nm}\mathrm{Im}_{m-2}\big),\ (m>1) $$

- **代码位置**：`Harmonic.cpp:180-198`（G/H 与 sum11..sum44）、`Harmonic.cpp:219-230`（a11..a44 累加）、`Harmonic.cpp:246-258`（Eq.37 组装）。
- **深度讲解**：

```cpp
180:                Real G = m<=1 ? 0 : (Cval*Re[m-2] + Sval*Im[m-2]) * sqrt2;
181:                Real H = m<=1 ? 0 : (Sval*Re[m-2] - Cval*Im[m-2]) * sqrt2;
183:                Real Avv02 = VR02[n][m] * A[n][m+2];
184:                Real Avv12 = VR12[n][m] * A[n+1][m+2];
185:                Real Avv22 = VR22[n][m] * A[n+2][m+2];
190:                sum11 += m*(m-1) * Avv00 * G;
191:                sum12 += m*(m-1) * Avv00 * H;
192:                sum13 += m       * Avv01 * E;
193:                sum14 += m       * Avv11 * E;
...
198:                sum44 +=           Avv22 * D;
...
222:          a11 += rho_np2/FieldRadius/FieldRadius*sum11;
...
230:          a44 += rho_np2/FieldRadius/FieldRadius*sum44;
```

- 第180-181行：二阶经度导数需要 $m-2$ 阶的 Re/Im（$m\le1$ 置零，第179行注释 GMT-5295 曾把阈值从 `m<=2` 改为 `m<=1`）。
- 第183-185行：二阶 $u$-导数需要 $\bar P$ 的 $m+2$ 阶（$A[n][m+2]$ 等），经 $V_{02},V_{12},V_{22}$ 归一化校正（第304-306行定义）；这正是 `Allocate` 里 excess=3（多分配 3 层）的原因。
- 第190-198行：Pines Eq.36 的十个和（$sum_{11}$~$sum_{44}$，对称分量复用）。第186-187行的 NaN/Inf 防护把 $A[n][m+2]$ 的溢出置零（wcs 补丁）。
- 第222-230行：量纲前置因子现在是 $\rho_{n+2}/a^2=\mu a^n/r^{n+3}$（梯度比加速度多除一个长度）。
- **截断机制**：梯度只对 $m\le$ `gradientlimit` 且 $n\le$ `gradientlimit` 累加（第176-177行），超过则跳过并只警告一次（`matrixTruncationWasPosted`，第202-209行）——`gradientlimit` 来自 `StmLimit`（`HarmonicField` 构造默认 100，见后文），即**加速度按满阶 360 算，STM/A-Matrix 用的梯度按 StmLimit 截断**。这是精度与计算量的工程权衡：梯度项要算到 $n+2$，360 阶全算代价过高。
- 用途：`gradient`（Rmatrix33）在 `GravityField::GetDerivatives` 中直接填入 A-tilde 左下 6×6 块（第649-659行），驱动 $\dot\Phi=\tilde A\Phi$——球谐场的 STM 就是靠这套二阶偏导。

### VR 归一化校正系数（VR01..VR22）

- **公式**：归一化 Legendre 导数恒等式所需的代数系数（$m>0$；$m=0$ 各除以 $\sqrt2$）：

$$ V_{01}=\sqrt{(n-m)(n+m+1)},\quad V_{11}=\sqrt{\frac{(2n+1)(n+m+2)(n+m+1)}{2n+3}} $$

$$ V_{02}=\sqrt{(n-m)(n-m-1)(n+m+1)(n+m+2)},\quad
V_{12}=\sqrt{\frac{2n+1}{2n+3}(n-m)(n+m+1)(n+m+2)(n+m+3)} $$

$$ V_{22}=\sqrt{\frac{2n+1}{2n+5}(n+m+1)(n+m+2)(n+m+3)(n+m+4)} $$

- **代码位置**：`src/base/forcemodel/harmonic/Harmonic.cpp:298-315`。
- **深度讲解**：

```cpp
302:          VR01[n][m] = sqrt(Real((nn-m)*(nn+m+1)));
303:          VR11[n][m] = sqrt(Real((2*nn+1)*(nn+m+2)*(nn+m+1))/Real((2*nn+3)));
304:          VR02[n][m] = sqrt(Real((nn-m)*(nn-m-1)*(nn+m+1)*(nn+m+2))) ;
305:          VR12[n][m] = sqrt(Real(2*nn+1)/Real(2*nn+3)*Real((nn-m)*(nn+m+1)*(nn+m+2)*(nn+m+3)));
306:          VR22[n][m] = sqrt(Real(2*nn+1)/Real(2*nn+5)*Real((nn+m+1)*(nn+m+2)*(nn+m+3)*(nn+m+4)));
307:          if (m==0)
308:             {
309:             VR01[n][m] /= sqrt(Real(2));
...
```

- 这些系数来自归一化关联勒让德函数的导数递推：$\mathrm{d}\bar P_{nm}/\mathrm{d}u$ 与 $\bar P_{n,m+1}$ 相差 $\sqrt{(n-m)(n+m+1)}$ 等代数因子，二阶导再关联到 $m+2$ 阶（$V_{02},V_{12},V_{22}$）。$m=0$ 时除以 $\sqrt2$（第307-314行）与全归一化约定的 $\sqrt2$ 因子一致。
- 数值意义：把"对 $u$ 求导"替换为"对相邻阶求值"是稳定化关键——直接数值微分高阶勒让德会在 360 阶时灾难性放大舍入误差，而代数恒等式保持 $O(1)$ 量级。这些系数只依赖 $n,m$，在 `Allocate()` 一次性预计算（第298-315行），运行期零开销。

---

## 四、HarmonicGravity —— 球谐引擎与固体潮

### 中心项点质量场（CalculatePointField）

- **公式**：$n=0$（点质量）部分，与 `PointMassForce` 相同：

$$ \vec a_{point} = \frac{\mu}{r^3}\,\vec r,\qquad \nabla\vec a_{point} = \frac{\mu}{r^3}\Big(3\hat r\hat r^\top - I\Big) $$

（注意此处 $\vec r$ 是场点位置，代码 `acc[i] = -mu_r_3*pos[i]` 的符号因 `mu_r_3 = -Factor/r³` 且 `Factor=-μ` 而抵消，净效果是 $+\mu\vec r/r^3$——引力指向中心体。）

- **代码位置**：`src/base/forcemodel/harmonic/HarmonicGravity.cpp:168-195`。
- **深度讲解**：

```cpp
173:    Real r = sqrt(pos[0]*pos[0] + pos[1]*pos[1] + pos[2]*pos[2]);
174:    if (r == 0)
175:       r = 0.01;   // was0,01 - is this correct?
176:    Real mu_r_3 = (-Factor) / (r * r * r);   // Factor = -mu
177:    // Calculate acceleration
178:    for (Integer i=0;  i<=2;  ++i)
179:       acc[i] = -mu_r_3 * pos[i];
180:    // Calculate gradient
181:    if (fillgradient)
182:       {
183:       for (Integer i=0;  i<=2;  ++i)
184:          for (Integer j=0;  j<=2;  ++j)
185:             {
186:             gradient(i,j) = 3*mu_r_3 * pos[i]/r * pos[j]/r;
187:             if (i==j)
188:                gradient(i,j) += -mu_r_3;
189:             }
190:       }
```

- 第174-175行：原点处把半径钳到 0.01 km 防除零（注释自问"is this correct?"——这是已知的防御性写法）。
- 第176行：`mu_r_3 = μ/r³`（`Factor=-μ`）。第179行 `acc[i] = -(μ/r³)·pos[i] = −μr/r³`。
- 第186-188行：梯度 $(μ/r^3)(3\hat r\hat r^\top-I)$，对角补 $-μ/r^3$。这就是球谐场的 $n=0$ 项；`CalculateFullField` 把它与谐波部分相加（见下），避免在 Pines 求和里单独处理 $n=0$。

### CalculateFullField 分量合成

- **公式**：

$$ \vec a = \vec a_{point} + \vec a_{harmonic},\qquad \nabla\vec a = \nabla\vec a_{point} + \nabla\vec a_{harmonic} $$

- **代码位置**：`src/base/forcemodel/harmonic/HarmonicGravity.cpp:197-229`。
- **深度讲解**：

```cpp
205:    TideLevel = tidelevel;
206:    ClearDeltaCS ();
207:    if (tidelevel >= 2 && BodyName == GmatSolarSystemDefaults::EARTH_NAME)
208:       IncrementEarthTide(jday,sunpos,sunmukm,otherpos,othermukm,xp,yp);
209:    else if (tidelevel >= 1)
210:       {
211:       IncrementSolidTide (sunpos,sunmukm);
212:       if (othermukm > 0)
213:          IncrementSolidTide (otherpos,othermukm);
214:       }
...
219:    CalculatePointField(jday,pos,nn,mm,fillgradient,gradientlimit,accpoint,gradientpoint);
220:    CalculateField(jday,pos,nn,mm,fillgradient,gradientlimit,accharmonic,gradientharmonic);
221:    for (Integer i=0;  i<=2;  ++i)
222:       acc[i] = accpoint[i] + accharmonic[i];
223:    if (fillgradient)
224:       gradient = gradientpoint + gradientharmonic;
```

- 第205-206行：`TideLevel` 存入成员（`Cnm/Snm` 靠它决定是否加 $\Delta C,\Delta S$），`ClearDeltaCS` 把 5×5 潮汐增量清零（第417-425行）。
- 第207-214行：潮汐层级——`SolidAndPole`（≥2）且天体是地球 → 走完整 `IncrementEarthTide`（含频率相关项与极潮）；`Solid`（≥1）→ 只算太阳（及非零 μ 的第二摄动体）的固体潮。`tidelevel` 由 `GravityField::Calculate` 从脚本 `TideModel` 字符串映射而来（见后文）。
- 第219-224行：点质量项 + Pines 谐波项直接相加（加速度与梯度都加）。`CalculateField` 内部用 `Cnm/Snm` 取系数——当 `TideLevel>0` 且 $n,m\le4$ 时返回 `C[n][m]+DeltaC[n][m]`（见下一条目），因此潮汐修正自然进入谐波求和。

### 潮汐系数修正 Cnm/Snm（ΔC, ΔS）

- **公式**：低阶（$n,m\le4$）系数叠加潮汐增量：

$$ \bar C_{nm}^{eff} = \bar C_{nm} + \Delta\bar C_{nm},\qquad \bar S_{nm}^{eff} = \bar S_{nm} + \Delta\bar S_{nm} $$

- **代码位置**：`src/base/forcemodel/harmonic/HarmonicGravity.cpp:144-166`（`Cnm`/`Snm` 虚函数实现）。
- **深度讲解**：`Harmonic::CalculateField` 每取一对系数都调用这两个虚函数（`Harmonic.cpp:157-158`），正常返回 `C[n][m]`；仅当 `TideLevel>0` 且 $n,m\le LoveMax(=4)$ 时叠加 `DeltaC/DeltaS`（第146-149行）。这样潮汐增量只影响低 4 阶系数，Pines 递推代码无需感知潮汐。`DeltaC/DeltaS` 是 5×5 成员数组（`HarmonicGravity.hpp:110-111`），每次 `CalculateFullField` 先清零再累加（第206行 + 第417-425行），不污染静态系数。

### 固体潮增量（IERS 第6章）

- **公式**：对摄动体（日/月）在固连系位置 $(R,\phi,\lambda)$，按 IERS Conventions 第6章（eq.1-4, p.59-60）累加归一化系数增量：

$$ f_{nm} = \frac{GM'}{GM}\Big(\frac{a}{R}\Big)^{n+1}\bar P_{nm}(\sin\phi) $$

$$ \Delta\bar C_{nm} \mathrel{+}= \frac{k_{nm}}{2n+1}\,f_{nm}\cos(m\lambda),\qquad
   \Delta\bar S_{nm} \mathrel{+}= \frac{k_{nm}}{2n+1}\,f_{nm}\sin(m\lambda),\quad n=2,3 $$

四阶间接项（$n=2$ 时）：$\Delta\bar C_{4m} \mathrel{+}= \frac{k^{+}_{m}}{2n+1}\,f_{2m}\cos(m\lambda)$（同理 $\Delta\bar S_{4m}$）。

- **代码位置**：`src/base/forcemodel/harmonic/HarmonicGravity.cpp:427-449`（`IncrementSolidTide`）；`CartesianToPolar` 第376-383行、`PolarToLegendre` 第385-415行。
- **深度讲解**：

```cpp
429:    Real massratio    = -mukm/Factor;      // factor is minus body mukm  → GM'/GM
430:    Real polar[3];    // R,Latitude,Longitude (Radians)
431:    CartesianToPolar (pos,polar);
432:    Real poly[5][5];
433:    PolarToLegendre (polar,poly);
437:    for (Integer n=2;  n<=3;  ++n)
438:       for (Integer m=0;  m<=n;  ++m)
439:          {
440:          Real f  = massratio*Pow(FieldRadius/polar[0],n+1)*poly[n][m];
441:          DeltaC[n][m] += K[n][m]/(2*n+1) * (f*Cos(m*polar[2]));
442:          DeltaS[n][m] += K[n][m]/(2*n+1) * (f*Sin(m*polar[2]));
443:          if (n==2)
444:             {
445:             DeltaC[4][m] += KPlus[m]/(2*n+1) * (f*Cos(m*polar[2]));
446:             DeltaS[4][m] += KPlus[m]/(2*n+1) * (f*Sin(m*polar[2]));
447:             }
448:          }
```

- 第429行：质量比 $GM'/GM$（`Factor=-GM`，`mukm=GM'`，`-mukm/Factor=GM'/GM`）。
- 第431行：`CartesianToPolar` 把固连系笛卡尔坐标转成 $(R=\sqrt{x^2+y^2+z^2},\ \phi=\mathrm{atan2}(z,\sqrt{x^2+y^2}),\ \lambda=\mathrm{atan2}(y,x))$（第376-383行）。
- 第433行：`PolarToLegendre` 硬编码 $\bar P_{20}\sim\bar P_{33}$ 的解析式（第402-408行：$\bar P_{20}=\sqrt5(1.5s^2-0.5)$、$\bar P_{21}=3\sqrt{5/3}\,cs$ 等，均为**全归一化**值，与 `Harmonic` 的 $V(n,m)$ 约定一致）。
- 第440-442行：$f=(GM'/GM)(a/R)^{n+1}\bar P_{nm}$，乘 Love 数 $k_{nm}/(2n+1)$ 和 $\cos(m\lambda)/\sin(m\lambda)$ 累加 $\Delta C/\Delta S$——与 IERS eq.1-4 逐项对应。Love 数来自 IERS Table 6.3（见下一条目）。
- 第443-447行：$n=2$ 时额外产生四阶项，用 $k^{+}_m$（"K+" 加载 Love 数），这是 IERS 第6章中"degree-2 潮对 degree-4 势的间接贡献"。
- 物理背景：固体潮是日/月引力使地球弹性形变，形变体对外引力位的变化等价于低阶球谐系数的时变；Love 数 $k_{nm}$ 是"响应幅度/激发幅度"之比（弹性地球 $k_2\approx0.3$）。`IncrementSolidTide` 对日、月各调用一次（第211-213行），线性叠加。

### 频率相关项与极潮（IncrementEarthTide）

- **公式**：固体潮中随潮汐频率变化的部分（IERS eq.5a/5b, p.60）：对 C20（表 6.3b）、C21/S21（表 6.3a）、C22/S22（表 6.3c），

$$ \theta_f = \sum_{j=0}^{4} N_{fj}\,F_j \quad(\text{C20});\qquad \theta_f = m\big(GMST+\pi\big) - \sum_{j=0}^{4} N_{fj}\,F_j \quad(m=1,2) $$

$$ \Delta\bar C_{20}=\sum_f \big[A_f\cos\theta_f - B_f\sin\theta_f\big]\cdot10^{-12},\qquad
   \Delta\bar C_{21}=\sum_f \big[A_f\sin\theta_f+B_f\cos\theta_f\big]\cdot10^{-12} $$

其中 $F_j$ 为 Delaunay 变量 $(\ell,\ell',F,D,\Omega)$（章动基本幅角），$A_f,B_f$ 为表 6.3 的振幅（单位 $10^{-12}$）。极潮（固体 + 海洋）：

$$ m_1=x_p-\bar x_p,\quad m_2=-(y_p-\bar y_p),\quad \bar x_p=0.054+0.00083\,t_{yr},\quad \bar y_p=0.357+0.00395\,t_{yr} $$

$$ \Delta\bar C_{21} \mathrel{-}= 1.333\times10^{-9}(m_1+0.0115\,m_2) - 2.2344\times10^{-10}(m_1-0.01737\,m_2) $$

$$ \Delta\bar S_{21} \mathrel{-}= 1.333\times10^{-9}(m_2-0.0115\,m_1) - 1.7680\times10^{-10}(m_2-0.03351\,m_1) $$

- **代码位置**：`HarmonicGravity.cpp:451-593`（`IncrementEarthTide`）；GMST 第491-499行、Delaunay 变量第503-517行、频率项第519-565行、极潮第570-582行；表数据 `Table63a:291-339`、`Table63b:344-365`、`Table63c:369-372`。
- **深度讲解**：

```cpp
491:    Real a1mjd  = jday - GmatTimeConstants::JD_JAN_5_1941;
492:    Real JD     = theTimeConverter->Convert(a1mjd, TimeSystemConverter::A1MJD,
493:                 TimeSystemConverter::UTCMJD, GmatTimeConstants::JD_JAN_5_1941)
                 + GmatTimeConstants::JD_JAN_5_1941;      // A1 → UTC(≈UT1)
494:    Real t  = (JD-GmatTimeConstants::JD_OF_J2000)/GmatTimeConstants::DAYS_PER_JULIAN_CENTURY;
498:    Real GMST = 67310.54841 + 3164400184.812866*t + 0.093104*t2 - 6.2E-06*t3; // seconds of time
499:    GMST /= 240.0;                                         // → degrees
...
519:    // compute (2,0) freq dependent terms, IERS eqn 5a, p.60, (n=2,m=0)
520:    Real freq_dep_C20 = 0;
522:    for (Integer f=0;  f<Table63bDim1;  ++f)
523:       {
524:       Real theta_f = 0;
525:       for (Integer j=0;  j<=4;  ++j)
526:          theta_f += Table63b[f][j]*F[j];                  // θ_f = Σ N_fj F_j
527:       theta_f = -theta_f * GmatMathConstants::RAD_PER_DEG;
528:       freq_dep_C20 += (Table63b[f][5]*Cos(theta_f)-Table63b[f][6]*Sin(theta_f));
529:       }
530:    DeltaC[2][0] += freq_dep_C20 * 1e-12;
```

- 第491-493行：输入是 A1 MJD，先经 `TimeSystemConverter` 转 UTC MJD（近似 UT1）再算儒略世纪数 $t$（第494行）。GMST 用 IAU 多项式（第498-499行，单位秒→度）。
- 第503-517行：Delaunay 变量 $F[0..4]=(\ell,\ell',F,D,\Omega)$ 的 IAU 多项式（秒→度）。
- 第522-530行：C20 的频率相关项——表 6.3b 每行 7 个数 $(\ell,\ell',F,D,\Omega,A,B)$，前 5 个是 Delaunay 系数 $N_{fj}$，后两个是振幅；$\theta_f=-\Sigma N_{fj}F_j$（弧度），$A\cos\theta_f-B\sin\theta_f$ 后乘 $10^{-12}$ 累加（第528、530行）。C21/S21（第537-547行）与 C22/S22（第554-565行）用 $m(GMST+\pi)-\theta_f$ 且 sin/cos 互换（eq.5b），对应田谐潮的经度旋转因子 $e^{im(\theta_g-\lambda)}$——这正是需要 GMST 的原因。
- 第570-582行：极潮。$t_{yr}$ 为自 J2000 的年数；$\bar x_p,\bar y_p$ 为平均极移（IERS p.84 线性模型，第571-572行）；$m_1,m_2$ 为极移偏差（第574-575行）。固体极潮系数 $1.333\times10^{-9}$（第577-578行），海洋极潮系数 $2.2344\times10^{-10}$/$1.7680\times10^{-10}$（第581-582行，TechNote 32 §6.3）。`xp/yp` 由 `GravityField::Calculate` 从 EOP 文件取（见后文）。
- 物理背景：与"固体潮增量"（时域、只依赖摄动体瞬时位置）互补，频率相关项把固体潮按潮汐频率分解（长周期/周日/半日带），弥补时域方法对近共振频率成分的不足；永久潮（permanent tide）修正按 IERS Step 3 在模型装载时处理（第482-483行注释），避免与 tide-free/zero-tide 系数重复计算。

### Love 数与潮汐表

- **公式**：弹性 Love 数（IERS Table 6.3, p.71）与加载 Love 数 $k^+$：

$$ k_{20}=0.30190,\ k_{21}=0.29830,\ k_{22}=0.30102;\qquad k_{3m}=0.093/0.093/0.093/0.094;\qquad k^{+}_0..k^{+}_2 = -0.00087,-0.00079,-0.00057 $$

- **代码位置**：`HarmonicGravity.cpp:276-286`（`KEarth`/`KPlusEarth` 静态表）；`.tide` 文件装载 `LM_LoadTide` 第1026-1099行；`.grv` 内嵌 `K2/K3` 关键字第965-976行。
- **深度讲解**：第278-283行的 `KEarth[LoveMax+1][LoveMax+1]` 即 IERS Table 6.3 的 $k_{nm}$（第281行是被注释掉的旧值 0.29525 等，现用 0.30190 系列）；`KPlusEarth`（第285-286行）是 $k^+_m$。`LM_SetDefaultEarthTide`（第704-716行）在未装载 Love 数且天体是地球时填入默认表（第708-712行），供 `TideModel=Solid/SolidAndPole` 直接使用。`.tide` 文件格式为 `k n m 值` / `kplus m 值`（`LM_LoadTide` 第1051-1091行；样例 `application/data/gravity/luna/grgm900c.tide` 第3-5行：`k 2 0 0.024116` 等——月球潮汐 Love 数 $k_2\approx0.024$，远小于地球）。`K2/K3` 也可由 `.grv` 文件的 `BEGIN SIMPLETIDEMODEL` 段提供（第965-976行，`K[2][0..2]=rr`）。

### 位势系数文件格式与单位换算

- **公式**：`.cof` 文件（JGM2/JGM3/EGM96 等）的解析规则与单位换算：

$$ \mu_{internal}=\frac{\mu_{file}}{10^9}\ \text{(m³/s²→km³/s²)},\qquad a_{internal}=\frac{a_{file}}{10^3}\ \text{(m→km)},\qquad \bar C_{nm}=\frac{C_{nm}^{file}}{V(n,m)}\ \text{(非归一化时)} $$

- **代码位置**：`HarmonicGravity.cpp:755-799`（`LM_LoadCof`）、`625-641`（`LM_SetMu`/`LM_SetFieldRadius`）、`652-695`（`LM_SetCoefficients`，归一化换算第675-687行）；样例数据 `application/data/gravity/earth/EGM96low.cof:7-10`。
- **深度讲解**：

```cpp
773:          if (firstStr == "POTFIELD")
774:             {
775:             LM_SetNN (line.substr (8,3));       // 度 NN
776:             LM_SetMM (line.substr (11,3));      // 阶 MM
777:             StringArray sa = GmatStringUtil::SeparateBy (line.substr(14)," ");
778:             LM_SetMu (sa[1]);                   // 文件 μ（m³/s²）
779:             LM_SetFieldRadius (sa[2]);          // 参考半径（m）
780:             LM_SetNormalized (sa[3]);           // 归一化标志
781:             if (loadcoefficients) Allocate ();
782:             }
783:          else if (firstStr == "RECOEF")
784:             {
785:             if (!loadcoefficients) break;
786:             StringArray sa = StringArray (4,"");
787:             sa[0] = line.substr(8, 3);          // n
788:             sa[1] = line.substr(11, 3);         // m
789:             sa[2] = line.substr(17, 21);        // C
790:             if (line.size() > 38)
791:                sa[3] = line.substr(38, 21);     // S（m>0 时存在）
792:             LM_SetCoefficients (sa,false);
793:             }
```

- `POTFIELD` 行定宽解析：度/阶各 3 字符（第775-776行），后续空格分隔出"地球标志/μ/半径/归一化标志"（第777-780行；注意 `sa[0]` 是"1"表示地球，μ 是 `sa[1]`）。`RECOEF` 行 `n m C [S]`，S 仅在 $m>0$ 时存在（第790-791行）。样例 `EGM96low.cof:7`：`POTFIELD 70 70  1 3.98600441500000E+14 6.37813630000000E+06 1.00000000000000E+00`——μ=3.986004415e14 m³/s² → 398600.4415 km³/s²，a=6378.1363 km，归一化标志=1。
- `LM_SetMu`（第625-632行）：`Factor = -rr/1e9`，即文件 μ（m³/s²）除以 1e9 得 km³/s²，存入 `Factor` 的相反数；`LM_SetFieldRadius`（第634-641行）：`FieldRadius = rr/1e3`（m→km）。反向写入见 `WriteCofFile`（第238-267行）：`-Factor*1e9`、`FieldRadius*1e3`（第251-252行），与读取严格互逆。
- 归一化换算（第675-687行）：`Normalized==false` 时 `c /= V[n][m]`、`s /= V[n][m]`，用 `Harmonic::Allocate` 预计算的 $V(n,m)$（上一节）把非归一化系数转成全归一化——保证 `Harmonic.cpp` 的递推始终吃归一化系数。
- 其它格式：`.gfc`（ICGEM 文本，`LM_LoadGfc` 第801-854行，关键字 `earth_gravity_constant/radius/max_degree/norm/tide_system`）、`.grv`（GTDS/AGI 风格，`LM_LoadGrv` 第856-990行，含 `DEGREE/ORDER/GM/REFDISTANCE` 与潮汐段）、`.tab`（`LM_LoadTab` 第992-1024行，首行逗号分隔，读入后再 `FieldRadius*=1e3; Factor*=1e9` 校正单位，第1006-1008行）。`CheckEarthCoefficient`（第1115-1123行）对地球用 $\bar C_{20}$ 阈值判 tide-free/zero-tide：

```cpp
1117:    if (BodyName == GmatSolarSystemDefaults::EARTH_NAME && C != NULL && NN >= 2)
1118:    {
1119:       // Special case for Earth
1120:       bool tidefreemodel = C[2][0] > -4.84167E-04;
1121:       HaveTideFree = tidefreemodel;
1122:       HaveZeroTide = !tidefreemodel;
1123:    }
```

- 第1120行：tide-free 地球模型的 $\bar C_{20}\approx-4.8416537\times10^{-4}$（如 `EGM96low.cof:8` 的 `-4.84165371736000E-04`），zero-tide 模型约 $-4.84169\times10^{-4}$；阈值 $-4.84167\times10^{-4}$ 恰在两者之间，据此判别文件属于哪种潮汐系统，供 `TideModel` 选择与"永久潮重复计数"告警（`GravityField.cpp:1150-1156`）使用。

---

## 五、HarmonicField / GravityField —— 场容器与坐标链

### 度/阶截断（SetDegreeOrder 与 360×360 默认）

- **公式**：截断规则

$$ n_{use}=\min(\deg, n_{file}),\qquad m_{use}=\min(\ord, n_{use}, m_{file}),\qquad m_{use}\le n_{use} $$

- **代码位置**：`src/base/forcemodel/HarmonicField.cpp:371-396`（`SetDegreeOrder`）；默认值 `HarmonicField.cpp:141-143`（`degree=4, order=4, stmLimit=100`）；360×360 默认 `GravityField.hpp:155-156`（`DEFAULT_DEGREE=360, DEFAULT_ORDER=360`）；初始化期截断校验 `GravityField.cpp:393-424`。
- **深度讲解**：

```cpp
375:    if (deg <= maxDegree)
376:        degree = deg;
377:    else
378:    {
379:        degree = maxDegree;      // 超模型上限 → 钳到 maxDegree（=360）
...
385:    if ((ord <= deg) && (ord <= maxOrder))
386:        order = ord;
387:    else
388:    {
389:        order = (deg < maxOrder ? deg : maxOrder );
...
394:    stmLimit = stmlimit;
```

- 脚本 `Forces.GravityField.Earth.Degree/Order` 经此设置实际截断阶次；`GravityField` 构造默认 360×360（`GravityField.hpp:155-156`），`HarmonicField` 默认运行阶次 4（`HarmonicField.cpp:141-142`，脚本未显式设置时的保守起点）。`GravityField::Initialize` 里再做文件核对：请求度>文件度 → 抛异常（第393-400行）；请求阶>文件阶 → 抛异常（第401-408行）；`order>degree` → 告警并把 order 钳到 degree（第409-420行）。
- `stmLimit`（默认 100，`HarmonicField.cpp:143`）是上文"梯度截断"的限值：加速度按 `degree/order`（最高 360）算，STM/A-Matrix 的梯度按 `stmLimit` 截断——脚本可单独调 `StmLimit` 平衡估计精度与耗时。
- 物理背景：360×360 是 EGM96 的满阶（`EGM96.cof`），对应 ~10 km 地表分辨率；低轨（LEO）精密定轨必须用满阶，但 STM 梯度的高阶项对短期变分传播贡献小，故默认截到 100。

### 固连系 → 惯性系旋转链（Calculate + InverseRotate）

- **公式**：设惯性系（`inputCS`，如 EarthMJ2000Eq）到固连系（`fixedCS`，地球为 EarthFixed，含极移/章动/自转的"重力参考系"）的旋转矩阵为 $R$（`cc.GetLastRotationMatrix()` 返回 `R2ᵀ·R1`，见 `src/base/coordsystem/CoordinateConverter.cpp:395-413`，满足 $r_{fixed}=R\,r_{inertial}$），则反向变换为

$$ \vec a_{inertial} = R^{\top}\,\vec a_{fixed},\qquad
   \frac{\partial \vec a_{inertial}}{\partial \vec r_{inertial}} = R^{\top}\Big(\frac{\partial \vec a}{\partial \vec r}\Big)_{fixed}\,R $$

- **代码位置**：`GravityField.cpp:1425-1559`（`Calculate`）；`InverseRotate` 第1370-1384行；坐标系初始化 `GravityField.cpp:328-334`；`HarmonicField::Initialize` 第271-317行（inputCS/fixedCS/targetCS/eop 校验）。
- **深度讲解**：

```cpp
1453:    // convert to body fixed coordinate system
1454:    Real tmpState[6];
1456:    //BodyFixed coordinate should use the correct gravity frame and not a user defined frame
1457:    fixedCS->SetForGravityUpdate(true);
1459:    if (hasPrecisionTime)
1460:       cc.Convert(nowGT, state, inputCS, tmpState, fixedCS);
1461:    else
1462:       cc.Convert(now, state, inputCS, tmpState, fixedCS);
1463:    fixedCS->SetForGravityUpdate(false);
1469:    Rmatrix33 rotMatrix = cc.GetLastRotationMatrix();
...
1553:    // Convert back to target CS
1554:    InverseRotate (rotMatrix,rotacc,acc);
1555:    grad = rotMatrix.Transpose() * rotgrad * rotMatrix;
```

- 第1457/1463行：`SetForGravityUpdate(true)` 让 `fixedCS` 在本次转换中使用"引力参考系"定义（含 EOP 极移/UT1-UTC 的完整 GCRF→ITRF 链），而不是用户自定义的普通固连系——这是球谐系数严格定义在"真地球固连系"上的前提。
- 第1459-1462行：`CoordinateConverter::Convert` 把惯性状态（位置+速度）转到固连系，内部执行"岁差/章动 → 恒星时（GMST/GAST）→ 极移"旋转链（EOP 数据来自 `HarmonicField` 持有的 `EopFile*`，`HarmonicField.hpp:198`；校验见 `HarmonicField.cpp:290-299`）。旋转链的具体矩阵实现在 `src/base/coordsystem/`，本章只关心它的数学角色——一个正交矩阵 $R$。
- 第1469行：`GetLastRotationMatrix()` 取回本次转换的旋转矩阵 $R$（满足"from→to"，即惯性→固连，故 $r_{fixed}=R\,r_{inertial}$，$r_{inertial}=R^\top r_{fixed}$）。
- 第1554行：`InverseRotate`（第1370-1384行）用 $R^\top$ 的三行点乘把固连系加速度转回惯性系：

```cpp
1372:    const Real *rm = rot.GetDataVector();
1373:    const Real  rmt[9] = {rm[0], rm[3], rm[6],
1374:       rm[1], rm[4], rm[7],
1375:       rm[2], rm[5], rm[8]};                 // Rᵀ（行主序转置）
1376:    for (Integer p = 0; p < 3; ++p)
1377:    {
1378:       Integer p3 = 3*p;
1379:       out[p] = rmt[p3]*in[0] + rmt[p3+1]*in[1] + rmt[p3+2]*in[2];
1380:    }
```

- 第1555行：梯度是二阶张量，必须做相似变换 $R^\top G R$（`rotMatrix.Transpose()*rotgrad*rotMatrix`），不能只乘一次——这正是 `grad` 能直接填入惯性系 A-tilde（`GravityField.cpp:649-659`）的原因。
- 时间变量：`Calculate` 内部维护 A1 JD（`jday = epoch + JD_JAN_5_1941 + ...`，第1446-1448行）供潮汐/时变系数用；`hasPrecisionTime` 分支用 `GmatTime` 高精度路径（第1437-1443行）。

### 原点偏移间接项（body ≠ forceOrigin）

- **公式**：当引力体不是力模型原点时，先算原点处加速度并扣除：

$$ \vec a(\vec r_{sat}) \leftarrow \vec a(\vec r_{sat}) - \vec a(0),\qquad
   \nabla\vec a \leftarrow \nabla\vec a(\vec r_{sat}) - \nabla\vec a(0) $$

- **代码位置**：`GravityField.cpp:542-570`（`GetDerivatives` 内）；判定 `GravityField.cpp:341-344`（`offsetBodyOrigin`）。
- **深度讲解**：与 `PointMassForce` 的间接项同源（相对运动），但这里发生在**球谐场**上：`body`（系数所属天体）与 `forceOrigin`（积分原点）不同（如月球引力场挂在地心 ODE 里）时，第542-549行先对零状态调 `Calculate` 得原点加速度/梯度，第553-570行对每个航天器扣减：

```cpp
562:          if (body != forceOrigin)
563:          {
564:             for (Integer i=0;  i<=2;  ++i)
565:                accnew[i] -= originacc[i];
566:             gradnew -= origingrad;
567:          }
```

- 第565行 `accnew[i] -= originacc[i]`：航天器加速度减去原点（地心）被月球吸引的加速度；第566行梯度同步扣减。注意第564行 `GetDerivatives` 入口只处理 `fillCartesian||fillSTM||fillAMatrix`（第531行），`dvorder==2`（RKN 积分器）时加速度直接写入位置导数槽（第587-594行）。
- 这解释了为何 `GetDerivatives` 对 `cartesianCount` 个航天器逐个调 `Calculate`（第553-561行）而非共享一次——每个航天器位置不同，球谐场是位置的函数；而原点项只需算一次（在循环外，第545行）。

### 潮汐数据链路（GetTideData + EOP）

- **公式**：潮汐摄动体的固连系位置与 μ 由惯性星历经同一旋转链转换：

$$ \vec r'_{body,fixed} = R\,\vec r'_{body,inertial} $$

- **代码位置**：`GravityField.cpp:1386-1421`（`GetTideData`）；调用点 `GravityField.cpp:1492-1506`；EOP 极移读取第1507-1522行；`TideModel` 字符串→`tideLevel` 映射第1481-1490行；`SetTideFilename` 第1707-1773行。
- **深度讲解**：`GetTideData(dt, bodyname, pos, mukm)` 取天体惯性状态（第1396-1400行，`body->GetMJ2000State`），同样用 `fixedCS->SetForGravityUpdate(true)` + `cc.Convert` 转到固连系（第1409-1414行），`state.GetR(pos)` 取位置、`mukm = body->GetGravitationalConstant()`（第1419-1420行）。`Calculate` 中的选择逻辑（第1492-1506行）：`TideModel` 非 "None" 时，太阳必算（第1495行）；"other" 摄动体——地球取月球（第1498-1499行）、绕日行星无（第1500-1501行）、卫星取中心行星（第1503-1504行）。极移 `xp,yp,lod` 从 `eop->GetPolarMotionAndLod` 取（第1511-1522行，先 A1→UTC 转换），随 `CalculateFullField` 传入极潮。`TideModel` 脚本参数（"None"/"Solid"/"SolidAndPole"，`HarmonicGravity.hpp:88-90`）在 `GravityField::SetStringParameter`（第1138-1189行）校验模型支持性并设 `TideModel` 字符串；`tideLevel` 映射（第1481-1490行）：`ETideString[i]==TideModel` 且 `HaveTideModel(i)` → `tideLevel=i`，否则 0（无潮汐）。潮汐文件经 `SetTideFilename`（第1707-1773行，`.tide` 扩展名自动补全，第1132-1134行）交给 `GetHarmonicGravity` 装载。

### 系数装载与缓存（GetHarmonicGravity）

- **公式**：无（装载/复用机制）；关键语义：`mu` 与 `a` 以**文件值为准**回写：

$$ \mu = -gravityModel\text{->}GetFactor(),\qquad a = gravityModel\text{->}GetFieldRadius() $$

- **代码位置**：`GravityField.cpp:1684-1692`（`GetHarmonicGravity`）；初始化调用 `GravityField.cpp:346-384`；缓存成员 `GravityField.hpp:196`（`static std::vector<HarmonicGravity*> cache`）。
- **深度讲解**：

```cpp
1684: HarmonicGravity* GravityField::GetHarmonicGravity
1685:   (const std::string& filename, const std::string& tideFilename,
1686:    const Real &radius, const Real &mukm, const std::string& bodyname,
1687:    const bool& loadCoefficients)
1688:    {
1689:    HarmonicGravity* hg = new HarmonicGravity (filename,tideFilename,radius,mukm,bodyname,loadCoefficients);
1690:    if (hg->GetNN() == 0) return NULL;
1691:    return hg;
1692:    }
```

- 第1689行：构造 `HarmonicGravity` 即触发 `LM_Load`（`HarmonicGravity.cpp:83`）读系数；`GetNN()==0` 表示文件无有效系数 → 返回 NULL，`GravityField::Initialize` 抛"cannot be opened or read"（第368-374行）。
- 初始化期（第346-384行）：`mu=body->GetGravitationalConstant()`、`a=body->GetEquatorialRadius()` 先取天体默认（第350-351行），装载后**用文件值覆盖**（第382-383行：`mu = -gravityModel->GetFactor()`、`a = gravityModel->GetFieldRadius()`）——保证 μ/a 与系数文件自洽（JGM3 与 EGM96 的 μ 有细微差别）。`GravityField.hpp:196` 的静态 `cache` 注释说"跨实例共享已装载系数避免重复读文件"，但当前实现（第1689行）每次新建——实际复用由 `HarmonicGravity` 自身的装载路径保证（`HarmonicGravity.cpp:718-726`，`.tide` 只在文件名含 ".tide" 时装载，第721-724行）。`filenameFullPath` 经 `HarmonicField::SetFilename` 解析（`HarmonicField.cpp:410-499`，`DFLT__` 前缀表示默认文件，第422-426行；无扩展名补 `.cof`，`HarmonicField.cpp:763-764`）。

### 引力梯度力矩（GravityField）

- **公式**：与点质量同名方法相同（见上）：

$$ \vec T = \frac{3\mu}{r^3}\,\hat r \times (I\,\hat r) $$

- **代码位置**：`GravityField.cpp:1787-1852`（`GetTorquesForSpacecraft`）。
- **深度讲解**：第1835-1836行算 `dist`，第1839-1840行 `nadirVec=-r̂`，第1842-1843行 `Cross((3μ/r³)·nadirVec, scMOITensor·nadirVec)`——与 `PointMassForce.cpp:1291-1292` 完全同式（μ 用 `body->GetGravitationalConstant()`，第1842行）。`ODEModel::GetTorquesForSpacecraft`（`ODEModel.cpp:6577-6579`）遍历点质量与引力场分别累加力矩，供姿态动力学（第7章）使用。注意此处用的是点质量近似力矩（$\mu/r^3$ 项），不含球谐高阶贡献。

---

## 六、PolyhedronGravityPlugin —— Werner-Scheeres 多面体模型

### 多面体引力势与加速度合成（Werner-Scheeres 法）

- **公式**：对三角面片多面体，场点 $\vec r$ 处的引力势与加速度（Werner & Scheeres 1996/1997）：

$$ U = \frac{1}{2}G\rho\Big[\sum_{e\in E}\vec r_e^{\top}E_e\,\vec r_e\,L_e - \sum_{f\in F}\vec r_f^{\top}F_f\,\vec r_f\,\omega_f\Big] $$

$$ \vec a = -\nabla U = G\rho\Big(-\sum_{e}\vec E_e\,\vec r_e\,L_e + \sum_{f}\vec F_f\,\vec R_1\,\omega_f\Big) = G\rho\big(-\vec{sumEdge}+\vec{sumFace}\big) $$

- **代码位置**：`plugins/PolyhedronGravityPlugin/src/base/gravitymodel/PolyhedronGravityModel.cpp:424-700`（`Calculation`）；加速度合成第669-684行。类体系与参数表见 [第14章](../CH14-plugins-b.md) 第294-324行。
- **深度讲解**：`Calculation` 是核心（入口 `GetDerivatives` 第931-997行调用，状态为相对引力体的 MJ2000Eq 状态，第971行）：

```cpp
437:    Rvector3 sumEdge(0.0, 0.0, 0.0);
438:    Rvector3 sumFace(0.0, 0.0, 0.0);
439:    Rmatrix33 sumEdgeA(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
440:    Rmatrix33 sumFaceA(0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0);
441:    sumWf = 0.0;
...
463:    r = D*r;                            // position in BodyFixed coordinate system
464:    Rvector3 v1 = Ddot*r + D*v;         // velocity in BodyFixed coordinate system
...
673:    Rvector3 a = (GmatPhysicalConstants::UNIVERSAL_GRAVITATIONAL_CONSTANT * 1.0e9 * bodyDensity) * (-sumEdge + sumFace);
678:    Rvector3 aa = D.Transpose()*a;      // gravity vector in MJ2000Eq coordinate system
684:    xdot.Set(v(0), v(1), v(2), aa(0), aa(1), aa(2));
```

- 第463-464行：先经旋转矩阵 $D$ 把场点转到体固系（$r_{fixed}=Dr$，速度含 $D$ 的时间导数项 $v_1=\dot D r+Dv$——体固系随天体自转，速度必须做"旋转坐标系"变换）。
- 第673行：$G\cdot10^9$ 的数学含义——`UNIVERSAL_GRAVITATIONAL_CONSTANT=6.673\times10^{-20}$ km³/(kg·s²)（`src/gmatutil/util/GmatConstants.hpp:117`），乘 $10^9$ 后数值上等于 SI 的 $6.673\times10^{-11}$；配合密度 $\rho$（kg/m³）与公里量纲的位置，恰好抵消 km³→m³ 换算，使 $a=(G\cdot10^9)\rho(-\vec{sumEdge}+\vec{sumFace})$ 直接得 km/s²（第670-673行注释自述此约定；$\vec{sumEdge},\vec{sumFace}$ 量纲为 km）。
- 第678行：加速度转回惯性系 $a_{inertial}=D^\top a_{fixed}$；第684行组装导数 $\dot x=(v,\,a_{inertial})$。
- **内/外判定**：$\sum_f\omega_f$（`sumWf`）在体内为 $4\pi$（第666-667行注释），`GetSolidAngle`（第1085-1155行）与 `SurfaceHeight` 参数（[第14章](../CH14-plugins-b.md) 第330行）据此判定"在场内/触地"。

### 边贡献（Ee 与 Le）

- **公式**：对每条边，顶点 $P_1,P_2$，单位方向 $\hat n_{12}$，两侧面法向 $\hat n_a,\hat n_b$，面内边法向 $\hat n_{a12}=\hat n_{12}\times\hat n_a$、$\hat n_{b21}=\hat n_{21}\times\hat n_b$，边矩阵与对数项：

$$ E_e = \hat n_a\hat n_{a12}^{\top} + \hat n_b\hat n_{b21}^{\top},\qquad
   L_e = \ln\frac{r_1+r_2+e}{r_1+r_2-e} $$

$$ \vec{sumEdge} = \sum_e E_e\,\vec r_e\,L_e $$

其中 $\vec r_e=P_1-\vec r$（场点指向边端点），$r_1=|\vec R_1|$、$r_2=|\vec R_2|$ 为场点到两端点距离，$e=|P_1P_2|$。

- **代码位置**：`PolyhedronGravityModel.cpp:486-587`（边循环）；`Ee` 组装第548-550行；`Le` 第572-577行；面内边法向第513-518行与指向修正第534-541行。
- **深度讲解**：

```cpp
513:       na12.Set(-n12(2)*na(1) + n12(1)*na(2),      // n12 × na
514:     		    n12(2)*na(0) - n12(0)*na(2),
515:     		   -n12(1)*na(0) + n12(0)*na(1));
...
534:       a2v = P1 - polybody->ic[face1];              // 面1内心 → 边端点
535:       if (a2v*na12<0.0)
536:          na12 = -na12;                             // 确保朝外
...
548:       Ee.Set(na(0)*na12(0)+nb(0)*nb21(0), ...);    // Ee = na·na12ᵀ + nb·nb21ᵀ
...
573:       Le = GmatMathUtil::Ln((r1+r2+e)/(r1+r2-e)); // ln((r1+r2+e)/(r1+r2-e))
577:       sumEdge = sumEdge + Ee*re*Le;                // Σ Ee·re·Le
```

- 第513-518行：`na12 = n12×na`、`nb21 = n21×nb` 是"在面内、垂直于边、指向面内"的边法向（叉积构造，注释里的 MatLab 原式第511-512行）。
- 第534-541行：用"面内心指向边端点"的向量与 $n_{a12}$ 点积判符号，负则取反——保证 $n_{a12}$ 指向面 1 内部（Werner-Scheeres 要求边法向分别指向各自邻接面，方向错了会整体变号）。
- 第548-550行：$E_e=\hat n_a\hat n_{a12}^\top+\hat n_b\hat n_{b21}^\top$ 是两条邻接面对边贡献的投影算子（把 $\vec r_e$ 投影到两个面的法向-边法向张成的方向）。
- 第573行：$L_e$ 是沿边长的 $\int 1/r\,dl$ 解析积分的结果（$\ln$ 形式）；$r_1+r_2-e\to0$ 时（场点贴近边）对数发散，这是多面体模型的已知奇性，航天器通常不进入该区域。
- 第577行：累加 $\vec{sumEdge}$。`Edges()`/`EdgeAttachments`（`PolyhedronBody.cpp:449-543, 559-564`）预先建好边表与两侧邻接面，使运行期循环只需查表（第502行）。

### 面贡献与立体角 ω_f

- **公式**：对三角面（顶点 $A,B,C$），场点相对向量 $\vec R_1=\vec A-\vec r$、$\vec R_2=\vec B-\vec r$、$\vec R_3=\vec C-\vec r$，面投影算子与立体角：

$$ F_f = \hat n_f\hat n_f^{\top},\qquad
   \omega_f = 2\,\mathrm{atan2}\Big(\vec R_1\cdot(\vec R_2\times\vec R_3),\,
   r_1r_2r_3 + r_1(\vec R_2\cdot\vec R_3) + r_2(\vec R_3\cdot\vec R_1) + r_3(\vec R_1\cdot\vec R_2)\Big) $$

$$ \vec{sumFace} = \sum_f F_f\,\vec R_1\,\omega_f,\qquad \mathrm{sumWf} = \sum_f \omega_f $$

- **代码位置**：`PolyhedronGravityModel.cpp:604-648`（面循环）；立体角第636-637行；`GetSolidAngle` 复用第1122-1148行。
- **深度讲解**：

```cpp
612:	  Ff.Set(n(0)*n(0), n(0)*n(1), n(0)*n(2), ...);   // Ff = n·nᵀ
...
623:	  R1 = A-r;  R2 = B-r;  R3 = C-r;
627:	  r1 = R1.Norm();  r2 = R2.Norm();  r3 = R3.Norm();
631:	  cR23.Set(-R2(2)*R3(1) + R2(1)*R3(2), ...);       // R2 × R3
636:	  wf = 2*atan2(R1*cR23,
637:	        (r1*r2*r3+r1*R2*R3+r2*R3*R1+r3*R1*R2));
640:	  sumFace = sumFace + Ff*R1*wf;
641:	  sumWf = sumWf + wf;
```

- 第612-614行：$F_f=\hat n_f\hat n_f^\top$ 把 $\vec R_1$ 投影到面法向（面贡献只沿法向）。
- 第631-633行：`cR23 = R2×R3`。第636-637行是标准的多面体立体角公式（van Oosterom & Strackee 1983 形式）：分子 $\vec R_1\cdot(\vec R_2\times\vec R_3)$ 是三重积（带符号，决定 $\omega_f$ 符号），分母是四个标量积组合（保证 $|\omega_f|\le2\pi$ 且对退化面平滑）。`atan2` 保证角度在 $(-\pi,\pi]$ 且符号与法向一致——面法向朝外时，体外场点的 $\omega_f$ 为正。
- 第640-641行：累加面贡献向量与立体角总和。$\sum_f\omega_f=4\pi$ 当且仅当场点在体内（立体角覆盖整个球面），这是"内外判定"的数学依据；第666-667行注释的 Laplacian 检验即此。
- 第645行 `sumFaceA += Ff*wf`：面变分项（无 $\vec R_1$ 因子），供 A 矩阵用。

### 变分项与 A 矩阵（∂a/∂r）

- **公式**：位置部分雅可比（体固系）为

$$ \Big(\frac{\partial \vec a}{\partial \vec r}\Big)_{fixed} = (G\cdot10^9\,\rho)\,\big(\vec{sumEdgeA}-\vec{sumFaceA}\big),\qquad
   \vec{sumEdgeA}=\sum_e E_e\,L_e,\quad \vec{sumFaceA}=\sum_f F_f\,\omega_f $$

惯性系下做相似变换：$\tilde A_{(3+i,j)} = D^\top\big[(G\cdot10^9\rho)(\vec{sumEdgeA}-\vec{sumFaceA})\big]D$。

- **代码位置**：`PolyhedronGravityModel.cpp:584-585`（`sumEdgeA`）、`645-646`（`sumFaceA`）、`686-698`（A 矩阵组装）。
- **深度讲解**：

```cpp
584:          sumEdgeA = sumEdgeA + Ee*Le;               // Σ Ee·Le
...
645:	  sumFaceA = sumFaceA + Ff*wf;                    // Σ Ff·ωf
...
687:	//   A = [zeros(3,3) eye(3,3);
688:	//            D'*G*rho*(sumEdgeA - sumFaceA)*D zeros(3,3)];
689:	   Rmatrix33 m1 = D.Transpose() * (GmatPhysicalConstants::UNIVERSAL_GRAVITATIONAL_CONSTANT * 1.0e9 *bodyDensity) * (sumEdgeA - sumFaceA)*D;
694:	   M(0,3) = 1.0; M(1,4) = 1.0; M(2,5) = 1.0;       // 速度块 = I
695:	   for (int i = 1; i < 3; ++i)
696:		   for (int j = 0; j < 3; ++j)
697:			   M(i+3,j) = m1(i,j);                       // 加速度块 = m1
```

- 第584行：$\vec{sumEdgeA}$ 对 $\vec r_e$ 求导时去掉 $\vec r_e$ 因子（$\partial(E_e r_e L_e)/\partial r_e = E_e L_e$，因 $E_e$ 与场点无关、$L_e$ 只依赖距离标量）；第645行同理。第689行组合成 $m_1$ 并做 $D^\top(\cdot)D$ 相似变换转回惯性系（与球谐梯度的旋转处理一致，见第5节）。
- 第694行：速度块 $\dot\Phi$ 的运动学部分 $\partial v/\partial r=0$、$\partial v/\partial v=I$——A 矩阵左上为 0、右上为 $I$、左下为 $m_1$、右下为 0（第687-688行注释给出完整分块结构）。
- 用途：多面体模型同样支持 STM/A-Matrix 变分传播（估计与协方差）；注意 `SetStart` 只注册了 `CARTESIAN_STATE`（第1030-1036行），`SupportsDerivative` 仅 CARTESIAN（第1064-1067行），即当前多面体实现不参与 STM 填充（`Calculation` 算出的 M 保留扩展接口）。

### 旋转矩阵链（IAU 简化版与完整版）

- **公式**：惯性系→体固系的旋转（IAU 简化版，`CalculateTransformationMatrix_UsingIAUSimplified`）：

$$ C_{IB} = D_3(-\tfrac{\pi}{2}-RA)\,D_1(DEC-\tfrac{\pi}{2})\,D_3(-\theta),\qquad \theta = PRA+\omega\,t,\qquad D = C_{IB}^{\top} $$

其中 $D_3(\alpha)$ 绕 z 轴、$D_1(\alpha)$ 绕 x 轴的标准旋转；`RA/DEC` 为天体自转轴在 J2000 惯性系的赤经/赤纬，`PRA` 为初始本初子午线角，$\omega$ 为自转速率（rad/day），$t$ 为自 `OrientationEpoch` 起的天数。

- **代码位置**：`PolyhedronGravityModel.cpp:301-351`（简化版）；完整版 `CalculateTransformationMatrix` 第353-415行（用 `CoordinateConverter` 从 MJ2000Eq 转 BodyFixed，第356-370行）。
- **深度讲解**：

```cpp
312:    Real w	= (bodyOrientation[5]*pi/180);		// rad/day
313:    Real PRA = bodyOrientation[4]*pi/180;
314:    Real RA	= bodyOrientation[0]*pi/180;
315:    Real DEC = bodyOrientation[2]*pi/180;
316:    Real theta = PRA + w*t;
318:    Rmatrix33 D3w(cos(-theta), sin(-theta), 0.0, ...);   // D3(-θ)
322:    Rmatrix33 D1(1.0, 0.0, 0.0,
323:         0.0, cos(DEC-pi/2), sin(DEC-pi/2), ...);        // D1(DEC-π/2)
326:    Rmatrix33 D3(cos(-pi/2-RA), sin(-pi/2-RA), 0.0, ...);// D3(-π/2-RA)
330:    Rmatrix33 C_IB = D3*D1*D3w;
331:    Rmatrix33 D = C_IB.Transpose();
```

- 第312-316行：姿态参数来自 `createForceBody->GetOrientationParameters()`（第962行）——[RA, 自转角, DEC, 本初子午线, PRA, ω] 顺序（`RA=bodyOrientation[0]`、`DEC=[2]`、`PRA=[4]`、`w=[5]`）；$\theta=PRA+\omega t$ 为相对初始姿态的自转角。
- 第318-331行：$C_{IB}=D_3(-\pi/2-RA)\,D_1(DEC-\pi/2)\,D_3(-\theta)$ 是 IAU 小天体自转轴定义的标准构造（先用 $D_1(DEC-\pi/2)$ 把赤纬转到 z 轴附近，再用 $D_3$ 消去赤经与自转相位）；`D = C_IBᵀ` 是体固→惯性的方向余弦阵（代码约定 `r_fixed = D·r_inertial`，与第463行一致）。
- 完整版（第353-415行）默认启用：直接构造 MJ2000Eq 与 BodyFixed 两个局部坐标系（第356-359行），用 `CoordinateConverter` 转换一个占位向量并取 `GetLastRotationMatrix`（第364-371行）与 `GetLastRotationDotMatrix`（第373行）——走的是与 `GravityField` 相同的完整岁差章动链，适合自转轴缓慢进动的小天体；简化版（第301行）适合自转轴固定的粗模型。`Ddot` 用于体固系速度（第464行），其物理含义是 $\dot D=\partial D/\partial t$（自转 + 进动导致的方向余弦阵变化率）。

### 多面体几何预处理（法向/内心/边）

- **公式**：面法向（右手定则，需数据文件顶点环绕序一致）、内心（边长加权平均）、边表（去重 + 邻接面）：

$$ \hat n_f = \frac{(\vec B-\vec A)\times(\vec C-\vec B)}{|(\vec B-\vec A)\times(\vec C-\vec B)|},\qquad
   \vec{ic}_f = \frac{a\vec A+b\vec B+c\vec C}{a+b+c}\ (a=|\vec{BC}|,\ b=|\vec{CA}|,\ c=|\vec{AB}|) $$

- **代码位置**：`PolyhedronBody.cpp:365-404`（`FaceNormals`）、`319-354`（`Incenters`）、`449-543`（`Edges`）、`141-309`（`LoadBodyShape`，顶点/面读取与 1→0 基转换）。
- **深度讲解**：

```cpp
382:		r1 = B - A;						// vector AB
383:		r2 = C - B;						// vector BC
384:		x = r1[1]*r2[2] - r1[2]*r2[1];
385:		y = r1[2]*r2[0] - r1[0]*r2[2];
386:		z = r1[0]*r2[1] - r1[1]*r2[0];
387:      n.Set(x,y,z);		         // n = AB × BC
388:		if (n.Norm() < 1.0e-15)
389:			return false;                // 退化面（共线顶点）拒绝
390:		n.Normalize();
```

- 第382-392行：法向 $=\overrightarrow{AB}\times\overrightarrow{BC}$ 归一化；模 < 1e-15 视为退化面拒绝（第388-389行）。法向指向由顶点环绕序决定，故数据文件必须约定一致的逆时针/顺时针序（第14章已述，[CH14](../CH14-plugins-b.md) 第290行）。
- `Incenters`（第339-343行）：内心 = 对边长加权的顶点平均 $ic=(aA+bB+cC)/(a+b+c)$——用于边法向的"朝外"判据（`PolyhedronGravityModel.cpp:534-541`）。
- `Edges`（第464-517行）：对每个三角面枚举 3 条边 $(f_0,f_1),(f_1,f_2),(f_2,f_0)$（第469-471行），用 `indexKey = min·100000+max` 做哈希键（第474-475行）去重；首次出现记录 `attachmentA`（第479行），再次出现记录 `attachmentB`（第484-485行）——得到每条边的两侧邻接面，供引力求和的 $E_e$ 组装用。`LoadBodyShape`（第278-280行）把文件里 1 基顶点下标转 0 基（`ix-1`），顶点单位 km（第212行注释）。

---

## 七、公式索引表

| 公式 | 文件:行 | 所属类 |
| --- | --- | --- |
| 点质量加速度 $\vec a=-\mu\vec r/r^3$（主循环） | src/base/forcemodel/PointMassForce.cpp:492-521 | PointMassForce |
| 间接项 $\vec a_{indirect}=\mu\vec r_{bb}/|\vec r_{bb}|^3$ | src/base/forcemodel/PointMassForce.cpp:440-453 | PointMassForce |
| 时间雅可比 $\partial a_i/\partial t=\mu\sum_j[(\delta_{ij}-3\hat u_i\hat u_j)/r^3]\cdot v_j$ | src/base/forcemodel/PointMassForce.cpp:387-438 | PointMassForce |
| A-tilde $\tilde A_{(3+i,j)}=(\mu/r^3)(\delta_{ij}-3r_ir_j/r^2)$ | src/base/forcemodel/PointMassForce.cpp:606-636 | PointMassForce |
| 重力梯度力矩 $\vec T=(3\mu/r^3)\hat r\times(I\hat r)$ | src/base/forcemodel/PointMassForce.cpp:1283-1292 | PointMassForce |
| 球谐势展开 $U=(\mu/r)\sum_n (a/r)^n\bar P_{nm}[\bar C\cos m\lambda+\bar S\sin m\lambda]$ | src/base/forcemodel/harmonic/Harmonic.hpp:31-51（文献）；Harmonic.cpp:160-171（实现） | Harmonic |
| 方向余弦 $s,t,u=x,y,z/r$ | src/base/forcemodel/harmonic/Harmonic.cpp:97-100 | Harmonic |
| 勒让德对角 $A[n][n]=\sqrt{(2n+1)/(2n)}A[n-1][n-1]$ | src/base/forcemodel/harmonic/Harmonic.cpp:280-282 | Harmonic |
| 勒让德列填充 $A[n][m]=uN_1A[n-1][m]-N_2A[n-2][m]$ | src/base/forcemodel/harmonic/Harmonic.cpp:104-116, 317-325 | Harmonic |
| 归一化因子 $V(n,m)=\sqrt{2(2n+1)(n-m)!/(n+m)!}$ | src/base/forcemodel/harmonic/Harmonic.cpp:284-297 | Harmonic |
| Re/Im 递推 $\mathrm{Re}_m=s\mathrm{Re}_{m-1}-t\mathrm{Im}_{m-1}$ | src/base/forcemodel/harmonic/Harmonic.cpp:113-115 | Harmonic |
| rho 递推 $\rho_{n+1}=\mu a^{n+1}/r^{n+2}$（Pines Eq.26） | src/base/forcemodel/harmonic/Harmonic.cpp:120-122, 137-140 | Harmonic |
| D/E/F 组合与一阶和（Pines Eq.27/30） | src/base/forcemodel/harmonic/Harmonic.cpp:157-171, 213-218 | Harmonic |
| 加速度合成 $a=(a_1+a_4s,\ a_2+a_4t,\ a_3+a_4u)$（Eq.31） | src/base/forcemodel/harmonic/Harmonic.cpp:242-245 | Harmonic |
| 梯度合成（Eq.36/37，STM 用） | src/base/forcemodel/harmonic/Harmonic.cpp:179-198, 219-230, 246-258 | Harmonic |
| VR 归一化校正系数（VR01..VR22） | src/base/forcemodel/harmonic/Harmonic.cpp:298-315 | Harmonic |
| 中心项点质量场 $\vec a=\mu\vec r/r^3$ 与梯度 | src/base/forcemodel/harmonic/HarmonicGravity.cpp:168-195 | HarmonicGravity |
| 全场合成 $\vec a=\vec a_{point}+\vec a_{harmonic}$ | src/base/forcemodel/harmonic/HarmonicGravity.cpp:197-229 | HarmonicGravity |
| 潮汐系数修正 $\bar C+\Delta\bar C$ | src/base/forcemodel/harmonic/HarmonicGravity.cpp:144-166 | HarmonicGravity |
| 固体潮增量 $\Delta\bar C_{nm}=\frac{k_{nm}}{2n+1}(\frac{GM'}{GM})(\frac{a}{R})^{n+1}\bar P_{nm}\cos m\lambda$ | src/base/forcemodel/harmonic/HarmonicGravity.cpp:427-449 | HarmonicGravity |
| 频率相关项/极潮（IERS eq.5a/5b, p.65） | src/base/forcemodel/harmonic/HarmonicGravity.cpp:451-593 | HarmonicGravity |
| Love 数 $k_{nm}$、$k^+_m$ | src/base/forcemodel/harmonic/HarmonicGravity.cpp:276-286 | HarmonicGravity |
| .cof 解析与单位换算 $\mu/10^9$、$a/10^3$、$\bar C=C/V$ | src/base/forcemodel/harmonic/HarmonicGravity.cpp:625-641, 652-695, 755-799 | HarmonicGravity |
| tide-free/zero-tide 判别 $\bar C_{20}>-4.84167\times10^{-4}$ | src/base/forcemodel/harmonic/HarmonicGravity.cpp:1115-1123 | HarmonicGravity |
| 度/阶截断 $n\le360,\ m\le n$ | src/base/forcemodel/HarmonicField.cpp:371-396；GravityField.hpp:155-156 | HarmonicField/GravityField |
| 旋转链 $a_{inertial}=R^\top a_{fixed}$、$G_{in}=R^\top G_{fixed}R$ | src/base/forcemodel/GravityField.cpp:1370-1384, 1453-1555 | GravityField |
| 原点偏移间接项 $a\leftarrow a-a(0)$ | src/base/forcemodel/GravityField.cpp:542-570 | GravityField |
| 潮汐数据链路（体固系位置 + EOP 极移） | src/base/forcemodel/GravityField.cpp:1386-1421, 1492-1522 | GravityField |
| 系数装载/缓存 $\mu=-GetFactor(),\ a=GetFieldRadius()$ | src/base/forcemodel/GravityField.cpp:346-384, 1684-1692 | GravityField |
| 多面体加速度 $a=G\rho(-\sum E_e r_e L_e+\sum F_f R_1\omega_f)$ | plugins/PolyhedronGravityPlugin/src/base/gravitymodel/PolyhedronGravityModel.cpp:424-700（673,678） | PolyhedronGravityModel |
| 边贡献 $E_e=\hat n_a\hat n_{a12}^\top+\hat n_b\hat n_{b21}^\top$、$L_e=\ln\frac{r_1+r_2+e}{r_1+r_2-e}$ | plugins/PolyhedronGravityPlugin/src/base/gravitymodel/PolyhedronGravityModel.cpp:513-550, 572-577 | PolyhedronGravityModel |
| 面贡献与立体角 $\omega_f=2\tan^{-1}\frac{R_1\cdot(R_2\times R_3)}{r_1r_2r_3+r_1R_2\cdot R_3+r_2R_3\cdot R_1+r_3R_1\cdot R_2}$ | plugins/PolyhedronGravityPlugin/src/base/gravitymodel/PolyhedronGravityModel.cpp:612-641, 1122-1148 | PolyhedronGravityModel |
| 变分项与 A 矩阵 $m_1=D^\top(G\rho)(\sum E_eL_e-\sum F_f\omega_f)D$ | plugins/PolyhedronGravityPlugin/src/base/gravitymodel/PolyhedronGravityModel.cpp:584-585, 645-646, 686-698 | PolyhedronGravityModel |
| 旋转矩阵 $C_{IB}=D_3(-\pi/2-RA)D_1(DEC-\pi/2)D_3(-\theta)$ | plugins/PolyhedronGravityPlugin/src/base/gravitymodel/PolyhedronGravityModel.cpp:301-351, 353-415 | PolyhedronGravityModel |
| 面法向/内心/边表（几何预处理） | plugins/PolyhedronGravityPlugin/src/base/gravitymodel/PolyhedronBody.cpp:365-404, 319-354, 449-543 | PolyhedronBody |
