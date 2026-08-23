# 太阳电源系统（SolarPowerSystem）
> 译自 GMAT R2026a 帮助文档 SolarPowerSystem.html

**SolarPowerSystem** —— 太阳电源系统模型

## 描述

SolarPowerSystem 对太阳电源系统建模，包括发电功率随时间和日距的变化，并包含天体阴影建模。该模型允许您配置太阳翼（solar array）产生的功率以及航天器母线（bus）所需的功率。

有关电推进建模所需全部资源的完整配置说明，请参阅教程"第 12 章 电推进（Electric Propulsion）"。

另请参阅：ElectricTank、ElectricThruster、NuclearPowerSystem

## 字段

| 字段 | 描述 |
|------|------|
| **AnnualDecayRate** | 电源系统的年衰减率。<br>数据类型：Real；允许值：0 ≤ Real ≤ 100；访问：set；默认值：5；单位：Percent/Year；接口：GUI、脚本 |
| **BusCoeff1** | 航天器母线所需功率的系数。<br>数据类型：Real；允许值：Real；访问：set；默认值：0.3；单位：kW；接口：GUI、脚本 |
| **BusCoeff2** | 航天器母线所需功率的系数。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：kW*AU；接口：GUI、脚本 |
| **BusCoeff3** | 航天器母线所需功率的系数。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：kW*AU²；接口：GUI、脚本 |
| **EpochFormat** | PowerInitialEpoch 字段的历元格式。<br>数据类型：String；允许值：有效的历元格式；访问：set；默认值：UTCGregorian；单位：N/A；接口：GUI、脚本 |
| **InitialEpoch** | 系统的初始历元，用于定义电源系统的已运行寿命。<br>数据类型：String；允许值：与 PowerInitialEpochFormat 一致的有效 GMAT 历元；访问：set；默认值：01 Jan 2000 11:59:27.966；单位：N/A；接口：GUI、脚本 |
| **InitialMaxPower** | 在 PowerInitialEpoch 时产生的最大功率。<br>数据类型：Real；允许值：Real ≥ 0；访问：set；默认值：1.2；单位：kW；接口：GUI、脚本 |
| **Margin** | 扣除母线功率后剩余功率与推进系统所用功率之间所需的裕度。<br>数据类型：Real；允许值：0 ≤ Real ≤ 100；访问：set；默认值：5；单位：Percent；接口：GUI、脚本 |
| **ShadowBodies** | 用于阴影计算的天体列表。同一天体不能添加多次。<br>数据类型：String List；允许值：天体列表；访问：set；默认值：Earth；单位：N/A；接口：GUI、脚本 |
| **ShadowModel** | 太阳电源系统模型中用于阴影计算的模型。<br>数据类型：String；允许值：None、DualCone；访问：set；默认值：DualCone；单位：N/A；接口：GUI、脚本 |
| **SolarCoeff1** | 太阳电源系统发电功率的系数。<br>数据类型：Real；允许值：Real；访问：set；默认值：1.32077；单位：见"备注"；接口：GUI、脚本 |
| **SolarCoeff2** | 太阳电源系统发电功率的系数。<br>数据类型：Real；允许值：Real；访问：set；默认值：-0.10848；单位：见"备注"；接口：GUI、脚本 |
| **SolarCoeff3** | 太阳电源系统发电功率的系数。<br>数据类型：Real；允许值：Real；访问：set；默认值：-0.11665；单位：见"备注"；接口：GUI、脚本 |
| **SolarCoeff4** | 太阳电源系统发电功率的系数。<br>数据类型：Real；允许值：Real；访问：set；默认值：0.10843；单位：见"备注"；接口：GUI、脚本 |
| **SolarCoeff5** | 太阳电源系统发电功率的系数。<br>数据类型：Real；允许值：Real；访问：set；默认值：-0.01279；单位：见"备注"；接口：GUI、脚本 |

## GUI

SolarPowerSystem 的 GUI 如下所示。

> [图：SolarPowerSystem 的 GUI 界面]

## 备注

### 基础功率的计算

SolarPowerSystem 将功率衰减建模为时间的函数。您必须提供电源系统初始历元、该历元时的发电功率以及年功率衰减率。此外，AnnualDecayRate 字段按年度建模功率衰减。基础功率按下式计算：

> [图：基础功率计算公式]

其中 "tau" 为功率 AnnualDecayRate，P_0 为 InitialMaxPower，"delta t" 为仿真历元与 InitialEpoch 之间经过的时间。

### 母线功率的计算

航天器母线对除推进系统外所有分系统所需的功率按下式计算：

> [图：母线功率计算公式]

其中 A_Bus、B_Bus 和 C_Bus 分别为 BusCoeff1、BusCoeff2 和 BusCoeff3，r 为到太阳的距离（单位：AU）。

### 可用于推进的功率的计算

太阳电源模型根据以日距为自变量的多项式函数对基础功率进行缩放。总功率按下式计算：

> [图：总功率计算公式]

其中 P_Sun 为日照百分比（全日照为 1.0，无日照为 0.0），r 为到太阳的距离（单位：AU），C_1 为 SolarCoeff1，依此类推。最终可用于电推进的推力功率按下式计算：

> [图：可用推力功率计算公式]

其中 "delta M" 为功率 Margin。

### 阴影建模与不连续性

注意，对太阳电源系统进行阴影建模时，当可用于推进的功率小于推力器的最小可用功率设置时，力模型可能出现不连续。当航天器从半影进入本影、可用于推力的功率变为零时，推力功率会使推力加速度不连续地终止，从而在使用自适应步长积分器时引发问题。在这种情况下，有几种选择。您可以通过将 ErrorControl 设为 None，配置任意积分器使用固定步长积分；或者配置积分器在出现不良步长（此处为小的不连续）时继续传播。更多信息请参阅 Propagator 参考资料。

## 示例

创建一个 SolarPowerSystem 并将其挂接到 Spacecraft。

```
%  Create the Solar Power System
Create SolarPowerSystem SolarPowerSystem1

%  Create a spacecraft an attach the Solar Power System
Create Spacecraft DefaultSC
DefaultSC.PowerSystem = SolarPowerSystem1

BeginMissionSequence
```

说明：本示例创建太阳电源系统 SolarPowerSystem1，创建航天器 DefaultSC，并将该电源系统挂接到航天器。

有关电推进建模所需全部资源的完整配置说明，请参阅教程"第 12 章 电推进（Electric Propulsion）"。
