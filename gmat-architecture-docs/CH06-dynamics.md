# 第6章 力模型、太阳系、航天器与硬件模型

> 本章范围：`src/base/forcemodel/`（力模型与 ODE 聚合，30 个文件）、`src/base/solarsys/`（太阳系、天体与星历，55 个文件）、`src/base/spacecraft/`（航天器与空间对象，11 个文件）、`src/base/hardware/`（硬件全家族，34 个文件），共 **130 个文件**。任务描述中提到的 `FiniteBurn` 位于 `src/base/burn/`（第7章），`TransientForce` 在本仓库即为 `FiniteThrust`（瞬态力模型）；通信类硬件 `Antenna/Transmitter/Receiver/Transponder/Sensor` 不在 `src/base/hardware/`，而在 `plugins/EstimationPlugin/src/base/hardware/`（第13章），本章以链接引用说明关系。

---

## 一、本章目录树

```
src/base/
├── forcemodel/                        (30 文件)
│   ├── PhysicalModel.{hpp,cpp}        力模型基类
│   ├── ODEModel.{hpp,cpp}             力聚合容器（ODE 右手边）
│   ├── ODEModelException.{hpp,cpp}    力模型异常
│   ├── GravityBase.{hpp,cpp}          高级引力模型中间基类
│   ├── HarmonicField.{hpp,cpp}        球谐场基类（度/阶、位文件）
│   ├── GravityField.{hpp,cpp}         中心天体球谐引力（JGM2/JGM3/EGM96）
│   ├── PointMassForce.{hpp,cpp}       质点引力（含第三体间接项）
│   ├── DragForce.{hpp,cpp}            大气阻力
│   ├── SolarRadiationPressure.{hpp,cpp} 太阳光压（锥形/圆柱地影）
│   ├── FiniteThrust.{hpp,cpp}         有限推力（瞬态力，质量消耗）
│   ├── RelativisticCorrection.{hpp,cpp} 相对论摄动
│   ├── EventModel.{hpp,cpp}           事件函数导数容器
│   ├── NumericJacobianOriginal.{hpp,cpp} 数值雅可比（MATLAB numjac 移植）
│   └── harmonic/
│       ├── Harmonic.{hpp,cpp}         球谐递推 + 归一化勒让德
│       └── HarmonicGravity.{hpp,cpp}  球谐引力 + 固体潮
├── solarsys/                          (55 文件)
│   ├── SolarSystem.{hpp,cpp}          太阳系单例容器
│   ├── CelestialBody.{hpp,cpp}        天体基类（星历/坐标系/自转）
│   ├── Planet.{hpp,cpp} Star.{hpp,cpp} Moon.{hpp,cpp}
│   ├── Asteroid.{hpp,cpp} Comet.{hpp,cpp} SpecialCelestialPoint.{hpp,cpp}
│   ├── CalculatedPoint.{hpp,cpp} Barycenter.{hpp,cpp} LibrationPoint.{hpp,cpp}
│   ├── PlanetaryEphem.{hpp,cpp}       星历读取接口
│   ├── DeFile.{hpp,cpp}               JPL DE 二进制/ASCII 内核
│   ├── SlpFile.{hpp,cpp}              GTDS SLP 曲线拟合星历
│   ├── EphemSmoother.{hpp,cpp}        星历三次样条平滑（CSALT 用）
│   ├── SolarFluxReader.{hpp,cpp}       F10.7/Ap 太阳通量读取
│   ├── AtmosphereModel.{hpp,cpp}      大气模型基类
│   ├── ExponentialAtmosphere.{hpp,cpp} SimpleExponentialAtmosphere.{hpp,cpp}
│   ├── JacchiaRobertsAtmosphere.{hpp,cpp} Msise90Atmosphere.{hpp,cpp}
│   ├── msise90_sub.c / msise90_sub.for MSISE-90 底层 Fortran/C 实现
│   ├── ShadowState.{hpp,cpp}          地影锥/圆柱判据
│   ├── PlanetographicRegion.{hpp,cpp} 行星表面区域
│   ├── MediaCorrectionInterface.{hpp,cpp} 介质改正（对流层/电离层）
│   └── AtmosphereException.hpp PlanetaryEphemException.{hpp,cpp} SolarSystemException.{hpp,cpp}
├── spacecraft/                        (11 文件)
│   ├── SpaceObject.{hpp,cpp}          空间对象基类
│   ├── Spacecraft.{hpp,cpp}           航天器（状态/硬件聚合）
│   ├── SpaceObjectException.hpp       异常
│   ├── FormationInterface.{hpp,cpp}   编队代理接口（Formation 插件实现）
│   ├── Plate.{hpp,cpp}                N-板 SRP 反射面板
│   └── TextTrajectoryFile.{hpp,cpp}   文本轨迹读取
└── hardware/                          (34 文件)
    ├── Hardware.{hpp,cpp}             硬件基类（位姿/方向）
    ├── FuelTank.{hpp,cpp} ChemicalTank.{hpp,cpp} ElectricTank.{hpp,cpp}
    ├── Thruster.{hpp,cpp} ChemicalThruster.{hpp,cpp} ElectricThruster.{hpp,cpp}
    ├── PowerSystem.{hpp,cpp} SolarPowerSystem.{hpp,cpp} NuclearPowerSystem.{hpp,cpp}
    ├── FieldOfView.{hpp,cpp} ConicalFOV.{hpp,cpp} RectangularFOV.{hpp,cpp} CustomFOV.{hpp,cpp}
    ├── Imager.{hpp,cpp}               带 FOV 的成像硬件中间类
    └── HardwareException.{hpp,cpp} FieldOfViewException.{hpp,cpp}
```

---

## 二、逐文件/逐类讲解

### 2.1 forcemodel —— 力模型与 ODE 右手边

GMAT 的力模型体系遵循一条清晰的继承链：`GmatBase → PhysicalModel → 各具体力模型`。`PhysicalModel` 定义"一个力给出加速度贡献"的统一契约，`ODEModel` 则把多个 `PhysicalModel` 聚合成积分器需要的完整导数向量。所有力模型在"力模型原点"（通常是中心天体）的 MJ2000Eq 坐标系下计算加速度，由 `ODEModel` 统一求和。

#### 2.1.1 PhysicalModel —— 力模型基类

- 文件：`src/base/forcemodel/PhysicalModel.hpp` / `.cpp`
- 职责：所有力模型的抽象基类，统一"给状态求导数"的接口与内部状态管理。
- 关键成员（`PhysicalModel.hpp`）：
  - `class GMAT_API PhysicalModel : public GmatBase`（第143行）。
  - `body` / `forceOrigin`（第350、352行）：被作用天体指针与力模型原点（积分参考系原点）。
  - `theState`（`GmatState*`，第365行）：由 `PropagationStateManager` 注入的当前传播状态。
  - `modelState` / `modelStateDot`（第367、369行）：模型自己的工作状态与导数副本。
  - `rawState` / `rawStateDot`（第372、374行）：J2000BodyMJ2000Eq 坐标下的状态/导数，供跨力模型坐标统一。
  - `deriv` / `rawDeriv`（第388、390行）：最近一次导数结果缓冲。
  - 核心虚接口：`GetDerivatives(Real* state, Real dt, Integer order, Integer id)`（第188行）与 `GetDerivativesForSpacecraft(Spacecraft* sc)`（第190行）。
  - 能力标志：`IsTransient()`（第219行，是否瞬态力）、`DepletesMass()`（第220行，是否耗质量）、`AttitudeAffectsDynamics()`（第221行）、`SupportsDerivative()`/`SetStart()`（第231-233行，由 ODEModel 设定导数在输出向量中的起始索引）。

设计要点：`PhysicalModel` 自己不做加法，只负责"算出自己那份加速度"，并通过 `SetStart(Gmat::StateElementId, index, quantity, totalSize)` 得知自己应把结果写到 `deriv` 的哪一段。这是"策略模式 + 位置映射"：每个力是独立策略，容器负责拼接。

#### 2.1.2 ODEModel —— 力聚合容器与核心求和循环

- 文件：`src/base/forcemodel/ODEModel.hpp` / `.cpp`
- 职责：把若干 `PhysicalModel` 叠加成积分器（第7章传播器）所需的完整 ODE 右手边函数 `ẋ = f(x,t)`。
- 关键成员（`ODEModel.hpp`）：
  - `class GMAT_API ODEModel : public PhysicalModel`（第93行）——容器本身也是一个 `PhysicalModel`，可被嵌套。
  - `std::vector<PhysicalModel*> forceList`（第333行）：真正的力列表。
  - `Integer numForces`（第317行）：力数量。
  - `GmatState* state`（第323行）：由状态管理器设置。
  - `Integer satCount`（第363行）：以 6 维笛卡尔状态传播的对象数。
  - `Integer satIds[11]`（第366行）：用于在积分中读取航天器参数的参数 ID 缓存（Cd、Cr、质量等）。
  - `muMap`（第483行）：`map<string,Real>` 记录各 SpacePoint 的 μ 值。

**核心求和循环**位于 `ODEModel::GetDerivatives`，`src/base/forcemodel/ODEModel.cpp` 第3261-3363行：

```cpp
3261:    // Apply superposition of forces/derivatives
3262:    for (std::vector<PhysicalModel *>::iterator i = forceList.begin();
3263:          i != forceList.end(); ++i)
3264:    {
...
3283:       if (!(*i)->GetDerivatives(state, dt, order))
3284:       {
...
3289:          throw ODEModelException("Derivative " + (*i)->GetTypeName() + " failed\n");
...
3293:       ddt = (*i)->GetDerivativeArray();
...
3306:       for (Integer j = 0; j < dimension; ++j)
3307:       {
3309:          if (GmatMathUtil::IsNaN(ddt[j]))
3310:             MessageInterface::ShowMessage("NAN found in derivative for %s "
3311:                      "force element %d, Value is %lf\n", ...);
3314:          deriv[j] += ddt[j];
...
3318:       }
...
3336:       if (fillTimeJacobian) { ... timeJacobian[j] += forceTimeJac[j]; ... }
3354:       if (fillMassJacobian && !finiteDifferencingTimeJac) { ... massJacobian[j] += forceMassJac[j]; ... }
3363:    }
```

逐行解释：
- 第3262-3263行遍历 `forceList` 中的每个力模型（Gravity/Drag/SRP/Thrust……），这就是加速度的**线性叠加**。
- 第3283行调用每个力自己的 `GetDerivatives(state, dt, order)`，让该力把贡献写进自己的 `deriv` 缓冲；任一力失败即抛 `ODEModelException`。
- 第3293行 `ddt = (*i)->GetDerivativeArray()` 取回该力算好的导数数组。
- 第3306-3314行是**核心求和**：对状态向量每个分量 `j`，执行 `deriv[j] += ddt[j]`，把各力的分量贡献逐元素累加进总导数。第3309行顺带做 NaN 保护告警。
- 第3336-3362行在需要时同步累加时间雅可比（`timeJacobian`）与质量雅可比（`massJacobian`），供估计/协方差传播使用。

