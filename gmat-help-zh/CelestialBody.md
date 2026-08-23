# 天体（CelestialBody）

> 译自 GMAT R2026a 帮助文档 CelestialBody.html

**CelestialBody** —— 用于建模 Moon（卫星）、Planet（行星）、Asteroid（小行星）和 Comet（彗星）对象。

## 描述

> **注意**：并不存在名为 CelestialBody 的资源。用户必须创建 **Moon**、**Planet**、**Asteroid** 或 **Comet** 的实例，如下面的示例所示。所有这些对象的用户界面参数完全相同，在下表中统一说明。

**Moon**、**Planet**、**Asteroid** 和 **Comet** 资源用于建模一个天体，包含物理属性设置以及轨道运动和自转定向模型。GMAT 内置了太阳、八大行星、地球月球（Luna）和冥王星的模型。你可以创建自定义资源来建模行星、小行星、彗星或卫星。该资源不能在任务序列（Mission Sequence）中被修改。

**另请参阅**：SolarSystem、Barycenter、LibrationPoint、CoordinateSystem、Color

> **警告**：创建新的 **Moon**、**Planet**、**Asteroid** 或 **Comet** 时，**Mu**、**EquatorialRadius**、**Flattening**、**SpinAxisRAConstant**、**SpinAxisRARate**、**SpinAxisDECConstant**、**SpinAxisDECRate**、**RotationConstant**、**RotationRate** 的默认值全部设为 0。这些参数与用户自定义天体的重力建模和地面站布设有关，因此需要时用户应赋予合适的值。如果不需要非球形重力和形状建模，天体姿态与形状参数可以不设置。

## 字段

