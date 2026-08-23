# GMAT 函数资源（GmatFunction）
> 译自 GMAT R2026a 帮助文档 GmatFunction.html

GMATFunction —— GMAT 函数的声明。

## 描述

`GmatFunction` 资源用于声明一个新的 GMAT 函数，或用于加载一个已存在的 GMAT 函数。该函数可以在任务序列中通过 GMAT 的 `CallGmatFunction` 命令调用。详见 `CallGmatFunction` 参考文档。

通过该 GMAT 函数，数据可以作为输入传入函数、作为输出接收。作为输入传入函数或作为输出从函数接收的数据还可以声明为全局。更多细节请参见 `Global` 参考文档。另请参见"备注"和"示例"一节，其中有关于 GMAT 函数及其用法的详细讨论。

**另请参见**：CallGmatFunction、Global

## 字段

| 字段 | 描述 |
|------|------|
| `FunctionPath` | 允许用户定义合法的函数路径。在 GUI 中，`FunctionPath` 字段在编辑函数并点击函数的 `Save As` 按钮后被激活。函数路径可以定义为绝对路径或相对路径。<br>数据类型：字符串<br>允许的值：合法的文件路径，可以是绝对路径或相对路径。在脚本模式下，如果完全不使用此字段，则函数的默认位置是 GMAT 的 ...\userfunctions\gmat\ 目录<br>访问方式：set<br>默认值：用户定义<br>单位：N/A<br>接口：GUI、脚本 |

## GUI

在 GUI 中，按以下步骤创建新的 `GmatFunction` 资源：

1. 在资源树（Resources Tree）中，右键点击 `Functions` 文件夹，选择 `Add` -> `GMAT Function` -> `New`
2. 在 `New GMAT function` 对话框中，输入你想要的函数名称。

> [图：新建 GMAT 函数对话框]

`GmatFunction` 资源的 GUI 窗口非常简单。当通过 GUI 创建新的 GMAT 函数时，`FunctionPath` 字段通过先编辑函数、再点击 `Save As` 按钮来定义，这让你可以以图形方式定义路径。

> [图：GmatFunction 资源的 GUI 编辑窗口]

## 备注

### 输入和输出参数

参数可以作为输入传入 GMAT 函数，也可以作为输出从 GMAT 函数返回。你可以把 GMAT 对象作为输入传入函数，并从函数接收整个对象作为输出。如果某个 GMAT 对象没有在主脚本和函数中都被声明为全局，那么所有传入函数或作为输出从函数接收的对象都被视为该函数和主脚本的局部对象。

在 GMAT 中，你可以使用 `CallGmatFunction` 命令把 GMAT 对象作为输入参数传入函数，并从函数接收对象作为输出。一般来说，GMAT 资源树中的任何对象都可以作为输入传入函数。用户最可能传入函数的对象是：与传播航天器相关的对象、在目标器（targeter）中执行差分修正（DC）的对象、在优化器循环中实现优化的对象、用户自定义的变量/数组/字符串，或用于绘制和报告参数的订阅器。注意，与大多数编程语言类似，如果在函数内部创建了与某个输入同名的资源，该对象会被全新初始化，输入对象的参数会被忽略。最可能作为输出参数从函数传出的对象是 `Spacecraft` 资源或用户自定义对象（如 `Variables`、`Arrays` 或 `Strings`）。

下面列出了可以作为输入和输出传入/传出函数的允许对象。另请参见"示例"一节，其中用两个独立的示例展示了两种不同方法：如何把局部对象作为输入传入函数、在函数内执行操作、然后把局部对象作为输出从函数接收。

输入参数可以是以下任一类型：

- 任何资源对象（例如 `Spacecraft`、`Propagator`、`DC`、`Optimizers`、`Impulsive` 或 `FiniteBurns`）
- 实数类型的资源参数（例如 *Spacecraft*.X）
- 字符串类型的资源参数（例如 *Spacecraft*.UTCGregorian）
- `Array`、`String` 或 `Variable` 资源

输出参数可以是以下任一类型：

