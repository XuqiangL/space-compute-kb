# 航天器姿态（Spacecraft Attitude）
> 译自 GMAT R2026a 帮助文档 SpacecraftAttitude.html

**Spacecraft Attitude —— 航天器姿态模型**

## 描述

GMAT 使用多种不同的数学模型来建模航天器的指向（orientation）和转动角速度。目前 GMAT 假定航天器（Spacecraft）为刚体。当前支持的姿态模型有 `Spinner`（自旋）、`PrecessingSpinner`（进动自旋）、`CoordinateSystemFixed`（坐标系固定）、`NadirPointing`（对地/天底指向）、`CommandableNadirPointing`（可指令对地指向）、`ThreeAxisKinematic`（三轴运动学）、`CCSDS-AEM` 和 `SpiceAttitude`。`Spinner` 模型是简单的惯性空间固定自旋轴模型；`PrecessingSpinner` 模型在此基础上增加了自旋轴的进动（precession）和章动（nutation）建模；`CoordinateSystemFixed` 模型允许你使用 GMAT 支持的任意 `CoordinateSystem`（坐标系）作为航天器的姿态；`NadirPointing` 模型基于航天器位置和速度矢量构造坐标系；`CommandableNadirPointing` 姿态模型与 Nadir Pointing 模型完全相同，但增加了在任务序列（Mission Sequence）中用四元数设置姿态的能力；`SpiceAttitude` 模型允许你基于 SPICE 姿态核（kernel）定义航天器姿态；`ThreeAxisKinematic` 模型由角速度输入传播姿态四元数，它最初为一个动画应用而设计，该应用每 25 毫秒传播一次姿态。

**另请参阅**：`Spacecraft`

## 字段

### AngularVelocityX

航天器本体角速度在惯性系中表达的 x 分量。`AngularVelocityX` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：0
- 单位：deg/sec
- 接口：GUI、脚本

### AngularVelocityY

航天器本体角速度在惯性系中表达的 y 分量。`AngularVelocityY` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：0
- 单位：deg/sec
- 接口：GUI、脚本

### AngularVelocityZ

航天器本体角速度在惯性系中表达的 z 分量。`AngularVelocityZ` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：0
- 单位：deg/sec
- 接口：GUI、脚本

### Attitude

航天器的姿态模式。

- 数据类型：字符串（String）
- 允许值：`CoordinateSystemFixed`、`Spinner`、`SpiceAttitude`、`NadirPointing`、`CommandableNadirPointing`、`CCSDS-AEM`、`PrecessingSpinner`、`ThreeAxisKinematic`
- 访问权限：仅可设置（set）
- 默认值：`CoordinateSystemFixed`
- 单位：N/A
- 接口：GUI、脚本

### AttitudeConstraintType

用于消除姿态模糊性的约束（constraint）类型。姿态的计算使 `BodyConstraintVector` 与由 `AttitudeConstraintType` 定义的约束之间的夹角最小。`Velocity` 约束使用相对于 `AttitudeReferenceBody` 表达的惯性速度矢量；`OrbitNormal` 约束使用相对于 `AttitudeReferenceBody` 表达的轨道法线矢量。`AttitudeConstraintType` 用于以下姿态模型：`NadirPointing`、`CommandableNadirPointing`。

- 数据类型：枚举（Enumeration）
- 允许值：`Velocity`、`OrbitNormal`
- 访问权限：仅可设置（set）
- 默认值：OrbitNormal
- 单位：N/A
- 接口：GUI、脚本

### AttitudeCoordinateSystem

姿态计算中使用的 `CoordinateSystem`（坐标系）。`AttitudeCoordinateSystem` 字段仅用于以下姿态模型：`CoordinateSystemFixed`。

- 数据类型：字符串（String）
- 允许值：`CoordinateSystem` 资源
- 访问权限：仅可设置（set）
- 默认值：`EarthMJ2000Eq`
- 单位：N/A
- 接口：GUI、脚本

### AttitudeFileName

CCSDS 姿态星历报文（AEM）文件的路径（可选）和文件名。如果未提供路径，且 GMAT 在当前目录中找不到该文件，则会出错并停止执行。

- 数据类型：字符串（String）
- 允许值：AEM 文件
- 访问权限：仅可设置（set）
- 默认值：N/A
- 单位：N/A
- 接口：GUI、脚本

### AttitudeRateDisplayStateType

在 GUI 和脚本文件中显示的姿态角速度表示法。`AttitudeRateDisplayType` 用于以下姿态模型：`Spinner`。

- 数据类型：字符串（String）
- 允许值：`AngularVelocity`、`EulerAngleRates`
- 访问权限：仅可设置（set）
- 默认值：`AngularVelocity`
- 单位：N/A
- 接口：GUI、脚本

### AttitudeReferenceBody

用于定义天底（nadir）方向的天体。`AttitudeReferenceBody` 用于以下姿态模型：`NadirPointing`、`CommandableNadirPointing`。

- 数据类型：资源（Resource）
- 允许值：天体（Celestial Body）
- 访问权限：仅可设置（set）
- 默认值：Earth
- 单位：N/A
- 接口：GUI、脚本

### AttitudeSpiceKernelName

用于航天器姿态的 SPK 核文件。SPK 姿态核的扩展名为 ".BC"。此字段不能在任务序列（Mission Sequence）中设置。空列表会卸载该航天器上此类型的所有核文件。

- 数据类型：字符串数组（String array）
- 允许值：姿态核文件组成的数组
- 访问权限：仅可设置（set）
- 默认值：空数组
- 单位：N/A
- 接口：GUI、脚本
### BodyAlignmentVectorX

`BodyAlignmentVectorX` 是对准矢量（alignment vector）在本体系中的 x 分量。`BodyAlignmentVectorX` 用于以下姿态模型：`NadirPointing`、`CommandableNadirPointing`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：1
- 单位：N/A
- 接口：GUI、脚本

### BodyAlignmentVectorY

`BodyAlignmentVectorY` 是对准矢量在本体系中的 y 分量。`BodyAlignmentVectorY` 用于以下姿态模型：`NadirPointing`、`CommandableNadirPointing`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：N/A
- 接口：GUI、脚本

### BodyAlignmentVectorZ

`BodyAlignmentVectorZ` 是对准矢量在本体系中的 z 分量。`BodyAlignmentVectorZ` 用于以下姿态模型：`NadirPointing`、`CommandableNadirPointing`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：N/A
- 接口：GUI、脚本

### BodyConstraintVectorX

`BodyConstraintVectorX` 是约束矢量在本体系中的 x 分量。`BodyConstraintVectorX` 用于以下姿态模型：`NadirPointing`、`CommandableNadirPointing`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：N/A
- 接口：GUI、脚本

### BodyConstraintVectorY

`BodyConstraintVectorY` 是约束矢量在本体系中的 y 分量。`BodyConstraintVectorY` 用于以下姿态模型：`NadirPointing`、`CommandableNadirPointing`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：N/A
- 接口：GUI、脚本

### BodyConstraintVectorZ

