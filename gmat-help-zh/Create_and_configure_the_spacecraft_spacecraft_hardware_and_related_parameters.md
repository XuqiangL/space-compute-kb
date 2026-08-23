# 创建并配置航天器、航天器硬件及相关参数（Create_and_configure_the_spacecraft_spacecraft_hardware_and_related_parameters）

> 译自 GMAT R2026a 帮助文档 Create_and_configure_the_spacecraft_spacecraft_hardware_and_related_parameters.html

（本小节属于"第 16 章 仿真与估计航天器间跟踪"教程）

对于本教程，您需要打开 GMAT，并打开一个新的空脚本。要创建新脚本，点击 **New Script**。

## 创建仿真卫星，设置其历元和笛卡尔坐标

首先，我们创建用于仿真的新航天器 `SimSat` 和 `SimTrackSat`，并设置它们的历元和笛卡尔坐标。

```
%
%   Simulated Spacecraft
%

Create Spacecraft SimSat

SimSat.DateFormat            = UTCGregorian
SimSat.Epoch                 = '10 Jun 2010 00:00:00.000'
SimSat.CoordinateSystem      = EarthMJ2000Eq
SimSat.DisplayStateType      = Cartesian
SimSat.X                     =   576.86955
SimSat.Y                     = -5701.14276
SimSat.Z                     = -4170.59369
SimSat.VX                    = -1.76450794
SimSat.VY                    =  4.18128798
SimSat.VZ                    = -5.96578986
SimSat.Id                    = 'ObservedSat'

Create Spacecraft SimTrackSat

SimTrackSat.DateFormat       = UTCGregorian
SimTrackSat.Epoch            = '10 Jun 2010 00:00:00.000'
SimTrackSat.CoordinateSystem = EarthMJ2000Eq
SimTrackSat.DisplayStateType = Cartesian
SimTrackSat.X                = -36517.051189    
SimTrackSat.Y                = -21083.129334       
SimTrackSat.Z                = -0.000000      
SimTrackSat.VX               = -0.005964       
SimTrackSat.VY               = 0.010330       
SimTrackSat.VZ               = 0.267968
SimTrackSat.Id               = 'TrackSat'
```

**中文说明**：创建两艘仿真航天器——被观测星 SimSat（低轨，ID 为 'ObservedSat'）和跟踪星 SimTrackSat（高轨/地球同步附近，ID 为 'TrackSat'），历元均为 2010-06-10 00:00 UTCG，地心 J2000 坐标系。

注意，除了设置每艘航天器的坐标外，我们还为各自分配了 ID。这是将写入我们稍后讨论的 GMAT 测量数据（GMD）文件的标签。

## 创建估计卫星，设置其历元和笛卡尔坐标

接下来，我们创建用于估计的新航天器 `EstSat` 和 `EstTrackSat`，并设置它们的历元和笛卡尔坐标。

```
%
%   Estimator Spacecraft
%

Create Spacecraft EstSat

EstSat.DateFormat            = UTCGregorian
EstSat.Epoch                 = '10 Jun 2010 00:00:00.000'
EstSat.CoordinateSystem      = EarthMJ2000Eq
EstSat.DisplayStateType      = Cartesian
EstSat.X                     = 576.87
EstSat.Y                     = -5701.14
EstSat.Z                     = -4170.59
EstSat.VX                    = -1.764508
EstSat.VY                    = 4.181288
EstSat.VZ                    = -5.965790
EstSat.Id                    = 'ObservedSat'
EstSat.AddHardware           = {Transponder1, SpacecraftAntenna}
EstSat.SolveFors             = {CartesianState}

Create Spacecraft EstTrackSat

EstTrackSat.DateFormat       = UTCGregorian
EstTrackSat.Epoch            = '10 Jun 2010 00:00:00.000'
EstTrackSat.CoordinateSystem = EarthMJ2000Eq
EstTrackSat.DisplayStateType = Cartesian
EstTrackSat.X                = -36517.051189    
EstTrackSat.Y                = -21083.129334       
EstTrackSat.Z                = -0.000000      
EstTrackSat.VX               = -0.005964       
EstTrackSat.VY               = 0.010330       
EstTrackSat.VZ               = 0.267968
EstTrackSat.Id               = 'TrackSat'
```

