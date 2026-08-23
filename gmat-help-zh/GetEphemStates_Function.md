# 获取星历状态函数（GetEphemStates()）
> 译自 GMAT R2026a 帮助文档 GetEphemStates_Function.html

GetEphemStates() —— 用于从星历文件输出航天器初始和最终状态的函数。

## 脚本语法

```
[initialEpoch, initialState, finalEpoch, finalState] = 
      GetEphemStates(ephemType, sat, epochFormat, coordinateSystem)
```

输入：

- `ephemType`：星历类型（'STK'、'SPK'、'Code500'、'CCSDS-OEM'）
- `sat`：带有关联星历文件的 Spacecraft（航天器）
- `epochFormat`：单引号字符串，包含结果历元输出的合法历元格式
- `coordSystem`：结果状态输出的坐标系（CoordinateSystem）

输出：

- `initialEpoch`：文件中初始历元的字符串，采用所请求的 epochFormat
- `initialState`：所请求 coordinateSystem 下的 6 元素数组
- `finalEpoch`：文件中最终历元的字符串，采用所请求的 epochFormat
- `finalState`：所请求 coordinateSystem 下的 6 元素数组

## 描述

`GetEphemStates()` 是一个特殊函数，允许你从生成的航天器星历文件中输出航天器的初始和最终星历状态。`GetEphemStates()` 函数可以查询以下星历类型：STK-TimePosVel（即 STK .e 星历）、SPICE（SPK）、CCSDS 轨道星历电文（CCSDS-OEM）和 Code-500。你可以按自己选择的历元格式和坐标系请求所得的初始历元、初始状态、最终历元和最终状态。

存储在 `initialState` 数组中的初始状态输出对应于星历文件中星历初始历元处的状态。同样，存储在 `finalState` 数组中的最终状态输出对应于星历文件中星历最终历元处的最终状态。你可以以 GMAT 支持的任何历元格式请求初始和最终历元，也可以以 GMAT 的任何默认或用户自定义坐标系请求初始和最终状态。

**另请参见**：EphemerisFile、CoordinateSystem、Spacecraft

## GUI

> [图：GetEphemStates() 命令的 GUI 面板]

`GetEphemStates()` 的 GUI 非常简单，它只是反映了你在脚本模式中如何实现此函数。在脚本模式中使用 `GetEphemStates()` 函数最为方便。

## 备注

在使用 `GetEphemStates()` 函数查询 STK .e、CCSDS-OEM 或 Code-500 星历文件之前，你必须先把星历文件设置到 `Spacecraft` 资源的一个纯脚本字段 `EphemerisName` 上（即 *Spacecraft*.EphemerisName）。星历文件可以通过相对路径或绝对路径设置到这个纯脚本的 `EphemerisName` 字段。

在使用 `GetEphemStates()` 函数查询 SPICE 星历时，你完全不需要使用 `EphemerisName` 字段。相反，你必须把 SPICE 星历文件设置到 `Spacecraft` 资源的 `OrbitSpiceKernelName` 字段上（即 *Spacecraft*.OrbitSpiceKernelName）。SPICE 星历文件可以通过相对路径或绝对路径设置到 `OrbitSpiceKernelName` 字段。

"示例"一节将展示如何使用 `GetEphemStates()` 函数提取初始和最终星历状态的简单示例。

## 示例

先只运行"示例 1A"生成 STK-TimePosVel（即 STK .e）星历文件。然后运行"示例 1B"，它展示如何读取生成的 STK .e 星历文件，并以所需的历元格式和坐标系检索航天器的初始/最终状态。运行示例 1B 之前，请确保把 'STK_Ephemeris.e' 星历文件放在与主 GMAT 脚本相同的目录中。

```
%% Example 1A. Generate STK .e ephemeris file:

Create Spacecraft aSat

Create Propagator aProp

Create EphemerisFile anEphmerisFile
anEphmerisFile.Spacecraft = aSat
anEphmerisFile.Filename = 'STK_Ephemeris.e'
anEphmerisFile.FileFormat = STK-TimePosVel

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1}


%%% Example 1B. Read through .e ephemeris file using GetEphemStates():

Create Spacecraft aSat
aSat.EphemerisName = './STK_Ephemeris.e'

Create Propagator aProp

Create EphemerisFile anEphmerisFile
anEphmerisFile.Spacecraft = aSat
anEphmerisFile.Filename = 'STK_Ephemeris.e'
anEphmerisFile.FileFormat = STK-TimePosVel

Create Array initialState[6,1] finalState[6,1] 
Create String initialEpoch finalEpoch

Create ReportFile rf

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1}

[initialEpoch, initialState, finalEpoch, finalState] = ...
 GetEphemStates('STK', aSat, 'UTCGregorian', EarthMJ2000Eq)

Report rf initialEpoch initialState finalEpoch finalState
```

