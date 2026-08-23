# GMAT R2013b 发行说明（ReleaseNotesR2013b）

> 译自 GMAT R2026a 帮助文档 ReleaseNotesR2013b.html

GMAT R2013b 于 2013 年 8 月发布。这是自 2013 年 4 月以来的第一个版本，是本项目的第 7 个版本。这是一个仅限内部发布的版本，旨在支持 ACE 任务。以下为本版本关键变更摘要；完整清单见 JIRA 上的完整 R2013b 发行说明。

## 新功能

### 数据文件接口

GMAT 现在可以直接从数据文件加载 `Spacecraft` 状态和物理特性数据。新资源 `FileInterface` 控制与数据文件的接口，新的 `Set` 命令允许你在任务序列中应用数据。

> [图：FileInterface 与 Set 命令界面]

示例：

```
Create Spacecraft aSat
Create FileInterface tvhf
tvhf.Filename = 'statevec.txt'
tvhf.Format = 'TVHF_ASCII'

BeginMissionSequence

Set aSat tvhf
```

以上示例创建 FileInterface 资源读取 TVHF_ASCII 格式的状态向量文件，并在任务序列中用 Set 命令将数据应用到航天器。更多信息见 FileInterface 和 Set 参考文档。

### Code-500 星历格式

GMAT 的 `EphemerisFile` 资源现在可以写出 Code-500 格式的星历文件。Code-500 格式是由 NASA 戈达德航天飞行中心飞行动力学设施定义的二进制星历格式。

> [图：Code-500 星历文件配置]

```
Create Spacecraft sc
Create Propagator prop
Create EphemerisFile ephem
ephem.Spacecraft = sc
ephem.Filename = 'ephem.eph'
ephem.FileFormat = 'Code-500'
ephem.StepSize = 60
ephem.OutputFormat = 'PC'

BeginMissionSequence

Propagate prop(sc) {sc.ElapsedDays = 1}
```

以上示例配置 EphemerisFile 资源以 Code-500 格式、60 秒步长、PC 字节序输出一天的星历。有关此格式的更多信息见 EphemerisFile 参考文档。

### 新的局部对准-约束坐标系

局部对准-约束（local aligned-constrained）坐标系是由一个对准向量（基于参考对象相对于原点的位置定义）和两个约束向量定义的坐标系。这是一个高度灵活的坐标系，可根据任务需求以多种方式定义。要使用它，在创建新 `CoordinateSystem` 时选择 `LocalAlignedConstrained` 轴类型。

> [图：LocalAlignedConstrained 坐标系配置]

```
Create CoordinateSystem ACECoordSys
ACECoordSys.Origin = Earth
ACECoordSys.Axes = LocalAlignedConstrained
ACECoordSys.ReferenceObject = ACE
ACECoordSys.AlignmentVectorX = 0
ACECoordSys.AlignmentVectorY = 0
ACECoordSys.AlignmentVectorZ = 1
ACECoordSys.ConstraintVectorX = 1
ACECoordSys.ConstraintVectorY = 0
ACECoordSys.ConstraintVectorY = 0
ACECoordSys.ConstraintCoordinateSystem = EarthMJ2000Ec
ACECoordSys.ConstraintReferenceVectorX = 0
ACECoordSys.ConstraintReferenceVectorY = 0
ACECoordSys.ConstraintReferenceVectorZ = 1
```

以上示例创建以地球为原点、以 ACE 航天器为参考对象的局部对准-约束坐标系。更多信息见 CoordinateSystem 参考文档。

## 改进

### 力模型参数

现在可以访问依赖 `ForceModel` 的参数，如 `Spacecraft` 加速度和大气密度。新参数为：

- `Spacecraft`.`ForceModel`.Acceleration
- `Spacecraft`.`ForceModel`.AccelerationX
- `Spacecraft`.`ForceModel`.AccelerationY
- `Spacecraft`.`ForceModel`.AccelerationZ
- `Spacecraft`.`ForceModel`.AtmosDensity

### 空间点参数

所有在空间中具有坐标的资源现在都有笛卡尔位置和速度参数，因此你可以访问星历信息。这包括所有内置太阳系天体和其他资源，如 `CelestialBody`、`Planet`、`Moon`、`Asteroid`、`Comet`、`Barycenter`、`LibrationPoint` 和 `GroundStation`：

- `CelestialBody`.`CoordinateSystem`.X
- `CelestialBody`.`CoordinateSystem`.Y
- `CelestialBody`.`CoordinateSystem`.Z
- `CelestialBody`.`CoordinateSystem`.VX
- `CelestialBody`.`CoordinateSystem`.VY
- `CelestialBody`.`CoordinateSystem`.VZ

注意，要使用这些参数，必须先将资源的历元设置为想要获取数据的所需历元。示例：

```
Create ReportFile rf

BeginMissionSequence

Luna.Epoch.A1ModJulian = 21545
Report rf Luna.EarthMJ2000Eq.X Luna.EarthMJ2000Eq.Y Luna.EarthMJ2000Eq.Z ...
       Luna.EarthMJ2000Eq.VX Luna.EarthMJ2000Eq.VY Luna.EarthMJ2000Eq.VZ
```

以上示例将月球（Luna）的历元设置为 A1 修正儒略历 21545，然后报告其在 EarthMJ2000Eq 坐标系中的位置和速度分量。

## 兼容性变更

- `EphemerisFile`.InitialEpoch 现在不能晚于 `EphemerisFile`.FinalEpoch。详见 EphemerisFile 参考文档。
- 当 `EphemerisFile`.FileFormat 设置为 'SPK' 时，`EphemerisFile`.CoordinateSystem 必须以 MJ2000Eq 作为轴系统。此星历格式不再允许其他轴系统。详见 EphemerisFile 参考文档。
- 已弃用的字段 `Thruster`.Element{1–3} 已被移除。请改用 `Thruster`.ThrustDirection{1–3}。详见 Thruster 参考文档。
- 字符串中的制表符（Tab）现在按字面处理，不再被转换为空格。详见 GMT-3336。

## 已修复与已知问题

本版本关闭了 50 多个 bug。关键 bug 及解决方案清单见 "Critical Issues Fixed in R2013b" 报告；次要问题见 "Minor Issues Fixed for R2013b" 报告。

### 已知问题

影响此版本 GMAT 的所有已知问题见 JIRA 中的 "Known Issues in R2013b" 报告。本版本中几个重要的已知问题：

| ID | 描述 |
| --- | --- |
| GMT-2561 | 闰秒期间的 UTC 历元输入和报告不正确。 |
| GMT-3043 | 创建遮蔽内置数学函数的变量时验证不一致。 |
| GMT-3108 | 带 STM 和 Propagate Synchronized 的 OrbitView 不能在正确位置显示航天器。 |
| GMT-3289 | 使用 SPK 传播器向后传播时首步算法失败。 |
| GMT-4097 | 星历文件在某些不连续类型处未分块写出文件。 |
| GMT-3350 | 单引号要求在不同对象和模式间不一致。 |
| GMT-3556 | 无法在命令模式中将贮箱与推力器关联。 |
| GMT-3629 | 以 --minimize 启动时 GUI 进入错误状态。 |
| GMT-3669 | 优化期间 OrbitView 中不绘制行星。 |
| GMT-3738 | 无法在 CallMatlabFunction 中设置独立的 FuelTank、Thruster 字段。 |
| GMT-3745 | SPICE 星历压力测试未为整个任务序列写出星历。 |