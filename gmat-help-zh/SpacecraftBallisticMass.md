# 航天器弹道/质量特性（Spacecraft Ballistic/Mass Properties）
> 译自 GMAT R2026a 帮助文档 SpacecraftBallisticMass.html

**Spacecraft Ballistic/Mass Properties —— 航天器的物理特性**

## 描述

航天器（Spacecraft）的弹道与质量特性包括阻力面积（drag area）和光压面积（SRP area）及相应系数，以及航天器干重（dry mass）。这些量主要用于轨道动力学建模。GMAT 支持球形（spherical）SRP 和阻力模型，以及一种称为 SPAD 的更高保真度的阻力与面积模型。

GMAT 还支持一组扩展质量特性，用于建模力矩（torque）和角动量变化。航天器的扩展质量特性是航天器干态质心（dry center of mass）和干态转动惯量（dry moment of inertia）。

标准和扩展质量特性模型都会与 **FuelTank**（燃料箱）模型协同工作，计算干态航天器质量特性与箱内推进剂质量特性聚合后的结果。具体做法详见"备注"一节。

**另请参阅**：`Propagate`、`Propagator`、`Spacecraft`、`ChemicalTank`

## 字段

### AddPlates

用于 NPlate 面积模型。选择构成航天器面积模型的 `Plate`（平板）对象。另请参阅 `Plate`。

- 数据类型：资源数组（Resource array）
- 允许值：`Plate` 资源的实例
- 访问权限：仅可设置（Set）
- 默认值：空（Empty）
- 单位：不适用
- 接口：脚本

### AtmosDensityScaleFactor

对所选密度模型计算出的标称大气密度施加的乘性比例因子。

- 数据类型：实数（Real）
- 允许值：Real > 0
- 访问权限：仅可设置（Set）
- 默认值：1.0
- 单位：无量纲（dimensionless）
- 接口：脚本

### Cd

阻力系数（coefficient of drag），用于球形阻力面积模型中计算阻力引起的加速度。使用 SPAD 阻力建模时忽略此参数。

- 数据类型：实数（Real）
- 允许值：Real >= 0
- 访问权限：set、get
- 默认值：2.2
- 单位：无量纲（dimensionless）
- 接口：GUI、脚本

### CenterOfMassOffsetX

质心偏移量的 X 分量。该偏移仅用于 "Lookup"（查表）模型，用于计入预先列表数据未考虑的因素所造成的偏差。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：m
- 接口：脚本

### CenterOfMassOffsetY

质心偏移量的 Y 分量。该偏移仅用于 "Lookup" 模型，用于计入预先列表数据未考虑的因素所造成的偏差。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：m
- 接口：脚本

### CenterOfMassOffsetZ

质心偏移量的 Z 分量。该偏移仅用于 "Lookup" 模型，用于计入预先列表数据未考虑的因素所造成的偏差。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：m
- 接口：脚本

### CenterOfMassTableFileName

包含不同航天器总质量对应质心插值数据的文件名。总质量包括航天器干重和燃料箱内容物的质量。

- 数据类型：字符串（String）
- 允许值：有效的质心查表文件名
- 访问权限：仅可设置（set）
- 默认值：N/A
- 单位：N/A
- 接口：脚本

### Cr

反射系数（coefficient of reflectivity），用于球形面积模型中计算光压（SRP）引起的加速度。值为 0 表示航天器对入射辐射是"透明"的；值为 1.0 表示所有辐射被吸收，全部的力传递给航天器；值为 2.0 表示所有辐射被反射，两倍的力传递给航天器。使用 SPAD SRP 建模时忽略此参数。

- 数据类型：实数（Real）
- 允许值：Real >= 0
- 访问权限：set、get
- 默认值：1.8
- 单位：无量纲（dimensionless）
- 接口：GUI、脚本

### Drag Area（DragArea，阻力面积）

用于球形阻力面积模型中计算大气阻力加速度的面积。使用 SPAD 阻力建模时忽略此参数。

- 数据类型：实数（Real）
- 允许值：Real >= 0
- 访问权限：set、get
- 默认值：15
- 单位：m^2
- 接口：GUI、脚本

### DryCenterOfMassX

干态航天器质心在 BCS（本体坐标系）中的 X 分量（m）。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：set、get
- 默认值：0.0
- 单位：m
- 接口：脚本

### DryCenterOfMassY

