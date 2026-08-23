# 优化（Optimize）

> 译自 GMAT R2026a 帮助文档 Optimize.html

**Optimize** —— 通过改变一个或多个参数来求解条件。

## 脚本语法

```
Optimize SolverName [{[SolveMode = value], [ExitMode = value], [ShowProgressWindow = value]}]
   Vary 命令 ...
   脚本语句 ...
   NonlinearConstraint 命令 ...
   Minimize 命令 ...
EndOptimize
```

## 描述

GMAT 中的 `Optimize` 命令允许你使用求解器对象求解优化问题。目前，你可以从两个可用的求解器中选择：`FminconOptimizer` 求解器对象（可供所有能访问 Matlab 优化工具箱的 GMAT 用户使用）和 `VF13ad` 求解器对象插件（你必须自行安装）。

你使用 `Optimize` 和 `EndOptimize` 命令来定义一个优化（Optimize）序列，例如，用于确定将轨道远地点提升到 42164 km 所需的机动分量，同时最小化所需的 DeltaV。GMAT 中的 `Optimize` 序列适用于各种各样的问题，这只是一个示例。我们把那些精确值未知、但需要确定的量定义为控制变量（Control Variables），把必须满足的条件定义为约束（Constraints），把要最小化的量（例如 DeltaV）定义为目标函数（Objective function）。`Optimize` 序列通过数值方法求解边值问题，以确定满足约束所需的控制变量值，同时最小化目标函数。与 `Target`/`EndTarget` 命令序列的情况一样，你使用 `Vary` 命令定义控制变量，使用 `NonlinearConstraint` 命令定义必须满足的约束，使用 `Minimize` 命令定义要最小化的目标函数。`Optimize`/`EndOptimize` 序列是一条高级命令。本节后面的示例给出了更详细的说明。

另请参阅：Vary（优化变量）、NonlinearConstraint（非线性约束）、Minimize（最小化）、VF13ad。

## 选项

| 选项 | 描述 |
|------|------|
| **ApplyCorrections** | `ApplyCorrections` GUI 按钮将 `Vary` 命令中指定的初始猜测值替换为优化器在运行期间计算的值。如果 `Optimize` 序列已收敛，则应用收敛值；如果 `Optimize` 序列未收敛，则应用最后计算的值。存在一种情况不会发生上述"替换 `Vary` 命令中指定的初始猜测值"的动作：当 `Vary` 命令中指定的初始猜测值由变量给出时。<br>• 接受的数据类型：N/A<br>• 允许值：N/A<br>• 默认值：N/A<br>• 是否必需：否<br>• 接口：GUI、脚本 |
| **ExitMode** | 控制嵌套在控制流中的 `Optimize` 序列的初始猜测值。如果 `ExitMode` 设置为 `SaveAndContinue`，则保存 `Optimize` 序列的解，并在下次运行该 Optimize 序列时用作初始猜测，然后执行任务序列的其余部分。如果 `ExitMode` 设置为 `DiscardAndContinue`，则丢弃该解，并在每次 `Optimize` 序列执行时使用 `Vary` 命令中指定的初始猜测值，然后执行任务序列的其余部分。如果 `ExitMode` 设置为 `Stop`，则执行 `Optimize` 序列，丢弃解，并且不执行任务序列的其余部分。<br>• 接受的数据类型：Reference Array<br>• 允许值：`DiscardAndContinue`、`SaveAndContinue`、`Stop`<br>• 默认值：`DiscardAndContinue`<br>• 是否必需：否<br>• 接口：GUI、脚本 |
| **ShowProgressWindow** | 标志位，指示是否应显示求解器进度窗口。<br>• 接受的数据类型：Boolean<br>• 允许值：true、false<br>• 默认值：true<br>• 是否必需：否<br>• 接口：GUI、脚本 |
| **SolveMode** | 指定优化循环在任务执行期间的行为。当 `SolveMode` 设置为 `Solve` 时，优化循环执行并尝试求解优化问题。当 `SolveMode` 设置为 `RunInitialGuess` 时，优化器不尝试求解优化问题，`Optimize` 序列中的命令使用 `Vary` 命令中定义的初始猜测值执行。<br>• 接受的数据类型：Reference Array<br>• 允许值：`Solve`、`RunInitialGuess`<br>• 默认值：`Solve`<br>• 是否必需：否<br>• 接口：GUI、脚本 |
| **SolverName** | 指定 `Optimize` 序列中使用的求解器/优化器对象。<br>• 接受的数据类型：Reference Array<br>• 允许值：任何 `VF13ad` 或 `FminconOptimizer` 资源<br>• 默认值：`DefaultSQP`<br>• 是否必需：是<br>• 接口：GUI、脚本 |

