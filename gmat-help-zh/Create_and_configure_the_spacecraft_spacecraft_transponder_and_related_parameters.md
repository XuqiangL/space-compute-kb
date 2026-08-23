# 创建并配置航天器、航天器应答机及相关参数（Create_and_configure_the_spacecraft_spacecraft_transponder_and_related_parameters）

> 译自 GMAT R2026a 帮助文档 Create_and_configure_the_spacecraft_spacecraft_transponder_and_related_parameters.html

（本小节属于"第 13 章 仿真 DSN 测距与多普勒数据"教程）

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
Sat.X                = -126544968
Sat.Y                =  61978514
Sat.Z                =  24133221
Sat.VX               = -13.789
Sat.VY               = -24.673
Sat.VZ               = -10.662

Sat.Id               = 11111;
```

**中文说明**：创建航天器 Sat，历元 2015-08-19 00:00 UTCG，日心惯性系位置约 (-1.265e8, 6.198e7, 2.413e7) km，速度约 (-13.79, -24.67, -10.66) km/s，航天器 ID 11111。

注意，除了设置 `Sat` 的坐标外，我们还为它分配了 ID 号。这是将写入我们稍后讨论的 GMAT 测量数据（GMD）文件的编号。

## 创建应答机对象并挂接到航天器

要为给定航天器仿真导航测量，GMAT 要求航天器挂接一个 `Transponder` 对象，该对象接收地面站上行信号并（通常）向地面站转发。下面，我们创建 `Transponder` 对象并挂接到航天器。

```
Create Antenna HGA;

Create Transponder SatTransponder;
SatTransponder.PrimaryAntenna      = HGA;
SatTransponder.HardwareDelay       = 1e-06; %seconds
SatTransponder.TurnAroundRatio     = '880/749';

Sat.AddHardware                    = {SatTransponder, HGA};
```

**中文说明**：创建高增益天线 HGA 和应答机 SatTransponder；主天线为 HGA，硬件延迟 1 微秒，转发比 880/749；将应答机和天线挂接到 Sat。

创建 `Transponder` 对象后，有三个字段必须设置：`PrimaryAntenna`、`HardwareDelay` 和 `TurnAroundRatio`。

`PrimaryAntenna` 是航天器应答机 `SatTransponder` 用于接收和转发射频信号的天线。在上例中，我们将此字段设为已创建的 `Antenna` 对象 `HGA`。目前 `Antenna` 资源没有功能，但在未来版本中可能会有。`HardwareDelay`（应答机信号延迟，秒）设为 1 微秒。我们将 `TurnAroundRatio`（转发信号与输入信号之比）设为 '880/749'。GMAT 如何使用此输入字段的讨论请参见 RunSimulator 帮助和"附录 A —— 测量噪声值的确定"。如帮助中所述，如果我们的 DSN 数据不使用斜坡表，此转发比将直接用于计算多普勒测量。

注意，在上面最后的脚本命令中，我们将新创建的 `Transponder` 及其相关 `Antenna` 对象挂接到航天器 `Sat`。