| 字段 | 描述 |
|------|------|
| **3DModelFile** | 允许你为天体加载 3D 模型。模型必须为 .3ds 格式。<br><br>**数据类型**：String<br>**允许取值**：仅 .3ds 模型格式<br>**访问方式**：set<br>**默认值**：空<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **3DModelOffsetX** | 沿中心天体坐标系的 +X 或 -X 轴平移天体。<br><br>**数据类型**：Real<br>**允许取值**：-3.5 <= Real <= 3.5<br>**访问方式**：set<br>**默认值**：0.000000<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **3DModelOffsetY** | 沿中心天体坐标系的 +Y 或 -Y 轴平移天体。<br><br>**数据类型**：Real<br>**允许取值**：-3.5 <= Real <= 3.5<br>**访问方式**：set<br>**默认值**：0.000000<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **3DModelOffsetZ** | 沿中心天体坐标系的 +Z 或 -Z 轴平移天体。<br><br>**数据类型**：Real<br>**允许取值**：-3.5 <= Real <= 3.5<br>**访问方式**：set<br>**默认值**：0.000000<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **3DModelRotationX** | 绕中心天体坐标系的 X 轴对天体姿态进行固定旋转。<br><br>**数据类型**：Real<br>**允许取值**：-180 <= Real <= 180<br>**访问方式**：set<br>**默认值**：0.000000<br>**单位**：Deg.<br>**接口**：GUI、脚本 |
| **3DModelRotationY** | 绕中心天体坐标系的 Y 轴对天体姿态进行固定旋转。<br><br>**数据类型**：Real<br>**允许取值**：-180 <= Real <= 180<br>**访问方式**：set<br>**默认值**：0.000000<br>**单位**：Deg.<br>**接口**：GUI、脚本 |
| **3DModelRotationZ** | 绕中心天体坐标系的 Z 轴对天体姿态进行固定旋转。<br><br>**数据类型**：Real<br>**允许取值**：-180 <= Real <= 180<br>**访问方式**：set<br>**默认值**：0.000000<br>**单位**：Deg.<br>**接口**：GUI、脚本 |
| **3DModelScale** | 对天体模型尺寸应用缩放因子。<br><br>**数据类型**：Real<br>**允许取值**：0.001 <= Real <= 1000<br>**访问方式**：set<br>**默认值**：10<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **CentralBody** | 自定义天体轨道的中心天体。该字段主要由 GUI 使用。<br><br>**数据类型**：String<br>**允许取值**：**Comet**、**Planet**、**Asteroid** 或 **Moon** 的实例<br>**访问方式**：set<br>**默认值**：**Comet**、**Planet** 或 **Asteroid** 实例默认为 **Sun**；**Moon** 实例默认为 **Earth**。<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **DSNMediaFileDirectories** | 包含 DSN TRK-2-23 介质修正文件的目录列表。目录必须以完整路径或相对于 GMAT 可执行文件的路径给出。目录中的文件必须为 .csp 或 .csp.ql 格式。当地面站的对流层或电离层模型设为 'TRK-2-23' 时使用此参数。该字段仅对 **Earth** 有效。有关 TRK-2-23 介质模型的更多细节，请参阅 GroundStation。<br><br>**数据类型**：String 数组<br>**允许取值**：有效的目录路径<br>**访问方式**：set<br>**默认值**：{}<br>**单位**：N/A<br>**接口**：脚本 |
| **EquatorialRadius** | 天体的赤道半径。<br><br>**数据类型**：Real<br>**允许取值**：Real > 0<br>**访问方式**：set<br>**默认值**：0.0<br>**单位**：km<br>**接口**：GUI、脚本 |
| **EopFileName** | 可选的地球 EOP 文件，用于替代启动文件中定义的 EOP 文件。注意默认值为空字符串；当设为空字符串时，使用 GMAT 启动文件中定义的 EOP 文件。该字段仅对 **Earth** 有效。<br><br>**数据类型**：Filename<br>**允许取值**：有效的文件名<br>**访问方式**：set<br>**默认值**：''<br>**单位**：N/A<br>**接口**：脚本 |
| **FileName** | **OrbitView** 图形中使用的纹理贴图文件的路径和/或文件名。<br><br>**数据类型**：String<br>**允许取值**：以下格式的文件：.jpeg、.bmp、.png、.gif、.tif、.pcx、.pnm、.tga 或 .xpm<br>**访问方式**：set<br>**默认值**：`'../data/graphics/texture/GenericCelestialBody.jpg'`<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **Flattening** | 天体的极扁率。扁率定义为 *f = 1 - polar_radius / equatorial_radius*（1 减去极半径与赤道半径之比）。<br><br>**数据类型**：Real<br>**允许取值**：Real >= 0<br>**访问方式**：set<br>**默认值**：0.0<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **FrameSpiceKernelName** | 为该天体加载的 SPICE FK 文件列表。用于定义供 **ContactLocator** 和 **EclipseLocator** 使用的天体属性，以及当 **RotationDataSource** 设为 SPICE 时定义 Luna 或用户自定义天体的体固坐标轴。请参阅"备注"一节。<br><br>**数据类型**：String 数组<br>**允许取值**：有效 SPICE FK 文件的路径<br>**访问方式**：set<br>**默认值**：内置天体各不相同；用户自定义天体为空。<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **Mu** | 天体的引力参数（gravitational parameter）。<br><br>**数据类型**：Real<br>**允许取值**：Real > 0<br>**访问方式**：set<br>**默认值**：0.0<br>**单位**：km^3/s^2<br>**接口**：GUI、脚本 |
| **NAIFId** | 天体的 NAIF 整数 ID。<br><br>**数据类型**：Integer<br>**允许取值**：Integer<br>**访问方式**：set<br>**默认值**：-123456789<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **NutationUpdateInterval** | 地球章动（nutation）矩阵更新的时间间隔。若 NutationUpdateInterval = 3600，则 GMAT 仅每小时更新一次章动。<br><br>**数据类型**：Real<br>**允许取值**：Real >= 0<br>**访问方式**：set<br>**默认值**：60<br>**单位**：sec.<br>**接口**：GUI、脚本 |
| **OrbitColor** | 允许你为 3D **OrbitView** 图形显示中绘制的内置或用户自定义天体对象设置可用颜色。对象颜色可通过字符串或整数数组设置。例如：将天体轨道颜色设为红色有以下两种方式：`CelestialBody.OrbitColor = Red` 或 `Celestialbody.OrbitColor = [255 0 0]`。该字段也可以在任务序列中修改。<br><br>**数据类型**：Integer 数组或 String<br>**允许取值**：GUI 轨道颜色选择器中可用的任意颜色；有效的预定义颜色名称或 0 到 255 之间的 RGB 三元组值。<br>**访问方式**：set<br>**默认值**：用户自定义 **Planet** 为 Orchid（兰花紫），用户自定义 **Comet** 为 Pink（粉红），用户自定义 **Asteroid** 为 Salmon（鲑红），用户自定义 **Moon** 为 Tan（棕褐）<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **OrbitSpiceKernelName** | SPK 内核列表。提供空括号将卸载先前加载的内核。<br><br>**数据类型**：Reference 数组<br>**允许取值**：有效的 SPK 内核列表<br>**访问方式**：set<br>**默认值**：N/A<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **OrientationEpoch** | 定向数据的参考历元。<br><br>**数据类型**：String<br>**允许取值**：6116.0 <= Epoch <= 58127.5<br>**访问方式**：set<br>**默认值**：21545.0<br>**单位**：A1 修正儒略历元（A1 Modified Julian Epoch）<br>**接口**：GUI、脚本 |
| **PlanetarySpiceKernelName** | 为该天体加载的 SPICE PCK 文件列表。用于定义供 **ContactLocator** 和 **EclipseLocator** 使用的天体属性，以及当 **RotationDataSource** 设为 SPICE 时定义 Luna 或用户自定义天体的体固坐标轴。请参阅"备注"一节。<br><br>**数据类型**：String 数组<br>**允许取值**：有效 SPICE PCK 文件的路径<br>**访问方式**：set<br>**默认值**：内置天体各不相同；用户自定义天体为空。<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **PosVelSource** | 用户自定义天体轨道星历的模型。GMAT 目前对自定义天体仅支持单一星历模型（SPICE），通过 **PosVelSource** 字段设置。**PosVelSource** 的默认值为 SPICE，在当前版本的 GMAT 中无需配置此字段。该字段对内置天体无效。<br><br>**数据类型**：String<br>**允许取值**：**SPICE**<br>**访问方式**：set<br>**默认值**：内置天体为 **DE405**；用户自定义天体为 **SPICE**。<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **RotationConstant** | 天体在定向历元时刻的自转角。<br><br>**数据类型**：Real<br>**允许取值**：Real<br>**访问方式**：set<br>**默认值**：0.0<br>**单位**：deg<br>**接口**：GUI、脚本 |
| **RotationDataSource** | 指定天体体固坐标架（即该天体的 **CoordinateSystem** **BodyFixed** 坐标轴）的数据来源。此参数只能对 Luna 和任何用户自定义 CelestialBody 修改。除 Luna 外，内置天体的 **RotationDataSource** 目前不能更改。<br><br>**数据类型**：String<br>**允许取值**：**IAUSimplified**、**SPICE**（仅限 Luna 和用户自定义天体）<br>**访问方式**：none<br>**默认值**：**IAUSimplified**<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **RotationRate** | 天体的自转速率。<br><br>**数据类型**：Real<br>**允许取值**：Real<br>**访问方式**：set<br>**默认值**：0.0<br>**单位**：deg/day<br>**接口**：GUI、脚本 |
| **SpiceFrameId** | 体固坐标架的 SPICE ID。用于定义供 **ContactLocator** 和 **EclipseLocator** 使用的天体属性，以及当 **RotationDataSource** 设为 SPICE 时定义 Luna 或用户自定义天体的体固坐标轴。请参阅"备注"一节。<br><br>**数据类型**：String<br>**允许取值**：有效的 SPICE 坐标架 ID（文本或数字）<br>**访问方式**：set<br>**默认值**：内置天体各不相同；用户自定义天体为空。<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **SpinAxisDECConstant** | 天体自转轴在定向历元时刻的赤纬（declination）。<br><br>**数据类型**：Real<br>**允许取值**：Real<br>**访问方式**：set<br>**默认值**：90<br>**单位**：deg<br>**接口**：GUI、脚本 |
| **SpinAxisDECRate** | 天体自转轴赤纬的变化率。<br><br>**数据类型**：Real<br>**允许取值**：Real<br>**访问方式**：set<br>**默认值**：0.0<br>**单位**：deg/century<br>**接口**：GUI、脚本 |
| **SpinAxisRAConstant** | 天体自转轴在定向历元时刻的赤经（right ascension）。<br><br>**数据类型**：Real<br>**允许取值**：Real<br>**访问方式**：set<br>**默认值**：0.0<br>**单位**：deg<br>**接口**：GUI、脚本 |
| **SpinAxisRARate** | 天体自转轴赤经的变化率。<br><br>**数据类型**：Real<br>**允许取值**：Real<br>**访问方式**：set<br>**默认值**：0.0<br>**单位**：deg/century<br>**接口**：GUI、脚本 |
| **TargetColor** | 允许你为在差分校正（Differential Correction）或优化（Optimization）等迭代过程中绘制的对象摄动轨道轨迹设置可用颜色。目标颜色可通过字符串或整数数组指定。例如：将天体摄动轨迹颜色设为黄色有以下两种方式：`Celestialbody.TargetColor = Yellow` 或 `Celestialbody.TargetColor = [255 255 0]`。该字段也可以在任务序列中修改。<br><br>**数据类型**：Integer 数组或 String<br>**允许取值**：GUI 轨道颜色选择器中可用的任意颜色；有效的预定义颜色名称或 0 到 255 之间的 RGB 三元组值。<br>**访问方式**：set<br>**默认值**：内置或用户自定义的 **Planet**、**Comet**、**Asteroid** 和 **Moon** 均为 Dark Gray（深灰）<br>**单位**：N/A<br>**接口**：GUI、脚本 |
| **TextureMapFileName** | 允许你为天体加载纹理贴图文件。<br><br>**数据类型**：String<br>**允许取值**：jpeg 格式的纹理贴图文件<br>**访问方式**：set<br>**默认值**：`'GenericCelestialBody.jpg'`<br>**单位**：N/A<br>**接口**：GUI、脚本 |

