# 第10章 机动与推力模型数学

> 本章范围：`src/base/burn/`（Burn 基类、`ImpulsiveBurn` 脉冲机动、`FiniteBurn` 有限推力机动、机动参考系）、`src/base/forcemodel/FiniteThrust.*`（有限推力瞬态力模型）、`src/base/hardware/`（`Thruster`/`ChemicalThruster`/`ElectricThruster` 推力量级与 Isp、`FuelTank` 及其派生箱的燃料质量流）、`plugins/ThrustFilePlugin/`（`FileThrust` 推力表格插值与推力角旋转）。
> 关于"TransientForce"：本仓库没有独立的 `TransientForce` 类文件（glob 全树无 `TransientForce.*`），瞬态力机制由 `FiniteThrust`/`FileThrust` + `ODEModel::UpdateTransientForces`（`src/base/forcemodel/ODEModel.cpp:2551`）承担，`GmatBase.cpp:130` 仍以字符串注册该类型名，详见[CH06](../CH06-dynamics.md) 引言。
> 术语与调用链约定与 [CH06](../CH06-dynamics.md)（力模型/航天器/硬件）、[CH07](../CH07-propagator.md)（传播器/`SetBurning`/步长限制）、[CH14](../CH14-plugins-b.md)（ThrustFilePlugin 架构）保持一致；本章只讲公式与算法，类图/调用链不重复。

## 一、机动数据流总览（一分钟版）

```text
Maneuver/BeginFiniteBurn 命令
   │  （点火/关火，见 CH05-command.md）
   ▼
Burn（ImpulsiveBurn | FiniteBurn）── 每次 Fire() 产出 burnData[4]
   │   burnData[0..2] = 加速度 (km/s²)；burnData[3] = 质量流率 (kg/s)
   ▼
FiniteThrust::GetDerivatives（瞬态力，BeginFiniteBurn 注入 transientForces）
   │   对每颗航天器累加 accel，写入 deriv[3+i6..5+i6] 与 deriv[mDotIndex]
   ▼
ODEModel（力聚合，GetForceMaxStep 取各力步长下限）
   ▼
RungeKutta::Step（forceMaxStep 截断步长 + followUpStep 接力步 + SetBurning）
```

- 脉冲机动：`Maneuver` 命令在**一个时刻**调用 `ImpulsiveBurn::Fire`，直接修改航天器速度状态（不经过力模型）。
- 有限推力：`BeginFiniteBurn`/`EndFiniteBurn` 命令之间由传播器推进，`FiniteThrust` 每个导数调用点调用 `FiniteBurn::Fire` 取当前推力加速度与质量流率。
- 推力表格：`BeginFileThrust` 注入 `FileThrust`（瞬态力），按 THF 剖面在**每步内**插值推力/质量流。

---

## 二、脉冲机动：ImpulsiveBurn

### 2.1 Δv 大小与正向速度施加
- **公式**：$$\|\Delta\mathbf{v}\|=\sqrt{\Delta v_1^2+\Delta v_2^2+\Delta v_3^2},\qquad \mathbf{v}^+=\mathbf{v}^-+\Delta\mathbf{v}_{\text{inertial}}$$
- **代码位置**：`src/base/burn/ImpulsiveBurn.cpp:1179`（模长）、`:358-360`（正向施加）
- **深度讲解**：
  - 工程背景：脉冲机动假设推力在无穷短的时间内施加，只改变速度不改变位置（理想冲量模型）。`ImpulsiveBurn` 的 `Element1/2/3`（旧名 `V/N/B`，见 `Burn.cpp:433-467` 的弃用警告）在**机动坐标系**中给出 Δv 分量，先由 `ConvertDeltaVToInertial`（第 2.2 节）旋到惯性系，再直接加到航天器速度分量上；从代码看位置分量（下标 0-2）始终不被触碰（`Fire` 全程只写 `satState[3..5]`），与"脉冲"假设一致。
  - 实现细节（正向路径）：
    ```cpp
    266:    ConvertDeltaVToInertial(deltaV, deltaVInertial, epoch);  // 机动系→惯性系
    ...
    358:    satState[3] += deltaVInertial[0];  // vx += Δvx（惯性系）
    359:    satState[4] += deltaVInertial[1];  // vy += Δvy
    360:    satState[5] += deltaVInertial[2];  // vz += Δvz
    ```
    逐行注释：第 266 行把用户定义的 Δv（体轴/VNB 等）投影到惯性系（第 2.2 节）；第 358-360 行直接改写航天器状态数组的速度分量——注意这里 `satState` 是 `spacecraft->GetState().GetState()`（第 249 行）返回的**引用**，改的就是航天器当前状态。
  - 模长 `dv`（第 1179 行）不参与速度施加，只用于火箭方程质量扣除（第 2.4 节）与反向传播的模长保持（第 2.3 节）。
  - 参数表（`ImpulsiveBurn.hpp:128-137` 枚举，默认值 `ImpulsiveBurn.cpp:86-87`）：

    | 参数名 | 类型 | 含义 |
    |---|---|---|
    | `CoordinateSystem/Origin/Axes` | 对象/枚举 | 机动坐标系（默认 Local + VNB，`Burn.cpp:120-122`） |
    | `Element1/Element2/Element3` | Real | Δv 三分量（km/s） |
    | `DecrementMass` | 布尔 | 是否从贮箱扣质量（默认 false） |
    | `Tank` | 对象数组 | 扣质量来源的 FuelTank 列表 |
    | `Isp` | Real | 比冲，秒（默认 300） |
    | `GravitationalAccel` | Real | 比冲换算用重力加速度（默认 9.81 m/s²） |
    | `DeltaTankMass` | Real（只读） | 本次机动结算的箱质量变化 |

### 2.2 Δv 从机动系到惯性系的旋转（基矢投影）
- **公式**：$$\Delta\mathbf{v}_I = \mathbf{R}(t)\,\Delta\mathbf{v}_L \quad(\text{coincident}=true\text{，仅旋转不平移})$$；对 `SpacecraftBody` 轴系（`ImpulsiveBurn.cpp:1247-1262`）：$$\Delta\mathbf{v}_I = \Delta\mathbf{v}_B\,\mathbf{R}_{BI}^{\mathsf T}\quad(\mathbf{R}_{BI}=\text{Spacecraft::GetAttitude}(t))$$
- **代码位置**：`src/base/burn/Burn.cpp:1193-1283`（`ConvertDeltaVToInertial`），体轴分支 `:1247-1263`
- **深度讲解**：
  - 工程背景：`Burn` 支持三类局部轴（`Burn.cpp:151-154`：`VNB`/`LVLH`/`MJ2000Eq`/`SpacecraftBody`）与任意全局坐标系。VNB 基矢的构造见 `src/base/burn/VnbManeuverFrame.cpp:110-149`：V 轴 = 速度方向、N 轴 = r×v 归一、B 轴 = v×n（公式与 [CH07](../CH07-propagator.md) 第 2.2 节机动参考系一致，此处不重复）。旋转由 `CoordinateSystem::ToBaseSystem(A1Mjd(epoch), in, out, true)` 完成——`true` 表示"coincident"（两系原点重合，只旋转）。
  - 实现细节（`Burn.cpp:1202-1275` 分支结构）：
    ```cpp
    1215:    Real inDeltaV[6], outDeltaV[6];     // 6 分量容器，后 3 位置零
    1222:    if (!usingLocalCoordSys)             // 用户显式指定全局坐标系
    1226:       coordSystem->ToBaseSystem(A1Mjd(epoch), inDeltaV, outDeltaV, true);
    1241:    if (isMJ2000EqAxes)                  // MJ2000Eq 局部轴 → 旋转阵恒等
    1243:       dvInertial[i] = dv[i];
    1247:    else if (isSpacecraftBodyAxes) {     // 体轴：取姿态阵并转置
    1254:       Rmatrix33 inertialToBody = spacecraft->GetAttitude(epoch);
    1255:       Rmatrix33 rotMat = inertialToBody.Transpose();
    1260:       outDeltaV = inDeltaV * rotMat;    // 体→惯性
    1268:    else
    1269:       localCoordSystem->ToBaseSystem(A1Mjd(epoch), inDeltaV, outDeltaV, true);
    ```
    逐行注释：`GetAttitude(epoch)` 返回"惯性→体"的 DCM，因此"体→惯性"取其转置；`Rvector3 * Rmatrix33` 按行向量约定右乘旋转阵（GMAT 向量为行向量，见 [MD-06](../math-deep-dive/MD-06-linearalgebra.md) 若存在，或 [CH06](../CH06-dynamics.md) 坐标系统一节）。**注意** `TransformJ2kToBurnOrigin`（`Burn.cpp:1297-1344`）另做位置平移（`state += (r_J2000body − r_origin)`，`:1315`、`:1331-1336`），用于 burn 原点 ≠ J2000 天体的情形。
  - 与坐标系统的联动：局部坐标系在 `SetSpacecraftToManeuver`（`Burn.cpp:983-1020`）与 `Initialize`（`:1092-1093`）中创建，因此旋转矩阵随**机动时刻的轨道状态**变化——同一条 Δv 在轨道不同位置施加，惯性结果不同。

