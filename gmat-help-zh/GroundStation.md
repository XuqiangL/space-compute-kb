# 地面站（GroundStation）
> 译自 GMAT R2026a 帮助文档 GroundStation.html

**GroundStation** —— 地面站模型。

## 描述

GroundStation 对固定在某 CelestialBody 表面的设施建模。有多种状态表示形式可用于定义地面站的位置，包括笛卡尔（Cartesian）和球面（spherical）表示。此资源不能在任务序列中修改。

另请参阅：ContactLocator、CoordinateSystem、Color

## 字段

| 字段 | 描述 |
|------|------|
| **AddHardware** | 地面站使用的所有 Transmitter、Receiver 和 Antenna 硬件的列表。<br>数据类型：Object Array；允许值：列表中每个元素必须是有效的 Transmitter、Receiver 或 Antenna；访问：set；默认值：None；单位：N/A；接口：脚本 |
| **Altitude** | 地面站相对于 HorizonReference 的高度。<br>数据类型：Real；允许值：-∞ < Real < ∞；访问：set；默认值：0；单位：km；接口：GUI、脚本 |
| **CentralBody** | GroundStation 的中心天体。<br>数据类型：String；允许值：Earth、已配置的天体；访问：set；默认值：Earth；单位：N/A；接口：GUI、脚本 |
| **DataSource** | 获取 Temperature、Pressure、Humidity 和 MinimumElevationAngle 的数据来源。如果值为 Constant，则这些参数在 GroundStation 资源中设置的值对所有相关测量保持恒定。目前，Constant 是唯一允许的值。<br>数据类型：枚举；允许值：Constant；访问：set；默认值：Constant；单位：N/A；接口：脚本 |
| **ErrorModels** | 用户定义的 ErrorModel 对象列表，描述此 GroundStation 使用的测量误差模型。<br>数据类型：StringList；允许值：任何有效的用户自定义 ErrorModel 资源；访问：set；默认值：None；单位：N/A；接口：脚本 |
| **HorizonMaskFileName** | 指定角度对的外部文件的路径，这些角度对描述随方向变化的地平遮蔽剖面。该遮蔽仅由 ContactLocator 资源使用，对估计或仿真没有影响。有关此文件内容和格式的更多细节，请参阅下面的"备注"。<br>数据类型：String；允许值：指向已存在文本遮蔽文件的路径；访问：set；默认值：None；单位：N/A；接口：脚本 |
| **HorizonReference** | 用于地平的参考系统。Sphere 等价于地心（Geocentric），Ellipsoid 等价于大地（Geodetic）。<br>数据类型：String；允许值：Sphere、Ellipsoid；访问：set；默认值：Sphere；单位：N/A；接口：GUI、脚本 |
| **Humidity** | 地面站处的湿度，用于计算 HopfieldSaastamoinen 模型的对流层修正。GMAT 仅在 DataSource 设为 Constant 时使用此值。<br>数据类型：Real；允许值：0.0 <= Real <= 100.0；访问：set、get；默认值：55；单位：percentage；接口：脚本 |
| **Id** | 仿真和估计中使用的 GroundStation 的标识。<br>数据类型：String；允许值：可包含字母、整数、连字符、下划线；访问：set；默认值：StationId；单位：N/A；接口：GUI、脚本 |
| **IonosphereModel** | 光行时计算中使用的电离层模型的指定。<br>数据类型：枚举；允许值：'None'、'IRI2007'、'TRK-2-23'；访问：set；默认值：'None'；单位：N/A；接口：脚本 |
| **Latitude** | 地面站相对于 HorizonReference 的纬度。<br>数据类型：Real；允许值：-90 < Real < 90；访问：set；默认值：0；单位：deg.；接口：GUI、脚本 |
| **Location1** | GroundStation 位置的第一个分量。当 StateType 为 Cartesian 时，Location1 是站址在体固系中的 x 分量。当 StateType 为 Spherical 或 Ellipsoid 时，Location1 是 GroundStation 的 Latitude（deg.）。<br>数据类型：Real；允许值：Cartesian 时 -∞ < Real < ∞，其他见 Longitude、Latitude、Altitude；访问：set；默认值：6378.1363；单位：见描述；接口：GUI、脚本 |
| **Location2** | GroundStation 位置的第二个分量。当 StateType 为 Cartesian 时，Location2 是站址在体固系中的 y 分量。当 StateType 为 Spherical 或 Ellipsoid 时，Location2 是 GroundStation 的 Longitude（deg.）。<br>数据类型：Real；允许值：Cartesian 时 -∞ < Real < ∞，其他见 Longitude、Latitude、Altitude；访问：set；默认值：0；单位：见描述；接口：GUI、脚本 |
| **Location3** | GroundStation 位置的第三个分量。当 StateType 为 Cartesian 时，Location3 是站址在体固系中的 z 分量。当 StateType 为 Spherical 或 Ellipsoid 时，Location3 是 GroundStation 在参考形状之上的高度（km）。<br>数据类型：Reals；允许值：Cartesian 时 -∞ < Real < ∞，其他见 Longitude、Latitude、Altitude；访问：set；默认值：0；单位：见描述；接口：GUI、脚本 |
| **Longitude** | 地面站的经度。<br>数据类型：Real；允许值：value >= 0；访问：set；默认值：0；单位：deg.；接口：GUI、脚本 |
| **MinimumElevationAngle** | 与 ContactLocator 配合使用的最小高度角约束。如果地面站还挂接了带 FieldOfView 遮蔽的天线，则接触定位器计算的时间将被限制为同时满足最小高度角准则和视场遮蔽的时间。<br>对于跟踪数据测量和估计，这是从航天器发射到地面站的信号所允许的最小高度角。仿真时，仅当航天器相对地面站的高度角超过此值时才生成测量。估计时，测量必须超过此值才会被估计器接纳处理。<br>GMAT 仅在 DataSource 设为 Constant 时使用此值。<br>数据类型：Real；允许值：-90 ≤ MinimumElevationAngle ≤ 90；访问：set；默认值：7；单位：deg；接口：GUI、脚本 |
| **OrbitColor** | 允许您为用户自定义的 GroundStation 选择可用颜色。GroundStation 对象绘制在由 GroundTrack 二维图形显示资源创建的航天器星下点轨迹图上。颜色可以通过字符串或整数数组指定。例如：将地面站颜色设为红色可用以下两种方式：`GroundStation.OrbitColor = Red` 或 `GroundStation.OrbitColor = [255 0 0]`。此字段也可以在任务序列中修改。<br>数据类型：整数数组或字符串；允许值：GUI 中轨道颜色选择器可用的任何颜色。有效的预定义颜色名称或 0 到 255 之间的 RGB 三元组值；访问：set；默认值：Thistle；单位：N/A；接口：GUI、脚本 |
| **Pressure** | 地面站处的大气压力，用于计算 HopfieldSaastamoinen 模型的对流层修正。GMAT 仅在 DataSource 设为 Constant 时使用此值。<br>数据类型：Real；允许值：Real > 0.0；访问：set、get；默认值：1013.5；单位：hPa；接口：脚本 |
| **StateType** | 用于定义地面站位置的状态类型。<br>数据类型：String；允许值：Cartesian、Spherical；访问：set；默认值：Cartesian；单位：N/A；接口：GUI、脚本 |
| **SpiceFrameId** | 地面站的 SPICE 坐标系 ID。注意，此字段没有默认值，除非设置为特定的允许值，否则不会保存到脚本中。<br>数据类型：字符串或整数；允许值：有效的 SPICE 坐标系 ID（文本或数字）。地面站的约定为 '399xyz'，其中 'xyz' 为映射到地面站的整数。例如，DSN 地面站 'DSS-66' 的 Id 为 '399066'；访问：set；默认值：无默认值；单位：N/A；接口：脚本 |
| **TargetColor** | 允许您在差分修正或优化等迭代过程中为用户自定义的 GroundStation 对象选择可用颜色。目标颜色可以通过字符串或整数数组指定。例如：将地面站的目标颜色设为黄色可用以下两种方式：`GroundStation.TargetColor = Yellow` 或 `GroundStation.TargetColor = [255 255 0]`。此字段也可以在任务序列中修改。<br>数据类型：整数数组或字符串；允许值：GUI 中轨道颜色选择器可用的任何颜色。有效的预定义颜色名称或 0 到 255 之间的 RGB 三元组值；访问：set；默认值：DarkGray；单位：N/A；接口：GUI、脚本 |
| **Temperature** | 地面站处的气温，用于计算 HopfieldSaastamoinen 模型的对流层修正。GMAT 仅在 DataSource 设为 Constant 时使用此值。<br>数据类型：Real；允许值：Real > 0.0；访问：set、get；默认值：295.1；单位：Kelvin；接口：脚本 |
| **TroposphereModel** | 光行时计算中使用的对流层模型的指定。<br>数据类型：枚举；允许值：'None'、'HopfieldSaastamoinen'、'Marini'、'TRK-2-23'；访问：set；默认值：'None'；单位：N/A；接口：脚本 |