叠加完成后，容器补上"位置导数 = 速度"的运动学项（`src/base/forcemodel/ODEModel.cpp` 第3380-3391行）：

```cpp
3380:    if (fillCartesian)
3381:    {
3382:       if (order == 1)  // Fill in 1st dv of position with the input velocity
3383:       {
3384:          for (Integer i = 0; i < cartStateSize; i += 6)
3385:          {
3386:             deriv[cartesianStart + i]     = state[cartesianStart + i + 3];
3387:             deriv[cartesianStart + i + 1] = state[cartesianStart + i + 4];
3388:             deriv[cartesianStart + i + 2] = state[cartesianStart + i + 5];
3389:          }
3390:       }
3391:    }
```

即对于一阶导数：`d(pos)/dt = vel`（第3386-3388行直接把输入状态的 4、5、6 分量写入导数 0、1、2 分量）。力模型只填 `d(vel)/dt`（加速度），速度项由容器统一补齐——这也是为什么各力模型实现里常见 `deriv[i6]=deriv[i6+1]=deriv[i6+2]=0.0` 的写法（位置导数清零，把运动学项让给容器）。

> 说明：任务描述中的"GetDerivativesForState"实为 `GetDerivatives`（本节所述）；另有 `GetDerivativesForSpacecraft(Spacecraft*)`（`ODEModel.cpp` 第4071行，逐力调用 `GetDerivativesForSpacecraft` 后累加，见第4084-4135行），它返回单个航天器的 `Rvector6` 导数，用于不经过整条 ODE 状态向量的快捷查询。

其余关键方法：
- `AddForce`（`ODEModel.cpp` 第635行）：把力加入 `forceList`，`numForces = forceList.size()`（第857行），并把力设为 owned object。
- `AddExclusiveForce`（第135行声明）：互斥力（如"点质量 vs 球谐场"二选一）。
- `GetDerivatives` 开头做防御：`psm == NULL` 抛异常（第3147-3149行）；多个航天器 + 瞬态力（有限推力）时抛异常（第3152-3158行）。
- `SetEpoch`（第292行声明）：供 C 接口强制更新力模型时间。

#### 2.1.3 引力模型族：GravityBase / HarmonicField / GravityField / harmonic/

继承链：`PhysicalModel → GravityBase → HarmonicField → GravityField`；球谐计算引擎单独为 `Harmonic → HarmonicGravity`（不继承 GmatBase，是纯数值内核）。

- `src/base/forcemodel/GravityBase.hpp`：
  - `class GMAT_API GravityBase : public PhysicalModel`（第46行）。
  - 职责：为"高级引力模型"（球谐、多面体等）提供统一的标记基类，便于 `ODEModel` 识别"中心天体引力"这一类力（第37-45行注释）。2012年加入，用于与 `PolyhedronGravityPlugin`（第13章）等并列。
  - 目前无新增参数（`GravityBaseParamCount = PhysicalModelParamCount`，第59行）。

- `src/base/forcemodel/HarmonicField.hpp`：
  - `class HarmonicField : public GravityBase`（第94行）。
  - 参数：`MAX_DEGREE`/`MAX_ORDER`/`DEGREE`/`ORDER`/`STMLIMIT`/`FILENAME`/`INPUT_COORD_SYSTEM`/`FIXED_COORD_SYSTEM`/`TARGET_COORD_SYSTEM`（第147-158行枚举）。
  - 职责：管理球谐场的度/阶截断、位势文件读取、以及"固连坐标系（fixed）↔惯性坐标系（input）"转换所需的坐标系与 EOP 文件（`EopFile* eop`，第198行）。`SetDegreeOrder(degree, order, stmlimit)`（第108行）设置截断阶次。

- `src/base/forcemodel/GravityField.hpp`：
  - `class GMAT_API GravityField : public HarmonicField`（第95行）。
  - 关键成员：`mu`（中心天体引力常数，第205行）、`a`（参考赤道半径，第207行）、`HarmonicGravity* gravityModel`（第229行，球谐引擎）、`static std::vector<HarmonicGravity*> cache`（第196行，跨实例共享已装载的系数，避免重复读文件）。
  - 常量：`DEFAULT_DEGREE = 360`、`DEFAULT_ORDER = 360`（第155-156行）。
  - 支持模型枚举：`GFM_EGM96 / GFM_JGM2 / GFM_JGM3 / GFM_LP165P / GFM_MARS50C / GFM_MGNP180U`（第158-174行）。
  - `static HarmonicGravity* GetHarmonicGravity(...)`（第149-152行）：从文件装载/复用球谐模型，含潮汐文件（`TideFilename`）。
  - 核心算法入口：`Calculate(dt, state, force, grad)`（第249-250行）——把状态转到固连系、调用 `HarmonicGravity::CalculateFullField`、再逆旋转回惯性系（`InverseRotate`，第251行）。

- `src/base/forcemodel/harmonic/Harmonic.hpp`：
  - `class GMAT_API Harmonic`（第66行），纯数值内核，非 GmatBase。
  - 纯虚接口：`Cnm(jday,n,m)` 与 `Snm(jday,n,m)`（第76-79行）返回归一化球谐系数；`CalculateField(...)`（第84-86行）计算加速度与梯度。
  - 关键成员：`Factor = -mu`（重力）或 `1`（磁场，第92行注释）；`C/S` 归一化系数矩阵、`A` 归一化派生勒让德多项式、`V` 归一化因子（第93-96行）。
  - 算法出处（第31-44行注释）：Lundberg-Schutz 递推 + Pines 均匀表示（非奇异，避免极区退化）。
  - 核心公式在 `Harmonic::CalculateField`（`harmonic/Harmonic.cpp` 第91行起）：`rho = FieldRadius/r`（第120行）、`rho_np1 = -Factor/r * rho`（第121行，`Factor=mu` 时即 `-μ/r·(R/r)`），随后按 Pines 递推累加，最终加速度 `acc[0]=a1+a4*s; acc[1]=a2+a4*t; acc[2]=a3+a4*u`（第243-245行）。

- `src/base/forcemodel/harmonic/HarmonicGravity.hpp`：
  - `class HarmonicGravity : public Harmonic`（第52行），实现 `Cnm`/`Snm`（第70-71行）。
  - `CalculatePointField`（第72-75行）：不含潮汐的加速度；`CalculateFullField`（第76-82行）：加入固体潮与极潮（`sunpos/sunmukm/otherpos/othermukm`、`xp/yp` 极移）。
  - 潮汐模型枚举 `ETide { NoTide, Solid, SolidAndPole }`（第88行）；固体潮增量 `IncrementSolidTide`（第115行）、地球潮 `IncrementEarthTide`（第116行）。
  - 系数装载：`LM_LoadGfc/LM_LoadCof/LM_LoadGrv/LM_LoadTab`（第135-138行）分别支持 `.gfc/.cof/.grv/.tab` 多种位势文件格式。

JGM 谐项小结（数学上）：中心天体引力势以带谐/田谐展开，`Cnm/Snm` 为归一化系数（J2 即 `-C20`），`GravityField` 用 `mu`、`a` 与 `HarmonicGravity` 引擎把"归一化系数 + 归一化勒让德递推"组合成固连系加速度，再经 `EopFile`+`CoordinateConverter` 转到 MJ2000Eq。默认满阶 360×360（如 EGM96）。

#### 2.1.4 PointMassForce —— 点质量引力（含第三体间接项）

- 文件：`src/base/forcemodel/PointMassForce.hpp` / `.cpp`
- 职责：`a = -μ r / r³` 的二体/点质量加速度，并支持"力模型原点 ≠ 引力体"时的间接项。
- 关键成员（`PointMassForce.hpp`）：`mu`（第155行，注释 `G*M`）、`isPrimaryBody`（第160行）。

核心公式在 `src/base/forcemodel/PointMassForce.cpp`：

间接项（力模型原点不是被积分的引力体时，需扣除原点自身被该体吸引的加速度），第440-453行：

```cpp
440:       // The vector from the force origin to the gravitating body
441:       // Precalculations for the indirect effect term
442:       rbb3 = rv[0]*rv[0]+rv[1]*rv[1]+rv[2]*rv[2];
443:       if (rbb3 != 0.0)
444:       {
446:          rbb3 = sqrt(rbb3 * rbb3 * rbb3);
447:          mu_rbb = mu / rbb3;
448:          a_indirect[0] = mu_rbb * rv[0];
449:          a_indirect[1] = mu_rbb * rv[1];
450:          a_indirect[2] = mu_rbb * rv[2];
451:       }
```

主加速度（第492-521行）：

```cpp
492:             relativePosition[0] = rv[0] - state[ i6 ];
493:             relativePosition[1] = rv[1] - state[i6+1];
494:             relativePosition[2] = rv[2] - state[i6+2];
496:             r3 = relativePosition[0]*relativePosition[0] +
497:                  relativePosition[1]*relativePosition[1] +
498:                  relativePosition[2]*relativePosition[2];
500:             radius = sqrt(r3);
501:             r3 *= radius;
502:             mu_r = mu / r3;
...
519:                deriv[3 + i6] = relativePosition[0] * mu_r - a_indirect[0];
520:                deriv[4 + i6] = relativePosition[1] * mu_r - a_indirect[1];
521:                deriv[5 + i6] = relativePosition[2] * mu_r - a_indirect[2];
```

逐行解释：
- 第492-494行：`relativePosition = 引力体位置 - 航天器位置`（即从航天器指向引力体的矢量 r）。
- 第496-501行：`r3 = |r|²`，再乘 `radius=|r|` 得 `|r|³`（避免调用 `pow`，纯乘法更省）。
- 第502行：`mu_r = μ/|r|³`。
- 第519-521行：`d²x/dt² = mu_r·r − a_indirect`，即点质量引力加速度扣除间接项。当原点就是引力体时 `rbb3=0`、`a_indirect=0`，退化为标准二体形式 `a = -μ r/r³`（符号因 `relativePosition` 方向定义而体现）。
- 第523-532行注释说明：速度项 `dr/dt=v` 已交给 `ODEModel` 统一填充，这里位置导数清零。

`PointMassForce` 是"第三体摄动"的实现载体：在 `ODEModel` 里对每个摄动天体挂一个 `PointMassForce`，`mu` 来自对应 `CelestialBody`。

