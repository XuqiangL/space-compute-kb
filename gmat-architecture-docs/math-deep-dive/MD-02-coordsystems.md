# 第2章 坐标系与参考架旋转数学

本章把 GMAT 引擎里所有「旋转/定向公式」逐条从源码中提炼成数学形式：`src/base/coordsystem/`（76 个文件）里的轴系类、FK5 归算五件套、ITRF 的 IAU2000/2006 路线、ICRF↔FK5 转换；`src/base/solarsys/` 里 `Planet.cpp`/`CelestialBody.cpp`/`Moon.cpp`/`DeFile.cpp` 的天体定向（IAU 2000 α、δ、W 展开）；以及 `src/gmatutil/util/EopFile.cpp` 的极移/UT1-UTC/LOD 数据流。每个条目三要素：**公式**（从代码实现提炼，LaTeX）、**代码位置**（真实相对路径+行号）、**深度讲解**（天文背景、实现细节、旋转方向/序列约定、EOP 数据流向、使用场景）。轴系类的整体职责、参数表与继承关系见 [第8章 §8.5](../CH08-base-subsystems.md)，力模型如何消费这些旋转见 [第6章](../CH06-dynamics.md)，本章只讲数学本身，不重复架构叙述。

## 一、参考架与转换总框架

GMAT 里每个 `CoordinateSystem` = 原点（`SpacePoint* origin`）+ 轴系（`AxisSystem* axes`）。所有状态换算都归结为两段式（详见 [CH08 §8.5.1](../CH08-base-subsystems.md)）：

$$
\vec{x}_{\text{base}} = \underbrace{\mathrm{T}\big(\vec{r}_{\text{origin}}-\vec{r}_{J2000\,\text{body}}\big)}_{\text{平移：CoordinateSystem::TranslateToBaseSystem}}\Big(\underbrace{R_{\text{axes}}\, \vec{x}}_{\text{旋转：AxisSystem::RotateToBaseSystem}}\Big)
$$

两个关键约定贯穿全章，务必先建立：

1. **基系统（base system）**：每个轴系声明自己的 `baseSystem`，只取 `"FK5"`（= MJ2000Eq，J2000 平赤道）或 `"ICRF"` 二值（`AxisSystem.hpp:242-244`）。`MJ2000EqAxes`/`ICRFAxes` 是各自的"基系本身"，`rotMatrix` 恒等；其它轴系的 `CalculateRotationMatrix` 一律计算「本轴系 → 基系」的旋转。基系统不同（FK5↔ICRF）时由 `CoordinateConverter` 用 ICRF Euler 旋转向量补齐。
2. **旋转矩阵语义**：`rotMatrix` 是把**本轴系坐标旋转到基系坐标**的矩阵，`rotDotMatrix` 是它的时间导数。旋转 6 维状态时速度为
   $$
   \vec{v}_{\text{base}} = \dot{R}\,\vec{r} + R\,\vec{v}
   $$
   （`AxisSystem.cpp:1545-1558` `CompleteRotateToBase`）。反向 `RotateFromBaseSystem` 用转置 $R^\top$（`AxisSystem.cpp:1668-1688`）。

**时间尺标**：所有角度公式的输入都是 TT 近似的 TDB 儒略世纪 $t=\frac{\mathrm{MJD_{TT}}+(\mathrm{JD\_JAN\_5\_1941}-\mathrm{JD\_OF\_J2000})}{36525}$，其中 `JD_JAN_5_1941 = 2430000.0`、`JD_OF_J2000 = 2451545.0`（`src/gmatutil/util/GmatConstants.hpp:145,151`），即 GMAT 的 MJD 以 JD 2430000.0 为参考零点、J2000 处为 21545.0。恒星时与极移要用 UT1/UTC（来自 EopFile），于是有 EOP 数据流：`A1 → UTC（极移插值自变量）`、`A1 → UT1（GMST 自变量）`、`A1 → TT（岁差章动自变量）`，见 §十。

## 二、FK5 归算五件套（AxisSystem 基类）

`AxisSystem` 把经典 FK5/IAU-76/80 归算做成五个可复用方法（声明见 `AxisSystem.hpp:324-344`），供 `BodyFixedAxes`（地球分支）、`TODEq/TODEc`、`TEMEAxes`、`EquatorAxes`、`GSM`、`TOEEq/TOEEc` 等按需调用。产物是五个 3×3 矩阵 `PREC/NUT/ST/STderiv/PM`，带 `lastXxxEpoch` 缓存（`AxisSystem.hpp:266-291`），同一历元不重算。

### 2.1 岁差角多项式（IAU-76）

- **公式**：以儒略世纪 $t$ 计（$t=\frac{\mathrm{JD_{TT}}-2451545.0}{36525}$），IAU-76 岁差角（Vallado 式 3-56）：

$$
\begin{aligned}
\zeta &= (2306.2181\,t + 0.30188\,t^2 + 0.017998\,t^3)\ \text{arcsec} \\
\Theta &= (2004.3109\,t - 0.42665\,t^2 - 0.041833\,t^3)\ \text{arcsec} \\
z &= (2306.2181\,t + 1.09468\,t^2 + 0.018203\,t^3)\ \text{arcsec}
\end{aligned}
$$

- **代码位置**：`src/base/coordsystem/AxisSystem.cpp:2233-2242`（`AxisSystem::ComputePrecessionMatrix`）。
- **深度讲解**：
  - 天文背景：岁差是日月引力使地球自转轴在空间缓慢进动的长期项。IAU-76 采用 Laskar 拟合的 $\zeta,\Theta,z$ 三次多项式，把 J2000 平赤道转到**平赤道历元（MOD）**。GMAT 全程用 TT 近似 TDB（`BodyFixedAxes.cpp:613-616` 注释明示 "this is really TT, an approximation of TDB"），弧秒统一乘 `RAD_PER_ARCSEC` 转弧度。
  - 实现细节（`AxisSystem.cpp:2233-2242`）：

    ```cpp
    Real tTDB2 = tTDB * tTDB;                  // t²
    Real tTDB3 = tTDB2 * tTDB;                 // t³
    // 岁差角（Vallado 式 3-56），乘 RAD_PER_ARCSEC 转弧度
    Real zeta  = ( 2306.2181*tTDB + 0.30188*tTDB2 + 0.017998*tTDB3 ) *RAD_PER_ARCSEC;
    Real Theta = ( 2004.3109*tTDB - 0.42665*tTDB2 - 0.041833*tTDB3 ) *RAD_PER_ARCSEC;
    Real     z = ( 2306.2181*tTDB + 1.09468*tTDB2 + 0.018203*tTDB3 ) *RAD_PER_ARCSEC;
    ```

    第 2234 行先算 $t^2,t^3$；2237-2242 行按 Vallado 式 3-56 填三个角，系数单位是角秒/儒略世纪，`RAD_PER_ARCSEC = π/(180×3600)`。
  - 旋转约定：这三个角经 2.2 的 `PREC` 矩阵体现为序列 $R_3(-z)\,R_2(\Theta)\,R_3(-\zeta)$（先绕 Z 转 $-\zeta$，再绕新 Y 转 $\Theta$，再绕新 Z 转 $-z$），把 J2000 平赤道 → 平赤道历元。
  - 使用场景：凡需要"从 J2000 平赤道到某历元平赤道"的轴系（MODEq/MODEc/MOEEq/MOEEc/TODEq/TODEc/TEME/BodyFixed 地球分支）第一步都调它。

### 2.2 岁差矩阵 PREC

- **公式**（Vallado 式 3-57，J2000→MOD）：

$$
\mathrm{PREC}=
\begin{bmatrix}
\cos\Theta\cos z\cos\zeta-\sin z\sin\zeta &
-\sin\zeta\cos\Theta\cos z-\sin z\cos\zeta &
-\sin\Theta\cos z\\
\sin z\cos\Theta\cos\zeta+\sin\zeta\cos z &
-\sin z\sin\zeta\cos\Theta+\cos z\cos\zeta &
-\sin\Theta\sin z\\
\sin\Theta\cos\zeta & -\sin\Theta\sin\zeta & \cos\Theta
\end{bmatrix}
$$

- **代码位置**：`src/base/coordsystem/AxisSystem.cpp:2244-2262`（`AxisSystem::ComputePrecessionMatrix`）。
- **深度讲解**：
  - 实现细节（`AxisSystem.cpp:2254-2262`）：

    ```cpp
    PREC.Set( cosTheta*cosz*coszeta - sinz*sinzeta,          // 行0
             -sinzeta*cosTheta*cosz - sinz*coszeta,
             -sinTheta*cosz,
              sinz*cosTheta*coszeta + sinzeta*cosz,          // 行1
             -sinz*sinzeta*cosTheta + cosz*coszeta,
             -sinTheta*sinz,
              sinTheta*coszeta,                              // 行2
             -sinTheta*sinzeta,
              cosTheta);
    ```

    2245-2250 行先算 6 个三角函数；2254-2262 行按行填充。`Rmatrix33::Set` 按行主序接收 9 个元素。
  - 旋转方向：代码注释（2252 行）明确 "transformations from FK5 to MOD"——`PREC` 把 J2000 坐标转到平赤道历元坐标；因此**反向**（MOD→J2000）取 `PREC.Transpose()`，这正是 MODEq/MODEc 等轴系把 `precData` 行列转置后写入 `rotMatrix` 的原因（见 §7.1）。
  - 缓存：2266-2267 行存 `lastPREC/lastPRECEpoch`。
  - 使用场景：`MODEqAxes`、`MOEEqAxes`、`TOEEqAxes`、`BodyFixedAxes`（地球）等。

### 2.3 平黄赤交角 ε̄

- **公式**（Vallado 式 3-52）：

$$
\bar\varepsilon = (84381.448 - 46.8150\,t - 0.00059\,t^2 + 0.001813\,t^3)\ \text{arcsec}
$$

- **代码位置**：`src/base/coordsystem/AxisSystem.cpp:2379-2381`（`ComputeNutationMatrix` 内）；同式另见于 `TOEEcAxes.cpp:144-148`、`TODEcAxes.cpp:186-190`、`MODEcAxes.cpp:181-182`、`MOEEcAxes.cpp:139-140`。
- **深度讲解**：84381.448″ = 23°26′21.448″ 是 J2000 平黄赤交角；线性项 −46.8150″/世纪为主进动率，二次、三次项为长期漂移。`cosEpsbar` 通过引用参数传出（`AxisSystem.cpp:2381`），供章动矩阵与分点方程使用。TOEEc/TODEc/MODEc/MOEEc 需要黄道面时各自独立重算同一公式（代码重复而非复用，是历史沿革）。

### 2.4 章动基本角（IAU-1980/1996）

- **公式**（Vallado 式 3-54；角度取模 $2\pi$）：月亮平近点角 $l$、太阳平近点角 $l'$、月亮升交点平黄经 $\Omega$、月亮纬角参数 $F$、日月平距角 $D$（1980 常数，`AxisSystem.cpp:2312-2316`）：

$$
\begin{aligned}
\Omega &= 125.04452222^\circ + (-6962890.539\,t + 7.455\,t^2 + 0.008\,t^3)\ \text{arcsec} \\
l &= 134.96298139^\circ + (1717915922.6330\,t + 31.310\,t^2 + 0.064\,t^3)\ \text{arcsec} \\
l' &= 357.52772333^\circ + (129596581.2240\,t - 0.577\,t^2 - 0.012\,t^3)\ \text{arcsec} \\
F &= 93.27191028^\circ + (1739527263.1370\,t - 13.257\,t^2 + 0.011\,t^3)\ \text{arcsec} \\
D &= 297.85036306^\circ + (1602961601.3280\,t - 6.891\,t^2 + 0.019\,t^3)\ \text{arcsec}
\end{aligned}
$$

1996 组改用 `125.04455501 / 134.96340251 / 357.52910918 / 93.27209062 / 297.85019547` 度与四阶项（`AxisSystem.cpp:2320-2324, 2373-2375, 2434-2441`）。

- **代码位置**：`src/base/coordsystem/AxisSystem.cpp:2369-2377`（Ω）、`2420-2447`（l、l'、F、D）。
- **深度讲解**：
  - 实现细节（`AxisSystem.cpp:2369-2377`）：

    ```cpp
    // 月球升交点平黄经 Ω（1980 系数），单位：度 + 弧秒多项式
    longAscNodeLunar  = const125 + (  -6962890.5390*tTDB
                     + 7.455*tTDB2 + 0.008*tTDB3) * RAD_PER_ARCSEC;
    // 归约到 [0, 2π)
    longAscNodeLunar = longAscNodeLunar -
        ((int)(longAscNodeLunar/(2*PI)))*2*PI;
    ```

    2377 行用 `(int)` 截断除法做角度归约——注意对负角 `(int)` 向零截断会使结果落在 $[-2\pi,2\pi)$ 之外，实际靠后续 `sin/cos` 周期性与模 2π 等价；这是源码既有的近似处理。
  - 系数来源：代码注释（2307-2308 行）说明 Vallado 书里的常数有误，按 *Supplement to the Astronomical Almanac* 修正（GMT-4295）。1996 组为 IERS 1996 岁差章动理论，四项多项式升到 $t^4$。
  - 使用场景：这些角是 2.5 章动级数的自变量；Ω 与 cos ε̄ 还进入分点方程（§2.7）。