## GUI

要创建 GroundStation，从资源树（Resource Tree）开始：

1. 右键点击 GroundStation 文件夹并选择 Add Ground Station。
2. 双击 GroundStation1。

> [图：GroundStation 默认对话框（Cartesian 表示）]

您可以用多种状态表示形式设置地面站位置。上图展示的是 Cartesian 表示。要将相对于参考椭球的 Longitude、Latitude 和 Altitude 分别设为 45 deg.、270 deg. 和 0.1 km：

1. 在 StateType 菜单中选择 Spherical。
2. 在 HorizonReference 菜单中选择 Ellipsoid。
3. 在 Latitude 文本框中输入 `45`。
4. 在 Longitude 文本框中输入 `270`。
5. 在 Altitude 文本框中输入 `0.1`。

> [图：采用 Ellipsoid 参考的 GroundStation 对话框]

## 备注

GroundStation 模型允许您使用多种状态表示形式之一，以体固坐标定义设施位置来配置地面站。GMAT 支持 Cartesian、Sphere 和 Ellipsoid 表示，下面的示例展示了如何在每种表示中配置 GroundStation。当使用 Ellipsoid 模型或 Sphere 表示时，GMAT 使用 CelestialBody 资源上定义的物理属性（例如扁率和半径），基于双轴椭球模型将其转换为笛卡尔坐标。