干态航天器质心在 BCS 中的 Y 分量（m）。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：set、get
- 默认值：0.0
- 单位：m
- 接口：脚本

### DryCenterOfMassZ

干态航天器质心在 BCS 中的 Z 分量（m）。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：set、get
- 默认值：0.0
- 单位：m
- 接口：脚本

### DryMass

航天器的干重（不包括燃料质量）。

- 数据类型：实数（Real）
- 允许值：Real >= 0
- 访问权限：set、get
- 默认值：850
- 单位：kg
- 接口：GUI、脚本
### DryMomentOfInertiaXX

干态航天器转动惯量的 XX 分量。

- 数据类型：实数（Real）
- 允许值：Real >= 0
- 访问权限：set、get
- 默认值：999
- 单位：Kg-m^2
- 接口：脚本

### DryMomentOfInertiaXY

干态航天器转动惯量的 XY 分量。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：set、get
- 默认值：0
- 单位：Kg-m^2
- 接口：脚本

### DryMomentOfInertiaXZ

干态航天器转动惯量的 XZ 分量。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：set、get
- 默认值：0
- 单位：Kg-m^2
- 接口：脚本

### DryMomentOfInertiaYY

干态航天器转动惯量的 YY 分量。

- 数据类型：实数（Real）
- 允许值：Real >= 0
- 访问权限：set、get
- 默认值：999
- 单位：Kg-m^2
- 接口：脚本

### DryMomentOfInertiaYZ

干态航天器转动惯量的 YZ 分量。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：set、get
- 默认值：0
- 单位：Kg-m^2
- 接口：脚本

### DryMomentOfInertiaZZ

干态航天器转动惯量的 ZZ 分量。

- 数据类型：实数（Real）
- 允许值：Real >= 0
- 访问权限：set、get
- 默认值：999
- 单位：Kg-m^2
- 接口：脚本

### ExtendedMassPropertiesModel

选择是否建模质心、转动惯量、两者都建模或都不建模。

- 数据类型：字符串（String）
- 允许值：`None`、`CenterOfMass`、`MomentOfInertia`、`CenterOfMassAndMomentOfInertia`
- 访问权限：仅可设置（set）
- 默认值：**None**
- 单位：N/A
- 接口：脚本

### ExtendedMassPropertiesModelType

选择用于计算质心和转动惯量的模型。可用模型为：对质量特性文件进行插值（"Lookup"），或基于干态航天器质量特性和各 FuelTank 内容物的质量特性计算系统质量特性（"Analytic"）。

- 数据类型：字符串（String）
- 允许值：`Lookup`、`Analytic`
- 访问权限：仅可设置（set）
- 默认值：Analytic
- 单位：N/A
- 接口：脚本

### MassPropertiesTableFilePath

用于插值质心或转动惯量数据的文件所在路径。

- 数据类型：字符串（String）
- 允许值：指向包含质心或转动惯量插值表文本文件的目录的有效路径
- 访问权限：仅可设置（set）
- 默认值：""
- 单位：N/A
- 接口：脚本

### MomentOfInertiaOffsetXX

转动惯量偏移量的 XX 分量。该偏移仅用于 "Lookup" 模型，用于计入预先列表数据未考虑的因素所造成的偏差。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：kg-m^2
- 接口：脚本

### MomentOfInertiaOffsetXY

转动惯量偏移量的 XY 分量。该偏移仅用于 "Lookup" 模型，用于计入预先列表数据未考虑的因素所造成的偏差。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：kg-m^2
- 接口：脚本

### MomentOfInertiaOffsetXZ

转动惯量偏移量的 XZ 分量。该偏移仅用于 "Lookup" 模型，用于计入预先列表数据未考虑的因素所造成的偏差。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：kg-m^2
- 接口：脚本

### MomentOfInertiaOffsetYY

转动惯量偏移量的 YY 分量。该偏移仅用于 "Lookup" 模型，用于计入预先列表数据未考虑的因素所造成的偏差。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：kg-m^2
- 接口：脚本

### MomentOfInertiaOffsetYZ

转动惯量偏移量的 YZ 分量。该偏移仅用于 "Lookup" 模型，用于计入预先列表数据未考虑的因素所造成的偏差。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：kg-m^2
- 接口：脚本

### MomentOfInertiaOffsetZZ

转动惯量偏移量的 ZZ 分量。该偏移仅用于 "Lookup" 模型，用于计入预先列表数据未考虑的因素所造成的偏差。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：kg-m^2
- 接口：脚本

