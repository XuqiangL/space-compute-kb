# 第12章 轨道估计滤波与测量模型数学

> 本章范围：GMAT 轨道确定（Orbit Determination）与测量仿真的**公式级**解析，覆盖
> `plugins/EstimationPlugin/src/base/` 下的 `signal/`（光时解、测站/观测坐标系旋转、距离/距离变化率矢量）、`measurementmodel/`（`MeasureModel` 测量模型基类）、`adapter/`（Range/RangeRate/DSN/Doppler/方位角/仰角/RA/DEC/GPS 适配器）、`estimator/`（`BatchEstimator` 加权最小二乘正规方程与估计雅可比）、`errormodel/`（`ErrorModel` 噪声/偏置），
> `plugins/ExtendedKalmanFilterPlugin/src/base/` 下的 `EKF/`（平方根 EKF 五方程）、`noise/`（SNC/线性/FOGM 过程噪声模型）、`estimatedparam/`，
> 以及 `plugins/GeometricMeasurementPlugin/src/base/measurement/`（四个几何测量模型）。
> 术语与类/调用链背景见 [第13章](../CH13-plugins-a.md)（13.6 EstimationPlugin、13.8 ExtendedKalmanFilterPlugin），本章只提炼公式，不重复类图与数据流。
> 本仓库为 depth-1 克隆（commit ce6eba2）；所有行号均经 read 工具核实。`CoreMeasurement` 基类头文件不在本克隆内（`GeometricMeasurementPlugin` 的 4 个派生类自带的 `Evaluate()` 实现了全部几何公式，可直接引用）。

---

## 〇、测量与估计的两条主线

GMAT 的轨道确定后端包含两条数学主线，本章依次展开：

1. **测量模型链**（正向）：观测历元 → 把参与者同步到历元 → 光时迭代解出收发时刻 → 惯性系距离矢量 → 地固/站心坐标旋转 → 介质修正（对流层/电离层）与相对论/ET-TAI 修正 → 适配器按测量类型合成 C 值（km、km/s、Hz、RU、度）→ 加噪声/偏置。
2. **估计器链**（反向）：O−C 残差 → 测量雅可比（含 STM 传播与坐标换算）→ 信息矩阵累积 → 正规方程求解状态修正（批估计），或逐历元 Kalman 增益/协方差更新（EKF）。

两条主线的交汇点：**测量残差** $y=O-C$ 与**测量偏导数矩阵** $H=\partial C/\partial X$。测量偏导数全部由 `SignalBase` 的 `GetRangeDerivative/GetRangeRateDerivative/GetCDerivativeVector` 系列按**解析式**给出（差分只出现在 RangeRate 的两点式与部分光行差处理中），因此本章对雅可比的来源也逐条给出公式。

---

## 一、信号链路与光时/坐标系数学（`signal/`、`measurementmodel/`）

### 1. 惯性系距离矢量与坐标系原点平移（GMT MathSpec Eq. 6.10/6.12）
- **公式**：
  设 $t_T,t_R$ 为收发时刻（光时解后），$\mathbf{r}_t,\mathbf{r}_r$ 为参与者位置（各自坐标系的 MJ2000 状态），$\mathbf{R}_t^{SSB},\mathbf{R}_r^{SSB}$ 为收发坐标系原点相对太阳系质心（SSB）的位置，则
  $$\mathbf{j2kOriginSep}=\mathbf{R}_r^{SSB}(t_R)-\mathbf{R}_t^{SSB}(t_T)$$
  $$\boldsymbol{\rho}_{in}=\mathbf{r}_r+\mathbf{j2kOriginSep}-\mathbf{r}_t \quad(\text{Eq. 6.12})$$
  $$\mathbf{disp}=\big[\mathbf{R}_{prop}^{SSB}(t_R)-\mathbf{R}_{SSB}(t_R)\big]-\big[\mathbf{R}_{prop}^{SSB}(t_T)-\mathbf{R}_{SSB}(t_T)\big],\qquad \boldsymbol{\rho}_I=\boldsymbol{\rho}_{in}-\mathbf{disp}\quad(\text{Eq. 6.10})$$
  其中 $\mathbf{R}_{prop}^{SSB}$ 是**力模型原点**（propOrigin，典型为地球质心）相对 SSB 的状态，$\mathbf{R}_{SSB}$ 为 SSB 自身状态；$\mathbf{disp}$ 吸收"力模型原点在光时内的运动"（含地面站链路中地球相对 SSB 的 ~30 km/s 运动）对距离矢量的影响。纯航天器链路中收发两端各自使用本端力模型原点（1218-1236），一端为地面站时两端共用航天器的力模型原点（1237-1258）。
- **代码位置**：`plugins/EstimationPlugin/src/base/signal/SignalBase.cpp:1190-1268`（`CalculateRangeVectorInertial()`；核心赋值 1206-1212 与 1259-1260）。
- **深度讲解**：`SignalBase` 是单段信号（leg）的载体，`SignalData` 里同时保存参与者状态（`tLoc/rLoc/tVel/rVel`，在参与者自身坐标系，如"卫星 MJ2000 以力模型原点为原点"）与坐标系原点状态（`tOStateSSB/rOStateSSB`）。把两者相加才能得到 SSB 下的绝对位置；距离矢量必须在**同一坐标系**下相减，故先做原点平移再做差。代码注释明确标注了 MathSpec 方程号，是本章公式与实现一一对应的锚点：

```cpp
// SignalBase.cpp:1206-1212  计算 SSB 下的原点位置，再做坐标平移的矢量差
theData.tOStateSSB = origin1->GetMJ2000PrecState(theData.tPrecTime)
                   - ssb->GetMJ2000PrecState(theData.tPrecTime);   // 发端原点相对 SSB
theData.rOStateSSB = origin2->GetMJ2000PrecState(theData.rPrecTime)
                   - ssb->GetMJ2000PrecState(theData.rPrecTime);   // 收端原点相对 SSB
theData.j2kOriginSep = (theData.rOStateSSB.GetR() - theData.tOStateSSB.GetR()); // 原点差
theData.rangeVecInertial = theData.rLoc + theData.j2kOriginSep - theData.tLoc;  // Eq.6.12
```

### 2. 光照时间（光时）迭代求解
- **公式**：固定测量时刻（默认收端 $t_R$ 固定，`epochIsAtEnd=true`），迭代求解发端时刻 $t_T$：
  $$\Delta t = \frac{|\boldsymbol{\rho}_{SSB}| + \Delta_{rel}}{c},\qquad t_T = t_R - \Delta t$$
  迭代判据 $|\Delta t_{k+1}-\Delta t_k|<\epsilon$（$\epsilon=1.0\times10^{-12}\,\text{s}$，等价于约 0.3 mm 距离精度），最多 10 次。
- **代码位置**：`plugins/EstimationPlugin/src/base/signal/PhysicalSignal.cpp:1811-1909`（`GenerateLightTimeData()`；容差 1822、初始位移 1832-1837、迭代循环 1859-1899）。
- **深度讲解**：光时迭代是"固定一端、用传播器克隆把另一端步进到候选时刻"的定点迭代（`MoveToEpoch` + `StepParticipant`，见 `SignalBase.cpp:2054-2272`、`2357-2569`）。每次迭代：
  1. `MoveToEpoch(atEpoch + deltaT/SECS_PER_DAY, !epochAtReceive, false)` 把非固定端传播到候选时刻（`PhysicalSignal.cpp:1865`）；
  2. 重新计算 SSB 下位移 $|\mathbf{r}_r^{SSB}-\mathbf{r}_t^{SSB}|$（1870-1873）；
  3. 若启用相对论修正，加入 `RelativityCorrection()`（1881-1885）；
  4. 用新 $\Delta R$ 更新 $\Delta T$（1887-1890），循环直到 $\Delta E$（当前收发时刻差）与 $\Delta T$ 之差小于容差。
  迭代结束后重算惯性/观测系距离矢量（1904-1906）。传播器克隆由 `MeasureModel::SetPropagators()` 分配（`MeasureModel.cpp:848-926`），`StepParticipant` 还会同步 STM（2491-2507），保证偏导链与光时一致。

```cpp
// PhysicalSignal.cpp:1859-1890  光时定点迭代核心
while ((GmatMathUtil::Abs(deltaE - deltaT) > timeTolerance) && (loopCount < 10))
{
   MoveToEpoch(atEpoch + deltaT / GmatTimeConstants::SECS_PER_DAY,
               !epochAtReceive, false);                    // 步进非固定端到候选时刻
   deltaE = (epochAtReceive ? -1.0 : 1.0) *
            (theData.rPrecTime - theData.tPrecTime).GetTimeInSec();  // 当前收发时刻差
   displacement = rLocSSB - tLocSSB;                       // SSB 下位移 (Eq.6.12)
   if (useRelativity) relCorrection = RelativityCorrection(...);    // 相对论修正
   deltaR = displacement.GetMagnitude() + relCorrection;   // 光程 = 几何距离 + 相对论
   deltaT = (epochAtReceive ? -1.0 : 1.0) * deltaR /
            (GmatPhysicalConstants::SPEED_OF_LIGHT_VACUUM / 1000.0); // km/s 换算
   ++loopCount;
}
```

### 3. 距离变化率矢量（含测站速度项）
- **公式**：距离变化率矢量 = 收端速度 − 原点速度差 − 发端速度：
  $$\dot{\boldsymbol{\rho}}_{in}=\mathbf{v}_r-\dot{\mathbf{j2kOriginSep}}-\mathbf{v}_t$$
  其中 $\dot{\mathbf{j2kOriginSep}}=\dot{\mathbf{R}}_t^{SSB}(t_T)-\dot{\mathbf{R}}_r^{SSB}(t_R)$（两原点相对 SSB 的速度差）。转到观测系时计及坐标系旋转的时间导数：
  $$\dot{\boldsymbol{\rho}}_{obs}=\dot{R}_{Obs,j2k}\,\boldsymbol{\rho}_{in}+R_{Obs,j2k}\,\dot{\boldsymbol{\rho}}_{in}$$
- **代码位置**：`plugins/EstimationPlugin/src/base/signal/SignalBase.cpp:1324-1352`（`CalculateRangeRateVectorObs()`；1332-1339、1348）。
- **深度讲解**：这是"测站速度项"的源头——地面站随地球自转的速度（由 `GetMJ2000PrecVelocity` 从地固系旋转求出，隐含在 $R_{j2k}$ 的时间导数中），因此即使卫星静止，测距率也不为零（地球自转造成视线变化）。`rangeRateVecObs` 由 `RDot_Obs_j2k`（观测系相对惯性系的旋转矩阵导数）与 `R_Obs_j2k` 两项合成，等价于对 $\boldsymbol{\rho}_{obs}=R\,\boldsymbol{\rho}_{in}$ 求全导数。该矢量被 `RangeRateAdapterKps`（两点差分）与 `GeometricRangeRate`（直接投影）两类测距率消费。

### 4. 测站/观测坐标系旋转矩阵链（地固→惯性→站心 SEZ）
- **公式**：信号初始化时按参与者类型建立 4 个坐标系句柄 `tcs/rcs/ocs/j2k`，其中 `ocs` 是站心 **Topocentric（SEZ：南-东-天）** 坐标系，`j2k` 是 MJ2000 惯性系；随后在每个需要旋转的时刻调用 `CoordinateConverter` 取旋转矩阵：
  $$R_{j2k,1}=M_{tcs\to j2k},\quad R_{j2k,2}=M_{rcs\to j2k},\quad R_{Obs,j2k}=M_{j2k\to ocs}$$
  对地面站，`rcs`（或 `tcs`）取站的**地固（BodyFixed）坐标系**（`BodyFixedPoint::GetBodyFixedCoordinateSystem()`），因此 `rJ2kRotation` 就是**地固→惯性（MJ2000）**的旋转矩阵，其时间导数 `rJ2kRotationDot` 隐含地球自转角速度 $\boldsymbol{\omega}_\oplus$；双星情形（crosslink）下所有旋转矩阵取单位阵 $I_{33}$、旋转导数取零阵。
