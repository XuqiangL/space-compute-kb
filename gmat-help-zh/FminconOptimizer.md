# fmincon 优化器（FminconOptimizer）

> 译自 GMAT R2026a 帮助文档 FminconOptimizer.html

**FminconOptimizer** —— 序列二次规划（SQP）优化器 fmincon。

## 描述

`fmincon` 是 MATLAB 优化工具箱中提供的非线性规划求解器。`fmincon` 执行非线性约束优化，支持线性和非线性约束。要使用此求解器，必须配置求解器选项，包括收敛准则、最大迭代次数以及梯度的计算方式。在任务序列中，你通过 `Optimize`/`EndOptimize` 序列来实现诸如 fmincon 之类的优化器。在该序列中，你使用 `Vary` 命令定义优化变量，分别使用 `Minimize` 和 `NonlinearConstraint` 命令定义代价函数和约束。

该资源不能在任务序列中修改。该资源在 API 中不可用。

另请参阅：VF13ad、Optimize（优化）、Vary（优化变量）、NonlinearConstraint（非线性约束）、Minimize（最小化）。

## 字段

| 字段 | 描述 |
|------|------|
| **DiffMaxChange** | MATLAB 有限差分算法中所用摄动的上限。对于 fmincon，你不指定单一的摄动值，而是给 MATLAB 一个范围，它使用自适应算法尝试找到最优摄动。<br>• 数据类型：String<br>• 允许值：实数 > 0<br>• 访问权限：Set<br>• 默认值：0.1<br>• 单位：无<br>• 接口：GUI、脚本 |
| **DiffMinChange** | MATLAB 有限差分算法中所用摄动的下限。对于 fmincon，你不指定单一的摄动值，而是给 MATLAB 一个范围，它使用自适应算法尝试找到最优摄动。<br>• 数据类型：String<br>• 允许值：实数 > 0<br>• 访问权限：Set<br>• 默认值：1e-8<br>• 单位：无<br>• 接口：GUI、脚本 |
| **MaxFunEvals** | 指定在尝试寻找最优解时使用的代价函数最大求值次数。这相当于设置 GMAT 脚本中通过优化循环的最大次数。如果在达到最大函数求值次数之前未找到解，fmincon 输出 ExitFlag 为零，GMAT 继续执行。<br>• 数据类型：String<br>• 允许值：Integer > 0<br>• 访问权限：Set<br>• 默认值：1000<br>• 单位：无<br>• 接口：GUI、脚本 |
| **MaximumIterations** | 指定允许通过优化器的最大标称次数。注意，这与 `VF13ad` 优化器所显示的优化器迭代次数不同。<br>• 数据类型：String<br>• 允许值：Integer > 0<br>• 访问权限：Set<br>• 默认值：25<br>• 单位：无<br>• 接口：GUI、脚本 |
| **ReportFile** | 包含报告文件的路径和文件名。<br>• 数据类型：String<br>• 允许值：任何用户定义的文件名<br>• 访问权限：Set<br>• 默认值：`FminconOptimizerSQP1.data`<br>• 单位：无<br>• 接口：GUI、脚本 |
| **ReportStyle** | 确定求解器每次迭代时写入消息窗口以及写入 `ReportFile` 字段所指定报告的数据量和类型（当 `ShowProgress` 为 true 时）。目前，`Normal`、`Debug` 和 `Concise` 选项包含相同的信息：控制变量的值、约束和目标函数。除这些信息外，`Verbose` 选项还包含经优化器缩放的控制变量的值。<br>• 数据类型：String<br>• 允许值：`Normal`、`Concise`、`Verbose`、`Debug`<br>• 访问权限：Set<br>• 默认值：`Normal`<br>• 单位：无<br>• 接口：GUI、脚本 |
| **ShowProgress** | 确定与求解器迭代相关的数据是否既显示在消息窗口中，又写入 `ReportFile` 字段所指定的报告。当 `ShowProgress` 为 true 时，消息窗口中包含的信息量和写入报告的信息量由 `ReportStyle` 字段控制。<br>• 数据类型：Boolean<br>• 允许值：`true`、`false`<br>• 访问权限：Set<br>• 默认值：`true`<br>• 单位：无<br>• 接口：GUI、脚本 |
| **TolCon** | 指定约束函数的收敛容差。<br>• 数据类型：String<br>• 允许值：实数 > 0<br>• 访问权限：Set<br>• 默认值：1e-4<br>• 单位：无<br>• 接口：GUI、脚本 |
| **TolFun** | 指定代价函数值的收敛容差。<br>• 数据类型：String<br>• 允许值：实数 > 0<br>• 访问权限：Set<br>• 默认值：1e-4<br>• 单位：无<br>• 接口：GUI、脚本 |
| **TolX** | 指定自变量矢量的终止容差，仅在用户为该字段设置了值时使用。<br>• 数据类型：String<br>• 允许值：实数 > 0<br>• 访问权限：Set<br>• 默认值：1e-4<br>• 单位：无<br>• 接口：GUI、脚本 |
## GUI