### 2.5 Δψ / Δε 章动傅里叶级数

- **公式**（Vallado 式 3-60）：设第 $i$ 项组合角 $\theta_i = a_1^{(i)}l + a_2^{(i)}l' + a_3^{(i)}F + a_4^{(i)}D + a_5^{(i)}\Omega$，则

$$
\begin{aligned}
\Delta\psi &= \sum_i \big[(A_i + B_i\,t)\sin\theta_i + E_i\cos\theta_i\big] \cdot (1''\text{ 缩放}) \\
\Delta\varepsilon &= \sum_i \big[(C_i + D_i\,t)\cos\theta_i + F_i\sin\theta_i\big] \cdot (1''\text{ 缩放})
\end{aligned}
$$

1980 组无 $E_i,F_i$ 项（`AxisSystem.cpp:2593-2597`），1996/2000 组保留（`AxisSystem.cpp:2598-2602`）。

- **代码位置**：`src/base/coordsystem/AxisSystem.cpp:2579-2613`（主级数）、`2628-2674`（行星项）。
- **深度讲解**：
  - 数据流：系数表由 `ItrfCoefficientsFile` 从 `NUTATION.DAT`/`NUT85.DAT` 读入（见 §5.3），`InitializeFK5`（`AxisSystem.cpp:2079-2204`）把 `std::vector<IntegerArray> a`（5×106 或 5×263 整数倍乘系数）拍平成 `aVals[numNut*5]`，`A..F` 六个 Rvector 由 `GetNutationTerms`（`ItrfCoefficientsFile.cpp:458-472`）返回并乘上文件倍乘因子（1980: 1e-4，1996: 1e-6，`ItrfCoefficientsFile.cpp:60-65, 299-304`）。
  - 实现细节（`AxisSystem.cpp:2587-2602`）：

    ```cpp
    // 组合角：aVals 列优先存储，i 为项号
    apNut = aVals[i]*meanAnomalyMoon + aVals[nut*1+i]*meanAnomalySun
       + aVals[nut*2+i]*argLatitudeMoon + aVals[nut*3+i]*meanElongationSun
       + aVals[nut*4+i]*longAscNodeLunar;
    cosAp = cos(apNut);  sinAp = sin(apNut);
    if (nutationSrc == GmatItrf::NUTATION_1980) {
       dPsi += (AVals[i] + BVals[i]*tTDB )*sinAp;   // Δψ 正弦项
       dEps += (CVals[i] + DVals[i]*tTDB )*cosAp;   // Δε 余弦项
    } else { // 1996/2000 增加 E、F 项
       dPsi += (AVals[i] + BVals[i]*tTDB )*sinAp + EVals[i]*cosAp;
       dEps += (CVals[i] + DVals[i]*tTDB )*cosAp + FVals[i]*sinAp;
    }
    ```

    2612-2613 行把累计和乘 `RAD_PER_ARCSEC` 转弧度。章动刷新率由 `updateIntervalToUse` 控制：`AxisSystem.cpp:2384-2406` 中若距上次计算不足一个刷新间隔（默认 60 s，地球可取 `Planet::GetNutationUpdateInterval`，`Planet.cpp:458-461`），直接复用 `lastDPsi` 并 return——这是章动"稀疏更新"的性能设计。
  - 行星项（仅 1996 组，`AxisSystem.cpp:2631-2670`）：先算金/地/火/木/土日心黄经与黄经总岁差 $p_A=(1.39697137214\,t+0.0003086\,t^2)^\circ$（2631-2637 行），再对 112 项行星表（`apVals[nutpl*10]`）叠加 $\Delta\psi_p=\sum(A_p+B_p t)\sin\theta_p$、$\Delta\varepsilon_p=\sum(C_p+D_p t)\cos\theta_p$，最后 2673-2674 行并入主值。注意代码注释（2624 行）说明行星项按 Steve Hughes 意见暂未启用。
  - 使用场景：输出 `dPsi` 供章动矩阵（§2.6）与分点方程（§2.7）共用；`longAscNodeLunar`、`cosEpsbar` 以引用参数返回。

### 2.6 章动矩阵 NUT

- **公式**（Vallado 式 3-64，MOD→TOD）：记 $\bar\varepsilon$ 平黄赤交角、$\Delta\psi$、$\Delta\varepsilon$，真黄赤交角 $\varepsilon=\bar\varepsilon+\Delta\varepsilon$：

$$
\mathrm{NUT}=
\begin{bmatrix}
\cos\Delta\psi & -\sin\Delta\psi\cos\bar\varepsilon & -\sin\Delta\psi\sin\bar\varepsilon\\
\sin\Delta\psi\cos\varepsilon & \cos\varepsilon\cos\Delta\psi\cos\bar\varepsilon+\sin\varepsilon\sin\bar\varepsilon & \sin\bar\varepsilon\cos\varepsilon\cos\Delta\psi-\sin\varepsilon\cos\bar\varepsilon\\
\sin\varepsilon\sin\Delta\psi & \sin\varepsilon\cos\Delta\psi\cos\bar\varepsilon-\sin\bar\varepsilon\cos\varepsilon & \sin\varepsilon\sin\bar\varepsilon\cos\Delta\psi+\cos\varepsilon\cos\bar\varepsilon
\end{bmatrix}
$$

- **代码位置**：`src/base/coordsystem/AxisSystem.cpp:2697-2717`（`AxisSystem::ComputeNutationMatrix`）。
- **深度讲解**：
  - 实现细节（`AxisSystem.cpp:2698-2717`）：

    ```cpp
    Real TrueOoE = Epsbar + dEps;            // 真黄赤交角 ε = ε̄ + Δε
    Real cosdPsi = cos(dPsi);  Real cosTEoE = cos(TrueOoE);
    Real sindPsi = sin(dPsi);  Real sinEpsbar = sin(Epsbar);
    Real sinTEoE = sin(TrueOoE);
    // MOD → TOD 旋转矩阵（Vallado 式 3-64）
    NUT.Set( cosdPsi, -sindPsi*cosEpsbar, -sindPsi*sinEpsbar,
             sindPsi*cosTEoE, cosTEoE*cosdPsi*cosEpsbar + sinTEoE*sinEpsbar,
             sinEpsbar*cosTEoE*cosdPsi - sinTEoE*cosEpsbar,
             sinTEoE*sindPsi, sinTEoE*cosdPsi*cosEpsbar - sinEpsbar*cosTEoE,
             sinTEoE*sinEpsbar*cosdPsi + cosTEoE*cosEpsbar);
    ```

    注意行 1-2 用平交角 $\bar\varepsilon$，行 2-3 用真交角 $\varepsilon$，这是 Vallado 式 3-64 的标准结构。2719-2721 行缓存 `lastNUTEpoch/lastNUT/lastDPsi`。
  - 旋转方向：`NUT` 把**平赤道历元（MOD）→ 真赤道历元（TOD）**；反向（TOD→MOD）取 `NUT.Transpose()`，即 TODEq 等轴系写入 `rotMatrix` 时的 `NutT`。
  - 使用场景：`TODEq/TODEc/TEME/EquatorAxes/BodyFixedAxes(地球)` 的"真赤道"环节。

### 2.7 格林尼治平恒星时 GMST 与分点方程

- **公式**（Vallado 式 3-45，单位先角秒后转度；代码以 1 秒 = 15″ = 1/240° 折算，`sec2deg = 15/3600`，`AxisSystem.cpp:2799-2800`）：

$$
\begin{aligned}
\theta_{\mathrm{GMST}} &= \frac{67310.54841}{240}^\circ + 360^\circ\!\cdot\!\mathrm{frac}(\mathrm{MJD_{UT1}}) + \frac{8640184.812866}{240}t_{\mathrm{UT1}} + \frac{0.093104}{240}t_{\mathrm{UT1}}^2 - \frac{6.2\times10^{-6}}{240}t_{\mathrm{UT1}}^3 \\
\mathrm{EqEq} &= \Delta\psi\cos\bar\varepsilon + (0.00264\sin\Omega + 0.000063\sin 2\Omega)\ \text{arcsec} \quad(\text{仅 } \mathrm{JD_{TT}}>2450449.5) \\
\theta_{\mathrm{AST}} &= \theta_{\mathrm{GMST}} + \mathrm{EqEq}
\end{aligned}
$$

- **代码位置**：`src/base/coordsystem/AxisSystem.cpp:2778-2808`（`AxisSystem::ComputeSiderealTimeRotation`）。
- **深度讲解**：
  - 实现细节（`AxisSystem.cpp:2788-2808`）：

    ```cpp
    // 1997-01-01 之后才加后两项（1982 章动模型不完整）
    if (jdTT > JD_OF_JANUARY_1_1997) {
       term2 = (0.00264 * sin(longAscNodeLunar))        * RAD_PER_ARCSEC;
       term3 = (0.000063 * sin(2.0 * longAscNodeLunar)) * RAD_PER_ARCSEC;
    }
    Real EQequinox = (dPsi * cosEpsbar) + term2 + term3;      // 分点方程
    Real hour2deg = 15.0;  Real sec2deg = hour2deg / SECS_PER_HOUR; // 1″=1/240°
    Real ThetaGmst = ((67310.54841 * sec2deg) +
        (mjdUT1.GetSec() + mjdUT1.GetFracSec())/SECS_PER_DAY*TWO_PI_DEG +
        (8640184.812866 * sec2deg)*tUT1 + (0.093104 * sec2deg)*tUT12
        - (6.2e-06 * sec2deg)*tUT13) * RAD_PER_DEG;
    ThetaGmst = AngleUtil::PutAngleInRadRange(ThetaGmst, 0.0, TWO_PI);
    Real ThetaAst = ThetaGmst + EQequinox;                     // 真恒星时
    ```

    $t_{\mathrm{UT1}} = \frac{\mathrm{MJD_{UT1}} + (\mathrm{JD\_JAN\_5\_1941}-\mathrm{JD\_OF\_J2000})}{36525}$（2778-2779 行）即自 J2000 的 UT1 儒略世纪；2802 行的 `frac(MJD)` 项给出 360°/日。`JD_OF_JANUARY_1_1997 = 2450449.5`（`AxisSystem.cpp:86`）。
  - 旋转方向：`ST = R_3(\theta_{\mathrm{AST}})$`（见 2.8），把真赤道坐标绕 Z 轴转 $\theta_{\mathrm{AST}}$ 到地球固连方向——这是"地球自转相位"环节。
  - 使用场景：`BodyFixedAxes`（地球）、`GSM`；`TEMEAxes` 用其简化形式（仅 $\Delta\psi\cos\bar\varepsilon$，见 §7.3）。`Planet::GetHourAngle`（`Planet.cpp:339-366`）用同式但整体以度为单位（`Planet.cpp:356-359`），供地面站时角计算。

### 2.8 恒星时旋转矩阵 ST 与恒星时率矩阵 SṪ

- **公式**：

$$
\mathrm{ST} = R_3(\theta_{\mathrm{AST}}) =
\begin{bmatrix}
\cos\theta_{\mathrm{AST}} & \sin\theta_{\mathrm{AST}} & 0\\
-\sin\theta_{\mathrm{AST}} & \cos\theta_{\mathrm{AST}} & 0\\
0 & 0 & 1
\end{bmatrix},
\qquad
\dot{\mathrm{ST}} = \frac{d}{dt}\mathrm{ST} =
\begin{bmatrix}
-\omega_E\sin\theta & \omega_E\cos\theta & 0\\
-\omega_E\cos\theta & -\omega_E\sin\theta & 0\\
0 & 0 & 0
\end{bmatrix}
$$

其中地球自转角速率 $\omega_E = 7.29211514670698\times10^{-5}\left(1-\dfrac{\mathrm{LOD}}{86400}\right)\ \text{rad/s}$，LOD 为日长（秒）。

