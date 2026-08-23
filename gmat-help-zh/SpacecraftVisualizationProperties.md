# 航天器可视化属性（Spacecraft Visualization Properties）
> 译自 GMAT R2026a 帮助文档 SpacecraftVisualizationProperties.html

**SpacecraftVisualizationProperties —— 航天器的可视化属性**

## 描述

航天器可视化属性（Spacecraft Visualization Properties）允许你定义航天器模型、沿 X、Y、Z 方向平移航天器，或对模型的姿态（attitude）朝向施加固定旋转。你还可以调整航天器模型大小的比例因子。GMAT 也允许通过航天器可视化属性设置轨道颜色：可以为航天器轨道轨迹，以及迭代过程中绘制的任何摄动轨迹设置颜色。有关如何使用 `Spacecraft` 对象的 `OrbitColor` 和 `TargetColor` 字段设置轨道颜色的讨论与示例，请参阅 `Color` 文档；也可参阅下文"字段"一节进一步了解这两个字段。航天器可视化属性既可以通过 GMAT 的 GUI 配置，也可以通过脚本接口配置。

**另请参阅**：`OrbitView`、`Color`

## 字段

### ModelOffsetX

该字段允许你沿中心天体（central body）坐标系的 +X 或 -X 轴平移航天器。

- 数据类型：实数（Real）
- 允许值：-3.5 <= Real <= 3.5
- 访问权限：仅可设置（set）
- 默认值：0.000000
- 单位：N/A
- 接口：GUI、脚本

### ModelOffsetY

允许你沿中心天体坐标系的 +Y 或 -Y 轴平移航天器。

- 数据类型：实数（Real）
- 允许值：-3.5 <= Real <= 3.5
- 访问权限：仅可设置（set）
- 默认值：0.000000
- 单位：N/A
- 接口：GUI、脚本

### ModelOffsetZ

允许你沿中心天体坐标系的 +Z 或 -Z 轴平移航天器。

- 数据类型：实数（Real）
- 允许值：-3.5 <= Real <= 3.5
- 访问权限：仅可设置（set）
- 默认值：0.000000
- 单位：N/A
- 接口：GUI、脚本

### ModelRotationX

允许你绕中心天体坐标系的 X 轴，对航天器姿态施加固定旋转。

- 数据类型：实数（Real）
- 允许值：-180 <= Real <= 180
- 访问权限：仅可设置（set）
- 默认值：0.000000
- 单位：Deg.
- 接口：GUI、脚本

### ModelRotationY

允许你绕中心天体坐标系的 Y 轴，对航天器姿态施加固定旋转。

- 数据类型：实数（Real）
- 允许值：-180 <= Real <= 180
- 访问权限：仅可设置（set）
- 默认值：0.000000
- 单位：Deg.
- 接口：GUI、脚本

### ModelRotationZ

允许你绕中心天体坐标系的 Z 轴，对航天器姿态施加固定旋转。

- 数据类型：实数（Real）
- 允许值：-180 <= Real <= 180
- 访问权限：仅可设置（set）
- 默认值：0.000000
- 单位：Deg.
- 接口：GUI、脚本

### ModelScale

允许你对航天器模型的大小应用比例因子。

- 数据类型：实数（Real）
- 允许值：0.001 <= Real <= 1000
- 访问权限：仅可设置（set）
- 默认值：3.000000
- 单位：N/A
- 接口：GUI、脚本

### ModelFile

允许你加载 .3ds 模型格式的航天器模型。

- 数据类型：字符串（String）
- 允许值：仅 .3ds 航天器模型格式
- 访问权限：仅可设置（set）
- 默认值：`../data/vehicle/models/aura.3ds`
- 单位：N/A
- 接口：GUI、脚本

### OrbitColor

允许你为航天器轨道设置可用颜色。航天器轨道通过 `OrbitView` 图形显示绘制。颜色可以通过字符串或整数数组指定。例如，将航天器轨道颜色设为红色有以下两种方式：`DefaultSC.OrbitColor = Red` 或 `DefaultSC.OrbitColor = [255 0 0]`。此字段也可以在任务序列（Mission Sequence）中修改。

