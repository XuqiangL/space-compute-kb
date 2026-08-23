# 接收机（Receiver）
> 译自 GMAT R2026a 帮助文档 Receiver.html

**Receiver** —— 接收射频（RF）信号的硬件。

## 描述

GroundStation 或 Spacecraft 可以配置 Receiver。Receiver 在 GroundStation 或 Spacecraft 实例的 AddHardware 列表中指定。

例如，GroundStation 资源需要接收来自被跟踪航天器的射频信号。接收机资源还用作 GPS_PosVec 和星间（航天器间）测量误差模型的宿主对象。当使用 GPS_PosVec 数据进行估计或仿真时，应在 Receiver 对象上指定一个指定 GPS_PosVec 测量类型的 ErrorModel 实例，并将该接收机指定给相关联的 Spacecraft 对象。对于星间跟踪的仿真或估计，"跟踪"航天器必须具有已指定并配置了适当 ErrorModel 的 Receiver。

另请参阅：GroundStation、Antenna

## 字段

| 字段 | 描述 |
|------|------|
| **ErrorModels** | 用户定义的 ErrorModel 对象列表，描述此接收机使用的测量误差模型。接收机对象当前支持的误差模型类型为 GPS_PosVec、Range 和 RangeRate。当使用 GPS_PosVec 数据进行仿真或估计时，需要此参数来描述接收机的测量误差模型。星间跟踪的仿真和估计（目前针对 Range 和 RangeRate 测量类型实现）也需要此参数。<br>数据类型：StringList；允许值：使用 GPS_PosVec、Range 或 RangeRate 观测类型的 ErrorModel 实例；访问：set；默认值：None；单位：N/A；接口：脚本 |
| **Id** | 此接收机的整数标识号。它应与 GMD 文件中为 GPS_PosVec 数据指定的接收机 ID 相匹配。仅在使用 GPS_PosVec 数据进行仿真或估计时才需要此参数。<br>数据类型：Integer；允许值：Integer ≥ 0；访问：set；默认值：800；单位：N/A；接口：脚本 |
| **PrimaryAntenna** | Receiver 或 Spacecraft 资源用于接收信号的 Antenna 资源。<br>数据类型：Antenna 对象；允许值：任何有效的 Antenna 对象；访问：set；默认值：None；单位：N/A；接口：脚本 |

## 示例

创建并配置一个 Receiver 对象，并将其挂接到 GroundStation。

```
Create Antenna DSNReceiverAntenna;
Create Receiver Receiver1;

Receiver1.PrimaryAntenna = DSNReceiverAntenna;

Create GroundStation DSN
DSN.AddHardware = {Receiver1};
BeginMissionSequence;
```

说明：本示例创建天线 DSNReceiverAntenna 和接收机 Receiver1，将该天线设为接收机的主天线，然后创建地面站 DSN 并将接收机挂接到地面站。
