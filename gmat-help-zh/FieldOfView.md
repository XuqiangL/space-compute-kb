# 视场（FieldOfView）
> 译自 GMAT R2026a 帮助文档 FieldOfView.html

**Field-Of-View** —— 对硬件资源的遮蔽（mask）或视场建模。

## 描述

GMAT 支持三种视场资源：ConicalFOV、RectangularFOV 和 CustomFOV。这些资源用于对敏感器和天线的遮蔽建模（目前用于图形显示），并可添加到选定的硬件资源。有关每种视场资源的详细讨论，请参阅"备注"部分。

另请参阅：Antenna

## 字段

| 字段 | 描述 |
|------|------|
| **Alpha** | 图形显示中敏感器视场的透明度。<br>数据类型：Integer；允许值：0 到 255。0 表示完全透明，255 表示完全不透明；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **AngleWidth** | 视场内各点相对参考点（硬件坐标系 +X 轴）的最大时钟角距离。仅适用于 RectangularFOV 资源。<br>数据类型：Real；允许值：0 到 180；访问：set；默认值：30；单位：N/A；接口：脚本 |
| **AngleHeight** | 视场内各点相对瞄准方向（硬件坐标系 +Z 轴）的最大锥角距离。仅适用于 RectangularFOV 资源。<br>数据类型：Real；允许值：0 到 90；访问：set；默认值：10；单位：degrees；接口：脚本 |
| **Azimuth** | 包含视场边界上各点方位角的数组。此数组与 ConeAngles 或 Elevation 结合使用。仅适用于 CustomFOV 资源。<br>数据类型：实数数组；允许值：实数数组，每个元素在 0 到 360 范围内；访问：set；默认值：空数组；单位：Degrees；接口：脚本 |
| **ClockAngles** | 包含视场边界上各点时钟角的数组。此数组与 ConeAngles 结合使用。仅适用于 CustomFOV 资源。<br>数据类型：实数数组；允许值：实数数组，每个元素在 -180 到 180 范围内；访问：set；默认值：空数组；单位：Degrees；接口：脚本 |
| **Color** | 图形中显示的敏感器视场的颜色。<br>数据类型：整数数组或字符串；允许值：有效的预定义颜色，或表示红、绿、蓝值（范围 0 到 255）的整数三元组；访问：set；默认值：[0 0 0] 或 Black；单位：N/A；接口：GUI、脚本 |
| **ConeAngles** | 包含视场边界上各点锥角的数组。此数组与 ClockAngles 结合使用。仅适用于 CustomFOV 资源。<br>数据类型：实数数组；允许值：实数数组，每个元素在 0 到 180 范围内；访问：set；默认值：空数组；单位：Degrees；接口：脚本 |
| **Elevation** | 包含视场边界上各点高度角的数组。注意，高度角是相对于与敏感器瞄准方向相切的平面度量的。此数组与 Azimuth 或 ClockAngles 结合使用。仅适用于 CustomFOV 资源。<br>数据类型：实数数组；允许值：实数数组，每个元素在 -90 到 90 范围内；访问：set；默认值：空数组；单位：Degrees；接口：脚本 |
| **FieldOfViewAngle** | 圆锥敏感器视场的半角。仅适用于 ConicalFOV 资源。<br>数据类型：Real；允许值：0 < FieldOfViewAngle ≤ 90；访问：set；默认值：30；单位：degrees；接口：脚本 |
| **FOVFileName** | FOV 文件的名称和路径。仅适用于 CustomFOV 资源。<br>数据类型：String；允许值：每行包含有效锥角和时钟角的文本文件；访问：set；默认值：none；单位：角度以度为单位；接口：脚本 |
| **InterpolationStepSize** | 对遮蔽文件执行球面线性插值时所取的步长。可设为 0.0 以禁用。仅适用于 CustomFOV，且仅在使用 Azimuth 和 Elevation 定义角度时适用。<br>数据类型：Real；允许值：0.0 或 0.2 到 180.0 之间（含）的值；访问：set；默认值：0.2 degrees；单位：角度以度为单位；接口：脚本 |

## 备注

视场对象定义敏感器遮蔽（视场边界的表示），用于图形应用。GMAT 的未来版本将能够判断给定矢量（例如航天器-太阳矢量）是否在敏感器视场内。

> **注意**：敏感器在本体坐标系中的位置和方向在 Antenna 资源上配置。硬件对象在航天器本体坐标系中的方向与航天器姿态一起，用于在参考系和硬件坐标系之间旋转变换矢量。按照惯例，敏感器瞄准方向为敏感器坐标系的 +Z 轴。

### 配置 ConicalFOV

ConicalFOV 对象对圆锥视场建模，可用其锥角（瞄准方向与视场边缘之间的夹角）表示。该角度保持恒定，视场遮蔽可视为单位球面上的一个圆。

配置一个 ConicalFOV：