### MomentOfInertiaTableFileName

包含不同航天器总质量对应转动惯量插值数据的文件名。总质量包括航天器干重和燃料箱内容物的质量。

- 数据类型：字符串（String）
- 允许值：有效的转动惯量查表文件名
- 访问权限：仅可设置（set）
- 默认值：N/A
- 单位：N/A
- 接口：脚本
### NPlateSRPEquateAreaCoefficients

在估计时将 NPlate 模型的 SRP 面积系数设为相等（或关联）。当为一个或多个平板估计 `AreaCoefficient` 时，此列表中指定的任何平板在估计过程中都将被强制取相同的 `AreaCoefficient` 值。仅在使用 NPlate 面积模型并解算 `AreaCoefficient` 时适用。

- 数据类型：资源数组（Resource array）
- 允许值：`Plate` 资源的实例
- 访问权限：仅可设置（Set）
- 默认值：空（Empty）
- 单位：不适用
- 接口：脚本

### SPADDragFile

SPAD 阻力模型文件的名称（可选包含路径信息）。

- 数据类型：字符串（String）
- 允许值：有效的路径和 SPAD 文件
- 访问权限：仅可设置（set）
- 默认值：N/A
- 单位：N/A
- 接口：GUI、脚本

### SPADDragInterpolationMethod

SPAD 阻力矢量的插值方法。

- 数据类型：字符串（String）
- 允许值：'Bicubic' 或 'Bilinear'
- 访问权限：仅可设置（set）
- 默认值：Bilinear
- 单位：N/A
- 接口：GUI、脚本

### SPADDragScaleFactor

使用 SPAD 阻力面积模型时施加于阻力的比例因子。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：仅可设置（set）
- 默认值：1.0
- 单位：无量纲（dimensionless）
- 接口：GUI、脚本

### SPADSRPFile

SPAD SRP 模型文件的名称（可选包含路径信息）。

- 数据类型：字符串（String）
- 允许值：有效的路径和 SPAD 文件
- 访问权限：仅可设置（set）
- 默认值：N/A
- 单位：N/A
- 接口：GUI、脚本

### SPADSRPInterpolationMethod

SPAD SRP 模型矢量的插值方法。

- 数据类型：字符串（String）
- 允许值：'Bicubic' 或 'Bilinear'
- 访问权限：仅可设置（set）
- 默认值：Bilinear
- 单位：N/A
- 接口：GUI、脚本

### SPADSRPScaleFactor

使用 SPAD SRP 面积模型时施加于 SRP 力的比例因子。

- 数据类型：实数（Real）
- 允许值：任意实数
- 访问权限：仅可设置（set）
- 默认值：1.0
- 单位：无量纲（dimensionless）
- 接口：GUI、脚本

### SRPArea

用于球形 SRP 面积模型中计算太阳辐射压力（SRP）加速度的面积。使用 SPAD SRP 建模时忽略此参数。

- 数据类型：实数（Real）
- 允许值：Real > 0
- 访问权限：set、get
- 默认值：1
- 单位：m^2
- 接口：GUI、脚本

## GUI

> [图：Spacecraft 资源 Ballistic/Mass 选项卡界面]

弹道与质量特性的 GUI 界面位于 `Spacecraft` 资源的 Ballistic/Mass（弹道/质量）选项卡中。你可以输入用于轨道动力学建模的物理特性，如阻力与 SRP 的面积和系数以及航天器干重。GMAT 支持球形 SRP 模型和 SPAD（Solar Pressure and Aerodynamic Drag，太阳压力与气动阻力）文件。

## 备注

### 为球形面积模型配置面积特性

GMAT 支持用于阻力和 SRP 建模的球形面积模型（有时称为 "cannonball"，即"炮弹"模型）。在球形模型中，假定面积与航天器相对于当地速度矢量和太阳矢量的朝向无关。通过将所配置 `ForceModel` 的 `SRP.SRPModel` 和 `Drag.DragModel` 设为 `Spherical` 来选择球形面积模型。有关阻力与 SRP 模型计算和配置的更多细节，请参阅 `ForceModel` 文档。

### 为 NPlate 面积模型配置面积特性