`BodyConstraintVectorZ` 是约束矢量在本体系中的 z 分量。`BodyConstraintVectorZ` 用于以下姿态模型：`NadirPointing`、`CommandableNadirPointing`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：1
- 单位：N/A
- 接口：GUI、脚本

### BodySpinAxisX

`BodySpinAxisX` 是自旋轴在本体系中的 x 分量。`BodySpinAxisX` 用于以下姿态模型：`PrecessingSpinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：N/A
- 接口：GUI、脚本

### BodySpinAxisY

`BodySpinAxisY` 是自旋轴在本体系中的 y 分量。`BodySpinAxisY` 用于以下姿态模型：`PrecessingSpinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：N/A
- 接口：GUI、脚本

### BodySpinAxisZ

`BodySpinAxisZ` 是自旋轴在本体系中的 z 分量。`BodySpinAxisZ` 用于以下姿态模型：`PrecessingSpinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：1
- 单位：N/A
- 接口：GUI、脚本
### DCM11

方向余弦矩阵（DCM）的元素 11。`DCM11` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-1 <= Real <= 1
- 访问权限：set、get
- 默认值：1
- 单位：N/A
- 接口：GUI、脚本

### DCM12

方向余弦矩阵的元素 12。`DCM12` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-1 <= Real <= 1
- 访问权限：set、get
- 默认值：0
- 单位：N/A
- 接口：GUI、脚本

### DCM13

方向余弦矩阵的元素 13。`DCM13` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-1 <= Real <= 1
- 访问权限：set、get
- 默认值：0
- 单位：N/A
- 接口：GUI、脚本

### DCM21

方向余弦矩阵的元素 21。`DCM21` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-1 <= Real <= 1
- 访问权限：set、get
- 默认值：0
- 单位：N/A
- 接口：GUI、脚本

### DCM22

方向余弦矩阵的元素 22。`DCM22` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-1 <= Real <= 1
- 访问权限：set、get
- 默认值：1
- 单位：N/A
- 接口：GUI、脚本

### DCM23

方向余弦矩阵的元素 23。`DCM23` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-1 <= Real <= 1
- 访问权限：set、get
- 默认值：0
- 单位：N/A
- 接口：GUI、脚本

### DCM31

方向余弦矩阵的元素 31。`DCM31` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-1 <= Real <= 1
- 访问权限：set、get
- 默认值：0
- 单位：N/A
- 接口：GUI、脚本

### DCM32

方向余弦矩阵的元素 32。`DCM32` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-1 <= Real <= 1
- 访问权限：set、get
- 默认值：0
- 单位：N/A
- 接口：GUI、脚本

### DCM33

方向余弦矩阵的元素 33。`DCM33` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-1 <= Real <= 1
- 访问权限：set、get
- 默认值：1
- 单位：N/A
- 接口：GUI、脚本
### EulerAngle1

欧拉角 1（Euler Angle 1）。`EulerAngle1` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：0
- 单位：deg.
- 接口：GUI、脚本

### EulerAngle2

欧拉角 2（Euler Angle 2）。`EulerAngle2` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：0
- 单位：deg.
- 接口：GUI、脚本

### EulerAngle3

欧拉角 3（Euler Angle 3）。`EulerAngle3` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：0
- 单位：deg.
- 接口：GUI、脚本

### EulerAngleRate1

欧拉角角速度 1（Euler Angle Rate 1）。`EulerAngleRate1` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：0
- 单位：deg./sec.
- 接口：GUI、脚本

### EulerAngleRate2

欧拉角角速度 2（Euler Angle Rate 2）。`EulerAngleRate2` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：1
- 单位：deg./sec.
- 接口：GUI、脚本

### EulerAngleRate3

欧拉角角速度 3（Euler Angle Rate 3）。`EulerAngleRate3` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：1
- 单位：deg./sec.
- 接口：GUI、脚本

### EulerAngleSequence

用于描述姿态的欧拉角转动序列。`EulerAngleSequence` 用于以下姿态模型：`Spinner`。

- 数据类型：字符串（String）
- 允许值：121、123、131、132、212、213、231、232、312、313、321、323
- 访问权限：仅可设置（set）
- 默认值：321
- 单位：N/A
- 接口：GUI、脚本

### FrameSpiceKernelName

用于航天器姿态的帧核（frame kernel）文件。SPK 帧核的扩展名为 ".tf"。此字段不能在任务序列中设置。空列表会卸载该航天器上此类型的所有核文件。

- 数据类型：字符串数组（String array）
- 允许值：帧核文件组成的数组
- 访问权限：仅可设置（set）
- 默认值：空数组
- 单位：N/A
- 接口：GUI、脚本

### InitialPrecessionAngle

初始进动角（Initial Precession Angle）。`InitialPrecessionAngle` 用于以下姿态模型：`PrecessingSpinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：deg.
- 接口：GUI、脚本

### InitialSpinAngle

初始自旋角（Initial Spin Angle）。`InitialSpinAngle` 用于以下姿态模型：`PrecessingSpinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：deg.
- 接口：GUI、脚本

### NAIFIdReferenceFrame

用于姿态核的参考系 NAIF Id。此字段不能在任务序列中设置。

- 数据类型：整数（Integer）
- 允许值：-∞ < Integer < ∞
- 访问权限：仅可设置（set）
- 默认值：-9000001
- 单位：N/A
- 接口：GUI、脚本

### NutationAngle

章动角（Nutation Angle）。`NutationAngle` 用于以下姿态模型：`PrecessingSpinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：15
- 单位：deg.
- 接口：GUI、脚本

### NutationReferenceVectorX

章动参考矢量（Nutation Reference Vector）在惯性系中表达的 x 分量。`NutationReferenceVectorX` 用于以下姿态模型：`PrecessingSpinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：N/A
- 接口：GUI、脚本

### NutationReferenceVectorY

章动参考矢量在惯性系中表达的 y 分量。`NutationReferenceVectorY` 用于以下姿态模型：`PrecessingSpinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：N/A
- 接口：GUI、脚本

### NutationReferenceVectorZ

章动参考矢量在惯性系中表达的 z 分量。`NutationReferenceVectorZ` 用于以下姿态模型：`PrecessingSpinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：1
- 单位：N/A
- 接口：GUI、脚本
### MRP1

修正罗德里格斯参数（Modified Rodrigues Parameter）1。`MRP1` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：0
- 单位：无量纲
- 接口：GUI、脚本

### MRP2

修正罗德里格斯参数 2。`MRP2` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：0
- 单位：无量纲
- 接口：GUI、脚本

### MRP3

修正罗德里格斯参数 3。`MRP3` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：0
- 单位：无量纲
- 接口：GUI、脚本

### PrecessionRate

进动角速度（Precession Rate）。`PrecessionRate` 用于以下姿态模型：`PrecessingSpinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：0
- 单位：deg./s
- 接口：GUI、脚本

### Q1

四元数分量 1（Quaternion component 1）。`Q1` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：0
- 单位：无量纲
- 接口：GUI、脚本

### Q2

