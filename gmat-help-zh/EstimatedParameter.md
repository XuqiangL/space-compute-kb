# 待估参数（EstimatedParameter）

> 译自 GMAT R2026a 帮助文档 EstimatedParameter.html

**EstimatedParameter** —— 用于在扩展卡尔曼滤波中对动态估计参数建模。

## 描述

`EstimatedParameter` 资源允许用户在卡尔曼滤波器中将动态参数（如阻力系数 Cd、太阳光压系数 Cr）以及观测偏差建模为随机过程。该资源目前仅实现一阶高斯-马尔可夫（Gauss-Markov）过程。用户配置的 `EstimatedParameter` 资源实例被指定到 `Spacecraft.SolveFors` 列表中，以启用基于该建模过程的估计。

目前支持的求解参数仅为航天器阻力系数（Cd）和大气密度比例因子（AtmosDensityScaleFactor）。`EstimatedParameter` 资源仅用于卡尔曼滤波器，不能与 BatchEstimator 一起使用。

**另请参阅**：ExtendedKalmanFilter、Spacecraft Ballistic/Mass Properties

## 字段

| 字段 | 描述 |
|------|------|
| **HalfLife** | 估计参数值和 sigma（不确定度）传播的半衰期（秒）。模型过程噪声由稳态 sigma 和半衰期导出。更多细节见下文备注。<br>数据类型：Real > 0；允许值：任意正实数；访问方式：Set；默认值：**7200**；单位：Seconds；接口：脚本 |
| **Model** | 随机过程模型的名称。<br>数据类型：String；允许值：FirstOrderGaussMarkov；访问方式：Set；默认值：**FirstOrderGaussMarkov**；单位：None；接口：脚本 |
| **SolveFor** | 随机过程所作用的参数名称。<br>数据类型：String；允许值：Cd、AtmosDensityScaleFactor；访问方式：Set；默认值：**None**；单位：None；接口：脚本 |
| **SteadyStateSigma** | 稳态参数不确定度。在缺少测量量的情况下，参数不确定度将回归到此值。模型过程噪声由稳态 sigma 和半衰期导出。更多细节见下文备注。<br>数据类型：Real；允许值：Real > 0；访问方式：Set；默认值：**0.1**；单位：None；接口：脚本 |
| **SteadyStateValue** | 稳态参数值。在缺少测量量的情况下，参数值将回归到此值。此值可能不同于参数的初始值——初始值取自 Spacecraft 对象上所选定求解参数的赋值。更多细节见下文备注。<br>数据类型：Real；允许值：Real >= 0；访问方式：Set；默认值：**1.0**；单位：None；接口：脚本 |

## 备注

> **注意**：不允许创建与内置求解参数同名的 `EstimatedParameter` 实例。内置求解参数名称列表请参见 Spacecraft Navigation 中的 `SolveFors`。

> **注意**：创建 `EstimatedParameter` 实例时，必须先指定 `Model` 参数，然后再指定该待估参数的任何其他参数。示例见下文。

航天器动态求解参数的选择在 `Spacecraft` 资源的 `SolveFors` 列表中指定。如 Spacecraft Navigation 中所述，有特定的关键字可用于在批处理估计器和滤波器中调用动态参数估计。在卡尔曼滤波运行的 `SolveFors` 列表中使用任何这些预定义参数名称，会将该参数建模为"随机常数"（random constant）。在随机常数模型中，估计参数及其不确定度（sigma）在滤波器时间更新期间都保持在其最后估计值不变。随机常数模型在参数估计传播期间不添加任何过程噪声，长期使用此模型会在滤波器中引发问题。

若要改为将参数建模为一阶高斯-马尔可夫过程，用户应为所需的动态求解参数配置一个 `EstimatedParameter` 实例，并将该实例指定到 `Spacecraft` 的 `SolveFors` 列表中，而不是使用预定义参数名称。详见下文示例一节。

以冷启动模式运行滤波器时，所选待估参数的标称（先验）值和不确定度为 Spacecraft 对象上指定的值。例如，若选择 `EstimatedParameter.SolveFor = 'Cd'`，则 Cd 的初始值为 `Spacecraft.Cd` 参数上指定的值，Cd 的初始不确定度在 `Spacecraft.CdSigma` 参数上指定。随后该参数按照一阶高斯-马尔可夫随机过程随时间向前传播。以热启动模式运行滤波器时（使用滤波器 `InputWarmStartFile`），初始参数值和协方差从热启动文件中的指定记录获取。

