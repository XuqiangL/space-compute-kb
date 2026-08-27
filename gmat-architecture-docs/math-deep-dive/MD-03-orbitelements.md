# 第3章 轨道要素与状态转换数学

## 3.1 总览与约定

### 3.1.1 本章范围与本仓库文件可用性

本章逐条列出 GMAT 中轨道状态表示之间的全部转换公式（笛卡尔↔开普勒六要素、真/平/偏/双曲近点角互换算、无奇点元素集、渐近线元素、Brouwer-Lyddane 平均根数、状态转换偏导），以及参数层（`src/base/parameter` 轨道要素参数类的 `Evaluate`）与平动点（LibrationPoint）的数学实现。

> ⚠️ 本仓库（depth-1 克隆）与上游 GMAT 的目录布局略有差异，任务清单中以下文件**在本仓库中不存在**，本章按其真实等价物覆盖：
>
> - `src/gmatutil/util/Anomaly.*` → 不存在。近点角换算全部集中在 `src/gmatutil/util/StateConversionUtil.*`（3.3 节），另有单元测试 `src/UnitTests/TestAnomaly/TestAnomaly.cpp` 可佐证行为。
> - `src/gmatutil/util/OrbitData.*` → 不存在。`OrbitData` 位于 `src/base/parameter/OrbitData.*`（3.10.1 节）。
> - `src/base/spacecraft/SpacecraftOrbitState.*` → 不存在。轨道状态参数化由 `src/base/spacecraft/Spacecraft.cpp` 的 `GetStateInRepresentation` / `SetStateFromRepresentation` / `GetElement` 承担（3.11 节）。

术语（状态表示命名、继承体系、Spacecraft 状态容器）与[第6章 §2.2.4、§2.3](../CH06-dynamics.md) 保持一致，本章只补充公式与推导，不重复架构描述。

### 3.1.2 状态表示与角度/单位约定

`StateConversionUtil::StateType` 枚举（`src/gmatutil/util/StateConversionUtil.hpp:56-73`）定义 14 种状态表示：`Cartesian, Keplerian, ModifiedKeplerian, SphericalAZFPA, SphericalRADEC, Equinoctial, ModifiedEquinoctial, AlternateEquinoctial, Delaunay, Planetodetic, OutgoingAsymptote, IncomingAsymptote, BrouwerMeanShort, BrouwerMeanLong`。近点角类型 `AnomalyType`（`StateConversionUtil.hpp:75-82`）：`TA=0, MA=1, EA=2, HA=3`，长/短文本表见 `StateConversionUtil.cpp:145-153`。

**单位约定**（全库一致）：
- 笛卡尔状态：位置 km、速度 km/s；开普勒状态：`[a(km), e, i(°), RAAN(°), AOP(°), 近点角(°)]`。
- 近点角**互换算函数**一律以**弧度**为输入/输出（`taRadians/maRadians`），只有经 `RAD_PER_DEG / DEG_PER_RAD`（`src/gmatutil/util/GmatConstants.hpp:192-195`）包装后才进状态向量；`CartesianToTA/MA/EA/HA` 等以 `inRadian` 参数决定输出单位，默认输出**度**。
- `ComputeCartToKepl` 内部角度用弧度，输出 `elem[2..5]` 前乘 `DEG_PER_RAD`（`StateConversionUtil.cpp:7837-7840`）。

### 3.1.3 容差常量

`StateConversionUtil.cpp:76-87`：`ORBIT_TOL=1e-10`、`ORBIT_TOL_SQ=1e-20`、`SINGULAR_TOL=1e-3`（近点半径 < 1 m 判据）、`INFINITE_TOL=1e-30`、`PARABOLIC_TOL=1e-7`（近抛物线判据）、`MU_TOL=1e-15`、`EQUINOCTIAL_TOL=1e-5`、`ANGLE_TOL=0.0`、`MAX_ITERATIONS=75`。

轨道常数（`src/gmatutil/util/GmatConstants.hpp:219-233`，`namespace GmatOrbitConstants`）：`KEP_TOL=1e-11`、`KEP_ANOMALY_TOL=1e-12`、`KEP_ZERO_TOL=1e-30`、`KEP_ECC_TOL=1e-7`（近抛物线/近圆判据，注释注明由数值实验确定）、`ECC_RANGE_TOL=1e-5`、`ORBIT_REAL_UNDEFINED`（参数未定义哨兵值）。

---

## 3.2 笛卡尔 ↔ 开普勒六要素

### ComputeCartToKepl —— 笛卡尔 → 开普勒核心（角动量/偏心率矢量法）

- **公式**：
  $$\mathbf h = \mathbf r\times\mathbf v,\qquad h=|\mathbf h|,\qquad \mathbf n=\hat{\mathbf z}\times\mathbf h,\qquad n=|\mathbf n|$$
  $$\mathbf e=\frac{1}{\mu}\left[\left(v^2-\frac{\mu}{r}\right)\mathbf r-(\mathbf r\cdot\mathbf v)\mathbf v\right],\qquad \zeta=\frac{v^2}{2}-\frac{\mu}{r},\qquad a=-\frac{\mu}{2\zeta}$$
  $$i=\cos^{-1}\!\left(\frac{h_z}{h}\right)$$
  四情形（按"是否圆轨道 × 是否赤道轨道"分派）：
  - 情形1（非圆、倾斜）：$\Omega=\cos^{-1}(n_x/n)$（$n_y<0$ 时取 $2\pi-\Omega$）；$\omega=\cos^{-1}(\mathbf n\cdot\mathbf e/(ne))$（$e_z<0$ 时取 $2\pi-\omega$）；$\nu=\cos^{-1}(\mathbf e\cdot\mathbf r/(er))$（$\mathbf r\cdot\mathbf v<0$ 时取 $2\pi-\nu$）
  - 情形2（非圆、赤道）：$\Omega=0$，$\omega=\cos^{-1}(e_x/e)$（$e_y<0$ 修正；逆行时 $\omega\to-\omega$），$\nu$ 同情形1
  - 情形3（圆、倾斜）：$\Omega=\cos^{-1}(n_x/n)$，$\omega=0$，$\nu=\cos^{-1}(\mathbf n\cdot\mathbf r/(nr))$（$r_z<0$ 修正）
  - 情形4（圆、赤道）：$\Omega=0,\ \omega=0,\ \nu=\cos^{-1}(r_x/r)$（$r_y<0$ 修正；逆行时 $\nu\to-\nu$）

- **代码位置**：`src/gmatutil/util/StateConversionUtil.cpp:7632-7843`

- **深度讲解**：
  代码对公式的逐行映射（`StateConversionUtil.cpp:7648-7842`）：

  ```cpp
  Rvector3 angMomentum = Cross(pos, vel);            // h = r × v（式 4.1）
  Real h = angMomentum.GetMagnitude();               // h = |h|
  Rvector3 v3(0.0,0.0,1.0);
  Rvector3 nodeVec = Cross(v3, angMomentum);         // n = ẑ × h（式 4.3）
  Real n = nodeVec.GetMagnitude();                   // n = |n|（式 4.4）
  Real posMag = pos.GetMagnitude();  Real velMag = vel.GetMagnitude();
  Rvector3 eccVec = (1/grav)*((velMag*velMag - grav/posMag)*pos
                     - (pos * vel) * vel);           // 偏心率矢量（式 4.7-4.8）
  Real e = eccVec.GetMagnitude();
  Real zeta = 0.5*velMag*velMag - (grav/posMag);    // 比机械能（式 4.9）
  Real sma = -grav/(2*zeta);                         // a = -μ/(2ζ)（式 4.10）
  Real i = ACos( angMomentum.Get(2)/h );            // i = acos(h_z/h)（式 4.11）
  ```
  - **数学推导要点**：`e_vec` 公式可由拉普拉斯–龙格–楞次矢量 $(\mathbf v\times\mathbf h)/\mu - \hat{\mathbf r}$ 展开得到；能量式 $\zeta=\xi$ 与半通径无关，直接给出半长轴。近点半径判据 `|a(1−e)| < 1e-3`（km，注释"must be greater than 1 meter"）在 `StateConversionUtil.cpp:7729-7735` 拦截奇异圆锥曲线。
  - **象限处理**：全部角度用 `ACos` 主值（$[0,\pi]$）再按分量符号补 $2\pi$，这与 3.3 节的 `ATan2` 家族不同；`pos*vel < 0`（正在趋近近地点）是 $\nu$ 的象限判据。
  - **奇点处理**：`i≈0` 时节点矢量消失（情形2/4 直接置 $\Omega=0$）；`e≈0` 时近地点矢量消失（情形3/4 置 $\omega=0$，$\nu$ 改由 $\mathbf n$ 或 $\mathbf r$ 度量）；`Abs(1−e) ≤ KEP_ECC_TOL`（1e-7）抛"GMAT does not support parabolic orbits"（`7714-7719`）；`h==0`（共线状态）抛异常（`7737-7740`）；`n==0` 且情形需要时抛异常（`7761-7764`）。
  - 逆行轨道（$i>180°$ 的镜像）修复见 `GMT-4446` 注释（`7791-7794, 7828-7832`）：情形2 的 $\omega$、情形4 的 $\nu$ 取负后归一到 $[0,2\pi)$。

### ComputeKeplToCart —— 开普勒 → 笛卡尔核心（经典轨道坐标方程）

- **公式**：
  $$p=a(1-e^2),\qquad r=\frac{p}{1+e\cos\nu}$$
  $$\mathbf r=r\begin{pmatrix}\cos(\omega+\nu)\cos\Omega-\cos i\,\sin(\omega+\nu)\sin\Omega\\ \cos(\omega+\nu)\sin\Omega+\cos i\,\sin(\omega+\nu)\cos\Omega\\ \sin(\omega+\nu)\sin i\end{pmatrix}$$
  $$\mathbf v=\sqrt{\frac{\mu}{p}}\begin{pmatrix} (\cos\nu+e)(-\sin\omega\cos\Omega-\cos i\sin\Omega\cos\omega)-\sin\nu(\cos\omega\cos\Omega-\cos i\sin\Omega\sin\omega)\\ (\cos\nu+e)(-\sin\omega\sin\Omega+\cos i\cos\Omega\cos\omega)-\sin\nu(\cos\omega\sin\Omega+\cos i\cos\Omega\sin\omega)\\ (\cos\nu+e)\sin i\cos\omega-\sin\nu\sin i\sin\omega\end{pmatrix}$$

- **代码位置**：`src/gmatutil/util/StateConversionUtil.cpp:7862-7979`

- **深度讲解**：
  若输入近点角是 MA，先经 `ComputeMeanToTrueAnomaly` 换成 TA（`7875-7885`，默认容差 1e-8）。核心片段（`7894-7976`）：

  ```cpp
  Real p = sma*(1 - ecc*ecc);                        // 半通径（式 4.24）
  if (Abs(p) < INFINITE_TOL) return 2;               // 近抛物线，p→0
  Real onePlusECos = 1 + ecc*Cos(anom);
  if (onePlusECos == 0.0) return 3;                  // 分母为零：半径趋于无穷
  else if (onePlusECos < ORBIT_TOL) { ... }          // 近奇点警告；双曲线时校验
  Real rad = p/onePlusECos;                          // r = p/(1+e·cosν)（式 4.25）
  Real cosPerAnom = Cos(per + anom);                 // cos(ω+ν)
  Real sinPerAnom = Sin(per + anom);
  Real sqrtGravP  = Sqrt(grav/p);                    // √(μ/p)
  r[0] = rad*(cosPerAnom*cosRaan - cosInc*sinPerAnom*sinRaan);   // 式 4.26
  r[1] = rad*(cosPerAnom*sinRaan + cosInc*sinPerAnom*cosRaan);   // 式 4.27
  r[2] = rad* sinPerAnom*sinInc;                     // 式 4.28
  ```
  - **数学推导要点**：速度公式即 $\dot{\mathbf r}$ 在"先绕 $\hat z$ 转 $\Omega$、再绕新 $\hat x$ 转 $i$、再绕新 $\hat z$ 转 $\omega$"的欧拉 3-1-3 旋转链下对近点角求导，径向/切向分量为 $\dot r=\sqrt{\mu/p}\,e\sin\nu$、$r\dot\nu=\sqrt{\mu/p}\,(1+e\cos\nu)$。
  - **双曲线 TA 合法性校验**（`7920-7942`）：当 $e>1$ 且 $\nu$ 落入渐近线角 $[\arccos(-1/e),\ 2\pi-\arccos(-1/e)]$ 区间（双曲线无物理点），抛异常，这是"双曲线情形"的核心守卫。
  - **奇点处理**：`rad == +inf` 返回错误码 3（`7947-7951`）；`p` 过小判定为抛物线返回 2，由调用方 `KeplerianToCartesian` 转成 "nearly parabolic" 异常（`1608-1615`）。

### KeplerianToCartesian —— 校验包装层

- **公式**：同 `ComputeKeplToCart`；额外做输入合法性修正。
- **代码位置**：`src/gmatutil/util/StateConversionUtil.cpp:1483-1634`（枚举版）、`:1650-1655`（字符串版）

- **深度讲解**：
  - 输入修正（`1496-1529`）：`e<0` → 取反并警告；`(a>0 ∧ e>1)` 或 `(a<0 ∧ e<1)` → `a` 取反（注释：**从双曲线改椭圆时必须先设 ECC**，因为 $a$ 的符号依赖 $e$）；`mu < MU_TOL` 抛异常（`1536-1543`）。
  - 奇点守卫（`1547-1570`）：`|a(1−e)| < SINGULAR_TOL`（近地点半径 < 1 m）抛异常；`|1−e| < PARABOLIC_TOL`（1e-7）判近抛物线抛异常。双曲线 TA 越界与"半径近无穷"的检查在代码中已注释禁用（`1573-1602`），实际改由 `ComputeKeplToCart` 内部拦截。
  - 错误码映射：`ComputeKeplToCart` 返回 2 → "nearly parabolic"，其他 >0 → 通用失败（`1605-1623`）。