#### 2.1.5 DragForce —— 指数大气阻力

- 文件：`src/base/forcemodel/DragForce.hpp` / `.cpp`
- 职责：`a_drag = −½ (Cd·A/m) ρ v_rel² v̂_rel`，其中 v_rel 为相对大气的速度（含地球自转风 `ω×R` 项）。
- 关键成员（`DragForce.hpp`）：
  - `atmos` / `internalAtmos`（第175、177行）：大气模型指针（外部指定或内建）。
  - `area/mass/dragCoeff/atmosDensityScaleFactor`（第198-204行）：每航天器的阻力面积、质量、`Cd`、大气密度比例因子。
  - `cbFixed` / `internalCoordSystem`（第304、306行）：固连系与内部坐标系，用于 `ω×R` 与太阳凸起（bulge）计算。
  - 参数枚举：`ATMOSPHERE_MODEL/FLUX/AVERAGE_FLUX/MAGNETIC_INDEX/DRAG_MODEL/...`（第326-345行），F10.7/Ap/Kp 等空间天气输入。

**阻力公式实现**——预因子构建（`DragForce.cpp` 第1182-1217行）：

```cpp
1182:  * The drag prefactor is given by
1184:  *     \f[F_d = -\frac{1}{2} \frac{C_d A}{m} \f]
...
1216:          // Note: Prefactor is scaled to account for density in kg / m^3 (*1000/2)
1217:          prefactor[i] = -500.0 * dragCoeff[i] * area[i] / mass[i];
```

第1217行的 `-500.0 = −(1/2)·1000`：`1000` 把 `kg/m³` 密度换算到 `kg/km³` 以匹配 `km/s²` 加速度单位。

**主循环**（`DragForce.cpp` 第1307-1527行，公式注释见第1290-1292行）：

```cpp
1479:             vRelative[0] = dragState[i6+3] - wind[3];
1480:             vRelative[1] = dragState[i6+4] - wind[4];
1481:             vRelative[2] = dragState[i6+5] - wind[5];
1482:             vRelMag = sqrt(vRelative[0]*vRelative[0] + vRelative[1]*vRelative[1] +
1483:                            vRelative[2]*vRelative[2]);
...
1501:             // v_rel = v - w x R
1502:             vRelative[0] = dragState[i6+3] -
1503:                            (angVel[1]*dragState[i6+2] - angVel[2]*dragState[i6+1]);
1504:             vRelative[1] = dragState[i6+4] -
1505:                            (angVel[2]*dragState[ i6 ] - angVel[0]*dragState[i6+2]);
1506:             vRelative[2] = dragState[i6+5] -
1507:                            (angVel[0]*dragState[i6+1] - angVel[1]*dragState[ i6 ]);
1508:             vRelMag = sqrt(...);
...
1513:          factor = prefactor[i] * density[i];
...
1525:                deriv[3+j6] = factor * vRelMag * vRelative[0];
1526:                deriv[4+j6] = factor * vRelMag * vRelative[1];
1527:                deriv[5+j6] = factor * vRelMag * vRelative[2];
```

逐行解释：
- 第1479-1483行（有风模型时）或第1501-1509行（默认）计算相对速度：`v_rel = v_sat − ω×R`，其中 `ω` 是中心天体自转角速度 `angVel`，`ω×R` 项是大气随地球旋转的牵连速度。
- 第1513行：`factor = prefactor·ρ = −½(Cd·A/m)·ρ`。
- 第1525-1527行：`a = factor·|v_rel|·v_rel`，即 `−½(CdA/m)ρ v_rel²·(v_rel/|v_rel|)` 的分量形式（`factor·|v_rel|` 后乘 `vRelative` 向量，含方向）。
- 密度来源：`GetDensity(dragState, now)`（第1441行）→ `atmos->Density(state, density, when, count)`（第3319行），再乘 `atmosDensityScaleFactor`（第3361行）。

`Cd` 与估计接口耦合：`cdEpsilon` 用于"求解 Cd"时 `dragCoeff[i] = cdInitial[i]*(1+cdEpsilon[i])`（第1343行）；若为 FirstOrderGaussMarkov 模型则追加 `−β·ε` 项（第1362行）。

#### 2.1.6 SolarRadiationPressure —— 锥形地影太阳光压

- 文件：`src/base/forcemodel/SolarRadiationPressure.hpp` / `.cpp`
- 职责：`a_srp = ν·(Cr·A/m)·P_sun·(1AU/r_sun)²·ŝ`，其中 `ν`（`percentSun`）为锥形/圆柱地影的受照百分比，`P_sun = flux/c`。
- 关键成员（`SolarRadiationPressure.hpp`）：
  - `flux` / `fluxPressure`（第227、229行）：太阳通量（W/m²）与光压（N/m²）。构造函数 `fluxPressure = flux / GmatPhysicalConstants::c`（`.cpp` 第160行）——光压 = 通量/光速。
  - `cr` / `area` / `mass`（第216-221行）：反射系数、受光面积、质量。
  - `ShadowState* shadowState`（第191行）：地影计算器；`modelShadows`（第196行）。
  - 形状模型：`srpShapeModel`（`Spherical/SPADFile/NPlate`，第231行）；N 板模型 `ComputeNPlateAcceleration`（第275-276行）。

**核心公式**（`SolarRadiationPressure.cpp` 第992-1084行）：

```cpp
992:          // Build vector from the Sun to the current spacecraft
993:          sunSat[0] = state[ i6 ] - cbSunVector[0];
...
996:          sunDistance = sqrt(sunSat[0]*sunSat[0] + sunSat[1]*sunSat[1] +
997:                            sunSat[2]*sunSat[2]);
...
1001:          forceVector[0] = sunSat[0] / sunDistance;
1002:          forceVector[1] = sunSat[1] / sunDistance;
1003:          forceVector[2] = sunSat[2] / sunDistance;
1005:          distancefactor = nominalSun / sunDistance;        // (1AU/rs)
1006:          distancefactor *= distancefactor;                 // (1AU/rs)^2
...
1013:          // Test shadow condition for current spacecraft (only if body isn't Sol)
1014:          if (modelShadows)
1015:          {
1016:             if (sunRadius < sunDistance)
1031:                percentSun = GetShadowStateFromAllBodies(ep, &state[i6]);
...
1067:             mag = percentSun * fluxPressure * distancefactor /
1068:                                 mass[i];                    // (N/m^2)/kg = 1/(m·s^2)
...
1070:             if (srpShapeModelIndex == ShapeModel::SPHERICAL_MODEL)
1071:             {
1076:                mag *= cr[i] * area[i];                      // * m^2
1077:                mag = mag*GmatMathConstants::M_TO_KM;        // m/s^2 -> km/s^2
...
1082:                   deriv[i6 + 3] = mag * forceVector[0];     // km/s^2
1083:                   deriv[i6 + 4] = mag * forceVector[1];
1084:                   deriv[i6 + 5] = mag * forceVector[2];
```

逐行解释：
- 第992-1003行：`sunSat = 航天器 − 太阳位置`（注意与 PointMassForce 方向相反，光压从太阳"推"向航天器），`forceVector` 为单位方向向量。
- 第1005-1006行：`distancefactor = (1AU/rs)²`，即平方反比衰减因子。
- 第1014-1031行：地影判定——若中心天体不是太阳且 `sunRadius < sunDistance`，调用 `GetShadowStateFromAllBodies` 得到 `percentSun`（全影 0、全照 1、半影取 (0,1)），支持多个掩星体。
- 第1067-1068行：`mag = ν·P_sun·(1AU/rs)² / m`（单位 `(N/m²)/kg`）。
- 第1076-1077行：球形模型下乘 `Cr·A`，并把 `m/s²` 转为 `km/s²`（`M_TO_KM = 0.001`）。
- 第1082-1084行：把加速度沿 `forceVector` 方向写入导数速度分量。

地影模型：`ShadowState::FindShadowState`（`src/base/solarsys/ShadowState.cpp`）实现锥形（conical）与圆柱（cylindrical）判据，`GetPercentSunInPenumbra`（`ShadowState.hpp` 第54行）计算半影受照百分比。`SolarRadiationPressure.hpp` 第174-179行枚举 `CYLINDRICAL_MODEL/CONICAL_MODEL`。

#### 2.1.7 FiniteThrust —— 有限推力（瞬态力）

- 文件：`src/base/forcemodel/FiniteThrust.hpp` / `.cpp`
- 职责：有限推力机动的加速度模型。它是"瞬态力"（`IsTransient()` 返回 true，第76行）且"消耗质量"（`DepletesMass()` 返回 true，第77行），由 `BeginFiniteBurn/EndFiniteBurn` 命令（第5章）在任务序列中动态加入/移除。
- 关键成员：`burns`（`std::vector<FiniteBurn*>`，第98行）、`mDotIndex`（第117行，质量流率在状态向量中的索引）、`depleteMass`（第119行）。

核心累加在 `src/base/forcemodel/FiniteThrust.cpp` 第657-784行：

```cpp
714:             mDot = accel[0] = accel[1] = accel[2] = 0.0;
716:             // Accumulate thrust and mass flow for each active thruster
...
728:                   accel[0] += burnData[0];
729:                   accel[1] += burnData[1];
730:                   accel[2] += burnData[2];
...
741:                      mDot += burnData[3];
...
771:                deriv[3 + i6] = accel[0];
772:                deriv[4 + i6] = accel[1];
773:                deriv[5 + i6] = accel[2];
...
777:                   deriv[mloc+i]   = mDot;
```

逐行解释：第716-730行对每个点火的推力器累加 `burnData`（由 `FiniteBurn::Fire` 计算出的推力加速度分量，见第7章）；第741行累加质量流率 `mDot`；第771-773行把合加速度写入导数；第777行把 `dm/dt` 写入状态向量质量分量（使积分器同步推进质量）。推力方向由 `Thruster::ConvertDirectionToInertial`（`Thruster.hpp` 第256行）从推力器本体系转到惯性系。

#### 2.1.8 RelativisticCorrection —— 相对论摄动

- 文件：`src/base/forcemodel/RelativisticCorrection.hpp` / `.cpp`
- 职责：后牛顿（post-Newtonian）相对论加速度摄动（Einstein–Infeld–Hoffmann 的一阶项）。用于高精度近太阳任务。
- 关键成员：`bodyMu` / `sunMu`（第94、97行）、`bodyInertial` / `bodyFixed`（第107、109行，惯性/固连坐标系）、`EopFile* eop`（第111行）。
- 参数仅 `BODY_RADIUS`（第121行）。`SetEopFile`（第61行）注入章动/极移文件。