- 数据类型：整数数组或字符串（Integer Array or String）
- 允许值：GUI 中轨道颜色选择器（Orbit Color Picker）可用的任何颜色；有效的预定义颜色名称，或 0 到 255 之间的 RGB 三元组值
- 访问权限：仅可设置（set）
- 默认值：Red
- 单位：N/A
- 接口：GUI、脚本

### TargetColor

允许你在差分修正（Differential Correction）或优化（Optimization）等迭代过程中，为航天器的摄动轨迹设置可用颜色。摄动轨迹通过 `OrbitView` 资源绘制。目标颜色可以通过字符串或整数数组指定。例如，将航天器摄动轨迹设为黄色有以下两种方式：`DefaultSC.TargetColor = Yellow` 或 `DefaultSC.TargetColor = [255 255 0]`。此字段也可以在任务序列（Mission Sequence）中修改。

- 数据类型：整数数组或字符串（Integer Array or String）
- 允许值：GUI 中轨道颜色选择器（Orbit Color Picker）可用的任何颜色；有效的预定义颜色名称，或 0 到 255 之间的 RGB 三元组值
- 访问权限：仅可设置（set）
- 默认值：Teal
- 单位：N/A
- 接口：GUI、脚本

## GUI

下图显示了航天器可视化属性资源的默认设置：

> [图：Spacecraft 可视化属性的默认设置界面]

航天器可视化属性的 GUI 界面位于 `Spacecraft` 资源的 Visualization（可视化）选项卡中。你可以配置航天器的可视化属性，并在 Display（显示）窗口中直观地查看更改效果。

在 Display 窗口中，你可以按住鼠标**左键**拖动来改变相机朝向，相机朝向可沿上/下/左/右方向改变。你也可以按住鼠标**右键**拖动来缩放 Display 窗口：按住右键并向上移动光标可缩小，向下移动光标可放大。

## 备注

### 配置航天器可视化属性

GMAT 允许你定义任意航天器模型，但目前 GMAT 仅支持 .3ds 模型格式。NASA 网站（http://www.nasa.gov/multimedia/3d_resources/models.html）提供了若干 .3ds 航天器模型，你也可以在 http://www.celestiamotherlode.net/ 下载更多 .3ds 模型。这些模型大多为 .3ds 格式，可被大多数 3D 程序读取。

GMAT 允许你对航天器模型的姿态朝向施加固定旋转，或沿 X、Y、Z 任一方向平移模型，还可以对所选航天器模型应用比例因子以调整模型大小。对航天器模型、姿态朝向、平移或比例因子所做的任何更改，也会显示在 `OrbitView` 资源的图形窗口中。配置好的航天器可视化属性只有在运行任务之后才会显示在 OrbitView 图形窗口中。请参阅 `OrbitView` 资源的用户说明文档，进一步了解 OrbitView 图形窗口。

## 示例

此示例展示如何配置航天器可视化属性资源。所有值均为非默认值。

```
Create Spacecraft aSat
aSat.ModelFile = '../data/vehicle/models/aura.3ds'
aSat.ModelOffsetX = 1.5
aSat.ModelOffsetY = -2
aSat.ModelOffsetZ = 3
aSat.ModelRotationX = 180
aSat.ModelRotationY = 180
aSat.ModelRotationZ = 90
aSat.ModelScale = 15

Create Propagator aProp

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}

BeginMissionSequence
Propagate aProp(aSat) {aSat.ElapsedSecs = 9000}
```

**中文说明**：创建航天器 `aSat`，加载 aura.3ds 模型，设置模型在 X/Y/Z 方向的平移偏移、绕三轴的固定旋转角以及 15 倍缩放；再创建传播器 `aProp` 和轨道视图 `anOrbitView`，传播 9000 秒后即可在图形窗口中查看效果。