四元数分量 2。`Q2` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：0
- 单位：无量纲
- 接口：GUI、脚本

### Q3

四元数分量 3。`Q3` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：0
- 单位：无量纲
- 接口：GUI、脚本

### Q4

四元数分量 4。`Q4` 用于以下姿态模型：`Spinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：set、get
- 默认值：1
- 单位：无量纲
- 接口：GUI、脚本

### Quaternion

四元数（Quaternion）。

- 数据类型：实数数组（Real array）
- 允许值：长度为 4 的实数数组
- 访问权限：set、get
- 默认值：[ 0 0 0 1 ]
- 单位：N/A
- 接口：GUI、脚本

### SCClockSpiceKernelName

用于航天器姿态的航天器时钟核（spacecraft clock kernel）文件。SPK 航天器时钟核的扩展名为 ".tsc"。此字段不能在任务序列中设置。空列表会卸载该航天器上此类型的所有核文件。

- 数据类型：字符串数组（String array）
- 允许值：航天器时钟核文件组成的数组
- 访问权限：set、get
- 默认值：空数组
- 单位：N/A
- 接口：GUI、脚本

### SpinRate

自旋角速度（Spin Rate）。`SpinRate` 用于以下姿态模型：`PrecessingSpinner`。

- 数据类型：实数（Real）
- 允许值：-∞ < Real < ∞
- 访问权限：仅可设置（set）
- 默认值：10
- 单位：deg./s
- 接口：GUI、脚本
## 备注

### 可用姿态模型概述

GMAT 支持多种姿态模型，它们使用不同的状态表示法，并具有不同的传播特性。GMAT 目前支持以下姿态模型：

- `Spinner`（自旋）
- `PrecessingSpinner`（进动自旋）
- `CoordinateSystemFixed`（坐标系固定）
- `NadirPointing`（对地/天底指向）
- `CommandableNadirPointing`（可指令对地指向）
- `CCSDS-AEM`
- `PrecessingSpinner`（进动自旋）
- `ThreeAxisKinematic`（三轴运动学）

我们建议使用 `PrecessingSpinner` 模型而不是 `Spinner` 模型。保留 `Spinner` 模型是为了向后兼容。不同的模型需要不同的信息来完全定义模型。例如，当使用 `Spinner` 模型时，你必须在设置姿态之前指定 `EulerAngleSequence`（欧拉角序列）；当使用 `CoordinateSystemFixed` 模型时，你必须提供 `AttitudeCoordinateSystem`（姿态坐标系）。详见下文对各模型的详细说明。

> **注意**：GMAT 的姿态参数化（例如方向余弦矩阵 DCM）是从惯性系旋转到本体系的。

### 姿态状态表示法概述

#### 四元数（Quaternion）

四元数是一种四元素、非奇异的姿态表示法，常用于需要传播航天器姿态的应用中。GMAT 可以使用四元数定义航天器的初始姿态，但四元数通常用于在传播过程中查询姿态。四元数定义为：前三个分量代表转动的矢量分量，最后一个分量代表转动角本身。四元数赋值有两种模式。你可以逐个元素地设置四元数，也可以整体设置四元数矢量，如下例所示：

```
Create Spacecraft aSat;
aSat.Q1 = 0;
aSat.Q2 = 0;
aSat.Q3 = 0;
aSat.Q4 = 1;

BeginMissionSequence;
```

```
Create Spacecraft aSat;
aSat.Quaternion = [0 0 0 1];

BeginMissionSequence;
```

上述示例中，四元数的各分量 `Q1`、`Q2`、`Q3`、`Q4` 分别单独赋值，或作为整体矢量 `Quaternion` 赋值。

在 GMAT 内部，四元数总是被归一化。因此，如果提供的四元数模不为 1，GMAT 会在内部将其缩放为单位四元数。在命令模式（command mode）下工作时，必须将完整的四元数作为单个矢量输入，例如：

```
aSat.Quaternion = [0 0 0 1];
```

#### 方向余弦矩阵（Direction Cosine Matrix，DCM）

方向余弦矩阵（DCM）是一个 3x3 的方向余弦数组，用于描述从惯性 x、y、z 轴到本体 x、y、z 轴的转动。DCM 必须是正交归一（ortho-normal）矩阵。在 GMAT 中，必须逐元素定义 DCM，如下例所示：

```
Create Spacecraft aSat;
aSat.DCM11 = 1;
aSat.DCM12 = 0;
aSat.DCM13 = 0;
aSat.DCM21 = 0;
aSat.DCM22 = 1;
aSat.DCM23 = 0;
aSat.DCM31 = 0;
aSat.DCM32 = 0;
aSat.DCM33 = 1;

BeginMissionSequence;
```

此示例将 DCM 设置为单位矩阵，即本体轴与惯性轴对齐。

#### 欧拉角（Euler Angles）

欧拉角是一组三个转动角，通过按指定顺序执行三次转动来描述姿态。GMAT 支持全部 12 种欧拉角序列。欧拉角序列通过 `EulerAngleSequence` 字段设置。下例展示如何使用 321 序列设置欧拉角：

```
Create Spacecraft aSat;
aSat.EulerAngleSequence = 321;
aSat.EulerAngle1 = 15;
aSat.EulerAngle2 = 35;
aSat.EulerAngle3 = 45;

BeginMissionSequence;
```

> **警告**：欧拉角存在奇异点。当第二个欧拉角接近奇异值时，GMAT 会抛出错误消息并停止执行。

#### 修正罗德里格斯参数（Modified Rodrigues Parameters，MRP）

修正罗德里格斯参数是一种三元素姿态表示法，由欧拉轴单位矢量（n̂）乘以 tan(欧拉角/4) 得到。下例展示如何设置 MRP：

```
Create Spacecraft aSat;
aSat.MRP1 = 0;
aSat.MRP2 = 0;
aSat.MRP3 = 0;

BeginMissionSequence;
```

#### 欧拉角角速度（Euler Angle Rates）

欧拉角角速度是欧拉角的一阶时间导数。欧拉角角速度使用与欧拉角相同的转动序列，由 `EulerAngleSequence` 字段定义。下例展示如何使用 321 序列设置欧拉角角速度：

```
Create Spacecraft aSat;
aSat.EulerAngleSequence = 321;
aSat.EulerAngleRate1 = -5;
aSat.EulerAngleRate2 = 20;
aSat.EulerAngleRate3 = 30;

BeginMissionSequence;
```

#### 角速度（Angular Velocity）

角速度是本体相对于惯性系的角速度，表达在惯性系中。下例展示如何设置角速度分量：

```
Create Spacecraft aSat;
aSat.AngularVelocityX = 5;
aSat.AngularVelocityY = 10;
aSat.AngularVelocityZ = 5;

