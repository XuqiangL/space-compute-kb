# 事件查找（FindEvents）
> 译自 GMAT R2026a 帮助文档 FindEvents.html

**FindEvents** —— 执行事件定位搜索。

## 脚本语法

```
FindEvents Locator [{Append = true|false}]
```

## 描述

`FindEvents` 命令执行由事件定位资源（`ContactLocator`（可见性分析器）或 `EclipseLocator`（食分析器））定义的事件定位搜索。如果已配置，搜索将生成一份基于文本的事件报告。

对于大多数简单的事件定位搜索，并不需要显式的 `FindEvents` 命令。如果定位资源配置为 `RunMode` = `'Automatic'`，`FindEvents` 会在任务序列末尾自动执行。手动执行该命令最有用的场景是：为任务的某一部分生成自定义搜索，或根据任务数据更改搜索区间。

`Append` 选项用于配置报告文件的写入方式。如果 `Append` 为 true，新报告将追加到现有文件的末尾。如果 `Append` 为 false，将替换旧文件。注意，如果 `Append` 为 true，报告可能会被追加到在当前 GMAT 会话之前就已存在的文件中。

**另请参阅**：ContactLocator（可见性分析器）、EclipseLocator（食分析器）

## 选项

| 选项 | 描述 |
|------|------|
| **Locator** | 要执行的事件定位器。<br>接受的数据类型：`ContactLocator`、`EclipseLocator`<br>允许值：任何有效的 `ContactLocator` 或 `EclipseLocator` 资源<br>默认值：无<br>是否必需：是<br>接口：GUI、脚本 |
| **Append** | 追加到现有事件报告（为 true 时）或替换它（为 false 时）。<br>接受的数据类型：布尔值<br>允许值：`true`、`false`<br>默认值：false<br>是否必需：否<br>接口：GUI、脚本 |

## GUI

> [图：FindEvents 命令面板，含事件定位器列表和 Append 复选框]

`FindEvents` GUI 面板非常简单。从 **Event Locator**（事件定位器）列表中选择要执行的事件定位器，该列表由所有现有的 `EclipseLocator` 和 `ContactLocator` 资源填充。要追加报告（如果生成了报告），请勾选 **Append** 复选框。

## 备注

### 在循环中使用 FindEvents

`FindEvents` 命令可以在 `For` 和 `While` 等循环内使用，但不能在求解器序列（如 `Target` 和 `Optimize`）内使用。要基于求解器序列的结果执行事件定位，请将 `FindEvents` 命令放在该序列之后。

当 `FindEvents` 在循环内使用时，有几个潜在问题需要注意。下面的代码片段说明了其中的几个问题。

```
Create EclipseLocator ec
ec.Spacecraft = sat
ec.OccultingBodies = {Mercury, Venus, Earth, Luna, Mars, Phobos, Deimos}
ec.Filename = 'ForLoop.report'
ec.InputEpochFormat = TAIGregorian

% Prevents automatic execution at end of mission
ec.RunMode = 'Manual'

% Lets us manually control search intervals
ec.UseEntireInterval = false

BeginMissionSequence

% Execute FindEvents once before loop, to clear
% out any existing file.
ec.InitialEpoch = sat.TAIGregorian
Propagate prop(sat) {sat.ElapsedSecs = 2400}
ec.FinalEpoch = sat.TAIGregorian
FindEvents ec {Append = false}

% Main loop
For I = 1:1:71
    % Set initial epoch of search to current epoch
    ec.InitialEpoch = sat.TAIGregorian
    % Propagate
    Propagate prop(sat) {sat.ElapsedSecs = 2400}
    % Set final epoch of search to new epoch
    ec.FinalEpoch = sat.TAIGregorian
    % Execute search, appending to file
    FindEvents ec {Append = true}
EndFor
```

说明：将 `RunMode` 设为 `'Manual'` 以防止任务末尾自动执行；将 `UseEntireInterval` 设为 false 以便手动控制搜索区间；在循环前先执行一次 `FindEvents ec {Append = false}` 以清除任何已存在的文件；在主循环中，每次迭代都把搜索起始历元设为当前历元、传播 2400 秒、把搜索结束历元设为新历元，并以追加方式执行搜索。

## 示例

在 LEO（近地轨道）中执行基本的食搜索。

```
SolarSystem.EphemerisSource = 'DE421'

Create Spacecraft sat
sat.DateFormat = UTCGregorian
sat.Epoch = '15 Sep 2010 16:00:00.000'
sat.CoordinateSystem = EarthMJ2000Eq
sat.DisplayStateType = Keplerian
sat.SMA = 6678.14
sat.ECC = 0.001
sat.INC = 0
sat.RAAN = 0
sat.AOP = 0
sat.TA = 180

Create ForceModel fm
fm.CentralBody = Earth
fm.PrimaryBodies = {Earth}
fm.GravityField.Earth.PotentialFile = 'JGM2.cof'
fm.GravityField.Earth.Degree = 0
fm.GravityField.Earth.Order = 0
fm.GravityField.Earth.TideModel = 'None'
fm.Drag.AtmosphereModel = None
fm.PointMasses = {}
fm.RelativisticCorrection = Off
fm.SRP = Off

Create Propagator prop
prop.FM = fm
prop.Type = RungeKutta89

Create EclipseLocator el
el.Spacecraft = sat
el.Filename = 'Simple.report'
el.OccultingBodies = {Earth}
el.EclipseTypes = {'Umbra', 'Penumbra', 'Antumbra'}
el.RunMode = 'Manual'

BeginMissionSequence

Propagate prop(sat) {sat.ElapsedSecs = 10800}

FindEvents el
```

