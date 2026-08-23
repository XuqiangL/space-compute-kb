# 行星表面区域（PlanetographicRegion）
> 译自 GMAT R2026a 帮助文档 PlanetographicRegion.html

**PlanetographicRegion** —— 将天体表面上的一个区域定义为观测航天器（Spacecraft）的目标。

## 描述

> **注意**：`PlanetographicRegion` 与 **ContactLocator**（可见性分析器）资源紧密关联。它实际上定义了一个区域目标，然后在 `ContactLocator` 中像任何其他目标一样使用。

`PlanetographicRegion` 是天体表面上的区域目标，用于查找航天器的星下点进入和离开该 `PlanetographicRegion` 的穿越事件。**PlanetographicRegion** 由用户输入的纬度和经度点对定义。默认情况下，**PlanetographicRegion** 使用 `ContactLocator` 生成文本事件报告，列出每次穿越事件的开始和结束时间以及持续时间。可见性（contact）定位可以在整个传播区间或子区间上执行；与常规的 **ContactLocator** 不同，此时忽略光行时延迟和恒星光行差。与标准可见性定位的另一个区别是，**PlanetographicRegion** 使用星下点，因此仰角按设计为 90 度。

可见性定位可以在一个 `Spacecraft`（`Observer`，观测者）和一个 `PlanetographicRegion` 区域（`Target`，目标）之间执行。使用多个 `ContactLocator` 资源，可以在一次运行中包含多个目标-观测者对。

默认情况下，`PlanetographicRegion` 搜索 `Observer` 的整个传播区间；详情请参阅"备注"。要像标准 **ContactLocator** 一样搜索自定义区间，请将 `UseEntireInterval` 设为 `False` 并相应地设置 `InitialEpoch` 和 `FinalEpoch`。注意，如果这些历元落在 `Observer` 的传播区间之外，GMAT 将显示错误。

与标准 ContactLocator 不同，**PlanetographicRegion** 忽略光行时延迟和恒星光行差。这两个开关可以设为 `True` 或 `False`，但每种组合都会产生相同的输出区间。（虽然与 **PlanetographicRegion** 无关，但如果恒星光行差为 `True` 而光行时修正为 `False`，GMAT 会抛出错误。）选择这种行为是为了使结果与在穿越时间计算中使用星下点保持一致。

事件搜索以固定步长遍历区间。你可以通过设置 `StepSize` 字段来控制步长（以秒为单位）。对于穿越复杂区域（例如经纬度 **PlanetographicRegion** 定义点密集排列的区域），或掠过"尖锐"目标区域的情况，减小步长可能很有用；否则，算法可能会"跨过"该特征，导致对区域的进入/退出判断出现误报或漏报。详情请参阅"备注"。

GMAT 使用 SPICE 库作为基本的事件定位算法。因此，该子系统的所有天体数据都从 SPICE 内核加载，而不是使用 GMAT 自己的 `CelestialBody` 形状和定向配置。目前 **PlanetographicRegion** 仅支持以地球为 **CentralBody**（中心天体）；其他选择会导致 GMAT 抛出错误。

除非另有说明，`ContactLocator` 字段不能在任务序列中设置。

**另请参阅**：ContactLocator（可见性分析器）、Spacecraft（航天器）、CelestialBody（天体）、FindEvents（事件查找）

## 字段