## GUI

`Optimize` 命令允许你使用优化过程来求解问题。要求解给定问题，需要创建一个所谓的 `Optimize` 序列，其定义如下。当你向任务序列添加 `Optimize` 命令时，会自动添加一个 `EndOptimize` 命令，如下图所示。

> [图：任务树中的 Optimize/EndOptimize 命令]

在上面的示例中，`Optimize` 命令序列定义为 `Optimize1` 和 `EndOptimize1` 命令之间（含）的所有命令。尽管上图中未显示，但 `Optimize` 命令序列必须包含一个 `Vary` 命令，用于定义可以变化以帮助求解问题的控制变量。`Optimize` 命令还必须包含一个 `Minimize` 命令和/或一个或多个 `NonlinearConstraint` 命令。你使用 `Minimize` 命令定义希望最小化的代价函数，使用 `NonlinearConstraint` 命令定义你希望在优化过程结束时满足的等式或不等式约束。

双击上面的 `Optimize1` 命令打开 `Optimize` 命令对话框（如下图所示），它允许你指定求解器（Solver，即你选择的优化器）、求解模式（Solver Mode）和退出模式（Exit Mode）。如"备注"部分所述，`Optimize` 命令对话框还允许你将修正应用到 `Optimize` 命令序列。

> [图：Optimize 命令对话框界面]

如果将 `ShowProgressWindow` 设置为 true，则在优化期间会显示一个动态窗口，其中包含变量和约束的值，如下图所示。

> [图：优化求解器状态窗口]
## 备注

### Optimize/EndOptimize 序列的内容

一个 `Optimize/EndOptimize` 序列必须包含至少一个 `Vary` 命令，以及以下命令中的至少一个：`NonlinearConstraint` 和 `Minimize`。这些命令的语法细节请参阅 `Vary`、`NonlinearConstraint` 和 `Minimize` 命令部分。第一个 `Vary` 命令必须出现在第一个 `NonlinearConstraint` 或 `Minimize` 命令之前。花括号中的每个 `Optimize` 命令字段都是可选的。你可以省略整个列表和花括号，此时 `Optimize` 配置字段（如 `SolveMode` 和 `ExitMode`）将使用默认值。

### 与 Target/EndTarget 命令序列的关系

`Target/EndTarget` 和 `Optimize/EndOptimize` 命令序列之间存在一些功能上的相似之处。在两种情况下，我们都定义控制变量和约束。对于 `Target` 和 `Optimize` 序列，我们都使用 `Vary` 命令定义控制变量。对于 `Target` 序列，我们使用 `Achieve` 命令定义约束；而对于 `Optimize` 序列，我们使用 `NonlinearConstraint` 命令。`Target` 和 `Optimize` 序列之间的最大区别在于，`Optimize` 序列允许通过使用 `Minimize` 命令来最小化目标函数。

### 命令交互

