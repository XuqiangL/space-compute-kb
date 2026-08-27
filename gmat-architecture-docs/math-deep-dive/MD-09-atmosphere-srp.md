# 第9章 大气阻力与太阳光压模型数学

> 本章范围：从代码实现提炼 **大气阻力**（`src/base/forcemodel/DragForce.*`）、**大气密度模型族**（实际位于 `src/base/solarsys/`：`AtmosphereModel` 基类、`ExponentialAtmosphere`、`SimpleExponentialAtmosphere`、`JacchiaRobertsAtmosphere`、`Msise90Atmosphere`，任务描述中的 `forcemodel/atmosphere/` 子目录经 glob 定位为 `solarsys/`，详见下）、**NRLMSISE-00 插件接口**（`plugins/Msise00Plugin/src/base/atmosphere/NRLMsise00Atmosphere.*`）、**太阳光压**（`SolarRadiationPressure.*`、地影几何 `solarsys/ShadowState.*`、N-Plate 反射向量 `spacecraft/Plate.*`）与**相对论修正**（`RelativisticCorrection.*`）的全部公式。共 23 个代码文件（11 个 .cpp + 1 个 .c + 11 个 .hpp，另含 1 个数据文件；另引用 `Spacecraft.cpp`/`SolarFluxReader.hpp`/`gmatdefs.hpp` 的个别函数）。本章只讲公式的**数学内容**与实现；类的职责、继承链、参数表等架构性内容见 [第6章](../CH06-dynamics.md) 2.1.5~2.1.8 与 2.2.6~2.2.7，Msise00Plugin 的工厂注册见 [第14章](../CH14-plugins-b.md) 14.5，本章不再重复。

---

## 一、代码地图：公式住在哪里

```
src/base/forcemodel/
├── DragForce.{hpp,cpp}                阻力 a = −½(CdA/m)ρ v_rel² v̂_rel；预因子；密度标度
├── SolarRadiationPressure.{hpp,cpp}   光压 a = ν·Cr·(F/c)·(A/m)·(r₀/r)²·ŝ；SPAD/N-Plate；A 矩阵
└── RelativisticCorrection.{hpp,cpp}   Schwarzschild + 测地线 + Lense-Thirring 后牛顿修正
src/base/solarsys/
├── AtmosphereModel.{hpp,cpp}          大气模型基类：Density 契约、F10.7/Kp 输入、大地测量、ω
├── ExponentialAtmosphere.{hpp,cpp}    ρ = ρ₀·exp(−(h−h₀)/H)，Vallado 28 带表
├── SimpleExponentialAtmosphere.{hpp,cpp}  STK 三参数单带指数模型
├── JacchiaRobertsAtmosphere.{hpp,cpp} JR-1971：外大气层温度 + 分带密度 + 修正因子
├── Msise90Atmosphere.{hpp,cpp}        MSISE-90 封装（调 gtd6_，cg/cm³→kg/m³）
├── msise90_sub.c                       gtd6_ 入口（:558）
└── ShadowState.{hpp,cpp}               地影锥形几何：全照/本影/半影/环食
src/base/spacecraft/
└── Plate.{hpp,cpp}                     N-Plate 反射向量 R = A·C·D（镜面 ρ + 漫反射 δ）
plugins/Msise00Plugin/src/base/atmosphere/
└── NRLMsise00Atmosphere.{hpp,cpp}      NRLMSISE-00 接口（调 gtd7_，cg/cm³→kg/m³）
application/data/atmosphere/earth/
└── EarthExponentialAtmosphereData.txt  指数模型数据表（h₀, ρ₀, H 三列 × 28 行）
```

**公式主链**：`DragForce::GetDerivatives` 每步取 密度（经 `AtmosphereModel::Density` 虚函数分发到各模型）→ 乘预因子 → 得阻力加速度；`SolarRadiationPressure::GetDerivatives` 每步取 地影受照百分比（`ShadowState::FindShadowState`）→ 乘光压标量 → 得光压加速度。两条链的单位约定相同：状态/加速度为 `km, km/s, km/s²`，密度 `kg/m³`、面积 `m²`、质量 `kg`，故两条链内部都出现 `×1000` 或 `M_TO_KM` 的换算（[第6章](../CH06-dynamics.md) 2.1 末的单位说明同样适用）。

---

## 二、DragForce：阻力加速度

### 2.1 阻力主公式（球形模型）

- **公式**：
  $$\vec a = -\frac{1}{2}\frac{C_d A}{m}\,\rho\,v_{rel}^2\,\hat v_{rel}$$
  分量形式 $a_i = -\tfrac{1}{2}\frac{C_d A}{m}\rho\,|v_{rel}|\,v_{rel,i}$，其中 $\rho$ 为大气密度（kg/m³），$C_d$ 为阻力系数，$A$ 为阻力面积（m²），$m$ 为质量（kg），$v_{rel}$ 为航天器相对大气的速度。

- **代码位置**：公式注释 `src/base/forcemodel/DragForce.cpp:1290-1292`；实现 `DragForce.cpp:1513, 1525-1527`（预因子来自 `:1217`）。

- **深度讲解**：
  **物理背景**：动量交换模型——航天器以相对速度 $v_{rel}$ 扫过密度 $\rho$ 的大气，单位时间撞击的空气质量正比于 $\rho\,|v_{rel}|A$，每个分子带来的动量损失正比于 $v_{rel}$，故 $F \propto \rho A v_{rel}^2$；系数 $1/2$ 与 $C_d$ 吸收流体力学平板阻力公式 $F=\tfrac12 C_d \rho v^2 A$。$C_d$ 是无量纲形状/表面交互系数（LEO 卫星典型 2.0~2.3），$A$ 取迎风投影面积。加速度方向**与 $v_{rel}$ 反向**。
  **实现细节**（`DragForce.cpp:1513` 与 `:1525-1527`，`factor` 把预因子与密度合并）：

  ```cpp
  // 1513: factor = prefactor[i] * density[i];          // prefactor = −½(CdA/m)·1000
  ...
  // 1525: deriv[3+j6] = factor * vRelMag * vRelative[0]; // a_x = factor·|v_rel|·v_rel,x
  // 1526: deriv[4+j6] = factor * vRelMag * vRelative[1]; // a_y
  // 1527: deriv[5+j6] = factor * vRelMag * vRelative[2]; // a_z
  ```
  逐行解释：`factor·|v_rel|` 等价于 $-\tfrac12(C_dA/m)\rho\,v_{rel}$（含 $-1000$ 换算，见 2.4），再逐分量乘 `vRelative` 得到 $v_{rel}^2\hat v_{rel}$ 的三个分量，写入导数速度分量（`deriv[0..2]` 位置分量为 0，因为阻力不直接改变位置速率）。`order==2`（RKN 积分器）时位置/速度分量互换写入（`:1581-1586`）。默认无大气模型时密度取 $4.0\times10^{-13}$ kg/m³（`:3294`），保证模型可跑不崩溃。

### 2.2 相对速度与大气旋转（ω×R）

- **公式**：
  $$\vec v_{rel} = \vec v_{sc} - \vec\omega \times \vec R$$
  其中 $\vec R$ 为航天器在大气天体固连系下的位置，$\vec\omega$ 为中心天体自转角速度（惯性系分量）。

- **代码位置**：`src/base/forcemodel/DragForce.cpp:1501-1509`（默认路径）；无风时的等效代码亦见 `:3423-3428`（A 矩阵有限差分用）。

- **深度讲解**：
  **物理背景**：大气随行星自转共转，固连系中大气速度为 $\vec\omega\times\vec R$；阻力取决于航天器**相对大气的速度**而非惯性速度。忽略此项在 LEO 会造成约 0.46 km/s（赤道）的伪速度差，阻力偏差可达百分之十几，故必须扣除。
  **实现细节**（`DragForce.cpp:1501-1509`）：

  ```cpp
  // 1501: // v_rel = v - w x R
  // 1502: vRelative[0] = dragState[i6+3] -
  // 1503:                (angVel[1]*dragState[i6+2] - angVel[2]*dragState[i6+1]);
  // 1504: vRelative[1] = dragState[i6+4] -
  // 1505:                (angVel[2]*dragState[ i6 ] - angVel[0]*dragState[i6+2]);
  // 1506: vRelative[2] = dragState[i6+5] -
  // 1507:                (angVel[0]*dragState[i6+1] - angVel[1]*dragState[ i6 ]);
  // 1508: vRelMag = sqrt(...)  // |v_rel|
  ```
  逐行解释：`angVel` 由大气模型在惯性系中给出（默认 $(0,0,7.29211585530\times10^{-5})$ rad/s，`AtmosphereModel.cpp:144-146`）；`(angVel[1]*R_z − angVel[2]*R_y)` 即 $\vec\omega\times\vec R$ 的 x 分量，其余类推；状态先在 `TranslateOrigin`（`:1256-1281`）中从力模型原点平移到大气体（当前实现要求两者同体，否则抛异常，`:1259-1264`）。自转角速度按 `wUpdateInterval`（默认 0.02 天 = 28.8 分钟，`DragForce.hpp:159`）周期刷新，见 3.2。

### 2.3 含风模型：v_rel = v − w

- **公式**：
  $$\vec v_{rel} = \vec v_{sc} - \vec w_{wind}$$
  其中 $\vec w_{wind}$ 为大气模型给出的局地风（MJ2000Eq 惯性系，6 维状态向量，取后三维速度）。

- **代码位置**：`src/base/forcemodel/DragForce.cpp:1475-1483`；风接口 `AtmosphereModel::Wind`（基类返回 false，`AtmosphereModel.cpp:883-887`）。

- **深度讲解**：
  **物理背景**：高层大气存在显著的局地风（热层风，可达数百 m/s），把风叠加进 $v_{rel}$ 可提高低轨阻力/寿命预报精度。GMAT 基类不提供风模型（`HasWindModel()` 默认 false，`AtmosphereModel.cpp:864-867`），第三方/派生模型可实现 `Wind` 接口后使 `hasWindModel=true`（`DragForce.cpp:1074`）。
  **实现细节**（`DragForce.cpp:1477-1483`）：

  ```cpp
  // 1477: // v_rel = v - w x R
  // 1478: atmos->Wind(&(dragState[i6]), wind, now, 1);   // 模型填 wind[0..5]，速度在 [3..5]
  // 1479: vRelative[0] = dragState[i6+3] - wind[3];       // v_rel = v_sc − 风速
  // 1480: vRelative[1] = dragState[i6+4] - wind[4];
  // 1481: vRelative[2] = dragState[i6+5] - wind[5];
  // 1482: vRelMag = sqrt(vRelative[0]*vRelative[0] + ...) // |v_rel|
  ```
  逐行解释：注释里的 `v - w x R` 沿袭自 2.2 的写法（本分支不扣 $\omega\times R$，风向量本身已含大气运动），实际计算就是惯性速度减风速。两种路径（有风/无风）共用后续 `factor` 与导数写入，仅 $v_{rel}$ 来源不同（`:1498-1510`）。

### 2.4 预因子 BuildPrefactors 与单位换算

- **公式**：
  $$\text{prefactor} = -\frac{1}{2}\frac{C_d\,A}{m}\times 1000 = -500\,\frac{C_d A}{m}$$
  （SPAD 模式：$\text{prefactor} = -500/m$，面积与 $C_d$ 由 SPAD 文件给出。）

- **代码位置**：`src/base/forcemodel/DragForce.cpp:1182-1189`（注释）、`:1214-1223`（实现）。

- **深度讲解**：
  **物理背景**：把与状态无关的航天器属性（$C_d, A, m$）预先合并成单一标量，避免每个积分步重复乘除——这是飞行力学软件的经典预因子（prefactor）优化。$1000$ 因子的量纲推导：SI 下 $a = -\tfrac12(C_dA/m)\rho v^2$ 得 m/s²；若速度以 km/s 输入，$v_{SI}=1000\,v_{km}$，代入得 $a_{SI}=10^6\cdot\left[-\tfrac12(C_dA/m)\rho\,v_{km}^2\right]$，再除以 1000 换回 km/s²，净得 $\times1000$。等价地看，$(C_dA/m)\rho$ 的量纲是 1/m = $10^{-3}$/km，与 $v^2$（km²/s²）相乘得 $10^{-3}$ km/s²，预因子补 $\times1000$ 即归一为 km/s²；再并入 $\tfrac12$ 与负号即 `-500`。
  **实现细节**（`DragForce.cpp:1214-1223`）：

  ```cpp
  // 1214: if (forModel == "Spherical")
  // 1215: {
  // 1216:    // Note: Prefactor is scaled to account for density in kg / m^3 (*1000/2)
  // 1217:    prefactor[i] = -500.0 * dragCoeff[i] * area[i] / mass[i];
  // 1218: }
  // 1219: else // SPAD
  // 1220: {
  // 1221:    // Note: Prefactor is scaled to account for density in kg / m^3 (*1000/2)
  // 1222:    prefactor[i] = -500.0 / mass[i];
  // 1223: }
  ```
  逐行解释：球形模型把 `Cd·area/mass` 全部折入；SPAD 模式面积与 $C_d$ 来自 SPAD 文件（逐方向、逐时刻变化的向量面积），故预因子只剩 `−500/m`，面积改在力计算处乘（2.8）。质量须为正（`:1207-1213` 抛异常）。质量-面积-系数通过 `SetSatelliteParameter`（`:661-746`）从航天器注入，`DragForce.hpp:198-204` 保存每航天器副本。