- 资源对象，如 `Spacecraft`
- 实数类型的资源参数（例如 *Spacecraft*.X）
- 字符串类型的资源参数（例如 *Spacecraft*.UTCGregorian）
- `Array`、`String` 或 `Variable` 资源

### 全局航天器、订阅器和其他对象

在 GMAT 中，可以使用任务（Mission）树中的 `Global` 命令把对象声明为全局。GMAT 资源树中的所有默认对象或任何新的用户自定义资源都可以声明为全局。目前，任何默认或新用户自定义的坐标系、`SolarSystemBarycenter`、`SolarSystem`、默认或新用户自定义的传播器都是自动全局对象，不需要通过 `Global` 命令专门声明为全局。

经常会有这样的情况：你既在主脚本中传播航天器，也在 GMAT 函数内部传播航天器。此外，用户可能希望从主脚本和/或仅从函数内部，向同一批订阅器报告和/或绘制航天器的轨迹、参数、变量、数组和字符串。如果你希望向五个订阅器（即 `OrbitView`、`GroundTrack`、`XYPlot`、`ReportFile`、`EphemerisFile`）中的任何一个报告和绘制连续的数据集，那么请始终在主脚本和函数内部都将你的 `Spacecraft` 对象和订阅器对象声明为全局。遵守此规则可以正确地绘制图形、生成报告和星历文件，数据流将持续报告给所有订阅器。

一般来说，一个好的脚本编写习惯是：已声明为全局的对象不需要再作为输入或输出参数传入/传出函数。例如，如果 `Spacecraft`、所有订阅器对象或用于执行传播、目标求解或优化的对象已经声明为全局，那么你无需冗余地把这些全局对象再作为输入传入或作为输出从函数接收。话虽如此，GMAT 确实允许把全局声明的对象（如 `Spacecraft`、全局变量/数组/字符串）作为输入/输出参数传入和传出函数。全局声明的对象（如航天器、变量/数组/字符串）可以在主脚本和函数内部交替地向全局声明的订阅器绘制或报告。

参见"示例"一节，其中展示了三个示例，演示如何在主脚本和函数内部将航天器、全部五个订阅器和变量/数组声明为全局。运行这些示例时，请注意报告给所有五个订阅器的数据流是连续的。

### 在赋值命令中使用 GMAT 函数

GMAT 允许你在主脚本中以赋值命令的方式使用简单的 GMAT 函数。下面的示例片段展示了如何在数学语句中使用简单的 GMAT 函数。注意，在下面的片段中，GMAT 函数 `FunctionPath` 字段的函数路径没有被专门定义。只要在脚本模式下没有定义 `FunctionPath` 字段，这些函数的首选默认路径就在 GMAT 安装目录下的 ..GMAT\userfunctions\gmat\ 目录中：

```
%%Using a GMAT function in a mathematical statement

Create ReportFile rf

Create GmatFunction Math_GmatPi Math_GmatSin
Create GmatFunction Math_GmatAtan2 Math_GmatInv

Create Variable x y z pi in
Create Array A[2,2] B[2,2]

BeginMissionSequence

A(1,1) = 1
A(1,2) = 3
A(2,1) = 4
A(2,2) = 2

% no inputs into the function
pi = Math_GmatPi * 2
Report rf pi

% one input into the function
[pi] = Math_GmatPi
in = pi/4
x = Math_GmatSin(in) - 15
Report rf x

% two inputs:
in = 0.5
y = Math_GmatAtan2(in, x)^2
Report rf y

% array input/output:
B = Math_GmatInv(A)'
Report rf B


%%%% Math_GmatPi Function begins below:

function [pi] = Math_GmatPi
Create Variable pi
BeginMissionSequence
pi = acos(-1)


%%%% Math_GmatSin Function begins below:

function [y] = Math_GmatSin(x)
Create Variable y
BeginMissionSequence
y = sin(x)


%%%% Math_GmatAtan2 Function begins below:

function  [z] = Math_GmatAtan2(y, x)
Create Variable z
BeginMissionSequence
z = atan2(y, x)


%%%% Math_GmatInv Function begins below:

function  [B] = Math_GmatInv(A)
Create Array B[2,2]
BeginMissionSequence
B = inv(A)
```

