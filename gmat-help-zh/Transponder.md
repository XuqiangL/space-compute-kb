# 应答机（Transponder）
> 译自 GMAT R2026a 帮助文档 Transponder.html

**Transponder** —— 定义通常挂接到航天器、用于接收并自动转发入射信号的电子设备硬件。

## 描述

航天器 Transponder 模型是建模双向相干测距和多普勒数据类型所必需的。Transponder 对象包括对航天器应答机电子设备引起的转发延迟的建模。您还可以指定转发比（turn around ratio），这是一个乘性比率，描述转发信号的频率与接收频率的差异。入射和出射频率被设计为不同，以避免地面站发射到航天器的信号与航天器返回地面站的信号之间的射频干扰。

另请参阅：GroundStation、Antenna

## 字段

| 字段 | 描述 |
|------|------|
| **HardwareDelay** | 应答机接收时刻与发射时刻之间的应答机电子设备延迟。无论是否使用斜坡表，它在仿真和估计中都会应用。<br>数据类型：Real；允许值：Real ≥ 0；访问：set；默认值：0；单位：seconds；接口：脚本 |
| **PrimaryAntenna** | Transponder 资源使用的 Antenna 资源。<br>数据类型：Antenna 对象；允许值：任何有效的 Antenna 对象；访问：set；默认值：None；单位：N/A；接口：脚本 |
| **TurnAroundRatio** | 应答机转发比，在仿真和估计中都会使用。对于不使用输入斜坡表的 DSN 多普勒数据类型，改变应答机转发比会显著改变测量值。对于所有 DSN 数据类型，改变转发比会影响介质修正计算，这通常会导致测量值发生小的变化。更多细节请参阅 RunSimulator 和 RunEstimator 帮助。<br>数据类型：STRING_TYPE；允许值：形如 'a/b' 的字符串，其中 a 和 b 为实数；访问：set；默认值：'240/221'；单位：N/A；接口：脚本 |

## 备注

### 转发比影响介质修正计算

假设给定一个具有 n 个链路段（leg）的信号。为了计算给定链路段的介质（电离层）修正，我们需要知道该链路段的关联频率。转发比用于计算第 2 至第 n 段的频率。如果建模了介质修正，那么对于 DSN 测距和多普勒测量，Transponder 资源中设置的转发比的值都会影响测量值，因此仿真和估计过程都会受到影响。

### 与介质修正无关：Transponder 资源中设置的转发比如何影响 DSN 测量？

假设介质修正已关闭，因此可以忽略介质修正对 DSN 测量造成的（通常很小的）任何变化。我们作如下观察：

1. Transponder.TurnAroundRatio 的值对 DSN 测距测量没有影响。
2. 如果提供了斜坡表，则 Transponder.TurnAroundRatio 的值对 DSN 多普勒测量没有影响。在这种情况下，用于计算测量计算值的乘性转发比基于斜坡表中给出的上行频段（S 频段为 240/221，X 频段为 880/749）。
3. 如果未提供斜坡表，则 Transponder.TurnAroundRatio 的值对 DSN 多普勒测量有正比影响。例如，如果转发比加倍，则以 Hz 为单位的 DSN 多普勒测量值也加倍。

有关 Transponder.TurnAroundRatio 字段如何影响 DSN 测量的更多讨论，请参阅 RunSimulator 和 RunEstimator 帮助。

### DSN 多普勒数据的自定义转发比

如上所述，DSN 多普勒（TRK-2-34 类型 17）数据类型的观测值取决于应答机转发比。如 RunSimulator 和 RunEstimator 帮助中的表格所示，对于斜坡多普勒数据，GMAT 只允许使用标准的 S 频段（240/221）和 X 频段（880/749）转发比。对于不使用斜坡表的多普勒数据，设置 Transponder 转发比将正确建模 Doppler 数据。GMAT 目前无法支持斜坡多普勒数据的自定义转发比。

## 示例

```
% Create and configure a Transponder object

Create Spacecraft Sat1;
Create Antenna HGA;
Create Transponder Transponder1;

Transponder1.PrimaryAntenna  = HGA;
Transponder1.HardwareDelay   = 0.0;
Transponder1.TurnAroundRatio = '240/221';

Sat1.AddHardware = {HGA, Transponder1};
BeginMissionSequence;
```

说明：本示例创建航天器 Sat1、高增益天线 HGA 和应答机 Transponder1；应答机主天线设为 HGA，硬件延迟为 0 秒，转发比为 '240/221'（S 频段标准值）；最后将天线和应答机挂接到航天器。
