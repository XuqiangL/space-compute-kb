# #Include 宏（IncludeMacro）
> 译自 GMAT R2026a 帮助文档 IncludeMacro.html

\#Include 宏 —— 加载或导入脚本片段。

## 脚本语法

```
#Include './Define_Path_to_Script_Snippet_File_In_SingleQuotes.txt'
```

```
#Include UserStringVariable
```

## 描述

使用 `#Include` 宏，GMAT 现在允许你在脚本初始化和任务执行期间从外部文件加载 GMAT 资源和脚本片段。这是一个强大的特性，允许你在多个用户和/或多个脚本之间复用配置。该特性可用于简化运行操作的自动化，以及蒙特卡洛（Monte-Carlo）和参数扫描——这些用例有大量公共数据，但每次执行之间有部分数据会变化。

你现在可以用 `#Include` 宏加载的脚本片段外部文件可以使用任何文件扩展名，不过最常用的扩展名是（*.script）或（*.txt）。`#Include` 宏既可以在 `BeginMissionSequence` 脚本命令之前、也可以在之后用于从外部文件加载片段。`#Include` 宏只能通过脚本模式使用，不允许通过 GUI 使用。

## GUI

关于使用 `#Include` 宏时 GMAT GUI 的行为，有两条规则：

1. 如果在 `BeginMissionSequence` 之前使用了任何 `#Include` 宏，那么 GMAT 的 GUI 可编辑、可运行，但你无法通过 GUI 的 `Save` 按钮保存 GMAT 脚本。当然，你可以在脚本模式中修改脚本并从脚本模式保存更改。
2. 如果在 `BeginMissionSequence` 之前没有 `#Include` 宏，而在 `BeginMissionSequence` 之后有任意数量的 `#Include` 宏，那么 GMAT 的 GUI 可编辑、可运行且可保存（即你可以在 GUI 中修改对象，然后通过 GUI 的 `Save` 按钮把这些更改保存到脚本）。

每当你加载并运行可能在 `BeginMissionSequence` 命令之前使用了 `#Include` 宏的 GMAT 脚本时（即上述规则 1），GMAT 的资源（Resources）、任务（Mission）和输出（Output）树的颜色会变为浅橄榄绿，并且在 GMAT 主屏幕顶部中央会以红色显示 `Non-Savable GUI Mode`（不可保存 GUI 模式）消息。浅橄榄绿的颜色变化和 `Non-Savable GUI Mode` 消息只是在告诉你：GMAT 的 GUI 可编辑、可运行，但你无法通过 GMAT GUI 的 `Save` 按钮保存对 GMAT 脚本的更改。

如果你的 GMAT 脚本只在 `BeginMissionSequence` 之后包含 `#Include` 宏（即上述规则 2），那么 GMAT 的资源、任务和输出树不会发生颜色变化，你可以从 GUI 或脚本模式保存对脚本的更改。

## 备注

在 GMAT 中，定义要用 `#Include` 宏加载的外部文件路径的默认方法是：`'./My_Script_Snippet.txt'`。这是定义脚本片段文件路径最简单、最方便的方法，因为它只要求你的主脚本和脚本片段文件位于同一目录中。你也可以定义指向外部脚本片段文件的相对路径（`'..\My_Script_Snippet.txt'`）和绝对路径。

你也可以使用已创建的 String（字符串）变量的值作为 `#Include` 的路径。例如，设置变量为 `UserString = './My_Script_Snippet.txt'` 后，脚本语句 `#Include UserString` 就会包含你列出的文件。

"示例"一节展示了简单而强大的例子，说明如何使用 `#Include` 宏来简化你的主 GMAT 脚本。

## 示例

从名为 'Initialize_Spacecraft.txt' 的外部脚本片段文件初始化航天器。运行本例的方法：创建一个 .txt 文件，粘贴 'Initialize_Spacecraft.txt' 的内容，并把该片段脚本放在与主 GMAT 脚本相同的目录中。

```
Create Spacecraft aSat

%Initialize aSat from external file:
#Include './Initialize_Spacecraft.txt'

Create Propagator aProp

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}

BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedDays = 0.5}


%%%%%% Contents of 'Initialize_Spacecraft.txt' snippet file begins below:

aSat.DateFormat = UTCGregorian
aSat.Epoch = '02 Jan 2000 11:59:28.000'
aSat.CoordinateSystem = EarthMJ2000Eq
aSat.DisplayStateType = Cartesian
aSat.X = 8000
aSat.Y = 2000
aSat.Z = 4000
aSat.VX = 0.5
aSat.VY = 7.5
aSat.VZ = 1.5
aSat.DryMass = 1000
aSat.Cd = 2.2
aSat.Cr = 1.8
aSat.DragArea = 20
aSat.SRPArea = 1
aSat.NAIFId = -10009001
aSat.NAIFIdReferenceFrame = -9009001
aSat.OrbitColor = Yellow
aSat.TargetColor = Teal
aSat.Id = 'SatId'
aSat.Attitude = CoordinateSystemFixed
aSat.SPADSRPScaleFactor = 1
aSat.ModelFile = 'aura.3ds'
aSat.ModelOffsetX = 0
aSat.ModelOffsetY = 0
aSat.ModelOffsetZ = 0
aSat.ModelRotationX = 0
aSat.ModelRotationY = 0
aSat.ModelRotationZ = 0
aSat.ModelScale = 1
aSat.AttitudeDisplayStateType = 'Quaternion'
aSat.AttitudeRateDisplayStateType = 'AngularVelocity'
aSat.AttitudeCoordinateSystem = EarthMJ2000Eq
aSat.EulerAngleSequence = '321'
```