- **代码位置**：`plugins/EstimationPlugin/src/base/signal/SignalBase.cpp:968-1140`（`InitializeSignal()` 建系）、`1933-2033`（`UpdateRotationMatrix()`；地面站分支 1956-2012、双星分支 2013-2032）。
- **深度讲解**：坐标系链是本章所有"测站"公式的地基：
  1. **地固→惯性**：`converter.Convert(epoch, dummyIn, rcs, dummyOut, j2k)` 得到 $R_{j2k,Receiver}$（`SignalBase.cpp:1966-1971`），再转一次得到反向 $R_{rcs\leftarrow j2k}$ 及其时间导数（1970-1971）；
  2. **惯性→站心**：`converter.Convert(epoch, dummyIn, j2k, dummyOut, ocs)` 得到 $R_{Obs,j2k}$ 与 $\dot R_{Obs,j2k}$（2000-2002）；
  3. 观测系距离矢量 $\boldsymbol{\rho}_{obs}=R_{Obs,j2k}\boldsymbol{\rho}_{in}$（`SignalBase.cpp:1306`），SEZ 第三分量就是仰角方向。
  测角适配器直接复用这条链：`bfRange = rJ2kRotation * lssb`（`AngleAdapterDeg.cpp:625`）把惯性视线转到地固系，再经 `R_Obs_bf` 转到站心系（690）。

```cpp
// SignalBase.cpp:1966-1971  地面站分支：取地固→惯性旋转矩阵及其时间导数
converter.Convert(itsEpoch, dummyIn, rcs, dummyOut, j2k);      // 地固→MJ2000
R_j2k_Receiver = converter.GetLastRotationMatrix();
converter.Convert(itsEpoch, dummyIn, j2k, dummyOut, rcs);      // MJ2000→地固（反向）
theData.rJ2kRotation    = converter.GetLastRotationMatrix();   // 地固→惯性旋转
theData.rJ2kRotationDot = converter.GetLastRotationDotMatrix();// 旋转导数（含地球自转）
```

### 5. 相对论（光行时）修正
- **公式**（Moyer/GTDS 形式）：对每个启用天体，设 $\mathbf{r}_1,\mathbf{r}_2$ 为收发点在**该天体局部惯性系**中的位置（$r_i=|\mathbf{r}_i|$），$r_{12}=|\mathbf{r}_2-\mathbf{r}_1|$，$c$ 为光速（km/s），$\gamma=1$，则
  $$\Delta_{rel}=\sum_{planets}\frac{(1+\gamma)\,\mu_{planet}}{c^2}\,\ln\frac{r_1+r_2+r_{12}}{r_1+r_2-r_{12}}$$
  对太阳（光路穿过其引力势阱）额外在分子/分母加 $\frac{(1+\gamma)\mu}{c^2}$ 项（`term1`），避免对数奇异。
- **代码位置**：`plugins/EstimationPlugin/src/base/signal/PhysicalSignal.cpp:2664-2731`（`RelativityCorrection()`；`term1` 2701、太阳分支 2703-2706、一般天体 2707-2710）。
- **深度讲解**：修正量纲为 km，直接加进光时迭代的 $\Delta R$（见条目 2）与最终 C 值。实现遍历 `solarSystem->GetBodiesInUse()`，对每个天体在 $t_T,t_R$ 分别取位置，把 SSB 坐标平移到天体局部系再计算 $r_1,r_2,r_{12}$。`useRelativity` 由 `AddCorrection("…","Relativity")` 开启（`PhysicalSignal.cpp:2600-2620`），并把结果写入 `theData.corrections`（2714-2725），供适配器按 `correctionTypes=="Range"` 汇总。

### 6. ET−TAI 修正
- **公式**（Moyer Eq. 2-23，p.2-14）：对参与者 $P$ 在时刻 $t$ 计算
  $$\text{ET}-\text{TAI}=32.184+\frac{2}{c^2}\dot{\mathbf{R}}_{EM/\odot}\cdot\mathbf{R}_{EM/\odot}+\frac{1}{c^2}\dot{\mathbf{R}}_{EM/SSB}\cdot\mathbf{R}_{E/EM}+\frac{1}{c^2}\dot{\mathbf{R}}_{E/SSB}\cdot\mathbf{R}_{P/E}+(\text{木/土星项})+\frac{1}{c^2}\dot{\mathbf{R}}_{\odot/SSB}\cdot\mathbf{R}_{EM/\odot}$$
  对航天器参与者再加 Moyer Eq. 2-24 项 $P_{sat}=\frac{2}{c^2}\dot{\mathbf{R}}_{P/E}\cdot\mathbf{R}_{P/E}$。信号腿的修正量为发收两端之差乘光速：
  $$\Delta_{ETTAI}=(ET_{TAI}(t_T)-ET_{TAI}(t_R))\cdot c\cdot10^{-3}\ (\text{km})$$
- **代码位置**：`plugins/EstimationPlugin/src/base/signal/PhysicalSignal.cpp:2735-2855`（`ETminusTAI()`；主式 2824-2829、卫星项 2844-2845），合成在 `ModelSignal()` 462-477（`ettaiCorrection` 469）。
- **深度讲解**：ET−TAI 本质是广义相对论时标差（地球钟在太阳系引力场与运动中的速率差异），对深空测距（精度到米级）必须考虑。实现临时构造"地月质心"（`Barycenter`，2747-2752），取太阳/地球/月/木/土相对 SSB 的位置速度，按 Moyer 公式逐项点乘。注意 `muSun` 等常数读法有个已知的复制粘贴（2808-2811 都读 Earth 的参数 ID），但数值上取自太阳系配置，不影响公式结构。该修正只对地面站→卫星类测量启用（`useETTAI`）。

### 7. 介质修正：对流层与电离层（含仰角门限）
- **公式**：站心 SEZ 下视线仰角
  $$el=\arcsin\big((R_{Obs,j2k}\,\hat{\boldsymbol{\rho}})_z\big),\qquad R_{Obs,j2k}=M_{j2k\to ocs}$$
  仅当 $el>\epsilon=10^{-8}\,\text{rad}$ 时计算修正；总修正为（单位 m、rad、s 三元组）：
  $$\Delta_{media}=[\Delta_{tropo}(f,|\boldsymbol{\rho}|,el,t)+\Delta_{iono}(f,\mathbf{r}_1^{EBF},\mathbf{r}_2^{EBF},t_1,t_2)]$$
  其中对流层 `TroposphereCorrection()` 调用所选模型（`Troposphere` 插件类，气象输入来自测站的温度/气压/湿度/波长/仰角/斜距，见 3013-3089）；电离层 `IonosphereCorrection()` 先把收发位置由 SSB 惯性系经 $R_{g,j2k}$ 转到**地球固连系**再交给 `Ionosphere` 模型（3106-3226）。角测量使用 `Troposphere-Elev`/`Ionosphere-Elev` 修正类型（弧度），测距使用 `Troposphere`/`Ionosphere`（km）。
- **代码位置**：`plugins/EstimationPlugin/src/base/signal/PhysicalSignal.cpp:2876-2996`（`MediaCorrection()`；仰角 2900-2902、对流层 2908、电离层 2955、缓存 2942-2959）。
- **深度讲解**：介质修正是"信号腿"级（每条腿一次），并带**电离层缓存**（`SignalDataCache`，以 strand/频率/收发时刻为键，2942-2959）——多普勒 E/S 两条路径在同一频率与相近时刻复用结果，避免重复积分。电离层的坐标链（3150-3176）把 SSB 位置先减地球质心（得到地球惯性系）再用 $R_{g,j2k}$ 转到地固系，是条目 4 旋转链在介质模型里的复用。对流层/电离层本体（`Troposphere`、`Ionosphere` 类）的精细公式属模型插件内部，本章只锚定其入口与输入合成。

### 8. 视线可行性检查（仰角、掩星、HORP）
- **公式**：对含地面站的测量，站心 SEZ 下的仰角
  $$el=\arcsin(\hat{\boldsymbol{\rho}}_{sez,z})\cdot\frac{180}{\pi}\ (\text{deg}),\qquad \text{feasible}\iff el-minElevationAngle>0$$
  双星（crosslink）测量用射线-中心体几何检查（`TestSignalBlockedBetweenTwoParticipants`，掩星）与射线最低高度检查（`TestHeightOfRayPath`，HORP）。
- **代码位置**：`plugins/EstimationPlugin/src/base/signal/PhysicalSignal.cpp:485-597`（`ModelSignal()` 内可行性判定 487-597）；`plugins/StationPlugin/src/base/station/GroundStation.cpp:1466-1485`（`IsValidElevationAngle()`，仰角 1474-1476）。
- **深度讲解**：可行性是数据编辑链的第一道闸门：不可见（`"B"`）、HORP（`"H"`）、ramp 越界（`"R"`）的观测在 `Estimator::CalculateResiduals` 里被计数剔除（`Estimator.cpp:4256-4287`）。`feasibilityValue` 存仰角（度），供报告文件使用。注意仿真（`forSimulation=true`）才做掩星检查，估计模式默认不做（`PhysicalSignal.cpp:552-575` 有 `if (forSimulation)` 门），因为掩星会破坏偏导的连续性；估计时若显式要求 HORP 则执行（580-597）。

---

## 二、测量适配器公式（`adapter/`）

### 9. 测距 C 值合成（RangeAdapterKm）
- **公式**：对信号路径第 $i$ 条腿累加（单位 km）：
  $$C=\sum_{legs}\Big(|\boldsymbol{\rho}_{in}|+\sum_{j:\ type_j=\text{Range}}corr_j\Big)+\sum_{legs}(t_{Delay}+r_{Delay})\cdot c\cdot10^{-3}$$
  其中 $corr_j$ 覆盖相对论、ET-TAI、对流层、电离层（`correctionTypes=="Range"`）；硬件延迟（收发两端，秒）乘光速换算成 km。可选加乘子/噪声/偏置：
  $$C'\ =\ M\cdot C\ +\ \underbrace{\mathcal{N}(0,\sigma_{noise})}_{\text{if }addNoise}\ +\ \underbrace{b\ \text{或 }b_{pass}(t)}_{\text{if }addBias}$$
- **代码位置**：`plugins/EstimationPlugin/src/base/adapter/RangeAdapterKm.cpp:380-833`（`CalculateMeasurement()`；光程累加 573-575、修正累加 578-585、硬件延迟 588-591、乘子 716、高斯噪声 728、偏置 745-752）。
- **深度讲解**：`RangeAdapterKm` 是测距类适配器的公共实现（`DSNRangeAdapter/GNRangeAdapter/BRTSRangeAdapter/DopplerAdapter` 都继承或调用它）。C 值=光时解出的几何距离 + 各修正 + 硬件延迟折算，全部在适配器层汇总（信号层只把原始量写进 `SignalData`）。噪声注入用 `RandomNumber::Instance()->Gaussian(0.0, sigma)`（零均值白噪声），偏置分两类：**常数偏置** `measurementBias[i]` 与 **pass 偏置** `measErrorModel->GetPassBias(epochGT)`（按弧段分段常数，见条目 20）。`rangeOnly` 标志使 Doppler 的中间路径只取 C 值不加噪声（721）。

### 10. DSN 顺序测距（RU 换算、解模糊、斜坡积分）
- **公式**：DSN 测距单位是 Range Unit（RU），由往返光行时与频率因子换算：
  $$C_{RU}=\begin{cases}F(f_{uplink})\cdot\tau_{RT},&\text{恒频}\\ \displaystyle\int_{t_1}^{t_3} F(f_{ramp}(\tau))\,d\tau,&\text{斜坡表}\end{cases},\qquad \tau_{RT}=\frac{C_{km}}{c_{km/s}}$$
  频率因子（Moyer Eq. 13-110）：
  $$F(f)=\begin{cases}f/2,&S\text{ 波段}\\ f\cdot 221/1498,&X\text{ 波段}\end{cases}$$
  斜坡积分按段梯形累加：每段 $\Delta=((F(f_0)+F(f_1))/2-F(f_{base}))\cdot\Delta t$，$f_1=f_0+\dot f\,\Delta t$。观测值模糊度解算（`ObservationDataCorrection`）：$O'=O+N\cdot M$，$N=\lfloor(C-O)/M+0.5\rfloor$，$M$ 为 `rangeModulo`（RU）。