#### 2.1.9 其余：EventModel / NumericJacobianOriginal / ODEModelException

- `src/base/forcemodel/EventModel.hpp`：`class EventModel : public PhysicalModel`（第50行）。把 `EventLocator` 列表（第86行）接入积分器，为每个事件函数生成导数数据（第40-49行注释），供停止条件/事件定位（第7章）使用。`SetEventLocators`（第59行）、`GetDerivatives`（第79行）。
- `src/base/forcemodel/NumericJacobianOriginal.hpp`：`class NumericJacobianOriginal`（第42行），MATLAB `numjac` 的移植。`CalculateJacobian(PhysicalModel* F, ...)`（第50-53行）用有限差分+稀疏结构求状态雅可比，供 CSALT/估计使用。
- `src/base/forcemodel/ODEModelException.hpp`：`class ODEModelException : public BaseException`（第39行），力模型统一异常。

---

### 2.2 solarsys —— 太阳系、天体与星历

`solarsys` 提供力模型所需的"引力体位置/速度、天体参数、大气密度、地影、太阳通量"等数据。核心分层：`GmatBase → SpacePoint → CelestialBody → 各天体`；另有一条 `SpacePoint → CalculatedPoint → Barycenter/LibrationPoint` 的"计算点"支线。

#### 2.2.1 SolarSystem —— 太阳系容器（近似单例）

- 文件：`src/base/solarsys/SolarSystem.hpp` / `.cpp`
- 职责：持有并管理所有在用天体、行星历源、SPICE 内核，是 GMAT 任务里唯一的太阳系对象（"近似单例"——每个 Sandbox 建一个，全局共享）。
- 关键成员（`SolarSystem.hpp`）：
  - 天体名常量：`SUN_NAME/EARTH_NAME/MOON_NAME/...`（第197-266行），覆盖到各大行星卫星（土星的 18 颗、天王星的 15 颗等）。
  - `bodiesInUse`（`std::vector<CelestialBody*>`，第321行）、`specialPoints`（`map<string,SpecialCelestialPoint*>`，第329行）。
  - `thePlanetaryEphem`（第299行）、`theDefaultDeFile`（第316行）、`planetarySPK`（第332行，`__USE_SPICE__` 时）。
  - 参数：`EPHEMERIS_SOURCE/DE_FILE_NAME/SPK_FILE_NAME/OVERRIDE_TIME_SYSTEM/EPHEM_UPDATE_INTERVAL`（第279-287行）。

**初始化流程**（`src/base/solarsys/SolarSystem.cpp`）：

```cpp
343: SolarSystem::SolarSystem(std::string withName) :
...
393:    Star* theSun     = new Star(SUN_NAME);
...
448:    AddBody(theSun);
...
463:       Planet *newPlanet = new Planet(PLANET_NAMES[ii], SUN_NAME);
...
533:       AddBody(newPlanet);
...
543:       Moon *newMoon = new Moon(MOON_NAMES[ii], MOON_CENTRAL_BODIES[ii]);
...
615:       AddBody(newMoon);
...
623:    SpecialCelestialPoint *ssb = new SpecialCelestialPoint(SOLAR_SYSTEM_BARYCENTER_NAME);
...
640:    SetJ2000Body();
...
655:    CreatePlanetarySource();
```

逐行解释：
- 第393行先建太阳（`Star`），第448行加入列表；第463-533行按 `PLANET_NAMES` 建各行星并 `AddBody`；第543-615行建各卫星（指定中心天体）。
- 第623行建太阳系质心 `SolarSystemBarycenter`（`SpecialCelestialPoint`，其状态直接来自 DE/SPK 星历）。
- 第640行 `SetJ2000Body()`：把所有天体的 J2000 参考体统一设为地球（见 2.2.2），保证全任务坐标一致。
- 第655行 `CreatePlanetarySource()`：创建/配置星历源（默认 DE421，第993行起；含 ASCII→二进制转换与 FileManager 路径解析）。

关键方法：
- `AddBody`（第2025行）把天体加入列表；`GetBody(name)`（第2167/2184行）按名查找（内部 `FindBody`，第3887行）。
- `SetPlanetarySourceName`（`.hpp` 第78行）指定星历源文件；`GetPlanetarySourceTypesInUse`（第77行）。
- `SetSPKFile/SetLSKFile/SetPCKFile`（第134-136行）：SPICE 内核（`.bsp`/`.tls`/`.tpc`）加载入口。

#### 2.2.2 CelestialBody —— 天体基类

- 文件：`src/base/solarsys/CelestialBody.hpp` / `.cpp`
- 职责：天体的位置/速度来源（DE 内核 vs 解析二体 vs SPICE）、物理参数（μ、半径、扁率、质量）、自转/章动、大气模型聚合。
- 关键枚举（`CelestialBody.hpp` 第57-150行的 `namespace Gmat`）：
  - `PosVelSource { DE405, DE421, DE424, SPICE }`（第60-69行）——星历来源。
  - `BodyType { STAR, PLANET, MOON, ASTEROID, COMET, SPECIAL_CELESTIAL_POINT, KUIPER_BELT_OBJECT }`（第82-92行）。
  - `RotationDataSource { DE_FILE, IAU_2002, FK5_IAU_1980, IAU_SIMPLIFIED, SPICE_KERNEL }`（第123-136行）。
- 关键方法（`CelestialBody.hpp`）：
  - `GetState(A1Mjd)`（第184行）/`GetMJ2000State(A1Mjd)`（第283行）——天体状态与 J2000 状态。
  - `GetGravitationalConstant/GetEquatorialRadius/GetFlattening/GetMass`（第206-210行）。
  - `GetBodyCartographicCoordinates`（第326行）——返回 α、δ、W、Wdot（IAU 自转元素）。
  - `SetTwoBodyElements`（第269行）：用户自定义天体时用开普勒根数解析传播。

**坐标转换核心** `GetMJ2000State`（`CelestialBody.cpp` 第3806-3879行）：

```cpp
3828:    Rvector6         stateEphem    = GetState(atTime);
...
3833:       j2kEphemState = ((CelestialBody*)j2000Body)->GetState(atTime);
...
3871:       j2kState = stateEphem;
...
3876:       j2kState = stateEphem - j2kEphemState;
3879:    return j2kState;
```

解释：`GetState` 返回天体在其参考体坐标系下的状态（DE 文件里各行星状态以太阳系质心或地球为参考）；`GetMJ2000State` 通过**减去 J2000 参考体（地球）的星历状态**，把任意天体状态统一转到 MJ2000Eq 地球系。第3876行 `j2kState = stateEphem - j2kEphemState` 就是这一平移（对地球本身则 `j2kState = stateEphem`，第3871行）。

**星历读取分支** `GetState`（`CelestialBody.cpp` 第1150行起）：
- 若 `posVelSrc == SPICE` 且 SPICE 可用：走 SPICE 内核读取（`SpiceOrbitKernelReader`）。
- 否则 `theSourceFile->GetPosVel(bodyNumber, atTime, overrideTime)`（第1195行）从 `DeFile`/`SlpFile` 读状态。
- 若天体用户自定义（`userDefined`），用 `ComputeTwoBody`（第6272行）= `KeplersProblem(forTime) + cbState`（第6299行），即解析开普勒传播叠加中心天体状态。`KeplersProblem`（第6317行）解开普勒方程。

天体自转：`GetBodyCartographicCoordinates`（第4275行）按 IAU 2000 报告公式计算 α、δ、W；地球额外支持 EOP（`Planet.hpp` 第126-128行 `NUTATION_UPDATE_INTERVAL/EOP_FILE_NAME`）与章动更新间隔。

#### 2.2.3 各天体类（Planet/Star/Moon/Asteroid/Comet/SpecialCelestialPoint）

- `Planet.hpp`：`class Planet : public CelestialBody`（第62行）。额外参数 `NUTATION_UPDATE_INTERVAL`（章动更新间隔，仅地球）与 `EOP_FILE_NAME`（第126-128行）。地球特殊逻辑：`SetTwoBodyEpoch/Elements` 需转发给太阳（第34-42行注释——太阳无中心体，需借用地球信息反推其状态）。
- `Star.hpp`：`class Star : public CelestialBody`（第49行）。太阳专属：`RADIANT_POWER`（辐射功率 W/m²）、`REFERENCE_DISTANCE`（参考距离 km）、`PHOTOSPHERE_RADIUS`（第92-94行）。`GetRadiantPower/GetReferenceDistance`（第61-62行）供 SRP 与电源系统使用。
- `Moon.hpp`：`class Moon : public CelestialBody`（第44行）。默认数据仅 Luna/Phobos/Deimos（第31行注释）。重写 `GetBodyCartographicCoordinates`（第58行）。
- `Asteroid.hpp` / `Comet.hpp`：分别 `class Asteroid/Comet : public CelestialBody`（第43行/第43行），无额外参数（`ParamCount = CelestialBodyParamCount`），是"轻量天体"占位，供用户自定义小天体。
- `SpecialCelestialPoint.hpp`：`class SpecialCelestialPoint : public CelestialBody`（第48行）。用于太阳系质心（SSB）等"可从星历文件取状态"的特殊点；`ComputeTwoBody`（第69行）被禁用（其状态只来自 DE/SPK）。

#### 2.2.4 计算点：CalculatedPoint / Barycenter / LibrationPoint

- `CalculatedPoint.hpp`：`class CalculatedPoint : public SpacePoint`（第57行，**抽象类**）。"计算点"是由两个以上天体计算出的点（质心、平动点）。持有 `bodyList`（`std::vector<SpacePoint*>`，第166行）、`bodyNames`（第168行）、`isBuiltIn`（第174行）。纯虚 `CheckBodies()`（第195行）强制子类校验天体类型。`SetRefObject`（第127行）用于注入参与计算的天体。
- `Barycenter.hpp`：`class Barycenter : public CalculatedPoint`（第50行）。按质量加权求质心：`GetMass()`（第82行）聚合成员质量，`GetMJ2000State`（第66-76行）返回 `Σ(mᵢ·rᵢ)/Σmᵢ`。内置 SSB/EMB（太阳系/地月质心）通过 `builtInSP`（第97行）指向真实星历点。
- `LibrationPoint.hpp`：`class LibrationPoint : public CalculatedPoint`（第49行）。参数 `PRIMARY_BODY_NAME/SECONDARY_BODY_NAME/WHICH_POINT`（第116-119行）；用牛顿迭代解平动点（L1-L5），收敛容差 `CONVERGENCE_TOLERANCE = 1.0E-8`、最大迭代 `MAX_ITERATIONS = 2000`（第126-127行）。

#### 2.2.5 星历读取：PlanetaryEphem / DeFile / SlpFile / EphemSmoother