### 2.3 反向传播：逆机动的定点迭代
- **公式**：求解使"反向点火后再正向点火回到起点"的 $\mathbf{b}$（模长固定为 $\|\Delta\mathbf{v}\|$）：
$$\mathbf{b}^{(k+1)} = \left[\mathbf{b}^{(k)} + \left(\mathbf{v}_{\text{start}}-\mathbf{v}_{\text{end}}^{(k)}\right)\right]\cdot\frac{\|\Delta\mathbf{v}\|}{\|\mathbf{b}^{(k)}+\left(\mathbf{v}_{\text{start}}-\mathbf{v}_{\text{end}}^{(k)}\right)\|},\quad \mathbf{v}_{\text{end}}^{(k)}=\mathbf{v}_{\text{start}}+\mathbf{b}^{(k)}+\Delta\mathbf{v}_I$$
迭代终止：$\varepsilon_k=\sum_i|v_{\text{start},i}-v_{\text{end},i}^{(k)}|<10^{-15}$ 或 50 次；不收敛则退回 $\mathbf{v}=\mathbf{v}_{\text{start}}-\Delta\mathbf{v}_I$。
- **代码位置**：`src/base/burn/ImpulsiveBurn.cpp:268-349`（`do/while` 循环），常量 `:46-47`（`BACKPROP_PRECISION=1.0e-15`、`BACKPROP_ITERATIONS=50`）
- **深度讲解**：
  - 工程背景：反向传播（backprop）要求"反向机动是正向机动的精确逆"。由于 Δv 的惯性化旋转依赖机动时刻的**航天器状态**（局部轴随状态变），直接施加 $-\Delta\mathbf{v}_I$ 再用 $\Delta\mathbf{v}_I$ 反演不会回到起点（旋转参考系不同），所以代码用定点迭代校正。
  - 实现细节（核心迭代 `:292-337`）：
    ```cpp
    294:    if (eps != 0.0) {                    // 首轮跳过，之后每轮校正
    297:       satState[3..5] = theV[0..2];       // 复位速度到起点
    302:       trialBurn[i] += satState[i+3] - endState[i];  // 误差修正方向
    307:       tbMag = sqrt(trialBurn[0]^2+...);  // 修正后的模长
    308:       trialBurn[i] *= mag / tbMag;       // 重新归一化到目标 |Δv|
    317:    satState[3..5] += trialBurn[0..2];    // 施加试探反向 Δv
    322:    ConvertDeltaVToInertial(deltaV, deltaVInertial, epoch); // 正向 Δv（当前状态系）
    324:    endState[i] = satState[i+3] + deltaVInertial[i];        // 模拟正向点火终点
    329:    eps = Σ|theV[i] - endState[i]|;       // 与起点的偏差
    ```
    逐行注释：每轮先用"当前试探的反向 Δv"推一次，再在当前终态系下加正向 $\Delta\mathbf{v}_I$，检查是否回到起点；偏差按向量误差修正试探方向并把模长钉死在 `mag`（第 285 行的 $\|\Delta\mathbf{v}\|$）；这是把"旋转依赖状态"这一非线性效应压到 $<10^{-15}$ 的 Picard 型迭代。
  - 数值特性：50 次上限意味着欠收敛时给出警告（`:339-344`）并退化为朴素 $\mathbf{v}_{\text{start}}-\Delta\mathbf{v}_I$（`:346-348`）；该退化在旋转随状态变化剧烈的场景（如大 Δv、低轨）可能不可逆，使用时应留意警告。

### 2.4 火箭方程：燃尽质量与推进剂消耗
- **公式**（正向，`ImpulsiveBurn.cpp:1181`）：$$\Delta m = M_0\left(e^{-\|\Delta\mathbf{v}\|\,(1000)/(I_{\text{sp}}\,g)}-1\right),\qquad M_1 = M_0+\Delta m = M_0\,e^{-\|\Delta\mathbf{v}\|\,(1000)/(I_{\text{sp}}\,g)}$$
  反向（`:1183`）指数取正号（回加质量）；$\|\Delta\mathbf{v}\|$ 单位为 km/s，乘 1000 化为 m/s。
- **代码位置**：`src/base/burn/ImpulsiveBurn.cpp:1164-1240`（`DecrementMass`）
- **深度讲解**：
  - 工程背景：由齐奥尔科夫斯基方程 $M_1=M_0\exp(-\Delta v/v_e)$ 与排气速度 $v_e=I_{\text{sp}}g$。GMAT 的 `GravitationalAccel` 参数默认 **9.81 m/s²**（`ImpulsiveBurn.cpp:87`、`Thruster.cpp:136`），**不是** SI 标准 $g_0=9.80665$——这是可配置参数，改它直接改变 Δm 结算，高精度任务应显式设置。
  - 实现细节：
    ```cpp
    1171:    totalTankMass = spacecraft->GetRealParameter("TotalMass"); // 机动前总质量
    1179:    Real dv = sqrt(deltaV[0]*deltaV[0] + ...);                  // |Δv| (km/s)
    1180:    if (!backwards)
    1181:       deltaTankMass = totalTankMass * (exp(-dv*1000/(isp*gravityAccel)) - 1.0);
    1182:    else
    1183:       deltaTankMass = totalTankMass * (exp( dv*1000/(isp*gravityAccel)) - 1.0);
    1190:    totalTankMass = totalTankMass + deltaTankMass;              // 新总质量
    1219:    Integer paramID = currTank->GetParameterID("FuelMass");
    1220:    Real oldTankMass = currTank->GetRealParameter(paramID);
    1221:    Real currTankMass = oldTankMass + deltaTankMass;            // 箱质量结算
    1227:    currTank->SetRealParameter(paramID, currTankMass);
    ```
    逐行注释：$\Delta m<0$ 表示消耗；`FuelMass` 是 FuelTank 的公开参数（`FuelTank.cpp:495-518` 校验非负或 `AllowNegativeFuelMass`）；多箱场景代码只支持单箱（`:1200-1203` 抛异常），注释明示多箱按比例分摊尚未实现。
  - 与传播器/力模型联动：脉冲机动不经过 ODE，质量一次性结算；有限推力则把 $\dot m$ 作为状态元素交给积分器逐步积分（见 4.2 节）。

---

## 三、有限推力机动：FiniteBurn

### 3.1 单推力器加速度与合加速度/合推力合成
- **公式**（`FiniteBurn.cpp:350-351`、`:354-356`）：
$$\mathbf{a} = \sum_i \frac{T_i\cdot \text{TSF}_i\cdot \text{DC}_i}{m\,\|\hat{\mathbf{d}}_i\|\cdot 1000}\,\hat{\mathbf{d}}_i\quad(\text{km/s}^2),\qquad \mathbf{F}_{\text{tot}}=\sum_i \frac{\hat{\mathbf{d}}_i}{\|\hat{\mathbf{d}}_i\|}\,T_{i}^{\text{applied}}$$
- **代码位置**：`src/base/burn/FiniteBurn.cpp:311-380`（`Fire` 内推力器循环）
- **深度讲解**：
  - 工程背景：有限推力把推力视为持续加速度源。状态单位 km/s，故 $\vec a=F/m$ 的 m/s² 要除以 1000；`thrustScaleFactor`（TSF）与 `dutyCycle`（DC）是推力器级标定/占空比参数。质量取 `burnMass`（若 `SetManeuverEpochAndState` 传入）否则 `TotalMass`（`:284-287`）。
  - 实现细节：
    ```cpp
    330:    current->ComputeInertialDirection(epoch);   // 体轴推力方向→惯性系
    331:    dir = current->inertialDirection;
    332:    norm = sqrt(dir[0]*dir[0] + dir[1]*dir[1] + dir[2]*dir[2]); // 冗余归一
    340:    if (norm == 0.0) throw ...                 // 方向为零则报错
    348:    dm += current->CalculateMassFlow();        // 累计各推力器质量流率
    350:    tOverM = current->thrust * current->thrustScaleFactor *
    351:             current->dutyCycle / (tMass * norm * 1000.0);       // a = T/(m·1000)
    354:    deltaV[0] += dir[0] * tOverM;              // 注意：deltaV 实为加速度
    364:    totalThrust[0] += dir[0]/norm * current->appliedThrustMag;  // 合推力矢量
    ```
    逐行注释：`thrust`/`appliedThrustMag`/`mDot` 由 `CalculateThrustAndIsp()` 与 `CalculateMassFlow()` 在本轮求值（见第 5 节）；`FiniteBurn` 被声明为 `Thruster` 的友元（`Thruster.hpp:145`）直接读成员；`dir` 已由惯性化（`ComputeInertialDirection`，`Thruster.cpp:2090-2094`），`norm` 只是防御性归一。第 354-356 行累加的是**加速度**，`deltaV` 字段名具历史性（注释 `:353`"deltaV is really totalAcceleration"）。
  - 与传播器/力模型联动：每步每个导数求值点调用一次 `Fire`，因此推力随状态、时间、功率实时变化；`isElectricBurn` 时先做节流分配（3.3 节）。
  - 参数表（`FiniteBurn.hpp:135-142`，默认 `FiniteBurn.cpp:96-97`）：

    | 参数名 | 类型 | 含义 |
    |---|---|---|
    | `Thrusters` | 对象数组 | 参与机动的推力器名（`FiniteBurn.cpp:726-732`） |
    | `Tanks`（弃用） | 对象数组 | 旧接口，已忽略（`:705-709`） |
    | `BurnScaleFactor`（弃用） | Real | 旧接口，返回哨兵（`:847-848`） |
    | `ThrottleLogicAlgorithm` | 字符串 | 电推进节流算法，现仅 `MaxNumberOfThrusters`（`:710-720`） |

### 3.2 burnData 组装与帧基投影
- **公式**：$$\begin{bmatrix}\dot v_x\\\dot v_y\\\dot v_z\\\dot m\end{bmatrix}_{\text{burn}} = \begin{bmatrix}\mathbf{B}\,\mathbf{a}\\ \sum_i\dot m_i\end{bmatrix},\quad (\mathbf{B})_{ij}=\text{frameBasis}[i][j]$$
- **代码位置**：`src/base/burn/FiniteBurn.cpp:401-413`
- **深度讲解**：
  - `burnData[0..2]` 是加速度（km/s²）、`burnData[3]` 是质量流率（kg/s），被 `FiniteThrust::GetDerivatives` 直接累加（`FiniteThrust.cpp:728-741`）。
  - 实现细节：
    ```cpp
    401:    burnData[0] = deltaV[0]*frameBasis[0][0] + deltaV[1]*frameBasis[0][1] +
    402:                  deltaV[2]*frameBasis[0][2];     // 行 0 点乘加速度
    404:    burnData[1] = deltaV[0]*frameBasis[1][0] + ... // 行 1
    407:    burnData[2] = deltaV[0]*frameBasis[2][0] + ... // 行 2
    410:    burnData[3] = dm;                              // 质量流率
    413:    totalMassFlowRate = dm;                        // 供 GetTotalMassFlowRate()
    ```
    逐行注释：`frameBasis[3][3]`（`Burn.hpp:164`）在现行代码中恒为单位阵（`Burn.cpp:144-146`，无其他写入点）——方向旋转已由 `ComputeInertialDirection` 完成，此处的帧基投影是遗留钩子；若未来恢复 `ManeuverFrame` 装配（见 [CH07](../CH07-propagator.md) 2.2），该投影可把加速度旋回机动系输出。
  - `totalAccel`（`:388-390`）与 `deltaVInertial`（`:383-385`）同值保存，供 `GetTotalAcceleration()`/`GetDeltaVInertial()` 查询（`Burn.cpp:349-355`）。

