# 推力历史文件（ThrustHistoryFile）

> 译自 GMAT R2026a 帮助文档 ThrustHistoryFile.html

**ThrustHistoryFile** —— 输入推力/加速度矢量和质量流率的时间历程。

## 描述

`ThrustHistoryFile` 资源用于读入将施加到指定航天器的推力或加速度矢量的时间历程。用户可以选择性地读入适用于指定燃料资源的质量流率时间历程。

另请参阅：ThrustSegment（推力段）、BeginFileThrust（开始文件推力）、EndFileThrust（结束文件推力）。

## 字段

| 字段 | 描述 |
|------|------|
| **AddThrustSegment** | 用于指定给定推力/加速度和质量流率历史文件中包含的一个或多个推力段的方法。<br>• 数据类型：String<br>• 允许值：任何用户定义的 `ThrustSegment` 资源<br>• 访问权限：set<br>• 默认值：N/A<br>• 单位：N/A<br>• 接口：脚本 |
| **FileName** | 关联的推力/加速度和质量流率历史文件的文件名。该用户创建文件的格式细节在"备注"中描述。<br>• 数据类型：String<br>• 允许值：任何用户定义的文件名<br>• 访问权限：set<br>• 默认值：N/A<br>• 单位：N/A<br>• 接口：脚本 |

## 备注

### 推力历史文件的格式

推力历史文件包含若干数据块。每个数据块以 BeginThrust 关键字开始，以 EndThrust 关键字结束。更具体地说，数据块的开始由关键字 "BeginThrust {ThrustSegment 对象名}" 标识，以关键字 "EndThrust {ThrustSegment 对象名}" 结束。所指定的 `ThrustSegment` 资源定义给定数据块中的数据将如何使用。

我们假设用户已创建了一个脚本，其中已创建了 `ThrustSegment` 资源 `Segment1`。下面给出一个引用 `Segment1` 的示例推力历史文件。

```
BeginThrust {Segment1}
Start_Epoch = 29 Jan 2019 16:35:00.000
Thrust_Vector_Coordinate_System = EarthMJ2000Eq   
Thrust_Vector_Interpolation_Method  = None
Mass_Flow_Rate_Interpolation_Method = None
ModelAccelOnly
0.0     0.003 0.011 0.002
1.0     0.003 0.011 0.002
EndThrust {Segment1}
```

该历史文件中的 `Start_Epoch` 参数值指定文件中的推力/加速度数据应从 29 Jan 2019 16:35:00.000 UTCG 开始施加。`Thrust_Vector_Coordinate_System` 参数值指定该文件中的推力/加速度数据使用 EarthMJ2000Eq 坐标系。`Thrust_Vector_Interpolation_Method` 参数值指定该文件中的推力/加速度数据不应插值。`Mass_Flow_Rate_Interpolation_Method` 参数值指定该文件中的质量流率数据（如果有）不应插值。上面文件中的 `ModelAccelOnly` 是描述其后数据的头部，它告诉 GMAT 要执行哪种类型的加速度/推力和质量流率建模。在本例中，`ModelAccelOnly` 告诉 GMAT 我们仅建模加速度。

接下来，推力历史文件包含两行加速度数据。每行的第一个条目是相对于 `Start_Epoch` 值的经过秒数。每行的接下来三个条目是以 m/s² 为单位的加速度矢量。第一行中的 0.0 值表示加速度应在距 `Start_Epoch` 0 经过秒时（即 29 Jan 2019 16:35:00.000 UTCG）发生。此时的加速度矢量值为 (0.003 0.011 0.002) m/s²，在 EarthMJ2000Eq 坐标系中施加。第二行中的 1.0 值表示所施加的加速度应在 29 Jan 2019 16:35:01.000 UTCG 结束。此时的加速度矢量值为 (0.003 0.011 0.002) m/s²，在 EarthMJ2000Eq 坐标系中施加。注意，如果插值方法如此处所示为 `None`，则加速度以分段常值方式施加，只需要最后一条加速度记录的时间；加速度值被忽略。`Linear`（线性）和 `CubicSpline`（三次样条）插值方法将使用最后一条记录中的加速度值作为插值节点。
下表提供了关于推力历史文件中、封装在 `BeginThrust`/`EndThrust` 关键字对内的数据块里定义的四个参数的更多信息。

| 文件参数 | 描述 |
|------|------|
| **Start_Epoch** | 推力/加速度和质量流率数据的参考历元，采用 UTC 格里历格式。<br>• 数据类型：String<br>• 允许值：任何有效的 UTCG 格式历元<br>• 单位：N/A |
| **Thrust_Vector_Coordinate_System** | 用于指定推力/加速度矢量数据的坐标系。<br>• 数据类型：String<br>• 允许值：任何有效的内置或用户定义的 `CoordinateSystem` 资源。如果选择了用户定义的航天器体固连坐标系，用户还必须单独定义航天器姿态。<br>• 单位：N/A |
| **Thrust_Vector_Interpolation_Method** | 推力/加速度矢量分量使用的插值方法。<br>• 数据类型：String<br>• 允许值：Linear、CubicSpline 或 None<br>• 单位：N/A |
| **Mass_Flow_Rate_Interpolation_Method** | 质量流率使用的插值方法。<br>• 数据类型：String<br>• 允许值：Linear、CubicSpline 或 None<br>• 单位：N/A |

