# 推力段（ThrustSegment）

> 译自 GMAT R2026a 帮助文档 ThrustSegment.html

**ThrustSegment** —— 一个或多个推力段定义推力历史文件中的数据如何使用。

## 描述

`ThrustSegment` 资源用于定义推力历史文件中封装在 "BeginThrust {ThrustSegment 对象名}" 和 "EndThrust {ThrustSegment 对象名}" 关键字之间的一部分数据如何使用。

另请参阅：ThrustSegment（推力段）、BeginFileThrust（开始文件推力）、EndFileThrust（结束文件推力）。

## 字段

| 字段 | 描述 |
|------|------|
| **ApplyThrustScaleToMassFlow** | 标志位，指定推力/加速度的 `ThrustScaleFactor`（推力比例因子）是否也应用于质量流率。<br>• 数据类型：Boolean<br>• 允许值：True、False<br>• 访问权限：set<br>• 默认值：False<br>• 单位：N/A<br>• 接口：脚本 |
| **MassFlowScaleFactor** | 应用于推力历史文件中质量流率数据的乘性比例因子。仅在推力历史文件中建模质量流率时使用。<br>• 数据类型：Real<br>• 允许值：任何实数<br>• 访问权限：set<br>• 默认值：1.0<br>• 单位：N/A<br>• 接口：脚本 |
| **MassSource** | 在对推力段描述的有限推力机动建模时，存放所用推进剂的燃料箱。GMAT 将按照用户选择的质量流建模选项扣减该燃料箱中的燃料质量。如果指定了多个燃料箱，仅使用第一个。<br>• 数据类型：ChemicalTank<br>• 允许值：{} 或任何用户定义的 `ChemicalTank` 资源<br>• 访问权限：set<br>• 默认值：{}<br>• 单位：N/A<br>• 接口：脚本 |
| **SolveFors** | 要估计的参数列表。<br>• 数据类型：String<br>• 允许值：{} 或 ThrustScaleFactor、ThrustAngle1 和/或 ThrustAngle2 的任意组合<br>• 访问权限：set<br>• 默认值：{}<br>• 单位：N/A<br>• 接口：脚本 |
| **ThrustAngle1** | 推力或加速度矢量第一个角度修正的系数。更多细节见下面的"备注"。<br>• 数据类型：实数数组<br>• 允许值：任何实数<br>• 访问权限：set<br>• 默认值：[ 0.0 ]<br>• 单位：deg、deg/sec、deg/sec^2……（见"备注"部分）<br>• 接口：脚本 |
| **ThrustAngle1Sigma** | `ThrustAngle1` 的标准差。仅当 `ThrustAngle1` 被定义为求解参数（使用上面定义的 `SolveFors` 参数）时使用。更多细节见下面的"备注"。<br>• 数据类型：实数数组<br>• 允许值：正实数<br>• 访问权限：set<br>• 默认值：[ 1e70 ]<br>• 单位：deg、deg/sec、deg/sec^2……（见"备注"部分）<br>• 接口：脚本 |
| **ThrustAngle2** | 推力或加速度矢量第二个角度修正的系数。更多细节见下面的"备注"。<br>• 数据类型：实数数组<br>• 允许值：任何实数<br>• 访问权限：set<br>• 默认值：[ 0.0 ]<br>• 单位：deg、deg/sec、deg/sec^2……（见"备注"部分）<br>• 接口：脚本 |
| **ThrustAngle2Sigma** | `ThrustAngle2` 的标准差。仅当 `ThrustAngle2` 被定义为求解参数（使用上面定义的 `SolveFors` 参数）时使用。更多细节见下面的"备注"。<br>• 数据类型：实数数组<br>• 允许值：正实数<br>• 访问权限：set<br>• 默认值：[ 1e70 ]<br>• 单位：deg、deg/sec、deg/sec^2……（见"备注"部分）<br>• 接口：脚本 |
| **ThrustAngleConstraintVector** | 该矢量与来自推力历史文件（THF）的推力方向矢量一起，用于定义推力角度旋转的坐标系。更多细节见下面的"备注"。<br>• 数据类型：实数数组<br>• 允许值：实数数组（长度为三）<br>• 访问权限：set<br>• 默认值：[ 0 0 1 ]<br>• 单位：N/A<br>• 接口：脚本 |
| **ThrustScaleFactor** | 应用于推力历史文件中推力/加速度数据的乘性比例因子。<br>• 数据类型：Real<br>• 允许值：任何实数<br>• 访问权限：set<br>• 默认值：1.0<br>• 单位：N/A<br>• 接口：脚本 |
| **ThrustScaleFactorSigma** | `ThrustScaleFactor` 的标准差。仅当 `ThrustScaleFactor` 被定义为求解参数（使用上面定义的 `SolveFors` 参数）时使用。<br>• 数据类型：Real<br>• 允许值：正实数<br>• 访问权限：set<br>• 默认值：1e70<br>• 单位：N/A<br>• 接口：脚本 |
## 备注

### 推力角度修正概述