### 3.3 电推进节流分配（MaxNumberOfThrusters）
- **公式**：$$P_{\text{per}}=\frac{P_{\text{avail}}}{n_{\text{fire}}},\qquad n_{\text{fire}}=\max\left\{n:\frac{P_{\text{avail}}}{n}>\frac{1}{n}\sum_{j<n}P_{\min,j}\right\}$$
即从"全部点火"向下逐台减少，直到每台分到的功率大于前 $n$ 台的最小可用功率均值；若一台都点不燃则 $n_{\text{fire}}=0$。
- **代码位置**：`src/base/burn/FiniteBurn.cpp:1283-1386`（`ComputeThrottleLogic`），核心 `:1330-1375`
- **深度讲解**：
  - 工程背景：电推力器只能在 `[MinimumUsablePower, MaximumUsablePower]` 功率窗口内工作（`ElectricThruster::Initialize` 校验 $P_{\max}>P_{\min}$，`ElectricThruster.cpp:728-736`）。航天器可用功率（`spacecraft->GetThrustPower()`，`FiniteBurn.cpp:307`）有限时，要决定"点几台、每台分多少电"。
  - 实现细节：
    ```cpp
    1330:    Integer numToFire = numThrusters;             // 从全部点火开始
    1332:    for (Integer ii = numThrusters-1; ii >= 0; ii--) {
    1334:       powerPerThruster = powerAvailable / numToFire;
    1337:       for (jj < numToFire)
    1338:          meanMinUsablePower += minUsablePowerPerThruster.at(ii); // 注：只累加第 ii 台
    1339:       meanMinUsablePower /= numToFire;
    1341:       if (powerPerThruster > meanMinUsablePower) break;   // 够分，保持当前台数
    1345:       if ((numToFire == 1) && (powerPerThruster < meanMinUsablePower)) {
    1347:          numToFire = 0; break;                             // 一台都点不燃
    1358:    for (nn < numToFire)
    1364:       electricThrusters.at(nn)->SetPower(powerPerThruster); // 前 n 台均分功率
    1368:    for (nono = numToFire; nono < numThrusters; nono++)
    1374:       electricThrusters.at(nono)->SetPower(0.0);            // 其余断电
    ```
    逐行注释：实现细节与文档式算法略有出入——均值累加实际只叠加下标 `ii` 的值（`minUsablePowerPerThruster.at(ii)`，疑似笔误，`:1338`），因此比较基准退化为单台 `P_min[ii]`；`SetPower` 落到 `ElectricThruster::SetPower`（`ElectricThruster.cpp:767-778`）供 5.5 节功率钳制使用。功率分配后 `Fire` 循环内的 `CalculateMassFlow`（`ElectricThruster.cpp:886`）以 `power` 求推力。
  - 参数表：`MinimumUsablePower`/`MaximumUsablePower`（kW，默认 0.638/7.266，`ElectricThruster.cpp:129-130`）；算法名 `MaxNumberOfThrusters` 是当前唯一合法值（`FiniteBurn.cpp:711-719`）。

### 3.4 点火状态机与"点火时长"
- **公式**：无显式点火时长解析式——有限推力的点火时长由任务序列定义：$$t_{\text{burn}}=t_{\text{EndFiniteBurn}}-t_{\text{BeginFiniteBurn}}$$（其间 `Propagate` 携带停止条件推进；推进剂总消耗 = $\int_{t_0}^{t_0+t_{\text{burn}}}\dot m(t)\,dt$ 由积分器完成）。
- **代码位置**：`src/base/command/BeginFiniteBurn.cpp:623-729`（`IsFiring=true` 于 `:642`、瞬态力注册 `:673`/`:706`）、`src/base/command/EndFiniteBurn.cpp:471-585`（`IsFiring=false` 于 `:527`、移除 `:562`）
- **深度讲解**：
  - `BeginFiniteBurn::Execute`：逐台置 `IsFiring=true`（`:642`）→ `spacecraft->IsManeuvering(true)`（`:655`）→ `maneuver->SetSpacecraftToManeuver(*s)` + `TakeAction("SetData")`（`:657-658`，让参数在机动起点求值）→ 把 `burnForce`（`FiniteThrust`）push 进沙箱 `transientForces`（`:673`，去重逻辑 `:677-707`）。
  - `FiniteBurn::IsFiring`（`FiniteBurn.cpp:434-494`）：只要任一推力器 `thrusterFiring` 即返回 true，供 `Burn::GetTotalMassFlowRate`/`GetTotalAcceleration`（`Burn.cpp:330-355`）在**未点火时返回 0**。
  - `EndFiniteBurn::Execute`：置 `IsFiring=false`、`IsManeuvering(false)`、从 `transientForces` 擦除（`:527`、`:548`、`:562`），`FiniteThrust` 不再被调用，推力归零。
  - `SetManeuverEpochAndState(epoch, state, mass, origin)`（`FiniteBurn.cpp:230-237`）：允许外部（估计器/参数系统）传入机动求值的快照状态与质量，`Fire` 优先使用（`:284-287`、`:345-346` `SetDerivativeState`）。
  - 联动说明：`RungeKutta::Step` 检测到 `FileThrust` 时置 `hasFiniteBurn`（`RungeKutta.cpp:338-348`），点火/关火沿用"步长缩短 + 接力步"机制（见 7 节）。脉冲机动等效点火时长为 0，质量直接按 2.4 节结算。

---

## 四、有限推力力模型：FiniteThrust（瞬态力）

### 4.1 导数累加与状态写入
- **公式**：$$\dot{\mathbf{r}}=0,\quad \dot{\mathbf{v}}=\sum_{b}\mathbf{a}_b(t),\quad \dot{m}=\sum_b \dot m_b(t)$$
写入导数向量：`deriv[3+i6..5+i6] = accel`（一阶，`order==1` 时位置导数为 0 由其他力模型补），`deriv[mDotIndex+i] = mDot`。
- **代码位置**：`src/base/forcemodel/FiniteThrust.cpp:657-827`（`GetDerivatives`），累加 `:728-741`，写入 `:765-788`
- **深度讲解**：
  - 工程背景：`FiniteThrust` 是"瞬态力"（`IsTransient()=true`，`:500-503`）——只有 `BeginFiniteBurn` 点火期间挂在 ODEModel 上（见 3.4 节与 `ODEModel::UpdateTransientForces`，`ODEModel.cpp:2551-2604`）。它不实现自己的导数源，而是调用关联 `FiniteBurn::Fire` 取数。
  - 实现细节：
    ```cpp
    714:    mDot = accel[0] = accel[1] = accel[2] = 0.0;   // 每步归零
    717:    for (fb = burns.begin(); fb != burns.end(); ++fb) {
    721:       (*fb)->SetSpacecraftToManeuver((Spacecraft*)sat);
    722:       Real now = epoch + (elapsedTime + dt) / GmatTimeConstants::SECS_PER_DAY; // 当前历元
    723:       if ((*fb)->Fire(burnData, now)) {
    728:          accel[0] += burnData[0];                    // 累加各 burn 的加速度
    729:          accel[1] += burnData[1];
    730:          accel[2] += burnData[2];
    736:          if ((*fb)->DepletesMass()) {
    738:             if (order != 1) throw ...;               // 质量消耗仅支持一阶
    741:             mDot += burnData[3];                     // 累加质量流率
    765:    if (order == 1) {
    768:       deriv[i6]=deriv[1+i6]=deriv[2+i6]=0.0;        // 位置导数置 0（速度类力）
    771:       deriv[3+i6]=accel[0]; deriv[4+i6]=accel[1]; deriv[5+i6]=accel[2];
    775:       if (mloc >= 0)
    777:          deriv[mloc+i] = mDot;                      // dm/dt 写入质量流元素
    ```
    逐行注释：`i6 = cartIndex + i*6`（`:678`）是该航天器笛卡尔状态起点；`mloc = mDotIndex + j`（`:684`）是质量流状态元素位置；`now` 用 `epoch + (elapsedTime+dt)/86400`（`SECS_PER_DAY=86400.0`，`src/gmatutil/util/GmatConstants.hpp:136`）把积分器时间转为儒略日历元传给 `Fire`；`order != 1` 抛异常表示质量消耗不能用于二阶（如 STM 二阶导数）传播。
  - 与传播器联动：`Fire` 每导数调用点都重算（含 RK 各阶段），因此 `ComputeThrottleLogic`、`CalculateMassFlow` 也被逐点触发；这保证推力随质量/功率实时演化，但要求积分器能正确处理步内开关（见 7 节步长截断）。

### 4.2 状态元素注册（CARTESIAN_STATE / MASS_FLOW）
- **公式**：$$n_{\text{state}}=6\,n_{\text{sat}}+n_{\text{massFlow}}$$（每个耗质量航天器多一个 MASS_FLOW 元素）
- **代码位置**：`src/base/forcemodel/FiniteThrust.cpp:921-943`（`SupportsDerivative`）、`:961-1009`（`SetStart`）
- **深度讲解**：
  - `SupportsDerivative` 声明支持 `CARTESIAN_STATE` 与 `MASS_FLOW`（`:928-940`）。
  - `SetStart` 由 `PropagationStateManager` 初始化时调用（见 [CH07](../CH07-propagator.md)），记录 `cartIndex`/`mDotIndex`：
    ```cpp
    973:    case Gmat::CARTESIAN_STATE:
    974:       satCount = quantity; cartIndex = index; fillCartesian = true; break;
    996:    case Gmat::MASS_FLOW:
    998:       satThrustCount = quantity; mDotIndex = index; depleteMass = true; break;
    ```
    逐行注释：`depleteMass` 被置 true 表示该力参与质量流状态；`FiniteThrust::DepletesMass()`（`:514-517`）返回它，供 `GetDerivatives` 决定是否写 `deriv[mloc]` 与 `Fire` 侧 `dm` 累加（3.2 节 `burnData[3]`）。初始化还校验每个 `FiniteBurn` 至少指定一个推力器（`:612-621`）。