### 2.5 密度标度与 Cd/ADSF 参数估计

- **公式**：
  $$C_d = C_{d0}\,(1+\varepsilon_{Cd}),\qquad \text{ADSF} = \text{ADSF}_0\,(1+\varepsilon_{\text{ADSF}})$$
  $$\rho_{used} = \rho_{model}\cdot \text{ADSF}$$
  一阶高斯-马尔可夫（FOGM）模型：$\dot\varepsilon = -\beta\,\varepsilon$，$\beta = \ln 2 / t_{1/2}$（半衰期）。

- **代码位置**：`src/base/forcemodel/DragForce.cpp:1343, 1372`（状态到参数）；`:1354, 1362, 1391`（FOGM）；`:3361`（密度标度应用）。

- **深度讲解**：
  **物理背景**：$C_d$ 与大气密度缩放因子 `AtmosDensityScaleFactor`（ADSF）是轨道确定中两个最常估计的"乘性偏差"。把它们写成 $1+\varepsilon$ 形式，使估计量 $\varepsilon$ 围绕 0 波动，避免参数有偏；密度标度把大气模型本身的系统偏差（模型误差、通量数据误差）吸收为一个乘数。FOGM 对 $\varepsilon$ 施加均值回归，半衰期 $t_{1/2}$ 决定回归速率。
  **实现细节**（`DragForce.cpp:1340-1343, 1360-1363`）：

  ```cpp
  // 1342:    cdEpsilon[i] = state[cdEpsilonIndex + i];   // 从状态向量读 ε_Cd
  // 1343:    dragCoeff[i] = cdInitial[i] * (1 + cdEpsilon[i]); // Cd = Cd0(1+ε)
  ...
  // 1354:    beta[cdFogmIndex + i] = GmatMathUtil::Ln(2.0) / ...HalfLife; // β = ln2/t½
  // 1355:    beta[cdFogmIndex + i] *= direction;
  ...
  // 1362:    deriv[cdEpsilonIndex + i] = -beta[cdFogmIndex + i] * cdEpsilon[i]; // dε/dt = −βε
  ```
  逐行解释：`cdEpsilon` 作为状态元素（`CD_EPSILON`）由积分器推进（`SetStart`，`:3242-3247`）；FOGM 的漂移项写入导数使估计器向 0 回归；ADSF 完全对称（`:1371-1372, 1391`，状态元素 `ATMOS_DENSITY_EPSILON`）。应用点 `:3361`：`density[i] *= atmosDensityScaleFactor[i]`，即 3.7 得到的模型密度乘标度因子后才进 `factor`。A 矩阵中相应列取 $\partial a/\partial\varepsilon = a/(1+\varepsilon)$（`:1816, 1835`）。

### 2.6 Kp→Ap 转换（DragForce::CalculateAp）

- **公式**（无大气模型时的后备公式，Vallado 2nd ed 式 8-31）：
  $$A_p = \exp\!\left(\frac{K_p + 1.6}{1.75}\right)$$

- **代码位置**：`src/base/forcemodel/DragForce.cpp:3464-3466`（注释）、`:3473-3483`（实现）；正式转换在 `AtmosphereModel::ConvertKpToAp`（见 3.3）。

- **深度讲解**：
  **物理背景**：$K_p$ 是行星际磁场驱动的 3 小时地磁活动指数（0~9，按 1/3 步进），$A_p$ 是其线性振幅等效值。JR/MSISE 等模型内部需要 $A_p$（7 个时刻的历史值），而用户只给 $K_p$。指数公式是 $K_p$–$A_p$ 分段表的解析拟合。
  **实现细节**（`DragForce.cpp:3477-3480`）：

  ```cpp
  // 3477: if (atmos)                          // 有大气模型 → 用模型的转换（表/割线，见 3.3）
  // 3478:    newAp = atmos->ConvertKpToAp(kp);
  // 3479: else                                 // 无模型 → 指数近似
  // 3480:    newAp = exp((kp + 1.6) / 1.75);
  ```
  逐行解释：构造时即用默认 $K_p=3.0$ 算出初始 `ap`（`DragForce.cpp:221`）；`SetRealParameter(MAGNETIC_INDEX)` 校验 $0\le K_p\le 9$ 后同步 `ap` 并下发大气模型（`:2311-2337`）。

### 2.7 质量雅可比与 A 矩阵有限差分

- **公式**：
  $$\frac{\partial \vec a}{\partial m} = -\frac{\vec a}{m}\qquad(\text{因 }a\propto 1/m)$$
  A 矩阵位置子块：$\dfrac{\partial a_i}{\partial r_j} \approx \dfrac{a_i(r+\Delta r_j)-a_i(r)}{\Delta r_j}$，$\Delta r_j = 10^{-2}$ km；速度子块同理，$\Delta v_j = 10^{-6}$ km/s。

- **代码位置**：`src/base/forcemodel/DragForce.cpp:1903-1911`（质量雅可比）；`:1706-1803`（位置/速度有限差分）。

- **深度讲解**：
  **物理背景**：状态转移矩阵（STM）与 A 矩阵的阻力贡献。位置分量的解析导数涉及密度梯度（由大气模型隐式给出），代码选择数值差分：对位置加扰动后重算 `Accelerate`（`:3401-3455`，内部重新查密度、重算 $v_{rel}$），差商填入 A 矩阵行 4~6。质量雅可比对估计质量与 STM 的质量行必需。
  **实现细节**（`DragForce.cpp:1706-1710, 1723-1724`）：

  ```cpp
  // 1706: for (UnsignedInt j = 0; j < 3; ++j)
  // 1708:    val = state[i*6 + j];            // 保存原值
  // 1709:    state[i*6 + j] += pert;          // pert = 1e-2 km 位置扰动
  // 1710:    daccel = Accelerate(i, &state[i*6], now, prefactor[0]);
  // 1711:    ix = stmRowCount * 3 + j;
  // 1724:    aTilde[ix+k*stmRowCount] = (daccel[k] - accel[k]) / pert; // 前向差商
  ```
  逐行解释：`pert=1e-2` 对位置、`1e-6` 对速度（`:1757`）；`useCentralDifferences` 时用中心差分 `(a(+)−a(−))/(2pert)`（`:1713-1730`）；差分后恢复状态（`:1752`）。速度子块只支持数值差分，解析未实现（`:1805-1809` 抛异常）。

### 2.8 SPAD 阻力模型

- **公式**：
  $$\vec a = -\frac{1}{2}\frac{\rho}{m}\,\vec A_{SPAD}\,|v_{rel}|^2 \qquad(\vec A_{SPAD}\text{ 为 SPAD 文件给出的方向面积向量，m²})$$
  注意 `GetDerivatives` 主循环用 $|v_{rel}|^2$（`:1626-1628`），而 `GetDerivativesForSpacecraft` 用 $|v_{rel}|\,v_{rel,i}$（`:2044-2046`）。

- **代码位置**：`src/base/forcemodel/DragForce.cpp:1611-1647`；`Spacecraft::GetSPADDragArea` `src/base/spacecraft/Spacecraft.cpp:2786-2811`。

- **深度讲解**：
  **物理背景**：SPAD（Spacecraft Plasma Analysis and Drag？此处为 GMAT 的面积文件格式）把航天器外形离散为**随姿态变化的面元面积向量**：文件按方向表插值出"该方向的等效投影面积×系数"三分量，姿态旋转后变换回惯性系。阻力不再用标量 $C_d A$ 而用向量面积，`AttitudeAffectsDynamics()` 返回 true（`DragForce.cpp:917-920`），ODE 必须联立姿态积分。
  **实现细节**（`DragForce.cpp:1621-1628`）：

  ```cpp
  // 1621: Rvector3 velVec(vRelative[0], vRelative[1], vRelative[2]);
  // 1622: spadArea = ((Spacecraft*) scObjs.at(i))->GetSPADDragArea(now, velVec);
  // 1623: if (order == 1)
  // 1626:    deriv[3+j6] = factor * spadArea[0] * vRelMag * vRelMag; // factor=−500ρ/m
  // 1627:    deriv[4+j6] = factor * spadArea[1] * vRelMag * vRelMag;
  // 1628:    deriv[5+j6] = factor * spadArea[2] * vRelMag * vRelMag;
  ```
  逐行解释：`GetSPADDragArea` 把速度向量转到体固系、用 `SPADFileReader` 查表得面积三分量、再转回惯性系（`Spacecraft.cpp:2758-2780` 是 SRP 版，阻力版同构）；`factor` 已含 `−500/m`（2.4），面积在这里才乘入，故是 $|v_{rel}|^2$ 形式。两处 `|v_{rel}|^2` 与 $|v_{rel}|v_{rel,i}$ 的写法差异是历史遗留（量纲一致），文档按代码原样标注。

---

## 三、大气密度模型族（src/base/solarsys/）

### 3.1 AtmosphereModel 基类：Density 契约与空间天气输入

- **公式**（契约，非具体模型）：
  $$\text{Density}(\vec r, \rho, t) : \rho\in[\text{kg/m}^3]\qquad\text{纯虚函数}$$
  基类持有空间天气输入：$F_{10.7}$、$F_{10.7A}$（3 月滑动平均）、$K_p$，默认常数 $F_{10.7}=F_{10.7A}=150$ sfu、$K_p=3.0$。

- **代码位置**：`src/base/solarsys/AtmosphereModel.hpp:79-80`（Density 纯虚）；`AtmosphereModel.cpp:90-156`（构造默认值，`:103-108`）；`AtmosphereModel.hpp:276-281`（参数枚举）。

- **深度讲解**：
  **物理背景**：$F_{10.7}$（10.7 cm 射电通量，sfu，1 sfu = $10^{-22}$ W/m²/Hz）是太阳极紫外辐射的代理量，直接驱动热层温度与密度；$K_p/A_p$ 刻画地磁活动对高纬加热的贡献。所有大气模型共享"常数 or CSSI 历史文件 or Schatten 预测文件"三种来源，由 `SetInputSource`（`:792-816`）与 `SetSchattenFlags`（`:828-852`）配置（历史源：0=常数、1=CSSI；预测源：0=常数、1=CSSI、2=Schatten；Schatten 时相/误差：Early/Nominal/Late × −2σ/Nominal/+2σ）。
  **实现细节**（`AtmosphereModel.cpp:356-362`）：

  ```cpp
  // 356: if (fluxReader == NULL)
  // 357: {
  // 358:    fluxReader = new SolarFluxReader();          // 通量文件读取器
  // 359:    fluxReader->SetHistoricDataSource(historicalDataSource);
  // 360:    fluxReader->SetPredictedDataSource(predictedDataSource);
  // 361:    fluxReader->SetConstValues(constantF107, constantF107a, constantKp, constantAp);
  // 362: }
  ```
  逐行解释：`SolarFluxReader`（`SolarFluxReader.hpp:55-69` 的 `FluxData`：`obsF107/obsCtrF107a/kp[8]/ap[8]`）在 `GetInputs` 中被按需惰性加载（3.4）。默认自转角速度 $(0,0,7.29211585530e-5)$ rad/s（`:146`）即地球标称值，供 2.2 的 $\omega\times R$ 使用。

### 3.2 大地测量（geodetic）与自转角速度

- **公式**（Vallado 算法 12，迭代大地纬度）：
  $$e^2 = f(2-f),\qquad N(\phi)=\frac{R_e}{\sqrt{1-e^2\sin^2\phi}},\qquad
    \phi_{k+1}=\tan^{-1}\!\left(\frac{z+N(\phi_k)e^2\sin\phi_k}{\sqrt{x^2+y^2}}\right),\qquad
    h = \frac{r_{xy}}{\cos\phi}-N(\phi)$$
  自转角速度：$\vec\omega = \mathbf R\,[\mathbf R^T\dot{\mathbf R}]_\times$ 的反对称分量。

- **代码位置**：`src/base/solarsys/AtmosphereModel.cpp:1559-1578`（大地纬度迭代）、`:1576-1578`（高度）；自转角速度 `:512-562`。

- **深度讲解**：
  **物理背景**：所有密度模型都需要"高于参考椭球的高度"与纬/经度。大地纬度（geodetic）与地心纬度（geocentric）差可达 ~0.2°，对 100 km 尺度的大气分层不可忽略；GM 默认 `useGeodetic=true`（`:122`）。
  **实现细节**（`AtmosphereModel.cpp:1564-1578`）：

  ```cpp
  // 1564: Real ecc2 = cbFlattening * (2.0 - cbFlattening); // 第一偏心率平方 e²
  // 1567: while (delta > geodeticTolerance)                // 迭代至 1e-7 rad 收敛
  // 1571:    cFactor = cbRadius / sqrt(1.0 - ecc2 * sinlat * sinlat); // N(φ)
  // 1572:    geoLat  = atan2(state[2] + cFactor*ecc2*sinlat, rxy);   // φ_{k+1}
  // 1576: sinlat = sin(geoLat);
  // 1577: cFactor = cbRadius / sqrt(1.0 - ecc2 * sinlat * sinlat);
  // 1578: geoHeight = rxy / cos(geoLat) - cFactor;         // h = rxy/cosφ − N
  ```
  逐行解释：位置先经 `CoordinateConverter` 从 MJ2000Eq 转到体固系（`:1550-1551`）；`cbRadius/cbFlattening` 来自 `SetCentralBody`（`:987-988`）。`BuildAngularVelocity`（`:512-529`）用 $\mathbf R^T\dot{\mathbf R}$ 构造角速度并旋转到 J2000；`UpdateAngularVelocity`（`:577-591`）按 `wUpdateInterval` 节流刷新（2.2 的 28.8 分钟默认即来自此）。`CalculateGeocentrics`（`:1618-1704`）是地心版，结构相同。