- **代码位置**：`plugins/EstimationPlugin/src/base/adapter/DSNRangeAdapter.cpp:377-589`（`CalculateMeasurement()`；乘子 431、km→RU 438/442、恒频 470、斜坡 453）；`GetFrequencyFactor()` 845-889（S 855、X 863）；`IntegralRampedFrequency()` 906-1030（段梯形 1000-1020）；解模糊在 `plugins/EstimationPlugin/src/base/estimator/Estimator.cpp:4032-4038`。
- **深度讲解**：RU 体系的关键是**相位测距的模糊度**：相位观测量只能测一个码周期内的相位，`rangeModulo`（RU 数）给出整周数；估计/仿真首遍迭代用计算值 $C$ 与观测值 $O$ 的差解出整周数 $N$ 并修正观测值（`Estimator.cpp:4235-4240` 只对 `DSN_SeqRange/DSN_PNRange` 且 `iterationsTaken==0` 执行一次）。斜坡表积分从 `end_interval` 向前逐段回溯（`DSNRangeAdapter.cpp:1000-1019`），`f_dot` 为斜坡率（Hz/s）。

```cpp
// DSNRangeAdapter.cpp:1000-1019  斜坡频率积分（梯形累加，从接收时刻向前回溯）
for (Integer i = end_interval; dt > 0; --i)
{
   if (i == end_interval)                       // 末段：只积到 t1
      interval_len = (t1 - (*rampTB)[i].epochGT).GetTimeInSec();
   else                                         // 中间段：整段积分
      interval_len = ((*rampTB)[i+1].epochGT - (*rampTB)[i].epochGT).GetTimeInSec();
   f0 = (*rampTB)[i].rampFrequency;             // 段首频率
   f_dot = (*rampTB)[i].rampRate;               // 斜坡率 Hz/s
   if (dt < interval_len)                       // 截断最后一段
   {  f0 = (*rampTB)[i].rampFrequency + f_dot*(interval_len - dt);
      interval_len = dt; }
   f1 = f0 + f_dot*interval_len;                // 段末频率（线性斜坡）
   // value1 = ((F(f0)+F(f1))/2 - F(f_base))*interval_len   （1020 行）
}
```

### 11. 测距率（两点差分，含测站速度）
- **公式**：在基历元与基历元偏移 `dopplerInterval` 处各算一次单向距离，中心差分：
  $$\dot{\rho}=\frac{\rho(t+\Delta t)-\rho(t)}{\Delta t},\qquad \Delta t=\text{dopplerInterval}$$
  偏导数同样差分：$\partial\dot\rho/\partial X=(\partial\rho_2/\partial X-\partial\rho_1/\partial X)/\Delta t$。
- **代码位置**：`plugins/EstimationPlugin/src/base/adapter/RangeRateAdapterKps.cpp:449-514`（`CalculateMeasurement()`；两次 `CalculateMeasurementAtOffset` 455-457、单向距离 476-477、差分 485）；偏导 530-657（差分式 570-571、587-588、619-620）。
- **深度讲解**：`RangeRateAdapterKps` 通过 `forStrand` 与 `atTimeOffset` 复用 `MeasureModel::CalculateMeasurement`（`MeasureModel.cpp:1416-1418` 的 `atTimeOffset` 参数，偏移历元见 1499-1503），两个"strand"各自独立完成光时解。这是**差分测距率**（与条目 42 的直接投影测距率、条目 12 的相位多普勒三套测速模型并存）。偏导差分与 C 值差分共用同一 `dopplerInterval`，保证 $H$ 与 $C$ 的相容性。`PointRangeRateAdapterKps` 是它的单点变体（`PointRangeRateAdapterKps.cpp:353`）。

### 12. 多普勒频移（E/S 双路径，DSN_TCP）
- **公式**：E 路径（End path，测量时刻 $t_3$）与 S 路径（Start path，提前 `dopplerCountInterval`）各算一个往返 C 值，转成光行时差 $\delta t=t_E-t_S$，再乘转发比与上行频率：
  $$C_{Hz}=-\alpha\,f_{up}\cdot\frac{T_c-\delta t}{T_c}\qquad(\text{恒频}),\qquad
  C_{Hz}=-\alpha\,\frac{1}{T_c}\int_{t_1}^{t_1+T_c-\delta t}f_{ramp}(\tau)\,d\tau\qquad(\text{斜坡})$$
  其中 $\alpha=\prod\alpha_{transponder}$ 为总转发比（S 波段 240/221、X 波段 880/749，`DopplerAdapter.cpp:1497-1511`），$T_c=\text{dopplerCountInterval}$。乘子 $M_E=M_S=\alpha f_{up}/(T_c\,c)$ 把 km 差转 Hz（899-900）。修正项 $corr=\alpha\,(corr_E-corr_S)/T_c$（1003）。偏导按链式法则合成：$\partial C/\partial X=M_E\,\partial\rho_E/\partial X-M_S\,\partial\rho_S/\partial X$（1349）。
- **代码位置**：`plugins/EstimationPlugin/src/base/adapter/DopplerAdapter.cpp:723-1119`（E 路径 777-780、S 路径 817-822、乘子 899-900、光行时 903-904、差分 963、斜坡 981、恒频 999、修正 1003、离子/对流层贡献 1061-1064）；偏导 1135-1380（合成式 1349）。
- **深度讲解**：多普勒的物理量是**载波相位积分**：接收机在计数间隔内累计的周数 $f\cdot T_c$，与转发信号到达时刻差的乘积。实现把"两段光行时之差"当作核心可观测量，符号约定：下行链路（地面发射→星上转发→地面接收）使 $\delta t<0$ 时接收频率高于上行频率，公式带负号。`measDataE.value[0]` 减去 2 倍电离层修正（779-780）是因为双程信号穿电离层两次；S 路径再除 `GetMultiplierFactor()`（821）恢复满程值。斜坡情形调用 `IntegralRampedFrequency(t1TE, interval - dtdt, errnum)`（981），与 DSN 测距的积分器同源（条目 10）。

```cpp
// DopplerAdapter.cpp:899-904, 963-999  多普勒核心换算与 C 值
multiplierS = turnaround*(uplinkFreq*1.0e6)/(interval*speedoflightkm); // S 路径乘子
multiplierE = turnaround*(uplinkFreqE*1.0e6)/(interval*speedoflightkm);// E 路径乘子
dtS = measDataS.value[i] / speedoflightkm;   // S 路径光行时 (s)
dtE = measDataE.value[i] / speedoflightkm;   // E 路径光行时 (s)
...
dtdt = dtE - dtS;                            // 两路径光行时之差 (s)
...
cMeasurement.value[i] = -turnaround*(uplinkFreq*1.0e6)*(interval - dtdt)/interval; // Hz
```

### 13. GN/BRTS 变体（GN_Doppler、BRTS_Doppler）
- **公式**：GN 多普勒用 1/Tc 乘子把**光程长差**直接转成 km/s：
  $$C_{GN}=\frac{\Delta\rho}{T_c}\ (\text{km/s}),\qquad \Delta\rho=\rho_E-\rho_S,\qquad M_S=M_E=1/T_c$$
  BRTS 多普勒结构与 DSN_TCP 相同，转发比/频率来源换成 BRTS 站参数。偏导合成同式（`derivativesE*multiplierE - derivativesS*multiplierS`）。
- **代码位置**：`plugins/EstimationPlugin/src/base/adapter/GNDopplerAdapter.cpp:944-945`（乘子）、`1011`（C 值）、`1016`（修正）、`1380`（偏导）；`BRTSDopplerAdapter.cpp:978-1440`（结构同 DopplerAdapter，E/S 两路径 1078、合成 C 值区）。
- **深度讲解**：这两类是 DSN_TCP 的工程变体，公式骨架（E/S 路径、光行时差分、乘子换算）完全一致，差别只在乘子量纲（Hz vs km/s）与上行频率来源。本章不再重复推导，公式索引表统一归到"多普勒族"。

### 14. 角度测量几何（SEZ 变换与 Az/El、RA/Dec 通用链）
- **公式**：设 $\mathbf{l}=-\boldsymbol{\rho}_{in}$（地面站→卫星，惯性系），经地固旋转与站心旋转得到 SEZ 矢量 $\mathbf{s}=R_{Obs,bf}\,R_{bf,j2k}\,\mathbf{l}$，则
  $$el=\arcsin(s_z/|\mathbf{s}|),\qquad az=\text{atan2}(s_y,-s_x)$$
  地固系下的经纬式（用于 RA/Dec 与 X/Y 型角度）：
  $$\delta=\arcsin(\rho_{bf,z}/|\boldsymbol{\rho}_{bf}|),\qquad \lambda=\text{atan2}(\rho_{bf,y},\rho_{bf,x})$$
  视差介质修正（测角）：
  $$\boldsymbol{\rho}_{bf}'=\boldsymbol{\rho}_{bf}+|\boldsymbol{\rho}_{bf}|\tan(\Delta_{tropo}+\Delta_{iono})\,\tilde{\mathbf{D}},\quad
  \tilde{\mathbf{D}}=-\sin el\cos az\,\hat{\mathbf{N}}-\sin el\sin az\,\hat{\mathbf{E}}+\cos el\,\hat{\mathbf{Z}}$$
- **代码位置**：`plugins/EstimationPlugin/src/base/adapter/AngleAdapterDeg.cpp:372-890`（`CalculateMeasurement()`；`lssb` 595、地固旋转 625、介质修正矢量 643-678（`D_tilde` 662、`tropoIonoCorrVec` 664）、站心投影 690、惯性回投 692）；`TopocentricSEZToAzEl()` 906-921；`GetENZUnitVectors()` 989-1030（E/N/Z 由站经纬度给出 1006-1016）。
- **深度讲解**：测角测量只关心**方向**，因此全部走"惯性视线 → 地固 → 站心 SEZ"的旋转链（条目 4 的复用），不叠加硬件延迟。SEZ 坐标系为**南-东-天**：$az=\text{atan2}(E,-S)$ 保证北向为 0、顺时针为正。介质修正不是标量加在角度上，而是把视线矢量平移 $|\boldsymbol{\rho}|\tan(\Delta)$ 再重投影——这样 $az/el$ 的修正在低仰角自动放大（正割效应）。站心单位矢量 $\hat{\mathbf{E}},\hat{\mathbf{N}},\hat{\mathbf{Z}}$ 由站大地经纬度构造（1006-1016），与站地固位置共享同源数据。

### 15. 方位角/仰角测量与解析偏导
- **公式**：测量值
  $$az=\frac{180}{\pi}\,\text{atan2}(s_y,-s_x),\qquad el=\frac{180}{\pi}\,\arcsin(s_z/|\mathbf{s}|)$$
  偏导（Moyer 9-9/9-10、13-192/13-193）：
  $$\frac{\partial az}{\partial\mathbf{r}}=\frac{\tilde{\mathbf{A}}_{in}}{|\boldsymbol{\rho}|\cos el},\quad
  \tilde{\mathbf{A}}=-\sin az\,\hat{\mathbf{N}}+\cos az\,\hat{\mathbf{E}};\qquad
  \frac{\partial el}{\partial\mathbf{r}}=\frac{\tilde{\mathbf{D}}_{in}}{|\boldsymbol{\rho}|},\quad
  \tilde{\mathbf{D}}=-\sin el\cos az\,\hat{\mathbf{N}}-\sin el\sin az\,\hat{\mathbf{E}}+\cos el\,\hat{\mathbf{Z}}$$
  速度偏导恒为零（角度只依赖位置）。周期量在 0°≤az<360° 归位（`AzimuthAdapter::Initialize()` 设 `isPeriodic/period=360`）。
- **代码位置**：`plugins/EstimationPlugin/src/base/adapter/AzimuthAdapter.cpp:193-201`（`CalcMeasValue()`）、`219-254`（`CalcDerivValue()`，`Atilde_bf` 230、`deriv` 236）；`ElevationAdapter.cpp:160-171`、`189-229`（`Dtilde_bf` 205、`deriv` 211）。
- **深度讲解**：两个适配器把"测量值合成"（条目 14 的 SEZ 链）与"解析偏导"分离：`AngleAdapterDeg::CalculateMeasurement()` 计算 `topoRange/mj2000Range/bfRange`，子类 `CalcMeasValue()` 只做一次 `TopocentricSEZToAzEl` 投影；`CalcDerivValue()` 用**体固系下的方向矢量**（$\tilde{\mathbf{A}},\tilde{\mathbf{D}}$）经 `BodyFixedToMJ2000T3`（`AngleAdapterDeg.cpp:1157-1185`）转回惯性系再除以斜距。这样偏导自动兼容站心旋转（旋转在求导之前完成）。$|\boldsymbol{\rho}|=r_{23}$ 是站心斜距。

