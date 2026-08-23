# 轨道视图（OrbitView）

> 译自 GMAT R2026a 帮助文档 OrbitView.html

**OrbitView** —— 用户自定义资源，用于绘制三维轨迹。

## 描述

`OrbitView` 资源允许你绘制航天器或天体的轨迹。GMAT 还允许你绘制与多个航天器或天体关联的轨迹。你可以通过 GMAT 的 GUI 或脚本接口创建多个 `OrbitView` 资源。`OrbitView` 图还带有多个选项，允许你自定义航天器轨迹的视图。可用绘图和绘制选项的详细讨论见下文"字段"一节。

GMAT 还通过 `Toggle On/Off` 命令提供何时开始和停止向 `OrbitView` 资源绘制航天器轨迹的选项。`OrbitView` 资源与 `Toggle` 命令的交互详见下文"备注"一节。GMAT 的 `Spacecraft`、`SolarSystem` 和 `OrbitView` 资源在整个任务持续期间也会相互交互，这些资源之间交互的讨论同样见"备注"一节。

**另请参阅**：`Toggle`、`Spacecraft`、`SolarSystem`、`CoordinateSystem`、`Color`

## 字段

| 字段 | 描述 |
| --- | --- |
| `Add` | 该字段允许你向图中添加 `Spacecraft`（航天器）、`Celestial body`（天体）、`Libration Point`（天平动点）或 `Barycenter`（质心）资源。创建图时，`Earth` 作为默认天体被添加，可随时移除。你可以使用创建资源时的名称把航天器、天体、天平动点或质心添加到图中。GUI 的 **Selected** 字段等同于脚本的 `Add` 字段。如果没有 `Add` 命令或 **Selected** 字段中没有资源，GMAT 将在没有 `OrbitView` 图的情况下运行，并在消息窗口显示警告消息，例如：The OrbitView named "DefaultOrbitView" will be turned off. No SpacePoints were added to plot（名为 "DefaultOrbitView" 的 OrbitView 将被关闭，没有向图添加任何 SpacePoint）。该字段不能在任务序列中修改。**数据类型**：引用数组；**允许值**：`Spacecraft`、`CelestialBody`、`LibrationPoint`、`Barycenter`；**访问**：set；**默认值**：`DefaultSC`、`Earth`；**单位**：N/A；**接口**：GUI、脚本 |
| `Axes` | 允许你绘制与 `OrbitView` 图的 `CoordinateSystem` 字段下所选坐标系关联的笛卡尔坐标轴系。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：On、Off；**访问**：set；**默认值**：On；**单位**：N/A；**接口**：GUI、脚本 |
| `EclipticPlane` | 允许你在 `OrbitView` 图中绘制表示黄道面（Ecliptic Plane）的网格。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：On、Off；**访问**：set；**默认值**：Off；**单位**：N/A；**接口**：GUI、脚本 |
| `CoordinateSystem` | 允许你选择用哪个坐标系来绘制图数据。坐标系定义为原点（origin）和轴系（axis system）。`CoordinateSystem` 字段允许你确定 `OrbitView` 图的原点和轴系。关于定义不同类型坐标系的信息，请参阅 `CoordinateSystem` 资源字段。该字段不能在任务序列中修改。**数据类型**：字符串；**允许值**：`CoordinateSystem` 资源；**访问**：set；**默认值**：`EarthMJ2000Eq`；**单位**：N/A；**接口**：GUI、脚本 |
| `DataCollectFrequency` | 允许你定义如何为绘图收集数据。绘制与轨迹关联的每个星历点通常效率低下；绘制较小的数据子集通常仍能得到平滑的轨迹图，同时执行更快。`DataCollectFrequency` 是一个整数，表示多久收集一次数据并存储用于绘图。如果设为 10，则每 10 个积分步收集一次数据。该字段不能在任务序列中修改。**数据类型**：整数；**允许值**：整数 ≥ 1；**访问**：set；**默认值**：1；**单位**：N/A；**接口**：GUI、脚本 |
| `DrawObject` | `DrawObject` 字段让你可以选择是否在 `OrbitView` 图上显示 `Spacecraft` 或 `Celestial` 资源。该字段不能在任务序列中修改。**数据类型**：布尔数组；**允许值**：true、false；**访问**：set；**默认值**：[true true]；**单位**：N/A；**接口**：GUI、脚本 |
| `EnableConstellations` | 让你可以选择是否在 `OrbitView` 图上显示星座。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：On、Off；**访问**：set；**默认值**：On；**单位**：N/A；**接口**：GUI、脚本 |
| `EnableStars` | 该字段让你可以选择是否在 `OrbitView` 图上显示恒星。当 `EnableStars` 字段关闭时，`EnableConstellations` 字段会自动禁用。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：On、Off；**访问**：set；**默认值**：On；**单位**：N/A；**接口**：GUI、脚本 |
| `Grid` | 允许你在添加到 `OrbitView` 图的天体上绘制表示经纬线的网格。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：On、Off；**访问**：set；**默认值**：Off；**单位**：N/A；**接口**：GUI、脚本 |
| `Maximized` | 允许你最大化 `OrbitView` 绘图窗口。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：True、False；**访问**：set；**默认值**：false；**单位**：N/A；**接口**：脚本 |
| `NumPointsToRedraw` | 当 `NumPointsToRedraw` 字段设为零时，绘制所有星历点。当设为正整数（例如 10）时，只绘制最后收集的 10 个数据点。关于如何为 `OrbitView` 图收集数据的说明见 `DataCollectFrequency`。该字段不能在任务序列中修改。**数据类型**：整数；**允许值**：整数 ≥ 1；**访问**：set；**默认值**：0；**单位**：N/A；**接口**：GUI、脚本 |
| `RelativeZOrder` | 允许你选择哪个 `OrbitView` 窗口最先显示在屏幕上。`RelativeZOrder` 值最低的 `OrbitViewPlot` 最后显示，值最高的最先显示。该字段不能在任务序列中修改。**数据类型**：整数；**允许值**：整数 ≥ 0；**访问**：set；**默认值**：0；**单位**：N/A；**接口**：脚本 |
| `ShowPlot` | 允许你针对某次运行关闭绘图，而无需删除该图或将其从脚本中移除。选 true 则显示图；选 false 则不显示。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：True、False；**访问**：set；**默认值**：True；**单位**：N/A；**接口**：GUI、脚本 |
| `ShowLabels` | 允许你打开或关闭航天器和天体对象的标签。选 true 则航天器和天体对象标签会显示在轨道视图中；选 false 则不显示。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：True、False；**访问**：set；**默认值**：True；**单位**：N/A；**接口**：GUI、脚本 |
| `Size` | 允许你控制 `OrbitViewPlot` 窗口的显示尺寸。[0 0] 矩阵中第一个值控制水平尺寸，第二个值控制垂直尺寸。该字段不能在任务序列中修改。**数据类型**：实数数组；**允许值**：任意实数；**访问**：set；**默认值**：[0 0]；**单位**：N/A；**接口**：脚本 |
| `SolverIterations` | 决定在求解器（`Targeter`、`Optimize`）序列期间，与受扰轨迹关联的数据是否绘制到 `OrbitView`。设为 `All` 时，所有扰动/迭代都绘制到 `OrbitView` 图；设为 `Current` 时，只绘制当前解；设为 `None` 时，只显示迭代过程结束后的最终解，并只把最终轨迹绘制到 `OrbitView` 图。**数据类型**：枚举；**允许值**：`All`、`Current`、`None`；**访问**：set；**默认值**：`Current`；**单位**：N/A；**接口**：GUI、脚本 |
| `StarCount` | 允许你输入需要在 `OrbitView` 图中显示的恒星数量。该字段不能在任务序列中修改。**数据类型**：整数；**允许值**：整数 ≥ 1；**访问**：set；**默认值**：7000；**单位**：N/A；**接口**：GUI、脚本 |
| `SunLine` | 允许你绘制一条从中心天体中心指向太阳（`Sun`）的线。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：On、Off；**访问**：set；**默认值**：Off；**单位**：N/A；**接口**：GUI、脚本 |
| `UpdatePlotFrequency` | 该字段让你指定在传播航天器和运行任务过程中，多久用新收集的数据更新一次 `OrbitView` 图。图的数据按 `DataCollectFrequency` 定义的值收集，并按 `UpdatePlotFrequency` 设置的值用新数据更新。如果 `UpdatePlotFrequency` 设为 10 且 `DataCollectFrequency` 设为 2，则每 20（10*2）个积分步用新数据更新一次图。该字段不能在任务序列中修改。**数据类型**：整数；**允许值**：整数 ≥ 1；**访问**：set；**默认值**：50；**单位**：N/A；**接口**：GUI、脚本 |
| `UpperLeft` | 允许你沿任意方向平移 `OrbitView` 绘图窗口。[0 0] 矩阵中第一个值水平平移窗口，第二个值垂直平移窗口。该字段不能在任务序列中修改。**数据类型**：实数数组；**允许值**：任意实数；**访问**：set；**默认值**：[0 0]；**单位**：N/A；**接口**：脚本 |
| `UseInitialView` | 该字段让你控制任务序列多次运行之间 `OrbitView` 图的视图。第一次创建某个 `OrbitView` 图时，GMAT 会自动使用由 **View Definition**、**View Up Direction** 和 **View Option** 相关字段定义的视图。但是，如果你用鼠标更改了视图，只要 `UseInitialView` 设为 false，GMAT 会在重新运行任务时保留该视图。如果 `UseInitialView` 设为 true，`OrbitView` 图的视图将回到初始设置定义的视图。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：On、Off；**访问**：set；**默认值**：On；**单位**：N/A；**接口**：GUI、脚本 |
| `ViewDirection` | 允许你选择 `OrbitView` 图中的观察方向。你可以通过选择要指向的资源来指定观察方向，如 `Spacecraft`、`Celestial body`、`Libration Point` 或 `Barycenter`；也可以指定 [x y z] 形式的向量。如果用户对 `ViewDirection`、`ViewPointReference` 和 `ViewPointVector` 的指定结果为零向量，GMAT 会为 `ViewDirection` 使用 [0 0 10000]。该字段不能在任务序列中修改。**数据类型**：引用数组；**允许值**：`Spacecraft`、`CelestialBody`、`LibrationPoint`、`Barycenter` 或数值三维向量；**访问**：set；**默认值**：Earth；**单位**：km 或 N/A；**接口**：GUI、脚本 |
| `ViewPointReference` | 该可选字段允许你更改 `ViewPointVector` 的测量参考点。`ViewPointReference` 默认为图的坐标系原点。`ViewPointReference` 可以是任何 `Spacecraft`、`Celestial body`、`Libration Point` 或 `Barycenter`。该字段不能在任务序列中修改。**数据类型**：引用数组；**允许值**：`Spacecraft`、`CelestialBody`、`LibrationPoint`、`Barycenter` 或数值三维向量；**访问**：set；**默认值**：Earth；**单位**：km 或 N/A；**接口**：GUI、脚本 |
| `ViewPointVector` | `ViewScaleFactor` 与 `ViewPointVector` 字段的乘积决定视点相对于 `ViewPointReference` 的位置。`ViewPointVector` 可以是向量，或以下任何资源：`Spacecraft`、`Celestial body`、`Libration Point`、`Barycenter`。视点在三维空间中的位置定义为 `ViewPointReference` 与由 `ViewScaleFactor` 和 `ViewPointVector` 乘积定义的向量在你所选坐标系中的矢量相加。该字段不能在任务序列中修改。**数据类型**：引用数组；**允许值**：`Spacecraft`、`CelestialBody`、`LibrationPoint`、`Barycenter` 或数值三维向量；**访问**：set；**默认值**：[30000 0 0]；**单位**：km 或 N/A；**接口**：GUI、脚本 |
| `ViewScaleFactor` | 该字段在把 `ViewPointVector` 加到 `ViewPointReference` 之前对其进行缩放。`ViewScaleFactor` 允许你远离某个对象以使其纳入视野。该字段不能在任务序列中修改。**数据类型**：实数；**允许值**：实数 ≥ 0；**访问**：set；**默认值**：1；**单位**：N/A；**接口**：GUI、脚本 |
| `ViewUpAxis` | 该字段让你定义 `ViewUpCoordinateSystem` 字段的哪个轴将在 `OrbitView` 图中显示为"上"方向。更多细节见 `ViewUpCoordinateSystem` 下的说明。该字段不能在任务序列中修改。**数据类型**：枚举；**允许值**：`X`、`-X`、`Y`、`-Y`、`Z`、`-Z`；**访问**：set；**默认值**：`Z`；**单位**：N/A；**接口**：GUI、脚本 |
| `ViewUpCoordinateSystem` | `ViewUpCoordinateSystem` 和 `ViewUpAxis` 字段用于确定哪个方向在 `OrbitView` 图中显示为"上"，并与 **View Direction** 相关字段一起唯一地定义视图。**View Definition** 相关字段允许你定义三维空间中的视点和视线方向，但仅凭这些信息还不足以唯一地定义视图，还必须提供视图绕视线的定向方式。这通过定义哪个方向应显示为图中的"上"方向来实现，使用 `ViewUpCoordinateSystem` 字段和 `ViewUpAxis` 字段配置。`ViewUpCoordinateSystem` 允许你选择一个坐标系来定义上方向。大多数情况下，该坐标系会与 `CoordinateSystem` 字段下选择的坐标系相同。该字段不能在任务序列中修改。**数据类型**：字符串；**允许值**：`CoordinateSystem` 资源；**访问**：set；**默认值**：`EarthMJ2000Eq`；**单位**：N/A；**接口**：GUI、脚本 |
| `WireFrame` | 当 `WireFrame` 字段设为 `On` 时，天体用线框模型绘制；设为 `Off` 时，天体用完整贴图绘制。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：Off、On；**访问**：set；**默认值**：Off；**单位**：N/A；**接口**：GUI、脚本 |
| `XYPlane` | 允许你绘制表示 `OrbitView` 图的 `CoordinateSystem` 字段下所选坐标系 XY 平面的网格。该字段不能在任务序列中修改。**数据类型**：布尔；**允许值**：On、Off；**访问**：set；**默认值**：On；**单位**：N/A；**接口**：GUI、脚本 |
## GUI