逐段说明：

- 声明四个 GmatFunction 资源（Math_GmatPi、Math_GmatSin、Math_GmatAtan2、Math_GmatInv），未指定 FunctionPath，因此从默认目录 ...\userfunctions\gmat\ 加载。
- `pi = Math_GmatPi * 2`：无输入函数直接出现在数学表达式中；`[pi] = Math_GmatPi`：也可以用传统的输出参数形式调用。
- `x = Math_GmatSin(in) - 15`：单输入函数参与表达式；`y = Math_GmatAtan2(in, x)^2`：双输入函数的结果还可继续参与幂运算。
- `B = Math_GmatInv(A)'`：数组输入/输出，对函数返回的逆矩阵再做转置。
- 函数定义部分展示了四个 .gmf 文件的内容，每个文件恰好包含一个函数定义，函数体内用 Create 声明输出变量/数组后计算赋值。
## 示例

方法 1：如何把局部对象传入函数并从函数接收局部对象作为输出。把局部航天器和其他局部对象传入函数，在函数内执行霍曼转移目标求解，接收更新后的局部航天器和局部变量作为输出，最后在主脚本中把它们报告给局部订阅器。由于航天器和全部五个订阅器都只是局部对象（即未声明为全局），注意所有订阅器都是在更新后的航天器返回主脚本并开始传播后，才开始绘制和报告数据的。

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
anOrbitView.SolverIterations = Current
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
anEphemerisFile.Spacecraft = aSat

Create GmatFunction Targeter_Inside_Function
Targeter_Inside_Function.FunctionPath = ...
'C:\Users\rqureshi\Desktop\Targeter_Inside_Function.gmf' 

Create Variable DV1 DV2   

BeginMissionSequence;

% Pass local S/C, local objects into function and receive back
% updated local S/C and local variables:
'Hohmann Transfer'[DV1, DV2, aSat] ...
= Targeter_Inside_Function(aSat, aProp, TOI, GOI, DC)
 
TOI.Element1 = DV1
GOI.Element1 = DV2

% Report updated S/C:
Report rf2 aSat.UTCModJulian aSat.UTCGregorian aSat.X aSat.Y aSat.Z ...
aSat.VX aSat.VY aSat.VZ TOI.Element1 GOI.Element1

Propagate 'Prop one day' aProp(aSat) {aSat.ElapsedDays = 1.0}
 
Report rf2 aSat.UTCModJulian aSat.UTCGregorian aSat.X aSat.Y aSat.Z ...
aSat.VX aSat.VY aSat.VZ


%%%%%%%%%%% Function begins below:

function [dv1, dv2, aSat] = Targeter_Inside_Function(aSat, aProp, TOI, GOI, DC)

% Create local variables:
Create Variable dv1 dv2

BeginMissionSequence

Propagate 'Propagate to Periapsis' aProp(aSat) {aSat.Earth.Periapsis}   

 Target 'Hohmann Transfer' DC {SolveMode = Solve, ExitMode = SaveAndContinue}
    Vary 'Vary TOI' DC(TOI.Element1 = 1.0, {Perturbation = 0.0001, ...
	Lower = 0.0, Upper = 3.14159, MaxStep = 0.5})
    Maneuver 'Perform TOI' TOI(aSat)
    Propagate 'Prop to Apoapsis' aProp(aSat) {aSat.Earth.Apoapsis}
    Achieve 'Achieve RMAG = 42165' DC(aSat.Earth.RMAG = 42165)
    Vary 'Vary GOI' DC(GOI.Element1 = 1.0, {Perturbation = 0.0001, ...
	Lower = 0.0, Upper = 3.14159, MaxStep = 0.2})
    Maneuver 'Perform GOI' GOI(aSat)
    Achieve 'Achieve ECC = 0.005' DC(aSat.Earth.ECC = 0.005)
 EndTarget 
 