### 地面站遮蔽文件

用户可以指定一个随方向变化的遮蔽文件，供 ContactLocator 资源使用。该遮蔽通常用于描述天线附近的地形、建筑物或其他可能在某些方向阻挡信号的障碍物。遮蔽文件由一个描述文件中角度类型的关键字和两列表示遮蔽角度对的数据组成，如下例所示。

```
AzimuthElevationAngles

  0.0   7.6
  3.0   6.5
  8.0   3.1
 38.0   6.6
 45.0   5.5
 58.0   8.4
 70.0   7.6
 77.0   9.2
... etc ...
360.0   7.6
```

说明：该遮蔽文件首行以关键字 AzimuthElevationAngles 声明角度类型，随后每行为一对角度（方位角、高度角，单位：度），覆盖 0 到 360 度方位范围。

允许的角度类型为 `AzimuthElevationAngles`（指定文件包含方位角和高度角对）或 `ClockConeAngles`（指定文件包含时钟角和锥角）。

GMAT 还可以读取 STK 格式的 "aem" 遮蔽文件，STK "aem" 文件可以指定给 HorizonMaskFileName 参数使用。

### 设置地面站设施的颜色

GMAT 允许您为创建的地面站设施设置颜色。GroundStation 绘制在 GroundTrack 二维图形显示上。GroundStation 对象的 OrbitColor 和 TargetColor 字段用于设置地面站设施的颜色。有关这两个字段的更多信息，请参阅"字段"部分。另请参阅 Color 文档，了解如何设置地面站设施颜色的讨论和示例。

### Marini 对流层模型数据文件