下图显示 `OrbitView` 资源的默认设置：

> [图：OrbitView 资源 GUI 设置面板]

### OrbitView 窗口鼠标控制

下表中的控制项帮助你在 `OrbitView` 图形窗口中导航。"Left（左键）"和 "Right（右键）"指需要按下的鼠标按键。

| 控制 | 描述 |
| --- | --- |
| **Left Drag（左键拖拽）** | 改变相机朝向。相机朝向可沿上/下/左/右方向改变。 |
| **Right Drag（右键拖拽）** | 缩放图形窗口。向上移动光标为缩小，向下移动光标为放大。 |
| **Shift+Right Drag（Shift+右键拖拽）** | 调整视野（Field of View）。 |

## 备注

### 使用 OrbitView 资源与 Toggle 命令时的行为

`OrbitView` 资源在整个任务持续期间的每个传播步绘制航天器轨迹。如果你只想在任务的特定点向 `OrbitView` 图报告数据，可以在任务序列中插入 `Toggle On`/`Off` 命令来控制 `OrbitView` 何时绘制给定轨迹。对某个 `OrbitView` 发出 `Toggle Off` 命令后，在发出 `Toggle On` 命令之前不会绘制任何轨迹；同样，使用 `Toggle On` 命令后，每个积分步都会绘制轨迹，直到使用 `Toggle Off` 命令为止。