```cpp
// ElevationAdapter.cpp:205-211  仰角偏导：方向矢量 D_tilde 除以斜距
Rvector3 Dtilde_bf = -sinElev*cosAzim*N_unit - sinElev*sinAzim*E_unit + cosElev*Z_unit;
Rvector3 Dtilde_inertial = BodyFixedToMJ2000T3(Dtilde_bf);   // 地固→惯性
Real r23 = topoRange.GetMagnitude();                          // 站心斜距
Rvector3 deriv = Dtilde_inertial / r23;                       // ∂el/∂r（弧度）
```

### 16. 赤经/赤纬测量与解析偏导
- **公式**：惯性（MJ2000）视线投影：
  $$RA=\frac{180}{\pi}\,\text{atan2}(l_y,l_x),\qquad Dec=\frac{180}{\pi}\,\arcsin(l_z/|\mathbf{l}|)$$
  偏导（Moyer 9-1/9-2、13-189/13-191，用**地固经度** $\lambda$ 与赤纬 $\delta$ 构造方向矢量）：
  $$\frac{\partial RA}{\partial\mathbf{r}}=\frac{\tilde{\mathbf{A}}_{in}}{|\boldsymbol{\rho}|\cos\delta},\ \tilde{\mathbf{A}}=(-\sin\lambda,\cos\lambda,0);\qquad
  \frac{\partial Dec}{\partial\mathbf{r}}=\frac{\tilde{\mathbf{D}}_{in}}{|\boldsymbol{\rho}|},\ \tilde{\mathbf{D}}=(-\sin\delta\cos\lambda,-\sin\delta\sin\lambda,\cos\delta)$$
- **代码位置**：`plugins/EstimationPlugin/src/base/adapter/RightAscAdapter.cpp:192-201`（`CalcMeasValue()`）、`219-250`（`CalcDerivValue()`，`A_bf` 226、`deriv` 232）；`DeclinationAdapter.cpp:159-167`、`185-221`（`D_bf` 197、`deriv` 203）；投影函数 `MJ2000ToRaDec()`/`BodyFixedToLongDec()` 在 `AngleAdapterDeg.cpp:1033-1081`。
- **深度讲解**：RA/Dec 是**惯性系**角度量（对应光学/天体测量观测），与站心 Az/El（**地固/站心**量）的区别就在投影坐标系：RA/Dec 用 `mj2000Range`（`rJ2kRotation.Inverse()*bfRange`，`AngleAdapterDeg.cpp:692`），偏导方向矢量也用 `BodyFixedToLongDec` 得到的**地固经纬度**构造后再转惯性（因为旋转矩阵在求导时作为常数处理）。`RightAscAdapter` 中 `Initialize()` 同样设 `period=360` 处理 0°~360° 周期。

### 17. 光行差修正（周年/周日）
- **公式**（狭义相对论光行差，`beta=|\mathbf{v}_{gs}|/c`）：
  $$\mathbf{l}'=\frac{\beta_{inv}\,\mathbf{l}+(\mathbf{v}_{gs}/c)\,f_2\,|\mathbf{l}|}{1+f_1},\qquad
  \beta_{inv}=\sqrt{1-\beta^2},\ f_1=\hat{\mathbf{l}}\cdot(\mathbf{v}_{gs}/c),\ f_2=1+\frac{f_1}{1+\beta_{inv}}$$
  周年项取站所属中心体相对 SSB 的速度（`rOStateSSB.GetV()`），周日项取站随地球自转的附加速度（站 SSB 速度减原点 SSB 速度）。
- **代码位置**：`plugins/EstimationPlugin/src/base/adapter/AngleAdapterDeg.cpp:1318-1358`（`GetAberrationVel()`，周年 1323-1334、周日 1336-1352）、`1376-1403`（`ApplyAberrationCorrection()`，1391 主式）；调用点 603-608。
- **深度讲解**：光行差把"接收时刻视线"修正为"发射时刻视线"（信号传播期间观测者移动造成的方向偏差）。公式是速度叠加的严格相对论形式（非一阶近似），`f_1,f_2` 是 $\beta$ 展开的中间量。实现把修正作用在**惯性系视线矢量**上（`lssb`），再进旋转链，因此角度偏导链不受影响。该修正由 `useAnnual/useDiurnal` 两个布尔开关控制（`AngleAdapterDeg` 参数），默认关闭。

### 18. GPS 位置点测量（GPS_PosVec）
- **公式**：观测值 = 航天器在地固系（ECF）的三维位置：
  $$\mathbf{r}_{ECF}=R_{ECF\gets MJ2000}\big(\mathbf{r}_{rLoc}-\mathbf{R}_{origin\to Earth}(t)\big),\qquad C=[r_x,r_y,r_z]\ (\text{km})$$
  协方差 $\Sigma=\text{diag}(\sigma^2,\sigma^2,\sigma^2)$，无噪声设置时对角取 1.0。
- **代码位置**：`plugins/EstimationPlugin/src/base/adapter/GPSAdapter.cpp:372-595`（位置链 398-426、噪声/偏置 471-482、协方差 485-501）。
- **深度讲解**：GPS 点测量把航天器位置矢量当"三维观测"，是**无信号路径几何**的测量（单点信号模型 `GPSPointMeasureModel`，`measurementmodel/GPSPointMeasureModel.cpp:517`）。坐标链：`rLoc`（参与者坐标系）→ 若原点非地球则平移到地球 MJ2000（405-410）→ `CoordinateConverter::Convert` 转到 BodyFixed（422）。测量模型自身不参与光时/介质（`GPSPointMeasureModel` 直接给出 rLoc）。偏导为单位阵块（位置对位置），速度偏导为零——对应"接收机直接测量位置"的物理。

### 19. 噪声与偏置注入（白噪声/偏置的统一实现）
- **公式**：所有适配器统一执行：
  $$C_{\text{meas}}=\text{Mod}\big(M\,C_0+\varepsilon+b,\ period\big),\qquad
  \varepsilon\sim\mathcal{N}(0,\sigma^2),\qquad
  b=\begin{cases}\text{measurementBias},&\text{常数偏置}\\ b_{pass}(t),&\text{pass 偏置}\end{cases}$$
  周期量（az/RA）用 `GmatMathUtil::Mod` 归位（`AngleAdapterDeg.cpp:824-833`）。测量协方差矩阵 `measErrorCovariance` 由 `ComputeMeasurementErrorCovarianceMatrix()` 由噪声 sigma 构造（GPS 见条目 18，一般类型见 `RangeAdapterKm.cpp:652-666` 的调用）。
- **代码位置**：`plugins/EstimationPlugin/src/base/adapter/RangeAdapterKm.cpp:716-758`（乘子/噪声/偏置）、`AngleAdapterDeg.cpp:790-836`（角度版）、`DopplerAdapter.cpp:1020-1057`（Hz 版）、`DSNRangeAdapter.cpp:487-524`（RU 版）。
- **深度讲解**：噪声注入采用"先噪声后偏置"顺序（避免偏置的噪声再被计入，`RangeAdapterKm.cpp:734` 注释）。仿真（`Simulator`）用这套注入生成带噪观测；估计（`BatchEstimator`）把 `addNoise=false` 走同一路径得到**无噪 C 值**与残差。`correction` 数组始终携带"修正+噪声+偏置"以便报告里分离。

---

## 三、测量误差模型（`errormodel/`、`estimator/`）

### 20. ErrorModel：白噪声、常数偏置与 pass 偏置
- **公式**：`ErrorModel` 是挂在测站/接收机上的可解算参数容器：
  $$b(t)=\begin{cases}b_0,&\text{Bias}\\ b_{pass}(p(t)),& p(t)=\{p:T_p\le t<T_{p+1}\},\ \text{PassBiases}\end{cases}$$
  $\sigma$（NoiseSigma）与 $b$ 同单位（由测量类型决定：km、km/s、Hz、RU、deg，见 `ErrorModel.cpp:442-491`）。pass 偏置是**分段常数**，分段边界由各 pass 起始历元给出（`GetBiasPassNumber` 线性扫描，1779-1797）；其偏导是 0/1 指示向量（当前 pass 对应元素为 1，其余 0，见 `PhysicalSignal.cpp:1562-1579` 的 `PassBiases` 分支）。
- **代码位置**：`plugins/EstimationPlugin/src/base/errormodel/ErrorModel.cpp:1779-1797`（`GetBiasPassNumber`）、`1811-1814`（`GetPassBias`）；参数定义 `ErrorModel.hpp`（`BIAS/BIAS_SIGMA/PASS_BIASES/SOLVEFORS` 枚举区，见 `ErrorModel.cpp:505-514` 的 ID 解析）。偏导指示向量在 `plugins/EstimationPlugin/src/base/signal/PhysicalSignal.cpp:1358-1500`（`Bias` 分支 1368-1499）与 `1510-1704`（`PassBiases` 分支）。
- **深度讲解**：`ErrorModel` 本身**不产生随机数**——它只保存 $\sigma,b$ 参数并被适配器读取（条目 19）；"白噪声"的实现是适配器里的 `RandomNumber::Gaussian(0, sigma)`。求解 `Bias` 或 `PassBiases` 时，估计器把它加入状态向量（`SolveFors` 参数，`ErrorModel.cpp:668-704`），偏导由信号层返回 1.0（Bias 对整个路径只计一次，见 1368 起的"首腿才计算"逻辑）或 pass 指示向量。这也解释了为什么 `Bias` 的 $H$ 列是 1：$C$ 对 $b$ 的导数恒为 1。

### 21. 测量权重与测量协方差
- **公式**（Montenbruck & Gill Eq. 8.33）：
  $$w_i=\frac{1}{\Sigma_{ii}},\qquad \Sigma=\text{measErrorCovariance}$$
  无噪声 sigma（协方差对角为 0）时 $w_i=1$（等权）。多测量分量（如 GPS 三维）取各自对角元素。
- **代码位置**：`plugins/EstimationPlugin/src/base/estimator/Estimator.cpp:3552-3562`（`GetMeasurementWeight()`）；协方差构造调用 `ComputeMeasurementErrorCovarianceMatrix()`（`RangeAdapterKm.cpp:659`、`AngleAdapterDeg.cpp:748`）。
- **深度讲解**：权重进入批估计信息矩阵（条目 24）与 WRMS（条目 29）与数据编辑判据（条目 30）。$w=1/\sigma^2$ 使高精度测量（小 $\sigma$）在正规方程中占主导；协方差为零时回退等权避免除以零。注意 GMAT 的权重是**无偏归一**（未乘 $1/(m-n)$ 自由度因子），因此 WRMS 接近 1 表示残差统计与噪声假设一致。

### 22. DSN 距离模糊度解算（观测值修正）
- **公式**：$O'=O+N\cdot M$，$N=\lfloor(C-O)/M+0.5\rfloor$（就近取整），$M=\text{rangeModulo}$（RU）。
- **代码位置**：`plugins/EstimationPlugin/src/base/estimator/Estimator.cpp:4032-4038`（`ObservationDataCorrection()`）；调用点 4235-4240（仅 `DSN_SeqRange/DSN_PNRange` 且首次迭代）；EKF 侧调用 `ExtendedKalmanFilter.cpp:622-627`。
- **深度讲解**：相位测距的整周模糊度在**观测值侧**修正（不动计算值），保证残差 $O'-C$ 进入正确的相位周期；`rangeModulo` 来自观测文件（`DSNRangeAdapter.cpp:412-415` 从 `obsData` 读入）。`+0.5` 实现四舍五入取整，对应"选择使 $|O'-C|$ 最小的整周数"。该修正只做一次（首次迭代），之后残差不再跳周期。

---

## 四、批处理加权最小二乘估计器（`estimator/`）

> 批估计 vs 序贯滤波的适用场景：**批估计**（`BatchEstimator`）一次性处理整段弧长的全部观测，用信息矩阵 $\Lambda=H^TWH$ 求全局最优解，适合**事后精密定轨**（弧段内状态可视为常值、初值较好、需要全弧段统计量）；**序贯滤波**（EKF）逐历元递推，只保留当前状态与协方差，适合**实时/近实时**处理、状态随时间演化的场景（机动、过程噪声显著）。数值上批估计累积 $n\times n$ 信息矩阵（$n$=状态数），EKF 每步只做 $m\times m$（$m$=测量维数）求逆（平方根形式甚至不求逆），计算量随弧段长度变化的方式不同。GMAT 中两者共用同一测量/偏导基础设施，差异只在"何时累加、如何解算"。

### 23. 残差 O−C 与周期量回绕
- **公式**：
  $$y_i=O_i-C_i;\qquad \text{若 }C\text{ 为周期量且 }|y|>period/2:\quad y\leftarrow(period-|y|)\cdot\text{sign}(y)$$