dv1 = TOI.Element1
dv2 = GOI.Element1
```

逐段说明：

- 主脚本创建航天器、力模型、传播器、两次脉冲机动（TOI/GOI）、差分修正器 DC、五个订阅器以及 GmatFunction 资源 Targeter_Inside_Function。
- `'Hohmann Transfer'[DV1, DV2, aSat] = Targeter_Inside_Function(aSat, aProp, TOI, GOI, DC)`：带命令标签的函数调用，把局部航天器、传播器、两次机动和 DC 全部作为输入传入，接收更新后的航天器和两个速度增量变量。
- 函数内部：先传播到近地点，然后用 Target/EndTarget 差分修正循环求解霍曼转移——第一次 Vary/Maneuver 施加 TOI 并传播到远地点，Achieve 目标为地心距 RMAG = 42165 km；第二次 Vary/Maneuver 施加 GOI 使轨道圆化，Achieve 目标为偏心率 ECC = 0.005。最后把两次机动的速度增量存入局部变量 dv1、dv2 返回。
- 主脚本接收后把 DV1/DV2 写回 TOI/GOI 的 Element1，报告更新后的状态，再传播一天并再次报告。由于所有对象都是局部的，订阅器只在主脚本传播期间才有数据。
方法 2：如何把局部对象传入函数并从函数接收局部对象作为输出。注意，在这种方法中，我们只把局部航天器作为输入传入函数；不再把其他局部对象传入函数，而是在函数内部创建所需的这些局部对象。与方法 1 类似，我们在函数内执行霍曼转移目标求解，然后把更新后的航天器和变量作为输出送回主脚本。最后，更新后的航天器在主脚本中传播一天，并由所有订阅器报告。由于航天器和全部五个订阅器都只是局部对象（即未声明为全局），注意所有订阅器都是在更新后的航天器在主脚本中开始传播后，才开始绘制和报告数据的。

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
anOrbitView.SolverIterations = Current
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
anEphemerisFile.Spacecraft = aSat

Create GmatFunction Targeter_Inside_Function
Targeter_Inside_Function.FunctionPath = ...
'C:\Users\rqureshi\Desktop\Targeter_Inside_Function.gmf' 

Create Variable DV1 DV2   

BeginMissionSequence;

% Pass only local S/C into the function and receive back
% updated local S/C and local variables:
'Hohmann Transfer'[DV1, DV2, aSat] ...
= Targeter_Inside_Function(aSat)
 
TOI.Element1 = DV1
GOI.Element1 = DV2

% Report updated S/C:
Report rf2 aSat.UTCModJulian aSat.UTCGregorian aSat.X aSat.Y aSat.Z ...
aSat.VX aSat.VY aSat.VZ TOI.Element1 GOI.Element1

Propagate 'Prop one day' aProp(aSat) {aSat.ElapsedDays = 1.0}
 
Report rf2 aSat.UTCModJulian aSat.UTCGregorian aSat.X aSat.Y aSat.Z ...
aSat.VX aSat.VY aSat.VZ


%%%%%%%%%%% Function begins below:

function [dv1, dv2, aSat] = Targeter_Inside_Function(aSat)

% Create local objects that are used to do targeting:
Create ForceModel aFM
aFM.CentralBody = Earth
aFM.PointMasses = {Earth}

Create Propagator aProp
aProp.FM = aFM

Create ImpulsiveBurn TOI
Create ImpulsiveBurn GOI

Create DifferentialCorrector DC

% Create local variables:
Create Variable dv1 dv2

BeginMissionSequence

Propagate 'Propagate to Periapsis' aProp(aSat) {aSat.Earth.Periapsis}   

 Target 'Hohmann Transfer' DC {SolveMode = Solve, ExitMode = SaveAndContinue}
    Vary 'Vary TOI' DC(TOI.Element1 = 1.0, {Perturbation = 0.0001, ...
	Lower = 0.0, Upper = 3.14159, MaxStep = 0.5})
    Maneuver 'Perform TOI' TOI(aSat)
    Propagate 'Prop to Apoapsis' aProp(aSat) {aSat.Earth.Apoapsis}
    Achieve 'Achieve RMAG = 42165' DC(aSat.Earth.RMAG = 42165)
    Vary 'Vary GOI' DC(GOI.Element1 = 1.0, {Perturbation = 0.0001, ...
	Lower = 0.0, Upper = 3.14159, MaxStep = 0.2})
    Maneuver 'Perform GOI' GOI(aSat)
    Achieve 'Achieve ECC = 0.005' DC(aSat.Earth.ECC = 0.005)
 EndTarget 
 
dv1 = TOI.Element1
dv2 = GOI.Element1
```

