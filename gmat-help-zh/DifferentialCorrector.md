# 微分修正器（DifferentialCorrector）

> 译自 GMAT R2026a 帮助文档 DifferentialCorrector.html

**DifferentialCorrector** —— 数值求解器。

## 描述

`DifferentialCorrector`（微分修正器，简称 DC）是用于求解边值问题的数值求解器。它用于精化一组可变参数，以满足为所建模任务定义的一组目标。GMAT 中的 DC 支持多种数值技术。在任务序列中，你在 `Target` 控制序列中使用 `DifferentialCorrector` 资源来求解边值问题。在 GMAT 中，微分修正器常用于确定实现期望轨道条件（例如行星飞越时的 B 平面条件）所需的机动分量。

你必须为你的应用创建并配置 `DifferentialCorrector` 资源，设置求解器的数值属性，例如算法类型、允许的最大迭代次数，以及用于计算有限差分的导数方法选择。你还可以在不同的输出选项中进行选择，以显示每次微分修正器迭代的逐级详细的信息。

该资源不能在任务序列中修改。

另请参阅：Target（目标求解）、Vary（优化变量）、Achieve（目标达成）。

## 字段

| 字段 | 描述 |
|------|------|
| **Algorithm** | 用于求解边值问题的数值方法。<br>• 数据类型：String<br>• 允许值：`NewtonRaphson`、`Broyden`、`ModifiedBroyden`<br>• 访问权限：set<br>• 默认值：`NewtonRaphson`<br>• 单位：N/A<br>• 接口：GUI、脚本 |
| **DerivativeMethod** | 在数值求解导数时选择单侧差分或中心差分。仅在 `Algorithm` 设置为 `NewtonRaphson` 时使用。<br>• 数据类型：String<br>• 允许值：`ForwardDifference`（前向差分）、`BackwardDifference`（后向差分）、`CentralDifference`（中心差分）<br>• 访问权限：set<br>• 默认值：`ForwardDifference`<br>• 单位：N/A<br>• 接口：GUI、脚本 |
| **MaximumIterations** | 设置 `DifferentialCorrector` 在尝试求解时允许的最大标称迭代次数。如果达到最大迭代次数，GMAT 退出目标循环并继续执行任务序列中的下一条命令。在这种情况下，各对象保留其最后一次标称通过目标循环时的状态。<br>• 数据类型：Integer<br>• 允许值：Integer >= `1`<br>• 访问权限：set<br>• 默认值：25<br>• 单位：N/A<br>• 接口：GUI、脚本 |
| **ReportFile** | 指定 `DifferentialCorrector` 报告的路径和文件名。仅当 `ShowProgress` 设置为 true 时才生成报告。<br>• 数据类型：String<br>• 允许值：符合操作系统规范的文件名<br>• 访问权限：set<br>• 默认值：`DifferentialCorrectorDCName.data`，其中 `DCname` 为 `DifferentialCorrector` 的名称<br>• 单位：N/A<br>• 接口：GUI、脚本 |
| **ReportStyle** | 控制写入 `ReportFile` 字段所定义文件的信息量和类型。目前，`Normal` 和 `Concise` 选项包含相同的信息：雅可比矩阵、雅可比矩阵的逆、控制变量的当前值，以及约束的达成值和期望值。`Verbose` 除包含 `Normal` 和 `Concise` 的数据外，还包含摄动变量的值。`Debug` 包含每次迭代时具有控制变量的对象的详细脚本片段。<br>• 数据类型：String<br>• 允许值：`Normal`、`Concise`、`Verbose`、`Debug`<br>• 访问权限：set<br>• 默认值：`Normal`<br>• 单位：N/A<br>• 接口：GUI、脚本 |
| **ShowProgress** | 当 `ShowProgress` 字段设置为 true 时，展示微分修正过程进展的数据将写入消息窗口和 `ReportFile`。消息窗口会更新当前控制变量值和约束偏差的信息。当 `ShowProgress` 字段设置为 false 时，微分修正过程的进展信息既不显示到消息窗口，也不写入 `ReportFile`。<br>• 数据类型：String<br>• 允许值：`true`、`false`<br>• 访问权限：set<br>• 默认值：`true`<br>• 单位：N/A<br>• 接口：GUI、脚本 |