### 3.3 Kp→Ap 三种转换方法

- **公式**：
  - 表查（默认，Vallado 3rd ed 表 8-3）：$A_p = T(K_p)$，如 $K_p=0\to0$、$K_p=1\to4$、$K_p=3\to15$、$K_p=9\to400$。
  - 指数近似（Vallado 2nd ed 式 8-31）：$A_p = e^{(K_p+1.6)/1.75}$。
  - 割线法解超越方程：$28K_p + 0.03e^{K_p} = A_p + 100(1-e^{-0.08A_p})$。

- **代码位置**：`src/base/solarsys/AtmosphereModel.cpp:640-775`（`ConvertKpToAp`，注释 `:620-631`）。

- **深度讲解**：
  **物理背景**：$K_p$（对数尺度）到 $A_p$（线性尺度）官方定义即查表；解析式便于连续化。割线法是求解反函数的数值途径。
  **实现细节**（`AtmosphereModel.cpp:646-648, 741-742, 745-771`）：

  ```cpp
  // 646: case 0:  // 表查
  // 648:    Integer index = (Integer)((kp + .01) * 3);   // 0~27 档，覆盖 0~9 每 1/3 步
  // 651:    case 0:  ap = 0.0;  break;                  // Kp=0
  // 733:    case 9:  default: ap = 15.0; break;         // Kp=3 档
  // 741: case 1:  // Vallado 2nd ed
  // 742:    ap = exp((kp + 1.6) / 1.75);
  // 748: case 2:  // 割线法
  // 759:    y[0] = 100.0 * exp(-0.08 * x[0]) + r - x[0]; // r = 28Kp+0.03e^Kp−100
  // 762:    x[2] = x[1] - y[1] * (x[1] - x[0]) / (y[1] - y[0]); // 割线更新
  ```
  逐行解释：表查索引 `(kp+0.01)*3` 把 0~9 映射到 0~27 档（`:648-731`）；割线法从 $x_0=0,x_1=500$ 出发迭代至 $|y|<10^{-6}$，最多 15 次（`:750-771`）。方法由 `SetKpApConversionMethod` 选择（`:603-607`），默认 0。JR 内部用的是 `geo.tkp`（$K_p$ 本身，见 3.7），MSISE 用 $A_p$ 序列（3.4）。

### 3.4 GetInputs：F10.7/Kp 数据流

- **公式**（历元→日期分解）：
  $$\text{year} = 1941 + \left\lfloor\frac{t+5.5}{365.2422}\right\rfloor,\qquad
    \text{doy} = \lfloor t\rfloor - \lfloor\text{yearOffset}\cdot365.2422\rfloor + 5,\qquad
    \text{sod} = 86400\,(t - \lfloor t\rfloor + 0.5)$$
  输出 `yd = year*1000 + doy`（MSISE 的 YYYYDDD 格式）。

- **代码位置**：`src/base/solarsys/AtmosphereModel.cpp:1717-1884`（`GetInputs`），日期分解 `:1725-1742`，通量选择 `:1803-1861`。

- **深度讲解**：
  **物理背景**：MSISE/JR 家族需要"年+年内日+秒内日"作为时间输入；F10.7/F10.7A/Ap 需要按"历史/预测"两个区间分别取源。这是全部大气模型共享的数据管线（`Msise90Atmosphere.cpp:179`、`NRLMsise00Atmosphere.cpp:178`、`JacchiaRobertsAtmosphere.cpp:483-524` 都调它或其同构逻辑）。
  **实现细节**（`AtmosphereModel.cpp:1805-1815` 历史 CSSI 分支）：

  ```cpp
  // 1805: if (epoch < historicEnd)          // 历史区间
  // 1809: case 1:                           // CSSI 文件
  // 1810:    fDbuffer = fluxReader->GetInputs(epoch);
  // 1811:    fluxReader->PrepareApData(fDbuffer, epoch);   // 由 Kp 序列准备 7 个 Ap
  // 1812:    f107  = fDbuffer.obsF107;       // 当日 F10.7
  // 1813:    f107a = fDbuffer.obsCtrF107a;   // 81 日中心滑动平均 F10.7A
  // 1814:    for (Integer i = 0; i < 7; i++)
  // 1815:        ap[i] = fDbuffer.ap[i];     // 当前及前 6 个 3h Ap（MSISE 输入）
  ```
  逐行解释：`epoch < historicEnd` 走历史源、否则走预测源（`:1833-1861`，预测源 1/2 同为文件，0 为常数）；常数分支把 7 个 `ap[i]` 全填 `constantAp`（`:1823-1826`）。`PrepareApData`（`SolarFluxReader.hpp:250`）负责把观测 Kp 序列换算成 MSISE 需要的 `ap[0..6]`（当前 3h、前 3h、前 6h、前 9h、前 12h、前 33h、前 57h 的近似）。该数据流汇总：**文件/常数 → FluxData{obsF107, obsCtrF107a, kp[], ap[]} → f107/f107a/ap[7] → 各模型**。

### 3.5 ExponentialAtmosphere：分层指数密度

- **公式**：
  $$\rho(h) = \rho_0^{(k)}\,\exp\!\left(-\frac{h_{ellp}-h_0^{(k)}}{H^{(k)}}\right),\qquad
    h_0^{(k)}\le h_{ellp} < h_0^{(k+1)}$$
  其中 $(h_0^{(k)},\rho_0^{(k)},H^{(k)})$ 是第 $k$ 带参数（Vallado p.534 表 8-4 / Wertz p.820，共 28 带）。

- **代码位置**：公式注释 `src/base/solarsys/ExponentialAtmosphere.hpp:48-55`；实现 `ExponentialAtmosphere.cpp:490-495`；常数表 `:557-641`；数据文件 `application/data/atmosphere/earth/EarthExponentialAtmosphereData.txt:1-28`。

- **深度讲解**：
  **物理背景**：等温大气假设下静力学平衡给出指数密度，但真实大气温度分层使 $H$ 随高度变化，故用 28 带分段常数 $H$。地面参考 $\rho_0(0\,\text{km})=1.225$ kg/m³、$H=7.249$ km；100 km 处 $\rho_0=5.297\times10^{-7}$、$H=5.877$ km；1000 km 处 $3.019\times10^{-15}$、$H=268$ km（`:557-641` 硬编码与数据文件一致，文件在 `ReadParameters` 中按 `"Earth"/"Mars"` 读取，`:372-380`）。本模型**无太阳活动调制**（头注释 `ExponentialAtmosphere.hpp:43-46`），不建大气凸起。
  **实现细节**（`ExponentialAtmosphere.cpp:490-495`）：

  ```cpp
  // 485: height = CalculateGeodetics(loc, epoch);   // 大地高度（3.2）
  // 490: index = FindBand(height);                  // 定位高度带
  // 491: if (smoothDensity)
  // 492:    density[i] = Smooth(height, index);      // 平滑（未实现，:688 抛异常）
  // 493: else
  // 494:    density[i] = refDensity[index] * exp(-(height - refHeight[index]) /
  // 495:                                          scaleHeight[index]);   // ρ=ρ₀e^{−(h−h₀)/H}
  ```
  逐行解释：`FindBand`（`:656-668`）线性扫描找 `height < refHeight[i+1]` 的首个带；`Smooth`（`:686-689`）当前直接抛 "not yet coded"，注释说明积分在带边界的小间断处稳定，故未启用；高度为负（进入行星内部）抛异常（`:486-488`）。带边界处密度不连续（相邻带 $\rho_0$ 与 $H$ 不同），幅值差在数值可接受范围。

### 3.6 SimpleExponentialAtmosphere：STK 三参数单带模型

- **公式**：
  $$\rho(h) = \rho_0\,\exp\!\left(-\frac{h-h_0}{H}\right),\qquad H=8.5\ \text{km},\ h_0=0\ \text{km},\ \rho_0=1.217\ \text{kg/m}^3$$

- **代码位置**：`src/base/solarsys/SimpleExponentialAtmosphere.cpp:51-53`（默认参数）、`:155-160`（密度实现）。

- **深度讲解**：
  **物理背景**：STK 图形界面中可配置的三参数简化模型，单带、无表、无太阳活动，用于快速定性分析（低轨粗估）。位置需先减中心体位置（`:151-153`，本类直接使用 `centralBodyLocation`，与 `ExponentialAtmosphere` 经 `CalculateGeodetics` 不同）。
  **实现细节**（`SimpleExponentialAtmosphere.cpp:155-160`）：

  ```cpp
  // 155: height = CalculateGeodetics(loc, epoch);   // 大地高度
  // 156: if (height < 0.0) throw ...;               // 行星内部保护
  // 160: density[i] = refDensity * exp(-(height - refHeight) / scaleHeight);
  ```
  逐行解释：参数为标量而非数组，故无需 `FindBand`；其余流程与 3.5 相同。`geocentricAltitude` 成员（`:54`）为未来地心模式预留，当前恒用大地高度。

### 3.7 JacchiaRoberts：外大气层温度

- **公式**（核心温度模型）：
  $$T_\infty = \begin{cases}
    T_1 + 14\,K_p + 0.02\,e^{K_p}, & h < 200\ \text{km}\\[2pt]
    T_1 + 28\,K_p + 0.03\,e^{K_p}, & h \ge 200\ \text{km}
  \end{cases},\qquad
  T_1 = T_{ex,0}\left[1+0.3\left(\sin^{2.2}\theta + \cos^3\tfrac{\tau}{2}\left(\cos^{2.2}\eta - \sin^{2.2}\theta\right)\right)\right]$$
  其中 $\theta=\tfrac12|\varphi_{lat}+\delta_\odot|$、$\eta=\tfrac12|\varphi_{lat}-\delta_\odot|$、$\tau$ 为修正时角，基温 $T_{ex,0}=379+3.24\,F_{10.7A}+1.3\,(F_{10.7}-F_{10.7A})$（`geo.xtemp`）。$h<125$ km 时 $T(h) = T_x + (T_x-T_0)\,C(h)/1.500625\times10^6$，$C(h)$ 为 CON_C 多项式；$h>125$ km 时 $T(h) = T_\infty - (T_\infty-T_x)\exp\!\left[-\frac{T_x-T_0}{T_\infty-T_x}\frac{h-125}{35}\frac{L(T_\infty)}{R_p+h}\right]$，$L$ 为 CON_L 多项式。辅助量 $T_x = 371.6678 + 0.0518806\,T_\infty - 294.3505\,e^{-0.00216222\,T_\infty}$。

- **代码位置**：`src/base/solarsys/JacchiaRobertsAtmosphere.cpp:546`（基温）、`:844-855`（θ/η/τ/T₁）、`:868-878`（T∞ 与 Tx）、`:884-903`（高度外推）；常数 `CON_C :67-74`、`CON_L :76-83`。

- **深度讲解**：
  **物理背景**：Jacchia-Roberts（1971，Swingby 移植）是半经验扩散平衡模型。**太阳加热**（$F_{10.7}$ 项）、**地磁加热**（$K_p$ 项）与**昼夜/纬向不对称**（$\theta,\eta,\tau$ 的球谐状因子）共同决定外大气层温度 $T_\infty$；$T_\infty$ 沿高度向低层外推得到温度剖面，再以扩散平衡求各组分密度。
  **实现细节**（`JacchiaRobertsAtmosphere.cpp:868-878`）：

  ```cpp
  // 868: if (height < 200.0)
  // 870:    t_infinity = t1 + 14.0 * geo->tkp + 0.02 * expkp;   // 低轨地磁加热项
  // 871: else
  // 874:    t_infinity = t1 + 28.0 * geo->tkp + 0.03 * expkp;   // 高层加热更强
  // 877: tx = 371.6678 + 0.0518806 * t_infinity - 294.3505 *
  // 878:      exp(-0.00216222 * t_infinity);                    // 125 km 处锚定温度
  ```
  逐行解释：`geo->tkp` 是 $K_p$（`GEOPARMS` 结构 `gmatdefs.hpp:95-100`），`geo->xtemp` 是 $T_{ex,0}$；$t_1$ 中的 `th22 = sin^{2.2}(θ)`、`pow(cos(0.5*tau),3.0)` 等即上述公式（`:852-854`）。$h<125$ km 的分段多项式对高度展开（CON_C），$h>125$ km 对 $T_\infty$ 展开（CON_L）后指数外推（`:884-903`）。`sun_dec = atan2(sun[2], sqrt(sun[0]²+sun[1]²))`（`:640`）为太阳赤纬，`geo_lat` 为大地纬度（弧度，`:642`）。

### 3.8 JacchiaRoberts：低层密度（90–125 km）

