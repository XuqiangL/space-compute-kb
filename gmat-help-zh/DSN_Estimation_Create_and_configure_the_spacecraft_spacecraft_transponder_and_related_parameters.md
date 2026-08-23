# 创建并配置航天器、航天器应答机及相关参数（DSN_Estimation_Create_and_configure_the_spacecraft_spacecraft_transponder_and_related_parameters）

> 译自 GMAT R2026a 帮助文档 DSN_Estimation_Create_and_configure_the_spacecraft_spacecraft_transponder_and_related_parameters.html

对于本教程，您需要打开 GMAT，并打开一个新的空脚本。要创建新脚本，点击 **New Script**。

## 创建卫星并设置其历元和笛卡尔坐标

由于这是一艘环绕太阳的航天器，我们选择在以太阳为中心的坐标系中表示轨道，该坐标系用下面的脚本定义。

```
%  Create the Sun-centered J2000 frame.
Create CoordinateSystem SunMJ2000Eq;
SunMJ2000Eq.Origin = Sun;
SunMJ2000Eq.Axes   = MJ2000Eq;  %Earth mean equator axes
```

**中文说明**：创建日心 J2000 坐标系 SunMJ2000Eq，原点为太阳，坐标轴为 MJ2000Eq（地球平赤道轴）。

接下来，我们创建新航天器 `Sat`，并设置其历元和笛卡尔坐标。

```
Create Spacecraft Sat;
Sat.DateFormat       = UTCGregorian;
Sat.CoordinateSystem = SunMJ2000Eq;
Sat.DisplayStateType = Cartesian;
Sat.Epoch            = 19 Aug 2015 00:00:00.000;
Sat.X                = -126544963   %-126544968
Sat.Y                = 61978518     %61978514
Sat.Z                = 24133225     %24133221
Sat.VX               = -13.789
Sat.VY               = -24.673
Sat.VZ               = -10.662

Sat.Id               = 11111;
```

**中文说明**：创建航天器 Sat，历元 2015-08-19 00:00 UTCG，日心惯性系位置约 (-1.265e8, 6.198e7, 2.413e7) km，速度约 (-13.79, -24.67, -10.66) km/s，航天器 ID 11111。注释中的值为仿真"真实"状态。

注意，除了设置 `Sat` 的坐标外，我们还为它分配了 ID 号。当 GMAT 在读入的 GMD 文件中找到此编号时，它就知道关联数据对应于 `Sat` `Spacecraft`。

在仿真教程中，上述笛卡尔状态代表"真实"状态。而在这里，笛卡尔状态代表航天器运营方对状态的最佳"估计"，即所谓的*先验*（a priori）估计。由于人们永远无法精确获知真实状态，我们相对注释字段中显示的仿真真实状态，将上述笛卡尔状态的每个分量扰动了几 km。

## 创建应答机对象并挂接到航天器

要估计给定航天器的轨道状态，GMAT 要求航天器挂接一个 `Transponder` 对象，该对象接收地面站上行信号并（通常）向地面站转发。下面，我们创建 `Transponder` 对象并挂接到航天器。注意，创建 `Transponder` 对象后，有三个字段必须设置：`PrimaryAntenna`、`HardwareDelay` 和 `TurnAroundRatio`。

```
Create Antenna HGA;  %High Gain Antenna

Create Transponder SatTransponder;
SatTransponder.PrimaryAntenna   = HGA;
SatTransponder.HardwareDelay    = 1e-06; %seconds
SatTransponder.TurnAroundRatio  = '880/749';

Sat.AddHardware                 = {SatTransponder, HGA};
Sat.SolveFors                   = {CartesianState};
```

**中文说明**：创建高增益天线 HGA 和应答机 SatTransponder；主天线为 HGA，硬件延迟 1 微秒，转发比 880/749（X 频段）；将应答机和天线挂接到 Sat；求解变量为笛卡尔状态。

`PrimaryAntenna` 是航天器应答机 `SatTransponder` 用于接收和转发射频信号的天线。在上例中，我们将此字段设为已创建的 `Antenna` 对象 `HGA`。目前 `Antenna` 资源没有功能，但在未来版本中可能会有。`HardwareDelay`（应答机信号延迟，秒）设为 1 微秒。

我们将 `TurnAroundRatio`（转发信号与输入信号之比）设为 '880/749'。GMAT 如何使用此输入字段的讨论请参见 `RunEstimator` 帮助。回想一下，作为计算的一部分，估计器需要形成一个称为观测残差 O-C 的量，其中 O 是测量的"观测"值，C 是基于当前轨道状态知识的"计算"值。如帮助中所述，由于本教程的 DSN 数据使用斜坡表，此输入转发比不用于计算多普勒测量的计算值 C。取而代之的是，用于计算多普勒测量计算值的转发比将从斜坡表中包含的上行频段值推断。

注意，在上面倒数第二条脚本命令中，我们将新创建的 `Transponder` 资源 `SatTransponder` 及其相关 `Antenna` 资源 `HGA` 挂接到航天器 `Sat`。

最后一行脚本（在仿真脚本中不存在）用于告诉 GMAT 估计器将估计哪些量，即所谓的"求解变量"（solve-fors）。这里，我们告诉 GMAT 求解卫星笛卡尔状态的 6 个分量。由于我们以 SunMJ2000 坐标输入 `Sat` 状态，这就是 GMAT 将用于求解笛卡尔状态的坐标系。
