# 航天器历元（Spacecraft Epoch）
> 译自 GMAT R2026a 帮助文档 SpacecraftEpoch.html

**Spacecraft Epoch —— 航天器历元**

## 描述

航天器（Spacecraft）的历元（Epoch）是与指定轨道状态相对应的时间和日期。关于历元、坐标系与航天器状态字段之间的相互作用，请参见"航天器轨道状态（Spacecraft Orbit State）"一节。

**另请参阅**：航天器（Spacecraft）

> **注意**
>
> GMAT 的修正儒略日期（Modified Julian Date，MJD）格式与其他软件不同。修正儒略格式与完整儒略日期（JD）之间相差一个常数偏移量：
>
> `MJD = JD - offset`
>
> GMAT 使用非标准的偏移量，如下表所示。
>
> | 历元类型 | **GMAT** | 通用（common） |
> |---|---|---|
> | 参考历元 | **1941 年 1 月 5 日 12:00:00.000** | 1858 年 11 月 17 日 00:00:00.000 |
> | 修正儒略偏移量 | **2430000.0** | 2400000.5 |

## 字段

### DateFormat

`Epoch` 字段的时间系统和格式。在 GUI 中，此字段称为 `EpochFormat`。

- 数据类型：枚举（Enumeration）
- 允许值：`A1ModJulian`、`TAIModJulian`、`UTCModJulian`、`TTModJulian`、`TDBModJulian`、`A1Gregorian`、`TAIGregorian`、`TTGregorian`、`UTCGregorian`、`TDBGregorian`
- 访问权限：仅可设置（set only）
- 默认值：`TAIModJulian`
- 接口：GUI、脚本

### Epoch

与指定轨道状态相对应的时间和日期。

- 数据类型：时间（Time）
- 允许值：Gregorian（公历格式）：`04 Oct 1957 12:00:00.000` <= `Epoch` <= `28 Feb 2100 00:00:00.000`
  Modified Julian（修正儒略格式）：`6116.0` <= `Epoch` <= `58127.5`
- 访问权限：仅可设置（set only）
- 默认值：21545
- 接口：GUI、脚本

### A1ModJulian

A.1 时间系统、修正儒略（Modified Julian）格式的航天器轨道历元。

- 数据类型：字符串（String）
- 允许值：参见 `Epoch`
- 访问权限：可设置、可读取（读取仅限任务序列）
- 默认值：21545.00000039794
- 单位：Days
- 接口：脚本

### CurrA1MJD

*此字段已弃用，不应再使用。*

以 `A1ModJulian` 格式表示的当前历元。此字段只能在任务序列中使用。

- 数据类型：时间（Time）
- 允许值：`6116.0` <= `CurrA1MJD` <= `58127.5`
- 访问权限：可读取、可设置（仅限任务序列）
- 默认值：21545 修正儒略（TAI）的换算等效值
- 接口：仅脚本

### A1Gregorian

A.1 时间系统、公历（Gregorian）格式的航天器轨道历元。

- 数据类型：字符串（String）
- 允许值：参见 `Epoch`
- 访问权限：可设置、可读取（读取仅限任务序列）
- 默认值：01 Jan 2000 12:00:00.034
- 单位：N/A
- 接口：GUI、脚本

### TAIGregorian

TAI 时间系统、公历格式的航天器轨道历元。

- 数据类型：字符串（String）
- 允许值：参见 `Epoch`
- 访问权限：可设置、可读取（读取仅限任务序列）
- 默认值：01 Jan 2000 12:00:00.000
- 单位：公历日期（Gregorian date）
- 接口：GUI、脚本

### TAIModJulian

TAI 时间系统、修正儒略格式的航天器轨道历元。

- 数据类型：字符串（String）
- 允许值：参见 `Epoch`
- 访问权限：可设置、可读取（读取仅限任务序列）
- 默认值：21545
- 单位：参见 A1ModJulian
- 接口：GUI、脚本

### TDBGregorian

TDB 时间系统、公历格式的航天器轨道历元。