- **代码位置**：`src/base/coordsystem/AxisSystem.cpp:2816-2818`（ST）、`2884-2887`（SṪ，`ComputeSiderealTimeDotRotation`）。
- **深度讲解**：
  - 实现细节（`AxisSystem.cpp:2884-2887`）：

    ```cpp
    // 从 EOP 文件取极移与 LOD（按 UTC 时刻插值）
    eop->GetPolarMotionAndLod(mjdUTC, x, y, lod);
    // 有效自转速率 = 名义速率 × (1 − LOD/86400)
    Real omegaE = 7.29211514670698e-05 * (1.0 - (lod / SECS_PER_DAY));
    STderiv.Set(-omegaE * sinAst,  omegaE * cosAst, 0.0,
                -omegaE * cosAst, -omegaE * sinAst, 0.0,
                             0.0,              0.0, 0.0);
    ```

    2872-2874 行把 `mjdUTC`（已加 `offset = JD_JAN_5_1941 − JD_NOV_17_1858 = 29999.5` 天，见 `BodyFixedAxes.cpp:595-600`）交给 EopFile 插值；2884 行 LOD 修正 $\omega_E$——LOD>0 表示地球自转变慢。
  - 使用场景：`rotDotMatrix` 的"恒星时率"分量，速度变换 $\vec v_{\text{base}}=\dot R\vec r+R\vec v$ 的 $\dot R$ 主要来自它（岁差/章动/极移的导数被忽略，注释见 `AxisSystem.cpp:2894-2895` 附近的实现与 §4.1 的合成）。

### 2.9 极移矩阵 PM

- **公式**：极移角 $x_p,y_p$（EOP 文件，弧秒）。代码用 `cX=cos(-x_p·RAD_PER_ARCSEC), sX=sin(-x_p·…)` 等构造，等价于

$$
\mathrm{PM} = R_2(-x_p)\,R_1(-y_p) =
\begin{bmatrix}
cX & sX\,sY & sX\,cY\\
0 & cY & -sY\\
-sX & cX\,sY & cX\,cY
\end{bmatrix}
$$

- **代码位置**：`src/base/coordsystem/AxisSystem.cpp:2940-2948`（`AxisSystem::ComputePolarMotionRotation`）。
- **深度讲解**：
  - 实现细节（`AxisSystem.cpp:2940-2948`）：

    ```cpp
    eop->GetPolarMotionAndLod(mjdUTC, x, y, lod);   // x,y 单位：弧秒
    Real cosX = cos(-x * RAD_PER_ARCSEC);  Real sinX = sin(-x * RAD_PER_ARCSEC);
    Real cosY = cos(-y * RAD_PER_ARCSEC);  Real sinY = sin(-y * RAD_PER_ARCSEC);
    PM.Set( cosX,  sinX*sinY, -sinX*cosY,
              0.0,       cosY,       sinY,
            sinX, -cosX*sinY,  cosX*cosY);
    ```

    小角近似下 $x,y\sim1''$，矩阵退化为经典形式 $\approx\begin{bmatrix}1&xy&x\\0&1&-y\\-x&y&1\end{bmatrix}$。极移把"真赤道→地球固连"的最后一步（地极在体上的摆动）补上。
  - 天文背景：极移是地球自转轴相对固体地球的准周期摆动（钱德勒摆动 ~433 天 + 周年项），幅度约 0.1~0.3″，必须用 IERS EOP 实测数据，无法解析建模。
  - 使用场景：`BodyFixedAxes`（地球）、`GSM`；`ITRFAxes` 用同一数据但矩阵形式不同（§5.1 的 `W`）。极移插值细节见 §10.2。

### 2.10 ICRF↔FK5 旋转（Euler 旋转向量 / Rodrigues 公式）

- **公式**：从 `ICRF_Table.txt` 按历元插值得到 Euler 旋转向量 $\vec e=(e_1,e_2,e_3)$，角 $\theta=|\vec e|$，轴 $\hat a=\vec e/\theta$；FK5→ICRF 的旋转矩阵为 Rodrigues 公式

$$
R_{\mathrm{FK5\to ICRF}} = \cos\theta\, I + (1-\cos\theta)\,\hat a\hat a^{\top} + \sin\theta\,[\hat a]_\times
$$

ICRF→FK5 取转置 $R_{\mathrm{ICRF\to FK5}}=R_{\mathrm{FK5\to ICRF}}^{\top}$。

- **代码位置**：`src/base/coordsystem/AxisSystem.cpp:3005-3059`（`RotationMatrixFromICRFToFK5`）；同式复制于 `CoordinateConverter.cpp:1047-1111` 与 `ICRFFile.cpp:247-308`。
- **深度讲解**：
  - 天文背景：FK5（J2000 平赤道，由光学恒星实现定义）与 ICRF（射电河外源实现，GCRS 定向）相差约 23 mas 的固定偏置 + 微小进动率。GMAT 用 `ICRF_Table.txt` 中 1957–2100 年的 3 分量 Euler 旋转向量表描述该差（`ICRFFile.cpp:63` 注释），表值经 9 阶 Lagrange 插值得到任意历元向量（`ICRFFile.cpp:175-233`）。
  - 实现细节（`AxisSystem.cpp:3024-3044`）：

    ```cpp
    // 旋转角 = 向量模长，轴 = 单位化向量
    Real angle = Sqrt(vec[0]*vec[0] + vec[1]*vec[1] + vec[2]*vec[2]);
    a[0] = vec[0]/angle;  a[1] = vec[1]/angle;  a[2] = vec[2]/angle;
    Real c = Cos(angle);  Real s = Sin(angle);
    // FK5 → ICRF 的旋转矩阵（Rodrigues）
    rotM.SetElement(0,0, c + a[0]*a[0]*(1-c));
    rotM.SetElement(0,1, a[0]*a[1]*(1-c) + a[2]*s);
    rotM.SetElement(0,2, a[0]*a[2]*(1-c) - a[1]*s);
    ...
    icrfToFK5 = rotM.Transpose();   // ICRF → FK5 取转置
    ```

    3024 行：角度即向量模长（小角度，~1.6e-7 rad）；3033-3041 行逐元素填 Rodrigues 矩阵；3044 行取转置得到 `icrfToFK5` 成员。3008-3010 行按历元缓存（`lastIcrfToFk5Epoch`）避免重复插值；`CoordinateConverter.cpp:1055-1059` 用 `fabs(dEpoch) < 1e-10` 容差缓存。
  - 数据流向：`CoordinateConverter::Convert` 在入/出轴系基系统不同（FK5 vs ICRF）时经 `ConvertFromBaseToBase`（§9.2）调用它；`AxisSystem::CalculateSpiceFrameRotationMatrix` 用它把 SPICE 返回的 J2000 帧旋转补到 FK5（§2.11）。
  - 使用场景：ICRF 基系统的轴系（`ICRFAxes`、`ITRFAxes`）与 FK5 基系统轴系互转；SPICE 帧桥接。

### 2.11 SPICE 帧旋转合成

- **公式**：设 CSPICE 返回的 6×6 变换 $M_{\mathrm{spice}}=\begin{bmatrix}R&\dot R\\0&R\end{bmatrix}$（J2000→目标帧），则

$$
R_{\text{body}\to\text{MJ2000Eq}} = R_{\mathrm{ICRF\to FK5}}\cdot R^{\top},\qquad \dot R_{\text{body}\to\text{MJ2000Eq}} = R_{\mathrm{ICRF\to FK5}}\cdot \dot R^{\top}
$$

- **代码位置**：`src/base/coordsystem/AxisSystem.cpp:3073-3091`（`AxisSystem::CalculateSpiceFrameRotationMatrix`）。
- **深度讲解**：`GetRotationMatrix("J2000", spiceToFrame, atEpoch)`（3085 行）返回 J2000→目标帧的 6×6 矩阵；`UpperLeft()` 是旋转部分、`LowerLeft()` 是速率部分（3086/3090 行）。SPICE 的 J2000 帧按 ICRF 定向，与 GMAT 的 FK5 基系差一个 `icrfToFK5`，故 3088-3090 行先调 `RotationMatrixFromICRFToFK5` 再左乘。消费方：`BodyFixedAxes`（`spiceIdSet` 或 `RotationDataSource()==SPICE_KERNEL` 时，`BodyFixedAxes.cpp:550-558`）、`SpiceAxes`（`SpiceAxes.cpp:407-416`）。

## 三、体固连系 BodyFixedAxes

`BodyFixedAxes::CalculateRotationMatrix`（`BodyFixedAxes.cpp:423-1023`）按原点类型分四支：Spacecraft（姿态 DCM）、地球（FK5 五件套合成）、月球（DE 天平动或 SPICE）、其它天体（IAU 简化 α,δ,W）。重算判据见 `BodyFixedAxes.cpp:532-547, 563-575`（历元/刷新间隔变化才重算）。

### 3.1 地球分支：PM·ST·NUT·PREC 组合

- **公式**：

$$
R_{\mathrm{BF\to MJ2000Eq}} = \big(\mathrm{PM}\cdot\mathrm{ST}\cdot\mathrm{NUT}\cdot\mathrm{PREC}\big)^{\top},
\qquad
\dot R_{\mathrm{BF\to MJ2000Eq}} = \big(\mathrm{PM}\cdot\dot{\mathrm{ST}}\cdot\mathrm{NUT}\cdot\mathrm{PREC}\big)^{\top}
$$

- **代码位置**：`src/base/coordsystem/BodyFixedAxes.cpp:587-676`（时间换算与五件套调用）、`690-769`（矩阵合成）。
- **深度讲解**：
  - 时间换算（`BodyFixedAxes.cpp:595-616`）：`A1→UTC`（极移/LOD 插值用，加 `offset=29999.5` 天对齐 EOP 文件 MJD）、`A1→UT1`（GMST 用）、`A1→TT`（岁差章动用）；`tTDB ≈ tTT`。
  - 合成实现（`BodyFixedAxes.cpp:693-731`）：

    ```cpp
    // NUT * PREC（行主序手工矩阵乘）
    np[p][q] = nutData[p3]*precData[q] + nutData[p3+1]*precData[q+3]
             + nutData[p3+2]*precData[q+6];
    // ST * (NUT * PREC)
    tmp[p][q] = stData[p3]*np[0][q] + stData[p3+1]*np[1][q] + stData[p3+2]*np[2][q];
    // PM * (ST * (NUT * PREC))
    rot[p][q] = pmData[p3]*tmp[0][q] + pmData[p3+1]*tmp[1][q] + pmData[p3+2]*tmp[2][q];
    // 写入 rotMatrix 时行列互换 → 等价取转置，得 BF→基系
    rotMatrix.Set(rot[0][0], rot[1][0], rot[2][0],
                  rot[0][1], rot[1][1], rot[2][1],
                  rot[0][2], rot[1][2], rot[2][2]);
    ```

    693-727 行先算 `np=ST·NUT·PREC` 次序中的内层乘积，729-731 行 `Set` 读列写行完成转置。745-769 行用 `stDerivData` 重复同构合成 `rotDotMatrix`。738-741 行（DEBUG 宏下）校验行列式 $|R|=1$（`DETERMINANT_TOLERANCE=1e-14`，`AxisSystem.cpp:85`）。
  - 旋转序列约定：经典 IAU-76/80 地固转换（逆序即 $R=W\,R_3(\theta)\,N\,P$，GMAT 记法 $\mathrm{PM}\cdot\mathrm{ST}\cdot\mathrm{NUT}\cdot\mathrm{PREC}$）——先岁差、再章动、再恒星时、最后极移，把"J2000 平赤道→真赤道→地球固连"走完，转置后即为固连→J2000。
  - 使用场景：任何 `EarthFixed` 系（默认 `EarthFixed` 轴系就是 BodyFixed），地面站坐标、引力场球谐项（[CH06 §6.x](../CH06-dynamics.md) 的 `GravityField` 需要 `xp/yp` 极移做极潮）都走这条链。

### 3.2 Spacecraft 原点分支：姿态 DCM 与斜对称矩阵

- **公式**：设姿态模型给出惯性→体 DCM $D$、惯性系中角速度 $\vec\omega$，则体固连角速度 $\vec\omega_B=D\vec\omega$，

$$
R_{\mathrm{BF\to inertial}}=D^{\top},\qquad
\dot R_{\mathrm{BF\to inertial}} = \big(-\big[\vec\omega_B\big]_\times D\big)^{\top}
$$

其中 $[\vec\omega_B]_\times=\begin{bmatrix}0&-\omega_z&\omega_y\\\omega_z&0&-\omega_x\\-\omega_y&\omega_x&0\end{bmatrix}$。