BeginMissionSequence;
```
### 坐标系固定姿态模型（Coordinate System Fixed Attitude Model）

`CoordinateSystemFixed` 姿态模型允许你将任意现有的 `CoordinateSystem`（坐标系）用作航天器的姿态。航天器的姿态和本体角速度由所选坐标系完全确定。注意：使用 `CoordinateSystemFixed` 姿态模型时，欧拉角和角速度字段不是必需的，设置它们不会产生任何效果。但是，你可以定义 `EulerAngleSequence`，GMAT 在输出欧拉角和欧拉角角速度时会使用该序列。

> **警告**：当使用 `CoordinateSystemFixed` 姿态模型时，姿态完全由所选坐标系描述。设置姿态或姿态角速度参数不会产生任何效果。

> [图：CoordinateSystemFixed 姿态模型的 GUI 配置界面]

下面的脚本示例展示如何配置航天器使用 VNB（Velocity-Normal-Binormal，速度-法线-副法线）姿态坐标系：

```
Create Spacecraft aSat;
aSat.Attitude = CoordinateSystemFixed;

Create CoordinateSystem VNB;
VNB.Origin = aSat;
VNB.Axes = VNB;

aSat.AttitudeCoordinateSystem = VNB;

Create ForceModel Propagator1_ForceModel;
Create Propagator Propagator1;
Propagator1.FM = Propagator1_ForceModel;
Propagator1.MaxStep = 10;

Create OrbitView OrbitView1;
OrbitView1.Add = {aSat, Earth}
OrbitView1.ViewPointReference = Earth
OrbitView1.ViewPointVector = [ 30000 0 0 ]

BeginMissionSequence;

Propagate Propagator1(aSat) {aSat.ElapsedSecs = 12000.0}
```

此示例创建名为 `VNB` 的坐标系（原点为 `aSat`，坐标轴为 VNB），将航天器姿态设为 `CoordinateSystemFixed` 并指定 `AttitudeCoordinateSystem = VNB`，然后传播 12000 秒。

### 自旋姿态模型（Spinner Attitude Model）

`Spinner` 姿态模型在假定自旋轴方向在惯性空间中固定的前提下传播航天器姿态。所提供的初始条件以 `Spacecraft` 上设置的初始历元为参考。我们建议使用 `PrecessingSpinner` 模型而不是 `Spinner` 模型；保留 `Spinner` 模型是为了向后兼容。

你可以通过指定本体的初始指向和初始角速度来定义姿态。GMAT 通过以下方式传播姿态：先计算角速度矢量，然后绕该矢量以恒定速率（等于角速度矢量的模）旋转。初始姿态可以用四元数、欧拉角、方向余弦矩阵（DCM）或修正罗德里格斯参数（MRP）指定；初始角速度可以用欧拉角角速度或角速度指定。当使用欧拉角或欧拉角角速度时，转动序列由 `EulerAngleSequence` 字段决定。

> **警告**：注意：如果在脚本中工作，为 `Spinner` 姿态模型设置 `CoordinateSystem` 不会产生任何效果。

> [图：Spinner 姿态模型的 GUI 配置界面]

下面的脚本示例展示如何配置航天器绕惯性 z 轴自旋：

```
Create Spacecraft aSat;
aSat.Attitude = Spinner;

aSat.AngularVelocityX = 0;
aSat.AngularVelocityY = 0;
aSat.AngularVelocityZ = 5;

Create ForceModel Propagator1_ForceModel;
Create Propagator Propagator1;
Propagator1.FM = Propagator1_ForceModel;
Propagator1.MaxStep = 10;

Create OrbitView OrbitView1;
OrbitView1.Add = {aSat, Earth}
OrbitView1.ViewPointReference = Earth
OrbitView1.ViewPointVector = [ 30000 0 0 ]

BeginMissionSequence;

Propagate Propagator1(aSat) {aSat.ElapsedSecs = 12000.0}
```

此示例将航天器姿态设为 `Spinner`，并设置角速度 z 分量为 5 deg/sec（绕惯性 z 轴自旋），然后传播 12000 秒。
### SPK 姿态模型（SPK Attitude Model）

`SpiceAttitude` 姿态模型使用 SPICE 核（kernel）传播航天器姿态。

> **警告**：当使用 `SpiceAttitude` 姿态模型时，姿态完全由 SPICE 核描述。设置 `CoordinateSystem`、姿态或姿态角速度参数不会产生任何效果。

> [图：SpiceAttitude 姿态模型的 GUI 配置界面]

SPICE 姿态模型需要三类 SPICE 核文件：姿态核（attitude kernel，扩展名 ".bc"）、帧核（frame kernel，扩展名 ".tf"）和航天器时钟核（spacecraft clock kernel，扩展名 ".tsc"）。这些核文件在 `Spacecraft` 资源的 SPICE 选项卡上定义。你还必须提供航天器的 `NAIFId` 和 `NAIFIdReferenceFrame`（用于姿态核的参考系 NAIF Id）。

> [图：MarsExpress 航天器使用 SPICE 姿态核的 GUI 配置界面]

下面的脚本示例展示如何配置 MarsExpress 航天器使用 SPK 姿态：

```
Create Spacecraft MarsExpress;
MarsExpress.DateFormat = UTCGregorian;
MarsExpress.Epoch = '01 Jun 2010 16:59:09.815';
MarsExpress.CoordinateSystem = MarsMJ2000Eq;
MarsExpress.DisplayStateType = Cartesian;
MarsExpress.X = -6042.5;
MarsExpress.Y = -3414.0;
MarsExpress.Z = -1591.5;
MarsExpress.VX = 1.8832;
MarsExpress.VY = -2.7184;
MarsExpress.VZ = -1.0734;

MarsExpress.Attitude = SpiceAttitude;
MarsExpress.NAIFId = -41;
MarsExpress.NAIFIdReferenceFrame = -41001;
MarsExpress.AttitudeSpiceKernelName = {'../data/vehicle/ephem/spice/MarsExpress/ORMM_T19_031222000906_00052.BC'};
MarsExpress.FrameSpiceKernelName = {'../data/vehicle/ephem/spice/MarsExpress/MEX_V12.TF'};
MarsExpress.SCClockSpiceKernelName = {'../data/vehicle/ephem/spice/MarsExpress/MEX_100331_STEP.TSC'};

Create Propagator spkProp
spkProp.Type = SPK
spkProp.StepSize = 60
spkProp.CentralBody = Mars
spkProp.EpochFormat = 'UTCGregorian'
spkProp.StartEpoch = '01 Jun 2010 16:59:09.815'

Create CoordinateSystem MarsMJ2000Eq
MarsMJ2000Eq.Origin = Mars
MarsMJ2000Eq.Axes = MJ2000Eq

Create OrbitView Enhanced3DView1
Enhanced3DView1.Add = {MarsExpress, Mars}
Enhanced3DView1.CoordinateSystem = MarsMJ2000Eq
Enhanced3DView1.ViewPointReference = Mars
Enhanced3DView1.ViewPointVector = [ 10000 10000 10000 ]
Enhanced3DView1.ViewDirection = Mars

BeginMissionSequence