- 数据类型：字符串（String）
- 允许值：参见 `Epoch`
- 访问权限：可设置、可读取（读取仅限任务序列）
- 默认值：01 Jan 2000 12:00:32.184
- 单位：参见 A1Gregorian
- 接口：GUI、脚本

### TDBModJulian

TDB 时间系统、修正儒略格式的航天器轨道历元。

- 数据类型：字符串（String）
- 允许值：参见 `Epoch`
- 访问权限：可设置、可读取（读取仅限任务序列）
- 默认值：21545.00037249916
- 单位：参见 A1ModJulian
- 接口：GUI、脚本

### TTGregorian

TT 时间系统、公历格式的航天器轨道历元。

- 数据类型：字符串（String）
- 允许值：参见 `Epoch`
- 访问权限：可设置、可读取（读取仅限任务序列）
- 默认值：01 Jan 2000 12:00:32.184
- 单位：参见 A1Gregorian
- 接口：GUI、脚本

### TTModJulian

TT 时间系统、修正儒略格式的航天器轨道历元。

- 数据类型：字符串（String）
- 允许值：参见 `Epoch`
- 访问权限：可设置、可读取（读取仅限任务序列）
- 默认值：21545.0003725
- 单位：参见 A1ModJulian
- 接口：GUI、脚本

### UTCGregorian

UTC 时间系统、公历格式的航天器轨道历元。

- 数据类型：字符串（String）
- 允许值：参见 `Epoch`
- 访问权限：可设置、可读取（读取仅限任务序列）
- 默认值：01 Jan 2000 11:59:28.000
- 单位：参见 A1Gregorian
- 接口：GUI、脚本

### UTCModJulian

UTC 时间系统、修正儒略格式的航天器轨道历元。

- 数据类型：字符串（String）
- 允许值：参见 `Epoch`
- 访问权限：可设置、可读取（读取仅限任务序列）
- 默认值：21544.99962962963
- 单位：参见 A1ModJulian
- 接口：GUI、脚本

## GUI

> [图：航天器轨道/历元资源的 GUI 默认界面（Resource_SpacecraftOrbit_Default.png）]

更改 `EpochFormat` 会使 `Epoch` 立即更新，以反映所选的时间系统和格式。

## 备注

GMAT 支持五种时间系统（时间尺度）和两种格式：

| 时间系统 | 说明 |
|---|---|
| A.1 | USNO（美国海军天文台）原子时；GMAT 的内部时间系统 |
| TAI | 国际原子时（International Atomic Time） |
| TDB | 质心力学时（Barycentric Dynamical Time） |
| TT | 地球时（Terrestrial Time） |
| UTC | 协调世界时（Coordinated Universal Time） |

| 格式 | 说明 |
|---|---|
| Gregorian（公历） | 文本，格式为：`dd mmm yyyy HH:MM:SS.FFF`。其中 `dd`＝两位月份日；`mmm`＝月份英文名称的前三个字母；`yyyy`＝四位年份；`HH`＝两位小时；`MM`＝两位分钟；`SS`＝两位秒；`FFF`＝三位秒的小数部分 |
| Modified Julian（修正儒略） | 自参考历元起算的浮点天数。在 GMAT 中，参考历元为 1941 年 1 月 5 日 12:00:00.000（JD 2430000.0） |

历元必须以两种不同的方式设置，取决于它是在对象创建时（`BeginMissionSequence` 之前）还是在任务序列中（`BeginMissionSequence` 之后）设置。在对象创建时，必须先将 `DateFormat` 字段设置为所需的时间系统和格式，然后将 `Epoch` 字段设置为所需的历元。此方法不能用于读取历元值（例如在任务序列中赋值语句的右侧）。

```
aSat.DateFormat = UTCGregorian
aSat.Epoch = '18 May 2012 12:00:00.000'
```

上述脚本先将时间格式设为 UTC 公历，再设置历元。

在任务序列中（即 `BeginMissionSequence` 命令之后），必须通过指定与所赋历元关联的特定时间格式参数来设置历元，如下所示。此语法也用于在任务序列中"读取"当前航天器历元。