### CartesianToKeplerian —— 包装层（近点角类型处理）

- **公式**：`ComputeCartToKepl` 输出 TA（度）；若请求 MA/EA/HA，再执行 $\nu\to$ 目标近点角（弧度）并转回度：
  $$\text{anomaly} = \text{ConvertFromTrueAnomaly}(type,\ \nu\cdot\text{RAD\_PER\_DEG},\ e)\cdot\text{DEG\_PER\_RAD}$$
- **代码位置**：`src/gmatutil/util/StateConversionUtil.cpp:1280-1321`（枚举版）、`:1340-1346`、`:1363-1369`、`:1386-1392`（字符串/Rvector6 重载）、`:1407-1466`（带 `Real *ma` 出参版）

- **深度讲解**：`1305-1314` 处 `kepOut[5]` 是 `ComputeCartToKepl` 返回的 TA（度），`anomalyType != TA` 时经 `ConvertFromTrueAnomaly`（3.3 节）换算后写回第 6 分量。带 `ma` 指针的重载（`1407-1466`）直接调用 `ComputeCartToKepl` 同时取得 MA，是 `GmatCommand.cpp:2732` 等调用方的底层通道；`mu < MU_TOL` 与 `IsRvValid` 在此层抛出可读错误（`1423-1462`）。

### CartesianToSMA / CartesianToECC / CartesianToINC / CartesianToRAAN / CartesianToAOP —— 单要素提取

- **公式**：
  $$a=-\frac{\mu}{2\left(v^2/2-\mu/r\right)},\qquad e=|\mathbf e|,\qquad i=\cos^{-1}\!\left(\frac{(\mathbf r\times\mathbf v)_z}{|\mathbf r\times\mathbf v|}\right)$$
  $\Omega$、$\omega$：同 3.2.1 的 4 情形公式（$\mathbf n=\hat{\mathbf z}\times\mathbf h$）。
- **代码位置**：SMA `StateConversionUtil.cpp:5354-5402`；ECC `:5418-5433`；INC `:5452-5494`；RAAN `:5512-5586`；AOP `:5605-5677`

- **深度讲解**：
  - SMA（`5369-5393`）：`zeta = v²/2 − μ/r`，`zeta==0` 或 `|1−e|≤KEP_ECC_TOL`（近抛物线）抛异常；`|a(1−e)|<1e-3` 判奇异。
  - ECC（`5425-5426`）：直接取 `CartesianToEccVector` 的模。
  - INC（`5469-5477`）：`h = r×v`，`hMag==0` 抛"angular momentum is a zero vector"；`inc = ACos(h_z/h, KEP_TOL)`（带容差的余弦截断，防 |x|>1 的浮点越界）。
  - RAAN/AOP（`5531-5572, 5625-5664`）：与 `ComputeCartToKepl` 完全相同的 4 情形分派与象限修正；AOP 在圆轨道（情形3/4）直接置 0，在赤道情形（情形2）用 $e$ 矢量 x/y 分量定象限；全部结果 `Mod(·, TWO_PI)` 归一到 $[0,2\pi)$。
  - 这些函数是 `OrbitData::GetKepReal`（3.10.2 节）的直接底层，即 SMA/ECC/INC/TA 等**参数类的最终公式来源**。

### CartesianToEccVector / CartesianToDirOfLineOfNode / CartesianToAngularMomentum —— 矢量中间量

- **公式**：
  $$\mathbf e=\frac{(v^2-\mu/r)\,\mathbf r-(\mathbf r\cdot\mathbf v)\,\mathbf v}{\mu},\qquad \mathbf n=\hat{\mathbf z}\times(\mathbf r\times\mathbf v),\qquad \mathbf h=\mathbf r\times\mathbf v,\ p=\frac{h^2}{\mu}$$
- **代码位置**：`StateConversionUtil.cpp:5694-5712`；`:5726-5731`；`:5752-5778`

- **深度讲解**：
  - `CartesianToEccVector`（`5704`）：单行公式实现；`mu==0 || rMag==0` 抛异常（`5699-5702`）。注意该式在近抛物线（$\zeta\to0$ 即 $e\to1$）时仍是良态矢量，只是 $e$ 趋于 1。
  - `CartesianToDirOfLineOfNode`（`5728-5730`）：$\mathbf n=\hat{\mathbf z}\times\mathbf h$，**未归一化**，由调用方自行归一化。
  - `CartesianToAngularMomentum`（`5759-5771`）：返回 6 元组 `[ĥ_x, ĥ_y, ĥ_z, h, v², p]`——角动量单位矢量、模、速度平方、轨道参数 $p=h^2/\mu$；`mu==0` 抛异常。

### KeplerianToModKeplerian / ModKeplerianToKeplerian —— 改进开普勒（近地点/远地点半径）

- **公式**：
  $$r_p=a(1-e),\qquad r_a=a(1+e)$$
  $$\text{逆：}\quad e=\frac{1-r_p/r_a}{1+r_p/r_a},\qquad a=\frac{r_p}{1-e}$$
- **代码位置**：`StateConversionUtil.cpp:1888-2003`；`:2017-2055`

- **深度讲解**：
  - 正变换（`1989-1990`）前做完整校验：`a==1 || IsInf(a)` 判抛物线（`1900-1903`，注意这里 `a==1` 疑似笔误，意图是"半通径无定义"类检查，随后 `1973-1979` 用 `|e−1|<2·REAL_EPSILON` 补判）；`e<0`、`(a>0∧e>1)`、`(a<0∧e<1)` 修正与 `KeplerianToCartesian` 相同（`1906-1942`）；`|a(1−e)|<SINGULAR_TOL` 与 `|1−e|<PARABOLIC_TOL` 守卫（`1945-1968`）。
  - 逆变换（`2046-2050`）：`rpbyra = radPer/radApo`，`e=(1−rpbyra)/(1+rpbyra)`，`a=radPer/(1−e)`。校验 `radApo==0`、`radApo<radPer∧radApo>0`、`radPer≤0`（双曲线时允许 $r_a<0$，见 `2031-2038` 的"RadApo 必须为负"约定与 `2032-2034` 的"先设 RadApo 再设 RadPer"提示）。

---

## 3.3 近点角换算：TA / MA / EA / HA

### TrueToEccentricAnomaly —— TA → EA（椭圆）

- **公式**（半角恒等式的四象限安全形式）：
  $$\sin E=\frac{\sqrt{1-e^2}\sin\nu}{1+e\cos\nu},\qquad \cos E=\frac{e+\cos\nu}{1+e\cos\nu},\qquad E=\operatorname{atan2}(\sin E,\cos E)$$
- **代码位置**：`StateConversionUtil.cpp:4763-4795`

- **深度讲解**：
  ```cpp
  if (ecc <= (1.0 - GmatOrbitConstants::KEP_ANOMALY_TOL)) {   // 严格椭圆（1e-12 余量）
     Real cosTa = Cos(taRadians);
     Real eccCosTa = ecc * cosTa;
     Real sinEa = (Sqrt(1.0 - ecc*ecc) * Sin(taRadians)) / (1.0 + eccCosTa);
     Real cosEa = (ecc + cosTa) / (1.0 + eccCosTa);
     ea = ATan2(sinEa, cosEa);                                 // 四象限，规避 tan 半角奇点
  }
  if (ea < 0.0) ea = ea + TWO_PI;                              // 归一到 [0, 2π)
  ```
  - **数学推导要点**：由椭圆极坐标 $r\cos\nu=a(\cos E-e)$ 与 $r\sin\nu=a\sqrt{1-e^2}\sin E$ 相除即得；用 `atan2` 而非 `tan(E/2)` 公式，避免 $\nu=\pi$（$E=\pi$）处 $1+e\cos\nu\to1-e\ne0$ 但半角公式分支混乱的问题。
  - **奇点处理**：$e>1-\text{KEP\_ANOMALY\_TOL}$（近抛物线/双曲线）时 `ea` 保持 0 返回（`4772-4780`）——调用方若期望双曲线应走 `TrueToHyperbolicAnomaly`；`modBy2Pi` 时循环减 $2\pi$（`4784-4788`）。

### EccentricToTrueAnomaly —— EA → TA（椭圆）

- **公式**：
  $$\sin\nu=\frac{\sqrt{1-e^2}\sin E}{1-e\cos E},\qquad \cos\nu=\frac{\cos E-e}{1-e\cos E},\qquad \nu=\operatorname{atan2}(\sin\nu,\cos\nu)$$
- **代码位置**：`StateConversionUtil.cpp:4915-4934`

- **深度讲解**：`oneMinusECosE == 0`（即 $E$ 使 $e\cos E=1$，椭圆下不可能，双曲线下对应无穷远）显式抛除零异常（`4920-4923`）；`modBy2Pi` 分支 `while (ta) ta -= TWO_PI;` 是**代码缺陷**——`ta` 非零时循环永不退出（`4930-4931`），实践中该标志极少以 true 调用，属潜在死循环，改造时应删去。

### TrueToHyperbolicAnomaly —— TA → HA（双曲线）

- **公式**（半角双曲正切）：
  $$\tanh\frac{H}{2}=\tan\frac{\nu}{2}\sqrt{\frac{e-1}{e+1}},\qquad H=2\,\operatorname{artanh}\!\left(\tan\frac{\nu}{2}\sqrt{\frac{e-1}{e+1}}\right)$$
- **代码位置**：`StateConversionUtil.cpp:4813-4856`

- **深度讲解**：仅在 $e\ge 1+\text{KEP\_TOL}$ 时计算（`4821-4835`），否则返回 0。注释掉的备选实现（`4826-4834`）给出 $\sinh H=\sin\nu\sqrt{e^2-1}/(1+e\cos\nu)$、$H=\operatorname{asinh}$ 形式——两条路线数学等价，代码最终采用 $2\operatorname{atanh}$ 形式以避免 $\operatorname{asinh}$ 的参数域问题；$1+e\cos\nu=0$（$\nu$ 在渐近线角 $\arccos(-1/e)$）时被规避。`modBy2Pi` 分支被整段注释（`4847-4853`）：$H$ 是"伪角"，不应当按 $2\pi$ 取模。

### HyperbolicToTrueAnomaly —— HA → TA（双曲线）

- **公式**：
  $$\sin\nu=\frac{\sqrt{e^2-1}\sinh H}{1-e\cosh H},\qquad \cos\nu=\frac{\cosh H-e}{1-e\cosh H},\qquad \nu=\operatorname{atan2}(\sin\nu,\cos\nu)$$
- **代码位置**：`StateConversionUtil.cpp:4949-4969`

- **深度讲解**：分母 `1−e·coshH == 0`（$H=0$ 附近 $e\cosh H=1$ 有解，对应近点附近半径有限的合法情形外）抛除零异常（`4954-4957`）；`modBy2Pi` 分支同样存在 `while (ta)` 死循环缺陷（`4963-4967`）。

### TrueToMeanAnomaly —— TA → MA（含双曲线/近抛物线）

- **公式**：
  $$\text{椭圆：}\ M=E-e\sin E;\qquad \text{双曲线：}\ M=e\sinh H-H;\qquad \text{近抛物线：}\ M:=0\ (\text{警告})$$
- **代码位置**：`StateConversionUtil.cpp:4706-4747`

- **深度讲解**：按 $e$ 三分支（`4715-4740`）：
  ```cpp
  if (ecc < (1.0 - KEP_TOL)) {                 // 椭圆：E ← ν，再开普勒方程
     Real ea = TrueToEccentricAnomaly(taRadians, ecc);
     ma = ea - ecc * Sin(ea);
     if (ma < 0.0) ma = ma + TWO_PI;           // 椭圆 MA 归一到 [0, 2π)
  }
  else if (ecc > (1.0 + KEP_TOL)) {            // 双曲线：F ← ν，再双曲开普勒方程
     Real ha = TrueToHyperbolicAnomaly(taRadians, ecc);
     ma = ecc * Sinh(ha) - ha;                 // 不取模！MA 在双曲线下无周期
  }
  else { /* 警告 "near parabolic"，MA = 0 */ }  // 1e-11 带内判近抛物线
  ```
  - **数学推导要点**：开普勒方程 $M=E-e\sin E$ 的逆；双曲线对应 $M=e\sinh H-H$（$M$ 随 $H$ 单调增长，无 $2\pi$ 周期，故**不取模**——与椭圆分支的 `+TWO_PI` 归一形成鲜明对比）。
  - **调用方**：`GmatCommand.cpp:2732`、`Code500EphemerisFile.cpp:1663`、`DelaunayToKeplerian` 链路（`StateConversionUtil.cpp:2602`）均使用之。

### MeanToTrueAnomaly / ComputeMeanToTrueAnomaly —— MA → TA（Newton–Raphson 解开普勒方程）

- **公式**：
  $$\text{椭圆：}\ E_{k+1}=E_k-\frac{E_k-e\sin E_k-M}{1-e\cos E_k},\quad E_0=M+e\sin M;\qquad \tan\frac{\nu}{2}=\sqrt{\frac{1+e}{1-e}}\tan\frac{E}{2}$$
  $$\text{双曲线：}\ H_{k+1}=H_k-\frac{e\sinh H_k-H_k-M}{e\cosh H_k-1},\quad H_0=0;\qquad \tan\frac{\nu}{2}=\sqrt{\frac{e+1}{e-1}}\tanh\frac{H}{2}$$
  （抛物线情形代码未实现 Barker 方程，直接判错返回）