```
Create Spacecraft aSat
Create Propagator aProp

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}

BeginMissionSequence

Toggle anOrbitView Off
Propagate aProp(aSat) {aSat.ElapsedDays = 2}
Toggle anOrbitView On
Propagate aProp(aSat) {aSat.ElapsedDays = 4}
```

说明：前 2 天关闭轨迹绘制，之后打开并继续传播 4 天。

### 使用 OrbitView、Spacecraft 和 SolarSystem 资源时的行为

`Spacecraft` 资源包含航天器轨道的信息。`Spacecraft` 资源在整个任务持续期间与 `OrbitView` 交互。在每个传播步，从航天器检索到的轨迹数据就是会被绘制的数据。同样，`SolarSystem` 资源下的太阳和所有其他行星也可以在 `OrbitView` 资源中被绘制或引用。

### 在迭代过程中报告数据时的行为

GMAT 允许你指定在差分校正或优化等迭代过程中如何绘制轨迹。`OrbitView` 资源的 `SolverIterations` 字段支持 3 个选项：

| SolverIterations 选项 | 描述 |
| --- | --- |
| `Current` | 只显示迭代过程中的当前迭代/扰动，并绘制当前轨迹 |
| `All` | 显示迭代过程中的所有迭代/扰动，并绘制所有受扰轨迹 |
| `None` | 只显示迭代过程结束后的最终解，并只绘制该最终轨迹 |