- **代码位置**：`plugins/EstimationPlugin/src/base/estimator/Estimator.cpp:4119-4357`（`CalculateResiduals()`；O−C 4292、周期回绕 4293-4295、权重 4299）。
- **深度讲解**：周期回绕保证 az/RA 等 360° 周期量在 0° 附近不产生虚假大残差（359.9° 与 0.1° 的差按 −0.2° 计）。`measStat` 携带 `residual/weight/hAccum` 三件套，`BatchEstimator::Accumulate` 直接消费。O−C 前还执行二级数据编辑（`FilteringData`）与 sigma 编辑（见条目 30），被剔除的记录带 `editFlag`（`NORMAL_FLAG/IRMS_FLAG/OLSE_FLAG/ILSE_FLAG/BLOCKED_FLAG/HORP_FLAG…`，枚举定义见 `Estimator.hpp`）。

### 24. 信息矩阵与残差累积（正规方程左侧）
- **公式**（GTDS MathSpec Eq. 8-57 的前两项）：
  $$\Lambda=\sum_k H_k^T W_k H_k,\qquad \mathbf{b}=\sum_k H_k^T W_k\,(O-C)_k$$
  逐元素实现（对第 $k$ 个测量、状态 $i,j$）：
  $$\Lambda_{ij}\mathrel{+}=h_{ki}h_{kj}w_k,\qquad b_i\mathrel{+}=h_{ki}w_k\,y_k$$
- **代码位置**：`plugins/EstimationPlugin/src/base/estimator/BatchEstimator.cpp:889-1022`（`Accumulate()`；累积循环 914-933，信息矩阵 926、残差 931）。
- **深度讲解**：GMAT 按"先 $h_i h_j$ 再乘 $w$"的顺序累加（注释 926-929 说明这是为数值精度与对称性保持），而非 $h_i(w h_j)$——避免 $h$ 尺度悬殊时信息矩阵不对称。`editFlag==NORMAL_FLAG` 才参与累积。信息矩阵与残差矢量在**求解参数坐标系（Solve-for state）**下累积，$h_{ki}$ 已含 STM 与坐标变换（条目 25）。

```cpp
// BatchEstimator.cpp:914-932  单条观测的信息矩阵/残差累积
for (UnsignedInt k = 0; k < measStat.residual.size(); ++k)
{
   Real ocDiff = measStat.residual[k];      // O - C
   Real weight = measStat.weight[k];        // w = 1/sigma^2
   if (measStat.editFlag == NORMAL_FLAG)     // 只有通过编辑的记录进入正规方程
   {
      for (UnsignedInt i = 0; i < stateSize; ++i)
         for (UnsignedInt j = 0; j < stateSize; ++j)
            information(i, j) += hMeas[k][i] * hMeas[k][j] * weight; // Lambda += h h^T w
      for (UnsignedInt i = 0; i < stateSize; ++i)
         residuals[i] += hMeas[k][i] * weight * ocDiff;              // b += h w y
   }
}
```

### 25. 测量雅可比 H：STM 传播与坐标变换
- **公式**：测量对测量时刻状态的偏导 $H_{t_m}$ 由 `MeasureModel::CalculateMeasurementDerivatives` 解析给出；对**先验时刻 $t_0$ 状态**的偏导乘状态转移矩阵，再右乘"笛卡尔→求解参数"坐标变换导数：
  $$\mathbf{h}_{t_0}=\mathbf{h}_{t_m}\,\Phi(t_m,t_0),\qquad \mathbf{h}_{solve}=\mathbf{h}_{t_0}\,D_{cart\to solve}$$
  实现：`hRow[j]=\sum_k hTilde[i][k]\cdot stm(k,j)`，再 `hRowSolveFor[ii]=\sum_{jj} hRow[jj]\cdot cart2SolvMatrix(jj,ii)`。
- **代码位置**：`plugins/EstimationPlugin/src/base/estimator/BatchEstimator.cpp:1894-2042`（`EstimationPartials()`；逐状态求偏导 1911-1958、STM 应用 1980-1993、坐标变换 1997-2005）；测量侧偏导入口 `MeasureModel::CalculateMeasurementDerivatives`（`measurementmodel/MeasureModel.cpp:2108-2140`）。
- **深度讲解**：$H$ 的组装分三层：① 信号层给出对参与者**测量时刻**状态的解析偏导（位置/速度块，见条目 26）；② `BatchEstimator` 用 STM 把它映射到弧段起点 $t_0$（因为所有求解参数定义在 $t_0$）；③ `cart2SolvMatrix`（`EstimationStateManager::CartToSolveForStateConversionDerivativeMatrix`）把笛卡尔状态偏导变换到求解参数（如 Keplerian 要素、Cd、Bias）坐标系。`stateMap` 中 `subelement==1` 表示该状态块的首元素（1913），逐块填入 `hTilde` 再统一变换，避免重复调用信号层。

### 26. 状态/参数偏导的解析链（SignalBase 层）
- **公式**：对参与者 $P$（发端 $s=-1$，收端 $s=+1$），用 STM 子块构造位置/速度偏导：
  $$\frac{\partial\boldsymbol{\rho}_{in}}{\partial\mathbf{r}_P}=s\,R_{j2k}\,\Phi_{rr},\qquad
  \frac{\partial\boldsymbol{\rho}_{in}}{\partial\mathbf{v}_P}=s\,R_{j2k}\,\Phi_{rv}\qquad(\Phi=\Phi(t_1,t_m)\Phi^{-1}(t_m,t_0))$$
  距离偏导（$\hat{\boldsymbol{\rho}}=\boldsymbol{\rho}/|\boldsymbol{\rho}|$）：
  $$\frac{\partial \rho}{\partial X}=s\,\hat{\boldsymbol{\rho}}\cdot R_{j2k}\,\Phi_{rX}$$
  测距率偏导（含 $\partial\hat{\boldsymbol{\rho}}/\partial\boldsymbol{\rho}=[I-\hat{\boldsymbol{\rho}}\hat{\boldsymbol{\rho}}^T]/\rho$）：
  $$\frac{\partial\dot\rho}{\partial X}=\dot{\boldsymbol{\rho}}\cdot\Big(\frac{I-\hat{\boldsymbol{\rho}}\hat{\boldsymbol{\rho}}^T}{\rho}\Big)\frac{\partial\boldsymbol{\rho}}{\partial X}+\hat{\boldsymbol{\rho}}\cdot\frac{\partial\dot{\boldsymbol{\rho}}}{\partial X},\qquad
  \frac{\partial\dot{\boldsymbol{\rho}}}{\partial X}=s\,Q\,\Phi_X,\ Q=[\dot R_{j2k}\ |\ R_{j2k}]$$
  估计参数（Cr/Cd/ADSF/TSF）偏导：$\partial C/\partial p=\hat{\boldsymbol{\rho}}\cdot R_{j2k}\,E$，$E$ 为 $\Phi$ 去掉前 6 列的"参数列"子块。