## GUI

GUI 有三个选项卡，分别用于设置物理属性、轨道属性和定向模型。天体资源可用于 **ForceModels**、**CoordinateSystems**、**LibrationPoints** 和 **Barycenters** 等。对于内置天体，**Orbit**（轨道）和 **Orientation**（定向）选项卡大部分处于非激活状态，其行为在下文说明。要创建一个自定义 **Asteroid**——作为创建自定义天体的示例——请执行以下步骤：

1. 在**资源树（Resource Tree）**中展开 **SolarSystem** 文件夹。
2. 右键单击 **Sun**，选择 **Add** -> **Asteroid**。
3. 在 **New Asteroid** 对话框中输入所需名称。

> [图：新建 Asteroid 对话框]

天体 Properties（属性）选项卡如下图所示。GMAT 将所有天体建模为球形椭球体（spherical ellipsoid），你可以在此对话框中设置 **Equatorial Radius**（赤道半径）、**Flattening**（扁率）和 **Mu**（引力参数），以及 **OrbitView** 图形显示中使用的纹理贴图。

> [图：天体属性（Properties）选项卡]

创建自定义天体时的天体 **Orbit**（轨道）选项卡如下图所示。对于内置天体，此面板上的设置为非激活状态，内置天体的星历在 **SolarSystem** 对话框中配置。**CentralBody** 字段在对象创建时自动填充，且始终为非激活状态。要为自定义天体配置 **SPICE** 星历，请提供 SPK 文件列表和 **NAIF ID**。有关配置 **SPICE** 文件的更多信息，请参阅下文的讨论。

