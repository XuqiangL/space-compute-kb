# 目标求解（Target）

> 译自 GMAT R2026a 帮助文档 Target.html

**Target** —— 通过改变一个或多个参数来求解条件。

## 脚本语法

```
Target SolverName [{SolveMode = value, ExitMode = value, ShowProgressWindow = value}]
   Vary 命令 ...
   脚本语句 ...
   Achieve 命令 ...
EndTarget
```

> **注意**：对于这条复杂命令，请参阅"备注"和"描述"部分。允许多个 `Vary` 和 `Achieve` 命令。脚本语句可以出现在 `Target` 序列中的任何位置。

## 描述

`Target` 和 `EndTarget` 命令用于定义一个目标求解（Target）序列，例如，用于确定将轨道远地点提升到 42164 km 所需的机动分量。另一个常见的目标求解示例是确定使月球转移轨道与月球对齐所需的停泊轨道指向。GMAT 中的 `Target` 序列是通用的，这些只是示例。我们把那些精确值未知、但需要确定的量定义为*控制变量*（control variables），把必须满足的条件定义为*约束*（constraints）。`Target` 序列通过数值方法求解边值问题，以确定满足约束所需的控制变量值。你使用 `Vary` 命令定义控制变量，使用 `Achieve` 命令定义问题的约束。`Target/EndTarget` 序列是一条高级命令。本节后面的示例给出了更多细节。

另请参阅：DifferentialCorrector（微分修正器）、Vary（优化变量）、Achieve（目标达成）、Optimize（优化）。

## 选项

| 选项 | 描述 |
|------|------|
| **ApplyCorrections** | 该 GUI 按钮替换 `Vary` 命令中指定的初始猜测值。如果 `Target` 序列已收敛，则应用收敛值；如果 `Target` 序列未收敛，则应用最后计算的值。存在一种情况不会发生上述"替换 `Vary` 命令中指定的初始猜测值"的动作：当 `Vary` 命令中指定的初始猜测值由变量给出时。更多细节请参阅帮助的"备注"部分。<br>• 接受的数据类型：N/A<br>• 允许值：N/A<br>• 默认值：N/A<br>• 是否必需：否<br>• 接口：GUI |
| **ExitMode** | 控制嵌套在控制流中的 `Target` 序列的初始猜测值。如果 `ExitMode` 设置为 `SaveAndContinue`，则保存 `Target` 序列的解，并将其用作下一次 `Target` 序列执行的初始猜测，然后执行任务序列的其余部分。如果 `ExitMode` 设置为 `DiscardAndContinue`，则丢弃该解，并在每次 `Target` 序列执行时使用 `Vary` 命令中指定的初始猜测值，然后执行任务序列的其余部分。如果 `ExitMode` 设置为 `Stop`，则执行 `Target` 序列，丢弃解，并且不执行任务序列的其余部分。<br>• 接受的数据类型：Reference Array<br>• 允许值：`DiscardAndContinue`、`SaveAndContinue`、`Stop`<br>• 默认值：`DiscardAndContinue`<br>• 是否必需：否<br>• 接口：GUI、脚本 |
| **ShowProgressWindow** | 标志位，指示是否应显示求解器进度窗口。<br>• 接受的数据类型：Boolean<br>• 允许值：true、false<br>• 默认值：true<br>• 是否必需：否<br>• 接口：GUI、脚本 |
| **SolveMode** | 指定 `Target` 序列在任务执行期间的行为。当 `SolveMode` 设置为 `Solve` 时，`Target` 序列执行并尝试求解满足目标器约束（即目标）的边值问题。当 `SolveMode` 设置为 `RunInitialGuess` 时，目标器不尝试求解边值问题，`Target` 序列中的命令使用 `Vary` 命令中定义的初始猜测值执行。<br>• 接受的数据类型：Reference Array<br>• 允许值：`Solve`、`RunInitialGuess`<br>• 默认值：`Solve`<br>• 是否必需：否<br>• 接口：GUI、脚本 |
| **SolverName** | 标识用于 `Target` 序列的 `DifferentialCorrector`（微分修正器）。<br>• 接受的数据类型：`DifferentialCorrector`<br>• 允许值：任何用户定义的或默认的 `DifferentialCorrector`<br>• 默认值：`DefaultDC`<br>• 是否必需：是<br>• 接口：GUI、脚本 |

## GUI