- **代码位置**：`MeanToTrueAnomaly` `StateConversionUtil.cpp:4872-4900`；`ComputeMeanToTrueAnomaly` `:7995-8153`

- **深度讲解**：
  椭圆分支（`8012-8090`）：
  ```cpp
  e2 = rm + ecc * Sin(rm);                       // E₀ = M + e·sinM（GTDS 3-182）
  while (!done) {
     temp = 1.0 - ecc * Cos(e2);                 // f'(E) = 1 − e·cosE（GTDS 3-180，
                                                 //  注释：用 Cos(E) 而非 Cos(E−f/2)）
     if (Abs(temp) < ztol) return (3);           // 导数近零 → 发散
     e1 = e2 - (e2 - ecc*Sin(e2) - rm)/temp;     // Newton 步（GTDS 3-181）
     if (Abs(e2-e1) < tol) done = true;          // 收敛判据：|ΔE| < tol（默认 1e-8）
     e2 = e1;
  }
  if (e < 0.0) e = e + TWO_PI;
  c = Abs(e - PI);
  if (c >= 1.0e-08) {                            // E ≈ π 时 tan(E/2) 发散 →
     f = Sqrt((1.0+ecc)/(1.0-ecc));              //  (1+e)/(1−e) 恒正（e<1）
     g = Tan(e/2.0);
     *ta = 2.0*ATan(f*g);                        // ν = 2·atan(√((1+e)/(1−e))·tan(E/2))
  } else *ta = e;                                // 直接取 ν = E（π 邻域）
  ```
  - 双曲线分支（`8092-8149`）：初值 `f2 = 0`（`8105`，注释指出这才是**正确初值**，GTDS 3-186 的 $M/2$ 被注释为 incorrect）；Newton 迭代 `f1 = f2 − (e·sinh f2 − f2 − rm)/(e·cosh f2 − 1)`（`8124`）；`temp2=(e+1)/(e−1)>0` 保证 $\sqrt{\cdot}$ 定义域（`8138-8142`）；`ν = 2·atan(√((e+1)/(e−1))·tanh(H/2))`（`8145`），`ν<0` 补 $2\pi$（`8147-8148`）。
  - **Barker 方程说明**：抛物线（$e=1$）走椭圆分支的 $e\le1$ 判据（`8012`），但 $e=1$ 时 $f'(E)=1-\cos E$ 在 $E=0$ 处为零、`temp2=(1+e)/(1−e)` 发散，最终由 `temp2 < 0`/`Abs(temp)<ztol` 的返回码（5/6）兜底报错——**代码没有实现 Barker 方程**（抛物线情形 3.3.8 的 `CalculateEccentricAnomalyParabola` 亦直接抛"not implemented"，`StateConversionUtil.cpp:6976-6989`）。
  - 迭代上限 1000 次防死循环（`8028-8034, 8111-8117`）；返回码 3/5/6/7/9/10 分别对应导数零、$1-e=0$、$(1+e)/(1-e)<0$、$\cosh$ 发散、$e-1=0$、$(e+1)/(e-1)<0$。

### ConvertFromTrueAnomaly / ConvertToTrueAnomaly —— 近点角派发开关

- **公式**：$\nu\to\{\nu,\ M,\ E,\ H\}$ 与 $\{\nu,\ M,\ E,\ H\}\to\nu$ 的统一派发。
- **代码位置**：`StateConversionUtil.cpp:4986-4990`、`:5007-5023`（From）；`:5040-5044`、`:5061-5076`（To）

- **深度讲解**：字符串版先经 `GetAnomalyType`（`7466-7487`，支持 "TA"/"True Anomaly" 等长短名）解析枚举。From 开关（`5012-5019`）：`MA→TrueToMeanAnomaly`、`EA→TrueToEccentricAnomaly`、`HA→TrueToHyperbolicAnomaly`；To 开关（`5065-5072`）：`MA→MeanToTrueAnomaly`（注意此处**未传递** `modBy2Pi`，且用默认容差 1e-8）、`EA→EccentricToTrueAnomaly`、`HA→HyperbolicToTrueAnomaly`。`CartesianToKeplerian`（3.2.4）与 `Spacecraft::GetElement`（3.11）都经它完成"任意近点角 ↔ 真近点角"的桥接。

### CartesianToTA / CartesianToMA / CartesianToEA / CartesianToHA —— 由笛卡尔状态直接取近点角

- **公式**：
  $$\nu=\begin{cases}\cos^{-1}(\mathbf e\cdot\mathbf r/(er)),&\mathbf r\cdot\mathbf v\ge0\\ 2\pi-\cos^{-1}(\mathbf e\cdot\mathbf r/(er)),&\mathbf r\cdot\mathbf v<0\end{cases}\ (\text{非圆})$$
  圆轨道时 $\mathbf e$ 以 $\mathbf n$（情形3）或 $\mathbf r$ 的 x 分量（情形4）代替；$M,E,H$ 由 3.3.1/3.3.5 链式得出。
- **代码位置**：TA `StateConversionUtil.cpp:5095-5217`；MA `:5236-5255`；EA `:5275-5294`；HA `:5313-5333`

- **深度讲解**：`CartesianToTA` 与 `ComputeCartToKepl` 同构的四情形分派（`5131-5204`），但独立于主转换（供参数层单点求值，避免整组转换）；`ta = Mod(ta, TWO_PI)` 归一到 $[0,2\pi)$（`5207`）；`rMag==0` 抛异常（`5118-5121`）。MA/EA/HA 均为"先 TA 后换"的 3 行组合（如 `5236-5255`：`ta=CartesianToTA(...,true)` → `ecc=CartesianToECC` → `ma=TrueToMeanAnomaly(ta,ecc)`），默认输出度，`inRadian=true` 输出弧度。双曲线下 `CartesianToHA` 若 $e\le1$ 则 `TrueToHyperbolicAnomaly` 返回 0（3.3.3），属设计行为。

### CalculateEccentricAnomaly（椭圆/双曲线/抛物线三分支）

- **公式**：
  $$\text{椭圆：}\ E_0=M+e\sin M;\quad E_{k+1}=E_k-\frac{E_k-e\sin E_k-M}{1-e\cos(E_k-f_k/2)},\ f_k=E_k-e\sin E_k-M$$
  $$\text{双曲线：}\ E_0=M/2;\quad E_{k+1}=E_k-\frac{e\sinh E_k-E_k-M}{e\cosh E_k-1}$$
- **代码位置**：`StateConversionUtil.cpp:6926-6939`（分派）、`:6941-6957`（椭圆）、`:6959-6973`（双曲线）、`:6976-6989`（抛物线）

- **深度讲解**：这是**以偏近点角为未知量的开普勒方程解算器**（与 3.3.6 的 `ComputeMeanToTrueAnomaly` 以真近点角为目标不同），供雅可比矩阵（3.9 节 `CartesianToKeplerianDerivativeConversionWithKeplInput:6038`）在 MA 输入时求 $E$。椭圆版使用 **Danby 修正**：$D=1-e\cos(E-f/2)$（`6952`，GTDS 3-180 的 $E-\tfrac12 f$ 形式），比普通 Newton 收敛更快；双曲线版初值 $M/2$（`6964`，与 3.3.6 的 $H_0=0$ 不一致，是两套实现各自的经验初值）；容差均 1e-12。抛物线版抛 "not implemented"。

---

## 3.4 球坐标与大地坐标

### CartesianToSphericalAZFPA / SphericalAZFPAToCartesian —— 球坐标（半径-赤经-赤纬-速度-方位角-航迹角）

- **公式**：
  $$r=|\mathbf r|,\quad \lambda=\operatorname{atan2}(r_y,r_x),\quad \delta=\sin^{-1}(r_z/r),\quad v=|\mathbf v|,\quad \psi=\cos^{-1}\!\left(\frac{\mathbf r\cdot\mathbf v}{rv}\right)$$
  局部系基矢 $\hat{\mathbf x}_l=(\cos\delta\cos\lambda,\cos\delta\sin\lambda,\sin\delta)$、$\hat{\mathbf y}_l=(-\sin\lambda,\cos\lambda,0)$、$\hat{\mathbf z}_l=(-\sin\delta\cos\lambda,-\sin\delta\sin\lambda,\cos\delta)$，方位角 $\alpha_F=\operatorname{atan2}(v_{l,y},v_{l,z})$；
  $$\mathbf r=r(\cos\delta\cos\lambda,\ \cos\delta\sin\lambda,\ \sin\delta)$$
  $$\mathbf v=v\begin{pmatrix}\cos\psi\cos\delta\cos\lambda-\sin\psi(\sin\alpha_F\sin\lambda+\cos\alpha_F\sin\delta\cos\lambda)\\ \cos\psi\cos\delta\sin\lambda+\sin\psi(\sin\alpha_F\cos\lambda-\cos\alpha_F\sin\delta\sin\lambda)\\ \cos\psi\sin\delta+\sin\psi\cos\alpha_F\cos\delta\end{pmatrix}$$
- **代码位置**：`StateConversionUtil.cpp:1671-1727`；`:1740-1777`

- **深度讲解**：
  - 正变换（`1676-1726`）：`rMag < 1e-10` 或 `vMag < 1e-10` 抛"undefined"异常（`1678-1686, 1694-1702`）；`psi = ACos(r·v/(rMag·vMag))` 是**垂直航迹角**（与速度的夹角，$[0,\pi]$）；本地帧由 `Rli = [x y z]ᵀ` 构造（`1715-1717`，即"列向量为基、转置得旋转矩阵"），`vLocal = Rli * vel` 后 `alphaF = ATan2(vLocal[1], vLocal[2])`（`1723`）——注意 `ATan2(y,z)` 的**分量顺序**是代码约定。输出顺序 `[rMag, λ°, δ°, vMag, αF°, ψ°]`（`1725-1726`）。
  - 逆变换（`1754-1773`）：`vx/vy/vz` 三行正是 $v[\cos\psi\,\hat{\mathbf x}_l-\sin\psi(\sin\alpha_F\hat{\mathbf y}_l+\cos\alpha_F\hat{\mathbf z}_l)]$ 的展开。角度输入乘 `RAD_PER_DEG`（`1747-1751`）。
  - **奇点**：$\delta=\pm90°$ 时 $\lambda$ 无定义（代码未特判，靠 `rMag` 检查兜底）；$\psi$ 用 `acos` 主值天然在 $[0,\pi]$，避免象限歧义。

### CartesianToSphericalRADEC / SphericalRADECToCartesian —— 球坐标（赤经赤纬，速度独立表示）

- **公式**：
  $$\lambda=\operatorname{atan2}(r_y,r_x),\ \delta=\sin^{-1}(r_z/r),\ \lambda_V=\operatorname{atan2}(v_y,v_x),\ \delta_V=\sin^{-1}(v_z/v)$$
  $$\mathbf r=r(\cos\delta\cos\lambda,\cos\delta\sin\lambda,\sin\delta);\qquad \mathbf v=v(\cos\delta_V\cos\lambda_V,\ \cos\delta_V\sin\lambda_V,\ \sin\delta_V)$$
- **代码位置**：`StateConversionUtil.cpp:1790-1831`；`:1844-1875`

- **深度讲解**：与 AZFPA 版共享 $\lambda/\delta$ 计算与 `rMag/vMag < 1e-10` 守卫（`1797-1821`），区别在于速度不分解为航迹角/方位角，而是直接给出速度矢量的赤经赤纬 `(λV, δV)`（`1824-1827`）。逆变换实现中 `vy = vx * Tan(lambdaV)`（`1865`）等价于 $v\cos\delta_V\sin\lambda_V$——这是"先算 $v_x$ 再乘 $\tan\lambda_V$"的写法，在 $\lambda_V=90°$（$\cos\lambda_V=0$）处**数值脆弱**，但数学等价；`RADECToCartesian` 不检查 $v_x=0$，是该实现的已知弱点。输出顺序 `[rMag, λ°, δ°, vMag, λV°, δV°]`。

### CartesianToPlanetodetic / PlanetodeticToCartesian —— 大地坐标（迭代法）

- **公式**（正变换，$e^2=2f-f^2$ 为第一偏心率平方）：
  $$\phi_{k+1}=\tan^{-1}\!\left(\frac{r_z+C_k e^2\sin\phi_k}{r_{xy}}\right),\qquad C_k=\frac{R_{eq}}{\sqrt{1-e^2\sin^2\phi_k}}$$
  逆变换（$\hat h=\text{alt}/R_{eq}$ 为归一化高度）：
  $$\phi_g=\phi_d+\frac{-\sin 2\phi_d}{1+\hat h}f+\left(\frac{-\sin 2\phi_d}{2(1+\hat h)^2}+\frac{1}{4(1+\hat h)^2}+\frac{1}{4(1+\hat h)}\sin 4\phi_d\right)f^2$$
  （Vallado 二阶级数修正，用于纬度的快速反演）
- **代码位置**：`StateConversionUtil.cpp:2674-2719`；`:2739-2843`

- **深度讲解**：
  - 正变换（`2678-2717`）：先转 `SphericalAZFPA` 得到地心系要素（`2678`），再用**不动点迭代**把地心纬度 $\phi_g$ 换成大地纬度 $\phi_d$：`C = Req/√(1−e²sin²φ_old)`，`latd = ATan((r_z + C·e²·sin φ_old)/r_xy)`（`2711-2712`），容差 1e-13（`2701`）；输出第 6 分量是**水平**航迹角 `hfpa = 90 − vfpa`（`2691, 2717`）。
  - 逆变换（`2757-2842`）：先校验纬度 $[-90,90]$ 与 hfpa $[-90,90]$（`2757-2792`）；再做 $\phi_g$ 的级数反演（`2804-2829`），近 ±90° 时直接令 $\phi_g=\phi_d$（`2807-2812`）；最后转回 `SphericalAZFPA` 再转笛卡尔（`2840`）。
  - **奇点**：$r_{xy}\to0$（极轴）时 $\phi$ 迭代仍收敛但 $\lambda$ 无定义；纬度近 ±90° 分支显式处理（`2807-2812`）。单位：经度/纬度/航迹角输出度。