逐段说明：

- 与方法 1 的区别在于：主脚本只把 aSat 传入函数；力模型、传播器、TOI/GOI 机动和 DC 都在函数内部创建为局部对象。
- 函数内的目标求解流程与方法 1 完全相同：传播到近地点后，用 Target 循环先后求解 TOI（目标 RMAG = 42165 km）和 GOI（目标 ECC = 0.005）。
- 返回值 dv1、dv2、aSat 传回主脚本后，主脚本把速度增量写回自己的 TOI/GOI 并继续传播一天。

在本例中，我们在主脚本和函数内部都把航天器、所有订阅器和其他对象声明为全局。在函数内传播、在函数内执行目标求解，并把局部变量、全局航天器状态和全局变量（DV1、DV2）报告到全局报告文件。随后我们在主脚本中继续传播，并在主脚本中继续把航天器状态报告到全局报告文件。运行本例后，请特别注意所有订阅器：航天器轨迹在三个绘图订阅器上连续绘制，数据也连续地报告到两个报告文件和星历文件。

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
anOrbitView.SolverIterations = Current
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
anEphemerisFile.Spacecraft = aSat

Create GmatFunction Global_Subscribers
Global_Subscribers.FunctionPath = ...
'C:\Users\rqureshi\Desktop\Global_Subscribers.gmf' 

Create Variable DV1 DV2

BeginMissionSequence;

% Declare aSat, Subscribers and other objects as Global:
Global aSat
Global aFM TOI GOI DC %aProp is global by default. 
Global anOrbitView GroundTrack1 XYPlot1 rf rf2 anEphemerisFile
Global DV1 DV2

Report rf2 aSat.UTCGregorian aSat.UTCModJulian aSat.X aSat.Y aSat.Z ...
aSat.VX aSat.VY aSat.VZ

% Call function:
Global_Subscribers()
 
% Report updated Global S/C, TOI and GOI:
Report rf2 aSat.UTCGregorian aSat.UTCModJulian aSat.X aSat.Y aSat.Z ...
aSat.VX aSat.VY aSat.VZ TOI.Element1 GOI.Element1

Propagate 'Prop one more day' aProp(aSat) {aSat.ElapsedDays = 1.0}
 
Report rf2 aSat.UTCGregorian aSat.UTCModJulian aSat.X aSat.Y aSat.Z ...
aSat.VX aSat.VY aSat.VZ

% Report Global DV1 and DV2 to global 'rf2' in main script:
Report rf2 DV1 DV2


%%%%%%%%%%% Function begins below:

function Global_Subscribers()

% Create Local variables, string:
Create Variable sc_epoch x y z vx vy vz dv1 dv2;
Create String utc_epoch

Global aSat
Global aFM TOI GOI DC
Global anOrbitView GroundTrack1 XYPlot1 rf rf2 anEphemerisFile
Global DV1 DV2

BeginMissionSequence

