# Yukon 优化器（Yukon）

> 译自 GMAT R2026a 帮助文档 Yukon.html

**Yukon** —— 序列二次规划（SQP）优化器 Yukon。

## 描述

`Yukon` 优化器是基于 SQP 的非线性规划求解器，它使用积极集线搜索算法方法，并使用改进的 BFGS 更新来近似黑塞矩阵（Hessian）。

`Yukon` 执行非线性约束优化，同时支持线性和非线性约束。要使用此求解器，必须配置求解器选项，包括收敛准则、最大迭代次数和梯度计算方法。在任务序列中，你通过 `Optimize`/`EndOptimize` 序列来实现诸如 Yukon 之类的优化器。在该序列中，你使用 `Vary` 命令定义优化变量，分别使用 `Minimize` 和 `NonlinearConstraint` 命令定义代价函数和约束。

该资源不能在任务序列中修改。

另请参阅：FminconOptimizer、VF13ad、Optimize（优化）、Vary（优化变量）、NonlinearConstraint（非线性约束）、Minimize（最小化）。

## 字段

| 字段 | 描述 |
|------|------|
| **FeasibilityTolerance** | 收敛所必须满足的最大无量纲约束违反量的容差（可行容差）。<br>• 数据类型：Real<br>• 允许值：Real > 0<br>• 访问权限：set<br>• 默认值：1e-4<br>• 单位：无<br>• 接口：GUI、脚本 |
| **FunctionTolerance** | 触发收敛的代价函数值变化量容差。如果从一次迭代到下一次迭代的代价函数变化小于 FunctionTolerance，且最大（无量纲）约束违反量小于 `OptimalityTolerance`，则算法终止。<br>• 数据类型：Real<br>• 允许值：Real > 0<br>• 访问权限：set<br>• 默认值：1e-4<br>• 单位：无<br>• 接口：GUI、脚本 |
| **HessianUpdateMethod** | 用于近似拉格朗日函数黑塞矩阵的方法。这些方法基于 BFGS，但对使用有限精度算术进行 BFGS 更新时可能出现的数值问题更具鲁棒性。<br>• 数据类型：String<br>• 允许值：`DampedBFGS`、`SelfScaledBFGS`<br>• 访问权限：set<br>• 默认值：`SelfScaledBFGS`<br>• 单位：无<br>• 接口：GUI、脚本 |
| **MaximumElasticWeight** | 当问题看起来不可行时，尝试最小化约束不可行性所允许的最大弹性权重。当检测到可能的不可行性时，弹性权重初始化为零，并且每次迭代失败后增加 10 倍，直到达到 `MaximumElasticWeight` 设置值，算法终止。<br>• 数据类型：Integer<br>• 允许值：Integer > 0<br>• 访问权限：set<br>• 默认值：10000<br>• 单位：无<br>• 接口：GUI、脚本 |
| **MaximumFunctionEvals** | 终止前通过控制序列的次数（最大函数求值次数）。<br>• 数据类型：Integer<br>• 允许值：Integer > 0<br>• 访问权限：set<br>• 默认值：1000<br>• 单位：无<br>• 接口：GUI、脚本 |
| **MaximumIterations** | 终止前允许的最大优化器迭代次数。<br>• 数据类型：Integer<br>• 允许值：Integer > 0<br>• 访问权限：set<br>• 默认值：200<br>• 单位：无<br>• 接口：GUI、脚本 |
| **OptimalityTolerance** | 触发收敛的拉格朗日函数梯度变化量容差（最优容差）。如果拉格朗日函数的梯度小于 `FeasibilityTolerance`，且最大（无量纲）约束违反量小于 `OptimalityTolerance`，则算法终止。<br>• 数据类型：Real<br>• 允许值：Real > 0<br>• 访问权限：set<br>• 默认值：1e-4<br>• 单位：无<br>• 接口：GUI、脚本 |
| **ReportFile** | 包含报告文件的路径和文件名，该报告包含迭代和收敛信息。<br>• 数据类型：String<br>• 允许值：任何用户定义的文件名<br>• 访问权限：set<br>• 默认值：`YukonOptimizer.data`<br>• 单位：无<br>• 接口：GUI、脚本 |
| **ReportStyle** | 确定求解器每次迭代时写入消息窗口以及写入 `ReportFile` 字段所指定报告的数据量和类型（当 `ShowProgress` 为 true 时）。目前，`Normal`、`Debug` 和 `Concise` 选项包含相同的信息：控制变量的值、约束和目标函数。除这些信息外，`Verbose` 选项还包含经优化器缩放的控制变量的值和约束雅可比矩阵。约束雅可比矩阵的值在缩放优化问题时很有用。更多信息请参阅"备注"部分。<br>• 数据类型：String<br>• 允许值：`Normal`、`Concise`、`Verbose`、`Debug`<br>• 访问权限：set<br>• 默认值：`Normal`<br>• 单位：无<br>• 接口：GUI、脚本 |
| **ShowProgress** | 确定与求解器迭代相关的数据是否既显示在消息窗口中，又写入 `ReportFile` 字段所指定的报告。当 `ShowProgress` 为 true 时，消息窗口中包含的信息量和写入报告的信息量由 `ReportStyle` 字段控制。<br>• 数据类型：Boolean<br>• 允许值：`true`、`false`<br>• 访问权限：set<br>• 默认值：`true`<br>• 单位：无<br>• 接口：GUI、脚本 |
| **UseCentralDifferences** | 允许你选择是否使用中心差分来数值求解导数。对于该字段的默认值 'false'，使用前向差分来计算导数。<br>• 数据类型：Boolean<br>• 允许值：`true`、`false`<br>• 访问权限：set<br>• 默认值：`false`<br>• 单位：无<br>• 接口：GUI、脚本 |
## GUI