- `PlanetaryEphem.hpp`：星历接口基类（第59行，非 GmatBase）。纯虚：`GetBodyID`（第86行）、`GetPosVel`（第103-110行）、`GetStartDayAndYear`（第121行）。枚举 `DeFileType { DE405, DE421, DE424, DE430 }` 与 `DeFileFormat { ASCII, BINARY }`（第43-56行）。
- `DeFile.hpp`：`class DeFile : public PlanetaryEphem`（第51行）。JPL DE 内核读取（复用 JPL/JSC D. Hoffman 代码）。天体 ID 常量（第109-123行）：`SUN_ID=10, MERCURY=0, ..., EARTH=2, MOON=9, ..., SS_BARY=11, EM_BARY=12, NUTATIONS=13, LIBRATIONS=14`。各格式系数数组尺寸（第134-139行）：`ARRAY_SIZE_405/421/424/430 = 1018`、`ARRAY_SIZE_200 = 826`。底层函数：`Read_Coefficients/Interpolate_State/Interpolate_Libration/Interpolate_Nutation`（第378-414行）——切比雪夫多项式插值。
- `SlpFile.hpp`：`class SlpFile : public PlanetaryEphem`（第42行）。GTDS（Goddard Trajectory Determination System）SLP 曲线拟合星历（第110-156行 `slp_header` 结构），仅支持 Sun/Earth/Moon 三体（`MAX_BODIES = 3`，第98行）。`open_slp/read_slp/slp_pos/slp_vel`（第164-173行）。
- `EphemSmoother.hpp`：`class EphemSmoother`（第44行）。把星历点拟合成三次样条，为 CSALT 配点法提供连续状态/导数（`GetState` 返回 `state/dState/ddState`，第54-56行）。`CreateSmoothedEphem`（第58-64行）按"每圈区域数 nRegionsPerRevolution"布结。内部 `EphemData` 结构（第68行）存 a/b/c/d 三次多项式系数。

#### 2.2.6 大气模型：AtmosphereModel 及四个实现

- `AtmosphereModel.hpp`：`class AtmosphereModel : public GmatBase`（第49行）。核心纯虚 `Density(position, density, epoch, count)`（第79行）——所有大气模型的核心输出（kg/m³）。持有 `SolarFluxReader* fluxReader`（第157行）、`CelestialBody* mCentralBody`（第163行）、`CoordinateSystem* cbFixed`（第214行）、`angVel[3]`（第216行）。可选能力：`Wind/HasWindModel`（第108-110行）、`Temperature`（第111行）、`Pressure`（第115行）。空间天气参数：`NOMINAL_FLUX/NOMINAL_AVERAGE_FLUX/NOMINAL_MAGNETIC_INDEX/CSSI_WEATHER_FILE/SCHATTEN_WEATHER_FILE`（第276-281行）。
- `ExponentialAtmosphere.hpp`：`class ExponentialAtmosphere : public AtmosphereModel`（第64行）。公式（第50行注释）：`ρ = ρ₀·exp(−(h_ellp − h₀)/H)`。分层表格：`scaleHeight/refHeight/refDensity`（第105-109行）+ `altitudeBands`（第111行）。`FindBand`（第116行）查高度所在带，`Smooth`（第117行）做带边界平滑。源：Vallado pp.532-534 与 Wertz p.820（第28行注释）。
- `SimpleExponentialAtmosphere.hpp`：`class ... : public AtmosphereModel`（第65行），STK 三参数指数模型（单一 `scaleHeight/refHeight/refDensity`，第80-84行），无分层表，速度更快。
- `JacchiaRobertsAtmosphere.hpp`：`class ... : public AtmosphereModel`（第42行）。Jacchia-Roberts 1971 模型（Swingby 移植）。核心 `JacchiaRoberts(height, sc, sun, a1_time)`（第111-112行）、`exotherm`（第113-114行，外大气层温度）、`rho_100/rho_125/rho_cor/rho_high`（第115-120行，按高度分段的密度）。常量表：`CON_C/CON_L/M_CON/S_CON/ZETA_CON/MOL_MASS/NUM_DENS/CON_DEN`（第84-105行）。`GEOPARMS geo`（第107行）存 F107/Kp/温度。
- `Msise90Atmosphere.hpp`：`class ... : public AtmosphereModel`（第41行）。封装 MSISE-90（a.i. Solutions 从 Fortran 移植，第30-32行注释）。底层为 `msise90_sub.c`（C 移植）与 `msise90_sub.for`（原始 Fortran）两个文件——`msise90_sub.c` 暴露 `gtd7` 入口供 C++ 调用。
- `msise90_sub.c` / `msise90_sub.for`：MSISE-90 中性大气经验模型的底层实现（输入太阳 F10.7/Ap、地磁活动、位置/时间，输出各成分数密度与总密度）。`.for` 是上游原始 Fortran，`.c` 是供 GMAT 链接的 C 版本。

#### 2.2.7 ShadowState / SolarFluxReader / PlanetographicRegion / MediaCorrectionInterface

- `ShadowState.hpp`：`class ShadowState`（第36行）。`FindShadowState(state, cbSun, sunSat, sunRad, bodyRad)`（第47-49行）判地影；`GetPercentSunInPenumbra`（第54行）返回半影受照百分比（SRP 与太阳电源共用）。
- `SolarFluxReader.hpp`：`class SolarFluxReader`（第46行）。读取 CSSI 历史通量文件与 Schatten 预测文件。结构 `FluxDataCSSI`（第55-67行：`kp[8]/ap[8]/adjF107/obsF107` 等）与 `FluxData`（第69-155行：`F107a[9]/apSchatten[3]`）。`GetInputs(GmatEpoch)`（第245行）返回某历元的 F10.7/F10.7A/Ap/Kp；`LoadCSSIHistoric/LoadCSSIPredict/LoadSchattenData`（第228-230行）。
- `PlanetographicRegion.hpp`：`class PlanetographicRegion : public BodyFixedPoint`（第42行）。天体表面的经纬度+高度多边形区域。`isWithin(lat, lon, height, distance)`（第58行）点在多边形判据；`EllipsoidToCartesian/CartesianToEllipsoid`（第59-60行）椭球坐标互转；`ReadLatitudeLongitudeFile`（第132行）从文件读顶点。
- `MediaCorrectionInterface.hpp`：`class MediaCorrectionInterface : public GmatBase`（第38行）。测量介质改正接口（对流层/电离层，供第13章估计插件与第8章测量模型用）。`Correction()`（第67行）纯虚，输出改正量；`SetTemperature/SetPressure/SetHumidityFraction/SetWaveLength/SetElevationAngle/SetRange`（第56-62行）设置改正输入；`LoadTRK223DataFile`（第65行）读 DSN TRK-2-23 数据。

#### 2.2.8 异常类

- `AtmosphereException.hpp`（第37行）、`PlanetaryEphemException.hpp`（第37行）、`SolarSystemException.hpp`（第37行）：均为 `BaseException` 派生，分别带前缀 "Atmosphere model exception: " 等，用于大气、星历、太阳系子系统报错。

---

### 2.3 spacecraft —— 航天器与空间对象

继承链：`GmatBase → SpacePoint → SpaceObject → Spacecraft`（以及 `→ FormationInterface`）。

#### 2.3.1 SpaceObject —— 空间对象基类

- 文件：`src/base/spacecraft/SpaceObject.hpp` / `.cpp`
- 职责：航天器与编队的公共基类，持有"状态 + 参考原点 + 机动标志"。
- 关键成员（`SpaceObject.hpp`）：
  - `GmatState state`（第144行）：六维状态（含 STM 时更高维）的容器。
  - `Rvector3 acceleration`（第146行）：最近加速度。
  - `isManeuvering`（第149行）与 `maneuveringMembers`（第151行）：有限机动标记。
  - `origin`（`SpacePoint*`，第155行）与 `originName`（第153行）：状态参考原点（通常地球）。
  - `lastStopTriggered`（第159行）：最近触发的停止条件名（供第7章停止条件）。
- 关键方法：`GetState()/SetEpoch()/GetEpochGT()`（第51-59行）、`GetMJ2000State` 系列（第101-114行，通过 `origin->GetMJ2000State` 平移实现）、`GetOrigin()/SetOrigin()`（第98-99行）。

`SpaceObject` 与坐标系的交互：`GetMJ2000State` 把"以 origin 为原点的状态"叠加 `origin` 自身的 MJ2000 状态，得到绝对 J2000 状态——这是航天器状态能与 `CelestialBody::GetMJ2000State` 在同一坐标系下互算的基础（力模型里第三体位置与航天器位置的减法依赖这一点）。

#### 2.3.2 Spacecraft —— 航天器

- 文件：`src/base/spacecraft/Spacecraft.hpp` / `.cpp`
- 职责：轨道状态（多表示）、坐标系、Epoch、质量特性、推进剂/硬件聚合、估计参数（Cd/Cr/STM）的综合容器。

**轨道状态表示**（`Spacecraft.hpp`）：
- `MultipleReps` 枚举（第496-590行）列出全部状态表示：`Cartesian / Keplerian / Modified Keplerian / SphericalAZFPA / SphericalRADEC / Equinoctial / Modified Equinoctial / Alternate Equinoctial / Delaunay / Planetodetic / Incoming/Outgoing Asymptotes / Brouwer-Lyddane(短/长)`。
- `STATE_REPS`（第601-617行）给表示编号；`MULT_REP_STRINGS`（第592行）对应字符串。
- 转换方法：`GetState(rep)/GetCartesianState()/GetKeplerianState()/GetModifiedKeplerianState()`（第81-86行）；内部 `GetStateInRepresentation/SetStateFromRepresentation`（第963-965行）走 `StateConversionUtil`（第3章数学库）。
- 六要素参数：`ELEMENT1_ID..ELEMENT6_ID`（第367-372行，含义随 `STATE_TYPE` 变化）、`ANOMALY_ID`（第381行，真近点角/偏近点角）。

**坐标系与 Epoch**：
- `internalCoordSystem`（第732行，内部传播用 MJ2000Eq）、`coordinateSystem`（第734行，GUI/脚本输入输出用）、`coordSysName`（第736行）。
- `originMu/originFlattening/originEqRadius`（第739-743行）：中心天体参数缓存（用于元素↔笛卡尔转换）。
- Epoch 处理：`epochSystem/epochFormat/epochType`（第698-702行）区分 A1/TAI/UTC/TT 时间系统与 Gregorian/ModJulian 格式；`SetEpoch(string)`（第297行）与 `SetEpoch(type, ep, a1mjd)`（第298行）解析脚本时间字符串；`scEpochStr`（第650行）缓存文本形式。
- `GetEpochString()/GetUTCEpochString()/SetDateFormat()`（第291-293行）。

