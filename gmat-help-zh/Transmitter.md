# 发射机（Transmitter）
> 译自 GMAT R2026a 帮助文档 Transmitter.html

**Transmitter** —— 定义挂接到 GroundStation 或 Spacecraft 资源、用于发射射频（RF）信号的电子设备硬件。

## 描述

地面站需要 Transmitter 来向用户航天器以及 TDRS 等导航航天器发射射频信号。Transmitter 在 GroundStation 实例的 AddHardware 列表中指定。Transmitter 也可以指定在 TDRS 用户航天器上，用于指定或估计用户到 TDRS 的发射频率属性。

另请参阅：GroundStation、Antenna

## 字段

| 字段 | 描述 |
|------|------|
| **EpochFormat** | 此字段允许您设置为 ReferenceEpoch 输入的历元类型。此字段不能在任务序列中修改。<br>数据类型：枚举；允许值：以下任一历元格式：UTCGregorian、UTCModJulian、TAIGregorian、TAIModJulian、TTGregorian、TTModJulian、A1Gregorian、A1ModJulian；访问：set；默认值：UTCGregorian；单位：N/A；接口：GUI、脚本 |
| **Frequency** | 发射频率。<br>数据类型：Real；允许值：Real ≥ 0；访问：set；默认值：2000；单位：MHz；接口：脚本 |
| **FrequencyBand** | 发射频段。此参数仅用于测量仿真。估计时（如适用）的频段在 GMD 跟踪数据文件中指定。<br>仿真 DSN 数据类型时忽略此参数。对于 DSN 数据的仿真，频段根据 Frequency 参数按照 DSN 频率范围规范推断。如果设为 None，GMAT 将尝试根据发射机 Frequency 推断频段。<br>数据类型：String；允许值：'None'、'C'、'S'、'X'、'K'；访问：set；默认值：None；单位：NA；接口：脚本 |
| **FrequencyBias** | 发射机频率偏差模型的系数。FrequencyBias 列表中的系数指定多项式频率偏差 f_bias(t)，使得 f_bias(t) = C0 + C1*(t - t0) + C2*(t - t0)^2 + …，其中 t0 为 ReferenceEpoch，t 为测量或积分时间。列表中系数的个数决定多项式的阶数。<br>瞬时发射机频率由 f(t) = F + f_bias(t) 给出，其中 F 为 Transmitter Frequency 参数的值。<br>数据类型：实数数组；允许值：任意实数；访问：set；默认值：[ 0.0 ]；单位：Hz、Hz/sec、Hz/sec^2、…；接口：脚本 |
| **PrimaryAntenna** | GroundStation 资源用于发射信号的 Antenna 资源。<br>数据类型：Antenna 对象；允许值：任何 Antenna 对象；访问：set；默认值：None；单位：N/A；接口：脚本 |
| **ReferenceEpoch** | FrequencyBias 多项式的锚定历元。FrequencyBias 列表中的系数指定多项式频率偏差 f_bias(t)，使得 f_bias(t) = C0 + C1*(t - t0) + C2*(t - t0)^2 + …，其中 t0 为 ReferenceEpoch，t 为测量或积分时间。默认值 FromSpacecraft 将 ReferenceEpoch 赋值为航天器初始历元。<br>数据类型：String；允许值：用户定义的历元或默认值；访问：set；默认值：FromSpacecraft；单位：N/A；接口：脚本 |
| **SolveFors** | 待估计参数的列表。如果指定估计 FrequencyBias，GMAT 将按 FrequencyBias 数组的大小所决定的阶数估计频率偏差系数。<br>数据类型：String；允许值：{} 或 FrequencyBias；访问：set；默认值：{}；单位：N/A；接口：脚本 |

## 备注

### 发射机频率在仿真和估计中的使用

发射机可以挂接到 GroundStation 或 Spacecraft 资源。如 RunSimulator 帮助中所述，在不使用斜坡表（ramp table）的情况下，发射频率直接用于计算 DSN 测距和多普勒测量。对于仿真和估计，如果在相关 TrackingFileSet 上指定了斜坡表，则使用斜坡表中指定的频率剖面，并忽略 Transmitter 的 Frequency 和 FrequencyBand。

对于 TDRS 测量的仿真，可以将 Transmitter 挂接到 TDRS 用户航天器，以指定用于测量仿真的用户到 TDRS 发射频率。如果 TDRS 用户未挂接 Transmitter，则使用 2000 MHz 的默认频率。估计时，用户到 TDRS 的发射频率从 GMD 跟踪数据文件获取，并忽略 Transmitter 的 Frequency 和 FrequencyBand。

## 示例

创建并配置一个 Transmitter 对象。

```
Create Antenna DSNAntenna;
Create Transmitter Transmitter1;

Transmitter1.PrimaryAntenna = DSNAntenna;
Transmitter1.Frequency = 7186.3; 

Create GroundStation DSN
DSN.AddHardware = {Transmitter1};

BeginMissionSequence;
```

说明：本示例创建天线 DSNAntenna 和发射机 Transmitter1，将天线设为发射机主天线并将发射频率设为 7186.3 MHz，然后创建地面站 DSN 并将发射机挂接到地面站。

创建并配置一个用于估计线性频率偏差的 Transmitter。FrequencyBias 数组有两个元素，表示频率偏差多项式只有常数项 C0 和线性项 C1。在此情况下（估计），频率的标称值从 GMD 文件获取（此处未显示）。对于仿真，您应使用 Frequency 参数在 Transmitter 上指定标称频率。

```
Create Spacecraft Sat
Create Antenna HGA;
Create Transmitter Transmitter1;

Transmitter1.PrimaryAntenna = HGA
Transmitter1.FrequencyBand  = 'S'
Transmitter1.EpochFormat    = 'UTCGregorian'
Transmitter1.ReferenceEpoch = '15 Nov 2018 12:00:00.000'
Transmitter1.FrequencyBias  = [0.0, 0.0] 
Transmitter1.SolveFors      = {FrequencyBias}

Sat.AddHardware = {Transmitter1, HGA}

BeginMissionSequence;
```

说明：本示例在航天器 Sat 上挂接高增益天线 HGA 和发射机 Transmitter1；发射机设为 S 频段，频率偏差多项式参考历元为 2018-11-15 12:00:00 UTC，偏差系数初值为 [0.0, 0.0]（常数项和线性项），并将 FrequencyBias 列为待估参数。
