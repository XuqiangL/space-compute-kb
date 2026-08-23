# 质心（Barycenter）
> 译自 GMAT R2026a 帮助文档 Barycenter.html

**Barycenter** —— 一组选定天体的质心。

## 描述

`Barycenter`（质心）是一组天体的质量中心。GMAT 包含两个质心资源：内置的 `SolarSystemBarycenter`（太阳系质心）资源，以及允许你构建自定义 `Barycenter`（如地月质心）的 `Barycenter` 资源。该资源不能在任务序列（Mission Sequence）中修改。

**另请参阅**：LibrationPoint（天平动点）、CoordinateSystem（坐标系）、CelestialBody（天体）、SolarSystem（太阳系）、Color（颜色）

## 字段

| 字段 | 描述 |
|------|------|
| **BodyNames** | 包含在该质心中的 `CelestialBody`（天体）资源列表。提供空括号会将天体设置为下文所述的默认列表。<br>数据类型：字符串数组<br>允许值：天体数组。你不能向内置的 `SolarSystemBarycenter` 资源添加天体。一个 `CelestialBody` 在 `BodyNames` 列表中只能出现一次。<br>访问权限：set<br>默认值：`Earth`、`Luna`<br>单位：N/A<br>接口：GUI、脚本 |
| **OrbitColor** | 允许你为用户定义的 `Barycenter` 对象轨道设置可用颜色。质心轨道使用 `OrbitView` 图形资源绘制。`Barycenter` 对象的颜色可以通过字符串或整数数组设置。例如：将质心轨道颜色设为红色可以用以下两种方式：`Barycenter.OrbitColor = Red` 或 `Barycenter.OrbitColor = [255 0 0]`。该字段也可以在任务序列中修改。<br>数据类型：整数数组或字符串<br>允许值：GUI 轨道颜色选择器（Orbit Color Picker）中可用的任何颜色。有效的预定义颜色名称，或 0 到 255 之间的 RGB 三元组值。<br>访问权限：set<br>默认值：GreenYellow<br>单位：N/A<br>接口：GUI、脚本 |
| **TargetColor** | 允许你为 `Barycenter` 对象在差分修正（Differential Correction）或优化（Optimization）等迭代过程中绘制的受扰轨道轨迹选择可用颜色。目标颜色可以通过字符串或整数数组指定。例如：将质心受扰轨迹颜色设为黄色可以用以下两种方式：`Barycenter.TargetColor = Yellow` 或 `Barycenter.TargetColor = [255 255 0]`。该字段也可以在任务序列中修改。<br>数据类型：整数数组或字符串<br>允许值：GUI 轨道颜色选择器中可用的任何颜色。有效的预定义颜色名称，或 0 到 255 之间的 RGB 三元组值。<br>访问权限：set<br>默认值：DarkGray<br>单位：N/A<br>接口：GUI、脚本 |

## GUI

> [图：Barycenter 对话框，默认配置包含 Earth 和 Luna]

`Barycenter` 对话框允许你定义自定义 `Barycenter` 中包含的天体。所有天体（包括用户自定义天体）都可用于 `Barycenter`，并出现在 **Available Bodies**（可用天体）列表或 **Selected Bodies**（已选天体）列表中。上图示例展示了默认配置，其中包含 **Earth** 和 **Luna**。

> [图：SolarSystemBarycenter 对话框]

上图所示的 `SolarSystemBarycenter` 对话框是内置对象，你不能修改其配置。有关 `SolarSystemBarycenter` 模型的详细信息，请参阅"备注"一节。

## 备注

**内置 SolarSystemBarycenter 对象**

内置的 `SolarSystemBarycenter` 使用 `SolarSystem.EphemerisSource` 字段中选择的历表进行建模。例如，如果你为 `SolarSystem.EphemerisSource` 选择了 `DE421`，则质心位置通过调用 DE421 历表例程计算。对于 DE 和 SPICE 历表，太阳系质心的模型包括行星以及数百颗小行星。注意，你不能向 `SolarSystemBarycenter` 添加天体。

**自定义质心对象**

你可以使用 `Barycenter` 资源创建自定义质心。`Barycenter` 的位置和速度是所包含天体位置和速度的质量加权平均。在下式中，*m*ᵢ、*r*ᵢ 和 *v*ᵢ 分别为质心中第 *i* 个天体的质量、位置和速度，*r*ᵦ 和 *v*ᵦ 分别为质心的位置和速度。