Propagate spkProp(MarsExpress) {MarsExpress.ElapsedDays = 0.2}
```

此示例创建 MarsExpress 航天器，设置其姿态为 `SpiceAttitude`，指定 NAIF Id（-41）、姿态参考系 NAIF Id（-41001）以及三个 SPICE 核文件（姿态核 .BC、帧核 .TF、时钟核 .TSC），使用 SPK 传播器沿火星轨道传播 0.2 天。
### 对地（天底）指向模型（Nadir Pointing Model）

`NadirPointing` 姿态模式将航天器姿态配置为：使本体系中指定的矢量指向天底（nadir）方向。绕天底矢量的角度模糊性通过使两个约束矢量之间的夹角最小来消除。注意：天底指向模式将姿态指向负径向方向（而不是行星测地法线的反方向）。

要配置哪个轴指向天底，将 `AttitudeReferenceBody` 字段设置为所需的天体，并使用 `BodyAlignmentVector` 字段定义对准矢量（alignment vector）的本体分量。要配置约束（constraint），将 `AttitudeConstraintType` 字段设置为所需的约束类型，并使用 `BodyConstraintVector` 字段定义约束的本体分量。GMAT 支持两种约束类型：`OrbitNormal`（轨道法线）和 `Velocity`（速度），在这两种情况下，矢量都是使用航天器相对于 `AttitudeReferenceBody` 的惯性状态构造的。

> **警告**：`NadirPointing` 模型不计算姿态角速度。如果在使用 `NadirPointing` 模式时执行需要姿态角速度信息的计算，GMAT 会抛出错误消息并停止执行。同样，如果 `BodyAlignmentVector` 和 `BodyConstraintVector` 字段的定义导致姿态未定义，也会抛出错误消息并停止执行。

> [图：NadirPointing 姿态模型的 GUI 配置界面]

下面的脚本示例展示如何配置航天器使用地球 `NadirPointing` 姿态系统，其中本体 y 轴指向天底，且本体 x 轴与轨道法线矢量之间的夹角最小：

```
Create Spacecraft aSat;
aSat.Attitude               = NadirPointing;
aSat.AttitudeReferenceBody  = Earth
aSat.AttitudeConstraintType = OrbitNormal
aSat.BodyAlignmentVectorX   = 0
aSat.BodyAlignmentVectorY   = 1
aSat.BodyAlignmentVectorZ   = 0
aSat.BodyConstraintVectorX  = 1
aSat.BodyConstraintVectorY  = 0
aSat.BodyConstraintVectorZ  = 0

Create ForceModel Propagator1_ForceModel
Create Propagator Propagator1
Propagator1.FM        = Propagator1_ForceModel
Propagator1.MaxStep   = 10

Create OrbitView OrbitView1;
OrbitView1.Add                = {aSat, Earth}
OrbitView1.ViewPointReference = Earth
OrbitView1.ViewPointVector    = [ 30000 0 0 ]

BeginMissionSequence

Propagate Propagator1(aSat) {aSat.ElapsedSecs = 12000.0}
```

此示例将航天器姿态设为 `NadirPointing`，参考天体为地球，约束类型为 `OrbitNormal`，对准矢量为本体 y 轴（指向天底），约束矢量为本体 x 轴（使其与轨道法线夹角最小），然后传播 12000 秒。

### 可指令对地指向模型（Commandable Nadir Pointing Model）

`CommandableNadirPointing` 姿态模式与 `NadirPointing` 模式完全相同，但增加了在任务序列中用四元数设置姿态的能力。与 `NadirPointing` 模型一样，GMAT 不会计算角速度。

实现 `CommandableNadirPointing` 的动机来自一个任务需求：该任务需要计算相对于对地指向参考系的姿态机动（例如偏航翻转 yaw flip），并使用 GMAT 的质量属性和力矩模型对机动期间的角动量变化建模。GMAT 需要使用该姿态来计算需要积分的力矩。

解决方案是：在脚本中传播机动，在 GMAT 中设置姿态，使用该姿态执行所需的计算（本例中为力矩和动量计算），然后传播航天器到下一步，此时姿态被重置为对地指向模式。

详细步骤如下。所使用的四元数为：

- qRI —— 从惯性系到对地指向参考系的旋转
- qBR —— 从参考系到本体系的旋转
- qBI —— 从惯性系到本体系的旋转

下面引用的四元数函数位于用户函数目录中，`aSat` 指当前的 `Spacecraft` 对象。

1. 在开始时设置 qRI = aSat.Quaternion。这必须首先完成，因为对地指向参考系是直接从位置和速度计算的；否则会（错误地）使用默认姿态。
2. 如果处于机动转姿（slew）中，使用 PropagateQuaternion 函数在脚本中计算 qBR。如果相对于对地指向参考系的角速度为零，则跳过此步骤；此时 qBR 为常值。
3. 使用 ComposeQuaternions 函数计算 qBI = qBR * qRI。
4. 将 aSat.Quaternion 设置为 qBI。
5. 执行所需的 GMAT 计算。
6. 调用 Propagate 命令推进航天器状态。
7. 按需重复上述步骤。

下面的脚本演示了如何用脚本设置的四元数覆盖 GMAT 计算的四元数：

```
Create Spacecraft aSat;
aSat.DateFormat       = UTCGregorian;
aSat.Epoch            = '03 Jan 2021 09:00:01.000';
aSat.CoordinateSystem = EarthFixed;
aSat.DisplayStateType = Cartesian;
aSat.X                = 10767.10941722319;
aSat.Y                = -40769.63147707024;
aSat.Z                = -71.30282941332682;
aSat.VX               = -0.0003907864381020865;
aSat.VY               = -0.0001003662189780208;
aSat.VZ               = 0.003005535138648318;
aSat.Id               = 'aSat';

aSat.Attitude                 = CommandableNadirPointing;
aSat.AttitudeDisplayStateType = 'Quaternion';
aSat.AttitudeConstraintType   = 'OrbitNormal';
aSat.BodyAlignmentVectorX     = 1;
aSat.BodyAlignmentVectorY     = 0;
aSat.BodyAlignmentVectorZ     = 0;
aSat.BodyConstraintVectorX    = 0;
aSat.BodyConstraintVectorY    = 0;
aSat.BodyConstraintVectorZ    = 1;

Create Propagator aProp

Create ReportFile AttitudeReport;
AttitudeReport.Filename     = 'SC_CNP.report';
AttitudeReport.WriteHeaders = false;

Create Array q[4];

%---------- Mission Sequence ---------------

BeginMissionSequence;
% report initial value of quaternion
Report AttitudeReport aSat.Quaternion
Report AttitudeReport aSat.DirectionCosineMatrix

% need to do first get to properly initialize
q = aSat.Quaternion
Report AttitudeReport aSat.Quaternion
Report AttitudeReport aSat.DirectionCosineMatrix

% now set should work OK
aSat.Quaternion = [1 2 3 4]
Report AttitudeReport aSat.Quaternion
Report AttitudeReport aSat.DirectionCosineMatrix