- **代码位置**：`src/base/coordsystem/BodyFixedAxes.cpp:444-529`。
- **深度讲解**：
  - 实现细节（`BodyFixedAxes.cpp:464-512`）：

    ```cpp
    Rmatrix33 dcm = sc->GetAttitude(theEpoch);   // 惯性→体
    rotMatrix     = dcm.Transpose();             // 我们要的是 体→惯性
    ...
    Rvector3 av   = sc->GetAngularVelocity(theEpoch);  // 惯性系中角速度
    Rvector3 avB  = dcm * av;                    // 转到体坐标
    Rmatrix33 skew( 0.0, -avB[2], avB[1],
                    avB[2], 0.0, -avB[0],
                   -avB[1], avB[0], 0.0);        // [ω_B]×
    Rmatrix33 RdotBI = -skew * dcm;              // d/dt(D^T)=−(ω_B)× D
    rotDotMatrix     = RdotBI.Transpose();
    ```

    数学依据：对正交阵 $D$，$\dot D=-\big[\omega_B\big]_\times D$，故 $\dot R=\dot D^{\top}$。472-488 行：姿态模型不计算速率时按 `allowNoRates` 置零矩阵或抛异常。
  - 使用场景：原点为 Spacecraft 的 BodyFixed 系（如"本体坐标系"），用于姿态相关输出；`rotMatrixDeriv`（对航天器状态偏导，`AxisSystem.hpp:225-227`）支持估计器。

### 3.3 月球分支：DE 文件天平动角