**推进剂与硬件聚合**（第772-786行）：

```cpp
772:    /// Fuel tank names
773:    StringArray       tankNames;
...
776:    /// Pointers to the fuel tanks
777:    ObjectArray       tanks;
780:    /// Pointers to the spacecraft thrusters
782:    ObjectArray       thrusters;
784:    PowerSystem       *powerSystem;
786:    Real              totalMass;
```

- `tanks/thrusters/powerSystem`（第777/782/784行）为硬件聚合；`hardwareNames/hardwareList`（第887-889行）为通用硬件列表（通信硬件等）。
- `totalMass`（第786行）= `dryMass`（第651行）+ 各箱燃料质量。`UpdateMassProperties()`（第936行）在每次质量变化后重算质心/惯量：`CalculateTotalMass/CalculateSystemCenterOfMass/CalculateSystemMOI`（第937-939行）。
- 阻力/光压参数：`coeffDrag`（Cd0，第669行）、`Cd = Cd0*(1+CdEpsilon)`（第671行注释）、`dragArea`（第674行）、`reflectCoeff`（Cr0，第678行）、`Cr`（第680行）、`srpArea`（第675行）。
- SPAD/N 板：`spadSRPReader/spadDragReader`（第837、855行）、`plateList`（第874行，N 板反射面板）。
- 姿态：`attitude`（`Attitude*`，第764行）、`GetAttitude(a1mjdTime)`（第93行）、`GetAttitudeRotationMatrix`（第99行）——SRP 的 ATTITUDE_BASED 方向与 N 板反射率依赖它。

**Clone 语义**：`Spacecraft::Clone`（第141行）+ `Copy`（第142行）是深拷贝——`CloneOwnedObjects(att, tanks, thrusters, pwr, otherHw)`（第953-955行）克隆所有硬件并重建指向关系；`DeleteOwnedObjects`（第950-952行）负责析构时清理。`HasLocalClones/UpdateClonedObject/UpdateClonedObjectParameter`（第324-327行）支持 Sandbox 的"克隆对象同步"机制（估计/命令模式下工作副本与主副本参数联动）。

**估计接口**：`GetEstimationParameterID/GetParameterSTM/MapCovarianceToParameters`（第309-321行）；STM 相关 `fullSTM/fullAMatrix/fullSTMRowCount/stmIndices`（第806-812行）、`SetSTMToIdentityMatrix`（第348行）。`externalStmSources`（第820行）供外部硬件（如估计插件的 Transmitter 频率偏置）贡献 STM 条目。

#### 2.3.3 FormationInterface / Plate / TextTrajectoryFile / SpaceObjectException

- `FormationInterface.hpp`：`class FormationInterface : public SpaceObject`（第40行）。编队的代理接口——实际 `Formation` 类在 `libFormation`（第27-29行注释，Formation 插件）。纯虚 `BuildState/UpdateElements/UpdateState`（第49-51行）定义编队成员状态合成契约。
- `Plate.hpp`：`class Plate : public GmatBase`（第43行）。N 板光压模型的一块反射面板。`plateType`（第158行，`FixedInBody/SunFacing/File`）、`plateNormal/plateArea/areaCoeff`（第165-171行）、`litFrac/specularFrac/diffuseFrac`（第176-185行，受照比例/镜面/漫反射比例）。`GetReflectance/GetReflectanceI/GetReflectanceDerivative`（第122-139行）计算惯性系反射面积矢量及其对状态/系数的偏导（供 SRP 的 NPlate 加速度与 STM）。
- `TextTrajectoryFile.hpp`：`class TextTrajectoryFile`（第68行）。读 7 列文本轨迹（`NUM_ITEM_IN_LINE = 7`，第48行：Time,X,Y,Z,Vx,Vy,Vz），存入 `TrajectoryArray`（第53行），用于从文件初始化轨迹。
- `SpaceObjectException.hpp`：`class SpaceObjectException : public BaseException`（第39行），前缀 "SpaceObject Exception Thrown: "。

---

### 2.4 hardware —— 硬件全家族

继承链：`GmatBase → Hardware → {FuelTank→(ChemicalTank/ElectricTank), Thruster→(ChemicalThruster/ElectricThruster), PowerSystem→(Solar/Nuclear), Imager}`；`GmatBase → FieldOfView → {ConicalFOV/RectangularFOV/CustomFOV}`。

#### 2.4.1 Hardware —— 硬件基类

- 文件：`src/base/hardware/Hardware.hpp` / `.cpp`
- 职责：定义硬件在航天器本体系（BCS）中的位姿（位置+方向）与通用参数接口。
- 关键成员（`Hardware.hpp`）：
  - `location[3]`（第179行，BCS 中的安装位置，米）、`direction[3]`（第181行，主轴方向）、`secondDirection[3]`（第183行，副方向）。
  - `coordinates` / `rotationInput`（第185、193行）：坐标类型（`Body/Inertial/...`）与旋转输入方式（`DCM/Euler/Construct`）。
  - `Rmatrix33 R_SB`（第203行）：本体系→硬件系的旋转矩阵。
  - FOV 接口：`HasFOV()/GetRotationMatrix()`（第69-70行）、`GetLocation/GetDirection/GetSecondDirection`（第75-77行）。
  - 参数枚举：`COORDINATES/ROTATION_INPUT_TYPE/DIRECTION_*/SECOND_DIRECTION_*/HW_ORIGIN_BCS_*/ROTATION_MATRIX/R_SB*`（第208-233行）。

#### 2.4.2 燃料箱：FuelTank / ChemicalTank / ElectricTank

- `FuelTank.hpp`：`class FuelTank : public Hardware`（第47行）。抽象基类。核心成员：`fuelMass`（第111行）、`fuelCM/fuelMOI`（第113、115行，燃料质心/惯量）、`allowNegativeFuelMass`（第117行）、`noThrusterNeeded`（第119行，允许无推力器直接流质量，用于推力历史文件）。纯虚 `UpdateTank()`（第123行）与 `DepleteFuel(dm)`（第124行）。质量特性访问：`GetFuelMass/GetFuelCM_BCS/GetFuelMOI_BCS`（第103-105行）。
- `ChemicalTank.hpp`：`class ChemicalTank : public FuelTank`（第40行）。化学推进剂箱。成员：`pressure/temperature/refTemperature/volume/density`（第95-103行）、`pressureModel`（第109行，`PRESSURE_REGULATED` 定压 / `BLOW_DOWN` 泄压，第122-126行）。`UpdateTank` 按压力模型更新 `pvBase`（第116行），`DepleteFuel` 减燃料并联动压力/温度。
- `ElectricTank.hpp`：`class ElectricTank : public FuelTank`（第39行）。电推进剂箱（如氙），无额外参数（第79行 `ParamCount = FuelTankParamCount`），仅重写 `UpdateTank/DepleteFuel`。

#### 2.4.3 推力器：Thruster / ChemicalThruster / ElectricThruster

- `Thruster.hpp`：`class Thruster : public Hardware`（第47行）。抽象基类。核心：
  - `friend class FiniteBurn`（第145行）：`FiniteBurn::Fire` 直接读推力器内部数据算推力。
  - 计算量：`thrust/impulse/mDot`（第181-188行，最近推力/比冲/质量流率）、`appliedThrustMag`（第184行，含 scale/duty cycle 的实际推力）。
  - `gravityAccel`（第172行）：比冲（秒）→质量流率换算用的标准重力加速度 `g₀`。
  - `thrustScaleFactor/dutyCycle`（第176、174行）、`decrementMass`（第192行，是否耗质量）、`thrusterFiring`（第194行）。
  - `tanks/mixRatio`（第208-210行）：供燃料箱与混合比。
  - 纯虚 `CalculateMassFlow()`（第141行）与 `CalculateThrustAndIsp()`（第252行）。
  - 方向投影：`ConvertDirectionToInertial/ComputeInertialDirection`（第256-258行）把推力方向从本体系转到惯性系（`inertialDirection`，第190行）。
- `ChemicalThruster.hpp`：`class ChemicalThruster : public Thruster`（第42行）。`COEFFICIENT_COUNT = 16`（第47行）。`cCoefficients[16]`（推力多项式系数）、`kCoefficients[16]`（比冲多项式系数，第80-82行）。参数 `C1..C16/K1..K16`（第92-97行）。

**化学推力器推力多项式**（`ChemicalThruster.cpp` 第798-892行）：

```cpp
843:       thrust = cCoefficients[2];
844:       impulse = kCoefficients[2];
846:       if (!constantExpressions)
847:       {
849:          thrust  += pressure*(cCoefficients[3] + pressure*cCoefficients[4]);
850:          impulse += pressure*(kCoefficients[3] + pressure*kCoefficients[4]);
854:          if (!simpleExpressions) {
855:             thrust  += cCoefficients[5] * pow(pressure, cCoefficients[6]) + ...
861:             impulse += kCoefficients[5] * pow(pressure, kCoefficients[6]) + ...
866:          }
867:       }
871:       thrust  *= pow(temperatureRatio, (1.0 + cCoefficients[14] + pressure*cCoefficients[15]));
873:       impulse *= pow(temperatureRatio, (1.0 + kCoefficients[14] + pressure*kCoefficients[15]));
877:       thrust  += cCoefficients[0] + cCoefficients[1] * pressure;
878:       impulse += kCoefficients[0] + kCoefficients[1] * pressure;
...
884:    appliedThrustMag = thrustScaleFactor * dutyCycle * thrust;
```

解释：推力/比冲是**压力 p 与温度比 (T/T_ref) 的多项式**；第843-850行取常数项与低阶项，第855-866行取高阶幂项（非"简单表达式"时），第871-873行乘温度比修正，第877-878行加 `C0+C1·p` 线性项；第884行最终 `实际推力 = 比例因子 × 占空比 × 推力`。

**质量流率**（`ChemicalThruster.cpp` 第907-957行，火箭方程）：

```cpp
937:             mDot = -thrust / (gravityAccel * impulse);
...
955:    mDot = mDot * dutyCycle;
```

即 `ṁ = −T/(g₀·Isp)`（负号表示质量减少），再乘占空比。

- `ElectricThruster.hpp`：`class ElectricThruster : public Thruster`（第41行）。`ELECTRIC_COEFF_COUNT = 5`（第45行）。参数：`THRUST_MODEL/MAXIMUM_USABLE_POWER/MINIMUM_USABLE_POWER/THRUST_COEFF1..5/MASS_FLOW_COEFF1..5/EFFICIENCY/ISP/CONSTANT_THRUST`（第98-116行）。