下表列出了描述推力历史文件中、封装在 `BeginThrust`/`EndThrust` 关键字对内的数据如何使用的四个有效头部值。

| 头部 | 描述 |
|------|------|
| **ModelThrustAndMassRate** | 每行数据包含五个元素。第一个元素是相对于 `Start_Epoch` 参数值的经过秒数（非负）。接下来三个元素是以牛顿（N）为单位的推力三分量。最后（第五个）元素是以 kg/s 为单位的质量流率。第五个元素为正值对应于质量减少，用于模拟燃料质量的消耗。 |
| **ModelThrustOnly** | 每行数据包含四个元素。第一个元素是相对于 `Start_Epoch` 参数值的经过秒数（非负）。接下来三个元素是以牛顿（N）为单位的推力三分量。 |
| **ModelAccelAndMassRate** | 每行数据包含五个元素。第一个元素是相对于 `Start_Epoch` 参数值的经过秒数（非负）。接下来三个元素是以 m/s^2 为单位的加速度三分量。最后（第五个）元素是以 kg/s 为单位的质量流率。第五个元素为正值对应于质量减少，用于模拟燃料质量的消耗。 |
| **ModelAccelOnly** | 每行数据包含四个元素。第一个元素是相对于 `Start_Epoch` 参数值的经过秒数（非负）。接下来三个元素是以 m/s^2 为单位的加速度三分量。 |

### 运动方程（EOM）随头部类型和 ThrustSegment.ApplyThrustScaleToMassFlow 参数值的变化

上表中列出的头部值选择将影响 GMAT 的运动方程（EOM）。此外，关联的 `ThrustSegment` 的 `ApplyThrustScaleToMassFlow` 标志的取值（True 或 False）也会影响 EOM。下表显示了 GMAT 的 EOM 如何随头部类型和 `ThrustSegment.ApplyThrustScaleToMassFlow` 参数值而变化。

| 头部 | ApplyThrustScaleToMassFlow | 总加速度 | 总质量流率 |
|------|:---:|------|------|
| ModelAccelOnly | True 或 False | a_Total = a + s·a_File | ṁ_Total = ṁ |
| ModelThrustOnly | True 或 False | a_Total = a + s·T_File / m_Total | ṁ_Total = ṁ |
| ModelAccelAndMassRate | True | a_Total = a + s·a_File | ṁ_Total = ṁ − s·s_m·ṁ_File |
| ModelAccelAndMassRate | False | a_Total = a + s·a_File | ṁ_Total = ṁ − s_m·ṁ_File |
| ModelThrustAndMassRate | True | a_Total = a + s·T_File / m_Total | ṁ_Total = ṁ − s·s_m·ṁ_File |
| ModelThrustAndMassRate | False | a_Total = a + s·T_File / m_Total | ṁ_Total = ṁ − s_m·ṁ_File |

符号说明：

- a_Total = 总加速度
- a = 除输入推力历史文件给出的加速度之外，所有其他来源产生的加速度
- a_File = 输入推力历史文件中给出的加速度
- m_Total = 总质量
- ṁ_Total = 总质量流率
- ṁ = 除输入文件给出的质量流率之外，所有其他来源产生的质量流率
- ṁ_File = 输入文件中给出的质量流率
- T_File = 输入文件中给出的推力
- s = ThrustSegment.ThrustScaleFactor（推力比例因子）。用户可以选择在估计过程中求解 s。
- s_m = ThrustSegment.MassFlowScaleFactor（质量流比例因子）。
## 示例

创建一个使用两个 `ThrustSegment` 的 `ThrustHistoryFile`。

```
Create ThrustHistoryFile aThrustHistoryFile
aThrustHistoryFile.AddThrustSegment = {Segment1, Segment2}   
aThrustHistoryFile.FileName = '../data/myThrustFile.thrust'

Create ThrustSegment Segment1 Segment2

BeginMissionSequence;
```

上述脚本可以通过语法检查，但要使其无错误运行，你必须创建一个推力文件 `myThrustFile.thrust`，并将其放在 GMAT 的 'data' 文件夹中。关于如何使用 `ThrustHistoryFile` 和 `ThrustSegment` 资源向航天器施加推力/加速度和质量流率剖面的完整示例，请参阅 BeginFileThrust（开始文件推力）帮助中的第一个示例。