说明：示例 1A 传播 1 天并生成 STK .e 格式星历文件。示例 1B 中，关键一步是把星历文件路径赋给 aSat 的纯脚本字段 `EphemerisName`；传播后调用 `GetEphemStates('STK', aSat, 'UTCGregorian', EarthMJ2000Eq)`，以 UTC 公历格式和 EarthMJ2000Eq 坐标系取出文件的初始/最终历元与状态，并写入报告文件。

先只运行"示例 2A"生成 Code-500 星历文件。然后运行"示例 2B"，它展示如何读取生成的 Code-500 星历文件，并以所需的历元格式和坐标系检索航天器的初始/最终状态。运行示例 2B 之前，请确保把 'Code500_Ephemeris.eph' 星历文件放在与主 GMAT 脚本相同的目录中。

```
%% Example 2A. Generate Code-500 ephemeris file:

Create Spacecraft aSat

Create Propagator aProp

Create EphemerisFile anEphmerisFile
anEphmerisFile.Spacecraft = aSat
anEphmerisFile.Filename = 'Code500_Ephemeris.eph'
anEphmerisFile.FileFormat = Code-500

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1}


%%% Example 2B. Read through Code-500 ephemeris file using GetEphemStates():

Create Spacecraft aSat
aSat.EphemerisName = './Code500_Ephemeris.eph'

Create Propagator aProp

Create EphemerisFile anEphmerisFile
anEphmerisFile.Spacecraft = aSat
anEphmerisFile.Filename = 'Code500_Ephemeris.eph'
anEphmerisFile.FileFormat = Code-500

Create Array initialState[6,1] finalState[6,1] 
Create String initialEpoch finalEpoch

Create ReportFile rf

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 1}

[initialEpoch, initialState, finalEpoch, finalState] = ...
 GetEphemStates('Code500', aSat, 'TDBGregorian', EarthMJ2000Ec)

Report rf initialEpoch initialState finalEpoch finalState
```

说明：与示例 1 相同的两步流程，只是星历格式改为 Code-500；查询时 ephemType 用 'Code500'，历元格式改用 'TDBGregorian'，坐标系改用 EarthMJ2000Ec。

先只运行"示例 3A"生成 SPICE 星历文件。然后运行"示例 3B"，它展示如何读取生成的 SPICE 星历文件，并以所需的历元格式和坐标系检索航天器的初始/最终状态。运行示例 3B 之前，请确保把 'SPK_Ephemeris.bsp' 星历文件放在与主 GMAT 脚本相同的目录中。

```
%% Example 3A. Generate a Spice ephemeris file:

Create Spacecraft aSat
aSat.NAIFId = -10025001;
aSat.NAIFIdReferenceFrame = -9025001;

Create Propagator aProp

Create ImpulsiveBurn IB
IB.Element1 = 0.5

Create EphemerisFile anEphmerisFile
anEphmerisFile.Spacecraft = aSat
anEphmerisFile.Filename = 'SPK_Ephemeris.bsp'
anEphmerisFile.FileFormat = SPK

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 0.25}
Maneuver IB(aSat)
Propagate aProp(aSat) {aSat.ElapsedDays = 0.25}


%%% Example 3B. Read through a Spice ephemeris file using GetEphemStates():

Create Spacecraft aSat
aSat.NAIFId = -10025001
aSat.NAIFIdReferenceFrame = -9025001
aSat.OrbitSpiceKernelName = {'./SPK_Ephemeris.bsp'}

Create Propagator aProp

Create ImpulsiveBurn IB
IB.Element1 = 0.5

Create EphemerisFile anEphmerisFile
anEphmerisFile.Spacecraft = aSat
anEphmerisFile.Filename = 'SPK_Ephemeris.bsp'
anEphmerisFile.FileFormat = SPK

Create Array initialState[6,1] finalState[6,1] 
Create String initialEpoch finalEpoch

Create ReportFile rf

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 0.25}
Maneuver IB(aSat)
Propagate aProp(aSat) {aSat.ElapsedDays = 0.25}


[initialEpoch, initialState, finalEpoch, finalState] = ...
 GetEphemStates('SPK', aSat, 'UTCGregorian', EarthMJ2000Eq)

Report rf initialEpoch initialState finalEpoch finalState
```

说明：SPK 星历要求为航天器设置 NAIFId 和 NAIFIdReferenceFrame；示例 3A 传播 0.25 天、施加一次脉冲机动、再传播 0.25 天，生成含两段弧的 SPK 文件。示例 3B 中，SPICE 星历不使用 `EphemerisName`，而是把文件路径（花括号数组形式）赋给 `OrbitSpiceKernelName` 字段；重复同样的传播与机动后，用 `GetEphemStates('SPK', ...)` 查询初始/最终状态并输出。