GMAT 支持用于 SRP 建模的多平板（multi-plate）面积模型。在 NPlate 模型中，面积由一组 `Plate` 资源构成，每个平板各自指定独立的面积、朝向和反射特性。通过将所配置 `ForceModel` 的 `SRP.SRPModel` 设为 `NPlate` 来选择 NPlate 面积模型。NPlate 模型目前不可用于阻力建模。有关 NPlate 模型配置的更多细节，请参阅 `Plate` 文档。

### 为 SPAD 面积模型配置面积特性

SPAD 是 Solar Pressure and Aerodynamic Drag（太阳压力与气动阻力）的缩写。SPAD 文件可用于高保真 SRP 和阻力建模，它计入航天器的物理特性（形状和反射率）以及航天器姿态。SPAD 文件包含列表数据，表示按 Cr 等物理特性（包括镜面反射、漫反射和反射特性）缩放后的航天器面积。SPAD 文件中的面积数据以航天器本体坐标系中的方位角（azimuth）和仰角（elevation）为自变量列表给出。在 SRP 建模中，文件中列表的方位角和仰角应为本体坐标系中表示的、从航天器指向太阳的矢量的方位角和仰角；在阻力建模中，方位角和仰角表示航天器相对于旋转大气的速度矢量方向。通过将所配置 `ForceModel` 的 `SRP.SRPModel` 和 `Drag.DragModel` 设为 `SPADFile` 来选择 SPAD 面积模型。

为在每个积分点计算 SRP 或阻力加速度，GMAT 确定积分时刻太阳矢量或相对速度矢量在航天器本体坐标系中的方位角和仰角，然后使用双线性（bi-linear）或双三次（bi-cubic）插值对 SPAD 数据插值。由于 SRP 或阻力矢量是在航天器本体坐标系中取的，这种公式得到的加速度与姿态相关。有关阻力与 SRP 模型计算和配置的更多细节，请参阅 `ForceModel` 文档。

> **注意**
>
> 使用 SPAD 文件时，GMAT 使用 `Spacecraft` 资源上定义的姿态来计算本体坐标系中的太阳矢量或相对速度矢量。如果姿态使用 `Axes` 设为 `ObjectReferenced` 的坐标系，且这些轴反过来引用 `Spacecraft` 的轨道状态（即 VNB 或 LVLH 系统），GMAT 会在给定积分步内将姿态保持为常值。在这些情况下，建议谨慎选择足够小的最大步长，以确保由此产生的近似对你的应用是可接受的。

下面给出一个有效 SPAD 文件的头部和前三行数据作为示例。注意，GMAT 并不使用文件上提供的所有值；GMAT 对 SPAD 文件的用法在示例下方的表格中有详细说明。

```
Version            : 4.21
System             : sphericalSat
Analysis Type      : Area
Pixel Size         : 5
Spacecraft Size    : 436.2
Pressure           : 1
Center of Mass     :  (50.9, 184.9, -49)
Current time       : May  7, 2009  15:53:38.00

Motion    : 1
  Name    : Azimuth
  Method  : Step
  Minimum : -180
  Maximum : 180
  Step    : 5
Motion    : 2
  Name    : Elevation
  Method  : Step
  Minimum : -90
  Maximum : 90
  Step    : 5
: END

Record count       : 2701

 AzimuthElevatio  Force(X)  Force(Y)  Force(Z)  
 degrees degrees      m^2      m^2      m^2      
 ------- ------- --------- --------- --------- --------- 
 -180.00   -90.00 -0.00000000000000 -0.00000000000000 -8.94500000000000 
 -180.00   -85.00 -0.77960811887780 -0.00000000000000 -8.91096157443066 
 -180.00   -80.00 -1.55328294923069 -0.00000000000000 -8.80910535069420 
```

**中文说明**：该 SPAD 文件示例头部标明分析类型为 Area；两个 Motion 分别定义方位角（-180~180，步长 5）和仰角（-90~90，步长 5）；数据区每行给出某方位角/仰角下的 Force(X/Y/Z) 面积矢量（单位 m^2）。

SPAD 文件包含三个部分，如上所示。每个部分中各项的数据规格在下表中说明。SPAD 文件头可以包含许多字段，但 GMAT 只使用下述少数字段，其他字段被忽略。