- **公式**：DE 文件给出 3 个天平动角 $(\theta_1,\theta_2,\theta_3)$ 及其变化率 $(\dot\theta_1,\dot\theta_2,\dot\theta_3)$（`DeFile::GetAnglesAndRates`，`DeFile.cpp:809-864`，切比雪夫插值 `Interpolate_Libration`）。`rotMatrix = [\text{ToCosineMatrix}(\theta)]^{\top}$，`rotDotMatrix` 按 9 元素显式写出（含三对角乘积导数）。

- **代码位置**：`src/base/coordsystem/BodyFixedAxes.cpp:813-887`；数据入口 `DeFile.cpp:834, 863`。
- **深度讲解**：
  - 实现细节（`BodyFixedAxes.cpp:834-869`）：

    ```cpp
    de->GetAnglesAndRates(atEpoch, librationAngles, andRates, override);
    // 用姿态工具把 3-1-3 欧拉角转成 DCM，再转置得到 月固连→惯性
    rotMatrix = (AttitudeConversionUtility::ToCosineMatrix(
                 librationAngles, 3, 1, 3)).Transpose();
    // 随后用 cos/sin 组合逐元素写出 rotDotMatrix（859-869 行）
    rotDotMatrix.Set(
       -andRates[2]*(s3c1+s1c2c3) + andRates[1]*sa3*s1s2 - andRates[0]*(s1c3+s3c1c2),
       ...
    );
    ```

    836 行把 DE 天平动角按 3-1-3 欧拉序列转 DCM 再转置；859-869 行的 9 个表达式是 $\frac{d}{dt}\big(R_3^{\top}R_1^{\top}R_3^{\top}\big)$ 的展开（`s1c2 = sinθ1·cosθ2` 等缩写，837-857 行预计算）。`EquatorAxes` 的月球分支（`EquatorAxes.cpp:304-403`）用同一数据源但只取前两个角（$R_3^{\top}(\theta_1)R_1^{\top}(\theta_2)$，341-343 行）。
  - 触发条件：`originName==MOON_NAME` 且 `RotationDataSource()==DE_FILE`（`BodyFixedAxes.cpp:813-814`）；SPICE 源时走 §2.11。
  - 使用场景：月球固连系（`LunaFixed`），月面着陆/环月任务。

### 3.4 IAU 简化分支：由 (α, δ, W) 构造 DCM

- **公式**：设天体北极赤经 α、赤纬 δ、本初子午线经度 W（均来自 §11 的天体定向展开），记 $a=\frac\pi2+\alpha$、$b=\frac\pi2-\delta$：

$$
R_{\mathrm{BF\to MJ2000Eq}} = R_3^{\top}(a)\,R_1^{\top}(b)\,R_3^{\top}(W),\qquad
\dot R = R_3^{\top}(a)\,R_1^{\top}(b)\,\dot R_3^{\top}(W)
$$

其中 $\dot R_3^{\top}(W)=\begin{bmatrix}-\dot W\sin W&-\dot W\cos W&0\\\dot W\cos W&-\dot W\sin W&0\\0&0&0\end{bmatrix}$，$\dot W=\dfrac{W_{\text{deg/day}}}{86400}$（rad/s）。

- **代码位置**：`src/base/coordsystem/BodyFixedAxes.cpp:888-1007`（天体分支）；同构实现见 `BodyInertialAxes.cpp:194-200` 与 `EquatorAxes.cpp:419-442`（后者不含 W）。
- **深度讲解**：
  - 实现细节（`BodyFixedAxes.cpp:906-922, 970-982`）：

    ```cpp
    // 返回 α(deg)、δ(deg)、W(deg)、Wdot(deg/day)
    cartCoord = ((CelestialBody*)origin)->GetBodyCartographicCoordinates(atEpoch.GetMjd());
    Real rot1 = PI_OVER_TWO + Rad(cartC[0]);   // π/2 + α
    Real rot2 = PI_OVER_TWO - Rad(cartC[1]);   // π/2 − δ
    Real W    = Rad(cartC[2]);  Real Wdot = Rad(cartC[3]) / SECS_PER_DAY; // rad/s
    Real R3leftT[9]  = {Cos(rot1),-Sin(rot1),0.0, Sin(rot1),Cos(rot1),0.0, 0.0,0.0,1.0};
    Real R1middleT[9]= {1.0,0.0,0.0, 0.0,Cos(rot2),-Sin(rot2), 0.0,Sin(rot2),Cos(rot2)};
    Real R3rightT[9] = {Cos(W),-Sin(W),0.0, Sin(W),Cos(W),0.0, 0.0,0.0,1.0};
    // ... 三矩阵连乘得 rotResult，再 Set 进 rotMatrix
    Wderiv[0] = -Wdot*Sin(W); Wderiv[1] = -Wdot*Cos(W); Wderiv[2] = 0.0; ...
    ```

    913-922 行的 `R3leftT`/`R1middleT`/`R3rightT` 分别是 $R_3^{\top}(a),R_1^{\top}(b),R_3^{\top}(W)$（名字里的 T 表示转置后的矩阵）；949-972 行连乘；974-982 行构造 $\dot R_3^{\top}(W)$；984-1006 行得到 `rotDotMatrix`。
  - 天文背景：IAU 2000 工作组给出的天体定向约定就是"北极指向 (α,δ) + 绕北极自转角 W"，对除地球/月球/海王星外的大行星、矮行星、小行星、卫星都适用（§11 的多项式展开）；地球不适用（需 FK5+EOP），月球用天平动或 DE，海王星用 IAU_2002 特殊式。
  - 使用场景：`MarsFixed`、`VenusFixed` 等一切非地球/月球的体固连系（`RotationDataSource()==IAU_SIMPLIFIED` 或 `IAU_2002` 之外的路径）。

## 四、ITRF 与 IAU2000/2006 路线（CIO 基）

### 4.1 基本旋转矩阵 R1/R2/R3 与斜对称 Skew

- **公式**（右手系，主动旋转约定）：

$$
R_1(\theta)=\begin{bmatrix}1&0&0\\0&\cos\theta&\sin\theta\\0&-\sin\theta&\cos\theta\end{bmatrix},\quad
R_2(\theta)=\begin{bmatrix}\cos\theta&0&-\sin\theta\\0&1&0\\\sin\theta&0&\cos\theta\end{bmatrix},\quad
R_3(\theta)=\begin{bmatrix}\cos\theta&\sin\theta&0\\-\sin\theta&\cos\theta&0\\0&0&1\end{bmatrix}
$$

- **代码位置**：`src/base/coordsystem/ITRFAxes.cpp:340-399`（R1/R2/R3）、`414-422`（Skew）。
- **深度讲解**：这三个矩阵是 ITRF 路线（§4.2）的构件，也定义了全章"绕 X/Y/Z 轴旋转"的符号约定（与 §2 各矩阵一致）。`Skew` 构造 $[\vec v]_\times$，用于 $\dot R$ 的 $\omega\times$ 表达。注意 ITRF 的 R1/R2/R3 与 `BodyFixedAxes.cpp:913-922` 手工展开的转置版本符号一致（互为转置关系），使用时以各自代码为准。

### 4.2 ITRF：X/Y/s 天球中间极（CIP）路线

- **公式**（IERS 2010 / IAU 2006 约定，`ITRFAxes.cpp:486-516`）：

$$
\begin{aligned}
s' &= -0.000047''\cdot T_{TT} \qquad(\text{弧秒})\\
\theta &= 2\pi\big(0.7790572732640 + 1.00273781191135448\,(\mathrm{JD_{UT1}}-2451545.0)\big) \bmod 2\pi \quad(\text{地球自转角 ERA})\\
W &= R_3(-s')\,R_2(x_p)\,R_1(y_p)\\
b &= \frac{1}{1+\sqrt{1-X^2-Y^2}}\\
C_T &= \begin{bmatrix}1-bX^2&-bXY&X\\-bXY&1-bY^2&Y\\-X&-Y&1-b(X^2+Y^2)\end{bmatrix} R_3(s)\\
R_{\mathrm{ITRF\to GCRF}} &= C_T\,R_3(-\theta)\,W
\end{aligned}
$$

其中 $X,Y,s$ 来自 `IAU_SOFA.DAT`（按 $T_{TT}$ 插值，弧秒转弧度）。速率矩阵 $\dot R = C_T\,R_3(-\theta)\,[\vec\omega_E]_\times\,W$，$\vec\omega_E=(0,0,\omega_E)^{\top}$、$\omega_E=7.292115146706979\times10^{-5}\big(1-\frac{\mathrm{LOD}}{86400}\big)$。

- **代码位置**：`src/base/coordsystem/ITRFAxes.cpp:449-516`（`ITRFAxes::CalculateRotationMatrix`）。
- **深度讲解**：
  - 实现细节（`ITRFAxes.cpp:486-516`）：

    ```cpp
    Real sPrime = -0.000047*sec2rad*T_TT;                     // 极移运动学项 s′
    Rmatrix33 W = R3(-sPrime)*R2(xp)*R1(yp);                  // 极移矩阵（含 s′）
    Real theta  = fmod(TWO_PI*(0.7790572732640 +
         1.00273781191135448*(jdUT1 - 2451545.0)), TWO_PI);   // 地球自转角 ERA
    iauFile->GetIAUData(jdTT, data, 3, 9);                    // 插值 X, Y, s
    Real X = data[0]*sec2rad;  Real Y = data[1]*sec2rad;  Real s = data[2]*sec2rad;
    Real b = 1/(1 + sqrt(1 - X*X - Y*Y));                     // 法向化因子
    CT.SetElement(0,0, 1-b*X*X); ...                          // CIP→GCRF 矩阵
    CT = CT*R3(s);                                            // 补上 天体中间原点 s
    Rmatrix33 R    = CT*R3(-theta)*W;                         // ITRF→GCRF
    Real omegaEarth = 7.292115146706979e-5*(1 - LOD/86400);
    Rmatrix33 Rdot = CT*R3(-theta)*Skew(vec)*W;               // 速率矩阵
    rotMatrix = R;  rotDotMatrix = Rdot;
    ```

    462 行 `eop->GetPolarMotionAndLod(utcMJD+offset, xp, yp, LOD)` 取极移（弧秒，464-465 行转弧度）；483 行 $T_{TT}$ 为 TT 儒略世纪；488 行 ERA 是 IAU 2000 定义的"地球自转角"，取代经典 GMST+分点方程路线。
  - 与 FK5 路线的关系：经典路线（§3.1）用 $\zeta,\Theta,z$ + $\Delta\psi,\Delta\varepsilon$ + GMST/分点方程 + 极移；IAU2000/2006 路线改用 CIP 的 $X,Y$ 分量与 ERA，精度更高、无赤经原点奇点问题。GMAT 中 `ITRFAxes` 走新路线，`BodyFixedAxes`（地球）走经典路线，两者并存。
  - 基系统：`ITRFAxes` 构造时 `baseSystem="ICRF"`（`ITRFAxes.cpp:97`），故它输出的旋转目标基系是 ICRF 而非 FK5——`Convert` 需要时再经 §2.10 补齐。
  - 使用场景：`EarthFixed` 若用户指定 ITRF 轴系；IERS 2010 兼容输出。

### 4.3 IAUFile：IAU_SOFA.DAT 插值

- **公式**：$X,Y,s$ 为日心/地心中间天球坐标分量（弧秒），按 TT 儒略日 1 天步长表存储，任意历元用 $n$ 阶（默认 9 阶）Lagrange 插值。
- **代码位置**：`src/base/coordsystem/IAUFile.cpp:76-146`（`Initialize` 读表）、`176-219`（`GetIAUData` 插值）。
- **深度讲解**：单例（`IAUFile.cpp:61-67`），`FileManager` 定位 `IAU_SOFA.DAT`（94-96 行），`fscanf` 逐行读 `t X Y s`（110-141 行）；插值前二分定位中点（196-201 行，等步长 1 天故可用公式 198 行），`LagrangeInterpolator` 做 9 阶插值（205-216 行）。消费方只有 `ITRFAxes`（`ITRFAxes.cpp:222-224, 497`）。

### 4.4 ItrfCoefficientsFile：章动/行星系数表

- **公式**：系数文件提供 2.5 级数所需的倍乘系数 $a_{ji}$（5 个）与振幅 $A_i,B_i,C_i,D_i$（1980：106 项×1e-4；1996：263 项×1e-6）以及行星项 10 个倍乘系数与 $A_p,B_p,C_p,D_p$（85 或 112 项×1e-4）。
- **代码位置**：`src/base/coordsystem/ItrfCoefficientsFile.cpp:53-71`（常量）、`242-351`（`Initialize` 解析）、`458-472`/`490-501`（`GetNutationTerms`/`GetPlanetaryTerms`）、`522-610`（`InitializeArrays` 分配）。
- **深度讲解**：按"首个标识短语"（`"1980 IAU"`/`"1996 IAU"`/`"2000 IAU"`，53-58 行）定位数据段，跳过表头后逐行读整数倍乘系数与振幅（273-298 行），再整体乘倍乘因子（299-304 行）。`AxisSystem::InitializeFK5`（`AxisSystem.cpp:2092-2203`）消费它：取项数、分配 `A..F`/`Ap..Dp` 向量并拍平 `aVals/apVals`。数据来源注明为 Vallado celestrak 软件页（`ItrfCoefficientsFile.hpp:31-32`）。

## 五、惯性轴系

### 5.1 MJ2000EqAxes：基系本身（恒等）

- **公式**：$R=I_3$，$\dot R=0$。
- **代码位置**：`src/base/coordsystem/MJ2000EqAxes.cpp:129-149`（`Initialize` 置 138-140 行对角元为 1），`CalculateRotationMatrix` 为空（186-190 行）。
- **深度讲解**：MJ2000Eq 是 FK5 基系统下所有旋转的"终点"——其它轴系算出的 `rotMatrix` 都以它为目标。`rotMatrix` 在 `Initialize` 一次置位，运行时不再变化。

### 5.2 MJ2000EcAxes：J2000 黄道（固定黄赤交角）

- **公式**：设 J2000 平黄赤交角 $\varepsilon_0$，则 $R=R_1(\varepsilon_0)$，数值矩阵

$$
R=\begin{bmatrix}1&0&0\\0&0.917482062076895741&-0.397777155914121383\\0&0.397777155914121383&0.917482062076895741\end{bmatrix}
$$

- **代码位置**：`src/base/coordsystem/MJ2000EcAxes.cpp:119-136`（`Initialize` 硬编码 123-131 行）。
- **深度讲解**：常数即 $\cos\varepsilon_0,\sin\varepsilon_0$（$\varepsilon_0\approx23.4392911^\circ$）。绕 X 轴转 $-\varepsilon_0$ 把 J2000 赤道坐标转到 J2000 黄道坐标。`rotDotMatrix` 恒零。

### 5.3 ICRFAxes：ICRF 基系统本身（恒等）

- **公式**：$R=I_3$，$\dot R=0$。
- **代码位置**：`src/base/coordsystem/ICRFAxes.cpp:75-86`（构造设 `baseSystem="ICRF"`）、`234-244`（`CalculateRotationMatrix` 置恒等）。
- **深度讲解**：与 MJ2000Eq 同构但基系统标签为 ICRF；两者的数值差（~23 mas 偏置）不在本轴系内处理，而是由 `CoordinateConverter` 在基系统不同时经 `icrfToFK5` 补齐（§9.2）。`UsesEopFile` 恒 `NOT_USED`（`ICRFAxes.cpp:173-178`）。

### 5.4 BodyInertialAxes：天体惯性系（北极指向固定）

- **公式**：地球：$R=I_3$；月球：硬编码常数 DCM（`BodyInertialAxes.cpp:177-180`）；其它天体：用历元处天体定向角 $\alpha,\delta$（§11）构造 $R=R_3^{\top}\big(\frac\pi2+\alpha\big)\,R_1^{\top}\big(\frac\pi2-\delta\big)$。
- **代码位置**：`src/base/coordsystem/BodyInertialAxes.cpp:154-208`（`Initialize`）。
- **深度讲解**：`MarsInertial` 等"天体赤道系（J2000 定向）"的实现——把天体北极固定在 J2000 方向，不自转。与 §3.4 相比少了 $R_3^{\top}(W)$ 自转项（该系不随天体自转）。

### 5.5 TOEEqAxes / TOEEcAxes：真赤道/真黄道（历元 2000 定向）

- **公式**（在 `Initialize` 时对设定历元计算一次，之后固定）：

$$
R_{\mathrm{TOEEq}} = \mathrm{PREC}^{\top}\mathrm{NUT}^{\top},\qquad
R_{\mathrm{TOEEc}} = \mathrm{PREC}^{\top}\,R_1(-\bar\varepsilon)\,R_3(-\Delta\psi)
$$

- **代码位置**：`src/base/coordsystem/TOEEqAxes.cpp:129-211`（`Initialize`：时间换算 145-151 行、`PrecT·NutT` 连乘 173-203 行）；`TOEEcAxes.cpp:123-195`（`Epsbar` 144-148 行、`R3PsiT` 158-160 行、连乘 166-190 行）。
- **深度讲解**：TOE 家族由 Kenton Gee 加入（文件头注释），语义是"把 J2000 定向的坐标轴在设定历元处对到真赤道/真黄道"，随后冻结——是**历元固定的惯性系**，与 TODEq（随历元实时变化）不同。`PrecT = PREC.Transpose()`、`NutT = NUT.Transpose()`（173-181 行）体现"从真赤道回到 J2000"的方向。`UsesEpoch` 返回 `REQUIRED`（`TOEEqAxes.cpp:221-224`）。

### 5.6 MOEEqAxes / MOEEcAxes：平赤道/平黄道（历元 2000 定向）

- **公式**：

$$
R_{\mathrm{MOEEq}} = \mathrm{PREC}^{\top},\qquad
R_{\mathrm{MOEEc}} = \mathrm{PREC}^{\top}\,R_1(-\bar\varepsilon)
$$

- **代码位置**：`src/base/coordsystem/MOEEqAxes.cpp:123-149`（`Initialize`，`PrecT` 142-144 行）；`MOEEcAxes.cpp:123-175`（`Epsbar` 139-140 行、`R1EpsT` 142-144 行、`PrecT·R1EpsT` 连乘 156-171 行）。
- **深度讲解**：与 TOE 族对称的"平"版本——只走岁差不走章动。`MOEEq` 即"J2000 定向的平赤道历元"，`MOEEc` 再转平黄道。同样在 `Initialize` 冻结（`CalculateRotationMatrix` 为空实现，`MOEEqAxes.cpp:199-203`）。

## 六、历元系（随历元实时变化）

### 6.1 MODEqAxes / MODEcAxes：平赤道/平黄道（历元）

- **公式**（每次 `CalculateRotationMatrix` 实时计算）：

$$
R_{\mathrm{MODEq}}=\mathrm{PREC}^{\top},\qquad
R_{\mathrm{MODEc}}=\mathrm{PREC}^{\top}\,R_1(-\bar\varepsilon)
$$

- **代码位置**：`src/base/coordsystem/MODEqAxes.cpp:165-191`（`CalculateRotationMatrix`：`tTDB` 170-176 行、`rotMatrix = PrecT` 185-187 行）；`MODEcAxes.cpp:165-218`（`Epsbar` 181-182 行、`R1EpsT` 184-186 行、`PrecT·R1EpsT` 连乘 194-214 行）。
- **深度讲解**：`MODEq`（Mean of Date Equator）是"当前历元平赤道"，常用于近地轨道摄动分析；与 `MOEEq`（固定历元）的区别在于 MODEq 每个求值历元都重算 `PREC`。`rotDotMatrix` 保持零矩阵（注释"assume it is negligibly small"，`MODEqAxes.cpp:189-190`）——岁差率 ~50″/世纪，相对轨道角速度可忽略。

### 6.2 TODEqAxes / TODEcAxes：真赤道/真黄道（历元）

- **公式**：

$$
R_{\mathrm{TODEq}}=\mathrm{PREC}^{\top}\mathrm{NUT}^{\top},\qquad
R_{\mathrm{TODEc}}=\mathrm{PREC}^{\top}\,R_1(-\bar\varepsilon)\,R_3(-\Delta\psi)
$$

- **代码位置**：`src/base/coordsystem/TODEqAxes.cpp:171-238`（`PrecT·NutT` 213-234 行）；`TODEcAxes.cpp:167-237`（`Epsbar` 186-190 行、`R3PsiT` 200-202 行、`R1EpsT·R3PsiT` 连乘 210-229 行、`rotMatrix.Set` 230-232 行）。
- **深度讲解**：`TODEq`（True of Date Equator）即经典"真赤道真春分点（TOD）"，J2000→TOD 的净旋转 $N^{\top}P^{\top}$。`TODEc` 是"真赤道真春分点的黄道版本"，绕 Z 转 $-\Delta\psi$ 消去黄经章动、绕 X 转 $-\bar\varepsilon$ 从黄道回赤道。注意：TODEc 的 $R_1$ 用**平**黄赤交角 $\bar\varepsilon$ 而非真值 $\varepsilon=\bar\varepsilon+\Delta\varepsilon$（代码 186-190 行只用 `Epsbar`），这是实现选择，与教科书版本略有出入。`rotDotMatrix` 亦置零（`TODEqAxes.cpp:236-237`）。

### 6.3 TEMEAxes：真赤道平春分点（TEME）

- **公式**：在 TOD 基础上移除"赤经章动"（分点方程），使春分点回到平位置：

$$
R_{\mathrm{TEME\to MJ2000Eq}}=\mathrm{PREC}^{\top}\mathrm{NUT}^{\top}\,R_3(-\mathrm{EqMod}),\qquad
\mathrm{EqMod}=\Delta\psi\cos\bar\varepsilon
$$

- **代码位置**：`src/base/coordsystem/TEMEAxes.cpp:176-262`（`CalculateRotationMatrix`：`EqNox` 矩阵 229-231 行、连乘 233-258 行）、`282-304`（`ComputeModEq`）。
- **深度讲解**：
  - 实现细节（`TEMEAxes.cpp:203-231`）：

    ```cpp
    ComputePrecessionMatrix(tTDB, atEpoch);
    ComputeNutationMatrix(tTDB, atEpoch, dPsi, longAscNodeLunar, cosEpsbar, forceComputation);
    Real eqMod = ComputeModEq(atEpoch.GetReal(), tTDB, dPsi, longAscNodeLunar, cosEpsbar);
    ...
    Real EqNox[9] = { cos(-eqMod), sin(-eqMod), 0,
                     -sin(-eqMod), cos(-eqMod), 0,
                     0, 0, 1};                       // R3(−EqMod)
    // res = PrecT·NutT；temp = res·EqNox
    ```

    `ComputeModEq`（282-304 行）只取 $\Delta\psi\cos\bar\varepsilon$（1997 后的补充项 term2/term3 在此实现中恒为 0，298-300 行），注释指向 Vallado 式 3-90/3-91（TEME 定义）。`InitializeReference` 强制原点为 Earth（`TEMEAxes.cpp:316-322`）。
  - 天文背景：TEME 是 NORAD/SGP4 两行根数所用的近地惯性系，"真赤道 + 平春分点"使赤经无需顾及章动赤经分量。`EqNox` 名即 "Equation of the equinoxes"。
  - 使用场景：两行根数（TLE）→ 笛卡尔状态的兼容换算。

### 6.4 EquatorAxes：天体赤道面系

- **公式**：三分支——地球：$R=\mathrm{PREC}^{\top}\mathrm{NUT}^{\top}$（=TODEq）；月球（DE 源）：$R=R_3^{\top}(\theta_1)\,R_1^{\top}(\theta_2)$ 及 $\dot R$ 含 $\dot\theta_1,\dot\theta_2$ 项；其它天体：$R=R_3^{\top}\big(\frac\pi2+\alpha\big)\,R_1^{\top}\big(\frac\pi2-\delta\big)$。
- **代码位置**：`src/base/coordsystem/EquatorAxes.cpp:226-444`（地球 233-302 行、月球 DE 304-403 行、IAU 404-443 行）。
- **深度讲解**：`EquatorAxes` 表示"某天体赤道面"，但不随天体自转（与 BodyFixed 区别在于不含 $W$ 旋转；与 BodyInertial 区别在于随历元进动/章动或取 DE 天平动）。月球分支的 `rotDotMatrix` 用 $\dot R=R_3^{\top}\dot R_1^{\top}+\dot R_3^{\top}R_1^{\top}$ 展开（`EquatorAxes.cpp:369-402`，`R3Dot_ang1_T`/`R1Dot_ang2_T` 见 345-351 行）。

## 七、对象参考与局部轴系

### 7.1 ObjectReferencedAxes：R/V/N 轴系

- **公式**：设 $\vec r,\vec v$ 为 secondary 相对 primary 的位置/速度（MJ2000Eq），$\vec n=\vec r\times\vec v$；用户指定 X/Y/Z 轴取 $\pm\hat r,\pm\hat v,\pm\hat n$ 中的两个，第三个由叉积补全；`rotMatrix` 的三列即 $(\hat x,\hat y,\hat z)$，`rotDotMatrix` 三列为 $(\dot{\hat x},\dot{\hat y},\dot{\hat z})$，其中 $\dot{\hat r}=\frac{\vec v}{r}-\frac{\hat r}{r}(\hat r\cdot\vec v)$ 等。
- **代码位置**：`src/base/coordsystem/ObjectReferencedAxes.cpp:875-1165`（`CalculateRotationMatrix`：r/v/n 946-952 行、单位向量导数 975-977 行、第三轴补全 1102-1121 行、填矩阵 1123-1142 行、正交性校验 1159-1164 行）。
- **深度讲解**：通用"轨道系"生成器——`VNB`、`NTW`、`RIC` 等任务常用系都是它的特例（由 X/Y/Z 轴字符串配置）。轴选取校验见 899-915 行（三轴不可重复、最多指定两个）。1159 行用 `ORTHONORMAL_TOL` 校验正交性并告警。

### 7.2 GeocentricSolarEclipticAxes（GSE）

- **公式**：$\hat x=\hat r_{\odot}$（地心→太阳单位向量）、$\hat z=\dfrac{\vec r\times\vec v}{|\vec r\times\vec v|}$、$\hat y=\hat z\times\hat x$；$\dot{\hat x}=\frac{\vec v}{r}-\hat x(\hat x\cdot\frac{\vec v}{r})$、$\dot{\hat z}=0$、$\dot{\hat y}=\hat z\times\dot{\hat x}$。
- **代码位置**：`src/base/coordsystem/GeocentricSolarEclipticAxes.cpp:233-285`（`CalculateRotationMatrix`：242-258 行基向量、270-283 行导数）。
- **深度讲解**：GSE 的 X 轴严格指向太阳、Z 轴垂直黄道面（实为轨道面法向近似）。primary=Earth、secondary=Sun 由沙箱注入。rotMatrix 行列填充方式（260-268 行）与 ObjectReferencedAxes 相同（列 = 轴单位向量）。

### 7.3 GeocentricSolarMagneticAxes（GSM）

- **公式**：先做 FK5 五件套把偶极方向转到 MJ2000Eq：$\hat d=R_{\mathrm{fixed\to MJ2000Eq}}\,\hat d_{\mathrm{fixed}}$（$\hat d_{\mathrm{fixed}}=(\cos\phi_D\cos\lambda_D,\ \cos\phi_D\sin\lambda_D,\ \sin\phi_D)$，偶极地理经纬度 $\lambda_D=288.555^\circ,\ \phi_D=79.379^\circ$ 附近，见 `GeocentricSolarMagneticAxes.cpp:296-301`）；再取 $\hat x=\hat r_{\odot}$、$\hat y=\dfrac{\hat d\times\hat x}{|\hat d\times\hat x|}$、$\hat z=\hat x\times\hat y$。
- **代码位置**：`src/base/coordsystem/GeocentricSolarMagneticAxes.cpp:296-301`（`ComputeDipoleEarthFixed`）、`316-560`（`CalculateRotationMatrix`：五件套 356-363 行、固定→MJ2000Eq 合成 365-447 行、基向量 448-486 行、导数 488-522 行）。
- **深度讲解**：GSM 是空间天气/磁层研究标准系（X 指太阳、Y 在磁偶极与太阳方向张成的平面内）。代码 356-363 行复用 `ComputePrecession/Nutation/SiderealTime/PolarMotion` 四件套（无岁差章动缓存开销），404-447 行先按 §3.1 同构合成 `fixedToMJ2000` 及其导数，再转偶极方向；450-486 行构造基向量；488-522 行用链式法则求 $\dot{\hat x},\dot{\hat y},\dot{\hat z}$（含 $\dot{\hat d}=R_{\mathrm{fixed\to MJ2000Eq}}\,\hat d$ 项，498-510 行）。416-418 行行列式校验与 BodyFixed 地球分支同款。

### 7.4 LocalAlignedConstrainedAxes（LAC，triad 算法）

- **公式**：对齐向量 $\vec a$（reference→origin，惯性系）与约束向量 $\vec c$（约束坐标系给出），triad：

$$
\hat n_I=\frac{\vec a_I\times\vec c_I}{|\vec a_I\times\vec c_I|},\quad
\hat w_I=\hat a_I\times\hat n_I,\qquad
R_1=\big[\hat a_I\ \hat n_I\ \hat w_I\big],\quad
R_2=\big[\hat a_B\ \hat n_B\ \hat w_B\big]^{\top},\quad
R=R_1\,R_2
$$

导数：$\dot R=\dot R_1R_2+R_1\dot R_2$（单位向量导数 $\dot{\hat a}=\frac{\dot{\vec a}}{a}-\frac{\hat a}{a}(\hat a\cdot\dot{\vec a})$ 等）。

- **代码位置**：`src/base/coordsystem/LocalAlignedConstrainedAxes.cpp:900-1075`（`CalculateRotationMatrix`：基向量 984-1024 行、`R1·R2` 1025 行、导数 1034-1067 行）。
- **深度讲解**：LAC 是姿态确定里"三轴对齐"的经典问题：对齐轴必须沿 reference→origin 视线，约束轴尽量贴近用户给定方向，第三轴由叉积闭合。零向量防护见 970-979、991-999 行（`MAGNITUDE_TOL`）。`constraintCS->ToBaseSystem`（936 行）把约束向量转到惯性系。

### 7.5 TopocentricAxes：站心系

- **公式**：站心（Topocentric）→体固连（RFT）矩阵由站址大地坐标构造：迭代求大地纬度 $\phi_g$（`TopocentricAxes.cpp:392-408`），$\hat z=(\cos\phi_g\cos\lambda,\ \cos\phi_g\sin\lambda,\ \sin\phi_g)$、$\hat y=\dfrac{\hat k\times\hat z}{|\hat k\times\hat z|}$、$\hat x=\hat y\times\hat z$；`rotMatrix = RIF·RFT`（体固连→惯性 × 站心→体固连）。
- **代码位置**：`src/base/coordsystem/TopocentricAxes.cpp:221-343`（`CalculateRotationMatrix`）、`359-470`（`CalculateRFT`）。
- **深度讲解**：`RIF` 从原点天体的体固连系取（305-306 行，`bfcs->GetLastRotationMatrix()`，内部用"伪状态"触发一次 `ToBaseSystem` 得到最近矩阵，287-288 行）；`RFT` 仅在站址变化时重算（276-279 行）。极区奇点防护见 373-378 行（$r_{xy}<1$ mm 抛异常）。`rotDotMatrix = RIFDot·RFT`（325 行）忽略站址运动。

### 7.6 SpiceAxes：任意 SPICE 帧

- **公式**：$R_{\text{frame}\to\text{MJ2000Eq}} = R_{\mathrm{ICRF\to FK5}}\cdot R_{\text{spice}}^{\top}$（同 §2.11 的 `CalculateSpiceFrameRotationMatrix`）。
- **代码位置**：`src/base/coordsystem/SpiceAxes.cpp:353-425`（`CalculateRotationMatrix`：SPICE 分支 407-416 行）；核心在 `AxisSystem.cpp:3073-3091`。
- **深度讲解**：`SpiceAxes` 允许用户指定任意 NAIF 帧名（`SpiceFrameId`），前提是已加载相应内核（CK/PK）。407 行同时接受坐标系级 `spiceFrameId` 与原点天体的 `SpiceFrameId` 参数。`Initialize` 对地球调用 `InitializeFK5`（`SpiceAxes.cpp:212`），因为合成需要 `icrfToFK5`。

## 八、坐标转换器与平移

### 8.1 AxisSystem::RotateToBaseSystem 与速度变换

- **公式**：`RotateToBaseSystem` = `CalculateRotationMatrix(epoch)` + `CompleteRotateToBase`；位置/速度变换为

$$
\vec r_{\mathrm{base}}=R\,\vec r,\qquad
\vec v_{\mathrm{base}}=\dot R\,\vec r+R\,\vec v
$$

反向 `RotateFromBaseSystem` 用 $R^{\top},\dot R^{\top}$。

- **代码位置**：`src/base/coordsystem/AxisSystem.cpp:1088-1121`（入口）、`1516-1630`（正向）、`1645-1763`（反向）。
- **深度讲解**：`CompleteRotateToBase`（`AxisSystem.cpp:1545-1558`）逐分量展开 $\dot R$ 项——速度变换必须同时包含"坐标轴转动带来的表观速度"（$\dot R\vec r$）与"本系真实速度的旋转"（$R\vec v$），这是转动参考系速度合成的核心。反向实现（1668-1688 行）手工构造转置数组 `rotDataT`。`CalculateRotationMatrix` 的 GmatTime 重载退化到 A1Mjd（`AxisSystem.cpp:1765-1769`）。

### 8.2 CoordinateConverter::Convert 管线与 lastRotMatrix

- **公式**：两系换算 = `inCoord->ToBaseSystem`（旋转+平移，`coincident` 时免平移）→ 若基系统不同走 `ConvertFromBaseToBase` → `outCoord->FromBaseSystem`。记录最近旋转 $R_{\mathrm{last}}=R_2^{\top}R_1$（$R_1$：入系→基系，$R_2$：出系→基系），$\dot R_{\mathrm{last}}=\dot R_2^{\top}R_1+R_2^{\top}\dot R_1$。
- **代码位置**：`src/base/coordsystem/CoordinateConverter.cpp:270-497`（`Convert` A1Mjd 版：同系短路 291-297 行、基系分支 360-368 行、`lastRotMatrix` 395-413 行、`lastRotDotMatrix` 430-457 行、旋转矩阵导数 460-476 行）。
- **深度讲解**：`coincident = (origin 相同) || omitTranslation`（323-327 行）——原点相同即免平移，这是"纯旋转"换算的快速路径。`lastRotMatrix` 的推导：入系→基系 $R_1$、出系→基系 $R_2$，则出系 = $R_2^{\top}R_1\cdot$入系（基系中转），故 406-409 行算 $R_2^{\top}R_1$。`specifyRotMatrixDeriv` 开启时（460-476 行）输出 $\frac{d}{dX}(R_2^{\top}R_1)=\dot R_2^{\top}R_1+R_2^{\top}\dot R_1$ 供估计器（[CH15](../CH15-csalt-interop-tests.md) 的 CSALT 接口）使用。`GmatTime` 版本（500-728 行）逻辑同构。

### 8.3 ConvertFromBaseToBase：FK5↔ICRF

- **公式**：`ICRF→FK5`：$\vec x_{\mathrm{FK5}}=R_{\mathrm{ICRF\to FK5}}\vec x_{\mathrm{ICRF}}$；`FK5→ICRF`：$\vec x_{\mathrm{ICRF}}=R_{\mathrm{ICRF\to FK5}}^{\top}\vec x_{\mathrm{FK5}}$（位置与速度各乘一次，速度无附加项——偏置旋转是常值）。
- **代码位置**：`src/base/coordsystem/CoordinateConverter.cpp:901-951`（ICRF→FK5 921-930 行、FK5→ICRF 931-941 行）、`1019-1033`（`RotateFromICRFtoFK5` 公开接口）、`1047-1111`（矩阵生成）。
- **深度讲解**：916 行先调 `RotationMatrixFromICRFToFK5`（1047 行，含 1e-10 天缓存）；ICRF→FK5 用矩阵正序乘（923-929 行），FK5→ICRF 用转置乘（934-940 行）。速度分量同样只乘矩阵（无 $\dot R$ 项，且 1090 行显式把 `icrfToFK5Dot` 置零）——因为 ICRF 与 FK5 的差在 GMAT 的时间跨度内视为常值偏置。

### 8.4 CoordinateSystem：ToBaseSystem / FromBaseSystem（旋转+平移）

- **公式**：

$$
\vec x_{\mathrm{base}}=R\,\vec x+\vec r_{\text{origin}}-\vec r_{J2000\,\text{body}}\quad(\text{基系统为 ICRF 时 }\vec r \text{ 先乘 }R_{\mathrm{ICRF\to FK5}}^{\top})
$$

- **代码位置**：`src/base/coordsystem/CoordinateSystem.cpp:1158-1205`（`ToBaseSystem` Rvector 版）、`1288-1334`（Real* 版）、`2700-2755`（`TranslateToBaseSystem`）。
- **深度讲解**：`ToBaseSystem` 严格"先旋转后平移"（1172-1192 行）：`axes->RotateToBaseSystem` 得方向，`TranslateToBaseSystem` 把原点差补上；`coincident` 时跳过平移（1181-1192 行）。平移量 $\vec r_{\text{rif}}=\vec r_{\text{origin}}-\vec r_{J2000\,\text{body}}$（`CoordinateSystem.cpp:2715-2716`，两状态都来自 `GetMJ2000State`，即 FK5/地球系）；若本系基系统是 ICRF，则 2717-2728 行先用 $R_{\mathrm{ICRF\to FK5}}^{\top}$ 把平移量转到 ICRF 再相加。反向 `FromBaseSystem` 对称（先平移回原点、再反向旋转）。

### 8.5 CoordinateTranslation / CoordinateTransformation / TransformUtil

- **公式**：`TranslateOrigin`：$\vec x_{\text{新原点}}=\big(\vec x_{\text{旧原点}}-\vec x_{\text{新原点}}\big)_{\text{参考系}}+\vec x_{\text{旧}}$；`TransformState`：`RotateToBaseSystem → (基系不同则 ICRF↔FK5) → RotateFromBaseSystem`。
- **代码位置**：`src/base/coordsystem/CoordinateTranslation.cpp:57-75`（`TranslateOrigin`：差向量 62-63 行、`RotateFromBaseSystem` 68-69 行、加和 72 行）；`CoordinateTransformation.cpp:54-94`（`TransformState`：`RotateToBaseSystem` 58 行、基系分支 64-86 行、`RotateFromBaseSystem` 91 行）；`TransformUtil.cpp:61-149`（`TransformOrbitalState`：先化 Cartesian 92-115 行、`TranslateOrigin` 125-135 行、`TransformState` 144-147 行）。
- **深度讲解**：这三个工具构成"任意状态表示 × 任意坐标系"的完整换算链：`TransformUtil::TransformOrbitalState` 先统一到笛卡尔（用 `StateConversionUtil`，需要 μ/扁率/赤道半径，98-102 行），再按需平移（`ephemType` 支持 `"Spice"` 直读或 `"Spline"` 平滑历表）与旋转。`TranslateOriginSmoothedWithDerivatives`（`CoordinateTranslation.cpp:157-179`）额外输出对状态的偏导（恒零，因为原点状态只依赖时间）与对时间导数，供估计器。

## 九、EOP 数据流（EopFile）

### 9.1 文件读取与时间尺标链

- **公式**：EOP C04 行格式 `year month day mjd x y ut1_utc lod`（`EopFile.cpp:251`），内部时间戳统一为儒略日：`ut1UtcOffsets(:,0) = mjd + JD_NOV_17_1858`（2400000.5）；极移表 `polarMotion(:,0..3) = (mjd+2400000.5, x, y, lod)`；同时把 UTC 转 TAI 存 `taiTime`（263-265 行）。
- **代码位置**：`src/gmatutil/util/EopFile.cpp:176-342`（`Initialize`）。
- **深度讲解**：GMAT 内部 MJD 以 `JD_JAN_5_1941=2430000.0` 为参考（`GmatConstants.hpp:151`），而 EOP 文件用经典 MJD（参考 2400000.5），两者相差 29999.5 天——所有 `eop->GetPolarMotionAndLod(mjdUTC + offset)` 调用（`AxisSystem.cpp:2874`、`BodyFixedAxes.cpp:600`、`ITRFAxes.cpp:462`）都先加这个 `offset`。TAI 列用于 `GetUt1UtcOffset` 的二分插值定位（395-468 行）。

### 9.2 UT1-UTC 插值（含闰秒处理）

- **公式**：线性插值 $u(t)=u_i+\dfrac{t-t_i}{t_{i+1}-t_i}\big(u_{i+1}-u_i\big)$；若相邻表项间隔偏离 1 天超过 0.6 秒（闰秒日），先把差值按整天取整剔除（`errorInSec` 修正，`EopFile.cpp:435-437, 460-462`）。
- **代码位置**：`src/gmatutil/util/EopFile.cpp:387-478`（`GetUt1UtcOffset`）。
- **深度讲解**：UT1-UTC 是地球自转不规则性的直接度量（日长积分），闰秒日表项间隔为 86401 或 86399 秒，`EopFile.cpp:435-437` 用 `Round(errorInSec)` 把整秒跳变从插值斜率中剔除，避免闰秒处插值失真。搜索结果从文件尾向前（330-334 行预置 `lastIndex`），并缓存最近命中区间（`previousIndex`）加速连续调用。消费方：`TimeSystemConverter` 的 A1→UT1 换算，进而驱动 GMST（§2.7）与 ERA（§4.2）。

### 9.3 极移 x/y 插值与 LOD 步进

- **公式**：$x(t),y(t)$ 按时间线性插值；LOD 取区间左端表值（不插值——"Steve says not to interpolate lod"，`EopFile.cpp:556-558, 591-593`）。
- **代码位置**：`src/gmatutil/util/EopFile.cpp:511-604`（`GetPolarMotionAndLod`）。
- **深度讲解**：时间戳按 `utcJD = forUtcMjd + JD_NOV_17_1858`（517 行）统一；越界时取端点值（524-532、569-574 行）。x/y 线性插值（543-555、577-590 行）进入 §2.9 极移矩阵与 §4.2 的 $W$。LOD 的阶跃处理是精度权衡：LOD 变化率小（ms/日量级），插值收益低于复杂度。`ResetEopFile`（349-358 行）支持按 `Planet` 的 `EopFileName` 参数换文件（`Planet.cpp:263-264, 797-804`）。

## 十、天体定向（IAU 2000 α、δ、W 展开）

### 10.1 CelestialBody：IAU_SIMPLIFIED 线性展开

- **公式**（`CelestialBody.cpp:4305-4308`）：设 $d$ = 自 TDB 历元的儒略日数，$T=d/36525$（儒略世纪），定向参数向量 $\vec o=(\alpha_0,\alpha_1,\delta_0,\delta_1,W_0,W_1)$（度）：

$$
\alpha = \alpha_0+\alpha_1\,T,\qquad
\delta = \delta_0+\delta_1\,T,\qquad
W = W_0+W_1\,d,\qquad
\dot W = W_1\cdot\dot d
$$

- **代码位置**：`src/base/solarsys/CelestialBody.cpp:4275-4327`（`GetBodyCartographicCoordinates`）；参数索引 `CelestialBody.cpp:4471-4476`（`SPIN_AXIS_RA_CONSTANT` 等）。
- **深度讲解**：这就是 IAU 2000 报告（*Cartographic Coordinates and Rotational Elements of the Planets and Satellites: 2000*）中"简化"（linear-in-time）定向格式的代码化：北极赤经/赤纬随时间线性漂移、本初子午线经度 $W$ 以恒定速率 $W_1$ 旋转。`userDefined` 时 $d$ 相对 `orientationEpoch` 起算（4300-4301 行）。数据入口：`Planet` 构造按星表硬编码（见 `src/base/solarsys/Planet.cpp` 与各 `CelestialBody` 派生构造器中的 `orientation` 数组，参数见 `CelestialBody.cpp:4471-4476` 的 getter）。注意 α/δ 的 $T$ 是儒略世纪、$W$ 的 $d$ 是儒略日，量纲不同（IAU 报告原式即如此）。

### 10.2 Planet：Neptune 的 IAU_2002 特殊式与 Earth 分派

- **公式**（`Planet.cpp:291-301`，仅 Neptune + `IAU_2002` 源）：$N=357.85^\circ+52.316^\circ\,T$，$\dot N=0.0014323$（°/日，`Planet.cpp:296` 修正常量）：

$$
\alpha = \alpha_0+\alpha_1\sin N,\quad
\delta = \delta_0+\delta_1\cos N,\quad
W = W_0+W_1\,d-0.48\sin N,\quad
\dot W = W_1\dot d-0.48\,\dot N\cos N
$$

- **代码位置**：`src/base/solarsys/Planet.cpp:284-323`（`GetBodyCartographicCoordinates`：Neptune 分支 287-313 行、Earth 分派 314-319 行、默认 321-322 行）。
- **深度讲解**：Neptune 的磁场轴（即定向参考）偏离自转轴约 47°，IAU 2000 给出带 $\sin N/\cos N$ 的解析修正（$N$ 为海王星轨道近点角函数）。`rotationSrc` 默认值在构造器里按天体分派（`Planet.cpp:107-111`：地球 `FK5_IAU_1980`、海王星 `IAU_2002`、其余 `IAU_SIMPLIFIED`）。Earth 分支不在此计算——地球定向完全交给轴系层（FK5 五件套 + EOP，注释 316-318 行）。`Planet::Initialize` 顺带处理 `EopFileName` 覆盖（`Planet.cpp:263-264`）。

### 10.3 Moon：IAU 2002 谐波展开

- **公式**（`Moon.cpp:227-260`，地月系）：13 个中间角 $p_1\dots p_{13}$（线性于 $d$，`Moon.cpp:227-239`），北极与子午线为三角级数（单位度，$T$ 儒略世纪、$d$ 儒略日）：

$$
\begin{aligned}
\alpha &= 269.9949 + 0.0031\,T - 3.8787\sin p_1 - 0.1204\sin p_2 + 0.0700\sin p_3 - 0.0172\sin p_4 \\
&\qquad + 0.0072\sin p_6 - 0.0052\sin p_{10} + 0.0043\sin p_{13}\\
\delta &= 66.5392 + 0.0130\,T + 1.5419\cos p_1 + 0.0239\cos p_2 - 0.0278\cos p_3 + 0.0068\cos p_4 \\
&\qquad - 0.0029\cos p_6 + 0.0009\cos p_7 + 0.0008\cos p_{10} - 0.0009\cos p_{13}\\
W &= 38.3213 + 13.17635815\,d - 1.4\times10^{-12}d^2 + 3.5610\sin p_1 + 0.1208\sin p_2 - 0.0642\sin p_3\\
&\qquad + 0.0158\sin p_4 + 0.0252\sin p_5 - 0.0066\sin p_6 - 0.0047\sin p_7 - 0.0046\sin p_8\\
&\qquad + 0.0028\sin p_9 + 0.0052\sin p_{10} + 0.0040\sin p_{11} + 0.0019\sin p_{12} - 0.0044\sin p_{13}
\end{aligned}
$$

$\dot W$ 为对应余弦级数（`Moon.cpp:255-260`，主项 13.17635815°/日）。

- **代码位置**：`src/base/solarsys/Moon.cpp:208-317`（`GetBodyCartographicCoordinates`：地月系 223-277 行、火卫一/二 279-309 行）。
- **深度讲解**：月球天平动的 IAU 2002 解析表达（本质是物理天平动的傅里叶拟合），供 `LunaFixed` 在未选 DE 源时使用（`rotationSrc != DE_FILE` 的路径，`Moon.cpp:225-261` 的 `IAU_2002` 分支被注释但仍按该式执行）。火卫一/火卫二分支（281-303 行）含 $T^2$ 项（如 $W=35.06+1128.8445850d+8.864T^2-\dots$，290-291 行）。注意 `Wdot` 对火卫一/二尚未实现（292、301 行打印提示并返回 0）。

### 10.4 DeFile：天平动与章动的切比雪夫插值

- **公式**：DE 星历把月球天平动角（3 个）与章动（2 个）存为分段切比雪夫系数；插值式 $f(T_c)=\sum_{j=0}^{N-1}A_j\,C_j(T_c)$，$C_0=1,\ C_1=T_c,\ C_j=2T_cC_{j-1}-C_{j-2}$，归一化时间 $T_c=\frac{2(t-t_{\text{seg}})}{\Delta t_{\text{seg}}}-1$。
- **代码位置**：`src/base/solarsys/DeFile.cpp:809-864`（`GetAnglesAndRates`：TT/TDB 选择 813-827 行、`Interpolate_Libration(absJD, 12, angles, rates)` 834 行）、`1565-1654`（`Interpolate_Nutation`：归一化 1609/1627 行、递推 1646-1650 行）。
- **深度讲解**：`GetAnglesAndRates` 把 A1 时刻转 TT 或 TDB（`overrideTimeSystem` 开关，816-827 行）后交给切比雪夫插值。`Interpolate_Nutation` 展示标准递推（`Cp[j] = 2*Tc*Cp[j-1] - Cp[j-2]`，1648 行）与和式（1644-1650 行）。该章动数据（dPsi、dEps）在 GMAT 主流程中未被轴系使用（轴系章动走 2.4-2.6 的解析级数），但保留为 DE 数据访问能力；天平动角被 §3.3/§6.4 消费。

## 十一、公式索引表

| 公式 | 文件:行 | 所属类/函数 |
| --- | --- | --- |
| 岁差角 ζ,Θ,z（IAU-76，Vallado 3-56） | src/base/coordsystem/AxisSystem.cpp:2233-2242 | `AxisSystem::ComputePrecessionMatrix` |
| 岁差矩阵 PREC（Vallado 3-57） | src/base/coordsystem/AxisSystem.cpp:2244-2262 | `AxisSystem::ComputePrecessionMatrix` |
| 平黄赤交角 ε̄（Vallado 3-52） | src/base/coordsystem/AxisSystem.cpp:2379-2381 | `AxisSystem::ComputeNutationMatrix` |
| 平黄赤交角 ε̄（同式各历元系复制） | src/base/coordsystem/TODEcAxes.cpp:186-190；TOEEcAxes.cpp:144-148；MODEcAxes.cpp:181-182；MOEEcAxes.cpp:139-140 | 各轴系 `CalculateRotationMatrix/Initialize` |
| 章动基本角 l,l′,F,D,Ω（IAU-1980/1996） | src/base/coordsystem/AxisSystem.cpp:2369-2377, 2420-2447 | `AxisSystem::ComputeNutationMatrix` |
| Δψ/Δε 傅里叶级数（Vallado 3-60） | src/base/coordsystem/AxisSystem.cpp:2579-2613 | `AxisSystem::ComputeNutationMatrix` |
| 行星项 Δψp/Δεp（IAU-1996） | src/base/coordsystem/AxisSystem.cpp:2631-2674 | `AxisSystem::ComputeNutationMatrix` |
| 章动矩阵 NUT（Vallado 3-64） | src/base/coordsystem/AxisSystem.cpp:2697-2717 | `AxisSystem::ComputeNutationMatrix` |
| GMST（Vallado 3-45） | src/base/coordsystem/AxisSystem.cpp:2778-2806 | `AxisSystem::ComputeSiderealTimeRotation` |
| 分点方程 EqEq | src/base/coordsystem/AxisSystem.cpp:2788-2793 | `AxisSystem::ComputeSiderealTimeRotation` |
| 真恒星时 ST = R3(θAST) | src/base/coordsystem/AxisSystem.cpp:2808-2818 | `AxisSystem::ComputeSiderealTimeRotation` |
| 恒星时率 SṪ（ωE=7.292e-5(1−LOD/86400)） | src/base/coordsystem/AxisSystem.cpp:2884-2887 | `AxisSystem::ComputeSiderealTimeDotRotation` |
| 极移矩阵 PM = R2(−xp)R1(−yp) | src/base/coordsystem/AxisSystem.cpp:2940-2948 | `AxisSystem::ComputePolarMotionRotation` |
| ICRF↔FK5 Rodrigues 矩阵 | src/base/coordsystem/AxisSystem.cpp:3024-3044；CoordinateConverter.cpp:1068-1087；ICRFFile.cpp:268-287 | `AxisSystem/CoordinateConverter/ICRFFile::RotationMatrixFromICRFToFK5` |
| SPICE 帧旋转合成 R=RFK5←ICRF·R⊤ | src/base/coordsystem/AxisSystem.cpp:3085-3090 | `AxisSystem::CalculateSpiceFrameRotationMatrix` |
| 旋转+速度变换 v_base=Ṙr+Rv | src/base/coordsystem/AxisSystem.cpp:1545-1558（反向 1668-1688） | `AxisSystem::CompleteRotateToBase/FromBase` |
| 地球体固连 R=(PM·ST·NUT·PREC)⊤ | src/base/coordsystem/BodyFixedAxes.cpp:690-769 | `BodyFixedAxes::CalculateRotationMatrix`（地球分支） |
| 航天器体固连 R=D⊤, Ṙ=(−[ωB]×D)⊤ | src/base/coordsystem/BodyFixedAxes.cpp:464-512 | `BodyFixedAxes::CalculateRotationMatrix`（Spacecraft 分支） |
| 月球天平动 DCM（DE 源） | src/base/coordsystem/BodyFixedAxes.cpp:834-869 | `BodyFixedAxes::CalculateRotationMatrix`（月球分支） |
| IAU 简化 DCM R3⊤(π/2+α)R1⊤(π/2−δ)R3⊤(W) | src/base/coordsystem/BodyFixedAxes.cpp:906-1006 | `BodyFixedAxes::CalculateRotationMatrix`（其它天体） |
| 基本旋转 R1/R2/R3 与 Skew | src/base/coordsystem/ITRFAxes.cpp:340-422 | `ITRFAxes::R1/R2/R3/Skew` |
| ITRF 极移 W=R3(−s′)R2(xp)R1(yp) | src/base/coordsystem/ITRFAxes.cpp:486-487 | `ITRFAxes::CalculateRotationMatrix` |
| 地球自转角 ERA θ | src/base/coordsystem/ITRFAxes.cpp:488 | `ITRFAxes::CalculateRotationMatrix` |
| CIP 矩阵 CT(X,Y,s)（IAU2000/2006） | src/base/coordsystem/ITRFAxes.cpp:498-508 | `ITRFAxes::CalculateRotationMatrix` |
| ITRF→GCRF R=CT·R3(−θ)·W 与 Ṙ | src/base/coordsystem/ITRFAxes.cpp:511-516 | `ITRFAxes::CalculateRotationMatrix` |
| X,Y,s 插值（IAU_SOFA.DAT，9 阶 Lagrange） | src/base/coordsystem/IAUFile.cpp:176-219 | `IAUFile::GetIAUData` |
| 章动/行星系数表读取与倍乘 | src/base/coordsystem/ItrfCoefficientsFile.cpp:242-351, 458-501 | `ItrfCoefficientsFile::Initialize/GetNutationTerms/GetPlanetaryTerms` |
| MJ2000Eq 恒等 R=I3 | src/base/coordsystem/MJ2000EqAxes.cpp:138-140 | `MJ2000EqAxes::Initialize` |
| MJ2000Ec 固定黄赤交角 R1(ε0) | src/base/coordsystem/MJ2000EcAxes.cpp:123-131 | `MJ2000EcAxes::Initialize` |
| ICRF 恒等 R=I3 | src/base/coordsystem/ICRFAxes.cpp:234-244 | `ICRFAxes::CalculateRotationMatrix` |
| 天体惯性系 R3⊤(π/2+α)R1⊤(π/2−δ) | src/base/coordsystem/BodyInertialAxes.cpp:194-200 | `BodyInertialAxes::Initialize` |
| TOEEq R=PREC⊤NUT⊤（历元冻结） | src/base/coordsystem/TOEEqAxes.cpp:173-203 | `TOEEqAxes::Initialize` |
| TOEEc R=PREC⊤R1(−ε̄)R3(−Δψ)（历元冻结） | src/base/coordsystem/TOEEcAxes.cpp:158-190 | `TOEEcAxes::Initialize` |
| MOEEq R=PREC⊤（历元冻结） | src/base/coordsystem/MOEEqAxes.cpp:142-144 | `MOEEqAxes::Initialize` |
| MOEEc R=PREC⊤R1(−ε̄)（历元冻结） | src/base/coordsystem/MOEEcAxes.cpp:151-171 | `MOEEcAxes::Initialize` |
| MODEq R=PREC⊤（随历元） | src/base/coordsystem/MODEqAxes.cpp:185-187 | `MODEqAxes::CalculateRotationMatrix` |
| MODEc R=PREC⊤R1(−ε̄)（随历元） | src/base/coordsystem/MODEcAxes.cpp:184-214 | `MODEcAxes::CalculateRotationMatrix` |
| TODEq R=PREC⊤NUT⊤（随历元） | src/base/coordsystem/TODEqAxes.cpp:213-234 | `TODEqAxes::CalculateRotationMatrix` |
| TODEc R=PREC⊤R1(−ε̄)R3(−Δψ)（随历元） | src/base/coordsystem/TODEcAxes.cpp:200-232 | `TODEcAxes::CalculateRotationMatrix` |
| TEME R=PREC⊤NUT⊤R3(−Δψcos ε̄) | src/base/coordsystem/TEMEAxes.cpp:203-258；ComputeModEq 282-304 | `TEMEAxes::CalculateRotationMatrix/ComputeModEq` |
| 赤道面系三分支（TOD / 月球天平动 / IAU） | src/base/coordsystem/EquatorAxes.cpp:233-443 | `EquatorAxes::CalculateRotationMatrix` |
| R/V/N 对象参考轴系 | src/base/coordsystem/ObjectReferencedAxes.cpp:946-1142 | `ObjectReferencedAxes::CalculateRotationMatrix` |
| GSE 基向量与导数 | src/base/coordsystem/GeocentricSolarEclipticAxes.cpp:242-283 | `GeocentricSolarEclipticAxes::CalculateRotationMatrix` |
| GSM 偶极 + 五件套合成 | src/base/coordsystem/GeocentricSolarMagneticAxes.cpp:296-522 | `GeocentricSolarMagneticAxes::ComputeDipoleEarthFixed/CalculateRotationMatrix` |
| LAC triad R=R1R2, Ṙ=Ṙ1R2+R1Ṙ2 | src/base/coordsystem/LocalAlignedConstrainedAxes.cpp:984-1067 | `LocalAlignedConstrainedAxes::CalculateRotationMatrix` |
| 站心 RFT 与 R=RIF·RFT | src/base/coordsystem/TopocentricAxes.cpp:324-325, 359-458 | `TopocentricAxes::CalculateRotationMatrix/CalculateRFT` |
| SpiceAxes 帧旋转 | src/base/coordsystem/SpiceAxes.cpp:407-416 | `SpiceAxes::CalculateRotationMatrix` |
| 转换器管线与 Rlast=R2⊤R1 | src/base/coordsystem/CoordinateConverter.cpp:360-413（导数 460-476） | `CoordinateConverter::Convert` |
| FK5↔ICRF 基系状态转换 | src/base/coordsystem/CoordinateConverter.cpp:916-941；RotateFromICRFtoFK5 1019-1033 | `CoordinateConverter::ConvertFromBaseToBase/RotateFromICRFtoFK5` |
| 坐标系旋转+平移 ToBaseSystem | src/base/coordsystem/CoordinateSystem.cpp:1172-1192；平移 2715-2730 | `CoordinateSystem::ToBaseSystem/TranslateToBaseSystem` |
| 原点平移 TranslateOrigin | src/base/coordsystem/CoordinateTranslation.cpp:62-72 | `CoordinateTranslation::TranslateOrigin` |
| 轴系状态变换 TransformState | src/base/coordsystem/CoordinateTransformation.cpp:58-91 | `CoordinateTransformation::TransformState` |
| 任意状态换算 TransformOrbitalState | src/base/coordsystem/TransformUtil.cpp:92-147 | `TransformUtil::TransformOrbitalState` |
| EOP 读表与时间戳统一 | src/gmatutil/util/EopFile.cpp:206-342 | `EopFile::Initialize` |
| UT1-UTC 插值（闰秒修正） | src/gmatutil/util/EopFile.cpp:429-463 | `EopFile::GetUt1UtcOffset` |
| 极移 x/y 插值、LOD 步进 | src/gmatutil/util/EopFile.cpp:543-594 | `EopFile::GetPolarMotionAndLod` |
| 天体定向线性展开 α,δ,W（IAU 简化） | src/base/solarsys/CelestialBody.cpp:4305-4308 | `CelestialBody::GetBodyCartographicCoordinates` |
| Neptune IAU_2002（N 项修正） | src/base/solarsys/Planet.cpp:291-301 | `Planet::GetBodyCartographicCoordinates` |
| 时角/GMST（度制） | src/base/solarsys/Planet.cpp:356-359 | `Planet::GetHourAngle` |
| 月球 IAU2002 谐波展开 | src/base/solarsys/Moon.cpp:227-260 | `Moon::GetBodyCartographicCoordinates` |
| 天平动角/章动切比雪夫插值 | src/base/solarsys/DeFile.cpp:809-864（GetAnglesAndRates）、1565-1654（Interpolate_Nutation） | `DeFile` |