- **公式**（90–100 km，`rho_100`）：
  $$\rho(h) = \frac{\rho_{90}\,T_{90}\,M(h)\,\exp\!\left[k\,(\ln f_1(h)+f_2(h))\right]}{M_{90}\,T(h)},\qquad
    k = -\frac{g_0}{R_g(T_x-T_0)}\quad(\text{Vallado 3rd ed p.951})$$
  其中 $M(h)$ 为平均分子量多项式（M_CON），$f_1,f_2$ 由 S_CON/S_BETA 构造的偏分式 + 反正切积分给出；$\rho_{90}=3.46\times10^{-9}$ g/cm³、$T_{90}=183$ K、$M_{90}=28.82678$、$g_0=9.80665$ m/s²、$R_g=8.31432$ J/(K·mol)（`RHO_ZERO/TZERO/MZERO/G_ZERO/GAS_CON :54-62, 86`）。
  （100–125 km，`rho_125`：$\rho(h)=\rho'(T_\infty)\,\dfrac{T_{100}}{T(h)}\sum_i M_i N_i \exp\!\left[M_i k'\,(f_3(h)+f_4(h))\right]$，氦项指数带 $-0.38$ 修正，$k'=-\dfrac{1500625\,g_0 R_p^2}{R_g C_4(T_x-T_0)}$，$\rho'$ 为 ZETA_CON 多项式、$T_{100}=T_x+\Omega(T_x-T_0)$，$\Omega=-0.94585589$。）

- **代码位置**：`src/base/solarsys/JacchiaRobertsAtmosphere.cpp:955-1066`（rho_100，k 因子 `:1047`，返回 `:1064-1065`）；`:1082-1163`（rho_125，k′ `:1147`，求和 `:1150-1162`）；高度选择 `:711-736`。

- **深度讲解**：
  **物理背景**：90~125 km 是分子扩散→涡流扩散混合过渡区，JR 用解析偏分式（把高度积分 $\int 1/T\,dh$ 解析化：以 $T(h)$ 剖面在复平面上的根做部分分式展开）求密度，避免数值积分。$k$ 是无量纲高度积分的系数，$f_1\sim f_4$ 是 $\ln$ 与 $\arctan$ 组合。
  **实现细节**（`JacchiaRobertsAtmosphere.cpp:1047, 1064-1065`）：

  ```cpp
  // 1047: factor_k = -G_ZERO/(GAS_CON*(tx-TZERO));   // Vallado p 951，替换旧的 GTDS 形式
  // 1064: return RHO_ZERO * TZERO * m_poly * exp(factor_k*(log_f1 + f2)) /
  // 1065:        (MZERO * temperature);
  ```
  逐行解释：`m_poly` 是 M_CON 对高度求值的平均分子量（`:962-965`）；`log_f1` 含四个 $\ln$ 项（`:1026-1030`），`f2` 含 $\arctan$ 项（`:1033-1036`）；最终密度以 g/cm³ 为单位，由 `Density()` 统一乘 $10^3$ 转 kg/m³（`:376-377`）。`rho_125` 逐组分求和（N₂/Ar/He/O₂/O，`MOL_MASS/NUM_DENS :132-149`），各组分按各自分子量指数化（`:1150-1159`），氦的 $-0.38$ 是扩散分离修正（`:1155-1158`）。`roots()`（`:1354-1427`，Newton 法）与 `deflate_polynomial()`（`:1458-1473`）在 `exotherm` 中求温度剖面的复根，供部分分式展开使用（`:912-936`）。

### 3.9 JacchiaRoberts：高层密度（125–2500 km）

- **公式**（`rho_high`，扩散平衡）：
  $$\rho(h) = \sum_{i=0}^{5} r_i,\qquad
    r_i = f_i\,M_i\,d_i\left(\frac{T_x}{T}\right)^{1+\gamma_i}
          \left(\frac{T_\infty-T}{T_\infty-T_x}\right)^{\gamma_i}$$
  $$\gamma_i = \frac{35\,M_i\,g_0\,R_p^2\,(T_\infty-T_x)}{R_g\,L(T_\infty)\,T_\infty\,(T_x-T_0)\,(R_p+125)},\qquad
    d_i = 10^{P_i(T_\infty)}/N_A\ (P_i \text{ 为 CON_DEN 多项式})$$
  氦（$i=2$）修正：指数减 0.38、乘 $f=10^{4.9914|\delta_\odot|(\sin^3(\pi/4-\varphi_{lat}\,\text{sgn}\,\delta_\odot/2)-0.35355)/\pi}$；氢（$i=5$，仅 $h>500$ km）：$r_H = M_H\,10^{73.13-(39.4-5.5\log_{10}T_{500})\log_{10}T_{500}}\,(T_{500}/T)^{1+\gamma}((T_\infty-T)/(T_\infty-T_{500}))^{\gamma}/N_A$。

- **代码位置**：`src/base/solarsys/JacchiaRobertsAtmosphere.cpp:1238-1310`（rho_high；γ `:1264-1265`、d_i `:1255-1259`、氦 `:1274-1281`、氢 `:1284-1292`）；高度选择 `:737-749`。

- **深度讲解**：
  **物理背景**：125 km 以上各组分处于扩散平衡，密度按 $\left(\frac{T_x}{T}\right)^{1+\gamma}\left(\frac{T_\infty-T}{T_\infty-T_x}\right)^{\gamma}$ 的"温度比幂律"随高度衰减，γ 由组分分子量与重力位差决定；氦因逃逸/扩散分离需额外修正，氢只在 500 km 以上计入（其 500 km 处参考密度由经验对数多项式给出）。
  **实现细节**（`JacchiaRobertsAtmosphere.cpp:1264-1265, 1298-1299`）：

  ```cpp
  // 1264: gamma = 35.0 * MOL_MASS[i] * G_ZERO * cbPolarSquared * (t_infinity - tx) /
  // 1265:        ( GAS_CON * sum * t_infinity * (tx - TZERO) * polar125);  // polar125=Rp+125
  // 1298: r = f * MOL_MASS[i] * di * pow(tx/temperature, exp1)
  // 1299:     * pow((t_infinity - temperature)/(t_infinity - tx), gamma);
  ```
  逐行解释：`sum` 是 CON_L 多项式在 $T_\infty$ 处的值（`exotherm :894-898` 算好，`rho_high` 直接复用）；`exp1 = 1+γ`（`:1268`）；`di = 10^{log_di}/N_A`（`:1255-1259`，CON_DEN 是组分密度对 $T_\infty$ 的对数多项式）。>2500 km 密度置 0（`:750-757`），因为该高度以上模型外推不可靠。

### 3.10 JacchiaRoberts：密度修正因子 rho_cor

- **公式**：
  $$\rho_{corr} = 10^{\,g_{geo}+g_{sem}+g_{lat}}$$
  $$g_{geo} = \begin{cases}0.012\,K_p + 0.000012\,e^{K_p}, & h<200\ \text{km}\\ 0, & h\ge200\ \text{km}\end{cases}$$
  $$g_{sem} = \left(5.876\times10^{-7}h^{2.331}+0.06328\right)e^{-0.002868h}\cdot g_{SA},\qquad
    g_{SA} = 0.02835+\left(0.3817+0.17829\sin(2\pi\tau_{sa}+4.137)\right)\sin(4\pi\tau_{sa}+4.259)$$
  $$\tau_{sa} = d_{58}+0.09544\left[\left(\tfrac12(1+\sin(2\pi d_{58}+6.035))\right)^{1.65}-\tfrac12\right],\qquad d_{58}=\tfrac{t_{A1}-6204.5}{365.2422}$$
  $$g_{lat} = 0.014\,(h-90)\,\sin(2\pi d_{58}+1.72)\,\sin\varphi_{lat}\,|\sin\varphi_{lat}|\,e^{-0.0013(h-90)^2}$$

- **代码位置**：`src/base/solarsys/JacchiaRobertsAtmosphere.cpp:1179-1218`（rho_cor；地磁 `:1186-1193`、半年 `:1196-1204`、季节纬向 `:1207-1210`、返回 `:1217`）；应用 `:765`。

- **深度讲解**：
  **物理背景**：JR 的三个经验修正——**地磁活动**（低层额外加热）、**半年变化**（两分点附近密度峰）、**季节-纬向变化**（7 月南北极不对称氦/氧分布）——以 $10^{(\cdot)}$ 乘子的形式作用在扩散平衡密度上。注意 `rho_cor` 用 `geo.tkp`（$K_p$）而非 $A_p$。
  **实现细节**（`JacchiaRobertsAtmosphere.cpp:1186-1188, 1196-1204, 1217`）：

  ```cpp
  // 1188: geo_cor = 0.012 * geo->tkp + 0.000012 * exp(geo->tkp);   // h<200 地磁项
  // 1196: f = (5.876e-7 * pow(height, 2.331) + 0.06328) *
  // 1197:     exp(-0.002868 * height);                             // 半年变化幅度包络
  // 1198: day_58 = (a1_time - 6204.5)/365.2422;                   // 自 1958.0 起的天数
  // 1201: alpha = sin(4.0*PI*tausa + 4.259);                      // 半年双谐波
  // 1217: return pow(10.0, geo_cor + semian_cor + slat_cor);      // 三修正合并为乘子
  ```
  逐行解释：`6204.5` 是 1958 年 1 月 0 日的 MJD（半年变化的相位基准）；`tausa` 含 0.09544 的非线性"半年相位调制"项（`:1199-1200`）；`g` 是幅度随 $\tau_{sa}$ 变化的半年振荡（`:1202-1203`）。最终 `Density()` 返回 `密度 × rho_cor`（`:765`）。

### 3.11 MSISE-90：gtd6_ 接口与单位换算

- **公式**（接口，模型内部为 Fortran/C 经验展开）：
  $$\rho = \rho_{gtd6}(yd,\ sod,\ h_{geo},\ \varphi_{geo},\ \lambda,\ LST,\ F_{10.7A},\ F_{10.7},\ ap[7]) \times 1000$$
  输入为 UTC 历元分解出的 YYYYDDD、日内秒、大地高度/纬度/经度、地方太阳时 LST；输出 `den[5]`（总质量密度，g/cm³），乘 1000 得 kg/m³。

- **代码位置**：`src/base/solarsys/Msise90Atmosphere.cpp:176-179`（UTC 转换 + GetInputs）、`:221-222`（大地测量与 LST）、`:295-299`（gtd6_ 调用）、`:340`（单位换算）；C 入口 `src/base/solarsys/msise90_sub.c:558-560`。

- **深度讲解**：
  **物理背景**：MSISE-90（Mass Spectrometer Incoherent Scatter radar, Extended）把热层中性大气密度建模为经验函数，输入 F10.7/F10.7A（太阳 EUV 代理）与 ap[7]（地磁活动时间序列）。GMAT 封装由 a.i. Solutions 从 Fortran 移植（`Msise90Atmosphere.hpp:30-31`）。`gtd6_` 输出 8 个数密度 + 2 个温度，密度取索引 5（总质量密度）。
  **实现细节**（`Msise90Atmosphere.cpp:295-299, 340`）：

  ```cpp
  // 295: gtd6_(&xyd,&xsod,&xalt,&xlat,&xlon,&xlst,&xf107a,&xf107,&xap[0],&xmass,
  // 296:       &xden[0],&xtemp[0]);
  //      // 参数: YYYYDDD, 日内秒, 高度km, 纬度°, 经度°, LST h, F10.7A, F10.7, ap[7],
  //      //       质量标志(=48), 密度输出den[9], 温度输出temp[2]
  // 340: density[i] = xden[5] * 1000.0;   // den[5]=总质量密度(g/cm³)→kg/m³
  ```
  逐行解释：`mass=48`（`:216`）选择总质量密度输出标志；`lst = sod/3600.0 + geoLong/15.0`（`:222`，地方太阳时 = 日内小时 + 经度/15°）；UTC 转换用 `JD_JAN_5_1941` 基准（`:176-177`，与 GetInputs 的 year=1941 起始一致）。C 侧 `gtd6_`（`msise90_sub.c:558`）内部按 mesosphere/thermosphere 分层、纬度-季节展开，是纯经验系数运算，无解析闭式。

### 3.12 NRLMSISE-00（插件）：gtd7_ 接口

- **公式**（接口）：
  $$\rho = \rho_{gtd7}(iyd,\ sec,\ alt,\ glat,\ glong,\ stl,\ f107a,\ f107,\ ap[7],\ mass) \times 1000$$
  输出 `d[5]` 为总质量密度，乘 1000 得 kg/m³。源码注释写 "cg/cm³" 系笔误：`gtd7_` 官方输出单位是 g/cm³，1 g/cm³ = 1000 kg/m³，故 `×1000`（与 MSISE-90 的 `:340`、JR 的 `:376` 完全一致）。

- **代码位置**：`plugins/Msise00Plugin/src/base/atmosphere/NRLMsise00Atmosphere.cpp:176-178`（UTC+GetInputs）、`:217-218`（大地测量与 LST）、`:284-285`（gtd7_ 调用）、`:322`（单位换算）；Fortran/C 内核 `plugins/Msise00Plugin/src/base/atmosphere/nrlmsise00_sub.c`（入口 `gtd7_` 见 [第14章](../CH14-plugins-b.md) 14.5.1 说明，f2c 翻译）。