说明：主脚本只创建 aSat 本身，然后用 `#Include` 从外部文件初始化 aSat 的全部字段（历元、坐标系、笛卡尔状态、物理属性、颜色、姿态、3D 模型等）；再创建传播器和轨道视图，传播半天。由于 `#Include` 出现在 `BeginMissionSequence` 之前，此脚本在 GUI 中处于不可保存模式。

在本例中，我们通过 `#Include` 宏调用一个只在 `BeginMissionSequence` 命令之后使用的外部文件。从名为 'Perform_FiniteBurn.txt' 的外部脚本片段文件执行一次有限推力机动。运行本例的方法：创建一个 .txt 文件，粘贴 'Perform_FiniteBurn.txt' 的内容，并把该片段脚本放在与主 GMAT 脚本相同的目录中。

```
Create Spacecraft aSat

Create ChemicalTank aFuelTank

Create ChemicalThruster aThruster
aThruster.DecrementMass = true
aThruster.Tank = {aFuelTank}
aThruster.C1 = 1000 % Constant Thrust
aThruster.K1 = 300 % Constant Isp

aSat.Thrusters = {aThruster}
aSat.Tanks = {aFuelTank}

Create ForceModel aFM
aFM.CentralBody = Earth
aFM.PointMasses = {Earth}

Create Propagator aProp
aProp.FM = aFM

Create FiniteBurn aFB
aFB.Thrusters = {aThruster}

Create ReportFile rf
rf.Add = {aSat.UTCGregorian, aFB.TotalAcceleration1, ...
aFB.TotalAcceleration2, aFB.TotalAcceleration3, ...
aFB.TotalMassFlowRate, aFB.TotalThrust1, ...
aFB.TotalThrust2, aFB.TotalThrust3, ...
aSat.aThruster.MassFlowRate, ...
aSat.aThruster.ThrustMagnitude, aSat.aThruster.Isp}

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}


BeginMissionSequence

Propagate aProp(aSat) {aSat.ElapsedSecs = 1000}

%Perform a FiniteBurn from an external file:
#Include './Perform_FiniteBurn.txt'

Propagate aProp(aSat) {aSat.ElapsedSecs = 1000}


%%%%%% Contents of 'Perform_FiniteBurn.txt' snippet file begins below:

% Do a Finite-Burn for 1800 Secs

BeginFiniteBurn aFB(aSat)
Propagate aProp(aSat) {aSat.ElapsedSecs = 1800,  OrbitColor = Yellow}
EndFiniteBurn aFB(aSat)
```

说明：主脚本完整创建所有资源（航天器、燃料箱、推力器、有限推力弧段 aFB、报告文件等）；任务序列中先传播 1000 秒，然后用 `#Include` 引入外部片段执行 1800 秒的有限推力机动（BeginFiniteBurn/Propagate/EndFiniteBurn），最后再传播 1000 秒。由于 `#Include` 只出现在 `BeginMissionSequence` 之后，此脚本在 GUI 中可正常保存。

在本例中，我们通过 `#Include` 宏调用在 `BeginMissionSequence` 之前和之后都使用的外部文件。注意，资源树中的所有对象都从名为 'Entire_Resources_Tree.txt' 的外部脚本片段文件导入并初始化；同样，任务树中的所有命令都从名为 'Entire_Mission_Tree.txt' 的外部片段文件加载。运行本例的方法：创建一个 .txt 文件并粘贴 'Entire_Resources_Tree.txt' 的内容；再创建另一个 .txt 文件并粘贴 'Entire_Mission_Tree.txt' 的内容。把这两个片段脚本放在与主 GMAT 脚本相同的目录中，然后运行主 GMAT 脚本。

```
% Initialize all Resources tree objects
% from an external file:
#Include './Entire_Resources_Tree.txt'

BeginMissionSequence

% Execute all Mission tree commands
% from an external file:
#Include './Entire_Mission_Tree.txt'


%%%%%% Contents of 'Entire_Resources_Tree.txt' snippet file begins below:

Create Spacecraft aSat

Create Propagator aProp

Create ImpulsiveBurn TOI

Create DifferentialCorrector aDC

Create OrbitView anOrbitView
anOrbitView.Add = {aSat, Earth}
anOrbitView.SolverIterations = All


%%%%%% Contents of 'Entire_Mission_Tree.txt' snippet file begins below:

Propagate aProp(aSat) {aSat.Earth.Periapsis}

Target aDC
Vary aDC(TOI.Element1 = 0.24, {Perturbation = 0.001, ... 
Lower = 0.0, Upper = 3.14159, MaxStep = 0.5})
Maneuver TOI(aSat)
Propagate aProp(aSat) {aSat.Earth.Apoapsis}
Achieve aDC(aSat.Earth.RMAG = 42165)
EndTarget
```

说明：主脚本被精简为两条 `#Include` 宏：第一条（在 BeginMissionSequence 之前）加载整个资源树——创建航天器、传播器、脉冲机动 TOI、差分修正器和轨道视图；第二条（在 BeginMissionSequence 之后）加载整个任务树——传播到近地点后执行 Target 差分修正循环，调整 TOI 使航天器到达远地点时地心距 RMAG = 42165 km。由于存在 BeginMissionSequence 之前的 `#Include`，此脚本在 GUI 中不可保存。