---

## 3.5 无奇点元素集（赤道型 / 改进型 / 交替型）

### CartesianToEquinoctial —— 笛卡尔 → 经典赤道型元素

- **公式**（$j=1$，顺行）：
  $$h=\mathbf e\cdot\hat{\mathbf g},\quad k=\mathbf e\cdot\hat{\mathbf f},\quad p=\frac{\hat{\mathbf h}_x}{1+\hat{\mathbf h}_z},\quad q=-\frac{\hat{\mathbf h}_y}{1+\hat{\mathbf h}_z}$$
  $$\hat{\mathbf f}=\left(1-\frac{\hat h_x^2}{1+\hat h_z},\ -\frac{\hat h_x\hat h_y}{1+\hat h_z},\ -\hat h_x\right)/|\cdot|,\qquad \hat{\mathbf g}=\hat{\mathbf h}\times\hat{\mathbf f}$$
  $$\beta=\frac{1}{1+\sqrt{1-h^2-k^2}},\quad \cos F=k+\frac{(1-k^2\beta)X_1-hk\beta Y_1}{a\sqrt{1-h^2-k^2}},\quad \sin F=h+\frac{(1-h^2\beta)Y_1-hk\beta X_1}{a\sqrt{1-h^2-k^2}}$$
  $$\lambda=F+h\cos F-k\sin F\qquad (\text{平黄经，度})$$
- **代码位置**：`StateConversionUtil.cpp:2070-2165`

- **深度讲解**：$\mathbf h$ 是角动量单位矢量，$\hat{\mathbf f}/\hat{\mathbf g}$ 定义赤道面内旋转坐标系（`2132-2138`）；$X_1=\mathbf r\cdot\hat{\mathbf f}$、$Y_1=\mathbf r\cdot\hat{\mathbf g}$ 为赤道坐标分量（`2147-2148`）；$F$ 由 `ATan2` 恢复四象限并归一到正（`2159-2161`），$\lambda$ 不取模直接以度输出。**奇点处理**：$e>1-\text{KEP\_ECC\_TOL}$（抛物线/双曲线）抛异常（`2097-2102`，赤道型元素仅定义于椭圆）；$i\ge\pi-\text{KEP\_TOL}$（180° 逆行）抛异常（`2122-2127`）；`|a(1−e)|<1e-3` 判奇异（`2108-2118`）。$p,q$ 分母 $1+\hat h_z$ 在 $i=\pi$ 时为零——正是上面 180° 检查的原因。

### EquinoctialToCartesian —— 赤道型 → 笛卡尔

- **公式**（Newton 迭代解 $\lambda$ 的隐式方程）：
  $$F+h\cos F-k\sin F=\lambda\quad\Rightarrow\quad F_{n+1}=F_n-\frac{F_n+h\cos F_n-k\sin F_n-\lambda}{1-h\sin F_n-k\cos F_n},\ F_0=\lambda$$
  $$n=\sqrt{\frac{\mu}{a^3}},\qquad r=a(1-k\cos F-h\sin F)$$
  $$X_1=a\left((1-h^2\beta)\cos F+hk\beta\sin F-k\right),\qquad Y_1=a\left((1-k^2\beta)\sin F+hk\beta\cos F-h\right)$$
  $$\dot X_1=\frac{na^2}{r}\left(hk\beta\cos F-(1-h^2\beta)\sin F\right),\qquad \dot Y_1=\frac{na^2}{r}\left((1-k^2\beta)\cos F-hk\beta\sin F\right)$$
  $$Q=\frac{1}{1+p^2+q^2}\begin{pmatrix}1-p^2+q^2&2pq&2p\\ 2pq&1+p^2-q^2&-2q\\ -2p&2q&1-p^2-q^2\end{pmatrix},\qquad \mathbf r=X_1\hat{\mathbf f}+Y_1\hat{\mathbf g},\ \mathbf v=\dot X_1\hat{\mathbf f}+\dot Y_1\hat{\mathbf g}$$
- **代码位置**：`StateConversionUtil.cpp:2179-2277`

- **深度讲解**：$F$ 的 Newton 迭代（`2206-2211`）以 $\lambda$ 为初值、容差 `ORBIT_TOL`(1e-10)，是"改进开普勒方程"在赤道型元素下的对应物（$\lambda$ 相当于平近点角、$F$ 相当于偏近点角）；`e=√(h²+k²) ≥ 1−ECC_RANGE_TOL` 抛异常（`2189-2199`），`Sqrt(1−h²−k²)` 的负数域也捕获（`2220-2233`）；`r ≤ 0` 抛异常（`2245-2248`）。$Q$ 矩阵（`2263-2265`，行优先写入 `Rmatrix33`）把赤道平面分量旋转回惯性系，$\hat{\mathbf f},\hat{\mathbf g}$ 取 $Q$ 的**列**（`2268-2271`）。**注意**：$j=1$ 硬编码（`2260`），180° 逆行轨道不支持。

### CartesianToModEquinoctial / ModEquinoctialToCartesian —— 改进型（半通径版）

- **公式**：
  $$p=\frac{h^2}{\mu},\qquad f=\mathbf e\cdot\hat{\mathbf f},\qquad g=\mathbf e\cdot\hat{\mathbf g},\qquad k=\frac{\hat h_x}{1+\hat h_z},\qquad h=-\frac{\hat h_y}{1+\hat h_z}$$
  $$\sin L=\hat r_y-\hat v_x,\quad \cos L=\hat r_x+\hat v_y,\qquad L=\operatorname{atan2}(\sin L,\cos L)\ (\text{真黄经})$$
  $$r=\frac{p}{1+f\cos L+g\sin L},\qquad \dot X_1=-\sqrt{\frac{\mu}{p}}(g+\sin L),\qquad \dot Y_1=\sqrt{\frac{\mu}{p}}(f+\cos L)$$
- **代码位置**：`StateConversionUtil.cpp:2292-2398`；`:2413-2475`

- **深度讲解**：
  - 正变换（`2316-2396`）：`hVec = r×v`，`hMag = |h|`，`p = hMag²/μ`（`2343`）；`vHat = (rMag·v − (r·v)/rMag·r)/hMag`（`2338`，径向外的共速度单位矢量）；真黄经用 `atan2(rHat[1]−vHat[0], rHat[0]+vHat[1])`（`2380-2383`）——这是 $L=\Omega+\omega+\nu$ 的无奇点版本，$i=0$ 时仍良态。奇点守卫：`|1+ĥ_z| < 1e-7` 抛异常（GMT-4174 修复，`2354-2359`），即 $i\to\pi$。
  - 逆变换（`2443-2472`）：`r = p/(1+f·cosL+g·sinL)`（`2443`）是圆锥曲线极坐标的半通径形式；$f$ 与 $\sin$ 项同号、$g$ 与 $\cos$ 项同号——注意**符号约定**：这里 `f,g` 的定义与赤道型 `h,k` 的"投影"恰好互换角色（代码注释 `2425-2428`）。$\hat{\mathbf f},\hat{\mathbf g}$ 显式写出（`2463-2469`），$\alpha2=h²-k²,\ s2=1+h²+k²$。
  - **改进型优势**：以 $p$ 代替 $a$，**双曲线也可表示**（$p>0$ 恒成立），仅校验 `p < 0`（`2438-2441`）与 `mu < MU_TOL`（`2433-2436`）。

### EquinoctialToAltEquinoctial / AltEquinoctialToEquinoctial —— 交替赤道型

- **公式**：
  $$i=2\tan^{-1}\sqrt{p^2+q^2};\qquad \tilde p=p\cos\frac{i}{2},\qquad \tilde q=q\cos\frac{i}{2}$$
  $$\text{逆：}\quad i=2\sin^{-1}\sqrt{\tilde p^2+\tilde q^2};\qquad p=\frac{\tilde p}{\cos(i/2)},\qquad q=\frac{\tilde q}{\cos(i/2)}$$
- **代码位置**：`StateConversionUtil.cpp:4595-4633`；`:4649-4686`

- **深度讲解**：交替型把 $p,q$ 乘以 $\cos(i/2)$ 消除 $i\to180°$ 奇点的一部分，代价是 $|\tilde p|,|\tilde q|<1$ 的取值域（`ValidateValue` 以 `EQUINOCTIAL_TOL` 校验，见 3.10.4）；`i=π`（`IsEqual(i,PI)`）仍抛异常（`4606-4613, 4660-4667`），$a,h,k,\lambda$ 原样透传（`4632, 4685`）。`AltEquinoctialToEquinoctial` 是 `ConvertFromAltEquinoctial` 的第一站（`StateConversionUtil.cpp:877`）。

---

## 3.6 Delaunay 元素

### KeplerianToDelaunay / DelaunayToKeplerian

- **公式**：
  $$L=\sqrt{\mu a},\qquad G=L\sqrt{1-e^2},\qquad H=G\cos i,\qquad l=M,\quad g=\omega,\quad h=\Omega$$
  $$\text{逆：}\quad a=\frac{L^2}{\mu},\qquad e=\sqrt{1-\left(\frac{G}{L}\right)^2},\qquad i=\cos^{-1}\!\left(\frac{H}{G}\right)$$
- **代码位置**：`StateConversionUtil.cpp:2490-2608`；`:2623-2655`

- **深度讲解**：Delaunay 变量是"作用–角"对：角变量 $(l,g,h)$ = (MA, AOP, RAAN)，作用变量 $(L,G,H)$ = 角动量三元组。正变换（`2599-2604`）中 `ll_dela = TrueToMeanAnomaly(ta,ecc)`（`2602`，输入 TA 度 → 输出 MA 度），`gg/hh` 直接透传 AOP/RAAN；双曲线（$e>1+\text{KEP\_ECC\_TOL}$）抛异常（`2571-2575`），因为 $G=L\sqrt{1-e^2}$ 在 $e>1$ 无实义。逆变换（`2647-2652`）校验 `|H|≤|G|` 与 `G/L≤1`（`2630-2645`，保证 $\sqrt{1-(G/L)^2}$ 定义域），`ta = MeanToTrueAnomaly(ll_dela,ecc)`（`2652`）再乘 `DEG_PER_RAD` 输出度。

---

## 3.7 渐近线元素（Incoming / Outgoing Asymptote）

### CartesianToIncomingAsymptote —— 笛卡尔 → 入射渐近线

- **公式**（$c_3=v^2-2\mu/r$ 为 C3 能量，$\mathbf e$ 为偏心率矢量，$\mathbf h=\mathbf r\times\mathbf v$）：
  $$a=-\frac{\mu}{c_3},\qquad r_p=a(1-e),\qquad f=\frac{1}{1+c_3 h^2/\mu^2}$$
  $$c_3>0:\ \hat{\mathbf s}=-\frac{\sqrt{c_3}}{\mu}\left(\mathbf h\times\mathbf e\right)-\mathbf e \ \text{（归一化后）};\qquad c_3<0\ (\text{椭圆}):\ \hat{\mathbf s}=-\mathbf e/e\ (\text{近地点矢量})$$
  $$b_{va}=\operatorname{atan2}(\mathbf b\cdot\hat{\mathbf e}_a/h,\ \mathbf b\cdot(-\hat{\mathbf n}_o)/h),\ \mathbf b=\mathbf h\times\hat{\mathbf s};\qquad \delta_{ha}=\sin^{-1}(\hat s_z),\quad \alpha_{ha}=\operatorname{atan2}(\hat s_y,\hat s_x)$$
- **代码位置**：`StateConversionUtil.cpp:2859-2986`

- **深度讲解**：
  - 渐近线矢量 $\hat{\mathbf s}$（无穷远速度方向）由 $\mathbf h\times\mathbf e$ 与 $\mathbf e$ 的线性组合构造（`2920-2941`）；$c_3<0$（椭圆）时渐近线**不存在**，代码用近地点矢量 `−e/e` 作为"唯一且可逆"的替身（`2930-2941`，SPH 注释说明这是为数值求解器穿越区间的 hack）。
  - 基构造：`eaVec = ẑ×ŝ`（赤经方向）、`noVhat = ŝ×êa`（`2958-2960`），构成"渐近线赤道标架"；`bva`（渐近线方位角）用 `ATan2` 恢复四象限并归正（`2962-2967`）；`dha/rha` 即渐近线方向的天球坐标（`2969-2972`）。真近点角 $\nu=\cos^{-1}(\mathbf e\cdot\mathbf r/(er))$，$\mathbf r\cdot\mathbf v<0$ 时取补角（`2974-2976`）。
  - **奇点/守卫**：`|c3|<1e-7`（近抛物线）、`vMag<1e-7`、`ecc≤1e-7`（近圆，渐近线无定义）均抛异常（`2885-2916`）；$\hat{\mathbf s}$ 与 $\hat{\mathbf z}$ 夹角 <1e-7（赤道面内，$\hat{\mathbf e}_a$ 消失）抛异常（`2948-2956`）。
  - 元素顺序 `[radPer, c3, rha°, dha°, bva°, TA°]`（`2978`）——与 `OrbitData.hpp:257` 的 `INCASYM_*` 枚举一致。

### IncomingAsymptoteToCartesian —— 入射渐近线 → 笛卡尔