`Target` 命令允许你使用微分修正过程来求解问题。要求解给定问题，需要创建一个所谓的 `Target` 序列，其定义如下。当你向任务序列添加 `Target` 命令时，会自动添加一个 `EndTarget` 命令，如下图所示。

> [图：任务树中的 Target/EndTarget 命令]

在上面的示例中，`Target` 命令序列定义为 `Target1` 和 `End Target1` 命令之间（含）的所有命令。尽管上图中未显示，但 `Target` 命令序列必须同时包含 `Vary` 命令和 `Achieve` 命令。`Vary` 命令用于定义可以变化以达成某个目标的控制变量；`Achieve` 命令用于定义期望的目标。为了使 `Target` 序列结构良好，在任何 `Achieve` 命令之前必须至少有一个 `Vary` 命令，以便 `Vary` 命令中定义的变量能够影响后续 `Achieve` 命令中指定的目标。双击上面的 `Target1` 命令会弹出 `Target` 命令对话框（如下图所示），它允许你指定求解器（Solver，即你选择的 `DifferentialCorrector`）、求解模式（Solver Mode）和退出模式（Exit Mode）。如"备注"部分所述，`Target` 命令对话框还允许你将修正应用到 `Target` 命令序列。

> [图：Target 命令对话框界面]

如果将 `ShowProgressWindow` 设置为 true，则在目标求解期间会显示一个动态窗口，其中包含变量和约束的值，如下图所示。

> [图：目标求解求解器状态窗口]
## 备注

### Target/EndTarget 序列的内容

一个 `Target/EndTarget` 序列必须包含至少一个 `Vary` 命令和至少一个 `Achieve` 命令。这些命令的语法细节请参阅 `Vary` 和 `Achieve` 命令部分。第一个 `Vary` 命令必须出现在第一个 `Achieve` 命令之前。`Target` 命令必须与且仅与一个 `EndTarget` 命令配对。花括号中的每个 `Target` 命令字段都是可选的。你可以省略整个列表和花括号，此时 `Target` 配置字段（如 `SolveMode` 和 `ExitMode`）将使用默认值。

### Target/EndTarget 序列的用途

GMAT 的 `Target` 序列可以求解方阵问题（控制变量数量等于约束数量）、超定问题（控制变量数量少于约束数量）和欠定问题（控制变量数量多于约束数量）。在任何这些情况下，都可能不存在解，且求得的解的类型取决于目标器的选择（目前仅支持微分修正器）。假设问题存在解且满足某些数学条件，方阵问题通常有一个解，而欠定问题有许多解。目标（即约束）多于变量的问题可能没有解。如果你的问题是欠定的，可以考虑使用 `Optimize` 序列在可行解空间中寻找最优解。

> **注意**：如果你配置了 `Target` 序列并收到错误 "Rmatrix error: matrix is singular"（Rmatrix 错误：矩阵奇异），则说明你在 `Vary` 命令中定义的控制变量不影响 `Achieve` 命令中定义的约束。这种情况下一个常见的错误是忘记施加机动。

### 关于使用 Apply Corrections（应用修正）的说明

`Target` 序列运行后，你可以选择应用修正：导航到任务（Mission）树，右键单击 `Target` 命令以打开 `Target` 窗口，然后单击 **Apply Corrections** 按钮。**Apply Corrections** 按钮会替换 `Vary` 命令中指定的初始猜测值。如果 `Target` 序列已收敛，则应用收敛值；如果 `Target` 序列未收敛，则应用最后计算的值。注意，Apply Corrections 功能目前仅通过 GUI 界面提供。

存在一种情况不会发生上述"替换 `Vary` 命令中指定的初始猜测值"的动作。如下例所示，当 `Vary` 命令中指定的初始猜测值由变量给出时，**Apply Corrections** 按钮无效，因为 GMAT 不允许覆盖变量。

```
Create Variable InitialGuess_BurnDuration BurnDuration
Create DifferentialCorrector aDC
BeginMissionSequence
Target aDC
Vary aDC(BurnDuration = InitialGuess_BurnDuration)
Achieve aDC(BurnDuration = 10) % atypical Achieve command for
                               % illustrative purposes only
EndTarget
```

上述脚本：演示了初始猜测值由变量 InitialGuess_BurnDuration 给出的情况（其中 Achieve 命令的写法仅为示意，并非常规用法）。

### 命令交互

