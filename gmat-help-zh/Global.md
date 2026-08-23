# 全局对象声明命令（Global）
> 译自 GMAT R2026a 帮助文档 Global.html

Global —— 将对象声明为全局对象。

## 脚本语法

```
Global ObjectList
```

`ObjectList`：列出所有你希望声明为全局的 GMAT 对象。

## 描述

在 GMAT 中，你可以使用一个特殊命令将 GMAT 对象声明为全局对象。通过使用 `Global` 命令，你可以通过 GUI 或脚本方式将 GMAT 的对象声明为全局。

将对象声明为全局的语法非常简单。在使用 `Global` 命令之后，只需列出需要全局声明的对象名称即可。一旦 `GmatFunction` 资源在初始化期间被声明，就可以使用 GMAT 的 `CallGmatFunction` 命令向函数传入参数或从函数接收参数（作为输入/输出）。作为输入传入函数或作为输出从函数接收的数据，可以使用 `Global` 命令声明为全局。有关 `Global` 命令的更多细节，请参见"备注"一节。

**另请参见**：GmatFunction、CallGmatFunction

## GUI

下图展示了 `Global` 命令的默认设置。默认情况下，只有 `Spacecraft` 对象被勾选并声明为全局。随着用户在 GMAT 的资源（Resources）树中创建更多对象，可声明为全局的对象列表也会增加。

> [图：Global 命令的默认面板，对象列表中只有 Spacecraft 被勾选]

请注意，在上图中，GMAT 默认已经将默认坐标系、`SolarSystemBarycenter`、`DefaultProp` 和 `SolarSystem` 等对象视为自动全局对象。此外，每当在资源树中创建新的坐标系或传播器时，GMAT 会自动将新创建的坐标系和传播器声明为全局对象。由于 GMAT 始终将默认或新创建的坐标系和传播器声明为全局，因此你无需对坐标系和传播器对象使用 `Global` 命令。

## 备注

### 全局对象的声明

GMAT 对象可以作为输入传入 GMAT 函数，也可以作为输出从函数返回。关于可以作为输入和输出传入/传出函数的允许对象列表，请参阅 `GmatFunction` 资源和 `CallGmatFunction` 命令的"备注"部分。默认情况下，在 GMAT 中，主脚本内创建的任何对象都被视为主脚本的局部对象；同样，GMAT 函数内创建的任何对象都被视为该函数的局部对象。在 GMAT 中，要将对象声明为全局，你必须在主脚本和函数内部都将该对象声明为全局。一个好的做法是：在主脚本和函数内部，都紧跟 `BeginMissionSequence` 行之后声明全局对象。

如果某个 GMAT 对象没有在主脚本和函数中都被声明为全局，那么所有作为输入传入函数和/或作为输出从函数接收的对象，都被视为该函数和主脚本的局部对象。

你经常会需要在主脚本和函数内部交替地传播航天器、执行差分修正（DC）或优化例程。每当你希望从主脚本和函数内部交替地向同一批订阅器（Subscriber）绘制连续的航天器轨迹数据并报告参数时，请始终在主脚本和函数内部都将你的 `Spacecraft` 对象和订阅器对象（即 `OrbitView`、`GroundTrack`、`XYPlot`、`ReportFile`、`EphemerisFile`）声明为全局。遵守此规则可以正确地绘制图形、生成报告和星历文件，数据流将持续报告给所有订阅器。

GMAT 允许将全局声明的对象（如 `Spacecraft`、全局变量/数组/字符串）作为输入/输出参数传入和传出函数。只要所有订阅器也被声明为全局，全局声明的对象（如 `Spacecraft`、变量/数组/字符串）就可以在主脚本和函数内部交替地被绘制或报告。

请参阅 `GmatFunction` 资源的"示例"一节，其中展示了另外三个示例，演示如何在主脚本和函数内部将航天器、五个订阅器、数组/变量/字符串声明为全局。

## 示例

将航天器、所有订阅器和变量声明为全局。全局变量作为输入传入函数，并作为全局输出从函数接收。运行该示例时，注意数据会持续报告给全部 5 个订阅器。