- **深度讲解**：
  **物理背景**：NRLMSISE-00 是 MSISE-90 的继承者（NRL 2001 版），新增异常氧、更精细的低层参数化。GMAT 以插件形式提供（`Msise00Plugin`），工厂键 `"NRLMSISE00"` 由 `NRLMsise00Factory` 注册（[第14章](../CH14-plugins-b.md) 表 14-2）。
  **实现细节**（`NRLMsise00Atmosphere.cpp:284-285, 322`）：

  ```cpp
  // 284: gtd7_((integer*)&xyd,&xsod,&xalt,&xlat,&xlon,&xlst,&xf107a,&xf107,
  // 285:       &xap[0],(integer*)&xmass,&xden[0], &xtemp[0]);
  //      // 与 gtd6_ 同构：YYYYDDD, 秒, 高度, 纬度, 经度, LST, F10.7A, F10.7, ap[7],
  //      //             质量标志(48), 密度den[9], 温度temp[2]
  // 322: density[i] = ((double)xden[5] * 1000.0);  // den[5] 总质量密度 → kg/m³
  ```
  逐行解释：`mass=48`（`:215`）；`GetInputs(utcEpoch)`（`:178`）走基类数据管线（3.4）；输出同样取 `den[5]`。插件层仅做"状态→大地坐标→gtd7_ 调用→单位换算"，模型系数全在 `nrlmsise00_sub.c` 的 COMMON 块中，编译期可用 `__SKIP_NRLMSISE00__` 禁用（`:38-45`）。

### 3.13 大气模型数据流总览（F10.7/Kp → 密度 → 阻力）

- **公式**（数据流，无闭式）：
  $$\underbrace{F_{10.7},F_{10.7A},K_p}_{\text{常数或文件}}\ \xrightarrow{\text{GetInputs}}\ f107,f107a,ap[7]\ \xrightarrow{\text{模型}}\ \rho(\vec r,t)\ \xrightarrow{\text{ADSF}}\ \rho_{used}\ \xrightarrow{\text{DragForce}}\ \vec a_{drag}$$

- **代码位置**：`src/base/forcemodel/DragForce.cpp:1441`（`GetDensity`）、`:3319`（`atmos->Density`）、`:3361`（ADSF 应用）；各模型 Density 入口见 3.5~3.12。

- **深度讲解**：
  **实现细节**（`DragForce.cpp:3300-3311, 3319, 3361`）：

  ```cpp
  // 3300: if (sun && centralBody) {
  // 3306:    sunLoc[0] = sunV[0]; ...  // 每步刷新太阳/中心体位置（JR 的 sunVector 输入）
  // 3319: atmos->Density(state, density, when, count);  // 虚函数分发到具体模型
  // 3360: for (Integer i = 0; i < count && i < atmosDensityScaleFactor.size(); ++i)
  // 3361:    density[i] *= atmosDensityScaleFactor[i];  // 乘密度标度（2.5）
  ```
  逐行解释：`DragForce::GetDensity`（`:3281-3364`）是阻力与大气模型之间的唯一接口，同时负责 NaN/Inf 检查（`:3339-3357`）与 ADSF 应用；`sunLoc/cbLoc` 经 `SetSunVector/SetCentralBodyVector`（`AtmosphereModel.cpp:377-394`）注入模型，JR 用 `sunVector` 求太阳赤纬（3.7）。各模型统一输出 kg/m³，因此 `DragForce` 的预因子只出现一次 $1000$ 换算（2.4）。`GetDerivativesForSpacecraft` 版本（`:1978-1983`）同样 `dens *= adsf`，供 `FMDensity` 等参数使用（[第14章](../CH14-plugins-b.md) 中 `NewParameterPlugin` 的 `FMDensity` 再乘 $10^9$ 输出 kg/km³）。

---

## 四、SolarRadiationPressure：太阳光压

### 4.1 SRP 主公式（球形模型）

- **公式**（Montenbruck & Gill eq. 3.75，代码注释）：
  $$\vec a_{srp} = \nu\,C_r\,\frac{F}{c}\,\frac{A}{m}\left(\frac{r_0}{r}\right)^2 \hat s$$
  其中 $\nu$ 为受照百分比（全影 0、全照 1、半影 $(0,1)$），$C_r$ 为反射系数，$F/c$ 为光压（$F$ 太阳通量 W/m²，$c$ 光速），$A$ 受光面积（m²），$r_0$=1 AU，$r$ 为日心距，$\hat s$ 为**太阳→航天器**单位向量。

- **代码位置**：`src/base/forcemodel/SolarRadiationPressure.cpp:1050`（M&G 引注）、`:1067-1068, 1076-1077, 1082-1084`（实现）；每航天器版 `:2166-2168`。

- **深度讲解**：
  **物理背景**：光子动量 $\hbar k$ 撞击航天器产生压力，完全吸收时动量传递 $p=F/c$，反射时加倍；$C_r$（0~2，典型 1.0~1.5）折中吸收/镜面/漫反射比例。1 AU 处 $F/c \approx 4.56\times10^{-6}$ N/m²，LEO 典型面质比 $A/m\sim10^{-2}$ m²/kg 时产生 $\sim5\times10^{-11}$ km/s² 量级加速度（太阳帆级别 $A/m\sim1$ 时约 $5\times10^{-9}$ km/s²），量级虽小但长期连续作用，造成显著的轨道偏心率漂移。方向取"从太阳指向航天器"（`forceVector`），与 PointMassForce 的"航天器指向太阳"相反（[第6章](../CH06-dynamics.md) 2.1.6 已注明）。
  **实现细节**（`SolarRadiationPressure.cpp:1067-1068, 1076-1077, 1082-1084`）：

  ```cpp
  // 1067: mag = percentSun * fluxPressure * distancefactor /
  // 1068:                     mass[i];                // (N/m²)/kg = 1/(m·s²)
  // 1076: mag *= cr[i] * area[i];                    // × Cr·A(m²) → m/s²
  // 1077: mag = mag*GmatMathConstants::M_TO_KM;      // m/s² → km/s²（M_TO_KM=0.001）
  // 1082: deriv[i6 + 3] = mag * forceVector[0];      // a_x = mag·ŝ
  // 1083: deriv[i6 + 4] = mag * forceVector[1];
  // 1084: deriv[i6 + 5] = mag * forceVector[2];
  ```
  逐行解释：`percentSun` 来自地影判定（4.4~4.6）；`fluxPressure = flux/c`（构造 `:160`，见 4.2）；`distancefactor = (r₀/r)²`（`:1005-1006`）；全影时 `percentSun=0` 直接写零导数（`:1181-1185`）。

### 4.2 太阳通量与光压

- **公式**：
  $$P = \frac{F}{c},\qquad F = 1367\ \text{W/m}^2\ (\text{IERS 1996}),\qquad P \approx 4.56\times10^{-6}\ \text{N/m}^2$$

- **代码位置**：`src/base/forcemodel/SolarRadiationPressure.cpp:159-160`（构造）；`SetRealParameter` 联动 `:492-493, 509-510`；边界 `:127-132`。

- **深度讲解**：
  **物理背景**：1367 W/m² 是 IERS 1996 太阳常数（地日平均距离处辐照度）；除以光速得动量通量即辐射压。GMAT 允许用户覆盖通量或直接给光压，两者自动互算（`flux = fluxPressure * c`，`:510`），并做合理性校验（通量限 $1200<F<1450$ W/m²、光压限 $4.33\times10^{-6}<P<4.84\times10^{-6}$ N/m²、标称距离限 $135\times10^6<r_0<165\times10^6$ km，`:127-132`）。
  **实现细节**（`SolarRadiationPressure.cpp:159-160`）：

  ```cpp
  // 159: flux         (1367.0),              // W/m², IERS 1996
  // 160: fluxPressure (flux / GmatPhysicalConstants::c),  // 转 N/m²
  ```
  逐行解释：`GmatPhysicalConstants::c = 299792458` m/s；校验在 `SetRealParameter(FLUX)`/`(FLUX_PRESSURE)` 中执行（`:479-511`），越界抛 `ODEModelException`。`nominalSun = 149597870.691` km（`:163-164`）即 1 AU 的 IAU 定义值，`sunDistance` 初始同值。

### 4.3 距离因子与方向向量

- **公式**：
  $$\hat s = \frac{\vec r_{sc}-\vec r_\odot}{|\vec r_{sc}-\vec r_\odot|},\qquad
    \left(\frac{r_0}{r}\right)^2 = \left(\frac{149597870.691\ \text{km}}{r}\right)^2$$

- **代码位置**：`src/base/forcemodel/SolarRadiationPressure.cpp:993-1003`（sunSat 与单位向量）、`:1005-1006`（平方反比）。

- **深度讲解**：
  **实现细节**（`SolarRadiationPressure.cpp:993-1006`）：

  ```cpp
  // 993: sunSat[0] = state[ i6 ] - cbSunVector[0];   // 太阳→航天器 = r_sc − r_sun
  // 996: sunDistance = sqrt(sunSat[0]*sunSat[0] + ...);
  // 998: if (sunDistance == 0.0) sunDistance = 1.0;  // 除零保护
  // 1001: forceVector[0] = sunSat[0] / sunDistance;  // 单位向量 ŝ
  // 1005: distancefactor = nominalSun / sunDistance; // (r₀/r)
  // 1006: distancefactor *= distancefactor;          // (r₀/r)²
  ```
  逐行解释：`cbSunVector = sun − centralBody` 在 `:951-954` 计算（中心体为太阳时置零，`:955-960`）；状态 `state[i6..i6+2]` 是中心体 MJ2000Eq 位置，故 `sunSat` 即航天器相对太阳的位置。火星/小行星任务中 $r$ 偏离 1 AU 较多，平方反比因子不可省略。

### 4.4 地影判定总控（GetShadowStateFromAllBodies）

- **公式**（组合规则）：
  $$\nu = \min_k \nu_k\quad(\text{任一全影}\Rightarrow\nu=0)；\qquad\text{两个半影体}:\ \nu = \nu_a + \nu_b - 1\ (\text{若日面不重叠})$$

- **代码位置**：`src/base/forcemodel/SolarRadiationPressure.cpp:3208-3408`（`GetShadowStateFromAllBodies`）；`modelShadows` 开关 `:3211-3212`；组合 `:3359-3397`。

- **深度讲解**：
  **阴影状态机（多体版）**：主循环 `GetDerivatives` 中，若 `modelShadows` 且 `sunRadius < sunDistance`（避免 `asin` 错误，`:1016`），调用本方法；它维护掩星体列表（中心体 + `ExtraShadowBodies`，去重、排除太阳，`:3219-3232`），对每个掩星体把状态平移至其坐标系（`:3278-3291`）后调用 `ShadowState::FindShadowState` 得 $\nu_k$（`:3320`）。**状态转移规则**：全影（$\nu=0$）立即短路返回（`:3327-3335`）；否则取最小 $\nu$；恰有两个半影体时按"日面不重叠→$\nu_a+\nu_b-1$"合并（`:3389-3396`，GMT-6543 规范）。`lastPercentSunEpoch`/`shadowBodiesNeedsUpdate` 缓存避免重复构建列表（`:3215-3232`）。关闭 `modelShadows` 时恒返回 1.0（`:3211-3212`）。

### 4.5 ShadowState：锥形/圆柱地影几何

- **公式**（锥形，Montenbruck & Gill §3.4.2）：
  $$a = \arcsin\frac{R_\odot}{d_{s}},\qquad b = \arcsin\frac{R_b}{d_{b}},\qquad
    c = \arccos\!\left(-\hat u_{b\to s}\cdot\hat u_{s\to\odot}\right)$$
  $$\text{状态判定:}\ \begin{cases}
    a+b\le c & \Rightarrow \nu=1\ (\text{全照})\\
    c < b-a & \Rightarrow \nu=0\ (\text{本影 umbra})\\
    |a-b|<c<a+b & \Rightarrow \text{半影 penumbra}\ (\nu\in(0,1), \text{见 4.6})\\
    \text{其余} & \Rightarrow \text{环食 anteumbra}:\ \nu = 1-\frac{b^2}{a^2}
  \end{cases}$$
  圆柱模型判据（旧实现，现注释保留）：$\nu=0 \iff |\vec r_\perp| < R_b$，其中 $\vec r_\perp = \vec r - (\vec r\cdot\hat u_\odot)\hat u_\odot$。

- **代码位置**：`src/base/solarsys/ShadowState.cpp:131-234`（`FindShadowState`；视半径 `:183-185`、夹角 `:198-199`、判定 `:201-232`）；圆柱判据注释于 `src/base/forcemodel/SolarRadiationPressure.cpp:2310-2332`。

- **深度讲解**：
  **阴影状态机（单体版）**：入口先做快速排除——$\vec r\cdot\hat u_{sun}>0$（航天器在太阳一侧）直接全照（`:145-153`）；`bodyRad ≥ d_b`（在行星内部）直接全影（`:176-180`）；`sunRad ≥ d_s`（"贴脸"太阳）全照（`:170-174`）。随后以**视半径**（apparent radius）$a,b$ 与**视夹角** $c$ 判定三态：$c$ 是航天器视角下太阳中心与掩星体中心张角。物理上 $a+b\le c$ 意味着两个视圆盘分离（全照），$c<b-a$ 意味着掩星体盘完全盖住太阳盘（本影），$|a-b|<c<a+b$ 为部分重叠（半影），两者都不满足（$c<|a-b|$ 且 $b<a$ 的"太阳大掩星体小"情形）为环食（antumbra/annular），此时日面被掩面积占比 $b^2/a^2$，故 $\nu=1-b^2/a^2$（`:230`）。圆柱模型把太阳当平行光源，判据只有"垂直距离 < 体半径"二元态，精度低、无半影，故现行实现只用锥形（`ShadowModel` 枚举 `CYLINDRICAL_MODEL=1/CONICAL_MODEL=2` 见 `SolarRadiationPressure.hpp:174-179`，实际代码路径恒走锥形）。