% now propagate; [1 2 3 4] values should be replaced
% with nadir-pointing attitude
Propagate aProp(aSat) {aSat.ElapsedSecs = 30.0}
Report AttitudeReport aSat.Quaternion
Report AttitudeReport aSat.DirectionCosineMatrix
```

此示例演示 `CommandableNadirPointing` 模式下四元数的读取与覆盖：先报告初始四元数；执行一次读取（get）以正确初始化；然后将四元数设置为 [1 2 3 4] 并报告；传播 30 秒后，[1 2 3 4] 的值会被对地指向姿态替换。
### CCSDS 姿态星历报文（CCSDS Attitude Ephemeris Message）

CCSDS 姿态星历报文（Attitude Ephemeris Message，AEM）是一种用于姿态星历的 ASCII 标准，记录在推荐标准 CCSDS 504.0-B-1《ATTITUDE DATA MESSAGES》中。GMAT 支持该标准中定义的部分（而非全部）姿态报文。根据 CCSDS AEM 规范："本推荐标准中描述的姿态数据报文集，是在 CCSDS 各成员机构之间交叉支持的数据交换应用中进行姿态表示的基线概念。"此外，该标准的前言指出："派生的机构标准可以只实现本推荐标准所允许的可选特性的子集，也可以包含本推荐标准未涉及的特性。"有关支持的关键字类型以及创建可供 GMAT 用于姿态建模的 AEM 文件的详细信息，请参见下文。

> [图：CCSDS-AEM 姿态模型的 GUI 配置界面]

AEM 文件必须采用下图所示的格式（标准中的表 4-1）。头部（header）部分包含版本、生成机构和日期等高层信息。文件正文由成对的元数据（Metadata）块和数据块组成。元数据部分包含有关数据的信息，例如该数据块的首末历元、所采用的时间系统、参考系、姿态类型（四元数、欧拉角等）以及后续章节中记录的许多其他项目。数据部分包含历元和姿态数据行。

> [图：CCSDS AEM 文件格式示意（头部 + 元数据/数据块对）]

CCSDS AEM 文件示例如下：

```
CCSDS_AEM_VERS = 1.0
CREATION_DATE = 2002-11-04T17:22:31
ORIGINATOR = NASA/JPL

META_START
COMMENT This file was produced by M.R. Somebody, MSOO NAV/JPL, 2002 OCT 04.
COMMENT It is to be used for attitude reconstruction only.
COMMENT  The relative accuracy of these attitudes is 0.1 degrees per axis.
OBJECT_NAME = MARS GLOBAL SURVEYOR
OBJECT_ID = 1996-062A
CENTER_NAME = mars barycenter
REF_FRAME_A = EME2000
REF_FRAME_B = SC_BODY_1
ATTITUDE_DIR = A2B
TIME_SYSTEM = UTC
START_TIME = 1996-11-28T21:29:07.2555
USEABLE_START_TIME = 1996-11-28T22:08:02.5555
USEABLE_STOP_TIME = 1996-11-30T01:18:02.5555
STOP_TIME = 1996-11-30T01:28:02.5555
ATTITUDE_TYPE = QUATERNION
QUATERNION_TYPE = LAST
INTERPOLATION_METHOD = hermite
INTERPOLATION_DEGREE = 7
META_STOP

DATA_START
1996-11-28T21:29:07.2555 0.56748 0.03146 0.45689 0.68427
1996-11-28T22:08:03.5555 0.42319 -0.45697 0.23784 0.74533
1996-11-28T22:08:04.5555 -0.84532 0.26974 -0.06532 0.45652
< intervening data records omitted here >
1996-11-30T01:28:02.5555 0.74563 -0.45375 0.36875 0.31964
DATA_STOP

META_START
COMMENT This block begins after trajectory correction maneuver TCM-3.
OBJECT_NAME = mars global surveyor
OBJECT_ID = 1996-062A
CENTER_NAME = MARS BARYCENTER
REF_FRAME_A = EME2000
REF_FRAME_B = SC_BODY_1
ATTITUDE_DIR = A2B
TIME_SYSTEM = UTC
START_TIME = 1996-12-18T12:05:00.5555
USEABLE_START_TIME = 1996-12-18T12:10:00.5555
USEABLE_STOP_TIME = 1996-12-28T21:23:00.5555
STOP_TIME = 1996-12-28T21:28:00.5555
ATTITUDE_TYPE = QUATERNION
QUATERNION_TYPE = LAST
META_STOP