### 绘制多个航天器时的行为

使用 `OrbitView` 资源时，GMAT 允许你绘制任意数量航天器的轨迹。为绘制轨迹，所有航天器的初始历元必须相同。如果某个航天器的初始历元与其他航天器的初始历元不匹配，GMAT 会抛出错误，提示航天器之间存在耦合传播误差（coupled propagation error）不匹配。GMAT 还允许你使用可创建的传播器的任意组合来传播航天器轨迹。

下面的脚本片段示例展示了如何绘制使用不同传播器的多个航天器的轨迹：

```
Create Spacecraft aSat aSat2 aSat3
aSat2.INC = 45.0
aSat3.INC = 90.0
aSat3.SMA = 9000

Create Propagator aProp
Create Propagator bProp

Create OrbitView anOrbitView anOrbitView2

anOrbitView.Add = {aSat, aSat2, Earth}
anOrbitView2.Add = {aSat3, Earth}

BeginMissionSequence

Propagate aProp(aSat, aSat2) bProp(aSat3) {aSat.ElapsedSecs = 12000.0}
```

说明：三个航天器使用两个不同传播器同时传播，并分别绘制在两个 OrbitView 图中。
### OrbitView 视图定义控制

GMAT 能够绘制轨道图，让你可视化航天器和天体在整个任务序列中的运动。这里讨论可用于设置和查看轨道图的选项。你可以选择许多属性，包括轨道视图的坐标系，以及可视化观察的视图位置和方向。下面的脚本片段展示如何创建包含关键视图定义控制字段的 `OrbitView` 资源。`OrbitView` 资源所有字段的详细定义见"字段"一节。

```
Create OrbitView PlotName
PlotName.CoordinateSystenm      = CoordinateSystemName
PlotName.Add                    = [SpacecraftName, BodyName, ... 
                                  LibrationPoint, Barycenter]
PlotName.ViewPointReference     = [ObjectName, VectorName]
PlotName.ViewPointVector        = [ObjectName, VectorName]
PlotName.ViewDirection          = [ObjectName, VectorName]
PlotName.ViewScaleFactor        = [Real Number]
PlotName.ViewUpCoordinateSystem = CoordinateSystemName
PlotName.ViewUpAxis             = [X,-X,Y,-Y,Z,-Z];
```

说明：以上为视图定义字段的配置模板（注意原文中 `CoordinateSystenm` 为原文拼写）。