> [图：天体轨道（Orbit）选项卡]

天体 **Orientation**（定向）选项卡如下图所示。对于内置天体，此面板上的大多数设置为非激活状态，地球和地球月球的例外情况在下文进一步说明。要定义天体的定向，需要提供参考历元、参考历元时刻的初始定向以及角速率。有关定向模型的更详细描述，请参阅下文的讨论。

> [图：天体定向（Orientation）选项卡]

地球和地球月球拥有用于配置其定向模型的独有字段。地球有一个额外的字段 **NutationUpdateInterval**，可在需要较低精度、较高性能的仿真时使用。

> [图：地球定向选项卡（含 NutationUpdateInterval）]

天体 **Visualization**（可视化）选项卡如下图所示。在可视化选项卡上，你可以设置天体的 3D 模型、纹理文件、天体在三个坐标轴上的平移和旋转、3D 模型的缩放比例，以及为天体轨道指定轨道颜色和目标颜色等数据。

> [图：天体可视化（Visualization）选项卡]
## 备注

### 天体定向模型

内置天体的定向采用逐天体的高精度理论建模。地球的定向使用 IAU-1976/FK5 建模。海王星的定向使用 IAU-2002 建模。其余内置天体的定向使用 IAU/IAG 发布的《IAU/IAG 行星与卫星制图坐标与自转元素工作组报告：2000》（Report of the IAU/IAG Working Group on Cartographic Coordinates and Rotational Elements of the Planets and Satellites: 2000）中的数据建模。