| 关键字 | 必需 | 说明与支持值 |
| --- | --- | --- |
| `Analysis Type` | 是 | SPAD 软件可创建 Analysis Type 为 Solar Pressure、Area 和 Drag 的文件。GMAT 仅支持 Area 选项。示例：`Analysis Type : Area` |
| `Pressure` | 否 | SPAD 支持对 SRP 和阻力施加比例因子。GMAT 不读取该值；它在 SPAD 文件中的作用是告知用户文件上的特性已按 Pressure 因子缩放。该值通常为 "1"。但当其不为 1 时，比例因子可能被施加两次：一次来自 SPAD 文件中数据上已施加的值，一次来自 `SPADSRPScaleFactor` 或 `SPADDragScaleFactor`。应注意：如果所需比例因子在创建文件时已施加，则不要在 GMAT 中重复施加。 |
SPAD 文件的 Motion Data（运动数据）部分描述文件正文包含的数据。GMAT 使用的 Motion Data 字段如下所述，其他字段被忽略。

| 关键字 | 必需 | 说明与支持值 |
| --- | --- | --- |
| `Motion` | 是 | Motion 和 Name 字段共同指定文件正文前两列的数据类型。GMAT 目前仅支持 Azimuth 和 Elevation 运动（无活动附件），并要求第一个 Motion 为 Azimuth、第二个 Motion 为 Elevation。示例：`Motion : 1` / `Name : Azimuth`，以及 `Motion : 2` / `Name : Elevation` |
| `Name` | 是 | 与 Motion 字段共同指定文件正文前两列的数据类型。GMAT 目前仅支持 Azimuth 和 Elevation 运动（无活动附件），并要求第一个 Motion 为 Azimuth、第二个 Motion 为 Elevation。示例：`Motion : 1` / `Name : Azimuth`，以及 `Motion : 2` / `Name : Elevation` |
| `Method` | 是 | 自变量的步进方式。唯一支持的值是 Step。示例：`Motion : 1` / `Method : Step` |
| `Maximum` | 是 | 自变量（Motion 类型）的最大值。Azimuth 的 Maximum 必须为 180，Elevation 的 Maximum 必须为 90。示例：`Motion : 1` / `Name : Azimuth` / `Maximum : 180`；`Motion : 2` / `Name : Elevation` / `Maximum : 90` |
| `Minimum` | 是 | 自变量（Motion 类型）的最小值。Azimuth 的 Minimum 必须为 -180，Elevation 的 Minimum 必须为 -90。示例：`Motion : 1` / `Name : Azimuth` / `Minimum : -180`；`Motion : 2` / `Name : Elevation` / `Minimum : -90` |
| `Step` | 是 | 自变量（Motion 类型）的步长。如果 Step 不能整除变量范围，则可能出错，因为最大值和/或最小值可能不在文件上。示例：`Motion : 1` / `Step : 15` |
| `Record count` | 是 | Record count 是数据段中的数据行数。Record count = (360/(Azimuth Step)+1)*(180/(Elevation Step)+1)。示例：`Record count : 325` |

SPAD 文件数据块包含按下表所列的力建模列表数据。

| 关键字 | 必需 | 说明与支持值 |
| --- | --- | --- |
| `Azimuth` | 是 | 方位角数据列，必须是数据的第一列，单位必须是度。方位角是从航天器指向太阳的矢量（对 SRP，atan2(ySun,xSun)）或相对速度矢量（对阻力）在本体坐标系中表达的方位角。示例：见上方代码清单 |
| `Elevation` | 否 | 仰角数据列，必须是数据的第二列，单位必须是度。仰角是从航天器指向太阳的矢量（对 SRP，atan2(zSun,sqrt(xSun^2 + ySun^2))）或相对速度矢量（对阻力）在本体坐标系中表达的仰角。示例：见上方代码清单 |
| `Force(*)` | 否 | 面积矢量列，必须是数据的第 3~5 列。量的基本单位必须是 m^2、mm^2、cm^2、in^2 或 ft^2。如果头部行中提供了其他单位，将抛出异常。面积矢量是所得 SRP 力在航天器本体坐标系中的方向，按面积和反射特性缩放。示例：见上方代码清单 |

### 总质量计算（Total Mass Computation）

`Spacecraft` 的 `TotalMass` 属性是只读属性，等于 `DryMass` 值与所有挂接燃料箱中燃料质量之和。GMAT 的传播器不允许航天器总质量为负。但是，GMAT 允许 `ChemicalTank` 的质量为负。详细信息请参阅 `ChemicalTank` 文档。

### 扩展质量特性：概述