`FminconOptimizer` 对话框允许你指定 `FminconOptimizer` 资源的属性，例如最大迭代次数、最大函数求值次数、控制变量终止容差、约束容差、代价函数容差、有限差分算法参数以及报告选项的选择。

要创建 `FminconOptimizer` 资源，导航到资源（Resources）树，展开 `Solvers` 文件夹，选中并右键单击 `Optimizers` 子文件夹，指向 **Add**，然后选择 **SQP (fmincon)**。这将创建一个新的 `FminconOptimizer` 资源 `SQP1`。双击 `SQP1` 弹出如下图所示的 `FminconOptimizer` 对话框。

> [图：FminconOptimizer 对话框界面]

## 备注

### fmincon 优化器的可用性

此优化器仅在你能同时访问 MATLAB 和 MATLAB 优化工具箱时可用。GMAT 包含 fmincon 优化器的接口，因此在你看来 fmincon 就像是 GMAT 内置的优化器。为了与 MATLAB 保持一致（与 GMAT 中的其他求解器不同），该资源的字段名复制自 MATLAB 的 optimset 函数中使用的字段名。

### 使用 Fmincon 时，GMAT 停止按钮在某些情况下不起作用

有时，在开发 GMAT 脚本时，你可能会无意中造成 GMAT 进入无限传播循环的情况。这种情况通常的补救方法是单击 GMAT 的 **Stop** 按钮。但是，目前如果无限循环发生在使用 fmincon 的 `Optimize` 序列内，则无法停止 GMAT，你只能关闭 GMAT。幸运的是，你可以采用一些方法来避免这种情况。你应该使用多个停止条件，以便不会发生长时间传播。例如，如果 fmincon 控制变量 `myVar`，并且我们知道 `myVar` 绝不应超过 2，那么可以这样做：

```
Propagate myProp(mySat){mySat.ElapsedDays = myVar, mySat.ElapsedDays = 2}
```

上述脚本：传播时同时施加两个停止条件——经过天数等于 myVar 或等于 2，这样即使 myVar 异常增大，传播也会在 2 天时停止，避免无限循环。

### 资源与命令交互

`FminconOptimizer` 资源只能在优化类命令的上下文中使用。更多信息和完整示例请参阅 Optimize（优化）、Vary（优化变量）、NonlinearConstraint（非线性约束）和 Minimize（最小化）的文档。

## 示例

创建一个名为 SQP1 的 `FminconOptimizer` 资源。

```
Create FminconOptimizer SQP1
SQP1.ShowProgress = true
SQP1.ReportStyle = Normal
SQP1.ReportFile = 'FminconOptimizerSQP1.data'
SQP1.MaximumIterations = 25
SQP1.DiffMaxChange = '0.1000'
SQP1.DiffMinChange = '1.0000e-08'
SQP1.MaxFunEvals = '1000'
SQP1.TolX = '1.0000e-04'
SQP1.TolFun = '1.0000e-04'
SQP1.TolCon = '1.0000e-04'
```

上述脚本：创建 fmincon 优化器 SQP1，开启进度显示，报告样式为 Normal，指定报告文件名，并设置最大迭代次数 25、有限差分摄动上下限、最大函数求值次数 1000，以及自变量、代价函数和约束的收敛容差均为 1e-4。

关于如何在优化序列中使用 `FminconOptimizer` 资源的示例，请参阅 Optimize（优化）命令示例。