| 字段 | 描述 |
|------|------|
| **AreaFileName** | 区域定义文件的名称和路径。文件顶部可以包含注释，之后是纬度和经度点对。示例见下文。对于特定区域，使用此文件定义区域，或使用下文所述的纬度/经度数组，二者择一。对同一区域同时使用两者会导致 GMAT 抛出错误。<br>数据类型：字符串<br>允许值：有效的文件路径<br>访问权限：set<br>默认值：`None`<br>单位：N/A<br>接口：脚本 |
| **CentralBody** | 定义区域所在的天体。目前仅实现了地球。<br>数据类型：字符串<br>允许值：仅 `"Earth"`<br>访问权限：set<br>默认值：`"Earth"`<br>单位：N/A<br>接口：脚本 |
| **Latitude** | 定义区域的纬度点数组。必须有元素数量相同的对应 **Longitude**（经度）数组。<br>数据类型：实数数组，以逗号分隔<br>允许值：-90 到 90<br>访问权限：set<br>默认值：`None`<br>单位：度<br>接口：脚本 |
| **Longitude** | 定义区域的经度点数组。必须有元素数量相同的对应 **Latitude**（纬度）数组。<br>数据类型：实数数组，以逗号分隔<br>允许值：-180 到 180 或 0 到 360（不能在一个数组中混用两种）<br>访问权限：set<br>默认值：`None`<br>单位：度<br>接口：脚本 |

## 备注

### 搜索区间

对于 **PlanetographicRegion**，`ContactLocator` 搜索区间可以指定为 `Observers`（观测者）的整个历表区间，也可以指定为用户自定义区间。每种模式在处理不连续区间方面都有特定的行为。

如果 `UseEntireInterval` 为 true，搜索将在 `Observers` 的整个历表区间上执行，包括任何空隙或不连续段。对于 **PlanetographicRegion**，光行时延迟被忽略。

如果 `UseEntireInterval` 为 false，则直接使用提供的 `InitialEpoch` 和 `FinalEpoch` 构成搜索区间。用户必须确保所提供的区间对应有效的 `Observers` 历表历元。

### 运行模式

在运行模式方面，**PlanetographicRegion** 功能使用 `ContactLocator` 的功能，它与 `FindEvents` 命令协同工作：`ContactLocator` 资源定义事件搜索的配置，`FindEvents` 命令在任务序列的特定位置执行搜索。交互模式由 `ContactLocator`.`RunMode` 定义，它有三个选项：

- `Automatic`：所有 `FindEvents` 命令照常执行，另外在任务序列末尾自动执行一次额外的 `FindEvents`。
- `Manual`：所有 `FindEvents` 命令照常执行。
- `Disabled`：`FindEvents` 命令被忽略。

### 搜索算法

`PlanetographicRegion` 算法从星下点（在指定时间区间）到确定位于天体之外的一点作一条线段。如果它与奇数条线段相交（通常是一条），则该点被认为在多边形*内部*；同样，如果遇到偶数条（通常为零），则星下点被认为在区域*外部*。当发生变化（由内到外或由外到内）时，GMAT 将确定变化发生的*时刻*。

点之间的线段是基于两点在所在天体表面上的最短路径绘制的。这通常称为两点之间的大圆路径。这意味着两点之间的线段在平面地图上绘制时可能呈现弯曲。越接近极点、线段越长，这种弯曲效应越明显。如果需要非大圆路径，请添加位于所需线段上的额外点。这将使线条在平面地图上绘制时变直。

需要注意的是，如果起始历元时星下点在区域内，那么即使它不靠近边界，也会被列为进入区域；同样，如果历元结束时星下点在区域内，则历元结束时间将被列为离开区域的最终点。

还需要注意的是，如果星下点在两次检查之间穿越了两次或更多次（由于区间较长），则可能不会记录穿越（穿越次数为偶数时），或者不能找到所有穿越（穿越次数为三及以上的奇数时）。在这些情况下，可以减小 **StepSize** 参数以捕捉更精细的细节。相关示例请参阅下文"为具有尖锐顶点的区域减小步长"。

相反，过于细致的区域或过小的时间区间可能会导致性能问题。因此需要权衡，例如，如果没有复杂的区域目标，可以通过增大 `StepSize` 来提高搜索性能。

## 示例

为 LEO（近地轨道）航天器设置一个基本的 **PlanetographicRegion**：