默认情况下，地球月球的定向使用 DE 文件中的月球天平动（lunar libration）建模。用户可以按照以下规则指定地球月球（**Luna**）的定向：

- 如果 **SolarSystem** 的 **EphemerisSource** 设为某个 DE 文件选项（**DE405**、**DE421**、**DE424**），且 **Luna** 的 **RotationDataSource** 未设置，则月球定向由所选 DE 文件中提供的定向导出。
- 无论 SolarSystem EphemerisSource 如何设置，如果 **Luna** 的 **RotationDataSource** 设为 **SPICE**，则用于事件定位和 **CoordinateSystem** **BodyFixed** 坐标轴的月球定向由 **Luna** 的 **SpiceFrameId** 参数上设置的坐标架给出，同时还必须在 **Luna** 的 **PlanetarySpiceKernelName** 和 **FrameSpiceKernelName** 参数上指定提供该坐标架的相应 SPICE 内核。
- Luna 的重力建模将始终使用高精度的 DE 文件固定坐标架，无论旋转数据源如何选择。

默认情况下，自定义天体的定向通过基于 IAU/IAG 约定的三个角度及其速率来建模。下图展示了这些角度。角度 α₀、δ₀ 和 W 分别为 **SpinAxisRAConstant**、**SpinAxisDECConstant** 和 **RotationConstant**。角速率分别为 **SpinAxisRARate**、**SpinAxisDECRate** 和 **RotationRate**。所有角度均以 **ICRF** 轴系的 X-Y 平面为基准。常数值 **SpinAxisRAConstant**、**SpinAxisDECConstant** 和 **RotationConstant** 定义为 **OrientationEpoch** 中所定义历元时刻的值。

> [图：自定义天体定向角度 α₀、δ₀ 和 W 的示意图]

自定义天体也可以通过将天体的 **RotationDataSource** 选为 SPICE 并指定合适的 **SpiceFrameId**、**PlanetarySpiceKernelName** 和 **FrameSpiceKernelName**，来使用 SPICE 定义的固定坐标架。自定义天体的重力建模将使用所指定的旋转数据源进行。

> **注意**：航天器的 **Latitude**（纬度）、**Longitude**（经度）和 **Altitude**（高度）计算参数将使用指定的 SPICE 坐标架把航天器状态从惯性系转换到体固系，但纬度、经度和高度的计算将使用 GMAT 脚本中赋予天体的 **EquatorialRadius** 和 **Flattening** 值，而不是任何 SPICE 内核文件中的值。

下面是一个按照 IAU 2006 推荐值配置 **Asteroid**（以 Vesta 灶神星为例）的示例。注意 IAU 通常使用的定向历元是 01 Jan 2000 12:00:00.00.000 TDB，必须将其转换为 A1ModJulian，这可以使用 **Spacecraft** 的 **Orbit** 对话框轻松完成。

```
Create Asteroid Vesta
Vesta.CentralBody         = Sun
%  Note that currently the only available
%  format for OrientationEpoch is A1ModJulian
Vesta.OrientationEpoch    = 21544.99962789878  
Vesta.SpinAxisRAConstant  = 301.9
Vesta.SpinAxisRARate      = 0.9
Vesta.SpinAxisDECConstant = 90.9
Vesta.SpinAxisDECRate     = 0.0
Vesta.RotationConstant    = 292.9
Vesta.RotationRate        = 1617.332776
```

上述脚本创建小行星 Vesta，中心天体为太阳，并按 IAU 2006 推荐值设置其定向历元（A1 修正儒略日）、自转轴赤经/赤纬常数及变化率、自转角常数和自转速率。

地球和 Luna 可用的定向模型有额外的配置字段。地球有一个额外的字段 **NutationUpdateInterval**，用于控制章动矩阵的更新频率。对于高精度应用，**NutationUpdateInterval** 应设为零。

### 设置天体轨道的颜色