### 4.6 半影受照百分比（M&G eq. 3.87–3.94）

- **公式**（圆盘重叠面积法）：
  $$x = \frac{c^2+a^2-b^2}{2c},\qquad y=\sqrt{a^2-x^2}$$
  $$A_{overlap} = a^2\arccos\!\frac{x}{a} + b^2\arccos\!\frac{c-x}{b} - c\,y,\qquad
    \nu = 1-\frac{A_{overlap}}{\pi a^2}$$

- **代码位置**：`src/base/solarsys/ShadowState.cpp:259-289`（`GetPercentSunInPenumbra`；c `:267-269`、x `:275`、y `:280`、面积 `:283-285`、返回 `:288`）。

- **深度讲解**：
  **物理背景**：半影中太阳盘被掩星体盘部分遮挡，$\nu$ 取"未遮挡日面面积占比"。两圆交叠面积由两段扇形减三角形给出（上式即 M&G eq. 3.92），归一化到太阳盘面积 $\pi a^2$。$c,x,y$ 均为弧度制视量。
  **实现细节**（`ShadowState.cpp:283-288`）：

  ```cpp
  // 283: Real area = a2*acos(x/psunrad) +          // 太阳侧扇形 a²·acos(x/a)
  // 284:             b2*acos((c-x)/pcbrad)         // 掩星体侧扇形 b²·acos((c−x)/b)
  // 285:             - c*y;                          // 减三角形 c·y
  // 288: return 1.0 - area / (GmatMathConstants::PI * a2);  // ν = 1 − A/(πa²)
  ```
  逐行解释：`psunrad/pcbrad` 是 4.5 的视半径 $a,b$（`:218-219` 由 `asin` 重算）；`c` 用航天器位置与日向单位向量点积的反余弦（`:267-269`，与 4.5 的 $c$ 同源）。该百分比同时被 SRP 力与太阳电源功率（`SolarPowerSystem`）复用（[第6章](../CH06-dynamics.md) 2.2.7）。

### 4.7 SPAD SRP 模型

- **公式**：
  $$\vec a = \nu\,\frac{F}{c}\left(\frac{r_0}{r}\right)^2\frac{1}{m}\,\vec A_{SPAD},\qquad
    \vec A_{SPAD} = \text{SF}_{SPAD}\,(1+\varepsilon_{Cr})\,A_{file}(\hat s_{body})$$
  其中 $\vec A_{SPAD}$ 由 SPAD 文件按体固系日向插值得到的面元面积向量（m²），乘 SPAD 缩放因子与 Cr 估计因子后转回惯性系。

- **代码位置**：`src/base/forcemodel/SolarRadiationPressure.cpp:1094-1118`（主循环）、`:2460-2521`（`ComputeSPADAcceleration`，A 矩阵用）；面积源 `src/base/spacecraft/Spacecraft.cpp:2722-2781`（`GetSPADSRPArea`）。

- **深度讲解**：
  **物理背景**：与球形模型同构，但标量 $C_r A$ 换成姿态相关的向量面积——光压面积随太阳相对航天器的方向变化（太阳能帆板、非对称外形）。`AttitudeAffectsDynamics()` 返回 true（`SolarRadiationPressure.cpp:2833-2840`），姿态进状态向量。
  **实现细节**（`SolarRadiationPressure.cpp:1116-1118`）：

  ```cpp
  // 1107: Rvector3 sunSC(sunSat[0], sunSat[1], sunSat[2]);  // 日→航天器向量
  // 1108: spadArea = ((Spacecraft*) scObjs.at(i))->GetSPADSRPArea(ep, sunSC);
  // 1116: deriv[i6 + 3] = mag * spadArea[0] * GmatMathConstants::M_TO_KM;  // mag 单位 (Km/s²)/m²
  // 1117: deriv[i6 + 4] = mag * spadArea[1] * GmatMathConstants::M_TO_KM;
  // 1118: deriv[i6 + 5] = mag * spadArea[2] * GmatMathConstants::M_TO_KM;
  ```
  逐行解释：`mag = ν·P·(r₀/r)²/m`（`:1067-1068`），面积在文件读取处已含 `spadSRPScaleFactor·(1+crEpsilon)`（`Spacecraft.cpp:2773`）——与 2.5 的估计框架一致，Cr 估计走 `crEpsilon`；`M_TO_KM` 在此处把 $(Km/s²)/m²\cdot m²$ 归一。A 矩阵用位置三点扰动的 `ComputeSPADAcceleration` 数值差分（`:1326-1398`，扰动 $\Delta = |r|\times10^{-4}$，`:1338-1340`）。

### 4.8 N-Plate 模型：镜面 + 漫反射反射向量

- **公式**（每板反射向量，Plate::GetReflectanceI，SRP N-Plates MathSpec Eq.20/25/26/27）：
  $$\vec R_k = A_k\,C_k\,D_k\qquad(D_k>0\ \text{时})$$
  $$A_k = a_k\,S_k\,\ell_k,\qquad D_k = \hat s\cdot\hat n_k,\qquad
    \vec C_k = (1-\rho_k)\,\hat s + 2\left(\frac{\delta_k}{3}+\rho_k D_k\right)\hat n_k$$
  $$\vec a = -\nu\,\frac{F}{c}\left(\frac{r_0}{r}\right)^2\frac{1}{m}\sum_k \vec R_k$$
  其中 $\rho_k$=镜面反射率（SpecularFraction）、$\delta_k$=漫反射率（DiffuseFraction）、$a_k$=面积系数、$S_k$=板面积、$\ell_k$=光照比例、$\hat n_k$=板法向（体固/日向/文件三种类型）。

- **代码位置**：`src/base/spacecraft/Plate.cpp:1203-1211`（A/C/D/R）；总反射向量 `src/base/spacecraft/Spacecraft.cpp:2550-2558`（逐板求和）；加速度应用 `src/base/forcemodel/SolarRadiationPressure.cpp:1162-1165`（`(-mag)·scReflectance`，Eq.1 N-Plates MathSpec）；`mag` 定义 `:1067-1068`。

- **深度讲解**：
  **物理背景**：把航天器建模为 $N$ 个平板，每板把入射光子按三通道分配：吸收 $(1-\rho-\delta)$、镜面反射 $\rho$、漫反射 $\delta$。镜面反射沿法向弹回（贡献 $2\rho D\,\hat n$），漫反射按朗伯余弦分布（等效 $(2\delta/3)\hat n$，1/3 因子来自半球积分），吸收只贡献 $-\hat s$ 冲量。$D=\hat s\cdot\hat n<0$ 时背光板不受力（`Plate.cpp:1210-1211` 的 `D > EPSILON` 门控）。反射向量 $\vec R$ 单位是 m²，故 SRP 处用负号乘 `mag`（$(Km/s²)/m²$），因为 $\vec R$ 方向与光压推力相反（`SolarRadiationPressure.cpp:1162` 注释明示）。
  **实现细节**（`Plate.cpp:1203-1211`）：

  ```cpp
  // 1203: Real A = areaCoeff * plateArea * litFrac;      // 有效面积
  // 1204: Real rho = specularFrac;                        // 镜面份额
  // 1205: Real delta = diffuseFrac;                       // 漫射份额（1−ρ−δ 为吸收）
  // 1207: Real D = sHatI * nHatI;                         // Eq.25: cos 入射角
  // 1208: Rvector3 C = (1.0 - rho)*sHatI + 2.0 * (delta / 3.0 + rho * D)*nHatI; // Eq.26
  // 1210: if (D > EPSILON)
  // 1211:    reflectance = A * C*D;                       // Eq.20/27: R = A·C·D
  ```
  逐行解释：法向 $\hat n$ 按板类型取——`FixedInBody` 用体固常数（`Plate.cpp:1189-1190`）、`SunFacing` 直接指向太阳（`:1191-1192`）、`File` 由 N-Plate 历史文件按时插值（`:1193-1196`）；`Spacecraft::GetNPlateSRPReflectance`（`Spacecraft.cpp:2534-2564`）先把日向转成单位向量 $\hat s$、逐板累加（`:2551-2558`）。**与姿态的耦合**：体固法向经姿态矩阵 $\mathbf M_T$ 转到惯性系（`Plate.cpp:1190`），姿态变化直接改变 $\vec R$，故 `AttitudeAffectsDynamics()=true`。

### 4.9 N-Plate 的 A 矩阵（dF/dX = dK/dX·A + K·dA/dX）

- **公式**：
  $$K = -\nu\,\frac{F}{c}\left(\frac{r_0}{r}\right)^2\frac{1}{m},\qquad
    \frac{\partial K}{\partial \vec r} = \frac{2K}{r^2}\,\hat r_{s\to sc},\qquad
    \frac{\partial \vec a}{\partial X} = \frac{\partial K}{\partial X}\vec R + K\frac{\partial \vec R}{\partial X}$$

- **代码位置**：`src/base/forcemodel/SolarRadiationPressure.cpp:1431-1433`（K）、`:1444-1450`（dK/dX）、`:1483-1488`（乘积法则）；$\partial\vec R/\partial X$ 来自 `Spacecraft::GetNPlateSRPReflectanceDerivative`（`Spacecraft.cpp:2603-2629`）与 `Plate::GetReflectanceDerivativeI`（`Plate.cpp:1314-1362`）。

- **深度讲解**：
  **实现细节**（`SolarRadiationPressure.cpp:1446-1450, 1484`）：

  ```cpp
  // 1446: Real term = 2.0 * K / (sunDistance * sunDistance); // 2K/r²
  // 1447: Rvector3 rs(-sunSat[0], -sunSat[1], -sunSat[2]);    // 航天器→太阳单位向量·r
  // 1448: dKdX[0] = term * rs[0];  ...                       // dK/dr = (2K/r²)r̂·r
  // 1484: vec = dKdX[col] * A + K * dAdX[col];               // dF/dX = dK/dX·A + K·dA/dX
  // 1485: aTilde[ix0 + col] = vec[0];  ...                   // 填 A 矩阵第 4~6 行
  ```
  逐行解释：$K\propto r^{-2}$，故 $\partial K/\partial\vec r = -2K\vec r/r^3 = (2K/r^2)\,\hat r_{s\to sc}$；$\partial\vec R/\partial X$ 由航天器姿态导数（`GetAttitudeRotationMatrixDerivative`）链式展开，列数可超过 6（含估计参数），A 矩阵按需扩容（`:1453-1478`）。$\partial K/\partial v=0$、$\partial K/\partial C_p=0$（`:1444-1445`）。

### 4.10 SRP 的球形解析 A 矩阵与时间雅可比

- **公式**（球形模型位置子块，$\vec s = \vec r_{sc}-\vec r_\odot$）：
  $$\frac{\partial \vec a}{\partial \vec r} = C_s\left(\mathbf I_3 - 3\,\frac{\vec s\,\vec s^T}{s^2}\right),\qquad
    C_s = \nu\,C_r\,P\,\frac{A}{m}\left(\frac{r_0}{r}\right)^2\frac{1}{r}$$
  时间雅可比：$\dfrac{\partial \vec a}{\partial t} = \nu\,C_e\left(\mathbf I_3-3\hat s\hat s^T\right)(-\dot{\vec r}_\odot)/1000 + C_e\,\vec s\,(-\dot\nu)/10^5$，$C_e = P\,r_0^2\,C_r A/(m r^3)$，$\dot\nu$ 为半影百分比时间导数。

- **代码位置**：`src/base/forcemodel/SolarRadiationPressure.cpp:1285-1287`（Cs）、`:1293-1317`（子块填充）；时间雅可比 `:1975-1976`（Ce）、`:1989-2002`（填充）。

- **深度讲解**：
  **物理背景**：$\partial a_i/\partial r_j = \partial(\kappa s_i/s^3)/\partial r_j$ 直接微分即 $\kappa/s^3(\delta_{ij}-3s_is_j/s^2)$，是 SRP 对 STM 的解析贡献；注意此处**不包含 $\partial\nu/\partial r$**（半影梯度被忽略，代码在 `:1192-1202` 打印警告"STM does not currently contain SRP contributions from shadow partial derivatives"）。时间雅可比补充太阳相对运动 $-\dot r_\odot$ 与半影百分比变化率 $\dot\nu$ 两项。
  **实现细节**（`SolarRadiationPressure.cpp:1285-1287, 1293-1295`）：

  ```cpp
  // 1285: mag = percentSun * cr[i] * fluxPressure * area[i] * distancefactor /
  // 1286:       (mass[i] * sunDistance);            // Cs = ν·Cr·P·A·(r₀/r)²/(m·r)
  // 1287: mag = mag*GmatMathConstants::M_TO_KM;    // → 1/s²
  // 1293: aTilde[ix]     = mag * (1.0 - 3.0 * sunSat[0]*sunSat[0] / sSquared); // δ₁₁−3s₁²/s²
  // 1294: aTilde[ix + 1] = mag * (    - 3.0 * sunSat[0]*sunSat[1] / sSquared);
  // 1295: aTilde[ix + 2] = mag * (    - 3.0 * sunSat[0]*sunSat[2] / sSquared);
  ```
  逐行解释：`sSquared = s²`（`:1289`）；三个行（4~6）分别对 $s_x,s_y,s_z$ 微分（`:1293-1317`）；Cr 估计列取 $\partial a/\partial\varepsilon = a/(1+\varepsilon)$（`:1300`）。SPAD 的 A 矩阵用数值差分（`:1326-1398`，见 4.7），N-Plate 用 4.9 的解析式。时间雅可比的半影项 `dpdt` 来自 4.11 的完整导数链（`:1846-1970`）。