Propagate 'Propagate to Periapsis' aProp(aSat) {aSat.Earth.Periapsis}   

 Target 'Hohmann Transfer' DC {SolveMode = Solve, ExitMode = SaveAndContinue}
    Vary 'Vary TOI' DC(TOI.Element1 = 1.0, {Perturbation = 0.0001, ...
	Lower = 0.0, Upper = 3.14159, MaxStep = 0.5})
    Maneuver 'Perform TOI' TOI(aSat)
    Propagate 'Prop to Apoapsis' aProp(aSat) {aSat.Earth.Apoapsis}
    Achieve 'Achieve RMAG = 42165' DC(aSat.Earth.RMAG = 42165)
    Vary 'Vary GOI' DC(GOI.Element1 = 1.0, {Perturbation = 0.0001, ...
	Lower = 0.0, Upper = 3.14159, MaxStep = 0.2})
    Maneuver 'Perform GOI' GOI(aSat)
    Achieve 'Achieve ECC = 0.005' DC(aSat.Earth.ECC = 0.005)
 EndTarget 
  
sc_epoch = aSat.UTCModJulian
utc_epoch = aSat.UTCGregorian
x   = aSat.X   
y   = aSat.Y
z   = aSat.Z
vx  = aSat.VX       
vy  = aSat.VY
vz  = aSat.VZ
dv1 = TOI.Element1 
dv2 = GOI.Element1

% Report local variables/strings to Global reportfile 'rf2':
Report rf2 utc_epoch sc_epoch x y z vx vy vz dv1 dv2
 
Propagate 'Prop one Day Inside Function' aProp(aSat) {aSat.ElapsedDays = 1.0}

% Report Global aSat state to global 'rf2':
Report rf2 aSat.UTCGregorian aSat.UTCModJulian  aSat.X aSat.Y aSat.Z aSat.VX ...
aSat.VY aSat.VZ TOI.Element1 GOI.Element1

% Report Global variables DV1 and DV2 to global 'rf2' in main script:
DV1 = TOI.Element1
DV2 = TOI.Element1
```

逐段说明：

- 主脚本在 `BeginMissionSequence` 之后立即用 `Global` 声明航天器、力模型/机动/DC、全部订阅器和 DV1/DV2 为全局（注释说明 aProp 默认即为全局，无需声明）。
- 主脚本先报告初始状态，然后 `Global_Subscribers()` 无参数调用函数——因为所有对象都是全局的，无需传递参数。
- 函数内部同样先声明同一批全局对象，然后执行与前例相同的霍曼转移目标求解；求解后把状态存入局部变量并报告到全局 rf2，再在函数内传播一天并再次报告；最后把 TOI 的速度增量赋给全局变量 DV1、DV2，使其在主脚本中可用。
- 主脚本在函数返回后继续传播一天并报告。由于订阅器也是全局的，函数内外的传播数据连续不断地写入所有订阅器。
与上一个示例一样，我们在主脚本和函数内部都把航天器、所有订阅器和其他对象声明为全局。这次 GMAT 函数嵌套在 While 和 If-EndIf 等控制逻辑语句中。在函数内执行 LEO 轨道保持（station-keeping）。示例运行时，请特别注意所有订阅器：航天器轨迹在三个绘图订阅器上连续绘制，数据也连续地报告到两个报告文件和星历文件。

```
Create Spacecraft LEOsat
LEOsat.DisplayStateType = Keplerian
LEOsat.SMA  = 6733.989999999996
LEOsat.ECC  = 0.0004329999999984123
LEOsat.INC  = 34.98399999999998
LEOsat.RAAN = 274.742
LEOsat.AOP  = 287.8049999999732
LEOsat.TA   = 294.0690000000269

Create ForceModel LEOprop_ForceModel
LEOprop_ForceModel.CentralBody = Earth
LEOprop_ForceModel.PrimaryBodies = {Earth}
LEOprop_ForceModel.PointMasses = {Luna, Sun}
LEOprop_ForceModel.SRP = On
LEOprop_ForceModel.GravityField.Earth.Degree = 4
LEOprop_ForceModel.GravityField.Earth.Order = 4
LEOprop_ForceModel.GravityField.Earth.PotentialFile = 'JGM2.cof'
LEOprop_ForceModel.Drag.AtmosphereModel = JacchiaRoberts
LEOprop_ForceModel.Drag.F107 = 150
LEOprop_ForceModel.Drag.F107A = 150

Create Propagator LEOprop
LEOprop.FM = LEOprop_ForceModel