```
% Create the ConicalFOV object
Create ConicalFOV cone1;
cone1.FieldOfViewAngle = 60;
cone1.Color = Blue;
cone1.Alpha = 255;  %the field of view is fully opaque

% Attach the FOV object to an antenna
Create Antenna antenna1;
antenna1.FieldOfView = cone1;
```

说明：本示例创建圆锥视场 cone1，半锥角 60 度，颜色为蓝色，Alpha 为 255（视场完全不透明）；然后创建天线 antenna1 并将该视场挂接到天线。

### 配置 RectangularFOV

RectangularFOV 资源对四角由角宽度和角高度限制定义的视场建模。RectangularFOV 对象对由锥角和时钟角限制定义的视场建模。（锥角，时钟角）对定义单位球面上的一个点。与假设所有时钟角上锥角均相同的圆锥敏感器不同，锥角沿位于硬件坐标系 X-Z 平面内的"本初子午线"度量。正锥角朝 +X 轴方向度量，负锥角朝 -X 轴方向度量。

配置一个 RectangularFOV：

```
% Create the RectangularFOV object
Create RectangularFOV box1;
box1.AngleHeight = 20;
box1.AngleWidth  = 50;
box1.Color = [255 255 0];  % Yellow
box1.Alpha = 255;  %the field of view is fully opaque

% Attach the FOV object to an antenna
Create Antenna antenna1;
antenna1.FieldOfView = cone1;
```

说明：本示例创建矩形视场 box1，角高 20 度、角宽 50 度，颜色为黄色 [255 255 0]，Alpha 为 255（完全不透明）；然后创建天线 antenna1 并挂接视场。

### 配置 CustomFOV

CustomFOV 将视场边界建模为单位球面上的一系列点，由（锥角，时钟角）或（方位角，高度角）角度对表示。CustomFOV 可用于建模不规则的敏感器视场。注意，锥角相对于天顶方向度量，高度角相对于水平面度量。

GMAT 有两种方式确定两个已定义点之间的 FOV 边界：

1. GMAT 将 FOV 视为多面体，两点之间的边界由这两点与原点构成的平面定义。当 FOV 点使用锥角和时钟角定义，或 InterpolationStepSize = 0 时，使用此方法。
2. GMAT 在方位角 0 到 360 范围内按 InterpolationStepSize 定义的步长，对 FOV 的高度角进行线性插值。当 FOV 点使用方位角和高度角定义且 InterpolationStepSize 非零时（InterpolationStepSize 默认值为 0.2 度），使用此方法。最终遮蔽将是用户定义点集与插值生成的点的并集。

> **警告**：CustomFOV 使用若尔当曲线定理（Jordan Curve Theorem）来判断某点是否在敏感器内。GMAT 的未来版本将公开该接口以提供敏感器覆盖计算。重要的是，CustomFOV 中的任何线段都不得相互交叉。

> **警告**：当计划在使用 SPICE 的功能（即事件定位）中使用 CustomFOV 时，相对两侧方位上的点不能同时具有处于或接近零的高度角。这会导致角半径接近 90 度，从而引发 SPICE 错误。用于 SPICE 时，角半径必须低于 89.999942704220 度。

配置一个 CustomFOV：

```
% Create a CustomFOV from a text file of cone and clock angles
Create CustomFOV fov;
fov.FOVFileName = 'ConeClockAngles.txt';

% ... or alternatively, create a CustomFOV by 
fov.ClockAngles = [ 15.0 25.0 35.0];
fov.ConeAngles  = [ 30.0 45.0 60.0];

% ... or alternatively, create an equivalent CustomFOV by 
fov.Azimuth    = [ 15.0 25.0 35.0];
fov.Elevation  = [ 60.0 45.0 30.0];

% Attach the FOV object to an antenna
Create Antenna antenna1;
antenna1.FieldOfView = fov;
```

说明：本示例展示三种创建 CustomFOV 的方式：从锥角/时钟角文本文件 'ConeClockAngles.txt' 读取；或直接指定 ClockAngles = [15 25 35]、ConeAngles = [30 45 60]；或等效地指定 Azimuth = [15 25 35]、Elevation = [60 45 30]；最后将视场挂接到天线 antenna1。

下面的示例包含上例所用遮蔽文件的内容。遮蔽文件由以度为单位的时钟角和锥角对组成。时钟角和锥角对位于同一行，时钟角在前，锥角在后。关键字 `ClockConeAngles` 指定角度对为时钟角和锥角。或者，用户可以使用 `AzimuthElevationAngles` 关键字指定方位角和高度角。文件中必须存在角度类型关键字。

```
ClockConeAngles

15.0  30.0
25.0  45.0
35.0  60.0
```

说明：该遮蔽文件首行以关键字 ClockConeAngles 声明角度类型，随后每行为一对时钟角和锥角（单位：度）。