### 4.11 半影百分比时间导数 dp/dt

- **公式**（日面重叠面积的完整链式导数；全影/全照时 $\dot\nu=0$）：
  $$\dot\nu = \frac{100}{\pi a^2}\left(\dot A_{ov} - \frac{2 A_{ov}}{a}\dot a\right)\quad(\text{半影})，\qquad
    \dot\nu = 100\left(\frac{2b}{a^2}\dot b - \frac{2b^2}{a^3}\dot a\right)\quad(\text{环食})$$
  其中 $a,b,c$ 视半径/视夹角及其时间导数由 $\dot{\vec r}_\odot,\dot{\vec r}_{occ}$ 与几何关系解析展开（$\dot a = -\frac{R_\odot}{d_s^2\sqrt{1-(R_\odot/d_s)^2}}\,\hat r_{s\to sc}\cdot\dot{\vec r}_\odot$ 等）。

- **代码位置**：`src/base/forcemodel/SolarRadiationPressure.cpp:1846-1870`（视量及 $\dot a,\dot b,\dot c$）、`:1877-1960`（半影重叠面积导数）、`:1964-1969`（环食导数）。

- **深度讲解**：
  **实现细节**（`SolarRadiationPressure.cpp:1855-1858, 1958-1960`）：

  ```cpp
  // 1855: Real dAppSunRaddt = -sunRadius / (pow(scToSunVecMag, 3) *
  // 1856:    sqrt(1 - pow(sunRadius, 2) / pow(scToSunVecMag, 2))) *
  // 1857:    (scToSunVec[0] * cbSunVelVec[0] + ...);   // da/dt：太阳视半径变化率
  // 1958: dpdt = 100.0 / GmatMathConstants::PI * (1.0 / pow(appSunRad, 2) *
  // 1959:    dAreadt - 2.0 * overlapA / (pow(appSunRad, 3)) * dAppSunRaddt);
  ```
  逐行解释：`cbSunVelVec = v_sun − v_cb`（`:1820-1822`），掩星体速度取 0（当前假设掩星体=中心体，`:1837-1840`）；`dAppSunRaddt` 是视半径 $a=\arcsin(R_\odot/d_s)$ 对时间的导数，`dAppBodyRaddt` 同理（`:1861-1864`）；`overlapA` 是 4.6 的重叠面积（`:1882-1885`），`dAreadt` 经 c₁/c₂/反三角函数的完整链式求导（`:1928-1955`）。$\dot\nu$ 供 4.10 的时间雅可比使用（`:2001-2002`）。

### 4.12 SRP 力矩（N-Plate，姿态耦合）

- **公式**（每板，`GetTorquesForSpacecraft`）：
  $$\vec T_k = \vec r_k \times \vec F_k,\qquad
    \vec F_k = \nu\,\frac{F}{c}\,A_k\,D_k\left(\frac{r_0}{r}\right)^2\,\vec f_k$$
  $$\vec f_k = -2\rho_k D_k\,\hat n_k - \delta_k\left(\tfrac{2}{3}\hat n_k + \hat s\right) - (1-\rho_k-\delta_k)\,\hat s$$
  其中 $\vec r_k = \vec p_k - \vec r_{CM}$ 为板心相对质心位置，$D_k=\hat n_k\cdot\hat s<0$ 才计力。

- **代码位置**：`src/base/forcemodel/SolarRadiationPressure.cpp:3081-3086`（板参数与 $C_a=1-\rho-\delta$）、`:3147-3148`（力方向）、`:3164-3167`（力大小）、`:3174-3175`（力矩累加）。

- **深度讲解**：
  **物理背景**：光压力矩是航天器姿态扰动的主要来源之一（太阳能帆板不对称）。每板的光压冲量分解为镜面 $(-2\rho D\,\hat n)$、漫射 $(-\delta(\tfrac23\hat n+\hat s))$、吸收 $(-C_a\hat s)$ 三部分（与 4.8 的反射向量同源，符号相反），力矩为板心相对质心位置叉乘该力。背光板（$D>0$）跳过（`:3133-3134`）。姿态矩阵把日向与法向转到体固系计算 $D$（`:3119`），体现"姿态影响力矩、力矩反馈姿态"的双向耦合。
  **实现细节**（`SolarRadiationPressure.cpp:3147-3148, 3164-3167, 3175`）：

  ```cpp
  // 3147: Rvector3 forceDir = -2.0 * plateCRs * normDotSunToSC * plateNorm -
  // 3148:    plateCRd * ((2.0/3.0) * plateNorm + sunToSCUnitBF) - plateCa * sunToSCUnitBF;
  // 3164: Rvector3 srpForce = (percentSun * (flux / speedOfLight) * plateArea *
  // 3165:                      (plateNorm * sunToSCUnitBF) *
  // 3166:                      pow((nominalSun / sunDistance), 2.0) ) * forceDir;
  // 3175: torque += Cross(cmPosToPlatePos, srpForce);   // T = r × F
  ```
  逐行解释：`plateCRs/plateCRd/plateCa` 即 $\rho,\delta,1-\rho-\delta$（`:3084-3086`）；`normDotSunToSC = D`；力大小含 $\nu$、$F/c$、面积、$D$ 与 $(r_0/r)^2$（`:3164-3167`）；`PlateX/Y/Z` 为板心坐标（`:3171-3173`），`sc->GetSystemCM()` 为质心（`:3071`）。

---

## 五、RelativisticCorrection：后牛顿相对论修正

### 5.1 Schwarzschild 项（中心体 1PN）

- **公式**：
  $$\vec a_{Schw} = \frac{\mu}{c^2 r^3}\left[\left(\frac{4\mu}{r}-v^2\right)\vec r + 4(\vec r\cdot\vec v)\,\vec v\right]$$
  其中 $\mu$ 为中心体引力常数，$c=299792.458$ km/s（`SPEED_OF_LIGHT_VACUUM × M_TO_KM`），$\vec r,\vec v$ 为航天器相对中心体状态。

- **代码位置**：`src/base/forcemodel/RelativisticCorrection.cpp:245`（c 换算）、`:346-359`（实现；s1 `:348`、s2 `:349-352`、s3 `:353-356`、求和 `:357-359`）。

- **深度讲解**：
  **物理背景**：这是 Schwarzschild 度规下相对论质点运动的 1PN（一阶后牛顿）加速度，包含引力对时间膨胀、空间弯曲与速度依赖的全部一阶效应；它使近日点进动、引力时间延迟等效应进入轨道积分。对地球 LEO 量级约 $10^{-9}$ km/s²，但对**近日航天器**（如太阳轨道任务）不可忽略。
  **实现细节**（`RelativisticCorrection.cpp:348-359`）：

  ```cpp
  // 348: s1 = bodyMu / (c * c * r * r * r);       // μ/(c²r³)
  // 349: s2_1 = (4.0 * bodyMu / r) - (v * v);     // 4μ/r − v²
  // 350: s2[0] = s2_1 * rv[0];                    // (4μ/r − v²)·r
  // 353: rvDotvvX4 = 4.0 * (rv[0]*vv[0] + ...);   // 4(r·v)
  // 354: s3[0] = rvDotvvX4 * vv[0];               // 4(r·v)·v
  // 357: schwarzschild[0] = s1 * (s2[0] + s3[0]); // μ/(c²r³)·[(4μ/r−v²)r + 4(r·v)v]
  ```
  逐行解释：`r = |r|`、`v = |v|`（`:346-347`）；`bodyMu` 在每次调用从中心体取（`:247`）；全部在 km 单位下计算，$c$ 已换算为 km/s（`:245`）。

### 5.2 测地线（geodesic）项

- **公式**：
  $$\vec a_{geo} = 2\,\vec\Omega \times \vec v_{sc},\qquad
    \vec\Omega = \frac{3}{2}\,\vec v_b \times \left(-\frac{\mu_\odot}{c^2 r_b^3}\,\vec r_b\right)$$
  其中 $\vec r_b,\vec v_b$ 是中心体相对太阳的位置/速度（MJ2000），$\mu_\odot$ 为太阳引力常数；中心体为太阳时该项置零。

- **代码位置**：`src/base/forcemodel/RelativisticCorrection.cpp:277-297`（$\vec r_b,\vec v_b$ 与 $\vec\Omega$；`muCBc2r3 :286`、叉积 `:295-297`）、`:362-374`（geodesic 计算与太阳特判）。

- **深度讲解**：
  **物理背景**：测地线进动（de Sitter 进动）——航天器随中心体绕太阳公转时，其自转/轨道参考系被太阳引力弯曲，等效于一个与公转角速度耦合的进动项 $2\Omega\times v$。这是 EIH（Einstein–Infeld–Hoffmann）方程组在"以中心体为原点"展开后的交叉项，只在地球等非太阳中心体时出现（太阳中心时轨道参考系即日心系，该项无意义，`:369-374` 置零）。
  **实现细节**（`RelativisticCorrection.cpp:286-297, 365-367`）：

  ```cpp
  // 286: muCBc2r3 = sunMu / (c * c * posMag * posMag * posMag); // μ_sun/(c²r_b³)
  // 291: pos[0] = -muCBc2r3 * posWRTSun[0];      // −μ_sun·r_b/(c²r_b³)
  // 288: vel[0] = threeOver2 * velWRTSun[0];     // (3/2)·v_b
  // 295: omega[0] = vel[1]*pos[2] - vel[2]*pos[1]; // Ω = (3/2)v_b × (−μ_sun r_b/(c²r_b³))
  // 365: geodesic[0] = 2.0 * (omega[1]*vv[2] - omega[2]*vv[1]); // 2Ω×v_sc
  ```
  逐行解释：`stateWRTSun = body MJ2000 − Sun MJ2000`（`:277`）给出 $\vec r_b,\vec v_b$；`posMag = |r_b|`（`:284`）；`Ω` 只随中心体公转变化，故在航天器循环**外**计算一次（`:270-307`），循环内直接复用。

### 5.3 Lense-Thirring 项（惯性系拖曳）

- **公式**：
  $$\vec a_{LT} = \frac{2\mu}{c^2 r^3}\left[\frac{3}{r^2}(\vec r\cdot\vec J)\,(\vec r\times\vec v) + \vec v\times\vec J\right],\qquad
    \vec J = \mathbf R\,\left(0,\ 0,\ \frac{2}{5}R_b^2\,\omega_b\right)^T$$
  其中 $\vec J$ 为中心体**比角动量**（单位质量角动量，$J/M=\tfrac25 R_b^2\omega$），$\mathbf R$ 为体固→惯性旋转矩阵，$R_b$ 为赤道半径，$\omega_b$ 为自转角速率。

- **代码位置**：`src/base/forcemodel/RelativisticCorrection.cpp:316-325`（自转轴/$\vec J$；`J1 :322`、旋转 `:323-325`）、`:377-388`（Lense-Thirring；`lt1 :383`、`lt2 :384`、累加 `:386-388`）。

- **深度讲解**：
  **物理背景**：旋转天体拖曳周围时空（frame dragging），使轨道平面产生进动；对地球 $J_2$ 级任务该项比 Schwarzschild 再小 ~2 个量级，主要见于高精度近地轨道与引力探测实验。
  **实现细节**（`RelativisticCorrection.cpp:322-325, 383-388`）：

  ```cpp
  // 322: J1[2] = (2.0 / 5.0) * bodyRadius * bodyRadius * bodySpinRate; // J/M = (2/5)R²ω
  // 323: J[0] = R(0,0)*J1[0] + R(0,1)*J1[1] + R(0,2)*J1[2];           // 旋转到惯性系
  // 383: lt1 = 2.0 * s1;                                  // 2μ/(c²r³)
  // 384: lt2 = (3.0 / (r * r)) * (rv[0]*J[0] + ...);      // 3(r·J)/r²
  // 386: lenseThirring[0] = lt1 * ((lt2 * rvCrossvv[0]) + vvCrossJ[0]); // 2μ/(c²r³)[3(r·J)/r²·(r×v) + v×J]
  ```
  逐行解释：`bodySpinRate` 由 $\mathbf R^T\dot{\mathbf R}$ 的反对称分量求模（`:316-319`）；`rvCrossvv = r×v`（`:377-379`）、`vvCrossJ = v×J`（`:380-382`）。

### 5.4 三项求和与导数输出

- **公式**：
  $$\vec a_{rel} = \vec a_{Schw} + \vec a_{geo} + \vec a_{LT}$$

- **代码位置**：`src/base/forcemodel/RelativisticCorrection.cpp:391-393`（求和）、`:404-422`（写入导数；order=1 时加速度进速度分量，order=2 时进位置分量）。