## 一阶高斯-马尔可夫建模

参数过程噪声的方差由用户指定的 `SteadyStateSigma` 和 `HalfLife` 导出。高斯-马尔可夫过程噪声的方差 σ_u^2 与 `EstimatedParameter` 的 `SteadyStateSigma` 之间的关系由下式给出：

> [图：σ_u^2 = 2·SteadyStateSigma^2 / τ（稳态 sigma 与过程噪声方差的关系式）]

其中 *τ* 与 `EstimatedParameter` 的 `HalfLife` 之间的关系为：

> [图：τ = HalfLife / ln(2)（半衰期与时间常数的关系式）]

一阶高斯-马尔可夫 `Cd` 和 `AtmosDensityScaleFactor` 参数的过程噪声矩阵在参考文献 1 的第 3.2.3.4 节中给出。GMAT 中实现的结果为如下定义的 7x7 矩阵 **S**：

> [图：7x7 过程噪声矩阵 S，由阻力加速度外积项 dd' 与 gamma 标量构成]

向量 **d** 为阻力加速度，由下式给出。在 **S** 的表达式中，**dd'** 项是由 **d** 向量与自身取外积形成的 3x3 子矩阵。

> [图：阻力加速度向量 d 的定义式]

**S** 中的 gamma 标量如下所示，其中 **Δt** 为过程噪声 `UpdateTimeStep`（在 ProcessNoise 资源实例上指定），*τ* 为上述高斯-马尔可夫时间常数。

> [图：gamma 标量定义式（含 Δt 与 τ 的指数项）]

当 **Δt/τ** 很小时（高斯-马尔可夫时间常数远大于过程噪声时间步长或测量间隔），gamma 标量中的指数项可能产生不准确的结果。对于 **Δt/τ** < 0.01 的情况，GMAT 用等效的三项泰勒级数展开替换上述 gamma 标量。

## 示例

此示例说明如何将航天器阻力系数的估计配置为一阶高斯-马尔可夫过程。

```
%
%   Configure estimation of spacecraft coefficient of drag (Cd) 
%   as a first-order Gauss-Markov process.
%

Create EstimatedParameter FogmCd
 
FogmCd.Model            = 'FirstOrderGaussMarkov'; % Must be assigned first, before any other options
FogmCd.SolveFor         = 'Cd'
FogmCd.SteadyStateSigma = 0.1
FogmCd.HalfLife         = 7200

%
%   Use the configured instance of FogmCd in the spacecraft
%   SolveFors list, instead of the built-in 'Cd'
%

Create Spacecraft EstSat;

EstSat.DateFormat        = UTCGregorian;
EstSat.Epoch             = '10 Jun 2010 00:00:00.000'
EstSat.CoordinateSystem  = EarthMJ2000Eq
EstSat.DisplayStateType  = Cartesian
EstSat.X                 = 576.8
EstSat.Y                 = -5701.1
EstSat.Z                 = -4170.5
EstSat.VX                = -1.7645
EstSat.VY                = 4.1813
EstSat.VZ                = -5.9658
EstSat.DryMass           = 10
EstSat.Cd                = 1.75
EstSat.CdSigma           = 0.1
EstSat.Cr                = 1.8
EstSat.DragArea          = 100
EstSat.SRPArea           = 100
EstSat.Id                = 'LEOSat'
EstSat.AddHardware       = {GpsReceiver, GpsAntenna}
EstSat.SolveFors         = {CartesianState, FogmCd}
EstSat.ProcessNoiseModel = SNC
```

**中文说明**：创建 EstimatedParameter 实例 FogmCd（注意 Model 必须最先赋值），求解参数为 Cd，稳态 sigma 为 0.1，半衰期 7200 秒。然后在航天器 EstSat 的 SolveFors 列表中使用 {CartesianState, FogmCd}——即用配置好的 FogmCd 实例代替内置的 'Cd' 关键字，使 Cd 按一阶高斯-马尔可夫过程估计；同时指定过程噪声模型 SNC。

## 参考文献

1. Carpenter, J. R., & D'Souza, C. N. (Eds.). (2025). *Navigation Filter Best Practices Second Edition* (NASA/TP–2018–219822/Revision). NASA Engineering and Safety Center.（《导航滤波器最佳实践（第二版）》，NASA 工程与安全中心）