---

## 五、推力器硬件：Thruster / ChemicalThruster / ElectricThruster

### 5.1 推力方向：体轴系→惯性系旋转（推力矢量在体轴系旋转）
- **公式**：$$\hat{\mathbf{d}}_I=\hat{\mathbf{d}}_B\,\mathbf{R}_{BI}^{\mathsf T}\ (\text{SpacecraftBody}),\qquad \hat{\mathbf{d}}_I=\mathbf{R}_{\text{cs}}\,\hat{\mathbf{d}}_{\text{cs}}\ (\text{其他坐标系})$$
- **代码位置**：`src/base/hardware/Thruster.cpp:1977-2084`（`ConvertDirectionToInertial`）、`:2090-2094`（`ComputeInertialDirection`）
- **深度讲解**：
  - 工程背景：推力器的 `ThrustDirection1/2/3`（`Thruster.cpp:464-471`）是**本体系**单位方向（默认 `(1,0,0)`，`Thruster.cpp:161-163`）；点火时须旋到惯性系才能与轨道状态相加。局部轴选项与 `Burn` 一致（VNB/LVLH/MJ2000Eq/SpacecraftBody，`Thruster.cpp:167-171`）。
  - 实现细节（体轴分支）：
    ```cpp
    2043:    else if (isSpacecraftBodyAxes) {
    2045:       Rvector3 inDir(dir[0], dir[1], dir[2]);
    2050:       Rmatrix33 inertialToBody = spacecraft->GetAttitude(epoch);
    2051:       Rmatrix33 rotMat = inertialToBody.Transpose();  // 惯性→体 转置得 体→惯性
    2052:       outDir = inDir * rotMat;                        // 行向量右乘
    2053:       for (i<3) dirInertial[i] = outDir[i];
    2068:    localCoordSystem->ToBaseSystem(A1Mjd(epoch), inDir, outDir, true); // 其余局部系
    ```
    逐行注释：与 `Burn::ConvertDeltaVToInertial`（2.2 节）同构；MJ2000Eq 直通（`Thruster.cpp:2036-2042`）；`ComputeInertialDirection` 缓存 `inertialEpoch` 后调用本函数（`:2090-2094`），由 `FiniteBurn::Fire` 每点调用（`FiniteBurn.cpp:330`）。
  - 与姿态模型联动：`GetAttitude(epoch)` 来自 `Attitude`（见 [CH07](../CH07-propagator.md) 2.3）；姿态变化（自旋/指向）会实时改变惯性推力方向——这是"推力矢量随姿态旋转"的数学入口。
  - 参数表（`Thruster.hpp:226-243` 枚举）：

    | 参数名 | 类型 | 含义（默认值，`Thruster.cpp:135-145`） |
    |---|---|---|
    | `CoordinateSystem/Origin/Axes` | 对象/枚举 | 方向参考系（默认 Local/VNB） |
    | `ThrustDirection1/2/3` | Real | 体轴推力方向（默认 1,0,0） |
    | `DutyCycle` | Real ∈ [0,1] | 占空比（默认 1.0） |
    | `ThrustScaleFactor` | Real ≥ 0 | 推力比例因子（默认 1.0） |
    | `DecrementMass` | 布尔 | 是否消耗燃料（默认 false） |
    | `Tank` / `MixRatio` | 对象数组/Rvector | 供箱与混合比 |
    | `GravitationalAccel` | Real > 0 | 比冲换算重力加速度（默认 9.81 m/s²） |
    | `Thrust` / `Isp` / `MassFlowRate` / `AppliedThrustMag` | Real（只读） | 最近一次求值的推力量级/比冲/质量流/实际推力 |

### 5.2 化学推力器：推力与 Isp 的 16 系数多项式
- **公式**（`ChemicalThruster.cpp:776-780` 文档式）：
$$F(P,T)=C_1+C_2P+\left\{C_3+C_4P+C_5P^2+C_6P^{C_7}+C_8P^{C_9}+C_{10}P^{C_{11}}+C_{12}C_{13}^{C_{14}P}\right\}\left(\frac{T}{T_{\text{ref}}}\right)^{1+C_{15}+C_{16}P}$$
$$I_{sp}(P,T)=K_1+K_2P+\left\{K_3+K_4P+K_5P^2+K_6P^{K_7}+K_8P^{K_9}+K_{10}P^{K_{11}}+K_{12}K_{13}^{K_{14}P}\right\}\left(\frac{T}{T_{\text{ref}}}\right)^{1+K_{15}+K_{16}P}$$
- **代码位置**：`src/base/hardware/ChemicalThruster.cpp:798-893`（`CalculateThrustAndIsp`），求值 `:843-878`；系数单元表 `:127-162`
- **深度讲解**：
  - 工程背景：化学推力器的推力/比冲随**箱压 P（kPa）与温度比 T/T_ref** 变化（吹除式贮箱压力下降 → 推力衰减，见 6.2 节）。C1-C16/K1-K16 是 16 个拟合系数，代码下标与文档编号差 1（`cCoefficients[0]=C1`）。
  - 实现细节（温度/压强混合与求值）：
    ```cpp
    831:    for (i < mixRatio.GetSize()) {
    833:       mixTotal += mixRatio[i];
    834:       pressureSum += tanks[i]->GetRealParameter(pressID) * mixRatio[i];
    835:       tempSum     += tanks[i]->GetRealParameter(tempID)    * mixRatio[i];
    836:       refTempSum  += tanks[i]->GetRealParameter(refTempID) * mixRatio[i];
    838:    pressure = pressureSum / mixTotal;                    // 混合压强（加权平均）
    841:    temperatureRatio = tempSum / refTempSum;              // 混合温度比
    843:    thrust = cCoefficients[2]; impulse = kCoefficients[2];  // 常数项 C3/K3
    846:    if (!constantExpressions) {                           // 有非零 C2/C4/C5/… 时
    849:       thrust  += pressure*(cCoefficients[3] + pressure*cCoefficients[4]);
    850:       impulse += pressure*(kCoefficients[3] + pressure*kCoefficients[4]);
    854:       if (!simpleExpressions) {                          // 高次项（C6..C13）
    855:          thrust += C5*pow(P,C6) + C7*pow(P,C8) + C9*pow(P,C10) +
    858:                    C11*pow(C12, P*C13);
    861:          impulse += K5*pow(P,K6) + K7*pow(P,K8) + K9*pow(P,K10) +
    864:                    K11*pow(K12, P*K13);
    871:    thrust  *= pow(temperatureRatio, 1 + C14 + P*C15);    // 温度指数项
    873:    impulse *= pow(temperatureRatio, 1 + K14 + P*K15);
    877:    thrust  += C1 + C2*P;                                 // 温度无关项最后加
    878:    impulse += K1 + K2*P;
    884:    appliedThrustMag = thrustScaleFactor * dutyCycle * thrust; // 实际推力
    ```
    逐行注释：`constantExpressions`/`simpleExpressions` 标志在 `SetRealParameter` 中按"哪些系数非零"自动维护（`ChemicalThruster.cpp:527-694`）——全零时跳过全部多项式求值（高性能路径）；温度指数项在代码里先乘后加常数项（与文档式展开等价，注意代码顺序）。
  - 数值特性：P 以 kPa、T 以 ℃（文档注释 `:782-783`）；指数项 `pow(P, C7)` 要求 P>0；默认系数 `C1=10 N, K1=300 s`（`:118-124`）。

### 5.3 化学推力器质量流率
- **公式**：$$\dot m=-\frac{T\cdot \text{DC}}{g\,I_{sp}}$$
- **代码位置**：`src/base/hardware/ChemicalThruster.cpp:907-957`（`CalculateMassFlow`），核心 `:937`、`:955`
- **深度讲解**：
  - 工程背景：由 $\dot m=T/v_e$、$v_e=I_{sp}g$ 得 $\dot m=T/(I_{sp}g)$；负号表示质量流出。注意 `g` 是**可配置** `gravityAccel`（默认 9.81，`Thruster.cpp:136`），不是硬编码 $g_0=9.80665$。
  - 实现细节：
    ```cpp
    936:    if (decrementMass)
    937:       mDot = -thrust / (gravityAccel * impulse);   // 负号：质量流出
    938:    else
    939:       mDot = 0.0;
    955:    mDot = mDot * dutyCycle;                        // 占空比折减
    ```
    逐行注释：`impulse==0` 抛异常（`:930-932`）；`decrementMass=false` 时只出力不出质量（模拟无燃料/固定质量）；`dutyCycle` 在最后乘，与 5.2 节 `appliedThrustMag` 的 DC 处理一致。
  - 联动：该 `mDot` 经 `FiniteBurn::Fire` 的 `dm += current->CalculateMassFlow()`（`FiniteBurn.cpp:348`）汇入 `burnData[3]`，再经 `FiniteThrust` 写入 `MASS_FLOW` 状态元素；`Spacecraft` 的质量状态元素由积分器推进（见 [CH06](../CH06-dynamics.md) 2.1.7 与 6.3 节箱质量分摊）。