```
aSat.UTCGregorian = '18 May 2012 12:00:00.000'
Report aReport aSat.UTCGregorian
```

上述脚本设置历元并通过报告输出该历元。

GMAT 内部计算使用修正儒略格式的 A.1 时间系统。系统在输入时将所有其他时间系统和格式转换为内部格式，并在输出时再次转换。

### 闰秒（Leap Seconds）

在与 UTC 时间系统相互转换时，GMAT 会根据 IERS（国际地球自转服务）的 `tai-utc.dat` 数据文件适当地计入闰秒。该文件包含 TAI 与 UTC 之间的转换关系，包括所有已经添加或已宣布的闰秒。

GMAT 将闰秒应用为 `tai-utc.dat` 文件中所列日期之前的最后一秒；历史上该日期一直是 1 月 1 日或 7 月 1 日。在公历日期格式中，闰秒显示为"第 60 秒"：例如"31 Dec 2008 23:59:60.000"。引自国际天文学联合会基本天文学标准（SOFA）"时间尺度与历法工具"文档："*注意，如果要正确地考虑闰秒，UTC 必须以时、分、秒（或至少以给定日中的秒数）来表示*。特别地，将 UTC 表示为儒略日期是不合适的，因为在闰秒期间会产生歧义——例如 1994 年 6 月 30 日 23:59:60.0 和 1994 年 7 月 1 日 00:00:00.0 都会得出 MJD 49534.00000；并且对这样的两个 JD 作减法，在包含闰秒的情形下无法得出正确的时间间隔。"因此，我们不建议使用 UTC 修正儒略系统，并建议在需要 UTC 时间系统时使用 UTC 公历格式（UTC Gregorian）。

对于早于闰秒文件第一个条目的历元，UTC 和 TAI 时间系统被视为相同（即添加零个闰秒）。对于晚于最后一个条目的历元，使用最后一个条目对应的闰秒计数。

`tai-utc.dat` 文件由 IERS 在宣布新闰秒时定期更新。该文件的最新版本始终可以在 http://maia.usno.navy.mil/ser7/tai-utc.dat 找到。要替换它，请下载最新版本，并替换 GMAT 中位于 `<GMAT>/data/time/tai-utc.dat` 的文件，其中 `<GMAT>` 是 GMAT 在您系统上的安装目录。

## 示例

设置用于传播的历元：

```
Create Spacecraft aSat
aSat.DateFormat = TAIModJulian
aSat.Epoch      = 25562.5

Create ForceModel aFM
Create Propagator aProp
aProp.FM = aFM

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1}
```

上述脚本创建航天器并以 TAI 修正儒略格式设置历元，然后传播 1 天。

绘制并报告历元（语法 #1）：

```
Create Spacecraft aSat
aSat.DateFormat = A1Gregorian
aSat.Epoch      = '12 Jul 2015 08:21:45.921'

Create XYPlot aPlot
aPlot.XVariable  = aSat.UTCModJulian
aPlot.YVariables = aSat.Earth.Altitude

Create Report aReport
aReport.Add = {aSat.UTCGregorian, aSat.EarthMJ2000Eq.ECC}
```

上述脚本以 A1 公历格式设置历元，绘制高度随 UTC 修正儒略历元变化的曲线，并报告 UTC 公历历元与偏心率。

绘制并报告历元（语法 #2）：

```
Create Spacecraft aSat
aSat.DateFormat = TTGregorian
aSat.Epoch      = '01 Dec 1978 00:00:00.000'

Create XYPlot aPlot
aPlot.XVariable  = aSat.TTModJulian
aPlot.YVariables = aSat.Earth.RMAG

Create Report aReport
aReport.Add = {aSat.A1Gregorian, aSat.Earth.RMAG}
```

上述脚本以 TT 公历格式设置历元，绘制位置矢量模随 TT 修正儒略历元变化的曲线，并报告 A1 公历历元与位置矢量模。