Create ImpulsiveBurn TCM1
Create ImpulsiveBurn TCM2

Create DifferentialCorrector DC

Create OrbitView DefaultOrbitView
DefaultOrbitView.Add = {LEOsat, Earth}

Create XYPlot XYPlot1
XYPlot1.XVariable = LEOsat.A1ModJulian
XYPlot1.YVariables = {LEOsat.Earth.Altitude}

Create GroundTrack GroundTrack1
GroundTrack1.Add = {LEOsat}

Create ReportFile rf

Create ReportFile rf2
rf2.Add = {LEOsat.UTCModJulian, LEOsat.Earth.Altitude, ...
LEOsat.Earth.RMAG, LEOsat.Earth.ECC}

Create EphemerisFile anEphemerisFile
anEphemerisFile.Spacecraft = LEOsat

Create GmatFunction TargetLEOStationKeeping
TargetLEOStationKeeping.FunctionPath = ...
'C:\Users\rqureshi\Desktop\TargetLEOStationKeeping.gmf' 

Create Variable desiredRMAG desiredECC X Y Z

BeginMissionSequence

desiredRMAG = 6737
desiredECC = 0.00005

% Declare LEOsat, Subscribers and other objects as Global:
Global LEOsat
Global DC TCM1 TCM2 LEOprop_ForceModel
Global DefaultOrbitView XYPlot1 GroundTrack1
Global rf rf2 anEphemerisFile

While 'While ElapsedDays < 10' LEOsat.ElapsedDays < 10.0

Propagate 'Prop One Step' LEOprop(LEOsat)
	
If 'If Alt < Threshold' LEOsat.Earth.Altitude < 342

Propagate 'Prop To Periapsis' LEOprop(LEOsat) {LEOsat.Periapsis}

% Call function to implement SK. Pass local variables as input:
TargetLEOStationKeeping(desiredRMAG,desiredECC)

EndIf
	
EndWhile

Report rf LEOsat.UTCGregorian LEOsat.UTCModJulian LEOsat.X ...
LEOsat.Y LEOsat.Z LEOsat.Earth.Altitude LEOsat.Earth.ECC


%%%%%%%%%%% Function begins below:

function TargetLEOStationKeeping(desiredRMAG,desiredECC)
  
BeginMissionSequence

Global LEOsat
Global DC TCM1 TCM2 LEOprop_ForceModel
Global DefaultOrbitView XYPlot1 GroundTrack1
Global rf rf2 anEphemerisFile
  
Target 'Raise Orbit' DC {SolveMode = Solve, ExitMode = DiscardAndContinue}
	Vary 'Vary TCM1.V' DC(TCM1.Element1 = 0.002, {Perturbation = 0.0001, ...
	Lower = -9.999999e300, Upper = 9.999999e300, MaxStep = 0.05})
	Maneuver 'Apply TCM1' TCM1(LEOsat);
	Propagate 'Prop to Apoapsis' LEOprop(LEOsat) {LEOsat.Apoapsis}
	Achieve 'Achieve RMAG' DC(LEOsat.RMAG = desiredRMAG, {Tolerance = 0.1})
	Vary 'Vary TCM2.V' DC(TCM2.Element1 = 1e-005, {Perturbation = 0.00005, ...
	Lower = -9.999999e300, Upper = 9.999999e300, MaxStep = 0.05})
	Maneuver 'Apply TCM2' TCM2(LEOsat);
	Achieve 'Achieve ECC' DC(LEOsat.Earth.ECC = desiredECC)