**电推力器推力多项式**（`ElectricThruster.cpp` 第793-848行，功率多项式）：

```cpp
828:          thrust = ((thrustCoeff[4] * powerToUse4) +
829:                    (thrustCoeff[3] * powerToUse3) +
830:                    (thrustCoeff[2] * powerToUse2) +
831:                    (thrustCoeff[1] * powerToUse)  +
832:                    thrustCoeff[0]) / 1.0e3;
834:          Real mdot = ((massFlowCoeff[4] * powerToUse4) + ... ) / 1.0e6;
...
848:          thrust = (2.0 * efficiency * powerToUse) / ...
```

解释：推力 = 功率 `P` 的四次多项式（除以 `1e3`，系数给出 mN→N 的换算）；质量流率 = 功率四次多项式除以 `1e6`（mg/s→kg/s）。另一种模式（第848行）`T = 2·η·P/(g₀·Isp)` 由功率、效率、比冲直接导出。`CalculateMassFlow`（第879行）先算 `powerToUse2/3/4`（第915-917行）再评估多项式。默认系数（第144-154行）是一组真实电推的拟合值。

#### 2.4.4 电源系统：PowerSystem / SolarPowerSystem / NuclearPowerSystem

- `PowerSystem.hpp`：`class PowerSystem : public Hardware`（第44行）。基类。核心：`GetBasePower/GetPowerGenerated/GetSpacecraftBusPower/GetThrustPower`（第63-66行，功率/母线功率/可用推力功率）；成员 `initialMaxPower/annualDecayRate/margin/busCoeff1..3`（第107-115行，初始功率/年衰减/裕度/母线系数）。`SetSpacecraft(Spacecraft*)`（第58行）建立与航天器的联系。
- `SolarPowerSystem.hpp`：`class SolarPowerSystem : public PowerSystem`（第39行）。太阳电池阵。`solarCoeff1..5`（第127-131行，功率关于太阳距离的多项式）、`shadowModel/shadowBodies`（第133-139行）、`ShadowState* shadowState`（第143行，地影降低发电量）。`GetPowerGenerated()`（第55行）。
- `NuclearPowerSystem.hpp`：`class NuclearPowerSystem : public PowerSystem`（第38行）。放射性同位素/核电源，无额外参数（第58行），功率基本恒定（只受年衰减影响）。

#### 2.4.5 视场：FieldOfView / ConicalFOV / RectangularFOV / CustomFOV

- `FieldOfView.hpp`：`class FieldOfView : public GmatBase`（第37行，抽象类）。纯虚 `CheckTargetVisibility`（两个重载：单位向量版与锥/钟角版，第56-58行）与 `GetMaskConeAngles/GetMaskClockAngles`（第62-63行，返回视场掩模角供绘图）。`maxExcursionAngle`（第116行，外接圆判据，先粗筛加速）。坐标工具：`ConeClocktoRADEC/RADECtoUnitVec/UnitVecToStereographic`（第139-150行）。
- `ConicalFOV.hpp`：`class ConicalFOV : public FieldOfView`（第32行）。单参数 `fieldOfViewAngle`（第75行，半锥角弧度）。可见性判据：锥角 ≤ 视场角。
- `RectangularFOV.hpp`：`class RectangularFOV : public FieldOfView`（第34行）。`angleWidth/angleHeight`（第83-84行）定义矩形视场。
- `CustomFOV.hpp`：`class CustomFOV : public FieldOfView`（第37行）。任意多边形视场：`coneAngleVec/clockAngleVec`（第105-106行）定义边界点，经立体投影（`xProjectionCoordArray/yProjectionCoordArray`，第111-112行）后用线段相交算法做点在多边形判断。`ReadConeClockAngles`（第136行）从文件读边界；`CheckRegionVisibility`（第57行）判区域可见性。

#### 2.4.6 Imager 与异常类

- `Imager.hpp`：`class Imager : public Hardware`（第38行）。带视场的成像硬件中间类（相机等）。持有 `fov/fovName/fovIsModeled`（第151-153行，可选 FOV）与 `naifID`（第154行）。`CheckTargetVisibility`（第140行）、`GetMaskConeAngles/ClockAngles`（第141-142行）、`GetFieldOfView/HasFOV`（第144-145行）。是"有 FOV 的硬件"与"无 FOV 的硬件"之间的隔离层（第26-28行注释）。
- `HardwareException.hpp`：`class HardwareException : public BaseException`（第39行）。
- `FieldOfViewException.hpp`：`class FieldOfViewException : public BaseException`（第36行）。

#### 2.4.7 通信硬件（Antenna/Transmitter/Receiver/Transponder/Sensor）——本章范围外的说明

任务列出的通信类硬件**不在** `src/base/hardware/`，它们位于 `plugins/EstimationPlugin/src/base/hardware/`（属于第13章插件体系）：`Antenna`、`Transmitter`、`Receiver`、`Transponder`、`Sensor` 及配套 `SignalData` 等。这些类继承 `Hardware` 基类（本章 2.4.1），作为"信号路径"的端点接入估计/测量的数据流——它们与订阅者（subscriber，[第8章](CH08-base-subsystems.md)）的关系是：估计插件把"发射/接收硬件"产生的测量与地面站/航天器状态绑定，经由 GMAT 的 Publisher/Subscriber 机制发布给报告、残差、绘图等订阅者。具体讲解见 [第13章](CH13-plugins-a.md)。

---

## 三、关键设计模式与数据流

### 3.1 继承体系总览

```
GmatBase
├── PhysicalModel (forcemodel)
│   ├── ODEModel                     ← 容器，叠加所有力
│   ├── GravityBase → HarmonicField → GravityField
│   ├── PointMassForce / DragForce / SolarRadiationPressure
│   ├── FiniteThrust (瞬态) / RelativisticCorrection / EventModel
├── SpacePoint
│   ├── CelestialBody → Planet/Star/Moon/Asteroid/Comet/SpecialCelestialPoint
│   ├── SpaceObject → Spacecraft / FormationInterface
│   └── CalculatedPoint → Barycenter / LibrationPoint
├── Hardware → FuelTank/Thruster/PowerSystem/Imager → 具体子类
├── FieldOfView → Conical/Rectangular/CustomFOV
├── AtmosphereModel → Exponential/SimpleExponential/JacchiaRoberts/Msise90
└── Harmonic → HarmonicGravity            (纯数值引擎，不继承 GmatBase)
```

### 3.2 工厂与注册

所有领域类（`ODEModel`、`PointMassForce`、`DragForce`、`SolarSystem`、`Spacecraft`、`ChemicalThruster` 等）都在各自 `.cpp` 末尾通过 `GmatFactory` 注册（`REGISTER_OBJECT` 类宏），由第4章的 `FactoryManager` 按脚本/GUI 字符串创建。类名（如 `"DragForce"`）即工厂键。

### 3.3 核心数据流：ODE 右手边如何被组装

这是本章与 [第7章](CH07-propagator.md) 传播器的衔接点，完整链路如下：

1. **脚本配置**：脚本/GUI 创建 `Spacecraft`、`ODEModel`（内含 `GravityField` + `DragForce` + `SRP` 等）与 `PropSetup`（指定积分器）。
2. **状态管理器**（第7章 `PropagationStateManager`）：初始化时把 `Spacecraft` 的笛卡尔状态、质量、STM 等打包成一条 `GmatState`，并调用每个力模型的 `SetStart(...)` 告知其导数在输出向量中的偏移。
3. **力模型参数注入**：`ODEModel::SetupSpacecraftData`（`ODEModel.cpp` 第2675行起）把航天器的 `Cd/Cr/面积/质量` 等参数 ID 缓存到 `satIds[]`，供每个力在 `GetDerivatives` 里按 ID 高速读取。
4. **积分器步进**：积分器（Runge-Kutta 等，第7章）在每一步调用 `ODEModel::GetDerivatives(state, dt, order)`。
5. **叠加**：`ODEModel::GetDerivatives` 遍历 `forceList`，逐个调用 `force->GetDerivatives(state, dt, order)`，把每个力的 `deriv` 累加进总 `deriv`（`ODEModel.cpp` 第3261-3363行），再补速度项（第3380-3391行）。
6. **返回**：积分器拿到完整 `ẋ`，推进状态；停止条件/事件定位（第7章）在需要时调用 `EventModel`/`GetForceMaxStep` 决定步长与终止。

力模型内部的数据流（以一次积分步为例）：
- `DragForce`：`GetDerivatives` → 读 `dragCoeff/area/mass`（来自航天器）→ `TranslateOrigin`（转到大气体）→ `GetDensity`（`AtmosphereModel::Density`，可能读 `SolarFluxReader` 的 F10.7/Ap）→ `a = −½(CdA/m)ρ v_rel² v̂_rel` → 写 `deriv`。
- `SRP`：`GetDerivatives` → 从 `SolarSystem` 拿太阳位置 → 算 `sunDistance/forceVector` → `ShadowState::FindShadowState` 得 `percentSun` → `a = ν(CrA/m)P_sun(1AU/r)²ŝ` → 写 `deriv`。
- `GravityField`：`GetDerivatives` → 状态转到固连系（`CoordinateConverter` + `EopFile`）→ `HarmonicGravity::CalculateFullField`（球谐递推 + 固体潮）→ `InverseRotate` 回惯性系 → 写 `deriv`。

### 3.4 设计模式要点

- **策略模式**：每个 `PhysicalModel` 是独立"力策略"，`ODEModel` 通过统一接口 `GetDerivatives` 组合它们，用户可在脚本里自由增删力。
- **线性叠加 + 位置映射**：力的加速度线性可加，`SetStart/SupportsDerivative` 让每个力只写自己的分量区间，容器负责拼接（`deriv[j] += ddt[j]`）。
- **缓存/复用**：`GravityField::cache`（静态 `vector<HarmonicGravity*>`）复用球谐系数；`CelestialBody` 缓存最近星历状态（`lastState/j2kState`）避免重复查表。
- **接口隔离**：`FormationInterface`（编队）、`MediaCorrectionInterface`（介质改正）、`PlanetaryEphem`（星历）都是"基类定契约、插件/实现类补实现"的接口模式。
- **瞬态力生命周期**：`FiniteThrust` 由 `BeginFiniteBurn/EndFiniteBurn` 命令动态增删（`IsTransient()==true`），`ODEModel::UpdateTransientForces` 管理其加入/移除（第413行）。
- **单位约定**：状态/加速度统一 `km`、`km/s`、`km/s²`，MJ2000Eq 坐标系；大气密度 `kg/m³`、面积 `m²`，因此 Drag/SRP 预因子内嵌 `*1000` 或 `M_TO_KM` 换算（`DragForce.cpp` 第1217行、`SRP.cpp` 第1077行）。

