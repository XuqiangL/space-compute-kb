# 运行仿真器命令（RunSimulator）

> 译自 GMAT R2026a 帮助文档 RunSimulator.html

**RunSimulator** —— 生成仿真导航测量量。

## 脚本语法

```
RunSimulator Simulator_InstanceName
```

## 描述

`RunSimulator` 命令生成用户提供的 `Simulator` 资源中指定的仿真测量量，并创建输出文件，文件名在 `Simulator` 资源中指定。

**另请参阅**：Simulator

## 备注

### DSN 数据输出文件的内容

`RunSimulator` 命令执行完成后，将创建一个或多个输出文件，如指定的 `Simulator` 对象中所定义。输出文件中的每一行数据包含给定时刻某个特定测量量的信息。数据行的格式在 TrackingFileSet 资源帮助中有完整描述。

当您仿真 DSN 测距或多普勒测速时，可以选择来自发射地面站的频率是非斜坡（non-ramped）还是斜坡（ramped）的。如果希望建模斜坡数据，必须提供输入斜坡表。输入斜坡表的格式在 Tracking Data Types 资源帮助的"Transmit Frequency Ramp Records"（发射频率斜坡记录）一节中讨论。

下表显示了上行频段、C、M2 以及发射频率的值是如何计算的。第二列显示上行频段的计算方式，上行频段包含在测距和多普勒测量量的输出文件中。对于 S 频段输出"1"，对于 X 频段输出"2"。

输出的 GMAT 测量数据（GMD）文件包含观测值，该值使用《Tracking Data Types for Orbit Determination》中所示的公式计算。第三列显示用于计算 GMD 文件中所示观测值的 C（测距）或 M2（多普勒）的计算方式。最后，第四列显示发射频率的计算方式，发射频率直接出现在 GMD 文件中（仅 DSN 测距，DSN 多普勒不含），并且也用于计算 GMD 文件中给出的观测值。

| 测量类型 | 上行频段 | 用于计算观测值的 C（测距）或 M2（多普勒） | 用于计算观测值的发射频率 |
|----------|----------|--------------------------------------------|--------------------------|
| **仿真测距（无斜坡表）** | 根据用户在 Transmitter.Frequency 字段上设置的发射机频率确定。若频率在 [2000-4000] MHz 内，则上行频段为 S 频段；若频率在 [7000-8000] MHz 内，则上行频段为 X 频段。 | 根据上一列所示的上行频段结果设置。S 频段 C=1/2，X 频段 C=221/1498。<br>Transponder.TurnAroundRatio 的值对 C 无影响。 | f_T = Transmitter.frequency（此频率将写入 GMD 测距文件） |
| **仿真测距（有斜坡表）** | 斜坡表中的上行频段优先于用户设置的发射机频率和斜坡表中的发射频率。 | 根据上一列所示的上行频段结果设置。S 频段 C=1/2，X 频段 C=221/1498。<br>Transponder.TurnAroundRatio 的值对 C 无影响。 | f_T = 斜坡表频率（此频率将写入 GMD 测距文件） |
| **仿真多普勒（无斜坡表）** | 根据用户在 Transmitter.Frequency 字段上设置的发射机频率确定。若频率在 [2000-4000] MHz 内，则上行频段为 S 频段；若频率在 [7000-8000] MHz 内，则上行频段为 X 频段。 | M2 = Transponder.TurnAroundRatio | f_T = Transmitter.frequency |
| **仿真多普勒（有斜坡表）** | 斜坡表中的上行频段优先于用户设置的发射机频率和斜坡表中的发射频率。 | 根据上一列所示的上行频段结果设置。S 频段 M2=240/221，X 频段 M2=880/749。<br>Transponder.TurnAroundRatio 的值对 M2 无影响。 | f_T = 斜坡表频率 |

如 Transponder 帮助中所述，对于斜坡和非斜坡数据，应答机对象上设置的转发比 `Transponder.TurnAroundRatio` 将用于计算确定仿真测距和多普勒测量量值所需的介质修正。

### 地球章动更新间隔

为了在仿真与估计过程之间获得最佳一致性，应按如下方式将地球章动更新间隔设为 0。对所有测量类型，将地球章动更新间隔设为零都是良好的通用做法。

```
Earth.NutationUpdateInterval = 0
```

## 示例

运行仿真。

```
%Perform a simulation

Create Simulator mySim

BeginMissionSequence 
RunSimulator mySim
```

**中文说明**：创建仿真器 mySim 后，在任务序列中用 RunSimulator 执行仿真。

若要查看运行仿真的综合示例，请参见第 13 章《Simulate DSN Range and Doppler Data》教程。
