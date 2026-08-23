# 天平动点（LibrationPoint）
> 译自 GMAT R2026a 帮助文档 LibrationPoint.html

**LibrationPoint** —— 圆型限制性三体问题中的平衡点。

## 描述

`LibrationPoint`（天平动点，又称拉格朗日点）是圆型限制性三体问题（CRTBP）中的平衡点。共有五个天平动点，其中三个在 CRTBP 意义下是不稳定的，两个是稳定的。有关不同天平动点的详细解释以及在 GMAT 中配置常见天平动点区域的示例，请参阅下文的讨论。该资源不能在任务序列（Mission Sequence）中修改。

**另请参阅**：Barycenter（质心）、Color（颜色）

## 字段

| 字段 | 描述 |
|------|------|
| **OrbitColor** | 允许你为用户定义的 `LibrationPoint` 轨道设置可用颜色。天平动点轨道使用 3D `OrbitView` 图形显示绘制。`LibrationPoint` 对象的颜色可以通过字符串或整数数组设置。例如：将天平动点轨道颜色设为红色可以用以下两种方式：`LibrationPoint.OrbitColor = Red` 或 `LibrationPoint.OrbitColor = [255 0 0]`。该字段也可以在任务序列中修改。<br>数据类型：整数数组或字符串<br>允许值：GUI 轨道颜色选择器（Orbit Color Picker）中可用的任何颜色。有效的预定义颜色名称，或 0 到 255 之间的 RGB 三元组值。<br>访问权限：set<br>默认值：GreenYellow<br>单位：N/A<br>接口：GUI、脚本 |
| **Point** | 天平动点编号。<br>数据类型：字符串<br>允许值：`L1`、`L2`、`L3`、`L4` 或 `L5`<br>访问权限：set<br>默认值：`L1`<br>单位：N/A<br>接口：GUI、脚本 |
| **Primary** | 主天体或主质心。<br>数据类型：字符串<br>允许值：`CelestialBody`（天体）或 `Barycenter`（质心）。`Primary` 不能是 `SolarSystemBarycenter`，且 `Primary` 不能与 `Secondary` 相同。<br>访问权限：set<br>默认值：`Sun`<br>单位：N/A<br>接口：GUI、脚本 |
| **Secondary** | 次天体或次质心。<br>数据类型：字符串<br>允许值：`CelestialBody` 或 `Barycenter`。`Secondary` 不能是 `SolarSystemBarycenter`，且 `Primary` 不能与 `Secondary` 相同。<br>访问权限：set<br>默认值：`Earth`<br>单位：N/A<br>接口：GUI、脚本 |
| **TargetColor** | 允许你为 `LibrationPoint` 对象在差分修正（Differential Correction）或优化（Optimization）等迭代过程中绘制的受扰轨道轨迹设置可用颜色。目标颜色可以通过字符串或整数数组指定。例如：将天平动点受扰轨迹颜色设为黄色可以用以下两种方式：`LibrationPoint.TargetColor = Yellow` 或 `LibrationPoint.TargetColor = [255 255 0]`。该字段也可以在任务序列中修改。<br>数据类型：整数数组或字符串<br>允许值：GUI 轨道颜色选择器中可用的任何颜色。有效的预定义颜色名称，或 0 到 255 之间的 RGB 三元组值。<br>访问权限：set<br>默认值：DarkGray<br>单位：N/A<br>接口：GUI、脚本 |

## GUI

> [图：LibrationPoint 对话框，含主天体、次天体和天平动点编号选择]

`LibrationPoint` 对话框允许你选择 **Primary Body**（主天体）、**Secondary Body**（次天体）以及天平动点编号。你可以从天体和质心中进行选择。你不能将 `SolarSystemBarycenter` 选为 `Primary` 或 `Secondary`，并且 `Primary` 和 `Secondary` 不能是同一个对象。

## 备注

**天平动点几何概述**

`LibrationPoint`（天平动点，又称拉格朗日点）是圆型限制性三体问题（CRTBP）中的平衡点。下图说明了 GMAT 中使用的天平动点定义，其中 `Primary`（主天体）和 `Secondary`（次天体）显示在一个旋转坐标系中，该坐标系的 x 轴由 `Primary` 指向 `Secondary`。GMAT 针对完整历表问题进行配置，计算天平动点位置时假定：在给定时刻，可以使用 Lagrange 和 Szebehely 建立的 CRTBP 理论，利用 JPL 历表中主天体和次天体的位置来计算天平动点的位置。三个共线点（L1、L2 和 L3）是不稳定的（即使在 CRTBP 中也是如此），而三角点（L4 和 L5）在 CRTBP 中是稳定的。

> [图：天平动点几何示意图，显示旋转系中 L1~L5 的位置]

**配置天平动点**

GMAT 允许你将 `Primary` 和/或 `Secondary` 定义为 `CelestialBody`（天体）或 `Barycenter`（质心）（`SolarSystemBarycenter` 除外）。这使你可以将 `Primary` 设为太阳、`Secondary` 设为地月质心，从而对日-地-月天平动点进行建模。详见下文示例。

### 设置天平动点轨道的颜色

GMAT 允许你为使用 `OrbitView` 图形显示窗口绘制的天平动点轨道指定颜色。GMAT 还允许你为在差分修正或优化等迭代过程中绘制的受扰天平动点轨道轨迹指定颜色。`LibrationPoint` 对象的 `OrbitColor` 和 `TargetColor` 字段用于为轨道轨迹和受扰轨迹指定颜色。请参阅"字段"一节了解这两个字段的更多信息。另请参阅 Color（颜色）文档，其中讨论了如何设置天平动点轨道颜色并给出了示例。