`Yukon` 对话框允许你指定 `Yukon` 的属性，例如最大迭代次数、代价函数容差、可行容差、报告选项的选择，以及是否使用中心差分导数方法的选择。

要创建 `Yukon` 资源，导航到资源（Resources）树，展开 `Solvers` 文件夹，选中并右键单击 `Optimizers` 子文件夹，指向 **Add**，然后选择 **Yukon**。这将创建一个新的 `Yukon` 资源 Yukon1。双击 Yukon1 弹出如下图所示的 `Yukon` 对话框。

> [图：Yukon 对话框界面]

## 备注

### Yukon 优化器的可用性

此优化器在公开发行版和内部发行版中均有分发。

### 资源与命令交互

`Yukon` 资源只能在优化类命令的上下文中使用。更多信息和完整示例请参阅 Optimize（优化）、Vary（优化变量）、NonlinearConstraint（非线性约束）和 Minimize（最小化）的文档。

## 示例

创建一个名为 Yukon1 的 `Yukon` 资源。

```
Create Yukon Yukon1
Yukon1.ShowProgress          = true;
Yukon1.ReportStyle           = Normal;
Yukon1.ReportFile            = 'YukonYukon1.data';
Yukon1.MaximumIterations     = 200;
Yukon1.UseCentralDifferences = false;
Yukon1.FeasibilityTolerance  = 0.0001;
Yukon1.HessianUpdateMethod   = SelfScaledBFGS;
Yukon1.MaximumFunctionEvals  = 1000;
Yukon1.OptimalityTolerance   = 0.0001;
Yukon1.FunctionTolerance     = 0.0001;
Yukon1.MaximumElasticWeight  = 10000;
```

上述脚本：创建 Yukon 优化器 Yukon1，开启进度显示，报告样式为 Normal，指定报告文件名，设置最大迭代次数 200、使用前向差分、可行容差 1e-4、黑塞矩阵更新方法为 SelfScaledBFGS、最大函数求值次数 1000、最优容差与函数容差均为 1e-4、最大弹性权重 10000。

下面是一个配置为使用 Yukon 优化器的带非线性约束的简单优化示例。

```
%------ Create and Setup the Optimizer
Create Yukon NLPSolver;

%------ Arrays, Variables, Strings
Create Variable X1 X2 J G;

%------ Mission Sequence
BeginMissionSequence;

Optimize NLPSolver {SolveMode = Solve, ExitMode = DiscardAndContinue};
   
   %  Vary the independent variables
   Vary 'Vary X1' NLPSolver(X1 = 0, {Perturbation = 0.0000001});
   Vary 'Vary X2' NLPSolver(X2 = 0, {Perturbation = 0.0000001});
   
   %  The cost function and Minimize command
   'Compute Cost (J)' J = ( X1 - 2 )^2 + ( X2 - 2 )^2;
   Minimize 'Minimize Cost (J)' NLPSolver(J);
   
   %  Calculate constraint and use NonLinearConstraint command
   'Compute Constraint (G)' G = X2 + X1;
   NonlinearConstraint 'G = 8' NLPSolver(G =8);

EndOptimize;  % For optimizer NLPSolver
```

上述脚本：创建 Yukon 优化器 NLPSolver 和变量 X1、X2、J、G；在 Optimize 序列中以 X1、X2 为控制变量（初值 0，摄动步长 1e-7），最小化代价函数 J = (X1-2)² + (X2-2)²，并施加非线性约束 G = X1+X2 = 8。