## GUI

`DifferentialCorrector` 对话框允许你指定 `DifferentialCorrector` 的属性，例如数值算法、最大迭代次数、用于计算有限差分的导数方法选择以及报告选项的选择。

要创建 `DifferentialCorrector` 资源，导航到资源（Resources）树，展开 `Solvers` 文件夹，右键单击 `Boundary Value Solvers` 文件夹，指向 **Add**，然后单击 **DifferentialCorrector**。将创建一个名为 `DC1` 的资源。双击 `DC1` 资源，弹出下面的微分修正器对话框。

> [图：DifferentialCorrector 对话框界面]
## 备注

### 支持的算法细节

GMAT 支持多种求解边值问题的算法，包括 Newton Raphson（牛顿-拉夫森）、Broyden（布罗伊登）和 Modified Broyden（改进布罗伊登）。这些算法使用有限差分或其他数值近似来计算约束和自变量的雅可比矩阵。目前的默认算法是 `NewtonRaphson`。`Broyden` 方法和 `ModifiedBroyden` 通常比 `NewtonRaphson` 需要更多次迭代，但函数求值次数更少，因此通常更快。下面提供每种算法的描述。我们建议为你的应用尝试不同的算法选项，以确定哪种算法在性能和鲁棒性之间提供最佳平衡。

#### Newton-Raphson（牛顿-拉夫森）

`NewtonRaphson` 算法是一种拟牛顿法，使用有限差分计算雅可比矩阵。GMAT 支持前向、中心和后向差分来计算雅可比矩阵。

#### Broyden（布罗伊登）

`Broyden` 方法使用状态迭代之间的斜率作为一阶导数的近似，而不是使用有限差分来数值计算一阶导数。这大大减少了函数求值次数。Broyden 迭代使用以下方程更新：

> [图：Broyden 迭代更新公式]

#### ModifiedBroyden（改进布罗伊登）

改进的 `Broyden` 方法更新雅可比矩阵的逆，以避免在求解接近奇异的问题时矩阵求逆的数值问题。与 `Broyden` 方法一样，它比 `NewtonRaphson` 算法需要更少的函数求值次数。雅可比矩阵的逆 H 使用以下方程更新：

> [图：ModifiedBroyden 雅可比逆更新公式]

其中：

> [图：ModifiedBroyden 更新公式中各符号的定义]

### 资源与命令交互

`DifferentialCorrector` 对象只能在目标求解类命令的上下文中使用。更多信息和完整示例请参阅 Target（目标求解）、Vary（优化变量）和 Achieve（目标达成）的文档。

## 示例

创建一个配置为使用 Broyden 方法的 `DifferentialCorrector`，并用它求解远地点提升机动。

```
Create Spacecraft aSat
Create Propagator aProp
Create ImpulsiveBurn aDeltaV
Create OrbitView a3DPlot
a3DPlot.Add = {aSat,Earth};

Create DifferentialCorrector aDC
aDC.Algorithm = 'Broyden'

BeginMissionSequence

Propagate aProp(aSat){aSat.Periapsis}

Target aDC

    Vary aDC(aDeltaV.Element1 = 0.01)
    Maneuver aDeltaV(aSat)
    Propagate aProp(aSat){aSat.Apoapsis}
    Achieve aDC(aSat.RMAG = 12000)

EndTarget
```

上述脚本：创建航天器、传播器、脉冲机动 aDeltaV 和轨道视图；创建微分修正器 aDC 并设置算法为 Broyden；先传播到近地点，然后在 Target 序列中以 aDeltaV.Element1 为控制变量（初值 0.01），施加机动并传播到远地点，使远地点处位置量值 RMAG 达到 12000 km。

要查看更多关于 `DifferentialCorrector` 对象如何与 `Target`、`Vary` 和 `Achieve` 命令配合求解轨道问题的示例，请参阅 Target 命令示例。