说明：创建一颗近地轨道卫星和只考虑地球点质量的力模型，配置一个以地球为掩食天体、搜索本影（Umbra）/半影（Penumbra）/伪本影（Antumbra）三类食的食分析器，并设为手动运行模式；传播 10800 秒后显式执行 `FindEvents el` 进行食搜索。

在循环中执行 FindEvents，每次追加报告：

```
SolarSystem.EphemerisSource = 'SPICE'
SolarSystem.SPKFilename = 'de421.bsp'

Create Spacecraft sat
sat.DateFormat = UTCGregorian
sat.Epoch = '10 May 1984 00:00:00.000'
sat.CoordinateSystem = MarsMJ2000Eq
sat.DisplayStateType = Keplerian
sat.SMA = 6792.38
sat.ECC = 0
sat.INC = 45
sat.RAAN = 0
sat.AOP = 0
sat.TA = 0

Create ForceModel fm
fm.CentralBody = Mars
fm.PrimaryBodies = {Mars}
fm.GravityField.Mars.PotentialFile = 'Mars50c.cof'
fm.GravityField.Mars.Degree = 0
fm.GravityField.Mars.Order = 0
fm.Drag.AtmosphereModel = None
fm.PointMasses = {}
fm.RelativisticCorrection = Off
fm.SRP = Off

Create Propagator prop
prop.FM = fm
prop.Type = RungeKutta89

Create CoordinateSystem MarsMJ2000Eq
MarsMJ2000Eq.Origin = Mars
MarsMJ2000Eq.Axes = MJ2000Eq

Create Moon Phobos
Phobos.CentralBody = 'Mars'
Phobos.PosVelSource = 'SPICE'
Phobos.NAIFId = 401
Phobos.OrbitSpiceKernelName = {'mar063.bsp'}
Phobos.SpiceFrameId = 'IAU_PHOBOS'
Phobos.EquatorialRadius = 13.5
Phobos.Flattening = 0.3185185185185186
Phobos.Mu = 7.093399e-004

Create Moon Deimos
Deimos.CentralBody = 'Mars'
Deimos.PosVelSource = 'SPICE'
Deimos.NAIFId = 402
Deimos.OrbitSpiceKernelName = {'mar063.bsp'}
Deimos.SpiceFrameId = 'IAU_DEIMOS'
Deimos.EquatorialRadius = 7.5
Deimos.Flattening = 0.30666666666666664
Deimos.Mu = 1.588174e-004

Create EclipseLocator ec
ec.Spacecraft = sat
ec.OccultingBodies = {Mercury, Venus, Earth, Luna, Mars, Phobos, Deimos}
ec.Filename = 'ForLoop.report'
ec.RunMode = 'Manual'
ec.UseEntireInterval = false
ec.InputEpochFormat = TAIGregorian

Create Variable I

BeginMissionSequence

ec.InitialEpoch = sat.TAIGregorian
Propagate prop(sat) {sat.ElapsedSecs = 2400}
ec.FinalEpoch = sat.TAIGregorian
FindEvents ec {Append = false}

For I = 1:1:71
    ec.InitialEpoch = sat.TAIGregorian
    Propagate prop(sat) {sat.ElapsedSecs = 2400}
    ec.FinalEpoch = sat.TAIGregorian
    FindEvents ec {Append = true}
EndFor
```

说明：火星轨道器示例。使用 SPICE 历表并定义火卫一（Phobos）、火卫二（Deimos）；食分析器设为手动模式并关闭整区间搜索；循环中每传播 2400 秒执行一次搜索，除第一次（`Append = false`，用于清空旧文件）外均以追加方式写入报告。

在循环中执行 FindEvents，分阶段执行搜索但不追加：

```
Create Spacecraft sat
sat.DateFormat = UTCGregorian
sat.Epoch = '1 Mar 2016 12:00:00.000'
sat.CoordinateSystem = EarthMJ2000Eq
sat.DisplayStateType = Keplerian
sat.SMA = 42164
sat.ECC = 0
sat.INC = 0
sat.RAAN = 0
sat.AOP = 0
sat.TA = 0

Create ForceModel fm
fm.CentralBody = Earth
fm.PrimaryBodies = {Earth}
fm.GravityField.Earth.PotentialFile = 'JGM2.cof'
fm.GravityField.Earth.Degree = 0
fm.GravityField.Earth.Order = 0
fm.GravityField.Earth.TideModel = 'None'
fm.Drag.AtmosphereModel = None
fm.PointMasses = {}
fm.RelativisticCorrection = Off
fm.SRP = Off

Create Propagator prop
prop.FM = fm
prop.Type = RungeKutta89
prop.MaxStep = 2700

Create EclipseLocator ec
ec.Spacecraft = sat
ec.OccultingBodies = {Mercury, Venus, Earth, Luna}
ec.Filename = 'WhileLoop.report'
ec.RunMode = 'Manual'

SolarSystem.EphemerisSource = 'DE421'

BeginMissionSequence

While sat.UTCModJulian <= 27480
    Propagate prop(sat) {sat.ElapsedSecs = 28800}
    FindEvents ec {Append = false}
EndWhile
```

说明：地球同步轨道卫星示例。在 `While` 循环中，每传播 28800 秒执行一次 `FindEvents`，且每次都用 `Append = false` 替换报告文件，因此报告始终只包含最近一次搜索区间的结果。