GMAT 允许你为 **OrbitView** 图形显示窗口中绘制的天体轨道指定颜色。GMAT 还允许你为差分校正或优化等迭代过程中绘制的摄动天体轨道轨迹指定颜色。对象的 **OrbitColor** 和 **TargetColor** 字段用于为轨道轨迹和摄动轨迹指定颜色。这两个字段的说明请参阅"字段"一节。另请参阅 Color 文档，了解如何设置天体颜色的讨论和示例。
### 配置轨道星历

内置天体的星历由 **SolarSystem.EphemerisSource** 字段指定，所有内置天体使用同一来源。自定义天体的星历由 SPICE 文件提供。可用的 SPICE 文件存档可在 [JPL NAIF 站点](ftp://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/) 和 [太阳系动力学站点](ftp://ssd.jpl.nasa.gov/pub/eph/planets/bsp/) 找到。如果现有内核不能满足你的应用需求，JPL 提供了创建自定义 SPICE 文件的工具。要创建自定义 SPICE 内核，请参阅 [JPL 提供的文档](http://naif.jpl.nasa.gov/naif/documentation.html)。天体的 NAIF ID 列表位于[此处](http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/naif_ids.html)。

注意，DE 文件建模的是行星系统的质心（barycenter）。因此，以木星为例，当使用 **DE405** 时，你建模的木星位置是木星系统（Jovian system）的质心。**SPICE** 内核区分行星系统质心与单个天体的位置。因此，当使用 **SPICE** 建模木星时，你建模的木星位置是木星的质心。

要为自定义天体指定 SPICE 内核，请使用 **NAIFId**、**CentralBody** 和 **OrbitSpiceKernelName** 字段。GMAT 随附了谷神星（CERES）的 SPK 文件，其 **NAIF ID** 为 2000001。以下是将一个 **Asteroid** 配置为使用 CERES SPICE 星历数据的方法。

```
Create Asteroid Ceres
Ceres.CentralBody          = Sun
Ceres.OrbitSpiceKernelName = ...
    {'../data/planetary_ephem/spk/ceres_1900_2100.bsp'}
```

上述脚本创建小行星 Ceres，中心天体为太阳，并加载谷神星 1900–2100 年的 SPK 星历内核。

注意：GMAT 目前对自定义天体仅支持单一星历模型（SPICE），通过 **PosVelSource** 字段设置。**PosVelSource** 的默认值为 SPICE，在当前版本的 GMAT 中无需配置此字段。

> **警告**：NAIF 分发的 SPICE 内核涵盖许多天体，每个内核都与特定的主星历版本（如 DE421）保持一致。对于高精度分析，务必确保自定义天体所用的星历与 **SolarSystem.EphemerisSource** 字段中选择的星历来源保持一致。SPICE 内核通常随附一个 ".cmt" 文件，该文件中包含星历模型的行如下所示：
>
> `Planetary Ephemeris Number: DE-0421/LE-0421`

### 配置物理属性

GMAT 将所有天体建模为球形椭球体。要定义物理属性，请使用 **Flattening**、**EquatorialRadius** 和 **Mu** 字段。

### 配置用于事件定位

GMAT 的事件定位子系统（由 **ContactLocator** 和 **EclipseLocator** 组成）使用来自 SPICE 工具包的天体定义。半径、扁率、星历和定向等属性必须单独配置才能用于事件定位器。

天体形状和定向通过 SPICE PCK 文件配置，按以下顺序从两个来源加载：

1. **SolarSystem**.**PCKFilename**
2. **Sun**.**PlanetarySpiceKernelName**（按列表顺序），随后依次为 **Mercury**、**Venus**、**Earth**、**Mars**、**Jupiter**、**Saturn**、**Uranus**、**Neptune**、**Pluto**、**Luna**
3. 用户自定义天体

如果存在冲突，后加载的数据优先于先加载的数据。注意，由于 SPICE 内核池在整个运行期间共享，为 **Pluto** 加载的 PCK 文件可能会覆盖 **Sun** 加载的数据（如果文件包含冲突数据）。注意此顺序并非绝对——例如，以 SPK 定义原点的坐标系加载方式不同。要确定确切的加载顺序，请参阅 `GmatLog.txt` 文件。

> **注意**：GMAT 的 SPICE 内核加载顺序取决于许多因素，可能不可预测。因此，任务所引用的内核必须保持一致，这一点很重要。例如，NAIF 的 `de421.bsp` 和 `mar085.bsp` 是一致的，因为它们都基于 DE421 模型。不一致的内核会因加载顺序不同而导致不可预测的行为。

天体的体固坐标架在 **Orientation**（定向）选项卡上通过 **SpiceFrameId** 和 **SpiceFrameKernelFile** 字段定义。**SpiceFrameId** 包含体固坐标架的 SPICE ID，该坐标架可以是内置的，也可以通过外部 FK 文件定义。外部 FK 文件可通过将其添加到每个天体的 **SpiceFrameKernelFile** 列表来加载。这些文件在每个天体的 **PlanetarySpiceKernelName** 之后加载。内置坐标架的列表可在 [SPICE 文档](http://naif.jpl.nasa.gov/pub/naif/toolkit_docs/C/req/frames.html)的附录中找到。GMAT 的默认坐标架为：

- 地球：`ITRF93`
- Luna：`MOON_PA`
- 其他默认天体：`IAU_<天体名>`

地球 ITRF93 坐标架由三个高精度定向 PCK 文件定义，如下所示。有关这些文件的更多信息，请参阅 NAIF 的 `aareadme.txt` 文件。

- `earth_<起始>_<结束>_predict.bpc`：长期低精度 EOP 预报
- `earth_<起始>_<结束>.bpc`：长期低精度历史 EOP
- `earth_<起始>_<结束>_<文件日期>.bpc`：近期高精度 EOP 历史与预报

Luna 的 MOON_PA 坐标架由一个定向 PCK 文件和一个定义坐标架的 FK 文件定义，如下所示。更多信息请参阅 NAIF PCK 的 `aareadme.txt` 文件和 FK 的 `aareadme.txt` 文件。NAIF 还提供其他版本的 MOON_PA 坐标架。

- `moon_pa_de421_1900-2050.bpc`：与 DE421 PA 坐标架一致的月球定向
- `moon_080317.tf`：MOON_PA 坐标架定义
## 示例

配置一个 **Moon** 来建模土星的卫星 Titan（土卫六）。注意，你必须从[此处](ftp://naif.jpl.nasa.gov/pub/naif/generic_kernels/spk/satellites/)获取名为 `sat288.bsp` 的 SPICE 内核，并将其放置在下面脚本片段所指定的目录中。

```
Create Moon Titan
Titan.NAIFId               = 606
Titan.OrbitSpiceKernelName = { ...
    '../data/planetary_ephem/spk/sat288.bsp' ...
    }
Titan.SpiceFrameId         = 'IAU_TITAN'
Titan.EquatorialRadius     = 2575
Titan.Flattening           = 0
Titan.Mu                   = 8978.5215
Titan.PosVelSource         = 'SPICE'
Titan.CentralBody          = 'Saturn'
Titan.RotationDataSource   = 'IAUSimplified'
Titan.OrientationEpoch     = 21545
Titan.SpinAxisRAConstant   = 36.41
Titan.SpinAxisRARate       = -0.036
Titan.SpinAxisDECConstant  = 83.94
Titan.SpinAxisDECRate      = -0.004
Titan.RotationConstant     = 189.64
Titan.RotationRate         = 22.5769768
```

上述脚本创建卫星 Titan：NAIF ID 为 606，轨道星历来自 SPICE 内核 `sat288.bsp`，体固坐标架为 IAU_TITAN，并设置赤道半径、扁率、引力参数、中心天体（土星）以及 IAU 简化定向模型的各参数。

将地球月球（Luna）的体固坐标架配置为 MOON_ME 坐标架。

```
Luna.PlanetarySpiceKernelName = '../data/planetary_coeff/SPICELunaCurrentKernel.bpc'
Luna.FrameSpiceKernelName     = '../data/planetary_coeff/SPICELunaFrameKernel.tf'
Luna.RotationDataSource       = 'SPICE'
Luna.SpiceFrameId             = 'MOON_ME'

%
%   Create a body-fixed coordinate system tied to the MOON_ME axes
%

Create CoordinateSystem MoonME

MoonME.Origin = Luna
MoonME.Axes   = BodyFixed
```

上述脚本为 Luna 加载行星 PCK 内核和坐标架 FK 内核，将旋转数据源设为 SPICE、体固坐标架设为 MOON_ME，然后创建一个原点为 Luna、坐标轴为 BodyFixed（体固）的坐标系 MoonME，使其绑定到 MOON_ME 坐标轴。