| 命令 | 描述 |
|------|------|
| `Vary` 命令 | 每个 `Target` 序列必须包含至少一个 `Vary` 命令。`Vary` 命令用于定义与 `Target` 序列关联的控制变量。 |
| `Achieve` 命令 | 每个 `Target` 序列必须包含至少一个 `Achieve` 命令。`Achieve` 命令用于定义与 `Target` 序列关联的目标。 |

## 示例

使用 `Target` 序列求解代数方程的根。这里我们为控制变量（或自变量）x 提供初始猜测值 5，并求解满足约束 y = 0 的 x 值，其中 y := 3*x^3 + 2*x^2 - 4*x + 8。执行此示例后，你可以在消息窗口中查看变量 x 的解。你可以很容易地验证所得的值确实满足约束。

```
Create Variable x y
Create DifferentialCorrector aDC

BeginMissionSequence

Target aDC
  Vary aDC(x = 5)
  y = 3*x^3 + 2*x^2 - 4*x + 8
  Achieve aDC(y = 0,{Tolerance = 0.0000001})
EndTarget
```

上述脚本：创建变量 x、y 和微分修正器 aDC；在 Target 序列中以 x 为控制变量（初值 5），计算多项式 y，并通过 Achieve 命令驱动 y 收敛到 0（容差 1e-7）。

使用 `Target` 序列提升轨道远地点。这里控制变量是 `ImpulsiveBurn` 对象的速度分量。约束是轨道远地点处的位置矢量量值为 42164。将收敛状态报告到文件。

```
Create Spacecraft aSat
Create Propagator aPropagator
Create Variable I

Create ImpulsiveBurn aBurn
Create DifferentialCorrector aDC
Create OrbitView EarthView
EarthView.Add = {Earth,aSat}
EarthView.ViewScaleFactor = 5

Create ReportFile aReport

BeginMissionSequence
Target aDC
   Vary aDC(aBurn.Element1 = 1.0, {Upper = 3})
   Maneuver aBurn(aSat)
   Propagate aPropagator(aSat,{aSat.Apoapsis})
   Achieve aDC(aSat.RMAG = 42164)
EndTarget
Report aReport aDC.SolverStatus aDC.SolverState
```

上述脚本：创建航天器、传播器、脉冲机动 aBurn、微分修正器 aDC、轨道视图和报告文件；在 Target 序列中以 aBurn.Element1 为控制变量（初值 1.0，上限 3），施加机动并传播到远地点，通过 Achieve 命令使远地点处位置量值 RMAG 达到 42164 km；最后将求解器状态报告到文件。

与前一个示例类似，我们使用 `Target` 序列提升轨道远地点，但这次使用有限推力机动。这里控制变量是 `FiniteBurn` 对象速度分量的持续时间。约束是轨道远地点处的位置矢量量值为 12000。下面示例的更多细节可在"Target Finite Burn to Raise Apogee"（目标求解有限推力机动提升远地点）教程中找到。

```
Create Spacecraft DefaultSC
Create Propagator DefaultProp
Create ChemicalThruster Thruster1
Thruster1.C1 = 1000
Thruster1.DecrementMass = true
Create ChemicalTank FuelTank1
Thruster1.Tank = {FuelTank1}
Create FiniteBurn FiniteBurn1
FiniteBurn1.Thrusters = {Thruster1}
DefaultSC.Tanks = {FuelTank1}
DefaultSC.Thrusters = {Thruster1}
Create Variable BurnDuration
Create DifferentialCorrector DC1

BeginMissionSequence

Propagate DefaultProp(DefaultSC) {DefaultSC.Earth.Periapsis}
Target DC1
  Vary DC1(BurnDuration = 200, {Upper = 10000})
  BeginFiniteBurn FiniteBurn1(DefaultSC)
  Propagate DefaultProp(DefaultSC){DefaultSC.ElapsedSecs=BurnDuration}
  EndFiniteBurn FiniteBurn1(DefaultSC)
  Propagate DefaultProp(DefaultSC) {DefaultSC.Earth.Apoapsis}
  Achieve DC1(DefaultSC.Earth.RMAG = 12000)
EndTarget
```

上述脚本：创建航天器、传播器、化学推力器（C1=1000，开启质量消耗）、燃料箱和有限推力机动，并建立挂载关系；先传播到近地点，然后在 Target 序列中以机动时长 BurnDuration 为控制变量（初值 200 s，上限 10000 s），执行有限推力机动并传播到远地点，使远地点处 RMAG 达到 12000 km。