```
Create Spacecraft Fermi

Fermi.DateFormat                   = UTCGregorian;
Fermi.Epoch                        = '16 Mar 2010 00:00:00.000';
Fermi.CoordinateSystem             = EarthMJ2000Eq;
Fermi.DisplayStateType             = Cartesian;
Fermi.X                            = 1861.715588    
Fermi.Y                            = -6097.672271    
Fermi.Z                            = -2687.893642       
Fermi.VX                           = 7.278672       
Fermi.VY                           = 1.600198       
Fermi.VZ                           = 1.424786
Fermi.DryMass                      = 4357.33
Fermi.Cd                           = 2.1
Fermi.CdSigma                      = 0.21
Fermi.AtmosDensityScaleFactor      = 1.0;
Fermi.AtmosDensityScaleFactorSigma = 1.0;
Fermi.Cr                           = 0.75
Fermi.CrSigma                      = 0.1
Fermi.DragArea                     = 14.18
Fermi.SRPArea                      = 14.18
Fermi.Id                           = 'Fermi'

Create ForceModel FM

FM.CentralBody            = Earth
FM.PointMasses            = {Earth}
FM.RelativisticCorrection = Off
FM.SRP                    = Off
FM.ErrorControl           = None

Create Propagator Prop

Prop.FM   = FM
Prop.Type = RungeKutta89

Create PlanetographicRegion SAA
SAA.CentralBody = Earth
SAA.Latitude  = [ 20,  20, -20, -20]
SAA.Longitude = [ 20, -20, -20,  20]

Create ContactLocator CL
CL.Observers = {Fermi}
CL.Target    = SAA
CL.Filename  = 'Contacts_PlanetoRegion_Square.txt'

BeginMissionSequence

Propagate Prop(Fermi) {Fermi.ElapsedDays = 1.0}
```

说明：创建 Fermi 卫星（近地轨道）和仅含地球点质量的力模型；用经纬度数组定义一个以地球为中心天体的方形区域 SAA（纬度 ±20°、经度 ±20°）；可见性分析器以 Fermi 为观测者、SAA 为目标；传播 1 天并输出穿越报告。

通过文件为 LEO 航天器输入 **PlanetographicRegion**：

```
%
Create Spacecraft Fermi

Fermi.DateFormat                   = UTCGregorian;
Fermi.Epoch                        = '16 Mar 2010 00:00:00.000';
Fermi.CoordinateSystem             = EarthMJ2000Eq;
Fermi.DisplayStateType             = Cartesian;
Fermi.X                            = 1861.715588    
Fermi.Y                            = -6097.672271    
Fermi.Z                            = -2687.893642       
Fermi.VX                           = 7.278672       
Fermi.VY                           = 1.600198       
Fermi.VZ                           = 1.424786
Fermi.DryMass                      = 4357.33
Fermi.Cd                           = 2.1
Fermi.CdSigma                      = 0.21
Fermi.AtmosDensityScaleFactor      = 1.0;
Fermi.AtmosDensityScaleFactorSigma = 1.0;
Fermi.Cr                           = 0.75
Fermi.CrSigma                      = 0.1
Fermi.DragArea                     = 14.18
Fermi.SRPArea                      = 14.18
Fermi.Id                           = 'Fermi'

Create ForceModel FM

FM.CentralBody            = Earth
FM.PointMasses            = {Earth}
FM.RelativisticCorrection = Off
FM.SRP                    = Off
FM.ErrorControl           = None

Create Propagator Prop

Prop.FM   = FM
Prop.Type = RungeKutta89

Create PlanetographicRegion SAA
SAA.CentralBody = Earth
SAA.AreaFileName = (optional directory path\)PlanetoRegion_Sample.AT

Create ContactLocator CL
CL.Observers = {Fermi}
CL.Target    = SAA
CL.Filename  = 'Contacts_PlanetoRegion_Sample_FileInput.txt'

BeginMissionSequence

Propagate Prop(Fermi) {Fermi.ElapsedDays = 1.0}
```

说明：与上例相同，但区域改用区域定义文件（`AreaFileName`）输入，而不是经纬度数组。

**PlanetographicRegion** 区域输入文件示例（用于上例）：

