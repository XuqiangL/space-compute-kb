# 成像仪（Imager）
> 译自 GMAT R2026a 帮助文档 Imager.html

**Imager** —— 具有定义视场的成像仪。

## 描述

GMAT 的许多资源（包括 Spacecraft 和 IntrusionLocator）使用 Imager 资源来仿真物体何时穿过航天器相机的视场。

另请参阅：Spacecraft、IntrusionLocator

## 字段

| 字段 | 描述 |
|------|------|
| **FieldOfView** | 对可选视场（field-of-view）对象的引用，该对象对成像仪可见区域建模。<br>数据类型：FOV 资源；允许值：CustomFOV、ConicalFOV 或 RectangularFOV 资源；访问：set；默认值：空；单位：N/A；接口：脚本 |
| **DirectionX** | 视场瞄准（boresight）矢量在航天器本体坐标中表达的 X 分量。<br>数据类型：Real；允许值：实数；访问：set；默认值：1；单位：N/A；接口：脚本 |
| **DirectionY** | 视场瞄准矢量在航天器本体坐标中表达的 Y 分量。<br>数据类型：Real；允许值：实数；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **DirectionZ** | 视场瞄准矢量在航天器本体坐标中表达的 Z 分量。<br>数据类型：Real；允许值：实数；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **SecondDirectionX** | 在本体坐标系中表达的、用于确定敏感器绕瞄准矢量姿态的矢量的 X 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **SecondDirectionY** | 在本体坐标系中表达的、用于确定敏感器绕瞄准矢量姿态的矢量的 Y 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：1；单位：N/A；接口：脚本 |
| **SecondDirectionZ** | 在本体坐标系中表达的、用于确定敏感器绕瞄准矢量姿态的矢量的 Z 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **HWOriginInBCSX** | 成像仪坐标系原点在航天器本体坐标系中表达的 X 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **HWOriginInBCSY** | 成像仪坐标系原点在航天器本体坐标系中表达的 Y 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：N/A；接口：脚本 |
| **HWOriginInBCSZ** | 成像仪坐标系原点在航天器本体坐标系中表达的 Z 分量。<br>数据类型：Real；允许值：Real；访问：set；默认值：0；单位：N/A；接口：脚本 |

## 备注

成像仪模型支持遮蔽（mask）、方向和位置设置。遮蔽由 FieldOfView 指定的对象提供。位置是敏感器坐标系原点的位置，在航天器本体坐标系中表达。方向表示为方向余弦矩阵，最初由用户以 Direction 和 SecondDirection 分量提供的两个不共线矢量计算得出。以本体坐标表达的敏感器坐标系的三个轴按如下方式计算：

1. 归一化 **z** 和 **v**，其中 **z** 是由 Direction 表示的瞄准方向，**v** 为 SecondDirection 矢量。
2. 计算法向 N = z × v 及其模 m。
3. 验证 **N** 的模不为 0.0，如果过于接近则发出消息。当输入矢量之一为零矢量，或两个矢量共线（包括它们指向相反方向的情况）时，会出现这种情况。
4. **x** = **N** / m
5. **y** = **z** × **x**
6. 旋转矩阵 **R**sb 由 **x** 为第一行、**y** 为第二行、**z** 为第三行构成。该矩阵将矢量从本体坐标系旋转到敏感器坐标系。

**R**sb 用作检查某物体是否在视场内的变换链的一部分。一般方法是：在给定参考系中取得从成像仪到物体的矢量，然后进行一系列旋转，其中最后一步使用 **R**sb 将矢量从航天器坐标系旋转到成像仪坐标系。瞄准方向的默认方向沿其所挂接本体的 z 轴。注意，**Direction** 和 **SecondDirection** 的默认值分别为 [0,0,1] 和 [-1,0,0]。选择此默认方向是为了匹配带有指向上方的 **Imager** 的 **GroundStation** 的正确方向，其中 **SecondDirection** 与站心（topocentric）坐标系中的北向一致。

## 示例

将 Imager 挂接到 Spacecraft 资源类型。

```
Create Imager SatImager 

Create Spacecraft Sat
Sat.AddHardware = {SatImager};

BeginMissionSequence;
```

说明：本示例创建成像仪 SatImager，创建航天器 Sat，并将成像仪挂接到航天器。

定义成像仪的视场、方向和位置。

```
% Define a conical FOV
Create ConicalFOV coneFOV;
coneFOV.FieldOfViewAngle = 20;

% Create an imager and attache a FOV
Create Imager myImager;
myImager.FieldOfView = coneFOV;

% Define the antenna boresight direction in body coordinates
myImager.DirectionX = 1;
myImager.DirectionY = 0;
myImager.DirectionZ = 0;

% Define the vector to resolve orientation about boresight
myImager.SecondDirectionX = 0;
myImager.SecondDirectionY = 1;
myImager.SecondDirectionZ = 0;

% Define the location of antenna in body coordinates
myImager.HWOriginInBCSX = 100;
myImager.HWOriginInBCSY = -100;
myImager.HWOriginInBCSZ = 0;
```

说明：本示例先创建半锥角为 20 度的圆锥视场 coneFOV；然后创建成像仪 myImager 并挂接该视场；接着定义瞄准方向为本体 X 轴、用于确定绕瞄准方向姿态的第二方向为 Y 轴；最后定义成像仪在本体坐标中的安装位置。