除计算 `Spacecraft` 的 `TotalMass` 属性外，GMAT 还可以计算 `SystemCenterOfMass`（系统质心）和 `SystemMomentOfInertia`（系统转动惯量）属性。与 `TotalMass` 一样，这些属性是只读的，由干态 `Spacecraft` 的相应特性计算得出。所得 `SystemCenterOfMass` 在航天器本体坐标系（BCS）中表示，所得 `SystemMomentOfInertia` 相对于 `SystemCenterOfMass` 给出。

计算扩展质量特性有两种模型：

- `Lookup` 选项：对查找表进行插值，表中以质量为自变量，以质心或转动惯量为因变量；
- `Analytic` 选项：根据干态特性和燃料特性计算系统特性。

截至本文撰写时，`Lookup` 模型已完整实现，`Analytic` 模型仍在开发中。

模型的选择由两个输入参数控制。第一个 `ExtendedMassPropertiesModelType` 控制使用 `Lookup` 还是 `Analytic` 模型；第二个 `ExtendedMassPropertiesModel` 控制计算哪些特性。`TotalMass` 总是会被计算；如果既不需要质心也不需要转动惯量，则将 `ExtendedMassPropertiesModel` 的值设为 `None`（这是默认值）。`ExtendedMassPropertiesModelType` 的默认值是 `Analytic`，这样默认情况下无需指定查表文件。在扩展质量特性的解析模型完成之前，选择 `Analytic` 模型*仅*在 `ExtendedMassPropertiesModel` 设为 `None` 时有效。换句话说，默认是不建模扩展质量特性，只计算 `TotalMass`。其他选项 `CenterOfMass`、`MomentOfInertia` 和 `CenterOfMassAndMomentOfInertia` 的含义不言自明。
### 扩展质量特性：Lookup 模型

使用 `Lookup` 模型有三个要素：指定要使用的文件名、理解查找表文件的格式，以及对插值数据的偏移。质心和转动惯量查表数据存储在单独的文件中，并独立插值。用户有责任为给定航天器准备一套一致的数据；`Lookup` 模型更常用于特性已充分了解的航天器的任务运行中。两个文件应存放在同一文件夹中；参数 `MassPropertiesTableFilePath` 用于设置该文件夹的路径，文件名由参数 `CenterOfMassTableFileName` 和 `MomentOfInertiaTableFileName` 提供。

两个文件都是文本文件，每行第一个参数为航天器质量，随后是对应的质心或转动惯量值。

质心数据在以总质量为索引的文本文件中列表给出。示例文件如下。在当前实现中，该文件的头部数据仅供参考：其中显示的数据当前 GMAT 代码并不使用，但可能在以后的实现中使用。

```
% Center of Mass Datafile

Spacecraft:  SampleSat
Index:  TotalMass
CoordinateSystem:  BCS
Units:   Meters

% Data order:
% RefMass, COMx COMy COMz

BeginData
2200    0.0220    0.0500    0.3000
2100    0.0215    0.0366    0.2888
2000    0.0211    0.0233    0.2777
1900    0.0206    0.0100    0.2666
1800    0.0202   -0.0033    0.2555
1700    0.0197   -0.0166    0.2444
1600    0.0193   -0.0300    0.2333
1500    0.0188   -0.0433    0.2222
1400    0.0184   -0.0566    0.2111
1300    0.0180   -0.0700    0.2000
EndData
```

**中文说明**：质心查表文件以总质量（TotalMass）为索引列，每行给出该总质量对应的质心坐标（COMx COMy COMz，单位米，BCS 本体坐标系）。

BeginData 和 EndData 行之间列表的数据在 GMAT 中用于插值质心位置，使用 GMAT 的拉格朗日（Lagrange）插值器。数据的第一列是航天器总质量，作为查表索引。该索引列必须单调，但可以递增，也可以如本例所示递减。质心位置以笛卡尔本体固连坐标列表给出，每行指定与第一列总质量值对应的质心位置，数据按 X-Y-Z 顺序，单位为米。如果用于插值的 `TotalMass` 超出第一列列表质量上下界给出的范围，GMAT 将抛出异常，表明无法插值航天器质心。

转动惯量张量以类似方式列表。示例文件如下。与质心情况一样，转动惯量表文件中的头部信息目前不使用，但可能在以后的实现中使用。