## 示例

创建并使用地月 `LibrationPoint`。

```
%  Create the libration point and rotating libration point coordinate system
Create LibrationPoint EarthMoonL2
EarthMoonL2.Primary   = Earth
EarthMoonL2.Secondary = Luna
EarthMoonL2.Point     = L2

Create CoordinateSystem EarthMoonRotLibCoord
EarthMoonRotLibCoord.Origin    = EarthMoonL2
EarthMoonRotLibCoord.Axes      = ObjectReferenced
EarthMoonRotLibCoord.XAxis     = R
EarthMoonRotLibCoord.ZAxis     = N
EarthMoonRotLibCoord.Primary   = Earth
EarthMoonRotLibCoord.Secondary = Luna

%  Configure the spacecraft and propagator
Create Spacecraft aSat
aSat.DateFormat       = TAIModJulian
aSat.Epoch            = '25220.0006220895'
aSat.CoordinateSystem = EarthMoonRotLibCoord
aSat.DisplayStateType = Cartesian
aSat.X  = 9999.752137149568
aSat.Y  = 1.774296833900735e-007
aSat.Z  = 21000.02640446094
aSat.VX = -1.497748388797418e-005
aSat.VY = -0.2087816321971509
aSat.VZ = -5.42471673237177e-006

Create ForceModel EarthMoonL2Prop_ForceModel
EarthMoonL2Prop_ForceModel.PointMasses = {Earth, Luna, Sun}
Create Propagator EarthMoonL2Prop
EarthMoonL2Prop.FM = EarthMoonL2Prop_ForceModel

%  Create the orbit view
Create OrbitView ViewEarthMoonRot
ViewEarthMoonRot.Add                = {Earth, Luna, Sun,...
                                            aSat, EarthMoonL2}
ViewEarthMoonRot.CoordinateSystem   = EarthMoonRotLibCoord
ViewEarthMoonRot.ViewPointReference = EarthMoonL2
ViewEarthMoonRot.ViewDirection      = EarthMoonL2
ViewEarthMoonRot.ViewScaleFactor    = 5

Create Variable I

BeginMissionSequence

% Prop for 3 xz-plane crossings
For I = 1:3
  Propagate 'Prop to Y Crossing' EarthMoonL2Prop(aSat) ...
                      {aSat.EarthMoonRotLibCoord.Y = 0}
EndFor
```

说明：创建地月 L2 天平动点，并以该点为原点、以 ObjectReferenced（对象参考）轴系建立旋转天平动点坐标系；在该坐标系中定义航天器状态并传播，直到航天器三次穿越该坐标系的 xz 平面（Y = 0）。

创建并使用日-地月 `LibrationPoint`。

```
%  Create the Earth-Moon Barycenter and Libration Point
Create Barycenter EarthMoonBary
EarthMoonBary.BodyNames = {Earth,Luna}

Create LibrationPoint SunEarthMoonL1
SunEarthMoonL1.Primary   = Sun
SunEarthMoonL1.Secondary = EarthMoonBary
SunEarthMoonL1.Point     = L1

%  Create the coordinate system
Create CoordinateSystem RotatingSEML1Coord
RotatingSEML1Coord.Origin    = SunEarthMoonL1
RotatingSEML1Coord.Axes      = ObjectReferenced
RotatingSEML1Coord.XAxis     = R
RotatingSEML1Coord.ZAxis     = N
RotatingSEML1Coord.Primary   = Sun
RotatingSEML1Coord.Secondary = EarthMoonBary

%  Create the spacecraft and propagator
Create Spacecraft aSpacecraft
aSpacecraft.DateFormat       = UTCGregorian
aSpacecraft.Epoch            = '09 Dec 2005 13:00:00.000'
aSpacecraft.CoordinateSystem = RotatingSEML1Coord
aSpacecraft.X  = -32197.88223741966
aSpacecraft.Y  = 211529.1500044117
aSpacecraft.Z  = 44708.57017366499
aSpacecraft.VX = 0.03209516489451751
aSpacecraft.VY = 0.06100386504053736
aSpacecraft.VZ = 0.0550442738917212

Create Propagator aPropagator
aPropagator.FM           = aForceModel
aPropagator.MaxStep = 86400
Create ForceModel aForceModel
aForceModel.PointMasses = {Earth,Sun,Luna}

% Create a 3-D graphic
Create OrbitView anOrbitView
anOrbitView.Add                     = {aSpacecraft,  Earth, Sun, Luna}
anOrbitView.CoordinateSystem        = RotatingSEML1Coord
anOrbitView.ViewPointReference      = SunEarthMoonL1
anOrbitView.ViewPointVector         = [-1500000 0 0 ]
anOrbitView.ViewDirection           = SunEarthMoonL1
anOrbitView.ViewUpCoordinateSystem = RotatingSEML1Coord
anOrbitView.Axes                    = Off
anOrbitView.XYPlane                 = Off

BeginMissionSequence
           
Propagate aPropagator(aSpacecraft, {aSpacecraft.ElapsedDays = 180})
```

说明：先创建地月质心 EarthMoonBary，再以太阳为主天体、地月质心为次天体定义日-地月 L1 天平动点；建立相应的旋转坐标系并定义航天器，传播 180 天并在三维视图中显示。