### 5.4 电推力器：ThrustMassPolynomial 四阶功率多项式
- **公式**：$$T(P)=\frac{a_4P^4+a_3P^3+a_2P^2+a_1P+a_0}{10^3}\ (\text{N}),\qquad \dot m(P)=\frac{b_4P^4+b_3P^3+b_2P^2+b_1P+b_0}{10^6}\ (\text{kg/s})$$
- **代码位置**：`src/base/hardware/ElectricThruster.cpp:793-865`（`CalculateThrustAndIsp`），多项式 `:828-840`；默认系数 `:144-154`
- **深度讲解**：
  - 工程背景：电推进推力/质量流是**输入功率 P（kW）**的函数（喷流功率→推力的经验拟合）。系数量级：`thrustCoeff` 除 1e3 得 N（原始量级 mN），`massFlowCoeff` 除 1e6 得 kg/s（原始量级 mg/s）。
  - 实现细节：
    ```cpp
    886:    powerToUse = power;              // 由 FiniteBurn::SetPower 分配
    912:    if (powerToUse > maxUsablePower) powerToUse = maxUsablePower; // 上限钳制
    915:    powerToUse2 = powerToUse * powerToUse;      // P²
    916:    powerToUse3 = powerToUse2 * powerToUse;     // P³
    917:    powerToUse4 = powerToUse3 * powerToUse;     // P⁴
    826:    else if (thrustModel == "ThrustMassPolynomial") {
    828:       thrust = ((thrustCoeff[4]*powerToUse4) + (thrustCoeff[3]*powerToUse3) +
    830:                (thrustCoeff[2]*powerToUse2) + (thrustCoeff[1]*powerToUse) +
    832:                thrustCoeff[0]) / 1.0e3;
    834:       Real mdot = ((massFlowCoeff[4]*powerToUse4) + ... + massFlowCoeff[0]) / 1.0e6;
    840:       impulse = thrust / (mdot * gravityAccel);   // Isp = T/(ṁ·g)
    862:    appliedThrustMag = thrustScaleFactor * dutyCycle * thrust;
    ```
    逐行注释：默认系数（`:144-154`）为真实电推拟合值；`impulse` 由多项式比值反推（保证 $\dot m=T/(I_{sp}g)$ 自洽）；`thrust<0` 时清零（`:853-857`）。
  - 参数表（`ElectricThruster.cpp:68-89`）：

    | 参数名 | 类型 | 含义（默认值） |
    |---|---|---|
    | `ThrustModel` | 枚举 | `ThrustMassPolynomial`（默认）/`ConstantThrustAndIsp`/`FixedEfficiency` |
    | `MaximumUsablePower` | Real | 功率上限 kW（默认 7.266） |
    | `MinimumUsablePower` | Real | 功率下限 kW（默认 0.638） |
    | `ThrustCoeff1..5` / `MassFlowCoeff1..5` | Real | 五阶系数（默认见 `:144-154`） |
    | `Efficiency` | Real | 固定效率 η（默认 0.7，FixedEfficiency 用） |
    | `Isp` | Real | 固定比冲 s（默认 4200，Constant/Fixed 用） |
    | `ConstantThrust` | Real | 恒定推力 N（默认 0.237） |

### 5.5 电推力器：ConstantThrustAndIsp 与 FixedEfficiency 模型
- **公式**（`ElectricThruster.cpp:842-849`）：
$$\text{ConstantThrustAndIsp:}\quad T=T_c,\ \dot m=\frac{T_c}{I_{sp}\,g};\qquad \text{FixedEfficiency:}\quad T=\frac{2\eta P}{I_{sp}\,g\cdot 0.001},\ \dot m=\frac{2\eta P\cdot 0.001}{(I_{sp}\,g\cdot 0.001)^2}$$
- **代码位置**：`src/base/hardware/ElectricThruster.cpp:842-849`（推力）、`:937-946`（质量流）
- **深度讲解**：
  - 工程背景：`ConstantThrustAndIsp` 把推力钉死为常数（不随功率变，用于任务设计初筛）；`FixedEfficiency` 由喷流功率 $P_j=\eta P$ 与 $T=2P_j/v_e$（$v_e=I_{sp}g$）导出：$T=2\eta P/v_e$。功率 P 以 kW 计，代码除以 0.001 完成 kW→W 换算。
  - 实现细节：
    ```cpp
    937:    else if (thrustModel == "ConstantThrustAndIsp")
    939:       mDot = constantThrust / (isp * gravityAccel);        // T/(Isp·g)
    941:    else {                                                  // FixedEfficiency
    943:       Real ispG  = (isp * gravityAccel * 0.001);          // v_e×0.001（kW 换算）
    944:       Real ispG2 = ispG * ispG;
    945:       mDot = (2.0 * efficiency * powerToUse * 0.001) / ispG2;  // 2ηP/v_e²
    965:    mDot = mDot * -dutyCycle;                               // 负号在最后
    ```
    逐行注释：质量流公式与 $T=2\eta P/v_e$ 一致（$\dot m=T/v_e=2\eta P/v_e^2$）；`mDot` 的负号在**最后**统一乘（与化学推力器不同，化学机在中间乘 DC）；`powerToUse < minUsablePower` 时推力/质量流清零（`:902-910`）。
  - 与节流联动：三种模型都在 3.3 节 `ComputeThrottleLogic` 分配功率之后求值；`SetPower`（`ElectricThruster.cpp:767-778`）只存 `power`，钳制在 `CalculateMassFlow` 内完成（`:912-913`）。

---

## 六、贮箱：FuelTank / ChemicalTank / ElectricTank 与箱质量分摊

### 6.1 燃料质心与惯量（BCS 表达）
- **公式**（`FuelTank.cpp:751-766`、`:778-804`）：
$$\mathbf{r}_{cm}^{\text{BCS}}=\mathbf{r}_b+\mathbf{R}_{SB}^{\mathsf T}\mathbf{r}_T,\qquad \mathbf{I}^{\text{BCS}}=\mathbf{R}_{SB}^{\mathsf T}\mathbf{I}_t\mathbf{R}_{SB}+m_f\left(|\mathbf{r}|^2\mathbf{I}_3-\mathbf{r}\mathbf{r}^{\mathsf T}\right),\ \mathbf{r}=\mathbf{r}_{cm}^{\text{BCS}}-\mathbf{R}_{CM}^{\text{SC}}$$
- **代码位置**：`src/base/hardware/FuelTank.cpp:751-766`、`:778-804`
- **深度讲解**：
  - 工程背景：`FuelTank` 是抽象基类（`FuelTank.hpp:47`），提供燃料质量特性。`fuelCM`/`fuelMOI` 为**箱坐标系**量（`FuelTank.hpp:113-115`）；`R_SB` 是"箱体→航天器体"安装旋转阵（Hardware 基类成员），转置 $\mathbf{R}_{SB}^{\mathsf T}$ 把箱坐标旋到 BCS；$\mathbf{r}_b$ 是箱安装原点（`HW_ORIGIN_BCS_[XYZ]`）。
  - 实现细节（`GetFuelCM_BCS`）：
    ```cpp
    758:    Rvector3 rcm;
    759:    Rvector3 rb(location[0], location[1], location[2]);  // 箱原点在 BCS 的位置
    761:    Rmatrix33 MTB = R_SB.Transpose();                    // 箱→体旋转
    763:    rcm = rb + (MTB * fuelCM);                           // 平移 + 旋转
    ```
    惯量（`:800-801`）是平行轴定理 + 旋转相似变换：`(MTB * fuelMOI * R_SB) + m·(|r|²I₃ − rrᵀ)`。这些量供 `Spacecraft::UpdateMassProperties`（见 [CH06](../CH06-dynamics.md) 2.3）计算整星质心/惯量，间接影响姿态动力学。
  - 参数表（`FuelTank.hpp:128-151`）：`FuelMass`（kg，默认 756，`FuelTank.cpp:115`）、`FuelCenterOfMassX/Y/Z`、`FuelMomentOfInertiaXX..ZZ`（箱系）、`*_BCS` 派生量（只读）、`AllowNegativeFuelMass`（布尔）。

### 6.2 化学箱吹除模式压强更新（理想气体定容）
- **公式**：$$V_G=V_T-\frac{M_F}{\rho},\qquad P_f=\frac{P_i\,V_{G,i}}{V_{G,f}}$$
- **代码位置**：`src/base/hardware/ChemicalTank.cpp:824-852`（`UpdateTank`），初值 `:787-788`
- **深度讲解**：
  - 工程背景：吹除式（blow-down）贮箱按理想气体 $PV=nRT$ 定容演化（`:806-822` 文档注释）：燃料减少 → 气腔增大 → 压强下降 → 化学推力器推力衰减（5.2 节 P 项）。压力调节模式（`TPM_PRESSURE_REGULATED`）跳过更新（`:826`）。
  - 实现细节：
    ```cpp
    787:    gasVolume = volume - fuelMass / density;   // 初始气腔体积
    788:    pvBase = pressure * gasVolume;             // 保存 P·V 常数
    839:    gasVolume = volume - fuelMass / density;   // 更新后气腔体积
    845:    pressure = pvBase / gasVolume;             // P = (P_i V_i)/V_f
    ```
    逐行注释：`fuelMass/density` 是燃料体积，`volume` 是箱总容积；`DepleteFuel`（`:864-872`）直接 `fuelMass -= dm` 并在负质量时抛异常（该抽象虚函数由箱质量流结算调用，现结算走 `Spacecraft::ApplyTotalMass`，见 6.3 节）。
  - 联动：`ChemicalTank::Validate`（`:874-881`）要求 $\rho>0$ 且 $V_T-M_F/\rho\ge 0$；`ElectricTank` 的 `UpdateTank/DepleteFuel` 为空实现（`ElectricTank.cpp:367-412` 全注释）——电箱不建模压力/体积演化，燃料质量只经 6.3 节总质量分摊更新。