- **公式**：
  $$a=-\frac{\mu}{c_3},\qquad e=1-\frac{r_p}{a},\qquad \hat{\mathbf s}=(\cos\delta_{ha}\cos\alpha_{ha},\ \cos\delta_{ha}\sin\alpha_{ha},\ \sin\delta_{ha})$$
  $$\text{ami}=\frac{\pi}{2}-b_{va},\qquad \hat{\mathbf h}_v=\sin(\text{ami})\hat{\mathbf e}_a+\cos(\text{ami})\hat{\mathbf n}_o,\qquad \hat{\mathbf e}=\begin{cases}-\hat{\mathbf s},&c_3\le0\\ \sin\nu_{\max}\hat{\mathbf o}+\cos\nu_{\max}\hat{\mathbf s},&c_3>0\end{cases},\ \nu_{\max}=\cos^{-1}(-1/e)$$
  $$i=\cos^{-1}(\hat{\mathbf z}\cdot\hat{\mathbf h}_v),\qquad \Omega=\cos^{-1}(n_x/n)\ (n_y<0\ \text{修正}),\qquad \omega=\cos^{-1}(\mathbf n\cdot\hat{\mathbf e}/n)\ (e_z<0\ \text{修正})$$
- **代码位置**：`StateConversionUtil.cpp:2999-3130`

- **深度讲解**：由 `radPer/c3` 反解 $a,e$（`3014-3015`），由 `rha/dha` 重建 $\hat{\mathbf s}$（`3042-3045`）；`ami=π/2−bva` 把方位角换算成"无穷远处角动量方向"（`3062-3063`）。$\hat{\mathbf e}$ 的双分支（`3068-3077`）对应正变换的镜像：椭圆取 $-{\hat{\mathbf s}}$，双曲线在渐近线标架内绕 $\hat{\mathbf o}$ 转 $\nu_{\max}$ 角。RAAN/AOP 的赤道/逆行三情形分派（`3083-3114`）与 `ComputeCartToKepl` 一致。最终 `KeplerianToCartesian` 组装（`3116-3129`）。

### CartesianToOutgoingAsymptote / OutgoingAsymptoteToCartesian —— 出射渐近线

- **公式**：与入射版同构，仅渐近线矢量符号翻转：
  $$c_3>0:\ \hat{\mathbf s}=\frac{\sqrt{c_3}}{\mu}\left(\mathbf h\times\mathbf e\right)-\mathbf e;\qquad \hat{\mathbf e}=-\sin\nu_{\max}\hat{\mathbf o}+\cos\nu_{\max}\hat{\mathbf s}\ (c_3>0\ \text{逆变换})$$
- **代码位置**：`StateConversionUtil.cpp:3144-3249`；`:3263-3392`

- **深度讲解**：正变换 `3199` 与入射版 `2926` 相比 $\sqrt{c_3}$ 项符号相反（出射方向取"远离"分支）；椭圆替身同样取 `−e/e`（`3205`）。逆变换 `3340` 与入射版 `3076` 的 $\sin\nu_{\max}$ 项符号相反。其余（$\hat{\mathbf e}_a/\hat{\mathbf n}_o$ 标架、`bva`、四情形 RAAN/AOP）与 3.7.1/3.7.2 完全对称，守卫阈值相同（`3159-3190, 3282-3306`）。

---

## 3.8 Brouwer-Lyddane 平均根数（仅地球，J₂ 摄动）

### BrouwerMeanShortToOsculatingElements —— 短周期项平均根数 → 吻切根数

- **公式**（$\bar a,\bar e,\bar i,\bar\Omega,\bar\omega,\bar M$ 为输入；$a_e$=地球半径，$J_2$=1.082626925638815e-3）：
  $$\eta=\sqrt{1-\bar e^2},\quad \theta=\cos\bar i,\quad \bar p=\bar a\eta^2,\quad k_2=\tfrac12 J_2,\quad \gamma_2=\frac{k_2}{\bar a^2},\quad \gamma_{2p}=\frac{\gamma_2}{\eta^4}$$
  $$\nu=\text{MA→TA}(\bar M,\bar e),\qquad r=\frac{\bar p}{1+\bar e\cos\nu},\qquad \frac{\bar a}{r}\equiv \text{adr}$$
  $$a=\bar a+\bar a\gamma_2\left[\left(\text{adr}^3-\eta^{-3}\right)(-1+3\theta^2)+3(1-\theta^2)\text{adr}^3\cos(2\bar\omega+2\nu)\right]$$
  $\Delta e$、$\Delta i$、$\Delta\Omega$、$\omega$、$M$、$\ell+g+h$（lgh）的短周期修正见代码 `3802-3826`；最终偏心率的"长分量 + 短分量"合成：
  $$e\cos M=(e+\Delta e)\cos\bar M-e_{\text{dl}}\sin\bar M,\qquad e\sin M=(e+\Delta e)\sin\bar M+e_{\text{dl}}\cos\bar M$$
- **代码位置**：`StateConversionUtil.cpp:3681-3907`

- **深度讲解**：这是 Brouwer 1963 短周期理论的直接移植。结构（`3787-3898`）：① 无量纲化 $\bar a/a_e$（`3700`）并把角度转弧度（`3702-3705`）；② 逆行镜像（`pseudostate`，$i>175°$ 时 $i\to180°-i,\ \Omega\to-\Omega$，`3764-3769`，输出时再镜像回来 `3900-3904`）；③ $\nu$ 由 `MeanToTrueAnomaly(...,1e-8)`（`3794`），$r=\bar p/(1+\bar e\cos\nu)$（`3799`）；④ 逐项实现短周期修正（`3802-3826`），其中 `aop1` 与 `ma1` 的表达式分别以 $1/\bar e$ 为系数量级，**$\bar e$ 很小时数值发散**——因此入口校验 `radPer>3000km`、`0<ECC<0.99`（`3717-3761`），RadPer<6378km 时仅警告（`3728-3738`）；⑤ 用 $e\cos M/e\sin M$ 的 atan2 合成 $\Delta e$ 与长周期 MA（`3832-3845`），用半角变量 $\sin(\tfrac i2)\sin/\cos$ 合成 $\Delta i,\Delta\Omega$（`3847-3861`，避免 $i=0$ 处 $\Omega$ 奇点）；⑥ 输出 `[a·a_e, e, i°, Ω°, ω°, M°]`（`3892-3898`）——**近点角固定为 MA**（调用方 `BrouwerMeanShortToCartesian` 以 `MA` 类型调用 `KeplerianToCartesian`，`3924-3925`）。
  - 关键守卫（`3686-3761`）：`|μ−μ_Earth|>1` 抛"仅适用于地球"；`eccp<0` 时翻转 $\bar e$ 并把 $M\to M-\pi/2,\ \omega\to\omega+\pi/2$（`3739-3751`，负偏心率 = 拱线互换）。

### CartesianToBrouwerMeanShort —— 笛卡尔 → 短周期平均根数（不动点迭代）

- **公式**（等价于在"赤道型"中间空间做不动点迭代）：
  $$\mathbf q=(a,\ e\sin(\omega+\Omega),\ e\cos(\omega+\Omega),\ \sin\tfrac i2\sin\Omega,\ \sin\tfrac i2\cos\Omega,\ \Omega+\omega+M)$$
  $$\mathbf q^{(k+1)}=\mathbf q^{(k)}+(\mathbf q_\text{osc}-\mathbf q^{(k)}_\text{osc}),\qquad \text{收敛判据：}\ \frac{\|\mathbf r(\mathbf q^{(k+1)})-\mathbf r\|}{\|\mathbf r\|}<10^{-8}$$
- **代码位置**：`StateConversionUtil.cpp:3408-3667`

- **深度讲解**：把吻切根数转赤道型 $\mathbf q$（`3512-3517`），用 `BrouwerMeanShortToOsculatingElements` 求其"吻切化" $\mathbf q^{(k)}_\text{osc}$，差值回代（`3533`），直到**笛卡尔状态**的相对误差 < 1e-8（`3571-3577`）；最大 75 次迭代（`3424`），不收敛时记录一次性警告并中断（`3601-3613`）。入口校验与 3.8.1 相同（仅地球、$i<180°$、$0<e<0.99$、RadPer>3000km，`3413-3468`），$i>175°$ 时先镜像（`3484-3491`）。输出前做负 $e$ 修复（`3637-3642`）与 $[0,360°)$ 归一（`3650-3664`）。

### BrouwerMeanLongToOsculatingElements —— 长周期项平均根数 → 吻切根数

- **公式**：在 3.8.1 基础上增加 J₃、J₄、J₅ 与长周期项（$k_2=\tfrac12 J_2$、$k_3=-J_3$、$k_4=-\tfrac38 J_4$、$k_5=-J_5$，`4308-4311`）：
  $$\gamma_m=k_m/\bar a^{m}\ (m=2..5),\qquad \gamma_{mp}=\gamma_m/\eta^{\,2m}$$
  临界倾角判据 $\left(1-5\theta^2\right)^{-2}\cdot 25\theta^4\theta\,\gamma_{2p}\bar e^2\ge 10^{-3}$ 时**截断全部长周期项**（`4424-4438`，63°/117° 临界倾角警告）；否则按 `a1..a8, b1..b12` 中间量（`4353-4397`）计算 $\ell+g+h$、$\Delta e$、$\Delta i$、$\sin\Delta H$（`4441-4450`）。
- **代码位置**：`StateConversionUtil.cpp:4208-4557`

- **深度讲解**：入口 `μ`、RadPer、$e<0.99$、$i<180°$ 校验同短周期版（`4213-4289`），另加临界倾角区间警告（58.80°–65.78° / 114.22°–121.2°，`4005-4016` 在调用方 `CartesianToBrouwerMeanLong`）。`tadp = MeanToTrueAnomaly(meanAnom, eccdp, 1e-12)`（`4342`，GMT-4446 修复放宽容差）。$a$ 的公式（`4402`）含 $\eta^{-6}$ 项与 $1/(1+\eta)$ 项——$\eta\to0$（$e\to1$）发散，靠 $e<0.99$ 守卫。最终 `inc=2·asin(√(sin²ΔH+(Δi·cos(i/2)/2+sin(i/2))²))`（`4474-4480`），$e=√(\Delta e_{dl}^2+(e+\Delta e)^2)$（`4472`）；$M,\Omega,\omega$ 由 `atan2` 与 $\ell+g+h$ 差分解出（`4507-4523`），全部归一到 $[0,2\pi)$。近点角固定 MA（`BrouwerMeanLongToCartesian` `4574-4575`）。

### CartesianToBrouwerMeanLong —— 笛卡尔 → 长周期平均根数

- **公式**：与 3.8.2 同构的不动点迭代，但 $\mathbf q^{(k)}_\text{osc}$ 由 `BrouwerMeanLongToOsculatingElements` 计算。
- **代码位置**：`StateConversionUtil.cpp:3939-4195`

- **深度讲解**：迭代骨架（`4084-4155`）与短周期版逐行对应（赤道型中间量 `4053-4074`、相对误差判据 `4112-4118`、不收敛警告 `4137-4147`、75 次上限 `3955`）；校验包括临界倾角警告（`4005-4016`）与 $i>175°$ 镜像（`4022-4029`）。输出 `blmean` 的负 $e$ 修复（`4157-4170` 附近逻辑与短周期版一致）与 $[0,360°)$ 归一（`4179-4193`）。

---

## 3.9 状态转换偏导（Jacobian）

### StateConvJacobian / JacobianOfCartesian / JacobianWrtCartesian —— 通用雅可比框架

- **公式**：
  $$J=\frac{\partial Y}{\partial X}:\quad \begin{cases}J=I,&X=Y\\ J=\left.\frac{\partial Y}{\partial \mathbf c}\right|_{\mathbf c}\cdot\left.\frac{\partial \mathbf c}{\partial X}\right|_{\mathbf c},&\text{经笛卡尔中转}\end{cases}$$
- **代码位置**：`StateConversionUtil.cpp:5805-5845`；`:5868-5893`；`:5916-5941`

- **深度讲解**：`StateConvJacobian` 把输入状态先统一转到笛卡尔（`5822-5826`），若分子分母都非笛卡尔则用**逐元素乘法**（`ElementWiseMultiply`）合成两个子雅可比（`5836-5841`）——这是链式法则的矩阵实现；`JacobianOfCartesian`（输出=笛卡尔）与 `JacobianWrtCartesian`（输入=笛卡尔）只认 `Keplerian` 与 `SphericalAZFPA` 两种表示（`5887-5890, 5935-5938`），其余类型返回单位阵。

### CartesianToKeplerianDerivativeConversion / …WithKeplInput —— 解析 $d\mathbf X/d\mathbf K$

- **公式**（GTDS MathSpec 3-176~3-204；$\mathbf r_p$ 为近焦点系位置，$P$ 为欧拉 3-1-3 旋转阵）：
  $$\mathbf r_p=\begin{cases}a(\cos E-e,\ \sin E\sqrt{1-e^2},\ 0),&\text{椭圆}\\ a(\cosh E-e,\ -\sinh E\sqrt{e^2-1},\ 0),&\text{双曲线}\end{cases},\qquad \dot{\mathbf r}_p=\begin{cases}\frac{\sqrt{\mu/a}}{1-e\cos E}(-\sin E,\ \cos E\sqrt{1-e^2},\ 0)\\ \frac{\sqrt{-(\mu/a)}}{e\cosh E-1}(\sinh E,\ -\cosh E\sqrt{e^2-1},\ 0)\end{cases}$$
  $$P=\begin{pmatrix}\cos\Omega\cos\omega-\sin\Omega\cos i\sin\omega&-\cos\Omega\sin\omega-\sin\Omega\cos i\cos\omega&\sin\Omega\sin i\\ \sin\Omega\cos\omega+\cos\Omega\cos i\sin\omega&-\sin\Omega\sin\omega+\cos\Omega\cos i\cos\omega&-\cos\Omega\sin i\\ \sin i\sin\omega&\sin i\cos\omega&\cos i\end{pmatrix}$$
  $$n=\frac{1}{a}\sqrt{\frac{\mu}{a}},\qquad \frac{\partial\mathbf r}{\partial(a,e,M)}=P\,c_1,\qquad \frac{\partial\dot{\mathbf r}}{\partial(a,e,M)}=P\,c_2$$