Marini 对流层模型使用一个数据文件，其中包含地球表面不同位置的模型计算月平均值。该数据文件的位置由启动文件中的 `MARINI_TROPO_FILE` 属性指定。数据文件中每行包含一个纬度经度对，后跟 12 个值，对应一年中的每个月。数据文件中的每个值将折射率和标高因子组合为一个整数，两者都用于 Marini 模型。最右边的两位数字用于获得标高，左边其余数字表示折射率。用于标高的数字将小数点放在两位数字之间，而折射率值的小数点放在其最右数字的右侧。例如，数据文件中的值 37068 对应折射率 370 和标高 6.8。

如果某行与地面站位置的纬度差和经度差均在一度以内，则选中该行使用。然后根据一年中的月份选择列。如果地面站位置与数据文件中多个位置的纬度和经度差都在一度以内，则选择第一行。如果地面站位置与数据文件中任何位置的纬度和经度差都不在一度以内，则无论月份如何，都使用默认值 37068。纬度范围为 -90 到 90 度，经度范围为 0 到 360 度。

### 用于轨道确定的电离层建模

跟踪数据测量的信号路径在穿过地球电离层时会发生弯曲。该效应的大小取决于信号频率，并在高频时迅速减小。K 频段或更高频率的测量通常可以安全地忽略或禁用电离层修正，但对于 S 频段或更低频率的跟踪，通常希望对电离层修正建模。电离层修正还与高度角相关，在低信号路径高度角处急剧增大。在低高度角（低于 5 度）时，计算的修正很可能不准确，一般应将低高度角测量排除在估计使用之外。

电离层修正所用的频率不是从跟踪数据中获取的，必须在挂接到发射地面站的 Transmitter 对象上设置。如果未提供 Transmitter 对象，则使用 2000 MHz 的默认频率。

> **注意**：TDRS 用户和 BRTS 跟踪在上行/下行链路（地面与 TDRS 之间）和前向/返向链路（TDRS 与用户或 BRTS 之间）使用不同的频率。用于电离层建模的上行/下行频率在 TDRS 地面站的 Transmitter 对象上设置。用于电离层建模的前向/返向频率在 BRTS 地面站的 Transmitter 对象上设置。如果 BRTS 没有挂接 Transmitter，则使用前向链路的地面上行频率计算电离层修正。目前，TDRS 与在轨用户之间的前向/返向链路不包含任何介质修正（对流层和电离层均不包含）。

### TRK-2-23 模型实现

使用 TRK-2-23 文件进行对流层和电离层约定时，要求用户遵循某些约定。每艘航天器应将其 NAIFId 参数设置为与其航天器编号匹配。对于每个使用 TRK-2-23 模型的地面站，将 Id 参数设置为 DSN 站编号。此外，每个包含待处理 .csp 和 .csp.ql（快速查看）文件的目录，都应以字符串数组的形式指定给 Earth.DSNMediaFileDirectories 参数，每个数组元素包含一个目录路径。如果某个目录包含时间条目重叠的 .csp 和 .csp.ql 文件，则优先使用 .csp 文件中的数据。

TRK-2-23 数据条目包含以下测量类型的修正信息：ALL、DOPRNG、RANGE、DOPPLER 和 VLBI。指定为 ALL 的系数可应用于任何类型的测量，并用于对流层修正。仅使用 seasonal.csp 文件即可执行对流层修正，但如果包含覆盖运行时间跨度的月度修正文件，将获得更高的精度。DOPRNG、RANGE、DOPPLER 和 VLBI 系数适用于电离层修正。由于 GMAT 将介质修正作为计算两点之间距离测量的一个组成部分来执行，因此文件必须为 DOPRNG 或 RANGE 类型才能与 GMAT 电离层修正模型兼容。

由于 GMAT 通过先计算距离再确定多普勒频移来生成多普勒测量，因此介质修正不直接应用于多普勒测量。因此，不支持使用仅含 DOPPLER 测量修正的 TRK-2-23 文件。同样不支持 VLBI，因为 GMAT 目前不支持基于 VLBI 的测量。

由于电离层条目仅在地面站对航天器可见的狭窄时间窗口内定义，因此用户在实现该模型时应特别注意使用准确的初始参数。TRK-2-23 数据格式的进一步规范见参考文献 1 的第 3 节。

## 示例