### 6.3 箱质量按 MixRatio 分摊（Spacecraft::ApplyTotalMass）
- **公式**（`Spacecraft.cpp:9813`、`:9825`、`:9831-9832`）：
$$\Delta m_i=\Delta M_{\text{tot}}\,\frac{\dot m_i}{\sum_j \dot m_j},\qquad \Delta m_{\text{tank},k}=\frac{\Delta m_i}{\sum_l \text{mr}_l}\,\text{mr}_k,\qquad M_{\text{tank},k}^+=M_{\text{tank},k}+\Delta m_{\text{tank},k}$$
THF 直排箱（`:9852`）：$\Delta m_k=\Delta M_{\text{tot}}/N_{\text{tanks}}$。
- **代码位置**：`src/base/spacecraft/Spacecraft.cpp:9738-9871`（`ApplyTotalMass`）
- **深度讲解**：
  - 工程背景：积分器推进**总质量**状态后，GMAT 把总质量变化按"各点火推力器的质量流率占比 → 各推力器的 MixRatio 占比"两级分摊回各 `FuelTank::FuelMass`（`FuelTank.cpp:486-518` 校验非负）。`MixRatio` 在 `Thruster::Initialize` 中补齐为 1.0（`Thruster.cpp:1687-1692`）。
  - 实现细节：
    ```cpp
    9741:    Real massChange = newMass - CalculateTotalMass();   // 总质量变化（负=消耗）
    9759:    rate = ((Thruster*)(*i))->CalculateMassFlow();      // 各点火推力器流率
    9765:    totalFlow += rate;
    9811:    if (!IsEqual(totalFlow,0.0)) {
    9813:       dm = massChange * flowrate[i] / totalFlow;       // 第一级分摊
    9821:       Rvector mixRatio = activeThrusters[i]->GetRvectorParameter("MixRatio");
    9824:       mixTotal += mixRatio[imix];
    9825:       Real dmt = dm / mixTotal;
    9831:       usedTanks[j]->SetRealParameter("FuelMass",
    9832:             usedTanks[j]->GetRealParameter("FuelMass") + dmt * mixRatio[j]); // 第二级
    9852:       dm = massChange / thrustHistoryTanks.size();    // THF 直排箱均分
    9858:       if ((FuelMass + dm) < 0 && !AllowNegativeFuelMass) throw ...; // 耗尽检查
    9862:       thrustHistoryTanks[i]->SetRealParameter("FuelMass", FuelMass + dm);
    ```
    逐行注释：`flowrate` 直接取 `CalculateMassFlow()` 的返回值（化学机已乘 DC `:955`、电推已乘 −DC `:965`，见 5.3/5.5 节），因此分摊比例内含占空比；两级分母同时为 0（无点火、无直排箱且 massChange≠0）抛异常（`:9781-9789`）；THF 路径在 `FileThrust::GetDerivatives` 置 `SetFlowWithoutThruster(true)`（`FileThrust.cpp:1311-1314`）后被识别（`Spacecraft.cpp:9769-9775`）。
  - 与传播器联动：该函数在传播步间按 `newMass`（积分后的总质量）结算箱燃料，保证 `FuelMass` 与总质量自洽；负质量默认抛异常（除非 `AllowNegativeFuelMass`）。

---

## 七、ThrustFilePlugin：FileThrust（推力表格插值与角度旋转）

> 架构（THF 读取器→段对象→力模型→命令）见 [CH14](../CH14-plugins-b.md) 14.8 节，此处只讲插值/旋转/缩放公式。

### 7.1 段区间判定与数据段选择
- **公式**：$$e\in(t_s,t_e)\ \lor\ (e=t_s,\ \text{正向})\ \lor\ (e=t_e,\ \text{反向})$$
- **代码位置**：`plugins/ThrustFilePlugin/src/base/forcemodel/FileThrust.cpp:3134-3146`（`InSegmentInterval`）、`:1787-1843`（段选择）、`:2080-2099`（`GetSegmentData`）
- **深度讲解**：
  - THF 每段有 `Start_Epoch`/`End_Epoch`（`ThrustHistoryFile.cpp:87-90` 关键字）与剖面节点（`profile[i].time` 为相对段首的**天数**偏移，`ThrustHistoryFile.cpp:1396-1399` 由末节点时间定 `endEpoch`）。
  - 实现细节（边界方向性）：
    ```cpp
    3136:    if (begin < epoch && epoch < end) return true;   // 开区间内
    3139:    if (direction == 1.0 && begin == epoch) return true; // 正向含左端点
    3142:    if (direction == -1.0 && end == epoch) return true;  // 反向含右端点
    ```
    逐行注释：防止正向/反向传播在同一段首尾重复点火；段重叠时取**第一个**覆盖段（`:1788-1793`）；`GetSegmentData` 在剖面节点对间定位插值区间（`:2088-2096`）。

### 7.2 线性插值
- **公式**：$$u=\frac{t-t_0}{t_1-t_0},\qquad y(t)=y_0+u\,(y_1-y_0)$$
- **代码位置**：`plugins/ThrustFilePlugin/src/base/forcemodel/FileThrust.cpp:2193-2234`（`LinearInterpolate`）
- **深度讲解**：
  - 实现细节：
    ```cpp
    2209:    Real pct = 0.0;
    2210:    if ((dataSet[1][4] != dataSet[0][4]))
    2211:       pct = (offset - dataSet[0][4]) / (dataSet[1][4] - dataSet[0][4]); // 归一化位置
    2213:    if (dataBlock[5] == ThfDataSegment::LINEAR) {      // 推力/加速度插值
    2215:       dataBlock[0] = dataSet[0][0] + pct * (dataSet[1][0] - dataSet[0][0]);
    2216:       dataBlock[1] = dataSet[0][1] + pct * (dataSet[1][1] - dataSet[0][1]);
    2217:       dataBlock[2] = dataSet[0][2] + pct * (dataSet[1][2] - dataSet[0][2]);
    2219:    if (dataBlock[6] == ThfDataSegment::LINEAR)        // 质量流插值
    2220:       dataBlock[3] = dataSet[0][3] + pct * (dataSet[1][3] - dataSet[0][3]);
    ```
    逐行注释：`dataSet[0]`/`dataSet[1]` 分别装载当前节点与下一节点（`:2197-2207`）；`offset` 是相对段首的天数；推力与质量流可**各自独立**选插值方式（`dataBlock[5]`/`[6]` 分别存 `accelIntType`/`massIntType`，`FileThrust.cpp:1847-1848`，来源见 `ThrustHistoryFile.cpp:1402-1433`：`None`/`Linear`/`CubicSpline`，`ThrustVectorMethod` 为保留值实际不可用）。

### 7.3 样条插值（NotAKnot 三次样条，5 点模板）
- **公式**：以 $t_{i-1},t_i,t_{i+1},t_{i+2},t_{i+3}$ 五个节点（中心窗口）构造 not-a-knot 三次样条 $S(t)$（4 维向量：3 个推力分量 + 1 个质量流率），求 $y=S(t)$。
- **代码位置**：`plugins/ThrustFilePlugin/src/base/forcemodel/FileThrust.cpp:2249-2313`（`SplineInterpolate`）
- **深度讲解**：
  - 实现细节：
    ```cpp
    2252:    if (profile.size() < 5) {          // 点数不足 5 → 退化为线性（带警告）
    2263:       LinearInterpolate(atIndex, profileIndex, offset); return;
    2268:    spliner = new NotAKnotInterpolator("SplineInterpolator", 4); // 4 维输出
    2269:    spliner->SetExtrapolation(true);   // 允许外推（RK89 采样可能越界）
    2280:    if (interpIndex < 1) interpIndex = 1;          // 窗口钳制
    2282:    else if (interpIndex > profileSize-4) interpIndex = profileSize-4;
    2285:    interpolatorData[0..4] = interpIndex-1 .. interpIndex+3;  // 5 点窗口
    2292:    spliner->Clear();
    2293:    for (i < 5) spliner->AddPoint(profile[interpData[i]].time,
    2300:          {vector[0], vector[1], vector[2], mdot});   // 装载 4 维数据
    2303:    spliner->Interpolate(offset, data);              // 求值
    ```
    逐行注释：`NotAKnotInterpolator` 是 GMAT 标准插值器（见 [MD-05](../math-deep-dive/MD-05-interpolation.md) 若存在，及 [CH07](../CH07-propagator.md) 停止条件插值）；**每次调用都重建**（`Clear`+`AddPoint`，注释 `:2291`"done at each call"）——THF 数据点较少，重建开销可接受；外推开启是为了兼容 RK 级数采样点略越过段界的情形。

### 7.4 比例因子：ThrustScaleFactor / MassFlowScaleFactor / TSF_Epsilon
- **公式**（`FileThrust.cpp:1802`、`ThrustSegment.cpp:1735-1740`）：
$$\mathbf{a}(t)=\text{TSF}\,(1+\varepsilon_{\text{TSF}})\,\hat{\mathbf{a}}_{\text{tab}}(t),\qquad \dot m(t)=\begin{cases}\text{MFSF}\cdot\text{TSF}\,\dot m_{\text{tab}}(t),&\text{ApplyThrustScaleToMassFlow}\\ \text{MFSF}\,\dot m_{\text{tab}}(t),&\text{否则}\end{cases}$$
- **代码位置**：`plugins/ThrustFilePlugin/src/base/forcemodel/FileThrust.cpp:1798-1802`、`:1873-1876`；`plugins/ThrustFilePlugin/src/base/datareader/ThrustSegment.cpp:1735-1740`
- **深度讲解**：
  - `GetScaleFactors`（`ThrustSegment.cpp:1737-1739`）：`sf[0]=thrustScaleFactor`；`sf[1]=useMassAndThrustFactor ? massFlowFactor*thrustScaleFactor : massFlowFactor`——`ApplyThrustScaleToMassFlow`（`ThrustSegment.cpp:47`）为 true 时质量流率也乘 TSF（保证 $\dot m=T/(I_{sp}g)$ 同比例缩放）。
  - `TSF_Epsilon`（段参数，`ThrustSegment.cpp:56`）供**估计器**求解推力比例因子：`scaleFactors[0] *= (1+TSF_Epsilon)`（`FileThrust.cpp:1802`）；STM 中对应的偏导列写入 `aTilde[ix+tsfEpsilonRow] = deriv[3+jj]·thrustSFinitial/thrustSF`（`FileThrust.cpp:1459-1463`）。
  - 组装（`FileThrust.cpp:1873-1876`）：
    ```cpp
    1873:    burnData[0] = dataBlock[0] * scaleFactors[0];   // 推力/加速度 × TSF
    1874:    burnData[1] = dataBlock[1] * scaleFactors[0];
    1875:    burnData[2] = dataBlock[2] * scaleFactors[0];
    1876:    burnData[3] = dataBlock[3] * scaleFactors[1];   // 质量流 × MFSF
    ```
    随后若段指定坐标系则 `ConvertDirectionToInertial(burnData, burnData, atEpoch)`（`:1906-1907`，`ToBaseSystem` 实现见 `:2529-2548`）。
  - 参数表（`ThrustSegment.cpp:43-78`）：`ThrustScaleFactor`（默认 1.0，`:93`）、`MassFlowScaleFactor`（默认 1.0，`:98`）、`ApplyThrustScaleToMassFlow`、`ThrustAngleConstraintVector`（默认 (0,0,1)，`:99`）、`ThrustAngle1/2`（系数向量，默认 0，`:111-112`）、`TSF_Epsilon`、`MassSource`（箱名）、`StartEpoch`/`EndEpoch`、`SolveFors`。

