# 核电源系统（NuclearPowerSystem）
> 译自 GMAT R2026a 帮助文档 NuclearPowerSystem.html

**NuclearPowerSystem** —— 核电源系统

## 描述

NuclearPowerSystem 对核电源系统建模，包括发电功率随时间和日距的变化。

有关电推进建模所需全部资源的完整配置说明，请参阅教程"第 12 章 电推进（Electric Propulsion）"。

另请参阅：ElectricTank、ElectricThruster、SolarPowerSystem

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

## GUI

NuclearPowerSystem 的 GUI 如下所示。

> [图：NuclearPowerSystem 的 GUI 界面]

## 备注

### 基础功率的计算

NuclearPowerSystem 将功率衰减建模为时间的函数。您必须提供电源系统初始历元、该历元时的发电功率以及年功率衰减率。此外，AnnualDecayRate 字段按年度建模功率衰减。基础功率按下式计算：

> [图：基础功率计算公式]

其中 "tau" 为功率 AnnualDecayRate，P_0 为 InitialMaxPower，"delta t" 为仿真历元与 InitialEpoch 之间经过的时间。

### 母线功率的计算

航天器母线对除推进系统外所有分系统所需的功率按下式计算：

> [图：母线功率计算公式]

其中 A_Bus、B_Bus 和 C_Bus 分别为 BusCoeff1、BusCoeff2 和 BusCoeff3，r 为到太阳的距离（单位：AU）。

### 可用于推进的功率的计算

总功率按下式计算：

> [图：总功率计算公式]

最终可用于电推进的推力功率按下式计算：

> [图：可用推力功率计算公式]

其中 "delta M" 为功率 Margin。

## 示例

创建一个 NuclearPowerSystem 并将其挂接到 Spacecraft。

```
Create Spacecraft DefaultSC
DefaultSC.PowerSystem = NuclearPowerSystem1

Create NuclearPowerSystem NuclearPowerSystem1

BeginMissionSequence
```

说明：本示例创建航天器 DefaultSC 和核电源系统 NuclearPowerSystem1，并将该电源系统挂接到航天器。

有关电推进建模所需全部资源的完整配置说明，请参阅教程"第 12 章 电推进（Electric Propulsion）"。