以大地（Geodetic）坐标配置 GroundStation：

```
Create GroundStation aGroundStation
aGroundStation.CentralBody      = Earth
aGroundStation.StateType        = Spherical
aGroundStation.HorizonReference = Ellipsoid
aGroundStation.Location1        = 60
aGroundStation.Location2        = 45
aGroundStation.Location3        = 0.01

% or alternatively

aGroundStation.Latitude  = 60
aGroundStation.Longitude = 45
aGroundStation.Altitude  = 0.01
```

说明：本示例以大地坐标配置地面站：中心天体为地球，状态类型为球面，地平参考为椭球（即大地纬度），Location1/2/3 分别为纬度 60 deg.、经度 45 deg.、高度 0.01 km；也可以等效地直接设置 Latitude、Longitude、Altitude 字段。

以地心（Geocentric）坐标配置 GroundStation：

```
Create GroundStation aGroundStation
aGroundStation.CentralBody      = Earth
aGroundStation.StateType        = Spherical
aGroundStation.HorizonReference = Sphere
aGroundStation.Location1        = 59.83308194090783
aGroundStation.Location2        = 45
aGroundStation.Location3        = -15.99424674414058

% or alternatively

aGroundStation.Latitude        = 59.83308194090783
aGroundStation.Longitude       = 45
aGroundStation.Altitude        = -15.99424674414058
```

说明：本示例以地心坐标配置地面站：地平参考为球体（即地心纬度），纬度 59.83308194090783 deg.、经度 45 deg.、高度 -15.99424674414058 km；也可以等效地直接设置 Latitude、Longitude、Altitude 字段。

以笛卡尔坐标配置 GroundStation：

```
Create GroundStation aGroundStation
aGroundStation.CentralBody = Earth
aGroundStation.StateType   = Cartesian
aGroundStation.Location1   = 2260.697433050543
aGroundStation.Location2   = 2260.697433050542
aGroundStation.Location3   = 5500.485954732006
```

说明：本示例以笛卡尔坐标配置地面站：中心天体为地球，状态类型为 Cartesian，Location1/2/3 分别为站址在体固系中的 x、y、z 分量（单位：km）。

配置一个 GroundStation，使其在用于导航时对 RF 信号在大气中的折射建模：

```
Create GroundStation aGroundStation
aGroundStation.IonosphereModel       = 'IRI2007';
aGroundStation.TroposphereModel      = 'HopfieldSaastamoinen';

BeginMissionSequence;
```

说明：本示例配置地面站的电离层模型为 IRI2007、对流层模型为 HopfieldSaastamoinen，用于导航时对 RF 信号的大气折射建模。

配置一个 GroundStation，使其在用于导航时使用 TRK-2-23 数据对 RF 信号在大气中的折射建模：

```
Create GroundStation aSpacecraft
aSpacecraft.NAIFId       = -64;

Create GroundStation aGroundStation
aGroundStation.Id                    = '026';
aGroundStation.IonosphereModel       = 'TRK-2-23';
aGroundStation.TroposphereModel      = 'TRK-2-23';

Earth.DSNMediaFileDirectories = {'path/to/directory/Troposphere','path/to/directory/Ionosphere','path/to/directory/Additional'}

BeginMissionSequence;
```

说明：本示例设置航天器 NAIFId 为 -64，地面站 Id 为 DSN 站编号 '026'，电离层和对流层模型均为 TRK-2-23，并将包含介质修正文件的目录数组指定给 Earth.DSNMediaFileDirectories。

将 Transmitter 和 Receiver 资源挂接到 GroundStation：

```
Create Transmitter Transmitter1
Create Receiver Receiver1

Create GroundStation aGroundStation;
aGroundStation.AddHardware = {Transmitter1, Receiver1};

BeginMissionSequence;
```

说明：本示例创建发射机 Transmitter1 和接收机 Receiver1，创建地面站 aGroundStation，并通过 AddHardware 将两者挂接到地面站。

## 参考文献

[1] Machuzak, Berner, Pham and Stipanuk. *TRK-2-23 Media Calibration Interface*. Technical Report JPL D-16765, NASA, 2008.