你可以使用 `ViewPointReference`、`ViewPointVector`、`ViewDirection`、`ViewUpCoordinateSystem` 和 `ViewUpAxis` 字段指定 `OrbitView` 图对象的视图位置和方向。下图展示了 `ViewPointReference`、`ViewPointVector` 和 `ViewDirection` 字段的图形化定义，以及它们如何决定实际的视图位置和观察方向。

> [图：ViewPointReference、ViewPointVector、ViewDirection 的几何关系示意图]

`ViewPointReference`、`ViewPointVector` 和 `ViewDirection` 字段既可以用 [x y z] 格式的向量提供，也可以用对象名指定。如果为某个量给定了向量，就直接在下面计算的相应位置使用它；如果给定的是对象，则必须先确定与该对象关联的向量。本节的其余部分专门讨论在指定对象时如何确定 `ViewPointReference`、`ViewPointVector` 和 `ViewDirection` 字段。

`ViewPointReference` 字段定义 `ViewPointVector` 的测量起点。如果为 `ViewPointReference` 字段给定了一个对象，即示例脚本中有：

```
MyOrbitViewPlot.CoordinateSystenm    = MyCoordSys 
MyOrbitViewPlot.ViewPointReference   = ViewRefObject
```

那么需要确定上图所示的 r_r。如果 ViewRefObject 与 MyCoordSys 的原点相同，则 r_r = [0 0 0]；否则 r_r 是 `ViewPointReference` 在 MyCoordSys 中的笛卡尔位置。

> [图：r_r 的计算公式]

`ViewPointVector` 字段从 `ViewPointReference`（r_r）指向视点位置的方向。如果为 `ViewPointVector` 字段给定了一个对象，即示例脚本中有：

```
MyOrbitViewPlot.CoordinateSystenm    = MyCoordSys 
MyOrbitViewPlot.ViewPointVector      = ViewPointObject
```

那么需要通过坐标系转换例程确定上图所示的 r_v。

> [图：r_v 的计算公式]

现在我们已经知道了在所需坐标系中计算视点位置所需的全部内容。观察上图可知其关系为：

> [图：视点位置 = r_r + ViewScaleFactor × r_v 的计算公式]

知道了视点位置后，还需要确定观察方向 ViewDirection：上图所示的 r_d。如果为 `ViewDirection` 字段指定了向量，则无需计算；但如果给定的是对象，如以下示例脚本所示：

```
MyOrbitViewPlot.CoordinateSystenm    = MyCoordSys 
MyOrbitViewPlot.ViewDiection         = ViewDirectionObject
```

则按相应公式计算 r_d。

> [图：r_d 的计算公式]

注意，ViewDirection 向量 r_d 不能是零向量 [0 0 0]。

`ViewUpCoordinateSystem` 和 `ViewUpAxis` 字段用于确定哪个方向在 `OrbitView` 图中显示为"上"。大多数情况下，`ViewUpCoordinateSystem` 字段下选择的坐标系会与 `CoordinateSystem` 字段下选择的坐标系相同。`ViewUpAxis` 字段允许你定义 `ViewUpCoordinateSystem` 字段的哪个轴将在轨道图中显示为上方向。

下面是一些示例，展示如何使用不同的视图定义控制配置生成 `OrbitView` 图：

**带航天器的地球惯性视图**：本例展示包含地球和一个航天器的轨道视图。由于 `ViewPointReference` 字段设为对象（即 Earth），上图中 ViewPointRef 向量在 EarthMJ2000Eq 坐标系中为 [0 0 0]。`ViewPointVector` 字段设为向量（即 [0 0 40000]），这意味着视图从 EarthMJ2000Eq 坐标系 z 轴上地球赤道面上方 40000 km 处观察。观察方向（在 `ViewDirection` 字段中指定）朝向地球。

```
Create Spacecraft aSat

Create Propagator aProp

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}

anOrbitView.CoordinateSystem = EarthMJ2000Eq
anOrbitView.ViewPointReference = Earth
anOrbitView.ViewPointVector = [ 0 0 40000 ]
anOrbitView.ViewDirection = Earth
anOrbitView.ViewScaleFactor = 1
anOrbitView.ViewUpCoordinateSystem = EarthMJ2000Eq
anOrbitView.ViewUpAxis = Z

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1}
```

说明：从地球赤道面上方 40000 km 处俯视，传播 1 天。

**带航天器和月球的地球惯性视图**：本例展示包含地球、航天器和月球的轨道视图。注意 `ViewPointReference` 字段设为对象（即 Earth），故 ViewPointRef 向量在 EarthMJ2000Eq 坐标系中为 [0 0 0]。`ViewPointVector` 字段仍设为向量（即 [0 0 500000]），这意味着视图从 EarthMJ2000Eq 坐标系 z 轴上地球赤道面上方 500000 km 处观察。`ViewDirection` 字段定义的观察方向朝向地球。