```
PlanetographicRegion
% First line is required to be the above keyword
% comment lines indicated by the percent sign
% any number of comment lines allowed between header and data lines
% blank lines are allowed in the header
% Windows or Linux line endings are allowed
% this file implements the same simple square which is 
%    implemented in arrays in the above sample
% each row is a Lat/Long pair: 
%    first column is Latitude, second is Longitude
% no intrinsic limit on the number of rows; has been tested to 1200
% last row does not have to repeat first row

 20    20 
 20   -20 
-20   -20 
-20    20 
```

说明：区域文件第一行必须是关键字 `PlanetographicRegion`；百分号表示注释行；文件头与数据行之间允许任意数量的注释行和空行；允许 Windows 或 Linux 换行符；每行是一对纬度/经度（第一列纬度、第二列经度）；行数没有内在限制（已测试到 1200 行）；最后一行不必重复第一行。

在单次运行中使用多个 **PlanetographicRegion** 区域（输入区域可以是文件和数组的任意组合）：

```
Create Spacecraft Fermi
Fermi.DateFormat                   = UTCGregorian;
Fermi.Epoch                        = '16 Mar 2010 00:00:00.000';
Fermi.CoordinateSystem             = EarthMJ2000Eq;
Fermi.DisplayStateType             = Cartesian;
Fermi.X                            = 1861.715588    
Fermi.Y                            = -6097.672271    
Fermi.Z                            = -2687.893642       
Fermi.VX                           = 7.278672       
Fermi.VY                           = 1.600198       
Fermi.VZ                           = 1.424786
Fermi.DryMass                      = 4357.33
Fermi.Cd                           = 2.1
Fermi.CdSigma                      = 0.21
Fermi.AtmosDensityScaleFactor      = 1.0;
Fermi.AtmosDensityScaleFactorSigma = 1.0;
Fermi.Cr                           = 0.75
Fermi.CrSigma                      = 0.1
Fermi.DragArea                     = 14.18
Fermi.SRPArea                      = 14.18
Fermi.Id                           = 'Fermi'

Create ForceModel FM
FM.CentralBody            = Earth
FM.PointMasses            = {Earth}
FM.RelativisticCorrection = Off
FM.SRP                    = Off
FM.ErrorControl           = None

Create Propagator Prop
Prop.FM   = FM
Prop.Type = RungeKutta89

Create PlanetographicRegion LAT_SAA
Create PlanetographicRegion GBM_SAA

LAT_SAA.CentralBody = Earth
LAT_SAA.Latitude  = [ 20,  20, -20, -20]
LAT_SAA.Longitude = [ 20, -20, -20,  20]

GBM_SAA.CentralBody = Earth
GBM_SAA.Latitude  = [9.515, 11.0, -7.0, -9.0]
GBM_SAA.Longitude = [-170.0, 168.0, 178.0, -175.0]

Create ContactLocator CL1
CL1.Observers = {Fermi}
CL1.Target    = LAT_SAA
CL1.Filename  = 'Contacts_PlanetoRegion_FermiMultiArea_LAT.txt'

Create ContactLocator CL2
CL2.Observers = {Fermi}
CL2.Target    = GBM_SAA
CL2.Filename  = 'Contacts_PlanetoRegion_FermiMultiArea2_GBM.txt'

BeginMissionSequence

Propagate Prop(Fermi) {Fermi.ElapsedDays = 1.0}
```

说明：定义两个区域（LAT_SAA 和 GBM_SAA），并各用一个 ContactLocator（CL1、CL2）分别输出穿越报告，实现在一次运行中分析多个区域。

为具有尖锐顶点的区域减小步长：