> [图：质心位置方程 *r*ᵦ = Σ(*m*ᵢ*r*ᵢ)/Σ(*m*ᵢ)]

> [图：质心速度方程 *v*ᵦ = Σ(*m*ᵢ*v*ᵢ)/Σ(*m*ᵢ)]

### 设置质心轨道的颜色

GMAT 允许你为使用 `OrbitView` 图形资源绘制的质心轨道指定颜色。GMAT 还允许你为在差分修正或优化等迭代过程中绘制的受扰质心轨道轨迹指定颜色。`Barycenter` 对象的 `OrbitColor` 和 `TargetColor` 字段用于为轨道轨迹和受扰轨迹指定颜色。请参阅"字段"一节了解这两个字段的更多信息。另请参阅 Color（颜色）文档，其中讨论了如何设置质心轨道颜色并给出了示例。

## 示例

在 `SolarSystemBarycenter` 坐标中定义航天器的状态。

```
Create CoordinateSystem SSB
SSB.Origin = SolarSystemBarycenter
SSB.Axes   = MJ2000Eq

Create ReportFile aReport

Create Spacecraft aSpacecraft
aSpacecraft.CoordinateSystem = SSB
aSpacecraft.X  = -27560491.88656896
aSpacecraft.Y  = 132361266.8009069
aSpacecraft.Z  = 57419875.95483227
aSpacecraft.VX = -29.78491261798486
aSpacecraft.VY = 2.320067257851091
aSpacecraft.VZ = -1.180722388963864

BeginMissionSequence

Report aReport aSpacecraft.EarthMJ2000Eq.X aSpacecraft.EarthMJ2000Eq.Y ...                
             aSpacecraft.EarthMJ2000Eq.Z 
```

说明：创建一个原点为太阳系质心、轴系为 MJ2000Eq 的坐标系 SSB，在该坐标系中给定航天器初始状态，然后在内置的 EarthMJ2000Eq 坐标系（地球 MJ2000 赤道惯性系）中报告其位置分量。

在 `SolarSystemBarycenter` 坐标中报告航天器的状态。

```
Create CoordinateSystem SSB
SSB.Origin = SolarSystemBarycenter
SSB.Axes   = MJ2000Eq

Create Spacecraft aSpacecraft
Create ReportFile aReport

BeginMissionSequence

Report aReport aSpacecraft.SSB.X aSpacecraft.SSB.Y aSpacecraft.SSB.Z ...
      aSpacecraft.SSB.VX aSpacecraft.SSB.VY aSpacecraft.SSB.VZ
```

说明：通过 `aSpacecraft.SSB.X` 这种"对象.坐标系.分量"语法，直接输出航天器在 SSB 坐标系中的位置和速度分量。

创建一个地月 `Barycenter`，并将其用于日-地月 `LibrationPoint`（天平动点）。

```
Create Barycenter EarthMoonBary
EarthMoonBary.BodyNames = {Earth,Luna}

Create LibrationPoint SunEarthMoonL2
SunEarthMoonL2.Primary   = Sun
SunEarthMoonL2.Secondary = EarthMoonBary
SunEarthMoonL2.Point     = L2

Create CoordinateSystem SEML2Coordinates
SEML2Coordinates.Origin = SunEarthMoonL2
SEML2Coordinates.Axes   = MJ2000Eq

Create Spacecraft aSpacecraft
aSpacecraft.DateFormat = UTCGregorian
aSpacecraft.Epoch = '09 Dec 2005 13:00:00.000'
aSpacecraft.CoordinateSystem = SEML2Coordinates
aSpacecraft.X  = -32197.88223741966
aSpacecraft.Y  = 211529.1500044117
aSpacecraft.Z  = 44708.57017366499
aSpacecraft.VX = 0.03209516489451751
aSpacecraft.VY = 0.06086386504053736
aSpacecraft.VZ = 0.0550442738917212

Create ReportFile aReport

BeginMissionSequence

Report aReport aSpacecraft.EarthMJ2000Eq.X aSpacecraft.EarthMJ2000Eq.Y ...                
             aSpacecraft.EarthMJ2000Eq.Z 
```

说明：先创建包含地球和月球的地月质心 EarthMoonBary，再以太阳为主天体、地月质心为次天体定义日-地月 L2 天平动点，并以该点为原点建立坐标系，最后在该坐标系中定义航天器状态并输出报告。