EndTarget
```

逐段说明：

- 主脚本创建一颗 LEO 卫星（开普勒根数初始化）、带大气阻力和太阳光压的力模型、传播器、两次轨道修正机动（TCM1/TCM2）、DC 和全部订阅器；设置期望的地心距 desiredRMAG = 6737 km 和期望偏心率 desiredECC = 0.00005。
- 主脚本的 `While` 循环在 10 天内逐步传播；每当高度低于 342 km（`If` 判断）时，先传播到近地点，再调用 `TargetLEOStationKeeping(desiredRMAG, desiredECC)` 函数实施轨道保持——只把两个局部变量作为输入，航天器和其他对象通过全局声明共享。
- 函数内部再次声明同一批全局对象，然后用 Target 循环（ExitMode = DiscardAndContinue）求解：先在近地点施加 TCM1 并传播到远地点以达到期望 RMAG，再施加 TCM2 以达到期望偏心率。
- 循环结束后主脚本把最终状态报告到 rf。整个过程中，三个绘图订阅器和两个报告文件、星历文件都连续接收数据。

在本例中，所有数组、一个字符串和单个订阅器在主脚本和函数内部都被声明为全局。注意，全局数组被传入函数，计算叉积后，计算所得的全局数组（v5、v6）被送回主脚本。还要注意，全局数组和字符串在主脚本和函数内部都被报告到全局报告文件。

```
Create ReportFile rf
rf.WriteHeaders = false

Create GmatFunction cross3by1;
cross3by1.FunctionPath = ...
'C:\Users\rqureshi\Desktop\cross3by1.gmf'      

Create Array v1[3,1] v2[3,1] v3[3,1] ...
v4[3,1] v5[3,1] v6[3,1]
Create String tempstring

BeginMissionSequence

% Declare Arrays, string and subscriber as global:
Global v1 v2 v3 v4 v5 v6  tempstring rf

v1(1,1) = 1
v1(2,1) = 2
v1(3,1) = 3
v2(1,1) = 4
v2(2,1) = 5
v2(3,1) = 6
v3(1,1) = 8
v3(2,1) = 9
v3(3,1) = 10
v4(1,1) = 10
v4(2,1) = 11
v4(3,1) = 12

% Report global arrays/string to global 'rf':
Report rf v1 v2 v3 v4
tempstring = '--------------------'
Report rf tempstring

% Call function. Pass in Global arrays
% Receive global arrays in return:
[v5, v6] = cross3by1(v1, v2, v3, v4)

% Report global output to global 'rf':
Report rf v5 v6

tempstring = '--------------------'
Report rf tempstring


%%%%%%%%%%% Function begins below:

function [v5, v6] = cross3by1(vector1,vector2, vector3, vector4)

BeginMissionSequence

Global v1 v2 v3 v4 v5 v6  tempstring rf

v5(1,1) = vector1(2,1)*vector2(3,1) - vector1(3,1)*vector2(2,1)
v5(2,1) = -(vector1(1,1)*vector2(3,1) - vector1(3,1)*vector2(1,1))
v5(3,1) = vector1(1,1)*vector2(2,1) - vector1(2,1)*vector2(1,1)

v6(1,1) = vector3(2,1)*vector4(3,1) - vector3(3,1)*vector4(2,1)
v6(2,1) = -(vector3(1,1)*vector4(3,1) - vector3(3,1)*vector4(1,1))
v6(3,1) = vector3(1,1)*vector4(2,1) - vector3(2,1)*vector4(1,1)

v1 = v1 + 1
v2 = v2*2
v3 = v3/2
v4 = v4 + v4

% Continue to report global arrays/string to global 'rf':
Report rf v1 v2 v3 v4
tempstring = '--------------------'
Report rf tempstring
```

逐段说明：

- 主脚本声明 6 个 3×1 数组、一个字符串和报告文件 rf 为全局，给 v1–v4 赋值后报告，并输出分隔线。
- `[v5, v6] = cross3by1(v1, v2, v3, v4)` 把四个全局数组传入函数，接收两个叉积结果数组。
- 函数内部同样声明这些数组、字符串和 rf 为全局；先按叉积公式计算 v5 = v1×v2 和 v6 = v3×v4，然后对全局数组 v1–v4 做数学运算（加 1、乘 2、除 2、加倍）——这些修改因为是全局的，会直接反映到主脚本中；最后把修改后的 v1–v4 和分隔线继续报告到全局 rf。
- 主脚本接收 v5、v6 后报告它们。整个示例展示了全局数组既可作为输入/输出参数传递，又能在函数内被直接修改和报告。