```
Create Spacecraft aSat

Create Propagator aProp

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth, Luna}

anOrbitView.CoordinateSystem = EarthMJ2000Eq
anOrbitView.ViewPointReference = Earth
anOrbitView.ViewPointVector = [ 0 0 500000 ]
anOrbitView.ViewDirection = Earth
anOrbitView.ViewScaleFactor = 1
anOrbitView.ViewUpCoordinateSystem = EarthMJ2000Eq
anOrbitView.ViewUpAxis = Z

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 5}
```

说明：从 500000 km 高处俯视地月系，传播 5 天。
**在地球惯性参考架中从月球看航天器**：本例展示在惯性参考架中，从环绕地球的月球（Luna）视角看航天器。`ViewPointReference` 字段设为对象（即 Earth），故 ViewPointRef 向量在 EarthMJ2000Eq 坐标系中为 [0 0 0]。这次 `ViewPointVector` 字段设为对象（即 Luna），这意味着将从 Luna 的有利位置看到航天器。注意 `ViewDirection` 字段设为航天器（aSat），即从 Luna 看去的观察方向朝向航天器。运行本例后，把 `ViewScaleFactor` 字段设为 2 重新运行，观察会发生什么——你会发现 `ViewScaleFactor` 只是对 `ViewPointVector` 字段进行缩放。

```
Create Spacecraft aSat

Create Propagator aProp

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth, Luna}

anOrbitView.CoordinateSystem = EarthMJ2000Eq
anOrbitView.ViewPointReference = Earth
anOrbitView.ViewPointVector = Luna
anOrbitView.ViewDirection = aSat
anOrbitView.ViewScaleFactor = 1
anOrbitView.ViewUpCoordinateSystem = EarthMJ2000Eq
anOrbitView.ViewUpAxis = Z

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 5}
```

说明：视点位于月球处，视线指向航天器，传播 5 天。

**在惯性参考架中，航天器环绕月球时从地球看月球**：本例展示当航天器环绕月球时，从地球的有利位置看月球的视图。`ViewPointReference` 字段设为对象（即 Luna），故 ViewPointRef 向量在 LunaMJ2000Eq 坐标系中为 [0 0 0]。`ViewPointVector` 字段设为对象（即 Earth），这意味着相机或观察点位于地球。`ViewDirection` 字段也设为对象（即 Luna），即从地球看去的观察方向朝向月球。

```
Create Spacecraft aSat

Create CoordinateSystem LunaMJ2000Eq
LunaMJ2000Eq.Origin = Luna
LunaMJ2000Eq.Axes = MJ2000Eq

aSat.CoordinateSystem = LunaMJ2000Eq
aSat.SMA = 7300
aSat.ECC = 0.4
aSat.INC = 90
aSat.RAAN = 270
aSat.AOP = 315
aSat.TA = 180

Create ForceModel aFM
aFM.CentralBody = Luna
aFM.PointMasses = {Luna}

Create Propagator aProp
aProp.FM = aFM

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Luna, Earth}
anOrbitView.CoordinateSystem = LunaMJ2000Eq
anOrbitView.ViewPointReference = Luna
anOrbitView.ViewPointVector = Earth
anOrbitView.ViewDirection = Luna
anOrbitView.ViewScaleFactor = 1;
anOrbitView.ViewUpCoordinateSystem = LunaMJ2000Eq;
anOrbitView.ViewUpAxis = Z;

BeginMissionSequence
Propagate aProp(aSat) {aSat.ElapsedDays = 5}
```

说明：在以月球为中心的坐标系中传播环月轨道，从地球方向观察月球。

**在惯性参考架中从航天器 2 看航天器 1**：本例展示航天器 1（aSat1）从航天器 2（aSat2）的视角被观察，二者在惯性参考架中运动。`ViewPointReference` 字段设为对象（即 Earth），故 ViewPointRef 向量在 EarthMJ2000Eq 坐标系中为 [0 0 0]。`ViewPointVector` 字段设为对象（即 aSat2），`ViewDirection` 字段也设为对象（即 aSat1）。这意味着将从 aSat2 的有利位置观察 aSat1。

```
Create Spacecraft aSat aSat2

aSat2.X = 19500
aSat2.Z = 10000

Create Propagator aProp

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, aSat2, Earth,}

anOrbitView.CoordinateSystem = EarthMJ2000Eq
anOrbitView.ViewPointReference = Earth
anOrbitView.ViewPointVector = aSat2
anOrbitView.ViewDirection = aSat
anOrbitView.ViewScaleFactor = 1.0
anOrbitView.ViewUpCoordinateSystem = EarthMJ2000Eq
anOrbitView.ViewUpAxis = Z

BeginMissionSequence

Propagate aProp(aSat, aSat2){aSat.ElapsedSecs = 12000.0}
```

说明：从 aSat2 位置观察 aSat1，双航天器共同传播 12000 秒。