- **代码位置**：`StateConversionUtil.cpp:5960-5998`；`:6018-6209`

- **深度讲解**：主函数按 $e$ 分派（`5981-5993`）：$0\le e<1$ 走解析解，$e\ge1$ 走有限差分（3.9.3）。解析版：$E$ 由 MA 经 `CalculateEccentricAnomaly`（`6038`）或由 TA 经 `TrueToEccentricAnomaly`（`6040`）求得；$\mathbf r_p,\dot{\mathbf r}_p$ 按椭圆/双曲线分支（`6048-6073`）；$c_1,c_2$ 是 $\mathbf r_p$ 对 $(a,e,M)$ 或 $(a,e,\nu)$ 的偏导（MA 版 `6102-6107`、TA 版 `6111-6118`；速度侧 `6128-6142`），角分量 $\Omega,\omega,i$ 的偏导由 $P$ 的解析导数 $\partial P/\partial\Omega,\ \partial P/\partial\omega,\ \partial P/\partial i$ 给出（`6148-6186`）；最终 6×6 装配（`6188-6200`）并把角分量列乘 `RAD_PER_DEG`（$dX/dK$ 中角度以度为分母，`6204-6206`）。注释多处标注 GTDS MathSpec 对应公式号，并指出 MathSpec 3-202/3-204 个别元素**有误**、代码已修正（`6150-6153, 6178-6184`）。

### CartesianToKeplerianDerivativeConversion_FiniteDiff / …WithKeplInput_FiniteDiff —— 差分版

- **公式**（前向差分，扰动 $\varepsilon$）：
  $$\left[\frac{dK}{dX}\right]_{ij}=\frac{K_i(X+\varepsilon e_j)-K_i(X)}{\varepsilon X_j},\ \varepsilon=10^{-6};\qquad \frac{dX}{dK}=\left(\frac{dK}{dX}\right)^{-1}$$
- **代码位置**：`StateConversionUtil.cpp:6225-6278`；`:6299-6339`

- **深度讲解**：`…_FiniteDiff` 扰动**笛卡尔**分量（`X1[col] *= 1.000001`，`6257`）得 $dK/dX$ 再求逆（`6272`）；`…WithKeplInput_FiniteDiff` 扰动**开普勒**分量（`ecc` 用 1.000001，其余用 1.00000001，`6321-6324`）直接得 $dX/dK$（`6332-6334`）。$e\ge1$（双曲线/抛物线）时主函数走后者（`5986-5993`）——解析公式的 $\sqrt{1-e^2}$ 在 $e\ge1$ 无实义，差分是双曲线情形的标准退路。

### KeplerianToCartesianDerivativeConversion —— $d\mathbf K/d\mathbf X$（对笛卡尔解析求导）

- **公式**：由 $\mathbf e$、$\mathbf n$、$\mathbf h$、$a$、$\xi$ 的链式法则逐项展开，例如：
  $$\frac{\partial a}{\partial \mathbf r}=2\frac{(a/r)^2}{r}\mathbf r,\qquad \frac{\partial a}{\partial \mathbf v}=\frac{2a^2}{\mu}\mathbf v$$
  $$\frac{\partial e}{\partial \mathbf r}=\frac{1}{e\mu}\mathbf e^T\left[\left(v^2-\frac{\mu}{r}\right)I+\frac{\mu}{r^3}\mathbf r\mathbf r^T-\mathbf v\mathbf v^T\right],\qquad \frac{\partial \nu}{\partial \mathbf r}=-\frac{1}{\sqrt{1-(\hat{\mathbf e}\cdot\hat{\mathbf r})^2}}\left(\frac{1}{r}\mathbf r^T\frac{\partial\hat{\mathbf e}}{\partial\mathbf r}+\frac{1}{e}\mathbf e^T\frac{\partial\hat{\mathbf r}}{\partial\mathbf r}\right)$$
- **代码位置**：`StateConversionUtil.cpp:6356-6663`

- **深度讲解**：先由状态求 $r,v,\mathbf h,\mathbf n,\mathbf e,E,\xi$（`6359-6415`），近抛物线双守卫（`6395-6408`）；再按中间量偏导（外积矩阵 $\mathbf r\mathbf r^T$ 等，`6420-6474`）逐元素合成六要素梯度（`6479-6660`）：SMA（`6479-6480`）、ECC（`6491-6493`）、INC（`6511-6514`，含 $\sqrt{1-(h_z/h)^2}$ 分母）、RAAN（`6529-6533`）、AOP（`6554-6568`）、TA（`6588-6603`），象限修正标志同步作用于梯度符号（$n_y<0$、$e_z<0$、$\mathbf r\cdot\mathbf v<0$，`6536-6540, 6570-6574, 6605-6609`）——**梯度在角度跨越象限边界时保持与主值一致的符号约定**。

### CartesianToSphericalAzFPADerivativeConversion / SphericalAzFPAToCartesianDerivativeConversion —— 球坐标雅可比

- **公式**：对 3.4.1 的正/逆变换逐分量求导，例如逆变换侧：
  $$\frac{\partial r}{\partial \mathbf r}=\frac{\mathbf r}{r},\qquad \frac{\partial \lambda}{\partial \mathbf r}=\left(-\frac{r_y}{r_{xy}^2},\ \frac{r_x}{r_{xy}^2},\ 0\right),\qquad \frac{\partial\delta}{\partial \mathbf r}=\frac{(-r_x r_z,\ -r_y r_z,\ r_{xy}^2)}{r^2\sqrt{r_{xy}^2}}$$
  $$\frac{\partial\psi}{\partial \mathbf r}=\frac{1}{r\sqrt{v^2-\dot r^2}}\left(\frac{\dot r}{r}\mathbf r-\mathbf v\right)$$
- **代码位置**：`StateConversionUtil.cpp:6680-6801`；`:6818-6911`

- **深度讲解**：正变换侧（$dX/dS$，`6680-6801`）先转球坐标再对六个球分量解析求导（位置 `6708-6711`、速度 `6719-6747`，`dvvdRA` 等按 3.4.1 逆变换公式微分），6×6 装配（`6751-6798`）。逆变换侧（$dS/dX$，`6818-6911`）直接对笛卡尔求导：`dRMAGdrv = r/r`（`6832`）、`dRAdrv`（`6833`）、`dDECdrv`（`6834-6835`）、`dAZIdrv`（`6838-6846`）、`dFPAdrv`（`6847-6848`，注释指出 GTDS 原式 $RMAG^2$ 有误已改 $RMAG$）、速度侧（`6852-6857`）。这两个矩阵与 3.9.4 一起支撑 `StateConvJacobian` 的全部表示组合。

---

## 3.10 参数层：轨道要素参数类与 CalculateKeplerianData

### OrbitData（src/base/parameter）—— 参数求值的数据中枢

- **公式**：本身无新公式，是"参数 → 状态 → `StateConversionUtil`"的装配层；唯一例外是 `GetEquinDot`（见 3.10.5）。
- **代码位置**：`src/base/parameter/OrbitData.cpp:722-743`（`GetKepState`）、`:832-843`（`GetModKepState`）、`:894-905`（`GetEquinState`）、`:934-1041`（`GetEquinDot`）、`:1168-1229`（`GetKepReal`）、`:1279-1295`（`GetOtherKepReal`）、`:1398-1422`（`GetAngularReal`）

- **深度讲解**：
  - `GetKepState`（`734`）：`StateConversionUtil::CartesianToKeplerian(mGravConst, state)` 一行；`GetKepReal`（`1189-1228`）按 `KEP_SMA/ECC/INC/TA/EA/MA/HA/RAAN/RADN/AOP`（枚举见 `src/base/parameter/OrbitData.hpp:219-220`）分派到 3.2.5 的单要素函数，**`KEP_RADN` = RAAN+180°** 经 `AngleUtil::PutAngleInDegRange` 归一（`1218-1221`）。
  - `GetOtherKepReal`（`1293`）把 `MM/VelApoapsis/VelPeriapsis/OrbitPeriod/C3Energy/Energy`（`OrbitData.hpp:203`）交给 `GmatCalcUtil::CalculateKeplerianData`；`GetAngularReal`（`1420`）把 `SemilatusRectum/HMag/HX/HY/HZ/BetaAngle/HyperbolicRLA/HyperbolicDLA`（`OrbitData.hpp:206`）交给 `GmatCalcUtil::CalculateAngularData`。
  - 其余 `GetModKepReal`（RadApo/RadPer，`1259-1262`）、`GetEquinReal`/`GetModEquinReal`/`GetAltEquinReal`/`GetDelaReal`/`GetPlanetodeticReal`/`GetIncAsymReal`/`GetOutAsymReal`/`GetBLshortReal`/`GetBLlongReal`（`1463-1926` 区间）均为"取对应 `GetXxxState` 的第 i 分量"的薄分派。

### KeplerianParameters 家族 —— SMA/ECC/TA 等参数类 Evaluate

- **公式**：全部委托 `OrbitData::GetKepReal`（单值）或 `GetKepState`（六元组）。
- **代码位置**：`src/base/parameter/KeplerianParameters.cpp:121-129`（`KepSMA::Evaluate`）、`:234-242`（`KepEcc`）、`:349-357`（`KepInc`）、`:465-473`（`KepAOP`）、`:581-589`（`KepRAAN`）、`:694-702`（`KepRADN`）、`:809-817`（`KepTA`）、`:924-932`（`KepMA`）、`:1039-1047`（`KepEA`）、`:1154-1162`（`KepHA`）、`:1266-1274`（`KepMM`）、`:1381-1386`（`KepElem`）、`:1493-1504`（`ModKepRadApo`）、`:1611-1622`（`ModKepRadPer`）

- **深度讲解**：每个类的 `Evaluate` 都是同一模式（以 `KepSMA` 为例，`121-129`）：

  ```cpp
  bool KepSMA::Evaluate()
  {
     mRealValue = OrbitData::GetKepReal(KEP_SMA);   // 最终落到 StateConversionUtil::CartesianToSMA
     if (mRealValue == GmatOrbitConstants::ORBIT_REAL_UNDEFINED)
        return false;                                // 哨兵值 = 求值失败
     else
        return true;
  }
  ```

  `KepElem::Evaluate` 略有不同：`mRvec6Value = OrbitData::GetKepState()` 并 `IsValid` 校验（`1381-1386`）。**公式来源链**：`Parameter::Evaluate → OrbitReal 子类 → OrbitData::GetKepReal → StateConversionUtil::CartesianToXXX`，故本章 3.2/3.3 的全部公式即参数类的公式。`KepMA` 构造器（`855-863`）标记 `mIsAngleParam=true, mCycleType=ZERO_360`，`KepInc`（`280-288`）为 `ZERO_180`——角度参数在 GUI/脚本层的周期折叠约定。

### OrbitalParameters 家族 + GmatCalcUtil::CalculateKeplerianData —— 派生轨道量

- **公式**（`GmatCalcUtil::CalculateKeplerianData`，`src/gmatutil/util/CalculationUtilities.cpp:269-343`）：
  $$n=\begin{cases}\sqrt{\mu/a^3},&e<1\\ \sqrt{-\mu/a^3},&e>1\\ 2\sqrt{\mu}\ (\text{占位}),&e\approx1\end{cases}\qquad v_a=\sqrt{\frac{\mu}{a}\frac{1-e}{1+e}},\qquad v_p=\sqrt{\frac{\mu}{a}\frac{1+e}{1-e}}$$
  $$T=2\pi\sqrt{\frac{a^3}{\mu}}\ (a>0),\qquad r_a=a(1+e),\qquad r_p=a(1-e),\qquad C_3=-\frac{\mu}{a},\qquad \xi=-\frac{\mu}{2a}$$
- **代码位置**：`src/gmatutil/util/CalculationUtilities.cpp:269-343`；参数类 `src/base/parameter/OrbitalParameters.cpp:126-137`（`VelApoapsis::Evaluate`）、`:247`、`:368`、`:503`、`:643`（`OrbitPeriod`）、`:762`（`C3Energy`）、`:879`（`Energy`）

- **深度讲解**：`CalculateKeplerianData` 先经 `CartesianToSMA`/`CartesianToECC` 取 $a,e$（`275-276`），再按条目返回；抛物线（$|1-e|\le\text{KEP\_ECC\_TOL}$）与奇异圆锥（$a(1-e)<10^{-3}$）抛异常（`278-290`）。`MeanMotion` 双曲线分支开根取正（`296-297`，$n$ 为虚频率），抛物线分支返回 `2√μ` 并注释"应为 0"（`299`）——**占位值，未按物理修正**。`OrbitPeriod` 对 $a<0$（双曲线）返回 0（`314-317`）。`OrbitalParameters` 各 `Evaluate` 即 `OrbitData::GetOtherKepReal(VEL_APOAPSIS/...)` 的包装（如 `VelApoapsis::Evaluate` `126-137`）。

### GmatCalcUtil::CalculateAngularData + ValidateValue —— 角量参数与输入校验

- **公式**（`CalculationUtilities.cpp:165-251`）：
  $$p=\frac{h^2}{\mu},\qquad \beta=\sin^{-1}(\hat{\mathbf h}\cdot\hat{\mathbf s}_\odot),\qquad \mathbf s=\frac{1}{1+C_3 h^2/\mu^2}\left(\frac{\sqrt{C_3}}{\mu}\mathbf h\times\mathbf e-\mathbf e\right),\quad \alpha_{rla}=\operatorname{atan2}(s_y,s_x),\ \delta_{dla}=\sin^{-1}(s_z)$$