### 7.5 推力角旋转（Rodrigues 公式 + 约束矢量）
- **公式**（`FileThrust.cpp:2487-2494`）：
$$\alpha(t)=\sum_i c_i\,(\Delta t_{\text{sec}})^i\ (\text{度})\xrightarrow{\times\pi/180}\ \text{弧度};\qquad \hat{\mathbf{r}}_1=\frac{\hat{\mathbf{d}}\times\hat{\mathbf{c}}}{\|\hat{\mathbf{d}}\times\hat{\mathbf{c}}\|},\quad \hat{\mathbf{r}}_2=\frac{\hat{\mathbf{r}}_1\times\hat{\mathbf{d}}}{\|\hat{\mathbf{r}}_1\times\hat{\mathbf{d}}\|}$$
$$\mathbf{C}(\theta,\hat{\mathbf{r}})=\cos\theta\,\mathbf{I}_3+(1-\cos\theta)\,\hat{\mathbf{r}}\hat{\mathbf{r}}^{\mathsf T}+\sin\theta\,[\hat{\mathbf{r}}]_\times,\qquad \mathbf{d}'=\mathbf{C}_1\mathbf{C}_2\,\mathbf{d}$$
- **代码位置**：`plugins/ThrustFilePlugin/src/base/forcemodel/FileThrust.cpp:2326-2389`（`ApplyAngleRotations`）、`:2487-2494`（`CalcAngleRotationMatrix`）；导数版 `:2402-2473`、`:2508-2515`
- **深度讲解**：
  - 工程背景：推力表给出名义推力方向，任务希望按"随时间多项式变化的角度"绕特定轴旋转（如斜向点火/姿态机动重构），角度系数 `ThrustAngle1/2` 是**以秒为自变量**的多项式系数（`FileThrust.cpp:2338-2341`：$\alpha=\sum c_i\,\Delta t^i$，$\Delta t$ 为距段首秒数）。
  - 实现细节（旋转轴构造与罗德里格斯旋转）：
    ```cpp
    2338:    for (ii < angleVec1.GetSize()) angle1 += angleVec1[ii]*Pow(offsetSec, ii);
    2343:    angle1 *= GmatMathConstants::RAD_PER_DEG;   // 度 → 弧度
    2352:    Real thrustMag = thrustVec.GetMagnitude();  // 零推力直接返回
    2362:    thrustUnit[ii] = thrustVec[ii] / thrustMag; // 手动归一
    2365:    Rvector3 rotVec1 = Cross(thrustUnit, constraintVec); // 轴1 = d̂×ĉ
    2369:    rotVec1.Normalize();
    2371:    Rvector3 rotVec2 = Cross(rotVec1, thrustUnit);        // 轴2 = r̂1×d̂
    2375:    rotVec2.Normalize();
    2379:    CalcAngleRotationMatrix(angle1, rotVec1, rotMat1);
    2380:    CalcAngleRotationMatrix(angle2, rotVec2, rotMat2);
    2382:    Rmatrix33 rot = rotMat1 * rotMat2;          // 先转 angle1 再转 angle2
    2383:    Rvector3 thrustVecOut = rot * thrustVec;    // 旋转后的推力矢量
    2489:    rotMat = cos(angle)*eye + (1-cos(angle))*Outerproduct(rotVec, rotVec)
    2493:           + sin(angle)*SkewSymmetric(rotVec);  // 罗德里格斯公式
    ```
    逐行注释：轴1 垂直"推力×约束矢量"（绕它转 angle1 会把推力拉向约束矢量）；轴2 垂直"轴1×推力"，实现第二自由度的锥形偏转；`d̂×ĉ` 平行（模 <1e-14）时抛异常（`:2366-2368`）避免零轴；`CalcAngleDotRotationMatrix`（`:2508-2515`）是 $\partial\mathbf{C}/\partial\theta$（$\cos\theta$ 项换 $\sin\theta$、$\sin\theta$ 项换 $\cos\theta$），供 STM 中角度 solve-for 偏导（`ApplyAngleDotRotations`，`:2402-2473`）。
  - 联动：旋转后的 `dataBlock[0..2]` 再乘 TSF（7.4 节）并惯性化；`nominalBurnBody` 保存旋转前名义推力供偏导计算（`:1866-1868`、`:1305-1306`）。

### 7.6 导数组装与单位换算
- **公式**：$$\dot{\mathbf{v}}=\begin{cases}0.001\,\mathbf{a}_{\text{tab}}(t),&\text{ModelAccel}\\ \dfrac{0.001}{m}\,\mathbf{F}_{\text{tab}}(t),&\text{ModelThrust}\end{cases},\qquad \dot m=-\dot m_{\text{tab}}(t)$$
- **代码位置**：`plugins/ThrustFilePlugin/src/base/forcemodel/FileThrust.cpp:1285-1319`，写入 `:1331-1348`
- **深度讲解**：
  - 实现细节：
    ```cpp
    1287:    Real factor = 0.001;                       // m/s² → km/s²
    1288:    if (dataIsThrust) {
    1291:       Real mass = sat->GetRealParameter("TotalMass");
    1292:       factor /= mass;                         // 推力 → 加速度：再除质量
    1295:    accel[0] += burnData[0] * factor;          // 累加（含 TSF 缩放后）
    1296:    accel[1] += burnData[1] * factor;
    1297:    accel[2] += burnData[2] * factor;
    1319:    mDot -= burnData[3];                       // 质量流取负（流出）
    1331:    if (order == 1) {
    1337:       deriv[3+i6] = accel[0]; deriv[4+i6] = accel[1]; deriv[5+i6] = accel[2];
    1341:       if (mloc >= 0)
    1347:          deriv[mloc+i] = mDot;                // MASS_FLOW 元素
    ```
    逐行注释：`dataIsThrust` 由 THF 段头 `ModelThrustOnly/ModelThrustAndMassRate/ModelAccelOnly/ModelAccelAndMassRate` 决定（`ThrustHistoryFile.cpp:95-98`、`:1415-1419`）——推力数据须除当前总质量（与 3.1 节 tOverM 一致），加速度数据直接用；`segIndicies[i]` 记录命中段用于 STM 偏导装配（`:1277`、`:1466-1532`）。`SupportsDerivative`/`SetStart` 另支持 `ORBIT_STATE_TRANSITION_MATRIX` 与 `ORBIT_A_MATRIX`（`:1620-1642`、`:1689-1703`）。

### 7.7 GetForceMaxStep：段/节点边界步长截断
- **公式**：$$\Delta t_{\max}=\min\left(\Delta t_{\text{default}},\ \min_{\text{seg}}\{\text{到段边界与剖面节点的正距离}\}\right)$$
- **代码位置**：`plugins/ThrustFilePlugin/src/base/forcemodel/FileThrust.cpp:2832-2883`（Real 版）、`:2899-2952`（GmatTime 版）
- **深度讲解**：
  - 实现细节：
    ```cpp
    2835:    Real dt = PhysicalModel::GetForceMaxStep(theEpoch, forward); // 默认无穷大
    2841:    dtStart = (seg.startEpoch - theEpoch) * SECS_PER_DAY; // 距段首（秒）
    2842:    dtEnd   = (seg.endEpoch   - theEpoch) * SECS_PER_DAY; // 距段尾
    2846:    if (dtStart > 0) dt = Min(dt, dtStart);   // 正向：不得跨过段边界
    2860:    if (dtStart <= 0 && dtEnd >= 0) {          // 已在段内
    2863:       for (jj < profile.size()-1) {
    2866:          dtProfile = (profile[jj].time - offset) * SECS_PER_DAY; // 距节点
    2870:          if (dtProfile > 0) dt = Min(dt, dtProfile);
    ```
    逐行注释：保证 RK 步不越过段边界/剖面节点（插值区间切换点），配合 8 节 `RungeKutta::Step` 的 `forceMaxStep` 截断与 `followUpStep` 接力，使点火/关火与插值不连续点落在**步边界**上；反向传播取 `Max`（`:2853-2856`、`:2874-2877`）。
  - 联动：`ODEModel::GetForceMaxStep`（`ODEModel.cpp:6504-6521`）对 forceList 取 min，把该上限传给积分器。

---

## 八、与传播器/力模型的联动：SetBurning 与步长缩短

### 8.1 RungeKutta::Step 的 forceMaxStep / stepLimited / followUpStep
- **公式**（逻辑而非代数）：$$\tilde h=\min(h,\ \text{ODEModel::GetForceMaxStep}),\qquad h_{\text{余}}=h-\tilde h\ \text{由递归 }Step()\ \text{续推}$$
- **代码位置**：`src/base/propagator/RungeKutta.cpp:304-497`（`Step`），截断 `:334-365`，接力 `:444-494`
- **深度讲解**：
  - 实现细节：
    ```cpp
    334:    Real forceMaxStep = physicalModel->GetForceMaxStep(stepSize > 0.0);
    335:    while (fabs(stepSize) > fabs(forceMaxStep)) {
    338:       if (!finalStep && hasFiniteBurn == false) {     // 检测 FileThrust
    343:          if (checker->GetForce(indexer)->GetTypeName() == "FileThrust" ...)
    345:             hasFiniteBurn = true;
    362:       stepLimited = true;
    363:       stepSize = forceMaxStep;                          // 步长截到力模型上限
    444:    if (stepLimited) {
    449:       if (!finalStep && hasFiniteBurn) {
    451:          if (followUpStep) burning = true;             // SetBurning 语义
    453:          forceMaxStep = physicalModel->GetForceMaxStep(...);
    456:          if (|forceMaxStep| == REAL_MAX || endOfSegment) burning = false;
    458:          stepSize = originalStep;
    459:          followUpStep = true;
    461:          return false;                                  // 先推进到边界，再续推
    469:       followUpStep = true;
    470:       stepSize = originalStep - stepSize;               // 余下步长递归续推
    ```
    逐行注释：`hasFiniteBurn` 只在发现 `FileThrust` 型力时置位（`:338-348`），随后 `burning`/`followUpStep` 驱动"先走到机动边界、再接力走完剩余"的两段式推进；`SetBurning`（`Propagator::SetBurning/IsBurning`，见 [CH07](../CH07-propagator.md) 2.1）就是这里 `burning` 标志的对外接口。第 390-402 行还有针对"步长贴近 forceMaxStep"的燃料质量误差处理（把步长再缩 0.1 精度）。
  - 数值特性：机动边界（`BeginFileThrust` 段起止、THF 剖面节点）被精确落在步边界上，避免步内推力跳变污染 RK 误差估计。