ThrustSegment 支持小角度修正，用于补偿推力历史文件中定义的推力或加速度矢量的失准。该修正通过绕某坐标系的两次角度旋转来施加。每个角度由时变多项式定义：θ = a₀ + a₁t + a₂t² + … + aₙtⁿ，其系数由用户通过 `ThrustAngle1` 和 `ThrustAngle2` 字段提供，时间 t 以 `ThrustSegment` 初始历元之后的秒数计量。多项式的阶数由数组 `ThrustAngle1` 和 `ThrustAngle2` 的长度决定，用户可以自由选择该数组的长度。

角度修正作为绕两个正交轴的两次相继旋转施加到推力或加速度矢量上。所有矢量都在推力历史文件中 `ThrustSegment` 所指定的坐标系中定义。第一次旋转绕由"与推力或加速度矢量对齐的矢量"和 `ThrustAngleConstraintVector` 所指定矢量的叉积形成的轴进行。第二次旋转轴与"第一次旋转轴矢量"和"第一次角度旋转后推力矢量所指方向"的叉积所定义的矢量对齐。例如，如果推力历史文件指定沿航天器体坐标系 +X 轴的推力，选择约束矢量 [ 0 0 1 ]（也在体坐标系中）将把 `ThrustAngle1` 映射为绕体 -Y 轴的旋转（相当于俯仰角），而 `ThrustAngle2` 将映射为绕体 +Z 轴的旋转（相当于偏航角）。

#### 求解推力角度

求解推力角度时，只要 `ThrustAngle1` 或 `ThrustAngle2` 中指定的多项式系数列在 `SolveFors` 字段中，GMAT 就会求解每个系数。`ThrustAngle1Sigma` 和 `ThrustAngle2Sigma` 字段包含相应角度字段中每个系数的先验标准差数组。使用 `BatchEstimator`（批处理估计器）时，用户还必须将 `BatchEstimator` 的 `UseInitialCovariance` 参数设置为 `True`，推力角度标准差才会被应用。用户可以通过查看批处理估计器输出报告文件中的 Estimation Initial Conditions（估计初始条件）报告来确认标准差已被应用。所指定的推力角度标准差总是由 `ExtendedKalmanFilter`（扩展卡尔曼滤波器）自动使用。

> **注意**：相对于角度系数的偏导数是高度非线性的。求解推力角度时，需要注意多项式的阶数、推力角度的不确定度以及所选的先验值。如果使用的多项式阶数过高、推力段期间观测数量不足，或先验角度与真实失准角相差太远，收敛可能变得困难。推力角度标准差使用过大的值会给估计器过多的自由度来收敛系数值。通过使用 ThrustAngle 标准差（并将 `BatchEstimator` 的 `UseInitialCovariance` 设置为 `True`）来约束估计，可以通过限制估计器的自由度来帮助收敛，但这通常要求用户对推力角度及其系数有良好的先验了解。此外，角度的周期性（360 度的角度等价于 0 度的角度）会进一步加剧这些影响。

#### 推力角度和推力角度标准差的单位

由于 `ThrustAngle1`、`ThrustAngle2`、`ThrustAngle1Sigma` 和 `ThrustAngle2Sigma` 的值是多项式的系数，因此单位取决于它们在数组中的位置。每个数组的第一个元素以度（degrees）为单位，下一个元素以度/秒（degrees/seconds）为单位。每增加一个元素，分母中就增加一个"秒"。

## 示例

创建一个 `ThrustSegment`，其中值为 2.0 的推力比例因子也将应用于质量流率。

```
Create Spacecraft aSat
Create ChemicalTank aTank
aSat.Tanks = {aTank}

Create ThrustSegment aThrustSegment;  
aThrustSegment.ThrustScaleFactor = 2.0;
aThrustSegment.ApplyThrustScaleToMassFlow = True; 
aThrustSegment.MassFlowScaleFactor = 1.5;
aThrustSegment.MassSource={aTank};

BeginMissionSequence
```

上述脚本：创建航天器 aSat、燃料箱 aTank 并挂载；创建推力段 aThrustSegment，设置推力比例因子 2.0、推力比例同时作用于质量流（True）、质量流比例因子 1.5、质量来源为 aTank。

如果你使用上面的脚本片段创建完整脚本，则需要创建一个推力/加速度和质量流率输入文件。假设文件中给定时刻的质量流率设置为 1 kg/s，那么实际施加到航天器的质量流率是多少？在回答这个问题之前，我们需要考虑 `ThrustScaleFactor`、`MassFlowScaleFactor` 和 `ApplyThrustScaleToMassFlow` 的值。在所有情况下，`MassFlowScaleFactor` 都会应用于文件中给出的质量流率值。在本例中，由于 `ApplyThrustScaleToMassFlow` 设置为 `True`，`ThrustScaleFactor` 也将应用于文件中给出的质量流率值。因此，回答我们的问题：在本例中，实际施加到航天器的质量流率为 `MassFlowScaleFactor` × `ThrustScaleFactor` × 1 kg/s，等于 3 kg/s。在上面的示例中，实际施加到航天器的推力/加速度剖面为输入文件中给出的推力/加速度乘以（`ThrustScaleFactor` = 2.0）。

关于如何使用 `ThrustHistoryFile` 和 `ThrustSegment` 资源向航天器施加推力/加速度和质量流率剖面的完整示例，请参阅 BeginFileThrust（开始文件推力）帮助中的第一个示例。