DATA_START
1996-12-18T12:05:00.5555 -0.64585 0.018542 -0.23854 0.72501
1996-12-18T12:10:05.5555 0.87451 -0.43475 0.13458 -0.16767
1996-12-18T12:10:10.5555 0.03125 -0.65874 0.23458 -0.71418
< intervening records omitted here >
1996-12-28T21:28:00.5555 -0.25485 0.58745 -0.36845 0.67394
DATA_STOP
```

CCSDS 文件需要许多关键字和字段，其中一些对所有文件类型都是必需的，另一些则视文件类型而"视情况必需"（Situationally Required，SR）（例如，如果 ATTITUDE_TYPE = QUATERNION，则必须包含 QUATERNION_TYPE）。下表从头部长键字开始描述 GMAT 的实现。

**头部长键字（Header Keywords）**

| 关键字 | 必需 | 描述及支持的值 |
|---|---|---|
| `CCSDS_AEM_VERS` | Y | 格式版本，形式为 "x.y"，其中 "y" 因更正和小改动而递增，"x" 因重大更改而递增。此行必须是文件中第一个非空行。在 GMAT 中版本必须设置为 1.0；如果版本不是受支持的版本，GMAT 会抛出异常。示例：`CCSDS_AEM_VERS = 1.0` |
| `COMMENT` | N | 注释（允许出现在 AEM 版本号之后、META_START 之后以及星历行数据块之前）。每行注释必须以此关键字开头。GMAT 不使用此字段。 |
| `CREATION_DATE` | Y | 文件创建日期/时间，格式为以下之一：YYYY-MM-DDThh:mm:ss[.d…d] 或 YYYY-DDDThh:mm:ss[.d…d]，其中 "YYYY" 为年，"MM" 为两位月份，"DD" 为两位日，"DDD" 为三位年内日序，"T" 为常量，"hh:mm:ss[.d…d]" 为 UTC 时间（时、分、秒及可选的小数秒）。小数点右侧可按需使用任意多个 "d" 字符以获得所需精度。所有字段都需要前导零。GMAT 不使用此字段。 |
| `ORIGINATOR` | Y | 创建机构（值应在 ICD 中指定）。GMAT 不使用此字段。 |
**元数据关键字（MetaData Keywords）**

| 关键字 | 必需 | 描述及支持的值 |
|---|---|---|
| `META_START` | Y | AEM 报文同时包含元数据和姿态星历数据；此关键字用于界定报文中元数据块的开始（元数据以块的形式提供，由 "META_START" 和 "META_STOP" 标记包围，以便于文件解析）。此关键字必须单独占一行。 |
| `COMMENT` | N | 仅允许出现在元数据部分开头的注释。每行注释必须以此关键字开头。GMAT 不使用此字段。示例：`COMMENT This is a comment` |
| `OBJECT_NAME` | Y | 与给定姿态数据对应的航天器名称。CCSDS 对此关键字的值没有限制，但建议使用 SPACEWARN Bulletin 中的名称，包括对象名称和国际标识符。示例：`OBJECT_NAME = EUTELSAT`。注意：GMAT 不使用此字段。在 GMAT 中，通过配置特定航天器来使用文件，从而将文件与特定航天器关联，如下所示：`Create Spacecraft aSat` / `aSat.Attitude = CCSDS-AEM` / `aSat.AttitudeFileName = myFile.aem` |
| `OBJECT_ID` | Y | 与给定姿态数据对应的对象的航天器标识符。有关航天器 Id 的建议请参见 AEM 规范。GMAT 不使用此字段。 |
| `CENTER_NAME` | N | 参考系的原点，可以是自然太阳系天体（行星、小行星、彗星和天然卫星），包括任何行星星系质心或太阳系质心，也可以是另一个航天器（此时 "CENTER_NAME" 的值遵循与 "OBJECT_NAME" 相同的规则）。CCSDS 对此关键字的值没有限制，但对于自然天体，建议使用 NASA/JPL 太阳系动力学组（Solar System Dynamics Group）的名称。GMAT 不使用此字段。 |
| `REF_FRAME_A` | Y | 指定变换中一个参考系的名称，变换方向由关键字 ATTITUDE_DIR 指定。完整的取值集合在 AEM 标准附录 A 中列举，"取值/示例" 列中提供了摘录。在 GMAT 中，REF_FRAME_A 可以是以下值之一，且必须与 REF_FRAME_B 不同：EME2000、SC_BODY_1。示例：`REF_FRAME_A = EME2000`、`REF_FRAME_A = SC_Body_1` |
| `REF_FRAME_B` | Y | 指定变换中一个参考系的名称，变换方向由关键字 ATTITUDE_DIR 指定。完整的取值集合在 AEM 标准附录 A 中列举，"取值/示例" 列中提供了摘录。在 GMAT 中，REF_FRAME_B 可以是以下值之一，且必须与 REF_FRAME_A 不同：EME2000、SC_BODY_1。示例：`REF_FRAME_A = EME2000`、`REF_FRAME_A = SC_Body_1` |
| `ATTITUDE_DIR` | Y | 姿态的旋转方向，指定变换从哪个坐标系出发：A2B 指定从 REF_FRAME_A 到 REF_FRAME_B 的变换；B2A 指定从 REF_FRAME_B 到 REF_FRAME_A 的变换。示例：`ATTITUDE_DIR = A2B`、`ATTITUDE_DIR = B2A` |
| `TIME_SYSTEM` | Y | 姿态星历数据和元数据所使用的时间系统。GMAT 支持以下选项：UTC。示例：`TIME_SYSTEM = UTC` |
| `START_TIME` | Y | 紧跟此元数据块之后的姿态星历数据所覆盖的总时间跨度的起点。新姿态星历数据块的 START_TIME 时间标签必须等于或大于前一个块的 STOP_TIME 时间标签。有关时间格式的详细信息请参见 CREATION_DATE 规范。注意：秒位上的精度只能保留到几微秒。示例：`START_TIME = 1996-12-18T14:28:15.117` |
| `USEABLE_START_TIME`、`USEABLE_STOP_TIME` | N | 可选的、紧跟此元数据块之后的姿态星历数据所覆盖的可用（USEABLE）时间跨度的起点和终点。为了在姿态星历数据块端点附近进行正确的插值，根据所使用的插值方法，可能有必要使用这些关键字，其取值位于由 START/STOP_TIME 时间标签所标示的姿态星历数据记录时间跨度之内。如果提供了此关键字，GMAT 仅使用 USEABLE 时间跨度内的数据进行插值；如果未提供，GMAT 使用 START_TIME/STOP_TIME 区段内的数据进行插值。有关时间格式的详细信息请参见 CREATION_DATE 规范。示例：`USEABLE_START_TIME = 1996-12-18T14:28:15.117`、`USEABLE_STOP_TIME = 1996-12-18T14:28:15.117` |
| `STOP_TIME` | Y | 紧跟此元数据块之后的姿态星历数据所覆盖的总时间跨度的终点。该姿态星历数据块的 STOP_TIME 时间标签必须等于或小于下一个块的 START_TIME 时间标签。有关时间格式的详细信息请参见 CREATION_DATE 规范。注意：秒位上的精度只能保留到几微秒。示例：`STOP_TIME = 1996-12-18T14:28:15.117` |
| `ATTITUDE_TYPE` | Y | 报文中数据行的格式。GMAT 支持以下类型：`ATTITUDE_TYPE = QUATERNION`、`ATTITUDE_TYPE = EULER_ANGLE` |
| `QUATERNION_TYPE` | SR | 四元数标量部分（QC）在姿态数据中的位置。仅当 ATTITUDE_TYPE 为四元数时使用此关键字，此时该字段为必需。示例：`QUATERNION_TYPE = FIRST`、`QUATERNION_TYPE = LAST` |
| `EULER_ROT_SEQ` | SR | 从 REF_FRAME_A 旋转到 REF_FRAME_B（或按 ATTITUDE_DIR 关键字指定的相反方向）的欧拉角转动序列。仅当 ATTITUDE_TYPE 为欧拉角时使用此关键字，此时该字段为必需。示例：`EULER_ROT_SEQ = 321` |
| `RATE_FRAME` | N | GMAT 不使用此字段。 |
| `INTERPOLATION_METHOD` | N | 建议用于紧跟此元数据块之后的数据块中姿态星历数据的插值方法。注意：当 ATTITUDE_TYPE = QUATERNION 时，GMAT 使用球面线性插值（spherical linear interpolation）；当 ATTITUDE_TYPE = EULER_ANGLE 时，GMAT 使用拉格朗日插值（lagrange interpolation）。示例：`INTERPOLATION_METHOD = LINEAR`、`INTERPOLATION_METHOD = LAGRANGE` |
| `INTERPOLATION_DEGREE` | SR | 建议用于紧跟此元数据块之后的数据块中姿态星历数据的插值阶数。必须为整数值。如果使用 "INTERPOLATION_METHOD" 关键字，则必须使用此关键字。该字段仅用于拉格朗日插值，此时取值必须在 0 到 9 之间。当拉格朗日插值阶数为零时，不执行插值，返回的姿态为所请求历元之前紧邻的值。示例：`INTERPOLATION_DEGREE = 7` |
| `META_STOP` | Y | 报文中元数据块的结束。AEM 报文同时包含元数据和姿态星历数据；此关键字用于界定报文中元数据块的结束（元数据以块的形式提供，由 "META_START" 和 "META_STOP" 标记包围，以便于文件解析）。此关键字必须单独占一行。 |

**数据关键字（Data Keywords）**

| 关键字 | 必需 | 描述及支持的值 |
|---|---|---|
| `DATA_START` | Y | 报文中姿态数据块的开始。AEM 报文同时包含元数据和姿态星历数据；此关键字用于界定报文中数据块的开始（数据以块的形式提供，由 "DATA_START" 和 "DATA_STOP" 标记包围，以便于文件解析）。此关键字必须单独占一行。 |
| `DATA_STOP` | Y | 报文中姿态数据块的结束。AEM 报文同时包含元数据和姿态星历数据；此关键字用于界定报文中数据块的结束（数据以块的形式提供，由 "DATA_START" 和 "DATA_STOP" 标记包围，以便于文件解析）。此关键字必须单独占一行。 |
| `QUATERNION` | SR | 当 ATTITUDE_TYPE = QUATERNION 时必需。四元数数据行的一般格式为：Epoch, QC, Q1, Q2, Q3 或 Epoch, Q1, Q2, Q3, QC。示例：`2000-01-01T11:59:28.000 0.195286 -0.079460 0.3188764 0.92404936` |
| `EULER ANGLE` | SR | 当 ATTITUDE_TYPE = EULER_ANGLE 时必需。欧拉角数据行的一般格式为：Epoch, X_Angle, Y_Angle, Z_Angle。示例：`2000-001T11:59:28.000 35.45409 -15.74726 18.803877` |

使用 CCSDS AEM 文件传播航天器姿态：

```
Create Spacecraft aSat ;
aSat.Attitude         = CCSDS-AEM;
aSat.AttitudeFileName = ...
         '../data/vehicle/ephem/ccsds/CCSDS_BasicEulerFile.aem'