### 8.2 ODEModel::GetForceMaxStep 与瞬态力装配
- **公式**：$$\Delta t_{\max}^{\text{ODE}}=\min_{f\in\text{forceList}}\Delta t_{\max}^{(f)}$$
- **代码位置**：`src/base/forcemodel/ODEModel.cpp:6504-6521`（`GetForceMaxStep`）、`:2551-2604`（`UpdateTransientForces`）
- **深度讲解**：
  - `GetForceMaxStep`：遍历 `forceList` 取最小值（正向）/最大值（反向，`:6514-6517`），把 `FileThrust` 的段边界限制聚合给积分器。
  - `UpdateTransientForces`：把传播对象列表（`psm->GetStateMap()` 中的航天器，`:2564-2589`）下发给所有瞬态力（`IsTransient()` 命中，`:2595-2602`），`FiniteThrust`/`FileThrust` 由此拿到 `spacecraft` 列表（`SetPropList`，`FiniteThrust.cpp:527-537`、`FileThrust.cpp:1070-1079`）。
  - 装配时序：`BeginFiniteBurn::Execute` push 进 `transientForces`（`BeginFiniteBurn.cpp:673`）→ `Propagate` 调用 `AddTransientForce`（`Propagate.cpp:3548` 等，见 [CH07](../CH07-propagator.md)）→ 下次 `ODEModel::UpdateTransientForces` 生效；`EndFiniteBurn` 对称移除（`EndFiniteBurn.cpp:562`）。

---

## 九、公式索引表

| 公式 | 文件:行 | 所属类 |
|---|---|---|
| $\|\Delta\mathbf{v}\|=\sqrt{\Delta v_1^2+\Delta v_2^2+\Delta v_3^2}$ | src/base/burn/ImpulsiveBurn.cpp:1179 | ImpulsiveBurn |
| $\mathbf{v}^+=\mathbf{v}^-+\Delta\mathbf{v}_I$（正向施加） | src/base/burn/ImpulsiveBurn.cpp:358-360 | ImpulsiveBurn |
| $\Delta\mathbf{v}_I=\mathbf{R}(t)\,\Delta\mathbf{v}_L$；体轴 $\Delta\mathbf{v}_I=\Delta\mathbf{v}_B\mathbf{R}_{BI}^{\mathsf T}$ | src/base/burn/Burn.cpp:1226, 1249-1262, 1269 | Burn |
| VNB 基矢 $\hat V=\mathbf{v}/v,\ \hat N=(\mathbf{r}\times\mathbf{v})/…,\ \hat B=\hat V\times\hat N$ | src/base/burn/VnbManeuverFrame.cpp:110-149 | VnbManeuverFrame |
| 反向机动定点迭代 $\mathbf{b}^{(k+1)}=[\mathbf{b}^{(k)}+\mathbf{v}_{s}-\mathbf{v}_{e}^{(k)}]\,|\Delta\mathbf{v}|/\|…\|$，$\varepsilon<10^{-15}$ | src/base/burn/ImpulsiveBurn.cpp:292-337 | ImpulsiveBurn |
| $\Delta m=M_0(e^{\mp\|\Delta\mathbf{v}\|1000/(I_{sp}g)}-1)$，$M_1=M_0+\Delta m$ | src/base/burn/ImpulsiveBurn.cpp:1181-1190 | ImpulsiveBurn |
| $\mathbf{a}=\sum T_i\text{TSF}_i\text{DC}_i\,\hat{\mathbf{d}}_i/(m\|\hat{\mathbf{d}}_i\|1000)$ | src/base/burn/FiniteBurn.cpp:350-356 | FiniteBurn |
| $\mathbf{F}_{\text{tot}}=\sum (\hat{\mathbf{d}}_i/\|\hat{\mathbf{d}}_i\|)T_i^{\text{applied}}$ | src/base/burn/FiniteBurn.cpp:364-366 | FiniteBurn |
| $\text{burnData}[0..2]=\mathbf{B}\,\mathbf{a},\ \text{burnData}[3]=\sum\dot m_i$ | src/base/burn/FiniteBurn.cpp:401-413 | FiniteBurn |
| $P_{\text{per}}=P_{\text{avail}}/n_{\text{fire}}$，台数递减直至够分 | src/base/burn/FiniteBurn.cpp:1330-1375 | FiniteBurn |
| $\dot{\mathbf{r}}=0,\ \dot{\mathbf{v}}=\sum\mathbf{a}_b,\ \dot m=\sum\dot m_b$ | src/base/forcemodel/FiniteThrust.cpp:714-788 | FiniteThrust |
| $t_{\text{now}}=\text{epoch}+(\text{elapsedTime}+dt)/86400$ | src/base/forcemodel/FiniteThrust.cpp:722 | FiniteThrust |
| 状态元素 CARTESIAN_STATE / MASS_FLOW 索引 | src/base/forcemodel/FiniteThrust.cpp:973-1002 | FiniteThrust |
| $\hat{\mathbf{d}}_I=\hat{\mathbf{d}}_B\mathbf{R}_{BI}^{\mathsf T}$（体轴推力方向） | src/base/hardware/Thruster.cpp:2050-2054 | Thruster |
| $F(P,T)$、$I_{sp}(P,T)$ 16 系数多项式 | src/base/hardware/ChemicalThruster.cpp:843-878 | ChemicalThruster |
| $\dot m=-T\,\text{DC}/(g\,I_{sp})$ | src/base/hardware/ChemicalThruster.cpp:937, 955 | ChemicalThruster |
| $T(P)=(\sum a_iP^i)/10^3$、$\dot m(P)=(\sum b_iP^i)/10^6$、$I_{sp}=T/(\dot m g)$ | src/base/hardware/ElectricThruster.cpp:828-840 | ElectricThruster |
| $T=T_c$、$\dot m=T_c/(I_{sp}g)$（ConstantThrustAndIsp） | src/base/hardware/ElectricThruster.cpp:844, 939 | ElectricThruster |
| $T=2\eta P/(I_{sp}g\cdot0.001)$、$\dot m=2\eta P\cdot0.001/(I_{sp}g\cdot0.001)^2$ | src/base/hardware/ElectricThruster.cpp:848-849, 943-945 | ElectricThruster |
| 功率钳制 $P=\min(P,P_{\max})$、$P<P_{\min}\Rightarrow T=0$ | src/base/hardware/ElectricThruster.cpp:902-913 | ElectricThruster |
| $\mathbf{r}_{cm}^{\text{BCS}}=\mathbf{r}_b+\mathbf{R}_{SB}^{\mathsf T}\mathbf{r}_T$ | src/base/hardware/FuelTank.cpp:761-763 | FuelTank |
| $\mathbf{I}^{\text{BCS}}=\mathbf{R}_{SB}^{\mathsf T}\mathbf{I}_t\mathbf{R}_{SB}+m(|\mathbf{r}|^2\mathbf{I}_3-\mathbf{r}\mathbf{r}^{\mathsf T})$ | src/base/hardware/FuelTank.cpp:800-801 | FuelTank |
| 吹除 $V_G=V_T-M_F/\rho$、$P_f=P_iV_{G,i}/V_{G,f}$ | src/base/hardware/ChemicalTank.cpp:787-788, 839-845 | ChemicalTank |
| 质量分摊 $\Delta m_i=\Delta M\,\dot m_i/\sum\dot m_j$、$\Delta m_{\text{tank}}=\Delta m_i\,\text{mr}_k/\sum\text{mr}_l$ | src/base/spacecraft/Spacecraft.cpp:9813, 9821-9832 | Spacecraft |
| 段区间 $t_s<e<t_e$（含方向端点） | plugins/ThrustFilePlugin/src/base/forcemodel/FileThrust.cpp:3134-3146 | FileThrust |
| 线性插值 $y=y_0+u(y_1-y_0)$ | plugins/ThrustFilePlugin/src/base/forcemodel/FileThrust.cpp:2210-2220 | FileThrust |
| 5 点 NotAKnot 样条（可外推） | plugins/ThrustFilePlugin/src/base/forcemodel/FileThrust.cpp:2252-2313 | FileThrust |
| $\mathbf{a}=\text{TSF}(1+\varepsilon)\mathbf{a}_{\text{tab}}$、$\dot m=\text{MFSF}(·\text{TSF})\dot m_{\text{tab}}$ | plugins/ThrustFilePlugin/src/base/forcemodel/FileThrust.cpp:1802, 1873-1876；ThrustSegment.cpp:1735-1740 | FileThrust / ThrustSegment |
| 推力角 $\alpha=\sum c_i\Delta t^i$（秒），度→弧度 | plugins/ThrustFilePlugin/src/base/forcemodel/FileThrust.cpp:2338-2344 | FileThrust |
| $\mathbf{C}=\cos\theta\mathbf{I}+(1-\cos\theta)\hat{\mathbf{r}}\hat{\mathbf{r}}^{\mathsf T}+\sin\theta[\hat{\mathbf{r}}]_\times$ | plugins/ThrustFilePlugin/src/base/forcemodel/FileThrust.cpp:2487-2494 | FileThrust |
| $\dot{\mathbf{v}}=0.001\,\mathbf{a}$ 或 $0.001\,\mathbf{F}/m$ | plugins/ThrustFilePlugin/src/base/forcemodel/FileThrust.cpp:1287-1297 | FileThrust |
| 步长上限 = min(到段边界/节点距离) | plugins/ThrustFilePlugin/src/base/forcemodel/FileThrust.cpp:2841-2877 | FileThrust |
| $\tilde h=\min(h,\Delta t_{\max}^{\text{ODE}})$ + followUpStep 接力 | src/base/propagator/RungeKutta.cpp:334-363, 444-494 | RungeKutta |
| $\Delta t_{\max}^{\text{ODE}}=\min_f\Delta t_{\max}^{(f)}$ | src/base/forcemodel/ODEModel.cpp:6504-6521 | ODEModel |