```
%   South Polar Region Area target with EOS-like sun-sync satellite
Create Spacecraft EOS
EOS.DateFormat                   = UTCGregorian;
EOS.Epoch                        = '16 Mar 2010 00:00:00.000';
EOS.CoordinateSystem             = EarthMJ2000Eq;
EOS.DisplayStateType             = Cartesian;
EOS.X                            = 257.38045993527360   
EOS.Y                            = 948.52767071254202
EOS.Z                            = -6869.1766527867969
EOS.VX                           = 6.1343425407376108   
EOS.VY                           = -4.4346302750983723      
EOS.VZ                           = -0.38250721354048136
EOS.DryMass                      = 4357.33
EOS.Cd                           = 2.1
EOS.CdSigma                      = 0.21
EOS.AtmosDensityScaleFactor      = 1.0;
EOS.AtmosDensityScaleFactorSigma = 1.0;
EOS.Cr                           = 0.75
EOS.CrSigma                      = 0.1
EOS.DragArea                     = 14.18
EOS.SRPArea                      = 14.18
EOS.Id                           = 'EOS'

Create ForceModel FM
FM.CentralBody            = Earth
FM.PointMasses            = {Earth}
FM.RelativisticCorrection = Off
FM.SRP                    = Off
FM.ErrorControl           = None

Create Propagator Prop
Prop.FM   = FM
Prop.Type = RungeKutta89

Create PlanetographicRegion SAA
SAA.CentralBody = Earth
SAA.Latitude  = [-70.0, -80.0, -85.0, -85.0, -70.0, -75.0]
SAA.Longitude = [20.0,   80.0,   0.0,  220.0, 320.0, 359.0]

Create ContactLocator CL
CL.StepSize = 1.0
CL.Observers = {EOS}
CL.Target    = SAA
CL.Filename  = 'Contacts_PlanetoRegion_EOSsouthPolarArea.txt'

BeginMissionSequence

Propagate Prop(EOS) {EOS.ElapsedDays = 1.0}
```

说明：以类 EOS 太阳同步卫星分析南极区域目标。该区域顶点尖锐，因此将 `CL.StepSize` 减小到 1.0 秒，以避免算法跨过细小特征而漏报穿越。

仅在观测者（Observers）轨道的部分区间上生成报告：

```
Create Spacecraft Fermi
Fermi.DateFormat                   = UTCGregorian;
Fermi.Epoch                        = '16 Mar 2010 00:00:00.000';
Fermi.CoordinateSystem             = EarthMJ2000Eq;
Fermi.DisplayStateType             = Cartesian;
Fermi.X                            = 1861.715588    
Fermi.Y                            = -6097.672271    
Fermi.Z                            = -2687.893642       
Fermi.VX                           = 7.278672       
Fermi.VY                           = 1.600198       
Fermi.VZ                           = 1.424786
Fermi.DryMass                      = 4357.33
Fermi.Cd                           = 2.1
Fermi.CdSigma                      = 0.21
Fermi.AtmosDensityScaleFactor      = 1.0;
Fermi.AtmosDensityScaleFactorSigma = 1.0;
Fermi.Cr                           = 0.75
Fermi.CrSigma                      = 0.1
Fermi.DragArea                     = 14.18
Fermi.SRPArea                      = 14.18
Fermi.Id                           = 'Fermi'

Create ForceModel FM
FM.CentralBody            = Earth
FM.PointMasses            = {Earth}
FM.RelativisticCorrection = Off
FM.SRP                    = Off
FM.ErrorControl           = None

Create Propagator Prop
Prop.FM   = FM
Prop.Type = RungeKutta89

Create PlanetographicRegion SAA
SAA.CentralBody = Earth
SAA.Latitude  = [ 20,  20, -20, -20]
SAA.Longitude = [ 20, -20, -20,  20]

Create ContactLocator CL
CL.Observers = {Fermi}
CL.Target    = SAA
CL.Filename  = 'Contacts_PlanetoRegion_DelayStartTime.txt'

CL.UseEntireInterval = false
CL.InputEpochFormat = UTCGregorian;
CL.InitialEpoch     = '16 Mar 2010 04:30:00.000';
CL.FinalEpoch       = '17 Mar 2010 00:00:00.000';

BeginMissionSequence

Propagate Prop(Fermi) {Fermi.ElapsedDays = 1.0}
```

说明：将 `UseEntireInterval` 设为 false，并用 `InitialEpoch`/`FinalEpoch` 指定自定义搜索区间（从 04:30 开始而非传播起点），使报告只覆盖观测者轨道的一部分。