**中文说明**：创建估计用航天器 EstSat 和 EstTrackSat。EstSat 的初始状态相对 SimSat 略有截断（作为先验估计），挂接应答机和天线，求解变量为笛卡尔状态；EstTrackSat 与 SimTrackSat 状态完全相同（假设跟踪星轨道已知）。

注意，在本例中我们假设 TrackSat 的位置已通过先前跟踪的估计或其他方式确定。因此 `SimTrackSat` 和 `EstTrackSat` 的坐标设为相同值。但我们确实将 `EstSat` 的初始状态设为与 `SimSat` 不同，因为我们最终将尝试从仿真跟踪中估计 `EstSat` 的状态，不想给它一个完美的初始猜测。

## 创建应答机对象并挂接到航天器

要为给定航天器仿真导航测量，GMAT 要求航天器挂接一个 `Transponder` 对象，该对象接收上行信号并转发。下面，我们创建 `Transponder` 对象并挂接到航天器。创建 `Transponder` 对象后，有三个字段必须设置：`PrimaryAntenna`、`HardwareDelay` 和 `TurnAroundRatio`。

```
%
%   Spacecraft hardware
%

Create Antenna SpacecraftAntenna
Create Transponder HGA

HGA.PrimaryAntenna  = SpacecraftAntenna
HGA.HardwareDelay   = 1e-06
HGA.TurnAroundRatio = '880/749'

SimSat.AddHardware = {HGA, SpacecraftAntenna}
EstSat.AddHardware = {HGA, SpacecraftAntenna}
```

**中文说明**：创建航天器天线 SpacecraftAntenna 和应答机 HGA；主天线为 SpacecraftAntenna，硬件延迟 1 微秒，转发比 880/749；将应答机和天线挂接到 SimSat 和 EstSat。

`PrimaryAntenna` 是航天器应答机用于接收和转发射频信号的天线。在上例中，我们将此字段设为已创建的 `Antenna` 对象。目前 `Antenna` 资源没有功能，但测量仿真和估计需要它。`HardwareDelay`（应答机信号延迟，秒）设为 1 微秒。我们将 `TurnAroundRatio`（转发信号与输入信号之比）设为 '880/749'。GMAT 如何使用此输入字段的讨论请参见 RunSimulator 帮助。在上面最后的脚本命令中，我们将新创建的 `Transponder` 及其相关 `Antenna` 对象挂接到每艘被观测航天器。

## 创建接收机对象并挂接到测量航天器

要用给定航天器执行测量，GMAT 要求跟踪航天器挂接 `Transmitter` 和 `Receiver` 对象，它们发送和接收前向与返向跟踪信号。下面，我们创建这些对象并挂接到航天器。

```
%
%   Measurement Spacecraft hardware
%

Create Transmitter MeasurementTransmitter
Create Receiver MeasurementReceiver

MeasurementTransmitter.PrimaryAntenna = SpacecraftAntenna
MeasurementTransmitter.Frequency      = 7200
MeasurementReceiver.PrimaryAntenna    = SpacecraftAntenna

SimTrackSat.AddHardware = {HGA, SpacecraftAntenna, MeasurementTransmitter, MeasurementReceiver}
EstTrackSat.AddHardware = {HGA, SpacecraftAntenna, MeasurementTransmitter, MeasurementReceiver}
```

**中文说明**：创建发射机 MeasurementTransmitter（频率 7200 MHz，主天线 SpacecraftAntenna）和接收机 MeasurementReceiver，并将它们与应答机、天线一起挂接到跟踪航天器 SimTrackSat 和 EstTrackSat。

我们将 `Frequency`（前向/上行跟踪信号的频率）设为 7200 MHz。在上面最后的脚本命令中，我们将新创建的 `Transmitter` 和 `Receiver` 对象挂接到执行测量的航天器。
