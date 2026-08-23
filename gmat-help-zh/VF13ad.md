# VF13ad 优化器（VF13ad）

> 译自 GMAT R2026a 帮助文档 VF13ad.html

**VF13ad** —— 序列二次规划（SQP）优化器 VF13ad。

## 描述

`VF13ad` 优化器是 Harwell 子程序库中提供的基于 SQP 的非线性规划求解器。`VF13ad` 执行非线性约束优化，同时支持线性和非线性约束。要使用此求解器，必须配置求解器选项，包括收敛准则、最大迭代次数和梯度计算方法。在任务序列中，你通过 `Optimize`/`EndOptimize` 序列来实现诸如 VF13ad 之类的优化器。在该序列中，你使用 `Vary` 命令定义优化变量，分别使用 `Minimize` 和 `NonlinearConstraint` 命令定义代价函数和约束。

该资源不能在任务序列中修改。

另请参阅：FminconOptimizer、Optimize（优化）、Vary（优化变量）、NonlinearConstraint（非线性约束）、Minimize（最小化）。

## 字段

| 字段 | 描述 |
|------|------|
| **FeasibilityTolerance** | 指定你希望约束被满足的精度（可行容差）。<br>• 数据类型：Real<br>• 允许值：Real > 0<br>• 访问权限：set<br>• 默认值：1e-3<br>• 单位：无<br>• 接口：GUI、脚本 |
| **UseFeasibility** | 切换是否应用优化约束。<br>• 数据类型：Boolean<br>• 允许值：true 或 false<br>• 访问权限：set<br>• 默认值：true<br>• 单位：无<br>• 接口：GUI、脚本 |
| **MaximumIterations** | 指定允许通过求解器控制序列的最大标称次数。<br>• 数据类型：Integer<br>• 允许值：Integer > 0<br>• 访问权限：set<br>• 默认值：200<br>• 单位：无<br>• 接口：GUI、脚本 |
| **ReportFile** | 包含报告文件的路径和文件名。<br>• 数据类型：String<br>• 允许值：任何用户定义的文件名<br>• 访问权限：set<br>• 默认值：`VF13adVF13ad1.data`<br>• 单位：无<br>• 接口：GUI、脚本 |
| **ReportStyle** | 确定求解器每次迭代时写入消息窗口以及写入 `ReportFile` 字段所指定报告的数据量和类型（当 `ShowProgress` 为 true 时）。目前，`Normal`、`Debug` 和 `Concise` 选项包含相同的信息：控制变量的值、约束和目标函数。除这些信息外，`Verbose` 选项还包含经优化器缩放的控制变量的值。<br>• 数据类型：String<br>• 允许值：`Normal`、`Concise`、`Verbose`、`Debug`<br>• 访问权限：set<br>• 默认值：`Normal`<br>• 单位：无<br>• 接口：GUI、脚本 |
| **ShowProgress** | 确定与求解器迭代相关的数据是否既显示在消息窗口中，又写入 `ReportFile` 字段所指定的报告。当 `ShowProgress` 为 true 时，消息窗口中包含的信息量和写入报告的信息量由 `ReportStyle` 字段控制。<br>• 数据类型：Boolean<br>• 允许值：`true`、`false`<br>• 访问权限：set<br>• 默认值：`true`<br>• 单位：无<br>• 接口：GUI、脚本 |
| **Tolerance** | 指定优化器用于根据 `Minimize` 命令中设置的目标值来判断何时找到最优解的度量。<br>• 数据类型：Real<br>• 允许值：Real > 0<br>• 访问权限：set<br>• 默认值：1e-5<br>• 单位：无<br>• 接口：GUI、脚本 |
| **UseCentralDifferences** | 允许你选择是否使用中心差分来数值求解导数。对于该字段的默认值 'false'，使用前向差分来计算导数。<br>• 数据类型：Boolean<br>• 允许值：`true`、`false`<br>• 访问权限：set<br>• 默认值：`false`<br>• 单位：无<br>• 接口：GUI、脚本 |
| **MaximumLineSearches** | 允许你指定优化过程每次迭代时沿下降方向执行的搜索次数。该设置使得即使对于非常平坦的目标函数，优化也能继续进行，即使执行的搜索次数超过典型搜索次数。不建议使用小于 20（VF13ad 默认值）的值，但也不会被阻止。<br>• 数据类型：Integer<br>• 允许值：Integer > 0<br>• 访问权限：set<br>• 默认值：`20`<br>• 单位：无<br>• 接口：GUI、脚本 |
| **CheckPhysicalTolerances** | 在每次标称迭代时启用对优化过程的监视。如果目标函数值在容差范围内，该监视允许在非线性约束落入容差范围时终止优化。可以为脚本中的约束单独设置约束容差。<br>• 数据类型：Boolean<br>• 允许值：`true`、`false`<br>• 访问权限：set<br>• 默认值：`false`<br>• 单位：无<br>• 接口：GUI、脚本 |
## GUI

`VF13ad` 对话框允许你指定 `VF13ad` 的属性，例如最大迭代次数、代价函数容差、可行容差、报告选项的选择，以及是否使用中心差分导数方法的选择。

要创建 `VF13ad` 资源，导航到资源（Resources）树，展开 `Solvers` 文件夹，选中并右键单击 `Optimizers` 子文件夹，指向 **Add**，然后选择 **VF13ad**。这将创建一个新的 `VF13ad` 资源 VF13ad1。双击 VF13ad1 弹出如下图所示的 `VF13ad` 对话框。

> [图：VF13ad 对话框界面]

## 备注

### VF13ad 优化器的可用性

此优化器不包含在 GMAT 的标称安装中，仅在你创建或下载并安装了 VF13ad 插件后可用。

### 资源与命令交互

`VF13ad` 资源只能在优化类命令的上下文中使用。更多信息和完整示例请参阅 Optimize（优化）、Vary（优化变量）、NonlinearConstraint（非线性约束）和 Minimize（最小化）的文档。

## 示例

创建一个名为 VF13ad1 的 `VF13ad` 资源。

```
Create VF13ad VF13ad1;
VF13ad1.ShowProgress = true;
VF13ad1.ReportStyle = Normal;
VF13ad1.ReportFile = 'VF13adVF13ad1.data';
VF13ad1.MaximumIterations = 200;
VF13ad1.Tolerance = 1e-05;
VF13ad1.UseCentralDifferences = false;
VF13ad1.UseFeasibility = true;
VF13ad1.FeasibilityTolerance = 0.001;
VF13ad1.MaximumLineSearches = 20;
VF13ad1.CheckPhysicalTolerances = false;
```

上述脚本：创建 VF13ad 优化器 VF13ad1，开启进度显示，报告样式为 Normal，指定报告文件名，设置最大迭代次数 200、收敛容差 1e-5、使用前向差分、启用可行容差 0.001、最大线搜索次数 20，并关闭物理容差检查。

关于如何在优化序列中使用 `VF13ad` 资源的示例，请参阅 Optimize（优化）命令示例。