**日-地-月 L1 旋转系轨道视图**：本例展示在日-地-月旋转坐标系中的地球和航天器。`ViewPointReference` 字段设为对象（即 ESL1），故 ViewPointRef 向量在 SunEarthMoonL1 旋转坐标系中为 [0 0 0]。`ViewPointVector` 字段设为向量（即 [0 0 30000]），这意味着视图从 SunEarthMoonL1 坐标系 z 轴上、该坐标系 XY 平面上方 30000 km 处观察。`ViewDirection` 字段也设为对象（即 ESL1），即从 SunEarthMoonL1 坐标系 XY 平面上方 30000 km 处看去的观察方向朝向 ESL1。注意本例中 `ViewScaleFactor` 设为 25，这只是把 `ViewPointVector` 字段缩放或放大到其原始值的 25 倍。

```
Create Spacecraft aSat

aSat.DateFormat = UTCGregorian;
aSat.Epoch            = '01 Apr 2013 00:00:00.000' 
aSat.CoordinateSystem = EarthMJ2000Eq
aSat.DisplayStateType = Cartesian
aSat.X  = 1429457.8833484
aSat.Y  = 147717.32846679
aSat.Z  = -86529.655549364
aSat.VX = -0.037489820883615                     
aSat.VY = 0.32032521614858
aSat.VZ = 0.15762889268226

Create Barycenter EarthMoonBarycenter
EarthMoonBarycenter.BodyNames = {Earth, Luna}

Create LibrationPoint ESL1
ESL1.Primary   = Sun
ESL1.Secondary = EarthMoonBarycenter
ESL1.Point     = L1

Create ForceModel aFM
aFM.CentralBody = Earth
aFM.PointMasses = {Luna, Sun}

Create Propagator aProp
aProp.FM = aFM

Create CoordinateSystem SunEarthMoonL1
SunEarthMoonL1.Origin  = ESL1
SunEarthMoonL1.Axes    = ObjectReferenced
SunEarthMoonL1.XAxis   = R
SunEarthMoonL1.ZAxis   = N
SunEarthMoonL1.Primary = Sun
SunEarthMoonL1.Secondary = EarthMoonBarycenter

Create OrbitView anOrbitView
anOrbitView.Add                    = {aSat, Earth, Sun}
anOrbitView.CoordinateSystem       = SunEarthMoonL1
anOrbitView.ViewPointReference     = ESL1
anOrbitView.ViewPointVector        = [ 0 0 30000 ]
anOrbitView.ViewDirection          = ESL1
anOrbitView.ViewScaleFactor        = 25
anOrbitView.ViewUpCoordinateSystem = SunEarthMoonL1
anOrbitView.ViewUpAxis             = Z

BeginMissionSequence
Propagate aProp(aSat) {aSat.ElapsedDays = 15}
```

说明：定义日-地/月质心 L1 点与相应的 ObjectReferenced 旋转坐标系，从 L1 上方观察并放大 25 倍，传播 15 天。

### 使用 OrbitView 资源的 View Definition 面板时的行为

目前在 `OrbitView` 资源的 View Definition（视图定义）面板中，`ViewPointReference`、`ViewPointVector` 和 `ViewDirection` 等字段会被初始化，但在任务运行期间不会动态更新。`OrbitView` 资源的 View Definition 面板在初始历元时刻设置几何关系，此后由鼠标控制仿真的几何关系。

### GMAT OrbitView 中的航天器模型注意事项

GMAT 通过读取描述航天器形状和颜色的 3D Studio 文件中的模型数据来显示航天器模型。这些文件的扩展名为 .3ds，通常称为 3ds 文件。3ds 文件包含定义航天器轮廓顶点的三维坐标的数据、把这些顶点映射为用于创建航天器显示表面的三角形的映射，以及用于填充所显示三角形的颜色和纹理贴图信息。

GMAT 的航天器模型实现可以显示最多由 200,000 个顶点组成的模型，这些顶点最多映射 100,000 个三角形。GMAT 模型最多可使用 500 个单独的颜色或纹理贴图来填充这些三角形。

### 在 OrbitView 的 Add 字段中指定空括号时的行为

使用 `OrbitView.Add` 字段时，如果括号内没有填入用户自定义的航天器，GMAT 会关闭 `OrbitView` 资源，不生成任何图。如果在 `Add` 字段为空括号的情况下运行脚本，GMAT 会在消息窗口中抛出警告消息，提示由于没有向图添加任何 SpacePoint，`OrbitView` 资源将被关闭。会产生此类警告消息的示例脚本片段：

```
Create Spacecraft aSat aSat2
Create Propagator aProp

Create OrbitView anOrbitView
anOrbitView.Add = {}

BeginMissionSequence
Propagate aProp(aSat, aSat2){aSat.ElapsedSecs = 12000.0}
```

说明：`Add` 为空集合，运行时 GMAT 将给出警告并关闭该轨道视图。
## 示例

传播航天器 1 天，并在每个积分步绘制轨道：

```
Create Spacecraft aSat
Create Propagator aProp

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1}
```

说明：创建航天器、传播器和轨道视图，传播 1 天并绘制轨迹。