| 命令 | 描述 |
|------|------|
| `Vary` 命令 | 每个 `Optimize` 序列必须包含至少一个 `Vary` 命令。`Vary` 命令用于定义与 `Optimize` 序列关联的控制变量。 |
| `NonlinearConstraint` 命令 | `NonlinearConstraint` 命令用于定义与 `Optimize` 序列关联的约束。注意，一个 `Optimize` 序列中允许多个 `NonlinearConstraint` 命令。 |
| `Minimize` 命令 | `Minimize` 命令在 `Optimize` 序列内使用，用于定义将被最小化的目标函数。注意，一个 `Optimize` 序列最多允许包含一个 `Minimize` 命令。（`Optimize` 序列不要求必须包含 `Minimize` 命令。） |

## 示例

使用带有 fmincon 求解器对象的 `Optimize` 序列，找出单位圆上 y 值最小的点 (x, y)。注意，使用 `FminconOptimizer` 求解器假定你能访问 Matlab 优化工具箱。

```
Create FminconOptimizer SQP1
SQP1.MaximumIterations = 50
Create Variable x y Circle

BeginMissionSequence
Optimize SQP1
  Vary SQP1(x = 1)
  Vary SQP1(y = 1)
  Circle = x*x + y*y
  NonlinearConstraint SQP1(Circle = 1)
  Minimize SQP1(y)
EndOptimize
```

上述脚本：创建 fmincon 优化器 SQP1（最大迭代次数 50）和变量 x、y、Circle；在 Optimize 序列中以 x、y 为控制变量（初值均为 1），施加约束 Circle = x²+y² = 1（单位圆），并最小化 y，即求单位圆上 y 最小的点。

与 Target 命令帮助中给出的示例类似，使用 `Optimize` 序列提升轨道远地点。在 Target 命令示例中，我们有一个控制变量（`ImpulsiveBurn` 对象的速度分量）和单个约束（轨道远地点处的位置矢量量值等于 42164）。在本示例中，我们保留该控制变量和约束，但现在添加第二个控制变量：机动发生位置的真近点角。此外，我们要求优化器最小化机动的 Delta-V 代价。正如预期的那样，执行远地点提升机动的最佳（DV 最小化）轨道位置在近地点附近（即 TA 接近 0）。在本示例中，由于所使用的力模型并非完美的二体开普勒模型，因此获得的最优 TA 值接近但不完全等于 0。注意，本示例中使用 `VF13ad` 求解器对象假定你已安装此可选插件。最后，将收敛状态报告到文件。

```
Create Spacecraft aSat
Create Propagator aPropagator
Create ImpulsiveBurn aBurn
Create VF13ad VF13ad1
VF13ad1.Tolerance = 1e-008
Create OrbitView EarthView
EarthView.Add = {Earth, aSat}
EarthView.ViewScaleFactor = 5
Create Variable ApogeeRadius DVCost
Create ReportFile aReport

BeginMissionSequence
Optimize VF13ad1
  Vary VF13ad1(aSat.TA = 100, {MaxStep = 10})
  Vary VF13ad1(aBurn.Element1 = 1, {MaxStep = 1})
  Maneuver aBurn(aSat)
  Propagate aPropagator(aSat) {aSat.Apoapsis}
  GMAT ApogeeRadius = aSat.RMAG
  NonlinearConstraint VF13ad1(ApogeeRadius=42164)
  GMAT DVCost = aBurn.Element1
  Minimize VF13ad1(DVCost)
EndOptimize 
Report aReport VF13ad1.SolverStatus VF13ad1.SolverState
```

上述脚本：创建航天器、传播器、脉冲机动 aBurn、VF13ad 优化器（容差 1e-8）、轨道视图、变量 ApogeeRadius 与 DVCost 以及报告文件；在 Optimize 序列中以机动位置真近点角 aSat.TA（初值 100 度，最大步长 10）和机动速度分量 aBurn.Element1（初值 1，最大步长 1）为控制变量，施加机动并传播到远地点，约束远地点半径 ApogeeRadius 等于 42164 km，同时最小化 Delta-V 代价 DVCost；最后将求解器状态报告到文件。