---

## 四、文件清单附录

### forcemodel（30 文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| src/base/forcemodel/PhysicalModel.hpp/.cpp | 力模型抽象基类 | `PhysicalModel`、`GetDerivatives`、`SetStart`、`IsTransient/DepletesMass` |
| src/base/forcemodel/ODEModel.hpp/.cpp | 力聚合容器 | `ODEModel`、`GetDerivatives`（求和循环）、`AddForce`、`SetupSpacecraftData` |
| src/base/forcemodel/ODEModelException.hpp/.cpp | 力模型异常 | `ODEModelException` |
| src/base/forcemodel/GravityBase.hpp/.cpp | 高级引力模型标记基类 | `GravityBase` |
| src/base/forcemodel/HarmonicField.hpp/.cpp | 球谐场基类 | `HarmonicField`、`SetDegreeOrder`、`SetFilename` |
| src/base/forcemodel/GravityField.hpp/.cpp | 中心天体球谐引力 | `GravityField`、`GetHarmonicGravity`、`Calculate` |
| src/base/forcemodel/PointMassForce.hpp/.cpp | 质点引力 | `PointMassForce`、`GetDerivatives`（μ/r³ + 间接项） |
| src/base/forcemodel/DragForce.hpp/.cpp | 大气阻力 | `DragForce`、`BuildPrefactors`、`Accelerate`、`GetDensity` |
| src/base/forcemodel/SolarRadiationPressure.hpp/.cpp | 太阳光压 | `SolarRadiationPressure`、`ComputeSPADAcceleration`、`ComputeNPlateAcceleration`、`GetShadowStateFromAllBodies` |
| src/base/forcemodel/FiniteThrust.hpp/.cpp | 有限推力（瞬态力） | `FiniteThrust`、`GetDerivatives`（推力累加 + dm/dt） |
| src/base/forcemodel/RelativisticCorrection.hpp/.cpp | 相对论摄动 | `RelativisticCorrection` |
| src/base/forcemodel/EventModel.hpp/.cpp | 事件函数导数容器 | `EventModel`、`SetEventLocators` |
| src/base/forcemodel/NumericJacobianOriginal.hpp/.cpp | 数值雅可比 | `NumericJacobianOriginal`、`CalculateJacobian` |
| src/base/forcemodel/harmonic/Harmonic.hpp/.cpp | 球谐递推内核 | `Harmonic`、`CalculateField`、`Cnm/Snm` |
| src/base/forcemodel/harmonic/HarmonicGravity.hpp/.cpp | 球谐引力 + 固体潮 | `HarmonicGravity`、`CalculateFullField`、`IncrementSolidTide` |

### solarsys（55 文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| src/base/solarsys/SolarSystem.hpp/.cpp | 太阳系容器 | `SolarSystem`、`AddBody`、`GetBody`、`CreatePlanetarySource`、`SetJ2000Body` |
| src/base/solarsys/CelestialBody.hpp/.cpp | 天体基类 | `CelestialBody`、`GetState`、`GetMJ2000State`、`ComputeTwoBody`、`KeplersProblem`、`GetBodyCartographicCoordinates` |
| src/base/solarsys/Planet.hpp/.cpp | 行星 | `Planet`（EOP/章动） |
| src/base/solarsys/Star.hpp/.cpp | 恒星（太阳） | `Star`（辐射功率/光球半径） |
| src/base/solarsys/Moon.hpp/.cpp | 卫星 | `Moon` |
| src/base/solarsys/Asteroid.hpp/.cpp | 小行星 | `Asteroid` |
| src/base/solarsys/Comet.hpp/.cpp | 彗星 | `Comet` |
| src/base/solarsys/SpecialCelestialPoint.hpp/.cpp | 特殊天体点（SSB 等） | `SpecialCelestialPoint` |
| src/base/solarsys/CalculatedPoint.hpp/.cpp | 计算点基类 | `CalculatedPoint`、`CheckBodies` |
| src/base/solarsys/Barycenter.hpp/.cpp | 质心 | `Barycenter`、`GetMass` |
| src/base/solarsys/LibrationPoint.hpp/.cpp | 平动点 | `LibrationPoint` |
| src/base/solarsys/PlanetaryEphem.hpp/.cpp | 星历接口 | `PlanetaryEphem`、`GetPosVel`、`GetBodyID` |
| src/base/solarsys/DeFile.hpp/.cpp | JPL DE 内核 | `DeFile`、`Read_Coefficients`、`Interpolate_State`、`Interpolate_Nutation` |
| src/base/solarsys/SlpFile.hpp/.cpp | GTDS SLP 星历 | `SlpFile`、`slp_pos`、`slp_vel` |
| src/base/solarsys/EphemSmoother.hpp/.cpp | 星历样条平滑 | `EphemSmoother`、`CreateSmoothedEphem` |
| src/base/solarsys/SolarFluxReader.hpp/.cpp | 太阳通量读取 | `SolarFluxReader`、`GetInputs`、`LoadCSSIHistoric` |
| src/base/solarsys/AtmosphereModel.hpp/.cpp | 大气模型基类 | `AtmosphereModel`、`Density`、`Wind` |
| src/base/solarsys/ExponentialAtmosphere.hpp/.cpp | 指数大气 | `ExponentialAtmosphere`、`FindBand`、`Smooth` |
| src/base/solarsys/SimpleExponentialAtmosphere.hpp/.cpp | 三参数指数大气 | `SimpleExponentialAtmosphere` |
| src/base/solarsys/JacchiaRobertsAtmosphere.hpp/.cpp | Jacchia-Roberts | `JacchiaRobertsAtmosphere`、`JacchiaRoberts`、`exotherm` |
| src/base/solarsys/Msise90Atmosphere.hpp/.cpp | MSISE-90 封装 | `Msise90Atmosphere` |
| src/base/solarsys/msise90_sub.c | MSISE-90 C 底层 | `gtd7` |
| src/base/solarsys/msise90_sub.for | MSISE-90 Fortran 底层 | `gtd7` |
| src/base/solarsys/ShadowState.hpp/.cpp | 地影判定 | `ShadowState`、`FindShadowState`、`GetPercentSunInPenumbra` |
| src/base/solarsys/PlanetographicRegion.hpp/.cpp | 行星表面区域 | `PlanetographicRegion`、`isWithin`、`EllipsoidToCartesian` |
| src/base/solarsys/MediaCorrectionInterface.hpp/.cpp | 介质改正接口 | `MediaCorrectionInterface`、`Correction` |
| src/base/solarsys/AtmosphereException.hpp | 大气异常 | `AtmosphereException` |
| src/base/solarsys/PlanetaryEphemException.hpp/.cpp | 星历异常 | `PlanetaryEphemException` |
| src/base/solarsys/SolarSystemException.hpp/.cpp | 太阳系异常 | `SolarSystemException` |

### spacecraft（11 文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| src/base/spacecraft/SpaceObject.hpp/.cpp | 空间对象基类 | `SpaceObject`、`GetState`、`GetMJ2000State`、`GetOrigin` |
| src/base/spacecraft/Spacecraft.hpp/.cpp | 航天器 | `Spacecraft`、`GetState(rep)`、`UpdateMassProperties`、`Clone`、`GetAttitudeRotationMatrix` |
| src/base/spacecraft/SpaceObjectException.hpp | 空间对象异常 | `SpaceObjectException` |
| src/base/spacecraft/FormationInterface.hpp/.cpp | 编队代理接口 | `FormationInterface`、`BuildState/UpdateElements/UpdateState` |
| src/base/spacecraft/Plate.hpp/.cpp | N 板反射面板 | `Plate`、`GetReflectance`、`GetReflectanceDerivative` |
| src/base/spacecraft/TextTrajectoryFile.hpp/.cpp | 文本轨迹读取 | `TextTrajectoryFile` |

### hardware（34 文件）

| 相对路径 | 职责 | 关键类/函数 |
|---|---|---|
| src/base/hardware/Hardware.hpp/.cpp | 硬件基类 | `Hardware`、`GetLocation/GetDirection`、`R_SB` |
| src/base/hardware/FuelTank.hpp/.cpp | 燃料箱基类 | `FuelTank`、`DepleteFuel`、`UpdateTank` |
| src/base/hardware/ChemicalTank.hpp/.cpp | 化学燃料箱 | `ChemicalTank`（压力/温度/体积） |
| src/base/hardware/ElectricTank.hpp/.cpp | 电推燃料箱 | `ElectricTank` |
| src/base/hardware/Thruster.hpp/.cpp | 推力器基类 | `Thruster`、`CalculateMassFlow`、`CalculateThrustAndIsp`、`ConvertDirectionToInertial` |
| src/base/hardware/ChemicalThruster.hpp/.cpp | 化学推力器 | `ChemicalThruster`（C/K 16 项多项式） |
| src/base/hardware/ElectricThruster.hpp/.cpp | 电推力器 | `ElectricThruster`（功率多项式） |
| src/base/hardware/PowerSystem.hpp/.cpp | 电源基类 | `PowerSystem`、`GetPowerGenerated` |
| src/base/hardware/SolarPowerSystem.hpp/.cpp | 太阳电源 | `SolarPowerSystem`（solarCoeff + 地影） |
| src/base/hardware/NuclearPowerSystem.hpp/.cpp | 核电源 | `NuclearPowerSystem` |
| src/base/hardware/FieldOfView.hpp/.cpp | 视场基类 | `FieldOfView`、`CheckTargetVisibility`、`GetMaskConeAngles` |
| src/base/hardware/ConicalFOV.hpp/.cpp | 锥形视场 | `ConicalFOV` |
| src/base/hardware/RectangularFOV.hpp/.cpp | 矩形视场 | `RectangularFOV` |
| src/base/hardware/CustomFOV.hpp/.cpp | 自定义多边形视场 | `CustomFOV`、`ReadConeClockAngles` |
| src/base/hardware/Imager.hpp/.cpp | 带 FOV 成像硬件 | `Imager`、`CheckTargetVisibility` |
| src/base/hardware/HardwareException.hpp/.cpp | 硬件异常 | `HardwareException` |
| src/base/hardware/FieldOfViewException.hpp/.cpp | 视场异常 | `FieldOfViewException` |

> 说明：通信类硬件 `Antenna/Transmitter/Receiver/Transponder/Sensor` 位于 `plugins/EstimationPlugin/src/base/hardware/`，见 [第13章](CH13-plugins-a.md)；其与订阅者的关系见 [第8章](CH08-base-subsystems.md)。任务描述中的 `FiniteBurn` 位于 `src/base/burn/`，见 [第7章](CH07-propagator.md)。