- **代码位置**：`src/gmatutil/util/CalculationUtilities.cpp:165-251`；`ValidateValue` `src/gmatutil/util/StateConversionUtil.cpp:7012-7395`

- **深度讲解**：`SemilatusRectum = h²/μ`（`191`，`hMag<KEP_TOL` 时返回 0）；`BetaAngle` 是轨道面法线与日向夹角的反正弦（`211-213`）；`RLA/DLA`（双曲线渐近线赤经/赤纬）复用 3.7.1 的 $\hat{\mathbf s}$ 构造（`226-243`），$e<1+\text{KEP\_ECC\_TOL}$ 时返回 `QUIET_NAN`（`228-229`）。
  `ValidateValue`（`7012-7395`）是脚本输入的门卫，**每条规则即一个取值范围公式**：`RADAPO/RADPER` 要求 $|v|\ge10^{-3}$ km（`7046-7081`）；`ECC` 要求 $|e-1|\ge\text{PARABOLIC\_TOL}$，与 SMA 耦合时（$a>0\Rightarrow 0<e<1$，$a<0\Rightarrow e>1$，`7082-7112`）；Brouwer 系要求 $0\le e<0.99$、$a\ge1000/(1-e)$（`7113-7170`）；`INC/FPA\in[0,180]°$`（`7171-7185`）；`RMAG/VMAG\ge10^{-10}$（`7186-7196`）；`DEC\in[-90,90]°$（`7197-7211`）；赤道型元素 $|h|,|k|<1$ 且 $\sqrt{h^2+k^2}<1-\text{EQUINOCTIAL\_TOL}$（`7212-7259`）；`MLONG\in[-360,360]°$、`TLONG/Delaunayl/g/h\in[0,360]°$（`7260-7288`）；`SEMILATUSRECTUM\ge10^{-7}$（`7289-7300`）；Delaunay 耦合 $G/L\le1$、$|H|\le|G|$（`7316-7382`）。

### OrbitData::GetEquinDot —— 赤道型元素变率（Read 等 2016 公式）

- **公式**（基于改进赤道型，摄动 $\mathbf P$ 为去掉中心项 $\mu\mathbf r/r^3$ 后的加速度；$C,S,N$ 为其在共速度/径向/法向的分量）：
  $$p=a(1-e^2),\quad s^2=1+h^2+k^2,\quad w=1+f\cos L+g\sin L,\quad \sqrt{p/\mu}=\text{rootPoverMu}$$
  $$\dot a=\frac{2}{n^2a}(\mathbf v\cdot\mathbf P),\qquad \dot f=\sqrt{\frac{p}{\mu}}\left(-S\cos L+\frac{(w+1)\sin L+g}{w}C+\frac{f(h\sin L-k\cos L)}{w}N\right)$$
  $$\dot g=\sqrt{\frac{p}{\mu}}\left(S\sin L+\frac{(w+1)\cos L+f}{w}C-\frac{g(h\sin L-k\cos L)}{w}N\right)$$
  $$\dot h=\sqrt{\frac{p}{\mu}}\frac{s^2}{2w}N\sin L,\qquad \dot k=\sqrt{\frac{p}{\mu}}\frac{s^2}{2w}N\cos L,\qquad \dot L=\sqrt{\mu p}\,\frac{w^2}{p^2}+\sqrt{\frac{p}{\mu}}\frac{h\sin L-k\cos L}{w}N$$
- **代码位置**：`src/base/parameter/OrbitData.cpp:934-1041`

- **深度讲解**：`ode->GetDerivativesForSpacecraft` 取总加速度，加上 $\mu\mathbf r/r^3$ 还原成摄动 $\mathbf P$（`951-958`）；$\hat{\mathbf r},\hat{\mathbf n},\hat{\mathbf c}$ 基由位置/速度构造（`998-1009`），$C=\mathbf P\cdot\hat{\mathbf c}, S=\mathbf P\cdot\hat{\mathbf r}, N=\mathbf P\cdot\hat{\mathbf n}$（`1011-1013`）；$\dot a$ 用 $\dot a=2(\mathbf v\cdot\mathbf P)/(n^2a)$（`1022-1024`）；$\dot L$ 的第一项 $\sqrt{\mu p}\,w^2/p^2$ 是开普勒无摄项（即 $n(1+e\cos\nu)^2/(1-e^2)^{3/2}$ 的等价形式），第二项为摄动贡献（`1035-1037`）。文件头注释（`914-925`）说明该组公式取自 Read et al. CMES 111(1):65-81, 2016，并指出 GTDS 5.7.2 的 $h,k,p,q,L$ 变率与数值差分**不一致**故弃用——这是 GMAT 中罕见的"以论文公式取代规范公式"的案例。`EQ_TLONG_DOT` 参数报告的是**真黄经变率**而非平黄经（`OrbitData.hpp:237` 注释）。

---

## 3.11 Spacecraft 状态表示参数化

### GetStateInRepresentation / SetStateFromRepresentation —— 状态表示入口

- **公式**：`rep == "Cartesian"` 时恒等；否则
  $$\mathbf s_\text{rep}=\text{StateConversionUtil::Convert}(\mathbf s_\text{cs},\ \text{"Cartesian"},\ rep,\ \mu_\text{origin}, f_\text{origin}, R_{eq,\text{origin}}, \text{anomalyType})$$
- **代码位置**：`src/base/spacecraft/Spacecraft.cpp:10863-10975`；`:10998-11080`

- **深度讲解**：`GetStateInRepresentation` 先把内部坐标系（MJ2000Eq）状态经 `coordConverter` 转到参数坐标系（`10877-10905`），再按表示调用 `StateConversionUtil::Convert`（`10939-10940`）——**$\mu$/扁率/赤道半径来自原点天体**（`originMu/originFlattening/originEqRadius`，与 CH06 §2.3.2 描述一致）；非惯性系/非天体原点时对开普勒类表示给出警告（`10942-10962`）。`SetStateFromRepresentation` 反向：先 `Convert(st, rep, "Cartesian", ...)`（`11036-11037`），Planetodetic 要求 BodyFixed 坐标系（`11013-11023`），再转内部坐标系写入 `state`（`11061-11072`）。**注意**：`src/base/spacecraft/SpacecraftOrbitState.*` 在本仓库不存在，此二函数 + `GetElement` 承担其"状态参数化"职责。

### Spacecraft::GetElement —— 单要素读取（含近点角链式换算）

- **公式**（TA/EA/MA/HA 分支）：
  $$\nu_0=\text{ConvertToTrueAnomaly}(\text{anomalyType},\ \text{kep}[5],\ \text{kep}[1])\cdot\text{RAD\_PER\_DEG};\qquad \text{value}=\text{ConvertFromTrueAnomaly}(label,\ \nu_0,\ \text{kep}[1])\cdot\text{DEG\_PER\_RAD}$$
- **代码位置**：`src/base/spacecraft/Spacecraft.cpp:11094-11134`

- **深度讲解**：`GetElement` 先取目标表示的六元组（`11108`）；对近点角类标签走"双跳"换算（`11116-11122`）：**先把航天器当前 `anomalyType` 存的近点角换成 TA，再从 TA 换成请求的近点角**——这是 `ConvertToTrueAnomaly`（3.3.7）与 `ConvertFromTrueAnomaly` 在航天器层的实际装配，两条链共用 TA 作为枢纽的原因是 TA 是 `ComputeKeplToCart` 唯一直接消费的近点角（3.2.2 的 `7875-7885`）。其余标签按 `ELEMENT1..6_ID` 直取（`11125-11130`）。

---

## 3.12 平动点（LibrationPoint）

### LibrationPoint::GetMJ2000State —— L1–L5 位置/速度（牛顿迭代解五次方程）

- **公式**（归一化质量 $\mu^*=m_2/(m_1+m_2)$，$\gamma$ 为以次天体方向为 +x 的归一化偏移）：
  $$\text{L1：}\ F(\gamma)=\gamma^5-(3-\mu^*)\gamma^4+(3-2\mu^*)\gamma^3-\mu^*\gamma^2+2\mu^*\gamma-\mu^*=0$$
  $$\text{L2：}\ F(\gamma)=\gamma^5+(3-\mu^*)\gamma^4+(3-2\mu^*)\gamma^3-\mu^*\gamma^2-2\mu^*\gamma-\mu^*=0$$
  $$\text{L3：}\ F(\gamma)=\gamma^5+(2+\mu^*)\gamma^4+(1+2\mu^*)\gamma^3-(1-\mu^*)\gamma^2-2(1-\mu^*)\gamma-(1-\mu^*)=0$$
  $$\gamma_{k+1}=\gamma_k-\frac{F(\gamma_k)}{F'(\gamma_k)},\qquad \gamma_0=\begin{cases}1,&\text{L3}\\ \left(\dfrac{\mu^*}{3(1-\mu^*)}\right)^{1/3},&\text{L1/L2}\end{cases}$$
  $$\text{L4/L5（解析）：}\ (x,y)=\left(\tfrac12,\ \pm\tfrac{\sqrt3}{2}\right)$$
- **代码位置**：`src/base/solarsys/LibrationPoint.cpp:174-380`（A1Mjd 版）、`:383-591`（GmatTime 版，公式逐行重复）

- **深度讲解**：核心循环（`243-286`）：

  ```cpp
  while (diff > CONVERGENCE_TOLERANCE) {          // 1e-8
     if (counter > MAX_ITERATIONS) throw ...;      // 2000 次上限
     gamma2 = gamma*gamma; gamma3 = gamma2*gamma;  // 预计算幂
     gamma4 = gamma3*gamma; gamma5 = gamma4*gamma;
     if (whichPoint == "L1") {
        F    = gamma5 - (3.0-muStar)*gamma4 + (3.0-2.0*muStar)*gamma3
               - muStar*gamma2 + 2.0*muStar*gamma - muStar;   // L1 五次方程
        Fdot = 5.0*gamma4 - 4.0*(3.0-muStar)*gamma3
               + 3.0*(3.0-2.0*muStar)*gamma2 - 2.0*muStar*gamma + 2.0*muStar;
     } /* L2 / L3 同理（264-281） */
     gammaPrev = gamma;
     gamma     = gammaPrev - (F/Fdot);             // Newton 步
     diff      = Abs(gamma - gammaPrev);           // 收敛判据
  }
  ```
  - **数学推导要点**：三个共线点的 $x$ 坐标代入圆型限制性三体问题平衡方程 $x-\frac{1-\mu^*}{(x+\mu^*)^2}+\frac{\mu^*}{(x-1+\mu^*)^2}=0$（以 $\gamma$ 代换 $x=1-\gamma$、$x=1+\gamma$、$x=-\gamma$）即得三个五次式，其导数是 Newton 迭代的 $F'$。L4/L5 是等边三角形解，解析给出（`305-314`）。
  - **旋转系到惯性系**（`330-371`）：$r_i=r_{12}\cdot(x,y,0)$、$v_i=(\mathbf v_{12}\cdot\mathbf r_{12}/r_{12})(x,y,0)$（`330-332`，**共线点速度沿连线方向**，无切向分量）；基矢 $\hat{\mathbf x}=\mathbf r_{12}/r_{12}$、$\hat{\mathbf z}=(\mathbf r\times\mathbf v)/|\cdot|$、$\hat{\mathbf y}=\hat{\mathbf z}\times\hat{\mathbf x}$（`334-336`），导数 $\dot{\hat{\mathbf x}}=\mathbf v/r-(\hat{\mathbf x}\cdot\mathbf v)\hat{\mathbf x}/r$、$\dot{\hat{\mathbf z}}=(\mathbf r\times\mathbf a)/|\mathbf r\times\mathbf v|-\hat{\mathbf z}((\mathbf r\times\mathbf a)\cdot\hat{\mathbf z})/|\mathbf r\times\mathbf v|$（`337-341`）——$\hat{\mathbf z}$ 的导数用到**相对加速度** $\mathbf a$（`199-200`，由两体 `GetMJ2000Acceleration` 差分得到）；位置 $\mathbf r_{Li}=R\mathbf r_i$、速度 $\mathbf v_{Li}=\dot R\mathbf r_i+R\mathbf v_i$（`365-366`）；最后平移回 J2000 原点 $\mathbf r_{Li}+\mathbf r_\text{primary}$（`371`）。
  - **奇点处理**：`mass ≤ ZERO_MASS_TOL(1e-15)` 抛异常（`213-220`）；`r_{12} ≤ ZERO_MAG_TOL(1e-12)`（两天体重合）抛异常（`325-328`）；$\gamma$ 迭代 2000 次不收敛抛异常（`247-249`）。$F'/F$ 无显式守卫，但 $\gamma$ 初值（L1/L2 取 $\sqrt[3]{\mu^*/3(1-\mu^*)}$，L3 取 1）保证快速收敛。
  - 类参数 `PRIMARY_BODY_NAME/SECONDARY_BODY_NAME/WHICH_POINT` 与 `SetStringParameter` 的 L1–L5 白名单见 `LibrationPoint.cpp:817-859`；体系结构（`CalculatedPoint` 继承、`bodyList`）见[第6章 §2.2.4](../CH06-dynamics.md)。

---

## 3.13 公式索引表

| 公式 | 文件:行 | 所属类/函数 |
| --- | --- | --- |
| $h=\mathbf r\times\mathbf v,\ n=\hat{\mathbf z}\times\mathbf h,\ \mathbf e=((v^2-\mu/r)\mathbf r-(\mathbf r\cdot\mathbf v)\mathbf v)/\mu,\ a=-\mu/(2\zeta)$ | `src/gmatutil/util/StateConversionUtil.cpp:7648-7722` | StateConversionUtil::ComputeCartToKepl |
| 四情形 $\Omega,\omega,\nu$（象限修正） | `StateConversionUtil.cpp:7759-7840` | ComputeCartToKepl |
| $p=a(1-e^2),\ r=p/(1+e\cos\nu)$；$\mathbf r,\mathbf v$ 3-1-3 旋转展开 | `StateConversionUtil.cpp:7895-7976` | ComputeKeplToCart |
| 双曲线 TA 越界校验 $\arccos(-1/e)$ | `StateConversionUtil.cpp:7922-7931` | ComputeKeplToCart |
| $e<0$ 取反；$(a>0\wedge e>1)$ 或 $(a<0\wedge e<1)$ 时 $a$ 取反 | `StateConversionUtil.cpp:1496-1529` | KeplerianToCartesian |
| 近点半径 $<1$ m / 近抛物线守卫 | `StateConversionUtil.cpp:1547-1570` | KeplerianToCartesian |
| $\text{anomaly}=\text{ConvertFromTrueAnomaly}(type,\nu,e)$ | `StateConversionUtil.cpp:1310-1313` | CartesianToKeplerian |
| $a=-\mu/(2(v^2/2-\mu/r))$ | `StateConversionUtil.cpp:5369-5386` | CartesianToSMA |
| $e=\|\mathbf e\|$；$i=\cos^{-1}(h_z/h)$ | `StateConversionUtil.cpp:5425-5426, 5469-5477` | CartesianToECC / CartesianToINC |
| $\Omega,\omega$ 四情形公式 | `StateConversionUtil.cpp:5531-5572, 5625-5664` | CartesianToRAAN / CartesianToAOP |
| $\mathbf e=((v^2-\mu/r)\mathbf r-(\mathbf r\cdot\mathbf v)\mathbf v)/\mu$ | `StateConversionUtil.cpp:5704` | CartesianToEccVector |
| $\mathbf n=\hat{\mathbf z}\times\mathbf h$；$[ĥ,h,v²,p=h²/μ]$ | `StateConversionUtil.cpp:5728-5730, 5766-5771` | CartesianToDirOfLineOfNode / CartesianToAngularMomentum |
| $r_p=a(1-e),\ r_a=a(1+e)$ | `StateConversionUtil.cpp:1989-1990` | KeplerianToModKeplerian |
| $e=(1-r_p/r_a)/(1+r_p/r_a),\ a=r_p/(1-e)$ | `StateConversionUtil.cpp:2046-2050` | ModKeplerianToKeplerian |
| $\sin E=\sqrt{1-e^2}\sin\nu/(1+e\cos\nu)$，$E=\operatorname{atan2}$ | `StateConversionUtil.cpp:4777-4779` | TrueToEccentricAnomaly |
| $\sin\nu=\sqrt{1-e^2}\sin E/(1-e\cos E)$ | `StateConversionUtil.cpp:4925-4927` | EccentricToTrueAnomaly |
| $\tanh(H/2)=\tan(\nu/2)\sqrt{(e-1)/(e+1)}$ | `StateConversionUtil.cpp:4823-4824` | TrueToHyperbolicAnomaly |
| $\sin\nu=\sqrt{e^2-1}\sinh H/(1-e\cosh H)$ | `StateConversionUtil.cpp:4959-4961` | HyperbolicToTrueAnomaly |
| $M=E-e\sin E$；$M=e\sinh H-H$；近抛物线 $M=0$ | `StateConversionUtil.cpp:4717-4739` | TrueToMeanAnomaly |
| $E_{k+1}=E_k-(E_k-e\sin E_k-M)/(1-e\cos E_k)$，$E_0=M+e\sin M$ | `StateConversionUtil.cpp:8018-8046` | ComputeMeanToTrueAnomaly（椭圆） |
| $\nu=2\tan^{-1}(\sqrt{(1+e)/(1-e)}\tan(E/2))$；$E\approx\pi$ 时 $\nu=E$ | `StateConversionUtil.cpp:8065-8086` | ComputeMeanToTrueAnomaly（椭圆） |
| $H_{k+1}=H_k-(e\sinh H_k-H_k-M)/(e\cosh H_k-1)$，$H_0=0$ | `StateConversionUtil.cpp:8105-8129` | ComputeMeanToTrueAnomaly（双曲线） |
| $\nu=2\tan^{-1}(\sqrt{(e+1)/(e-1)}\tanh(H/2))$ | `StateConversionUtil.cpp:8138-8145` | ComputeMeanToTrueAnomaly（双曲线） |
| TA/MA/EA/HA 派发开关 | `StateConversionUtil.cpp:5012-5019, 5065-5072` | ConvertFromTrueAnomaly / ConvertToTrueAnomaly |
| $\nu=\cos^{-1}(\mathbf e\cdot\mathbf r/(er))$ 四情形 + $\operatorname{Mod}(,2\pi)$ | `StateConversionUtil.cpp:5131-5207` | CartesianToTA |
| $M=\text{TrueToMeanAnomaly}(\text{TA},\ e)$ 链 | `StateConversionUtil.cpp:5243-5245` | CartesianToMA |
| $E$ / $H$ 链 | `StateConversionUtil.cpp:5282-5284, 5320-5322` | CartesianToEA / CartesianToHA |
| Danby 修正 $D=1-e\cos(E-f/2)$，容差 1e-12 | `StateConversionUtil.cpp:6946-6953` | CalculateEccentricAnomalyEllipse |
| 双曲 Newton $E_0=M/2$ | `StateConversionUtil.cpp:6964-6969` | CalculateEccentricAnomalyHyperbola |
| 抛物线未实现（Barker 缺失） | `StateConversionUtil.cpp:6976-6989` | CalculateEccentricAnomalyParabola |
| $r,\lambda,\delta,\psi$ 球坐标正/逆变换 | `StateConversionUtil.cpp:1676-1726, 1754-1773` | CartesianToSphericalAZFPA / SphericalAZFPAToCartesian |
| $\lambda_V,\delta_V$ 速度球坐标 | `StateConversionUtil.cpp:1807-1828, 1859-1867` | CartesianToSphericalRADEC / SphericalRADECToCartesian |
| $\phi_{k+1}=\tan^{-1}((r_z+C_k e^2\sin\phi_k)/r_{xy})$，容差 1e-13 | `StateConversionUtil.cpp:2701-2715` | CartesianToPlanetodetic |
| $\phi_g$ 二阶级数反演 | `StateConversionUtil.cpp:2813-2826` | PlanetodeticToCartesian |
| $h,k,p,q,\lambda$ 赤道型元素构造 | `StateConversionUtil.cpp:2132-2162` | CartesianToEquinoctial |
| $F$ 的 Newton 迭代解 $\lambda$ | `StateConversionUtil.cpp:2206-2211` | EquinoctialToCartesian |
| $X_1,Y_1,\dot X_1,\dot Y_1$ 与 $Q$ 矩阵 | `StateConversionUtil.cpp:2252-2273` | EquinoctialToCartesian |
| $p=h^2/\mu,\ f,g,h,k,L$ 改进赤道型 | `StateConversionUtil.cpp:2343-2394` | CartesianToModEquinoctial |
| $r=p/(1+f\cos L+g\sin L)$；$\dot X_1,\dot Y_1$ | `StateConversionUtil.cpp:2443-2472` | ModEquinoctialToCartesian |
| $i=2\tan^{-1}\sqrt{p^2+q^2}$；$\tilde p=p\cos(i/2)$ | `StateConversionUtil.cpp:4605-4625` | EquinoctialToAltEquinoctial |
| $i=2\sin^{-1}\sqrt{\tilde p^2+\tilde q^2}$ | `StateConversionUtil.cpp:4659-4679` | AltEquinoctialToEquinoctial |
| $L=\sqrt{\mu a},G=L\sqrt{1-e^2},H=G\cos i,l=M$ | `StateConversionUtil.cpp:2599-2604` | KeplerianToDelaunay |
| $a=L^2/\mu,e=\sqrt{1-(G/L)^2},i=\cos^{-1}(H/G)$ | `StateConversionUtil.cpp:2647-2652` | DelaunayToKeplerian |
| $c_3,\ a=-μ/c_3,\ r_p$；$\hat{\mathbf s}$ 双分支 | `StateConversionUtil.cpp:2879-2933` | CartesianToIncomingAsymptote |
| $\hat{\mathbf e}$ 双分支与 $\nu_{\max}$ | `StateConversionUtil.cpp:3068-3077` | IncomingAsymptoteToCartesian |
| 出射 $\hat{\mathbf s}$ 符号翻转 | `StateConversionUtil.cpp:3198-3199, 3334-3341` | CartesianToOutgoingAsymptote / OutgoingAsymptoteToCartesian |
| 短周期 J₂ 修正（$\eta,\theta,\gamma_{2p}$） | `StateConversionUtil.cpp:3787-3831` | BrouwerMeanShortToOsculatingElements |
| $e\cos M/e\sin M$ 合成与半角 $i,\Omega$ 合成 | `StateConversionUtil.cpp:3832-3876` | BrouwerMeanShortToOsculatingElements |
| 赤道型不动点迭代 | `StateConversionUtil.cpp:3512-3533, 3571-3577` | CartesianToBrouwerMeanShort |
| J₃–J₅ 长周期项与临界倾角截断 | `StateConversionUtil.cpp:4308-4450` | BrouwerMeanLongToOsculatingElements |
| 长周期不动点迭代 | `StateConversionUtil.cpp:4053-4135` | CartesianToBrouwerMeanLong |
| 雅可比链式合成（ElementWiseMultiply） | `StateConversionUtil.cpp:5836-5841` | StateConvJacobian |
| $\mathbf r_p,\dot{\mathbf r}_p$ 椭圆/双曲线分支与 $P$ 矩阵 | `StateConversionUtil.cpp:6051-6085` | CartesianToKeplerianDerivativeConversionWithKeplInput |
| $c_1,c_2$ 与 $\partial P/\partial\Omega,\partial\omega,\partial i$ | `StateConversionUtil.cpp:6102-6186` | 同上 |
| 角度列 × RAD_PER_DEG 单位修正 | `StateConversionUtil.cpp:6204-6206` | 同上 |
| 差分 $dK/dX$ 后求逆 | `StateConversionUtil.cpp:6257-6272` | CartesianToKeplerianDerivativeConversion_FiniteDiff |
| 差分 $dX/dK$（ecc 用 1e-6 扰动） | `StateConversionUtil.cpp:6321-6334` | …WithKeplInput_FiniteDiff |
| $\partial a/\partial\mathbf r,\partial a/\partial\mathbf v$ 等六要素梯度 | `StateConversionUtil.cpp:6479-6609` | KeplerianToCartesianDerivativeConversion |
| 球坐标 $dX/dS$ 各列解析偏导 | `StateConversionUtil.cpp:6708-6797` | CartesianToSphericalAzFPADerivativeConversion |
| 球坐标 $dS/dX$ 各列解析偏导 | `StateConversionUtil.cpp:6832-6907` | SphericalAzFPAToCartesianDerivativeConversion |
| $\mathbf s_\text{rep}=\text{Convert}(\mathbf s_\text{cs},\text{"Cartesian"},rep,\mu,f,R_{eq})$ | `Spacecraft.cpp:10939-10940, 11036-11037` | Spacecraft::GetStateInRepresentation / SetStateFromRepresentation |
| 近点角双跳：$\nu_0=\text{ToTA}(\text{anomType})$, value=$\text{FromTA}(label,\nu_0)$ | `Spacecraft.cpp:11116-11122` | Spacecraft::GetElement |
| $n,v_a,v_p,T,r_a,r_p,C_3,\xi$ | `src/gmatutil/util/CalculationUtilities.cpp:292-337` | GmatCalcUtil::CalculateKeplerianData |
| $p=h^2/\mu,\beta=\sin^{-1}(\hat{\mathbf h}\cdot\hat{\mathbf s}_\odot)$、RLA/DLA | `CalculationUtilities.cpp:186-243` | GmatCalcUtil::CalculateAngularData |
| 参数取值域规则（ECC/INC/RMAG/赤道型/Delaunay 等） | `StateConversionUtil.cpp:7046-7382` | StateConversionUtil::ValidateValue |
| $\dot a,\dot f,\dot g,\dot h,\dot k,\dot L$（Read 2016） | `src/base/parameter/OrbitData.cpp:1022-1037` | OrbitData::GetEquinDot |
| 参数 Evaluate 委托链 | `src/base/parameter/KeplerianParameters.cpp:121-129, 234-242, 349-357, 465-473, 581-589, 694-702, 809-817, 924-932, 1039-1047, 1154-1162, 1266-1274, 1381-1386, 1493-1504, 1611-1622` | KepSMA…KepElem / ModKepRadApo / ModKepRadPer |
| 派生轨道量 Evaluate | `src/base/parameter/OrbitalParameters.cpp:126-137, 247, 368, 503, 643, 762, 879` | VelApoapsis / VelPeriapsis / Apoapsis / Periapsis / OrbitPeriod / C3Energy / Energy |
| $\mu^*=m_2/(m_1+m_2)$ 与 L1–L3 五次方程 | `src/base/solarsys/LibrationPoint.cpp:222, 256-281` | LibrationPoint::GetMJ2000State |
| Newton 迭代 $\gamma\leftarrow\gamma-F/F'$，容差 1e-8，上限 2000 | `LibrationPoint.cpp:284-285, 243-249` | 同上 |
| L4/L5 解析 $(1/2,\pm\sqrt3/2)$ | `LibrationPoint.cpp:305-314` | 同上 |
| 旋转系→惯性系 $\mathbf r_{Li}=R\mathbf r_i,\mathbf v_{Li}=\dot R\mathbf r_i+R\mathbf v_i$ | `LibrationPoint.cpp:330-371` | 同上 |
