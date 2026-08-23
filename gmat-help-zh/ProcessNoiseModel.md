# 过程噪声模型（ProcessNoiseModel）

> 译自 GMAT R2026a 帮助文档 ProcessNoiseModel.html

**ProcessNoiseModel** —— 在使用 ExtendedKalmanFilter 估计器时，用于指定估计所用的过程噪声。

## 描述

`ProcessNoiseModel` 在 `Spacecraft` 实例的 `ProcessNoiseModel` 字段上指定，使 `ExtendedKalmanFilter` 能够考虑力建模中的一般性误差。此外，在使用 **Propagate** 命令传播协方差时，也用它包含噪声计算。

**另请参阅**：ExtendedKalmanFilter、Spacecraft Navigation

## 字段

| 字段 | 描述 |
|------|------|
| **AccelNoiseSigma** | 三轴过程噪声 sigma。假定高斯噪声过程沿各轴的方差平方根。<br>数据类型：Array；允许值：Real > 0；访问方式：set；默认值：**[1.0e-8 1.0e-8 1.0e-8]**；单位：取决于过程噪声模型类型，见下文备注；接口：脚本 |
| **CoordinateSystem** | 过程噪声加速度 sigma 向量的参考坐标系。<br>数据类型：String；允许值：任何内置或用户定义的 `CoordinateSystem` 资源名称；访问方式：set；默认值：**EarthMJ2000Eq**；单位：N/A；接口：脚本 |
| **Type** | 过程噪声建模类型。更多细节见下文备注。<br>数据类型：枚举；允许值：`StateNoiseCompensation`；访问方式：set；默认值：**StateNoiseCompensation**；单位：N/A；接口：脚本 |
| **UpdateTimeStep** | 更新过程噪声并传播协方差的时间步长。若设为 0，则在每个积分步进行更新。在 **Propagate** 命令中使用多个模型进行协方差传播时，此参数在所有模型上必须一致。更多细节见下文备注。<br>数据类型：Real；允许值：Real > 0；访问方式：set；默认值：**0**；单位：Seconds；接口：脚本 |

## 备注

### 状态噪声补偿（State Noise Compensation）

`StateNoiseCompensation` 过程噪声类型实现了 Tapley、Schutz 和 Born 所著《Statistical Orbit Determination》（《统计轨道确定》）第 4.9 节和附录 F 中描述的过程噪声算法。过程噪声被假定为施加在总确定性加速度上的加性高斯噪声过程。对于此方案，用户在所选参考系中提供以下矩阵的对角元素。

> [图：Q 矩阵——由 q1、q2、q3 构成的 3x3 对角过程噪声谱密度矩阵]

其中 *q1*、*q2*、*q3* 是所选 `CoordinateSystem` 中指定的 `AccelNoiseSigma` 各元素的平方。过程噪声 **S** 则由下式给出：

> [图：S 矩阵——由 Q 与 Δt 的各阶项构成的 6x6（或含增广状态的）过程噪声矩阵]

其中 **Δt** 取自由输入测量时刻与所选 `ProcessNoiseModel` 的 `UpdateTimeStep` 共同构成的时间网格。在使用 **Propagate** 命令进行协方差传播的场合，**Δt** 为传播起点与终点之间各积分步与 UpdateTimeStep 的并集。**Q̃** 是变换到积分坐标系中的 **Q** 矩阵。在滤波和预测期间，每次时间更新和测量更新都按此公式添加过程噪声。

确定 *q1*、*q2*、*q3* 的合适取值通常需要通过试错或参数化分析进行实验。参考文献 1 和 2 指出，对于以沿迹误差为主的近圆轨道情形，这种调参的合适起点可由下式导出：

> [图：q_AT = (σ_AT · π / (2·T))^2 之类的调参公式]

其中 σ_AT 为每个轨道周期的沿迹误差（或许由经验确定），*T* 为轨道周期（秒）。注意，输入 `AccelNoiseSigma` 分量时指定的是 *q_AT* 的平方根。对于状态噪声补偿，`AccelNoiseSigma` 的单位为 km/second^(3/2)。

## 示例

此示例展示如何创建并指定 `ProcessNoiseModel`。

```
%   Create a ProcessNoiseModel
 
Create ProcessNoiseModel SNC;

SNC.Type             = StateNoiseCompensation;
SNC.CoordinateSystem = EarthMJ2000Eq;
SNC.AccelNoiseSigma  = [1e-8 1e-8 1e-8];
SNC.UpdateTimeStep   = 120.
 
%   Assign it to a Spacecraft
 
Create Spacecraft EstSat;

EstSat.ProcessNoiseModel = SNC;
```

**中文说明**：创建过程噪声模型 SNC，类型为状态噪声补偿，参考坐标系为 EarthMJ2000Eq，三轴加速度噪声 sigma 均为 1e-8 km/s^(3/2)，每 120 秒更新一次过程噪声；然后将其指定给航天器 EstSat。

## 参考文献

1. Carpenter, Russell and Chris D'Souza. *Navigation Filter Best Practices*. Technical Report TP-2018-219822, NASA, April 2018.（NASA 技术报告《导航滤波器最佳实践》）
2. Geller, David. *Orbital Rendezvous: When is Autonomy Required?*. Journal of Guidance, Control, and Dynamics, Vol. 30, No.4. July-August 2007.（《轨道交会：何时需要自主？》，《制导、控制与动力学杂志》）