Create Propagator aProp;

Create OrbitView a3DView
a3DView.Add = {aSat,Earth}

BeginMissionSequence;

Propagate aProp(aSat) {aSat.ElapsedSecs = 3600};
```

此示例将航天器姿态设为 `CCSDS-AEM`，指定 AEM 姿态星历文件，然后传播 3600 秒。
### 进动自旋模型（Precessing Spinner Model）

`PrecessingSpinner` 姿态模式将航天器姿态配置为：相对于惯性系中定义的指定矢量做稳态进动（precession）运动。自旋轴必须以航天器本体系给出。所提供的初始条件以 `Spacecraft` 上设置的初始历元为参考。

要配置航天器本体的自旋轴，设置 `BodySpinAxis`（表达在本体系中）；并使用 `NutationReferenceVector`（表达在惯性系中）定义稳态进动运动的参考矢量。要配置航天器的初始姿态，设置 `InitialPrecessionAngle` 定义进动的初始角，设置 `InitialSpinAngle` 定义自旋的初始角，设置 `NutationAngle` 定义章动角（为常值）。要配置进动角速度和自旋角速度，设置 `PrecessionRate` 和 `SpinRate`（均为常值）。

> **注意**：`PrecessingSpinner` 模型使用 `BodySpinAxis` 轴与惯性 x 轴的叉积作为初始姿态的参考。为避免当自旋轴与惯性 x 轴对齐或接近对齐时姿态未定义，在这种情况下会使用不同的参考矢量：当 `BodySpinAxis` 与惯性 x 轴的叉积小于 1e-5 时，使用惯性 y 轴作为参考矢量。更多细节请参见工程/数学规范文档。

> [图：PrecessingSpinner 姿态模型的 GUI 配置界面]

下面的脚本示例展示如何配置航天器使用 `PrecessingSpinner` 姿态模式，其中本体 z 轴相对于惯性 z 轴自旋。`PrecessionRate` 设置为 1 deg./sec.，`InitialPrecessionAngle` 设置为 0 deg./sec.，`SpinRate` 设置为 2 deg./sec.，`InitialSpinAngle` 设置为 0 deg./sec.，`NutationAngle` 设置为 30 deg.：

```
Create Spacecraft aSat; 
aSat.Attitude = PrecessingSpinner;
aSat.NutationReferenceVectorX = 0;
aSat.NutationReferenceVectorY = 0;
aSat.NutationReferenceVectorZ = 1;
aSat.BodySpinAxisX            = 0;
aSat.BodySpinAxisY            = 0;
aSat.BodySpinAxisZ            = 1;
aSat.InitialPrecessionAngle   = 0;
aSat.PrecessionRate           = 1;
aSat.NutationAngle            = 30;
aSat.InitialSpinAngle         = 0;
aSat.SpinRate                 = 2;

Create OrbitView OrbitView1;
OrbitView1.Add                = {aSat, Earth}
OrbitView1.ViewPointReference = Earth
OrbitView1.ViewPointVector    = [ 30000 0 0 ]

Create Propagator aProp
aProp.MaxStep = 10

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedSecs = 12000.0}
```

此示例将航天器姿态设为 `PrecessingSpinner`，章动参考矢量为惯性 z 轴，自旋轴为本体 z 轴，进动角速度 1 deg/s、自旋角速度 2 deg/s、章动角 30 deg，然后传播 12000 秒。

### 三轴运动学模型（Three Axis Kinematic Model）

`ThreeAxisKinematic` 姿态模型使用姿态四元数和角速度的函数来传播姿态状态。所提供的初始条件以提供给 `Spacecraft` 的初始历元为参考。该模型不包含任何力矩建模。在抗辐射加固（rad hard）处理器强大到足以支持数值积分之前，四元数运动学算法曾用于星载姿态计算。它在数学上与 `Spinner` 模型产生相同的结果；但在工程运用上不假定自旋轴固定——它的首次应用是在一个月球催化剂（Lunar Catalyst）项目中，该项目每秒从遥测中读取新的角速度。初始姿态可以用方向余弦矩阵（DCM）、四元数、欧拉角或修正罗德里格斯参数中的任意一种指定；初始角速度可以用角速度或欧拉角角速度指定。当使用欧拉角角速度时，转动序列由 `EulerAngleSequence` 字段决定。

> **警告**：注意：如果在脚本中工作，为 `ThreeAxisKinematic` 姿态模型设置 `CoordinateSystem` 不会产生任何效果。

> [图：ThreeAxisKinematic 姿态模型的 GUI 配置界面]

下面的示例将航天器配置为以 3 度/秒滚转：

```
Create Spacecraft aSat;
aSat.Attitude = ThreeAxisKinematic;

Create ForceModel Propagator1_ForceModel;
Create Propagator Propagator1;
Propagator1.FM = Propagator1_ForceModel;

aSat.Q1 = 0.0
aSat.Q2 = 0.0
aSat.Q3 = 0.0
aSat.Q4 = 1.0;
DefaultSC.AngularVelocityX = 3; % deg/sec
DefaultSC.AngularVelocityY = 0
DefaultSC.AngularVelocityZ = 0;

BeginMissionSequence

Propagate Propagator1(aSat) {aSat.ElapsedSecs = 12000.0}
```

此示例将航天器姿态设为 `ThreeAxisKinematic`，初始四元数设为单位四元数 [0 0 0 1]，角速度 x 分量设为 3 deg/sec（绕 x 轴滚转），然后传播 12000 秒。（译注：原文示例中角速度设置在 `DefaultSC` 上，与所创建的 `aSat` 不一致，此处照原文保留。）