- **代码位置**：`plugins/EstimationPlugin/src/base/signal/SignalBase.cpp:1699-1770`（`GetRangeVectorDerivative()`，$\Phi$ 1720、A/B 子块 1728-1741、符号 1742、拼装 1755/1767）；`1786-1842`（`GetRangeRateDerivative()`，$\partial\hat{\rho}/\partial\rho$ 1799-1810、合成 1812-1827）；`1859-1920`（`GetRangeRateVectorDerivative()`，$Q$ 矩阵 1890-1901、`drhoVecDot_dX=Q\Phi_X s$ 1904）；`1566-1622`（`GetCDerivativeVector()`，$\Phi$ 1578、E 子块 1581-1589、$sR E$ 1592-1606、投影 1616-1621）。
- **深度讲解**：这是整个 OD 雅可比的核心。$\Phi=\Phi(t_1,t_m)\Phi^{-1}(t_m,t_0)$ 把 STM 规范到"测量时刻→收发时刻"（1720 行注释），发端取负、收端取正（符号来自 $\boldsymbol{\rho}=\mathbf{r}_r-\mathbf{r}_t$）。测距率偏导用链式法则两次：先对 $\hat{\boldsymbol{\rho}}$ 求导（投影矩阵 $[I-\hat\rho\hat\rho^T]/\rho$），再对 $\boldsymbol{\rho}$ 与 $\dot{\boldsymbol{\rho}}$ 求导，其中 $\dot{\boldsymbol{\rho}}$ 的偏导含 $Q=[\dot R_{j2k}|R_{j2k}]$——**测站速度项**（地球自转旋转导数）在这里进入 $H$。参数偏导（Cr 等）走 STM 的"参数列"：$\Phi$ 的第 6 列之后对应估计参数对初始状态的传播，投影到视线方向即得。地面站的 STM 取单位阵（`SignalBase.cpp:2124-2127`、2208-2212），因为站位置是解析函数（无积分状态）。

### 27. 正规方程求解与信息矩阵求逆
- **公式**：
  $$\Delta x=\Lambda^{-1}\mathbf{b},\qquad P=\Lambda^{-1}\ (\text{协方差}),\qquad x\leftarrow x+\Delta x$$
  若启用先验：$\Lambda\leftarrow\Lambda+P_{x_0}^{-1}$，$\mathbf{b}\leftarrow\mathbf{b}+P_{x_0}^{-1}\Delta x_{prior}$。求解前先压缩零行/列（阈值 $10^{-50}$），求逆后按原索引扩回：
  $$\Lambda_{red}=\text{Compress}(\Lambda),\quad P_{red}=\Lambda_{red}^{-1}\ (\text{Schur/Cholesky/通用}),\quad P=\text{Expand}(P_{red})$$
- **代码位置**：`plugins/EstimationPlugin/src/base/estimator/BatchEstimator.cpp:1033-1271`（`Estimate()`；先验 1129-1145、`dx` 1192-1200、状态更新 1226）；`1651-1823`（`SolveNormalEquations()`；压缩 1684-1685、Schur 1736-1757、Cholesky 1758-1765、通用求逆 1770、扩回 1805-1806）。
- **深度讲解**：`Estimate()` 在每次外迭代收敛检查前执行：解正规方程 → 算 WRMS → 内环编辑（条目 30）→ 更新状态 → 重算坐标变换导数矩阵。`SolveNormalEquations` 支持三种求逆策略：默认通用 `Rmatrix::Inverse()`（LU），`Schur`（特征分解，对病态更稳但先 Cholesky 试错，1738-1749）、`Cholesky`（要求正定）。压缩阈值 $10^{-50}$ 把"从未被任何测量激励"的状态列剔除——这就是**可估性**的实现：信息矩阵零行/列对应不可估参数（无测量敏感），压缩后求解、扩回时对应行/列置零（协方差 0 表示"不更新"）。整个状态数 $n$ 不可估时抛异常（1686-1688）。

```cpp
// BatchEstimator.cpp:1192-1200  dx = Lambda^-1 * b（正规方程求解后的状态修正）
dx.clear();
Real delta;
for (UnsignedInt i = 0; i < stateSize; ++i)
{
   delta = 0.0;
   for (UnsignedInt j = 0; j < stateSize; ++j)
      delta += informationInverse(i, j) * residuals(j);   // 信息矩阵逆 × 残差矢量
   dx.push_back(delta);                                    // 本次迭代的状态修正
}
// 1226 行： estimationStateS[i] += dx[i]   （x <- x + dx）
```

### 28. 先验协方差（A-priori）
- **公式**：先验信息项 $P_{x_0}^{-1}$ 叠加进信息矩阵，先验残差项 $\mathbf{b}_{prior}=P_{x_0}^{-1}\Delta x_0$（$\Delta x_0=x-x_0^{prior}$）叠加进残差矢量；WRMS 的先验项为 $(\Delta x)^T P_{x_0}^{-1}(\Delta x)$。
- **代码位置**：`plugins/EstimationPlugin/src/base/estimator/BatchEstimator.cpp:1129-1145`（信息/残差叠加）、`1314-1330`（WRMS 先验项）。
- **深度讲解**：先验把"解偏向已知参考状态"的约束写成二次型加入最小二乘，等价于把先验当作伪测量。`InvertApriori` 由 `EstimationStateManager` 提供（协方差 → 信息）。EKF 侧没有显式先验项（初值协方差直接是 $P_0$，见条目 31-33）。

### 29. WRMS 与预测 RMS
- **公式**：
  $$\text{WRMS}=\sqrt{\frac{1}{N}\Big[\sum_k w_k\,(y_k-\mathbf{h}_k\Delta x)^2+\underbrace{(\Delta x)^TP_{x_0}^{-1}\Delta x}_{\text{先验项}}\Big]}$$
  $y_k$ 为当前残差，$\mathbf{h}_k\Delta x$ 为"残差变化"（`CalculateResidualChange`，线性化预测）。
- **代码位置**：`plugins/EstimationPlugin/src/base/estimator/BatchEstimator.cpp:1286-1373`（`CalculateWRMS` 两重载 1286/1309、残差变化 1366-1373）。
- **深度讲解**：`newResidualRMS`（当前状态）与 `predictedRMS`（按 $\Delta x$ 线性外推）是收敛判据与数据编辑的标尺（条目 30 的 $\sigma$ 源）。`CalculateResidualChange` 用累积的 $h_{accum}$ 与 $\Delta x$ 点积，避免重算测量——这是内环编辑能快速迭代的关键（条目 30）。

### 30. 数据编辑：IRMS/OLSE/ILSE σ 编辑
- **公式**：
  - 初值编辑（`iterationsTaken==0`，IRMS）：剔除 $\sqrt{w}\,|O-C|>\text{maxResidualMult}$；
  - 外环编辑（OLSE）：剔除 $\sqrt{w}\,|O-C|>\text{constMult}\cdot\sigma+\text{additiveConst}$，$\sigma\in\{\text{predictedRMS},\text{newResidualRMS}\}$；
  - 内环编辑（ILSE，每次外迭代内重解）：对"残差变化后"的残差 $\sqrt{w}\,|y-\mathbf{h}\Delta x|>\text{constMultIL}\cdot\sigma_{IL}$ 的记录，从信息矩阵中**减去**其贡献后重解（`informationIL = information - informationIL`）。
- **代码位置**：`plugins/EstimationPlugin/src/base/estimator/BatchEstimator.cpp:1835-1884`（`DataFilter()`，IRMS 1852、OLSE 1874）、`1383-1641`（`InnerLoop()`，判据 1470、信息扣减 1519、重解 1524）。
- **深度讲解**：σ 编辑是 OD 的经典野值抑制：IRMS 只作用首轮（无先验统计），OLSE 用当前/预测 RMS 做 $k\sigma$ 门限，ILSE 在"外环已收敛的解"上再迭代剔除"对解影响大"的记录并**增量式**更新正规方程（扣除被剔除记录的 $hh^Tw$ 贡献，1519-1520），直到两次编辑集合一致（收敛判据 1564-1583）。被编辑记录写入 `removedReason`（"IRMS"/"OLSE"/"ILSE"）并在报告里计数。

---

## 五、扩展卡尔曼滤波（`ExtendedKalmanFilterPlugin`）

> EKF 采用**平方根（QR/thinQR）实现**：全程维护 $P$ 的 Cholesky 平方根 $S$（$\sqrt{P}$），用 QR 分解代替矩阵求逆，保证协方差半正定。经典五方程为：
> 预测：$\bar x=\Phi x$，$\bar P=\Phi P\Phi^T+Q$；增益：$K=\bar P H^T(H\bar P H^T+R)^{-1}$；更新：$\hat x=\bar x+K(y-H\bar x)$，$\hat P=(I-KH)\bar P$。
> 下面对照实现逐条给出。

### 31. EKF 时间更新（平方根 thinQR 形式）
- **公式**：先把 $Q$ 与 $\Phi$ 变换到求解参数坐标系（$D=\partial X/\partial S$）：
  $$Q_S=D_S^{-1}Q(D_S^{-1})^T,\qquad \Phi_S=D_S^{-1}\Phi D_S$$
  再对 $[\Phi_S S\ |\ \sqrt{Q_S}]$ 做 thin QR 得预测平方根：
  $$\bar S=\text{thinQR}(\Phi_S S,\ \sqrt{Q_S})\ \Rightarrow\ \bar P=\bar S\bar S^T$$
- **代码位置**：`plugins/ExtendedKalmanFilterPlugin/src/base/EKF/ExtendedKalmanFilter.cpp:396-595`（`TimeUpdate()`；$Q_S$ 422、$\Phi_S$ 460、stmP 523、`thinQR` 555、$\bar P$ 579、对称化 582）。
- **深度讲解**：thin QR 把 $[\Phi_SS\ |\ \sqrt{Q}]$（$n\times 2n$）正交三角化，取上三角的前 $n$ 列作为 $\bar S$——数值上等价于 $\bar P=\Phi P\Phi^T+Q$ 的平方根分解，但避免了显式求积的精度损失（半正定保持）。$Q_S$ 可能带零对角（未启用过程噪声的轴），先 `CompressNormalMatrix` 压缩再分解、扩回（500-521）。分解失败（$Q$ 非正定）抛异常（497）。时间更新还推进"参考轨迹偏移" `xOffset = stm*xOffset`（463-473，用于延迟整流）。

```cpp
// ExtendedKalmanFilter.cpp:523-555  平方根时间更新
Rmatrix stmP = stm_S * sqrtP;              // Phi_S * S
Rmatrix sqrtQ = sqrtQ_T.Transpose();       // sqrt(Q_S)
...
sqrtP = thinQR(stmP, sqrtQ);               // thin QR: 预测平方根 S_bar
...
pBar = sqrtP * sqrtP.Transpose();          // P_bar = S_bar * S_bar^T
Symmetrize(pBar);                          // 强制对称
```

### 32. 卡尔曼增益与测量更新
- **公式**：对 $[\sqrt{\text{scale}}\,H\bar S\ |\ \sqrt{R}]$ 做 thin QR 得 $S_w$（$S_wS_w^T=H\bar P H^T+R$ 的平方根），增益与更新协方差平方根：
  $$K=\bar S\bar S^T H^T (S_wS_w^T)^{-1}=\bar P H^T(H\bar P H^T+R)^{-1}$$
  $$\hat S=\text{thinQR}((I-KH)\bar S,\ K\sqrt{R}),\qquad \Delta x=K\,y$$
- **代码位置**：`plugins/ExtendedKalmanFilterPlugin/src/base/EKF/ExtendedKalmanFilter.cpp:759-816`（`ComputeGain()`；`sqrtScale` 768-772、`Sw` 792、$K$ 810、`sqrtPupdate` 811）、`829-896`（`UpdateElements()`；$\Delta x=Ky$ 837、状态更新 852-856、$P=\hat S\hat S^T$ 875-888）。
- **深度讲解**：增益的 thinQR 形式同时产出 $S_w$（用于残差缩放的 $\sigma=\sqrt{(H\bar P H^T+R)_{kk}}$，见条目 34）与更新平方根 $\hat S$（Joseph 形式的平方根实现，无需显式 $I-KH$ 乘方）。`sqrtScale` 实现**测量欠加权**（Lear 方法）：当位置协方差迹的平方根 $\sqrt{P_{00}+P_{11}+P_{22}}>$`deweightThreshold` 时，$K$ 的 $H\bar S$ 预乘 $\sqrt{1+\text{deweightCoeff}}$（等价于放大 $R$、压低增益），防止滤波器发散时测量主导（768-772、792）。测量更新把 $\Delta x$ 加到状态（或延迟整流偏移 `offsetState`，839-848）。

### 33. 协方差更新：简单与 Joseph 形式
- **公式**：
  $$P_{simple}=(I-KH)\bar P\qquad(\text{Brown\&Hwang Eq.4.7.12})$$
  $$P_{Joseph}=(I-KH)\bar P(I-KH)^T+K R K^T\qquad(\text{Tapley Eq.4.7.19})$$
- **代码位置**：`plugins/ExtendedKalmanFilterPlugin/src/base/EKF/ExtendedKalmanFilter.cpp:906-915`（`UpdateCovarianceSimple()`）、`927-952`（`UpdateCovarianceJoseph()`）。
- **深度讲解**：两个函数在 `UpdateElements` 里被注释掉（871-873），默认走平方根路径（`sqrtPupdate` 的直接乘积）。它们保留为**可插拔的数值对照实现**：简单形式计算量小但可能在舍入下失去对称/半正定；Joseph 形式对任意 $K$ 保持对称半正定（对次优增益稳健）。默认平方根路径在精度上等价于 Joseph 形式（thinQR 正交化），故注释选择它。

### 34. 残差缩放与测量统计
- **公式**：对第 $k$ 个测量分量：
  $$\text{scaledResid}_k=\frac{y_k}{\sqrt{(H\bar P H^T+R)_{kk}}}$$
  测量更新前若存在参考轨迹偏移，先修正计算值与残差：$C\leftarrow C+H\,x_{offset}$，$y\leftarrow y-H\,x_{offset}$。
- **代码位置**：`plugins/ExtendedKalmanFilterPlugin/src/base/EKF/ExtendedKalmanFilter.cpp:656-741`（`ComputeObs()`；偏移修正 674-679、缩放残差 695-701）。
- **深度讲解**：缩放残差以"预测残差协方差的单分量标准差"为尺度，是滤波健康度指标（理想 ~N(0,1)）；GMAT 按元素逐分量缩放（注释 690-692 说明整向量缩放留待实现）。`xOffset` 修正是"延迟整流"（Delayed Rectification）的一部分：滤波在参考轨迹附近线性化，偏移量计入测量计算后再随 `AdvanceEpoch` 的 `delayRectifySpan` 归并（954-1048）。

### 35. 序贯估计器（SeqEstimator）的标准形式时间更新
- **公式**：`SeqEstimator` 用经典（非平方根）形式：
  $$\bar P=\Phi_S P\Phi_S^T+Q_S,\qquad Q=\sum_{\text{SC}}Q_{SC}(dt)+Q_{estParam}(dt)$$
  过程噪声按 SC 状态块叠加（`Q(idx+ii, idx+jj) += scNoise(ii,jj)`），估计参数（FOGM 等）额外叠加（见条目 38）。时间步小于 $10^{-6}\,\text{s}$ 时跳过噪声累积（数值保护）。
- **代码位置**：`plugins/ExtendedKalmanFilterPlugin/src/base/EKF/SeqEstimator.cpp:1637-1685`（`TimeUpdate()`，$\bar P$ 1670）；`1469-1527`（`UpdateProcessNoise()`，容差 1483、叠加 1517）；`1540-1625`（`AddEstimatedParameterNoise()`，加速度 1597-1599、FOGM 噪声 1606-1622）；容器类 `ProcessNoiseModel::GetProcessNoise` 直接委托给内部模型（`plugins/ExtendedKalmanFilterPlugin/src/base/noise/ProcessNoiseModel.cpp:191-199`）。
- **深度讲解**：EKF 与 SeqEstimator 是同一插件里的两种数值路线：EKF 走平方根 thinQR（条目 31-33），SeqEstimator 走标准 $\Phi P\Phi^T+Q$。估计参数噪声（如 FOGM 的 7×7 块）在 `AddEstimatedParameterNoise` 里先取力模型偏导缓存（`forceDerivativeCache`）除以 $(1+stateValue)$ 还原加速度（$\epsilon$ 归一化参数），再交给 `EstimatedParameter::GetProcessNoise` 生成与状态耦合的噪声块（1617-1622 把第 6 行/列散到对应状态索引）。

### 36. SNC 过程噪声（白色加速度）
- **公式**（逐轴对角块，$\sigma_i$ 为加速度噪声密度）：
  $$Q_{ii}=\sigma_i^2\frac{dt^3}{3},\quad Q_{i,i+3}=Q_{i+3,i}=\sigma_i^2\frac{dt^2}{2},\quad Q_{i+3,i+3}=\sigma_i^2\,dt$$
- **代码位置**：`plugins/ExtendedKalmanFilterPlugin/src/base/noise/SNCProcessNoise.cpp:180-219`（`GetProcessNoise(elapsedTime, epoch)`；190-193）；仅时间参数的重载 233-278。
- **深度讲解**：SNC 假设加速度为白噪声（功率谱密度 $\sigma^2$），对状态（r,v）积分两次得到标准 $\left[\begin{smallmatrix}dt^3/3&dt^2/2\\dt^2/2&dt\end{smallmatrix}\right]$ 块——这是"随机游走位置 + 随机游走速度"的离散化协方差。$\sigma$ 用户以 `AccelSigma` 输入（km/s²/√s）。输出经 `ConvertMatrix` 转到惯性系（条目 39）。

### 37. 线性过程噪声
- **公式**：$Q=\text{diag}\big((\dot r_i\,dt)^2\big)$——每个状态分量的方差 =（速率 × 时间步）²。
- **代码位置**：`plugins/ExtendedKalmanFilterPlugin/src/base/noise/LinearProcessNoise.cpp:133-142`（`GetProcessNoise()`；138）。
- **深度讲解**：线性模型假设状态按常速率漂移，$dt$ 内不确定度为 $\dot r_i dt$（如钟漂、缓慢变化的偏置），各分量独立。是比 SNC 更简单的"确定性漂移 + 增长不确定度"模型。

### 38. 一阶高斯-马尔可夫（FOGM）过程噪声
- **公式**（相关时间 $\tau=\text{HalfLife}/\ln 2$，稳态方差 $\sigma_{ss}$，归一化因子 $\kappa$）：
  $$Q=\sigma_0^2\,G(t),\qquad \sigma_0^2=\frac{2\sigma_{ss}^2}{\kappa^2\tau}$$
  其中 $G$ 的元素为指数-多项式组合（$\gamma_{pp},\gamma_{pv},\gamma_{pa},\gamma_{vv},\gamma_{va},\gamma_{aa}$，由 $e^{-dt/\tau}$ 与 $dt$ 多项式给出，见 180-192）；$dt/\tau<0.01$ 时改用 Taylor 级数（204-209）避免指数精度损失。完整 7×7 块：位置/速度/参数（FOGM 标量）三块交叉耦合，且按力模型加速度外积 $\mathbf{a}\mathbf{a}^T$ 加权（217-221）。
- **代码位置**：`plugins/ExtendedKalmanFilterPlugin/src/base/estimatedparam/FirstOrderGaussMarkov.cpp:147-234`（`GetProcessNoise()`；$\tau$ 156、$\sigma_0^2$ 166-167、$\gamma$ 显式 180-192、Taylor 204-209、组装 213-231）。
- **深度讲解**：FOGM 描述**指数相关**的随机过程（如大气密度、SRP 系数的时间相关摄动），相关时间由半衰期给定。$\gamma$ 函数是"相关过程 + 白噪声驱动"线性系统的协方差闭式解；小 $dt/\tau$ 时 $e^{-dt/\tau}$ 出现灾难性抵消，故切换 Taylor 展开。加速度外积 $\mathbf{a}\mathbf{a}^T$ 把"该参数对加速度的影响方向"投影进位置/速度块（$\partial a/\partial p$ 的秩一近似），最后一行/列是参数自身方差。这是 $Q$ 中唯一与**动力学模型耦合**的过程噪声。

### 39. 过程噪声坐标变换
- **公式**：$Q$ 从用户坐标系转到 MJ2000 惯性系：
  $$Q_{j2k}=T\,Q\,T^T,\qquad T=\begin{bmatrix}R&0\\0&R\end{bmatrix},\ R=M_{cs\to j2k}$$
- **代码位置**：`plugins/ExtendedKalmanFilterPlugin/src/base/noise/ProcessNoiseBase.cpp:214-271`（`ConvertMatrix(Rmatrix&, GmatTime&)`；旋转 242-243、分块对角 245-254、相似变换 263）。
- **深度讲解**：SNC/线性模型定义在**用户指定坐标系**（默认 VNB 或某局部系），位置与速度块共用同一旋转（分块对角 $T$），因为位置-速度耦合项在同一正交变换下保持一致。相似变换 $TQT^T$ 保持对称半正定。若用户坐标系即惯性系则直接返回（227-235）。

---

## 六、几何测量模型（`GeometricMeasurementPlugin`）

> 几何测量是**纯几何**测量（无光时迭代、无介质修正、无硬件延迟），在观测历元瞬时计算，供 `Measure` 命令/事件驱动场景使用，也可被 `RunEstimator` 用作无噪声的对照。它们继承 `CoreMeasurement`，`Evaluate()` 内部调用与 EstimationPlugin 同名的 `CalculateRangeVectorInertial/Obs`、`CalculateRangeRateVectorObs`、`UpdateRotationMatrix`（基类实现）。由于本克隆不含 `CoreMeasurement` 源码，以下公式直接锚定 4 个派生类的 `Evaluate()`。

### 40. GeometricRange（几何测距）
- **公式**：
  $$C=|\boldsymbol{\rho}_{in}|,\qquad el=\arcsin\big((R_{o,j2k}\hat{\boldsymbol{\rho}}_{in})_z\big)\cdot\frac{180}{\pi}$$
  偏导：$\partial C/\partial\mathbf{r}_P=s\,\hat{\boldsymbol{\rho}}\cdot R_{j2k,P}$（$s=-1$ 发端/$+1$ 收端，站参与时乘其 $R_{j2k}$），速度偏导为 0，`Bias` 偏导为 1。
- **代码位置**：`plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricRange.cpp:203-283`（`Evaluate()`；仰角 223-224、C 值 232）、`299-555`（偏导；$\hat{\boldsymbol{\rho}}$ 375、站旋转 388、$s\hat\rho$ 396/477）。
- **深度讲解**：几何测距就是"瞬时欧氏距离"，可行性以站仰角门槛判定（`minAngle` 214-218、236-246）。偏导与 EstimationPlugin 的 `SignalBase::GetRangeDerivative` 一致（$\hat\rho$ 投影 + 站旋转），但无 STM（几何测量是单历元瞬时量）。`CalculateMeasurementDerivatives` 里 `objNumber` 区分参与者 1/2 与测量模型本身（Bias 列恒 1，529-533）。

### 41. GeometricRangeRate（几何测距率）
- **公式**：瞬时测距率 = 测距率矢量在视线方向的投影：
  $$\dot\rho=\dot{\boldsymbol{\rho}}_{obs}\cdot\hat{\boldsymbol{\rho}}_{obs}$$
  可行性判据 $\boldsymbol{\rho}_{in}\cdot\mathbf{p}_1>0$。
- **代码位置**：`plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricRangeRate.cpp:139-201`（`Evaluate()`；`CalculateRangeRateVectorObs` 149、投影 157）。
- **深度讲解**：与 `RangeRateAdapterKps`（两点差分，条目 11）不同，几何测距率是**单历元直接投影**——无需双 strand，也不含转发比/多普勒约定，是"视线闭合速率"的纯几何定义。`rangeRateVecObs` 已含测站速度（条目 3），故地球自转效应自动计入。偏导在 203-423（`CalculateMeasurementDerivatives`，按参与者与 Position/Velocity/Bias 分支，见 275/309/346 的 `range = rangeVecInertial.GetMagnitude()` 投影结构）。

### 42. GeometricAzEl（几何方位/仰角）
- **公式**（SEZ 站心系，与条目 14 同式）：
  $$el=\arcsin(\rho_{obs,z}/|\boldsymbol{\rho}_{obs}|),\qquad az=\text{atan2}(\rho_{obs,y},-\rho_{obs,x})$$
  $el=\pm90°$ 时 az 无定义（抛异常）；$|\rho_{obs,x}|<10^{-8}$ 判不可行。
- **代码位置**：`plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricAzEl.cpp:155-235`（`Evaluate()`；仰角 181、方位角 188、可行性 176）。
- **深度讲解**：`GeometricAzEl` 与 `AngleAdapterDeg` 家族（条目 14/15）公式同源，但直接用 `rangeVecObs`（观测系 SEZ 矢量，由基类旋转链给出），无光行差/介质修正。`value[0]=az`、`value[1]=el`（弧度）。偏导（237-537）按 `Position/Velocity/CartesianX` 分支从 SEZ 几何解析给出。

### 43. GeometricRADec（几何赤经/赤纬）
- **公式**（MJ2000 惯性系投影）：
  $$\delta=\arcsin(\rho_{obs,z}/|\boldsymbol{\rho}_{obs}|),\qquad RA=\text{atan2}(\rho_{obs,y},-\rho_{obs,x})$$
- **代码位置**：`plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricRADec.cpp:153-235`（`Evaluate()`；赤纬 180、赤经 187、可行性 175）。
- **深度讲解**：与 `GeometricAzEl` 结构完全相同（代码几乎同构），差别只在语义：RA/Dec 是惯性参考量（对应星表测量），Az/El 是站心参考量。`InitializeMeasurement()`（523 起）按"有无站参与者"建 `Fo` 局部坐标系（站心时用 Topocentric 系）。

---

## 七、公式索引表

| 公式 | 文件:行 | 所属类 |
|---|---|---|
| $\boldsymbol{\rho}_{in}=\mathbf{r}_r+\mathbf{j2kOriginSep}-\mathbf{r}_t$（Eq.6.12） | `plugins/EstimationPlugin/src/base/signal/SignalBase.cpp:1206-1212` | SignalBase::CalculateRangeVectorInertial |
| $\boldsymbol{\rho}_I=\boldsymbol{\rho}_{in}-\mathbf{disp}$（Eq.6.10） | `plugins/EstimationPlugin/src/base/signal/SignalBase.cpp:1259-1260` | SignalBase::CalculateRangeVectorInertial |
| $\dot{\boldsymbol{\rho}}_{in}=\mathbf{v}_r-\dot{\mathbf{j2kOriginSep}}-\mathbf{v}_t$ | `plugins/EstimationPlugin/src/base/signal/SignalBase.cpp:1332-1339` | SignalBase::CalculateRangeRateVectorObs |
| $\dot{\boldsymbol{\rho}}_{obs}=\dot R_{Obs,j2k}\boldsymbol{\rho}_{in}+R_{Obs,j2k}\dot{\boldsymbol{\rho}}_{in}$ | `plugins/EstimationPlugin/src/base/signal/SignalBase.cpp:1348` | SignalBase::CalculateRangeRateVectorObs |
| 地固→惯性旋转 $R_{j2k}$ 及其导数（测站链） | `plugins/EstimationPlugin/src/base/signal/SignalBase.cpp:1966-2002` | SignalBase::UpdateRotationMatrix |
| 光时定点迭代 $\Delta t=\Delta R/c$，容差 $10^{-12}$ s | `plugins/EstimationPlugin/src/base/signal/PhysicalSignal.cpp:1822-1899` | PhysicalSignal::GenerateLightTimeData |
| 相对论修正 $\Delta_{rel}=\sum\frac{(1+\gamma)\mu}{c^2}\ln\frac{r_1+r_2+r_{12}}{r_1+r_2-r_{12}}$ | `plugins/EstimationPlugin/src/base/signal/PhysicalSignal.cpp:2700-2711` | PhysicalSignal::RelativityCorrection |
| ET−TAI（Moyer 2-23/2-24）→ 腿修正 $(ET_t-ET_r)c$ | `plugins/EstimationPlugin/src/base/signal/PhysicalSignal.cpp:2824-2845,469` | PhysicalSignal::ETminusTAI / ModelSignal |
| 介质修正仰角 $el=\arcsin((R_{Obs,j2k}\hat\rho)_z)$ 与对流层/电离层合成 | `plugins/EstimationPlugin/src/base/signal/PhysicalSignal.cpp:2900-2971` | PhysicalSignal::MediaCorrection |
| 可行性仰角 $el=\arcsin(\hat\rho_{sez,z})\cdot180/\pi$ | `plugins/StationPlugin/src/base/station/GroundStation.cpp:1474-1476` | GroundStation::IsValidElevationAngle |
| 测距 C 值 $=\sum(|\boldsymbol{\rho}_{in}|+\sum corr)+\sum(t_d+r_d)c$ | `plugins/EstimationPlugin/src/base/adapter/RangeAdapterKm.cpp:573-591` | RangeAdapterKm::CalculateMeasurement |
| 白噪声注入 $\varepsilon\sim\mathcal{N}(0,\sigma)$ 与偏置 $+b$ | `plugins/EstimationPlugin/src/base/adapter/RangeAdapterKm.cpp:728-753` | RangeAdapterKm::CalculateMeasurement |
| 乘子 $M$ 应用 $C'=M\cdot C$ | `plugins/EstimationPlugin/src/base/adapter/RangeAdapterKm.cpp:716` | RangeAdapterKm::CalculateMeasurement |
| DSN RU 换算 $C_{RU}=F(f)\tau$；$F_S=f/2$、$F_X=221f/1498$ | `plugins/EstimationPlugin/src/base/adapter/DSNRangeAdapter.cpp:431-470,845-889` | DSNRangeAdapter::CalculateMeasurement / GetFrequencyFactor |
| DSN 斜坡积分（梯形累加） | `plugins/EstimationPlugin/src/base/adapter/DSNRangeAdapter.cpp:1000-1020` | DSNRangeAdapter::IntegralRampedFrequency |
| 测距率差分 $\dot\rho=(\rho_2-\rho_1)/\Delta t$ | `plugins/EstimationPlugin/src/base/adapter/RangeRateAdapterKps.cpp:476-485` | RangeRateAdapterKps::CalculateMeasurement |
| 测距率偏导差分 $(\partial\rho_2-\partial\rho_1)/\Delta t$ | `plugins/EstimationPlugin/src/base/adapter/RangeRateAdapterKps.cpp:570-571` | RangeRateAdapterKps::CalculateMeasurementDerivatives |
| 多普勒 $C=-\alpha f_{up}(T_c-\delta t)/T_c$ | `plugins/EstimationPlugin/src/base/adapter/DopplerAdapter.cpp:999` | DopplerAdapter::CalculateMeasurement |
| 多普勒斜坡 $C=-\alpha\int f_{ramp}/T_c$ | `plugins/EstimationPlugin/src/base/adapter/DopplerAdapter.cpp:981` | DopplerAdapter::CalculateMeasurement |
| 多普勒偏导 $M_E\partial\rho_E-M_S\partial\rho_S$ | `plugins/EstimationPlugin/src/base/adapter/DopplerAdapter.cpp:1349` | DopplerAdapter::CalculateMeasurementDerivatives |
| 转发比 S=240/221、X=880/749 | `plugins/EstimationPlugin/src/base/adapter/DopplerAdapter.cpp:1501-1504` | DopplerAdapter::GetTurnAroundRatio |
| GN 多普勒 $C=\Delta\rho/T_c$（km/s） | `plugins/EstimationPlugin/src/base/adapter/GNDopplerAdapter.cpp:944-945,1011` | GNDopplerAdapter::CalculateMeasurement |
| 视线/地固/站心旋转 $bfRange=R_{rJ2k}\mathbf{l}$ | `plugins/EstimationPlugin/src/base/adapter/AngleAdapterDeg.cpp:595-625` | AngleAdapterDeg::CalculateMeasurement |
| 测角介质矢量 $+\|\boldsymbol{\rho}\|\tan(\Delta)\tilde{\mathbf{D}}$ | `plugins/EstimationPlugin/src/base/adapter/AngleAdapterDeg.cpp:662-666` | AngleAdapterDeg::CalculateMeasurement |
| $az=\text{atan2}(s_y,-s_x),\ el=\arcsin(s_z/\|\mathbf{s}\|)$ | `plugins/EstimationPlugin/src/base/adapter/AngleAdapterDeg.cpp:906-913` | AngleAdapterDeg::TopocentricSEZToAzEl |
| $RA=\text{atan2}(l_y,l_x),\ Dec=\arcsin(l_z/\|\mathbf{l}\|)$ | `plugins/EstimationPlugin/src/base/adapter/AngleAdapterDeg.cpp:1033-1048` | AngleAdapterDeg::MJ2000ToRaDec |
| E/N/Z 站心单位矢量（经纬度构造） | `plugins/EstimationPlugin/src/base/adapter/AngleAdapterDeg.cpp:1006-1016` | AngleAdapterDeg::GetENZUnitVectors |
| 方位角偏导 $\tilde A_{in}/(r\cos el)$ | `plugins/EstimationPlugin/src/base/adapter/AzimuthAdapter.cpp:230-239` | AzimuthAdapter::CalcDerivValue |
| 仰角偏导 $\tilde D_{in}/r$ | `plugins/EstimationPlugin/src/base/adapter/ElevationAdapter.cpp:205-214` | ElevationAdapter::CalcDerivValue |
| RA 偏导 $\tilde A_{in}/(r\cos\delta)$ | `plugins/EstimationPlugin/src/base/adapter/RightAscAdapter.cpp:226-235` | RightAscAdapter::CalcDerivValue |
| Dec 偏导 $\tilde D_{in}/r$ | `plugins/EstimationPlugin/src/base/adapter/DeclinationAdapter.cpp:197-206` | DeclinationAdapter::CalcDerivValue |
| 光行差 $\mathbf{l}'=(\beta_{inv}\mathbf{l}+(\mathbf{v}/c)f_2|\mathbf{l}|)/(1+f_1)$ | `plugins/EstimationPlugin/src/base/adapter/AngleAdapterDeg.cpp:1383-1391` | AngleAdapterDeg::ApplyAberrationCorrection |
| GPS 位置 $C=\mathbf{r}_{ECF}$，$\Sigma=\text{diag}(\sigma^2)$ | `plugins/EstimationPlugin/src/base/adapter/GPSAdapter.cpp:398-426,485-501` | GPSAdapter::CalculateMeasurement |
| pass 偏置分段常数 $b_{pass}(t)$ | `plugins/EstimationPlugin/src/base/errormodel/ErrorModel.cpp:1779-1814` | ErrorModel::GetPassBias |
| 权重 $w=1/\Sigma_{ii}$（零协方差取 1） | `plugins/EstimationPlugin/src/base/estimator/Estimator.cpp:3552-3562` | Estimator::GetMeasurementWeight |
| 残差 $y=O-C$ 与周期回绕 | `plugins/EstimationPlugin/src/base/estimator/Estimator.cpp:4292-4295` | Estimator::CalculateResiduals |
| 模糊度解算 $O'=O+N\cdot M$ | `plugins/EstimationPlugin/src/base/estimator/Estimator.cpp:4032-4038` | Estimator::ObservationDataCorrection |
| 信息矩阵 $\Lambda_{ij}\mathrel{+}=h_ih_jw$、残差 $b_i\mathrel{+}=h_iwy$ | `plugins/EstimationPlugin/src/base/estimator/BatchEstimator.cpp:926,931` | BatchEstimator::Accumulate |
| $H_{t_0}=H_{t_m}\Phi$ 与 solve-for 变换 | `plugins/EstimationPlugin/src/base/estimator/BatchEstimator.cpp:1990,2002` | BatchEstimator::EstimationPartials |
| 距离偏导 $\partial\rho/\partial X=s\,\hat\rho\cdot R\Phi_{rX}$ | `plugins/EstimationPlugin/src/base/signal/SignalBase.cpp:1720-1767` | SignalBase::GetRangeVectorDerivative |
| 测距率偏导（含 $\partial\hat\rho/\partial\rho$ 与 $Q=[\dot R|R]$） | `plugins/EstimationPlugin/src/base/signal/SignalBase.cpp:1799-1827,1890-1904` | SignalBase::GetRangeRateDerivative / GetRangeRateVectorDerivative |
| 参数偏导 $\partial C/\partial p=\hat\rho\cdot R\,E$（STM 参数列） | `plugins/EstimationPlugin/src/base/signal/SignalBase.cpp:1578-1621` | SignalBase::GetCDerivativeVector |
| 状态修正 $\Delta x=\Lambda^{-1}\mathbf{b}$，$x\leftarrow x+\Delta x$ | `plugins/EstimationPlugin/src/base/estimator/BatchEstimator.cpp:1192-1200,1226` | BatchEstimator::Estimate |
| 先验叠加 $\Lambda+P_0^{-1}$、$\mathbf{b}+P_0^{-1}\Delta x_0$ | `plugins/EstimationPlugin/src/base/estimator/BatchEstimator.cpp:1135-1144` | BatchEstimator::Estimate |
| 正规方程求逆（压缩/Schur/Cholesky/通用） | `plugins/EstimationPlugin/src/base/estimator/BatchEstimator.cpp:1684-1806` | BatchEstimator::SolveNormalEquations |
| WRMS 与预测 RMS | `plugins/EstimationPlugin/src/base/estimator/BatchEstimator.cpp:1314-1348` | BatchEstimator::CalculateWRMS |
| σ 编辑 IRMS/OLSE 判据 $\sqrt w|O-C|>k\sigma+K$ | `plugins/EstimationPlugin/src/base/estimator/BatchEstimator.cpp:1852,1874` | BatchEstimator::DataFilter |
| 内环 ILSE 判据与信息扣减 | `plugins/EstimationPlugin/src/base/estimator/BatchEstimator.cpp:1470,1519` | BatchEstimator::InnerLoop |
| EKF 时间更新 $Q_S,\Phi_S$ 与 thinQR | `plugins/ExtendedKalmanFilterPlugin/src/base/EKF/ExtendedKalmanFilter.cpp:422-555` | ExtendedKalmanFilter::TimeUpdate |
| $\bar P=\bar S\bar S^T$ 与对称化 | `plugins/ExtendedKalmanFilterPlugin/src/base/EKF/ExtendedKalmanFilter.cpp:579-582` | ExtendedKalmanFilter::TimeUpdate |
| 欠加权 $\sqrt{1+\text{deweightCoeff}}$（Lear） | `plugins/ExtendedKalmanFilterPlugin/src/base/EKF/ExtendedKalmanFilter.cpp:768-772` | ExtendedKalmanFilter::ComputeGain |
| 增益 $K=\bar P H^T(S_wS_w^T)^{-1}$ 与 $\hat S$ thinQR | `plugins/ExtendedKalmanFilterPlugin/src/base/EKF/ExtendedKalmanFilter.cpp:792-811` | ExtendedKalmanFilter::ComputeGain |
| 测量更新 $\Delta x=Ky$，$P=\hat S\hat S^T$ | `plugins/ExtendedKalmanFilterPlugin/src/base/EKF/ExtendedKalmanFilter.cpp:837,875` | ExtendedKalmanFilter::UpdateElements |
| 协方差简单/Joseph 形式 | `plugins/ExtendedKalmanFilterPlugin/src/base/EKF/ExtendedKalmanFilter.cpp:914,937-939` | ExtendedKalmanFilter::UpdateCovarianceSimple / UpdateCovarianceJoseph |
| 缩放残差 $y/\sqrt{(H\bar P H^T+R)_{kk}}$ | `plugins/ExtendedKalmanFilterPlugin/src/base/EKF/ExtendedKalmanFilter.cpp:697-700` | ExtendedKalmanFilter::ComputeObs |
| 序贯时间更新 $\bar P=\Phi_SP\Phi_S^T+Q_S$ | `plugins/ExtendedKalmanFilterPlugin/src/base/EKF/SeqEstimator.cpp:1670` | SeqEstimator::TimeUpdate |
| 过程噪声叠加 $Q=\sum Q_{SC}+Q_{est}$ | `plugins/ExtendedKalmanFilterPlugin/src/base/EKF/SeqEstimator.cpp:1517,1523` | SeqEstimator::UpdateProcessNoise |
| SNC：$\sigma^2[dt^3/3,dt^2/2;dt^2/2,dt]$ 块 | `plugins/ExtendedKalmanFilterPlugin/src/base/noise/SNCProcessNoise.cpp:190-193` | SNCProcessNoise::GetProcessNoise |
| 线性：$Q=\text{diag}((\dot r\,dt)^2)$ | `plugins/ExtendedKalmanFilterPlugin/src/base/noise/LinearProcessNoise.cpp:138` | LinearProcessNoise::GetProcessNoise |
| FOGM：$\sigma_0^2G(t)$，$\gamma$ 指数/Taylor | `plugins/ExtendedKalmanFilterPlugin/src/base/estimatedparam/FirstOrderGaussMarkov.cpp:156-231` | FirstOrderGaussMarkov::GetProcessNoise |
| 噪声坐标变换 $Q_{j2k}=TQT^T$ | `plugins/ExtendedKalmanFilterPlugin/src/base/noise/ProcessNoiseBase.cpp:245-263` | ProcessNoiseBase::ConvertMatrix |
| 几何测距 $C=\|\boldsymbol{\rho}_{in}\|$ | `plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricRange.cpp:232` | GeometricRange::Evaluate |
| 几何测距率 $\dot\rho=\dot{\boldsymbol{\rho}}_{obs}\cdot\hat{\boldsymbol{\rho}}_{obs}$ | `plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricRangeRate.cpp:157` | GeometricRangeRate::Evaluate |
| 几何 Az/El：$el=\arcsin(\rho_z/\|\rho\|)$、$az=\text{atan2}(\rho_y,-\rho_x)$ | `plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricAzEl.cpp:181-188` | GeometricAzEl::Evaluate |
| 几何 RA/Dec 同式（惯性系） | `plugins/GeometricMeasurementPlugin/src/base/measurement/GeometricRADec.cpp:180-187` | GeometricRADec::Evaluate |