在迭代过程中绘制轨道。注意 `SolverIterations` 字段选为 `All`，即所有迭代/扰动都会被绘制：

```
Create Spacecraft aSat
Create Propagator aProp

Create ImpulsiveBurn TOI
Create DifferentialCorrector aDC

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}
anOrbitView.SolverIterations = All

BeginMissionSequence

Propagate aProp(aSat) {aSat.Earth.Periapsis}

Target aDC
  Vary aDC(TOI.Element1 = 0.24, {Perturbation = 0.001, Lower = 0.0, ...
  Upper = 3.14159, MaxStep = 0.5})
  Maneuver TOI(aSat)
  Propagate aProp(aSat) {aSat.Earth.Apoapsis}
  Achieve aDC(aSat.Earth.RMAG = 42165)
EndTarget
```

说明：在差分校正目标定位循环中绘制所有迭代的轨迹，目标为远地点 RMAG = 42165 km。

绘制航天器绕非默认中心天体的轨迹。本例展示如何绘制航天器绕月球的轨迹：

```
Create Spacecraft aSat
  
Create CoordinateSystem LunaMJ2000Eq
LunaMJ2000Eq.Origin = Luna
LunaMJ2000Eq.Axes = MJ2000Eq

aSat.CoordinateSystem = LunaMJ2000Eq
aSat.SMA = 7300
aSat.ECC = 0.4
aSat.INC = 90
aSat.RAAN = 270
aSat.AOP = 315
aSat.TA = 180

Create ForceModel aFM
aFM.CentralBody = Luna
aFM.PointMasses = {Luna}

Create Propagator aProp
aProp.FM = aFM

Create OrbitView anOrbitView

anOrbitView.Add = {aSat, Luna}
anOrbitView.CoordinateSystem = LunaMJ2000Eq
anOrbitView.ViewPointReference = Luna
anOrbitView.ViewDirection = Luna

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1}
```

说明：在以月球为中心的坐标系中传播并绘制环月轨道 1 天。

绘制航天器绕非默认中心天体的轨迹。本例展示如何绘制航天器绕火星的轨迹：

```
Create Spacecraft aSat

Create CoordinateSystem MarsMJ2000Eq
MarsMJ2000Eq.Origin = Mars
MarsMJ2000Eq.Axes = MJ2000Eq

aSat.CoordinateSystem = MarsMJ2000Eq
aSat.SMA = 7300
aSat.ECC = 0.4
aSat.INC = 90
aSat.RAAN = 270
aSat.AOP = 315
aSat.TA = 180

Create ForceModel aFM
aFM.CentralBody = Mars
aFM.PointMasses = {Mars}

Create Propagator aProp
aProp.FM = aFM

Create OrbitView anOrbitView

anOrbitView.Add = {aSat, Mars}
anOrbitView.CoordinateSystem = MarsMJ2000Eq
anOrbitView.ViewPointReference = Mars
anOrbitView.ViewDirection = Mars

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1}
```

说明：在以火星为中心的坐标系中传播并绘制绕火星轨道 1 天。

绘制航天器绕非默认中心天体的轨迹。本例展示如何绘制航天器绕太阳的轨迹。这是一条行星际轨迹：航天器先在 EarthView 中显示为出射双曲线轨迹，然后在 SunView 中绘制绕太阳的行星际轨迹，同时显示火星绕太阳的轨道：

```
Create Spacecraft aSat

aSat.CoordinateSystem = EarthMJ2000Eq
aSat.DateFormat = UTCGregorian
aSat.Epoch = '18 Nov 2013 20:26:24.315'

aSat.X = 3728.345810006184
aSat.Y = 4697.943961035268
aSat.Z = -2784.040094879185
aSat.VX = -9.502477543864449
aSat.VY = 5.935188001372066
aSat.VZ = -2.696272103530009

Create ForceModel aFM
aFM.CentralBody = Earth
aFM.PointMasses = {Earth}

Create ForceModel bFM
aFM.CentralBody = Sun
aFM.PointMasses = {Sun}

Create Propagator aProp
aProp.FM = aFM

Create Propagator bProp
aProp.FM = bFM

Create CoordinateSystem SunEcliptic
SunEcliptic.Origin = Sun
SunEcliptic.Axes = MJ2000Ec

Create OrbitView EarthView SunView

EarthView.Add = {aSat, Earth}
EarthView.CoordinateSystem = EarthMJ2000Eq
EarthView.ViewPointReference = Earth
EarthView.ViewDirection = Earth

SunView.Add = {aSat, Mars, Sun}
SunView.CoordinateSystem = SunEcliptic
SunView.ViewPointReference = Sun
SunView.ViewDirection = Sun
SunView.ViewPointVector = [ 0 0 500000000 ]

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 3}
Propagate bProp(aSat) {aSat.ElapsedDays = 225}
```

说明：先用地球中心力模型传播 3 天（地球视图），再用太阳中心力模型传播 225 天（太阳黄道视图），展示行星际转移轨迹。