```
% Moment of Inertia Datafile

Spacecraft:  SampleSat
Index:  TotalMass
Origin:  Spacecraft Center of Mass
Units:   kg-m^2

% Data order:
% RefMass, MOIxx MOIyy MOIzz MOIxy MOIxz MOIyz

BeginData
1300    12.755    17.423   14.111     0.187   -0.622    0.455
1400    12.655    17.001   14.116     0.186   -0.622    0.445
1500    12.455    16.722   14.120     0.185   -0.622    0.435
1600    12.155    16.432   14.123     0.184   -0.622    0.425
1700    12.055    16.395   14.124     0.183   -0.622    0.415
1800    12.155    16.388   14.124     0.182   -0.622    0.405
1900    12.455    16.376   14.124     0.181   -0.622    0.395
2000    12.555    16.368   14.123     0.180   -0.622    0.385
2100    12.755    16.365   14.119     0.179   -0.622    0.375
2200    12.955    16.365   14.107     0.178   -0.622    0.365
EndData
```

**中文说明**：转动惯量查表文件同样以总质量为索引，每行给出相对于航天器质心的惯量张量分量，顺序为 MOIxx MOIyy MOIzz MOIxy MOIxz MOIyz，单位 kg-m^2。

BeginData 和 EndData 行之间列表的数据在 GMAT 中用于插值相对于航天器质心的惯性矩和惯性积，使用 GMAT 的拉格朗日插值器。数据的第一列是航天器总质量，作为查表索引。该索引列必须单调，但可以如本例所示递增，也可以递减。每个张量元素在笛卡尔坐标系中列表给出。每行指定与第一列总质量值对应的、相对于航天器质心的惯量张量分量。数据按 XX-YY-ZZ-XY-XZ-YZ 顺序。惯性矩和惯性积的单位为千克-平方米。如果用于插值的 `TotalMass` 超出第一列列表质量上下界给出的范围，GMAT 将抛出异常，表明无法插值航天器质心。

上面列表给出的航天器质心是质心的标称位置。由于项目开始时列表数据未考虑的航天器构型因素，该位置可能会发生偏移。GMAT 脚本通过航天器上的一组偏移值来计入这些因素。质心有 3 个偏移参数，分别表示 X、Y 和 Z 方向的偏移；转动惯量有 6 个偏移，分别表示 XX、YY、ZZ、XY、XZ 和 YZ。两种情况下偏移都默认为零。两者之中，质心偏移在实践中更可能用到；转动惯量偏移则是为完整性和未预见情况而设的。

### 扩展质量特性：Analytic 模型

由于该模型尚未完成，本节将概述其计算过程，而不强调各用户选项（这些选项将在完整实现后记录于此）。我们假设已同时选择质心和转动惯量。

解析模型在 `Spacecraft` 和 `FuelTank` 类之间分配扩展质量特性的计算职责。`FuelTank` 将能够计算其自身在 BCS 中的质心以及绕系统质心的转动惯量；`Spacecraft` 负责把所有燃料质量特性与干态航天器质量特性相加，得到系统质量特性。对于转动惯量，由于所有部件都绕系统质心计算其转动惯量，系统转动惯量就是所有部件转动惯量之和。计算步骤为：

- 对每个 `FuelTank`，计算其内容物的质心和转动惯量——这是模型中尚未完成的部分。
- 对每个 `FuelTank`，计算其在 BCS 中的质心。它是燃料箱在箱坐标系中的质心、箱坐标系原点在 BCS 中的位置以及箱坐标系相对于 BCS 的朝向的函数。
- 在 `Spacecraft` 对象中计算系统质心。这是燃料和干态航天器各质心的加权平均，按各自质量加权。
- 对每个 `FuelTank`，使用平行轴定理（Parallel Axis Theorem）计算其绕系统质心的转动惯量。注意，此计算使用上一步算得的系统质心。
- 在 `Spacecraft` 对象中计算系统转动惯量。这就是各部件转动惯量的简单求和，因为它们都是绕系统质心计算的。

后 4 步的代码已实现并集成到两个类中。当最后一部分实现后，选择扩展质量特性解析建模时抛出异常的代码将被移除。
## 示例

为球形 SRP 模型配置物理特性。

```
Create Spacecraft aSpacecraft
aSpacecraft.Cd       = 2.2
aSpacecraft.Cr       = 1.8
aSpacecraft.DragArea = 40
aSpacecraft.SRPArea  = 35
aSpacecraft.DryMass  = 2000
Create Propagator aPropagator

BeginMissionSequence

Propagate aPropagator(aSpacecraft, {aSpacecraft.ElapsedSecs = 600})
```