```
Create Spacecraft aSat

Create ForceModel aFM
aFM.CentralBody = Earth
aFM.PointMasses = {Earth}

Create Propagator aProp
aProp.FM = aFM

Create ImpulsiveBurn TOI
Create ImpulsiveBurn GOI

Create DifferentialCorrector DC

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}

Create GroundTrack GroundTrack1
GroundTrack1.Add = {aSat}
GroundTrack1.CentralBody = Earth

Create XYPlot XYPlot1
XYPlot1.XVariable = aSat.ElapsedDays
XYPlot1.YVariables = {aSat.EarthMJ2000Eq.X}

Create ReportFile rf
rf.Add = {aSat.UTCGregorian, aSat.EarthMJ2000Eq.X, ... 
aSat.EarthMJ2000Eq.Y, aSat.EarthMJ2000Eq.Z, ...
aSat.EarthMJ2000Eq.VX, aSat.EarthMJ2000Eq.VY, aSat.EarthMJ2000Eq.VZ}

Create ReportFile rf2
rf2.WriteHeaders = false

Create EphemerisFile anEphemerisFile
GMAT anEphemerisFile.Spacecraft = aSat

Create GmatFunction Global_Objects
Global_Objects.FunctionPath = ...
'C:\Users\rqureshi\Desktop\Global_Objects.gmf'

Create Variable T X Y Z VX VY VZ


BeginMissionSequence

Global aSat
Global aFM TOI GOI DC
Global anOrbitView GroundTrack1 XYPlot1 rf rf2 anEphemerisFile
Global T X Y Z VX VY VZ 

% Report initial state to Global 'rf2':
Report rf2 aSat.UTCGregorian aSat.X aSat.Y aSat.Z ...
aSat.VX aSat.VY aSat.VZ

Propagate aProp(aSat) {aSat.ElapsedDays = 1.0}

T = aSat.UTCModJulian
X = aSat.X
Y = aSat.Y
Z = aSat.Z
VX = aSat.VX
VY = aSat.VY
VZ = aSat.VZ

% Call function. Pass Global Variables as input:
% Receive updated global S/C state via global variables:
[T,X,Y,Z,VX,VY,VZ] = Global_Objects(T,X,Y,Z,VX,VY,VZ)

% Report global variables to global 'rf2':
Report rf2 T X Y Z VX VY VZ

% Re-report global S/C state:
Report rf2 aSat.UTCGregorian aSat.X aSat.Y aSat.Z ...
aSat.VX aSat.VY aSat.VZ


%%%%%%%% Function begins below:

function [T,X,Y,Z,VX,VY,VZ] = Global_Objects(T,X,Y,Z,VX,VY,VZ)


BeginMissionSequence

Global aSat
Global aFM TOI GOI DC
Global anOrbitView GroundTrack1 XYPlot1 rf rf2 anEphemerisFile
Global T X Y Z VX VY VZ 

% Report global variables to global 'rf2':
Report rf2 T X Y Z VX VY VZ

While aSat.ElapsedDays < 5
   Propagate aProp(aSat) {aSat.ElapsedDays = 0.5}
EndWhile

% Send global variables back to main script:
T = aSat.UTCModJulian
X = aSat.X
Y = aSat.Y
Z = aSat.Z
VX = aSat.VX
VY = aSat.VY
VZ = aSat.VZ
```

逐段说明：

- 初始化部分创建航天器 aSat、力模型、传播器、两个脉冲机动（TOI/GOI）、差分修正器 DC，以及 5 个订阅器（OrbitView、GroundTrack、XYPlot、两个 ReportFile）和一个 EphemerisFile；随后创建 GmatFunction 资源 `Global_Objects` 并指定函数文件路径，最后创建 7 个全局变量。
- 主脚本任务序列中，紧跟 `BeginMissionSequence` 之后用四条 `Global` 语句把航天器、力模型/机动/DC、全部订阅器和全部变量声明为全局；然后把初始状态报告到全局报告文件 rf2，传播 1 天，将航天器状态存入全局变量。
- `[T,X,Y,Z,VX,VY,VZ] = Global_Objects(...)` 调用函数：全局变量作为输入传入，函数返回更新后的全局变量；随后把全局变量和更新后的航天器状态再次报告到 rf2。
- 函数部分（`function ... = Global_Objects(...)` 开始）同样紧跟 `BeginMissionSequence` 声明同样的全局对象——这是关键规则：全局声明必须在主脚本和函数中成对出现。函数内先把接收到的全局变量报告到 rf2，然后用 While 循环继续传播到 5 天，最后把最新状态写回全局变量，返回给主脚本。