- **深度讲解**：
  **实现细节**（`RelativisticCorrection.cpp:391-393, 406-413`）：

  ```cpp
  // 391: ar[0] = schwarzschild[0] + geodesic[0] + lenseThirring[0]; // 三项线性叠加
  // 392: ar[1] = schwarzschild[1] + geodesic[1] + lenseThirring[1];
  // 393: ar[2] = schwarzschild[2] + geodesic[2] + lenseThirring[2];
  // 406: case 1:
  // 410:    deriv[3+nOffset] = ar[0];   // 一阶导数：加速度进速度槽
  // 411:    deriv[4+nOffset] = ar[1];
  // 412:    deriv[5+nOffset] = ar[2];
  ```
  逐行解释：三项均为 1PN 同阶、线性叠加（非线性高阶项忽略）；`order==2`（RKN）时把加速度写进位置槽（`:415-422`），与 Drag/SRP 的约定一致。STM/A 矩阵部分输出全零块（`:429-509`，相对论项对 STM 的解析贡献未实现）。模型要求 EOP 文件（`Initialize :184-185`）与中心体/太阳指针（`:187-209`），并创建 MJ2000Eq 与 BodyFixed 局部坐标系（`:214-217`）供 $\mathbf R,\dot{\mathbf R}$ 使用。

---

## 六、公式索引表

| 公式 | 文件:行 | 所属类 |
|---|---|---|
| $a = -\tfrac12(C_dA/m)\rho v_{rel}^2\hat v_{rel}$（主公式注释） | src/base/forcemodel/DragForce.cpp:1290-1292 | DragForce |
| $\text{prefactor} = -500\,C_dA/m$（含 kg/m³→kg/km³ 换算） | src/base/forcemodel/DragForce.cpp:1214-1217 | DragForce::BuildPrefactors |
| $\text{prefactor} = -500/m$（SPAD） | src/base/forcemodel/DragForce.cpp:1222 | DragForce::BuildPrefactors |
| $a_i = factor\cdot|v_{rel}|\cdot v_{rel,i}$ | src/base/forcemodel/DragForce.cpp:1513, 1525-1527 | DragForce::GetDerivatives |
| $\vec v_{rel} = \vec v - \vec\omega\times\vec R$ | src/base/forcemodel/DragForce.cpp:1501-1509 | DragForce::GetDerivatives |
| $\vec v_{rel} = \vec v - \vec w_{wind}$ | src/base/forcemodel/DragForce.cpp:1475-1483 | DragForce::GetDerivatives |
| $C_d = C_{d0}(1+\varepsilon)$ | src/base/forcemodel/DragForce.cpp:1343 | DragForce::GetDerivatives |
| $\dot\varepsilon = -\beta\varepsilon,\ \beta=\ln2/t_{1/2}$ | src/base/forcemodel/DragForce.cpp:1354, 1362 | DragForce（FOGM） |
| $\rho_{used} = \rho_{model}\cdot\text{ADSF}$ | src/base/forcemodel/DragForce.cpp:3361 | DragForce::GetDensity |
| $\partial a/\partial m = -a/m$ | src/base/forcemodel/DragForce.cpp:1909 | DragForce（质量雅可比） |
| A 矩阵有限差分（$\Delta r=10^{-2}$ km, $\Delta v=10^{-6}$ km/s） | src/base/forcemodel/DragForce.cpp:1706-1803 | DragForce::GetDerivatives |
| $A_p = e^{(K_p+1.6)/1.75}$（后备） | src/base/forcemodel/DragForce.cpp:3480 | DragForce::CalculateAp |
| 密度默认值 $4\times10^{-13}$ kg/m³ | src/base/forcemodel/DragForce.cpp:3294 | DragForce::GetDensity |
| $A_p$ 表查（Vallado 表 8-3） | src/base/solarsys/AtmosphereModel.cpp:646-738 | AtmosphereModel::ConvertKpToAp |
| $A_p = e^{(K_p+1.6)/1.75}$ | src/base/solarsys/AtmosphereModel.cpp:741-742 | AtmosphereModel::ConvertKpToAp |
| $28K_p+0.03e^{K_p} = A_p+100(1-e^{-0.08A_p})$（割线法） | src/base/solarsys/AtmosphereModel.cpp:745-772 | AtmosphereModel::ConvertKpToAp |
| $\omega_{Earth}=(0,0,7.29211585530\times10^{-5})$ rad/s | src/base/solarsys/AtmosphereModel.cpp:144-146 | AtmosphereModel |
| $\vec\omega = \mathbf R[\mathbf R^T\dot{\mathbf R}]_\times$ | src/base/solarsys/AtmosphereModel.cpp:512-529 | AtmosphereModel::BuildAngularVelocity |
| 大地纬度迭代 $\phi_{k+1}=\tan^{-1}((z+Ne^2\sin\phi)/r_{xy})$ | src/base/solarsys/AtmosphereModel.cpp:1564-1578 | AtmosphereModel::CalculateGeodetics |
| $h = r_{xy}/\cos\phi - N(\phi)$ | src/base/solarsys/AtmosphereModel.cpp:1576-1578 | AtmosphereModel::CalculateGeodetics |
| year/doy/sod 分解（`yd=year*1000+doy`） | src/base/solarsys/AtmosphereModel.cpp:1725-1742 | AtmosphereModel::GetInputs |
| $f_{107},f_{107a},ap[7]$ 历史/预测选择 | src/base/solarsys/AtmosphereModel.cpp:1803-1861 | AtmosphereModel::GetInputs |
| $\rho = \rho_0^{(k)}e^{-(h-h_0^{(k)})/H^{(k)}}$（28 带） | src/base/solarsys/ExponentialAtmosphere.cpp:490-495 | ExponentialAtmosphere::Density |
| 28 带常数（$\rho_0(0)=1.225$, $H=7.249$…） | src/base/solarsys/ExponentialAtmosphere.cpp:557-641 | ExponentialAtmosphere::SetConstants |
| 指数大气数据表（h₀,ρ₀,H） | application/data/atmosphere/earth/EarthExponentialAtmosphereData.txt:1-28 | （数据文件） |
| $\rho = \rho_0 e^{-(h-h_0)/H}$（单带） | src/base/solarsys/SimpleExponentialAtmosphere.cpp:160 | SimpleExponentialAtmosphere::Density |
| $T_{ex,0} = 379+3.24F_{10.7A}+1.3(F_{10.7}-F_{10.7A})$ | src/base/solarsys/JacchiaRobertsAtmosphere.cpp:546 | JacchiaRobertsAtmosphere::JacchiaRoberts |
| $T_\infty = T_1+14K_p+0.02e^{K_p}$（h<200 km） | src/base/solarsys/JacchiaRobertsAtmosphere.cpp:868-875 | JacchiaRobertsAtmosphere::exotherm |
| $T_x = 371.6678+0.0518806T_\infty-294.3505e^{-0.00216222T_\infty}$ | src/base/solarsys/JacchiaRobertsAtmosphere.cpp:877-878 | JacchiaRobertsAtmosphere::exotherm |
| $T(h)$ 低层多项式/高层指数外推 | src/base/solarsys/JacchiaRobertsAtmosphere.cpp:884-903 | JacchiaRobertsAtmosphere::exotherm |
| $k = -g_0/(R_g(T_x-T_0))$ | src/base/solarsys/JacchiaRobertsAtmosphere.cpp:1047 | JacchiaRobertsAtmosphere::rho_100 |
| $\rho_{100} = \rho_{90}T_{90}M\,e^{k(\ln f_1+f_2)}/(M_{90}T)$ | src/base/solarsys/JacchiaRobertsAtmosphere.cpp:1064-1065 | JacchiaRobertsAtmosphere::rho_100 |
| $\rho_{125} = \rho'\,T_{100}\sum_i M_iN_i e^{M_i k'(f_3+f_4)}/T$ | src/base/solarsys/JacchiaRobertsAtmosphere.cpp:1150-1162 | JacchiaRobertsAtmosphere::rho_125 |
| $\rho_{corr}=10^{g_{geo}+g_{sem}+g_{lat}}$ | src/base/solarsys/JacchiaRobertsAtmosphere.cpp:1186-1217 | JacchiaRobertsAtmosphere::rho_cor |
| $r_i = fM_id_i(T_x/T)^{1+\gamma}((T_\infty-T)/(T_\infty-T_x))^{\gamma}$ | src/base/solarsys/JacchiaRobertsAtmosphere.cpp:1298-1299 | JacchiaRobertsAtmosphere::rho_high |
| $\gamma = 35M_ig_0R_p^2(T_\infty-T_x)/(R_g L T_\infty(T_x-T_0)(R_p+125))$ | src/base/solarsys/JacchiaRobertsAtmosphere.cpp:1264-1265 | JacchiaRobertsAtmosphere::rho_high |
| $\rho = \rho_{gtd6}(\dots)\times1000$（cg/cm³→kg/m³） | src/base/solarsys/Msise90Atmosphere.cpp:295-299, 340 | Msise90Atmosphere::Density |
| $\rho = \rho_{gtd7}(\dots)\times1000$ | plugins/Msise00Plugin/src/base/atmosphere/NRLMsise00Atmosphere.cpp:284-285, 322 | NRLMsise00Atmosphere::Density |
| $a = \nu C_r(F/c)(A/m)(r_0/r)^2\hat s$（M&G 3.75） | src/base/forcemodel/SolarRadiationPressure.cpp:1067-1084 | SolarRadiationPressure::GetDerivatives |
| $P = F/c,\ F=1367$ W/m² | src/base/forcemodel/SolarRadiationPressure.cpp:159-160 | SolarRadiationPressure |
| $\hat s = (\vec r_{sc}-\vec r_\odot)/r$，$(r_0/r)^2$ | src/base/forcemodel/SolarRadiationPressure.cpp:993-1006 | SolarRadiationPressure::GetDerivatives |
| $\nu = \min\nu_k$；$\nu_a+\nu_b-1$ 合并 | src/base/forcemodel/SolarRadiationPressure.cpp:3320-3396 | SolarRadiationPressure::GetShadowStateFromAllBodies |
| $a=\arcsin(R_\odot/d_s), b=\arcsin(R_b/d_b), c=\arccos(-\hat u\cdot\hat u)$ | src/base/solarsys/ShadowState.cpp:183-199 | ShadowState::FindShadowState |
| 全照/本影/半影/环食状态机 | src/base/solarsys/ShadowState.cpp:201-232 | ShadowState::FindShadowState |
| 环食 $\nu=1-b^2/a^2$ | src/base/solarsys/ShadowState.cpp:230 | ShadowState::FindShadowState |
| $A_{ov}=a^2\arccos(x/a)+b^2\arccos((c-x)/b)-cy$，$\nu=1-A_{ov}/(\pi a^2)$ | src/base/solarsys/ShadowState.cpp:275-288 | ShadowState::GetPercentSunInPenumbra |
| $\vec a = \nu P(r_0/r)^2\vec A_{SPAD}/m$ | src/base/forcemodel/SolarRadiationPressure.cpp:1116-1118 | SolarRadiationPressure（SPAD） |
| $\vec R_k = A_kC_kD_k$，$\vec C_k=(1-\rho)\hat s+2(\delta/3+\rho D)\hat n$ | src/base/spacecraft/Plate.cpp:1203-1211 | Plate::GetReflectanceI |
| $\vec a = -\nu P(r_0/r)^2\sum_k\vec R_k/m$ | src/base/forcemodel/SolarRadiationPressure.cpp:1162-1165 | SolarRadiationPressure（N-Plate） |
| $\partial a/\partial r = C_s(\mathbf I-3\hat s\hat s^T)$ | src/base/forcemodel/SolarRadiationPressure.cpp:1285-1317 | SolarRadiationPressure（A 矩阵） |
| $dF/dX = dK/dX\cdot A + K\cdot dA/dX$ | src/base/forcemodel/SolarRadiationPressure.cpp:1446-1488 | SolarRadiationPressure（N-Plate A 矩阵） |
| $\dot\nu$（半影/环食时间导数） | src/base/forcemodel/SolarRadiationPressure.cpp:1846-1969 | SolarRadiationPressure（时间雅可比） |
| $\vec T_k = \vec r_k\times\vec F_k$，$\vec f_k=-2\rho D\hat n-\delta(\tfrac23\hat n+\hat s)-C_a\hat s$ | src/base/forcemodel/SolarRadiationPressure.cpp:3147-3175 | SolarRadiationPressure::GetTorquesForSpacecraft |
| $\vec a_{Schw} = \tfrac{\mu}{c^2r^3}[(4\mu/r-v^2)\vec r+4(\vec r\cdot\vec v)\vec v]$ | src/base/forcemodel/RelativisticCorrection.cpp:348-359 | RelativisticCorrection::GetDerivatives |
| $\vec a_{geo}=2\vec\Omega\times\vec v$，$\vec\Omega=\tfrac32\vec v_b\times(-\mu_\odot\vec r_b/(c^2r_b^3))$ | src/base/forcemodel/RelativisticCorrection.cpp:286-297, 365-367 | RelativisticCorrection::GetDerivatives |
| $\vec a_{LT}=\tfrac{2\mu}{c^2r^3}[\tfrac3{r^2}(\vec r\cdot\vec J)(\vec r\times\vec v)+\vec v\times\vec J]$ | src/base/forcemodel/RelativisticCorrection.cpp:383-388 | RelativisticCorrection::GetDerivatives |
| $\vec J=\mathbf R(0,0,\tfrac25R_b^2\omega_b)$ | src/base/forcemodel/RelativisticCorrection.cpp:316-325 | RelativisticCorrection::GetDerivatives |
| $\vec a_{rel}=\vec a_{Schw}+\vec a_{geo}+\vec a_{LT}$ | src/base/forcemodel/RelativisticCorrection.cpp:391-393 | RelativisticCorrection::GetDerivatives |