**中文说明**：创建航天器并设置 Cd=2.2、Cr=1.8、阻力面积 40 m^2、SRP 面积 35 m^2、干重 2000 kg，然后传播 600 秒。

配置 SPAD SRP 模型。

```
Create Spacecraft aSpacecraft;
aSpacecraft.DryMass = 2000
aSpacecraft.SPADSRPFile = '../data/vehicle/spad/SphericalModel.spo'
aSpacecraft.SPADSRPScaleFactor = 1
aSpacecraft.SPADDragInterpolationMethod = Bicubic

Create ForceModel aFM;
aFM.SRP          = On;
aFM.SRP.SRPModel = SPADFile

Create Propagator aProp;
aProp.FM = aFM;

BeginMissionSequence

Propagate aProp(aSpacecraft) {aSpacecraft.ElapsedDays = 0.2}
```

**中文说明**：为航天器指定 SPAD SRP 文件与比例因子，在力模型 `aFM` 中打开 SRP 并将 `SRPModel` 设为 `SPADFile`，再用该力模型传播 0.2 天。

计算质心和转动惯量的变化。

```
         %---------- Spacecraft ----------------
         Create Spacecraft JSL;
         JSL.Tanks = {TankA}
         JSL.Thrusters = {ThrusterA}

         %% Added Mass Properties' lookup table files
         JSL.DryMass = 2440;
         JSL.MassPropertiesTableFilePath = '../include'
         JSL.ExtendedMassPropertiesModelType = 'Lookup'
         JSL.ExtendedMassPropertiesModel     = 'CenterOfMassAndMomentOfInertia'
         JSL.CenterOfMassTableFileName       = 'FakeLinearCM.table'
         JSL.MomentOfInertiaTableFileName    = 'FakeLinearMOI.table'

         Create ChemicalTank TankA
         TankA.Volume = 2.0
         TankA.FuelMass = 1500
         Create Thruster ThrusterA
         ThrusterA.Tank = {TankA}
         Create FiniteBurn fb1;
         fb1.Thrusters = {ThrusterA};
         ThrusterA.DecrementMass = true;

         %---------- Propagator ----------------
         Create Propagator EarthProp;
         Create ForceModel TorqueForces;
         EarthProp.FM = TorqueForces

         %---------- Reports -------------------
         Create ReportFile CM;
         CM.Filename = 'CM.report'
         Create ReportFile MOI;
         MOI = 'MOI.report'

         %---------- Mission Sequence ----------
         BeginMissionSequence;

         BeginFiniteBurn fb1(JSL);
            For loop = 1:14
               Report  CM JSL.TotalMass JSL.SystemCenterOfMassX JSL.SystemCenterOfMassY JSL.SystemCenterOfMassZ
               Report MOI JSL.SystemMomentOfInertiaXX JSL.SystemMomentOfInertiaXY JSL.SystemMomentOfInertiaXZ  ...
                          JSL.SystemMomentOfInertiaYY JSL.SystemMomentOfInertiaYZ JSL.SystemMomentOfInertiaZZ
               nextFuelMass = JSL.TankA.FuelMass - 100
               Propagate EarthProp(JSL) {JSL.TankA.FuelMass = nextFuelMass}
            EndFor
            Report  CM JSL.TotalMass JSL.SystemCenterOfMassX JSL.SystemCenterOfMassY JSL.SystemCenterOfMassZ
            Report MOI JSL.SystemMomentOfInertiaXX JSL.SystemMomentOfInertiaXY JSL.SystemMomentOfInertiaXZ  ...
                       JSL.SystemMomentOfInertiaYY JSL.SystemMomentOfInertiaYZ JSL.SystemMomentOfInertiaZZ

         EndFiniteBurn fb1(JSL);
```

**中文说明**：该示例使用 Lookup 扩展质量特性模型：为航天器 JSL 指定质心和转动惯量查表文件，并挂载燃料箱 TankA 与推力器 ThrusterA；在有限推力弧段（FiniteBurn）内循环 14 次，每次把燃料质量减少 100 kg 并传播，同时用报告文件输出 `TotalMass`、系统质心三分量和系统转动惯量六个分量，从而观察质心和转动惯量随燃料消耗的变化。（注：示例中 `MOI = 'MOI.report'` 为原文写法，疑为 `MOI.Filename` 之笔误。）